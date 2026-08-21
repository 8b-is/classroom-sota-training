# The infrastructure — RunPod · CometAPI · the VFS

Three lanes, one universe of training.

## Training: RunPod

Managed GPU pods with **persistent volumes** — the property that matters,
because the vast.ai H100 that died mid-run took the optimizer state and the
schedule with it (two resumes diverged). RunPod's persistent volumes survive
pod termination; checkpoints, optimizer state, and the schedule ride them.
The rule, provider-independent:

- checkpoints + optimizer state + schedule go to durable storage
- resume is a first-class path, never a reload of weights alone
- the HF-bucket mount pattern (`/assets/ckpts-…`) is the shape

HF Jobs (H200, $5/h) stays a fine alternative; the 1000h B200 classroom
run wants whichever gives the strongest persistence guarantee at the price.

## Inference: CometAPI

The split:

| lane | provider | what |
|------|----------|------|
| teacher logits cache | local MLX fp8 | the KL targets — must come from the real fp8 forward |
| external council | CometAPI | 8 elders, open-weights Qwen/DeepSeek, MAX thinking |
| evaluators / judges | CometAPI | model-as-judge, benchmarking, the external calls |

Only the teachers too expensive to self-host go external; one
OpenAI-compatible endpoint, fallback across providers.

## Storage: the VFS

The missing middle box — one namespace over everything the classroom
touches:

```
hf-bucket://<bucket>/<path>     durable archives (weights, the cogito corpus)
hf://<owner>/<name>/<path>      HF repos (models, datasets, the corpus)
local://<path>                  the box's scratch
```

`scripts/vfs.py` implements the interface; every entry carries size + sha256
where declared, so the provenance layer the audit built rides on top of the
storage instead of being bolted on later. The corpus rows are already
provenance capsules; the VFS extends that to every artifact.

```
pipeline ──> [ VFS ] ──> HF buckets + HF repos (+ local scratch)
                │
                └── size + sha256 sidecar: machine-readable the whole time
```

## The lesson, restated

The saga taught it twice: the blob mismatch and the dead box were the same
bug — *the artifact a reader can actually reach was not the artifact the
metadata describes.* RunPod's persistence + the VFS's hash sidecar + the
post-push hash gate close that loop by construction, not by audit.
