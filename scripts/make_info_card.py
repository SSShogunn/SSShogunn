#!/usr/bin/env python3
"""
Hand-author a simple neofetch-style info card SVG: shared terminal chrome,
short "label: value" rows that fade + slide in on a short stagger, and a
classic neofetch color-swatch row at the bottom (the genuinely "neofetch"
touch -- not about the person, just the terminal palette every neofetch
screenshot ends with).

Sized to 35% of the shared width -- it sits next to toplangs.svg in one row.

STATIC=1 env var emits a frozen (fully revealed) frame for local previews.
Output: info-card.svg (repo root).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _svg_common import INFO_CARD_WIDTH as WIDTH, TITLEBAR_H, ROW_CARD_HEIGHT, frame_open, svg_open, esc

STATIC = os.environ.get("STATIC") == "1"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

TITLE = "neofetch"

ROWS = [
    ("Role", "Backend Engineer"),
    ("Stack", "FastAPI, Bedrock, Java"),
    ("Building", "WebRTC, homelab"),
    ("Exploring", "Go, ESP32"),
]

# classic neofetch palette swatch -- just the terminal's 8 ANSI colors,
# nothing personal, the bit every neofetch screenshot has at the bottom.
SWATCH_COLORS = [
    "#0d1117", "#ff5f56", "#39d353", "#ffbd2e",
    "#58a6ff", "#bc8cff", "#56d4dd", "#c9d1d9",
]

LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"

ROW_H = 24
PAD_X = 18
TOP_PAD = 18
SWATCH_SIZE = 16
HEIGHT = ROW_CARD_HEIGHT


def build_svg():
    parts = [svg_open(WIDTH, HEIGHT)]
    parts.extend(frame_open(WIDTH, HEIGHT, TITLE, border=False))

    step = 0.3
    y = TITLEBAR_H + TOP_PAD + 10
    for i, (label, value) in enumerate(ROWS):
        delay = i * step
        if STATIC:
            row_open = "<g>"
        else:
            row_open = (
                '<g opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.35s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-10 0" to="0 0" begin="{delay:.2f}s" dur="0.35s" fill="freeze" '
                f'additive="sum"/>'
            )
        parts.append(row_open)
        parts.append(
            f'<text x="{PAD_X}" y="{y}" font-size="11.5" xml:space="preserve">'
            f'<tspan fill="{LABEL_COLOR}" font-weight="bold">{esc(label)}: </tspan>'
            f'<tspan fill="{VALUE_COLOR}">{esc(value)}</tspan>'
            f'</text>'
        )
        parts.append("</g>")
        y += ROW_H

    # neofetch-style color swatch row, revealed after the text rows
    swatch_delay = len(ROWS) * step + 0.1
    swatch_y = y + 4
    sx = PAD_X
    for i, color in enumerate(SWATCH_COLORS):
        delay = swatch_delay + i * 0.04
        opacity_attr = "" if STATIC else ' opacity="0"'
        parts.append(
            f'<rect x="{sx}" y="{swatch_y}" width="{SWATCH_SIZE}" height="{SWATCH_SIZE}" '
            f'fill="{color}" stroke="#30363d" stroke-width="0.5"{opacity_attr}>'
        )
        if not STATIC:
            parts.append(
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.2s" fill="freeze"/>'
            )
        parts.append("</rect>")
        sx += SWATCH_SIZE

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
