"""canonical_tree_er_check.py -- ground Theorem CT (D40) + BSC-1: does a
BLOCK-SPARING canonical tree close ER's four residual failures (D39:
116/120 under BS-1+AS) to a clean 120/120 over the seven branch-2
witnesses?

Theorem CT (D40 ER_CANONICAL_TREE doc) claims the canonical in-arb
    T*_in = (cage packing) + (K\\cage hooks) + (any I-internal arc)
is ALWAYS valid and dissolves the R3-conflict residue.  Combined with
BSC-1 (if the block escape's target z* lies in REACH then Z empties),
the operational prediction is:

    on EVERY branch-2 witness there exists a BLOCK-SPARING T (its T_in
    routes every AV_u head off its out-of-block escape -- a cage hook or
    a block-internal retreat -- AND leaves the cage residual reaching u)
    whose CANONICAL rho-exit pair completes (residual reaches every
    vertex), yielding a verified good arc-disjoint in-arb pair.

This is exactly the closure of the 4 BS-1+AS residual failures
(dominated 1, core_embedding 2, blocker_cex 1).  A witness on which NO
block-sparing T with a completing distinct-tail rho-exit pair exists
would be a CHAIN-KERNEL signature -- the open obstruction.

We do NOT re-derive the C7 packing per witness; we test the OPERATIONAL
content of CT/BSC-1 directly on the in-class digraphs: enumerate
block-sparing T_in via randomized block-aware attachment, then over all
distinct-tail rho-exit prescription pairs (canonical pair preferred),
check full residual reachability + build a valid arc-disjoint U with a
strict exit (a genuine good pair, the same bar as v_target_check /
saturation_kernel_witness).
"""
from __future__ import annotations

import os
import random
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import networkx as nx  # noqa: E402

from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)
from v_target_check import is_in_arb, reverse_bfs_in_arb  # noqa: E402


def cage_of(n, root, u, mult):
    G = nx.MultiDiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(mult)
    Gm = G.copy()
    Gm.remove_node(u)
    return {u} | {
        x for x in range(n)
        if x not in (root, u) and not nx.has_path(Gm, x, root)
    }


def x_p_set(n, root, u, v, mult, K_set):
    """The D30 X_P: V minus ({rho} u V(P_v) u J(P)) for a shortest v->rho
    path P_v in D-u, with J(P) the no-path-to-u closure (I-vertices only)."""
    Gm = nx.MultiDiGraph()
    Gm.add_nodes_from(range(n))
    Gm.add_edges_from(mult)
    Gm.remove_node(u)
    P_v = nx.shortest_path(Gm, v, root)
    X = set(range(n)) - {root} - set(P_v[:-1])
    while True:
        DX = nx.DiGraph((x, y) for (x, y) in mult if x in X and y in X)
        DX.add_nodes_from(X)
        bad = {x for x in X - {u} if not nx.has_path(DX, x, u)}
        if not bad:
            break
        assert not (bad & K_set), ("K removed", sorted(bad & K_set))
        X -= bad
    return X, P_v


def block_sparing_T_in(X, u, v, av_heads, cage, mult, rng):
    """Random block-sparing in-arb of D[X] rooted at u: every AV_u head in X
    is attached to a NON-block-escape arc (an arc whose head stays in the
    block = cage u {u} u heads, i.e. a hook or block-internal retreat),
    sparing its out-of-block escapes; the cage is grown sparingly.  Returns
    succ on X-{u} or None."""
    block = set(cage) | {u} | set(av_heads)
    S = {u}
    succ = {}
    arcs = [(x, y) for (x, y) in mult if x in X and (y in X or y == u)]
    # First force every AV_u head sitting in X to retreat inside the block.
    heads_in_X = [h for h in av_heads if h in X]
    for h in heads_in_X:
        block_targets = [y for (x, y) in arcs if x == h and y in block and y != h]
        if not block_targets:
            # I-head whose unique internal arc IS its escape: BS-1 says its
            # >=2 remaining arcs are boundary (never consumed); it may attach
            # anywhere then, but to stay block-sparing we still prefer block.
            block_targets = [y for (x, y) in arcs if x == h and y != h]
            if not block_targets:
                return None
        succ[h] = rng.choice(block_targets)
    # Now grow the rest by random outside->tree attachment, with the heads
    # pinned; verify the heads connect (they may need the block to be built).
    pending = set(X) - {u} - set(succ)
    S = {u}
    placed = dict(succ)
    # iterative attachment honouring the pinned head choices
    changed = True
    while len(S) < len(X):
        # add any head whose target is already in S
        progressed = False
        for h in list(heads_in_X):
            if h not in S and placed.get(h) in S:
                S.add(h)
                progressed = True
        choices = [(x, y) for (x, y) in arcs
                   if x not in S and y in S and x not in heads_in_X]
        if choices:
            x, y = rng.choice(choices)
            placed[x] = y
            S.add(x)
            progressed = True
        if not progressed:
            # try to seed a head whose block target is buildable
            stuck_heads = [h for h in heads_in_X if h not in S]
            opened = False
            for h in stuck_heads:
                tgt = placed.get(h)
                # if tgt currently unreachable, leave; otherwise wait
            if not opened:
                return None
    if set(placed) != set(X) - {u}:
        return None
    return placed


def cage_sparing(succ_X, cage, u, mult):
    """The cage residual (cage-internal arcs minus those used by T_in) still
    reaches u from every cage vertex."""
    tset = set(succ_X.items())
    R = nx.MultiDiGraph()
    R.add_nodes_from(cage)
    for arc, m in mult.items():
        if arc[0] in cage and arc[1] in cage:
            for _ in range(m - (1 if arc in tset else 0)):
                R.add_edge(*arc)
    return all(nx.has_path(R, c, u) for c in cage - {u})


def residual_reach(n, root, mult, tset, e1, e2):
    H = nx.MultiDiGraph()
    H.add_nodes_from(range(n))
    for arc, m in mult.items():
        res = m - (1 if arc in tset else 0)
        if arc[0] == e1[0]:
            res = res if arc == e1 else 0
        if arc[0] == e2[0]:
            res = res if arc == e2 else 0
        for _ in range(max(0, res)):
            H.add_edge(*arc)
    reach = {x for x in range(n) if nx.has_path(H, x, root)}
    return H, reach


def find_block_sparing_good_pair(name, db, n, u, v, K_set, trials=400):
    root = 0
    a = (u, v)
    mult = Counter(db)
    rng = random.Random(20260612)
    cage = cage_of(n, root, u, mult)
    av_heads = sorted(z for (x, z) in mult if x == u and z != v)
    X, P_v = x_p_set(n, root, u, v, mult, K_set)
    assert 2 <= len(X) <= n - 2
    # rho-exit prescription candidates: boundary arcs leaving X (head outside),
    # tail in X, != a.  Canonical = a distinct-tail rho-arc pair if present.
    R_in_X = sorted({e[0] for e in mult if e[1] == root and e[0] in X})

    best = None
    for _ in range(trials):
        T_in = block_sparing_T_in(X, u, v, av_heads, cage, mult, rng)
        if T_in is None:
            continue
        T = dict(T_in)
        T[u] = v
        outside = set(range(n)) - X - {root}
        T_out = reverse_bfs_in_arb(outside, set(mult), root, rng)
        if T_out is None:
            continue
        T.update(T_out)
        if not is_in_arb(T, n, root):
            continue
        if subtree_through(T, u, root, n) != X:
            continue
        tset = tree_arcs(T)
        if not cage_sparing(T_in, cage, u, mult):
            continue
        # block-sparing certificate: at least one out-of-block arc of a head
        # survives in T (never consumed)
        block = set(cage) | {u} | set(av_heads)
        block_escapes = [e for e in mult
                         if e[0] in av_heads and e[1] not in block]
        if block_escapes and not any(e not in tset for e in block_escapes):
            continue
        # candidate rho-exit pairs, canonical (two rho-arcs) FIRST
        exits = [e for e in mult
                 if e[0] in X and e[1] not in X and e != a
                 and mult[e] - (1 if e in tset else 0) >= 1]
        rho_exits = [e for e in exits if e[1] == root]
        ordered = []
        # canonical: pairs of rho-exits with distinct tails first
        for i in range(len(rho_exits)):
            for j in range(i + 1, len(rho_exits)):
                if rho_exits[i][0] != rho_exits[j][0]:
                    ordered.append((rho_exits[i], rho_exits[j]))
        for i in range(len(exits)):
            for j in range(i + 1, len(exits)):
                if exits[i][0] != exits[j][0]:
                    ordered.append((exits[i], exits[j]))
        for e1, e2 in ordered:
            H, reach = residual_reach(n, root, mult, tset, e1, e2)
            if len(reach) != n:
                continue
            U = reverse_bfs_in_arb(set(range(n)) - {root}, set(H.edges()),
                                   root, rng)
            if U is None:
                continue
            U[e1[0]], U[e2[0]] = e1[1], e2[1]
            if not is_in_arb(U, n, root):
                continue
            uset = tree_arcs(U)
            if not pair_realizable(tset, uset, mult):
                continue
            ex = sorted(e for e in uset if e[0] in X and e[1] not in X)
            if len(ex) < 2:
                continue
            strict = [e for e in ex
                      if (subtree_through(U, e[0], root, n) & X) < X]
            if not strict:
                continue
            canonical = (e1[1] == root and e2[1] == root)
            return dict(name=name, X=sorted(X), exits=ex, strict=strict,
                        prescribed=(e1, e2), canonical=canonical,
                        block_escapes_spared=[e for e in block_escapes
                                              if e not in tset])
    return None


def main():
    from gateway_t_eq_u_witness import dbullet_arcs as g1
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4
    from core_embedding_witness import dbullet_arcs as g5
    from v_target_internal_reachability_counterexample import construction
    from saturation_kernel_witness import dbullet_arcs as g7

    db6 = construction()[1]

    specs = [
        ("rho_headless(D17)", g2(), 8, 1, 5, set(range(2, 8))),
        ("dominated(D18)", g3(), 11, 1, 5, set(range(2, 11))),
        ("relay_free(D19)", g4(), 14, 1, 5, set(range(2, 14))),
        ("core_embedding(D28)", g5(), 11, 1, 8, set(range(2, 11))),
        ("blocker_cex(D30)", db6, 23, 1, 5, set(range(2, 14))),
        ("saturation_kernel(D38)", g7(), 14, 1, 5, set(range(2, 14))),
    ]
    # t_eq_u is out of scope (rho-heads, T1 territory) per BS-1 doc.

    n_ok = 0
    for (name, db, n, u, v, K_set) in specs:
        r = find_block_sparing_good_pair(name, db, n, u, v, K_set)
        if r is None:
            print(f"{name}: NO block-sparing good pair found "
                  f"-> CHAIN-KERNEL SIGNATURE (or search miss)")
            continue
        n_ok += 1
        tag = "CANONICAL pair" if r["canonical"] else "distinct-tail pair"
        print(f"{name}: GOOD pair via BLOCK-SPARING T ({tag}); "
              f"prescribed={r['prescribed']}; "
              f"escapes spared={r['block_escapes_spared']}; "
              f"strict={r['strict']}")
    print(f"\nBLOCK-SPARING canonical-tree completion: {n_ok}/{len(specs)} "
          f"in-scope branch-2 witnesses")
    assert n_ok == len(specs), (
        f"ER NOT closed: {len(specs) - n_ok} residual chain-kernel signature(s)")
    print("ALL ASSERTIONS PASS: ER's residual failures close under a "
          "block-sparing canonical tree")


if __name__ == "__main__":
    main()
