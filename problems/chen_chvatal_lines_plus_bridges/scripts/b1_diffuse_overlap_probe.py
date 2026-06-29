"""Probe a component proof for D-CARD in the G3-Hall1 split.

D-CARD says every diffuse family Y of collided distance-2 lines has

    d(Y) <= |U(Y)|.

Under the observed collision-forest shape, diffuse rows have demand 2.  A
possible proof is purely support-overlap:

    each diffuse row has |S_L| >= 3,
    two diffuse row supports overlap in at most one vertex,
    every diffuse support-overlap component is acyclic.

Then a component with k rows has union size at least 3k-(k-1)=2k+1.
This script tests that certificate and reports the first obstruction if it fails.
"""
from __future__ import annotations

import argparse
import itertools
import sys
from collections import Counter, defaultdict

import networkx as nx

sys.path.insert(0, "scripts")
import b1_hall_profile as hall  # noqa: E402
import core  # noqa: E402


def diffuse_rows(n: int, edges: list[tuple[int, int]]) -> dict:
    data = hall.collision_rows(n, edges)
    rows = [row for row in data["rows"] if row["star_units"] == 0]
    return {**data, "rows": rows}


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    data = diffuse_rows(n, edges)
    rows = data["rows"]
    overlap = nx.Graph()
    overlap.add_nodes_from(range(len(rows)))
    max_pair_intersection = 0
    pair_overlap_fail = None
    for i, j in itertools.combinations(range(len(rows)), 2):
        inter = set(rows[i]["support"]) & set(rows[j]["support"])
        max_pair_intersection = max(max_pair_intersection, len(inter))
        if inter:
            overlap.add_edge(i, j, intersection=sorted(inter), size=len(inter))
        if len(inter) > 1 and pair_overlap_fail is None:
            pair_overlap_fail = {"rows": [i, j], "intersection": sorted(inter), "row_i": rows[i], "row_j": rows[j]}

    small_support_fail = None
    for i, row in enumerate(rows):
        if len(row["support"]) < 3:
            small_support_fail = {"row": i, "support": sorted(row["support"]), "data": row}
            break

    cycle_fail = None
    component_deficit_fail = None
    min_component_margin = None
    max_component_rows = 0
    component_shapes = Counter()
    for comp in nx.connected_components(overlap):
        comp = sorted(comp)
        support = set()
        demand = 0
        edge_count = overlap.subgraph(comp).number_of_edges()
        for i in comp:
            support.update(rows[i]["support"])
            demand += rows[i]["demand"]
        margin = len(support) - demand
        min_component_margin = margin if min_component_margin is None else min(min_component_margin, margin)
        max_component_rows = max(max_component_rows, len(comp))
        cycle_rank = edge_count - len(comp) + 1
        component_shapes[(len(comp), edge_count, cycle_rank, margin)] += 1
        if cycle_rank > 0 and cycle_fail is None:
            cycle_fail = {
                "rows": comp,
                "edges": [
                    (a, b, overlap[a][b]["intersection"])
                    for a, b in overlap.subgraph(comp).edges()
                ],
                "support": sorted(support),
                "demand": demand,
                "margin": margin,
            }
        if margin < 0 and component_deficit_fail is None:
            component_deficit_fail = {
                "rows": comp,
                "support": sorted(support),
                "demand": demand,
                "margin": margin,
            }

    return {
        "diam": data["diam"],
        "num_diffuse": len(rows),
        "small_support_fail": small_support_fail,
        "pair_overlap_fail": pair_overlap_fail,
        "cycle_fail": cycle_fail,
        "component_deficit_fail": component_deficit_fail,
        "max_pair_intersection": max_pair_intersection,
        "min_component_margin": min_component_margin,
        "max_component_rows": max_component_rows,
        "component_shapes": component_shapes,
    }


def summarize(tagged_graphs) -> dict:
    total = 0
    with_diffuse = 0
    small_support_fail = 0
    pair_overlap_fail = 0
    cycle_fail = 0
    component_deficit_fail = 0
    max_pair_intersection = 0
    max_component_rows = 0
    min_component_margin = None
    shapes = Counter()
    examples = []
    for tag, n, edges in tagged_graphs:
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        if not hall.is_three_connected(g):
            continue
        dist = core.all_pairs_distances(n, edges)
        if max(dist[i][j] for i in range(n) for j in range(n)) < 4:
            continue
        result = analyze(n, edges)
        total += 1
        if result["num_diffuse"]:
            with_diffuse += 1
        small_support_fail += int(result["small_support_fail"] is not None)
        pair_overlap_fail += int(result["pair_overlap_fail"] is not None)
        cycle_fail += int(result["cycle_fail"] is not None)
        component_deficit_fail += int(result["component_deficit_fail"] is not None)
        max_pair_intersection = max(max_pair_intersection, result["max_pair_intersection"])
        max_component_rows = max(max_component_rows, result["max_component_rows"])
        if result["min_component_margin"] is not None:
            min_component_margin = (
                result["min_component_margin"]
                if min_component_margin is None
                else min(min_component_margin, result["min_component_margin"])
            )
        shapes.update(result["component_shapes"])
        if len(examples) < 6 and (
            result["small_support_fail"] is not None
            or result["pair_overlap_fail"] is not None
            or result["cycle_fail"] is not None
            or result["component_deficit_fail"] is not None
            or result["min_component_margin"] == 0
        ):
            examples.append({"tag": tag, **result})
    return {
        "total": total,
        "with_diffuse": with_diffuse,
        "small_support_fail": small_support_fail,
        "pair_overlap_fail": pair_overlap_fail,
        "cycle_fail": cycle_fail,
        "component_deficit_fail": component_deficit_fail,
        "max_pair_intersection": max_pair_intersection,
        "max_component_rows": max_component_rows,
        "min_component_margin": min_component_margin,
        "component_shapes": dict(shapes.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260629)
    parser.add_argument("--source", choices=["gnp", "sparse"], default="gnp")
    parser.add_argument("--geng", nargs="*", default=[], help="exact geng specs like 13:20")
    parser.add_argument("--g6", nargs="*")
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
