"""Forced-forest frontier diagnostics for the Path-FAS score-window sweep.

The refined width theorem gives the safe but blunt bound

    pw(J) <= 8 + 2|H|.

It does this by adding every endpoint of every forced backedge to every
bag of the interval decomposition of the flexible graph.  This script
measures how much of that endpoint set is genuinely "live" at each
score-window cut.

Definitions at position p:

* active vertex: p lies in its score window.
* closed vertex: its score window ends before p.
* future vertex: its score window starts after p.
* live H-component: a connected component of the forced-backedge graph
  H that either intersects the active band, or has vertices on both
  sides of the current cut.  A component entirely closed is inert; a
  component entirely future has not interacted with the prefix yet.
* crossing H-edge: an H-edge whose endpoints are not in the same
  closed/active/future category at p.

The optimistic "forced-frontier compression" size reported here is

    active_count + 2 * live_H_components.

This is only a diagnostic upper bound for a hypothetical compressed
state; it is not a correctness theorem.  If this quantity is linear on
a clean family, the endpoint-compression route is likely dead.  If it
stays small on adversarial families, the next target is a formal
replacement lemma for closed H-path segments.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import asdict, dataclass
from typing import Sequence

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interaction_graph import build_H_and_Gflex, hall_feasible, score_windows  # noqa: E402

Matrix = Sequence[Sequence[int]]


@dataclass(frozen=True)
class FrontierAtCut:
    position: int
    active_count: int
    closed_count: int
    future_count: int
    live_h_components: int
    live_h_vertices: int
    dormant_crossing_components: int
    crossing_h_edges: int
    crossing_h_endpoints: int
    compressed_frontier_size: int
    blunt_endpoint_bag_size: int


@dataclass(frozen=True)
class FrontierReport:
    n: int
    hall_ok: bool
    h_edges: int
    h_components: int
    max_active_count: int
    max_live_h_components: int
    max_live_h_vertices: int
    max_dormant_crossing_components: int
    max_crossing_h_edges: int
    max_crossing_h_endpoints: int
    max_compressed_frontier_size: int
    max_blunt_endpoint_bag_size: int
    cuts: list[FrontierAtCut]

    def as_dict(self) -> dict:
        d = asdict(self)
        d["cuts"] = [asdict(c) for c in self.cuts]
        return d


def transitive_tournament(n: int) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    return T


def reversed_matching_tournament(m: int) -> list[list[int]]:
    """Transitive tournament on 2m vertices with arcs i -> i+m reversed."""
    T = transitive_tournament(2 * m)
    for i in range(m):
        T[i][i + m] = 0
        T[i + m][i] = 1
    return T


def random_skew_tournament(n: int, flips: int, seed: int) -> list[list[int]]:
    """Transitive tournament with `flips` random forward arcs reversed."""
    rng = random.Random(seed)
    T = transitive_tournament(n)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    for i, j in pairs[:flips]:
        T[i][j] = 0
        T[j][i] = 1
    return T


def _status(lo: int, hi: int, p: int) -> str:
    if hi < p:
        return "closed"
    if lo > p:
        return "future"
    return "active"


def forced_frontier_profile(T: Matrix, radius: int = 2) -> FrontierReport:
    """Return forced-frontier diagnostics across all sweep positions."""
    n = len(T)
    windows = score_windows(T, radius)
    H, _ = build_H_and_Gflex(T, radius)
    U = H.to_undirected()
    h_endpoint_count = len({v for e in U.edges() for v in e})
    components = [
        set(c)
        for c in nx.connected_components(U)
        if any(U.degree(v) > 0 for v in c)
    ]
    cuts: list[FrontierAtCut] = []

    for p in range(n):
        statuses = [_status(lo, hi, p) for lo, hi in windows]
        active = {v for v, s in enumerate(statuses) if s == "active"}
        closed = {v for v, s in enumerate(statuses) if s == "closed"}
        future = {v for v, s in enumerate(statuses) if s == "future"}

        live_components = 0
        live_vertices = 0
        dormant_crossing_components = 0
        for comp in components:
            has_active = bool(comp & active)
            has_closed = bool(comp & closed)
            has_future = bool(comp & future)
            live = has_active or (has_closed and has_future)
            if live:
                live_components += 1
                live_vertices += len(comp)
            if has_closed and has_future and not has_active:
                dormant_crossing_components += 1

        crossing_edges: list[tuple[int, int]] = []
        for u, v in U.edges():
            if statuses[u] != statuses[v]:
                crossing_edges.append((u, v))
        crossing_endpoints = {v for e in crossing_edges for v in e}

        compressed = len(active) + 2 * live_components
        blunt = len(active) + h_endpoint_count
        cuts.append(
            FrontierAtCut(
                position=p,
                active_count=len(active),
                closed_count=len(closed),
                future_count=len(future),
                live_h_components=live_components,
                live_h_vertices=live_vertices,
                dormant_crossing_components=dormant_crossing_components,
                crossing_h_edges=len(crossing_edges),
                crossing_h_endpoints=len(crossing_endpoints),
                compressed_frontier_size=compressed,
                blunt_endpoint_bag_size=blunt,
            )
        )

    return FrontierReport(
        n=n,
        hall_ok=hall_feasible(T, radius),
        h_edges=H.number_of_edges(),
        h_components=len(components),
        max_active_count=max((c.active_count for c in cuts), default=0),
        max_live_h_components=max((c.live_h_components for c in cuts), default=0),
        max_live_h_vertices=max((c.live_h_vertices for c in cuts), default=0),
        max_dormant_crossing_components=max(
            (c.dormant_crossing_components for c in cuts), default=0
        ),
        max_crossing_h_edges=max((c.crossing_h_edges for c in cuts), default=0),
        max_crossing_h_endpoints=max((c.crossing_h_endpoints for c in cuts), default=0),
        max_compressed_frontier_size=max(
            (c.compressed_frontier_size for c in cuts), default=0
        ),
        max_blunt_endpoint_bag_size=max((c.blunt_endpoint_bag_size for c in cuts), default=0),
        cuts=cuts,
    )


def summarize_family(kind: str, sizes: list[int], seed: int = 20260527) -> list[dict]:
    rows: list[dict] = []
    for size in sizes:
        if kind == "transitive":
            T = transitive_tournament(size)
        elif kind == "reversed_matching":
            T = reversed_matching_tournament(size)
        elif kind == "random_skew":
            T = random_skew_tournament(size, max(1, size // 8), seed + size)
        else:
            raise ValueError(f"unknown family: {kind}")
        rep = forced_frontier_profile(T)
        d = rep.as_dict()
        d.pop("cuts")
        d["family"] = kind
        d["size_parameter"] = size
        rows.append(d)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", help="Tournament as JSON matrix")
    parser.add_argument(
        "--family",
        choices=["transitive", "reversed_matching", "random_skew"],
        help="Run a built-in family.",
    )
    parser.add_argument("--sizes", default="8,12,20", help="Comma-separated family sizes.")
    parser.add_argument("--seed", type=int, default=20260527)
    parser.add_argument("--with-cuts", action="store_true")
    args = parser.parse_args()

    if args.T:
        rep = forced_frontier_profile(json.loads(args.T))
        d = rep.as_dict()
        if not args.with_cuts:
            d.pop("cuts")
        print(json.dumps(d, indent=2, sort_keys=True))
        return

    if args.family:
        sizes = [int(x) for x in args.sizes.split(",") if x.strip()]
        print(json.dumps(summarize_family(args.family, sizes, args.seed), indent=2, sort_keys=True))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
