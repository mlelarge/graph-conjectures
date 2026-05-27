"""Symbolic universal repair suffix sigma*(k) for fork-tree V6''-negative
cyclic-ladder cores (D60).

Background
==========

D59 (`ff_repair_tracer.py`) empirically showed that the FF backtracker's
completing suffix on every V6''-negative cyclic-ladder core depends
*only on k* — the same vertex order works regardless of the pairing pi
or the core C.  The mined "swap-lower-endpoint" sets are:

    k=2:  {0, 3}
    k=4:  {0, 2, 5, 7}
    k=5:  {0, 2, 4, 6, 8}
    k=6:  {0, 2, 4, 7, 9, 11}
    k=7:  {0, 2, 4, 6, 8, 10, 12}

This module replaces that empirical observation with an explicit
closed-form formula and an equivalent recursive definition.

Closed form
===========

Vertex labels (standard fork-tree numbering):
    r   = 2k + 1
    A_i = 2k + 2 + i      for i = 0..k-1
    B_i = 3k + 2 + i      for i = 0..k-1

For k >= 1, define sigma_star(k) as the length-(2k+1) sequence:

    sigma*(k)[0] = A_0
    sigma*(k)[1] = r

    For i = 0, 1, ..., floor((k-1)/2) - 1:
        sigma*(k)[2 + 2i] = A_{2i+2}
        sigma*(k)[3 + 2i] = A_{2i+1}

    If k is even (so k-1 is odd):
        sigma*(k)[k] = A_{k-1}                # unpaired A-tail

    For j = 0, 1, ..., floor(k/2) - 1:
        sigma*(k)[(k+1) + 2j] = B_{2j+1}
        sigma*(k)[(k+2) + 2j] = B_{2j}

    If k is odd (so k-1 is even):
        sigma*(k)[2k] = B_{k-1}               # unpaired B-tail

The "A-block" occupies positions 0..k and the "B-block" occupies
positions k+1..2k.  The unpaired tail sits on whichever side has an odd
count of A/B vertices to pair up.

Recursive form
==============

    sigma*(2) = [A_0, r, A_1, B_1, B_0]   (base case)

    k odd -> k+1 even:
        sigma*(k+1) = sigma*(k)[0..k] ++ [A_k] ++ sigma*(k)[k+1..2k-1]
                                          ++ [B_k, B_{k-1}]
        (The previously-unpaired B_{k-1} is replaced by the pair
         (B_k, B_{k-1}).  A new unpaired A_k is appended to the A-block.)

    k even -> k+1 odd:
        sigma*(k+1) = sigma*(k)[0..k-1] ++ [A_k, A_{k-1}] ++ sigma*(k)[k+1..2k]
                                          ++ [B_k]
        (The previously-unpaired A_{k-1} is replaced by the pair
         (A_k, A_{k-1}).  A new unpaired B_k is appended to the B-block.)

Theorem 60.1 (closed = recursive).  The two definitions agree for all
k >= 2.  Verified symbolically up to k = 12 (see `closed_equals_recursive`).

Theorem 60.2 (FF-validity, conjectural).  For every k >= 2 and every
V6''-negative extendable cyclic-ladder core C at k, the FF tracer's
completing suffix on (pi, C) equals sigma*(k) (as integers).  Verified
empirically at k = 2, 4, 5, 6, 7 (see `verify_matches_tracer`).

This module's role
==================

  * `sigma_star_symbolic_closed(k)` returns the closed-form sequence of
    abstract labels (`('A', i)`, `('r',)`, `('B', i)`).
  * `sigma_star_symbolic_recursive(k)` does the same by recursion.
  * `sigma_star_closed(k)` and `sigma_star_recursive(k)` convert to
    fork-tree integer vertex labels.
  * `closed_equals_recursive(k_max)` checks Theorem 60.1.
  * `verify_matches_tracer(k)` checks Theorem 60.2 at a single k.

Used by Section 60 of `docs/exchange_proof_draft.md`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_repair_tracer import completing_suffix  # noqa: E402
from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from v6pp_completion_constructor import (  # noqa: E402
    has_no_v6pp_trigger,
    is_cyclic_ladder_core,
)


# ----------------------------------------------------------------------
# 1. Symbolic <-> integer label conversions
# ----------------------------------------------------------------------

Label = tuple  # ('r',) | ('A', i) | ('B', i)


def label_to_int(k: int, lab: Label) -> int:
    """Map a symbolic label to its fork-tree integer vertex id."""
    if lab == ('r',):
        return 2 * k + 1
    kind, i = lab
    if kind == 'A':
        if not (0 <= i < k):
            raise ValueError(f"A_{i} out of range for k={k}")
        return 2 * k + 2 + i
    if kind == 'B':
        if not (0 <= i < k):
            raise ValueError(f"B_{i} out of range for k={k}")
        return 3 * k + 2 + i
    raise ValueError(f"unknown label {lab}")


def int_to_label(k: int, v: int) -> Label:
    """Inverse of label_to_int restricted to suffix vertices."""
    if v == 2 * k + 1:
        return ('r',)
    if 2 * k + 2 <= v <= 3 * k + 1:
        return ('A', v - (2 * k + 2))
    if 3 * k + 2 <= v <= 4 * k + 1:
        return ('B', v - (3 * k + 2))
    raise ValueError(f"vertex {v} is not a suffix vertex for k={k}")


# ----------------------------------------------------------------------
# 2. Closed-form sigma*(k)
# ----------------------------------------------------------------------

def sigma_star_symbolic_closed(k: int) -> list[Label]:
    """Closed-form sigma*(k) as symbolic labels.  See module docstring."""
    if k < 1:
        raise ValueError("k >= 1 required")
    out: list[Label] = [('A', 0), ('r',)]
    t_A = (k - 1) // 2
    for i in range(t_A):
        out.append(('A', 2 * i + 2))
        out.append(('A', 2 * i + 1))
    if k % 2 == 0:
        out.append(('A', k - 1))
    t_B = k // 2
    for j in range(t_B):
        out.append(('B', 2 * j + 1))
        out.append(('B', 2 * j))
    if k % 2 == 1:
        out.append(('B', k - 1))
    assert len(out) == 2 * k + 1, (k, out)
    return out


def sigma_star_closed(k: int) -> list[int]:
    return [label_to_int(k, lab) for lab in sigma_star_symbolic_closed(k)]


# ----------------------------------------------------------------------
# 3. Recursive sigma*(k)
# ----------------------------------------------------------------------

def sigma_star_symbolic_recursive(k: int) -> list[Label]:
    """Recursive sigma*(k) built from sigma*(k-1).  Base k = 2."""
    if k < 2:
        raise ValueError("k >= 2 required for recursion")
    if k == 2:
        return [('A', 0), ('r',), ('A', 1), ('B', 1), ('B', 0)]
    prev = sigma_star_symbolic_recursive(k - 1)
    # In sigma*(k-1):
    #   A-block = prev[0..k-1]  (length k = (k-1)+1)
    #   B-block = prev[k..2k-2] (length k-1)
    a_block_prev = prev[:k]
    b_block_prev = prev[k:]
    if (k - 1) % 2 == 0:
        # k-1 even -> k odd.
        # Previously-unpaired ('A', k-2) sits at the end of a_block_prev.
        # Replace with the pair (A_{k-1}, A_{k-2}) and append unpaired B_{k-1}.
        out = list(a_block_prev[:k - 1])
        assert a_block_prev[k - 1] == ('A', k - 2)
        out.append(('A', k - 1))
        out.append(('A', k - 2))
        out.extend(b_block_prev)
        out.append(('B', k - 1))
    else:
        # k-1 odd -> k even.
        # Previously-unpaired ('B', k-2) sits at the end of b_block_prev.
        # Append unpaired A_{k-1} to A-block; replace ('B', k-2) with pair (B_{k-1}, B_{k-2}).
        out = list(a_block_prev)
        out.append(('A', k - 1))
        assert b_block_prev[-1] == ('B', k - 2)
        out.extend(b_block_prev[:-1])
        out.append(('B', k - 1))
        out.append(('B', k - 2))
    assert len(out) == 2 * k + 1, (k, out)
    return out


def sigma_star_recursive(k: int) -> list[int]:
    return [label_to_int(k, lab) for lab in sigma_star_symbolic_recursive(k)]


# ----------------------------------------------------------------------
# 4. Equivalence and tracer-match verification
# ----------------------------------------------------------------------

def closed_equals_recursive(k_max: int = 12) -> dict:
    """Verify sigma*_closed(k) == sigma*_recursive(k) for k = 2..k_max."""
    discrepancies: list[dict] = []
    for k in range(2, k_max + 1):
        c = sigma_star_symbolic_closed(k)
        r = sigma_star_symbolic_recursive(k)
        if c != r:
            discrepancies.append({
                'k': k,
                'closed': c,
                'recursive': r,
            })
    return {
        'k_max': k_max,
        'all_agree': not discrepancies,
        'n_discrepancies': len(discrepancies),
        'discrepancies': discrepancies[:3],
    }


def verify_matches_tracer(k: int) -> dict:
    """For every V6''-negative cyclic-ladder core C at k, check that the
    FF tracer's output equals sigma*(k) per the closed-form formula.

    Non-extendable V6''-negative cores (where the FF returns None) are
    excluded — they have a smaller V6''-positive sub-core and are handled
    by the inductive descent, not by sigma*(k)."""
    blocks = even_adjacent_blocks(k)
    sigma = sigma_star_closed(k)
    total = 0
    extendable = 0
    matches = 0
    mismatches: list[dict] = []
    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                if not has_no_v6pp_trigger(k, pi, C):
                    continue
                total += 1
                suf = completing_suffix(k, pi, C)
                if suf is None:
                    continue
                extendable += 1
                if list(suf) == list(sigma):
                    matches += 1
                else:
                    if len(mismatches) < 5:
                        mismatches.append({
                            'pi': list(pi),
                            'C': list(C),
                            'expected_sigma_star': list(sigma),
                            'found_by_tracer': list(suf),
                        })
    return {
        'k': k,
        'total_v6pp_negative_cores': total,
        'extendable_v6pp_negative': extendable,
        'matches_sigma_star': matches,
        'mismatches': len(mismatches),
        'first_mismatches': mismatches[:3],
        'sigma_star_holds_on_extendable': matches == extendable,
    }


# ----------------------------------------------------------------------
# 5. CLI
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
        "--check-equivalence",
        action="store_true",
        help="Run closed_equals_recursive(k) and exit.",
    )
    parser.add_argument(
        "--verify-tracer",
        action="store_true",
        help="Run verify_matches_tracer(k) and dump JSON.",
    )
    args = parser.parse_args()
    print(f"sigma*(symbolic) at k={args.k}:")
    for j, lab in enumerate(sigma_star_symbolic_closed(args.k)):
        print(f"  pos {j:3d}: {lab}")
    print(f"sigma*(integers) at k={args.k}: {sigma_star_closed(args.k)}")
    if args.check_equivalence:
        print(json.dumps(closed_equals_recursive(args.k), indent=2, default=list))
    if args.verify_tracer:
        print(json.dumps(verify_matches_tracer(args.k), indent=2, default=list))


if __name__ == "__main__":
    main()
