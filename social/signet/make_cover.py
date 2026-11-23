"""Signet cover for the site (960x600 SVG), in the style of assets/covers/*.svg: cream ground, faint grid, ink marks,
grain. Three seals pressed into the grid (rings = parameters in billions), one wax mark.

    python3 social/signet/make_cover.py   # -> assets/signet/../covers/signet.svg
"""
import math
from pathlib import Path

W, H = 960, 600
INK, PAPER, WAX = "#16171a", "#ece5d6", "#b3261e"
SEALS = [(250, 390, 2, 62, 0.62), (500, 230, 4, 92, 0.66), (740, 380, 9, 135, 0.7)]  # x, y, rings, Rmax, pinch k


def pinch(x, y):
    for sx, sy, _, R, k in SEALS:
        dx, dy = x - sx, y - sy
        r = math.hypot(dx, dy)
        f = 1 - k * math.exp(-r / (R * 1.45))
        x, y = sx + dx * f, sy + dy * f
    return x, y


def ring_radii(n, rmax, rin):
    L = math.log(1 / (n + 1))
    return [rin + (rmax - rin) * math.log(k / (n + 1)) / L for k in range(1, n + 1)]


def main():
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           '<defs><filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
           'baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  '
           '0 0 0 0 1  0 0 0 0.55 0"/></filter></defs>',
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    gap = 40
    paths = []
    for y in range(0, H + 1, gap):
        pts = [pinch(x, y) for x in range(-gap, W + gap + 1, 4)]
        paths.append("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts))
    for x in range(0, W + 1, gap):
        pts = [pinch(x, y) for y in range(-gap, H + gap + 1, 4)]
        paths.append("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts))
    out.append(f'<path d="{" ".join(paths)}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.16"/>')
    for x in range(0, W + 1, gap):
        for y in range(0, H + 1, gap):
            px, py = pinch(x, y)
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.6" fill="{INK}" opacity="0.5"/>')
    for sx, sy, n, R, _ in SEALS:
        for r in ring_radii(n, R, max(6, R * 0.1)):
            out.append(f'<circle cx="{sx}" cy="{sy}" r="{r:.1f}" fill="none" stroke="{INK}" stroke-width="{1.6 if n > 6 else 2.2}"/>')
        out.append(f'<circle cx="{sx}" cy="{sy}" r="{6 if n == 9 else 3.5}" fill="{WAX if n == 9 else INK}"/>')
    out.append(f'<rect x="40" y="34" width="250" height="58" fill="{PAPER}"/>')
    out.append(f'<text x="48" y="58" font-family="Geist Mono, ui-monospace, monospace" font-size="15" font-weight="600" fill="{INK}" letter-spacing="1">SIGNET</text>')
    out.append(f'<text x="48" y="80" font-family="Geist Mono, ui-monospace, monospace" font-size="12" fill="{INK}" opacity="0.7" letter-spacing="0.6">RINGS = PARAMETERS (2 · 4 · 9B)</text>')
    out.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.18"/>')
    out.append("</svg>")
    p = Path(__file__).resolve().parents[2] / "assets/covers/signet.svg"
    p.write_text("".join(out))
    print("wrote", p, f"{p.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
