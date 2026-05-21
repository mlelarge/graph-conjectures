"""Polynomial-time MFAS decider via the structural theorem +
2-SAT (see docs/lemmas.md, Theorem 2).

The decoupling lemmas (Lemmas 3 and 4) imply:
  - cyclic modules (cyclic 3-cycles with all 3 arcs no-shortcut) are
    pairwise vertex-disjoint and share no arc with any other cyclic
    3-cycle;
  - therefore any one arc per module can be added to M without
    consequence;
  - the residual constraint is 2-SAT: clauses come from cyclic
    3-cycles with 1 or 2 no-shortcut arcs and from the matching
    constraint (any two arcs sharing a vertex cannot both be in M).
"""
from __future__ import annotations
from typing import Sequence

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structural import cyclic_3_cycles, no_shortcut_arcs  # noqa: E402


# ------------------------------ 2-SAT solver ------------------------------

class TwoSAT:
    """A bare-bones 2-SAT solver via implication graph + SCCs."""

    def __init__(self, nvars: int) -> None:
        self.n = nvars
        self.adj: list[list[int]] = [[] for _ in range(2 * nvars)]

    @staticmethod
    def lit(var: int, sign: bool) -> int:
        # var in [0..n), sign True = positive, False = negative.
        return 2 * var + (0 if sign else 1)

    @staticmethod
    def neg(lit_idx: int) -> int:
        return lit_idx ^ 1

    def add_clause(self, l1: int, l2: int) -> None:
        # (l1 OR l2): equivalent to (~l1 -> l2) AND (~l2 -> l1).
        self.adj[self.neg(l1)].append(l2)
        self.adj[self.neg(l2)].append(l1)

    def add_force(self, lit_idx: int) -> None:
        # force lit_idx to be True: ~lit -> lit, i.e., adding clause
        # (lit OR lit) collapses to the implication ~lit -> lit.
        self.add_clause(lit_idx, lit_idx)

    def solve(self) -> dict[int, bool] | None:
        # Kosaraju SCC.
        n2 = 2 * self.n
        visited = [False] * n2
        order: list[int] = []

        def dfs1(u: int) -> None:
            stack = [(u, iter(self.adj[u]))]
            visited[u] = True
            while stack:
                _, it = stack[-1]
                for v in it:
                    if not visited[v]:
                        visited[v] = True
                        stack.append((v, iter(self.adj[v])))
                        break
                else:
                    order.append(stack[-1][0])
                    stack.pop()

        for v in range(n2):
            if not visited[v]:
                dfs1(v)

        radj: list[list[int]] = [[] for _ in range(n2)]
        for u in range(n2):
            for v in self.adj[u]:
                radj[v].append(u)

        comp = [-1] * n2
        c = 0
        for v in reversed(order):
            if comp[v] != -1:
                continue
            stack = [v]
            comp[v] = c
            while stack:
                u = stack.pop()
                for w in radj[u]:
                    if comp[w] == -1:
                        comp[w] = c
                        stack.append(w)
            c += 1

        assignment: dict[int, bool] = {}
        for v in range(self.n):
            if comp[2 * v] == comp[2 * v + 1]:
                return None  # unsat: var and its negation in same SCC
            # 2-SAT convention: variable is True iff its positive literal's
            # SCC index is greater than its negative literal's SCC.
            assignment[v] = comp[2 * v] > comp[2 * v + 1]
        return assignment


# --------------------------- MFAS algorithm ---------------------------

def decide_mfas_poly(T: Sequence[Sequence[int]]) -> dict:
    """Polynomial-time MFAS decider.

    Returns {found: bool, M: list[(u,v)] | None, reason: str|None}.
    """
    cycles = cyclic_3_cycles(T)
    ok = no_shortcut_arcs(T)

    if not cycles:
        return {"found": True, "M": [], "reason": "T is transitive"}

    # Partition cycles by # of no-shortcut arcs.
    cycles_partition: dict[int, list[frozenset]] = {0: [], 1: [], 2: [], 3: []}
    for cyc in cycles:
        cnt = sum(1 for a in cyc if a in ok)
        cycles_partition[cnt].append(cyc)

    if cycles_partition[0]:
        return {
            "found": False, "M": None,
            "reason": f"cyclic 3-cycle with no no-shortcut arcs: "
                      f"{list(cycles_partition[0][0])}",
        }

    # By Lemma 4, modules are disjoint from non-module arcs. Pick one
    # arc per module.
    M_forced: list[tuple[int, int]] = []
    module_arc_set: set[tuple[int, int]] = set()
    module_vertex_set: set[int] = set()
    for cyc in cycles_partition[3]:
        # Pick the lexicographically smallest arc.
        chosen = sorted(cyc)[0]
        M_forced.append(chosen)
        for a in cyc:
            module_arc_set.add(a)
        for (u, v) in cyc:
            module_vertex_set.add(u); module_vertex_set.add(v)

    # Non-module arcs: candidate set for 2-SAT.
    non_module_arcs = [a for a in ok if a not in module_arc_set]
    arc_index = {a: i for i, a in enumerate(non_module_arcs)}
    sat = TwoSAT(len(non_module_arcs))
    pos = TwoSAT.lit

    # Forced arcs from 1-arc-no-shortcut cycles.
    forced_vars = set()
    for cyc in cycles_partition[1]:
        e = next(a for a in cyc if a in ok)
        if e in module_arc_set:
            # By Lemma 4 this can't happen, but guard anyway.
            continue
        i = arc_index[e]
        sat.add_force(pos(i, True))
        forced_vars.add(i)

    # 2-arc cycles: exactly one of two.
    for cyc in cycles_partition[2]:
        es = [a for a in cyc if a in ok]
        assert len(es) == 2, f"expected 2 no-shortcut arcs in {cyc}, got {es}"
        i1, i2 = arc_index[es[0]], arc_index[es[1]]
        # x_i1 XOR x_i2 = 1:
        #   (x_i1 OR x_i2) AND (~x_i1 OR ~x_i2)
        sat.add_clause(pos(i1, True), pos(i2, True))
        sat.add_clause(pos(i1, False), pos(i2, False))

    # Matching constraint: for each pair of non-module arcs sharing a
    # vertex, not both selected.
    arcs_by_vertex: dict[int, list[int]] = {}
    for idx, (u, v) in enumerate(non_module_arcs):
        arcs_by_vertex.setdefault(u, []).append(idx)
        arcs_by_vertex.setdefault(v, []).append(idx)
    seen_pairs = set()
    for v, idxs in arcs_by_vertex.items():
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                a, b = sorted((idxs[i], idxs[j]))
                if (a, b) in seen_pairs:
                    continue
                seen_pairs.add((a, b))
                sat.add_clause(pos(a, False), pos(b, False))

    sol = sat.solve()
    if sol is None:
        return {"found": False, "M": None,
                "reason": "2-SAT residual unsatisfiable"}

    # Build M from solution + forced module arcs.
    M = list(M_forced)
    for arc, i in arc_index.items():
        if sol[i]:
            M.append(arc)
    return {"found": True, "M": M, "reason": None}


# --------------------------- Cross-check harness ---------------------------

if __name__ == "__main__":
    import argparse, random, time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from brute import decide
    from random_check import random_tournament
    from sweep import all_tournaments, canonical_key

    p = argparse.ArgumentParser()
    p.add_argument("--nmax", type=int, default=6)
    p.add_argument("--rand-n", type=int, default=8)
    p.add_argument("--rand-samples", type=int, default=300)
    args = p.parse_args()

    disagreements = 0

    # Exhaustive
    for n in range(3, args.nmax + 1):
        seen = set()
        total = 0
        t0 = time.time()
        for T in all_tournaments(n):
            key = canonical_key(T)
            if key in seen:
                continue
            seen.add(key)
            total += 1
            poly = decide_mfas_poly(T)
            br = decide(T, "matching")
            if poly["found"] != br["found"]:
                print(f"DISAGREE n={n} T={T} poly={poly['found']} brute={br['found']}")
                disagreements += 1
        print(f"n={n}: poly vs brute agreement on {total} tournaments "
              f"({time.time() - t0:.2f}s)")

    # Random
    rng = random.Random(123)
    t0 = time.time()
    for _ in range(args.rand_samples):
        T = random_tournament(args.rand_n, rng)
        poly = decide_mfas_poly(T)
        br = decide(T, "matching")
        if poly["found"] != br["found"]:
            print(f"DISAGREE n={args.rand_n} T={T} poly={poly['found']} brute={br['found']}")
            disagreements += 1
    print(f"random n={args.rand_n}, {args.rand_samples} samples "
          f"({time.time() - t0:.2f}s)")

    print(f"\nTOTAL DISAGREEMENTS: {disagreements}")
    sys.exit(0 if disagreements == 0 else 1)
