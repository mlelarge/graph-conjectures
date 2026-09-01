"""Probe the proper pair-local OR target for the refuted DP-Hall route.

For a diameter pair {p,q}, let P=N[p] union N[q].  Each collided row L has
restricted support S_L^pq = S_L cap P and demand d(L).

The full pair-local Hall strengthening is now known to be false.  The correct
logical reduction would require checking connected subfamilies in the
row-overlap graph, not just components of the full row graph; this script does
that enumeration when the number of collided rows is small enough and profiles
the proper-support part:

    (DP-PROPER-OR)  if U(X) != P then E(U(X)) >= d(X).

The script is retained as a guard.  It finds the sparse empty-support
refutation, while also tracking the old sufficient certificate:

    if d(X) > |U(X)|, prove min_{v in U(X)} degG2(v) >= 4
    and d(X) <= 2 |U(X)|.

Together these imply E(U) = |U| + sum(degG2(v)-3) >= 2|U| >= d(X).

G21 later refuted the encompassing scalar DP-G3 localization.  These
proper-support measurements therefore remain historical diagnostics only; they
do not constitute a live route to B1.
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


def pair_rows(n: int, edges: list[tuple[int, int]], p: int, q: int) -> dict:
    dist = core.all_pairs_distances(n, edges)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    deg2 = [sum(1 for u in range(n) if dist[v][u] == 2) for v in range(n)]
    rows = hall.collision_rows(n, edges)["rows"]
    pair_set = {p, q} | adj[p] | adj[q]
    supports = [set(row["support"]) & pair_set for row in rows]
    overlap = nx.Graph()
    overlap.add_nodes_from(range(len(rows)))
    for i, j in itertools.combinations(range(len(rows)), 2):
        if supports[i] & supports[j]:
            overlap.add_edge(i, j)
    return {
        "p": p,
        "q": q,
        "pair_set": pair_set,
        "deg2": deg2,
        "rows": rows,
        "supports": supports,
        "overlap": overlap,
    }


def is_connected_subset(overlap: nx.Graph, chosen: list[int]) -> bool:
    if len(chosen) <= 1:
        return True
    return nx.is_connected(overlap.subgraph(chosen))


def row_matching_ok(rows: list[dict], supports: list[set[int]], chosen: list[int]) -> bool:
    left = [("r", i) for i in chosen]
    support = set().union(*(supports[i] for i in chosen)) if chosen else set()
    graph = nx.Graph()
    graph.add_nodes_from(left, bipartite=0)
    graph.add_nodes_from([("v", v) for v in support], bipartite=1)
    for i in chosen:
        for v in supports[i]:
            graph.add_edge(("r", i), ("v", v))
    matching = nx.algorithms.bipartite.maximum_matching(graph, top_nodes=left)
    return sum(1 for node in left if node in matching) == len(left)


def subfamily_record(pair: dict, chosen: list[int]) -> dict:
    rows = pair["rows"]
    supports = pair["supports"]
    deg2 = pair["deg2"]
    pair_set = pair["pair_set"]
    support = set().union(*(supports[i] for i in chosen)) if chosen else set()
    demand = sum(rows[i]["demand"] for i in chosen)
    capacity = sum(deg2[v] - 2 for v in support)
    support_inc = Counter()
    for i in chosen:
        for v in supports[i]:
            support_inc[v] += 1
    return {
        "pair": (pair["p"], pair["q"]),
        "chosen": chosen,
        "k": len(chosen),
        "support": sorted(support),
        "support_size": len(support),
        "pair_size": len(pair_set),
        "support_is_pair": support == pair_set,
        "demand": demand,
        "capacity": capacity,
        "margin": capacity - demand,
        "card_margin": len(support) - demand,
        "two_cap_margin": 2 * len(support) - demand,
        "min_deg2": min((deg2[v] for v in support), default=None),
        "extra": sum(deg2[v] - 3 for v in support),
        "row_matching_ok": row_matching_ok(rows, supports, chosen),
        "kinds": tuple(sorted(Counter(row_kind(rows[i]) for i in chosen).items())),
        "row_sizes": tuple(sorted(Counter(rows[i]["size"] for i in chosen).items())),
        "row_demands": tuple(sorted(Counter(rows[i]["demand"] for i in chosen).items())),
        "support_inc_hist": tuple(sorted(Counter(support_inc.values()).items())),
        "support_capacity_hist": tuple(sorted(Counter(deg2[v] - 2 for v in support).items())),
        "touches_endpoint": bool({pair["p"], pair["q"]} & support),
    }


def analyze_pair(n: int, edges: list[tuple[int, int]], p: int, q: int, cap: int) -> dict:
    pair = pair_rows(n, edges, p, q)
    rows = pair["rows"]
    if len(rows) > cap:
        return {"skipped": True, "p": p, "q": q, "num_rows": len(rows)}

    recs = []
    proper_or_fail = []
    proper_card_fail = []
    min4_fail = []
    twocap_fail = []
    shape_fail = []
    matching_fail = []
    low3_card_fail = []
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        if not is_connected_subset(pair["overlap"], chosen):
            continue
        rec = subfamily_record(pair, chosen)
        if rec["support_is_pair"]:
            continue
        recs.append(rec)
        if rec["margin"] < 0:
            proper_or_fail.append(rec)
        if rec["card_margin"] < 0:
            proper_card_fail.append(rec)
            if rec["min_deg2"] is None or rec["min_deg2"] < 4:
                min4_fail.append(rec)
            if rec["two_cap_margin"] < 0:
                twocap_fail.append(rec)
            if rec["kinds"] != (("diffuse", rec["k"]),) or rec["row_sizes"] != ((2, rec["k"]),):
                shape_fail.append(rec)
            if not rec["row_matching_ok"]:
                matching_fail.append(rec)
        if rec["min_deg2"] == 3 and rec["card_margin"] < 0:
            low3_card_fail.append(rec)

    return {
        "skipped": False,
        "p": p,
        "q": q,
        "num_rows": len(rows),
        "proper": recs,
        "proper_or_fail": proper_or_fail,
        "proper_card_fail": proper_card_fail,
        "min4_fail": min4_fail,
        "twocap_fail": twocap_fail,
        "shape_fail": shape_fail,
        "matching_fail": matching_fail,
        "low3_card_fail": low3_card_fail,
    }


def analyze(n: int, edges: list[tuple[int, int]], cap: int) -> dict:
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    pairs = [(p, q) for p, q in itertools.combinations(range(n), 2) if dist[p][q] == diam]
    return {"n": n, "diam": diam, "pairs": [analyze_pair(n, edges, p, q, cap) for p, q in pairs]}


def summarize(graphs, cap: int) -> dict:
    total = 0
    pair_count = 0
    skipped_pairs = 0
    proper_count = 0
    proper_card_fail_count = 0
    proper_or_fail_count = 0
    min4_fail_count = 0
    twocap_fail_count = 0
    shape_fail_count = 0
    matching_fail_count = 0
    low3_card_fail_count = 0
    min_proper_margin = None
    min_proper_card_margin = None
    min_two_cap_margin = None
    min_min_deg2 = None
    max_card_deficit = 0
    shape_counts = Counter()
    examples = []
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
            pair_count += 1
            proper_count += len(pair["proper"])
            proper_card_fail_count += len(pair["proper_card_fail"])
            proper_or_fail_count += len(pair["proper_or_fail"])
            min4_fail_count += len(pair["min4_fail"])
            twocap_fail_count += len(pair["twocap_fail"])
            shape_fail_count += len(pair["shape_fail"])
            matching_fail_count += len(pair["matching_fail"])
            low3_card_fail_count += len(pair["low3_card_fail"])
            for comp in pair["proper"]:
                min_proper_margin = (
                    comp["margin"] if min_proper_margin is None else min(min_proper_margin, comp["margin"])
                )
                min_proper_card_margin = (
                    comp["card_margin"]
                    if min_proper_card_margin is None
                    else min(min_proper_card_margin, comp["card_margin"])
                )
                if comp["card_margin"] < 0:
                    min_two_cap_margin = (
                        comp["two_cap_margin"]
                        if min_two_cap_margin is None
                        else min(min_two_cap_margin, comp["two_cap_margin"])
                    )
                    min_min_deg2 = (
                        comp["min_deg2"] if min_min_deg2 is None else min(min_min_deg2, comp["min_deg2"])
                    )
                    max_card_deficit = max(max_card_deficit, -comp["card_margin"])
                    shape_counts[
                        (
                            comp["k"],
                            comp["demand"],
                            comp["support_size"],
                            comp["card_margin"],
                            comp["margin"],
                            comp["two_cap_margin"],
                            comp["min_deg2"],
                            comp["kinds"],
                            comp["row_sizes"],
                            comp["support_inc_hist"],
                            comp["support_capacity_hist"],
                            comp["touches_endpoint"],
                        )
                    ] += 1
                    if len(examples) < 10:
                        examples.append({"tag": tag, **comp})

    return {
        "total": total,
        "pair_count": pair_count,
        "skipped_pairs": skipped_pairs,
        "proper_count": proper_count,
        "proper_card_fail_count": proper_card_fail_count,
        "proper_or_fail_count": proper_or_fail_count,
        "min4_fail_count": min4_fail_count,
        "twocap_fail_count": twocap_fail_count,
        "shape_fail_count": shape_fail_count,
        "matching_fail_count": matching_fail_count,
        "low3_card_fail_count": low3_card_fail_count,
        "min_proper_margin": min_proper_margin,
        "min_proper_card_margin": min_proper_card_margin,
        "min_two_cap_margin": min_two_cap_margin,
        "min_min_deg2": min_min_deg2,
        "max_card_deficit": max_card_deficit,
        "shape_counts": dict(shape_counts.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260707)
    parser.add_argument("--source", choices=["gnp", "sparse"], default="gnp")
    parser.add_argument("--geng", nargs="*", default=[])
    parser.add_argument("--cap", type=int, default=22)
    args = parser.parse_args()

    if args.g6:
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
