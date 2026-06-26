#!/usr/bin/env python3
import os
import sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_c6_attack import build_ACC3
from rt_c6_sat import omega_vec_leq, exact_omega_vec_sat

def to_index(V, arc):
    idx = {v:i for i,v in enumerate(V)}
    N = len(V)
    arc_dir = {}
    for a in V:
        for b in V:
            if a==b: continue
            arc_dir[(idx[a], idx[b])] = arc[(a,b)]
    return N, arc_dir, idx

def run_full(n):
    V, arc, m = build_ACC3(n)
    N, arc_dir, idx = to_index(V, arc)
    t=time.time()
    # check omega_vec == 4: omega_vec<=4 SAT and omega_vec<=3 UNSAT
    sat4,c4 = omega_vec_leq(N, arc_dir, 4)
    sat3,c3 = omega_vec_leq(N, arc_dir, 3)
    print(f"[full n={n} N={N}] omega_vec<=4: {'SAT' if sat4 else 'UNSAT'} (clauses {c4}); "
          f"omega_vec<=3: {'SAT' if sat3 else 'UNSAT'} (clauses {c3})  "
          f"=> omega_vec {'==4' if (sat4 and not sat3) else 'NOT 4!!'}  [{time.time()-t:.1f}s]")
    return sat4 and not sat3

def run_delete(n, vdel=(0,0)):
    V, arc, m = build_ACC3(n)
    Vk = [v for v in V if v != vdel]
    idx = {v:i for i,v in enumerate(Vk)}
    N = len(Vk)
    arc_dir = {}
    for a in Vk:
        for b in Vk:
            if a==b: continue
            arc_dir[(idx[a],idx[b])] = arc[(a,b)]
    t=time.time()
    sat3,c3 = omega_vec_leq(N, arc_dir, 3)
    sat2,c2 = omega_vec_leq(N, arc_dir, 2)
    print(f"[del {vdel} n={n} N={N}] omega_vec<=3: {'SAT' if sat3 else 'UNSAT'}; "
          f"omega_vec<=2: {'SAT' if sat2 else 'UNSAT'}  "
          f"=> omega_vec {'==3' if (sat3 and not sat2) else 'NOT 3!!'}  [{time.time()-t:.1f}s]")
    return sat3 and not sat2

if __name__ == "__main__":
    mode = sys.argv[1]
    ns = [int(x) for x in sys.argv[2:]]
    for n in ns:
        if mode=="full": run_full(n)
        elif mode=="del": run_delete(n)
        elif mode=="both":
            run_full(n); run_delete(n)
