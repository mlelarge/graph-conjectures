"""Fully independent red-team. Build AC_n[AC_n] from scratch, compute backedge
clique under inner_then_outer order on full graph and deletions, plus independent LB."""
import sys
import itertools

def build_T(n):
    m = (n - 1) // 2
    g = set(range(1, m)) | {m + 1}   # {1..m-1} U {m+1}
    g = {x % n for x in g}
    V = [(a, b) for a in range(n) for b in range(n)]
    # arc (a,b)->(a',b') iff [a!=a' and (a'-a)%n in g] or [a==a' and (b'-b)%n in g]
    def arc(u, v):
        (a, b), (a2, b2) = u, v
        if a != a2:
            return (a2 - a) % n in g
        else:
            return (b2 - b) % n in g
    return V, arc, m, g

def c(t, m):
    if t == 0: return 3
    if 1 <= t <= m: return 2
    return 1  # m+1..2m

def inner_then_outer_key(v, m):
    a, b = v
    return (c(b, m), c(a, m), a, b)

def merged_sum_key(v, m):
    a, b = v
    return (c(a, m) + c(b, m), a, b)

def backedge_clique_number(V, arc, key):
    """Order ascending by key. Backedge clique = set listed in reverse-topo order:
    every LATER vertex (higher key) beats every EARLIER one. So edge in backedge graph
    between u<v (key order) iff later beats earlier, i.e. arc(later, earlier)."""
    order = sorted(V, key=key)
    N = len(order)
    # build backedge graph adjacency: i<j connected iff arc(order[j], order[i])
    adj = [set() for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            if arc(order[j], order[i]):
                adj[i].add(j)
                adj[j].add(i)
    # find max clique via Bron-Kerbosch with pivot
    best = [0]
    def bk(R, P, X):
        if not P and not X:
            if R > best[0]:
                best[0] = R
            return
        # bound: prune
        if R + len(P) <= best[0]:
            return
        # pivot
        u = max(P | X, key=lambda v: len(adj[v] & P)) if (P or X) else None
        cand = P - (adj[u] if u is not None else set())
        for v in list(cand):
            bk(R + 1, P & adj[v], X & adj[v])
            P = P - {v}
            X = X | {v}
    bk(0, set(range(N)), set())
    return best[0], order

def main():
    for n in [7, 9, 11, 13]:
        V, arc, m, g = build_T(n)
        key_io = lambda v: inner_then_outer_key(v, m)
        key_ms = lambda v: merged_sum_key(v, m)
        # full graph, inner_then_outer
        w_io_full, _ = backedge_clique_number(V, arc, key_io)
        # full graph, merged_sum
        w_ms_full, _ = backedge_clique_number(V, arc, key_ms)
        # deletion of (0,0), inner_then_outer
        Vd = [v for v in V if v != (0, 0)]
        w_io_del, _ = backedge_clique_number(Vd, arc, key_io)
        print(f"n={n}: io_full={w_io_full} ms_full={w_ms_full} io_del(0,0)={w_io_del}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
