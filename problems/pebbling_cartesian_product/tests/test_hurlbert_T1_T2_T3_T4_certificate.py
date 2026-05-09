"""Phase 2b reproduction test: Hurlbert WFL Theorem 10 four-strategy certificate.

Loads the persisted four-strategy certificate transcribed from Hurlbert's
*The weight function lemma for graph pebbling*, J. Combinatorial
Optimization 34(2) (2017), 343-361 (arXiv:1101.5641), Theorem 10,
Figure 5, and rationally verifies the derived bound matches the
published 108 via the same rational checker that handles the synthetic
Phase 2a smoke tests.

This is a full rational certificate (not arithmetic-only): the tree
structure of each of the four strategies is encoded, and the parent-
doubling inequalities are checked entry by entry. Cross-checked against
the average matrix sum 107 and the per-strategy weight totals.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from check_pebbling_weight_certificate import (
    check_certificate,
    load_certificate_file,
)


CERT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "pebbling_product"
    / "certificates"
    / "Hurlbert_T1_T2_T3_T4_v1v1_le108.json"
)


def test_hurlbert_T1_T2_T3_T4_certificate_accepted() -> None:
    cert, g = load_certificate_file(CERT_PATH)
    res = check_certificate(cert, g)
    assert res.accepted, res.message
    assert res.derived_bound == 108
    assert res.claimed_bound == 108


def test_hurlbert_certificate_has_four_strategies() -> None:
    cert, _ = load_certificate_file(CERT_PATH)
    assert len(cert.strategies) == 4
    # Uniform alpha = 1/4
    from fractions import Fraction
    assert all(a == Fraction(1, 4) for a in cert.dual_multipliers)


def test_hurlbert_certificate_sum_alpha_b_is_107() -> None:
    """Average matrix has sum 107, so sum_i (1/4) b_i = (1/4) sum b_i = 107."""
    cert, g = load_certificate_file(CERT_PATH)
    res = check_certificate(cert, g)
    from fractions import Fraction
    # res.sum_alpha_b is a string repr of a Fraction
    assert Fraction(res.sum_alpha_b) == Fraction(107)


def test_hurlbert_certificate_per_strategy_b_T_sum_to_428() -> None:
    """The four strategies' b_T values sum to 4 * 107 = 428 by construction."""
    cert, g = load_certificate_file(CERT_PATH)
    res = check_certificate(cert, g)
    from fractions import Fraction
    bs = [Fraction(s["b_T"]) for s in res.extra["per_strategy"]]
    assert sum(bs) == 428
