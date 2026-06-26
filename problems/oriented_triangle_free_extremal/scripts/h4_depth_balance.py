"""H4 depth-balancing online orientation (ground plan).

Build the triangle-free PROCESS graph in BUILD ORDER (the online filtration),
orient each arriving edge into the deeper endpoint (point into the endpoint with
larger longest-path-ending depth), keeping D acyclic. Compute EXACT
core.acyclic_number a*; report a*/(sqrt(n) log n).

CONFIRM if a*/(sqrt n log n) declines monotonically toward 0 (<=0.95 by n=60).
KILL if it stays flat or rises (>= ~1.0, not decreasing) vs random floor ~1.07.
"""
import os
import sys, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def triangle_free_process_buildorder(n, m_cap, seed):
    """Like lit_reduction_test.triangle_free_process but returns edges in BUILD
    ORDER (the genuine online filtration), not sorted."""
    import random
    rng = random.Random(seed)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    adj = [set() for _ in range(n)]
    edges = []  # build order
    for (u, v) in pairs:
        if len(edges) >= m_cap:
            break
        if adj[u] & adj[v]:
            continue
        edges.append((u, v))
        adj[u].add(v)
        adj[v].add(u)
    return n, edges


def depth_balance_orient(n, edges_in_build_order):
    """Online depth-balancing: orient each edge into the deeper endpoint.
    depth[v] = longest directed path ending at v. Point a->b with b the deeper
    endpoint, then propagate b's new depth forward."""
    depth = [0] * n
    succ = [[] for _ in range(n)]
    arcs = []
    for (u, v) in edges_in_build_order:
        if depth[u] <= depth[v]:
            a, b = u, v
        else:
            a, b = v, u  # a->b, point into deeper endpoint
        arcs.append((a, b))
        succ[a].append(b)
        if depth[a] + 1 > depth[b]:
            depth[b] = depth[a] + 1
            stack = [b]
            while stack:
                x = stack.pop()
                for y in succ[x]:
                    if depth[x] + 1 > depth[y]:
                        depth[y] = depth[x] + 1
                        stack.append(y)
    return arcs


def main():
    print(f"{'n':>4} {'a*':>4} {'a*/(sqrt n logn)':>17}", flush=True)
    rows = []
    for n in [20, 30, 40, 50, 60]:
        best = n
        for c in [1, 1.5, 2, 2.5, 3]:
            m_cap = int(c * math.sqrt(n) * n / 2)
            for s in range(4):
                _, edges = triangle_free_process_buildorder(
                    n, m_cap, seed=1000 * int(c * 10) + s + n)
                arcs = depth_balance_orient(n, edges)
                assert core.is_oriented(arcs), "not oriented"
                assert core.is_triangle_free(n, arcs), "not triangle-free"
                assert core.is_acyclic(n, arcs), "rule did not yield acyclic D"
                a = core.acyclic_number(n, arcs)
                if a < best:
                    best = a
        sc = math.sqrt(n) * math.log(n)
        print(f"{n:>4} {best:>4} {best / sc:>17.4f}", flush=True)
        rows.append((n, best, best / sc))

    print("\n=== RANDOM FLOOR (G4): n=20->1.045, n=30->1.074, n=40->1.072 ===")
    print("=== ratios ===")
    for n, a, r in rows:
        print(f"n={n}: a*/(sqrt n logn)={r:.4f}", flush=True)


if __name__ == "__main__":
    main()
