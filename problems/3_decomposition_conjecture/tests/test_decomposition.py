"""Regression tests for scripts/decomposition.py.

These tests check the 3-decomposition verifier and the trace-set computer
on small hand-built cases.
"""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

from decomposition import (  # noqa: E402
    BRIDGE_PORT_STATES,
    are_2pole_traces_compatible,
    compute_trace_set,
    compute_trace_set_2pole,
    edge_key,
    find_3_decomposition,
    is_subcubic_partition_valid,
    verify_bridge_side_realisable,
    verify_decomposition,
)
from gadget_lattice import build_payload  # noqa: E402


# ---- brute-force 3-decomposition finder on small cubic graphs -------------


def test_brute_force_K4():
    G = nx.complete_graph(4)
    sol = find_3_decomposition(G)
    assert sol is not None
    ok, _ = verify_decomposition(G, sol)
    assert ok


def test_brute_force_K33():
    G = nx.complete_bipartite_graph(3, 3)
    sol = find_3_decomposition(G)
    assert sol is not None
    ok, _ = verify_decomposition(G, sol)
    assert ok


def test_brute_force_prism():
    """The 3-prism (triangular prism) is the smallest non-K_4 cubic graph."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0),       # bottom triangle
                      (3, 4), (4, 5), (5, 3),       # top triangle
                      (0, 3), (1, 4), (2, 5)])      # vertical edges
    sol = find_3_decomposition(G)
    assert sol is not None
    ok, reason = verify_decomposition(G, sol)
    assert ok, reason


def test_brute_force_petersen():
    """Petersen graph: 10 vertices, 15 edges. Known 3-decomposable
    (Hamiltonian cubic case; Petersen is not Hamiltonian, but
    Hoffmann-Ostenhof-Kaiser-Ozeki / Bachstein settle the
    non-Hamiltonian 3-connected planar/surface cases too, and
    Zhang-Szeider verified n<=28). Test brute-force finds one."""
    G = nx.petersen_graph()
    sol = find_3_decomposition(G)
    assert sol is not None
    ok, reason = verify_decomposition(G, sol)
    assert ok, reason


# ---- 3-decomposition verifier on small cubic graphs -------------------------


def test_K4_star_plus_triangle_is_3_decomposition():
    G = nx.complete_graph(4)
    labels = {
        edge_key(0, 1): "T",
        edge_key(0, 2): "T",
        edge_key(0, 3): "T",
        edge_key(1, 2): "C",
        edge_key(2, 3): "C",
        edge_key(1, 3): "C",
    }
    ok, reason = verify_decomposition(G, labels)
    assert ok, reason


def test_K4_missing_tree_edge_fails():
    G = nx.complete_graph(4)
    labels = {
        edge_key(0, 1): "T",
        edge_key(0, 2): "T",
        edge_key(0, 3): "C",   # would-be tree edge swapped to C
        edge_key(1, 2): "C",
        edge_key(2, 3): "C",
        edge_key(1, 3): "C",
    }
    ok, reason = verify_decomposition(G, labels)
    assert not ok
    assert "tree" in reason.lower() or "spanning" in reason.lower() or "|T|" in reason


def test_K33_hamilton_cycle_plus_matching():
    # K_{3,3}: Hamilton cycle 0-3-1-4-2-5-0; perfect matching {0-3, 1-4, 2-5}.
    # Actually that overlaps. Build a fresh decomposition:
    #   Hamilton cycle of K_{3,3}: 0-3-1-4-2-5-0.
    #   Tree: take path 0-3-1-4-2-5 (5 edges, spanning, acyclic).
    #   Remaining edges: 0-5 (was cycle closing), 0-4, 1-5, 2-3.
    #   Cycle subgraph: 0-4-2-3-1-5-0 has 6 edges -- too many.
    # Instead pick: T = star at 0 (0-3, 0-4, 0-5) + 3-1, 3-2 (path extension).
    #   But 3-2 is not an edge of K_{3,3} (both in same side). Drop.
    # Try: T = {0-3, 0-4, 0-5, 3-1, 4-2}. That's 5 edges.
    #   T edges: 0-3, 0-4, 0-5, 1-3, 2-4. Spans {0,1,2,3,4,5}? Yes.
    #   Acyclic? Yes (it's a tree).
    #   Remaining edges of K_{3,3}: 1-4, 1-5, 2-3, 2-5. That's 4 edges.
    #   Need: 2-regular subgraph + matching, partitioning 4 edges.
    #   Try C = {1-4, 2-5, ...} – need a cycle. 1-4-2-5-1 is a 4-cycle.
    #     C = {1-4, 4-2, 2-5, 5-1}. But 4-2 == 2-4 was in T. Conflict.
    # Try again. T = {0-3, 0-4, 0-5, 1-4, 2-5}. Acyclic? Yes.
    #   Remaining: 1-3, 2-3, 2-4, 1-5. Form a 4-cycle 1-3-2-4-1? 1-3, 3-2, 2-4, 4-1 -- 4-1 is in T.
    #   Hm.
    # K_{3,3} 3-decomp: trees of K_{3,3} have 5 edges; cotree 4 edges. a = c+2.
    # a + b + c = 6, b + 2c = 4. Solutions:
    #   c=0: a=2, b=4. But a>=3 for non-empty cycle. So c>=1.
    #   c=1: a=3, b=2. Cycle on 3 vertices in K_{3,3}? K_{3,3} is bipartite,
    #        no odd cycles. So a=3 impossible.
    #   c=2: a=4, b=0. Cycle on 4 vertices. b=0 means no matching.
    # So decomposition: C is a 4-cycle on 4 vertices, M empty, T spans.
    # T has 5 edges, C has 4 edges, total 9 = |E(K_{3,3})|. ✓
    # Pick C = 4-cycle 0-3-1-4-0. C = {0-3, 3-1, 1-4, 4-0}.
    # T = remaining 5 edges = {0-5, 1-5, 2-3, 2-4, 2-5}.
    #   Is T a spanning tree? Check connectedness on {0,...,5}:
    #     0-5, 1-5, 2-5: star at 5 covering {0,1,2,5}.
    #     2-3 connects 3 to 2.
    #     2-4 connects 4 to 2.
    #   So {0,1,2,3,4,5} all connected through 5 then 2.
    #   |T| = 5 = n-1. Acyclic by edge count + connectedness.
    # Great. M = {}.
    G = nx.complete_bipartite_graph(3, 3)
    # Vertices: {0,1,2} on one side, {3,4,5} on other.
    C_edges = [(0, 3), (1, 3), (1, 4), (0, 4)]
    T_edges = [(0, 5), (1, 5), (2, 3), (2, 4), (2, 5)]
    labels = {edge_key(*e): "C" for e in C_edges}
    labels.update({edge_key(*e): "T" for e in T_edges})
    ok, reason = verify_decomposition(G, labels)
    assert ok, reason


# ---- subcubic trace-set tests -----------------------------------------------


def make_path_with_two_ports(length: int) -> tuple[nx.Graph, list]:
    """Path graph P_{length+1}: vertices 0..length, edges i-(i+1).

    Endpoints 0 and `length` have degree 1, hence port-degree 2 each -- so
    this is a 2-port-degree-2 example, not what we want.
    """
    raise NotImplementedError("path endpoints are port-degree 2")


def make_one_port_subcubic_K4_minus_edge() -> tuple[nx.Graph, int]:
    """K_4 minus one edge: vertices {0,1,2,3}, edges all pairs except 0-1.
    Degrees: 0->2, 1->2, 2->3, 3->3. Two ports of port-degree 1: 0 and 1.
    """
    G = nx.Graph()
    G.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    return G, [0, 1]


def test_K4_minus_edge_has_two_ports():
    G, ports = make_one_port_subcubic_K4_minus_edge()
    assert sorted(d for _, d in G.degree()) == [2, 2, 3, 3]
    assert ports == [0, 1]


def test_K4_minus_edge_trace_set_nonempty():
    G, ports = make_one_port_subcubic_K4_minus_edge()
    traces = compute_trace_set(G, ports)
    # The trace set must be non-empty: some valid partition exists.
    assert len(traces) > 0


def make_single_port_subcubic_paw() -> tuple[nx.Graph, int]:
    """Paw graph: a triangle {1,2,3} plus a pendant edge 0-1.
    Degrees: 0->1, 1->3, 2->2, 3->2.
    The single port-degree-1 vertex is 2 (or 3). Vertex 0 is port-degree 2
    (deg=1). So this isn't a 1-port graph in our sense (we need exactly
    one port-degree-1 port and no other ports).

    Skip this -- build a different example.
    """
    raise NotImplementedError


def make_K4_with_one_subdivided_edge() -> tuple[nx.Graph, int]:
    """K_4 with edge 0-1 subdivided by a new vertex 4.

    Vertices: {0,1,2,3,4}. Edges: {0-2, 0-3, 0-4, 1-2, 1-3, 1-4, 2-3}.
    Degrees: 0->3, 1->3, 2->3, 3->3, 4->2. So vertex 4 is the unique
    port (port-degree 1).
    """
    G = nx.Graph()
    G.add_edges_from([(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3)])
    return G, 4


def test_K4_subdivided_one_port():
    G, port = make_K4_with_one_subdivided_edge()
    assert G.degree(port) == 2
    others = [d for v, d in G.degree() if v != port]
    assert all(d == 3 for d in others)


def test_K4_subdivided_bridge_side_realisable():
    """K_4 with one subdivided edge: this is a 1-port subcubic graph.
    If we glue it back through the port (with another such graph or a
    gadget), we should be able to find a 3-decomposition. So at least one
    of the bridge-admissible states {T_T, T_TM} should be realisable.
    """
    G, port = make_K4_with_one_subdivided_edge()
    assert verify_bridge_side_realisable(G, port)


# ---- vertex-type identity sanity ------------------------------------------


def test_vertex_type_identity_on_K4_decomposition():
    """In the K_4 decomposition above (T = star at 0, C = triangle 123):
    V_T = {0} (degT=3), V_C = {1,2,3} (degC=2), V_M = {}.
    Check a = c + 2: a=3, c=1, 1+2=3. ✓"""
    a, b, c = 3, 0, 1
    assert a == c + 2
    assert a + b + c == 4
    assert a + 2 * b + 3 * c == 2 * (4 - 1)


def test_vertex_type_identity_on_K33_decomposition():
    """In the K_{3,3} decomposition above (C = 4-cycle on {0,1,3,4}):
    V_C = {0,1,3,4}, V_T = {2,5} (degT = 3 each), V_M = {}.
    a=4, b=0, c=2. a = c+2 = 4. ✓"""
    a, b, c = 4, 0, 2
    assert a == c + 2
    assert a + b + c == 6
    assert a + 2 * b + 3 * c == 2 * (6 - 1)


# ---- 2-pole trace set computer ----------------------------------------------


def make_2pole_two_triangles_joined_at_edge() -> tuple[nx.Graph, list]:
    """Two triangles sharing an edge: K_4 minus one perfect matching.

    Vertices {0,1,2,3} with edges 0-1, 1-2, 2-3, 3-0, 0-2 (=K_4 minus 1-3).
    Degrees: 0->3, 1->2, 2->3, 3->2. Ports: {1, 3}, each port-degree 1.
    Five edges, four vertices.
    """
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    return G, [1, 3]


def test_2pole_K4_minus_edge_traces_nonempty():
    G, ports = make_2pole_two_triangles_joined_at_edge()
    traces = compute_trace_set_2pole(G, ports)
    assert len(traces) > 0


def test_2pole_pi_consistency():
    """Every (chi, pi) in the trace set must satisfy:
       - pi block elements are subsets of {0, 1}
       - port i appears in some pi block iff state_combo[i] is T-incident
         (in {T_T, T_TM, T_CC})
    """
    from decomposition import BOUNDARY_COLOUR  # local import for clarity
    G, ports = make_2pole_two_triangles_joined_at_edge()
    traces = compute_trace_set_2pole(G, ports)
    for chi, pi in traces:
        union = set()
        for block in pi:
            assert block <= {0, 1}
            union |= set(block)
        for i, state in enumerate(chi):
            t_incident = BOUNDARY_COLOUR[state] == "T"
            assert (i in union) == t_incident, (
                f"port {i} state={state} t_incident={t_incident} but "
                f"i in union = {i in union}; chi={chi} pi={pi}"
            )


def test_2pole_pi_signatures_in_allowed_set():
    """Every pi signature must be one of the five allowed forms."""
    G, ports = make_2pole_two_triangles_joined_at_edge()
    traces = compute_trace_set_2pole(G, ports)
    allowed = {
        frozenset(),
        frozenset({frozenset({0})}),
        frozenset({frozenset({1})}),
        frozenset({frozenset({0, 1})}),
        frozenset({frozenset({0}), frozenset({1})}),
    }
    for _, pi in traces:
        assert pi in allowed, f"unexpected pi={pi}"


def test_2pole_chi_all_TT_pi_consistency():
    """For the K_4-minus-edge 2-pole side, with both ports in state T_T:
    inside H both side edges at each port are T. Some valid partitions
    should exist (it's a small graph); pi must be one of the two T-incident
    options {same} or {diff}.
    """
    G, ports = make_2pole_two_triangles_joined_at_edge()
    traces = compute_trace_set_2pole(G, ports)
    tt_traces = [(chi, pi) for chi, pi in traces if chi == ("T_T", "T_T")]
    for _, pi in tt_traces:
        # Both ports T-incident; pi has exactly one block containing both,
        # or two singleton blocks. Either is acceptable a priori.
        union = set()
        for block in pi:
            union |= set(block)
        assert union == {0, 1}


def make_2pole_path_then_join() -> tuple[nx.Graph, list]:
    """Build a 2-pole subcubic graph by 'plumbing' a small piece.

    Take the prism (triangular prism, K_3 x K_2) and subdivide two
    non-adjacent edges; the subdivision vertices become port-degree-1.

    Prism: vertices {0..5}, edges
      (0,1), (1,2), (2,0), (3,4), (4,5), (5,3), (0,3), (1,4), (2,5).
    Subdivide (0,1) by 6 and (3,4) by 7:
      remove (0,1), add (0,6),(6,1); remove (3,4), add (3,7),(7,4).
    Now 8 vertices: 0..5 each degree 3, 6 and 7 each degree 2.
    """
    G = nx.Graph()
    G.add_edges_from([
        (1, 2), (2, 0), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5),
        (0, 6), (6, 1), (3, 7), (7, 4),
    ])
    return G, [6, 7]


def test_2pole_subdivided_prism_traces_nonempty():
    G, ports = make_2pole_path_then_join()
    # This graph has 11 edges; brute force is 3^11 = 177k partitions.
    traces = compute_trace_set_2pole(G, ports)
    assert len(traces) > 0


def test_2pole_subdivided_prism_pi_consistency():
    G, ports = make_2pole_path_then_join()
    from decomposition import BOUNDARY_COLOUR
    traces = compute_trace_set_2pole(G, ports)
    for chi, pi in traces:
        union = set()
        for block in pi:
            union |= set(block)
        for i, state in enumerate(chi):
            t_incident = BOUNDARY_COLOUR[state] == "T"
            assert (i in union) == t_incident


# ---- gadget lattice -----------------------------------------------------------


def test_gadget_lattice_small_payload():
    payload = build_payload(n_max=4, orientations="both")
    assert payload["meta"]["gadget_count"] == 2
    assert payload["meta"]["counts_by_order"] == {"4": 2}
    assert len(payload["classes"]) >= 1
    assert all("_trace_key" not in g for g in payload["gadgets"])
    assert all("trace_class" in g for g in payload["gadgets"])


def test_gadget_lattice_cover_edges_are_class_ids():
    payload = build_payload(n_max=6, orientations="both")
    class_ids = {c["id"] for c in payload["classes"]}
    for edge in payload["cover_edges"]:
        assert edge["subset"] in class_ids
        assert edge["superset"] in class_ids


# ---- coverage check against the lattice ------------------------------------


def _small_lattice_payload():
    """A small in-memory lattice for unit tests (n_max=6, both orientations)."""
    return build_payload(n_max=6, orientations="both")


def test_coverage_K4_minus_edge_is_self_covered():
    """The K_4-minus-edge gadget is in the n=4 lattice; checking it against
    the lattice should produce zero uncovered traces and a covering class."""
    from coverage_check import check_coverage
    G, ports = make_2pole_two_triangles_joined_at_edge()
    payload = _small_lattice_payload()
    result = check_coverage(G, ports, payload)
    assert result["uncovered_traces"] == []
    assert len(result["covering_class_ids"]) >= 1
    assert result["smallest_covering_class"] is not None


def test_coverage_pi_block_int_round_trip():
    """JSON traces use list-of-lists for pi; loading must round-trip."""
    from coverage_check import trace_key_from_json
    t_json = {"chi": ["T_T", "T_TM"], "pi": [[0, 1]]}
    key = trace_key_from_json(t_json)
    assert key == (("T_T", "T_TM"), ((0, 1),))


def test_coverage_universe_contains_all_class_traces():
    from coverage_check import union_of_all_traces, trace_set_from_class
    payload = _small_lattice_payload()
    universe = union_of_all_traces(payload)
    for cls in payload["classes"]:
        for t in trace_set_from_class(cls):
            assert t in universe


def test_coverage_smallest_covering_is_minimum_order():
    """Among all covering classes, the smallest_covering_class entry must
    have minimal min_order (or tie-break by trace_count)."""
    from coverage_check import check_coverage
    G, ports = make_2pole_two_triangles_joined_at_edge()
    payload = _small_lattice_payload()
    result = check_coverage(G, ports, payload)
    if result["smallest_covering_class"]:
        smallest = result["smallest_covering_class"]
        for cid in result["covering_class_ids"]:
            cls = next(c for c in payload["classes"] if c["id"] == cid)
            assert (cls["min_order"], cls["trace_count"]) >= (
                smallest["min_order"], smallest["trace_count"]
            )


def test_replacement_K4_minus_edge_not_strictly_replaceable():
    from coverage_check import find_replacement_gadget
    G, ports = make_2pole_two_triangles_joined_at_edge()
    payload = build_payload(n_max=8, orientations="both")
    result = find_replacement_gadget(G, ports, payload)
    assert not result["replaceable"]
    assert result["side_size"] == 4


def test_replacement_subdivided_prism_is_replaceable():
    from coverage_check import find_replacement_gadget
    G, ports = make_2pole_path_then_join()
    payload = build_payload(n_max=8, orientations="both")
    result = find_replacement_gadget(G, ports, payload)
    assert result["replaceable"]
    assert result["smallest_candidate"]["min_order"] < G.number_of_nodes()


def test_classIII_residual_is_compatible_with_every_universe_trace():
    """The n=12 residual side is not trace-contained by a smaller gadget,
    but it is compatibility-universal: every possible opposite-side trace
    can be glued to at least one of its realised traces.
    """
    universe = {
        (("M_TT", "T_T"), frozenset({frozenset({1})})),
        (("M_TT", "T_TM"), frozenset({frozenset({1})})),
        (("T_CC", "T_T"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_CC", "T_TM"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_T", "M_TT"), frozenset({frozenset({0})})),
        (("T_T", "T_CC"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_T", "T_T"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_T", "T_T"), frozenset({frozenset({0, 1})})),
        (("T_T", "T_TM"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_T", "T_TM"), frozenset({frozenset({0, 1})})),
        (("T_TM", "M_TT"), frozenset({frozenset({0})})),
        (("T_TM", "T_CC"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_TM", "T_T"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_TM", "T_T"), frozenset({frozenset({0, 1})})),
        (("T_TM", "T_TM"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_TM", "T_TM"), frozenset({frozenset({0, 1})})),
    }
    residual = {
        (("M_TT", "T_T"), frozenset({frozenset({1})})),
        (("M_TT", "T_TM"), frozenset({frozenset({1})})),
        (("T_CC", "T_T"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_T", "M_TT"), frozenset({frozenset({0})})),
        (("T_T", "T_CC"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_T", "T_T"), frozenset({frozenset({0, 1})})),
        (("T_T", "T_TM"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_T", "T_TM"), frozenset({frozenset({0, 1})})),
        (("T_TM", "M_TT"), frozenset({frozenset({0})})),
        (("T_TM", "T_T"), frozenset({frozenset({0}), frozenset({1})})),
        (("T_TM", "T_T"), frozenset({frozenset({0, 1})})),
        (("T_TM", "T_TM"), frozenset({frozenset({0}), frozenset({1})})),
    }
    assert len(universe) == 16
    assert len(residual) == 12
    assert all(
        any(are_2pole_traces_compatible(h_trace, b_trace) for h_trace in residual)
        for b_trace in universe
    )


def test_compatibility_universality_payload_counts():
    from compatibility_universality import build_payload

    root = HERE.parent
    payload = build_payload(
        root / "data" / "gadget_lattice_2pole_n10_both.json",
        root / "data" / "replacement_sweep_n12.json",
    )
    assert payload["compatibility_universal_class_count"] == 43
    assert payload["axis_characterisation_agreement_count"] == 59
    assert payload["trace_count_threshold"]["min_universal_trace_count"] == 4
    assert payload["trace_count_threshold"]["max_non_universal_trace_count"] == 10
    assert payload["trace_count_threshold"]["all_classes_with_trace_count_at_least_11_are_universal"]
    assert payload["atomic_universal_classes"] == [
        {"id": "C4", "min_order": 10, "trace_count": 4, "member_count": 2}
    ]
    assert payload["smallest_universal_class"]["id"] == "C5"
    assert payload["smallest_universal_class"]["min_order"] == 6
    assert payload["smallest_universal_class"]["trace_count"] == 5
    assert all(row["compatibility_universal"] for row in payload["n12_failures_universality"])
    assert all(row["all_axes_present"] for row in payload["n12_failures_universality"])
    assert len(payload["n12_atomic_universal_failures"]) == 1
    assert payload["n12_atomic_universal_failures"][0]["trace_count"] == 4


def test_reverse_trace_set_matches_reversed_port_order():
    from full_replacement_sweep import reverse_trace_set

    G, ports = make_2pole_path_then_join()
    forward = compute_trace_set_2pole(G, ports)
    direct_reverse = compute_trace_set_2pole(G, list(reversed(ports)))
    assert reverse_trace_set(forward) == direct_reverse


def test_realises_target_traces_self_check_K4_minus_edge():
    """K_4 minus edge IS the C0 gadget with 3 traces. It should
    realise C0's trace set (itself)."""
    from decomposition import realises_target_traces
    from full_replacement_sweep import C0_TRACES

    G, ports = make_2pole_two_triangles_joined_at_edge()
    assert realises_target_traces(G, ports, set(C0_TRACES))


def test_realises_target_traces_empty_targets_trivially_true():
    """Empty target set is trivially realised."""
    from decomposition import realises_target_traces

    G, ports = make_2pole_two_triangles_joined_at_edge()
    assert realises_target_traces(G, ports, set())


def test_realises_target_traces_full_match_subdivided_prism():
    """Subdivided prism realises all 3 of C0's traces (it has 11 traces total)."""
    from decomposition import realises_target_traces
    from full_replacement_sweep import C0_TRACES

    G, ports = make_2pole_path_then_join()
    # First confirm Trace(prism) contains C0's traces using full check:
    full = compute_trace_set_2pole(G, ports)
    assert set(C0_TRACES) <= full
    # Then early-termination check should also return True:
    assert realises_target_traces(G, ports, set(C0_TRACES))
