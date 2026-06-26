"""DECIDE ov(C3[QR_19]) in {5,6}  (next_action lever 1, cheap add-on / sharp discriminator).

C3[QR_19] = lex substitution: OUTER C3 (order 3), INNER QR_19 (order 19) -> order 57.
ov(C3) = 2, ov(QR_19) = 4. PROVEN lex lower bound:
    omega_vec(C3[QR_19]) >= ov(C3)+ov(QR_19)-1 = 5.
So the value is in {5,6}; this script decides which.

DECISION (sound, certificate-checked):
  omega_vec(T) <= 5  IFF  there EXISTS a total order whose backedge graph has NO 6-clique.
  Encode with the standard linear-ordering CNF (same encoding as the red-team-passed
  ground_noK6_witness.py): boolean x_{uv} = "u precedes v"; transitivity 3-clauses;
  and for EVERY transitive 6-subset (as a source->...->sink chain s_1..s_6) one clause
  forbidding it being realised source-to-sink (i.e. forbidding a backedge 6-clique).
    SAT   => witness order exists with backedge clique <= 5 => omega_vec = 5
             (re-verified by core.omega_of_order on the reconstructed order, fully
              independent of SAT; the proven lex lower bound = 5 pins it to exactly 5).
    UNSAT => no order avoids a backedge 6-clique => omega_vec = 6.

If SAT (ov=5): the H21 overshoot-to-6 on C3[QR_19] is a GENUINE mechanism failure
  (the merged order is suboptimal), the load-bearing-property discriminator becomes real.
If UNSAT (ov=6): C3[QR_19] is a (structured, order-57) omega_vec=6 tournament =>
  ell(6) gets a witness AND the H21 "overshoot" is correct, not a failure.
"""
import sys, os, time, signal, functools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lexlib import lex_substitute, C3, is_tournament
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22


def _alarm(sig, frm):
    print("SELF-ALARM TIMEOUT", flush=True)
    sys.exit(2)
signal.signal(signal.SIGALRM, _alarm)
signal.alarm(560)

# ---- build C3[QR_19] (outer C3, inner QR_19) ----
QR = sorted({(x * x) % 19 for x in range(1, 19)})
arcs19 = [(i, (i + d) % 19) for i in range(19) for d in QR]
assert core.is_tournament(19, arcs19), "QR_19 not a tournament"
QR19 = (19, arcs19)
n, arcs = lex_substitute(C3, QR19)
assert is_tournament(n, arcs)
print("object C3[QR_19]  order", n, "tournament", True, "QR=", QR, flush=True)

# sanity: ov(QR_19) should be 4 (cheap upper-bound spot-check via identity-ish order is not needed;
# we trust the ledger-proven value; lower bound below is what we decide).

beats = [[False] * n for _ in range(n)]
for (u, v) in arcs:
    beats[u][v] = True
out = [0] * n
for u in range(n):
    m = 0
    for v in range(n):
        if beats[u][v]:
            m |= (1 << v)
    out[u] = m

# ---- enumerate all transitive 6-subsets as source->sink chains ----
def enum_chains(K):
    res = []
    ap = res.append
    def rec(chosen, cand):
        if len(chosen) == K:
            ap(tuple(chosen)); return
        m = cand
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            rec(chosen + [v], cand & out[v])
    for s in range(n):
        rec([s], out[s])
    return res

t0 = time.time()
chains = enum_chains(6)
print("transitive 6-chains:", len(chains), "(%.2fs)" % (time.time() - t0), flush=True)

# ---- CNF ----
idx = {}; nv = [0]
def lit(u, v):
    if (u, v) in idx:
        return idx[(u, v)]
    if (v, u) in idx:
        return -idx[(v, u)]
    nv[0] += 1; idx[(u, v)] = nv[0]; return nv[0]
for u in range(n):
    for v in range(u + 1, n):
        lit(u, v)
cnf = CNF()
for u in range(n):
    for v in range(n):
        if v == u: continue
        for w in range(n):
            if w == u or w == v: continue
            cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
for ch in chains:
    cnf.append([lit(ch[i], ch[i + 1]) for i in range(5)])
print("CNF vars", nv[0], "clauses", len(cnf.clauses), flush=True)

# ---- solve (two solvers for soundness) ----
t1 = time.time()
s = Cadical153(bootstrap_with=cnf.clauses)
sat = s.solve()
print("Cadical153 no-K6 SAT =", sat, "(%.2fs)" % (time.time() - t1), flush=True)

t2 = time.time()
s2 = Minisat22(bootstrap_with=cnf.clauses)
sat2 = s2.solve()
print("Minisat22 no-K6 SAT =", sat2, "(%.2fs)" % (time.time() - t2), flush=True)
assert sat == sat2, "SOLVER DISAGREEMENT"

if sat:
    model = set(s.get_model())
    def precedes(u, v):
        l = lit(u, v)
        return (l in model) if l > 0 else ((-l) not in model)
    def cmp(a, b):
        if a == b: return 0
        return -1 if precedes(a, b) else 1
    order = sorted(range(n), key=functools.cmp_to_key(cmp))
    w = core.omega_of_order(n, arcs, order)
    print("INDEPENDENT CHECK backedge clique of SAT witness order =", w, flush=True)
    assert w <= 5, "SAT witness gave clique %d > 5 -- encoding bug" % w
    print("RESULT ov(C3[QR_19]) = 5  (upper bound 5 via witness order + proven lex lower bound 5)",
          flush=True)
    print("VERDICT VALUE=5", flush=True)
else:
    print("RESULT ov(C3[QR_19]) = 6  (no order avoids a backedge 6-clique => omega_vec=6)",
          flush=True)
    print("VERDICT VALUE=6", flush=True)
s.delete(); s2.delete()
print("DONE", flush=True)
