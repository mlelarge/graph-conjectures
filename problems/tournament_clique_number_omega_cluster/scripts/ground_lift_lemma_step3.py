"""D31 lift-lemma STEP 3: dic propagation + X5 = AC_7[AC_7] dic-criticality.

(b) dic(C3[AC_7]) = 4 with deletion dic 3 (VT, single deletion).
(c) AC_7[AC_7] (order 49, P19: 5-omega_vec-critical): dic<=4 UNSAT (so dic=5,
    since omega_vec=5 <= dic <= 5) and deletion dic<=4 SAT (so dic(T-v)=4,
    since omega_vec(T-v)=4 <= dic(T-v)).
Saves the 5-dicoloring of AC_7[AC_7] and the 4-dicoloring of AC_7[AC_7]-v
for the step-4 strike order.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
from lexlib import AC, lex_substitute, is_tournament
from constructions import directed_C3
from pysat.solvers import Cadical153

def beats(n, arcs):
    b = [[False]*n for _ in range(n)]
    for (u,v) in arcs: b[u][v]=True
    return b

def directed_triangles(n, arcs):
    b = beats(n, arcs)
    return [(u,v,w) for u,v,w in itertools.combinations(range(n),3)
            if (b[u][v] and b[v][w] and b[w][u]) or (b[v][u] and b[w][v] and b[u][w])]

def dicolor_model(n, arcs, k, tris=None):
    """Return a k-dicoloring (list of colors) or None if UNSAT."""
    if tris is None: tris = directed_triangles(n, arcs)
    var = lambda v,c: v*k + c + 1
    cls = [[var(v,c) for c in range(k)] for v in range(n)]
    for (u,v,w) in tris:
        for c in range(k):
            cls.append([-var(u,c), -var(v,c), -var(w,c)])
    cls.append([var(0,0)])
    t0 = time.time()
    with Cadical153(bootstrap_with=cls) as m:
        ok = m.solve()
        if not ok:
            return None, time.time()-t0
        mod = set(l for l in m.get_model() if l > 0)
        col = [next(c for c in range(k) if var(v,c) in mod) for v in range(n)]
        return col, time.time()-t0

def sub(n, arcs, delv):
    keep = [v for v in range(n) if v != delv]
    idx = {v:i for i,v in enumerate(keep)}
    return n-1, [(idx[u],idx[v]) for (u,v) in arcs if u!=delv and v!=delv]

def main():
    out = {}
    # (b) C3[AC_7], order 21
    T21 = lex_substitute(directed_C3(), AC(7,[1,2,4]))
    n, arcs = T21
    tris = directed_triangles(n, arcs)
    c3, t3 = dicolor_model(n, arcs, 3, tris)
    c4, t4 = dicolor_model(n, arcs, 4, tris)
    nn, aa = sub(n, arcs, 0)
    cd3, td3 = dicolor_model(nn, aa, 3)
    out['C3[AC_7]'] = dict(order=n, ntri=len(tris),
                           dic_le3=(c3 is not None), dic_le4=(c4 is not None),
                           del_dic_le3=(cd3 is not None),
                           times=[t3,t4,td3])
    print(f"C3[AC_7]: dic<=3 {c3 is not None} ({t3:.1f}s); dic<=4 {c4 is not None} ({t4:.1f}s); "
          f"deletion dic<=3 {cd3 is not None} ({td3:.1f}s)", flush=True)

    # (c) AC_7[AC_7], order 49
    X5 = lex_substitute(AC(7,[1,2,4]), AC(7,[1,2,4]))
    n, arcs = X5
    assert is_tournament(n, arcs)
    tris = directed_triangles(n, arcs)
    print(f"AC_7[AC_7]: order {n}, directed triangles {len(tris)}", flush=True)
    c4, t4 = dicolor_model(n, arcs, 4, tris)
    print(f"AC_7[AC_7]: dic<=4 {c4 is not None} ({t4:.1f}s)", flush=True)
    c5, t5 = dicolor_model(n, arcs, 5, tris)
    print(f"AC_7[AC_7]: dic<=5 {c5 is not None} ({t5:.1f}s)", flush=True)
    nn, aa = sub(n, arcs, 0)
    cd4, td4 = dicolor_model(nn, aa, 4)
    print(f"AC_7[AC_7]-v0: dic<=4 {cd4 is not None} ({td4:.1f}s)", flush=True)
    out['AC_7[AC_7]'] = dict(order=n, ntri=len(tris),
                             dic_le4=(c4 is not None), dic_le5=(c5 is not None),
                             del_dic_le4=(cd4 is not None),
                             coloring5=c5, del_coloring4=cd4,
                             times=[t4,t5,td4])
    json.dump(out, open(os.path.join(os.path.dirname(__file__),'..','data','lift_lemma_step3.json'),'w'), indent=1)
    print("saved data/lift_lemma_step3.json", flush=True)

if __name__ == '__main__':
    main()
