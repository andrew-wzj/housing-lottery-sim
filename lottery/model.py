"""Data model for the housing lottery."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Class-year points used for group priority (rule R3).
YEAR_POINTS = {"senior": 4, "junior": 3, "sophomore": 2, "freshman": 1}
YEARS = ["senior", "junior", "sophomore", "freshman"]


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
    prefs: List[str]          # ranked hall names, 1 to 6 of them
    allow_split: bool         # rule R7
    ticket: float = 0.0       # random lottery number, one per group (R4)
    priority: float = 0.0     # filled in by the priority rule (R3)

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
    hall: Optional[str]       # None if unplaced
    room_id: Optional[str]
    choice_rank: Optional[int]  # 1 = first choice; None if unplaced
    was_split: bool = False
    reason: str = ""


@dataclass
class Result:
    placements: Dict[str, Placement]  # by student id
    order: List[str]                  # group ids in processing order
    splits: int = 0                   # number of split operations
