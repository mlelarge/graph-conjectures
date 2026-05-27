"""Empirical characterization of fatal toggle patterns on arbitrary fork pairings.

The Section 21 result for cyclic shift pi(i)=i+1 mod k says: fatal iff
both bits of one of (0,1), (2,3), ..., (2r-2, 2r-1) are selected.  The
structural reading is a Local Alternating-Rectangle Criterion.

This script generalizes: for an arbitrary pairing pi (permutation of
[k]), compute the exact fatal-toggle set via FF and compare to a
candidate criterion.

Candidate (working): for every pair of indices (i, j) with i < j,
the *abstract rectangle* at (i, j) is the 4-cycle

    A_i -- A_j (chain segment) -- B_{pi(j)} (bridge j) --
    B_{pi(i)} (chain segment in B) -- A_i (bridge i).

The rectangle is "local" if:
  (R1) j = i + 1 (A-side adjacent), AND
  (R2) pi(j) and pi(i) are adjacent in B with |pi(j) - pi(i)| = 1.

The rectangle is "fatal" if it is local AND the four boundary edges
all must load in any valid completion.

We test the simpler "local rectangle" criterion as a first cut: a
toggle prefix is non-extendable iff it activates a local rectangle.

If this fails, we refine.

Usage:
  uv run python scripts/alternating_rectangle_probe.py --k 5 \
      --pairings shift1 shift2 random
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from itertools import permutations, product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fork_tree_probe import count_fork_tree_signatures  # noqa: E402


def local_rectangles(pi: Sequence[int]) -> list[tuple[int, int]]:
    """List of (i, j) with j = i+1 and |pi(j) - pi(i)| = 1.

    These are the candidate fatal pairs under the working criterion.
    """
    k = len(pi)
    rects: list[tuple[int, int]] = []
    for i in range(k - 1):
        j = i + 1
        if abs(pi[j] - pi[i]) == 1:
            rects.append((i, j))
    return rects


def candidate_extendable(bits: Sequence[int], rects: Sequence[tuple[int, int]]) -> bool:
    """Predict extendable iff no local rectangle has both bits set."""
    for (i, j) in rects:
        if bits[i] and bits[j]:
            return False
    return True


def evaluate_pairing(k: int, pi: Sequence[int]) -> dict:
    """Run FF on every toggle prefix; compare to candidate criterion."""
    out = count_fork_tree_signatures(k, pi)
    rects = local_rectangles(pi)
    by_bits = out["by_bits"]
    candidate_correct = 0
    candidate_wrong = 0
    candidate_misses: list[dict] = []
    for row in by_bits:
        if row["status"] != "ok":
            continue
        bits = row["bits"]
        actual = row["extendable"]
        predicted = candidate_extendable(bits, rects)
        if predicted == actual:
            candidate_correct += 1
        else:
            candidate_wrong += 1
            if len(candidate_misses) < 6:
                candidate_misses.append({
                    "bits": bits,
                    "predicted": predicted,
                    "actual": actual,
                    "rects": rects,
                })
    return {
        "k": k,
        "pi": list(pi),
        "extendable_actual": out["extendable"],
        "non_extendable_actual": out["non_extendable"],
        "invalid": out["invalid"],
        "local_rectangles": rects,
        "candidate_correct": candidate_correct,
        "candidate_wrong": candidate_wrong,
        "candidate_misses": candidate_misses,
    }


def sweep(
    k: int,
    pairings: Sequence[Sequence[int] | str],
    seed: int = 0,
) -> dict:
    rng = random.Random(seed)
    rows = []
    for tag in pairings:
        if tag == "identity":
            pi = tuple(range(k))
        elif isinstance(tag, str) and tag.startswith("shift"):
            shift = int(tag[5:]) if len(tag) > 5 else 1
            pi = tuple((i + shift) % k for i in range(k))
        elif isinstance(tag, str) and tag.startswith("reverse"):
            pi = tuple(range(k - 1, -1, -1))
        elif isinstance(tag, str) and tag == "random":
            pi = tuple(rng.sample(range(k), k))
        elif isinstance(tag, (list, tuple)):
            pi = tuple(tag)
        else:
            raise ValueError(f"Unknown pairing tag: {tag!r}")
        out = evaluate_pairing(k, pi)
        out["tag"] = tag if isinstance(tag, str) else "explicit"
        rows.append(out)
    return {
        "k": k,
        "seed": seed,
        "results": rows,
    }


def all_pairings_sweep(k: int) -> dict:
    """Evaluate ALL k! pairings at small k for exhaustive coverage."""
    rows = []
    for pi in permutations(range(k)):
        out = evaluate_pairing(k, pi)
        rows.append(out)
    correct_count = sum(1 for r in rows if r["candidate_wrong"] == 0)
    incorrect_count = len(rows) - correct_count
    return {
        "k": k,
        "total_pairings": len(rows),
        "candidate_correct_for_all_bits": correct_count,
        "candidate_wrong_at_least_once": incorrect_count,
        "wrong_examples": [r for r in rows if r["candidate_wrong"] > 0][:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument(
        "--pairings", nargs="*",
        default=["identity", "shift1", "shift2", "shift3", "random"],
    )
    parser.add_argument("--all", action="store_true",
                        help="exhaustively sweep all k! pairings")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    if args.all:
        result = all_pairings_sweep(args.k)
    else:
        result = sweep(args.k, args.pairings, seed=args.seed)
    print(json.dumps(result, indent=2, default=list))


if __name__ == "__main__":
    main()
