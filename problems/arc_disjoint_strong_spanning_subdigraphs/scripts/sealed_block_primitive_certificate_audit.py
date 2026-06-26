"""Audit primitive sealed-block clauses that imply HBO and OC.

This is the executable companion to D73.  It checks the clauses that are
supposed to come directly from the existing C3/C7/CL/DT machinery:

  * C7 reserve expansion in the cage;
  * u's root fan into the head block;
  * C3 hooks from the head block into the cage reserve;
  * semicompleteness of the head block, giving at most one weak source;
  * the outside-core certificate behind FSQ.

The script is not a proof that every abstract sealed block has these
clauses; it audits the D42/D63/D66 normal forms against the primitive
clauses isolated in D73.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_kernel_witness import dbullet_arcs  # noqa: E402
from digraph import Digraph  # noqa: E402
from local_normal_form_audit import (  # noqa: E402
    D63_REVERSE_HEAD,
    D66_RHO_ENTRY,
    Q0,
    V2_HOST,
    all_subsets,
    host_from_db,
    relabel_core_arcs,
)


U = 2
RESERVE = frozenset((3, 4, 5))
HEADS = frozenset((6, 7, 8))
CAGE = frozenset((U,)) | RESERVE
W1 = 10
OUTSIDE = frozenset(V2_HOST) - Q0
OUTSIDE_CORE = OUTSIDE - {W1}


def core_edges(extras):
    db = tuple(dbullet_arcs()) + tuple(extras)
    host = tuple(host_from_db(db))
    core_arcs = relabel_core_arcs(host, V2_HOST)
    return tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)


def powerset_nonempty(vertices):
    vertices = tuple(sorted(vertices))
    for mask in range(1, 1 << len(vertices)):
        yield frozenset(vertices[i] for i in range(len(vertices)) if (mask >> i) & 1)


def arcs_between(edges, left, right):
    left = set(left)
    right = set(right)
    return sorted((u, v) for u, v in edges if u in left and v in right)


def induced_lambda(edges, vertices):
    vertices = tuple(sorted(vertices))
    rel = {v: i for i, v in enumerate(vertices)}
    arcs = [(rel[u], rel[v]) for u, v in edges if u in rel and v in rel]
    return Digraph.from_arcs(range(len(vertices)), arcs).arc_connectivity()


def head_sources(edges):
    sources = []
    for z in sorted(HEADS):
        incoming = arcs_between(edges, HEADS - {z}, {z})
        if not incoming:
            sources.append(z)
    return sources


def low_head_complements(edges):
    lows = []
    for T in all_subsets(Q0):
        incoming = arcs_between(edges, Q0 - T, T)
        if len(incoming) <= 1:
            lows.append((tuple(sorted(T)), tuple(incoming)))
    return lows


def audit(name, extras):
    edges = core_edges(extras)
    edge_set = set(edges)

    reserve_expansion = [
        (tuple(sorted(P)), tuple(arcs_between(edges, P, CAGE - P)))
        for P in powerset_nonempty(RESERVE)
    ]
    root_fan = [(U, z) for z in sorted(HEADS)]
    hooks = [(z, r) for z in sorted(HEADS) for r in sorted(RESERVE)]
    head_pairs = [
        (a, b)
        for a in sorted(HEADS)
        for b in sorted(HEADS)
        if a < b
    ]
    head_semicomplete_missing = [
        (a, b) for a, b in head_pairs
        if (a, b) not in edge_set and (b, a) not in edge_set
    ]
    sources = head_sources(edges)

    w1_exits = arcs_between(edges, {W1}, OUTSIDE_CORE)
    returns_to_w1 = arcs_between(edges, OUTSIDE_CORE, {W1})
    outside_core_lambda = induced_lambda(edges, OUTSIDE_CORE)

    assert all(len(row[1]) >= 2 for row in reserve_expansion), (
        name,
        reserve_expansion,
    )
    assert all(e in edge_set for e in root_fan), (name, root_fan)
    assert all(e in edge_set for e in hooks), (name, "hooks")
    assert not head_semicomplete_missing, (name, head_semicomplete_missing)
    assert len(sources) <= 1, (name, sources)
    assert len(w1_exits) >= 1, (name, w1_exits)
    assert len(returns_to_w1) >= 2, (name, returns_to_w1)
    assert outside_core_lambda >= 2, (name, outside_core_lambda)

    reverse_head = D63_REVERSE_HEAD in extras
    expected_lows = [] if reverse_head else [((6,), ((2, 6),))]
    assert low_head_complements(edges) == expected_lows, (
        name,
        low_head_complements(edges),
    )

    print(f"\n{name}")
    print(f"  extras={extras}")
    print(f"  min_reserve_expansion={min(len(row[1]) for row in reserve_expansion)}")
    print(f"  root_fan={root_fan}")
    print(f"  head_sources={sources}")
    print(f"  w1_exits={w1_exits}")
    print(f"  returns_to_w1={returns_to_w1}")
    print(f"  outside_core_lambda={outside_core_lambda}")
    print(f"  low_head_complements={low_head_complements(edges)}")


def main():
    print("Sealed-block primitive certificate audit")
    audit("D42 original", ())
    audit("D63 reverse-head", (D63_REVERSE_HEAD,))
    audit("D66 rho-entry", (D66_RHO_ENTRY,))
    audit("D63+D66 combined", (D63_REVERSE_HEAD, D66_RHO_ENTRY))
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
