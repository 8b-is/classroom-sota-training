#!/usr/bin/env python3
"""
cometapi_teacher.py — the external teacher lane for the Council of Elders.

The council's self-hosted teachers run on MLX fp8 locally. CometAPI is the
external lane: hosted Qwen (3 / 3.5 / 3.8 Max) and DeepSeek (R1 / Reasoner)
in pure MAX-thinking mode — the teachers that are too expensive to self-host
and too valuable to skip. One OpenAI-compatible endpoint, 500+ models,
fallback across providers (per the redeem-credit trial, see docs/cometapi.md).

Stdlib only (urllib) — the classroom repo stays dependency-light.

Usage:
  export COMETAPI_API_KEY=...
  python scripts/cometapi_teacher.py \
    --teacher qwen3.8-max --prompt "Explain geometric-mean softmax" \
    --max-tokens 256
  python scripts/cometapi_teacher.py --teacher deepseek-r1 --file prompt.txt -n 3
"""

import argparse
import json
import os
import sys
import time
import urllib.request

BASE_URL = os.environ.get("COMETAPI_BASE_URL", "https://www.cometapi.com/v1")

# the council's external teacher table: id → (model name, thinking mode flag)
TEACHERS = {
    "qwen2.5": ("Qwen/Qwen2.5-72B-Instruct", False),
    "qwen3": ("Qwen/Qwen3-235B-A22B-Instruct", True),
    "qwen3.5": ("Qwen/Qwen3.5-30B-A3B-Instruct", True),
    "qwen3.8-max": ("Qwen/Qwen3.8-Max", True),
    "deepseek-r1": ("deepseek/deepseek-r1", True),
    "deepseek-reasoner": ("deepseek-reasoner", True),
    "deepseek-pro": ("deepseek/deepseek-pro", True),
}


def teacher_call(model: str, prompt: str, max_tokens: int, temperature: float) -> dict:
    api_key = os.environ.get("COMETAPI_API_KEY")
    if not api_key:
        sys.exit("COMETAPI_API_KEY is not set (export COMETAPI_API_KEY=...)")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    elapsed = time.monotonic() - start
    msg = data["choices"][0]["message"]
    usage = data.get("usage", {})
    return {
        "model": model,
        "content": msg.get("content", ""),
        "reasoning": msg.get("reasoning_content") or msg.get("reasoning", ""),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "seconds": elapsed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CometAPI teacher inference for the classroom")
    ap.add_argument("--teacher", choices=TEACHERS, default="qwen3.8-max")
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--file", default=None, help="read the prompt from a file")
    ap.add_argument("-n", "--count", type=int, default=1, help="how many teacher calls")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=0.7)
    args = ap.parse_args()

    if args.file:
        with open(args.file) as f:
            prompt = f.read()
    else:
        prompt = args.prompt or "What is the geometric-mean softmax consensus, and why does a council of elders prefer it over a majority vote?"

    model, thinking = TEACHERS[args.teacher]
    print(f"cometapi teacher — {args.teacher} ({model})"
          + (" · MAX thinking" if thinking else ""))
    total_in, total_out, total_s = 0, 0, 0.0
    for i in range(args.count):
        r = teacher_call(model, prompt, args.max_tokens, args.temperature)
        if r["reasoning"]:
            print(f"\n[{i+1}] reasoning ({len(r['reasoning'])} chars)")
        print(f"\n[{i+1}] {r['content'].strip()}")
        print(f"  → {r['prompt_tokens']} in / {r['completion_tokens']} out · {r['seconds']:.2f}s")
        total_in += r["prompt_tokens"]
        total_out += r["completion_tokens"]
        total_s += r["seconds"]
    print(f"\ntotals: {total_in} in / {total_out} out · {total_s:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
