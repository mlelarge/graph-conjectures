"""Level-labeling SAT for the canonical three-poset layer product of B_k.

Replaces the chain-enumeration encoding of ``decide_stilde_layer_product`` (which
blows up for caps >= 5, the L_5 blocker) by a compact *level labeling*:

For colour c, bound the height of the backward colour-c poset Q_c by <= cap_c
with thermometer variables a_{c,v,t} = [lvl_c(v) >= t], t = 2..cap_c, and the
implication

    (arc u->v colour c is backward)  ==>  lvl_c(u) < lvl_c(v).

A longest backward colour-c chain then forces lvl_c to strictly increase along
it, so height(Q_c) <= cap_c.  The order pi is a tournament with no directed
triangle (2 clauses per unordered triple), i.e. a total order.

This is O(#colour-c comparable pairs * cap_c) clauses for the height part,
instead of O(#(cap+1)-chains).  Cross-checked against the chain encoding on
depths 2-4; used to push the exact L_k frontier past depth 4.
"""

from __future__ import annotations

import argparse
import functools
import itertools

from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

from decide_stilde_layer_product import canonical_poset_arcs
from stilde_pod_profiles import pod_profile


def build_cnf(depth, caps):
    order = 3**depth
    cnf = CNF()
    next_var = 0

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var

    # --- order variables: pair_var[(a,b)] (a<b) means "a before b" ---
    pair_var = {}
    for a in range(order):
        for b in range(a + 1, order):
            pair_var[(a, b)] = fresh()

    def before(a, b):
        """Literal: a precedes b in pi."""
        if a < b:
            return pair_var[(a, b)]
        return -pair_var[(b, a)]

    # total order: no directed triangle on any unordered triple (i<j<k)
    for i, j, k in itertools.combinations(range(order), 3):
        cnf.append([-before(i, j), -before(j, k), before(i, k)])
        cnf.append([before(i, j), before(j, k), -before(i, k)])

    # --- level (thermometer) variables per colour: lvl in {1..cap} ---
    # a[c][v][t] = [lvl_c(v) >= t] for t = 2..cap_c (level >= 1 is constant True)
    TRUE = fresh()
    cnf.append([TRUE])

    level = []
    for c, cap in enumerate(caps):
        a_cv = [[None] * (cap + 2) for _ in range(order)]
        for v in range(order):
            for t in range(2, cap + 1):
                a_cv[v][t] = fresh()
            # monotonicity: lvl>=t implies lvl>=t-1
            for t in range(3, cap + 1):
                cnf.append([-a_cv[v][t], a_cv[v][t - 1]])
        level.append(a_cv)

    def geq(c, v, t):
        """Literal: lvl_c(v) >= t."""
        if t <= 1:
            return TRUE
        return level[c][v][t]

    # --- height constraints: backward colour-c arc u->v forces lvl_c(u)<lvl_c(v)
    for c, cap in enumerate(caps):
        arcs = canonical_poset_arcs(depth, c)  # arcs[u] = {v : u <_{P_c} v}
        for u in range(order):
            for v in arcs[u]:
                back = before(v, u)  # arc u->v is backward iff v precedes u
                # lvl_c(u) >= t  ==>  lvl_c(v) >= t+1, for t=1..cap-1
                for t in range(1, cap):
                    lu = geq(c, u, t)
                    rv = geq(c, v, t + 1)
                    clause = [-back, rv]
                    if lu != TRUE:
                        clause.append(-lu)
                    cnf.append(clause)
                # lvl_c(u) = cap is impossible when backward (no room above)
                lu = geq(c, u, cap)
                clause = [-back]
                if lu != TRUE:
                    clause.append(-lu)
                cnf.append(clause)

    return cnf, before, order


def decide_caps_labeling(depth, caps, solver_type=Cadical153):
    cnf, before, order = build_cnf(depth, caps)
    solver = solver_type(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    witness = None
    if sat:
        model = set(solver.get_model())

        def precedes(a, b):
            lit = before(a, b)
            return lit in model if lit > 0 else -lit not in model

        witness = sorted(
            range(order),
            key=functools.cmp_to_key(
                lambda a, b: 0 if a == b else (-1 if precedes(a, b) else 1)
            ),
        )
        profile = pod_profile(witness, depth)
        assert all(
            h <= cap for h, cap in zip(profile["layer_heights"], caps)
        ), (profile["layer_heights"], caps)
    solver.delete()
    return {
        "depth": depth,
        "caps": tuple(caps),
        "product": caps[0] * caps[1] * caps[2],
        "num_vars": cnf.nv,
        "num_clauses": len(cnf.clauses),
        "sat": sat,
        "witness_order": witness,
    }


def minimum_layer_product(depth, max_cap, solver_type=Cadical153, verbose=False):
    """Smallest product q0 q1 q2 achievable, scanning cap triples by product."""
    candidates = sorted(
        itertools.product(range(1, max_cap + 1), repeat=3),
        key=lambda caps: (caps[0] * caps[1] * caps[2], caps),
    )
    for caps in candidates:
        result = decide_caps_labeling(depth, caps, solver_type)
        if verbose:
            print(
                f"  caps={caps} product={result['product']} "
                f"vars={result['num_vars']} clauses={result['num_clauses']} "
                f"-> {'SAT' if result['sat'] else 'UNSAT'}",
                flush=True,
            )
        if result["sat"]:
            result["L"] = result["product"]
            return result
    return {"depth": depth, "sat": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--caps", type=int, nargs=3)
    parser.add_argument("--minimum", action="store_true")
    parser.add_argument("--max-cap", type=int, default=8)
    parser.add_argument("--minisat", action="store_true")
    args = parser.parse_args()
    solver = Minisat22 if args.minisat else Cadical153

    if args.minimum:
        result = minimum_layer_product(
            args.depth, args.max_cap, solver, verbose=True
        )
        print({k: v for k, v in result.items() if k != "witness_order"})
    elif args.caps is not None:
        result = decide_caps_labeling(args.depth, tuple(args.caps), solver)
        print({k: v for k, v in result.items() if k != "witness_order"})
    else:
        parser.error("pass --caps a b c or --minimum")


if __name__ == "__main__":
    main()
