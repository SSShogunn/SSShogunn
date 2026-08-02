#!/usr/bin/env python3
"""
Downsample the prepped grayscale photo to a character grid (~100 wide),
map each cell's brightness to a glyph from a density ramp, and render as
a monochrome SVG. Each row wipes in left-to-right (staggered top to
bottom), prints once, then freezes -- no looping.

STATIC=1 emits a frozen (fully revealed) frame for local previews.
Output: ascii-portrait.svg (repo root).
"""
import os

import numpy as np
from PIL import Image

STATIC = os.environ.get("STATIC") == "1"
IN_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "source-prepped.png")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "ascii-portrait.svg")

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = background
COLS = 100
CHAR_ASPECT = 2.1  # monospace glyphs are ~2x taller than wide -> more rows needed
FONT_SIZE = 6.2
CELL_W = FONT_SIZE * 0.6
CELL_H = FONT_SIZE * 1.0
COLOR = "#8b949e"  # single light-gray fill -- monochrome on purpose


def load_grid():
    im = Image.open(IN_PATH).convert("L")
    w, h = im.size
    rows = max(1, round(COLS * (h / w) / CHAR_ASPECT))
    small = im.resize((COLS, rows), Image.LANCZOS)
    arr = np.array(small).astype(np.float32) / 255.0  # 0 = black, 1 = white
    return arr


def to_ascii_rows(arr):
    n = len(RAMP) - 1
    rows = []
    for row in arr:
        # bright (arr close to 1) -> sparse (index 0); dark -> dense (index n)
        idx = np.clip(((1.0 - row) * n).round().astype(int), 0, n)
        rows.append("".join(RAMP[i] for i in idx))
    return rows


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(rows):
    n_rows = len(rows)
    n_cols = len(rows[0]) if rows else 0
    width = n_cols * CELL_W
    height = n_rows * CELL_H

    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="#0d1117"/>',
    ]

    step = 0.045  # seconds between each row starting to wipe in
    for r, text in enumerate(rows):
        if not text.strip():
            continue
        y = (r + 1) * CELL_H - CELL_H * 0.2
        delay = r * step
        clip_id = f"row{r}"
        row_w = width
        parts.append(f'<clipPath id="{clip_id}">')
        if STATIC:
            parts.append(f'<rect x="0" y="{r * CELL_H:.1f}" width="{row_w:.1f}" height="{CELL_H:.1f}"/>')
        else:
            parts.append(
                f'<rect x="0" y="{r * CELL_H:.1f}" width="0" height="{CELL_H:.1f}">'
                f'<animate attributeName="width" from="0" to="{row_w:.1f}" '
                f'begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
                f"</rect>"
            )
        parts.append("</clipPath>")
        parts.append(
            f'<text x="0" y="{y:.1f}" fill="{COLOR}" font-size="{FONT_SIZE}" '
            f'xml:space="preserve" clip-path="url(#{clip_id})">{esc(text)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    arr = load_grid()
    rows = to_ascii_rows(arr)
    svg = build_svg(rows)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({len(rows)} rows x {len(rows[0]) if rows else 0} cols)")


if __name__ == "__main__":
    main()
