"""DECISIVE p=23 probe: is the almost-consecutive circulant
    AC_23 = Cay(Z/23, g={1..10} U {12})
3-omega_vec-critical?  (the rule g(p)={1..(p-3)/2} U {(p+1)/2})

Reuses the SAME verified triangle-free lower-bound method as probe_p19.py / reverify_ac17.py
(has_le2_order, fixed_first=0, sound for vertex-transitive circulants).

LOWER BOUND omega_vec>=3  <=>  NO total order has a triangle-free backedge graph.
UPPER BOUND omega_vec<=3   via core.omega_of_order over rotations.
DELETION                   via canonical core.omega_vec_bb(T-0).
"""
import os
import sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

P = 23
g = set(range(1, 11)) | {12}   # {1..10} U {12} = {1..(p-3)/2} U {(p+1)/2}

arcs = [(i, (i + d) % P) for i in range(P) for d in g]
out = {}
out["P"] = P
out["g"] = sorted(g)
out["is_tournament"] = core.is_tournament(P, arcs)
print("is_tournament:", out["is_tournament"])

# generator validity: g and -g partition {1..22}
neg = {(-d) % P for d in g}
out["g_partition_ok"] = (sorted(g | neg) == list(range(1, P)) and (g & neg) == set())
out["abs_g_size_half"] = (len(g) == (P - 1) // 2)
print("g       =", sorted(g))
print("-g mod23=", sorted(neg))
print("partition {1..22}:", out["g_partition_ok"], "|g|=(p-1)/2:", out["abs_g_size_half"])

# vertex-transitivity
beats = core.beats_matrix(P, arcs)
def is_auto(perm):
    for u in range(P):
        for v in range(P):
            if beats[u][v] != beats[perm[u]][perm[v]]:
                return False
    return True
rot = [(x + 1) % P for x in range(P)]
out["rotation_automorphism"] = is_auto(rot)
print("rotation automorphism:", out["rotation_automorphism"])
out["P_mod_4"] = P % 4
sg = sorted(g)
out["consecutive_generators"] = all(sg[i+1]-sg[i] == 1 for i in range(len(sg)-1))
print("23 mod 4 =", P % 4, "consecutive:", out["consecutive_generators"])

# QR_23 check (is this Paley?)
qr = sorted({(x*x) % P for x in range(1, P)})
out["QR_23"] = qr
out["is_paley_23"] = (sorted(g) == qr)
print("QR_23 =", qr, " is_paley:", out["is_paley_23"])

# ---- the verified triangle-free decision (copied verbatim from probe_p19) ----
def has_le2_order(n, arcs_, fixed_first=None, all_starts=False):
    bm = core.beats_matrix(n, arcs_)
    placed_nb = [set() for _ in range(n)]
    placed = []
    placed_set = set()

    def dfs(remaining):
        if not remaining:
            return True
        for b in list(remaining):
            nb = {a for a in placed if bm[b][a]}
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
            placed.append(b)
            placed_set.add(b)
            for a in nb:
                placed_nb[a].add(b)
                placed_nb[b].add(a)
            if dfs(remaining - {b}):
                return True
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

# ---- UPPER BOUND ----
best_w = min(core.omega_of_order(P, arcs, [(s + k) % P for k in range(P)])
             for s in range(P))
out["upper_bound_min_omega_rotations"] = best_w
print("\nUPPER BOUND min omega over 23 rotations:", best_w)

# ---- DELETION (canonical, vertex-transitive => all 23 equal) ---- (cheap, do first)
sub_n, sub_arcs = core.subtournament(P, arcs, [v for v in range(P) if v != 0])
t0 = time.time()
del_ov = core.omega_vec_bb(sub_n, sub_arcs, ub=3)
out["deletion_omega_vec_minus0"] = del_ov
out["deletion_time_s"] = round(time.time() - t0, 1)
print("deletion omega_vec(AC_23 - vertex 0):", del_ov, f"({out['deletion_time_s']}s)")

# ---- LOWER BOUND: triangle-free order? (fixed_first=0, sound vertex-transitive) ----
t0 = time.time()
le2 = has_le2_order(P, arcs, fixed_first=0)
dt = time.time() - t0
out["has_triangle_free_order_ff0"] = le2
out["lb_time_s"] = round(dt, 1)
print(f"\nLOWER BOUND has triangle-free order (fixed_first=0): {le2} ({dt:.1f}s)")
omega_vec = 3 if (not le2 and best_w == 3) else (2 if le2 else None)
out["omega_vec"] = omega_vec
print("=> omega_vec(AC_23) =", omega_vec)

out["is_3_critical"] = (omega_vec == 3 and del_ov == 2)
print("\n3-omega_vec-critical:", out["is_3_critical"])

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'probe_p23.json'), "w") as f:
    json.dump(out, f, indent=2)
print("\nRESULT:", json.dumps(out))
