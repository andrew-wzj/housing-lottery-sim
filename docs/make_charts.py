"""Draw the case-study charts as static SVG from results/summary.csv.

    python3 docs/make_charts.py

Standard library only. Colors follow a validated categorical palette
(slot 1 blue, slot 2 orange) with separate light and dark steps.
"""

import csv
import os
from collections import defaultdict
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "img")

STYLE = """
<style>
  svg { --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --grid:#e6e5e0;
        --s1:#2a78d6; --s2:#eb6834; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  @media (prefers-color-scheme: dark) {
    svg { --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --grid:#3a3936;
          --s1:#3987e5; --s2:#d95926; }
  }
  .bg { fill: var(--surface); }
  .t { fill: var(--ink); font-size: 15px; font-weight: 600; }
  .lab { fill: var(--ink2); font-size: 13px; }
  .val { fill: var(--ink); font-size: 12px; }
  .grid { stroke: var(--grid); stroke-width: 1; }
  .axis { stroke: var(--ink2); stroke-width: 1; }
  .s1 { fill: var(--s1); } .s2 { fill: var(--s2); }
  .l1 { stroke: var(--s1); fill: none; stroke-width: 2; }
  .l2 { stroke: var(--s2); fill: none; stroke-width: 2; }
  .d1 { fill: var(--s1); stroke: var(--surface); stroke-width: 2; }
  .d2 { fill: var(--s2); stroke: var(--surface); stroke-width: 2; }
</style>
"""


def load():
    data = defaultdict(dict)
    with open(os.path.join(ROOT, "results", "summary.csv")) as f:
        for row in csv.DictReader(f):
            data[row["rule"]][row["metric"]] = float(row["mean"])
    return data


def svg(name, w, h, title, desc, body):
    os.makedirs(OUT, exist_ok=True)
    text = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t d">{STYLE}'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            f'<rect class="bg" width="{w}" height="{h}" rx="8"/>'
            f'<text class="t" x="24" y="32">{escape(title)}</text>{body}</svg>\n')
    with open(os.path.join(OUT, name), "w") as f:
        f.write(text)


def legend(x, y, items):
    out, cx = [], x
    for cls, label in items:
        out.append(f'<rect class="{cls}" x="{cx}" y="{y - 10}" width="12" height="12" rx="3"/>'
                   f'<text class="lab" x="{cx + 18}" y="{y}">{escape(label)}</text>')
        cx += 30 + 7.5 * len(label)
    return "".join(out)


def hbars(name, title, desc, cats, series, vmax, fmt=lambda v: f"{v:.0f}%", w=720):
    """Grouped horizontal bars. series = [(css class, label, [values])]."""
    left, right, top = 150, 70, 76
    bar, gap, group_gap = 14, 2, 18
    group_h = len(series) * bar + (len(series) - 1) * gap
    h = top + len(cats) * (group_h + group_gap) + 34
    plot_w = w - left - right
    x = lambda v: left + plot_w * v / vmax
    body = [legend(24, 58, [(c, l) for c, l, _ in series])] if len(series) > 1 else []
    for t in range(0, int(vmax) + 1, 20 if vmax > 40 else 10):
        body.append(f'<line class="grid" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 6}" y2="{h - 30}"/>'
                    f'<text class="lab" x="{x(t):.1f}" y="{h - 12}" text-anchor="middle">{t}%</text>')
    y = top
    for i, cat in enumerate(cats):
        body.append(f'<text class="lab" x="{left - 10}" y="{y + group_h / 2 + 4}" text-anchor="end">{escape(cat)}</text>')
        for j, (cls, _, vals) in enumerate(series):
            by = y + j * (bar + gap)
            v = vals[i]
            body.append(f'<rect class="{cls}" x="{left}" y="{by}" width="{max(x(v) - left, 1):.1f}" height="{bar}" rx="3">'
                        f'<title>{escape(cat)}: {fmt(v)}</title></rect>'
                        f'<text class="val" x="{x(v) + 6:.1f}" y="{by + bar - 3}">{fmt(v)}</text>')
        y += group_h + group_gap
    body.append(f'<line class="axis" x1="{left}" x2="{left}" y1="{top - 6}" y2="{h - 30}"/>')
    svg(name, w, h, title, desc, "".join(body))


def diverging_bars(name, title, desc, cats, vals, lo, hi, w=720):
    left, right, top, bar, gap = 150, 70, 60, 18, 14
    h = top + len(cats) * (bar + gap) + 34
    plot_w = w - left - right
    x = lambda v: left + plot_w * (v - lo) / (hi - lo)
    body = []
    for t in range(int(lo), int(hi) + 1, 10):
        body.append(f'<line class="grid" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 6}" y2="{h - 30}"/>'
                    f'<text class="lab" x="{x(t):.1f}" y="{h - 12}" text-anchor="middle">{t:+d}</text>')
    y = top
    for cat, v in zip(cats, vals):
        x0, x1 = sorted((x(0), x(v)))
        anchor, tx = ("start", x1 + 6) if v >= 0 else ("end", x0 - 6)
        body.append(f'<text class="lab" x="{left - 10}" y="{y + bar - 4}" text-anchor="end">{escape(cat)}</text>'
                    f'<rect class="s1" x="{x0:.1f}" y="{y}" width="{max(x1 - x0, 1):.1f}" height="{bar}" rx="3">'
                    f'<title>{escape(cat)}: {v:+.1f} points</title></rect>'
                    f'<text class="val" x="{tx:.1f}" y="{y + bar - 4}" text-anchor="{anchor}">{v:+.1f}</text>')
        y += bar + gap
    body.append(f'<line class="axis" x1="{x(0):.1f}" x2="{x(0):.1f}" y1="{top - 6}" y2="{h - 30}"/>')
    svg(name, w, h, title, desc, "".join(body))


def lines(name, title, desc, xs, series, vmax, xlabel, w=720, h=340):
    left, right, top, bottom = 60, 150, 70, 56
    plot_w, plot_h = w - left - right, h - top - bottom
    X = lambda i: left + plot_w * i / (len(xs) - 1)
    Y = lambda v: top + plot_h * (1 - v / vmax)
    body = [legend(24, 56, [(c.replace("l", "s"), l) for c, _, l, _ in series])]
    for t in range(0, int(vmax) + 1, 10):
        body.append(f'<line class="grid" x1="{left}" x2="{left + plot_w}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>'
                    f'<text class="lab" x="{left - 8}" y="{Y(t) + 4:.1f}" text-anchor="end">{t}%</text>')
    for i, xv in enumerate(xs):
        body.append(f'<text class="lab" x="{X(i):.1f}" y="{top + plot_h + 20}" text-anchor="middle">{xv}</text>')
    body.append(f'<text class="lab" x="{left + plot_w / 2:.1f}" y="{h - 10}" text-anchor="middle">{escape(xlabel)}</text>')
    for lcls, dcls, label, vals in series:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        body.append(f'<polyline class="{lcls}" points="{pts}"/>')
        for i, v in enumerate(vals):
            body.append(f'<circle class="{dcls}" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="5">'
                        f'<title>{escape(label)}, {xs[i]}: {v:.1f}%</title></circle>')
        body.append(f'<text class="val" x="{X(0) + 12:.1f}" y="{Y(vals[0]) - 8:.1f}">{vals[0]:.0f}%</text>')
    end = max(series, key=lambda s: s[3][-1])
    body.append(f'<text class="val" x="{X(len(xs) - 1) + 12:.1f}" y="{Y(end[3][-1]) + 4:.1f}">'
                f'both {end[3][-1]:.0f}%</text>')
    svg(name, w, h, title, desc, "".join(body))


def main():
    d = load()
    years = ["senior", "junior", "sophomore", "freshman"]
    hbars("first-choice-by-year.svg",
          "Students who got their first-choice hall",
          "Average class-year priority versus a pure lottery, by class year. Mean of 1,000 simulated lotteries.",
          [y.title() for y in years],
          [("s1", "Average class-year priority", [100 * d["average"][f"{y}.first"] for y in years]),
           ("s2", "Pure lottery", [100 * d["pure lottery"][f"{y}.first"] for y in years])],
          100)

    rules = ["highest", "average", "lowest", "pure lottery"]
    names = {"highest": "Highest (2023)", "average": "Average (2026)", "lowest": "Lowest",
             "pure lottery": "Pure lottery"}
    gaps = [100 * (d[r]["underclass_in_mixed.first"] - d[r]["underclass_in_same.first"]) for r in rules]
    diverging_bars("carry-effect.svg",
                   "Gain from grouping with older students (points)",
                   "First-choice rate of sophomores and freshmen in mixed-year groups minus same-year groups, by priority rule.",
                   [names[r] for r in rules], gaps, -20, 30)

    ks = [1, 2, 3, 4, 5, 6]
    lines("short-list-risk.svg",
          "Students left without a bed, by halls listed",
          "Unplaced rate by number of halls a group listed, with no group using the fallback and with every group using it.",
          ks,
          [("l2", "d2", "No fallback", [100 * d["fallback 0%"][f"ranked_{k}.unplaced"] for k in ks]),
           ("l1", "d1", "Every group ticks the fallback", [100 * d["fallback 100%"][f"ranked_{k}.unplaced"] for k in ks])],
          30, "Halls listed by the group")


if __name__ == "__main__":
    main()
