"""Audit the exact cut-cover inequalities behind the D42 split core.

D59 corrected the D58 feed-existence step: the three deficient prefix
cuts need to be covered, but their repairs need not all be
{u,heads}->chainK feeds.  This script states the exact finite
criterion:

    cover(Q-) >= 1, cover(Q0) >= 2, cover(Q+) >= 1.

The criterion is necessary and sufficient for the D42 capped split
suite because D53 verified that every other split-core cut already has
out-size at least two before adding pending split arcs.
"""
from __future__ import annotations

import itertools
import os
import sys
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from d42_split_predicate_tester import (  # noqa: E402
    best_candidate,
    d42_split_setup,
    deficient_core_cuts,
    feature_counts,
    out_cut_size,
    region,
    split_arcs_and_pairs,
    split_repairs_all_deficient_cuts,
)


def cut_vertices(v2, mask):
    return tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1)


def cover_vector(split_arcs, deficient):
    return tuple(out_cut_size(split_arcs, mask) for mask, _core_out in deficient)


def crosses(mask, rel, x, y):
    ux = rel[x]
    vy = rel[y]
    return bool((mask >> ux) & 1 and not ((mask >> vy) & 1))


def atomic_repair_table(v2, rel, vertices, per_vertex, deficient):
    atoms = set()
    for s in vertices:
        for local in per_vertex[s]:
            for x, y in local:
                atoms.add((s, x, y))

    grouped = defaultdict(list)
    for s, x, y in sorted(atoms):
        vector = tuple(1 if crosses(mask, rel, x, y) else 0 for mask, _ in deficient)
        if vector == (0, 0, 0):
            continue
        key = (region(x), region(y), vector)
        grouped[key].append((x, s, y))
    return grouped


def main():
    v2, core_arcs, rel, vertices, per_vertex = d42_split_setup()
    deficient = deficient_core_cuts(len(v2), core_arcs)
    requirements = tuple(2 - core_out for _mask, core_out in deficient)

    print("D42 cut-cover inequality audit")
    print("deficient cuts:")
    for i, (mask, core_out) in enumerate(deficient):
        print(
            f"  Q{i}: core_out={core_out} need={2 - core_out} "
            f"cut={cut_vertices(v2, mask)}"
        )
    print(f"requirements={requirements}")

    print("\natomic repairing split arcs, grouped by region and cover vector:")
    atomic = atomic_repair_table(v2, rel, vertices, per_vertex, deficient)
    for key in sorted(atomic):
        src_region, dst_region, vector = key
        examples = atomic[key][:6]
        more = "" if len(atomic[key]) <= 6 else f" ... +{len(atomic[key]) - 6}"
        print(
            f"  {src_region}->{dst_region} vector={vector} "
            f"count={len(atomic[key])} examples={examples}{more}"
        )

    total = 1
    for s in vertices:
        total *= len(per_vertex[s])

    cover_success = 0
    d53_selected = 0
    d53_bad = 0
    non_d53_success = 0
    distribution = Counter()
    non_d53_example = None
    broad_repair_success = 0
    broad_repair_example = None

    for product in itertools.product(*(range(len(per_vertex[s])) for s in vertices)):
        choice = {s: per_vertex[s][product[i]] for i, s in enumerate(vertices)}
        split_arcs, pairs = split_arcs_and_pairs(choice, rel, vertices)
        vector = cover_vector(split_arcs, deficient)
        covers = all(vector[i] >= requirements[i] for i in range(len(requirements)))
        ok, witness = split_repairs_all_deficient_cuts(deficient, split_arcs)
        assert covers == ok, (product, vector, requirements, witness)
        if covers:
            cover_success += 1
            distribution[vector] += 1
            repairing_paths = []
            for s in vertices:
                for x, y in choice[s]:
                    atom = (x, s, y, region(x), region(y))
                    atom_vector = tuple(
                        1 if crosses(mask, rel, x, y) else 0
                        for mask, _ in deficient
                    )
                    if atom_vector != (0, 0, 0):
                        repairing_paths.append((atom, atom_vector))
            if any(
                atom[3:5] in (("v", "chainK"), ("chainK", "chainK"))
                for atom, _atom_vector in repairing_paths
            ):
                broad_repair_success += 1
                if broad_repair_example is None:
                    broad_repair_example = {
                        "key": product,
                        "vector": vector,
                        "repairing_paths": tuple(repairing_paths),
                        "choice": choice,
                    }

        features = feature_counts(pairs)
        selected = best_candidate(features)
        if selected:
            d53_selected += 1
            if not covers:
                d53_bad += 1
        elif covers:
            non_d53_success += 1
            if non_d53_example is None:
                non_d53_example = {
                    "key": product,
                    "vector": vector,
                    "pairs": tuple(sorted(pairs)),
                    "choice": choice,
                }

    minimal_success_vectors = []
    for vector in distribution:
        if not all(vector[i] >= requirements[i] for i in range(len(requirements))):
            continue
        if not any(
            other != vector
            and all(other[i] <= vector[i] for i in range(len(requirements)))
            and all(other[i] >= requirements[i] for i in range(len(requirements)))
            for other in distribution
        ):
            minimal_success_vectors.append(vector)

    print("\nexact capped-suite results:")
    print(f"  local_counts={{{', '.join(f'{s}: {len(per_vertex[s])}' for s in vertices)}}}")
    print(f"  total={total}")
    print(f"  cover_success={cover_success}")
    print(f"  d53_selected={d53_selected}")
    print(f"  d53_bad={d53_bad}")
    print(f"  non_d53_success={non_d53_success}")
    print(f"  broad_repair_success={broad_repair_success}")
    print(f"  minimal_success_vectors={sorted(minimal_success_vectors)}")
    print("  top_success_vectors:")
    for vector, count in distribution.most_common(10):
        print(f"    {vector}: {count}")
    print(f"  first_non_d53_success={non_d53_example}")
    print(f"  first_broad_repair_success={broad_repair_example}")

    assert len(deficient) == 3
    assert requirements == (1, 2, 1)
    assert cover_success == 84014
    assert d53_selected == 56264
    assert d53_bad == 0
    assert non_d53_success == cover_success - d53_selected
    assert non_d53_example is not None
    assert broad_repair_success > 0
    assert broad_repair_example is not None
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
