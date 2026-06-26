#!/usr/bin/env python3
"""Exhibit the witnessing min-Kraft covers for k=2,3,4 and confirm equality
at 1/2 is NOT forced to all-c=1.  This directly tests the proposal's CONFIRM
clause: 'equality forcing all-c=1 (i.e. k=1)'."""
import itertools
from fractions import Fraction

def affine_subcubes(m):
    cube = list(range(1 << m))
    subs = []
    for fixed in range(m + 1):
        for coords in itertools.combinations(range(m), fixed):
            for vals in itertools.product((0, 1), repeat=fixed):
                req = dict(zip(coords, vals))
                pts = frozenset(p for p in cube
                                if all(((p >> c) & 1) == v for c, v in req.items()))
                subs.append((pts, fixed))  # dim = m-fixed; c = 1+fixed
    return subs, frozenset(cube)

for k in range(2, 5):
    m = k - 1
    subs, full = affine_subcubes(m)
    # min-Kraft exact cover, recover the actual cover used
    pts = sorted(full); idx = {p:i for i,p in enumerate(pts)}; N=len(pts)
    target=(1<<N)-1
    opts=[]
    for sub,fixed in subs:
        bm=0
        for p in sub: bm|=1<<idx[p]
        if bm: opts.append((bm, Fraction(1,2**(1+fixed)), 1+fixed, sub))
    import heapq
    best={0:(Fraction(0),[])}; pq=[(Fraction(0),0,[])]
    found=None
    while pq:
        w,mask,cov=heapq.heappop(pq)
        if mask==target: found=(w,cov); break
        if w>best[mask][0]: continue
        for bm,wt,c,sub in opts:
            nm=mask|bm; nw=w+wt
            if nm not in best or nw<best[nm][0]:
                best[nm]=(nw,cov+[(c,sorted(sub))]); heapq.heappush(pq,(nw,nm,cov+[(c,sorted(sub))]))
    w,cov=found
    cs=[c for c,_ in cov]
    print(f"k={k} (Omega=2^{m}): min Kraft sum = {w}")
    print(f"   cover = {cov}")
    print(f"   c-values used = {cs}; all c==1 ? {all(c==1 for c in cs)}")
    print(f"   equality at 1/2 ? {w==Fraction(1,2)}; forces all-c=1 ? {all(c==1 for c in cs)}")
