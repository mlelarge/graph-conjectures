"""Tests for the path-augmented certificate that improves Hurlbert's 108 to 107."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from check_pebbling_weight_certificate import check_certificate, load_certificate_file


CERT_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "pebbling_product" / "certificates"
)
PATH_CERT = CERT_DIR / "Hurlbert_path_augmented_v1v1_le107.json"


def test_path_augmented_certificate_accepted() -> None:
    """The persisted column-generation certificate is rationally checked
    and gives derived bound 107, beating Hurlbert's 108."""
    cert, g = load_certificate_file(PATH_CERT)
    res = check_certificate(cert, g)
    assert res.accepted, res.message
    assert res.derived_bound == 107
    assert res.claimed_bound == 107


def test_path_augmented_sum_alpha_b_is_47021_over_440() -> None:
    """The exact rational LP optimum is 47021/440 ~= 106.866, hence
    derived bound = floor(47021/440) + 1 = 107."""
    cert, g = load_certificate_file(PATH_CERT)
    res = check_certificate(cert, g)
    assert Fraction(res.sum_alpha_b) == Fraction(47021, 440)


def test_path_augmented_strictly_below_107() -> None:
    """The LP optimum 47021/440 is strictly less than 107; otherwise the
    derived bound would still be 108."""
    cert, g = load_certificate_file(PATH_CERT)
    res = check_certificate(cert, g)
    assert Fraction(res.sum_alpha_b) < Fraction(107)
