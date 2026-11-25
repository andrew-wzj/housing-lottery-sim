"""Synthetic campus generator. All names and numbers are made up.

No real halls, students or data from any college are used.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .model import YEARS, Group, Option, Room, Student


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
    want_single_share: float = 0.40   # solo applicants who prefer a single to a double
    fallback_share: float = 0.50      # groups that tick "place us anywhere if all options are full"
    together_first_share: float = 0.50   # split-willing groups that keep the group together first
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

        # True taste: a full ranking of all halls (Plackett-Luce draw from
        # popularity with personal noise). The group lists its top k.
        remaining = {h.name: h.popularity * rng.lognormvariate(0, cfg.taste_noise) for h in halls}
        ranking = []
        while remaining:
            name = rng.choices(list(remaining), weights=list(remaining.values()))[0]
            ranking.append(name)
            del remaining[name]
        k = _pick(rng, cfg.pref_counts)
        allow_split = rng.random() < cfg.allow_split_share
        g = Group(f"g{len(groups):04d}", members, ranking, k, allow_split)
        g.options = make_options(g, cfg, rng)
        g.fallback_draw = rng.random()   # kept so a sweep can vary the share on the same campus
        g.fallback = g.fallback_draw < cfg.fallback_share
        g.fallback_split = g.fallback and allow_split
        groups.append(g)
    return groups


def make_options(g: Group, cfg: Config, rng: random.Random) -> List[Option]:
    """Turn a group's taste into a v2 list of (hall, room size) options.

    Assumption: because v2 shows room types on the form, a group lists its k
    favorite halls among those with at least one usable option for it.
    - A group lists the tightest room type that fits all of it.
    - Groups that accept splitting also list the largest smaller room type;
      some try every hall together before splitting ("together first"),
      the rest split before leaving a hall ("hall first").
    - Solo applicants list both singles and doubles where a hall has both;
      some put the single first.
    """
    types = {h.name: sorted(h.room_mix) for h in cfg.halls}
    together_first = rng.random() < cfg.together_first_share
    want_single = rng.random() < cfg.want_single_share
    together, split, per_hall = [], [], []
    listed = 0
    for hall in g.ranking:
        if listed == g.k:
            break
        t = types[hall]
        opts = []
        if g.size == 1:
            solo = [s for s in t if s <= 2]
            opts = [(hall, s) for s in (solo if want_single else sorted(solo, reverse=True))]
        else:
            fit = [s for s in t if s >= g.size]
            smaller = [s for s in t if 2 <= s < g.size] or [s for s in t if s < g.size]
            if fit:
                opts.append((hall, fit[0]))
                together.append((hall, fit[0]))
            if g.allow_split and smaller:
                opts.append((hall, smaller[-1]))
                split.append((hall, smaller[-1]))
        if opts:
            listed += 1
            per_hall.extend(opts)
    if g.size > 1 and together_first:
        return together + split
    return per_hall


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
