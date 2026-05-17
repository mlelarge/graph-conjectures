"""SAT verifier with arborescence witnesses.

Encoding (per `team/03_verifier_design.md` §3):

Variables:
 - x_e          1 = arc e is red, 0 = arc e is blue
 - t^{c, +}_e   arc e is in the out-branching of color c (root r_c)
 - t^{c, -}_e   arc e is in the in-branching of color c (root r_c)
 - level^{c, sigma}_{v, j}   thermometer encoding of `level >= j` for vertex
                             v, color c, direction sigma. Levels lie in
                             [0, n-1]; level of the root is 0.

Constraints (per direction sigma in {+, -} and color c in {R, B}):
 1. The branching has exactly n - 1 arcs.
 2. Every non-root has exactly one incoming branching-arc (for sigma = +)
    or exactly one outgoing branching-arc (for sigma = -).
 3. The root has zero incoming branching-arcs (sigma = +) / zero outgoing
    (sigma = -).
 4. Color compatibility: t^{R, *}_e -> x_e; t^{B, *}_e -> ~x_e.
 5. Level monotonicity:
      sigma = + : t^{c, +}_{(u, v)} = 1 -> level(v) > level(u);
      sigma = - : t^{c, -}_{(u, v)} = 1 -> level(u) > level(v).
    Root has level 0; all other vertices have level in [1, n-1].

Together (2) + (3) force every non-root to have an incoming (or outgoing)
edge, while (5) forbids cycles. With exactly n - 1 arcs (constraint 1) and
acyclicity, every non-root has a unique directed path to/from the root,
i.e. the t-subdigraph is a spanning arborescence rooted at r_c.

We use PySAT with the CaDiCaL solver. Cardinality constraints are encoded
via `pysat.card.CardEnc` (sequential counter encoding) for `= 1` (or `<= 1`
combined with `>= 1`) and `= n - 1`.

Public API:
    verify_sat(D, time_limit_s=...) -> {
        "status":     "SAT" | "UNSAT" | "UNKNOWN",
        "witness":    (red, blue) | None,
        "unsat_core": list | None,
        "time_s":     float,
        "iterations": int (always 1 for SAT),
        "backend":    "pysat_cadical" | "pysat_glucose4",
    }
"""

from __future__ import annotations

import time
from typing import Any

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from digraph import Digraph
from verifier_ilp import _sanity_gate, _validate_witness


def _build_cnf(D: Digraph) -> tuple[CNF, IDPool, dict, dict, dict]:
    """Build the CNF and return (cnf, vpool, x_vars, t_vars, level_vars).

    x_vars: dict mapping arc-key -> integer variable id;
    t_vars: dict mapping (color, sigma, arc-key) -> integer variable id;
    level_vars: dict mapping (color, sigma, vertex, j) -> integer variable id,
                where j in {1, ..., n-1}.
    """
    V = D.vertices()
    arcs = D.arcs()
    n = len(V)
    if n < 2:
        raise ValueError("need >= 2 vertices")

    vpool = IDPool()
    cnf = CNF()

    # Allocate variables
    x_vars: dict = {}
    for e in arcs:
        x_vars[e] = vpool.id(("x", e))

    colors = ("R", "B")
    sigmas = ("+", "-")
    t_vars: dict = {}
    for c in colors:
        for sigma in sigmas:
            for e in arcs:
                t_vars[(c, sigma, e)] = vpool.id(("t", c, sigma, e))

    level_vars: dict = {}
    for c in colors:
        for sigma in sigmas:
            for v in V:
                for j in range(1, n):
                    level_vars[(c, sigma, v, j)] = vpool.id(("L", c, sigma, v, j))

    # Color compatibility
    for e in arcs:
        for c in colors:
            t_pos = t_vars[(c, "+", e)]
            t_neg = t_vars[(c, "-", e)]
            if c == "R":
                # t_R -> x_e (i.e. x_e = 1)
                cnf.append([-t_pos, x_vars[e]])
                cnf.append([-t_neg, x_vars[e]])
            else:
                # t_B -> ~x_e
                cnf.append([-t_pos, -x_vars[e]])
                cnf.append([-t_neg, -x_vars[e]])

    # Branching structure: choose root r_c = V[0] for both colors and both
    # directions. (Choice of root does not affect existence of arborescence.)
    r = V[0]

    for c in colors:
        # Out-branching: every non-root has exactly one incoming t_pos arc;
        # root has zero incoming t_pos arcs.
        for v in V:
            in_arcs = [e for e in arcs if e[1] == v]
            lits = [t_vars[(c, "+", e)] for e in in_arcs]
            if v == r:
                # zero incoming
                for lit in lits:
                    cnf.append([-lit])
            else:
                # exactly one incoming
                _add_exactly_k(cnf, vpool, lits, 1)

        # In-branching: every non-root has exactly one outgoing t_neg arc;
        # root has zero outgoing t_neg arcs.
        for v in V:
            out_arcs = [e for e in arcs if e[0] == v]
            lits = [t_vars[(c, "-", e)] for e in out_arcs]
            if v == r:
                for lit in lits:
                    cnf.append([-lit])
            else:
                _add_exactly_k(cnf, vpool, lits, 1)

        # exactly n - 1 arcs in each branching (redundant given degree constraints,
        # but useful as a propagator)
        for sigma in sigmas:
            all_t = [t_vars[(c, sigma, e)] for e in arcs]
            _add_exactly_k(cnf, vpool, all_t, n - 1)

    # Level encoding: thermometer. level(v, j) means "level of v >= j".
    # Monotone: level(v, j+1) -> level(v, j). Root has level 0: level(r, 1) = 0.
    for c in colors:
        for sigma in sigmas:
            for v in V:
                if v == r:
                    # forbid any level >= 1
                    for j in range(1, n):
                        cnf.append([-level_vars[(c, sigma, v, j)]])
                else:
                    # require level >= 1 (every non-root vertex has positive level)
                    cnf.append([level_vars[(c, sigma, v, 1)]])
                # monotonicity
                for j in range(2, n):
                    cnf.append(
                        [
                            -level_vars[(c, sigma, v, j)],
                            level_vars[(c, sigma, v, j - 1)],
                        ]
                    )

    # Level propagation along chosen arcs.
    # For sigma = + (out-branching from r), t^{c, +}_{(u,v)} implies
    #   level(v) >= level(u) + 1
    # That is, for every j in [1, n-1]:
    #   level(u) >= j  AND  t -> level(v) >= j + 1
    # Equivalently:
    #   ~t  v  ~level(u, j)  v  level(v, j+1)        (for 1 <= j <= n-2)
    # And the base case: t -> level(v) >= 1 (which is already implied for
    # non-root v above). We also need t -> level(v) >= level(u) + 1 when
    # level(u) = 0, i.e. u = r: covered by "level(v) >= 1" since the level
    # of r is 0.
    for c in colors:
        for e in arcs:
            u, v, _ = e
            t_pos = t_vars[(c, "+", e)]
            t_neg = t_vars[(c, "-", e)]
            for j in range(1, n - 1):
                # out-branching: level(v) > level(u)
                lu = level_vars[(c, "+", u, j)]
                lv_next = level_vars[(c, "+", v, j + 1)]
                cnf.append([-t_pos, -lu, lv_next])
                # in-branching: level(u) > level(v)
                lv = level_vars[(c, "-", v, j)]
                lu_next = level_vars[(c, "-", u, j + 1)]
                cnf.append([-t_neg, -lv, lu_next])
            # Boundary: if the tail (head) is already at the max level n-1
            # and the arc is chosen, the head (tail) would need level n which
            # does not exist. Equivalently this rules out cycles in the
            # branching: a directed cycle of any length forces some vertex
            # along it to exceed n-1.
            #
            # Out-branching forbids tail at max level:
            cnf.append([-t_pos, -level_vars[(c, "+", u, n - 1)]])
            # In-branching forbids head at max level:
            cnf.append([-t_neg, -level_vars[(c, "-", v, n - 1)]])

    return cnf, vpool, x_vars, t_vars, level_vars


def _add_exactly_k(cnf: CNF, vpool: IDPool, lits: list[int], k: int) -> None:
    """Append clauses asserting exactly k of `lits` are true.

    Implemented via sequential counter encoding for both at-least-k and
    at-most-k. Edge case: k == 0 -> all literals must be false; k ==
    len(lits) -> all must be true.
    """
    if k < 0 or k > len(lits):
        # infeasibility hard-coded
        cnf.append([])
        return
    if k == 0:
        for lit in lits:
            cnf.append([-lit])
        return
    if k == len(lits):
        for lit in lits:
            cnf.append([lit])
        return
    # at most k
    amk = CardEnc.atmost(lits=lits, bound=k, vpool=vpool, encoding=EncType.seqcounter)
    for cl in amk.clauses:
        cnf.append(cl)
    # at least k <=> at most (n - k) of the negations
    neg = [-l for l in lits]
    alk_neg = CardEnc.atmost(
        lits=neg, bound=len(lits) - k, vpool=vpool, encoding=EncType.seqcounter
    )
    for cl in alk_neg.clauses:
        cnf.append(cl)


def verify_sat(
    D: Digraph,
    time_limit_s: float = 60.0,
    verbose: bool = False,
    solver_name: str = "cadical153",
) -> dict[str, Any]:
    """Decide SAD via SAT with arborescence witnesses."""
    t0 = time.time()

    gate = _sanity_gate(D)
    if gate is not None:
        gate = dict(gate)
        gate["backend"] = "sanity"
        return gate

    arcs = D.arcs()
    cnf, vpool, x_vars, t_vars, level_vars = _build_cnf(D)

    # Symmetry break: fix lex-smallest arc to red.
    e0 = min(arcs, key=lambda e: (repr(e[0]), repr(e[1]), e[2]))
    cnf.append([x_vars[e0]])

    if verbose:
        print(
            f"  [pysat] vars={vpool.top}  clauses={len(cnf.clauses)}  "
            f"solver={solver_name}"
        )

    backend_label = f"pysat_{solver_name}"

    # PySAT solvers do not all support a true wall-clock time limit through
    # the solve() API. We rely on the global benchmark watchdog for very
    # large instances; for the validation set timing has not been an issue.
    with Solver(name=solver_name, bootstrap_with=cnf) as s:
        sat = s.solve()
        elapsed = time.time() - t0
        if sat is None:
            return {
                "status": "UNKNOWN",
                "witness": None,
                "unsat_core": None,
                "time_s": elapsed,
                "iterations": 1,
                "backend": backend_label,
                "reason": "solver returned None",
            }
        if sat:
            model = s.get_model()
            true_set = set(l for l in model if l > 0)
            red, blue = [], []
            for e in arcs:
                if x_vars[e] in true_set:
                    red.append(e)
                else:
                    blue.append(e)
            if not _validate_witness(D, red, blue):
                return {
                    "status": "UNKNOWN",
                    "witness": None,
                    "unsat_core": None,
                    "time_s": elapsed,
                    "iterations": 1,
                    "backend": backend_label,
                    "reason": "witness failed independent re-validation (BUG)",
                }
            return {
                "status": "SAT",
                "witness": (red, blue),
                "unsat_core": None,
                "time_s": elapsed,
                "iterations": 1,
                "backend": backend_label,
            }
        # UNSAT — we have a solver-level refutation proof (handled by
        # the solver internals). For human-readable cores we would need to
        # re-run with assumptions; we record `"core": "solver_proof"` here.
        return {
            "status": "UNSAT",
            "witness": None,
            "unsat_core": [{"note": "solver-level proof (no assumption set used)"}],
            "time_s": elapsed,
            "iterations": 1,
            "backend": backend_label,
        }


if __name__ == "__main__":
    from benchmarks import all_benchmarks

    for b in all_benchmarks():
        D = b.build()
        res = verify_sat(D, time_limit_s=60, verbose=False)
        ok = res["status"] == b.expected
        print(
            f"{b.name:18s} expected={b.expected:6s} got={res['status']:7s} "
            f"t={res['time_s']:.2f}s  {'OK' if ok else 'FAIL'}"
        )
