"""Runtime certificate for the G1, G2 invariants of Section 13.7.

  (G1) For every FF-pruned prefix at cut i and every v in A_i ∪ O_i,
       the visible-latent signature contains the value deg[v] from the
       union-find. Specifically, the visible_partition tuple in
       visible_latent_signature has the entry (v_id_or_old, degree[v],
       block_label).

  (G2) For every FF-pruned prefix at cut i and every v in F_i (i.e.,
       unplaced future-opening), deg[v] in the union-find at cut i
       equals the number of forced backedges incident to v in the
       initial state (no flex backedge contributes to v's degree at
       cut i because v is unplaced).

Both invariants are computable per-instance. This script verifies them
on every FF-pruned depth-bounded prefix of a test tournament. The
output certifies the structural skeleton of Section 13.

Usage:
  uv run python scripts/sleeping_g1g2_certificate.py --T <json> --depth 5
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
    prefixes,
    valid_prefix_state_ff,
    visible_latent_signature,
)
from lfo_forced_flexible import _initial_forced_state  # noqa: E402
from lfo_score_window import score_windows  # noqa: E402
from sleeping_certificate import _boundary_set  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]


def _forced_degree_into(
    T: Matrix,
    v: int,
    windows: Sequence[tuple[int, int]],
) -> int:
    """Count forced backedges incident to v from initial state.

    A forced backedge between u and v exists iff their score windows are
    disjoint AND T's arc orientation makes one a backedge of the other.
    """
    n = len(T)
    count = 0
    lo_v, hi_v = windows[v]
    for u in range(n):
        if u == v:
            continue
        lo_u, hi_u = windows[u]
        # Disjoint windows
        if hi_u < lo_v and T[v][u] == 1:
            # u placed before v, arc v->u back
            count += 1
        elif hi_v < lo_u and T[u][v] == 1:
            # v placed before u, arc u->v back
            count += 1
    return count


def certify_g1_g2(T: Matrix, depth: int = 5) -> dict:
    """For every depth-bounded FF-pruned prefix, verify G1 and G2."""
    n = len(T)
    windows = score_windows(T)
    g1_failures = []
    g2_failures = []
    prefixes_checked = 0

    for prefix in prefixes(n, depth):
        state = valid_prefix_state_ff(T, prefix)
        if state is None:
            continue
        pos = len(prefix)
        if not survives_pruning(state, pos, n):
            continue
        prefixes_checked += 1
        prefix_mask, degree, parent, flex_outmask, win = state
        assert win == windows

        # G1: visible-latent records degree for v in A_i ∪ O_i
        v_sig = visible_latent_signature(
            pos, prefix_mask, degree, parent, flex_outmask, windows
        )
        # visible_partition is at index 4
        visible_partition = v_sig[4]
        # The signature records visible_old as "old" rather than vertex
        # id, so we extract degrees keyed by the visible-vertex order
        # the signature uses. The "visible" list is implicit; we
        # reconstruct it from active_set ∪ visible_old.
        active_set = {v for v, (lo, hi) in enumerate(windows) if lo <= pos <= hi}
        placed_set = {v for v in range(n) if prefix_mask & (1 << v)}
        unplaced_active = active_set - placed_set
        visible_old = set()
        for x in unplaced_active:
            for p in range(n):
                if (flex_outmask[x] >> p) & 1 and (prefix_mask >> p) & 1:
                    if p not in active_set:
                        visible_old.add(p)
        visible_set = sorted(active_set | visible_old)

        # visible_partition is a tuple of (label, degree, block_label)
        # ordered by sorted visible. Check that the degree in the
        # signature matches the union-find degree.
        if len(visible_partition) != len(visible_set):
            g1_failures.append({
                "prefix": list(prefix),
                "reason": "visible_partition length mismatch",
                "vis_len": len(visible_set),
                "sig_len": len(visible_partition),
            })
        for idx, v in enumerate(visible_set):
            label, sig_deg, _block = visible_partition[idx]
            if sig_deg != degree[v]:
                g1_failures.append({
                    "prefix": list(prefix),
                    "vertex": v,
                    "sig_degree": sig_deg,
                    "uf_degree": degree[v],
                })

        # G2: F_i degree = forced backedges into v
        future_opening = {
            v for v, (lo, _hi) in enumerate(windows)
            if lo > pos and not (prefix_mask & (1 << v))
        }
        for v in future_opening:
            forced_deg = _forced_degree_into(T, v, windows)
            if forced_deg != degree[v]:
                g2_failures.append({
                    "prefix": list(prefix),
                    "vertex": v,
                    "uf_degree": degree[v],
                    "forced_deg": forced_deg,
                })

    return {
        "n": n,
        "depth": depth,
        "prefixes_checked": prefixes_checked,
        "g1_failures": len(g1_failures),
        "g2_failures": len(g2_failures),
        "g1_examples": g1_failures[:3],
        "g2_examples": g2_failures[:3],
        "g1_holds": len(g1_failures) == 0,
        "g2_holds": len(g2_failures) == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", required=True)
    parser.add_argument("--depth", type=int, default=5)
    args = parser.parse_args()
    T = json.loads(args.T)
    out = certify_g1_g2(T, args.depth)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
