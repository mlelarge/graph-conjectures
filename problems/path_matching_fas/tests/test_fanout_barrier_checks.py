"""Regression tests for the Fanout Barrier checks (D75).

Pins the load-bearing computational claims of
`docs/fanout_barrier_theorem.md`:

  * No faithful free-bit splitter exists at n <= 7 for k in {2, 3}:
    no gadget realizes EQ_k as R_T with joint capacity on BOTH
    equality vectors.  (Theorem, verified exhaustively over iso-reps.)
  * Capacity on one equality vector forces R_T != EQ_k: every
    capacity-on-v witness co-realizes a mixed vector or misses the
    opposite equality vector (the two-value competition engine).
  * The internal-arc back-arc dictionary: each port's tournament arc is
    a back-arc on EXACTLY ONE of the two equality LFOs (0 mismatches).
  * The EQ_3 -> EQ_2 reduction premise (no EQ_2 faithful copy => no
    EQ_3 faithful splitter).

The n=7 cases use the 456 iso-class representatives; they are the
slow tests and are kept minimal.
"""
from __future__ import annotations

import os
import sys

import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fanout_barrier_checks import (  # noqa: E402
    check_capacity_forces_non_equality,
    check_equality_deficit_profile,
    check_internal_arc_accounting,
    check_no_faithful_splitter,
)


def test_no_faithful_splitter_k2_small():
    """EQ_2 copies appear at n=6 (4 of them) but none has capacity on
    both values; n<=5 has no EQ_2 gadget at all."""
    assert check_no_faithful_splitter(5, 2)["eq_gadgets"] == 0
    r6 = check_no_faithful_splitter(6, 2)
    assert r6["eq_gadgets"] == 4
    assert r6["faithful_splitters"] == 0
    assert r6["eq_with_capacity_on_zero"] == 1
    assert r6["eq_with_capacity_on_one"] == 1


def test_no_faithful_splitter_k3_n6():
    """No EQ_3 gadget at n=6 (need n>=7)."""
    r = check_no_faithful_splitter(6, 3)
    assert r["eq_gadgets"] == 0
    assert r["faithful_splitters"] == 0


@pytest.mark.slow
def test_no_faithful_splitter_k2_n7():
    r = check_no_faithful_splitter(7, 2)
    assert r["eq_gadgets"] == 660
    assert r["eq_with_capacity_on_zero"] == 16
    assert r["eq_with_capacity_on_one"] == 16
    assert r["faithful_splitters"] == 0


@pytest.mark.slow
def test_no_faithful_splitter_k3_n7():
    """The headline: at n=7, EQ_3 gadgets exist (62) but have capacity on
    NEITHER equality value -- strictly stronger than 'no splitter'."""
    r = check_no_faithful_splitter(7, 3)
    assert r["eq_gadgets"] == 62
    assert r["eq_with_capacity_on_zero"] == 0
    assert r["eq_with_capacity_on_one"] == 0
    assert r["faithful_splitters"] == 0


@pytest.mark.slow
def test_capacity_forces_non_equality_k3_n7():
    r = check_capacity_forces_non_equality(7, 3)["by_value"]
    for label in ("zero", "one"):
        d = r[label]
        assert d["capacity_witnesses"] == 17281
        assert d["with_R_eq_EQ"] == 0          # never EQ_3 with capacity
        assert d["with_a_mixed_vector"] == 17192
        assert d["missing_opposite_equality_vector"] == 89


@pytest.mark.slow
def test_equality_deficit_profile_k3_n7():
    r = check_equality_deficit_profile(7, 3)
    assert r["eq_gadgets"] == 62
    assert r["min_saturated_on_zero"] == 2
    assert r["min_saturated_on_one"] == 2
    assert r["min_combined_deficit"] == 6


@pytest.mark.slow
def test_internal_arc_dictionary_k3_n7():
    """Each port's tournament arc is a back-arc on exactly one of the two
    equality LFOs: 0 mismatches over ~1.1M port instances, and the count
    splits exactly 50/50."""
    r = check_internal_arc_accounting(7, 3)
    assert r["ports_where_both_eq_LFOs_share_internal_backarc_status"] == 0
    assert r["internal_backarc_on_one_LFO"] == r["internal_backarc_on_zero_LFO"]


def test_internal_arc_dictionary_k2_n6():
    """Fast version of the internal-arc dictionary at n=6, k=2."""
    r = check_internal_arc_accounting(6, 2)
    assert r["ports_where_both_eq_LFOs_share_internal_backarc_status"] == 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
