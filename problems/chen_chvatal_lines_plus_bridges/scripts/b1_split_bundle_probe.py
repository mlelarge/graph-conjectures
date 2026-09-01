"""Historical probe of STAR-bundle structure inside G3-Hall1 failures.

This is a diagnostic for the split route in docs/H5_LEMMA_B_OBSTRUCTION.md.
The former sufficient reduction needed conditional STAR reserve only for
families X whose unit-capacity support was deficient.  This script asks whether
the STAR part of every such X localizes to one diameter-pair bundle, or at
least to support-overlap components each carried by one diameter pair.

G21 refuted the encompassing G3 localization route.  The bundle measurements
are retained as historical diagnostics, not as a current sufficient reduction.
"""
from __future__ import annotations

import argparse
import itertools
import sys
from collections import Counter, defaultdict

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b1_hall_profile as hall  # noqa: E402
import core  # noqa: E402


def star_outer_pairs(row: dict, dist: list[list[int]]) -> set[tuple[int, int]]:
    keys = set()
    for (a1, b1), (a2, b2) in itertools.combinations(row["pairs"], 2):
        common = {a1, b1} & {a2, b2}
        if len(common) != 1:
            continue
        center = next(iter(common))
        p = b1 if a1 == center else a1
        q = b2 if a2 == center else a2
        if dist[p][q] == 4 and dist[p][center] + dist[center][q] == 4:
            keys.add(tuple(sorted((p, q))))
    return keys


def subset_record(rows: list[dict], deg2: list[int], dist: list[list[int]], chosen: list[int]) -> dict:
    support = set()
    demand = 0
    starry = []
    diffuse = []
    key_to_rows: dict[tuple[int, int], set[int]] = defaultdict(set)
    for i in chosen:
        row = rows[i]
        support.update(row["support"])
        demand += row["demand"]
        keys = star_outer_pairs(row, dist)
        if keys:
            starry.append(i)
            for key in keys:
                key_to_rows[key].add(i)
        else:
            diffuse.append(i)

    star_support = set()
    star_demand = 0
    for i in starry:
        star_support.update(rows[i]["support"])
        star_demand += rows[i]["demand"]

    row_graph_parent = {i: i for i in starry}

    def find(x: int) -> int:
        while row_graph_parent[x] != x:
            row_graph_parent[x] = row_graph_parent[row_graph_parent[x]]
            x = row_graph_parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            row_graph_parent[rb] = ra

    for a, b in itertools.combinations(starry, 2):
        if set(rows[a]["support"]) & set(rows[b]["support"]):
            union(a, b)

    components: dict[int, list[int]] = defaultdict(list)
    for i in starry:
        components[find(i)].append(i)

    component_rows = []
    for comp in components.values():
        comp_support = set()
        comp_demand = 0
        comp_keys = set()
        for i in comp:
            comp_support.update(rows[i]["support"])
            comp_demand += rows[i]["demand"]
            comp_keys.update(star_outer_pairs(rows[i], dist))
        extra = sum(deg2[v] - 3 for v in comp_support)
        component_rows.append(
            {
                "rows": sorted(comp),
                "keys": sorted(comp_keys),
                "demand": comp_demand,
                "support": sorted(comp_support),
                "card_deficit": comp_demand - len(comp_support),
                "min_deg2": min((deg2[v] for v in comp_support), default=None),
                "extra": extra,
                "extra_margin": extra - comp_demand,
            }
        )

    key_rows = []
    for key, idxs in key_to_rows.items():
        key_support = set()
        key_demand = 0
        for i in idxs:
            key_support.update(rows[i]["support"])
            key_demand += rows[i]["demand"]
        extra = sum(deg2[v] - 3 for v in key_support)
        key_rows.append(
            {
                "key": key,
                "rows": sorted(idxs),
                "demand": key_demand,
                "support": sorted(key_support),
                "card_deficit": key_demand - len(key_support),
                "min_deg2": min((deg2[v] for v in key_support), default=None),
                "extra": extra,
                "extra_margin": extra - key_demand,
            }
        )

    return {
        "chosen": chosen,
        "demand": demand,
        "support": sorted(support),
        "card_deficit": demand - len(support),
        "starry": sorted(starry),
        "diffuse": sorted(diffuse),
        "star_keys": sorted(key_to_rows),
        "star_demand": star_demand,
        "star_support": sorted(star_support),
        "star_extra": sum(deg2[v] - 3 for v in star_support),
        "star_extra_margin": sum(deg2[v] - 3 for v in star_support) - star_demand,
        "key_rows": sorted(key_rows, key=lambda item: item["key"]),
        "component_rows": sorted(component_rows, key=lambda item: item["rows"]),
    }


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    data = hall.collision_rows(n, edges)
    rows = data["rows"]
    deg2 = data["deg2"]
    if len(rows) > 22:
        return {"skipped": True, "num_classes": len(rows)}

    card_deficient = []
    worst = None
    single_pair_fail = None
    component_single_pair_fail = None
    component_reserve_fail = None
    key_reserve_fail = None
    component_rule_fail = None
    component_card_def_count = 0
    min_component_extra_margin = None
    min_component_min_deg2 = None
    min_card_def_component_min_deg2 = None
    max_component_density_num = 0
    max_component_density_den = 1
    for mask in range(1, 1 << len(rows)):
        chosen = [i for i in range(len(rows)) if mask & (1 << i)]
        rec = subset_record(rows, deg2, dist, chosen)
        if rec["card_deficit"] <= 0:
            continue
        card_deficient.append(rec)
        if worst is None or rec["card_deficit"] > worst["card_deficit"]:
            worst = rec
        if len(rec["star_keys"]) > 1 and single_pair_fail is None:
            single_pair_fail = rec
        if any(len(comp["keys"]) > 1 for comp in rec["component_rows"]) and component_single_pair_fail is None:
            component_single_pair_fail = rec
        if any(comp["extra_margin"] < 0 for comp in rec["component_rows"]) and component_reserve_fail is None:
            component_reserve_fail = rec
        if any(key["extra_margin"] < 0 for key in rec["key_rows"]) and key_reserve_fail is None:
            key_reserve_fail = rec
        for comp in rec["component_rows"]:
            support_size = len(comp["support"])
            if support_size and comp["demand"] * max_component_density_den > max_component_density_num * support_size:
                max_component_density_num = comp["demand"]
                max_component_density_den = support_size
            min_component_extra_margin = (
                comp["extra_margin"]
                if min_component_extra_margin is None
                else min(min_component_extra_margin, comp["extra_margin"])
            )
            if comp["min_deg2"] is not None:
                min_component_min_deg2 = (
                    comp["min_deg2"]
                    if min_component_min_deg2 is None
                    else min(min_component_min_deg2, comp["min_deg2"])
                )
            if comp["card_deficit"] > 0:
                component_card_def_count += 1
                if comp["min_deg2"] is not None:
                    min_card_def_component_min_deg2 = (
                        comp["min_deg2"]
                        if min_card_def_component_min_deg2 is None
                        else min(min_card_def_component_min_deg2, comp["min_deg2"])
                    )
            low_density_ok = comp["card_deficit"] <= 0 and comp["min_deg2"] is not None and comp["min_deg2"] >= 4
            high_density_ok = (
                comp["card_deficit"] > 0
                and comp["min_deg2"] is not None
                and comp["min_deg2"] >= 5
                and comp["demand"] <= 2 * support_size
            )
            if not (low_density_ok or high_density_ok) and component_rule_fail is None:
                component_rule_fail = rec

    return {
        "skipped": False,
        "diam": diam,
        "num_classes": len(rows),
        "card_deficient_count": len(card_deficient),
        "max_card_deficit": 0 if worst is None else worst["card_deficit"],
        "worst": worst,
        "single_pair_fail": single_pair_fail,
        "component_single_pair_fail": component_single_pair_fail,
        "component_reserve_fail": component_reserve_fail,
        "key_reserve_fail": key_reserve_fail,
        "component_rule_fail": component_rule_fail,
        "component_card_def_count": component_card_def_count,
        "min_component_extra_margin": min_component_extra_margin,
        "min_component_min_deg2": min_component_min_deg2,
        "min_card_def_component_min_deg2": min_card_def_component_min_deg2,
        "max_component_density": (max_component_density_num, max_component_density_den),
        "shape_counts": Counter(
            (
                row["size"],
                bool(star_outer_pairs(row, dist)),
                row["components"],
                row["line_de"],
                row["line_den"],
            )
            for row in rows
        ),
    }


def summarize(tagged_graphs) -> dict:
    total = 0
    skipped = 0
    card_def_graphs = 0
    max_card_deficit = 0
    single_pair_fail = 0
    component_single_pair_fail = 0
    component_reserve_fail = 0
    key_reserve_fail = 0
    component_rule_fail = 0
    component_card_def_count = 0
    min_component_extra_margin = None
    min_component_min_deg2 = None
    min_card_def_component_min_deg2 = None
    max_component_density_num = 0
    max_component_density_den = 1
    shapes = Counter()
    examples = []
    for tag, n, edges in tagged_graphs:
        g = hall.nx.Graph()
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
        shapes.update(result["shape_counts"])
        if result["card_deficient_count"]:
            card_def_graphs += 1
            max_card_deficit = max(max_card_deficit, result["max_card_deficit"])
        for key in ("single_pair_fail", "component_single_pair_fail", "component_reserve_fail", "key_reserve_fail", "component_rule_fail"):
            if result[key] is not None:
                if key == "single_pair_fail":
                    single_pair_fail += 1
                elif key == "component_single_pair_fail":
                    component_single_pair_fail += 1
                elif key == "component_reserve_fail":
                    component_reserve_fail += 1
                elif key == "key_reserve_fail":
                    key_reserve_fail += 1
                elif key == "component_rule_fail":
                    component_rule_fail += 1
        component_card_def_count += result["component_card_def_count"]
        if result["min_component_extra_margin"] is not None:
            min_component_extra_margin = (
                result["min_component_extra_margin"]
                if min_component_extra_margin is None
                else min(min_component_extra_margin, result["min_component_extra_margin"])
            )
        if result["min_component_min_deg2"] is not None:
            min_component_min_deg2 = (
                result["min_component_min_deg2"]
                if min_component_min_deg2 is None
                else min(min_component_min_deg2, result["min_component_min_deg2"])
            )
        if result["min_card_def_component_min_deg2"] is not None:
            min_card_def_component_min_deg2 = (
                result["min_card_def_component_min_deg2"]
                if min_card_def_component_min_deg2 is None
                else min(min_card_def_component_min_deg2, result["min_card_def_component_min_deg2"])
            )
        den = result["max_component_density"][1]
        num = result["max_component_density"][0]
        if den and num * max_component_density_den > max_component_density_num * den:
            max_component_density_num = num
            max_component_density_den = den
        if len(examples) < 6 and result["card_deficient_count"]:
            examples.append(
                {
                    "tag": tag,
                    "card_deficient_count": result["card_deficient_count"],
                    "max_card_deficit": result["max_card_deficit"],
                    "worst": result["worst"],
                    "single_pair_fail": result["single_pair_fail"],
                    "component_single_pair_fail": result["component_single_pair_fail"],
                    "component_reserve_fail": result["component_reserve_fail"],
                    "key_reserve_fail": result["key_reserve_fail"],
                    "component_rule_fail": result["component_rule_fail"],
                }
            )
    return {
        "total": total,
        "skipped": skipped,
        "card_def_graphs": card_def_graphs,
        "max_card_deficit": max_card_deficit,
        "single_pair_fail": single_pair_fail,
        "component_single_pair_fail": component_single_pair_fail,
        "component_reserve_fail": component_reserve_fail,
        "key_reserve_fail": key_reserve_fail,
        "component_rule_fail": component_rule_fail,
        "component_card_def_count": component_card_def_count,
        "min_component_extra_margin": min_component_extra_margin,
        "min_component_min_deg2": min_component_min_deg2,
        "min_card_def_component_min_deg2": min_card_def_component_min_deg2,
        "max_component_density": (max_component_density_num, max_component_density_den),
        "shapes": dict(shapes.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14, 15, 16])
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260628)
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
