#!/usr/bin/env python3
"""Verify an exponential family of distinct directed minimum out-cut arc-sets.

For k >= 2, B_k has vertices s, t, p_1, ..., p_k and arcs

  s -> p_i                    (one copy),
  p_i -> t                    (one copy),
  p_i -> s                    (k-1 copies),
  t -> p_i                    (k-1 copies),
  t -> s                      (k copies).

The graph has lambda(B_k) = k.  For every S subseteq {1, ..., k},
X_S = {s} union {p_i : i in S} has a distinct minimum out-cut

  delta+(X_S) = {s -> p_i : i not in S} union {p_i -> t : i in S}.

Thus B_k has at least 2^k distinct minimum out-cut arc-sets, all represented
by sides avoiding root t.  At k=6 this also refutes EPK-2 by pigeonhole:
2^6 > (n-1)^2 = 49 possible signatures on an ordered pair of spanning
in-arborescences.
"""

from __future__ import annotations

import argparse
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle


def build_binary_channel(k: int):
    if k < 2:
        raise ValueError("k must be at least 2")

    s, t = 0, 1
    channels = list(range(2, k + 2))
    arcs = []
    for p in channels:
        arcs.append((s, p))
        arcs.append((p, t))
        arcs.extend([(p, s)] * (k - 1))
        arcs.extend([(t, p)] * (k - 1))
    arcs.extend([(t, s)] * k)
    return k + 2, arcs, s, t, channels


def labeled_outcut(arcs, side):
    side = frozenset(side)
    return frozenset(
        label
        for label, (tail, head) in enumerate(arcs)
        if tail in side and head not in side
    )


def enumerate_minimum_arcsets(n, arcs, lam, root=None):
    result = set()
    for mask in range(1, (1 << n) - 1):
        side = frozenset(v for v in range(n) if mask & (1 << v))
        if root is not None and root in side:
            continue
        cut = labeled_outcut(arcs, side)
        if len(cut) == lam:
            result.add(cut)
    return result


def binary_family_arcsets(arcs, s, channels):
    result = set()
    for bits in itertools.product((False, True), repeat=len(channels)):
        side = {s}
        side.update(p for p, chosen in zip(channels, bits) if chosen)
        result.add(labeled_outcut(arcs, side))
    return result


def verify_minimum_only_coloring_obstruction(q: int = 1):
    """Return the K_4^* thickening obstruction to a minimum-cut-only lift."""
    vertices = range(4)
    part_a = {0, 3}
    part_b = {1, 2}
    arcs = [
        (u, v)
        for u in vertices
        for v in vertices
        if u != v
        for _ in range(q)
    ]
    red = frozenset(
        label
        for label, (u, v) in enumerate(arcs)
        if (u in part_a and v in part_a) or (u in part_b and v in part_b)
    )
    lam = oracle.arc_connectivity(4, arcs)
    minimum_cuts = enumerate_minimum_arcsets(4, arcs, lam)
    all_minimum_bichromatic = all(cut & red and cut - red for cut in minimum_cuts)
    cut_a = labeled_outcut(arcs, part_a)
    larger_cut_is_all_blue = not (cut_a & red)
    return {
        "q": q,
        "lambda": lam,
        "n_minimum_arcsets": len(minimum_cuts),
        "all_minimum_bichromatic": all_minimum_bichromatic,
        "larger_cut_size": len(cut_a),
        "larger_cut_is_all_blue": larger_cut_is_all_blue,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=8)
    args = parser.parse_args()

    n, arcs, s, t, channels = build_binary_channel(args.k)
    lam = oracle.arc_connectivity(n, arcs)
    all_minimum = enumerate_minimum_arcsets(n, arcs, lam)
    avoiding_t = enumerate_minimum_arcsets(n, arcs, lam, root=t)
    binary = binary_family_arcsets(arcs, s, channels)

    expected_binary = 1 << args.k
    assertions = {
        "lambda_is_k": lam == args.k,
        "binary_family_has_2^k_arcsets": len(binary) == expected_binary,
        "binary_family_is_minimum": all(len(cut) == lam for cut in binary),
        "binary_family_avoids_t": binary <= avoiding_t,
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)

    print(f"B_{args.k}: n={n}, m={len(arcs)}, lambda={lam}")
    print(f"distinct minimum out-cut arc-sets: {len(all_minimum)}")
    print(f"distinct minimum arc-sets with side avoiding t: {len(avoiding_t)}")
    print(f"proved binary subfamily: {len(binary)} = 2^{args.k}")
    print(f"n^2={n * n}; 2(n-1)^2={2 * (n - 1) ** 2}")
    print(
        "EPK-2 per-root pigeonhole: "
        f"{len(binary)} > (n-1)^2={(n - 1) ** 2}: "
        f"{len(binary) > (n - 1) ** 2}"
    )

    coloring = verify_minimum_only_coloring_obstruction(q=max(1, args.k))
    if not (
        coloring["lambda"] == 3 * coloring["q"]
        and coloring["all_minimum_bichromatic"]
        and coloring["larger_cut_is_all_blue"]
    ):
        raise AssertionError(coloring)
    print(
        "minimum-cut-only lift obstruction: "
        f"K_4^* thickening q={coloring['q']}, lambda={coloring['lambda']}, "
        f"all {coloring['n_minimum_arcsets']} minimum arc-sets bichromatic, "
        f"but a size-{coloring['larger_cut_size']} cut is all blue"
    )


if __name__ == "__main__":
    main()
