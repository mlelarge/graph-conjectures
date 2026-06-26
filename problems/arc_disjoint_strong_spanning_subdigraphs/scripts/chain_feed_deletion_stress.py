"""Stress-test D42 by deleting {u,heads}->forced-I feed arcs.

D55 identifies seven D42 feed arcs that support the Chain-Feed Missing
Entry Lemma.  The most direct refutation attempt is to delete these
arcs, hoping to keep the sealed multi-crossing chain-kernel gates while
destroying the two-feed supply.  This script enumerates all 2^7 feed-arc
deletion patterns and records which gates survive.
"""
from __future__ import annotations

import itertools
import os
import sys
from collections import Counter, defaultdict

import networkx as nx

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_feed_source_audit import feed_pairs, source_table  # noqa: E402
from chain_kernel_witness import dbullet_arcs, is_in_arb  # noqa: E402
from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)
from digraph import Digraph  # noqa: E402


N_DB = 23
N_HOST = 24
ROOT = 0
U = 1
V = 7
V1_HOST = {0, 1, 9, 11, 13}
V2_HOST = tuple(v for v in range(N_HOST) if v not in V1_HOST)
FEED_ARCS = (
    (1, 8),
    (1, 10),
    (1, 12),
    (5, 8),
    (6, 8),
    (5, 10),
    (6, 10),
)
FORCED_DO = ((7, 8), (8, 9), (10, 11), (12, 13))
B_STAR = {1, 2, 3, 4, 5, 6, 7, 8, 10, 12}


def host_arcs_from_dbullet(arcs):
    host = [(0, 1)]
    rho_in = Counter()
    rho_out = Counter()
    for x, y in arcs:
        if y == ROOT:
            rho_in[x] += 1
        elif x == ROOT:
            rho_out[y] += 1
        else:
            host.append((x + 1, y + 1))
    for x, m in rho_in.items():
        host.append((x + 1, 0))
        if m == 2:
            host.append((x + 1, 1))
    for y, m in rho_out.items():
        host.append((0, y + 1))
        if m == 2:
            host.append((1, y + 1))
    return host


def is_one_zero_near_split_host(host):
    if len(host) != len(set(host)):
        return False, "host-not-simple"
    internal = [(x, y) for x, y in host if x in V1_HOST and y in V1_HOST]
    if internal != [(0, 1)]:
        return False, f"bad-v1-internal:{internal}"
    v2_arcs = set((x, y) for x, y in host if x in V2_HOST and y in V2_HOST)
    for a, b in itertools.combinations(V2_HOST, 2):
        if (a, b) not in v2_arcs and (b, a) not in v2_arcs:
            return False, f"v2-not-semicomplete:{a},{b}"
    return True, "ok"


def min_cut_witness(arcs, n):
    D = Digraph.from_arcs(range(n), arcs)
    if not D.is_strongly_connected():
        scc = next(iter(nx.strongly_connected_components(D.G)))
        return 0, tuple(sorted(scc))
    simple = nx.DiGraph()
    simple.add_nodes_from(range(n))
    cap = Counter(arcs)
    for (x, y), c in cap.items():
        simple.add_edge(x, y, capacity=c)
    best = (10**9, None, None, None)
    for v in range(1, n):
        for s, t in ((0, v), (v, 0)):
            value, part = nx.minimum_cut(simple, s, t, capacity="capacity")
            side = tuple(sorted(part[0]))
            if value < best[0]:
                best = (int(value), side, s, t)
    return best


def structural_gates(arcs):
    out = {}
    host = host_arcs_from_dbullet(arcs)
    near_ok, near_reason = is_one_zero_near_split_host(host)
    out["near_split"] = near_ok
    out["near_split_reason"] = near_reason

    out["lambda_db"] = Digraph.from_arcs(range(N_DB), arcs).arc_connectivity()
    out["lambda_host"] = Digraph.from_arcs(range(N_HOST), host).arc_connectivity()
    out["db_min_cut"] = None
    if out["lambda_db"] < 3:
        out["db_min_cut"] = min_cut_witness(arcs, N_DB)

    mult = Counter(arcs)
    G = nx.MultiDiGraph()
    G.add_nodes_from(range(N_DB))
    G.add_edges_from(arcs)
    Gm = G.copy()
    Gm.remove_node(U)
    cage = {U} | {
        x for x in range(N_DB)
        if x not in (ROOT, U) and not nx.has_path(Gm, x, ROOT)
    }
    out["cage"] = tuple(sorted(cage))

    paths = list(nx.all_shortest_paths(Gm, V, ROOT))
    out["unique_path"] = paths == [[7, 8, 9, 10, 11, 12, 13, 0]]

    forced_ok = True
    forced_seen = {}
    O = {7, 8, 9, 10, 11, 12, 13}
    for t, hd in FORCED_DO:
        do_arcs = sorted(
            (x, y) for (x, y) in mult
            if x == t and (y in O or y == ROOT)
        )
        forced_seen[t] = tuple(do_arcs)
        forced_ok = forced_ok and do_arcs == [(t, hd)]
    out["forced_do"] = forced_ok
    out["forced_seen"] = forced_seen

    b_out = sorted((x, y) for (x, y) in mult if x in B_STAR and y not in B_STAR)
    out["sealed_bstar"] = b_out == [(8, 9), (10, 11), (12, 13)]
    out["bstar_out"] = tuple(b_out)
    out["structural_ok"] = (
        near_ok
        and out["lambda_db"] >= 3
        and out["lambda_host"] >= 3
        and out["cage"] == (1, 2, 3, 4)
        and out["unique_path"]
        and out["forced_do"]
        and out["sealed_bstar"]
    )
    return out


def original_hard_pair_survives(arcs):
    mult = Counter(arcs)
    T0 = {2:3, 3:1, 4:1, 1:7, 5:8, 6:8, 7:8, 8:9, 9:22, 10:5, 12:5,
          11:12, 13:0, 14:0, 15:0, 22:20, 20:18, 18:16, 16:14, 17:14,
          19:16, 21:18}
    U0 = {2:1, 3:2, 4:2, 1:10, 10:11, 11:18, 18:17, 17:15, 15:0,
          5:10, 6:10, 7:2, 8:2, 9:10, 12:13, 13:0, 14:0, 16:15,
          19:17, 20:19, 21:19, 22:21}
    Ts0, Us0 = tree_arcs(T0), tree_arcs(U0)
    usage = Counter(Ts0) + Counter(Us0)
    available = all(usage[e] <= mult[e] for e in usage)
    ok = is_in_arb(T0, N_DB, ROOT) and is_in_arb(U0, N_DB, ROOT)
    ok = ok and available and pair_realizable(Ts0, Us0, mult)
    if not ok:
        missing = tuple(sorted(e for e in usage if usage[e] > mult[e]))
        return False, {"reason": "not-realizable", "missing": missing}
    Xg = subtree_through(T0, U, ROOT, N_DB)
    exits = [(x, y) for x, y in Us0 if x in Xg and y not in Xg]
    free = [
        e for e in mult
        if e[0] in Xg and e[1] not in Xg
        and mult[e] - (e in Ts0) - (e in Us0) >= 1
    ]
    return Xg == {1, 2, 3, 4} and len(exits) == 1 and free, {
        "X": tuple(sorted(Xg)),
        "exits": tuple(exits),
        "free": tuple(sorted(free)),
    }


def deletion_rows():
    base = list(dbullet_arcs())
    base_counter = Counter(base)
    assert all(base_counter[e] == 1 for e in FEED_ARCS)
    rows = []
    for bits in range(1 << len(FEED_ARCS)):
        deleted = tuple(FEED_ARCS[i] for i in range(len(FEED_ARCS)) if (bits >> i) & 1)
        deleted_set = set(deleted)
        arcs = [e for e in base if e not in deleted_set]
        gates = structural_gates(arcs)
        source_rows = source_table(arcs)
        options, good_pairs = feed_pairs(source_rows)
        hard_ok, hard_info = original_hard_pair_survives(arcs)
        row = {
            "deleted": deleted,
            "n_deleted": len(deleted),
            "structural_ok": gates["structural_ok"],
            "lambda_db": gates["lambda_db"],
            "lambda_host": gates["lambda_host"],
            "feed_options": tuple(options),
            "good_two_feed_pairs": len(good_pairs),
            "hard_pair_ok": bool(hard_ok),
            "hard_info": hard_info,
            "gates": gates,
        }
        rows.append(row)
    return rows


def first_failed_gate(row):
    gates = row["gates"]
    checks = [
        ("near_split", gates["near_split"]),
        ("lambda_db>=3", gates["lambda_db"] >= 3),
        ("lambda_host>=3", gates["lambda_host"] >= 3),
        ("cage", gates["cage"] == (1, 2, 3, 4)),
        ("unique_path", gates["unique_path"]),
        ("forced_do", gates["forced_do"]),
        ("sealed_bstar", gates["sealed_bstar"]),
    ]
    for name, ok in checks:
        if not ok:
            return name
    return "ok"


def main():
    rows = deletion_rows()
    structural = [r for r in rows if r["structural_ok"]]
    counter = [
        r for r in structural
        if r["good_two_feed_pairs"] == 0
    ]
    weak = [
        r for r in structural
        if r["good_two_feed_pairs"] < 11
    ]
    hard_survivors = [r for r in structural if r["hard_pair_ok"]]
    no_good = [r for r in rows if r["good_two_feed_pairs"] == 0]

    print("D42 chain-feed deletion stress")
    print(f"feed_arcs={FEED_ARCS}")
    print(f"patterns={len(rows)} structural_survivors={len(structural)}")
    print(f"weak_feed_structural_survivors={len(weak)} counter_candidates={len(counter)}")
    print(f"original_hard_pair_survivors={len(hard_survivors)}")
    print(f"no_good_patterns={len(no_good)}")

    by_deleted = defaultdict(int)
    by_gate = defaultdict(int)
    for r in rows:
        if r["structural_ok"]:
            by_deleted[r["n_deleted"]] += 1
        else:
            by_gate[first_failed_gate(r)] += 1
    print(f"structural_survivors_by_deleted={dict(sorted(by_deleted.items()))}")
    print(f"first_failed_gate_counts={dict(sorted(by_gate.items()))}")
    no_good_by_gate = Counter(first_failed_gate(r) for r in no_good)
    print(f"no_good_first_failed_gate_counts={dict(sorted(no_good_by_gate.items()))}")

    print("\nStructural survivors with feed loss:")
    for r in sorted(weak, key=lambda x: (x["good_two_feed_pairs"], x["n_deleted"], x["deleted"]))[:20]:
        print(
            f"  deleted={r['deleted']} lambda_db={r['lambda_db']} "
            f"lambda_host={r['lambda_host']} feeds={len(r['feed_options'])} "
            f"good_pairs={r['good_two_feed_pairs']} hard_pair={r['hard_pair_ok']}"
        )

    if counter:
        print("\nCOUNTER CANDIDATE:")
        r = sorted(counter, key=lambda x: (x["n_deleted"], x["deleted"]))[0]
        print(r)
    else:
        print("\nNo-good deletion attempts:")
        for r in sorted(no_good, key=lambda x: (first_failed_gate(x), x["n_deleted"], x["deleted"]))[:10]:
            print(
                f"  deleted={r['deleted']} first_failed={first_failed_gate(r)} "
                f"lambda_db={r['lambda_db']} db_min_cut={r['gates']['db_min_cut']}"
            )
        # Explain the nearest failures that try hardest to kill feeds.
        min_pairs = min(r["good_two_feed_pairs"] for r in structural)
        nearest = [r for r in structural if r["good_two_feed_pairs"] == min_pairs]
        print(f"\nNo structural survivor kills the two-feed condition; min_good_pairs={min_pairs}")
        for r in sorted(nearest, key=lambda x: (x["n_deleted"], x["deleted"]))[:10]:
            print(f"  nearest deleted={r['deleted']} feed_options={r['feed_options']}")

    assert len(rows) == 128
    assert structural
    assert not counter
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
