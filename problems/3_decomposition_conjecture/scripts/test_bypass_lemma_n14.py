"""Test the Cycle-bypass lemma claim against all essentially-3-conn n=14 records.

Claim: every essentially-3-conn n=14 oriented side realises both
  (T_CC, T_T) split  AND  (T_T, T_CC) split.
"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import networkx as nx
from decomposition import compute_trace_set_2pole

BYPASS_TRACES = {
    (("T_CC", "T_T"), frozenset([frozenset([0]), frozenset([1])])),
    (("T_T", "T_CC"), frozenset([frozenset([0]), frozenset([1])])),
}

records = []
with open(str(Path(__file__).resolve().parent.parent / 'data') + '/n14_full.jsonl') as f:
    for line in f:
        r = json.loads(line)
        if r['structural_class'] == 'essentially_3conn':
            records.append(r)
print(f"Total essentially-3-conn n=14: {len(records)}", flush=True)

exceptions = [r for r in records if r['absorbing_class_id'] != 'C0']
print(f"  Non-C0-absorbed exceptions: {len(exceptions)}", flush=True)

failures = []
for i, r in enumerate(exceptions, 1):
    G = nx.from_graph6_bytes(r['graph6'].encode())
    traces = compute_trace_set_2pole(G, r['ports'])
    norm = {(t[0], frozenset(frozenset(b) for b in t[1])) for t in traces}
    ok = BYPASS_TRACES <= norm
    if not ok:
        failures.append(r)
    print(f"  [{i}/{len(exceptions)}] {r['graph6']} ports={r['ports']} bypass={'BOTH' if ok else 'MISSING'}", flush=True)

print(flush=True)
print(f"Exceptions checked: {len(exceptions)}", flush=True)
print(f"Missing bypass: {len(failures)}", flush=True)
if not failures:
    print("All 14 exceptions realise BOTH bypass traces.", flush=True)
