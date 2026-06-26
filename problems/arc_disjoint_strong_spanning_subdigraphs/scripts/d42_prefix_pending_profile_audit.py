r"""Audit the full D42 prefix-plus-pending profile used by D61.

D61 assumes that for each deficient prefix Q and every subset J of
pending vertices, the original host cut Q union J has the form

    b(Q) + sum_{i notin J} e_i(Q) + sum_{i in J} f_i(Q).

Here b(Q) is the split-core out-size, e_i(Q) counts arcs Q -> i, and
f_i(Q) counts arcs i -> (core \ Q).  This script verifies that formula
on D42, checks 3-arc-strongness on all Q union J cuts, and prints the
capacity inequalities used in the cut-cover selection proof.
"""
from __future__ import annotations

import itertools
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_kernel_witness import host_arcs  # noqa: E402
from d42_split_predicate_tester import (  # noqa: E402
    d42_split_setup,
    deficient_core_cuts,
)


def out_cut(arcs, side):
    side = set(side)
    return sum(1 for u, v in arcs if u in side and v not in side)


def cut_vertices(v2, mask):
    return tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1)


def main():
    v2, core_arcs_rel, _rel, pending_vertices, _per_vertex = d42_split_setup()
    core_arcs = [(v2[u], v2[v]) for u, v in core_arcs_rel]
    deficient = deficient_core_cuts(len(v2), core_arcs_rel)
    host = tuple(host_arcs())
    v2_set = set(v2)
    chord_endpoints = {0, 1}

    print("D42 prefix-plus-pending profile audit")
    print(f"pending_vertices={pending_vertices}")
    print(f"deficient_count={len(deficient)}")

    for idx, (mask, core_out) in enumerate(deficient):
        q_name = ("Q-", "Q0", "Q+")[idx]
        Q = set(cut_vertices(v2, mask))
        endpoint_exits = sorted((u, v) for u, v in host if u in Q and v in chord_endpoints)
        endpoint_entries = sorted((u, v) for u, v in host if u in chord_endpoints and v in Q)
        print(f"\n{q_name}: core_out={core_out} cut={tuple(sorted(Q))}")
        print(f"  endpoint_exits={endpoint_exits}")
        print(f"  endpoint_entries={endpoint_entries}")
        assert not endpoint_exits
        assert not endpoint_entries

        min_sum = 0
        table = []
        for s in pending_vertices:
            noncore_in = sorted(u for u, v in host if v == s and u not in v2_set)
            noncore_out = sorted(v for u, v in host if u == s and v not in v2_set)
            e = sum(1 for u, v in host if u in Q and v == s)
            f = sum(1 for u, v in host if u == s and v in v2_set - Q)
            table.append((s, e, f, min(e, f), noncore_in, noncore_out))
            min_sum += min(e, f)
        print("  pending table: s e_i f_i min noncore_in noncore_out")
        for row in table:
            print(f"    {row}")
            assert not row[4]
            assert not row[5]
        print(f"  min_sum={min_sum} required_by_lambda={3 - core_out}")
        assert min_sum >= 3 - core_out

        for r in range(len(pending_vertices) + 1):
            for J_tuple in itertools.combinations(pending_vertices, r):
                J = set(J_tuple)
                side = Q | J
                actual = out_cut(host, side)
                formula = core_out
                for s, e, f, *_rest in table:
                    formula += f if s in J else e
                print(f"    J={J_tuple}: actual={actual} formula={formula}")
                assert actual == formula
                assert actual >= 3

    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
