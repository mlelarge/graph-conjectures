"""Independent red-team of proof_AC_n_AC_n_k5.md §3.3.

Built from scratch from the DEFINITIONS, not the repo oracle.

AC_n = Cay(Z/n, g), n=2m+1, g = {1..m-1} U {m+1}.
  arc i->j  iff (j-i) mod n in g.
T = AC_n[AC_n]: vertex (a,b), a,b in Z/n.
  (a,b)->(a',b')  iff  [a!=a' and (a'-a) mod n in g]
                    or  [a==a' and (b'-b) mod n in g].

c(t) = 3 if t==0, 2 if 1<=t<=m, 1 if m+1<=t<=2m.
cell chi(a,b) = (c(b), c(a))  in {1,2,3}^2.

A backedge clique = a subset of vertices inducing a TRANSITIVE (acyclic)
subtournament; equivalently can be ordered so every later vertex beats every
earlier one ("reverse-topological").  We want the max set with <=1 vertex/cell.
"""
import sys
from itertools import combinations


def ac_g(n):
    assert n % 2 == 1
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}


def cval(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1  # m+1 .. 2m


def beats(u, v, n, g):
    """Does u -> v in T = AC_n[AC_n]?  u=(a,b), v=(a2,b2)."""
    a, b = u
    a2, b2 = v
    if a != a2:
        return (a2 - a) % n in g
    else:
        return (b2 - b) % n in g


def is_transitive(verts, n, g):
    """True iff the induced subtournament on `verts` is acyclic (transitive),
    i.e. forms a backedge clique.  Check via topological ordering existence:
    a tournament is transitive iff it has no directed 3-cycle AND no longer
    cycle; for tournaments transitive == acyclic == no 3-cycle.  But to be
    safe and fully independent, test acyclicity directly by Kahn / out-degree
    score uniqueness."""
    k = len(verts)
    # out-degrees within the set; transitive tournament has scores 0,1,..,k-1
    outdeg = []
    for u in verts:
        d = sum(1 for v in verts if v != u and beats(u, v, n, g))
        outdeg.append(d)
    return sorted(outdeg) == list(range(k))


def cell(v, m):
    a, b = v
    return (cval(b, m), cval(a, m))


def max_realizable_cellset(n, verbose=False):
    """Enumerate all backedge cliques with <=1 vertex per cell among survivors
    (a,b) with (a,b) != (0,0).  Return (max_size, an example cellset, example verts)."""
    m = (n - 1) // 2
    g = ac_g(n)
    # group survivor vertices by cell
    cells = {}
    for a in range(n):
        for b in range(n):
            if (a, b) == (0, 0):
                continue
            ch = cell((a, b), m)
            cells.setdefault(ch, []).append((a, b))
    eight = sorted(cells.keys())
    assert (3, 3) not in cells, "deleted (0,0) is the only (3,3) cell"
    assert len(eight) == 8, eight

    best = 0
    best_ex = None
    best_verts = None
    # search from largest cellset down: try every subset of cells of size s,
    # and see if we can pick one rep per cell so the whole set is transitive.
    for s in range(8, 0, -1):
        found = None
        for cellset in combinations(eight, s):
            reps = realize(cellset, cells, n, g)
            if reps is not None:
                found = (cellset, reps)
                break
        if found is not None:
            best = s
            best_ex, best_verts = found
            break
    return best, best_ex, best_verts, eight, cells


def realize(cellset, cells, n, g):
    """Try to pick one vertex per cell in `cellset` so the induced set is a
    backedge clique (transitive).  Backtracking over reps."""
    cl = list(cellset)

    def bt(i, chosen):
        if i == len(cl):
            return list(chosen)
        for v in cells[cl[i]]:
            # check v is consistent (the partial set stays transitive when
            # adding v): a set is transitive iff every subset is; cheapest is
            # to fully test at the end, but prune: with the partial `chosen`,
            # require chosen+{v} acyclic.
            cand = chosen + [v]
            if is_transitive(cand, n, g):
                res = bt(i + 1, cand)
                if res is not None:
                    return res
        return None

    return bt(0, [])


def all_5subsets_have_infeasible_subset(n):
    """For each 5-subset of the 8 cells: is it infeasible? and does it contain a
    3- or 4-subset that is itself infeasible?  Returns list of anomalies."""
    m = (n - 1) // 2
    g = ac_g(n)
    cells = {}
    for a in range(n):
        for b in range(n):
            if (a, b) == (0, 0):
                continue
            cells.setdefault(cell((a, b), m), []).append((a, b))
    eight = sorted(cells.keys())

    def feasible(cs):
        return realize(cs, cells, n, g) is not None

    anomalies = []
    realizable5 = []
    for five in combinations(eight, 5):
        if feasible(five):
            realizable5.append(five)
            continue
        # find a smaller infeasible subset (size 3 or 4)
        has_small = False
        for s in (3, 4):
            for sub in combinations(five, s):
                if not feasible(sub):
                    has_small = True
                    break
            if has_small:
                break
        if not has_small:
            anomalies.append(("infeasible-5-no-small-cover", five))
    return realizable5, anomalies, eight


def main():
    ns = [int(x) for x in sys.argv[1:]] or [7, 9, 11, 13]
    for n in ns:
        best, ex, verts, eight, cells = max_realizable_cellset(n)
        sizes = {c: len(v) for c, v in cells.items()}
        print(f"n={n}: 8 cells = {eight}")
        print(f"      cell populations = {sizes}")
        print(f"      MAX realizable cellset size = {best}")
        print(f"      example cellset = {ex}")
        print(f"      example verts   = {verts}")
        r5, anom, _ = all_5subsets_have_infeasible_subset(n)
        print(f"      # realizable 5-cellsets = {len(r5)}  (claim: 0)")
        if r5:
            print(f"      !!! REALIZABLE 5-SETS: {r5}")
        print(f"      5-subsets infeasible but with NO 3/4 infeasible subset: {anom}")
        print()


if __name__ == "__main__":
    main()
