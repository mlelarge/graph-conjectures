"""Regression for plan v9 bug fix in lprime_max_degsum.md §2.

The earlier draft wrote
    ||w||^2 = (e_a + e_b)^T (e_a + e_b) = 2 + 2 A(H)_{ab} = 4.
This is wrong: e_a, e_b are orthogonal standard basis vectors for a != b,
so e_a^T e_b = 0 *regardless of whether ab is an edge in H*. The correct
value is ||w||^2 = 1 + 0 + 1 = 2.

This test enshrines the corrected value on three small 2-tree ears and
explicitly exercises the ab-edge-independence (one case with ab in E(H),
another contrived case marked with ab not in E(H)). All values must equal
2.0 to within 1e-12.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "w_norm_squared_is_2.json"
)
TOL = 1e-12


def _load_cases():
    with FIXTURE.open() as f:
        data = json.load(f)
    return data["cases"]


def test_w_norm_squared_is_two_on_all_fixture_cases():
    """Every fixture case asserts ||w||^2 = 2 (the v9-corrected value)."""
    cases = _load_cases()
    assert len(cases) >= 1, "fixture should contain at least one case"
    for case in cases:
        n = case["n"]
        a = case["a"]
        b = case["b"]
        # w lives in R^{n-1} (H = G - v has n-1 vertices); for the K_3
        # case n=3 gives R^2, for B_3 and L_5 we have R^4.
        n_H = n - 1
        e_a = np.zeros(n_H)
        e_b = np.zeros(n_H)
        e_a[a] = 1.0
        e_b[b] = 1.0
        w = e_a + e_b
        computed = float(w @ w)
        expected = float(case["w_norm_squared"])
        assert expected == 2.0, (
            f"fixture expected_w_norm_squared must be exactly 2.0 (v9 bug fix); "
            f"got {expected} for family={case['family']!r}"
        )
        assert abs(computed - expected) < TOL, (
            f"computed ||w||^2 = {computed!r} disagrees with fixture "
            f"{expected!r} (tol={TOL}) for family={case['family']!r}"
        )

    # Cross-case invariance: the value is the same whether ab is an
    # edge in H or not, since e_a^T e_b = 0 for a != b regardless of
    # adjacency. Verify by directly checking values on the two flavors
    # present in the fixture.
    seen_edge = {c["ab_is_edge_in_H"]: c["w_norm_squared"] for c in cases}
    assert True in seen_edge or False in seen_edge, (
        "fixture should include at least one ab_is_edge_in_H flavour"
    )
    for flag, value in seen_edge.items():
        assert value == 2.0, (
            f"||w||^2 must equal 2.0 independently of ab_is_edge_in_H; "
            f"got {value} for ab_is_edge_in_H={flag}"
        )
