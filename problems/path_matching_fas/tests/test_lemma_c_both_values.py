"""Regression tests for the corrected (both-values) Lemma C (D78).

Pins:
  * the recount that REFUTES the one-value form ("capacity on a value
    => R_T != EQ"): at n=7, k=2 there are 16 EQ_2 gadgets with capacity
    on 00 and 16 on 11 -- so the one-value form is false;
  * the verified both-values form: 0 EQ_2 gadgets have capacity on both
    00 and 11;
  * the saturation mechanism: every EQ_2 gadget with capacity on 00 but
    not 11 saturates ALL FOUR port endpoints on its 11-LFOs.
"""
from __future__ import annotations

import os
import sys

import pytest


SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPT_DIR))

from single_port_slide import both_values_saturation_profile  # noqa: E402


@pytest.mark.slow
def test_one_value_form_refuted_both_value_form_holds_n7():
    out = both_values_saturation_profile(7)
    assert out["eq2_instances"] == 660
    # one-value form is FALSE: EQ_2 gadgets DO have capacity on a value
    assert out["cap_on_00"] == 16
    assert out["cap_on_11"] == 16
    # both-values form HOLDS: none has capacity on both
    assert out["cap_on_both"] == 0


@pytest.mark.slow
def test_saturation_mechanism_all_four_endpoints_n7():
    """Every EQ_2 cap-on-00-only gadget saturates all four port
    endpoints {a,b,c,d} on its 11-LFOs (the both-values mechanism)."""
    out = both_values_saturation_profile(7)
    profile = out["min_saturated_roles_on_11_for_cap00only"]
    # the only key should be the all-four-endpoints set
    assert set(profile.keys()) == {("a", "b", "c", "d")} or \
        all(set(k) == {"a", "b", "c", "d"} for k in profile)
    assert sum(profile.values()) == 16


def test_n6_both_values_no_capacity_on_both():
    """Fast check at n=6: the single EQ_2 gadget family has 0 gadgets
    with capacity on both equality values."""
    out = both_values_saturation_profile(6)
    assert out["cap_on_both"] == 0


def test_flip_lemma_holds_n4():
    """Flip lemma (step 4 of the Saturation sub-claim proof): every
    config with both port edges isolated K_2 on the (1,1) value has a
    MIXED vector realizable.  Verified at n=4; the adjacent-swap
    sub-case proves 30/48, the other 18 are non-adjacent (the residual
    gap), yet still mixed-realizable."""
    from single_port_slide import flip_lemma_census
    out = flip_lemma_census(4)
    assert out["both_isolated_configs"] == 48
    assert out["flip_lemma_holds"] is True       # all mixed-realizable
    assert out["non_adjacent_count"] == 18        # not all reduce to adjacency


@pytest.mark.slow
def test_flip_lemma_holds_n5():
    from single_port_slide import flip_lemma_census
    out = flip_lemma_census(5)
    assert out["both_isolated_configs"] == 3228
    assert out["flip_lemma_holds"] is True
    assert out["non_adjacent_count"] == 1098


def test_single_vertex_relocation_partial_coverage_n4():
    """Non-adjacent residual: a single-vertex relocation reaches a mixed
    vector for all 18 non-adjacent configs at n=4 (but does NOT suffice
    at n=5, where 60 need multi-vertex moves -- pinned slow)."""
    from single_port_slide import single_vertex_relocation_coverage
    out = single_vertex_relocation_coverage(4)
    assert out["non_adjacent_configs"] == 18
    assert out["single_vertex_reaches_mixed"] == 18
    assert out["needs_multivertex"] == 0


@pytest.mark.slow
def test_single_vertex_relocation_incomplete_n5():
    """Single-vertex relocation covers 1038/1098 non-adjacent configs at
    n=5 -- 60 require a multi-vertex reorder, so no bounded-local-move
    proof of the non-adjacent Flip Lemma."""
    from single_port_slide import single_vertex_relocation_coverage
    out = single_vertex_relocation_coverage(5)
    assert out["non_adjacent_configs"] == 1098
    assert out["single_vertex_reaches_mixed"] == 1038
    assert out["needs_multivertex"] == 60


def test_three_cycle_characterization_n4():
    """3-Cycle Characterization (back-arc framing, PROVED, all n):
    when port {a,b}'s arc is an isolated degree-1 back-arc, every vertex
    between a and b forms a directed 3-cycle with {a,b}.  Verified at
    n=4 with 0 violations; the flip lemma also holds in this framing."""
    from single_port_slide import three_cycle_characterization_check
    out = three_cycle_characterization_check(4)
    assert out["three_cycle_holds"] is True
    assert out["three_cycle_violations"] == 0
    assert out["flip_lemma_holds"] is True


@pytest.mark.slow
def test_three_cycle_characterization_n5():
    from single_port_slide import three_cycle_characterization_check
    out = three_cycle_characterization_check(5)
    assert out["three_cycle_holds"] is True
    assert out["between_vertex_instances"] == 3600
    assert out["flip_lemma_holds"] is True


def test_c_equals_between_and_necessity_n4():
    """C(P) = between-vertices (proved) and |C(P)|<=4 necessary for
    flipping (proved); both verified at n=4."""
    from single_port_slide import c_set_analysis
    out = c_set_analysis(4)
    assert out["C_equals_between_holds"] is True
    assert out["necessary_holds"] is True


@pytest.mark.slow
def test_c_equals_between_holds_but_sufficiency_fails_n6():
    """At n=6: C(P)=between still exact and |C|<=4 still necessary, BUT
    |C|<=4 is NOT sufficient for flippability (3600 ports have |C|<=4
    yet are not flippable) -- the clean |C|-characterization fails."""
    from single_port_slide import c_set_analysis
    out = c_set_analysis(6)
    assert out["C_equals_between_holds"] is True
    assert out["necessary_holds"] is True
    assert out["sufficiency_holds"] is False
    suff_ok, suff_total = out["sufficiency_rate"]
    assert suff_total - suff_ok == 3600


def test_two_port_coupled_flip_n5():
    """Two-port coupled flip theorem (D80), n=5.  Over configs that
    realize BOTH isolated-11 (both ports degree-1 K_2) and 00, at least
    one port is always flippable: at n=5 every config is (True,True)."""
    from single_port_slide import two_port_coupled_flip
    out = two_port_coupled_flip(5)
    assert out["isolated_11_and_00_configs"] == 1800
    assert out["both_nonflippable"] == 0
    assert out["coupled_flip_theorem_holds"] is True
    assert out["flip_distribution"] == {"(True, True)": 1800}


@pytest.mark.slow
def test_two_port_coupled_flip_obstruction_is_cycle_n6():
    """Two-port coupled flip theorem (D80), n=6.  (False,False) never
    occurs (3600 nonflippable ports split 1800/1800 over the two mixed
    targets), and EVERY nonflippable port is blocked by a CYCLE -- zero
    degree blockers.  So the obstruction is internal cycle structure
    coupling the two ports, not back-degree saturation."""
    from single_port_slide import two_port_coupled_flip
    out = two_port_coupled_flip(6)
    assert out["isolated_11_and_00_configs"] == 53280
    assert out["both_nonflippable"] == 0
    assert out["coupled_flip_theorem_holds"] is True
    assert out["flip_distribution"] == {
        "(True, True)": 49680,
        "(False, True)": 1800,
        "(True, False)": 1800,
    }
    # the decisive refinement: all blockers are cycles, none are degree
    assert out["nonflippable_obstruction_types"] == {"cycle": 3600}


def test_no_eq2_iso11_backarc_n6():
    """D80 in the unambiguous BACK-ARC framing, n=6: no iso-11 gadget has
    R_arc subset of {00,11}, i.e. iso-11 => a mixed value is realizable
    (the both-values Lemma C form).  Also: no EQ_2 gadget has an iso-11
    LFO.  Confirms the no-00-hypothesis strengthening over iso-reps."""
    from single_port_slide import iso11_eq2_backarc_count
    out = iso11_eq2_backarc_count(6)
    assert out["eq2_with_iso11"] == 0
    assert out["iso11_with_no_mixed"] == 0
    assert out["D80_holds_iso11_implies_mixed"] is True


@pytest.mark.slow
def test_no_eq2_iso11_backarc_n7():
    """DECISIVE n=7 check (back-arc framing, over tournament iso-reps):
    223 EQ_2 gadgets, ZERO with an iso-11 LFO (588 iso-11 gadgets total),
    and ZERO iso-11 gadgets with no mixed value.  So D80 (iso-11 =>
    mixed) holds at n=7 -- NOT a small-n artifact.  The D78 bit-framing
    '16 cap_on_11' is an orientation relabeling, not a back-arc-framing
    iso-11; capacity never sits on the both-back-arc value."""
    from single_port_slide import iso11_eq2_backarc_count
    out = iso11_eq2_backarc_count(7)
    assert out["eq2_gadgets"] == 223
    assert out["eq2_with_iso11"] == 0
    assert out["iso11_gadgets_total"] == 588
    assert out["iso11_with_no_mixed"] == 0
    assert out["D80_holds_iso11_implies_mixed"] is True


@pytest.mark.slow
def test_obstruction_structure_n6():
    """D80 obstruction structure at n=6: interval geometry is always
    NESTED, and the shortest blocking cycle is a triangle (1440) or a
    6-cycle (2160) -- the latter threading both full port arcs (the
    alternating ladder)."""
    from single_port_slide import coupling_structure
    out = coupling_structure(6)
    assert out["interval_geometry"] == {"nested": 3600}
    assert out["cycle_length_distribution"] == {3: 1440, 6: 2160}
    assert out["essentiality_of_00"]["of_those_both_nonflippable"] == 0


@pytest.mark.slow
def test_blocks_always_coupled_n6():
    """D80 coupling at n=6: every nonflippable port (3600) is COUPLED --
    it becomes flippable once the partner port's back-arc constraint is
    dropped.  Zero intrinsic blocks, so the obstruction genuinely couples
    the two ports."""
    from single_port_slide import intrinsic_vs_coupled
    out = intrinsic_vs_coupled(6)
    assert out["nonflippable_ports_classification"] == {"coupled": 3600}
    assert out["all_coupled"] is True


def test_kernel_foundation_lemmas_n5():
    """D81 kernelization foundation at n=5 (all checks 0 violations):
    Fact 1 (deletion preserves iso-11), Fact 2 (deletion only relaxes
    R_arc -- anti-monotone), and the Clean-Cut Insertability Lemma.  At
    n=5 no vertex is essential (the mixed witness already lives in the
    4-vertex port core)."""
    from single_port_slide import kernel_lemmas_check
    out = kernel_lemmas_check(5)
    assert out["fact1_iso11_preserved_violations"] == 0
    assert out["fact2_deletion_relaxes_violations"] == 0
    assert out["cleancut_insertability_violations"] == 0
    assert out["essential_implies_onstructure"] is True


@pytest.mark.slow
def test_kernel_foundation_lemmas_n6():
    """D81 kernelization at n=6: the three lemmas hold (0 violations),
    and the key localization -- every essential vertex (7200 of them,
    deletion adds a mixed value) lies between some port's endpoints
    (essential => on-structure, 7200/7200)."""
    from single_port_slide import kernel_lemmas_check
    out = kernel_lemmas_check(6)
    assert out["iso11_configs"] == 54000
    assert out["fact1_iso11_preserved_violations"] == 0
    assert out["fact2_deletion_relaxes_violations"] == 0
    assert out["cleancut_insertability_violations"] == 0
    assert out["essential_vertices_total"] == 7200
    assert out["essential_offstructure"] == 0
    assert out["essential_implies_onstructure"] is True


def test_essential_locality_no_essential_n5():
    """D82 red-team, n=5 sanity: no non-port vertex is essential, so all
    three locality candidates hold vacuously."""
    from single_port_slide import essential_locality_refutation
    out = essential_locality_refutation(5)
    assert out["essential_total"] == 0
    assert out["C1_refuted"] is False
    assert out["C2_refuted"] is False
    assert out["C3_refuted"] is False


@pytest.mark.slow
def test_essential_locality_all_three_candidates_refuted_n6():
    """D82: at n=6 the three natural LOCAL criteria for deletability are
    all refuted -- deletability of a vertex is NOT a local property, so
    the Insertability/kernel bound cannot rest on sigma-load, single-C
    membership, or a degree floor.  (Essentiality as in
    kernel_lemmas_check: deletion changes R_arc cap {01,10}.)"""
    from single_port_slide import essential_locality_refutation
    out = essential_locality_refutation(6)
    assert out["essential_total"] == 7200
    # (C1) sigma-isolated vertices CAN be essential
    assert out["C1_sigma_isolated_essential"] == 1440
    assert out["C1_refuted"] is True
    # (C2) single-C ("outer rung") vertices CAN be essential
    assert out["C2_single_C_essential"] == 5760
    assert out["C2_refuted"] is True
    # (C3) degree-1 vertices CAN be essential (profiles (1,4) and (4,1))
    assert out["C3_lowdegree_essential"] == 1440
    assert out["C3_refuted"] is True
    assert out["C3_violator_degree_profiles"] == {"(1, 4)": 720,
                                                  "(4, 1)": 720}
    # raw structure
    assert out["essential_sigma_backdeg_dist"] == {0: 1440, 1: 5760}
    assert out["essential_role_dist"] == {"cP": 2880, "cQ": 2880,
                                          "cPcQ": 1440}


def test_rung_compression_n5_sanity():
    """D83 sanity, n=5: iso-11 configs have a single isolated rung,
    removing it always preserves the mixed set, no twins, no rigid cores
    -- the compression question is vacuous below n=6."""
    from single_port_slide import rung_compression_refutation
    out = rung_compression_refutation(5)
    assert out["compression_lemma_refuted"] is False
    iso = out["remove_isolated_rung"]
    assert iso["applicable"] == iso["mixed_preserved"] == 14
    assert out["rigid_configs_by_rungs"] == {}


@pytest.mark.slow
def test_rung_compression_lemma_refuted_n7():
    """D83: the Rung-Compression Lemma is REFUTED at n=7 (over iso-reps).
    No same-type contraction preserves the realized mixed set, and rigid
    all-essential cores exist up to the largest observable size (3 rungs):

      * removing the MIDDLE of a 3-rung back-arc path preserves the mixed
        set only 26/49 (9/13 even when all three rungs share a role);
      * removing a LEAF preserves only 77/98;
      * 40 of 184 TWIN pairs (identical port-arcs) are BOTH essential --
        the pair jointly blocks a value neither blocks alone (long-range
        memory);
      * RIGID (all-essential, no safe single deletion) configs exist with
        1, 2 and 3 rungs (11 / 44 / 15), and are 100% of single-mixed
        configs at 1-2 rungs -- single deletion cannot shorten such cores.
    """
    from single_port_slide import rung_compression_refutation
    out = rung_compression_refutation(7)
    assert out["compression_lemma_refuted"] is True
    assert out["twin_pairs_total"] == 184
    assert out["twin_pairs_both_essential"] == 40
    assert out["remove_middle_3path"] == {"applicable": 49,
                                          "mixed_preserved": 26}
    assert out["remove_middle_3path_samerole"] == {"applicable": 13,
                                                   "mixed_preserved": 9}
    assert out["remove_leaf_3path"] == {"applicable": 98,
                                        "mixed_preserved": 77}
    # rigid cores at every observable rung count (int keys)
    assert out["rigid_configs_by_rungs"] == {1: 11, 2: 44, 3: 15}
    # all single-mixed 1- and 2-rung configs are rigid
    assert out["rigid_single_mixed_by_rungs"][1] == \
        out["total_single_mixed_by_rungs"][1] == 11
    assert out["rigid_single_mixed_by_rungs"][2] == \
        out["total_single_mixed_by_rungs"][2] == 44


def test_d80_refuted_at_n8():
    """D84 (MAJOR CORRECTION): D80 ("iso-11 => a mixed value") is FALSE at
    n=8.  Two explicit 8-vertex witnesses, re-verified by a self-contained
    brute-force LFO scan: each is a valid tournament with an iso-11 LFO
    (both port arcs back-arcs, all four endpoints back-degree 1) yet
    realizes NO mixed value.  The first has R_arc={(1,1)}; the second is a
    full EQ_2 gadget R_arc={(0,0),(1,1)} that is iso-11 -- refuting both
    "no iso-11 gadget has R_arc subset {00,11}" and "eq2_with_iso11=0".
    This overturns the n<=7 "verified => conjectured all n" extrapolation
    and explains why the D81/D82/D83 kernel routes (which tried to PROVE
    D80 for all n) were all blocked."""
    from single_port_slide import verify_d80_counterexamples
    out = verify_d80_counterexamples()
    assert out["D80_refuted_at_n8"] is True
    w0, w1 = out["witnesses"]
    assert w0["is_d80_counterexample"] is True
    assert w0["R_arc"] == [(1, 1)] and w0["n_lfos"] == 13
    assert w1["is_d80_counterexample"] is True
    assert w1["R_arc"] == [(0, 0), (1, 1)] and w1["n_lfos"] == 17
    assert all(w["has_iso11"] and w["no_mixed"] and w["valid_tournament"]
               for w in out["witnesses"])


def test_eq2_capacity_census_n6_n7():
    """D85: capacity-form Fanout-Barrier census (back-arc framing).  At
    n=6,7 there is NO faithful EQ_2 splitter (cap_on_both=0).  The n=7 row
    reproduces D78 §1's '16 cap-on-00' (and shows the '16 cap-on-11' was
    the orientation artifact -- =0 in back-arc framing); the EQ_2 count
    223 matches the canonical iso11_eq2_backarc_count(7)."""
    from single_port_slide import eq2_capacity_census
    o6 = eq2_capacity_census(6)
    assert (o6["eq2_gadgets"], o6["cap_on_00"], o6["cap_on_11"],
            o6["cap_on_both"]) == (2, 1, 0, 0)
    o7 = eq2_capacity_census(7)
    assert (o7["eq2_gadgets"], o7["cap_on_00"], o7["cap_on_11"],
            o7["cap_on_both"]) == (223, 16, 0, 0)
    assert o7["fanout_barrier_refuted"] is False


@pytest.mark.slow
def test_eq2_capacity_census_n8_barrier_survives():
    """D85 (decisive): the full n=8 capacity-form census.  Over all 6880
    iso-classes there are 5430 EQ_2 gadgets, 189 with capacity on 00, and
    -- for the FIRST time -- 6 with capacity on 11 (the D84 iso-11 EQ_2
    gadgets), but ZERO with capacity on BOTH.  So:
      * the Fanout Barrier (no faithful EQ_2 splitter) SURVIVES at n=8;
      * the old 'the 11 value always saturates' mechanism (D78 §1) is
        DEAD (cap_on_11 jumped 0 -> 6); the barrier now holds because
        capacity on 00 and on 11 never co-occur, not because 11 has none.
    """
    from single_port_slide import eq2_capacity_census
    out = eq2_capacity_census(8)
    assert out["eq2_gadgets"] == 5430
    assert out["cap_on_00"] == 189
    assert out["cap_on_11"] == 6      # FIRST nonzero -> old mechanism dead
    assert out["cap_on_both"] == 0    # barrier survives
    assert out["faithful_splitter_exists"] is False
    assert out["fanout_barrier_refuted"] is False


@pytest.mark.slow
def test_eq2_capacity_profile_no_local_separator_n8():
    """D86: mine WHY cap-00 and cap-11 never co-occur (D85).  The 6 cap-11
    EQ_2 gadgets share a uniform PORT-LOCAL signature (port-score-order
    uP<vP<uQ<vQ, quad-type (1,1,2,2), vP->uQ, min-saturated-on-00 =
    {uQ,vP}).  But that signature does NOT separate: 170 cap-00 gadgets
    share the cap-11 quad-type and 2 share its full port-score-order.  So
    no port-local invariant distinguishes the classes -- the capacity
    separator is GLOBAL (as with the non-locality of D82/D83)."""
    from single_port_slide import eq2_capacity_profile
    out = eq2_capacity_profile(8)
    assert out["classes"] == {"no_capacity": 5235, "cap00_only": 189,
                              "cap11_only": 6}
    assert out["cap11_quad_type"] == {"(1, 1, 2, 2)": 6}
    assert out["cap11_vP_uQ_arc"] == {"vP->uQ": 6}
    assert out["cap11_minsat_on_00"] == {"('uQ', 'vP')": 6}
    # the decisive negative: cap00 gadgets share the cap11 port-signature
    assert out["cap00_sharing_cap11_quadtype"] == 170
    assert out["cap00_sharing_cap11_scoreorder"] == 2
    assert out["port_local_separator_exists"] is False


@pytest.mark.slow
def test_cap00_3cycle_bound_lever_n7_n8():
    """D87 global-proof lever: cap-00 ⟹ |C(P)| ≤ 2 and |C(Q)| ≤ 2 (C =
    3-cycle partners of the port arc).  Verified n=7,8 with 0 violations.
    Also pins the obstruction to finishing with this bound alone: every
    iso-11 EQ_2 gadget at n=8 is CROSSING (so the clean nested-case
    Adjacent-Flip finish is vacuous), and there is a crossing iso-11 EQ_2
    gadget (no mixed) with |C(P)| = |C(Q)| = 2 -- so |C|≤2 is NECESSARY but
    NOT SUFFICIENT to force a mixed value."""
    from single_port_slide import cap00_3cycle_bound
    o7 = cap00_3cycle_bound(7)
    assert o7["lever_holds"] is True
    assert o7["iso11_eq2_geometry"] == {}      # no iso-11 EQ_2 at n=7
    o8 = cap00_3cycle_bound(8)
    assert o8["lever_holds"] is True
    assert o8["iso11_eq2_geometry"] == {"crossing": 6}   # all crossing
    # |C| up to 3 for iso-11 EQ_2 (so cap-00's |C|<=2 genuinely cuts)
    assert o8["iso11_eq2_C_size_dist"] == {"(3, 2)": 2, "(3, 3)": 1,
                                           "(2, 3)": 2, "(2, 2)": 1}
    # |C|<=2 insufficiency: a crossing iso-11 EQ_2 gadget with |C|=(2,2)
    w = o8["Cle2_insufficiency_witness"]
    assert w is not None and tuple(w["C_sizes"]) == (2, 2) \
        and w["geometry"] == "crossing"


@pytest.mark.slow
def test_outdeg_separator_n8():
    """D88 (expert-team result, independently re-verified): the out-degree
    separator.  On the port-local-signature-matched EQ_2 family at n=8:
      * every iso-11 EQ_2 gadget (6/6) is signature-matched and has sign
        pattern (out(uP)<out(vP), out(uQ)<out(vQ)) = (<,<);
      * every signature-matched cap-00 gadget (170/170) has NO '<' on
        either port (156 strict (>,>) + 14 with one tie -- NOT all strict,
        the synthesis's '(>,>) 170/170' was an overclaim);
      * mutually exclusive => cap_both = 0; the residual is the SINGLE
        crossing |C|=(2,2) gadget P=(1,3),Q=(4,6).
    The Crossing Splice Lemma is refuted as a local reorder (not encoded
    here); this separator is the redirection target -- verified n<=8, not
    proved."""
    from single_port_slide import eq2_outdeg_separator
    out = eq2_outdeg_separator(8)
    assert out["iso11_eq2_total"] == 6
    assert out["iso11_all_signature_matched"] is True
    assert out["iso11_sign_patterns"] == {"('<', '<')": 6}
    assert out["cap00_matched_no_less"] is True
    assert out["cap00_matched_strict_gg"] == 156      # NOT 170: ties exist
    assert out["cap00_matched_sign_patterns"] == {"('>', '>')": 156,
                                                  "('>', '=')": 7,
                                                  "('=', '>')": 7}
    assert out["cap_both"] == 0
    crux = out["crux_iso11_C22_gadgets"]
    assert len(crux) == 1
    assert tuple(crux[0][0]) == (1, 3) and tuple(crux[0][1]) == (4, 6)
    assert out["separator_holds"] is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
