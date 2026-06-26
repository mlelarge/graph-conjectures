"""p=23 LOWER BOUND ONLY: has_triangle_free_order(fixed_first=0) for
   AC_23 = Cay(Z/23, g={1..10} U {12}).  All cheap facts already known
   (upper=3, deletion=2). This isolates the DFS to give it the full budget.
   Verbatim has_le2_order from probe_p23.py (= verified P10/P11 method).
"""
import os
import sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

P = 23
g = set(range(1, 11)) | {12}
arcs = [(i, (i + d) % P) for i in range(P) for d in g]


def has_le2_order(n, arcs_, fixed_first=0):
    bm = core.beats_matrix(n, arcs_)
    placed_nb = [set() for _ in range(n)]
    placed = []

    def dfs(remaining):
        if not remaining:
            return True
        for b in list(remaining):
            nb = {a for a in placed if bm[b][a]}
            tri = False
            nbl = list(nb)
            for x in range(len(nbl)):
                if tri:
                    break
                for y in range(x + 1, len(nbl)):
                    if nbl[y] in placed_nb[nbl[x]]:
                        tri = True
                        break
            if tri:
                continue
            placed.append(b)
            for a in nb:
                placed_nb[a].add(b)
                placed_nb[b].add(a)
            if dfs(remaining - {b}):
                return True
            placed.pop()
            for a in nb:
                placed_nb[a].discard(b)
                placed_nb[b].discard(a)
        return False

    placed.append(fixed_first)
    return dfs(frozenset(range(n)) - {fixed_first})


t0 = time.time()
le2 = has_le2_order(P, arcs, fixed_first=0)
dt = round(time.time() - t0, 1)
out = {
    "P": P, "g": sorted(g),
    "upper_bound_min_omega_rotations": 3,   # from probe_p23.py live run
    "deletion_omega_vec_minus0": 2,         # from probe_p23.py live run (4.6s)
    "has_triangle_free_order_ff0": le2,
    "lb_time_s": dt,
    "omega_vec": 3 if not le2 else 2,
    "is_3_critical": (not le2),
    "status": "COMPLETED",
}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'probe_p23.json'), "w") as f:
    json.dump(out, f, indent=2)
print("has_triangle_free_order_ff0:", le2, f"({dt}s)")
print("RESULT:", json.dumps(out))
