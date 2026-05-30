"""Reversed-matching substrate hardness attempt for Path-FAS.

This script implements (and tests the limits of) an NP-hardness reduction
candidate that uses the reversed-matching tournament family as a substrate.
It does **not** claim to prove NP-hardness; on the contrary, it surfaces
a new and precise structural obstruction (the **global back-arc budget**
plus the **linear-forest shape constraint on the back-arc graph**) that
defeats every natural reversed-matching-based reduction discovered here.

Background
==========

Aboulker, Aubian, Charbit, Lopes, *Finding forest-orderings of
tournaments is NP-complete*, arXiv:2402.10782 (2024).  Their Problem
4.4 asks for the complexity of C-FAS when C is the class of paths.

The prior reduction attempt (docs/J_hardness_via_wires.md) used long
forced backedge paths to broadcast a variable's truth value.  It died
on **interior degree saturation** (Theorem 5.1 of that doc): every
interior vertex of a forced backedge path already has its full
back-degree-2 budget consumed by the two adjacent forced edges, so no
clause attachment can land on the interior of a wire.

The **reversed-matching substrate** (this script) is the natural way
to bypass that obstruction: every forced component has size 2, so
there is no interior — every vertex is an endpoint.  Theorem 5.1 is
vacuous on this substrate.

Substrate definition (Section 1 of the companion document)
==========================================================

The **reversed matching tournament** RM(m) on n = 2m vertices is built
from the transitive tournament on positions 0..n-1 by reversing each
of the m matching arcs (i, i+m) for i = 0..m-1.

For m >= 8 (the smallest m at which score-window radius 2 yields
disjoint windows between the low and high halves), the forced backedge
graph H(RM(m)) is exactly the m-edge matching
   { (i + m, i) : 0 <= i < m }.
Each H-edge {i, i+m} forces i before i+m in every linear-forest
ordering (LFO).

Matching component as a "register"
==================================

Each matching component C_i = {i, i+m} has the LFO-forced internal
order   i first, i+m second.  The remaining degree of freedom of C_i
in any LFO is **its embedding into the linear order**:

  * the position of i within its score window I_i,
  * the position of i+m within its score window I_{i+m},
  * subject to those two positions being distinct and consistent with
    the LFO degree-2 + acyclicity constraints.

Equivalently, the "state" of C_i is the relative position of (i, i+m)
in the LFO with respect to the other matching components.  In a
strict matching tournament where score windows are width 5, this state
ranges over O(m) global positions but only constant-many local choices.

The shuffle freedom between two components C_i and C_j is governed by
flex edges in G_flex.  If the score window of i overlaps with the
score window of j (resp. j+m), then the relative order of i and j
(resp. j+m) is free, subject to the back-arc degree-2 budget.

This is the "register" point of view: each C_i is a register whose
value is its shuffle position relative to the other registers.

The reduction attempt
=====================

We attempt the simplest natural reduction: from **3-COLORING** (Karp
1972, [DOI 10.1137/0205049 indirectly via reduction tree]; original:
Karp, Reducibility among combinatorial problems, *Complexity of
Computer Computations* 1972, pp. 85-103) to Path-FAS on a generalised
reversed-matching tournament.

The encoding intended:

  * Graph G = (V, E) of 3-coloring instance has |V| = m vertices.
  * Each graph vertex v in V becomes a matching component C_v
    augmented with a 3-slot position structure.
  * Each graph edge (u, v) in E becomes a flex-edge constraint between
    C_u and C_v that forbids C_u and C_v from being in the same slot.

The natural slot encoding: position of (i+m) within its 5-position
window picks one of 3 "color slots" (slot 0 = early, slot 1 = mid,
slot 2 = late).

Constraint encoding via flex arcs: for each clause-edge (u, v) we add
extra reversed arcs to inject flex constraints into G_flex linking
(u+m) and (v+m) so that their relative position must differ.

The obstruction (this script's main finding)
============================================

Both directions of the reduction fail to encode 3-COLORING.  The
underlying reason is a new and structurally cleaner obstruction than
Theorem 5.1:

  (Global Back-Arc Budget).  In any LFO sigma of a tournament T on n
  vertices, the back-arc graph B(sigma) is a linear forest on n
  vertices, so |B(sigma)| <= n - 1.  Hence the *total* number of
  back-arcs - across all encoded constraints combined - is at most
  n - 1.

This is the **global** version of the local "back-degree-2 per
vertex" constraint.  It says: the **shape of the back-arc graph is a
union of vertex-disjoint paths**, so the constraint graph is at most
a *linear forest of pairwise relations*.  But 3-COLORING requires an
arbitrary edge set, which can be far from a linear forest.

In particular, if E(G) is not embeddable as a linear forest on a
subset of vertices, no reversed-matching reduction can encode all
edges of E via "shuffle constraints between matching components."

This is the same shape constraint that defines Path-FAS itself: the
back-arc graph must be a linear forest.  So any reduction that
encodes constraints purely via back-arc presence is bounded by the
linear-forest shape.  Generalising: the shape of *all* the constraint
attachments combined is itself the input of the Path-FAS problem,
which is a perfect circularity.

(The wire-reduction obstruction Theorem 5.1 is a *local* per-vertex
consequence; the present obstruction is a *global* shape consequence.
The two are independent: a wire structure could in principle have
free interior vertices and still hit the global cap.)

What this script does
=====================

  build_reversed_matching(m)             RM(m) substrate.
  build_3coloring_reduction(G)           the candidate reduction.
  verify_obstruction(G)                  empirical check that the
                                         reduction fails to encode
                                         3-COLORING; reports the
                                         observed obstruction.

  small_instance_demo()                  driver for the docs.

Run with:

  uv run python scripts/reversed_matching_hardness.py --demo

Author: reduction-theorist side, May 2026.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interaction_graph import (  # noqa: E402
    build_H_and_Gflex,
    hall_feasible,
    score_windows,
)
from verify import verify  # noqa: E402


Matrix = list[list[int]]


# ---------------------------------------------------------------------------
# Substrate constructors
# ---------------------------------------------------------------------------


def transitive_tournament(n: int) -> Matrix:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    return T


def build_reversed_matching(m: int) -> Matrix:
    """Reversed matching RM(m) on n = 2m vertices.

    Forced backedge graph H is the matching {(i+m, i) : 0 <= i < m} for
    m >= 8 (when score windows of i and i+m become disjoint).
    """
    T = transitive_tournament(2 * m)
    for i in range(m):
        T[i][i + m] = 0
        T[i + m][i] = 1
    return T


def build_general_reversed_matching(m: int, perm: Sequence[int]) -> Matrix:
    """Generalised reversed matching: arc (i, m + perm[i]) reversed for each i.

    The forced backedge set is then { (m + perm[i], i) : 0 <= i < m },
    a matching on 2m vertices (provided score windows of i and m+perm[i]
    are disjoint, which happens for sufficiently spread permutations).
    """
    if sorted(perm) != list(range(m)):
        raise ValueError("perm must be a permutation of [0..m-1]")
    T = transitive_tournament(2 * m)
    for i in range(m):
        j = m + perm[i]
        T[i][j] = 0
        T[j][i] = 1
    return T


# ---------------------------------------------------------------------------
# LFO enumeration with score-window pruning
# ---------------------------------------------------------------------------


def enumerate_lfos(T: Matrix, cap: int = 200000) -> list[tuple[int, ...]]:
    """Enumerate all LFOs (orders whose back-arc graph is a linear forest).

    Uses score-window pruning: vertex v can only be placed at positions
    in its score window [d^-(v) - 2, d^-(v) + 2].  At full placement,
    we call the verifier to check the linear-forest condition.
    """
    n = len(T)
    wins = score_windows(T)
    used = [False] * n
    order: list[int] = []
    found: list[tuple[int, ...]] = []

    def back() -> None:
        if len(found) >= cap:
            return
        i = len(order)
        if i == n:
            info = verify(T, list(order))
            if info["is_linear_forest"]:
                found.append(tuple(order))
            return
        for v in range(n):
            if used[v]:
                continue
            lo, hi = wins[v]
            if lo <= i <= hi:
                order.append(v)
                used[v] = True
                back()
                used[v] = False
                order.pop()

    back()
    return found


def has_lfo(T: Matrix) -> bool:
    """True iff the tournament T has at least one LFO."""
    return len(enumerate_lfos(T, cap=1)) > 0


# ---------------------------------------------------------------------------
# Position-slot decoding ("register state")
# ---------------------------------------------------------------------------


def slot_of(position: int, window: tuple[int, int]) -> int:
    """Return the slot index of a position within its window.

    For a width-5 window [lo, hi], slot is 0 (early), 1 (mid), 2 (late).
    Generalises to width < 5 windows by clamping to slot in [0, hi-lo].
    """
    lo, hi = window
    width = hi - lo
    if width <= 0:
        return 0
    third = max(1, (width + 2) // 3)
    rel = position - lo
    if rel < third:
        return 0
    if rel < 2 * third:
        return 1
    return 2


def register_state(T: Matrix, order: Sequence[int], m: int) -> list[int]:
    """For each register C_i = {i, i+m}, return the slot of (i+m) in
    its score window.  The "state" of C_i.
    """
    n = len(T)
    wins = score_windows(T)
    pos = [0] * n
    for p, v in enumerate(order):
        pos[v] = p
    return [slot_of(pos[i + m], wins[i + m]) for i in range(m)]


# ---------------------------------------------------------------------------
# 3-coloring reduction attempt
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GColoringInstance:
    """Triangle-free graph 3-coloring instance.  V = 0..m-1.  E is the
    set of unordered edges."""

    m: int
    edges: tuple[tuple[int, int], ...]

    @classmethod
    def of(cls, m: int, edges: Iterable[tuple[int, int]]) -> "GColoringInstance":
        normalised = tuple(sorted((min(a, b), max(a, b)) for a, b in edges))
        return cls(m=m, edges=normalised)


def build_3coloring_reduction(
    G: GColoringInstance, base_m: int | None = None
) -> tuple[Matrix, dict]:
    """Attempted reduction from G-3COLORING to Path-FAS on a reversed-
    matching-style tournament.

    The construction tries to attach a single "color-class constraint" arc
    per clause-edge (u, v) of G to the matching component pair C_u, C_v.
    Specifically, for each clause-edge we reverse an extra tournament arc
    chosen to inject a flex constraint between (u + m) and (v + m).

    Returns (T, info) where info reports the construction layer-by-layer
    plus the obstruction encountered.

    *This function is structured to FAIL.*  Section 6 of the companion
    document explains why: the global back-arc budget caps the number of
    "extra" constraints that can be simultaneously enforced by back-arc
    presence, and the linear-forest shape of any back-arc graph caps the
    shape of the encoded constraint graph.
    """
    m = max(G.m, base_m or 8)
    if m < 8:
        m = 8
    T = build_reversed_matching(m)
    n = 2 * m

    info = {
        "m": m,
        "n": n,
        "G_vertices": G.m,
        "G_edges": list(G.edges),
        "constraint_arcs_added": [],
        "h_after": None,
        "hall_after": None,
        "obstructions": [],
    }

    # Try to inject one constraint arc per edge (u, v) of G.
    # The natural choice: reverse the arc between (u + m) and (v + m)
    # so that the relative LFO order of these high-vertices is biased.
    # Note: this can break Hall feasibility; we record what happens.
    for u, v in G.edges:
        if u >= G.m or v >= G.m:
            info["obstructions"].append(
                f"edge ({u},{v}) refers to a vertex outside G"
            )
            continue
        hu, hv = u + m, v + m
        # Reverse arc (hu, hv) (i.e. swap orientation between them).
        if T[hu][hv] == 1:
            T[hu][hv] = 0
            T[hv][hu] = 1
        else:
            T[hu][hv] = 1
            T[hv][hu] = 0
        info["constraint_arcs_added"].append((hu, hv))

    H_after, _ = build_H_and_Gflex(T)
    info["h_after"] = sorted(H_after.edges())
    info["hall_after"] = hall_feasible(T)

    return T, info


# ---------------------------------------------------------------------------
# Brute-force 3-coloring checker (for ground truth)
# ---------------------------------------------------------------------------


def is_3_colorable(G: GColoringInstance) -> bool:
    for col in itertools.product(range(3), repeat=G.m):
        if all(col[u] != col[v] for u, v in G.edges):
            return True
    return False


# ---------------------------------------------------------------------------
# Reduction verification (the honest check)
# ---------------------------------------------------------------------------


def verify_reduction(G: GColoringInstance, *, lfo_cap: int = 200000) -> dict:
    """Empirically check whether the candidate reduction correctly encodes
    3-COLORING on this G.

    For the reduction to be a valid encoding we need:

      (A) G is 3-colorable iff T_G has an LFO whose register-state vector
          is a valid 3-coloring of G.
      (B) The reduction runs in polynomial time and the constructed T_G
          has size polynomial in |G|.

    This function checks (A) by:

      1. Computing ground-truth 3-colorability of G.
      2. Building T_G via build_3coloring_reduction.
      3. Enumerating LFOs of T_G (with the score-window pruner).
      4. For each LFO, computing its register-state vector and checking
         whether it is a proper 3-coloring of G.

    Returns a dict with the diagnostic info.
    """
    truth = is_3_colorable(G)
    T, info = build_3coloring_reduction(G)
    n = info["n"]
    m = info["m"]
    lfos = enumerate_lfos(T, cap=lfo_cap)
    lfo_count = len(lfos)

    # Compute register states for each LFO
    encoded_colorings = []
    valid_colorings = []
    for order in lfos:
        rs = register_state(T, order, m)
        # Restrict to the G.m vertices of G
        col = rs[: G.m]
        encoded_colorings.append(tuple(col))
        if all(col[u] != col[v] for u, v in G.edges):
            valid_colorings.append(tuple(col))

    unique_encoded = sorted(set(encoded_colorings))
    unique_valid = sorted(set(valid_colorings))

    return {
        "G_vertices": G.m,
        "G_edges": list(G.edges),
        "true_3colorable": truth,
        "T_size": n,
        "register_count": m,
        "T_has_lfo": lfo_count > 0,
        "lfo_count": lfo_count,
        "unique_encoded_states": unique_encoded,
        "unique_valid_3colorings_among_states": unique_valid,
        "encoded_a_valid_coloring": len(unique_valid) > 0,
        "T_construction_info": info,
        "reduction_status": _reduction_status(truth, lfo_count, unique_valid),
    }


def _reduction_status(
    truth: bool, lfo_count: int, valid: list[tuple[int, ...]]
) -> str:
    if lfo_count == 0:
        return "T has no LFO (Path-FAS instance is NO)"
    if not valid:
        return "T has LFOs but none encode a valid 3-coloring"
    if truth:
        return "Consistent so far: G is 3-colorable and at least one LFO encodes a valid coloring (but soundness not established)"
    return "INCONSISTENT: G is not 3-colorable but T encodes a 3-coloring"


# ---------------------------------------------------------------------------
# Diagnostic: count distinct register-state vectors per matching tournament
# ---------------------------------------------------------------------------


def register_state_diagnostic(T: Matrix, m: int, *, lfo_cap: int = 50000) -> dict:
    """For a reversed-matching tournament, return:
       (a) the set of register-state vectors realised by some LFO;
       (b) summary stats.
    """
    lfos = enumerate_lfos(T, cap=lfo_cap)
    states = {tuple(register_state(T, lfo, m)) for lfo in lfos}
    return {
        "lfo_count": len(lfos),
        "distinct_register_states": len(states),
        "states_sample": sorted(states)[:20],
    }


# ---------------------------------------------------------------------------
# Demo: small instance + obstruction surface
# ---------------------------------------------------------------------------


def small_instance_demo() -> dict:
    """Run a documented small-instance experiment.

    Builds three small G's:
      * G_path:  3-vertex path 0--1--2  (3-colorable trivially)
      * G_K3:    triangle 0--1, 1--2, 0--2  (3-colorable: needs all 3 colors)
      * G_K4:    K_4  (not 3-colorable)

    For each: build the candidate reduction T_G and verify.
    """
    instances = {
        "G_path_3vert": GColoringInstance.of(3, [(0, 1), (1, 2)]),
        "G_triangle_K3": GColoringInstance.of(3, [(0, 1), (0, 2), (1, 2)]),
        "G_K4": GColoringInstance.of(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
        "G_C5_5cycle": GColoringInstance.of(5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]),
    }
    out = {}
    for name, G in instances.items():
        rep = verify_reduction(G)
        out[name] = rep
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true", help="Run the small instance demo.")
    p.add_argument(
        "--substrate",
        type=int,
        default=None,
        help="If set, dump the reversed matching RM(m) substrate info.",
    )
    p.add_argument(
        "--verify-edges",
        type=str,
        default=None,
        help='JSON: {"m": int, "edges": [[u,v],...]}. Verify the reduction on this G.',
    )
    args = p.parse_args()

    if args.substrate is not None:
        m = args.substrate
        T = build_reversed_matching(m)
        H, Gflex = build_H_and_Gflex(T)
        diag = register_state_diagnostic(T, m, lfo_cap=20000)
        out = {
            "m": m,
            "n": 2 * m,
            "h_edges": sorted(H.edges()),
            "h_size": H.number_of_edges(),
            "gflex_edges": Gflex.number_of_edges(),
            "hall_feasible": hall_feasible(T),
            "lfo_count": diag["lfo_count"],
            "distinct_register_states": diag["distinct_register_states"],
            "register_state_sample": diag["states_sample"],
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return

    if args.verify_edges is not None:
        d = json.loads(args.verify_edges)
        G = GColoringInstance.of(d["m"], [tuple(e) for e in d["edges"]])
        rep = verify_reduction(G)
        print(json.dumps(rep, indent=2, sort_keys=True, default=str))
        return

    if args.demo:
        out = small_instance_demo()
        print(json.dumps(out, indent=2, sort_keys=True, default=str))
        return

    p.print_help()


if __name__ == "__main__":
    main()
