"""CLI checks use synthetic temporary ledgers; no webhook or network."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

OBSERVER = Path(__file__).parent.parent / 'honesty' / 'observer.py'


def test_verify_exit_codes_include_other_channels():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Path(tmp) / 'synthetic.jsonl'
        env = dict(os.environ, HONESTY_LEDGER=str(ledger))
        def run(*args):
            return subprocess.run([sys.executable, str(OBSERVER), *args], env=env,
                                  capture_output=True, text=True, timeout=5)
        for channel in ['alpha', 'beta']:
            assert run('ingest', '--channel', channel, '--text', 'synthetic turn').returncode == 0
        for args in [(), ('--channel', 'alpha')]:
            result = run('verify', *args)
            assert result.returncode == 0
            assert 'chain INTACT' in result.stdout
        rows = [json.loads(line) for line in ledger.read_text().splitlines()]
        rows[1]['text'] = 'tampered in another channel'
        ledger.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        before = ledger.read_bytes()
        for args in [(), ('--channel', 'alpha')]:
            result = run('verify', *args)
            assert 'chain BROKEN' in result.stdout
            assert result.returncode == 1
        assert ledger.read_bytes() == before


def test_full_verify_scans_once():
    import importlib.util
    from unittest.mock import patch
    spec = importlib.util.spec_from_file_location('observer_test', OBSERVER)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    with tempfile.TemporaryDirectory() as tmp:
        observer.LEDGER = Path(tmp) / 'synthetic.jsonl'
        for i in range(20):
            observer.ingest('alpha' if i % 2 else 'beta', str(i))
        original = Path.read_text
        reads = []
        def counted(path, *args, **kwargs):
            reads.append(path)
            return original(path, *args, **kwargs)
        with patch.object(sys, 'argv', ['observer.py', 'verify']), patch.object(Path, 'read_text', counted):
            assert observer.main() == 0
        assert len(reads) == 1


def test_overlapping_ingests_preserve_one_chain():
    import importlib.util
    import threading
    from concurrent.futures import ThreadPoolExecutor
    from unittest.mock import patch
    spec = importlib.util.spec_from_file_location('observer_concurrent_test', OBSERVER)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    with tempfile.TemporaryDirectory() as tmp:
        observer.LEDGER = Path(tmp) / 'synthetic.jsonl'
        first_read = threading.Event()
        release_first = threading.Event()
        second_done = threading.Event()
        original = observer.entry_body
        calls = 0
        def delayed_head(*args):
            nonlocal calls
            calls += 1
            first = calls == 1
            value = original(*args)
            if first:
                first_read.set()
                assert release_first.wait(3)
            return value
        def second():
            try:
                return observer.ingest('beta', 'second synthetic turn')
            finally:
                second_done.set()
        with patch.object(observer, 'entry_body', delayed_head), ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(observer.ingest, 'alpha', 'first synthetic turn')
            assert first_read.wait(3)
            other = pool.submit(second)
            # Before serialization the second writer commits against the same head.
            second_done.wait(0.15)
            release_first.set()
            first.result(timeout=3)
            other.result(timeout=3)
        result = observer.verify_channel(None)
        assert result['ledger_entries'] == 2
        assert result['chain_intact']


def test_separate_processes_preserve_chain():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Path(tmp) / 'processes.jsonl'
        env = dict(os.environ, HONESTY_LEDGER=str(ledger))
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import observer; "
                "[observer.ingest(sys.argv[2], str(i)) for i in range(20)]")
        workers = [subprocess.Popen([sys.executable, '-c', code, str(OBSERVER.parent), channel],
                                   env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                   for channel in ['alpha', 'beta']]
        try:
            for worker in workers:
                _, err = worker.communicate(timeout=5)
                assert worker.returncode == 0, err
        finally:
            for worker in workers:
                if worker.poll() is None:
                    worker.kill()
                    worker.wait()
        result = subprocess.run([sys.executable, str(OBSERVER), 'verify'], env=env,
                                capture_output=True, text=True, timeout=5)
        assert result.returncode == 0
        assert 'chain INTACT' in result.stdout
        assert len(ledger.read_text().splitlines()) == 40


def test_failed_append_releases_lock_without_partial_record():
    import importlib.util
    spec = importlib.util.spec_from_file_location('observer_failure_test', OBSERVER)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    with tempfile.TemporaryDirectory() as tmp:
        observer.LEDGER = Path(tmp) / 'failure.jsonl'
        try:
            observer.ingest('alpha', 'bad claims', [object()])
        except TypeError:
            pass
        else:
            raise AssertionError('Expected non-serializable claims to fail')
        observer.ingest('alpha', 'valid')
        result = observer.verify_channel('alpha')
        assert result['entries'] == 1
        assert result['chain_intact']


def test_empty_ledger_and_reader_waits_for_writer():
    import importlib.util
    import threading
    from concurrent.futures import ThreadPoolExecutor
    import tempfile
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('observer_snapshot_test', Path(__file__).parent.parent / 'honesty' / 'observer.py')
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    with tempfile.TemporaryDirectory() as tmp:
        observer.LEDGER = Path(tmp) / 'ledger.jsonl'
        assert observer.ledger_snapshot() == []
        assert observer.verify_channel(None)['chain_intact'] is True
        assert observer.verify_channel(None)['ledger_entries'] == 0
        observer.ingest('synthetic', 'first')
        started = threading.Event()
        finished = threading.Event()
        def read():
            started.set()
            result = observer.ledger_snapshot()
            finished.set()
            return result
        with ThreadPoolExecutor(max_workers=1) as pool:
            with observer._ledger_lock(exclusive=True):
                future = pool.submit(read)
                assert started.wait(1)
                assert not finished.wait(.15), 'reader bypassed writer lock'
            assert len(future.result(timeout=2)) == 1
