"""Computer-checked Sub-lemma 1' on small 1-port subcubic graphs.

Sub-lemma 1' (from docs/minimal_counterexample.md §2.1):

  Every connected subcubic graph H with exactly one port (a vertex of
  degree 2, all other vertices of degree 3) realises at least one of
  the two bridge-admissible port states {T_T, T_TM} at the port.

This script enumerates all such graphs up to a fixed order n (n must be
odd; see parity remark) and verifies Sub-lemma 1' on each.

For n <= 7 the enumeration is by brute-force search over edge subsets, then by
canonical-form deduplication via networkx's Weisfeiler-Lehman hash. For larger
n, the script uses nauty `geng` when available, so the edge-subset explosion is
avoided.

For n=7 this script does ~350k edge subsets and finishes in seconds. For
n=9 the edge subset count is ~3e9, so nauty is the intended path.
"""

from __future__ import annotations

import argparse
import itertools
import shutil
import subprocess
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from decomposition import verify_bridge_side_realisable


def one_port_subcubic_graphs(n: int) -> list[nx.Graph]:
    """All connected simple graphs on n vertices with exactly one vertex
    of degree 2 and the rest of degree 3. Canonical-deduped via WL hash.

    For a graph with one degree-2 vertex and (n-1) degree-3 vertices,
    sum of degrees = 3n - 1. Edges = (3n-1)/2. Hence n must be odd.
    """
    if n % 2 == 0:
        return []
    n_edges = (3 * n - 1) // 2
    vertices = list(range(n))
    all_edges = list(itertools.combinations(vertices, 2))
    seen: dict[str, nx.Graph] = {}
    for edge_set in itertools.combinations(all_edges, n_edges):
        G = nx.Graph()
        G.add_nodes_from(vertices)
        G.add_edges_from(edge_set)
        degs = sorted(d for _, d in G.degree())
        if degs != [2] + [3] * (n - 1):
            continue
        if not nx.is_connected(G):
            continue
        # Canonical key (WL hash discriminates up to isomorphism for small n).
        key = nx.weisfeiler_lehman_graph_hash(G)
        if key in seen:
            continue
        seen[key] = G
    return list(seen.values())


def one_port_subcubic_graphs_nauty(n: int) -> list[nx.Graph]:
    """Enumerate via nauty geng, which emits one graph per isomorphism class.

    We ask for connected simple graphs with minimum degree 2, maximum degree 3,
    and exactly (3n-1)/2 edges, then filter to the desired degree sequence.
    """
    if n % 2 == 0:
        return []
    if shutil.which("geng") is None:
        raise RuntimeError("geng not found on PATH")

    n_edges = (3 * n - 1) // 2
    proc = subprocess.run(
        ["geng", "-q", "-c", "-d2", "-D3", str(n), f"{n_edges}:{n_edges}"],
        check=True,
        capture_output=True,
    )
    graphs: list[nx.Graph] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        G = nx.from_graph6_bytes(line)
        degs = sorted(d for _, d in G.degree())
        if degs == [2] + [3] * (n - 1):
            graphs.append(G)
    return graphs


def check_sublemma_1prime(n_max: int = 7) -> dict[int, dict]:
    """Run Sub-lemma 1' over all 1-port subcubic graphs on n <= n_max vertices.

    Returns dict[n] = {"count": int, "source": str, "all_realisable": bool,
                       "counterexamples": list[graph6]}.
    """
    out: dict[int, dict] = {}
    for n in range(3, n_max + 1):
        if n % 2 == 0:
            continue
        if n <= 7 or shutil.which("geng") is None:
            graphs = one_port_subcubic_graphs(n)
            source = "bruteforce"
        else:
            graphs = one_port_subcubic_graphs_nauty(n)
            source = "nauty"
        counterex: list[str] = []
        for G in graphs:
            ports = [v for v, d in G.degree() if d == 2]
            assert len(ports) == 1
            port = ports[0]
            if not verify_bridge_side_realisable(G, port):
                counterex.append(nx.to_graph6_bytes(G, header=False).decode().strip())
        out[n] = {
            "count": len(graphs),
            "source": source,
            "all_realisable": len(counterex) == 0,
            "counterexamples": counterex,
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-max", type=int, default=7, help="largest n to test")
    args = parser.parse_args()

    print(f"Sub-lemma 1' check: 1-port subcubic graphs on n <= {args.n_max} vertices")
    print()
    results = check_sublemma_1prime(args.n_max)
    all_ok = True
    for n in sorted(results):
        r = results[n]
        flag = "OK " if r["all_realisable"] else "FAIL"
        print(
            f"  n={n}: {r['count']} graphs ({r['source']}), "
            f"all bridge-realisable? {flag}"
        )
        if not r["all_realisable"]:
            all_ok = False
            for g6 in r["counterexamples"]:
                print(f"    counterexample: {g6}")

    print()
    if all_ok:
        print("Sub-lemma 1' holds on every enumerated 1-port subcubic graph.")
        return 0
    print("Sub-lemma 1' has counterexamples in the enumerated range.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
