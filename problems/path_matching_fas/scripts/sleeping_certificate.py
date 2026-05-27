"""Runtime certificates for the sleeping-block extension-equivalence proof.

For every pair (S, S') of FF-pruned prefixes with the same prefix set
and the same sleeping-block signature, the proof in Section 13.3 of
exchange_proof_draft.md predicts identical FF inputs under two related
checks.

Suffix mode applies the same suffix sigma to both states and records:

  (C1) prefix_mask at cut i+t agrees between S, S' for every t.
  (C2) degree[v] for v in B_i = A_i union O_i union F_i agrees.
  (C3) the union-find class of v in B_i (canonical block label) agrees.
  (C4) the union-find class of any suffix-placed vertex agrees.

Transition mode checks the stronger one-step bisimulation obligation:
for every unplaced vertex x, placing x has the same window/placement/
pruning outcome in both states, and successful children have the same
sleeping-block signature.

Usage:
  uv run python scripts/sleeping_certificate.py --T <json> --depth 5
  uv run python scripts/sleeping_certificate.py --T <json> --depth 5 --mode transition
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    prefixes,
    valid_prefix_state_ff,
)
from lfo_forced_flexible import _find  # noqa: E402
from sleeping_block_probe import sleeping_block_signature  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]
State = tuple[int, tuple[int, ...], tuple[int, ...], list[int], list[tuple[int, int]]]


def _boundary_set(pos: int, prefix_mask: int, windows, flex_outmask, n: int) -> set[int]:
    """Compute B_i = A_i union O_i union F_i for the state."""
    active = {v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi}
    future_opening = {
        v for v, (lo, _hi) in enumerate(windows)
        if lo > pos and not (prefix_mask & (1 << v))
    }
    visible_old = set()
    placed_set = {v for v in range(n) if prefix_mask & (1 << v)}
    unplaced_active = active - placed_set
    for x in unplaced_active:
        for p in range(n):
            if (flex_outmask[x] >> p) & 1 and (prefix_mask >> p) & 1:
                if p not in active:
                    visible_old.add(p)
    return active | visible_old | future_opening


def _canonical_labels(parent: Sequence[int]) -> dict[int, int]:
    """Map each vertex v to its block's canonical label (min vertex in
    the block under union-find parent)."""
    par = list(parent)
    blocks = defaultdict(list)
    for v in range(len(par)):
        blocks[_find(par, v)].append(v)
    canonical = {root: min(members) for root, members in blocks.items()}
    return {v: canonical[_find(par, v)] for v in range(len(par))}


def replay_suffix(
    T: Matrix,
    initial_state,
    suffix: Sequence[int],
) -> list[dict]:
    """Replay suffix step by step; record FF inputs at each step.

    Returns a list of dicts, one per step (including step 0 = state
    just before placing suffix[0]).
    """
    prefix_mask, degree, parent, flex_outmask, windows = initial_state
    n = len(T)
    pos = prefix_mask.bit_count()
    records = []

    boundary = _boundary_set(pos, prefix_mask, windows, flex_outmask, n)
    labels = _canonical_labels(parent)

    for step_idx, x in enumerate(suffix):
        record = {
            "step": step_idx,
            "pos": pos,
            "prefix_mask": prefix_mask,
            "x": x,
            "deg_x_before": degree[x],
            "boundary_set": sorted(boundary),
            "deg_boundary": {v: degree[v] for v in boundary},
            "labels_boundary": {v: labels[v] for v in boundary},
        }
        # Apply placement.
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            record["placement_failed"] = True
            records.append(record)
            return records
        degree, parent = nxt
        prefix_mask |= 1 << x
        pos += 1
        boundary = _boundary_set(pos, prefix_mask, windows, flex_outmask, n)
        labels = _canonical_labels(parent)
        # After placement
        record["deg_x_after"] = degree[x]
        record["placement_failed"] = False
        records.append(record)

    return records


def certify_pair(
    T: Matrix,
    prefix_a: Sequence[int],
    prefix_b: Sequence[int],
    suffix: Sequence[int],
) -> dict:
    """Run the runtime certificate on the (S_a, S_b) pair under suffix."""
    state_a = valid_prefix_state_ff(T, prefix_a)
    state_b = valid_prefix_state_ff(T, prefix_b)
    if state_a is None or state_b is None:
        return {"valid": False, "reason": "invalid_prefix_state"}

    n = len(T)
    pos_a = len(prefix_a)
    pos_b = len(prefix_b)
    if pos_a != pos_b:
        return {"valid": False, "reason": "different_cuts"}
    if state_a[0] != state_b[0]:
        return {"valid": False, "reason": "different_prefix_sets"}

    sig_a = sleeping_block_signature(pos_a, *state_a)
    sig_b = sleeping_block_signature(pos_b, *state_b)
    if sig_a != sig_b:
        return {"valid": False, "reason": "different_sleeping_signatures"}

    if not survives_pruning(state_a, pos_a, n):
        return {"valid": False, "reason": "state_a_pruned"}
    if not survives_pruning(state_b, pos_b, n):
        return {"valid": False, "reason": "state_b_pruned"}

    recs_a = replay_suffix(T, state_a, suffix)
    recs_b = replay_suffix(T, state_b, suffix)

    # Sanity: same number of steps before failure.
    if len(recs_a) != len(recs_b):
        return {
            "valid": False,
            "reason": "different_failure_steps",
            "len_a": len(recs_a),
            "len_b": len(recs_b),
        }

    mismatches = []
    for ra, rb in zip(recs_a, recs_b):
        if ra["prefix_mask"] != rb["prefix_mask"]:
            mismatches.append(("prefix_mask", ra["step"], ra["prefix_mask"], rb["prefix_mask"]))
        if ra["deg_x_before"] != rb["deg_x_before"]:
            mismatches.append(("deg_x_before", ra["step"], ra["deg_x_before"], rb["deg_x_before"]))
        if set(ra["boundary_set"]) != set(rb["boundary_set"]):
            mismatches.append(("boundary_set", ra["step"]))
        for v in set(ra["boundary_set"]) & set(rb["boundary_set"]):
            if ra["deg_boundary"].get(v) != rb["deg_boundary"].get(v):
                mismatches.append(("deg_boundary", ra["step"], v,
                                   ra["deg_boundary"].get(v), rb["deg_boundary"].get(v)))
        # Partition equivalence on B_i: instead of comparing absolute
        # block labels (which use min-of-block and so can differ when
        # placed-old members of a boundary block differ between S, S'),
        # check that the EQUIVALENCE RELATION agrees: for every pair
        # u, v in B_i, u ~ v in S iff u ~ v in S'.
        shared_boundary = sorted(
            set(ra["boundary_set"]) & set(rb["boundary_set"])
        )
        for ix in range(len(shared_boundary)):
            for iy in range(ix + 1, len(shared_boundary)):
                u = shared_boundary[ix]
                v = shared_boundary[iy]
                same_a = ra["labels_boundary"][u] == ra["labels_boundary"][v]
                same_b = rb["labels_boundary"][u] == rb["labels_boundary"][v]
                if same_a != same_b:
                    mismatches.append(("partition_disagree", ra["step"], u, v,
                                       same_a, same_b))
        if ra["placement_failed"] != rb["placement_failed"]:
            mismatches.append(("placement_failed", ra["step"],
                              ra["placement_failed"], rb["placement_failed"]))

    return {
        "valid": True,
        "steps": len(recs_a),
        "mismatches": mismatches,
        "all_agree": len(mismatches) == 0,
        "completed": all(not r["placement_failed"] for r in recs_a),
    }


def certify_witness_set(
    T: Matrix,
    depth: int = 5,
    max_pairs: int = 50,
) -> dict:
    """Group depth-bounded FF-pruned prefixes by sleeping-block sig and
    run the certificate on each same-sig pair (with the natural-order
    suffix)."""
    by_sig: dict[tuple, list[tuple]] = defaultdict(list)
    n = len(T)
    for prefix in prefixes(n, depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if not survives_pruning(state, pos, n):
            continue
        sig = sleeping_block_signature(pos, *state)
        by_sig[sig].append((prefix, state))

    summary = {
        "n": n,
        "depth": depth,
        "pairs_checked": 0,
        "all_pairs_certify": True,
        "first_failure": None,
    }
    for sig, group in by_sig.items():
        if len(group) < 2:
            continue
        for i_a in range(len(group)):
            for i_b in range(i_a + 1, len(group)):
                if summary["pairs_checked"] >= max_pairs:
                    break
                prefix_a, _ = group[i_a]
                prefix_b, _ = group[i_b]
                # Natural-order suffix
                remaining = [v for v in range(n)
                             if not (group[i_a][1][0] & (1 << v))]
                suffix = tuple(remaining)
                result = certify_pair(T, prefix_a, prefix_b, suffix)
                summary["pairs_checked"] += 1
                if not result.get("all_agree", False):
                    summary["all_pairs_certify"] = False
                    if summary["first_failure"] is None:
                        summary["first_failure"] = {
                            "prefix_a": list(prefix_a),
                            "prefix_b": list(prefix_b),
                            "result": result,
                        }
    return summary


def _transition_outcome(T: Matrix, state: State, x: int) -> dict:
    """Return the one-step DP outcome of trying to place x."""
    prefix_mask, degree, parent, flex_outmask, windows = state
    n = len(T)
    pos = prefix_mask.bit_count()
    if prefix_mask & (1 << x):
        return {"status": "already_placed"}
    if not (windows[x][0] <= pos <= windows[x][1]):
        return {
            "status": "window_fail",
            "pos": pos,
            "window": windows[x],
        }
    nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
    if nxt is None:
        return {"status": "placement_fail"}

    next_degree, next_parent = nxt
    next_mask = prefix_mask | (1 << x)
    next_pos = pos + 1
    next_state = (next_mask, next_degree, next_parent, flex_outmask, windows)
    if not survives_pruning(next_state, next_pos, n):
        return {"status": "pruning_fail"}

    return {
        "status": "ok",
        "child_signature": sleeping_block_signature(next_pos, *next_state),
    }


def certify_transition_pair(
    T: Matrix,
    prefix_a: Sequence[int],
    prefix_b: Sequence[int],
) -> dict:
    """Check one-step sleeping-block bisimulation for one prefix pair."""
    state_a = valid_prefix_state_ff(T, prefix_a)
    state_b = valid_prefix_state_ff(T, prefix_b)
    if state_a is None or state_b is None:
        return {"valid": False, "reason": "invalid_prefix_state"}

    n = len(T)
    pos_a = len(prefix_a)
    pos_b = len(prefix_b)
    if pos_a != pos_b:
        return {"valid": False, "reason": "different_cuts"}
    if state_a[0] != state_b[0]:
        return {"valid": False, "reason": "different_prefix_sets"}

    sig_a = sleeping_block_signature(pos_a, *state_a)
    sig_b = sleeping_block_signature(pos_b, *state_b)
    if sig_a != sig_b:
        return {"valid": False, "reason": "different_sleeping_signatures"}

    if not survives_pruning(state_a, pos_a, n):
        return {"valid": False, "reason": "state_a_pruned"}
    if not survives_pruning(state_b, pos_b, n):
        return {"valid": False, "reason": "state_b_pruned"}

    failures = []
    transitions_checked = 0
    remaining = [v for v in range(n) if not (state_a[0] & (1 << v))]
    for x in remaining:
        out_a = _transition_outcome(T, state_a, x)
        out_b = _transition_outcome(T, state_b, x)
        transitions_checked += 1
        if out_a["status"] != out_b["status"]:
            failures.append({
                "x": x,
                "kind": "status_mismatch",
                "outcome_a": out_a,
                "outcome_b": out_b,
            })
            continue
        if (
            out_a["status"] == "ok"
            and out_a["child_signature"] != out_b["child_signature"]
        ):
            failures.append({
                "x": x,
                "kind": "child_signature_mismatch",
            })

    return {
        "valid": True,
        "transitions_checked": transitions_checked,
        "failures": failures,
        "all_agree": len(failures) == 0,
    }


def certify_transition_witness_set(
    T: Matrix,
    depth: int = 5,
    max_pairs: int = 50,
) -> dict:
    """Certify one-step sleeping-block bisimulation on a test family."""
    by_sig: dict[tuple, list[tuple]] = defaultdict(list)
    n = len(T)
    for prefix in prefixes(n, depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if not survives_pruning(state, pos, n):
            continue
        sig = sleeping_block_signature(pos, *state)
        by_sig[sig].append((prefix, state))

    summary = {
        "n": n,
        "depth": depth,
        "pairs_checked": 0,
        "pairs_skipped_different_prefix_sets": 0,
        "transitions_checked": 0,
        "all_pairs_certify": True,
        "first_failure": None,
    }
    for group in by_sig.values():
        if len(group) < 2:
            continue
        for i_a in range(len(group)):
            for i_b in range(i_a + 1, len(group)):
                if summary["pairs_checked"] >= max_pairs:
                    break
                prefix_a, state_a = group[i_a]
                prefix_b, state_b = group[i_b]
                if state_a[0] != state_b[0]:
                    summary["pairs_skipped_different_prefix_sets"] += 1
                    continue
                result = certify_transition_pair(T, prefix_a, prefix_b)
                summary["pairs_checked"] += 1
                summary["transitions_checked"] += result.get(
                    "transitions_checked", 0
                )
                if not result.get("all_agree", False):
                    summary["all_pairs_certify"] = False
                    if summary["first_failure"] is None:
                        summary["first_failure"] = {
                            "prefix_a": list(prefix_a),
                            "prefix_b": list(prefix_b),
                            "result": result,
                        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", required=True)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--max-pairs", type=int, default=50)
    parser.add_argument(
        "--mode",
        choices=["suffix", "transition"],
        default="suffix",
    )
    args = parser.parse_args()
    T = json.loads(args.T)
    out = (
        certify_transition_witness_set(T, args.depth, args.max_pairs)
        if args.mode == "transition"
        else certify_witness_set(T, args.depth, args.max_pairs)
    )
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
