"""Cycle-Core Extraction for fork-tree fatal supports (D52).

The Cycle-Core Extraction Lemma:

  Let pi be a fork-tree pairing and S a fatal toggle support.
  Then S contains a subset C ⊆ S such that:
    (CC1) C is fatal;
    (CC2) C is a union of even-odd blocks (no half-blocks);
    (CC3) pi(C) decomposes into disjoint adjacent 2-pairs;
    (CC4) the block/interval incidence of C is a simple cycle.

  C is a "minimal fatal cyclic-ladder core" contained in S.

Implication: if S is itself minimally fatal, then S = C is a cyclic
ladder, giving the Normal-Form Lemma 50.1.

This module:

  - implements `extract_cycle_core(k, pi, S)` that searches for a
    cyclic-ladder core C ⊆ S, returning None if none exists;
  - verifies the existence across all fatal supports at small k.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import product, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def is_cyclic_ladder_core(k: int, pi: Sequence[int], C: Sequence[int]) -> bool:
    """C satisfies (CC2), (CC3), (CC4)."""
    if len(C) == 0:
        return False
    if not verify_NF1_block_union(k, C):
        return False
    if not verify_NF2_adjacent_pairs(pi, C):
        return False
    if not verify_NF3_incidence_cycle(pi, C):
        return False
    return True


def is_fatal(k: int, pi: Sequence[int], S: Sequence[int],
             R_cached: frozenset | None = None) -> bool:
    """Is the toggle support S fatal?"""
    R = R_cached if R_cached is not None else extract_relation(k, pi)
    eps = tuple(1 if i in set(S) else 0 for i in range(k))
    return eps not in R


def extract_cycle_core(
    k: int,
    pi: Sequence[int],
    S: Sequence[int],
    R_cached: frozenset | None = None,
) -> tuple[int, ...] | None:
    """Find a subset C ⊆ S satisfying CC1-CC4, or None if none exists.

    Search strategy: iterate over subsets of selected even-odd blocks,
    in increasing size.  Return the first cyclic-ladder core that is
    fatal.
    """
    S_set = set(S)
    blocks = [(a, b) for (a, b) in even_adjacent_blocks(k)
              if a in S_set and b in S_set]
    R = R_cached if R_cached is not None else extract_relation(k, pi)

    # Iterate over non-empty subsets of blocks, smallest first.
    for size in range(1, len(blocks) + 1):
        from itertools import combinations
        for block_subset in combinations(blocks, size):
            C = tuple(sorted(i for block in block_subset for i in block))
            if not is_cyclic_ladder_core(k, pi, C):
                continue
            if is_fatal(k, pi, C, R_cached=R):
                return C
    return None


def verify_extractor_at_k(k: int) -> dict:
    """For every fatal support S at k, find a cycle-core C ⊆ S."""
    total_fatal = 0
    fatal_with_core = 0
    fatal_without_core: list[dict] = []
    for pi in permutations(range(k)):
        R = extract_relation(k, pi)
        R_set = set(R)
        for bits in product((0, 1), repeat=k):
            if bits in R_set:
                continue
            total_fatal += 1
            S = tuple(i for i, b in enumerate(bits) if b == 1)
            C = extract_cycle_core(k, pi, S, R_cached=R)
            if C is None:
                fatal_without_core.append({
                    "pi": list(pi),
                    "S": list(S),
                })
                if len(fatal_without_core) >= 3:
                    return {
                        "k": k,
                        "total_fatal_supports": total_fatal,
                        "fatal_with_core": fatal_with_core,
                        "fatal_without_core": len(fatal_without_core),
                        "first_violations": fatal_without_core,
                    }
            else:
                fatal_with_core += 1

    return {
        "k": k,
        "total_fatal_supports": total_fatal,
        "fatal_with_core": fatal_with_core,
        "fatal_without_core": len(fatal_without_core),
        "first_violations": fatal_without_core[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    out = verify_extractor_at_k(args.k)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
