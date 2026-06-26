"""Bounded no-K5 SAT decision on C3[QR_19] - v0 (order 56).

Skeptic feasibility probe: build the same no-K5 CNF as
ground_c3_qr19_criticality.py and try to SOLVE it with a hard internal
time budget, so the command returns DEFINITIVELY (SAT/UNSAT) or cleanly
reports INDETERMINATE inside one foreground turn.  No background, no poll.
"""
import sys, os, time, signal, functools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lexlib import lex_substitute, C3, is_tournament

BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 240  # wall seconds for solve

NI = 19
QR = sorted({(x * x) % 19 for x in range(1, 19)})
arcs19 = [(i, (i + d) % 19) for i in range(19) for d in QR]
QR19 = (19, arcs19)
N, ARCS = lex_substitute(C3, QR19)
assert is_tournament(N, ARCS)
V0 = 0
surv = [u for u in range(N) if u != V0]
relabel = {u: i for i, u in enumerate(surv)}
Nd = len(surv)
arcs_d = [(relabel[u], relabel[v]) for (u, v) in ARCS if u != V0 and v != V0]
assert core.is_tournament(Nd, arcs_d)
print("T-v0 order", Nd, flush=True)

from pysat.formula import CNF
from pysat.solvers import Cadical153

out = [0] * Nd
for (u, v) in arcs_d:
    out[u] |= (1 << v)

def enum_chains(K):
    res = []; ap = res.append
    def rec(chosen, cand):
        if len(chosen) == K:
            ap(tuple(chosen)); return
        m = cand
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            rec(chosen + [v], cand & out[v])
    for s in range(Nd):
        rec([s], out[s])
    return res

t0 = time.time()
chains = enum_chains(5)
print("transitive 5-chains:", len(chains), "(%.2fs)" % (time.time() - t0), flush=True)

idx = {}; nv = [0]
def lit(u, v):
    if (u, v) in idx: return idx[(u, v)]
    if (v, u) in idx: return -idx[(v, u)]
    nv[0] += 1; idx[(u, v)] = nv[0]; return nv[0]
for u in range(Nd):
    for v in range(u + 1, Nd):
        lit(u, v)
cnf = CNF()
for u in range(Nd):
    for v in range(Nd):
        if v == u: continue
        for w in range(Nd):
            if w == u or w == v: continue
            cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
for ch in chains:
    cnf.append([lit(ch[i], ch[i + 1]) for i in range(4)])
print("CNF vars", nv[0], "clauses", len(cnf.clauses), flush=True)

# hard self-alarm so the PROCESS itself returns cleanly well inside the
# foreground command timeout
def _alarm(sig, frm):
    print("INDETERMINATE: solver budget %ds elapsed, no SAT/UNSAT" % BUDGET, flush=True)
    print("VERDICT INDETERMINATE", flush=True)
    os._exit(0)
signal.signal(signal.SIGALRM, _alarm)
signal.alarm(BUDGET)

t1 = time.time()
s = Cadical153(bootstrap_with=cnf.clauses)
sat = s.solve()
signal.alarm(0)
dt = time.time() - t1
print("Cadical153 no-K5 SAT =", sat, "(%.2fs)" % dt, flush=True)
if sat:
    model = set(s.get_model())
    def precedes(u, v):
        l = lit(u, v)
        return (l in model) if l > 0 else ((-l) not in model)
    order = sorted(range(Nd), key=functools.cmp_to_key(
        lambda a, b: 0 if a == b else (-1 if precedes(a, b) else 1)))
    w = core.omega_of_order(Nd, arcs_d, order)
    print("INDEPENDENT CHECK clique =", w, flush=True)
    assert w <= 4
    print("VERDICT 5-CRITICAL (KILL prediction: ov(T-v0)=4)", flush=True)
else:
    print("VERDICT NOT-5-CRITICAL (CONFIRM: ov(T-v0)=5, no-K5 UNSAT)", flush=True)
s.delete()
print("DONE", flush=True)
