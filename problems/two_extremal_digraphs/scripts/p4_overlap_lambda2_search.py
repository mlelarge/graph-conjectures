#!/usr/bin/env python3
"""
ADVERSARIAL SEARCH for P4 (ledger next_action (iii), H3).

P4 claims: a 3-connected 2-extremal digraph with k(F_D)=3 forest components and
an OVERLAPPING pure-point 4-full-support single-arc cover forces lambda_D >= 3.

Equivalently: NO such digraph has lambda_D = 2.  Finding one with lambda_D = 2
that is genuinely 2-extremal would BREAK P4 (and is the only thing that can).

This script constructs candidates directly in the P4 shape and stress-tests them:
  * digon graph F_D = a forest with exactly k=3 components (a small tree each),
    so the flip cube is Omega = {0,1}^2 after fixing component 0's bit;
  * single arcs = a union of >=4 simple directed cycles ("suppliers"), each a
    PURE-POINT bad cycle (monochromatic on exactly ONE flip in Omega), the four
    flips collectively covered (full-support cover), and the suppliers OVERLAP
    (share at least one single arc -> not arc-disjoint);
  * in/out balance (Eulerian) on single arcs, no parallel arcs, no accidental
    digon among singles.

For every constructed candidate we record kappa_U, lambda_D, chi_vec,
is_2extremal, overlap, pure-point, full-cover, and FLAG any with
kappa>=3, lambda==2, is_2extremal True, overlap True  (a P4 BREAKER).

Run in FOREGROUND with a hard timeout.
"""

import itertools
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from fd_flip_cube import (  # noqa: E402
    f_components_and_bits,
    simple_directed_cycles,
)
from seam_invariant import split_digons_singles  # noqa: E402
from step1b_fd_connectivity import vertex_connectivity  # noqa: E402


def cycle_arcs(cycle):
    return frozenset(
        (cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))
    )


def build_forest_3comp(comp_sizes):
    """Return (n, forest_edges, component_of, bit_of) for k=3 path-trees of the
    given sizes laid out on consecutive vertex blocks."""
    forest = []
    comp = []
    bit = []
    base = 0
    for cid, size in enumerate(comp_sizes):
        verts = list(range(base, base + size))
        for i in range(size - 1):
            forest.append((verts[i], verts[i + 1]))
        for i, v in enumerate(verts):
            comp.append(cid)
            bit.append(i % 2)
        base += size
    return base, tuple(forest), tuple(comp), tuple(bit)


def flip_of_vertex(v, comp, bit, flip):
    # flip is a tuple over the k components; component 0 fixed to 0.
    return bit[v] ^ flip[comp[v]]


def bad_flip_points(cycle, comp, bit, omega):
    """Return the set of flips in omega on which `cycle` is monochromatic."""
    out = []
    for flip in omega:
        colours = {flip_of_vertex(v, comp, bit, flip) for v in cycle}
        if len(colours) == 1:
            out.append(flip)
    return frozenset(out)


def random_pure_point_cycle(comp, bit, target_flip, omega, n, rng, length_range):
    """Try to build a simple directed cycle that is monochromatic on EXACTLY
    target_flip (a pure-point bad cycle).  Returns a cycle (tuple) or None.

    Strategy: a cycle is bad on a flip iff all its vertices have the same
    induced colour under that flip.  We pick a colour c in {0,1}; eligible
    vertices for target_flip are those v with bit[v]^target_flip[comp[v]]==c.
    A simple cycle on >=3 of them (touching >=2 components so it crosses) is
    monochromatic on target_flip; we then reject if it is also monochromatic
    on another flip (we want PURE point)."""
    for _ in range(40):
        c = rng.randint(0, 1)
        eligible = [
            v for v in range(n)
            if flip_of_vertex(v, comp, bit, target_flip) == c
        ]
        # Need vertices spanning >=2 components for a crossing cycle.
        comps_present = {comp[v] for v in eligible}
        if len(comps_present) < 2 or len(eligible) < 3:
            continue
        L = rng.randint(min(length_range), min(max(length_range), len(eligible)))
        if L < 3:
            continue
        verts = rng.sample(eligible, L)
        # ensure >=2 components
        if len({comp[v] for v in verts}) < 2:
            continue
        rng.shuffle(verts)
        cyc = tuple(verts)
        bad = bad_flip_points(cyc, comp, bit, omega)
        if bad == frozenset((target_flip,)):
            return cyc
    return None


def assemble_candidate(comp_sizes, suppliers, forest, comp, bit, n):
    digon_arcs = frozenset(
        arc for u, v in forest for arc in ((u, v), (v, u))
    )
    single_sets = [cycle_arcs(c) for c in suppliers]
    singles = frozenset().union(*single_sets)
    arcs = singles | digon_arcs
    # No accidental digon among singles, no overlap with digon graph.
    for (u, v) in singles:
        if (v, u) in singles:
            return None
        if (u, v) in digon_arcs:
            return None
    # Eulerian (in=out): each supplier is a cycle so union is a circulation,
    # but overlapping arcs are deduped -> need to recheck balance.
    if not H.is_eulerian_deg(n, arcs):
        return None
    overlap = sum(len(s) for s in single_sets) > len(singles)
    return arcs, singles, overlap


def classify(n, arcs, singles, comp, bit, omega):
    # pure-point + full cover check via ALL single dicycles
    all_bad = []
    for cyc in simple_directed_cycles(n, singles):
        bad = bad_flip_points(cyc, comp, bit, omega)
        if bad:
            all_bad.append((cyc, bad))
    pure_point = all(len(bad) == 1 for _, bad in all_bad)
    covered = set()
    for _, bad in all_bad:
        covered |= bad
    full_cover = covered == set(omega)
    return {
        "pure_point": pure_point,
        "full_cover": full_cover,
        "n_bad_cycles": len(all_bad),
    }


def search(comp_sizes, n_trials, rng, length_range=(3, 6)):
    n, forest, comp, bit = build_forest_3comp(comp_sizes)
    # Omega: component 0 bit fixed to 0; flips over comps 1,2.
    omega = tuple((0, a, b) for a, b in itertools.product((0, 1), repeat=2))

    stats = Counter()
    breakers = []
    classes = Counter()
    for _ in range(n_trials):
        # choose >=4 suppliers, at least one per flip, allow extras to overlap
        suppliers = []
        ok = True
        for flip in omega:
            cyc = random_pure_point_cycle(
                comp, bit, flip, omega, n, rng, length_range
            )
            if cyc is None:
                ok = False
                break
            suppliers.append(cyc)
        if not ok:
            stats["build_fail"] += 1
            continue
        # optionally add 1-2 extra pure-point suppliers to force overlap
        extra = rng.randint(0, 2)
        for _ in range(extra):
            flip = rng.choice(omega)
            cyc = random_pure_point_cycle(
                comp, bit, flip, omega, n, rng, length_range
            )
            if cyc is not None:
                suppliers.append(cyc)

        res = assemble_candidate(comp_sizes, suppliers, forest, comp, bit, n)
        if res is None:
            stats["assemble_fail"] += 1
            continue
        arcs, singles, overlap = res
        if not overlap:
            stats["not_overlap"] += 1
            # still measure but we want overlap specifically
        if not H.is_strong(n, arcs):
            stats["not_strong"] += 1
            continue
        kappa = vertex_connectivity(n, arcs)
        if kappa < 3:
            stats["kappa_lt_3"] += 1
            continue
        chi = H.chi_vec(n, arcs)
        lam = H.lambda_D(n, arcs)
        is2e = H.is_2extremal(n, arcs)
        cl = classify(n, arcs, singles, comp, bit, omega)
        key = (kappa >= 3, lam, chi, is2e, overlap,
               cl["pure_point"], cl["full_cover"])
        classes[key] += 1
        stats["valid_3conn"] += 1
        # P4 BREAKER: 3-connected, 2-extremal, lambda==2, overlapping,
        # pure-point full cover.
        if (kappa >= 3 and lam == 2 and is2e and overlap
                and cl["pure_point"] and cl["full_cover"]):
            breakers.append({
                "n": n,
                "comp_sizes": comp_sizes,
                "arcs": sorted(map(list, arcs)),
                "kappa": kappa, "lambda": lam, "chi_vec": chi,
            })
    return n, stats, classes, breakers


def main():
    rng = random.Random(20260607)
    total_breakers = []
    configs = [
        ((3, 3, 3), 4000),   # n=9, the calibration shape
        ((3, 3, 4), 4000),   # n=10
        ((4, 3, 3), 4000),   # n=10
        ((4, 4, 3), 3000),   # n=11
        ((4, 4, 4), 3000),   # n=12 (a few extra)
        ((2, 3, 3), 4000),   # n=8 small trees
        ((2, 2, 3), 4000),   # n=7 minimal
    ]
    for comp_sizes, n_trials in configs:
        n, stats, classes, breakers = search(comp_sizes, n_trials, rng)
        print(f"# comp_sizes={comp_sizes} n={n} trials={n_trials}")
        print(f"  stats: {dict(stats)}")
        print("  class key = (kappa>=3, lambda, chi_vec, is_2extremal, "
              "overlap, pure_point, full_cover)")
        for key, cnt in sorted(classes.items()):
            print(f"    {key}: {cnt}")
        print(f"  P4 BREAKERS found: {len(breakers)}")
        for b in breakers[:3]:
            print(f"    BREAKER: {b}")
        total_breakers.extend(breakers)
        print()

    print("=" * 60)
    print(f"TOTAL P4 BREAKERS across all configs: {len(total_breakers)}")
    if total_breakers:
        print("P4 IS BROKEN — hand-verify these candidates (oracle "
              "incompleteness gate):")
        for b in total_breakers[:5]:
            print(b)
    else:
        print("NO P4 breaker found: every 3-connected, overlapping, "
              "pure-point full-cover candidate had lambda>=3 OR was not "
              "2-extremal. P4 survives this adversarial search.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
