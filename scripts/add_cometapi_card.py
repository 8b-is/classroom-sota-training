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

# Emery's agreed card block: a plain markdown section, verbatim.
BLOCK = """## Infrastructure

Model API provider: CometAPI
Usage: Teacher-model inference / evaluation
Models: Qwen / DeepSeek
API: OpenAI-compatible
And you can link CometAPI here: https://www.cometapi.com/
If you end up publishing a lot of models/datasets using it, this simple format is totally fine.
"""

# the marker that decides "already has the block"; older cards carry the
# short form without the link line and get upgraded to the full block.
HAVE_MARKER = "Model API provider: CometAPI"
LINK_MARKER = "link CometAPI here"

CORE_MODELS = [
    "PeetPedro/qwen2.5-coder-32b-heretic-swe-sft",
    "PeetPedro/gpt-oss-120b-heretic",
    "PeetPedro/Qwen3-30B-A3B-Agentic-ToolCaller",
    "PeetPedro/anonymus-1bit-gpt",
    "PeetPedro/kompress-v17",
    "PeetPedro/unit",
    "PeetPedro/ultrawhale-dogfood",
]


def repo_type_of(repo_id: str, token: str) -> str:
    """Resolve whether a repo id is a model or a dataset."""
    for kind in ("models", "datasets"):
        req = urllib.request.Request(
            f"https://huggingface.co/api/{kind}/{repo_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return "model" if kind == "models" else "dataset"
        except urllib.error.HTTPError:
            continue
    return "model"


def read_card(repo_id: str, token: str, repo_type: str = "model") -> str:
    url = f"https://huggingface.co/{repo_type}s/{repo_id}/raw/main/README.md"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise


def commit_card(repo_id: str, token: str, content: str, title: str, repo_type: str = "model") -> None:
    from huggingface_hub import upload_file

    upload_file(
        path_or_fileobj=content.encode(),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type=repo_type,
        token=token,
        commit_message=title,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="add the CometAPI infra block to HF cards")
    ap.add_argument("repos", nargs="*", help="HF repo ids")
    ap.add_argument("--all-core", action="store_true", help="patch the core teacher set")
    ap.add_argument("--all-peetpedro", action="store_true", help="patch every PeetPedro model + dataset card")
    args = ap.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("HF_TOKEN is not set")
    if args.all_peetpedro:
        import urllib.request
        repos = []
        for kind in ("models", "datasets"):
            req = urllib.request.Request(
                f"https://huggingface.co/api/{kind}?author=PeetPedro&limit=200",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                for m in json.load(resp):
                    if m["id"] not in repos:
                        repos.append(m["id"])
    else:
        repos = CORE_MODELS if args.all_core else args.repos
    if not repos:
        sys.exit("give repos, --all-core, or --all-peetpedro")

    for repo_id in repos:
        rtype = repo_type_of(repo_id, token)
        card = read_card(repo_id, token, rtype)
        if HAVE_MARKER in card:
            if LINK_MARKER in card:
                print(f"· {repo_id}: full CometAPI block present — skipped")
                continue
            # old short form: upgrade in place (replace just the infra section)
            import re
            card = re.sub(r"## Infrastructure.*?(?=\n## |\Z)", BLOCK.rstrip() + "\n", card, flags=re.S)
            commit_card(repo_id, token, card, "docs: CometAPI block — full form (link line)", rtype)
            print(f"· {repo_id}: CometAPI block upgraded to full form")
            continue
        new = card.rstrip() + "\n\n---\n\n" + BLOCK if card else BLOCK
        commit_card(repo_id, token, new, "docs: CometAPI infrastructure block", rtype)
        print(f"· {repo_id}: CometAPI block added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
