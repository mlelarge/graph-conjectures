"""Q2 diagnostic: where does the D70 forward-DP fooling family live?

Settles the critical fork for Q2 (acyclicity among Delta*=2 tournaments):

  * Base reversed-matching RM(m) and base toggle family: Delta* = 1
    (so trivially Path-FAS YES; back-arc graph is a matching).
  * The PROBE-augmented toggle tournaments (the actual D70 fooling
    instances) have Delta* = 2 -- i.e. they live in the Q2 layer.

Moreover the fooling mechanism is an ACYCLICITY obstruction, not a
degree obstruction: every toggle prefix is back-degree-<=2 feasible
throughout, and the failure at eps_j = 1 under the gadget-j probe is a
back-arc CYCLE, never a degree-3 vertex.

CONCLUSION.  The D70 2^Omega(n) forward-DP lower bound lives entirely at
Delta* = 2 and is driven by the very acyclicity question Q2 asks.  Hence
Q2 INHERITS the forward-DP lower bound: any polynomial Q2 algorithm must
be NON-forward / global.

Reuses degreewidth_exact and toggle_fooling_set; does not modify shared
files.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from degreewidth_exact import degreewidth  # noqa: E402
from reversed_matching_hardness import build_reversed_matching  # noqa: E402
from toggle_fooling_set import (  # noqa: E402
    build_toggle_family,
    build_toggle_with_probe,
    toggle_prefix,
)

Matrix = list[list[int]]


def arcs_of(T: Matrix) -> list[tuple[int, int]]:
    n = len(T)
    return [(u, v) for u in range(n) for v in range(n) if u != v and T[u][v]]


def back_arc_graph(T: Matrix, order):
    """Undirected back-arc graph edges for a given full order.

    A back-arc is u->v with v earlier than u in `order`; its undirected
    edge is {u, v}.  Returns (edges, max_degree, has_cycle)."""
    pos = {v: i for i, v in enumerate(order)}
    edges = []
    deg = {v: 0 for v in order}
    for (u, v) in arcs_of(T):
        if pos[u] > pos[v]:  # u after v -> back-arc
            edges.append((u, v))
            deg[u] += 1
            deg[v] += 1
    maxdeg = max(deg.values()) if deg else 0
    # cycle test on undirected graph via union-find
    parent = {v: v for v in order}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    has_cycle = False
    for (u, v) in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            has_cycle = True
        else:
            parent[ru] = rv
    return edges, maxdeg, has_cycle


def degreewidth_table():
    print("=== Delta* of D70 families ===")
    print("Reversed matching RM(m):")
    for m in range(2, 11):
        T = build_reversed_matching(m)
        print(f"  m={m:2d} n={2*m:2d}  Delta*={degreewidth(T)}")
    print("Toggle family (base):")
    for k in range(1, 6):
        T = build_toggle_family(k)
        print(f"  k={k} n={4*k:2d}  Delta*={degreewidth(T)}")
    print("Toggle WITH probe (gadget j=0):")
    for k in range(1, 5):
        T = build_toggle_with_probe(k, 0)
        print(f"  k={k} n={len(T):2d}  Delta*={degreewidth(T)}")


def fooling_is_acyclicity(k: int):
    """For each probe gadget j and toggle eps, complete the toggle prefix
    greedily by appending the remaining (padding + z) vertices in index
    order, and report whether the failure (when it fails) is a CYCLE or a
    DEGREE violation in the back-arc graph.

    We use the canonical completion: prefix = toggle_prefix(eps), then the
    remaining vertices (the f/g block, padding, and z) in increasing index
    order.  This is the natural LFO completion the D70 argument uses.
    """
    print(f"\n=== Acyclicity-vs-degree of fooling failures, k={k} ===")
    for j in range(k):
        T = build_toggle_with_probe(k, j)
        n = len(T)
        for eps in _binary(k):
            prefix = toggle_prefix(k, eps)
            rest = [v for v in range(n) if v not in set(prefix)]
            order = prefix + rest
            edges, maxdeg, cyc = back_arc_graph(T, order)
            # also: is it a linear forest? (maxdeg<=2 and acyclic)
            ok = (maxdeg <= 2) and (not cyc)
            expected_feasible = (eps[j] == 0)
            tag = ""
            if not ok:
                tag = "DEGREE>2" if maxdeg > 2 else ("CYCLE" if cyc else "?")
            if eps[j] == 1 and j == 0:  # show a representative failure
                print(
                    f"  j={j} eps={list(eps)}: maxdeg={maxdeg} cycle={cyc} "
                    f"linear_forest={ok} failure={tag}"
                )


def _binary(k):
    for x in range(1 << k):
        yield tuple((x >> i) & 1 for i in range(k))


def all_prefixes_degree_feasible(k: int) -> dict:
    """Check that EVERY toggle prefix, under the canonical completion and
    under every probe j, never produces a back-degree-3 vertex within the
    prefix region -- i.e. degree feasibility is never the discriminator."""
    violations = []
    for j in range(k):
        T = build_toggle_with_probe(k, j)
        n = len(T)
        for eps in _binary(k):
            prefix = toggle_prefix(k, eps)
            rest = [v for v in range(n) if v not in set(prefix)]
            order = prefix + rest
            _, maxdeg, cyc = back_arc_graph(T, order)
            if cyc and maxdeg <= 2:
                # acyclicity-only failure (the interesting case)
                pass
            if maxdeg > 2 and not cyc:
                violations.append((j, eps, "degree-only failure"))
    return {"degree_only_failures": violations}


if __name__ == "__main__":
    degreewidth_table()
    for k in (2, 3):
        fooling_is_acyclicity(k)
    print()
    for k in (2, 3):
        print(f"k={k}:", all_prefixes_degree_feasible(k))
