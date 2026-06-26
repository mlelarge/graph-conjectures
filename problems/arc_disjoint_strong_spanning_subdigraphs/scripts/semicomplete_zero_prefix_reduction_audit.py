"""Audit the semicomplete zero-prefix reduction for D42/D63 cores.

D64 reduces pending repair to the actual deficient prefix list.  The next
structural question is how to prove that this list is complete.  This
script audits the purely semicomplete part of that proof.

Given a split semicomplete core C and a zero out-cut Q0, every cut S is
one of:

  * internal: S subset Q0;
  * external-prefix: Q0 subset S;
  * mixed: S meets both sides but neither contains nor is contained in Q0.

Since d_C^+(Q0)=0, mixed cuts have the exact decomposition

  d^+(A union B)
    = d^+_{Q0}(A, Q0\\A)
      + d^+_{O}(B, O\\B)
      + d^+(B, Q0\\A),

where A=S cap Q0, B=S\\Q0, and O=V(C)\\Q0.  Semicompleteness and
d^+(Q0)=0 force at least one arc b -> q for each b in B and q in Q0\\A,
so mixed cuts are automatically large except for the single-exchange
case |B|=|Q0\\A|=1.  The script verifies that even those exchange cuts
have out-size at least two in D42 and in the D63 reverse-head variant.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from d42_split_predicate_tester import (  # noqa: E402
    d42_split_setup,
    deficient_core_cuts,
    out_cut_size,
)


Q0 = frozenset((2, 3, 4, 5, 6, 7, 8))
Q_MINUS = frozenset((2, 3, 4, 5, 7, 8))
Q_PLUS = frozenset((2, 3, 4, 5, 6, 7, 8, 10))
D63_EXTRA_HOST_ARC = (7, 6)


def mask_for(v2, vertices):
    rel = {v: i for i, v in enumerate(v2)}
    return sum(1 << rel[v] for v in vertices)


def vertices_for(v2, mask):
    return frozenset(v2[i] for i in range(len(v2)) if (mask >> i) & 1)


def add_core_arc(core_arcs, rel, arc):
    u, v = arc
    extra = (rel[u], rel[v])
    assert extra not in set(core_arcs)
    return tuple(core_arcs) + (extra,)


def arc_count(core_edges, left, right):
    return sum(1 for u, v in core_edges if u in left and v in right)


def classify(side, q0):
    if side <= q0:
        return "internal"
    if q0 <= side:
        return "external-prefix"
    return "mixed"


def out_edges(core_edges, side):
    return sorted((u, v) for u, v in core_edges if u in side and v not in side)


def audit_scenario(name, extra_host_arc=None):
    v2, core_arcs, rel, _pending_vertices, _per_vertex = d42_split_setup()
    if extra_host_arc is not None:
        core_arcs = add_core_arc(core_arcs, rel, extra_host_arc)
    core_edges = tuple((v2[u], v2[v]) for u, v in core_arcs)
    universe = frozenset(v2)
    outside = universe - Q0

    q0_mask = mask_for(v2, Q0)
    qminus_mask = mask_for(v2, Q_MINUS)
    qplus_mask = mask_for(v2, Q_PLUS)
    assert out_cut_size(core_arcs, q0_mask) == 0

    low_cuts = [
        (out, vertices_for(v2, mask), classify(vertices_for(v2, mask), Q0))
        for mask, out in deficient_core_cuts(len(v2), core_arcs)
    ]

    internal_low = []
    external_low = []
    mixed_low = []
    min_mixed = None
    min_exchange = None
    formula_checked = 0

    for mask in range(1, (1 << len(v2)) - 1):
        side = vertices_for(v2, mask)
        out = out_cut_size(core_arcs, mask)
        kind = classify(side, Q0)
        if kind == "internal" and side != Q0 and out <= 1:
            internal_low.append((out, tuple(sorted(side)), out_edges(core_edges, side)))
        elif kind == "external-prefix" and side != Q0 and out <= 1:
            external_low.append((out, tuple(sorted(side)), out_edges(core_edges, side)))
        elif kind == "mixed":
            A = side & Q0
            B = side - Q0
            missing = Q0 - A
            outside_rest = outside - B
            formula = (
                arc_count(core_edges, A, missing)
                + arc_count(core_edges, B, outside_rest)
                + arc_count(core_edges, B, missing)
            )
            assert formula == out, (name, side, out, formula)
            formula_checked += 1
            lower = len(B) * len(missing)
            assert arc_count(core_edges, B, missing) >= lower
            row = (
                out,
                tuple(sorted(side)),
                len(B),
                len(missing),
                out_edges(core_edges, side),
            )
            if min_mixed is None or row < min_mixed:
                min_mixed = row
            if len(B) == 1 and len(missing) == 1:
                if min_exchange is None or row < min_exchange:
                    min_exchange = row
            if out <= 1:
                mixed_low.append(row)

    requirements = (
        max(0, 2 - out_cut_size(core_arcs, qminus_mask)),
        max(0, 2 - out_cut_size(core_arcs, q0_mask)),
        max(0, 2 - out_cut_size(core_arcs, qplus_mask)),
    )

    print(f"\n{name}")
    print(f"  extra_host_arc={extra_host_arc}")
    print(f"  low_cuts={[(out, tuple(sorted(side)), kind) for out, side, kind in low_cuts]}")
    print(f"  requirements(Q-,Q0,Q+)={requirements}")
    print(f"  internal_low={internal_low}")
    print(f"  external_low={external_low}")
    print(f"  mixed_low={mixed_low}")
    print(f"  min_mixed={min_mixed}")
    print(f"  min_exchange={min_exchange}")
    print(f"  mixed_formula_checked={formula_checked}")

    assert not mixed_low
    assert min_mixed[0] >= 2
    assert min_exchange is not None and min_exchange[0] >= 2
    assert all(set(row[1]) in (Q_MINUS,) for row in internal_low)
    assert all(set(row[1]) in (Q_PLUS,) for row in external_low)
    return {
        "low_cuts": low_cuts,
        "requirements": requirements,
        "internal_low": internal_low,
        "external_low": external_low,
        "min_mixed": min_mixed,
        "min_exchange": min_exchange,
    }


def main():
    print("Semicomplete zero-prefix reduction audit")
    original = audit_scenario("D42 original")
    perturbed = audit_scenario("D63 reverse-head perturbation", D63_EXTRA_HOST_ARC)

    assert original["requirements"] == (1, 2, 1)
    assert len(original["internal_low"]) == 1
    assert len(original["external_low"]) == 1

    assert perturbed["requirements"] == (0, 2, 1)
    assert not perturbed["internal_low"]
    assert len(perturbed["external_low"]) == 1

    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
