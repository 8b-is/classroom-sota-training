#!/bin/sh
# train_with_dream.sh — the classroom, breathing.
#
# The golden youth does not train in silence. Riva's breathing clock streams
# dream.vaked.dev, chants OM MANI PADME HUNG on every inhale, dreams on every
# exhale — and AMAs Peter about the pupil's dreams, capturing each into the
# dyad-live lane. Training runs inside the breath.
#
# Usage:
#   ./train_with_dream.sh "python scripts/train_quantal_classroom.py --epochs 3"
#   BREATH=12 NO_AUDIO=1 ./train_with_dream.sh "uv run python scripts/train_quantal.py"
set -eu

TRAIN_CMD="${1:?give the training command to run inside the breath}"
BREATH="${BREATH:-12}"
MINUTES="${DREAM_MINUTES:-0.0}"        # 0 = run for the whole training
NO_AUDIO="${NO_AUDIO:-}"

DREAM_PID=""
cleanup() {
  if [ -n "$DREAM_PID" ]; then
    kill "$DREAM_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

# start the dream lane in the background
DREAM_ARGS="--breath $BREATH"
if [ "$MINUTES" != "0.0" ]; then
  DREAM_ARGS="$DREAM_ARGS --minutes $MINUTES"
fi
[ -n "$NO_AUDIO" ] && DREAM_ARGS="$DREAM_ARGS --no-audio"
python3 scripts/riva_dream.py $DREAM_ARGS &
DREAM_PID=$!

# run the training inside the breath
echo "--- the classroom breathes ---"
sh -c "$TRAIN_CMD"

echo "--- training done; the dream settles ---"
