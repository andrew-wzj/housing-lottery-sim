"""Run many lotteries on synthetic campuses and compare priority rules.

    python3 simulate.py --trials 1000 --out results

Rules "average", "highest", "lowest" and "pure lottery" use the v2 mechanism
(groups rank hall + room size). The row "v1: halls only" re-runs the first
design (rank halls, automatic split) with the average rule, for comparison.

Each trial builds one campus (students, groups, rooms), draws one set of
tickets, then runs the assignment once per priority rule on a fresh copy of
the rooms. Using the same campus and tickets for every rule means the rules
are compared on identical inputs.
"""

import argparse
import copy
import csv
import os
import statistics
import time
from typing import Dict, List

from lottery.assign import RULES, assign, assign_v1, average_priority, draw_tickets, seed_commitment
from lottery.generate import Config, make_campus
from lottery.metrics import summarize
from lottery.model import YEARS


V1 = "v1: halls only (average)"
FALLBACK_SHARES = [0.0, 0.25, 0.5, 0.75, 1.0]


def run(trials: int, cfg: Config, base_seed: int) -> Dict[str, Dict[str, List[float]]]:
    data: Dict[str, Dict[str, List[float]]] = {r: {} for r in RULES}
    data[V1] = {}
    for t in range(trials):
        _, groups, rooms = make_campus(cfg, seed=base_seed + t)
        draw_tickets(groups, seed=f"trial-{base_seed + t}")
        for name, rule in RULES.items():
            res = assign(groups, copy.deepcopy(rooms), rule)
            for k, v in summarize(groups, res).items():
                data[name].setdefault(k, []).append(v)
        res = assign_v1(groups, copy.deepcopy(rooms), average_priority)
        for k, v in summarize(groups, res).items():
            data[V1].setdefault(k, []).append(v)
        # Fallback sweep: same campus and tickets, only the share of groups
        # that tick "place us anywhere" changes.
        for share in FALLBACK_SHARES:
            for g in groups:
                g.fallback = g.fallback_draw < share
                g.fallback_split = g.fallback and g.allow_split
            res = assign(groups, copy.deepcopy(rooms), average_priority)
            key = f"fallback {share:.0%}"
            for k, v in summarize(groups, res).items():
                data.setdefault(key, {}).setdefault(k, []).append(v)
        for g in groups:
            g.fallback = g.fallback_draw < cfg.fallback_share
            g.fallback_split = g.fallback and g.allow_split
    return data


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def write_outputs(data, out_dir: str, trials: int, cfg: Config, seconds: float) -> str:
    os.makedirs(out_dir, exist_ok=True)
    # Long-format CSV: one row per rule x metric, with mean and spread.
    with open(os.path.join(out_dir, "summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rule", "metric", "mean", "stdev", "p5", "p95"])
        for rule, metrics in data.items():
            for k, vals in metrics.items():
                s = sorted(vals)
                w.writerow([rule, k, f"{statistics.mean(vals):.4f}",
                            f"{statistics.pstdev(vals):.4f}",
                            f"{s[int(0.05 * (len(s) - 1))]:.4f}",
                            f"{s[int(0.95 * (len(s) - 1))]:.4f}"])

    def m(rule: str, key: str) -> float:
        vals = [v for v in data[rule][key] if v == v]   # drop NaN (no fallback placements)
        return statistics.mean(vals) if vals else float("nan")

    main = list(RULES) + [V1]
    lines = [
        "# Simulation results",
        "",
        f"{trials} trials, {cfg.students} students each, {cfg.bed_ratio:.2f} beds per student, "
        f"{len(cfg.halls)} halls. Runtime {seconds:.1f}s.",
        "All data is synthetic. Numbers are means over trials.",
        "",
        "## First-choice hall, by class year",
        "",
        "| Rule | " + " | ".join(y.title() for y in YEARS) + " | All |",
        "|---|" + "---:|" * (len(YEARS) + 1),
    ]
    for rule in main:
        lines.append(f"| {rule} | " + " | ".join(pct(m(rule, f'{y}.first')) for y in YEARS)
                     + f" | {pct(m(rule, 'all.first'))} |")
    lines += ["", "## Top-3 hall, by class year", "",
              "| Rule | " + " | ".join(y.title() for y in YEARS) + " | All |",
              "|---|" + "---:|" * (len(YEARS) + 1)]
    for rule in main:
        lines.append(f"| {rule} | " + " | ".join(pct(m(rule, f'{y}.top3')) for y in YEARS)
                     + f" | {pct(m(rule, 'all.top3'))} |")
    lines += ["", "## Unplaced and split students", "",
              "| Rule | Unplaced | In a split group | Groups split per lottery |",
              "|---|---:|---:|---:|"]
    for rule in main:
        lines.append(f"| {rule} | {pct(m(rule, 'all.unplaced'))} | {pct(m(rule, 'all.split'))} "
                     f"| {m(rule, 'groups.split'):.1f} |")
    lines += ["", "## Does joining an older group help underclass students?", "",
              "First-choice rate of sophomores and freshmen, depending on whether their group",
              "has older members.", "",
              "| Rule | In a mixed-year group | In a same-year group | Gap |",
              "|---|---:|---:|---:|"]
    for rule in RULES:
        a, b = m(rule, "underclass_in_mixed.first"), m(rule, "underclass_in_same.first")
        lines.append(f"| {rule} | {pct(a)} | {pct(b)} | {100 * (a - b):+.1f} pts |")
    lines += ["", "## How risky is a short list?", "",
              "Share of students left unplaced, by how many halls their group listed (average rule).", "",
              "| Mechanism | " + " | ".join(str(k) for k in range(1, 7)) + " |",
              "|---|" + "---:|" * 6]
    for rule, label in (("average", "v2: hall + room size"), (V1, "v1: halls only")):
        lines.append(f"| {label} | " + " | ".join(pct(m(rule, f"ranked_{k}.unplaced")) for k in range(1, 7)) + " |")
    lines += ["", "## The fallback option", "",
              "Share of groups that tick \"if all our options are full, place us anywhere\"",
              "(average rule, v2). Groups that accept splitting also tick \"you may split us\".",
              "Same campuses and tickets in every column.", "",
              "| Groups that tick it | " + " | ".join(f"{x:.0%}" for x in FALLBACK_SHARES) + " |",
              "|---|" + "---:|" * len(FALLBACK_SHARES)]
    keys = [f"fallback {x:.0%}" for x in FALLBACK_SHARES]
    rows = [("Unplaced, all students", "all.unplaced", pct),
            ("Unplaced, listed 1 hall", "ranked_1.unplaced", pct),
            ("Placed by the fallback", "all.fallback", pct),
            ("Unplaced, groups of 4", "size_4.unplaced", pct),
            ("First-choice hall, all", "all.first", pct),
            ("Fallback hall, rank in own taste (1-6)", "fallback.mean_hall_rank",
             lambda x: "n/a" if x != x else f"{x:.1f}")]
    for label, key, fmt in rows:
        lines.append(f"| {label} | " + " | ".join(fmt(m(k, key)) for k in keys) + " |")
    lines += ["", "## Verifiable draw (rule R5)", "",
              "Example: before the draw, publish the commitment; after, publish the seed.", "",
              f"- seed: `trial-{0}`", f"- SHA-256 commitment: `{seed_commitment('trial-0')}`", ""]
    text = "\n".join(lines)
    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write(text)
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=1000)
    ap.add_argument("--students", type=int, default=1000)
    ap.add_argument("--bed-ratio", type=float, default=1.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    cfg = Config(students=args.students, bed_ratio=args.bed_ratio)
    start = time.time()
    data = run(args.trials, cfg, args.seed)
    print(write_outputs(data, args.out, args.trials, cfg, time.time() - start))


if __name__ == "__main__":
    main()
