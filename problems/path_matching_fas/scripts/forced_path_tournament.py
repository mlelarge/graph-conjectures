"""Forced-forest wire probe: how long can a forced path in H be?

Setup
-----
For a tournament T on n vertices and score-window radius r = 2, the
score-window theorem (`docs/score_window.md`) puts every vertex v in an
LFO at a position inside its score window

    I_v := [d^-(v) - r, d^-(v) + r].

The forced-relation graph H has an undirected edge {u, v} iff the
windows I_u and I_v are *disjoint*, i.e. |d^-(u) - d^-(v)| > 2r = 4.
Equivalently, |d^-(u) - d^-(v)| >= 5.  For such a pair the relative
order of u and v in any LFO is fixed by the score-window inequalities;
hence the actual tournament arc between u and v is either always a
forward arc (a forced "forward" in any LFO) or always a back-arc (a
forced back-arc, the "wire" we are trying to exploit).

Goal of this script
-------------------
Search empirically how long the forced-back-arc subgraph of H can be
*as a path* on small tournaments (n up to ~16) under several random
distributions.  This is the prerequisite of any "forced-forest wire"
reduction: if H restricted to back-arcs is never a path of length >= 3
in any tournament family of polynomial size, the wire reduction is
infeasible.

What we measure
---------------
- The forced-undirected graph H_und on V(T) with edge {u, v} iff
  |d^-(u) - d^-(v)| >= 5.
- The subgraph H_back containing only the *back-arc-forced* edges
  (i.e. where T has the arc later -> earlier).
- The longest path length in H_back (via brute force DFS on small n).

Theoretical bound
-----------------
A path v_0 - v_1 - ... - v_k in H_back requires the in-degree sequence
of consecutive vertices to differ by >= 5.  Hence the alternating-sign
gap argument gives no immediate bound, but the *score-span* bound

    max d^- - min d^- >= 5 * ceil(k/2)

does apply: if the v_i in-degrees zig-zag, the span between the
extremes is at least 5 * ceil(k/2).  Combined with d^- in [0, n-1],
this gives

    n - 1 >= 5 * ceil(k/2),
    k <= 2 * floor((n - 1) / 5).

For n = 12 this yields k <= 4.  For n = 16 this yields k <= 6.  For
arbitrarily long forced paths, n must grow linearly in k.

This is the central structural obstruction documented by this script.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import indegrees, score_windows  # noqa: E402

Matrix = Sequence[Sequence[int]]


def forced_relations(T: Matrix, radius: int = 2) -> dict:
    """Compute the forced edges of H on T.

    Returns a dict with:
      - 'forced_back': list of (later, earlier) tournament arcs whose
        relative order is forced AND whose orientation is a back-arc.
      - 'forced_forward': forced forward arcs.
      - 'pairs': total forced pairs.
      - 'undirected_edges': all forced undirected edges {u, v}.
    """
    n = len(T)
    windows = score_windows(T, radius)
    forced_back: list[tuple[int, int]] = []
    forced_forward: list[tuple[int, int]] = []
    undirected: list[tuple[int, int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            lo_u, hi_u = windows[u]
            lo_v, hi_v = windows[v]
            if hi_u < lo_v:
                earlier, later = u, v
            elif hi_v < lo_u:
                earlier, later = v, u
            else:
                continue
            undirected.append((earlier, later))
            if T[later][earlier]:
                forced_back.append((later, earlier))
            else:
                forced_forward.append((earlier, later))
    return {
        "forced_back": forced_back,
        "forced_forward": forced_forward,
        "undirected_edges": undirected,
        "n_forced_pairs": len(undirected),
    }


def longest_path_length(edges: list[tuple[int, int]], n: int) -> int:
    """Length (#edges) of the longest *simple path* in an undirected graph.

    Brute force.  Acceptable for n <= 20 with sparse graphs.
    """
    adj: dict[int, list[int]] = {i: [] for i in range(n)}
    for u, v in edges:
        a = min(u, v)
        b = max(u, v)
        if b not in adj[a]:
            adj[a].append(b)
            adj[b].append(a)

    best = 0

    def dfs(cur: int, visited: int, length: int) -> None:
        nonlocal best
        if length > best:
            best = length
        for nxt in adj[cur]:
            bit = 1 << nxt
            if not (visited & bit):
                dfs(nxt, visited | bit, length + 1)

    for start in range(n):
        dfs(start, 1 << start, 0)
    return best


def is_linear_forest(edges: list[tuple[int, int]], n: int) -> bool:
    """Check whether the undirected graph (edges, n vertices) is a linear forest."""
    adj: dict[int, list[int]] = {i: [] for i in range(n)}
    for u, v in edges:
        a = min(u, v)
        b = max(u, v)
        if b not in adj[a]:
            adj[a].append(b)
            adj[b].append(a)
    # max degree <= 2
    if any(len(nbrs) > 2 for nbrs in adj.values()):
        return False
    # acyclic via DFS
    color = [0] * n  # 0 white, 1 gray, 2 black
    for s in range(n):
        if color[s] != 0:
            continue
        stack: list[tuple[int, int]] = [(s, -1)]
        color[s] = 1
        while stack:
            u, parent = stack.pop()
            for v in adj[u]:
                if v == parent:
                    continue
                if color[v] == 1:
                    return False
                if color[v] == 0:
                    color[v] = 1
                    stack.append((v, u))
            color[u] = 2
    return True


def random_tournament(n: int, rng: random.Random) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.getrandbits(1):
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def transitive_noise_tournament(n: int, p: float, rng: random.Random) -> list[list[int]]:
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                T[j][i] = 1
            else:
                T[i][j] = 1
    return T


def stretched_in_degree_tournament(n: int, rng: random.Random) -> list[list[int]]:
    """Construct T with in-degree sequence ~ (0, n//2, 0, n//2, ...) so that
    consecutive ranks have in-degree gap >= n//2 - 1 >= 5.

    Strategy: arrange the n vertices in groups G_0, G_1, ... so that for
    vertex v in group G_k, d^-(v) is roughly  k * (n // m).  We
    realise this by interleaving "dense" and "sparse" vertices.
    """
    # As a concrete construction, start from a transitive tournament
    # but pin specific vertices to have extremal in-degree.
    T = [[0] * n for _ in range(n)]
    # Build target in-degrees: try to alternate low and high.
    targets = []
    half = n // 2
    for k in range(n):
        targets.append(0 if k % 2 == 0 else min(n - 1, half + (k // 2)))
    targets.sort()
    # Realise the score sequence by a greedy construction (Fulkerson).
    score_seq = targets[:]
    available = list(range(n))
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    # Initialise as transitive then perturb to match in-degree targets.
    for i, j in pairs:
        T[i][j] = 1
    deg = indegrees(T)
    # Random local flips toward targets.
    for _ in range(8 * n * n):
        worst = max(range(n), key=lambda v: abs(deg[v] - score_seq[v]))
        diff = deg[worst] - score_seq[worst]
        if diff == 0:
            break
        if diff > 0:
            # too many incoming; flip one incoming to outgoing
            cands = [u for u in range(n) if T[u][worst]]
            if not cands:
                break
            u = rng.choice(cands)
            T[u][worst] = 0
            T[worst][u] = 1
        else:
            cands = [u for u in range(n) if T[worst][u]]
            if not cands:
                break
            u = rng.choice(cands)
            T[worst][u] = 0
            T[u][worst] = 1
        deg = indegrees(T)
    return T


def search_max_forced_path(
    family: str,
    n: int,
    trials: int,
    seed: int,
    p: float = 0.05,
) -> dict:
    rng = random.Random(seed)
    best_length = -1
    best_T = None
    best_back: list[tuple[int, int]] = []
    best_und: list[tuple[int, int]] = []
    cumulative_back_lengths: list[int] = []
    is_lf_count = 0
    t0 = time.time()
    for _ in range(trials):
        if family == "uniform":
            T = random_tournament(n, rng)
        elif family == "skew":
            T = transitive_noise_tournament(n, p, rng)
        elif family == "stretched":
            T = stretched_in_degree_tournament(n, rng)
        else:
            raise ValueError(f"unknown family {family!r}")
        rel = forced_relations(T)
        back_edges = [(u, v) for (u, v) in rel["forced_back"]]
        und_edges = list(rel["undirected_edges"])
        length = longest_path_length(back_edges, n)
        cumulative_back_lengths.append(length)
        if is_linear_forest(back_edges, n):
            is_lf_count += 1
        if length > best_length:
            best_length = length
            best_T = T
            best_back = back_edges
            best_und = und_edges
    elapsed = time.time() - t0
    return {
        "family": family,
        "n": n,
        "trials": trials,
        "seed": seed,
        "p_noise": p if family == "skew" else None,
        "seconds": round(elapsed, 3),
        "best_forced_back_path_length": best_length,
        "best_T": best_T,
        "best_forced_back_edges": best_back,
        "best_undirected_forced_edges": best_und,
        "linear_forest_fraction": is_lf_count / max(trials, 1),
        "score_bound_max_path": 2 * ((n - 1) // 5),
        "histogram": {
            f"length_{k}": cumulative_back_lengths.count(k)
            for k in range(0, max(cumulative_back_lengths) + 1)
        } if cumulative_back_lengths else {},
    }


def theoretical_max_forced_path(n: int) -> int:
    """Hard score-span bound on the longest forced path in H.

    A path v_0 - v_1 - ... - v_k in H means consecutive in-degrees
    differ by >= 5.  Standard sign-alternation argument: the in-degrees
    must lie in [0, n-1] of total span n - 1 and reach >= 5*ceil(k/2)
    extremes; hence k <= 2*floor((n-1)/5).
    """
    return 2 * ((n - 1) // 5)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=12)
    parser.add_argument("--trials", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260527)
    parser.add_argument("--family", choices=["uniform", "skew", "stretched"], default="skew")
    parser.add_argument("--p", type=float, default=0.05, help="noise probability for skew family")
    parser.add_argument("--sweep", action="store_true",
                        help="run all families across n in {8, 10, 12, 14, 16}")
    parser.add_argument("--out", help="output JSON file")
    args = parser.parse_args()

    if args.sweep:
        results = []
        for n in (8, 10, 12, 14, 16, 20):
            for family in ("uniform", "skew", "stretched"):
                trials = args.trials // 4 if n > 14 else args.trials
                p = args.p
                if family == "skew":
                    for p_val in (0.02, 0.05, 0.1):
                        r = search_max_forced_path(family, n, trials, args.seed, p_val)
                        r["theoretical_max"] = theoretical_max_forced_path(n)
                        # don't carry the full tournament in the sweep
                        r.pop("best_T", None)
                        r.pop("best_forced_back_edges", None)
                        r.pop("best_undirected_forced_edges", None)
                        results.append(r)
                else:
                    r = search_max_forced_path(family, n, trials, args.seed, p)
                    r["theoretical_max"] = theoretical_max_forced_path(n)
                    r.pop("best_T", None)
                    r.pop("best_forced_back_edges", None)
                    r.pop("best_undirected_forced_edges", None)
                    results.append(r)
        out = {"mode": "sweep", "trials_per_cell": args.trials, "results": results}
    else:
        out = search_max_forced_path(args.family, args.n, args.trials, args.seed, args.p)
        out["theoretical_max"] = theoretical_max_forced_path(args.n)

    text = json.dumps(out, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
            f.write("\n")
    print(text)


if __name__ == "__main__":
    main()
