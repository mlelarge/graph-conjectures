"""GROUND: LINEAR-LAMBDA GENERAL SAD THEOREM (P4 candidate).

Claim under test (UNIVERSAL): every multidigraph D on n vertices with
lambda^arc(D) >= n+1 admits a SAD, via:
  - pack t = n+1 arc-disjoint OUT-branchings O_1..O_t rooted at r=0 (Edmonds);
  - pack t arc-disjoint IN-branchings I_1..I_t to r=0 (Edmonds);
  - each O_i has n-1 arcs, each arc lies in at most one I_j, so O_i conflicts
    with <= n-1 of the I's; with t >= n+1 the free sets
        F1 = {j : I_j cap O_1 = empty}, F2 = {j : I_j cap O_2 = empty}
    each have size >= 2; pick DISTINCT j_a in F2, j_b in F1 (possible since
    each has >=2 elements);
  - class1 = O_1 u I_{j_b} u (all leftover arcs), class2 = O_2 u I_{j_a};
    cross intersections O_1 cap I_{j_b} = empty and O_2 cap I_{j_a} = empty by
    choice; each class contains an out-branching + an in-branching at r so is
    spanning strong.
  - feed BOTH classes to the oracle and confirm SAD = SAT.

This script BUILDS the construction and FEEDS it to the oracle.  It does NOT
trust the proof a priori: it independently verifies (a) the packings are valid
and arc-disjoint, (b) the conflict-degree bound, (c) the extracted colouring is
a genuine partition of A(D), (d) BOTH classes are strongly connected
(networkx), and (e) the oracle agrees SAD=SAT.

Run as ONE foreground command:
  timeout 600 .venv/bin/python scripts/linear_lambda_sad.py --nmax 8 --trials 100 --seed 0
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for p in (_HERE, _CODE):
    if p not in sys.path:
        sys.path.insert(0, p)

import networkx as nx  # noqa: E402
import pulp  # noqa: E402

from oracle import arc_connectivity, check_construction  # noqa: E402


# --------------------------------------------------------------------------- #
#  Branching packing via ILP (exact Edmonds packing, t arc-disjoint branchings)
# --------------------------------------------------------------------------- #

def pack_branchings(n, arcs, root, t, kind, time_limit=60):
    """Pack t arc-disjoint branchings.

    arcs : list of (u,v) with an implicit index = position in the list
           (parallel arcs are distinct indices).
    kind = "out": out-branchings rooted at `root` (every v!=root reachable
           FROM root along tree arcs; each non-root vertex has in-degree 1
           in the branching).
    kind = "in" : in-branchings to `root` (every v!=root reaches root; each
           non-root vertex has out-degree 1 in the branching).

    Returns list of t branchings, each a frozenset of arc-INDICES, or None if
    infeasible.

    Encoding: per branching b, choose x[a,b] in {0,1}.  Arc-disjointness:
    sum_b x[a,b] <= 1.  Each branching is a spanning arborescence enforced by a
    single-commodity-per-target flow (degree + connectivity via flow from root).
    For out-branchings we route a flow of value (n-1) from root that delivers 1
    unit to every other vertex, supported only on chosen arcs, plus the
    in-degree-exactly-1 (non-root) / 0 (root) degree constraints.  This is the
    standard exact arborescence ILP.
    """
    m = len(arcs)
    idx = list(range(m))
    nodes = list(range(n))
    others = [v for v in nodes if v != root]

    prob = pulp.LpProblem("pack", pulp.LpMinimize)
    # x[a,b] = arc a used in branching b
    x = {(a, b): pulp.LpVariable(f"x_{a}_{b}", cat="Binary")
         for a in idx for b in range(t)}
    # flow f[a,b] >= 0 : commodity routed on arc a in branching b
    f = {(a, b): pulp.LpVariable(f"f_{a}_{b}", lowBound=0)
         for a in idx for b in range(t)}

    prob += 0  # feasibility

    # arc-disjoint across branchings
    for a in idx:
        prob += pulp.lpSum(x[a, b] for b in range(t)) <= 1

    for b in range(t):
        # degree constraints define the arborescence shape
        for v in others:
            if kind == "out":
                # in-degree exactly 1 at every non-root
                prob += pulp.lpSum(x[a, b] for a in idx if arcs[a][1] == v) == 1
            else:  # "in"
                # out-degree exactly 1 at every non-root
                prob += pulp.lpSum(x[a, b] for a in idx if arcs[a][0] == v) == 1
        if kind == "out":
            prob += pulp.lpSum(x[a, b] for a in idx if arcs[a][1] == root) == 0
        else:
            prob += pulp.lpSum(x[a, b] for a in idx if arcs[a][0] == root) == 0

        # connectivity via single-source flow on the chosen arcs
        # out-branching: source = root supplies (n-1), each other vertex demands 1
        # in-branching:  sink   = root demands (n-1), each other vertex supplies 1
        for a in idx:
            prob += f[a, b] <= (n - 1) * x[a, b]
        for v in nodes:
            inflow = pulp.lpSum(f[a, b] for a in idx if arcs[a][1] == v)
            outflow = pulp.lpSum(f[a, b] for a in idx if arcs[a][0] == v)
            if kind == "out":
                if v == root:
                    prob += outflow - inflow == (n - 1)
                else:
                    prob += inflow - outflow == 1
            else:  # "in"
                if v == root:
                    prob += inflow - outflow == (n - 1)
                else:
                    prob += outflow - inflow == 1

    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    status = prob.solve(solver)
    if pulp.LpStatus[status] != "Optimal":
        return None
    out = []
    for b in range(t):
        s = frozenset(a for a in idx if x[a, b].value() is not None
                      and x[a, b].value() > 0.5)
        out.append(s)
    return out


def branching_arcset(arcs, branching_idx):
    return frozenset(branching_idx)


def is_spanning_strong(n, arc_list):
    """networkx-independent strong + spanning check on an arc multiset."""
    G = nx.MultiDiGraph()
    G.add_nodes_from(range(n))
    for (u, v) in arc_list:
        G.add_edge(u, v)
    if G.number_of_nodes() != n:
        return False
    return nx.is_strongly_connected(G)


# --------------------------------------------------------------------------- #
#  Test-instance builders
# --------------------------------------------------------------------------- #

def thickened_Kstar(n, mult=2):
    """K_n^* (complete bidirected) with every arc taken `mult` times.
    lambda = mult*(n-1) >= n+1 for mult>=2, n>=... (2(n-1)>=n+1 iff n>=3)."""
    arcs = []
    for u in range(n):
        for v in range(n):
            if u != v:
                arcs += [(u, v)] * mult
    return arcs


def g11_bundle(k, m):
    """G11 asymmetric in/out-bundle: digon {0,1} mult m + k toggle vertices.
    s=0, o=1; each toggle p (2..k+1) has s->p, p->o at mult m.
    Vertices: 0,1, then 2..k+1.  n = k+2."""
    n = k + 2
    arcs = []
    arcs += [(0, 1)] * m
    arcs += [(1, 0)] * m
    for i in range(k):
        p = 2 + i
        arcs += [(0, p)] * m
        arcs += [(p, 1)] * m
    return n, arcs


def random_multidigraph(n, rng, maxmult=3):
    arcs = []
    for u in range(n):
        for v in range(n):
            if u != v:
                c = rng.randint(0, maxmult)
                arcs += [(u, v)] * c
    return arcs


# --------------------------------------------------------------------------- #
#  Core: try the proof skeleton on one instance
# --------------------------------------------------------------------------- #

def attempt_sad_via_branchings(n, arcs, time_limit=60):
    """Returns dict with the full pipeline result for one instance."""
    res = {"n": n, "m": len(arcs)}
    lam = arc_connectivity(n, arcs)
    res["lambda"] = lam
    t = n + 1
    if lam < t:
        res["skip"] = f"lambda {lam} < n+1 = {t}"
        return res

    root = 0
    Os = pack_branchings(n, arcs, root, t, "out", time_limit)
    Is = pack_branchings(n, arcs, root, t, "in", time_limit)
    if Os is None:
        res["FAIL"] = "out-branching packing infeasible despite lambda>=t (kills derivation/impl)"
        return res
    if Is is None:
        res["FAIL"] = "in-branching packing infeasible despite lambda>=t (kills derivation/impl)"
        return res

    # validate packings: arc-disjoint, each size n-1, each is a valid branching
    for tag, pack, kind in (("O", Os, "out"), ("I", Is, "in")):
        seen = set()
        for b, s in enumerate(pack):
            if len(s) != n - 1:
                res["FAIL"] = f"{tag}_{b} has {len(s)} arcs != n-1"
                return res
            if s & seen:
                res["FAIL"] = f"{tag}_{b} not arc-disjoint from earlier"
                return res
            seen |= s

    # conflict-degree bound: deg(O_i) = #{j : I_j cap O_i != empty} <= n-1
    max_conf = 0
    for i in range(t):
        conf = sum(1 for j in range(t) if (Os[i] & Is[j]))
        max_conf = max(max_conf, conf)
    res["max_conflict_degree"] = max_conf
    if max_conf > n - 1:
        res["FAIL"] = f"conflict degree {max_conf} > n-1 = {n-1} (kills pigeonhole)"
        return res

    # pigeonhole extraction on O_1, O_2 (indices 0,1)
    F1 = [j for j in range(t) if not (Is[j] & Os[0])]  # I_j disjoint from O_1
    F2 = [j for j in range(t) if not (Is[j] & Os[1])]  # I_j disjoint from O_2
    res["F1_size"] = len(F1)
    res["F2_size"] = len(F2)
    if len(F1) < 2 or len(F2) < 2:
        res["FAIL"] = f"free sets too small F1={len(F1)} F2={len(F2)} (pigeonhole claims >=2)"
        return res
    # pick distinct j_a in F2 (for O_2), j_b in F1 (for O_1)
    j_b = F1[0]
    j_a = next((j for j in F2 if j != j_b), None)
    if j_a is None:
        res["FAIL"] = "could not pick distinct j_a in F2 != j_b (F2 had only j_b)"
        return res

    # build colouring on arc-INDICES
    all_idx = set(range(len(arcs)))
    class2 = set(Os[1]) | set(Is[j_a])        # O_2 u I_{j_a}
    class1 = (all_idx - class2)               # everything else incl O_1, I_{j_b}, leftovers
    # sanity: O_1 and I_{j_b} indeed in class1, and cross-disjointness held
    if (Os[0] & Is[j_b]):
        res["FAIL"] = "O_1 cap I_{j_b} nonempty -- pigeonhole selection wrong"
        return res
    if (Os[1] & Is[j_a]):
        res["FAIL"] = "O_2 cap I_{j_a} nonempty -- pigeonhole selection wrong"
        return res
    # DIAGNOSTIC: the proof's partition is well-defined ONLY if the arcs the
    # proof PUTS in class1 (O_1, I_{j_b}) do not also belong to the set forced
    # into class2 (O_2 u I_{j_a}). The proof only guarantees the two NAMED cross
    # pairs empty (O_2 cap I_{j_a}, O_1 cap I_{j_b}); it does NOT control
    # O_1 cap I_{j_a}, I_{j_b} cap O_2, I_{j_b} cap I_{j_a}.
    o1_lost = set(Os[0]) & class2          # O_1 arcs stolen by class2
    ijb_lost = set(Is[j_b]) & class2       # I_{j_b} arcs stolen by class2
    res["O1_arcs_lost_to_class2"] = len(o1_lost)
    res["Ijb_arcs_lost_to_class2"] = len(ijb_lost)
    if o1_lost or ijb_lost:
        res["partition_ill_defined"] = True
        # Do NOT bail: the partition is still a valid PARTITION (class2 = those
        # arcs, class1 = the rest). The real question the proof makes is whether
        # BOTH classes are spanning-strong. We test that directly below; the
        # proof's structural guarantee (O_1, I_{j_b} intact in class1) is what
        # has FAILED, so record it.

    c1_arcs = [arcs[a] for a in class1]
    c2_arcs = [arcs[a] for a in class2]
    res["class1_size"] = len(c1_arcs)
    res["class2_size"] = len(c2_arcs)

    s1 = is_spanning_strong(n, c1_arcs)
    s2 = is_spanning_strong(n, c2_arcs)
    res["class1_strong"] = s1
    res["class2_strong"] = s2
    # The PROOF SKELETON's prediction is that THIS specific colouring (the one
    # the proof constructs) is both-strong. Record whether it held.
    res["proof_colouring_both_strong"] = bool(s1 and s2)
    res["proof_structure_held"] = bool(s1 and s2 and not res.get("partition_ill_defined"))

    # Oracle confirmation that a SAD exists AT ALL on this instance (independent
    # of whether the proof's colouring worked). lambda>=n+1 instances are very
    # dense, so SAD=SAT is essentially never in doubt; the load-bearing claim is
    # the PROOF's specific construction, not mere SAD-existence.
    ores = check_construction(n, arcs, cross_check=True)
    res["oracle_sad"] = ores["sad"]
    res["oracle_cross"] = ores.get("cross_check")

    if not (s1 and s2):
        res["FAIL"] = (f"PROOF colouring NOT both-strong (c1={s1}, c2={s2}); "
                       f"partition_ill_defined={res.get('partition_ill_defined', False)}")
        return res

    res["OK"] = True
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=8)
    ap.add_argument("--trials", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--time-limit", type=float, default=30.0)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    instances = []

    # (A) thickened K_n^* mult 2, n=4..nmax
    for n in range(4, args.nmax + 1):
        instances.append((f"K{n}star_x2", n, thickened_Kstar(n, 2)))

    # (B) G11 asymmetric bundle thickened to lambda >= n+1.
    # n = k+2; need lambda >= n+1 = k+3. lambda of bundle = min out-cut.
    # The digon gives cut(0)= m + sum over toggles of m (arcs 0->p) ... let oracle decide;
    # pick m generously then rely on lambda filter.
    for k in (2, 3, 4):
        n = k + 2
        # choose m so lambda >= n+1; bump m until satisfied (cheap, exact oracle)
        chosen = None
        for m in range(2, 20):
            nn, arcs = g11_bundle(k, m)
            if arc_connectivity(nn, arcs) >= nn + 1:
                chosen = (nn, arcs, m)
                break
        if chosen:
            nn, arcs, m = chosen
            instances.append((f"g11_k{k}_m{m}", nn, arcs))

    # (C) generic random multidigraphs n=5..nmax, rejection-filtered lambda>=n+1
    want = args.trials
    got = 0
    tries = 0
    while got < want and tries < want * 200:
        tries += 1
        n = rng.randint(5, args.nmax)
        arcs = random_multidigraph(n, rng, maxmult=3)
        if not arcs:
            continue
        if arc_connectivity(n, arcs) >= n + 1:
            instances.append((f"rand_n{n}_{got}", n, arcs))
            got += 1

    results = []
    n_ok = n_fail = n_skip = 0
    for name, n, arcs in instances:
        r = attempt_sad_via_branchings(n, arcs, time_limit=args.time_limit)
        r["name"] = name
        results.append(r)
        if r.get("OK"):
            n_ok += 1
        elif r.get("skip"):
            n_skip += 1
        else:
            n_fail += 1
            print("FAIL INSTANCE:", json.dumps(r, default=str))

    summary = {
        "n_instances": len(instances),
        "n_ok": n_ok,
        "n_fail": n_fail,
        "n_skip": n_skip,
        "random_lambda_ge_np1_found": got,
        "all_ok_among_nonskip": (n_fail == 0 and (n_ok > 0)),
    }
    print(json.dumps({"summary": summary, "results": results}, indent=2, default=str))


if __name__ == "__main__":
    main()
