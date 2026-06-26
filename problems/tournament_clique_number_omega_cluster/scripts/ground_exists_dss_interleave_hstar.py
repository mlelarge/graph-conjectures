"""next_action lever (1)(b): EXISTS-DSS + lag-interleave / H25 split-sum FEASIBILITY
check on the THREE proven-value inner-ov=4 objects H1* / H2* / QR_19.

The H22 kill closed every STATIC merge rule.  The surviving VALUE-leg form (H25)
is the per-H EXISTENTIAL selection:  does H (with ov(H)=k>=3) admit inner orders
(possibly per-copy distinct) + an interleave of the 3 copies whose ALL THREE
cyclic-pair SPLIT-SUMS are <= k+1 ?  By the H25 split-sum identity the merged
backedge clique EQUALS the max of those three pair split-sums, so:

   gold merged clique = ov+1 = 5   <=>   all 3 pair split-sums <= 5.

This was VERIFIED at k=3 generically (ground_dss_interleave_k3) but NEVER run on
the inner-ov=4 proven objects.  Here we run it on H1*/H2* (and QR_19 for the
cross-copy contrast), computing for the GOLD merged order (clique 5, PROVEN):

  * the three cyclic-pair split-sums  s_(1,0), s_(2,1), s_(0,2)
  * whether all <= 5  (EXISTS-reading holds on this object)
  * per copy: is the inner order in the merged order itself a DSS(5) OPTIMAL
    inner order, i.e. omega_be(inner)=4 AND max_p[omega_be(prefix)+omega_be(suffix)]<=5?
  * the uniform-structure verdict across all three (does the EXISTS-reading hold
    uniformly, and is the per-copy DSS-optimality + lag structure the same shape?)

Self-grounding: re-running recomputes from raw circulant defs + the stored G59
SAT witness, via the H22 discriminator's own recovery routines and the H25
split-sum formula (ground_twocopy_identity.split_sum_formula).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
from lexlib import AC, is_tournament  # noqa: E402
from ground_h22_merge_discriminator import (  # noqa: E402
    analyze_hstar, analyze_qr19, H1, H2, QR19, inner_dprofile,
)
from ground_twocopy_identity import (  # noqa: E402
    lex_c3, split_sum_formula, omega_be_subset, copy_of,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

C3_ARCS = [(0, 1), (1, 2), (2, 0)]
PAIRS = [(1, 0), (2, 1), (0, 2)]  # cyclic copy-pairs (Y,X) with cross backedge X before Y


def pair_split_sums(nC, arcsC, beats, merged_order, nH):
    """Return {(Y,X): max_p[omega_be(Y-prefix<p)+omega_be(X-suffix>=p)]} for the
    three cyclic pairs, plus the global max (= H25 split-sum formula value)."""
    pos_index = {v: i for i, v in enumerate(merged_order)}
    out = {}
    for (Y, X) in PAIRS:
        Ypos = [v for v in merged_order if copy_of(v, nH) == Y]
        Xpos = [v for v in merged_order if copy_of(v, nH) == X]
        best = 0
        for p in range(nC + 1):
            left = [v for v in Ypos if pos_index[v] < p]
            right = [v for v in Xpos if pos_index[v] >= p]
            wl = omega_be_subset(beats, left)
            wr = omega_be_subset(beats, right)
            if wl + wr > best:
                best = wl + wr
        out[(Y, X)] = best
    return out


def dss_optimal_inner(nH, arcsH, inner_order, k):
    """Is `inner_order` a DSS(k+1) OPTIMAL inner order?
    optimal: omega_be(inner_order)=k ; DSS(k+1): max disjoint-split sum <= k+1."""
    beatsH = core.beats_matrix(nH, arcsH)
    full = omega_be_subset(beatsH, inner_order)
    m = len(inner_order)
    split = 0
    for t in range(m + 1):
        s = (omega_be_subset(beatsH, inner_order[:t])
             + omega_be_subset(beatsH, inner_order[t:]))
        split = max(split, s)
    return {"inner_clique": full, "optimal": full == k,
            "split_sum": split, "dss_ok": split <= k + 1}


def analyze(name, obj, nH, arcsH, merged_order, k=4):
    nC, arcsC = lex_c3(nH, arcsH)
    beats = core.beats_matrix(nC, arcsC)
    direct = core.omega_of_order(nC, arcsC, merged_order)
    pss = pair_split_sums(nC, arcsC, beats, merged_order, nH)
    formula = max(pss.values())
    # per-copy inner orders as they appear in the merged order
    per_copy = {0: [], 1: [], 2: []}
    for f in merged_order:
        per_copy[f // nH].append(f % nH)
    dss = {c: dss_optimal_inner(nH, arcsH, per_copy[c], k) for c in range(3)}
    all_pairs_ok = all(v <= k + 1 for v in pss.values())
    return {
        "name": name, "nH": nH, "order": nC, "k_inner": k, "target": k + 1,
        "gold_merged_clique_core_verified": direct,
        "split_sum_formula": formula,
        "formula_eq_direct": formula == direct,
        "pair_split_sums": {f"{Y}<{X}": v for (Y, X), v in pss.items()},
        "all_three_pairs_le_target": all_pairs_ok,
        "per_copy_inner_orders": per_copy,
        "per_copy_dss": dss,
        "uses_single_inner_order": (per_copy[0] == per_copy[1] == per_copy[2]),
        "all_copies_dss_optimal": all(dss[c]["dss_ok"] and dss[c]["optimal"]
                                      for c in range(3)),
    }


def main():
    objs = []

    # H1*, H2*: gold = H21 potential-sum merged order (re-derived via attack_class)
    for name, g in [("H1star", H1), ("H2star", H2)]:
        nH, arcsH = AC(25, g)
        assert is_tournament(nH, arcsH)
        rec = analyze_hstar(name, g)
        assert rec["pass"], f"{name}: no gold order"
        # reconstruct the merged order from the recovered signature
        # analyze_hstar stores per_copy_inner + copy_signature; rebuild flat order
        sig = rec["signature"]
        copy_sig = sig["copy_signature"]
        per_copy = rec["per_copy_inner"]
        ptr = {0: 0, 1: 0, 2: 0}
        merged = []
        for c in copy_sig:
            v = per_copy[c][ptr[c]]
            ptr[c] += 1
            merged.append(c * nH + v)
        objs.append(analyze(name, rec, nH, arcsH, merged, k=4))

    # QR_19: gold = G59 SAT-recovered interleaved witness
    d = json.load(open(os.path.join(DATA, "ground_h21_skeleton_sat.json")))
    nH = 19
    mo = d["witness_order"]
    nH2, arcsH = AC(19, QR19)
    assert nH2 == nH and is_tournament(nH, arcsH)
    objs.append(analyze("QR_19", None, nH, arcsH, mo, k=4))

    # uniform-structure verdict across all three
    all_exists_ok = all(o["all_three_pairs_le_target"] for o in objs)
    all_formula_ok = all(o["formula_eq_direct"] for o in objs)
    all_clique5 = all(o["gold_merged_clique_core_verified"] == 5 for o in objs)
    single_inner = {o["name"]: o["uses_single_inner_order"] for o in objs}
    dss_uniform = {o["name"]: o["all_copies_dss_optimal"] for o in objs}

    result = {
        "leg": "exists_dss_interleave_hstar",
        "claim_form": "structural",
        "k_inner": 4, "target_split_sum": 5,
        "objects": objs,
        "EXISTS_reading_holds_on_all_three": all_exists_ok,
        "split_sum_formula_matches_direct_all": all_formula_ok,
        "all_gold_merged_clique_eq_5": all_clique5,
        "uses_single_inner_order": single_inner,
        "per_copy_dss_optimal_uniform": dss_uniform,
        "uniform_structure": (
            len(set(tuple(sorted(single_inner.values())))) == 1
            and len(set(tuple(sorted(dss_uniform.values())))) == 1
        ),
        "verdict": None,
    }
    if all_exists_ok and all_clique5:
        if all(single_inner.values()) == all(single_inner.values()):
            pass
        same_single = len(set(single_inner.values())) == 1
        same_dss = len(set(dss_uniform.values())) == 1
        if same_single and same_dss:
            result["verdict"] = ("EXISTS-reading UNIFORM: all 3 pair split-sums <= 5 on "
                                 "all three, with the SAME per-copy structure.")
        else:
            result["verdict"] = ("EXISTS-reading HOLDS on all three (all pair split-sums "
                                 "<= 5) but the per-copy STRUCTURE is NON-UNIFORM "
                                 f"(single_inner={single_inner}, dss_optimal={dss_uniform}): "
                                 "no uniform per-copy-DSS lag-interleave shape -> the VALUE "
                                 "leg needs a per-H dynamic selection, not a uniform recipe.")
    else:
        result["verdict"] = ("EXISTS-reading FAILS on some object (a pair split-sum > 5): "
                             f"{[(o['name'], o['pair_split_sums']) for o in objs]}")

    out = os.path.join(DATA, "ground_exists_dss_interleave_hstar.json")
    with open(out, "w") as fh:
        json.dump(result, fh, indent=2, default=int)
    # console summary
    for o in objs:
        print(f"{o['name']:8s} order={o['order']} gold_clique="
              f"{o['gold_merged_clique_core_verified']} formula={o['split_sum_formula']} "
              f"pair_split_sums={o['pair_split_sums']} all<=5={o['all_three_pairs_le_target']} "
              f"single_inner={o['uses_single_inner_order']} "
              f"all_dss_opt={o['all_copies_dss_optimal']}")
    print("EXISTS_reading_holds_on_all_three:", all_exists_ok)
    print("split_sum_formula_matches_direct_all:", all_formula_ok)
    print("all_gold_merged_clique_eq_5:", all_clique5)
    print("uses_single_inner_order:", single_inner)
    print("per_copy_dss_optimal_uniform:", dss_uniform)
    print("uniform_structure:", result["uniform_structure"])
    print("VERDICT:", result["verdict"])
    print("WROTE", out)


if __name__ == "__main__":
    main()
