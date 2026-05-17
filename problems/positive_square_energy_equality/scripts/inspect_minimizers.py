"""Inspect the structure of the 2-trees minimizing delta- and delta+."""
from __future__ import annotations
import json, sys
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]


def show(g6):
    G = nx.from_graph6_bytes(g6.encode())
    n = G.number_of_nodes()
    degs = sorted(dict(G.degree()).values(), reverse=True)
    # detect special families
    diam = nx.diameter(G)
    return {
        "n": n,
        "edges": sorted([tuple(sorted(e)) for e in G.edges()]),
        "deg_seq": degs,
        "diameter": diam,
    }


def main():
    for n in [4, 5, 6, 7, 8, 9, 10]:
        path = ROOT / "data" / f"two_tree_ear_gains_n{n}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        # min delta+ and delta- across (G, v) pairs
        flat = []
        for entry in data:
            for ear in entry["ears"]:
                flat.append({"g6": entry["g6"], **ear})
        if not flat:
            continue
        mp = min(flat, key=lambda e: e["delta_plus"])
        mm = min(flat, key=lambda e: e["delta_minus"])
        print(f"\n=== n={n} ===")
        print(f"min delta+ = {mp['delta_plus']:.8f}, g6={mp['g6']}, v={mp['v']}")
        print(f"  graph: {show(mp['g6'])}")
        print(f"min delta- = {mm['delta_minus']:.8f}, g6={mm['g6']}, v={mm['v']}")
        print(f"  graph: {show(mm['g6'])}")


if __name__ == "__main__":
    main()
