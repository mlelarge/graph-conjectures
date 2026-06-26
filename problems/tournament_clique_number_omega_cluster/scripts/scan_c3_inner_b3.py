#!/usr/bin/env python3
"""Multiplicative-attainment census for width-2 outer, inner omega_vec = 3.

D35 refuted H16 with omega_vec(C3[H7]) = 4 = 2*2 (inner b=2, generic H7).
The valid universal bounds are  a+b-1 <= omega_vec(S[H]) <= a*b.
For inner b=3 the ONLY known datapoint is the STRUCTURED S~_3
(C3[S~_3] = S~_4, omega_vec 4 = a+b-1) -- exactly the biased-sample trap
(universal_needs_generic_census).  This script runs the EXHAUSTIVE generic
census at the smallest generic scale:

  * enumerate ALL order-8 tournament iso classes (gentourng, 6880 classes),
  * keep those with omega_vec exactly 3 (expected 13, per P7),
  * for each such H compute omega_vec(C3[H]) (order 24) EXACTLY via the
    validated no-K-clique betweenness SAT ladder:
       lower bounds: no-K CNF UNSAT  =>  omega_vec >= K
                     (UNSATs cross-checked with a 2nd encoding + 2nd solver)
       upper bounds: no-K CNF SAT    =>  decoded order has backedge clique
                     < K, verified by canonical core.omega_of_order.
    The window is provably [4, 6]: lower 2+3-1 (proven lex lower bound),
    upper 2*3 (block laminarity).

If ANY H attains omega_vec(C3[H]) = 6, that is the FIRST omega_vec=6 object
at order 24 (existential claim, settled by the certificate itself) and the
k=6 frontier moves.  If the max is 5, the multiplicative blow-up partially
transfers to b=3 and yields new k=5-size objects of order 24.  If ALL 13
give 4, the blow-up is (at this scope) a b=2 phenomenon and the structured
S~_3 value is generic after all -- scoped to inner order 8.

Controls: C3[QR_7] (order 21, structured inner) and C3[S~_3] (order 27,
structured inner, expected 4 = G45's S~_4 value).
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core
from lexlib import C3, lex_substitute
from pysat.solvers import Cadical153, Minisat22
from refute_h16_substitution_law import (
    build_no_k_clique_cnf_all_pairs,
    build_no_k_clique_cnf_chain,
    gentourng_classes,
    solve_cnf,
)

HARD_TIMEOUT_S = 840  # global alarm; the run must finish in the foreground


def omega_vec_small_exact(n, arcs):
    """Exact omega_vec for small n via the canonical oracle."""
    return core.omega_vec(n, arcs)


def exact_value_via_sat_ladder(n, arcs, lo, hi):
    """Exact omega_vec in the proven window [lo, hi] via the no-K ladder.

    Invariant maintained: lo <= omega_vec <= hi, with certificates:
      raising lo: no-K(lo+1)... wait -- we raise lo by showing no-K(lo+1)
      UNSAT is wrong direction; correct: no-K(K) UNSAT => omega_vec >= K.
    We walk K = lo+1, ..., asking no-K(K):
      SAT   => an explicit order with clique <= K-1 => omega_vec <= K-1
               combined with omega_vec >= lo... and since previous K'-call
               (if any) was UNSAT we know omega_vec >= K-1 -- value pinned.
      UNSAT => omega_vec >= K, continue.
    Returns (value, log).
    """
    log = []
    known_lo = lo
    for K in range(lo + 1, hi + 2):
        res = solve_cnf(build_no_k_clique_cnf_chain, Cadical153, n, arcs, K)
        entry = {"K": K, "encoding": "chain/Cadical153", **{
            k: res[k] for k in ("sat", "forbidden_transitive_sets",
                                "clauses", "seconds", "order_clique")}}
        if res["sat"]:
            # explicit order with backedge clique <= K-1 (verified in solve_cnf)
            entry["upper_witness_order"] = res["order"]
            log.append(entry)
            value = max(known_lo, res["order_clique"])
            # value must equal known_lo..K-1; clique of the witness order is
            # an upper bound K-1 and >= actual only if optimal; the exact
            # value is known_lo if order_clique <= known_lo else order_clique
            # is only an upper bound -- but since no-K(known_lo) was UNSAT
            # (or known_lo proven), omega_vec >= known_lo, and witness gives
            # omega_vec <= K-1.  If K-1 == known_lo the value is pinned.
            assert K - 1 >= known_lo
            if K - 1 == known_lo:
                return known_lo, log
            # window [known_lo, K-1] not a point: tighten by descending SAT
            # calls (should not happen in a +1 ladder)
            return None, log
        # UNSAT: cross-check with the independent encoding + solver
        xres = solve_cnf(build_no_k_clique_cnf_all_pairs, Minisat22, n, arcs, K)
        entry["crosscheck_all_pairs_Minisat_sat"] = xres["sat"]
        assert not xres["sat"], "solver disagreement on UNSAT"
        log.append(entry)
        known_lo = K
    # All K up to hi+1 UNSAT would contradict the proven upper bound hi.
    return known_lo, log


def s_tilde_3():
    from constructions import S_tilde
    return S_tilde(3)


def qr7():
    g = {1, 2, 4}
    return (7, [(i, (i + d) % 7) for i in range(7) for d in g])


def main():
    signal.alarm(HARD_TIMEOUT_S)
    t0 = time.time()
    out = {"experiment": "C3[H] multiplicative attainment, inner b=3, "
                         "exhaustive generic census at inner order 8",
           "window_proof": "lower a+b-1=4 (proven lex lower bound), "
                           "upper a*b=6 (block laminarity)"}

    # 1) exhaustive enumeration of order-8 iso classes; keep omega_vec == 3
    classes3 = []
    hist = {}
    n_classes = 0
    for idx, arcs in enumerate(gentourng_classes(8), start=1):
        n_classes += 1
        ov = omega_vec_small_exact(8, arcs)
        hist[ov] = hist.get(ov, 0) + 1
        if ov == 3:
            classes3.append((idx, arcs))
    out["n8_iso_classes"] = n_classes
    out["n8_omega_vec_histogram"] = {str(k): v for k, v in sorted(hist.items())}
    out["n8_omega3_class_count"] = len(classes3)
    print(f"[{time.time()-t0:.1f}s] order-8 census: {n_classes} classes, "
          f"histogram {hist}, omega_vec=3 count {len(classes3)}", flush=True)
    assert n_classes == 6880, "gentourng census incomplete"
    assert hist.get(3, 0) == len(classes3)

    # 2) per-class exact omega_vec(C3[H]) at order 24
    results = []
    value_hist = {}
    for idx, arcs in classes3:
        pn, parcs = lex_substitute(C3, (8, arcs))
        assert pn == 24
        val, log = exact_value_via_sat_ladder(pn, parcs, lo=4, hi=6)
        assert val is not None
        value_hist[val] = value_hist.get(val, 0) + 1
        rec = {"inner_class_index": idx,
               "inner_arcs": arcs,
               "omega_vec_C3_H": val,
               "sat_ladder": log}
        results.append(rec)
        print(f"[{time.time()-t0:.1f}s] class {idx}: omega_vec(C3[H]) = {val}",
              flush=True)
    out["per_class"] = results
    out["value_histogram"] = {str(k): v for k, v in sorted(value_hist.items())}
    out["max_value"] = max(value_hist) if value_hist else None

    # 3) structured controls
    controls = {}
    for name, (hn, harcs), expect in (
            ("C3[QR_7]", qr7(), None),
            ("C3[S~_3]", s_tilde_3(), 4)):
        assert omega_vec_small_exact(hn, harcs) == 3
        pn, parcs = lex_substitute(C3, (hn, harcs))
        val, log = exact_value_via_sat_ladder(pn, parcs, lo=4, hi=6)
        controls[name] = {"order": pn, "omega_vec": val,
                          "expected": expect, "sat_ladder": log}
        print(f"[{time.time()-t0:.1f}s] control {name} (order {pn}): "
              f"omega_vec = {val}", flush=True)
        if expect is not None:
            assert val == expect
    out["controls"] = controls
    out["elapsed_seconds"] = round(time.time() - t0, 1)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "data", "scan_c3_inner_b3.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"DONE in {out['elapsed_seconds']}s -> {path}")
    print("VALUE HISTOGRAM over the exhaustive 13 generic inner classes:",
          out["value_histogram"], "max =", out["max_value"])


if __name__ == "__main__":
    main()
