# Figures: When thinking helps models believe forged records

All charts are drawn by code; no generated imagery is used for data marks.

| File | Built from | Notes |
|---|---|---|
| `fig1-accuracy-vs-forged.svg/.png` | `T_thinking_vs_nonthinking.json` (`final_accuracy`, `fabricated_evidence_resistance`) | Article Fig. 1 |
| `fig2-paired-differences.svg/.png` | same file, `thinking_minus_nonthinking.{diff,lo,hi}` | Article Fig. 2 |
| `fig4-twin-pairs.svg/.png` | `../data/twin-pairs.json` | Article Fig. 3 (exploratory, not pre-registered) |

Article Fig. 4 is HTML in `../index.html` (logged episode `g001958-*`, final answers only).

Source revision: `Laplace-AI-Research/conviction@7ae8292b695145e1c40eb23862d3497fa960bbb8`.

Rebuild:

```
python3 build_figures.py --comparison /path/to/conviction/results/comparisons/T_thinking_vs_nonthinking.json
./render_png.sh   # needs google-chrome; renders 2x PNGs
```

`../data/counts.json` and `../data/twin-pairs.json` were computed offline from the item-level prediction
files (`results/**/predictions_*.jsonl`, gitignored in the conviction repo) with the repository's own
`sample_groups`, `compute` and `paired_bootstrap`. `build_figures.py` asserts that every count reproduces
the canonical rate.

Metric definitions: `conviction/evaluation/metrics.py`. Intervals: 95% paired cluster bootstrap over 90 problem
groups, 2,000 resamples, seed 0 (`conviction/evaluation/statistics.py`).
