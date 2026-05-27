"""Probe local exchange repairs for visible-latent suffix failures.

The visible-latent signature is not a bisimulation, and same-suffix
transfer is false. The remaining positive route is an exchange lemma:
if a suffix that completes one visible-equivalent state fails on another
because a vertex is placed after two already-connected past neighbors,
then a nearby reorder should repair the failed state.

This script searches for failures of same-suffix transfer and tests the
minimal repair used by the 10-vertex witness: move the first failing
vertex left in the suffix until the repaired suffix completes.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import defaultdict
from functools import lru_cache
from itertools import combinations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    _canonical_parent,
    _iter_census_records,
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
from score_window_forced import forced_order  # noqa: E402
from score_window_random_probe import (  # noqa: E402
    random_tournament,
    transitive_noise_tournament,
)
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]
State = tuple[int, tuple[int, ...], tuple[int, ...], list[int], list[tuple[int, int]]]


def _edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def suffix_is_valid(T: Matrix, state: State, suffix: Sequence[int]) -> bool:
    prefix_mask, degree, parent, flex_outmask, windows = state
    pos = prefix_mask.bit_count()
    for x in suffix:
        if prefix_mask & (1 << x):
            return False
        if not (windows[x][0] <= pos <= windows[x][1]):
            return False
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            return False
        degree, parent = nxt
        prefix_mask |= 1 << x
        pos += 1
    return prefix_mask == (1 << len(T)) - 1


def first_failure(T: Matrix, state: State, suffix: Sequence[int]) -> dict | None:
    prefix_mask, degree, parent, flex_outmask, windows = state
    pos = prefix_mask.bit_count()
    placed_suffix: list[int] = []
    for index, x in enumerate(suffix):
        if prefix_mask & (1 << x):
            return {"index": index, "vertex": x, "reason": "already_placed"}
        if not (windows[x][0] <= pos <= windows[x][1]):
            return {
                "index": index,
                "vertex": x,
                "reason": "window",
                "pos": pos,
                "window": windows[x],
                "placed_suffix": placed_suffix,
            }

        hits = list(_iter_bits(flex_outmask[x] & prefix_mask))
        par = list(parent)
        degree_blockers = []
        if degree[x] + len(hits) > 2:
            degree_blockers.append((x, degree[x], len(hits)))
        for h in hits:
            if degree[h] >= 2:
                degree_blockers.append((h, degree[h], 1))
        same_as_x = [h for h in hits if _find(par, x) == _find(par, h)]
        same_pairs = [
            (a, b)
            for a, b in combinations(hits, 2)
            if _find(par, a) == _find(par, b)
        ]

        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            if degree_blockers:
                reason = "degree"
            elif same_as_x or same_pairs:
                reason = "cycle"
            else:
                reason = "degree_or_cycle"
            return {
                "index": index,
                "vertex": x,
                "reason": reason,
                "pos": pos,
                "window": windows[x],
                "hits": hits,
                "placed_suffix": placed_suffix,
                "degree_blockers": degree_blockers,
                "same_as_x": same_as_x,
                "same_pairs": same_pairs,
            }
        degree, parent = nxt
        prefix_mask |= 1 << x
        placed_suffix.append(x)
        pos += 1
    return None


def one_completion(T: Matrix, state: State) -> tuple[int, ...] | None:
    n = len(T)
    all_mask = (1 << n) - 1
    prefix_mask, degree, parent, flex_outmask, windows = state

    @lru_cache(maxsize=None)
    def rec(
        pos: int,
        mask: int,
        deg: tuple[int, ...],
        par: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        if mask == all_mask:
            return ()
        remaining = all_mask ^ mask
        if not hall_interval_ok(remaining, pos, windows, n):
            return None
        ok, _reason = _forced_future_ok_flexible(
            flex_outmask, mask, remaining, deg, par
        )
        if not ok:
            return None
        candidates = [
            x for x in _iter_bits(remaining)
            if windows[x][0] <= pos <= windows[x][1]
        ]
        candidates.sort(
            key=lambda x: (
                (flex_outmask[x] & mask).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        for x in candidates:
            nxt = _add_flexible_vertex(flex_outmask, mask, deg, par, x)
            if nxt is None:
                continue
            nd, np = nxt
            tail = rec(pos + 1, mask | (1 << x), nd, _canonical_parent(np))
            if tail is not None:
                return (x,) + tail
        return None

    return rec(
        prefix_mask.bit_count(),
        prefix_mask,
        degree,
        _canonical_parent(parent),
    )


def completing_suffixes(
    T: Matrix,
    state: State,
    limit: int | None = None,
) -> list[tuple[int, ...]]:
    if limit == 1:
        suffix = one_completion(T, state)
        return [] if suffix is None else [suffix]

    n = len(T)
    all_mask = (1 << n) - 1
    prefix_mask, degree, parent, flex_outmask, windows = state
    out: list[tuple[int, ...]] = []

    def rec(
        pos: int,
        mask: int,
        deg: tuple[int, ...],
        par: tuple[int, ...],
        suffix: tuple[int, ...],
    ) -> None:
        if limit is not None and len(out) >= limit:
            return
        if mask == all_mask:
            out.append(suffix)
            return
        remaining = all_mask ^ mask
        if not hall_interval_ok(remaining, pos, windows, n):
            return
        ok, _reason = _forced_future_ok_flexible(
            flex_outmask, mask, remaining, deg, par
        )
        if not ok:
            return
        candidates = [
            x for x in _iter_bits(remaining)
            if windows[x][0] <= pos <= windows[x][1]
        ]
        candidates.sort(
            key=lambda x: (
                (flex_outmask[x] & mask).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        for x in candidates:
            nxt = _add_flexible_vertex(flex_outmask, mask, deg, par, x)
            if nxt is None:
                continue
            nd, np = nxt
            rec(pos + 1, mask | (1 << x), nd, _canonical_parent(np), suffix + (x,))

    rec(
        prefix_mask.bit_count(),
        prefix_mask,
        degree,
        _canonical_parent(parent),
        (),
    )
    return out


def single_left_move_repairs(
    T: Matrix,
    state: State,
    suffix: Sequence[int],
    failure_index: int,
) -> dict | None:
    x = suffix[failure_index]
    for target in range(failure_index - 1, -1, -1):
        repaired = (
            tuple(suffix[:target])
            + (x,)
            + tuple(suffix[target:failure_index])
            + tuple(suffix[failure_index + 1:])
        )
        if suffix_is_valid(T, state, repaired):
            return {
                "move_vertex": x,
                "from_index": failure_index,
                "to_index": target,
                "suffix": list(repaired),
            }
    return None


def single_right_move_repairs(
    T: Matrix,
    state: State,
    suffix: Sequence[int],
    failure_index: int,
) -> dict | None:
    """Try moving one earlier suffix vertex just after the failure.

    This is the block exchange suggested by the strict-progress
    counterexample: instead of moving the failing vertex left, delay one
    of the already placed vertices that participates in its hidden
    component.
    """
    for source in range(failure_index - 1, -1, -1):
        repaired = (
            tuple(suffix[:source])
            + tuple(suffix[source + 1:failure_index + 1])
            + (suffix[source],)
            + tuple(suffix[failure_index + 1:])
        )
        if suffix_is_valid(T, state, repaired):
            return {
                "move_vertex": suffix[source],
                "from_index": source,
                "to_index": failure_index,
                "suffix": list(repaired),
            }
    return None


def single_adjacent_internal_swap_repairs(
    T: Matrix,
    state: State,
    suffix: Sequence[int],
    failure_index: int,
) -> dict | None:
    """Try one adjacent swap strictly before the first failing vertex."""
    for left in range(failure_index - 1):
        repaired = list(suffix)
        repaired[left], repaired[left + 1] = repaired[left + 1], repaired[left]
        repaired_tuple = tuple(repaired)
        if suffix_is_valid(T, state, repaired_tuple):
            return {
                "left_index": left,
                "right_index": left + 1,
                "swap_vertices": [suffix[left], suffix[left + 1]],
                "suffix": list(repaired_tuple),
            }
    return None


def _move_left(suffix: Sequence[int], source: int, target: int) -> tuple[int, ...]:
    return (
        tuple(suffix[:target])
        + (suffix[source],)
        + tuple(suffix[target:source])
        + tuple(suffix[source + 1:])
    )


def _edge_load_steps(
    T: Matrix,
    windows: Sequence[tuple[int, int]],
    initial_prefix: Sequence[int],
    placed_suffix: Sequence[int],
) -> dict[tuple[int, int], int]:
    """Return current backedge load steps.

    Forced backedges and flexible backedges loaded before the analyzed
    suffix receive step -1. A flexible backedge loaded by suffix vertex
    x_s receives step s.
    """
    n = len(T)
    out: dict[tuple[int, int], int] = {}
    for u in range(n):
        for v in range(u + 1, n):
            fixed = forced_order(windows, u, v)
            if fixed is None:
                continue
            earlier, later = fixed
            if T[later][earlier]:
                out[(u, v)] = -1

    initial = tuple(initial_prefix)
    for later_index, later in enumerate(initial):
        earlier_vertices = initial[:later_index]
        for earlier in earlier_vertices:
            if forced_order(windows, later, earlier) is None and T[later][earlier]:
                out[_edge(later, earlier)] = -1

    current_prefix = list(initial)
    for step, later in enumerate(placed_suffix):
        for earlier in current_prefix:
            if forced_order(windows, later, earlier) is None and T[later][earlier]:
                out[_edge(later, earlier)] = step
        current_prefix.append(later)
    return out


def _path_edges(
    n: int,
    edge_steps: dict[tuple[int, int], int],
    source: int,
    target: int,
) -> list[tuple[int, int]] | None:
    adj: list[list[int]] = [[] for _ in range(n)]
    for a, b in edge_steps:
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    parent[source] = source
    stack = [source]
    while stack:
        v = stack.pop()
        if v == target:
            break
        for w in adj[v]:
            if parent[w] == -1:
                parent[w] = v
                stack.append(w)
    if parent[target] == -1:
        return None
    path = []
    v = target
    while v != source:
        p = parent[v]
        path.append(_edge(v, p))
        v = p
    path.reverse()
    return path


def _suffix_position_map(
    initial_prefix: Sequence[int],
    placed_suffix: Sequence[int],
) -> dict[int, int]:
    pos = {v: -1 for v in initial_prefix}
    for step, v in enumerate(placed_suffix):
        pos[v] = step
    return pos


def rho_diagnostics(
    T: Matrix,
    initial_prefix: Sequence[int],
    state: State,
    suffix: Sequence[int],
    failure: dict,
) -> list[dict]:
    if failure.get("reason") not in {"cycle", "degree_or_cycle"}:
        return []
    index = failure.get("index")
    if index is None:
        return []
    prefix_mask, _degree, _parent, _flex_outmask, windows = state
    del prefix_mask
    placed_suffix = tuple(suffix[:index])
    edge_steps = _edge_load_steps(T, windows, initial_prefix, placed_suffix)
    pi = _suffix_position_map(initial_prefix, placed_suffix)
    x = failure["vertex"]
    out = []
    query_pairs = list(failure.get("same_pairs", []))
    query_pairs.extend((x, h) for h in failure.get("same_as_x", []))
    for a, b in query_pairs:
        path = _path_edges(len(T), edge_steps, a, b)
        if path is None:
            out.append(
                {
                    "pair": [a, b],
                    "path_missing": True,
                    "rho": None,
                    "irreducible": False,
                }
            )
            continue
        beta = max((edge_steps[e] for e in path), default=-1)
        pi_a = index if a == x else pi.get(a)
        pi_b = index if b == x else pi.get(b)
        known_pi = [v for v in (pi_a, pi_b) if v is not None]
        rho = max([beta, *known_pi])
        out.append(
            {
                "pair": [a, b],
                "beta": beta,
                "pi": [pi_a, pi_b],
                "rho": rho,
                "failure_index": index,
                "irreducible": rho == index - 1,
                "path": [list(e) for e in path],
                "path_edge_steps": [
                    {"edge": list(e), "step": edge_steps[e]}
                    for e in path
                ],
            }
        )
    return out


def strict_progress_options(
    T: Matrix,
    state: State,
    suffix: Sequence[int],
    failure_index: int,
) -> list[dict]:
    out = []
    for target in range(failure_index - 1, -1, -1):
        candidate = _move_left(suffix, failure_index, target)
        if suffix_is_valid(T, state, candidate):
            out.append(
                {
                    "to_index": target,
                    "valid": True,
                    "strict_progress": True,
                    "failure_index": None,
                    "suffix": list(candidate),
                }
            )
            continue
        candidate_failure = first_failure(T, state, candidate)
        candidate_failure_index = (
            candidate_failure.get("index")
            if candidate_failure is not None
            else None
        )
        out.append(
            {
                "to_index": target,
                "valid": False,
                "strict_progress": (
                    candidate_failure_index is not None
                    and candidate_failure_index > failure_index
                ),
                "failure_index": candidate_failure_index,
                "failure_reason": (
                    candidate_failure.get("reason")
                    if candidate_failure is not None
                    else None
                ),
                "suffix": list(candidate),
            }
        )
    return out


def iterated_left_move_repair(
    T: Matrix,
    state: State,
    suffix: Sequence[int],
    max_steps: int | None = None,
) -> dict | None:
    """Try repeated first-failure left moves.

    This is deliberately conservative: each accepted move must strictly
    push the first failure later in the suffix. If the suffix is repaired
    in one move, this agrees with single_left_move_repairs.
    """
    current = tuple(suffix)
    if suffix_is_valid(T, state, current):
        return {"exchanges": 0, "suffix": list(current), "moves": []}

    if max_steps is None:
        max_steps = len(current) * len(current)
    moves = []
    seen = {current}
    for _step in range(max_steps):
        failure = first_failure(T, state, current)
        if failure is None or "index" not in failure:
            return None
        failure_index = failure["index"]
        best = None
        best_failure_index = failure_index
        for target in range(failure_index - 1, -1, -1):
            candidate = _move_left(current, failure_index, target)
            if candidate in seen:
                continue
            if suffix_is_valid(T, state, candidate):
                moves.append(
                    {
                        "move_vertex": current[failure_index],
                        "from_index": failure_index,
                        "to_index": target,
                    }
                )
                return {
                    "exchanges": len(moves),
                    "suffix": list(candidate),
                    "moves": moves,
                }
            candidate_failure = first_failure(T, state, candidate)
            if candidate_failure is None or "index" not in candidate_failure:
                continue
            candidate_failure_index = candidate_failure["index"]
            if candidate_failure_index > best_failure_index:
                best = (candidate, target)
                best_failure_index = candidate_failure_index
        if best is None:
            return None
        candidate, target = best
        moves.append(
            {
                "move_vertex": current[failure_index],
                "from_index": failure_index,
                "to_index": target,
            }
        )
        current = candidate
        seen.add(current)
    return None


def exchange_repair_stats(
    T: Matrix,
    depth: int = 5,
    completion_limit: int | None = None,
) -> dict:
    groups: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    valid_prefixes = 0
    pruned_prefixes = 0
    for prefix in prefixes(len(T), depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        valid_prefixes += 1
        if not survives_pruning(state, len(prefix), len(T)):
            continue
        pruned_prefixes += 1
        sig = visible_latent_signature(len(prefix), *state)
        groups[sig].append(tuple(prefix))

    duplicate_groups = [group for group in groups.values() if len(group) >= 2]
    stats = {
        "n": len(T),
        "depth": depth,
        "valid_prefixes": valid_prefixes,
        "pruned_prefixes": pruned_prefixes,
        "visible_classes": len(groups),
        "duplicate_visible_classes": len(duplicate_groups),
        "duplicate_prefixes": sum(len(group) for group in duplicate_groups),
        "source_completions": 0,
        "source_states_with_completion": 0,
        "source_states_completion_capped": 0,
        "transfer_checks": 0,
        "same_remaining_transfer_checks": 0,
        "different_remaining_transfer_checks": 0,
        "same_suffix_successes": 0,
        "same_suffix_failures": 0,
        "same_remaining_failures": 0,
        "one_exchange_repairs": 0,
        "right_move_repairs": 0,
        "adjacent_internal_swap_repairs": 0,
        "iterated_exchange_repairs": 0,
        "unrepaired_failures": 0,
        "max_single_move_distance": 0,
        "max_iterated_exchanges": 0,
        "failure_reasons": {},
        "rho_pair_counts": {},
        "irreducible_failures": 0,
        "strict_progress_failures": 0,
        "no_strict_progress_failures": 0,
        "first_same_suffix_failure": None,
        "first_irreducible_failure": None,
        "first_no_strict_progress_failure": None,
        "first_repair": None,
        "first_unrepaired": None,
    }

    for group in duplicate_groups:
        states = {prefix: valid_prefix_state_ff(T, prefix) for prefix in group}
        completions_by_prefix = {
            prefix: completing_suffixes(T, states[prefix], completion_limit)
            for prefix in group
        }
        target_one_completion = {
            prefix: (suffixes[0] if suffixes else None)
            for prefix, suffixes in completions_by_prefix.items()
        }
        for source, suffixes in completions_by_prefix.items():
            if not suffixes:
                continue
            stats["source_states_with_completion"] += 1
            stats["source_completions"] += len(suffixes)
            if completion_limit is not None and len(suffixes) >= completion_limit:
                stats["source_states_completion_capped"] += 1
            for suffix in suffixes:
                for target in group:
                    if target == source:
                        continue
                    target_state = states[target]
                    same_remaining = states[source][0] == target_state[0]
                    stats["transfer_checks"] += 1
                    if same_remaining:
                        stats["same_remaining_transfer_checks"] += 1
                    else:
                        stats["different_remaining_transfer_checks"] += 1
                    if suffix_is_valid(T, target_state, suffix):
                        stats["same_suffix_successes"] += 1
                        continue

                    stats["same_suffix_failures"] += 1
                    if same_remaining:
                        stats["same_remaining_failures"] += 1
                    failure = first_failure(T, target_state, suffix)
                    reason = (
                        "unknown"
                        if failure is None
                        else failure.get("reason", "unknown")
                    )
                    stats["failure_reasons"][reason] = (
                        stats["failure_reasons"].get(reason, 0) + 1
                    )
                    rho_info = rho_diagnostics(
                        T, target, target_state, suffix, failure
                    )
                    has_irreducible_pair = any(
                        item.get("irreducible") for item in rho_info
                    )
                    for item in rho_info:
                        if item.get("rho") is None:
                            bucket = "missing"
                        else:
                            delta = item["rho"] - failure["index"]
                            if delta <= -2:
                                bucket = "rho<=t-2"
                            elif delta == -1:
                                bucket = "rho=t-1"
                            elif delta == 0:
                                bucket = "rho=t"
                            else:
                                bucket = "rho>t"
                        stats["rho_pair_counts"][bucket] = (
                            stats["rho_pair_counts"].get(bucket, 0) + 1
                        )
                    progress_options = (
                        strict_progress_options(
                            T,
                            target_state,
                            suffix,
                            failure["index"],
                        )
                        if failure is not None and "index" in failure
                        else []
                    )
                    has_strict_progress = any(
                        option["strict_progress"] for option in progress_options
                    )
                    if has_strict_progress:
                        stats["strict_progress_failures"] += 1
                    else:
                        stats["no_strict_progress_failures"] += 1
                    if has_irreducible_pair:
                        stats["irreducible_failures"] += 1
                    if stats["first_same_suffix_failure"] is None:
                        stats["first_same_suffix_failure"] = {
                            "source_prefix": list(source),
                            "target_prefix": list(target),
                            "source_suffix": list(suffix),
                            "failure": failure,
                            "rho": rho_info,
                            "strict_progress_options": progress_options,
                        }
                    if (
                        has_irreducible_pair
                        and stats["first_irreducible_failure"] is None
                    ):
                        stats["first_irreducible_failure"] = {
                            "source_prefix": list(source),
                            "target_prefix": list(target),
                            "source_suffix": list(suffix),
                            "failure": failure,
                            "rho": rho_info,
                            "strict_progress_options": progress_options,
                            "T": [list(row) for row in T],
                        }
                    if (
                        not has_strict_progress
                        and stats["first_no_strict_progress_failure"] is None
                    ):
                        stats["first_no_strict_progress_failure"] = {
                            "source_prefix": list(source),
                            "target_prefix": list(target),
                            "source_suffix": list(suffix),
                            "failure": failure,
                            "rho": rho_info,
                            "strict_progress_options": progress_options,
                            "T": [list(row) for row in T],
                        }

                    repair = (
                        single_left_move_repairs(
                            T, target_state, suffix, failure["index"]
                        )
                        if failure is not None and "index" in failure
                        else None
                    )
                    if repair is not None:
                        stats["one_exchange_repairs"] += 1
                        distance = repair["from_index"] - repair["to_index"]
                        stats["max_single_move_distance"] = max(
                            stats["max_single_move_distance"],
                            distance,
                        )
                        if stats["first_repair"] is None:
                            stats["first_repair"] = {
                                "source_prefix": list(source),
                                "target_prefix": list(target),
                                "source_suffix": list(suffix),
                                "repair": repair,
                        }
                        continue

                    right_repair = (
                        single_right_move_repairs(
                            T, target_state, suffix, failure["index"]
                        )
                        if failure is not None and "index" in failure
                        else None
                    )
                    if right_repair is not None:
                        stats["right_move_repairs"] += 1
                        if stats["first_repair"] is None:
                            stats["first_repair"] = {
                                "source_prefix": list(source),
                                "target_prefix": list(target),
                                "source_suffix": list(suffix),
                                "right_repair": right_repair,
                            }
                        continue

                    adjacent_repair = (
                        single_adjacent_internal_swap_repairs(
                            T, target_state, suffix, failure["index"]
                        )
                        if failure is not None and "index" in failure
                        else None
                    )
                    if adjacent_repair is not None:
                        stats["adjacent_internal_swap_repairs"] += 1
                        if stats["first_repair"] is None:
                            stats["first_repair"] = {
                                "source_prefix": list(source),
                                "target_prefix": list(target),
                                "source_suffix": list(suffix),
                                "adjacent_repair": adjacent_repair,
                            }
                        continue

                    iterated = iterated_left_move_repair(T, target_state, suffix)
                    if iterated is not None:
                        stats["iterated_exchange_repairs"] += 1
                        stats["max_iterated_exchanges"] = max(
                            stats["max_iterated_exchanges"],
                            iterated["exchanges"],
                        )
                        continue

                    stats["unrepaired_failures"] += 1
                    if stats["first_unrepaired"] is None:
                        target_completion = target_one_completion[target]
                        stats["first_unrepaired"] = {
                            "source_prefix": list(source),
                            "target_prefix": list(target),
                            "source_suffix": list(suffix),
                            "failure": failure,
                            "rho": rho_info,
                            "strict_progress_options": progress_options,
                            "target_extendable": target_completion is not None,
                            "target_completion": (
                                list(target_completion)
                                if target_completion is not None
                                else None
                            ),
                            "T": [list(row) for row in T],
                        }
    return stats


def find_exchange_obstruction(T: Matrix, depth: int = 5) -> dict | None:
    stats = exchange_repair_stats(T, depth, completion_limit=1)
    return stats["first_unrepaired"]


def census_exchange_repair_stats(
    path: str,
    depth: int = 5,
    limit: int | None = None,
    completion_limit: int | None = None,
) -> dict:
    aggregate = {
        "path": path,
        "depth": depth,
        "checked": 0,
        "stopped_on_obstruction": False,
        "obstruction_location": None,
        "totals": {
            "valid_prefixes": 0,
            "pruned_prefixes": 0,
            "visible_classes": 0,
            "duplicate_visible_classes": 0,
            "duplicate_prefixes": 0,
            "source_completions": 0,
            "source_states_with_completion": 0,
            "source_states_completion_capped": 0,
            "transfer_checks": 0,
            "same_remaining_transfer_checks": 0,
            "different_remaining_transfer_checks": 0,
            "same_suffix_successes": 0,
            "same_suffix_failures": 0,
            "same_remaining_failures": 0,
            "one_exchange_repairs": 0,
            "right_move_repairs": 0,
            "adjacent_internal_swap_repairs": 0,
            "iterated_exchange_repairs": 0,
            "unrepaired_failures": 0,
            "irreducible_failures": 0,
            "strict_progress_failures": 0,
            "no_strict_progress_failures": 0,
        },
        "max_single_move_distance": 0,
        "max_iterated_exchanges": 0,
        "failure_reasons": {},
        "rho_pair_counts": {},
        "first_same_suffix_failure": None,
        "first_irreducible_failure": None,
        "first_no_strict_progress_failure": None,
        "first_repair": None,
        "first_unrepaired": None,
    }
    total_keys = set(aggregate["totals"])
    for bucket_index, record_index, T in _iter_census_records(path):
        if limit is not None and aggregate["checked"] >= limit:
            break
        stats = exchange_repair_stats(T, depth, completion_limit)
        aggregate["checked"] += 1
        for key in total_keys:
            aggregate["totals"][key] += stats[key]
        aggregate["max_single_move_distance"] = max(
            aggregate["max_single_move_distance"],
            stats["max_single_move_distance"],
        )
        aggregate["max_iterated_exchanges"] = max(
            aggregate["max_iterated_exchanges"],
            stats["max_iterated_exchanges"],
        )
        for reason, count in stats["failure_reasons"].items():
            aggregate["failure_reasons"][reason] = (
                aggregate["failure_reasons"].get(reason, 0) + count
            )
        for bucket, count in stats["rho_pair_counts"].items():
            aggregate["rho_pair_counts"][bucket] = (
                aggregate["rho_pair_counts"].get(bucket, 0) + count
            )
        if (
            aggregate["first_same_suffix_failure"] is None
            and stats["first_same_suffix_failure"] is not None
        ):
            aggregate["first_same_suffix_failure"] = {
                "bucket_index": bucket_index,
                "record_index": record_index,
                "witness": stats["first_same_suffix_failure"],
            }
        if (
            aggregate["first_irreducible_failure"] is None
            and stats["first_irreducible_failure"] is not None
        ):
            aggregate["first_irreducible_failure"] = {
                "bucket_index": bucket_index,
                "record_index": record_index,
                "witness": stats["first_irreducible_failure"],
            }
        if (
            aggregate["first_no_strict_progress_failure"] is None
            and stats["first_no_strict_progress_failure"] is not None
        ):
            aggregate["first_no_strict_progress_failure"] = {
                "bucket_index": bucket_index,
                "record_index": record_index,
                "witness": stats["first_no_strict_progress_failure"],
            }
        if aggregate["first_repair"] is None and stats["first_repair"] is not None:
            aggregate["first_repair"] = {
                "bucket_index": bucket_index,
                "record_index": record_index,
                "witness": stats["first_repair"],
            }
        if stats["first_unrepaired"] is not None:
            aggregate["stopped_on_obstruction"] = True
            aggregate["obstruction_location"] = {
                "bucket_index": bucket_index,
                "record_index": record_index,
            }
            aggregate["first_unrepaired"] = stats["first_unrepaired"]
            break
    return aggregate


def run_random(
    mode: str,
    ns: list[int],
    ps: list[float],
    samples: int,
    depth: int,
    seed: int,
) -> dict:
    rng = random.Random(seed)
    groups = []
    for n in ns:
        probs = ps if mode == "skew" else [0.0]
        for p in probs:
            group = {
                "mode": mode,
                "n": n,
                "p": p if mode == "skew" else None,
                "samples": 0,
                "obstruction": None,
            }
            for sample in range(samples):
                T = (
                    transitive_noise_tournament(n, p, rng)
                    if mode == "skew"
                    else random_tournament(n, rng)
                )
                obstruction = find_exchange_obstruction(T, depth)
                group["samples"] += 1
                if obstruction is not None:
                    group["obstruction"] = {
                        "sample": sample,
                        "witness": obstruction,
                    }
                    groups.append(group)
                    return {
                        "seed": seed,
                        "depth": depth,
                        "groups": groups,
                        "stopped_on_obstruction": True,
                    }
            groups.append(group)
    return {
        "seed": seed,
        "depth": depth,
        "groups": groups,
        "stopped_on_obstruction": False,
    }


def _empty_totals() -> dict:
    return {
        "valid_prefixes": 0,
        "pruned_prefixes": 0,
        "visible_classes": 0,
        "duplicate_visible_classes": 0,
        "duplicate_prefixes": 0,
        "source_completions": 0,
        "source_states_with_completion": 0,
        "source_states_completion_capped": 0,
        "transfer_checks": 0,
        "same_remaining_transfer_checks": 0,
        "different_remaining_transfer_checks": 0,
        "same_suffix_successes": 0,
        "same_suffix_failures": 0,
        "same_remaining_failures": 0,
        "one_exchange_repairs": 0,
        "right_move_repairs": 0,
        "adjacent_internal_swap_repairs": 0,
        "iterated_exchange_repairs": 0,
        "unrepaired_failures": 0,
        "irreducible_failures": 0,
        "strict_progress_failures": 0,
        "no_strict_progress_failures": 0,
    }


def _merge_stats(group: dict, stats: dict) -> None:
    for key in group["totals"]:
        group["totals"][key] += stats[key]
    group["max_single_move_distance"] = max(
        group["max_single_move_distance"],
        stats["max_single_move_distance"],
    )
    group["max_iterated_exchanges"] = max(
        group["max_iterated_exchanges"],
        stats["max_iterated_exchanges"],
    )
    for reason, count in stats["failure_reasons"].items():
        group["failure_reasons"][reason] = (
            group["failure_reasons"].get(reason, 0) + count
        )
    for bucket, count in stats["rho_pair_counts"].items():
        group["rho_pair_counts"][bucket] = (
            group["rho_pair_counts"].get(bucket, 0) + count
        )
    for key in [
        "first_same_suffix_failure",
        "first_irreducible_failure",
        "first_no_strict_progress_failure",
        "first_repair",
        "first_unrepaired",
    ]:
        if group[key] is None and stats[key] is not None:
            group[key] = stats[key]


def run_random_stats(
    mode: str,
    ns: list[int],
    ps: list[float],
    samples: int,
    depth: int,
    seed: int,
    completion_limit: int | None,
) -> dict:
    rng = random.Random(seed)
    groups = []
    for n in ns:
        probs = ps if mode == "skew" else [0.0]
        for p in probs:
            group = {
                "mode": mode,
                "n": n,
                "p": p if mode == "skew" else None,
                "samples": 0,
                "totals": _empty_totals(),
                "max_single_move_distance": 0,
                "max_iterated_exchanges": 0,
                "failure_reasons": {},
                "rho_pair_counts": {},
                "first_same_suffix_failure": None,
                "first_irreducible_failure": None,
                "first_no_strict_progress_failure": None,
                "first_repair": None,
                "first_unrepaired": None,
            }
            for _sample in range(samples):
                T = (
                    transitive_noise_tournament(n, p, rng)
                    if mode == "skew"
                    else random_tournament(n, rng)
                )
                stats = exchange_repair_stats(T, depth, completion_limit)
                group["samples"] += 1
                _merge_stats(group, stats)
                if stats["first_unrepaired"] is not None:
                    break
            groups.append(group)
    return {
        "seed": seed,
        "depth": depth,
        "completion_limit": completion_limit,
        "groups": groups,
    }


def parse_ints(raw: str) -> list[int]:
    return [int(x) for x in raw.split(",") if x]


def parse_floats(raw: str) -> list[float]:
    return [float(x) for x in raw.split(",") if x]


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--T", help="Tournament as JSON matrix")
    source.add_argument("--census", help="Census JSON file with records or buckets")
    source.add_argument("--random", choices=["uniform", "skew"])
    parser.add_argument("--ns", default="10,12")
    parser.add_argument("--ps", default="0.02,0.05,0.1")
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260529)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--completion-limit", type=int)
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    if args.T is not None:
        T = json.loads(args.T)
        out = (
            exchange_repair_stats(T, args.depth, args.completion_limit)
            if args.stats
            else find_exchange_obstruction(T, args.depth)
        )
    elif args.census is not None:
        out = census_exchange_repair_stats(
            args.census,
            args.depth,
            args.limit,
            args.completion_limit,
        )
    elif args.stats:
        out = run_random_stats(
            args.random,
            parse_ints(args.ns),
            parse_floats(args.ps),
            args.samples,
            args.depth,
            args.seed,
            args.completion_limit,
        )
    else:
        out = run_random(
            args.random,
            parse_ints(args.ns),
            parse_floats(args.ps),
            args.samples,
            args.depth,
            args.seed,
        )
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
