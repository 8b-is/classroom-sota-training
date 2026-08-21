#!/usr/bin/env python3
"""
add_cometapi_card.py — add the CometAPI infrastructure block to HF model and
dataset cards. Idempotent: if the block is already present, it is left
untouched. Uses the v2 commit API so the whole README is written atomically.

Usage:
  export HF_TOKEN=...
  python scripts/add_cometapi_card.py PeetPedro/qwen2.5-coder-32b-heretic-swe-sft ...
  python scripts/add_cometapi_card.py --all-core   # the core teacher set
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

# Emery's agreed card block: a plain markdown section.
BLOCK = """## Infrastructure

Model API provider: [CometAPI](https://www.cometapi.com/)
Usage: Teacher-model inference / evaluation
Models: Qwen / DeepSeek
API: OpenAI-compatible
"""

CORE_MODELS = [
    "PeetPedro/qwen2.5-coder-32b-heretic-swe-sft",
    "PeetPedro/gpt-oss-120b-heretic",
    "PeetPedro/Qwen3-30B-A3B-Agentic-ToolCaller",
    "PeetPedro/anonymus-1bit-gpt",
    "PeetPedro/kompress-v17",
    "PeetPedro/unit",
    "PeetPedro/ultrawhale-dogfood",
]


def read_card(repo_id: str, token: str) -> str:
    req = urllib.request.Request(
        f"https://huggingface.co/{repo_id}/raw/main/README.md",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise


def commit_card(repo_id: str, token: str, content: str, title: str) -> None:
    from huggingface_hub import upload_file

    upload_file(
        path_or_fileobj=content.encode(),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
        token=token,
        commit_message=title,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="add the CometAPI infra block to HF cards")
    ap.add_argument("repos", nargs="*", help="HF repo ids")
    ap.add_argument("--all-core", action="store_true", help="patch the core teacher set")
    args = ap.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("HF_TOKEN is not set")
    repos = CORE_MODELS if args.all_core else args.repos
    if not repos:
        sys.exit("give repos, or --all-core")

    for repo_id in repos:
        card = read_card(repo_id, token)
        if "Model API provider: [CometAPI]" in card:
            print(f"· {repo_id}: already has the CometAPI block — skipped")
            continue
        new = card.rstrip() + "\n\n---\n\n" + BLOCK if card else BLOCK
        commit_card(repo_id, token, new, "docs: CometAPI infrastructure block")
        print(f"· {repo_id}: CometAPI block added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
