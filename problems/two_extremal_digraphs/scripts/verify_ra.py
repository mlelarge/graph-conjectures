#!/usr/bin/env python3
"""
verify_ra.py
============
Reproducible verification of Residual Lemma R-a (ANGLE C, directed-Hajos / MC=1
side) and the EXTREMAL-a bookkeeping, over the complete non-base truth set
L_6 u L_7 and the hard instances 7.33 / 7.7 / 7.14 / 7.36 / 7.17.

Claims tested (all n<=7 -> EVIDENCE only, never a theorem):
  (T1) every mixed 2-cut (v,e) has the single arc e=u->w as the UNIQUE arc between
       S1\\{v} and S2\\{v}                                          [definitional]
  (T2) every mixed 2-cut promotes to a genuine 2-extremal directed-Hajos join
  (T3) all 5 2-extremality clauses hold for BOTH pieces of every promoting cut
  (T4) merge-vertex Eulerian balance: v_in^S1+1==v_out^S1 and v_in^S2==v_out^S2+1
  (T5) R-a-star: every MC=1 non-base member has a NON-ISOLATING promoting cut

Run:  python3 scripts/verify_ra.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import h2_oracle as O
import seam_invariant as S
from h2_oracle import _component, is_strong, is_2connected, is_eulerian_deg, lambda_D


def parse(oc):
    head, rest = oc.split("|")
    n = int(head)
    arcs = [tuple(int(x) for x in t.split(",")) for t in rest.split(";")]
    return n, arcs


def cut_pieces(n, arcs, v, e):
    """Yield (u, w, S1, S2, d1, d2) for each orientation of e that realises a
    directed-Hajos inverse at (v, e)."""
    arcset = set(arcs)
    a, b = tuple(e)
    for (u, w) in [(a, b), (b, a)]:
        if (u, w) not in arcset or (w, u) in arcset:
            continue
        rest = arcset - {(u, w)}
        ru = [set() for _ in range(n)]
        for (x, y) in rest:
            ru[x].add(y); ru[y].add(x)
        cu = _component(ru, u, blocked=v)
        cw = _component(ru, w, blocked=v)
        if w in cu or u in cw:
            continue
        S1 = cu | {v}; S2 = cw | {v}
        if S1 & S2 != {v} or S1 | S2 != set(range(n)):
            continue
        if not all((x in S1 and y in S1) or (x in S2 and y in S2) for (x, y) in rest):
            continue
        d1 = O._induce_plus(arcs, S1, extra=(u, v))
        d2 = O._induce_plus(arcs, S2, extra=(v, w))
        yield u, w, S1, S2, d1, d2


def two_ext_clauses(d):
    nn, aa = d
    return {
        "eulerian": is_eulerian_deg(nn, aa, 2),
        "strong": is_strong(nn, aa),
        "2connected": is_2connected(nn, aa),
        "lambda2": O.lambda_at_most(nn, aa, 2) and lambda_D(nn, aa) == 2,
        "chi3": O.chi_vec(nn, aa) == 3,
    }


def main():
    data = json.load(open(os.path.join(ROOT, "data", "seam_search_L6_L7.json")))
    t1 = [0, 0]; t2 = [0, 0]; t3 = [0, 0]; t4 = [0, 0]
    members_mc1 = 0; members_nonisolating = 0
    for r in data["results"]:
        if r["status"] == "base":
            continue
        n, arcs = parse(r["oracle_canon"])
        arcset = set(arcs)
        cuts = S.mixed_2_cuts(n, arcs)
        if not cuts:
            continue
        members_mc1 += 1
        member_has_nonisolating = False
        for (v, e) in cuts:
            for (u, w, S1, S2, d1, d2) in cut_pieces(n, arcs, v, e):
                # T1: unique crossing arc
                cross = [(x, y) for (x, y) in arcset
                         if (x in S1 - {v} and y in S2 - {v})
                         or (x in S2 - {v} and y in S1 - {v})]
                t1[1] += 1; t1[0] += (cross == [(u, w)])
                # T2/T3: promotion + clauses
                promotes = (d1 and d2 and O.is_2extremal(*d1) and O.is_2extremal(*d2))
                t2[1] += 1; t2[0] += bool(promotes)
                if d1 and d2:
                    for d in (d1, d2):
                        cl = two_ext_clauses(d)
                        t3[1] += 1; t3[0] += all(cl.values())
                # T4: Eulerian balance at v
                vin1 = sum(1 for (x, y) in arcs if y == v and x in S1 - {v})
                vout1 = sum(1 for (x, y) in arcs if x == v and y in S1 - {v})
                vin2 = sum(1 for (x, y) in arcs if y == v and x in S2 - {v})
                vout2 = sum(1 for (x, y) in arcs if x == v and y in S2 - {v})
                t4[1] += 1
                t4[0] += (vin1 + 1 == vout1) and (vin2 == vout2 + 1)
                # R-a-star: non-isolating promoting cut
                if promotes and len(S1) >= 3 and len(S2) >= 3:
                    member_has_nonisolating = True
        if member_has_nonisolating:
            members_nonisolating += 1

    print("=" * 68)
    print("R-a verification over L_6 u L_7 (non-base); n<=7 EVIDENCE only")
    print("=" * 68)
    print(f"(T1) unique crossing arc            : {t1[0]}/{t1[1]}")
    print(f"(T2) promotes to 2-ext Hajos join   : {t2[0]}/{t2[1]}")
    print(f"(T3) both pieces 2-extremal (5 cl.) : {t3[0]}/{t3[1]}")
    print(f"(T4) merge-vertex Eulerian balance  : {t4[0]}/{t4[1]}")
    print(f"(T5) R-a-star: MC=1 members with a non-isolating promoting cut: "
          f"{members_nonisolating}/{members_mc1}")
    ok = (t1[0] == t1[1] and t2[0] == t2[1] and t3[0] == t3[1]
          and t4[0] == t4[1] and members_nonisolating == members_mc1)
    print("=" * 68)
    print(f"OVERALL: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
