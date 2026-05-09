"""Optimize dual multipliers ``alpha_i`` for a fixed set of Hurlbert strategies.

Solves the master LP

    minimize    sum_i alpha_i b_i
    subject to  sum_i alpha_i w_i(v) >= 1   for every non-root v
                alpha_i >= 0

using SciPy's floating-point LP solver to *nominate* an optimal
``alpha``, then **rationalises** the result and feeds it through the
existing rational checker
(``scripts/check_pebbling_weight_certificate.py``). The checker
remains the only authority for accepting or rejecting a certificate;
the LP is just a search heuristic.

By LP duality, the master LP optimum equals the dual LP optimum
(maximum of ``sum_v C(v)`` over rational ``r``-unsolvable ``C``
configurations subject to the strategy weight constraints). So if the
LP optimum equals ``floor(claimed_bound) - 1``, no further improvement
is achievable from this strategy set; the only way to tighten the
derived bound is to introduce different strategies.

Usage::

    python scripts/optimize_certificate_multipliers.py <certificate.json>

The script prints the LP optimum, the rationalised ``alpha``, and an
end-to-end checker verdict on the resulting certificate. If the
rationalised certificate is strictly tighter than the input
(``derived_bound`` strictly smaller), an *_optimized.json file is
written next to the input.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_pebbling_weight_certificate import (
    check_certificate,
    load_certificate_file,
    parse_certificate,
)
from pebbling_graphs import make_graph


@dataclass
class OptResult:
    lp_optimum_float: float
    lp_alpha_float: list[float]
    alpha_rational: list[Fraction]
    sum_alpha_b_rational: Fraction
    derived_bound: int
    binding_vertices: list[int]
    matched_input_bound: bool
    improvement_over_input: int
    accepted_by_checker: bool


def _load_input_certificate(path: Path):
    cert, g = load_certificate_file(path)
    return cert, g


def _build_lp(cert, n_vertices: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build (c, A, sense): minimize c^T alpha s.t. A alpha >= 1.

    Returns numpy arrays in the form expected by ``scipy.optimize.linprog``:
    we return ``A_ub`` and ``b_ub`` for the equivalent ``-A alpha <= -1``
    formulation.
    """
    k = len(cert.strategies)
    # b_i = sum_{v != root} w_i(v)
    c = np.zeros(k, dtype=float)
    for i, strat in enumerate(cert.strategies):
        b_T = sum(
            (
                w
                for v, w in strat.weights.items()
                if v != cert.root
            ),
            start=Fraction(0),
        )
        c[i] = float(b_T)
    # A: one row per non-root vertex, columns are strategies.
    # A[v_idx, i] = w_i(v).
    A_ub = np.zeros((n_vertices - 1, k), dtype=float)
    rhs = np.zeros(n_vertices - 1, dtype=float)
    row = 0
    for v in range(n_vertices):
        if v == cert.root:
            continue
        rhs[row] = -1.0  # -A alpha <= -1
        for i, strat in enumerate(cert.strategies):
            w = strat.weights.get(v, Fraction(0))
            A_ub[row, i] = -float(w)
        row += 1
    return c, A_ub, rhs


def _rationalize_alpha(
    alpha_float: list[float], cert, n_vertices: int
) -> list[Fraction]:
    """Convert float ``alpha`` to exact rationals.

    Strategy: identify constraints that are (numerically) tight at the
    LP solution, then solve the corresponding linear system in
    ``Fraction`` arithmetic. If the system is square and
    full-rank, the rational solution exactly reconstructs ``alpha``.
    Otherwise, fall back to a Decimal-based conversion via
    ``Fraction(Decimal(str(x)))``.
    """
    from decimal import Decimal

    k = len(cert.strategies)
    alpha_arr = np.array(alpha_float)

    # Identify tight constraints: |A row . alpha - 1| < tol
    tight_rows: list[tuple[int, list[Fraction]]] = []
    for v in range(n_vertices):
        if v == cert.root:
            continue
        row = []
        for i, strat in enumerate(cert.strategies):
            row.append(strat.weights.get(v, Fraction(0)))
        lhs = sum((a * float(r) for a, r in zip(alpha_arr, row)), 0.0)
        if abs(lhs - 1.0) < 1e-7:
            tight_rows.append((v, row))

    # Try to find k linearly independent tight rows
    if len(tight_rows) >= k:
        # Greedy linear-independence selection over Fraction arithmetic
        chosen: list[list[Fraction]] = []
        chosen_v: list[int] = []
        for v, row in tight_rows:
            test = chosen + [row]
            if _is_full_rank(test, k):
                chosen = test
                chosen_v.append(v)
            if len(chosen) == k:
                break
        if len(chosen) == k:
            # Solve chosen * alpha = (1, 1, ..., 1) using Fraction Gauss-Jordan
            sys = [list(row) + [Fraction(1)] for row in chosen]
            sol = _gauss_jordan_solve(sys)
            if sol is not None:
                if all(a >= 0 for a in sol):
                    return sol

    # Fallback: decimal conversion
    return [Fraction(Decimal(str(round(a, 12)))) for a in alpha_float]


def _is_full_rank(rows: list[list[Fraction]], k: int) -> bool:
    """Check if a set of rows in Q^k is linearly independent (rank = number of rows)."""
    if not rows:
        return True
    matrix = [list(r) for r in rows]
    n_rows = len(matrix)
    if n_rows > k:
        return False
    # Row-reduce and count pivots
    pivot_col = 0
    pivots = 0
    for r in range(n_rows):
        # Find a non-zero in column pivot_col onwards
        while pivot_col < k:
            pivot_row = None
            for rr in range(r, n_rows):
                if matrix[rr][pivot_col] != 0:
                    pivot_row = rr
                    break
            if pivot_row is None:
                pivot_col += 1
                continue
            if pivot_row != r:
                matrix[r], matrix[pivot_row] = matrix[pivot_row], matrix[r]
            pv = matrix[r][pivot_col]
            for rr in range(r + 1, n_rows):
                if matrix[rr][pivot_col] != 0:
                    factor = matrix[rr][pivot_col] / pv
                    matrix[rr] = [
                        matrix[rr][c] - factor * matrix[r][c] for c in range(k)
                    ]
            pivots += 1
            pivot_col += 1
            break
    return pivots == n_rows


def _gauss_jordan_solve(augmented: list[list[Fraction]]) -> list[Fraction] | None:
    """Solve a k x k linear system in Fraction arithmetic. Augmented is k rows of length k+1."""
    k = len(augmented)
    if k == 0:
        return []
    n_cols = k + 1
    M = [list(r) for r in augmented]
    for r in range(k):
        # Find pivot
        pivot = None
        for rr in range(r, k):
            if M[rr][r] != 0:
                pivot = rr
                break
        if pivot is None:
            return None  # singular
        if pivot != r:
            M[r], M[pivot] = M[pivot], M[r]
        pv = M[r][r]
        M[r] = [x / pv for x in M[r]]
        for rr in range(k):
            if rr == r:
                continue
            f = M[rr][r]
            if f != 0:
                M[rr] = [M[rr][c] - f * M[r][c] for c in range(n_cols)]
    return [row[-1] for row in M]


def optimize_multipliers(cert_path: Path) -> OptResult:
    cert, g = _load_input_certificate(cert_path)
    n = g.n
    k = len(cert.strategies)

    c, A_ub, rhs = _build_lp(cert, n)

    # SciPy linprog with HiGHS
    res = linprog(
        c=c,
        A_ub=A_ub,
        b_ub=rhs,
        bounds=[(0, None)] * k,
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"LP solve failed: {res.message}")

    alpha_float = list(res.x)
    lp_optimum = float(res.fun)

    # Rationalise
    alpha_rational = _rationalize_alpha(alpha_float, cert, n)

    # Check feasibility with rationals: every non-root vertex must satisfy
    # sum_i alpha_i * w_i(v) >= 1.
    binding = []
    for v in range(n):
        if v == cert.root:
            continue
        s = sum(
            (
                a * strat.weights.get(v, Fraction(0))
                for a, strat in zip(alpha_rational, cert.strategies)
            ),
            start=Fraction(0),
        )
        if s == 1:
            binding.append(v)
        elif s < 1:
            raise RuntimeError(
                f"Rationalised alpha violates dual feasibility at v={v}: "
                f"sum = {s} < 1. Float-to-rational conversion was lossy. "
                f"Manual repair needed."
            )

    # Compute exact sum_alpha_b
    b_T_rational: list[Fraction] = []
    for strat in cert.strategies:
        b_T = sum(
            (
                w
                for v, w in strat.weights.items()
                if v != cert.root
            ),
            start=Fraction(0),
        )
        b_T_rational.append(b_T)

    sum_alpha_b = sum(
        (a * b for a, b in zip(alpha_rational, b_T_rational)),
        start=Fraction(0),
    )
    derived_bound = (sum_alpha_b.numerator // sum_alpha_b.denominator) + 1

    # Compare to input's claimed bound
    input_claimed = cert.claimed_bound
    matched = sum_alpha_b == sum(
        (Fraction(str(a)) * b for a, b in zip(cert.dual_multipliers, b_T_rational)),
        start=Fraction(0),
    )

    return OptResult(
        lp_optimum_float=lp_optimum,
        lp_alpha_float=alpha_float,
        alpha_rational=alpha_rational,
        sum_alpha_b_rational=sum_alpha_b,
        derived_bound=derived_bound,
        binding_vertices=binding,
        matched_input_bound=(derived_bound == input_claimed),
        improvement_over_input=input_claimed - derived_bound,
        accepted_by_checker=False,  # to be filled in
    )


def _emit_optimized_certificate(
    cert_path: Path, alpha_rational: list[Fraction], new_bound: int
) -> Path:
    with cert_path.open() as fp:
        payload = json.load(fp)
    payload["claimed_bound"] = new_bound
    payload["dual_multipliers"] = [str(a) for a in alpha_rational]
    payload["notes"] = (
        (payload.get("notes", "") + " ").strip()
        + " Optimized via fixed-strategy master LP "
        "(scripts/optimize_certificate_multipliers.py): rationalised "
        "alpha vector replaces the input multipliers. Derived bound "
        f"floor(sum_i alpha_i b_i) + 1 = {new_bound}."
    )
    out = cert_path.with_name(cert_path.stem + "_optimized.json")
    with out.open("w") as fp:
        json.dump(payload, fp, indent=2)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("certificate", help="path to a certificate JSON")
    ap.add_argument("--emit-optimized", action="store_true", help="write *_optimized.json on improvement")
    args = ap.parse_args()

    cert_path = Path(args.certificate)
    res = optimize_multipliers(cert_path)

    print(f"input certificate: {cert_path}")
    print(f"  LP optimum (float): {res.lp_optimum_float:.6f}")
    print(f"  rationalised alpha: {[str(a) for a in res.alpha_rational]}")
    print(f"  rational sum alpha_i b_i = {res.sum_alpha_b_rational}")
    print(f"  derived bound: {res.derived_bound}")

    cert, g = _load_input_certificate(cert_path)
    if res.improvement_over_input > 0:
        out = _emit_optimized_certificate(cert_path, res.alpha_rational, res.derived_bound)
        print(f"  IMPROVEMENT: derived bound {res.derived_bound} < claimed {cert.claimed_bound}")
        print(f"  wrote optimized certificate: {out}")
        # Re-check
        cert2, g2 = load_certificate_file(out)
        check_res = check_certificate(cert2, g2)
        print(f"  optimized cert checker: accepted={check_res.accepted}, derived={check_res.derived_bound}")
    elif res.derived_bound == cert.claimed_bound:
        print(
            f"  no improvement: LP confirms claimed bound {cert.claimed_bound} is optimal "
            "for this fixed strategy set."
        )
        print(
            "  (By LP duality, the dual primal also has optimum "
            f"{res.sum_alpha_b_rational}, so the bound floor + 1 = "
            f"{res.derived_bound} cannot be tightened from these strategies alone.)"
        )
    else:
        print(
            f"  oddity: LP claims derived bound {res.derived_bound} but input was {cert.claimed_bound}; "
            "investigate before trusting."
        )

    # Number of binding constraints
    print(f"  binding (tight) constraints: {len(res.binding_vertices)} of {g.n - 1}")


if __name__ == "__main__":
    main()
