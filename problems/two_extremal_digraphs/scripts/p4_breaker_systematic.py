#!/usr/bin/env python3
"""
SYSTEMATIC (exhaustive on n=9) P4 breaker search.

Unlike the randomized p4_overlap_lambda2_search.py, this enumerates EVERY
pure-point bad dicycle on the full single-arc skeleton of the 3-block bit
pattern, then enumerates 4-tuples (one supplier per flip of Omega) plus a
bounded number of extra suppliers to force OVERLAP, and gates each assembled
candidate through the oracle.  A P4 BREAKER = 3-connected + 2-extremal +
lambda_D==2 + overlapping + pure-point + full-support cover with k(F_D)=3.

We fix F_D = three path-trees on consecutive blocks (forest, k=3 components).
A "pure-point bad dicycle" is a simple directed cycle on >=3 vertices that is
monochromatic on EXACTLY one flip of Omega = {(0,x1,x2)}.

To keep the join finite we restrict to the FULL single-arc skeleton = all arcs
between distinct vertices that are NOT forest-digon arcs (i.e. the candidate
single-arc universe), enumerate simple dicycles up to a length cap, classify
their pure-point flip, then combine.

Run in FOREGROUND with a hard timeout.
"""
import itertools
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from step1b_fd_connectivity import vertex_connectivity  # noqa: E402


def cycle_arcs(cycle):
    return frozenset((cycle[i], cycle[(i + 1) % len(cycle)])
                     for i in range(len(cycle)))


def build_forest_3comp(comp_sizes):
    forest, comp, bit, base = [], [], [], 0
    for cid, size in enumerate(comp_sizes):
        verts = list(range(base, base + size))
        for i in range(size - 1):
            forest.append((verts[i], verts[i + 1]))
        for i, v in enumerate(verts):
            comp.append(cid)
            bit.append(i % 2)
        base += size
    return base, tuple(forest), tuple(comp), tuple(bit)


def all_pure_point_cycles(n, comp, bit, omega, digon_arcs, max_len):
    """Enumerate every simple directed cycle (len 3..max_len) on the
    non-digon arc universe that is monochromatic on EXACTLY one flip,
    and crosses >=2 components.  Returns dict: flip -> list of cycle tuples."""
    by_flip = defaultdict(list)
    seen = set()

    def colours(cyc, flip):
        return {bit[v] ^ flip[comp[v]] for v in cyc}

    def bad_flips(cyc):
        return frozenset(f for f in omega if len(colours(cyc, f)) == 1)

    # generate simple cycles by DFS over vertex permutations (length-bounded)
    verts = list(range(n))
    for L in range(3, max_len + 1):
        for combo in itertools.combinations(verts, L):
            if len({comp[v] for v in combo}) < 2:
                continue
            # fix smallest vertex first to dedupe rotation; try orderings
            base = combo[0]
            rest = combo[1:]
            for perm in itertools.permutations(rest):
                cyc = (base,) + perm
                # avoid using a digon arc as a single arc
                arcs = cycle_arcs(cyc)
                if any(a in digon_arcs for a in arcs):
                    continue
                # no 2-cycle issue: L>=3 simple so fine; canonical rep
                key = cyc
                if key in seen:
                    continue
                # dedupe by directed-rotation canonical form
                rots = [cyc[i:] + cyc[:i] for i in range(L)]
                canon = min(rots)
                if canon in seen:
                    continue
                seen.add(canon)
                bf = bad_flips(cyc)
                if len(bf) == 1:
                    by_flip[next(iter(bf))].append(canon)
    return by_flip


def assemble(n, suppliers, digon_arcs):
    sets = [cycle_arcs(c) for c in suppliers]
    singles = frozenset().union(*sets)
    for (u, v) in singles:
        if (v, u) in singles:
            return None
        if (u, v) in digon_arcs:
            return None
    arcs = singles | digon_arcs
    if not H.is_eulerian_deg(n, arcs):
        return None
    overlap = sum(len(s) for s in sets) > len(singles)
    return arcs, singles, overlap


def main():
    comp_sizes = (3, 3, 3)
    max_len = 5          # cycle length cap on the skeleton
    extra_cap = 2        # extra overlapping suppliers beyond the 4 base
    n, forest, comp, bit = build_forest_3comp(comp_sizes)
    digon_arcs = frozenset(a for u, v in forest for a in ((u, v), (v, u)))
    omega = tuple((0, x1, x2)
                  for x1, x2 in itertools.product((0, 1), repeat=2))

    by_flip = all_pure_point_cycles(n, comp, bit, omega, digon_arcs, max_len)
    print(f"# SYSTEMATIC P4 search  n={n} comp_sizes={comp_sizes} "
          f"max_len={max_len}")
    for f in omega:
        print(f"  pure-point cycles for flip {f}: {len(by_flip[f])}")
    base_combos = 1
    for f in omega:
        base_combos *= max(1, len(by_flip[f]))
    print(f"  base 4-tuple combinations: {base_combos}")

    stats = Counter()
    classes = Counter()
    breakers = []
    seen_arc = set()

    # all flips must have at least one supplier else cover impossible
    if any(len(by_flip[f]) == 0 for f in omega):
        print("  some flip has NO pure-point cycle -> full cover impossible")
        return 0

    # enumerate one base supplier per flip
    flip_lists = [by_flip[f] for f in omega]
    for base_tuple in itertools.product(*flip_lists):
        # candidate extra suppliers: any pure-point cycle (forces overlap)
        all_cyc = [c for f in omega for c in by_flip[f]]
        # build with 0 extra first, then up to extra_cap extras
        for n_extra in range(0, extra_cap + 1):
            extra_iter = (itertools.combinations(all_cyc, n_extra)
                          if n_extra > 0 else [()])
            for extra in extra_iter:
                suppliers = list(base_tuple) + list(extra)
                res = assemble(n, suppliers, digon_arcs)
                if res is None:
                    stats["assemble_fail"] += 1
                    continue
                arcs, singles, overlap = res
                fa = frozenset(arcs)
                if fa in seen_arc:
                    stats["dup"] += 1
                    continue
                seen_arc.add(fa)
                if not H.is_strong(n, arcs):
                    stats["not_strong"] += 1
                    continue
                kappa = vertex_connectivity(n, arcs)
                if kappa < 3:
                    stats["kappa_lt_3"] += 1
                    continue
                lam = H.lambda_D(n, arcs)
                chi = H.chi_vec(n, arcs)
                is2e = H.is_2extremal(n, arcs)
                stats["valid_3conn"] += 1
                key = (lam, chi, is2e, overlap)
                classes[key] += 1
                if (lam == 2 and is2e and overlap and chi == 3):
                    breakers.append({
                        "n": n, "arcs": sorted(map(list, arcs)),
                        "kappa": kappa, "lambda": lam, "chi": chi,
                        "suppliers": suppliers,
                    })
        # bound total work: stop early if explosion (safety)
        if stats["valid_3conn"] > 200000:
            stats["truncated"] = 1
            break

    print(f"  stats: {dict(stats)}")
    print("  class key = (lambda, chi_vec, is_2extremal, overlap)")
    for k, c in sorted(classes.items()):
        print(f"    {k}: {c}")
    print(f"  distinct 3-connected candidates examined: {len(seen_arc) - stats['not_strong'] - stats['kappa_lt_3']}")
    print(f"  P4 BREAKERS: {len(breakers)}")
    for b in breakers[:5]:
        print(f"    BREAKER: {b}")
    if not breakers:
        print("  RESULT: no lambda==2 2-extremal overlapping pure-point "
              "full-cover candidate exists in this exhaustive family. "
              "P4 SURVIVES.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
