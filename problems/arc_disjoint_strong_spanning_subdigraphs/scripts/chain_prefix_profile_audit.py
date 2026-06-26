"""Audit the D42 prefix-cut and prefix-lift profiles.

D58 proves the pending connectivity lemma assuming a D42-style
prefix-cut/profile-lift package.  This script prints that package
directly for the D42 split core:

  * the only split-core cuts of out-size <= 1;
  * the two-step pending paths x -> s -> y through forced host vertices
    that can repair each deficient cut;
  * the region types of those repair paths.
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

from chain_kernel_witness import host_arcs  # noqa: E402
from d42_split_predicate_tester import (  # noqa: E402
    d42_split_setup,
    deficient_core_cuts,
    region,
)


def cut_vertices(v2, mask):
    return tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1)


def pending_repairs(cut, v2, pending_vertices):
    cut_set = set(cut)
    v2_set = set(v2)
    host = set(host_arcs())
    repairs = []
    for s in pending_vertices:
        incoming = sorted(x for x in v2_set if x in cut_set and (x, s) in host)
        outgoing = sorted(y for y in v2_set if y not in cut_set and (s, y) in host)
        for x in incoming:
            for y in outgoing:
                repairs.append((x, s, y, region(x), region(y)))
    return tuple(repairs)


def main():
    v2, core_arcs, _rel, pending_vertices, _per_vertex = d42_split_setup()
    deficient = deficient_core_cuts(len(v2), core_arcs)

    print("D42 prefix profile audit")
    print(f"pending_vertices={pending_vertices}")
    print("deficient split-core cuts:")
    profiles = []
    for mask, core_out in deficient:
        cut = cut_vertices(v2, mask)
        repairs = pending_repairs(cut, v2, pending_vertices)
        region_counts = Counter((src_region, dst_region) for *_xyz, src_region, dst_region in repairs)
        feed_repairs = [
            r for r in repairs
            if r[3] in {"u", "heads"} and r[4] == "chainK"
        ]
        profiles.append((core_out, cut, repairs, feed_repairs))
        print(f"  out={core_out} cut={cut}")
        print(f"    repair_region_counts={dict(sorted(region_counts.items()))}")
        print(f"    feed_repairs={feed_repairs}")

    assert len(deficient) == 3
    assert [p[0] for p in profiles] == [1, 0, 1]
    q_minus, q0, q_plus = profiles
    assert q0[3], "middle prefix has no u/head->chainK repair"
    assert any(r[3] == "u" and r[4] == "chainK" for r in q_minus[2])
    assert any(r[4] == "chainK" and r[2] not in q_plus[1] for r in q_plus[3])
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
