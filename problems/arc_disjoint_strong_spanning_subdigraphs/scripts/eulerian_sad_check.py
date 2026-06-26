"""ESAD red-team: does every Eulerian lambda>=c digraph admit an EULERIAN SAD?

EULERIAN SAD (ESAD): a partition of the arc multiset A into two parts A_1, A_2
such that BOTH parts are
   (i)  per-vertex BALANCED (d^+ = d^- at every vertex), and
   (ii) weakly CONNECTED and SPANNING (the underlying undirected graph of the
        part touches every vertex and is connected).
Lemma (used here): a non-trivial digraph that is balanced AND weakly connected
is strongly connected.  Hence an ESAD is automatically an ordinary SAD; ESAD is
the STRICTLY STRONGER property the FKK route would deliver.

Because D itself is Eulerian (balanced), A_1 balanced  <=>  A_2 balanced; so we
only constrain ONE part to be balanced and the complement is balanced for free.
We still require BOTH parts to be weakly-connected+spanning.

Claim under test (UNIVERSAL, the proposal's ESAD(c)): every Eulerian
lambda^arc >= c instance admits an ESAD.  We locate the empirical threshold
c_emp = min lambda with ZERO ESAD failures.

KILL arm: a single Eulerian instance with lambda >= 4 that has an ordinary SAD
(oracle SAT) but NO balanced-connected 2-split (ESAD fails).

Method: ILP over binary x_a (a in arc-multiset, class-1 indicator) with
  - balance:  sum_{a out of v} x_a  ==  sum_{a into v} x_a   for all v
  - non-trivial:  1 <= sum x_a <= m-1   (both parts non-empty)
  - >=1 incident arc of each class at every vertex (spanning, necessary)
Weak connectivity of BOTH parts is enforced by LAZY no-good cuts: solve, check
weak-connectivity of part1 and part2 on the underlying undirected support; if a
part is disconnected, add a cut forbidding that exact assignment's connectivity
failure (a min-cut separating set must gain a crossing arc), and re-solve.  This
is exact: it terminates with either an ESAD or a proof of infeasibility.

Every YES witness is CROSS-VALIDATED by the oracle: both parts fed to
oracle.check_construction as standalone digraphs must be strong (SAT-trivially:
a strong spanning digraph on n vertices is its own SAD-less strong subdigraph;
we directly check strong-connectivity via the digraph backend).

Input universe: Eulerian slice of the (n, maxmult) multi-arc cell, exactly as in
eulerian_multiarc_census.py:  geng -c -d1 n | directg -T  base supports, all
multiplicity vectors {1..M}^arcs, arithmetic Eulerian (in==out>=3) pre-filter,
oracle-exact lambda filter.  Driven internally so this is ONE foreground command.

Usage:
    python eulerian_sad_check.py --n 4 --maxmult 3 [--lambda-min 4] [--limit N]
"""
import sys, os, json, time, itertools, argparse, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)
from digraph import Digraph  # noqa: E402

import pulp  # noqa: E402

GENG = "/opt/homebrew/bin/geng"
DIRECTG = "/opt/homebrew/bin/directg"


# --------------------------------------------------------------------------- #
#  weak connectivity + strong connectivity helpers on an arc list
# --------------------------------------------------------------------------- #

def weakly_connected_spanning(n, arc_idx_set, arcs):
    """Underlying-undirected connectivity touching ALL n vertices."""
    if not arc_idx_set:
        return False
    adj = [[] for _ in range(n)]
    touched = [False] * n
    for i in arc_idx_set:
        u, v = arcs[i]
        adj[u].append(v)
        adj[v].append(u)
        touched[u] = True
        touched[v] = True
    if not all(touched):
        return False
    # BFS from vertex 0
    seen = [False] * n
    stack = [0]
    seen[0] = True
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if not seen[y]:
                seen[y] = True
                stack.append(y)
    return all(seen)


def undirected_components(n, arc_idx_set, arcs):
    """Return list of vertex-sets = connected components of underlying graph
    induced by the arcs (isolated vertices each their own component)."""
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in arc_idx_set:
        u, v = arcs[i]
        union(u, v)
    comps = {}
    for v in range(n):
        comps.setdefault(find(v), set()).add(v)
    return list(comps.values())


def is_strong(n, arcs):
    """Exact strong-connectivity via the project's digraph backend."""
    D = Digraph.from_arcs(range(n), [(int(u), int(v)) for u, v in arcs])
    return D.is_strongly_connected()


# --------------------------------------------------------------------------- #
#  ESAD decision via ILP + lazy weak-connectivity cuts
# --------------------------------------------------------------------------- #

def decide_esad(n, arcs, max_iters=2000):
    """Return (found_bool, witness_or_None, iters).  found True => witness =
    (part1_idx_list, part2_idx_list), both balanced + weakly-connected-spanning.
    Exact: lazy connectivity cuts; returns False only when ILP proves no such
    assignment exists."""
    m = len(arcs)
    out_arcs = [[] for _ in range(n)]
    in_arcs = [[] for _ in range(n)]
    for i, (u, v) in enumerate(arcs):
        out_arcs[u].append(i)
        in_arcs[v].append(i)

    prob = pulp.LpProblem("ESAD", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x{i}", cat="Binary") for i in range(m)]
    prob += 0  # feasibility only

    # balance of part 1 at every vertex (=> part 2 balanced since D Eulerian)
    for v in range(n):
        prob += (pulp.lpSum(x[i] for i in out_arcs[v])
                 == pulp.lpSum(x[i] for i in in_arcs[v]))
    # both parts non-empty
    prob += pulp.lpSum(x) >= 1
    prob += pulp.lpSum(x) <= m - 1
    # spanning: each vertex has >=1 incident arc in EACH class.
    # incident arcs of v = out_arcs[v] + in_arcs[v]; part1 count and part2 count
    for v in range(n):
        inc = out_arcs[v] + in_arcs[v]
        prob += pulp.lpSum(x[i] for i in inc) >= 1            # >=1 in part1
        prob += pulp.lpSum((1 - x[i]) for i in inc) >= 1      # >=1 in part2

    solver = pulp.PULP_CBC_CMD(msg=0)

    for it in range(max_iters):
        status = prob.solve(solver)
        if pulp.LpStatus[status] != "Optimal":
            return False, None, it + 1
        sol = [int(round(x[i].value())) for i in range(m)]
        p1 = [i for i in range(m) if sol[i] == 1]
        p2 = [i for i in range(m) if sol[i] == 0]
        ok1 = weakly_connected_spanning(n, p1, arcs)
        ok2 = weakly_connected_spanning(n, p2, arcs)
        if ok1 and ok2:
            return True, (p1, p2), it + 1
        # add lazy connectivity cuts for whichever part is disconnected.
        if not ok1:
            comps = undirected_components(n, p1, arcs)
            # for each component S (proper), some part-1 arc must cross S
            for S in comps:
                if 0 < len(S) < n:
                    cross = [i for i in range(m)
                             if (arcs[i][0] in S) != (arcs[i][1] in S)]
                    # at least one crossing arc assigned to part1
                    prob += pulp.lpSum(x[i] for i in cross) >= 1
        if not ok2:
            comps = undirected_components(n, p2, arcs)
            for S in comps:
                if 0 < len(S) < n:
                    cross = [i for i in range(m)
                             if (arcs[i][0] in S) != (arcs[i][1] in S)]
                    prob += pulp.lpSum((1 - x[i]) for i in cross) >= 1
    return None, None, max_iters  # hit iteration cap (treat as UNKNOWN)


# --------------------------------------------------------------------------- #
#  universe generation (Eulerian multi-arc cell)  -- internal, single command
# --------------------------------------------------------------------------- #

def iter_eulerian_cell(n, M):
    """Yield (arcs, lam) for every Eulerian (in==out>=3) lambda>=3 multidigraph
    in the (n,M) cell. Drives geng/directg internally."""
    geng = subprocess.Popen([GENG, "-c", "-d1", str(n)], stdout=subprocess.PIPE)
    directg = subprocess.Popen([DIRECTG, "-T"], stdin=geng.stdout,
                               stdout=subprocess.PIPE, text=True)
    geng.stdout.close()
    for line in directg.stdout:
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        nv = int(toks[0]); ne = int(toks[1])
        nums = list(map(int, toks[2:]))
        base_arcs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        for mult in itertools.product(range(1, M + 1), repeat=ne):
            indeg = [0] * nv
            outdeg = [0] * nv
            for (u, v), k in zip(base_arcs, mult):
                outdeg[u] += k
                indeg[v] += k
            if any(indeg[v] != outdeg[v] or indeg[v] < 3 for v in range(nv)):
                continue
            arcs = []
            for (u, v), k in zip(base_arcs, mult):
                arcs.extend([(u, v)] * k)
            lam = oracle.arc_connectivity(nv, arcs)
            if lam < 3:
                continue
            yield arcs, lam
    directg.wait()
    geng.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--maxmult", type=int, default=3)
    ap.add_argument("--lambda-min", type=int, default=3,
                    help="only test instances with lambda >= this")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after this many instances tested (0 = all)")
    args = ap.parse_args()
    n, M = args.n, args.maxmult

    t0 = time.time()
    tested = 0
    by_lambda = {}          # lam -> {"tested","esad_yes","esad_no","unknown"}
    failures = []           # ESAD-failures (SAD-SAT but no balanced split)
    unknown = []
    sanity_C4sq = None

    for arcs, lam in iter_eulerian_cell(n, M):
        if lam < args.lambda_min:
            continue
        tested += 1
        d = by_lambda.setdefault(lam, {"tested": 0, "esad_yes": 0,
                                       "esad_no": 0, "unknown": 0})
        d["tested"] += 1
        found, wit, iters = decide_esad(n, arcs)
        if found is True:
            d["esad_yes"] += 1
            # cross-validate: both parts strong
            p1, p2 = wit
            a1 = [arcs[i] for i in p1]
            a2 = [arcs[i] for i in p2]
            s1 = is_strong(n, a1)
            s2 = is_strong(n, a2)
            if not (s1 and s2):
                # this would break the strong<=>balanced+connected lemma
                failures.append({
                    "kind": "ESAD_witness_not_strong",
                    "lambda": lam, "arcs": [list(a) for a in arcs],
                    "part1": [list(a) for a in a1],
                    "part2": [list(a) for a in a2],
                    "strong1": s1, "strong2": s2,
                })
        elif found is False:
            d["esad_no"] += 1
            # ESAD fails -- is ordinary SAD still SAT? (the KILL arm payload)
            r = oracle.check_construction(n, arcs, cross_check=True)
            failures.append({
                "kind": "no_ESAD",
                "lambda": lam, "arcs": [list(a) for a in arcs],
                "ordinary_sad": r["sad"], "cross_check": r.get("cross_check"),
                "iters": iters,
            })
        else:
            d["unknown"] += 1
            unknown.append({"lambda": lam, "arcs": [list(a) for a in arcs]})

        if args.limit and tested >= args.limit:
            break

    # c_emp = min lambda with zero ESAD failures (no_ESAD), over tested strata
    esad_fail_by_lambda = {}
    for f in failures:
        if f.get("kind") == "no_ESAD":
            esad_fail_by_lambda[f["lambda"]] = esad_fail_by_lambda.get(
                f["lambda"], 0) + 1
    c_emp = None
    for lam in sorted(by_lambda):
        if esad_fail_by_lambda.get(lam, 0) == 0:
            # require all higher strata also clean for a true threshold note
            pass
    # report c_emp as the smallest lambda such that this and all larger tested
    # strata had zero no_ESAD failures
    lams = sorted(by_lambda)
    for lam in lams:
        if all(esad_fail_by_lambda.get(l, 0) == 0 for l in lams if l >= lam):
            c_emp = lam
            break

    summary = {
        "n": n, "maxmult": M, "lambda_min": args.lambda_min,
        "instances_tested": tested,
        "by_lambda": by_lambda,
        "esad_failures_by_lambda": esad_fail_by_lambda,
        "n_no_ESAD": sum(1 for f in failures if f.get("kind") == "no_ESAD"),
        "n_witness_not_strong": sum(1 for f in failures
                                    if f.get("kind") == "ESAD_witness_not_strong"),
        "n_unknown": len(unknown),
        "c_emp": c_emp,
        "failures": failures[:50],
        "unknown_sample": unknown[:10],
        "elapsed_s": round(time.time() - t0, 2),
        "ESAD_holds_lambda_ge4": all(
            esad_fail_by_lambda.get(l, 0) == 0
            for l in by_lambda if l >= 4),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
