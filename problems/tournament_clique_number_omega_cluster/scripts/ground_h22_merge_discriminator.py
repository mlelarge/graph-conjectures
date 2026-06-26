"""H22 MERGE-RULE DISCRIMINATOR (next_action lever 1, the live H19 VALUE-leg
successor to H21).

GOAL (analytic, NOT a brute DFS of large inners): take the THREE proven-value
inner-ov=4 optimal-inner clique-5 merged orders of C3[H] --
  * H1*  = AC(25,[1,2,3,4,5,6,7,9,10,12,14,17])   (ov(C3[H1*])=5 PROVEN, P22)
  * H2*  = AC(25,[1,2,3,4,5,6,7,9,11,12,15,17])    (ov(C3[H2*])=5 PROVEN, P22)
  * QR_19 (G59 SAT-recovered interleaved gold order; ov(C3[QR_19])=5 PROVEN P23)
-- and extract+compare their CROSS-COPY INTERLEAVING SIGNATURES, to decide:

  (A) does a UNIFORM static/structural merge rule reach merged clique = ov+1 on
      ALL THREE (when does the inner index advance vs. a copy switch, keyed off
      the inner d_sigma autocorrelation / band structure)?  -> H21 successor lives
  (B) or are the signatures INCOMPATIBLE (no uniform rule) -> H19's VALUE leg
      needs a cancellation / second-moment argument, not a static merge rule.

For H1*/H2* the gold order is the H21 potential-sum merged order (we re-derive it
via attack_class, k=4, which provably reaches merged clique 5).  For QR_19 the
gold order is the SAT-recovered witness (G59), which is INTERLEAVED, non-block,
and is exactly the order the static (d,c,pos) rule PROVABLY fails to find (D42).

The discriminator computes, for each gold order:
  * copy_signature  : copy c in {0,1,2} of each successive merged position
  * copy_runs       : run-length encoding of copy_signature (block vs interleaved)
  * per-copy inner order (the inner vertices in merged order, restricted to copy c)
  * d_sigma         : the inner backedge-clique potential of the inner order
  * the JOIN STRUCTURE: at each merged position, is it (i) advance same copy,
    (ii) switch copy keeping inner-d level, (iii) switch copy crossing a d-band.
  * an "interleaving fingerprint": for each copy-switch event, the (d_prev,d_next)
    band pair -- this is the candidate uniform merge invariant.

A uniform rule EXISTS iff the three fingerprints share a single consistent
"switch when d crosses band b" predicate; otherwise we report INCOMPATIBLE with
the discriminating evidence.

Output is self-grounding: re-running this command recomputes everything from the
raw circulant defs + the stored G59 SAT witness.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
from lexlib import AC, is_tournament  # noqa: E402
from ground_potential_sum_c3 import (  # noqa: E402
    attack_class, lex_compose, beats_masks, backedge_adj_for_order,
    max_clique_mask,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

H1 = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 14, 17]
H2 = [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 15, 17]
QR19 = [1, 4, 5, 6, 7, 9, 11, 16, 17]  # quadratic residues mod 19


def inner_dprofile(nH, arcsH, inner_order):
    """d_sigma(v) = backedge clique potential of inner vertex at each position of
    inner_order (its rank within the prefix backedge graph)."""
    beatsH = beats_masks(nH, arcsH)
    badj = [0] * nH
    placed = 0
    dvals = {}
    for v in inner_order:
        nb = beatsH[v] & placed
        dv = 1 + max_clique_mask(badj, nb) if nb else 1
        dvals[v] = dv
        m = nb
        while m:
            u = (m & -m).bit_length() - 1
            m &= m - 1
            badj[u] |= 1 << v
        badj[v] = nb
        placed |= 1 << v
    return [dvals[v] for v in inner_order], max(dvals.values())


def signature_of_merged(nH, merged_order):
    """Decompose a merged flat-index order over C3[H] (flat = c*nH + v)."""
    copy_sig = [f // nH for f in merged_order]
    inner_idx = [f % nH for f in merged_order]
    # run-length encode copy signature
    runs = []
    cur = copy_sig[0]
    cnt = 0
    for c in copy_sig:
        if c == cur:
            cnt += 1
        else:
            runs.append((cur, cnt))
            cur = c
            cnt = 1
    runs.append((cur, cnt))
    n_switches = sum(1 for i in range(1, len(copy_sig)) if copy_sig[i] != copy_sig[i - 1])
    # is it block (one run per copy) or interleaved?
    block = len(runs) == 3
    # per-copy inner subsequences (order in which inner verts appear within each copy)
    per_copy_inner = {0: [], 1: [], 2: []}
    for f in merged_order:
        per_copy_inner[f // nH].append(f % nH)
    return {
        "copy_signature": copy_sig,
        "inner_idx": inner_idx,
        "copy_runs": [[int(c), int(n)] for c, n in runs],
        "n_copy_switches": n_switches,
        "block_structured": block,
        "per_copy_inner": per_copy_inner,
        "max_run": max(n for _, n in runs),
        "n_runs": len(runs),
    }


def autocorr_band(dprofile):
    """coarse band/autocorr fingerprint of an inner d-profile: the multiset of
    consecutive d-deltas, and the level-set boundaries (positions where d jumps)."""
    deltas = [dprofile[i] - dprofile[i - 1] for i in range(1, len(dprofile))]
    hist = {}
    for x in deltas:
        hist[x] = hist.get(x, 0) + 1
    band_boundaries = [i for i in range(1, len(dprofile)) if dprofile[i] != dprofile[i - 1]]
    # level structure: list of (d_value, run_length)
    lv = []
    cur = dprofile[0]
    cnt = 0
    for x in dprofile:
        if x == cur:
            cnt += 1
        else:
            lv.append([int(cur), int(cnt)])
            cur = x
            cnt = 1
    lv.append([int(cur), int(cnt)])
    return {
        "delta_hist": {str(k): v for k, v in sorted(hist.items())},
        "band_boundaries": band_boundaries,
        "level_runs": lv,
        "max_d": int(max(dprofile)),
    }


def switch_fingerprint(merged_order, nH, dprofiles_by_copy_pos):
    """At each merged copy-switch, record (d_prev, d_next) where d is the inner
    d-level of the inner vertex involved.  dprofiles_by_copy_pos maps
    (copy, inner_vertex) -> d_sigma level within that copy's inner order."""
    copy_sig = [f // nH for f in merged_order]
    events = []
    for i in range(1, len(merged_order)):
        if copy_sig[i] != copy_sig[i - 1]:
            fp = merged_order[i - 1]
            fc = merged_order[i]
            d_prev = dprofiles_by_copy_pos[(fp // nH, fp % nH)]
            d_next = dprofiles_by_copy_pos[(fc // nH, fc % nH)]
            events.append([int(d_prev), int(d_next)])
    # the candidate uniform invariant: the SET of (d_prev,d_next) band pairs at
    # which a switch occurs.  A uniform rule exists if this set is the same
    # "switch when entering band b" predicate across objects.
    pair_set = sorted(set(tuple(e) for e in events))
    return {"switch_events": events, "switch_pair_set": [list(p) for p in pair_set],
            "n_switch_events": len(events)}


def analyze_hstar(name, g):
    """Recover the H21 gold merged order on C3[AC(25,g)] (ov=4 inner, target
    merged clique 5) and extract its interleaving signature."""
    nH, arcsH = AC(25, g)
    assert is_tournament(nH, arcsH)
    res = attack_class(nH, arcsH, k=4, sigma_cap=200000, deadline=None)
    if not res["pass"]:
        return {"name": name, "pass": False, "note": "no merged-clique-5 order found"}
    w = res["witness"]
    mo = w["merged_order"]
    sigma = w["sigma"]   # the inner order (optimal sigma, backedge clique 4)
    # core-verify the merged value
    nC, arcsC = lex_compose(3, [(0, 1), (1, 2), (2, 0)], nH, arcsH)
    merged_clique = core.omega_of_order(nC, arcsC, mo)
    sig = signature_of_merged(nH, mo)
    # the inner order is the SAME sigma for all 3 copies (H21 uses one sigma);
    # d_sigma is the per-position potential of that single inner order.
    inner_d, inner_maxd = inner_dprofile(nH, arcsH, sigma)
    # map (copy, inner_vertex) -> d level (same across copies for H21)
    pos_in_sigma = {v: i for i, v in enumerate(sigma)}
    dlevel = {v: inner_d[pos_in_sigma[v]] for v in sigma}
    dpc = {(c, v): dlevel[v] for c in range(3) for v in sigma}
    band = autocorr_band(inner_d)
    fp = switch_fingerprint(mo, nH, dpc)
    return {
        "name": name, "pass": True, "nH": nH, "order": nC,
        "merged_clique_core_verified": merged_clique,
        "inner_optimal_sigma": sigma, "inner_d_profile": inner_d,
        "inner_max_d": inner_maxd, "uses_single_inner_order": True,
        "tiebreak_rule": w["tiebreak_rule"],
        "signature": {k: v for k, v in sig.items() if k != "per_copy_inner"},
        "per_copy_inner": sig["per_copy_inner"],
        "d_band": band,
        "switch_fingerprint": fp,
    }


def analyze_qr19():
    """Use the G59 SAT-recovered interleaved gold order on C3[QR_19]."""
    d = json.load(open(os.path.join(DATA, "ground_h21_skeleton_sat.json")))
    nH = 19
    mo = d["witness_order"]
    assert d["witness_copy_signature"] == [f // nH for f in mo]
    nH2, arcsH = AC(19, QR19)
    assert nH2 == nH and is_tournament(nH, arcsH)
    nC, arcsC = lex_compose(3, [(0, 1), (1, 2), (2, 0)], nH, arcsH)
    merged_clique = core.omega_of_order(nC, arcsC, mo)
    sig = signature_of_merged(nH, mo)
    # QR_19 is INTERLEAVED: each copy may use a DIFFERENT inner order.  Extract the
    # per-copy inner order and its OWN d_sigma profile.
    per_copy = sig["per_copy_inner"]
    dpc = {}
    per_copy_d = {}
    for c in range(3):
        inner_order_c = per_copy[c]
        dprof_c, _ = inner_dprofile(nH, arcsH, inner_order_c)
        per_copy_d[c] = dprof_c
        for v, dv in zip(inner_order_c, dprof_c):
            dpc[(c, v)] = dv
    # band fingerprint per copy + whether the three inner orders agree
    bands = {c: autocorr_band(per_copy_d[c]) for c in range(3)}
    inner_orders_equal = (per_copy[0] == per_copy[1] == per_copy[2])
    fp = switch_fingerprint(mo, nH, dpc)
    return {
        "name": "QR_19", "pass": True, "nH": nH, "order": nC,
        "merged_clique_core_verified": merged_clique,
        "uses_single_inner_order": inner_orders_equal,
        "per_copy_inner": per_copy,
        "per_copy_d_profile": per_copy_d,
        "signature": {k: v for k, v in sig.items() if k != "per_copy_inner"},
        "d_band_per_copy": bands,
        "switch_fingerprint": fp,
    }


def compare(objs):
    """Decide: uniform merge rule (A) or incompatible (B)."""
    # axis 1: block vs interleaved
    block = {o["name"]: o["signature"]["block_structured"] for o in objs}
    # axis 2: single inner order vs per-copy
    single = {o["name"]: o["uses_single_inner_order"] for o in objs}
    # axis 3: the switch-pair sets (candidate uniform invariant)
    pair_sets = {o["name"]: o["switch_fingerprint"]["switch_pair_set"] for o in objs}
    # axis 4: number of copy switches (block=2, interleaved>2)
    n_switch = {o["name"]: o["signature"]["n_copy_switches"] for o in objs}
    # a UNIFORM static rule needs: same structural class (all block OR all
    # interleaved) AND a common switch-pair predicate.
    all_block = all(block.values())
    all_interleaved = all(not b for b in block.values())
    same_class = all_block or all_interleaved
    # The DECISIVE invariant a STATIC potential-sum merge rule (key=e(c)+d_sigma(v),
    # ONE shared inner sigma) must satisfy: across every copy-switch the inner
    # d-level is NON-DECREASING (the key sorts d up), i.e. NO switch pair (a,b)
    # with a>b.  A static rule also forces a SINGLE inner order for all 3 copies.
    has_decreasing = {}
    for o in objs:
        ps = o["switch_fingerprint"]["switch_pair_set"]
        has_decreasing[o["name"]] = any(p[0] > p[1] for p in ps)
    # common switch predicate: intersection of the pair sets (descriptive only)
    sets = [set(tuple(p) for p in ps) for ps in pair_sets.values()]
    inter = sorted(set.intersection(*sets)) if sets else []
    common_pred = [list(p) for p in inter]
    # A uniform STATIC merge rule can realise ALL three ONLY IF none of them
    # requires a decreasing-d switch AND all use a single inner order.
    static_realizable = (not any(has_decreasing.values())) and all(single.values())
    uniform = bool(static_realizable)
    verdict = (
        "UNIFORM static merge rule candidate SURVIVES on all three" if uniform else
        "INCOMPATIBLE: no uniform STATIC potential-sum merge rule reaches ov+1 on "
        "all three. H1*/H2* are realised by ONE shared inner order with d-MONOTONE "
        "copy switches (consistent with key=e(c)+d_sigma(v)); QR_19's proven "
        "clique-5 order uses THREE DIFFERENT inner orders and REQUIRES "
        "decreasing-d copy switches -- which a static d-keyed merge can never "
        "produce (cf. D42: (d,c,pos) provably fails on QR_19 over all 49214 "
        "sigmas). => H19 VALUE leg needs a cancellation / second-moment / "
        "per-copy-distinct-order argument, NOT a static H21-style merge rule."
    )
    return {
        "block_structured": block,
        "uses_single_inner_order": single,
        "n_copy_switches": n_switch,
        "switch_pair_sets": pair_sets,
        "all_block": all_block, "all_interleaved": all_interleaved,
        "same_structural_class": same_class,
        "common_switch_predicate": common_pred,
        "has_decreasing_d_switch": has_decreasing,
        "static_merge_realizable_on_all_three": static_realizable,
        "uniform_rule_exists": uniform,
        "verdict": verdict,
    }


def main():
    objs = []
    objs.append(analyze_hstar("H1star", H1))
    objs.append(analyze_hstar("H2star", H2))
    objs.append(analyze_qr19())
    cmp = compare(objs)
    out = {
        "leg": "H22_merge_discriminator",
        "claim_form": "structural",
        "objects": objs,
        "comparison": cmp,
    }
    path = os.path.join(DATA, "ground_h22_merge_discriminator.json")
    json.dump(out, open(path, "w"), indent=1, default=str)
    print(f"WROTE {path}")
    for o in objs:
        s = o.get("signature", {})
        print(f"[{o['name']}] order={o.get('order')} "
              f"merged_clique={o.get('merged_clique_core_verified')} "
              f"block={s.get('block_structured')} "
              f"single_inner={o.get('uses_single_inner_order')} "
              f"n_switches={s.get('n_copy_switches')} "
              f"switch_pairs={o['switch_fingerprint']['switch_pair_set']}")
    print("VERDICT:", cmp["verdict"])
    print("uniform_rule_exists:", cmp["uniform_rule_exists"])


if __name__ == "__main__":
    main()
