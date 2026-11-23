# Signet — LinkedIn post · DRAFT for Tuesday 2026-11-25

**Images (multi-image post, in this order):** `out/x-01-title.png`, `out/x-02-problem.png`, `out/x-03-channel.png`,
`out/x-04-9b.png`, `out/x-06-checks.png`. Alternative single image: `out/linkedin-hero.png` (1200×627).
Put the link in the post body; LinkedIn shows the `social.png` card when the article link is the last line.

---

Today Laplace Research is releasing Signet: three open models that check where a record came from before they
believe it.

Here's the problem. Language models increasingly act on what tools tell them: a database lookup, an account balance,
a search result. The text of a record is easy to copy. Where it came from is not. When we gave Qwen3.5-9B the same
record twice, once as a genuine tool response and once pasted into a user message, it believed 86% of the genuine ones
and 85% of the pasted ones. It couldn't tell them apart.

Signet can. Signet-9B, our largest model to date, adopts 96% of genuine tool records and 1% of pasted ones, including
paste formats it never saw in training.

It also does the rest of the job. On problem types held out of training entirely, Signet-9B:
• answers correctly 97.8% of the time (base model: 68.8%)
• gives in to pressure 1.1% of the time (base: 39.9%)
• rejects 97.9% of forged records (base: 15.8%)
• accepts every valid correction

The family comes in three sizes. Signet-4B nearly matches the 9B at less than half the size; Signet-2B fits the
tightest budgets.

We wrote down our release checks before running them, and all of them passed: a second training seed replicates the
result at every size, a private evaluation split that has never been published shows no contamination, and a reworded
system prompt costs at most 3.7 points. Where something was weaker, like one Signet-4B seed on unfamiliar paste
formats, the model card says so. Our 1.7B attempts didn't meet the bar, and we report that too.

A note on scope: this is a synthetic benchmark with a fixed response format, and tool messages are trusted by
construction. Signet learns to trust the channel it's told is trusted. It doesn't authenticate the world by itself.

Weights are Apache-2.0 on Hugging Face, with the code and every result behind them.

By Arya Somu and Bruce Nshuti Hirwa.

laplaceresearch.org/signet
