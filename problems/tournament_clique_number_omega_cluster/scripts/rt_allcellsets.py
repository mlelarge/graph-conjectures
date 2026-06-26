"""Independent: enumerate ALL feasible/infeasible cell-sets and the minimal infeasible ones.

For each subset of the 8 cells, decide (by brute force over representatives) whether a
backedge clique using exactly one rep per cell exists. From that, derive the minimal
infeasible cell-sets, and CHECK the proof's central claim: every 5-subset of the 8 cells
contains a minimal infeasible set (=> no 5 cells realizable => omega_vec(T-(0,0)) <= 4).

Also: directly check whether ALL 5-cell subsets are infeasible (the real target).
"""
import sys, itertools

def ac_gen(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}

def c(t, m):
    if t == 0: return 3
    if 1 <= t <= m: return 2
    return 1

def cell(a, b, m):
    return (c(b, m), c(a, m))

def key(a, b, m):
    return (c(b, m), c(a, m), a, b)

def beats_T(p, q, n, g):
    a, b = p; ap, bp = q
    if a != ap:
        return ((ap - a) % n) in g
    return ((bp - b) % n) in g

def cell_vertices(target_cell, n, m):
    return [(a, b) for a in range(n) for b in range(n)
            if (a, b) != (0, 0) and cell(a, b, m) == target_cell]

def is_backedge_clique(reps, n, g, m):
    ordered = sorted(reps, key=lambda v: key(v[0], v[1], m))
    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            if not beats_T(ordered[j], ordered[i], n, g):
                return False
    return True

def feasible(cells, n, m, g, cv):
    pools = [cv[cl] for cl in cells]
    for combo in itertools.product(*pools):
        if is_backedge_clique(list(combo), n, g, m):
            return list(combo)
    return None

ALL_CELLS = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2)]

def main():
    ns = [int(x) for x in sys.argv[1:]] or [7, 9, 11]
    for n in ns:
        m = (n - 1) // 2
        g = ac_gen(n)
        cv = {cl: cell_vertices(cl, n, m) for cl in ALL_CELLS}
        print(f"\n===== n={n} =====")
        # feasibility of every subset
        feas = {}  # frozenset(cells) -> witness or None
        for r in range(1, 9):
            for cells in itertools.combinations(ALL_CELLS, r):
                feas[frozenset(cells)] = feasible(cells, n, m, g, cv)
        # max feasible cell-set size
        max_feas = max((len(s) for s, w in feas.items() if w is not None), default=0)
        print(f"  max feasible cell-set size = {max_feas}")
        # all 5-subsets infeasible?
        five = [s for s in feas if len(s) == 5]
        bad5 = [s for s in five if feas[s] is not None]
        print(f"  #5-subsets={len(five)}; feasible 5-subsets={len(bad5)}")
        if bad5:
            for s in bad5[:5]:
                print(f"    FEASIBLE 5-set {sorted(s)} witness={feas[s]}")
        # minimal infeasible sets
        infeas = [s for s in feas if feas[s] is None]
        minimal = []
        infset = set(infeas)
        for s in infeas:
            if not any((t < s) for t in infset):
                minimal.append(s)
        triples = sorted([sorted(s) for s in minimal if len(s) == 3])
        quads = sorted([sorted(s) for s in minimal if len(s) == 4])
        bigger = [sorted(s) for s in minimal if len(s) > 4]
        print(f"  #minimal infeasible: {len(minimal)} "
              f"(triples={len(triples)}, quads={len(quads)}, >4={len(bigger)})")
        print(f"    triples: {triples}")
        print(f"    quads:   {quads}")
        if bigger:
            print(f"    bigger:  {bigger}")
        # central claim: every 5-subset contains a minimal infeasible set
        cover_ok = True
        for s in five:
            if not any(mm <= s for mm in minimal):
                cover_ok = False
                print(f"    5-set NOT covered by any minimal infeasible: {sorted(s)} feasible={feas[s] is not None}")
        print(f"  every 5-subset contains a minimal infeasible set? {cover_ok}")
        # Identify the 'squares' among the quads
        print(f"  total minimal count vs proof's 20: {len(minimal)}")

if __name__ == "__main__":
    main()
