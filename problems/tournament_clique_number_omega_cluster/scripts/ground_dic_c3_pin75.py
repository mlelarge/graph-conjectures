"""PIN dic(C3[H1*])=6 by EXPLICIT cross-block pairing colouring (poly-time, no search).

H1* = C25({1,2,3,4,5,6,7,9,10,12,14,17}), dic(H1*)=4 (P22).
Upper-bound construction: take an optimal 4-dicolouring A_1..A_4 of H1*. C3[H*] has
3 blocks B_0,B_1,B_2 (one per outer C3 vertex). The 12 "slots" (block b, class i)
are each acyclic (B_b restricted to A_i is a copy of H*|A_i, acyclic). Pair slots
ACROSS DISTINCT blocks: the union of an acyclic set in B_b and one in B_{b'} (b!=b')
is acyclic because ALL arcs between two distinct blocks go ONE way (outer C3),
so no new directed triangle can use vertices from both. 12 slots -> ceil(12/2)=6
colours. We BUILD this 6-colouring and machine-VERIFY every class is acyclic
(C3-free subtournament == acyclic). Combined with recorded dic>=6 (P22: 5-dic UNSAT)
this PINS dic(C3[H1*])=6=ceil(3*4/2).
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(__file__))
from ground_lift_lemma_step1 import dicolorable, directed_triangles
from lexlib import lex_substitute, is_tournament, AC
from constructions import directed_C3


def beats(n, arcs):
    b = [[False] * n for _ in range(n)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def is_acyclic_tournament_subset(n, arcs, verts):
    """A subset of a tournament induces an acyclic (transitive) subdigraph iff
    it contains NO directed triangle. Exact check over all triples in verts."""
    b = beats(n, arcs)
    vs = list(verts)
    for u, v, w in itertools.combinations(vs, 3):
        if (b[u][v] and b[v][w] and b[w][u]) or (b[v][u] and b[w][v] and b[u][w]):
            return False
    return True


def optimal_4dicolouring(n, arcs):
    """Find an explicit 4-dicolouring (no mono directed triangle) via SAT,
    return partition list of 4 vertex-sets. Uses the same encoding as dicolorable
    but extracts the model."""
    from pysat.solvers import Cadical153
    tris = directed_triangles(n, arcs)
    k = 4
    var = lambda v, c: v * k + c + 1
    cls = []
    for v in range(n):
        cls.append([var(v, c) for c in range(k)])
    for (u, v, w) in tris:
        for c in range(k):
            cls.append([-var(u, c), -var(v, c), -var(w, c)])
    cls.append([var(0, 0)])
    with Cadical153(bootstrap_with=cls) as m:
        assert m.solve(), "H* is not 4-dicolourable?!"
        model = set(x for x in m.get_model() if x > 0)
    classes = [[] for _ in range(k)]
    for v in range(n):
        for c in range(k):
            if var(v, c) in model:
                classes[c].append(v)
                break
    # verify it really is a valid dicolouring
    for c in classes:
        assert is_acyclic_tournament_subset(n, arcs, c), "bad H* colour class"
    return classes


def main():
    n = 25
    g = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 14, 17]
    Hstar = AC(25, g)
    assert is_tournament(*Hstar)
    nH, aH = Hstar

    # exact dic(H*) sanity
    dH = None
    for k in range(1, 6):
        if dicolorable(nH, aH, k):
            dH = k
            break
    print(f"dic(H1*) = {dH}  (expect 4)", flush=True)
    assert dH == 4

    classes = optimal_4dicolouring(nH, aH)
    print("4-dicolouring class sizes:", [len(c) for c in classes], flush=True)

    # Build C3[H*], order 75
    N, A = lex_substitute(directed_C3(), Hstar)
    assert is_tournament(N, A)
    assert N == 75
    print(f"C3[H1*] order={N}, arcs={len(A)} (expect {N*(N-1)//2})", flush=True)

    # vertex (block b, inner v) -> global index = b*25 + v   (lex_substitute layout:
    # u = o1*ni + a1, so outer index = b, inner index = v)
    def gv(b, v):
        return b * nH + v

    # 12 slots (b, i): vertices = {gv(b,v) : v in classes[i]}
    slots = []
    for b in range(3):
        for i in range(4):
            slots.append((b, i, [gv(b, v) for v in classes[i]]))

    # PAIR slots across DISTINCT blocks into 6 colours.
    # slot order: (0,0)(0,1)(0,2)(0,3)(1,0)(1,1)(1,2)(1,3)(2,0)(2,1)(2,2)(2,3)
    # pairing: pair slot j with slot j+6 (blocks differ: j in 0..5 -> block 0 or 1,
    # j+6 in 6..11 -> block 1 or 2). Check distinct blocks each pair.
    colours = []
    for j in range(6):
        s1 = slots[j]
        s2 = slots[j + 6]
        assert s1[0] != s2[0], f"pair {j}: same block {s1[0]}=={s2[0]}"
        colours.append(s1[2] + s2[2])

    # VERIFY: partition of all 75 vertices + each colour acyclic
    allv = sorted(v for col in colours for v in col)
    assert allv == list(range(N)), f"not a partition: {len(allv)} vs {N}"
    results = []
    all_ok = True
    for ci, col in enumerate(colours):
        ok = is_acyclic_tournament_subset(N, A, col)
        all_ok = all_ok and ok
        results.append({"colour": ci, "size": len(col), "acyclic": ok})
        print(f"colour {ci}: size={len(col)} acyclic={ok}", flush=True)

    # Cross-check via the SAT dicolorability oracle: 6-dicolourable must be True
    sat6 = dicolorable(N, A, 6)
    print(f"\nexplicit 6-colouring all acyclic = {all_ok}", flush=True)
    print(f"SAT dicolorable(C3[H1*], 6) = {sat6}  (independent confirmation)", flush=True)
    out = {"n_H": nH, "g": g, "dic_H": dH, "N": N,
           "explicit_6colouring_all_acyclic": all_ok,
           "sat_6dicolorable": bool(sat6),
           "pred_ceil_3k_2": (3 * dH + 1) // 2,
           "colour_classes_sizes": [len(c) for c in colours],
           "per_colour": results,
           "note": "P22 records dic(C3[H1*])>=6 (5-dic UNSAT); explicit acyclic "
                   "6-colouring => dic<=6; together dic=6=ceil(3*4/2)."}
    path = os.path.join(os.path.dirname(__file__), '..', 'data',
                        'dic_c3_pin75.json')
    json.dump(out, open(path, 'w'), indent=1)
    print("wrote", path, flush=True)
    print("\nVERDICT:", "PIN dic(C3[H1*])=6 CONFIRMED" if all_ok and sat6
          else "FAIL", flush=True)


if __name__ == '__main__':
    main()
