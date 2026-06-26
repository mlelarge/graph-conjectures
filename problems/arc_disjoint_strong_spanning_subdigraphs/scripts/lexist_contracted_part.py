"""lexist_contracted_part.py -- red-team (L-exist) on the CONTRACTED-PART
population D^bullet<V_2> that CRUX-A actually needs (addresses the G13
population mismatch).

next_action (D4): the only admissible NEW computation is a checker VARIANT
that red-teams the CONTRACTED-PART multidigraph family D^bullet<V_2>
DIRECTLY -- NOT generic simple digraphs, NOT n>=6 generic.

REMINDER (G9 lesson, restated verbatim in next_action): D^bullet<V_2> is the
INDUCED subdigraph D<V_2> (no contracted vertex r), NOT a contraction, and
is NOT guaranteed 2-arc-strong. So the right population is:

  1. Generate 3-arc-strong (1,0)-near-split D (V = V_1 u V_2, D[V_2]
     semicomplete, exactly one V_1-internal arc), confirmed by the
     INDEPENDENT predicate is_one_zero_near_split.
  2. Induce M := D<V_2> (the contracted-part semicomplete multidigraph;
     parallel arcs preserved -- though a simple semicomplete V_2 has at
     most a digon per pair, the induced object may carry digons that the
     generic-simple census never sees in the SAME structural role).
  3. Run the EXACT L-exist checker (lexist_at_arc / check_digraph from
     check_lexist.py) on M at EVERY arc of M.

L-exist is the EXISTENTIAL-per-(M,a) rescue of the refuted universal
Conjecture L. For a FIXED (M,a) the verdict is EXACT (exhaustive
arc-disjoint in-arborescence PAIR enumeration). The OVERALL claim is
UNIVERSAL over (M, a) in the contracted-part class; we red-team it by
running over an EXHAUSTIVE small (|V_1|,|V_2|) census of the near-split
hosts, taking the INDUCED V_2-part of each 3-arc-strong host.

Falsifiable prediction: L-exist predicts 0 FAILS / 0 NO_PAIR across every
induced contracted-part M. A single (M, a) at which EVERY arc-disjoint
in-arb pair fails the strict-subset test (verdict FAILS) is a finite,
oracle-checkable REFUTATION of L-exist on the population CRUX-A needs --
which would KILL the H2 rescue and the unconditional (1,0)-near-split
theorem route.

Important honesty note: this is the CONTRACTED-PART variant, so it closes
the G13 population-mismatch gap that generic-simple check_lexist.py left
open. It is STILL a small-scope census; it cannot PROMOTE L-exist to a
theorem (universal_needs_generic_census). Its value is purely as a
red-team aimed at the correct population: survival rules out a cheap
contracted-part counterexample; a FAIL would refute the rescue outright.
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from digraph import Digraph  # noqa: E402
from generators.near_split import (  # noqa: E402
    enumerate_construction_A,
    is_one_zero_near_split,
)
from check_lexist import check_digraph  # noqa: E402  (EXACT same L-exist core)


def _arc_conn(n, arcs):
    return Digraph.from_arcs(range(n), [(u, v) for (u, v) in arcs]).arc_connectivity()


def chord_contraction(inst):
    """Return (k, arcs) for D^bullet, the CHORD CONTRACTION of the whole D
    (team/21 S1.2): the unique V_1-internal chord e_0=(p,q) is deleted and p,q
    are identified into a fresh vertex r; every other arc (x,y) is mapped by
    pi (p,q -> r), PRESERVING multiplicity (parallel arcs kept). D^bullet is
    proved 3-arc-strong when D is (team/21 S1.3). This -- NOT the bare induced
    D<V_2> -- is the object in L-exist's hypothesis 'for every 3-arc-strong
    D^bullet'. Self-loops at r (from arcs internal to {p,q}, none survive but
    guard anyway) are dropped.

    Relabel: r := 0, then the remaining vertices V \ {p,q} in increasing order.
    """
    e0 = tuple(inst.internal_arc)
    p, q = e0
    # pi: p,q -> r ; everyone else -> self
    others = sorted(v for v in range(inst.n) if v != p and v != q)
    relabel = {p: 0, q: 0}
    for i, v in enumerate(others, start=1):
        relabel[v] = i
    k = 1 + len(others)
    arcs = []
    for (x, y) in inst.arcs:
        if (x, y) == e0:           # chord e_0 deleted
            continue
        rx, ry = relabel[x], relabel[y]
        if rx == ry:               # self-loop at r -> dropped
            continue
        arcs.append((rx, ry))
    return k, arcs


def run(v1_size, v2_size, cap_per_v2_orientation, bridge_cap_per_pair,
        max_hosts=0):
    """Census over 3-arc-strong (1,0)-near-split hosts of given (|V1|,|V2|);
    for each, red-team L-exist on the INDUCED contracted-part M = D<V2>."""
    n_hosts_seen = 0          # near-split, independently confirmed
    n_hosts_3arc = 0          # of those, lambda(D) >= 3
    n_below_gate = 0          # D^bullet with lambda<3 (should be 0; out of class)
    n_parts_tested = 0        # distinct 3-arc-strong D^bullet L-exist-checked
    fails = []                # (M, a) where L-exist FAILS
    nopair = []               # (M, a) with NO arc-disjoint pair
    lam_part_hist = {}        # lambda(M) distribution -- M is NOT guaranteed >=2
    seen_part_keys = set()    # dedup identical induced parts (canonical-ish)

    for inst in enumerate_construction_A(
        v1_size, v2_size,
        cap_per_v2_orientation=cap_per_v2_orientation,
        bridge_cap_per_pair=bridge_cap_per_pair,
    ):
        if max_hosts and n_hosts_seen >= max_hosts:
            break
        D = inst.build()
        ok, _reason = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
        if not ok:
            continue
        n_hosts_seen += 1
        lamD = _arc_conn(inst.n, list(inst.arcs))
        if lamD < 3:
            continue
        n_hosts_3arc += 1

        k, sub_arcs = chord_contraction(inst)
        # dedup identical contracted parts (same vertex count + sorted arc multiset)
        key = (k, tuple(sorted(sub_arcs)))
        if key in seen_part_keys:
            continue
        seen_part_keys.add(key)

        lamM = _arc_conn(k, sub_arcs)
        lam_part_hist[lamM] = lam_part_hist.get(lamM, 0) + 1
        # GATE: L-exist's hypothesis is 'for every 3-arc-strong D^bullet'.
        # Only D^bullet with lambda>=3 are in the hypothesis class; lower-lambda
        # contractions are OUTSIDE L-exist and must NOT be counted as FAILS
        # (the G9/G13 object-mismatch trap). team/21 S1.3 proves lambda(D^bullet)
        # >=3 when D is 3-arc-strong, so we expect ALL to pass this gate; we
        # assert it and SKIP (recording) any that somehow don't.
        if lamM < 3:
            n_below_gate += 1
            continue
        n_parts_tested += 1

        # EXACT L-exist red-team on the 3-arc-strong contracted whole D^bullet.
        res = check_digraph(k, sub_arcs, name=inst.name)
        if res["fails"]:
            fails.append({"host": inst.name, "k": k, "lambdaM": lamM,
                          "lambdaD": lamD, "M_arcs": sub_arcs, **res})
        if res["nopair"]:
            nopair.append({"host": inst.name, "k": k, "lambdaM": lamM,
                           "M_arcs": sub_arcs, **res})

    return {
        "scope": f"contracted-part D^bullet (chord contraction), |V1|={v1_size} |V2|={v2_size}",
        "object": "D^bullet = chord contraction of the whole 3-arc-strong (1,0)-near-split D (team/21 S1.2); L-exist hypothesis object",
        "n_nearsplit_hosts_confirmed": n_hosts_seen,
        "n_hosts_3arcstrong": n_hosts_3arc,
        "n_Dbullet_below_lambda3_gate": n_below_gate,
        "n_distinct_Dbullet_tested": n_parts_tested,
        "lambda_Dbullet_hist": {str(k): v for k, v in sorted(lam_part_hist.items())},
        "n_with_Lexist_FAILS": len(fails),
        "n_with_NO_PAIR": len(nopair),
        "fail_examples": fails[:5],
        "nopair_examples": nopair[:5],
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("v1", type=int)
    ap.add_argument("v2", type=int)
    ap.add_argument("--orient-cap", type=int, default=64,
                    help="cap on V2 semicomplete orientations sampled")
    ap.add_argument("--bridge-cap", type=int, default=32,
                    help="cap on bridge subsets per orientation")
    ap.add_argument("--max-hosts", type=int, default=0,
                    help="stop after this many confirmed near-split hosts")
    args = ap.parse_args()
    out = run(args.v1, args.v2, args.orient_cap, args.bridge_cap,
              max_hosts=args.max_hosts)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
