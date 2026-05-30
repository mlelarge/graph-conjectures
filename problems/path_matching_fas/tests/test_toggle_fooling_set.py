"""Regression tests for the toggle-pair forward-DP lower bound (D70).

These pin the fooling-set construction that strengthens Section 16's
signature-specific 2^(n/4) bound to a fundamental forward-DP lower
bound:

  * the probe leaves every prefix vertex's score window unchanged
    (soundness of the fooling set), and
  * with the gadget-j probe, the toggle prefix P_eps extends iff
    eps_j = 0 (pairwise extension-distinguishability).
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from toggle_fooling_set import (  # noqa: E402
    build_toggle_family,
    build_toggle_with_probe,
    prefix_extends,
    toggle_prefix,
    verify_fooling_set,
    verify_prefix_windows_probe_invariant,
    a,
    b,
    f,
    g,
)


def test_base_toggle_family_is_tournament():
    """build_toggle_family produces a valid tournament (exactly one arc
    per pair)."""
    k = 4
    T = build_toggle_family(k)
    n = 4 * k
    assert len(T) == n
    for i in range(n):
        for j in range(i + 1, n):
            assert T[i][j] + T[j][i] == 1


def test_forced_reversals_present():
    """f_i -> a_i and g_i -> b_i are reversed from transitive base."""
    k = 4
    T = build_toggle_family(k)
    for i in range(k):
        assert T[f(k, i)][a(i)] == 1
        assert T[a(i)][f(k, i)] == 0
        assert T[g(k, i)][b(i)] == 1
        assert T[b(i)][g(k, i)] == 0


def test_probe_window_invariant_k4():
    """The probe leaves every prefix vertex's score window unchanged."""
    out = verify_prefix_windows_probe_invariant(4)
    assert out["windows_invariant"], out


def test_fooling_set_holds_k4():
    """All 2^4 toggle prefixes are pairwise extension-distinguishable:
    P_eps extends in probe-j tournament iff eps_j = 0."""
    out = verify_fooling_set(4)
    assert out["fooling_set_holds"], out
    assert out["distinguishable_prefixes"] == 16


def test_probe_distinguishes_single_gadget():
    """Spot check: at k=4, probe gadget 1, eps with eps_1=1 is NOT
    extendable; flipping eps_1 to 0 makes it extendable."""
    k = 4
    j = 1
    T = build_toggle_with_probe(k, j)
    eps_on = [0, 1, 0, 0]
    eps_off = [0, 0, 0, 0]
    assert prefix_extends(T, toggle_prefix(k, eps_on)) is False
    assert prefix_extends(T, toggle_prefix(k, eps_off)) is True


def test_probe_only_constrains_its_own_gadget():
    """The gadget-j probe is insensitive to eps_i for i != j."""
    k = 4
    j = 2
    T = build_toggle_with_probe(k, j)
    # eps_2 = 0 -> extendable regardless of the other bits
    for other in [[0, 0, 0, 0], [1, 1, 0, 1], [1, 0, 0, 1]]:
        assert other[j] == 0
        assert prefix_extends(T, toggle_prefix(k, other)) is True
    # eps_2 = 1 -> not extendable regardless of the other bits
    for other in [[0, 0, 1, 0], [1, 1, 1, 1], [0, 1, 1, 0]]:
        assert other[j] == 1
        assert prefix_extends(T, toggle_prefix(k, other)) is False


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
