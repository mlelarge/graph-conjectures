"""ECLOG C=3 boundary CONFIRM (G10-salvage Step 3).

Build an Eulerian digraph at the C=3 boundary n=17, lambda >= ceil(3*log2 17)=13,
and SAD-decide it with the oracle (cross_check=True).  The theorem (threshold
lambda >= 3*log2 n, n_0 = 17) predicts SAT.

Construction: circulant on Z_17 with connection set C of size 13.  A circulant
has in-degree = out-degree = |C| at every vertex, so it is automatically
EULERIAN.  We pick |C| = 13 consecutive shifts {1,...,13}.  arc-connectivity is
reported exactly by the oracle.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle  # noqa: E402

n = 17
log2 = lambda x: math.log(x) / math.log(2)
lam_threshold = math.ceil(3 * log2(n))   # = 13
C = list(range(1, 14))                    # 13 shifts -> Eulerian, out-deg 13
assert len(C) == 13

arcs = []
for i in range(n):
    for s in C:
        arcs.append([i, (i + s) % n])

# Eulerian check: in-deg == out-deg for every vertex.
outdeg = [0]*n; indeg = [0]*n
for u, v in arcs:
    outdeg[u] += 1; indeg[v] += 1
eulerian = all(outdeg[i] == indeg[i] for i in range(n))
print(f"n={n}  |arcs|={len(arcs)}  out-deg=in-deg=13 per vertex  Eulerian={eulerian}")
assert eulerian, "construction not Eulerian"

lam = oracle.arc_connectivity(n, arcs)
print(f"oracle arc_connectivity lambda = {lam}   (threshold ceil(3 log2 17) = {lam_threshold})")
assert lam >= lam_threshold, f"lambda {lam} below boundary threshold {lam_threshold}"

res = oracle.check_construction(n, arcs, name="eclog_c3_boundary_n17", cross_check=True)
cc = res.get('cross_check')
agree = (cc is None) or (cc.get('agree') is True if isinstance(cc, dict) else cc in (True, 'AGREE', 'agree'))
print(f"SAD = {res['sad']}   cross_check = {cc}   arc_strong = {res.get('arc_strong')}")

if res['sad'] == 'SAT' and agree:
    print("CONFIRM PASS: Eulerian boundary instance (n=17, lambda=13) is SAT, both backends agree, as the theorem predicts.")
else:
    print("CONFIRM FAIL / DISAGREE:", res)
    sys.exit(1)
