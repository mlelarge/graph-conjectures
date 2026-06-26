"""SHARDED dic census v3 (fully budget-guarded). Same soundness/completeness as
census_dic_circulant_shard.py, but EVERY SAT call (dicolorability ladder AND
no-K5) runs under a wall-clock budget via a watchdog thread that calls
solver.interrupt(). A budget hit => orbit recorded HARD (undecided), never
silently miscounted. This removes the unguarded dicolorability stall that killed
n=31 unsharded and shard v1/v2 in the dense dic>=5 region.

dic computed by climbing k=1..6; a k where dicolorable is SAT gives dic=k. The
costly checks are the UNSAT ones (dic>k). We budget each.

JACKPOT = dic==5, vertex-critical (T-0 not 4-dicolorable), and no-K5 UNSAT x2
within budget => omega_vec>=5 (Prop 6.2 k=5 input candidate).

Usage: census_dic_circulant_shard3.py n start end [dic_budget_s] [sat_budget_s]
Output: data/census3_dic_n{n}_shard_{start}_{end}.json
"""
import sys, os, json, time, threading
sys.path.insert(0, os.path.dirname(__file__))
from math import gcd
from ground_lift_lemma_step1 import directed_triangles, sub
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
        seen[canon] = seen.get(canon, 0) + 1
    assert total == 2 ** len(pairs)
    return [(c, cnt) for c, cnt in sorted(seen.items())], total


def solve_guarded(clauses, SolverCls, budget):
    """Return True/False (sat result) or None if budget hit."""
    s = SolverCls(bootstrap_with=clauses)
    done = {"v": "PENDING"}
    def run():
        try:
            done["v"] = s.solve()
        except Exception:
            done["v"] = "ERR"
    t = threading.Thread(target=run)
    t.start()
    t.join(budget)
    if t.is_alive():
        try: s.interrupt()
        except Exception: pass
        t.join(5)
        try: s.delete()
        except Exception: pass
        return None
    try: s.delete()
    except Exception: pass
    v = done["v"]
    return v if v in (True, False) else None


def dicolorable_clauses(n, arcs, k, tris):
    var = lambda v, c: v * k + c + 1
    cls = [[var(v, c) for c in range(k)] for v in range(n)]
    for (u, v, w) in tris:
        for c in range(k):
            cls.append([-var(u, c), -var(v, c), -var(w, c)])
    cls.append([var(0, 0)])
    return cls


def dicolorable_g(n, arcs, k, tris, budget):
    if k >= n: return True
    if not tris: return k >= 1
    if k <= 0: return False
    return solve_guarded(dicolorable_clauses(n, arcs, k, tris), Cadical153, budget)


def dic_of_g(n, arcs, budget, kmax=6):
    """Return dic (int) or None if any decisive check timed out."""
    tris = directed_triangles(n, arcs)
    for k in range(1, kmax + 1):
        r = dicolorable_g(n, arcs, k, tris, budget)
        if r is None:
            return None
        if r:
            return k
    return kmax + 1


def no_k5_decide(n, arcs, budget):
    cnf, _ = build_cnf_no_kclique(n, arcs, 5)
    clauses = cnf.clauses
    res = {}
    for name, Cls in (("cadical", Cadical153), ("minisat", Minisat22)):
        r = solve_guarded(clauses, Cls, budget)
        res[name] = r
        if r is None:
            return "HARD", res
        if r is True:
            return "SAT", res
    if res["cadical"] is False and res["minisat"] is False:
        return "UNSAT", res
    return "HARD", res


def main():
    n, start, end = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    dic_budget = float(sys.argv[4]) if len(sys.argv) > 4 else 8.0
    sat_budget = float(sys.argv[5]) if len(sys.argv) > 5 else 15.0
    t0 = time.time()
    orbits, total = all_generator_orbits(n)
    end = min(end, len(orbits))
    print(f"n={n}: {total} gen, {len(orbits)} orbits; shard [{start},{end}) "
          f"dicB={dic_budget}s satB={sat_budget}s", flush=True)
    rows, hist = [], {}
    jackpots, hard = [], []
    for i in range(start, end):
        g, osz = orbits[i]
        arcs = circ_arcs(n, list(g))
        ti = time.time()
        k = dic_of_g(n, arcs, dic_budget)
        if k is None:
            row = {"i": i, "g": sorted(g), "orbit": osz, "dic": "HARD"}
            hard.append(row); rows.append(row)
            hist["HARD"] = hist.get("HARD", 0) + osz
            print(f"  HARD dic i={i} g={sorted(g)} ({time.time()-ti:.0f}s)", flush=True)
            continue
        hist[k] = hist.get(k, 0) + osz
        row = {"i": i, "g": sorted(g), "orbit": osz, "dic": k}
        if k >= 4:
            nn, aa = sub(n, arcs, 0)
            vc = dicolorable_g(nn, aa, k - 1, directed_triangles(nn, aa), dic_budget)
            row["vertex_critical"] = (None if vc is None else bool(vc))
            if k == 5 and vc is True:
                verdict, detail = no_k5_decide(n, arcs, sat_budget)
                row["noK5"] = verdict
                if verdict == "SAT":
                    row["ov"] = "<=4"
                elif verdict == "UNSAT":
                    row["ov"] = ">=5"; jackpots.append(row)
                    print("JACKPOT (5-dic-vc, ov>=5):", row, flush=True)
                else:
                    row["ov"] = "HARD"; hard.append(row)
                    print(f"  HARD noK5 i={i} g={sorted(g)} {detail} "
                          f"({time.time()-ti:.0f}s)", flush=True)
        rows.append(row)
        if (i - start) % 25 == 0:
            print(f"  ..orbit {i} ({time.time()-t0:.0f}s) dic={k} dt={time.time()-ti:.1f}s",
                  flush=True)
    dt = time.time() - t0
    n5vc = sum(1 for r in rows if r["dic"] == 5 and r.get("vertex_critical") is True)
    out = {"n": n, "shard": [start, end], "n_orbits_total": len(orbits),
           "total_gen_sets": total, "hist_labelled_shard": hist,
           "dic_budget_s": dic_budget, "sat_budget_s": sat_budget,
           "time_s": round(dt, 1), "n_dic5_vc": n5vc, "n_jackpot": len(jackpots),
           "n_hard": len(hard), "hard": hard,
           "rows_ge4": [r for r in rows if r["dic"] != "HARD" and r["dic"] >= 4],
           "n_rows": len(rows)}
    path = os.path.join(os.path.dirname(__file__), '..', 'data',
                        f'census3_dic_n{n}_shard_{start}_{end}.json')
    json.dump(out, open(path, 'w'), indent=1)
    print(f"SHARD3 DONE n={n} [{start},{end}) hist={hist} dic5_vc={n5vc} "
          f"jackpots={len(jackpots)} hard={len(hard)} time={dt:.1f}s", flush=True)


if __name__ == "__main__":
    main()
