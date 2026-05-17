#!/usr/bin/env python3
"""Exploration of the hypothesis of Theorem 8.1 of arXiv:2506.07264.

Theorem 8.1 says: if G is a connected graph of order n with
    alpha(G) * omega(G) <= n / 17,
then min(s^+(G), s^-(G)) >= n (so the equality case in Conjecture 9.2
forces G to be a tree / tree-or-K_n).

This script answers two empirical questions on small n:

1.  For all connected graphs of order n <= 7 (graph atlas), what is
    the **empirical threshold** c*(n) such that
        alpha(G) * omega(G) <= n / c*(n)  ==>  min(s^+,s^-) >= n
    holds for every G in the corpus?  Equivalently,
        c*(n) := min over G of  n / (alpha*omega)  taken over those G
        for which  min(s^+,s^-) < n.

2.  For each n, what fraction of connected graphs satisfies the
    Thm 8.1 hypothesis  alpha*omega <= n/17 ?  (Sanity:  on small n
    this fraction is essentially 0.)

The corpus also records  min(s^+,s^-) / n  so we can scatter-plot the
slack against alpha*omega/n.

Output: writes a JSON corpus to
    problems/positive_square_energy_equality/data/alpha_omega_corpus.json
and prints a summary to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np


# -- spectral / structural primitives ----------------------------------------

def square_energies(G: nx.Graph) -> tuple[float, float]:
    """Return (s^+(G), s^-(G)) using float64 eigenvalues."""
    if G.number_of_nodes() == 0:
        return 0.0, 0.0
    A = nx.to_numpy_array(G, dtype=float)
    w = np.linalg.eigvalsh(A)
    sp = float(np.sum(w[w > 1e-9] ** 2))
    sm = float(np.sum(w[w < -1e-9] ** 2))
    return sp, sm


def alpha_omega(G: nx.Graph) -> tuple[int, int]:
    """Exact independence and clique numbers via Bron-Kerbosch.

    alpha(G) = omega(complement(G)) computed via nx.find_cliques.
    For n <= ~20 this is fast enough.
    """
    if G.number_of_nodes() == 0:
        return 0, 0
    omega = max((len(c) for c in nx.find_cliques(G)), default=1)
    H = nx.complement(G)
    alpha = max((len(c) for c in nx.find_cliques(H)), default=1)
    return alpha, omega


# -- corpus enumeration -------------------------------------------------------

def iter_connected_atlas() -> list[nx.Graph]:
    """All connected graphs on 1..7 vertices from the NetworkX graph atlas."""
    from networkx.generators.atlas import graph_atlas_g

    atlas = graph_atlas_g()
    return [G for G in atlas if G.number_of_nodes() >= 2 and nx.is_connected(G)]


def iter_random_larger(
    n_values: list[int],
    samples_per_n: int = 200,
    seed: int = 20260517,
) -> list[nx.Graph]:
    """Random connected graphs on larger n (8..14) for a coarse extension.

    For each n, sample Erdos-Renyi G(n, p) at several densities and keep
    the connected ones.  This is an *unstratified* sample; the atlas at
    n <= 7 remains the rigorous core.
    """
    rng = np.random.default_rng(seed)
    out: list[nx.Graph] = []
    densities = [0.2, 0.35, 0.5, 0.65, 0.8]
    for n in n_values:
        per_density = max(1, samples_per_n // len(densities))
        for p in densities:
            attempts = 0
            kept = 0
            while kept < per_density and attempts < per_density * 10:
                seed_i = int(rng.integers(1, 2**31 - 1))
                G = nx.erdos_renyi_graph(n, p, seed=seed_i)
                attempts += 1
                if nx.is_connected(G):
                    out.append(G)
                    kept += 1
    return out


# -- per-graph record ---------------------------------------------------------

def record(G: nx.Graph) -> dict:
    n = G.number_of_nodes()
    m = G.number_of_edges()
    sp, sm = square_energies(G)
    alpha, omega = alpha_omega(G)
    aw = alpha * omega
    return {
        "n": n,
        "m": m,
        "alpha": alpha,
        "omega": omega,
        "alpha_omega": aw,
        "aw_over_n": aw / n,
        "s_plus": sp,
        "s_minus": sm,
        "min_s": min(sp, sm),
        "min_s_over_n": min(sp, sm) / n,
        "min_s_ge_n": min(sp, sm) >= n - 1e-7,
        "min_s_ge_n_minus_1": min(sp, sm) >= n - 1 - 1e-7,
        # ratio  n / (alpha*omega)  -- meaningful only when alpha*omega > 0
        "n_over_aw": (n / aw) if aw > 0 else float("inf"),
    }


# -- analysis ----------------------------------------------------------------

def empirical_c_star(records: list[dict]) -> dict:
    """Compute the empirical threshold c* and related statistics.

    c*(n) is defined as the **smallest n/(alpha*omega) over those graphs
    that violate min(s^+,s^-) >= n**.  If no graph in the corpus violates
    that inequality, c*(n) = +inf and Theorem 8.1's hypothesis is
    *unnecessarily strong* on this corpus.

    Conversely, the **largest n/(alpha*omega) of any graph that satisfies
    min(s^+,s^-) >= n** measures how slack Thm 8.1's constant 17 is in
    the other direction:  if there are violators with n/(alpha*omega)
    much smaller than 17, then 17 is a comfortable safety margin.
    """
    by_n: dict[int, dict] = {}
    for r in records:
        n = r["n"]
        slot = by_n.setdefault(
            n,
            {
                "count": 0,
                "n": n,
                "thm81_hypothesis_count": 0,  # alpha*omega <= n/17
                "violators_min_s_lt_n": [],
                "satisfiers_min_s_ge_n": [],
            },
        )
        slot["count"] += 1
        if r["alpha_omega"] * 17 <= n:
            slot["thm81_hypothesis_count"] += 1
        if not r["min_s_ge_n"]:
            slot["violators_min_s_lt_n"].append(r["n_over_aw"])
        else:
            slot["satisfiers_min_s_ge_n"].append(r["n_over_aw"])

    summary: dict[int, dict] = {}
    for n, slot in sorted(by_n.items()):
        viol = slot["violators_min_s_lt_n"]
        sats = slot["satisfiers_min_s_ge_n"]
        # c*(n) = inf  n/(alpha*omega)  over violators
        c_star = min(viol) if viol else float("inf")
        # largest n/aw seen among satisfiers (a soft upper-confidence on c*)
        c_sat_max = max(sats) if sats else float("nan")
        # smallest n/aw seen among satisfiers (most "dangerous" satisfier)
        c_sat_min = min(sats) if sats else float("nan")
        summary[n] = {
            "n": n,
            "count": slot["count"],
            "violators_count": len(viol),
            "satisfiers_count": len(sats),
            "thm81_hypothesis_count": slot["thm81_hypothesis_count"],
            "thm81_hypothesis_fraction": slot["thm81_hypothesis_count"]
            / slot["count"],
            "c_star_empirical": c_star,
            "c_sat_max": c_sat_max,
            "c_sat_min": c_sat_min,
        }
    return summary


def summarize_violators(records: list[dict], top: int = 12) -> list[dict]:
    """Return the most informative violators (small n_over_aw means
    Thm 8.1's hypothesis is *closer to being applicable*, yet min(s^+,s^-) < n).

    These are the graphs that 'test' the constant 17 the hardest.
    """
    vio = [r for r in records if not r["min_s_ge_n"]]
    vio_sorted = sorted(vio, key=lambda r: r["n_over_aw"], reverse=True)
    return vio_sorted[:top]


# -- entry point --------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-random-larger",
        action="store_true",
        help="Also sample random connected graphs at n in {8,10,12,14}.",
    )
    parser.add_argument(
        "--samples-per-n",
        type=int,
        default=200,
        help="Samples per n for the random extension (default 200).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(
            Path(__file__).resolve().parents[1]
            / "data"
            / "alpha_omega_corpus.json"
        ),
        help="Output JSON path.",
    )
    args = parser.parse_args()

    graphs: list[nx.Graph] = []
    graphs.extend(iter_connected_atlas())
    if args.with_random_larger:
        graphs.extend(
            iter_random_larger([8, 10, 12, 14], samples_per_n=args.samples_per_n)
        )

    print(f"Total graphs to process: {len(graphs)}")

    records = []
    for i, G in enumerate(graphs):
        rec = record(G)
        records.append(rec)
        if (i + 1) % 200 == 0:
            print(f"  processed {i + 1} / {len(graphs)}")

    summary = empirical_c_star(records)
    violators = summarize_violators(records, top=25)

    out = {
        "meta": {
            "description": (
                "Per-graph data for the alpha*omega exploration of "
                "Theorem 8.1 of arXiv:2506.07264.  Hypothesis "
                "alpha*omega <= n/17  =>  min(s+,s-) >= n."
            ),
            "graph_count": len(records),
            "n_range": (
                min(r["n"] for r in records),
                max(r["n"] for r in records),
            ),
        },
        "summary_by_n": summary,
        "interesting_violators": violators,
        "records": records,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"Wrote {args.out}")

    # Print a compact summary table
    print()
    print(f"{'n':>3} {'#G':>6} {'#viol':>6} {'#sat':>6} {'%thm81':>7} "
          f"{'c*_emp':>10} {'c_sat_min':>10}")
    for n, s in summary.items():
        c_star = s["c_star_empirical"]
        c_star_str = f"{c_star:.4f}" if c_star != float("inf") else "  +inf"
        c_sat_min = s["c_sat_min"]
        c_sat_min_str = (
            f"{c_sat_min:.4f}"
            if isinstance(c_sat_min, float) and c_sat_min == c_sat_min
            else "  n/a"
        )
        print(
            f"{n:>3} {s['count']:>6} {s['violators_count']:>6} "
            f"{s['satisfiers_count']:>6} "
            f"{100 * s['thm81_hypothesis_fraction']:>6.2f}% "
            f"{c_star_str:>10} {c_sat_min_str:>10}"
        )

    print()
    print("Most informative violators (largest n/(alpha*omega) among graphs "
          "with min(s+,s-) < n):")
    print(f"{'n':>3} {'m':>3} {'alpha':>5} {'omega':>5} {'aw':>4} "
          f"{'n/aw':>7} {'s+':>8} {'s-':>8} {'min_s/n':>8}")
    for v in violators:
        print(
            f"{v['n']:>3} {v['m']:>3} {v['alpha']:>5} {v['omega']:>5} "
            f"{v['alpha_omega']:>4} "
            f"{v['n_over_aw']:>7.3f} {v['s_plus']:>8.4f} {v['s_minus']:>8.4f} "
            f"{v['min_s_over_n']:>8.4f}"
        )


if __name__ == "__main__":
    main()
