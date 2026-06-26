"""D31 lift-lemma STEP 1: dic + dic-vertex-criticality table.

dic(T) = min #colors partitioning V into acyclic sets. For a tournament,
a vertex subset induces an acyclic subtournament iff it contains no directed
triangle (a tournament is acyclic iff transitive iff C3-free). So
k-dicolorability <=> exists k-coloring with no monochromatic directed triangle.
Decided by SAT (pysat Cadical153), exact both directions.
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(__file__))
from lexlib import AC, lex_substitute, is_tournament
from constructions import directed_C3, S_tilde
from pysat.solvers import Cadical153

def beats(n, arcs):
    b = [[False]*n for _ in range(n)]
    for (u,v) in arcs: b[u][v]=True
    return b

def directed_triangles(n, arcs):
    b = beats(n, arcs)
    tris = []
    for u,v,w in itertools.combinations(range(n),3):
        # directed triangle iff the 3 induce a 3-cycle
        if (b[u][v] and b[v][w] and b[w][u]) or (b[v][u] and b[w][v] and b[u][w]):
            tris.append((u,v,w))
    return tris

def dicolorable(n, arcs, k, tris=None):
    """SAT: exists k-coloring with no mono directed triangle."""
    if k >= n: return True
    if tris is None: tris = directed_triangles(n, arcs)
    if not tris: return k >= 1
    if k <= 0: return False
    var = lambda v,c: v*k + c + 1
    cls = []
    for v in range(n):
        cls.append([var(v,c) for c in range(k)])
    for (u,v,w) in tris:
        for c in range(k):
            cls.append([-var(u,c), -var(v,c), -var(w,c)])
    # symmetry break: vertex 0 color 0
    cls.append([var(0,0)])
    with Cadical153(bootstrap_with=cls) as m:
        return m.solve()

def dic(n, arcs, kmax=6):
    tris = directed_triangles(n, arcs)
    for k in range(1, kmax+1):
        if dicolorable(n, arcs, k, tris): return k
    return None

def sub(n, arcs, delv):
    keep = [v for v in range(n) if v != delv]
    idx = {v:i for i,v in enumerate(keep)}
    return n-1, [(idx[u],idx[v]) for (u,v) in arcs if u!=delv and v!=delv]

def dic_vertex_critical(n, arcs, k, vt=False):
    """dic(T)=k and dic(T-v)=k-1 for all v (deletion drops dic by <=1, so
    suffices to check (k-1)-dicolorability of T-v)."""
    vs = [0] if vt else range(n)
    dels = []
    for v in vs:
        nn, aa = sub(n, arcs, v)
        ok = dicolorable(nn, aa, k-1)
        dels.append((v, k-1 if ok else k))
    crit = all(d == k-1 for _,d in dels)
    return crit, dels

def main():
    out = {}
    # the two n=8 3-omega_vec-critical iso classes
    iso = json.load(open(os.path.join(os.path.dirname(__file__),'..','data','iso_critical_scan.json')))
    n8 = [(8, [tuple(a) for a in ex['arcs']]) for ex in iso['8']['critical_examples']]
    assert len(n8) == 2
    cases = [
        ('C3', directed_C3(), False),
        ('QR_7=AC_7', AC(7,[1,2,4]), True),
        ('n8_classA', n8[0], False),
        ('n8_classB', n8[1], False),
        ('S~_3', S_tilde(3), True),
        ('AC_9', AC(9,[1,2,3,5]), True),
        ('AC_11', AC(11,[1,2,3,4,6]), True),
    ]
    for name, (n,arcs), vt in cases:
        assert is_tournament(n, arcs), name
        d = dic(n, arcs)
        crit, dels = dic_vertex_critical(n, arcs, d, vt=vt)
        out[name] = dict(n=n, dic=d, dic_vertex_critical=crit,
                         deletions=[list(x) for x in dels], vt_used=vt)
        print(f"{name:12s} n={n:3d} dic={d} dic_vertex_critical={crit} dels={dels}", flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(__file__),'..','data','lift_lemma_step1_dic_table.json'),'w'), indent=1)

if __name__ == '__main__':
    main()
