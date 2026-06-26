"""Ground the dic=3 proposal: for each 3-omega_vec-critical witness, compute
min over OPTIMAL orders of chi(backedge graph).  NSS sandwich: dic <= chi, and
for an optimal order omega(backedge)=omega_vec, so chi>=omega=omega_vec=3 there;
hence min-optimal-chi==3  <=>  dic=3.  Prediction: ==3 for all witnesses.
KILL: any witness whose EVERY optimal-order backedge graph has chi>=4.
"""
import sys, os, json, itertools, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from core import backedge_graph, clique_number, is_tournament, omega_vec, omega_vec_bb
import networkx as nx

random.seed(12345)


def chi_exact(g):
    n = g.number_of_nodes()
    if n == 0:
        return 0
    nodes = sorted(g.nodes(), key=lambda v: -g.degree(v))
    adj = {v: set(g.neighbors(v)) for v in nodes}
    for k in range(1, n + 1):
        color = {}
        def bt(i):
            if i == len(nodes):
                return True
            v = nodes[i]
            used = {color[u] for u in adj[v] if u in color}
            for c in range(k):
                if c not in used:
                    color[v] = c
                    if bt(i + 1):
                        return True
                    del color[v]
            return False
        if bt(0):
            return k
    return n


def circ(n, g):
    gs = set(x % n for x in g)
    return [(i, j) for i in range(n) for j in range(n) if i != j and (j - i) % n in gs]


def exact_min_optimal_chi(n, arcs, ov):
    """EXACT over all n! orders: min chi among orders achieving omega==ov.
    Returns (min_chi, n_optimal_seen). Early-stops min_chi at ov."""
    best = n
    seen = 0
    for order in itertools.permutations(range(n)):
        bg = backedge_graph(n, arcs, order)
        om = clique_number(bg)
        if om == ov:
            seen += 1
            c = chi_exact(bg)
            if c < best:
                best = c
            if best == ov:
                # still count how many optimal exist? no: early exit is fine for min
                return best, seen
    return best, seen


def sampled_min_optimal_chi(n, arcs, ov, fix0=True, n_samples=200000):
    """For large vertex-transitive circulants: sample orders (optionally fixing
    orbit-rep vertex 0 first, sound by vertex-transitivity), keep optimal ones,
    take min chi.  Returns (min_chi_at_optimal, n_optimal_seen, n_sampled)."""
    best = n
    seen = 0
    rest = list(range(1, n)) if fix0 else list(range(n))
    for _ in range(n_samples):
        perm = rest[:]
        random.shuffle(perm)
        order = ([0] + perm) if fix0 else perm
        bg = backedge_graph(n, arcs, order)
        om = clique_number(bg)
        if om == ov:
            seen += 1
            c = chi_exact(bg)
            if c < best:
                best = c
            if best == ov:
                return best, seen, _ + 1
    return best, seen, n_samples


def load_critical(path, key=None):
    d = json.load(open(os.path.join(HERE, "..", path)))
    if key is not None:
        d = d[key]
    out = []
    for ex in d.get("critical_examples", []):
        arcs = [tuple(a) for a in ex["arcs"]]
        nn = max(max(a) for a in arcs) + 1
        out.append((nn, arcs))
    return out


results = []

# ---- QR7 (exact) ----
n, arcs = 7, circ(7, [1, 2, 4])
assert is_tournament(n, arcs)
ov = omega_vec(n, arcs)
mc, seen = exact_min_optimal_chi(n, arcs, ov)
results.append({"witness": "QR7", "n": 7, "omega_vec": ov, "min_optimal_chi": mc,
                "method": "exact_all_orders", "n_optimal_seen": seen})
print("QR7 omega_vec", ov, "min_optimal_chi", mc, flush=True)

# ---- n=8 critical (exact, both iso classes) ----
for i, (nn, arcs) in enumerate(load_critical("data/iso_critical_scan.json", "8")):
    assert is_tournament(nn, arcs)
    ov = omega_vec(nn, arcs)
    mc, seen = exact_min_optimal_chi(nn, arcs, ov)
    results.append({"witness": f"n8_crit_{i}", "n": nn, "omega_vec": ov,
                    "min_optimal_chi": mc, "method": "exact_all_orders",
                    "n_optimal_seen": seen})
    print(f"n8_crit_{i} omega_vec {ov} min_optimal_chi {mc}", flush=True)

# ---- n=9 critical (exact over 9!, the 10 saved examples) ----
for i, (nn, arcs) in enumerate(load_critical("data/iso_critical_scan_n9.json")):
    assert is_tournament(nn, arcs)
    ov = omega_vec(nn, arcs)
    mc, seen = exact_min_optimal_chi(nn, arcs, ov)
    results.append({"witness": f"n9_crit_{i}", "n": nn, "omega_vec": ov,
                    "min_optimal_chi": mc, "method": "exact_all_orders",
                    "n_optimal_seen": seen})
    print(f"n9_crit_{i} omega_vec {ov} min_optimal_chi {mc}", flush=True)

# ---- circulants (sampled, fix orbit-rep 0; vertex-transitive) ----
circulants = [
    ("C11_g12346", 11, [1, 2, 3, 4, 6]),
    ("C13_P9_g123457", 13, [1, 2, 3, 4, 5, 7]),
    ("C17_g1234567_9", 17, [1, 2, 3, 4, 5, 6, 7, 9]),
]
for nm, n, g in circulants:
    arcs = circ(n, g)
    assert is_tournament(n, arcs)
    # omega_vec known =3 from ledger; recompute lower bound by sampling for the
    # optimal-order filter we only need ov.  Use ledger value 3 as the optimal
    # target (we VERIFY it is achievable by finding an order with omega==3).
    ov = 3
    mc, seen, nsamp = sampled_min_optimal_chi(n, arcs, ov, fix0=True, n_samples=300000)
    results.append({"witness": nm, "n": n, "omega_vec_target": ov,
                    "min_optimal_chi": mc, "method": "sampled_fix0",
                    "n_optimal_seen": seen, "n_sampled": nsamp})
    print(f"{nm} (n={n}) optimal-orders-seen {seen} min_optimal_chi {mc}", flush=True)

# ---- VERDICT ----
all3 = all(r["min_optimal_chi"] == 3 for r in results)
any_no_optimal = any(r.get("n_optimal_seen", 1) == 0 for r in results)
print("\n=== SUMMARY ===")
for r in results:
    print(r)
print("\nALL min_optimal_chi == 3 :", all3)
print("any witness with NO optimal order sampled:", any_no_optimal)
json.dump({"results": results, "all_min_optimal_chi_eq_3": all3},
          open(os.path.join(HERE, "..", "data", "dic_grounding.json"), "w"), indent=1)
