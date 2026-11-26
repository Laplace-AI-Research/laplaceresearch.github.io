"""Usage: python3 tools/generate_brand.py

Renders every raster form of the Laplace Δ mark from one polygon:
assets/mark.png (CSS mask + schema logo), logo.png, favicons, and the
circle-safe social avatars in assets/brand/.
"""
import io, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "brand"
# Five-point Δ on a 2000 x 2000 canvas (traced from the brand masters).
MARK = [(1000, 432), (1699, 1567.5), (1044.4, 1375.5), (1267.8, 1170.9), (301, 1567.5)]
NAVY_BG = NAVY_MARK = (2, 51, 138)
WHITE = (255, 255, 255)
SS = 8  # supersampling


def scaled(k, cx=1000, cy=1000):
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in MARK]


def coverage(size, pts, box=(0, 0, 2000, 2000)):
    x0, y0, x1, y1 = box
    sx, sy = size[0] * SS / (x1 - x0), size[1] * SS / (y1 - y0)
    m = Image.new("L", (size[0] * SS, size[1] * SS), 0)
    ImageDraw.Draw(m).polygon([((x - x0) * sx, (y - y0) * sy) for x, y in pts], fill=255)
    return m.resize(size, Image.LANCZOS)


def mark_only(size, colour, box):
    im = Image.new("RGBA", size, colour + (0,))
    im.putalpha(coverage(size, MARK, box))
    return im


def tile(px, k=1.0, bg=NAVY_BG, fg=WHITE):
    im = Image.new("RGB", (px, px), bg)
    im.paste(Image.new("RGB", (px, px), fg), (0, 0), coverage((px, px), scaled(k)))
    return im


def svg(pts, fill, bg=None):
    p = " ".join(f"{x:g},{y:g}" for x, y in pts)
    rect = f'<rect width="2000" height="2000" fill="#{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}"/>' if bg else ""
    f = "#%02X%02X%02X" % fill
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" role="img" aria-label="Laplace Research">{rect}<polygon points="{p}" fill="{f}"/></svg>\n'


# Tight crop of the mark (1% margin) for masks and logo files.
pad = 14
box = (301 - pad, 432 - pad, 1699 + pad, 1567.5 + pad)
w = 512
mark_only((w, round(w * (box[3] - box[1]) / (box[2] - box[0]))), NAVY_MARK, box).save(ROOT / "assets" / "mark.png", optimize=True)
mark_only((256, round(256 * (box[3] - box[1]) / (box[2] - box[0]))), NAVY_MARK, box).save(ROOT / "logo.png", optimize=True)

# Favicons: white Δ on navy, mark enlarged slightly so it holds at 16 px.
tile(96, 1.1).save(ROOT / "favicon-96.png", optimize=True)
tile(192, 1.1).save(ROOT / "favicon-192.png", optimize=True)
tile(180, 1.0).save(ROOT / "apple-touch-icon.png", optimize=True)
tile(256, 1.12).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

# Avatars for LinkedIn, GitHub, Hugging Face and X: these crop to a circle, so the mark sits at 85%.
k = 0.85
tile(2000, k).save(BRAND / "laplace-avatar-white-on-navy.png", optimize=True)
tile(800, k).save(BRAND / "laplace-avatar-white-on-navy-800.png", optimize=True)
(BRAND / "laplace-avatar-white-on-navy.svg").write_text(svg(scaled(k), WHITE, NAVY_BG))
print("ok")
