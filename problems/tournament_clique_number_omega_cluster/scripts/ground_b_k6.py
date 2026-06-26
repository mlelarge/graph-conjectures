"""(b) order 63: no-K6 SAT.  UNSAT => ov>=6 (KILL the law, value exceeds pred 5);
SAT => ov<=5 (consistent with pred when combined with no-K5 UNSAT).
Fast transitive-6-chain CNF build + Cadical/Minisat, signal.alarm bounded."""
import sys, os, signal, time, json
sys.path.insert(0, os.path.dirname(__file__))
import core
import constructions as C
from law_exact_sweep import lex_compose
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22


class TO(Exception):
    pass
def _a(s, f):
    raise TO()


def circ(p, g):
    return [(i, j) for i in range(p) for j in range(p)
            if i != j and ((j - i) % p) in g]


def fast_no_kK_cnf(n, arcs, K):
    beats = core.beats_matrix(n, arcs)
    idx = {}; nv = 0
    def lit(u, v):
        nonlocal nv
        if (u, v) in idx: return idx[(u, v)]
        if (v, u) in idx: return -idx[(v, u)]
        nv += 1; idx[(u, v)] = nv; return nv
    cnf = CNF()
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    nclq = 0
    chain = []
    def dfs(cands):
        nonlocal nclq
        if len(chain) == K:
            cnf.append([lit(chain[i], chain[i + 1]) for i in range(K - 1)])
            nclq += 1
            return
        for x in cands:
            chain.append(x)
            dfs([y for y in cands if y != x and beats[x][y]])
            chain.pop()
    allv = list(range(n))
    for a1 in allv:
        chain.append(a1)
        dfs([y for y in allv if y != a1 and beats[a1][y]])
        chain.pop()
    return cnf, nclq


def solve(cnf, solver, secs):
    signal.signal(signal.SIGALRM, _a); signal.setitimer(signal.ITIMER_REAL, secs)
    t0 = time.time()
    try:
        S = Minisat22 if solver == "m" else Cadical153
        with S(bootstrap_with=cnf.clauses) as mm:
            sat = mm.solve()
        signal.setitimer(signal.ITIMER_REAL, 0)
        return ((not sat), round(time.time() - t0, 3))
    except TO:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    out = {}
    C3 = C.directed_C3()
    nH, aH = lex_compose(C3[0], C3[1], C3[0], C3[1])
    aAC = circ(7, {1, 2, 4})
    nb, ab = lex_compose(7, aAC, nH, aH)
    print("order", nb, flush=True)
    signal.signal(signal.SIGALRM, _a); signal.setitimer(signal.ITIMER_REAL, 600)
    try:
        t0 = time.time(); cnf, ncl = fast_no_kK_cnf(nb, ab, 6)
        signal.setitimer(signal.ITIMER_REAL, 0)
        print(f"no-K6 CNF: {ncl} forbid-clauses, build {round(time.time()-t0,2)}s", flush=True)
        out["nclauses_k6"] = ncl
    except TO:
        print("K6 build timeout", flush=True); out["k6"] = "build_timeout"
        cnf = None
    if cnf is not None:
        rc = solve(cnf, "c", 400); rm = solve(cnf, "m", 400)
        out["k6_cadical_ge6"] = rc; out["k6_minisat_ge6"] = rm
        print(f"no-K6 cadical ge6(ov>=6)={rc}  minisat={rm}", flush=True)
        if rc and rm:
            if rc[0] is False and rm[0] is False:
                print("=> ov < 6 (no-K6 SAT): consistent with pred 5", flush=True)
            elif rc[0] is True and rm[0] is True:
                print("=> ov >= 6 (no-K6 UNSAT): VALUE EXCEEDS pred 5 -> KILL", flush=True)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "b_order63_k6.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
