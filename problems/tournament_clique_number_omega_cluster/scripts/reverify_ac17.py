"""INDEPENDENT re-verification of AC_17 from scratch.
Does NOT import ground_ac17 or any prior triangle-free helper.
Uses only core.py canonical primitives + an independently-coded
triangle-free-order search (for the lower bound past the bb wall).
"""
import os
import sys, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

P = 17
g = {1, 2, 3, 4, 5, 6, 7, 9}

# ---- build AC_17 ----
arcs = [(i, (i + d) % P) for i in range(P) for d in g]
print("is_tournament:", core.is_tournament(P, arcs))

# generator validity: g and -g partition {1..16}
neg = {(-d) % P for d in g}
print("g       =", sorted(g))
print("-g mod17=", sorted(neg))
print("partition {1..16}:", sorted(g | neg) == list(range(1, P)) and (g & neg) == set())
print("|g|=", len(g), "= (p-1)/2:", len(g) == (P - 1) // 2)

# vertex-transitivity: x->x+1 mod 17 is an automorphism
beats = core.beats_matrix(P, arcs)
def is_auto(perm):
    for u in range(P):
        for v in range(P):
            if beats[u][v] != beats[perm[u]][perm[v]]:
                return False
    return True
rot = [(x + 1) % P for x in range(P)]
print("rotation automorphism:", is_auto(rot))

# 17 mod 4 (dodge Paley) and non-consecutive (dodge G7)
print("17 mod 4 =", P % 4)
sg = sorted(g)
consecutive = all(sg[i+1]-sg[i] == 1 for i in range(len(sg)-1))
print("consecutive generators:", consecutive)

# ---- UPPER BOUND: some explicit order gives omega(backedge) <= 3 ----
w_id = core.omega_of_order(P, arcs, list(range(P)))
print("\nUPPER BOUND omega(identity order) =", w_id)
best_w = w_id
for s in range(P):
    o = [(s + k) % P for k in range(P)]
    w = core.omega_of_order(P, arcs, o)
    best_w = min(best_w, w)
print("min over 17 rotations:", best_w)

# ---- LOWER BOUND: independently-coded triangle-free-order DFS ----
# omega_vec(T) <= 2  iff  exists total order whose backedge graph is triangle-free.
# Reasoning: backedge graph clique number <=2 means no triangle (omega<=2).
# So min over orders of omega <=2  <=>  some order yields a triangle-free backedge graph.
# DFS places vertices in prec order; a vertex b placed after prefix gets backedge
# neighbours among placed a with beats[b][a]. A triangle appears iff b has two
# placed neighbours that are themselves adjacent in the (final) backedge graph.
# Adjacency among placed vertices is FINAL (monotone), so this is a sound check.

def has_le2_order(n, arcs_, fixed_first=None, all_starts=False):
    bm = core.beats_matrix(n, arcs_)
    # adjacency among placed determined incrementally
    placed_nb = [set() for _ in range(n)]  # backedge neighbours among placed
    placed = []
    placed_set = set()

    def dfs(remaining):
        if not remaining:
            return True
        for b in list(remaining):
            nb = {a for a in placed if bm[b][a]}
            # triangle check: any two of nb adjacent?
            tri = False
            nbl = list(nb)
            for x in range(len(nbl)):
                if tri: break
                for y in range(x+1, len(nbl)):
                    if nbl[y] in placed_nb[nbl[x]]:
                        tri = True
                        break
            if tri:
                continue
            # place b
            placed.append(b)
            placed_set.add(b)
            for a in nb:
                placed_nb[a].add(b)
                placed_nb[b].add(a)
            if dfs(remaining - {b}):
                return True
            # undo
            placed.pop()
            placed_set.discard(b)
            for a in nb:
                placed_nb[a].discard(b)
                placed_nb[b].discard(a)
        return False

    if all_starts:
        for s in range(n):
            placed.clear(); placed_set.clear()
            for i in range(n): placed_nb[i].clear()
            placed.append(s); placed_set.add(s)
            if dfs(frozenset(range(n)) - {s}):
                return True
        return False
    else:
        ff = 0 if fixed_first is None else fixed_first
        placed.append(ff); placed_set.add(ff)
        return dfs(frozenset(range(n)) - {ff})

t0 = time.time()
le2 = has_le2_order(P, arcs, fixed_first=0)
print("\nLOWER BOUND: has triangle-free order (fixed_first=0):", le2,
      f"({time.time()-t0:.1f}s)")
# vertex-transitive => start vertex WLOG; le2 False => omega_vec >= 3
print("=> omega_vec(AC_17) >=", 3 if not le2 else "<=2")
print("combined omega_vec(AC_17) =", 3 if (not le2 and best_w == 3) else "??")

# ---- VALIDATE the triangle-free method against the canonical oracle ----
# on smaller circulants where core.omega_vec_bb is feasible.
def circ(p, gen):
    return [(i, (i + d) % p) for i in range(p) for d in gen]

print("\n--- METHOD VALIDATION (triangle-free le2 vs canonical omega_vec) ---")
cases = [
    (11, {1,2,3,4,6}),      # P8: omega_vec=3
    (13, {1,2,3,4,5,7}),    # P9: omega_vec=3
    (11, {1,2,3,4,5}),      # consecutive: omega_vec=2
]
for p, gen in cases:
    a = circ(p, gen)
    assert core.is_tournament(p, a)
    ov = core.omega_vec_bb(p, a)
    le2_ = has_le2_order(p, a, fixed_first=0)  # circulant => fixed first WLOG
    derived = 2 if le2_ else 3   # only valid when omega_vec in {2,3}
    agree = (ov <= 3 and ((ov == 2) == le2_))
    print(f"p={p} g={sorted(gen)}: omega_vec_bb={ov}, le2={le2_}, derived(2or3)={derived}, AGREE={agree}")

print("\nVALIDATION DONE")
