"""Recursive construction on the q_0=1 face: build q_0=1 orders of B_k from a
bounded Pareto-(q1,q2) frontier of B_{k-1} orders, and track F_k = min q1*q2.

Decoded structure (docs sec. 15): parent (1,A,B) = M_0(1,A,b0) | M_1(1,a1,B)
with M_2(1,A,B) split; parent height = (1, q1(M_0), q2(M_1)).  We evaluate every
(triple, M_2-split) by the crossing recursion (closure_heights), keep the
Pareto-(q1,q2) frontier, and step_profile only the kept representatives so the
next level has profiles.  This is a heuristic upper bound on F_k (bounded
frontier); it reproduces F_2=4 and F_3=8 but stalls at 16 for depth 4, above the
exact F_4=15 that needs a finer M_2 interleaving.
"""

from __future__ import annotations

import itertools

from stilde_profile_closure import (
    closure_heights,
    module_orders,
    reconstruct_order,
    step_profile,
)


def face_paths(m):
    """Lattice paths for q_0=1 arrangements: M_0 before M_1, M_2 split.

    Yields several split patterns of M_2 (prefix before M_0, suffix after M_1,
    plus a middle and a 2-cut interleave)."""
    patterns = []
    for s in range(m + 1):  # ALL 2-cut splits (a clean 2-cut reaches F_4=15)
        # [M_2[:s]] [M_0] [M_1] [M_2[s:]]
        st = [(0, 0, 0)]
        for j in range(1, s + 1):
            st.append((0, 0, j))
        for i in range(1, m + 1):
            st.append((i, 0, s))
        for j in range(1, m + 1):
            st.append((m, j, s))
        for j in range(s + 1, m + 1):
            st.append((m, m, j))
        patterns.append(tuple(st))
    # [M_0] [M_2] [M_1]  (M_2 entirely between)
    st = [(0, 0, 0)]
    for i in range(1, m + 1):
        st.append((i, 0, 0))
    for j in range(1, m + 1):
        st.append((m, 0, j))
    for j in range(1, m + 1):
        st.append((m, j, m))
    patterns.append(tuple(st))
    return patterns


def build(max_depth, cap_per_shape=3, max_shapes=60):
    """Return {depth: {(q1,q2): [(face_profile_key, StepProfile, order), ...]}}."""
    # level 1: q_0=1 orders of B_1
    frontier = {}
    lvl1 = []
    for o in itertools.permutations(range(3)):
        p = step_profile(list(o), 1)
        if p.heights[0] == 1:
            lvl1.append(p)
    frontier[1] = _pareto(lvl1, cap_per_shape, max_shapes)
    results = {1: min(p.heights[1] * p.heights[2] for p in lvl1)}

    for depth in range(2, max_depth + 1):
        m = 3 ** (depth - 1)
        reps = [p for shape in frontier[depth - 1].values() for p in shape]
        paths = face_paths(m)
        best = {}  # (q1,q2) -> (product, m0,m1,m2, path)
        for m0, m1, m2 in itertools.product(reps, repeat=3):
            for path in paths:
                h, _ = closure_heights([m0, m1, m2], path)
                if h[0] != 1:
                    continue
                key = (h[1], h[2])
                prod = h[1] * h[2]
                if key not in best or prod < best[key][0]:
                    best[key] = (prod, m0, m1, m2, path)
        # reconstruct + profile the kept (Pareto) shapes
        profs = []
        for key, (prod, m0, m1, m2, path) in best.items():
            order = reconstruct_order([m0.order, m1.order, m2.order], path)
            pr = step_profile(order, depth)
            assert pr.heights[0] == 1 and (pr.heights[1], pr.heights[2]) == key, (
                pr.heights, key)
            profs.append(pr)
        frontier[depth] = _pareto(profs, cap_per_shape, max_shapes)
        results[depth] = min(p.heights[1] * p.heights[2] for p in profs)
        if _VERBOSE:
            exact = {1: 2, 2: 4, 3: 8, 4: 15, 5: 25}
            r = results[depth] / results[depth - 1]
            print(f"  depth {depth}: F^constr={results[depth]:4d}  "
                  f"exact={exact.get(depth,'?'):>3}  ratio={r:.3f}  "
                  f"(3/2)^k={1.5**depth:.1f}  #shapes={len(frontier[depth])}",
                  flush=True)
    return results, frontier


_VERBOSE = False


def _face_key(p):
    return (p.prefix[1], p.suffix[1], p.prefix[2], p.suffix[2])


def _dom(a, b):
    return all(all(x <= y for x, y in zip(sa, sb)) for sa, sb in zip(a, b))


def _pareto(profiles, cap_per_shape, max_shapes):
    """Keep Pareto-minimal face profiles, capped per (q1,q2) shape and overall."""
    by_shape = {}
    for p in profiles:
        by_shape.setdefault((p.heights[1], p.heights[2]), []).append(p)
    out = {}
    for shape, ps in by_shape.items():
        keys = [(_face_key(p), p) for p in ps]
        keep = [p for k, p in keys
                if not any(k2 != k and _dom(k2, k) for k2, _ in keys)]
        # dedup identical face keys, cap
        seen = set()
        uniq = []
        for p in keep:
            fk = _face_key(p)
            if fk not in seen:
                seen.add(fk)
                uniq.append(p)
        out[shape] = uniq[:cap_per_shape]
    # cap total shapes by product (keep the cheapest shapes)
    shapes = sorted(out, key=lambda s: s[0] * s[1])[:max_shapes]
    return {s: out[s] for s in shapes}


if __name__ == "__main__":
    import time
    t = time.time()
    res, _ = build(6, cap_per_shape=3, max_shapes=60)
    exact = {1: 2, 2: 4, 3: 8, 4: 15, 5: 25}
    print(f"depth  F_k^constr  F_k(exact)  ratio  (3/2)^k  ({time.time()-t:.0f}s)")
    for k in sorted(res):
        e = exact.get(k, "?")
        r = res[k] / res[k - 1] if k > 1 else None
        print(f"  {k}     {res[k]:5d}      {e:>3}      "
              f"{('%.3f' % r) if r else '  -  '}    {1.5**k:.1f}")
