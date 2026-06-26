#!/usr/bin/env python3
"""
Finite casework aid for the R4 opposite-cross target.

R4 after the first correction:

    k=2, m=2, strong, Eulerian, U(D) 2-connected, repo-lambda<=2,
    opposite-cross full-cover mode  ==>  U(D) has a vertex 2-cut.

The previous shorthand "both cross parities are present" is too weak: a 4-vertex
K4 example has both parities but chi_vec=2 and no full cover.  This script keeps
the two notions separate:

  * arc-parities: parities appearing among the four cross arcs;
  * constraint-parities: parities of actual monochromatic cross dicycles.

It also enumerates labelled k=2,m=2 single-arc completions for small component
sizes.  The exhaustive default (n<=6) is fast; larger n is available for stress
testing but grows quickly.
"""

import argparse
import itertools
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from fd_cover_cuts import k2_profile, vertex_2_cuts  # noqa: E402
from fd_flip_cube import f_components_and_bits, simple_directed_cycles  # noqa: E402
from seam_invariant import split_digons_singles  # noqa: E402
from step1b_fd_connectivity import vertex_connectivity  # noqa: E402


def prufer_trees(labels):
    labels = tuple(labels)
    m = len(labels)
    if m == 1:
        yield frozenset()
        return
    if m == 2:
        yield frozenset([frozenset(labels)])
        return

    seen = set()
    for seq in itertools.product(labels, repeat=m - 2):
        deg = {x: 1 for x in labels}
        for x in seq:
            deg[x] += 1
        edges = []
        for x in seq:
            leaf = min(y for y in labels if deg[y] == 1)
            edges.append(frozenset((leaf, x)))
            deg[leaf] -= 1
            deg[x] -= 1
        rem = [y for y in labels if deg[y] == 1]
        edges.append(frozenset(rem))
        tree = frozenset(edges)
        if tree not in seen:
            seen.add(tree)
            yield tree


def bits_for_tree(labels, edges):
    if not labels:
        return {}
    adj = {v: set() for v in labels}
    for e in edges:
        a, b = tuple(e)
        adj[a].add(b)
        adj[b].add(a)
    bit = {labels[0]: 0}
    stack = [labels[0]]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in bit:
                bit[y] = bit[x] ^ 1
                stack.append(y)
    return bit


def internal_pairs(labels, tree_edges):
    tree = {frozenset(e) for e in tree_edges}
    return [
        (u, v)
        for u, v in itertools.combinations(labels, 2)
        if frozenset((u, v)) not in tree
    ]


def enum_internal_arcs(pairs, net, idx=0, rem=None):
    """Orient or omit each internal non-digon pair so final single-net is zero."""
    if rem is None:
        rem = {v: 0 for v in net}
        for u, v in pairs:
            rem[u] += 1
            rem[v] += 1
    if any(abs(net[v]) > rem[v] for v in net):
        return
    if idx == len(pairs):
        if all(value == 0 for value in net.values()):
            yield []
        return

    u, v = pairs[idx]
    rem[u] -= 1
    rem[v] -= 1

    yield from enum_internal_arcs(pairs, net, idx + 1, rem)

    net[u] += 1
    net[v] -= 1
    for rest in enum_internal_arcs(pairs, net, idx + 1, rem):
        yield [(u, v)] + rest
    net[u] -= 1
    net[v] += 1

    net[v] += 1
    net[u] -= 1
    for rest in enum_internal_arcs(pairs, net, idx + 1, rem):
        yield [(v, u)] + rest
    net[v] -= 1
    net[u] += 1

    rem[u] += 1
    rem[v] += 1


def add_digon_tree_arcs(arcs, tree_edges):
    for e in tree_edges:
        u, v = tuple(e)
        arcs.add((u, v))
        arcs.add((v, u))


def cross_arc_parities(n, arcs):
    digons, singles = split_digons_singles(n, arcs)
    comp, bit, comps = f_components_and_bits(n, digons)
    if comp is None or len(comps) != 2:
        return None
    out = []
    for u, v in singles:
        if comp[u] == comp[v]:
            continue
        if comp[u] == 0:
            delta = bit[u] ^ bit[v]
            direction = "0->1"
        else:
            delta = bit[v] ^ bit[u]
            direction = "1->0"
        out.append((u, v, direction, delta))
    return out


def print_example(title, n, arcs):
    prof = k2_profile(n, arcs)
    print(f"# {title}")
    print(f"  arcs={sorted(arcs)}")
    print(f"  cross_arc_parities={cross_arc_parities(n, arcs)}")
    print(f"  mode={prof['mode']} deltas={prof['deltas']} "
          f"covered={prof['covered']} chi={prof['chi_vec']}")
    print(f"  kappa_U={prof['kappa_U']} lambda_repo={prof['lambda_repo']} "
          f"strong={H.is_strong(n, arcs)} "
          f"eulerian_min2={H.is_eulerian_deg(n, arcs, min_deg=2)}")
    print(f"  vertex_2_cuts={vertex_2_cuts(n, arcs)}")
    print(f"  single_dicycles={simple_directed_cycles(n, split_digons_singles(n, arcs)[1])}")


def k4_both_arc_parity_not_cover():
    arcs = {
        (0, 1), (1, 0), (2, 3), (3, 2),
        (0, 2), (1, 3), (3, 0), (2, 1),
    }
    return 4, frozenset(arcs)


def enumerate_r4(max_n, search_only=False):
    counts = Counter()
    counterexample = None

    for n in range(4, max_n + 1):
        by_partition = Counter()
        for a in range(1, n // 2 + 1):
            b = n - a
            v0 = list(range(a))
            v1 = list(range(a, n))
            for t0 in prufer_trees(v0):
                p0 = internal_pairs(v0, t0)
                for t1 in prufer_trees(v1):
                    p1 = internal_pairs(v1, t1)
                    cross_pairs = [(u, v) for u in v0 for v in v1]
                    for fwd in itertools.combinations(cross_pairs, 2):
                        fset = set(fwd)
                        # A reverse single arc on the same pair would create a digon
                        # joining the two F_D components, so it is disallowed.
                        back_avail = [pair for pair in cross_pairs if pair not in fset]
                        for back_pairs in itertools.combinations(back_avail, 2):
                            net = {v: 0 for v in range(n)}
                            cross = []
                            for u, v in fwd:
                                cross.append((u, v))
                                net[u] += 1
                                net[v] -= 1
                            for u, v in back_pairs:
                                cross.append((v, u))
                                net[v] += 1
                                net[u] -= 1
                            if sum(net[v] for v in v0) != 0:
                                continue
                            if sum(net[v] for v in v1) != 0:
                                continue

                            for arcs0 in enum_internal_arcs(p0, {v: net[v] for v in v0}):
                                for arcs1 in enum_internal_arcs(p1, {v: net[v] for v in v1}):
                                    arcs = set(cross + arcs0 + arcs1)
                                    add_digon_tree_arcs(arcs, t0)
                                    add_digon_tree_arcs(arcs, t1)
                                    arcs = frozenset(arcs)

                                    if search_only:
                                        if not H.is_eulerian_deg(n, arcs, min_deg=2):
                                            continue
                                        if not H.is_strong(n, arcs):
                                            continue
                                        if vertex_connectivity(n, arcs) < 3:
                                            continue
                                        if H.lambda_D(n, arcs) > 2:
                                            continue
                                        prof = k2_profile(n, arcs)
                                        if prof and prof["mode"] == "opposite-cross":
                                            counterexample = (n, arcs)
                                            return counts, counterexample
                                        continue

                                    prof = k2_profile(n, arcs)
                                    if prof is None:
                                        continue
                                    key = (n, a, prof["mode"], prof["kappa_U"],
                                           prof["lambda_repo"], prof["chi_vec"],
                                           H.is_eulerian_deg(n, arcs, min_deg=2),
                                           H.is_strong(n, arcs))
                                    counts[key] += 1

                                    if prof["mode"] != "opposite-cross":
                                        continue
                                    if not H.is_eulerian_deg(n, arcs, min_deg=2):
                                        continue
                                    if not H.is_strong(n, arcs):
                                        continue
                                    if prof["lambda_repo"] > 2:
                                        continue
                                    if prof["kappa_U"] < 2:
                                        continue
                                    if prof["kappa_U"] >= 3:
                                        counterexample = (n, arcs)
                                        return counts, counterexample
            if search_only:
                print(f"  searched n={n} partition={a}+{b}", flush=True)
        if search_only:
            print(f"  completed n={n}", flush=True)
    return counts, counterexample


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-n", type=int, default=6,
                    help="maximum n for exhaustive labelled enumeration")
    ap.add_argument("--search-only", action="store_true",
                    help="only search for an R4 counterexample; skips census output")
    args = ap.parse_args(argv)

    print_example("both arc parities is not enough", *k4_both_arc_parity_not_cover())
    print()

    counts, counterexample = enumerate_r4(args.max_n, search_only=args.search_only)
    if args.search_only:
        print(f"# search-only k=2,m=2 opposite-cross through n={args.max_n}")
        if counterexample:
            print_example("R4 COUNTEREXAMPLE", *counterexample)
            return 1
        print("  R4 counterexamples found: 0")
        return 0
    print(f"# exhaustive labelled k=2,m=2 enumeration through n={args.max_n}")
    print("# key = (n, |V0|, mode, kappa_U, lambda_repo, chi_vec, eulerian_min2, strong)")
    for key, count in sorted(counts.items()):
        if key[2] == "opposite-cross":
            print(f"  {key}: {count}")
    if counterexample:
        print()
        print_example("R4 COUNTEREXAMPLE", *counterexample)
        return 1
    print("  R4 counterexamples found: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
