"""The q_0=1 face: F_k = min{ q_1 q_2 : q_0 = 1 } and its Pareto frontier.

F_k is an upper bound on L_k (the face is a sub-family), is submultiplicative,
and lambda_F = lim F_k^{1/k} = 3/2 would prove pod-tightness lambda = 3/2.
See docs/stilde_pod_tightness.md sec. 15.

Exact: F_1..F_6 = 2, 4, 8, 15, 25, 45.  F_6 is certified by the
boundary-cut lower bound in ``certify_F6_face_exact`` plus the explicit
``(1,5,9)`` construction.
"""

from __future__ import annotations

import itertools

from decide_layer_labeling import decide_caps_labeling
from stilde_profile_closure import step_profile


def face_min_product(depth, max_cap=None, solver=None):
    """F_depth = min b*c over SAT cap triples (1, b, c) (scan by product)."""
    max_cap = max_cap or 2**depth
    cands = sorted(
        ((b, c) for b in range(1, max_cap + 1) for c in range(1, max_cap + 1)),
        key=lambda bc: (bc[0] * bc[1], bc),
    )
    for b, c in cands:
        kwargs = {"solver_type": solver} if solver else {}
        r = decide_caps_labeling(depth, (1, b, c), **kwargs)
        if r["sat"]:
            return b * c, (1, b, c), r["witness_order"]
    return None


def face_profile(profile):
    """Face-relevant staircases of an order: (pre_1, suf_1, pre_2, suf_2)."""
    return (
        profile.prefix[1],
        profile.suffix[1],
        profile.prefix[2],
        profile.suffix[2],
    )


def _dominates(a, b):
    return all(all(x <= y for x, y in zip(sa, sb)) for sa, sb in zip(a, b))


def face_pareto_frontier(depth):
    """Exhaustive Pareto-minimal face profiles over all q_0=1 orders of B_depth.

    Intended for depth <= 2 (depth 2 enumerates 9! orders)."""
    n = 3**depth
    reps = {}
    for order in itertools.permutations(range(n)):
        prof = step_profile(list(order), depth)
        if prof.heights[0] == 1:
            reps.setdefault(face_profile(prof), prof.heights)
    items = list(reps.items())
    keep = [
        (fp, h)
        for fp, h in items
        if not any(fp2 != fp and _dominates(fp2, fp) for fp2, _ in items)
    ]
    return {
        "depth": depth,
        "q0_orders": "see distinct",
        "distinct_face_profiles": len(items),
        "pareto_minimal": len(keep),
        "height_pairs": sorted({h[1:] for _, h in keep}),
    }


if __name__ == "__main__":
    for depth in range(1, 5):
        product, caps, _ = face_min_product(depth)
        print(f"F_{depth} = {product:3d}  optimum {caps}")
    print(face_pareto_frontier(2))
