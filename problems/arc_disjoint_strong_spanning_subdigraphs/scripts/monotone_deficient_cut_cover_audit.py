"""Audit the monotone deficient-prefix cut-cover criterion.

D63 showed that the exact D42 profile (1,0,1) is not structural: adding
the reverse head arc 7 -> 6 in host labels preserves the sealed-chain
gates but changes the old Q- core out-size from 1 to 2.

This script checks the corrected monotone criterion on both cores.  We
keep the same candidate prefix coordinates Q-, Q0, Q+, but set the
repair requirement at coordinate Q to max(0, 2 - d_C^+(Q)).  Thus the
original D42 core has requirement vector (1,2,1), while the D63
perturbation has (0,2,1).  For each capped pending split choice, the
script verifies that this vector criterion is exactly equivalent to
repairing all split-core cuts of out-size at most one.
"""
from __future__ import annotations

import itertools
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from d42_split_predicate_tester import (  # noqa: E402
    d42_split_setup,
    deficient_core_cuts,
    out_cut_size,
    split_arcs_and_pairs,
    split_repairs_all_deficient_cuts,
)


PREFIXES = (
    ("Q-", (2, 3, 4, 5, 7, 8)),
    ("Q0", (2, 3, 4, 5, 6, 7, 8)),
    ("Q+", (2, 3, 4, 5, 6, 7, 8, 10)),
)

D63_EXTRA_HOST_ARC = (7, 6)


def mask_for(v2, vertices):
    rel = {v: i for i, v in enumerate(v2)}
    return sum(1 << rel[v] for v in vertices)


def cut_vertices(v2, mask):
    return tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1)


def add_core_arc(core_arcs, rel, arc):
    u, v = arc
    assert u in rel and v in rel, arc
    extra = (rel[u], rel[v])
    assert extra not in set(core_arcs), extra
    return tuple(core_arcs) + (extra,)


def cover_vector(split_arcs, masks):
    return tuple(out_cut_size(split_arcs, mask) for mask in masks)


def minimal_success_vectors(distribution, requirements):
    out = []
    for vector in distribution:
        if not all(vector[i] >= requirements[i] for i in range(len(requirements))):
            continue
        dominated = False
        for other in distribution:
            if other == vector:
                continue
            if all(other[i] <= vector[i] for i in range(len(requirements))) and all(
                other[i] >= requirements[i] for i in range(len(requirements))
            ):
                dominated = True
                break
        if not dominated:
            out.append(vector)
    return sorted(out)


def scenario(name, extra_host_arc=None):
    v2, core_arcs, rel, pending_vertices, per_vertex = d42_split_setup()
    if extra_host_arc is not None:
        core_arcs = add_core_arc(core_arcs, rel, extra_host_arc)

    masks = tuple(mask_for(v2, vertices) for _name, vertices in PREFIXES)
    core_outs = tuple(out_cut_size(core_arcs, mask) for mask in masks)
    requirements = tuple(max(0, 2 - out) for out in core_outs)
    low_cuts = deficient_core_cuts(len(v2), core_arcs)
    active_prefixes = [
        (PREFIXES[i][0], PREFIXES[i][1], core_outs[i], requirements[i])
        for i in range(len(PREFIXES))
        if requirements[i] > 0
    ]
    active_by_mask = {
        mask_for(v2, vertices): (name, core_out)
        for name, vertices, core_out, _req in active_prefixes
    }

    low_details = [
        (core_out, cut_vertices(v2, mask))
        for mask, core_out in low_cuts
    ]
    assert set(active_by_mask) == {mask for mask, _core_out in low_cuts}, (
        name,
        active_prefixes,
        low_details,
    )

    total = 1
    for s in pending_vertices:
        total *= len(per_vertex[s])

    success = 0
    distribution = Counter()
    first_success = None

    for product in itertools.product(
        *(range(len(per_vertex[s])) for s in pending_vertices)
    ):
        choice = {
            s: per_vertex[s][product[i]]
            for i, s in enumerate(pending_vertices)
        }
        split_arcs, pairs = split_arcs_and_pairs(choice, rel, pending_vertices)
        vector = cover_vector(split_arcs, masks)
        covers = all(vector[i] >= requirements[i] for i in range(len(requirements)))
        ok, witness = split_repairs_all_deficient_cuts(low_cuts, split_arcs)
        assert covers == ok, (name, product, vector, requirements, witness)
        if covers:
            success += 1
            distribution[vector] += 1
            if first_success is None:
                first_success = {
                    "key": product,
                    "vector": vector,
                    "pairs": tuple(sorted(pairs)),
                }

    print(f"\n{name}")
    print(f"  extra_host_arc={extra_host_arc}")
    print(f"  core_outs={core_outs}")
    print(f"  requirements={requirements}")
    print(f"  active_prefixes={active_prefixes}")
    print(f"  low_cuts={low_details}")
    print(f"  total={total}")
    print(f"  success={success}")
    print(
        "  minimal_success_vectors="
        f"{minimal_success_vectors(distribution, requirements)}"
    )
    print(f"  first_success={first_success}")
    return {
        "core_outs": core_outs,
        "requirements": requirements,
        "success": success,
        "minimal_success_vectors": minimal_success_vectors(
            distribution, requirements
        ),
    }


def main():
    print("Monotone deficient cut-cover audit")
    original = scenario("D42 original")
    perturbed = scenario("D63 reverse-head perturbation", D63_EXTRA_HOST_ARC)

    assert original["core_outs"] == (1, 0, 1)
    assert original["requirements"] == (1, 2, 1)
    assert original["success"] == 84014
    assert original["minimal_success_vectors"] == [(1, 2, 1)]

    assert perturbed["core_outs"] == (2, 0, 1)
    assert perturbed["requirements"] == (0, 2, 1)
    assert perturbed["success"] > original["success"]
    assert perturbed["minimal_success_vectors"] == [(0, 2, 1)]

    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
