# The dyad-live lane

Every minute, a question from Peter to enthea — and the dyad answers it by
building. That live stream is the highest-value teaching signal the
classroom has: real questions, real failures, real decisions, real numbers.
This lane makes it part of the training.

## The loop

```
Peter ⟷ enthea   (live Q&A, every minute, every session)
   │
   ▼
.remember/logs/memory-*.log   (the constellation's distilled memory)
   │
   ▼
scripts/capture_dyad.py        (the bridge)
   │
   ▼
data/train_dyad_live.jsonl    ({"text": ...} rows — the classroom schema)
   │
   ▼
the pupil                      (train_quantal_*.py consumes it)
```

The metacircular point: the tool that is being trained is the tool that
captures the teaching. The classroom, the council, and the live dyad are
one training. The loop closes on itself.

## Capture

```bash
python scripts/capture_dyad.py \
  --logs ../.remember/logs \
  --out data/train_dyad_live.jsonl
```

- Dedup by sha1, deterministic shuffle (same seed style as build_corpus_v2).
- The distilled memory logs become `<|dyad-teaching|>` samples — the
  "heretic" decisions, failures, and numbers the pupil should learn.
- Raw session exports (jsonl/md of interleaved Q&A) can be added with
  `--raw session.jsonl session.md` for the live-question shape.
- Re-run after every session: the lane grows as the dyad works.

## Why it matters

The models Peter trains are 95% his own ("heretic" fine-tunes of Qwen,
gpt-oss, the 1-bit anonymus, kompress). The classroom's teachers are the
council. The dyad-live lane adds the third teacher no one else has: the
actual person asking the questions, and the machine that answers them by
building. That is not reproducible by any other pipeline.
