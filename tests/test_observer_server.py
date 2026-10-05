"""Read-route authorization against an ephemeral loopback server only."""
import importlib.util
from pathlib import Path
import tempfile
import threading
import http.client
from unittest.mock import patch
from http.server import ThreadingHTTPServer

SERVER = Path(__file__).parent.parent / 'honesty' / 'server.py'


def test_private_read_routes_require_explicit_token():
    spec = importlib.util.spec_from_file_location('observer_server_test', SERVER)
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)
    import observer
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Path(tmp) / 'synthetic.jsonl'
        with patch.object(observer, 'LEDGER', ledger):
            observer.ingest('whatsapp', 'SYNTHETIC_PRIVATE_TEXT')
            # Server name is irrelevant here; avoid host reverse-DNS in synthetic tests.
            with patch('socket.getfqdn', return_value='localhost'):
                httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            def request(path, headers):
                conn = http.client.HTTPConnection(*httpd.server_address, timeout=2)
                try:
                    conn.request('GET', path, headers=headers)
                    response = conn.getresponse()
                    return response.status, response.read(), dict(response.getheaders())
                finally:
                    conn.close()
            try:
                with patch.dict(server.os.environ, {'HONESTY_READ_TOKEN': 'synthetic-read-token'}):
                    for path in ['/ledger', '/verify']:
                        for headers in [{}, {'Authorization': 'Bearer wrong'}, {'Authorization': 'Basic synthetic-read-token'}]:
                            status, body, _ = request(path, headers)
                            assert status == 401
                            assert b'SYNTHETIC_PRIVATE_TEXT' not in body
                        status, _, _ = request(path + '?token=synthetic-read-token', {})
                        assert status == 401
                        status, body, headers = request(path, {'Authorization': 'Bearer synthetic-read-token'})
                        assert status == 200
                        assert headers.get('Cache-Control') == 'no-store'
                        assert 'Access-Control-Allow-Origin' not in headers
                        if path == '/ledger':
                            assert b'SYNTHETIC_PRIVATE_TEXT' in body
                with patch.dict(server.os.environ, {'HONESTY_READ_TOKEN': ''}):
                    status, body, _ = request('/ledger', {'Authorization': 'Bearer synthetic-read-token'})
                    assert status == 503
                    assert b'SYNTHETIC_PRIVATE_TEXT' not in body
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=2)
                assert not thread.is_alive()


def test_webhook_authentication_and_payload_bounds():
    import hashlib
    import hmac
    import json
    spec = importlib.util.spec_from_file_location('observer_hook_test', SERVER)
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)
    calls = []
    with patch.object(server, 'ingest_batch', side_effect=lambda *args: calls.append(args)), patch('socket.getfqdn', return_value='localhost'):
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        def request(method, path='/hook', body=None, headers=None):
            conn = http.client.HTTPConnection(*httpd.server_address, timeout=2)
            try:
                conn.request(method, path, body=body, headers=headers or {})
                response = conn.getresponse()
                return response.status, response.read()
            finally:
                conn.close()
        def signature(body):
            return {'X-Hub-Signature-256': 'sha256=' + hmac.new(b'synthetic-secret', body, hashlib.sha256).hexdigest()}
        try:
            with patch.dict(server.os.environ, {'HONESTY_VERIFY_TOKEN': 'synthetic-verify', 'HONESTY_APP_SECRET': 'synthetic-secret'}):
                query = '/hook?hub.mode=subscribe&hub.challenge=synthetic-challenge'
                assert request('GET', query)[0] == 403
                assert request('GET', query + '&hub.verify_token=wrong')[0] == 403
                assert request('GET', query + '&hub.verify_token=synthetic-verify') == (200, b'synthetic-challenge')
                assert request('GET', query + '&hub.verify_token=synthetic-verify&hub.verify_token=synthetic-verify')[0] == 403
                body = json.dumps({'entry': [{'changes': [{'value': {'messages': [{'id': 'synthetic-id', 'text': {'body': 'synthetic text'}}]}}]}]}).encode()
                assert request('POST', body=body)[0] == 401
                assert request('POST', body=body + b' ', headers=signature(body))[0] == 401
                assert request('POST', body=b'[]', headers=signature(b'[]'))[0] == 400
                assert request('POST', body=b'{', headers=signature(b'{'))[0] == 400
                assert request('POST', body=b'', headers={'Content-Length': '1048577'})[0] == 413
                assert request('POST', body=b'', headers={'Content-Length': '-1'})[0] == 400
                assert request('POST', body=b'', headers={'Transfer-Encoding': 'chunked'})[0] == 400
                assert calls == []
                assert request('POST', body=body, headers=signature(body))[0] == 200
                assert calls == [('whatsapp', [('synthetic text', 'synthetic-id', None)])]
                # A later invalid text must prevent even the earlier valid text from being appended.
                invalid = json.dumps({'entry': [{'changes': [{'value': {'messages': [{'text': {'body': 'valid'}}, {'text': {'body': 123}}]}}]}]}).encode()
                assert request('POST', body=invalid, headers=signature(invalid))[0] == 400
                assert len(calls) == 1
            with patch.dict(server.os.environ, {'HONESTY_VERIFY_TOKEN': '', 'HONESTY_APP_SECRET': ''}):
                assert request('GET', query)[0] == 503
                assert request('POST', body=body, headers=signature(body))[0] == 503
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=2)
            assert not thread.is_alive()


def test_signed_delivery_retries_and_conflicts():
    import json
    import hashlib
    import hmac
    spec = importlib.util.spec_from_file_location('observer_delivery_server', SERVER)
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)
    import observer
    with tempfile.TemporaryDirectory() as tmp, patch.object(observer, 'LEDGER', Path(tmp) / 'ledger.jsonl'), patch.dict(server.os.environ, {'HONESTY_APP_SECRET': 'synthetic'}), patch('socket.getfqdn', return_value='localhost'):
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        def post(messages):
            body = json.dumps({'entry': [{'changes': [{'value': {'messages': messages}}]}]}).encode()
            headers = {'X-Hub-Signature-256': 'sha256=' + hmac.new(b'synthetic', body, hashlib.sha256).hexdigest()}
            conn = http.client.HTTPConnection(*httpd.server_address, timeout=2)
            try:
                conn.request('POST', '/hook', body, headers)
                response = conn.getresponse()
                response.read()
                return response.status
            finally:
                conn.close()
        def msg(identifier, text='same text'):
            return {'id': identifier, 'text': {'body': text}}
        try:
            # A prior partial delivery persisted the first item before retry.
            observer.ingest('whatsapp', 'same text', delivery_id='first')
            assert post([msg('first'), msg('second')]) == 200
            assert post([msg('first'), msg('second')]) == 200
            assert len(observer.ledger_snapshot()) == 2
            before = observer.LEDGER.read_bytes()
            assert post([msg('third'), msg('first', 'conflicting')]) == 409
            assert observer.LEDGER.read_bytes() == before
            assert post([msg('third'), msg('third', 'conflicting')]) == 409
            assert observer.LEDGER.read_bytes() == before
            assert post([msg('third'), {'text': {'body': 'missing id'}}]) == 400
            assert observer.LEDGER.read_bytes() == before
            assert post([msg('third'), msg('third')]) == 200
            assert len(observer.ledger_snapshot()) == 3
            assert observer.verify_channel('whatsapp')['chain_intact']
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=2)
            assert not thread.is_alive()
