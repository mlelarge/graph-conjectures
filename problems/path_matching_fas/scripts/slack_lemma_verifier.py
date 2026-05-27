r"""Empirical verifier for the Mixed-Parity Slack Lemma (D57).

Given a V6''-negative cyclic-ladder core C on a fork-tree pairing pi
at size k, identify a "slack pair" (u, v) of B-chain vertices such
that:

  (S1) u and v are flex-related (their reversed arc creates a chain
       backedge); concretely, {u, v} = {B_{2a}, B_{2a+1}} for some
       even-start interval I_t = {2a, 2a+1} of pi(C).
  (S2) Their score windows overlap by >= 1 position, so an FF-valid
       LFO can place them in either order.
  (S3) At least one ordering (u, v) avoids loading the chain backedge
       B_{2a+1} -> B_{2a}; specifically, placing B_{2a+1} BEFORE B_{2a}
       prevents that chain link from loading.

Strategy.

  - C is a cyclic-ladder core means C is a union of full blocks of
    even-adjacent type (NF1), pi(C) decomposes into adjacent 2-pairs
    (NF2), and the block/interval incidence is a simple cycle (NF3).
  - "No V6'' trigger" means: no P3, no (P3' AND NaturalOddStart), and
    EITHER m < 2 OR not NaturalOddStart.  By 55.2, since the lemma is
    relevant for m >= 2, this forces NOT NaturalOddStart -- i.e. at
    least one interval I_t = {2a, 2a+1} has even lower endpoint 2a.
  - That interval is the "parity break" of C.  Its two B-side images
    are B_{2a}, B_{2a+1}, our slack pair.
  - The score-window arithmetic of D29 forces the windows
    I(B_{2a}) = [3k + 2a - 1, 3k + 2a + 3]  (for 2a < k-1)
    I(B_{2a+1}) = [3k + 2a, 3k + 2a + 4]    (for 2a+1 < k-1)
  i.e. they overlap on the 4-position interval [3k+2a, 3k+2a+3].
  - Both orderings (B_{2a}, B_{2a+1}) and (B_{2a+1}, B_{2a}) respect
    the window constraint, since their intersection has length >= 2.
  - In the order B_{2a+1} BEFORE B_{2a} (LFO sense), the chain backedge
    B_{2a+1} -> B_{2a} does NOT load.

Verifier.

  For each k in {4, ..., kmax}, enumerate every V6''-negative
  cyclic-ladder core C across all pairings pi, identify the slack
  pair, confirm S2 (overlap) and S3 (existence of a swap order).
  If any C has no even-start interval, that is a counterexample to
  the lemma -- report it.

Usage:
  uv run python scripts/slack_lemma_verifier.py --kmax 6
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fork_tree_probe import fork_tree_tournament  # noqa: E402
from lfo_score_window import score_windows, indegrees  # noqa: E402
from normal_form_verifier import (  # noqa: E402
    verify_NF1_block_union,
    verify_NF2_adjacent_pairs,
    verify_NF3_incidence_cycle,
)
from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from v6pp_predictor import _intervals_from_images, predict_v6pp  # noqa: E402


def is_cyclic_ladder_core(k: int, pi: Sequence[int], C: Sequence[int]) -> bool:
    if len(C) == 0:
        return False
    return (
        verify_NF1_block_union(k, C)
        and verify_NF2_adjacent_pairs(pi, C)
        and verify_NF3_incidence_cycle(pi, C)
    )


def b_vertex(k: int, j: int) -> int:
    """Index of B_j inside fork_tree_tournament(k, ...)."""
    return 3 * k + 2 + j


def find_slack_pair(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
) -> dict | None:
    """Identify the slack pair (u, v) = (B_{2a}, B_{2a+1}) for some
    even-start interval I_t = {2a, 2a+1} of pi(C).

    Returns a dict with keys:
      "interval"   -- (2a, 2a+1)
      "u", "v"     -- vertex indices of B_{2a}, B_{2a+1}
      "win_u", "win_v" -- their score windows
      "overlap"    -- (lo, hi) intersection
      "overlap_len"-- length of overlap (>=1 required for S2)
      "swap_legal" -- True if both orderings respect the windows
    Returns None if no even-start interval exists.
    """
    pi_C = sorted(pi[i] for i in C)
    intervals = _intervals_from_images(pi_C)
    if intervals is None:
        return None

    # Find even-start interval.
    even_start = None
    for iv in intervals:
        if iv[0] % 2 == 0:
            even_start = iv
            break
    if even_start is None:
        return None

    a2, a2p1 = even_start  # a2 = 2a, a2p1 = 2a+1
    # The B-vertices for these images are B_{2a}, B_{2a+1}.
    T = fork_tree_tournament(k, pi)
    win = score_windows(T)
    u = b_vertex(k, a2)
    v = b_vertex(k, a2p1)
    win_u = win[u]
    win_v = win[v]
    olo = max(win_u[0], win_v[0])
    ohi = min(win_u[1], win_v[1])
    overlap_len = max(0, ohi - olo + 1)
    swap_legal = overlap_len >= 2  # need to place both inside intersection

    return {
        "interval": list(even_start),
        "u": u,
        "v": v,
        "u_label": f"B_{a2}",
        "v_label": f"B_{a2p1}",
        "win_u": list(win_u),
        "win_v": list(win_v),
        "overlap": [olo, ohi],
        "overlap_len": overlap_len,
        "swap_legal": swap_legal,
    }


def verify_lemma_at_k(k: int, verbose: bool = False) -> dict:
    """Sweep all V6''-negative cyclic-ladder cores at size k."""
    blocks = even_adjacent_blocks(k)
    total = 0
    with_slack = 0
    missing_slack: list[dict] = []
    bad_overlap: list[dict] = []
    examples: list[dict] = []

    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                pred = predict_v6pp(k, pi, C)
                if pred["prediction"] != "not_minimal_fatal":
                    continue
                # V6''-negative cyclic-ladder core.
                # Lemma scope: m >= 2 (multi-interval).  m=1 falls
                # under the F1 base case (Section 55.2).
                intervals = pred["intervals"]
                if len(intervals) < 2:
                    continue
                total += 1
                slack = find_slack_pair(k, pi, C)
                if slack is None:
                    # No even-start interval -- counterexample.
                    missing_slack.append({
                        "k": k,
                        "pi": list(pi),
                        "C": list(C),
                        "intervals": intervals,
                    })
                    continue
                if not slack["swap_legal"]:
                    bad_overlap.append({
                        "k": k,
                        "pi": list(pi),
                        "C": list(C),
                        "slack": slack,
                    })
                    continue
                with_slack += 1
                if verbose and len(examples) < 5:
                    examples.append({
                        "k": k,
                        "pi": list(pi),
                        "C": list(C),
                        "intervals": intervals,
                        "slack": slack,
                    })

    return {
        "k": k,
        "total_v6pp_negative_multi_interval_cores": total,
        "with_slack_pair": with_slack,
        "missing_slack_counterexamples": len(missing_slack),
        "bad_overlap_counterexamples": len(bad_overlap),
        "first_missing_slack": missing_slack[:3],
        "first_bad_overlap": bad_overlap[:3],
        "lemma_holds": (len(missing_slack) == 0 and len(bad_overlap) == 0),
        "examples": examples[:5],
    }


# -------------------------------------------------------------------
# Converse: NaturalOddStart cyclic ladders admit NO slack pair.
# -------------------------------------------------------------------

def verify_natural_odd_start_converse_at_k(k: int) -> dict:
    """For NaturalOddStart V6''-positive cores (P4 case): confirm NO
    even-start interval exists in any decomposition.

    By definition, NaturalOddStart means every interval has odd lower
    endpoint.  Hence find_slack_pair returns None.  This is the
    rigidity that makes P4 fire.
    """
    blocks = even_adjacent_blocks(k)
    total_p4 = 0
    rigid = 0
    surprise: list[dict] = []
    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                pred = predict_v6pp(k, pi, C)
                if pred.get("reason") != "P4_natural_odd_start_residual":
                    continue
                total_p4 += 1
                slack = find_slack_pair(k, pi, C)
                if slack is None:
                    rigid += 1
                else:
                    surprise.append({
                        "k": k,
                        "pi": list(pi),
                        "C": list(C),
                        "slack": slack,
                    })
    return {
        "k": k,
        "total_natural_odd_start_cores": total_p4,
        "rigid_no_slack": rigid,
        "unexpected_slack": len(surprise),
        "converse_holds": (len(surprise) == 0),
        "first_surprise": surprise[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--kmax", type=int, default=6)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--converse", action="store_true",
                        help="Also run the NaturalOddStart converse check.")
    args = parser.parse_args()
    ks = [args.k] if args.k is not None else list(range(4, args.kmax + 1))
    out = {}
    for k in ks:
        out[f"k={k}"] = verify_lemma_at_k(k, verbose=args.verbose)
        if args.converse:
            out[f"k={k}_converse"] = verify_natural_odd_start_converse_at_k(k)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
