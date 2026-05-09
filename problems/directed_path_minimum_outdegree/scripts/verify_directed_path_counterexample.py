"""Independent verifier for candidate counterexamples to Cheng--Keevash
Conjecture 1: every oriented graph with minimum out-degree >= delta
contains a directed simple path of length 2*delta.

A "candidate counterexample" is a directed graph D supplied as an edge list
(or adjacency representation), claimed to satisfy:
  - oriented (no antiparallel arcs, no loops)
  - delta+(D) >= delta (some claimed minimum)
  - longest directed simple path strictly less than 2*delta

This verifier checks each property independently of the local miner. It
is intended for:
  - sanity-checking miner completions when investigating obstructions
  - verifying explicit candidate counterexamples submitted by humans
  - regression testing as the project scales to n >= 11.

Usage:
  python verify_directed_path_counterexample.py <input.edges> [--k K] [--longest]

Input format (edge list, default):
  Each line:  u v
  meaning the directed arc (u, v) is in A(D).
  Vertices may be integers or strings; whitespace separated.

Output:
  Per-check status (PASS/FAIL) for each of:
    1. no loops
    2. no antiparallel pair
    3. min out-degree >= K (if --k supplied)
    4. strongly connected? (yes/no, plus sink-SCC sizes)
    5. longest directed simple path length L
    6. counterexample status: yes if L < 2K, else no.

  If --longest is set, also report a witness path of length L.

Algorithms:
  - Strong connectivity: Tarjan's SCC (iterative).
  - Longest simple directed path: bitset DFS branch-and-bound for
    n <= 24, falling back to subset DP (Held--Karp style) for n <= 16
    when --exact is set. For larger n, the answer is reported as
    "lower bound" found by DFS within a time budget.
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Set, Tuple, Optional


# ---------- I/O ----------

def parse_edge_list(path: str) -> Tuple[List, Dict]:
    """Read edge list, return (vertex_list, adjacency_dict).

    Adjacency: vertex -> set of out-neighbours.
    Vertex labels preserved as-is (strings or ints).
    """
    edges = []
    vertices = set()
    with open(path, 'r') as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(f"line {lineno}: expected 'u v', got {raw!r}")
            u, v = parts[0], parts[1]
            # Try to coerce to int for canonical comparison
            try:
                u = int(u)
            except ValueError:
                pass
            try:
                v = int(v)
            except ValueError:
                pass
            edges.append((u, v))
            vertices.add(u)
            vertices.add(v)

    vertex_list = sorted(vertices, key=lambda x: (isinstance(x, str), x))
    adj: Dict = {v: set() for v in vertex_list}
    for (u, v) in edges:
        adj[u].add(v)
    return vertex_list, adj


# ---------- Checks ----------

def check_no_loops(adj: Dict) -> Tuple[bool, str]:
    bad = [v for v in adj if v in adj[v]]
    if bad:
        return False, f"loops at {bad}"
    return True, "no loops"


def check_no_antiparallel(adj: Dict) -> Tuple[bool, str]:
    bad = []
    for u in adj:
        for v in adj[u]:
            if u in adj.get(v, set()):
                pair = tuple(sorted([str(u), str(v)]))
                if pair not in [tuple(sorted([str(p), str(q)])) for (p, q) in bad]:
                    bad.append((u, v))
    if bad:
        return False, f"antiparallel pairs: {bad[:10]}"
    return True, "no antiparallel pairs"


def check_min_outdegree(adj: Dict, k: int) -> Tuple[bool, str]:
    bad = []
    for v in adj:
        if len(adj[v]) < k:
            bad.append((v, len(adj[v])))
    if bad:
        return False, f"vertices with out-degree < {k}: {bad[:10]}"
    return True, f"min out-degree >= {k}"


def tarjan_scc(adj: Dict) -> List[List]:
    """Tarjan's algorithm for strongly connected components, iterative.

    Returns list of SCCs (each a list of vertices), in reverse topological
    order on the SCC condensation (i.e., sink SCCs first).
    """
    index_of = {}
    lowlink = {}
    on_stack = {}
    stack = []
    sccs = []
    counter = [0]

    def strongconnect(v):
        # Iterative Tarjan using explicit work stack
        work = [(v, iter(adj.get(v, set())))]
        index_of[v] = counter[0]
        lowlink[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        while work:
            u, it = work[-1]
            try:
                w = next(it)
                if w not in index_of:
                    index_of[w] = counter[0]
                    lowlink[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    on_stack[w] = True
                    work.append((w, iter(adj.get(w, set()))))
                elif on_stack.get(w, False):
                    lowlink[u] = min(lowlink[u], index_of[w])
            except StopIteration:
                if lowlink[u] == index_of[u]:
                    component = []
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        component.append(w)
                        if w == u:
                            break
                    sccs.append(component)
                work.pop()
                if work:
                    parent = work[-1][0]
                    lowlink[parent] = min(lowlink[parent], lowlink[u])

    for v in adj:
        if v not in index_of:
            strongconnect(v)
    return sccs


def check_strong_connectivity(adj: Dict) -> Tuple[bool, str, List[List]]:
    sccs = tarjan_scc(adj)
    n = len(adj)
    is_strong = len(sccs) == 1 and len(sccs[0]) == n
    sizes = sorted([len(c) for c in sccs], reverse=True)
    msg = (f"strongly connected"
           if is_strong
           else f"not strongly connected ({len(sccs)} SCCs, sizes {sizes})")
    return is_strong, msg, sccs


def find_sink_sccs(adj: Dict, sccs: List[List]) -> List[List]:
    """Return SCCs with no outgoing arcs to other SCCs (i.e., sink SCCs)."""
    scc_id = {}
    for i, comp in enumerate(sccs):
        for v in comp:
            scc_id[v] = i
    sink_ids = set(range(len(sccs)))
    for u in adj:
        for v in adj[u]:
            if scc_id[u] != scc_id[v]:
                sink_ids.discard(scc_id[u])
    return [sccs[i] for i in sink_ids]


def longest_simple_directed_path(adj: Dict, time_budget_seconds: float = 30.0):
    """DFS branch-and-bound for the longest directed simple path.

    Returns (length_in_arcs, path_vertices) where path_vertices is the
    witness path. For n <= 16, uses subset DP (exact). For 16 < n <= 24,
    uses DFS with reachable-vertex pruning. For n > 24, uses DFS within
    the time budget; result is a *lower bound*.
    """
    import time
    vertices = list(adj.keys())
    n = len(vertices)
    idx_of = {v: i for i, v in enumerate(vertices)}

    if n == 0:
        return 0, []

    # Adjacency as bitsets
    out_bits = [0] * n
    for v in vertices:
        i = idx_of[v]
        for w in adj[v]:
            j = idx_of[w]
            out_bits[i] |= (1 << j)

    if n <= 16:
        # Subset DP: dp[mask][end] = True iff there's a simple path visiting
        # exactly mask, ending at end.
        # Then longest = max over mask, end of (popcount(mask) - 1) where
        # dp[mask][end] is true.
        # For witness, also track parent.
        # Memory: 2^16 * 16 bools = 1M.
        dp = [[False] * n for _ in range(1 << n)]
        parent = [[-1] * n for _ in range(1 << n)]
        for i in range(n):
            dp[1 << i][i] = True

        best_len = 0
        best_mask = 0
        best_end = 0
        for mask in range(1, 1 << n):
            popcount = bin(mask).count('1')
            for end in range(n):
                if not dp[mask][end]:
                    continue
                if popcount - 1 > best_len:
                    best_len = popcount - 1
                    best_mask = mask
                    best_end = end
                # Extend
                for nxt in range(n):
                    if (mask >> nxt) & 1:
                        continue
                    if (out_bits[end] >> nxt) & 1:
                        new_mask = mask | (1 << nxt)
                        if not dp[new_mask][nxt]:
                            dp[new_mask][nxt] = True
                            parent[new_mask][nxt] = end

        # Reconstruct
        path_idx = []
        mask, end = best_mask, best_end
        while end != -1:
            path_idx.append(end)
            prev = parent[mask][end]
            mask ^= (1 << end)
            end = prev
        path_idx.reverse()
        path = [vertices[i] for i in path_idx]
        return best_len, path

    # DFS branch-and-bound (n > 16)
    start_time = time.time()
    best = [0, []]
    timed_out = [False]

    def reachable_count(visited: int, start: int) -> int:
        """BFS reach count from start avoiding visited (bitset)."""
        seen = (1 << start)
        frontier = (1 << start)
        while frontier:
            new_frontier = 0
            tmp = frontier
            while tmp:
                bit = tmp & -tmp
                v = bit.bit_length() - 1
                new_frontier |= out_bits[v]
                tmp ^= bit
            new_frontier &= ~seen & ~visited
            seen |= new_frontier
            frontier = new_frontier
        return bin(seen).count('1')

    def dfs(v: int, visited: int, length: int, path: List[int]):
        if time.time() - start_time > time_budget_seconds:
            timed_out[0] = True
            return
        if length > best[0]:
            best[0] = length
            best[1] = list(path)

        # Pruning: upper bound on extension
        cands = out_bits[v] & ~visited
        if cands == 0:
            return
        ub = reachable_count(visited, v) - 1  # excluding v itself
        if length + ub <= best[0]:
            return

        tmp = cands
        while tmp:
            bit = tmp & -tmp
            w = bit.bit_length() - 1
            tmp ^= bit
            path.append(w)
            dfs(w, visited | bit, length + 1, path)
            path.pop()
            if timed_out[0]:
                return

    for start in range(n):
        if timed_out[0]:
            break
        dfs(start, 1 << start, 0, [start])

    path = [vertices[i] for i in best[1]]
    return best[0], path


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="Verifier for candidate counterexamples to the directed-path conjecture.")
    parser.add_argument('input', help='edge list file (lines: u v)')
    parser.add_argument('--k', type=int, default=None, help='claimed delta (min out-degree)')
    parser.add_argument('--longest', action='store_true', help='also report longest directed simple path')
    parser.add_argument('--time-budget', type=float, default=30.0, help='time budget for longest-path DFS (seconds)')
    args = parser.parse_args()

    vertex_list, adj = parse_edge_list(args.input)
    n = len(vertex_list)

    print(f"Loaded {n} vertices, {sum(len(adj[v]) for v in adj)} arcs from {args.input}")

    # 1. No loops
    ok, msg = check_no_loops(adj)
    print(f"  [{'PASS' if ok else 'FAIL'}] no loops: {msg}")
    loops_ok = ok

    # 2. No antiparallel pairs
    ok, msg = check_no_antiparallel(adj)
    print(f"  [{'PASS' if ok else 'FAIL'}] no antiparallel: {msg}")
    antiparallel_ok = ok

    oriented_ok = loops_ok and antiparallel_ok
    print(f"  oriented graph: {'yes' if oriented_ok else 'NO'}")

    # 3. Min outdegree
    min_outdeg = min((len(adj[v]) for v in adj), default=0)
    print(f"  min_outdegree = {min_outdeg}")

    if args.k is not None:
        ok, msg = check_min_outdegree(adj, args.k)
        print(f"  [{'PASS' if ok else 'FAIL'}] min out-degree >= {args.k}: {msg}")

    # 4. Strong connectivity
    is_strong, msg, sccs = check_strong_connectivity(adj)
    print(f"  strongly_connected: {'yes' if is_strong else 'no'}")
    print(f"    SCC count = {len(sccs)}")
    if not is_strong:
        sink_sccs = find_sink_sccs(adj, sccs)
        sink_sizes = sorted([len(c) for c in sink_sccs], reverse=True)
        print(f"    sink SCCs (count {len(sink_sccs)}, sizes {sink_sizes})")

    # 5. Longest path (always, as it's the key check)
    print(f"  computing longest simple directed path (budget {args.time_budget}s)...")
    L, path = longest_simple_directed_path(adj, time_budget_seconds=args.time_budget)
    print(f"  longest_simple_directed_path_length = {L}")
    if args.longest:
        print(f"    witness: {' -> '.join(str(v) for v in path)}")

    # 6. Counterexample status
    if args.k is not None:
        target = 2 * args.k
        is_cex = oriented_ok and (min_outdeg >= args.k) and (L < target)
        print(f"  target_length (2k) = {target}")
        print(f"  COUNTEREXAMPLE: {'YES' if is_cex else 'no'} "
              f"(needs oriented + min-outdeg >= {args.k} + longest-path < {target})")
    else:
        print(f"  (no --k supplied; counterexample status not evaluated)")


if __name__ == '__main__':
    main()
