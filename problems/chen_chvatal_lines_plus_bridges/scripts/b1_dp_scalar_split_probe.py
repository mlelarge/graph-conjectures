"""Probe a scalar split for the diameter-pair G3 target.

For a diameter pair {p,q}, set P=N[p] union N[q] and

    cap(v) = degG2(v) - 2,
    D      = total collision demand = 2*collisions.

DP-G3 is the scalar inequality D <= sum_{v in P} cap(v).

The split tested here is a proof-facing anti-correlation:

    (LOW-P)   D <= 2|P| - t1, where t1=# {v in P : cap(v)=1}.

or

    (HIGH-P) min cap(P) >= 3 and D <= 3|P|.

Since alpha' gives cap(v)>=1 on P, LOW-P implies
sum cap(v) >= 2|P|-t1 >= D.  HIGH-P implies sum cap(v)>=3|P|>=D.
Thus the split implies DP-G3.
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


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    deg2 = [sum(1 for u in range(n) if dist[v][u] == 2) for v in range(n)]
    rows = hall.collision_rows(n, edges)["rows"]
    demand = sum(row["demand"] for row in rows)
    pairs = []
    for p, q in itertools.combinations(range(n), 2):
        if dist[p][q] != diam:
            continue
        pair_set = {p, q} | adj[p] | adj[q]
        caps = [deg2[v] - 2 for v in pair_set]
        t1 = sum(1 for cap in caps if cap == 1)
        low_margin = 2 * len(pair_set) - t1 - demand
        high_margin = 3 * len(pair_set) - demand
        min_cap = min(caps)
        capacity = sum(caps)
        low_ok = low_margin >= 0
        high_ok = min_cap >= 3 and high_margin >= 0
        pairs.append(
            {
                "pair": (p, q),
                "pair_size": len(pair_set),
                "capacity": capacity,
                "demand": demand,
                "dp_margin": capacity - demand,
                "t1": t1,
                "min_cap": min_cap,
                "cap_hist": tuple(sorted(Counter(caps).items())),
                "low_margin": low_margin,
                "high_margin": high_margin,
                "low_ok": low_ok,
                "high_ok": high_ok,
                "split_ok": low_ok or high_ok,
            }
        )
    return {"n": n, "diam": diam, "num_rows": len(rows), "demand": demand, "pairs": pairs}


def summarize(graphs) -> dict:
    total = 0
    pair_count = 0
    dp_fail = 0
    split_fail = 0
    high_used = 0
    low_used = 0
    min_dp_margin = None
    min_low_margin = None
    min_high_margin = None
    max_demand_over_pair_size = 0.0
    shape_counts = Counter()
    examples = []
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
            min_dp_margin = (
                pair["dp_margin"] if min_dp_margin is None else min(min_dp_margin, pair["dp_margin"])
            )
            min_low_margin = (
                pair["low_margin"] if min_low_margin is None else min(min_low_margin, pair["low_margin"])
            )
            min_high_margin = (
                pair["high_margin"] if min_high_margin is None else min(min_high_margin, pair["high_margin"])
            )
            max_demand_over_pair_size = max(
                max_demand_over_pair_size, pair["demand"] / pair["pair_size"] if pair["pair_size"] else 0.0
            )
            if pair["dp_margin"] < 0:
                dp_fail += 1
            if not pair["split_ok"]:
                split_fail += 1
            if pair["high_ok"] and not pair["low_ok"]:
                high_used += 1
            if pair["low_ok"]:
                low_used += 1
            if len(examples) < 10 and (not pair["split_ok"] or pair["dp_margin"] <= 4 or not pair["low_ok"]):
                examples.append({"tag": tag, **pair})
            shape_counts[
                (
                    rec["diam"],
                    pair["pair_size"],
                    pair["demand"],
                    pair["dp_margin"],
                    pair["low_margin"],
                    pair["high_margin"],
                    pair["min_cap"],
                    pair["t1"],
                    pair["cap_hist"],
                    pair["low_ok"],
                    pair["high_ok"],
                )
            ] += 1
    return {
        "total": total,
        "pair_count": pair_count,
        "dp_fail": dp_fail,
        "split_fail": split_fail,
        "low_used": low_used,
        "high_used": high_used,
        "min_dp_margin": min_dp_margin,
        "min_low_margin": min_low_margin,
        "min_high_margin": min_high_margin,
        "max_demand_over_pair_size": max_demand_over_pair_size,
        "shape_counts": dict(shape_counts.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260709)
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
