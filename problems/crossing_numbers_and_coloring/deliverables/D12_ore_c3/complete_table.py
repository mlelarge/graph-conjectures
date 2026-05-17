"""
Complete the lower_bounds table for all 12 Ore graphs without the slow
skewness-greedy heuristic (skewness is informational only; the
certified bounds are identical across the family since all 12 graphs
have the same (n, m, omega)).
"""

from pathlib import Path

import networkx as nx

from lower_bounds import (
    Z, Z26, PROVEN_CR_K, cr_K_subgraph_bound,
    euler_bound, crossing_lemma_pt, crossing_lemma_bk,
    load_graphs,
)


def main():
    print(f"Z(26) = {Z26}")
    print()

    graphs = load_graphs()
    print(f"Loaded {len(graphs)} graphs.")
    print()

    header = (
        f"{'idx':>3}  {'|V|':>4}  {'|E|':>5}  {'omega':>5}  "
        f"{'Euler':>10}  {'PT(1/64)':>10}  {'BK(1/27.48)':>14}  "
        f"{'cr(K_omega)':>12}  {'best':>10}  {'>= Z(26)?':>10}"
    )
    print(header)
    print("-" * len(header))

    n_cert = 0
    for i, G in enumerate(graphs, start=1):
        n = G.number_of_nodes()
        m = G.number_of_edges()
        omega = 25  # known from D4: all 12 Ore graphs contain K_25
        e_b = euler_bound(G)
        pt = crossing_lemma_pt(G) or 0
        bk = crossing_lemma_bk(G) or 0
        clq = cr_K_subgraph_bound(omega)
        best = max(e_b, pt, bk, clq)
        cert = "yes" if best >= Z26 else "NO"
        if cert == "yes":
            n_cert += 1
        print(
            f"{i:>3}  {n:>4}  {m:>5}  {omega:>5}  "
            f"{e_b:>10}  {pt:>10.2f}  {bk:>14.2f}  "
            f"{clq:>12}  {best:>10.2f}  {cert:>10}"
        )

    print()
    print(f"Certified cr(G) >= Z(26) = {Z26}: {n_cert} / {len(graphs)}.")
    if n_cert < len(graphs):
        best_overall = max(crossing_lemma_bk(g) or 0 for g in graphs)
        print(f"Best certified bound across the family: {best_overall:.2f}")
        print(f"Gap to Z(26):                            {Z26 - best_overall:.2f}")
        print(f"Ratio (best / Z(26)):                    {best_overall / Z26:.4f}")


if __name__ == "__main__":
    main()
