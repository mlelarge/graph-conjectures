#!/usr/bin/env python3
"""Independent SAT exact omega_vec, from scratch, with validation vs brute force.

omega_vec(D) = min over total orders prec of omega(D^prec), where in D^prec the
edge {u,v} is present iff the arc between u,v is *backward* (tail later than head
in prec).

Key fact (tournament): a set S is a clique in D^prec iff S induces a transitive
subtournament whose unique acyclic order is the REVERSE of prec|S. So a clique of
size r corresponds to r vertices v_1,...,v_r with prec v_1 < ... < v_r and arc
v_j -> v_i for ALL i<j (every pair backward). For a TOURNAMENT, "every pair
backward under prec" already forces: if we list S by prec increasing, the arc of
each pair goes from the later to the earlier. That's it -- no separate transitivity
constraint is needed because the arcs are fixed and we just demand they're all
backward.

So: omega_vec(D) <= k  iff  exists total order prec such that there is NO set of
(k+1) vertices that is pairwise backward.

SAT encoding for the DECISION "omega_vec <= k":
 Variables p[u][v] for u<v (index order): p=True means u prec v.
 Order axioms: for the pair {u,v}, exactly one of u prec v / v prec u -- encoded
   by single boolean p[u][v] (p True => u prec v, else v prec u). Transitivity:
   for all triples a,b,c: forbid cyclic prec (a<b<c<a). 6 clauses per triple? We
   add the standard 2 clauses per ordered triple to forbid 3-cycles in prec.
 "backward" predicate b(u,v): given arc dir, edge {u,v} in backedge graph iff the
   tail comes AFTER the head in prec. Concretely if arc u->v: backward iff v prec u.
   if arc v->u: backward iff u prec v.
 Forbid (k+1)-clique: this is the expensive part. A clique = (k+1)-subset all pairs
   backward. We encode via "level"/colouring is NOT exact. Instead we forbid cliques
   directly only for sets that induce a transitive subtournament -- but enumerating
   (k+1)-subsets is C(N,k+1), too many for N~40, k=4 (C(40,5)=658k) -- borderline ok.
 We instead use a cleaner approach: omega_vec<=k iff the backedge graph (which depends
 on prec) is K_{k+1}-free. We add, for EVERY (k+1)-subset of vertices that induces a
 transitive tournament, a clause forbidding all its pairs being simultaneously backward.
 A (k+1)-subset can be pairwise-backward under SOME prec only if it induces a transitive
 tournament; for non-transitive subsets no prec makes all backward, so we skip them.

For N~40 and k=4 this is up to C(40,5)=658008 subsets; each generates ONE clause of
length C(5,2)=10 literals (the negations of "this pair is backward"). Manageable.

We use python-sat (Glucose/Cadical).
"""
import os
import sys, itertools
from pysat.solvers import Cadical153
from pysat.formula import IDPool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_c6_attack import build_ACC3, backedge_omega_for_order, AC_arcs

def omega_vec_leq(N, arc_dir, k, V=None, time_budget=None):
    """arc_dir: dict (i,j)->bool meaning i->j, vertices 0..N-1 (we use index space).
    Return True if omega_vec <= k (i.e. a no-K_{k+1} order exists), else False.
    """
    pool = IDPool()
    def P(u, v):
        # variable: u prec v, for u<v. For u>v return -P(v,u) handled by caller.
        assert u < v
        return pool.id(('p', u, v))
    def prec_lit(u, v):
        # literal that is true iff u prec v
        if u < v: return P(u, v)
        else: return -P(v, u)
    solver = Cadical153()
    # transitivity: forbid 3-cycles a->b->c->a in prec
    for a, b, c in itertools.combinations(range(N), 3):
        # forbid a<b<c<a (cyclic). Two orientations of the cycle.
        # cycle1: aprecb & bprecc & cpreca  -> impossible
        solver.add_clause([-prec_lit(a,b), -prec_lit(b,c), -prec_lit(c,a)])
        # cycle2: aprecc & cprecb & bpreca
        solver.add_clause([-prec_lit(a,c), -prec_lit(c,b), -prec_lit(b,a)])
    # backward predicate as a literal: edge {u,v} backward iff tail-after-head.
    def backward_lit(u, v):
        # if arc u->v (i.e. arc_dir[(u,v)] True): backward iff v prec u
        if arc_dir[(u, v)]:
            return prec_lit(v, u)
        else:
            # arc v->u: backward iff u prec v
            return prec_lit(u, v)
    # forbid (k+1)-cliques: only transitive (k+1)-subsets can be all-backward
    cnt = 0
    for sub in itertools.combinations(range(N), k+1):
        # check induced subtournament is transitive (acyclic). If not, skip.
        # transitive iff it has a unique topological order; equivalently no 3-cycle.
        trans = True
        for a, b, c in itertools.combinations(sub, 3):
            # 3-cycle among a,b,c?
            def dir3(x, y): return arc_dir[(x, y)]
            # count: is there a directed 3-cycle?
            # arcs among a,b,c
            e_ab = dir3(a,b); e_bc = dir3(b,c); e_ca = dir3(c,a)
            if e_ab and e_bc and e_ca:
                trans = False; break
            e_ba = not e_ab; e_cb = not e_bc; e_ac = not e_ca
            if e_ba and e_cb and e_ac:
                trans = False; break
        if not trans:
            continue
        # clause: NOT all pairs backward  => OR of negations
        clause = []
        for u, w in itertools.combinations(sub, 2):
            clause.append(-backward_lit(u, w))
        solver.add_clause(clause)
        cnt += 1
    sat = solver.solve()
    solver.delete()
    return sat, cnt

def exact_omega_vec_sat(N, arc_dir, lo=1, hi=None):
    if hi is None: hi = N
    # find min k with omega_vec<=k true
    k = lo
    while k <= hi:
        sat, _ = omega_vec_leq(N, arc_dir, k)
        if sat:
            return k
        k += 1
    return hi+1  # shouldn't happen

# ---- validation vs brute force on small random tournaments ----
def validate():
    import random
    from itertools import permutations
    random.seed(1)
    def brute(N, arc_dir):
        V = list(range(N))
        best = N
        for perm in permutations(V):
            # backedge omega
            adj = [set() for _ in range(N)]
            posn = {v:i for i,v in enumerate(perm)}
            for a in range(N):
                for b in range(a+1,N):
                    if posn[a] < posn[b]:
                        early, late = a, b
                    else:
                        early, late = b, a
                    # backward arc late->early
                    if arc_dir[(late, early)]:
                        adj[a].add(b); adj[b].add(a)
            # max clique
            bestc=[0]
            def bk(R,Pp,X):
                if not Pp and not X:
                    bestc[0]=max(bestc[0],len(R));return
                if len(R)+len(Pp)<=bestc[0]:return
                for v in list(Pp):
                    bk(R|{v},Pp&adj[v],X&adj[v]); Pp=Pp-{v}; X=X|{v}
            bk(set(),set(range(N)),set())
            best=min(best,bestc[0])
        return best
    ok=True
    for trial in range(40):
        N = random.randint(3,6)
        arc_dir={}
        for i in range(N):
            for j in range(i+1,N):
                if random.random()<0.5:
                    arc_dir[(i,j)]=True; arc_dir[(j,i)]=False
                else:
                    arc_dir[(i,j)]=False; arc_dir[(j,i)]=True
        b = brute(N, arc_dir)
        s = exact_omega_vec_sat(N, arc_dir)
        if b!=s:
            ok=False
            print(f"MISMATCH N={N} brute={b} sat={s} arcs={[(i,j) for (i,j),d in arc_dir.items() if d]}")
    print("VALIDATION", "PASS" if ok else "FAIL", "(40 random tournaments n<=6)")
    return ok

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "validate"
    if cmd == "validate":
        validate()
