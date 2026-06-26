#!/usr/bin/env python3
"""
Attack Step 1b of the 3-connected-wheel route.

Target under review:

    3-connected 2-extremal  =>  the digon forest F_D is connected.

This script tests the stronger separator-only hope

    disconnected F_D + U(D) 3-connected is impossible,

and shows it is false even with most of the 2-extremal structure present.  The
missing condition is exactly the colouring obstruction chi_vec(D)=3.

Two near-miss families are printed:
  * the cyclic regular tournament T5: F_D empty, U 4-connected, MC=0, lambda=2,
    Eulerian and strong, but chi_vec=2;
  * two disjoint digon 3-stars with a balanced single-arc cycle cover on the
    six leaves.  Many members have U 3-connected, MC=0, lambda=2 and disconnected
    F_D; all such members are chi_vec=2.

So Step 1b should be attacked as a colouring lemma:

    U(D) 3-connected + lambda<=2 + F_D disconnected  =>  D is 2-dicolourable,

not as a bare graph-separator lemma.
"""

import itertools
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from seam_invariant import mixed_2_cuts, split_digons_singles  # noqa: E402


def underlying_edges(arcs):
    return {frozenset((a, b)) for a, b in arcs if a != b}


def vertex_connectivity(n, arcs):
    """Brute-force vertex connectivity for small graphs."""
    edges = underlying_edges(arcs)

    def connected_after(removed):
        removed = set(removed)
        verts = [v for v in range(n) if v not in removed]
        if not verts:
            return True
        adj = {v: set() for v in verts}
        for e in edges:
            a, b = tuple(e)
            if a in removed or b in removed:
                continue
            adj[a].add(b)
            adj[b].add(a)
        seen = {verts[0]}
        stack = [verts[0]]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        return len(seen) == len(verts)

    for r in range(n):
        for removed in itertools.combinations(range(n), r):
            if not connected_after(removed):
                return r
    return n - 1


def f_components_and_bipartition(n, digon_edges):
    adj = {v: set() for v in range(n)}
    for e in digon_edges:
        a, b = tuple(e)
        adj[a].add(b)
        adj[b].add(a)
    comp = [-1] * n
    bit = [0] * n
    comps = []
    for s in range(n):
        if comp[s] != -1:
            continue
        cid = len(comps)
        comps.append([])
        comp[s] = cid
        stack = [s]
        while stack:
            x = stack.pop()
            comps[cid].append(x)
            for y in adj[x]:
                if comp[y] == -1:
                    comp[y] = cid
                    bit[y] = bit[x] ^ 1
                    stack.append(y)
                elif bit[y] == bit[x]:
                    raise ValueError("digon graph is not bipartite/forest-like")
    return comp, bit, comps


def has_monochromatic_single_dicycle(n, single_arcs, colour):
    for c in (0, 1):
        verts = {v for v in range(n) if colour[v] == c}
        adj = {v: [] for v in verts}
        for a, b in single_arcs:
            if a in verts and b in verts:
                adj[a].append(b)
        state = {}

        def dfs(x):
            state[x] = 1
            for y in adj[x]:
                if state.get(y) == 1:
                    return True
                if state.get(y, 0) == 0 and dfs(y):
                    return True
            state[x] = 2
            return False

        for v in verts:
            if state.get(v, 0) == 0 and dfs(v):
                return True
    return False


def forest_colouring_witness(n, arcs):
    """Return a proper F_D 2-colouring with no monochromatic single dicycle,
    if one exists.  By the colouring theorem, such a witness proves chi_vec<=2."""
    digons, singles = split_digons_singles(n, arcs)
    comp, bit, comps = f_components_and_bipartition(n, digons)
    for flips in itertools.product((0, 1), repeat=len(comps)):
        colour = [bit[v] ^ flips[comp[v]] for v in range(n)]
        if not has_monochromatic_single_dicycle(n, singles, colour):
            return colour
    return None


def cyclic_tournament_5():
    n = 5
    arcs = frozenset(
        (i, j)
        for i in range(n)
        for j in range(n)
        if i != j and ((j - i) % n in (1, 2))
    )
    return n, arcs


def two_star_cycle_cover(outmap):
    n = 8
    arcs = set()
    for h, leaves in [(0, [2, 3, 4]), (1, [5, 6, 7])]:
        for leaf in leaves:
            arcs.add((h, leaf))
            arcs.add((leaf, h))
    for a, b in outmap.items():
        arcs.add((a, b))
    return n, frozenset(arcs)


def summarise(name, n, arcs):
    digons, singles = split_digons_singles(n, arcs)
    witness = forest_colouring_witness(n, arcs)
    return {
        "name": name,
        "n": n,
        "kappa_U": vertex_connectivity(n, arcs),
        "digon_components": len(f_components_and_bipartition(n, digons)[2]),
        "digon_edges": len(digons),
        "single_arcs": len(singles),
        "eulerian_min2": H.is_eulerian_deg(n, arcs),
        "strong": H.is_strong(n, arcs),
        "lambda_repo": H.lambda_D(n, arcs),
        "MC": len(mixed_2_cuts(n, arcs)),
        "chi_vec": H.chi_vec(n, arcs),
        "is_2extremal": H.is_2extremal(n, arcs),
        "forest_2colouring_witness": witness,
    }


def print_summary(row):
    print(f"# {row['name']}")
    for key in [
        "n", "kappa_U", "digon_components", "digon_edges", "single_arcs",
        "eulerian_min2", "strong", "lambda_repo", "MC", "chi_vec",
        "is_2extremal", "forest_2colouring_witness",
    ]:
        print(f"  {key}: {row[key]}")


def sweep_two_stars():
    leaves = [2, 3, 4, 5, 6, 7]
    counts = Counter()
    good_near_misses = []
    for perm in itertools.permutations(leaves):
        outmap = dict(zip(leaves, perm))
        if any(a == b for a, b in outmap.items()):
            continue
        # A single 2-cycle would be a digon, not two single arcs.
        if any(outmap.get(b) == a for a, b in outmap.items()):
            continue
        n, arcs = two_star_cycle_cover(outmap)
        row = summarise("two-star", n, arcs)
        key = (
            row["kappa_U"],
            row["lambda_repo"],
            row["MC"],
            row["chi_vec"],
            row["is_2extremal"],
        )
        counts[key] += 1
        if row["kappa_U"] >= 3 and row["lambda_repo"] <= 2 and row["MC"] == 0:
            good_near_misses.append((outmap, row))

    print("# two disjoint digon 3-stars + balanced single cycle-cover sweep")
    print("# key = (kappa_U, lambda_repo, MC-count, chi_vec, is_2extremal)")
    for key, count in sorted(counts.items()):
        print(f"  {key}: {count}")
    print(f"# near-misses with kappa>=3, lambda<=2, MC=0: {len(good_near_misses)}")
    print("# all near-misses are killed by chi_vec=2:",
          all(row["chi_vec"] == 2 and not row["is_2extremal"]
              for _, row in good_near_misses))
    if good_near_misses:
        outmap, row = good_near_misses[0]
        print("# first near-miss outmap:", dict(sorted(outmap.items())))
        print_summary(row)


def main():
    print_summary(summarise("cyclic regular tournament T5", *cyclic_tournament_5()))
    print()
    sweep_two_stars()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
