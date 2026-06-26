"""Bounded repair-and-delete search for chain-feed counterkernels.

D56 showed that pure deletion of D42's {u,heads}->forced-I feeds cannot
kill the two-feed condition while preserving lambda(D^bullet)>=3.  This
script tries the next counterexample move: after deleting enough feeds
to kill all valid two-feed pairs, add a small number of substitute arcs
from non-{u,heads} sources into forced I-vertices and test whether the
sealed chain-kernel structural gates return.
"""
from __future__ import annotations

import itertools
import os
import sys
import argparse
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_feed_deletion_stress import (  # noqa: E402
    FEED_ARCS,
    FORCED_DO,
    N_DB,
    deletion_rows,
    first_failed_gate,
    host_arcs_from_dbullet,
    is_one_zero_near_split_host,
    structural_gates,
)
from chain_feed_source_audit import feed_pairs, source_table  # noqa: E402
from chain_kernel_witness import dbullet_arcs  # noqa: E402
import networkx as nx


DEFAULT_MAX_ADDED = 2
FORCED_I = tuple(t for t, _succ in FORCED_DO if t != 7)
NON_FEED_SOURCES = tuple(
    v for v in range(1, N_DB)
    if v not in {1, 5, 6, 8, 10, 12}
)
B_STAR = {1, 2, 3, 4, 5, 6, 7, 8, 10, 12}


def candidate_arcs(arcs):
    have = set(arcs)
    out = []
    for x in NON_FEED_SOURCES:
        for y in FORCED_I:
            if x == y or (x, y) in have:
                continue
            out.append((x, y))
    return tuple(sorted(out))


def region(v):
    if v in {2, 3, 4}:
        return "cage"
    if v == 7:
        return "v"
    if v in {9, 11, 13}:
        return "chainK"
    if v in {14, 15}:
        return "roots"
    if 16 <= v <= 22:
        return "ladder"
    return f"other{v}"


def base_arcs_after_deletion(deleted):
    deleted = set(deleted)
    return [e for e in dbullet_arcs() if e not in deleted]


def no_good_after(arcs):
    _options, good = feed_pairs(source_table(arcs))
    return len(good) == 0


def cheap_chain_gates(arcs):
    host = host_arcs_from_dbullet(arcs)
    near_ok, _reason = is_one_zero_near_split_host(host)
    if not near_ok:
        return False, "near_split"

    mult = Counter(arcs)
    G = nx.MultiDiGraph()
    G.add_nodes_from(range(N_DB))
    G.add_edges_from(arcs)
    Gm = G.copy()
    Gm.remove_node(1)
    cage = {1} | {
        x for x in range(N_DB)
        if x not in (0, 1) and not nx.has_path(Gm, x, 0)
    }
    if cage != {1, 2, 3, 4}:
        return False, "cage"

    paths = list(nx.all_shortest_paths(Gm, 7, 0))
    if paths != [[7, 8, 9, 10, 11, 12, 13, 0]]:
        return False, "unique_path"

    O = {7, 8, 9, 10, 11, 12, 13}
    for t, hd in FORCED_DO:
        do_arcs = sorted(
            (x, y) for (x, y) in mult
            if x == t and (y in O or y == 0)
        )
        if do_arcs != [(t, hd)]:
            return False, "forced_do"

    b_out = sorted((x, y) for (x, y) in mult if x in B_STAR and y not in B_STAR)
    if b_out != [(8, 9), (10, 11), (12, 13)]:
        return False, "sealed_bstar"
    return True, "ok"


def repairs_base_min_cut(row, added):
    cut = row["gates"].get("db_min_cut")
    if cut is None:
        return True
    value, side, _s, _t = cut
    side = set(side)
    crossing = sum(1 for x, y in added if x in side and y not in side)
    return value + crossing >= 3


def search(max_added=DEFAULT_MAX_ADDED):
    rows = deletion_rows()
    no_good_deletions = [r for r in rows if r["good_two_feed_pairs"] == 0]
    hits = []
    tried = 0
    by_delete = {}
    fail_gate_counts = Counter()
    cheap_fail_counts = Counter()
    mincut_skip = 0
    full_checks = 0
    candidate_region_counts = Counter()

    for row in no_good_deletions:
        base = base_arcs_after_deletion(row["deleted"])
        cands = candidate_arcs(base)
        local_tried = 0
        local_hits = []
        for size in range(1, max_added + 1):
            for added in itertools.combinations(cands, size):
                tried += 1
                local_tried += 1
                candidate_region_counts[tuple(region(x) for x, _y in added)] += 1
                if not repairs_base_min_cut(row, added):
                    mincut_skip += 1
                    continue
                arcs = base + list(added)
                if not no_good_after(arcs):
                    continue
                cheap_ok, cheap_reason = cheap_chain_gates(arcs)
                if not cheap_ok:
                    cheap_fail_counts[cheap_reason] += 1
                    continue
                full_checks += 1
                gates = structural_gates(arcs)
                if gates["structural_ok"]:
                    hit = {
                        "deleted": row["deleted"],
                        "added": added,
                        "lambda_db": gates["lambda_db"],
                        "lambda_host": gates["lambda_host"],
                        "cage": gates["cage"],
                    }
                    hits.append(hit)
                    local_hits.append(hit)
                else:
                    fail_gate_counts[first_failed_gate({"gates": gates})] += 1
        by_delete[row["deleted"]] = {
            "tried": local_tried,
            "hits": len(local_hits),
        }
    return {
        "no_good_deletions": len(no_good_deletions),
        "tried": tried,
        "hits": hits,
        "by_delete": by_delete,
        "fail_gate_counts": fail_gate_counts,
        "cheap_fail_counts": cheap_fail_counts,
        "mincut_skip": mincut_skip,
        "full_checks": full_checks,
        "candidate_region_counts": candidate_region_counts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-added", type=int, default=DEFAULT_MAX_ADDED)
    args = parser.parse_args()

    result = search(max_added=args.max_added)
    print("D42 chain-feed repair-and-delete search")
    print(f"max_added={args.max_added}")
    print(f"non_feed_sources={NON_FEED_SOURCES}")
    print(f"forced_i_targets={FORCED_I}")
    print(f"feed_arcs={FEED_ARCS}")
    print(
        f"no_good_deletions={result['no_good_deletions']} "
        f"tried={result['tried']} hits={len(result['hits'])}"
    )
    print(f"fail_gate_counts={dict(sorted(result['fail_gate_counts'].items()))}")
    print(f"cheap_fail_counts={dict(sorted(result['cheap_fail_counts'].items()))}")
    print(f"mincut_skip={result['mincut_skip']} full_checks={result['full_checks']}")
    print("candidate_region_patterns_top:")
    for regs, count in result["candidate_region_counts"].most_common(10):
        print(f"  {regs}: {count}")

    if result["hits"]:
        print("\nCOUNTERKERNEL CANDIDATES:")
        for hit in result["hits"][:20]:
            print(f"  {hit}")
    else:
        worst = sorted(
            result["by_delete"].items(),
            key=lambda kv: (-kv[1]["tried"], kv[0]),
        )[:5]
        print("\nNo repaired no-good structural survivor found.")
        print("largest local searches:")
        for deleted, info in worst:
            print(f"  deleted={deleted} tried={info['tried']} hits={info['hits']}")

    assert result["no_good_deletions"] == 25
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
