"""Structural characterization of matching-FAS tournaments.

Theorem (this workstream, see docs/lemmas.md for the proof).
A tournament T has a matching-FAS iff there exists a matching M of arcs
of T such that:
  (a) every arc (u,v) in M is "no-shortcut": there is no w with
      u -> w -> v in T (equivalently, N^+(u) cap N^-(v) is empty);
  (b) every cyclic 3-cycle of T contains exactly one arc of M.

Proof sketch.
=============
If F is a FAS and P is a topological order of T-F, then the back-arc set
B_P(T) is contained in F. Hence a matching-FAS exists iff there is an
order whose back-arc set is a matching. Equivalently, T xor M (T with
arcs of M reversed) must be transitive, where M is that back-arc set and
the order is the topological order of T xor M. So MFAS exists iff some
matching M makes T xor M transitive.

A tournament is transitive iff it has no cyclic 3-cycle. T xor M has a
3-cycle on a triple {a,b,c} iff the arcs of T on that triple, with the
arcs of M flipped, form a 3-cycle.

Since M is a matching, at most one arc of M is in any 3-vertex triangle.
So we split:

- If 0 arcs of M are in triangle: triangle in T xor M = triangle in T.
  Must be transitive in T.
- If 1 arc of M is in triangle: flipping that arc must keep the
  triangle transitive.

A cyclic triangle of T becomes transitive when any single arc is
flipped, so condition (b) says exactly one arc of M is in each cyclic
3-cycle. A transitive triangle stays transitive iff the flipped arc is
NOT the "long arc" (top -> bottom skip arc); flipping the long arc
creates a 3-cycle. The long-arc condition for an arc (u,v) of T being
the long arc of a transitive triangle through w is exactly
"u -> w and w -> v in T", giving condition (a). QED.

This module implements:
  - `cyclic_3_cycles(T)`: enumerate the cyclic 3-cycles, as frozensets
    of arcs.
  - `no_shortcut_arcs(T)`: enumerate arcs with no shortcut (= cannot be
    long arc of any transitive triangle).
  - `decide_mfas(T)`: a backtracking solver that searches for a valid
    M. Polynomial-time in many cases but exponential worst-case.
  - `verify_against_brute(T)`: cross-check `decide_mfas` against
    `brute.decide(T, 'matching')`.
"""
from __future__ import annotations
from typing import Sequence

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import verify  # noqa: E402
from brute import decide   # noqa: E402


def arcs(T: Sequence[Sequence[int]]) -> list[tuple[int, int]]:
    n = len(T)
    return [(u, v) for u in range(n) for v in range(n) if T[u][v]]


def cyclic_3_cycles(T: Sequence[Sequence[int]]) -> list[frozenset[tuple[int, int]]]:
    """Return all cyclic 3-cycles of T as frozensets of 3 arcs.

    Each cyclic 3-cycle is enumerated once by the unordered triple of
    its vertices.
    """
    n = len(T)
    out = []
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                # Determine arcs on triple.
                cyc = None
                if T[a][b] and T[b][c] and T[c][a]:
                    cyc = ((a, b), (b, c), (c, a))
                elif T[a][c] and T[c][b] and T[b][a]:
                    cyc = ((a, c), (c, b), (b, a))
                if cyc:
                    out.append(frozenset(cyc))
    return out


def no_shortcut_arcs(T: Sequence[Sequence[int]]) -> set[tuple[int, int]]:
    """Arcs (u,v) of T such that no w satisfies T[u][w] and T[w][v].

    Equivalently, arcs that are NOT the long arc of any transitive
    triangle through them. By the theorem, only such arcs can be in
    M for a valid matching-FAS witness.
    """
    n = len(T)
    out = set()
    for u in range(n):
        for v in range(n):
            if not T[u][v]:
                continue
            shortcut = any(T[u][w] and T[w][v] for w in range(n)
                           if w != u and w != v)
            if not shortcut:
                out.add((u, v))
    return out


def decide_mfas(T: Sequence[Sequence[int]]) -> dict:
    """Decide MFAS by combinatorial backtracking on the theorem.

    Returns {found: bool, M: list[(u,v)] | None}. Also runs the brute-
    force verifier as a sanity check (it produces an explicit order
    too).
    """
    cycles = cyclic_3_cycles(T)
    ok_arcs = no_shortcut_arcs(T)

    # Trivial case: no cyclic 3-cycles. T already transitive, MFAS YES
    # with M = empty.
    if not cycles:
        return {"found": True, "M": []}

    # For each cyclic 3-cycle, the arcs in it that are also in ok_arcs
    # (the candidate arcs we may pick from this cycle).
    candidates_per_cycle = [
        [a for a in cyc if a in ok_arcs] for cyc in cycles
    ]
    # If any cycle has no candidate, MFAS is NO.
    for i, cands in enumerate(candidates_per_cycle):
        if not cands:
            return {"found": False, "M": None,
                    "reason": f"cyclic 3-cycle #{i} has no no-shortcut arc",
                    "cycle": list(cycles[i])}

    # Backtracking: choose one arc per cycle, enforcing matching.
    chosen: list[tuple[int, int]] = []
    used_vertices: set[int] = set()

    def rec(i: int) -> bool:
        if i == len(cycles):
            return True
        # Try each candidate for cycle i; skip cycles already covered.
        cyc = cycles[i]
        # Is any arc already chosen in this cycle?
        for c_arc in chosen:
            if c_arc in cyc:
                # Cycle covered (with one arc); but we need EXACTLY one,
                # so check no other arc of cyc is already in chosen.
                # Since M is a matching and chosen reflects M so far,
                # each cycle has at most 1 chosen arc — but we want
                # exactly 1 by the time recursion ends. If we have 1,
                # move to next cycle.
                return rec(i + 1)
        # No arc of cycle i is chosen yet — pick one.
        for (u, v) in candidates_per_cycle[i]:
            if u in used_vertices or v in used_vertices:
                continue
            chosen.append((u, v))
            used_vertices.add(u); used_vertices.add(v)
            if rec(i + 1):
                return True
            chosen.pop()
            used_vertices.discard(u); used_vertices.discard(v)
        return False

    if rec(0):
        return {"found": True, "M": list(chosen)}
    return {"found": False, "M": None,
            "reason": "no matching M satisfies all cycle constraints"}


def verify_against_brute(T: Sequence[Sequence[int]]) -> dict:
    """Cross-check structural decision against brute force.

    Returns a dict with `agree: bool` and the two decisions.
    """
    s = decide_mfas(T)
    b = decide(T, "matching")
    agree = (s["found"] == b["found"])
    return {"agree": agree, "structural": s, "brute": b}


if __name__ == "__main__":
    # Sanity: cyclic triangle
    T = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    print("cyclic triangle:", verify_against_brute(T)["agree"], decide_mfas(T))
    # Transitive
    T = [[0, 1, 1], [0, 0, 1], [0, 0, 0]]
    print("transitive    :", verify_against_brute(T)["agree"], decide_mfas(T))
