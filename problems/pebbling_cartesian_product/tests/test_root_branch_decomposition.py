"""Tests for root-branch decomposition of Hurlbert strategies."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from check_pebbling_weight_certificate import check_certificate, load_certificate_file
from decompose_root_branches import decompose_certificate, decompose_strategy
from optimize_certificate_multipliers import optimize_multipliers


CERT_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "pebbling_product" / "certificates"
)
INPUT = CERT_DIR / "Hurlbert_T1_T2_T3_T4_v1v1_le108.json"
DECOMPOSED = CERT_DIR / "Hurlbert_decomposed_branches_v1v1.json"


def test_decomposition_produces_six_branch_columns() -> None:
    """T_1 and T_2 each have two root-children, T_3 and T_4 each have one,
    so decomposition produces 2+2+1+1 = 6 branch columns."""
    with INPUT.open() as fp:
        payload = json.load(fp)
    out = decompose_certificate(payload)
    assert len(out["strategies"]) == 6


def test_decomposed_certificate_passes_rational_checker() -> None:
    """Each branch column on its own is a valid Hurlbert nonbasic strategy;
    the rational checker accepts the decomposed certificate."""
    cert, g = load_certificate_file(DECOMPOSED)
    res = check_certificate(cert, g)
    assert res.accepted, res.message
    # Sum of b_T's across branches still equals 4 * 107 = 428
    bs = [Fraction(s["b_T"]) for s in res.extra["per_strategy"]]
    assert sum(bs) == 428


def test_decomposition_does_not_improve_LP() -> None:
    """Branch decomposition allows the LP to assign different alpha to
    different branches, but the LP optimum stays at 107: the original
    uniform-alpha solution is still optimal under decomposition."""
    res = optimize_multipliers(DECOMPOSED)
    assert res.derived_bound == 108
    assert res.sum_alpha_b_rational == Fraction(107)
    # Uniform alpha = 1/4 across all 6 branches recovers the original
    # 4-strategy contributions
    assert all(a == Fraction(1, 4) for a in res.alpha_rational)


def test_branch_b_T_values() -> None:
    """The expected per-branch b_T values from the inspection."""
    cert, g = load_certificate_file(DECOMPOSED)
    res = check_certificate(cert, g)
    bs = sorted(int(Fraction(s["b_T"])) for s in res.extra["per_strategy"])
    # 2 branches of T_1 (b 85, 15), 2 of T_2 (b 95, 19), single T_3 (102), T_4 (112)
    assert bs == [15, 19, 85, 95, 102, 112]
