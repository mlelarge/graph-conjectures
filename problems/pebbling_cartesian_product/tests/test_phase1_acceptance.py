"""Phase 1 acceptance tests for the pebbling verifier.

Each test reproduces a known pebbling fact from a primary source. The
gating tests are ``test_pi_L_is_8`` and ``test_hurlbert_two_pebbling_witness``;
without those, no product-search result on Lemke graphs is trusted.
"""

from __future__ import annotations

import pytest

from pebbling_graphs import (
    cartesian_product,
    complete_graph,
    cycle_graph,
    hypercube,
    load_named_graph,
    path_graph,
)
from verify_pebbling_configuration import (
    PebblingNumberInconclusive,
    ResourceLimits,
    SizeSweepResult,
    distance_weight,
    is_r_solvable_for_size,
    pebbling_number,
    verify_configuration,
)


# --- pebbling numbers of standard families --------------------------------


@pytest.mark.parametrize("n,expected", [(2, 2), (3, 4), (4, 8)])
def test_pi_path(n: int, expected: int) -> None:
    assert pebbling_number(path_graph(n)) == expected


@pytest.mark.parametrize("n,expected", [(2, 2), (3, 3), (4, 4), (5, 5)])
def test_pi_complete(n: int, expected: int) -> None:
    assert pebbling_number(complete_graph(n)) == expected


@pytest.mark.parametrize("n,expected", [(3, 3), (4, 4), (5, 5)])
def test_pi_cycle(n: int, expected: int) -> None:
    assert pebbling_number(cycle_graph(n)) == expected


def test_pi_q3_is_8() -> None:
    assert pebbling_number(hypercube(3)) == 8


# --- Lemke-factor pebbling numbers (Phase 1 gating) -----------------------


@pytest.mark.parametrize("name", ["L", "L1", "L2"])
def test_pi_lemke_factor_is_8(name: str) -> None:
    """Reproduce pi(L) = pi(L1) = pi(L2) = 8 (Wood-Pulaj 2024 audit)."""
    assert pebbling_number(load_named_graph(name)) == 8


# --- Hurlbert 2-pebbling witness (Phase 1 gating) -------------------------


def test_hurlbert_two_pebbling_witness() -> None:
    """Reproduce Hurlbert math/0406024 witness: D=(8,1,1,1,0,0,0,1) on (a,b,c,d,w,x,y,z)
    is 1-pebbling-solvable but 2-pebbling-unsolvable at root x.

    0-based indices: a=4, b=3, c=5, d=7, w=2, x=1, y=0, z=6 -> values_by_index =
    [0, 0, 0, 1, 8, 1, 1, 1].
    """
    L = load_named_graph("L")
    cfg = (0, 0, 0, 1, 8, 1, 1, 1)
    root = 1  # vertex x in Hurlbert's labelling

    res1 = verify_configuration(L, root, cfg, target_pebbles=1)
    assert res1.outcome == "solvable", res1.message

    res2 = verify_configuration(L, root, cfg, target_pebbles=2)
    assert res2.outcome == "unsolvable", res2.message
    # Distance weight is exactly 2, so the simple weight test does NOT
    # rule out 2-pebbling: exhaustion is what proves unsolvability.
    assert res2.weight_pre_filter is not None
    assert res2.weight_pre_filter["weight"] == "2"
    assert res2.weight_pre_filter["rules_out_solvability"] is False


# --- distance-weight pre-filter -------------------------------------------


def test_distance_weight_path() -> None:
    """On P3, configuration (3, 0, 0) with root 2 has weight 3/4 < 1."""
    P3 = path_graph(3)
    w = distance_weight(P3, 2, (3, 0, 0))
    assert w.numerator == 3 and w.denominator == 4


def test_weight_filter_certifies_unsolvable() -> None:
    """If the distance weight is < 1, the verifier returns 'unsolvable'
    without entering the BFS."""
    P4 = path_graph(4)
    res = verify_configuration(P4, 3, (7, 0, 0, 0))
    assert res.outcome == "unsolvable"
    assert res.weight_pre_filter is not None
    assert res.weight_pre_filter["rules_out_solvability"] is True
    assert res.explored_states == 0


def test_solvable_emits_move_sequence() -> None:
    """Solvable configurations come back with a legal move sequence."""
    P3 = path_graph(3)
    res = verify_configuration(P3, 2, (4, 0, 0))
    assert res.outcome == "solvable"
    assert res.move_sequence is not None and len(res.move_sequence) >= 1
    # Replay the moves and check the root ends with at least 1 pebble.
    state = list((4, 0, 0))
    adj = P3.adjacency()
    for src, dst in res.move_sequence:
        assert state[src] >= 2
        assert dst in adj[src]
        state[src] -= 2
        state[dst] += 1
    assert state[2] >= 1


# --- input validation ------------------------------------------------------


def test_invalid_root_returns_invalid_input() -> None:
    res = verify_configuration(path_graph(3), 5, (1, 1, 1))
    assert res.outcome == "invalid_input"


def test_negative_pebbles_rejected() -> None:
    res = verify_configuration(path_graph(3), 0, (1, -1, 1))
    assert res.outcome == "invalid_input"


def test_wrong_length_rejected() -> None:
    res = verify_configuration(path_graph(3), 0, (1, 1))
    assert res.outcome == "invalid_input"


# --- Cartesian product construction ---------------------------------------


def test_cartesian_product_p3_p3_edge_count() -> None:
    P3 = path_graph(3)
    G = cartesian_product(P3, P3)
    # |V| = 9, |E| = |V(P3)| * |E(P3)| + |V(P3)| * |E(P3)| = 3*2 + 3*2 = 12
    assert G.n == 9
    assert len(G.edges) == 12


def test_lemke_square_edge_count() -> None:
    L = load_named_graph("L")
    LL = cartesian_product(L, L)
    # 8 * 13 + 8 * 13 = 208
    assert LL.n == 64
    assert len(LL.edges) == 208


def test_q3_via_cartesian_product_p2_p2_p2() -> None:
    P2 = path_graph(2)
    G = cartesian_product(cartesian_product(P2, P2), P2)
    Q3 = hypercube(3)
    assert G.n == Q3.n
    assert set(G.edges) == set(Q3.edges)


# --- determinism -----------------------------------------------------------


def test_deterministic_state_set_hash() -> None:
    """Repeated runs on the same input produce the same state-set hash."""
    L = load_named_graph("L")
    cfg = (0, 0, 0, 1, 8, 1, 1, 1)
    a = verify_configuration(L, 1, cfg, target_pebbles=2)
    b = verify_configuration(L, 1, cfg, target_pebbles=2)
    assert a.outcome == b.outcome == "unsolvable"
    assert a.state_set_hash == b.state_set_hash
    assert a.explored_states == b.explored_states


# --- tri-state SizeSweepResult and inconclusive propagation ---------------


def test_size_sweep_returns_unsolvable_witness() -> None:
    """At size 7 on P4, root 0, there is some unsolvable configuration."""
    res = is_r_solvable_for_size(path_graph(4), 0, 7)
    assert isinstance(res, SizeSweepResult)
    assert res.status == "unsolvable_witness"
    assert sum(res.witness) == 7


def test_size_sweep_returns_all_solvable() -> None:
    """At size 8 on P4, root 0, every configuration is solvable."""
    res = is_r_solvable_for_size(path_graph(4), 0, 8)
    assert res.status == "all_solvable"
    assert res.witness == []


def test_size_sweep_inconclusive_with_tight_budget() -> None:
    """A pathologically tight budget produces 'inconclusive', not a false witness."""
    # Tiny max_states: anything that needs even one BFS step trips it.
    L = load_named_graph("L")
    limits = ResourceLimits(max_states=1, max_seconds=60.0)
    res = is_r_solvable_for_size(L, 0, 8, limits=limits)
    # We expect inconclusive on the first BFS-needing config; if the very
    # first config happens to be unsolvable by the weight pre-filter, the
    # sweep can finish, but for this graph that is not the case.
    assert res.status == "inconclusive"
    assert res.witness != []


def test_pebbling_number_raises_on_inconclusive() -> None:
    """When the verifier hits its budget, pebbling_number must raise rather
    than silently inflate the answer."""
    L = load_named_graph("L")
    limits = ResourceLimits(max_states=1, max_seconds=60.0)
    with pytest.raises(PebblingNumberInconclusive) as excinfo:
        pebbling_number(L, limits=limits)
    assert "inconclusive_within_budget" in str(excinfo.value)
