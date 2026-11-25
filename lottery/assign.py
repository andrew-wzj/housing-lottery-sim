"""Priority rules and the Random Serial Dictatorship assignment (section 3)."""

import hashlib
import random
from typing import Callable, Dict, List, Optional, Tuple

from .model import YEAR_POINTS, Group, Placement, Result, Room

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
    """Open beds, bucketed by (hall, gender, free beds) for O(1) best-fit lookup."""

    def __init__(self, rooms: List[Room]):
        self.max_size = max((r.size for r in rooms), default=0)
        self._buckets: Dict[Tuple[str, str, int], List[Room]] = {}
        # Reverse so pop() returns rooms in their original order (deterministic).
        for r in reversed(rooms):
            if r.free > 0:
                self._buckets.setdefault((r.hall, r.gender, r.free), []).append(r)

    def best_fit(self, hall: str, gender: str, need: int) -> Optional[Room]:
        """The room with the fewest free beds that still fits `need` people."""
        for free in range(need, self.max_size + 1):
            bucket = self._buckets.get((hall, gender, free))
            if bucket:
                return bucket[-1]
        return None

    def occupy(self, room: Room, student_ids: List[str]) -> None:
        bucket = self._buckets[(room.hall, room.gender, room.free)]
        bucket.pop()
        room.occupants.extend(student_ids)
        if room.free > 0:
            self._buckets.setdefault((room.hall, room.gender, room.free), []).append(room)


# --- Assignment -----------------------------------------------------------


def assign(groups: List[Group], rooms: List[Room], rule: PriorityRule) -> Result:
    """Random Serial Dictatorship with best-fit rooms and optional splitting.

    Groups must already have tickets (see draw_tickets).
    Rooms are modified in place (occupants are filled in).
    """
    inv = Inventory(rooms)
    order = lottery_order(groups, rule)
    placements: Dict[str, Placement] = {}
    splits = 0

    def place(g: Group, members, was_split: bool) -> None:
        nonlocal splits
        for rank, hall in enumerate(g.prefs, start=1):
            room = inv.best_fit(hall, g.gender, len(members))
            if room is not None:
                inv.occupy(room, [s.id for s in members])
                for s in members:
                    placements[s.id] = Placement(s, g.id, hall, room.id, rank, was_split)
                return
        if g.allow_split and len(members) > 1:
            splits += 1
            half = (len(members) + 1) // 2
            # Both halves keep the group's place in line and try right away.
            place(g, members[:half], True)
            place(g, members[half:], True)
            return
        for s in members:
            placements[s.id] = Placement(s, g.id, None, None, None, was_split,
                                         reason="no fitting bed in ranked halls")

    for g in order:
        place(g, g.members, False)
    return Result(placements=placements, order=[g.id for g in order], splits=splits)
