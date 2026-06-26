"""core_embedding_witness.py -- the D27 tournament core EMBEDS in-class:
the H9 CONVERSE is refuted INSIDE a chord-contraction gateway, while the
cut-avoidance lemma A' SURVIVES there via the D26 multi-w mechanism.

Host, cell (3,9): V1 = {p,q,y}, y =: u in I (strictly rho-headless).
V2 = {ka,kb,kc} (cage) + {c0..c4} (the reviewer's tournament core) + {w}.
u -> c3 (= a), c0, c2 (the two escaped heads).  Core internal arcs are the
D27 tournament; c3 -> rho (mult 2, needed so an arc-disjoint gateway pair
EXISTS -- c2 is escape-poor by design and U needs the second (c3,rho)
label), c4 -> rho (mult 2), w -> rho (mult 2); c4 -> w is the ONLY O-arc
into w; w dominates c0..c3; everything outside dominates the cage.

With w absorbed: O = {c0..c4} and D_O is STRUCTURALLY THE CORE, exactly.
Asserted:
  * in-class: simple, (1,0)-near-split, lambda(host)=3, host SAD=SAT,
    lambda(D-bullet)=3, no u->rho arc, cage = {u,ka,kb,kc};
  * an explicit rho-headless HARD gateway pair at a=(u,c3);
  * w admissible, B_w = {}, D_O == core (exact arc-set match);
  * F = {(c2,c1)}; head c0 reaches w in D_O - F (uniquely), yet NO
    cut-avoiding c0->w path exists  ==>  H9 CONVERSE REFUTED IN-CLASS;
  * head c2 fails everywhere (its unique escape is the forced arc);
  * the SECOND admissible rho-tail w' = c4 RESCUES head c0
    (P = c0->c3->c1->c4 is cut-avoiding)  ==>  A' SATISFIED here via
    multi-w -- the embedding kills H9's converse but NOT the lemma.
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

from check_lexist_fixedroot import subtree_through, tree_arcs  # noqa: E402


def host_arcs():
    # p=0 q=1 y=u=2 | ka=3 kb=4 kc=5 | c0=6 c1=7 c2=8 c3=9 c4=10 | w=11
    arcs = [
        (0, 1),                                          # chord
        (3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4),  # cage digons
        (3, 2), (4, 2), (5, 2),                          # ki -> u
        (2, 9), (2, 6), (2, 8),                          # u -> c3(=a), c0, c2
        # tournament core (D27): 1->0 0->2 0->3 4->0 2->1 3->1 1->4 3->2 4->2 4->3
        (7, 6), (6, 8), (6, 9), (10, 6), (8, 7),
        (9, 7), (7, 10), (9, 8), (10, 8), (10, 9),
        (10, 11),                                        # c4 -> w (only O-arc into w)
        (11, 6), (11, 7), (11, 8), (11, 9), (11, 10),    # w dominates c0..c4
        (9, 0), (9, 1),                                  # c3 -> rho (mult 2)
        (10, 0), (10, 1),                                # c4 -> rho (mult 2)
        (11, 0), (11, 1),                                # w  -> rho (mult 2)
        (0, 11), (0, 6), (0, 10),                        # rho-side out-arcs
        (1, 11), (1, 7), (1, 8),
    ]
    arcs += [(x, c) for x in (6, 7, 8, 9, 10, 11) for c in (3, 4, 5)]
    return arcs


def dbullet_arcs():
    # rho=0 u=1 ka=2 kb=3 kc=4 | c0=5 c1=6 c2=7 c3=8 c4=9 | w=10
    rel = {0: 0, 1: 0, 2: 1}
    rel.update({v: v - 1 for v in range(3, 12)})
    out = []
    for (x, y) in host_arcs():
        if (x, y) == (0, 1):
            continue
        rx, ry = rel[x], rel[y]
        if rx != ry:
            out.append((rx, ry))
    return out


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


def cut_avoiding_paths(mult, O, root, w, h):
    import networkx as nx
    DO = nx.DiGraph((x, y) for (x, y) in mult if x in O and (y in O or y == root))
    Hw = nx.DiGraph((x, y) for (x, y) in mult if x in O and (y in O or y == w))
    good = []
    if h in Hw and w in Hw:
        for P in nx.all_simple_paths(Hw, h, w):
            AO = [(P[i], P[i + 1]) for i in range(len(P) - 2)]
            D2 = DO.copy(); D2.remove_edges_from(AO)
            if all(nx.has_path(D2, z, root) for z in O):
                good.append(P)
    return good


def main():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    H = host_arcs()
    assert len(H) == len(set(H)), "host must be simple"
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(12), H), [0, 1, 2], list(range(3, 12)))
    assert ok, why
    assert oracle.arc_connectivity(12, H) == 3
    sad = oracle.check_construction(12, H, name="core-embedding-host")
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    db = dbullet_arcs()
    n, root, u, v = 11, 0, 1, 8           # a = (u, c3) = (1, 8)
    a = (u, v)
    mult = Counter(db)
    assert oracle.arc_connectivity(n, db) == 3
    assert (u, root) not in mult           # strictly rho-headless

    G = nx.MultiDiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(db)
    Gm = G.copy(); Gm.remove_node(u)
    cage = {u} | {x for x in range(n) if x not in (root, u)
                  and not nx.has_path(Gm, x, root)}
    assert cage == {1, 2, 3, 4}, cage

    # explicit rho-headless hard gateway pair at a=(1,8)
    T = {2: 3, 3: 1, 4: 1, 1: 8,
         5: 7, 7: 6, 6: 9, 9: 0, 8: 0, 10: 0}
    U = {2: 1, 3: 2, 4: 2, 1: 5,
         5: 8, 8: 0, 6: 5, 7: 2, 9: 0, 10: 0}
    Ts, Us = tree_arcs(T), tree_arcs(U)
    assert is_in_arb(T, n, root) and is_in_arb(U, n, root)
    assert all(mult[e] >= 2 for e in Ts & Us), sorted(Ts & Us)
    X = subtree_through(T, u, root, n)
    assert X == cage, sorted(X)
    ex = [(x, y) for (x, y) in Us if x in X and y not in X]
    assert ex == [(1, 5)], ex              # single U-exit: failing
    free = [e for e in mult if e[0] in X and e[1] not in X
            and mult[e] - (e in Ts) - (e in Us) >= 1]
    assert free and all(e[0] == u for e in free)
    print("rho-headless hard gateway at a=(u,c3): verified")

    # w = 10 admissible, B_w empty, D_O == the tournament core EXACTLY
    w = 10
    red = G.copy(); red.remove_nodes_from(cage | {w})
    B = {z for z in range(n) if z not in cage | {w} and z != root
         and not (z in red and nx.has_path(red, z, root))}
    assert B == set(), B
    Xst = cage | {w}
    assert v not in Xst and len(Xst) <= n - 2
    O = set(range(n)) - Xst - {root}
    assert O == {5, 6, 7, 8, 9}
    DO_arcs = {(x, y) for (x, y) in mult if x in O and (y in O or y == root)}
    core = {(6, 5), (5, 7), (5, 8), (9, 5), (7, 6), (8, 6), (6, 9),
            (8, 7), (9, 7), (9, 8), (8, 0), (9, 0)}
    assert DO_arcs == core, ("D_O is not the core", DO_arcs ^ core)
    print("w admissible; O = {c0..c4}; D_O == tournament core exactly")

    # F = {(c2,c1)} = {(7,6)}; H9 converse refuted in-class at (w, c0)
    DO = nx.DiGraph(DO_arcs)
    F = set()
    for e in list(DO.edges()):
        D2 = DO.copy(); D2.remove_edge(*e)
        if any(not nx.has_path(D2, z, root) for z in O):
            F.add(e)
    assert F == {(7, 6)}, F
    HmF = nx.DiGraph((x, y) for (x, y) in mult
                     if x in O and (y in O or y == w) and (x, y) not in F)
    pths = list(nx.all_simple_paths(HmF, 5, w))
    assert pths == [[5, 8, 6, 9, 10]], pths    # unique F-avoiding c0->w path
    assert cut_avoiding_paths(mult, O, root, w, 5) == []
    print("H9 CONVERSE REFUTED IN-CLASS: c0 reaches w in D_O - F, "
          "no cut-avoiding path exists (Y = {c0,c1,c2})")

    # head c2 = 7 fails everywhere (unique escape IS the forced arc)
    assert cut_avoiding_paths(mult, O, root, w, 7) == []

    # THE STRONGER FINDING: the second admissible rho-tail w' = c4 does NOT
    # rescue -- absorbing c4 removes (c1,c4) from D_O', so Y = {c0,c1,c2}
    # keeps only the single D_O'-exit (c0,c3), which every path consumes.
    # Hence ALL FOUR admissible (w, h) combinations fail:
    # A' (single-w cut-avoidance) is REFUTED IN-CLASS at this gateway.
    red2 = G.copy(); red2.remove_nodes_from(cage | {9})
    B2 = {z for z in range(n) if z not in cage | {9} and z != root
          and not (z in red2 and nx.has_path(red2, z, root))}
    assert B2 == set() and v not in cage | {9}      # w' = c4 IS admissible
    O2 = set(range(n)) - (cage | {9}) - {root}
    assert cut_avoiding_paths(mult, O2, root, 9, 5) == []
    assert cut_avoiding_paths(mult, O2, root, 9, 7) == []
    print("A' REFUTED IN-CLASS: all four admissible (w,h) combinations fail "
          "(w in {w, c4} x h in {c0, c2})")

    # ...YET fixed-root L-exist HOLDS at this gateway, via a mechanism
    # OUTSIDE the T1-T4 prescription framework: absorb EVERYTHING except v
    # (X = V \ {rho, v}, |X| = n-2, intermediate), with U's exits pointing
    # INTO v = c3 -- exits need not head to the rho-side at all; v is a
    # rho-tail and carries them home.
    Tg = {2: 3, 3: 1, 4: 1, 1: 8,
          5: 7, 7: 6, 6: 2, 9: 2, 10: 2, 8: 0}
    Ug = {2: 1, 3: 2, 4: 2, 1: 5,
          5: 8, 6: 5, 7: 2, 9: 8, 10: 8, 8: 0}
    Tgs, Ugs = tree_arcs(Tg), tree_arcs(Ug)
    assert is_in_arb(Tg, n, root) and is_in_arb(Ug, n, root)
    assert all(mult[e] >= 2 for e in Tgs & Ugs), sorted(Tgs & Ugs)
    Xg = subtree_through(Tg, u, root, n)
    assert Xg == set(range(n)) - {root, v}, sorted(Xg)
    assert 2 <= len(Xg) <= n - 2
    exg = sorted((x, y) for (x, y) in Ugs if x in Xg and y not in Xg)
    assert exg == [(5, 8), (9, 8), (10, 8)], exg     # three exits, all INTO v
    strict = [e for e in exg
              if (subtree_through(Ug, e[0], root, n) & Xg) < Xg]
    assert strict, "no strict exit"
    print(f"L-EXIST HOLDS at the gateway: good pair with X = V-{{rho,v}}, "
          f"exits {exg} all pointing INTO v=c3 (a rho-tail), strict={strict}")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
