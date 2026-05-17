"""Build the Case A / Case B census for Phase 9 (b.minor) target.

For each 2-tree in the union of:
  * enumerated 2-trees, n in [4, 10],
  * BT(k, 2) for k in {2, 5, 10, 25, 50, 100},
  * books B_k for k in [2, 30],
  * 2-paths L_n for n in [4, 30],
  * fans F_n for n in [4, 30],

compute the max-degsum simplicial degree-2 ear v*, then classify the
ear deletion as Case A (n^-(G) = n^-(H)) or Case B
(n^-(G) = n^-(H) + 1). Record:
    delta_minus(v*)               -- ground truth via eigvalsh
    alpha_sq                      -- lambda_min(A(G))^2
    W_minus, M1_minus, M2_minus
    f_min_sq                      -- Lemma B1 lower bound on alpha_sq
                                     when W_minus > 0; else None
    slot_shift_sum                -- delta_minus - alpha_sq (=0 in Case A)
                                     used for the harder Case A route.
    n_minus_G, n_minus_H
    deg_a, deg_b (in H)           -- diagnostic
Output: data/case_AB_census.json

Reuses scripts/joint_invariant_features.py for the (W^-, M_k^-) data
and scripts/build_joint_invariant_corpus.py for the family generators
(book_graph, two_path_graph, fan_graph, book_with_tail).
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
from joint_invariant_features import ear_records, from_graph6, simplicial_deg2_ears  # noqa: E402
from build_joint_invariant_corpus import (  # noqa: E402
    book_graph, two_path_graph, fan_graph,
)
from extreme_family import book_with_tail  # noqa: E402
from spectrum_check import spectrum  # noqa: E402

DATA = ROOT / "data"
TOL = 1e-9


def case_AB_record(G: nx.Graph, max_only: bool = True) -> list[dict]:
    """For each ear v (or only the max-degsum ear if max_only) compute
    Case A vs B classification + Lemma B1 features + slot-shift stats.

    Slot decomposition (verified empirically, sign-corrected wrt the
    prompt v11 text): with pairing (lambda_{i+1}(G), mu_i(H)) by
    Cauchy interlacing,
        Case A:  delta- = sum_{j in J^-}(lambda_{j+1}^2 - mu_j^2),
                 all summands >= 0.
        Case B:  delta- = alpha_top^2 + sum_{j in J^-}(lambda_{j+1}^2
                 - mu_j^2), where alpha_top := lambda_{n - n^-(H)}(G) is
                 the LEAST negative of G's negatives (its index in
                 ascending-from-zero of negatives = 1); all slot summands
                 >= 0.
    Lemma B1 bounds the MOST-negative eigenvalue
    alpha_min := lambda_min(A(G)) = lambda_n(G), separate from
    alpha_top.
    """
    base_recs = ear_records(G)
    if max_only:
        base_recs = [r for r in base_recs if r["is_max_degsum"]]
    eigs_G_desc = np.array(sorted(spectrum(G), reverse=True))  # lambda_1 >= ... >= lambda_n
    n_G = len(eigs_G_desc)
    alpha_min_sq = float(eigs_G_desc[-1] ** 2)  # lambda_min^2
    n_minus_G = int(np.sum(eigs_G_desc < -TOL))
    out = []
    for r in base_recs:
        v = r["v"]
        H = G.copy()
        H.remove_node(v)
        eigs_H_desc = np.array(sorted(spectrum(H), reverse=True))  # mu_1 >= ... >= mu_{n-1}
        n_H = len(eigs_H_desc)
        n_minus_H = int(np.sum(eigs_H_desc < -TOL))
        case = "A" if n_minus_G == n_minus_H else "B"
        assert n_minus_G in (n_minus_H, n_minus_H + 1), (
            f"unexpected inertia change: G g6={r['graph6']} v={v} "
            f"n_minus_G={n_minus_G} n_minus_H={n_minus_H}"
        )
        # Slot decomposition. J^- (in descending indexing of H) = indices
        # j s.t. mu_j(H) < 0, i.e. j in {n_H - n_minus_H, ..., n_H - 1}
        # under 1-based indexing, or {n_H - n_minus_H .. n_H - 1} 1-based
        # which is python indices {n_H - n_minus_H - 1 .. n_H - 1}.
        # Cleaner: just take the n_minus_H smallest entries of H's negs.
        H_negs_desc = eigs_H_desc[eigs_H_desc < -TOL]  # mu's, descending magnitude
        # Pair lambda_{j+1}(G) with mu_j(H), 1-based: in python (0-indexed),
        # lambda_{j+1} -> eigs_G_desc[j], mu_j -> eigs_H_desc[j-1]. The
        # relation lambda_{j+1} <= mu_j means in python eigs_G_desc[j] <=
        # eigs_H_desc[j-1]. So pair eigs_G_desc[j] with eigs_H_desc[j-1]
        # for j = 1, ..., n_H. For j in J^- (1-based): j in [n_H - n_minus_H + 1, n_H]
        # python: j in [n_H - n_minus_H, n_H - 1]
        slot_shifts = []
        for j_one in range(n_H - n_minus_H + 1, n_H + 1):  # 1-based, j in J^-
            # G eigenvalue at position j_one + 1 (1-based) = python index j_one
            # H eigenvalue at position j_one (1-based) = python index j_one - 1
            lam = float(eigs_G_desc[j_one])
            mu = float(eigs_H_desc[j_one - 1])
            slot_shifts.append(lam * lam - mu * mu)
        slot_shift_sum = float(sum(slot_shifts))
        slot_shift_max = float(max(slot_shifts)) if slot_shifts else 0.0
        slot_shift_min = float(min(slot_shifts)) if slot_shifts else 0.0
        # alpha_top in Case B: lambda_{n - n_minus_H} (1-based)
        # = python eigs_G_desc[n_G - n_minus_H - 1]. Equivalent to "least
        # negative G-neg" (the one with smallest |lambda|).
        if case == "B":
            alpha_top = float(eigs_G_desc[n_G - n_minus_H - 1])
            alpha_top_sq = alpha_top * alpha_top
        else:
            alpha_top = 0.0
            alpha_top_sq = 0.0
        # Sanity check: delta- = alpha_top_sq + slot_shift_sum (verify).
        dminus = float(r["delta_minus"])
        recon = alpha_top_sq + slot_shift_sum
        assert abs(recon - dminus) < 1e-6, (
            f"slot reconstruction failed: dminus={dminus} recon={recon} "
            f"case={case} g6={r['graph6']} v={v}"
        )
        Wm = float(r["W_minus"])
        M1m = float(r["M1_minus"])
        M2m = float(r["M2_minus"])
        if Wm > TOL:
            disc = M1m * M1m + 4.0 * Wm * Wm * Wm
            f_min_abs = (abs(M1m) + math.sqrt(disc)) / (2.0 * Wm)
            f_min_sq = float(f_min_abs * f_min_abs)
        else:
            f_min_sq = None
        rec = {
            "graph6": r["graph6"],
            "n": r["n"],
            "v": v,
            "a": r["a"],
            "b": r["b"],
            "case": case,
            "n_minus_G": n_minus_G,
            "n_minus_H": n_minus_H,
            "delta_minus": dminus,
            "alpha_min_sq": alpha_min_sq,    # lambda_min(A(G))^2
            "alpha_top_sq": alpha_top_sq,    # Case B's "new" eigenvalue at the top of G's negs
            "W_minus": Wm,
            "M1_minus": M1m,
            "M2_minus": M2m,
            "f_min_sq": f_min_sq,
            "slot_shift_sum": slot_shift_sum,
            "slot_shift_max": slot_shift_max,
            "slot_shift_min": slot_shift_min,
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
            for r in case_AB_record(G):
                r["source"] = f"enum_n{n_str}"
                r["family"] = "enum"
                r["param_n"] = int(n_str)
                records.append(r)
        print(f"  enum n={n_str}: {len(codes)} graphs", file=sys.stderr)

    # 2. BT(k, 2)
    for k in [2, 5, 10, 25, 50, 100]:
        G = book_with_tail(k, 2)
        for r in case_AB_record(G):
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
        for r in case_AB_record(G):
            r["source"] = f"book_k{k}"
            r["family"] = "book"
            r["k"] = k
            r["param_n"] = G.number_of_nodes()
            records.append(r)
    print(f"  books k=2..30 done", file=sys.stderr)

    # 4. 2-paths L_n
    for n in range(4, 31):
        G = two_path_graph(n)
        for r in case_AB_record(G):
            r["source"] = f"L_n{n}"
            r["family"] = "L"
            r["param_n"] = n
            records.append(r)
    print(f"  L_n n=4..30 done", file=sys.stderr)

    # 5. Fans F_n
    for n in range(4, 31):
        G = fan_graph(n)
        for r in case_AB_record(G):
            r["source"] = f"F_n{n}"
            r["family"] = "F"
            r["param_n"] = n
            records.append(r)
    print(f"  F_n n=4..30 done", file=sys.stderr)

    return records


def summarise(records):
    nA = sum(1 for r in records if r["case"] == "A")
    nB = sum(1 for r in records if r["case"] == "B")
    print(f"Total records: {len(records)} (A: {nA}, B: {nB})")
    A_recs = [r for r in records if r["case"] == "A"]
    B_recs = [r for r in records if r["case"] == "B"]
    # min alpha_min_sq in Case B
    if B_recs:
        rmin = min(B_recs, key=lambda r: r["alpha_min_sq"])
        print(f"min alpha_min_sq in Case B = {rmin['alpha_min_sq']:.6f} "
              f"(fam={rmin['family']} n={rmin['n']} v={rmin['v']} g6={rmin['graph6']})")
    # min alpha_top_sq in Case B
    if B_recs:
        rmin = min(B_recs, key=lambda r: r["alpha_top_sq"])
        print(f"min alpha_top_sq in Case B = {rmin['alpha_top_sq']:.6f} "
              f"(fam={rmin['family']} n={rmin['n']} v={rmin['v']} g6={rmin['graph6']})")
    # min f_min_sq in Case B
    B_f = [r for r in B_recs if r["f_min_sq"] is not None]
    if B_f:
        rmin = min(B_f, key=lambda r: r["f_min_sq"])
        print(f"min f_min_sq in Case B (W- > 0) = {rmin['f_min_sq']:.6f} "
              f"(fam={rmin['family']} n={rmin['n']} v={rmin['v']} g6={rmin['graph6']})")
    # min slot_shift_max in Case A
    if A_recs:
        rmin = min(A_recs, key=lambda r: r["slot_shift_max"])
        print(f"min slot_shift_max in Case A = {rmin['slot_shift_max']:.6f} "
              f"(= max-slot bound on delta-) "
              f"(fam={rmin['family']} n={rmin['n']} v={rmin['v']} g6={rmin['graph6']})")
        rmin = min(A_recs, key=lambda r: r["slot_shift_sum"])
        print(f"min slot_shift_sum in Case A (= delta-) = {rmin['slot_shift_sum']:.6f} "
              f"(fam={rmin['family']} n={rmin['n']} v={rmin['v']} g6={rmin['graph6']})")
    # min delta- overall, by case
    if A_recs:
        rmin = min(A_recs, key=lambda r: r["delta_minus"])
        print(f"min delta- in Case A = {rmin['delta_minus']:.6f} "
              f"(fam={rmin['family']} n={rmin['n']} v={rmin['v']} g6={rmin['graph6']})")
    if B_recs:
        rmin = min(B_recs, key=lambda r: r["delta_minus"])
        print(f"min delta- in Case B = {rmin['delta_minus']:.6f} "
              f"(fam={rmin['family']} n={rmin['n']} v={rmin['v']} g6={rmin['graph6']})")
    rmin = min(records, key=lambda r: r["delta_minus"])
    print(f"min delta- overall = {rmin['delta_minus']:.6f} "
          f"(case {rmin['case']}, fam={rmin['family']}, n={rmin['n']}, "
          f"v={rmin['v']}, g6={rmin['graph6']})")
    # Cauchy-Schwarz extras: M2_minus / W_minus on Case B records
    print("\nCauchy-Schwarz check: M2_minus >= 4 W_minus (would suffice for f_min^2 >= 1):")
    bad = [r for r in records if r["W_minus"] > TOL
           and r["M2_minus"] < 4.0 * r["W_minus"] - TOL]
    print(f"  records violating M2- >= 4 W-: {len(bad)} of {len(records)}")
    if bad:
        rmin = min(bad, key=lambda r: r["M2_minus"] / r["W_minus"])
        print(f"  worst ratio M2-/W-: {rmin['M2_minus']/rmin['W_minus']:.4f} "
              f"(fam={rmin['family']} n={rmin['n']} g6={rmin['graph6']})")


def main():
    records = build_census()
    out_path = DATA / "case_AB_census.json"
    out_path.write_text(json.dumps(records, indent=None))
    print(f"\nwrote {len(records)} records to {out_path}")
    summarise(records)


if __name__ == "__main__":
    main()
