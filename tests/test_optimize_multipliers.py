"""Tests for scripts/optimize_certificate_multipliers.py."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from optimize_certificate_multipliers import optimize_multipliers


CERT_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "pebbling_product" / "certificates"
)


def test_hurlbert_four_strategy_alpha_is_optimal() -> None:
    """The published uniform alpha = (1/4, 1/4, 1/4, 1/4) is LP-optimal for the
    four Hurlbert strategies; sum_alpha_b = 107 cannot be tightened by
    reweighting alone."""
    res = optimize_multipliers(CERT_DIR / "Hurlbert_T1_T2_T3_T4_v1v1_le108.json")
    assert res.derived_bound == 108
    assert res.sum_alpha_b_rational == Fraction(107)
    assert all(a == Fraction(1, 4) for a in res.alpha_rational)
    assert res.improvement_over_input == 0


def test_hurlbert_lp_has_many_tight_constraints() -> None:
    """Of 63 non-root vertices, many constraints are tight under uniform alpha;
    this is structural evidence that the four-strategy averaging is well-tuned."""
    res = optimize_multipliers(CERT_DIR / "Hurlbert_T1_T2_T3_T4_v1v1_le108.json")
    # The 51 vertices with T_avg = 1 give tight constraints
    assert len(res.binding_vertices) == 51


def test_C4_two_strategy_alpha() -> None:
    """The synthetic C_4 multi-strategy cert has uniform alpha = (1/4, 1/4) and
    sum = 7/2; LP should not improve it (matches the trivial lower bound)."""
    res = optimize_multipliers(CERT_DIR / "C4_root0_le4.json")
    assert res.derived_bound == 4
    # Two strategies, sum alpha_b = 7/2
    assert res.sum_alpha_b_rational == Fraction(7, 2)
