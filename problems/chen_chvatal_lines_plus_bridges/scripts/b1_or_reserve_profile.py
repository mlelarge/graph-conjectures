"""Profile the OR-reserve target for G3-Hall1.

This script is proof-facing rather than just a gate.  For each connected
support-overlap family with cardinal deficit, it records where the reserve
sum(degG2-3) is paid and how much of each support vertex's distance-2 degree
points outside the component support.
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


def connected_subsets(rows: list[dict]):
    if len(rows) > 22:
        return
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        overlap = nx.Graph()
        overlap.add_nodes_from(chosen)
        for i, j in itertools.combinations(chosen, 2):
            if set(rows[i]["support"]) & set(rows[j]["support"]):
                overlap.add_edge(i, j)
        if nx.is_connected(overlap):
            yield chosen, overlap


def analyze_component(n: int, edges: list[tuple[int, int]], chosen: list[int], overlap: nx.Graph) -> dict:
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    dist = core.all_pairs_distances(n, edges)
    deg2 = data["deg2"]
    de = set(data["de"])
    den = set(data["den"])
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    support = set()
    demand = 0
    pair_vertices = set()
    line_vertices = set()
    for i in chosen:
        support.update(rows[i]["support"])
        demand += rows[i]["demand"]
        pair_vertices.update(itertools.chain.from_iterable(rows[i]["pairs"]))
        line_vertices.update(rows[i]["line"])

    support_incidence = Counter()
    for i in chosen:
        for v in rows[i]["support"]:
            support_incidence[v] += 1

    vertex_records = []
    for v in sorted(support):
        n2 = {u for u in range(n) if dist[v][u] == 2}
        vertex_records.append(
            {
                "v": v,
                "deg2": deg2[v],
                "extra": deg2[v] - 3,
                "in_de": v in de,
                "in_den": v in den,
                "row_incidence": support_incidence[v],
                "n2_in_support": len(n2 & support),
                "n2_out_support": len(n2 - support),
                "n2_out": sorted(n2 - support),
                "adj_de": sorted(adj[v] & de),
            }
        )

    row_records = []
    for i in chosen:
        line = set(rows[i]["line"])
        endpoints = set(itertools.chain.from_iterable(rows[i]["pairs"]))
        base = line | endpoints
        row_records.append(
            {
                "index": i,
                "kind": row_kind(rows[i]),
                "demand": rows[i]["demand"],
                "pairs": rows[i]["pairs"],
                "line": sorted(line),
                "support": sorted(rows[i]["support"]),
                "support_size": len(rows[i]["support"]),
                "base_in_den": sorted(base & den),
                "expanded_only": sorted(set(rows[i]["support"]) - base),
                "star_units": rows[i]["star_units"],
            }
        )

    extra = sum(deg2[v] - 3 for v in support)
    deficit = demand - len(support)
    return {
        "chosen": chosen,
        "k": len(chosen),
        "kinds": dict(Counter(row_kind(rows[i]) for i in chosen)),
        "demand": demand,
        "support": sorted(support),
        "support_size": len(support),
        "den": sorted(den),
        "den_size": len(den),
        "support_is_den": support == den,
        "card_deficit": deficit,
        "extra": extra,
        "weighted_margin": len(support) + extra - demand,
        "overlap_edges": overlap.number_of_edges(),
        "cycle_rank": overlap.number_of_edges() - len(chosen) + 1,
        "max_pair_overlap": max(
            (len(set(rows[a]["support"]) & set(rows[b]["support"])) for a, b in overlap.edges()),
            default=0,
        ),
        "pair_vertices": sorted(pair_vertices),
        "line_vertices": sorted(line_vertices),
        "support_incidence_hist": dict(Counter(support_incidence.values())),
        "support_deg2_hist": dict(Counter(deg2[v] for v in support)),
        "support_de_count": len(support & de),
        "support_vertices": vertex_records,
        "rows": row_records,
    }


def profile_graph(tag: str, n: int, edges: list[tuple[int, int]]) -> dict | None:
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    if not hall.is_three_connected(g):
        return None
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    if diam < 4:
        return None
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    if len(rows) > 22:
        return {"tag": tag, "n": n, "diam": diam, "skipped": True, "num_rows": len(rows)}

    deficient = []
    worst_margin = None
    worst_deficit = None
    proper_trap_fail = None
    support_not_den_fail = None
    for chosen, overlap in connected_subsets(rows):
        rec = analyze_component(n, edges, chosen, overlap)
        if rec["card_deficit"] <= 0:
            continue
        rec["all_rows_chosen"] = len(chosen) == len(rows)
        deficient.append(rec)
        if not rec["all_rows_chosen"] and proper_trap_fail is None:
            proper_trap_fail = rec
        if not rec["support_is_den"] and support_not_den_fail is None:
            support_not_den_fail = rec
        if worst_margin is None or rec["weighted_margin"] < worst_margin["weighted_margin"]:
            worst_margin = rec
        if worst_deficit is None or rec["card_deficit"] > worst_deficit["card_deficit"]:
            worst_deficit = rec
    return {
        "tag": tag,
        "n": n,
        "diam": diam,
        "num_rows": len(rows),
        "num_deficient_components": len(deficient),
        "proper_trap_fail": proper_trap_fail,
        "support_not_den_fail": support_not_den_fail,
        "worst_margin": worst_margin,
        "worst_deficit": worst_deficit,
    }


def summarize(graphs) -> dict:
    total = 0
    skipped = 0
    with_deficit = 0
    proper_trap_fail = 0
    support_not_den_fail = 0
    min_margin = None
    min_extra_minus_deficit = None
    shape_counts = Counter()
    examples = []
    for tag, n, edges in graphs:
        rec = profile_graph(tag, n, edges)
        if rec is None:
            continue
        if rec.get("skipped"):
            skipped += 1
            continue
        total += 1
        wm = rec["worst_margin"]
        if wm is not None:
            with_deficit += 1
            proper_trap_fail += int(rec["proper_trap_fail"] is not None)
            support_not_den_fail += int(rec["support_not_den_fail"] is not None)
            min_margin = wm["weighted_margin"] if min_margin is None else min(min_margin, wm["weighted_margin"])
            emd = wm["extra"] - wm["card_deficit"]
            min_extra_minus_deficit = emd if min_extra_minus_deficit is None else min(min_extra_minus_deficit, emd)
            shape_counts[
                (
                    wm["k"],
                    wm["kinds"].get("diffuse", 0),
                    wm["kinds"].get("starry", 0),
                    wm["support_size"],
                    wm["card_deficit"],
                    wm["extra"],
                    wm["support_de_count"],
                    tuple(sorted(wm["support_deg2_hist"].items())),
                )
            ] += 1
            if len(examples) < 6:
                examples.append(rec)
    return {
        "total": total,
        "skipped": skipped,
        "with_deficit": with_deficit,
        "proper_trap_fail": proper_trap_fail,
        "support_not_den_fail": support_not_den_fail,
        "min_margin": min_margin,
        "min_extra_minus_deficit": min_extra_minus_deficit,
        "shape_counts": dict(shape_counts.most_common(10)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260630)
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
