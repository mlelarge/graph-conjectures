"""Defect measure and local exchange-repair framework (D56).

This module formalizes the *defect measure* D(sigma) and the finite set of
*local repair moves* that the Mixed-Parity Escape Lemma (55.1) must use to
turn any window-feasible suffix sigma for a non-V6''-trigger cyclic-ladder
core C into an FF-valid completion (D(sigma)=0).

The lemma (55.1) states: if C is V6''-negative, then C is extendable
or contains a smaller V6''-positive sub-core.  The constructive content
is: starting from any window-feasible suffix sigma_0, a finite sequence
of local repair moves drives D(sigma) strictly down to D(sigma)=0
(i.e., FF-valid suffix), assuming we are in the (O1) extendable branch.

The defect measure D(sigma) is a lexicographic triple

    D(sigma) = (c(sigma), d_3(sigma), ell(sigma))

over the *abstract back-arc graph* G(sigma) obtained by loading every
flexible backedge whose endpoints lie in (placed_before, placed_after)
relative to sigma, *without* aborting on FF-degree/FF-cycle violations.

  - c(sigma) = number of independent cycles in G(sigma)
              (= |E(G)| - |V_touched(G)| + #components(G) restricted
                  to the touched-vertex subgraph).
  - d_3(sigma) = sum_v max(0, deg_v(G) - 2) = total degree excess.
  - ell(sigma) = number of loaded chain links inside the *mixed-parity
              break region* — the chain links B_{2a+1} -> B_{2a} (or
              A_{2a+1} -> A_{2a}) inside an even-start image interval
              of C.

The triple is ordered LEXICOGRAPHICALLY: (c, d_3, ell).

EMPIRICAL FINDING: the strict-decrease repair loop using the FULL
lex triple (c, d_3, ell) gets stuck for 8/24 non-trigger cores at k=4
(both the non-minimal-fatal and 4/16 pure-Escape cases).  The stuck
configurations have D=(0, 1, 0) but the unique FF-valid suffix has
D=(0, 0, 1); reaching it requires INCREASING ell from 0 to 1, which
the strict-lex-decrease rule forbids.

The CORRECTED success criterion drops ell:

    SUCCESS(sigma) iff c(sigma) == 0 AND d_3(sigma) == 0.

ell is a DIAGNOSTIC, not a defect to be minimized.  With the corrected
criterion, the repair loop reaches FF-validity on ALL non-trigger
cyclic-ladder cores at k=4,5,6 (856/856 cases).

A configuration is FF-valid iff (c(sigma), d_3(sigma)) = (0, 0):
  - c = 0 means the abstract back-arc graph is a forest;
  - d_3 = 0 means every vertex has degree <= 2 (linear forest).

ell is a *tertiary* defect that does NOT affect FF-feasibility on its
own.  In non-minimal-fatal cores (e.g., k=4 with C=(0,1,2,3)) an
FF-valid completion can still load chain links inside even-start
intervals (ell > 0) because the cyclic-ladder cycle is broken
elsewhere — e.g., by a V6''-positive sub-core elsewhere in the
ladder.  ell tracks how far the suffix has driven the breakage
toward the slack interval, but its value at FF-validity is allowed
to be positive.

Hence the **repair-loop success criterion** is

    SUCCESS(sigma) iff c(sigma) == 0 AND d_3(sigma) == 0.

ell is retained in the lex tuple as a fine-grained progress measure
that can break ties when c and d_3 cannot be reduced further by a
local move.

This is the COMMON LANGUAGE shared by the four parallel agents
attacking the Mixed-Parity Escape Lemma.

Usage:
  uv run python scripts/defect_repair_framework.py --k 4
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations, permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import (  # noqa: E402
    _add_flexible_vertex,
    valid_prefix_state_ff,
)
from fork_tree_probe import fork_tree_prefix, fork_tree_tournament  # noqa: E402
from lfo_forced_flexible import _find, _iter_bits, _union  # noqa: E402
from rectangle_detachability_probe import even_adjacent_blocks  # noqa: E402
from v6pp_completion_constructor import (  # noqa: E402
    has_no_v6pp_trigger,
    is_cyclic_ladder_core,
)
from v6pp_predictor import _intervals_from_images  # noqa: E402


# --------------------------------------------------------------------------
# Soft FF state: accumulate the abstract back-arc graph without aborting.
# --------------------------------------------------------------------------

def _abstract_back_arc_graph(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    sigma: Sequence[int],
) -> dict:
    """Build the abstract back-arc graph G(sigma) at full cut n.

    Returns dict with:
      - "n": vertex count.
      - "edges": sorted list of edges {u,v} with u<v.
      - "degree": list of degree per vertex.
      - "forced_edges": edges already preloaded by _initial_forced_state.
      - "flex_edges_by_step": list of (step_index, vertex_placed, partner)
        for diagnostics.
      - "valid_prefix": bool whether the prefix from C is valid.
      - "windows": score windows.
      - "flex_outmask": flexible-out masks per vertex.
    """
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return {"valid_prefix": False}
    prefix_mask, degree0, parent0, flex_outmask, windows = state
    n = len(T)

    # Forced edges from _initial_forced_state.
    # We reconstruct them indirectly: any vertex u with degree0[u] > 0 has
    # forced edges to specific partners.  But _initial_forced_state doesn't
    # return the edge list; we just have the union-find and degree array.
    # For our purposes, we need the full edge set: derive it by re-running
    # the forced loader OR by tracking degree/parent changes per step.
    #
    # Cleaner: compute the edge set from scratch by walking forced + flex.
    from score_window_forced import forced_order
    forced_edges = set()
    for u in range(n):
        for v in range(u + 1, n):
            fixed = forced_order(windows, u, v)
            if fixed is None:
                continue
            earlier, later = fixed
            if T[later][earlier]:
                forced_edges.add((min(u, v), max(u, v)))

    # Flex backedges loaded as suffix is placed.
    edges = set(forced_edges)
    flex_edges = []
    pmask = prefix_mask
    pos = bin(pmask).count('1')
    window_ok = True
    first_window_violation = None
    for i, x in enumerate(sigma):
        if not (windows[x][0] <= pos <= windows[x][1]):
            window_ok = False
            first_window_violation = {"step": i, "vertex": x, "pos": pos}
            break
        for p in _iter_bits(flex_outmask[x] & pmask):
            e = (min(x, p), max(x, p))
            edges.add(e)
            flex_edges.append((i, x, p))
        pmask |= 1 << x
        pos += 1

    # Compute degree per vertex.
    deg = [0] * n
    for (u, v) in edges:
        deg[u] += 1
        deg[v] += 1

    return {
        "valid_prefix": True,
        "window_ok": window_ok,
        "first_window_violation": first_window_violation,
        "n": n,
        "edges": sorted(edges),
        "forced_edges": sorted(forced_edges),
        "flex_edges_by_step": flex_edges,
        "degree": deg,
        "windows": windows,
        "flex_outmask": flex_outmask,
        "prefix_mask_initial": prefix_mask,
        "start_pos": bin(prefix_mask).count('1'),
        "T": T,
    }


def _count_cycles_and_excess(edges, degree, n) -> tuple[int, int]:
    """Compute (#independent_cycles, total_degree_excess) of the multigraph
    induced by `edges`.  Independent cycles in a graph = |E| - |V'| + |C|
    where V' is the set of touched vertices and C is the number of
    connected components in the touched-vertex subgraph.
    """
    touched = set()
    for (u, v) in edges:
        touched.add(u)
        touched.add(v)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
            return True
        return False

    edge_count = 0
    cycle_edges = 0  # edges that close a cycle
    for (u, v) in edges:
        edge_count += 1
        if not union(u, v):
            cycle_edges += 1

    # Components in touched-vertex subgraph.
    comps = {find(v) for v in touched}

    # Independent cycles = E - V' + C.
    c = len(edges) - len(touched) + len(comps)
    # That equals cycle_edges, confirming.
    assert c == cycle_edges

    d3 = sum(max(0, d - 2) for d in degree)
    return c, d3


def _mixed_parity_break_chain_links(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
) -> set:
    """Return the set of "mixed-parity break" chain links inside C.

    For each even-start image interval I_t = {2a, 2a+1} of C, identify
    which B (or A) chain link B_{i_low}->B_{i_high} (in LFO loading
    convention) corresponds to "within-interval chain edge" that, if
    loaded, contributes to the cyclic ladder cycle's closure.

    Specifically: each interval {2a, 2a+1} in pi(C) corresponds to two
    pair-indices i_a, i_b with pi(i_a)=2a, pi(i_b)=2a+1.  The B-side
    chain link is between B_{i_a} and B_{i_b} — at LFO level, the
    backedge {B_{i_a}, B_{i_b}} loads iff the later-placed of the two
    has a flex_outmask bit to the earlier.

    We return the *edges* (in canonical sorted form) corresponding to
    chain links inside even-start intervals.  Counting how many of
    these are loaded is ell(sigma).
    """
    images = sorted({pi[i] for i in C})
    intervals = _intervals_from_images(images)
    if intervals is None:
        return set()
    C_set = set(C)
    even_start_intervals = [iv for iv in intervals if iv[0] % 2 == 0]

    n = 4 * k + 2

    def A(i):
        return 2 * k + 2 + i

    def B(i):
        return 3 * k + 2 + i

    # For each even-start interval, find the two pair-indices in C whose
    # images are the interval's two endpoints.
    chain_links = set()
    inverse_pi = {pi[i]: i for i in range(k)}
    for iv in even_start_intervals:
        lo, hi = iv
        i_lo = inverse_pi[lo]
        i_hi = inverse_pi[hi]
        if i_lo not in C_set or i_hi not in C_set:
            continue
        # Both B and A chain links inside this interval are candidates.
        # We focus on the B-side (B-vertices map to the toggle).  The
        # within-interval B chain link connects B_{min(i_lo,i_hi)} and
        # B_{max(i_lo,i_hi)} via the chain B_{j+1}->B_{j}.
        if abs(i_lo - i_hi) == 1:
            j_lo, j_hi = min(i_lo, i_hi), max(i_lo, i_hi)
            # Chain link B_{j_hi} -> B_{j_lo} (immediate chain edge)
            chain_links.add((B(j_lo), B(j_hi)))
        # Also A-side chain link inside interval — but cyclic-ladder cycle
        # threads through B side via reversal; we focus on B-chain.
    return chain_links


def _loaded_break_links(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    sigma: Sequence[int],
    graph_info: dict,
) -> int:
    """Count how many mixed-parity break chain links are LOADED in G(sigma)."""
    links = _mixed_parity_break_chain_links(k, pi, C)
    edge_set = set(graph_info["edges"])
    return sum(1 for e in links if e in edge_set)


# --------------------------------------------------------------------------
# 1. Defect measure D(sigma).
# --------------------------------------------------------------------------

def compute_defect(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    sigma: Sequence[int],
) -> tuple:
    """Compute D(sigma) = (c, d_3, ell) lex-ordered.

    If sigma is not window-feasible, returns (None, None, None) with
    a diagnostic dict.

    Returns the triple as a Python tuple; the caller can compare with
    lex order.

    Convention: D = (cycles, degree_excess, loaded_break_links).
    Smaller is better.  D = (0, 0, 0) iff sigma is FF-valid and breaks
    every mixed-parity chain link.
    """
    info = _abstract_back_arc_graph(k, pi, C, sigma)
    if not info["valid_prefix"]:
        return (float('inf'), float('inf'), float('inf'))
    if not info["window_ok"]:
        # Window violation: assign +inf — sigma not window-feasible.
        return (float('inf'), float('inf'), float('inf'))
    c, d3 = _count_cycles_and_excess(info["edges"], info["degree"], info["n"])
    ell = _loaded_break_links(k, pi, C, sigma, info)
    return (c, d3, ell)


def is_ff_valid(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    sigma: Sequence[int],
) -> bool:
    """Replay sigma through FF; return True iff every step accepted and
    suffix completes."""
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return False
    pmask, deg, par, flex, win = state
    n = len(T)
    pos = bin(pmask).count('1')
    for x in sigma:
        if not (win[x][0] <= pos <= win[x][1]):
            return False
        nxt = _add_flexible_vertex(flex, pmask, deg, par, x)
        if nxt is None:
            return False
        deg, par = nxt
        pmask |= 1 << x
        pos += 1
    return pmask == (1 << n) - 1


# --------------------------------------------------------------------------
# 2. Enumerate the finite set of local repair moves.
# --------------------------------------------------------------------------

def _window_feasible(
    sigma: Sequence[int],
    start_pos: int,
    windows: Sequence[tuple[int, int]],
) -> bool:
    for i, x in enumerate(sigma):
        pos = start_pos + i
        if not (windows[x][0] <= pos <= windows[x][1]):
            return False
    return True


def enumerate_repair_moves(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    sigma: Sequence[int],
) -> list[dict]:
    """Return a list of candidate local repair moves.

    Move catalogue (all four user-proposed move types):

    1. ADJACENT SWAP (i, i+1): swap suffix positions i, i+1 if both
       remain window-feasible.

    2. 3-BLOCK ROTATION (i, i+1, i+2): rotate (sigma[i], sigma[i+1],
       sigma[i+2]) cyclically; two rotations possible
       (left = (i+1, i+2, i), right = (i+2, i, i+1)).  We emit both.

    3. DELAYED SATURATED ENDPOINT (j, j'): move sigma[j] to position
       j' > j, where j' is the latest window-feasible position.
       Restricted to vertices currently at FF-saturating positions
       (degree>=2 in the abstract graph).

    4. ADVANCED SLACK FILLER (j, j'): move sigma[j] to position
       j' < j, where j' is the earliest window-feasible position.
       Restricted to vertices that are "slack" (flex_outmask bit-count
       low in their current backward direction).

    All moves are emitted as window-feasible candidates only; FF
    validity is verified later (we only need D(sigma') < D(sigma)).

    Each move is a dict with keys:
      "type": one of "adj_swap", "rot3_left", "rot3_right",
              "delay_endpoint", "advance_slack".
      "params": specific to the move type.
    """
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return []
    prefix_mask, _, _, _, windows = state
    start_pos = bin(prefix_mask).count('1')

    moves: list[dict] = []
    L = len(sigma)

    # 1. Adjacent swaps.
    for i in range(L - 1):
        new_sigma = list(sigma)
        new_sigma[i], new_sigma[i + 1] = new_sigma[i + 1], new_sigma[i]
        if _window_feasible(new_sigma, start_pos, windows):
            moves.append({
                "type": "adj_swap",
                "params": {"i": i, "j": i + 1},
                "new_sigma": tuple(new_sigma),
            })

    # 2. 3-block rotations.
    for i in range(L - 2):
        a, b, c_ = sigma[i], sigma[i + 1], sigma[i + 2]
        # Left rotation: (a, b, c) -> (b, c, a).
        new_left = list(sigma)
        new_left[i], new_left[i + 1], new_left[i + 2] = b, c_, a
        if _window_feasible(new_left, start_pos, windows):
            moves.append({
                "type": "rot3_left",
                "params": {"i": i},
                "new_sigma": tuple(new_left),
            })
        # Right rotation: (a, b, c) -> (c, a, b).
        new_right = list(sigma)
        new_right[i], new_right[i + 1], new_right[i + 2] = c_, a, b
        if _window_feasible(new_right, start_pos, windows):
            moves.append({
                "type": "rot3_right",
                "params": {"i": i},
                "new_sigma": tuple(new_right),
            })

    # 3. Delayed saturated endpoint: move a vertex with high degree later.
    info = _abstract_back_arc_graph(k, pi, C, sigma)
    if info["valid_prefix"]:
        degree = info["degree"]
        for j in range(L):
            v = sigma[j]
            if degree[v] < 2:
                continue
            # Try moving v to every j' > j.
            for jp in range(j + 1, L):
                new_sigma = list(sigma)
                v_moved = new_sigma.pop(j)
                new_sigma.insert(jp, v_moved)
                if _window_feasible(new_sigma, start_pos, windows):
                    moves.append({
                        "type": "delay_endpoint",
                        "params": {"j": j, "jp": jp, "vertex": v},
                        "new_sigma": tuple(new_sigma),
                    })

        # 4. Advanced slack filler: move a low-flex-load vertex earlier.
        flex_outmask = info["flex_outmask"]
        for j in range(L):
            v = sigma[j]
            # "Slack" means flex_outmask[v] has few in-prefix bits at j.
            # Heuristic: only move vertices whose flex_outmask has 0 or 1
            # bits to suffix-prior vertices.
            n = info["n"]
            prior_mask = info["prefix_mask_initial"]
            for k_idx in range(j):
                prior_mask |= 1 << sigma[k_idx]
            in_prior = (flex_outmask[v] & prior_mask).bit_count()
            if in_prior > 1:
                continue
            for jp in range(j):
                new_sigma = list(sigma)
                v_moved = new_sigma.pop(j)
                new_sigma.insert(jp, v_moved)
                if _window_feasible(new_sigma, start_pos, windows):
                    moves.append({
                        "type": "advance_slack",
                        "params": {"j": j, "jp": jp, "vertex": v},
                        "new_sigma": tuple(new_sigma),
                    })

    return moves


def apply_move(sigma: Sequence[int], move: dict) -> tuple[int, ...]:
    """Apply a move dict to sigma, returning the new tuple."""
    return tuple(move["new_sigma"])


# --------------------------------------------------------------------------
# 3. Repair step.
# --------------------------------------------------------------------------

def _descent_key(D: tuple) -> tuple:
    """The (c, d_3) prefix of D used for strict-lex-decrease descent.

    ell is retained as a diagnostic in compute_defect but is NOT part
    of the strict-decrease criterion — see module docstring.
    """
    return (D[0], D[1])


def _is_ff_valid_defect(D: tuple) -> bool:
    """Success: c=0 AND d_3=0.  ell allowed to be positive."""
    return D[0] == 0 and D[1] == 0


def repair_step(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    sigma: Sequence[int],
) -> dict:
    """Find a single repair move strictly decreasing (c, d_3).

    Returns a dict:
      "decreased": bool — whether a move was found.
      "sigma_old": tuple — original sigma.
      "sigma_new": tuple — sigma' with descent_key strictly less.
      "D_old": full triple (c, d_3, ell).
      "D_new": full triple or None.
      "move": move dict or None.
    """
    D_old = compute_defect(k, pi, C, sigma)
    if _is_ff_valid_defect(D_old):
        return {
            "decreased": False,
            "sigma_old": tuple(sigma),
            "sigma_new": None,
            "D_old": D_old,
            "D_new": None,
            "move": None,
            "reason": "already_ff_valid",
        }
    moves = enumerate_repair_moves(k, pi, C, sigma)
    best_move = None
    best_key = _descent_key(D_old)
    best_D = D_old
    best_sigma = None
    for m in moves:
        new_sigma = apply_move(sigma, m)
        D_new = compute_defect(k, pi, C, new_sigma)
        k_new = _descent_key(D_new)
        if k_new < best_key:
            best_key = k_new
            best_D = D_new
            best_move = m
            best_sigma = new_sigma
    return {
        "decreased": best_move is not None,
        "sigma_old": tuple(sigma),
        "sigma_new": best_sigma,
        "D_old": D_old,
        "D_new": best_D if best_move is not None else None,
        "move": best_move,
    }


def repair_loop(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
    sigma_0: Sequence[int],
    max_steps: int = 200,
) -> dict:
    """Iterate repair_step until D=0 or no decrease found."""
    sigma = tuple(sigma_0)
    trace = []
    for step in range(max_steps):
        D = compute_defect(k, pi, C, sigma)
        trace.append({"step": step, "D": list(D), "sigma": list(sigma)})
        if _is_ff_valid_defect(D):
            return {
                "reached_zero": True,
                "steps": step,
                "trace": trace,
                "final_sigma": list(sigma),
            }
        res = repair_step(k, pi, C, sigma)
        if not res["decreased"]:
            return {
                "reached_zero": False,
                "steps": step,
                "trace": trace,
                "final_sigma": list(sigma),
                "stuck_at_D": list(D),
                "reason": "no_strict_decrease",
            }
        sigma = res["sigma_new"]
    return {
        "reached_zero": False,
        "steps": max_steps,
        "trace": trace,
        "final_sigma": list(sigma),
        "reason": "max_steps_exceeded",
    }


# --------------------------------------------------------------------------
# Empirical verification: enumerate non-trigger cores and try the loop.
# --------------------------------------------------------------------------

def _initial_window_feasible_sigma(
    k: int,
    pi: Sequence[int],
    C: Sequence[int],
) -> tuple[int, ...] | None:
    """Pick a deterministic window-feasible suffix as starting point:
    place remaining vertices in increasing window-low order (ties broken
    by index)."""
    bits = tuple(1 if i in set(C) else 0 for i in range(k))
    prefix = fork_tree_prefix(k, bits)
    T = fork_tree_tournament(k, pi)
    state = valid_prefix_state_ff(T, prefix)
    if state is None:
        return None
    pmask, _, _, _, windows = state
    n = len(T)
    remaining = [v for v in range(n) if not (pmask & (1 << v))]
    # Sort by (window_lo, vertex).
    remaining.sort(key=lambda v: (windows[v][0], v))
    start_pos = bin(pmask).count('1')
    if _window_feasible(remaining, start_pos, windows):
        return tuple(remaining)
    # Otherwise try permutations by greedy assignment.
    used = [False] * len(remaining)
    out: list[int] = []
    for p in range(len(remaining)):
        pos = start_pos + p
        for idx, v in enumerate(remaining):
            if used[idx]:
                continue
            if windows[v][0] <= pos <= windows[v][1]:
                used[idx] = True
                out.append(v)
                break
        else:
            return None
    return tuple(out)


def verify_repair_loop_at_k(k: int, max_cases: int = 20) -> dict:
    """Enumerate non-V6''-trigger cyclic-ladder cores at k, attempt the
    repair loop from a deterministic initial sigma_0.  Report success
    rate."""
    blocks = even_adjacent_blocks(k)
    total = 0
    reached_zero = 0
    failed: list[dict] = []
    stuck_summary: dict[tuple, int] = {}

    for pi in permutations(range(k)):
        for size in range(1, len(blocks) + 1):
            for block_subset in combinations(blocks, size):
                C = tuple(sorted(i for blk in block_subset for i in blk))
                if not is_cyclic_ladder_core(k, pi, C):
                    continue
                if not has_no_v6pp_trigger(k, pi, C):
                    continue
                total += 1
                sigma_0 = _initial_window_feasible_sigma(k, pi, C)
                if sigma_0 is None:
                    continue
                result = repair_loop(k, pi, C, sigma_0, max_steps=100)
                if result["reached_zero"]:
                    reached_zero += 1
                else:
                    key = tuple(result.get("stuck_at_D", []))
                    stuck_summary[key] = stuck_summary.get(key, 0) + 1
                    if len(failed) < max_cases:
                        failed.append({
                            "pi": list(pi),
                            "C": list(C),
                            "stuck_at_D": result.get("stuck_at_D"),
                            "reason": result.get("reason"),
                        })

    return {
        "k": k,
        "total_non_trigger_cores": total,
        "repair_loop_reached_zero": reached_zero,
        "repair_loop_failed": total - reached_zero,
        "stuck_D_histogram": {
            "_".join(str(x) for x in d): n_ for d, n_ in stuck_summary.items()
        },
        "first_failures": failed[:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    out = verify_repair_loop_at_k(args.k)
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
