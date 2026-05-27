"""Runtime certificate for A''-aux-1 (Hidden-Connection Exclusion).

Given a state (S', sigma) where sigma first fails on S' at step t via
cycle, and given a failing pair (p1, p2) in the cycle, A''-aux-1 says
that beta_{p1,p2} >= L_1 = max(0, l_{x_t} - i).

The proof (Section 9.9 of exchange_proof_draft.md) constructs a
contradiction at cut j = i + beta + 1 if beta < L_1: it shows that the
forced-future cycle check at cut j fails for x_t.

This module:
  - given a tournament T and a suffix sigma that first fails on S' at
    step t with cycle failure, computes the failing pair (a, b), the
    path Q in G^{S'}(P_t), and beta = beta_{a,b};
  - verifies that beta >= L_1 (the A''-aux-1 conclusion);
  - if beta < L_1, produces the cut j = i + beta + 1 at which the
    forced-future cycle check fails, as the runtime certificate.

The verification is run on every cycle-failure witness in the
exchange-repair test set.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict, deque
from itertools import combinations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exchange_repair_probe import first_failure  # noqa: E402
from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    valid_prefix_state_ff,
)
from lfo_forced_flexible import (  # noqa: E402
    _find,
    _forced_future_ok_flexible,
    _iter_bits,
    _union,
)
from lfo_score_window import score_windows  # noqa: E402


Matrix = Sequence[Sequence[int]]


def _bfs_path(adj: dict[int, list[int]], src: int, dst: int) -> list[int] | None:
    if src == dst:
        return [src]
    parent = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v in parent:
                continue
            parent[v] = u
            if v == dst:
                # reconstruct
                path = [v]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                path.reverse()
                return path
            q.append(v)
    return None


def _replay_with_history(
    T: Matrix,
    initial_state,
    suffix: Sequence[int],
    stop_at_step: int,
) -> tuple[list, dict[tuple[int, int], int]]:
    """Replay suffix from initial_state for `stop_at_step` steps; record at
    which step each (undirected) flexible backedge was loaded.

    Returns (states_per_cut, edge_step_map).
    """
    prefix_mask, degree, parent, flex_outmask, windows = initial_state
    pos = prefix_mask.bit_count()
    states = [(prefix_mask, degree, parent)]
    edge_step: dict[tuple[int, int], int] = {}
    for step, x in enumerate(suffix[:stop_at_step]):
        # Identify which flexible backedges will be added by this placement.
        for p in _iter_bits(flex_outmask[x] & prefix_mask):
            edge = (min(x, p), max(x, p))
            edge_step.setdefault(edge, step)
        nxt = _add_flexible_vertex(flex_outmask, prefix_mask, degree, parent, x)
        if nxt is None:
            # Shouldn't happen if first_failure already confirmed steps succeed.
            break
        degree, parent = nxt
        prefix_mask |= 1 << x
        pos += 1
        states.append((prefix_mask, degree, parent))
    return states, edge_step


def _build_full_edge_set(
    T: Matrix,
    final_prefix_mask: int,
    final_parent: Sequence[int],
    initial_state,
    edge_step: dict[tuple[int, int], int],
) -> dict[int, list[int]]:
    """Build adjacency for current back-arc graph at the failing cut.

    We reconstruct by combining initial forced + chosen flex (initial state)
    plus all loaded flex backedges from the replay.
    """
    n = len(T)
    initial_prefix_mask, initial_degree, initial_parent, flex_outmask, windows = initial_state
    adj: dict[int, list[int]] = defaultdict(list)

    # Initial: add edges between vertices in same union-find class.
    # We can't easily extract edges from a union-find, but we can extract
    # them from T's forced backedges + flex_outmask intersected with the
    # initial prefix_mask. For our certificate we don't actually need the
    # full initial edge set — only the path in the back-arc graph at the
    # failing cut. Use union-find traversal as a fallback: two vertices
    # are connected iff same union-find class. We build a tree by adding
    # one edge per merge.

    # Simpler: reconstruct edges by:
    #  (a) forced backedges from T (windows disjoint, T-arc late->early).
    #  (b) flex backedges from edge_step (loaded during the replay).
    #  (c) any flex backedge already loaded in the *initial* state — these
    #      came from cuts before i; we don't have their identity but they
    #      contribute to initial_parent. Approximate by adding edges from
    #      the union-find: for each connected pair (u, v) with u<v that
    #      we can't already explain, add a synthetic edge.

    # For the A''-aux-1 certificate, we only need to find the path in the
    # back-arc graph. The edges in the path are loaded at known steps if
    # they came from the suffix; if they came from the initial state we
    # just need to know they're "initial" (step = -1).

    # Strategy: add forced backedges + suffix flex backedges. Verify
    # union-find at the failing cut matches; if not, augment with
    # additional initial-pre-edges.

    # Forced backedges
    forced_pairs = set()
    for u in range(n):
        lo_u, hi_u = windows[u]
        for v in range(u + 1, n):
            lo_v, hi_v = windows[v]
            if hi_u < lo_v and T[v][u] == 1:
                forced_pairs.add((u, v))
                adj[v].append(u)
                adj[u].append(v)
            elif hi_v < lo_u and T[u][v] == 1:
                forced_pairs.add((u, v))
                adj[u].append(v)
                adj[v].append(u)

    # Suffix-loaded flex backedges
    for (u, v), _step in edge_step.items():
        adj[u].append(v)
        adj[v].append(u)

    # Initial-pre-cut flex backedges: extract from initial parent.
    # For each pair (u, v) in same initial union-find class but not yet
    # connected in adj, find a spanning tree edge.
    # Simplification: build union-find from current adj, then add edges to
    # match initial_parent's class structure.
    par_check = list(range(n))
    for u in range(n):
        for v in adj[u]:
            if u < v:
                _union(par_check, u, v)

    initial_par = list(initial_parent)
    initial_classes: dict[int, list[int]] = defaultdict(list)
    for v in range(n):
        initial_classes[_find(initial_par, v)].append(v)

    for cls in initial_classes.values():
        if len(cls) <= 1:
            continue
        cls = sorted(cls)
        # Add edges to ensure all members are in one component of adj.
        for v in cls[1:]:
            if _find(par_check, cls[0]) != _find(par_check, v):
                adj[cls[0]].append(v)
                adj[v].append(cls[0])
                _union(par_check, cls[0], v)
    return adj


def certify_aux1(
    T: Matrix,
    initial_state,
    suffix: Sequence[int],
) -> dict:
    """Run the A''-aux-1 certificate.

    Returns a dict:
      - failed_at: int (step t of suffix where cycle failure occurs), or None
      - cycle_pair: (a, b)
      - beta: int (latest contributing step on Q)
      - L1: int
      - aux1_holds: bool (True iff beta >= L1)
      - prune_witness: dict (at cut j = i + beta + 1, the forced-future
        cycle check fails for x_t) — present when aux1_holds is False
    """
    n = len(T)
    failure = first_failure(T, initial_state, suffix)
    if failure is None:
        return {"failed_at": None, "result": "suffix completes"}
    if failure.get("reason") != "cycle":
        return {
            "failed_at": failure["index"],
            "result": "non-cycle first failure",
            "reason": failure["reason"],
        }
    t = failure["index"]
    x_t = failure["vertex"]
    # Use any failing pair (a, b).
    same_pairs = failure["same_pairs"]
    if not same_pairs:
        return {"failed_at": t, "result": "cycle without explicit pair"}
    (a, b) = same_pairs[0]

    initial_prefix_mask, initial_degree, initial_parent, flex_outmask, windows = initial_state
    i = initial_prefix_mask.bit_count()
    L_1 = max(0, windows[x_t][0] - i)

    # Replay the suffix for t steps; record edge step map.
    states, edge_step = _replay_with_history(T, initial_state, suffix, t)

    # Build adjacency of back-arc graph at cut i + t.
    final_prefix_mask, final_degree, final_parent = states[-1]
    adj = _build_full_edge_set(T, final_prefix_mask, final_parent, initial_state, edge_step)

    # Find path Q from a to b.
    Q = _bfs_path(adj, a, b)
    if Q is None:
        return {"failed_at": t, "result": "no a-b path found"}

    # Compute beta = max step in edge_step among edges of Q.
    beta = -1
    for u, v in zip(Q, Q[1:]):
        e = (min(u, v), max(u, v))
        if e in edge_step:
            beta = max(beta, edge_step[e])

    out = {
        "failed_at": t,
        "x_t": x_t,
        "cycle_pair": [a, b],
        "Q": Q,
        "beta": beta,
        "L1": L_1,
        "aux1_holds": beta >= L_1,
    }

    if not out["aux1_holds"]:
        # Certificate: at cut j = i + beta + 1 in S', the forced-future
        # cycle check fails for x_t.
        j_step = beta + 1
        prefix_mask_j = states[j_step][0]
        degree_j = states[j_step][1]
        parent_j = states[j_step][2]
        remaining_mask = ((1 << n) - 1) ^ prefix_mask_j
        ok, reason = _forced_future_ok_flexible(
            flex_outmask, prefix_mask_j, remaining_mask, degree_j, parent_j,
        )
        out["prune_witness"] = {
            "cut": i + j_step,
            "pruning_passes": ok,
            "reason": reason,
        }
    return out


def certify_witness_set(T: Matrix, depth: int = 5) -> dict:
    """Run aux1 certificate over all visible-equivalent prefix pairs at
    depth in T."""
    from ff_signature_probe import prefixes, visible_latent_signature
    by_sig: dict[tuple, list[tuple]] = defaultdict(list)
    for prefix in prefixes(len(T), depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pm, deg, par, flx, win = state
        sig = visible_latent_signature(len(prefix), pm, deg, par, flx, win)
        by_sig[sig].append((prefix, state))

    results = {
        "pairs_checked": 0,
        "cycle_failures": 0,
        "aux1_violations": 0,
        "examples": [],
    }
    for sig, group in by_sig.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                results["pairs_checked"] += 1
                pref_s, state_s = group[i]
                pref_sp, state_sp = group[j]
                # Need to find a suffix completing S; for this lightweight
                # test, use the prefix_sp's continuation. Skip if no
                # cycle-failure pair found.
                # Use suffix = remaining vertices in some order.
                remaining = [v for v in range(len(T))
                             if not (state_s[0] & (1 << v))]
                # Try the natural order
                suffix = tuple(remaining)
                cert = certify_aux1(T, state_sp, suffix)
                if cert.get("failed_at") is None:
                    continue
                if "aux1_holds" not in cert:
                    continue
                results["cycle_failures"] += 1
                if not cert["aux1_holds"]:
                    results["aux1_violations"] += 1
                    if len(results["examples"]) < 3:
                        results["examples"].append(cert)
    return results


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("--T", required=True, help="Tournament as a JSON matrix")
    p.add_argument("--depth", type=int, default=5)
    args = p.parse_args()
    T = json.loads(args.T)
    out = certify_witness_set(T, args.depth)
    print(json.dumps(out, indent=2, default=str))
