"""Test the column-generation negative result.

No single-anchor BFS shortest-path-tree strategy on L_fpy box L_fpy
lowers the master LP optimum below 107 when added to Hurlbert's four
strategies. This test pins that finding so a future regression --
or a future positive finding -- is loud.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from column_generate_path_strategies import run_column_generation


CERT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "pebbling_product"
    / "certificates"
    / "Hurlbert_T1_T2_T3_T4_v1v1_le108.json"
)


def test_no_single_anchor_path_strategy_improves() -> None:
    summary = run_column_generation(CERT_PATH)
    assert summary["n_candidates"] == 63  # 64 vertices minus root
    assert summary["n_improvements"] == 0
    assert Fraction(summary["best_lp_value"]) == Fraction(107)
