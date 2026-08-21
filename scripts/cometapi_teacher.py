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

# the council's external teacher table: id → (CometAPI model id, thinking)
# — my eight picks from the live catalog: four Qwen + four DeepSeek, all
# open-weights, spanning the generations, MAX thinking.
TEACHERS = {
    "qwen3.8-max": ("qwen3.8-max", True),
    "qwen3.7-max": ("qwen3.7-max", True),
    "qwen3-235b": ("qwen3-235b-a22b", True),
    "qwen3-30b": ("qwen3-30b-a3b", True),
    "qwen3-coder": ("qwen3-coder-480b-a35b-instruct", True),
    "deepseek-pro": ("deepseek-v4-pro", True),
    "deepseek-r2": ("deepseek-r2", True),
    "deepseek-r1": ("deepseek-r1-0528", True),
    # the expanded council's new dimensions (r: new open families, code, vision)
    "glm-5.3": ("glm-5.3", True),
    "glm-5.2": ("glm-5.2", True),
    "kimi-k3": ("kimi-k3", True),
    "kimi-k2.7-code": ("kimi-k2.7-code", True),
    "minimax-m3": ("minimax-m3", True),
    "minimax-m2.7": ("minimax-m2.7", True),
    "mimo-v2.5": ("mimo-v2.5", True),
    "deepseek-chat": ("deepseek-chat", True),
    "qwen3-vl-235b": ("qwen3-vl-235b-a22b", True),
    # the fast frontier judge — the council's one closed-weight exception
    "claude-haiku": ("claude-haiku-4-5-20251001", False),
}

# the council in deliberation order — the geometric-mean softmax consensus
# is taken over exactly these eight elders.
COUNCIL = ["qwen3.8-max", "qwen3.7-max", "qwen3-235b", "qwen3-30b",
           "qwen3-coder", "deepseek-pro", "deepseek-r2", "deepseek-r1"]

# the expanded council — the original eight plus the five new dimensions:
# three new open families (Zhipu, Moonshot, MiniMax), a code specialist,
# and the first vision elder. The consensus hears disagreements it never
# heard and sees what it never saw.
EXTENDED = ["qwen3.8-max", "qwen3.7-max", "qwen3-235b", "qwen3-30b",
            "qwen3-coder", "deepseek-pro", "deepseek-r2", "deepseek-r1",
            "glm-5.3", "glm-5.2", "kimi-k3", "kimi-k2.7-code",
            "minimax-m3", "minimax-m2.7", "mimo-v2.5", "deepseek-chat",
            "qwen3-vl-235b", "claude-haiku"]


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
    ap.add_argument("--council", action="store_true", help="run all eight elders in deliberation order")
    ap.add_argument("--extended", action="store_true", help="run the expanded thirteen-voice council")
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--file", default=None, help="read the prompt from a file")
    ap.add_argument("-n", "--count", type=int, default=1, help="how many teacher calls per elder")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=0.7)
    args = ap.parse_args()

    if args.file:
        with open(args.file) as f:
            prompt = f.read()
    else:
        prompt = args.prompt or "What is the geometric-mean softmax consensus, and why does a council of elders prefer it over a majority vote?"

    elders = EXTENDED if args.extended else (COUNCIL if args.council else [args.teacher])
    print(f"cometapi council — {len(elders)} elders · {', '.join(elders)}")
    total_in, total_out, total_s = 0, 0, 0.0
    for elder in elders:
        model, thinking = TEACHERS[elder]
        print(f"\n· {elder} ({model})" + (" · MAX thinking" if thinking else ""))
        for i in range(args.count):
            r = teacher_call(model, prompt, args.max_tokens, args.temperature)
            if r["reasoning"]:
                print(f"\n  [{i+1}] reasoning ({len(r['reasoning'])} chars)")
            print(f"\n  [{i+1}] {r['content'].strip()}")
            print(f"  → {r['prompt_tokens']} in / {r['completion_tokens']} out · {r['seconds']:.2f}s")
            total_in += r["prompt_tokens"]
            total_out += r["completion_tokens"]
            total_s += r["seconds"]
    print(f"\ntotals: {total_in} in / {total_out} out · {total_s:.2f}s across {len(elders)} elders")
    return 0


if __name__ == "__main__":
    sys.exit(main())
