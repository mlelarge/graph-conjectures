"""Gate the DEN-saturation reduction for OR-reserve.

Historical target, now refuted:

  DEN-SAT: every connected support-overlap family with d(C)>|U(C)| has U(C)=DEN.

If DEN-SAT held, then OR-reserve would follow from the original global G3 inequality:
for such C, d(C) <= 2*collisions <= E(DEN) = |DEN|+extra(DEN) = |U(C)|+extra(U(C)).
Thus G3-Hall1 has no extra proper-support obstruction beyond G3.

The gate is retained because support_not_den_fail is the DEN-SAT failure counter.
The next historical replacement, profiled in b1_den_sat_profile.py, tested
min degG2(U)>=4 and d(C)<=2|U(C)| for proper deficient components.  G21 later
refuted G3 and the encompassing OR-reserve route, so neither reduction is live.
"""
from __future__ import annotations

import argparse
import itertools
import sys

import networkx as nx

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b1_hall_profile as hall  # noqa: E402
import core  # noqa: E402


def connected(rows: list[dict], chosen: list[int]) -> bool:
    overlap = nx.Graph()
    overlap.add_nodes_from(chosen)
    for i, j in itertools.combinations(chosen, 2):
        if set(rows[i]["support"]) & set(rows[j]["support"]):
            overlap.add_edge(i, j)
    return nx.is_connected(overlap)


def has_private_demand_row(rows: list[dict], chosen: list[int]) -> bool:
    """Return whether some row pays its demand outside the other supports."""
    for i in chosen:
        others = set()
        for j in chosen:
            if j != i:
                others.update(rows[j]["support"])
        if len(set(rows[i]["support"]) - others) >= rows[i]["demand"]:
            return True
    return False


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    deg2 = data["deg2"]
    den = set(data["den"])
    if len(rows) > 22:
        return {"skipped": True, "num_rows": len(rows)}

    den_extra = sum(deg2[v] - 3 for v in den)
    den_supply = sum(deg2[v] - 2 for v in den)
    total_demand = sum(row["demand"] for row in rows)
    g3_margin = den_supply - total_demand

    deficient = 0
    support_not_den_fail = None
    or_fail = None
    private_row_fail = None
    min_or_margin = None
    min_proper_card_margin = None
    max_deficit = 0
    proper_deficient = 0
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        if not connected(rows, chosen):
            continue
        support = set()
        demand = 0
        for i in chosen:
            support.update(rows[i]["support"])
            demand += rows[i]["demand"]
        deficit = demand - len(support)
        card_margin = len(support) - demand
        extra = sum(deg2[v] - 3 for v in support)
        margin = len(support) + extra - demand
        min_or_margin = margin if min_or_margin is None else min(min_or_margin, margin)
        if support != den:
            min_proper_card_margin = (
                card_margin
                if min_proper_card_margin is None
                else min(min_proper_card_margin, card_margin)
            )
        if margin < 0 and or_fail is None:
            or_fail = {
                "chosen": chosen,
                "demand": demand,
                "support": sorted(support),
                "deficit": deficit,
                "extra": extra,
                "margin": margin,
            }
        if support != den and not has_private_demand_row(rows, chosen) and private_row_fail is None:
            private_row_fail = {
                "chosen": chosen,
                "demand": demand,
                "support": sorted(support),
                "den": sorted(den),
                "margin": margin,
                "rows": [
                    {
                        "index": i,
                        "demand": rows[i]["demand"],
                        "support": sorted(rows[i]["support"]),
                    }
                    for i in chosen
                ],
            }
        if deficit > 0:
            deficient += 1
            max_deficit = max(max_deficit, deficit)
            if len(chosen) < len(rows):
                proper_deficient += 1
            if support != den and support_not_den_fail is None:
                support_not_den_fail = {
                    "chosen": chosen,
                    "demand": demand,
                    "support": sorted(support),
                    "den": sorted(den),
                    "deficit": deficit,
                    "extra": extra,
                    "margin": margin,
                }

    return {
        "skipped": False,
        "num_rows": len(rows),
        "den_size": len(den),
        "den_extra": den_extra,
        "total_demand": total_demand,
        "g3_margin": g3_margin,
        "deficient": deficient,
        "proper_deficient": proper_deficient,
        "max_deficit": max_deficit,
        "min_proper_card_margin": min_proper_card_margin,
        "min_or_margin": min_or_margin,
        "support_not_den_fail": support_not_den_fail,
        "private_row_fail": private_row_fail,
        "or_fail": or_fail,
    }


def summarize(graphs) -> dict:
    total = 0
    skipped = 0
    with_deficient = 0
    proper_deficient_graphs = 0
    support_not_den_fail = 0
    private_row_fail = 0
    or_fail = 0
    min_g3_margin = None
    min_or_margin = None
    min_proper_card_margin = None
    max_deficit = 0
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
        min_g3_margin = rec["g3_margin"] if min_g3_margin is None else min(min_g3_margin, rec["g3_margin"])
        if rec["min_or_margin"] is not None:
            min_or_margin = rec["min_or_margin"] if min_or_margin is None else min(min_or_margin, rec["min_or_margin"])
        if rec["min_proper_card_margin"] is not None:
            min_proper_card_margin = (
                rec["min_proper_card_margin"]
                if min_proper_card_margin is None
                else min(min_proper_card_margin, rec["min_proper_card_margin"])
            )
        if rec["deficient"]:
            with_deficient += 1
            max_deficit = max(max_deficit, rec["max_deficit"])
        if rec["proper_deficient"]:
            proper_deficient_graphs += 1
        if rec["support_not_den_fail"] is not None:
            support_not_den_fail += 1
        if rec["private_row_fail"] is not None:
            private_row_fail += 1
        if rec["or_fail"] is not None:
            or_fail += 1
        if len(examples) < 6 and (
            rec["support_not_den_fail"] is not None
            or rec["private_row_fail"] is not None
            or rec["or_fail"] is not None
            or rec["deficient"]
        ):
            examples.append({"tag": tag, **rec})

    return {
        "total": total,
        "skipped": skipped,
        "with_deficient": with_deficient,
        "proper_deficient_graphs": proper_deficient_graphs,
        "support_not_den_fail": support_not_den_fail,
        "private_row_fail": private_row_fail,
        "or_fail": or_fail,
        "min_g3_margin": min_g3_margin,
        "min_or_margin": min_or_margin,
        "min_proper_card_margin": min_proper_card_margin,
        "max_deficit": max_deficit,
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
