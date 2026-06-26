import sys, itertools

# Correct, order-aware test of the (2,2)-lemma.
# d_then_c order: ascending by (d(h), c(t), t, h).
# BACKEDGE between u and w (with u earlier in order, u<w): arc w->u (the LATER dominates the EARLIER).
# X backedge-independent  <=>  no pair a,b in X forms a backedge (i.e. the later one does NOT dominate the earlier one).

def make_g(m):
    n = 2*m+1
    return n, (set(range(1, m)) | {m+1})

def dval(h): return 2 if h==0 else 1
def cval(t,m,n): return 3 if t==0 else (2 if 1<=t<=m else 1)

def key(v,m,n):
    t,h=v
    return (dval(h), cval(t,m,n), t, h)

def arc(u,v,n,g):
    # arc u->v in AC_n[C3]
    tu,hu=u; tv,hv=v
    if tu!=tv:
        return ((tv-tu)%n) in g
    else:
        return (hv-hu)%3==1

def is_backedge_pair(a,b,m,n,g):
    # returns True if {a,b} is a backedge in the order (the later vertex dominates the earlier)
    ka,kb=key(a,m,n),key(b,m,n)
    if ka==kb: return False  # same vertex (shouldn't happen)
    if ka<kb:
        early,late=a,b
    else:
        early,late=b,a
    return arc(late,early,n,g)

def compute_X(s,sp,m,n,g):
    # X = d=1 vertices (h in {1,2}) dominated by BOTH (s,0) and (s',0), excluding deleted (0,0) (not d=1 anyway)
    X=[]
    for t in range(n):
        for h in (1,2):
            u=(s,0); up=(sp,0); w=(t,h)
            if arc(u,w,n,g) and arc(up,w,n,g):
                X.append(w)
    return X

def test_lemma_hyprange(m):
    """Proof hypothesis: s in [m+1,2m], s' in [1,m], delta=s-s' in g. Report backedge pairs in X."""
    n,g=make_g(m)
    counters=[]
    for s in range(m+1,2*m+1):
        for sp in range(1,m+1):
            if ((s-sp)%n) not in g: continue
            X=compute_X(s,sp,m,n,g)
            for a,b in itertools.combinations(X,2):
                if is_backedge_pair(a,b,m,n,g):
                    counters.append((m,s,sp,a,b))
    return counters

def test_lemma_all_pairs(m):
    """Maximally adversarial: ALL ordered S2 pairs (s,s'), both h=0 vertices != (0,0),
       that form a 2-clique (one arc direction). X = d=1 verts dominated by both.
       Report backedge pairs in X."""
    n,g=make_g(m)
    counters=[]
    h0=[t for t in range(n) if (t,0)!=(0,0)]  # all h=0 blocks except deleted vertex
    for s,sp in itertools.combinations(h0,2):
        u=(s,0); up=(sp,0)
        # need them to be a clique: in tournament always an arc; fine.
        X=compute_X(s,sp,m,n,g)
        for a,b in itertools.combinations(X,2):
            if is_backedge_pair(a,b,m,n,g):
                counters.append((m,s,sp,a,b))
    return counters

if __name__=="__main__":
    mode=sys.argv[1]; lo=int(sys.argv[2]); hi=int(sys.argv[3])
    fn = test_lemma_hyprange if mode=="hyp" else test_lemma_all_pairs
    allc=[]
    for m in range(lo,hi+1):
        c=fn(m); allc+=c
        print(f"m={m} n={2*m+1}: {'OK (X backedge-independent)' if not c else f'{len(c)} BACKEDGE-PAIRS e.g. {c[:3]}'}")
    print(f"TOTAL violations [{mode}] m={lo}..{hi}: {len(allc)}")
