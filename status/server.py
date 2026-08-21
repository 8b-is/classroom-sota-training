#!/usr/bin/env python3
"""
server.py — the classroom's live-status webhook server.

A stdlib-only HTTP server. The training box POSTs progress to /hook (the
webhook); the landing page GETs /status and receives the latest report as a
ternaryPureASCII frame (per enthea pure/WIRE.md) — delayed but LIVE: the
page polls, and what it gets is the machine's own alphabet, self-judged.

Endpoints:
  POST /hook   {"phase": "...", "epoch": n, "val": x, "status": "..."}
  GET  /status → t3:<payload>:<checksum>   (the ternaryPureASCII report)
  GET  /raw    → the JSON report (for debugging)

Usage:
  python status/server.py --port 8787
  # on the box: python status/hook.py --url http://host:8787/hook ...
"""

import argparse
import json
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import os

sys.path.insert(0, os.path.dirname(__file__))
from wire import encode_json  # noqa: E402

STATE = {"phase": "idle", "epoch": 0, "val": None, "status": "the classroom is quiet", "updated": 0}
LOCK = threading.Lock()


def report_json() -> dict:
    with LOCK:
        return dict(STATE)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/hook":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            body = {}
        with LOCK:
            for k in ("phase", "epoch", "val", "status"):
                if k in body:
                    STATE[k] = body[k]
            STATE["updated"] = int(time.time())
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/status":
            # the delayed-but-live report, on the machine's own wire
            # (ternarySIMDJSON — the t3j frame, judged by its own 1-bit model)
            frame = encode_json(report_json())
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(frame.encode())
            return
        if path == "/raw":
            body = json.dumps(report_json()).encode()
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self._cors()
        self.end_headers()


def main() -> int:
    ap = argparse.ArgumentParser(description="the classroom's live-status webhook server")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"classroom status server on {args.host}:{args.port} — POST /hook · GET /status (ternaryPureASCII)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
