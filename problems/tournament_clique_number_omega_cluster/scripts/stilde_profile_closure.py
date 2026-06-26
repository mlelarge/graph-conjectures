"""Prefix/suffix profile closure for the layer heights of B_k = C3[B_{k-1}].

The crossing recursion in ``stilde_crossing_recursion.py`` still mentions the
global split position p.  This module factors that dependence into:

* the three induced orders inside the top modules M_0, M_1, M_2; and
* the monotone lattice path n(p) = (#M_0 before p, #M_1 before p, #M_2 before p).

For a fixed induced order sigma in one module, record for each colour c

    pref_c(a) = longest backward colour-c chain in the first a vertices of sigma
    suff_c(b) = longest backward colour-c chain in the last b vertices of sigma.

Then a cap triple q_c <= cap_c is feasible for the interleaving iff there is a
monotone path from (0,0,0) to (m,m,m), m=|B_{k-1}|, whose every state n satisfies

    suff^{M_c}_c(m - n_c) + pref^{M_{c+1}}_c(n_{c+1}) <= cap_c

for c=0,1,2, together with the far-module condition
q_c(M_{c+2}) <= cap_c.  This is the finite profile-closure object needed by
the open lambda > 3/2 route.
"""

from __future__ import annotations

import argparse
import itertools
from collections import deque
from dataclasses import dataclass
from functools import lru_cache

from stilde_crossing_recursion import direct_q, is_below
from stilde_pod_profiles import pod_profile


@dataclass(frozen=True)
class StepProfile:
    """All prefix/suffix chain staircases for one order of one B_depth copy."""

    depth: int
    order: tuple[int, ...]
    prefix: tuple[tuple[int, ...], ...]
    suffix: tuple[tuple[int, ...], ...]
    heights: tuple[int, int, int]


def profile_signature(profile):
    """Hashable profile data, excluding the witness order."""

    return profile.prefix, profile.suffix


@lru_cache(maxsize=None)
def relation_matrix(depth, colour):
    """Matrix for the canonical poset relation <_{P_colour} on B_depth."""

    expected = 3**depth
    return tuple(
        tuple(
            left != right and is_below(left, right, depth, colour)
            for right in range(expected)
        )
        for left in range(expected)
    )


def _prefix_suffix_for_colour(order, depth, colour):
    """Prefix and suffix height staircases for one colour.

    Prefixes are incremental.  Suffixes are recomputed by their left boundary;
    depth 2 then costs only small integer-matrix DP rather than repeated word
    decoding and sorting.
    """

    expected = len(order)
    relation = relation_matrix(depth, colour)

    prefix = [0] * (expected + 1)
    ranks = [0] * expected
    for right_index, vertex in enumerate(order):
        best = 1
        for left_index in range(right_index):
            if relation[vertex][order[left_index]]:
                best = max(best, ranks[left_index] + 1)
        ranks[right_index] = best
        prefix[right_index + 1] = max(prefix[right_index], best)

    suffix = [0] * (expected + 1)
    for start in range(expected - 1, -1, -1):
        local_ranks = [0] * expected
        height = 0
        for right_index in range(start, expected):
            vertex = order[right_index]
            best = 1
            for left_index in range(start, right_index):
                if relation[vertex][order[left_index]]:
                    best = max(best, local_ranks[left_index] + 1)
            local_ranks[right_index] = best
            height = max(height, best)
        suffix[expected - start] = height
    return tuple(prefix), tuple(suffix)


def step_profile(order, depth):
    """Return the per-colour prefix/suffix chain profiles of ``order``."""

    expected = 3**depth
    order = tuple(order)
    if sorted(order) != list(range(expected)):
        raise ValueError(f"order must be a permutation of range({expected})")

    prefixes = []
    suffixes = []
    for colour in range(3):
        prefix, suffix = _prefix_suffix_for_colour(order, depth, colour)
        prefixes.append(prefix)
        suffixes.append(suffix)
    heights = tuple(prefixes[colour][expected] for colour in range(3))
    return StepProfile(
        depth=depth,
        order=order,
        prefix=tuple(prefixes),
        suffix=tuple(suffixes),
        heights=heights,
    )


def module_orders(order, depth):
    """Induced lower-coordinate orders in the top modules of B_depth."""

    if depth <= 0:
        raise ValueError("module_orders requires depth >= 1")
    inner_size = 3 ** (depth - 1)
    modules = [[], [], []]
    for vertex in order:
        top = vertex // inner_size
        modules[top].append(vertex % inner_size)
    return tuple(tuple(module) for module in modules)


def lattice_path(order, depth):
    """The top-module count vector after each global prefix of ``order``."""

    if depth <= 0:
        raise ValueError("lattice_path requires depth >= 1")
    inner_size = 3 ** (depth - 1)
    counts = [0, 0, 0]
    states = [tuple(counts)]
    for vertex in order:
        counts[vertex // inner_size] += 1
        states.append(tuple(counts))
    return tuple(states)


def closure_heights(profiles, states):
    """Compute q_0,q_1,q_2 from module profiles and a monotone path."""

    if len(profiles) != 3:
        raise ValueError("profiles must be a length-3 sequence")
    depth = profiles[0].depth
    if any(profile.depth != depth for profile in profiles):
        raise ValueError("all profiles must have the same depth")

    m = 3**depth
    heights = []
    crossing = []
    for colour in range(3):
        cross = max(
            profiles[colour].suffix[colour][m - state[colour]]
            + profiles[(colour + 1) % 3].prefix[colour][state[(colour + 1) % 3]]
            for state in states
        )
        far = profiles[(colour + 2) % 3].heights[colour]
        crossing.append(cross)
        heights.append(max(far, cross))
    return tuple(heights), tuple(crossing)


def closure_details(order, depth):
    """Return profile-closure heights for a concrete order of B_depth."""

    modules = module_orders(order, depth)
    profiles = tuple(step_profile(module, depth - 1) for module in modules)
    states = lattice_path(order, depth)
    heights, crossing = closure_heights(profiles, states)
    direct = tuple(direct_q(order, depth, colour) for colour in range(3))
    return {
        "depth": depth,
        "module_orders": modules,
        "states": states,
        "heights": heights,
        "crossing": crossing,
        "direct_heights": direct,
    }


def state_ok(profiles, caps, state):
    """Whether one lattice state satisfies all profile cap inequalities."""

    caps = tuple(caps)
    m = 3 ** profiles[0].depth
    for colour in range(3):
        if profiles[(colour + 2) % 3].heights[colour] > caps[colour]:
            return False
        split_sum = (
            profiles[colour].suffix[colour][m - state[colour]]
            + profiles[(colour + 1) % 3].prefix[colour][state[(colour + 1) % 3]]
        )
        if split_sum > caps[colour]:
            return False
    return True


def reachable_under_caps(profiles, caps):
    """Find a monotone path satisfying the cap inequalities, if one exists."""

    depth = profiles[0].depth
    m = 3**depth
    start = (0, 0, 0)
    target = (m, m, m)
    if not state_ok(profiles, caps, start):
        return {"reachable": False, "path": None, "visited": 0}

    parents = {start: None}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        if state == target:
            path = []
            while state is not None:
                path.append(state)
                state = parents[state]
            path.reverse()
            return {
                "reachable": True,
                "path": tuple(path),
                "visited": len(parents),
            }
        for step in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            nxt = tuple(state[i] + step[i] for i in range(3))
            if any(value > m for value in nxt):
                continue
            if nxt in parents:
                continue
            if not state_ok(profiles, caps, nxt):
                continue
            parents[nxt] = state
            queue.append(nxt)
    return {"reachable": False, "path": None, "visited": len(parents)}


def reconstruct_order(module_orders_, path):
    """Build the global B_{d+1} order encoded by module orders and a path."""

    module_orders_ = tuple(tuple(order) for order in module_orders_)
    if len(module_orders_) != 3:
        raise ValueError("module_orders must be a length-3 sequence")
    m = len(module_orders_[0])
    if any(len(order) != m for order in module_orders_):
        raise ValueError("all module orders must have the same length")

    result = []
    previous = path[0]
    if previous != (0, 0, 0):
        raise ValueError("path must start at (0,0,0)")
    for state in path[1:]:
        delta = tuple(state[i] - previous[i] for i in range(3))
        if sorted(delta) != [0, 0, 1]:
            raise ValueError("path must take unit coordinate steps")
        module = delta.index(1)
        local_index = state[module] - 1
        result.append(module * m + module_orders_[module][local_index])
        previous = state
    if previous != (m, m, m):
        raise ValueError("path must end at (m,m,m)")
    return tuple(result)


def distinct_profiles(depth):
    """One witness for each distinct step profile of B_depth.

    This is intended for depth 0, 1, and occasionally 2.  Depth 2 enumerates
    9! orders and is still foreground-sized; depth 3 is not.
    """

    expected = 3**depth
    profiles = {}
    for order in itertools.permutations(range(expected)):
        profile = step_profile(order, depth)
        profiles.setdefault(profile_signature(profile), profile)
    return tuple(profiles.values())


def decide_caps_by_profile_closure(inner_depth, caps):
    """Decide B_{inner_depth+1} cap feasibility by profile closure."""

    profiles = distinct_profiles(inner_depth)
    tested = 0
    for triple in itertools.product(profiles, repeat=3):
        tested += 1
        reach = reachable_under_caps(triple, caps)
        if not reach["reachable"]:
            continue
        order = reconstruct_order(
            [profile.order for profile in triple],
            reach["path"],
        )
        outer_depth = inner_depth + 1
        direct_profile = pod_profile(order, outer_depth)
        assert all(
            height <= cap
            for height, cap in zip(direct_profile["layer_heights"], caps)
        )
        return {
            "inner_depth": inner_depth,
            "depth": outer_depth,
            "caps": tuple(caps),
            "sat": True,
            "profile_count": len(profiles),
            "tested_profile_triples": tested,
            "module_orders": tuple(profile.order for profile in triple),
            "path": reach["path"],
            "witness_order": order,
            "layer_heights": tuple(direct_profile["layer_heights"]),
        }
    return {
        "inner_depth": inner_depth,
        "depth": inner_depth + 1,
        "caps": tuple(caps),
        "sat": False,
        "profile_count": len(profiles),
        "tested_profile_triples": tested,
    }


def minimum_product_by_profile_closure(inner_depth, max_cap):
    """Search cap triples by product using the profile-closure decision."""

    checked = 0
    candidates = sorted(
        itertools.product(range(1, max_cap + 1), repeat=3),
        key=lambda caps: (caps[0] * caps[1] * caps[2], caps),
    )
    for caps in candidates:
        checked += 1
        result = decide_caps_by_profile_closure(inner_depth, caps)
        if result["sat"]:
            result["product"] = caps[0] * caps[1] * caps[2]
            result["checked_caps"] = checked
            return result
    return {
        "inner_depth": inner_depth,
        "depth": inner_depth + 1,
        "sat": False,
        "checked_caps": checked,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inner-depth", type=int, default=1)
    parser.add_argument("--caps", type=int, nargs=3)
    parser.add_argument("--minimum", action="store_true")
    parser.add_argument("--max-cap", type=int, default=4)
    args = parser.parse_args()

    if args.minimum:
        result = minimum_product_by_profile_closure(args.inner_depth, args.max_cap)
    elif args.caps is not None:
        result = decide_caps_by_profile_closure(args.inner_depth, tuple(args.caps))
    else:
        profiles = distinct_profiles(args.inner_depth)
        result = {
            "inner_depth": args.inner_depth,
            "profile_count": len(profiles),
            "height_profiles": sorted({profile.heights for profile in profiles}),
        }
    print(result)


if __name__ == "__main__":
    main()
