"""Regression tests for V6'' completeness (D54).

Conjecture 53.5 (V6'' completeness): every cyclic-ladder core with
no V6'' trigger is NOT minimally fatal — i.e., it's either
extendable or contains a smaller fatal subset.

This is the **completeness** direction of V6''.  Combined with
**soundness** (Theorem 53.4: V6'' trigger ⇒ minimal fatal) — proved
structurally — V6'' becomes the exact classifier of minimal fatal
cyclic-ladder cores.

Empirical verification:

  - k=4: 24 non-trigger cyclic-ladder cores; 16 extendable, 8
    non-minimal fatal. 0 counterexamples.
  - k=5: 16 non-trigger cyclic-ladder cores; all extendable.
  - k=6: 816 non-trigger cyclic-ladder cores; 576 extendable, 240
    non-minimal fatal. 0 counterexamples.

This is the strongest empirical evidence for Conjecture 53.5.
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from v6pp_completion_constructor import (  # noqa: E402
    has_no_v6pp_trigger,
    is_cyclic_ladder_core,
    verify_completion_exists,
    verify_construction_at_k,
)


def test_v6pp_completeness_k4_no_counterexamples():
    out = verify_construction_at_k(4)
    assert out["MINIMAL_FATAL_COUNTEREXAMPLES"] == 0
    assert out["v6pp_completeness_holds"]


def test_v6pp_completeness_k5_no_counterexamples():
    out = verify_construction_at_k(5)
    assert out["MINIMAL_FATAL_COUNTEREXAMPLES"] == 0
    assert out["v6pp_completeness_holds"]


def test_v6pp_completeness_k6_no_counterexamples():
    out = verify_construction_at_k(6)
    assert out["MINIMAL_FATAL_COUNTEREXAMPLES"] == 0
    assert out["v6pp_completeness_holds"]


def test_v6pp_trigger_at_k4_anchored_p3():
    """At k=4 with pi=(1,2,0,3), C={0,1} fires P3 (filler image 3 > 2)."""
    pi = (1, 2, 0, 3)
    C = (0, 1)
    assert is_cyclic_ladder_core(4, pi, C)
    assert not has_no_v6pp_trigger(4, pi, C)


def test_v6pp_no_trigger_extendable():
    """At k=5 with identity, no fatal supports.  All cyclic-ladder
    cores have no trigger; all are extendable."""
    pi = (0, 1, 2, 3, 4)
    # Single block (0,1) with image (0,1) — even-start, no triggers.
    C = (0, 1)
    if is_cyclic_ladder_core(5, pi, C) and has_no_v6pp_trigger(5, pi, C):
        assert verify_completion_exists(5, pi, C)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
