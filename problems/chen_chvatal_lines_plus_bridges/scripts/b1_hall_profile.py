"""Profile the G3-Hall1 support inequalities.

This is an exploratory gate for the B1/G3 proof.  It keeps the same collision
support family as b1_collision_structure_probe.py, but reports the tightest
subfamily inequalities under two capacities:

  card(X)     = |union S_L|
  weighted(X) = sum_{v in union S_L} (degG2(v)-2)

The useful diagnostic is whether the cardinal deficit

  demand(X) - |union S_L|

is exactly compensated by high distance-2 degree inside DEN.
"""
from __future__ import annotations

import argparse
import itertools
import random
import subprocess
import sys
from collections import Counter, defaultdict

import networkx as nx

sys.path.insert(0, "scripts")
import core  # noqa: E402


def is_three_connected(g: nx.Graph) -> bool:
    if g.number_of_nodes() < 4 or min(dict(g.degree()).values()) < 3:
        return False
    for a, b in itertools.combinations(list(g.nodes()), 2):
        h = g.copy()
        h.remove_nodes_from([a, b])
        if h.number_of_nodes() and not nx.is_connected(h):
            return False
    return True


def collision_rows(n: int, edges: list[tuple[int, int]]) -> dict:
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

    by_line: dict[frozenset[int], list[tuple[int, int]]] = defaultdict(list)
    for a, b in itertools.combinations(range(n), 2):
        if dist[a][b] == 2:
            by_line[core.line_of_pair(dist, n, a, b)].append((a, b))

    rows = []
    for line, pairs in by_line.items():
        if len(pairs) <= 1:
            continue
        endpoints = set(itertools.chain.from_iterable(pairs))
        pair_graph = nx.Graph()
        pair_graph.add_nodes_from(endpoints)
        pair_graph.add_edges_from(pairs)
        star_triples = 0
        for (a1, b1), (a2, b2) in itertools.combinations(pairs, 2):
            common = {a1, b1} & {a2, b2}
            if len(common) == 1:
                a = next(iter(common))
                p = b1 if a1 == a else a1
                q = b2 if a2 == a else a2
                if dist[p][q] == 4 and dist[p][a] + dist[a][q] == 4:
                    star_triples += 1
        star_outer_de = None
        if len(pairs) == 2 and pair_graph.number_of_nodes() == 3:
            common = set(pairs[0]) & set(pairs[1])
            if len(common) == 1:
                outer = endpoints - common
                star_outer_de = len(outer & de)
        base = endpoints | set(line)
        expanded = set(base)
        for v in base:
            expanded.update(adj[v])
        support = expanded & den
        common_endpoint = set(pairs[0])
        for pair in pairs[1:]:
            common_endpoint &= set(pair)
        rows.append(
            {
                "line": sorted(line),
                "pairs": pairs,
                "demand": 2 * (len(pairs) - 1),
                "support": support,
                "size": len(pairs),
                "common_endpoint": bool(common_endpoint),
                "components": nx.number_connected_components(pair_graph),
                "cycle_rank": len(pairs) - len(endpoints) + nx.number_connected_components(pair_graph),
                "star_units": star_triples,
                "endpoints_de": len(endpoints & de),
                "star_outer_de": star_outer_de,
                "line_de": len(set(line) & de),
                "line_den": len(set(line) & den),
            }
        )
    return {"diam": diam, "deg2": deg2, "de": de, "den": den, "rows": rows}


def profile(n: int, edges: list[tuple[int, int]]) -> dict:
    data = collision_rows(n, edges)
    deg2 = data["deg2"]
    rows = data["rows"]
    best_card = None
    best_weight = None
    best_extra = None
    conditional_split_fail = None
    def best_subset(allowed: set[int] | None = None, *, unit_capacity: bool = False, reserve: bool = False):
        if len(rows) > 22:
            return None
        best = None
        allowed_mask = 0
        for i in range(len(rows)):
            if allowed is None or i in allowed:
                allowed_mask |= 1 << i
        submask = allowed_mask
        while submask:
            mask = submask
            chosen = [i for i in range(len(rows)) if mask & (1 << i)]
            support = set()
            demand = 0
            for i in chosen:
                support.update(rows[i]["support"])
                demand += rows[i]["demand"]
            card_supply = len(support)
            weighted_supply = sum(deg2[v] - 2 for v in support)
            extra_supply = sum(deg2[v] - 3 for v in support)
            card_deficit = demand - card_supply
            weighted_margin = weighted_supply - demand
            reserve_margin = weighted_supply - demand - card_supply
            record = {
                "chosen": chosen,
                "demand": demand,
                "support": sorted(support),
                "card_supply": card_supply,
                "card_deficit": card_deficit,
                "extra_supply": extra_supply,
                "min_deg2_support": min((deg2[v] for v in support), default=None),
                "deg2_support": {v: deg2[v] for v in sorted(support)},
                "weighted_supply": weighted_supply,
                "weighted_margin": weighted_margin,
                "reserve_margin": reserve_margin,
            }
            if record["min_deg2_support"] is not None:
                record["min_deg2_scaled_margin"] = (record["min_deg2_support"] - 2) * card_supply - demand
            else:
                record["min_deg2_scaled_margin"] = None
            if best is None:
                best = record
            elif unit_capacity and card_deficit > best["card_deficit"]:
                best = record
            elif reserve and reserve_margin < best["reserve_margin"]:
                best = record
            elif not unit_capacity and not reserve and weighted_margin < best["weighted_margin"]:
                best = record
            submask = (submask - 1) & allowed_mask
        return best

    best_card = best_subset(unit_capacity=True)
    best_weight = best_subset()
    if len(rows) <= 22:
        for mask in range(1, 1 << len(rows)):
            chosen = [i for i in range(len(rows)) if mask & (1 << i)]
            support = set()
            demand = 0
            for i in chosen:
                support.update(rows[i]["support"])
                demand += rows[i]["demand"]
            card_supply = len(support)
            extra_supply = sum(deg2[v] - 3 for v in support)
            weighted_supply = sum(deg2[v] - 2 for v in support)
            card_deficit = demand - card_supply
            record = {
                "chosen": chosen,
                "demand": demand,
                "support": sorted(support),
                "card_supply": card_supply,
                "card_deficit": card_deficit,
                "extra_supply": extra_supply,
                "min_deg2_support": min((deg2[v] for v in support), default=None),
                "deg2_support": {v: deg2[v] for v in sorted(support)},
                "weighted_supply": weighted_supply,
                "weighted_margin": weighted_supply - demand,
                "min_deg2_scaled_margin": None,
            }
            if record["min_deg2_support"] is not None:
                record["min_deg2_scaled_margin"] = (record["min_deg2_support"] - 2) * card_supply - demand
            if card_deficit > 0 and (best_extra is None or extra_supply - card_deficit < best_extra["extra_minus_deficit"]):
                best_extra = {**record, "extra_minus_deficit": extra_supply - card_deficit}
    diffuse = {i for i, row in enumerate(rows) if row["star_units"] == 0}
    starry = {i for i, row in enumerate(rows) if row["star_units"] > 0}
    best_card_diffuse = best_subset(diffuse, unit_capacity=True)
    best_weight_starry = best_subset(starry)
    best_reserve_starry = best_subset(starry, reserve=True)
    if len(rows) <= 22:
        for mask in range(1, 1 << len(rows)):
            chosen = [i for i in range(len(rows)) if mask & (1 << i)]
            support = set()
            demand = 0
            for i in chosen:
                support.update(rows[i]["support"])
                demand += rows[i]["demand"]
            if demand <= len(support):
                continue
            diffuse_part = {i for i in chosen if rows[i]["star_units"] == 0}
            starry_part = {i for i in chosen if rows[i]["star_units"] > 0}
            diffuse_cert = best_subset(diffuse_part, unit_capacity=True)
            starry_cert = best_subset(starry_part, reserve=True)
            diffuse_ok = diffuse_cert is None or diffuse_cert["card_deficit"] <= 0
            starry_ok = starry_cert is not None and starry_cert["reserve_margin"] >= 0
            if not (diffuse_ok and starry_ok):
                conditional_split_fail = {
                    "chosen": chosen,
                    "demand": demand,
                    "support": sorted(support),
                    "card_supply": len(support),
                    "card_deficit": demand - len(support),
                    "diffuse_part": sorted(diffuse_part),
                    "starry_part": sorted(starry_part),
                    "diffuse_cert": diffuse_cert,
                    "starry_cert": starry_cert,
                }
                break
    shape_counts = Counter(
        (
            row["size"],
            row["common_endpoint"],
            row["components"],
            row["cycle_rank"],
            row["star_units"],
            row["endpoints_de"],
            row["star_outer_de"],
            row["line_de"],
            row["line_den"],
        )
        for row in rows
    )
    return {
        "diam": data["diam"],
        "num_classes": len(rows),
        "collisions": sum(row["size"] - 1 for row in rows),
        "best_card": best_card,
        "best_weight": best_weight,
        "best_extra": best_extra,
        "best_card_diffuse": best_card_diffuse,
        "best_weight_starry": best_weight_starry,
        "best_reserve_starry": best_reserve_starry,
        "conditional_split_fail": conditional_split_fail,
        "shapes": shape_counts,
        "rows": rows,
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


def random_sparse(order: int, count: int, seed: int):
    rng = random.Random(seed)
    yielded = 0
    attempts = 0
    while yielded < count and attempts < count * 30000:
        attempts += 1
        mode = attempts % 3
        try:
            if mode == 0 and order % 2 == 0:
                g = nx.random_regular_graph(3, order, seed=rng.randrange(1 << 30))
            elif mode == 1 and (4 * order) % 2 == 0:
                g = nx.random_regular_graph(4, order, seed=rng.randrange(1 << 30))
            else:
                m = rng.randint(max(order + 2, int(1.55 * order)), max(order + 3, int(2.35 * order)))
                g = nx.gnm_random_graph(order, m, seed=rng.randrange(1 << 30))
        except nx.NetworkXError:
            continue
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


def family_graphs(ms: list[int]):
    for m in ms:
        for name, (n, edges) in families(m).items():
            yield f"{name}_{m}", n, edges


def families(m: int) -> dict[str, tuple[int, list[tuple[int, int]]]]:
    out = {}
    edges = []
    for i in range(m):
        edges.append((i, (i + 1) % m))
        edges.append((m + i, m + (i + 1) % m))
        edges.append((i, m + i))
    out["prism"] = (2 * m, edges)

    edges = []
    n = 2 * m
    for i in range(n):
        edges.append((i, (i + 1) % n))
    for i in range(m):
        edges.append((i, i + m))
    out["mobius"] = (n, edges)

    edges = []
    for i in range(m):
        edges.append((i, (i + 1) % m))
        edges.append((m + i, m + (i + 1) % m))
        edges.append((i, m + i))
        edges.append((i, m + (i + 1) % m))
    out["antiprism"] = (2 * m, edges)
    return out


def geng_graphs(specs: list[str]):
    for spec in specs:
        n_s, band = spec.split(":", 1)
        n = int(n_s)
        cmd = ["geng", "-C", "-d3", "-q", str(n), band]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
        assert proc.stdout is not None
        for line in proc.stdout:
            g6 = line.strip()
            if not g6:
                continue
            nn, edges = core.graph6_to_edges(g6)
            yield f"geng_{n}_{band}_{g6}", nn, edges
        proc.wait()


def summarize(tagged_graphs) -> dict:
    aggregate_shapes = Counter()
    total = 0
    card_fail = 0
    weighted_fail = 0
    max_card_deficit = 0
    diffuse_card_fail = 0
    starry_weight_fail = 0
    starry_reserve_fail = 0
    conditional_split_fail = 0
    min_starry_reserve_margin = None
    min_cardfail_deg2 = None
    min_scaled_margin_on_cardfail = None
    min_extra_minus_deficit = None
    min_weighted_margin = None
    examples = []
    for tag, n, edges in tagged_graphs:
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        if not is_three_connected(g):
            continue
        p = profile(n, edges)
        if p["diam"] < 4:
            continue
        total += 1
        aggregate_shapes.update(p["shapes"])
        bc = p["best_card"]
        bw = p["best_weight"]
        be = p["best_extra"]
        if bc and bc["card_deficit"] > 0:
            card_fail += 1
            max_card_deficit = max(max_card_deficit, bc["card_deficit"])
            min_cardfail_deg2 = bc["min_deg2_support"] if min_cardfail_deg2 is None else min(min_cardfail_deg2, bc["min_deg2_support"])
            min_scaled_margin_on_cardfail = bc["min_deg2_scaled_margin"] if min_scaled_margin_on_cardfail is None else min(min_scaled_margin_on_cardfail, bc["min_deg2_scaled_margin"])
        if bw and bw["weighted_margin"] < 0:
            weighted_fail += 1
        bcd = p["best_card_diffuse"]
        bws = p["best_weight_starry"]
        brs = p["best_reserve_starry"]
        if bcd and bcd["card_deficit"] > 0:
            diffuse_card_fail += 1
        if bws and bws["weighted_margin"] < 0:
            starry_weight_fail += 1
        if brs:
            min_starry_reserve_margin = brs["reserve_margin"] if min_starry_reserve_margin is None else min(min_starry_reserve_margin, brs["reserve_margin"])
            if brs["reserve_margin"] < 0:
                starry_reserve_fail += 1
        if p["conditional_split_fail"] is not None:
            conditional_split_fail += 1
        if be is not None:
            min_extra_minus_deficit = be["extra_minus_deficit"] if min_extra_minus_deficit is None else min(min_extra_minus_deficit, be["extra_minus_deficit"])
        if bw is not None:
            min_weighted_margin = bw["weighted_margin"] if min_weighted_margin is None else min(min_weighted_margin, bw["weighted_margin"])
        if len(examples) < 6 and ((bc and bc["card_deficit"] > 0) or (bw and bw["weighted_margin"] <= 2)):
            examples.append(
                {
                    "tag": tag,
                    "num_classes": p["num_classes"],
                    "collisions": p["collisions"],
                    "best_card": bc,
                    "best_weight": bw,
                    "best_extra": be,
                    "best_card_diffuse": bcd,
                    "best_weight_starry": bws,
                    "best_reserve_starry": brs,
                    "conditional_split_fail": p["conditional_split_fail"],
                }
            )
    return {
        "total": total,
        "card_fail": card_fail,
        "weighted_fail": weighted_fail,
        "diffuse_card_fail": diffuse_card_fail,
        "starry_weight_fail": starry_weight_fail,
        "starry_reserve_fail": starry_reserve_fail,
        "conditional_split_fail": conditional_split_fail,
        "min_starry_reserve_margin": min_starry_reserve_margin,
        "max_card_deficit": max_card_deficit,
        "min_cardfail_deg2": min_cardfail_deg2,
        "min_scaled_margin_on_cardfail": min_scaled_margin_on_cardfail,
        "min_extra_minus_deficit": min_extra_minus_deficit,
        "min_weighted_margin": min_weighted_margin,
        "shapes": dict(aggregate_shapes.most_common(12)),
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", nargs="*", type=int, default=[11, 12, 13, 14])
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260628)
    parser.add_argument("--source", choices=["gnp", "sparse"], default="gnp")
    parser.add_argument("--family-ms", nargs="*", type=int, default=[])
    parser.add_argument("--geng", nargs="*", default=[], help="exact geng specs like 13:20:22")
    parser.add_argument("--g6", nargs="*")
    args = parser.parse_args()

    if args.g6:
        rows = []
        for g6 in args.g6:
            n, edges = core.graph6_to_edges(g6)
            rows.append((g6, n, edges))
        print({"named": summarize(rows)})
        return

    if args.family_ms:
        print({"families": summarize(family_graphs(args.family_ms))})
    if args.geng:
        print({"geng": summarize(geng_graphs(args.geng))})
    for order in args.orders:
        if args.source == "sparse":
            rows = ((g6, order, edges) for g6, edges in random_sparse(order, args.samples, args.seed + order))
        else:
            rows = ((g6, order, edges) for g6, edges in random_three_connected(order, args.samples, args.seed + order))
        print({f"{args.source}_n{order}": summarize(rows)})


if __name__ == "__main__":
    main()
