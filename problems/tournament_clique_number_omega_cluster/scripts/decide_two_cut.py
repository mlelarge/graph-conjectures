"""SAT oracle for the two-cut face construction.

The one-cut portfolio asks for one cut p in a depth-d face module M_2 with

    pre_1(M_2,p) <= r1 and suf_2(M_2,m-p) <= r2.

The two-cut extension uses the schedule

    M_2[:s] | M_0 | M_2[s:t] | M_1 | M_2[t:]

with 0 <= s <= t <= m.  Its exact face formulas are

    Q1 = max(q1(M_0), q1(M_2), q1(M_1) + pre_1(M_2,t))
    Q2 = max(q2(M_1), q2(M_2), q2(M_0) + suf_2(M_2,m-s)).

Thus target (A,B) with companion slack (r1,r2) needs a depth-d face M_2 of
heights <= (1,A,B), plus two nested cuts with

    pre_1(M_2,t) <= r1 and suf_2(M_2,m-s) <= r2.

This file extends ``decide_simultaneous_cut`` by replacing the single cut boolean
with two prefix booleans ``left`` and ``right`` satisfying left => right.
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import math

from pysat.formula import CNF
from pysat.solvers import Cadical153

from decide_layer_labeling import decide_caps_labeling
from decide_stilde_layer_product import canonical_poset_arcs
from stilde_face_2cut import order_3piece
from stilde_pod_profiles import pod_profile
from stilde_profile_closure import step_profile

F5 = 25


def max_companion_slack(A, B, floor=F5):
    """Largest nonnegative slack whose two companions clear the product floor."""

    return A - math.ceil(floor / B), B - math.ceil(floor / A)


def build_cnf_two_cut(depth, A, B, r1, r2):
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

    # Total order: no directed triangle on any unordered triple.
    for i, j, k in itertools.combinations(range(n), 3):
        cnf.append([-before(i, j), -before(j, k), before(i, k)])
        cnf.append([before(i, j), before(j, k), -before(i, k)])

    TRUE = fresh()
    cnf.append([TRUE])

    def thermometer(cap):
        if cap < 0:
            raise ValueError("thermometer cap must be nonnegative")
        table = [[None] * (cap + 2) for _ in range(n)]
        for v in range(n):
            for t in range(2, cap + 1):
                table[v][t] = fresh()
            for t in range(3, cap + 1):
                cnf.append([-table[v][t], table[v][t - 1]])
        return table

    def geq(table, v, t):
        if t <= 1:
            return TRUE
        return table[v][t]

    arcs = [canonical_poset_arcs(depth, c) for c in range(3)]

    def height_clauses(table, cap, colour, extra=()):
        if cap <= 0:
            raise ValueError("global height caps must be positive")
        for u in range(n):
            for v in arcs[colour][u]:
                back = before(v, u)
                for t in range(1, cap):
                    clause = [-back, geq(table, v, t + 1)]
                    lu = geq(table, u, t)
                    if lu != TRUE:
                        clause.append(-lu)
                    clause.extend(extra)
                    cnf.append(clause)
                clause = [-back]
                lu = geq(table, u, cap)
                if lu != TRUE:
                    clause.append(-lu)
                clause.extend(extra)
                cnf.append(clause)

    # Global face module heights q0=1, q1<=A, q2<=B.
    caps = (1, A, B)
    levels = [thermometer(cap) for cap in caps]
    for colour, cap in enumerate(caps):
        height_clauses(levels[colour], cap, colour)

    # left(v): v is before the first cut s.
    # right(v): v is before the second cut t.
    left = [fresh() for _ in range(n)]
    right = [fresh() for _ in range(n)]
    for cut in (left, right):
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                # before(a,b) & cut(b) -> cut(a)
                cnf.append([-before(a, b), -cut[b], cut[a]])
    for v in range(n):
        cnf.append([-left[v], right[v]])

    def block_height(table, cap, colour, side):
        """Conditional height cap on a cut block.

        side='right-prefix' caps vertices with right(v)=True.
        side='left-suffix' caps vertices with left(v)=False.
        cap=0 is allowed and forces the corresponding block empty.
        """

        if side == "right-prefix":
            if cap == 0:
                for v in range(n):
                    cnf.append([-right[v]])
                return
            cond = lambda u, v: [-right[u], -right[v]]
        elif side == "left-suffix":
            if cap == 0:
                for v in range(n):
                    cnf.append([left[v]])
                return
            cond = lambda u, v: [left[u], left[v]]
        else:
            raise ValueError(f"unknown side {side!r}")

        for u in range(n):
            for v in arcs[colour][u]:
                back = before(v, u)
                extra = cond(u, v)
                for t in range(1, cap):
                    clause = [-back, geq(table, v, t + 1)]
                    lu = geq(table, u, t)
                    if lu != TRUE:
                        clause.append(-lu)
                    clause.extend(extra)
                    cnf.append(clause)
                clause = [-back]
                lu = geq(table, u, cap)
                if lu != TRUE:
                    clause.append(-lu)
                clause.extend(extra)
                cnf.append(clause)

    pre1 = thermometer(r1)
    suf2 = thermometer(r2)
    block_height(pre1, r1, 1, side="right-prefix")
    block_height(suf2, r2, 2, side="left-suffix")

    return cnf, before, left, right, n


def decide_two_cut(depth, A, B, r1, r2, solver_type=Cadical153):
    cnf, before, left, right, n = build_cnf_two_cut(depth, A, B, r1, r2)
    solver = solver_type(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    result = {
        "depth": depth,
        "A": A,
        "B": B,
        "r1": r1,
        "r2": r2,
        "product": A * B,
        "num_vars": cnf.nv,
        "num_clauses": len(cnf.clauses),
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
        s = sum(1 for v in range(n) if truth(left[v]))
        t = sum(1 for v in range(n) if truth(right[v]))
        profile = step_profile(order, depth)
        result.update(
            {
                "witness_order": order,
                "first_cut": s,
                "second_cut": t,
                "heights": profile.heights,
                "pre1_at_second_cut": profile.prefix[1][t],
                "suf2_after_first_cut": profile.suffix[2][n - s],
                "verified": (
                    s <= t
                    and profile.heights[0] == 1
                    and profile.heights[1] <= A
                    and profile.heights[2] <= B
                    and profile.prefix[1][t] <= r1
                    and profile.suffix[2][n - s] <= r2
                ),
            }
        )
    solver.delete()
    return result


@functools.lru_cache(maxsize=None)
def _profile(depth, caps):
    result = decide_caps_labeling(depth, caps)
    if not result["sat"]:
        return None
    return step_profile(list(result["witness_order"]), depth)


def certify_parent(record):
    """Build and verify the depth-(d+1) two-cut parent from a SAT record."""

    depth = record["depth"]
    A, B, r1, r2 = record["A"], record["B"], record["r1"], record["r2"]
    m2 = step_profile(list(record["witness_order"]), depth)
    m0 = _profile(depth, (1, A, B - r2))
    m1 = _profile(depth, (1, A - r1, B))
    if m0 is None or m1 is None:
        return None
    order = order_3piece(m0, m1, m2, record["first_cut"], record["second_cut"])
    profile = pod_profile(order, depth + 1)
    certified = dict(record)
    certified["module_heights"] = [m0.heights, m1.heights, m2.heights]
    certified["certified_heights"] = tuple(profile["layer_heights"])
    certified["certified_product"] = profile["height_product"]
    certified["certified_q0_is_1"] = profile["layer_heights"][0] == 1
    certified["certified"] = (
        profile["layer_heights"][0] == 1
        and profile["layer_heights"][1] <= A
        and profile["layer_heights"][2] <= B
    )
    return certified


def candidate_targets_below(limit=45, floor=F5):
    """Ordered target pairs below limit with maximal companion slack."""

    out = []
    for A in range(2, limit):
        for B in range(2, limit):
            product = A * B
            if product < floor or product >= limit:
                continue
            r1, r2 = max_companion_slack(A, B, floor)
            if r1 < 0 or r2 < 0:
                continue
            out.append((product, A, B, r1, r2))
    return sorted(out)


def scan_below_45(output=None):
    rows = []
    for _, A, B, r1, r2 in candidate_targets_below(45):
        result = decide_two_cut(5, A, B, r1, r2)
        row = {k: result[k] for k in (
            "product", "A", "B", "r1", "r2", "sat", "num_vars", "num_clauses"
        )}
        if result["sat"]:
            certified = certify_parent(result)
            row.update({
                "first_cut": result["first_cut"],
                "second_cut": result["second_cut"],
                "heights": result["heights"],
                "pre1_at_second_cut": result["pre1_at_second_cut"],
                "suf2_after_first_cut": result["suf2_after_first_cut"],
                "parent_heights": certified["certified_heights"] if certified else None,
                "parent_product": certified["certified_product"] if certified else None,
                "certified": certified["certified"] if certified else False,
            })
        rows.append(row)
        print(row, flush=True)
        if row["sat"] and row.get("certified") and row.get("parent_product", 10**9) < 45:
            break
    if output is not None:
        with open(output, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "problem": "two-cut portfolio construction search for F_6 < 45",
                    "target_count": len(rows),
                    "sat_count": sum(1 for row in rows if row["sat"]),
                    "rows": rows,
                },
                handle,
                indent=2,
            )
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--A", type=int)
    parser.add_argument("--B", type=int)
    parser.add_argument("--r1", type=int)
    parser.add_argument("--r2", type=int)
    parser.add_argument("--scan-below-45", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.scan_below_45:
        scan_below_45(args.output)
        return
    if args.A is None or args.B is None:
        parser.error("pass --A/--B or --scan-below-45")
    r1, r2 = args.r1, args.r2
    if r1 is None or r2 is None:
        r1, r2 = max_companion_slack(args.A, args.B)
    result = decide_two_cut(args.depth, args.A, args.B, r1, r2)
    show = {k: v for k, v in result.items() if k != "witness_order"}
    if result["sat"]:
        certified = certify_parent(result)
        if certified:
            show["certified_heights"] = certified["certified_heights"]
            show["certified_product"] = certified["certified_product"]
            show["certified"] = certified["certified"]
    print(show)


if __name__ == "__main__":
    main()
