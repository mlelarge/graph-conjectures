"""all_heads_lamdo1_search.py -- D24 FALSIFICATION TARGET (branch-2 of O2b*).

The T4 cut-avoidance lemma (D24, cut_avoidance_check.py) is saved on ALL three
in-scope witnesses by the SAME mechanism: among the escaped AV_u heads, at least
one has lambda_DO(h, rho) >= 2 (head 6, on every witness), and that head's
admissible h->w path is the one that "passes" (D_O - A_O(P) keeps every O-vertex
reaching rho).  The lambda_DO = 1 head (head 7) FAILS on every path.

If there were an in-class strictly-rho-headless gateway in which EVERY escaped
head has lambda_DO(h, rho) = 1, then NO head passes, cut-avoidance is VIOLATED,
and T4 cannot close branch (2).  D24 named this exact gateway as the next
falsification target.  This script SEARCHES for it.

METHOD (perturbation of the relay_free witness, the largest checked-in one).
The relay_free host is (1,0)-near-split with oracle lambda = 3; its contraction
has the escaped-head lambda_DO profile {6: 2, 7: 1}.  We drive head 6 down to
lambda_DO = 1 by REMOVING D_O escape arcs of head 6 (its only D_O out-arcs are
6->5 and 6->7; the second escape is host arc (7,8)), then -- because a naive
deletion breaks near-split / arc-strength -- we try to REPAIR back to in-class
by adding compensating arcs from a pool that does NOT restore a second D_O
escape for either head (arcs into the cage, into the rho-tails, or rho->V2
back-arcs).  For every candidate we re-run the full in-class oracle gate
(near-split + host lambda == 3) AND recompute the contraction's per-head
lambda_DO.  A candidate that is IN-CLASS, strictly rho-headless, and has
ALL escaped heads at lambda_DO = 1 is a branch-2 WITNESS (refutes the cut-
avoidance lemma); if the entire search yields NONE, that is the empirical
signal that lambda_DO = 1 on ALL heads is incompatible with in-class
(supports T4 / closes the falsification attempt for this neighbourhood).

This is an EXISTENTIAL search: ONE in-class witness settles branch-2 negatively
(against the lemma); exhaustion over this engineered neighbourhood is biased
SUPPORT only, reported as such.
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from itertools import combinations

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import networkx as nx  # noqa: E402
import oracle  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.near_split import is_one_zero_near_split  # noqa: E402
from relay_free_witness import host_arcs  # noqa: E402

RELABEL = {0: 0, 1: 0, 2: 1}
RELABEL.update({v: v - 1 for v in range(3, 15)})


def contract(host):
    out = []
    for x, y in host:
        if (x, y) == (0, 1):
            continue
        rx, ry = RELABEL[x], RELABEL[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def head_lamdo_profile(host):
    """Return (in_class, contract_lambda, rho_headless, lamdo dict, cage, O).

    in_class := host is (1,0)-near-split with V1={0,1,2} and oracle host
    lambda == 3.  lamdo maps each escaped AV_u head in O to lambda_DO(h, rho).
    """
    host = [e for e in host if e[0] != e[1]]
    if len(host) != len(set(host)):
        return None  # not simple
    ns, _why = is_one_zero_near_split(
        Digraph.from_arcs(range(15), host), [0, 1, 2], list(range(3, 15)))
    lam = oracle.arc_connectivity(15, host)
    in_class = ns and lam == 3

    arcs = contract(host)
    n, root, u = 14, 0, 1
    mult = Counter(arcs)
    lamb = oracle.arc_connectivity(n, arcs)
    rho_headless = (u, root) not in mult

    g = nx.MultiDiGraph()
    g.add_nodes_from(range(n))
    g.add_edges_from(arcs)
    wo = g.copy()
    wo.remove_node(u)
    cage = {u} | {x for x in range(n)
                  if x not in (root, u) and not nx.has_path(wo, x, root)}
    w = 11
    red = g.copy()
    red.remove_nodes_from(cage | {w})
    trapped = {z for z in range(n) if z not in cage | {w} and z != root
               and not nx.has_path(red, z, root)}
    Xst = cage | {w} | trapped
    O = set(range(n)) - Xst - {root}
    heads = sorted(z for x, z in mult if x == u and z != 5)

    def lam_do(h):
        cap = nx.DiGraph()
        for (x, y), m in mult.items():
            if x in O and (y in O or y == root):
                cap.add_edge(x, y, capacity=m)
        if not nx.has_path(cap, h, root):
            return 0
        return int(nx.maximum_flow_value(cap, h, root))

    lds = {h: lam_do(h) for h in heads if h in O}
    return dict(in_class=in_class, host_lambda=lam, near_split=ns,
                contract_lambda=lamb, rho_headless=rho_headless,
                lamdo=lds, cage=sorted(cage), O=sorted(O))


def main():
    base = host_arcs()
    base_set = set(base)

    # The D_O escape arcs of head 6 (host label 7): host arc (7,8) is the
    # contraction arc 6->7 that gives head 6 its SECOND escape.  Removing it
    # forces lamdo(6)=1 (verified in the perturbation probe).  We also try
    # removing other forward escapes head 6/7 use to leave their cut side.
    head6_escapes = [(7, 8)]            # contraction 6->7
    # generic forward arcs out of the head layer into the L-layer that feed
    # alternative D_O routes (heads 7,8 host = 6,7 contraction internal)
    layer_feeds = [(6, 9), (6, 10), (6, 11)]  # host v->L (6 is host v)

    # repair pool: arcs that restore arc-strength / near-split WITHOUT giving
    # any escaped head a second D_O escape.  Candidates: rho-tail back-arcs,
    # cage in-arcs from outside, rho->V2 arcs, and R<->R / R->head arcs.
    cage = (3, 4, 5)
    rho_tails = (12, 13, 14)
    heads_h = (6, 7, 8)
    layer = (9, 10, 11)
    repair_pool = []
    repair_pool += [(r, c) for r in rho_tails for c in cage]      # R->cage
    repair_pool += [(0, x) for x in layer + rho_tails]            # rho(p)->V2
    repair_pool += [(1, x) for x in layer + rho_tails]            # rho(q)->V2
    repair_pool += [(r, h) for r in rho_tails for h in heads_h]   # R->heads
    repair_pool += [(x, 0) for x in rho_tails]                    # ->rho(p)
    repair_pool += [(x, 1) for x in rho_tails]                    # ->rho(q)
    repair_pool = [e for e in dict.fromkeys(repair_pool)
                   if e not in base_set and e[0] != e[1]]

    base_prof = head_lamdo_profile(base)
    print("=== baseline relay_free ===")
    print(f"  {base_prof}")

    # 1) single + double deletions that may push BOTH heads to lamdo=1
    del_pool = head6_escapes + layer_feeds
    candidates = []
    for k in (1, 2):
        for combo in combinations(del_pool, k):
            h = [e for e in base if e not in set(combo)]
            candidates.append(("del" + str(combo), h))

    # collect deletion variants that achieve ALL_LAMDO1 (regardless of in_class)
    all1_variants = []
    print("\n=== deletion sweep (drive all heads to lamdo=1) ===")
    for tag, h in candidates:
        prof = head_lamdo_profile(h)
        if prof is None:
            continue
        lds = prof["lamdo"]
        all1 = len(lds) > 0 and all(v == 1 for v in lds.values())
        if all1:
            all1_variants.append((tag, h, prof))
        if all1 or prof["in_class"]:
            print(f"  {tag}: in_class={prof['in_class']} "
                  f"lamdo={prof['lamdo']} all1={all1} "
                  f"ns={prof['near_split']} hlam={prof['host_lambda']}")

    # 2) for each all-lamdo1 deletion variant that is NOT in-class, try single
    #    and double repair-arc additions to restore in-class while preserving
    #    ALL_LAMDO1 and strict rho-headlessness.
    print("\n=== repair search over all-lamdo1 variants ===")
    found = None
    n_repair_tested = 0
    for tag, h, prof in all1_variants:
        if prof["in_class"]:
            found = (tag, h, prof)
            break
        hset = set(h)
        local_pool = [e for e in repair_pool if e not in hset]
        repairs = [()] + [(e,) for e in local_pool]
        repairs += list(combinations(local_pool, 2))
        for rep in repairs:
            n_repair_tested += 1
            h2 = h + list(rep)
            if len(h2) != len(set(h2)):
                continue
            p2 = head_lamdo_profile(h2)
            if p2 is None:
                continue
            lds = p2["lamdo"]
            all1 = len(lds) > 0 and all(v == 1 for v in lds.values())
            if (p2["in_class"] and all1 and p2["rho_headless"]):
                found = (tag + "+rep" + str(rep), h2, p2)
                break
        if found:
            break

    print(f"  repair candidates tested: {n_repair_tested}")
    print("\n=== VERDICT ===")
    print(f"all-lamdo1 deletion variants found: {len(all1_variants)} "
          f"(none in-class on their own: "
          f"{not any(p['in_class'] for _, _, p in all1_variants)})")
    if found:
        tag, h, prof = found
        print(f"BRANCH-2 WITNESS FOUND: {tag}")
        print(f"  profile={prof}")
        print("  => cut-avoidance lemma REFUTED (all escaped heads lamdo=1, "
              "in-class)")
    else:
        print("NO in-class all-lamdo1 gateway found in this neighbourhood.")
        print("  Every way to force ALL escaped heads to lambda_DO=1 (deletion "
              "+ up to 2 repair arcs) either breaks near-split or drops host "
              "lambda below 3.")
        print("  => SUPPORTS the cut-avoidance lemma (lamdo>=2 on some head is "
              "forced in-class) for this neighbourhood; biased-sample support, "
              "NOT a proof.")


if __name__ == "__main__":
    main()
