"""Build the joint-invariant feature corpus for plan v10 search.

Output:
    data/joint_invariant_scan.json        -- max-degsum ears only.
    data/joint_invariant_scan_all_ears.json -- every simplicial ear.

Inputs:
    1. Enumerated 2-trees, n=4..10 (from data/two_trees_n10.json).
    2. Random 2-trees: 50 seeds at each n in {15, 20, 30, 50, 100}.
    3. Structured families: BT(k, 2), books B_k, 2-paths L_n, fans F_n.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from joint_invariant_features import ear_records, from_graph6  # noqa: E402
from extreme_family import book_with_tail  # noqa: E402

DATA = ROOT / "data"


def random_two_tree(n: int, seed: int) -> nx.Graph:
    rng = random.Random(seed)
    G = nx.complete_graph(3)
    while G.number_of_nodes() < n:
        edges = list(G.edges())
        a, b = rng.choice(edges)
        v = G.number_of_nodes()
        G.add_node(v)
        G.add_edge(v, a)
        G.add_edge(v, b)
    return G


def book_graph(k: int) -> nx.Graph:
    """B_k = book with k pages on spine (0,1); n = k+2."""
    G = nx.Graph()
    G.add_edge(0, 1)
    for j in range(k):
        G.add_edge(0, 2 + j)
        G.add_edge(1, 2 + j)
    return G


def two_path_graph(n: int) -> nx.Graph:
    """L_n = 2-path on n vertices. K_3 on {0,1,2}; vertex i (i>=3) is
    attached to (i-2, i-1) forming a triangle."""
    assert n >= 3
    G = nx.complete_graph(3)
    for i in range(3, n):
        G.add_edge(i - 2, i)
        G.add_edge(i - 1, i)
    return G


def fan_graph(n: int) -> nx.Graph:
    """F_n = fan on n vertices: a path on n-1 vertices {1, .., n-1}
    joined to a hub vertex 0. Equivalently, repeatedly add vertex i to
    edge (0, i-1)."""
    assert n >= 3
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_edge(0, 2)
    G.add_edge(1, 2)
    for i in range(3, n):
        G.add_edge(0, i)
        G.add_edge(i - 1, i)
    return G


def collect_records():
    all_ears: list[dict] = []
    max_ears: list[dict] = []
    seen = 0

    def add(G: nx.Graph, tag: str, extra: dict | None = None):
        nonlocal seen
        recs = ear_records(G)
        for r in recs:
            r["source"] = tag
            if extra:
                r.update(extra)
            all_ears.append(r)
            if r["is_max_degsum"]:
                max_ears.append(r)
        seen += 1

    # 1. Enumerated 2-trees n=4..10
    enum_path = DATA / "two_trees_n10.json"
    enum = json.loads(enum_path.read_text())
    for n_str in ["4", "5", "6", "7", "8", "9", "10"]:
        codes = enum[n_str]
        for code in codes:
            G = from_graph6(code)
            add(G, f"enum_n{n_str}", {"family": "enum", "param_n": int(n_str)})
        print(f"  enum n={n_str}: {len(codes)} graphs", file=sys.stderr)

    # 2. Random 2-trees, 50 seeds each at n in {15,20,30,50,100}
    for n in [15, 20, 30, 50, 100]:
        for seed in range(50):
            G = random_two_tree(n, seed)
            add(G, f"random_n{n}_s{seed}",
                {"family": "random", "param_n": n, "seed": seed})
        print(f"  random n={n}: 50 seeds", file=sys.stderr)

    # 3. Structured families
    # BT(k, 2) for k in {2,5,10,25,50,100}
    for k in [2, 5, 10, 25, 50, 100]:
        G = book_with_tail(k, 2)
        add(G, f"BT_k{k}_t2", {"family": "BT", "k": k, "t": 2,
                                "param_n": G.number_of_nodes()})
    # Books B_k for k in {2..30}
    for k in range(2, 31):
        G = book_graph(k)
        add(G, f"book_k{k}", {"family": "book", "k": k,
                               "param_n": G.number_of_nodes()})
    # 2-paths L_n for n in {4..30}
    for n in range(4, 31):
        G = two_path_graph(n)
        add(G, f"L_n{n}", {"family": "L", "param_n": n})
    # Fans F_n for n in {4..30}
    for n in range(4, 31):
        G = fan_graph(n)
        add(G, f"F_n{n}", {"family": "F", "param_n": n})

    print(f"\nGraphs processed: {seen}", file=sys.stderr)
    print(f"All-ear records:    {len(all_ears)}", file=sys.stderr)
    print(f"Max-degsum records: {len(max_ears)}", file=sys.stderr)
    return all_ears, max_ears


def main():
    all_ears, max_ears = collect_records()
    (DATA / "joint_invariant_scan.json").write_text(json.dumps(max_ears))
    (DATA / "joint_invariant_scan_all_ears.json").write_text(json.dumps(all_ears))
    print(f"wrote {len(max_ears)} max-degsum records to data/joint_invariant_scan.json")
    print(f"wrote {len(all_ears)} all-ear records to data/joint_invariant_scan_all_ears.json")


if __name__ == "__main__":
    main()
