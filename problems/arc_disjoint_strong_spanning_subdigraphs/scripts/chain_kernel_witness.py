"""chain_kernel_witness.py -- the D40 CHAIN KERNEL in-class.

Design v3 (D-bullet labels, n=23):
  0 rho; 1 u (K, no rho-arc); 2,3,4 cage; 5,6 heads (K, dist 5);
  7 v (K, FORCED); 8 p1 (I, FORCED); 9 p2 (K, W via ladder entry);
  10 p3 (I, FORCED); 11 p4 (K, W); 12 p5 (I, FORCED);
  13 p6 = p_k (K, W via spare (13,0) mult 2); 14,15 roots;
  ladder (distance-graded R2-pairs): 16,17 (d2) -> roots;
  18,19 (d3) -> {16,17}; 20,21 (d4) -> {18,19}; 22 (d5) -> {20,21}.

  Host V1 = {p, q, p1, p3, p5} (chord p->q); V2 = the 19 K-vertices.

  P_v = 7->8->9->10->11->12->13->0, unique shortest (length 7).
  W-entries: (9,22) and (11,18) (never-consumed O->X arcs into the
  ladder at the exact distance grade -- no shortcuts, no ties), and the
  spare label of (13,0).
  FORCED: 7, 8, 10, 12 each have exactly ONE D_O-arc (their chain arc).
  KEY MOVES vs the naive design:
   * u in K: its AV_u arcs (1,8),(1,10),(1,12) are never consumed (u's
     T-arc is always `a`), feed the thin B*-pockets to lambda >= 3, and
     are INVISIBLE to P_v (computed in D-u);
   * the forced I-vertices 10, 12 carry X-side arcs (10,5),(10,6),
     (12,5),(12,6): usable by C_u-pair trees (so a hard gateway pair
     EXISTS) but NOT by the program's T_out (heads not in O) -- the
     program-forcedness survives;
   * 8 is absolutely forced ((8,9) in every spanning in-arb: its only
     other arcs funnel cage -> u -> a -> v -> (7,8) back to 8).

  B* = {u, cage, heads, 7, 8, 10, 12}; delta+(B*) =
  {(8,9),(10,11),(12,13)} = 3 = lambda, each arc the unique D_O-arc of
  its tail => for EVERY T of the X_P program (T_out arcs head O u {rho})
  all three are consumed => B* SEALED in D-hat: no prescription pair
  completes ANY T.  The chain kernel: P_v alternates
  B*(7,8) | W(9) | B*(10) | W(11) | B*(12) | W(13).
"""
from __future__ import annotations

import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)

LADDER = [16, 17, 18, 19, 20, 21, 22]


def dbullet_arcs():
    A = []
    # cage digon triangle + ki -> u
    A += [(2,3),(3,2),(2,4),(4,2),(3,4),(4,3),(2,1),(3,1),(4,1)]
    # u (K): a + AV_u arcs at heads and at the forced I-vertices
    A += [(1,7),(1,5),(1,6),(1,8),(1,10),(1,12)]
    # hooks: every K\cage vertex -> cage (x3)
    for x in [5,6,7,9,11,13,14,15] + LADDER:
        A += [(x,2),(x,3),(x,4)]
    # heads (d5): -> each other/v and the forced I-vertices 8, 10
    A += [(5,6),(5,7),(6,7),(5,8),(6,8),(5,10),(6,10)]
    # v: single D_O-arc (7,8); hooks only otherwise
    A += [(7,8)]
    # chain + p_k spare
    A += [(8,9),(9,10),(10,11),(11,12),(12,13)] + [(13,0)]*2
    # forced I-vertices: cage arcs (X\W); 10,12 also -> heads (X\W)
    A += [(8,2),(8,3)]
    A += [(10,2),(10,3),(10,5),(10,6)]
    A += [(12,2),(12,3),(12,5),(12,6)]
    # 9 (K, W): ladder entry (9,22) + arcs into X\W and backward
    A += [(9,22),(9,5),(9,6),(9,7)]
    # 11 (K, W): ladder entry (11,18) + backward/X\W arcs
    A += [(11,18),(11,22),(11,9),(11,7),(11,5),(11,6)]
    # 13 (K, W, p_k): backward + X-side arcs (unforced; 13 in W by spare)
    A += [(13,9),(13,11),(13,7),(13,5),(13,6)]
    A += [(13,16),(13,17),(13,18),(13,19),(13,20),(13,21),(13,22)]
    # roots: digon, rho-labels x2, dominate O/heads/deep ladder, -> u
    A += [(14,15),(15,14)] + [(14,0)]*2 + [(15,0)]*2
    for r in (14, 15):
        A += [(r,5),(r,6),(r,7),(r,8),(r,9),(r,10),(r,11),(r,12),(r,13)]
        A += [(r,18),(r,19),(r,20),(r,21),(r,22),(r,1)]
    # ladder core: distance-graded R2 pairs
    A += [(16,14),(16,15),(17,14),(17,15),(16,17)]
    A += [(18,16),(18,17),(19,16),(19,17),(18,19)]
    A += [(20,18),(20,19),(21,18),(21,19),(20,21)]
    A += [(22,20),(22,21)]
    # ladder extra pairs (distance-preserving orientations)
    A += [(16,20),(16,21),(17,20),(17,21),(16,22),(17,22),(18,22),(19,22)]
    # ladder vs O/v/heads/u (ladder ->, except the two entries)
    for L in LADDER:
        A += [(L,5),(L,6),(L,7),(L,1)]
    A += [(16,9),(17,9),(18,9),(19,9),(20,9),(21,9)]
    A += [(16,11),(17,11),(19,11),(20,11),(21,11)]
    # O cap K -> u (semicompleteness; O->X arcs, harmless)
    A += [(9,1),(11,1),(13,1)]
    # rho-side out (host p/q): rho -> roots (x2 each), rho -> 22
    A += [(0,14)]*2 + [(0,15)]*2 + [(0,22)]*2
    return A


def host_arcs():
    # host: p=0, q=1; D-bullet z>=1 -> host z+1 (V1 extras: 9=p1, 11=p3,
    # 13=p5 in host labels)
    H = [(0,1)]
    rho_in = Counter(); rho_out = Counter()
    for (x, y) in dbullet_arcs():
        if y == 0:
            rho_in[x] += 1
        elif x == 0:
            rho_out[y] += 1
        else:
            H.append((x+1, y+1))
    for x, m in rho_in.items():
        H.append((x+1, 0))
        if m == 2:
            H.append((x+1, 1))
    for y, m in rho_out.items():
        H.append((0, y+1))
        if m == 2:
            H.append((1, y+1))
    return H


def is_in_arb(succ, n, root):
    for s in range(n):
        if s == root:
            continue
        seen, cur = set(), s
        while cur != root:
            if cur in seen or cur not in succ:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def main():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    H = host_arcs()
    assert len(H) == len(set(H)), "host must be simple"
    nH = 24
    V1 = [0, 1, 9, 11, 13]
    V2 = [z for z in range(2, nH) if z not in (9, 11, 13)]
    ok, why = is_one_zero_near_split(Digraph.from_arcs(range(nH), H), V1, V2)
    assert ok, why
    lamH = oracle.arc_connectivity(nH, H)
    assert lamH == 3, ("lambda(host)", lamH)
    sad = oracle.check_construction(nH, H, name="chain-kernel-host")
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    db = dbullet_arcs()
    n, root, u, v = 23, 0, 1, 7
    a = (u, v)
    mult = Counter(db)
    assert oracle.arc_connectivity(n, db) == 3
    assert (u, root) not in mult and (root, u) not in mult

    G = nx.MultiDiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(db)
    Gm = G.copy(); Gm.remove_node(u)
    cage = {u} | {x for x in range(n) if x not in (root, u)
                  and not nx.has_path(Gm, x, root)}
    assert cage == {1, 2, 3, 4}, sorted(cage)

    # unique shortest P_v exactly as designed
    paths = list(nx.all_shortest_paths(Gm, v, root))
    assert paths == [[7, 8, 9, 10, 11, 12, 13, 0]], paths

    O = {7, 8, 9, 10, 11, 12, 13}
    X = set(range(n)) - {root} - O
    DX = nx.DiGraph((x, y) for (x, y) in mult if x in X and y in X)
    DX.add_nodes_from(X)
    assert all(nx.has_path(DX, x, u) for x in X if x != u)  # J empty

    # forced vertices: unique D_O-arc = the chain arc
    for t, hd in [(7, 8), (8, 9), (10, 11), (12, 13)]:
        do_arcs = [(p, q) for (p, q) in mult
                   if p == t and (q in O or q == root)]
        assert do_arcs == [(t, hd)], (t, do_arcs)

    # B* sealed: delta+(B*) = exactly the three forced chain crossings
    Bs = {1, 2, 3, 4, 5, 6, 7, 8, 10, 12}
    out = sorted((p, q) for (p, q) in mult if p in Bs and q not in Bs)
    assert out == [(8, 9), (10, 11), (12, 13)], out
    print("delta+(B*) = {(8,9),(10,11),(12,13)}, each its tail's unique "
          "D_O-arc:")
    print("  every X_P-program T consumes all three -> B* SEALED for "
          "every T and every pair")

    # explicit hard gateway pair at a=(1,7) with X = C_u: T0 routes the
    # forced I-vertices through the heads (10->5, 12->5), freeing
    # (10,11),(12,13) for U0; U0's single C_u-exit is (1,10).
    T0 = {2:3, 3:1, 4:1, 1:7, 5:8, 6:8, 7:8, 8:9, 9:22, 10:5, 12:5,
          11:12, 13:0, 14:0, 15:0, 22:20, 20:18, 18:16, 16:14, 17:14,
          19:16, 21:18}
    U0 = {2:1, 3:2, 4:2, 1:10, 10:11, 11:18, 18:17, 17:15, 15:0,
          5:10, 6:10, 7:2, 8:2, 9:10, 12:13, 13:0, 14:0, 16:15,
          19:17, 20:19, 21:19, 22:21}
    Ts0, Us0 = tree_arcs(T0), tree_arcs(U0)
    assert is_in_arb(T0, n, root), "T0 invalid"
    assert is_in_arb(U0, n, root), "U0 invalid"
    assert pair_realizable(Ts0, Us0, mult)
    Xg = subtree_through(T0, u, root, n)
    assert Xg == cage, sorted(Xg)
    ex = [(p, q) for (p, q) in Us0 if p in Xg and q not in Xg]
    assert len(ex) == 1, ex                       # failing: single U-exit
    free = [e for e in mult if e[0] in Xg and e[1] not in Xg
            and mult[e] - (e in Ts0) - (e in Us0) >= 1]
    assert free and all(e[0] == u for e in free)  # hard gateway at t=u
    print(f"hard gateway pair at a=(u,v): verified (single exit {ex})")

    # Stronger honesty check: no iteration and no re-chosen U are needed.
    # Rehang p5=12 directly into the cage.  Its old T-subtree is
    # {p4,p5}={11,12}; the original U0 then has three exits.
    T2 = dict(T0)
    T2[12] = 2
    Ts2 = tree_arcs(T2)
    assert is_in_arb(T2, n, root)
    assert pair_realizable(Ts2, Us0, mult)
    X2 = subtree_through(T2, u, root, n)
    assert X2 == {1, 2, 3, 4, 11, 12}, sorted(X2)
    ex2 = sorted(e for e in Us0 if e[0] in X2 and e[1] not in X2)
    strict2 = [
        e for e in ex2
        if (subtree_through(U0, e[0], root, n) & X2) < X2
    ]
    assert ex2 == [(1, 10), (11, 18), (12, 13)], ex2
    assert strict2 == ex2, strict2
    print(f"one-shot free-entry absorption: X = {sorted(X2)}, "
          f"original U kept, exits {ex2}")

    # kernel demonstration with the canonical X_P tree (all hooks) and the
    # canonical pair at the two X_P roots 14, 15
    T = {2:3, 3:1, 4:1, 1:7}
    for w in [5, 6, 14, 15] + LADDER:
        T[w] = 2
    T[7], T[8], T[9], T[10], T[11], T[12], T[13] = 8, 9, 10, 11, 12, 13, 0
    Ts = tree_arcs(T)
    assert is_in_arb(T, n, root)
    assert subtree_through(T, u, root, n) == X
    r1, r2 = 14, 15
    Hh = nx.MultiDiGraph(); Hh.add_nodes_from(range(n))
    for e, m in mult.items():
        res = m - (1 if e in Ts else 0)
        if e[0] == r1: res = res if e == (r1, root) else 0
        if e[0] == r2: res = res if e == (r2, root) else 0
        if res >= 1: Hh.add_edge(*e)
    stranded = sorted(z for z in Bs if not nx.has_path(Hh, z, root))
    reach_rest = all(nx.has_path(Hh, z, root) for z in range(1, n)
                     if z not in Bs)
    assert stranded == sorted(Bs), stranded
    assert reach_rest
    print(f"canonical pair + canonical tree: ALL of B* = {sorted(Bs)} "
          f"stranded (everything else reaches rho); the seal makes this "
          f"T-independent and pair-independent")

    # L-exist HONESTY CHECK: the kernel kills the X_P RECIPE, not the
    # conjecture -- a good pair exists at X = {cage, 10} (absorb the
    # forced I-vertex 10 into the T-side; two U-exits).
    T1 = {2:3, 3:1, 4:1, 1:7, 5:8, 6:8, 7:8, 8:9, 9:22, 10:2, 12:5,
          11:12, 13:0, 14:0, 15:0, 22:20, 20:18, 18:16, 16:14, 17:14,
          19:16, 21:18}
    U1 = {2:1, 3:2, 4:2, 1:12, 12:13, 13:0, 10:11, 11:18, 18:17, 17:15,
          15:0, 5:10, 6:10, 7:2, 8:2, 9:10, 14:0, 16:15, 19:17, 20:19,
          21:19, 22:21}
    Ts1, Us1 = tree_arcs(T1), tree_arcs(U1)
    assert is_in_arb(T1, n, root) and is_in_arb(U1, n, root)
    assert pair_realizable(Ts1, Us1, mult)
    X1 = subtree_through(T1, u, root, n)
    assert X1 == {1, 2, 3, 4, 10}, sorted(X1)
    ex1 = [(p, q) for (p, q) in Us1 if p in X1 and q not in X1]
    assert len(ex1) >= 2, ex1                     # GOOD pair: L-exist holds
    print(f"L-exist survives: good pair at X = {sorted(X1)} with exits "
          f"{ex1} (absorb the forced vertex)")
    print("CHAIN KERNEL REALIZED IN-CLASS")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
