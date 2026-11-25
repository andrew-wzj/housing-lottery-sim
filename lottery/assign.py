"""Priority rules and two assignment mechanisms.

- assign():    v2. Groups rank (hall, room size) options. Random Serial
               Dictatorship over options; splitting only where the group listed it.
- assign_v1(): v1. Groups rank halls only; the room is picked by best fit and a
               group that allowed it is halved automatically when nothing fits.
"""

import hashlib
import random
from typing import Callable, Dict, List, Optional, Set, Tuple

from .model import YEAR_POINTS, Group, Placement, Result, Room, Student

# --- Priority rules (R3 and alternatives compared in the simulation) ------

PriorityRule = Callable[[Group], float]


def average_priority(g: Group) -> float:
    return sum(YEAR_POINTS[s.year] for s in g.members) / g.size


def highest_priority(g: Group) -> float:
    return max(YEAR_POINTS[s.year] for s in g.members)


def lowest_priority(g: Group) -> float:
    return min(YEAR_POINTS[s.year] for s in g.members)


def no_priority(g: Group) -> float:
    """Pure lottery: class year is ignored."""
    return 0.0


RULES: Dict[str, PriorityRule] = {
    "average": average_priority,
    "highest": highest_priority,
    "lowest": lowest_priority,
    "pure lottery": no_priority,
}

# --- Verifiable randomness (R5) -------------------------------------------


def seed_commitment(seed: str) -> str:
    """Published before the draw; anyone can check it against the seed later."""
    return hashlib.sha256(seed.encode()).hexdigest()


def draw_tickets(groups: List[Group], seed: str) -> None:
    """Give each group one ticket (R4). Same seed + same groups = same tickets."""
    rng = random.Random(seed)
    for g in sorted(groups, key=lambda g: g.id):
        g.ticket = rng.random()


def lottery_order(groups: List[Group], rule: PriorityRule) -> List[Group]:
    """Higher priority first; ties broken by the random ticket."""
    for g in groups:
        g.priority = rule(g)
    return sorted(groups, key=lambda g: (-g.priority, g.ticket))


# --- Rooms ----------------------------------------------------------------


class Inventory:
    """Open beds, bucketed by (hall, gender, room size, free beds)."""

    def __init__(self, rooms: List[Room]):
        self.sizes = sorted({r.size for r in rooms})
        self.halls = sorted({r.hall for r in rooms})
        self._buckets: Dict[Tuple[str, str, int, int], List[Room]] = {}
        # Reverse so the last element is the earliest room (deterministic picks).
        for r in reversed(rooms):
            self._add(r)

    def _add(self, r: Room) -> None:
        if r.free > 0:
            self._buckets.setdefault((r.hall, r.gender, r.size, r.free), []).append(r)

    def find(self, hall: str, gender: str, need: int, size: Optional[int] = None,
             exclude: Set[int] = frozenset()) -> Optional[Room]:
        """Best fit: the room with the fewest free beds that holds `need` people.

        With `size`, only rooms of that type count. `exclude` holds id()s of
        rooms already reserved in the same step.
        """
        best = None
        for s in ([size] if size else self.sizes):
            for free in range(need, s + 1):
                for r in reversed(self._buckets.get((hall, gender, s, free), ())):
                    if id(r) not in exclude:
                        if best is None or (free, s) < (best.free, best.size):
                            best = r
                        break
                else:
                    continue
                break
        return best

    def occupy(self, room: Room, student_ids: List[str]) -> None:
        self._buckets[(room.hall, room.gender, room.size, room.free)].remove(room)
        room.occupants.extend(student_ids)
        self._add(room)


def _placement(s: Student, g: Group, hall, room, choice, split, reason="",
               fallback=False) -> Placement:
    rank = g.ranking.index(hall) + 1 if hall in g.ranking else None
    return Placement(s, g.id, hall, room.id if room else None, rank, choice, split,
                     fallback, reason)


# --- v2: (hall, room size) options -----------------------------------------


def pieces(members: List[Student], room_size: int) -> List[List[Student]]:
    """Cut a group into rooms of `room_size`; the last piece may be smaller."""
    return [members[i:i + room_size] for i in range(0, len(members), room_size)]


def assign(groups: List[Group], rooms: List[Room], rule: PriorityRule) -> Result:
    """Random Serial Dictatorship over (hall, room size) options.

    On its turn a group gets the first option on its list that can be filled
    entirely: every piece of the group in its own room of that size, all in
    that hall. Nothing is reserved unless the whole option fits. A group whose
    options all fail goes to the unplaced list. Splitting happens only through
    options the group listed itself.
    """
    inv = Inventory(rooms)
    order = lottery_order(groups, rule)
    placements: Dict[str, Placement] = {}
    splits = 0

    for g in order:
        for choice, (hall, size) in enumerate(g.options, start=1):
            parts = pieces(g.members, size)
            plan, used = [], set()
            for part in parts:
                room = inv.find(hall, g.gender, len(part), size, used)
                if room is None:
                    break
                used.add(id(room))
                plan.append((room, part))
            else:
                split = len(parts) > 1
                splits += split
                for room, part in plan:
                    inv.occupy(room, [s.id for s in part])
                    for s in part:
                        placements[s.id] = _placement(s, g, hall, room, choice, split)
                break
        else:
            if g.fallback and _place_anywhere(inv, g, placements):
                continue
            for s in g.members:
                placements[s.id] = _placement(s, g, None, None, None, False,
                                              "no listed option could be filled")
    return Result(placements=placements, order=[g.id for g in order], splits=splits)


def _place_anywhere(inv: Inventory, g: Group, placements: Dict[str, Placement]) -> bool:
    """Fallback ("place us anywhere"): the tightest room in any hall that holds
    the whole group. Halls are tried in a fixed public order, not the group's
    taste, since the group did not rank them. If the whole group fits nowhere
    and it ticked "you may split us", it is halved and each half tries again.
    Halves are reserved together: if any member cannot be placed, nothing is.
    """
    plan = _plan_anywhere(inv, g.members, g.gender, g.fallback_split, set())
    if plan is None:
        return False
    split = len(plan) > 1
    for room, part in plan:
        inv.occupy(room, [s.id for s in part])
        for s in part:
            placements[s.id] = _placement(s, g, room.hall, room, None, split, fallback=True)
    return True


def _plan_anywhere(inv: Inventory, members: List[Student], gender: str, may_split: bool,
                   used: Set[int]) -> Optional[List[Tuple[Room, List[Student]]]]:
    best = None
    for hall in inv.halls:
        room = inv.find(hall, gender, len(members), exclude=used)
        if room is not None and (best is None or room.free < best.free):
            best = room
    if best is not None:
        used.add(id(best))
        return [(best, members)]
    if not may_split or len(members) == 1:
        return None
    half = (len(members) + 1) // 2
    first = _plan_anywhere(inv, members[:half], gender, may_split, used)
    if first is None:
        return None
    second = _plan_anywhere(inv, members[half:], gender, may_split, used)
    if second is None:
        return None
    return first + second


# --- v1: halls only, automatic split ---------------------------------------


def assign_v1(groups: List[Group], rooms: List[Room], rule: PriorityRule) -> Result:
    """The first design: rank halls, best-fit room, halve the group if needed."""
    inv = Inventory(rooms)
    order = lottery_order(groups, rule)
    placements: Dict[str, Placement] = {}
    split_groups: Set[str] = set()

    def place(g: Group, members: List[Student], was_split: bool) -> None:
        for choice, hall in enumerate(g.halls, start=1):
            room = inv.find(hall, g.gender, len(members))
            if room is not None:
                inv.occupy(room, [s.id for s in members])
                for s in members:
                    placements[s.id] = _placement(s, g, hall, room, choice, was_split)
                return
        if g.allow_split and len(members) > 1:
            split_groups.add(g.id)
            half = (len(members) + 1) // 2
            # Both halves keep the group's place in line and try right away.
            place(g, members[:half], True)
            place(g, members[half:], True)
            return
        for s in members:
            placements[s.id] = _placement(s, g, None, None, None, was_split,
                                          "no fitting bed in ranked halls")

    for g in order:
        place(g, g.members, False)
    return Result(placements=placements, order=[g.id for g in order], splits=len(split_groups))
