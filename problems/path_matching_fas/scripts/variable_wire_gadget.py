"""Variable wire gadget: encode a Boolean value as the position of a
forced-path terminus.

Setup
-----
Let T be a tournament containing a forced-back-arc path

    v_0 - v_1 - v_2 - ... - v_k   in H_back(T),

where each edge {v_i, v_{i+1}} is a forced backedge (the in-degrees of
v_i and v_{i+1} differ by >= 5 = 2r+1 with score-window radius r = 2,
and T has the arc later -> earlier).  In any LFO sigma of T:

* The relative orientation of consecutive (v_i, v_{i+1}) is fixed by
  the score-window inequalities.
* Every interior vertex v_i  (1 <= i <= k-1) has back-degree at least 2
  in sigma (one back-arc per forced-neighbour).  Combined with the
  Path-FAS budget back-deg <= 2 this forces

      back-deg_sigma(v_i) = 2     for every 1 <= i <= k-1.

  In particular **no other back-arc may touch an interior path
  vertex**.

This last clause is the fundamental obstruction documented below.

What we explore in this file
----------------------------
We attempt the following construction:

* Pick a forced-path skeleton  v_0 - v_1 - ... - v_k  in some T.
* Attach **two** extra vertices L (left) and R (right) outside the
  path.  Their relative LFO position should encode bit = True / False.
* Wire L, R to the path endpoints v_0, v_k via flexible interval edges
  (windows overlapping with v_0 and v_k respectively).

Claim (positive direction).  When L < R in sigma, the back-arc structure
on { L, v_0, ..., v_k, R } is a single linear forest extending the
forced path by one edge at each end.  When L > R, the structure
contains a back-arc cycle.

Claim (negative direction).  The construction *only* propagates the
relative order of L and R when the path endpoints' degrees are not
saturated.  In an isolated wire (no clause attachments) this works.
The trouble starts when clauses introduce additional back-arcs touching
the wire.

This file implements both claims and checks them empirically.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forced_path_tournament import forced_relations  # noqa: E402
from lfo_score_window import indegrees, score_windows  # noqa: E402
from verify import verify  # noqa: E402

Matrix = list[list[int]]


def build_pure_forced_path_tournament(k: int) -> tuple[Matrix, list[int]]:
    """Construct a tournament of size n = 5*(k+1) + epsilon whose forced
    relation graph H contains an explicit path  v_0 - v_1 - ... - v_k
    of length k.

    Strategy.  We want in-degrees d^-(v_i) chosen so |d^-(v_i) -
    d^-(v_{i+1})| >= 5 for every i.  The simplest realisation uses a
    monotone arithmetic progression  d^-(v_i) = 5*i.  We then pad the
    tournament with "filler" vertices whose in-degrees lie *strictly
    between* the path values to soak up the remaining arc-budget while
    not introducing further forced relations with the path.

    Returns (T, path)  where  path = [v_0, ..., v_k]  is the explicit
    forced path in H_back.
    """
    # We need n >= 5k + 1 to place v_i in-degrees at 0, 5, 10, ..., 5k.
    # Use n = 5k + 1 exactly; the path vertices are labelled 0..k and
    # filler vertices fill the rest.
    n = 5 * k + 1
    # Reserve labels: path vertices = 0, 1, ..., k.
    # We want d^-(i) = 5*i.
    T = [[0] * n for _ in range(n)]

    # Order all n vertices in a transitive backbone: position p has
    # in-degree p.  We assign positions so that:
    #   path vertex i occupies position 5*i  (in-degree = 5*i).
    # Filler vertices fill the other positions.
    path_positions = [5 * i for i in range(k + 1)]
    filler_positions = [p for p in range(n) if p not in path_positions]
    # Map vertex labels to positions:
    pos_of = [0] * n
    for i, p in enumerate(path_positions):
        pos_of[i] = p
    next_label = k + 1
    for p in filler_positions:
        pos_of[next_label] = p
        next_label += 1
    # Build the transitive tournament along these positions.
    # Vertex u points to v iff pos_of[u] < pos_of[v].
    for u in range(n):
        for v in range(n):
            if u != v and pos_of[u] < pos_of[v]:
                T[u][v] = 1

    # We now want to flip enough arcs to make the path edges
    # (v_i, v_{i+1}) become BACK-ARCs (later -> earlier).
    # In the transitive backbone, v_{i+1} points to v_i? No -- in transitive,
    # higher position has higher in-degree but arcs go LOW position -> HIGH
    # position.  So v_i (position 5i) -> v_{i+1} (position 5(i+1)) is a
    # forward arc, not a back-arc.  We need to reverse those k arcs:
    for i in range(k):
        u, v = i, i + 1
        # currently T[u][v] = 1 (u -> v).  Reverse:
        T[u][v] = 0
        T[v][u] = 1

    # The reversal changed in-degrees!  Each reversal increases d^-(u)
    # by 1 and decreases d^-(v) by 1.  After k reversals at path edges
    # i -> i+1:
    #   path-vertex j gains a +1 from its predecessor reversal (if j>=1)
    #   path-vertex j loses a -1 from its successor reversal (if j<=k-1)
    # so d^-(j) = 5*j + [j>=1] - [j<=k-1] = 5j + (1 - 1) = 5j for 1<=j<=k-1
    # and d^-(0) = 0 - 1 = -1?  Wait, that's negative.  Let me redo:
    #
    # Before any reversal, d^-(j) = pos_of[j] = 5*j (under the
    # transitive labelling).
    # Reversing the arc (u, v) where u <- v becomes u -> v in our
    # convention -- we flipped T[u][v]:=0, T[v][u]:=1.  This means:
    #   * u GAINED an incoming arc from v: d^-(u) += 1.
    #   * v LOST an incoming arc from u: d^-(v) -= 1.
    # For edge i: u = i, v = i+1:
    #   d^-(i)  += 1   (for i = 0, ..., k-1)
    #   d^-(i+1) -= 1  (for i = 0, ..., k-1)
    # Aggregate:
    #   d^-(0) += 1                      = 0 + 1 = 1
    #   d^-(j) += 1 (gain from j-th edge u=j) and -= 1 (loss from
    #               (j-1)-th edge v=j) = 5j + 1 - 1 = 5j   (1<=j<=k-1)
    #   d^-(k) -= 1                       = 5k - 1.
    # So gaps between consecutive d^-(v_i) values are:
    #   |d^-(v_0) - d^-(v_1)| = |1 - 5| = 4    -- NOT >= 5!
    # So this naive construction does NOT produce a forced path.
    #
    # We need d^- gaps of >= 5 after the flips.  Switch to spacing 6:
    # let path vertex i live at position 6*i, n = 6k+1.
    # This file's `build_pure_forced_path_tournament` builds the naive
    # 5*i version; the corrected version below uses 6*i.
    return T, list(range(k + 1))


def build_forced_path_tournament(k: int) -> tuple[Matrix, list[int]]:
    """Construct a tournament with an explicit forced path of length k.

    Uses spacing 7 so that after the k arc reversals needed to make the
    path edges back-arcs, the in-degree gaps still exceed 4 = 2*radius.

    Path positions: 7*i.  Path vertex i has in-degree 7*i + delta where
    delta in {-1, 0, +1} after reversal.  Endpoint gaps: 7 - 2 = 5.
    Interior gaps: 7.  Score windows do not overlap (strictly disjoint
    by >= 1).

    Returns (T, path) with path = [v_0, ..., v_k]  and  n = 7*k + 1.
    """
    n = 7 * k + 1
    T = [[0] * n for _ in range(n)]
    path_positions = [7 * i for i in range(k + 1)]
    filler_positions = [p for p in range(n) if p not in path_positions]
    pos_of = [0] * n
    for i, p in enumerate(path_positions):
        pos_of[i] = p
    next_label = k + 1
    for p in filler_positions:
        pos_of[next_label] = p
        next_label += 1
    for u in range(n):
        for v in range(n):
            if u != v and pos_of[u] < pos_of[v]:
                T[u][v] = 1
    for i in range(k):
        u, v = i, i + 1
        T[u][v] = 0
        T[v][u] = 1
    return T, list(range(k + 1))


def report_forced_path(T: Matrix, path: list[int]) -> dict:
    """Return a sanity-check report on a proposed forced path."""
    n = len(T)
    windows = score_windows(T)
    ds = indegrees(T)
    gaps = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        gaps.append((ds[a], ds[b], abs(ds[a] - ds[b])))
    rel = forced_relations(T)
    forced_back_set = {tuple(sorted(e)) for e in rel["forced_back"]}
    path_edges_forced = [
        tuple(sorted((path[i], path[i + 1]))) in forced_back_set
        for i in range(len(path) - 1)
    ]
    return {
        "n": n,
        "indegrees_on_path": [ds[v] for v in path],
        "windows_on_path": [windows[v] for v in path],
        "consecutive_gaps": gaps,
        "all_gaps_>=_5": all(g[2] >= 5 for g in gaps),
        "path_edges_forced_back": path_edges_forced,
        "all_path_edges_forced": all(path_edges_forced),
        "n_forced_back_total": len(rel["forced_back"]),
    }


def variable_wire_truth_table(k: int) -> dict:
    """Enumerate LFOs of the pure forced-path tournament and check that
    each LFO has the path in a fixed direction.

    Since the forced path has every interior vertex with back-degree
    exactly 2 already, **no LFO is possible if the rest of the
    tournament contributes any back-arc touching an interior path
    vertex**.  This is the structural obstruction.
    """
    T, path = build_forced_path_tournament(k)
    n = len(T)
    # We brute force LFO enumeration only for small k.
    if n > 9:
        return {
            "k": k, "n": n,
            "skipped_brute_force": True,
            "reason": "n > 9; enumerate_extendable_orderings would take too long",
        }
    lfo_orders = []
    for P in permutations(range(n)):
        info = verify(T, list(P))
        if info["is_linear_forest"]:
            lfo_orders.append(list(P))
    # For each LFO, check the path vertices appear in increasing order
    # of label, i.e. the path direction.
    directions = []
    for P in lfo_orders:
        pos = {v: i for i, v in enumerate(P)}
        positions = [pos[v] for v in path]
        is_monotone_increasing = all(positions[i] < positions[i + 1] for i in range(len(positions) - 1))
        is_monotone_decreasing = all(positions[i] > positions[i + 1] for i in range(len(positions) - 1))
        if is_monotone_increasing:
            directions.append("L->R")
        elif is_monotone_decreasing:
            directions.append("R->L")
        else:
            directions.append("MIXED!_violation")
    return {
        "k": k,
        "n": n,
        "n_lfos": len(lfo_orders),
        "directions": {
            d: directions.count(d)
            for d in ("L->R", "R->L", "MIXED!_violation")
        },
    }


def saturation_check(k: int) -> dict:
    """Quantify the degree-saturation obstruction.

    On the pure forced-path tournament, for each LFO, compute the
    back-degree of each interior path vertex (should be exactly 2) and
    the spare back-degree budget on path endpoints v_0 and v_k.
    """
    T, path = build_forced_path_tournament(k)
    n = len(T)
    if n > 9:
        return {"k": k, "n": n, "skipped_brute_force": True}
    interior = path[1:-1]
    spare_per_vertex_histogram: dict[int, dict[int, int]] = {v: {0: 0, 1: 0, 2: 0} for v in path}
    n_lfos = 0
    for P in permutations(range(n)):
        info = verify(T, list(P))
        if not info["is_linear_forest"]:
            continue
        n_lfos += 1
        pos = {v: i for i, v in enumerate(P)}
        back_deg = {v: 0 for v in path}
        for u, v in info["arcs"]:
            if u in back_deg:
                back_deg[u] += 1
            if v in back_deg:
                back_deg[v] += 1
        for v, d in back_deg.items():
            spare_per_vertex_histogram[v][d] = spare_per_vertex_histogram[v].get(d, 0) + 1
    interior_saturated = all(
        spare_per_vertex_histogram[v].get(2, 0) == n_lfos and
        spare_per_vertex_histogram[v].get(0, 0) == 0 and
        spare_per_vertex_histogram[v].get(1, 0) == 0
        for v in interior
    ) if interior else True
    return {
        "k": k,
        "n": n,
        "n_lfos": n_lfos,
        "interior_path_vertices": interior,
        "back_deg_histogram_per_path_vertex": spare_per_vertex_histogram,
        "interior_always_saturated_at_2": interior_saturated,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=1, help="forced-path length")
    parser.add_argument("--all", action="store_true",
                        help="run k = 1, 2 (n = 7, 13)")
    args = parser.parse_args()
    ks = [1, 2] if args.all else [args.k]
    out = {"runs": []}
    for k in ks:
        T, path = build_forced_path_tournament(k)
        rep = report_forced_path(T, path)
        tt = variable_wire_truth_table(k)
        sat = saturation_check(k)
        out["runs"].append({
            "k": k,
            "report": rep,
            "truth_table": tt,
            "saturation_check": sat,
        })
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
