#!/usr/bin/env python3
"""
Render data/contributions.json as a 53-week x 7-day animated SVG calendar,
GitHub-green ramp, boxes sliding in diagonally (line-after-line, plays once
then freezes -- CSS keyframes with staggered animation-delay).
Output: contrib-heatmap.svg (repo root).
"""
import json
import os
from datetime import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#           none    -> ................................. -> brightest (neon top end)

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
MONTH_LABEL_H = 16

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")


def load():
    with open(DATA_PATH) as f:
        return json.load(f)


def build_weeks(days):
    """Bucket days into weeks (columns), Sunday-first, matching GitHub's grid."""
    by_date = {d["date"]: d["level"] for d in days}
    dates = sorted(by_date.keys())
    if not dates:
        return []

    start = datetime.strptime(dates[0], "%Y-%m-%d").date()
    # rewind to the preceding Sunday so week columns align
    start = start.fromordinal(start.toordinal() - (start.weekday() + 1) % 7)
    end = datetime.strptime(dates[-1], "%Y-%m-%d").date()

    weeks = []
    cur_week = []
    d = start
    while d <= end:
        ds = d.isoformat()
        level = by_date.get(ds)
        cur_week.append({"date": ds, "level": level})
        if len(cur_week) == 7:
            weeks.append(cur_week)
            cur_week = []
        d = d.fromordinal(d.toordinal() + 1)
    if cur_week:
        while len(cur_week) < 7:
            cur_week.append({"date": None, "level": None})
        weeks.append(cur_week)
    return weeks


def month_labels(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        for day in week:
            if day["date"] is None:
                continue
            m = day["date"][:7]
            if m != last_month:
                labels.append((wi, day["date"][5:7]))
                last_month = m
            break
    month_names = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
        "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
    }
    return [(wi, month_names[m]) for wi, m in labels]


def render(payload):
    days = payload["days"]
    stats = payload["stats"]
    username = payload.get("username", "")
    weeks = build_weeks(days)
    n_weeks = len(weeks)

    grid_w = n_weeks * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    width = LEFT_PAD + grid_w + 20
    height = TOP_PAD + MONTH_LABEL_H + grid_h + 46

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
    )
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="#0d1117"/>')

    # month labels
    for wi, name in month_labels(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        svg_parts.append(
            f'<text x="{x}" y="{TOP_PAD + 10}" fill="#7d8590" font-size="10">{name}</text>'
        )

    # day cells, staggered diagonal reveal: delay = (week_index + day_index) * step
    step = 0.012
    max_delay = 0
    grid_top = TOP_PAD + MONTH_LABEL_H
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day["date"] is None:
                continue
            level = day["level"] or 0
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = LEFT_PAD + wi * (CELL + GAP)
            y = grid_top + di * (CELL + GAP)
            delay = (wi + di) * step
            max_delay = max(max_delay, delay)
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                f'fill="{color}" opacity="0" class="cell">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" '
                f'dur="0.25s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-6 -6" to="0 0" begin="{delay:.3f}s" dur="0.25s" fill="freeze" '
                f'additive="sum"/>'
                f"</rect>"
            )

    # legend
    legend_y = grid_top + grid_h + 18
    svg_parts.append(
        f'<text x="{LEFT_PAD}" y="{legend_y}" fill="#7d8590" font-size="10">Less</text>'
    )
    lx = LEFT_PAD + 32
    for i, color in enumerate(PALETTE):
        svg_parts.append(
            f'<rect x="{lx + i * (CELL + GAP)}" y="{legend_y - 9}" width="{CELL}" '
            f'height="{CELL}" rx="2" ry="2" fill="{color}"/>'
        )
    svg_parts.append(
        f'<text x="{lx + len(PALETTE) * (CELL + GAP) + 4}" y="{legend_y}" '
        f'fill="#7d8590" font-size="10">More</text>'
    )

    # stats footer
    footer_y = legend_y + 20
    footer = (
        f"{stats['total_contributions']} contributions in the last year "
        f"\u00b7 current streak {stats['current_streak']} \u00b7 "
        f"longest streak {stats['longest_streak']}"
    )
    svg_parts.append(
        f'<text x="{LEFT_PAD}" y="{footer_y}" fill="#c9d1d9" font-size="11">{footer}</text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main():
    payload = load()
    svg = render(payload)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
