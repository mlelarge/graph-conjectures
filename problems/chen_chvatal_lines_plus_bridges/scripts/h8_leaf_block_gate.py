"""H8 structural-induction gate for Chen-Chvatal H5.

H5 target:
    every connected pendant-free graph G with diam(G) >= 4 has ell(G) >= |G|.

The earlier explicit line-counting charges are dead.  This gate tests a
different induction invariant for the non-2-connected case.

For a non-2-connected pendant-free graph, every leaf block is nontrivial
(not a bridge leaf).  If B is a leaf block with cut vertex u, put
S = B - {u} and R = G - S.  The desired recursive inequality is

    ell(G) - ell(R) >= |S| + max(0, |R| - ell(R)).

The right-hand deficit term means that peeling B pays for the deleted
vertices and also covers any line deficit left in the remaining connected
graph R.  If this can be proved symbolically, all non-2-connected H5 inputs
reduce to the 2-connected core.

This script is an exact oracle gate: it enumerates connected min-degree-2
graphs with geng, filters to diam>=4, and reports whether some leaf block
satisfies the recursive inequality.  No sampling or heuristic line counts.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter

import networkx as nx

import core


def diameter(n, edges):
    dist = core.all_pairs_distances(n, edges)
    return max(dist[i][j] for i in range(n) for j in range(n))


def nx_from_edges(n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    return g


def ell_nx(g):
    h = nx.convert_node_labels_to_integers(g)
    return core.ell(h.number_of_nodes(), list(h.edges()))


def leaf_blocks(g):
    """Return (block_vertices, cut_vertex) for non-bridge leaf blocks."""
    articulations = set(nx.articulation_points(g))
    out = []
    for block in nx.biconnected_components(g):
        block = set(block)
        cuts = block & articulations
        if len(cuts) == 1 and len(block) >= 3:
            out.append((block, next(iter(cuts))))
    return out


def leaf_margins(g6, n, edges):
    """All recursive margins for leaf blocks of one graph."""
    g = nx_from_edges(n, edges)
    ell_g = core.ell(n, edges)
    rows = []
    for block, cut in leaf_blocks(g):
        removed = block - {cut}
        rest_vertices = set(g.nodes()) - removed
        rest = g.subgraph(rest_vertices).copy()
        ell_rest = ell_nx(rest)
        deficit_rest = max(0, rest.number_of_nodes() - ell_rest)
        delta = ell_g - ell_rest
        margin = delta - len(removed) - deficit_rest
        rows.append({
            "margin": margin,
            "delta": delta,
            "removed": len(removed),
            "rest_deficit": deficit_rest,
            "cut": cut,
            "block": sorted(block),
            "ell_rest": ell_rest,
            "n_rest": rest.number_of_nodes(),
        })
    rows.sort(key=lambda r: (r["margin"], r["delta"], r["removed"]), reverse=True)
    return rows


def run_n(order, max_worst=10):
    cmd = ["geng", "-c", "-q", "-d2", str(order)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)

    total_scope = 0
    non_biconnected = 0
    no_leaf = 0
    failures = []
    worst = []
    stats = Counter()

    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        if core.has_pendant_edge(n, edges):
            continue
        diam = diameter(n, edges)
        if diam < 4:
            continue
        total_scope += 1

        g = nx_from_edges(n, edges)
        if nx.is_biconnected(g):
            stats["biconnected"] += 1
            continue

        non_biconnected += 1
        rows = leaf_margins(g6, n, edges)
        if not rows:
            no_leaf += 1
            failures.append({
                "graph6": g6,
                "reason": "no non-bridge leaf block",
                "ell": core.ell(n, edges),
                "br": core.bridges_count(n, edges),
                "diam": diam,
            })
            continue

        best = rows[0]
        record = {
            "graph6": g6,
            "ell": core.ell(n, edges),
            "br": core.bridges_count(n, edges),
            "diam": diam,
            "best": best,
        }
        worst.append(record)
        worst.sort(key=lambda r: r["best"]["margin"])
        worst = worst[:max_worst]

        if best["margin"] < 0:
            failures.append(record)

    return {
        "n": order,
        "total_pendant_free_diam_ge4": total_scope,
        "biconnected": stats["biconnected"],
        "non_biconnected": non_biconnected,
        "no_leaf": no_leaf,
        "n_failures": len(failures),
        "min_best_margin": None if not worst else min(r["best"]["margin"] for r in worst),
        "worst": worst,
        "failures": failures[:max_worst],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("orders", nargs="*", type=int, default=[8, 9])
    ap.add_argument("--max-worst", type=int, default=10)
    args = ap.parse_args()
    out = {str(n): run_n(n, max_worst=args.max_worst) for n in args.orders}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    sys.exit(main())
