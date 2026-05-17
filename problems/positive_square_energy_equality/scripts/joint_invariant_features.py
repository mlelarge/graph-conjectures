"""Joint-invariant feature extractor for plan v10, Concrete next action #1.

For a 2-tree G with a simplicial degree-2 ear v with neighbors {a, b} and
H = G - v, this module computes the spectral feature vector used in the
v10 joint-invariant ansatz search:

    W_minus, W_zero, W_plus     (with ||w||^2 = 2 normalization)
    c1_sq, c_last_sq            (Perron and least-eigenvector c-weights)
    M1_minus, M2_minus, M3_minus
    M1_plus,  M2_plus,  M3_plus
    mu_min, mu_max
    delta_minus, delta_plus     (ground truth via eigvalsh)

The vertex v* maximizing deg_{G-v*}(a) + deg_{G-v*}(b) is identified;
ties are emitted as multiple records.

Used by the v10 joint-invariant scan (see plan_v10.md Concrete next action #1).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spectrum_check import s_plus_minus  # noqa: E402

TOL = 1e-9


def to_graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def from_graph6(code: str) -> nx.Graph:
    return nx.from_graph6_bytes(code.encode())


def simplicial_deg2_ears(G: nx.Graph) -> Iterable[tuple[int, int, int]]:
    """Yield (v, a, b) for each simplicial degree-2 vertex v of G such that
    H = G - v has at least 3 vertices."""
    for v in G.nodes():
        if G.degree(v) != 2:
            continue
        nbrs = list(G.neighbors(v))
        if len(nbrs) != 2:
            continue
        a, b = nbrs
        if not G.has_edge(a, b):
            continue
        if G.number_of_nodes() - 1 < 3:
            continue
        yield v, a, b


def _spectral_features(H: nx.Graph, a: int, b: int) -> dict:
    """Compute the spectral feature vector for the pair (a, b) in H.

    H has n_H = G.n - 1 vertices. The order of nodes from H matters: we
    use a list ordering and the indices of a, b in that ordering.
    """
    nodes = sorted(H.nodes())
    idx = {u: i for i, u in enumerate(nodes)}
    n_H = len(nodes)
    A = nx.to_numpy_array(H, nodelist=nodes, dtype=float)
    mu, U = np.linalg.eigh(A)  # ascending order: mu[0] <= ... <= mu[-1]
    # eigenvalue ordering: numpy eigh returns ascending; the conventional
    # convention in our formula has mu_1 >= mu_2 >= ... so reverse.
    mu = mu[::-1]
    U = U[:, ::-1]  # columns: u_1, u_2, ..., u_{n-1}
    ia, ib = idx[a], idx[b]
    # c_i = u_i(a) + u_i(b)
    c = U[ia, :] + U[ib, :]
    c_sq = c * c
    # Partition by sign of mu_i (negative / zero / positive)
    neg_mask = mu < -TOL
    pos_mask = mu > TOL
    zero_mask = ~(neg_mask | pos_mask)
    w_minus = float(np.sum(c_sq[neg_mask]))
    w_zero = float(np.sum(c_sq[zero_mask]))
    w_plus = float(np.sum(c_sq[pos_mask]))
    # Moments
    def moments(mask):
        cc = c_sq[mask]
        mm = mu[mask]
        m1 = float(np.sum(cc * mm))
        m2 = float(np.sum(cc * mm * mm))
        m3 = float(np.sum(cc * mm * mm * mm))
        return m1, m2, m3
    m1n, m2n, m3n = moments(neg_mask)
    m1p, m2p, m3p = moments(pos_mask)
    c1_sq = float(c_sq[0])              # largest eigenvalue (Perron)
    c_last_sq = float(c_sq[-1])         # smallest eigenvalue
    mu_max = float(mu[0])
    mu_min = float(mu[-1])
    return {
        "W_minus": w_minus,
        "W_zero": w_zero,
        "W_plus": w_plus,
        "c1_sq": c1_sq,
        "c_last_sq": c_last_sq,
        "M1_minus": m1n,
        "M2_minus": m2n,
        "M3_minus": m3n,
        "M1_plus": m1p,
        "M2_plus": m2p,
        "M3_plus": m3p,
        "mu_min": mu_min,
        "mu_max": mu_max,
        "n_H": n_H,
    }


def ear_records(G: nx.Graph, full_spec: dict | None = None) -> list[dict]:
    """For every simplicial deg-2 ear v of G, compute the feature record.

    Marks `is_max_degsum=True` on records whose deg(a)+deg(b) in H equals
    the max over all simplicial ears. `tied_count` records how many ears
    share the max deg-sum.
    """
    if full_spec is None:
        full_spec = s_plus_minus(G)
    s_plus_G = full_spec["s_plus"]
    s_minus_G = full_spec["s_minus"]
    g6 = to_graph6(G)
    out = []
    ears = list(simplicial_deg2_ears(G))
    if not ears:
        return out
    # Compute deg-sum in H for each ear; H = G - v.
    deg_sums = []
    for v, a, b in ears:
        # deg of a in G-v = deg_G(a) - 1 (since v is adj to a)
        deg_sums.append(G.degree(a) - 1 + G.degree(b) - 1)
    max_ds = max(deg_sums)
    tied_count = sum(1 for d in deg_sums if d == max_ds)
    for (v, a, b), ds in zip(ears, deg_sums):
        H = G.copy()
        H.remove_node(v)
        sub = s_plus_minus(H)
        delta_plus = float(s_plus_G - sub["s_plus"])
        delta_minus = float(s_minus_G - sub["s_minus"])
        feats = _spectral_features(H, a, b)
        record = {
            "graph6": g6,
            "n": G.number_of_nodes(),
            "v": int(v),
            "a": int(a),
            "b": int(b),
            "deg_sum": int(ds),
            "is_max_degsum": (ds == max_ds),
            "tied_count": int(tied_count),
            "delta_minus": delta_minus,
            "delta_plus": delta_plus,
        }
        record.update(feats)
        out.append(record)
    return out


if __name__ == "__main__":
    # Quick sanity check
    G = nx.complete_graph(3)
    G.add_node(3); G.add_edge(0, 3); G.add_edge(1, 3)  # K_3 + ear -> n=4
    recs = ear_records(G)
    for r in recs:
        wsum = r["W_minus"] + r["W_zero"] + r["W_plus"]
        print(f"n={r['n']} v={r['v']} W- = {r['W_minus']:.4f} W0 = {r['W_zero']:.4f} "
              f"W+ = {r['W_plus']:.4f}  total = {wsum:.6f}  delta- = {r['delta_minus']:.4f}")
