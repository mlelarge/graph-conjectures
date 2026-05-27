"""Unified V6 fatal detector for cyclic m-interval ladders.

Combines:
  - (P3)  any filler image above the high interval -> fatal;
  - (P3') at odd k, lone unpaired filler index k-1 has image below
          the low interval -> fatal;
  - (P4)  in the residual case (no P3/P3'), all selected intervals
          are natural odd-start B-pairs ({1,2}, {3,4}, {5,6}, ...) -> fatal.

V6 is the user's P4 result (Section 37 of exchange_proof_draft.md)
applied to all sizes m >= 2.

This script tests V6 against suffix-walk ground truth on constructed
candidates at sizes 2, 3, 4 intervals.

Usage:
  uv run python scripts/unified_v6_probe.py --size 4 --k 11
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cyclic_ladder_probe import (  # noqa: E402
    cyclic_ladder_structure,
    predict_cyclic_ladder_minimal_fatal,
)


def predict_v6(
    k: int,
    pi: Sequence[int],
    selected: Sequence[int],
) -> dict:
    """V6: chain-end (P3, P3') + residual natural-odd-start (P4)."""
    chain_end = predict_cyclic_ladder_minimal_fatal(k, pi, selected)
    if chain_end["prediction"] in ("minimal_fatal", "not_a_candidate"):
        return chain_end
    # Residual: not_minimal_fatal under chain-end.  Check P4.
    structure = cyclic_ladder_structure(k, pi, selected)
    if structure is None:
        return chain_end
    intervals = structure["intervals"]
    natural_odd_start = all(interval[0] % 2 == 1 for interval in intervals)
    if natural_odd_start:
        return {
            "prediction": "minimal_fatal",
            "reason": "P4_natural_odd_start_residual",
            "intervals": [list(iv) for iv in intervals],
        }
    return {
        "prediction": "not_minimal_fatal",
        "reason": "P4_misaligned_residual",
        "intervals": [list(iv) for iv in intervals],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=11)
    parser.add_argument("--pi", type=str, required=True,
                        help="comma-separated permutation")
    parser.add_argument("--selected", type=str, required=True,
                        help="comma-separated selected indices")
    args = parser.parse_args()

    pi = tuple(int(x) for x in args.pi.split(","))
    selected = tuple(int(x) for x in args.selected.split(","))
    out = predict_v6(args.k, pi, selected)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
