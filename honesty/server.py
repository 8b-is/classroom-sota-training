#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
server.py — the honesty observer's channel adapter.

An eBPF-like hook on a chat stream: WhatsApp's Business Cloud API delivers
group messages to this webhook; every message is folded into the honesty
ledger (hash-chained, t3-fingerprinted). The channel is unchanged — the
observer just watches it.

Set the callback URL in the WhatsApp Business app to:
  POST /hook   ← WhatsApp delivers messages here (verification GET /hook?hub.challenge)
  GET  /verify ← chain verdict for the whole ledger
  GET  /ledger ← the recent entries

Read routes require Authorization: Bearer <HONESTY_READ_TOKEN>.
Without HONESTY_READ_TOKEN, read access is unavailable. Use HTTPS termination
before exposing this adapter. /hook requires HONESTY_VERIFY_TOKEN for the GET
challenge and HONESTY_APP_SECRET for raw-body HMAC-SHA256 POST validation.
Delivery retry behavior is covered by synthetic loopback tests;
live provider compatibility remains unverified;
this adapter is not a production deployment recipe.

Usage (loopback by default):
  python honesty/server.py --port 8788
"""

import argparse
import hmac
import hashlib
import json
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import os

sys.path.insert(0, str(Path(__file__).resolve().parent))
from observer import ingest_batch, verify_channel, ledger_snapshot  # noqa: E402


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send(self, code, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _authorize_read(self):
        token = os.environ.get("HONESTY_READ_TOKEN", "")
        if not token:
            self._send(503, b'{"ok": false, "error": "Read access is not configured"}')
            return False
        values = self.headers.get_all("Authorization", [])
        expected = ("Bearer " + token).encode("utf-8")
        if len(values) != 1 or not hmac.compare_digest(values[0].encode("utf-8"), expected):
            self._send(401, b'{"ok": false, "error": "Unauthorized"}')
            return False
        return True

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/hook":  # WhatsApp webhook verification
            token = os.environ.get("HONESTY_VERIFY_TOKEN", "")
            if not token:
                self._send(503, b'{"ok": false, "error": "Webhook verification is not configured"}')
                return
            supplied = q.get("hub.verify_token", [])
            challenge = q.get("hub.challenge", [])
            if (q.get("hub.mode") == ["subscribe"] and len(supplied) == 1
                    and len(challenge) == 1
                    and hmac.compare_digest(supplied[0].encode(), token.encode())):
                self._send(200, challenge[0].encode(), "text/plain")
            else:
                self._send(403, b'{"ok": false}')
            return
        if path in ("/verify", "/ledger") and not self._authorize_read():
            return
        if path == "/verify":
            self._send(200, json.dumps(verify_channel("whatsapp")).encode())
            return
        if path == "/ledger":
            lines = ledger_snapshot()
            self._send(200, json.dumps(lines[-20:]).encode())
            return
        self._send(404, b'{"ok": false}')

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path != "/hook":
            self._send(404, b'{"ok": false}')
            return
        secret = os.environ.get("HONESTY_APP_SECRET", "")
        if not secret:
            self._send(503, b'{"ok": false, "error": "Webhook ingestion is not configured"}')
            return
        lengths = self.headers.get_all("Content-Length", [])
        if (self.headers.get_all("Transfer-Encoding", []) or len(lengths) != 1
                or not lengths[0].isascii() or not lengths[0].isdigit()):
            self._send(400, b'{"ok": false, "error": "Invalid body framing"}')
            return
        if len(lengths[0]) > 7 or int(lengths[0]) > 1048576:
            self._send(413, b'{"ok": false, "error": "Body too large"}')
            return
        length = int(lengths[0])
        signatures = self.headers.get_all("X-Hub-Signature-256", [])
        if len(signatures) != 1:
            self._send(401, b'{"ok": false}')
            return
        self.connection.settimeout(5)
        try:
            body = self.rfile.read(length)
        except TimeoutError:
            self._send(408, b'{"ok": false}')
            return
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if len(body) != length or not hmac.compare_digest(signatures[0].encode(), expected.encode()):
            self._send(401, b'{"ok": false}')
            return
        try:
            data = json.loads(body)
            messages = message_deliveries(data)
        except (ValueError, TypeError, AttributeError, UnicodeDecodeError):
            self._send(400, b'{"ok": false, "error": "Invalid payload"}')
            return
        try:
            ingest_batch("whatsapp", [(text, identifier, None) for text, identifier in messages])
        except ValueError:
            self._send(409, b'{"ok": false, "error": "Delivery conflict"}')
            return
        self._send(200, json.dumps({"ok": True, "processed": len(messages)}).encode())


def message_deliveries(data):
    """Validate the full batch before appending any text."""
    if not isinstance(data, dict) or not isinstance(data.get("entry", []), list):
        raise ValueError("Invalid entries")
    texts = []
    for entry in data.get("entry", []):
        changes = entry.get("changes", [])
        if not isinstance(changes, list):
            raise ValueError("Invalid changes")
        for change in changes:
            messages = change.get("value", {}).get("messages", [])
            if not isinstance(messages, list):
                raise ValueError("Invalid messages")
            for message in messages:
                text = message.get("text", {}).get("body", "")
                if not isinstance(text, str):
                    raise ValueError("Invalid text")
                if text:
                    identifier = message.get("id")
                    if not isinstance(identifier, str) or not identifier or len(identifier) > 1024:
                        raise ValueError("Missing or invalid delivery ID")
                    texts.append((text, identifier))
    return texts


def main() -> int:
    ap = argparse.ArgumentParser(description="the honesty observer's WhatsApp webhook")
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"honesty observer on {args.host}:{args.port} — POST /hook · GET /verify · GET /ledger")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
