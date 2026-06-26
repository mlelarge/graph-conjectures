"""Ground CONJECTURE-A(3): every 3-omega_vec-critical tournament admits an OPTIMAL
ordering (omega(backedge)==3) whose backedge graph has independence number alpha<=3.

For each witness compute m(T) = min over OPTIMAL orders of alpha(backedge graph).
alpha = clique number of the complement of the backedge graph.

n<=8: exhaustive over all n! orders.
n=9,11 (vertex-transitive): large random sample of orders + symmetry note.
"""
from __future__ import annotations
import itertools, json, random, sys
import networkx as nx
from scripts import core, constructions


def alpha_of_graph(g):
    comp = nx.complement(g)
    return core.clique_number(comp)


def min_alpha_exhaustive(n, arcs):
    """Exact: enumerate all n! orders, among OPTIMAL ones (omega==3) take min alpha.
    Returns (min_alpha_over_optimal, num_optimal, global_omega_vec)."""
    beats = core.beats_matrix(n, arcs)
    best_omega = n
    best_alpha = None
    num_opt = 0
    # first pass to find omega_vec
    omega_vec = core.omega_vec(n, arcs)
    for order in itertools.permutations(range(n)):
        g = core.backedge_graph(n, arcs, order)
        w = core.clique_number(g)
        if w == omega_vec:
            num_opt += 1
            a = alpha_of_graph(g)
            if best_alpha is None or a < best_alpha:
                best_alpha = a
    return best_alpha, num_opt, omega_vec


def min_alpha_sampled(n, arcs, samples, seed=0):
    """Sampled: random orders; among OPTIMAL ones take min alpha."""
    rng = random.Random(seed)
    omega_vec = core.omega_vec(n, arcs)
    best_alpha = None
    num_opt = 0
    base = list(range(n))
    for _ in range(samples):
        order = base[:]
        rng.shuffle(order)
        g = core.backedge_graph(n, arcs, order)
        w = core.clique_number(g)
        if w == omega_vec:
            num_opt += 1
            a = alpha_of_graph(g)
            if best_alpha is None or a < best_alpha:
                best_alpha = a
    return best_alpha, num_opt, omega_vec


def main():
    iso = json.load(open("data/iso_critical_scan.json"))
    results = {}

    # n=7 (the single iso class)
    arcs7 = [tuple(a) for a in iso["7"]["critical_examples"][0]["arcs"]]
    a7, no7, w7 = min_alpha_exhaustive(7, arcs7)
    results["7"] = {"min_alpha": a7, "num_optimal": no7, "omega_vec": w7}
    print(f"n=7   min_alpha_over_optimal={a7}  (#optimal={no7}, omega_vec={w7})")

    # n=8 (two iso classes)
    for idx in (0, 1):
        arcs8 = [tuple(a) for a in iso["8"]["critical_examples"][idx]["arcs"]]
        a8, no8, w8 = min_alpha_exhaustive(8, arcs8)
        results[f"8{'ab'[idx]}"] = {"min_alpha": a8, "num_optimal": no8, "omega_vec": w8}
        print(f"n=8{'ab'[idx]} min_alpha_over_optimal={a8}  (#optimal={no8}, omega_vec={w8})")

    # n=9: S_tilde(3), vertex-transitive
    n9, arcs9 = constructions.S_tilde(3)
    a9, no9, w9 = min_alpha_sampled(n9, arcs9, samples=40000, seed=1)
    results["9"] = {"min_alpha": a9, "num_optimal": no9, "omega_vec": w9, "method": "sampled-40000"}
    print(f"n=9   min_alpha_over_optimal={a9}  (#optimal={no9}/40000, omega_vec={w9})")

    # n=11: circulant g={1,2,3,4,6}
    circ = json.load(open("data/circulant_3critical_n11.json"))
    arcs11 = [tuple(a) for a in circ["arcs"]]
    n11 = circ["n"]
    a11, no11, w11 = min_alpha_sampled(n11, arcs11, samples=60000, seed=2)
    results["11"] = {"min_alpha": a11, "num_optimal": no11, "omega_vec": w11, "method": "sampled-60000"}
    print(f"n=11  min_alpha_over_optimal={a11}  (#optimal={no11}/60000, omega_vec={w11})")

    print("\nTABLE:", {k: v["min_alpha"] for k, v in results.items()})
    all_le3 = all(v["min_alpha"] is not None and v["min_alpha"] <= 3 for v in results.values())
    print("ALL min_alpha <= 3 :", all_le3)
    json.dump(results, open("data/conjA3_grounding.json", "w"), indent=2)


if __name__ == "__main__":
    main()
