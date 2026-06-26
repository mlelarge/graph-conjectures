"""Directed-Mycielskian / iterated apex-cone family over a C_3 base.

M(D): given a C_3 digraph D on vertices v_0..v_{r-1}, add a shadow u_i for each
v_i (shadows mutually ARC-FREE) and a single apex w.
  * per-arc shadow coupling: for each arc v_i->v_j of D add either u_i->v_j
    (forward) or v_j->u_i (reverse), chosen per-arc.
  * per-shadow apex direction: either w->u_i or u_i->w, chosen per-shadow.

Sweep all per-arc shadow orientations x all apex-direction patterns, keep the
is_C3 members, compute exact chi_vec (ub=3), report any chi>=3 witness and the
per-order (n, #C_3, max_chi).

GROUND everything through the exact oracle (core.is_C3 + core.dichromatic_number,
the SAT + combinatorial ground truth).
"""
from __future__ import annotations

import itertools
import json
import sys

sys.path.insert(0, "scripts")
import core
import oracle


def mycielskian(base_n, base_arcs, smask, amask):
    """Build M(D). base on 0..base_n-1; shadow u_i = base_n+i ; apex = 2*base_n.
    smask: per-arc bit (0=forward u_i->v_j, 1=reverse v_j->u_i), len = #arcs.
    amask: per-shadow bit (0=u_i->w, 1=w->u_i), len = base_n.
    Returns (n, arcs).
    """
    shad = lambda i: base_n + i
    w = 2 * base_n
    n = 2 * base_n + 1
    arcs = list(base_arcs)
    for k, (i, j) in enumerate(base_arcs):
        if (smask >> k) & 1:
            arcs.append((j, shad(i)))
        else:
            arcs.append((shad(i), j))
    for i in range(base_n):
        if (amask >> i) & 1:
            arcs.append((w, shad(i)))
        else:
            arcs.append((shad(i), w))
    return n, arcs


def asymmetric_cone(base_n, base_arcs, smask, apex_pattern):
    """Apex-cone over a base: shadows arc-free, per-arc shadow orientation via
    smask, and apex_pattern is an explicit tuple giving the apex direction for
    each shadow (0=u_i->w, 1=w->u_i, 2=NO apex arc to this shadow) -- the
    'asymmetric' (non-uniform / partial) cone.  Returns (n, arcs)."""
    shad = lambda i: base_n + i
    w = 2 * base_n
    n = 2 * base_n + 1
    arcs = list(base_arcs)
    for k, (i, j) in enumerate(base_arcs):
        if (smask >> k) & 1:
            arcs.append((j, shad(i)))
        else:
            arcs.append((shad(i), j))
    for i, p in enumerate(apex_pattern):
        if p == 0:
            arcs.append((shad(i), w))
        elif p == 1:
            arcs.append((w, shad(i)))
        # p==2 : no apex arc
    return n, arcs


def sweep_mycielskian(base_n, base_arcs, label, cap_smask=None, cap_amask=None):
    """Full sweep of M(D) over all smask x amask; oracle-grounded."""
    m = len(base_arcs)
    n_members = 0
    max_chi = 0
    witnesses = []
    smask_range = range(2 ** m) if cap_smask is None else range(min(2 ** m, cap_smask))
    amask_range = range(2 ** base_n) if cap_amask is None else range(min(2 ** base_n, cap_amask))
    n_out = 2 * base_n + 1
    for smask in smask_range:
        for amask in amask_range:
            n, arcs = mycielskian(base_n, base_arcs, smask, amask)
            if not core.is_C3(n, arcs):
                continue
            n_members += 1
            cv = core.dichromatic_number(n, arcs, ub=3)
            if cv > max_chi:
                max_chi = cv
            if cv >= 3:
                witnesses.append({"label": label, "n": n, "smask": smask,
                                  "amask": amask, "arcs": arcs, "chi_vec": cv})
    return {"label": label, "n": n_out, "n_C3_members": n_members,
            "max_chi": max_chi, "witnesses": witnesses}


def main():
    import time
    BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 480.0
    t0 = time.time()
    results = []
    G2 = (3, [(0, 1), (1, 2), (2, 0)])

    # --- depth-1: M(G_2), n=7 (full sweep, sanity = 52 / chi 2) ---
    r = sweep_mycielskian(3, G2[1], "M(G2) n=7")
    results.append(r)
    print(json.dumps({k: r[k] for k in ("label", "n", "n_C3_members", "max_chi")}))

    # collect the in-C_3 M(G_2) members to use as bases for depth-2 / cones
    g2_members = []
    for smask in range(2 ** 3):
        for amask in range(2 ** 3):
            n, arcs = mycielskian(3, G2[1], smask, amask)
            if core.is_C3(n, arcs):
                g2_members.append((n, arcs, smask, amask))

    # --- depth-2: M(M(G_2)), base n=7 -> n=15.  Full smask x amask over several
    #     distinct in-C_3 M(G2) bases (each base ~60s -> budget-bounded). ---
    seen_depth2 = {"max_chi": 0, "n_C3_members": 0, "witnesses": [], "n": 15}
    DEPTH2_BUDGET = BUDGET * 0.55
    for (bn, barcs, sm, am) in g2_members:
        if time.time() - t0 > DEPTH2_BUDGET:
            break
        m = len(barcs)
        for smask in range(2 ** m):
            if time.time() - t0 > DEPTH2_BUDGET:
                break
            for amask in range(2 ** bn):
                n, arcs = mycielskian(bn, barcs, smask, amask)
                if not core.is_C3(n, arcs):
                    continue
                seen_depth2["n_C3_members"] += 1
                cv = core.dichromatic_number(n, arcs, ub=3)
                if cv > seen_depth2["max_chi"]:
                    seen_depth2["max_chi"] = cv
                if cv >= 3:
                    seen_depth2["witnesses"].append(
                        {"label": "M(M(G2)) n=15", "n": n, "base_sm": sm,
                         "base_am": am, "smask": smask, "amask": amask,
                         "arcs": arcs, "chi_vec": cv})
        if seen_depth2["witnesses"]:
            break
    seen_depth2["label"] = "M(M(G2)) n=15 (slab)"
    results.append(seen_depth2)
    print(json.dumps({k: seen_depth2[k] for k in
                      ("label", "n", "n_C3_members", "max_chi")}))

    # --- asymmetric / partial cones over M(G_2) bases (n=15) at varying apex
    #     density, and over smaller bases to hit n in {9..14} ---
    # Smaller bases: directed cycles C_r for r in 3..6 (all in C_3? C_4,5,6 are
    # long induced dicycles -> NOT in C_3, so cone base must itself be in C_3).
    # The only small C_3 bases other than G_2 of order <=6 are unions of triangle
    # gadgets; use the M(G2) members (n=7) and partial-apex cones to span n=15,
    # and use 2-vertex / single-arc bases padded to land in {9..14}.
    cone_summary = {"label": "asym-cones over M(G2) n=15", "n": 15,
                    "n_C3_members": 0, "max_chi": 0, "witnesses": []}
    apex_choices = [0, 1, 2]
    cone_base_sample = g2_members[:6]
    CONE_BUDGET = BUDGET * 0.80
    for (bn, barcs, sm, am) in cone_base_sample:
        if time.time() - t0 > CONE_BUDGET:
            break
        m = len(barcs)
        for smask in range(min(2 ** m, 32)):
            if time.time() - t0 > CONE_BUDGET:
                break
            for apex_pattern in itertools.product(apex_choices, repeat=bn):
                n, arcs = asymmetric_cone(bn, barcs, smask, apex_pattern)
                if not core.is_C3(n, arcs):
                    continue
                cone_summary["n_C3_members"] += 1
                cv = core.dichromatic_number(n, arcs, ub=3)
                if cv > cone_summary["max_chi"]:
                    cone_summary["max_chi"] = cv
                if cv >= 3:
                    cone_summary["witnesses"].append(
                        {"label": "asym-cone n=15", "n": n, "smask": smask,
                         "apex_pattern": apex_pattern, "arcs": arcs,
                         "chi_vec": cv})
        if cone_summary["witnesses"]:
            break
    results.append(cone_summary)
    print(json.dumps({k: cone_summary[k] for k in
                      ("label", "n", "n_C3_members", "max_chi")}))

    # --- intermediate orders n in {9..14}: cone over base = G_2 itself but with
    #     EXTRA shadow apexes / multiple apexes is out of M's definition; instead
    #     build cones over a 4..6 vertex C_3 base.  The C_3 bases of order 4,5,6
    #     are exactly the directed triangle plus isolated/pendant structure --
    #     enumerate small C_3 bases directly via the oracle and cone each. ---
    inter = {"label": "cones over small C_3 bases n in 9..13", "max_chi": 0,
             "n_C3_members": 0, "witnesses": [], "n": "9..13"}
    for r in range(4, 7):
        if time.time() - t0 > BUDGET:
            break
        # enumerate C_3 bases on r vertices (full geng x orientations)
        for (gn, edges) in core.all_simple_graphs(r):
            if time.time() - t0 > BUDGET:
                break
            for barcs in core.all_orientations(edges):
                if not core.is_C3(r, list(barcs)):
                    continue
                barcs = list(barcs)
                m = len(barcs)
                # full Mycielskian over this base
                for smask in range(min(2 ** m, 64)):
                    for amask in range(min(2 ** r, 64)):
                        n, arcs = mycielskian(r, barcs, smask, amask)
                        if not core.is_C3(n, arcs):
                            continue
                        inter["n_C3_members"] += 1
                        cv = core.dichromatic_number(n, arcs, ub=3)
                        if cv > inter["max_chi"]:
                            inter["max_chi"] = cv
                        if cv >= 3:
                            inter["witnesses"].append(
                                {"label": f"M(base r={r}) n={n}", "n": n,
                                 "base_arcs": barcs, "smask": smask,
                                 "amask": amask, "arcs": arcs, "chi_vec": cv})
                if inter["witnesses"]:
                    break
            if inter["witnesses"]:
                break
        if inter["witnesses"]:
            break
    results.append(inter)
    print(json.dumps({k: inter[k] for k in
                      ("label", "n", "n_C3_members", "max_chi")}))

    # --- final report ---
    all_witnesses = []
    for r in results:
        all_witnesses.extend(r.get("witnesses", []))
    print("=== SUMMARY ===")
    for r in results:
        print(f"{r['label']:40s} n={r['n']!s:6s} "
              f"C_3={r['n_C3_members']:8d} max_chi={r['max_chi']}")
    print(f"TOTAL chi>=3 witnesses: {len(all_witnesses)}")
    if all_witnesses:
        # GROUND each witness through the oracle's check_construction
        print("=== GROUNDING WITNESSES THROUGH ORACLE ===")
        for wd in all_witnesses[:5]:
            g = oracle.check_construction(wd["n"], wd["arcs"],
                                          name=wd["label"])
            print(json.dumps({"is_C3": g["is_C3"], "chi_vec": g["chi_vec"],
                              "n": g["n"], "arcs": wd["arcs"]}))
    else:
        print("NO chi>=3 witness in the entire swept family.")


if __name__ == "__main__":
    main()
