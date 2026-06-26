"""Binary-key order encoding for the layer product of B_k.

``decide_layer_labeling.py`` uses pairwise order variables and O(n^3)
transitivity clauses.  At depth 6 this is the blocker.  This file keeps the
same level-labeling height constraints, but replaces transitivity by a binary
key for each vertex:

    a precedes b  iff  (key[a], a) < (key[b], b).

Ties are broken by vertex id, so every assignment defines a genuine total order.
Conversely, every total order is represented by assigning distinct increasing
keys to its vertices.  Therefore this encoding is equisatisfiable with the
pairwise total-order encoding, but needs only O(n^2 log n) comparator clauses
instead of O(n^3) triangle clauses.
"""

from __future__ import annotations

import argparse
import functools
import itertools
import math

from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

from decide_stilde_layer_product import canonical_poset_arcs
from stilde_pod_profiles import pod_profile


def _append_clause(cnf, clause, true_lit):
    """Append a clause after simplifying occurrences of the fixed true literal."""

    simplified = []
    seen = set()
    for lit in clause:
        if lit == true_lit:
            return
        if lit == -true_lit:
            continue
        if -lit in seen:
            return
        if lit not in seen:
            seen.add(lit)
            simplified.append(lit)
    cnf.append(simplified)


def _constant_bits(value, bit_count):
    return tuple((value >> shift) & 1 for shift in range(bit_count - 1, -1, -1))


def _add_key_less_than(cnf, bits, bound, true_lit):
    """Constrain the key encoded by ``bits`` to be strictly less than ``bound``."""

    bit_count = len(bits)
    if bound >= 2**bit_count:
        return
    if bound <= 0:
        cnf.append([])
        return
    bound_bits = _constant_bits(bound, bit_count)
    equal_prefix = []
    for bit, bound_bit in zip(bits, bound_bits):
        if bound_bit == 0:
            _append_clause(cnf, [-lit for lit in equal_prefix] + [-bit], true_lit)
        equal_prefix.append(bit if bound_bit else -bit)


def build_cnf(depth, caps, range_keys=False, distinct_keys=False):
    order = 3**depth
    bit_count = max(1, math.ceil(math.log2(order)))
    cnf = CNF()
    next_var = 0

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var

    true_lit = fresh()
    cnf.append([true_lit])

    # key_bits[v] are listed most-significant bit first.
    key_bits = [
        [fresh() for _ in range(bit_count)]
        for _ in range(order)
    ]

    compare_cache = {}

    def compare_bits(left_bits, right_bits, tie_true):
        """Literal for left_bits < right_bits, or <= when tie_true is set."""

        result = true_lit if tie_true else -true_lit
        # Build the suffix comparator from the least significant bit upward.
        for x_lit, y_lit in reversed(list(zip(left_bits, right_bits))):
            z_lit = fresh()
            # z = (x < y at this bit) OR ((x == y) AND result).
            #
            # If x=0,y=1 then z=1; if x=1,y=0 then z=0.
            _append_clause(cnf, [x_lit, -y_lit, z_lit], true_lit)
            _append_clause(cnf, [-x_lit, y_lit, -z_lit], true_lit)
            # If x=y=0 then z=result.
            _append_clause(cnf, [x_lit, y_lit, -result, z_lit], true_lit)
            _append_clause(cnf, [x_lit, y_lit, result, -z_lit], true_lit)
            # If x=y=1 then z=result.
            _append_clause(cnf, [-x_lit, -y_lit, -result, z_lit], true_lit)
            _append_clause(cnf, [-x_lit, -y_lit, result, -z_lit], true_lit)
            result = z_lit
        return result

    def compare(a, b, tie_true):
        key = (a, b, tie_true)
        cached = compare_cache.get(key)
        if cached is not None:
            return cached
        lit = compare_bits(key_bits[a], key_bits[b], tie_true)
        compare_cache[key] = lit
        return lit

    def before(a, b):
        """Literal meaning a precedes b in the key/tie order."""

        if a == b:
            raise ValueError("before(a,b) requires distinct vertices")
        return compare(a, b, tie_true=(a < b))

    def strict_before(a, b):
        """Literal meaning key[a] < key[b], without the vertex-id tie-break."""

        if a == b:
            raise ValueError("strict_before(a,b) requires distinct vertices")
        return compare(a, b, tie_true=False)

    if range_keys:
        for bits in key_bits:
            _add_key_less_than(cnf, bits, order, true_lit)

    if distinct_keys:
        for a in range(order):
            for b in range(a + 1, order):
                cnf.append([strict_before(a, b), strict_before(b, a)])

    # --- level (thermometer) variables per colour: lvl in {1..cap} ---
    level = []
    for cap in caps:
        a_cv = [[None] * (cap + 2) for _ in range(order)]
        for v in range(order):
            for t in range(2, cap + 1):
                a_cv[v][t] = fresh()
            for t in range(3, cap + 1):
                cnf.append([-a_cv[v][t], a_cv[v][t - 1]])
        level.append(a_cv)

    def geq(c, v, t):
        if t <= 1:
            return true_lit
        return level[c][v][t]

    # Backward colour-c arc u->v forces lvl_c(u) < lvl_c(v).
    for c, cap in enumerate(caps):
        arcs = canonical_poset_arcs(depth, c)
        for u in range(order):
            for v in arcs[u]:
                back = before(v, u)
                for t in range(1, cap):
                    clause = [-back, geq(c, v, t + 1)]
                    lu = geq(c, u, t)
                    if lu != true_lit:
                        clause.append(-lu)
                    _append_clause(cnf, clause, true_lit)
                clause = [-back]
                lu = geq(c, u, cap)
                if lu != true_lit:
                    clause.append(-lu)
                _append_clause(cnf, clause, true_lit)

    return cnf, key_bits, order, bit_count, len(compare_cache)


def _key_value(model_set, bits):
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit in model_set)
    return value


def decide_caps_positional(
    depth,
    caps,
    solver_type=Cadical153,
    conf_budget=None,
    range_keys=False,
    distinct_keys=False,
):
    cnf, key_bits, order, bit_count, compare_count = build_cnf(
        depth,
        caps,
        range_keys=range_keys,
        distinct_keys=distinct_keys,
    )
    solver = solver_type(bootstrap_with=cnf.clauses)
    if conf_budget is not None and hasattr(solver, "conf_budget"):
        solver.conf_budget(conf_budget)
        sat = solver.solve_limited(expect_interrupt=True)
    else:
        sat = solver.solve()

    witness = None
    heights = None
    if sat:
        model = set(solver.get_model())
        keys = [_key_value(model, key_bits[v]) for v in range(order)]
        witness = sorted(range(order), key=lambda v: (keys[v], v))
        profile = pod_profile(witness, depth)
        heights = tuple(profile["layer_heights"])
        assert all(h <= cap for h, cap in zip(heights, caps)), (heights, caps)
    solver.delete()
    return {
        "depth": depth,
        "caps": tuple(caps),
        "product": caps[0] * caps[1] * caps[2],
        "num_vars": cnf.nv,
        "num_clauses": len(cnf.clauses),
        "bit_count": bit_count,
        "comparators": compare_count,
        "range_keys": range_keys,
        "distinct_keys": distinct_keys,
        "conf_budget": conf_budget,
        "sat": sat,
        "verified_heights": heights,
        "witness_order": witness,
    }


def minimum_layer_product(depth, max_cap, solver_type=Cadical153, verbose=False):
    candidates = sorted(
        itertools.product(range(1, max_cap + 1), repeat=3),
        key=lambda caps: (caps[0] * caps[1] * caps[2], caps),
    )
    for caps in candidates:
        result = decide_caps_positional(depth, caps, solver_type)
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
    parser.add_argument("--conf-budget", type=int)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--range-keys", action="store_true")
    parser.add_argument("--distinct-keys", action="store_true")
    args = parser.parse_args()
    solver = Minisat22 if args.minisat else Cadical153

    if args.minimum:
        result = minimum_layer_product(
            args.depth, args.max_cap, solver, verbose=True
        )
    elif args.caps is not None:
        if args.build_only:
            cnf, _, order, bit_count, compare_count = build_cnf(
                args.depth,
                tuple(args.caps),
                range_keys=args.range_keys,
                distinct_keys=args.distinct_keys,
            )
            result = {
                "depth": args.depth,
                "caps": tuple(args.caps),
                "product": args.caps[0] * args.caps[1] * args.caps[2],
                "order": order,
                "bit_count": bit_count,
                "comparators": compare_count,
                "num_vars": cnf.nv,
                "num_clauses": len(cnf.clauses),
                "range_keys": args.range_keys,
                "distinct_keys": args.distinct_keys,
            }
        else:
            result = decide_caps_positional(
                args.depth,
                tuple(args.caps),
                solver_type=solver,
                conf_budget=args.conf_budget,
                range_keys=args.range_keys,
                distinct_keys=args.distinct_keys,
            )
    else:
        parser.error("pass --caps a b c or --minimum")
    print({k: v for k, v in result.items() if k != "witness_order"})


if __name__ == "__main__":
    main()
