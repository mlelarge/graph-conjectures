#!/usr/bin/env python3
"""
ADVERSARIAL verification of the L1 splice argument (proof_condL_dicut_acyclicity.md).

We do NOT trust the prose. For each directed Hajos join D = D1 v D2 we:

  (T1) Directly verify the LOWER BOUND chi_vec(D) >= min(chi_vec(D1),chi_vec(D2))
       by brute computation, over a wide and adversarial family of pieces
       (sym cycles, directed cycles, random strong digraphs, asymmetric pieces,
        pieces of minimal size 2).

  (T2) Directly verify the SPLICE CLAIM that is the heart of L1's proof:
       for EVERY 2-dicolouring phi of D (when one exists), at least one side
       restriction phi_i is a valid 2-dicolouring of D_i = D[S_i] + interface arc.
       This is the contrapositive engine. If it EVER fails, L1's proof is broken.

  (T3) Independently CONSTRUCT the splice cycle: take phi a k-dicolouring of D,
       suppose (adversarially) we force both sides to fail by picking phi that
       is invalid -- instead, when D IS k-dicolourable but we look at the
       boundary, verify that the constructed object C = (C1-uv1) u (C2-v2w) u {uw}
       is genuinely a simple directed cycle whenever C1, C2 exist. We synthesise
       C1, C2 as monochromatic dicycles through the deleted arcs and check the
       splice is a simple dicycle in D (steps 1-3 of the proof).

  (T4) CRITICALITY DESCENT (Prop 4.2 / L3): for 3-dicritical joins, verify both
       pieces are 3-dicritical.

A single failure in T1 or T2 kills the corresponding step.
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h2_oracle as O
from cond_l_hajos_lb_check import hajos_join, all_2dicolourings


def is_simple_dicycle(n, arcs_list, oadj_check_arcs):
    """arcs_list: list of (a,b). Check it is a single simple directed cycle:
    each vertex appearing has in=out=1, arcs form one cycle, all arcs in the
    allowed set oadj_check_arcs (a set of (a,b))."""
    if not arcs_list:
        return False
    verts = set()
    outd = {}
    ind = {}
    for (a, b) in arcs_list:
        if (a, b) not in oadj_check_arcs:
            return False
        verts.add(a); verts.add(b)
        outd[a] = outd.get(a, 0) + 1
        ind[b] = ind.get(b, 0) + 1
    for v in verts:
        if outd.get(v, 0) != 1 or ind.get(v, 0) != 1:
            return False
    # connectivity / single cycle: follow from any start
    succ = {a: b for (a, b) in arcs_list}
    start = next(iter(verts))
    seen = [start]
    cur = succ[start]
    while cur != start:
        if cur in seen:
            return False
        seen.append(cur)
        if cur not in succ:
            return False
        cur = succ[cur]
    return len(seen) == len(verts)


def mono_dicycles_through_arc(n, arcs, colours, arc):
    """Find a monochromatic (in colours) simple directed cycle using `arc`,
    or None. Brute DFS."""
    (a0, b0) = arc
    if colours[a0] != colours[b0]:
        return None
    col = colours[a0]
    oadj = O.out_adj(n, arcs)
    # find a directed path from b0 back to a0 using only color-col vertices.
    target = a0
    path = [b0]
    onp = {b0}
    if colours[b0] != col:
        return None

    def dfs(u):
        if u == target:
            return list(path)
        for w in oadj[u]:
            if w == target:
                return path + [w]
            if w not in onp and colours[w] == col:
                path.append(w); onp.add(w)
                r = dfs(w)
                if r is not None:
                    return r
                path.pop(); onp.discard(w)
        return None
    # special: if b0 connects directly back
    pth = dfs(b0)
    if pth is None:
        return None
    # pth is b0 ... a0 ; cycle arcs = arc + consecutive arcs of pth
    cyc = [arc]
    for i in range(len(pth) - 1):
        cyc.append((pth[i], pth[i + 1]))
    return cyc


def random_strong_digraph(rng, n, p, force_digons=0.3):
    """Random small digraph; keep only if strong & min in/out>=1."""
    for _ in range(60):
        arcs = set()
        for a in range(n):
            for b in range(n):
                if a != b and rng.random() < p:
                    arcs.add((a, b))
                    if rng.random() < force_digons:
                        arcs.add((b, a))
        if not arcs:
            continue
        # need each vertex to have an out and in arc and be strong
        outd = [0]*n; ind=[0]*n
        for (a,b) in arcs:
            outd[a]+=1; ind[b]+=1
        if any(outd[v]==0 or ind[v]==0 for v in range(n)):
            continue
        if O.is_strong(n, frozenset(arcs)):
            return n, frozenset(arcs)
    return None


def collect_pieces():
    """A diverse adversarial pool of pieces, each with at least one arc."""
    pool = []
    # sym cycles chi=3
    for m in (3,5,7):
        pool.append(O.sym_cycle(m))
    # directed cycles chi=2
    for m in (3,4,5):
        pool.append((m, frozenset((i,(i+1)%m) for i in range(m))))
    # bidirected complete graph K2-ish? digon = chi=2 base. K3 bidirected chi=3? no, that's sym C3.
    # bidirected K4 (chi=2? each color class must be acyclic; K4 bidir needs... chi=2 fails since any 2 vtx same color => digon => dicycle). chi=4 actually? digon=2cycle. independent set in underlying. chi_vec(bidir K_m)=ceil(m/?) ... just include it.
    K4 = frozenset((a,b) for a in range(4) for b in range(4) if a!=b)
    pool.append((4, K4))
    # a 2-vertex digon (minimal piece, chi=2)
    pool.append((2, frozenset({(0,1),(1,0)})))
    # random
    rng = random.Random(12345)
    for _ in range(15):
        n = rng.choice([3,4,5,6])
        r = random_strong_digraph(rng, n, rng.choice([0.4,0.5,0.6]))
        if r is not None:
            pool.append((r[0], frozenset(r[1])))
    return pool


def test_lower_bound_and_splice():
    pool = collect_pieces()
    lb_fail = []
    splice_fail = []
    splice_construct_fail = []
    total = 0
    rng = random.Random(99)
    # cache chi
    chi = {}
    def getchi(n,A):
        key=O.canon(n,A)
        if key not in chi: chi[key]=O.chi_vec(n,A)
        return chi[key]

    for (n1,A1) in pool:
        for (n2,A2) in pool:
            A1s=set(A1); A2s=set(A2)
            arcs1=list(A1s); arcs2=list(A2s)
            # try a sample of arc choices to keep runtime bounded
            for (u,v1) in arcs1:
                for (v2,w) in arcs2:
                    if u==v1 or v2==w:
                        continue
                    total += 1
                    c1=getchi(n1,A1s); c2=getchi(n2,A2s)
                    n,arcs,v_lab,u_img,w_img,S1,S2 = hajos_join(n1,A1s,u,v1,n2,A2s,v2,w)
                    cj = O.chi_vec(n,arcs)
                    if cj < min(c1,c2):
                        lb_fail.append((n1,A1s,u,v1,n2,A2s,v2,w,c1,c2,cj))
                    # T2: splice claim -- every 2-dicolouring restricts validly on a side
                    if n <= 11:  # brute over 2-colourings only when small
                        # build label maps
                        d2map={}; nxt=n1
                        for x in range(n2):
                            d2map[x]= v_lab if x==v2 else nxt
                            if x!=v2: nxt+=1
                        # piece1 = D[S1]+(u,v_lab) ; in join labels S1=0..n1-1 identity
                        piece1_arcs = set((a,b) for (a,b) in arcs if a in S1 and b in S1)
                        piece1_arcs.add((u_img, v_lab))
                        piece2_arcs = set((a,b) for (a,b) in arcs if a in S2 and b in S2)
                        piece2_arcs.add((v_lab, w_img))
                        oadj1 = None
                        for phi in all_2dicolourings(n,arcs):
                            # restriction valid on side1?
                            def valid(side_verts, parcs):
                                oadj={vv:set() for vv in side_verts}
                                for (a,b) in parcs:
                                    oadj[a].add(b)
                                for c in (0,1):
                                    sub={vv for vv in side_verts if phi[vv]==c}
                                    if O._has_dicycle_in_subset(oadj, sub):
                                        return False
                                return True
                            ok1 = valid(S1, piece1_arcs)
                            ok2 = valid(S2, piece2_arcs)
                            if not (ok1 or ok2):
                                splice_fail.append((n,arcs,phi))
                                break
    return total, lb_fail, splice_fail


def test_splice_is_simple_cycle():
    """T3: when both side-restrictions of some phi fail (we manufacture this by
    using a phi that is NOT a valid dicolouring of D but IS chosen so both sides
    have a mono dicycle through the deleted arc), verify the spliced object is a
    genuine simple directed cycle of D. This validates proof step 3 directly."""
    pool = collect_pieces()
    constructed = 0
    bad = []
    rng = random.Random(7)
    for (n1,A1) in pool:
        for (n2,A2) in pool:
            A1s=set(A1); A2s=set(A2)
            for (u,v1) in list(A1s):
                for (v2,w) in list(A2s):
                    if u==v1 or v2==w: continue
                    n,arcs,v_lab,u_img,w_img,S1,S2 = hajos_join(n1,A1s,u,v1,n2,A2s,v2,w)
                    arcset=set(arcs)
                    if n>11: continue
                    # piece arc sets
                    piece1_arcs = set((a,b) for (a,b) in arcs if a in S1 and b in S1); piece1_arcs.add((u_img,v_lab))
                    piece2_arcs = set((a,b) for (a,b) in arcs if a in S2 and b in S2); piece2_arcs.add((v_lab,w_img))
                    # enumerate colourings of the WHOLE vertex set with phi(u)=phi(v)=phi(w)
                    # and look for phi where side1 has mono dicycle thru (u,v) AND
                    # side2 has mono dicycle thru (v,w). Then splice and check.
                    for bits in itertools.product((0,1), repeat=n):
                        if not (bits[u_img]==bits[v_lab]==bits[w_img]):
                            continue
                        col=list(bits)
                        c1 = mono_dicycles_through_arc(n1 if False else n, frozenset(piece1_arcs),
                                                       {x:col[x] for x in S1}, (u_img,v_lab))
                        # need to run on piece1 as its own digraph over S1 labels
                        c1 = mono_dicycles_through_arc(n, frozenset(piece1_arcs), col, (u_img,v_lab))
                        if c1 is None: continue
                        c2 = mono_dicycles_through_arc(n, frozenset(piece2_arcs), col, (v_lab,w_img))
                        if c2 is None: continue
                        # splice: (C1 - (u,v)) u (C2 - (v,w)) u {(u,w)}
                        spliced = [e for e in c1 if e!=(u_img,v_lab)] + \
                                  [e for e in c2 if e!=(v_lab,w_img)] + [(u_img,w_img)]
                        constructed += 1
                        if not is_simple_dicycle(n, spliced, arcset):
                            bad.append((n,arcs,u_img,v_lab,w_img,c1,c2,spliced))
                        # one example per join is enough
                        break
                    # limit
    return constructed, bad


def test_criticality_descent():
    """L3 / Prop 4.2: for 3-dicritical D=D1vD2, both pieces 3-dicritical."""
    pool = collect_pieces()
    fails=[]
    tested=0
    def is_dicritical(n,A,k):
        if O.chi_vec(n,A)!=k: return False
        arcs=list(A)
        for a in arcs:
            sub=frozenset(x for x in A if x!=a)
            if O.chi_vec(n,sub)>=k:
                return False
        return True
    for (n1,A1) in pool:
        for (n2,A2) in pool:
            A1s=set(A1);A2s=set(A2)
            for (u,v1) in list(A1s):
                for (v2,w) in list(A2s):
                    if u==v1 or v2==w: continue
                    n,arcs,*_=hajos_join(n1,A1s,u,v1,n2,A2s,v2,w)
                    if n>9: continue
                    if not is_dicritical(n,arcs,3): continue
                    tested+=1
                    # pieces D1=(n1,A1s with arc u->v1), D2 similarly: but the
                    # *recovered* pieces are D[S1]+(u,v) etc. Use original D1,D2.
                    d1crit=is_dicritical(n1,frozenset(A1s),3)
                    d2crit=is_dicritical(n2,frozenset(A2s),3)
                    if not (d1crit and d2crit):
                        fails.append((n1,A1s,n2,A2s,d1crit,d2crit))
    return tested, fails


def main():
    print("=== T1+T2: lower bound + splice claim (heart of L1) ===")
    total, lb_fail, splice_fail = test_lower_bound_and_splice()
    print(f"  joins tested: {total}")
    print(f"  LOWER BOUND failures: {len(lb_fail)}")
    for f in lb_fail[:3]: print("    LB FAIL:", f)
    print(f"  SPLICE-CLAIM failures (both sides invalid for some 2-dicolouring): {len(splice_fail)}")
    for f in splice_fail[:3]: print("    SPLICE FAIL:", f)

    print("=== T3: spliced object is a genuine simple directed cycle ===")
    constructed, bad = test_splice_is_simple_cycle()
    print(f"  splices constructed & checked: {constructed}; NOT-a-simple-cycle: {len(bad)}")
    for b in bad[:3]: print("    BAD SPLICE:", b)

    print("=== T4: criticality descent (Prop 4.2 / L3) ===")
    tested, cf = test_criticality_descent()
    print(f"  3-dicritical joins tested: {tested}; descent failures: {len(cf)}")
    for f in cf[:3]: print("    DESCENT FAIL:", f)

    ok = (len(lb_fail)==0 and len(splice_fail)==0 and len(bad)==0 and len(cf)==0)
    print("=== OVERALL:", "PASS" if ok else "FAIL", "===")
    return 0 if ok else 1


if __name__=="__main__":
    sys.exit(main())
