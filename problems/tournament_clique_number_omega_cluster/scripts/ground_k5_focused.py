import sys, time
sys.path.insert(0, 'scripts')
import core
from search_4critical_circulant import build_cnf_no_kclique, omega_vec_ge_K_via_sat

def lex(nT, aT, nH, aH):
    bT = core.beats_matrix(nT, aT); bH = core.beats_matrix(nH, aH)
    return nT*nH, [(a*nH+b, ap*nH+bp)
                   for a in range(nT) for b in range(nH)
                   for ap in range(nT) for bp in range(nH)
                   if (a, b) != (ap, bp) and (bT[a][ap] or (a == ap and bH[b][bp]))]

C3 = [(0, 1), (1, 2), (2, 0)]

# --- PROXIES via validated SAT oracle (cheap, ge_K instead of exact bb) ---
qr7 = sorted({(x*x) % 7 for x in range(1, 7)})
a7 = [(i, (i+d) % 7) for i in range(7) for d in qr7]
n21, a21 = lex(7, a7, 3, C3)  # order 21, law predicts ov=4
print("QR7[C3] order", n21,
      "ge_4", omega_vec_ge_K_via_sat(n21, a21, 4)[0],
      "ge_5", omega_vec_ge_K_via_sat(n21, a21, 5)[0], flush=True)
n9, a9 = lex(3, C3, 3, C3)  # order 9, law predicts ov=3
print("C3[C3] order", n9,
      "ge_3", omega_vec_ge_K_via_sat(n9, a9, 3)[0],
      "ge_4", omega_vec_ge_K_via_sat(n9, a9, 4)[0],
      "exact", core.omega_vec(n9, a9), flush=True)

# --- DECISIVE: build QR_19[C3] order 57, time CNF build then solve separately ---
qr19 = sorted({(x*x) % 19 for x in range(1, 19)})
arcs19 = [(i, (i+d) % 19) for i in range(19) for d in qr19]
n, arcs = lex(19, arcs19, 3, C3)
print("T5 = QR19[C3] order", n, "tournament", core.is_tournament(n, arcs), flush=True)

t0 = time.time()
cnf, nclq = build_cnf_no_kclique(n, arcs, 5)
print("ge_5 CNF built: nvars=%d nclauses=%d forbid=%d build=%.1fs"
      % (cnf.nv, len(cnf.clauses), nclq, time.time()-t0), flush=True)

from pysat.solvers import Cadical153
t0 = time.time()
with Cadical153(bootstrap_with=cnf.clauses) as m:
    sat = m.solve()
print("ge_5 solve: sat=%s (omega_vec>=5 is %s) %.1fs"
      % (sat, (not sat), time.time()-t0), flush=True)
print("DONE_FOCUSED", flush=True)
