import sys, os, math, random, time, signal
import networkx as nx
from g_saturated_alpha import build_saturated, triangle_free, exact_alpha

def run(ns, seeds, timeout):
    print(f"{'n':>4} {'d':>6} {'d/sqrt(nlogn)':>13} {'alpha':>7} {'a/sqrt(nlogn)':>13} {'a/(sqrtn*logn)':>15} {'tf':>5}")
    rows=[]
    for n in ns:
        logn = math.log(n)
        ds=[]; alphas=[]; tf_all=True; ok=True
        for s in seeds:
            G = build_saturated(n,s)
            d = 2.0*G.number_of_edges()/n
            tf_all = tf_all and triangle_free(G)
            a = exact_alpha(G, timeout=timeout)
            if a is None:
                ok=False; break
            ds.append(d); alphas.append(a)
        if not ok:
            print(f"{n:>4}  TIMEOUT"); continue
        d=sum(ds)/len(ds); a=sum(alphas)/len(alphas)
        snl=math.sqrt(n*logn); snln=math.sqrt(n)*logn
        r1=a/snl; r2=a/snln
        rows.append((n,r1,r2))
        print(f"{n:>4} {d:6.2f} {d/snl:13.3f} {a:7.2f} {r1:13.3f} {r2:15.3f} {str(tf_all):>5}")
    # trend summary
    if len(rows)>=2:
        import statistics
        r1s=[x[1] for x in rows]; r2s=[x[2] for x in rows]
        print(f"\nalpha/sqrt(nlogn): first={r1s[0]:.3f} last={r1s[-1]:.3f} ratio={r1s[-1]/r1s[0]:.3f} CV={statistics.pstdev(r1s)/statistics.mean(r1s):.4f}")
        print(f"alpha/(sqrtn*logn): first={r2s[0]:.3f} last={r2s[-1]:.3f} ratio={r2s[-1]/r2s[0]:.3f} CV={statistics.pstdev(r2s)/statistics.mean(r2s):.4f}")

if __name__=="__main__":
    # 5 seeds, larger n, generous timeout per alpha
    run([40,60,80,100,120,140], seeds=[0,1,2,3,4], timeout=110)
