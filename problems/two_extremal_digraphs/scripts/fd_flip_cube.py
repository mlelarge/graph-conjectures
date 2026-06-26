#!/usr/bin/env python3
"""
Flip-cube audit for the Step 1b' colouring target.

For a digraph whose digon graph F_D is a forest, every proper 2-colouring of F_D
is obtained by independently flipping the bipartition of each component.  A
single-arc dicycle is monochromatic on a subset of those flip assignments.  Thus
`chi_vec(D)=3` is equivalent to:

    the union of the bad flip sets of all single-arc dicycles covers the cube.

This script makes that formulation explicit.  It reports:
  * near-misses from `step1b_fd_connectivity.py`, where U(D) can be 3-connected,
    MC=0, lambda=2, and F_D disconnected, but the bad sets do NOT cover the cube;
  * genuine truth-set members L_3..L_7, where every non-SOC member is covered
    exactly as expected from chi_vec=3.

The output is intended to guide the remaining proof of Step 1b':

    U(D) 3-connected + repo-lambda<=2 + F_D disconnected
        => some flip assignment avoids every monochromatic single dicycle.
"""

import itertools
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from seam_invariant import split_digons_singles, mixed_2_cuts  # noqa: E402
from step1b_fd_connectivity import (  # noqa: E402
    two_star_cycle_cover,
    cyclic_tournament_5,
    vertex_connectivity,
)


def f_components_and_bits(n, digon_edges):
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
                    return None, None, None
    return comp, bit, comps


def simple_directed_cycles(n, arcs):
    """Enumerate simple directed cycles, deduped by choosing the minimum vertex
    as the start.  Good enough for the small digraphs used in this audit."""
    adj = {v: [] for v in range(n)}
    for a, b in arcs:
        adj[a].append(b)
    for v in adj:
        adj[v].sort()

    cycles = []
    for start in range(n):
        stack = [(start, [start], {start})]
        while stack:
            x, path, seen = stack.pop()
            for y in adj[x]:
                if y == start and len(path) >= 2:
                    cycles.append(tuple(path))
                elif y not in seen and y >= start:
                    stack.append((y, path + [y], seen | {y}))
    return cycles


def cycle_bad_partials(cycle, comp, bit, k):
    """Return the two possible partial flip assignments that make `cycle`
    monochromatic, one for final colour 0 and one for final colour 1.  A partial
    is represented as frozenset((component, value))."""
    out = []
    for colour in (0, 1):
        req = {}
        ok = True
        for v in cycle:
            c = comp[v]
            val = colour ^ bit[v]
            old = req.get(c)
            if old is not None and old != val:
                ok = False
                break
            req[c] = val
        if ok:
            out.append(frozenset(req.items()))
    return tuple(out)


def partial_contains(mask, partial):
    return all(((mask >> c) & 1) == val for c, val in partial)


def analyse(n, arcs):
    digons, singles = split_digons_singles(n, arcs)
    comp, bit, comps = f_components_and_bits(n, digons)
    if comp is None:
        return {"forest": False}
    k = len(comps)
    cycles = simple_directed_cycles(n, singles)
    partials = []
    for cyc in cycles:
        for p in cycle_bad_partials(cyc, comp, bit, k):
            partials.append((cyc, p))

    if k > 22:
        raise ValueError(f"flip cube too large for brute-force audit: 2^{k}")
    bad = set()
    for mask in range(1 << k):
        if any(partial_contains(mask, p) for _, p in partials):
            bad.add(mask)
    uncovered = [mask for mask in range(1 << k) if mask not in bad]
    return {
        "forest": True,
        "k": k,
        "digon_edges": len(digons),
        "single_arcs": len(singles),
        "single_dicycles": len(cycles),
        "bad_partials": len(partials),
        "covered": not uncovered,
        "covered_count": len(bad),
        "cube_size": 1 << k,
        "first_uncovered": uncovered[0] if uncovered else None,
        "first_uncovered_colouring": (
            [bit[v] ^ ((uncovered[0] >> comp[v]) & 1) for v in range(n)]
            if uncovered else None
        ),
        "partial_size_hist": Counter(len(p) for _, p in partials),
    }


def row(name, n, arcs):
    a = analyse(n, arcs)
    if not a["forest"]:
        return {"name": name, "forest": False}
    return {
        "name": name,
        "n": n,
        "kappa_U": vertex_connectivity(n, arcs),
        "lambda_repo": H.lambda_D(n, arcs),
        "MC": len(mixed_2_cuts(n, arcs)),
        "chi_vec": H.chi_vec(n, arcs),
        "is_2extremal": H.is_2extremal(n, arcs),
        **a,
    }


def print_row(r):
    print(f"# {r['name']}")
    if not r.get("forest"):
        print("  F_D is not a forest")
        return
    keys = [
        "n", "kappa_U", "lambda_repo", "MC", "chi_vec", "is_2extremal",
        "k", "digon_edges", "single_arcs", "single_dicycles", "bad_partials",
        "covered_count", "cube_size", "covered", "first_uncovered_colouring",
        "partial_size_hist",
    ]
    for key in keys:
        print(f"  {key}: {r[key]}")


def load_truth(max_n=7):
    for nn in range(3, max_n + 1):
        path = os.path.join(ROOT, "data", f"L_{nn}.json")
        if not os.path.exists(path):
            continue
        for idx, obj in enumerate(json.load(open(path))):
            n = obj["n"]
            arcs = frozenset(tuple(a) for a in obj["arcs"])
            yield f"L{nn}.{idx}", n, arcs


def two_star_near_miss_rows():
    leaves = [2, 3, 4, 5, 6, 7]
    for perm in itertools.permutations(leaves):
        outmap = dict(zip(leaves, perm))
        if any(a == b for a, b in outmap.items()):
            continue
        if any(outmap.get(b) == a for a, b in outmap.items()):
            continue
        n, arcs = two_star_cycle_cover(outmap)
        r = row("two-star", n, arcs)
        if r["kappa_U"] >= 3 and r["lambda_repo"] <= 2 and r["MC"] == 0:
            yield outmap, r


def two_star_arcs(a_leaves, b_leaves, outmap):
    n = 2 + a_leaves + b_leaves
    left = list(range(2, 2 + a_leaves))
    right = list(range(2 + a_leaves, n))
    arcs = set()
    for h, leaves in [(0, left), (1, right)]:
        for leaf in leaves:
            arcs.add((h, leaf))
            arcs.add((leaf, h))
    arcs.update(outmap.items())
    return n, frozenset(arcs)


def two_star_flip_sweep(a_leaves, b_leaves):
    leaves = list(range(2, 2 + a_leaves + b_leaves))
    covered_class = Counter()
    covered_examples = {}
    total = covered = danger = 0
    uncovered_hist = Counter()
    for perm in itertools.permutations(leaves):
        outmap = dict(zip(leaves, perm))
        if any(a == b for a, b in outmap.items()):
            continue
        # A single 2-cycle would be a digon, not two single arcs.
        if any(outmap.get(b) == a for a, b in outmap.items()):
            continue
        n, arcs = two_star_arcs(a_leaves, b_leaves, outmap)
        total += 1
        a = analyse(n, arcs)
        uncovered_hist[a["cube_size"] - a["covered_count"]] += 1
        if not a["covered"]:
            continue
        covered += 1
        key = (
            vertex_connectivity(n, arcs),
            H.lambda_D(n, arcs),
            len(mixed_2_cuts(n, arcs)),
            H.chi_vec(n, arcs),
            H.is_2extremal(n, arcs),
        )
        covered_class[key] += 1
        covered_examples.setdefault(key, dict(sorted(outmap.items())))
        if key[0] >= 3 and key[1] <= 2 and key[2] == 0:
            danger += 1
    return {
        "total": total,
        "covered": covered,
        "danger": danger,
        "uncovered_hist": uncovered_hist,
        "covered_class": covered_class,
        "covered_examples": covered_examples,
    }


def main():
    print("# canonical near-misses")
    print_row(row("cyclic regular tournament T5", *cyclic_tournament_5()))
    first = next(two_star_near_miss_rows())
    print("# first two-star near-miss outmap:", dict(sorted(first[0].items())))
    print_row(first[1])

    near = list(two_star_near_miss_rows())
    print()
    print("# two-star near-miss aggregate")
    print(f"  near-misses: {len(near)}")
    print("  covered bad-cube instances:", sum(1 for _, r in near if r["covered"]))
    print("  all have an uncovered colouring:",
          all(not r["covered"] and r["chi_vec"] == 2 for _, r in near))
    print("  uncovered-count histogram:",
          dict(sorted(Counter(r["cube_size"] - r["covered_count"]
                              for _, r in near).items())))

    print()
    print("# larger two-star stress test: two digon 4-stars")
    stress = two_star_flip_sweep(4, 4)
    print(f"  layouts tested: {stress['total']}")
    print(f"  bad sets cover cube: {stress['covered']}")
    print(f"  covered layouts with kappa>=3, lambda<=2, MC=0: {stress['danger']}")
    print("  uncovered-count histogram:",
          dict(sorted(stress["uncovered_hist"].items())))
    print("  covered-layout classification")
    print("  # key = (kappa_U, lambda_repo, MC-count, chi_vec, is_2extremal)")
    for key, count in sorted(stress["covered_class"].items()):
        print(f"    {key}: {count}  ex={stress['covered_examples'][key]}")

    print()
    print("# truth set L3..L7, excluding symmetric odd cycles")
    counts = Counter()
    disconnected = []
    for name, n, arcs in load_truth(7):
        if H.is_symmetric_odd_cycle(n, arcs):
            continue
        r = row(name, n, arcs)
        key = (r["covered"], r["chi_vec"], r["k"] > 1, r["kappa_U"] >= 3)
        counts[key] += 1
        if r["k"] > 1:
            disconnected.append(r)
    print("# key = (bad sets cover cube, chi_vec, F_D disconnected, U 3-connected)")
    for key, count in sorted(counts.items()):
        print(f"  {key}: {count}")
    print("  disconnected F_D truth members:", len(disconnected))
    print("  disconnected and covered:", sum(1 for r in disconnected if r["covered"]))
    print("  disconnected and U 3-connected:",
          sum(1 for r in disconnected if r["kappa_U"] >= 3))
    print("  first disconnected truth member:")
    if disconnected:
        print_row(disconnected[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
