"""RED-TEAM the Mader directed-splitting-off / minimal-degree backbone of the
proposed PINCHING GENERATOR against the existing oracle ground truth: the
complete 116-member iso-census of decrement-minimal (n=4, M<=3) lambda>=3
multidigraphs (scripts/minimal_census_n4_m3.py).

The proposed n=5 census generator rests on the multidigraph form of two Mader
theorems.  This script tests the THREE falsifiable predictions of that backbone
on the 116-instance ground truth WITHOUT building anything at n=5:

 (a) every decrement-minimal instance has a BALANCED vertex v with
     d+(v) = d-(v) = 3 (= k).  [needed: a complete splitting site exists]
 (b) Mader degree counts: >= k+1 = 4 vertices of out-degree EXACTLY 3 AND
     >= 4 of in-degree EXACTLY 3.  At n=4 this forces ALL FOUR vertices to be
     (3,3)-balanced -- i.e. every minimal is a 3-regular (3,3) multidigraph.
 (c) at least one COMPLETE splitting-off at some balanced v (one of the 3!=6
     in/out arc pairings) yields an n=3 multidigraph with exact lambda >= 3.

KILL (any one): a minimal with no balanced (3,3) vertex; or fewer than 4
out-deg-3 (or in-deg-3) vertices; or where ALL pairings at ALL balanced
vertices drop lambda below 3.  Any of these refutes the multidigraph form of
the Mader backbone and closes the pinching-generator route.

Reuses the CHECKED-IN census logic (run_census, canonical, ARCS, etc.) from
minimal_census_n4_m3 -- does NOT re-derive minimality.  Cross-checks exact
lambda on randomly chosen instances and split images against the oracle.
"""
from __future__ import annotations

import json
import os
import sys
import time
from itertools import permutations

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import oracle  # noqa: E402
import minimal_census_n4_m3 as mc  # noqa: E402

N = mc.N      # 4
M = mc.M      # 3
LAM = mc.LAM  # 3
ARCS = mc.ARCS


def degree_profile(vec):
    """Return (outdeg, indeg) length-N arrays of multiplicity-weighted degrees."""
    outd = np.zeros(N, dtype=np.int64)
    ind = np.zeros(N, dtype=np.int64)
    for (u, v), k in zip(ARCS, vec):
        outd[u] += int(k)
        ind[v] += int(k)
    return outd, ind


def lam_general(n, arclist):
    """Exact lambda^arc on a multidigraph given as an explicit arc list (with
    repeats) on n vertices, by direct min-out-cut over all 2^n-2 proper subsets.
    Multiplicity-aware (each listed arc counts 1)."""
    best = None
    for mask in range(1, (1 << n) - 1):
        cut = 0
        for (u, v) in arclist:
            if (mask >> u) & 1 and not ((mask >> v) & 1):
                cut += 1
        if best is None or cut < best:
            best = cut
    return best


def expand(vec):
    arcs = []
    for (u, v), k in zip(ARCS, vec):
        arcs += [(u, v)] * int(k)
    return arcs


def complete_splittings_at(vec, w):
    """Enumerate all complete splittings-off at balanced vertex w (d+=d-=3).

    A complete splitting pairs each ENTERING arc (x,w) with a LEAVING arc (w,y)
    and replaces the pair by a new arc (x,y); w is then deleted.  With d-(w)=
    d+(w)=3 there are 3! = 6 pairings (matchings between the in-arc list and the
    out-arc list, multiplicity-respecting).  Yields, for each pairing, the
    resulting (n-1=3)-vertex multidigraph as an explicit arc list on the
    relabelled vertex set V \\ {w} -> {0,1,2}.

    Returns list of (pairing_repr, arclist_on_3, lambda3)."""
    # entering arcs (tails, with multiplicity) and leaving arcs (heads)
    tails = []  # x for each entering arc (x,w)
    heads = []  # y for each leaving arc (w,y)
    base_arcs = []  # arcs not touching w
    for (u, v), k in zip(ARCS, vec):
        if v == w and u != w:
            tails += [u] * int(k)
        elif u == w and v != w:
            heads += [v] * int(k)
        elif u != w and v != w:
            base_arcs += [(u, v)] * int(k)
    assert len(tails) == 3 and len(heads) == 3, (tails, heads)

    # relabel V\{w} -> 0..2
    others = [x for x in range(N) if x != w]
    relabel = {x: i for i, x in enumerate(others)}

    results = []
    seen = set()
    # all 6 matchings of the 3 heads to the 3 tail-slots
    for perm in permutations(range(3)):
        new_arcs = []
        for i in range(3):
            x = tails[i]
            y = heads[perm[i]]
            new_arcs.append((relabel[x], relabel[y]))  # split arc (x,y)
        full = [(relabel[u], relabel[v]) for (u, v) in base_arcs] + new_arcs
        key = tuple(sorted(full))
        lam3 = lam_general(3, full)
        results.append({
            "pairing": [(tails[i], heads[perm[i]]) for i in range(3)],
            "arclist3": full,
            "lambda3": lam3,
        })
        seen.add(key)
    return results


def main():
    t0 = time.time()
    rng = np.random.default_rng(20260612)

    # --- regenerate the 116 iso-distinct decrement-minimal instances --------
    n_lam_ge, minimals = mc.run_census()
    canon = set()
    for v in minimals:
        canon.add(mc.canonical(v))
    iso = sorted(canon)
    n_iso = len(iso)
    assert n_iso == 116, ("EXPECTED 116 iso-distinct minimals", n_iso)

    # --- per-instance Mader-backbone tests ----------------------------------
    n_no_balanced = 0          # KILL (a): no (3,3) vertex
    n_degcount_fail = 0        # KILL (b): <4 outdeg-3 or <4 indeg-3
    n_all_pairings_drop = 0    # KILL (c): every pairing at every balanced v < 3
    min_outdeg3 = N
    min_indeg3 = N
    fails = []
    per_instance = []

    for v in iso:
        outd, ind = degree_profile(v)
        balanced = [x for x in range(N) if outd[x] == 3 and ind[x] == 3]
        n_out3 = int((outd == 3).sum())
        n_in3 = int((ind == 3).sum())
        min_outdeg3 = min(min_outdeg3, n_out3)
        min_indeg3 = min(min_indeg3, n_in3)

        rec = {
            "mu": list(v),
            "outdeg": outd.tolist(),
            "indeg": ind.tolist(),
            "n_outdeg3": n_out3,
            "n_indeg3": n_in3,
            "balanced_vertices": balanced,
        }

        if not balanced:
            n_no_balanced += 1
            rec["KILL_a_no_balanced"] = True
            fails.append(rec)
            per_instance.append(rec)
            continue

        if n_out3 < 4 or n_in3 < 4:
            n_degcount_fail += 1
            rec["KILL_b_degcount"] = True

        # (c): does SOME complete splitting at SOME balanced v keep lambda>=3?
        good_split = None
        any_ge3 = False
        for w in balanced:
            for s in complete_splittings_at(v, w):
                if s["lambda3"] >= LAM:
                    any_ge3 = True
                    if good_split is None:
                        good_split = {"w": w, **s}
                    break
            if any_ge3:
                break
        rec["some_split_keeps_lambda3"] = any_ge3
        if good_split is not None:
            rec["witness_split"] = good_split
        if not any_ge3:
            n_all_pairings_drop += 1
            rec["KILL_c_all_drop"] = True
            fails.append(rec)
        elif rec.get("KILL_b_degcount"):
            fails.append(rec)

        per_instance.append(rec)

    # --- oracle cross-checks: exact lambda on random instances + split images
    cross = {"instance_lambda": [], "split_lambda": []}
    sample_idx = rng.choice(n_iso, size=5, replace=False)
    for ix in sample_idx:
        v = iso[int(ix)]
        arcs = expand(v)
        lam_oracle = oracle.arc_connectivity(N, arcs)
        lam_vec = mc.lam_of(v)
        cross["instance_lambda"].append({
            "mu": list(v), "lambda_oracle": lam_oracle,
            "lambda_vectorized": lam_vec, "agree": lam_oracle == lam_vec,
        })
    # 5 split images: take first 5 instances with a witness split, oracle-check
    got = 0
    for rec in per_instance:
        if got >= 5:
            break
        ws = rec.get("witness_split")
        if ws is None:
            continue
        arclist3 = ws["arclist3"]
        lam_oracle3 = oracle.arc_connectivity(3, arclist3)
        cross["split_lambda"].append({
            "w": ws["w"], "lambda_oracle": lam_oracle3,
            "lambda_direct": ws["lambda3"],
            "agree": lam_oracle3 == ws["lambda3"],
        })
        got += 1

    cross_all_agree = all(
        e["agree"] for e in cross["instance_lambda"]
    ) and all(e["agree"] for e in cross["split_lambda"])

    out = {
        "elapsed_s": round(time.time() - t0, 1),
        "n_iso_distinct": n_iso,
        "PREDICTION_a_all_have_balanced_33_vertex": n_no_balanced == 0,
        "PREDICTION_b_all_four_vertices_3_3": (min_outdeg3 == 4 and min_indeg3 == 4),
        "PREDICTION_c_some_split_keeps_lambda3": n_all_pairings_drop == 0,
        "counts": {
            "n_no_balanced_vertex_KILL_a": n_no_balanced,
            "n_degcount_below_4_KILL_b": n_degcount_fail,
            "n_all_pairings_drop_KILL_c": n_all_pairings_drop,
            "min_n_outdeg3_over_instances": min_outdeg3,
            "min_n_indeg3_over_instances": min_indeg3,
        },
        "oracle_cross_check": cross,
        "oracle_cross_check_all_agree": cross_all_agree,
        "BACKBONE_HOLDS": (n_no_balanced == 0 and n_all_pairings_drop == 0
                           and cross_all_agree),
        "n_fail_records": len(fails),
        "fail_records_sample": fails[:20],
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
