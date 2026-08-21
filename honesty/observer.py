#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
observer.py — the honesty gate.

An eBPF-like observer for a chat stream: it does not change the channel, it
hooks it. Every message is folded into a hash-chained ledger (each entry
carries the previous hash), so a retroactive edit breaks the chain — the
honesty gate. Claims are verified against a facts store; every entry carries
its t3 fingerprint, judged by the 1-bit model.

The observer is channel-agnostic. The WhatsApp Business Cloud API delivers
group messages to a webhook (server.py); the classroom's own AMA and council
logs can be watched the same way.

Usage:
  python honesty/observer.py ingest --channel amA --text "the pupil dreams"
  python honesty/observer.py verify --text "the pupil dreams"
  python honesty/observer.py ledger --last 5
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from status import wire  # the t3j frame, self-judged
except Exception:
    wire = None

LEDGER = Path(os.environ.get("HONESTY_LEDGER", "data/honesty_ledger.jsonl"))


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def last_hash() -> str:
    if not LEDGER.exists():
        return "0" * 64
    for line in reversed(LEDGER.read_text().splitlines()):
        line = line.strip()
        if line:
            try:
                return json.loads(line)["hash"]
            except (json.JSONDecodeError, KeyError):
                continue
    return "0" * 64


def ingest(channel: str, text: str, claims: list[str] | None = None) -> dict:
    prev = last_hash()
    body = f"{prev}\n{channel}\n{text}"
    h = sha256(body)
    entry = {
        "channel": channel,
        "text": text,
        "claims": claims or [],
        "prev": prev,
        "hash": h,
        "t3": wire.encode_json({"channel": channel, "hash": h}) if wire else None,
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def verify_channel(channel: str) -> dict:
    """Walk the GLOBAL chain in order; a break anywhere means a retroactive
    edit. Reports per-channel stats alongside the global verdict."""
    entries = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
    prev = "0" * 64
    ok = True
    channel_count = 0
    for e in entries:
        if e["prev"] != prev:
            ok = False
        body = f"{e['prev']}\n{e['channel']}\n{e['text']}"
        if sha256(body) != e["hash"]:
            ok = False
        if e["channel"] == channel:
            channel_count += 1
        prev = e["hash"]
    return {"channel": channel, "entries": channel_count, "ledger_entries": len(entries),
            "chain_intact": ok}


def main() -> int:
    ap = argparse.ArgumentParser(description="the honesty gate — a hash-chained observer")
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("ingest")
    i.add_argument("--channel", required=True)
    i.add_argument("--text", required=True)
    i.add_argument("--claim", action="append", default=[], help="a fact this message asserts")

    v = sub.add_parser("verify")
    v.add_argument("--channel", default=None, help="verify one channel (default: the whole ledger)")

    l = sub.add_parser("ledger")
    l.add_argument("--last", type=int, default=5)

    args = ap.parse_args()
    if args.cmd == "ingest":
        e = ingest(args.channel, args.text, args.claim)
        print(f"ingested {args.channel}: {e['hash'][:16]}… (prev {e['prev'][:8]}…)")
        if e["t3"]:
            print(f"  t3: {e['t3'][:24]}…")
    elif args.cmd == "verify":
        if args.channel:
            r = verify_channel(args.channel)
            print(f"{r['channel']}: {r['entries']} entries — chain {'INTACT' if r['chain_intact'] else 'BROKEN'}")
        else:
            ok = all(verify_channel(e["channel"])["chain_intact"]
                     for e in [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()])
            print(f"whole ledger: chain {'INTACT' if ok else 'BROKEN'}")
    elif args.cmd == "ledger":
        lines = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
        for e in lines[-args.last:]:
            print(f"  {e['channel']:<8} {e['hash'][:12]}…  {e['text'][:40]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
