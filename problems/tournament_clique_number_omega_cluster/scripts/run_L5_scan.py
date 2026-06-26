"""Background runner: exact L_5 via level-labeling SAT, scanning by product."""
import sys, time, itertools, json
sys.path.insert(0, "scripts")
from decide_layer_labeling import decide_caps_labeling

MAX_CAP = 26
candidates = sorted(
    itertools.product(range(1, MAX_CAP + 1), repeat=3),
    key=lambda c: (c[0] * c[1] * c[2], c),
)
candidates = [c for c in candidates if c[0] * c[1] * c[2] <= 27]

log = open("data/L5_scan.log", "w")
def emit(s):
    print(s, flush=True); log.write(s + "\n"); log.flush()

emit(f"# L_5 scan: {len(candidates)} cap triples (product<=27), max_cap={MAX_CAP}")
t0 = time.time()
L5 = None
for caps in candidates:
    t = time.time()
    r = decide_caps_labeling(5, caps)
    emit(f"caps={caps} product={r['product']} clauses={r['num_clauses']} "
         f"{'SAT' if r['sat'] else 'UNSAT'} {time.time()-t:.1f}s")
    if r["sat"]:
        L5 = r["product"]
        emit(f"\n*** L_5 = {L5}  (first SAT at caps={caps}, witness len "
             f"{len(r['witness_order'])}) ***")
        json.dump({"L5": L5, "caps": list(caps),
                   "witness_order": r["witness_order"]},
                  open("data/L5_result.json", "w"))
        break
emit(f"# total {time.time()-t0:.1f}s")
if L5 is None:
    emit("# no SAT triple with product<=27 (unexpected)")
