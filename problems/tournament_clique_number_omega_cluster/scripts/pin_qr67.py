"""Pin omega_vec(QR_67) EXACTLY (next_action D23 ROUND-1 EXECUTOR TASK).

QR_67 = Paley(67), p=67 == 3 mod 4 (so a tournament). Arc i->j iff (j-i) mod 67
is a quadratic residue mod 67. D23 found an explicit order with backedge clique 6,
so omega_vec(QR_67) in {5,6}. This script pins it:

 UPPER: omega_of_order on the stored D23 best_order  (= 6).
 LOWER: (i) dom(QR_67) via Property 3.2 dom<=omega_vec (O(p^2) additive + direct);
        (ii) no-K6 SAT betweenness: UNSAT => omega_vec>=6  (the decider).
        (iii) no-K5 SAT: UNSAT => omega_vec>=5 (sanity floor).

If omega_vec(QR_67)=6 AND no-K5-on-deletion shows every deletion omega_vec=5
(vertex-transitive => single vertex), QR_67 is the FIRST k=6 critical witness.
This script does the VALUE pin (k=6 existence); criticality is a follow-up only if =6.

All SAT/dom calls are FOREGROUND with signal.alarm hard timeouts.
"""
import sys, os, signal, time, json
sys.path.insert(0, os.path.dirname(__file__))
import core
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22


class TO(Exception):
    pass


def _a(s, f):
    raise TO()


def qr_set(p):
    return set((x * x) % p for x in range(1, p)) - {0}


def circ(p, g):
    # arc i->j iff (j-i)%p in g
    return [(i, j) for i in range(p) for j in range(p)
            if i != j and ((j - i) % p) in g]


def dom_additive_le_k(p, g, k):
    """dom(T)<=k iff some k translates of N0={0}|g cover Z/p (closed out-nbhd).
    Returns smallest cover size up to k+1 (k+1 means >k). Greedy+exhaustive small k."""
    import itertools
    N0 = set(d % p for d in ({0} | set(g)))
    full = set(range(p))
    # translates: T_t = t + N0  (vertex t's closed out-neighborhood when shifted)
    # Actually dom set X: union_{x in X}(x+N0)=Z/p. By transitivity test all small X.
    translates = [set((d + t) % p for d in N0) for t in range(p)]
    for size in range(1, k + 1):
        # exhaustive only cheap for size<=3; use that
        if size <= 3:
            for X in itertools.combinations(range(p), size):
                cov = set()
                for x in X:
                    cov |= translates[x]
                if cov == full:
                    return size
        else:
            return None  # not decided cheaply
    return k + 1  # > k


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
        return ((not sat), round(time.time() - t0, 3))  # (is_UNSAT, secs)
    except TO:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    p = 67
    g = qr_set(p)
    arcs = circ(p, g)
    out = {"p": p, "g_sorted": sorted(g), "g_size": len(g)}
    out["is_tournament"] = core.is_tournament(p, arcs)
    print("QR_67 |g|=", len(g), "is_tournament=", out["is_tournament"], flush=True)

    # UPPER via stored D23 best_order
    best_order = [7, 40, 46, 54, 34, 66, 33, 38, 5, 64, 42, 4, 59, 13, 60, 15, 0,
                  43, 58, 47, 23, 8, 36, 3, 55, 61, 1, 2, 22, 37, 62, 31, 17, 30,
                  19, 6, 48, 29, 27, 57, 26, 63, 50, 25, 24, 21, 20, 9, 10, 18,
                  16, 14, 28, 51, 35, 56, 53, 49, 45, 11, 44, 12, 41, 39, 32, 52, 65]
    assert sorted(best_order) == list(range(p))
    up = core.omega_of_order(p, arcs, best_order)
    out["upper_omega_of_best_order"] = up
    print("UPPER: omega_of_order(best_order) =", up, flush=True)

    # LOWER via dom (Property 3.2 dom<=omega_vec)
    t0 = time.time()
    dom_k = dom_additive_le_k(p, g, 3)
    out["dom_le3_probe"] = dom_k  # value v<=3 means dom=v; 4 means dom>3
    out["dom_probe_time_s"] = round(time.time() - t0, 2)
    print("dom (additive, cap size<=3):", dom_k, "(>3 means dom>=4)", flush=True)

    # LOWER via SAT: no-K5 then no-K6
    signal.signal(signal.SIGALRM, _a); signal.setitimer(signal.ITIMER_REAL, 600)
    try:
        t0 = time.time(); cnf5, n5 = fast_no_kK_cnf(p, arcs, 5)
        signal.setitimer(signal.ITIMER_REAL, 0)
        out["nclauses_k5"] = n5
        print(f"no-K5 CNF built: {n5} forbid-clauses, {round(time.time()-t0,2)}s", flush=True)
    except TO:
        out["k5"] = "build_timeout"; cnf5 = None
        print("no-K5 build timeout", flush=True)
    if cnf5 is not None:
        r5c = solve(cnf5, "c", 300); r5m = solve(cnf5, "m", 300)
        out["no_k5_cadical_unsat_ge5"] = r5c
        out["no_k5_minisat_unsat_ge5"] = r5m
        print(f"no-K5 cadical (UNSAT=>ov>=5): {r5c}  minisat: {r5m}", flush=True)

    signal.signal(signal.SIGALRM, _a); signal.setitimer(signal.ITIMER_REAL, 600)
    try:
        t0 = time.time(); cnf6, n6 = fast_no_kK_cnf(p, arcs, 6)
        signal.setitimer(signal.ITIMER_REAL, 0)
        out["nclauses_k6"] = n6
        print(f"no-K6 CNF built: {n6} forbid-clauses, {round(time.time()-t0,2)}s", flush=True)
    except TO:
        out["k6"] = "build_timeout"; cnf6 = None
        print("no-K6 build timeout", flush=True)
    if cnf6 is not None:
        r6c = solve(cnf6, "c", 400); r6m = solve(cnf6, "m", 400)
        out["no_k6_cadical_unsat_ge6"] = r6c
        out["no_k6_minisat_unsat_ge6"] = r6m
        print(f"no-K6 cadical (UNSAT=>ov>=6): {r6c}  minisat: {r6m}", flush=True)
        if r6c and r6m:
            if r6c[0] and r6m[0]:
                out["verdict"] = "omega_vec(QR_67)=6 (no-K6 UNSAT + upper order=6)"
            elif r6c[0] is False and r6m[0] is False:
                out["verdict"] = "omega_vec(QR_67)=5 (no-K6 SAT => ov<=5; if no-K5 UNSAT then =5)"

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "pin_qr67.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
