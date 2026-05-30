"""Dormant-Matching Quotient Lemma probe.

Background.  The refined width theorem (D66) gives
``pw(J), tw(J) <= 8 + 2|H|`` for the score-window interaction graph
``J = H ∪ G_flex``.  The forced-frontier probe (D67,
``forced_frontier_probe.py``) shows that the naive "two handles per live
H-component" frontier already gives ``7 + 2m`` on the reversed-matching
family on ``n = 2m`` vertices — no improvement on the
``8 + 2|H|`` theorem for general H.

The decisive next question is the **Dormant-Matching Quotient Lemma**
(``docs/forced_frontier_probe.md`` §4):

> In a score-window sweep where many disjoint forced edges are
> simultaneously dormant crossing components, their individual
> identities can be replaced by a polynomial-size aggregate without
> changing Path-FAS extendability.

This module makes the lemma's *aggregate signature* precise and searches
for two valid prefixes that share the aggregate but have different
extendability.  A collision refutes the lemma and seeds the next
hardness attempt; a no-collision result over a large search space is the
empirical complement to the theoretical proof attempt in
``docs/dormant_matching_quotient_lemma.md``.

Aggregate signature.  At sweep position ``p`` and a valid prefix
``sigma_prefix`` of length ``p``:

* an H-component is **dormant** iff
    (a) it does not intersect the active band ``A_p``, AND
    (b) every vertex in the component is unplaced (i.e. has not been
        consumed by the prefix), AND
    (c) it has at least one "closed" vertex (window ends before ``p``)
        and at least one "future" vertex (window starts after ``p``).

  In the reversed-matching family, every forced edge ``{i, i+m}`` is
  dormant for ``p`` in the middle of the sweep.

* the **profile** of a dormant component ``C`` is the triple
  ``(type, state, ports)`` where:
    - ``type`` is a canonical encoding of the H-component's shape
      (currently just its size, since H is a linear forest of
      matching edges or short paths);
    - ``state`` records, per vertex of ``C``, whether it is closed or
      future, plus its current H-degree;
    - ``ports`` records, per vertex of ``C``, the *set of positions in
      the active band* at which it could attach via a flex edge.

  Crucially, ``ports`` is recorded *positionally* in the active band
  rather than by global vertex id; this is what gives the aggregate a
  chance of being polynomial in ``n``.

* the **dormant aggregate** is the sorted multiset of profiles.

Augmented signature.  We pair the dormant aggregate with the standard
visible-latent signature on the active band + visible-prefix-ports
(see ``ff_signature_probe.visible_latent_signature``).  The lemma claims
this augmented signature is sufficient: two valid prefixes with equal
augmented signature have equal extendability.

If the lemma is false on the reversed-matching family, we exhibit a
minimal collision below ``m = 12`` (so ``n = 24``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Iterable, Sequence

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    has_completion_ff,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from forced_frontier_probe import (  # noqa: E402
    random_skew_tournament,
    reversed_matching_tournament,
)
from interaction_graph import build_H_and_Gflex  # noqa: E402


Matrix = Sequence[Sequence[int]]


# ---------------------------------------------------------------------------
# Dormant aggregate construction
# ---------------------------------------------------------------------------


def _h_components(T: Matrix, radius: int = 2) -> list[frozenset[int]]:
    """Return the connected components of the underlying graph of H."""
    H, _ = build_H_and_Gflex(T, radius)
    U = H.to_undirected()
    comps: list[frozenset[int]] = []
    for c in nx.connected_components(U):
        if any(U.degree(v) > 0 for v in c):
            comps.append(frozenset(c))
    return comps


def _component_type(component: frozenset[int], H_undirected: nx.Graph) -> tuple:
    """Canonical type of an H-component.

    For a linear forest, the type is determined by the multiset of
    degrees of its vertices.  A matching edge gives (1, 1); a path of
    length 2 gives (1, 2, 1); etc.

    We sort the degree sequence to make the type canonical (independent
    of vertex labelling).
    """
    degs = sorted(H_undirected.degree(v) for v in component)
    return tuple(degs)


def dormant_components_at(
    T: Matrix,
    pos: int,
    prefix: Sequence[int],
    radius: int = 2,
) -> list[dict] | None:
    """Return profiles of dormant H-components at sweep position ``pos``.

    A component is dormant iff
        * it has no vertex in the active band at ``pos``,
        * it has at least one closed vertex (window ended before ``pos``;
          this vertex *must* already be in the prefix, otherwise it can
          never be placed),
        * it has at least one future vertex (window starts after ``pos``;
          this vertex must NOT yet be in the prefix).

    The component therefore straddles the sweep: some endpoints have
    been forgotten, some have not yet been touched.  In particular,
    its forced backedges have been *loaded* in the DP state by the
    forced-edge preload (every H-edge is loaded by
    ``_initial_forced_state``).  What remains uncertain is how the
    future endpoints will be threaded into the upcoming flex choices.

    Each profile is a dict ``{"type", "vertices_state"}`` recording, per
    component vertex, ``(status, degree, ports)`` where ``ports`` is the
    set of *positions in the active band* the vertex could attach to via
    a flex edge.  We sort the per-vertex tuples so the profile is
    independent of the global labels.

    Returns ``None`` if the prefix is invalid.
    """
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return None
    prefix_mask, degree, parent, flex_outmask, windows = state
    n = len(T)
    if pos != len(prefix):
        raise ValueError("pos must equal len(prefix)")

    active = [v for v in range(n) if windows[v][0] <= pos <= windows[v][1]]
    active_set = set(active)
    closed = {v for v in range(n) if windows[v][1] < pos}
    future = {v for v in range(n) if windows[v][0] > pos}

    H, _ = build_H_and_Gflex(T, radius)
    U = H.to_undirected()
    comps = _h_components(T, radius)

    # Canonicalize port positions to indices in the sorted active list.
    active_sorted = sorted(active)
    active_index = {v: i for i, v in enumerate(active_sorted)}

    profiles: list[dict] = []
    for comp in comps:
        # Skip components that intersect the active band.
        if any(v in active_set for v in comp):
            continue
        has_closed = any(v in closed for v in comp)
        has_future = any(v in future for v in comp)
        if not (has_closed and has_future):
            continue
        # In a valid prefix, every closed vertex must already be placed
        # and every future vertex must not yet be placed.  We verify
        # rather than assume: an invalid prefix would have been rejected
        # by valid_prefix_state_ff above.
        # (Closed-vertex placedness is enforced by the window check.)

        ctype = _component_type(comp, U)
        per_vertex_records = []
        for v in comp:
            if v in closed:
                status = "closed"
            elif v in future:
                status = "future"
            else:
                status = "other"
            # Flex ports into the active band: symmetric over directions.
            ports_active = []
            for a in active_sorted:
                if (flex_outmask[v] >> a) & 1:
                    ports_active.append(active_index[a])
                elif (flex_outmask[a] >> v) & 1:
                    ports_active.append(active_index[a])
            ports_tuple = tuple(sorted(ports_active))
            per_vertex_records.append(
                (status, int(degree[v]), ports_tuple)
            )
        per_vertex_records.sort()
        profiles.append({
            "type": ctype,
            "vertices_state": tuple(per_vertex_records),
        })
    return profiles


def aggregate_signature(profiles: Sequence[dict]) -> tuple:
    """Return a canonical hashable signature of the dormant aggregate."""
    encoded = []
    for p in profiles:
        encoded.append((p["type"], p["vertices_state"]))
    # Sort to make the multiset canonical.
    encoded.sort()
    return tuple(encoded)


def augmented_signature(
    T: Matrix,
    prefix: Sequence[int],
    radius: int = 2,
) -> tuple | None:
    """Visible-latent signature + dormant aggregate at position ``len(prefix)``."""
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return None
    prefix_mask, degree, parent, flex_outmask, windows = state
    pos = len(prefix)
    vis = visible_latent_signature(
        pos, prefix_mask, degree, parent, flex_outmask, windows
    )
    profiles = dormant_components_at(T, pos, prefix, radius)
    if profiles is None:
        return None
    agg = aggregate_signature(profiles)
    return (vis, agg)


# ---------------------------------------------------------------------------
# Collision search
# ---------------------------------------------------------------------------


def _iter_valid_prefixes(
    T: Matrix,
    depth: int,
    only_length: int | None = None,
) -> Iterable[tuple[tuple[int, ...], tuple]]:
    """Yield (prefix, valid_prefix_state_ff(T, prefix)) for valid prefixes.

    If ``only_length`` is given, only prefixes of that length are yielded.
    Otherwise, prefixes of lengths 0..depth inclusive are yielded.

    Implementation: extend prefixes incrementally so invalid prefixes are
    not re-validated from scratch.  We rely on
    ``valid_prefix_state_ff`` for the final state, but prune invalid
    extensions on the fly via the windows check.
    """
    from lfo_score_window import score_windows  # local import to avoid cycle

    n = len(T)
    windows = score_windows(T, 2)
    if only_length is not None:
        ks = [only_length]
    else:
        ks = list(range(depth + 1))

    for k in ks:
        if k == 0:
            state = valid_prefix_state_ff(T, ())
            if state is not None:
                yield (), state
            continue
        # Use backtracking on length-k prefixes with cheap window
        # pruning (must place each v in its window).  Final validity is
        # confirmed by valid_prefix_state_ff.
        def rec(prefix: tuple, used: frozenset):
            pos = len(prefix)
            if pos == k:
                state = valid_prefix_state_ff(T, prefix)
                if state is not None:
                    yield prefix, state
                return
            for v in range(n):
                if v in used:
                    continue
                lo, hi = windows[v]
                if not (lo <= pos <= hi):
                    continue
                yield from rec(prefix + (v,), used | {v})

        yield from rec((), frozenset())


def find_collision(
    T: Matrix,
    depth: int = 6,
    radius: int = 2,
    track_extendability: bool = True,
    bucket_by_pos: bool = True,
    only_length: int | None = None,
    require_dormant: bool = False,
    max_prefixes: int | None = None,
) -> dict | None:
    """Search for two valid prefixes with the same augmented signature but
    different extendability.

    Returns a dict describing the collision or ``None`` if none found.

    Parameters
    ----------
    only_length : int or None
        Only consider prefixes of this exact length.  If given, ``depth``
        is ignored.
    require_dormant : bool
        If True, only consider prefixes that have at least one dormant
        component (otherwise the lemma is vacuous).
    max_prefixes : int or None
        Cap on the total prefix count to keep runtime bounded.
    """
    n = len(T)
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    checked = 0
    dormant_checked = 0

    for prefix, state in _iter_valid_prefixes(T, depth, only_length=only_length):
        prefix_mask, degree, parent, flex_outmask, windows = state
        pos = len(prefix)
        profiles = dormant_components_at(T, pos, prefix, radius)
        if require_dormant and not profiles:
            continue
        vis = visible_latent_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        agg = aggregate_signature(profiles)
        sig = (pos if bucket_by_pos else None, vis, agg)

        if track_extendability:
            ext = has_completion_ff(
                T, pos, prefix_mask, degree, parent,
                tuple(flex_outmask), tuple(windows),
            )
        else:
            ext = None

        checked += 1
        if profiles:
            dormant_checked += 1
        row = {
            "prefix": list(prefix),
            "pos": pos,
            "extendable": ext,
            "n_dormant": len(profiles),
        }
        for other in grouped[sig]:
            if track_extendability and other["extendable"] != ext:
                return {
                    "checked_valid_prefixes": checked,
                    "dormant_checked": dormant_checked,
                    "n": n,
                    "depth": depth,
                    "pos": pos,
                    "signature_class_size": len(grouped[sig]) + 1,
                    "state_a": other,
                    "state_b": row,
                    "dormant_profiles": profiles,
                    "T": [list(r) for r in T],
                }
        grouped[sig].append(row)
        if max_prefixes is not None and checked >= max_prefixes:
            break

    return None


def search_reversed_matching_family(
    m_range: Sequence[int],
    depth_fn=None,
    only_length_fn=None,
    require_dormant: bool = True,
    max_prefixes: int | None = None,
) -> list[dict]:
    """Search for collisions in the reversed-matching tournament family.

    For each ``m`` in ``m_range``:
        * if ``only_length_fn`` is given, only prefixes of that length
          are tested (typically a position in the dormant phase);
        * otherwise prefixes up to ``depth_fn(m)`` are tested.

    Default: ``only_length_fn(m) = m // 2 + 1`` (a position near the
    middle of the sweep, which is the dormant-rich regime).
    """
    if depth_fn is None:
        def depth_fn(m: int) -> int:
            return min(m, 6)
    if only_length_fn is None:
        def only_length_fn(m: int) -> int:
            # The dormant phase typically begins around p = 4 (gap is
            # [4, m-1]).  Use p = m // 2 + 1 to be safely inside it.
            return max(4, m // 2 + 1)
    out: list[dict] = []
    for m in m_range:
        T = reversed_matching_tournament(m)
        only_length = only_length_fn(m)
        depth = depth_fn(m)
        result = find_collision(
            T,
            depth=depth,
            only_length=only_length,
            require_dormant=require_dormant,
            max_prefixes=max_prefixes,
        )
        row = {
            "m": m,
            "n": 2 * m,
            "only_length": only_length,
            "depth": depth,
        }
        if result is None:
            row["collision"] = None
        else:
            row["collision"] = {
                "pos": result["pos"],
                "state_a": result["state_a"],
                "state_b": result["state_b"],
                "n_dormant": result["state_a"]["n_dormant"],
                "signature_class_size": result["signature_class_size"],
            }
        out.append(row)
    return out


def search_random_skew_family(
    n_range: Sequence[int],
    flips_fn=None,
    depth_fn=None,
    seeds: Sequence[int] = (20260527, 20260528, 20260529),
) -> list[dict]:
    """Search for collisions in the random-skew tournament family."""
    if flips_fn is None:
        def flips_fn(n: int) -> int:
            return max(1, n // 8)
    if depth_fn is None:
        def depth_fn(n: int) -> int:
            return min(n, 5)
    out: list[dict] = []
    for n in n_range:
        flips = flips_fn(n)
        depth = depth_fn(n)
        for seed in seeds:
            T = random_skew_tournament(n, flips, seed)
            result = find_collision(T, depth=depth)
            row = {
                "n": n,
                "flips": flips,
                "depth": depth,
                "seed": seed,
            }
            if result is None:
                row["collision"] = None
            else:
                row["collision"] = {
                    "pos": result["pos"],
                    "state_a": result["state_a"],
                    "state_b": result["state_b"],
                    "n_dormant": result["state_a"]["n_dormant"],
                    "signature_class_size": result["signature_class_size"],
                }
            out.append(row)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--T", help="Tournament as JSON matrix")
    src.add_argument(
        "--family",
        choices=["reversed_matching", "random_skew"],
        help="Search a built-in family.",
    )
    parser.add_argument(
        "--m-range", default="3,4,5,6,7,8,9,10",
        help="Comma-separated m values (reversed_matching).",
    )
    parser.add_argument(
        "--n-range", default="14,16,20,24",
        help="Comma-separated n values (random_skew).",
    )
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--seeds", default="20260527,20260528,20260529")
    args = parser.parse_args()

    if args.T:
        T = json.loads(args.T)
        result = find_collision(T, depth=args.depth)
        print(json.dumps(result, indent=2, default=list))
        return

    if args.family == "reversed_matching":
        ms = [int(x) for x in args.m_range.split(",") if x.strip()]
        rows = search_reversed_matching_family(
            ms, depth_fn=lambda m: args.depth,
        )
        print(json.dumps(rows, indent=2, default=list))
        return

    if args.family == "random_skew":
        ns = [int(x) for x in args.n_range.split(",") if x.strip()]
        seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
        rows = search_random_skew_family(
            ns,
            depth_fn=lambda n: args.depth,
            seeds=seeds,
        )
        print(json.dumps(rows, indent=2, default=list))


if __name__ == "__main__":
    main()
