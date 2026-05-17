"""Ansatz search for the v10 joint-invariant selector.

For each candidate functional I = I(feature_vector), we compute:
    g_lower = min over max-degsum corpus of I(v*)
    g_upper = max over bad ears (delta_minus < 17/16) in the all-ears corpus
The candidate is *consistent* if g_lower > g_upper. The "gap" g_lower - g_upper
quantifies the safety margin.

A threshold T can then be chosen in (g_upper, g_lower].

Two-stage filter:
    Stage 1: scan every candidate against the full corpus. Emit gap.
    Stage 2: validate on a held-out random 2-tree set (n=200, 20 seeds).

Candidate families (degree <= 2 polynomials in the features, plus rational forms
motivated by the Case B analysis):
    - linear in {W_minus, W_zero, W_plus, c1_sq, c_last_sq, |M1_minus|,
      M2_minus, |M1_plus|, M2_plus, 1/mu_max, c1_sq/mu_max}.
    - 2-way products of features.
    - sum-of-ratios: W_minus + M1_minus^2 / max(M2_minus, eps).
    - Case-B-aware: c1_sq / mu_max^2, W_plus / mu_max^2,
      c1_sq / (mu_max^2 + 1).
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from joint_invariant_features import ear_records  # noqa: E402
from build_joint_invariant_corpus import random_two_tree  # noqa: E402

DATA = ROOT / "data"
TESTS = ROOT / "tests"
FIXTURES = TESTS / "fixtures"
THRESHOLD = 17.0 / 16.0
EPS = 1e-12


def load_corpus():
    max_recs = json.loads((DATA / "joint_invariant_scan.json").read_text())
    all_recs = json.loads((DATA / "joint_invariant_scan_all_ears.json").read_text())
    return max_recs, all_recs


# --- candidate registry ----------------------------------------------------

def feat(r, k):
    return r[k]


def safe_div(a, b, eps=1e-12):
    return a / (b if abs(b) > eps else (eps if b >= 0 else -eps))


CANDIDATES: list[tuple[str, Callable]] = []


def register(name):
    def deco(f):
        CANDIDATES.append((name, f))
        return f
    return deco


# Linear in single features
@register("W_minus")
def f_wminus(r): return r["W_minus"]
@register("W_zero")
def f_wzero(r): return r["W_zero"]
@register("W_minus + W_zero")
def f_wmz(r): return r["W_minus"] + r["W_zero"]
@register("W_minus + 0.5*W_zero")
def f_wmz_half(r): return r["W_minus"] + 0.5 * r["W_zero"]
@register("W_minus + 0.25*W_zero")
def f_wmz_q(r): return r["W_minus"] + 0.25 * r["W_zero"]
@register("W_minus + 0.75*W_zero")
def f_wmz_3q(r): return r["W_minus"] + 0.75 * r["W_zero"]
@register("c_last_sq")
def f_clast(r): return r["c_last_sq"]
@register("|M1_minus|")
def f_m1neg(r): return abs(r["M1_minus"])
@register("M2_minus")
def f_m2neg(r): return r["M2_minus"]
@register("c1_sq")
def f_c1(r): return r["c1_sq"]

# Cauchy-Schwarz motivated
@register("W_minus + M1_minus^2/M2_minus")
def f_cs(r):
    if r["M2_minus"] > 1e-12:
        return r["W_minus"] + r["M1_minus"] ** 2 / r["M2_minus"]
    return r["W_minus"]

# Case-B aware: resolvent-pole proxies
@register("c1_sq / mu_max")
def f_c1_over_mu(r): return safe_div(r["c1_sq"], r["mu_max"])
@register("c1_sq / mu_max^2")
def f_c1_over_mu2(r): return safe_div(r["c1_sq"], r["mu_max"] ** 2)
@register("W_plus / mu_max^2")
def f_wp_over_mu2(r): return safe_div(r["W_plus"], r["mu_max"] ** 2)
@register("c1_sq / (mu_max^2 + 1)")
def f_c1_over_mu2p1(r): return r["c1_sq"] / (r["mu_max"] ** 2 + 1.0)
@register("1/mu_max")
def f_inv_mu(r): return 1.0 / max(r["mu_max"], 1e-12)
@register("1/mu_max^2")
def f_inv_mu2(r): return 1.0 / max(r["mu_max"] ** 2, 1e-12)

# Joint with Case-B pole proxy
@register("W_minus + c1_sq/mu_max^2")
def f_join1(r):
    return r["W_minus"] + safe_div(r["c1_sq"], r["mu_max"] ** 2)
@register("W_minus + W_zero + c1_sq/mu_max^2")
def f_join2(r):
    return r["W_minus"] + r["W_zero"] + safe_div(r["c1_sq"], r["mu_max"] ** 2)
@register("W_minus + 0.5*W_zero + c1_sq/mu_max^2")
def f_join3(r):
    return r["W_minus"] + 0.5 * r["W_zero"] + safe_div(r["c1_sq"], r["mu_max"] ** 2)
@register("W_minus + 0.5*W_zero + 0.5*c1_sq/mu_max^2")
def f_join4(r):
    return r["W_minus"] + 0.5 * r["W_zero"] + 0.5 * safe_div(r["c1_sq"], r["mu_max"] ** 2)
@register("W_minus + c_last_sq")
def f_join5(r):
    return r["W_minus"] + r["c_last_sq"]
@register("|M1_minus| + c1_sq/mu_max^2")
def f_join6(r):
    return abs(r["M1_minus"]) + safe_div(r["c1_sq"], r["mu_max"] ** 2)
@register("|M1_minus|^2/M2_minus + c1_sq/mu_max^2")
def f_join7(r):
    a = r["M1_minus"] ** 2 / r["M2_minus"] if r["M2_minus"] > 1e-12 else 0.0
    return a + safe_div(r["c1_sq"], r["mu_max"] ** 2)
@register("W_minus + W_zero + 0.5*c1_sq/mu_max^2")
def f_join8(r):
    return r["W_minus"] + r["W_zero"] + 0.5 * safe_div(r["c1_sq"], r["mu_max"] ** 2)

# Two-way products
@register("W_minus * W_plus")
def f_prod1(r): return r["W_minus"] * r["W_plus"]
@register("W_minus * mu_max")
def f_prod2(r): return r["W_minus"] * r["mu_max"]
@register("c_last_sq * |mu_min|")
def f_prod3(r): return r["c_last_sq"] * abs(r["mu_min"])
@register("c_last_sq * mu_min^2")
def f_prod4(r): return r["c_last_sq"] * r["mu_min"] ** 2
@register("c1_sq * c_last_sq")
def f_prod5(r): return r["c1_sq"] * r["c_last_sq"]
@register("(W_minus+W_zero) * mu_max")
def f_prod6(r): return (r["W_minus"] + r["W_zero"]) * r["mu_max"]
@register("M2_minus + c1_sq/mu_max")
def f_prod7(r): return r["M2_minus"] + safe_div(r["c1_sq"], r["mu_max"])

# delta- exact-target proxies
@register("M2_minus / W_minus")
def f_ratio1(r):
    return r["M2_minus"] / r["W_minus"] if r["W_minus"] > 1e-12 else 0.0
@register("|M1_minus|^2/W_minus")
def f_ratio2(r):
    return r["M1_minus"] ** 2 / r["W_minus"] if r["W_minus"] > 1e-12 else 0.0

# Trace-identity motivated: delta- = (sum c_i^2 mu_i^2 over kept + new e^2)
@register("M2_minus + c_last_sq*mu_min^2")
def f_sec1(r): return r["M2_minus"] + r["c_last_sq"] * r["mu_min"] ** 2
@register("M2_minus + 0.5*(c_last_sq+c1_sq)*(mu_min^2)")
def f_sec2(r): return r["M2_minus"] + 0.5 * (r["c_last_sq"] + r["c1_sq"]) * r["mu_min"] ** 2
@register("M2_minus + c1_sq/(mu_max-mu_min)^2")
def f_sec3(r):
    d = r["mu_max"] - r["mu_min"]
    return r["M2_minus"] + r["c1_sq"] / (d ** 2 if d > 1e-12 else 1e-12)


def evaluate(name: str, fn: Callable, max_recs: list[dict], all_recs: list[dict]):
    vals_max = np.array([fn(r) for r in max_recs])
    vals_all = np.array([fn(r) for r in all_recs])
    deltas = np.array([r["delta_minus"] for r in all_recs])
    bad_mask = deltas < THRESHOLD - EPS
    bad_vals = vals_all[bad_mask]
    g_lower = float(np.min(vals_max))
    if bad_vals.size > 0:
        g_upper = float(np.max(bad_vals))
        idx_max_bad = int(np.argmax(bad_vals))
        bad_indices = np.where(bad_mask)[0]
        worst_bad = all_recs[int(bad_indices[idx_max_bad])]
    else:
        g_upper = float("-inf")
        worst_bad = None
    gap = g_lower - g_upper
    idx_min_max = int(np.argmin(vals_max))
    return {
        "name": name,
        "g_lower": g_lower,
        "g_upper": g_upper,
        "gap": gap,
        "consistent": gap > 0,
        "argmin_max_record": max_recs[idx_min_max],
        "argmax_bad_record": worst_bad,
    }


def stage2_validate(fn: Callable, T: float, n: int = 200, seeds=range(20)) -> dict:
    """Held-out random 2-tree validation."""
    lower = float("inf")
    bad_max = float("-inf")
    violations = []
    for seed in seeds:
        G = random_two_tree(n, seed)
        for r in ear_records(G):
            v = fn(r)
            if r["is_max_degsum"] and v < lower:
                lower = v
            if r["delta_minus"] < THRESHOLD - EPS and v > bad_max:
                bad_max = v
            # Implication test:
            if v >= T and r["delta_minus"] < THRESHOLD - EPS:
                violations.append({
                    "graph6": r["graph6"], "v": r["v"],
                    "I_value": v, "delta_minus": r["delta_minus"],
                    "is_max_degsum": r["is_max_degsum"],
                })
            # Lower-bound test:
            if r["is_max_degsum"] and v < T:
                violations.append({
                    "graph6": r["graph6"], "v": r["v"],
                    "I_value": v, "delta_minus": r["delta_minus"],
                    "is_max_degsum": True, "below_T": True,
                })
    return {
        "stage2_min_max_degsum": lower,
        "stage2_max_bad": bad_max,
        "stage2_violations": violations[:10],
        "stage2_n_violations": len(violations),
    }


def main():
    max_recs, all_recs = load_corpus()
    print(f"Corpus: {len(max_recs)} max-degsum records, {len(all_recs)} all-ear records")
    bad = [r for r in all_recs if r["delta_minus"] < THRESHOLD - EPS]
    print(f"Bad ears (delta_minus < 17/16): {len(bad)}")
    if bad:
        worst = min(bad, key=lambda r: r["delta_minus"])
        print(f"  worst delta_minus = {worst['delta_minus']:.6f} "
              f"at graph6={worst['graph6']} v={worst['v']} is_max_degsum={worst['is_max_degsum']}")

    results = []
    for name, fn in CANDIDATES:
        results.append(evaluate(name, fn, max_recs, all_recs))

    results.sort(key=lambda x: -x["gap"])

    print("\n=== Top candidates by gap ===")
    print(f"{'rank':>4} {'name':<55} {'g_lower':>10} {'g_upper':>10} {'gap':>10} {'consistent':>10}")
    consistent = []
    for i, res in enumerate(results[:20], 1):
        print(f"{i:>4} {res['name']:<55} {res['g_lower']:>10.5f} "
              f"{res['g_upper']:>10.5f} {res['gap']:>10.5f} {str(res['consistent']):>10}")
        if res["consistent"]:
            consistent.append(res)

    print(f"\nConsistent candidates: {len(consistent)} of {len(CANDIDATES)}")

    # Stage 2 for top consistent candidates
    print("\n=== Stage 2: held-out random 2-trees n=200, seeds 0..19 ===")
    fn_by_name = {n: f for n, f in CANDIDATES}
    stage2_data = []
    for res in consistent[:8]:
        T = 0.5 * (res["g_lower"] + res["g_upper"])  # midpoint threshold
        s2 = stage2_validate(fn_by_name[res["name"]], T)
        s2["candidate"] = res["name"]
        s2["T"] = T
        s2["stage1_g_lower"] = res["g_lower"]
        s2["stage1_g_upper"] = res["g_upper"]
        s2["stage1_gap"] = res["gap"]
        stage2_data.append(s2)
        print(f"{res['name']:<55} T={T:.4f} stage2_min={s2['stage2_min_max_degsum']:.4f} "
              f"stage2_max_bad={s2['stage2_max_bad']:.4f} n_viol={s2['stage2_n_violations']}")

    # Falsified candidates
    falsified = [r for r in results if not r["consistent"]]
    print(f"\nFalsified candidates: {len(falsified)}")
    print("\n=== Top 10 falsified candidates ===")
    for i, res in enumerate(falsified[:10], 1):
        bad = res["argmax_bad_record"]
        rec = res["argmin_max_record"]
        print(f"{i}. {res['name']}: g_lower={res['g_lower']:.4f} g_upper={res['g_upper']:.4f}")
        if bad:
            print(f"    bad-ear witness: g6={bad['graph6']} v={bad['v']} "
                  f"delta-={bad['delta_minus']:.4f} I={res['g_upper']:.4f}")
        print(f"    max-degsum argmin: g6={rec['graph6']} v={rec['v']} I={res['g_lower']:.4f}")

    # Save results
    out = {
        "n_candidates": len(CANDIDATES),
        "n_consistent": len(consistent),
        "top20": [
            {
                "name": r["name"], "g_lower": r["g_lower"],
                "g_upper": r["g_upper"], "gap": r["gap"],
                "consistent": r["consistent"],
                "argmax_bad_g6": r["argmax_bad_record"]["graph6"] if r["argmax_bad_record"] else None,
                "argmax_bad_v": r["argmax_bad_record"]["v"] if r["argmax_bad_record"] else None,
                "argmax_bad_delta_minus": r["argmax_bad_record"]["delta_minus"] if r["argmax_bad_record"] else None,
                "argmin_max_g6": r["argmin_max_record"]["graph6"],
                "argmin_max_v": r["argmin_max_record"]["v"],
            } for r in results[:20]
        ],
        "falsified_top10": [
            {
                "name": r["name"], "g_lower": r["g_lower"],
                "g_upper": r["g_upper"], "gap": r["gap"],
                "argmax_bad": r["argmax_bad_record"],
                "argmin_max": r["argmin_max_record"],
            } for r in falsified[:10]
        ],
        "stage2": stage2_data,
    }
    (DATA / "joint_invariant_ansatz_results.json").write_text(json.dumps(out, indent=2))
    print("\nWrote data/joint_invariant_ansatz_results.json")

    # Falsified-candidates fixture
    falsified_fix = []
    for r in falsified[:20]:
        bad = r["argmax_bad_record"]
        if bad is None:
            continue
        falsified_fix.append({
            "candidate": r["name"],
            "T_used": 0.5 * (r["g_lower"] + r["g_upper"]) if r["g_upper"] > 0 else r["g_lower"],
            "g_lower": r["g_lower"],
            "g_upper": r["g_upper"],
            "counterexample_graph6": bad["graph6"],
            "counterexample_v": bad["v"],
            "counterexample_a": bad["a"],
            "counterexample_b": bad["b"],
            "counterexample_delta_minus": bad["delta_minus"],
            "counterexample_is_max_degsum": bad["is_max_degsum"],
            "counterexample_features": {
                "W_minus": bad["W_minus"], "W_zero": bad["W_zero"],
                "W_plus": bad["W_plus"], "c1_sq": bad["c1_sq"],
                "c_last_sq": bad["c_last_sq"],
                "M1_minus": bad["M1_minus"], "M2_minus": bad["M2_minus"],
                "mu_min": bad["mu_min"], "mu_max": bad["mu_max"],
            },
        })
    FIXTURES.mkdir(parents=True, exist_ok=True)
    (FIXTURES / "joint_invariant_falsified.json").write_text(json.dumps(falsified_fix, indent=2))
    print(f"Wrote tests/fixtures/joint_invariant_falsified.json ({len(falsified_fix)} entries)")

    return results, consistent, stage2_data


if __name__ == "__main__":
    main()
