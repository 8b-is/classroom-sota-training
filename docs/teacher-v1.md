# Teacher V1 — trajectory lane (Emery's guidance)

> **Emery (CometAPI), 2026-08-21:** *"For V1, I'd actually be curious to see
> Qwen3.8 Max or a strong DeepSeek reasoning model used as the teacher,
> especially for generating reasoning/tool-use trajectories rather than just
> standard SFT answers. Dataset-wise, an agentic coding + tool-calling
> dataset could be pretty interesting, especially if you mix successful
> trajectories with harder cases where the teacher has to recover from tool
> errors."*

## What this means for the classroom

1. **The V1 teacher is a reasoner, not an answerer.** Qwen3.8 Max is already
   one of the 18 council voices; the DeepSeek reasoning members (deepseek-r2,
   deepseek-v4-pro) cover the DeepSeek side. V1 teacher inference should be
   routed through CometAPI to one of those — the point is *trajectories*:
   a plan, the tool calls, the observations, then the revision.
2. **The corpus is a trajectory corpus, not an SFT answer corpus.** The
   `capture_trajectories.py` lane builds it:
   - every row is `<|trajectory|> … <|/trajectory|>` with the tool steps
   - **success** rows: the agent's plan → calls → clean finish
   - **recovery** rows (tagged `<|recovery|>`): a tool errored and the
     teacher dug itself out — the hard cases that teach repair
   - `--slice-bytes` keeps every recovery, then the best success slice
     (the $200 lane)
3. **Data sources.** `data/trajectories/*.jsonl` (the constellation's real
   agent runs — Crush/entheai/deepsiper sweeps) plus `osc9000-traces`
   (private HF) when mounted. Feed the failure cases first: the model that
   has recovered from a broken tool call learns to trust its own retries.

## The notify hook

Emery explicitly asked to be told when teacher inference starts through
CometAPI and how it performs. When the first `cometapi_teacher.py` roll call
runs, send:

- which teacher (Qwen3.8 Max / DeepSeek reasoning) produced the trajectories
- the success:recovery ratio of the emitted lane
- the CometAPI latency/throughput on the first batch

## Lane pipeline

```bash
# 1. collect agent runs into data/trajectories/
# 2. build the lane
uv run scripts/capture_trajectories.py --src data/trajectories \
    --out data/train_trajectories.jsonl
# 3. (budget) keep every recovery + a curated success slice
uv run scripts/capture_trajectories.py --src data/trajectories --slice-bytes 32
```
