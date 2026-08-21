#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
capture_trajectories.py — Emery's V1 lane: agentic tool-calling trajectories.

The teacher (V1: Qwen3.8 Max or a strong DeepSeek reasoning model) should be
trained on *trajectories*, not just SFT answers: a plan, the tool calls, the
observations, and the recovery when a tool fails. This lane builds that
corpus.

Each local trajectory file is JSONL: one row per turn/trajectory, with
optional `steps` and `error` fields. The lane:

  - classifies every trajectory as `success` (no tool error) or `recovery`
    (a tool errored and the agent retried or repaired after it)
  - wraps each in <|trajectory|> … <|/trajectory|> with a <|recovery|> tag
    when the teacher had to dig itself out of a tool failure
  - mixes the two so the harder cases (recovery) are always present

Usage:
  python scripts/capture_trajectories.py \
      --src data/trajectories --out data/train_trajectories.jsonl
  python scripts/capture_trajectories.py --src ... --slice-bytes 32
      (the $200 lane: emit only a tiny curated slice, ~N MB)
"""

import argparse
import json
from pathlib import Path


def is_recovery(row) -> bool:
    """Recovery = a tool errored AND the agent continued (a later step
    exists). A turn that fails and ends is failure, not recovery."""
    if isinstance(row, dict) and isinstance(row.get("steps"), list):
        steps = row["steps"]
        for i, s in enumerate(steps):
            if s.get("error") or "error" in str(s.get("output", "")).lower():
                return i + 1 < len(steps)
        return False
    # text fallback: an error marker plus a continuation marker
    text = str(row).lower()
    has_error = "tool_error" in text or '"error":' in text or "error:" in text
    has_retry = "retry" in text or "then" in text
    return has_error and has_retry


def load_file(p: Path) -> list[tuple[str, bool]]:
    samples = []
    for line in p.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            if "steps" in row:
                parts = []
                for s in row["steps"]:
                    tool = s.get("tool", "")
                    inp = s.get("input", "")
                    out = s.get("output", "")
                    err = s.get("error")
                    parts.append(f"[{tool}] in: {inp} out: {out or err or ''}")
                text = "\n".join(parts)
            else:
                text = row.get("text") or row.get("trajectory") or row.get("prompt")
            if text:
                samples.append((str(text), is_recovery(row)))
        elif isinstance(row, str):
            samples.append((row, is_recovery(row)))
    return samples


def build(src: Path) -> list[tuple[str, bool]]:
    if not src.is_dir():
        return []
    samples = []
    for p in sorted(src.glob("*.jsonl")):
        samples.extend(load_file(p))
    return samples


def render(samples: list[tuple[str, bool]], slice_bytes: int | None) -> tuple[list[str], dict]:
    successes, recoveries = [], []
    for text, rec in samples:
        tag = "<|recovery|>\n" if rec else ""
        wrapped = f"<|trajectory|>\n{tag}{text}\n<|/trajectory|>"
        (recoveries if rec else successes).append(wrapped)

    emitted = successes + recoveries
    if slice_bytes:
        # the $200 lane: keep every recovery, then a curated slice of success
        out, budget = [], slice_bytes
        for s in recoveries:
            if budget <= 0:
                break
            out.append(s)
            budget -= len(s.encode())
        for s in successes:
            if budget <= 0:
                break
            out.append(s)
            budget -= len(s.encode())
        emitted = out

    return emitted, {"success": len(successes), "recovery": len(recoveries)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=Path("data/trajectories"))
    ap.add_argument("--out", type=Path, default=Path("data/train_trajectories.jsonl"))
    ap.add_argument("--slice-bytes", type=int, help="BUDGET-200: emit only a tiny curated slice")
    args = ap.parse_args()

    samples = build(args.src)
    emitted, stats = render(samples, args.slice_bytes)
    if not emitted:
        print(f"no trajectories under {args.src} — add data/trajectories/*.jsonl")
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for s in emitted:
            f.write(json.dumps({"text": s}) + "\n")

    print(f"{len(emitted)} trajectories -> {args.out} "
          f"(success {stats['success']}, recovery {stats['recovery']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
