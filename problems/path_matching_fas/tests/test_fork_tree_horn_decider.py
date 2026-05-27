"""Regression tests for the Horn-classification fork-tree decider (D36).

Replaces the broken V6 decider of D30 with one that:

  - Enumerates minimal fatal toggle supports by brute force
    (exponential in k).
  - Converts each minimal support to a negative Horn clause.
  - Decides eps-extendability by O(|cnf| * k) unit propagation on
    the Horn CNF.

The decider is CORRECT (matches brute-force enumeration exactly).
It is not polynomial-time: the brute-force minimal-support extraction
is exponential.  A polynomial-time variant would require a sound
poly-time fatality oracle for each candidate ladder; this is open
(V6 was wrong at k=7, D30).
"""
from __future__ import annotations

import os
import sys
from itertools import permutations

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from fork_tree_horn_decider import (  # noqa: E402
    compute_minimal_fatal_supports,
    decide_extendability,
    decide_path_fas_fork_tree,
    horn_cnf_from_supports,
    legality_classifier,
    sweep_at_k,
    verify_decider_matches_brute_force,
)


def test_horn_cnf_construction():
    supports = [(0, 1), (2, 3)]
    cnf = horn_cnf_from_supports(supports)
    assert cnf == [(0, 1), (2, 3)]


def test_decide_extendability_basic():
    cnf = [(0, 1), (2, 3)]
    # eps that has both 0 and 1 set: violates first clause.
    assert not decide_extendability(cnf, [1, 1, 0, 0])
    # eps that has 2 and 3 set: violates second clause.
    assert not decide_extendability(cnf, [0, 0, 1, 1])
    # eps that has only 0 set: satisfies both.
    assert decide_extendability(cnf, [1, 0, 0, 0])
    # All zero: satisfies all negative clauses.
    assert decide_extendability(cnf, [0, 0, 0, 0])


def test_k4_identity_path_fas_yes_trivially():
    """Identity at k=4: no minimal fatal supports, path-FAS yes."""
    out = decide_path_fas_fork_tree(4, (0, 1, 2, 3))
    assert out["yes"] is True
    assert out["minimal_fatal_supports"] == []
    assert out["horn_cnf_size"] == 0


def test_k5_cyclic_shift_horn_classifier():
    """Cyclic shift at k=5: known to have fatal pairs (0,1) and (2,3)."""
    cls = legality_classifier(5, (1, 2, 3, 4, 0))
    supports = cls["minimal_fatal_supports"]
    assert sorted(map(tuple, supports)) == [(0, 1), (2, 3)]
    # R(pi) has 18 patterns: 2^5 - (3*4 + 1*2) hmm let me verify directly
    # The Horn CNF says: not (eps_0 and eps_1) and not (eps_2 and eps_3)
    # Number of satisfying eps: (3 of 4 first pair) * (3 of 4 second pair) * 2 (eps_4)
    # = 3*3*2 = 18. Match.
    assert cls["relation_size"] == 18
    assert cls["schaefer"]["is_horn"] is True


def test_k5_full_sweep_horn_decider_matches_brute_force():
    """All 120 pairings at k=5: Horn decider agrees with brute force."""
    out = sweep_at_k(5, sample_size=None)
    assert out["pairings_with_mismatch"] == 0
    assert out["total_mismatches"] == 0
    assert out["pairings_checked"] == 120


def test_k7_specific_fatal_pair_pi():
    """Pi=(5,3,2,6,4,0,1) at k=7: the V6 failure case from D30.

    The Horn decider must classify this correctly: brute force says
    {0,1,2,3} is NOT a minimal fatal support (V6 wrongly fired P3').
    """
    pi = (5, 3, 2, 6, 4, 0, 1)
    out = verify_decider_matches_brute_force(7, pi)
    assert out["all_match"], out


def test_k7_size_6_ladder_horn_clause():
    """Pi=(1,3,2,5,4,6,0) at k=7: R6 from D35, size-6 minimal fatal."""
    pi = (1, 3, 2, 5, 4, 6, 0)
    supports = compute_minimal_fatal_supports(7, pi)
    sizes = sorted(len(s) for s in supports)
    assert sizes == [6]
    assert tuple(supports[0]) == (0, 1, 2, 3, 4, 5)
    # Horn CNF: not (eps_0 and ... and eps_5).
    # Number of satisfying eps: 2^7 - 2 (the 2 patterns where all 6 are 1
    # have 2 choices for eps_6) = 128 - 2 = 126.
    cls = legality_classifier(7, pi)
    assert cls["relation_size"] == 126


def test_decide_path_fas_fork_tree_always_yes():
    """For every k=5 pairing, the decider returns YES (R(pi) is 0-valid)."""
    for pi in permutations(range(5)):
        out = decide_path_fas_fork_tree(5, pi)
        assert out["yes"] is True
        assert out["witness"] == [0, 0, 0, 0, 0]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
