"""Deeper analysis of tight 3-cuts in the Phase-3-v2 SAT witnesses.

For each instance and each tight 3-cut delta+(X), classify its three arcs by
which structural compartment (S1-internal, S2-internal, interface-internal,
S1-to-I, I-to-S1, S2-to-I, I-to-S2, bridges) they live in, and by their
color in the witness. We want to know:

  Q1.  For each tight 3-cut, what is its "compartment signature"?
       (e.g. "2 interface-internal + 1 bridge_12")
  Q2.  When the compartment signature pins the cut down completely, is
       the color split forced by the signature alone?

The hypothesis seeded by Phase-3-v1/v2 is that tight 3-cuts come in a few
"types" and CL1's color-compatibility constraint is exactly one type.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from benchmarks import all_benchmarks  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.glue_deficit import (  # noqa: E402
    DeficitGenConfig,
    generate_deficit_gluings,
    passes_arc_strong_3,
)
from verifier_sat import verify_sat  # noqa: E402


def compartment_of(arc, interface_start, interface_end):
    u, v = arc[0], arc[1]
    def side(w):
        if w < interface_start:
            return "S1n"
        if w < interface_end:
            return "I"
        return "S2n"
    return (side(u), side(v))


def analyse_one(inst):
    bench = {b.name: b for b in all_benchmarks()}
    T1 = bench[inst.template1]
    T2 = bench[inst.template2]
    D = inst.build()
    if not passes_arc_strong_3(D, exact=True):
        return None
    res = verify_sat(D, time_limit_s=20.0)
    if res["status"] != "SAT":
        return None
    red, blue = res["witness"]
    red_set = set(red)
    blue_set = set(blue)

    # Build keyed arcs in inst.arcs order.
    parallel_ctr = Counter()
    keyed = []
    for (u, v) in inst.arcs:
        k = parallel_ctr[(u, v)]
        keyed.append((u, v, k))
        parallel_ctr[(u, v)] += 1

    s = len(inst.S1)
    interface_start = T1.n - s
    interface_end = T1.n
    color_of = {ke: ("R" if ke in red_set else "B") for ke in keyed}

    # Enumerate tight 3-cuts.
    n = inst.n
    V = list(range(n))
    tight3 = []
    for r in range(1, n):
        for X_tup in combinations(V, r):
            X = frozenset(X_tup)
            # quick reject by counting arcs out
            size = 0
            cut_arcs = []
            for ke in keyed:
                u, v, _ = ke
                if u in X and v not in X:
                    cut_arcs.append(ke)
                    size += 1
                    if size > 3:
                        break
            if size == 3:
                # classify each arc
                sig = []
                colors = []
                for ke in cut_arcs:
                    sig.append(compartment_of(ke, interface_start, interface_end))
                    colors.append(color_of[ke])
                tight3.append({
                    "X_size": len(X),
                    "sig_sorted": tuple(sorted(sig)),
                    "colors": tuple(colors),
                    "color_sig_sorted": tuple(sorted(zip(sorted(sig), colors))),
                    "X_intersects_S1n": any(v < interface_start for v in X),
                    "X_intersects_I": any(interface_start <= v < interface_end for v in X),
                    "X_intersects_S2n": any(v >= interface_end for v in X),
                })
    return tight3


def main():
    bench = {b.name: b for b in all_benchmarks()}
    pair_classes = {
        "C1_C8sq_C8sq": ("C8_square", "C8_square"),
        "C2c_L312_L312": ("AiEtAl_L312_min", "AiEtAl_L312_min"),
        "C3a_iv_iv": ("AiEtAl_iv_star_iv", "AiEtAl_iv_star_iv"),
    }
    cfg = DeficitGenConfig(
        interface_sizes=(3, 4),
        max_interfaces_per_pair_per_size=30,
        max_bridges_per_interface=24,
        max_extra_slack_per_direction=1,
        allow_self_glue=True,
        ordered_pairs=True,
        require_arc_conn_exactly_3=True,
        verified_per_pair_cap=6,
        seed=20260516,
    )

    all_sigs = Counter()
    sig_to_color = {}  # sig -> Counter of color-tuples
    for cls, (n1, n2) in pair_classes.items():
        templates = [bench[n1]] if n1 == n2 else [bench[n1], bench[n2]]
        cnt = 0
        for inst in generate_deficit_gluings(templates, cfg):
            if (inst.template1, inst.template2) != (n1, n2):
                continue
            t3 = analyse_one(inst)
            if t3 is None:
                continue
            for tc in t3:
                sig = tc["sig_sorted"]
                all_sigs[sig] += 1
                # sort colors by signature compartment to canonicalize
                # We'll keep color tuple paired with sig in lex-sorted order:
                paired = tuple(sorted(zip(tc["sig_sorted"], tc["colors"])))
                sig_to_color.setdefault(sig, Counter())[tuple(p[1] for p in paired)] += 1
            cnt += 1
            if cnt >= 5:
                break
        print(f"  done {cls}")
    print()
    print("=== Compartment signatures of all tight 3-cuts (across 15 instances over 3 classes) ===")
    for sig, n in sorted(all_sigs.items(), key=lambda x: -x[1]):
        print(f"  {sig}  count={n}")
        cdist = sig_to_color.get(sig, Counter())
        # Print as a histogram, normalizing red/blue (the labels themselves
        # are arbitrary modulo the SAT symmetry break).
        norm_cdist = Counter()
        for ct, k in cdist.items():
            # canonicalize: if more R than B, leave as is; else flip
            r = sum(1 for c in ct if c == "R")
            b = sum(1 for c in ct if c == "B")
            if r >= b:
                norm_cdist[ct] += k
            else:
                ct2 = tuple(("R" if c == "B" else "B") for c in ct)
                norm_cdist[ct2] += k
        for ct, k in sorted(norm_cdist.items(), key=lambda x: -x[1]):
            print(f"     colors={ct}  count={k}")


if __name__ == "__main__":
    main()
