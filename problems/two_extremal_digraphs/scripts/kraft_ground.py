#!/usr/bin/env python3
"""Ground the Kraft-cover-capacity proposal.

STEP 1: calibrate Kraft on the n=6 near-miss (k=2). Enumerate single-dicycles,
        compute bad-flip set over Omega={0,1}^{k-1}, c(C)=#distinct components,
        check whether the bad-cycle family COVERS Omega and the Kraft sum.
STEP 2: abstract Kraft feasibility for k=3,4: minimum cube covers of
        Omega={0,1}^{k-1} by affine subcubes of dim k-c(C); min achievable
        Kraft sum SUM 2^{-c(C)} over covers.  Pure combinatorics.
STEP 3: realizability search -- k=3 forest+even-single structures, build
        balanced orientations, call H.is_2extremal; any True with k>=2 BREAKS
        the open_crux direction.
"""
import itertools
import os
import sys
from collections import Counter
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H
from fd_flip_cube import (
    f_components_and_bits,
    simple_directed_cycles,
    cycle_bad_partials,
    split_digons_singles,
)


def omega_masks(k):
    # Omega = {0,1}^{k-1}: fix component 0's bit to 0, free bits comps 1..k-1.
    # We represent a full flip-mask over all k components but with comp0 bit=0.
    return [m << 1 for m in range(1 << (k - 1))]  # comp0 bit at position 0 = 0


def bad_flipmasks_of_cycle(cyc, comp, bit, k):
    """Return the set of FULL flip masks (over k comps, comp0 fixed 0) on which
    `cyc` is monochromatic, plus c = #distinct components the cycle touches."""
    comps_touched = {comp[v] for v in cyc}
    c = len(comps_touched)
    partials = cycle_bad_partials(cyc, comp, bit, k)
    masks = set()
    for m in range(1 << k):
        if (m & 1) != 0:  # comp0 fixed to 0
            continue
        if any(all(((m >> cc) & 1) == val for cc, val in p) for p in partials):
            masks.add(m)
    return masks, c


def step1_nearmiss():
    print("=" * 70)
    print("STEP 1: calibrate Kraft on n=6 near-miss (k=2)")
    print("=" * 70)
    forest = [(0, 1), (3, 2), (4, 2), (2, 5)]
    singles = [(0, 3), (0, 5), (1, 4), (1, 5), (3, 4)]
    # build digraph: digons for forest edges, single arcs as given (one orient)
    arcs = []
    for a, b in forest:
        arcs += [(a, b), (b, a)]
    arcs += singles
    n = 6
    digons, sing = split_digons_singles(n, arcs)
    comp, bit, comps = f_components_and_bits(n, digons)
    k = len(comps)
    print(f"  n={n} k(F_D)={k} components={comps}")
    print(f"  bit-labels={bit}")
    cycles = simple_directed_cycles(n, sing)
    print(f"  #single-dicycles={len(cycles)}: {cycles}")
    omega = set(omega_masks(k))
    print(f"  Omega masks (comp0=0): {sorted(omega)}  (size {len(omega)})")
    covered = set()
    per_cycle = []
    for cyc in cycles:
        masks, c = bad_flipmasks_of_cycle(cyc, comp, bit, k)
        masks &= omega
        covered |= masks
        per_cycle.append((cyc, c, masks))
        print(f"    cycle {cyc}: c(C)={c} bad-flips(in Omega)={sorted(masks)}"
              f"  2^-c={Fraction(1, 2**c)}")
    print(f"  union of bad flips = {sorted(covered)}")
    print(f"  COVERS Omega? {covered == omega}")
    # min cover Kraft sum (greedy/exact over small family)
    ksum = min_cover_kraft(per_cycle, omega)
    print(f"  min-cover Kraft sum (if coverable) = {ksum}")
    # oracle invariants
    print(f"  oracle chi_vec={H.chi_vec(n, arcs)} lambda_D={H.lambda_D(n, arcs)}"
          f" is_2extremal={H.is_2extremal(n, arcs)}")
    pred_ok = (covered != omega)  # prediction: near-miss does NOT cover Omega
    print(f"  PREDICTION (near-miss fails cover (a)): does NOT cover Omega"
          f" -> {pred_ok}")
    return pred_ok


def min_cover_kraft(per_cycle, omega):
    """Exact min-Kraft-sum set cover over the cycle family (small)."""
    items = [(c, masks) for _, c, masks in per_cycle if masks]
    best = None
    nitems = len(items)
    # brute force over subsets (family small)
    for r in range(1, nitems + 1):
        for combo in itertools.combinations(range(nitems), r):
            cov = set()
            ks = Fraction(0)
            for i in combo:
                cov |= items[i][1]
                ks += Fraction(1, 2 ** items[i][0])
            if cov == omega:
                if best is None or ks < best:
                    best = ks
    return best


def step2_abstract(kmax=4):
    print("\n" + "=" * 70)
    print("STEP 2: abstract Kraft feasibility for k=3,4")
    print("=" * 70)
    # Omega = {0,1}^{k-1}. An affine subcube of dim d covers 2^d points.
    # A bad dicycle touching c components covers an affine subcube of
    # dimension (k-1)-(c-1) = k-c.  We classify ALL affine subcubes of each
    # dimension and find the min-Kraft cover SUM 2^{-c} = SUM 2^{-(k - dim)}.
    for k in range(2, kmax + 1):
        m = k - 1  # ambient dim of Omega
        cube = list(range(1 << m))
        # enumerate affine subcubes: choose a set of "fixed" coords F subset
        # of m coords and an assignment on them; dim = m - |F|; this subcube
        # corresponds to c = k - dim = k - (m-|F|) = 1 + |F| components.
        subcubes = []  # (frozenset(points), c)
        for fixed in range(m + 1):
            for coords in itertools.combinations(range(m), fixed):
                for vals in itertools.product((0, 1), repeat=fixed):
                    req = dict(zip(coords, vals))
                    pts = frozenset(
                        p for p in cube
                        if all(((p >> c) & 1) == v for c, v in req.items())
                    )
                    c_comp = 1 + fixed  # = k - dim
                    subcubes.append((pts, c_comp))
        full = frozenset(cube)
        # min Kraft-sum cover.  Weight of a subcube = 2^{-c}.  Find min total
        # weight to cover `full`.  Use ILP-free DP over masks (m<=3 small).
        ksum = min_weight_cover(subcubes, full)
        # also: min cover if restricted to FULL-SUPPORT cycles only (c such
        # that subcube is a single point => c = k, dim 0), i.e. point cover.
        point_only = [(pts, c) for pts, c in subcubes if len(pts) == 1]
        ksum_pts = min_weight_cover(point_only, full)
        print(f"  k={k}  Omega=2^{m}={1<<m} pts")
        print(f"    min Kraft sum over ALL affine-subcube covers = {ksum}")
        print(f"    min Kraft sum over POINT (full-support c=k) covers = "
              f"{ksum_pts}")
        print(f"    Kraft threshold the proposal claims: SUM 2^-c >= 1/2")
        print(f"    => min cover Kraft sum < 1/2 ? {ksum < Fraction(1,2)}")


def min_weight_cover(subcubes, full):
    """Min total weight 2^{-c} to cover `full`. DP over covered-set bitmasks."""
    pts = sorted(full)
    idx = {p: i for i, p in enumerate(pts)}
    N = len(pts)
    target = (1 << N) - 1
    # weights as Fraction; convert each subcube to a bitmask + weight
    options = []
    for sub, c in subcubes:
        bm = 0
        for p in sub:
            if p in idx:
                bm |= 1 << idx[p]
        if bm:
            options.append((bm, Fraction(1, 2 ** c)))
    INF = None
    dp = {0: Fraction(0)}
    # Dijkstra-like over masks
    import heapq
    pq = [(Fraction(0), 0)]
    best = {0: Fraction(0)}
    while pq:
        w, mask = heapq.heappop(pq)
        if mask == target:
            return w
        if w > best.get(mask, None) if best.get(mask) is not None else False:
            continue
        for bm, wt in options:
            nm = mask | bm
            nw = w + wt
            if nm not in best or nw < best[nm]:
                best[nm] = nw
                heapq.heappush(pq, (nw, nm))
    return best.get(target)


def step3_realizability(nmax=8, time_budget_cycles=None):
    print("\n" + "=" * 70)
    print("STEP 3: realizability search (k=3 forest+even-single, oracle)")
    print("=" * 70)
    # We search small 3-connected structures: k=3 forest (path-trees) +
    # balanced single-arc sets forming >=4 pure-point full-support covers,
    # build digraph, call oracle.  Reuse p4 search constructor if present.
    breakers = []
    tested = 0
    # Build k=3 path-forests on n vertices, comp sizes summing to n,
    # then add single arcs as union of directed cycles touching all 3 comps.
    for n in range(7, nmax + 1):
        for sizes in comp_size_partitions(n, 3):
            forest, comp, bit, comps = build_path_forest(sizes)
            digon_arcs = []
            for a, b in forest:
                digon_arcs += [(a, b), (b, a)]
            # candidate full-support cycles: simple cycles over all vertices
            # touching all 3 comps; we enumerate small directed cycles on the
            # complete digraph minus digon-conflicts, pick balanced unions.
            res = search_single_sets(n, comp, bit, digon_arcs, comps)
            for arcs, info in res:
                tested += 1
                if not H.is_2extremal(n, arcs):
                    continue
                kappa = H.is_2connected(n, arcs)  # placeholder; refine below
                from step1b_fd_connectivity import vertex_connectivity
                kap = vertex_connectivity(n, arcs)
                lam = H.lambda_D(n, arcs)
                inh2 = H.is_in_H2(n, arcs)
                rec = dict(n=n, sizes=sizes, kappa=kap, lam=lam,
                           is_2extremal=True, in_H2=inh2, arcs=sorted(arcs),
                           **info)
                print(f"  2-EXTREMAL FOUND n={n} kappa={kap} lam={lam} "
                      f"in_H2={inh2} k=3 sizes={sizes}")
                if kap >= 3 and lam == 2:
                    breakers.append(rec)
                    print("    *** P4/open_crux BREAKER (kappa>=3, lambda=2,"
                          " k=3, 2-extremal) ***")
    print(f"  total candidate digraphs oracle-tested: {tested}")
    print(f"  breakers (kappa>=3,lam=2,k>=2,2-extremal): {len(breakers)}")
    return breakers


def comp_size_partitions(n, k):
    # ordered tuples of k sizes >=2 summing to n (each comp a tree needs >=2
    # vtx to be a nontrivial digon edge; but a singleton comp is allowed too).
    def rec(rem, parts):
        if parts == 1:
            if rem >= 1:
                yield (rem,)
            return
        for s in range(1, rem - (parts - 1) + 1):
            for tail in rec(rem - s, parts - 1):
                yield (s,) + tail
    seen = set()
    for t in rec(n, k):
        st = tuple(sorted(t))
        if st in seen:
            continue
        seen.add(st)
        yield t


def build_path_forest(sizes):
    forest = []
    comp = []
    bit = []
    base = 0
    comps = []
    for cid, size in enumerate(sizes):
        block = list(range(base, base + size))
        comps.append(block)
        for v in block:
            comp.append(cid)
        for i, v in enumerate(block):
            bit.append(i % 2)
        for i in range(size - 1):
            forest.append((base + i, base + i + 1))
        base += size
    return forest, comp, bit, comps


def search_single_sets(n, comp, bit, digon_arcs, comps, max_candidates=20000):
    """Enumerate balanced single-arc sets (unions of directed cycles touching
    all 3 components) that form a full-support pure-point cover; yield digraph
    arc-lists.  Bounded search for the timeout budget."""
    results = []
    # cross arcs: arcs between distinct components (single arcs must be balanced
    # and avoid creating digons among themselves / with forest).
    digon_set = set(digon_arcs)
    cross = [(u, v) for u in range(n) for v in range(n)
             if u != v and comp[u] != comp[v]
             and (u, v) not in digon_set]
    # Enumerate small directed cycles on the cross-arc digraph that touch all 3
    # comps (full support) and are monochromatic on exactly one flip (pure pt).
    full_cycles = enumerate_full_support_pure_cycles(n, comp, bit, cross)
    # group by which flip they are bad on
    from collections import defaultdict
    byflip = defaultdict(list)
    for cyc, flip in full_cycles:
        byflip[flip].append(cyc)
    flips = sorted(byflip.keys())
    if len(flips) < 4:  # need all 4 flips of Omega={0,1}^2 covered
        return results
    # pick one supplier per flip, OVERLAPPING (share >=1 arc) -> union of 4
    count = 0
    for combo in itertools.product(*[byflip[f] for f in flips]):
        arcset = set()
        for cyc in combo:
            for i in range(len(cyc)):
                arcset.add((cyc[i], cyc[(i + 1) % len(cyc)]))
        # balance check: in=out per vertex among singles
        if not balanced(n, arcset):
            continue
        # no digon among singles, no parallel with forest digons
        if any((b, a) in arcset for (a, b) in arcset):
            continue
        if arcset & digon_set:
            continue
        arcs = list(digon_arcs) + list(arcset)
        # in/out >=2 Eulerian needed for 2-extremal; let oracle decide
        info = dict(suppliers=len(combo), single_arcs=len(arcset))
        results.append((arcs, info))
        count += 1
        if count >= max_candidates:
            break
    return results


def enumerate_full_support_pure_cycles(n, comp, bit, cross, max_len=8):
    """Directed simple cycles using only cross arcs that touch all 3 comps and
    are monochromatic on exactly one flip of Omega (pure point)."""
    adj = {v: [] for v in range(n)}
    for u, v in cross:
        adj[u].append(v)
    out = []
    k = len({c for c in comp})
    for start in range(n):
        stack = [(start, [start], {start})]
        while stack:
            x, path, seen = stack.pop()
            if len(path) > max_len:
                continue
            for y in adj[x]:
                if y == start and len(path) >= 3:
                    cyc = tuple(path)
                    if len({comp[v] for v in cyc}) == k:  # full support
                        partials = cycle_bad_partials(cyc, comp, bit, k)
                        # bad on which flips of Omega (comp0 fixed 0)?
                        flips = []
                        for m in range(1 << k):
                            if m & 1:
                                continue
                            if any(all(((m >> cc) & 1) == val
                                       for cc, val in p) for p in partials):
                                flips.append(m)
                        if len(flips) == 1:  # pure point
                            out.append((cyc, flips[0]))
                elif y not in seen and y >= start:
                    stack.append((y, path + [y], seen | {y}))
    return out


def balanced(n, arcset):
    indeg = [0] * n
    outdeg = [0] * n
    for u, v in arcset:
        outdeg[u] += 1
        indeg[v] += 1
    return all(indeg[v] == outdeg[v] for v in range(n))


if __name__ == "__main__":
    p1 = step1_nearmiss()
    step2_abstract(4)
    brk = step3_realizability(nmax=8)
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"STEP1 near-miss fails cover(a) as predicted: {p1}")
    print(f"STEP3 breakers found: {len(brk)}")
    if brk:
        print("VERDICT-SIGNAL: P4/Kraft route DEAD (breaker exists)")
        for b in brk:
            print(b)
    else:
        print("VERDICT-SIGNAL: no breaker; Kraft prediction not contradicted")
