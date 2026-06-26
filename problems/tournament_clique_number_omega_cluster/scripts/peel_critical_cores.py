"""H1 vs H2 experiment (next_action): peel 3-omega_vec-critical cores out of the
substitution family S~_3 (and a Delta-tower variant) and TRACK the maximum order
of any 3-omega_vec-critical subtournament found.

For a tournament T with omega_vec(T) >= 3 we:
  (a) compute the SMALLEST subtournament order with omega_vec >= 3
      (= the ell(3) cluster certificate, min_subtournament_order_for_k);
  (b) enumerate induced subtournaments by ORDER and isolate every one that is
      exactly 3-omega_vec-critical (omega_vec = 3 and omega_vec(.-v) = 2 for all v);
  (c) report the MIN and MAX order over all 3-critical subtournaments.

H1 (Question 5.9 at k=3): the max 3-critical order is bounded by a small constant.
H2 (Conjecture 5.10 at k=3): peeling yields arbitrarily large 3-critical cores.

This is a finite VERIFICATION (discipline_gates.empirical_not_proof), not a proof.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core
import constructions as C


def scan_subtournaments_for_critical(n, arcs, k, max_size=None):
    """Enumerate ALL induced subtournaments by order; return data on which are
    k-omega_vec-critical and the smallest order achieving omega_vec >= k."""
    top = max_size if max_size is not None else n
    crit_orders = []          # orders of k-critical subtournaments
    crit_examples = {}        # order -> one example vertex set
    first_omega_ge_k = None   # smallest order with omega_vec >= k
    omega_ge_k_example = None
    counts_omega_ge_k = {}    # order -> #subtournaments with omega_vec >= k

    for size in range(1, top + 1):
        for keep in itertools.combinations(range(n), size):
            nn, sub = core.subtournament(n, arcs, keep)
            w = core.omega_vec(nn, sub)
            if w >= k:
                counts_omega_ge_k[size] = counts_omega_ge_k.get(size, 0) + 1
                if first_omega_ge_k is None:
                    first_omega_ge_k = size
                    omega_ge_k_example = keep
                # criticality test (only meaningful when w == k)
                if w == k and core.is_k_omega_vec_critical(nn, sub, k):
                    crit_orders.append(size)
                    crit_examples.setdefault(size, keep)
    return {
        "first_omega_ge_k_order": first_omega_ge_k,
        "first_omega_ge_k_example": list(omega_ge_k_example) if omega_ge_k_example else None,
        "counts_omega_ge_k_by_order": counts_omega_ge_k,
        "critical_orders": sorted(set(crit_orders)),
        "num_critical_by_order": {o: crit_orders.count(o) for o in sorted(set(crit_orders))},
        "min_critical_order": min(crit_orders) if crit_orders else None,
        "max_critical_order": max(crit_orders) if crit_orders else None,
        "critical_examples": {o: list(v) for o, v in crit_examples.items()},
    }


def run():
    results = {}
    k = 3

    # --- S~_3 : 9 vertices, omega_vec = 3 ---
    n, arcs = C.S_tilde(3)
    assert core.is_tournament(n, arcs)
    w = core.omega_vec(n, arcs)
    t0 = time.time()
    s3 = scan_subtournaments_for_critical(n, arcs, k)
    s3["n"] = n
    s3["omega_vec_whole"] = w
    s3["seconds"] = round(time.time() - t0, 2)
    results["S_tilde_3"] = s3
    print("S~_3:", json.dumps(s3, indent=2))

    # --- Delta(C3, C3, C3) : 9 vertices, a different Delta-tower ---
    c3 = C.directed_C3()
    n2, arcs2 = C.delta(c3, c3, c3)
    assert core.is_tournament(n2, arcs2)
    w2 = core.omega_vec(n2, arcs2)
    t0 = time.time()
    d = scan_subtournaments_for_critical(n2, arcs2, k)
    d["n"] = n2
    d["omega_vec_whole"] = w2
    d["seconds"] = round(time.time() - t0, 2)
    results["Delta_C3_C3_C3"] = d
    print("Delta(C3,C3,C3):", json.dumps(d, indent=2))

    # --- Delta(C3, TT1, TT1) and Delta(C3, C3, TT1) probes for omega_vec growth ---
    tt1 = C.transitive_tournament(1)
    for label, blocks in [
        ("Delta_C3_TT1_TT1", (c3, tt1, tt1)),
        ("Delta_C3_C3_TT1", (c3, c3, tt1)),
        ("Delta_TT1_C3_C3", (tt1, c3, c3)),
    ]:
        nn, aa = C.delta(*blocks)
        ww = core.omega_vec(nn, aa)
        results[label] = {"n": nn, "omega_vec_whole": ww}
        print(label, "omega_vec =", ww, "n =", nn)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'peel_critical_cores.json')
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print("WROTE", out)

    # Headline beat/floor signature
    print("\n=== HEADLINE ===")
    print("S~_3   3-critical orders:", s3["critical_orders"],
          "min=", s3["min_critical_order"], "max=", s3["max_critical_order"],
          "ell(3)=", s3["first_omega_ge_k_order"])
    print("DeltaC3 3-critical orders:", d["critical_orders"],
          "min=", d["min_critical_order"], "max=", d["max_critical_order"],
          "ell(3)=", d["first_omega_ge_k_order"])


if __name__ == "__main__":
    run()
