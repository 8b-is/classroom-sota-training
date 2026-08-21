# CometAPI — the external teacher lane

The Council of Elders has two lanes:

- **Self-hosted (MLX fp8)** — the open-weights teachers on the box
  (`teacher_logits.py`, `train_quantal_*.py`). No API cost; the fp8 logits
  are the KL targets.
- **External (CometAPI)** — the teachers that are too expensive to self-host
  and too valuable to skip: hosted Qwen (3 / 3.5 / 3.8 Max) and DeepSeek
  (R1 / Reasoner / Pro) in pure MAX-thinking mode. One OpenAI-compatible
  endpoint, 500+ models, fallback across providers.

## Why

- **tok/s per classroom teacher model** — the calls to individual teacher
  models are *not* a lot: more than free-tier OpenRouter allows, but less
  than a single coding session. CometAPI sits exactly there.
- **Cost** — model API costs cut by ≥20%; the redeem-credit trial lets us
  compare cost, latency, and output quality in our own setup.
- **No closed-weight "frontiers"** — the external teachers are still open
  weights (Qwen, DeepSeek), run at MAX thinking.

## The provider

`scripts/cometapi_teacher.py` — stdlib-only OpenAI-compatible client.

```bash
export COMETAPI_API_KEY=...
python scripts/cometapi_teacher.py --teacher qwen3.8-max --prompt "..."
python scripts/cometapi_teacher.py --teacher deepseek-r1 --file prompt.txt -n 3
```

The teacher table (`TEACHERS` in the script) maps a short id to the model
name and whether it uses thinking mode.

## The credits

- Redeem code: `b4348463150a47fba514bc81a14ad93c` (Emery, CometAPI — Aug 2026).
- The planned comparison: run the same small classroom teacher workload
  through Qwen3.8-Max and DeepSeek-Reasoner and compare output quality and
  cost against the self-hosted lane.

## Cards

`scripts/add_cometapi_card.py` adds the agreed infrastructure block to HF
model/dataset cards (idempotent, via `huggingface_hub`). Run with `--all-core`
to patch the core teacher set, or pass repo ids explicitly. Every new model
or dataset born from this work carries the block.

## Where it lands

- `scripts/cometapi_teacher.py` — the external teacher client.
- `scripts/add_cometapi_card.py` — the card block.
- HF cards: qwen2.5-coder-32b-heretic-swe-sft · gpt-oss-120b-heretic ·
  Qwen3-30B-A3B-Agentic-ToolCaller · anonymus-1bit-gpt · kompress-v17 ·
  unit · ultrawhale-dogfood.
