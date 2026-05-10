#!/usr/bin/env python3
"""
Phase 4 cycle clique-blowup enumerator and verifier.

Constructs the clique blowup C_{2r+1}[K_{a_1}, ..., K_{a_{2r+1}}] of an odd
cycle, computes its exact graph-theoretic invariants (n, m, omega, alpha, and
a chromatic-number lower bound), and either enumerates candidate weight
tuples or verifies a single instance. Operates entirely on graph theory; no
SAT, no biplanarity oracle. Used to provide a verifiable graph-theoretic
layer against which SMS results can be cross-checked.

Subcommands:
    enumerate    List weight tuples with n <= MAX_N, omega <= MAX_OMEGA,
                 chi_lb >= MIN_CHI, and m <= 6n - 12 (the biplanar edge bound).
    verify       Build a specific blowup, report its invariants, optionally
                 emit graph6.

Examples:
    python cycle_blowup.py enumerate --max-n 30
    python cycle_blowup.py verify --weights 4,4,4,4,3
    python cycle_blowup.py verify --weights 4,4,4,4,4,4,4 --emit-graph6
"""
import argparse
import itertools
import math
import sys

import networkx as nx


def cycle_blowup(weights):
    """Return C_{2r+1}[K_{a_1}, ..., K_{a_{2r+1}}] as an nx.Graph.

    Vertices are pairs (i, j) for 0 <= i < L, 0 <= j < weights[i]. Edges:
    every intra-fibre pair (clique on each K_{a_i}); every cross-fibre pair
    between cyclically adjacent fibres.
    """
    L = len(weights)
    if L < 3 or L % 2 == 0:
        raise ValueError(f"weights length must be odd and >= 3 (got {L})")
    if any(a < 1 for a in weights):
        raise ValueError(f"all weights must be >= 1 (got {weights})")

    G = nx.Graph()
    fibres = [[(i, j) for j in range(a)] for i, a in enumerate(weights)]
    for fibre in fibres:
        G.add_nodes_from(fibre)
    for fibre in fibres:
        for u, v in itertools.combinations(fibre, 2):
            G.add_edge(u, v)
    for i in range(L):
        for u in fibres[i]:
            for v in fibres[(i + 1) % L]:
                G.add_edge(u, v)
    return G


def invariants(weights):
    """Closed-form (n, m, omega, alpha, chi_lb) for the cycle clique blowup.

    chi_lb = max(omega, ceil(n / r)). Both terms are valid lower bounds on
    the chromatic number; the max is the standard Hoffman/clique-cover
    combination. The exact chromatic number can equal chi_lb for many
    weight patterns but is not guaranteed to in general.
    """
    L = len(weights)
    if L < 3 or L % 2 == 0:
        raise ValueError(f"weights length must be odd and >= 3 (got {L})")
    r = (L - 1) // 2  # alpha of an odd cycle clique blowup
    n = sum(weights)
    m_intra = sum(a * (a - 1) // 2 for a in weights)
    m_inter = sum(weights[i] * weights[(i + 1) % L] for i in range(L))
    m = m_intra + m_inter
    omega = max(weights[i] + weights[(i + 1) % L] for i in range(L))
    edge_budget = 6 * n - 12 if n >= 2 else 0
    return {
        "weights": tuple(weights),
        "L": L,
        "r": r,
        "n": n,
        "m": m,
        "omega": omega,
        "alpha": r,
        "chi_lb": max(omega, math.ceil(n / r)),
        "edge_budget_6n_minus_12": edge_budget,
        "edge_slack": edge_budget - m,
    }


def canonical_weights(weights):
    """Lex-min representative of the D_L orbit (rotations + reflection)."""
    L = len(weights)
    rotations = [tuple(weights[i:] + weights[:i]) for i in range(L)]
    rev = tuple(reversed(weights))
    reflections = [tuple(rev[i:] + rev[:i]) for i in range(L)]
    return min(rotations + reflections)


def compositions(total, parts, lo, hi):
    """Yield k-tuples summing to `total` with each entry in [lo, hi]."""
    if parts == 1:
        if lo <= total <= hi:
            yield (total,)
        return
    for x in range(lo, hi + 1):
        rem = total - x
        if (parts - 1) * lo <= rem <= (parts - 1) * hi:
            for rest in compositions(rem, parts - 1, lo, hi):
                yield (x,) + rest


def enumerate_blowups(max_n=30, max_omega=8, min_chi=10):
    """Enumerate candidate weighted blowups under the Phase 4 constraints.

    Constraints:
        omega <= max_omega   (max_omega = 8 forces K_9-freeness)
        chi_lb >= min_chi    (forces n >= min_chi * r since omega < min_chi)
        m <= 6n - 12         (biplanarity edge bound)
        n <= max_n
    """
    seen = set()
    results = []

    # Each a_i + a_neighbour <= max_omega and each a_i >= 1, so a_i <= max_omega - 1.
    max_weight = max_omega - 1

    # When omega < min_chi (forced here, since max_omega < min_chi typically),
    # chi_lb >= min_chi reduces to ceil(n/r) >= min_chi, i.e.
    # n >= (min_chi - 1) * r + 1. That also bounds r above.
    if max_omega >= min_chi:
        # Generic bound: any n >= min_chi works since omega alone can carry it.
        n_min_for = lambda r: min_chi
        max_r = (max_n - 1) // 1
    else:
        n_min_for = lambda r: (min_chi - 1) * r + 1
        max_r = (max_n - 1) // (min_chi - 1)
    odd_lengths = [2 * r + 1 for r in range(2, max_r + 1)]

    for L in odd_lengths:
        r = (L - 1) // 2
        n_min = n_min_for(r)
        for n in range(n_min, max_n + 1):
            for weights in compositions(n, L, 1, max_weight):
                # Adjacent-pair sum constraint, cheap pre-filter.
                if max(weights[i] + weights[(i + 1) % L] for i in range(L)) > max_omega:
                    continue
                inv = invariants(weights)
                if inv["chi_lb"] < min_chi:
                    continue
                if inv["m"] > inv["edge_budget_6n_minus_12"]:
                    continue
                key = canonical_weights(weights)
                if key in seen:
                    continue
                seen.add(key)
                inv["weights"] = key
                results.append(inv)

    results.sort(key=lambda d: (d["n"], -d["edge_slack"], d["weights"]))
    return results


def cross_check_with_networkx(weights, expected):
    """Verify formula-derived invariants against networkx-computed ones.

    Computes omega via maximum clique enumeration and alpha via the same on
    the complement. For the small graphs of interest (n <= 30) this is fast.
    """
    G = cycle_blowup(weights)
    omega_nx = max(len(c) for c in nx.find_cliques(G))
    alpha_nx = max(len(c) for c in nx.find_cliques(nx.complement(G)))
    return {
        "n_actual": G.number_of_nodes(),
        "m_actual": G.number_of_edges(),
        "omega_actual": omega_nx,
        "alpha_actual": alpha_nx,
        "n_match": G.number_of_nodes() == expected["n"],
        "m_match": G.number_of_edges() == expected["m"],
        "omega_match": omega_nx == expected["omega"],
        "alpha_match": alpha_nx == expected["alpha"],
    }


def cmd_enumerate(args):
    rs = enumerate_blowups(args.max_n, args.max_omega, args.min_chi)
    print(
        f"# {len(rs)} candidate blowups: max_n={args.max_n}, "
        f"max_omega={args.max_omega}, min_chi={args.min_chi}"
    )
    cols = ["weights", "L", "r", "n", "m", "omega", "alpha",
            "chi_lb", "edge_budget_6n_minus_12", "edge_slack"]
    print("# " + "\t".join(cols))
    for d in rs:
        wstr = ",".join(map(str, d["weights"]))
        row = [wstr] + [str(d[k]) for k in cols[1:]]
        print("\t".join(row))


def cmd_verify(args):
    weights = tuple(int(x) for x in args.weights.split(","))
    inv = invariants(weights)
    check = cross_check_with_networkx(weights, inv)
    print(f"weights: {inv['weights']}")
    for k in ("L", "r", "n", "m", "omega", "alpha", "chi_lb",
              "edge_budget_6n_minus_12", "edge_slack"):
        print(f"{k}: {inv[k]}")
    print("--- networkx cross-check ---")
    for k, v in check.items():
        print(f"{k}: {v}")
    if not all(check[k] for k in ("n_match", "m_match", "omega_match", "alpha_match")):
        print("MISMATCH between formula and networkx", file=sys.stderr)
        sys.exit(1)
    if args.emit_graph6:
        H = nx.convert_node_labels_to_integers(cycle_blowup(weights))
        sys.stdout.write(nx.to_graph6_bytes(H, header=False).decode("ascii"))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("enumerate", help="enumerate candidate weight tuples")
    pe.add_argument("--max-n", type=int, default=30)
    pe.add_argument("--max-omega", type=int, default=8)
    pe.add_argument("--min-chi", type=int, default=10)
    pe.set_defaults(func=cmd_enumerate)

    pv = sub.add_parser("verify", help="build and verify a single blowup")
    pv.add_argument(
        "--weights",
        required=True,
        help="comma-separated weights, e.g. 4,4,4,4,3",
    )
    pv.add_argument(
        "--emit-graph6",
        action="store_true",
        help="also write the graph in graph6 format to stdout",
    )
    pv.set_defaults(func=cmd_verify)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
