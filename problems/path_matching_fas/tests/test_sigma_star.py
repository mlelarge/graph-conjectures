"""Regression tests for the symbolic sigma*(k) universal repair suffix (D60).

These tests verify three properties:

  1. Closed-form == recursive characterizations agree.
  2. The closed-form output matches the tracer at small k (cached from
     the FF-tracer mined data).
  3. The FF tracer agrees that sigma*(k) is the completing suffix on
     every extendable V6''-negative cyclic-ladder core at k = 2, 4, 5, 6.
     (k = 3 has zero V6''-negative cores; the formula is well-defined
     but vacuous.)
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from sigma_star_formula import (  # noqa: E402
    closed_equals_recursive,
    sigma_star_closed,
    sigma_star_recursive,
    sigma_star_symbolic_closed,
    verify_matches_tracer,
)


# ----------------------------------------------------------------------
# 1. Closed-form == recursive
# ----------------------------------------------------------------------

def test_closed_equals_recursive_up_to_k15():
    """sigma*(k) by closed-form and by recursion agree for k = 2..15."""
    result = closed_equals_recursive(15)
    assert result["all_agree"], result


# ----------------------------------------------------------------------
# 2. Known small-k values (cached from FF tracer output)
# ----------------------------------------------------------------------

def test_sigma_star_k2_matches_tracer_cache():
    # FF tracer at k=2: suffix = [6, 5, 7, 9, 8].
    assert sigma_star_closed(2) == [6, 5, 7, 9, 8]


def test_sigma_star_k4_matches_tracer_cache():
    # FF tracer at k=4: suffix = [10, 9, 12, 11, 13, 15, 14, 17, 16].
    assert sigma_star_closed(4) == [10, 9, 12, 11, 13, 15, 14, 17, 16]


def test_sigma_star_k7_matches_tracer_cache():
    # FF tracer at k=7: swap lower endpoints {0, 2, 4, 6, 8, 10, 12}
    # applied to canonical [15, 16, 17, ..., 29].
    canonical = [2 * 7 + 1] + [2 * 7 + 2 + i for i in range(7)] + [3 * 7 + 2 + i for i in range(7)]
    expected = list(canonical)
    for lo in [0, 2, 4, 6, 8, 10, 12]:
        expected[lo], expected[lo + 1] = expected[lo + 1], expected[lo]
    assert sigma_star_closed(7) == expected


def test_sigma_star_k8_matches_tracer_cache():
    # FF tracer at k=8: swap lower endpoints {0, 2, 4, 6, 9, 11, 13, 15}.
    canonical = [2 * 8 + 1] + [2 * 8 + 2 + i for i in range(8)] + [3 * 8 + 2 + i for i in range(8)]
    expected = list(canonical)
    for lo in [0, 2, 4, 6, 9, 11, 13, 15]:
        expected[lo], expected[lo + 1] = expected[lo + 1], expected[lo]
    assert sigma_star_closed(8) == expected


# ----------------------------------------------------------------------
# 3. Symbolic structure checks
# ----------------------------------------------------------------------

def test_sigma_star_length_2k_plus_1():
    for k in range(2, 13):
        assert len(sigma_star_symbolic_closed(k)) == 2 * k + 1


def test_sigma_star_starts_with_A0_r():
    for k in range(2, 13):
        sym = sigma_star_symbolic_closed(k)
        assert sym[0] == ('A', 0)
        assert sym[1] == ('r',)


def test_sigma_star_covers_all_suffix_vertices():
    """Each suffix vertex appears exactly once in sigma*(k)."""
    for k in range(2, 13):
        sym = sigma_star_symbolic_closed(k)
        labels = sorted(sym)
        expected = sorted(
            [('r',)]
            + [('A', i) for i in range(k)]
            + [('B', i) for i in range(k)]
        )
        assert labels == expected, (k, labels)


def test_sigma_star_a_block_position():
    """Positions 0..k hold the A-block + r."""
    for k in range(2, 13):
        sym = sigma_star_symbolic_closed(k)
        a_block = sym[:k + 1]
        a_labels = sorted(a_block)
        expected = sorted([('r',)] + [('A', i) for i in range(k)])
        assert a_labels == expected


def test_sigma_star_b_block_position():
    """Positions k+1..2k hold the B-block."""
    for k in range(2, 13):
        sym = sigma_star_symbolic_closed(k)
        b_block = sym[k + 1:]
        b_labels = sorted(b_block)
        expected = sorted([('B', i) for i in range(k)])
        assert b_labels == expected


def test_sigma_star_disjoint_adjacent_swaps_from_canonical():
    """sigma*(k) differs from canonical [r, A_0..A_{k-1}, B_0..B_{k-1}]
    by exactly k disjoint adjacent transpositions."""
    for k in range(2, 13):
        sym = sigma_star_symbolic_closed(k)
        canonical = [('r',)] + [('A', i) for i in range(k)] + [('B', i) for i in range(k)]
        n_swaps = 0
        i = 0
        while i < len(sym):
            if sym[i] == canonical[i]:
                i += 1
                continue
            assert i + 1 < len(sym)
            assert sym[i] == canonical[i + 1]
            assert sym[i + 1] == canonical[i]
            n_swaps += 1
            i += 2
        assert n_swaps == k, (k, n_swaps)


# ----------------------------------------------------------------------
# 4. Tracer agreement (slow; only on small k)
# ----------------------------------------------------------------------

@pytest.mark.slow
def test_sigma_star_matches_tracer_at_k2():
    out = verify_matches_tracer(2)
    assert out["sigma_star_holds_on_extendable"], out


@pytest.mark.slow
def test_sigma_star_matches_tracer_at_k4():
    out = verify_matches_tracer(4)
    assert out["sigma_star_holds_on_extendable"], out


@pytest.mark.slow
def test_sigma_star_matches_tracer_at_k5():
    out = verify_matches_tracer(5)
    assert out["sigma_star_holds_on_extendable"], out


@pytest.mark.slow
def test_sigma_star_matches_tracer_at_k6():
    out = verify_matches_tracer(6)
    assert out["sigma_star_holds_on_extendable"], out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
