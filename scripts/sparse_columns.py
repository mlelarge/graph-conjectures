"""Sparse column representation and LP harness for column generation.

Replaces the JSON-roundtrip pipeline used by run_column_generation.py.
A `StrategyColumn` is a single Hurlbert basic / nonbasic strategy
expressed as:

- a sparse weight vector (vertex -> Fraction);
- (optional) tree edges, for round-trip into the rational checker;
- (optional) provenance metadata.

The master LP and dual extraction routines consume an iterable of
StrategyColumns; nothing serializes through JSON until a final
certificate is emitted via :func:`emit_certificate`.

This module is intentionally thin: it does not enumerate columns or
implement pricing -- those live in :mod:`price_tree_strategy` and
:mod:`run_sparse_column_generation`. Here we only define the data
type and the LP wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import linprog


@dataclass
class StrategyColumn:
    """One Hurlbert strategy: sparse weights + tree edges + metadata."""

    weights: dict[int, Fraction]
    tree_edges: list[tuple[int, int]] = field(default_factory=list)
    name: str = ""
    basic: bool = False
    source: str = ""

    @property
    def b(self) -> Fraction:
        """Sum of weights on non-root vertices.

        We do not know the root from a column alone, but the column
        carries weight 0 (or absence) at the root and positive weights
        elsewhere. So summing all weight values gives sum_{v != r} w(v)
        as long as the root weight is 0 / absent.
        """
        return sum(self.weights.values(), start=Fraction(0))

    def support(self) -> set[int]:
        return {v for v, w in self.weights.items() if w != 0}


def lp_from_columns(
    columns: Sequence[StrategyColumn],
    n_vertices: int,
    root: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build a sparse LP min c^T alpha s.t. -A alpha <= -1, alpha >= 0.

    Returns ``(c, A_ub, b_ub)`` ready for ``scipy.optimize.linprog``.
    """
    k = len(columns)
    c = np.zeros(k, dtype=float)
    for i, col in enumerate(columns):
        c[i] = float(col.b)
    A_ub = np.zeros((n_vertices - 1, k), dtype=float)
    rhs = np.full(n_vertices - 1, -1.0)
    row = 0
    for v in range(n_vertices):
        if v == root:
            continue
        for i, col in enumerate(columns):
            w = col.weights.get(v, Fraction(0))
            A_ub[row, i] = -float(w)
        row += 1
    return c, A_ub, rhs


def solve_master_lp(
    columns: Sequence[StrategyColumn],
    n_vertices: int,
    root: int,
    method: str = "highs-ds",
) -> tuple[float, np.ndarray, np.ndarray]:
    """Solve the master LP and return (optimum, alpha, dual_y).

    ``dual_y`` is the LP dual: y_v is the multiplier on the
    sum_i alpha_i T_i(v) >= 1 constraint (non-negative). v is indexed
    over non-root vertices in increasing order.
    """
    c, A_ub, rhs = lp_from_columns(columns, n_vertices, root)
    if not columns:
        return float("inf"), np.zeros(0), np.zeros(n_vertices - 1)
    res = linprog(
        c=c, A_ub=A_ub, b_ub=rhs,
        bounds=[(0, None)] * len(c),
        method=method,
    )
    if not res.success:
        raise RuntimeError(f"LP solve failed: {res.message}")
    alpha = np.array(res.x)
    # ineqlin.marginals are signed; for -A alpha <= -1 the LP gives
    # dual variables that are negated on entry, so the real y_v = -marginal.
    y = -np.array(res.ineqlin.marginals)
    return float(res.fun), alpha, y


def reduced_cost(column: StrategyColumn, y: np.ndarray, root: int, n_vertices: int) -> Fraction:
    """Reduced cost b_T - y . w_T (negative => column improves the LP)."""
    s = Fraction(0)
    j = 0
    for v in range(n_vertices):
        if v == root:
            continue
        w = column.weights.get(v, Fraction(0))
        if w != 0:
            # y is float; use float * Fraction = float, then convert
            # back conservatively. For pricing we want a quick float
            # estimate; the rational LP check happens later.
            s += Fraction(int(round(float(y[j]) * 10**12)), 10**12) * w
        j += 1
    return column.b - s


def emit_certificate(
    columns: Sequence[StrategyColumn],
    alpha: list[Fraction],
    *,
    graph_payload: dict,
    root: int,
    notes: str = "",
) -> dict:
    """Build a certificate JSON payload from selected columns and rational alpha."""
    if len(columns) != len(alpha):
        raise ValueError(
            f"len(columns) {len(columns)} != len(alpha) {len(alpha)}"
        )
    sum_ab = sum((a * c.b for a, c in zip(alpha, columns)), start=Fraction(0))
    derived = sum_ab.numerator // sum_ab.denominator + 1
    return {
        "graph": graph_payload,
        "root": root,
        "claimed_bound": derived,
        "strategies": [
            {
                "name": col.name,
                "tree_edges": [list(e) for e in col.tree_edges],
                "weights": {str(k): str(v) for k, v in col.weights.items()},
                "basic": col.basic,
            }
            for col in columns
        ],
        "dual_multipliers": [str(a) for a in alpha],
        "notes": notes,
    }
