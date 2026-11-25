import copy
import itertools
import random
import unittest

from lottery.assign import (assign, average_priority, draw_tickets, highest_priority,
                            lowest_priority, seed_commitment)
from lottery.generate import Config, make_campus
from lottery.model import Group, Room, Student


def grp(gid, years, prefs, split=False, gender="F", ticket=0.5):
    members = [Student(f"{gid}{i}", y, gender) for i, y in enumerate(years)]
    return Group(gid, members, prefs, split, ticket=ticket)


class WorkedExample(unittest.TestCase):
    """The four-group example from the design doc, section 4."""

    def test_example(self):
        rooms = [Room("F1", "Ferrin", "F", 2),
                 Room("N2", "Nyland", "F", 2), Room("N3", "Nyland", "F", 3)]
        a = grp("A", ["senior", "senior"], ["Ferrin", "Nyland"])
        b = grp("B", ["senior", "junior", "junior"], ["Ferrin", "Nyland"])
        c = grp("C", ["junior", "sophomore"], ["Ferrin"], split=True)
        d = grp("D", ["sophomore", "freshman"], ["Nyland"])
        res = assign([d, c, b, a], rooms, average_priority)

        self.assertEqual(res.order, ["A", "B", "C", "D"])
        p = res.placements
        self.assertEqual((p["A0"].room_id, p["A0"].choice_rank), ("F1", 1))
        self.assertEqual((p["B0"].room_id, p["B0"].choice_rank), ("N3", 2))
        self.assertIsNone(p["C0"].hall)
        self.assertTrue(p["C0"].was_split and p["C1"].was_split)
        self.assertEqual(p["D0"].room_id, "N2")
        self.assertEqual(res.splits, 1)


class Rules(unittest.TestCase):
    def test_priority_rules(self):
        g = grp("G", ["senior", "sophomore"], [])
        self.assertEqual(average_priority(g), 3.0)
        self.assertEqual(highest_priority(g), 4)
        self.assertEqual(lowest_priority(g), 2)

    def test_ticket_breaks_ties_only(self):
        hi = grp("H", ["junior"], ["X"], ticket=0.9)
        lo = grp("L", ["junior"], ["X"], ticket=0.1)
        res = assign([hi, lo], [Room("x", "X", "F", 1)], average_priority)
        self.assertEqual(res.placements["L0"].hall, "X")
        self.assertIsNone(res.placements["H0"].hall)

    def test_best_fit_keeps_big_rooms_free(self):
        rooms = [Room("quad", "X", "F", 4), Room("dbl", "X", "F", 2)]
        pair = grp("P", ["senior", "senior"], ["X"], ticket=0.1)
        four = grp("Q", ["junior"] * 4, ["X"], ticket=0.2)
        res = assign([pair, four], rooms, average_priority)
        self.assertEqual(res.placements["P0"].room_id, "dbl")
        self.assertEqual(res.placements["Q0"].room_id, "quad")

    def test_gender_respected(self):
        res = assign([grp("M", ["senior"], ["X"], gender="M")],
                     [Room("f", "X", "F", 2)], average_priority)
        self.assertIsNone(res.placements["M0"].hall)

    def test_no_split_without_consent(self):
        rooms = [Room("a", "X", "F", 1), Room("b", "X", "F", 1)]
        res = assign([grp("G", ["senior", "senior"], ["X"], split=False)], rooms, average_priority)
        self.assertIsNone(res.placements["G0"].hall)
        self.assertEqual(res.splits, 0)


class Lottery(unittest.TestCase):
    def test_draw_is_reproducible(self):
        _, g1, _ = make_campus(Config(students=200), seed=7)
        _, g2, _ = make_campus(Config(students=200), seed=7)
        draw_tickets(g1, "public-seed")
        draw_tickets(g2, "public-seed")
        self.assertEqual([g.ticket for g in g1], [g.ticket for g in g2])

    def test_commitment(self):
        self.assertEqual(len(seed_commitment("abc")), 64)
        self.assertNotEqual(seed_commitment("abc"), seed_commitment("abd"))


class Campus(unittest.TestCase):
    def test_everyone_in_exactly_one_group_with_one_gender(self):
        students, groups, _ = make_campus(Config(students=500), seed=3)
        ids = [s.id for g in groups for s in g.members]
        self.assertEqual(sorted(ids), sorted(s.id for s in students))
        for g in groups:
            self.assertEqual(len({s.gender for s in g.members}), 1)
            self.assertTrue(1 <= g.size <= 4 and 1 <= len(g.prefs) <= 6)

    def test_every_student_gets_a_placement_and_no_room_overflows(self):
        _, groups, rooms = make_campus(Config(students=500), seed=4)
        draw_tickets(groups, "s")
        res = assign(groups, rooms, average_priority)
        self.assertEqual(len(res.placements), sum(g.size for g in groups))
        self.assertTrue(all(len(r.occupants) <= r.size for r in rooms))


class StrategyProof(unittest.TestCase):
    """No group can get a hall it likes more by misreporting its ranking."""

    def test_no_profitable_misreport(self):
        rng = random.Random(11)
        halls = ["A", "B", "C"]
        for trial in range(60):
            rooms = [Room(f"{h}{i}", h, "F", rng.choice([1, 2, 3]))
                     for h in halls for i in range(rng.randint(0, 2))]
            groups = [grp(f"g{i}x", [rng.choice(["senior", "junior", "freshman"])] * rng.randint(1, 3),
                          rng.sample(halls, rng.randint(1, 3)), ticket=rng.random())
                      for i in range(5)]
            for target in groups:
                truth = target.prefs

                def outcome(report):
                    target.prefs = report
                    res = assign(copy.deepcopy(groups), copy.deepcopy(rooms), average_priority)
                    target.prefs = truth
                    hall = res.placements[target.members[0].id].hall
                    return truth.index(hall) if hall in truth else len(truth)

                honest = outcome(truth)
                for k in range(1, 4):
                    for report in itertools.permutations(halls, k):
                        self.assertLessEqual(honest, outcome(list(report)),
                                             f"trial {trial}: {target.id} gains by reporting {report}")


if __name__ == "__main__":
    unittest.main()
