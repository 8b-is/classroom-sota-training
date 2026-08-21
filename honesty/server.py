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

Usage:
  python honesty/server.py --port 8788
"""

import argparse
import json
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import os

sys.path.insert(0, str(Path(__file__).resolve().parent))
from observer import ingest, verify_channel, LEDGER  # noqa: E402


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send(self, code, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/hook":  # WhatsApp webhook verification
            if q.get("hub.mode") == ["subscribe"] and q.get("hub.challenge"):
                self._send(200, q["hub.challenge"][0].encode(), "text/plain")
                return
        if path == "/verify":
            self._send(200, json.dumps(verify_channel("whatsapp")).encode())
            return
        if path == "/ledger":
            lines = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
            self._send(200, json.dumps(lines[-20:]).encode())
            return
        self._send(404, b'{"ok": false}')

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path != "/hook":
            self._send(404, b'{"ok": false}')
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body or b"{}")
        except json.JSONDecodeError:
            data = {}
        # WhatsApp Business Cloud API: value → messages[].text.body
        texts = []
        for value in data.get("entry", []):
            for change in value.get("changes", []):
                for msg in change.get("value", {}).get("messages", []):
                    t = msg.get("text", {}).get("body", "")
                    if t:
                        texts.append(t)
        for t in texts:
            ingest("whatsapp", t)
        self._send(200, json.dumps({"ok": True, "ingested": len(texts)}).encode())


def main() -> int:
    ap = argparse.ArgumentParser(description="the honesty observer's WhatsApp webhook")
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--host", default="0.0.0.0")
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
