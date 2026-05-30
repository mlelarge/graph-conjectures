"""Forced-Loader Realizability for the n=7 exactly-2-in-3 candidate (D72).

The n=7 port-relation census (D71) found one disjoint-port gadget whose
lenient composable shadow is the non-Schaefer relation

    R_comp = {011, 101, 110} = exactly-2-in-3,

but whose STRICT shadow is empty (each 2-in-3 vector has a single
capacity witness).  The idealized composition (reserve one back-degree
per port vertex) realizes exactly 2-in-3, but realizing that reservation
as an actual tournament is constrained by score windows.

This module attacks the Loader Gap question directly:

  Given the candidate gadget G and a port endpoint v, can we extend the
  tournament (padding + a loader ell) so that
    (1) ell -> v is a FORCED back-arc in every score-window LFO,
    (2) ell consumes exactly one degree at v and does not otherwise
        distort the internal port relation,
    (3) the composed port relation is exactly 2-in-3?

It builds augmented tournaments (gadget + ordered top block of extra
vertices, some designated loaders with a reversed arc to a port vertex),
enumerates all valid LFOs with a score-window backtracker, projects to
the three port bits, and classifies the realized relation.

Outcomes per extension:
  * "exact_2in3"      — composed relation == {011,101,110};
  * "schaefer_only"   — composed relation is Schaefer;
  * "no_lfo"          — no valid LFO (over-constrained);
  * "distorted"       — some other relation.

A negative sweep is evidence for the Loader Gap Lemma:
  For the candidate's high-degree port vertices, any forced external
  back-arc shifts the score-window structure enough to destroy 2-in-3.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_forced_flexible import _find, _union  # noqa: E402
from lfo_score_window import hall_interval_ok, score_windows  # noqa: E402


Matrix = list[list[int]]

# The pinned n=7 candidate (D71).
CANDIDATE_G: Matrix = [
    [0, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 0],
    [1, 1, 0, 0, 1, 0, 0],
    [1, 1, 1, 0, 0, 0, 0],
    [1, 1, 0, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 0, 0],
]
CANDIDATE_PORTS = [(0, 1), (3, 4), (5, 6)]
CANDIDATE_ORIENT = (0, 1, 1)
TWO_IN_THREE = frozenset({(0, 1, 1), (1, 0, 1), (1, 1, 0)})


# ----------------------------------------------------------------------
# 1. Score-window LFO enumerator (backtracking, prunes degree+cycle+Hall)
# ----------------------------------------------------------------------

def enumerate_lfos(T: Matrix, cap: int | None = None) -> list[tuple[int, ...]]:
    """All orders whose back-arc graph is a linear forest, found by
    score-window backtracking.  `cap` optionally bounds the number of
    LFOs collected (None = all)."""
    n = len(T)
    windows = score_windows(T)
    all_mask = (1 << n) - 1
    results: list[tuple[int, ...]] = []

    def rec(pos: int, placed: int, degree: tuple[int, ...],
            parent: tuple[int, ...], order: list[int]) -> bool:
        if pos == n:
            results.append(tuple(order))
            return cap is not None and len(results) >= cap
        remaining = all_mask ^ placed
        if not hall_interval_ok(remaining, pos, windows, n):
            return False
        for v in range(n):
            if (placed >> v) & 1:
                continue
            lo, hi = windows[v]
            if not (lo <= pos <= hi):
                continue
            nbrs = [u for u in range(n) if (placed >> u) & 1 and T[v][u]]
            if degree[v] + len(nbrs) > 2:
                continue
            deg = list(degree)
            par = list(parent)
            ok = True
            for u in nbrs:
                if deg[u] >= 2 or _find(par, v) == _find(par, u):
                    ok = False
                    break
                deg[v] += 1
                deg[u] += 1
                _union(par, v, u)
            if not ok:
                continue
            order.append(v)
            stop = rec(pos + 1, placed | (1 << v), tuple(deg), tuple(par), order)
            order.pop()
            if stop:
                return True
        return False

    rec(0, 0, tuple([0] * n), tuple(range(n)), [])
    return results


def port_relation_of(T: Matrix, ports, orient) -> frozenset:
    """Realized port relation over all valid LFOs of T."""
    lfos = enumerate_lfos(T)
    rel: set[tuple[int, ...]] = set()
    for P in lfos:
        pos = [0] * len(T)
        for i, v in enumerate(P):
            pos[v] = i
        raw = tuple(1 if pos[y] < pos[x] else 0 for (x, y) in ports)
        rel.add(tuple(b ^ o for b, o in zip(raw, orient)))
    return frozenset(rel)


# ----------------------------------------------------------------------
# 2. Augmented-tournament construction (gadget + top block + loaders)
# ----------------------------------------------------------------------

def build_augmented(
    G: Matrix,
    n_extra: int,
    loaders: dict[int, int],
) -> Matrix:
    """Gadget G (vertices 0..g-1) plus `n_extra` extra vertices on top
    (indices g..g+n_extra-1), transitive among themselves and above the
    gadget.  `loaders` maps an extra-vertex index -> a gadget port
    vertex it reverse-points to (forcing a candidate back-arc)."""
    g = len(G)
    n = g + n_extra
    T = [[0] * n for _ in range(n)]
    # transitive base i -> j for i < j
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    # overwrite gadget block with G
    for i in range(g):
        for j in range(g):
            T[i][j] = G[i][j]
    # loaders: reverse extra -> port vertex
    for ell, v in loaders.items():
        T[ell][v] = 1
        T[v][ell] = 0
    return T


def is_forced_backarc(T: Matrix, src: int, tgt: int) -> bool:
    """ell=src -> tgt is forced iff their score windows are disjoint with
    src strictly above tgt (so src is always placed after tgt)."""
    windows = score_windows(T)
    return windows[src][0] > windows[tgt][1]


# ----------------------------------------------------------------------
# 3. Realizability search
# ----------------------------------------------------------------------

def classify_relation(rel: frozenset) -> str:
    if not rel:
        return "no_lfo"
    if rel == TWO_IN_THREE:
        return "exact_2in3"
    from port_relation_census import schaefer_flags
    if schaefer_flags(rel, 3)["non_schaefer"]:
        return "non_schaefer_other"
    return "schaefer_only"


def search(
    G: Matrix = CANDIDATE_G,
    ports=CANDIDATE_PORTS,
    orient=CANDIDATE_ORIENT,
    max_extra: int = 10,
) -> dict:
    """Search loader/padding configurations and classify the realized
    port relation.  Port vertices to load: all six endpoints of `ports`.

    Strategy: add `n_extra` top vertices; assign the highest extras as
    loaders to the highest-degree port vertices (which are hardest to
    force).  Vary n_extra and which ports are loaded."""
    g = len(G)
    port_vertices = [v for pr in ports for v in pr]
    # order port vertices by in-degree descending (hardest to force first)
    indeg = {v: sum(G[i][v] for i in range(g)) for v in port_vertices}
    by_hard = sorted(port_vertices, key=lambda v: -indeg[v])

    base_rel = port_relation_of(G, ports, orient)
    results = []
    outcomes: dict[str, int] = {}
    first_exact = None

    for n_extra in range(len(port_vertices), max_extra + 1):
        # assign the TOP loaders to the hardest port vertices: extra
        # vertex (g + n_extra - 1) is highest, give it the hardest port.
        loaders = {}
        # the top `len(port_vertices)` extras are loaders, lowest extras pad
        loader_slots = list(range(g + n_extra - len(port_vertices), g + n_extra))
        # highest slot -> hardest port
        for slot, v in zip(reversed(loader_slots), by_hard):
            loaders[slot] = v
        T = build_augmented(G, n_extra, loaders)
        forced = {ell: is_forced_backarc(T, ell, v) for ell, v in loaders.items()}
        all_forced = all(forced.values())
        rel = port_relation_of(T, ports, orient)
        outcome = classify_relation(rel)
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        rec = {
            "n_extra": n_extra,
            "n_total": g + n_extra,
            "loaders": {str(k): v for k, v in loaders.items()},
            "all_loaders_forced": all_forced,
            "forced_detail": {str(k): forced[k] for k in forced},
            "realized_relation": sorted(tuple(b) for b in rel),
            "outcome": outcome,
        }
        results.append(rec)
        if outcome == "exact_2in3" and first_exact is None:
            first_exact = rec

    return {
        "candidate": "n7_2in3",
        "base_relation_without_loaders": sorted(tuple(b) for b in base_rel),
        "port_indegrees": indeg,
        "outcome_counts": outcomes,
        "exact_2in3_realized": first_exact is not None,
        "first_exact": first_exact,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-extra", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(search(max_extra=args.max_extra), indent=2, default=list))


if __name__ == "__main__":
    main()
