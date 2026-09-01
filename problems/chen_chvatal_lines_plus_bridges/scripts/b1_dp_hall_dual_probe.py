"""Profile the dual cuts for the refuted diameter-pair Hall target.

For a diameter pair {p,q}, write P=N[p] union N[q].  For a collided row L, use
the existing expanded support S_L from b1_hall_profile, but restrict it to P.

DP-Hall dual:

    for every U subset P:
        sum_{L: S_L cap P subset U} demand(L) <= sum_{v in U}(degG2(v)-2).

This Hall strengthening is now known to be false in sparse 3-connected graphs:
a collided row can have empty restricted support for a diameter pair.  The
scalar DP-G3 target can have large margin on that witness, but G21 later refuted
DP-G3 itself.  This script is retained as a guard and a way to reproduce the
historical Hall refutation, not as a live B1 route.
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


def analyze_pair(n: int, edges: list[tuple[int, int]], p: int, q: int, cap: int) -> dict:
    dist = core.all_pairs_distances(n, edges)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    deg2 = [sum(1 for u in range(n) if dist[v][u] == 2) for v in range(n)]
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    pair_set = {p, q} | adj[p] | adj[q]
    p_list = sorted(pair_set)
    row_records = []
    for i, row in enumerate(rows):
        support = set(row["support"]) & pair_set
        row_records.append(
            {
                "index": i,
                "kind": row_kind(row),
                "size": row["size"],
                "demand": row["demand"],
                "support": support,
                "support_size": len(support),
                "support_capacity": sum(deg2[v] - 2 for v in support),
                "touches_endpoint": bool({p, q} & support),
                "touches_both_sides": bool((support & ({p} | adj[p])) and (support & ({q} | adj[q]))),
                "pairs": row["pairs"],
                "line": row["line"],
            }
        )

    if len(p_list) > cap:
        return {
            "skipped": True,
            "p": p,
            "q": q,
            "pair_size": len(p_list),
            "num_rows": len(rows),
        }

    worst = None
    tight_count = 0
    positive_trap_count = 0
    for mask in range(1 << len(p_list)):
        U = {p_list[i] for i in range(len(p_list)) if mask & (1 << i)}
        trapped = [row for row in row_records if row["support"] <= U]
        demand = sum(row["demand"] for row in trapped)
        if demand <= 0:
            continue
        positive_trap_count += 1
        supply = sum(deg2[v] - 2 for v in U)
        margin = supply - demand
        if margin == 0:
            tight_count += 1
        rec = {
            "U": sorted(U),
            "supply": supply,
            "demand": demand,
            "margin": margin,
            "trapped": [row["index"] for row in trapped],
            "U_size": len(U),
            "U_capacity_hist": tuple(sorted(Counter(deg2[v] - 2 for v in U).items())),
            "trapped_kinds": tuple(sorted(Counter(row["kind"] for row in trapped).items())),
            "trapped_sizes": tuple(sorted(Counter(row["size"] for row in trapped).items())),
        }
        if worst is None or rec["margin"] < worst["margin"] or (
            rec["margin"] == worst["margin"] and rec["U_size"] < worst["U_size"]
        ):
            worst = rec

    return {
        "skipped": False,
        "p": p,
        "q": q,
        "pair_size": len(p_list),
        "pair_set": p_list,
        "pair_capacity": sum(deg2[v] - 2 for v in pair_set),
        "total_demand": sum(row["demand"] for row in row_records),
        "pair_margin": sum(deg2[v] - 2 for v in pair_set) - sum(row["demand"] for row in row_records),
        "worst": worst,
        "tight_count": tight_count,
        "positive_trap_count": positive_trap_count,
        "row_support_shapes": tuple(
            sorted(
                Counter(
                    (
                        row["kind"],
                        row["size"],
                        row["demand"],
                        row["support_size"],
                        row["support_capacity"],
                        row["touches_endpoint"],
                        row["touches_both_sides"],
                    )
                    for row in row_records
                ).items()
            )
        ),
        "rows": [
            {
                **row,
                "support": sorted(row["support"]),
            }
            for row in row_records
        ],
    }


def analyze(n: int, edges: list[tuple[int, int]], cap: int) -> dict:
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    pairs = [(p, q) for p, q in itertools.combinations(range(n), 2) if dist[p][q] == diam]
    return {
        "n": n,
        "diam": diam,
        "pairs": [analyze_pair(n, edges, p, q, cap) for p, q in pairs],
    }


def summarize(graphs, cap: int) -> dict:
    total = 0
    checked_pairs = 0
    skipped_pairs = 0
    fail_pairs = 0
    min_pair_margin = None
    min_dual_margin = None
    max_tight_count = 0
    worst_examples = []
    shape_counts = Counter()
    for tag, n, edges in graphs:
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        if not hall.is_three_connected(g):
            continue
        rec = analyze(n, edges, cap)
        if rec["diam"] < 4:
            continue
        total += 1
        for pair in rec["pairs"]:
            if pair["skipped"]:
                skipped_pairs += 1
                continue
            checked_pairs += 1
            min_pair_margin = (
                pair["pair_margin"] if min_pair_margin is None else min(min_pair_margin, pair["pair_margin"])
            )
            if pair["worst"] is not None:
                min_dual_margin = (
                    pair["worst"]["margin"] if min_dual_margin is None else min(min_dual_margin, pair["worst"]["margin"])
                )
                if pair["worst"]["margin"] < 0:
                    fail_pairs += 1
                if len(worst_examples) < 8 or pair["worst"]["margin"] < max(
                    item["pair"]["worst"]["margin"] for item in worst_examples
                ):
                    worst_examples.append({"tag": tag, "pair": pair})
                    worst_examples = sorted(worst_examples, key=lambda item: item["pair"]["worst"]["margin"])[:8]
            max_tight_count = max(max_tight_count, pair["tight_count"])
            shape_counts[
                (
                    rec["diam"],
                    pair["pair_size"],
                    pair["total_demand"],
                    pair["pair_margin"],
                    None if pair["worst"] is None else pair["worst"]["margin"],
                    None if pair["worst"] is None else pair["worst"]["U_size"],
                    None if pair["worst"] is None else pair["worst"]["trapped_kinds"],
                    None if pair["worst"] is None else pair["worst"]["trapped_sizes"],
                )
            ] += 1
    return {
        "total": total,
        "checked_pairs": checked_pairs,
        "skipped_pairs": skipped_pairs,
        "fail_pairs": fail_pairs,
        "min_pair_margin": min_pair_margin,
        "min_dual_margin": min_dual_margin,
        "max_tight_count": max_tight_count,
        "shape_counts": dict(shape_counts.most_common(12)),
        "worst_examples": worst_examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260705)
    parser.add_argument("--source", choices=["gnp", "sparse"], default="gnp")
    parser.add_argument("--geng", nargs="*", default=[])
    parser.add_argument("--cap", type=int, default=22)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.g6:
        if args.verbose:
            for g6 in args.g6:
                n, edges = core.graph6_to_edges(g6)
                print("GRAPH", g6, analyze(n, edges, args.cap))
        else:
            rows = []
            for g6 in args.g6:
                n, edges = core.graph6_to_edges(g6)
                rows.append((g6, n, edges))
            print({"named": summarize(rows, args.cap)})
        return

    if args.geng:
        print({"geng": summarize(hall.geng_graphs(args.geng), args.cap)})
    for order in args.orders:
        if args.source == "sparse":
            graphs = ((g6, order, edges) for g6, edges in hall.random_sparse(order, args.samples, args.seed + order))
        else:
            graphs = ((g6, order, edges) for g6, edges in hall.random_three_connected(order, args.samples, args.seed + order))
        print({f"{args.source}_n{order}": summarize(graphs, args.cap)})


if __name__ == "__main__":
    main()
