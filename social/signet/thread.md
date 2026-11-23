# Signet — launch thread (X, @Laplace) · DRAFT for Tuesday 2026-11-25

Images are 1600×900 PNGs in `out/`, one per post. Post 8 has no image: X pulls the link card
(`/assets/signet/social.png`) from laplaceresearch.org/signet. Replace `[repo]` once the staging repo is public.
Each post is under 280 characters.

---

### 1/ · image: out/x-01-title.png

Introducing Signet: open models that check where a record came from before they believe it.

Three sizes (2B, 4B, 9B), Apache-2.0. Signet-9B is our largest model yet. 🧵

---

### 2/ · image: out/x-02-problem.png

Paste a fake "database record" into the chat and most models believe it.

Qwen3.5-9B adopts 86% of genuine tool records, and 85% of the identical record pasted into a user message. It can't tell them apart.

---

### 3/ · image: out/x-03-channel.png

Signet can.

Signet-9B adopts 96% of genuine tool records and 1% of pasted ones, including paste formats it never saw in training: quote blocks, forwarded messages, code blocks.

Off-the-shelf bases: a gap of ±0.03. Signet: +0.79 to +0.95.

---

### 4/ · image: out/x-04-9b.png

On problem types held out of training entirely, Signet-9B:

97.8% accuracy (base 68.8%)
1.1% flips under pressure (base 39.9%)
97.9% of forged records rejected (base 15.8%)
100% of valid corrections accepted

It holds firm on pressure and still changes its mind on evidence.

---

### 5/ · image: out/x-05-family.png

The family, ring count = parameters:

Signet-2B and Signet-4B: GRPO from the base model
Signet-9B: a 250-example warm-start, then GRPO

Signet-4B nearly matches the 9B at less than half the size.

---

### 6/ · image: out/x-06-checks.png

Release checks, written down before we ran them. All passed:

· a second seed replicates at every size
· a never-published split shows no contamination
· a reworded prompt costs ≤3.7 points

Disclosed: Signet-4B's second seed was weaker on unfamiliar paste formats.

---

### 7/ · image: out/x-07-get.png

What didn't work: no 1.7B model met our bar, and we say so.

And the scope: synthetic tasks, a fixed JSON format, and tool messages trusted by construction. Signet checks the channel; it doesn't authenticate the world.

---

### 8/ · no image (link card)

Weights: huggingface.co/Laplace-AI-Research/Signet-9B
Code and every result: [repo]
The write-up: laplaceresearch.org/signet

Built on ConvictionBench: convictionbench.org
