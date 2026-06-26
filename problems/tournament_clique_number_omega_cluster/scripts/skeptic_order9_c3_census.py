#!/usr/bin/env python3
"""SKEPTIC kill-hunt for the width-2-confinement proposal.

The proposal's scoped lemma (UNIVERSAL): omega_vec(C3[H]) <= ov(H)+1 whenever
ov(H) >= 3, supported so far ONLY at inner order <= 8 (13 generic classes).
Its own stated CONFIRM/KILL test is the order-9 generic census: all 1146
order-9 iso classes with omega_vec(H)=3 (P9b histogram {1:1,2:190389,3:1146}).
ANY class with omega_vec(C3[H]) >= 5 kills the confinement law.

Phase A (--phase a --start S --end E): scan gentourng-9 class indices in
  [S,E); decide omega_vec<=2 by cheap triangle-free-order certificate, exact
  bitmask fallback omega_vec_le_t(.,2) for stubborn classes.  Classes with
  omega_vec>=3 (== 3 exactly, since the P9b histogram has no 4s; we ALSO
  cross-check the global count == 1146) are saved with their arcs.

Phase B (--phase b --start S --end E): for ov3-class indices [S,E) in the
  merged phase-A list, build C3[H] (order 27, proven window [4,6]) and ask
  no-K5 (chain/Cadical):
    SAT   -> witness order verified by core.omega_of_order < 5 => value 4
             (with the proven lex lower bound 2+3-1=4).
    UNSAT -> cross-check all_pairs/Minisat; both UNSAT => omega_vec >= 5
             ====> KILL (recorded, plus a no-K6 call to pin the value).

All phases run in the foreground under signal.alarm; checkpoints are JSON
chunks in data/ merged at the end.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import core
from lexlib import C3, lex_substitute
from pysat.solvers import Cadical153, Minisat22
from refute_h16_substitution_law import (
    build_no_k_clique_cnf_all_pairs,
    build_no_k_clique_cnf_chain,
    gentourng_classes,
    solve_cnf,
)
from iso_critical_scan_n9 import (
    beats_matrix,
    cheap_le2_certificate,
    omega_vec_le_t,
)

DATA = os.path.join(ROOT, "data")


def phase_a(start, end, alarm_s):
    signal.alarm(alarm_s)
    t0 = time.time()
    found = []
    n_seen = 0
    n_cheap = 0
    n_exact = 0
    for idx, arcs in enumerate(gentourng_classes(9)):
        if idx < start:
            continue
        if idx >= end:
            break
        n_seen += 1
        beats = beats_matrix(9, arcs)
        if cheap_le2_certificate(9, beats, tries=40, greedy=8):
            n_cheap += 1
            continue
        # exact decision
        n_exact += 1
        if omega_vec_le_t(9, beats, 2):
            continue
        found.append({"class_index": idx, "arcs": arcs})
    out = {
        "phase": "a", "start": start, "end": end, "n_seen": n_seen,
        "n_cheap_le2": n_cheap, "n_exact_fallback": n_exact,
        "n_ov_ge3": len(found), "elapsed_s": round(time.time() - t0, 1),
        "classes": found,
    }
    path = os.path.join(DATA, f"skeptic_o9_phaseA_{start}_{end}.json")
    with open(path, "w") as f:
        json.dump(out, f)
    print(f"[A {start}:{end}] seen={n_seen} cheap={n_cheap} exact={n_exact} "
          f"ov>=3: {len(found)}  ({out['elapsed_s']}s) -> {path}", flush=True)


def merge_a():
    import glob
    classes = []
    tot = 0
    for p in sorted(glob.glob(os.path.join(DATA, "skeptic_o9_phaseA_*.json"))):
        with open(p) as f:
            d = json.load(f)
        tot += d["n_seen"]
        classes.extend(d["classes"])
    classes.sort(key=lambda c: c["class_index"])
    idxs = [c["class_index"] for c in classes]
    assert len(set(idxs)) == len(idxs), "duplicate class indices in chunks"
    out = {"n_seen_total": tot, "n_ov3": len(classes), "classes": classes}
    path = os.path.join(DATA, "skeptic_o9_ov3_classes.json")
    with open(path, "w") as f:
        json.dump(out, f)
    print(f"[merge] seen={tot} ov3={len(classes)} -> {path}", flush=True)
    print("P9b cross-check: expected 1146 ov=3 classes ->",
          "MATCH" if len(classes) == 1146 else "MISMATCH (INVESTIGATE)",
          flush=True)


def phase_b(start, end, alarm_s):
    signal.alarm(alarm_s)
    t0 = time.time()
    with open(os.path.join(DATA, "skeptic_o9_ov3_classes.json")) as f:
        allc = json.load(f)["classes"]
    chunk = allc[start:end]
    results = []
    kills = []
    hist = {}
    for c in chunk:
        H = (9, [tuple(a) for a in c["arcs"]])
        n, arcs = lex_substitute(C3, H)
        assert n == 27
        res = solve_cnf(build_no_k_clique_cnf_chain, Cadical153, n, arcs, 5)
        rec = {"class_index": c["class_index"], "noK5_sat": res["sat"],
               "seconds": res["seconds"]}
        if res["sat"]:
            # witness order already asserted: omega_of_order < 5 => value = 4
            rec["value"] = 4
            rec["order_clique"] = res["order_clique"]
        else:
            x = solve_cnf(build_no_k_clique_cnf_all_pairs, Minisat22, n, arcs, 5)
            rec["noK5_crosscheck_sat"] = x["sat"]
            assert not x["sat"], "solver disagreement on UNSAT"
            # omega_vec >= 5 : KILL.  Pin the value with no-K6.
            r6 = solve_cnf(build_no_k_clique_cnf_chain, Cadical153, n, arcs, 6)
            rec["noK6_sat"] = r6["sat"]
            rec["value"] = 5 if r6["sat"] else 6
            rec["kill"] = True
            rec["arcs"] = c["arcs"]
            kills.append(rec)
            print(f"  !! KILL class {c['class_index']}: omega_vec(C3[H]) = "
                  f"{rec['value']} >= 5", flush=True)
        hist[rec["value"]] = hist.get(rec["value"], 0) + 1
        results.append(rec)
    out = {"phase": "b", "start": start, "end": end,
           "n_tested": len(results),
           "value_histogram": {str(k): v for k, v in sorted(hist.items())},
           "n_kills": len(kills), "kills": kills,
           "elapsed_s": round(time.time() - t0, 1), "results": results}
    path = os.path.join(DATA, f"skeptic_o9_phaseB_{start}_{end}.json")
    with open(path, "w") as f:
        json.dump(out, f)
    print(f"[B {start}:{end}] tested={len(results)} hist={out['value_histogram']} "
          f"kills={len(kills)} ({out['elapsed_s']}s) -> {path}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=["a", "merge", "b"])
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=10**9)
    ap.add_argument("--alarm", type=int, default=560)
    a = ap.parse_args()
    if a.phase == "a":
        phase_a(a.start, a.end, a.alarm)
    elif a.phase == "merge":
        merge_a()
    else:
        phase_b(a.start, a.end, a.alarm)


if __name__ == "__main__":
    main()
