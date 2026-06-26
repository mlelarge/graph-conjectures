import math, statistics
import networkx as nx
from g_saturated_alpha import build_sparse, triangle_free, exact_alpha

def run(ns, seeds, timeout):
    print(f"{'n':>4} {'d':>6} {'alpha':>7} {'a/sqrt(nlogn)':>13} {'a/(sqrtn*logn)':>15}")
    rows=[]
    for n in ns:
        logn=math.log(n); alphas=[]; ds=[]; ok=True
        for s in seeds:
            G=build_sparse(n,s); ds.append(2.0*G.number_of_edges()/n)
            assert triangle_free(G)
            a=exact_alpha(G,timeout=timeout)
            if a is None: ok=False; break
            alphas.append(a)
        if not ok:
            print(f"{n:>4} TIMEOUT"); continue
        d=sum(ds)/len(ds); a=sum(alphas)/len(alphas)
        snl=math.sqrt(n*logn); snln=math.sqrt(n)*logn
        rows.append((a/snl,a/snln))
        print(f"{n:>4} {d:6.2f} {a:7.2f} {a/snl:13.3f} {a/snln:15.3f}")
    if len(rows)>=2:
        r1=[x[0] for x in rows]; r2=[x[1] for x in rows]
        print(f"\nsparse alpha/sqrt(nlogn): CV={statistics.pstdev(r1)/statistics.mean(r1):.4f} ratio={r1[-1]/r1[0]:.3f}")
        print(f"sparse alpha/(sqrtn*logn): CV={statistics.pstdev(r2)/statistics.mean(r2):.4f} ratio={r2[-1]/r2[0]:.3f}")

if __name__=="__main__":
    run([30,40,50,60,70,80], seeds=[0,1,2,3,4], timeout=100)
