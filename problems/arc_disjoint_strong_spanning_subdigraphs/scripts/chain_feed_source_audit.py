"""Audit feed sources for the D42 chain-feed pending lemma.

D54 isolates the next symbolic target: in a sealed multi-crossing chain
kernel, two forced I-vertices should admit pending split paths from
{u} union Heads into distinct chain successors, with at least one source
equal to u.  This script records the exact source-region table for the
realized D42 chain kernel.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_kernel_witness import dbullet_arcs  # noqa: E402


ROOT = 0
U = 1
HEADS = {5, 6}
FORCED_I = (8, 10, 12)
CHAIN_SUCCESSOR = {8: 9, 10: 11, 12: 13}
HOST_LABEL = {v: v + 1 for v in range(1, 23)}


def region(v):
    if v == ROOT:
        return "rho"
    if v == U:
        return "u"
    if v in {2, 3, 4}:
        return "cage"
    if v in HEADS:
        return "heads"
    if v == 7:
        return "v"
    if v in FORCED_I:
        return "forcedI"
    if v in {9, 11, 13}:
        return "chainK"
    if v in {14, 15}:
        return "roots"
    if 16 <= v <= 22:
        return "ladder"
    return f"other{v}"


def source_table(arcs):
    incoming = defaultdict(list)
    for x, y in arcs:
        incoming[y].append(x)

    rows = []
    for i in FORCED_I:
        succ = CHAIN_SUCCESSOR[i]
        sources = sorted(
            x for x in incoming[i]
            if x != ROOT and x not in FORCED_I
        )
        by_region = defaultdict(list)
        for x in sources:
            by_region[region(x)].append(x)
        feed_sources = sorted(
            x for x in sources
            if x == U or x in HEADS
        )
        rows.append({
            "forced_i": i,
            "host_forced_i": HOST_LABEL[i],
            "successor": succ,
            "host_successor": HOST_LABEL[succ],
            "sources": sources,
            "by_region": {k: tuple(v) for k, v in sorted(by_region.items())},
            "feed_sources": tuple(feed_sources),
            "has_u_feed": U in feed_sources,
            "has_head_feed": any(x in HEADS for x in feed_sources),
        })
    return rows


def feed_pairs(rows):
    options = []
    for r in rows:
        for x in r["feed_sources"]:
            options.append((x, r["forced_i"], r["successor"]))

    good = []
    for a_idx, a in enumerate(options):
        for b in options[a_idx + 1:]:
            if a[1] == b[1]:
                continue
            if U not in (a[0], b[0]):
                continue
            good.append((a, b))
    return options, good


def main():
    arcs = dbullet_arcs()
    rows = source_table(arcs)
    options, good_pairs = feed_pairs(rows)

    print("D42 chain-feed source audit")
    print("path: 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> rho")
    print("forced I vertices and incoming source regions:")
    for r in rows:
        print(
            f"  i={r['forced_i']} host={r['host_forced_i']} "
            f"succ={r['successor']} host_succ={r['host_successor']} "
            f"by_region={r['by_region']} feed_sources={r['feed_sources']}"
        )

    feed_region_counts = Counter()
    for x, _i, _succ in options:
        feed_region_counts[region(x)] += 1
    print(f"feed_options={options}")
    print(f"feed_region_counts={dict(sorted(feed_region_counts.items()))}")
    print(f"good_two_feed_pairs={len(good_pairs)}")
    print(f"sample_good_pair={good_pairs[0] if good_pairs else None}")

    assert sum(1 for r in rows if r["feed_sources"]) >= 2
    assert any(r["has_u_feed"] for r in rows)
    assert good_pairs
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
