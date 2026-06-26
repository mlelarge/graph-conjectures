"""Parallel depth-6 L_6 bracketing: positional SAT over sigma-cyclic-rep cap triples.

Aut(B_k)=C_3 (only sigma), so the only usable symmetry is the cyclic dedup of cap
triples (feasibility invariant under rotating (q0,q1,q2)).  No within-instance
automorphism symmetry exists for skewed caps.  We parallelize the scan instead.
Each solve self-limits via a conflict budget (UNKNOWN if exhausted).
"""
import sys, time, json, itertools, signal, os
import multiprocessing as mp
sys.path.insert(0, "scripts")

# Run as its own process group and turn SIGTERM into a clean SystemExit so the
# `with mp.Pool(...)` context manager terminates workers on stop — avoids
# orphaning multiprocessing.spawn workers on a bare pkill of the parent.
try:
    os.setpgrp()
except OSError:
    pass
signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))

LO, HI = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (28, 48)
BUDGET = int(sys.argv[3]) if len(sys.argv) > 3 else 3_000_000  # fast-map default
WORKERS = max(1, mp.cpu_count() - 2)

def cyc_rep(c):
    return min((c, (c[1], c[2], c[0]), (c[2], c[0], c[1])))

def solve(caps):
    from decide_layer_positional import decide_caps_positional
    t = time.time()
    r = decide_caps_positional(6, tuple(caps), conf_budget=BUDGET)
    st = 'SAT' if r['sat'] else ('UNSAT' if r['sat'] is False else 'UNKNOWN')
    return (tuple(caps), caps[0]*caps[1]*caps[2], st, round(time.time()-t, 0),
            r.get('verified_heights'))

def main():
    reps = {}
    for c in itertools.product(range(1, HI + 1), repeat=3):
        p = c[0]*c[1]*c[2]
        if LO <= p <= HI:
            reps.setdefault(cyc_rep(c), p)
    cands = sorted(reps, key=lambda c: (reps[c], c))
    print(f"# L_6 parallel: {len(cands)} cyclic-rep triples, product in [{LO},{HI}], "
          f"budget={BUDGET}, workers={WORKERS}", flush=True)
    log = open("data/L6_parallel.log", "w")
    results = []
    with mp.Pool(WORKERS) as pool:
        for res in pool.imap_unordered(solve, cands):
            results.append(res)
            line = f"caps={res[0]} product={res[1]} {res[2]} {res[3]}s heights={res[4]}"
            print(line, flush=True); log.write(line + "\n"); log.flush()
    sat = [r for r in results if r[2] == 'SAT']
    unsat = [r for r in results if r[2] == 'UNSAT']
    upper = min((r[1] for r in sat), default=None)
    # lower bound: largest P with ALL tested cyclic-reps of product <= P decided UNSAT
    by_prod = {}
    for r in results:
        by_prod.setdefault(r[1], []).append(r[2])
    lower = None
    for p in sorted(by_prod):
        if all(s == 'UNSAT' for s in by_prod[p]):
            lower = p
        else:
            break
    summary = {"upper_bound_min_SAT": upper, "all_unsat_through": lower,
               "n_sat": len(sat), "n_unsat": len(unsat),
               "n_unknown": len(results) - len(sat) - len(unsat)}
    print("# SUMMARY:", summary, flush=True); log.write(f"# SUMMARY: {summary}\n")
    json.dump({"results": [list(r) for r in results], "summary": summary},
              open("data/L6_parallel.json", "w"))

if __name__ == "__main__":
    main()
