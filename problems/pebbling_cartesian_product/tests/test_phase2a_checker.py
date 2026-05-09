"""Phase 2a acceptance tests for the rational weight-function checker.

Each test exercises a documented case from
``data/pebbling_product/certificates/`` or generates a tree certificate
on the fly. Perturbation tests target the four kinds of failure the
checker must catch:

1. tree edge that is not an edge of ``G``;
2. parent-doubling violation (basic strategy);
3. dual feasibility violation;
4. claimed bound stronger than the dual multipliers can support.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from check_pebbling_weight_certificate import (
    check_certificate,
    load_certificate_file,
    make_path_certificate,
    make_star_certificate,
    parse_certificate,
)
from pebbling_graphs import make_graph, path_graph
from verify_pebbling_configuration import pebbling_number


CERTIFICATE_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "pebbling_product" / "certificates"
)


# --- helpers --------------------------------------------------------------


def _check(payload: dict):
    cert = parse_certificate(payload)
    gp = payload["graph"]
    g = make_graph(int(gp["n"]), gp["edges"], name=gp.get("name", ""))
    return check_certificate(cert, g)


# --- positive: persisted small certificates -------------------------------


@pytest.mark.parametrize(
    "filename,expected_bound",
    [
        ("P3_root0_le4.json", 4),
        ("P4_root0_le8.json", 8),
        ("K1_3_root0_le4.json", 4),
        ("C4_root0_le4.json", 4),
    ],
)
def test_persisted_certificate_accepted(filename: str, expected_bound: int) -> None:
    cert, g = load_certificate_file(CERTIFICATE_DIR / filename)
    res = check_certificate(cert, g)
    assert res.accepted, res.message
    assert res.derived_bound == expected_bound
    assert res.claimed_bound == expected_bound


def test_c4_multi_strategy_matches_pi() -> None:
    """The 2-strategy averaging certificate for C4 should match pi(C4) = 4 exactly."""
    from pebbling_graphs import cycle_graph

    cert, g = load_certificate_file(CERTIFICATE_DIR / "C4_root0_le4.json")
    res = check_certificate(cert, g)
    assert res.accepted
    pi = pebbling_number(cycle_graph(4))
    assert res.derived_bound == pi == 4
    # Multiplier values are rational, sum is 7/2
    assert res.sum_alpha_b == "7/2"


# --- positive: generated tree certificates --------------------------------


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 8])
def test_generated_path_certificate_accepted(n: int) -> None:
    payload = make_path_certificate(n, root=0)
    res = _check(payload)
    assert res.accepted, res.message
    assert res.derived_bound == 2 ** (n - 1)


@pytest.mark.parametrize("k", [1, 2, 3, 5, 8])
def test_generated_star_certificate_accepted(k: int) -> None:
    payload = make_star_certificate(k)
    res = _check(payload)
    assert res.accepted, res.message
    assert res.derived_bound == k + 1


# --- negative: tree edge not in G ----------------------------------------


def test_reject_tree_edge_not_in_graph() -> None:
    payload = make_path_certificate(4, root=0)
    # Replace edge [2, 3] with the non-edge [0, 3] (skipping vertex 2)
    payload["strategies"][0]["tree_edges"] = [[0, 1], [1, 2], [0, 3]]
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "strategy_tree_edges"
    assert res.failure["edge"] == [0, 3]


# --- negative: tree disconnected -----------------------------------------


def test_reject_disconnected_tree() -> None:
    # P5 with two disjoint edges: [0,1] and [3,4] - root 0 cannot reach
    # the second component.
    payload = {
        "graph": {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "name": "P5"},
        "root": 0,
        "claimed_bound": 16,
        "strategies": [
            {
                "tree_edges": [[0, 1], [3, 4]],
                "weights": {"0": "0", "1": "1", "3": "1", "4": "1"},
                "basic": True,
            }
        ],
        "dual_multipliers": ["1"],
    }
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "strategy_tree_structure"


# --- negative: basic doubling violation -----------------------------------


def test_reject_broken_basic_doubling() -> None:
    payload = make_path_certificate(4, root=0)
    # Wrong: w(2) should be 2 (= w(1)/2 = 4/2). Set it to 3.
    payload["strategies"][0]["weights"]["2"] = "3"
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "strategy_basic_doubling"
    assert res.failure["vertex"] == 2


def test_nonbasic_doubling_accepted_when_inequality_holds() -> None:
    """Nonbasic strategies allow w(parent) > 2 w(child)."""
    payload = make_path_certificate(4, root=0)
    # Inflate w(1) from 4 to 5; basic would reject, nonbasic accepts.
    payload["strategies"][0]["weights"]["1"] = "5"
    payload["strategies"][0]["basic"] = False
    # Need to also bump dual multiplier or weights to keep dual feasible.
    # With w = (0, 5, 2, 1), dual feasibility at v=3 needs alpha*1 >= 1,
    # already holds. b_T = 5+2+1 = 8 -> derived = 9, but claimed is 8.
    # Bump claimed to 9.
    payload["claimed_bound"] = 9
    res = _check(payload)
    assert res.accepted, res.message
    assert res.derived_bound == 9


# --- negative: dual feasibility violation --------------------------------


def test_reject_dual_infeasible() -> None:
    payload = make_path_certificate(4, root=0)
    # Halve the dual multiplier so alpha*w(3) = 1/2 < 1
    payload["dual_multipliers"] = ["1/2"]
    payload["claimed_bound"] = 4  # also weaken the claim
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "dual_feasibility"
    assert res.failure["vertex"] == 3


# --- negative: claim too strong ------------------------------------------


def test_reject_claim_too_strong() -> None:
    payload = make_path_certificate(4, root=0)
    payload["claimed_bound"] = 7  # actual derived is 8
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "claim_too_strong"
    assert res.derived_bound == 8


# --- negative: structural / input -----------------------------------------


def test_reject_negative_dual_multiplier() -> None:
    payload = make_path_certificate(4, root=0)
    payload["dual_multipliers"] = ["-1"]
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "dual_multipliers"


def test_reject_nonzero_root_weight() -> None:
    payload = make_path_certificate(4, root=0)
    payload["strategies"][0]["weights"]["0"] = "1"
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "strategy_weight_root"


def test_reject_negative_weight() -> None:
    payload = make_path_certificate(4, root=0)
    payload["strategies"][0]["weights"]["3"] = "-1"
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "strategy_weight_nonneg"


def test_reject_weight_outside_tree() -> None:
    # Strategy uses only edge [0,1]; weight on vertex 2 must be 0.
    payload = {
        "graph": {"n": 3, "edges": [[0, 1], [1, 2]], "name": "P3"},
        "root": 0,
        "claimed_bound": 2,
        "strategies": [
            {
                "tree_edges": [[0, 1]],
                "weights": {"0": "0", "1": "1", "2": "1"},
                "basic": True,
            }
        ],
        "dual_multipliers": ["1"],
    }
    res = _check(payload)
    assert not res.accepted
    assert res.failure is not None
    assert res.failure["stage"] == "strategy_weight_outside_tree"


# --- cross-check: certificate is no stronger than the exact verifier ----


@pytest.mark.parametrize("n", [2, 3, 4, 5])
def test_path_certificate_matches_exact_pi(n: int) -> None:
    """A successful path certificate must claim at least the exact pi.
    Otherwise either the certificate or the verifier is wrong."""
    payload = make_path_certificate(n, root=0)
    res = _check(payload)
    assert res.accepted
    pi = pebbling_number(path_graph(n))
    assert res.derived_bound >= pi, (
        f"certificate derived {res.derived_bound} but pi(P{n}) = {pi}"
    )


# --- failure-message readability -----------------------------------------


def test_failure_message_is_human_readable() -> None:
    payload = make_path_certificate(4, root=0)
    payload["claimed_bound"] = 7
    res = _check(payload)
    assert not res.accepted
    assert "7" in res.message
    assert "8" in res.message
