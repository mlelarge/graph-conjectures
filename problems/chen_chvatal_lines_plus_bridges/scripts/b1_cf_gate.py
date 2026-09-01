"""Gate for CF collision-class structure in Lemma B/B1.

For a 3-connected graph G with diam>=4, color every distance-2 pair ab by the
metric line L(a,b).  For each color/line L, let F_L be the graph whose edges are
the distance-2 pairs realizing L.

CF structural target:
    every collided F_L is a forest with |E(F_L)| <= 3, and every size-3 class is
    P2 union K2.

CF may still inform a genuinely global B1 argument.  Its former use as a step
toward the localized G3 inequality does not survive G21: G3 and its descendants
are false.  This script is a verification/stress gate, not a proof of CF or B1.
"""
from __future__ import annotations

import argparse
import itertools
import random
import subprocess
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


def classify(n: int, edges: list[tuple[int, int]]) -> dict | None:
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    if not is_three_connected(g):
        return None
    dist = core.all_pairs_distances(n, edges)
    diam = max(dist[i][j] for i in range(n) for j in range(n))
    if diam < 4:
        return None

    by_line: dict[frozenset[int], list[tuple[int, int]]] = defaultdict(list)
    for a, b in itertools.combinations(range(n), 2):
        if dist[a][b] == 2:
            by_line[core.line_of_pair(dist, n, a, b)].append((a, b))

    failures = []
    shapes = Counter()
    max_class = 1
    collided = 0
    for line, pairs in by_line.items():
        if len(pairs) <= 1:
            continue
        collided += 1
        max_class = max(max_class, len(pairs))
        endpoints = set(itertools.chain.from_iterable(pairs))
        h = nx.Graph()
        h.add_nodes_from(endpoints)
        h.add_edges_from(pairs)
        comps = list(nx.connected_components(h))
        comp_edge_sizes = sorted((h.subgraph(c).number_of_edges() for c in comps), reverse=True)
        cycle_rank = h.number_of_edges() - h.number_of_nodes() + len(comps)
        shape = (len(pairs), h.number_of_nodes(), len(comps), tuple(comp_edge_sizes), cycle_rank)
        shapes[shape] += 1
        ok_size3 = len(pairs) != 3 or shape == (3, 5, 2, (2, 1), 0)
        if cycle_rank != 0 or len(pairs) > 3 or not ok_size3:
            failures.append(
                {
                    "line_size": len(line),
                    "pairs": pairs,
                    "shape": shape,
                    "line": sorted(line),
                }
            )

    return {
        "n": n,
        "m": len(edges),
        "diam": diam,
        "collided_classes": collided,
        "max_class": max_class,
        "shapes": shapes,
        "cf_ok": not failures,
        "failures": failures[:5],
    }


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
        if not is_three_connected(g):
            continue
        edges = list(g.edges())
        dist = core.all_pairs_distances(order, edges)
        if max(dist[i][j] for i in range(order) for j in range(order)) < 4:
            continue
        yielded += 1
        yield nx.to_graph6_bytes(g, header=False).decode().strip(), order, edges


def family_graphs(ms: list[int]):
    for m in ms:
        for name, (n, edges) in families(m).items():
            yield f"{name}_{m}", n, edges


def families(m: int) -> dict[str, tuple[int, list[tuple[int, int]]]]:
    """Long 3-connected tube families used as asymptotic stress tests."""
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
        returncode = proc.wait()
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, cmd)


def summarize(rows):
    out = {
        "graphs": 0,
        "cf_fail": 0,
        "max_class": 1,
        "diam_hist": Counter(),
        "shape_hist": Counter(),
        "fail_examples": [],
    }
    for tag, n, edges in rows:
        row = classify(n, edges)
        if row is None:
            continue
        out["graphs"] += 1
        out["max_class"] = max(out["max_class"], row["max_class"])
        out["diam_hist"][row["diam"]] += 1
        out["shape_hist"].update(row["shapes"])
        if not row["cf_ok"]:
            out["cf_fail"] += 1
            if len(out["fail_examples"]) < 5:
                out["fail_examples"].append((tag, row))
    out["diam_hist"] = dict(sorted(out["diam_hist"].items()))
    out["shape_hist"] = {str(k): v for k, v in out["shape_hist"].most_common(12)}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--random-orders", nargs="*", type=int, default=[14, 18, 24, 32])
    parser.add_argument("--samples", type=int, default=80)
    parser.add_argument("--family-ms", nargs="*", type=int, default=[6, 8, 10, 12, 16, 20, 28, 36])
    parser.add_argument("--geng", nargs="*", default=[], help="exact geng specs like 13:20:22")
    parser.add_argument("--seed", type=int, default=20260628)
    parser.add_argument("--g6", nargs="*")
    args = parser.parse_args()

    if args.g6:
        rows = []
        for g6 in args.g6:
            n, edges = core.graph6_to_edges(g6)
            rows.append((g6, n, edges))
        print({"named": summarize(rows)})
        return

    family_summary = summarize(family_graphs(args.family_ms))
    print({"families": family_summary})
    if args.geng:
        print({"geng": summarize(geng_graphs(args.geng))})
    for order in args.random_orders:
        rows = random_sparse(order, args.samples, args.seed + order)
        print({f"random_n{order}": summarize(rows)})


if __name__ == "__main__":
    main()
