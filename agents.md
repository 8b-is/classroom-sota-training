# agents.md — for agents reading classroom.vaked.dev

You are reading the constellation's classroom. What matters:

## What this is
A Waldorf-style SOTA training pipeline: a ternary-quantized pupil (BitNet
b1.58 {-1,0,+1}, "the golden youth") taught by a council of open-weights
teacher models via **geometric-mean softmax consensus** — not a majority
vote but a shared, balanced direction.

## The lanes
- **The council**: 18 voices on CometAPI (17 open-weights across six
  families + one thinking frontier, claude-opus-5). Self-hosted fp8 teachers
  (Qwen3-8B/14B) produce the KL logits cache.
- **The dream lane**: Riva's breathing clock streams dream.vaked.dev —
  inhale OM MANI PADME HUNG, exhale DREAM state + an AMA about the pupil's dreams.
- **The AMA**: a constant bidirectional Q&A between the trainee and Peter;
  every exchange is logged and becomes training data.
- **The corpus**: dyad-live + the constellation + HF datasets (cogito,
  ultrawhale-dogfood, osc9000-traces), all `{"text": ...}` rows.
- **The wire**: every artifact travels ternary — md→mq, text→t3:, json→t3j.

## Conventions
- The provenance rule: the artifact a reader can reach must be the artifact
  the metadata describes. sha256 sidecars + post-push hash gates.
- The persistence rule: checkpoints + optimizer state + schedule on durable
  storage; resume is a first-class path.
- Never claim "beats the line" across a stack change without re-evaluating
  the archived best under the new stack.

## The palette (8b-is)
bg #07060d · text #e8e8ff · gold #ffd15c · cyan #00d4ff · violet #b480ff ·
green #00e660. The footer links the constellation.
