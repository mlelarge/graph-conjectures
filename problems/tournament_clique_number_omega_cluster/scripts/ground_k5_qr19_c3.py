import sys, time
sys.path.insert(0, 'scripts')
import core
from search_4critical_circulant import omega_vec_ge_K_via_sat, validate_sat_oracle

ok, _ = validate_sat_oracle()
assert ok, "SAT oracle validation failed"
print("VALIDATE", ok, flush=True)

def lex(nT, aT, nH, aH):
    bT = core.beats_matrix(nT, aT); bH = core.beats_matrix(nH, aH)
    arcs = [(a*nH+b, ap*nH+bp)
            for a in range(nT) for b in range(nH)
            for ap in range(nT) for bp in range(nH)
            if (a, b) != (ap, bp) and (bT[a][ap] or (a == ap and bH[b][bp]))]
    return nT*nH, arcs

qr19 = sorted({(x*x) % 19 for x in range(1, 19)})
arcs19 = [(i, (i+d) % 19) for i in range(19) for d in qr19]
print("qr19", qr19, "is_tourn", core.is_tournament(19, arcs19), flush=True)

nH = 3
arcsH = [(0, 1), (1, 2), (2, 0)]
n, arcs = lex(19, arcs19, nH, arcsH)
print("order", n, "tournament", core.is_tournament(n, arcs), flush=True)

# WHOLE: lower leg ge_5 (decisive), then ge_6
t0 = time.time(); g5 = omega_vec_ge_K_via_sat(n, arcs, 5)
print("whole ge_5", g5[0], "(%.3fs)" % (time.time()-t0), flush=True)

# Upper bound via explicit interleaved order: block order = QR_19 rotation order,
# within-block = C3 order. Vertex (a,b) -> a*3+b. Pick block order = identity 0..18,
# within block C3 order 0,1,2. Try a few block rotations, take min omega.
def interleaved_order(block_order, within):
    return [a*nH + b for a in block_order for b in within]

best_ub = None; best_desc = None
for r in range(19):
    bo = [(i+r) % 19 for i in range(19)]
    o = interleaved_order(bo, [0, 1, 2])
    w = core.omega_of_order(n, arcs, o)
    if best_ub is None or w < best_ub:
        best_ub = w; best_desc = ("rot", r)
print("upper_bound omega_vec(T5) <=", best_ub, "via", best_desc, flush=True)

# ge_6: only run SAT if upper bound leaves it ambiguous (i.e. best_ub >= 6)
if best_ub <= 5:
    print("whole ge_6 SKIPPED (upper bound <=5 already gives omega_vec<6); ge_6=False",
          flush=True)
    g6_says = False
else:
    t0 = time.time(); g6 = omega_vec_ge_K_via_sat(n, arcs, 6)
    print("whole ge_6", g6[0], "(%.3fs)" % (time.time()-t0), flush=True)
    g6_says = g6[0]

# DELETION of vertex 0 (relabel)
keep = [v for v in range(n) if v != 0]
idx = {v: i for i, v in enumerate(keep)}
darcs = [(idx[u], idx[w]) for (u, w) in arcs if u != 0 and w != 0]
t0 = time.time(); d4 = omega_vec_ge_K_via_sat(n-1, darcs, 4)
print("del ge_4", d4[0], "(%.3fs)" % (time.time()-t0), flush=True)
t0 = time.time(); d5 = omega_vec_ge_K_via_sat(n-1, darcs, 5)
print("del ge_5", d5[0], "(%.3fs)" % (time.time()-t0), flush=True)

print("=== SUMMARY ===", flush=True)
print("whole ge_5 =", g5[0], "(True => omega_vec>=5)", flush=True)
print("whole ub   =", best_ub, "(<=5 => omega_vec<6)", flush=True)
print("del ge_4   =", d4[0], "(True => omega_vec(T-0)>=4)", flush=True)
print("del ge_5   =", d5[0], "(False => omega_vec(T-0)<=4)", flush=True)
ov_whole_5 = g5[0] and best_ub == 5
ov_del_4 = d4[0] and not d5[0]
print("omega_vec(T5)==5 :", ov_whole_5, flush=True)
print("omega_vec(T5-0)==4 :", ov_del_4, flush=True)
print("=> 5-critical (by vertex-transitivity):", ov_whole_5 and ov_del_4, flush=True)
