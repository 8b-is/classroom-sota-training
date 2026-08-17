# THE PLAN — deepseek-pro thinking pupil × 8+1 open-weights elders

The classroom grows up. The pupil is no longer the 1.7B quantal student — it
becomes the latest **deepseek-pro with thinking enabled**, sitting at the
center of the room as the golden youth, taught by a council of **8 + 1
open-weights teacher models**.

> The +1 is *itself* — the "flash" version of the pupil's own family, present
> at the table so the council always includes the voice of the pupil's lineage.

## Pupil

- **Model**: latest deepseek-pro, thinking enabled (reasoning before answer).
- **Why**: a pupil that can *think* learns differently from one that only
  imitates — the Waldorf ideal: capability built through understanding, not
  mimicry.
- Training: classroom objective (multi-faculty KL, geometric-mean softmax
  consensus over the elders' logits) applied to the pupil's own weights.

## Council of Elders (8 + 1)

Open-weights teachers, each casting a logits vote; consensus via
geometric-mean softmax (β-ramp). The +1 teacher is the pupil's own "flash"
variant — cheap, fast, and always present.

| Slot | Teacher (open weights) | Role at the table |
|------|------------------------|-------------------|
| 1    | Qwen3-8B               | generalist elder |
| 2    | Qwen3-14B              | generalist elder (proven in classroom-1.6) |
| 3    | Qwen3-30B-A3B-ToolCaller | tool-use / agentic elder |
| 4    | Qwen2.5-Coder-32B      | code elder |
| 5    | gpt-oss-120b (MXFP4)   | large-MoE elder (broad knowledge) |
| 6    | Nemotron-3-super-120b  | large-MoE elder (reasoning) |
| 7    | TBD (open SOTA teacher) | to be selected — security/guardrail specialist |
| 8    | TBD (open SOTA teacher) | to be selected — philosophy/dialogue specialist |
| +1   | deepseek "flash"       | the pupil's own lineage voice |

## Milestones

1. **Teacher logits cache** — extend `teacher_logits.py` to all 9 teachers
   (tokenizer must stay byte-identical with the pupil's; logits cached to
   bucket/disk).
2. **Pupil swap** — replace the 1.7B quantal student with deepseek-pro
   (thinking). Adapt `train_quantal_classroom.py` for the new pupil arch.
3. **Consensus tuning** — verify geometric-mean consensus over 9 votes
   (β-ramp, outlier-robustness: one bad teacher must not skew the council).
4. **Harness gate** — run the Dipankar fixed-point harness on the new pupil
   to prove gains are training, not eval drift.
5. **Eval + publish** — best-val checkpoint → model card + dataset → HF.

## Open questions

- Which two TBD teachers fill slots 7-8? (security + dialogue specialists)
- Does deepseek-pro licensing allow distillation? (verify before caching
  logits — if not, swap for an Apache-2.0 thinking model with identical
  tokenizer family.)
- Where does the pupil run? (GCP Agent Platform per lib-2 research, or HF
  Jobs H200 — TBD once teachers are cached.)
