"""Independent certification of the F3 PROOF's internal lemmas (the metric-cut
proof in docs/H5_LEMMA_A_REDUCTION.md).

F3: in a 2-connected graph B with root u, every non-representative s of a
Sigma-fiber has a PROPER apex A_s != S.  The proof proceeds:
  (P1) a non-representative has depth d(u,s) >= 2;
  (P2) if A_s = S and d(u,s) >= 2 then there is NO edge between Sigma_s and F_s
       (F_s = {x : [x u s]});  hence (S = Sigma_s ⊔ F_s) F_s nonempty would make u
       a cut vertex -> by 2-connectivity F_s = empty, so Sigma_s = S;
  (P3) a vertex with Sigma_s = S is alone in its Sigma-fiber (maximal in <=_u, else
       it is a cut vertex separating the 'up' set from u).
This gate checks (P1),(P2),(P3) and the end-to-end F3 over all 2-connected marked
graphs of the given orders.  0 failures => the proof's structural claims hold.
"""
from __future__ import annotations
import sys, subprocess, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core


def run(order):
    proc = subprocess.run(["geng", "-C", "-q", str(order)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    out = dict(order=order, marked=0,
               P1_nonrep_depth_lt2=0, P2_sigmaF_edge=0, P2_Fs_nonempty=0,
               P3_sigmaS_multi=0, F3_fail=0)
    for line in proc.stdout.splitlines():
        g6 = line.strip()
        if not g6:
            continue
        n, edges = core.graph6_to_edges(g6)
        d = core.all_pairs_distances(n, edges)
        adj = [set() for _ in range(n)]
        for a, b in edges:
            adj[a].add(b); adj[b].add(a)
        for u in range(n):
            out["marked"] += 1
            S = [x for x in range(n) if x != u]
            fS = frozenset(S)
            le = lambda x, y: d[u][x] + d[x][y] == d[u][y]
            Sig = {}; F = {}; A = {}
            for s in S:
                sig = set(); Fs = set()
                for x in S:
                    if le(x, s) or le(s, x):
                        sig.add(x)
                    elif d[u][x] + d[u][s] == d[s][x]:  # [x u s]
                        Fs.add(x)
                Sig[s] = frozenset(sig); F[s] = frozenset(Fs)
                A[s] = Sig[s] | F[s]
            fib = {}
            for s in S:
                fib.setdefault(Sig[s], []).append(s)
            reps = {min(m, key=lambda s: (d[u][s], s)) for m in fib.values()}
            for s in S:
                nonrep = s not in reps
                if nonrep and d[u][s] < 2:
                    out["P1_nonrep_depth_lt2"] += 1
                if A[s] == fS and d[u][s] >= 2:
                    if any(b in adj[a] for a in Sig[s] for b in F[s]):
                        out["P2_sigmaF_edge"] += 1
                    if F[s]:
                        out["P2_Fs_nonempty"] += 1
                if nonrep and A[s] == fS:
                    out["F3_fail"] += 1
            if sum(1 for s in S if Sig[s] == fS) > 1:
                out["P3_sigmaS_multi"] += 1
    return out


if __name__ == "__main__":
    for n in (int(x) for x in (sys.argv[1:] or [5, 6, 7, 8])):
        print(json.dumps(run(n)))
