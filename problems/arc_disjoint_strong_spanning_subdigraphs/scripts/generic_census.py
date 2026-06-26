"""H1-GENERIC-CENSUS: exhaustive generic census of small 3-arc-strong digraphs.

Pipeline (the universal_needs_generic_census gate the prior 310k STRUCTURED
search never passed):

    geng -d3 <n> | directg -T   ->  stdin of this script

geng -d3 emits all simple undirected graphs on n vertices with min degree >= 3
(a NECESSARY condition for arc-connectivity >= 3, since lambda>=3 forces min
in-degree AND out-degree >= 3, hence underlying degree >= 3).  directg -T
orients each edge in all ways (forward / backward / both), emitting one simple
*digraph* per line as:  nv ne u1 v1 u2 v2 ...  (each pair = one directed arc).
Isomorphic digraphs are suppressed by directg, so this is a canonical,
duplicate-free, EXHAUSTIVE enumeration of all simple digraphs whose underlying
graph has min degree >= 3.

For each digraph we compute lambda^arc exactly (oracle.arc_connectivity).
Survivors with lambda >= 3 are SAD-decided.  Any UNSAT is re-decided with the
ILP cross-check and reported as a CANDIDATE COUNTEREXAMPLE to WC3.

Usage:  geng -d3 6 | directg -T | python generic_census.py 6
Reads digraphs from stdin; prints a JSON summary to stdout at EOF.
"""
import sys, os, json, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import oracle


def main():
    n_expected = int(sys.argv[1]) if len(sys.argv) > 1 else None
    t0 = time.time()
    n_digraphs = 0
    n_lambda_ge3 = 0
    n_sat = 0
    unsat = []        # confirmed-UNSAT (ILP-cross-checked) counterexamples
    disagree = []     # backend disagreements (untrusted)
    unknown = 0
    lam_hist = {}     # lambda -> count among all digraphs read

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); ne = int(toks[1])
        nums = list(map(int, toks[2:]))
        arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        assert len(arcs) == ne, (ne, len(arcs), line)
        n_digraphs += 1

        lam = oracle.arc_connectivity(nv, arcs)
        lam_hist[lam] = lam_hist.get(lam, 0) + 1
        if lam < 3:
            continue
        n_lambda_ge3 += 1

        # SAD-decide.  Fast SAT pass (no cross-check); escalate on UNSAT/UNKNOWN.
        r = oracle.check_construction(nv, arcs, cross_check=False)
        sad = r["sad"]
        if sad == "SAT":
            n_sat += 1
            continue
        # Anything not SAT is load-bearing -> cross-check with ILP.
        r2 = oracle.check_construction(nv, arcs, cross_check=True)
        rec = {"n": nv, "lambda": lam, "arcs": [list(a) for a in arcs],
               "sad": r2["sad"], "cross_check": r2.get("cross_check")}
        if r2["sad"] == "UNSAT":
            unsat.append(rec)
        elif r2["sad"] == "DISAGREE":
            disagree.append(rec)
        else:
            unknown += 1

    summary = {
        "n": n_expected,
        "n_digraphs_read": n_digraphs,
        "n_lambda_ge3": n_lambda_ge3,
        "n_sat": n_sat,
        "n_unsat": len(unsat),
        "n_disagree": len(disagree),
        "n_unknown": unknown,
        "lambda_hist": lam_hist,
        "unsat_counterexamples": unsat,
        "disagree": disagree,
        "elapsed_s": round(time.time() - t0, 2),
        "WC3_survives": len(unsat) == 0 and len(disagree) == 0,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
