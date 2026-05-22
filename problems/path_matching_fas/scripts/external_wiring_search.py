"""Asymmetric external wiring search for the path-FAS hardness route.

The 7-vertex two-state port block exposes Y={4,5} as path endpoints in the
L state (x precedes l) and N={2,3} as path endpoints in the R state. The
inactive ports have no spare degree, so adding extra back-arcs to them
directly would break the LFO.

This script asks the dual question. For a single external "clause"
vertex c added to the 7-block, with arbitrary orientation of the 7 arcs
c <-> block, does there exist an orientation such that:

  - the combined 8-vertex tournament still has an LFO whose 7-block
    restriction is the L-state ordering, AND in that LFO every back-arc
    incident to c lands on a Y port (active in L);
  - similarly, the combined tournament has an LFO whose 7-block
    restriction is the R-state ordering, AND in that LFO every back-arc
    incident to c lands on an N port (active in R)?

If yes, this is the first concrete evidence that AAL-style clause arcs
can be routed asymmetrically to respect the path-FAS degree bound.
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from path_state_signature import TWO_STATE_PORT_BLOCK  # noqa: E402


# Block labels: x=0, l=1, n1=2, n2=3, y1=4, y2=5, q=6.
N_PORTS = (2, 3)
Y_PORTS = (4, 5)
X_VERTEX = 0
L_VERTEX = 1

# Two LFO orders of the bare 7-block, identified earlier.
L_ORDER = (6, 4, 0, 1, 5, 2, 3)   # x precedes l: y endpoints
R_ORDER = (6, 1, 4, 5, 2, 3, 0)   # l precedes x: n endpoints

BLOCK_N = 7
BLOCK_VERTICES = tuple(range(BLOCK_N))


def _find(parent: list[int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def back_arc_data(T: Sequence[Sequence[int]], order: Sequence[int]) -> dict | None:
    """Return back-arc info; None if the back-arc graph is not a linear forest."""
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    arcs = []
    deg = [0] * n
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[v] < pos[u]:
                arcs.append((u, v))
                deg[u] += 1
                deg[v] += 1
    if max(deg, default=0) > 2:
        return None
    parent = list(range(n))
    for u, v in arcs:
        ru = _find(parent, u)
        rv = _find(parent, v)
        if ru == rv:
            return None
        parent[ru] = rv
    return {"order": tuple(order), "arcs": arcs, "deg": deg}


def build_combined(orientations: tuple[int, ...]) -> list[list[int]]:
    """Build the 8-vertex tournament: 7-block + external vertex c=7.

    orientations[i] = 1 if T[c][i] = 1 (c -> block_i), else T[i][c] = 1.
    """
    assert len(orientations) == BLOCK_N
    n = BLOCK_N + 1
    T = [[0] * n for _ in range(n)]
    for u in range(BLOCK_N):
        for v in range(BLOCK_N):
            T[u][v] = TWO_STATE_PORT_BLOCK[u][v]
    c = BLOCK_N
    for v, b in enumerate(orientations):
        if b == 1:
            T[c][v] = 1
        else:
            T[v][c] = 1
    return T


def insertions(base_order: Sequence[int]) -> list[tuple[int, ...]]:
    """Return the 8 orderings obtained by inserting c=7 at any position
    of the 7-block ordering.
    """
    out = []
    for p in range(BLOCK_N + 1):
        seq = list(base_order)
        seq.insert(p, BLOCK_N)
        out.append(tuple(seq))
    return out


def classify_external_hits(arcs, c_vertex: int, ports: tuple[int, ...]) -> dict:
    """Look at back-arcs touching c and classify their other endpoint."""
    inactive_set = set()
    active_hits = []
    inactive_hits = []
    c_degree = 0
    for u, v in arcs:
        if u == c_vertex:
            c_degree += 1
            other = v
        elif v == c_vertex:
            c_degree += 1
            other = u
        else:
            continue
        if other in ports:
            active_hits.append(other)
        else:
            inactive_hits.append(other)
    return {
        "c_degree": c_degree,
        "active_hits": tuple(active_hits),
        "inactive_hits": tuple(inactive_hits),
    }


def search() -> list[dict]:
    """Enumerate all 2^7 orientations of c <-> block.

    For each, find every combined-LFO obtained by inserting c into the L
    or R order. Record orientations satisfying both:
      (L) at least one L-insertion LFO has c hitting only Y ports;
      (R) at least one R-insertion LFO has c hitting only N ports.
    """
    good: list[dict] = []
    for bits in itertools.product((0, 1), repeat=BLOCK_N):
        T = build_combined(bits)
        c = BLOCK_N

        # Collect LFOs by L- and R-insertion separately.
        l_lfo_records = []
        r_lfo_records = []
        for combined in insertions(L_ORDER):
            data = back_arc_data(T, combined)
            if data is None:
                continue
            # By definition the L-insertion ordering has x ≺ l (we are
            # inserting c into an order where x is at position 2 and l at
            # position 3 of the original).
            cls = classify_external_hits(data["arcs"], c, Y_PORTS)
            l_lfo_records.append({"order": combined, **data, **cls})
        for combined in insertions(R_ORDER):
            data = back_arc_data(T, combined)
            if data is None:
                continue
            cls = classify_external_hits(data["arcs"], c, N_PORTS)
            r_lfo_records.append({"order": combined, **data, **cls})

        l_clean = [r for r in l_lfo_records if not r["inactive_hits"]]
        r_clean = [r for r in r_lfo_records if not r["inactive_hits"]]
        if not l_clean or not r_clean:
            continue
        # Additionally require that c actually hits at least one active
        # port in each state (the wiring should not be vacuous).
        l_active = [r for r in l_clean if r["active_hits"]]
        r_active = [r for r in r_clean if r["active_hits"]]
        if not l_active or not r_active:
            continue
        good.append({
            "orientations": bits,
            "l_witness": l_active[0],
            "r_witness": r_active[0],
            "l_clean_count": len(l_active),
            "r_clean_count": len(r_active),
        })
    return good


def summarize(records: list[dict]) -> dict:
    if not records:
        return {"count": 0, "examples": []}
    # Dedup by (orientations, witnesses) is irrelevant; just sample a few.
    return {
        "count": len(records),
        "examples": records[:5],
        "orientation_set": sorted({r["orientations"] for r in records}),
    }


def search_summary() -> dict:
    records = search()
    return summarize(records)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    s = search_summary()
    print(f"Asymmetric wiring search over 2^{BLOCK_N} = {2**BLOCK_N} orientations.")
    print(f"Orientations admitting clean L and R wirings: {s['count']}")
    if args.verbose and s["count"]:
        for ex in s["examples"]:
            print(ex)


if __name__ == "__main__":
    main()
