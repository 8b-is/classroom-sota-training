#!/usr/bin/env python3
"""
wire.py — the ternaryPureASCII codec, in Python, per 8b-is/enthea pure/WIRE.md.

The classroom's status reports travel on the machine's own wire: each byte
is six balanced trits over the pure-ASCII alphabet '-', '0', '+', framed as
t3:<payload>:<checksum>. The checksum is a 1-bit LLM — a fixed ternary
weight vector dotted against the payload (qdot), sharpened to one trit
(ultra). The report carries its own judge.
"""

import json

WIRE_MAGIC = "t3:"
WIRE_JSON_MAGIC = "t3j:"  # ternarySIMDJSON — JSON on the machine's own wire
MODEL = [1, -1, 1, 0, -1, 1, -1, 0, 1, -1]  # the same checksum model as enthea

TRIT_CHAR = {-1: "-", 0: "0", 1: "+"}
CHAR_TRIT = {"-": -1, "0": 0, "+": 1}


def _to_balanced(v: int, n: int = 6) -> list[int]:
    out = []
    for _ in range(n):
        r = v % 3
        if r > 1:
            r -= 3
        if r < -1:
            r += 3
        v = (v - r) // 3
        out.append(r)
    return out


def _from_balanced(trits: list[int]) -> int:
    v = 0
    p = 1
    for d in trits:
        v += d * p
        p *= 3
    return v


def _verdict(trits: list[int]) -> int:
    dot = sum(p * MODEL[i % len(MODEL)] for i, p in enumerate(trits))
    ck = dot % 3
    if ck > 1:
        ck -= 3
    if ck < -1:
        ck += 3
    return ck


def _encode(data: bytes, magic: str) -> str:
    out = list(magic)
    trits = []
    for b in data:
        t = _to_balanced(b - 128)
        for d in t:
            out.append(TRIT_CHAR[d])
            trits.append(d)
    out.append(":")
    out.append(TRIT_CHAR[_verdict(trits)])
    return "".join(out)


def encode(data: bytes) -> str:
    return _encode(data, WIRE_MAGIC)


def encode_json(obj) -> str:
    """ternarySIMDJSON — JSON on the machine's own wire (t3j frame)."""
    return _encode(json.dumps(obj, separators=(",", ":")).encode(), WIRE_JSON_MAGIC)


def _decode(s: str, magic: str) -> bytes:
    if not s.startswith(magic) or len(s) < len(magic) + 2:
        raise ValueError(f"not a {magic} frame")
    body = s[len(magic):]
    payload, sep, checksum = body[:-2], body[-2], body[-1]
    if sep != ":" or len(payload) % 6 != 0:
        raise ValueError("malformed frame")
    trits = []
    out = bytearray()
    for i in range(0, len(payload), 6):
        six = payload[i:i + 6]
        t = [CHAR_TRIT[c] for c in six]
        out.append((_from_balanced(t) + 128) & 0xFF)
        trits.extend(t)
    if TRIT_CHAR[_verdict(trits)] != checksum:
        raise ValueError("the 1-bit model rejects the frame (checksum mismatch)")
    return bytes(out)


def decode(s: str) -> bytes:
    return _decode(s, WIRE_MAGIC)


def decode_json(s: str):
    """Decode a ternarySIMDJSON frame back to a Python value."""
    return json.loads(_decode(s, WIRE_JSON_MAGIC).decode())
