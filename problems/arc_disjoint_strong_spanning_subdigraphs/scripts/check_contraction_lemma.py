#!/usr/bin/env python3
"""Step (D): certify the two reduction lemma-steps on generated 3-arc-strong
(1,0)-near-split instances.

A (1,0)-near-split digraph D:  V = V_1 u V_2,
  - D[V_2] semicomplete, |V_2| in {4,5},
  - V_1 has a UNIQUE internal arc e_0 = (p,q),
  - bridges (arcs between V_1 and V_2) in both directions.
We generate random such D, keep the ones with lambda^arc(D) >= 3, then:
  (1) CONTRACTION LEMMA: contract all of V_1 to a single vertex r (= D/V_1),
      assert lambda^arc(D/V_1) >= 2  (predict >=3, never decreases).
  (2) ADJACENCY: record whether r is adjacent (some direction) to EVERY v in V_2
      in the contracted multidigraph => simple(D/V_1) is semicomplete => the
      reduction closes the instance via the BJY semicomplete-SAD theorem.

KILL condition: any generated 3-arc-strong near-split instance whose D/V_1 has
lambda < 2.
"""
import sys
import os
import random
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle  # noqa: E402


def gen_semicomplete_arcs(verts, rng):
    """Random semicomplete tournament-with-some-digons on `verts`."""
    arcs = []
    for u, v in itertools.combinations(verts, 2):
        c = rng.random()
        if c < 0.4:
            arcs.append((u, v))
        elif c < 0.8:
            arcs.append((v, u))
        else:
            arcs.append((u, v)); arcs.append((v, u))  # digon
    return arcs


def gen_near_split(rng):
    """Build one random (1,0)-near-split D. Returns (n, arcs, V1, V2, e0)."""
    k1 = rng.choice([2, 3])          # |V_1|
    k2 = rng.choice([4, 5])          # |V_2|
    V1 = list(range(k1))
    V2 = list(range(k1, k1 + k2))
    n = k1 + k2
    arcs = []
    # unique internal arc of V_1
    p, q = rng.sample(V1, 2)
    e0 = (p, q)
    arcs.append(e0)
    # to make V_1 internally connected without extra internal arcs is impossible
    # for |V1|>=2 unless we route through V2; that's fine -- V_1 has EXACTLY one
    # internal arc by definition; remaining V_1 connectivity is via bridges.
    # semicomplete V_2
    arcs += gen_semicomplete_arcs(V2, rng)
    # bridges: each (u in V1, v in V2) pair gets arcs in random directions,
    # ensure plenty so lambda>=3 is achievable
    for u in V1:
        for v in V2:
            c = rng.random()
            if c < 0.35:
                arcs.append((u, v))
            elif c < 0.7:
                arcs.append((v, u))
            elif c < 0.85:
                arcs.append((u, v)); arcs.append((v, u))
            # else no bridge on this pair
    return n, arcs, V1, V2, e0


def contract(n, arcs, V1):
    """Contract V_1 to a single new vertex r=0, V_2 relabeled to 1..|V2|.
    Keep parallel arcs (multidigraph). Drop loops."""
    V1s = set(V1)
    V2 = [v for v in range(n) if v not in V1s]
    relabel = {v: i + 1 for i, v in enumerate(V2)}
    r = 0
    new = []
    for (u, v) in arcs:
        nu = r if u in V1s else relabel[u]
        nv = r if v in V1s else relabel[v]
        if nu == nv:
            continue  # loop (internal V_1 arc, or V_1<->V_1)
        new.append((nu, nv))
    return len(V2) + 1, new, r, len(V2)


def r_fully_adjacent(arcs, r, n_v2):
    """In contracted multidigraph, is r adjacent (either direction) to all V_2?"""
    nbrs = set()
    for (u, v) in arcs:
        if u == r:
            nbrs.add(v)
        if v == r:
            nbrs.add(u)
    return all((r + 1 + i) in nbrs for i in range(n_v2))


def run(target=20, seed=12345, max_tries=200000):
    rng = random.Random(seed)
    found = 0
    tries = 0
    min_contract_lambda = 99
    n_full_adj = 0
    kills = []
    rows = []
    while found < target and tries < max_tries:
        tries += 1
        n, arcs, V1, V2, e0 = gen_near_split(rng)
        lam = oracle.arc_connectivity(n, arcs)
        if lam < 3:
            continue
        # verify it is genuinely (1,0)-near-split: unique V_1-internal arc
        internal = [(u, v) for (u, v) in arcs if u in V1 and v in V1]
        if len(internal) != 1:
            continue
        found += 1
        cn, carcs, r, nv2 = contract(n, arcs, V1)
        clam = oracle.arc_connectivity(cn, carcs)
        full = r_fully_adjacent(carcs, r, nv2)
        n_full_adj += int(full)
        min_contract_lambda = min(min_contract_lambda, clam)
        if clam < 2:
            kills.append((n, arcs, V1, clam))
        rows.append((n, lam, cn, clam, full))
    print(f"=== Contraction-lemma check: {found} 3-arc-strong (1,0)-near-split "
          f"instances (from {tries} tries) ===")
    for i, (n, lam, cn, clam, full) in enumerate(rows):
        print(f"  [{i:2d}] n={n} lambda(D)={lam} -> D/V1: n'={cn} "
              f"lambda(D/V1)={clam} r_fully_adjacent={full}")
    print("=== SUMMARY ===")
    print(f"instances: {found}")
    print(f"min lambda(D/V1) over all: {min_contract_lambda}  "
          f"(predict >=2; in fact >=3)")
    print(f"contraction-lemma KILLS (lambda<2): {len(kills)}")
    for k in kills:
        print(f"   KILL {k}")
    print(f"r fully adjacent to V_2 (=> simple(D/V1) semicomplete => "
          f"reduction CLOSES instance): {n_full_adj}/{found} "
          f"= {100*n_full_adj/max(found,1):.0f}%")
    pred_ok = (len(kills) == 0 and min_contract_lambda >= 2)
    print(f"CONTRACTION-LEMMA PREDICTION (all lambda(D/V1)>=2): "
          f"{'CONFIRMED' if pred_ok else 'REFUTED'}")
    return kills, min_contract_lambda, n_full_adj, found


if __name__ == "__main__":
    run()
