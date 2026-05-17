"""Enumerate connected 2-trees up to isomorphism, save graph6 codes per order.

Recursive construction: start from K_3, then repeatedly add a new vertex
adjacent to both endpoints of an existing edge. Deduplicate via the
Weisfeiler-Lehman graph hash, with a final exact isomorphism filter to be safe.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx


def graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def from_graph6(code: str) -> nx.Graph:
    return nx.from_graph6_bytes(code.encode())


def two_tree_children(G: nx.Graph):
    """Yield all 2-trees obtained from G by adding one simplicial degree-2 vertex."""
    n = G.number_of_nodes()
    new_v = n
    for a, b in G.edges():
        H = G.copy()
        H.add_node(new_v)
        H.add_edge(new_v, a)
        H.add_edge(new_v, b)
        yield H


def enumerate_two_trees(max_n: int):
    """Return {n: [graph6, ...]} for connected 2-trees of order 3..max_n."""
    K3 = nx.complete_graph(3)
    by_order: dict[int, list[nx.Graph]] = {3: [K3]}
    by_order_hashes: dict[int, set[str]] = {3: {nx.weisfeiler_lehman_graph_hash(K3)}}
    for n in range(4, max_n + 1):
        seen_hashes: set[str] = set()
        seen_graphs: list[nx.Graph] = []
        for parent in by_order[n - 1]:
            for child in two_tree_children(parent):
                h = nx.weisfeiler_lehman_graph_hash(child, iterations=4)
                if h in seen_hashes:
                    # Exact isomorphism check (cheap at small n)
                    iso = False
                    for g in seen_graphs:
                        if nx.weisfeiler_lehman_graph_hash(g, iterations=4) == h:
                            if nx.is_isomorphic(g, child):
                                iso = True
                                break
                    if iso:
                        continue
                seen_hashes.add(h)
                seen_graphs.append(child)
        by_order[n] = seen_graphs
        by_order_hashes[n] = seen_hashes
        print(f"  n={n}: {len(seen_graphs)} 2-trees", file=sys.stderr)
    return {n: [graph6(g) for g in gs] for n, gs in by_order.items()}


def main():
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    out = enumerate_two_trees(max_n)
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"two_trees_n{max_n}.json"
    path.write_text(json.dumps(out))
    print(f"wrote {path}")
    for n, codes in out.items():
        print(f"n={n}: {len(codes)} 2-trees")


if __name__ == "__main__":
    main()
