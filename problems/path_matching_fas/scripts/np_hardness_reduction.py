"""Candidate NP-hardness reduction from NAE-3SAT to Path-FAS.

Reduction-theorist side of the joint Aboulker Problem 4.4 attack.  This
script proposes variable / wire / clause gadgets and a composition
recipe; the matching verifier is
`scripts/np_hardness_gadget_verifier.py`, which exhaustively checks
truth tables (§ D32).

The target chosen here is **NAE-3SAT** (Not-All-Equal 3-SAT), the
alternative listed in the task brief.  The choice is forced by the
empirical data:

  * The Section 16 toggle is a valid variable gadget: balanced port-bit
    distribution (both bits realized), but asymmetric (9 vs 4 LFOs per
    bit, § D32.3.1).
  * The cyclic triangle realizes **exactly** the NAE-3SAT allowed
    truth table (all 6 non-constant 3-bit patterns, § D32.3.2), and
    fails 1-in-3-SAT (leaks three spurious 2-True patterns).
  * No proposed clause gadget passes 1-in-3-SAT in isolation; this is
    a hard combinatorial obstruction since 1-in-3 requires the clause
    to *forbid* (T,T,F), (T,F,T), (F,T,T), (T,T,T), (F,F,F) — five
    forbidden patterns out of eight, with three of them being non-
    constant.  The path-FAS local LFO structure does not naturally
    suppress 2-True patterns without also killing the 1-True patterns.

Hence this script targets **NAE-3SAT**.  The empirical 1-in-3-SAT
negative finding is documented as Section D31 §3.

Reduction architecture
======================

The reduction maps a NAE-3SAT instance Phi = clauses on n variables to
a tournament T_Phi as follows:

  * **Variable gadget** (Section 16 toggle, k=1).  Each variable v
    gets 4 vertices a_v, b_v, f_v, g_v.  The port pair (a_v, b_v)
    encodes the truth value: bit 1 (=True) iff b_v is placed before
    a_v in any LFO.

  * **Wire (fanout) gadget** — UNRESOLVED.  Each variable may appear
    in multiple clauses.  The candidate fanout is the aligned
    fork-tree (Section 20.2), which transmits the toggle state to k
    downstream "copy" ports without forcing agreement.  Forcing
    agreement (i.e., making the k copies *equal* in every LFO) is
    the open design problem; see § D31 §2.

  * **Clause gadget** — the cyclic triangle on three "literal" ports.
    Each clause C = (l_1, l_2, l_3) gets a fresh 3-vertex triangle
    whose ports plug into the literals' downstream copies.  Per the
    gadget-miner verifier (§ D32.3.2), the triangle's local truth
    table is *exactly* the NAE-3SAT allowed set.

The composition is fragile, because:

  (a) The fanout problem is unsolved, so copy-to-clause linking is
      currently done by **direct identification** (each literal port
      *is* the variable's b_v vertex).  This makes the clause-side
      tournament depend on the variable layout, and the composition
      audit (§ D31 §5) is the dominant open task.

  (b) Linking arcs between gadgets can produce *unintended* LFOs that
      don't correspond to any coherent variable assignment.  Soundness
      hinges on ruling these out, which requires either a proof or an
      exhaustive composition audit.

  (c) The cyclic-triangle clause's "validity in isolation" assumes
      *only* the three port pairs are present.  Once composed into a
      larger tournament with many other vertices, the local LFO count
      can change (cross-arcs interact with the triangle's loop).

Status
======

Per the brief's deliverable schedule:

  * T1 (variable gadget design): completed — Section 16 toggle
    re-verified, asymmetry pinned.
  * T2 (fanout gadget): **unresolved**.  The closest candidate
    (aligned fork-tree) does *not* force agreement.
  * T3 (clause gadget): cyclic triangle works in *isolation* for
    NAE-3SAT.  Composition unproven.
  * T4 (global composition): only a skeleton exists; no full T_Phi
    is constructible until T2 is solved.
  * T5 (iff proof): not started.  Without T2 the forward direction
    is incomplete and soundness is out of reach.

This document **does not claim NP-hardness**.  It states the
construction we *can* build, the obstruction at T2, and a precise
list of what remains.

Usage
=====

  uv run python scripts/np_hardness_reduction.py

This runs a battery of small self-tests against the verifier:

  * Section 16 toggle truth table (re-derived from miner's verifier).
  * Cyclic triangle NAE-3SAT match (re-derived).
  * Fanout candidate: aligned fork-tree at k=3 — toggle bits at
    different ports do **not** agree, hence not a valid fanout.
  * Composition skeleton: emits the JSON layout for a tiny NAE-3SAT
    instance and the expected vertex counts.
"""

from __future__ import annotations

import json
import os
import sys
from itertools import product
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verify import verify  # noqa: E402
from np_hardness_gadget_verifier import (  # noqa: E402
    ALLOWED_NAE3,
    enumerate_extendable_orderings,
    full_truth_table,
    placement_bit_first_pair_inversion,
    section16_toggle_ports,
    section16_toggle_tournament,
    verify_clause_gadget,
    verify_variable_gadget,
)


Matrix = list[list[int]]


# ----------------------------------------------------------------------
# Variable gadget (T1): re-export Section 16 toggle


def variable_gadget(num_vars: int = 1) -> tuple[Matrix, list[tuple[int, int]]]:
    """Return (tournament, list_of_port_pairs) for a Section 16 toggle bank.

    `num_vars` toggles laid out in sequence per Section 16.  Each toggle
    contributes 4 vertices; total = 4 * num_vars.  The port pair for
    variable i is (a_i, b_i) = (2i, 2i+1).
    """
    T = section16_toggle_tournament(num_vars)
    ports = section16_toggle_ports(num_vars)
    return T, ports


# ----------------------------------------------------------------------
# Clause gadget (T3): the cyclic triangle


def cyclic_triangle() -> tuple[Matrix, list[tuple[int, int]]]:
    """Return (tournament, port_pairs) for the cyclic triangle clause.

    Vertices 0, 1, 2; arcs 0 -> 1, 1 -> 2, 2 -> 0.  Port pairs:
    (0, 1), (1, 2), (2, 0).  This is the cleanest cyclic triangle.

    By § D32.3.2, the local NAE-3SAT truth table at these three ports
    is exactly the 6 non-constant patterns, each realized by exactly
    one LFO.  No LFO realizes (F, F, F) or (T, T, T).
    """
    T = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 0],
    ]
    ports = [(0, 1), (1, 2), (2, 0)]
    return T, ports


def verify_clause_in_isolation_nae3() -> dict:
    """Self-test: cyclic triangle is a valid NAE-3SAT clause in isolation."""
    T, ports = cyclic_triangle()
    return verify_clause_gadget(T, ports, mode="nae3")


def verify_clause_in_isolation_1in3() -> dict:
    """Self-test: cyclic triangle is NOT a valid 1-in-3 clause in isolation.

    Returns the verifier dict; the caller should expect `ok == False`
    with three spurious patterns.
    """
    T, ports = cyclic_triangle()
    return verify_clause_gadget(T, ports, mode="1in3")


# ----------------------------------------------------------------------
# Fanout candidate (T2): aligned fork-tree (does NOT force agreement)


def fanout_candidate_aligned_fork_tree(k: int) -> tuple[Matrix, list[tuple[int, int]]]:
    """Return (tournament, list_of_port_pairs) for the aligned fork-tree.

    This is a fork-tree with pairing pi = (0, 1, 2, ..., k-1) (identity).
    Per Section 20.2 every toggle prefix is extendable, so this *gadget*
    does not impose any constraint on the toggle bits.  In particular,
    it does **not** force the k toggle bits to agree, so it is NOT a
    fanout in the reduction sense.  We expose it here only to document
    the negative finding empirically.

    Vertex layout (cf. `fork_tree_tournament` docstring):
        a_i = 2i, b_i = 2i+1     for 0 <= i < k
        p   = 2k
        r   = 2k+1
        A_i = 2k+2+i
        B_i = 3k+2+i
    """
    from fork_tree_probe import fork_tree_tournament

    T = fork_tree_tournament(k, tuple(range(k)))
    ports = [(2 * i, 2 * i + 1) for i in range(k)]
    # Coerce to int-matrix shape expected by verifier.
    T_int = [[1 if T[i][j] else 0 for j in range(len(T))] for i in range(len(T))]
    return T_int, ports


def fanout_agreement_evidence(k: int = 3) -> dict:
    """Check whether the aligned-fork-tree fanout forces agreement among bits.

    Returns a dict with:
      `all_lfos_agree`: True iff every LFO has all k port bits equal.
      `truth_table`: histogram of k-bit outcomes across all LFOs.
      `verdict`: "forces_agreement" | "does_not_force_agreement".

    The expected outcome (Section 20.2) is **does_not_force_agreement**:
    all 2^k bit patterns are realized by some LFO.  This is the
    negative result documented in Section D31 §2.

    NOTE: at k >= 3 the fork-tree has n = 4k+2 >= 14 vertices, and
    enumerating all 14! orderings is infeasible.  We pass
    `allow_large=True` and rely on the fork-tree's structure to
    short-circuit — but practically this routine is only intended for
    *very small* k.  At k=2 it's already ~10! = 3.6M orderings.
    """
    if k > 2:
        # Without a smarter sub-tournament enumeration this becomes
        # intractable.  Bail with a descriptive error.
        return {
            "verdict": "untested_too_large",
            "k": k,
            "reason": (
                f"k={k} requires {4*k+2}! orderings; "
                "use the gadget-miner verifier with allow_large=True "
                "or restrict to k=1,2."
            ),
        }
    T, ports = fanout_candidate_aligned_fork_tree(k)
    tt = full_truth_table(
        T, ports,
        lambda P: placement_bit_first_pair_inversion(P, ports),
        width=k,
        allow_large=True,
    )
    nonzero = {bits for bits, c in tt.items() if c > 0}
    all_agree = all(len(set(bits)) <= 1 for bits in nonzero)
    return {
        "k": k,
        "truth_table": {str(bits): c for bits, c in tt.items()},
        "patterns_realized": [list(bits) for bits in sorted(nonzero)],
        "all_lfos_agree": all_agree,
        "verdict": (
            "forces_agreement" if all_agree else "does_not_force_agreement"
        ),
    }


# ----------------------------------------------------------------------
# Composition skeleton (T4)


def build_nae3sat_skeleton(
    num_vars: int,
    clauses: Sequence[tuple[tuple[int, bool], tuple[int, bool], tuple[int, bool]]],
) -> dict:
    """Emit the layout for a NAE-3SAT -> Path-FAS reduction.

    `clauses` is a list of triples, each `(literal_1, literal_2, literal_3)`
    where each literal is `(var_index, polarity)` (polarity True = positive,
    False = negated).

    Returns a dict describing:
      * variable vertex assignments (4 per variable, Section 16 toggle);
      * clause vertex assignments (3 per clause, cyclic triangle);
      * the *intended* linking between toggle ports and clause ports
        (currently a direct identification, since the fanout is
        unresolved — see § D31 §2).

    This routine does **not** produce a complete tournament because
    the fanout is missing.  It produces a *layout*, plus a list of
    unresolved arcs that the (future) fanout gadget would supply.
    """
    layout: dict = {
        "num_variables": num_vars,
        "num_clauses": len(clauses),
        "variable_offsets": [4 * v for v in range(num_vars)],
        "clause_offsets": [],
        "intended_linkage": [],
        "unresolved_arcs": [],
        "status": "skeleton_only",
        "open_problems": [],
    }
    next_v = 4 * num_vars
    for c_idx, clause in enumerate(clauses):
        offset = next_v
        layout["clause_offsets"].append(offset)
        next_v += 3
        for port_idx, (var, polarity) in enumerate(clause):
            # Intended linkage: clause port `port_idx` reads variable
            # `var`'s truth value (or its negation).  Currently
            # unresolved.
            layout["intended_linkage"].append(
                {
                    "clause": c_idx,
                    "port": port_idx,
                    "variable": var,
                    "polarity": polarity,
                    "via": "fanout_NOT_IMPLEMENTED",
                }
            )
    layout["total_vertices_so_far"] = next_v
    layout["open_problems"] = [
        "T2 (fanout): the aligned fork-tree does not force agreement; "
        "no working fanout gadget exists yet (§ D31 §2).",
        "T2 (negation): we lack a 'complement' gadget that reads the "
        "negation of a toggle bit (§ D31 §2.2).",
        "T4 (cross-clause cross-arcs): with the fanout missing, the "
        "tournament's cross-arcs between toggles and clauses are not "
        "specified.",
        "T5 (soundness): unattempted; depends on T2 / T4.",
    ]
    return layout


# ----------------------------------------------------------------------
# Self-tests


def _self_test_variable() -> dict:
    T, ports = variable_gadget(num_vars=1)
    result = verify_variable_gadget(T, ports[0])
    return result


def _self_test_clause_nae3() -> dict:
    return verify_clause_in_isolation_nae3()


def _self_test_clause_1in3() -> dict:
    return verify_clause_in_isolation_1in3()


def _self_test_fanout_k1() -> dict:
    """At k=1, the aligned fork-tree is a 6-vertex fragment with one
    toggle.  Its single-port truth table should be balanced."""
    T, ports = fanout_candidate_aligned_fork_tree(1)
    tt = full_truth_table(
        T, ports,
        lambda P: placement_bit_first_pair_inversion(P, ports),
        width=1,
    )
    return {
        "k": 1,
        "truth_table": {str(bits): c for bits, c in tt.items()},
        "is_balanced": all(c > 0 for c in tt.values()),
    }


def _self_test_fanout_k2() -> dict:
    """At k=2, the aligned fork-tree is a 10-vertex fragment.  Both
    port bits should be free to take any value -> fanout does not
    force agreement."""
    return fanout_agreement_evidence(k=2)


def _self_test_skeleton() -> dict:
    """Emit a skeleton for a tiny NAE-3SAT instance:
       Phi = (x_0 v x_1 v x_2) AND (~x_0 v x_1 v ~x_2)
    """
    clauses = [
        ((0, True), (1, True), (2, True)),
        ((0, False), (1, True), (2, False)),
    ]
    return build_nae3sat_skeleton(num_vars=3, clauses=clauses)


if __name__ == "__main__":
    print("=== T1: variable gadget (Section 16 toggle, k=1) ===")
    r = _self_test_variable()
    print(json.dumps({k: str(v) for k, v in r.items()}, indent=2))

    print()
    print("=== T3: clause gadget (cyclic triangle) in NAE-3SAT mode ===")
    r = _self_test_clause_nae3()
    print(json.dumps({k: str(v) for k, v in r.items()}, indent=2))

    print()
    print("=== T3 (negative): clause gadget in 1-in-3-SAT mode ===")
    r = _self_test_clause_1in3()
    print(json.dumps({k: str(v) for k, v in r.items()}, indent=2))

    print()
    print("=== T2 (fanout at k=1): does single-port toggle survive aligned fork-tree? ===")
    r = _self_test_fanout_k1()
    print(json.dumps(r, indent=2))

    print()
    print("=== T2 (fanout at k=2): does the aligned fork-tree force agreement? ===")
    r = _self_test_fanout_k2()
    print(json.dumps(r, indent=2))

    print()
    print("=== T4: skeleton composition for a tiny NAE-3SAT formula ===")
    r = _self_test_skeleton()
    print(json.dumps(r, indent=2, default=str))
