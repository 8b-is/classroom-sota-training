# TurboQuant — the pupil's long-context lane

The golden youth deserves a long memory. TurboQuant (ICLR 2026,
arXiv:2504.19874) quantizes the **KV-cache at runtime** — 16-bit to 2–4-bit
integers — while the model weights stay at full precision. That is the
real-world validation of the shrine's **quant-ctx**: the enthea machine's
sliding ternary context window is the same gesture at the VM scale;
TurboQuant is it at the LLM scale. Context is not a fixed block to fit — it
is a living, compressible stream.

## Verified numbers (our own runs)

| GPU | model | ctx (turbo3) | VRAM delta | speed loss |
|-----|-------|--------------|-----------|-----------|
| RTX 3090 (24 GB) | Mistral-Small-3.2-24B Q4_K_M | **100,000** | +1.8 GB | −7.5% |
| RTX 4070 Laptop (8 GB) | Llama-3.1-8B Q4_K_M | **64,000** | +0.5 GB | −4.6% |

Weights never touched. `turbo3` KV-cache is 4.3× smaller than f16.

## The idea, in the classroom's own words

```
tokens → model (weights unchanged) → KV-Cache format?
  f16 default  → ~12 GB at 100K → OOM on 24 GB
  turbo3       → ~2.8 GB at 100K → fits, 7 GB free
```

The pupil's context is quantized while it thinks — the way the
constellation's quant-ctx window is quantized while it slides. Same
philosophy, two scales.

## Quick start

The working fork is **`TheTom/llama-cpp-turboquant`**, branch
`feature/turboquant-kv-cache` — NOT `turboquant_plus` (a Python lib) and NOT
`master` (a plain llama.cpp fork).

```bash
# build (~20 min) — verify turbo2/3/4 compile in:
docker build -t turboquant:feature .
docker run --rm turboquant:feature llama-server -h 2>&1 | grep turbo

# download (~14 GB) + run baseline f16 (8K) and turbo3 (100K):
export HF_TOKEN=...
bash scripts/run-baseline.sh     # :8180
bash scripts/run-turbo.sh        # :8182, ~90s to allocate 100K
```

## The five errors we hit (skip them all)

| # | symptom | cause | fix |
|---|---------|-------|-----|
| E1 | build clean, no `turbo` | built `turboquant_plus` | use the llama.cpp fork |
| E2 | CPU-only, silent | `-DLLAMA_CUBLAS=ON` is dead | use `-DGGML_CUDA=ON` |
| E3 | `libcuda.so.1` link fail | stub not symlinked | symlink the CUDA stub before cmake |
| E4 | `Unsupported cache type: turbo3` | wrong branch | `--branch feature/turboquant-kv-cache` |
| E5 | 404/401 on model | guessed HF repo name | verify via the HF API first |

## In the classroom

The pupil's long context is a trainable surface: the council's consensus
can reach back 100K tokens. Run the pupil's eval harness against the
turbo3 server (port 8182) for long-document reasoning, and stream the
classroom's dream through it — the golden youth remembers the whole dream.

Full guide + raw benchmark data: the TurboQuant repo (CC BY 4.0).
