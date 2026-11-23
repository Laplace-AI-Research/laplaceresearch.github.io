"""Usage: python3 tools/generate_dither.py  (writes assets/dither.svg)

The rail signature: a Laplace density, ordered-dithered onto a 4px grid.
Peak sits left of centre and the tail runs out to the right edge, so the
strip reads as a distribution rather than a gradient.
"""
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "dither.svg"
CELL, COLS, ROWS = 4, 62, 16
W, H = COLS * CELL, ROWS * CELL
INK = "#3347d6"
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def intensity(cx, cy):
    u = (cx + 0.5) / COLS
    yb = (ROWS - cy - 0.5) / ROWS          # 0 at the floor, 1 at the top
    h = 0.06 + 0.94 * math.exp(-abs(u - 0.28) / 0.13)
    edge = (h - yb) / 0.42 + 0.5           # soft shoulder above the curve
    return max(0.0, min(1.0, edge)) * (1 - 0.35 * u)


rects = []
for cy in range(ROWS):
    for cx in range(COLS):
        t = (BAYER[cy % 4][cx % 4] + 0.5) / 16
        if intensity(cx, cy) > t:
            rects.append(f'<rect x="{cx*CELL}" y="{cy*CELL}" width="{CELL-1}" height="{CELL-1}"/>')

OUT.write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'shape-rendering="crispEdges"><g fill="{INK}">' + "".join(rects) + "</g></svg>\n"
)
print(f"wrote {OUT} ({len(rects)} cells)")
