"""Historical probe of the proper-support OR certificate for B1/G3-Hall1.

Former sufficient target inside the localized G3-Hall1 route:

  proper deficient component C:
    (MIN4)  min_{v in U(C)} degG2(v) >= 4
    (2CAP)  d(C) <= 2 |U(C)|

This script records structural facts about proper deficient components.  G21
later refuted G3 and the encompassing OR-reserve route, so these measurements
are diagnostic only and are not a live sufficient target for B1.
"""
from __future__ import annotations

import argparse
import itertools
import sys
from collections import Counter

import networkx as nx

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b1_hall_profile as hall  # noqa: E402
import core  # noqa: E402


def row_kind(row: dict) -> str:
    return "starry" if row["star_units"] else "diffuse"


def overlap_graph(rows: list[dict], chosen: list[int]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(chosen)
    for i, j in itertools.combinations(chosen, 2):
        if set(rows[i]["support"]) & set(rows[j]["support"]):
            graph.add_edge(i, j)
    return graph


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    den = set(data["den"])
    deg2 = data["deg2"]
    if len(rows) > 22:
        return {"skipped": True, "num_rows": len(rows)}

    proper_def = []
    lowdeg_proper = []
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        if not nx.is_connected(overlap_graph(rows, chosen)):
            continue
        support = set()
        demand = 0
        for i in chosen:
            support.update(rows[i]["support"])
            demand += rows[i]["demand"]
        if support == den or demand <= len(support):
            if support != den and support and any(deg2[v] == 3 for v in support):
                lowdeg_proper.append(
                    {
                        "chosen": chosen,
                        "demand": demand,
                        "support_size": len(support),
                        "card_margin": len(support) - demand,
                        "min_deg2": min(deg2[v] for v in support),
                        "kinds": tuple(sorted(Counter(row_kind(rows[i]) for i in chosen).items())),
                        "row_sizes": tuple(sorted(Counter(rows[i]["size"] for i in chosen).items())),
                        "support_deg2_hist": tuple(sorted(Counter(deg2[v] for v in support).items())),
                    }
                )
            continue

        kinds = Counter(row_kind(rows[i]) for i in chosen)
        row_sizes = Counter(rows[i]["size"] for i in chosen)
        row_demands = Counter(rows[i]["demand"] for i in chosen)
        support_inc = Counter()
        for i in chosen:
            for v in rows[i]["support"]:
                support_inc[v] += 1
        match_graph = nx.Graph()
        left = [("r", i) for i in chosen]
        right = [("v", v) for v in support]
        match_graph.add_nodes_from(left, bipartite=0)
        match_graph.add_nodes_from(right, bipartite=1)
        for i in chosen:
            for v in rows[i]["support"]:
                match_graph.add_edge(("r", i), ("v", v))
        matching = nx.algorithms.bipartite.maximum_matching(match_graph, top_nodes=left)
        row_matching_ok = sum(1 for node in left if node in matching) == len(left)
        proper_def.append(
            {
                "chosen": chosen,
                "k": len(chosen),
                "demand": demand,
                "support_size": len(support),
                "deficit": demand - len(support),
                "two_cap_margin": 2 * len(support) - demand,
                "row_matching_ok": row_matching_ok,
                "min_deg2": min(deg2[v] for v in support),
                "extra": sum(deg2[v] - 3 for v in support),
                "kinds": tuple(sorted(kinds.items())),
                "row_sizes": tuple(sorted(row_sizes.items())),
                "row_demands": tuple(sorted(row_demands.items())),
                "support_inc_hist": tuple(sorted(Counter(support_inc.values()).items())),
                "support_deg2_hist": tuple(sorted(Counter(deg2[v] for v in support).items())),
                "missing_den_size": len(den - support),
                "support": sorted(support),
                "missing_den": sorted(den - support),
                "rows": [
                    {
                        "index": i,
                        "kind": row_kind(rows[i]),
                        "size": rows[i]["size"],
                        "demand": rows[i]["demand"],
                        "support": sorted(rows[i]["support"]),
                        "pairs": rows[i]["pairs"],
                        "line_den": rows[i]["line_den"],
                        "endpoints_de": rows[i]["endpoints_de"],
                    }
                    for i in chosen
                ],
            }
        )
    return {"skipped": False, "num_rows": len(rows), "proper_def": proper_def, "lowdeg_proper": lowdeg_proper}


def summarize(graphs) -> dict:
    total = 0
    skipped = 0
    proper_def_graphs = 0
    min_two_cap_margin = None
    min_min_deg2 = None
    max_deficit = 0
    lowdeg_proper_graphs = 0
    min_lowdeg_margin = None
    shape_counts = Counter()
    lowdeg_shape_counts = Counter()
    bad = Counter()
    examples = []
    for tag, n, edges in graphs:
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        if not hall.is_three_connected(g):
            continue
        dist = core.all_pairs_distances(n, edges)
        if max(dist[i][j] for i in range(n) for j in range(n)) < 4:
            continue
        rec = analyze(n, edges)
        if rec.get("skipped"):
            skipped += 1
            continue
        total += 1
        if rec["proper_def"]:
            proper_def_graphs += 1
        if rec["lowdeg_proper"]:
            lowdeg_proper_graphs += 1
        for comp in rec["lowdeg_proper"]:
            min_lowdeg_margin = (
                comp["card_margin"]
                if min_lowdeg_margin is None
                else min(min_lowdeg_margin, comp["card_margin"])
            )
            lowdeg_shape_counts[
                (
                    comp["demand"],
                    comp["support_size"],
                    comp["card_margin"],
                    comp["min_deg2"],
                    comp["kinds"],
                    comp["row_sizes"],
                    comp["support_deg2_hist"],
                )
            ] += 1
        for comp in rec["proper_def"]:
            min_two_cap_margin = (
                comp["two_cap_margin"]
                if min_two_cap_margin is None
                else min(min_two_cap_margin, comp["two_cap_margin"])
            )
            min_min_deg2 = comp["min_deg2"] if min_min_deg2 is None else min(min_min_deg2, comp["min_deg2"])
            max_deficit = max(max_deficit, comp["deficit"])
            shape_counts[
                (
                    comp["k"],
                    comp["demand"],
                    comp["support_size"],
                    comp["deficit"],
                    comp["two_cap_margin"],
                    comp["min_deg2"],
                    comp["kinds"],
                    comp["row_sizes"],
                    comp["support_inc_hist"],
                    comp["support_deg2_hist"],
                    comp["missing_den_size"],
                )
            ] += 1
            if comp["kinds"] != (("diffuse", comp["k"]),):
                bad["starry_proper_def"] += 1
            if comp["row_sizes"] != ((2, comp["k"]),):
                bad["non_pair_collision"] += 1
            if comp["min_deg2"] < 4:
                bad["min4"] += 1
            if comp["two_cap_margin"] < 0:
                bad["2cap"] += 1
            if not comp["row_matching_ok"]:
                bad["row_matching"] += 1
            if len(examples) < 8:
                examples.append({"tag": tag, **comp})
    return {
        "total": total,
        "skipped": skipped,
        "proper_def_graphs": proper_def_graphs,
        "lowdeg_proper_graphs": lowdeg_proper_graphs,
        "min_lowdeg_margin": min_lowdeg_margin,
        "min_two_cap_margin": min_two_cap_margin,
        "min_min_deg2": min_min_deg2,
        "max_deficit": max_deficit,
        "bad": dict(bad),
        "shape_counts": dict(shape_counts.most_common(12)),
        "lowdeg_shape_counts": dict(lowdeg_shape_counts.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260702)
    parser.add_argument("--source", choices=["gnp", "sparse"], default="gnp")
    parser.add_argument("--geng", nargs="*", default=[])
    args = parser.parse_args()

    if args.g6:
        graphs = []
        for g6 in args.g6:
            n, edges = core.graph6_to_edges(g6)
            graphs.append((g6, n, edges))
        print({"named": summarize(graphs)})
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
