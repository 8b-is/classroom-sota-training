# The $200 lane — the budget run

The advice is right, and the golden youth already follows half of it. The
pupil is a **continued-train of a small pretrained model** (Qwen2.5-0.5B) —
not a from-scratch pre-train. For $200, the shape is:

1. **Don't pre-train.** Fine-tune an existing open-weight model with
   **LoRA / QLoRA** (Mistral, Llama 3 8B, Phi-3, or the 0.5B pupil itself).
2. **Tiny, curated data.** TinyStories (Microsoft's small-model dataset), or
   5–10 specific books, or the classroom's own curated sources.
3. **Take a slice.** A 10–50 MB slice of a corpus — not the whole thing.

## The classroom's $200 config

```bash
# the tiny curated slice — sources first (Doombible, the favorites, the dyad,
# the AMA), then capped at N MB of everything else
python3 scripts/capture_dyad.py --lane all --slice-bytes 50 \
  --out data/train_budget.jsonl

# then QLoRA the pupil on it (the 0.5B base keeps the box tiny)
# …qlora train_quantal_classroom.py --data data/train_budget.jsonl --lora
```

Why it works here: the slice is curated-first (the Doombible, the loved
songs, the dyad's decisions and dreams — the precious few) and *then* capped
— TinyStories' lesson, applied to the constellation's own canon.

The honest split: the $200 lane gets the golden youth a first fine-tune that
fits on one consumer GPU. The full 1000h B200 run waits for the 18-council
corpus. Both are the same classroom; the budget run just takes a smaller
class.
