#!/usr/bin/env python3
"""
Self-computed "top languages" bar -- shared chrome, same width as every
other block. No third-party stats card, no token required for local runs
(CI can optionally set GH_API_TOKEN for a higher rate limit). Pulls each
owned, non-fork repo's language breakdown from the public API and renders
a single stacked horizontal bar + legend.
Output: toplangs.svg (repo root).
"""
import json
import os
import sys
from collections import defaultdict

import requests

sys.path.insert(0, os.path.dirname(__file__))
from _svg_common import TOPLANGS_WIDTH as WIDTH, TITLEBAR_H, ROW_CARD_HEIGHT, frame_open, svg_open

USERNAME = os.environ.get("GITHUB_PROFILE_USERNAME", "SSShogunn")
TOKEN = os.environ.get("GH_API_TOKEN")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "toplangs.svg")
TITLE = "aman@github ~ $ toplangs"

HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "profile-toplangs-script"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Dart": "#00B4AB",
    "Go": "#00ADD8",
    "C++": "#f34b7d",
    "C": "#555555",
    "Shell": "#89e051",
    "Dockerfile": "#384d54",
}
FALLBACK_COLOR = "#8b949e"


def get_json(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def collect_language_bytes():
    totals = defaultdict(int)
    page = 1
    while True:
        repos = get_json(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&type=owner"
        )
        if not repos:
            break
        for repo in repos:
            if repo.get("fork"):
                continue
            langs = get_json(repo["languages_url"])
            for lang, n in langs.items():
                totals[lang] += n
        if len(repos) < 100:
            break
        page += 1
    return totals


def render(totals, top_n=6):
    total_bytes = sum(totals.values())
    if total_bytes == 0:
        raise RuntimeError("No language data found -- nothing to render.")

    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    top = ranked[:top_n]
    other = sum(n for _, n in ranked[top_n:])
    if other > 0:
        top.append(("Other", other))

    bar_h = 16
    pad_x = 24
    row_h = 22
    n_legend_rows = -(-len(top) // 2)  # ceil div, 2 per row at this narrower width

    height = ROW_CARD_HEIGHT
    content_h = bar_h + 20 + n_legend_rows * row_h
    available = height - TITLEBAR_H - 14  # inner space below title bar, minus bottom pad
    top_offset = TITLEBAR_H + max(14, (available - content_h) / 2 + 14)
    bar_top = top_offset

    parts = [svg_open(WIDTH, height)]
    parts.extend(frame_open(WIDTH, height, TITLE, border=False))

    bar_w = WIDTH - 2 * pad_x
    x = pad_x
    for lang, n in top:
        w = (n / total_bytes) * bar_w
        color = LANG_COLORS.get(lang, FALLBACK_COLOR)
        parts.append(
            f'<rect x="{x:.1f}" y="{bar_top:.1f}" width="0" height="{bar_h}" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{w:.1f}" begin="0s" '
            f'dur="0.6s" fill="freeze"/>'
            f"</rect>"
        )
        x += w

    legend_y = bar_top + bar_h + 24
    col_w = bar_w / 2
    for i, (lang, n) in enumerate(top):
        pct = 100 * n / total_bytes
        col = i % 2
        row = i // 2
        lx = pad_x + col * col_w
        ly = legend_y + row * row_h
        color = LANG_COLORS.get(lang, FALLBACK_COLOR)
        parts.append(f'<circle cx="{lx + 5:.1f}" cy="{ly - 4}" r="5" fill="{color}"/>')
        parts.append(
            f'<text x="{lx + 16:.1f}" y="{ly}" fill="#c9d1d9" font-size="11">'
            f"{lang} {pct:.1f}%</text>"
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    totals = collect_language_bytes()
    svg = render(totals)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} from {len(totals)} languages")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"make_toplangs_svg.py failed: {e}", file=sys.stderr)
        sys.exit(1)
