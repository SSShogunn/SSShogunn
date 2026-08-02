#!/usr/bin/env python3
"""
Hand-author a neofetch-style info card SVG: a title bar, then colored
key/value rows (Now, Prev, Stack, Highlights) that fade + slide in on a
short stagger, like the panel is printing next to the portrait.

STATIC=1 env var emits a frozen (fully revealed) frame for local previews.
Output: info-card.svg (repo root).
"""
import os

STATIC = os.environ.get("STATIC") == "1"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

# ---- content -----------------------------------------------------------
USER = "aman@sshogunn"
TITLE = f"{USER} ~ $ neofetch"

ROWS = [
    ("Role", "Backend Engineer -- AI-powered systems & infra"),
    ("Stack", "FastAPI - AWS Bedrock - LangChain - Snowflake - Java"),
    ("Building", "WebRTC file transfer - self-hosted homelab - agent sandboxes"),
    ("Exploring", "Go - ESP32 tinkering - Vedic astrology"),
    ("Grinding", "DSA (Striver A2Z) - graphs & DP next"),
]

LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
BG = "#0d1117"
BAR_BG = "#161b22"
BORDER = "#30363d"
TITLE_COLOR = "#7d8590"

# ---- layout --------------------------------------------------------------
WIDTH = 490
TITLEBAR_H = 30
ROW_H = 26
PAD_X = 18
TOP_PAD = 16
LABEL_W = 96
HEIGHT = TITLEBAR_H + TOP_PAD + len(ROWS) * ROW_H + 16


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg():
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
    )
    parts.append(
        f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="10" ry="10" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1"/>'
    )
    # title bar with fake traffic-light dots
    parts.append(f'<rect x="0" y="0" width="{WIDTH}" height="{TITLEBAR_H}" rx="10" ry="10" fill="{BAR_BG}"/>')
    parts.append(f'<rect x="0" y="{TITLEBAR_H - 10}" width="{WIDTH}" height="10" fill="{BAR_BG}"/>')
    for i, dot_color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{20 + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dot_color}"/>')
    parts.append(
        f'<text x="{WIDTH / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" '
        f'fill="{TITLE_COLOR}" font-size="11">{esc(TITLE)}</text>'
    )

    step = 0.35  # seconds between each row's stagger
    y = TITLEBAR_H + TOP_PAD + 12
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
            f'<text x="{PAD_X}" y="{y}" fill="{LABEL_COLOR}" font-size="12" '
            f'font-weight="bold">{esc(label)}</text>'
        )
        parts.append(
            f'<text x="{PAD_X + LABEL_W}" y="{y}" fill="{VALUE_COLOR}" font-size="12">'
            f'{esc(value)}</text>'
        )
        parts.append("</g>")
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
