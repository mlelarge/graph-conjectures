"""Mixed-Parity Escape Lemma constructive verifier (D55).

Lemma (Mixed-Parity Escape).  Let C be a cyclic-ladder core on a
fork-tree pairing pi at size k.  Suppose:

  (E1) C is not NaturalOddStart (at least one interval has even
       lower endpoint);
  (E2) no P3 trigger fires (no filler image > max(I_{m-1}));
  (E3) no P3' trigger fires (either k is even, or the lone filler
       index k-1 is in C, or its image is >= min(I_0)).

Then C is either extendable, or contains a smaller cyclic-ladder
core C' subset C that has a V6'' trigger.

Constructive proof strategy:

  1. Find an even-start interval I_t = {2a, 2a+1} in C's image
     decomposition.
  2. Place the suffix vertices in an order that places B_{2a+1}
     before B_{2a}, breaking the chain link B_{2a+1} -> B_{2a}.
  3. The m-cycle of C's incidence graph loses one chain edge,
     becoming an m-path.  Linear forest constraint preserved.

This module implements the verifier and tests it across all
non-V6''-trigger cyclic-ladder cores at k <= 6.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    _canonical_parent,
    valid_prefix_state_ff,
)
from fork_tree_probe import fork_tree_prefix, fork_tree_tournament  # noqa: E402
from lfo_score_window import hall_interval_ok  # noqa: E402
from lfo_forced_flexible import _forced_future_ok_flexible, _iter_bits  # noqa: E402
from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from v6pp_predictor import _intervals_from_images, predict_v6pp  # noqa: E402
from v6pp_completion_constructor import (  # noqa: E402
    is_cyclic_ladder_core,
    has_no_v6pp_trigger,
)


def find_slack_interval(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
) -> tuple[int, int] | None:
    """Return an even-start interval (a, a+1) with a even, or None."""
    images = sorted({pi[i] for i in C})
    intervals = _intervals_from_images(images)
    if intervals is None:
        return None
    for iv in intervals:
        if iv[0] % 2 == 0:
            return iv
    return None


def alternating_branch_order(branch_vertices: list[int]) -> list[int]:
    """Alternating order: (v_1, v_0, v_3, v_2, v_5, v_4, ...).

    This swaps each adjacent pair so that within-pair chain links
    (v_{2j+1} -> v_{2j}) are NOT loaded (the later-indexed vertex is
    placed first), while between-pair chain links (v_{2j+2} ->
    v_{2j+1}) ARE loaded (later-indexed placed later within the
    cross-pair transition).
    """
    out = []
    n = len(branch_vertices)
    j = 0
    while j < n:
        if j + 1 < n:
            out.append(branch_vertices[j + 1])
            out.append(branch_vertices[j])
            j += 2
        else:
            out.append(branch_vertices[j])
            j += 1
    return out


def construct_suffix_order(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
) -> list[int] | None:
    """Build an explicit suffix order for C's prefix.

    Strategy: ALTERNATING order on A and B branches, with r
    interleaved at a window-compatible position.

    Alternating order (A_1, A_0, A_3, A_2, ...) on A breaks the
    chain link A_{2j+1} -> A_{2j} loading.  Similarly on B.

    Effect on the cyclic ladder's cycle:
    - For natural odd-start intervals {2j-1, 2j}: within-interval
      chain link is B_{2j} -> B_{2j-1}, which IS loaded by the
      alternating order (B_{2j} placed after B_{2j-1}, j odd).
    - For even-start intervals {2a, 2a+1}: within-interval chain
      link is B_{2a+1} -> B_{2a}, which is NOT loaded (alternating
      places B_{2a+1} first within the pair).

    Hence: alternating order breaks the cycle at EACH even-start
    interval.  If at least one interval is even-start (NaturalOddStart
    fails), the cycle has a missing edge.  Linear forest preserved.
    """
    r_idx = 2 * k + 1
    A_vertices = [2 * k + 2 + j for j in range(k)]
    B_vertices = [3 * k + 2 + j for j in range(k)]

    A_order = alternating_branch_order(A_vertices)
    B_order = alternating_branch_order(B_vertices)

    # Suffix layout:
    #   (A_1, A_0), r, (A_3, A_2), ..., (A_{k-1}, A_{k-2}), B_order
    # We insert r between A_0 (suffix index 1) and A_3 (suffix index 2)
    # to keep r within its window [d^-(r) - 2, d^-(r) + 2] ~ [2k-2, 2k+2].
    # That puts r at LFO position 2k+3 (suffix position 2) — within
    # window for k>=2.
    order: list[int] = []
    if k >= 2:
        order.append(A_order[0])  # A_1 at LFO 2k+1
        order.append(A_order[1])  # A_0 at LFO 2k+2
        order.append(r_idx)        # r at LFO 2k+3
        order.extend(A_order[2:])  # remaining A's
    else:
        order.append(r_idx)
        order.extend(A_order)
    order.extend(B_order)
    return order


def verify_suffix_is_completing(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    suffix: Sequence[int],
) -> dict:
    """Replay the suffix step by step on C's prefix; report whether it
    completes to a valid LFO."""
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return {"valid": False, "reason": "invalid_prefix"}
    prefix_mask, degree, parent, flex_outmask, windows = state
    n = len(T)
    all_mask = (1 << n) - 1
    pos = len(prefix)

    for i, x in enumerate(suffix):
        # Check window.
        if not (windows[x][0] <= pos <= windows[x][1]):
            return {
                "valid": False,
                "reason": "window_violation",
                "step": i,
                "vertex": x,
                "pos": pos,
                "window": list(windows[x]),
            }
        # Check Hall feasibility on remaining unplaced.
        remaining = all_mask ^ prefix_mask
        if not hall_interval_ok(remaining, pos, windows, n):
            return {
                "valid": False,
                "reason": "hall_violation",
                "step": i,
            }
        # FF degree + cycle check via _add_flexible_vertex.
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            return {
                "valid": False,
                "reason": "degree_or_cycle_violation",
                "step": i,
                "vertex": x,
            }
        degree, parent = nxt
        prefix_mask |= 1 << x
        pos += 1

    if prefix_mask != all_mask:
        return {"valid": False, "reason": "incomplete"}

    return {"valid": True, "reason": "completed"}


def verify_mixed_parity_escape_at_k(k: int) -> dict:
    """For every non-V6''-trigger cyclic-ladder core C with a slack
    interval at k, verify the constructed suffix completes."""
    total_candidates = 0
    construction_succeeds = 0
    construction_fails: list[dict] = []
    no_slack_count = 0
    extendable_via_ff = 0

    blocks = even_adjacent_blocks(k)
    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                if not has_no_v6pp_trigger(k, pi, C):
                    continue
                total_candidates += 1
                suffix = construct_suffix_order(k, pi, C)
                if suffix is None:
                    no_slack_count += 1
                    continue
                verdict = verify_suffix_is_completing(k, pi, C, suffix)
                if verdict["valid"]:
                    construction_succeeds += 1
                else:
                    construction_fails.append({
                        "pi": list(pi),
                        "C": list(C),
                        "verdict": verdict,
                    })
                    if len(construction_fails) >= 5:
                        return {
                            "k": k,
                            "total_candidates": total_candidates,
                            "construction_succeeds": construction_succeeds,
                            "no_slack_interval": no_slack_count,
                            "construction_fails": len(construction_fails),
                            "first_failures": construction_fails,
                        }

    return {
        "k": k,
        "total_candidates": total_candidates,
        "construction_succeeds": construction_succeeds,
        "no_slack_interval": no_slack_count,
        "construction_fails": len(construction_fails),
        "first_failures": construction_fails[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    out = verify_mixed_parity_escape_at_k(args.k)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
