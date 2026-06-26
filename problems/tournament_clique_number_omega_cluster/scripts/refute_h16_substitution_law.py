#!/usr/bin/env python3
"""Exact certificate refuting the proposed omega_vec substitution value law.

The proposed identity was

    omega_vec(S[H]) = omega_vec(S) + omega_vec(H) - 1.

This script verifies a counterexample with S=C3 and |H|=7:

    omega_vec(C3) = omega_vec(H) = 2,
    omega_vec(C3[H]) = 4, not 3.

The upper bounds use explicit orders.  The product lower bound is checked with
two distinct no-K4 CNF formulations and two SAT solvers.  An optional
nauty/gentourng scan proves that no smaller H refutes the formula with outer
factor C3.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import time

import networkx as nx
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

import core
from lexlib import C3, lex_substitute


H7 = (
    7,
    [
        (0, 1), (0, 2), (3, 0), (4, 0), (0, 5), (6, 0),
        (1, 2), (1, 3), (1, 4), (5, 1), (6, 1),
        (2, 3), (2, 4), (2, 5), (6, 2),
        (3, 4), (5, 3), (3, 6),
        (4, 5), (4, 6), (5, 6),
    ],
)


def tournament_arc_dict(n, arcs):
    beats = core.beats_matrix(n, arcs)
    return {(u, v): beats[u][v] for u in range(n) for v in range(n) if u != v}


def directed_triangle(n, arcs):
    beats = core.beats_matrix(n, arcs)
    for a, b, c in itertools.combinations(range(n), 3):
        if beats[a][b] and beats[b][c] and beats[c][a]:
            return [a, b, c]
        if beats[a][c] and beats[c][b] and beats[b][a]:
            return [a, c, b]
    return None


def identity_backedges(n, arcs):
    beats = core.beats_matrix(n, arcs)
    return [(u, v) for u in range(n) for v in range(u + 1, n) if beats[v][u]]


def delete_vertex(n, arcs, vertex):
    keep = [u for u in range(n) if u != vertex]
    return core.subtournament(n, arcs, keep)


def transitive_order(beats, vertices):
    """Return source-to-sink order if the induced tournament is transitive."""
    outdegree = {
        u: sum(beats[u][v] for v in vertices if v != u)
        for u in vertices
    }
    if sorted(outdegree.values()) != list(range(len(vertices))):
        return None
    order = sorted(vertices, key=lambda u: -outdegree[u])
    if all(beats[order[i]][order[j]]
           for i in range(len(order))
           for j in range(i + 1, len(order))):
        return order
    return None


class OrderVariables:
    """One Boolean variable per unordered pair; lit(u,v) means u precedes v."""

    def __init__(self, n):
        self.n = n
        self.pair_var = {}
        next_var = 1
        for u in range(n):
            for v in range(u + 1, n):
                self.pair_var[(u, v)] = next_var
                next_var += 1

    def lit(self, u, v):
        if u < v:
            return self.pair_var[(u, v)]
        return -self.pair_var[(v, u)]

    def transitivity_clauses(self):
        clauses = []
        for a, b, c in itertools.combinations(range(self.n), 3):
            clauses.append([-self.lit(a, b), -self.lit(b, c), self.lit(a, c)])
            clauses.append([-self.lit(a, c), -self.lit(c, b), self.lit(a, b)])
        return clauses

    def decode(self, model):
        true_literals = {x for x in model if x > 0}

        def precedes(u, v):
            literal = self.lit(u, v)
            return literal in true_literals if literal > 0 else -literal not in true_literals

        predecessor_count = {
            v: sum(precedes(u, v) for u in range(self.n) if u != v)
            for v in range(self.n)
        }
        order = sorted(range(self.n), key=predecessor_count.get)
        assert all(precedes(order[i], order[j])
                   for i in range(self.n)
                   for j in range(i + 1, self.n))
        return order


def build_no_k_clique_cnf_chain(n, arcs, k):
    """CNF 1: forbid the consecutive reversed chain of each transitive k-set."""
    variables = OrderVariables(n)
    cnf = CNF(from_clauses=variables.transitivity_clauses())
    beats = core.beats_matrix(n, arcs)
    forbidden = 0
    for vertices in itertools.combinations(range(n), k):
        order = transitive_order(beats, vertices)
        if order is None:
            continue
        cnf.append([variables.lit(order[i], order[i + 1]) for i in range(k - 1)])
        forbidden += 1
    return cnf, variables, forbidden


def build_no_k_clique_cnf_all_pairs(n, arcs, k):
    """CNF 2: directly forbid all pairwise-backward literals on each k-set."""
    variables = OrderVariables(n)
    cnf = CNF(from_clauses=variables.transitivity_clauses())
    beats = core.beats_matrix(n, arcs)
    arc = tournament_arc_dict(n, arcs)
    forbidden = 0
    for vertices in itertools.combinations(range(n), k):
        if transitive_order(beats, vertices) is None:
            continue
        clause = []
        for u, v in itertools.combinations(vertices, 2):
            # If u->v, this pair is backward exactly when v precedes u.
            backward = variables.lit(v, u) if arc[(u, v)] else variables.lit(u, v)
            clause.append(-backward)
        cnf.append(clause)
        forbidden += 1
    return cnf, variables, forbidden


def solve_cnf(builder, solver_class, n, arcs, k):
    cnf, variables, forbidden = builder(n, arcs, k)
    started = time.time()
    with solver_class(bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    elapsed = time.time() - started
    order = variables.decode(model) if model is not None else None
    if order is not None:
        assert core.omega_of_order(n, arcs, order) < k
    return {
        "sat": sat,
        "forbidden_transitive_sets": forbidden,
        "clauses": len(cnf.clauses),
        "seconds": round(elapsed, 6),
        "order": order,
        "order_clique": core.omega_of_order(n, arcs, order) if order else None,
    }


def digraph(n, arcs):
    graph = nx.DiGraph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(arcs)
    return graph


def ac7_c3():
    ac7 = (
        7,
        [(i, (i + d) % 7) for i in range(7) for d in {1, 2, 4}],
    )
    return lex_substitute(ac7, C3)


def ac4_21():
    generators = {1, 2, 4, 7, 8, 9, 11, 15, 16, 18}
    return (
        21,
        [(i, (i + d) % 21) for i in range(21) for d in generators],
    )


def gentourng_classes(n):
    if n == 1:
        yield []
        return
    pairs = list(itertools.combinations(range(n), 2))
    proc = subprocess.run(
        ["gentourng", str(n)],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in proc.stdout.splitlines():
        bits = line.strip()
        if not bits:
            continue
        yield [
            (u, v) if bit == "1" else (v, u)
            for bit, (u, v) in zip(bits, pairs)
        ]


def has_width_at_most_two(n, arcs):
    """SAT iff some order has triangle-free backedge graph."""
    result = solve_cnf(
        build_no_k_clique_cnf_chain,
        Cadical153,
        n,
        arcs,
        3,
    )
    return result["sat"]


def scan_c3_inner_minimality(max_inner_order=7):
    """Exhaust all H up to max_inner_order and test C3[H] against H16."""
    records = []
    for n in range(1, max_inner_order + 1):
        classes = 0
        nontransitive_width_two = 0
        counterexamples = 0
        counterexample_classes = []
        for class_index, arcs in enumerate(gentourng_classes(n), start=1):
            classes += 1
            if directed_triangle(n, arcs) is None:
                continue
            if not has_width_at_most_two(n, arcs):
                continue
            nontransitive_width_two += 1
            product_n, product_arcs = lex_substitute(C3, (n, arcs))
            no_k4 = solve_cnf(
                build_no_k_clique_cnf_chain,
                Cadical153,
                product_n,
                product_arcs,
                4,
            )
            if not no_k4["sat"]:
                counterexamples += 1
                counterexample_classes.append(class_index)
        records.append({
            "inner_order": n,
            "isomorphism_classes": classes,
            "nontransitive_omega_vec_2_classes": nontransitive_width_two,
            "c3_product_counterexamples": counterexamples,
            "counterexample_class_indices": counterexample_classes,
        })
    return records


def verify(scan_minimality):
    n_h, arcs_h = H7
    assert core.is_tournament(n_h, arcs_h)
    h_identity_order = list(range(n_h))
    h_identity_width = core.omega_of_order(n_h, arcs_h, h_identity_order)
    h_triangle = directed_triangle(n_h, arcs_h)
    assert h_identity_width == 2
    assert h_triangle is not None
    assert core.omega_vec(n_h, arcs_h, method="bruteforce") == 2
    h_deletion_triangles = [
        directed_triangle(*delete_vertex(n_h, arcs_h, vertex))
        for vertex in range(n_h)
    ]
    assert all(triangle is not None for triangle in h_deletion_triangles)
    assert core.omega_vec(*C3, method="bruteforce") == 2

    n_product, arcs_product = lex_substitute(C3, H7)
    identity_product_width = core.omega_of_order(
        n_product,
        arcs_product,
        list(range(n_product)),
    )
    assert identity_product_width == 4

    product_no_k4_chain = solve_cnf(
        build_no_k_clique_cnf_chain,
        Cadical153,
        n_product,
        arcs_product,
        4,
    )
    product_no_k4_pairs = solve_cnf(
        build_no_k_clique_cnf_all_pairs,
        Minisat22,
        n_product,
        arcs_product,
        4,
    )
    assert not product_no_k4_chain["sat"]
    assert not product_no_k4_pairs["sat"]

    product_no_k5_chain = solve_cnf(
        build_no_k_clique_cnf_chain,
        Cadical153,
        n_product,
        arcs_product,
        5,
    )
    product_no_k5_pairs = solve_cnf(
        build_no_k_clique_cnf_all_pairs,
        Minisat22,
        n_product,
        arcs_product,
        5,
    )
    assert product_no_k5_chain["sat"]
    assert product_no_k5_pairs["sat"]
    assert product_no_k5_chain["order_clique"] == 4
    assert product_no_k5_pairs["order_clique"] == 4

    c3_c3 = lex_substitute(C3, C3)
    c3_c3_no_k3 = solve_cnf(
        build_no_k_clique_cnf_chain,
        Cadical153,
        *c3_c3,
        3,
    )
    c3_c3_no_k4 = solve_cnf(
        build_no_k_clique_cnf_chain,
        Cadical153,
        *c3_c3,
        4,
    )
    assert not c3_c3_no_k3["sat"]
    assert c3_c3_no_k4["sat"]
    assert c3_c3_no_k4["order_clique"] == 3

    product_deletions = []
    for vertex in range(n_product):
        deleted_n, deleted_arcs = delete_vertex(n_product, arcs_product, vertex)
        no_k4 = solve_cnf(
            build_no_k_clique_cnf_chain,
            Cadical153,
            deleted_n,
            deleted_arcs,
            4,
        )
        assert no_k4["sat"]
        assert no_k4["order_clique"] == 3
        product_deletions.append({
            "deleted_vertex": vertex,
            "width_3_order": no_k4["order"],
        })

    n_reverse, arcs_reverse = lex_substitute(H7, C3)
    reverse_no_k4 = solve_cnf(
        build_no_k_clique_cnf_chain,
        Cadical153,
        n_reverse,
        arcs_reverse,
        4,
    )
    assert reverse_no_k4["sat"]
    assert reverse_no_k4["order_clique"] == 3

    product_graph = digraph(n_product, arcs_product)
    comparison = {
        "isomorphic_to_AC7_C3": nx.is_isomorphic(
            product_graph,
            digraph(*ac7_c3()),
        ),
        "isomorphic_to_AC4_21": nx.is_isomorphic(
            product_graph,
            digraph(*ac4_21()),
        ),
    }

    result = {
        "claim": "omega_vec(C3[H7]) != omega_vec(C3)+omega_vec(H7)-1",
        "H7": {
            "arcs": arcs_h,
            "directed_triangle": h_triangle,
            "identity_backedge_edges": identity_backedges(n_h, arcs_h),
            "identity_backedge_degree_sequence": sorted(
                dict(nx.Graph(identity_backedges(n_h, arcs_h)).degree()).values()
            ),
            "identity_order_clique": h_identity_width,
            "exact_omega_vec": 2,
            "every_deletion_contains_directed_triangle": True,
            "deletion_triangle_witnesses": h_deletion_triangles,
        },
        "C3": {"exact_omega_vec": 2},
        "C3_of_H7": {
            "order": n_product,
            "identity_order_clique": identity_product_width,
            "no_K4_chain_Cadical": product_no_k4_chain,
            "no_K4_all_pairs_Minisat": product_no_k4_pairs,
            "no_K5_chain_Cadical": product_no_k5_chain,
            "no_K5_all_pairs_Minisat": product_no_k5_pairs,
            "exact_omega_vec": 4,
            "H16_predicted_value": 3,
            "is_4_omega_vec_critical": True,
            "all_deletions_exact_omega_vec": 3,
            "deletion_certificates": product_deletions,
            **comparison,
        },
        "H7_of_C3": {
            "order": n_reverse,
            "no_K4_chain_Cadical": reverse_no_k4,
            "exact_omega_vec": 3,
        },
    }
    if scan_minimality:
        result["C3_inner_minimality_scan"] = scan_c3_inner_minimality()
        assert all(
            row["c3_product_counterexamples"] == 0
            for row in result["C3_inner_minimality_scan"][:-1]
        )
        assert result["C3_inner_minimality_scan"][-1]["c3_product_counterexamples"] > 0
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-minimality-scan",
        action="store_true",
        help="skip the exhaustive gentourng scan for inner orders through 7",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "h16_counterexample.json",
        ),
    )
    args = parser.parse_args()
    result = verify(not args.skip_minimality_scan)
    with open(args.output, "w") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
