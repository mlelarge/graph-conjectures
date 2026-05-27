"""Clause wire gadget: empirical test of whether flexible interval edges
attached to a forced-path skeleton can encode a clause constraint.

Construction recipe (per the task brief, candidate 3 / NAE-3-SAT)
----------------------------------------------------------------
Given a forced path  v_0 - v_1 - ... - v_k  in H_back(T), attach three
"literal" flexible vertices  L_1, L_2, L_3  with score windows
overlapping the path's interior at three distinct positions.  The
relative position of L_j to a designated reference encodes literal_j's
truth value; the clause is satisfied iff the LFO is feasible.

Empirical claim under test
--------------------------
In any feasible LFO of T, every interior path vertex v_i (1 <= i <= k-1)
has back-degree exactly 2 (both back-arcs go to its forced-path
neighbours).  Hence **no L_j can contribute a back-arc to any interior
v_i**.  L_j's back-arcs must all land outside the interior of the
path: only the path endpoints v_0, v_k are accessible.

We test this claim by:
  1. Building a forced-path tournament of length k = 1 (n = 8).
  2. Attempting to attach a 3-vertex "clause" L_1, L_2, L_3 wired so
     that their score windows overlap the path interior.
  3. Brute-force enumerating LFOs to see whether the clause's truth-
     table at L_1, L_2, L_3 ever realises the NAE-3SAT allowed set.

For k = 1, there is no interior vertex; the obstruction does not
manifest.  We therefore must use k >= 2 (n >= 15) for the test, which
puts brute-force enumeration out of reach.

A *partial* test at k = 2 places only a single literal vertex L_1 and
checks whether its bit can take both values across LFOs.  This is the
"one-literal sanity check".  Empirically, even one extra vertex with
back-arcs to the interior of the path *kills all LFOs*: the saturated
interior degrees mean any new back-arc lands an interior vertex above
budget.

This file pins that obstruction.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forced_path_tournament import forced_relations  # noqa: E402
from lfo_score_window import find_lfo_order_score_window, indegrees, score_windows  # noqa: E402
from variable_wire_gadget import build_forced_path_tournament  # noqa: E402
from verify import verify  # noqa: E402

Matrix = list[list[int]]


def attach_single_literal_to_interior(
    T: Matrix,
    path: list[int],
    target_index: int,
) -> tuple[Matrix, int]:
    """Return a new tournament with one extra vertex L wired so that L
    has a forced backedge to the interior path vertex path[target_index].

    Strategy: pick L's in-degree so its score window overlaps a forced
    backedge to v = path[target_index].  Concretely, place L just after
    v (so that L -> v becomes a back-arc when v < L in any LFO).

    NEW VERTEX in-degree = d^-(v) + a few, with specific arc orientations
    so that L receives forced incoming from low-index vertices and
    points to high-index vertices.
    """
    n = len(T)
    ds = indegrees(T)
    v = path[target_index]
    # Place L "just after" v in the canonical order: L's window should
    # overlap the position 7*target_index + offset.  Choose L's
    # in-degree to be d^-(v) + 3 (still within score-window range of v).
    target_indeg = ds[v] + 3
    # Build the augmented tournament:
    n_new = n + 1
    T_new = [row[:] + [0] for row in T] + [[0] * n_new]
    L = n  # new vertex label
    # Strategy: L receives incoming arcs from vertices whose d^- < target_indeg
    # and outgoing arcs to the rest.  We pick the `target_indeg` lowest-degree
    # vertices to point AT L, and the rest receive arcs from L.
    sorted_vs = sorted(range(n), key=lambda x: ds[x])
    incoming = set(sorted_vs[:target_indeg])
    for u in range(n):
        if u in incoming:
            T_new[u][L] = 1
        else:
            T_new[L][u] = 1
    return T_new, L


def decide_lfo_existence(T: Matrix) -> bool:
    """Decide whether T has an LFO, via the score-window solver."""
    result = find_lfo_order_score_window(T)
    return result["found"]


def evaluate_literal_attachment(k: int, target_index: int) -> dict:
    """Build forced-path of length k, attach a single literal L_1 wired
    to the interior path vertex at position target_index, then check
    whether the augmented tournament still has any LFO.
    """
    T, path = build_forced_path_tournament(k)
    T_new, L = attach_single_literal_to_interior(T, path, target_index)
    base_has_lfo = decide_lfo_existence(T)
    aug_has_lfo = decide_lfo_existence(T_new)
    n = len(T_new)
    ds_new = indegrees(T_new)
    # Count back-arcs touching each interior path vertex in the score-window
    # solver's certificate.
    sol = find_lfo_order_score_window(T_new)
    interior = path[1:-1] if len(path) >= 3 else []
    return {
        "k": k,
        "target_index": target_index,
        "n_base": len(T),
        "n_aug": n,
        "base_has_lfo": base_has_lfo,
        "aug_has_lfo": aug_has_lfo,
        "L_indegree": ds_new[L],
        "interior_path_vertices": interior,
        "aug_lfo_order": sol.get("order"),
    }


def attempt_clause_attachment(k: int) -> dict:
    """Try attaching three literal vertices to three interior positions of a
    forced path; report whether any LFO exists.
    """
    T, path = build_forced_path_tournament(k)
    if len(path) < 4:
        return {
            "k": k,
            "skipped": True,
            "reason": (
                f"path length {len(path)-1} too short for 3-literal "
                "clause requiring 3 interior attachments (need k >= 4)."
            ),
        }
    # Attach to three different interior positions.
    interior_indices = [1, len(path) // 2, len(path) - 2]
    Ts = T
    L_labels = []
    for idx in interior_indices:
        Ts, L = attach_single_literal_to_interior(Ts, path, idx)
        L_labels.append(L)
    base_has_lfo = decide_lfo_existence(T)
    aug_has_lfo = decide_lfo_existence(Ts)
    return {
        "k": k,
        "interior_indices": interior_indices,
        "L_labels": L_labels,
        "n_base": len(T),
        "n_aug": len(Ts),
        "base_has_lfo": base_has_lfo,
        "aug_has_lfo": aug_has_lfo,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["single_literal", "three_literals"],
        default="single_literal",
    )
    parser.add_argument("--k", type=int, default=2)
    args = parser.parse_args()

    if args.mode == "single_literal":
        results = []
        for target in range(1, args.k):  # interior indices 1..k-1
            r = evaluate_literal_attachment(args.k, target)
            results.append(r)
        print(json.dumps({"mode": "single_literal", "k": args.k, "results": results}, indent=2))
    else:
        r = attempt_clause_attachment(args.k)
        print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
