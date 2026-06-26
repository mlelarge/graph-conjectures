"""D31 lift-lemma STEP 2: census lift-test.

For each 3-omega_vec-critical iso class H of order <=8 (QR_7 + two n=8 classes),
decide 4-omega_vec-criticality of C3[H] exactly via the validated no-K-clique
betweenness SAT (search_4critical_circulant.build_cnf_no_kclique):
  ov(T)>=4  <=> no-K4 CNF UNSAT
  ov(T)<=4  <=> no-K5 CNF SAT
  critical  <=> for all v: no-K4 SAT on T-v  (ov(T-v)<=3; >=3 automatic since
                deletion drops ov by at most 1).
Controls: S~_3 (NOT dic-vertex-critical; G45 says C3[S~_3]=S~_4 not critical,
re-verify ov=4 + one deletion via VT), AC_9 (dic-vertex-critical, order 27).
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from lexlib import AC, lex_substitute, is_tournament
from constructions import directed_C3, S_tilde
from search_4critical_circulant import build_cnf_no_kclique
from pysat.solvers import Cadical153

def sat(cnf):
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        return m.solve()

def no_k_clique_order_exists(n, arcs, K):
    cnf, _ = build_cnf_no_kclique(n, arcs, K)
    return sat(cnf)

def sub(n, arcs, delv):
    keep = [v for v in range(n) if v != delv]
    idx = {v:i for i,v in enumerate(keep)}
    return n-1, [(idx[u],idx[v]) for (u,v) in arcs if u!=delv and v!=delv]

def test_lift(name, H, vt=False):
    T = lex_substitute(directed_C3(), H)
    n, arcs = T
    assert is_tournament(n, arcs)
    t0 = time.time()
    ge4 = not no_k_clique_order_exists(n, arcs, 4)   # UNSAT no-K4 => ov>=4
    le4 = no_k_clique_order_exists(n, arcs, 5)       # SAT no-K5  => ov<=4
    res = dict(name=name, order=n, ov_ge4=ge4, ov_le4=le4)
    print(f"{name}: order={n} ov>=4:{ge4} ov<=4:{le4} ({time.time()-t0:.1f}s)", flush=True)
    if not (ge4 and le4):
        res['critical'] = False
        res['why'] = 'ov != 4'
        return res
    dels = []
    vs = [0] if vt else range(n)
    for v in vs:
        nn, aa = sub(n, arcs, v)
        ok = no_k_clique_order_exists(nn, aa, 4)     # SAT => ov(T-v)<=3
        dels.append((v, ok))
        if not ok:
            print(f"  deletion v={v}: ov stays >=4 -> NOT critical", flush=True)
            break
        print(f"  deletion v={v}: ov<=3 OK ({time.time()-t0:.1f}s)", flush=True)
    res['critical'] = all(ok for _,ok in dels)
    res['deletions_checked'] = [list(x) for x in dels]
    res['vt_used'] = vt
    return res

def main():
    iso = json.load(open(os.path.join(os.path.dirname(__file__),'..','data','iso_critical_scan.json')))
    n8 = [(8, [tuple(a) for a in ex['arcs']]) for ex in iso['8']['critical_examples']]
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    cases = {
        'qr7':  ('C3[QR_7]', AC(7,[1,2,4]), True),
        'n8a':  ('C3[n8_classA]', n8[0], False),
        'n8b':  ('C3[n8_classB]', n8[1], False),
        'st3':  ('C3[S~_3]', S_tilde(3), True),
        'ac9':  ('C3[AC_9]', AC(9,[1,2,3,5]), True),
    }
    keys = list(cases) if which == 'all' else [which]
    out = {}
    for k in keys:
        name, H, vt = cases[k]
        out[k] = test_lift(name, H, vt)
        print(json.dumps(out[k]), flush=True)
    p = os.path.join(os.path.dirname(__file__),'..','data','lift_lemma_step2_census.json')
    old = json.load(open(p)) if os.path.exists(p) else {}
    old.update(out)
    json.dump(old, open(p,'w'), indent=1)

if __name__ == '__main__':
    main()
