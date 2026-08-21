import subprocess
import sys
import tempfile
from pathlib import Path

WEAVE = Path(__file__).parent.parent / "honesty" / "weave.py"


def test_weave_is_closed_and_holds() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "weave.db"
        proc = subprocess.run(
            [sys.executable, str(WEAVE), str(db)],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "chain INTACT" in proc.stdout
        # every strand of the saga is present, genesis to seal
        assert "shrine" in proc.stdout
        assert "doom" in proc.stdout
        assert "wave" in proc.stdout
        assert "seal" in proc.stdout
