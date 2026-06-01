"""Non-sweep formulations for tournament Path-FAS (Aboulker-Aubian-Lopes
Problem 4.4, arXiv:2402.10782).

Path-FAS reformulated (see docs/path_fas.md):

    T has a path-FAS  <=>  T has a feedback arc set S that is a linear
    forest (underlying undirected graph has max-degree <= 2 and is acyclic).

The forward dynamic-programming route is provably closed (D66 + D70).  This
module collects the *non-sweep* attacks investigated in
docs/nonsweep_path_fas.md:

  1. matroid / degree-constrained-FAS reformulation (with non-matroid
     witness);
  2. the FAS LP with triangle + degree-<=2 constraints, and its
     integrality experiments (ILP via scipy.optimize.milp, LP relaxation
     via the same with continuous bounds);
  3. a coNP / certificate analysis for NO instances;
  4. a 2-SAT realizability attempt on the score-window structure.

Ground truth is `scripts/path_fas.py::decide_path_fas_bruteforce`.

All experiments use only stdlib + numpy + scipy (HiGHS through milp/linprog)
+ networkx; no external ILP solver.
"""
from __future__ import annotations

import os
import sys
from collections import deque
from itertools import combinations, permutations
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import LinearConstraint, milp, Bounds
from scipy.sparse import lil_matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import back_arcs  # noqa: E402


Arc = tuple[int, int]


# --------------------------------------------------------------------------
# basic tournament utilities
# --------------------------------------------------------------------------
def arcs_of(T: Sequence[Sequence[int]]) -> list[Arc]:
    n = len(T)
    return [(u, v) for u in range(n) for v in range(n) if T[u][v]]


def is_acyclic(n: int, arcs: Iterable[Arc]) -> bool:
    out: list[list[int]] = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in arcs:
        out[u].append(v)
        indeg[v] += 1
    q = deque([v for v in range(n) if indeg[v] == 0])
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in out[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == n


def underlying_is_linear_forest(arcs: Iterable[Arc]) -> bool:
    """Underlying undirected graph has max-degree <= 2 and is acyclic."""
    adj: dict[int, set[int]] = {}
    edges: set[frozenset[int]] = set()
    for u, v in arcs:
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
        edges.add(frozenset((u, v)))
    if any(len(nb) > 2 for nb in adj.values()):
        return False
    seen: set[int] = set()
    for s in adj:
        if s in seen:
            continue
        comp: list[int] = []
        dq = deque([s])
        seen.add(s)
        while dq:
            x = dq.popleft()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    dq.append(y)
        cv = set(comp)
        ce = sum(1 for e in edges if e <= cv)
        if ce != len(comp) - 1:
            return False
    return True


def directed_triangles(T: Sequence[Sequence[int]]) -> list[tuple[Arc, Arc, Arc]]:
    """All cyclic triangles a->b->c->a of the tournament (as three arcs)."""
    n = len(T)
    out: list[tuple[Arc, Arc, Arc]] = []
    for a, b, c in combinations(range(n), 3):
        # the six labelled cyclic orderings of {a,b,c}; pick the cyclic ones
        for x, y, z in ((a, b, c), (a, c, b)):
            if T[x][y] and T[y][z] and T[z][x]:
                out.append(((x, y), (y, z), (z, x)))
    return out


# --------------------------------------------------------------------------
# 1. brute-force linear-forest FAS (independent ground truth, used in tests)
# --------------------------------------------------------------------------
def decide_linear_forest_fas_bruteforce(T: Sequence[Sequence[int]]) -> bool:
    """True iff T has a feedback arc set that is a linear forest.

    Searches arc subsets in increasing size.  Equivalent to
    decide_path_fas_bruteforce (proved by exhaustive agreement in tests).
    """
    n = len(T)
    arcs = arcs_of(T)
    m = len(arcs)
    for r in range(m + 1):
        for idx in combinations(range(m), r):
            S = [arcs[i] for i in idx]
            if underlying_is_linear_forest(S) and is_acyclic(n, set(arcs) - set(S)):
                return True
    return False


# --------------------------------------------------------------------------
# 2. ILP / LP formulation:  triangle-FAS + degree<=2 over the support
# --------------------------------------------------------------------------
def _build_ilp(T: Sequence[Sequence[int]], integral: bool):
    """Build the (mixed-)integer program for linear-forest FAS.

    Variables, one per tournament arc a = (u,v):
        x_a in {0,1}  (or [0,1] when integral=False) -- 1 iff a is in the FAS S
                      (a is a "back-arc" reversed by the order).

    Constraints:
      (triangle / FAS)  for every cyclic triangle, at least one arc is in S:
            x_{a1} + x_{a2} + x_{a3} >= 1.
        These are NECESSARY (a FAS must break every cyclic triangle) but not
        sufficient for T-S acyclic: after deleting S, the kept arcs are no
        longer a tournament, and a directed 4-cycle can remain after every
        cyclic triangle has been hit.  See the modelling note below.

      (degree<=2) for every vertex v, the number of S-arcs incident to v
            (in either direction) is at most 2:
            sum_{a incident to v} x_a <= 2.

    Objective: minimise sum x_a (does not matter for feasibility; a YES
    answer is "feasible", we read feasibility).

    IMPORTANT MODELLING NOTE.  "T - S acyclic" for a tournament is NOT the
    same as "every cyclic triangle of T has an arc in S": deleting an arc
    leaves a non-tournament digraph that can still contain a longer directed
    cycle whose every triangle was already partly deleted.  So the triangle
    constraints are a RELAXATION of acyclicity.  If S is already known to be a
    linear forest, directed 3- and 4-cycle cuts are sufficient (see
    docs/q2_nonforward_attack.md), but this older relaxation has only
    triangle cuts.  We therefore also test the program against brute force to
    measure the integrality / soundness gap.
    """
    arcs = arcs_of(T)
    m = len(arcs)
    idx = {a: i for i, a in enumerate(arcs)}
    n = len(T)

    rows: list[list[float]] = []
    lb: list[float] = []
    ub: list[float] = []

    # triangle constraints: sum x >= 1
    for tri in directed_triangles(T):
        row = [0.0] * m
        for a in tri:
            row[idx[a]] = 1.0
        rows.append(row)
        lb.append(1.0)
        ub.append(np.inf)

    # degree<=2 constraints
    for v in range(n):
        row = [0.0] * m
        for i, (u, w) in enumerate(arcs):
            if u == v or w == v:
                row[i] = 1.0
        rows.append(row)
        lb.append(-np.inf)
        ub.append(2.0)

    A = np.array(rows) if rows else np.zeros((0, m))
    constraints = LinearConstraint(A, lb, ub) if rows else None
    c = np.ones(m)  # minimise FAS size
    bounds = Bounds(0, 1)
    integrality = np.ones(m) if integral else np.zeros(m)
    return c, constraints, bounds, integrality, arcs


def ilp_linear_forest_fas_feasible(T: Sequence[Sequence[int]]) -> dict:
    """Solve the ILP relaxation (triangle + degree<=2). Returns a dict.

    Because triangle constraints are only a *relaxation* of acyclicity, an
    ILP-feasible point need not be a genuine FAS.  We post-verify the integer
    solution against acyclicity and linear-forest-ness, so the returned
    `genuine` flag is sound; `ilp_feasible` reflects only the relaxed model.
    """
    c, constraints, bounds, integrality, arcs = _build_ilp(T, integral=True)
    res = milp(c=c, constraints=constraints, bounds=bounds,
               integrality=integrality)
    out = {"ilp_feasible": bool(res.success), "genuine": False, "S": None}
    if res.success:
        S = [arcs[i] for i in range(len(arcs)) if res.x[i] > 0.5]
        out["S"] = S
        out["genuine"] = (underlying_is_linear_forest(S)
                          and is_acyclic(len(T), set(arcs) - set(S)))
    return out


def lp_relaxation_value(T: Sequence[Sequence[int]]) -> dict:
    """Solve the LP relaxation; report optimum and whether it is integral."""
    c, constraints, bounds, integrality, arcs = _build_ilp(T, integral=False)
    res = milp(c=c, constraints=constraints, bounds=bounds,
               integrality=integrality)
    out = {"lp_feasible": bool(res.success), "lp_value": None, "integral": None}
    if res.success:
        out["lp_value"] = float(res.fun)
        out["integral"] = bool(np.all(np.abs(res.x - np.round(res.x)) < 1e-6))
    return out


# --------------------------------------------------------------------------
# 3. exact ILP with lazy cycle constraints (sound acyclic search)
# --------------------------------------------------------------------------
def ilp_exact_linear_forest_fas(T: Sequence[Sequence[int]],
                                max_rounds: int = 200) -> dict:
    """Sound ILP with cutting-plane (lazy) cycle constraints + degree<=2.

    Starts from triangle constraints; whenever the integer optimum leaves a
    directed cycle in T-S, add that cycle as a new constraint
    (sum_{a in cycle} x_a >= 1) and re-solve.  Terminates when T-S is acyclic
    or the model becomes infeasible.

    This is a genuinely non-sweep, branch-and-cut style decision procedure.
    It is *correct* (a decision oracle) but NOT proven polynomial: the number
    of added cycle cuts can in principle be exponential.  We use it only as a
    cross-check oracle, and to probe how many cuts real instances need.
    """
    arcs = arcs_of(T)
    m = len(arcs)
    idx = {a: i for i, a in enumerate(arcs)}
    n = len(T)
    arcset = set(arcs)

    # base rows: triangles + degree
    base_rows: list[list[float]] = []
    base_lb: list[float] = []
    base_ub: list[float] = []
    for tri in directed_triangles(T):
        row = [0.0] * m
        for a in tri:
            row[idx[a]] = 1.0
        base_rows.append(row)
        base_lb.append(1.0)
        base_ub.append(np.inf)
    for v in range(n):
        row = [0.0] * m
        for i, (u, w) in enumerate(arcs):
            if u == v or w == v:
                row[i] = 1.0
        base_rows.append(row)
        base_lb.append(-np.inf)
        base_ub.append(2.0)

    rows = list(base_rows)
    lb = list(base_lb)
    ub = list(base_ub)
    c = np.ones(m)
    bounds = Bounds(0, 1)
    integrality = np.ones(m)
    cuts = 0
    for _ in range(max_rounds):
        A = np.array(rows)
        res = milp(c=c, constraints=LinearConstraint(A, lb, ub),
                   bounds=bounds, integrality=integrality)
        if not res.success:
            return {"feasible": False, "cuts": cuts, "S": None}
        S = [arcs[i] for i in range(m) if res.x[i] > 0.5]
        kept = arcset - set(S)
        # cut 1: directed cycle still alive in T - S  =>  S not a FAS
        cyc = _find_directed_cycle(n, kept)
        if cyc is not None:
            row = [0.0] * m
            for a in cyc:
                row[idx[a]] = 1.0
            rows.append(row)
            lb.append(1.0)
            ub.append(np.inf)
            cuts += 1
            continue
        # cut 2: undirected cycle inside S  =>  S not a linear forest.
        # Degree-<=2 constraints alone permit even undirected cycles
        # (e.g. a 4-cycle a-b-c-d-a where the digraph T-S is acyclic).
        # Forbid this particular undirected cycle: at least one of its edges
        # must LEAVE S.  edge {u,w} of S corresponds to exactly one arc a; we
        # require sum_{edges} (1 - x_a) >= 1, i.e. sum x_a <= |cyc|-1.
        ucyc = _find_undirected_cycle_edges(S)
        if ucyc is not None:
            row = [0.0] * m
            for a in ucyc:
                row[idx[a]] = 1.0
            rows.append(row)
            lb.append(-np.inf)
            ub.append(float(len(ucyc) - 1))
            cuts += 1
            continue
        # both clean: genuine linear-forest FAS
        return {"feasible": True, "cuts": cuts, "S": S,
                "linear_forest": underlying_is_linear_forest(S)}
    return {"feasible": None, "cuts": cuts, "S": None, "note": "max_rounds hit"}


def _find_undirected_cycle_edges(arcs: list[Arc]) -> list[Arc] | None:
    """If the underlying undirected graph of `arcs` has a cycle, return the
    arc list of one such cycle; else None."""
    adj: dict[int, list[tuple[int, Arc]]] = {}
    for a in arcs:
        u, v = a
        adj.setdefault(u, []).append((v, a))
        adj.setdefault(v, []).append((u, a))
    seen: set[int] = set()
    for start in list(adj):
        if start in seen:
            continue
        # DFS tracking parent edge
        stack: list[tuple[int, Arc | None]] = [(start, None)]
        parent: dict[int, tuple[int, Arc] | None] = {start: None}
        seen.add(start)
        while stack:
            u, _ = stack.pop()
            for w, a in adj[u]:
                pe = parent.get(u)
                if pe is not None and pe[1] == a:
                    continue  # don't walk back along the same edge
                if w not in seen:
                    seen.add(w)
                    parent[w] = (u, a)
                    stack.append((w, a))
                else:
                    # found a cycle: reconstruct via parents from u and w
                    return _reconstruct_undirected_cycle(parent, u, w, a)
    return None


def _reconstruct_undirected_cycle(parent, u, w, closing_arc) -> list[Arc]:
    def path_to_root(x):
        chain = []
        while parent.get(x) is not None:
            p, a = parent[x]
            chain.append((x, p, a))
            x = p
        chain.append((x, None, None))
        return chain
    pu = path_to_root(u)
    pw = path_to_root(w)
    anc_u = {x for x, _, _ in pu}
    lca = None
    for x, _, _ in pw:
        if x in anc_u:
            lca = x
            break
    edges: list[Arc] = [closing_arc]
    for x, p, a in pu:
        if x == lca:
            break
        edges.append(a)
    for x, p, a in pw:
        if x == lca:
            break
        edges.append(a)
    return edges


def _find_directed_cycle(n: int, arcs: Iterable[Arc]) -> list[Arc] | None:
    out: dict[int, list[int]] = {v: [] for v in range(n)}
    present = set(arcs)
    for u, v in present:
        out[u].append(v)
    color = [0] * n  # 0 white 1 gray 2 black
    parent: dict[int, int] = {}
    cyc_edges: list[Arc] | None = None

    def dfs(u: int) -> bool:
        nonlocal cyc_edges
        color[u] = 1
        for w in out[u]:
            if color[w] == 0:
                parent[w] = u
                if dfs(w):
                    return True
            elif color[w] == 1:
                # back edge u->w closes a cycle
                cyc = [(u, w)]
                x = u
                while x != w:
                    cyc.append((parent[x], x))
                    x = parent[x]
                cyc_edges = cyc
                return True
        color[u] = 2
        return False

    for s in range(n):
        if color[s] == 0 and dfs(s):
            return cyc_edges
    return None


# --------------------------------------------------------------------------
# 4. 2-SAT realizability attempt (score-window order CSP)
# --------------------------------------------------------------------------
def order_to_backarcs(T: Sequence[Sequence[int]], order: Sequence[int]) -> list[Arc]:
    return back_arcs(T, list(order))


def two_sat_attempt(T: Sequence[Sequence[int]]) -> dict:
    """Attempt to express linear-forest-FAS realizability as 2-SAT.

    Variables: for every unordered pair {u,v}, a boolean p_{uv} meaning
    "u precedes v in the order".  A linear order needs transitivity, which is
    a ternary constraint (p_{uv} & p_{vw} -> p_{uw}); this is NOT 2-SAT.  The
    degree-<=2 constraint on back-arcs is at most ternary per vertex as well.
    We document why the natural encoding fails to be 2-SAT and return the
    structural reason rather than a solver.
    """
    return {
        "is_2sat": False,
        "reason": (
            "Transitivity of the order is an inherently ternary implication "
            "p_uv & p_vw -> p_uw (Horn-3, not 2-SAT); the degree<=2 back-arc "
            "cap is a cardinality constraint on >=3 literals per vertex.  "
            "Neither is expressible in 2-CNF, so Path-FAS realizability is "
            "not captured by 2-SAT under the pairwise-precedence encoding."
        ),
    }


if __name__ == "__main__":
    # tiny smoke
    T = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]  # 3-cycle
    print("brute lf-FAS:", decide_linear_forest_fas_bruteforce(T))
    print("ilp exact:", ilp_exact_linear_forest_fas(T))
    print("lp relax:", lp_relaxation_value(T))
