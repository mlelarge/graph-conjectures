#!/usr/bin/env python3
"""
EXHAUSTIVE-over-base-4-tuples P4 breaker search at max_len=4, n=9 (3,3,3).

Enumerates EVERY base 4-tuple (one pure-point cycle per flip) on the
single-arc skeleton with cycle length <=4, cheap-filters to OVERLAPPING
full-support no-clash candidates, de-duplicates by arc set, then tiers the
oracle gating (eulerian -> strong -> kappa>=3 -> chi==3 -> lambda -> 2extremal)
to find any P4 BREAKER (lambda==2 + 2-extremal + overlap + full-support cover).

This is an exhaustive deterministic sweep of the simplest overlapping cover
shape (4 suppliers, no extras), complementing the randomized search that
samples larger / extra-supplier shapes.

Run in FOREGROUND with a hard timeout.
"""
import itertools
import os
import signal
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from step1b_fd_connectivity import vertex_connectivity  # noqa: E402
from p4_breaker_systematic import (  # noqa: E402
    build_forest_3comp, all_pure_point_cycles, cycle_arcs,
)


def main():
    deadline_killed = {"v": False}

    def on_alarm(sig, frm):
        deadline_killed["v"] = True
        raise TimeoutError

    signal.signal(signal.SIGALRM, on_alarm)
    signal.alarm(820)  # internal hard cap, under the outer timeout

    comp_sizes = (3, 3, 3)
    n, forest, comp, bit = build_forest_3comp(comp_sizes)
    digon = frozenset(a for u, v in forest for a in ((u, v), (v, u)))
    omega = tuple((0, x1, x2)
                  for x1, x2 in itertools.product((0, 1), repeat=2))
    bf = all_pure_point_cycles(n, comp, bit, omega, digon, 4)
    lists = [bf[f] for f in omega]
    allverts = set(range(n))

    st = Counter()
    classes = Counter()
    breakers = []
    seen = set()
    try:
        for bt in itertools.product(*lists):
            st["base"] += 1
            sets = [cycle_arcs(c) for c in bt]
            singles = frozenset().union(*sets)
            if sum(len(s) for s in sets) <= len(singles):
                continue
            if {v for c in bt for v in c} != allverts:
                continue
            clash = False
            for (u, v) in singles:
                if (v, u) in singles or (u, v) in digon:
                    clash = True
                    break
            if clash:
                continue
            arcs = singles | digon
            fa = frozenset(arcs)
            if fa in seen:
                continue
            seen.add(fa)
            st["distinct"] += 1
            if not H.is_eulerian_deg(n, arcs):
                st["not_euler"] += 1
                continue
            if not H.is_strong(n, arcs):
                st["not_strong"] += 1
                continue
            kappa = vertex_connectivity(n, arcs)
            if kappa < 3:
                st["kappa_lt3"] += 1
                continue
            st["k3_candidates"] += 1
            chi = H.chi_vec(n, arcs)
            if chi != 3:
                classes[("chi", chi)] += 1
                continue
            lam = H.lambda_D(n, arcs)
            is2e = H.is_2extremal(n, arcs)
            classes[(lam, is2e)] += 1
            if lam == 2 and is2e:
                breakers.append({
                    "n": n, "arcs": sorted(map(list, arcs)),
                    "kappa": kappa, "lambda": lam, "chi": chi,
                    "suppliers": [list(c) for c in bt],
                })
    except TimeoutError:
        st["TIMEOUT_internal"] += 1

    print(f"# EXHAUSTIVE base-4-tuple ml=4  n={n} comp_sizes={comp_sizes}")
    print(f"  stats: {dict(st)}")
    print("  among 3-connected chi==3 candidates, key=(lambda,is_2extremal) "
          "or ('chi',value):")
    for k, c in sorted(classes.items(), key=lambda x: str(x[0])):
        print(f"    {k}: {c}")
    print(f"  P4 BREAKERS: {len(breakers)}")
    for b in breakers[:5]:
        print(f"    BREAKER: {b}")
    if deadline_killed["v"] or st.get("TIMEOUT_internal"):
        print("  WARNING: internal deadline hit -> NOT exhaustive "
              "(partial sweep).")
    elif not breakers:
        print("  RESULT (EXHAUSTIVE over base-4-tuples, ml<=4): no lambda==2 "
              "2-extremal overlapping full-support pure-point candidate. "
              "P4 SURVIVES this complete family.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
