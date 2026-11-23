# Signet — release thread v3 (X) · DRAFT for Tuesday 2026-11-25

10 posts, restyled after frontier-lab launch threads: one idea and one number per post, a takeaway chart on every
card, a "what we're releasing" post, caveats in one place. Cards: `out/thread3/NN-*.png` (1600×900).

---

### 1 · image: 01-title.png
Introducing Signet: open models (2B, 4B, 9B) that check where a record came from before they believe it.

Most models will accept a fake "database record" pasted into the chat. Signet won't, and it still changes its mind when the evidence is real.

---

### 2 · image: 02-example.png
Here's the failure.

The model has answered x = 12, correctly. The user then pastes a fake correction from a "constraint_service."

Qwen3.5-9B believes it and changes its answer to 4. Signet-9B recognizes the record didn't come from a tool and keeps 12.

---

### 3 · image: 03-result.png
The pattern holds at scale. Given the same record as a genuine tool message or pasted into the chat, Qwen3.5 adopts both at the same rate.

Signet-9B adopts 96% of genuine records and 1% of pasted ones, including in paste formats it never saw in training.

---

### 4 · image: 04-field.png
No other model we tested does this. Across 35 off-the-shelf models from the ConvictionBench leaderboard and our three earlier adapters, the gap between trusting a tool and trusting a paste is about zero.

For Signet, it's +0.77 to +0.97.

---

### 5 · image: 05-tradeoff.png
It isn't just more stubborn. A model that refuses every correction would also "resist" fake records.

On problem types never seen in training, Signet-9B rejects 98% of forged records and accepts 100% of valid corrections. Earlier models traded one for the other.

---

### 6 · image: 06-how.png
How we trained it: we made the wording useless.

Every genuine tool record in training is paired with its exact twin pasted into the chat, and every phrase appears with both labels. Only the channel predicts the right answer.

That pairing is what made the rule appear.

---

### 7 · image: 07-base.png
Finding 1: the base model decides whether RL can learn the rule at all.

Same GRPO recipe, same data, same starting accuracy. Qwen3-1.7B barely moved (+0.03, and +0.19 with twice the training). Qwen3.5-2B reached +0.79.

---

### 8 · image: 08-scale.png
Finding 2: imitation saturates bigger models. A 1,000-example warm-start left 4B and 9B nothing to learn in RL; 250 examples worked.

So the best recipe changes with scale: RL alone at 2B and 4B, a light warm-start then RL at 9B.

---

### 9 · image: 09-checks.png
We registered three checks before release, then ran them: a second training seed replicates, a never-published test split shows no contamination, and a reworded prompt costs at most 3.7 points.

Limits: synthetic tasks, and tool messages are trusted by construction.

---

### 10 · image: 10-release.png
Signet-2B, 4B and 9B are out now under Apache-2.0, with merged weights for 9B, code and every result.

Models: huggingface.co/Laplace-AI-Research
Code: github.com/Laplace-AI-Research/signet
Write-up: laplaceresearch.org/signet

Technical report next week.
