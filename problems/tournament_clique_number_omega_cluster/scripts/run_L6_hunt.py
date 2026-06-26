"""Depth-6 upper-bound hunt: smallest SAT cap triple via lazy CEGAR (big budget)."""
import sys, time, json
sys.path.insert(0, "scripts")
from decide_layer_lazy import decide_caps_lazy

BUDGET = 1200.0
CANDS = [(2,4,4),(3,3,4),(2,3,6),(2,4,5),(3,3,5),(3,4,4)]  # ascending product
log=open("data/L6_hunt.log","w")
def emit(s): print(s,flush=True); log.write(s+"\n"); log.flush()
emit(f"# L_6 hunt: budget {BUDGET}s/call")
best=None
for caps in sorted(CANDS, key=lambda c:(c[0]*c[1]*c[2],c)):
    p=caps[0]*caps[1]*caps[2]
    if best is not None and p>=best: break
    t=time.time(); r=decide_caps_lazy(6,caps,time_budget=BUDGET)
    s='SAT' if r.get('sat') else ('UNSAT' if r.get('sat') is False else 'TIMEOUT')
    emit(f"caps={caps} product={p} {s} rounds={r.get('rounds')} {time.time()-t:.0f}s heights={r.get('verified_heights')}")
    if r.get('sat'):
        best=p
        json.dump({"depth":6,"L6_upper":p,"caps":list(caps),"witness_order":r.get("witness_order")},
                  open("data/L6_result.json","w"))
        emit(f"*** L_6 <= {p} (SAT at {caps}) ***"); break
emit(f"# L_6 upper bound: {best}")
