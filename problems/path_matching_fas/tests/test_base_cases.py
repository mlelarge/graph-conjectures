"""Regression tests for D58 symbolic base cases of Mixed-Parity Escape.

Each test row of the D58 m=1, m=2, m=3 parity/trigger enumeration is
exercised here via:
  * `predict_v6pp` (V6'' classifier from D49) for the V6'' verdict;
  * `verify_completion_exists` (FF backtracker from D54) for
    extendability of V6''-negative cyclic-ladder cores;
  * a sub-core descent enumeration for non-minimal-fatal cases (O2 of
    Lemma 55.1).

Final sweep test (`test_d58_base_case_exhaustive_k_leq_7`) is the
load-bearing assertion: every V6''-negative cyclic-ladder core of
size 2m, m in {1, 2, 3}, at every k in {3, ..., 7}, is either
extendable or contains a V6''-positive proper sub-core.  Zero
counterexamples expected.
"""
from __future__ import annotations

import os
import sys
from itertools import combinations, permutations

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from rectangle_detachability_probe import (  # noqa: E402
    even_adjacent_blocks,
)
from v6pp_completion_constructor import (  # noqa: E402
    is_cyclic_ladder_core,
    verify_completion_exists,
)
from v6pp_predictor import predict_v6pp  # noqa: E402


# -------------------------------------------------------------------
# m = 1 rows (size-2 cyclic ladder; single block; one image interval)
# -------------------------------------------------------------------

def test_d58_m1_row_1_2_a_odd_P3_fires():
    """Row 1.2 (m=1, a odd / NaturalOddStart, P3 fires).

    k=4, pi=(1,2,0,3), C={0,1}: image {1,2}, a=1 odd; filler pi(3)=3>2
    -> P3 fires.  Predictor: minimal_fatal (P3).
    """
    pred = predict_v6pp(4, (1, 2, 0, 3), (0, 1))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3"
    assert pred["natural_odd_start"] is True


def test_d58_m1_row_1_3_a_odd_P3prime_NOS():
    """Row 1.3 (m=1, a odd, P3' ∧ NaturalOddStart, k odd).

    k=5, pi=(0,1,3,4,2), C={2,3}: image {3,4}, a=3 odd; lone filler
    k-1=4 has pi(4)=2 < 3.  Predictor: minimal_fatal (P3' ∧ NOS).
    """
    pred = predict_v6pp(5, (0, 1, 3, 4, 2), (2, 3))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3prime_and_natural_odd_start"
    assert pred["natural_odd_start"] is True


def test_d58_m1_row_1_4_a_even_extendable():
    """Row 1.4 (m=1, a even, no P3): the F1 base case.  Extendable.

    k=6, pi=identity, C={4,5}: image {4,5}, a=4 even; all filler
    images <= 5 (no P3); k=6 even, no P3' possible.  Predictor:
    not_minimal_fatal.  Mixed parity at m=1 -> extendable.
    """
    pred = predict_v6pp(6, (0, 1, 2, 3, 4, 5), (4, 5))
    assert pred["prediction"] == "not_minimal_fatal"
    assert pred["natural_odd_start"] is False
    assert is_cyclic_ladder_core(6, (0, 1, 2, 3, 4, 5), (4, 5))
    assert verify_completion_exists(6, (0, 1, 2, 3, 4, 5), (4, 5))


def test_d58_m1_row_1_4_second_witness():
    """Row 1.4 second example: k=4 pi=(2,3,1,0), C={0,1}.

    Image {2,3}, a=2 even; filler images {0,1} <= 3 (no P3); k=4 even
    (no P3').  Predictor: not_minimal_fatal; extendable.
    """
    pred = predict_v6pp(4, (2, 3, 1, 0), (0, 1))
    assert pred["prediction"] == "not_minimal_fatal"
    assert pred["natural_odd_start"] is False
    assert verify_completion_exists(4, (2, 3, 1, 0), (0, 1))


def test_d58_m1_row_1_5_a_even_P3_fires():
    """Row 1.5 (m=1, a even, P3 fires).

    k=4, pi=(0,1,2,3), C={0,1}: image {0,1}, a=0 even; pi(2)=2>1, pi(3)=3>1
    -> P3 fires.  Predictor: minimal_fatal (P3).
    """
    pred = predict_v6pp(4, (0, 1, 2, 3), (0, 1))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3"
    assert pred["natural_odd_start"] is False


def test_d58_m1_row_1_1_vacuous():
    """Row 1.1 (m=1, a odd, no P3, no P3') is vacuous.

    Exhaustive sweep at k <= 7: no cyclic-ladder core C of size 2
    satisfies natural_odd_start=True AND V6''(C)=not_minimal_fatal.
    """
    found = []
    for k in [3, 4, 5, 6, 7]:
        for blk in even_adjacent_blocks(k):
            for pi in permutations(range(k)):
                C = blk
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                pred = predict_v6pp(k, pi, C)
                if pred["prediction"] == "not_minimal_fatal" and pred["natural_odd_start"]:
                    found.append((k, pi, C))
    assert found == [], f"row 1.1 should be vacuous but found {found[:3]}"


# -------------------------------------------------------------------
# m = 2 rows (size-4 cyclic ladder; two blocks; two image intervals)
# -------------------------------------------------------------------

def test_d58_m2_row_2_1_P4_NOS():
    """Row 2.1 (m=2, both intervals odd-start, P4 fires).

    k=7, pi=(1,5,2,6,0,3,4), C={0,1,2,3}: image {1,2,5,6}, both
    intervals odd-start, no P3/P3' -> P4 fires.
    """
    pred = predict_v6pp(7, (1, 5, 2, 6, 0, 3, 4), (0, 1, 2, 3))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P4_natural_odd_start_residual"
    assert pred["natural_odd_start"] is True


def test_d58_m2_row_2_3_P3prime_NOS():
    """Row 2.3 (m=2, NOS, P3' fires at odd k).

    k=5, pi=(1,3,2,4,0), C={0,1,2,3}: image {1,2,3,4}, both intervals
    odd-start; lone filler k-1=4 has pi(4)=0 < 1.  P3' ∧ NOS fires.
    """
    pred = predict_v6pp(5, (1, 3, 2, 4, 0), (0, 1, 2, 3))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3prime_and_natural_odd_start"
    assert pred["natural_odd_start"] is True


def test_d58_m2_row_2_4_mixed_extendable_k4():
    """Row 2.4 (m=2, mixed parity, no trigger): extendable.

    k=4, pi=(0,2,1,3), C={0,1,2,3}: image {0,1,2,3} = {0,1}+{2,3};
    intervals (0,1) and (2,3) — both even-start.  No P3 (filler set
    empty at k=4); no P3' (k even); no P4 (NOS fails).
    Predictor: not_minimal_fatal; extendable.
    """
    pred = predict_v6pp(4, (0, 2, 1, 3), (0, 1, 2, 3))
    assert pred["prediction"] == "not_minimal_fatal"
    assert pred["natural_odd_start"] is False
    assert is_cyclic_ladder_core(4, (0, 2, 1, 3), (0, 1, 2, 3))
    assert verify_completion_exists(4, (0, 2, 1, 3), (0, 1, 2, 3))


def test_d58_m2_row_2_4_mixed_extendable_k7():
    """Row 2.4 at k=7: pi=(0,5,1,6,2,3,4), C={0,1,2,3}.

    Image {0,1,5,6} = {0,1}+{5,6}; first interval a_0=0 even, second
    a_1=5 odd — mixed parity.  No P3 (high=6, max filler image is 4),
    no P3' (NOS fails so the conjunction is false), no P4.
    Predictor: not_minimal_fatal; extendable.
    """
    pred = predict_v6pp(7, (0, 5, 1, 6, 2, 3, 4), (0, 1, 2, 3))
    assert pred["prediction"] == "not_minimal_fatal"
    assert pred["natural_odd_start"] is False
    assert verify_completion_exists(7, (0, 5, 1, 6, 2, 3, 4), (0, 1, 2, 3))


def test_d58_m2_row_2_5_P3_fires():
    """Row 2.5 (m=2, mixed parity, P3 fires).

    k=5, pi=(0,2,1,3,4), C={0,1,2,3}: image {0,1,2,3}; pi(4)=4 > 3
    -> P3 fires.
    """
    pred = predict_v6pp(5, (0, 2, 1, 3, 4), (0, 1, 2, 3))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3"


# -------------------------------------------------------------------
# m = 3 rows (size-6 cyclic ladder; three blocks; three image intervals)
# -------------------------------------------------------------------

def test_d58_m3_row_3_3_P3prime_NOS():
    """Row 3.3 (m=3, all odd-start, P3' fires at odd k).

    User's pinned k=7 size-6 example: pi=(5,4,6,1,3,2,0), C={0..5}.
    Intervals {1,2},{3,4},{5,6} all odd-start; lone filler 6 has
    pi(6)=0 < 1 -> P3' ∧ NOS fires.
    """
    pred = predict_v6pp(7, (5, 4, 6, 1, 3, 2, 0), (0, 1, 2, 3, 4, 5))
    assert pred["prediction"] == "minimal_fatal"
    assert pred["reason"] == "P3prime_and_natural_odd_start"


def test_d58_m3_row_3_4_mixed_extendable():
    """Row 3.4 (m=3, mixed parity, no trigger): extendable.

    k=6, pi=(0,2,1,4,3,5), C={0,1,2,3,4,5}: image {0,1,2,3,4,5}
    = {0,1}+{2,3}+{4,5}; intervals 0-even, 2-even, 4-even.  No P3 (no
    fillers at all in size-6 core at k=6 except... none, since k=6
    means full set).  Predictor: not_minimal_fatal; extendable.
    """
    pred = predict_v6pp(6, (0, 2, 1, 4, 3, 5), (0, 1, 2, 3, 4, 5))
    assert pred["prediction"] == "not_minimal_fatal"
    assert pred["natural_odd_start"] is False
    assert verify_completion_exists(6, (0, 2, 1, 4, 3, 5), (0, 1, 2, 3, 4, 5))


def test_d58_m3_row_3_4_extendable_k7():
    """Row 3.4 at k=7: pi=(0,2,1,5,3,6,4), C={0,1,2,3,4,5}.

    Image {0,1,2,3,5,6} = {0,1}+{2,3}+{5,6}; intervals 0-even, 2-even,
    5-odd — mixed parity (NOS fails).  No P3 (high=6, filler image 4
    < 6).  No P3' AND NOS (NOS false).  No P4.  Extendable.
    """
    pred = predict_v6pp(7, (0, 2, 1, 5, 3, 6, 4), (0, 1, 2, 3, 4, 5))
    assert pred["prediction"] == "not_minimal_fatal"
    assert verify_completion_exists(7, (0, 2, 1, 5, 3, 6, 4), (0, 1, 2, 3, 4, 5))


# -------------------------------------------------------------------
# D58 load-bearing exhaustive sweep at k <= 7
# -------------------------------------------------------------------

def _sub_core_has_v6pp_positive(k, pi, blk_combo):
    """Return True iff some strict sub-tuple of blk_combo, viewed as a
    set of even-adjacent blocks, forms a cyclic-ladder core C' with
    V6''(C') = minimal_fatal."""
    m = len(blk_combo)
    for m2 in range(1, m):
        for sub_blk in combinations(blk_combo, m2):
            C2 = tuple(sorted(i for blk in sub_blk for i in blk))
            if not is_cyclic_ladder_core(k, pi, C2):
                continue
            sub_pred = predict_v6pp(k, pi, C2)
            if sub_pred["prediction"] == "minimal_fatal":
                return True
    return False


@pytest.mark.parametrize("k", [3, 4, 5, 6, 7])
def test_d58_base_case_exhaustive_k_leq_7(k):
    """Load-bearing assertion: at every k <= 7, every V6''-negative
    cyclic-ladder core of size 2m, m in {1, 2, 3}, is either
    extendable (FF backtracker confirms) OR contains a V6''-positive
    proper sub-core (O2 of Lemma 55.1).

    Zero counterexamples expected.
    """
    blocks = even_adjacent_blocks(k)
    total = 0
    extendable = 0
    sub_core_escape = 0
    counterexamples = []
    for m in [1, 2, 3]:
        if len(blocks) < m:
            continue
        for blk_combo in combinations(blocks, m):
            C = tuple(sorted(i for blk in blk_combo for i in blk))
            for pi in permutations(range(k)):
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                pred = predict_v6pp(k, pi, C)
                if pred["prediction"] != "not_minimal_fatal":
                    continue
                total += 1
                if verify_completion_exists(k, pi, C):
                    extendable += 1
                elif _sub_core_has_v6pp_positive(k, pi, blk_combo):
                    sub_core_escape += 1
                else:
                    counterexamples.append({"k": k, "pi": pi, "C": C})

    assert counterexamples == [], (
        f"D58 Mixed-Parity Escape counterexample(s) at k={k}: "
        f"{counterexamples[:3]}"
    )
    # Sanity: every V6''-negative core is accounted for.
    assert extendable + sub_core_escape == total


def test_d58_row_counts_table_consistency():
    """Sanity check the empirical row counts reported in D58.3 / D58.4.

    Aggregated extendable + sub-core counts for m=2, m=3 at k <= 7:
      m=2 (k in {4,5,6,7}): 896 total; 840 extendable; 56 sub-core.
      m=3 (k in {6,7}): 1152 total; 768 extendable; 384 sub-core.
    """
    expected = {
        # (m, k): (total, extendable, sub_core)
        (1, 3): (0, 0, 0),
        (1, 4): (8, 8, 0),
        (1, 5): (0, 0, 0),
        (1, 6): (144, 144, 0),
        (1, 7): (0, 0, 0),
        (2, 4): (16, 8, 8),
        (2, 5): (16, 16, 0),
        (2, 6): (288, 240, 48),
        (2, 7): (576, 576, 0),
        (3, 6): (384, 192, 192),
        (3, 7): (768, 576, 192),
    }
    for (m, k), (exp_total, exp_ext, exp_sub) in expected.items():
        blocks = even_adjacent_blocks(k)
        if len(blocks) < m:
            assert exp_total == 0
            continue
        total = extendable = sub_core_escape = 0
        for blk_combo in combinations(blocks, m):
            C = tuple(sorted(i for blk in blk_combo for i in blk))
            for pi in permutations(range(k)):
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                pred = predict_v6pp(k, pi, C)
                if pred["prediction"] != "not_minimal_fatal":
                    continue
                total += 1
                if verify_completion_exists(k, pi, C):
                    extendable += 1
                elif _sub_core_has_v6pp_positive(k, pi, blk_combo):
                    sub_core_escape += 1
        assert (total, extendable, sub_core_escape) == (exp_total, exp_ext, exp_sub), (
            f"Row count mismatch at m={m}, k={k}: "
            f"got ({total}, {extendable}, {sub_core_escape}), "
            f"expected ({exp_total}, {exp_ext}, {exp_sub})"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
