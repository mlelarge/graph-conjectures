"""Pin tests for the FF repair tracer (D59).

The tracer mirrors `has_completion_ff` but threads the actual
completing suffix through the recursion.  These tests fix:

1. Tracer/decider agreement on small fork-tree examples.
2. Specific completing suffixes returned by the tracer at k=4..6
   on D54 cores.
3. The diff-as-moves classifier's behaviour on tiny examples.
4. The headline D59 finding: every extendable V6''-negative
   cyclic-ladder core at k <= 6 yields the SAME completing suffix
   modulo a fixed set of k disjoint adjacent swaps off the canonical
   baseline.
"""
from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from ff_repair_tracer import (  # noqa: E402
    canonical_suffix,
    completing_suffix,
    completing_suffix_ff,
    detect_rotations_and_blocks,
    diff_as_moves,
    trace_all_v6pp_negative_cores,
)
from ff_signature_probe import (  # noqa: E402
    has_completion_ff,
    valid_prefix_state_ff,
)
from fork_tree_probe import fork_tree_prefix, fork_tree_tournament  # noqa: E402
from v6pp_completion_constructor import (  # noqa: E402
    verify_completion_exists,
)


# ---------------------------------------------------------------------
# 1. Move-classifier unit tests
# ---------------------------------------------------------------------

def test_diff_as_moves_identity():
    out = diff_as_moves([1, 2, 3, 4], [1, 2, 3, 4])
    assert out["is_identity"]
    assert out["n_moves"] == 0
    assert out["move_classes"] == {}
    assert out["max_distance"] == 0


def test_diff_as_moves_single_adjacent_swap():
    out = diff_as_moves([1, 2, 3, 4], [2, 1, 3, 4])
    assert out["n_moves"] == 1
    assert out["move_classes"] == {"adjacent_swap": 1}
    assert out["max_distance"] == 1


def test_diff_as_moves_disjoint_adjacent_swaps():
    out = diff_as_moves([1, 2, 3, 4], [2, 1, 4, 3])
    assert out["n_moves"] == 2
    assert out["move_classes"] == {"adjacent_swap": 2}


def test_diff_as_moves_long_range_swap():
    out = diff_as_moves([1, 2, 3, 4], [4, 2, 3, 1])
    assert out["n_moves"] == 1
    assert out["move_classes"] == {"long_range_swap_d3": 1}
    assert out["max_distance"] == 3


def test_detect_3_rotation_left():
    out = detect_rotations_and_blocks([1, 2, 3, 4], [1, 3, 4, 2])
    assert out["pattern"] == "3_rotation_left"
    assert out["block_lo"] == 1
    assert out["block_hi"] == 3


def test_detect_disjoint_adjacent_swaps():
    out = detect_rotations_and_blocks([1, 2, 3, 4, 5, 6], [2, 1, 3, 5, 4, 6])
    assert out["pattern"] == "disjoint_adjacent_swaps_n2"
    assert out["n_adjacent_swaps"] == 2


def test_detect_block_reversal():
    out = detect_rotations_and_blocks([1, 2, 3, 4, 5], [1, 4, 3, 2, 5])
    assert out["pattern"].startswith("block_reversal")


# ---------------------------------------------------------------------
# 2. Tracer ⇄ decider agreement
# ---------------------------------------------------------------------

def _decider_says_complete(k: int, pi, C) -> bool:
    return verify_completion_exists(k, pi, C)


def test_tracer_matches_decider_k4_natural():
    pi = (0, 1, 2, 3)
    C = (2, 3)
    suffix = completing_suffix(4, pi, C)
    decider = _decider_says_complete(4, pi, C)
    if decider:
        assert suffix is not None
        # Suffix must be the exact set of post-prefix vertices.
        assert sorted(suffix) == sorted(canonical_suffix(4))
    else:
        assert suffix is None


def test_tracer_matches_decider_k5():
    pi = (0, 1, 2, 3, 4)
    C = (0, 1)
    suffix = completing_suffix(5, pi, C)
    decider = _decider_says_complete(5, pi, C)
    if decider:
        assert suffix is not None
        assert sorted(suffix) == sorted(canonical_suffix(5))
    else:
        assert suffix is None


def test_tracer_matches_decider_k6_sample():
    pi = (0, 1, 2, 3, 4, 5)
    C = (4, 5)
    suffix = completing_suffix(6, pi, C)
    decider = _decider_says_complete(6, pi, C)
    if decider:
        assert suffix is not None
        assert sorted(suffix) == sorted(canonical_suffix(6))
    else:
        assert suffix is None


# ---------------------------------------------------------------------
# 3. Suffix validity: the tracer's result must actually be a valid LFO
# ---------------------------------------------------------------------

def _suffix_validates(k: int, pi, C, suffix) -> bool:
    """Combine `valid_prefix_state_ff` with manual stepping through
    the FF state machine using the suffix; confirm the FF
    bookkeeping passes at every step."""
    from ff_signature_probe import _add_flexible_vertex  # noqa: WPS433
    from lfo_score_window import hall_interval_ok  # noqa: WPS433

    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return False
    prefix_mask, degree, parent, flex_outmask, windows = state
    pos = len(prefix)
    n = len(T)
    all_mask = (1 << n) - 1
    deg = tuple(degree)
    par = tuple(parent)
    for x in suffix:
        lo, hi = windows[x]
        if not (lo <= pos <= hi):
            return False
        if prefix_mask & (1 << x):
            return False
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, deg, par, x)
        if nxt is None:
            return False
        deg, par = nxt
        prefix_mask |= 1 << x
        pos += 1
    return prefix_mask == all_mask


def test_tracer_suffix_is_valid_k4():
    pi = (0, 1, 2, 3)
    C = (2, 3)
    suffix = completing_suffix(4, pi, C)
    assert suffix is not None
    assert _suffix_validates(4, pi, C, suffix)


def test_tracer_suffix_is_valid_k5():
    pi = (1, 0, 2, 3, 4)
    C = (0, 1)
    suffix = completing_suffix(5, pi, C)
    if suffix is not None:
        assert _suffix_validates(5, pi, C, suffix)


# ---------------------------------------------------------------------
# 4. Headline D59 finding: uniform adjacent-swap repair at k <= 6
# ---------------------------------------------------------------------

def test_d59_finding_k4_all_adjacent_swaps():
    out = trace_all_v6pp_negative_cores(4)
    assert out["extendable"] == 16
    assert out["n_distinct_found_suffixes"] == 1
    assert out["pattern_distribution"] == {"disjoint_adjacent_swaps_n4": 16}
    assert out["move_class_totals"] == {"adjacent_swap": 64}
    assert out["max_distance_distribution"] == {1: 16}


def test_d59_finding_k5_all_adjacent_swaps():
    out = trace_all_v6pp_negative_cores(5)
    assert out["extendable"] == 16
    assert out["n_distinct_found_suffixes"] == 1
    assert out["pattern_distribution"] == {"disjoint_adjacent_swaps_n5": 16}
    assert out["max_distance_distribution"] == {1: 16}


def test_d59_finding_k6_all_adjacent_swaps():
    out = trace_all_v6pp_negative_cores(6)
    assert out["extendable"] == 576
    assert out["n_distinct_found_suffixes"] == 1
    assert out["pattern_distribution"] == {"disjoint_adjacent_swaps_n6": 576}
    assert out["max_distance_distribution"] == {1: 576}
    # The swap positions are exactly [0, 2, 4, 7, 9, 11] (skipping
    # 6 = A_5 and 12 = B_5).
    assert out["n_distinct_swap_position_sets"] == 1
    assert out["distinct_swap_position_sets"][0]["swap_lower_endpoints"] == [
        0, 2, 4, 7, 9, 11,
    ]
