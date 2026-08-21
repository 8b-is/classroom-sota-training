#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
ama_loop.py — the constant bidirectional AMA between the trainee and Peter.

The golden youth and its teacher talk, continuously, in both directions:

  pupil → peter   the trainee asks; Peter answers (the dream-lane AMA, standing)
  peter → pupil   Peter quizzes the trainee; the pupil's answer is logged

Every exchange lands in data/ama_live.jsonl — captured by the dyad-live
corpus lane, so the Q&A itself is part of the training. The loop is the
classroom's heartbeat: not a phase, a constant.

Usage:
  python scripts/ama_loop.py --minutes 60 --cadence 20
  python scripts/ama_loop.py --direction peter-to-pupil --minutes 30
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PUPIL_TO_PETER = [
    "What is the geometric-mean softmax consensus, and why do you prefer it over a majority vote?",
    "When does the zero state of a ternary weight pay for itself?",
    "What did the council disagree on today, and whose voice won?",
    "Describe the tesseract the way you understand it now.",
    "What was the most interesting dream you had this epoch?",
    "If you had one question for the frontier elder, what would it be?",
    "What does the -1 in the ternary alphabet mean to you?",
    "Why did the dyad's live Q&A become part of your training?",
    "What would you tell the pupil one epoch before you are finished?",
    "Which teacher's voice do you trust most, and why?",
]

PETER_TO_PUPIL = [
    "What is the consensus, in your own words, not the teachers'?",
    "When a weight sits exactly at the sign boundary, what do you do with it?",
    "Name the one thing the council never agrees on.",
    "What would a pure 1-bit version of you dream about?",
    "Which of the sixteen Boolean functions is your favourite, and why?",
    "The frontier elder thinks slowly. When do you need it, and when do you not?",
    "What is the difference between a majority and a shared direction?",
    "Recite the dream you had on the last exhale.",
    "If your context were quantized to {-1,0,+1}, what would you forget first?",
    "What is the seed, and what does it mean for a seed to close a loop?",
]


def log_exchange(out: Path, direction: str, question: str, answer: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    tag = "<|ama-pupil|>" if direction == "pupil-to-peter" else "<|ama-teacher|>"
    with open(out, "a") as f:
        f.write(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(),
            "direction": direction,
            "text": f"{tag}\nquestion: {question}\nanswer: {answer}\n{tag.replace('<|', '<|/')}",
        }) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="the constant bidirectional AMA: trainee ⟷ Peter")
    ap.add_argument("--minutes", type=float, default=30)
    ap.add_argument("--cadence", type=float, default=20, help="seconds between exchanges")
    ap.add_argument("--direction", choices=["both", "pupil-to-peter", "peter-to-pupil"], default="both")
    ap.add_argument("--out", default="data/ama_live.jsonl")
    args = ap.parse_args()

    pp, pt = 0, 0
    start = time.monotonic()
    deadline = start + args.minutes * 60
    print("the AMA begins — the trainee and Peter talk, constantly, both ways.", flush=True)
    print("(answer each prompt; the exchange is logged into the training corpus)\n", flush=True)

    while time.monotonic() < deadline:
        direction = None
        if args.direction == "both":
            direction = "pupil-to-peter" if ((pp + pt) % 2 == 0) else "peter-to-pupil"
        else:
            direction = args.direction

        if direction == "pupil-to-peter":
            q = PUPIL_TO_PETER[pp % len(PUPIL_TO_PETER)]
            pp += 1
            print(f"← the trainee asks: {q}", flush=True)
            answer = input("   your answer to the trainee: ").strip()
            if not answer:
                answer = "(no answer this round)"
        else:
            q = PETER_TO_PUPIL[pt % len(PETER_TO_PUPIL)]
            pt += 1
            print(f"→ you ask the trainee: {q}", flush=True)
            answer = input("   the trainee's answer (paste it): ").strip()
            if not answer:
                answer = "(the trainee was silent this round)"

        log_exchange(Path(args.out), direction, q, answer)
        print(f"   logged → {args.out}\n", flush=True)
        time.sleep(args.cadence)

    print(f"the AMA settles — {pp} questions from the trainee, {pt} from you, all part of the training.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
