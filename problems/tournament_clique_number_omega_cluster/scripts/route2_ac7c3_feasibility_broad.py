"""!!! INVALID / SUPERSEDED (2026-06-12): this script passed build_ac_c3()'s 3rd
return value (=3, the inner C3 size) as the lattice order instead of n=21, so the
feasibility lattice and profile indexing are wrong. Its output is meaningless.
H19 for AC_7[C3] was settled INSTEAD by direct no-K6 SAT (omega_vec(C3[AC_7[C3]])=5,
H19 HOLDS); see docs/h19_cancellation_argument_sketch.md §13. Kept only for history.
!!!"""
"""Broader feasibility probe for C3[AC_7[C3]]: include NON-escaper optimal orders.

Feasibility (terminal-reachable) does NOT require an escaper (Escaper Necessity governs
only the stricter cycle-free condition), so the earlier escaper-only test was too narrow.
Here we collect a diverse set of OPTIMAL (clique-4) orders of AC_7[C3] via local search
(swap descent from random starts) + the append-escapers, and test all triples for
terminal_reachable.  A feasible triple => omega_vec(C3[AC_7[C3]]) <= 5 (H19 holds for this
H).  Broad failure is evidence (bounded) that omega_vec(C3[AC_7[C3]]) >= 6 -- which would be
a FIRST omega_vec>=6 object, not merely an H19 failure.  Foreground.
"""
import sys, os, time, itertools, random
from collections import deque
sys.path.insert(0, os.path.dirname(__file__))
import core, networkx as nx
from confirm_deletion_template_k4 import build as build_ac_c3, order_template as ac_c3_deletion_order
from h25_path_feasibility import omega_be_seq, profile_of
from route2_credit_deadlock import analyse_triple, demand_relief_map

def clique_of(beats, order):
    a=len(order); g=nx.Graph(); g.add_nodes_from(range(a))
    for i in range(a):
        for j in range(i+1,a):
            if beats[order[j]][order[i]]: g.add_edge(i,j)
    return max((len(c) for c in nx.find_cliques(g)), default=1)

def local_min_order(beats, n, k, rng, max_iter=400):
    """swap descent to an order of backedge clique k (optimum)."""
    order=list(range(n)); rng.shuffle(order); cur=clique_of(beats,order)
    it=0
    while cur>k and it<max_iter:
        it+=1; improved=False
        idxs=list(range(n-1)); rng.shuffle(idxs)
        for i in idxs:
            order[i],order[i+1]=order[i+1],order[i]
            c=clique_of(beats,order)
            if c<cur: cur=c; improved=True; break
            order[i],order[i+1]=order[i+1],order[i]   # undo
        if not improved:
            # random kick
            i,j=rng.randrange(n),rng.randrange(n); order[i],order[j]=order[j],order[i]
            cur=clique_of(beats,order)
    return order if cur==k else None

def dsig(prof,m,k):
    dm=demand_relief_map(prof,m,k); return tuple(dm[t]["successor_level"] for t in sorted(dm))

def main():
    t0=time.time(); rng=random.Random(11)
    n, arcs, m = build_ac_c3(7); k=4
    beats=core.beats_matrix(n,arcs)
    profs={}
    # (a) append-escapers from swap neighborhood
    base=tuple(ac_c3_deletion_order(m,deleted=0)); queue=deque([(base,0)]); seen={base}
    while queue and len(seen)<=4000 and len(profs)<12:
        tau,d=queue.popleft()
        if omega_be_seq(beats,list(tau))==k-1:
            p=profile_of(beats,tuple(list(tau)+[0]))
            if p[0][n]==k: profs[p]=("escaper",dsig(p,n,k))
        if d<5:
            for i in range(len(tau)-1):
                nb=list(tau); nb[i],nb[i+1]=nb[i+1],nb[i]; nb=tuple(nb)
                if nb not in seen: seen.add(nb); queue.append((nb,d+1))
    n_esc=len(profs)
    # (b) local-search optimal orders (mostly NON-escaper)
    for _ in range(120):
        o=local_min_order(beats,n,k,rng)
        if o is not None:
            p=profile_of(beats,tuple(o))
            if p not in profs: profs[p]=("local",dsig(p,n,k))
        if len(profs)>=44: break
    P=list(profs.keys()); meta=[profs[p] for p in P]
    n_escapers=sum(1 for p in P if any(v>k for v in p[0]))  # f[t]>k impossible; escaper via D
    n_esc_maps=sum(1 for mt in meta if any(s>k for s in mt[1]))
    print(f"AC_7[C3]: collected {len(P)} distinct optimal profiles "
          f"({n_esc} escaper-seeded + {len(P)-n_esc} local); {n_esc_maps} have escaper demand-map "
          f"[{time.time()-t0:.1f}s]", flush=True)
    print(f"  distinct demand-maps: {sorted({tuple(mt[1]) for mt in meta})}", flush=True)

    feasible=None; n_feas=0; tested=0; cap=len(P)
    for trip in itertools.product(range(cap),repeat=3):
        tested+=1
        r=analyse_triple([P[trip[0]],P[trip[1]],P[trip[2]]],m,k,record_deadlocks=False)
        if r["terminal_reachable"]:
            n_feas+=1
            if feasible is None: feasible=(trip,r);
    print(f"\ntested {tested} ordered triples over {cap} profiles:", flush=True)
    print(f"  FEASIBLE (terminal reachable): {n_feas}", flush=True)
    if feasible:
        trip,r=feasible
        print(f"  *** FEASIBLE TRIPLE -> omega_vec(C3[AC_7[C3]]) <= {k+1}: H19 HOLDS for AC_7[C3]", flush=True)
        print(f"      demand-maps {[meta[i][1] for i in trip]}, lattice reach={r['n_reachable']}/{r['n_safe']}", flush=True)
    else:
        print(f"  NO feasible triple over {cap} diverse optimal profiles (escaper + local-search).", flush=True)
        print(f"  -> bounded evidence that omega_vec(C3[AC_7[C3]]) >= 6 (a FIRST omega_vec>=6 object).", flush=True)
        print(f"     Decisive check would be a no-K6 lower bound on the order-63 product (SAT-walled).", flush=True)
    print(f"\nelapsed {time.time()-t0:.1f}s", flush=True)

if __name__=="__main__":
    main()
