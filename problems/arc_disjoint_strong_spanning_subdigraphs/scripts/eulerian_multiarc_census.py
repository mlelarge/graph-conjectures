"""Eulerian slice of the (n, maxmult) multi-arc cell.

H4 falsification arm: hunt an EULERIAN 3-arc-strong multidigraph with NO SAD.

The full (n=4, M=3) census cell (~1.5M instances) was marked foreground-
infeasible (D2/D3).  The Eulerian degree-balance condition is a PURE-ARITHMETIC
pre-filter on each multiplicity vector (in-mult-sum == out-mult-sum >= 3 at every
vertex) applied BEFORE any maxflow/SAD work, pruning the cell by orders of
magnitude.

Bases: all orientations (digons allowed) of all connected graphs on n vertices
with min degree >= 1 (`geng -c -d1 n | directg -T`).  At M=3 a mult-3 digon to a
single neighbour already gives degree 3, so underlying-degree-1 vertices are
admissible -- using -d2 would silently truncate the digon-pendant Eulerian
instances, so we MUST use -d1.

Pipeline per base arc-set A:
  sweep every multiplicity vector m in {1..M}^|A|
  ARITHMETIC filter first: for every vertex, in-mult-sum == out-mult-sum >= 3
  on survivors: oracle-exact lambda >= 3 filter
  on those: oracle.check_construction(cross_check=True), halt on any UNSAT/DISAGREE

Reads base simple digraphs from stdin (directg -T format), prints JSON at EOF.
Usage:
    geng -c -d1 <n> | directg -T | python eulerian_multiarc_census.py <n> --maxmult M
"""
import sys, os, json, time, itertools, argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import oracle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--maxmult", type=int, default=3)
    args = ap.parse_args()
    M = args.maxmult
    n = args.n

    t0 = time.time()
    n_bases = 0
    n_swept = 0            # total mult-vectors enumerated (no silent truncation)
    n_eulerian = 0         # passed arithmetic in==out>=3 filter
    n_lambda_ge3 = 0
    n_sat = 0
    unsat, disagree = [], []
    unknown = 0
    lam_hist = {}
    per_base = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); ne = int(toks[1])
        nums = list(map(int, toks[2:]))
        base_arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        assert len(base_arcs) == ne
        assert nv == n, f"base has {nv} vertices, expected {n}"
        n_bases += 1

        b_swept = 0
        b_euler = 0
        b_lam3 = 0
        b_sat = 0

        for mult in itertools.product(range(1, M + 1), repeat=ne):
            b_swept += 1
            n_swept += 1
            # Eulerian + necessary-lambda arithmetic pre-filter.
            indeg = [0] * nv
            outdeg = [0] * nv
            for (u, v), k in zip(base_arcs, mult):
                outdeg[u] += k
                indeg[v] += k
            ok = True
            for v in range(nv):
                if indeg[v] != outdeg[v] or indeg[v] < 3:
                    ok = False
                    break
            if not ok:
                continue
            b_euler += 1
            n_eulerian += 1

            arcs = []
            for (u, v), k in zip(base_arcs, mult):
                arcs.extend([(u, v)] * k)

            lam = oracle.arc_connectivity(nv, arcs)
            lam_hist[lam] = lam_hist.get(lam, 0) + 1
            if lam < 3:
                continue
            b_lam3 += 1
            n_lambda_ge3 += 1

            r = oracle.check_construction(nv, arcs, cross_check=False)
            if r["sad"] == "SAT":
                b_sat += 1
                n_sat += 1
                continue
            # non-SAT: re-decide with cross-check, record + halt immediately.
            r2 = oracle.check_construction(nv, arcs, cross_check=True)
            rec = {"n": nv, "lambda": lam,
                   "base_arcs": [list(a) for a in base_arcs],
                   "mult": list(mult),
                   "arcs": [list(a) for a in arcs],
                   "sad": r2["sad"], "cross_check": r2.get("cross_check")}
            if r2["sad"] == "UNSAT":
                unsat.append(rec)
                _emit(args, n_bases, n_swept, n_eulerian, n_lambda_ge3,
                      n_sat, unsat, disagree, unknown, lam_hist, per_base,
                      t0, halted="UNSAT")
                return
            elif r2["sad"] == "DISAGREE":
                disagree.append(rec)
                _emit(args, n_bases, n_swept, n_eulerian, n_lambda_ge3,
                      n_sat, unsat, disagree, unknown, lam_hist, per_base,
                      t0, halted="DISAGREE")
                return
            else:
                unknown += 1

        per_base.append({"base_arcs": [list(a) for a in base_arcs],
                         "swept": b_swept, "eulerian": b_euler,
                         "lambda_ge3": b_lam3, "sat": b_sat})

    _emit(args, n_bases, n_swept, n_eulerian, n_lambda_ge3,
          n_sat, unsat, disagree, unknown, lam_hist, per_base, t0, halted=None)


def _emit(args, n_bases, n_swept, n_eulerian, n_lambda_ge3, n_sat,
          unsat, disagree, unknown, lam_hist, per_base, t0, halted):
    summary = {
        "n": args.n,
        "maxmult": args.maxmult,
        "halted_on": halted,
        "n_bases_read": n_bases,
        "n_multvectors_swept": n_swept,
        "n_eulerian_survivors": n_eulerian,
        "n_lambda_ge3": n_lambda_ge3,
        "n_sat": n_sat,
        "n_unsat": len(unsat),
        "n_disagree": len(disagree),
        "n_unknown": unknown,
        "lambda_hist": lam_hist,
        "unsat_counterexamples": unsat,
        "disagree": disagree,
        "per_base": per_base,
        "elapsed_s": round(time.time() - t0, 2),
        "WC3_survives_eulerian_slice": len(unsat) == 0 and len(disagree) == 0,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
