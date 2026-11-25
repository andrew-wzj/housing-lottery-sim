"""Synthetic campus generator. All names and numbers are made up.

No real halls, students or data from any college are used.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .model import YEARS, Group, Room, Student


@dataclass
class HallSpec:
    name: str
    popularity: float            # relative appeal; higher = more students want it
    room_mix: Dict[int, float]   # room size -> share of beds in that size


@dataclass
class Config:
    students: int = 1000
    bed_ratio: float = 1.05      # total beds / students
    year_mix: Dict[str, float] = field(default_factory=lambda: {
        "senior": 0.22, "junior": 0.25, "sophomore": 0.27, "freshman": 0.26})
    female_share: float = 0.55
    # Share of groups of each size (a "group" of 1 is a solo applicant).
    group_sizes: Dict[int, float] = field(default_factory=lambda: {
        1: 0.30, 2: 0.40, 3: 0.15, 4: 0.15})
    same_year_share: float = 0.80   # chance a group is all one class year
    # How many halls a group ranks (rule: 1 to 6, not forced to fill all six).
    pref_counts: Dict[int, float] = field(default_factory=lambda: {
        1: 0.05, 2: 0.10, 3: 0.25, 4: 0.20, 5: 0.15, 6: 0.25})
    allow_split_share: float = 0.70
    taste_noise: float = 0.6     # 0 = everyone agrees on popularity; higher = more varied tastes
    halls: List[HallSpec] = field(default_factory=lambda: [
        HallSpec("Alder", 3.0, {2: 0.4, 4: 0.6}),          # new suites, most wanted
        HallSpec("Birch", 2.2, {1: 0.2, 2: 0.8}),          # singles and doubles
        HallSpec("Cedar", 1.6, {2: 0.7, 3: 0.3}),
        HallSpec("Maple", 1.2, {2: 0.6, 3: 0.2, 4: 0.2}),
        HallSpec("Oak", 1.0, {2: 1.0}),
        HallSpec("Willow", 0.7, {2: 0.5, 3: 0.5}),         # farthest from campus
    ])


def _pick(rng: random.Random, weights: Dict) -> object:
    keys = list(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys])[0]


def make_students(cfg: Config, rng: random.Random) -> List[Student]:
    out = []
    for i in range(cfg.students):
        year = _pick(rng, cfg.year_mix)
        gender = "F" if rng.random() < cfg.female_share else "M"
        out.append(Student(f"s{i:04d}", year, gender))
    return out


def make_groups(students: List[Student], cfg: Config, rng: random.Random) -> List[Group]:
    """Form confirmed, single-gender groups; most are same-year, some mixed."""
    pools: Dict[Tuple[str, str], List[Student]] = {}
    for s in students:
        pools.setdefault((s.gender, s.year), []).append(s)
    for pool in pools.values():
        rng.shuffle(pool)

    order = students[:]
    rng.shuffle(order)
    taken = set()
    groups = []
    halls = cfg.halls
    for leader in order:
        if leader.id in taken:
            continue
        taken.add(leader.id)
        size = _pick(rng, cfg.group_sizes)
        same_year = rng.random() < cfg.same_year_share
        members = [leader]
        while len(members) < size:
            year = leader.year if same_year else _pick(rng, cfg.year_mix)
            pool = pools[(leader.gender, year)]
            while pool and pool[-1].id in taken:
                pool.pop()
            if not pool:
                break
            mate = pool.pop()
            taken.add(mate.id)
            members.append(mate)

        # Rank halls: Plackett-Luce draw from popularity with personal noise.
        appeal = {h.name: h.popularity * rng.lognormvariate(0, cfg.taste_noise) for h in halls}
        k = _pick(rng, cfg.pref_counts)
        prefs = []
        remaining = dict(appeal)
        for _ in range(min(k, len(halls))):
            name = rng.choices(list(remaining), weights=list(remaining.values()))[0]
            prefs.append(name)
            del remaining[name]
        groups.append(Group(f"g{len(groups):04d}", members, prefs,
                            allow_split=rng.random() < cfg.allow_split_share))
    return groups


def make_rooms(students: List[Student], cfg: Config) -> List[Room]:
    """Split beds across halls and genders in proportion to demand."""
    n_f = sum(s.gender == "F" for s in students)
    total_beds = round(len(students) * cfg.bed_ratio)
    per_hall = total_beds / len(cfg.halls)
    rooms = []
    for h in cfg.halls:
        for gender, share in (("F", n_f / len(students)), ("M", 1 - n_f / len(students))):
            beds = per_hall * share
            for size, frac in sorted(h.room_mix.items()):
                count = max(1, round(beds * frac / size))
                for i in range(count):
                    rooms.append(Room(f"{h.name}-{gender}{size}-{i:03d}", h.name, gender, size))
    return rooms


def make_campus(cfg: Config, seed: int):
    rng = random.Random(seed)
    students = make_students(cfg, rng)
    groups = make_groups(students, cfg, rng)
    rooms = make_rooms(students, cfg)
    return students, groups, rooms
