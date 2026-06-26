"""SHARDED dic census v2 (robust): same soundness/completeness as
census_dic_circulant_shard.py but with PER-SAT-CALL time budgets so a single hard
no-K5 instance cannot stall the whole shard (this is what killed n=31 unsharded
and the v1 shard [350,500)). Each no-K5 solve runs under a wall-clock budget on
BOTH Cadical153 and Minisat22; if EITHER hits the budget the orbit is recorded
as HARD (undecided ov) and skipped -- it is NOT a jackpot and NOT silently
counted SAT. UNSAT x2 within budget => JACKPOT (5-dic-vc, ov>=5), the Prop 6.2
k=5 input candidate.

Usage: census_dic_circulant_shard2.py n start end [budget_s]
Output: data/census2_dic_n{n}_shard_{start}_{end}.json
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
        seen[canon] = seen.get(canon, 0) + 1
    assert total == 2 ** len(pairs)
    return [(c, cnt) for c, cnt in sorted(seen.items())], total


def dic_of(n, arcs, kmax=6):
    tris = directed_triangles(n, arcs)
    for k in range(1, kmax + 1):
        if dicolorable(n, arcs, k, tris):
            return k
    return kmax + 1


def solve_budget(cnf_clauses, SolverCls, budget_s):
    """Return (solved, result) where solved=False means budget hit/interrupted."""
    s = SolverCls(bootstrap_with=cnf_clauses, use_timer=True)
    try:
        try:
            res = s.solve_limited(expect_interrupt=True)
        except TypeError:
            res = s.solve()
        # solve_limited without a budget call returns immediately; we instead use
        # interrupt via a wall thread below for solvers lacking budgets.
        return (res is not None), res
    finally:
        s.delete()


def no_k5_decide(n, arcs, budget_s):
    """UNSAT x2 within budget -> ('UNSAT'); SAT (either) -> 'SAT';
    budget hit -> 'HARD'. Uses a watchdog thread to interrupt."""
    import threading
    cnf, _ = build_cnf_no_kclique(n, arcs, 5)
    clauses = cnf.clauses
    results = {}
    for name, Cls in (("cadical", Cadical153), ("minisat", Minisat22)):
        s = Cls(bootstrap_with=clauses, use_timer=True)
        done = {"v": None}
        def run():
            try:
                done["v"] = s.solve()
            except Exception:
                done["v"] = "ERR"
        t = threading.Thread(target=run)
        t.start()
        t.join(budget_s)
        if t.is_alive():
            try:
                s.interrupt()
            except Exception:
                pass
            t.join(5)
            try:
                s.delete()
            except Exception:
                pass
            return "HARD", {name: "timeout"}
        r = done["v"]
        try:
            s.delete()
        except Exception:
            pass
        results[name] = r
        if r is True:  # SAT -> ov<=4, no need to run other solver
            return "SAT", results
    # both ran; neither SAT
    if results.get("cadical") is False and results.get("minisat") is False:
        return "UNSAT", results
    return "HARD", results


def main():
    n, start, end = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 20.0
    t0 = time.time()
    orbits, total = all_generator_orbits(n)
    end = min(end, len(orbits))
    print(f"n={n}: {total} gen sets, {len(orbits)} orbits; shard [{start},{end}) "
          f"budget={budget}s", flush=True)
    rows, hist = [], {}
    jackpots, hard = [], []
    for i in range(start, end):
        g, osz = orbits[i]
        arcs = circ_arcs(n, list(g))
        ti = time.time()
        k = dic_of(n, arcs)
        hist[k] = hist.get(k, 0) + osz
        row = {"i": i, "g": sorted(g), "orbit": osz, "dic": k}
        if k >= 4:
            nn, aa = sub(n, arcs, 0)
            row["vertex_critical"] = bool(dicolorable(nn, aa, k - 1))
            if k == 5 and row["vertex_critical"]:
                verdict, detail = no_k5_decide(n, arcs, budget)
                row["noK5"] = verdict
                if verdict == "SAT":
                    row["ov"] = "<=4"
                elif verdict == "UNSAT":
                    row["ov"] = ">=5"
                    jackpots.append(row)
                    print("JACKPOT (5-dic-vc, ov>=5):", row, flush=True)
                else:
                    row["ov"] = "HARD"
                    hard.append(row)
                    print(f"  HARD noK5 i={i} g={sorted(g)} detail={detail} "
                          f"({time.time()-ti:.0f}s)", flush=True)
        rows.append(row)
        if (i - start) % 25 == 0:
            print(f"  ..orbit {i} ({time.time()-t0:.0f}s) dic={k} "
                  f"vc={row.get('vertex_critical','-')} dt={time.time()-ti:.1f}s",
                  flush=True)
    dt = time.time() - t0
    n5vc = sum(1 for r in rows if r["dic"] == 5 and r.get("vertex_critical"))
    out = {"n": n, "shard": [start, end], "n_orbits_total": len(orbits),
           "total_gen_sets": total, "hist_labelled_shard": hist, "budget_s": budget,
           "time_s": round(dt, 1), "n_dic5_vc": n5vc, "n_jackpot": len(jackpots),
           "n_hard": len(hard),
           "rows_ge4": [r for r in rows if r["dic"] >= 4], "n_rows": len(rows)}
    path = os.path.join(os.path.dirname(__file__), '..', 'data',
                        f'census2_dic_n{n}_shard_{start}_{end}.json')
    json.dump(out, open(path, 'w'), indent=1)
    print(f"SHARD2 DONE n={n} [{start},{end}) hist={hist} dic5_vc={n5vc} "
          f"jackpots={len(jackpots)} hard={len(hard)} time={dt:.1f}s", flush=True)


if __name__ == "__main__":
    main()
