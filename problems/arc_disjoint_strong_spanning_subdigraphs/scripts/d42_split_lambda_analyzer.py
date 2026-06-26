"""Analyze which D42 pending split choices make the split core lambda >= 2.

D51 showed that prescribed pending completion on the D42 chain kernel is
sparse because most split choices leave the semicomplete core with
lambda 0 or 1.  This script ignores colouring and samples more split
choices, recording only the split-core arc-connectivity and coarse
endpoint regions of the selected paths through the forced-chain host
vertices 9, 11, 13.
"""
from __future__ import annotations

import os
import random
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from digraph import Digraph  # noqa: E402
from pending_decomposition_probe import (  # noqa: E402
    Case,
    local_split_choices,
    relabel_core_arcs,
)
from chain_kernel_witness import host_arcs  # noqa: E402


SEED = 5113
SAMPLES = 2000


def region(v):
    if v == 2:
        return "u"
    if v in {3, 4, 5}:
        return "cage"
    if v in {6, 7}:
        return "heads"
    if v == 8:
        return "v"
    if v in {10, 12, 14}:
        return "chainK"
    if v in {15, 16}:
        return "roots"
    if 17 <= v <= 23:
        return "ladder"
    return f"other{v}"


def split_signature(choice):
    per_s = []
    all_pairs = []
    for s in (9, 11, 13):
        regs = tuple(sorted((region(x), region(y)) for x, y in choice[s]))
        per_s.append((s, regs))
        all_pairs.extend(regs)
    return tuple(per_s), tuple(sorted(all_pairs))


def main():
    rng = random.Random(SEED)
    v1 = (0, 1, 9, 11, 13)
    v2 = tuple(v for v in range(24) if v not in v1)
    case = Case("chain_kernel_D42_host", host_arcs(), 24, v1, v2)
    host = list(case.host_arcs)
    host_set = set(host)
    core_arcs = relabel_core_arcs(host, case.v2)
    rel = {v: i for i, v in enumerate(case.v2)}

    per_vertex = {
        s: local_split_choices(host_set, case.v2, s, rng)
        for s in (9, 11, 13)
    }
    local_counts = {s: len(per_vertex[s]) for s in per_vertex}
    lambda_counts = Counter()
    per_vertex_region_counts = {s: Counter() for s in per_vertex}
    success_signature_counts = Counter()
    fail_signature_counts = Counter()
    success_pair_presence = Counter()
    fail_pair_presence = Counter()
    examples = {}

    seen = set()
    attempts = 0
    while len(seen) < SAMPLES and attempts < 30 * SAMPLES:
        attempts += 1
        key = tuple(rng.randrange(len(per_vertex[s])) for s in (9, 11, 13))
        if key in seen:
            continue
        seen.add(key)
        choice = {s: per_vertex[s][key[i]] for i, s in enumerate((9, 11, 13))}

        split_arcs = []
        split_paths = []
        for s in (9, 11, 13):
            for x, y in choice[s]:
                split_arcs.append((rel[x], rel[y]))
                split_paths.append((x, s, y, region(x), region(y)))
                per_vertex_region_counts[s][(region(x), region(y))] += 1

        lam = Digraph.from_arcs(range(len(v2)), core_arcs + split_arcs).arc_connectivity()
        lambda_counts[lam] += 1
        per_s_sig, all_sig = split_signature(choice)
        if lam >= 2:
            success_signature_counts[all_sig] += 1
            for pair in set(all_sig):
                success_pair_presence[pair] += 1
            examples.setdefault(("success", lam), (choice, split_paths, all_sig, per_s_sig))
        else:
            fail_signature_counts[all_sig] += 1
            for pair in set(all_sig):
                fail_pair_presence[pair] += 1
            examples.setdefault(("fail", lam), (choice, split_paths, all_sig, per_s_sig))

    print("D42 split-core lambda analyzer")
    print(f"seed={SEED} samples={len(seen)} local_counts={local_counts}")
    print(f"lambda_counts={dict(sorted(lambda_counts.items()))}")
    success_total = sum(c for lam, c in lambda_counts.items() if lam >= 2)
    fail_total = sum(c for lam, c in lambda_counts.items() if lam < 2)
    print("\nper-vertex endpoint-region frequencies:")
    for s in (9, 11, 13):
        print(f"  s={s}: {dict(per_vertex_region_counts[s].most_common())}")
    print("\ntop successful all-pair region signatures:")
    for sig, count in success_signature_counts.most_common(10):
        print(f"  count={count} sig={sig}")
    print("\ntop failing all-pair region signatures:")
    for sig, count in fail_signature_counts.most_common(10):
        print(f"  count={count} sig={sig}")
    print("\nendpoint-region pair support (present in a split choice):")
    pairs = sorted(set(success_pair_presence) | set(fail_pair_presence))
    for pair in pairs:
        s_count = success_pair_presence[pair]
        f_count = fail_pair_presence[pair]
        if s_count == 0 and f_count == 0:
            continue
        s_pct = 100.0 * s_count / success_total if success_total else 0.0
        f_pct = 100.0 * f_count / fail_total if fail_total else 0.0
        if s_pct >= 80.0 or (s_pct - f_pct) >= 25.0 or f_pct - s_pct >= 25.0:
            print(
                f"  {pair}: success {s_count}/{success_total} ({s_pct:.1f}%), "
                f"fail {f_count}/{fail_total} ({f_pct:.1f}%)"
            )
    print("\nexamples:")
    for key in sorted(examples, key=lambda x: (x[0], x[1])):
        choice, split_paths, all_sig, per_s_sig = examples[key]
        print(f"  {key}: all_sig={all_sig}")
        print(f"    per_s_sig={per_s_sig}")
        print(f"    split_paths={split_paths}")

    assert lambda_counts[2] + lambda_counts[3] > 0
    assert lambda_counts[0] + lambda_counts[1] > 0
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
