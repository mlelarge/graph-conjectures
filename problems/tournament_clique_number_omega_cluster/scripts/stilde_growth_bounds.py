"""Rigorous growth bounds for the iterated directed-triangle family.

Write S_1 = TT_1 and S_{n+1} = C3[S_n].  The script records:

* the exact dichromatic recurrence d_{n+1} = ceil(3 d_n / 2);
* max(n, ceil(d_n^(1/3))) <= omega_vec(S_n) <= d_n;
* the first n where the cubic lower bound alone contradicts omega_vec(S_n) <= n;
* exact transitive-subtournament counts from
      F_1(x) = 1+x,  F_{n+1}(x) = 3 F_n(x)^2 - 3 F_n(x) + 1,
  and the resulting random-order first-moment upper bound.

Output: data/stilde_growth_bounds.json.
"""

from __future__ import annotations

import argparse
import json
import math
import os


HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def ceil_three_halves(value):
    return (3 * value + 1) // 2


def ceil_cuberoot(value):
    lo, hi = 0, 1
    while hi**3 < value:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**3 >= value:
            hi = mid
        else:
            lo = mid
    return hi


def next_transitive_counts(coefficients, cap):
    """Apply F -> 3F^2-3F+1, truncated to degree cap."""
    degree = min(cap, 2 * (len(coefficients) - 1))
    result = [0] * (degree + 1)
    result[0] = 1
    for r in range(1, degree + 1):
        convolution = 0
        lo = max(0, r - (len(coefficients) - 1))
        hi = min(len(coefficients) - 1, r)
        for left in range(lo, hi + 1):
            convolution += coefficients[left] * coefficients[r - left]
        old = coefficients[r] if r < len(coefficients) else 0
        result[r] = 3 * convolution - 3 * old
    return result


def first_moment_upper(coefficients):
    """If t_r/r! < 1, a random order avoids every r-clique with positive probability."""
    factorial = 1
    for r in range(1, len(coefficients)):
        factorial *= r
        if coefficients[r] < factorial:
            return r - 1
    return None


def build_report(max_n=30, count_max_n=12, count_cap=600):
    known_omega = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    rows = []
    dichromatic = 1
    first_forced_h19_failure = None
    for n in range(1, max_n + 1):
        pod_lower = ceil_cuberoot(dichromatic)
        combined_lower = max(n, pod_lower)
        if first_forced_h19_failure is None and pod_lower > n:
            first_forced_h19_failure = n
        rows.append(
            {
                "n": n,
                "order": 3 ** (n - 1),
                "dichromatic_exact": dichromatic,
                "omega_lower_linear": n,
                "omega_lower_pod": pod_lower,
                "omega_lower_combined": combined_lower,
                "omega_upper_dichromatic": dichromatic,
                "omega_exact_known": known_omega.get(n),
            }
        )
        dichromatic = ceil_three_halves(dichromatic)

    counts = [1, 1]
    count_rows = []
    for n in range(1, count_max_n + 1):
        count_rows.append(
            {
                "n": n,
                "max_transitive_size": len(counts) - 1,
                "random_order_first_moment_upper": first_moment_upper(counts),
                "counts_through_degree_12": [
                    str(value) for value in counts[: min(13, len(counts))]
                ],
            }
        )
        counts = next_transitive_counts(counts, count_cap)

    lower_base = (3 / 2) ** (1 / 3)
    upper_base = 5 ** (1 / 4)
    return {
        "family": "S~_1=TT_1; S~_{n+1}=C3[S~_n]",
        "proved_growth_constant": {
            "definition": "rho = lim_{i->infinity} omega_vec(S~_{i+1})^(1/i)",
            "exists_by": "submultiplicativity under lexicographic powers",
            "lower": lower_base,
            "upper": upper_base,
            "upper_certificate": "omega_vec(S~_5)=5",
            "vertex_count_exponent_lower": math.log(lower_base, 3),
            "vertex_count_exponent_upper": math.log(upper_base, 3),
        },
        "first_n_where_pod_lower_exceeds_h19_iterated_upper_n": (
            first_forced_h19_failure
        ),
        "bounds": rows,
        "transitive_subtournament_counts": count_rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=30)
    parser.add_argument("--count-max-n", type=int, default=12)
    parser.add_argument("--count-cap", type=int, default=600)
    args = parser.parse_args()

    report = build_report(args.max_n, args.count_max_n, args.count_cap)
    path = os.path.join(DATA, "stilde_growth_bounds.json")
    with open(path, "w", encoding="ascii") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    growth = report["proved_growth_constant"]
    print(
        "rho in "
        f"[{growth['lower']:.9f}, {growth['upper']:.9f}], "
        "vertex exponent in "
        f"[{growth['vertex_count_exponent_lower']:.9f}, "
        f"{growth['vertex_count_exponent_upper']:.9f}]"
    )
    print(
        "first forced H19 failure by S~_n:",
        report["first_n_where_pod_lower_exceeds_h19_iterated_upper_n"],
    )
    print("wrote", path)


if __name__ == "__main__":
    main()
