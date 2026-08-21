#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
capture_dyad.py — the live-dyad lane of the classroom.

Every minute, a question from Peter to enthea — and the dyad answers it by
building. That stream is the highest-value teaching signal the classroom
has: real questions, real failures, real decisions, real numbers. This
script turns it into a corpus.

Inputs:
  - .remember/logs/memory-*.log — the distilled dyad stream (already the
    constellation's cross-session memory). REQUIRED.
  - raw session exports (jsonl/md, optional) — interleaved Q&A captured
    live. Each becomes a user/assistant sample.

Output: data/train_dyad_live.jsonl with {"text": ...} rows — the exact
schema train_quantal_long.py / train_quantal_distill.py consume.

Usage:
  python scripts/capture_dyad.py \
    --logs ../../.remember/logs \
    --out data/train_dyad_live.jsonl
"""

import argparse
import hashlib
import json
import os
import random
import sys
from pathlib import Path


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def load_memory_logs(logs_dir: Path) -> list[str]:
    samples = []
    for path in sorted(logs_dir.glob("memory-*.log")):
        text = path.read_text()
        if not text.strip():
            continue
        samples.append(
            f"<|dyad-teaching|>\n"
            f"source: {path.name}\n"
            f"{text.strip()}\n"
            f"<|/dyad-teaching|>"
        )
    return samples


def load_raw_sessions(paths: list[str]) -> list[str]:
    samples = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        if path.suffix == ".jsonl":
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = row.get("text") or row.get("content")
                if text:
                    samples.append(text)
        else:
            text = path.read_text()
            if text.strip():
                samples.append(text)
    return samples


def main() -> int:
    ap = argparse.ArgumentParser(description="capture the live dyad as classroom corpus")
    ap.add_argument("--logs", default="../.remember/logs", help="the memory-log dir")
    ap.add_argument("--raw", nargs="*", default=[], help="raw session exports (jsonl/md)")
    ap.add_argument("--out", default="data/train_dyad_live.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-samples", type=int, default=0, help="0 = all")
    args = ap.parse_args()

    logs_dir = Path(args.logs).resolve()
    if not logs_dir.is_dir():
        sys.exit(f"memory-log dir not found: {logs_dir}")

    samples = load_memory_logs(logs_dir) + load_raw_sessions(args.raw)
    if not samples:
        sys.exit("no samples captured — nothing to train on")

    # dedup by content, deterministic shuffle (same seed style as the corpus)
    seen = set()
    uniq = []
    for s in samples:
        h = sha1(s)
        if h in seen:
            continue
        seen.add(h)
        uniq.append(s)
    random.Random(args.seed).shuffle(uniq)
    if args.max_samples:
        uniq = uniq[: args.max_samples]

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for s in uniq:
            f.write(json.dumps({"text": s}) + "\n")
    print(f"dyad-live: {len(uniq)} samples → {args.out}")
    print(f"  total bytes: {sum(len(s) for s in uniq)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
