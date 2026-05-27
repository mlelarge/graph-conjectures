"""Regression tests for Cycle-Core Extraction (D52).

The Cycle-Core Extraction Lemma:
  Every fatal toggle support S of a fork-tree pairing pi contains a
  subset C ⊆ S that is a cyclic-ladder core (full blocks, adjacent
  images, incidence cycle) AND is fatal.

Verified empirically across all 4! + 5! = 144 pairings: 32 + 400 =
432 fatal supports, all admit a cycle-core.
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from cycle_core_extractor import (  # noqa: E402
    extract_cycle_core,
    is_cyclic_ladder_core,
    is_fatal,
    verify_extractor_at_k,
)


def test_is_cyclic_ladder_core_full_block_pair():
    """Pi=(1,2,0,3) at k=4 with S={0,1}: single full block with image
    {1,2} (single interval).  Valid cyclic-ladder core."""
    assert is_cyclic_ladder_core(4, (1, 2, 0, 3), (0, 1)) is True


def test_is_cyclic_ladder_core_rejects_half_block():
    """Half-block selections are not cyclic-ladder cores."""
    assert is_cyclic_ladder_core(4, (1, 2, 0, 3), (0,)) is False
    assert is_cyclic_ladder_core(4, (1, 2, 0, 3), (0, 2)) is False


def test_extract_cycle_core_full_block_self():
    """For a minimal fatal full-block support, the cycle-core is the
    support itself."""
    pi = (1, 2, 0, 3)
    S = (0, 1)
    assert is_fatal(4, pi, S)
    C = extract_cycle_core(4, pi, S)
    assert C is not None
    assert C == (0, 1)


def test_extract_cycle_core_half_block_fatal():
    """For a fatal half-block-containing support, the extractor finds
    a strict full-block-only fatal subset."""
    pi = (1, 2, 0, 3)
    # {0, 1, 2} contains {0, 1} (fatal) plus a half-block at index 2.
    S = (0, 1, 2)
    assert is_fatal(4, pi, S)
    C = extract_cycle_core(4, pi, S)
    assert C is not None
    assert set(C).issubset(set(S))
    assert is_cyclic_ladder_core(4, pi, C)
    assert is_fatal(4, pi, C)


def test_extractor_k4_no_violations():
    out = verify_extractor_at_k(4)
    assert out["fatal_without_core"] == 0
    assert out["fatal_with_core"] == out["total_fatal_supports"]


def test_extractor_k5_no_violations():
    out = verify_extractor_at_k(5)
    assert out["fatal_without_core"] == 0
    assert out["fatal_with_core"] == 400


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
