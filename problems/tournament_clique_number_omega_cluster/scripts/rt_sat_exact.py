"""Independent EXACT omega_vec via SAT + CEGAR (lazy backward-clique constraints).

Model 'exists linear order s with backedge clique number <= K':
 - order vars o[i][j] (i<j as indices): o[i][j] = 1 iff vertex i precedes vertex j in s.
   Antisymmetry + transitivity enforce a total order.
 - A set S (|S|=K+1) is a *backedge clique* under s iff S induces a transitive subtournament
   AND s lists S in reverse of its transitive order, i.e. for the transitive order
   v_1 -> v_2 -> ... -> v_{K+1} (each beats all later? NO: transitive tournament v1 beats v2..),
   define: S is a backedge clique iff for every pair u,v in S, the LATER one in s beats the
   earlier one. Equivalently: order S by s as w_1 (first) .. w_{K+1} (last); need arc(w_q, w_p)
   for all p<q. This is possible only if S is transitive; and then there is a UNIQUE s-restriction
   (reverse of transitive order) realizing it.

 So 'backedge clique S placed backward' under order s  <=>  for the unique reverse order r_S,
 s restricted to S equals r_S. We forbid each transitive (K+1)-subtournament's reverse placement.

 Forbidding: for transitive subtournament with reverse-order w_1<w_2<...<w_{K+1} (the order that
 would make it a backedge clique, i.e. w_1 first), the clause: NOT(AND over consecutive? no, over
 all pairs o[w_p before w_q]). The placement is fully determined by the pairwise 'before' across
 the K+1 chosen; forbid the conjunction of the (K+1 choose 2) ordering literals.

 CEGAR: solve order with current clauses; if SAT, decode order, find any backward transitive
 (K+1)-clique in it; if found add its forbidding clause; else done -> omega_vec <= K.
 If UNSAT -> omega_vec >= K+1.
"""
import sys, itertools
from pysat.solvers import Glucose4

def build_T(n, delete=None):
    m = (n - 1) // 2
    g = {x % n for x in (set(range(1, m)) | {m + 1})}
    V = [(a, b) for a in range(n) for b in range(n)]
    if delete is not None:
        V = [v for v in V if v != delete]
    def arc(u, v):
        (a, b), (a2, b2) = u, v
        if a != a2: return (a2 - a) % n in g
        return (b2 - b) % n in g
    return V, arc

def backedge_clique_in_order(order, arc, target):
    """Given order (list, ascending), find a backedge clique of size 'target' if exists.
    Backedge clique: subset listed in order positions p1<p2<...<pt with arc(order[pj],order[pi])
    for all i<j. Equivalent to max clique in graph adj(i,j) [i<j] = arc(order[j],order[i]).
    Return a clique (as set of order-indices) of size >= target, else None."""
    N = len(order)
    adj = [0]*N
    for i in range(N):
        for j in range(i+1, N):
            if arc(order[j], order[i]):
                adj[i] |= (1<<j); adj[j] |= (1<<i)
    found = [None]
    def bk(R, P, Rset):
        if found[0] is not None: return
        if len(Rset) >= target:
            found[0] = list(Rset); return
        if len(Rset) + bin(P).count("1") < target: return
        PP = P
        while PP and found[0] is None:
            v = (PP & -PP).bit_length()-1
            bk(R+1, P & adj[v], Rset+[v])
            P &= ~(1<<v); PP &= ~(1<<v)
    bk(0, (1<<N)-1, [])
    return found[0]

def exists_order_with_clique_le(V, arc, K, max_iter=200000):
    """Return True if exists order with backedge clique number <= K (i.e. no (K+1)-backedge clique)."""
    N = len(V)
    # order vars: var(i,j) for i<j meaning V[i] before V[j]
    var = {}
    cnt = 0
    for i in range(N):
        for j in range(i+1, N):
            cnt += 1
            var[(i,j)] = cnt
    def before(i, j):
        if i < j: return var[(i,j)]
        else: return -var[(j,i)]
    solver = Glucose4()
    # transitivity clauses: before(i,j) & before(j,k) -> before(i,k)
    for i in range(N):
        for j in range(N):
            if j==i: continue
            for k in range(N):
                if k==i or k==j: continue
                # (-before(i,j)) v (-before(j,k)) v before(i,k)
                solver.add_clause([-before(i,j), -before(j,k), before(i,k)])
    it = 0
    while True:
        it += 1
        if it > max_iter:
            return None  # gave up
        if not solver.solve():
            return False  # no order avoids (K+1)-clique -> omega_vec >= K+1
        model = set(l for l in solver.get_model() if l>0)
        # decode order: count how many vertices each is 'before' -> position
        beforecount = [0]*N
        for i in range(N):
            for j in range(N):
                if i==j: continue
                if before(i,j) > 0:
                    if before(i,j) in model: beforecount[i]+=1
                else:
                    if (-before(i,j)) not in model: beforecount[i]+=1
        order_idx = sorted(range(N), key=lambda i: -beforecount[i])  # most-before = first
        order = [V[i] for i in order_idx]
        clique = backedge_clique_in_order(order, arc, K+1)
        if clique is None:
            return True  # found order with backedge clique <= K
        # clique are positions in 'order'; map to V-indices, add forbidding clause
        vidx = [order_idx[p] for p in clique]
        # the placement: these are listed in order pos increasing; forbid this exact backward set.
        # Forbid: NOT(all pairs placed in this relative order). For p<q in clique positions,
        # order_idx[clique[a]] is before order_idx[clique[b]] for a<b.
        lits = []
        cl_sorted = clique  # already increasing positions
        for a in range(len(cl_sorted)):
            for b in range(a+1, len(cl_sorted)):
                ia, ib = order_idx[cl_sorted[a]], order_idx[cl_sorted[b]]
                lits.append(-before(ia, ib))  # negate "ia before ib"
        solver.add_clause(lits)

def omega_vec_exact(V, arc, lo=1, hi=None):
    if hi is None: hi = len(V)
    # find smallest K with exists_order_with_clique_le True == omega_vec
    # omega_vec = min K such that an order achieves backedge clique <= K.
    # search K upward
    for K in range(lo, hi+1):
        r = exists_order_with_clique_le(V, arc, K)
        if r is True:
            return K
        if r is None:
            return f"timeout at K={K}"
    return hi

if __name__ == "__main__":
    n = 7
    V, arc = build_T(n)
    print(f"AC_{n}[AC_{n}] full: omega_vec =", omega_vec_exact(V, arc, lo=3, hi=6)); sys.stdout.flush()
    Vd, arcd = build_T(n, delete=(0,0))
    print(f"deletion (0,0): omega_vec =", omega_vec_exact(Vd, arcd, lo=3, hi=6)); sys.stdout.flush()
