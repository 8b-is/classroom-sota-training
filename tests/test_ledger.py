import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

LEDGER = Path(__file__).parent.parent / "honesty" / "ledger.py"


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(LEDGER), *args],
        capture_output=True,
        text=True,
    )


def test_chain_intact_then_broken() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "ledger.db"
        assert run(["init", str(db)]).returncode == 0
        assert run(["append", str(db), "--channel", "ama", "--text", "turn one"]).returncode == 0
        assert run(["append", str(db), "--channel", "ama", "--text", "turn two"]).returncode == 0

        ok = run(["verify", str(db)])
        assert "chain INTACT" in ok.stdout

        import sqlite3

        conn = sqlite3.connect(db)
        conn.execute("UPDATE entries SET text=? WHERE id=1", ("RETROACTIVELY EDITED",))
        conn.commit()
        conn.close()

        bad = run(["verify", str(db)])
        assert "chain BROKEN" in bad.stdout
