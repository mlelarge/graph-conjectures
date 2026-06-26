"""Level-labeling SAT with LAZY transitivity (CEGAR) for the layer product.

The eager encoding in ``decide_layer_labeling`` spends O(n^3) clauses forbidding
directed triangles to make the order a total order; that is ~4.7M clauses at
depth 5 and ~1.3e8 at depth 6 (infeasible).  Here we omit transitivity, solve,
and lazily add only the directed 3-cycles that the model actually violates,
re-solving incrementally.  An acyclic tournament is a total order, so on
termination either the model is a genuine order satisfying the caps, or the
formula is UNSAT.

3-cycle detection uses Python big-int bitsets: with out[v]/in[v] adjacency
masks, an arc u->v lies on a triangle iff out[v] & in[u] != 0.
"""

from __future__ import annotations

import argparse
import itertools
import time

from pysat.solvers import Cadical153

from decide_stilde_layer_product import canonical_poset_arcs
from stilde_pod_profiles import pod_profile


def _build_base(depth, caps):
    """Order pair-vars + level (height) clauses, WITHOUT transitivity."""
    order = 3**depth
    clauses = []
    next_var = 0

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var

    pair_var = {}
    for a in range(order):
        for b in range(a + 1, order):
            pair_var[(a, b)] = fresh()

    def before(a, b):
        if a < b:
            return pair_var[(a, b)]
        return -pair_var[(b, a)]

    TRUE = fresh()
    clauses.append([TRUE])

    level = []
    for c, cap in enumerate(caps):
        a_cv = [[None] * (cap + 2) for _ in range(order)]
        for v in range(order):
            for t in range(2, cap + 1):
                a_cv[v][t] = fresh()
            for t in range(3, cap + 1):
                clauses.append([-a_cv[v][t], a_cv[v][t - 1]])
        level.append(a_cv)

    def geq(c, v, t):
        if t <= 1:
            return TRUE
        return level[c][v][t]

    for c, cap in enumerate(caps):
        arcs = canonical_poset_arcs(depth, c)
        for u in range(order):
            for v in arcs[u]:
                back = before(v, u)
                for t in range(1, cap):
                    lu, rv = geq(c, u, t), geq(c, v, t + 1)
                    clause = [-back, rv]
                    if lu != TRUE:
                        clause.append(-lu)
                    clauses.append(clause)
                lu = geq(c, u, cap)
                clause = [-back]
                if lu != TRUE:
                    clause.append(-lu)
                clauses.append(clause)

    return clauses, before, pair_var, order


def _find_triangles(model_set, pair_var, order, limit):
    """Return up to `limit` directed 3-cycles in the model's tournament."""
    # out[v] bitset of w with v before w
    out = [0] * order
    for (a, b), var in pair_var.items():
        if var in model_set:  # a before b
            out[a] |= 1 << b
        else:                 # b before a
            out[b] |= 1 << a
    inn = [0] * order
    for v in range(order):
        ov = out[v]
        w = ov
        while w:
            lb = w & (-w)
            inn[(lb.bit_length() - 1)] |= 1 << v
            w ^= lb
    triangles = []
    for u in range(order):
        ou, iu = out[u], inn[u]
        w = ou
        while w and len(triangles) < limit:
            lb = w & (-w)
            v = lb.bit_length() - 1
            w ^= lb
            # need x with v->x and x->u : out[v] & in[u]
            common = out[v] & iu
            if common:
                x = (common & (-common)).bit_length() - 1
                triangles.append((u, v, x))  # u->v->x->u
    return triangles


def decide_caps_lazy(depth, caps, time_budget=None, verbose=False):
    clauses, before, pair_var, order = _build_base(depth, caps)
    solver = Cadical153(bootstrap_with=clauses)

    def triangle_clause(u, v, x):
        # forbid u->v, v->x, x->u simultaneously
        return [-before(u, v), -before(v, x), -before(x, u)]

    rounds = 0
    added = 0
    t0 = time.time()
    while True:
        if not solver.solve():
            solver.delete()
            return {"depth": depth, "caps": tuple(caps),
                    "product": caps[0] * caps[1] * caps[2], "sat": False,
                    "rounds": rounds, "lazy_clauses": added,
                    "secs": time.time() - t0}
        model = set(solver.get_model())
        tris = _find_triangles(model, pair_var, order, limit=4000)
        if not tris:
            # acyclic -> genuine total order
            def precedes(a, b):
                lit = before(a, b)
                return lit in model if lit > 0 else -lit not in model
            import functools
            witness = sorted(range(order), key=functools.cmp_to_key(
                lambda a, b: 0 if a == b else (-1 if precedes(a, b) else 1)))
            profile = pod_profile(witness, depth)
            ok = all(h <= cap for h, cap in zip(profile["layer_heights"], caps))
            solver.delete()
            return {"depth": depth, "caps": tuple(caps),
                    "product": caps[0] * caps[1] * caps[2], "sat": True,
                    "verified_heights": tuple(profile["layer_heights"]),
                    "caps_respected": ok, "rounds": rounds,
                    "lazy_clauses": added, "secs": time.time() - t0,
                    "witness_order": witness}
        for (u, v, x) in tris:
            solver.add_clause(triangle_clause(u, v, x))
        added += len(tris)
        rounds += 1
        if verbose and rounds % 10 == 0:
            print(f"    round {rounds}: +{added} lazy clauses, "
                  f"{time.time()-t0:.0f}s", flush=True)
        if time_budget and time.time() - t0 > time_budget:
            solver.delete()
            return {"depth": depth, "caps": tuple(caps), "sat": None,
                    "timeout": True, "rounds": rounds, "lazy_clauses": added,
                    "secs": time.time() - t0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--caps", type=int, nargs=3, required=True)
    parser.add_argument("--budget", type=float)
    args = parser.parse_args()
    r = decide_caps_lazy(args.depth, tuple(args.caps),
                         time_budget=args.budget, verbose=True)
    print({k: v for k, v in r.items() if k != "witness_order"})


if __name__ == "__main__":
    main()
