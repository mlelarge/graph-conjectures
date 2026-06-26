import sys, time, signal
sys.path.insert(0, 'scripts')
import core
import networkx as nx
from search_4critical_circulant import omega_vec_ge_K_via_sat, validate_sat_oracle

def _alarm(sig, frm):
    print("SELF-ALARM TIMEOUT", flush=True); sys.exit(2)
signal.signal(signal.SIGALRM, _alarm)
signal.alarm(700)

ok, _ = validate_sat_oracle()
print("SAT_ORACLE_VALIDATED", ok, flush=True)
assert ok

QR = sorted({(x*x) % 19 for x in range(1, 19)})
arcs19 = [(i, (i+d) % 19) for i in range(19) for d in QR]
nT, nH = 19, 3
arcsH = [(0, 1), (1, 2), (2, 0)]
bT = core.beats_matrix(nT, arcs19); bH = core.beats_matrix(nH, arcsH)
def vid(t, h): return t*nH + h
N = nT*nH
arcs = []
for t in range(nT):
    for h in range(nH):
        for tp in range(nT):
            for hp in range(nH):
                if (t, h) == (tp, hp): continue
                if bT[t][tp] or (t == tp and bH[h][hp]):
                    arcs.append((vid(t, h), vid(tp, hp)))

# deletion of source (0,0)
src = vid(0, 0)
keep = [v for v in range(N) if v != src]
idx = {v: i for i, v in enumerate(keep)}
darcs = [(idx[u], idx[w]) for (u, w) in arcs if u != src and w != src]
print("deletion order", len(keep), "is_tournament", core.is_tournament(len(keep), darcs), flush=True)

# SAT spot-check: omega_vec(deletion) >= 5 ?  (KILL branch (b): >=5 => not 4-critical)
t0 = time.time()
d5 = omega_vec_ge_K_via_sat(len(keep), darcs, 5)
print("deletion ge_5 (SAT) =", d5[0], "(%.1fs)" % (time.time()-t0),
      "[True => omega_vec(deletion)>=5 => NOT 4-critical => QR_19[C3] not 5-critical]",
      flush=True)
