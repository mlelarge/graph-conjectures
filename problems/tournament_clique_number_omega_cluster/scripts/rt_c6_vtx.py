#!/usr/bin/env python3
"""Verify vertex-transitivity of AC_n[C3] and test deletion of NON-(0,0) vertices."""
import os
import sys, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rt_c6_attack import build_ACC3
from rt_c6_sat import omega_vec_leq

def check_vertex_transitive(n):
    """AC_n is a Cayley graph on Z/n => the map t->t+s is an automorphism of AC_n
    (arcs depend only on j-i). In the lex substitution AC_n[C3], (t,h)->(t+s, h)
    should be an automorphism for any s (since across-block arcs depend on t2-t1 and
    within-block arcs unchanged). Combined with C3's rotation h->h+1 being an
    automorphism of C3 (0->1->2->0), the map (t,h)->(t+s, h+1) gives transitivity on
    BOTH coordinates => vertex-transitive. Verify the maps are graph automorphisms."""
    V, arc, m = build_ACC3(n)
    Vset = set(V)
    def is_auto(f):
        for a in V:
            for b in V:
                if a==b: continue
                fa, fb = f(a), f(b)
                if arc[(a,b)] != arc[(fa,fb)]:
                    return False, (a,b)
        return True, None
    # block shift by s
    ok_shift = True
    for s in range(n):
        f = lambda v,s=s: ((v[0]+s)%n, v[1])
        ok,_ = is_auto(f)
        if not ok: ok_shift=False; break
    # C3 rotation
    fr = lambda v: (v[0], (v[1]+1)%3)
    ok_rot,_ = is_auto(fr)
    # transitive group generated => can map any vertex to (0,0)?
    # orbit of (0,0) under <shift, rot>
    gens = [lambda v,s=s: ((v[0]+s)%n, v[1]) for s in range(n)] + [fr]
    orbit = {(0,0)}
    frontier=[(0,0)]
    while frontier:
        x=frontier.pop()
        for g in gens:
            y=g(x)
            if y not in orbit:
                orbit.add(y); frontier.append(y)
    print(f"n={n}: block-shift automorphism={ok_shift}, C3-rotation automorphism={ok_rot}, "
          f"orbit of (0,0) size={len(orbit)} of {len(V)} => vertex-transitive={len(orbit)==len(V) and ok_shift and ok_rot}")
    return ok_shift and ok_rot and len(orbit)==len(V)

def del_arbitrary(n, vdel):
    V, arc, m = build_ACC3(n)
    Vk=[v for v in V if v!=vdel]
    idx={v:i for i,v in enumerate(Vk)}; N=len(Vk)
    arc_dir={}
    for a in Vk:
        for b in Vk:
            if a==b: continue
            arc_dir[(idx[a],idx[b])]=arc[(a,b)]
    sat3,_=omega_vec_leq(N,arc_dir,3); sat2,_=omega_vec_leq(N,arc_dir,2)
    print(f"  delete {vdel}: omega_vec {'==3' if sat3 and not sat2 else 'NOT 3'} (<=3 {sat3}, <=2 {sat2})")

if __name__=="__main__":
    for n in [7,9,11,13]:
        check_vertex_transitive(n)
    print("--- direct deletion of assorted vertices (should all give 3) ---")
    n=9
    V,arc,m=build_ACC3(n)
    for vdel in [(0,1),(0,2),(3,0),(4,0),(5,0),(2,1),(8,2)]:
        del_arbitrary(n, vdel)
