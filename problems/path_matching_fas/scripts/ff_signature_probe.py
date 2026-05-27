"""Probe active-bag signatures for the forced/flexible DP attempt.

The natural interval-bag DP state after forced/flexible normalization is:

    (position,
     active-window vertices already placed,
     degrees of active-window vertices,
     component partition restricted to active-window vertices).

This script searches for two valid prefixes with the same such signature
but different extendability. Such a collision would refute the naive
bag-local DP. It also tests a stronger visible-latent signature that
keeps the bounded old-prefix ports still reachable by future flexible
backedges. Absence of collisions is not a proof, but it is the right
finite test before writing the formal DP.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from functools import lru_cache
from itertools import permutations
from typing import Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_forced_flexible import (  # noqa: E402
    _find,
    _forced_future_ok_flexible,
    _initial_forced_state,
    _iter_bits,
    _union,
)
from lfo_score_window import hall_interval_ok, score_windows  # noqa: E402


Matrix = Sequence[Sequence[int]]


def _canonical_parent(parent: Sequence[int]) -> tuple[int, ...]:
    par = list(parent)
    blocks: dict[int, list[int]] = defaultdict(list)
    for v in range(len(parent)):
        blocks[_find(par, v)].append(v)
    out = [0] * len(parent)
    for block in blocks.values():
        rep = min(block)
        for v in block:
            out[v] = rep
    return tuple(out)


def _add_flexible_vertex(
    flex_outmask: Sequence[int],
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    x: int,
) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
    deg = list(degree)
    par = list(parent)
    for p in _iter_bits(flex_outmask[x] & prefix_mask):
        if deg[x] >= 2 or deg[p] >= 2:
            return None
        if _find(par, x) == _find(par, p):
            return None
        deg[x] += 1
        deg[p] += 1
        _union(par, x, p)
    return tuple(deg), tuple(par)


def prefixes(n: int, depth: int) -> Iterable[tuple[int, ...]]:
    for k in range(depth + 1):
        yield from permutations(range(n), k)


def valid_prefix_state_ff(
    T: Matrix,
    prefix: Sequence[int],
) -> tuple[int, tuple[int, ...], tuple[int, ...], list[int], list[tuple[int, int]]] | None:
    windows = score_windows(T)
    if not hall_interval_ok((1 << len(T)) - 1, 0, windows, len(T)):
        return None
    degree, parent, flex_outmask, obstruction = _initial_forced_state(T, windows)
    if obstruction is not None:
        return None
    prefix_mask = 0
    for pos, x in enumerate(prefix):
        lo, hi = windows[x]
        if not (lo <= pos <= hi):
            return None
        if prefix_mask & (1 << x):
            return None
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            return None
        degree, parent = nxt
        prefix_mask |= 1 << x
    return prefix_mask, degree, parent, flex_outmask, windows


def has_completion_ff(
    T: Matrix,
    pos: int,
    prefix_mask: int,
    degree: tuple[int, ...],
    parent: tuple[int, ...],
    flex_outmask: tuple[int, ...],
    windows: tuple[tuple[int, int], ...],
) -> bool:
    n = len(T)
    all_mask = (1 << n) - 1

    @lru_cache(maxsize=None)
    def rec(
        at: int,
        prefix: int,
        deg: tuple[int, ...],
        par_sig: tuple[int, ...],
    ) -> bool:
        if prefix == all_mask:
            return True
        remaining = all_mask ^ prefix
        if not hall_interval_ok(remaining, at, windows, n):
            return False
        ok, _ = _forced_future_ok_flexible(
            flex_outmask,
            prefix,
            remaining,
            deg,
            par_sig,
        )
        if not ok:
            return False
        candidates = [
            v for v in _iter_bits(remaining)
            if windows[v][0] <= at <= windows[v][1]
        ]
        candidates.sort(
            key=lambda x: (
                (flex_outmask[x] & prefix).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        for x in candidates:
            nxt = _add_flexible_vertex(flex_outmask, prefix, deg, par_sig, x)
            if nxt is None:
                continue
            nd, np = nxt
            if rec(at + 1, prefix | (1 << x), nd, _canonical_parent(np)):
                return True
        return False

    return rec(pos, prefix_mask, degree, _canonical_parent(parent))


def active_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> tuple:
    active = tuple(v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi)
    placed_active = tuple(v for v in active if prefix_mask & (1 << v))
    active_degrees = tuple((v, degree[v]) for v in active)
    par = list(parent)
    labels: dict[int, int] = {}
    partition = []
    for v in active:
        root = _find(par, v)
        if root not in labels:
            labels[root] = len(labels)
        partition.append((v, labels[root]))
    return (
        pos,
        active,
        placed_active,
        active_degrees,
        tuple(partition),
    )


def visible_latent_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> tuple:
    """Return active bag plus bounded latent prefix interface.

    The latent interface consists of forgotten prefix vertices that are
    adjacent by a flexible backedge to some unplaced active vertex. These
    are precisely the forgotten vertices that can affect the next few
    choices before they disappear behind forced edges. The component
    partition is recorded on all active vertices plus these old ports:
    unplaced active vertices can already be connected to old vertices by
    forced backedges, and that relation is needed for future cycle tests.
    """
    active = tuple(v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi)
    active_set = set(active)
    placed_active = tuple(v for v in active if prefix_mask & (1 << v))
    unplaced_active = tuple(v for v in active if not (prefix_mask & (1 << v)))
    active_degrees = tuple((v, degree[v]) for v in active)

    visible_prefix: set[int] = set(active)
    active_neighbor_map: list[tuple[int, tuple[int, ...]]] = []
    for x in unplaced_active:
        neigh = tuple(sorted(_iter_bits(flex_outmask[x] & prefix_mask)))
        active_neighbor_map.append((x, neigh))
        visible_prefix.update(neigh)

    visible = tuple(sorted(visible_prefix))
    par = list(parent)
    root_labels: dict[int, int] = {}
    visible_partition = []
    for v in visible:
        root = _find(par, v)
        if root not in root_labels:
            root_labels[root] = len(root_labels)
        visible_partition.append((
            v if v in active_set else "old",
            degree[v],
            root_labels[root],
        ))

    # For active unplaced vertices, record which visible ports they will
    # hit if placed now. Old vertex identities are deliberately abstracted
    # to their visible-port index; active vertex identities are retained.
    port_index = {v: i for i, v in enumerate(visible)}
    neighbor_interface = tuple(
        (
            x,
            tuple(
                (
                    port_index[p],
                    degree[p],
                    root_labels[_find(par, p)],
                    p if p in active_set else "old",
                )
                for p in neigh
            ),
        )
        for x, neigh in active_neighbor_map
    )

    return (
        pos,
        active,
        placed_active,
        active_degrees,
        tuple(visible_partition),
        neighbor_interface,
    )


def _row_from_signature(
    prefix: Sequence[int],
    prefix_mask: int,
    ext: bool,
    sig: tuple,
) -> dict:
    return {
        "prefix": list(prefix),
        "prefix_mask": prefix_mask,
        "extendable": ext,
        "active": list(sig[1]),
        "placed_active": list(sig[2]),
    }


def find_signature_collision(T: Matrix, depth: int = 5, mode: str = "active") -> dict | None:
    if mode not in {"active", "visible"}:
        raise ValueError("mode must be 'active' or 'visible'")
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    checked = 0
    for prefix in prefixes(len(T), depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        checked += 1
        prefix_mask, degree, parent, flex_outmask, windows = state
        pos = len(prefix)
        if mode == "active":
            sig = active_signature(pos, prefix_mask, degree, parent, windows)
        else:
            sig = visible_latent_signature(
                pos,
                prefix_mask,
                degree,
                parent,
                flex_outmask,
                windows,
            )
        ext = has_completion_ff(
            T,
            pos,
            prefix_mask,
            degree,
            parent,
            tuple(flex_outmask),
            tuple(windows),
        )
        row = _row_from_signature(prefix, prefix_mask, ext, sig)
        for other in grouped[sig]:
            if other["extendable"] != row["extendable"]:
                return {
                    "n": len(T),
                    "depth": depth,
                    "mode": mode,
                    "checked_valid_prefixes": checked,
                    "signature": {
                        "pos": sig[0],
                        "active": list(sig[1]),
                        "placed_active": list(sig[2]),
                        "active_degrees": [list(x) for x in sig[3]],
                        "extra": json.loads(json.dumps(sig[4:], default=str)),
                    },
                    "state_a": other,
                    "state_b": row,
                    "T": [list(r) for r in T],
                }
        grouped[sig].append(row)
    return None


def find_active_signature_collision(T: Matrix, depth: int = 5) -> dict | None:
    return find_signature_collision(T, depth, "active")


def find_visible_signature_collision(T: Matrix, depth: int = 5) -> dict | None:
    return find_signature_collision(T, depth, "visible")


def _iter_census_records(path: str) -> Iterable[tuple[int, int, Matrix]]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    if "buckets" in data:
        for bucket_index, bucket in enumerate(data["buckets"]):
            for record_index, record in enumerate(bucket["records"]):
                yield bucket_index, record_index, record["T"]
        return

    for record_index, record in enumerate(data.get("records", [])):
        yield 0, record_index, record["T"]


def find_census_signature_collision(path: str, depth: int = 5, mode: str = "active") -> dict:
    checked = 0
    for bucket_index, record_index, T in _iter_census_records(path):
        checked += 1
        collision = find_signature_collision(T, depth, mode)
        if collision is not None:
            return {
                "checked": checked,
                "collision": True,
                "bucket_index": bucket_index,
                "record_index": record_index,
                "witness": collision,
            }
    return {
        "checked": checked,
        "collision": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--T", help="Tournament as a JSON matrix")
    source.add_argument("--census", help="Census JSON file with records or buckets")
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--mode", choices=["active", "visible"], default="active")
    args = parser.parse_args()
    if args.T is not None:
        out = find_signature_collision(json.loads(args.T), args.depth, args.mode)
    else:
        out = find_census_signature_collision(args.census, args.depth, args.mode)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
