"""Regression: an interval_witness certificate must be independently
re-verifiable via :func:`interval.replay_krawczyk`.

For Petersen and K_4 we (a) generate a numerical witness, (b) issue an
interval certificate, (c) hand the certificate to ``replay_krawczyk``
without sharing any internal state, and confirm the replay reaches the
same verdict, with positive containment margin and matching polynomial
hash.
"""
from __future__ import annotations

import json

import pytest

from graphs import k4, petersen
from interval import krawczyk_certify, replay_krawczyk
from witness import find_witness


@pytest.mark.parametrize("name,builder", [("K_4", k4), ("Petersen", petersen)])
def test_interval_cert_is_replayable(name, builder, tmp_path):
    G = builder()
    r = find_witness(G, restarts=200, seed=2026, residual_threshold=1e-15)
    assert r.status == "witness"
    result, cert = krawczyk_certify(
        G, r.vectors, radius=1e-5, dps=50, name=name
    )
    assert result.certified, f"{name}: krawczyk_certify failed: {result.notes}"
    cert_path = tmp_path / f"{name}.interval.json"
    cert_path.write_text(json.dumps(cert))
    reloaded = json.loads(cert_path.read_text())
    replay = replay_krawczyk(reloaded)
    assert replay["ok"] is True
    assert replay["polynomial_hash_match"] is True
    assert replay["verdict_matches_cert"] is True
