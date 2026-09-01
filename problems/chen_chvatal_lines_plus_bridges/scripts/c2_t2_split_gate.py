"""Historical T2 diagnostic for the deficit branch.

For a leaf block B glued to R at u, C2 in the deficit branch ell(R)<|R|
is exactly ell(G)>=|G|. The sound inequality is coupled:

  (P - |S|) + Q >= deficit(R).

This script checks the historical numerical target

  Q + nSigmaP*nT - nSigma >= deficit(R).        (*)

The former route combined (*) with a claimed product-to-P lower bound. That
bridge is false, so (*) is not a sufficient reduction and passing this script
does not prove C2. The gate is retained only to reproduce the historical
diagnostics over deficient leaf blocks in the H5 census.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import sys
from collections import Counter

import networkx as nx

sys.path.insert(0, os.path.dirname(__file__))
import core  # noqa: E402


def graph_from_edges(n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    return g


def diameter_from_dist(dist):
    n = len(dist)
    return max(dist[i][j] for i in range(n) for j in range(n))


def leaf_blocks(g):
    arts = set(nx.articulation_points(g))
    out = []
    for block in nx.biconnected_components(g):
        block = set(block)
        cuts = block & arts
        if len(cuts) == 1 and len(block) >= 3:
            out.append((block, next(iter(cuts))))
    return out


def ell_of_induced(g, vertices):
    labels = sorted(vertices)
    idx = {v: i for i, v in enumerate(labels)}
    edges = [(idx[a], idx[b]) for a, b in g.subgraph(labels).edges()]
    lines = set()
    dist = core.all_pairs_distances(len(labels), edges)
    for a, b in itertools.combinations(range(len(labels)), 2):
        lines.add(core.line_of_pair(dist, len(labels), a, b))
    return len(lines)


def block_row(n, g, dist_g, glines, block, u):
    s_side = set(block) - {u}
    r_side = set(range(n)) - s_side
    full_s = frozenset(s_side)

    ell_r = ell_of_induced(g, r_side)
    deficit = len(r_side) - ell_r
    if deficit <= 0:
        return None

    z_count = sum(1 for line in glines if (line & s_side) == set() or (line & s_side) == full_s)
    q = z_count - ell_r

    s0 = next(iter(s_side))
    r_other = [p for p in sorted(r_side) if p != u]
    sigma_values = {frozenset(core.line_of_pair(dist_g, n, s, r_other[0]) & s_side) for s in s_side}
    n_sigma = len(sigma_values)
    n_sigma_p = len({x for x in sigma_values if x != full_s})
    t_values = {frozenset(core.line_of_pair(dist_g, n, s0, p) & r_side) for p in r_other}
    n_t = len(t_values)

    core_margin = q + n_sigma_p * n_t - n_sigma - deficit
    r_margin = q + n_t - deficit
    thin_margin = q + 1 - deficit if n_t == 2 else None
    block_term = n_sigma_p * n_t - n_sigma

    return {
        "nS": len(s_side),
        "nR": len(r_side),
        "ellR": ell_r,
        "deficit": deficit,
        "Q": q,
        "nSigma": n_sigma,
        "nSigmaP": n_sigma_p,
        "nT": n_t,
        "block_term": block_term,
        "core_margin": core_margin,
        "r_margin_Q_plus_nT": r_margin,
        "thin_margin_Q_plus_1": thin_margin,
        "term_lt_nT": block_term < n_t,
    }


def run_order(order, max_examples=10):
    proc = subprocess.run(["geng", "-c", "-d2", "-q", str(order)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)

    rows = []
    failures = []
    term_exceptions = []
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        if core.has_pendant_edge(n, edges):
            continue
        dist_g = core.all_pairs_distances(n, edges)
        if diameter_from_dist(dist_g) < 4:
            continue
        g = graph_from_edges(n, edges)
        if nx.is_biconnected(g):
            continue
        glines = {core.line_of_pair(dist_g, n, a, b) for a, b in itertools.combinations(range(n), 2)}
        for block, u in leaf_blocks(g):
            row = block_row(n, g, dist_g, glines, block, u)
            if row is None:
                continue
            rows.append(row)
            if row["core_margin"] < 0 and len(failures) < max_examples:
                failures.append({"graph6": g6, "u": u, "block": sorted(block), **row})
            if row["term_lt_nT"] and len(term_exceptions) < max_examples:
                term_exceptions.append({"graph6": g6, "u": u, "block": sorted(block), **row})

    hist_nt = Counter(r["nT"] for r in rows)
    return {
        "n": order,
        "deficient_blocks": len(rows),
        "core_failures": sum(1 for r in rows if r["core_margin"] < 0),
        "min_core_margin": None if not rows else min(r["core_margin"] for r in rows),
        "min_r_margin_Q_plus_nT": None if not rows else min(r["r_margin_Q_plus_nT"] for r in rows),
        "term_lt_nT_count": sum(1 for r in rows if r["term_lt_nT"]),
        "nT_hist": dict(sorted(hist_nt.items())),
        "failures": failures,
        "term_lt_nT_examples": term_exceptions,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("orders", nargs="*", type=int, default=[8, 9])
    args = ap.parse_args()
    print(json.dumps([run_order(n) for n in args.orders], indent=2))


if __name__ == "__main__":
    main()
