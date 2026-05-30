#!/usr/bin/env python3
"""
Sweep: does the even-leaf-path B-parity condition control whether a 2-Hajos tree
join lands in the 2-extremal class? For each small plane tree and each A/B labeling
and gadget choice, build the join and record (parityOK, is_2extremal, lambda, chi).

HYPOTHESIS under test (the brief's "repair"):
  parityOK  <=>  the tree-join output is 2-extremal (given gadgets are 2-extremal
  H_2 members and the tree is valid).

We DO NOT assume; we tabulate. Counterexamples to either direction are reported.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from two_hajos_tree_join import build_tree_join, even_leaf_parity
from enumerate_2extremal_v0_recon import sym_cycle, is_2extremal, lambda_D, chi_vec

C3=(3,sym_cycle(3),(0,1))
C5=(5,sym_cycle(5),(0,1))

def make_path(k):
    """Path tree on k+1 nodes 0-1-...-k."""
    m=k+1; root=0
    children={i:[i+1] for i in range(k)}; children[k]=[]
    edges=[(i,i+1) for i in range(k)]
    return m,root,children,edges

def make_star(k):
    """Star: hub 0, leaves 1..k."""
    m=k+1; root=0
    children={0:list(range(1,k+1))}
    for i in range(1,k+1): children[i]=[]
    edges=[(0,i) for i in range(1,k+1)]
    return m,root,children,edges

def make_caterpillar():
    """spine 0-1-2 with an extra leaf 3 attached to 1: edges (0,1),(1,2),(1,3).
    leaves: 0,2,3."""
    m=4; root=0
    children={0:[1],1:[2,3],2:[],3:[]}
    edges=[(0,1),(1,2),(1,3)]
    return m,root,children,edges

def sweep(trees, gadget=C3, maxn=9):
    rows=[]
    for name,(m,root,children,edges) in trees:
        E=len(edges)
        for bits in itertools.product('AB',repeat=E):
            labels={edges[i]:bits[i] for i in range(E)}
            # A-edges need gadget; build gadgets dict
            gadgets={edges[i]:gadget for i in range(E) if bits[i]=='A'}
            res=build_tree_join(m,edges,parent={},children=children,root=root,labels=labels,gadgets=gadgets)
            if res is None: continue
            arcs,n=res
            if n>maxn or n<3: continue
            ev,par=even_leaf_parity(edges,labels,children,root,m)
            ext=is_2extremal(arcs,n)
            rows.append((name,''.join(bits),ev,ext,n))
    return rows

if __name__=="__main__":
    trees=[('path2',make_path(2)),('path3',make_path(3)),
           ('star3',make_star(3)),('star4',make_star(4)),
           ('caterpillar',make_caterpillar())]
    rows=sweep(trees, gadget=C3, maxn=9)
    # tabulate agreement parityOK <=> 2extremal
    agree=disagree=0
    bad=[]
    for (name,bits,ev,ext,n) in rows:
        if ev==ext: agree+=1
        else:
            disagree+=1; bad.append((name,bits,ev,ext,n))
    print(f"# parity-necessity sweep (gadget=C3), rows={len(rows)}")
    print(f"agree(parityOK==2extremal)={agree}  DISAGREE={disagree}")
    # show distribution
    from collections import Counter
    c=Counter((ev,ext) for (_,_,ev,ext,_) in rows)
    print("table (parityOK,2extremal)->count:",dict(c))
    if bad:
        print("DISAGREEMENTS (parityOK != 2extremal):")
        for r in bad[:30]: print("  ",r)
    else:
        print("No disagreements: parityOK <=> 2extremal across all sampled trees.")

    # second pass with C5 gadget (independent gadget family)
    trees2=[('path2',make_path(2)),('star3',make_star(3)),('caterpillar',make_caterpillar())]
    rows2=sweep(trees2, gadget=C5, maxn=11)
    a2=sum(1 for (_,_,ev,ext,_) in rows2 if ev==ext); d2=len(rows2)-a2
    c2=Counter((ev,ext) for (_,_,ev,ext,_) in rows2)
    print(f"# C5-gadget sweep rows={len(rows2)} agree={a2} DISAGREE={d2} table={dict(c2)}")
    print(f"# COMBINED rows={len(rows)+len(rows2)} disagreements={disagree+d2}")
