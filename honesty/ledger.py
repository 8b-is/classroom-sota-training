#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
ledger.py — quantSQLITE: an append-only honesty ledger.

The honesty chain, in a real database. Every row is appended (never
rewritten), carries the previous row's hash (the chain), its own sha256 over
the payload, and its t3 fingerprint — the 1-bit model's verdict, so the
ledger's own records are wire-honest. A retroactive edit breaks the chain
and verify() finds it.

Schema:
  entries(id INTEGER PRIMARY KEY AUTOINCREMENT,   -- append order
          channel TEXT, text TEXT, claims TEXT,
          prev TEXT,                               -- previous row's hash
          hash TEXT,                               -- sha256(prev|channel|text)
          t3 TEXT,                                 -- ternaryPureASCII frame
          ts TEXT)

Usage:
  python honesty/ledger.py init   data/honesty.db
  python honesty/ledger.py append data/honesty.db --channel ama --text "..."
  python honesty/ledger.py verify data/honesty.db
  python honesty/ledger.py tail   data/honesty.db --last 5
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from status import wire
except Exception:
    wire = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT NOT NULL,
    text TEXT NOT NULL,
    claims TEXT NOT NULL DEFAULT '[]',
    prev TEXT NOT NULL,
    hash TEXT NOT NULL,
    t3 TEXT NOT NULL DEFAULT '',
    ts TEXT NOT NULL
);
"""


def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


class Ledger:
    """One ledger, one connection.

    The connection is sacred and 1:1 — it is born when the ledger is opened
    and dies when it is closed. It is never handed to another function and
    never passed around: everything a strand needs happens inside this one
    object, over its one connection.
    """

    def __init__(self, db):
        self.db = db
        self.conn = sqlite3.connect(db)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def last_hash(self):
        row = self.conn.execute("SELECT hash FROM entries ORDER BY id DESC LIMIT 1").fetchone()
        return row["hash"] if row else "0" * 64

    def append(self, channel, text, claims=None):
        prev = self.last_hash()
        body = f"{prev}\n{channel}\n{text}"
        h = sha256(body)
        t3 = wire.encode_json({"channel": channel, "hash": h}) if wire else ""
        self.conn.execute(
            "INSERT INTO entries (channel, text, claims, prev, hash, t3, ts) VALUES (?,?,?,?,?,?,?)",
            (channel, text, json.dumps(claims or []), prev, h, t3,
             datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()
        return {"channel": channel, "hash": h, "prev": prev, "t3": t3}

    def verify(self):
        rows = self.conn.execute(
            "SELECT id, channel, text, prev, hash FROM entries ORDER BY id"
        ).fetchall()
        prev = "0" * 64
        ok = True
        for r in rows:
            if r["prev"] != prev:
                ok = False
            if sha256(f"{r['prev']}\n{r['channel']}\n{r['text']}") != r["hash"]:
                ok = False
            prev = r["hash"]
        return {"entries": len(rows), "chain_intact": ok}

    def tail(self, n):
        rows = self.conn.execute(
            "SELECT channel, hash, text, ts FROM entries ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def rows(self):
        return self.conn.execute(
            "SELECT id, channel, text, prev, hash FROM entries ORDER BY id"
        ).fetchall()


def main() -> int:
    ap = argparse.ArgumentParser(description="quantSQLITE — the append-only honesty ledger")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, help_ in [("init", "create the ledger"), ("append", "append a row"),
                        ("verify", "verify the chain"), ("tail", "recent rows")]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("db")
        if name == "append":
            p.add_argument("--channel", required=True)
            p.add_argument("--text", required=True)
            p.add_argument("--claim", action="append", default=[])
        elif name == "tail":
            p.add_argument("--last", type=int, default=5)
    args = ap.parse_args()

    if args.cmd == "init":
        ledger = Ledger(args.db)
        ledger.close()
        print(f"ledger ready: {args.db}")
    elif args.cmd == "append":
        ledger = Ledger(args.db)
        e = ledger.append(args.channel, args.text, args.claim)
        ledger.close()
        print(f"appended {args.channel}: {e['hash'][:16]}… (prev {e['prev'][:8]}…)")
        if e["t3"]:
            print(f"  t3: {e['t3'][:24]}…")
    elif args.cmd == "verify":
        ledger = Ledger(args.db)
        r = ledger.verify()
        ledger.close()
        print(f"{r['entries']} entries — chain {'INTACT' if r['chain_intact'] else 'BROKEN'}")
    elif args.cmd == "tail":
        ledger = Ledger(args.db)
        for e in ledger.tail(args.last):
            print(f"  {e['channel']:<8} {e['hash'][:12]}…  {e['text'][:40]}")
        ledger.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
