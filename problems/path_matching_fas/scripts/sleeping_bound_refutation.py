"""Exponential lower bound for the current sleeping-block signature.

The sleeping-block polynomial-bound conjecture says that the number of
distinct sleeping-block signatures reachable by FF-pruned LFO prefixes
is polynomially bounded in n.  This script gives a direct counterfamily.

For k gadgets, build a 4k-vertex tournament from the transitive order

    a_0,b_0,a_1,b_1,...,a_{k-1},b_{k-1},f_0,g_0,...,f_{k-1},g_{k-1}

and reverse the two long arcs f_i -> a_i and g_i -> b_i.  At cut 2k,
each local pair can be ordered either (a_i,b_i) or (b_i,a_i).  The first
choice leaves the forced sleeping edges a_i-f_i and b_i-g_i in distinct
components; the second also loads the flexible backedge a_i-b_i, merging
them into the path f_i-a_i-b_i-g_i.  These k independent bits give
2^k distinct sleeping-block signatures, all FF-pruned.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import product
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import valid_prefix_state_ff  # noqa: E402
from sleeping_block_probe import sleeping_block_signature  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = list[list[bool]]


def toggle_tournament(k: int) -> Matrix:
    """Return the 4k-vertex toggle-pair tournament."""
    if k <= 0:
        raise ValueError("k must be positive")
    n = 4 * k
    T = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = True
            T[j][i] = False

    for i in range(k):
        a = 2 * i
        b = 2 * i + 1
        f = 2 * k + 2 * i
        g = 2 * k + 2 * i + 1
        T[f][a] = True
        T[a][f] = False
        T[g][b] = True
        T[b][g] = False
    return T


def toggle_prefix(k: int, bits: Sequence[int]) -> tuple[int, ...]:
    """Prefix at cut 2k; bit 1 swaps the corresponding local pair."""
    if len(bits) != k:
        raise ValueError("bits length must equal k")
    prefix: list[int] = []
    for i, bit in enumerate(bits):
        a = 2 * i
        b = 2 * i + 1
        if bit:
            prefix.extend((b, a))
        else:
            prefix.extend((a, b))
    return tuple(prefix)


def count_toggle_signatures(k: int) -> dict:
    """Count signatures across the 2^k toggle prefixes at cut 2k."""
    T = toggle_tournament(k)
    n = len(T)
    cut = 2 * k
    signatures: dict[tuple, list[tuple[int, ...]]] = {}
    invalid: list[dict] = []
    valid_prefixes = 0
    pruned_prefixes = 0

    for bits in product((0, 1), repeat=k):
        prefix = toggle_prefix(k, bits)
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            invalid.append({"bits": bits, "reason": "invalid_prefix"})
            continue
        valid_prefixes += 1
        if not survives_pruning(state, cut, n):
            invalid.append({"bits": bits, "reason": "ff_pruned"})
            continue
        pruned_prefixes += 1
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = sleeping_block_signature(
            cut, prefix_mask, degree, parent, flex_outmask, windows
        )
        signatures.setdefault(sig, []).append(bits)

    collisions = [patterns for patterns in signatures.values() if len(patterns) > 1]
    return {
        "k": k,
        "n": n,
        "cut": cut,
        "expected_prefixes": 1 << k,
        "valid_prefixes": valid_prefixes,
        "ff_surviving_prefixes": pruned_prefixes,
        "distinct_sleeping_signatures": len(signatures),
        "collisions": len(collisions),
        "invalid": invalid[:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=8)
    args = parser.parse_args()
    rows = [count_toggle_signatures(k) for k in range(1, args.max_k + 1)]
    print(json.dumps(rows, indent=2, default=list))


if __name__ == "__main__":
    main()
