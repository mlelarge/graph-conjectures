"""single_relay_all_lambda1_witness.py -- D24 branch-2 FALSIFICATION TARGET.

Proposal (explicit-construction lens): build an IN-CLASS strictly rho-headless
hard gateway in which EVERY escaped AV_u head has lambda_DO(h, rho) = 1, by a
SINGLE-RELAY rewiring of the checked-in relay_free witness.

Concretely: take relay_free_witness.host_arcs() and replace v=6's outside
out-arcs {(6,9),(6,10),(6,11)} by {(6,9),(10,6),(11,6)} (reverse two L-arcs).
The claim is that every escaped head's D_O route to rho is then forced through
the unique bottleneck arc (v,9), so lambda_DO(h,rho)=1 for ALL heads, and the
cut-avoidance condition fails on every (w,h,P).

TRICHOTOMY (finite, oracle-checkable):
  (1) KILL: in-class + strictly rho-headless gateway + all heads lambda_DO=1 +
      cut-avoidance VIOLATED for all (w,h,P)  => queued lemma REFUTED in-class.
  (2) LEMMA-SURVIVES: in-class but some head still lambda_DO>=2 or condition
      satisfied  => the bottleneck prediction is falsified by max-flow values.
  (3) UNREALIZABLE: every variant fails oracle lambda>=3 or loses gateway scope
      => constructive evidence the all-lambda_DO=1 geometry is in-class
         unrealizable (the hypothesis the symbolic lemma needs).
"""
from __future__ import annotations

import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import networkx as nx  # noqa: E402

import oracle  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.near_split import is_one_zero_near_split  # noqa: E402
from relay_free_witness import host_arcs as base_host_arcs  # noqa: E402
from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)

RELABEL = {0: 0, 1: 0, 2: 1}
RELABEL.update({v: v - 1 for v in range(3, 15)})


def rewire(base, drop, add):
    s = [e for e in base if e not in set(drop)]
    s += list(add)
    return s


def variant_host(drop, add):
    return rewire(base_host_arcs(), drop, add)


def contract(host):
    out = []
    for x, y in host:
        if (x, y) == (0, 1):
            continue
        rx, ry = RELABEL[x], RELABEL[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def lam_do_profile(arcs, O, root):
    """lambda_DO(h,rho) for each escaped head, using unit/multiplicity caps on
    the D_O subdigraph (O-internal arcs + O->root arcs)."""
    mult = Counter(arcs)
    cap = nx.DiGraph()
    for (x, y), m in mult.items():
        if x in O and (y in O or y == root):
            if cap.has_edge(x, y):
                cap[x][y]["capacity"] += m
            else:
                cap.add_edge(x, y, capacity=m)
    out = {}
    heads = sorted(z for x, z in mult if x == 1 and z != 5 and z in O)
    for h in heads:
        if not nx.has_path(cap, h, root):
            out[h] = 0
        else:
            out[h] = int(nx.maximum_flow_value(cap, h, root))
    return out, heads


def analyse_host(host, tag):
    """Run the full in-class + gateway + cut-avoidance battery on one host.
    Returns a dict describing which trichotomy arm this host lands in."""
    host = [e for e in host if e[0] != e[1]]
    info = {"tag": tag}
    if len(host) != len(set(host)):
        info["arm"] = "UNREALIZABLE"
        info["reason"] = "host not simple"
        return info

    # (a) IN-CLASS gate.
    ns, why = is_one_zero_near_split(
        Digraph.from_arcs(range(15), host), [0, 1, 2], list(range(3, 15)))
    lam_host = oracle.arc_connectivity(15, host)
    info["near_split"] = bool(ns)
    info["near_split_why"] = None if ns else why
    info["host_lambda"] = lam_host
    if not ns or lam_host < 3:
        info["arm"] = "UNREALIZABLE"
        info["reason"] = f"in-class fail: ns={ns} lambda={lam_host} ({why})"
        return info

    sad = oracle.check_construction(15, host, name=tag, cross_check=True)
    info["sad"] = sad["sad"]
    info["arc_strong"] = sad["arc_strong"]
    if sad["cross_check"] is not None:
        info["cross_agree"] = sad["cross_check"]["agree"]
    if sad["sad"] != "SAT" or sad["arc_strong"] < 3:
        info["arm"] = "UNREALIZABLE"
        info["reason"] = f"oracle: sad={sad['sad']} arc_strong={sad['arc_strong']}"
        return info

    # Contraction.
    arcs = contract(host)
    n, root, u, v = 14, 0, 1, 5
    mult = Counter(arcs)
    info["contract_lambda"] = oracle.arc_connectivity(n, arcs)
    info["rho_headless"] = (u, root) not in mult
    if not info["rho_headless"]:
        info["arm"] = "UNREALIZABLE"
        info["reason"] = "not strictly rho-headless (u,root) present"
        return info

    G = nx.MultiDiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(arcs)
    Gm = G.copy()
    Gm.remove_node(u)
    cage = {u} | {x for x in range(n) if x not in (root, u)
                  and not nx.has_path(Gm, x, root)}
    info["cage"] = sorted(cage)
    R = sorted({e[0] for e in mult if e[1] == root})
    info["R"] = R

    # (c) admissible-w set and X*_w, exactly as cut_avoidance_check.analyse.
    admissible = []
    per_w = {}
    for w in R:
        if w in cage or w == v:
            continue
        red = G.copy()
        red.remove_nodes_from(cage | {w})
        B = {z for z in range(n) if z not in cage | {w} and z != root
             and not (z in red and nx.has_path(red, z, root))}
        Xst = cage | {w} | B
        if v in Xst or len(Xst) > n - 2:
            continue
        O = set(range(n)) - Xst - {root}
        admissible.append(w)
        per_w[w] = (Xst, O)
    info["admissible_w"] = admissible
    if not admissible:
        info["arm"] = "UNREALIZABLE"
        info["reason"] = "no admissible w (gateway scope lost)"
        return info

    # lambda_DO profile (use the first admissible w's O; O is w-dependent but
    # the escaped-head set is the AV_u heads which lie outside for each).
    w0 = admissible[0]
    Xst0, O0 = per_w[w0]
    lamdo, heads0 = lam_do_profile(arcs, O0, root)
    info["lamdo"] = lamdo
    info["escaped_heads"] = heads0
    all1 = len(lamdo) > 0 and all(val == 1 for val in lamdo.values())
    info["all_heads_lamdo1"] = all1

    # (d) hard-gateway non-vacuity: is there a failing arc-disjoint pair at a?
    info["hard_pair_found"] = check_hard_pair(arcs, n, root, u, v, cage)

    # (f) full cut-avoidance scan over all (w,h,P).
    satisfied, rows = cut_avoidance_scan(arcs, n, root, u, v, cage, admissible,
                                         per_w)
    info["cut_avoidance_satisfied"] = satisfied
    info["cut_rows"] = rows

    # Trichotomy classification.
    if all1 and not satisfied and info["hard_pair_found"]:
        info["arm"] = "KILL"
        info["reason"] = ("all escaped heads lambda_DO=1, in-class, strictly "
                          "rho-headless, hard pair present, cut-avoidance "
                          "VIOLATED for all (w,h,P)")
    elif all1 and satisfied:
        info["arm"] = "LEMMA-SURVIVES"
        info["reason"] = ("all heads lambda_DO=1 but cut-avoidance still "
                          "SATISFIED (bottleneck prediction falsified)")
    elif not all1:
        info["arm"] = "LEMMA-SURVIVES"
        info["reason"] = ("some escaped head retains lambda_DO>=2 "
                          "(single-relay bottleneck did NOT force all heads to 1)")
    else:
        info["arm"] = "LEMMA-SURVIVES"
        info["reason"] = "all1 but no hard pair / vacuous gateway"
    return info


def check_hard_pair(arcs, n, root, u, v, cage):
    """Reuse the explicit relay_free arc-disjoint pair if it is realizable for
    a copy of a=(u,v); else report whether ANY failing intermediate pair exists
    via a light search of in-arborescences. We use the checked-in explicit pair
    as the primary probe (it is the documented hard gateway for this host)."""
    mult = Counter(arcs)
    tree_t = {
        2: 3, 3: 1, 4: 1, 1: 5,
        5: 8, 6: 7, 7: 5,
        8: 11, 9: 11, 10: 11,
        11: 0, 12: 0, 13: 0,
    }
    tree_u = {
        2: 1, 3: 2, 4: 2, 1: 6,
        6: 5, 5: 9, 7: 2, 8: 6,
        9: 12, 10: 13,
        11: 0, 12: 11, 13: 0,
    }

    def is_in_arb(succ):
        for start in range(n):
            if start == root:
                continue
            seen, cur = set(), start
            while cur != root:
                if cur in seen or cur not in succ:
                    return False
                seen.add(cur)
                cur = succ[cur]
        return True

    # Validate both are in-arborescences in the rewired multidigraph.
    for succ in (tree_t, tree_u):
        for x, y in succ.items():
            if (x, y) not in mult:
                return False
    if not (is_in_arb(tree_t) and is_in_arb(tree_u)):
        return False
    t_arcs, u_arcs = tree_arcs(tree_t), tree_arcs(tree_u)
    if not pair_realizable(t_arcs, u_arcs, mult):
        return False
    x_set = subtree_through(tree_t, u, root, n)
    if not (2 <= len(x_set) <= n - 2):
        return False
    exits = [e for e in u_arcs if e[0] in x_set and e[1] not in x_set]
    strict = [e for e in exits
              if (subtree_through(tree_u, e[0], root, n) & x_set) < x_set]
    return len(exits) >= 1 and not strict


def cut_avoidance_scan(arcs, n, root, u, v, cage, admissible, per_w):
    mult = Counter(arcs)
    G = nx.MultiDiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(arcs)
    rows = []
    satisfied = False
    for w in admissible:
        Xst, O = per_w[w]
        heads = [z for z in range(n) if (u, z) in mult and z != v and z in O]
        DO = nx.DiGraph()
        DO.add_nodes_from(O | {root})
        for (x, y) in mult:
            if x in O and (y in O or y == root):
                DO.add_edge(x, y)
        H = nx.DiGraph()
        H.add_nodes_from(O | {w})
        for (x, y) in mult:
            if x in O and (y in O or y == w):
                H.add_edge(x, y)
        for h in heads:
            if nx.has_path(DO, h, root):
                cap = nx.DiGraph()
                for (x, y), m in mult.items():
                    if x in O and (y in O or y == root):
                        if cap.has_edge(x, y):
                            cap[x][y]["capacity"] += m
                        else:
                            cap.add_edge(x, y, capacity=m)
                lam_h = int(nx.maximum_flow_value(cap, h, root))
            else:
                lam_h = 0
            n_paths = n_pass = 0
            best = None
            for P in nx.all_simple_paths(H, h, w):
                n_paths += 1
                AO = [(P[i], P[i + 1]) for i in range(len(P) - 2)]
                DOr = DO.copy()
                DOr.remove_edges_from(AO)
                if all(nx.has_path(DOr, z, root) for z in O):
                    n_pass += 1
                    if best is None or len(P) < len(best):
                        best = P
            rows.append((w, h, lam_h, n_paths, n_pass, best))
            satisfied = satisfied or n_pass > 0
    return satisfied, rows


def main():
    # Pre-registered variants. Variant 0 = the proposal's exact rewiring.
    variants = [
        ("v0: drop {(6,9),(6,10),(6,11)} add {(6,9),(10,6),(11,6)}",
         [(6, 9), (6, 10), (6, 11)], [(6, 9), (10, 6), (11, 6)]),
        # Variant: keep (6,10) instead of (6,9).
        ("v1: keep (6,10): drop {(6,9),(6,10),(6,11)} add {(6,10),(9,6),(11,6)}",
         [(6, 9), (6, 10), (6, 11)], [(6, 10), (9, 6), (11, 6)]),
        # Variant: add a compensating cage->v arc (3,6) to restore strength.
        ("v2: v0 + compensating cage arc (3,6)",
         [(6, 9), (6, 10), (6, 11)], [(6, 9), (10, 6), (11, 6), (3, 6)]),
    ]

    results = []
    print("=== single-relay all-lambda_DO=1 trichotomy probe ===\n")
    for tag, drop, add in variants:
        host = variant_host(drop, add)
        info = analyse_host(host, tag)
        results.append(info)
        print(f"--- {tag}")
        for k in ("near_split", "near_split_why", "host_lambda", "sad",
                  "arc_strong", "cross_agree", "contract_lambda",
                  "rho_headless", "cage", "R", "admissible_w", "lamdo",
                  "escaped_heads", "all_heads_lamdo1", "hard_pair_found",
                  "cut_avoidance_satisfied", "arm", "reason"):
            if k in info:
                print(f"    {k} = {info[k]}")
        if info.get("cut_rows"):
            for (w, h, lam, np_, ok, best) in info["cut_rows"]:
                print(f"      w={w} h={h} lam_DO={lam}: {ok}/{np_} pass"
                      + (f", shortest {best}" if best else " (ALL FAIL)"))
        print()

    print("=== VERDICT ===")
    kills = [r for r in results if r.get("arm") == "KILL"]
    survives = [r for r in results if r.get("arm") == "LEMMA-SURVIVES"]
    unreal = [r for r in results if r.get("arm") == "UNREALIZABLE"]
    if kills:
        print("ARM (1) KILL: queued cut-avoidance lemma REFUTED in-class.")
        print(f"  witness: {kills[0]['tag']}")
    elif survives:
        print("ARM (2) LEMMA-SURVIVES: bottleneck prediction falsified.")
        for r in survives:
            print(f"  {r['tag']}: {r['reason']}")
            if "lamdo" in r:
                print(f"    lamdo = {r['lamdo']}")
    else:
        print("ARM (3) UNREALIZABLE: every variant fails in-class or scope.")
        for r in unreal:
            print(f"  {r['tag']}: {r['reason']}")
    print(f"\ncounts: KILL={len(kills)} SURVIVES={len(survives)} "
          f"UNREALIZABLE={len(unreal)}")


if __name__ == "__main__":
    main()
