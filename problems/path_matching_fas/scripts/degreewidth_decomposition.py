"""Degreewidth decomposition of tournament Path-FAS (a new direction, D92).

Define Δ*(T) = degreewidth = min over vertex orderings of the maximum
back-degree (number of back-arcs incident to a vertex).

THEOREM (immediate).  Path-FAS(T) = YES  ⟹  Δ*(T) ≤ 2.
  A linear-forest back-arc graph has max undirected degree ≤ 2, so the
  witnessing order already attains max-back-degree ≤ 2.  Contrapositive:
  Δ*(T) ≥ 3  ⟹  NO — a global NO-certificate independent of acyclicity.

DECOMPOSITION.
  Path-FAS(T) = [ Δ*(T) ≤ 2 ]  ∧  [ some max-back-degree-≤2 order has an
  ACYCLIC back-arc graph ].
  * Δ*(T) ≥ 3   : degree-obstructed NO (the majority).
  * Δ*(T) = 2, NO : the ACYCLICITY-CORE — a degree-2 order exists but every
    one has a cyclic back-arc graph.  The genuine hard residual.

Open sub-questions:
  (Q1) Is "Δ*(T) ≤ 2" decidable in polynomial time? (degreewidth ≤ 2
       recognition; Δ* = the studied tournament parameter "degreewidth".)
  (Q2) Among Δ*(T) ≤ 2 tournaments, is "∃ acyclic degree-2 order"
       polynomial?
"""
from __future__ import annotations

from itertools import permutations


def max_backdeg(T, order) -> int:
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    deg = [0] * n
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[u] > pos[v]:
                deg[u] += 1
                deg[v] += 1
    return max(deg) if n else 0


def degreewidth(T, cap: int | None = None) -> int:
    """Δ*(T) by brute force over orderings, early-exit once an order with
    max-back-degree ≤ `cap` is found (default: exact).

    NOTE: prefer scripts/degreewidth_exact.degreewidth, an O(2^n·n)
    Held-Karp DP that is exact and far faster.  This permutation scan is
    kept only as the small-n cross-check oracle.
    """
    n = len(T)
    best = n
    for p in permutations(range(n)):
        md = max_backdeg(T, p)
        if md < best:
            best = md
            if cap is not None and best <= cap:
                return best
            if best == 0:  # global minimum; cannot improve (was buggy `<= 1`)
                return best
    return best


def is_degreewidth_le2(T) -> bool:
    """True iff Δ*(T) ≤ 2 (degree-feasible)."""
    from degreewidth_exact import degreewidth_le
    return degreewidth_le(T, 2)


def classify(T) -> str:
    """'dw_ge3' (degree-obstructed NO), 'dw2_core' (acyclicity-core NO),
    or 'yes'."""
    from nonsweep_path_fas import decide_linear_forest_fas_bruteforce
    if not is_degreewidth_le2(T):
        return "dw_ge3"
    return "yes" if decide_linear_forest_fas_bruteforce(T) else "dw2_core"
