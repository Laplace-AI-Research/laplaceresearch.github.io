"""Usage: python3 tools/oracle/generate_cta.py  (writes assets/covers/oracle-cta.svg)

Closing-card art for /oracle/, in the halftone style of the other *-cta.svg covers:
one sensor wired to two displays (Fig. 1 of the article). Decorative; shows no results.
"""
import math, pathlib, random

OUT = pathlib.Path(__file__).resolve().parents[2] / "assets/covers/oracle-cta.svg"
W, H = 960, 720
BG, HI, LO, LINE = "#011a47", "#8cb7ff", "#02338a", "#8cb7ff"
SENSOR, DA, DB = (430, 250), (770, 130), (770, 370)


def bez(p0, p3, t):
    mx = (p0[0] + p3[0]) / 2
    p1, p2 = (mx, p0[1]), (mx, p3[1])
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])


wires = [[bez((SENSOR[0] + 70, SENSOR[1]), (DA[0] - 80, DA[1]), i / 60) for i in range(61)],
         [bez((SENSOR[0] + 70, SENSOR[1]), (DB[0] - 80, DB[1]), i / 60) for i in range(61)]]
pts = [p for w in wires for p in w]


def near(x, y):
    return min(math.hypot(x - px, y - py) for px, py in pts)


rnd = random.Random(7)
dots = []
step = 15
row = 0
y = step / 2
while y < H + step:
    x = step / 2 + (step / 2 if row % 2 else 0)
    while x < W + step:
        d = near(x, y)
        glow = math.exp(-d / 90)
        field = 0.55 + 0.45 * math.exp(-math.hypot(x - 640, y - 260) / 420)
        r = 0.6 + 2.9 * glow * field
        if r > 0.8:
            col, op = (HI, 0.86) if glow > 0.35 and rnd.random() < 0.55 else (LO, 0.72)
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" fill-opacity="{op}"/>')
        x += step
    y += step * 0.866
    row += 1


def node(cx, cy, label, dashed):
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    return (f'<rect x="{cx - 70}" y="{cy - 30}" width="140" height="60" fill="{BG}" stroke="{LINE}" stroke-width="2"{dash}/>'
            f'<text x="{cx}" y="{cy + 6}" fill="#ffffff" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" '
            f'font-size="15" letter-spacing="2" text-anchor="middle">{label}</text>')


path = lambda w: "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in w)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="{BG}"/><g>{"".join(dots)}</g>'
       + "".join(f'<path d="{path(w)}" fill="none" stroke="{LINE}" stroke-width="2.2"/>' for w in wires)
       + node(*SENSOR, "SENSOR", False) + node(*DA, "DISPLAY A", True) + node(*DB, "DISPLAY B", True)
       + "</svg>")
OUT.write_text(svg)
print(OUT.name, f"{len(svg) / 1024:.0f} KB")
