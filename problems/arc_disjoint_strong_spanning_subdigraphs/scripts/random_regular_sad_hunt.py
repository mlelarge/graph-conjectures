"""Random 3-in/3-out (lambda=3) digraph SAD hunt + Hamilton-peeling mechanism check.

Model: D_n = union of 3 iid uniform permutations of [n], arcs {(i, sigma_j(i))}.
Reject samples with self-loops or parallel arcs (keep model SIMPLE and generic).
Accept only if oracle.arc_connectivity == 3.

For each accepted sample:
  (A) SAD-decide via oracle.check_construction(..., cross_check=True).
      Any UNSAT = oracle-certified WC3 counterexample. Any DISAGREE flagged.
  (B) Mechanism predicate M(D): exists a Hamilton cycle H subseteq D with
      D - A(H) strongly connected. Solved by ILP over arc-vars for a Hamilton
      cycle (in/out-degree 1, single-commodity flow MTZ subtour elimination),
      iterating with no-good cuts until some H gives D-A(H) strong, or
      Hamilton cycles exhausted / iteration cap hit.

Single foreground run; no backgrounding.
"""
from __future__ import annotations
import argparse, json, os, random, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import oracle  # noqa: E402

import networkx as nx  # noqa: E402
import pulp  # noqa: E402


def _derangement(n, rng):
    """Uniform-ish derangement via rejection of fixed points (early-restart)."""
    while True:
        perm = list(range(n))
        rng.shuffle(perm)
        if all(perm[i] != i for i in range(n)):
            return perm


def draw_sample(n, rng, simple=False):
    """3 iid uniform DERANGEMENTS of [n], arcs (i, sigma_j(i)).

    This is the genuine random 3-in/3-out MULTIdigraph model (parallel arcs
    kept; Cooper-Frieze random k-in/k-out is exactly this multi model). Drawing
    derangements directly removes the self-loop rejection bottleneck. If
    simple=True, reject any sample with a parallel arc (almost never accepts at
    moderate n, by the birthday bound on permutation coincidences)."""
    arcs = []
    seen = set()
    for _ in range(3):
        perm = _derangement(n, rng)
        for i in range(n):
            a = (i, perm[i])
            if simple and a in seen:
                return None
            seen.add(a)
            arcs.append(a)
    return arcs


def is_strong(n, arcs):
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from(arcs)
    return nx.is_strongly_connected(g)


def find_hamilton_cycle(n, idx_arcs, excluded):
    """ILP over indexed arc copies (handles parallel arcs).
    idx_arcs: list of (k, (i,j)) where k is a unique copy index.
    excluded: list of frozensets of copy-indices to forbid as a full cycle.
    Returns a frozenset of copy-indices forming a Hamilton cycle, or None."""
    prob = pulp.LpProblem("ham", pulp.LpMinimize)
    x = {k: pulp.LpVariable(f"x_{k}", cat="Binary") for k, _ in idx_arcs}
    tail = {k: a[0] for k, a in idx_arcs}
    head = {k: a[1] for k, a in idx_arcs}
    for v in range(n):
        prob += pulp.lpSum(x[k] for k, _ in idx_arcs if tail[k] == v) == 1
        prob += pulp.lpSum(x[k] for k, _ in idx_arcs if head[k] == v) == 1
    u = {v: pulp.LpVariable(f"u_{v}", lowBound=0, upBound=n - 1, cat="Continuous")
         for v in range(n)}
    prob += u[0] == 0
    for k, (i, j) in idx_arcs:
        if j != 0:
            prob += u[j] >= u[i] + 1 - n * (1 - x[k])
    for ex in excluded:
        prob += pulp.lpSum(x[k] for k in ex) <= len(ex) - 1
    prob += 0
    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[status] != "Optimal":
        return None
    chosen = frozenset(k for k, _ in idx_arcs if x[k].value() and x[k].value() > 0.5)
    if len(chosen) != n:
        return None
    return chosen


def mechanism_M(n, arcs, cap=200):
    """Return (status, ham_count). status in {'M_true','M_false','cap_hit'}.
    Hamilton-peeling: exists Hamilton H with D - A(H) strongly connected."""
    idx_arcs = list(enumerate(arcs))
    excluded = []
    for it in range(cap):
        H = find_hamilton_cycle(n, idx_arcs, excluded)
        if H is None:
            return ("M_false", it)  # Hamilton cycles exhausted, none worked
        rest = [a for k, a in idx_arcs if k not in H]
        if is_strong(n, rest):
            return ("M_true", it + 1)
        excluded.append(H)
    return ("cap_hit", cap)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="12,24,48")
    ap.add_argument("--samples", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cap", type=int, default=200)
    args = ap.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]

    overall = {}
    witnesses = []
    for n in sizes:
        rng = random.Random(args.seed * 1000 + n)
        accepted = 0
        sat = unsat = disagree = unknown = 0
        m_true = m_false = m_cap = 0
        draws = 0
        while accepted < args.samples and draws < args.samples * 200:
            draws += 1
            arcs = draw_sample(n, rng)
            if arcs is None:
                continue
            lam = oracle.arc_connectivity(n, arcs)
            if lam != 3:
                continue
            accepted += 1
            res = oracle.check_construction(n, arcs, name=f"rr_n{n}_s{accepted}",
                                            cross_check=True)
            verdict = res["sad"]
            cc = res.get("cross_check")
            if cc is not None and not cc.get("agree", True):
                disagree += 1
                witnesses.append({"type": "DISAGREE", "n": n, "arcs": arcs, "res": res})
            elif verdict == "SAT":
                sat += 1
            elif verdict == "UNSAT":
                unsat += 1
                witnesses.append({"type": "UNSAT", "n": n, "arcs": arcs, "res": res})
            else:
                unknown += 1
                witnesses.append({"type": "UNKNOWN", "n": n, "arcs": arcs, "res": res})
            mstat, _ = mechanism_M(n, arcs, cap=args.cap)
            if mstat == "M_true":
                m_true += 1
            elif mstat == "M_false":
                m_false += 1
                witnesses.append({"type": "M_FALSE", "n": n, "arcs": arcs})
            else:
                m_cap += 1
            print(f"  [n={n}] sample {accepted}/{args.samples}: "
                  f"SAD={verdict} M={mstat}", flush=True)
        overall[n] = dict(accepted=accepted, draws=draws, sat=sat, unsat=unsat,
                          disagree=disagree, unknown=unknown,
                          m_true=m_true, m_false=m_false, m_cap=m_cap)

    print("\n=== SUMMARY ===")
    print(f"{'n':>4} {'acc':>4} {'SAT':>4} {'UNSAT':>6} {'DIS':>4} {'UNK':>4} "
          f"{'M_T':>4} {'M_F':>4} {'cap':>4} {'M_rate':>7}")
    for n in sizes:
        r = overall[n]
        denom = r["m_true"] + r["m_false"] + r["m_cap"]
        rate = r["m_true"] / denom if denom else 0.0
        print(f"{n:>4} {r['accepted']:>4} {r['sat']:>4} {r['unsat']:>6} "
              f"{r['disagree']:>4} {r['unknown']:>4} {r['m_true']:>4} "
              f"{r['m_false']:>4} {r['m_cap']:>4} {rate:>7.3f}")

    out = {"params": vars(args), "overall": overall, "witnesses": witnesses}
    wpath = os.path.join(os.path.dirname(_HERE), "data",
                         f"random_regular_sad_hunt_seed{args.seed}.json")
    os.makedirs(os.path.dirname(wpath), exist_ok=True)
    with open(wpath, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {wpath}")
    nonsat = sum(overall[n]["unsat"] + overall[n]["disagree"] + overall[n]["unknown"]
                 for n in sizes)
    print(f"TOTAL non-SAT (UNSAT/DISAGREE/UNKNOWN): {nonsat}")


if __name__ == "__main__":
    main()
