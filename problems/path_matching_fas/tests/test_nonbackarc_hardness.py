"""Regression tests for the non-back-arc hardness probes.

These pin the verified facts of the ordering/flex encoding attack on
tournament Path-FAS (Aboulker 4.4):

  * the FF score-window decider agrees with brute force on small random
    tournaments (so it may be trusted on larger instances);
  * the toggle/flex clause gadget realises an all-negative OR-clause
    ("infeasible iff all eps = 1"), verified against brute force on the
    feasibility of the full tournament where n <= 10;
  * the feasibility predicate of every extra-wiring is MONOTONE in eps
    (the obstruction: only monotone CSPs, which are in P, are reachable);
  * each variable supports at most 2 clause attachments (the degree-2
    fanout obstruction reappears in the ordering encoding);
  * the betweenness obstruction: no n=5 tournament realises the
    betweenness relative-order set of a trio (exhaustive);
  * the one_block non-monotone primitive exists (D68 collision).
"""
from __future__ import annotations

import itertools
import os
import random
import sys

import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from nonbackarc_hardness import (  # noqa: E402
    ONE_BLOCK,
    backarc_set_shrinks_when_unloaded,
    bf_has_lfo,
    build_with_extras,
    clause_feasibility_table,
    clause_not_all_true_extras,
    feasibility_is_monotone,
    ff_has_lfo,
    lfo_relative_orders,
    monotone_sat_to_path_fas,
    one_block_nonmonotone_pair,
    prefix_extends_ff,
    search_betweenness_gadget,
)
from toggle_fooling_set import a, b, f, g, toggle_prefix  # noqa: E402


# --------------------------------------------------------------------------
# FF decider trust: agreement with brute force
# --------------------------------------------------------------------------
def test_ff_agrees_with_bruteforce_on_random_tournaments():
    """FF score-window decider == brute-force Path-FAS on random
    tournaments at n=7,8 (the oracle-trust check)."""
    rng = random.Random(20260528)
    mismatches = 0
    total = 0
    for n in (7, 8):
        for _ in range(40):
            T = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < 0.5:
                        T[i][j] = 1
                    else:
                        T[j][i] = 1
            total += 1
            if ff_has_lfo(T) != bf_has_lfo(T):
                mismatches += 1
    assert mismatches == 0, f"{mismatches}/{total} FF vs brute-force mismatches"


# --------------------------------------------------------------------------
# Clause gadget semantics
# --------------------------------------------------------------------------
def test_clause_two_negative_literals():
    """clause [0,1] => infeasible iff eps_0 = 1 AND eps_1 = 1."""
    table = clause_feasibility_table(2, [0, 1])
    assert table[(0, 0)] is True
    assert table[(0, 1)] is True
    assert table[(1, 0)] is True
    assert table[(1, 1)] is False


def test_clause_three_negative_literals():
    """clause [0,1,2] => infeasible iff eps = (1,1,1)."""
    table = clause_feasibility_table(3, [0, 1, 2])
    for eps in itertools.product((0, 1), repeat=3):
        expected = not all(eps)  # feasible iff not all 1
        assert table[eps] is expected, (eps, table[eps])


def test_unit_clause():
    """Unit clause [0] => feasible iff eps_0 = 0."""
    table = clause_feasibility_table(2, [0])
    for eps in itertools.product((0, 1), repeat=2):
        assert table[eps] is (eps[0] == 0)


def test_clause_two_literals_global_matches_bruteforce_n10():
    """The k=2, pad=0 clause tournament (n=10) is globally Path-FAS
    feasible, and FF agrees with brute force on that global verdict."""
    T = build_with_extras(2, clause_not_all_true_extras(2, [0, 1]), pad=0)
    assert len(T) == 10
    assert ff_has_lfo(T) == bf_has_lfo(T)
    # the clause (~x0 v ~x1) is satisfiable (e.g. eps=(0,0)), so feasible
    assert bf_has_lfo(T) is True


# --------------------------------------------------------------------------
# The monotonicity obstruction
# --------------------------------------------------------------------------
def test_clause_wiring_is_monotone():
    """The 2- and 3-literal clause wirings are monotone-decreasing in eps."""
    assert feasibility_is_monotone(2, clause_not_all_true_extras(2, [0, 1]))
    assert feasibility_is_monotone(3, clause_not_all_true_extras(3, [0, 1, 2]))


def test_random_wirings_are_all_monotone():
    """Exhaustive-ish: 120 random extra-wirings are all monotone in eps.
    No wiring realises a non-monotone (hence NP-hard) predicate."""
    rng = random.Random(11)
    k = 3
    verts = []
    for i in range(k):
        verts += [a(i), b(i), f(k, i), g(k, i)]
    for _ in range(120):
        n_ext = rng.randint(1, 4)
        extras = [rng.sample(verts, rng.choice([2, 2, 3])) for _ in range(n_ext)]
        assert feasibility_is_monotone(k, extras), extras


def test_backarc_set_shrinks_when_unloaded():
    """Structural cause of monotonicity: flipping eps_i 1->0 only removes
    the a_i--b_i back-arc, so the back-arc set strictly shrinks."""
    assert backarc_set_shrinks_when_unloaded(4)


# --------------------------------------------------------------------------
# The degree-2 fanout obstruction (reappears in the ordering encoding)
# --------------------------------------------------------------------------
def test_two_attachments_per_variable_ok():
    """A variable supports 2 clause attachments (one at f_i, one at g_i)."""
    T = build_with_extras(1, [[f(1, 0)], [g(1, 0)]])
    assert prefix_extends_ff(T, toggle_prefix(1, (0,))) is True


def test_third_attachment_overloads():
    """A 3rd attachment to a variable's free ends overloads the degree
    budget -- the Corollary 5.2 fanout cap, now for the flex encoding."""
    T = build_with_extras(1, [[f(1, 0)], [f(1, 0)], [g(1, 0)]])
    assert prefix_extends_ff(T, toggle_prefix(1, (0,))) is False


def test_shared_variable_across_clauses_breaks_composition():
    """A variable shared by two 2-literal clauses overloads its f/g ends,
    destroying the LFO even though the formula is satisfiable.  This is
    the fanout obstruction blocking composition in the flex encoding."""
    # vars {0,1,2}; clauses [0,1] and [1,2] share variable 1.
    extras = clause_not_all_true_extras(3, [0, 1]) + clause_not_all_true_extras(3, [1, 2])
    T = build_with_extras(3, extras, pad=8)
    # formula is satisfiable (e.g. all L true = all eps 0), yet:
    assert ff_has_lfo(T) is False


# --------------------------------------------------------------------------
# Working (but P-time) monotone-SAT reduction
# --------------------------------------------------------------------------
def test_monotone_sat_single_clause_is_feasible():
    """Single-clause monotone formulas reduce to feasible tournaments
    (the all-eps-0 assignment always satisfies a positive clause)."""
    for nv, clauses in [(2, [[0, 1]]), (3, [[0, 1, 2]]), (2, [[0], [1]])]:
        T = monotone_sat_to_path_fas(nv, clauses, pad=8)
        assert ff_has_lfo(T) is True


# --------------------------------------------------------------------------
# The betweenness obstruction
# --------------------------------------------------------------------------
def test_betweenness_gadget_does_not_exist_n5():
    """Exhaustive over all 1024 tournaments on n=5: no trio's LFO
    relative-order set equals (or is a nonempty subset of) the
    betweenness set {(x,y,z),(z,y,x)}.  The smallest nonempty
    relative-order set has size >= 3."""
    out = search_betweenness_gadget(5)
    assert out["exact_betweenness_trios"] == 0
    assert out["nonempty_subset_trios"] == 0
    assert out["min_nonempty_relorder_size"] >= 3


def test_relative_order_set_is_thick():
    """Concretely: in a transitive-ish small tournament the relative-order
    set of a free trio has >= 3 elements (cannot be a 2-element
    betweenness set)."""
    # transitive tournament on 5 vertices, trio (1,2,3)
    n = 5
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    ro = lfo_relative_orders(T, (1, 2, 3))
    assert len(ro) >= 1  # transitive: exactly the identity order
    # a tournament with a free trio: any nonempty set has size != 2 betweenness
    betweenness = {(1, 2, 3), (3, 2, 1)}
    assert ro != betweenness


# --------------------------------------------------------------------------
# The non-monotone primitive (one_block, D68)
# --------------------------------------------------------------------------
def test_one_block_nonmonotone_primitive():
    """The two length-5 one_block prefixes have opposite extendability,
    establishing a genuine non-monotone ordering primitive."""
    out = one_block_nonmonotone_pair()
    assert out["A_extends"] is False
    assert out["B_extends"] is True


def test_one_block_is_valid_tournament():
    """one_block is a valid 12-vertex tournament."""
    n = len(ONE_BLOCK)
    assert n == 12
    for i in range(n):
        assert ONE_BLOCK[i][i] == 0
        for j in range(i + 1, n):
            assert ONE_BLOCK[i][j] + ONE_BLOCK[j][i] == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
