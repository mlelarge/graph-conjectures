"""Regression tests for the Normal-Form Lemma (D50).

Normal-Form Lemma: every minimal fatal toggle support is

  (NF1) a union of even-adjacent toggle blocks {(2p, 2p+1)};
  (NF2) image set decomposes into adjacent 2-pairs;
  (NF3) block/interval incidence is a simple cycle.

Verified empirically at k=4, 5, 6 across all pairings (8 + 64 + 384
minimal supports total, zero violations).
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from normal_form_verifier import (  # noqa: E402
    sweep_k,
    verify_NF1_block_union,
    verify_NF2_adjacent_pairs,
    verify_NF3_incidence_cycle,
    verify_normal_form,
)


def test_NF1_block_union_simple():
    # k=4, support {0, 1}: block (0, 1) entire.
    assert verify_NF1_block_union(4, (0, 1)) is True
    # Support {0, 1, 2, 3}: blocks (0,1) and (2,3).
    assert verify_NF1_block_union(4, (0, 1, 2, 3)) is True
    # Support {0, 2}: not a block union.
    assert verify_NF1_block_union(4, (0, 2)) is False
    # Support {0}: not a block union.
    assert verify_NF1_block_union(4, (0,)) is False


def test_NF1_rejects_lone_at_odd_k():
    # k=7, support {6}: lone vertex at k-1 cannot be in fatal support.
    assert verify_NF1_block_union(7, (6,)) is False


def test_NF2_adjacent_pairs():
    # Single interval {1, 2}.
    pi = (1, 2, 0, 3)
    assert verify_NF2_adjacent_pairs(pi, (0, 1)) is True
    # Two adjacent intervals: pi(S) = {1, 2, 3, 4}.
    pi2 = (1, 3, 2, 4)
    assert verify_NF2_adjacent_pairs(pi2, (0, 1, 2, 3)) is True
    # Non-pair-decomposable: pi(S) = {0, 2, 4}.
    pi3 = (0, 2, 4, 1)
    assert verify_NF2_adjacent_pairs(pi3, (0, 1, 2)) is False  # odd size anyway


def test_NF3_size2_single_block_cycle():
    # Single block, single interval: NF3 holds.
    pi = (1, 2, 0, 3)
    assert verify_NF3_incidence_cycle(pi, (0, 1)) is True


def test_NF3_size4_two_intervals_cycle():
    # pi = (1, 3, 2, 4): two blocks, two intervals, 2-cycle.
    pi = (1, 3, 2, 4)
    assert verify_NF3_incidence_cycle(pi, (0, 1, 2, 3)) is True


def test_sweep_k4_no_violations():
    out = sweep_k(4)
    assert out["NF1_violations"] == 0
    assert out["NF2_violations"] == 0
    assert out["NF3_violations"] == 0
    assert out["total_minimal_supports"] == 8


def test_sweep_k5_no_violations():
    out = sweep_k(5)
    assert out["NF1_violations"] == 0
    assert out["NF2_violations"] == 0
    assert out["NF3_violations"] == 0
    assert out["total_minimal_supports"] == 64


def test_sweep_k6_no_violations():
    out = sweep_k(6)
    assert out["NF1_violations"] == 0
    assert out["NF2_violations"] == 0
    assert out["NF3_violations"] == 0
    assert out["total_minimal_supports"] == 384


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
