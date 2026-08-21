#!/bin/sh
# train_with_ama.sh — the classroom, talking.
#
# The golden youth does not only train and dream — it talks, constantly,
# in both directions. The AMA loop runs alongside training: the trainee
# asks Peter, Peter quizzes the trainee, and every exchange lands in
# data/ama_live.jsonl — part of the training corpus.
#
# Usage:
#   ./train_with_ama.sh "python scripts/train_quantal_classroom.py --epochs 3"
set -eu

TRAIN_CMD="${1:?give the training command to run alongside the AMA}"
CADENCE="${AMA_CADENCE:-20}"

AMA_PID=""
cleanup() {
  if [ -n "$AMA_PID" ]; then
    kill "$AMA_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

python3 scripts/ama_loop.py --minutes 0 --cadence "$CADENCE" --direction pupil-to-peter &
AMA_PID=$!

echo "--- the classroom talks while it trains ---"
sh -c "$TRAIN_CMD"

echo "--- training done; the conversation becomes part of it ---"
