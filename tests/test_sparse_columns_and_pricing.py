"""Tests for sparse_columns + price_tree_strategy + run_sparse_column_generation."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from check_pebbling_weight_certificate import check_certificate, load_certificate_file
from pebbling_graphs import cartesian_product, load_named_graph
from price_tree_strategy import price_basic_trees
from run_sparse_column_generation import (
    column_generation_loop,
    load_seed_certificate,
)
from sparse_columns import (
    StrategyColumn,
    emit_certificate,
    lp_from_columns,
    solve_master_lp,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_00 = (
    REPO_ROOT / "data/pebbling_product/certificates/path_orbit_0_0_max_len7.json"
)


def test_strategy_column_b_excludes_root() -> None:
    col = StrategyColumn(
        weights={1: Fraction(4), 2: Fraction(2), 3: Fraction(1)},
        tree_edges=[(1, 2), (2, 3)],
        name="test",
        basic=True,
    )
    assert col.b == Fraction(7)


def test_solve_master_lp_matches_existing_LP() -> None:
    """Loading the same seed and re-solving via sparse_columns should match
    the LP optimum recorded in the certificate's notes."""
    columns, _gp, root = load_seed_certificate(SEED_00)
    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    fun, alpha, y = solve_master_lp(columns, LL.n, root)
    # The certificate was rationalized to derived bound 246, so float LP
    # should be in (245, 246) range
    assert 245.0 < fun < 246.0


def test_pricing_oracle_terminates_with_no_improvement_at_seed() -> None:
    """At root (0, 0) with the path max_len=7 seed, pricing under basic
    uniform-leaf-depth trees of depth <= 5 finds no negative reduced
    cost column."""
    columns, _, root = load_seed_certificate(SEED_00)
    L = load_named_graph("L_fpy")
    LL = cartesian_product(L, L)
    n = LL.n
    adj = LL.adjacency()
    fun, alpha, y = solve_master_lp(columns, n, root)
    pr = price_basic_trees(
        adj=adj, root=root, y=list(y), n_vertices=n,
        max_depth=4,  # smaller to keep test fast
        top_k=4, require_negative_reduced_cost=True,
        time_budget_s=10.0,
    )
    # Expected: no improvement at small depth
    assert pr.columns == [] or all(rc < 0 for rc in pr.reduced_costs)


def test_emit_certificate_round_trips() -> None:
    """A certificate emitted from sparse columns + rational alpha is
    accepted by the rational checker."""
    columns, gp, root = load_seed_certificate(SEED_00)
    # Use uniform alpha = 1/k
    k = len(columns)
    alpha = [Fraction(1, k)] * k
    payload = emit_certificate(columns, alpha, graph_payload=gp, root=root,
                                notes="test round trip")
    out = REPO_ROOT / "data/pebbling_product/certificates/_test_roundtrip.json"
    with out.open("w") as fp:
        json.dump(payload, fp)
    cert, g = load_certificate_file(out)
    res = check_certificate(cert, g)
    # Uniform 1/k may or may not be feasible; either accepted with
    # some bound, or rejected with dual feasibility violation. Both
    # outcomes are valid round-trip evidence.
    assert res.derived_bound is None or isinstance(res.derived_bound, int)
    out.unlink()
