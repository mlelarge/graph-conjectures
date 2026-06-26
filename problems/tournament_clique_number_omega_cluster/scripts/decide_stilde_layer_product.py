"""Exact SAT decisions for the canonical three-poset layer product of B_k.

For B_k=C3^k[TT_1] and an order pi, q_c(pi) is the largest chain of the
canonical poset P_c that appears backward in pi.  This script decides whether
there is an order satisfying q_c <= cap_c for a prescribed cap triple.

The product parameter

    L_k = min_pi q_0(pi) q_1(pi) q_2(pi)

satisfies L_k <= 2^k by the ordinary lexicographic order.  The finite target
is to rule out every cap triple with product below 2^k.
"""

from __future__ import annotations

import argparse
import functools
import itertools

from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

from stilde_pod_profiles import arc_colour, pod_profile


def canonical_poset_arcs(depth, colour):
    order = 3**depth
    arcs = [[] for _ in range(order)]
    for left in range(order):
        for right in range(order):
            if left != right and arc_colour(left, right, depth) == colour:
                # Recover the direction of the cyclic tournament arc.
                x, y = left, right
                left_digits = []
                right_digits = []
                for _ in range(depth):
                    left_digits.append(x % 3)
                    right_digits.append(y % 3)
                    x //= 3
                    y //= 3
                for a, b in zip(reversed(left_digits), reversed(right_digits)):
                    if a != b:
                        if b == (a + 1) % 3:
                            arcs[left].append(right)
                        break
    return arcs


def tournament_arcs(depth):
    order = 3**depth
    arcs = [[] for _ in range(order)]
    for left in range(order):
        left_word = []
        value = left
        for _ in range(depth):
            left_word.append(value % 3)
            value //= 3
        left_word.reverse()
        for right in range(order):
            if left == right:
                continue
            right_word = []
            value = right
            for _ in range(depth):
                right_word.append(value % 3)
                value //= 3
            right_word.reverse()
            for a, b in zip(left_word, right_word):
                if a != b:
                    if b == (a + 1) % 3:
                        arcs[left].append(right)
                    break
    return arcs


def chains_of_size(arcs, size):
    """Enumerate oriented chains in a transitively closed poset."""
    result = []

    def visit(chain, candidates):
        if len(chain) == size:
            result.append(tuple(chain))
            return
        for vertex in candidates:
            visit(chain + [vertex], [x for x in candidates if x in arcs[vertex]])

    for start in range(len(arcs)):
        visit([start], arcs[start])
    return result


def decide_caps(depth, caps, solver_type=Cadical153, clique_cap=None):
    order = 3**depth
    pair_var = {}
    next_var = 0

    def lit(left, right):
        nonlocal next_var
        if (left, right) in pair_var:
            return pair_var[(left, right)]
        if (right, left) in pair_var:
            return -pair_var[(right, left)]
        next_var += 1
        pair_var[(left, right)] = next_var
        return next_var

    for left in range(order):
        for right in range(left + 1, order):
            lit(left, right)

    cnf = CNF()
    for left, middle, right in itertools.permutations(range(order), 3):
        cnf.append([-lit(left, middle), -lit(middle, right), lit(left, right)])

    chain_counts = []
    for colour, cap in enumerate(caps):
        arcs = canonical_poset_arcs(depth, colour)
        chains = chains_of_size(arcs, cap + 1)
        chain_counts.append(len(chains))
        for chain in chains:
            # A chain is entirely backward exactly when every consecutive
            # relation is reversed by the total order.
            cnf.append([lit(chain[i], chain[i + 1]) for i in range(cap)])

    full_chain_count = None
    if clique_cap is not None:
        full_chains = chains_of_size(tournament_arcs(depth), clique_cap + 1)
        full_chain_count = len(full_chains)
        for chain in full_chains:
            cnf.append(
                [lit(chain[i], chain[i + 1]) for i in range(clique_cap)]
            )

    solver = solver_type(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    witness = None
    if sat:
        model = set(solver.get_model())

        def precedes(left, right):
            value = lit(left, right)
            return value in model if value > 0 else -value not in model

        witness = sorted(
            range(order),
            key=functools.cmp_to_key(
                lambda left, right: (
                    0
                    if left == right
                    else (-1 if precedes(left, right) else 1)
                )
            ),
        )
        profile = pod_profile(witness, depth)
        assert all(
            height <= cap
            for height, cap in zip(profile["layer_heights"], caps)
        )
    solver.delete()
    return {
        "depth": depth,
        "caps": list(caps),
        "product": caps[0] * caps[1] * caps[2],
        "chain_counts": chain_counts,
        "clique_cap": clique_cap,
        "full_chain_count": full_chain_count,
        "sat": sat,
        "witness_order": witness,
    }


def decide_below_lex_product(depth, cross_check=False):
    threshold = 2**depth
    results = []
    for caps in itertools.product(range(1, threshold + 1), repeat=3):
        if caps[0] * caps[1] * caps[2] >= threshold:
            continue
        result = decide_caps(depth, caps, Cadical153)
        if cross_check:
            check = decide_caps(depth, caps, Minisat22)
            assert check["sat"] == result["sat"]
        results.append(result)
    return results


def decide_joint_minimum(depth, clique_cap, cross_check=False):
    candidates = sorted(
        itertools.product(range(1, clique_cap + 1), repeat=3),
        key=lambda caps: (caps[0] * caps[1] * caps[2], caps),
    )
    results = []
    first_product = None
    for caps in candidates:
        product = caps[0] * caps[1] * caps[2]
        if first_product is not None and product > first_product:
            break
        result = decide_caps(
            depth, caps, Cadical153, clique_cap=clique_cap
        )
        if cross_check:
            check = decide_caps(
                depth, caps, Minisat22, clique_cap=clique_cap
            )
            assert check["sat"] == result["sat"]
        results.append(result)
        if result["sat"]:
            first_product = product
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--cross-check", action="store_true")
    parser.add_argument("--clique-cap", type=int)
    args = parser.parse_args()

    if args.clique_cap is not None:
        results = decide_joint_minimum(
            args.depth, args.clique_cap, args.cross_check
        )
        satisfiable = [result for result in results if result["sat"]]
        minimum = min(
            (result["product"] for result in satisfiable),
            default=None,
        )
        print(
            f"B_{args.depth}: full clique cap {args.clique_cap}; "
            f"checked {len(results)} cap triples; joint minimum={minimum}"
        )
        for result in satisfiable:
            print(result)
        return

    results = decide_below_lex_product(args.depth, args.cross_check)
    satisfiable = [result for result in results if result["sat"]]
    print(
        f"B_{args.depth}: checked {len(results)} cap triples with product "
        f"< {2**args.depth}; SAT={len(satisfiable)}"
    )
    for result in satisfiable:
        print(result)


if __name__ == "__main__":
    main()
