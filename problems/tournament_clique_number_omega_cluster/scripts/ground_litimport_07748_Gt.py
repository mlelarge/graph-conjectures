"""Oracle grounding of the Nassar-Yuster checkerboard family G_t imported by
arXiv:2606.07748 (Aboulker, Crew, Duron, Fan, Jacob, Kimbrough, Koerts, Moore,
Spirkl, Thomasse -- 'Decomposing tournaments into comparability graphs', Jun 2026),
the forward citation of 2310.04265.  Paper Thm 'thm:gt': diomega(G_t) >= (t/2)^{1/3}.

Definition (verbatim, src07748 line 522): V(G_t) = [t] x [t], with
  (i,j) -> (k,l)  iff   (i<=k and j<l)  or  (i<k and j>l)  or  (i>k and j=l).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import core

def Gt(t):
    V = [(i, j) for i in range(1, t+1) for j in range(1, t+1)]
    idx = {v: n for n, v in enumerate(V)}
    arcs = []
    for (i, j) in V:
        for (k, l) in V:
            if (i, j) == (k, l):
                continue
            if (i <= k and j < l) or (i < k and j > l) or (i > k and j == l):
                arcs.append((idx[(i, j)], idx[(k, l)]))
    return (len(V), arcs)

if __name__ == "__main__":
    t = int(sys.argv[1])
    n, arcs = Gt(t)
    ok = core.is_tournament(n, arcs)
    out = {"obj": "G_%d" % t, "n": n, "is_tournament": ok}
    if ok:
        out["omega_vec"] = core.omega_vec(n, arcs)
    print(out)
