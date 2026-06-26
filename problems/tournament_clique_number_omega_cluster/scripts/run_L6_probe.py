"""Depth-6 (B_6, 729 vertices) layer-volume probe via lazy-transitivity SAT.

Scans cyclic-representative cap triples by product (using the colour-shift
automorphism sigma: feasibility is invariant under cyclic rotation of caps).
Goal: tighten L_6 in [vec_chi(B_6)=18, 48] (48 = L_5*L_1 submultiplicative).
Reports first SAT product (upper bound) and the UNSAT triples below it.
"""
import sys, time, itertools, json
sys.path.insert(0, "scripts")
from decide_layer_lazy import decide_caps_lazy

DEPTH = 6
MAXP = int(sys.argv[1]) if len(sys.argv) > 1 else 48
BUDGET = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0

def cyclic_rep(c):
    return min((c, (c[1], c[2], c[0]), (c[2], c[0], c[1])))

reps = {}
for caps in itertools.product(range(1, MAXP + 1), repeat=3):
    p = caps[0] * caps[1] * caps[2]
    if p > MAXP:
        continue
    r = cyclic_rep(caps)
    reps.setdefault(r, p)
cands = sorted(reps, key=lambda c: (reps[c], c))

log = open("data/L6_probe.log", "w")
def emit(s):
    print(s, flush=True); log.write(s + "\n"); log.flush()

emit(f"# L_6 probe: {len(cands)} cyclic-rep cap triples, product<={MAXP}, budget {BUDGET}s/call")
t0 = time.time()
first_sat = None
for caps in cands:
    p = caps[0] * caps[1] * caps[2]
    if first_sat is not None and p > first_sat:
        break
    t = time.time()
    r = decide_caps_lazy(DEPTH, caps, time_budget=BUDGET)
    status = "SAT" if r.get("sat") else ("UNSAT" if r.get("sat") is False else "TIMEOUT")
    emit(f"caps={caps} product={p} {status} rounds={r.get('rounds')} "
         f"lazyCl={r.get('lazy_clauses')} {time.time()-t:.0f}s")
    if r.get("sat"):
        first_sat = p
        json.dump({"depth": DEPTH, "L6_upper": p, "caps": list(caps),
                   "witness_order": r.get("witness_order")},
                  open("data/L6_result.json", "w"))
emit(f"\n# L_6 upper bound = {first_sat}   (total {time.time()-t0:.0f}s)")
