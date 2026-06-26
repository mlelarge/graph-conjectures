"""Part (2) of the asymptotic-argument proposal: targeted search for a
WHOLE-TOURNAMENT 3-omega_vec-critical tournament at orders 10 and 11.

Strategy (cost-aware, given omega_vec at n=11 in the omega_vec=3 regime can cost
~60s/call): cheap filter first.
  1. Generate candidates at n=10,11:
     - Delta-block partitions over critical/omega>=2 seeds (C3, n7 witness, S~_2,
       transitive blocks) summing to 10 or 11.
     - S~_3 (order 9) + 1 or 2 added vertices with random/structured back-arcs.
     - local-flip hill-climbing seeded by S~_3 augmentations.
  2. FILTER 1 (one omega_vec call): keep only omega_vec == 3.
  3. FILTER 2: is_k_omega_vec_critical(.,3).
  4. FILTER 3 (whole-tournament): min_subtournament_order_for_k(.,3) == n.
Record every omega_vec==3 hit at order 10/11 and its min_cert_order.
"""
import sys, json, time, itertools, random
sys.path.insert(0, 'scripts')
from core import (omega_vec, is_k_omega_vec_critical,
                  min_subtournament_order_for_k, subtournament, is_tournament)
from constructions import (directed_C3, transitive_tournament, delta, S_tilde,
                           random_tournament)

C3 = directed_C3()
n7 = None
d = json.load(open('data/min3critical_n7.json'))
n7 = (d['order'], [tuple(a) for a in d['arcs']])
S2 = S_tilde(2)  # order 3 = C3 essentially

hits = []  # all omega_vec==3 candidates at order 10/11

def consider(T, tag):
    n, arcs = T
    if n not in (10, 11):
        return
    if not is_tournament(n, arcs):
        return
    t0 = time.time()
    w = omega_vec(n, arcs, method='bb')
    dt = time.time() - t0
    if w != 3:
        return
    print(f'[omega3] {tag} n={n} omega_vec=3 (omega_vec {dt:.1f}s)', flush=True)
    crit = is_k_omega_vec_critical(n, arcs, 3)
    rec = {'tag': tag, 'n': n, 'omega_vec': 3, 'crit3': crit, 'arcs': [list(a) for a in arcs]}
    if crit:
        sz, ks = min_subtournament_order_for_k(n, arcs, 3)
        rec['min_cert_order'] = sz
        rec['whole_tournament'] = (sz == n)
        print(f'   -> 3crit=True  min_cert_order={sz}  WHOLE_TOURNAMENT={sz==n}', flush=True)
    else:
        print(f'   -> 3crit=False', flush=True)
    hits.append(rec)

# ---- candidate generator A: Delta-block partitions summing to 10/11 ----
seeds = {
    'TT1': transitive_tournament(1),
    'TT2': transitive_tournament(2),
    'TT3': transitive_tournament(3),
    'TT4': transitive_tournament(4),
    'TT5': transitive_tournament(5),
    'C3': C3,
    'n7': n7,
}
print('=== Generator A: Delta partitions ===', flush=True)
for k1, k2, k3 in itertools.product(seeds, repeat=3):
    T1, T2, T3 = seeds[k1], seeds[k2], seeds[k3]
    n = T1[0] + T2[0] + T3[0]
    if n in (10, 11):
        consider(delta(T1, T2, T3), f'Delta({k1},{k2},{k3})')

# ---- candidate generator B: S~_3 (order 9) + 1 or 2 vertices ----
# Add vertices with various back/forward arc patterns. Filter by omega_vec==3.
print('=== Generator B: S~_3 + vertices ===', flush=True)
S3 = S_tilde(3)  # order 9
base_n, base_arcs = S3
rng = random.Random(12345)

def augment(base, k_new, patterns):
    """Add k_new vertices labelled base_n.., with arc directions given by
    patterns: for each new vertex i, patterns[i] is a function old->bool (True =>
    new beats old). Arcs among new vertices: transitive (new_i -> new_j for i<j)."""
    n0, arcs0 = base
    arcs = list(arcs0)
    new = list(range(n0, n0 + k_new))
    for idx, v in enumerate(new):
        for u in range(n0):
            if patterns[idx](u):
                arcs.append((v, u))
            else:
                arcs.append((u, v))
    for i in range(len(new)):
        for j in range(i + 1, len(new)):
            arcs.append((new[i], new[j]))
    return (n0 + k_new, arcs)

# n=10: add 1 vertex. Try many random arc patterns + structured ones.
for trial in range(400):
    thr = rng.random()
    pat = [lambda u, thr=thr, rng=rng: rng.random() < thr]
    # but we need deterministic per-vertex; build explicit bitmask instead
for trial in range(400):
    mask = rng.getrandbits(9)
    pat = [lambda u, m=mask: ((m >> u) & 1) == 1]
    consider(augment(S3, 1, pat), f'S3+1[mask{mask}]')

# n=11: add 2 vertices.
for trial in range(400):
    m1 = rng.getrandbits(9)
    m2 = rng.getrandbits(9)
    pat = [lambda u, m=m1: ((m >> u) & 1) == 1,
           lambda u, m=m2: ((m >> u) & 1) == 1]
    consider(augment(S3, 2, pat), f'S3+2[m{m1},{m2}]')

# ---- candidate generator C: random tournaments at n=10,11 (broad net) ----
print('=== Generator C: random n=10,11 ===', flush=True)
for n in (10, 11):
    for seed in range(150):
        consider(random_tournament(n, seed=1000 * n + seed), f'rand_n{n}_s{seed}')

print(f'=== TOTAL omega_vec==3 hits at n10/11: {len(hits)} ===', flush=True)
wt = [h for h in hits if h.get('whole_tournament')]
print(f'=== whole-tournament 3-critical hits: {len(wt)} ===', flush=True)
json.dump(hits, open('data/whole_tournament_critical_n10_11.json', 'w'), indent=1)
print('saved data/whole_tournament_critical_n10_11.json', flush=True)
