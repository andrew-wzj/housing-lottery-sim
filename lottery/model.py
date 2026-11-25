"""Data model for the housing lottery."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Class-year points used for group priority (rule R3).
YEAR_POINTS = {"senior": 4, "junior": 3, "sophomore": 2, "freshman": 1}
YEARS = ["senior", "junior", "sophomore", "freshman"]

# One line on a group's ranked list: (hall, room size).
# If the room size is smaller than the group, choosing it means the group agrees
# to split into rooms of that size, all in that hall.
Option = Tuple[str, int]


@dataclass
class Student:
    id: str
    year: str     # one of YEARS
    gender: str   # housing gender category, e.g. "F" or "M"


@dataclass
class Group:
    """A confirmed roommate group (rules R1 and R2: confirmed, one gender)."""

    id: str
    members: List[Student]
    ranking: List[str]        # the group's true ranking of every hall (used to score outcomes)
    k: int                    # how many halls the group lists (1 to 6)
    allow_split: bool         # v1 rule R7; in v2 consent is given per option instead
    options: List[Option] = field(default_factory=list)   # v2 ranked list
    fallback: bool = False    # v2: "if all my options are full, place us anywhere"
    fallback_split: bool = False  # v2: "...and you may split us if needed"
    fallback_draw: float = 1.0  # simulation only: lets a sweep vary how many groups tick it
    ticket: float = 0.0       # random lottery number, one per group (R4)
    priority: float = 0.0     # filled in by the priority rule (R3)

    @property
    def halls(self) -> List[str]:
        """The v1 list: the group's top k halls."""
        return self.ranking[:self.k]

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def gender(self) -> str:
        return self.members[0].gender


@dataclass
class Room:
    id: str
    hall: str
    gender: str
    size: int
    occupants: List[str] = field(default_factory=list)

    @property
    def free(self) -> int:
        return self.size - len(self.occupants)


@dataclass
class Placement:
    """Where one student ended up."""

    student: Student
    group_id: str
    hall: Optional[str]         # None if unplaced
    room_id: Optional[str]
    hall_rank: Optional[int]    # position of the hall in the group's true ranking (1 = favorite)
    choice_rank: Optional[int]  # which line of the submitted list was used
    was_split: bool = False
    via_fallback: bool = False
    reason: str = ""


@dataclass
class Result:
    placements: Dict[str, Placement]  # by student id
    order: List[str]                  # group ids in processing order
    splits: int = 0                   # number of groups that were split
