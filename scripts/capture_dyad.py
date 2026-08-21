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


def load_sources(data_dir: Path) -> list[str]:
    """Curated teaching documents — the Doombible and any future sources.
    Each becomes a full-document teaching sample."""
    samples = []
    src = data_dir / "sources"
    if not src.is_dir():
        return samples
    for p in sorted(src.glob("*.md")):
        text = p.read_text(errors="ignore")
        if not text.strip():
            continue
        samples.append(f"<|source-doc|>\nsource: {p.name}\n{text.strip()}\n<|/source-doc|>")
    return samples


def load_ama(data_dir: Path) -> list[str]:
    """The constant bidirectional AMA: the trainee's questions AND Peter's,
    every exchange a teaching sample (ama_live + the dream lane's ama)."""
    samples = []
    for name in ("ama_live.jsonl", "dream_ama.jsonl"):
        p = data_dir / name
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = row.get("text")
            if text and len(text) > 40:
                samples.append(text)
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


HF_DATASETS = [
    "PeetPedro/cogitoergosumma-corpus",
    "PeetPedro/ultrawhale-dogfood",
    "PeetPedro/osc9000-traces",
]


def hf_row_to_text(row: dict) -> str | None:
    # ultrawhale dialogue
    um = row.get("user_message")
    fr = row.get("free_response")
    if isinstance(um, str) and isinstance(fr, str) and um and fr:
        return f"user: {um}\nassistant: {fr}"
    # generic text/content columns
    for k in ("text", "content", "prompt", "instruction"):
        v = row.get(k)
        if isinstance(v, str) and len(v) > 40:
            resp = row.get("response") or row.get("completion") or row.get("output")
            if isinstance(resp, str) and resp:
                return f"{v}\n\n{resp}"
            return v
    # messages-style chat
    msgs = row.get("messages")
    if isinstance(msgs, list) and msgs:
        return "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in msgs if isinstance(m, dict))
    return None


def load_hf_datasets(token: str, files_cap: int) -> list[str]:
    import urllib.error
    import urllib.request

    samples = []
    for repo in HF_DATASETS:
        try:
            req = urllib.request.Request(
                f"https://huggingface.co/api/datasets/{repo}",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                meta = json.load(resp)
        except (urllib.error.HTTPError, OSError):
            print(f"· {repo}: unreachable — skipped")
            continue
        files = [f["rfilename"] for f in meta.get("siblings", [])
                 if f["rfilename"].endswith((".jsonl", ".json")) and "/assets/" not in f["rfilename"]]
        if not files:
            print(f"· {repo}: no data files — skipped")
            continue
        print(f"· {repo}: {len(files)} files (capped at {files_cap})")
        for path in files[:files_cap]:
            try:
                url = f"https://huggingface.co/datasets/{repo}/resolve/main/{path}"
                req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
            except (urllib.error.HTTPError, OSError) as e:
                print(f"  · {path}: {e} — skipped")
                continue
            added = 0
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                text = hf_row_to_text(row)
                if text and len(text) >= 40:
                    samples.append(f"<|hf-corpus|>\nsource: {repo}/{path}\n{text}\n<|/hf-corpus|>")
                    added += 1
                if added >= 200:
                    break  # cap rows per file — the box raises this
            if added:
                print(f"  · {path}: {added} samples")
    return samples


def main() -> int:
    ap = argparse.ArgumentParser(description="capture the dyad and the constellation as classroom corpus")
    ap.add_argument("--lane", choices=["dyad", "constellation", "hf", "all"], default="all")
    ap.add_argument("--logs", default="../.remember/logs", help="the memory-log dir")
    ap.add_argument("--raw", nargs="*", default=[], help="raw session exports (jsonl/md)")
    ap.add_argument("--out", default="data/train_ultra_corpus.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-samples", type=int, default=0, help="0 = all")
    ap.add_argument("--slice-bytes", type=int, default=0,
                    help="the $200 lane: emit only a tiny curated slice (~N MB), "
                         "TinyStories-style — sources + dyad first, then a capped slice")
    args = ap.parse_args()

    samples = []
    if args.lane in ("dyad", "all"):
        logs_dir = Path(args.logs).resolve()
        if logs_dir.is_dir():
            samples += load_memory_logs(logs_dir)
        samples += load_raw_sessions(args.raw)
        data_dir = Path(args.out).parent if args.out else Path("data")
        samples += load_ama(data_dir)
        samples += load_sources(data_dir)
    if args.lane in ("constellation", "all"):
        samples += load_constellation()
    if args.lane in ("hf", "all"):
        token = os.environ.get("HF_TOKEN")
        if token:
            samples += load_hf_datasets(token, int(os.environ.get("HF_FILES_CAP", "20")))
        else:
            print("· HF_TOKEN not set — hf lane skipped")
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

    if args.slice_bytes > 0:
        # the $200 lane: curated first (sources, dyad, dreams), then a capped slice
        budget = args.slice_bytes * 1024 * 1024
        curated = [s for s in uniq if any(k in s for k in ("<|source-doc|>", "<|dyad-teaching|>", "<|ama-pupil|>", "<|ama-teacher|>"))]
        rest = [s for s in uniq if s not in curated]
        picked, size = list(curated), sum(len(s) for s in curated)
        for s in rest:
            if size + len(s) > budget:
                break
            picked.append(s)
            size += len(s)
        uniq = picked

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for s in uniq:
            f.write(json.dumps({"text": s}) + "\n")
    print(f"corpus ({args.lane}): {len(uniq)} samples → {args.out}")
    print(f"  total bytes: {sum(len(s) for s in uniq)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
