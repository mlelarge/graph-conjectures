"""(b) AC_7[C3[C3]] order 63: pin omega_vec value vs prediction 5.

UPPER bound (ov<=5): structured NSS/lex order = outer omega_vec-optimal order of
AC_7, refined within each outer block by an omega_vec-optimal order of the inner
C3[C3]; report the backedge clique number under that order (a valid upper bound).
Also random shuffles as a sanity floor.

LOWER bound (ov>=5): no-K5 SAT betweenness CNF UNSAT.  We build the K=5
forbidding clauses with a FAST enumeration (iterate transitive 5-subsets by
growing transitive chains s_1->s_2->...->s_5 along the beats relation), wrapped
in signal.alarm.  UNSAT => ov>=5.

If upper==5 and lower says ov>=5 -> value EXACTLY 5 = prediction.  KILL iff
value > 5 (ov_ge_6 i.e. no-K6 UNSAT) or upper-bound order itself forces >5
inconsistently.
"""
import sys, os, signal, time, json
sys.path.insert(0, os.path.dirname(__file__))
import core
import constructions as C
from law_exact_sweep import lex_compose
from pysat.solvers import Cadical153, Minisat22


class TO(Exception):
    pass


def _a(s, f):
    raise TO()


def circ(p, g):
    return [(i, j) for i in range(p) for j in range(p)
            if i != j and ((j - i) % p) in g]


def optimal_order(n, arcs):
    """An omega_vec-optimal total order (min backedge omega) for small n, by
    exhaustive/bb search returning the witnessing order."""
    import itertools
    beats = core.beats_matrix(n, arcs)
    best = None
    best_w = n + 1
    for perm in itertools.permutations(range(n)):
        w = core.omega_of_order(n, arcs, list(perm))
        if w < best_w:
            best_w = w
            best = list(perm)
            if best_w == 1:
                break
    return best, best_w


def fast_no_k5_cnf(n, arcs):
    """Build CNF SAT-iff-some-order has K5-free backedge graph.
    Variables x_{u<v}.  Transitivity 3-clauses.  For each transitive 5-subset
    with acyclic order s1->...->s5 (s1 source), forbid full reverse placement:
    clause (s1<s2) OR (s2<s3) OR (s3<s4) OR (s4<s5).
    Fast transitive-5-chain enumeration via DFS along beats (chains s1>s2>...>s5
    with all pairwise beats = transitive subset)."""
    from pysat.formula import CNF
    beats = core.beats_matrix(n, arcs)
    idx = {}
    nv = 0

    def lit(u, v):
        nonlocal nv
        if (u, v) in idx:
            return idx[(u, v)]
        if (v, u) in idx:
            return -idx[(v, u)]
        nv += 1
        idx[(u, v)] = nv
        return nv

    cnf = CNF()
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    # transitivity
    for u in range(n):
        for v in range(n):
            if v == u:
                continue
            for w in range(n):
                if w == u or w == v:
                    continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    # transitive 5-subsets: chains a1->a2->...->a5 with a_i beats a_j for i<j.
    # DFS extending a transitive chain (every new vertex beaten by all in chain).
    nclq = 0
    chain = []

    def dfs(cands):
        nonlocal nclq
        if len(chain) == 5:
            # forbid reverse: clause OR over (chain[i] < chain[i+1])
            cnf.append([lit(chain[i], chain[i + 1]) for i in range(4)])
            nclq += 1
            return
        for x in cands:
            # x must be beaten by all current chain members (chain members beat x)
            # new candidates: those in cands beaten by x as well, and >? we need
            # transitivity: keep only y in cands with x beats y and chain beats y.
            chain.append(x)
            ncands = [y for y in cands if y != x and beats[x][y]]
            dfs(ncands)
            chain.pop()

    # start: every vertex as a1; cands = vertices it beats
    allv = list(range(n))
    for a1 in allv:
        chain.append(a1)
        dfs([y for y in allv if y != a1 and beats[a1][y]])
        chain.pop()
    return cnf, nclq


def geK_via_cnf(cnf, solver, secs):
    signal.signal(signal.SIGALRM, _a)
    signal.setitimer(signal.ITIMER_REAL, secs)
    t0 = time.time()
    try:
        S = Minisat22 if solver == "m" else Cadical153
        with S(bootstrap_with=cnf.clauses) as m:
            sat = m.solve()
        signal.setitimer(signal.ITIMER_REAL, 0)
        return ((not sat), round(time.time() - t0, 3))
    except TO:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    out = {}
    C3 = C.directed_C3()
    nH, aH = lex_compose(C3[0], C3[1], C3[0], C3[1])   # C3[C3], order 9, ov 3
    ovH = core.omega_vec(nH, aH)
    aAC = circ(7, {1, 2, 4})
    ovAC = core.omega_vec(7, aAC)
    nb, ab = lex_compose(7, aAC, nH, aH)               # order 63
    out["ovH"] = ovH
    out["ovAC7"] = ovAC
    out["order"] = nb
    print(f"ovH={ovH} ovAC7={ovAC} order={nb}", flush=True)

    # ---- UPPER BOUND via structured NSS/lex order ----
    oAC, wAC = optimal_order(7, aAC)
    oH, wH = optimal_order(nH, aH)
    print(f"AC7 opt order backedge-omega={wAC}; C3[C3] opt order backedge-omega={wH}",
          flush=True)
    # vertices of product = a*9 + b ; outer index a (in AC7), inner b (in C3[C3]).
    # lex order: outer by oAC, inner by oH.
    posH = {v: i for i, v in enumerate(oH)}
    posAC = {v: i for i, v in enumerate(oAC)}
    verts = list(range(nb))
    order = sorted(verts, key=lambda x: (posAC[x // 9], posH[x % 9]))
    w_struct = core.omega_of_order(nb, ab, order)
    out["upper_structured_lex"] = w_struct
    print(f"UPPER (structured lex order) backedge-omega = {w_struct}", flush=True)

    # ---- LOWER BOUND ov>=5 via no-K5 SAT ----
    print("building no-K5 CNF (fast chain enum)...", flush=True)
    signal.signal(signal.SIGALRM, _a)
    signal.setitimer(signal.ITIMER_REAL, 500)
    try:
        t0 = time.time()
        cnf5, ncl5 = fast_no_k5_cnf(nb, ab)
        signal.setitimer(signal.ITIMER_REAL, 0)
        build5 = round(time.time() - t0, 2)
        out["nclauses_k5"] = ncl5
        out["build5_s"] = build5
        print(f"  K5 CNF: {ncl5} forbid-clauses, build {build5}s", flush=True)
        rc = geK_via_cnf(cnf5, "c", 400)
        rm = geK_via_cnf(cnf5, "m", 400)
        out["k5_cadical_ge5"] = rc
        out["k5_minisat_ge5"] = rm
        print(f"  no-K5 cadical ge5(ov>=5)={rc}  minisat={rm}", flush=True)
    except TO:
        out["k5_status"] = "build_timeout"
        print("  K5 build TIMEOUT", flush=True)

    # ---- check NOT ov>=6 (no-K6 should be SAT) for the exact value ----
    # cheap sufficiency: structured upper bound already <=5 pins ov<=5 if w_struct<=5.
    out["value_conclusion"] = None
    if out.get("upper_structured_lex") is not None:
        ub = out["upper_structured_lex"]
        lo = None
        rc = out.get("k5_cadical_ge5")
        rm = out.get("k5_minisat_ge5")
        if rc and rm and rc[0] is True and rm[0] is True:
            lo = 5
        if lo == 5 and ub == 5:
            out["value_conclusion"] = "EXACTLY 5 (= pred) : PASS"
        elif lo == 5 and ub > 5:
            out["value_conclusion"] = f"ov>=5 but structured order only gives {ub}; need tighter UB"
        elif ub == 5 and lo is None:
            out["value_conclusion"] = "ov<=5 (UB); lower bound unresolved"
        else:
            out["value_conclusion"] = f"ub={ub} lo={lo}"
    print("CONCLUSION:", out.get("value_conclusion"), flush=True)

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "b_order63.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
