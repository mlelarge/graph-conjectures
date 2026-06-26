import os
"""GENERIC ov=5 record hunt at order n=43 (near-copy of random_k6_sweep.py).

Seeds 0..7 at n=43, exact G48 generator random_arcs(n,seed)
(rng_seed = 1000*n + seed). Build no-K5 betweenness CNF and solve with
Cadical153 (60s per-instance interrupt guard). SAT => omega_vec <= 4.
UNSAT => omega_vec >= 5 (record: explicit order-43 ov>=5 tournament,
beating ell(5)<=49). On UNSAT: cross-check with Minisat22, then solve
no-K6 (expect SAT) to pin ov=5 exactly, and dump witness.
"""
import random, time, sys, json, threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search_4critical_circulant import build_cnf_no_kclique
from pysat.solvers import Cadical153, Minisat22

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
SOLVE_BUDGET = 60.0

def random_arcs(n, seed):
    rng = random.Random(1000 * n + seed)
    arcs = set()
    for i in range(n):
        for j in range(i + 1, n):
            arcs.add((i, j) if rng.random() < 0.5 else (j, i))
    return arcs

def run_instance(n, seed, K):
    arcs = random_arcs(n, seed)
    t0 = time.time()
    cnf, nclq = build_cnf_no_kclique(n, arcs, K)
    t_build = time.time() - t0
    t0 = time.time()
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        timer = threading.Timer(SOLVE_BUDGET, m.interrupt)
        timer.start()
        res = m.solve_limited(expect_interrupt=True)
        timer.cancel()
    t_solve = time.time() - t0
    return arcs, nclq, res, t_build, t_solve

def main():
    n = 43
    for seed in range(8):
        arcs, nclq, res, tb, ts = run_instance(n, seed, 5)
        tag = {True: 'SAT', False: 'UNSAT', None: 'TIMEOUT'}[res]
        print((n, seed, 'K5', nclq, tag, round(tb, 1), round(ts, 1)), flush=True)
        if res is False:
            # cross-check UNSAT with Minisat22
            cnf5, _ = build_cnf_no_kclique(n, arcs, 5)
            with Minisat22(bootstrap_with=cnf5.clauses) as m2:
                res2 = m2.solve()
            print(('minisat_k5_crosscheck', n, seed, 'sat=', res2), flush=True)
            # pin ov=5 exactly: no-K6 should be SAT (ov<=5)
            cnf6, nclq6 = build_cnf_no_kclique(n, arcs, 6)
            with Cadical153(bootstrap_with=cnf6.clauses) as m3:
                timer = threading.Timer(SOLVE_BUDGET, m3.interrupt)
                timer.start()
                res6 = m3.solve_limited(expect_interrupt=True)
                timer.cancel()
            print(('no_k6', n, seed, 'sat=', res6), flush=True)
            json.dump({'n': n, 'seed': seed, 'rng_seed': 1000 * n + seed,
                       'arcs': sorted(arcs), 'nclq_k5': nclq,
                       'minisat_unsat_crosscheck': (res2 is False),
                       'no_k6_sat': res6},
                      open(DATA + '/random_k5_witness_n43.json', 'w'))
            print('UNSAT K5 WITNESS -> omega_vec>=5 at n=43', flush=True)
            sys.exit(0)
    print('ALL DECIDED INSTANCES SAT at n=43 - kill probe (generic ov<=4 at 43)', flush=True)

if __name__ == '__main__':
    main()
