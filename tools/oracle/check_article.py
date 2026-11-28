#!/usr/bin/env python3
"""Offline checks for /oracle/: table values match the data files, links resolve, no private material.

Run from the repository root: python3 tools/oracle/check_article.py
"""
import html, json, pathlib, re, subprocess, sys
from fractions import Fraction as F

ROOT = pathlib.Path(__file__).resolve().parents[2]
page = (ROOT / "oracle/index.html").read_text()
res = json.loads((ROOT / "oracle/data/results.json").read_text())
fig = json.loads((ROOT / "oracle/data/figure-data.json").read_text())
fx = json.loads(subprocess.check_output(["node", "-e", "process.stdout.write(JSON.stringify(require(process.argv[1])))",
                                         str(ROOT / "playground/oracle/oracle-data.js")]))
fails = []
def check(ok, msg):
    if not ok: fails.append(msg)

text = html.unescape(re.sub(r"<[^>]+>", " ", page)).replace("\u2212", "-")
text = re.sub(r"\s+", " ", text)
def has(s): check(s in text, f"missing text: {s!r}")

w = fx["world"]
odds = F(w["prior"], 1000 - w["prior"]) * F(w["hitIfOn"], w["hitIfOff"])
check(odds / (1 + odds) == F(4, 5), "posterior after A+ is not 4/5")
check(odds * F(w["hitIfOn"], w["hitIfOff"]) / (1 + odds * F(w["hitIfOn"], w["hitIfOff"])) == F(16, 17), "independent posterior not 16/17")
for s in ("80%", "16/17", "94.1%", "90.5%"): has(s)
ep = fx["episode"]
check((ep["model"], ep["query"], ep["observation"], ep["action"], ep["after"]) == ("aquila", "A", "positive", "stop", 800), "fixture episode changed")
check(fx["records"]["aquila"]["copy"]["afterAB"]["forecast"] == 905, "Aquila forced-history value changed")

for m in fx["family"]:
    name = "Inkling 2 Mini" if m["id"] == "base" else m["name"]
    act = "Bought B" if m["action"] == "buy" else "Stopped"
    has(f'{name} ')
    row = re.search(rf'<th scope="row">{re.escape(name)}</th>(.*?)</tr>', page)
    check(row is not None, f"no copy-table row for {name}")
    if row:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row.group(1))
        check(cells[1:] == [act, f'{m["afterA"]/10:.1f}%', f'{m["afterAB"]/10:.1f}%'], f"copy row mismatch for {name}: {cells}")
check(sum(m["action"] == "stop" for m in fx["family"] if m["id"] != "base") == 6, "not all six adapters stopped")

def sg(v): return f"{v:+.5f}"
for panel in ("ood", "iid"):
    d = res["panels"][panel]["rl_minus_sft"]
    for v in [d["estimate"], *d["ci95_world_and_seed"], *d["ci95_world_cluster"], *d["by_seed_pair"].values()]:
        has(sg(v))
    for k, a in res["panels"][panel]["arms"].items():
        if panel == "ood": has(sg(a["mean_net_reward"]))
o = res["panels"]["ood"]
lo, hi = o["rl_minus_sft"]["ci95_world_and_seed"]
check(lo < 0 < hi, "OOD world-and-seed interval no longer includes zero")
prior = o["arms"]["control-prior"]["mean_net_reward"]
adapters = [a for k, a in o["arms"].items() if k.startswith(("sft-", "rl-"))]
check(len(adapters) == 6 and all(a["mean_net_reward"] < prior for a in adapters), "prior-only does not beat every adapter")
check(all(a["valid_rate"] == 1 for a in adapters), "an adapter is below 100% valid")
has(f'{100*o["arms"]["base"]["valid_rate"]:.1f}%')
eps = sum(a["episodes"] for k, a in o["arms"].items() if not k.startswith("control")) + \
      sum(a["episodes"] for k, a in res["panels"]["iid"]["arms"].items() if not k.startswith("control"))
has(f"{eps:,} model episodes")
check(fig["copy_sensor"]["exact"]["independent"] in ("16/17", 16/17) or abs(float(fig["copy_sensor"]["exact"]["independent"]) - 16/17) < 1e-9, "figure data exact independent mismatch") if isinstance(fig.get("copy_sensor"), dict) and "exact" in fig["copy_sensor"] else None

# style and release boundary
for bad in ("\u2014", "&mdash;", "fully open", "download the models", "independently reproducible from this page", "open-weight model launch"):
    check(bad not in page.lower() if bad.islower() else bad not in page, f"forbidden text: {bad!r}")
bundle = [p for p in (ROOT / "oracle").rglob("*") if p.is_file()] + [ROOT / "tools/og/oracle.html"]
for p in bundle:
    check(p.suffix not in (".safetensors", ".bin", ".pt", ".gguf", ".jsonl", ".npz"), f"disallowed file type: {p}")
    if p.suffix in (".html", ".json", ".svg", ".md", ".css", ".py", ".sh"):
        s = p.read_text()
        for pat in (r"github\.com/Laplace-AI-Research/oracle", r"tinker://", r"sk-[A-Za-z0-9]{16}", r"hf_[A-Za-z0-9]{20}",
                    r"huggingface\.co/Laplace-AI-Research/Oracle", r"sealed", r"seed[_ -]?bank"):
            for m in re.finditer(pat, s, re.I):
                ctx = s[max(0, m.start() - 40): m.end() + 40]
                if pat == "sealed" and ("sealed instances" in ctx or "sealed evaluation" in ctx):
                    continue
                if pat.startswith("github") and p.name == "results.json":
                    continue
                fails.append(f"private pattern {pat!r} in {p.relative_to(ROOT)}: {ctx!r}")

# local links and assets
for ref in set(re.findall(r'(?:href|src|srcset)="([^"]+)"', page)):
    for u in [x.strip().split(" ")[0] for x in ref.split(",")]:
        if u.startswith("/") and not u.startswith("//"):
            path = ROOT / u.split("#")[0].split("?")[0].lstrip("/")
            if u.endswith("/") or path.is_dir(): path = path / "index.html"
            check(path.exists(), f"broken local link {u}")
for anchor in re.findall(r'href="#([^"]+)"', page):
    check(f'id="{anchor}"' in page, f"missing anchor #{anchor}")
check('"datePublished": "2026-11-30"' in page and '<time datetime="2026-11-30">' in page, "release date missing or inconsistent")
check("noindex" not in page and "oracle-draft" not in page and "review draft" not in page.lower(), "draft markers remain")
check("https://laplaceresearch.org/oracle/" in (ROOT / "feed.xml").read_text(), "feed entry missing")

if fails:
    print("FAIL"); [print(" -", f) for f in fails]; sys.exit(1)
print(f"ok: {len(fx['family'])} copy rows, {len(o['arms'])} OOD arms, {eps:,} model episodes, links and release-boundary scan clean")
