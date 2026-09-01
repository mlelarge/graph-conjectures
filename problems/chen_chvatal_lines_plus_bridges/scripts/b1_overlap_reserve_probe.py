"""Historical probe of overlap-reserve certificates for G3-Hall1.

The D-CARD split is too strong: diffuse-only support families can be cardinal
deficient.  In the samples that motivated this probe, G3-Hall1 survived because
the same support had extra capacity sum(degG2-3).  G21 later refuted G3 and its
Hall descendants.  This script studies the historical support subfamilies for
diagnosis only; it is not a live B1 route.
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
    return "starry" if row["star_units"] > 0 else "diffuse"


def analyze_subset(rows: list[dict], deg2: list[int], chosen: list[int]) -> dict:
    support = set()
    demand = 0
    local_slack = 0
    kind_counts = Counter()
    overlap = nx.Graph()
    overlap.add_nodes_from(chosen)
    for i in chosen:
        row_support = set(rows[i]["support"])
        support.update(row_support)
        demand += rows[i]["demand"]
        local_slack += len(row_support) - rows[i]["demand"]
        kind_counts[row_kind(rows[i])] += 1
    for i, j in itertools.combinations(chosen, 2):
        inter = set(rows[i]["support"]) & set(rows[j]["support"])
        if inter:
            overlap.add_edge(i, j, size=len(inter))
    extra = sum(deg2[v] - 3 for v in support)
    components = nx.number_connected_components(overlap) if chosen else 0
    cycle_rank = overlap.number_of_edges() - len(chosen) + components
    overlap_loss = sum(len(rows[i]["support"]) for i in chosen) - len(support)
    card_deficit = demand - len(support)
    return {
        "chosen": chosen,
        "k": len(chosen),
        "kinds": dict(kind_counts),
        "demand": demand,
        "support": sorted(support),
        "support_size": len(support),
        "local_slack": local_slack,
        "overlap_loss": overlap_loss,
        "card_deficit": card_deficit,
        "extra": extra,
        "weighted_margin": len(support) + extra - demand,
        "overlap_edges": overlap.number_of_edges(),
        "cycle_rank": cycle_rank,
        "connected": components == 1,
        "max_pair_overlap": max((overlap[a][b]["size"] for a, b in overlap.edges()), default=0),
        "rows": [
            {
                "index": i,
                "kind": row_kind(rows[i]),
                "demand": rows[i]["demand"],
                "support": sorted(rows[i]["support"]),
                "pairs": rows[i]["pairs"],
                "line": rows[i]["line"],
            }
            for i in chosen
        ],
    }


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    deg2 = data["deg2"]
    if len(rows) > 22:
        return {"skipped": True, "num_rows": len(rows)}

    worst_weighted = None
    worst_card = None
    card_cycle_fail = None
    cycle_reserve_fail = None
    connected_target_fail = None
    component_shapes = Counter()
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        rec = analyze_subset(rows, deg2, chosen)
        if not rec["connected"]:
            continue
        if worst_weighted is None or rec["weighted_margin"] < worst_weighted["weighted_margin"]:
            worst_weighted = rec
        if worst_card is None or rec["card_deficit"] > worst_card["card_deficit"]:
            worst_card = rec
        if rec["card_deficit"] > 0:
            component_shapes[
                (
                    rec["k"],
                    rec["kinds"].get("diffuse", 0),
                    rec["kinds"].get("starry", 0),
                    rec["card_deficit"],
                    rec["extra"],
                    rec["cycle_rank"],
                    rec["weighted_margin"],
                )
            ] += 1
            if rec["weighted_margin"] < 0 and connected_target_fail is None:
                connected_target_fail = rec
            if rec["card_deficit"] > rec["cycle_rank"] and card_cycle_fail is None:
                card_cycle_fail = rec
            if rec["extra"] < rec["cycle_rank"] and cycle_reserve_fail is None:
                cycle_reserve_fail = rec

    return {
        "skipped": False,
        "num_rows": len(rows),
        "worst_weighted": worst_weighted,
        "worst_card": worst_card,
        "connected_target_fail": connected_target_fail,
        "card_cycle_fail": card_cycle_fail,
        "cycle_reserve_fail": cycle_reserve_fail,
        "component_shapes": component_shapes,
    }


def summarize(tagged_graphs) -> dict:
    total = 0
    skipped = 0
    connected_target_fail = 0
    card_cycle_fail = 0
    cycle_reserve_fail = 0
    card_def_graphs = 0
    min_weighted_margin = None
    max_card_deficit = 0
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
        if result.get("skipped"):
            skipped += 1
            continue
        total += 1
        ww = result["worst_weighted"]
        wc = result["worst_card"]
        if ww is not None:
            min_weighted_margin = (
                ww["weighted_margin"]
                if min_weighted_margin is None
                else min(min_weighted_margin, ww["weighted_margin"])
            )
        if wc is not None and wc["card_deficit"] > 0:
            card_def_graphs += 1
            max_card_deficit = max(max_card_deficit, wc["card_deficit"])
        connected_target_fail += int(result["connected_target_fail"] is not None)
        card_cycle_fail += int(result["card_cycle_fail"] is not None)
        cycle_reserve_fail += int(result["cycle_reserve_fail"] is not None)
        shapes.update(result["component_shapes"])
        if len(examples) < 8 and (
            result["connected_target_fail"] is not None
            or result["card_cycle_fail"] is not None
            or result["cycle_reserve_fail"] is not None
            or (wc is not None and wc["card_deficit"] > 0)
        ):
            examples.append(
                {
                    "tag": tag,
                    "worst_weighted": ww,
                    "worst_card": wc,
                    "connected_target_fail": result["connected_target_fail"],
                    "card_cycle_fail": result["card_cycle_fail"],
                    "cycle_reserve_fail": result["cycle_reserve_fail"],
                }
            )
    return {
        "total": total,
        "skipped": skipped,
        "card_def_graphs": card_def_graphs,
        "max_card_deficit": max_card_deficit,
        "min_weighted_margin": min_weighted_margin,
        "connected_target_fail": connected_target_fail,
        "card_cycle_fail": card_cycle_fail,
        "cycle_reserve_fail": cycle_reserve_fail,
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
