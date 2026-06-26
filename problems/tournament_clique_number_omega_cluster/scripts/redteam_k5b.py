"""Red-team v2: respect the CELL KEY ORDER.

A backedge clique uses distinct cells (proof §3.1). The order ≺ is the
inner_then_outer key: key(a,b)=(c(b),c(a),a,b).  CRUCIAL: the proof's casework
assumes the cells are ordered by (c(b),c(a)) and reps are pairwise-backward in
that order: the HIGHER-cell rep beats the LOWER-cell rep.

BUT: two vertices in DIFFERENT cells may have the SAME (c(b),c(a))? No -- cell
IS (c(b),c(a)). So distinct cells => distinct (c(b),c(a)) pairs => the cell key
(c(b),c(a)) strictly orders the reps (ties broken by a,b but reps are in
distinct cells so the (c(b),c(a)) part already differs).

So feasibility WITH cell order: pick one rep per cell; for every pair, the rep
in the lexicographically-higher cell (by (c(b),c(a))) must beat the lower one.
Then they auto-form a backedge clique under any order extending the cell order.

We test the 14 sets under THIS (correct) constraint.

We ALSO test the weaker "transitive sub-tournament" notion (v1) and report the
difference -- if a set is transitive-feasible but cell-order-infeasible, the
clique would have to violate the cell order, meaning the reps appear in ≺ in a
different order than (c(b),c(a)) suggests. Check whether that's even possible:
since cell = (c(b),c(a)) and ≺ sorts by (c(b),c(a)) FIRST, the ≺-order of reps
in distinct cells is EXACTLY the cell-key order. So a backedge clique on these
reps under ≺ REQUIRES higher-cell beats lower-cell. The transitive notion is
too weak. The cell-order notion is the right one.
"""
import itertools


def g_set(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}


def c_pot(t, m):
    if t == 0: return 3
    if 1 <= t <= m: return 2
    return 1


def beats(u, v, n, g):
    a, b = u; ap, bp = v
    if a != ap: return (ap - a) % n in g
    else: return (bp - b) % n in g


def cell_vertices(cell, n, m):
    cb, ca = cell
    bs = [t for t in range(n) if c_pot(t, m) == cb]
    as_ = [t for t in range(n) if c_pot(t, m) == ca]
    return [(a, b) for a in as_ for b in bs]


def cell_order_feasible(cellset, n):
    """Reps with: for each pair, rep in higher (c(b),c(a)) cell beats lower one."""
    m = (n - 1) // 2
    g = g_set(n)
    # order cells by their (c(b),c(a)) = the cell itself, ascending
    order = sorted(range(len(cellset)), key=lambda i: cellset[i])
    pools = [cell_vertices(c, n, m) for c in cellset]
    for combo in itertools.product(*pools):
        ok = True
        for ii in range(len(order)):
            for jj in range(ii + 1, len(order)):
                lo = order[ii]; hi = order[jj]  # hi cell is higher
                # higher cell rep must beat lower cell rep
                if not beats(combo[hi], combo[lo], n, g):
                    ok = False; break
            if not ok: break
        if ok:
            return combo
    return None


# also verify: under inner_then_outer key, reps in distinct cells are ordered
# exactly by cell. confirm by checking the full key.
def full_key(v, m):
    a, b = v
    return (c_pot(b, m), c_pot(a, m), a, b)


TRIPLES_GIVEN = [
    [(1,1),(1,3),(2,1)], [(1,1),(1,3),(3,1)], [(1,1),(2,3),(3,1)],
    [(2,1),(2,3),(3,1)], [(1,3),(2,1),(2,3)],
]
def swap_alpha(cell):
    cb, ca = cell
    if ca == 1: ca = 2
    elif ca == 2: ca = 1
    return (cb, ca)
TRIPLES = []
for tr in TRIPLES_GIVEN:
    TRIPLES.append([tuple(c) for c in tr])
    TRIPLES.append([swap_alpha(tuple(c)) for c in tr])
QUADS = [
    [(1,1),(1,2),(2,1),(2,3)], [(1,2),(2,1),(2,2),(2,3)],
    [(1,3),(2,1),(2,2),(3,1)], [(1,3),(2,2),(3,1),(3,2)],
]
ALL14 = TRIPLES + QUADS


def main():
    ns = [7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
    print(f"{len(ALL14)} cell-sets, CELL-ORDER feasibility (correct notion)")
    print("="*70)
    any_feasible = False
    for cs in ALL14:
        verdicts = {}; witness = None
        for n in ns:
            f = cell_order_feasible(cs, n)
            verdicts[n] = (f is None)
            if f is not None and witness is None:
                witness = (n, f)
        all_inf = all(verdicts.values())
        tag = "INFEASIBLE(all n)" if all_inf else "*** FEASIBLE ***"
        if not all_inf: any_feasible = True
        print(f"{cs}  -> {tag}")
        if witness:
            print(f"      WITNESS n={witness[0]}: reps={witness[1]}")
    print("="*70)
    print("ANY CELL-ORDER FEASIBLE (counterexample)?:", any_feasible)


if __name__ == "__main__":
    main()
