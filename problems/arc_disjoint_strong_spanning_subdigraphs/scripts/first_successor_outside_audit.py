"""Audit the outside quotient certificate for FSQ.

D72 proves FSQ from a smaller outside-core condition.  Let w1 be the
first chain successor and O'=O\\{w1}.  If C[O'] is 2-arc-strong, w1 has
exactly one outside exit, and O' has at least two arcs back to w1, then
the only outside cut of size below two is {w1}.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_kernel_witness import dbullet_arcs  # noqa: E402
from digraph import Digraph  # noqa: E402
from local_normal_form_audit import (  # noqa: E402
    D63_REVERSE_HEAD,
    D66_RHO_ENTRY,
    Q0,
    V2_HOST,
    all_subsets,
    host_from_db,
    out_edges,
    relabel_core_arcs,
)


W1 = 10
OUTSIDE = frozenset(V2_HOST) - Q0
OUTSIDE_CORE = OUTSIDE - {W1}


def core_edges(extras):
    db = tuple(dbullet_arcs()) + tuple(extras)
    host = tuple(host_from_db(db))
    core_arcs = relabel_core_arcs(host, V2_HOST)
    return tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)


def induced_lambda(edges, vertices):
    vertices = tuple(sorted(vertices))
    rel = {v: i for i, v in enumerate(vertices)}
    arcs = [(rel[u], rel[v]) for u, v in edges if u in rel and v in rel]
    return Digraph.from_arcs(range(len(vertices)), arcs).arc_connectivity()


def audit(name, extras):
    edges = core_edges(extras)
    w1_exits = sorted((u, v) for u, v in edges if u == W1 and v in OUTSIDE_CORE)
    returns = sorted((u, v) for u, v in edges if u in OUTSIDE_CORE and v == W1)
    outside_core_lambda = induced_lambda(edges, OUTSIDE_CORE)

    low_outside = []
    for B in all_subsets(OUTSIDE):
        outgoing = out_edges(edges, B, OUTSIDE)
        if len(outgoing) <= 1:
            low_outside.append((tuple(sorted(B)), tuple(outgoing)))

    assert outside_core_lambda >= 2, (name, outside_core_lambda)
    assert w1_exits == [(10, 23)], (name, w1_exits)
    assert len(returns) >= 2, (name, returns)
    assert low_outside == [((10,), ((10, 23),))], (name, low_outside)

    print(f"\n{name}")
    print(f"  extras={extras}")
    print(f"  outside_core_lambda={outside_core_lambda}")
    print(f"  w1_exits={w1_exits}")
    print(f"  returns_to_w1={returns}")
    print(f"  low_outside={low_outside}")


def main():
    print("First-successor outside audit")
    audit("D42 original", ())
    audit("D63 reverse-head", (D63_REVERSE_HEAD,))
    audit("D66 rho-entry", (D66_RHO_ENTRY,))
    audit("D63+D66 combined", (D63_REVERSE_HEAD, D66_RHO_ENTRY))
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
