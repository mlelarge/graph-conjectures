"""Regression tests for the weighted-CDC Sigma_4-flow construction.

The construction succeeds where the discrete H_4 / oriented-4-CDC route
is dead for snarks. Three positive instances are checked here:

  - Petersen: the standard 6-pentagon CDC, *unorientable* in the H_4
    sense (see test_cdc_negative_calibration), nonetheless admits a
    weighted-CDC Sigma_4 flow that projects to a valid S^2 flow.
  - Blanusa-2: similar, with a mixed-length CDC.
  - J_5: similar, with mixed lengths.

The success criterion is the existing ``witness.verify_witness`` call
on the projected S^2 flow: max norm error and max vertex residual must
both fall below 1e-7.

A negative-direction sanity test: Petersen's 6-pentagon CDC, fed as a
*discrete* H_4 attempt via ``cdc.orient_cdc`` (i.e., basis-vector cycle
labels), must fail to orient. This is the calibration that motivates
the weighted relaxation in the first place.
"""
from __future__ import annotations

import numpy as np
import pytest

from cdc import find_cdc, orient_cdc
from cdc_weighted import (
    flow_from_weights,
    sigma4_to_s2,
    solve_first_weighted_cdc,
    solve_weighted_cdc,
)
from graphs import blanusa_second, flower_snark, petersen
from witness import verify_witness


@pytest.mark.parametrize("name,builder", [
    ("Petersen", petersen),
    ("Blanusa-2", blanusa_second),
    ("J_5", lambda: flower_snark(2)),
])
def test_weighted_cdc_produces_s2_flow(name, builder):
    G = builder()
    res = solve_first_weighted_cdc(
        G,
        max_cdcs=10,
        cdc_time_budget_s=60.0,
        solve_n_restarts=200,
    )
    assert res["status"] == "solved", (
        f"{name}: no weighted-CDC solution found; best rss={res['best_rss']:.3e}"
    )
    assert res["best_rss"] < 1e-20

    edges, V = flow_from_weights(G, res["cdc"], res["W"])
    # Sigma_4 sanity: every edge vector has sum zero and norm sqrt(2).
    sums = V.sum(axis=1)
    norms = np.linalg.norm(V, axis=1)
    assert np.allclose(sums, 0.0, atol=1e-8), f"{name}: edge component sums nonzero: {sums}"
    assert np.allclose(norms, np.sqrt(2.0), atol=1e-8), (
        f"{name}: edge norms not sqrt(2): {norms}"
    )

    # Sigma_4 -> S^2 projection should give a valid Kirchhoff flow.
    V3 = sigma4_to_s2(V)
    check = verify_witness(G, edges, V3.tolist(), tol=1e-7)
    assert check["ok"], f"{name}: S^2 flow verification failed: {check}"


def test_petersen_pentagon_cdc_is_unorientable_but_weighted_succeeds():
    """The discrete H_4 route fails on Petersen (6-pentagon CDC is
    unorientable), but the continuous relaxation succeeds. This is the
    headline calibration that the weighted ansatz is strictly stronger
    than the discrete one for snarks."""
    G = petersen()
    cdc = find_cdc(G, max_cycle_length=5, time_budget_s=10.0)
    assert cdc is not None
    assert all(len(c) == 5 for c in cdc) and len(cdc) == 6
    # Discrete H_4 attempt must fail.
    assert orient_cdc(cdc, G) is None
    # Continuous weighted attempt must succeed.
    res = solve_weighted_cdc(G, cdc, n_restarts=200, seed=2026)
    assert res["status"] == "solved", res["best_rss"]
    edges, V = flow_from_weights(G, cdc, res["W"])
    V3 = sigma4_to_s2(V)
    check = verify_witness(G, edges, V3.tolist(), tol=1e-7)
    assert check["ok"], check
