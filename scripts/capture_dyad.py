#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
capture_dyad.py — the live-dyad lane of the classroom.

Every minute, a question from Peter to enthea — and the dyad answers it by
building. That stream is the highest-value teaching signal the classroom
has: real questions, real failures, real decisions, real numbers. This
script turns it into a corpus. The constellation itself is the second lane:
the shrine, the specs, the voices, the papers.

Lanes:
  --lane dyad          the live-dyad memory logs (+ raw session exports)
  --lane constellation the constellation's teaching artifacts
  --lane all           both

Inputs:
  - dyad: .remember/logs/memory-*.log (REQUIRED for the dyad lane), plus
    raw session exports (jsonl/md, optional).
  - constellation: enthea (shrine/specs/voices), 8b-public-documents
    (papers/dyad-mapping), projects-wiki (the Obsidian vault).

Output: data/train_<lane>_live.jsonl with {"text": ...} rows — the exact
schema train_quantal_long.py / train_quantal_distill.py consume.

Usage:
  python scripts/capture_dyad.py --lane all --out data/train_ultra_corpus.jsonl
  python scripts/capture_dyad.py --lane constellation --out data/train_constellation.jsonl
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


def load_constellation() -> list[str]:
    samples = []
    here = Path(__file__).resolve().parent.parent  # the classroom repo root
    # the constellation's teaching roots: enthea (the whole engine door),
    # the dyad-mapping corpus, the public documents, and the wiki (opt-in).
    roots = {
        "enthea": here.parent / "enthea",
        "dyad-mapping": here.parent / "8b-public-documents" / "dyad-mapping",
        "public-docs": here.parent / "8b-public-documents",
        "wiki": Path(os.environ.get("PROJECTS_WIKI", str(here.parent / "projects-wiki"))),
    }
    max_per_root = int(os.environ.get("CONSTELLATION_CAP", "400"))
    for name, root in roots.items():
        if not root.exists():
            continue
        if name == "wiki" and not os.environ.get("CONSTELLATION_WIKI"):
            continue  # the Obsidian vault is iCloud-backed and huge — opt in
        if root.is_file():
            paths = [root]
        else:
            paths = list(root.rglob("*.md"))
        for p in sorted(paths)[:max_per_root]:
            if any(seg.startswith(".") or seg in ("node_modules", "backups", "_cold-archive", "dist", "target") for seg in p.parts):
                continue
            try:
                text = p.read_text()
            except OSError:
                continue
            if not text.strip():
                continue
            if len(text) < 200:
                continue  # skip stubs
            samples.append(
                f"<|constellation|>\n"
                f"source: {name}/{p.name}\n"
                f"{text.strip()}\n"
                f"<|/constellation|>"
            )
    return samples


def main() -> int:
    ap = argparse.ArgumentParser(description="capture the dyad and the constellation as classroom corpus")
    ap.add_argument("--lane", choices=["dyad", "constellation", "all"], default="all")
    ap.add_argument("--logs", default="../.remember/logs", help="the memory-log dir")
    ap.add_argument("--raw", nargs="*", default=[], help="raw session exports (jsonl/md)")
    ap.add_argument("--out", default="data/train_ultra_corpus.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-samples", type=int, default=0, help="0 = all")
    args = ap.parse_args()

    samples = []
    if args.lane in ("dyad", "all"):
        logs_dir = Path(args.logs).resolve()
        if logs_dir.is_dir():
            samples += load_memory_logs(logs_dir)
        samples += load_raw_sessions(args.raw)
    if args.lane in ("constellation", "all"):
        samples += load_constellation()
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
    print(f"corpus ({args.lane}): {len(uniq)} samples → {args.out}")
    print(f"  total bytes: {sum(len(s) for s in uniq)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
