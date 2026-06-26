import os
"""GENERIC random-tournament k=6 witness hunt (first-moment crossover proposal).

For n in given list, seeds 0..5, build a uniformly random tournament
(seed = 1000*n + seed, rng.random()<0.5 arc orientation, matching the
proposal's construction exactly), build the no-K6 betweenness CNF and
solve with Cadical153. SAT => omega_vec <= 5. UNSAT => omega_vec >= 6
(first k=6 witness; saved to data/random_k6_witness.json).

Per-instance wall-clock guard: 120s on the SAT solve via threading.Timer
+ solver.interrupt() (SIGALRM cannot interrupt the C solver); interrupted
solve_limited returns None => recorded as TIMEOUT for that instance.
"""
import random, time, sys, json, threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search_4critical_circulant import build_cnf_no_kclique
from pysat.solvers import Cadical153, Minisat22

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
SOLVE_BUDGET = 120.0

def random_arcs(n, seed):
    rng = random.Random(1000 * n + seed)
    arcs = set()
    for i in range(n):
        for j in range(i + 1, n):
            arcs.add((i, j) if rng.random() < 0.5 else (j, i))
    return arcs

def run_instance(n, seed):
    arcs = random_arcs(n, seed)
    t0 = time.time()
    cnf, nclq = build_cnf_no_kclique(n, arcs, 6)
    t_build = time.time() - t0
    t0 = time.time()
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        timer = threading.Timer(SOLVE_BUDGET, m.interrupt)
        timer.start()
        res = m.solve_limited(expect_interrupt=True)
        timer.cancel()
    t_solve = time.time() - t0
    return arcs, nclq, res, t_build, t_solve

def main(ns):
    for n in ns:
        for seed in range(6):
            arcs, nclq, res, tb, ts = run_instance(n, seed)
            tag = {True: 'SAT', False: 'UNSAT', None: 'TIMEOUT'}[res]
            print((n, seed, nclq, tag, round(tb, 1), round(ts, 1)), flush=True)
            if res is False:
                # cross-check with Minisat22 before claiming the witness
                cnf, _ = build_cnf_no_kclique(n, arcs, 6)
                with Minisat22(bootstrap_with=cnf.clauses) as m2:
                    res2 = m2.solve()
                print(('minisat_crosscheck', n, seed, res2), flush=True)
                json.dump({'n': n, 'seed': seed, 'rng_seed': 1000 * n + seed,
                           'arcs': sorted(arcs), 'minisat_sat': res2},
                          open(DATA + '/random_k6_witness.json', 'w'))
                print('UNSAT WITNESS -> omega_vec>=6', flush=True)
                sys.exit(0)
    print('ALL DECIDED INSTANCES SAT - kill branch (for these n)', flush=True)

if __name__ == '__main__':
    main([int(x) for x in sys.argv[1:]])
