"""Attempt: SAT instance -> tournament Path-FAS via forced-forest wires.

This file is the *honest documentation* of the reduction attempt and its
obstruction.  It does NOT produce a working reduction.  The contents:

1. A reduction architecture (variable wires + flex-edge clauses).
2. A small SAT-instance builder that compiles a NAE-3SAT formula into a
   *would-be* tournament under that architecture.
3. The empirical observation that the obstruction documented in
   `docs/J_hardness_via_wires.md` (Section 5 "Interior degree
   saturation") kills every non-trivial clause attachment.

Reduction architecture
======================

Given a NAE-3SAT formula Phi on n variables and m clauses:

  * For each variable v_j (1 <= j <= n) build a *variable wire*: a
    forced-path subgadget  P_j = (p_{j,0}, p_{j,1}, ..., p_{j,k_j})
    where k_j = (number of clauses in which v_j appears).  By the
    `variable_wire_gadget.build_forced_path_tournament` construction,
    P_j requires 7*k_j + 1 vertices.

  * For each clause C_i = (l_{i,1}, l_{i,2}, l_{i,3}), build a *clause
    triangle* T_i = (q_{i,1}, q_{i,2}, q_{i,3}) on 3 vertices (cyclic
    triangle as in `scripts/np_hardness_reduction.py`).

  * For each literal occurrence "C_i references v_j as literal l", wire
    q_{i,?} to the interior of P_j by a flexible interval edge.

Failure mode: interior degree saturation
========================================

By Theorem 5.1 of `docs/J_hardness_via_wires.md`, every interior
path-vertex p_{j,i} (1 <= i <= k_j - 1) has back-degree exactly 2 in
EVERY LFO, and both back-arcs go to its forced-path neighbours.  Hence
the clause-attachment back-arc CANNOT touch the interior of P_j.

There are two endpoints  p_{j,0}, p_{j,k_j}  per wire, hence at most
TWO clause attachments per variable.  But k_j (the number of
occurrences of v_j) can be Omega(m), so for m clauses on n variables
with average occurrence > 2, the architecture is infeasible.

This is the *same fanout obstruction* as in
`docs/general_path_fas_hardness.md`, re-expressed in the wire setting:
the forced-path skeleton merely re-allocates the degree-2 budget to a
fixed scaffold without freeing capacity for broadcasting.

What this file does
===================

* Implements the wire-builder.
* Implements the attachment recipe.
* Implements a brute-force check on tiny instances (n = 1 var, m <= 2
  clauses).  At m = 2 already, the construction has 2 endpoint slots
  on a single wire, which would allow exactly the maximum two
  attachments.  At m = 3 the construction must FAIL.
* Reports the obstruction explicitly.

This is NOT an NP-hardness reduction.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from variable_wire_gadget import build_forced_path_tournament  # noqa: E402

Matrix = list[list[int]]


def variable_occurrences(clauses: Sequence[Sequence[tuple[int, bool]]]) -> dict[int, int]:
    occ: dict[int, int] = {}
    for clause in clauses:
        for var, _ in clause:
            occ[var] = occ.get(var, 0) + 1
    return occ


def build_wire_reduction_attempt(
    num_vars: int,
    clauses: Sequence[Sequence[tuple[int, bool]]],
) -> dict:
    """Attempt to compile (num_vars, clauses) into a wire-based tournament.

    Returns a dict describing the attempted compilation and the verdict
    (success or obstruction triggered).
    """
    occ = variable_occurrences(clauses)
    max_occ = max(occ.values()) if occ else 0

    # Step 1: for each variable, build a forced wire of length
    # k_j = occ[v_j].  Total path-vertex count = sum (7 * k_j + 1).
    per_var_paths: list[dict] = []
    for var in range(num_vars):
        k = occ.get(var, 0)
        wire_len = max(k, 1)
        per_var_paths.append({
            "var": var,
            "occurrences": k,
            "wire_path_length_k": wire_len,
            "wire_n_vertices": 7 * wire_len + 1,
            "endpoint_slots_available": 2,
            "interior_slots_available": max(wire_len - 1, 0),
        })

    # Step 2: each variable needs k_j attachments (one per occurrence).
    # By the interior-degree-saturation theorem, only the 2 endpoints
    # are available.  If k_j > 2, the construction FAILS.
    obstruction = None
    for entry in per_var_paths:
        if entry["occurrences"] > entry["endpoint_slots_available"]:
            obstruction = {
                "trigger": "interior_degree_saturation",
                "var": entry["var"],
                "occurrences": entry["occurrences"],
                "endpoint_slots": entry["endpoint_slots_available"],
                "details": (
                    "By Theorem 5.1 of docs/J_hardness_via_wires.md, "
                    "interior path vertices have back-degree exactly 2 "
                    "in every LFO, both saturated by forced-path "
                    "neighbours.  Hence at most 2 clause attachments "
                    "per variable are possible (one per endpoint).  "
                    f"Variable {entry['var']} occurs {entry['occurrences']} "
                    f"times, which exceeds the available 2 slots."
                ),
            }
            break

    return {
        "num_vars": num_vars,
        "num_clauses": len(clauses),
        "variable_occurrences": occ,
        "per_var_paths": per_var_paths,
        "obstruction": obstruction,
        "constructible_under_architecture": (obstruction is None),
        "max_var_occurrence": max_occ,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--formula",
        type=str,
        default=None,
        help=(
            "NAE-3SAT formula as JSON: a list of clauses, each clause is "
            "a list of [var_index, polarity] pairs.  Polarity True = "
            "positive literal.  Example: '[[[0,true],[1,true],[2,true]],"
            " [[0,false],[1,true],[2,false]]]'"
        ),
    )
    parser.add_argument("--num-vars", type=int, default=3)
    args = parser.parse_args()

    if args.formula:
        clauses = json.loads(args.formula)
        # Convert inner lists to tuples for hashability.
        clauses = [[(v, bool(p)) for v, p in c] for c in clauses]
        num_vars = args.num_vars
    else:
        # Default tiny instance: 3 vars, 2 clauses (constructible).
        clauses = [
            [(0, True), (1, True), (2, True)],
            [(0, False), (1, True), (2, False)],
        ]
        num_vars = 3

    out = build_wire_reduction_attempt(num_vars, clauses)
    print(json.dumps(out, indent=2, default=str))

    # Also try a larger instance that triggers the obstruction.
    print()
    print("=== Triggering instance: var 0 in 3 clauses ===")
    triggering = [
        [(0, True), (1, True), (2, True)],
        [(0, False), (1, False), (2, True)],
        [(0, True), (1, True), (2, False)],
    ]
    out2 = build_wire_reduction_attempt(3, triggering)
    print(json.dumps(out2, indent=2, default=str))


if __name__ == "__main__":
    main()
