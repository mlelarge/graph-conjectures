"""Compute s^+, s^-, n^+, n^- of a graph via eigvalsh."""
from __future__ import annotations

import numpy as np
import networkx as nx


TOL = 1e-9


def spectrum(G: nx.Graph) -> np.ndarray:
    if G.number_of_nodes() == 0:
        return np.array([], dtype=float)
    A = nx.to_numpy_array(G, dtype=float)
    return np.linalg.eigvalsh(A)


def s_plus_minus(G: nx.Graph, tol: float = TOL) -> dict:
    eigs = spectrum(G)
    pos = eigs[eigs > tol]
    neg = eigs[eigs < -tol]
    return {
        "n": G.number_of_nodes(),
        "m": G.number_of_edges(),
        "s_plus": float(np.sum(pos ** 2)),
        "s_minus": float(np.sum(neg ** 2)),
        "n_plus": int(pos.size),
        "n_minus": int(neg.size),
        "eigs": eigs.tolist(),
    }


if __name__ == "__main__":
    for name, G in [
        ("P_4", nx.path_graph(4)),
        ("C_5", nx.cycle_graph(5)),
        ("K_5", nx.complete_graph(5)),
        ("K_{1,4}", nx.star_graph(4)),
    ]:
        r = s_plus_minus(G)
        print(f"{name}: n={r['n']} m={r['m']} s+={r['s_plus']:.6f} "
              f"s-={r['s_minus']:.6f} n+={r['n_plus']} n-={r['n_minus']}")
