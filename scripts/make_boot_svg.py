#!/usr/bin/env python3
"""
Self-hosted terminal "boot sequence" banner -- replaces the third-party
readme-typing-svg.herokuapp.com dependency with something we own and that
matches the rest of the terminal aesthetic. Each line wipes in left-to-right,
staggered top to bottom, then a cursor block blinks forever at the end.

STATIC=1 emits a frozen (fully revealed, no blink) frame for local previews.
Output: boot-banner.svg (repo root).
"""
import os

STATIC = os.environ.get("STATIC") == "1"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "boot-banner.svg")

# (text, color) -- keep this free of employer/location details on purpose.
LINES = [
    ("$ whoami", "#7d8590"),
    ("aman singh -- backend engineer", "#c9d1d9"),
    ("$ echo $INTERESTS", "#7d8590"),
    ("AI systems, self-hosting, retro terminals", "#c9d1d9"),
    ("$ ./status.sh", "#7d8590"),
    ("online.", "#39d353"),
]

WIDTH = 560
LINE_H = 26
PAD_X = 18
PAD_TOP = 24
CHAR_W = 8.4  # approx monospace advance at font-size 13
HEIGHT = PAD_TOP + len(LINES) * LINE_H + 20


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg():
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="10" ry="10" '
        f'fill="#0d1117" stroke="#30363d" stroke-width="1"/>',
    ]

    step = 0.55
    y = PAD_TOP
    last_line_end = 0.0
    for i, (text, color) in enumerate(LINES):
        delay = i * step
        text_w = len(text) * CHAR_W
        clip_id = f"clip{i}"
        parts.append(f'<clipPath id="{clip_id}">')
        if STATIC:
            parts.append(f'<rect x="{PAD_X}" y="{y - 14}" width="{text_w}" height="20"/>')
        else:
            parts.append(
                f'<rect x="{PAD_X}" y="{y - 14}" width="0" height="20">'
                f'<animate attributeName="width" from="0" to="{text_w:.1f}" '
                f'begin="{delay:.2f}s" dur="0.5s" fill="freeze"/>'
                f"</rect>"
            )
        parts.append("</clipPath>")
        parts.append(
            f'<text x="{PAD_X}" y="{y}" fill="{color}" font-size="13" '
            f'clip-path="url(#{clip_id})">{esc(text)}</text>'
        )
        last_line_end = delay + 0.5
        y += LINE_H

    # blinking cursor after the last line finishes typing
    cursor_x = PAD_X + len(LINES[-1][0]) * CHAR_W + 4
    cursor_y = PAD_TOP + (len(LINES) - 1) * LINE_H
    if STATIC:
        parts.append(
            f'<rect x="{cursor_x:.1f}" y="{cursor_y - 12}" width="7" height="14" fill="#39d353"/>'
        )
    else:
        parts.append(
            f'<rect x="{cursor_x:.1f}" y="{cursor_y - 12}" width="7" height="14" '
            f'fill="#39d353" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{last_line_end:.2f}s" '
            f'dur="0.01s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;0;1" dur="1s" '
            f'begin="{last_line_end:.2f}s" repeatCount="indefinite"/>'
            f"</rect>"
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    with open(OUT_PATH, "w") as f:
        f.write(build_svg())
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
