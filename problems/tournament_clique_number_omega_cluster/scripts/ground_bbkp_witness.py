"""Ground the Bellitto-Bousquet-Kabela-Pierron (arXiv:2210.09936, Math. Comp. 93)
19-vertex 5-chromatic tournament D against the omega_vec oracle.

D (paper Sec. 5, Thm 5.1 'thm:19vertices', = Neumann-Lara 2000 construction):
take Pal_7 (vertices 0..6, arc i->j iff (j-i) mod 7 in {1,2,4}), blow up every
vertex i in {1..6} into a directed triangle i_1->i_2->i_3->i_1; vertex 0 stays
single. Arcs between blocks follow Pal_7. Order 19, dic(D)=5 (paper, proven),
and every 18-vertex tournament is 4-dicolorable (paper Thm 1.2 / Sec. 6), so D
is AUTOMATICALLY 5-dic-vertex-critical.

Question for the oracle: omega_vec(D) = 5 (then Prop 6.2 fires: C3[D] order 57
is 6-omega_vec-critical) or omega_vec(D) <= 4 (dic-ov gap at the extremal
minimum-order 5-chromatic object)?

Legs:
  (1) build D, verify tournament; verify Pal_7 subtournament ov=3 sanity.
  (2) exact dic(D) via two solvers (Cadical153 + Glucose42): expect 5.
      Spot-check dic(D-v)=4 for a few v (criticality already follows from the
      imported theorem; this is a pipeline sanity check).
  (3) ov lower: no-K5 SAT (exists order with backedge clique <=4?) on D,
      two solvers. SAT => extract order, oracle-verify clique <=4 => ov<=4.
      UNSAT x2 => ov>=5, hence =5 by ov<=dic.
      Also run no-K4 to pin the exact value if no-K5 is SAT.
All foreground; caller wraps in `timeout`.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(__file__))
import core
from pysat.solvers import Cadical153, Glucose42
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from ground_lift_lemma_step1 import directed_triangles, dicolorable, dic, sub

PAL7_GEN = {1, 2, 4}


def pal7_arcs():
    return [(i, j) for i in range(7) for j in range(7)
            if i != j and (j - i) % 7 in PAL7_GEN]


def build_D():
    # vertex 0 -> index 0 ; vertex i in 1..6, copy j in 0..2 -> index 1+3*(i-1)+j
    def idx(i, j=None):
        return 0 if i == 0 else 1 + 3 * (i - 1) + j
    beats7 = {(i, j): ((j - i) % 7 in PAL7_GEN) for i in range(7) for j in range(7) if i != j}
    arcs = []
    for i in range(1, 7):
        # directed triangle i_0 -> i_1 -> i_2 -> i_0
        for j in range(3):
            arcs.append((idx(i, j), idx(i, (j + 1) % 3)))
    for i in range(7):
        for k in range(7):
            if i == k:
                continue
            if not beats7[(i, k)]:
                continue
            us = [idx(i, j) for j in range(3)] if i else [0]
            vs = [idx(k, j) for j in range(3)] if k else [0]
            for u in us:
                for v in vs:
                    arcs.append((u, v))
    return 19, arcs


def no_Kclique_cnf(n, arcs, K):
    """CNF: exists a total order (betweenness/transitivity on pair vars) whose
    backedge graph has no K-clique. Mirrors search_4critical_circulant encoding
    but built here so we can run it under two independent solvers."""
    from itertools import combinations, permutations
    pool = IDPool()
    P = {}  # P[(u,v)] true iff u before v, for u<v
    for u in range(n):
        for v in range(u + 1, n):
            P[(u, v)] = pool.id(('p', u, v))

    def before(u, v):
        # literal "u before v"
        return P[(u, v)] if u < v else -P[(v, u)]

    cls = []
    # transitivity: before(u,v) & before(v,w) -> before(u,w)
    for u, v, w in permutations(range(n), 3):
        if u < w or True:
            pass
    for a in range(n):
        for b in range(n):
            for c in range(n):
                if a == b or b == c or a == c:
                    continue
                if a < c:  # avoid duplicating each constraint pair-symmetric? keep all, cheap at n=19
                    cls.append([-before(a, b), -before(b, c), before(a, c)])
    beats = core.beats_matrix(n, arcs)
    # backedge var e_{u,v} for u<v: edge present iff (u before v and v beats u) or (v before u and u beats v)
    E = {}
    for u in range(n):
        for v in range(u + 1, n):
            if beats[v][u] or beats[u][v]:
                e = pool.id(('e', u, v))
                E[(u, v)] = e
                # u before v & v->u  => backedge
                if beats[v][u]:
                    cls.append([-before(u, v), e])
                else:
                    cls.append([-before(u, v), -e])
                if beats[u][v]:
                    cls.append([before(u, v), e])
                else:
                    cls.append([before(u, v), -e])
    # no K-clique in backedge graph
    from itertools import combinations
    ncl = 0
    for S in combinations(range(n), K):
        lits = []
        ok = True
        for u, v in combinations(S, 2):
            if (u, v) in E:
                lits.append(-E[(u, v)])
            else:
                ok = False
                break
        if ok:
            cls.append(lits)
            ncl += 1
    return cls, P, ncl


def order_from_model(n, model, P):
    pos = set(l for l in model if l > 0)
    from functools import cmp_to_key
    def cmp(u, v):
        if u == v:
            return 0
        if u < v:
            return -1 if P[(u, v)] in pos else 1
        return 1 if P[(v, u)] in pos else -1
    return sorted(range(n), key=cmp_to_key(cmp))


def run_noK(n, arcs, K):
    cls, P, ncl = no_Kclique_cnf(n, arcs, K)
    out = {}
    for name, S in (('cadical153', Cadical153), ('glucose42', Glucose42)):
        t0 = time.time()
        with S(bootstrap_with=cls) as m:
            sat = m.solve()
            model = m.get_model() if sat else None
        dt = time.time() - t0
        rec = {'sat': bool(sat), 't': round(dt, 2)}
        if sat:
            order = order_from_model(n, model, P)
            w = core.omega_of_order(n, arcs, order)
            rec['order'] = order
            rec['clique_of_order'] = w
        out[name] = rec
    return out, ncl


def main():
    n, arcs = build_D()
    print(f'order={n} arcs={len(arcs)} is_tournament={core.is_tournament(n, arcs)}')
    # sanity: Pal_7 subtournament (vertex 0 + first copy of each triangle)
    keep = [0] + [1 + 3 * (i - 1) for i in range(1, 7)]
    n7, a7 = core.subtournament(n, arcs, keep)
    ov7 = core.omega_vec(n7, a7)
    print(f'Pal7 subtournament ov={ov7} (expect 3)')

    # dic leg, two solvers
    tris = directed_triangles(n, arcs)
    print(f'directed triangles: {len(tris)}')
    for k in (4, 5):
        var = lambda v, c: v * k + c + 1
        cls = []
        for v in range(n):
            cls.append([var(v, c) for c in range(k)])
        for (u, v, w) in tris:
            for c in range(k):
                cls.append([-var(u, c), -var(v, c), -var(w, c)])
        cls.append([var(0, 0)])
        for name, S in (('cadical153', Cadical153), ('glucose42', Glucose42)):
            t0 = time.time()
            with S(bootstrap_with=cls) as m:
                sat = m.solve()
            print(f'dicolorable(k={k}) [{name}]: {bool(sat)}  ({time.time()-t0:.2f}s)')

    # spot-check vertex criticality on 3 vertices (0, a triangle vertex, another)
    for v in (0, 1, 10):
        nn, aa = sub(n, arcs, v)
        ok4 = dicolorable(nn, aa, 4)
        print(f'dic(D-{v}) <= 4: {ok4} (imported thm says True)')

    # ov leg
    print('--- no-K5 (omega_vec >= 5 iff UNSAT) ---')
    out5, ncl5 = run_noK(n, arcs, 5)
    print(json.dumps({'K': 5, 'nclique_clauses': ncl5, **out5}))
    if out5['cadical153']['sat']:
        print('--- no-K4 (omega_vec >= 4 iff UNSAT) ---')
        out4, ncl4 = run_noK(n, arcs, 4)
        # don't print full order twice; summarize
        s = {k: {kk: vv for kk, vv in v.items() if kk != 'order'} for k, v in out4.items()}
        print(json.dumps({'K': 4, 'nclique_clauses': ncl4, **s}))
        if out4['cadical153']['sat']:
            print('witness order for clique<=3:', out4['cadical153']['order'])

    # cross-check: exact bb omega_vec if feasible? n=19 generic, likely too slow; rely on SAT x2.


if __name__ == '__main__':
    main()
