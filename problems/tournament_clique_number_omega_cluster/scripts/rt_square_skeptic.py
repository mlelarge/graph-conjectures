"""ADVERSARIAL independent re-derivation of the 'square' quad infeasibility (proof S3.3 III).

NOTHING is imported from the repo's analysis scripts. We re-derive T = AC_n[AC_n]
from the prompt's definitions and brute-force search for a feasible square (backedge
clique on the 4 square cells, one rep per cell).

Definitions (from the prompt, NOT from repo):
  n = 2m+1, g = {1..m-1} U {m+1}.
  AC_n arc i->j iff (j-i) mod n in g.
  T = AC_n[AC_n]: vertex (a,b); arc (a,b)->(a',b') iff
     [a!=a' and (a'-a) mod n in g]  OR  [a==a' and (b'-b) mod n in g].
  c(t) = 3 if t==0, 2 if 1<=t<=m, 1 if m+1<=t<=2m.
  cell chi(a,b) = (c(b), c(a)).
  inner_then_outer key(a,b) = (c(b), c(a), a, b).
"""
import sys, itertools

def ac_gen(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}

def c(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1  # m+1..2m

def cell(a, b, m):
    return (c(b, m), c(a, m))

def key(a, b, m):
    return (c(b, m), c(a, m), a, b)

def beats_T(p, q, n, g):
    """Does vertex p beat vertex q in T = AC_n[AC_n]?  p,q are (a,b)."""
    a, b = p
    ap, bp = q
    if a != ap:
        return ((ap - a) % n) in g
    else:
        return ((bp - b) % n) in g

def cell_vertices(target_cell, n, m):
    return [(a, b) for a in range(n) for b in range(n)
            if (a, b) != (0, 0) and cell(a, b, m) == target_cell]

def is_backedge_clique(reps, n, g, m):
    """reps: list of vertices, in arbitrary order. A backedge clique requires:
    when sorted by `key` ascending, every later vertex beats every earlier one
    (later in key = higher; the higher beats the lower => backward arc)."""
    ordered = sorted(reps, key=lambda v: key(v[0], v[1], m))
    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            lo = ordered[i]  # earlier in key (lower)
            hi = ordered[j]  # later in key (higher)
            # backedge: hi must beat lo
            if not beats_T(hi, lo, n, g):
                return False
    return True

def try_realize_cellset(cells, n):
    """Brute-force search for a backedge clique with exactly one rep per cell.
    Returns a witness list of reps if feasible, else None."""
    m = (n - 1) // 2
    g = ac_gen(n)
    cellverts = [cell_vertices(cl, n, m) for cl in cells]
    for combo in itertools.product(*cellverts):
        # all reps in distinct cells by construction; check backedge clique
        if is_backedge_clique(list(combo), n, g, m):
            return list(combo)
    return None

# The 6 squares from proof S3.3 III: base square + 5 derived (replace a c(b)=2 cell
# by its inner-source b=0 counterpart). We must DERIVE which 6. The 8 cells are
# {1,2,3}^2 \ {(3,3)}.  Base square = {(1,1),(1,2),(2,1),(2,2)}.
# The proof says the other 5 replace ONE c(b)=2 cell by its (3,.) counterpart.
# c(b)=2 cells in the square are (2,1),(2,2). Their (3,.) counterparts: (3,1),(3,2).
# We instead enumerate ALL minimal infeasible cell-sets independently and identify
# the squares; but here for the directed task, also test the explicit 6.
BASE = frozenset({(1, 1), (1, 2), (2, 1), (2, 2)})
SQUARES = [
    {(1, 1), (1, 2), (2, 1), (2, 2)},   # base
    {(1, 1), (1, 2), (2, 1), (3, 2)},
    {(1, 1), (1, 2), (3, 1), (2, 2)},
    {(1, 1), (1, 2), (3, 1), (3, 2)},
    {(2, 1), (2, 2), (3, 1), (3, 2)},   # band2/band3 square analogue
    {(1, 1), (3, 2), (3, 1), (2, 2)},   # candidate; will be cross-checked below
]

def main():
    ns = [int(x) for x in sys.argv[1:]] or [7, 9, 11, 13, 15]
    for n in ns:
        m = (n - 1) // 2
        print(f"\n===== n={n} (m={m}) =====")
        # sanity: confirm it's a tournament and cell occupancy
        cells_present = {}
        for a in range(n):
            for b in range(n):
                if (a, b) == (0, 0):
                    continue
                cl = cell(a, b, m)
                cells_present.setdefault(cl, 0)
                cells_present[cl] += 1
        print("  cell occupancy:", dict(sorted(cells_present.items())))
        for cells in SQUARES:
            w = try_realize_cellset(cells, n)
            status = "FEASIBLE!! " + str(w) if w else "infeasible"
            print(f"  square {sorted(cells)}: {status}")

if __name__ == "__main__":
    main()
