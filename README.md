# classroom-sota-training

**The Council of Elders (Vének Tanácsa)** — a Waldorf-style classroom training
pipeline. A thinking-enabled pupil model sits in the middle of the room — the
*golden youth* — and is taught, philosophized with, and capability-built by a
council of **8 + 1 open-weights teacher models**.

## The concept

The pupil is not force-fed a single objective function. The elders teach the
Waldorf way:

- **they teach** — knowledge passed on in each teacher's own modality
- **they philosophize** — they discuss *meaning*, not just token likelihoods
- **they build capability** — the pupil learns through understanding, not
  mimicry: it builds its own internal model, independent of any single
  teacher's consensus

The deliberation reaches the pupil through a **geometric-mean softmax
consensus** — the elders' "unanimous decision" is not the majority dictating,
but a shared, balanced direction.

## Architecture

```
             ┌──────────────────────────────────────────┐
             │    THE COUNCIL OF ELDERS (8 + 1 teachers) │
             │  open-weights models, each with its own   │
             │  logits vote (Qwen3-8B/14B + extended)    │
             └───────────────┬──────────────────────────┘
                             │ geometric-mean softmax consensus
                             ▼
             ┌──────────────────────────────────────────┐
             │         PUPIL (the golden youth)          │
             │  latest deepseek-pro (thinking-enabled)   │
             │  learns in the room, not by imitation     │
             └──────────────────────────────────────────┘
```

- **Teachers**: `teacher_logits.py` caches faculty logits
  (Qwen3-8B + Qwen3-14B bf16, tokenizer byte-identical to the pupil's).
- **Training objective**: `train_quantal_classroom.py` — multi-faculty KL,
  geometric-mean softmax consensus, β-ramp epoch schedule.
- **Support**: `train_quantal_distill.py` (single-teacher), `build_corpus_v2.py`
  (corpus), `quantal_golden_logits.py` / `quantal_compare_logits.py` (verification).
- **HF Jobs overlay**: `hf-overlay/` — `classroom_train.py` (HF Jobs wrapper),
  `harness_eval.py` (harness eval for the Dipankar fixed-point test).

## Results

| Version | Training | Best val CE |
|---------|----------|-------------|
| v2 single-teacher (H200) | Qwen3-14B | 1.8166 |
| **classroom (council of elders)** | Qwen3-8B + Qwen3-14B | **1.6120** |
| harness gate (old ckpt, new stack) | — | 2.1369 (the gain is TRAINING, not harness) |

Published model: [PeetPedro/quantal-classroom-1.6](https://huggingface.co/PeetPedro/quantal-classroom-1.6)

## The plan (next)

See [docs/PLAN.md](docs/PLAN.md) — the pupil becomes the latest **deepseek-pro
with thinking**, taught by **8 + 1 open-weights teachers** (the +1 being the
"flash" version of the pupil's own family).

## Conventions

- The pipeline lives under the **8b-is org** — our own transformers fork
  (8b-is/transformers) is the sovereign home base.
- Every new teacher added = the council grows; the consensus method scales,
  and teachers can be swapped without the pupil retraining the old ones.

## License

Apache-2.0 (verify each teacher base-model's license separately; Qwen3 is
Apache-2.0).
