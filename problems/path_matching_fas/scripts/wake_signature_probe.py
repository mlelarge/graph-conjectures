"""Wake-horizon signatures for the forced/flexible DP attempt.

Visible-latent tracks the current active window and old prefix ports
that can be hit by currently active unplaced vertices. A one-step
failure mode is that a future-opening vertex enters the active band at
the next cut while already connected, through forced edges, to a
dormant component invisible at the current cut.

The horizon-h wake signature augments visible-latent by also tracking
future-opening vertices whose windows begin within h steps, together
with the old prefix ports they can already hit by flexible backedges.
For h=1 this is the minimal "wake next cut" repair.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Callable, Iterable, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    _iter_census_records,
    has_completion_ff,
    prefixes,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from lfo_forced_flexible import (  # noqa: E402
    _find,
    _forced_future_ok_flexible,
    _iter_bits,
)
from lfo_score_window import hall_interval_ok  # noqa: E402
from sleeping_block_probe import sleeping_block_signature  # noqa: E402


Matrix = Sequence[Sequence[int]]
State = tuple[int, tuple[int, ...], tuple[int, ...], list[int], list[tuple[int, int]]]
SignatureFn = Callable[[int, int, Sequence[int], Sequence[int], Sequence[int], Sequence[tuple[int, int]]], tuple]


BASE_WAKE_FAILURE_WITNESS: list[list[int]] = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
]

WAKE_FAILURE_PREFIX_A = (0, 1, 3, 2, 4)
WAKE_FAILURE_PREFIX_B = (2, 0, 3, 1, 4)


def _insert_transitive_padding_vertex(T: Matrix, before: int) -> list[list[int]]:
    """Insert one vertex at index `before`, oriented by index order.

    This raises the indegree, hence the score window, of every vertex at
    or after `before` by exactly one while preserving the old subtournament.
    In the wake-failure witness it delays the distinguishing dormant
    vertex by one cut.
    """
    n = len(T)
    out = [[0] * (n + 1) for _ in range(n + 1)]

    def old_to_new(v: int) -> int:
        return v if v < before else v + 1

    for u in range(n):
        for v in range(n):
            out[old_to_new(u)][old_to_new(v)] = T[u][v]

    for v in range(n + 1):
        if v == before:
            continue
        if v < before:
            out[v][before] = 1
        else:
            out[before][v] = 1
    return out


def padded_wake_failure_witness(horizon: int) -> dict:
    """Return a witness showing wake horizon `horizon` is not a bisimulation.

    For horizon h, insert h-1 transitive padding vertices immediately
    before the dormant delayed vertex. The two pinned prefixes still
    survive pruning and have the same horizon-h signature, but their
    horizon-h child transition profiles differ. Horizon h+1 separates
    this particular pair.
    """
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    T: Matrix = BASE_WAKE_FAILURE_WITNESS
    before = 11
    for _ in range(horizon - 1):
        T = _insert_transitive_padding_vertex(T, before)
        before += 1
    return {
        "horizon": horizon,
        "T": [list(row) for row in T],
        "prefix_a": WAKE_FAILURE_PREFIX_A,
        "prefix_b": WAKE_FAILURE_PREFIX_B,
        "delayed_vertex": 11 + horizon - 1,
    }


def _active_set(pos: int, windows: Sequence[tuple[int, int]]) -> set[int]:
    return {v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi}


def _visible_old_ports(
    pos: int,
    prefix_mask: int,
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
) -> set[int]:
    active = _active_set(pos, windows)
    unplaced_active = [v for v in active if not (prefix_mask & (1 << v))]
    out: set[int] = set()
    for x in unplaced_active:
        for p in _iter_bits(flex_outmask[x] & prefix_mask):
            if p not in active:
                out.add(p)
    return out


def wake_signature(
    pos: int,
    prefix_mask: int,
    degree: Sequence[int],
    parent: Sequence[int],
    flex_outmask: Sequence[int],
    windows: Sequence[tuple[int, int]],
    horizon: int = 1,
) -> tuple:
    """Visible-latent plus future-opening vertices within `horizon`.

    For horizon 1, the extra vertices are exactly those not yet active
    at cut `pos` but active at cut `pos + 1`.
    """
    base = visible_latent_signature(
        pos, prefix_mask, degree, parent, flex_outmask, windows
    )
    n = len(parent)
    active = _active_set(pos, windows)
    visible_old = _visible_old_ports(pos, prefix_mask, flex_outmask, windows)
    wake = {
        v for v, (lo, _hi) in enumerate(windows)
        if not (prefix_mask & (1 << v)) and pos < lo <= pos + horizon
    }

    wake_old: set[int] = set()
    for y in wake:
        for p in _iter_bits(flex_outmask[y] & prefix_mask):
            if p not in active:
                wake_old.add(p)

    relevant = active | visible_old | wake | wake_old
    ordered_relevant = tuple(sorted(relevant))
    par = list(parent)
    root_labels: dict[int, int] = {}

    def root_label(v: int) -> int:
        root = _find(par, v)
        if root not in root_labels:
            root_labels[root] = len(root_labels)
        return root_labels[root]

    def tag(v: int):
        if v in active:
            return ("active", v)
        if v in wake:
            lo, _hi = windows[v]
            return ("wake", v, lo - pos)
        return ("old",)

    wake_partition = tuple(
        (tag(v), degree[v], root_label(v))
        for v in ordered_relevant
    )
    port_index = {v: i for i, v in enumerate(ordered_relevant)}
    wake_neighbor_interface = tuple(
        (
            y,
            tuple(
                (
                    port_index[p],
                    degree[p],
                    root_label(p),
                    tag(p),
                )
                for p in _iter_bits(flex_outmask[y] & prefix_mask)
            ),
        )
        for y in sorted(wake)
    )
    return base + (
        ("wake_horizon", horizon),
        wake_partition,
        wake_neighbor_interface,
    )


def signature_function(kind: str, horizon: int = 1) -> SignatureFn:
    if kind == "visible":
        return visible_latent_signature
    if kind == "sleeping":
        return sleeping_block_signature
    if kind == "wake":
        return lambda pos, pm, deg, par, flex, win: wake_signature(
            pos, pm, deg, par, flex, win, horizon
        )
    raise ValueError("kind must be visible, wake, or sleeping")


def survives_pruning(state: State, pos: int, n: int) -> bool:
    prefix_mask, degree, parent, flex_outmask, windows = state
    remaining = ((1 << n) - 1) ^ prefix_mask
    if not hall_interval_ok(remaining, pos, windows, n):
        return False
    ok, _reason = _forced_future_ok_flexible(
        flex_outmask,
        prefix_mask,
        remaining,
        degree,
        parent,
    )
    return ok


def child_signature_or_dead(
    T: Matrix,
    state: State,
    x: int,
    sigfun: SignatureFn,
) -> tuple:
    prefix_mask, degree, parent, flex_outmask, windows = state
    pos = prefix_mask.bit_count()
    nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
    if nxt is None:
        return ("DEAD", "degree_or_cycle")
    child_degree, child_parent = nxt
    child_mask = prefix_mask | (1 << x)
    child_pos = pos + 1
    child_state = (child_mask, child_degree, child_parent, flex_outmask, windows)
    if not survives_pruning(child_state, child_pos, len(T)):
        return ("DEAD", "future_prune")
    return sigfun(
        child_pos,
        child_mask,
        child_degree,
        child_parent,
        flex_outmask,
        windows,
    )


def transition_profile(
    T: Matrix,
    prefix: Sequence[int],
    sigfun: SignatureFn,
    pruned: bool = True,
) -> tuple | None:
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return None
    pos = len(prefix)
    n = len(T)
    if pruned and not survives_pruning(state, pos, n):
        return None
    prefix_mask, _degree, _parent, _flex_outmask, windows = state
    remaining = ((1 << n) - 1) ^ prefix_mask
    out = []
    for x in _iter_bits(remaining):
        if windows[x][0] <= pos <= windows[x][1]:
            out.append((x, child_signature_or_dead(T, state, x, sigfun)))
    return tuple(sorted(out, key=lambda row: (row[0], repr(row[1]))))


def find_one_step_mismatch(
    T: Matrix,
    depth: int = 5,
    kind: str = "wake",
    horizon: int = 1,
    pruned: bool = True,
) -> dict | None:
    sigfun = signature_function(kind, horizon)
    groups: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    checked = 0
    for prefix in prefixes(len(T), depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if pruned and not survives_pruning(state, pos, len(T)):
            continue
        checked += 1
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = sigfun(pos, prefix_mask, degree, parent, flex_outmask, windows)
        groups[sig].append(tuple(prefix))

    for sig, group in groups.items():
        if len(group) < 2:
            continue
        base_prefix = group[0]
        base_profile = transition_profile(T, base_prefix, sigfun, pruned)
        if base_profile is None:
            continue
        for prefix in group[1:]:
            profile = transition_profile(T, prefix, sigfun, pruned)
            if profile != base_profile:
                return {
                    "n": len(T),
                    "depth": depth,
                    "kind": kind,
                    "horizon": horizon,
                    "pruned": pruned,
                    "checked_surviving_prefixes": checked,
                    "signature_class_size": len(group),
                    "state_a": {
                        "prefix": list(base_prefix),
                        "transition_count": len(base_profile),
                    },
                    "state_b": {
                        "prefix": list(prefix),
                        "transition_count": len(profile),
                    },
                    "T": [list(row) for row in T],
                }
    return None


def find_census_one_step_mismatch(
    path: str,
    depth: int = 5,
    kind: str = "wake",
    horizon: int = 1,
    pruned: bool = True,
    limit: int | None = None,
) -> dict:
    checked = 0
    for bucket_index, record_index, T in _iter_census_records(path):
        if limit is not None and checked >= limit:
            break
        checked += 1
        mismatch = find_one_step_mismatch(T, depth, kind, horizon, pruned)
        if mismatch is not None:
            return {
                "checked": checked,
                "mismatch": True,
                "bucket_index": bucket_index,
                "record_index": record_index,
                "witness": mismatch,
            }
    return {
        "checked": checked,
        "mismatch": False,
    }


def find_extendability_collision(
    T: Matrix,
    depth: int = 5,
    kind: str = "wake",
    horizon: int = 1,
    pruned: bool = True,
) -> dict | None:
    sigfun = signature_function(kind, horizon)
    groups: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    checked = 0
    for prefix in prefixes(len(T), depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if pruned and not survives_pruning(state, pos, len(T)):
            continue
        checked += 1
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = sigfun(pos, prefix_mask, degree, parent, flex_outmask, windows)
        groups[sig].append(tuple(prefix))

    completion_cache: dict[tuple[int, ...], bool] = {}

    def completion(prefix: tuple[int, ...]) -> bool:
        if prefix in completion_cache:
            return completion_cache[prefix]
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            raise RuntimeError("grouped prefix became invalid")
        pos = len(prefix)
        prefix_mask, degree, parent, flex_outmask, windows = state
        ext = has_completion_ff(
            T,
            pos,
            prefix_mask,
            degree,
            parent,
            tuple(flex_outmask),
            tuple(windows),
        )
        completion_cache[prefix] = ext
        return ext

    for _sig, group in groups.items():
        if len(group) < 2:
            continue
        base_prefix = group[0]
        base_ext = completion(base_prefix)
        base_row = {
            "prefix": list(base_prefix),
            "extendable": base_ext,
        }
        for prefix in group[1:]:
            ext = completion(prefix)
            if ext != base_ext:
                return {
                    "n": len(T),
                    "depth": depth,
                    "kind": kind,
                    "horizon": horizon,
                    "pruned": pruned,
                    "checked_surviving_prefixes": checked,
                    "checked_completion_prefixes": len(completion_cache),
                    "signature_class_size": len(group),
                    "state_a": base_row,
                    "state_b": {
                        "prefix": list(prefix),
                        "extendable": ext,
                    },
                    "T": [list(r) for r in T],
                }
    return None


def find_census_extendability_collision(
    path: str,
    depth: int = 5,
    kind: str = "wake",
    horizon: int = 1,
    pruned: bool = True,
    limit: int | None = None,
) -> dict:
    checked = 0
    for bucket_index, record_index, T in _iter_census_records(path):
        if limit is not None and checked >= limit:
            break
        checked += 1
        collision = find_extendability_collision(T, depth, kind, horizon, pruned)
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
    source.add_argument("--T", help="Tournament as JSON matrix")
    source.add_argument("--census", help="Census JSON path")
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--kind", choices=["visible", "wake", "sleeping"], default="wake")
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--unpruned", action="store_true")
    parser.add_argument(
        "--check",
        choices=["one-step", "extendability"],
        default="one-step",
    )
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    pruned = not args.unpruned
    if args.census is not None:
        if args.check == "one-step":
            out = find_census_one_step_mismatch(
                args.census,
                args.depth,
                args.kind,
                args.horizon,
                pruned,
                args.limit,
            )
        else:
            out = find_census_extendability_collision(
                args.census,
                args.depth,
                args.kind,
                args.horizon,
                pruned,
                args.limit,
            )
    else:
        T = json.loads(args.T)
        if args.check == "one-step":
            out = find_one_step_mismatch(T, args.depth, args.kind, args.horizon, pruned)
        else:
            out = find_extendability_collision(T, args.depth, args.kind, args.horizon, pruned)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
