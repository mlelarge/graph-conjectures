"""Historical probe of distance-2 line-collision structure in Lemma B/B1.

This is an exploratory gate, not a proof.  It classifies color classes of the
distance-2 graph G2, where the color of edge ab is the metric line L(a,b).
It was originally designed to feed the localized G3 target:

    2 * collisions <= E(DE union N(DE)).

G3 is false by G21.  The classifications remain useful diagnostics for a
genuinely global B1 argument, but this script provides no live G3 route.
"""
from __future__ import annotations

import argparse
import itertools
import random
import sys
from collections import Counter, defaultdict

import networkx as nx

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402


def is_three_connected(g: nx.Graph) -> bool:
    if g.number_of_nodes() < 4 or min(dict(g.degree()).values()) < 3:
        return False
    nodes = list(g.nodes())
    for a, b in itertools.combinations(nodes, 2):
        h = g.copy()
        h.remove_nodes_from([a, b])
        if h.number_of_nodes() and not nx.is_connected(h):
            return False
    return True


def analyze(n: int, edges: list[tuple[int, int]]) -> dict:
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    deg2 = [sum(1 for u in range(n) if dist[v][u] == 2) for v in range(n)]
    ecc = [max(dist[v]) for v in range(n)]
    de = {v for v in range(n) if ecc[v] == diam}
    den = set(de)
    for v in de:
        den.update(adj[v])

    line_to_pairs: dict[frozenset[int], list[tuple[int, int]]] = defaultdict(list)
    for a, b in itertools.combinations(range(n), 2):
        if dist[a][b] == 2:
            line_to_pairs[core.line_of_pair(dist, n, a, b)].append((a, b))

    class_rows = []
    for line, pairs in line_to_pairs.items():
        if len(pairs) <= 1:
            continue
        endpoints = set(itertools.chain.from_iterable(pairs))
        common_endpoint = set(pairs[0])
        for p in pairs[1:]:
            common_endpoint &= set(p)
        pair_graph = nx.Graph()
        pair_graph.add_nodes_from(endpoints)
        pair_graph.add_edges_from(pairs)
        base_support = endpoints | set(line)
        expanded_support = set(base_support)
        for v in base_support:
            expanded_support.update(adj[v])
        star_triples = 0
        for (a1, b1), (a2, b2) in itertools.combinations(pairs, 2):
            common = {a1, b1} & {a2, b2}
            if len(common) == 1:
                a = next(iter(common))
                p = b1 if a1 == a else a1
                q = b2 if a2 == a else a2
                if dist[p][q] == 4 and dist[p][a] + dist[a][q] == 4:
                    star_triples += 1
        class_rows.append(
            {
                "size": len(pairs),
                "collision": len(pairs) - 1,
                "endpoints": len(endpoints),
                "common_endpoint": len(common_endpoint),
                "components": nx.number_connected_components(pair_graph),
                "cycle_rank": len(pairs) - len(endpoints) + nx.number_connected_components(pair_graph),
                "endpoint_in_DE": len(endpoints & de),
                "endpoint_in_DEN": len(endpoints & den),
                "line_hits_DE": len(set(line) & de),
                "line_hits_DEN": len(set(line) & den),
                "star_triples": star_triples,
                "pairs": pairs,
                "support_DEN": base_support & den,
                "support_DEN1": expanded_support & den,
            }
        )

    collisions = sum(row["collision"] for row in class_rows)
    e_den = sum(deg2[v] - 2 for v in den)
    def support_hall(field: str, *, unit_capacity: bool = False):
        if len(class_rows) > 22:
            return None
        for mask in range(1, 1 << len(class_rows)):
            demand = 0
            support = set()
            chosen = []
            for i, row in enumerate(class_rows):
                if mask & (1 << i):
                    demand += 2 * row["collision"]
                    support.update(row[field])
                    chosen.append(i)
            supply = len(support) if unit_capacity else sum(deg2[v] - 2 for v in support)
            if supply < demand:
                return {
                    "chosen": chosen,
                    "demand": demand,
                    "supply": supply,
                    "support": sorted(support),
                }
        return None

    def dual_support_hall(field: str):
        if len(den) > 24:
            return None, {"den_size": len(den), "cap": 24}
        den_list = sorted(den)
        for mask in range(1 << len(den_list)):
            support = {den_list[i] for i in range(len(den_list)) if mask & (1 << i)}
            supply = sum(deg2[v] - 2 for v in support)
            trapped = [
                i for i, row in enumerate(class_rows)
                if row[field] <= support
            ]
            demand = sum(2 * class_rows[i]["collision"] for i in trapped)
            if demand > supply:
                return {
                    "trapped": trapped,
                    "demand": demand,
                    "supply": supply,
                    "support": sorted(support),
                }, None
        return None, None

    support_hall_fail = support_hall("support_DEN")
    support_hall1_fail = support_hall("support_DEN1")
    card_hall1_fail = support_hall("support_DEN1", unit_capacity=True)
    dual_hall1_fail, dual_hall1_skip = dual_support_hall("support_DEN1")
    return {
        "n": n,
        "diam": diam,
        "collisions": collisions,
        "g3_margin": e_den - 2 * collisions,
        "support_hall_ok": support_hall_fail is None,
        "support_hall_fail": support_hall_fail,
        "support_hall1_ok": support_hall1_fail is None,
        "support_hall1_fail": support_hall1_fail,
        "card_hall1_ok": card_hall1_fail is None,
        "card_hall1_fail": card_hall1_fail,
        "dual_hall1_checked": dual_hall1_skip is None,
        "dual_hall1_ok": dual_hall1_skip is None and dual_hall1_fail is None,
        "dual_hall1_fail": dual_hall1_fail,
        "dual_hall1_skip": dual_hall1_skip,
        "num_collision_classes": len(class_rows),
        "max_class": max((row["size"] for row in class_rows), default=1),
        "shape_counts": Counter(
            (
                row["size"],
                row["common_endpoint"] > 0,
                row["components"],
                row["cycle_rank"],
                row["endpoint_in_DE"],
            )
            for row in class_rows
        ),
        "hit_shape_counts": Counter(
            (
                row["size"],
                row["common_endpoint"] > 0,
                row["endpoint_in_DE"],
                row["endpoint_in_DEN"],
                row["line_hits_DE"],
                row["line_hits_DEN"],
            )
            for row in class_rows
        ),
        "largest_classes": sorted(
            class_rows,
            key=lambda row: (-row["size"], -row["star_triples"], row["endpoints"]),
        )[:8],
    }


def random_three_connected(order: int, count: int, seed: int):
    rng = random.Random(seed)
    yielded = 0
    attempts = 0
    while yielded < count and attempts < count * 20000:
        attempts += 1
        g = nx.gnp_random_graph(order, rng.uniform(0.2, 0.45), seed=rng.randrange(1 << 30))
        if not nx.is_connected(g):
            continue
        edges = list(g.edges())
        dist = core.all_pairs_distances(order, edges)
        if max(dist[i][j] for i in range(order) for j in range(order)) < 4:
            continue
        if not is_three_connected(g):
            continue
        yielded += 1
        yield nx.to_graph6_bytes(g, header=False).decode().strip(), edges


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14])
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260628)
    parser.add_argument("--g6", nargs="*")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    if args.g6:
        for g6 in args.g6:
            n, edges = core.graph6_to_edges(g6)
            print("GRAPH", g6, analyze(n, edges))
        return

    for order in args.orders:
        print("ORDER", order)
        if args.summary:
            total = 0
            aggregate_shapes = Counter()
            aggregate_hits = Counter()
            max_class = 1
            max_collisions = 0
            support_hall_fail = 0
            support_hall1_fail = 0
            card_hall1_fail = 0
            dual_hall1_checked = 0
            dual_hall1_fail = 0
            dual_hall1_skipped = 0
            worst_margin = None
            examples = []
            for g6, edges in random_three_connected(order, args.samples, args.seed + order):
                total += 1
                summary = analyze(order, edges)
                aggregate_shapes.update(summary["shape_counts"])
                aggregate_hits.update(summary["hit_shape_counts"])
                max_class = max(max_class, summary["max_class"])
                max_collisions = max(max_collisions, summary["collisions"])
                support_hall_fail += 0 if summary["support_hall_ok"] else 1
                support_hall1_fail += 0 if summary["support_hall1_ok"] else 1
                card_hall1_fail += 0 if summary["card_hall1_ok"] else 1
                dual_hall1_checked += 1 if summary["dual_hall1_checked"] else 0
                dual_hall1_skipped += 0 if summary["dual_hall1_checked"] else 1
                dual_hall1_fail += 1 if summary["dual_hall1_checked"] and not summary["dual_hall1_ok"] else 0
                worst_margin = summary["g3_margin"] if worst_margin is None else min(worst_margin, summary["g3_margin"])
                if summary["max_class"] >= 3 or summary["collisions"] >= 4 or not summary["support_hall_ok"] or not summary["support_hall1_ok"] or not summary["card_hall1_ok"] or (summary["dual_hall1_checked"] and not summary["dual_hall1_ok"]):
                    examples.append((g6, {k: summary[k] for k in ("collisions", "g3_margin", "support_hall_ok", "support_hall_fail", "support_hall1_ok", "support_hall1_fail", "card_hall1_ok", "card_hall1_fail", "dual_hall1_checked", "dual_hall1_ok", "dual_hall1_fail", "dual_hall1_skip", "num_collision_classes", "max_class")}))
            print("  total", total, "max_class", max_class, "max_collisions", max_collisions, "min_g3_margin", worst_margin, "support_hall_fail", support_hall_fail, "support_hall1_fail", support_hall1_fail, "card_hall1_fail", card_hall1_fail, "dual_hall1_checked", dual_hall1_checked, "dual_hall1_fail", dual_hall1_fail, "dual_hall1_skipped", dual_hall1_skipped)
            print("  shapes", dict(aggregate_shapes.most_common(12)))
            print("  hit_shapes", dict(aggregate_hits.most_common(12)))
            print("  examples", examples[:8])
            continue
        for g6, edges in random_three_connected(order, args.samples, args.seed + order):
            summary = analyze(order, edges)
            print("GRAPH", g6)
            print("  basic", {k: summary[k] for k in ("n", "diam", "collisions", "g3_margin", "support_hall_ok", "support_hall_fail", "support_hall1_ok", "support_hall1_fail", "card_hall1_ok", "card_hall1_fail", "dual_hall1_checked", "dual_hall1_ok", "dual_hall1_fail", "dual_hall1_skip", "num_collision_classes", "max_class")})
            print("  shapes", dict(summary["shape_counts"].most_common(8)))
            for row in summary["largest_classes"][:3]:
                compact = {k: row[k] for k in ("size", "collision", "endpoints", "common_endpoint", "components", "cycle_rank", "endpoint_in_DE", "endpoint_in_DEN", "line_hits_DE", "star_triples", "support_DEN")}
                print("  class", compact, "pairs", row["pairs"])


if __name__ == "__main__":
    main()
