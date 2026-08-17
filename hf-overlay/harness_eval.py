# /// script
# requires-python = ">=3.10"
# dependencies = ["mlx[cuda12]==0.30.0", "mlx-cuda==0.30.0", "mlx-lm==0.30.0",
#                 "numpy", "safetensors"]
# ///

"""Harness gate: evaluate the ARCHIVED 2.1369 checkpoint (old-stack KL best)
under the NEW stack — same deployed_forward=True, same threshold rule, same
held-out split (seed 42), same val 90. Dipankar r10's one-line test.

If val comes back ≈2.1369 → the gap is training (H200 runs are real).
If val comes back ≈2.0x  → the gap is harness (nothing beaten yet).

Run (mirrors the training wrappers; no fork install needed — mlx_lm uses the
stock transformers mlx-lm pins):
  hf jobs uv run --flavor h200 --timeout 2h --secrets HF_TOKEN \
      -v hf://datasets/PeetPedro/quantal-mlx-overlay:/overlay \
      -v hf://buckets/PeetPedro/quantal-train-assets:/assets:rw \
      -e OVERLAY=/overlay -e ASSETS=/assets -e UV_PRERELEASE=allow \
      harness_eval.py
"""
import os
import shutil
import subprocess
import sys
import tarfile

OVERLAY = os.environ.get("OVERLAY", "/overlay")
ASSETS = os.environ.get("ASSETS", "/assets")


def setup_env():
    import glob
    import site

    nvidia_libs, nvidia_incs = [], []
    for sp in site.getsitepackages():
        nvidia_libs += glob.glob(f"{sp}/nvidia/*/lib") + glob.glob(f"{sp}/nvidia/*/lib/*")
        nvidia_incs += glob.glob(f"{sp}/nvidia/*/include")
    lib64 = "/tmp/cuda/lib64"
    os.makedirs(lib64, exist_ok=True)
    for d in nvidia_libs:
        if os.path.isdir(d):
            for so in glob.glob(os.path.join(d, "*.so*")):
                dst = os.path.join(lib64, os.path.basename(so))
                if not os.path.exists(dst):
                    try:
                        os.symlink(so, dst)
                    except OSError:
                        pass
    inc_dir = "/tmp/cuda/include"
    os.makedirs(inc_dir, exist_ok=True)
    cuda_inc_tar = os.path.join(ASSETS, "cuda-include.tar")
    if os.path.exists(cuda_inc_tar) and not os.path.exists(os.path.join(inc_dir, "cuda_bf16.h")):
        with tarfile.open(cuda_inc_tar, "r") as tf:
            tf.extractall("/tmp/cuda", filter="data")
    if not os.path.exists(os.path.join(inc_dir, "nv", "target")):
        src = os.path.join(OVERLAY, "include", "nv", "target")
        if os.path.exists(src):
            os.makedirs(os.path.join(inc_dir, "nv"), exist_ok=True)
            try:
                os.symlink(src, os.path.join(inc_dir, "nv", "target"))
            except OSError:
                pass
    os.environ["CUDA_HOME"] = "/tmp/cuda"
    os.environ["CUDA_PATH"] = "/tmp/cuda"
    os.environ["LD_LIBRARY_PATH"] = lib64 + ":" + os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["MLX_CUDA_GRAPH_CACHE_SIZE"] = "1000"
    print("[eval] synthetic CUDA_HOME ready", flush=True)


def main():
    setup_env()

    # inputs -> local
    work = "/tmp/train-inputs"
    os.makedirs(work, exist_ok=True)

    def fetch(name):
        src = os.path.join(ASSETS, name)
        dst = os.path.join(work, name)
        if not os.path.exists(dst):
            print(f"[eval] copying {src} -> {dst}", flush=True)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        return dst

    corpus = fetch("train_ultra_qwen3_v2.jsonl")
    ckpt = fetch("quantal-best-2.1369.safetensors")
    cache_dir = "/tmp/teacher_logits_v2"
    if not os.path.isdir(cache_dir):
        tar = os.path.join(ASSETS, "teacher_logits_v2.tar")
        print(f"[eval] extracting {tar}...", flush=True)
        with tarfile.open(tar, "r") as tf:
            tf.extractall("/tmp")

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{OVERLAY}:{OVERLAY}/scripts"

    # Use the classroom script's evaluate machinery on the ARCHIVED checkpoint:
    # load base, swap BitLinear (deployed forward), load 2.1369 weights, eval
    # CE + KL on the SAME stratified val 90 (seed 42).
    code = f'''
import sys, os
sys.path.insert(0, {OVERLAY!r}); sys.path.insert(0, {OVERLAY!r} + "/scripts")
import mlx.core as mx, mlx.nn as nn
from train_quantal import replace_linear_with_bitlinear
from mlx.nn.layers.bitlinear import BitLinear
from train_quantal_classroom import (
    load_jsonl, stratified_val_split, load_cache_index, load_faculty,
    make_batch_faculty, ce_loss_masked, kl_loss_faculty,
)
from mlx_lm.utils import load as mlx_load

model, tokenizer = mlx_load("Qwen/Qwen3-1.7B")
tokenizer.pad_token = tokenizer.eos_token
model = replace_linear_with_bitlinear(model, deployed_forward=True)
model.load_weights({ckpt!r})
stud_tok = getattr(tokenizer, "vocab_size", None)
faculty_indices, _ = load_faculty([{cache_dir!r}], 64, stud_tok)
samples = load_jsonl({corpus!r})
_, val_samples = stratified_val_split(samples, tokenizer, 90, 42)
total_ce, total_kl, n, n_kl = 0.0, 0.0, 0, 0
for i in range(0, len(val_samples), 8):
    b = make_batch_faculty(tokenizer, val_samples[i:i+8], 256, faculty_indices, 64)
    if b is None: continue
    inputs, targets, mask, fb, _ = b
    logits = model(inputs)
    ce = ce_loss_masked(logits, targets, mask)
    total_ce += ce.item(); n += 1
    if fb is not None:
        kl = kl_loss_faculty(logits, fb, mask)
        if kl is not None:
            total_kl += kl.item(); n_kl += 1
print(f"HARNESS_VAL_CE={{total_ce/max(1,n):.4f}}")
print(f"HARNESS_VAL_KL={{total_kl/max(1,n_kl) if n_kl else 'None'}}")
print("HARNESS_DONE")
'''
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    print(r.stdout[-2000:])
    if r.stderr:
        print("STDERR:", r.stderr[-1000:])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
