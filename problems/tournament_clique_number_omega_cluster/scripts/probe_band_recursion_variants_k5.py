import os
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, networkx as nx
from search_4critical_circulant import circ_arcs
from ground_lex_compose_c3 import lex_compose, ac_gen, c3

def build_Y(n):
    nAC,aAC=n,circ_arcs(n,ac_gen(n)); nC,aC=c3()
    N1,A1=lex_compose(nAC,aAC,nC,aC); N2,A2=lex_compose(N1,A1,nC,aC)
    return N2, core.beats_matrix(N2,A2), (n-1)//2

def coords(flat):
    h1=flat%3; r=flat//3; h2=r%3; t=r//3; return t,h2,h1
def cval(t,m): return 3 if t==0 else (2 if 1<=t<=m else 1)
def d(h): return 2 if h==0 else 1

def clq(N,beats,order):
    g=nx.Graph(); g.add_nodes_from(order); L=len(order)
    for i in range(L):
        a=order[i]
        for j in range(i+1,L):
            b=order[j]
            if beats[b][a]: g.add_edge(a,b)
    return max((len(c) for c in nx.find_cliques(g)),default=0)

def run(n,keyfn,deleted):
    N,beats,m=build_Y(n)
    items=[]
    for flat in range(N):
        if flat==deleted: continue
        t,h2,h1=coords(flat)
        items.append((keyfn(t,h2,h1,m),flat))
    items.sort()
    return clq(N,beats,[f for _,f in items])

# inner-c order on X used d(h2),c(t). The OUTER added C3 -> d(h1).
keys = {
 "d1_then_(d2,c)": lambda t,h2,h1,m:(d(h1),d(h2),cval(t,m),t,h2,h1),
 "(d2,c)_then_d1": lambda t,h2,h1,m:(d(h2),cval(t,m),d(h1),t,h2,h1),
 "sum_c_outer+inner": lambda t,h2,h1,m:(d(h1)+d(h2)+cval(t,m),t,h2,h1),  # merged-sum-ish
 "Xfirst_recursive": lambda t,h2,h1,m:(d(h1),d(h2),cval(t,m)),  # ties broken arbitrarily
 "innerX_d2c_outerd1_interleave": lambda t,h2,h1,m:(d(h2)+cval(t,m), d(h1), t,h2,h1),
}
for name,kf in keys.items():
    full=run(7,kf,-1); dele=run(7,kf,0)
    print(f"{name:38s} n7 full={full} del={dele}")
