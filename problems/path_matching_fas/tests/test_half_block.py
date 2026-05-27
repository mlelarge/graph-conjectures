"""Regression tests for Sublemma 50.3 (Block Parity, D51).

Empirically established: every fatal half-block-containing support
admits a strict full-block-only fatal subset, across k=4, 5, 6.

This is the empirical strong form of Sublemma 50.3.  A full
structural proof remains open (Section 51.4 gap).
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from half_block_extractor import has_half_block, verify_block_parity_at_k  # noqa: E402


def test_has_half_block_unit():
    # Single index 0 is a half-block (block (0, 1) only has 0).
    assert has_half_block(4, (0,)) is True
    # {0, 1} is full block.
    assert has_half_block(4, (0, 1)) is False
    # {0, 2} is two half-blocks.
    assert has_half_block(4, (0, 2)) is True
    # Lone vertex at odd k.
    assert has_half_block(7, (6,)) is True
    # {0, 1, 2, 3} is two full blocks.
    assert has_half_block(4, (0, 1, 2, 3)) is False


def test_block_parity_k4():
    """At k=4: 16 fatal half-block supports, all have strict
    full-block-only fatal subsets."""
    out = verify_block_parity_at_k(4)
    assert out["violations"] == 0
    assert out["half_block_fatal_supports"] == 16


def test_block_parity_k5():
    """At k=5: 296 fatal half-block supports, 0 violations."""
    out = verify_block_parity_at_k(5)
    assert out["violations"] == 0
    assert out["half_block_fatal_supports"] == 296


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
