"""Show that current DT does not imply the top-support clause.

D77's next target says "prove top-support two-exit from DT/root-spare
support."  This audit separates the current DT theorem from the stronger
support-ladder endpoint needed for AOC: the two D76 top-support reversals
preserve the DT counting profile exactly, but fail top-support and AOC.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

import networkx as nx

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from attached_outside_cut_audit import (  # noqa: E402
    OUTSIDE_CORE,
    W1,
    arcs_between,
    core_edges,
)
from aoc_reversal_redteam import aoc_profile  # noqa: E402
from chain_feed_deletion_stress import structural_gates  # noqa: E402
from chain_kernel_witness import dbullet_arcs  # noqa: E402


N_DB = 23
ROOT = 0
U = 1
V = 7
BAD_REVERSALS = (
    ((22, 20), (20, 22)),
    ((22, 21), (21, 22)),
)


def reverse_once(base, delete_arc, add_arc):
    arcs = list(base)
    arcs.remove(delete_arc)
    arcs.append(add_arc)
    return tuple(arcs)


def dt_profile(arcs):
    mult = Counter(arcs)
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(N_DB))
    graph.add_edges_from(arcs)
    graph_minus_u = graph.copy()
    graph_minus_u.remove_node(U)
    path = nx.shortest_path(graph_minus_u, V, ROOT)

    x_set = set(range(N_DB)) - {ROOT} - set(path[:-1])
    while True:
        induced = nx.DiGraph((x, y) for (x, y) in mult if x in x_set and y in x_set)
        induced.add_nodes_from(x_set)
        bad = {x for x in x_set - {U} if not nx.has_path(induced, x, U)}
        if not bad:
            break
        x_set -= bad

    rho_tails = sorted({x for (x, y) in mult if y == ROOT})
    tails = sorted(
        {
            x
            for (x, y) in mult
            if x in x_set and y not in x_set and (x, y) != (U, V)
        }
    )
    return {
        "path": tuple(path),
        "rho_tails": tuple(rho_tails),
        "rho_tails_on_path": tuple(r for r in rho_tails if r in path),
        "rho_tails_in_XP": tuple(r for r in rho_tails if r in x_set),
        "boundary_tails": tuple(tails),
    }


def top_support_ok(arcs):
    edges = core_edges(arcs)
    w1_exits = arcs_between(edges, {W1}, OUTSIDE_CORE)
    assert len(w1_exits) == 1
    tau = w1_exits[0][1]
    tau_exits = arcs_between(edges, {tau}, OUTSIDE_CORE - {tau})
    return tau, tau_exits, len(tau_exits) >= 2


def main():
    base = tuple(dbullet_arcs())
    base_dt = dt_profile(base)
    rows = []
    for name, arcs in [("D42 original", base)] + [
        (f"{delete_arc}->{add_arc}", reverse_once(base, delete_arc, add_arc))
        for delete_arc, add_arc in BAD_REVERSALS
    ]:
        gates = structural_gates(arcs)
        profile = dt_profile(arcs)
        tau, tau_exits, top_ok = top_support_ok(arcs)
        aoc = aoc_profile(arcs)
        assert gates["structural_ok"], name
        assert profile == base_dt, (name, profile, base_dt)
        rows.append((name, profile, tau, tau_exits, top_ok, aoc["ok"]))

    assert rows[0][4] and rows[0][5]
    assert all(not row[4] and not row[5] for row in rows[1:])

    print("Top-support vs current DT gap audit")
    for name, profile, tau, tau_exits, top_ok, aoc_ok in rows:
        print(f"\n{name}")
        print(f"  DT path={profile['path']}")
        print(f"  DT rho_tails={profile['rho_tails']}")
        print(f"  DT rho_tails_on_path={profile['rho_tails_on_path']}")
        print(f"  DT rho_tails_in_XP={profile['rho_tails_in_XP']}")
        print(f"  tau={tau} tau_exits={tau_exits}")
        print(f"  top_support_ok={top_ok} AOC_ok={aoc_ok}")
    print("\nALL ASSERTIONS PASS: current DT does not imply top-support")


if __name__ == "__main__":
    main()
