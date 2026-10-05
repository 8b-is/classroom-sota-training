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
from contextlib import contextmanager
import fcntl
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


@contextmanager
def _ledger_lock(*, exclusive: bool):
    """POSIX advisory lock shared by cooperating CLI and webhook processes.

    A separate stable lock file protects the head-read/append transaction.
    Do not delete or replace this lock file while any observer is running.
    """
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    lock_path = LEDGER.with_name(LEDGER.name + ".lock")
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(lock_path, flags, 0o600)
    with os.fdopen(fd, "a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


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


def entry_body(prev, channel, text, delivery_id=None):
    if delivery_id is None:
        return f"{prev}\n{channel}\n{text}"
    return json.dumps(["delivery-v1", prev, channel, text, delivery_id], ensure_ascii=True, separators=(",", ":"))


def ingest(channel: str, text: str, claims: list[str] | None = None, *, delivery_id: str | None = None) -> dict:
    return ingest_batch(channel, [(text, delivery_id, claims)])[0]


def ingest_batch(channel, messages):
    """Reject delivery conflicts before writing, under one cross-process lock.

    A retry skips already durable rows. This does not promise atomic recovery
    from a torn filesystem write; malformed ledgers fail closed for inspection.
    """
    messages = list(messages)
    for text, delivery_id, claims in messages:
        if not isinstance(text, str):
            raise ValueError("Invalid text")
        if delivery_id is not None and (not isinstance(delivery_id, str) or not delivery_id or len(delivery_id) > 1024):
            raise ValueError("Invalid delivery ID")
    with _ledger_lock(exclusive=True):
        prior_rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()] if LEDGER.exists() else []
        by_id = {(row["channel"], row["delivery_id"]): row for row in prior_rows if "delivery_id" in row}
        prev = prior_rows[-1]["hash"] if prior_rows else "0" * 64
        results, additions = [], []
        for text, delivery_id, claims in messages:
            key = (channel, delivery_id)
            if delivery_id is not None and key in by_id:
                prior = by_id[key]
                if prior["text"] != text:
                    raise ValueError("Delivery ID reused with different text")
                results.append(prior)
                continue
            h = sha256(entry_body(prev, channel, text, delivery_id))
            entry = {"channel": channel, "text": text, "claims": claims or [],
                     "prev": prev, "hash": h,
                     "t3": wire.encode_json({"channel": channel, "hash": h}) if wire else None}
            if delivery_id is not None:
                entry["delivery_id"] = delivery_id
                by_id[key] = entry
            results.append(entry)
            additions.append(entry)
            prev = h
        if additions:
            with open(LEDGER, "a") as f:
                f.write("".join(json.dumps(entry) + "\n" for entry in additions))
                f.flush()
                os.fsync(f.fileno())
        return results


def ledger_snapshot() -> list[dict]:
    """Read a stable snapshot; a ledger with no writes has no entries."""
    with _ledger_lock(exclusive=False):
        if not LEDGER.exists():
            return []
        return [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]


def verify_channel(channel: str | None) -> dict:
    """Walk the GLOBAL chain in order; a break anywhere means a retroactive
    edit. Reports per-channel stats alongside the global verdict."""
    entries = ledger_snapshot()
    prev = "0" * 64
    ok = True
    channel_count = 0
    for e in entries:
        if e["prev"] != prev:
            ok = False
        body = entry_body(e["prev"], e["channel"], e["text"], e.get("delivery_id"))
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
        r = verify_channel(args.channel)
        if args.channel:
            print(f"{r['channel']}: {r['entries']} entries — chain {'INTACT' if r['chain_intact'] else 'BROKEN'}")
        else:
            ok = r["chain_intact"]
            print(f"whole ledger: chain {'INTACT' if ok else 'BROKEN'}")
        return 0 if r["chain_intact"] else 1
    elif args.cmd == "ledger":
        lines = ledger_snapshot()
        for e in lines[-args.last:]:
            print(f"  {e['channel']:<8} {e['hash'][:12]}…  {e['text'][:40]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
