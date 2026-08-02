#!/usr/bin/env python3
"""
Self-computed "top languages" bar -- no third-party stats card, no token
required for local runs (CI can optionally set GH_API_TOKEN for a higher
rate limit). Pulls each owned, non-fork repo's language breakdown from the
public API and renders a single stacked horizontal bar + legend.
Output: toplangs.svg (repo root).
"""
import json
import os
import sys
from collections import defaultdict

import requests

USERNAME = os.environ.get("GITHUB_PROFILE_USERNAME", "SSShogunn")
TOKEN = os.environ.get("GH_API_TOKEN")  # optional, raises API rate limit
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "toplangs.svg")

HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "profile-toplangs-script"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

# A small, readable palette -- extend if a new language shows up top-N.
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

    width = 560
    bar_h = 14
    pad_x = 18
    pad_top = 24
    row_h = 20
    n_legend_rows = -(-len(top) // 2)  # ceil div, 2 per row
    height = pad_top + bar_h + 16 + n_legend_rows * row_h + 12

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="10" ry="10" '
        f'fill="#0d1117" stroke="#30363d" stroke-width="1"/>',
        f'<text x="{pad_x}" y="18" fill="#7d8590" font-size="11">top languages</text>',
    ]

    # stacked bar
    bar_w = width - 2 * pad_x
    x = pad_x
    y = pad_top
    for lang, n in top:
        w = (n / total_bytes) * bar_w
        color = LANG_COLORS.get(lang, FALLBACK_COLOR)
        parts.append(
            f'<rect x="{x:.1f}" y="{y}" width="0" height="{bar_h}" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{w:.1f}" begin="0s" '
            f'dur="0.6s" fill="freeze"/>'
            f"</rect>"
        )
        x += w
    # rounded mask overlay to keep corners clean
    parts.append(
        f'<rect x="{pad_x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" ry="4" '
        f'fill="none" stroke="#0d1117" stroke-width="0"/>'
    )

    # legend, two columns
    legend_y = y + bar_h + 22
    col_w = bar_w / 2
    for i, (lang, n) in enumerate(top):
        pct = 100 * n / total_bytes
        col = i % 2
        row = i // 2
        lx = pad_x + col * col_w
        ly = legend_y + row * row_h
        color = LANG_COLORS.get(lang, FALLBACK_COLOR)
        parts.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{color}"/>')
        parts.append(
            f'<text x="{lx + 16}" y="{ly}" fill="#c9d1d9" font-size="11">'
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
