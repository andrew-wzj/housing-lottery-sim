"""Turn one assignment result into the numbers the case study reports."""

from typing import Dict, List

from .model import YEAR_POINTS, YEARS, Group, Result


def summarize(groups: List[Group], result: Result) -> Dict[str, float]:
    """Rates are shares of students (0-1). Keys look like 'senior.first'.

    'first' means the student got the hall the group truly likes best.
    """
    out: Dict[str, float] = {}
    by_year = {y: [] for y in YEARS}
    for p in result.placements.values():
        by_year[p.student.year].append(p)

    def rates(prefix: str, ps) -> None:
        n = len(ps) or 1
        out[f"{prefix}.first"] = sum(p.hall_rank == 1 for p in ps) / n
        out[f"{prefix}.top3"] = sum(p.hall_rank is not None and p.hall_rank <= 3 for p in ps) / n
        out[f"{prefix}.unplaced"] = sum(p.hall is None for p in ps) / n
        out[f"{prefix}.split"] = sum(p.was_split for p in ps) / n

    for y in YEARS:
        rates(y, by_year[y])
    rates("all", list(result.placements.values()))

    # Mixed-year groups: does the youngest member gain or lose by grouping up?
    mixed_young, same_young = [], []
    for g in groups:
        years = {s.year for s in g.members}
        youngest = min(g.members, key=lambda s: YEAR_POINTS[s.year])
        target = mixed_young if len(years) > 1 else same_young
        # Compare like with like: only underclass members (sophomores, freshmen).
        if YEAR_POINTS[youngest.year] <= 2:
            target.extend(result.placements[s.id] for s in g.members if s.year == youngest.year)
    rates("underclass_in_mixed", mixed_young)
    rates("underclass_in_same", same_young)

    # How risky is a short list? Unplaced rate by number of halls ranked.
    by_len = {}
    for g in groups:
        by_len.setdefault(g.k, []).extend(result.placements[s.id] for s in g.members)
    for k, ps in by_len.items():
        out[f"ranked_{k}.unplaced"] = sum(p.hall is None for p in ps) / len(ps)
    out["groups.split"] = result.splits
    return out
