"""Test the visible-latent signature on cut-isolated sums of the
component witness, the family that originally exhibited 2^k entropy
under the (placed_set, degree_vector) quotient.

The entropy family was constructed without score-window awareness. The
forced/flexible decomposition + score-window normalization changes the
state space. Two specific questions:

  Q1. Is the cut-isolated sum at k>=2 even score-window-feasible (under
      the LFO radius-2 windows)?

  Q2. If feasible, does the visible-latent signature still collide on
      the good^k extendable pattern vs the mixed non-extendable
      patterns, at any cut?

If the answer to Q1 is "no" for k>=K_0, the original 2^k entropy lower
bound does not apply to the forced/flexible DP, and visible-latent
remains a plausible final state.

If the answer to Q2 is "yes" at some cut, we have a concrete
counterexample to visible-latent sufficiency, and the DP needs further
augmentation (forced-future ports).
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import hall_interval_ok, score_windows  # noqa: E402
from pending_state_probe import (  # noqa: E402
    COMPONENT_PREFIX_BAD,
    COMPONENT_PREFIX_GOOD,
    COMPONENT_PREFIX_SET,
    COMPONENT_WITNESS_T,
    cut_isolated_sum,
)
from ff_signature_probe import (  # noqa: E402
    has_completion_ff,
    valid_prefix_state_ff,
    visible_latent_signature,
)


Matrix = list[list[int]]


def good_bad_prefix(pattern: Sequence[str]) -> list[int]:
    """Build a global prefix from a good/bad pattern over k witness copies."""
    block = len(COMPONENT_WITNESS_T)
    out: list[int] = []
    for c, tag in enumerate(pattern):
        if tag == "good":
            local = COMPONENT_PREFIX_GOOD
        elif tag == "bad":
            local = COMPONENT_PREFIX_BAD
        else:
            raise ValueError("pattern entries must be 'good' or 'bad'")
        out.extend(c * block + v for v in local)
    return out


def question_one_hall_feasibility(k: int) -> dict:
    """Q1: is the cut-isolated sum at k copies Hall-feasible?"""
    T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, k)
    n = len(T)
    windows = score_windows(T)
    feasible = hall_interval_ok((1 << n) - 1, 0, windows, n)
    return {
        "k": k,
        "n": n,
        "hall_feasible": feasible,
        "indegrees": [sum(row) for row in zip(*[
            [T[u][v] for v in range(n)] for u in range(n)
        ])],
        "windows": windows,
    }


def question_two_visible_collision(k: int) -> dict:
    """Q2: among (good/bad)^k patterns, does the visible-latent signature
    collide on patterns with different extendability at any cut depth?

    Strategy: for each pattern, compute the prefix state at each cut
    depth d=1..4k, get the visible-latent signature, and check
    extendability. Look for two patterns with same signature but
    different extendability.
    """
    T = cut_isolated_sum(COMPONENT_WITNESS_T, COMPONENT_PREFIX_SET, k)
    n = len(T)
    windows = score_windows(T)
    if not hall_interval_ok((1 << n) - 1, 0, windows, n):
        return {
            "k": k,
            "n": n,
            "hall_feasible": False,
            "note": "cut-isolated sum is not score-window-feasible at all",
        }

    # For each pattern, build the prefix and check feasibility + extension.
    by_signature: dict[tuple, list[dict]] = {}
    collisions = []
    pattern_results = []
    for bits in itertools.product(["good", "bad"], repeat=k):
        prefix = good_bad_prefix(bits)
        # Try cut depths 1..len(prefix)
        prefix_record = {"pattern": list(bits), "extendability_per_cut": []}
        is_pattern_feasible = True
        for d in range(1, len(prefix) + 1):
            partial = prefix[:d]
            state = valid_prefix_state_ff(T, partial)
            if state is None:
                is_pattern_feasible = False
                prefix_record["extendability_per_cut"].append({
                    "cut": d, "valid_prefix": False,
                })
                break
            prefix_mask, degree, parent, flex_outmask, windows2 = state
            sig = visible_latent_signature(
                d, prefix_mask, degree, parent, flex_outmask, windows2
            )
            ext = has_completion_ff(
                T, d, prefix_mask, degree, parent,
                tuple(flex_outmask), tuple(windows2),
            )
            prefix_record["extendability_per_cut"].append({
                "cut": d, "valid_prefix": True, "extendable": ext,
            })
            key = (d, sig)
            for other in by_signature.get(key, []):
                if other["extendable"] != ext:
                    collisions.append({
                        "cut": d,
                        "pattern_a": other["pattern"],
                        "pattern_b": list(bits),
                        "extendable_a": other["extendable"],
                        "extendable_b": ext,
                    })
            by_signature.setdefault(key, []).append({
                "pattern": list(bits),
                "extendable": ext,
            })
        prefix_record["pattern_feasible"] = is_pattern_feasible
        pattern_results.append(prefix_record)

    return {
        "k": k,
        "n": n,
        "hall_feasible": True,
        "patterns": pattern_results,
        "collisions": collisions,
        "collision_count": len(collisions),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--k", type=int, nargs="+", default=[2, 3],
        help="Numbers of witness copies to test.",
    )
    parser.add_argument(
        "--mode", choices=["q1", "q2", "both"], default="both",
    )
    args = parser.parse_args()

    out = {"results": []}
    for k in args.k:
        if args.mode in ("q1", "both"):
            out.setdefault("q1", []).append(question_one_hall_feasibility(k))
        if args.mode in ("q2", "both"):
            out.setdefault("q2", []).append(question_two_visible_collision(k))
    # Compact summary
    if "q1" in out:
        for entry in out["q1"]:
            print(f"Q1: k={entry['k']}, n={entry['n']}, "
                  f"hall_feasible={entry['hall_feasible']}")
    if "q2" in out:
        for entry in out["q2"]:
            if not entry.get("hall_feasible", False):
                print(f"Q2: k={entry['k']} skipped (not feasible)")
                continue
            patt_feas = sum(1 for p in entry["patterns"] if p.get("pattern_feasible"))
            print(f"Q2: k={entry['k']}, patterns={len(entry['patterns'])}, "
                  f"feasible={patt_feas}, "
                  f"visible-latent collisions={entry['collision_count']}")
            for c in entry["collisions"][:3]:
                print(f"   collision at cut {c['cut']}: "
                      f"{c['pattern_a']} (ext={c['extendable_a']}) vs "
                      f"{c['pattern_b']} (ext={c['extendable_b']})")
    print()
    print(json.dumps(out, indent=2, default=str)[:2000])


if __name__ == "__main__":
    main()
