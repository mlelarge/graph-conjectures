"""Fast parts of the independent re-verification (no slow AC_17 lower bound)."""
import os
import sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

P = 17
g = {1, 2, 3, 4, 5, 6, 7, 9}
arcs = [(i, (i + d) % P) for i in range(P) for d in g]
print("is_tournament:", core.is_tournament(P, arcs))
neg = {(-d) % P for d in g}
print("g=", sorted(g), "-g=", sorted(neg))
print("partition {1..16}:", sorted(g | neg) == list(range(1, P)) and (g & neg) == set())
beats = core.beats_matrix(P, arcs)
rot = [(x + 1) % P for x in range(P)]
def is_auto(perm):
    return all(beats[u][v] == beats[perm[u]][perm[v]] for u in range(P) for v in range(P))
print("rotation automorphism (vertex-transitive):", is_auto(rot))
print("17 mod 4 =", P % 4)
sg = sorted(g)
print("consecutive:", all(sg[i+1]-sg[i]==1 for i in range(len(sg)-1)))
print("g == QR_17?", sorted(g) == sorted({(x*x)%17 for x in range(1,17)}))

# upper bound
print("\nUPPER BOUND omega(identity) =", core.omega_of_order(P, arcs, list(range(P))))
print("min over 17 rotations:", min(core.omega_of_order(P, arcs, [(s+k)%P for k in range(P)]) for s in range(P)))
