"""Lemma HB grounding: half-bundle cactus structure of Eulerian minimum cuts.

Tests the proposal's UNIVERSAL claims over generic Eulerian lambda>=3 digraphs:

  (i)  directed-min iff undirected-min: X is a minimizer of |delta^+(X)| iff X is
       a minimizer of d_und(X)=|delta^+(X)|+|delta^-(X)|.  (For an Eulerian digraph
       |delta^+(X)|=|delta^-(X)| for EVERY X, so this is supposed to be immediate.)

  (ii) per-cactus-cycle (a,b) CONSTANCY: among the minimum directed cuts, the
       "crossing" relation partitions the minimizer SIDES into classes (cactus
       cycles).  The proposal claims: along a cactus cycle V_1..V_m the directed
       boundary profile is a CONSTANT (a,b) with a+b=lambda, i.e. for every pair
       of cyclically-consecutive (or all pairs) the forward boundary forward(j)
       and backward boundary backward(i) have constant sizes a,b.

  (iii) at lambda>=3, every CROSSING-generated minimum-cut arc-set contains a full
       directed half-bundle of size max(a,b)>=2; assembled generator family B has
       |B| <= 4n.

Control: on C4^2, C6^2, C8^2 (lambda=2) the same machinery must report singleton
half-bundles a=b=1 (mechanism failure exactly on the known UNSAT family).

KILL (verdict=fail) iff a single generic Eulerian lambda>=3 instance has:
  - a minimum directed-cut side that is NOT a minimum undirected-cut side (or vice
    versa)  [claim (i)],  OR
  - a crossing class with NON-CONSTANT (a,b)  [claim (ii)],  OR
  - a crossing-generated min-cut arc-set containing NO size>=2 half-bundle  [(iii)].

We generate the FULL n=4 mult<=3 Eulerian lambda>=3 cell and the Eulerian members
of the exhaustive simple n=5,6 generic lambda>=3 census, plus n=5,6 small-mult
Eulerian instances, and check every claim on every instance.
"""
import sys, os, json, time, itertools, argparse, subprocess
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import oracle

# --------------------------------------------------------------------------- #
#  Cut machinery on an arc multiset
# --------------------------------------------------------------------------- #

def all_proper_subsets(n):
    """Yield every nonempty proper subset of {0..n-1} as a frozenset."""
    full = (1 << n) - 1
    for mask in range(1, full):
        yield mask

def mask_to_set(mask, n):
    return frozenset(i for i in range(n) if (mask >> i) & 1)

def out_cut_arcs(arcs, Xmask):
    """delta^+(X): arcs (u,v) with u in X, v not in X. Returns list of (u,v)."""
    return [(u, v) for (u, v) in arcs if ((Xmask >> u) & 1) and not ((Xmask >> v) & 1)]

def in_cut_arcs(arcs, Xmask):
    return [(u, v) for (u, v) in arcs if not ((Xmask >> u) & 1) and ((Xmask >> v) & 1)]


def analyze_instance(n, arcs, lam):
    """Return a dict of findings / first violation for one Eulerian lambda>=3 instance.

    Records:
      - claim_i_violation: a subset where directed-min status != undirected-min status
      - min_dir_sides: list of masks achieving |delta^+|==lam
      - crossing classes (cactus cycles) among those sides, with (a,b) profile data
      - claim_ii_violation, claim_iii_violation
      - generator family size |B|
    """
    out = {"n": n, "lambda": lam,
           "claim_i_violation": None,
           "claim_ii_violation": None,
           "claim_iii_violation": None,
           "B_size": None, "B_over_4n": False,
           "n_min_dir_sides": 0, "n_crossing_classes": 0}

    # ----- compute |delta^+|, |delta^-| for every proper subset
    dirsz = {}
    undsz = {}
    min_dir = None
    min_und = None
    for mask in all_proper_subsets(n):
        dp = len(out_cut_arcs(arcs, mask))
        dm = len(in_cut_arcs(arcs, mask))
        dirsz[mask] = dp
        undsz[mask] = dp + dm
        if min_dir is None or dp < min_dir:
            min_dir = dp
        if min_und is None or (dp + dm) < min_und:
            min_und = dp + dm

    # sanity: directed min should equal lam
    assert min_dir == lam, (min_dir, lam, "min out-cut != lambda")

    # ----- claim (i): directed-min minimizer set == undirected-min minimizer set
    dir_min_sides = set(m for m, v in dirsz.items() if v == min_dir)
    und_min_sides = set(m for m, v in undsz.items() if v == min_und)
    if dir_min_sides != und_min_sides:
        # report a witnessing subset that distinguishes them
        diff = (dir_min_sides ^ und_min_sides)
        wm = min(diff)
        out["claim_i_violation"] = {
            "mask": wm, "X": sorted(mask_to_set(wm, n)),
            "dir": dirsz[wm], "min_dir": min_dir,
            "und": undsz[wm], "min_und": min_und,
            "in_dir_min": wm in dir_min_sides, "in_und_min": wm in und_min_sides}
        return out  # one violation kills it

    out["n_min_dir_sides"] = len(dir_min_sides)

    # ----- crossing relation among minimizer SIDES (cactus cycles)
    # Two sides X, Y "cross" if all four of X\Y, Y\X, X&Y, V\(XuY) are nonempty.
    sides = sorted(dir_min_sides)
    full = (1 << n) - 1
    def crosses(a, b):
        return (a & ~b) and (b & ~a) and (a & b) and (full & ~(a | b))
    # build crossing graph, connected components = crossing classes
    adj = defaultdict(set)
    for i in range(len(sides)):
        for j in range(i + 1, len(sides)):
            if crosses(sides[i], sides[j]):
                adj[sides[i]].add(sides[j])
                adj[sides[j]].add(sides[i])
    seen = set()
    classes = []
    for s in sides:
        if s in seen:
            continue
        # BFS over crossing graph
        comp = []
        stack = [s]
        seen.add(s)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if len(comp) >= 2:  # a real crossing class (cactus cycle)
            classes.append(comp)
    out["n_crossing_classes"] = len(classes)

    # ----- claim (ii): along each crossing class, profile (a,b) constant, a+b=lam
    # The proposal: cut(i,j)=forward(j) u backward(i) has size a_j+b_i=lam for ALL i,j.
    # We interpret forward(i)=|delta^+(V_i)| restricted... but more faithfully:
    # the proposal asserts a CONSTANT (a,b) per class. For each side X in the class,
    # define a(X)=|delta^+(X)| and b(X)=|delta^-(X)|. Since each side is a directed
    # min cut, a(X)=lam and b(X)=lam already (|delta^+|=|delta^-|=lam for Eulerian
    # min cuts). The proposal's (a,b) refers to the boundary BETWEEN consecutive
    # cactus segments. We extract, for every crossing pair (X,Y) in the class, the
    # forward bundle f=|delta^+(X) cap delta^-(Y)-style| ... we use the cleanest
    # operational reading consistent with "cut(i,j)=forward(j) u backward(i),
    # size a+b=lam": for a crossing pair X,Y the symmetric-difference regions give
    # a partition of the boundary into the four crossing arc-classes. We compute,
    # for the crossing pair, the four directed boundary counts and check that the
    # "diagonal pair" sums to lam consistently across the class.
    B = set()  # generator arc-sets (as frozensets of arcs)
    # tree-cut generators: each minimizer side's delta^+ is a generator
    for X in dir_min_sides:
        fs = frozenset(out_cut_arcs(arcs, X))
        B.add(fs)

    for comp in classes:
        # collect the (a,b) "diagonal" profile across all crossing pairs in comp
        profiles = []
        for ii in range(len(comp)):
            for jj in range(len(comp)):
                if ii == jj:
                    continue
                X = comp[ii]; Y = comp[jj]
                if not crosses(X, Y):
                    continue
                # four crossing regions
                A11 = X & Y
                A10 = X & ~Y & full
                A01 = Y & ~X & full
                A00 = full & ~(X | Y)
                # forward(Y) := arcs leaving Y that also leave from the X-overlap...
                # Operationally: the directed boundary decomposes; the proposal's
                # half-bundle is the set of arcs from one region to the adjacent
                # region. Compute the 4 directed crossing-arc counts of the cactus
                # cell. For a cactus cycle the only crossing arcs go between
                # cyclically adjacent cells: count arcs in each of the 4 directions
                # among {A11,A10,A01,A00}.
                def cnt(src, dst):
                    return sum(1 for (u, v) in arcs
                               if ((src >> u) & 1) and ((dst >> v) & 1))
                # half-bundle on the X side leaving X via the A10->A00 / A10->A01 split
                # delta^+(X) = arcs from {A11,A10} to {A01,A00}
                fwdX = (cnt(A10, A01) + cnt(A10, A00) +
                        cnt(A11, A01) + cnt(A11, A00))
                # the half-bundle the proposal wants: arcs from the "private" cell
                # A10 (=X\Y) outward = forward bundle of size a
                a = cnt(A10, A00) + cnt(A10, A01)
                b = cnt(A01, A00) + cnt(A01, A10)
                profiles.append((a, b, fwdX))
        # constancy check: all (a,b) equal AND a+b == lam
        abset = set((p[0], p[1]) for p in profiles)
        if profiles:
            # check a+b==lam for the diagonal reading: cut(X,Y)=delta^+( (X\Y) u (X&Y) )
            # Actually verify the proposal's literal a+b=lam on cut(i,j).
            bad = [p for p in profiles if (p[0] + p[1]) != lam]
            if len(abset) > 1 or bad:
                out["claim_ii_violation"] = {
                    "class_sides": [sorted(mask_to_set(c, n)) for c in comp],
                    "distinct_ab": sorted(abset),
                    "n_with_sum_ne_lambda": len(bad),
                    "example_bad": bad[:3],
                }
                return out
        # claim (iii): every crossing-generated min-cut arc-set contains a half-bundle
        # of size max(a,b)>=2.  Build the half-bundle arc-sets and check containment.
        # Recompute (a,b) PER PAIR (do not reuse a shared abset element -- the profile
        # may be non-constant, in which case (ii) already fired above and we never
        # reach here; but be robust regardless).
        for ii in range(len(comp)):
            for jj in range(len(comp)):
                if ii == jj:
                    continue
                X = comp[ii]; Y = comp[jj]
                if not crosses(X, Y):
                    continue
                A11 = X & Y; A10 = X & ~Y & full
                A01 = Y & ~X & full; A00 = full & ~(X | Y)
                def cnt2(src, dst):
                    return sum(1 for (u, v) in arcs
                               if ((src >> u) & 1) and ((dst >> v) & 1))
                a = cnt2(A10, A00) + cnt2(A10, A01)
                b = cnt2(A01, A00) + cnt2(A01, A10)
                hb = max(a, b)
                fwd_bundle = frozenset(
                    (u, v) for (u, v) in arcs
                    if ((A10 >> u) & 1) and (((A00 >> v) & 1) or ((A01 >> v) & 1)))
                deltaX = frozenset(out_cut_arcs(arcs, X))
                if hb >= 2:
                    B.add(fwd_bundle)
                    # the half-bundle the proposal claims is contained in delta^+(X)
                    # with size >= 2.  fwd_bundle is by construction subset of deltaX
                    # (A10 -> A00,A01 all leave X).  Violation = it is too small.
                    if len(fwd_bundle) < 2 or not fwd_bundle.issubset(deltaX):
                        out["claim_iii_violation"] = {
                            "X": sorted(mask_to_set(X, n)),
                            "Y": sorted(mask_to_set(Y, n)),
                            "a": a, "b": b,
                            "fwd_bundle_size": len(fwd_bundle),
                            "max_ab": hb,
                            "subset_of_deltaX": fwd_bundle.issubset(deltaX)}
                        return out

    out["B_size"] = len(B)
    out["B_over_4n"] = len(B) > 4 * n
    return out


def control_singleton_check(n, arcs, lam):
    """For lambda=2 control families: report the (a,b) half-bundle profile.
    Expected: singleton half-bundles a=b=1 along crossing classes."""
    res = analyze_instance.__wrapped__ if False else None
    # reuse analyze machinery but just extract the (a,b) of crossing classes
    full = (1 << n) - 1
    dirsz = {}
    min_dir = None
    for mask in all_proper_subsets(n):
        dp = len(out_cut_arcs(arcs, mask))
        dirsz[mask] = dp
        if min_dir is None or dp < min_dir:
            min_dir = dp
    dir_min_sides = sorted(m for m, v in dirsz.items() if v == min_dir)
    def crosses(a, b):
        return (a & ~b) and (b & ~a) and (a & b) and (full & ~(a | b))
    abs_seen = set()
    n_cross_pairs = 0
    for i in range(len(dir_min_sides)):
        for j in range(len(dir_min_sides)):
            if i == j:
                continue
            X = dir_min_sides[i]; Y = dir_min_sides[j]
            if not crosses(X, Y):
                continue
            n_cross_pairs += 1
            A10 = X & ~Y & full; A01 = Y & ~X & full; A00 = full & ~(X | Y)
            def cnt(src, dst):
                return sum(1 for (u, v) in arcs
                           if ((src >> u) & 1) and ((dst >> v) & 1))
            a = cnt(A10, A00) + cnt(A10, A01)
            b = cnt(A01, A00) + cnt(A01, A10)
            abs_seen.add((a, b))
    return {"n": n, "lambda": lam, "min_dir": min_dir,
            "n_min_dir_sides": len(dir_min_sides),
            "n_crossing_pairs": n_cross_pairs,
            "distinct_ab": sorted(abs_seen),
            "singletons_a_eq_b_eq_1": abs_seen == {(1, 1)} if abs_seen else None}


# --------------------------------------------------------------------------- #
#  Instance generation
# --------------------------------------------------------------------------- #

def gen_eulerian_multiarc(n, M):
    """All Eulerian lambda>=3 multidigraphs on n vertices, mult<=M, via
    geng -c -d1 n | directg -T bases + multiplicity sweep + balance filter."""
    p1 = subprocess.Popen(["geng", "-c", "-d1", str(n)], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["directg", "-T"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    out, _ = p2.communicate()
    instances = []
    for line in out.decode().splitlines():
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); ne = int(toks[1])
        nums = list(map(int, toks[2:]))
        base = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        for mult in itertools.product(range(1, M + 1), repeat=ne):
            indeg = [0] * nv; outdeg = [0] * nv
            for (u, v), k in zip(base, mult):
                outdeg[u] += k; indeg[v] += k
            ok = all(indeg[v] == outdeg[v] and indeg[v] >= 3 for v in range(nv))
            if not ok:
                continue
            arcs = []
            for (u, v), k in zip(base, mult):
                arcs.extend([(u, v)] * k)
            lam = oracle.arc_connectivity(nv, arcs)
            if lam < 3:
                continue
            instances.append((nv, arcs, lam))
    return instances


def cycle_power_arcs(k, p):
    """C_{k}^p as a digraph: vertices 0..k-1, arc i->i+d (mod k) for d=1..p."""
    arcs = []
    for i in range(k):
        for d in range(1, p + 1):
            arcs.append((i, (i + d) % k))
    return arcs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="n4m3,n5m2",
                    help="comma list of cells to scan, e.g. n4m3,n5m2,n6m1")
    args = ap.parse_args()
    t0 = time.time()

    cells = {
        "n4m3": (4, 3),
        "n4m2": (4, 2),
        "n5m1": (5, 1),
        "n5m2": (5, 2),
        "n6m1": (6, 1),
    }

    report = {"cells": {}, "controls": {}, "violations": [], "elapsed_s": None}

    for cell in args.cells.split(","):
        cell = cell.strip()
        if cell not in cells:
            continue
        n, M = cells[cell]
        insts = gen_eulerian_multiarc(n, M)
        c = {"n": n, "maxmult": M, "n_instances": len(insts),
             "n_claim_i_viol": 0, "n_claim_ii_viol": 0, "n_claim_iii_viol": 0,
             "n_B_over_4n": 0, "max_B_size": 0,
             "n_with_crossing_classes": 0}
        for (nv, arcs, lam) in insts:
            res = analyze_instance(nv, arcs, lam)
            if res["claim_i_violation"]:
                c["n_claim_i_viol"] += 1
                report["violations"].append({"cell": cell, "kind": "i",
                                              "arcs": arcs, **res["claim_i_violation"]})
            if res["claim_ii_violation"]:
                c["n_claim_ii_viol"] += 1
                report["violations"].append({"cell": cell, "kind": "ii",
                                              "arcs": arcs, **res["claim_ii_violation"]})
            if res["claim_iii_violation"]:
                c["n_claim_iii_viol"] += 1
                report["violations"].append({"cell": cell, "kind": "iii",
                                              "arcs": arcs, **res["claim_iii_violation"]})
            if res["n_crossing_classes"] > 0:
                c["n_with_crossing_classes"] += 1
            if res["B_size"] is not None:
                c["max_B_size"] = max(c["max_B_size"], res["B_size"])
                if res["B_over_4n"]:
                    c["n_B_over_4n"] += 1
        report["cells"][cell] = c

    # lambda=2 controls
    for name, (k, p) in [("C4^2", (4, 2)), ("C6^2", (6, 2)), ("C8^2", (8, 2))]:
        arcs = cycle_power_arcs(k, p)
        lam = oracle.arc_connectivity(k, arcs)
        report["controls"][name] = control_singleton_check(k, arcs, lam)

    report["elapsed_s"] = round(time.time() - t0, 2)
    report["KILL"] = any(v for v in report["violations"])
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
