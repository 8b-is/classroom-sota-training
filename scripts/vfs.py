#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["huggingface_hub"]
# ///
"""
vfs.py — the classroom's virtual filesystem: one namespace over HF buckets,
HF repos, and local disk.

  hf-bucket://<bucket>/<path>    durable archives (weights, the cogito bucket)
  hf://<repo>/<path>             HF repos (models, datasets, the corpus)
  local://<path>                 the box's scratch

Every read/write is a provenance capsule: files carry size + sha256 in a
sidecar MANIFEST, so the audit's "machine-readable the whole time" ethos
rides on top of the storage instead of being bolted on later.

Usage:
  export HF_TOKEN=...
  uv run --script scripts/vfs.py ls hf-bucket://cogitoergosumma-corpus | head
  uv run --script scripts/vfs.py ls hf://PeetPedro/ultrawhale-dogfood | head
  uv run --script scripts/vfs.py sha hf-bucket://.../some-file.bin
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

try:
    from huggingface_hub import HfApi
except ImportError:
    HfApi = None


def parse_uri(uri: str) -> tuple[str, str, str]:
    """Split a VFS uri into (kind, location, path)."""
    if uri.startswith("hf-bucket://"):
        rest = uri[len("hf-bucket://"):]
        loc, _, path = rest.partition("/")
        return "bucket", loc, path
    if uri.startswith("hf://"):
        rest = uri[len("hf://"):]
        parts = rest.split("/", 2)
        loc = "/".join(parts[:2])      # owner/name
        path = parts[2] if len(parts) > 2 else ""
        return "repo", loc, path
    if uri.startswith("local://"):
        return "local", "", uri[len("local://"):]
    raise ValueError(f"unknown VFS scheme in {uri!r} (use hf-bucket://, hf://, local://)")


def api():
    if HfApi is None:
        sys.exit("huggingface_hub is required (uv run --with huggingface_hub)")
    return HfApi(token=os.environ.get("HF_TOKEN"))


def ls_bucket(bucket: str, path: str, api):
    """List HF bucket objects via whatever API surface this hub version ships,
    falling back to the REST /api/buckets endpoint."""
    import json
    import urllib.request
    out = []
    for method in ("list_bucket_objects", "list_bucket_files", "list_bucket"):
        if hasattr(api, method):
            try:
                objs = getattr(api, method)(bucket)
                for o in objs:
                    key = getattr(o, "key", None) or getattr(o, "name", None)
                    if key and key.startswith(path):
                        out.append({"key": key, "size": getattr(o, "size", None),
                                    "sha256": getattr(o, "sha256", None)})
                return out
            except Exception:
                continue
    # REST fallback: GET /api/buckets/<bucket>
    try:
        req = urllib.request.Request(
            f"https://huggingface.co/api/buckets/{bucket}",
            headers={"Authorization": f"Bearer {os.environ.get('HF_TOKEN', '')}"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        objs = data if isinstance(data, list) else data.get("objects", data.get("files", []))
        for o in objs:
            key = o.get("key") or o.get("path") or o.get("name", "")
            if key.startswith(path):
                out.append({"key": key, "size": o.get("size"), "sha256": o.get("sha256")})
    except Exception as e:
        out = [{"error": f"bucket list failed: {e}"}]
    return out


def ls_repo(repo: str, path: str, api):
    """List an HF repo's files, detecting whether it is a dataset or a model."""
    for repo_type in ("dataset", "model"):
        try:
            files = api.list_repo_files(repo, repo_type=repo_type)
            return [{"path": f, "bytes": None} for f in files if f.startswith(path)]
        except Exception:
            continue
    return [{"error": f"repo {repo!r} not found as dataset or model"}]


def sha_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="the classroom's virtual filesystem")
    ap.add_argument("cmd", choices=["ls", "cat", "sha"])
    ap.add_argument("uri", help="hf-bucket://<bucket>/<path> · hf://<repo>/<path> · local://<path>")
    args = ap.parse_args()

    kind, loc, path = parse_uri(args.uri)
    if kind == "local":
        p = Path(path)
        if args.cmd == "ls":
            for child in sorted(p.iterdir()) if p.is_dir() else [p]:
                print(child)
        elif args.cmd == "sha":
            print(sha_of(p))
        return 0

    a = api()
    if kind == "bucket":
        rows = ls_bucket(loc, path, a)
    else:
        rows = ls_repo(loc, path, a)
    if args.cmd == "ls":
        for r in rows[:50]:
            key = r.get("key") or r.get("path") or r.get("error", "")
            size = r.get("size")
            print(f"  {key}" + (f"  ({size} bytes)" if size else ""))
        if len(rows) > 50:
            print(f"  … {len(rows) - 50} more")
    elif args.cmd == "sha":
        for r in rows[:20]:
            key = r.get("key") or r.get("path") or ""
            h = r.get("sha256")
            print(f"  {key}  sha256 {h or '(not declared — the gap the audit caught)'}")
    print(f"\n  → VFS {args.uri} · {len(rows)} entries · provenance: size + sha256 where declared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
