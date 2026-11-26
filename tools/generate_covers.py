"""Usage: python3 tools/generate_covers.py  (writes assets/covers/*.svg)

Halftone cover art for the homepage writing gallery.

Each cover is a standalone 960x600 SVG (16:10) with fixed colours, so it reads
like a printed image in both themes. Shapes come from the research itself:
Laplace densities, confidence intervals, model scale, the release checklist.
"""
import math, random, pathlib, sys

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "assets" / "covers")
OUT.mkdir(parents=True, exist_ok=True)
W, H = 960, 600
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"


def f(x):
    return f"{x:.1f}"


def head(bg, extra_defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        "<defs>"
        '<filter id="grain" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>'
        '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.55 0"/>'
        "</filter>"
        f"{extra_defs}</defs>"
        f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    )


def tail(grain=0.09):
    return f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{grain}"/></svg>'


def label(x, y, text, fill, size=17, anchor="start", spacing=1.6):
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{MONO}" font-size="{size}" '
        f'letter-spacing="{spacing}" text-anchor="{anchor}">{text}</text>'
    )


def laplace(u, mu, b):
    return math.exp(-abs(u - mu) / b)


def halftone(step, radius_fn, fill, jitter=0.0, offset=(0, 0), seed=1):
    """Dot grid; radius_fn(x, y) -> radius (0 skips)."""
    r = random.Random(seed)
    out = []
    y = step / 2 + offset[1]
    row = 0
    while y < H + step:
        x = step / 2 + offset[0] + (step / 2 if row % 2 else 0)
        while x < W + step:
            rad = radius_fn(x, y)
            if rad > 0.35:
                jx = (r.random() - 0.5) * jitter
                jy = (r.random() - 0.5) * jitter
                out.append(f'<circle cx="{f(x + jx)}" cy="{f(y + jy)}" r="{rad:.2f}"/>')
            x += step
        y += step * 0.866
        row += 1
    return f'<g fill="{fill}">' + "".join(out) + "</g>"


# ---------------------------------------------------------------- 1
def cover_convictionbench():
    bg, ink, hot = "#2c3bd1", "#ffffff", "#ff6a3d"
    s = [head(bg)]
    # halftone wash: dots swell toward the lower right
    s.append(halftone(15, lambda x, y: 6.2 * max(0, (x / W) * 0.55 + (y / H) * 0.65 - 0.3) ** 1.1, "#4a59e3", seed=3))
    truth = W * 0.64
    s.append(f'<rect x="{f(truth - 1.5)}" y="0" width="3" height="{H}" fill="{ink}"/>')
    rnd = random.Random(11)
    rows = 13
    for i in range(rows):
        t = i / (rows - 1)
        y = 70 + i * (H - 140) / (rows - 1)
        if i in (4, 8):
            c = truth - W * (0.26 + rnd.random() * 0.1)
            half = W * 0.05
            col, op = hot, 1
        else:
            c = truth + (1 - t) ** 1.3 * (rnd.random() - 0.5) * W * 0.62
            half = W * (0.24 * (1 - t) ** 1.15 + 0.016)
            col, op = ink, 0.75
        half = min(half, c - 24, W - 24 - c)
        s.append(f'<line x1="{f(c - half)}" y1="{f(y)}" x2="{f(c + half)}" y2="{f(y)}" stroke="{col}" stroke-width="3" stroke-linecap="round" opacity="{op}"/>')
        s.append(f'<circle cx="{f(c)}" cy="{f(y)}" r="8" fill="{col}" stroke="{bg}" stroke-width="4"/>')
    s.append(label(44, 64, "CONVICTIONBENCH", ink, 18))
    s.append(label(44, 90, "V0.1 · 26,478 EPISODES", "#c9cdfa", 15))
    s.append(tail(0.1))
    return "".join(s)


# ---------------------------------------------------------------- 2
def cover_series():
    bg = "#0f1013"
    s = [head(bg)]
    base = H * 0.82
    series = [  # colour, mu, b, peak height
        ("#3d8bff", 0.34, 0.075, 0.5),
        ("#24c08a", 0.5, 0.12, 0.36),
        ("#ff7140", 0.66, 0.035, 0.66),
    ]
    for k, (col, mu, b, amp) in enumerate(series):
        def rad(x, y, mu=mu, b=b, amp=amp):
            top = base - H * amp * laplace(x / W, mu, b)
            if y < top or y > base:
                return 0
            depth = (y - top) / max(1, base - top)
            return 1.2 + 3.6 * (1 - depth) ** 0.6
        s.append(halftone(11, rad, col, offset=(k * 3.7, k * 3.1), seed=k + 7))
    for col, mu, b, amp in series:
        pts = []
        for i in range(0, 401):
            u = i / 400
            pts.append(f"{f(u * W)},{f(base - H * amp * laplace(u, mu, b))}")
        pts.insert(round(mu * 400) + 1, f"{f(mu * W)},{f(base - H * amp)}")
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="3" stroke-linejoin="round"/>')
    s.append(f'<rect x="0" y="{f(base)}" width="{W}" height="2" fill="#ffffff" opacity="0.25"/>')
    for i, (name, col) in enumerate((("ANCHOR", "#3d8bff"), ("MERIDIAN", "#24c08a"), ("VECTOR", "#ff7140"))):
        x = 44 + i * 190
        s.append(f'<circle cx="{x + 6}" cy="{H - 44}" r="6" fill="{col}"/>')
        s.append(label(x + 22, H - 38, name, "#e9e7e1", 16))
    s.append(label(44, 64, "LAPLACE CONVICTION SERIES", "#e9e7e1", 18))
    s.append(tail(0.08))
    return "".join(s)


# ---------------------------------------------------------------- 3
def cover_tarot():
    bg, ink, hot = "#ece5d6", "#16171a", "#e2552a"
    s = [head(bg)]
    for k in range(1, 10):
        x = W * k / 10
        s.append(f'<rect x="{f(x)}" y="0" width="1" height="{H}" fill="{ink}" opacity="0.08"/>')
    for k in range(1, 6):
        y = H * k / 6
        s.append(f'<rect x="0" y="{f(y)}" width="{W}" height="1" fill="{ink}" opacity="0.08"/>')
    x0, y0, x1, y1 = 120, H - 70, W - 120, 70
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{ink}" stroke-width="2.5"/>')
    discs = [("1.7B", 0.24, 1.7), ("4B", 0.52, 4), ("8B", 0.8, 8)]
    for name, t, params in discs:
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        R = 34 * math.sqrt(params)
        lx, ly = cx - R * 0.35, cy - R * 0.35  # light from the upper left

        def rad(x, y, cx=cx, cy=cy, R=R, lx=lx, ly=ly):
            if (x - cx) ** 2 + (y - cy) ** 2 > R * R:
                return 0
            d = math.hypot(x - lx, y - ly) / (R * 1.35)
            return 0.9 + 4.3 * min(1, d) ** 0.9
        s.append(halftone(10, rad, hot, seed=int(params * 10)))
        s.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R)}" fill="none" stroke="{ink}" stroke-width="2"/>')
        s.append(label(f(cx + R + 14), f(cy + 6), name, ink, 17, spacing=1))
    s.append(label(44, 64, "TAROT-DRAW", ink, 18))
    s.append(label(44, 90, "WHAT SCALE CHANGES", "#6d6a63", 15))
    s.append(tail(0.12))
    return "".join(s)


# ---------------------------------------------------------------- 4
# The Laplace Δ mark (tools/generate_brand.py), centred on the origin with half-width 1.
DELTA = [((x - 1000) / 700, (y - 1000) / 700) for x, y in
         [(1000, 432), (1699, 1567.5), (1044.4, 1375.5), (1267.8, 1170.9), (301, 1567.5)]]


def delta_contains(x, y, cx, cy, R):
    """Point-in-polygon test for the Laplace Δ mark scaled to half-width R."""
    u, v = (x - cx) / R, (y - cy) / R
    inside = False
    for (x0, y0), (x1, y1) in zip(DELTA, DELTA[1:] + DELTA[:1]):
        if (y0 > v) != (y1 > v) and u < x0 + (v - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def cover_standard():
    bg, pale, ink = "#173d31", "#d7efe2", "#ffffff"
    s = [head(bg)]
    cx, cy, R = W * 0.72, H * 0.5, 230

    def rad(x, y):
        if not delta_contains(x, y, cx, cy, R):
            return 0
        lx, ly = cx - R * 0.35, cy - R * 0.4  # soft light from the upper left
        d = min(1, math.hypot(x - lx, y - ly) / (R * 1.25))
        return 1.0 + 3.8 * d ** 0.8
    s.append(halftone(12, rad, pale, seed=21))
    items = ["ARTIFACTS", "EVALUATION INPUTS", "METRIC CODE", "LIMITATIONS", "REPRODUCTION"]
    for i, t in enumerate(items):
        y = 168 + i * 72
        s.append(f'<rect x="44" y="{y - 26}" width="36" height="36" rx="5" fill="{pale}"/>')
        s.append(f'<path d="M53,{y - 8} l8,8 l13,-15" fill="none" stroke="{bg}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        s.append(label(100, y, t, ink, 19, spacing=2))
    s.append(label(44, 64, "RELEASE STANDARD", ink, 18))
    s.append(label(44, 90, "CLAIMS TRAVEL WITH EVIDENCE", "#9cc7b2", 15))
    s.append(tail(0.1))
    return "".join(s)


for name, fn in {
    "convictionbench": cover_convictionbench,
    "conviction-series": cover_series,
    "tarot-draw": cover_tarot,
    "release-standard": cover_standard,
}.items():
    svg = fn()
    (OUT / f"{name}.svg").write_text(svg)
    print(name, f"{len(svg) / 1024:.0f} KB")
