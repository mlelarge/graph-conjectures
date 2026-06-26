import os
import math, sys, statistics
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import core, networkx as nx
from lit_reduction_test import triangle_free_process

def alpha_exact(n, edges):
    # exact independence number via complement max-clique, but use the
    # faster max_weight_clique on the complement
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    Gc = nx.complement(G)
    clq, w = nx.max_weight_clique(Gc, weight=None)
    return w

def main():
    ns = [20,30,40,50,70,100]
    cs = [1.5,2.0,2.5]; seeds=6
    rows=[]
    out=open('/tmp/alpha_fast_out.txt','w')
    def emit(s):
        print(s, flush=True); out.write(s+'\n'); out.flush()
    emit(f"{'n':>4} {'alpha_min':>9} {'dbar':>6} {'a/snln':>8} {'a/(sqn*logn)':>12}")
    for n in ns:
        chosen=None; ds=[]
        for c in cs:
            p=c/math.sqrt(n); mcap=int(p*n*(n-1)/2)
            for s in range(seeds):
                n2,edges=triangle_free_process(n,mcap,seed=1000*int(c*10)+s+n)
                if not core.is_triangle_free(n2,edges): continue
                a=alpha_exact(n2,edges); d=2*len(edges)/n2; ds.append(d)
                if chosen is None or a<chosen[0]: chosen=(a,d)
        a=chosen[0]; snln=math.sqrt(n*math.log(n)); snlogn=math.sqrt(n)*math.log(n)
        emit(f"{n:>4} {a:>9} {statistics.mean(ds):>6.2f} {a/snln:>8.4f} {a/snlogn:>12.4f}")
        rows.append((n,a))
    import numpy as np
    xs=[math.log(math.sqrt(r[0])) for r in rows]; xl=[math.log(math.log(r[0])) for r in rows]; ys=[math.log(r[1]) for r in rows]
    M=np.column_stack([np.ones(len(ys)),xs,xl]); coef,*_=np.linalg.lstsq(M,np.array(ys),rcond=None)
    emit(f"FIT log alpha = {coef[0]:.3f} + {coef[1]:.3f} log(sqrt n) + {coef[2]:.3f} loglog n")
    emit("  C (loglog exp): 0.5 => sqrt(n logn) [proposal];  1.0 => sqrt(n)*logn [P2 scale]")
    # which normalization flatter? compare coefficient of variation
    r1=[rows[i][1]/math.sqrt(rows[i][0]*math.log(rows[i][0])) for i in range(len(rows))]
    r2=[rows[i][1]/(math.sqrt(rows[i][0])*math.log(rows[i][0])) for i in range(len(rows))]
    cv1=statistics.pstdev(r1)/statistics.mean(r1); cv2=statistics.pstdev(r2)/statistics.mean(r2)
    emit(f"CV alpha/sqrt(n logn) = {cv1:.4f} ; CV alpha/(sqrtn*logn) = {cv2:.4f}")
    emit(f"trend alpha/sqrt(n logn): {r1[0]:.3f} -> {r1[-1]:.3f} (rise {r1[-1]/r1[0]:.3f})")
    emit(f"trend alpha/(sqrtn*logn): {r2[0]:.3f} -> {r2[-1]:.3f} (rise {r2[-1]/r2[0]:.3f})")
    out.close()

if __name__=='__main__':
    main()
