"""ANGLE D: operational splice test on the iso-11 EQ_2 / cap-00 gadgets at n=8.

Goal: the both-case (iso-11 AND cap-00) is empty, so a splice is hypothetical.
We probe what a splice WOULD have to manufacture by:

 1. Extracting all iso-11 EQ_2 gadgets at n=8 (the cap-11 family, 6 iso-classes)
    with a role-labeled core set {uP,vP,uQ,vQ} U C(P) U C(Q) and their iso-11
    order sigma_1.
 2. For each, attempting EVERY single-port reorder to a mixed value (1,0)/(0,1):
    search for ANY LFO realizing it (none, since EQ_2), and find the MINIMUM
    back-degree-excess order realizing each mixed value (the obstruction), and
    report WHICH endpoint/cycle blocks it.
 3. Extracting signature-matched cap-00 gadgets (same port-quad type (1,1,2,2),
    cross-arc vP->uQ, score-order uP<vP<uQ<vQ) and their cap-00 order sigma_0;
    verifying each has NO iso-11 LFO (consistent with cap_both=0) and reporting
    which endpoint saturates on the 11 value.
 4. Aligning sigma_0 (from cap-00) against sigma_1 (from iso-11) on the
    role-labeled core, to identify the structural feature present in one family
    but absent in the other: what the splice would have to create.
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from itertools import combinations, permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fanout_barrier_checks import reps as _reps, disjoint as _disjoint
from two_aux_eq3_search import enum_lfos_deg

Matrix = list[list[int]]


def arc(T, x, y):
    return (x, y) if T[x][y] else (y, x)


def cset(T, u, v):
    """C(P) = {w : v->w and w->u} = 3-cycle partners of arc u->v."""
    return [w for w in range(len(T))
            if w not in (u, v) and T[v][w] and T[w][u]]


def score(T, v):
    return sum(T[v])


def lf_status(edges, n):
    """Return (max_degree, has_cycle) for an undirected back-arc edge set."""
    deg = [0] * n
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    cyc = False
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        ru, rv = find(u), find(v)
        if ru == rv:
            cyc = True
        else:
            par[ru] = rv
    return max(deg) if deg else 0, cyc


def back_edges_and_deg(T, order):
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    edges = []
    deg = [0] * n
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[u] > pos[v]:
                edges.append((u, v))
                deg[u] += 1
                deg[v] += 1
    return edges, deg, pos


def excess_of_order(T, order):
    """Linear-forest defect of an order: (#degree-excess units + #cycle-edges).

    A proxy for 'how far from a valid LFO'.  0 iff a valid LFO."""
    n = len(T)
    edges, deg, _ = back_edges_and_deg(T, order)
    deg_excess = sum(max(0, d - 2) for d in deg)
    # spanning-forest cycle count = E - (V_touched - components_touched)
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    cyc_edges = 0
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            cyc_edges += 1
        else:
            par[ru] = rv
    return deg_excess + cyc_edges, deg_excess, cyc_edges, deg, edges


def min_excess_mixed(T, P, Q, target):
    """Minimum-excess order realizing a target mixed value (sP,sQ), searched
    over ALL n! orders (n=8 is 40320, fine).  Returns the obstruction:
    the min total excess, and at the witnessing order which endpoints are
    saturated (deg>2) and how many cycle-edges remain."""
    n = len(T)
    uP, vP = arc(T, *P)
    uQ, vQ = arc(T, *Q)
    best = None
    for order in permutations(range(n)):
        pos = [0] * n
        for i, v in enumerate(order):
            pos[v] = i
        sP = 1 if pos[uP] > pos[vP] else 0
        sQ = 1 if pos[uQ] > pos[vQ] else 0
        if (sP, sQ) != target:
            continue
        tot, de, ce, deg, edges = excess_of_order(T, order)
        if best is None or tot < best[0]:
            # which port endpoints are saturated / what blocks
            sat = [v for v in (*P, *Q) if deg[v] > 2]
            best = (tot, de, ce, list(order), sat, deg[:])
            if tot == 0:
                break
    if best is None:
        return None
    tot, de, ce, order, sat, deg = best
    return {
        "target": target,
        "min_total_excess": tot,
        "degree_excess": de,
        "cycle_edges": ce,
        "witness_order": order,
        "saturated_port_endpoints": sat,
        "port_endpoint_degs": {v: deg[v] for v in (*P, *Q)},
    }


def role_label(T, P, Q, order):
    """Role-labeled position list for the core set in a given order."""
    uP, vP = arc(T, *P)
    uQ, vQ = arc(T, *Q)
    pos = [0] * len(T)
    for i, v in enumerate(order):
        pos[v] = i
    CP, CQ = cset(T, uP, vP), cset(T, uQ, vQ)
    label = {uP: "uP", vP: "vP", uQ: "uQ", vQ: "vQ"}
    for w in CP:
        label[w] = label.get(w, "") + ("cP" if w not in label else "+cP")
    for w in CQ:
        label[w] = label.get(w, "") + ("cQ" if w not in label else "+cQ")
    seq = [(pos[v], label.get(v, f"x{v}"), v) for v in range(len(T))]
    seq.sort()
    return [(lbl, v) for _, lbl, v in seq], CP, CQ


def find_iso11_eq2(n=8):
    """All iso-11 EQ_2 gadgets: R_arc={00,11}, some LFO realizes (1,1) with all
    four port endpoints back-degree exactly 1.  Returns role-labeled records."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]
    out = []
    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            iso_order = None
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (1, 1) and all(deg[v] == 1 for v in (a, b, c, d)) \
                        and iso_order is None:
                    iso_order = [0] * n
                    for v, p in enumerate(pos):
                        iso_order[p] = v
            if frozenset(R) != frozenset({(0, 0), (1, 1)}):
                continue
            if iso_order is None:
                continue
            out.append({"T": [r[:] for r in T], "P": P, "Q": Q,
                        "iso11_order": iso_order})
    return out


def port_quad_signature(T, P, Q):
    """Port-local signature (D86): score order of endpoints, quad score-seq,
    cross-arc direction vP->uQ."""
    uP, vP = arc(T, *P)
    uQ, vQ = arc(T, *Q)
    quad = [uP, vP, uQ, vQ]
    sub_scores = sorted(sum(1 for y in quad if T[x][y]) for x in quad)
    s = {v: score(T, v) for v in quad}
    score_order = (s[uP] < s[vP] < s[uQ] < s[vQ])
    cross_vP_uQ = T[vP][uQ] == 1
    return {"quad_score_seq": tuple(sub_scores),
            "score_order_uP_vP_uQ_vQ": score_order,
            "cross_vP_to_uQ": cross_vP_uQ,
            "endpoint_scores": (s[uP], s[vP], s[uQ], s[vQ])}


def find_cap00_eq2(n=8):
    """All cap-00 EQ_2 gadgets: R_arc={00,11}, some LFO realizes (0,0) with all
    four port endpoints back-degree <=1.  Records sigma_0 and whether iso-11."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pts = [(p, q) for p, q in combinations(pairs, 2) if _disjoint((p, q))]
    out = []
    for T in _reps(n):
        lfos = enum_lfos_deg(T)
        if not lfos:
            continue
        for P, Q in pts:
            a, b = P
            c, d = Q
            uP, vP = arc(T, *P)
            uQ, vQ = arc(T, *Q)
            R = set()
            cap00_order = None
            min_sat00 = None
            iso11 = False
            for pos, deg in lfos:
                sP = 1 if pos[uP] > pos[vP] else 0
                sQ = 1 if pos[uQ] > pos[vQ] else 0
                R.add((sP, sQ))
                if (sP, sQ) == (0, 0):
                    sat = sum(1 for v in (a, b, c, d) if deg[v] >= 2)
                    if min_sat00 is None or sat < min_sat00:
                        min_sat00 = sat
                    if sat == 0 and cap00_order is None:
                        cap00_order = [0] * n
                        for v, p in enumerate(pos):
                            cap00_order[p] = v
                if (sP, sQ) == (1, 1) and all(deg[v] == 1 for v in (a, b, c, d)):
                    iso11 = True
            if frozenset(R) != frozenset({(0, 0), (1, 1)}):
                continue
            if cap00_order is None:
                continue
            out.append({"T": [r[:] for r in T], "P": P, "Q": Q,
                        "cap00_order": cap00_order, "iso11": iso11})
    return out


def min_sat_on_11(T, P, Q):
    """Over all LFOs realizing (1,1), the minimum saturated-endpoint set
    (endpoints with back-degree >= 2).  Reports WHICH endpoints saturate."""
    n = len(T)
    uP, vP = arc(T, *P)
    uQ, vQ = arc(T, *Q)
    lfos = enum_lfos_deg(T)
    best = None
    for pos, deg in lfos:
        sP = 1 if pos[uP] > pos[vP] else 0
        sQ = 1 if pos[uQ] > pos[vQ] else 0
        if (sP, sQ) != (1, 1):
            continue
        sat = frozenset(v for v in (*P, *Q) if deg[v] >= 2)
        if best is None or len(sat) < len(best):
            best = sat
    return None if best is None else sorted(best)


def run():
    iso = find_iso11_eq2(8)
    cap = find_cap00_eq2(8)
    print(f"iso-11 EQ_2 gadgets found: {len(iso)}")
    print(f"cap-00 EQ_2 gadgets found: {len(cap)}")
    print(f"cap-both (iso-11 AND cap-00): {sum(1 for g in cap if g['iso11'])}")
    print("=" * 70)

    # --- iso-11 family: role labels, splice/obstruction test ---
    print("\n### ISO-11 EQ_2 GADGETS (sigma_1) — splice-to-mixed obstruction\n")
    iso_obstr = []
    splice_shapes = []
    for i, g in enumerate(iso):
        T, P, Q = g["T"], g["P"], g["Q"]
        seq, CP, CQ = role_label(T, P, Q, g["iso11_order"])
        sig = port_quad_signature(T, P, Q)
        ob01 = min_excess_mixed(T, P, Q, (0, 1))
        ob10 = min_excess_mixed(T, P, Q, (1, 0))
        print(f"[iso {i}] P={P} Q={Q}  |C(P)|={len(CP)} |C(Q)|={len(CQ)}")
        print(f"   sigma_1 role order: {[s[0] for s in seq]}")
        print(f"   sig: quad={sig['quad_score_seq']} "
              f"score_order={sig['score_order_uP_vP_uQ_vQ']} "
              f"cross_vP->uQ={sig['cross_vP_to_uQ']}")
        for ob in (ob01, ob10):
            print(f"   min-excess mixed {ob['target']}: total={ob['min_total_excess']} "
                  f"deg_excess={ob['degree_excess']} cyc={ob['cycle_edges']} "
                  f"sat_port_endpts={ob['saturated_port_endpoints']}")
        iso_obstr.append({"i": i, "P": P, "Q": Q, "CP": CP, "CQ": CQ,
                          "sig": sig, "ob01": ob01, "ob10": ob10,
                          "role_seq": [s[0] for s in seq]})
        splice_shapes.append((tuple(s[0] for s in seq),
                              ob01["min_total_excess"], ob01["cycle_edges"],
                              ob10["min_total_excess"], ob10["cycle_edges"]))

    # --- cap-00 family: signature match + iso-11 absence reason ---
    print("\n### CAP-00 EQ_2 GADGETS (sigma_0) — signature-matched subset\n")
    # signature of the iso-11 family (uniform per D86)
    iso_sigs = {(o["sig"]["quad_score_seq"], o["sig"]["cross_vP_to_uQ"])
                for o in iso_obstr}
    matched = []
    for g in cap:
        sig = port_quad_signature(g["T"], g["P"], g["Q"])
        if (sig["quad_score_seq"], sig["cross_vP_to_uQ"]) in iso_sigs:
            matched.append((g, sig))
    print(f"cap-00 gadgets matching iso-11 port-signature "
          f"(quad+cross): {len(matched)} of {len(cap)}")
    sample = matched[:6]
    cap00_role_seqs = []
    for j, (g, sig) in enumerate(sample):
        T, P, Q = g["T"], g["P"], g["Q"]
        seq, CP, CQ = role_label(T, P, Q, g["cap00_order"])
        sat11 = min_sat_on_11(T, P, Q)
        print(f"[cap {j}] P={P} Q={Q}  |C(P)|={len(CP)} |C(Q)|={len(CQ)} "
              f"iso11={g['iso11']}")
        print(f"   sigma_0 role order: {[s[0] for s in seq]}")
        print(f"   min-saturated endpoints on the 11 value: {sat11}")
        cap00_role_seqs.append([s[0] for s in seq])

    # --- splice-shape uniformity check ---
    print("\n### SPLICE-SHAPE UNIFORMITY\n")
    uniq_iso_seq = set(tuple(o["role_seq"]) for o in iso_obstr)
    print(f"distinct sigma_1 role orders among iso-11 gadgets: {len(uniq_iso_seq)}")
    for s in sorted(uniq_iso_seq):
        print("   ", s)
    ob_shapes = Counter((o["ob01"]["min_total_excess"], o["ob01"]["cycle_edges"],
                         o["ob10"]["min_total_excess"], o["ob10"]["cycle_edges"])
                        for o in iso_obstr)
    print(f"distinct (excess01,cyc01,excess10,cyc10) obstruction shapes: "
          f"{dict(ob_shapes)}")
    return iso_obstr, matched


if __name__ == "__main__":
    run()
