"""Regression: every constructor must produce a graph whose ``to_graph6``
encoding round-trips to the same adjacency under the canonical orientation.

This guards against the bug fixed in ``_canonicalize``: ``nx.to_graph6_bytes``
writes adjacency in **node-iteration order**, so a constructor that adds
nodes in non-sorted order silently emits a graph6 string for a relabelled
graph. Verification then fails with edge-set mismatch.
"""
from __future__ import annotations

import pytest

from graphs import (
    blanusa_first,
    blanusa_second,
    desargues,
    flower_snark,
    from_graph6,
    heawood,
    k4,
    moebius_kantor,
    petersen,
    prism,
    q3,
    to_graph6,
)
from witness import orient


CONSTRUCTORS = [
    ("K_4", k4),
    ("prism_3", lambda: prism(3)),
    ("prism_5", lambda: prism(5)),
    ("Q_3", q3),
    ("Heawood", heawood),
    ("Moebius-Kantor", moebius_kantor),
    ("Desargues", desargues),
    ("Petersen", petersen),
    ("Blanusa-1", blanusa_first),
    ("Blanusa-2", blanusa_second),
    ("J_5", lambda: flower_snark(2)),
    ("J_7", lambda: flower_snark(3)),
]


@pytest.mark.parametrize("name,builder", CONSTRUCTORS)
def test_graph6_roundtrip_preserves_orientation(name, builder):
    G = builder()
    H = from_graph6(to_graph6(G))
    edges_G, _ = orient(G)
    edges_H, _ = orient(H)
    assert edges_G == edges_H, (
        f"{name}: graph6 round-trip relabelled the graph; "
        f"first 3 G={edges_G[:3]} H={edges_H[:3]}"
    )
