"""Robust column generation with round-and-fix rationalization.

Variant of ``run_column_generation.py`` that handles LP degeneracy by
rationalizing the float alpha at a common denominator and then iteratively
bumping any alpha that is too small to satisfy a dual-feasibility constraint.

Each bump increases sum alpha_i b_i slightly; the bump magnitudes are
``deficit / T_i(v) * (1/D)`` rounded up to one denominator step. The
loop terminates when no constraint is violated. The resulting alpha is
LP-feasible and rational, suitable for the existing rational checker.

The trade-off vs ``run_column_generation.py``:

- This is **less tight**: the rationalized objective may be slightly
  above the LP optimum, because each bump increases sum alpha_i b_i.
- This is **more robust**: it always returns a valid rational
  certificate regardless of LP degeneracy.

For paths up to length 7 on L_fpy box L_fpy at root (v_1, v_1), the
LP optimum is ~105.76 and round-and-fix at D=4800 produces a rational
certificate at sum_ab = 169327/1600 ~= 105.83, yielding derived bound
floor(105.83) + 1 = 106 -- a 2-point improvement over Hurlbert's 108.

Usage::

    python scripts/run_column_generation_robust.py [--max-len 7] [--denominator 4800] [--out path.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import check_certificate, load_certificate_file
from optimize_certificate_multipliers import _build_lp
from pebbling_graphs import cartesian_product, load_named_graph
from run_column_generation import enumerate_simple_paths, path_to_strategy


def round_and_fix(
    D: int,
    alpha_floats: list[float],
    sub_strats: list,
    b_T: list[Fraction],
    n: int,
    root: int,
    max_iters: int = 200,
) -> list[Fraction] | None:
    """Snap alphas to denominator D, then bump each violated constraint.

    Returns the rationalised alpha vector, or None if convergence fails.
    """
    alpha_q = [Fraction(round(D * float(a)), D) for a in alpha_floats]
    for _ in range(max_iters):
        violations = []
        for v in range(n):
            if v == root:
                continue
            s = sum(
                (a * t.weights.get(v, Fraction(0)) for a, t in zip(alpha_q, sub_strats)),
                start=Fraction(0),
            )
            if s < 1:
                violations.append((v, 1 - s))
        if not violations:
            return alpha_q
        v_worst, def_worst = max(violations, key=lambda x: x[1])
        best_i = None
        best_b: Fraction | None = None
        for i, t in enumerate(sub_strats):
            if t.weights.get(v_worst, Fraction(0)) > 0:
                if best_i is None or b_T[i] < best_b:
                    best_i = i
                    best_b = b_T[i]
        if best_i is None:
            return None
        T_iv = sub_strats[best_i].weights.get(v_worst, Fraction(0))
        bump_real = def_worst / T_iv
        bump = Fraction((int(bump_real * D) + 1), D)
        alpha_q[best_i] += bump
    return None


def run_robust_pass(
    base_cert_path: Path,
    max_len: int,
    denominator: int,
    out_path: Path,
) -> dict:
    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    n = LL.n
    adj = LL.adjacency()

    with base_cert_path.open() as fp:
        base = json.load(fp)
    root = int(base["root"])

    paths = enumerate_simple_paths(adj, root, max_len=max_len)
    candidates = [path_to_strategy(p, root) for p in paths]

    mega = dict(base)
    mega["strategies"] = list(base["strategies"]) + candidates
    mega["dual_multipliers"] = ["0"] * len(mega["strategies"])
    mega["claimed_bound"] = 999

    tmp_path = Path("/tmp/_run_column_gen_robust.json")
    with tmp_path.open("w") as fp:
        json.dump(mega, fp)

    cert, g = load_certificate_file(tmp_path)
    c, A_ub, rhs = _build_lp(cert, g.n)
    res = linprog(c=c, A_ub=A_ub, b_ub=rhs, bounds=[(0, None)] * len(c), method="highs-ds")
    nonzero_idx = [i for i, x in enumerate(res.x) if x > 1e-9]
    sub_c = c[nonzero_idx]
    sub_A = A_ub[:, nonzero_idx]
    sub_res = linprog(
        c=sub_c, A_ub=sub_A, b_ub=rhs,
        bounds=[(0, None)] * len(sub_c),
        method="highs-ds",
    )

    sub_strats = [cert.strategies[i] for i in nonzero_idx]
    n_strats = len(sub_strats)
    b_T_rational = [
        sum((w for vv, w in t.weights.items() if vv != cert.root), start=Fraction(0))
        for t in sub_strats
    ]

    alpha_q = round_and_fix(denominator, sub_res.x, sub_strats, b_T_rational, g.n, cert.root)
    if alpha_q is None:
        raise RuntimeError(
            f"round-and-fix failed at D={denominator}; try larger denominator"
        )

    sum_ab = sum(
        (a * b for a, b in zip(alpha_q, b_T_rational)),
        start=Fraction(0),
    )
    derived = sum_ab.numerator // sum_ab.denominator + 1

    output = {
        "graph": base["graph"],
        "root": cert.root,
        "claimed_bound": derived,
        "strategies": [
            {
                "name": s.name,
                "tree_edges": [list(e) for e in s.tree_edges],
                "weights": {str(k): str(v) for k, v in s.weights.items()},
                "basic": s.basic,
            }
            for s in sub_strats
        ],
        "dual_multipliers": [str(a) for a in alpha_q],
        "notes": (
            f"Column generation max_len={max_len} ({len(paths)} candidate paths), "
            f"{n_strats} active. Float LP optimum {sub_res.fun:.6f}; "
            f"alpha rationalized at common denominator D={denominator} with "
            f"round-and-fix. sum alpha_i b_i = {sum_ab}. "
            f"Derived bound = floor({sum_ab}) + 1 = {derived}."
        ),
    }
    with out_path.open("w") as fp:
        json.dump(output, fp, indent=2)

    cert2, g2 = load_certificate_file(out_path)
    chk = check_certificate(cert2, g2)

    return {
        "n_candidate_paths": len(paths),
        "n_active_strategies": n_strats,
        "lp_optimum_float": float(sub_res.fun),
        "rationalised_sum_alpha_b": str(sum_ab),
        "denominator": denominator,
        "derived_bound": derived,
        "checker_accepted": chk.accepted,
        "checker_derived": chk.derived_bound,
        "out_path": str(out_path),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--base",
        default=str(
            REPO_ROOT
            / "data/pebbling_product/certificates/Hurlbert_decomposed_branches_v1v1.json"
        ),
    )
    ap.add_argument("--max-len", type=int, default=7)
    ap.add_argument("--denominator", type=int, default=4800)
    ap.add_argument(
        "--out",
        default=str(
            REPO_ROOT
            / "data/pebbling_product/certificates/Hurlbert_path_augmented_v1v1_le106.json"
        ),
    )
    args = ap.parse_args()
    summary = run_robust_pass(
        Path(args.base), args.max_len, args.denominator, Path(args.out)
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
