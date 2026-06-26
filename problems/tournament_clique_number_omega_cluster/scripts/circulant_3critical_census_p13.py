"""GROUND the asymptotic-density proposal (D5).

Per the proposal's ground_plan: iterate ALL 2^{(p-1)/2} generator sets g (NO
g/-g dedup -- the proposal explicitly counts gen-sets, denominator 2^{(p-1)/2}),
classify each circulant C_p(g):
   'omega_le2'      : omega_vec(T) <= 2
   'crit'           : omega_vec(T)==3 AND every deletion ==2  (3-omega_vec-critical)
   'omega3_noncrit' : omega_vec(T) >= 3 but deletion v=p-1 has omega_vec >= 3
report c(p) = #crit, full histogram, d(p)=c(p)/2^{(p-1)/2}.

Classification per ground_plan: delete the FIXED vertex p-1 (vertex-transitive =>
all deletions isomorphic, so one deletion decides criticality).  This is the
fast le2-census the proposal says it validated against saved oracle data on
p=7,11 -- we re-run p=7 and p=11 in the SAME script as a calibration cross-check.

Uses ONLY the validated fast routines from iso_critical_scan_n9 (omega_vec_le2,
omega_vec_le_t with node_budget) + core.is_tournament/beats_matrix.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from core import is_tournament
from iso_critical_scan_n9 import omega_vec_le2, omega_vec_le_t, sub_beats


def circ_arcs(p, g):
    gs = set(g)
    return [(i, (i + d) % p) for i in range(p) for d in g] if False else \
           [(i, j) for i in range(p) for j in range(p) if i != j and (j - i) % p in gs]


def beats_matrix(p, arcs):
    b = [[False] * p for _ in range(p)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def gen_sets(p):
    """ALL 2^{(p-1)/2} generator sets: for each antipodal pair {d,p-d} pick one."""
    half = (p - 1) // 2
    pairs = [(d, p - d) for d in range(1, half + 1)]
    for bits in itertools.product((0, 1), repeat=half):
        yield tuple(sorted(pairs[i][bits[i]] for i in range(half)))


def is_transitive(m, sb):
    score = [sum(sb[u][v] for v in range(m)) for u in range(m)]
    return sorted(score) == list(range(m))


def classify(p, g, node_budget=2_000_000):
    arcs = circ_arcs(p, g)
    if not is_tournament(p, arcs):
        return None, arcs
    beats = beats_matrix(p, arcs)
    if omega_vec_le2(p, beats):
        return 'omega_le2', arcs
    # omega_vec(T) >= 3.  delete fixed vertex p-1
    m, sb = sub_beats(p, beats, p - 1)
    if omega_vec_le2(m, sb) and not is_transitive(m, sb):
        # omega_vec(T - (p-1)) == 2; vertex-transitive => all deletions == 2;
        # sub-additivity forces omega_vec(T) == 3 -> 3-critical
        return 'crit', arcs
    return 'omega3_noncrit', arcs


def census(p, node_budget=2_000_000):
    hist = {}
    crit_gens = []
    t0 = time.time()
    total = 0
    for g in gen_sets(p):
        total += 1
        cls, _ = classify(p, g, node_budget=node_budget)
        if cls is None:
            cls = 'not_tournament'
        hist[cls] = hist.get(cls, 0) + 1
        if cls == 'crit':
            crit_gens.append(list(g))
    denom = 2 ** ((p - 1) // 2)
    c = hist.get('crit', 0)
    return {
        'p': p,
        'num_gen_sets': total,
        'denominator_2^((p-1)/2)': denom,
        'histogram': hist,
        'c(p)_num_3critical': c,
        'd(p)_density': round(c / denom, 6),
        'critical_gens': crit_gens,
        'seconds': round(time.time() - t0, 2),
    }


if __name__ == '__main__':
    # calibration: reproduce p=7 and p=11 in the SAME script
    for p in (7, 11):
        r = census(p)
        print(f"[calib p={p}] c={r['c(p)_num_3critical']} d={r['d(p)_density']} "
              f"hist={r['histogram']} denom={r['denominator_2^((p-1)/2)']} "
              f"({r['seconds']}s)", flush=True)

    p13 = census(13)
    print(json.dumps(p13, indent=2), flush=True)
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data',
                                       'circulant_3critical_census_p13.json'))
    json.dump(p13, open(out, 'w'), indent=2)
    print('SAVED', out, flush=True)
    print(f"=== RESULT p=13: c(13)={p13['c(p)_num_3critical']} "
          f"d(13)={p13['d(p)_density']} hist={p13['histogram']} ===", flush=True)
