"""Empirical verifier for the Normal-Form Lemma (D50).

Normal-Form Lemma (statement, Section 50):

  If S is a minimal fatal toggle support of fork-tree(k, pi), then:

  (NF1) S is a union of even-adjacent toggle blocks
        {(0,1), (2,3), (4,5), ...} — i.e., for every i in S with i
        even, i+1 is also in S; for every i in S with i odd, i-1
        is also in S.

  (NF2) The image set pi(S) decomposes into adjacent 2-pairs
        (a, a+1), all disjoint.

  (NF3) The bipartite block/interval incidence graph
        (blocks <-> image intervals, edge iff block has an image
        in interval) is a simple cycle.

This module exhaustively verifies NF1-NF3 across all pairings at
k in {4, 5, 6, 7}.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
    minimal_fatal_toggle_sets,
)
from v6pp_predictor import _intervals_from_images  # noqa: E402


def verify_NF1_block_union(k: int, S: Sequence[int]) -> bool:
    """S is a union of even-adjacent toggle blocks {(2p, 2p+1)}."""
    S_set = set(S)
    blocks = even_adjacent_blocks(k)
    # Each block is either fully in S or fully out.
    for (a, b) in blocks:
        if (a in S_set) != (b in S_set):
            return False
    # The lone unpaired index k-1 (odd k) cannot be selected unless it
    # somehow forms a block with k.  Empirically, lone vertex never
    # appears in a minimal fatal support.
    if k % 2 == 1 and (k - 1) in S_set:
        return False
    # All selected toggle indices must belong to some block.
    block_union = {i for block in blocks for i in block}
    if not S_set.issubset(block_union):
        return False
    return True


def verify_NF2_adjacent_pairs(pi: Sequence[int], S: Sequence[int]) -> bool:
    """pi(S) decomposes into adjacent 2-pairs."""
    images = [pi[i] for i in S]
    return _intervals_from_images(images) is not None


def verify_NF3_incidence_cycle(pi: Sequence[int], S: Sequence[int]) -> bool:
    """The bipartite block/interval incidence graph is a simple cycle."""
    S_sorted = tuple(sorted(S))
    images = sorted({pi[i] for i in S_sorted})
    intervals = _intervals_from_images(images)
    if intervals is None:
        return False
    # Selected blocks: (2p, 2p+1) such that both 2p and 2p+1 are in S.
    blocks = [(a, b) for (a, b) in even_adjacent_blocks(len(pi))
              if a in set(S_sorted) and b in set(S_sorted)]
    # Bipartite incidence: block <-> interval.
    # An edge exists iff one of pi(a), pi(b) lies in the interval.
    m = len(intervals)
    if m == 0 and len(blocks) == 0:
        return True  # Vacuously cycle.
    if m == 1:
        # 1-interval case: single block, both images in single interval.
        # No "cycle"; this is the size-2 case (single block).  Special
        # case: treat as a degenerate "1-cycle" (one block = one node).
        if len(blocks) == 1:
            block = blocks[0]
            img_set = {pi[block[0]], pi[block[1]]}
            return img_set == set(intervals[0])
        return False
    # General case: bipartite incidence.
    # Each block has degree (= number of intervals it touches).
    # Each interval has degree (= number of blocks incident).
    block_to_intervals: list[set[int]] = []
    for block in blocks:
        a, b = block
        img_a, img_b = pi[a], pi[b]
        touched = set()
        for idx, iv in enumerate(intervals):
            if img_a in iv or img_b in iv:
                touched.add(idx)
        if len(touched) != 2:
            # Each block should touch exactly 2 distinct intervals
            # (one image per interval).
            return False
        block_to_intervals.append(touched)
    # Interval degrees.
    interval_to_blocks: list[set[int]] = [set() for _ in intervals]
    for bi, touched in enumerate(block_to_intervals):
        for ti in touched:
            interval_to_blocks[ti].add(bi)
    # Every interval has degree exactly 2 (= block count for a cycle).
    for tb in interval_to_blocks:
        if len(tb) != 2:
            return False
    # Now the bipartite graph: blocks and intervals, all degree 2.
    # This is a disjoint union of cycles.  Check connectedness (single
    # cycle) via BFS.
    n_blocks = len(blocks)
    n_intervals = len(intervals)
    if n_blocks != n_intervals:
        return False
    visited_blocks = set()
    visited_intervals = set()
    stack = [(0, "block")]
    visited_blocks.add(0)
    while stack:
        node, kind = stack.pop()
        if kind == "block":
            for ti in block_to_intervals[node]:
                if ti not in visited_intervals:
                    visited_intervals.add(ti)
                    stack.append((ti, "interval"))
        else:
            for bi in interval_to_blocks[node]:
                if bi not in visited_blocks:
                    visited_blocks.add(bi)
                    stack.append((bi, "block"))
    return len(visited_blocks) == n_blocks and len(visited_intervals) == n_intervals


def verify_normal_form(k: int, pi: Sequence[int], S: Sequence[int]) -> dict:
    """Run all three NF checks."""
    return {
        "k": k,
        "pi": list(pi),
        "S": list(S),
        "NF1_block_union": verify_NF1_block_union(k, S),
        "NF2_adjacent_pairs": verify_NF2_adjacent_pairs(pi, S),
        "NF3_incidence_cycle": verify_NF3_incidence_cycle(pi, S),
    }


def sweep_k(k: int) -> dict:
    """Sweep all pairings, all minimal fatal supports, verify NF1-NF3."""
    total_supports = 0
    nf1_failures = []
    nf2_failures = []
    nf3_failures = []
    for pi in permutations(range(k)):
        supports = minimal_fatal_toggle_sets(k, pi)
        for S in supports:
            total_supports += 1
            check = verify_normal_form(k, pi, S)
            if not check["NF1_block_union"]:
                nf1_failures.append(check)
            if not check["NF2_adjacent_pairs"]:
                nf2_failures.append(check)
            if not check["NF3_incidence_cycle"]:
                nf3_failures.append(check)
    return {
        "k": k,
        "total_minimal_supports": total_supports,
        "NF1_violations": len(nf1_failures),
        "NF2_violations": len(nf2_failures),
        "NF3_violations": len(nf3_failures),
        "first_NF1_failure": nf1_failures[0] if nf1_failures else None,
        "first_NF2_failure": nf2_failures[0] if nf2_failures else None,
        "first_NF3_failure": nf3_failures[0] if nf3_failures else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    out = sweep_k(args.k)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
