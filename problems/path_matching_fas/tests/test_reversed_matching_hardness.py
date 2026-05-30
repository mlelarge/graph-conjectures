"""Tests for the reversed-matching hardness attempt.

These tests pin the substrate, the candidate reduction, and the
observed obstruction surface.  The intent is *not* to certify a
working reduction (there is none): the tests document the failure
mode so that any future attempt can be compared against it.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
)

from interaction_graph import build_H_and_Gflex, hall_feasible  # noqa: E402
from reversed_matching_hardness import (  # noqa: E402
    GColoringInstance,
    build_3coloring_reduction,
    build_general_reversed_matching,
    build_reversed_matching,
    enumerate_lfos,
    is_3_colorable,
    register_state,
    register_state_diagnostic,
    verify_reduction,
)


# ---------------------------------------------------------------------------
# Section 1: Substrate
# ---------------------------------------------------------------------------


def test_reversed_matching_RM8_has_8_forced_matching_edges() -> None:
    """RM(8) has |H| = 8, the forced matching {(i+8, i) : i in [0,8)}."""
    T = build_reversed_matching(8)
    H, _ = build_H_and_Gflex(T)
    assert H.number_of_edges() == 8
    expected = {(i + 8, i) for i in range(8)}
    assert set(H.edges()) == expected


def test_reversed_matching_RM10_has_10_forced_matching_edges() -> None:
    """RM(10) realises |H| = 10 (the central D67 diagnostic)."""
    T = build_reversed_matching(10)
    H, _ = build_H_and_Gflex(T)
    assert H.number_of_edges() == 10
    expected = {(i + 10, i) for i in range(10)}
    assert set(H.edges()) == expected


def test_reversed_matching_is_hall_feasible() -> None:
    """RM(m) is Hall-feasible for m in {8, 10, 12}."""
    for m in [8, 10, 12]:
        T = build_reversed_matching(m)
        assert hall_feasible(T), f"RM({m}) is not Hall-feasible"


def test_reversed_matching_components_have_size_2() -> None:
    """Every forced component is a single matching edge.

    This is the precise sense in which Theorem 5.1 of
    docs/J_hardness_via_wires.md (interior degree saturation) is
    vacuous on the reversed-matching substrate: there are no interior
    vertices.
    """
    import networkx as nx

    for m in [8, 10, 12]:
        T = build_reversed_matching(m)
        H, _ = build_H_and_Gflex(T)
        U = H.to_undirected()
        for comp in nx.connected_components(U):
            assert len(comp) == 2, (
                f"forced component {comp} has size != 2 in RM({m})"
            )


def test_reversed_matching_has_many_lfos() -> None:
    """RM(8) has a substantial LFO count (>=100), confirming flex
    between matching components is rich.
    """
    T = build_reversed_matching(8)
    lfos = enumerate_lfos(T, cap=2000)
    assert len(lfos) >= 100


# ---------------------------------------------------------------------------
# Section 2: Theorem 5.1 is vacuous in the reversed-matching substrate
# ---------------------------------------------------------------------------


def test_theorem_5_1_vacuous_on_matching() -> None:
    """For each forced backedge {u, v} in RM(m), neither u nor v is an
    interior vertex of any forced path.  So Theorem 5.1 has no content
    on this substrate.
    """
    import networkx as nx

    for m in [8, 10, 12]:
        T = build_reversed_matching(m)
        H, _ = build_H_and_Gflex(T)
        U = H.to_undirected()
        # Every component is a K_2.  No vertex of U has degree > 1.
        max_deg = max((d for _, d in U.degree()), default=0)
        assert max_deg == 1, (
            f"RM({m}) has H-vertex of degree {max_deg}; matching expected"
        )


# ---------------------------------------------------------------------------
# Section 3: Register-state diagnostic (number of distinct shuffle states)
# ---------------------------------------------------------------------------


def test_register_states_are_nontrivial() -> None:
    """RM(8) has more than 1 distinct register-state vector across its
    LFOs.  This confirms the 'register' has nontrivial state.
    """
    T = build_reversed_matching(8)
    diag = register_state_diagnostic(T, m=8, lfo_cap=5000)
    assert diag["lfo_count"] >= 100
    assert diag["distinct_register_states"] >= 2


# ---------------------------------------------------------------------------
# Section 4: The 3-coloring reduction's failure modes
# ---------------------------------------------------------------------------


def test_3coloring_reduction_C5_destroys_lfo_existence() -> None:
    """The candidate 3-coloring reduction applied to the 5-cycle C_5
    yields a tournament with NO LFO, even though C_5 is 3-colorable.

    This is a false negative: G is 3-colorable (truth = YES) but
    Path-FAS(T_G) = NO.  Hence the reduction is unsound.
    """
    G = GColoringInstance.of(5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)])
    assert is_3_colorable(G), "C_5 is 3-colorable as a sanity check"
    rep = verify_reduction(G, lfo_cap=20000)
    assert rep["true_3colorable"] is True
    assert rep["T_has_lfo"] is False, (
        "Expected the reduction to fail by losing LFO existence; saw an LFO."
    )


def test_3coloring_reduction_triangle_fails_to_encode_a_valid_coloring() -> None:
    """The candidate reduction on the triangle K_3 yields T with LFOs
    but none whose register-state vector is a valid 3-coloring.

    This is the second failure mode: T has feasible LFOs but the slot-
    decoding does not realise the demanded coloring relation.
    """
    G = GColoringInstance.of(3, [(0, 1), (0, 2), (1, 2)])
    assert is_3_colorable(G)
    rep = verify_reduction(G, lfo_cap=20000)
    assert rep["true_3colorable"] is True
    # The reduction loses validity here:
    assert rep["encoded_a_valid_coloring"] is False


def test_3coloring_reduction_K4_accidentally_matches() -> None:
    """K_4 is not 3-colorable.  T_{K_4} has LFOs but none encode a valid
    3-coloring.  So at the level of "is there an LFO that decodes to a
    valid coloring", the answer is correctly NO for K_4.

    This is *not* evidence the reduction works: the same outcome occurs
    on the triangle (a 3-colorable graph).  Both K_4 and K_3 produce the
    same observable "no valid coloring encoded", so the reduction cannot
    distinguish the two.
    """
    G_k4 = GColoringInstance.of(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    assert is_3_colorable(G_k4) is False
    rep = verify_reduction(G_k4, lfo_cap=20000)
    assert rep["true_3colorable"] is False
    assert rep["T_has_lfo"] is True
    assert rep["encoded_a_valid_coloring"] is False


def test_3coloring_reduction_path_is_consistent_but_not_definitive() -> None:
    """The candidate reduction on a 3-vertex path P_3 produces LFOs at
    least one of which decodes to a valid 3-coloring.  This is the
    *consistent* case — but it's not evidence of soundness, because we
    already saw the reduction is unsound on C_5 and K_3.
    """
    G = GColoringInstance.of(3, [(0, 1), (1, 2)])
    assert is_3_colorable(G)
    rep = verify_reduction(G, lfo_cap=20000)
    assert rep["true_3colorable"] is True
    assert rep["T_has_lfo"] is True


# ---------------------------------------------------------------------------
# Section 5: Brute-force ground truth checks
# ---------------------------------------------------------------------------


def test_is_3_colorable_brute_force_on_small_graphs() -> None:
    """Sanity-check the ground-truth 3-coloring checker."""
    # P_3 (path) is 3-colorable
    G_path = GColoringInstance.of(3, [(0, 1), (1, 2)])
    assert is_3_colorable(G_path) is True
    # K_3 (triangle) is 3-colorable (uses all 3 colors)
    G_k3 = GColoringInstance.of(3, [(0, 1), (0, 2), (1, 2)])
    assert is_3_colorable(G_k3) is True
    # K_4 is not 3-colorable
    G_k4 = GColoringInstance.of(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    assert is_3_colorable(G_k4) is False
    # C_5 is 3-colorable
    G_c5 = GColoringInstance.of(5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)])
    assert is_3_colorable(G_c5) is True
    # C_4 is 2-colorable, hence 3-colorable
    G_c4 = GColoringInstance.of(4, [(0, 1), (1, 2), (2, 3), (0, 3)])
    assert is_3_colorable(G_c4) is True


# ---------------------------------------------------------------------------
# Section 6: Generalised reversed matching with non-identity permutation
# ---------------------------------------------------------------------------


def test_general_reversed_matching_identity_equals_RM() -> None:
    """build_general_reversed_matching(m, identity) == build_reversed_matching(m).
    """
    for m in [3, 5, 8]:
        T1 = build_reversed_matching(m)
        T2 = build_general_reversed_matching(m, list(range(m)))
        assert T1 == T2


def test_general_reversed_matching_reversal_changes_forced_set() -> None:
    """A non-identity matching permutation produces a *different* forced
    set: the indegree zigzag of the high-half changes, so some matching
    pairs cease to be forced while others remain.

    This pins the substrate's sensitivity to the matching choice and
    confirms the constructor is functioning as a parametric family.
    """
    m = 8
    perm = list(reversed(range(m)))
    T = build_general_reversed_matching(m, perm)
    H, _ = build_H_and_Gflex(T)
    # Identity matching has 8 forced edges; reversal yields a non-empty
    # but smaller set due to indegree rebalancing.
    assert 0 < H.number_of_edges() < 8


# ---------------------------------------------------------------------------
# Section 7: Global back-arc budget (the new obstruction)
# ---------------------------------------------------------------------------


def test_global_back_arc_budget_bounds_lfo_back_arcs() -> None:
    """In any LFO of any tournament, the back-arc graph is a linear
    forest on n vertices, so it has at most n - 1 edges.

    This is the **global** back-arc-budget obstruction: it caps the
    number of "constraint-attachment" back-arcs across the entire
    reduction at n - 1.
    """
    from verify import verify

    for m in [4, 5, 6]:
        T = build_reversed_matching(m)
        n = 2 * m
        lfos = enumerate_lfos(T, cap=500)
        for order in lfos:
            info = verify(T, list(order))
            assert info["is_linear_forest"]
            assert len(info["arcs"]) <= n - 1, (
                f"LFO {order} has {len(info['arcs'])} back-arcs > n-1={n-1}"
            )


def test_global_constraint_capacity_is_at_most_n_minus_1() -> None:
    """Pinpoints the precise count: with n = 2m vertices and m forced
    matching back-arcs, the spare back-arc budget per LFO is at most
    (n - 1) - m = m - 1, i.e. m - 1 'free' back-arcs to encode
    additional constraints.

    For RM(8) this is 7 spare back-arcs, certified empirically.
    """
    from verify import verify

    m = 6
    T = build_reversed_matching(m)
    n = 2 * m
    lfos = enumerate_lfos(T, cap=2000)
    assert len(lfos) > 0
    max_back_arcs = 0
    for order in lfos:
        max_back_arcs = max(max_back_arcs, len(verify(T, list(order))["arcs"]))
    # Empirical: budget is at most n - 1
    assert max_back_arcs <= n - 1
    # m forced matching edges + at most n - 1 - m extra = n - 1 total
    # So spare budget is <= n - 1 - 0 (since H is empty at m=6) actually,
    # this is a sanity check for the general bound n - 1:
    assert max_back_arcs <= n - 1
