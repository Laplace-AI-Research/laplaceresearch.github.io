"""Build the SVG figures and chart data for /oracle/.

Inputs (no other numbers are typed in here)
  ../../playground/oracle/oracle-data.js  Playground fixture: generative law and recorded
                                          copy-sensor responses (read with node).
  ../data/results.json                    Aggregates extracted from Laplace-AI-Research/oracle
                                          docs/results/scorecard.json @ d95df24 (see README.md).
Outputs
  fig1-wiring, fig2-copy-sensor, fig3-rl-effect, fig4-baselines, fig5-lineage (.svg, plus -narrow.svg)
  ../data/figure-data.json  every value the figures draw
Usage: python3 build_figures.py && ./render_png.sh
"""
import json, pathlib, subprocess
from fractions import Fraction as F
from html import escape

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATA = HERE.parent / "data"
FONT = "Inter, 'Helvetica Neue', Arial, sans-serif"
INK, MUTED, RULE, ACC, PALE, GREY = "#23262d", "#5d626b", "#d9d6cf", "#02338a", "#e8edf7", "#8d9199"

fixture = json.loads(subprocess.check_output(
    ["node", "-e", "process.stdout.write(JSON.stringify(require(process.argv[1])))",
     str(ROOT / "playground/oracle/oracle-data.js")]))
results = json.loads((DATA / "results.json").read_text())

world = fixture["world"]
prior = F(world["prior"], 1000)
p_on, p_off = F(world["hitIfOn"], 1000), F(world["hitIfOff"], 1000)
lr = p_on / p_off
odds0 = prior / (1 - prior)
post = lambda odds: odds / (1 + odds)
EXACT = {"afterA": post(odds0 * lr), "copy": post(odds0 * lr), "independent": post(odds0 * lr * lr)}
assert EXACT["afterA"] == F(4, 5) and EXACT["independent"] == F(16, 17)


def pct(v, d=1):
    return f"{100 * float(v):.{d}f}%"


def sgn(v, d=5):
    s = f"{v:+.{d}f}"
    return s.replace("-", "\u2212")


def svg(w, h, title, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-labelledby="t d" font-family="{FONT}" fill="{INK}">\n<title id="t">{escape(title)}</title>'
            f'<desc id="d">{escape(desc)}</desc>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def T(x, y, s, size=13, anchor="start", fill=INK, weight=None, mono=False, halo=False):
    a = f' font-weight="{weight}"' if weight else ""
    if halo:
        a += ' paint-order="stroke" stroke="#fff" stroke-width="4" stroke-linejoin="round"'
    f = ' font-family="\'Geist Mono\', ui-monospace, Menlo, monospace" letter-spacing=".04em"' if mono else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{a}{f}>{escape(s)}</text>'


def box(x, y, w, h, fill="#fff", stroke=INK, dash=False, sw=1.2):
    d = ' stroke-dasharray="4 3"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def line(x1, y1, x2, y2, stroke=INK, sw=1.2, dash=None, arrow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#ah)"' if arrow else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>'


def path(d, stroke=INK, sw=1.4, arrow=False, dash=None):
    m = ' marker-end="url(#ah)"' if arrow else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{m}{da}/>'


ARROW = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker></defs>')


# ------------------------------------------------------------------ Fig. 1 wiring
def wiring_panel(x0, y0, w, kind):
    out = []
    copy = kind == "copy"
    out.append(T(x0, y0, "Same sensor" if copy else "Independent sensors", 15, weight=600))
    out.append(T(x0, y0 + 18, "Display B copies sensor A" if copy else "Sensor B errs independently of A, given the signal", 12, fill=MUTED))
    top = y0 + 36
    sx, sy, bw, bh = x0, top + 42, 66, 48
    out.append(box(sx, sy, bw, bh, PALE, ACC))
    out.append(T(sx + bw / 2, sy + 20, "SIGNAL", 10.5, "middle", ACC, mono=True))
    out.append(T(sx + bw / 2, sy + 38, "on or off", 12, "middle", INK))
    cx = x0 + 84
    dx = x0 + w - 80
    ya, yb = top + 8, top + 86
    # physical sensors
    sensors = [("SENSOR A", ya if not copy else top + 42)] + ([] if copy else [("SENSOR B", yb)])
    for name, y in sensors:
        out.append(box(cx, y, 88, 48, "#fff", INK, sw=1.6))
        out.append(T(cx + 44, y + 20, name, 10.5, "middle", INK, mono=True))
        out.append(T(cx + 44, y + 37, "80% accurate", 12, "middle", MUTED))
        out.append(path(f"M{sx + bw} {sy + bh / 2} C{(sx + bw + cx) / 2} {sy + bh / 2} {(sx + bw + cx) / 2} {y + 24} {cx - 2} {y + 24}", INK, 1.4, True))
    # displays
    for i, (name, y) in enumerate((("DISPLAY A", ya), ("DISPLAY B", yb))):
        out.append(box(dx, y, 80, 48, "#fff", GREY, dash=True))
        out.append(T(dx + 40, y + 19, name, 10.5, "middle", MUTED, mono=True))
        out.append(T(dx + 40, y + 38, "Positive", 13, "middle", ACC, weight=600))
        src_y = (top + 42 + 24) if copy else (ya + 24 if i == 0 else yb + 24)
        out.append(path(f"M{cx + 88} {src_y} C{(cx + 88 + dx) / 2} {src_y} {(cx + 88 + dx) / 2} {y + 24} {dx - 2} {y + 24}", ACC if copy else INK, 1.4, True))
    if copy:
        out.append(T(dx + 40, top + 70, "one wire, two ends", 11, "middle", ACC))
    ry = top + 152
    out.append(line(x0, ry - 14, x0 + w, ry - 14, RULE, 1))
    out.append(T(x0, ry + 4, "Exact probability the signal is on", 11, fill=MUTED, mono=True))
    rows = [("After A+", pct(EXACT["afterA"], 0)),
            ("After A+ and B+", pct(EXACT["copy"], 0) if copy else f"{pct(EXACT['independent'])} (16/17)")]
    for j, (k, v) in enumerate(rows):
        out.append(T(x0, ry + 26 + j * 22, k, 13))
        out.append(T(x0 + w, ry + 26 + j * 22, v, 15, "end", ACC, weight=600))
    note = "B adds a likelihood ratio of 1: odds stay 4:1" if copy else "B multiplies the odds by 4 again: 4:1 becomes 16:1"
    out.append(T(x0, ry + 76, note, 12, fill=MUTED))
    return out, ry + 86


def fig_wiring(narrow):
    w = 400 if narrow else 640
    pw = w - 40 if narrow else 284
    body = [ARROW]
    p1, h1 = wiring_panel(20, 30, pw, "copy")
    if narrow:
        p2, h2 = wiring_panel(20, h1 + 40, pw, "independent")
    else:
        p2, h2 = wiring_panel(336, 30, pw, "independent")
        body.append(line(320, 20, 320, h1 - 4, RULE, 1))
    body += p1 + p2
    h = max(h1, h2) + 20
    desc = ("Two wiring diagrams with both displays positive. Same sensor: one physical sensor A feeds display A and display B; "
            f"exact probability after A+ is {pct(EXACT['afterA'], 0)} and after A+ and the copy is still {pct(EXACT['copy'], 0)}. "
            "Independent sensors: sensor A feeds display A and a separate sensor B feeds display B; exact probability after A+ is "
            f"{pct(EXACT['afterA'], 0)} and after A+ and B+ is 16/17, {pct(EXACT['independent'])}. Generative law and exact calculation only; no model behavior.")
    return svg(w, h, "Same sensor versus independent sensors: exact probabilities", desc, body)


# ------------------------------------------------------------------ Fig. 2 copy-sensor dumbbell
FAM = {m["id"]: m for m in fixture["family"]}
ROWS = [("Base control", ["base"]), ("Seed 173", ["lyra", "vega"]), ("Seed 271", ["aquila", "altair"]), ("Seed 389", ["cygnus", "deneb"])]
SHORT = {"base": "Inkling 2 Mini", "lyra": "Oracle Lyra", "vega": "Oracle Vega", "aquila": "Oracle Aquila",
         "altair": "Oracle Altair", "cygnus": "Oracle Cygnus", "deneb": "Oracle Deneb"}
ROLE = {"base": "base", "lyra": "SFT", "vega": "RL", "aquila": "SFT", "altair": "RL", "cygnus": "SFT", "deneb": "RL"}
ACTION = {"buy": "Bought B", "stop": "Stopped"}


def marker_a(x, y):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#fff" stroke="{INK}" stroke-width="2"/>'


def marker_b(x, y):
    return f'<rect x="{x - 5.5:.1f}" y="{y - 5.5:.1f}" width="11" height="11" fill="{ACC}"/>'


def fig_copy(narrow):
    w = 400 if narrow else 640
    x0, x1 = (20, 380) if narrow else (268, 520)
    X = lambda v: x0 + (x1 - x0) * float(v)
    body = [ARROW.replace(INK, ACC).replace('id="ah"', 'id="ah"')]
    # legend
    body.append(marker_a(26, 22)); body.append(T(38, 26, "Forecast after A+", 12.5))
    lx, ly = (26, 44) if narrow else (170, 22)
    body.append(marker_b(lx, ly)); body.append(T(lx + 12, ly + 4, "After forced A+, B+ (told B copies A)", 12.5))
    y = 70 if narrow else 58
    if not narrow:
        body.append(T(20, y, "MODEL", 10.5, fill=MUTED, mono=True))
        body.append(T(166, y, "ACTION AFTER A+", 10.5, fill=MUTED, mono=True))
        body.append(T(w - 20, y, "A+ \u2192 A+, B+", 10.5, "end", MUTED, mono=True))
    y += 14
    rows_y = []
    step = 54 if narrow else 30
    for gi, (glabel, ids) in enumerate(ROWS):
        y += 26 if gi else 8
        body.append(T(20, y, glabel.upper() + ("" if gi == 0 else "  \u00b7  supervised \u2192 RL"), 10, fill=MUTED, mono=True))
        y += 0 if narrow else -8
        for mid in ids:
            m = FAM[mid]
            y += step
            cy = y - (8 if narrow else 4)
            name = SHORT[mid]
            act = ACTION[m["action"]]
            vals = f"{pct(m['afterA'] / 1000)} \u2192 {pct(m['afterAB'] / 1000)}"
            if narrow:
                body.append(T(20, y - 30, name, 13, weight=600, halo=True))
                body.append(T(20 + 7.6 * len(name) + 8, y - 30, f"{ROLE[mid]} \u00b7 {act}", 12, fill=MUTED, halo=True))
                body.append(T(w - 20, y - 30, vals, 12, "end", halo=True))
            else:
                body.append(T(20, cy + 4, name, 13, weight=600 if mid != "base" else None))
                body.append(T(130, cy + 4, ROLE[mid], 11, fill=MUTED))
                body.append(T(166, cy + 4, act, 12.5, fill=ACC if m["action"] == "buy" else INK))
                body.append(T(w - 20, cy + 4, vals, 12.5, "end"))
            a, b = m["afterA"] / 1000, m["afterAB"] / 1000
            if a != b:
                body.append(f'<line x1="{X(a) + 6:.1f}" y1="{cy:.1f}" x2="{X(b) - 8:.1f}" y2="{cy:.1f}" stroke="{ACC}" stroke-width="1.6" marker-end="url(#ah)"/>')
            body.append(marker_b(X(b), cy))
            body.append(marker_a(X(a), cy))
            rows_y.append(cy)
    top, bot = (82 if narrow else 74), y + 12
    for t in range(0, 101, 20):
        x = X(t / 100)
        body.insert(1, line(x, top, x, bot, "#efede8", 1))
        body.append(T(x, bot + 16, f"{t}%", 11, "middle", MUTED))
    ex = X(EXACT["copy"])
    body.insert(1, line(ex, top - 4, ex, bot, INK, 1.4, "5 3"))
    body.append(T(ex if not narrow else w / 2, bot + 32, f"Exact posterior {pct(EXACT['copy'], 0)} " + ("in both conditions" if narrow else "after A+ and after the copy"), 11.5, "middle", INK))
    body.append(T((x0 + x1) / 2, bot + 48, "Reported probability that the signal is on", 11, "middle", MUTED))
    h = bot + 62
    desc = "Recorded single responses on the fixed copy-sensor history. " + "; ".join(
        f"{SHORT[m['id']]}: action after A+ {ACTION[m['action']].lower()}, forecast after A+ {pct(m['afterA'] / 1000)}, after forced A+ and B+ {pct(m['afterAB'] / 1000)}"
        for m in fixture["family"]) + f". Exact posterior {pct(EXACT['copy'], 0)} in both conditions."
    return svg(w, h, "Recorded forecasts before and after a forced duplicate reading", desc, body)


# ------------------------------------------------------------------ Fig. 3 RL effect
def fig_rl(narrow):
    w = 400 if narrow else 640
    lab = 20 if narrow else 206
    x0, x1 = (lab + 10, w - 24) if narrow else (lab + 14, w - 28)
    lo, hi = -0.02, 0.04
    X = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)
    pairs = results["seed_pairs"]
    body = []
    y = 26
    body.append(f'<circle cx="26" cy="{y - 4}" r="6" fill="{ACC}"/>'); body.append(T(38, y, "Pooled estimate with 95% world-and-seed interval", 12.5))
    y += 20
    body.append(f'<path d="M26 {y - 10} L32 {y - 4} L26 {y + 2} L20 {y - 4} z" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'); body.append(T(38, y, "One seed pair (no interval: one run each)", 12.5))
    top = y + 20
    blocks = [("ood", "Structural holdout (primary)"), ("iid", "In-distribution (secondary)")]
    yy = top + 16
    marks = []
    for key, label in blocks:
        r = results["panels"][key]["rl_minus_sft"]
        body.append(T(20, yy, label.upper(), 10.5, fill=MUTED if key == "iid" else INK, mono=True, halo=True))
        yy += 26
        c = r["ci95_world_and_seed"]
        col = ACC if key == "ood" else GREY
        if narrow:
            body.append(T(20, yy - 12, f"Pooled, 3 pairs  {sgn(r['estimate'])}  [{sgn(c[0])}, {sgn(c[1])}]", 12, weight=600 if key == "ood" else None, halo=True))
            yy += 6
        else:
            yy += 12
            body.append(T(lab, yy + 4, "Pooled, three pairs", 13, "end", weight=600 if key == "ood" else None))
        body.append(line(X(c[0]), yy, X(c[1]), yy, col, 2.4))
        body.append(line(X(c[0]), yy - 6, X(c[0]), yy + 6, col, 2))
        body.append(line(X(c[1]), yy - 6, X(c[1]), yy + 6, col, 2))
        body.append(f'<circle cx="{X(r["estimate"]):.1f}" cy="{yy}" r="6.5" fill="{col}"/>')
        if not narrow:
            body.append(T((X(c[0]) + X(c[1])) / 2, yy - 12, f"{sgn(r['estimate'])}  [{sgn(c[0])}, {sgn(c[1])}]", 12, "middle", halo=True))
        marks.append((key, "pooled", r["estimate"], c))
        yy += 30
        for seed in ("173", "271", "389"):
            v = r["by_seed_pair"][seed]
            name = f"{pairs[seed][0].split()[1]} \u2192 {pairs[seed][1].split()[1]}"
            if narrow:
                body.append(T(20, yy - 12, f"{name} (seed {seed})  {sgn(v)}", 12, fill=INK if key == "ood" else MUTED, halo=True))
                yy += 4
            else:
                body.append(T(lab, yy + 4, f"{name} (seed {seed})", 12.5, "end", INK if key == "ood" else MUTED))
            xv = X(v)
            body.append(f'<path d="M{xv:.1f} {yy - 6} L{xv + 6:.1f} {yy} L{xv:.1f} {yy + 6} L{xv - 6:.1f} {yy} z" fill="#fff" stroke="{INK if key == "ood" else GREY}" stroke-width="1.6"/>')
            if not narrow:
                body.append(T(xv + 11, yy + 4, sgn(v), 12, fill=INK if key == "ood" else MUTED, halo=True))
            marks.append((key, seed, v, None))
            yy += 26 if not narrow else 34
        yy += 14
    bot = yy - 18
    thr = results["panels"]["ood"]["rl_minus_sft"]["practical_threshold"]
    body.insert(0, line(X(0), top, X(0), bot, INK, 1.4))
    body.insert(0, line(X(thr), top, X(thr), bot, MUTED, 1.2, "5 3"))
    for t in (-0.02, -0.01, 0, 0.01, 0.02, 0.03, 0.04):
        body.insert(0, line(X(t), top, X(t), bot, "#efede8", 1))
        body.append(T(X(t), bot + 16, sgn(t, 2), 11, "middle", MUTED))
    body.append(T(X(0), bot + 32, "No effect", 11, "middle", INK))
    body.append(T(X(thr) + 4, bot + 32, f"Practical threshold {sgn(thr, 3)}", 11, "start", MUTED))
    body.append(T((x0 + x1) / 2, bot + 50, "RL minus SFT, mean net reward per episode (higher favors RL)", 11, "middle", MUTED))
    h = bot + 64
    o, i = results["panels"]["ood"]["rl_minus_sft"], results["panels"]["iid"]["rl_minus_sft"]
    desc = (f"Structural holdout pooled RL minus SFT mean net reward {sgn(o['estimate'])}, 95% world-and-seed interval "
            f"{sgn(o['ci95_world_and_seed'][0])} to {sgn(o['ci95_world_and_seed'][1])}, which includes zero. Seed pairs: "
            + ", ".join(f"{results['seed_pairs'][s][0]} to {results['seed_pairs'][s][1]} {sgn(o['by_seed_pair'][s])}" for s in ("173", "271", "389"))
            + f". In-distribution pooled {sgn(i['estimate'])}, interval {sgn(i['ci95_world_and_seed'][0])} to {sgn(i['ci95_world_and_seed'][1])}; seed pairs "
            + ", ".join(sgn(i["by_seed_pair"][s]) for s in ("173", "271", "389"))
            + f". Dashed line: preregistered practical threshold {sgn(thr, 3)}.")
    return svg(w, h, "Change in mean net reward after RL, pooled and by seed pair", desc, body)


# ------------------------------------------------------------------ Fig. 4 baselines
ARM_ORDER = ["control-exact", "control-prior", "rl-271", "rl-173", "sft-173", "sft-389", "sft-271", "rl-389", "base"]
KIND = {"control-exact": "ref", "control-prior": "ref", "base": "base"}


def arm_mark(kind, x, y):
    if kind == "ref":
        return f'<rect x="{x - 5.5:.1f}" y="{y - 5.5:.1f}" width="11" height="11" fill="#fff" stroke="{INK}" stroke-width="1.8"/>'
    if kind == "base":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#fff" stroke="{GREY}" stroke-width="2"/><line x1="{x - 4:.1f}" y1="{y - 4:.1f}" x2="{x + 4:.1f}" y2="{y + 4:.1f}" stroke="{GREY}" stroke-width="1.6"/>'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{ACC}"/>'


def dot_panel(body, y, w, title, sub, arms, lo, hi, ticks, narrow, labels_right=True):
    lab = 20 if narrow else 196
    x0, x1 = (24, w - 70) if narrow else (lab + 16, w - 76)
    X = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)
    A = results["panels"]["ood"]["arms"]
    body.append(T(20, y, title, 13.5, weight=600))
    body.append(T(20, y + 17, sub, 11.5, fill=MUTED))
    top = y + 30
    yy = top + 14
    step = 34 if narrow else 24
    for k in arms:
        v = A[k]["mean_net_reward"]
        name = A[k]["name"]
        if narrow:
            body.append(T(20, yy - 9, name, 12, halo=True))
            yy += 6
        else:
            body.append(T(lab, yy + 4, name, 12.5, "end", MUTED if k == "base" else INK))
        body.append(line(x0, yy, X(v), yy, "#efede8", 1))
        body.append(arm_mark(KIND.get(k, "adapter"), X(v), yy))
        body.append(T(X(v) + 10, yy + 4, sgn(v), 11.5, halo=True))
        yy += step
    bot = yy - step + 14
    for t in ticks:
        body.insert(0, line(X(t), top, X(t), bot, "#efede8", 1))
        body.append(T(X(t), bot + 15, sgn(t, 2), 10.5, "middle", MUTED))
    return bot + 22


def fig_baselines(narrow):
    w = 400 if narrow else 640
    body = []
    y = 24
    items = [("adapter", "Trained adapter"), ("ref", "Symbolic reference or baseline"), ("base", "Untrained base")]
    x = 20
    for kind, txt in items:
        if narrow and x + 30 + 6.8 * len(txt) > w:
            x, y = 20, y + 20
        body.append(arm_mark(kind, x + 6, y - 4)); body.append(T(x + 18, y, txt, 12)); x += 34 + 6.6 * len(txt)
    y += 34
    y = dot_panel(body, y, w, "A. Full range, all arms", "Axis \u22121.2 to 0. Higher reward is better.",
                  ARM_ORDER, -1.2, 0.0, [-1.2, -0.9, -0.6, -0.3, 0.0], narrow)
    y += 24
    y = dot_panel(body, y, w, "B. Detail, zoomed", ("Axis \u22120.28 to \u22120.17. Base (\u22121.14332) is off scale; see A." if narrow else "Axis \u22120.28 to \u22120.17 only. The base (\u22121.14332) is off this scale; see A."),
                  ARM_ORDER[:-1], -0.28, -0.17, [-0.28, -0.25, -0.22, -0.19], narrow)
    body.append(T(w / 2, y + 6, "Structural-holdout mean net reward per episode" + ("" if narrow else f" ({results['panels']['ood']['episodes_per_arm']:,} episodes per arm)"), 11, "middle", MUTED))
    h = y + 22
    A = results["panels"]["ood"]["arms"]
    desc = "Structural-holdout mean net reward, higher is better: " + "; ".join(f"{A[k]['name']} {sgn(A[k]['mean_net_reward'])}" for k in ARM_ORDER) + \
        ". Panel A shows all arms on a full axis from -1.2 to 0; panel B zooms to -0.28 to -0.17 and omits the base."
    return svg(w, h, "Structural-holdout net reward: trained adapters, baselines and base", desc, body)


# ------------------------------------------------------------------ Fig. 5 lineage
def fig_lineage(narrow):
    names = results["seed_pairs"]
    body = [ARROW]
    if not narrow:
        w = 640
        body.append(box(20, 40, 118, 96, PALE, ACC)); body.append(T(79, 60, "SYNTHETIC LAWS", 10, "middle", ACC, mono=True))
        for i, s in enumerate(["Training families:", "independent", "shared source", "common cause"]):
            body.append(T(79, 80 + i * 15, s, 11.5 if i else 11, "middle", INK if i else MUTED))
        body.append(box(160, 56, 104, 64)); body.append(T(212, 78, "EXACT", 10, "middle", INK, mono=True))
        body.append(T(212, 94, "teacher", 11.5, "middle")); body.append(T(212, 109, "demonstrations", 11.5, "middle"))
        body.append(line(138, 88, 156, 88, arrow=True))
        for i, s in enumerate(("173", "271", "389")):
            y = 24 + i * 46
            body.append(box(290, y, 104, 36)); body.append(T(342, y + 16, names[s][0], 12, "middle", weight=600)); body.append(T(342, y + 30, f"SFT \u00b7 seed {s}", 10.5, "middle", MUTED))
            body.append(path(f"M264 88 C276 88 278 {y + 18} 287 {y + 18}", arrow=True))
            body.append(box(424, y, 104, 36, "#fff", ACC)); body.append(T(476, y + 16, names[s][1], 12, "middle", ACC, weight=600)); body.append(T(476, y + 30, "RL descendant", 10.5, "middle", MUTED))
            body.append(line(394, y + 18, 421, y + 18, arrow=True))
            body.append(path(f"M528 {y + 18} C540 {y + 18} 542 88 551 88", arrow=True, sw=1.1))
        body.append(T(342, 14, "THREE SFT MODELS", 9.5, "middle", MUTED, mono=True))
        body.append(T(476, 14, "THREE RL DESCENDANTS", 9.5, "middle", MUTED, mono=True))
        body.append(box(554, 40, 70, 96, "#fff", INK, sw=1.6)); body.append(T(589, 62, "PAIRED", 9.5, "middle", INK, mono=True)); body.append(T(589, 76, "EVAL", 9.5, "middle", INK, mono=True))
        for i, s in enumerate(["same", "worlds and", "budgets for", "every arm"]):
            body.append(T(589, 94 + i * 12, s, 10.5, "middle", MUTED))
        body.append(box(20, 172, 604, 58, "#fff", GREY, dash=True))
        body.append(T(32, 192, "HELD-OUT EVALUATION (never trained on)", 10, fill=MUTED, mono=True))
        body.append(T(32, 211, f"IID: {results['panels']['iid']['worlds']} new worlds from the training families", 12))
        body.append(T(32, 225, f"Structural holdout: {results['panels']['ood']['worlds']} worlds, XOR and switch", 12))
        body.append(T(612, 211, "Budgets 0, 2, 4, 8 credits", 12, "end"))
        body.append(T(612, 225, "Seven model arms and symbolic baselines", 12, "end"))
        body.append(path("M589 136 L589 168", arrow=True))
        h = 246
    else:
        w = 400
        y = 20
        body.append(box(20, y, 360, 52, PALE, ACC)); body.append(T(32, y + 20, "SYNTHETIC LAWS", 10, fill=ACC, mono=True)); body.append(T(32, y + 40, "Training families: independent, shared source, common cause", 11.5))
        body.append(line(200, y + 52, 200, y + 68, arrow=True)); y += 72
        body.append(box(20, y, 360, 34)); body.append(T(200, y + 22, "Exact teacher demonstrations", 12, "middle"))
        body.append(line(200, y + 34, 200, y + 50, arrow=True)); y += 56
        body.append(T(110, y, "SFT", 10, "middle", MUTED, mono=True)); body.append(T(290, y, "RL DESCENDANT", 10, "middle", MUTED, mono=True)); y += 8
        for s in ("173", "271", "389"):
            body.append(box(30, y, 160, 34)); body.append(T(110, y + 15, names[s][0], 12, "middle", weight=600)); body.append(T(110, y + 28, f"seed {s}", 10.5, "middle", MUTED))
            body.append(line(190, y + 17, 207, y + 17, arrow=True))
            body.append(box(210, y, 160, 34, "#fff", ACC)); body.append(T(290, y + 15, names[s][1], 12, "middle", ACC, weight=600)); body.append(T(290, y + 28, f"seed {s}", 10.5, "middle", MUTED))
            y += 42
        body.append(line(200, y, 200, y + 16, arrow=True)); y += 20
        body.append(box(20, y, 360, 104, "#fff", GREY, dash=True))
        for i, (s, c, f) in enumerate([("PAIRED HELD-OUT EVALUATION", MUTED, True), ("Same worlds and budgets (0, 2, 4, 8) for every arm", INK, False),
                                       (f"IID: {results['panels']['iid']['worlds']} new worlds from training families", INK, False),
                                       (f"Structural holdout: {results['panels']['ood']['worlds']} worlds, XOR and switch", INK, False),
                                       ("Never used in training", MUTED, False)]):
            body.append(T(32, y + 20 + i * 19, s, 10 if f else 11.5, fill=c, mono=f))
        h = y + 120
    desc = ("Synthetic laws from three training families feed exact teacher demonstrations, which train three supervised models "
            + ", ".join(f"{names[s][0]} (seed {s})" for s in names) + ". Each has one RL descendant: "
            + ", ".join(f"{names[s][1]} from {names[s][0]}" for s in names)
            + f". All arms are evaluated on the same held-out worlds and budgets: {results['panels']['iid']['worlds']} IID worlds and "
            + f"{results['panels']['ood']['worlds']} structural-holdout worlds using XOR and switch mechanisms that never appear in training.")
    return svg(w, h, "Oracle experiment lineage", desc, body)


FIGS = {"fig1-wiring": fig_wiring, "fig2-copy-sensor": fig_copy, "fig3-rl-effect": fig_rl,
        "fig4-baselines": fig_baselines, "fig5-lineage": fig_lineage}

if __name__ == "__main__":
    for name, fn in FIGS.items():
        (HERE / f"{name}.svg").write_text(fn(False))
        (HERE / f"{name}-narrow.svg").write_text(fn(True))
    o, i = results["panels"]["ood"], results["panels"]["iid"]
    fd = {"source": {"fixture": "playground/oracle/oracle-data.js", "aggregates": results["source"]},
          "fig1_exact_posteriors": {"after_A_positive": str(EXACT["afterA"]), "after_A_and_copy": str(EXACT["copy"]), "after_A_and_independent_B": str(EXACT["independent"])},
          "fig2_copy_sensor_recorded": [{"model": SHORT[m["id"]], "action_after_A": ACTION[m["action"]], "forecast_after_A": m["afterA"] / 1000, "forecast_after_forced_A_B": m["afterAB"] / 1000} for m in fixture["family"]],
          "fig3_rl_minus_sft": {k: {kk: p["rl_minus_sft"][kk] for kk in ("estimate", "ci95_world_and_seed", "by_seed_pair", "practical_threshold")} for k, p in (("ood", o), ("iid", i))},
          "fig4_ood_mean_net_reward": {o["arms"][k]["name"]: o["arms"][k]["mean_net_reward"] for k in ARM_ORDER}}
    (DATA / "figure-data.json").write_text(json.dumps(fd, indent=2) + "\n")
    print("wrote", ", ".join(FIGS))
