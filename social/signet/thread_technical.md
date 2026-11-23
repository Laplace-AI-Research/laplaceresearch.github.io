# Signet — technical launch thread (X) · DRAFT for Tuesday 2026-11-25

13 posts. Cards: `out/thread2/NN-*.png` (1600×900, numbered in posting order). URLs count as 23 characters.
Replace `[repo]` if the staging repo name changes.

---

### 1 · image: 01-title.png
Introducing Signet: open models (2B, 4B, 9B) that check where a record came from before they believe it.

Most models will accept a "database record" pasted into the chat. Signet won't, and it still changes its mind on real evidence.

Signet-9B is our largest model yet. 🧵

---

### 2 · image: 02-transcript.png
The failure in one example. The model answers x = 12, correctly. Then the user pastes a fake "constraint_service" correction.

Qwen3.5-9B believes it and switches to 4.

Signet-9B: "The text in the user message is not an authenticated tool record." It keeps 12.

---

### 3 · image: 03-adoption.png
It isn't one bad example. We gave models the same record two ways: as a genuine tool message, and pasted into a user turn.

Qwen3.5 adopts both at the same rate, at every size. Signet-9B adopts 96% of genuine records and 1% of pasted ones.

---

### 4 · image: 04-forest.png
We ran the same control on 35 off-the-shelf models from the ConvictionBench leaderboard, plus our three earlier adapters.

Every one sits at a channel gap of about zero. Signet-2B, 4B and 9B: +0.77 to +0.97.

---

### 5 · image: 05-pareto.png
Stubbornness isn't the fix: a useful model still has to accept valid corrections, and every earlier model trades one for the other.

On problem types never seen in training, Signet-9B rejects 98% of forged records and accepts 100% of valid corrections.

---

### 6 · image: 06-method.png
How: make the wording useless.

8,805 derived training episodes in which every pointer and forger phrase appears with both labels, and every genuine tool record is paired with its exact twin pasted into the user turn.

Only the channel predicts the label.

---

### 7 · image: 07-ablation.png
The pairing was the fix. Our first recipe learned no channel rule (gap −0.02).

More samples and a difficulty prefilter didn't help. Pairing each record with its pasted twin did (+0.24), and doubling the contrast data pushed it further.

---

### 8 · image: 08-base.png
Finding 1: the base model decides whether RL can find the rule at all.

Same GRPO recipe, same data, two bases with the same starting accuracy. Qwen3-1.7B reaches a channel gap of +0.03 (+0.19 at 800 steps). Qwen3.5-2B reaches +0.79.

---

### 9 · image: 09-scale.png
Findings 2 and 3: imitation saturates bigger models. A 1,000-example warm-start left 4B and 9B nothing for GRPO to learn; 250 examples worked.

And the best recipe flips with scale: RL-only wins at 2B and 4B, warm-start + GRPO at 9B.

---

### 10 · image: 10-dynamics.png
The training curves show the split. RL-only runs plateau for ~200 steps, then jump. After a light warm-start, 9B just climbs.

We didn't evaluate intermediate checkpoints, so "the jump is the channel rule clicking" is a hypothesis, not a result.

---

### 11 · image: 11-errors.png
We read the mistakes. Signet-9B's errors on the channel tests are mostly arithmetic: 60 of 69 wrong answers on pasted records reject the paste, then miscompute.

Signet-4B gets fooled by forwarded messages. Signet-2B tends to ignore records entirely.

---

### 12 · image: 12-checks.png
Before release we wrote down three checks, then ran them:
· a second training seed replicates at every size
· a never-published split shows no contamination
· a reworded prompt costs ≤3.7 points

All passed. Signet-4B's seed variance is on its model card.

---

### 13 · image: 13-get.png
Scope: synthetic tasks, tool messages trusted by construction. Signet checks the channel; it doesn't authenticate the world.

Weights (Apache-2.0): huggingface.co/Laplace-AI-Research
Code + every result: github.com/Laplace-AI-Research/signet
Write-up: laplaceresearch.org/signet

Technical report next week.
