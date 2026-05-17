"""ILP / cut-separation verifier for strong arc decomposition.

Backends:
 - Gurobi with lazy callbacks if `gurobipy` importable (preferred).
 - PuLP+CBC cutting-plane outer loop otherwise (default).

Contract:
    verify_ilp(D, time_limit_s=...) -> {
        "status":     "SAT" | "UNSAT" | "UNKNOWN",
        "witness":    (arcs_red, arcs_blue) | None,
        "unsat_core": [ {"X": list, "color": "red"|"blue"}, ... ] | None,
        "time_s":     float,
        "iterations": int,
        "backend":    "gurobi" | "pulp_cbc",
    }

Cut-separation logic:
 - variable x_e in {0,1}, 1 means RED;
 - for every nonempty proper X subsetneq V we require
       1 <= sum_{e in delta^+(X)} x_e <= |delta^+(X)| - 1.
 - separate violated cuts at integer incumbents only (fully correct);
 - the symmetry-breaking equality x_{e0} = 1 fixes one color.

Correctness rules enforced inline:
 - sanity gate: if D fails strong connectivity or arc-connectivity 2 the
   verifier returns UNSAT *with the witness cut* without calling the solver;
 - every SAT result is independently re-validated by computing strong
   connectivity of (V, A_R) and (V, A_B) outside the solver;
 - on UNSAT we record the cuts used and (best-effort) shrink them by a
   deletion filter to obtain a minimal core.
"""

from __future__ import annotations

import time
from typing import Any

import pulp

from digraph import Digraph, find_violated_cut


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def _arcs_by_color(D: Digraph, x_values: dict[tuple, int]) -> tuple[list, list]:
    """Split D's arcs according to x_values (1 = red, 0 = blue)."""
    red, blue = [], []
    for u, v, k in D.arcs():
        if x_values[(u, v, k)] == 1:
            red.append((u, v, k))
        else:
            blue.append((u, v, k))
    return red, blue


def _validate_witness(D: Digraph, red: list, blue: list) -> bool:
    """Re-check that (V, red) and (V, blue) are both strongly connected and
    that red, blue partition A(D)."""
    arcs_set = set(D.arcs())
    if len(red) + len(blue) != D.m():
        return False
    if set(red) | set(blue) != arcs_set:
        return False
    if set(red) & set(blue):
        return False
    R = D.subdigraph_on_arcs(red)
    B = D.subdigraph_on_arcs(blue)
    return R.is_strongly_connected() and B.is_strongly_connected()


def _sanity_gate(D: Digraph) -> dict[str, Any] | None:
    """Pre-solver necessary conditions.

    Returns a verifier-style dict if the instance is trivially UNSAT (not
    strongly connected, or arc-connectivity < 2); otherwise None.
    """
    if not D.is_strongly_connected():
        # produce a witness cut
        V = D.vertices()
        X = find_violated_cut(V, D.arcs())
        return {
            "status": "UNSAT",
            "witness": None,
            "unsat_core": [{"X": sorted(map(repr, X)) if X else [], "color": "input"}],
            "time_s": 0.0,
            "iterations": 0,
            "backend": "sanity",
            "reason": "input digraph is not strongly connected",
        }
    if D.arc_connectivity() < 2:
        return {
            "status": "UNSAT",
            "witness": None,
            "unsat_core": [],
            "time_s": 0.0,
            "iterations": 0,
            "backend": "sanity",
            "reason": "input digraph is not 2-arc-strong",
        }
    return None


# ----------------------------------------------------------------------------
# PuLP / CBC cutting-plane outer loop
# ----------------------------------------------------------------------------


def _verify_pulp(D: Digraph, time_limit_s: float, verbose: bool) -> dict[str, Any]:
    t0 = time.time()
    V = D.vertices()
    arcs = D.arcs()
    n = len(V)
    m = len(arcs)

    # Variables
    x = {e: pulp.LpVariable(f"x_{e[0]}_{e[1]}_{e[2]}", cat="Binary") for e in arcs}

    prob = pulp.LpProblem("SAD_cutplane", pulp.LpMinimize)
    prob += 0  # feasibility (no objective)

    # Symmetry-break: fix the lex-smallest arc to RED.
    e0 = min(arcs, key=lambda e: (repr(e[0]), repr(e[1]), e[2]))
    prob += x[e0] == 1, "symmetry_fix_e0_red"

    # Each vertex v != some root must have at least one RED out-arc and at
    # least one BLUE out-arc; this is the trivial vertex-singleton cut, and
    # it is a useful warmstart against degenerate LP optima. Add it upfront
    # for every nonempty proper *singleton* (n cuts), still polynomial.
    for v in V:
        out_arcs = [e for e in arcs if e[0] == v]
        in_arcs = [e for e in arcs if e[1] == v]
        if len(out_arcs) >= 2:  # else 2-arc-strongness already violated
            prob += pulp.lpSum(x[e] for e in out_arcs) >= 1
            prob += pulp.lpSum(x[e] for e in out_arcs) <= len(out_arcs) - 1
        if len(in_arcs) >= 2:
            prob += pulp.lpSum(x[e] for e in in_arcs) >= 1
            prob += pulp.lpSum(x[e] for e in in_arcs) <= len(in_arcs) - 1

    added_cuts: list[dict] = []
    iteration = 0
    max_iters = 200  # generous; small benchmarks finish well below this

    while True:
        iteration += 1
        if time.time() - t0 > time_limit_s:
            return {
                "status": "UNKNOWN",
                "witness": None,
                "unsat_core": None,
                "time_s": time.time() - t0,
                "iterations": iteration,
                "backend": "pulp_cbc",
                "reason": "time limit exceeded in cutting-plane outer loop",
            }
        if iteration > max_iters:
            return {
                "status": "UNKNOWN",
                "witness": None,
                "unsat_core": None,
                "time_s": time.time() - t0,
                "iterations": iteration,
                "backend": "pulp_cbc",
                "reason": "iteration cap reached",
            }

        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=max(5, time_limit_s - (time.time() - t0)))
        status_code = prob.solve(solver)
        status = pulp.LpStatus[status_code]
        if verbose:
            print(f"  [pulp_cbc] iter={iteration} status={status}")

        if status == "Infeasible":
            # Try to shrink added_cuts to a minimal core (deletion filter).
            core = _minimal_core_pulp(D, added_cuts, e0, time_limit_s - (time.time() - t0))
            return {
                "status": "UNSAT",
                "witness": None,
                "unsat_core": core,
                "time_s": time.time() - t0,
                "iterations": iteration,
                "backend": "pulp_cbc",
            }
        if status != "Optimal":
            return {
                "status": "UNKNOWN",
                "witness": None,
                "unsat_core": None,
                "time_s": time.time() - t0,
                "iterations": iteration,
                "backend": "pulp_cbc",
                "reason": f"unexpected solver status: {status}",
            }

        # Extract incumbent
        xv = {e: int(round(pulp.value(x[e]))) for e in arcs}
        red = [e for e in arcs if xv[e] == 1]
        blue = [e for e in arcs if xv[e] == 0]

        # Separate violated cuts. For each color, check strong connectivity;
        # if violated, add the X-cut inequality for both bounds (only the
        # one that's violated by the current incumbent will be binding, but
        # adding both is a cheap tightening).
        violated_added = False

        # Red separation
        X = find_violated_cut(V, red)
        if X is not None:
            cut_arcs = [(u, v, k) for (u, v, k) in arcs if u in X and v not in X]
            assert sum(xv[e] for e in cut_arcs) == 0, (
                "red separator claims violation but x-sum is nonzero"
            )
            prob += pulp.lpSum(x[e] for e in cut_arcs) >= 1, f"red_cut_iter{iteration}"
            added_cuts.append({"X": sorted(X, key=repr), "color": "red", "iter": iteration})
            violated_added = True

        # Blue separation
        X = find_violated_cut(V, blue)
        if X is not None:
            cut_arcs = [(u, v, k) for (u, v, k) in arcs if u in X and v not in X]
            assert sum(1 - xv[e] for e in cut_arcs) == 0, (
                "blue separator claims violation but (1-x)-sum is nonzero"
            )
            prob += pulp.lpSum(x[e] for e in cut_arcs) <= len(cut_arcs) - 1, f"blue_cut_iter{iteration}"
            added_cuts.append({"X": sorted(X, key=repr), "color": "blue", "iter": iteration})
            violated_added = True

        if not violated_added:
            # Feasible to the full cut family. Validate.
            if not _validate_witness(D, red, blue):
                return {
                    "status": "UNKNOWN",
                    "witness": None,
                    "unsat_core": None,
                    "time_s": time.time() - t0,
                    "iterations": iteration,
                    "backend": "pulp_cbc",
                    "reason": "witness failed independent re-validation (BUG)",
                }
            return {
                "status": "SAT",
                "witness": (red, blue),
                "unsat_core": None,
                "time_s": time.time() - t0,
                "iterations": iteration,
                "backend": "pulp_cbc",
            }


def _minimal_core_pulp(
    D: Digraph,
    cuts: list[dict],
    e0: tuple,
    budget_s: float,
) -> list[dict]:
    """Best-effort minimal core via deletion filter.

    Drop each cut in turn; if the remainder is still infeasible, keep it
    dropped. Bounded by budget_s; on timeout return the current shrunk list.
    """
    if budget_s <= 0:
        return list(cuts)
    t0 = time.time()
    remaining = list(cuts)
    i = 0
    while i < len(remaining):
        if time.time() - t0 > budget_s:
            break
        trial = remaining[:i] + remaining[i + 1 :]
        if _infeasible_with_cuts(D, trial, e0):
            remaining = trial
        else:
            i += 1
    return remaining


def _infeasible_with_cuts(D: Digraph, cuts: list[dict], e0: tuple) -> bool:
    """Test infeasibility of {symmetry, vertex-singleton cuts, supplied cuts}.

    Used by the deletion filter. Does *not* re-run the full cutting-plane
    loop; only the constraints that were already proven necessary.
    """
    arcs = D.arcs()
    V = D.vertices()
    x = {e: pulp.LpVariable(f"x_{e[0]}_{e[1]}_{e[2]}", cat="Binary") for e in arcs}
    prob = pulp.LpProblem("SAD_corecheck", pulp.LpMinimize)
    prob += 0
    prob += x[e0] == 1
    for v in V:
        out_arcs = [e for e in arcs if e[0] == v]
        in_arcs = [e for e in arcs if e[1] == v]
        if len(out_arcs) >= 2:
            prob += pulp.lpSum(x[e] for e in out_arcs) >= 1
            prob += pulp.lpSum(x[e] for e in out_arcs) <= len(out_arcs) - 1
        if len(in_arcs) >= 2:
            prob += pulp.lpSum(x[e] for e in in_arcs) >= 1
            prob += pulp.lpSum(x[e] for e in in_arcs) <= len(in_arcs) - 1
    for c in cuts:
        Xset = set(c["X"])
        cut_arcs = [(u, v, k) for (u, v, k) in arcs if u in Xset and v not in Xset]
        if c["color"] == "red":
            prob += pulp.lpSum(x[e] for e in cut_arcs) >= 1
        else:
            prob += pulp.lpSum(x[e] for e in cut_arcs) <= len(cut_arcs) - 1
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=10)
    code = prob.solve(solver)
    return pulp.LpStatus[code] == "Infeasible"


# ----------------------------------------------------------------------------
# Gurobi backend (optional)
# ----------------------------------------------------------------------------


def _verify_gurobi(D: Digraph, time_limit_s: float, verbose: bool) -> dict[str, Any]:
    import gurobipy as gp
    from gurobipy import GRB

    t0 = time.time()
    V = D.vertices()
    arcs = D.arcs()
    n = len(V)

    model = gp.Model("SAD")
    model.Params.OutputFlag = 1 if verbose else 0
    model.Params.LazyConstraints = 1
    model.Params.TimeLimit = time_limit_s

    x = {e: model.addVar(vtype=GRB.BINARY, name=f"x_{e[0]}_{e[1]}_{e[2]}") for e in arcs}
    model.update()

    e0 = min(arcs, key=lambda e: (repr(e[0]), repr(e[1]), e[2]))
    model.addConstr(x[e0] == 1, name="symmetry_fix")

    for v in V:
        out_arcs = [e for e in arcs if e[0] == v]
        in_arcs = [e for e in arcs if e[1] == v]
        if len(out_arcs) >= 2:
            model.addConstr(gp.quicksum(x[e] for e in out_arcs) >= 1)
            model.addConstr(gp.quicksum(x[e] for e in out_arcs) <= len(out_arcs) - 1)
        if len(in_arcs) >= 2:
            model.addConstr(gp.quicksum(x[e] for e in in_arcs) >= 1)
            model.addConstr(gp.quicksum(x[e] for e in in_arcs) <= len(in_arcs) - 1)

    added: list[dict] = []

    def callback(m: gp.Model, where: int) -> None:
        if where != GRB.Callback.MIPSOL:
            return
        xv = {e: int(round(m.cbGetSolution(x[e]))) for e in arcs}
        red = [e for e in arcs if xv[e] == 1]
        blue = [e for e in arcs if xv[e] == 0]
        X = find_violated_cut(V, red)
        if X is not None:
            cut_arcs = [(u, v, k) for (u, v, k) in arcs if u in X and v not in X]
            m.cbLazy(gp.quicksum(x[e] for e in cut_arcs) >= 1)
            added.append({"X": sorted(X, key=repr), "color": "red"})
        X = find_violated_cut(V, blue)
        if X is not None:
            cut_arcs = [(u, v, k) for (u, v, k) in arcs if u in X and v not in X]
            m.cbLazy(gp.quicksum(x[e] for e in cut_arcs) <= len(cut_arcs) - 1)
            added.append({"X": sorted(X, key=repr), "color": "blue"})

    model.optimize(callback)

    elapsed = time.time() - t0
    if model.Status == GRB.OPTIMAL:
        xv = {e: int(round(x[e].X)) for e in arcs}
        red = [e for e in arcs if xv[e] == 1]
        blue = [e for e in arcs if xv[e] == 0]
        if not _validate_witness(D, red, blue):
            return {
                "status": "UNKNOWN",
                "witness": None,
                "unsat_core": None,
                "time_s": elapsed,
                "iterations": len(added),
                "backend": "gurobi",
                "reason": "witness failed independent re-validation (BUG)",
            }
        return {
            "status": "SAT",
            "witness": (red, blue),
            "unsat_core": None,
            "time_s": elapsed,
            "iterations": len(added),
            "backend": "gurobi",
        }
    if model.Status == GRB.INFEASIBLE:
        return {
            "status": "UNSAT",
            "witness": None,
            "unsat_core": added,  # all added lazy cuts; not yet minimized
            "time_s": elapsed,
            "iterations": len(added),
            "backend": "gurobi",
        }
    return {
        "status": "UNKNOWN",
        "witness": None,
        "unsat_core": None,
        "time_s": elapsed,
        "iterations": len(added),
        "backend": "gurobi",
        "reason": f"gurobi status {model.Status}",
    }


# ----------------------------------------------------------------------------
# Public entry
# ----------------------------------------------------------------------------


def verify_ilp(
    D: Digraph,
    time_limit_s: float = 60.0,
    verbose: bool = False,
    prefer: str = "auto",  # "auto" | "gurobi" | "pulp"
) -> dict[str, Any]:
    """Decide strong arc decomposition of D by cut-separation ILP.

    See module docstring for the return contract.
    """
    gate = _sanity_gate(D)
    if gate is not None:
        return gate

    use_gurobi = False
    if prefer in ("auto", "gurobi"):
        try:
            import gurobipy  # noqa: F401

            use_gurobi = True
        except ImportError:
            if prefer == "gurobi":
                raise RuntimeError("gurobipy requested but not installed")

    if use_gurobi:
        return _verify_gurobi(D, time_limit_s, verbose)
    return _verify_pulp(D, time_limit_s, verbose)


if __name__ == "__main__":
    # Smoke test
    from benchmarks import all_benchmarks

    for b in all_benchmarks():
        D = b.build()
        res = verify_ilp(D, time_limit_s=30, verbose=False)
        ok = res["status"] == b.expected
        print(
            f"{b.name:18s} expected={b.expected:6s} got={res['status']:7s} "
            f"iters={res['iterations']:3d} t={res['time_s']:.2f}s  {'OK' if ok else 'FAIL'}"
        )
