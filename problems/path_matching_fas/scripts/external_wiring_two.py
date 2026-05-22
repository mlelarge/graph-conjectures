"""Two-external-vertex asymmetric wiring search.

Extends the single-external-vertex study by adding two external clause
vertices c1, c2. We search over orientations of the 14 c<->block arcs
and the 1 c1<->c2 arc, looking for combined-LFO orderings.

We use the relaxed "active hit in each state" criterion (LFO must hit at
least one active port in each state, inactive hits to spare-degree
vertices are tolerated).
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
from typing import Iterable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from external_wiring_search import (  # noqa: E402
    BLOCK_N, L_ORDER, R_ORDER, N_PORTS, Y_PORTS,
    back_arc_data, classify_external_hits,
)
from path_state_signature import TWO_STATE_PORT_BLOCK  # noqa: E402


def build_combined_two(c1_bits, c2_bits, c12_dir) -> list[list[int]]:
    """Build 9-vertex tournament: block + c1=7 + c2=8.

    c1_bits[i]=1 means T[c1][block_i]=1.
    c2_bits[i]=1 means T[c2][block_i]=1.
    c12_dir=1 means T[c1][c2]=1, else T[c2][c1]=1.
    """
    n = BLOCK_N + 2
    T = [[0]*n for _ in range(n)]
    for u in range(BLOCK_N):
        for v in range(BLOCK_N):
            T[u][v] = TWO_STATE_PORT_BLOCK[u][v]
    c1, c2 = BLOCK_N, BLOCK_N + 1
    for v, b in enumerate(c1_bits):
        if b == 1: T[c1][v] = 1
        else: T[v][c1] = 1
    for v, b in enumerate(c2_bits):
        if b == 1: T[c2][v] = 1
        else: T[v][c2] = 1
    if c12_dir == 1: T[c1][c2] = 1
    else: T[c2][c1] = 1
    return T


def insertions2(base_order, n_new=2):
    """Generate all orderings of (block + n_new external) by inserting
    n_new new vertices at any positions of base_order (preserving
    relative order of base).
    """
    base = list(base_order)
    new_vertices = list(range(BLOCK_N, BLOCK_N + n_new))
    total_n = len(base) + n_new
    # Choose positions for new vertices.
    out = []
    for positions in itertools.combinations(range(total_n), n_new):
        # positions are the positions where new vertices go (sorted asc).
        for perm in itertools.permutations(new_vertices):
            seq = [None] * total_n
            for p, v in zip(positions, perm):
                seq[p] = v
            i_base = 0
            for k in range(total_n):
                if seq[k] is None:
                    seq[k] = base[i_base]
                    i_base += 1
            out.append(tuple(seq))
    return out


def search_2ext(verbose=False, max_orientations=None):
    """Enumerate orientations and find asymmetric wirings."""
    good = []
    total_orientations = 2 ** (2 * BLOCK_N + 1)
    count = 0
    for c1_bits in itertools.product((0,1), repeat=BLOCK_N):
        for c2_bits in itertools.product((0,1), repeat=BLOCK_N):
            for c12_dir in (0, 1):
                count += 1
                if max_orientations and count > max_orientations:
                    return good
                T = build_combined_two(c1_bits, c2_bits, c12_dir)
                c1, c2 = BLOCK_N, BLOCK_N + 1
                # Find L-state LFOs with active hits at both c1 and c2.
                l_records = []
                for combined in insertions2(L_ORDER):
                    d = back_arc_data(T, combined)
                    if d is None: continue
                    cls1 = classify_external_hits(d["arcs"], c1, Y_PORTS)
                    cls2 = classify_external_hits(d["arcs"], c2, Y_PORTS)
                    if cls1["active_hits"] and cls2["active_hits"]:
                        l_records.append((combined, cls1, cls2))
                if not l_records: continue
                r_records = []
                for combined in insertions2(R_ORDER):
                    d = back_arc_data(T, combined)
                    if d is None: continue
                    cls1 = classify_external_hits(d["arcs"], c1, N_PORTS)
                    cls2 = classify_external_hits(d["arcs"], c2, N_PORTS)
                    if cls1["active_hits"] and cls2["active_hits"]:
                        r_records.append((combined, cls1, cls2))
                if not r_records: continue
                good.append({
                    "c1_bits": c1_bits, "c2_bits": c2_bits, "c12": c12_dir,
                    "l_witness": l_records[0],
                    "r_witness": r_records[0],
                    "l_count": len(l_records),
                    "r_count": len(r_records),
                })
                if verbose:
                    print(f"FOUND: c1={c1_bits}, c2={c2_bits}, c12={c12_dir}")
    return good


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None,
                   help="Cap on orientations to test (default: all)")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    print(f"Searching 2-external-vertex orientations "
          f"(2^{2*BLOCK_N+1} = {2**(2*BLOCK_N+1)} total)...")
    good = search_2ext(verbose=args.verbose, max_orientations=args.limit)
    print(f"Found {len(good)} orientations with active hits at both "
          f"externals in both states.")
    if args.verbose:
        for g in good[:5]:
            print(g)


if __name__ == "__main__":
    main()
