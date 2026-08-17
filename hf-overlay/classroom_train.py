# /// script
# requires-python = ">=3.10"
# dependencies = ["mlx[cuda12]==0.30.0", "mlx-cuda==0.30.0", "mlx-lm==0.30.0",
#                 "numpy", "safetensors"]
# ///

"""H200 classroom-training job — ring-of-teachers (Qwen3-8B + Qwen3-14B)
logits-KL distillation of the 1.7B ternary student, resuming from the best
single-teacher checkpoint. Runs train_quantal_classroom.py (the multi-faculty
extension) with both faculty caches mounted; checkpoints + curve to the rw
bucket so a job restart never loses state.

Run (mirrors h200_train.py):
  hf jobs uv run --flavor h200 --timeout 48h --secrets HF_TOKEN \
      -v hf://datasets/PeetPedro/quantal-mlx-overlay:/overlay \
      -v hf://buckets/PeetPedro/quantal-train-assets:/assets:rw \
      -e OVERLAY=/overlay -e ASSETS=/assets -e UV_PRERELEASE=allow \
      classroom_train.py
"""
import os
import shutil
import subprocess
import sys
import tarfile

OVERLAY = os.environ.get("OVERLAY", "/overlay")
ASSETS = os.environ.get("ASSETS", "/assets")


def setup_env():
    # NOTE: no 8b-is/transformers fork install here. The fork's current main
    # (4.58.0.post2) imports torch in transformers/__init__ and the HF job
    # image has no torch. The classroom script loads the student via
    # mlx_lm.utils.load, which works fine with the stock transformers that
    # mlx-lm 0.30.0 pins (==5.0.0rc1). The fork is our sovereign home base for
    # export/integration work — it is not required to RUN this training.

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
        print("[classroom] extracting CUDA headers...", flush=True)
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
    print("[classroom] synthetic CUDA_HOME ready", flush=True)


def fetch(name, work):
    src = os.path.join(ASSETS, name)
    dst = os.path.join(work, name)
    if not os.path.exists(dst):
        print(f"[classroom] copying {src} -> {dst}", flush=True)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return dst


def main():
    setup_env()

    work = "/tmp/train-inputs"
    os.makedirs(work, exist_ok=True)

    # corpus to local (rw bucket reads are flaky in-job)
    corpus = fetch("train_ultra_qwen3_v2.jsonl", work)
    # resume from the BEST checkpoint of the running v2 single-teacher H200 run
    # if present, else fall back to the archived 2.1369 best.
    v2_best = os.path.join(ASSETS, "ckpts-h200", "quantal-long-best.safetensors")
    if os.path.exists(v2_best):
        print("[classroom] resume from v2 run best", flush=True)
        resume = fetch("ckpts-h200/quantal-long-best.safetensors", work)
    else:
        print("[classroom] resume from archived 2.1369 best", flush=True)
        resume = fetch("quantal-best-2.1369.safetensors", work)

    # faculty cache 1: Qwen3-8B (tar in bucket) -> /tmp/teacher_logits_v2
    cache8_dir = "/tmp/teacher_logits_v2"
    if not os.path.isdir(cache8_dir):
        tar = os.path.join(ASSETS, "teacher_logits_v2.tar")
        print(f"[classroom] extracting {tar}...", flush=True)
        with tarfile.open(tar, "r") as tf:
            tf.extractall("/tmp")
        print(f"[classroom] cache8 files: {len(os.listdir(cache8_dir))}", flush=True)

    # faculty cache 2: Qwen3-14B — copy the tar from the model repo mount to
    # the job's LOCAL disk first (tarfile streaming off the /repo mount
    # produced truncated/duplicated extraction), then extract locally.
    cache14_dir = "/tmp/qwen3-14b"
    if not os.path.isdir(cache14_dir):
        tar_src = "/repo/classroom/qwen3-14b.tar"
        tar_local = "/tmp/qwen3-14b.tar"
        if not os.path.exists(tar_local):
            print(f"[classroom] copying {tar_src} -> {tar_local}", flush=True)
            shutil.copy2(tar_src, tar_local)
        sz = os.path.getsize(tar_local)
        print(f"[classroom] local tar size: {sz}", flush=True)
        with tarfile.open(tar_local, "r") as tf:
            tf.extractall("/tmp")
        print(f"[classroom] cache14 files: {len(os.listdir(cache14_dir))}", flush=True)

    for p in (corpus, resume, cache8_dir, cache14_dir):
        if not os.path.exists(p):
            print(f"[classroom] FAIL: missing {p}", flush=True)
            sys.exit(1)

    outdir = os.path.join(ASSETS, "ckpts-classroom")
    curve = os.path.join(ASSETS, "curve-classroom.jsonl")
    os.makedirs(outdir, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{OVERLAY}:{OVERLAY}/scripts"
    env["MLX_CUDA_GRAPH_CACHE_SIZE"] = os.environ.get("MLX_CUDA_GRAPH_CACHE_SIZE", "1000")

    cmd = [
        sys.executable, f"{OVERLAY}/scripts/train_quantal_classroom.py",
        "--model", "Qwen/Qwen3-1.7B",
        "--data", corpus,
        "--faculty-dirs", cache8_dir, cache14_dir,
        "--faculty-weight", "0.5",
        "--ce-weight", "0.5",
        "--beta-ramp-epochs", "2",
        "--batch-size", "8",
        "--max-len", "256",
        "--epochs", "40",
        "--lr-init", "1e-4",
        "--lr-end", "1e-5",
        "--grad-clip", "1.0",
        "--val-size", "90",
        "--seed", "42",
        "--outdir", outdir,
        "--curve", curve,
        "--resume", resume,
        "--deployed-forward",
    ]
    print("[classroom] training:", " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, env=env).returncode
    print(f"[classroom] exit {rc}", flush=True)
    sys.exit(rc)


if __name__ == "__main__":
    main()
