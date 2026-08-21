#!/usr/bin/env python3
"""weave.py — the enthea saga, woven as quantSQLITE history.

The append-only ledger is a weave. The craft, thread for thread:

  1. mark the grid        — the entries table (channel, text, prev, hash)
  2. set the diagonals    — every entry carries the previous hash: the
                            diagonal thread that crosses under the next
  3. build the weave      — append the saga, one strand at a time
  4. close the outer loop — a genesis anchor (prev = 0*64) and a head seal
                            (the final entry), so the chain is closed
  5. alternate over/under — each hash covers the entry *and* the previous
                            hash: nothing can be lifted without breaking
                            the one above it
  6. erase the guides     — the grid disappears; only the woven history
                            remains, and it must hold by itself

Run:  python honesty/weave.py [db]     (default: data/weave.db)
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from honesty.ledger import SCHEMA, append, connect, last_hash, sha256, verify

# the saga, in the order it happened — the strand order of the weave
SAGA: list[tuple[str, str]] = [
    ("shrine", "the Bayesian hypercube: the sixteen letters, complete"),
    ("machine", "the arena and the bytecode VM: the letters become an ISA"),
    ("metacircular", "the language runs itself: the evaluator in its own bytecode"),
    ("vakedc", "the capability-graph assembler: NAND-only synthesis, executable"),
    ("doom", "a maze walker written in the enthea language, running on the VM"),
    ("contract", "the VM is the verification target, not the inference runtime"),
    ("lang", "multi-parameter functions: r0..rn, no dummy single-param"),
    ("wave", "the Peirce triad: a well-formed signed triangle and its interpretant"),
]


def grid(conn: sqlite3.Connection) -> int:
    """1. mark the grid — the ledger table exists, empty and waiting."""
    conn.execute(SCHEMA)
    conn.commit()
    return conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]


def diagonals(conn: sqlite3.Connection, name: str, text: str) -> dict:
    """2-5. one strand: its prev thread, its hash, its over-and-under lock."""
    return append(conn, name, text)


def close_outer_loop(conn: sqlite3.Connection) -> str:
    """4. the head seal — a closing strand whose prev is the last real one,
    so the weave is closed at both ends (genesis below, seal above)."""
    tail = conn.execute("SELECT hash FROM entries ORDER BY id DESC LIMIT 1").fetchone()
    seal = append(conn, "seal", "the weave is closed: genesis to head, every strand verified")
    return seal["hash"]


def weave(db: str) -> dict:
    conn = connect(db)
    start = grid(conn)
    strands: list[dict] = []
    for name, text in SAGA:
        strands.append(diagonals(conn, name, text))
    head = close_outer_loop(conn)
    state = verify(conn)
    conn.close()
    return {
        "db": db,
        "start": start,
        "strands": strands,
        "head": head,
        "state": state,
    }


def render(db: str) -> None:
    conn = connect(db)
    rows = conn.execute(
        "SELECT id, channel, text, prev, hash FROM entries ORDER BY id"
    ).fetchall()
    conn.close()
    print("the woven history (guide erased):\n")
    for row in rows:
        short = row["prev"][:8]
        h = row["hash"][:8]
        line = f"{row['channel']:>14}  {row['text']}"
        print(f"  {row['id']:>2}  {line}")
        if row["id"] > 1:
            print(f"      └─ over {short}… under {h}…")
    print("\n  genesis anchored below · head sealed above · every strand over-and-under")


def main() -> int:
    db = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent / "data" / "weave.db")
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    result = weave(db)
    state = result["state"]
    print(f"grid: {result['start']} strands, woven: {len(result['strands'])}")
    print(f"head seal: {result['head'][:12]}…")
    print(f"verify: {'chain INTACT' if state['chain_intact'] else 'chain BROKEN'}")
    render(db)
    return 0 if state["chain_intact"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
