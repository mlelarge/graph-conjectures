"""STEP 4: lift the two verified Prop-6.2 inputs H* (order-25 circulants,
4-dic-vertex-critical AND 4-omega_vec-critical) to T = C3[H*] (order 75)
and verify 5-omega_vec-criticality COMPUTATIONALLY (not just by citation):

  (a) ov(T) >= 5: proven lex lower bound ov(C3[H]) >= 2+ov(H)-1 = ov(H)+1
      [paper's own first-vertex argument / ledger's proven lex lower].
  (b) deletion x=(A,0): build the paper's explicit interleaved order
      b < c < A1 < B1 < C1 < A2 < B2 < C2 < A3 < B3 < C3 from
      3-dicolorings of A-x, B-b, C-c (exist: H* is 4-dic-VERTEX-critical);
      core.omega_of_order on it => ov(T-x) <= clique(order).
  (c) ov(T-x) >= 4: T-x contains the intact copy C iso H* (ov=4).
  (d) subadditivity ov(T) <= ov(T-x)+1.
  If (b) gives clique 4: ov(T-x)=4, ov(T)=5 exactly, and C3[H*] is
  vertex-transitive (lex of vertex-transitive factors) => 5-ov-critical.

k=6 GATE: dic(C3[H*]) by SAT (4-dicolorable? 5-dicolorable?) + analytic
maxacyc bound (maxacyc multiplicative under lex, dic >= n/maxacyc).
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
from functools import lru_cache
from pysat.solvers import Cadical153, Minisat22
from ground_lift_lemma_step1 import dicolorable, directed_triangles


def circ_arcs(n, g):
    return [(i, (i + d) % n) for i in range(n) for d in g]


def c3_lex(nh, harcs):
    """C3[H]: blocks A=0..nh-1, B=nh..2nh-1, C=2nh..3nh-1; A->B->C->A."""
    n = 3 * nh
    arcs = []
    for b in range(3):
        off = b * nh
        arcs += [(u + off, v + off) for (u, v) in harcs]
    for (src, dst) in ((0, 1), (1, 2), (2, 0)):
        arcs += [(u + src * nh, v + dst * nh) for u in range(nh) for v in range(nh)]
    return n, arcs


def get_dicoloring(n, arcs, k):
    """Return a k-dicoloring (list of k lists, topologically unordered) or None."""
    tris = directed_triangles(n, arcs)
    var = lambda v, c: v * k + c + 1
    cls = [[var(v, c) for c in range(k)] for v in range(n)]
    for (u, v, w) in tris:
        for c in range(k):
            cls.append([-var(u, c), -var(v, c), -var(w, c)])
    with Cadical153(bootstrap_with=cls) as m:
        if not m.solve():
            return None
        mod = set(l for l in m.get_model() if l > 0)
    col = [[] for _ in range(k)]
    for v in range(n):
        for c in range(k):
            if var(v, c) in mod:
                col[c].append(v)
                break
    # sanity: each class C3-free (acyclic in a tournament)
    b = [[False] * n for _ in range(n)]
    for (u, v) in arcs:
        b[u][v] = True
    for cls_ in col:
        for x, y, z in itertools.combinations(cls_, 3):
            assert not ((b[x][y] and b[y][z] and b[z][x]) or
                        (b[y][x] and b[z][y] and b[x][z])), "mono triangle!"
    return col


def topo_sort_class(verts, beats):
    """Order an acyclic class by within-class out-degree (transitive => valid)."""
    return sorted(verts, key=lambda x: -sum(1 for y in verts if y != x and beats[x][y]))


def maxacyc(n, arcs):
    """Max transitive subtournament size, bitmask memo DFS."""
    out = [0] * n
    for (u, v) in arcs:
        out[u] |= (1 << v)

    @lru_cache(maxsize=None)
    def f(mask):
        best = 0
        m = mask
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            best = max(best, 1 + f(mask & out[v]))
        return best
    return f((1 << n) - 1)


def main():
    winners = [
        (25, [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 14, 17]),
        (25, [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 15, 17]),
    ]
    out = {}
    for (nh, g) in winners:
        key = f"C25_{'_'.join(map(str, g))}"
        harcs = circ_arcs(nh, g)
        assert core.is_tournament(nh, harcs)
        beats_h = [[False] * nh for _ in range(nh)]
        for (u, v) in harcs:
            beats_h[u][v] = True
        res = {"n_H": nh, "g": g}
        t0 = time.time()
        # ---- re-verify input legs once more (both solvers were used in step3)
        res["H_dic4"] = (not dicolorable(nh, harcs, 3)) and dicolorable(nh, harcs, 4)
        # deletion of H (vertex 0): 3-dicolorable?
        keep = [v for v in range(nh) if v != 0]
        idx = {v: i for i, v in enumerate(keep)}
        darcs = [(idx[u], idx[v]) for (u, v) in harcs if u != 0 and v != 0]
        res["H_dic_vc"] = dicolorable(nh - 1, darcs, 3)
        res["maxacyc_H"] = maxacyc(nh, harcs)

        # ---- build T = C3[H*]
        nT, Tarcs = c3_lex(nh, harcs)
        assert core.is_tournament(nT, Tarcs)
        beats_T = [[False] * nT for _ in range(nT)]
        for (u, v) in Tarcs:
            beats_T[u][v] = True

        # ---- (b) deletion explicit order: x = vertex 0 of block A
        x = 0
        b_pick = nh + 0      # b in B
        c_pick = 2 * nh + 0  # c in C
        colA = get_dicoloring(nh - 1, darcs, 3)            # of A - x (relabelled)
        colA = [[keep[i] for i in cl] for cl in colA]      # back to A labels
        # B - b, C - c: same circulant, deletion of 0, shift labels
        colB = [[nh + keep[i] for i in cl] for cl in get_dicoloring(nh - 1, darcs, 3)]
        colC = [[2 * nh + keep[i] for i in cl] for cl in get_dicoloring(nh - 1, darcs, 3)]
        order = [b_pick, c_pick]
        for layer in range(3):
            for col in (colA, colB, colC):
                order += topo_sort_class(col[layer], beats_T)
        rest = [v for v in range(nT) if v != x]
        assert sorted(order) == sorted(rest) and len(order) == nT - 1
        # omega of backedge graph of T - x under this order
        idxT = {v: i for i, v in enumerate(rest)}
        sub_arcs = [(idxT[u], idxT[v]) for (u, v) in Tarcs if u != x and v != x]
        sub_order = [idxT[v] for v in order]
        cl_del = core.omega_of_order(nT - 1, sub_arcs, sub_order)
        res["deletion_order_clique"] = cl_del   # <=4 hoped
        # (c) lower: T-x contains intact copy C iso H*, ov(H*)=4 (step3, two-sided)
        # (d) ov(T) <= ov(T-x)+1 ; (a) ov(T) >= ov(H*)+1 = 5 (proven lex lower)
        res["ov_T_eq5_and_5critical"] = (cl_del == 4)

        # ---- k=6 gate: dic(C3[H*])
        res["maxacyc_T_analytic"] = 2 * res["maxacyc_H"]  # multiplicative under lex
        res["dic_T_analytic_lb"] = -(-nT // (2 * res["maxacyc_H"]))
        tris_T = directed_triangles(nT, Tarcs)
        t1 = time.time()
        d4 = dicolorable(nT, Tarcs, 4, tris_T)
        t2 = time.time()
        d5 = dicolorable(nT, Tarcs, 5, tris_T)
        t3 = time.time()
        res["T_4dicolorable"] = d4
        res["T_5dicolorable"] = d5
        res["dic_T"] = (4 if d4 else (5 if d5 else ">=6"))
        res["t_sat_4_5"] = (round(t2 - t1, 1), round(t3 - t2, 1))
        res["time_total_s"] = round(time.time() - t0, 1)
        out[key] = res
        print(key, json.dumps(res), flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'data',
                                     'census_lift_step4.json'), 'w'), indent=1)
    print("saved data/census_lift_step4.json")


if __name__ == "__main__":
    main()
