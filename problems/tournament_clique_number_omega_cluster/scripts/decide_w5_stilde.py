"""Decide w_5 = omega_vec(S~_5) exactly, via no-K6 linear-ordering SAT (the P23 method).

S~_5 = C3 applied 4x to TT_1, order 81.  Proven lower bound w_5 >= 5 (omega_vec(S~_n) >= n).
no-K6 CNF SAT  <=>  some order has backedge clique <= 5  <=>  w_5 = 5.

RESULT (both Cadical153 + Minisat22, witness re-checked by core.omega_of_order): w_5 = 5.
Consequence (submultiplicativity of omega_vec under lex substitution, S~_{i+j-1}=S~_i[S~_j],
Fekete => rho = inf_n w_n^{1/(n-1)}):  rho <= w_5^{1/4} = 5^{1/4} ~ 1.4953 < 3/2.
So the S~_n growth constant is strictly below 3/2.  Also: w_n = n for n <= 5, so H19 holds
at every small level (S~_4 is NOT an H19 counterexample; the failure is asymptotic).
"""
import sys, os, functools, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
from lexlib import lex_substitute, C3, is_tournament
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

def _alarm(s, f):
    print("SELF-ALARM TIMEOUT", flush=True); sys.exit(2)
signal.signal(signal.SIGALRM, _alarm); signal.alarm(585)

def stilde(n):
    T = (1, [])                      # TT_1 = S~_1
    for _ in range(n - 1): T = lex_substitute(C3, T)
    return T

def decide(n_tower=5, K=5, print_order=False):
    n, arcs = stilde(n_tower)
    assert is_tournament(n, arcs)
    print(f"S~_{n_tower} order {n}; deciding omega_vec <= {K} (no-K{K+1} SAT)", flush=True)
    out = [0]*n; b = [[False]*n for _ in range(n)]
    for u, v in arcs: b[u][v] = True
    for u in range(n):
        msk = 0
        for v in range(n):
            if b[u][v]: msk |= (1 << v)
        out[u] = msk
    res = []; ap = res.append
    def rec(ch, cand):
        if len(ch) == K+1: ap(tuple(ch)); return
        m = cand
        while m:
            v = (m & -m).bit_length()-1; m &= m-1; rec(ch+[v], cand & out[v])
    for s in range(n): rec([s], out[s])
    idx = {}; nv = [0]
    def lit(u, v):
        if (u, v) in idx: return idx[(u, v)]
        if (v, u) in idx: return -idx[(v, u)]
        nv[0] += 1; idx[(u, v)] = nv[0]; return nv[0]
    for u in range(n):
        for v in range(u+1, n): lit(u, v)
    cnf = CNF()
    for u in range(n):
        for v in range(n):
            if v != u:
                for w in range(n):
                    if w != u and w != v: cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    for ch in res: cnf.append([lit(ch[i], ch[i+1]) for i in range(K)])
    t = time.time()
    s = Cadical153(bootstrap_with=cnf.clauses); sat = s.solve()
    s2 = Minisat22(bootstrap_with=cnf.clauses); sat2 = s2.solve()
    assert sat == sat2, "SOLVER DISAGREEMENT"
    print(f"  no-K{K+1} SAT = {sat} on both solvers  [{len(res)} chains, {time.time()-t:.1f}s]", flush=True)
    if sat:
        model = set(s.get_model())
        prec = lambda u, v: (lit(u, v) in model) if lit(u, v) > 0 else ((-lit(u, v)) not in model)
        order = sorted(range(n), key=functools.cmp_to_key(lambda a, b: 0 if a == b else (-1 if prec(a, b) else 1)))
        w = core.omega_of_order(n, arcs, order)
        assert w <= K, f"witness clique {w} > {K}"
        print(f"  INDEPENDENT CHECK omega_of_order(witness) = {w}", flush=True)
        if n_tower == 5 and K == 5:
            print(
                f"  => w_5 = {w} = 5.   "
                f"rho <= 5^(1/4) = {5**0.25:.5f} < 1.5",
                flush=True,
            )
        else:
            print(f"  => omega_vec(S~_{n_tower}) <= {w}", flush=True)
        if print_order:
            print("  witness order =", order, flush=True)
        result = {"sat": True, "order": order, "omega": w}
    else:
        print(f"  => omega_vec(S~_{n_tower}) >= {K+1}", flush=True)
        result = {"sat": False, "order": None, "omega": None}
    s.delete(); s2.delete()
    return result

if __name__ == "__main__":
    decide(print_order=True)
