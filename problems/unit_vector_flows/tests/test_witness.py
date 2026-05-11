"""Regression tests for the numerical S²-flow witness finder.

These cases all admit an S²-flow either from a nowhere-zero 4-flow (Tutte's
three-coordinate construction) or from an explicit construction in
Houdrouge–Miraftab–Morin 2026 (Petersen). They must return ``status ==
'witness'`` and pass independent verification.

Snarks are intentionally excluded from regression: their status is exactly
the open question, not a fixed-point check.
"""
from __future__ import annotations

import pytest

from graphs import (
    desargues,
    heawood,
    is_cubic_bridgeless,
    k4,
    moebius_kantor,
    petersen,
    prism,
    q3,
)
from witness import find_witness, verify_witness


POSITIVES = [
    ("K_4", k4),
    ("prism_3", lambda: prism(3)),
    ("prism_5", lambda: prism(5)),
    ("Q_3", q3),
    ("Heawood", heawood),
    ("Moebius-Kantor", moebius_kantor),
    ("Desargues", desargues),
    ("Petersen", petersen),
]


@pytest.mark.parametrize("name,builder", POSITIVES)
def test_cubic_bridgeless(name, builder):
    G = builder()
    assert is_cubic_bridgeless(G), f"{name} is not cubic bridgeless"


@pytest.mark.parametrize("name,builder", POSITIVES)
def test_witness_found(name, builder):
    G = builder()
    result = find_witness(G, restarts=400, seed=2026, residual_threshold=1e-10)
    assert result.status == "witness", (
        f"{name}: best_rss={result.best_residual_squared:.3e} "
        f"max|res|={result.best_max_abs_residual:.3e} after {result.n_restarts} restarts"
    )


@pytest.mark.parametrize("name,builder", POSITIVES)
def test_witness_verifies(name, builder):
    G = builder()
    result = find_witness(G, restarts=400, seed=2026, residual_threshold=1e-10)
    check = verify_witness(G, result.edges, result.vectors, tol=1e-7)
    assert check["ok"], f"{name}: {check}"
