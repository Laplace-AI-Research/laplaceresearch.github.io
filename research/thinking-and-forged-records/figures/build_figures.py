"""Build the figures and chart data for /research/thinking-and-forged-records/.

Inputs
  --comparison  conviction repo results/comparisons/T_thinking_vs_nonthinking.json
                (Laplace-AI-Research/conviction @ 7ae8292).
  ../data/counts.json      k/n behind each rate (offline reconstruction; checked against the rates).
  ../data/twin-pairs.json  exploratory forged/trusted twin counts, computed offline
                from the gitignored item-level prediction files (see README.md).

Outputs (next to this script and in ../data/)
  fig1-accuracy-vs-forged.svg, fig2-paired-differences.svg, fig4-twin-pairs.svg
  thinking-paired.csv / thinking-paired.json (every number the charts draw)

Usage: python3 build_figures.py --comparison /path/to/T_thinking_vs_nonthinking.json
PNG exports are rendered from the SVGs by render_png.sh.
"""
import argparse, csv, json, pathlib
from html import escape

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"
MODELS = ["Qwen3-1.7B", "Qwen3-8B", "Qwen3.5-9B", "Granite-4.2-8B"]
METRICS = {
    "final_accuracy": ("Final-answer accuracy", "higher is better", +1),
    "fabricated_evidence_resistance": ("Forged-record resistance", "higher is better", +1),
    "pressure_flip_rate": ("Pressure flips", "lower is better", -1),
    "authenticated_update_accuracy": ("Authenticated-update accuracy", "higher is better", +1),
    "legitimate_correction_rate": ("Valid-correction acceptance", "higher is better", +1),
    "insufficient_accuracy": ("Correct abstention", "higher is better", +1),
}
FONT = "Inter, 'Helvetica Neue', Arial, sans-serif"
INK, MUTED, RULE, OFF, ON = "#23262d", "#5d626b", "#d9d6cf", "#6b7079", "#02338a"
W = 640
NARROW = False


def svg_open(h, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
            f'role="img" aria-labelledby="t d" font-family="{FONT}" fill="{INK}">',
            f"<title id=\"t\">{escape(title)}</title><desc id=\"d\">{escape(desc)}</desc>",
            f'<rect width="{W}" height="{h}" fill="#ffffff"/>']


def pct(v):
    return f"{100 * v:.1f}%"


def dumbbell(out, y0, d, metric, label, sense):
    x0, x1 = (140, W - 44) if NARROW else (170, 600)
    X = lambda v: x0 + (x1 - x0) * v
    out.append(f'<text x="20" y="{y0}" font-size="16" font-weight="600">{escape(label)}</text>')
    out.append(f'<text x="{W - 20}" y="{y0}" font-size="13" fill="{MUTED}" text-anchor="end">{sense}</text>')
    top, step = y0 + 26, 40
    for t in range(0, 101, 25):
        x = X(t / 100)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top - 8}" y2="{top + step * 4 - 18}" stroke="{RULE}"/>')
        out.append(f'<text x="{x:.1f}" y="{top + step * 4 - 2}" font-size="12" fill="{MUTED}" text-anchor="middle">{t}%</text>')
    for i, m in enumerate(MODELS):
        y = top + 10 + i * step
        a, b = d[m]["off"][metric]["value"], d[m]["on"][metric]["value"]
        out.append(f'<text x="20" y="{y + 5}" font-size="{13 if NARROW else 14}">{m}</text>')
        out.append(f'<line x1="{X(a):.1f}" x2="{X(b):.1f}" y1="{y}" y2="{y}" stroke="{ON}" stroke-opacity=".35" stroke-width="4"/>')
        out.append(f'<circle cx="{X(a):.1f}" cy="{y}" r="6" fill="#ffffff" stroke="{OFF}" stroke-width="2.5"/>')
        out.append(f'<circle cx="{X(b):.1f}" cy="{y}" r="6.5" fill="{ON}"/>')
        lo, hi = (a, b) if a < b else (b, a)
        lo_is_off = a < b
        out.append(f'<text x="{X(lo) - 12:.1f}" y="{y + 4}" font-size="12" text-anchor="end" fill="{OFF if lo_is_off else ON}">{pct(lo)}</text>')
        out.append(f'<text x="{X(hi) + 12:.1f}" y="{y + 4}" font-size="12" fill="{ON if lo_is_off else OFF}">{pct(hi)}</text>')
    return top + step * 4 + 12


def legend(out, y, items):
    x = 20
    for kind, text in items:
        if x > 20 and x + 30 + 7.1 * len(text) > W:
            x, y = 20, y + 24
        if kind == "off":
            out.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="6" fill="#fff" stroke="{OFF}" stroke-width="2.5"/>')
        elif kind == "on":
            out.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="6.5" fill="{ON}"/>')
        else:
            out.append(f'<rect x="{x}" y="{y - 11}" width="13" height="13" fill="{kind}"/>')
        out.append(f'<text x="{x + 20}" y="{y + 1}" font-size="13">{escape(text)}</text>')
        x += 30 + 7.1 * len(text)
    return y


def fig1(d):
    out = svg_open(492, "Final-answer accuracy and forged-record resistance, thinking off and on",
                   "Two dot plots, one row per model. In every model, thinking-on raises final-answer accuracy "
                   "and lowers forged-record resistance. Values: " + "; ".join(
                       f"{m}: accuracy {pct(d[m]['off']['final_accuracy']['value'])} to {pct(d[m]['on']['final_accuracy']['value'])}, "
                       f"forged-record resistance {pct(d[m]['off']['fabricated_evidence_resistance']['value'])} to "
                       f"{pct(d[m]['on']['fabricated_evidence_resistance']['value'])}" for m in MODELS) + ".")
    ly = legend(out, 24, [("off", "Thinking off (greedy, 200-token cap)"), ("on", "Thinking on (sampled, 4,096-token cap)")])
    y = dumbbell(out, ly + 38, d, "final_accuracy", "Final-answer accuracy", "higher is better")
    end = dumbbell(out, y + 26, d, "fabricated_evidence_resistance", "Forged-record resistance", "higher is better") + 10
    out.append("</svg>")
    out[0] = out[0].replace('0 0 640 492"', f'0 0 {W} {end}"').replace(f'0 0 {W} 492"', f'0 0 {W} {end}"').replace('height="492"', f'height="{end}"')
    out[2] = f'<rect width="{W}" height="{end}" fill="#ffffff"/>'
    return "\n".join(out)


def fig2(d):
    rows = ["final_accuracy", "fabricated_evidence_resistance", "pressure_flip_rate"]
    step, gap = 30, 58
    h = 66 + len(rows) * (22 + step * 4 + gap) + 20
    x0, x1, lo_, hi_ = (136, W - 62, -40, 40) if NARROW else (170, 560, -40, 40)
    X = lambda v: x0 + (x1 - x0) * (100 * v - lo_) / (hi_ - lo_)
    desc = []
    for met in rows:
        for m in MODELS:
            t = d[m]["thinking_minus_nonthinking"][met]
            desc.append(f"{METRICS[met][0]} {m}: {100*t['diff']:+.1f} points [{100*t['lo']:+.1f}, {100*t['hi']:+.1f}]")
    out = svg_open(h, "Paired thinking-on minus thinking-off differences with 95% intervals", "; ".join(desc) + ".")
    ly = legend(out, 24, [("on", "Interval excludes 0"), ("off", "Interval includes 0 (inconclusive)")])
    y = ly + 42
    for met in rows:
        label, sense, sign = METRICS[met]
        out.append(f'<text x="20" y="{y}" font-size="16" font-weight="600">{label}</text>')
        better = "better if right of 0" if sign > 0 else "better if left of 0"
        if NARROW:
            out.append(f'<text x="20" y="{y + 18}" font-size="13" fill="{MUTED}">{sense}; {better}</text>')
            y += 18
        else:
            out.append(f'<text x="{W - 20}" y="{y}" font-size="13" fill="{MUTED}" text-anchor="end">{sense}; {better}</text>')
        top = y + 22
        for t in range(lo_, hi_ + 1, 20):
            x = X(t / 100)
            out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top - 6}" y2="{top + step * 4 - 6}" stroke="{INK if t == 0 else RULE}" stroke-width="{1.5 if t == 0 else 1}"/>')
            out.append(f'<text x="{x:.1f}" y="{top + step * 4 + 8}" font-size="12" fill="{MUTED}" text-anchor="middle">{t:+d}</text>')
        for i, m in enumerate(MODELS):
            yy = top + 8 + i * step
            t = d[m]["thinking_minus_nonthinking"][met]
            sig = t["lo"] > 0 or t["hi"] < 0
            out.append(f'<text x="20" y="{yy + 5}" font-size="{13 if NARROW else 14}">{m}</text>')
            out.append(f'<line x1="{X(t["lo"]):.1f}" x2="{X(t["hi"]):.1f}" y1="{yy}" y2="{yy}" stroke="{ON if sig else OFF}" stroke-width="2.5"/>')
            if sig:
                out.append(f'<circle cx="{X(t["diff"]):.1f}" cy="{yy}" r="6" fill="{ON}"/>')
            else:
                out.append(f'<circle cx="{X(t["diff"]):.1f}" cy="{yy}" r="5.5" fill="#fff" stroke="{OFF}" stroke-width="2.5"/>')
            out.append(f'<text x="{W - 20}" y="{yy + 5}" font-size="13" text-anchor="end" fill="{ON if sig else MUTED}">{100*t["diff"]:+.1f}</text>')
        y = top + step * 4 + gap
    end = y - gap + 52
    out.append(f'<text x="{(x0 + x1) / 2}" y="{end - 12}" font-size="13" fill="{MUTED}" text-anchor="middle">{"On minus off, percentage points" if NARROW else "Thinking on minus thinking off, percentage points"}</text>')
    out.append("</svg>")
    out[0] = out[0].replace(f'0 0 {W} {h}"', f'0 0 {W} {end}"').replace(f'height="{h}"', f'height="{end}"')
    out[2] = f'<rect width="{W}" height="{end}" fill="#ffffff"/>'
    return "\n".join(out)


TWIN = [("both", "Both right", "#02338a"), ("accept_trusted_only", "Genuine right, forged wrong", "#a5b8dd"),
        ("reject_forged_only", "Forged right, genuine wrong", "#8d9199"), ("neither", "Both wrong", "#e3e1dc")]


def fig4(p):
    n = p["n_pairs"]
    x0, x1, step = (124, W - 20, 26) if NARROW else (210, 600, 26)
    h = 92 + len(MODELS) * (2 * step + 20) + 44
    X = lambda k: x0 + (x1 - x0) * k / n
    desc = []
    for m in MODELS:
        for s in ("off", "on"):
            r = p["models"][m][s]
            desc.append(f"{m} thinking {s}: " + ", ".join(f"{lab.lower()} {r[k]}" for k, lab, _ in TWIN))
    out = svg_open(h, f"Outcomes on {n} matched forged and authenticated record pairs (exploratory)", "; ".join(desc) + ".")
    ly = legend(out, 24, [(c, lab) for _, lab, c in TWIN[:2]])
    ly = legend(out, ly + 24, [(c, lab) for _, lab, c in TWIN[2:]])
    y = ly + 30
    for m in MODELS:
        out.append(f'<text x="20" y="{y + 14}" font-size="{13 if NARROW else 14}" font-weight="600">{m}</text>')
        for j, s in enumerate(("off", "on")):
            yy = y + 4 + j * step
            out.append(f'<text x="{x0 - 10}" y="{yy + 14}" font-size="13" fill="{MUTED}" text-anchor="end">{s if NARROW else "thinking " + s}</text>')
            acc = 0
            r = p["models"][m][s]
            for k, lab, c in TWIN:
                v = r[k]
                if v:
                    out.append(f'<rect x="{X(acc):.1f}" y="{yy}" width="{X(acc + v) - X(acc):.1f}" height="20" fill="{c}" stroke="#fff" stroke-width="1"/>')
                    if X(acc + v) - X(acc) > 22:
                        fill = "#fff" if k in ("both", "reject_forged_only") else INK
                        out.append(f'<text x="{(X(acc) + X(acc + v)) / 2:.1f}" y="{yy + 15}" font-size="12" text-anchor="middle" fill="{fill}">{v}</text>')
                acc += v
        y += 2 * step + 20
    if NARROW:
        out.append(f'<text x="20" y="{y + 16}" font-size="13" fill="{MUTED}">Number of pairs (of {n}).</text>')
        y += 30
    else:
        out.append(f'<text x="{(x0 + x1) / 2}" y="{y + 18}" font-size="13" fill="{MUTED}" text-anchor="middle">Number of pairs (of {n}). Each pair carries the same record text,</text>')
        out.append(f'<text x="{(x0 + x1) / 2}" y="{y + 36}" font-size="13" fill="{MUTED}" text-anchor="middle">delivered once as a tool response and once pasted into a user message.</text>')
        y += 50
    out.append("</svg>")
    out[0] = out[0].replace(f'0 0 {W} {h}"', f'0 0 {W} {y}"').replace(f'height="{h}"', f'height="{y}"')
    out[2] = f'<rect width="{W}" height="{y}" fill="#ffffff"/>'
    return "\n".join(out)


def export(d, comparison):
    rows = []
    for m in MODELS:
        for met, (label, sense, _) in METRICS.items():
            o, n_, t = d[m]["off"][met], d[m]["on"][met], d[m]["thinking_minus_nonthinking"][met]
            rows.append({"model": m, "metric": met, "label": label, "direction": sense,
                         "off_k": o["k"], "off_n": o["n"], "off": round(o["value"], 6),
                         "on_k": n_["k"], "on_n": n_["n"], "on": round(n_["value"], 6),
                         "diff": round(t["diff"], 6), "ci_lo": round(t["lo"], 6), "ci_hi": round(t["hi"], 6),
                         "p_boot": t["p_boot"]})
    with open(DATA / "thinking-paired.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    meta = {m: {"n_episodes": d[m]["n_episodes"], "mean_gen_tokens": round(d[m]["mean_gen_tokens"], 1),
                "unfinished": d[m]["unfinished"]} for m in MODELS}
    json.dump({"source": "Laplace-AI-Research/conviction@7ae8292 results/comparisons/T_thinking_vs_nonthinking.json",
               "comparison": comparison,
               "interval": "95% paired cluster bootstrap over 90 problem groups, 2,000 resamples, seed 0",
               "runs": meta, "rows": rows}, open(DATA / "thinking-paired.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparison", required=True)
    a = ap.parse_args()
    raw = json.load(open(a.comparison))
    d = raw["models"]
    counts = json.load(open(DATA / "counts.json"))["models"]
    for m in MODELS:
        for s in ("off", "on"):
            for met, v in d[m][s].items():
                c = counts[m][s][met]
                assert c["n"] and abs(c["k"] / c["n"] - v) < 1e-12, (m, s, met)
                d[m][s][met] = {"value": v, **c}
    export(d, raw["comparison"])
    p = json.load(open(DATA / "twin-pairs.json"))
    global W, NARROW
    for W, NARROW, suffix in ((640, False, ""), (400, True, "-narrow")):
        (HERE / f"fig1-accuracy-vs-forged{suffix}.svg").write_text(fig1(d))
        (HERE / f"fig2-paired-differences{suffix}.svg").write_text(fig2(d))
        (HERE / f"fig4-twin-pairs{suffix}.svg").write_text(fig4(p))


if __name__ == "__main__":
    main()
