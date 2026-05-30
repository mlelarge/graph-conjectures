"""Regression test: the n=7 candidate is a genuine 2-in-3 clause gadget (D72).

The Loader Gap Lemma is FALSE.  Augmenting the D71 n=7 candidate with
one padding vertex and six forced loaders yields a 14-vertex tournament
whose realized port relation is exactly {011,101,110} = 2-in-3, the
NP-complete relation.  This is the first confirmed composable
non-Schaefer ordering primitive; the remaining barrier to NP-hardness
is fanout (variable reuse), not clause realizability.
"""
from __future__ import annotations

import itertools
import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from port_loader_realizability import (  # noqa: E402
    CANDIDATE_G,
    CANDIDATE_ORIENT,
    CANDIDATE_PORTS,
    build_augmented,
    enumerate_lfos,
    is_forced_backarc,
    port_relation_of,
)
from verify import verify  # noqa: E402


TWO_IN_THREE = frozenset({(0, 1, 1), (1, 0, 1), (1, 1, 0)})


def _canonical_loaders():
    g = 7
    n_extra = 7
    port_vertices = [v for pr in CANDIDATE_PORTS for v in pr]
    indeg = {v: sum(CANDIDATE_G[i][v] for i in range(g)) for v in port_vertices}
    by_hard = sorted(port_vertices, key=lambda v: -indeg[v])
    loader_slots = list(range(g + n_extra - len(port_vertices), g + n_extra))
    loaders = {}
    for slot, v in zip(reversed(loader_slots), by_hard):
        loaders[slot] = v
    return n_extra, loaders


def test_enumerator_matches_bruteforce_on_gadget():
    brute = {
        P for P in itertools.permutations(range(7))
        if verify(CANDIDATE_G, list(P))["is_linear_forest"]
    }
    enum = set(enumerate_lfos(CANDIDATE_G))
    assert enum == brute
    assert len(enum) == 35


def test_augmented_is_valid_tournament():
    n_extra, loaders = _canonical_loaders()
    T = build_augmented(CANDIDATE_G, n_extra, loaders)
    n = len(T)
    assert n == 14
    for i in range(n):
        for j in range(i + 1, n):
            assert T[i][j] + T[j][i] == 1


def test_all_loaders_forced():
    n_extra, loaders = _canonical_loaders()
    T = build_augmented(CANDIDATE_G, n_extra, loaders)
    for ell, v in loaders.items():
        assert is_forced_backarc(T, ell, v), (ell, v)


def test_realized_relation_is_exactly_2in3():
    n_extra, loaders = _canonical_loaders()
    T = build_augmented(CANDIDATE_G, n_extra, loaders)
    rel = port_relation_of(T, CANDIDATE_PORTS, CANDIDATE_ORIENT)
    assert rel == TWO_IN_THREE


def test_port_back_degrees_within_budget():
    n_extra, loaders = _canonical_loaders()
    T = build_augmented(CANDIDATE_G, n_extra, loaders)
    n = len(T)
    port_vertices = [v for pr in CANDIDATE_PORTS for v in pr]
    for P in enumerate_lfos(T):
        pos = [0] * n
        for i, x in enumerate(P):
            pos[x] = i
        for v in port_vertices:
            d = sum(
                1 for u in range(n)
                if (T[v][u] and pos[v] > pos[u]) or (T[u][v] and pos[u] > pos[v])
            )
            assert d <= 2, (v, d)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
