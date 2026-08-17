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

## Resolved questions (research done 2026-08-17)

- **deepseek-pro licensing — MIT, distillation allowed ✓**. "deepseek-pro" is
  **DeepSeek-V4-Pro** (1.6T/49B MoE, MIT, not gated). The V4-Flash is its
  "flash" sibling (284B/13B, MIT). No distillation clause, no branding/MAU
  strings — the only duty is keeping the copyright notice.
- **Real blocker is the tokenizer, not the license**: DeepSeek BPE vocab
  129,280 vs Qwen3 151,936 vs Qwen3.5 248,320. If the pupil is V4-Pro, the
  Qwen-family teachers are NOT byte-identical → token-level multi-faculty KL
  won't compose directly. Options: (1) sequence/embedding-level cross-tokenizer
  KL, (2) V4-Pro-generated thinking trajectories → SFT on the pupil (the
  proven community pattern), (3) all-DeepSeek teacher council.
- **Slot 7 (security/guardrail) → `Qwen/Qwen3Guard-Gen-8B`** — Apache-2.0,
  not gated, generative guardrail, **Qwen3 tokenizer (byte-identical to a
  Qwen pupil)**. Backups: nvidia Llama-3.1-Nemotron-Safety-Guard-8B-v3 (but
  Llama tokenizer), allenai/wildguard (older). Avoid Llama-Guard-4 (manual
  gated, "Built with Llama" + MAU clause) and ShieldGemma (gated).
- **Slot 8 (philosophy/dialogue) → `Qwen/Qwen3-32B`** — Apache-2.0, not
  gated, Qwen3 tokenizer, 131K YaRN, strong creative/multi-turn dialogue.
  For stronger reasoning: `Qwen3-235B-A22B` (same tokenizer).
- **+1 (pupil's flash voice)**: a small Qwen3 of the pupil's own family
  (e.g. Qwen3-4B) — Apache-2.0.

## Open questions

- **Council composition vs tokenizer**: if the pupil is V4-Pro (DeepSeek
  tokenizer), do we (a) keep Qwen teachers + cross-tokenizer KL / trajectory
  SFT, or (b) rebalance the council to DeepSeek-family teachers? — needs a
  decision before milestone 1.
- Where does the pupil run? (GCP Agent Platform per lib-2 research, or HF
  Jobs H200 — TBD once teachers are cached.)
