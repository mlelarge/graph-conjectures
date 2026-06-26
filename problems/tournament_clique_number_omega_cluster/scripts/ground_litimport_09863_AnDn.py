"""Oracle grounding of the A_n / D_n families from arXiv:2602.09863
(Crew, Fan, Koerts, Moore, Spirkl -- 'Characterizing Large Clique Number in
Tournaments', Feb 2026), the FORWARD CITATION of 2310.04265.

Definitions transcribed verbatim from src09863/main.tex:

 D_1 = single vertex; D_n = Delta(D_{n-1}, D_{n-1}, D_1).   |V(D_n)| = 2^n - 1.
   Delta(T1,T2,T3): block1=>block2, block2=>block3, block3=>block1.

 A_1 = single vertex.  A_n on V(T_1)..V(T_{n-1}) (each ~ A_{n-1}) plus
   v_1..v_n, with:
     - A_n[V(T_i)] = T_i;
     - v_j -> v_i  for i<j;
     - V(T_i) => V(T_j)  for i<j;
     - v_i => V(T_j)  for i<=j (j in 1..n-1);
     - V(T_j) => v_i  for i>j  (j in 1..n-1).
   |V(A_n)| <= 2 n!.

We compute EXACT omega_vec on the smallest feasible members and check the
prediction that omega_vec GROWS (Conj 5.10 direction: families certified
'large clique number' really do have unbounded omega_vec, with explicit small
members reachable by the oracle).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import core
from constructions import delta

# ---- D_n: Delta(D_{n-1}, D_{n-1}, D_1) ----
def D(n):
    if n == 1:
        return (1, [])
    d = D(n-1)
    return delta(d, d, (1, []))

# ---- A_n per Definition def:An ----
def A(n):
    if n == 1:
        return (1, [])
    Tprev = A(n-1)              # each T_i is a copy of A_{n-1}
    m = Tprev[0]
    # vertices: v_1..v_n  then  T_1 .. T_{n-1}
    # layout: v_i has index i-1 (i in 1..n); block T_i starts after the n v's
    vidx = {i: i-1 for i in range(1, n+1)}
    Tstart = {}
    off = n
    for i in range(1, n):       # T_1 .. T_{n-1}
        Tstart[i] = off
        off += m
    N = off
    beats = [[False]*N for _ in range(N)]
    # internal arcs of each T_i (copy of A_{n-1})
    for i in range(1, n):
        base = Tstart[i]
        for (u, v) in Tprev[1]:
            beats[base+u][base+v] = True
    # v_j -> v_i for i<j
    for i in range(1, n+1):
        for j in range(1, n+1):
            if i < j:
                beats[vidx[j]][vidx[i]] = True
    # V(T_i) => V(T_j) for i<j
    for i in range(1, n):
        for j in range(1, n):
            if i < j:
                for a in range(m):
                    for b in range(m):
                        beats[Tstart[i]+a][Tstart[j]+b] = True
    # v_i => V(T_j) for i<=j  (j in 1..n-1)
    for i in range(1, n+1):
        for j in range(1, n):
            if i <= j:
                for b in range(m):
                    beats[vidx[i]][Tstart[j]+b] = True
    # V(T_j) => v_i for i>j  (j in 1..n-1)
    for j in range(1, n):
        for i in range(1, n+1):
            if i > j:
                for b in range(m):
                    beats[Tstart[j]+b][vidx[i]] = True
    arcs = [(u, v) for u in range(N) for v in range(N) if beats[u][v]]
    return (N, arcs)


def report(label, T, do_critical=False):
    n, arcs = T
    ok = core.is_tournament(n, arcs)
    line = {"obj": label, "n": n, "is_tournament": ok}
    if not ok:
        print(line); return
    w = core.omega_vec(n, arcs)
    line["omega_vec"] = w
    if do_critical:
        line["is_%d_critical" % w] = core.is_k_omega_vec_critical(n, arcs, w)
    print(line)
    sys.stdout.flush()


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("D", "all"):
        for n in range(1, 6):          # D_5 = 31 vertices
            report("D_%d" % n, D(n))
    if which in ("A", "all"):
        for n in range(1, 4):          # A_3
            report("A_%d" % n, A(n))
