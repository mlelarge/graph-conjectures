"""Constructive F_6 upper bound via the portfolio 2-cut (docs sec 27).

The clean 2-cut  M_2[:s] | M_0 | M_1 | M_2[s:]  of three depth-5 face modules
produces a VALID depth-6 face order (q_0 = 1 automatic, sec 17).  So any target
(A,B) for which the three modules exist at depth 5 gives F_6 <= A*B by explicit
construction -- a route the direct depth-6 face SAT could not reach (sec 11.10).

This makes "companion regeneration" (sec 27) concrete and finite: target (A,B)
with slack (r1, r2) needs
    M_2 = (1, A, B)        self-similar / balanced     product A*B
    M_0 = (1, A, B - r2)   cheap in colour 2           product A*(B-r2)
    M_1 = (1, A - r1, B)   cheap in colour 1           product (A-r1)*B
to EXIST at depth 5, i.e. each cap must be realizable (necessarily product
>= F_5 = 25).  Among the constructible targets, the minimum actual parent product
is the portfolio upper bound on F_6.  Its position vs (3/2)^6 = 11.39 is the
evidence: a ratio F_6 / (3/2)^6 below the F_5 ratio (3.29) leans pod-tight.
"""

from __future__ import annotations

import functools
import itertools
import json
import os

from decide_layer_labeling import decide_caps_labeling
from stilde_pod_profiles import pod_profile
from stilde_profile_closure import step_profile
from stilde_face_2cut import (
    order_2cut, parent_heights_2cut, portfolio_cut_certificates,
)

DEPTH = 5            # module depth; parent is depth 6
F5 = 25              # face optimum at depth 5
SLACKS = [(1, 2), (2, 1), (1, 1), (2, 2), (2, 3), (3, 2)]


@functools.lru_cache(maxsize=None)
def witness_profile(depth, caps):
    """An ARBITRARY depth-`depth` face module under caps (scalars only), or None."""
    result = decide_caps_labeling(depth, caps)
    if not result["sat"]:
        return None
    return step_profile(list(result["witness_order"]), depth)


def module_profile(caps):
    return witness_profile(DEPTH, caps)


@functools.lru_cache(maxsize=None)
def structured_build(A, B, depth, base_depth=3):
    """A depth-`depth` self-similar M_2 of heights (1,A,B) built RECURSIVELY by
    portfolio 2-cuts, so it carries the prefix/suffix staircase structure a parent
    needs.  Companions (M_0,M_1) at each level are arbitrary witnesses (they enter
    as scalars).  Returns the StepProfile, or None if regeneration breaks.

    The recursion is the actual sec-27 companion/M_2 regeneration: keep the
    self-similar shape (A,B) fixed while descending, paying arbitrary cheap
    companions at every level, and check a simultaneous small cut survives.
    """
    if depth <= base_depth:
        return witness_profile(depth, (1, A, B))  # leaf: arbitrary witness
    m2 = structured_build(A, B, depth - 1, base_depth)
    if m2 is None:
        return None
    for r1, r2 in SLACKS:
        if A - r1 < 1 or B - r2 < 1:
            continue
        m0 = witness_profile(depth - 1, (1, A, B - r2))
        m1 = witness_profile(depth - 1, (1, A - r1, B))
        if m0 is None or m1 is None:
            continue
        certs = portfolio_cut_certificates(m0, m1, m2, target=(A, B))
        if certs:
            order = order_2cut(m0, m1, m2, certs[0].cut)
            return step_profile(order, depth)
    return None


def try_target(A, B, r1, r2):
    """Construct a depth-6 face order with parent heights <= (1,A,B), if possible."""
    if (A - r1) < 1 or (B - r2) < 1:
        return None
    # Necessary regeneration condition: companions must clear the F_5 floor.
    if A * (B - r2) < F5 or (A - r1) * B < F5:
        return None
    m2 = module_profile((1, A, B))
    m0 = module_profile((1, A, B - r2))
    m1 = module_profile((1, A - r1, B))
    if m2 is None or m0 is None or m1 is None:
        return None
    certs = portfolio_cut_certificates(m0, m1, m2, target=(A, B))
    if not certs:
        return None
    # pick the cut giving the smallest actual parent product
    best = None
    for cert in certs:
        q1, q2 = parent_heights_2cut(m0, m1, m2, cert.cut)
        if best is None or q1 * q2 < best[0]:
            best = (q1 * q2, cert.cut, q1, q2)
    product, cut, q1, q2 = best
    return {
        "target": (A, B), "slack": (r1, r2), "cut": cut,
        "module_heights": [m0.heights, m1.heights, m2.heights],
        "module_products": [m0.heights[1] * m0.heights[2],
                            m1.heights[1] * m1.heights[2],
                            m2.heights[1] * m2.heights[2]],
        "parent_heights": (1, q1, q2), "parent_product": product,
    }


def certify(record):
    """Rebuild the full depth-6 order and verify heights via pod_profile."""
    A, B = record["target"]
    r1, r2 = record["slack"]
    m2 = module_profile((1, A, B))
    m0 = module_profile((1, A, B - r2))
    m1 = module_profile((1, A - r1, B))
    order = order_2cut(m0, m1, m2, record["cut"])
    prof = pod_profile(order, 6)
    record["certified_heights"] = tuple(prof["layer_heights"])
    record["certified_product"] = prof["height_product"]
    record["certified_q0_is_1"] = prof["layer_heights"][0] == 1
    return record


def simultaneous_cuts(m2, r1, r2):
    """Cuts s of M_2 with pre_1(M_2,s) <= r1 AND suf_2(M_2,m-s) <= r2."""
    m = 3 ** m2.depth
    return [s for s in range(m + 1)
            if m2.prefix[1][s] <= r1 and m2.suffix[2][m - s] <= r2]


def diagnose():
    """Localize the sec-27 regeneration obstruction concretely.

    (1) the three (5,7)-portfolio companions all EXIST at depth 5 (not the issue);
    (2) an ARBITRARY (1,5,7)@5 witness gives a blown-up 2-cut (q2 stacks);
    (3) the STRUCTURED depth-5 optimum (1,5,5) has NO simultaneous (<=2,<=2) cut,
        so it cannot serve as M_2 to grow a depth-6 parent.
    Hence regeneration is entirely about M_2's simultaneous-cut structure.
    """
    import json
    facts = {}

    comp = {c: witness_profile(5, c) for c in [(1, 5, 7), (1, 5, 5), (1, 4, 7)]}
    facts["companions_57_exist"] = {str(c): (p.heights if p else None)
                                    for c, p in comp.items()}

    m2_arb = comp[(1, 5, 7)]
    m0, m1 = comp[(1, 5, 5)], comp[(1, 4, 7)]
    m = 3 ** 5
    best = min((parent_heights_2cut(m0, m1, m2_arb, s) for s in range(m + 1)),
               key=lambda qq: qq[0] * qq[1])
    facts["arbitrary_M2_best_2cut"] = {"heights": (1, *best),
                                       "product": best[0] * best[1]}

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "L5_refutation.json")
    with open(data_path, encoding="utf-8") as handle:
        order = json.load(handle)["witnesses"]["(1, 5, 5)"]["order"]
    m2_struct = step_profile(list(order), 5)
    facts["structured_1_5_5_simultaneous_cuts"] = {
        f"({r1},{r2})": len(simultaneous_cuts(m2_struct, r1, r2))
        for r1, r2 in [(1, 2), (2, 2), (2, 3), (3, 3)]
    }
    return facts


def run(a_range=range(4, 9), b_range=range(4, 9), max_product=44):
    targets = sorted(
        {(A, B) for A in a_range for B in b_range if A * B <= max_product},
        key=lambda t: (t[0] * t[1], t),
    )
    found = []
    for A, B in targets:
        hit = None
        for r1, r2 in SLACKS:
            rec = try_target(A, B, r1, r2)
            if rec is not None:
                if hit is None or rec["parent_product"] < hit["parent_product"]:
                    hit = rec
        if hit is not None:
            found.append(hit)
            print(
                f"target=({A},{B}) slack={hit['slack']} cut={hit['cut']} "
                f"modules={hit['module_heights']} "
                f"-> parent {hit['parent_heights']} product={hit['parent_product']}",
                flush=True,
            )
    found.sort(key=lambda r: r["parent_product"])
    print(f"\n{len(found)} constructible targets", flush=True)
    if found:
        best = certify(dict(found[0]))
        print(f"\nbest portfolio F_6 bound: {best['parent_product']}", flush=True)
        print(f"  certified depth-6 heights: {best['certified_heights']} "
              f"product={best['certified_product']} q0=1:{best['certified_q0_is_1']}",
              flush=True)
        ratio = best["certified_product"] / 1.5 ** 6
        print(f"  F_6 <= {best['certified_product']};  /(3/2)^6 = {ratio:.3f} "
              f"(F_5 ratio = {F5 / 1.5 ** 5:.3f})", flush=True)
        out = {"best": best, "all_constructible": found}
        with open("data/portfolio_f6_bound.json", "w") as handle:
            json.dump(out, handle, indent=2, default=list)
        print("wrote data/portfolio_f6_bound.json", flush=True)
    return found


if __name__ == "__main__":
    run()
