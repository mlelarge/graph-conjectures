"""INDEPENDENT red-team of proof_AC_n_AC_n_k5.md §3.3 (I)/(II).

Re-derived from scratch from the proof's stated definitions. NOT importing
the repo's lex_compose/cell code -- own implementation.

Definitions (from proof header):
  AC_n = Cay(Z/n, g), n=2m+1, g={1..m-1} ∪ {m+1}.   arc i->j iff (j-i) mod n in g.
  T = AC_n[AC_n]: vertex (a,b), a,b in Z/n.
      (a,b)->(a',b') iff [a!=a' and (a'-a) mod n in g]  (outer beats)
                       or [a==a' and (b'-b) mod n in g]  (inner beats, same outer).
  c(t) = 3 if t==0 ; 2 if 1<=t<=m ; 1 if m+1<=t<=2m.
  cell chi(a,b) = (c(b), c(a)).   (inner band, outer band)

A backedge clique under order ≺ is a set in reverse-topological order: every
later vertex (in ≺) beats every earlier one.  Within a cell-set, a "feasible
representative assignment" = one vertex per cell s.t. they form a backedge
clique in SOME order; equivalently the chosen vertices form a transitive
sub-tournament that is in fact a TOTAL ORDER where higher beats lower.
Since they must all pairwise beat in a consistent linear order, the set is a
backedge clique iff the induced sub-tournament on the chosen reps is
TRANSITIVE (acyclic) -- any transitive tournament can be linearly ordered so
later beats earlier. So: a cell-set is FEASIBLE iff there exist reps (one per
cell) inducing a transitive (acyclic) sub-tournament.

We brute-force over all rep choices for each cell-set, for several n.
"""
import sys, itertools


def g_set(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}


def c_pot(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1  # m+1..2m


def beats(u, v, n, g):
    """Does T-vertex u=(a,b) beat v=(a',b')?  u->v ?"""
    a, b = u
    ap, bp = v
    if a != ap:
        return (ap - a) % n in g
    else:
        return (bp - b) % n in g


def is_transitive(reps, n, g):
    """reps = list of T-vertices. Return True iff the induced sub-tournament
    is transitive (acyclic) -> can be linearly ordered as a backedge clique."""
    k = len(reps)
    # must be a tournament among them (no equal vertices); check pairwise
    # acyclicity = no directed cycle = exists a linear order consistent with arcs.
    # Equivalently: the 'beats' relation is a strict total order.
    # Check: it's a strict total order iff it's transitive and total.
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            bi = beats(reps[i], reps[j], n, g)
            bj = beats(reps[j], reps[i], n, g)
            if bi == bj:
                # either both beat (impossible in tournament) or neither (equal verts)
                return False
    # transitivity
    for i in range(k):
        for j in range(k):
            for l in range(k):
                if beats(reps[i], reps[j], n, g) and beats(reps[j], reps[l], n, g):
                    if not beats(reps[i], reps[l], n, g):
                        return False
    return True


def cell_vertices(cell, n, m):
    """All T-vertices (a,b) with chi(a,b) == cell=(beta,alpha)."""
    cb, ca = cell  # c(b)=cb (inner band), c(a)=ca (outer band)
    bs = [t for t in range(n) if c_pot(t, m) == cb]
    as_ = [t for t in range(n) if c_pot(t, m) == ca]
    return [(a, b) for a in as_ for b in bs]


def feasible(cellset, n):
    """Search for a feasible rep assignment (transitive sub-tournament)."""
    m = (n - 1) // 2
    g = g_set(n)
    pools = [cell_vertices(c, n, m) for c in cellset]
    for combo in itertools.product(*pools):
        # reps must be distinct vertices (different cells => automatically distinct)
        if is_transitive(list(combo), n, g):
            return combo
    return None


# The 14 cell-sets the claim says are infeasible:
# (I) 10 triples. Proof gives 5 representatives of 5 symmetric pairs; expand pairs.
TRIPLES_GIVEN = [
    [(1,1),(1,3),(2,1)],
    [(1,1),(1,3),(3,1)],
    [(1,1),(2,3),(3,1)],
    [(2,1),(2,3),(3,1)],
    [(1,3),(2,1),(2,3)],
]
# symmetric partner: swap c(a)=1 <-> c(a)=2 in the outer coordinate.
def swap_alpha(cell):
    cb, ca = cell
    if ca == 1:
        ca = 2
    elif ca == 2:
        ca = 1
    return (cb, ca)

TRIPLES = []
for tr in TRIPLES_GIVEN:
    TRIPLES.append([tuple(c) for c in tr])
    TRIPLES.append([swap_alpha(tuple(c)) for c in tr])

# (II) 4 outer-source quads
QUADS = [
    [(1,1),(1,2),(2,1),(2,3)],
    [(1,2),(2,1),(2,2),(2,3)],
    [(1,3),(2,1),(2,2),(3,1)],
    [(1,3),(2,2),(3,1),(3,2)],
]

ALL14 = TRIPLES + QUADS


def main():
    ns = [7, 9, 11, 13, 15, 17, 19, 21]
    print(f"Testing {len(TRIPLES)} triples + {len(QUADS)} quads = {len(ALL14)} cell-sets")
    print("="*70)
    any_feasible = False
    for cs in ALL14:
        verdicts = {}
        witness = None
        for n in ns:
            f = feasible(cs, n)
            verdicts[n] = (f is None)
            if f is not None and witness is None:
                witness = (n, f)
        all_infeasible = all(verdicts.values())
        tag = "INFEASIBLE(all n)" if all_infeasible else "*** FEASIBLE ***"
        if not all_infeasible:
            any_feasible = True
        print(f"{cs}  -> {tag}")
        if witness:
            print(f"      WITNESS n={witness[0]}: reps={witness[1]}")
    print("="*70)
    print("ANY FEASIBLE (counterexample to claim)?:", any_feasible)


if __name__ == "__main__":
    main()
