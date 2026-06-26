#!/usr/bin/env python3
"""Follow-up certificates for the b=3 census.

(1) Independent computational lower bound: for the first generic order-8
    inner class H, verify no-K4 UNSAT on C3[H] (omega_vec >= 4) so the
    value 4 is two-sided WITHOUT appealing to the lex lower-bound theorem.
(2) Iterated blow-up probe: X = C3[H7] (the D35 counterexample, omega_vec=4
    proven).  Compute omega_vec(C3[X]) (order 63) in the proven window
    [5, 8] (lower 2+4-1 lex, upper 2*4 laminarity).  Value 5 supports
    'the substitution law fails only at inner width 2'; value >5 means the
    blow-up ESCALATES under nesting (a potential k>=6 escalator).
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexlib import C3, lex_substitute
from refute_h16_substitution_law import (
    H7,
    build_no_k_clique_cnf_all_pairs,
    build_no_k_clique_cnf_chain,
    solve_cnf,
)
from scan_c3_inner_b3 import exact_value_via_sat_ladder
from pysat.solvers import Cadical153, Minisat22

signal.alarm(840)
t0 = time.time()
out = {}

# (1) two-sided lower bound spot check on the first census class
census = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "data", "scan_c3_inner_b3.json")))
first = census["per_class"][0]
h_arcs = [tuple(a) for a in first["inner_arcs"]]
pn, parcs = lex_substitute(C3, (8, h_arcs))
nok4_chain = solve_cnf(build_no_k_clique_cnf_chain, Cadical153, pn, parcs, 4)
nok4_pairs = solve_cnf(build_no_k_clique_cnf_all_pairs, Minisat22, pn, parcs, 4)
assert not nok4_chain["sat"] and not nok4_pairs["sat"]
out["lower_bound_spot_check"] = {
    "inner_class_index": first["inner_class_index"],
    "no_K4_chain_Cadical_sat": nok4_chain["sat"],
    "no_K4_all_pairs_Minisat_sat": nok4_pairs["sat"],
    "conclusion": "omega_vec(C3[H]) >= 4 certified computationally; "
                  "with the census SAT upper witness, value 4 is two-sided",
}
print(f"[{time.time()-t0:.1f}s] (1) no-K4 UNSAT x2 on class "
      f"{first['inner_class_index']}: lower bound 4 certified", flush=True)

# (2) iterated blow-up probe C3[C3[H7]], order 63, window [5,8]
xn, xarcs = lex_substitute(C3, H7)          # X = C3[H7], omega_vec = 4 (D35)
yn, yarcs = lex_substitute(C3, (xn, xarcs)) # order 63
assert yn == 63
val, log = exact_value_via_sat_ladder(yn, yarcs, lo=5, hi=8)
out["iterated_probe_C3_C3_H7"] = {
    "order": yn,
    "window_proof": "lower 2+4-1=5 (lex), upper 2*4=8 (laminarity)",
    "omega_vec": val,
    "sat_ladder": log,
}
print(f"[{time.time()-t0:.1f}s] (2) omega_vec(C3[C3[H7]]) = {val}", flush=True)

out["elapsed_seconds"] = round(time.time() - t0, 1)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "data", "scan_c3_inner_b3_followup.json")
with open(path, "w") as fh:
    json.dump(out, fh, indent=1)
print(f"DONE -> {path}")
