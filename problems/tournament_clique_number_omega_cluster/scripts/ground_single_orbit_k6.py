"""Ground the single-orbit-circulant k=6 proposal (decoupled from dom).

For odd n in {37,39,41,43,45,47,49}, sample valid circulant generators g
(one element per antipodal pair {x,n-x}), keep those whose identity-order
backedge clique == 6 (cheap upper bound), and run the validated
build_cnf_no_kclique(n, arcs, 6) SAT oracle:
  SAT   => some order is K6-free => omega_vec <= 5
  UNSAT => omega_vec >= 6 ; combined with id-clique==6 upper => omega_vec == 6.

A single UNSAT = FIRST single-orbit circulant k=6 witness at order <= 49.
"""
import sys, os, random, signal, time
sys.path.insert(0, os.path.dirname(__file__))
import core
import search_4critical_circulant as s
from pysat.solvers import Cadical153


def arcs(n, g):
    return [(i, (i + x) % n) for i in range(n) for x in g]


def valid(n, g):
    g = set(g)
    ng = set((n - x) % n for x in g)
    return len(g) == (n - 1) // 2 and not (g & ng) and (g | ng) == set(range(1, n))


def idc(n, g):
    return core.omega_of_order(n, arcs(n, g), list(range(n)))


class TO(Exception):
    pass


def _alarm(sig, frm):
    raise TO()


def nok(n, g, K, limit=110):
    cnf, _ = s.build_cnf_no_kclique(n, arcs(n, g), K)
    sv = Cadical153(bootstrap_with=cnf.clauses)
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(limit)
    try:
        r = sv.solve()
    finally:
        signal.alarm(0)
        sv.delete()
    return r


def main():
    random.seed(11)
    ns = [37, 39, 41, 43, 45, 47, 49]
    found = []
    for n in ns:
        m = (n - 1) // 2
        done = 0
        tested_ids = set()
        for _ in range(4000):
            g = frozenset(x if random.random() < 0.5 else n - x for x in range(1, m + 1))
            if not valid(n, g):
                continue
            if g in tested_ids:
                continue
            if idc(n, g) != 6:
                continue
            tested_ids.add(g)
            t0 = time.time()
            try:
                r = nok(n, g, 6)
                el = time.time() - t0
            except TO:
                print(f"n={n} g={sorted(g)} no-K6 SAT=TIMEOUT (>110s)", flush=True)
                done += 1
                if done >= 6:
                    break
                continue
            done += 1
            verdict = "<=5" if r else "==6 WITNESS"
            print(f"n={n} g={sorted(g)} no-K6 SAT={r} => omega_vec {verdict} ({el:.2f}s)", flush=True)
            if not r:
                print(f"K6 WITNESS FOUND n={n} g={sorted(g)}", flush=True)
                found.append((n, sorted(g)))
                break
            if done >= 6:
                break
        if not found:
            print(f"n={n}: tested {done} id_clique=6 circulants, no UNSAT", flush=True)
    print("=== SUMMARY ===", flush=True)
    print("witnesses:", found, flush=True)


if __name__ == "__main__":
    main()
