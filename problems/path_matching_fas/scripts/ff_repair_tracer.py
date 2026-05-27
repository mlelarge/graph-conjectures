"""FF repair tracer for V6'' completeness (D59).

Background
==========

`has_completion_ff` (in `ff_signature_probe.py`) is a YES/NO decision
procedure: given an FF prefix state, can the backtracker complete the
order?  For the V6''-completeness investigation we need more than
YES/NO: we need to know which completing suffix the FF solver returns,
and how it relates to a natural ("canonical") baseline order.

This module mirrors `has_completion_ff` almost line-for-line, but
threads the completing suffix through the recursion so the actual
sequence of placements can be inspected.  The FF candidate ordering
(forced-load-count then -window-right, reverse) is preserved verbatim,
so we trace the SAME suffix the original solver would have found first.

The tracer is then used to compare the FF completion against a
"canonical" baseline (the natural order r, A_0, A_1, ..., A_{k-1},
B_0, ..., B_{k-1}, restricted to the suffix vertices and rearranged to
respect FF placement constraints).  The diff is then decomposed into
elementary moves (adjacent swap, 3-rotation, long-range swap, larger
transposition).  Goal: see if the FF solver only ever uses a finite
catalogue of moves on the V6''-negative cyclic-ladder cores.

Used by Section D59 of `docs/exchange_proof_draft.md`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    _canonical_parent,
    valid_prefix_state_ff,
)
from fork_tree_probe import fork_tree_prefix, fork_tree_tournament  # noqa: E402
from lfo_forced_flexible import _forced_future_ok_flexible, _iter_bits  # noqa: E402
from lfo_score_window import hall_interval_ok  # noqa: E402
from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from v6pp_completion_constructor import (  # noqa: E402
    has_no_v6pp_trigger,
    is_cyclic_ladder_core,
)


Matrix = Sequence[Sequence[int]]


# ----------------------------------------------------------------------
# 1. Tracing FF solver
# ----------------------------------------------------------------------

def completing_suffix_ff(
    T: Matrix,
    pos: int,
    prefix_mask: int,
    degree: tuple[int, ...],
    parent: tuple[int, ...],
    flex_outmask: tuple[int, ...],
    windows: tuple[tuple[int, int], ...],
) -> list[int] | None:
    """Return the suffix of vertex placements found by the FF backtracker.

    Mirrors `has_completion_ff` but threads the actual suffix order
    through the recursion.  Returns None if no completion exists.
    Uses the SAME candidate ordering as `has_completion_ff` so the
    returned suffix is the FIRST one found by the backtracker.
    """
    n = len(T)
    all_mask = (1 << n) - 1

    # Cannot use lru_cache here because we need to return a SUFFIX,
    # not a bool.  But the FF backtracker is fast enough on cyclic-ladder
    # cores without caching that it doesn't matter at the scales we
    # care about (k <= 6).  For a quick speedup, we memoize the
    # "completable" predicate exactly as has_completion_ff does, and
    # only build the suffix on the first successful path.
    completable_cache: dict[tuple[int, int, tuple[int, ...], tuple[int, ...]], bool] = {}

    def can_complete(
        at: int,
        prefix: int,
        deg: tuple[int, ...],
        par_sig: tuple[int, ...],
    ) -> bool:
        key = (at, prefix, deg, par_sig)
        if key in completable_cache:
            return completable_cache[key]
        if prefix == all_mask:
            completable_cache[key] = True
            return True
        remaining = all_mask ^ prefix
        if not hall_interval_ok(remaining, at, windows, n):
            completable_cache[key] = False
            return False
        ok, _ = _forced_future_ok_flexible(
            flex_outmask, prefix, remaining, deg, par_sig,
        )
        if not ok:
            completable_cache[key] = False
            return False
        cands = [
            v for v in _iter_bits(remaining)
            if windows[v][0] <= at <= windows[v][1]
        ]
        cands.sort(
            key=lambda x: (
                (flex_outmask[x] & prefix).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        for x in cands:
            nxt = _add_flexible_vertex(flex_outmask, prefix, deg, par_sig, x)
            if nxt is None:
                continue
            nd, np_ = nxt
            if can_complete(at + 1, prefix | (1 << x), nd, _canonical_parent(np_)):
                completable_cache[key] = True
                return True
        completable_cache[key] = False
        return False

    def build_suffix(
        at: int,
        prefix: int,
        deg: tuple[int, ...],
        par_sig: tuple[int, ...],
        so_far: list[int],
    ) -> list[int] | None:
        if prefix == all_mask:
            return list(so_far)
        remaining = all_mask ^ prefix
        if not hall_interval_ok(remaining, at, windows, n):
            return None
        ok, _ = _forced_future_ok_flexible(
            flex_outmask, prefix, remaining, deg, par_sig,
        )
        if not ok:
            return None
        cands = [
            v for v in _iter_bits(remaining)
            if windows[v][0] <= at <= windows[v][1]
        ]
        cands.sort(
            key=lambda x: (
                (flex_outmask[x] & prefix).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        for x in cands:
            nxt = _add_flexible_vertex(flex_outmask, prefix, deg, par_sig, x)
            if nxt is None:
                continue
            nd, np_ = nxt
            if can_complete(at + 1, prefix | (1 << x), nd, _canonical_parent(np_)):
                so_far.append(x)
                result = build_suffix(
                    at + 1,
                    prefix | (1 << x),
                    nd,
                    _canonical_parent(np_),
                    so_far,
                )
                if result is not None:
                    return result
                so_far.pop()
        return None

    return build_suffix(pos, prefix_mask, degree, _canonical_parent(parent), [])


def completing_suffix(k: int, pi: Sequence[int], C: Sequence[int]) -> list[int] | None:
    """Convenience: given (k, pi, C), return the FF suffix or None.

    Uses the same prefix construction as `verify_completion_exists`.
    """
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return None
    prefix_mask, degree, parent, flex_outmask, windows = state
    return completing_suffix_ff(
        T,
        len(prefix),
        prefix_mask,
        degree,
        parent,
        tuple(flex_outmask),
        tuple(windows),
    )


# ----------------------------------------------------------------------
# 2. Canonical suffix baseline
# ----------------------------------------------------------------------

def canonical_suffix(k: int) -> list[int]:
    """Return the canonical baseline suffix order for the standard
    fork-tree.

    After `fork_tree_prefix` we have placed the 2k pair vertices plus
    the seed p.  The suffix consists of:
      r   = 2k + 1
      A_i = 2k + 2 + i  for i in 0..k-1
      B_i = 3k + 2 + i  for i in 0..k-1

    The canonical baseline places them in their natural index order:
        r, A_0, A_1, ..., A_{k-1}, B_0, B_1, ..., B_{k-1}.
    """
    r = 2 * k + 1
    suffix = [r]
    for i in range(k):
        suffix.append(2 * k + 2 + i)  # A_i
    for i in range(k):
        suffix.append(3 * k + 2 + i)  # B_i
    return suffix


# ----------------------------------------------------------------------
# 3. Permutation diff -> elementary moves
# ----------------------------------------------------------------------

def _classify_swap(i: int, j: int) -> str:
    """Classify a single (i,j) transposition."""
    if i == j:
        return "noop"
    a, b = sorted((i, j))
    if b - a == 1:
        return "adjacent_swap"
    return f"long_range_swap_d{b - a}"


def diff_as_moves(sigma_canonical: Sequence[int], sigma_found: Sequence[int]) -> dict:
    """Decompose the permutation taking sigma_canonical to sigma_found
    into a sequence of swaps using a simple left-to-right algorithm.

    Returns a dict with:
        - "moves": list of {"kind", "i", "j", "vertices", "distance"}
        - "move_classes": Counter of move kinds
        - "is_identity": bool
        - "n_moves": int
        - "max_distance": maximum |i-j| seen
    """
    if sorted(sigma_canonical) != sorted(sigma_found):
        return {
            "error": "vertex_sets_differ",
            "canonical_set": sorted(sigma_canonical),
            "found_set": sorted(sigma_found),
        }

    work = list(sigma_canonical)
    target = list(sigma_found)
    moves: list[dict] = []
    pos_of: dict[int, int] = {v: i for i, v in enumerate(work)}

    for i in range(len(target)):
        if work[i] == target[i]:
            continue
        j = pos_of[target[i]]
        # swap work[i] and work[j]
        moves.append({
            "kind": _classify_swap(i, j),
            "i": i,
            "j": j,
            "vertices": [work[i], work[j]],
            "distance": abs(i - j),
        })
        pos_of[work[i]] = j
        pos_of[work[j]] = i
        work[i], work[j] = work[j], work[i]

    move_classes: Counter[str] = Counter(m["kind"] for m in moves)
    max_dist = max((m["distance"] for m in moves), default=0)
    return {
        "moves": moves,
        "move_classes": dict(move_classes),
        "is_identity": len(moves) == 0,
        "n_moves": len(moves),
        "max_distance": max_dist,
    }


# ----------------------------------------------------------------------
# 4. Higher-level move detection: 3-rotations, blocks
# ----------------------------------------------------------------------

def _is_disjoint_adjacent_swaps(canon: list[int], found: list[int]) -> bool:
    """Return True iff `found` differs from `canon` by a set of
    pairwise-disjoint adjacent transpositions (i, i+1)."""
    n = len(canon)
    i = 0
    while i < n:
        if canon[i] == found[i]:
            i += 1
            continue
        if i + 1 >= n:
            return False
        if found[i] == canon[i + 1] and found[i + 1] == canon[i]:
            i += 2
            continue
        return False
    return True


def detect_rotations_and_blocks(
    sigma_canonical: Sequence[int],
    sigma_found: Sequence[int],
) -> dict:
    """Detect structural patterns: 3-rotations, contiguous reversals,
    block transpositions.

    A 3-rotation at i is sigma_found[i..i+2] = a cyclic rotation of
    sigma_canonical[i..i+2].

    A reversed block of length L at i is sigma_found[i..i+L-1] =
    reverse(sigma_canonical[i..i+L-1]).

    Returns a dict summarising whether the diff fits a single
    structural pattern, plus the full move list.
    """
    n = len(sigma_canonical)
    canon = list(sigma_canonical)
    found = list(sigma_found)

    diff_positions = [i for i in range(n) if canon[i] != found[i]]
    if not diff_positions:
        return {
            "pattern": "identity",
            "n_diff_positions": 0,
            "diff_positions": [],
        }

    lo = min(diff_positions)
    hi = max(diff_positions)
    span = hi - lo + 1
    canon_seg = canon[lo:hi + 1]
    found_seg = found[lo:hi + 1]

    # Single adjacent swap
    if span == 2 and canon_seg == [found_seg[1], found_seg[0]]:
        return {
            "pattern": "adjacent_swap",
            "n_diff_positions": 2,
            "diff_positions": diff_positions,
            "span": 2,
            "block_lo": lo,
            "block_hi": hi,
        }

    # 3-rotation: span 3, all three differ, found is a cyclic
    # rotation of canonical
    if span == 3 and len(diff_positions) == 3:
        if found_seg == [canon_seg[1], canon_seg[2], canon_seg[0]]:
            return {
                "pattern": "3_rotation_left",
                "n_diff_positions": 3,
                "diff_positions": diff_positions,
                "span": 3,
                "block_lo": lo,
                "block_hi": hi,
            }
        if found_seg == [canon_seg[2], canon_seg[0], canon_seg[1]]:
            return {
                "pattern": "3_rotation_right",
                "n_diff_positions": 3,
                "diff_positions": diff_positions,
                "span": 3,
                "block_lo": lo,
                "block_hi": hi,
            }

    # Reversal of a contiguous block
    if found_seg == canon_seg[::-1]:
        return {
            "pattern": f"block_reversal_len{span}",
            "n_diff_positions": len(diff_positions),
            "diff_positions": diff_positions,
            "span": span,
            "block_lo": lo,
            "block_hi": hi,
        }

    # Long-range transposition (exactly two positions differ, swapped)
    if len(diff_positions) == 2:
        i, j = diff_positions
        if found[i] == canon[j] and found[j] == canon[i]:
            return {
                "pattern": f"long_range_swap_d{j - i}",
                "n_diff_positions": 2,
                "diff_positions": diff_positions,
                "span": j - i + 1,
                "block_lo": i,
                "block_hi": j,
            }

    # Disjoint adjacent swaps: every diff position i has its partner
    # at i+1 or i-1, and they form a perfect matching by 2-cycles.
    if _is_disjoint_adjacent_swaps(canon, found):
        n_swaps = len(diff_positions) // 2
        return {
            "pattern": f"disjoint_adjacent_swaps_n{n_swaps}",
            "n_diff_positions": len(diff_positions),
            "diff_positions": diff_positions,
            "span": span,
            "block_lo": lo,
            "block_hi": hi,
            "n_adjacent_swaps": n_swaps,
        }

    # Block transposition: outside [lo, hi] is identity, inside is
    # some permutation
    if (canon[:lo] == found[:lo]) and (canon[hi + 1:] == found[hi + 1:]):
        return {
            "pattern": f"localized_block_perm_len{span}",
            "n_diff_positions": len(diff_positions),
            "diff_positions": diff_positions,
            "span": span,
            "block_lo": lo,
            "block_hi": hi,
            "canonical_block": canon_seg,
            "found_block": found_seg,
        }

    return {
        "pattern": "complex",
        "n_diff_positions": len(diff_positions),
        "diff_positions": diff_positions,
        "span": span,
        "block_lo": lo,
        "block_hi": hi,
        "canonical_block": canon_seg,
        "found_block": found_seg,
    }


# ----------------------------------------------------------------------
# 5. Enumeration over all V6''-negative cyclic-ladder cores at given k
# ----------------------------------------------------------------------

def trace_all_v6pp_negative_cores(k: int) -> dict:
    """For every V6''-negative cyclic-ladder core C at the given k,
    run the FF tracer, compute canonical baseline diff, and tally
    move classes.

    Returns a dict suitable for D59's tables.
    """
    blocks = even_adjacent_blocks(k)
    canon = canonical_suffix(k)

    total = 0
    extendable = 0
    not_extendable = 0
    identity_count = 0
    pattern_counter: Counter[str] = Counter()
    move_class_counter: Counter[str] = Counter()
    n_moves_distribution: Counter[int] = Counter()
    max_distance_distribution: Counter[int] = Counter()
    distinct_found_suffixes: Counter[tuple] = Counter()
    distinct_swap_position_sets: Counter[tuple] = Counter()

    examples_by_pattern: dict[str, list[dict]] = {}

    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                if not has_no_v6pp_trigger(k, pi, C):
                    continue
                total += 1
                suffix = completing_suffix(k, pi, C)
                if suffix is None:
                    not_extendable += 1
                    continue
                extendable += 1
                diff = diff_as_moves(canon, suffix)
                pattern = detect_rotations_and_blocks(canon, suffix)
                pattern_name = pattern["pattern"]
                pattern_counter[pattern_name] += 1
                if pattern_name == "identity":
                    identity_count += 1
                for cls, count in diff.get("move_classes", {}).items():
                    move_class_counter[cls] += count
                n_moves_distribution[diff["n_moves"]] += 1
                max_distance_distribution[diff["max_distance"]] += 1
                distinct_found_suffixes[tuple(suffix)] += 1
                # Record the set of LOWER endpoints of adjacent swaps,
                # if applicable, to see whether the FF solver picks the
                # same swap positions every time.
                if pattern_name.startswith("disjoint_adjacent_swaps"):
                    swap_los: list[int] = []
                    a, b = 0, 0
                    canon_l = list(canon)
                    suff_l = list(suffix)
                    ii = 0
                    while ii < len(canon_l):
                        if canon_l[ii] != suff_l[ii]:
                            swap_los.append(ii)
                            ii += 2
                        else:
                            ii += 1
                    distinct_swap_position_sets[tuple(swap_los)] += 1

                bucket = examples_by_pattern.setdefault(pattern_name, [])
                if len(bucket) < 3:
                    bucket.append({
                        "pi": list(pi),
                        "C": list(C),
                        "canonical": list(canon),
                        "found": list(suffix),
                        "n_moves": diff["n_moves"],
                        "move_classes": dict(diff.get("move_classes", {})),
                        "pattern_detail": {
                            kk: vv for kk, vv in pattern.items()
                            if kk != "pattern"
                        },
                    })

    return {
        "k": k,
        "total_v6pp_negative_cores": total,
        "extendable": extendable,
        "not_extendable": not_extendable,
        "identity_count": identity_count,
        "pattern_distribution": dict(pattern_counter),
        "move_class_totals": dict(move_class_counter),
        "n_moves_distribution": dict(sorted(n_moves_distribution.items())),
        "max_distance_distribution": dict(sorted(max_distance_distribution.items())),
        "n_distinct_found_suffixes": len(distinct_found_suffixes),
        "distinct_found_suffixes": [
            {"suffix": list(s), "count": c}
            for s, c in distinct_found_suffixes.most_common()
        ],
        "n_distinct_swap_position_sets": len(distinct_swap_position_sets),
        "distinct_swap_position_sets": [
            {"swap_lower_endpoints": list(s), "count": c}
            for s, c in distinct_swap_position_sets.most_common()
        ],
        "examples_by_pattern": examples_by_pattern,
    }


# ----------------------------------------------------------------------
# 6. CLI
# ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--k",
        type=int,
        required=True,
        help="Number of (a_i, b_i) pair levels in the fork tree.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to dump the full result JSON.",
    )
    args = parser.parse_args()
    result = trace_all_v6pp_negative_cores(args.k)
    text = json.dumps(result, indent=2, default=list)
    print(text)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)


if __name__ == "__main__":
    main()
