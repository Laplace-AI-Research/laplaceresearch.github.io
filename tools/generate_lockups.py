"""Usage: python3 tools/generate_lockups.py  (needs fonttools, brotli, uharfbuzz)

Writes the horizontal "Δ Laplace Research" lockups to assets/brand/ as SVGs with
outlined type, matching the site header: Newsreader wght 350 / opsz 24,
letter-spacing -0.03em, a 0.9em × 0.74em mark, 9/21 em gap, nudged up 0.08em.
"""
import io, pathlib
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "brand"
TEXT = "Laplace Research"
MARK = [(1000, 432), (1699, 1567.5), (1044.4, 1375.5), (1267.8, 1170.9), (301, 1567.5)]
NAVY, INK, WHITE, BLACK = "#02338A", "#23262D", "#FFFFFF", "#000000"
VARIANTS = {"color": (NAVY, INK), "navy": (NAVY, NAVY), "white": (WHITE, WHITE), "black": (BLACK, BLACK)}

font = TTFont(ROOT / "assets" / "fonts" / "newsreader-latin-opsz-normal.woff2")
font = instantiateVariableFont(font, {"wght": 350, "opsz": 24})
font.flavor = None
buf = io.BytesIO(); font.save(buf); data = buf.getvalue()
upm = font["head"].unitsPerEm
EM = 1000.0
k = EM / upm

hbf = hb.Font(hb.Face(data))
b = hb.Buffer(); b.add_str(TEXT); b.guess_segment_properties()
hb.shape(hbf, b, {"kern": True, "liga": True})
gs = font.getGlyphSet()
order = font.getGlyphOrder()

asc, desc = font["hhea"].ascent * k, -font["hhea"].descent * k
baseline = (EM - (asc + desc)) / 2 + asc            # line-height: 1 box
gap = EM * 9 / 21
mw, mh = 0.9 * EM, 0.74 * EM
xs = [p[0] for p in MARK]; ys = [p[1] for p in MARK]
s = min(mw / (max(xs) - min(xs)), mh / (max(ys) - min(ys)))
dx = (mw - (max(xs) - min(xs)) * s) / 2 - min(xs) * s
dy = (EM - mh) / 2 - 0.08 * EM + (mh - (max(ys) - min(ys)) * s) / 2 - min(ys) * s
mark = " ".join(f"{x*s+dx:.1f},{y*s+dy:.1f}" for x, y in MARK)

pen = SVGPathPen(gs)
x = mw + gap
for info, pos in zip(b.glyph_infos, b.glyph_positions):
    name = order[info.codepoint]
    gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x + pos.x_offset * k, baseline - pos.y_offset * k)))
    x += pos.x_advance * k - 0.03 * EM
width = x + 0.03 * EM
path = pen.getCommands()

pad = 0
for name, (mc, tc) in VARIANTS.items():
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {EM:.0f}" role="img" aria-label="Laplace Research">'
           f'<polygon points="{mark}" fill="{mc}"/><path d="{path}" fill="{tc}"/></svg>\n')
    (OUT / f"laplace-lockup-{name}.svg").write_text(svg)
print(f"lockups {width:.0f}×{EM:.0f}")
