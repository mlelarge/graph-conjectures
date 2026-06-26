"""H4 cyclic-depth-mod-L online orientation (ground plan, R4 proposal).

Adapts h4_depth_balance.py. Instead of an unbounded depth statistic (which makes
D globally acyclic => a*=n, the G8 self-defeat), maintain a CYCLIC class
cd(v) in {0..L-1}. Orient each arriving process-graph edge {u,v} so the class
ADVANCES by 1 modulo L, picking as source the endpoint whose class is the
predecessor of the other's, and updating cd(b) = (cd(a)+1) mod L. Break ties by
pointing INTO the endpoint whose current cyclic class is LEAST populated (a
self-correcting class-balancing rule). Because depth is mod L, long paths WRAP
and close short dicycles of length ~L => D is far from acyclic (a* < n).

CONFIRM (route survives) iff R(n)=min_L a*/(sqrt n log n) is DECREASING AND
R(60) < 1.07 (beats random floor) AND argmin L tracks upward ~ sqrt(log n).
KILL iff R(n) flat or rises, OR R(n) >= ~1.07 for all n, OR argmin L pinned at
boundary {2 or 8} with no n-dependence.
"""
import os
import sys, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def triangle_free_process_buildorder(n, m_cap, seed):
    """Triangle-free process graph, edges in BUILD ORDER (online filtration)."""
    import random
    rng = random.Random(seed)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    adj = [set() for _ in range(n)]
    edges = []
    for (u, v) in pairs:
        if len(edges) >= m_cap:
            break
        if adj[u] & adj[v]:
            continue
        edges.append((u, v))
        adj[u].add(v)
        adj[v].add(u)
    return n, edges


def cyclic_class_balance_orient(n, edges_in_build_order, L):
    """Online cyclic-depth-mod-L orientation with class balancing.

    cd[v] in {0..L-1}, pop[c] = count of vertices currently in class c.
    For edge {u,v}: orient a->b so cd(b) becomes (cd(a)+1) mod L. We pick the
    source a so the advance is consistent; if both orientations are equally
    "advancing" (generic case), break ties by sending the arc INTO the endpoint
    whose RESULTING class is least populated, i.e. prefer the assignment that
    fills the currently-least-populated class.
    """
    cd = [0] * n
    pop = [0] * L
    for v in range(n):
        pop[cd[v]] += 1
    arcs = []
    for (u, v) in edges_in_build_order:
        # Two candidate orientations:
        #   u->v : new class for v = (cd[u]+1)%L
        #   v->u : new class for u = (cd[v]+1)%L
        cu = (cd[u] + 1) % L  # class v would take if u->v
        cv = (cd[v] + 1) % L  # class u would take if v->u
        # Advance-by-1 rule: prefer the orientation whose source is the
        # predecessor of the sink's CURRENT class (closes/continues a chain).
        # u->v advances cleanly if cd[v] == (cd[u]+1)%L already (v is successor);
        # else evaluate both and pick the one filling the least-populated class.
        u_is_pred = (cd[v] == (cd[u] + 1) % L)  # u->v keeps cd[v] (advance hit)
        v_is_pred = (cd[u] == (cd[v] + 1) % L)  # v->u keeps cd[u] (advance hit)
        if u_is_pred and not v_is_pred:
            a, b, nb = u, v, cd[v]
        elif v_is_pred and not u_is_pred:
            a, b, nb = v, u, cd[u]
        else:
            # tie-break: choose orientation that puts the sink into the
            # least-populated resulting class (self-correcting balance).
            if pop[cu] <= pop[cv]:
                a, b, nb = u, v, cu
            else:
                a, b, nb = v, u, cv
        arcs.append((a, b))
        if nb != cd[b]:
            pop[cd[b]] -= 1
            cd[b] = nb
            pop[nb] += 1
    return arcs


def main():
    print(f"{'n':>4} {'L*':>3} {'a*':>4} {'a*/(sqrt n logn)':>17} {'acyclic?':>9}", flush=True)
    rows = []
    for n in [20, 30, 40, 50, 60]:
        best = n + 1
        best_L = None
        any_cyclic = False
        for L in [2, 3, 4, 5, 6, 7, 8]:
            bestL = n + 1
            for c in [1, 1.5, 2, 2.5, 3]:
                m_cap = int(c * math.sqrt(n) * n / 2)
                for s in range(4):
                    _, edges = triangle_free_process_buildorder(
                        n, m_cap, seed=1000 * int(c * 10) + s + n)
                    arcs = cyclic_class_balance_orient(n, edges, L)
                    assert core.is_oriented(arcs), "not oriented"
                    assert core.is_triangle_free(n, arcs), "not triangle-free"
                    if not core.is_acyclic(n, arcs):
                        any_cyclic = True
                    a = core.acyclic_number(n, arcs)
                    if a < bestL:
                        bestL = a
            if bestL < best:
                best = bestL
                best_L = L
        sc = math.sqrt(n) * math.log(n)
        print(f"{n:>4} {best_L:>3} {best:>4} {best / sc:>17.4f} {str(any_cyclic):>9}", flush=True)
        rows.append((n, best_L, best, best / sc))

    print("\n=== RANDOM FLOOR (G4): n=20->1.045, n=30->1.074, n=40->1.072 (~1.07) ===")
    print("=== R(n) = min_L a*/(sqrt n logn), argmin L ===")
    for n, L, a, r in rows:
        print(f"n={n}: R={r:.4f}  argmin L={L}", flush=True)
    decreasing = all(rows[i][3] >= rows[i+1][3] - 1e-9 for i in range(len(rows)-1))
    r60 = rows[-1][3]
    Ls = [r[1] for r in rows]
    L_boundary_pinned = all(L in (2, 8) for L in Ls) and len(set(Ls)) == 1
    print(f"\ndecreasing R(n)? {decreasing}")
    print(f"R(60)={r60:.4f}  (< 1.07 => beats floor: {r60 < 1.07})")
    print(f"argmin Ls over n = {Ls}  (boundary-pinned constant: {L_boundary_pinned})")
    confirm = decreasing and (r60 < 1.07)
    print(f"\nVERDICT: {'CONFIRM (route survives)' if confirm else 'KILL'}")


if __name__ == "__main__":
    main()
