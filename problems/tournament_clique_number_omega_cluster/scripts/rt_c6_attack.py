#!/usr/bin/env python3
"""Independent red-team of C6: omega_vec(AC_n[C3]) and deletion bound, from scratch.

omega_vec(D) = min over total orders prec of omega(backedge graph D^prec).
backedge graph: edge {u,v} iff (in order prec) the *backward* arc is present, i.e.
for the pair, the arc goes from the later vertex to the earlier vertex.

For a tournament D (every pair has exactly one arc), a set S is a clique in D^prec
iff S can be ordered so that EVERY pair is a backward arc, i.e. there's a linear
ordering of S that is a "reverse-topological" listing: for all u<v in prec within S,
arc v->u exists. Equivalently S is a clique in some backedge graph iff there is a
total order of S consistent with all pairwise arcs being backward -- but D restricted
to S is a tournament, so S is a transitive-tournament-shaped clique iff... actually
ANY pair in a tournament is a single arc; backedge means oriented "downward" in prec.
A set S forms a clique in D^prec iff for every pair {u,v} in S, the arc is backward,
i.e. tail comes after head in prec. So S is a clique iff prec restricted to S lists
them in reverse order of a transitive sub-tournament => S must induce a TRANSITIVE
tournament (a clique in backedge graph = transitive subtournament whose topological
order is the reverse of prec). Wait: in a tournament any subset induces a tournament;
for all pairs to be backward arcs simultaneously under one linear order prec, the
arcs within S must form a transitive tournament (the order prec|S = reverse of the
acyclic order). So: clique of size r in some backedge graph <=> S induces a TRANSITIVE
subtournament of size r AND prec orders S as reverse topological.

omega_vec(D) = min over prec of (max transitive subtournament that is "all backward").
We compute it exactly via SAT betweenness encoding below.

SAT encoding for "exists order prec with omega(D^prec) <= k" (i.e. omega_vec<=k):
We must forbid any (k+1)-clique in the backedge graph. A clique of size k+1 is a set
of k+1 vertices that induce a transitive tournament AND are listed reverse-topologically
by prec. Equivalently: a (k+1)-set v_0..v_k with arcs all one direction in prec's reverse.
Standard encoding (from the engine): variables x_{u,v} = u prec v, transitivity +
totality; forbid that there exist k+1 vertices forming an increasing chain in prec where
each consecutive (and hence all) pairs is a backward arc. Cleaner: a backward arc {u,v}
with arc v->u and u prec v. A clique in backedge graph = set where ordering by prec gives
a chain v_1 prec v_2 prec ... with arc v_{j}->v_{i} for i<j (backward). For a tournament,
if all consecutive pairs are backward AND it's a clique we need all pairs backward.
We forbid (k+1)-cliques directly: there's no order in which some (k+1) vertices each pair
is a backward arc. We use the "no increasing path of backward arcs of length k+1 in a
transitive set" but simplest correct route: enumerate over ORDER variables and assert no
(k+1) vertices are pairwise backward.

We use a clean, well-known encoding: for omega_vec <= k, find a linear order (via
position integers encoded as pairwise x_{uv}) such that the backedge graph has no clique
of size k+1. Backedge graph edges depend on order, so we encode: edge e_{uv} (u<v as index)
true iff arc(later,earlier). We then forbid (k+1)-cliques. But cliques range over all
subsets -> too many. Instead we use the contrapositive structural fact (paper): a clique
in backedge graph = a set S inducing transitive subtournament listed reverse-topologically.
For a FIXED order prec we can compute omega(D^prec) directly: build graph with edge {u,v}
iff the arc between them is backward wrt prec; omega = max clique. We do an EXACT min over
orders only via SAT for the decision, but for verification we (1) directly compute omega
for the proposed good orders from the docs, giving UPPER bounds, and (2) brute-force min
over all orders for tiny n to confirm the value, and (3) SAT for medium n.

Here we implement the direct backedge-clique computation for a GIVEN order (exact omega via
max-clique on the backedge graph), used to certify the docs' constructive orders, plus a
brute-force exact omega_vec for tiny instances (all orders) as ground truth.
"""
import sys, itertools

def AC_arcs(n):
    """Return set of arcs (i,j) meaning i->j, for AC_n. n=2m+1, g={1..m-1}∪{m+1}."""
    assert n % 2 == 1 and n >= 7, n
    m = (n - 1) // 2
    g = set(range(1, m)) | {m + 1}
    arcs = set()
    for i in range(n):
        for j in range(n):
            if i == j: continue
            if (j - i) % n in g:
                arcs.add((i, j))
    # sanity: tournament
    for i in range(n):
        for j in range(i+1, n):
            assert ((i,j) in arcs) ^ ((j,i) in arcs), (n,i,j)
    return arcs, m

def C3_arc(h1, h2):
    """C3 = 0->1->2->0. return True if h1->h2."""
    return (h2 - h1) % 3 == 1

def lex_sub_arc(arcs_T, t1, h1, t2, h2):
    """arc (t1,h1)->(t2,h2) in T[C3]? lex: if t1!=t2 use T; if t1==t2 use C3."""
    if t1 != t2:
        return (t1, t2) in arcs_T
    return C3_arc(h1, h2)

def build_ACC3(n):
    arcs_T, m = AC_arcs(n)
    V = [(t, h) for t in range(n) for h in range(3)]
    arc = {}
    for a in V:
        for b in V:
            if a == b: continue
            arc[(a, b)] = lex_sub_arc(arcs_T, a[0], a[1], b[0], b[1])
    # sanity tournament
    for a in V:
        for b in V:
            if a == b: continue
            assert arc[(a,b)] ^ arc[(b,a)], (n,a,b)
    return V, arc, m

def backedge_omega_for_order(V, arc, order):
    """Given a list 'order' (prec: order[0] is smallest), compute omega of backedge graph.
    Edge {u,v} present iff backward arc: with pos[u]<pos[v], edge iff arc v->u."""
    pos = {v: i for i, v in enumerate(order)}
    # adjacency in backedge graph
    idx = {v: i for i, v in enumerate(V)}
    nV = len(V)
    adj = [set() for _ in range(nV)]
    for a in range(nV):
        for b in range(a+1, nV):
            u, v = V[a], V[b]
            # determine which is earlier in prec
            if pos[u] < pos[v]:
                early, late = u, v
            else:
                early, late = v, u
            # backward arc: arc late->early
            if arc[(late, early)]:
                adj[a].add(b); adj[b].add(a)
    # max clique (Bron-Kerbosch with pivot)
    best = [0]
    def bk(R, P, X):
        if not P and not X:
            best[0] = max(best[0], len(R)); return
        if len(R) + len(P) <= best[0]:
            return
        pivot = max(P | X, key=lambda u: len(adj[u] & P)) if (P|X) else None
        cand = P - (adj[pivot] if pivot is not None else set())
        for v in list(cand):
            bk(R | {v}, P & adj[v], X & adj[v])
            P = P - {v}; X = X | {v}
    bk(set(), set(range(nV)), set())
    return best[0]

def brute_omega_vec(V, arc):
    """Exact omega_vec = min over ALL orders of backedge omega. Tiny only."""
    best = len(V)
    for perm in itertools.permutations(range(len(V))):
        order = [V[i] for i in perm]
        o = backedge_omega_for_order(V, arc, order)
        if o < best:
            best = o
            if best == 1: break
    return best

if __name__ == "__main__":
    print("Sanity: AC_n[C3] is a tournament for n in {7,9,11,13,15}")
    for n in [7,9,11,13,15]:
        V, arc, m = build_ACC3(n)
        print(f"  n={n} m={m} |V|={len(V)} OK")
