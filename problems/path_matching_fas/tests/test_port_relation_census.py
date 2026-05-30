"""Regression tests for the Port-Relation Census (D71, Q7.1).

The census classifies the relations R_T ⊆ {0,1}^k that a tournament
gadget can realize on k port pairs over all its valid LFOs, and the
composable shadow R_comp (vectors with a residual-back-degree witness).

The decisive Q7.1 finding pinned here:

  * Non-Schaefer R_T relations DO exist (NAE-type) from arity k = 3.
  * But every such relation's composable shadow R_comp is Schaefer —
    the degree-2 back-arc budget destroys non-Schaefer-ness under
    composition.  No composable non-Schaefer primitive exists at
    n ≤ 6, k = 3 with vertex-disjoint ports (n = 6 is the first
    non-vacuous arity-3 disjoint-port case; n = 5, k = 3 has no
    disjoint ports).

Composability requires vertex-DISJOINT ports (independently
attachable) and is judged on R_comp under all 2^k port orientations
(non-Schaefer-ness is not flip-invariant).

This is the evidence for the Q7.1 impossibility direction (no
composable non-monotone/non-Schaefer ordering primitive ⇒ hardness
route closed ⇒ Path-FAS likely in P).
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from port_relation_census import (  # noqa: E402
    build_lfo_cache,
    census,
    is_downward_closed,
    port_relation,
    port_relation_cached,
    schaefer_flags,
    valid_lfos,
)


# ----------------------------------------------------------------------
# 1. Classification primitives
# ----------------------------------------------------------------------

def test_downward_closed_basics():
    # {00, 10, 11} is NOT downward-closed (01 <= 11 missing).
    assert not is_downward_closed(frozenset({(0, 0), (1, 0), (1, 1)}), 2)
    # full cube is downward-closed
    assert is_downward_closed(frozenset({(0, 0), (0, 1), (1, 0), (1, 1)}), 2)
    # downward-closed example
    assert is_downward_closed(frozenset({(0, 0), (1, 0)}), 2)


def test_nae3_is_non_schaefer():
    nae3 = frozenset(
        b for b in [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
                    (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
        if b not in {(0, 0, 0), (1, 1, 1)}
    )
    flags = schaefer_flags(nae3, 3)
    assert flags["non_schaefer"], flags


def test_dual_horn_shadow_is_schaefer():
    # {001, 100, 101} (the R_comp shadow of the n=5 NAE gadget) is
    # dual-Horn (closed under OR), hence Schaefer.
    shadow = frozenset({(0, 0, 1), (1, 0, 0), (1, 0, 1)})
    flags = schaefer_flags(shadow, 3)
    assert flags["dual_horn"], flags
    assert not flags["non_schaefer"], flags


# ----------------------------------------------------------------------
# 2. Census decisions (small n, exact)
# ----------------------------------------------------------------------

def test_census_disjoint_ports_require_2k_vertices():
    """Composable ports must be vertex-disjoint (independently
    attachable).  k=3 needs >= 6 vertices, so n=5,k=3 has no disjoint
    port-tuples and the census is vacuous."""
    out = census(5, 3)
    assert out["disjoint_port_tuples_per_tournament"] == 0
    assert out["distinct_relations"] == 0
    assert out["composable_nonschaefer_found"] is False


def test_census_n5_k2_disjoint_all_schaefer():
    """k=2 (binary) relations are always bijunctive, so never
    non-Schaefer regardless of port disjointness."""
    out = census(5, 2)
    assert out["disjoint_port_tuples_per_tournament"] == 15
    assert out["composable_nonschaefer_found"] is False


def test_shared_vertex_ports_encode_transitivity_artifact():
    """Ports sharing all vertices of a triangle {2,3,4} make R_T = NAE_3
    by order-transitivity alone (no 3-cycle in a total order) — NOT a
    Path-FAS property.  Such ports are not vertex-disjoint, so they are
    excluded from the composable census."""
    T = [[0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 1, 0, 0, 1],
         [1, 1, 1, 0, 0], [1, 1, 0, 1, 0]]
    ports = [(2, 3), (2, 4), (3, 4)]  # all three pairs of {2,3,4}
    lfos = valid_lfos(T)
    R, _ = port_relation(T, lfos, ports)
    # transitivity: a total order on {2,3,4} has no 3-cycle, so exactly
    # the two cyclic patterns (an antipodal pair) are excluded.
    assert len(R) == 6
    missing = {(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
               (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)} - set(R)
    assert len(missing) == 2
    a, b = list(missing)
    assert a == tuple(1 - x for x in b)  # antipodal (complementary)
    # ports share vertices -> excluded from the composable census
    shared = set()
    is_disjoint = True
    for x, y in ports:
        if x in shared or y in shared:
            is_disjoint = False
        shared.update([x, y])
    assert not is_disjoint


# ----------------------------------------------------------------------
# 3. Arity-2 can never be non-Schaefer
# ----------------------------------------------------------------------

def test_arity2_always_schaefer():
    """Every relation on {0,1}^2 is bijunctive (binary clauses)."""
    import itertools
    for size in range(5):
        for combo in itertools.combinations(
            [(0, 0), (0, 1), (1, 0), (1, 1)], size
        ):
            R = frozenset(combo)
            if not R:
                continue
            assert not schaefer_flags(R, 2)["non_schaefer"], R


# ----------------------------------------------------------------------
# 4. The n=7 lenient 2-in-3 candidate is a strict artifact
# ----------------------------------------------------------------------

def test_n7_lenient_2in3_candidate_strict_empty():
    """At n=7 a genuinely disjoint-port gadget has lenient R_comp =
    {011,101,110} = exactly-2-in-3 (non-Schaefer), but each vector has
    only ONE capacity-witness, so R_comp_strict is empty.

    Status is UNRESOLVED (see docs/port_relation_census.md §4-5): the
    idealized degree-reserved composition realizes exactly 2-in-3, but
    realizing the reservation as a tournament hits the score-window gap
    obstruction on low-degree port vertices.  This test pins only the
    relation facts, not the (open) composability verdict."""
    T = [[0, 0, 1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0],
         [0, 1, 0, 1, 0, 1, 0], [1, 1, 0, 0, 1, 0, 0],
         [1, 1, 1, 0, 0, 0, 0], [1, 1, 0, 1, 1, 0, 1],
         [1, 1, 1, 1, 1, 0, 0]]
    ports = [(0, 1), (3, 4), (5, 6)]
    o = (0, 1, 1)
    # ports are vertex-disjoint
    verts = [v for p in ports for v in p]
    assert len(set(verts)) == 6
    cache = build_lfo_cache(T)
    R_base, Rc_base, Rcs_base = port_relation_cached(cache, ports)

    def flip(rel):
        return frozenset(tuple(b ^ oi for b, oi in zip(t, o)) for t in rel)

    R_comp = flip(Rc_base)
    R_comp_strict = flip(Rcs_base)
    # lenient shadow is exactly-2-in-3, non-Schaefer
    assert R_comp == frozenset({(0, 1, 1), (1, 0, 1), (1, 1, 0)})
    assert schaefer_flags(R_comp, 3)["non_schaefer"]
    # strict shadow is empty -> not a genuine primitive
    assert R_comp_strict == frozenset()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
