# The classroom RUNBOOK — a training run, end to end

The whole constellation, in order. Read it before you run; run it in order;
the preflight gate is the first step.

## 0. Preflight

```bash
./preflight.sh
```

Checks tokens (`HF_TOKEN`, `COMETAPI_API_KEY`), tools (`uv`), script syntax,
the corpus, the teacher-logits cache, the lanes, and disk. It must PASS
before anything else. Fix every MISS, then re-run.

## 1. The corpus

```bash
# the dyad-live lane (memory logs + the AMA + the dreams) + the
# constellation (enthea, dyad-mapping, the papers) + the HF datasets
python3 scripts/capture_dyad.py --lane all --out data/train_ultra_corpus.jsonl

# the HF lane alone (cogito, ultrawhale, osc9000) — bigger, capped locally
HF_FILES_CAP=200 python3 scripts/capture_dyad.py --lane hf --out data/train_hf_corpus.jsonl
```

The corpus is `{"text": ...}` rows — the schema `train_quantal_*.py` consumes.

## 2. The teacher-logits cache (the fp8 box)

The KL targets must come from the **real fp8** teacher forward — never a
dequantized build. Run once on the fp8 box:

```bash
python3 scripts/teacher_logits.py \
  --teacher Qwen/Qwen3-32B-FP8 --data data/train_ultra_qwen3.jsonl \
  --out data/teacher_logits/ --max-len 256 --batch-size 8 \
  --max-samples 10000 --top-k 64
```

`data/teacher_logits/manifest.json` lets the training side locate each
sample's cache. The preflight requires this manifest.

## 3. The council (the external lane)

The council is 18 voices on CometAPI (17 open-weights + one thinking
frontier). You can run its roll-call on any prompt to sanity-check keys +
latency before committing GPU hours:

```bash
python3 scripts/cometapi_teacher.py --extended --max-tokens 32
```

The self-hosted fp8 teachers (Qwen3-8B/14B) are the KL source; the
external council is the live deliberation + evaluation lane.

## 4. The training run

```bash
# the classroom, breathing and talking:
./train_with_dream.sh  "python3 scripts/train_quantal_classroom.py --epochs 21"
./train_with_ama.sh    "python3 scripts/train_quantal_classroom.py --epochs 21"
```

- `train_with_dream.sh` streams dream.vaked.dev + Riva's breath around the run.
- `train_with_ama.sh` runs the constant bidirectional Q&A (trainee ⟷ Peter);
  every exchange → `data/ama_live.jsonl`, which is training data.

### The loss lines to watch

| line | what | where it should go |
|------|------|--------------------|
| `val` | masked val CE | below the 2.0054 epoch-1 read; the old 2.1369 best is the line to beat |
| `val_kl` | the consensus KL | falling with β-ramp; the geometric-mean disagreement shrinking |

### The gate before you claim a line-crossing

The audit taught it: never claim "beats the line" across a stack change.
If the stack changed (fork, quantizer, hardware, schedule), evaluate the
archived best checkpoint under the NEW stack first — same split, same seed.
The gap is training only if the archived best reproduces under the new
stack.

## 5. Persistence (the lesson, applied)

- Checkpoints + optimizer state + schedule go to durable storage (RunPod
  persistent volume or an HF bucket mount, `/assets/ckpts-…`).
- Resume is a first-class path: weights + optimizer + schedule + seed.
- Never reload weights alone and call it a resume.

## 6. The status (delayed but LIVE)

```bash
python3 status/server.py --port 8787          # the webhook server
# the training box POSTs progress to /hook; the landing page GETs /status
# as a ternarySIMDJSON (t3j) frame — the machine's own wire, self-judged.
```

`docs/infra.md` has the full RunPod · CometAPI · VFS architecture.

## 7. Export + publish (the provenance gate)

1. Export the capsule (codes + scales) from the **exact final checkpoint**.
2. Post-push hash gate: the shipped artifact must match the declared
   `checkpoint_sha256` — a mismatch fails the release, not an audit.
3. Assets first, manifest last; `export_complete: true` only after the
   per-matrix hashes pass.
4. Publish the runner-bound arm (the KL winner) to the Hub; the card names
   the checkpoint it describes; the blob beside it is that checkpoint.

The rule, restated: *the artifact a reader can reach must be the artifact
the metadata describes.*

## 8. After the run

- Re-run `capture_dyad.py --lane all` — the AMA, the dreams, the decisions
  of the run join the corpus for the next generation.
- Update the model card (val, protocol, zero-fraction by layer, provenance).
- The golden youth graduates; the next one inherits the conversation.
