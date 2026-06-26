"""SHARDED exhaustive dic census of ALL circulant tournaments on Z/n (odd n),
extending census_dic_circulant.py past the n=29 wall (n=31 died at 880s
unsharded). Same soundness/completeness argument: enumerate ALL 2^{(n-1)/2}
generator sets, canonicalize by min over units of Z/n (covers reversal via -1),
keep one rep per unit-orbit; sum of orbit sizes == 2^{(n-1)/2} (asserted).

Shard semantics: the orbit list is DETERMINISTIC (sorted canon tuples); a shard
processes orbit indices [start, end). Per rep:
  dic via validated mono-triangle-free SAT (ground_lift_lemma_step1.dicolorable);
  if dic >= 4: vertex-criticality = dicolorable(T-0, dic-1) (one deletion
  suffices: circulant => vertex-transitive);
  if dic == 5 and vertex-critical: STEP-3 inline -- no-K5 CNF
  (build_cnf_no_kclique, validated) on BOTH Cadical153 and Minisat22:
  SAT => ov <= 4 (kill); UNSAT x2 => ov >= 5 (JACKPOT = Prop 6.2 k=5 input
  candidate; then a clique-5 witness order would pin ov = 5).

Output: data/census_dic_n{n}_shard_{start}_{end}.json (merged later).
Usage: census_dic_circulant_shard.py n start end
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from math import gcd
from ground_lift_lemma_step1 import dicolorable, directed_triangles, sub
from search_4critical_circulant import build_cnf_no_kclique
from pysat.solvers import Cadical153, Minisat22
import itertools


def circ_arcs(n, g):
    return [(i, (i + d) % n) for i in range(n) for d in g]


def all_generator_orbits(n):
    pairs = [(d, n - d) for d in range(1, (n + 1) // 2)]
    units = [u for u in range(1, n) if gcd(u, n) == 1]
    seen = {}
    total = 0
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        g = frozenset(p[b] for p, b in zip(pairs, bits))
        total += 1
        canon = min(tuple(sorted((u * d) % n for d in g)) for u in units)
        seen.setdefault(canon, 0)
        seen[canon] += 1
    assert total == 2 ** len(pairs)
    return [(c, cnt) for c, cnt in sorted(seen.items())], total


def dic_of(n, arcs, kmax=6):
    tris = directed_triangles(n, arcs)
    for k in range(1, kmax + 1):
        if dicolorable(n, arcs, k, tris):
            return k
    return kmax + 1


def no_k5_both(n, arcs):
    cnf, _ = build_cnf_no_kclique(n, arcs, 5)
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        s1 = m.solve()
    with Minisat22(bootstrap_with=cnf.clauses) as m:
        s2 = m.solve()
    assert s1 == s2, f"SOLVER DISAGREEMENT n={n} K=5"
    return s1


def main():
    n, start, end = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    t0 = time.time()
    orbits, total = all_generator_orbits(n)
    end = min(end, len(orbits))
    print(f"n={n}: {total} gen sets, {len(orbits)} unit-orbits "
          f"(enum {time.time()-t0:.1f}s); shard [{start},{end})", flush=True)
    rows, hist = [], {}
    jackpots = []
    for i in range(start, end):
        g, osz = orbits[i]
        arcs = circ_arcs(n, list(g))
        k = dic_of(n, arcs)
        hist[k] = hist.get(k, 0) + osz
        row = {"i": i, "g": sorted(g), "orbit": osz, "dic": k}
        if k >= 4:
            nn, aa = sub(n, arcs, 0)
            row["vertex_critical"] = bool(dicolorable(nn, aa, k - 1))
            if k == 5 and row["vertex_critical"]:
                sat5 = no_k5_both(n, arcs)
                row["noK5_sat"] = sat5
                row["ov"] = "<=4" if sat5 else ">=5"
                if not sat5:
                    jackpots.append(row)
                    print("JACKPOT (5-dic-vc, ov>=5):", row, flush=True)
        rows.append(row)
        verbose = os.environ.get("SHARD_VERBOSE")
        if verbose or (i - start) % 50 == 0:
            print(f"  ..orbit {i} ({time.time()-t0:.0f}s) dic={k} "
                  f"vc={row.get('vertex_critical','-')}", flush=True)
    dt = time.time() - t0
    n5vc = sum(1 for r in rows if r["dic"] == 5 and r.get("vertex_critical"))
    out = {"n": n, "shard": [start, end], "n_orbits_total": len(orbits),
           "total_gen_sets": total, "hist_labelled_shard": hist,
           "time_s": round(dt, 1), "n_dic5_vc": n5vc,
           "n_jackpot": len(jackpots),
           "rows_ge4": [r for r in rows if r["dic"] >= 4],
           "n_rows": len(rows)}
    path = os.path.join(os.path.dirname(__file__), '..', 'data',
                        f'census_dic_n{n}_shard_{start}_{end}.json')
    json.dump(out, open(path, 'w'), indent=1)
    print(f"SHARD DONE n={n} [{start},{end}) hist={hist} dic5_vc={n5vc} "
          f"jackpots={len(jackpots)} time={dt:.1f}s saved={path}", flush=True)


if __name__ == "__main__":
    main()
