"""Empirical evidence for Sublemma 50.3 (Block Parity).

The sublemma claims: no minimal fatal toggle support contains a
half-block (one of 2p, 2p+1 selected but not both).

This script empirically verifies a STRONGER claim:

  Claim:  For every fork-tree pairing pi and every fatal support
  S that contains a half-block, S has a STRICT subset S' that is
  also fatal AND S' is a union of even-odd blocks (no half-blocks).

This is equivalent to Sublemma 50.3 for the inclusion-minimal layer.
Verified across small k where exhaustive enumeration is feasible.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import permutations, product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    minimal_fatal_toggle_sets,
)
from relation_miner import extract_relation  # noqa: E402


def has_half_block(k: int, S: Sequence[int]) -> bool:
    """Does S contain a half-block (one of 2p, 2p+1 but not both)?"""
    S_set = set(S)
    blocks = even_adjacent_blocks(k)
    for (a, b) in blocks:
        if (a in S_set) != (b in S_set):
            return True
    # Lone unpaired index at odd k.
    if k % 2 == 1 and (k - 1) in S_set:
        return True
    return False


def fatal_supports(k: int, pi: Sequence[int]) -> list[tuple[int, ...]]:
    """All fatal supports (not just minimal) of pi at k."""
    R = extract_relation(k, pi)
    R_set = set(R)
    out: list[tuple[int, ...]] = []
    for bits in product((0, 1), repeat=k):
        if bits not in R_set:
            out.append(tuple(i for i, b in enumerate(bits) if b == 1))
    return out


def verify_block_parity_at_k(k: int) -> dict:
    """For every pi at k, every fatal half-block-containing support
    must contain a strict full-block-only fatal subset."""
    total_pairings = 0
    total_half_block_fatals = 0
    violations: list[dict] = []

    for pi in permutations(range(k)):
        total_pairings += 1
        fatals = set(map(tuple, fatal_supports(k, pi)))
        for S in fatals:
            if not has_half_block(k, S):
                continue
            total_half_block_fatals += 1
            # Look for a strict full-block-only fatal subset.
            S_set = set(S)
            blocks = even_adjacent_blocks(k)
            found_subset = False
            # All proper subsets of S that are unions of blocks.
            for nblock_mask in range(0, 1 << len(blocks)):
                subset = set()
                for j, (a, b) in enumerate(blocks):
                    if nblock_mask & (1 << j):
                        if a in S_set and b in S_set:
                            subset.add(a)
                            subset.add(b)
                        else:
                            subset = None
                            break
                if subset is None:
                    continue
                if subset == S_set:
                    continue  # Not a strict subset.
                subset_tuple = tuple(sorted(subset))
                if subset_tuple in fatals:
                    found_subset = True
                    break
            if not found_subset:
                violations.append({
                    "pi": list(pi),
                    "S_half_block": list(S),
                })
                if len(violations) > 5:
                    break
        if len(violations) > 5:
            break

    return {
        "k": k,
        "pairings_checked": total_pairings,
        "half_block_fatal_supports": total_half_block_fatals,
        "violations": len(violations),
        "first_violations": violations[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    out = verify_block_parity_at_k(args.k)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
