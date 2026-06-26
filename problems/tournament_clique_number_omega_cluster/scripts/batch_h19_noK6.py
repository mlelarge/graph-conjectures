"""Batch verification of H19 via direct no-K6 SAT on C3[H], for inner-ov=4 critical H.

For each H with ov(H)=4: omega_vec(C3[H]) >= 5 (lex lower bound).  The no-K6 linear-order
CNF is SAT iff some order has backedge clique <= 5.
   SAT   => omega_vec(C3[H]) = 5  => H19 holds for H.
   UNSAT => omega_vec(C3[H]) >= 6 => H19 FAILS for H (and C3[H] is a FIRST omega_vec>=6
            object -- an ell(6) witness).  Each SAT result is re-checked independently by
            core.omega_of_order on the reconstructed order; both Cadical153 and Minisat22 run.

SCOPE (honest): inner-ov=4 tournaments are rare (smallest order 19), so this batch is
STRUCTURED -- circulant {QR_19, AC4_21, H1*, H2*} and substitution {AC_n[C3], C3[H7]}.
It is NOT a generic census; it tests two structured families, the substitution one being
the harder (AC_7[C3] needed a non-optimal inner order).  A single UNSAT refutes H19.
"""
import sys, os, time, signal, functools
sys.path.insert(0, os.path.dirname(__file__))
import core
from lexlib import lex_substitute, C3, is_tournament
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

def circ(n, g):
    g = set(g % n for g in g)
    return [(i, (i + d) % n) for i in range(n) for d in g]

def AC(n):                       # almost-consecutive AC_n, n=2m+1: g={1..m-1} U {m+1}
    m = (n - 1) // 2
    return (n, circ(n, set(range(1, m)) | {m + 1}))

QR19 = (19, [(i, (i + d) % 19) for i in range(19) for d in sorted({(x*x) % 19 for x in range(1,19)})])
AC4_21 = (21, circ(21, {1,2,4,7,8,9,11,15,16,18}))
H1 = (25, circ(25, {1,2,3,4,5,6,7,9,10,12,14,17}))
H2 = (25, circ(25, {1,2,3,4,5,6,7,9,11,12,15,17}))
import json
_h7 = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "h16_counterexample.json")))
H7 = (7, [tuple(a) for a in _h7["H7"]["arcs"]])

def acC3(n):  return lex_substitute(AC(n), C3)      # AC_n[C3], order 3n, ov=4
def c3H7():   return lex_substitute(C3, H7)          # C3[H7], order 21, ov=4

# (label, inner H tournament, family) -- ordered by C3[H] size
CANDIDATES = [
    ("QR_19",        QR19,      "circulant"),
    ("AC4_21",       AC4_21,    "circulant"),
    ("AC_7[C3]",     acC3(7),   "substitution"),
    ("C3[H7]",       c3H7(),    "substitution"),
    ("H1*",          H1,        "circulant"),
    ("H2*",          H2,        "circulant"),
    ("AC_9[C3]",     acC3(9),   "substitution"),
    ("AC_11[C3]",    acC3(11),  "substitution"),
    ("AC_13[C3]",    acC3(13),  "substitution"),
]

class TO(Exception): pass
def _a(s, f): raise TO()

def decide_noK6(label, H, per_obj_timeout=170):
    n, arcs = lex_substitute(C3, H)
    assert is_tournament(n, arcs)
    signal.signal(signal.SIGALRM, _a); signal.alarm(per_obj_timeout)
    try:
        out = [0]*n
        b = [[False]*n for _ in range(n)]
        for u,v in arcs: b[u][v] = True
        for u in range(n):
            msk = 0
            for v in range(n):
                if b[u][v]: msk |= (1<<v)
            out[u] = msk
        # transitive 6-chains
        res=[]; ap=res.append
        def rec(ch, cand):
            if len(ch)==6: ap(tuple(ch)); return
            m=cand
            while m:
                v=(m&-m).bit_length()-1; m&=m-1; rec(ch+[v], cand & out[v])
        for s in range(n): rec([s], out[s])
        idx={}; nv=[0]
        def lit(u,v):
            if (u,v) in idx: return idx[(u,v)]
            if (v,u) in idx: return -idx[(v,u)]
            nv[0]+=1; idx[(u,v)]=nv[0]; return nv[0]
        for u in range(n):
            for v in range(u+1,n): lit(u,v)
        cnf=CNF()
        for u in range(n):
            for v in range(n):
                if v!=u:
                    for w in range(n):
                        if w!=u and w!=v: cnf.append([-lit(u,v),-lit(v,w),lit(u,w)])
        for ch in res: cnf.append([lit(ch[i],ch[i+1]) for i in range(5)])
        s=Cadical153(bootstrap_with=cnf.clauses); sat=s.solve()
        s2=Minisat22(bootstrap_with=cnf.clauses); sat2=s2.solve()
        assert sat==sat2, "SOLVER DISAGREEMENT on "+label
        wclique=None
        if sat:
            model=set(s.get_model())
            prec=lambda u,v:(lit(u,v) in model) if lit(u,v)>0 else ((-lit(u,v)) not in model)
            order=sorted(range(n), key=functools.cmp_to_key(lambda a,b:0 if a==b else(-1 if prec(a,b) else 1)))
            wclique=core.omega_of_order(n,arcs,order)
            assert wclique<=5, f"{label}: SAT witness clique {wclique}>5 (encoding bug)"
        s.delete(); s2.delete()
        signal.alarm(0)
        return {"order":n, "n_chains":len(res), "sat":sat,
                "omega_vec_C3H": 5 if sat else ">=6", "witness_clique": wclique}
    except TO:
        signal.alarm(0)
        return {"order":n, "timeout":True}

def main():
    print(f"{'H':<12}{'family':<14}{'C3[H] order':<13}{'no-K6 SAT':<11}{'omega_vec(C3[H])':<17}result", flush=True)
    print("-"*78, flush=True)
    refuted=[]
    for label, H, fam in CANDIDATES:
        t0=time.time()
        r=decide_noK6(label, H)
        if r.get("timeout"):
            print(f"{label:<12}{fam:<14}{r['order']:<13}{'(timeout)':<11}{'?':<17}skipped", flush=True)
            continue
        verdict = "H19 holds (=ov+1)" if r["sat"] else "*** H19 FAILS -> omega_vec>=6 PRIZE ***"
        print(f"{label:<12}{fam:<14}{r['order']:<13}{str(r['sat']):<11}{r['omega_vec_C3H']:<17}{verdict}  "
              f"[{time.time()-t0:.1f}s]", flush=True)
        if not r["sat"]: refuted.append(label)
    print("-"*78, flush=True)
    if refuted:
        print(f"H19 REFUTED for: {refuted}  -- these give omega_vec(C3[H])>=6 objects.", flush=True)
    else:
        print("H19 CONFIRMED (=ov+1=5) on EVERY tested inner-ov=4 critical H (structured sample).", flush=True)

if __name__=="__main__":
    main()
