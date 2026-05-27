"""Band-DP transition rank analysis for general tournament Path-FAS.

Score-window theory bounds the active window to width 5 (radius 2)
and Hall pruning bounds simultaneously-active vertices to <=9.  A
natural DP node treats each band of LFO positions [d-2, d+2] as a
5-state node and asks: what is the matrix rank of the transition
operator between two adjacent bands?

If the band-DP transition tensor has polynomially bounded rank, then
the DP factors through a low-rank decomposition and yields a poly-time
algorithm in spite of the exponential explicit state space.

This probe builds the transition operator for each cut empirically:

  Rows  = active-bag signatures of FF-pruned prefixes at cut c.
  Cols  = active-bag signatures of FF-pruned prefixes at cut c+1.
  Entry = number of FF-valid transitions from row state to col state.

The "rank" of this matrix bounds the algorithmic compressibility of the
DP at this cut.  We probe it on the toggle and chain-seeded toggle
families, where the lower bound is known to be exponential.

NOTE: This probe enumerates valid FF-prefixes by brute force, so it is
limited to small k.  The point is not to find an algorithm but to
empirically measure whether the rank stays bounded or grows.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from itertools import permutations
from typing import Sequence

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    active_signature,
    has_completion_ff,
    valid_prefix_state_ff,
)
from quotient_signature_probe import (  # noqa: E402
    chain_seeded_toggle_tournament,
)
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402
from sleeping_bound_refutation import (  # noqa: E402
    toggle_tournament,
)
from sleeping_block_probe import sleeping_block_signature  # noqa: E402
from wake_signature_probe import survives_pruning  # noqa: E402


Matrix = Sequence[Sequence[int]]


def enumerate_prefixes_at_cut(T: Matrix, cut: int) -> list[tuple]:
    """All FF-pruned prefixes of length exactly `cut`, via DFS.

    Uses window-feasibility to prune early: only vertices whose window
    contains the current position are extension candidates.
    """
    n = len(T)
    init = valid_prefix_state_ff(T, ())
    if init is None:
        return []
    _, _, _, _, windows = init
    out: list[tuple] = []

    def dfs(prefix: tuple, pos: int):
        if pos == cut:
            state = valid_prefix_state_ff(T, prefix)
            if state is None:
                return
            if not survives_pruning(state, cut, n):
                return
            out.append(prefix)
            return
        for v in range(n):
            if v in prefix:
                continue
            lo, hi = windows[v]
            if not (lo <= pos <= hi):
                continue
            new_prefix = prefix + (v,)
            state = valid_prefix_state_ff(T, new_prefix)
            if state is None:
                continue
            dfs(new_prefix, pos + 1)

    dfs((), 0)
    return out


def transition_matrix(T: Matrix, cut: int, sigfun=active_signature) -> dict:
    """Build the transition matrix between cut and cut+1."""
    n = len(T)
    rows_by_sig: dict[tuple, list[int]] = defaultdict(list)
    cols_by_sig: dict[tuple, list[int]] = defaultdict(list)

    prefs_c = enumerate_prefixes_at_cut(T, cut)
    prefs_cp1 = enumerate_prefixes_at_cut(T, cut + 1)

    for idx, prefix in enumerate(prefs_c):
        state = valid_prefix_state_ff(T, prefix)
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = sigfun(cut, prefix_mask, degree, parent, windows) \
            if sigfun.__name__ == "active_signature" else \
            sigfun(cut, prefix_mask, degree, parent, flex_outmask, windows)
        rows_by_sig[sig].append(idx)
    for idx, prefix in enumerate(prefs_cp1):
        state = valid_prefix_state_ff(T, prefix)
        prefix_mask, degree, parent, flex_outmask, windows = state
        sig = sigfun(cut + 1, prefix_mask, degree, parent, windows) \
            if sigfun.__name__ == "active_signature" else \
            sigfun(cut + 1, prefix_mask, degree, parent, flex_outmask, windows)
        cols_by_sig[sig].append(idx)

    row_sigs = list(rows_by_sig.keys())
    col_sigs = list(cols_by_sig.keys())
    row_idx = {s: i for i, s in enumerate(row_sigs)}
    col_idx = {s: i for i, s in enumerate(col_sigs)}

    M = np.zeros((len(row_sigs), len(col_sigs)), dtype=np.int64)

    for i, prefix_c in enumerate(prefs_c):
        state_c = valid_prefix_state_ff(T, prefix_c)
        pm_c, deg_c, par_c, flex_c, win_c = state_c
        sig_c = sigfun(cut, pm_c, deg_c, par_c, win_c) \
            if sigfun.__name__ == "active_signature" else \
            sigfun(cut, pm_c, deg_c, par_c, flex_c, win_c)
        prefix_c_set = set(prefix_c)
        for v in range(n):
            if v in prefix_c_set:
                continue
            new_pref = prefix_c + (v,)
            state_n = valid_prefix_state_ff(T, new_pref)
            if state_n is None:
                continue
            if not survives_pruning(state_n, cut + 1, n):
                continue
            pm_n, deg_n, par_n, flex_n, win_n = state_n
            sig_n = sigfun(cut + 1, pm_n, deg_n, par_n, win_n) \
                if sigfun.__name__ == "active_signature" else \
                sigfun(cut + 1, pm_n, deg_n, par_n, flex_n, win_n)
            if sig_n not in col_idx:
                continue
            M[row_idx[sig_c], col_idx[sig_n]] += 1

    # Reduce M to a 0/1 reachability matrix for rank purposes:
    R = (M > 0).astype(np.int64)
    return {
        "cut": cut,
        "rows": len(row_sigs),
        "cols": len(col_sigs),
        "rank_R_int": int(np.linalg.matrix_rank(R.astype(float))),
        "n_prefs_c": len(prefs_c),
        "n_prefs_cp1": len(prefs_cp1),
        "row_sigs": row_sigs,
        "col_sigs": col_sigs,
        "M": M.tolist(),
    }


def benchmark_toggle(max_k: int = 4) -> list[dict]:
    out: list[dict] = []
    for k in range(1, max_k + 1):
        T = toggle_tournament(k)
        n = len(T)
        cut = 2 * k - 1 if 2 * k - 1 > 0 else 1
        # Use cut just before all pairs are placed to test rank.
        # We probe at multiple cuts for stability.
        results = []
        # Probe cuts from cut=2 up to cut=2k+1, in steps of 1
        for c in range(2, min(2 * k + 2, n)):
            try:
                rec = transition_matrix(T, c, sigfun=active_signature)
                results.append({
                    "cut": c,
                    "rows": rec["rows"],
                    "cols": rec["cols"],
                    "rank": rec["rank_R_int"],
                })
            except Exception as e:
                results.append({"cut": c, "error": str(e)})
        out.append({"family": "toggle", "k": k, "n": n, "transitions": results})
    return out


def benchmark_chain_seeded(max_k: int = 4) -> list[dict]:
    out: list[dict] = []
    for k in range(1, max_k + 1):
        T = chain_seeded_toggle_tournament(k)
        n = len(T)
        results = []
        for c in range(2, min(2 * k + 3, n)):
            try:
                rec = transition_matrix(T, c, sigfun=active_signature)
                results.append({
                    "cut": c,
                    "rows": rec["rows"],
                    "cols": rec["cols"],
                    "rank": rec["rank_R_int"],
                })
            except Exception as e:
                results.append({"cut": c, "error": str(e)})
        out.append({
            "family": "chain_seeded",
            "k": k, "n": n, "transitions": results,
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps({
        "toggle": benchmark_toggle(args.max_k),
        "chain_seeded": benchmark_chain_seeded(args.max_k),
    }, indent=2, default=list))


if __name__ == "__main__":
    main()
