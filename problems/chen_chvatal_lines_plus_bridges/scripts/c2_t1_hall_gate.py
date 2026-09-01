"""T1 / block-local (4') Hall gate.

For a 2-connected graph B with marked vertex u, put S = V(B) - {u}.
For s in S:

  Sigma_s = {x in S : [u x s] or [u s x]}
  A_s     = line_B(u,s) - {u}
  D'      = {line_B(a,b) : u notin line_B(a,b), line_B(a,b) != S}

The block-local inequality (4') is

  #Sigma + #proper(A_s) + #D' >= |S|.

This script verifies a stronger SDR statement.  Choose one representative
from each Sigma-fiber.  Every non-representative vertex can be matched to
either its proper apex trace A_s or to a D' line containing it, with all chosen
resources distinct.  Saturating this matching proves (4') for that block.

Default mode checks H5 leaf blocks in connected pendant-free diam>=4 graphs.
Use --all-marked to check every 2-connected marked graph of the given orders.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import sys
from collections import defaultdict

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


def induced_metric(g, vertices):
    labels = sorted(vertices)
    idx = {v: i for i, v in enumerate(labels)}
    edges = [(idx[a], idx[b]) for a, b in g.subgraph(labels).edges()]
    return labels, idx, core.all_pairs_distances(len(labels), edges)


def block_local_data(g, block, u):
    labels, idx, dist = induced_metric(g, block)
    s_vertices = [v for v in labels if v != u]
    full_s = frozenset(s_vertices)
    ui = idx[u]

    sigma = {}
    apex = {}
    for s in s_vertices:
        si = idx[s]
        dus = dist[ui][si]
        ray = set()
        for x in s_vertices:
            xi = idx[x]
            if dist[ui][xi] + dist[xi][si] == dus:
                ray.add(x)
            elif dus + dist[si][xi] == dist[ui][xi]:
                ray.add(x)
        sigma[s] = frozenset(ray)

        line = core.line_of_pair(dist, len(labels), ui, si)
        apex[s] = frozenset(labels[i] for i in line) - {u}

    dprime = set()
    for a, b in itertools.combinations(labels, 2):
        line = core.line_of_pair(dist, len(labels), idx[a], idx[b])
        lifted = frozenset(labels[i] for i in line)
        if u not in lifted and lifted != full_s:
            dprime.add(lifted)

    return s_vertices, full_s, sigma, apex, dprime, dist, idx


def hall_check(g, block, u):
    s_vertices, full_s, sigma, apex, dprime, dist, idx = block_local_data(g, block, u)

    fibers = defaultdict(list)
    for s in s_vertices:
        fibers[sigma[s]].append(s)

    left = []
    for members in fibers.values():
        # Any one representative per Sigma-fiber is enough.  The shallowest
        # representative makes the diagnostic stable.
        rep = min(members, key=lambda s: (dist[idx[u]][idx[s]], s))
        left.extend(s for s in members if s != rep)

    bigraph = nx.Graph()
    left_nodes = [("L", s) for s in left]
    bigraph.add_nodes_from(left_nodes, bipartite=0)

    right_nodes = set()
    for s in left:
        incident = []
        if apex[s] != full_s:
            incident.append(("A", apex[s]))
        for line in dprime:
            if s in line:
                incident.append(("D", line))
        for r in incident:
            right_nodes.add(("R", r))
            bigraph.add_edge(("L", s), ("R", r))

    bigraph.add_nodes_from(right_nodes, bipartite=1)
    matching = nx.algorithms.bipartite.maximum_matching(bigraph, top_nodes=left_nodes)
    matched = sum(1 for node in left_nodes if node in matching)

    return {
        "ok": matched == len(left),
        "left": len(left),
        "matched": matched,
        "nS": len(s_vertices),
        "nSigma": len(fibers),
        "Adist": len({a for a in apex.values() if a != full_s}),
        "Dprime": len(dprime),
        "margin4": len(fibers) + len({a for a in apex.values() if a != full_s}) + len(dprime) - len(s_vertices),
        "unmatched": [s for s in left if ("L", s) not in matching],
    }


def iter_h5_leaf_blocks(order):
    proc = subprocess.run(["geng", "-c", "-d2", "-q", str(order)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        if core.has_pendant_edge(n, edges):
            continue
        dist = core.all_pairs_distances(n, edges)
        if diameter_from_dist(dist) < 4:
            continue
        g = graph_from_edges(n, edges)
        if nx.is_biconnected(g):
            continue
        for block, u in leaf_blocks(g):
            yield g6, g, block, u


def iter_all_marked_blocks(order):
    proc = subprocess.run(["geng", "-c", "-q", str(order)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        g = graph_from_edges(n, edges)
        if not nx.is_biconnected(g):
            continue
        block = set(range(n))
        for u in range(n):
            yield g6, g, block, u


def run_order(order, all_marked=False, max_examples=8):
    iterator = iter_all_marked_blocks(order) if all_marked else iter_h5_leaf_blocks(order)
    total = 0
    failures = []
    min_margin = None
    min_left_slack = None
    for g6, g, block, u in iterator:
        total += 1
        row = hall_check(g, block, u)
        min_margin = row["margin4"] if min_margin is None else min(min_margin, row["margin4"])
        left_slack = row["matched"] - row["left"]
        min_left_slack = left_slack if min_left_slack is None else min(min_left_slack, left_slack)
        if not row["ok"] and len(failures) < max_examples:
            failures.append({"graph6": g6, "u": u, "block": sorted(block), **row})

    return {
        "n": order,
        "mode": "all_marked_2connected" if all_marked else "h5_leaf_blocks",
        "blocks": total,
        "failures": len(failures),
        "min_margin4": min_margin,
        "min_matching_slack": min_left_slack,
        "examples": failures,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("orders", nargs="*", type=int, default=[8, 9])
    ap.add_argument("--all-marked", action="store_true",
                    help="check every 2-connected marked graph, not only H5 leaf blocks")
    args = ap.parse_args()
    print(json.dumps([run_order(n, all_marked=args.all_marked) for n in args.orders], indent=2))


if __name__ == "__main__":
    main()
