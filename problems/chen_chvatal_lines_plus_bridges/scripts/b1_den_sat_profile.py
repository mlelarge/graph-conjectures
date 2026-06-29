"""Profile the DEN-SAT target for B1/G3-Hall1.

DEN-SAT said that a connected support-overlap family with positive cardinal
deficit must have support equal to DEN.  This is false; the script is retained
to produce the counterexamples.

The live replacement checked here is the proper weighted certificate:
for every proper deficient component, min degG2(U)>=4 and d(C)<=2|U|.
Together these imply extra(U)>=|U|>=d(C)-|U|, hence OR-reserve.
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


def overlap_graph(rows: list[dict], chosen: list[int]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(chosen)
    for i, j in itertools.combinations(chosen, 2):
        inter = set(rows[i]["support"]) & set(rows[j]["support"])
        if inter:
            graph.add_edge(i, j, overlap=len(inter))
    return graph


def row_kind(row: dict) -> str:
    return "starry" if row["star_units"] else "diffuse"


def component_record(n: int, edges: list[tuple[int, int]], chosen: list[int]) -> dict:
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    dist = core.all_pairs_distances(n, edges)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    den = set(data["den"])
    de = set(data["de"])
    deg2 = data["deg2"]

    support: set[int] = set()
    demand = 0
    for i in chosen:
        support.update(rows[i]["support"])
        demand += rows[i]["demand"]
    missing = den - support

    ov = overlap_graph(rows, chosen)
    support_incidence = Counter()
    for i in chosen:
        for v in rows[i]["support"]:
            support_incidence[v] += 1

    # Internal support adjacency in G[D EN] is a cheap proxy for whether the
    # family is separated from the missing DEN vertices.
    boundary_vertices = sorted(v for v in support if adj[v] & missing)
    missing_boundary = sorted(v for v in missing if adj[v] & support)
    n2_boundary_vertices = sorted(
        v for v in support if any(dist[v][w] == 2 for w in missing)
    )

    rows_out = []
    for i in chosen:
        rows_out.append(
            {
                "index": i,
                "kind": row_kind(rows[i]),
                "demand": rows[i]["demand"],
                "support": sorted(rows[i]["support"]),
                "support_size": len(rows[i]["support"]),
                "pairs": rows[i]["pairs"],
                "line": rows[i]["line"],
                "star_units": rows[i]["star_units"],
                "line_den": rows[i]["line_den"],
                "endpoints_de": rows[i]["endpoints_de"],
            }
        )

    return {
        "chosen": chosen,
        "k": len(chosen),
        "kinds": dict(Counter(row_kind(rows[i]) for i in chosen)),
        "demand": demand,
        "support": sorted(support),
        "support_size": len(support),
        "den": sorted(den),
        "den_size": len(den),
        "missing_den": sorted(missing),
        "missing_de": sorted(missing & de),
        "missing_non_de": sorted(missing - de),
        "card_margin": len(support) - demand,
        "extra": sum(deg2[v] - 3 for v in support),
        "weighted_margin": sum(deg2[v] - 2 for v in support) - demand,
        "overlap_edges": ov.number_of_edges(),
        "cycle_rank": ov.number_of_edges() - len(chosen) + 1,
        "max_pair_overlap": max((ov[a][b]["overlap"] for a, b in ov.edges()), default=0),
        "support_incidence_hist": dict(Counter(support_incidence.values())),
        "support_deg2_hist": dict(Counter(deg2[v] for v in support)),
        "missing_deg2_hist": dict(Counter(deg2[v] for v in missing)),
        "boundary_vertices": boundary_vertices,
        "missing_boundary": missing_boundary,
        "n2_boundary_vertices": n2_boundary_vertices,
        "rows": rows_out,
    }


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    den = set(data["den"])
    if len(rows) > 22:
        return {"skipped": True, "num_rows": len(rows)}

    best_proper = None
    den_sat_fail = None
    min4_fail = None
    half_fail = None
    min4_half_cert_fail = None
    proper_margin_hist = Counter()
    tight_proper = 0
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        ov = overlap_graph(rows, chosen)
        if not nx.is_connected(ov):
            continue
        support = set()
        demand = 0
        for i in chosen:
            support.update(rows[i]["support"])
            demand += rows[i]["demand"]
        if support == den:
            continue
        margin = len(support) - demand
        deg2 = data["deg2"]
        extra = sum(deg2[v] - 3 for v in support)
        proper_margin_hist[margin] += 1
        if margin == 0:
            tight_proper += 1
        rec = None
        if best_proper is None or margin < best_proper["card_margin"]:
            rec = component_record(n, edges, chosen)
            best_proper = rec
        if margin < 0 and den_sat_fail is None:
            den_sat_fail = rec or component_record(n, edges, chosen)
        if margin < 0:
            min_deg2 = min((deg2[v] for v in support), default=None)
            deficit = demand - len(support)
            if min_deg2 is not None and min_deg2 < 4 and min4_fail is None:
                min4_fail = rec or component_record(n, edges, chosen)
            if demand > 2 * len(support) and half_fail is None:
                half_fail = rec or component_record(n, edges, chosen)
            if not (
                min_deg2 is not None
                and min_deg2 >= 4
                and deficit <= len(support)
                and extra >= deficit
            ) and min4_half_cert_fail is None:
                min4_half_cert_fail = rec or component_record(n, edges, chosen)

    return {
        "skipped": False,
        "num_rows": len(rows),
        "den_size": len(den),
        "best_proper": best_proper,
        "den_sat_fail": den_sat_fail,
        "min4_fail": min4_fail,
        "half_fail": half_fail,
        "min4_half_cert_fail": min4_half_cert_fail,
        "proper_margin_hist": dict(proper_margin_hist),
        "tight_proper": tight_proper,
    }


def summarize(graphs) -> dict:
    total = 0
    skipped = 0
    den_sat_fail = 0
    min4_fail = 0
    half_fail = 0
    min4_half_cert_fail = 0
    with_proper = 0
    with_tight_proper = 0
    min_proper_margin = None
    hist = Counter()
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
        hist.update(rec["proper_margin_hist"])
        if rec["best_proper"] is not None:
            with_proper += 1
            margin = rec["best_proper"]["card_margin"]
            min_proper_margin = margin if min_proper_margin is None else min(min_proper_margin, margin)
        if rec["tight_proper"]:
            with_tight_proper += 1
        if rec["den_sat_fail"] is not None:
            den_sat_fail += 1
        if rec["min4_fail"] is not None:
            min4_fail += 1
        if rec["half_fail"] is not None:
            half_fail += 1
        if rec["min4_half_cert_fail"] is not None:
            min4_half_cert_fail += 1
        if len(examples) < 8 and (
            rec["den_sat_fail"] is not None
            or rec["min4_fail"] is not None
            or rec["half_fail"] is not None
            or rec["min4_half_cert_fail"] is not None
            or (rec["best_proper"] is not None and rec["best_proper"]["card_margin"] <= 1)
        ):
            examples.append({"tag": tag, **rec})
    return {
        "total": total,
        "skipped": skipped,
        "with_proper": with_proper,
        "with_tight_proper": with_tight_proper,
        "den_sat_fail": den_sat_fail,
        "min4_fail": min4_fail,
        "half_fail": half_fail,
        "min4_half_cert_fail": min4_half_cert_fail,
        "min_proper_margin": min_proper_margin,
        "proper_margin_hist": dict(hist.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260701)
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
