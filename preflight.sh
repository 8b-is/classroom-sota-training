#!/bin/sh
# preflight.sh — the classroom's gate before a training run.
#
# Checks everything the run needs: tokens, tools, the corpus, the teacher
# cache, the lanes. Exits non-zero with a list of what's missing, so the
# run never starts blind. Run it on the box, on the Mac, before anything.
#
# Usage:
#   ./preflight.sh
set -eu

fail=0
ok()   { echo "  ok   $1"; }
bad()  { echo "  MISS $1"; fail=1; }

echo "── preflight: the classroom before the run ──"

echo "tools"
command -v python3 >/dev/null && ok "python3" || bad "python3"
command -v uv >/dev/null && ok "uv (python via uv)" || bad "uv"
command -v git >/dev/null && ok "git" || bad "git"

echo "tokens"
[ -n "${HF_TOKEN:-}" ] && ok "HF_TOKEN" || bad "HF_TOKEN (huggingface write)"
[ -n "${COMETAPI_API_KEY:-}" ] && ok "COMETAPI_API_KEY" || bad "COMETAPI_API_KEY (the external council)"

echo "scripts (syntax)"
for s in scripts/teacher_logits.py scripts/train_quantal_classroom.py \
         scripts/capture_dyad.py scripts/cometapi_teacher.py scripts/riva_dream.py \
         scripts/ama_loop.py scripts/vfs.py; do
  [ -f "$s" ] && python3 -c "import ast; ast.parse(open('$s').read())" 2>/dev/null \
    && ok "$s" || bad "$s (missing or syntax)"
done

echo "the corpus"
for c in data/train_ultra_corpus.jsonl data/train_constellation.jsonl \
         data/train_hf_corpus.jsonl data/train_dyad_live.jsonl; do
  if [ -f "$c" ]; then
    n=$(wc -l < "$c" | tr -d ' ')
    ok "$c ($n samples)"
  else
    bad "$c (rebuild with scripts/capture_dyad.py --lane all)"
  fi
done

echo "the teacher-logits cache"
if [ -d data/teacher_logits ] && [ -f data/teacher_logits/manifest.json ]; then
  ok "data/teacher_logits/ (manifest present)"
else
  bad "data/teacher_logits/ — run scripts/teacher_logits.py on the fp8 box first"
fi

echo "the lanes"
[ -f scripts/riva_dream.py ] && ok "dream lane" || bad "dream lane"
[ -f scripts/ama_loop.py ] && ok "bidirectional AMA" || bad "bidirectional AMA"
command -v curl >/dev/null && ok "curl (status hook)" || bad "curl"

echo "disk"
free=$(df -k . | tail -1 | awk '{print $4}')
if [ "${free:-0}" -gt 8388608 ]; then
  ok "≥8 GB free ($((free/1048576)) GB)"
else
  bad "need ≥8 GB free (have ${free:-0} KB)"
fi

echo ""
if [ "$fail" -eq 0 ]; then
  echo "preflight PASSED — the classroom is ready to run."
  echo "next:  ./run_training.sh  (see docs/RUNBOOK.md for the full sequence)"
else
  echo "preflight BLOCKED — fix the MISS items above, then re-run."
  exit 1
fi
