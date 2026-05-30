#!/usr/bin/env python3
r"""
lemma_b_checks.py
=================

LEMMA B (reduction soundness, the converse-of-routine step toward Conjecture 9.2,
arXiv:2304.04690).  If a 2-extremal digraph D is *exhibited* as

    (a) a directed Hajos join   D = D1 *_v D2        (Def 1.5), or
    (b) a non-empty-A 2-Hajos tree join              (Def 9.1),

along an actual seam, then EVERY constituent piece / A-block is itself 2-extremal.
This is what lets the induction for Sub-lemma A-prime DESCEND.

This script collects the *computational* evidence for Lemma B and pins the exact
structural identities the rigorous proof in docs/proof_lemma_b.md rests on.  It
uses ONLY the sound primitives of h2_oracle.py and runs under system python (it
imports h2_oracle, which is pure-Python; networkx is NOT required).

Checks performed
----------------
B1  Every structural Hajos piece  D[S1]+(u,v),  D[S2]+(v,w)  arising from the
    full underlying-graph seam inverse (h2_oracle._hajos_decompositions) over
    L3..L7 is 2-extremal, condition by condition.            [SOUNDNESS DATA]

B2  Structural identities the proof uses, verified on every Hajos seam of
    L6 u L7:
      (i)  the UNIQUE arc between S1\{v} and S2\{v} is the join arc (u,w);
      (ii) v's incidences split as  outdeg_S1(v) = indeg_S1(v) + 1   and
                                     indeg_S2(v) = outdeg_S2(v) + 1,
           so adding (u,v) to the S1 side and (v,w) to the S2 side restores
           in=out at v on both pieces, each >= 2.             [DEGREE BOOKKEEPING]

B3  Every tree-join A-block over L7 (the 3 tree-join-only members) is 2-extremal
    (in fact W3).                                             [CLAUSE (b) DATA]

B4  Adversarial soundness probe (the load-bearing empirical fact): a *broken*
    (non-2-extremal) piece never combines into a 2-extremal Hajos join.  Run with
    --adversarial (slower).                                   [no false reductions]

Empirical agreement for n <= 7 / over finite probes is EVIDENCE, never a proof.
The proof itself is in docs/proof_lemma_b.md, with every step labelled.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as O  # noqa: E402


# --------------------------------------------------------------------------

def load_L(n):
    data = json.load(open(os.path.join(ROOT, "data", f"L_{n}.json")))
    return [(m["n"], frozenset(tuple(a) for a in m["arcs"])) for m in data]


def all_members(ns=(3, 4, 5, 6, 7)):
    out = []
    for n in ns:
        for i, (nn, arcs) in enumerate(load_L(n)):
            out.append((n, i, nn, arcs))
    return out


def is_base(n, arcs):
    return O.is_symmetric_odd_cycle(n, arcs) or O._is_generalised_wheel(n, arcs)


def piece_conditions(nb, ab):
    nb, ab = O._norm(nb, ab)
    return {
        "eulerian_mindeg2": O.is_eulerian_deg(nb, ab, 2),
        "strong": O.is_strong(nb, ab),
        "underlying_2conn": O.is_2connected(nb, ab),
        "lambda==2": O.lambda_D(nb, ab) == 2,
        "chi_vec==3": O.chi_vec(nb, ab) == 3,
    }


# --------------------------------------------------------------------------
# Re-implementation of the Hajos inverse WITH the seam data exposed
# (mirrors h2_oracle._hajos_decompositions exactly; SOUND).
# --------------------------------------------------------------------------

def hajos_seams(n, arcs):
    """Yield (u, w, v, S1, S2) for every directed-Hajos seam of (n, arcs).

    Same enumeration as h2_oracle._hajos_decompositions, but reporting the seam
    skeleton instead of the relabelled pieces."""
    arcset = set(arcs)
    for (u, w) in arcset:
        if u == w:
            continue
        rest = arcset - {(u, w)}
        rest_und = [set() for _ in range(n)]
        for (a, b) in rest:
            rest_und[a].add(b)
            rest_und[b].add(a)
        for v in range(n):
            if v == u or v == w:
                continue
            comp_u = O._component(rest_und, u, blocked=v)
            comp_w = O._component(rest_und, w, blocked=v)
            if w in comp_u or u in comp_w:
                continue
            S1 = comp_u | {v}
            S2 = comp_w | {v}
            if S1 & S2 != {v} or S1 | S2 != set(range(n)):
                continue
            if not all((a in S1 and b in S1) or (a in S2 and b in S2)
                       for (a, b) in rest):
                continue
            if len(S1) < 2 or len(S2) < 2 or len(S1) >= n or len(S2) >= n:
                continue
            yield u, w, v, frozenset(S1), frozenset(S2)


# --------------------------------------------------------------------------
# B1: every structural Hajos / tree-join piece is 2-extremal
# --------------------------------------------------------------------------

def check_B1():
    from collections import Counter
    haj_fail = Counter()
    haj_total = 0
    tj_fail = Counter()
    tj_total = 0
    for (Ln, idx, n, arcs) in all_members():
        if is_base(n, arcs):
            continue
        for d1, d2 in O._hajos_decompositions(n, arcs):
            for (nb, ab) in (d1, d2):
                haj_total += 1
                for k, ok in piece_conditions(nb, ab).items():
                    if not ok:
                        haj_fail[k] += 1
        for blocks in O._tree_join_decompositions(n, arcs, max_internal=2):
            for (nb, ab) in blocks:
                tj_total += 1
                for k, ok in piece_conditions(nb, ab).items():
                    if not ok:
                        tj_fail[k] += 1
    return haj_total, dict(haj_fail), tj_total, dict(tj_fail)


# --------------------------------------------------------------------------
# B2: structural identities at the merge vertex
# --------------------------------------------------------------------------

def check_B2():
    n_seams = 0
    cross_violations = 0
    degree_violations = 0
    for (Ln, idx, n, arcs) in all_members((6, 7)):
        if is_base(n, arcs):
            continue
        arcset = set(arcs)
        for (u, w, v, S1, S2) in hajos_seams(n, arcs):
            n_seams += 1
            A = S1 - {v}
            B = S2 - {v}
            cross = [(a, b) for (a, b) in arcset
                     if (a in A and b in B) or (a in B and b in A)]
            if cross != [(u, w)]:
                cross_violations += 1
            vin_S1 = sum(1 for (a, b) in arcset if b == v and a in S1)
            vout_S1 = sum(1 for (a, b) in arcset if a == v and b in S1)
            vin_S2 = sum(1 for (a, b) in arcset if b == v and a in S2)
            vout_S2 = sum(1 for (a, b) in arcset if a == v and b in S2)
            # D1 = D[S1] + (u,v): at v, in = vin_S1 + 1, out = vout_S1.
            # D2 = D[S2] + (v,w): at v, in = vin_S2, out = vout_S2 + 1.
            d1_bal = (vin_S1 + 1 == vout_S1) and (vout_S1 >= 2)
            d2_bal = (vin_S2 == vout_S2 + 1) and (vin_S2 >= 2)
            if not (d1_bal and d2_bal):
                degree_violations += 1
    return n_seams, cross_violations, degree_violations


# --------------------------------------------------------------------------
# B3: tree-join A-blocks are 2-extremal
# --------------------------------------------------------------------------

def check_B3():
    rows = []
    for (Ln, idx, n, arcs) in all_members((7,)):
        if is_base(n, arcs):
            continue
        # only the tree-join-only members have NO Hajos seam
        if any(True for _ in O._hajos_decompositions(n, arcs)):
            continue
        blocks_info = []
        for blocks in O._tree_join_decompositions(n, arcs, max_internal=2):
            for (nb, ab) in blocks:
                blocks_info.append((nb, O.is_2extremal(nb, ab),
                                    O._is_generalised_wheel(nb, ab)))
        if blocks_info:
            rows.append((idx, blocks_info[:2]))
    return rows


# --------------------------------------------------------------------------
# B4: adversarial soundness probe
# --------------------------------------------------------------------------

def _hajos_join(n1, a1, u, v1, n2, a2, v2, w):
    a1 = set(a1)
    a2 = set(a2)
    if (u, v1) not in a1 or (v2, w) not in a2:
        return None
    a1.discard((u, v1))
    mp = {}
    nxt = n1
    for x in range(n2):
        if x == v2:
            mp[x] = v1
        else:
            mp[x] = nxt
            nxt += 1
    a2b = set()
    for (a, b) in a2:
        if (a, b) == (v2, w):
            continue
        a2b.add((mp[a], mp[b]))
    arcs = a1 | a2b
    arcs.add((u, mp[w]))
    return nxt, frozenset(arcs)


def check_B4(trials=80000, seed=99):
    import random
    random.seed(seed)
    seeds = []
    for n in (3, 4, 5):
        seeds += load_L(n)
    c3 = O.sym_cycle(3)
    tested = 0
    bad = 0
    for (n1, base) in seeds:
        allpairs = [(i, j) for i in range(n1) for j in range(n1) if i != j]
        for ntog in (1, 2):
            for _ in range(trials // (len(seeds) * 2) + 1):
                tog = random.sample(allpairs, ntog)
                a1 = set(base)
                for p in tog:
                    if p in a1:
                        a1.discard(p)
                    else:
                        a1.add(p)
                a1 = frozenset(a1)
                if O.is_2extremal(n1, a1):
                    continue           # want a BROKEN (non-2-extremal) piece
                if not O.is_strong(n1, a1):
                    continue
                for (u, v1) in a1:
                    for (v2, w) in c3[1]:
                        res = _hajos_join(n1, a1, u, v1, c3[0], c3[1], v2, w)
                        if res is None:
                            continue
                        nn, arcs = res
                        tested += 1
                        if O.is_2extremal(nn, arcs):
                            bad += 1
    return tested, bad


# --------------------------------------------------------------------------

def main():
    adversarial = "--adversarial" in sys.argv
    print("=" * 72)
    print("LEMMA B (reduction soundness) -- computational evidence")
    print("=" * 72)

    haj_total, haj_fail, tj_total, tj_fail = check_B1()
    print(f"\n[B1] structural Hajos pieces over L3..L7: {haj_total}")
    print(f"     condition failures: {haj_fail if haj_fail else 'NONE'}")
    print(f"     structural tree-join A-blocks over L3..L7: {tj_total}")
    print(f"     condition failures: {tj_fail if tj_fail else 'NONE'}")

    n_seams, cross_v, deg_v = check_B2()
    print(f"\n[B2] Hajos seams over L6 u L7: {n_seams}")
    print(f"     unique-cross-arc-is-join-arc violations: {cross_v}")
    print(f"     merge-vertex degree-split violations:    {deg_v}")

    rows = check_B3()
    print(f"\n[B3] tree-join-only members (L7) and their A-blocks "
          f"(nb, 2-extremal, gen-wheel):")
    for idx, info in rows:
        print(f"     L7.{idx}: {info}")

    if adversarial:
        tested, bad = check_B4()
        print(f"\n[B4] adversarial: broken-piece Hajos joins tested: {tested}")
        print(f"     that yielded a 2-EXTREMAL join: {bad}")
    else:
        print("\n[B4] adversarial probe skipped (pass --adversarial to run)")

    ok = (not haj_fail and not tj_fail and cross_v == 0 and deg_v == 0
          and len(rows) == 3 and all(
              all(b[1] for b in info) for _, info in rows))
    print("\n" + "=" * 72)
    print(f"OVERALL: {'PASS' if ok else 'FAIL'}")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
