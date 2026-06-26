"""Audit the head-block orientation lemma used for HBQ.

D71 proves HBQ from a concrete orientation package around
Q0={u} union R union Z:

  * R is the cage reserve;
  * Z is the ordered escaped-head string ending at v;
  * u feeds every vertex of Z;
  * every vertex of Z hooks into every vertex of R;
  * earlier Z vertices point to later Z vertices;
  * the cage reserve has C7-style expansion toward {u} union R.

This script checks those axioms and the resulting low-complement list on
the D42/D63/D66 variants.
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
from local_normal_form_audit import (  # noqa: E402
    D63_REVERSE_HEAD,
    D66_RHO_ENTRY,
    Q0,
    V2_HOST,
    all_subsets,
    host_from_db,
    relabel_core_arcs,
)


U = 2
RESERVE = frozenset((3, 4, 5))
HEAD_STRING = (6, 7, 8)
CAGE = frozenset((U,)) | RESERVE


def core_edges(extras):
    db = tuple(dbullet_arcs()) + tuple(extras)
    host = tuple(host_from_db(db))
    core_arcs = relabel_core_arcs(host, V2_HOST)
    return tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)


def powerset_nonempty(vertices):
    vertices = tuple(sorted(vertices))
    for mask in range(1, 1 << len(vertices)):
        yield frozenset(vertices[i] for i in range(len(vertices)) if (mask >> i) & 1)


def arcs_between(edges, left, right):
    left = set(left)
    right = set(right)
    return sorted((u, v) for u, v in edges if u in left and v in right)


def audit(name, extras):
    edges = core_edges(extras)
    edge_set = set(edges)

    root_fan = [(U, z) for z in HEAD_STRING]
    head_hooks = [(z, r) for z in HEAD_STRING for r in sorted(RESERVE)]
    head_order = [
        (HEAD_STRING[i], HEAD_STRING[j])
        for i in range(len(HEAD_STRING))
        for j in range(i + 1, len(HEAD_STRING))
    ]
    reserve_rows = [
        (tuple(sorted(P)), tuple(arcs_between(edges, P, CAGE - P)))
        for P in powerset_nonempty(RESERVE)
    ]

    assert all(e in edge_set for e in root_fan), (name, "root_fan", root_fan)
    assert all(e in edge_set for e in head_hooks), (name, "head_hooks")
    assert all(e in edge_set for e in head_order), (name, "head_order", head_order)
    assert all(len(row[1]) >= 2 for row in reserve_rows), (name, reserve_rows)

    low_complements = []
    for T in all_subsets(Q0):
        incoming = arcs_between(edges, Q0 - T, T)
        if len(incoming) <= 1:
            low_complements.append((tuple(sorted(T)), tuple(incoming)))

    reverse_head = D63_REVERSE_HEAD in extras
    expected = [] if reverse_head else [((6,), ((2, 6),))]
    assert low_complements == expected, (name, low_complements)

    print(f"\n{name}")
    print(f"  extras={extras}")
    print(f"  root_fan={root_fan}")
    print(f"  head_order={head_order}")
    print(f"  min_reserve_expansion={min(len(row[1]) for row in reserve_rows)}")
    print(f"  low_head_complements={low_complements}")


def main():
    print("Head-block orientation audit")
    audit("D42 original", ())
    audit("D63 reverse-head", (D63_REVERSE_HEAD,))
    audit("D66 rho-entry", (D66_RHO_ENTRY,))
    audit("D63+D66 combined", (D63_REVERSE_HEAD, D66_RHO_ENTRY))
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
