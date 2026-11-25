import copy
import itertools
import random
import unittest

from lottery.assign import (Inventory, assign, assign_v1, average_priority, draw_tickets,
                            highest_priority, lowest_priority, pieces, seed_commitment)
from lottery.generate import Config, make_campus
from lottery.model import Group, Room, Student


def grp(gid, years, halls=(), split=False, gender="F", ticket=0.5, options=()):
    members = [Student(f"{gid}{i}", y, gender) for i, y in enumerate(years)]
    ranking = list(halls) or sorted({h for h, _ in options})
    return Group(gid, members, ranking, len(ranking), split,
                 options=list(options), ticket=ticket)


class V1WorkedExample(unittest.TestCase):
    """The four-group example from the first design doc, section 4."""

    def test_example(self):
        rooms = [Room("F1", "Ferrin", "F", 2),
                 Room("N2", "Nyland", "F", 2), Room("N3", "Nyland", "F", 3)]
        a = grp("A", ["senior", "senior"], ["Ferrin", "Nyland"])
        b = grp("B", ["senior", "junior", "junior"], ["Ferrin", "Nyland"])
        c = grp("C", ["junior", "sophomore"], ["Ferrin"], split=True)
        d = grp("D", ["sophomore", "freshman"], ["Nyland"])
        res = assign_v1([d, c, b, a], rooms, average_priority)

        self.assertEqual(res.order, ["A", "B", "C", "D"])
        p = res.placements
        self.assertEqual((p["A0"].room_id, p["A0"].hall_rank), ("F1", 1))
        self.assertEqual((p["B0"].room_id, p["B0"].hall_rank), ("N3", 2))
        self.assertIsNone(p["C0"].hall)
        self.assertTrue(p["C0"].was_split and p["C1"].was_split)
        self.assertEqual(p["D0"].room_id, "N2")
        self.assertEqual(res.splits, 1)

    def test_no_split_without_consent(self):
        rooms = [Room("a", "X", "F", 1), Room("b", "X", "F", 1)]
        res = assign_v1([grp("G", ["senior", "senior"], ["X"], split=False)], rooms, average_priority)
        self.assertIsNone(res.placements["G0"].hall)
        self.assertEqual(res.splits, 0)

    def test_best_fit_keeps_big_rooms_free(self):
        rooms = [Room("quad", "X", "F", 4), Room("dbl", "X", "F", 2)]
        pair = grp("P", ["senior", "senior"], ["X"], ticket=0.1)
        four = grp("Q", ["junior"] * 4, ["X"], ticket=0.2)
        res = assign_v1([pair, four], rooms, average_priority)
        self.assertEqual(res.placements["P0"].room_id, "dbl")
        self.assertEqual(res.placements["Q0"].room_id, "quad")


class V2Options(unittest.TestCase):
    def test_room_type_is_respected(self):
        # The pair asked for a quad, so it does not take the double.
        rooms = [Room("dbl", "X", "F", 2), Room("quad", "X", "F", 4)]
        g = grp("G", ["senior", "senior"], options=[("X", 4)])
        res = assign([g], rooms, average_priority)
        self.assertEqual(res.placements["G0"].room_id, "quad")

    def test_split_option_keeps_group_in_one_hall(self):
        rooms = [Room("d1", "X", "F", 2), Room("d2", "X", "F", 2)]
        g = grp("G", ["junior"] * 4, options=[("X", 4), ("X", 2)])
        res = assign([g], rooms, average_priority)
        got = {res.placements[f"G{i}"].room_id for i in range(4)}
        self.assertEqual(got, {"d1", "d2"})
        self.assertTrue(res.placements["G0"].was_split)
        self.assertEqual(res.placements["G0"].choice_rank, 2)
        self.assertEqual(res.splits, 1)

    def test_partial_fit_reserves_nothing(self):
        # Only one double left: the 4-person split option cannot be filled, so
        # the group falls through to its next option and the double stays free.
        rooms = [Room("d1", "X", "F", 2), Room("q", "Y", "F", 4)]
        g = grp("G", ["junior"] * 4, options=[("X", 2), ("Y", 4)])
        solo = grp("S", ["freshman"], options=[("X", 2)], ticket=0.9)
        res = assign([g, solo], rooms, average_priority)
        self.assertEqual(res.placements["G0"].room_id, "q")
        self.assertEqual(res.placements["S0"].room_id, "d1")

    def test_odd_group_split(self):
        self.assertEqual([len(p) for p in pieces(list(range(3)), 2)], [2, 1])
        rooms = [Room("d1", "X", "F", 2), Room("d2", "X", "F", 2)]
        g = grp("G", ["junior"] * 3, options=[("X", 2)])
        res = assign([g], rooms, average_priority)
        self.assertEqual(sorted(len(r.occupants) for r in rooms), [1, 2])
        self.assertTrue(all(res.placements[f"G{i}"].hall == "X" for i in range(3)))

    def test_unplaced_when_no_option_fits(self):
        res = assign([grp("G", ["senior"] * 2, options=[("X", 4)])],
                     [Room("d", "X", "F", 2)], average_priority)
        self.assertIsNone(res.placements["G0"].hall)

    def test_gender_respected(self):
        res = assign([grp("M", ["senior"], gender="M", options=[("X", 2)])],
                     [Room("f", "X", "F", 2)], average_priority)
        self.assertIsNone(res.placements["M0"].hall)

    def test_inventory_find_excludes_reserved(self):
        r1, r2 = Room("a", "X", "F", 2), Room("b", "X", "F", 2)
        inv = Inventory([r1, r2])
        first = inv.find("X", "F", 2, 2)
        second = inv.find("X", "F", 2, 2, {id(first)})
        self.assertIsNot(first, second)
        self.assertIsNone(inv.find("X", "F", 2, 2, {id(r1), id(r2)}))


class Rules(unittest.TestCase):
    def test_priority_rules(self):
        g = grp("G", ["senior", "sophomore"], ["X"])
        self.assertEqual(average_priority(g), 3.0)
        self.assertEqual(highest_priority(g), 4)
        self.assertEqual(lowest_priority(g), 2)

    def test_ticket_breaks_ties_only(self):
        hi = grp("H", ["junior"], options=[("X", 1)], ticket=0.9)
        lo = grp("L", ["junior"], options=[("X", 1)], ticket=0.1)
        res = assign([hi, lo], [Room("x", "X", "F", 1)], average_priority)
        self.assertEqual(res.placements["L0"].hall, "X")
        self.assertIsNone(res.placements["H0"].hall)


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
    def test_groups_and_options_are_valid(self):
        cfg = Config(students=500)
        students, groups, _ = make_campus(cfg, seed=3)
        ids = [s.id for g in groups for s in g.members]
        self.assertEqual(sorted(ids), sorted(s.id for s in students))
        types = {h.name: set(h.room_mix) for h in cfg.halls}
        for g in groups:
            self.assertEqual(len({s.gender for s in g.members}), 1)
            self.assertTrue(1 <= g.size <= 4 and 1 <= g.k <= 6)
            self.assertEqual(sorted(g.ranking), sorted(types))
            self.assertLessEqual(len({h for h, _ in g.options}), g.k)
            for hall, size in g.options:
                self.assertIn(size, types[hall])
                if size < g.size and g.size > 1:
                    self.assertTrue(g.allow_split, "split option listed without consent")

    def test_every_student_placed_once_and_no_room_overflows(self):
        for mech in (assign, assign_v1):
            _, groups, rooms = make_campus(Config(students=500), seed=4)
            draw_tickets(groups, "s")
            res = mech(groups, rooms, average_priority)
            self.assertEqual(len(res.placements), sum(g.size for g in groups))
            self.assertTrue(all(len(r.occupants) <= r.size for r in rooms))
            placed = [o for r in rooms for o in r.occupants]
            self.assertEqual(len(placed), len(set(placed)))


class StrategyProof(unittest.TestCase):
    """No group can get an option it likes more by misreporting its list.

    Covers v2 split options too: a group's true list is its preference order
    over (hall, size) options, and any report is scored against that order.
    """

    def test_no_profitable_misreport(self):
        rng = random.Random(11)
        halls, sizes = ["A", "B"], [1, 2, 3]
        universe = [(h, s) for h in halls for s in sizes]
        for trial in range(40):
            rooms = [Room(f"{h}{s}{i}", h, "F", s)
                     for h in halls for s in sizes for i in range(rng.randint(0, 1))]
            groups = []
            for i in range(4):
                n = rng.randint(1, 3)
                opts = rng.sample(universe, rng.randint(1, 3))
                groups.append(grp(f"g{i}x", [rng.choice(["senior", "freshman"])] * n,
                                  options=opts, ticket=rng.random()))
            for target in groups:
                truth = target.options

                def outcome(report):
                    target.options = list(report)
                    gs = copy.deepcopy(groups)
                    target.options = truth
                    res = assign(gs, copy.deepcopy(rooms), average_priority)
                    p = res.placements[target.members[0].id]
                    if p.hall is None:
                        return len(truth)
                    got = report[p.choice_rank - 1]
                    return truth.index(got) if got in truth else len(truth)

                honest = outcome(truth)
                for k in range(1, 3):
                    for report in itertools.permutations(universe, k):
                        self.assertLessEqual(honest, outcome(report),
                                             f"trial {trial}: {target.id} gains by reporting {report}")


if __name__ == "__main__":
    unittest.main()
