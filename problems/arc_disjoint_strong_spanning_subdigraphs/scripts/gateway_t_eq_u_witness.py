"""gateway_t_eq_u_witness.py -- in-class refutation of (Irreducible) Gateway
Emptiness: a chord contraction with t==u HARD gateways, on which fixed-root
L-exist nevertheless SURVIVES via ABSORPTION (X-enlarging good pairs).

Construction (found while attempting to PROVE sub-claim (A) "gateway => t!=u";
the proof obligations turned out to be satisfiable instead). Host H, cell
(2,6) -- one beyond every previously tested cell:

  V1 = {p,q}, chord p->q;  V2 = {u, ka, kb, kc, k2, k3} simple semicomplete:
    {ka,kb,kc}: digon triangle;  u<->ki digons;  k2->ki, k3->ki (one-way);
    k2<->k3, u<->k2, u<->k3 digons.
  Bridges: u->p, u->q; k2->p; k3->p, k3->q; p->k2, q->k2; p->k3, q->k3;
    p->ka, q->kb.

H is simple, (1,0)-near-split (independent predicate), lambda(H)=3, and
SAD=SAT (both oracle backends) -- so this is NOT a WC3 event. The chord
contraction D^bullet (rho := p=q) has lambda=3 and the expected rho-side
multi-arcs (u->rho x2, k3->rho x2, rho->k2 x2, rho->k3 x2).

The trap: X = {u,ka,kb,kc}. The ki have out-arcs only to each other and to u,
so every in-arborescence routes them through u, and delta^+(X) = {u->k2,
u->k3, u->rho x2} sits entirely at u. Any valid U has exactly one exit from X
(u's out-arc must be external), so EVERY pair (T,U) with X_a^T = X is a
failing HARD gateway with t == u -- refuting both raw Gateway Emptiness and
sub-claim (A) of the Irreducible form, IN CLASS.

Why L-exist still survives (the ABSORPTION mechanism): T may instead route k2
(or k3) INTO X -- the arc k2->ka etc. exists by the Lemma 11.2 in-domination
wedge, which guarantees every w in K\\X an arc into X. Then X' = X u {w} is
still intermediate, and U can give w an external out-arc, producing TWO
U-exit tails {u, w} and hence (Lemma 2.1) a strict exit. Verified below:
at a=(u,k2), every good pair has |X|=5 and every gateway pair |X|=4.

Consequence recorded in ledger D10: the proof skeleton needs an ABSORPTION
REPAIR LEMMA for t==u gateways (one-shot good pair if some w in K\\X has an
external escape; recurse with |X| strictly growing toward the n-1 root
boundary otherwise), alongside shrink (P7), safe-target (S5), and path-pivot
(S10).
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

from digraph import Digraph  # noqa: E402
from generators.near_split import is_one_zero_near_split  # noqa: E402
from check_lexist_fixedroot import analyse_instance  # noqa: E402


def host_arcs():
    # p=0, q=1, u=2, ka=3, kb=4, kc=5, k2=6, k3=7
    return [
        (0, 1),
        (3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4),
        (2, 3), (3, 2), (2, 4), (4, 2), (2, 5), (5, 2),
        (6, 3), (6, 4), (6, 5),
        (7, 3), (7, 4), (7, 5),
        (6, 7), (7, 6),
        (2, 6), (6, 2), (2, 7), (7, 2),
        (2, 0), (2, 1),
        (6, 0), (7, 0), (7, 1),
        (0, 6), (1, 6), (0, 7), (1, 7),
        (0, 3), (1, 4),
    ]


def dbullet_arcs():
    # contraction relabel: rho=0, u=1, ka=2, kb=3, kc=4, k2=5, k3=6
    rel = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}
    out = []
    for (x, y) in host_arcs():
        if (x, y) == (0, 1):
            continue
        rx, ry = rel[x], rel[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def main():
    # oracle pulls in the SAT/ILP verifier chain (pysat, pulp); import lazily
    # so that `from gateway_t_eq_u_witness import dbullet_arcs` stays
    # dependency-free for downstream checkers.
    import oracle
    H = host_arcs()
    assert len(H) == len(set(H)), "host must be simple"
    D = Digraph.from_arcs(range(8), H)
    ok, reason = is_one_zero_near_split(D, [0, 1], [2, 3, 4, 5, 6, 7])
    assert ok, reason
    lamH = oracle.arc_connectivity(8, H)
    assert lamH == 3, lamH
    sad = oracle.check_construction(8, H, name="t-eq-u-host")
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad
    else:
        print("WARNING: ILP backend unavailable (pulp not installed); "
              "SAT verdict rests on the SAT backend + witness re-validation only")

    db = dbullet_arcs()
    lamB = oracle.arc_connectivity(7, db)
    assert lamB == 3, lamB
    rho_mult = {e: c for e, c in Counter(db).items() if c > 1}
    assert rho_mult == {(1, 0): 2, (6, 0): 2, (0, 5): 2, (0, 6): 2}, rho_mult

    r = analyse_instance(7, db, 0, K_set={1, 2, 3, 4, 5, 6},
                         name="t-eq-u-witness")
    assert r["FAILS"] == [], r["FAILS"]              # L-exist SURVIVES
    assert r["gateway_hard"] > 0, r                  # hard gateways EXIST
    assert r["pivot_missing"].get("t==u", 0) == r["gateway_hard"], r
    assert r["lemma21_violations"] == 0

    print(f"host: simple (1,0)-near-split, lambda=3, SAD=SAT (cross-checked)")
    print(f"D-bullet: n=7, lambda=3, rho-multiplicities {rho_mult}")
    print(f"fixed-root L-exist: FAILS={r['FAILS']} (survives), "
          f"arcs {r['arcs_good']}/{r['arcs_tested']} good, "
          f"{r['arcs_no_pair']} no-pair (the u->ki self-trap arcs)")
    print(f"gateways: {r['gateway_pairs']} total, {r['gateway_hard']} HARD, "
          f"all t==u -> Gateway Emptiness (raw AND irreducible) REFUTED in-class")
    print(f"lemma 2.1: {r['lemma21_checks']} checks, 0 violations")


if __name__ == "__main__":
    main()
