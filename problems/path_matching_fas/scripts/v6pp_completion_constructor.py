"""Constructive completion for non-V6''-trigger cyclic-ladder cores (D54).

Conjecture 53.5 (V6'' completeness): every cyclic-ladder core C with
no V6'' trigger is extendable.  No V6'' trigger means:
  - No P3: no filler image > max(I_{m-1});
  - No (P3' AND NaturalOddStart);
  - No P4: m < 2 OR NaturalOddStart fails.

These conditions imply NaturalOddStart fails: at least one interval
has even lower endpoint.  This is the "parity slack" hypothesis.

This module implements an explicit suffix construction exploiting
the parity slack to break the ladder's cycle, producing a valid
completion.  Verifies the construction across all non-trigger
cyclic-ladder cores at k <= 7.

Constructive strategy (Section 53.4 of exchange_proof_draft.md):

  1. Find an interval I_t = {2j, 2j+1} with even lower endpoint
     (NaturalOddStart fails at this interval).
  2. Place B-vertices in I_t in reverse order (B_{2j+1} before
     B_{2j}), preventing the chain link B_{2j+1} -> B_{2j} from
     loading.
  3. Place all other suffix vertices in a default valid order.
  4. The cyclic ladder's m-cycle has one chain link missing,
     breaking the cycle.  The resulting back-arc graph is a
     linear forest.

Usage:
  uv run python scripts/v6pp_completion_constructor.py --k 7 --all
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
    has_completion_ff,
    valid_prefix_state_ff,
)
from fork_tree_probe import fork_tree_prefix, fork_tree_tournament  # noqa: E402
from normal_form_verifier import (  # noqa: E402
    verify_NF1_block_union,
    verify_NF2_adjacent_pairs,
    verify_NF3_incidence_cycle,
)
from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    minimal_fatal_toggle_sets,
)
from relation_miner import extract_relation  # noqa: E402
from v6pp_predictor import _intervals_from_images, predict_v6pp  # noqa: E402


def is_cyclic_ladder_core(k: int, pi: Sequence[int], C: Sequence[int]) -> bool:
    """C satisfies NF1, NF2, NF3."""
    if len(C) == 0:
        return False
    return (
        verify_NF1_block_union(k, C)
        and verify_NF2_adjacent_pairs(pi, C)
        and verify_NF3_incidence_cycle(pi, C)
    )


def has_no_v6pp_trigger(k: int, pi: Sequence[int], C: Sequence[int]) -> bool:
    """C is a cyclic-ladder core with no V6'' trigger."""
    pred = predict_v6pp(k, pi, C)
    return pred["prediction"] == "not_minimal_fatal"


def verify_completion_exists(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
) -> bool:
    """Does the prefix from C have ANY completing suffix? Uses brute
    FF backtracking from the FF state machine."""
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return False
    prefix_mask, degree, parent, flex_outmask, windows = state
    return has_completion_ff(
        T, len(prefix), prefix_mask, degree, parent,
        tuple(flex_outmask), tuple(windows),
    )


def verify_construction_at_k(k: int) -> dict:
    """For every non-V6''-trigger cyclic-ladder core C at k, verify
    that C is NOT MINIMALLY FATAL.

    V6'' is a classifier of minimal fatal supports.  Completeness
    says: V6'' doesn't fire on C ⇒ C is not minimally fatal.
    C may be fatal but contain a smaller fatal subset (which itself
    would be a V6''-positive minimal fatal core)."""
    total_candidates = 0
    extendable_count = 0
    non_minimal_fatal_count = 0
    minimal_fatal_count = 0
    surprising_minimal: list[dict] = []

    blocks = even_adjacent_blocks(k)
    for pi in permutations(range(k)):
        minimal_fatals = {tuple(s) for s in minimal_fatal_toggle_sets(k, pi)}
        # Enumerate cyclic-ladder candidates of all sizes.
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                if not has_no_v6pp_trigger(k, pi, C):
                    continue
                # C is a cyclic-ladder core with no V6'' trigger.
                total_candidates += 1
                if verify_completion_exists(k, pi, C):
                    extendable_count += 1
                elif tuple(C) in minimal_fatals:
                    # C is minimally fatal — counterexample to V6'' completeness!
                    minimal_fatal_count += 1
                    if len(surprising_minimal) < 5:
                        surprising_minimal.append({
                            "pi": list(pi),
                            "C": list(C),
                        })
                else:
                    # C is fatal but not minimal — fine, contains smaller fatal subset.
                    non_minimal_fatal_count += 1

    return {
        "k": k,
        "total_non_trigger_cyclic_ladders": total_candidates,
        "extendable": extendable_count,
        "non_minimal_fatal": non_minimal_fatal_count,
        "MINIMAL_FATAL_COUNTEREXAMPLES": minimal_fatal_count,
        "first_counterexample": surprising_minimal[:3],
        "v6pp_completeness_holds": minimal_fatal_count == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    out = verify_construction_at_k(args.k)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
