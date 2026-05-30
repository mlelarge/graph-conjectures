#!/usr/bin/env python3
"""
Constructor for the 2-Hajos tree join (Def 9.1, arXiv:2304.04690), plus a SOUND
recursive recognizer scaffold. Imports validated primitives.

Def 9.1 (as stated in the task brief):
  - plane tree T with >=2 edges; partition E(T)=(A,B) such that EVERY leaf-to-leaf
    path uses an EVEN number of B-edges;
  - replace each A-edge u_i v_i by a digraph D_i (with digon [u_i,v_i] in A(D_i))
    minus that digon -- i.e. D_i is some smaller H_2 member, and we glue it in by
    identifying the digon endpoints u_i,v_i with the two tree-nodes of that edge,
    deleting the digon's two arcs;
  - replace each B-edge by a digon (two arcs);
  - add the directed peripheral cycle on the circular leaf order.
  - empty A => generalised wheel.

We implement the construction for a given plane tree given as:
  - nodes 0..m-1, edges as ordered list with a fixed plane embedding via children lists,
  - an A/B label per edge,
  - for each A-edge, a "gadget" digraph (n_i, arcs_i) with a designated digon (p_i,q_i).
The leaf circular order is the order leaves are visited in a DFS of the plane tree.

This is intentionally a careful, testable constructor; we validate it reproduces
known H_2 members (sym C3 join, wheels) before trusting it as an oracle component.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enumerate_2extremal_v0_recon import (
    sym_cycle, is_2extremal, lambda_D, chi_vec, canonical, is_strong,
    is_2connected, is_eulerian_deg,
)

def leaf_circular_order(children, root, m):
    """Plane-embedding circular order of the leaves of the UNROOTED tree.
    A leaf of the unrooted tree = node of (unrooted) degree 1. We obtain the
    cyclic boundary order by an Euler tour of the plane tree starting at root;
    the order in which degree-1 nodes are first encountered is the circular order.
    The root counts as a leaf iff it has exactly one child (unrooted degree 1)."""
    # unrooted degree
    deg=[0]*m
    for u in range(m):
        for c in children[u]:
            deg[u]+=1; deg[c]+=1
    order=[]
    seen=set()
    def visit(u):
        if deg[u]==1 and u not in seen:
            seen.add(u); order.append(u)
    # Euler tour: pre-order capturing leaves; root first if it is a leaf
    def dfs(u):
        visit(u)
        for c in children[u]:
            dfs(c)
    dfs(root)
    return order

def build_tree_join(m, edges, parent, children, root, labels, gadgets):
    """
    m: number of tree nodes.
    edges: list of (u,v) parent->child tree edges.
    labels: dict edge-> 'A' or 'B'.
    gadgets: dict edge-> (n_i, frozenset arcs_i, (p_i,q_i)) for A-edges. The gadget's
             digon (p_i,q_i) is identified with (u,v); p_i->u, q_i->v.
    Returns (arcs, n_total) on relabeled vertices, or None if construction invalid.
    Vertices: tree nodes keep ids 0..m-1; gadget-internal vertices get fresh ids.
    """
    arcs=set()
    nxt=m
    for e in edges:
        u,v=e
        lab=labels[e]
        if lab=='B':
            arcs.add((u,v)); arcs.add((v,u))   # digon
        else:
            ni,ai,(p,q)=gadgets[e]
            # map gadget vertex p->u, q->v, others fresh
            mp={}
            for x in range(ni):
                if x==p: mp[x]=u
                elif x==q: mp[x]=v
                else: mp[x]=nxt; nxt+=1
            for (a,b) in ai:
                if (a,b)==(p,q) or (a,b)==(q,p):  # delete the designated digon
                    continue
                x,y=mp[a],mp[b]
                if x!=y: arcs.add((x,y))
    # peripheral directed cycle on circular leaf order
    leaves=leaf_circular_order(children, root, m)
    L=len(leaves)
    if L>=2:
        for i in range(L):
            a=leaves[i]; b=leaves[(i+1)%L]
            arcs.add((a,b))
    return frozenset(arcs), nxt

def even_leaf_parity(edges, labels, children, root, m):
    """Check EVERY leaf-to-leaf path uses an even number of B-edges.
    Equiv: assign each node a parity = (#B-edges on root-path) mod 2; then a
    leaf-leaf path B-count = parity(l1) xor parity(l2) (B count along tree path).
    Even for ALL leaf pairs  <=>  all leaves share the same parity."""
    par={root:0}
    # build adjacency parent->children with edge labels
    elab={}
    for e in edges: elab[e]=labels[e]
    def dfs(u):
        for c in children[u]:
            b=1 if elab[(u,c)]=='B' else 0
            par[c]=par[u]^b
            dfs(c)
    dfs(root)
    deg=[0]*m
    for u in range(m):
        for c in children[u]:
            deg[u]+=1; deg[c]+=1
    leaves=[u for u in range(m) if deg[u]==1]
    parities={par[l] for l in leaves}
    return len(parities)==1, {l:par[l] for l in leaves}

# ---- validation cases ----
def case_path2_AA():
    """Path tree 0-1-2, both edges A, each gadget = sym C3 (digon (0,1) designated).
    Should reproduce a 2-extremal in H_2 (a directed Hajos-like join)."""
    m=3
    edges=[(0,1),(1,2)]; parent={1:0,2:1}; children={0:[1],1:[2],2:[]}; root=0
    labels={(0,1):'A',(1,2):'A'}
    # gadget sym C3 on vertices {0,1,2}; designated digon (0,1)
    c3=sym_cycle(3); gad=(3,c3,(0,1))
    gadgets={(0,1):gad,(1,2):gad}
    return build_tree_join(m,edges,parent,children,root,labels,gadgets), (edges,labels,children,root,m)

def case_star_wheel(rim):
    """Star tree: root=hub(0), leaves 1..rim, all edges B. Generalised wheel W_rim.
    Every leaf-leaf path = 2 B-edges = even. Empty A."""
    m=rim+1; root=0
    children={0:list(range(1,rim+1))}
    for i in range(1,rim+1): children[i]=[]
    edges=[(0,i) for i in range(1,rim+1)]
    labels={e:'B' for e in edges}
    parent={i:0 for i in range(1,rim+1)}
    return build_tree_join(m,edges,parent,children,root,labels,{}), (edges,labels,children,root,m)

if __name__=="__main__":
    print("# Validation of 2-Hajos tree join constructor")
    (arcs,n),meta=case_path2_AA()
    ev,par=even_leaf_parity(*[meta[0],meta[1],meta[2],meta[3],meta[4]])
    print(f"path2-AA: n={n} 2extremal={is_2extremal(arcs,n)} lambda={lambda_D(arcs,n)} chi={chi_vec(arcs,n)} parityOK={ev} leafpar={par}")
    print("   arcs=",sorted(arcs))
    for rim in (3,4,5):
        (arcs,n),meta=case_star_wheel(rim)
        ev,par=even_leaf_parity(meta[0],meta[1],meta[2],meta[3],meta[4])
        print(f"wheel W{rim}: n={n} 2extremal={is_2extremal(arcs,n)} lambda={lambda_D(arcs,n)} chi={chi_vec(arcs,n)} parityOK={ev}")
