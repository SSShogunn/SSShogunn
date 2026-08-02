#!/usr/bin/env python3
"""
Hand-author a neofetch-style info card SVG: shared terminal chrome, then
colored key/value rows that fade + slide in on a short stagger, with a
fixed-width label column (sized to the longest label) and thin divider
lines between rows for cleaner alignment.

STATIC=1 env var emits a frozen (fully revealed) frame for local previews.
Output: info-card.svg (repo root).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _svg_common import WIDTH, TITLEBAR_H, BORDER, frame_open, svg_open, esc

STATIC = os.environ.get("STATIC") == "1"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

TITLE = "aman@sshogunn ~ $ neofetch"

ROWS = [
    ("Role", "Backend Engineer -- AI-powered systems & infra"),
    ("Stack", "FastAPI - AWS Bedrock - LangChain - Snowflake - Java"),
    ("Building", "WebRTC file transfer - self-hosted homelab - agent sandboxes"),
    ("Exploring", "Go - ESP32 tinkering - Vedic astrology"),
    ("Grinding", "DSA (Striver A2Z) - graphs & DP next"),
]

LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
DIVIDER_COLOR = "#21262d"

ROW_H = 34
PAD_X = 24
TOP_PAD = 20
CHAR_W = 7.2  # approx bold-monospace advance at font-size 12.5
LABEL_W = max(len(label) for label, _ in ROWS) * CHAR_W + 28  # fits longest label + gap
HEIGHT = TITLEBAR_H + TOP_PAD + len(ROWS) * ROW_H + 12


def build_svg():
    parts = [svg_open(WIDTH, HEIGHT)]
    parts.extend(frame_open(WIDTH, HEIGHT, TITLE))

    step = 0.35
    y = TITLEBAR_H + TOP_PAD + 14
    for i, (label, value) in enumerate(ROWS):
        delay = i * step
        if STATIC:
            row_open = "<g>"
        else:
            row_open = (
                '<g opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.4s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-14 0" to="0 0" begin="{delay:.2f}s" dur="0.4s" fill="freeze" '
                f'additive="sum"/>'
            )
        parts.append(row_open)
        parts.append(
            f'<text x="{PAD_X}" y="{y}" fill="{LABEL_COLOR}" font-size="12.5" '
            f'font-weight="bold">{esc(label)}</text>'
        )
        parts.append(
            f'<text x="{PAD_X + LABEL_W:.1f}" y="{y}" fill="{VALUE_COLOR}" font-size="12.5">'
            f'{esc(value)}</text>'
        )
        parts.append("</g>")
        if i < len(ROWS) - 1:
            line_y = y + (ROW_H - 12) / 2 + 12
            parts.append(
                f'<line x1="{PAD_X}" y1="{line_y:.1f}" x2="{WIDTH - PAD_X}" y2="{line_y:.1f}" '
                f'stroke="{DIVIDER_COLOR}" stroke-width="1"/>'
            )
        y += ROW_H

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
