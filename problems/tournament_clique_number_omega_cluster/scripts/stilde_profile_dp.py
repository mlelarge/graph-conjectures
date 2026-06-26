"""Bottom-up generation of achievable B_k layer profiles via a grid path-DP.

A B_{d+1} order = three B_d module orders interleaved along a monotone lattice
path in {0..m}^3 (m=3^d).  This module tries to generate achievable parent
profiles from child orders by a DP over the grid that keeps, per cell, partial
parent orders deduplicated by their order-sensitive sequence of per-colour
longest-backward-chain rank triples.

Soundness note: at a fixed grid cell the placed vertex SET is identical across
paths (the first n_j of child j); only the order (hence ranks) differ.  Two
partials with rank_c(v) equal for all placed v and colours c are interchangeable
for the final HEIGHT triple, but NOT for the prefix/suffix STAIRCASES (which
depend on the order, not just the ranks).  combine_dp is exact for B_1->B_2
(validated: 0 mismatches).  At B_2->B_3, even the coarse rank-sequence signature
does NOT compress in the measured layers: the frontier is the full interleaving
count (1,2,6,...,1680=C(9;3,3,3),4200,11550,...).  See
docs/stilde_pod_tightness.md sec. 12: the *decision* layer Pareto-compresses to
a 16-frontier, but *generation* does not compress, because the prefix/suffix
profile is not closed under interleaving (the same wall as sec. 9.4).  This
module is therefore a validated reference / small-case oracle, not an L_6 engine.
"""

from __future__ import annotations

import itertools

from stilde_crossing_recursion import is_below
from stilde_pod_profiles import pod_profile, word
from stilde_profile_closure import reconstruct_order, step_profile


def _parent_id(child_index, local_vertex, m):
    return child_index * m + local_vertex


def combine_bruteforce(child_orders, inner_depth):
    """All achievable parent profiles by enumerating every interleaving path."""
    m = 3**inner_depth
    seen = {}
    # enumerate monotone paths as sequences of child choices (m of each)
    base = [0] * m + [1] * m + [2] * m
    for perm in set(itertools.permutations(base)):
        idx = [0, 0, 0]
        order = []
        for j in perm:
            order.append(_parent_id(j, child_orders[j][idx[j]], m))
            idx[j] += 1
        prof = step_profile(tuple(order), inner_depth + 1)
        seen.setdefault((prof.prefix, prof.suffix), prof)
    return list(seen.values())


def _rank_vector(order, depth):
    """rank_c(v) for every placed vertex v and colour c (longest backward chain
    ending at v); returned as a hashable nested tuple keyed by vertex."""
    pos = {v: i for i, v in enumerate(order)}
    ranks = {v: [1, 1, 1] for v in order}
    for i, v in enumerate(order):
        for u in order[:i]:  # u before v
            # backward arc v->u of colour c needs v <_{P_c} u
            for c in range(3):
                if is_below(v, u, depth, c):
                    if ranks[u][c] + 1 > ranks[v][c]:
                        ranks[v][c] = ranks[u][c] + 1
    return ranks


def combine_dp(child_orders, inner_depth, track_frontier=False):
    """Achievable parent profiles via grid DP, deduped by rank-triple sequence."""
    depth = inner_depth + 1
    m = 3**inner_depth
    # cell -> { rank_signature : partial_order(list) }
    start = (0, 0, 0)
    cells = {start: {(): []}}
    max_frontier = 0
    # process cells in increasing total size (topological on the grid)
    for total in range(3 * m):
        for n0 in range(min(total, m) + 1):
            for n1 in range(min(total - n0, m) + 1):
                n2 = total - n0 - n1
                if n2 < 0 or n2 > m:
                    continue
                cell = (n0, n1, n2)
                bucket = cells.get(cell)
                if not bucket:
                    continue
                if track_frontier:
                    max_frontier = max(max_frontier, len(bucket))
                for sig, order in bucket.items():
                    for j in range(3):
                        nj = cell[j]
                        if nj >= m:
                            continue
                        v = _parent_id(j, child_orders[j][nj], m)
                        new_order = order + [v]
                        nxt = tuple(cell[i] + (1 if i == j else 0) for i in range(3))
                        ranks = _rank_vector(new_order, depth)
                        new_sig = tuple(tuple(ranks[w]) for w in new_order)
                        cells.setdefault(nxt, {})
                        # dedup by rank signature (keep first; all equal for heights)
                        if new_sig not in cells[nxt]:
                            cells[nxt][new_sig] = new_order
        # free finished cells two layers back to save memory
    final = cells.get((m, m, m), {})
    seen = {}
    for order in final.values():
        prof = step_profile(tuple(order), depth)
        seen.setdefault((prof.prefix, prof.suffix), prof)
    result = list(seen.values())
    if track_frontier:
        return result, max_frontier
    return result


def _label_projection(profile, b):
    """Pieces of `profile` relevant when it plays label position b."""
    return profile.suffix[b], profile.prefix[(b - 1) % 3], profile.heights[(b + 1) % 3]


def _projection_dominates(a, b):
    """True if projection a is pointwise <= b (a dominates: makes any caps b makes)."""
    ga, fa, qa = a
    gb, fb, qb = b
    return (
        qa <= qb
        and all(x <= y for x, y in zip(ga, gb))
        and all(x <= y for x, y in zip(fa, fb))
    )


def compressed_labelsets(inner_depth):
    """Per-label Pareto-minimal B_{inner_depth} profile objects (decision frontier)."""
    from stilde_profile_closure import distinct_profiles

    profs = distinct_profiles(inner_depth)
    labelsets = []
    for b in range(3):
        rep = {}
        for p in profs:
            rep.setdefault(_label_projection(p, b), p)
        items = list(rep.items())
        keep = [
            p
            for (pr, p) in items
            if not any(pr2 != pr and _projection_dominates(pr2, pr) for (pr2, _) in items)
        ]
        labelsets.append(keep)
    return labelsets


def min_product_compressed(inner_depth, max_cap=8):
    """L_{inner_depth+1} via the Pareto-compressed profile-closure decision (no SAT)."""
    from stilde_profile_closure import reachable_under_caps

    labelsets = compressed_labelsets(inner_depth)
    candidates = sorted(
        itertools.product(range(1, max_cap + 1), repeat=3),
        key=lambda c: (c[0] * c[1] * c[2], c),
    )
    for caps in candidates:
        for triple in itertools.product(*labelsets):
            if reachable_under_caps(triple, caps)["reachable"]:
                return caps[0] * caps[1] * caps[2], caps, [len(s) for s in labelsets]
    return None


if __name__ == "__main__":
    # validate combine_dp against brute force on B_1 -> B_2 (inner_depth=1)
    import random
    rng = random.Random(0)
    perms = list(itertools.permutations(range(3)))
    mism = 0
    for _ in range(20):
        triple = [list(rng.choice(perms)) for _ in range(3)]
        bf = combine_bruteforce(triple, 1)
        dp = combine_dp(triple, 1)
        bf_set = {(p.prefix, p.suffix) for p in bf}
        dp_set = {(p.prefix, p.suffix) for p in dp}
        if bf_set != dp_set:
            mism += 1
            print("MISMATCH", triple, "bf", len(bf_set), "dp", len(dp_set))
    print(f"B_1->B_2 validation: {mism} mismatches over 20 triples")
