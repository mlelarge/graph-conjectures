"""For each vertex v in a witness, look at delta+({v}) and check the color
multiset.  For a 3-arc-strong digraph, every singleton out-cut has size
>= 3.  Under the deficit-aware regime, *most* non-interface vertices have
out-degree exactly 3.  We want to know: across the witnesses, what fraction
of degree-3 vertex out-cuts are (1,2) vs (2,1) vs other?
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from benchmarks import all_benchmarks  # noqa: E402
from generators.glue_deficit import (  # noqa: E402
    DeficitGenConfig,
    generate_deficit_gluings,
    passes_arc_strong_3,
)
from verifier_sat import verify_sat  # noqa: E402


def main():
    bench = {b.name: b for b in all_benchmarks()}
    pair_classes = {
        "C1_C8sq_C8sq": ("C8_square", "C8_square"),
        "C2c_L312_L312": ("AiEtAl_L312_min", "AiEtAl_L312_min"),
        "C3a_iv_iv": ("AiEtAl_iv_star_iv", "AiEtAl_iv_star_iv"),
    }
    cfg = DeficitGenConfig(
        interface_sizes=(3, 4),
        max_interfaces_per_pair_per_size=30,
        max_bridges_per_interface=24,
        max_extra_slack_per_direction=1,
        allow_self_glue=True,
        ordered_pairs=True,
        require_arc_conn_exactly_3=True,
        verified_per_pair_cap=6,
        seed=20260516,
    )

    # Categorize vertex out-cuts by (vertex_type, color split normalized)
    # Vertex types:
    #   "S1n_deg3" - side1-non-iface, out-deg 3
    #   "S1n_deg>3" - side1-non-iface, higher
    #   "I" - interface
    #   "S2n_deg3", "S2n_deg>3"
    vertex_pattern = Counter()

    for cls, (n1, n2) in pair_classes.items():
        templates = [bench[n1]] if n1 == n2 else [bench[n1], bench[n2]]
        cnt = 0
        for inst in generate_deficit_gluings(templates, cfg):
            if (inst.template1, inst.template2) != (n1, n2):
                continue
            D = inst.build()
            if not passes_arc_strong_3(D, exact=True):
                continue
            res = verify_sat(D, time_limit_s=20.0)
            if res["status"] != "SAT":
                continue
            red, blue = res["witness"]
            red_set = set(red)

            T1 = bench[inst.template1]
            s = len(inst.S1)
            interface_start = T1.n - s
            interface_end = T1.n
            n = inst.n

            # Build keyed arcs
            parallel = Counter()
            keyed = []
            for (u, v) in inst.arcs:
                k = parallel[(u, v)]
                keyed.append((u, v, k))
                parallel[(u, v)] += 1

            for v in range(n):
                out_arcs = [ke for ke in keyed if ke[0] == v]
                if not out_arcs:
                    continue
                d_out = len(out_arcs)
                colors = ["R" if ke in red_set else "B" for ke in out_arcs]
                R = colors.count("R")
                B = colors.count("B")
                # canonicalize: majority is "majority"
                maj, mino = (R, B) if R >= B else (B, R)
                if v < interface_start:
                    region = "S1n"
                elif v < interface_end:
                    region = "I"
                else:
                    region = "S2n"
                if d_out == 3:
                    bucket = f"{region}_outdeg3"
                else:
                    bucket = f"{region}_outdeg{d_out}"
                vertex_pattern[(bucket, (maj, mino))] += 1
            cnt += 1
            if cnt >= 5:
                break

    print("=== vertex out-cuts (canonical majority-first) ===")
    by_bucket = {}
    for (bucket, mb), n in vertex_pattern.items():
        by_bucket.setdefault(bucket, []).append((mb, n))
    for bucket in sorted(by_bucket):
        rows = sorted(by_bucket[bucket], key=lambda x: -x[1])
        print(f"  {bucket}:")
        for mb, n in rows:
            print(f"     (maj,min)={mb}  count={n}")


if __name__ == "__main__":
    main()
