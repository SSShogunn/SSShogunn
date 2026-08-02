"""
Shared terminal window-chrome for all profile SVGs -- same title bar,
traffic-light dots, border, and corner radius everywhere so the four
blocks read as one consistent dashboard instead of four different styles.
"""

BG = "#0d1117"
BAR_BG = "#161b22"
BORDER = "#30363d"
TITLE_COLOR = "#7d8590"
TITLEBAR_H = 30
RADIUS = 10

WIDTH = 792  # common width for every block in the README


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame_open(width, height, title):
    """Card background + border + title bar with traffic-light dots."""
    parts = [
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="{RADIUS}" ry="{RADIUS}" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1"/>',
        f'<rect x="0" y="0" width="{width}" height="{TITLEBAR_H}" rx="{RADIUS}" ry="{RADIUS}" fill="{BAR_BG}"/>',
        f'<rect x="0" y="{TITLEBAR_H - RADIUS}" width="{width}" height="{RADIUS}" fill="{BAR_BG}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{width}" y2="{TITLEBAR_H}" stroke="{BORDER}" stroke-width="1"/>',
    ]
    for i, dot_color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{20 + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dot_color}"/>')
    parts.append(
        f'<text x="{width / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" '
        f'fill="{TITLE_COLOR}" font-size="11">{esc(title)}</text>'
    )
    return parts


def svg_open(width, height):
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
    )
