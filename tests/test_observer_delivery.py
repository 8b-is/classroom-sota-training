"""Synthetic delivery idempotency, with no network or account access."""
import importlib.util
import json
from pathlib import Path
import tempfile
from concurrent.futures import ThreadPoolExecutor

SOURCE = Path(__file__).parents[1] / 'honesty/observer.py'


def load():
    spec = importlib.util.spec_from_file_location('delivery_observer', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_delivery_persistence_concurrency_and_chain():
    observer = load()
    with tempfile.TemporaryDirectory() as tmp:
        observer.LEDGER = Path(tmp) / 'ledger.jsonl'
        observer.ingest('synthetic', 'legacy')
        with ThreadPoolExecutor(max_workers=2) as pool:
            rows = list(pool.map(lambda _: observer.ingest('synthetic', 'same text', delivery_id='id1'), range(8)))
        assert all(row == rows[0] for row in rows)
        restarted = load()
        restarted.LEDGER = observer.LEDGER
        assert restarted.ingest('synthetic', 'same text', delivery_id='id1') == rows[0]
        restarted.ingest('synthetic', 'same text', delivery_id='id2')
        restarted.ingest('other-channel', 'same text', delivery_id='id1')
        assert len(restarted.ledger_snapshot()) == 4
        assert restarted.verify_channel(None)['chain_intact']
        before = restarted.LEDGER.read_bytes()
        try:
            restarted.ingest('synthetic', 'changed', delivery_id='id1')
        except ValueError:
            pass
        else:
            raise AssertionError('Conflicting delivery accepted')
        assert restarted.LEDGER.read_bytes() == before
        records = restarted.ledger_snapshot()
        records[1]['delivery_id'] = 'tampered'
        restarted.LEDGER.write_text(''.join(json.dumps(row) + '\n' for row in records))
        assert not restarted.verify_channel(None)['chain_intact']
