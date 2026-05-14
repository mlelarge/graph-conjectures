"""Hand-constructed CDC attempts for flower snarks J_n, n = 2k+1.

Per [cdc_gadget_plan.md](../docs/cdc_gadget_plan.md) §"Phase 2", the
goal is a uniform parametric weighted-CDC certificate for the flower
family. This module exposes candidate CDC constructions as functions
of ``k`` and validates each via ``cdc.cdc_summary`` before any
downstream weighted-CDC solve.

Validation gate: every candidate must have ``all_edges_covered_twice
== True`` for k in {2, 3, 4, 5, 6}. If any candidate fails the gate,
it is documented as a failed attempt and not fed to the solver.

Notation. Vertices in the labelled flower constructor
:func:`graphs.flower_snark_with_labels` carry integer labels assigned by
sorted ``(type, index)`` tuple. To build CDC cycles in human-readable
form, we keep the labelled tuple form ``("a", i)``, ``("b", i)``, etc.
and translate to integers via the same canonical relabel.
"""
from __future__ import annotations

from typing import Iterable

import networkx as nx

from graphs import flower_snark_with_labels


def _flower_relabel(k: int) -> dict[tuple, int]:
    """Reproduce the integer relabel used by ``flower_snark_with_labels``."""
    n = 2 * k + 1
    nodes: list[tuple] = []
    for i in range(n):
        nodes.append(("a", i))
        nodes.append(("b", i))
        nodes.append(("c", i))
        nodes.append(("d", i))
    nodes = sorted(nodes)
    return {node: idx for idx, node in enumerate(nodes)}


def _to_int_cycle(path: list[tuple], relabel: dict[tuple, int]) -> tuple:
    return tuple(relabel[v] for v in path)


def flower_cdc_v1(k: int) -> list[tuple]:
    """Attempt v1: b-cycle + cd-cycle + bc-shuttles + bd-shuttles
    for every i in Z/n. *Expected to over-cover internal a_i b_i spokes
    by a factor of 2*, kept here as documented failure.
    """
    n = 2 * k + 1
    relabel = _flower_relabel(k)
    cycles_abs: list[list[tuple]] = []

    # b-cycle: b_0 b_1 ... b_{n-1}
    cycles_abs.append([("b", i) for i in range(n)])

    # cd-cycle: c_0 c_1 ... c_{n-1} d_0 d_1 ... d_{n-1}
    cycles_abs.append(
        [("c", i) for i in range(n)] + [("d", i) for i in range(n)]
    )

    # bc-shuttle at i (i = 0..n-2):
    #   a_i, b_i, b_{i+1}, a_{i+1}, c_{i+1}, c_i  (length 6)
    for i in range(n - 1):
        cycles_abs.append([
            ("a", i), ("b", i), ("b", i + 1),
            ("a", i + 1), ("c", i + 1), ("c", i),
        ])

    # bd-shuttle at i (i = 0..n-2):
    for i in range(n - 1):
        cycles_abs.append([
            ("a", i), ("b", i), ("b", i + 1),
            ("a", i + 1), ("d", i + 1), ("d", i),
        ])

    return [_to_int_cycle(c, relabel) for c in cycles_abs]


def flower_cdc_v2(k: int) -> list[tuple]:
    """Attempt v2: drop the explicit b-cycle and use only bc + bd shuttles
    (so each b-cycle edge appears in exactly two shuttles via the
    consecutive ``i, i-1`` pair). Wrap-around at ``i = n-1`` is handled
    by routing through ``c_{n-1} d_0`` and ``d_{n-1} c_0`` cross edges.
    *Expected to over-cover a-b spokes for internal ``i``.*
    """
    n = 2 * k + 1
    relabel = _flower_relabel(k)
    cycles_abs: list[list[tuple]] = []

    # bc-shuttle at i for i = 0..n-2: a_i, b_i, b_{i+1}, a_{i+1}, c_{i+1}, c_i
    for i in range(n - 1):
        cycles_abs.append([
            ("a", i), ("b", i), ("b", i + 1),
            ("a", i + 1), ("c", i + 1), ("c", i),
        ])
    # Wrap bc: a_{n-1}, b_{n-1}, b_0, a_0, c_0, d_{n-1}, c_{n-1}   (length 7)
    cycles_abs.append([
        ("a", n - 1), ("b", n - 1), ("b", 0),
        ("a", 0), ("c", 0), ("d", n - 1), ("c", n - 1),
    ])
    # bd-shuttle at i for i = 0..n-2: a_i, b_i, b_{i+1}, a_{i+1}, d_{i+1}, d_i
    for i in range(n - 1):
        cycles_abs.append([
            ("a", i), ("b", i), ("b", i + 1),
            ("a", i + 1), ("d", i + 1), ("d", i),
        ])
    # Wrap bd: a_{n-1}, b_{n-1}, b_0, a_0, d_0, c_{n-1}, d_{n-1}   (length 7)
    cycles_abs.append([
        ("a", n - 1), ("b", n - 1), ("b", 0),
        ("a", 0), ("d", 0), ("c", n - 1), ("d", n - 1),
    ])

    return [_to_int_cycle(c, relabel) for c in cycles_abs]


CANDIDATES: dict[str, callable] = {
    "v1_bplus_cdplus_bcshuttles_bdshuttles": flower_cdc_v1,
    "v2_bcshuttles_bdshuttles_only": flower_cdc_v2,
}


def validate_candidate(name: str, builder, ks: Iterable[int] = (2, 3, 4, 5, 6)) -> dict:
    """Run ``cdc_summary`` for each k. Report which (if any) pass."""
    from cdc import cdc_summary

    results: dict[int, dict] = {}
    for k in ks:
        G, _ = flower_snark_with_labels(k)
        cdc = builder(k)
        try:
            summary = cdc_summary(cdc, G)
            results[k] = summary
        except Exception as exc:
            results[k] = {"error": f"{type(exc).__name__}: {exc}"}
    passing = [k for k, s in results.items() if s.get("all_edges_covered_twice")]
    return {"name": name, "results": results, "k_pass": passing, "k_tried": list(ks)}


if __name__ == "__main__":
    for name, builder in CANDIDATES.items():
        print(f"=== {name} ===")
        rep = validate_candidate(name, builder)
        for k, s in rep["results"].items():
            ok = s.get("all_edges_covered_twice")
            bad = len(s.get("bad_edges", [])) if "bad_edges" in s else "?"
            ncyc = s.get("n_cycles", "?")
            print(f"  k={k} (n={2*k+1}): n_cycles={ncyc}, all_2x_covered={ok}, bad_edges={bad}")
        print(f"  passing k: {rep['k_pass']}")
        print()
