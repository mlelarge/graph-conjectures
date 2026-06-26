"""SAT: does a depth-d face module of heights <=(1,A,B) admit a SIMULTANEOUS cut?

This is the sec-28 M_2-regeneration oracle.  A target (A,B) with slack (r1,r2) is
reachable by the portfolio 2-cut iff there is a depth-d face order pi (q_0=1,
q_1<=A, q_2<=B) and a cut position p with

    pre_1(pi, p)   = longest backward colour-1 chain in the first p vertices  <= r1
    suf_2(pi, m-p) = longest backward colour-2 chain in the last  m-p vertices <= r2

(the companions (1,A,B-r2),(1,A-r1,B) enter only as scalars and exist separately,
so SAT here + companions existing => F_{d+1} <= A*B by construction, sec 28).

Encoding (extends decide_layer_labeling):
  * total order (no directed triangle), reused;
  * global thermometers cap (1,A,B) -> q_0=1, q_1<=A, q_2<=B (reused);
  * cut booleans cb(v) constrained to a PREFIX of the order (downward closed):
        before(a,b) & cb(b) -> cb(a);
  * prefix thermometer ell1 cap r1, active only when BOTH endpoints are before the
    cut: clause carries extra literals (-cb(u), -cb(v));
  * suffix thermometer ell2 cap r2, active only when BOTH endpoints are after the
    cut: clause carries extra literals (+cb(u), +cb(v)).

Degenerate end-cuts self-exclude: an empty prefix forces q_2<=r2, which with
q_1<=A and the F_5=25 product floor is UNSAT for moderate (A,B).
"""

from __future__ import annotations

import argparse
import functools
import itertools

from pysat.formula import CNF
from pysat.solvers import Cadical153

from decide_stilde_layer_product import canonical_poset_arcs
from stilde_profile_closure import step_profile


def build_cnf_cut(depth, A, B, r1, r2):
    n = 3 ** depth
    cnf = CNF()
    counter = [0]

    def fresh():
        counter[0] += 1
        return counter[0]

    pair = {}
    for a in range(n):
        for b in range(a + 1, n):
            pair[(a, b)] = fresh()

    def before(a, b):
        return pair[(a, b)] if a < b else -pair[(b, a)]

    # total order: no directed triangle on any unordered triple
    for i, j, k in itertools.combinations(range(n), 3):
        cnf.append([-before(i, j), -before(j, k), before(i, k)])
        cnf.append([before(i, j), before(j, k), -before(i, k)])

    TRUE = fresh()
    cnf.append([TRUE])

    def thermometer(cap):
        """Per-vertex thermometer vars a[v][t]=[level>=t], t=2..cap, monotone."""
        a_cv = [[None] * (cap + 2) for _ in range(n)]
        for v in range(n):
            for t in range(2, cap + 1):
                a_cv[v][t] = fresh()
            for t in range(3, cap + 1):
                cnf.append([-a_cv[v][t], a_cv[v][t - 1]])
        return a_cv

    caps = (1, A, B)
    level = [thermometer(cap) for cap in caps]

    def geq(table, v, t, cap):
        return TRUE if t <= 1 else table[v][t]

    arcs = [canonical_poset_arcs(depth, c) for c in range(3)]

    def height_clauses(table, cap, colour, extra=()):
        """Backward colour-`colour` arc forces level(u) < level(v); `extra` makes
        the constraint conditional (added literals satisfy the clause when off)."""
        for u in range(n):
            for v in arcs[colour][u]:
                back = before(v, u)  # arc u->v backward iff v precedes u
                for t in range(1, cap):
                    clause = [-back, geq(table, v, t + 1, cap)]
                    lu = geq(table, u, t, cap)
                    if lu != TRUE:
                        clause.append(-lu)
                    clause.extend(extra)
                    cnf.append(clause)
                clause = [-back]
                lu = geq(table, u, cap, cap)
                if lu != TRUE:
                    clause.append(-lu)
                clause.extend(extra)
                cnf.append(clause)

    # global heights q_0=1, q_1<=A, q_2<=B
    for colour, cap in enumerate(caps):
        height_clauses(level[colour], cap, colour)

    # cut booleans, constrained to a prefix of the order
    cb = [fresh() for _ in range(n)]
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            # before(a,b) & cb(b) -> cb(a)
            cnf.append([-before(a, b), -cb[b], cb[a]])

    # prefix colour-1 height <= r1 among before-cut vertices
    pre1 = thermometer(r1)
    # suffix colour-2 height <= r2 among after-cut vertices
    suf2 = thermometer(r2)

    # rebuild conditional height clauses for the two cut blocks
    def block_height(table, cap, colour, both_before):
        for u in range(n):
            for v in arcs[colour][u]:
                back = before(v, u)
                # condition: both u,v on the chosen side of the cut
                if both_before:
                    cond = [-cb[u], -cb[v]]   # active only if cb(u) & cb(v)
                else:
                    cond = [cb[u], cb[v]]      # active only if ~cb(u) & ~cb(v)
                for t in range(1, cap):
                    clause = [-back, geq(table, v, t + 1, cap)]
                    lu = geq(table, u, t, cap)
                    if lu != TRUE:
                        clause.append(-lu)
                    clause.extend(cond)
                    cnf.append(clause)
                clause = [-back]
                lu = geq(table, u, cap, cap)
                if lu != TRUE:
                    clause.append(-lu)
                clause.extend(cond)
                cnf.append(clause)

    block_height(pre1, r1, 1, both_before=True)
    block_height(suf2, r2, 2, both_before=False)

    return cnf, before, cb, n


def decide_simultaneous_cut(depth, A, B, r1, r2, solver_type=Cadical153):
    cnf, before, cb, n = build_cnf_cut(depth, A, B, r1, r2)
    solver = solver_type(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    result = {
        "depth": depth, "A": A, "B": B, "r1": r1, "r2": r2,
        "product": A * B, "num_vars": cnf.nv, "num_clauses": len(cnf.clauses),
        "sat": sat,
    }
    if sat:
        model = set(solver.get_model())

        def truth(lit):
            return lit in model if lit > 0 else (-lit) not in model

        order = sorted(
            range(n),
            key=functools.cmp_to_key(
                lambda a, b: 0 if a == b else (-1 if truth(before(a, b)) else 1)
            ),
        )
        p = sum(1 for v in range(n) if truth(cb[v]))
        # ground-truth verification via step_profile
        prof = step_profile(order, depth)
        result["witness_order"] = order
        result["cut_position"] = p
        result["heights"] = prof.heights
        result["pre1_at_cut"] = prof.prefix[1][p]
        result["suf2_after_cut"] = prof.suffix[2][n - p]
        result["verified"] = (
            prof.heights[0] == 1
            and prof.heights[1] <= A and prof.heights[2] <= B
            and prof.prefix[1][p] <= r1 and prof.suffix[2][n - p] <= r2
        )
    solver.delete()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--A", type=int, required=True)
    parser.add_argument("--B", type=int, required=True)
    parser.add_argument("--r1", type=int, default=1)
    parser.add_argument("--r2", type=int, default=2)
    args = parser.parse_args()
    result = decide_simultaneous_cut(args.depth, args.A, args.B, args.r1, args.r2)
    show = {k: v for k, v in result.items() if k != "witness_order"}
    print(show)


if __name__ == "__main__":
    main()
