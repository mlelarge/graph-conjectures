"""Cutting-Plane Oracle Structural Audit (positive non-sweep route).

Two probes on the certified minimal-NO catalogues:

  STEP 1 (instrumented lazy oracle).  Run the exact branch-and-cut oracle
  (`ilp_exact_linear_forest_fas`, re-implemented here with tracking) and
  record, per instance: #directed-cycle cuts, #undirected-cycle cuts, the
  cut lengths, total rounds, and the final verdict.

  STEP 3 (full cycle-cut LP).  Enumerate ALL simple directed cycles of T
  (cut Σx ≥ 1) and ALL simple undirected cycles of the underlying K_n (cut
  Σx ≤ |C|−1), add degree ≤ 2, and solve the continuous **LP** (not ILP).
  For a NO instance the question is binary:
    * LP INFEASIBLE  ⇒ a polynomial (Farkas) certificate of NO exists from
      cycle cuts alone — a real proof target.
    * LP FEASIBLE (necessarily fractional, since an integral feasible point
      would be a linear-forest FAS = YES) ⇒ an integrality gap survives the
      full cycle-cut closure — the cutting-plane route is blocked, and the
      fractional point is the witness.

Ground truth: a NO instance has no linear-forest FAS
(`decide_linear_forest_fas_bruteforce`).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nonsweep_path_fas import (  # noqa: E402
    arcs_of, directed_triangles, is_acyclic, underlying_is_linear_forest,
    _find_directed_cycle, _find_undirected_cycle_edges,
    decide_linear_forest_fas_bruteforce,
)

Arc = tuple
from scipy.optimize import milp, LinearConstraint, Bounds  # noqa: E402


# ----------------------------------------------------------------------
# STEP 1: instrumented lazy branch-and-cut oracle
# ----------------------------------------------------------------------
def instrumented_oracle(T, max_rounds: int = 500) -> dict:
    arcs = arcs_of(T)
    m = len(arcs)
    idx = {a: i for i, a in enumerate(arcs)}
    n = len(T)
    arcset = set(arcs)
    rows, lb, ub = [], [], []
    for tri in directed_triangles(T):
        row = [0.0] * m
        for a in tri:
            row[idx[a]] = 1.0
        rows.append(row); lb.append(1.0); ub.append(np.inf)
    n_tri = len(rows)
    for v in range(n):
        row = [0.0] * m
        for i, (u, w) in enumerate(arcs):
            if u == v or w == v:
                row[i] = 1.0
        rows.append(row); lb.append(-np.inf); ub.append(2.0)
    c = np.ones(m)
    bounds = Bounds(0, 1)
    integrality = np.ones(m)
    dir_lengths, und_lengths = [], []
    for rnd in range(max_rounds):
        A = np.array(rows)
        res = milp(c=c, constraints=LinearConstraint(A, lb, ub),
                   bounds=bounds, integrality=integrality)
        if not res.success:
            ncut = len(dir_lengths) + len(und_lengths)
            return {"feasible": False, "rounds": rnd,
                    "n_directed_cuts": len(dir_lengths),
                    "n_undirected_cuts": len(und_lengths),
                    "directed_cut_lengths": dir_lengths,
                    "undirected_cut_lengths": und_lengths,
                    "total_cuts": ncut, "n_triangles": n_tri,
                    "cert_rows": n_tri + 2 * n + ncut}
        S = [arcs[i] for i in range(m) if res.x[i] > 0.5]
        kept = arcset - set(S)
        cyc = _find_directed_cycle(n, kept)
        if cyc is not None:
            row = [0.0] * m
            for a in cyc:
                row[idx[a]] = 1.0
            rows.append(row); lb.append(1.0); ub.append(np.inf)
            dir_lengths.append(len(cyc)); continue
        ucyc = _find_undirected_cycle_edges(S)
        if ucyc is not None:
            row = [0.0] * m
            for a in ucyc:
                row[idx[a]] = 1.0
            rows.append(row); lb.append(-np.inf); ub.append(float(len(ucyc) - 1))
            und_lengths.append(len(ucyc)); continue
        return {"feasible": True, "rounds": rnd,
                "n_directed_cuts": len(dir_lengths),
                "n_undirected_cuts": len(und_lengths),
                "directed_cut_lengths": dir_lengths,
                "undirected_cut_lengths": und_lengths,
                "total_cuts": len(dir_lengths) + len(und_lengths),
                "linear_forest": underlying_is_linear_forest(S)}
    return {"feasible": None, "note": "max_rounds hit"}


# ----------------------------------------------------------------------
# STEP 3: full cycle-cut LP
# ----------------------------------------------------------------------
def _all_directed_cycles(T, cap=200000):
    """All simple directed cycles of tournament T as arc lists."""
    n = len(T)
    out = []
    succ = [[v for v in range(n) if T[u][v]] for u in range(n)]

    def dfs(start, u, path, inpath):
        for v in succ[u]:
            if v == start and len(path) >= 3:
                out.append([(path[i], path[(i + 1) % len(path)])
                            for i in range(len(path))])
                if len(out) >= cap:
                    return True
            elif v > start and v not in inpath:
                inpath.add(v); path.append(v)
                if dfs(start, v, path, inpath):
                    return True
                path.pop(); inpath.discard(v)
        return False

    for s in range(n):
        if dfs(s, s, [s], {s}):
            break
    return out


def _all_undirected_cycles(T, cap=300000):
    """All simple cycles of the underlying K_n, as arc lists (the tournament
    arc for each undirected edge)."""
    n = len(T)
    def arc(u, v):
        return (u, v) if T[u][v] else (v, u)
    out = []

    def dfs(start, u, path, inpath):
        for v in range(n):
            if v == u:
                continue
            if v == start and len(path) >= 3:
                out.append([arc(path[i], path[(i + 1) % len(path)])
                            for i in range(len(path))])
                if len(out) >= cap:
                    return True
            elif v > start and v not in inpath:
                # canonical: second vertex > last, to avoid reversal dup
                if len(path) == 1 or v > path[1]:
                    pass
                inpath.add(v); path.append(v)
                if dfs(start, v, path, inpath):
                    return True
                path.pop(); inpath.discard(v)
        return False

    for s in range(n):
        if dfs(s, s, [s], {s}):
            break
    # dedup (each cycle found twice, both directions)
    seen = set(); uniq = []
    for cyc in out:
        key = frozenset(frozenset(a) for a in cyc)
        if key not in seen:
            seen.add(key); uniq.append(cyc)
    return uniq


def full_cycle_cut_lp(T) -> dict:
    arcs = arcs_of(T)
    m = len(arcs)
    idx = {a: i for i, a in enumerate(arcs)}
    n = len(T)
    A_ub, b_ub = [], []
    dcyc = _all_directed_cycles(T)
    for cyc in dcyc:                       # Σ x ≥ 1  →  -Σ x ≤ -1
        row = [0.0] * m
        for a in cyc:
            row[idx[a]] = -1.0
        A_ub.append(row); b_ub.append(-1.0)
    ucyc = _all_undirected_cycles(T)
    for cyc in ucyc:                       # Σ x ≤ |C|-1
        row = [0.0] * m
        for a in cyc:
            row[idx[a]] = 1.0
        A_ub.append(row); b_ub.append(float(len(cyc) - 1))
    for v in range(n):                     # degree ≤ 2
        row = [0.0] * m
        for i, (u, w) in enumerate(arcs):
            if u == v or w == v:
                row[i] = 1.0
        A_ub.append(row); b_ub.append(2.0)
    res = linprog(c=np.ones(m), A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, 1)] * m, method="highs")
    feasible = (res.status == 0)
    integral = None
    fractional_vars = None
    if feasible:
        x = res.x
        integral = bool(np.all(np.abs(x - np.round(x)) < 1e-6))
        fractional_vars = int(np.sum(np.abs(x - np.round(x)) >= 1e-6))
    return {"n_directed_cycles": len(dcyc), "n_undirected_cycles": len(ucyc),
            "lp_feasible": feasible, "lp_value": (float(res.fun) if feasible else None),
            "integral": integral, "n_fractional_vars": fractional_vars,
            "lp_status": int(res.status), "x": (res.x.tolist() if feasible else None)}


# ----------------------------------------------------------------------
# driver over a catalogue
# ----------------------------------------------------------------------
def audit_catalogue(n: int, limit: int | None, do_lp: bool,
                    bruteforce: bool = False) -> dict:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "data", f"minimal_no_obstruction_catalogue_n{n}.json")
    recs = json.load(open(path))["records"]
    if limit:
        recs = recs[:limit]
    oracle_cuts = Counter()
    dir_len_hist = Counter(); und_len_hist = Counter()
    cert_sizes = []
    n_no_confirmed = 0
    lp_infeasible = 0; lp_feasible_frac = 0; lp_feasible_int = 0
    lp_examples_frac = []
    # STEP 2: obstruction taxonomy x LP outcome
    by_obstruction = Counter()           # primary obstruction histogram
    lp_gap_by_obstruction = Counter()    # gaps split by obstruction primary
    cuts_by_obstruction = {}             # primary -> list of cut counts
    only_directed = only_undirected = both_cuts = neither = 0
    oracle_anomalies = 0
    for r in recs:
        T = r["T"]
        if bruteforce and decide_linear_forest_fas_bruteforce(T):
            continue   # not actually a NO; skip
        prim = r.get("obstruction", {}).get("primary", "unknown")
        o = instrumented_oracle(T)
        if o["feasible"] is not False:
            # oracle is exact: feasible=True => YES (catalogue mislabel),
            # None => max_rounds hit. Record and skip.
            oracle_anomalies += 1
            continue
        n_no_confirmed += 1
        by_obstruction[prim] += 1
        oracle_cuts[o["total_cuts"]] += 1
        for L in o["directed_cut_lengths"]: dir_len_hist[L] += 1
        for L in o["undirected_cut_lengths"]: und_len_hist[L] += 1
        cert_sizes.append(o["total_cuts"])
        cuts_by_obstruction.setdefault(prim, []).append(o["total_cuts"])
        nd, nu = o["n_directed_cuts"], o["n_undirected_cuts"]
        if nd and nu: both_cuts += 1
        elif nd: only_directed += 1
        elif nu: only_undirected += 1
        else: neither += 1
        if do_lp:
            lp = full_cycle_cut_lp(T)
            if not lp["lp_feasible"]:
                lp_infeasible += 1
            elif lp["integral"]:
                lp_feasible_int += 1   # should not happen for a NO
            else:
                lp_feasible_frac += 1
                lp_gap_by_obstruction[prim] += 1
                if len(lp_examples_frac) < 5:
                    lp_examples_frac.append({"name": r["name"], "T": T,
                        "lp_value": lp["lp_value"],
                        "n_fractional_vars": lp["n_fractional_vars"]})
    return {
        "n": n, "instances": n_no_confirmed,
        "oracle_anomalies": oracle_anomalies,
        "oracle_total_cuts_hist": dict(sorted(oracle_cuts.items())),
        "oracle_directed_cut_len_hist": dict(sorted(dir_len_hist.items())),
        "oracle_undirected_cut_len_hist": dict(sorted(und_len_hist.items())),
        "oracle_cut_count_min_max_mean": (min(cert_sizes), max(cert_sizes),
                                          round(sum(cert_sizes) / len(cert_sizes), 2))
            if cert_sizes else None,
        "lp_done": do_lp,
        "lp_infeasible_cert": lp_infeasible,
        "lp_feasible_fractional_GAP": lp_feasible_frac,
        "lp_feasible_integral_BUG": lp_feasible_int,
        "lp_fractional_examples": lp_examples_frac,
        "obstruction_hist": dict(by_obstruction),
        "lp_gap_by_obstruction": dict(lp_gap_by_obstruction),
        "cut_kind_split": {"only_directed": only_directed,
                           "only_undirected": only_undirected,
                           "both": both_cuts, "neither": neither},
        "mean_cuts_by_obstruction": {k: round(sum(v) / len(v), 2)
                                     for k, v in cuts_by_obstruction.items()},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--lp", action="store_true")
    ap.add_argument("--bf", action="store_true", help="brute-force recheck NO")
    args = ap.parse_args()
    print(json.dumps(audit_catalogue(args.n, args.limit, args.lp, args.bf),
                     indent=2))


if __name__ == "__main__":
    main()
