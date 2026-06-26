"""Calibrate depth-6 positional SAT: do any triples resolve under a budget?"""
import sys, time, json
sys.path.insert(0, "scripts")
from decide_layer_positional import decide_caps_positional
BUDGET = 8_000_000  # conflicts (~few min)
CANDS = [(3,3,4),(2,4,5),(3,3,5),(3,4,4),(4,4,4)]  # products 36,40,45,48,64
log=open("data/L6_calib.log","w")
def emit(s): print(s,flush=True); log.write(s+"\n"); log.flush()
emit(f"# depth-6 calib, conf_budget={BUDGET}")
for caps in CANDS:
    t=time.time(); r=decide_caps_positional(6,caps,conf_budget=BUDGET)
    s='SAT' if r['sat'] else ('UNSAT' if r['sat'] is False else 'UNKNOWN(budget)')
    emit(f"caps={caps} product={caps[0]*caps[1]*caps[2]} {s} {time.time()-t:.0f}s heights={r.get('verified_heights')}")
emit("# calib done")
