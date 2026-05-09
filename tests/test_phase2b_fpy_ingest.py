"""Smoke tests for the FPY-ingestion adapter.

These tests use small inline CSVs (not the full FPY data) to confirm
that the parser handles the file format and reports warnings about
non-dyadic weights, invalid headers, and missing rows.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from ingest_flocco_pulaj_yerger import (
    _decimal_to_fraction,
    _parse_pair,
    parse_edges_csv,
    parse_weight_csv,
)


def test_decimal_to_fraction_exact_for_dyadic() -> None:
    assert _decimal_to_fraction("1.75") == Fraction(7, 4)
    assert _decimal_to_fraction("3.25") == Fraction(13, 4)
    assert _decimal_to_fraction("16.0") == Fraction(16, 1)
    assert _decimal_to_fraction("0") == Fraction(0)


def test_decimal_to_fraction_for_rounded_lp_value() -> None:
    """31.56 -> 789/25: exact for the rounded value, but non-dyadic."""
    f = _decimal_to_fraction("31.56")
    assert f == Fraction(789, 25)
    assert f.denominator == 25


def test_parse_pair() -> None:
    assert _parse_pair("(0, 1)") == (0, 1)
    assert _parse_pair("(7, 3)") == (7, 3)
    assert _parse_pair(" (2, 5) ") == (2, 5)


def test_parse_pair_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        _parse_pair("0,1")
    with pytest.raises(ValueError):
        _parse_pair("(0)")


def test_parse_weight_csv_handles_full_grid() -> None:
    # Tiny 2x2 grid. Cell (0,1)=1.0, (1,0)=2.0; rest zero. h_n=2.
    text = ",0,1\n0,0.0,1.0\n1,2.0,0.0\n"
    weights, warnings = parse_weight_csv(text, h_n=2)
    # pair_to_index(0,1,2) = 1, pair_to_index(1,0,2) = 2
    assert weights == {1: Fraction(1), 2: Fraction(2)}
    assert warnings == []


def test_parse_weight_csv_warns_on_non_dyadic() -> None:
    text = ",0,1\n0,0.0,31.56\n1,0.0,0.0\n"
    weights, warnings = parse_weight_csv(text, h_n=2)
    assert weights == {1: Fraction(789, 25)}
    assert any("non-dyadic" in w for w in warnings)


def test_parse_edges_csv_basic() -> None:
    # 2x2 grid; encode an edge (0,0)-(0,1) -> flat 0-1.
    text = ',0,1\n0,"(0, 0)","(0, 1)"\n1,"(1, 0)","(1, 1)"\n'
    edges, warnings = parse_edges_csv(text, h_n=2)
    # Edges are (min, max) flat-index pairs; 0=>(0,0), 1=>(0,1),
    # 2=>(1,0), 3=>(1,1).
    assert edges == [(0, 1), (2, 3)]
    assert warnings == []


def test_parse_edges_csv_rejects_self_loop() -> None:
    text = ',0,1\n0,"(1, 1)","(1, 1)"\n'
    edges, warnings = parse_edges_csv(text, h_n=2)
    assert edges == []
    assert any("self-loop" in w for w in warnings)
