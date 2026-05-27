"""Regression tests for per-step loaded-edge analysis of sigma*(k) (D61).

These tests verify three load-bearing facts of Section 61:

  1. The per-step flex-partner classification: each step loads at most
     one flex edge (the per-step loaded-edge table in 61.2).
  2. All σ*(k) failures on V6''-negative cores are CYCLE failures
     (Lemma 61.C: no degree saturation occurs).
  3. Every cycle failure has a strictly smaller V6''-positive
     cyclic-ladder sub-core (the contrapositive of Lemma 61.S).

These are empirical guardrails, NOT the symbolic proof.  The proof
obligation (Open 61.E: cycle projection) is documented in Section 61.
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fork_tree_probe import fork_tree_prefix, fork_tree_tournament  # noqa: E402
from ff_signature_probe import valid_prefix_state_ff, _add_flexible_vertex, _canonical_parent  # noqa: E402
from lfo_forced_flexible import _find, _iter_bits, _union  # noqa: E402
from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from sigma_star_formula import sigma_star_closed  # noqa: E402
from sigma_star_step_analysis import per_step_analysis  # noqa: E402
from v6pp_completion_constructor import (  # noqa: E402
    has_no_v6pp_trigger,
    is_cyclic_ladder_core,
)
from v6pp_predictor import predict_v6pp  # noqa: E402

from itertools import combinations, permutations


# ----------------------------------------------------------------------
# 1. Per-step pairwise component separation among flex partners (Lemma 61.S)
# ----------------------------------------------------------------------

def _classify_failure(k, pi, C):
    """Return ('cycle' | 'degree' | 'ok', step_index)."""
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return ("invalid_prefix", -1)
    prefix_mask, degree, parent, flex_outmask, windows = state
    sigma = sigma_star_closed(k)
    par = list(parent)
    deg = list(degree)
    pm = prefix_mask
    for j, x in enumerate(sigma):
        for p in _iter_bits(flex_outmask[x] & pm):
            if deg[x] >= 2 or deg[p] >= 2:
                return ("degree", j)
            if _find(par, x) == _find(par, p):
                return ("cycle", j)
            deg[x] += 1
            deg[p] += 1
            _union(par, x, p)
        par = list(_canonical_parent(par))
        pm |= 1 << x
    return ("ok", -1)


def _find_smaller_v6pp_positive_subcore(k, pi, C):
    blocks = even_adjacent_blocks(k)
    C_set = set(C)
    block_subset = [blk for blk in blocks if all(i in C_set for i in blk)]
    for size in range(1, len(block_subset)):
        for sub in combinations(block_subset, size):
            S = tuple(sorted(i for blk in sub for i in blk))
            if not is_cyclic_ladder_core(k, pi, S):
                continue
            pred = predict_v6pp(k, pi, S)
            if pred["prediction"] != "not_minimal_fatal":
                return S
    return None


def _iter_v6pp_negative_cores(k):
    blocks = even_adjacent_blocks(k)
    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                if not has_no_v6pp_trigger(k, pi, C):
                    continue
                yield pi, C


def test_separation_at_every_step_at_k4():
    """Lemma 61.S empirical: at every σ*(k) step on a V6''-negative
    core where σ*(k) succeeds, all flex partners lie in pairwise
    distinct components.

    At k=4 with C carrying pair 3 toggled (e.g., C=(2,3) under
    pi=identity), the A_3 step is a 2-partner step (a_3, A_2).
    Their components must be distinct."""
    for pi, C in _iter_v6pp_negative_cores(4):
        analysis = per_step_analysis(4, pi, C)
        if analysis["failed"]:
            continue
        for row in analysis["rows"]:
            assert row["separation_ok"], (pi, C, row)


def test_separation_at_every_step_at_k6():
    for pi, C in _iter_v6pp_negative_cores(6):
        analysis = per_step_analysis(6, pi, C)
        if analysis["failed"]:
            continue
        for row in analysis["rows"]:
            assert row["separation_ok"], (pi, C, row)


def test_max_partners_observed_at_k4_is_2():
    """Document the k=4 edge case: A_3 step can have 2 partners when
    pair k-1 is in C."""
    max_per_step = {}
    for pi, C in _iter_v6pp_negative_cores(4):
        analysis = per_step_analysis(4, pi, C)
        if analysis["failed"]:
            continue
        for row in analysis["rows"]:
            j = row["j"]
            max_per_step[j] = max(max_per_step.get(j, 0), row.get("n_partners", 0))
    # j=4 (A_3 unpaired) can have up to 2 partners.
    assert max_per_step.get(4, 0) == 2, max_per_step


def test_max_partners_observed_at_k5_is_1():
    """At k=5, the unpaired tail is B_4 (k odd), which has 1 partner."""
    max_per_step = {}
    for pi, C in _iter_v6pp_negative_cores(5):
        analysis = per_step_analysis(5, pi, C)
        if analysis["failed"]:
            continue
        for row in analysis["rows"]:
            j = row["j"]
            max_per_step[j] = max(max_per_step.get(j, 0), row.get("n_partners", 0))
    for j, m in max_per_step.items():
        assert m <= 1, (j, m)


# ----------------------------------------------------------------------
# 2. All failures are cycles, no degree saturation (Lemma 61.C)
# ----------------------------------------------------------------------

@pytest.mark.parametrize("k", [4, 6])
def test_no_degree_saturation_failures_at_k(k):
    """Lemma 61.C: no σ*(k) failure on a V6''-negative core is a
    degree-saturation failure."""
    n_cycle = 0
    n_degree = 0
    for pi, C in _iter_v6pp_negative_cores(k):
        result, _ = _classify_failure(k, pi, C)
        if result == "cycle":
            n_cycle += 1
        elif result == "degree":
            n_degree += 1
    assert n_degree == 0, f"k={k} had {n_degree} degree failures"


# ----------------------------------------------------------------------
# 3. Every cycle failure has a smaller V6''-positive sub-core (Lemma 61.S)
# ----------------------------------------------------------------------

@pytest.mark.parametrize("k", [4, 6])
def test_every_cycle_failure_has_smaller_v6pp_positive_subcore(k):
    """Contrapositive of Lemma 61.S: every σ*(k) cycle failure on a
    V6''-negative core has a strictly smaller V6''-positive sub-core."""
    missed = []
    for pi, C in _iter_v6pp_negative_cores(k):
        result, _ = _classify_failure(k, pi, C)
        if result != "cycle":
            continue
        sub = _find_smaller_v6pp_positive_subcore(k, pi, C)
        if sub is None:
            missed.append((pi, C))
    assert not missed, f"k={k} had {len(missed)} cycle failures with no smaller positive sub-core: {missed[:3]}"


# ----------------------------------------------------------------------
# 4. σ*(k) succeeds iff no smaller V6''-positive sub-core (Theorem 61.D
#    on the V6''-negative core sub-population)
# ----------------------------------------------------------------------

def test_theorem_61D_at_k4():
    """At k=4: σ*(k) is FF-valid on a V6''-negative core iff the core
    contains no smaller V6''-positive sub-core."""
    for pi, C in _iter_v6pp_negative_cores(4):
        result, _ = _classify_failure(4, pi, C)
        sub = _find_smaller_v6pp_positive_subcore(4, pi, C)
        if result == "ok":
            assert sub is None, (pi, C, sub)
        elif result == "cycle":
            assert sub is not None, (pi, C)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
