"""Depth-6 attempt via the positional (binary-key) encoding + conflict budget.
Tries small-product triples for an UPPER bound on L_6; logs SAT/UNSAT/UNKNOWN."""
import sys, time, json
sys.path.insert(0, "scripts")
from decide_layer_positional import decide_caps_positional

BUDGET = 60_000_000  # conflict budget per call (solve_limited)
CANDS = [(2,4,4),(3,3,4),(2,3,6),(2,4,5)]
log=open("data/L6_positional.log","w")
def emit(s): print(s,flush=True); log.write(s+"\n"); log.flush()
emit(f"# L_6 positional attempt: conf_budget={BUDGET}/call")
best=None
for caps in sorted(CANDS, key=lambda c:(c[0]*c[1]*c[2],c)):
    p=caps[0]*caps[1]*caps[2]
    if best is not None and p>=best: break
    t=time.time(); r=decide_caps_positional(6,caps,conf_budget=BUDGET)
    s='SAT' if r['sat'] else ('UNSAT' if r['sat'] is False else 'UNKNOWN(budget)')
    emit(f"caps={caps} product={p} {s} vars={r['num_vars']} clauses={r['num_clauses']} {time.time()-t:.0f}s heights={r.get('verified_heights')}")
    if r['sat']:
        best=p
        json.dump({"depth":6,"L6_upper":p,"caps":list(caps),"witness_order":r.get("witness_order")},
                  open("data/L6_result.json","w"))
        emit(f"*** L_6 <= {p} (SAT at {caps}) ***"); break
emit(f"# done; L_6 upper bound: {best}")
