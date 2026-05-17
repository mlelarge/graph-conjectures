"""
D12 -- C3 attempt for the 12 (26, 51) Ore-corner graphs.

Goal: certify cr(G) >= Z(26) = 5148 for every G in the family of 12
26-Ore compositions K_26 * K_26 (D4 output at
../D4_ore_26_51/ore_26_51.g6).

This script computes the lower bounds on cr(G) that are accessible
without an exact MILP / SAT crossing-number solver. The classical
chain is:

 (LB1)  Euler / edge bound:        cr(G) >= m - 3n + 6
 (LB2)  Crossing Lemma (BK):       cr(G) >= m^3 / (27.48 * n^2),  if m >= 6.77 n
        (also reported with Ackerman 1/29 and  Pach-Toth 1/64)
 (LB3)  Subgraph monotonicity:     cr(G) >= cr(H)  for every subgraph H of G
        with cr(H) known (e.g. K_t for small t).
 (LB4)  Skewness-based (planar deletion): cr(G) >= |E(G)| - sk(G), where
        sk(G) is the smallest number of edges whose deletion makes G planar.
        We do not have sk(G); we estimate it from below by a greedy
        planarisation, giving an UPPER bound on sk(G), hence a LOWER bound
        on |E(G)| - sk(G).

Output: a table per graph with each bound, and a verdict
        bound_max >= Z(26)?  (yes => certified safe; no => insufficient.)

Caveats recorded in REPORT.md.
"""

import math
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
G6 = HERE.parent / "D4_ore_26_51" / "ore_26_51.g6"

Z26 = 5148  # Zarankiewicz value (conjectured cr(K_26))


def euler_bound(G):
    """cr(G) >= m - 3n + 6 (simple graph, m >= 3n - 6 => non-planar)."""
    n, m = G.number_of_nodes(), G.number_of_edges()
    return m - 3 * n + 6


def crossing_lemma(G, c_inv, threshold_factor):
    """Crossing Lemma cr(G) >= m^3 / (c_inv * n^2) when m >= threshold_factor * n."""
    n, m = G.number_of_nodes(), G.number_of_edges()
    if m < threshold_factor * n:
        return None
    return m ** 3 / (c_inv * n ** 2)


def crossing_lemma_pt(G):
    """Pach-Toth 1997: cr(G) >= m^3 / (64 n^2) for m >= 4n."""
    return crossing_lemma(G, 64.0, 4.0)


def crossing_lemma_ackerman(G):
    """Ackerman 2019 (arXiv:1509.01932): cr(G) >= m^3 / (29 n^2) for m >= 6.95n."""
    return crossing_lemma(G, 29.0, 6.95)


def crossing_lemma_bk(G):
    """Buengener-Kaufmann 2024 (arXiv:2409.01733): cr(G) >= m^3 / (27.48 n^2) for m >= 6.77n.
    We follow the Cranston-cited variant: c >= 1/27.48 when m >= 6.95n (the safe form)."""
    return crossing_lemma(G, 27.48, 6.95)


def skewness_greedy_planarisation(G, max_iters=2000):
    """Greedy planarisation lower bound on cr(G).

    This is NOT a true lower bound on the skewness sk(G): every deletion
    removes >=1 Kuratowski subgraph but a single edge can lie in many of
    them, so the greedy count is at most sk(G) and only a lower bound on
    sk(G) up to that overcounting. (cr(G) >= sk(G) is the standard
    relation we eventually want.)

    For our purposes we report it as a heuristic informational quantity,
    not as a certified lower bound on cr(G).

    Capped at `max_iters` iterations.
    """
    H = G.copy()
    deletions = 0
    while deletions < max_iters:
        try:
            is_planar, kur = nx.check_planarity(H, counterexample=True)
        except Exception:
            return None
        if is_planar:
            break
        edges = list(kur.edges())
        if not edges:
            return None
        edges.sort(key=lambda uv: -(H.degree(uv[0]) + H.degree(uv[1])))
        H.remove_edge(*edges[0])
        deletions += 1
    return deletions


PROVEN_CR_K = {
    # cr(K_t) for t <= 12, proven values (Pan-Richter 2007 for t=11,12;
    # earlier for smaller t).
    1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 3, 7: 9, 8: 18, 9: 36, 10: 60,
    11: 100, 12: 150,
}


def cr_K_subgraph_bound(omega):
    """Largest known cr(K_t) value with K_t a subgraph of clique-size omega.
       For omega in {13..26}, cr(K_omega) is unknown; conservatively use
       cr(K_12) = 150 as the certified bound."""
    return PROVEN_CR_K.get(min(omega, 12), 0)


def Z(t):
    """Zarankiewicz formula (conjectured cr(K_t)).
       Z(t) = floor(t/2) * floor((t-1)/2) * floor((t-2)/2) * floor((t-3)/2) / 4."""
    return (t // 2) * ((t - 1) // 2) * ((t - 2) // 2) * ((t - 3) // 2) // 4


def load_graphs():
    """Load the 12 graphs from D4's .g6 file."""
    raw = G6.read_text().strip().split("\n")
    return [nx.from_graph6_bytes(line.encode()) for line in raw]


def main():
    print(f"Z(26) = {Z26}")
    print(f"Sanity:  Z formula on t=26 = {Z(26)}")
    assert Z(26) == Z26
    print()

    graphs = load_graphs()
    print(f"Loaded {len(graphs)} graphs from {G6.name}.")
    print()

    header = (
        f"{'idx':>3}  {'|V|':>4}  {'|E|':>5}  {'omega':>5}  "
        f"{'Euler':>10}  {'PT(1/64)':>10}  {'BK(1/27.48)':>14}  "
        f"{'cr(K_omega)':>12}  {'skew_greedy':>12}  {'>= Z(26)?':>10}"
    )
    print(header)
    print("-" * len(header))

    rows = []
    for i, G in enumerate(graphs, start=1):
        n = G.number_of_nodes()
        m = G.number_of_edges()
        # All 12 Ore graphs contain K_25 (the first K_26 minus the deleted
        # edge xy is K_26 minus one edge, which contains K_25). We hardcode
        # omega >= 25; computing the exact clique number via find_cliques
        # on these graphs is exponential and unnecessary for our bound.
        omega = 25
        e_bound = euler_bound(G)
        pt_bound = crossing_lemma_pt(G) or float("nan")
        bk_bound = crossing_lemma_bk(G) or float("nan")
        clique_bound = cr_K_subgraph_bound(omega)
        skew_bound = skewness_greedy_planarisation(G)

        # Certified lower bounds: Euler, the Crossing Lemma variants, and
        # the clique-subgraph bound. skew_bound is informational only (it
        # over-counts; see docstring).
        best = max(e_bound, pt_bound, bk_bound, clique_bound)
        certified = "yes" if best >= Z26 else "NO"
        print(
            f"{i:>3}  {n:>4}  {m:>5}  {omega:>5}  "
            f"{e_bound:>10}  {pt_bound:>10.2f}  {bk_bound:>14.2f}  "
            f"{clique_bound:>12}  {skew_bound:>12}  {certified:>10}",
            flush=True,
        )
        rows.append(dict(idx=i, n=n, m=m, omega=omega,
                          euler=e_bound, pt=pt_bound, bk=bk_bound,
                          clique=clique_bound, skew=skew_bound, best=best,
                          certified=(best >= Z26)))

    print()
    n_certified = sum(1 for r in rows if r["certified"])
    print(f"Certified cr(G) >= Z(26) = {Z26}: {n_certified} / {len(rows)}")

    if n_certified < len(rows):
        gap = Z26 - max(r["best"] for r in rows)
        print(
            f"Best available lower bound across the family: "
            f"{max(r['best'] for r in rows):.2f}; gap to Z(26): {gap:.2f}"
        )


if __name__ == "__main__":
    main()
