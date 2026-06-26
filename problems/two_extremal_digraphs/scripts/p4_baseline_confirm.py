#!/usr/bin/env python3
"""Confirm the calibrated lambda=3 overlap witness via the oracle, and
identify the witnessing pair(s) realizing lambda_D=3 (3 arc-disjoint paths)."""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from fd_flip_cube import simple_directed_cycles  # noqa: E402
from step1b_fd_connectivity import vertex_connectivity  # noqa: E402


def cycle_arcs(cycle):
    return frozenset((cycle[i], cycle[(i + 1) % len(cycle)])
                     for i in range(len(cycle)))


def main():
    n = 9
    forest = ((0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8))
    component = tuple(v // 3 for v in range(n))
    bit = (0, 1, 0) * 3
    omega = tuple((0, x1, x2) for x1, x2 in itertools.product((0, 1), repeat=2))
    cycles = ((0, 3, 8, 6), (0, 3, 7), (0, 2, 4, 8, 6), (1, 3, 8, 5))

    def bad_points(cycle):
        return frozenset(
            flip for flip in omega
            if len({bit[v] ^ flip[component[v]] for v in cycle}) == 1)

    cyc_sets = [cycle_arcs(c) for c in cycles]
    singles = frozenset().union(*cyc_sets)
    digon_arcs = frozenset(a for u, v in forest for a in ((u, v), (v, u)))
    arcs = singles | digon_arcs

    print("# BASELINE overlap witness (calibrated lambda=3)")
    print(f"  n={n}")
    print(f"  cover flips: {[sorted(bad_points(c)) for c in cycles]}")
    print(f"  covered Omega == full: "
          f"{ {next(iter(bad_points(c))) for c in cycles} == set(omega)}")
    print(f"  all pure-point: {all(len(bad_points(c)) == 1 for c in cycles)}")
    print(f"  overlap (sum>union): "
          f"{sum(map(len, cyc_sets))} > {len(singles)} "
          f"= {sum(map(len, cyc_sets)) > len(singles)}")
    print(f"  is_eulerian_deg: {H.is_eulerian_deg(n, arcs)}")
    print(f"  vertex_connectivity (kappa): {vertex_connectivity(n, arcs)}")
    print(f"  chi_vec: {H.chi_vec(n, arcs)}")
    print(f"  criticality (all chi(arcs-a)<=2): "
          f"{all(H.chi_vec(n, arcs - {a}) <= 2 for a in arcs)}")
    lam = H.lambda_D(n, arcs)
    print(f"  lambda_D: {lam}")
    print(f"  is_2extremal: {H.is_2extremal(n, arcs)}")

    # identify witnessing pairs with maxflow_unit >= 3
    pairs3 = []
    maxf = 0
    for s, t in itertools.permutations(range(n), 2):
        f = H._maxflow_unit(n, arcs, s, t)
        maxf = max(maxf, f)
        if f >= 3:
            pairs3.append((s, t, f))
    print(f"  max over all pairs of maxflow_unit: {maxf}")
    print(f"  pairs realizing >=3 arc-disjoint paths: {len(pairs3)}")
    for p in pairs3[:10]:
        print(f"    {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
