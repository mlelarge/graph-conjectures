"""Probe a diameter-pair strengthening of the B1/G3 anti-correlation.

Global G3 is

    total_demand = 2*collisions <= E(DEN),
    E(U)=sum_{v in U}(degG2(v)-2),
    DEN=DE union N(DE).

This probe tests the stronger pair-local target:

    (DP-G3) for every diameter pair {p,q},
            total_demand <= E(N[p] union N[q]).

Since N[p] union N[q] is a subset of DEN, DP-G3 implies G3.  The script also
tests the even stronger pair-local Hall statement using the existing expanded
collision supports intersected with N[p] union N[q].
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


def pair_support(rows: list[dict], chosen: list[int], pair_set: set[int]) -> tuple[int, set[int]]:
    demand = 0
    support: set[int] = set()
    for i in chosen:
        demand += rows[i]["demand"]
        support.update(set(rows[i]["support"]) & pair_set)
    return demand, support


def pair_hall_worst(rows: list[dict], deg2: list[int], pair_set: set[int]) -> dict | None:
    if len(rows) > 22:
        return {"skipped": True, "num_rows": len(rows)}
    worst = None
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        demand, support = pair_support(rows, chosen, pair_set)
        supply = sum(deg2[v] - 2 for v in support)
        record = {
            "skipped": False,
            "chosen": chosen,
            "demand": demand,
            "supply": supply,
            "margin": supply - demand,
            "support": sorted(support),
        }
        if worst is None or record["margin"] < worst["margin"]:
            worst = record
    return worst


def row_kind(row: dict) -> str:
    return "starry" if row["star_units"] else "diffuse"


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    deg2 = [sum(1 for u in range(n) if dist[v][u] == 2) for v in range(n)]
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    total_demand = sum(row["demand"] for row in rows)
    pairs = [(p, q) for p, q in itertools.combinations(range(n), 2) if dist[p][q] == diam]
    pair_records = []
    for p, q in pairs:
        pair_set = {p, q} | adj[p] | adj[q]
        supply = sum(deg2[v] - 2 for v in pair_set)
        hall_worst = pair_hall_worst(rows, deg2, pair_set)
        layer_counts = Counter(dist[p][v] for v in range(n) if dist[p][v] + dist[q][v] == diam)
        off_geodesic = [v for v in range(n) if dist[p][v] + dist[q][v] != diam]
        pair_records.append(
            {
                "pair": (p, q),
                "pair_set": sorted(pair_set),
                "supply": supply,
                "margin": supply - total_demand,
                "hall_worst": hall_worst,
                "layer_counts": tuple(sorted(layer_counts.items())),
                "off_geodesic": off_geodesic,
            }
        )
    return {
        "n": n,
        "diam": diam,
        "num_rows": len(rows),
        "total_demand": total_demand,
        "row_kinds": tuple(sorted(Counter(row_kind(row) for row in rows).items())),
        "row_sizes": tuple(sorted(Counter(row["size"] for row in rows).items())),
        "diameter_pairs": pair_records,
    }


def summarize(graphs) -> dict:
    total = 0
    dp_fail = 0
    pair_hall_fail = 0
    pair_hall_skipped = 0
    min_pair_margin = None
    min_pair_hall_margin = None
    max_pairs = 0
    off_geodesic_graphs = 0
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
        max_pairs = max(max_pairs, len(rec["diameter_pairs"]))
        graph_has_off = any(pair["off_geodesic"] for pair in rec["diameter_pairs"])
        off_geodesic_graphs += int(graph_has_off)
        for pair in rec["diameter_pairs"]:
            min_pair_margin = pair["margin"] if min_pair_margin is None else min(min_pair_margin, pair["margin"])
            if pair["margin"] < 0:
                dp_fail += 1
                if len(examples) < 8:
                    examples.append({"tag": tag, "failure": "dp_g3", **rec, "bad_pair": pair})
            hw = pair["hall_worst"]
            if hw is not None:
                if hw.get("skipped"):
                    pair_hall_skipped += 1
                else:
                    min_pair_hall_margin = (
                        hw["margin"] if min_pair_hall_margin is None else min(min_pair_hall_margin, hw["margin"])
                    )
                    if hw["margin"] < 0:
                        pair_hall_fail += 1
                        if len(examples) < 8:
                            examples.append({"tag": tag, "failure": "pair_hall", **rec, "bad_pair": pair})
        shape_counts[
            (
                rec["diam"],
                rec["total_demand"],
                len(rec["diameter_pairs"]),
                rec["row_kinds"],
                rec["row_sizes"],
                tuple(sorted(pair["margin"] for pair in rec["diameter_pairs"])[:4]),
                graph_has_off,
            )
        ] += 1
    return {
        "total": total,
        "dp_fail": dp_fail,
        "pair_hall_fail": pair_hall_fail,
        "pair_hall_skipped": pair_hall_skipped,
        "min_pair_margin": min_pair_margin,
        "min_pair_hall_margin": min_pair_hall_margin,
        "max_diameter_pairs": max_pairs,
        "off_geodesic_graphs": off_geodesic_graphs,
        "shape_counts": dict(shape_counts.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260704)
    parser.add_argument("--source", choices=["gnp", "sparse"], default="gnp")
    parser.add_argument("--geng", nargs="*", default=[], help="exact geng specs like 13:20:22")
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
