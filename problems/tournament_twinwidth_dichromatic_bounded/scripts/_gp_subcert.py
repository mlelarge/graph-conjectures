import sys, time, itertools, random
sys.path.insert(0, '.')
import core, constructions as C

sub = C.substitute_into_C3
TT1 = C.single_vertex()
TT2 = C.transitive_tournament(2)
S3 = C.S(3)
CANDS = {
    'D(S3,S3,TT1)': sub(S3, S3, TT1),
    'D(S3,TT1,S3)': sub(S3, TT1, S3),
    'D(TT1,S3,S3)': sub(TT1, S3, S3),
    'D(S3,S3,TT2)': sub(S3, S3, TT2),
    'D(TT2,S3,S3)': sub(TT2, S3, S3),
}

def induced(n, arcs, verts):
    idx = {v: i for i, v in enumerate(verts)}
    vs = set(verts)
    na = [(idx[u], idx[v]) for (u, v) in arcs if u in vs and v in vs]
    return len(verts), na

nm = sys.argv[1]
n, a = CANDS[nm]
t0 = time.time()
# omegaVec is monotone under induced sub-tournaments: if some subset has omegaVec=3
# then the parent has omegaVec >= 3.  Search subsets of size up to 11 (omega_vec
# exact is fine there). Prioritise subsets that include the apex/structure.
random.seed(0)
found = None
# First: a few structured subsets (one vertex from singleton slot + two S3 blocks)
sizes_to_try = [9, 10, 11]
checked = 0
for sz in sizes_to_try:
    # random subsets + the "first sz" deterministic
    cand_subsets = [tuple(range(sz))]
    for _ in range(400):
        cand_subsets.append(tuple(sorted(random.sample(range(n), sz))))
    seen = set()
    for verts in cand_subsets:
        if verts in seen:
            continue
        seen.add(verts)
        m, na = induced(n, a, list(verts))
        ov = core.omega_vec(m, na)
        checked += 1
        if ov >= 3:
            found = (verts, ov)
            break
    if found:
        break
    print('SUBCERT %s no size-%d subset with omega>=3 in sample (checked=%d, %.1fs)'
          % (nm, sz, checked, time.time() - t0), flush=True)

if found:
    verts, ov = found
    print('SUBCERT %s omegaVec>=3 PROVED via induced subset size %d (omega=%d) verts=%s (checked=%d, %.1fs)'
          % (nm, len(verts), ov, list(verts), checked, time.time() - t0), flush=True)
else:
    print('SUBCERT %s NO small induced witness found in sample (inconclusive for omega>=3)'
          % nm, flush=True)
