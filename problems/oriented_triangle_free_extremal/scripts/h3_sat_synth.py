"""H3 SAT-synthesis: search for a 3-dichromatic oriented triangle-free graph on
n=18..24 over a FIXED d-regular skeleton via CEGAR.

Outer SAT variables:
  e_{ij}  (i<j)  : edge {i,j} present in the underlying simple graph
  o_{ij}  (i<j)  : if present, orientation is i->j (True) vs j->i (False)

Hard constraints (monolithic):
  (a) triangle-free : for every i<j<k, NOT(e_ij AND e_ik AND e_jk)
  (b) d-regular     : sum_j e_{ij} = d for each vertex i (sequential counter)
  (oriented is automatic: a single orientation bit per present edge, no digon)

Non-2-dicolourability is enforced by CEGAR (lazy refinement):
  - solve outer -> candidate (edges + orientation) -> build arcs
  - inner: core.is_k_dicolourable(n, arcs, 2)
      * if NOT 2-dicolourable -> chi_vec >= 3 -> CANDIDATE FOUND (verify exactly)
      * if 2-dicolourable     -> block this exact graph (over e/o vars) and loop

NOTE on soundness of UNSAT: blocking is per-candidate (a no-good over the full
e/o assignment), so the outer UNSAT after exhausting all candidates IS a complete
non-existence certificate for the d-regular slice -- but only if the loop runs to
outer-UNSAT within budget. A budget timeout is NOT a non-existence certificate
(empirical_not_proof gate). We report which of the two terminal states is reached.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time

from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

import core


def build_outer(n, d, vpool):
    """Return (clauses, e, o) where e[(i,j)] / o[(i,j)] are SAT var ids."""
    e = {}
    o = {}
    for i in range(n):
        for j in range(i + 1, n):
            e[(i, j)] = vpool.id(("e", i, j))
            o[(i, j)] = vpool.id(("o", i, j))
    clauses = []
    # (a) triangle-free
    for i, j, k in itertools.combinations(range(n), 3):
        clauses.append([-e[(i, j)], -e[(i, k)], -e[(j, k)]])
    # (b) d-regular via cardinality: for each vertex i, exactly d incident edges
    for i in range(n):
        lits = []
        for j in range(n):
            if j == i:
                continue
            a, b = (i, j) if i < j else (j, i)
            lits.append(e[(a, b)])
        enc = CardEnc.equals(lits=lits, bound=d, vpool=vpool,
                             encoding=EncType.seqcounter)
        clauses.extend(enc.clauses)
    return clauses, e, o


def candidate_arcs(model, e, o):
    mset = set(model)
    arcs = []
    for (i, j), ev in e.items():
        if ev in mset:
            if o[(i, j)] in mset:
                arcs.append((i, j))
            else:
                arcs.append((j, i))
    return arcs


def block_clause(model, e, o):
    """No-good over the full present-edge + orientation assignment."""
    mset = set(model)
    cl = []
    for (i, j), ev in e.items():
        if ev in mset:
            cl.append(-ev)                       # this edge present -> flip
            ov = o[(i, j)]
            cl.append(-ov if ov in mset else ov)  # this orientation -> flip
        else:
            cl.append(ev)                        # this edge absent -> flip
    return cl


def synth(n, d, time_cap, solver_name="glucose3", verbose=True):
    vpool = IDPool()
    clauses, e, o = build_outer(n, d, vpool)
    solver = Solver(name=solver_name, bootstrap_with=clauses)
    t0 = time.time()
    rounds = 0
    candidates_tested = 0
    last_chi3 = None
    while True:
        if time.time() - t0 > time_cap:
            solver.delete()
            return {"n": n, "d": d, "status": "TIMEOUT", "rounds": rounds,
                    "candidates_tested": candidates_tested,
                    "elapsed": round(time.time() - t0, 1)}
        if not solver.solve():
            solver.delete()
            return {"n": n, "d": d, "status": "UNSAT", "rounds": rounds,
                    "candidates_tested": candidates_tested,
                    "elapsed": round(time.time() - t0, 1)}
        model = solver.get_model()
        rounds += 1
        arcs = candidate_arcs(model, e, o)
        candidates_tested += 1
        two_col = core.is_k_dicolourable(n, arcs, 2)
        if not two_col:
            # chi_vec >= 3: a SAT hit. Verify exactly below.
            solver.delete()
            return {"n": n, "d": d, "status": "SAT", "rounds": rounds,
                    "candidates_tested": candidates_tested,
                    "arcs": arcs, "elapsed": round(time.time() - t0, 1)}
        # 2-dicolourable: block this exact graph and continue
        solver.add_clause(block_clause(model, e, o))
        if verbose and rounds % 200 == 0:
            print(f"  [n={n} d={d}] round {rounds} "
                  f"({round(time.time()-t0,1)}s) still searching", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("d", type=int)
    ap.add_argument("--cap", type=float, default=300.0)
    args = ap.parse_args()
    res = synth(args.n, args.d, args.cap)
    if res["status"] == "SAT":
        n, arcs = res["n"], res["arcs"]
        res["verify"] = {
            "is_oriented": core.is_oriented(arcs),
            "is_triangle_free": core.is_triangle_free(n, arcs),
            "chi_vec": core.dichromatic_number(n, arcs, ub=4),
        }
    print(json.dumps(res, default=str))


if __name__ == "__main__":
    main()
