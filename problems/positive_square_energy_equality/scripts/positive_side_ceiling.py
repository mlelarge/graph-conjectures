"""Positive-side dual of Lemma B1 (Lemma B1+).

For a 2-tree G with simplicial degree-2 ear v, supporting edge {a,b} in
E(H), H = G - v, w = e_a + e_b in R^{n-1}, c_i = w^T u_i, set

    W^+ := sum_{mu_i > 0} c_i^2,
    M_1^+ := sum_{mu_i > 0} c_i^2 mu_i  (>= 0).

Lemma B1+ (this module proves):
    lambda_max(A(G)) >= f_max^+
    f_max^+ := (M_1^+ + sqrt((M_1^+)^2 + 4 (W^+)^3)) / (2 W^+),    when W^+ > 0.

Derivation: trial vector z_+(beta) = tilde w_+ + beta e_v with
w_+ := sum_{mu_i > 0} c_i u_i, projection of w onto H's positive
eigenspace. Then
    ||z_+(beta)||^2 = W^+ + beta^2,
    z_+(beta)^T A(G) z_+(beta) = M_1^+ + 2 beta W^+.
Maximising R_+(beta) = (M_1^+ + 2 beta W^+) / (beta^2 + W^+) gives the
positive critical point beta_+^* = (-M_1^+ + sqrt((M_1^+)^2 + 4 (W^+)^3))
/ (2 W^+) and the maximum value f_max^+ above.

By Courant-Fischer, lambda_max(A(G)) >= R_+(beta_+^*) = f_max^+.

This script:
  (1) computes f_max^+ for each max-degsum simplicial degree-2 ear of
      every 2-tree in the same corpus used by case_AB_census.py;
  (2) records the trace-identity-induced ceiling delta^+ = 4 - delta^-
      (on degree-2 ears, since tr(A(G)^2) - tr(A(H)^2) = 2 deg_G(v) = 4);
  (3) emits data/positive_side_ceiling_census.json with columns
      {graph6, n, v, case, W_plus, M1_plus, M2_plus, f_max_plus,
       f_max_plus_sq, lambda_max_G, alpha_plus_min, alpha_plus_min_sq,
       alpha_plus_top, alpha_plus_top_sq, delta_plus, delta_minus,
       slot_shift_plus_sum, slot_shift_plus_max, n_plus_G, n_plus_H,
       case_plus, family, source, param_n, k, t}.

Reuses case_AB_census.case_AB_record-style data flow.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from joint_invariant_features import ear_records, from_graph6  # noqa: E402
from build_joint_invariant_corpus import (  # noqa: E402
    book_graph, two_path_graph, fan_graph,
)
from extreme_family import book_with_tail  # noqa: E402
from spectrum_check import spectrum  # noqa: E402

DATA = ROOT / "data"
TOL = 1e-9


def f_max_plus(W_plus: float, M1_plus: float) -> float | None:
    """Lemma B1+ explicit lower bound on lambda_max(A(G))."""
    if W_plus <= TOL:
        return None
    disc = M1_plus * M1_plus + 4.0 * W_plus * W_plus * W_plus
    return float((M1_plus + math.sqrt(disc)) / (2.0 * W_plus))


def positive_side_record(G: nx.Graph, max_only: bool = True) -> list[dict]:
    """For each max-degsum (or all) simplicial degree-2 ear of G:

      * compute (W^+, M_1^+, M_2^+) from H;
      * compute Lemma B1+'s explicit lower bound f_max^+ on lambda_max(A(G));
      * record the actual lambda_max(A(G)) and the tightness ratio;
      * compute the Case A/B classification for delta^+ via inertia of G
        and H on the positive side: Case A_+ iff n^+(G) = n^+(H), Case B_+
        iff n^+(G) = n^+(H) + 1;
      * compute the positive-side slot shifts under the convention
        (lambda_i(G), mu_i(H)) i=1..n-1: by Cauchy interlacing
        lambda_i(G) >= mu_i(H) >= lambda_{i+1}(G), so on indices where
        mu_i > 0 (J^+) one has lambda_i^2 - mu_i^2 >= 0 (when both
        positive). Case B_+ contributes an extra alpha_top_plus^2 term
        which is the SMALLEST G-positive eigenvalue
        (alpha_top_plus := lambda_{n^+(H)+1}(G) in the 1-based indexing
         where lambda_1 is the largest);
      * recover delta^+ = trace identity 4 - delta^- as a sanity check.
    """
    base_recs = ear_records(G)
    if max_only:
        base_recs = [r for r in base_recs if r["is_max_degsum"]]
    eigs_G_desc = np.array(sorted(spectrum(G), reverse=True))  # lambda_1 >= ... >= lambda_n
    n_G = len(eigs_G_desc)
    lambda_max_G = float(eigs_G_desc[0])
    lambda_max_G_sq = lambda_max_G * lambda_max_G
    n_plus_G = int(np.sum(eigs_G_desc > TOL))
    n_minus_G = int(np.sum(eigs_G_desc < -TOL))

    out = []
    for r in base_recs:
        v = r["v"]
        H = G.copy()
        H.remove_node(v)
        eigs_H_desc = np.array(sorted(spectrum(H), reverse=True))  # mu_1 >= ... >= mu_{n-1}
        n_H = len(eigs_H_desc)
        n_plus_H = int(np.sum(eigs_H_desc > TOL))
        n_minus_H = int(np.sum(eigs_H_desc < -TOL))

        case_neg = "A" if n_minus_G == n_minus_H else "B"
        case_pos = "A" if n_plus_G == n_plus_H else "B"

        Wp = float(r["W_plus"])
        M1p = float(r["M1_plus"])
        M2p = float(r["M2_plus"])
        fmp = f_max_plus(Wp, M1p)

        # Positive-side slot decomposition. We use the pairing
        # (lambda_i(G), mu_i(H)) for i = 1, ..., n-1, by interlacing
        # lambda_i >= mu_i. For J^+ := {i : mu_i > 0} (1-based, python
        # indices 0..n_plus_H - 1), the slot-shift lambda_i^2 - mu_i^2
        # is >= 0 iff |lambda_i| >= |mu_i|. Since lambda_i >= mu_i and
        # both positive (for i in J^+), this is automatic.
        slot_shifts_plus = []
        for j_one in range(1, n_plus_H + 1):  # 1-based i in J^+ = 1..n_plus_H
            lam = float(eigs_G_desc[j_one - 1])
            mu = float(eigs_H_desc[j_one - 1])
            slot_shifts_plus.append(lam * lam - mu * mu)
        slot_shift_plus_sum = float(sum(slot_shifts_plus))
        slot_shift_plus_max = float(max(slot_shifts_plus)) if slot_shifts_plus else 0.0
        slot_shift_plus_min = float(min(slot_shifts_plus)) if slot_shifts_plus else 0.0

        # In Case B_+ (n_plus_G = n_plus_H + 1), the EXTRA positive
        # eigenvalue of G compared to H sits at position n_plus_H + 1
        # (1-based, descending). That is the SMALLEST G-positive
        # eigenvalue (alpha_top_plus). The decomposition is then
        # delta^+ = alpha_top_plus^2 + sum_{i in J^+(H)}(lambda_i^2 - mu_i^2),
        # mirroring case_AB_census.py for the negative side.
        if case_pos == "B" and n_plus_H + 1 <= n_G:
            alpha_top_plus = float(eigs_G_desc[n_plus_H + 1 - 1])  # = lambda_{n_plus_H+1}(G)
            alpha_top_plus_sq = alpha_top_plus * alpha_top_plus
        else:
            alpha_top_plus = 0.0
            alpha_top_plus_sq = 0.0

        # alpha_plus_min: the SMALLEST positive G-eigenvalue (always
        # positive if G has any positive eigenvalue). This is the
        # quantity bounded *below* by 0 trivially; in Case B_+ it
        # coincides with alpha_top_plus.
        if n_plus_G > 0:
            alpha_plus_min = float(eigs_G_desc[n_plus_G - 1])
            alpha_plus_min_sq = alpha_plus_min * alpha_plus_min
        else:
            alpha_plus_min = 0.0
            alpha_plus_min_sq = 0.0

        # Trace identity: delta^+ = 4 - delta^-, since
        # tr(A(G)^2) - tr(A(H)^2) = 2 deg_G(v) = 4.
        dminus = float(r["delta_minus"])
        dplus = float(r["delta_plus"])
        # Sanity: dplus + dminus == 4
        # (small numerical drift OK).
        # Reconstruction sanity: in Case B_+, delta^+ = alpha_top_plus^2 + slot_sum.
        # In Case A_+, delta^+ = slot_sum (no extra term).
        recon = alpha_top_plus_sq + slot_shift_plus_sum
        ok = abs(recon - dplus) < 1e-6
        rec = {
            "graph6": r["graph6"],
            "n": r["n"],
            "v": v,
            "a": r["a"],
            "b": r["b"],
            "case_neg": case_neg,
            "case_pos": case_pos,
            "n_plus_G": n_plus_G,
            "n_plus_H": n_plus_H,
            "n_minus_G": n_minus_G,
            "n_minus_H": n_minus_H,
            "delta_plus": dplus,
            "delta_minus": dminus,
            "lambda_max_G": lambda_max_G,
            "lambda_max_G_sq": lambda_max_G_sq,
            "W_plus": Wp,
            "M1_plus": M1p,
            "M2_plus": M2p,
            "f_max_plus": fmp,
            "f_max_plus_sq": (fmp * fmp) if fmp is not None else None,
            "alpha_plus_min": alpha_plus_min,
            "alpha_plus_min_sq": alpha_plus_min_sq,
            "alpha_top_plus": alpha_top_plus,
            "alpha_top_plus_sq": alpha_top_plus_sq,
            "slot_shift_plus_sum": slot_shift_plus_sum,
            "slot_shift_plus_max": slot_shift_plus_max,
            "slot_shift_plus_min": slot_shift_plus_min,
            "slot_recon_ok": ok,
            "ratio_lambda_max_over_f_max_plus": (
                (lambda_max_G / fmp) if (fmp is not None and fmp > 0) else None
            ),
            "is_max_degsum": bool(r["is_max_degsum"]),
            "deg_sum_in_H": r["deg_sum"],
            "param_n": r.get("param_n"),
            "k": r.get("k"),
            "t": r.get("t"),
        }
        out.append(rec)
    return out


def build_census():
    records = []

    # 1. Enumerated 2-trees n=4..10
    enum_path = DATA / "two_trees_n10.json"
    enum = json.loads(enum_path.read_text())
    for n_str in ["4", "5", "6", "7", "8", "9", "10"]:
        codes = enum[n_str]
        for code in codes:
            G = from_graph6(code)
            for r in positive_side_record(G):
                r["source"] = f"enum_n{n_str}"
                r["family"] = "enum"
                r["param_n"] = int(n_str)
                records.append(r)
        print(f"  enum n={n_str}: {len(codes)} graphs", file=sys.stderr)

    # 2. BT(k, 2)
    for k in [2, 5, 10, 25, 50, 100]:
        G = book_with_tail(k, 2)
        for r in positive_side_record(G):
            r["source"] = f"BT_k{k}_t2"
            r["family"] = "BT"
            r["k"] = k
            r["t"] = 2
            r["param_n"] = G.number_of_nodes()
            records.append(r)
        print(f"  BT k={k}: n={G.number_of_nodes()}", file=sys.stderr)

    # 3. Books B_k
    for k in range(2, 31):
        G = book_graph(k)
        for r in positive_side_record(G):
            r["source"] = f"book_k{k}"
            r["family"] = "book"
            r["k"] = k
            r["param_n"] = G.number_of_nodes()
            records.append(r)
    print(f"  books k=2..30 done", file=sys.stderr)

    # 4. 2-paths L_n
    for n in range(4, 31):
        G = two_path_graph(n)
        for r in positive_side_record(G):
            r["source"] = f"L_n{n}"
            r["family"] = "L"
            r["param_n"] = n
            records.append(r)
    print(f"  L_n n=4..30 done", file=sys.stderr)

    # 5. Fans F_n
    for n in range(4, 31):
        G = fan_graph(n)
        for r in positive_side_record(G):
            r["source"] = f"F_n{n}"
            r["family"] = "F"
            r["param_n"] = n
            records.append(r)
    print(f"  F_n n=4..30 done", file=sys.stderr)

    return records


def summarise(records):
    nA = sum(1 for r in records if r["case_pos"] == "A")
    nB = sum(1 for r in records if r["case_pos"] == "B")
    print(f"Total records: {len(records)} (A_+ : {nA}, B_+ : {nB})")

    # min/max delta^+
    rmin = min(records, key=lambda r: r["delta_plus"])
    rmax = max(records, key=lambda r: r["delta_plus"])
    print(f"min delta^+ = {rmin['delta_plus']:.6f} (g6={rmin['graph6']} v={rmin['v']} family={rmin['family']})")
    print(f"max delta^+ = {rmax['delta_plus']:.6f} (g6={rmax['graph6']} v={rmax['v']} family={rmax['family']})")

    # tightness of Lemma B1+ overall
    ratios = [r["ratio_lambda_max_over_f_max_plus"] for r in records
              if r["ratio_lambda_max_over_f_max_plus"] is not None]
    if ratios:
        print(f"Tightness ratio lambda_max / f_max^+: min={min(ratios):.4f}, max={max(ratios):.4f}, "
              f"mean={float(np.mean(ratios)):.4f}")
        # worst (loosest) case
        rworst = max(records, key=lambda r: (r["ratio_lambda_max_over_f_max_plus"] or 0.0))
        print(f"loosest record: g6={rworst['graph6']} v={rworst['v']} family={rworst['family']} "
              f"ratio={rworst['ratio_lambda_max_over_f_max_plus']:.4f}")
        rtight = min(records, key=lambda r: (r["ratio_lambda_max_over_f_max_plus"] or float("inf")))
        print(f"tightest record: g6={rtight['graph6']} v={rtight['v']} family={rtight['family']} "
              f"ratio={rtight['ratio_lambda_max_over_f_max_plus']:.4f}")

    # delta^+ by case
    A_recs = [r for r in records if r["case_pos"] == "A"]
    B_recs = [r for r in records if r["case_pos"] == "B"]
    if A_recs:
        rmax = max(A_recs, key=lambda r: r["delta_plus"])
        print(f"max delta^+ Case A_+ = {rmax['delta_plus']:.6f} (g6={rmax['graph6']} v={rmax['v']} family={rmax['family']})")
    if B_recs:
        rmax = max(B_recs, key=lambda r: r["delta_plus"])
        print(f"max delta^+ Case B_+ = {rmax['delta_plus']:.6f} (g6={rmax['graph6']} v={rmax['v']} family={rmax['family']})")

    # Case B_+: how small is alpha_top_plus? (analogue of F11 caveat)
    if B_recs:
        rmin = min(B_recs, key=lambda r: r["alpha_top_plus_sq"])
        print(f"min alpha_top_plus^2 in Case B_+ = {rmin['alpha_top_plus_sq']:.6f} "
              f"(g6={rmin['graph6']} v={rmin['v']} family={rmin['family']})")

    # max delta^+ by n
    print()
    print("max delta^+ by n in enum corpus:")
    from collections import defaultdict
    by_n = defaultdict(list)
    for r in records:
        if r["family"] == "enum":
            by_n[r["param_n"]].append(r)
    for n in sorted(by_n):
        worst = max(by_n[n], key=lambda r: r["delta_plus"])
        print(f"  n={n}: max delta^+ = {worst['delta_plus']:.6f} (g6={worst['graph6']} v={worst['v']})")


def main():
    records = build_census()
    out_path = DATA / "positive_side_ceiling_census.json"
    out_path.write_text(json.dumps(records, indent=None))
    print(f"\nwrote {len(records)} records to {out_path}")
    summarise(records)


if __name__ == "__main__":
    main()
