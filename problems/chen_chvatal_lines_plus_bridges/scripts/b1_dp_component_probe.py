"""Probe pair-local support components for DP-Hall.

Fix a diameter pair {p,q} and P=N[p] union N[q].  For each collided row L, use
S_L^pq = S_L cap P.  Components of the support-overlap graph have disjoint
supports, so DP-Hall is equivalent to checking each component independently.

This script profiles whether all difficult components are the full P component,
or whether proper components require their own lemma.
"""
from __future__ import annotations

import argparse
import itertools
import sys
from collections import Counter

import networkx as nx

sys.path.insert(0, "scripts")
import b1_hall_profile as hall  # noqa: E402
import core  # noqa: E402


def row_kind(row: dict) -> str:
    return "starry" if row["star_units"] else "diffuse"


def analyze_pair(n: int, edges: list[tuple[int, int]], p: int, q: int) -> dict:
    dist = core.all_pairs_distances(n, edges)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    deg2 = [sum(1 for u in range(n) if dist[v][u] == 2) for v in range(n)]
    rows = hall.collision_rows(n, edges)["rows"]
    pair_set = {p, q} | adj[p] | adj[q]
    supports = [set(row["support"]) & pair_set for row in rows]
    graph = nx.Graph()
    graph.add_nodes_from(range(len(rows)))
    for i, j in itertools.combinations(range(len(rows)), 2):
        if supports[i] & supports[j]:
            graph.add_edge(i, j)
    comps = []
    for comp_nodes in nx.connected_components(graph):
        support = set().union(*(supports[i] for i in comp_nodes)) if comp_nodes else set()
        demand = sum(rows[i]["demand"] for i in comp_nodes)
        capacity = sum(deg2[v] - 2 for v in support)
        comps.append(
            {
                "rows": sorted(comp_nodes),
                "support": sorted(support),
                "support_size": len(support),
                "support_is_pair": support == pair_set,
                "demand": demand,
                "capacity": capacity,
                "margin": capacity - demand,
                "card_margin": len(support) - demand,
                "kinds": tuple(sorted(Counter(row_kind(rows[i]) for i in comp_nodes).items())),
                "row_sizes": tuple(sorted(Counter(rows[i]["size"] for i in comp_nodes).items())),
                "support_capacity_hist": tuple(sorted(Counter(deg2[v] - 2 for v in support).items())),
                "touches_endpoint": bool({p, q} & support),
                "touches_both_sides": bool((support & ({p} | adj[p])) and (support & ({q} | adj[q]))),
            }
        )
    return {
        "p": p,
        "q": q,
        "pair_size": len(pair_set),
        "pair_capacity": sum(deg2[v] - 2 for v in pair_set),
        "total_demand": sum(row["demand"] for row in rows),
        "components": comps,
    }


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    pairs = [(p, q) for p, q in itertools.combinations(range(n), 2) if dist[p][q] == diam]
    return {"n": n, "diam": diam, "pairs": [analyze_pair(n, edges, p, q) for p, q in pairs]}


def summarize(graphs) -> dict:
    total = 0
    pair_count = 0
    comp_count = 0
    comp_fail = 0
    proper_comp_fail = 0
    proper_card_fail = 0
    min_margin = None
    min_proper_margin = None
    min_proper_card_margin = None
    full_pair_worst = 0
    examples = []
    shape_counts = Counter()
    for tag, n, edges in graphs:
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        if not hall.is_three_connected(g):
            continue
        rec = analyze(n, edges)
        if rec["diam"] < 4:
            continue
        total += 1
        for pair in rec["pairs"]:
            pair_count += 1
            for comp in pair["components"]:
                comp_count += 1
                min_margin = comp["margin"] if min_margin is None else min(min_margin, comp["margin"])
                if comp["margin"] < 0:
                    comp_fail += 1
                if comp["support_is_pair"]:
                    full_pair_worst += int(comp["margin"] == pair["pair_capacity"] - pair["total_demand"])
                else:
                    min_proper_margin = (
                        comp["margin"] if min_proper_margin is None else min(min_proper_margin, comp["margin"])
                    )
                    min_proper_card_margin = (
                        comp["card_margin"]
                        if min_proper_card_margin is None
                        else min(min_proper_card_margin, comp["card_margin"])
                    )
                    if comp["margin"] < 0:
                        proper_comp_fail += 1
                    if comp["card_margin"] < 0:
                        proper_card_fail += 1
                if len(examples) < 10 and (comp["margin"] <= 4 or comp["card_margin"] < 0):
                    examples.append({"tag": tag, "pair": (pair["p"], pair["q"]), "component": comp})
                shape_counts[
                    (
                        rec["diam"],
                        pair["pair_size"],
                        comp["support_is_pair"],
                        comp["demand"],
                        comp["support_size"],
                        comp["card_margin"],
                        comp["margin"],
                        comp["kinds"],
                        comp["row_sizes"],
                        comp["support_capacity_hist"],
                    )
                ] += 1
    return {
        "total": total,
        "pair_count": pair_count,
        "comp_count": comp_count,
        "comp_fail": comp_fail,
        "proper_comp_fail": proper_comp_fail,
        "proper_card_fail": proper_card_fail,
        "min_margin": min_margin,
        "min_proper_margin": min_proper_margin,
        "min_proper_card_margin": min_proper_card_margin,
        "full_pair_worst": full_pair_worst,
        "shape_counts": dict(shape_counts.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260706)
    parser.add_argument("--source", choices=["gnp", "sparse"], default="gnp")
    parser.add_argument("--geng", nargs="*", default=[])
    args = parser.parse_args()

    if args.g6:
        rows = []
        for g6 in args.g6:
            n, edges = core.graph6_to_edges(g6)
            rows.append((g6, n, edges))
        print({"named": summarize(rows)})
        return

    if args.geng:
        print({"geng": summarize(hall.geng_graphs(args.geng))})
    for order in args.orders:
        if args.source == "sparse":
            graphs = ((g6, order, edges) for g6, edges in hall.random_sparse(order, args.samples, args.seed + order))
        else:
            graphs = ((g6, order, edges) for g6, edges in hall.random_three_connected(order, args.samples, args.seed + order))
        print({f"{args.source}_n{order}": summarize(graphs)})


if __name__ == "__main__":
    main()
