"""Exhaustive minimal-support catalogue at k=7 for the fork-tree
family (D49).

Iterates all 5040 pairings pi in S_7, computes every minimal fatal
toggle support, and records features:

  - support size
  - interval count (1 = pair, 2 = two-interval ladder, ...)
  - selected image intervals
  - natural-odd-start parity flag
  - chain-end trigger (P3, P3'), parity-aligned P4 status
  - V6'' classifier verdict
  - V6 (original D36) classifier verdict

The output supports two downstream uses:

  (a) D49 V6'' audit: does V6'' correctly classify every support?
  (b) Support-structure analysis: are minimal supports always cyclic
      ladders of bounded describable type?  How does the total
      clause count grow as a function of k?

Usage:
  uv run python scripts/k7_minimal_support_catalogue.py --out k7_catalogue.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from itertools import permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cyclic_ladder_probe import (  # noqa: E402
    cyclic_ladder_structure,
    predict_cyclic_ladder_minimal_fatal,
)
from rectangle_detachability_probe import minimal_fatal_toggle_sets  # noqa: E402
from v6pp_predictor import predict_v6pp  # noqa: E402


def _intervals_from_images(images: Sequence[int]) -> list[tuple[int, int]] | None:
    """Decompose sorted images into pairs of consecutive integers.

    Returns the list of intervals (a, a+1) if every image is in a
    consecutive pair; otherwise None.  The intervals must be disjoint
    with min(I_{j+1}) > max(I_j) + 1.
    """
    if len(images) % 2 != 0:
        return None
    images = sorted(images)
    intervals = []
    i = 0
    while i < len(images):
        if i + 1 >= len(images) or images[i + 1] - images[i] != 1:
            return None
        intervals.append((images[i], images[i + 1]))
        i += 2
    # Check disjoint with gap > 0.
    for a, b in zip(intervals, intervals[1:]):
        if b[0] <= a[1] + 1:
            return None
    return intervals


def classify_support(k: int, pi: Sequence[int], S: Sequence[int]) -> dict:
    """Compute features for a minimal fatal support."""
    S = tuple(sorted(S))
    pi_S = sorted(pi[i] for i in S)
    intervals = _intervals_from_images(pi_S)
    interval_count = len(intervals) if intervals else None
    natural_odd_start = (
        all(iv[0] % 2 == 1 for iv in intervals) if intervals else False
    )

    # Try V5 (P3/P3') chain-end trigger (size >= 4 only).
    chain_end = predict_cyclic_ladder_minimal_fatal(k, pi, S)
    v5_label = chain_end["prediction"]
    v5_reason = chain_end.get("reason", "")

    # V6'' unified predictor handles all sizes >= 2.
    v6pp = predict_v6pp(k, pi, S)
    v6pp_prediction = v6pp["prediction"]
    v6pp_reason = v6pp.get("reason", "")

    return {
        "support": list(S),
        "size": len(S),
        "image_set": pi_S,
        "intervals": [list(iv) for iv in intervals] if intervals else None,
        "interval_count": interval_count,
        "natural_odd_start": natural_odd_start,
        "v5_label": v5_label,
        "v5_reason": v5_reason,
        "v6pp_prediction": v6pp_prediction,
        "v6pp_reason": v6pp_reason,
    }


def catalogue_pi(k: int, pi: Sequence[int]) -> dict:
    """All minimal fatal supports of one pairing with classification."""
    supports = minimal_fatal_toggle_sets(k, pi)
    classified = [classify_support(k, pi, S) for S in supports]
    return {
        "pi": list(pi),
        "num_minimal_supports": len(supports),
        "supports": classified,
    }


def full_catalogue(k: int) -> dict:
    """Iterate all pairings of S_k."""
    pairings = []
    max_supports = 0
    max_supports_pi = None
    size_histogram: Counter = Counter()
    v6pp_mismatches: list[dict] = []
    total_supports = 0

    for pi in permutations(range(k)):
        out = catalogue_pi(k, pi)
        if out["num_minimal_supports"] > max_supports:
            max_supports = out["num_minimal_supports"]
            max_supports_pi = list(pi)
        total_supports += out["num_minimal_supports"]
        for s in out["supports"]:
            size_histogram[s["size"]] += 1
            if s["v6pp_prediction"] != "minimal_fatal":
                v6pp_mismatches.append({
                    "pi": list(pi),
                    "support": s["support"],
                    "intervals": s["intervals"],
                    "natural_odd_start": s["natural_odd_start"],
                    "v5_reason": s["v5_reason"],
                    "v6pp_reason": s["v6pp_reason"],
                })
        pairings.append(out)

    return {
        "k": k,
        "total_pairings": len(pairings),
        "total_minimal_supports": total_supports,
        "size_histogram": dict(size_histogram),
        "max_supports_per_pairing": max_supports,
        "max_supports_pi": max_supports_pi,
        "v6pp_mismatches": v6pp_mismatches,
        "num_v6pp_mismatches": len(v6pp_mismatches),
        "pairings": pairings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--summary-only", action="store_true",
                        help="omit per-pairing details from output")
    args = parser.parse_args()

    cat = full_catalogue(args.k)
    if args.summary_only:
        cat_out = {kk: vv for kk, vv in cat.items() if kk != "pairings"}
    else:
        cat_out = cat
    text = json.dumps(cat_out, indent=2, default=list)
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
