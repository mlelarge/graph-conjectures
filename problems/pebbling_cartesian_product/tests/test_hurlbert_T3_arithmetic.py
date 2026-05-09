"""Arithmetic-only tests for Hurlbert's averaged T_3 matrix.

These tests verify that the 8x8 matrix transcribed in
``data/pebbling_product/certificates/Hurlbert_T3_v1v1_arithmetic.json``
satisfies the arithmetic conditions of Hurlbert 2017 Theorem 10
(arXiv:1101.5641, J. Combinatorial Optimization 34(2), 343-361):

- root entry is 0,
- every other entry is at least 1,
- non-root sum is 107,
- derived bound floor(107) + 1 = 108.

They do **not** test that T_3 is the average of four valid basic Hurlbert
tree strategies; that would require transcribing Figure 5 of the paper.
This is an arithmetic reproduction, not an independent certificate.
"""

from __future__ import annotations

import copy

import pytest

from check_hurlbert_T3_arithmetic import (
    DEFAULT_MATRIX_PATH,
    check_T3_arithmetic,
    load_T3_matrix,
)


def test_T3_arithmetic_matches_paper() -> None:
    matrix = load_T3_matrix(DEFAULT_MATRIX_PATH)
    res = check_T3_arithmetic(matrix)
    assert res.accepted, res.failures
    assert res.matrix_shape == (8, 8)
    assert res.root_weight == 0
    assert res.minimum_non_root_weight >= 1
    assert res.sum_non_root_weights == 107
    assert res.derived_bound == 108


def test_T3_rejects_perturbed_root() -> None:
    matrix = load_T3_matrix(DEFAULT_MATRIX_PATH)
    matrix[0][0] = 1  # root weight should be 0
    res = check_T3_arithmetic(matrix)
    assert not res.accepted
    assert any("T_3[0][0]" in f for f in res.failures)


def test_T3_rejects_zero_non_root_entry() -> None:
    matrix = load_T3_matrix(DEFAULT_MATRIX_PATH)
    matrix[5][5] = 0  # was 1; setting to 0 violates dual feasibility
    res = check_T3_arithmetic(matrix)
    assert not res.accepted
    assert any("< 1" in f for f in res.failures)


def test_T3_rejects_wrong_sum() -> None:
    matrix = load_T3_matrix(DEFAULT_MATRIX_PATH)
    matrix[1][1] += 1  # bumps sum from 107 to 108
    res = check_T3_arithmetic(matrix)
    assert not res.accepted
    assert any("expected 107" in f for f in res.failures)


def test_T3_rejects_wrong_shape() -> None:
    matrix = [[0] * 8 for _ in range(7)]  # 7 rows, not 8
    res = check_T3_arithmetic(matrix)
    assert not res.accepted
    assert any("8x8" in f for f in res.failures)


def test_T3_label_is_explicit() -> None:
    """The label must call this an arithmetic reproduction, not a certificate."""
    matrix = load_T3_matrix(DEFAULT_MATRIX_PATH)
    res = check_T3_arithmetic(matrix)
    assert "arithmetic reproduction" in res.label.lower()
    assert "not an independent certificate" in res.label.lower()
