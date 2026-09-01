"""Historical profile of the refuted G3 localization inequality.

G3 is:

    total_demand = 2 * collisions <= E(DEN)
                 = sum_{v in DEN}(degG2(v)-2).

The former load-bearing case was a support-overlap component covering all of
DEN, i.e. G3 itself.  G21 refuted G3 at n=12.  This script records historical
low-margin instances and candidate coarse inequalities; it is not a live B1
proof route.  The surviving target is global collisions <= surplus on all V.
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


def support_components(rows: list[dict]) -> list[set[int]]:
    graph = nx.Graph()
    graph.add_nodes_from(range(len(rows)))
    for i, j in itertools.combinations(range(len(rows)), 2):
        if set(rows[i]["support"]) & set(rows[j]["support"]):
            graph.add_edge(i, j)
    return [set(comp) for comp in nx.connected_components(graph)]


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    deg2 = data["deg2"]
    den = set(data["den"])
    de = set(data["de"])
    total_demand = sum(row["demand"] for row in rows)
    den_supply = sum(deg2[v] - 2 for v in den)
    den_extra = sum(deg2[v] - 3 for v in den)
    low = {v for v in den if deg2[v] == 3}
    comps = support_components(rows) if rows else []
    comp_records = []
    for comp in comps:
        support = set()
        demand = 0
        kinds = Counter()
        sizes = Counter()
        for i in comp:
            support.update(rows[i]["support"])
            demand += rows[i]["demand"]
            kinds[row_kind(rows[i])] += 1
            sizes[rows[i]["size"]] += 1
        comp_records.append(
            {
                "k": len(comp),
                "demand": demand,
                "support_size": len(support),
                "support_is_den": support == den,
                "card_margin": len(support) - demand,
                "weighted_margin": sum(deg2[v] - 2 for v in support) - demand,
                "kinds": tuple(sorted(kinds.items())),
                "sizes": tuple(sorted(sizes.items())),
                "support_deg2_hist": tuple(sorted(Counter(deg2[v] for v in support).items())),
            }
        )
    return {
        "num_rows": len(rows),
        "total_demand": total_demand,
        "den_size": len(den),
        "de_size": len(de),
        "den_supply": den_supply,
        "den_extra": den_extra,
        "g3_margin": den_supply - total_demand,
        "unit_margin": len(den) - total_demand,
        "low_count": len(low),
        "min_den_deg2": min((deg2[v] for v in den), default=None),
        "den_deg2_hist": tuple(sorted(Counter(deg2[v] for v in den).items())),
        "row_kinds": tuple(sorted(Counter(row_kind(row) for row in rows).items())),
        "row_sizes": tuple(sorted(Counter(row["size"] for row in rows).items())),
        "support_components": comp_records,
    }


def summarize(graphs) -> dict:
    total = 0
    min_g3_margin = None
    min_unit_margin = None
    max_demand_minus_den = None
    low_margin_examples = []
    coarse_examples = {}
    shape_counts = Counter()
    coarse_fail = Counter()
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
        total += 1
        min_g3_margin = rec["g3_margin"] if min_g3_margin is None else min(min_g3_margin, rec["g3_margin"])
        min_unit_margin = rec["unit_margin"] if min_unit_margin is None else min(min_unit_margin, rec["unit_margin"])
        demand_minus_den = rec["total_demand"] - rec["den_size"]
        max_demand_minus_den = (
            demand_minus_den if max_demand_minus_den is None else max(max_demand_minus_den, demand_minus_den)
        )
        if rec["total_demand"] > 2 * rec["den_size"]:
            coarse_fail["2cap_den"] += 1
            coarse_examples.setdefault("2cap_den", {"tag": tag, **rec})
        if rec["den_extra"] < max(0, demand_minus_den):
            coarse_fail["extra_covers_unit_deficit"] += 1
            coarse_examples.setdefault("extra_covers_unit_deficit", {"tag": tag, **rec})
        if rec["den_extra"] < rec["low_count"]:
            coarse_fail["extra_ge_low_count"] += 1
            coarse_examples.setdefault("extra_ge_low_count", {"tag": tag, **rec})
        shape_counts[
            (
                rec["total_demand"],
                rec["den_size"],
                demand_minus_den,
                rec["den_extra"],
                rec["g3_margin"],
                rec["low_count"],
                rec["den_deg2_hist"],
                rec["row_kinds"],
                rec["row_sizes"],
                tuple(sorted((c["support_is_den"], c["demand"], c["support_size"]) for c in rec["support_components"])),
            )
        ] += 1
        if len(low_margin_examples) < 8 or rec["g3_margin"] < max(e["g3_margin"] for e in low_margin_examples):
            low_margin_examples.append({"tag": tag, **rec})
            low_margin_examples = sorted(low_margin_examples, key=lambda x: x["g3_margin"])[:8]
    return {
        "total": total,
        "min_g3_margin": min_g3_margin,
        "min_unit_margin": min_unit_margin,
        "max_demand_minus_den": max_demand_minus_den,
        "coarse_fail": dict(coarse_fail),
        "coarse_examples": coarse_examples,
        "shape_counts": dict(shape_counts.most_common(12)),
        "low_margin_examples": low_margin_examples,
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
