"""Band-decomposition probe for the score-window theorem.

By the score-window theorem (docs/score_window.md) any LFO satisfies
|pos(v) - d^-(v)| <= 2 for every v.  Partition position indices into
disjoint bands of width B:

    band_j = [jB, jB + B - 1].

The question this probe answers empirically is:

  HYPOTHESIS (band-decomposition).  There is a polynomial-size summary
  state that is sufficient to decide LFO band-by-band; i.e. the band-DP
  decides LFO correctly using only a polynomial summary of what has
  been placed.

We implement TWO band-DPs:

  - FULL-INFO band-DP (`band_dp_full`): state = (placed_mask,
    induced back-arc graph on placed_set).  This is equivalent to
    brute force restricted to orderings consistent with the band
    partition.  Its only purpose is to verify that orderings DO exist
    that respect bands (i.e. that the score-window theorem really lets
    LFOs slot into bands).

  - SUMMARY band-DP (`band_dp_summary`): state = (placed_mask,
    degree-vector on placed, union-find roots on placed).  This drops
    the explicit arc set but keeps the linear-forest invariants
    (degree<=2, acyclicity) plus the *identity* of every placed
    vertex (so unplaced vertices know which exact vertex they will
    attach to).  This is the strongest summary that is still polynomial
    in n at each band step (because |placed_mask| is fixed by the band
    boundary).

The SUMMARY DP is what real algorithms can implement.  We compare
SUMMARY against brute force, NOT FULL against brute force.

A disagreement between SUMMARY and brute force at band width B means:
the band-decomposition with summary state ALREADY LOSES INFORMATION
at width B.  Concretely: two prefixes with identical
(placed_mask, degree, UF) summaries — i.e. identical induced
linear-forest type — can have different LFO-extendability.

Output: smallest B where SUMMARY disagrees with brute force.

(For LFO, SUMMARY is in fact equivalent to FULL when we keep all
identities, because the linear-forest *type* is exactly determined by
deg+UF.  So we only run the SUMMARY DP.)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brute import decide  # noqa: E402
from lfo_score_window import indegrees, score_windows  # noqa: E402


Matrix = Sequence[Sequence[int]]


def _bands(n: int, B: int) -> list[tuple[int, int]]:
    return [(j, min(j + B - 1, n - 1)) for j in range(0, n, B)]


def _can_place_at(window: tuple[int, int], pos: int) -> bool:
    lo, hi = window
    return lo <= pos <= hi


def _find(parent: dict[int, int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def _try_add_arc(
    deg: dict[int, int],
    parent: dict[int, int],
    u: int,
    v: int,
) -> bool:
    """Attempt to add a single undirected arc (u, v) to current state.

    Mutates deg, parent on success.  Returns False if degree>2 or cycle.
    """
    if u not in parent:
        parent[u] = u
    if v not in parent:
        parent[v] = v
    if deg.get(u, 0) >= 2 or deg.get(v, 0) >= 2:
        return False
    ru, rv = _find(parent, u), _find(parent, v)
    if ru == rv:
        return False
    parent[rv] = ru
    deg[u] = deg.get(u, 0) + 1
    deg[v] = deg.get(v, 0) + 1
    return True


def band_dp_summary(T: Matrix, B: int, radius: int = 2,
                    use_uf: bool = True,
                    use_deg: bool = True,
                    return_stats: bool = False) -> bool | tuple[bool, dict]:
    """Summary-state band-DP.

    State = (placed_mask, [degree tuple], [UF root map]).

    `use_uf=True` keeps the UF partition (i.e. acyclic-component
    information).  `use_deg=True` keeps the degree vector.  Both default
    to True (this is the exact DP).  Setting `use_uf=False` tests the
    hypothesis "degree-only summary suffices"; `use_deg=False` tests
    "UF-only summary suffices"; setting both to False tests "placed_mask
    alone suffices" (this would be a trivial DP).

    NOTE: With both flags True the DP is sound and complete for the LFO
    decision problem.  Dropping either flag is what gives the empirical
    information-loss test.

    Transition: pick subset of unplaced vertices whose score-window
    intersects the current band, permute them into the band's positions
    (each respecting its window), accumulate forced new back-arcs from
    both
      (i) band -> earlier placed vertices,
      (ii) later band-vertex -> earlier band-vertex (within band).
    Check linear-forest preservation.  Reject if violated.

    Returns True iff some band sequence reaches full placement.
    """
    n = len(T)
    windows = score_windows(T, radius)
    bands = _bands(n, B)
    full = (1 << n) - 1

    # State key for dedup
    def state_key(placed_mask: int, deg: dict[int, int], parent: dict[int, int]):
        parts: list = [placed_mask]
        if use_deg:
            parts.append(tuple(deg.get(v, 0) for v in range(n)))
        if use_uf:
            parts.append(tuple(
                _find(parent, v) for v in range(n) if (placed_mask >> v) & 1
            ))
        return tuple(parts)

    max_states = 0

    start_deg: dict[int, int] = {}
    start_parent: dict[int, int] = {v: v for v in range(n)}
    frontier: dict[tuple, tuple[int, dict, dict]] = {
        state_key(0, start_deg, start_parent): (0, start_deg, start_parent)
    }

    for band in bands:
        size = band[1] - band[0] + 1
        new_frontier: dict[tuple, tuple[int, dict, dict]] = {}
        for key, (placed_mask, deg, parent) in frontier.items():
            available = [
                v for v in range(n)
                if not ((placed_mask >> v) & 1)
                and windows[v][0] <= band[1]
                and windows[v][1] >= band[0]
            ]
            if len(available) < size:
                continue
            for subset in combinations(available, size):
                for perm in permutations(subset):
                    # window check per slot
                    valid = True
                    for i, v in enumerate(perm):
                        if not _can_place_at(windows[v], band[0] + i):
                            valid = False
                            break
                    if not valid:
                        continue
                    deg2 = dict(deg)
                    par2 = dict(parent)
                    # type (a) back-arcs: band-vertex u -> placed p with T[u][p]
                    ok = True
                    for u in perm:
                        for p in range(n):
                            if (placed_mask >> p) & 1 and T[u][p]:
                                if not _try_add_arc(deg2, par2, u, p):
                                    ok = False
                                    break
                        if not ok:
                            break
                    if not ok:
                        continue
                    # type (b) back-arcs within band: later u'->earlier u
                    for i in range(len(perm)):
                        for j in range(i + 1, len(perm)):
                            u, up = perm[i], perm[j]
                            if T[up][u]:
                                if not _try_add_arc(deg2, par2, up, u):
                                    ok = False
                                    break
                        if not ok:
                            break
                    if not ok:
                        continue
                    new_mask = placed_mask
                    for v in perm:
                        new_mask |= 1 << v
                    nkey = state_key(new_mask, deg2, par2)
                    if nkey not in new_frontier:
                        new_frontier[nkey] = (new_mask, deg2, par2)
        frontier = new_frontier
        max_states = max(max_states, len(frontier))
        if not frontier:
            decision = False
            if return_stats:
                return decision, {"max_states": max_states, "final_states": 0}
            return decision

    decision = any(mask == full for (mask, _, _) in frontier.values())
    if return_stats:
        return decision, {"max_states": max_states, "final_states": len(frontier)}
    return decision


def brute_lfo(T: Matrix) -> bool:
    return decide(T, "linear_forest")["found"]


def probe_n7(
    B: int,
    census_path: str,
    limit: int | None = None,
    use_uf: bool = True,
    use_deg: bool = True,
    track_states: bool = False,
) -> dict:
    with open(census_path, "r") as f:
        data = json.load(f)
    assert data["n"] == 7

    total = 0
    yes_true = 0
    no_true = 0
    band_yes = 0
    band_no = 0
    disagreements: list[dict] = []
    max_states_overall = 0

    for bucket in data["buckets"]:
        for rec in bucket["records"]:
            T = rec["T"]
            true = rec["has_lfo"]
            if track_states:
                pred, stats = band_dp_summary(
                    T, B, use_uf=use_uf, use_deg=use_deg, return_stats=True
                )
                max_states_overall = max(
                    max_states_overall, stats["max_states"]
                )
            else:
                pred = band_dp_summary(
                    T, B, use_uf=use_uf, use_deg=use_deg
                )
            total += 1
            yes_true += int(true)
            no_true += int(not true)
            band_yes += int(pred)
            band_no += int(not pred)
            if pred != true:
                disagreements.append({
                    "iso_index": rec["iso_index"],
                    "score": rec["score_sequence"],
                    "true": true,
                    "pred": pred,
                    "T": T,
                })
            if limit is not None and total >= limit:
                break
        if limit is not None and total >= limit:
            break

    return {
        "B": B,
        "n": 7,
        "use_uf": use_uf,
        "use_deg": use_deg,
        "total": total,
        "true_yes": yes_true,
        "true_no": no_true,
        "band_yes": band_yes,
        "band_no": band_no,
        "disagreements": disagreements[:50],
        "n_disagreements": len(disagreements),
        "max_states_overall": max_states_overall if track_states else None,
    }


def probe_random(
    B: int, ns: Sequence[int], samples: int, seed: int,
    use_uf: bool = True, use_deg: bool = True,
) -> dict:
    import random

    rng = random.Random(seed)
    out = {"B": B, "use_uf": use_uf, "use_deg": use_deg, "by_n": []}
    for n in ns:
        agree = 0
        disagree = 0
        diffs: list[dict] = []
        for _ in range(samples):
            T = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < 0.5:
                        T[i][j] = 1
                    else:
                        T[j][i] = 1
            pred = band_dp_summary(T, B, use_uf=use_uf, use_deg=use_deg)
            truth = brute_lfo(T)
            if pred == truth:
                agree += 1
            else:
                disagree += 1
                if len(diffs) < 5:
                    diffs.append({"T": T, "true": truth, "pred": pred})
        out["by_n"].append({
            "n": n,
            "samples": samples,
            "agree": agree,
            "disagree": disagree,
            "examples": diffs,
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--B", type=int, required=True, help="Band width")
    parser.add_argument(
        "--census", default="data/lfo_full_n7.json",
        help="Path to exact n=7 census",
    )
    parser.add_argument(
        "--random-ns", default="", help="Comma-separated list, e.g. 4,5,6"
    )
    parser.add_argument("--random-samples", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260527)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-uf", action="store_true",
                        help="Drop UF root summary (test deg-only key)")
    parser.add_argument("--no-deg", action="store_true",
                        help="Drop degree summary (test UF-only key)")
    parser.add_argument("--track-states", action="store_true")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    use_uf = not args.no_uf
    use_deg = not args.no_deg

    result: dict = {}

    if os.path.exists(args.census):
        result["n7_full"] = probe_n7(
            args.B, args.census, limit=args.limit,
            use_uf=use_uf, use_deg=use_deg, track_states=args.track_states,
        )
        r = result["n7_full"]
        msg = (
            f"[B={args.B} use_uf={use_uf} use_deg={use_deg}] "
            f"n=7 census ({r['total']} records): "
            f"true_yes={r['true_yes']} band_yes={r['band_yes']} "
            f"disagreements={r['n_disagreements']}"
        )
        if args.track_states:
            msg += f" max_states_overall={r['max_states_overall']}"
        print(msg)

    if args.random_ns:
        ns = [int(s) for s in args.random_ns.split(",")]
        result["random"] = probe_random(
            args.B, ns, args.random_samples, args.seed,
            use_uf=use_uf, use_deg=use_deg,
        )
        for row in result["random"]["by_n"]:
            print(
                f"[B={args.B}] n={row['n']} samples={row['samples']}: "
                f"agree={row['agree']} disagree={row['disagree']}"
            )

    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
