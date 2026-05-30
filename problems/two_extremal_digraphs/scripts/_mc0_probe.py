import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seam_invariant as S, h2_oracle as O
d = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'L_7.json')))
for idx in (7, 14, 36):
    m = d[idx]; n = m['n']; arcs = frozenset(tuple(a) for a in m['arcs'])
    digons, singles = S.split_digons_singles(n, arcs)
    sout = {u: v for u, v in singles}
    seen = set(); cycles = []
    for u, _ in singles:
        if u in seen:
            continue
        c = [u]; seen.add(u); cur = sout[u]
        while cur != u:
            c.append(cur); seen.add(cur); cur = sout[cur]
        cycles.append(c)
    print(f'7.{idx}: single-arc directed cycles = {cycles}')
