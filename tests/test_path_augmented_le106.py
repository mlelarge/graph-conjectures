"""Tests for the 106-bound certificate (max_len=7 column generation)."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from check_pebbling_weight_certificate import check_certificate, load_certificate_file


CERT = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "pebbling_product"
    / "certificates"
    / "Hurlbert_path_augmented_v1v1_le106.json"
)


def test_le106_certificate_accepted() -> None:
    cert, g = load_certificate_file(CERT)
    res = check_certificate(cert, g)
    assert res.accepted, res.message
    assert res.derived_bound == 106


def test_le106_sum_alpha_b_below_106() -> None:
    """The exact rationalized LP value must be below 106 for derived bound 106."""
    cert, g = load_certificate_file(CERT)
    res = check_certificate(cert, g)
    sum_ab = Fraction(res.sum_alpha_b)
    assert sum_ab < Fraction(106)
    # Actual value 169327/1600 ~= 105.83
    assert sum_ab == Fraction(169327, 1600)


def test_le106_strict_improvement_over_le107() -> None:
    """The 106 certificate strictly improves the 107 certificate."""
    cert106, g106 = load_certificate_file(CERT)
    res106 = check_certificate(cert106, g106)
    le107 = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "pebbling_product"
        / "certificates"
        / "Hurlbert_path_augmented_v1v1_le107.json"
    )
    cert107, g107 = load_certificate_file(le107)
    res107 = check_certificate(cert107, g107)
    assert res106.derived_bound < res107.derived_bound
