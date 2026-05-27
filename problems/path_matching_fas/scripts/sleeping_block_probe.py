"""Sleeping-block signature for the forced/flexible DP.

The visible-latent signature uses only A_i ∪ O_i. A "sleeping block" is
a back-arc-graph component that has no current visible representative
but contains at least one future-opening vertex (i.e., a vertex whose
window has not yet started). Sleeping blocks can re-emerge later when
their members become active.

This module:

  1. defines `sleeping_block_signature(state)` that augments the
     visible-latent signature with the canonical partition restricted
     to (A_i ∪ O_i ∪ future-opening unplaced vertices);
  2. runs the same kind of collision sweep as `ff_signature_probe.py`;
  3. tabulates: do `visible-latent` and `sleeping-augmented` partition
     the prefix space into the same equivalence classes? If yes,
     sleeping blocks are redundant. If no, sleeping is required.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _iter_census_records,
    has_completion_ff,
    prefixes,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from lfo_forced_flexible import _find  # noqa: E402


Matrix = Sequence[Sequence[int]]


def sleeping_block_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> tuple:
    """Visible-latent signature extended with a sleeping-block partition.

    The sleeping-block tracking partitions the union of
      - active vertices A_i,
      - old visible ports O_i (placed, with unplaced flex partner in A_i),
      - future-opening vertices F_i (unplaced, with l_v > pos).
    using the current back-arc graph component map.

    For each vertex in this union, we record the union-find representative
    in a canonical (smallest-vertex-in-block) form. Vertices that are
    *placed dormant and not future-opening* are deliberately omitted: they
    cannot re-emerge in any future visible state, so their identity is
    irrelevant.
    """
    base = visible_latent_signature(
        pos, prefix_mask, degree, parent, flex_outmask, windows
    )
    n = len(parent)
    active_set = {v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi}
    future_opening = {
        v for v, (lo, _hi) in enumerate(windows)
        if lo > pos and not (prefix_mask & (1 << v))
    }
    visible_old = set()
    # Recompute visible_old explicitly: placed vertices that are flex
    # partners of unplaced active vertices.
    placed_set = {v for v in range(n) if prefix_mask & (1 << v)}
    unplaced_active = active_set - placed_set
    for x in unplaced_active:
        for p in range(n):
            if (flex_outmask[x] >> p) & 1 and (prefix_mask >> p) & 1:
                if p not in active_set:
                    visible_old.add(p)

    relevant = active_set | visible_old | future_opening
    par = list(parent)
    # Canonical labelling: for each relevant vertex, the smallest vertex
    # in its union-find block (over the *whole* vertex set).
    blocks: dict[int, list[int]] = defaultdict(list)
    for v in range(n):
        blocks[_find(par, v)].append(v)
    canonical_block = {root: min(members) for root, members in blocks.items()}

    block_membership = sorted(
        (v, canonical_block[_find(par, v)])
        for v in relevant
    )
    # Replace block-id with a position-relative label so that two states
    # with the same partition structure but different absolute IDs match.
    seen_blocks: dict[int, int] = {}
    block_labels: list[tuple[int, int]] = []
    for v, b in block_membership:
        if b not in seen_blocks:
            seen_blocks[b] = len(seen_blocks)
        block_labels.append((v, seen_blocks[b]))

    return base + (tuple(block_labels),)


def _row_from_signature(
    prefix: Sequence[int],
    prefix_mask: int,
    ext: bool,
    sig: tuple,
) -> dict:
    return {
        "prefix": list(prefix),
        "prefix_mask": prefix_mask,
        "extendable": ext,
        "pos": sig[0],
    }


def compare_signatures(
    T: Matrix,
    depth: int = 5,
) -> dict:
    """Compute equivalence classes under visible-latent vs sleeping-block.

    Returns counts and any collisions found by sleeping-block but NOT by
    visible-latent (none expected, since sleeping is a refinement) and
    vice versa (the interesting direction: visible-latent collisions
    that sleeping resolves).
    """
    visible_buckets: dict[tuple, list[dict]] = defaultdict(list)
    sleeping_buckets: dict[tuple, list[dict]] = defaultdict(list)
    visible_collisions = []
    sleeping_collisions = []
    checked = 0
    n = len(T)
    for prefix in prefixes(n, depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        checked += 1
        prefix_mask, degree, parent, flex_outmask, windows = state
        pos = len(prefix)
        v_sig = visible_latent_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        s_sig = sleeping_block_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        ext = has_completion_ff(
            T, pos, prefix_mask, degree, parent,
            tuple(flex_outmask), tuple(windows),
        )
        row = _row_from_signature(prefix, prefix_mask, ext, v_sig)
        # Visible-latent collisions
        for other in visible_buckets[v_sig]:
            if other["extendable"] != ext:
                visible_collisions.append({
                    "v_sig": v_sig,
                    "state_a": other,
                    "state_b": row,
                })
        visible_buckets[v_sig].append(row)
        # Sleeping-block collisions
        for other in sleeping_buckets[s_sig]:
            if other["extendable"] != ext:
                sleeping_collisions.append({
                    "s_sig": s_sig,
                    "state_a": other,
                    "state_b": row,
                })
        sleeping_buckets[s_sig].append(row)

    return {
        "n": n,
        "depth": depth,
        "checked_valid_prefixes": checked,
        "visible_classes": len(visible_buckets),
        "sleeping_classes": len(sleeping_buckets),
        "visible_collisions": len(visible_collisions),
        "sleeping_collisions": len(sleeping_collisions),
        "visible_refined_by_sleeping": len(sleeping_buckets) > len(visible_buckets),
        "visible_collision_examples": visible_collisions[:3],
    }


def compare_census(path: str, depth: int = 5, limit: int | None = None) -> dict:
    summary = {
        "checked": 0,
        "total_visible_classes": 0,
        "total_sleeping_classes": 0,
        "total_visible_collisions": 0,
        "total_sleeping_collisions": 0,
        "sleeping_strictly_refines_count": 0,
        "first_visible_collision_record": None,
    }
    for bucket_index, record_index, T in _iter_census_records(path):
        if limit is not None and summary["checked"] >= limit:
            break
        summary["checked"] += 1
        r = compare_signatures(T, depth)
        summary["total_visible_classes"] += r["visible_classes"]
        summary["total_sleeping_classes"] += r["sleeping_classes"]
        summary["total_visible_collisions"] += r["visible_collisions"]
        summary["total_sleeping_collisions"] += r["sleeping_collisions"]
        if r["visible_refined_by_sleeping"]:
            summary["sleeping_strictly_refines_count"] += 1
        if r["visible_collisions"] and summary["first_visible_collision_record"] is None:
            summary["first_visible_collision_record"] = {
                "bucket_index": bucket_index,
                "record_index": record_index,
                "T": [list(row) for row in T],
                "report": r,
            }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--T", help="Tournament as a JSON matrix")
    source.add_argument("--census", help="Census JSON path")
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.T is not None:
        out = compare_signatures(json.loads(args.T), args.depth)
    else:
        out = compare_census(args.census, args.depth, args.limit)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
