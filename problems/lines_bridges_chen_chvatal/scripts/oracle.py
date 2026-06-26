"""Oracle CLI + benchmark for arXiv:1606.06011 (lines + bridges).

The Chen-Chvatal "lines" inequality:
        ell(G) + br(G)  >=  |G| = n
for every connected graph G, where ell(G) = number of distinct (metric) lines
and br(G) = number of bridges.  A COUNTER-EXAMPLE is a connected G with
        ell(G) + br(G) < n.

The open question (paper's Conjecture 2.2 / "finite generating family"):
every counter-example arises from a FINITE list of graphs by replacing a bridge
with a path.  That asymptotic statement is NOT itself decidable by finite
enumeration -- but the underlying testable property and the *discovery of every
small counter-example* (classified bridgeless vs bridge-containing, and whether
a new minimal bridge counter-example appears beyond the known three) IS fully
oracle-able with EXACT BFS-distance combinatorics.

Two jobs:
  1. check_construction(n, edges): the workhorse the agent calls to GROUND a
     proposal -- verifies connectivity and reports the EXACT ell, br, n and the
     predicate ell+br>=n, tagging counter-examples bridgeless vs bridge-bearing.
  2. enumerate(n): EXACT scan over all connected graphs of order n (geng -c),
     returning the full counter-example census -- the sound truth table.
"""
from __future__ import annotations

import argparse
import json

import core


# --------------------------------------------------------------------------- #
#  Grounding a proposed construction
# --------------------------------------------------------------------------- #

def check_construction(n, edges, name="construction"):
    """Exactly verify and measure an explicit connected graph G=(n,edges)."""
    connected = core.is_connected(n, edges)
    out = {"name": name, "n": n, "m_edges": len(edges), "is_connected": connected}
    if not connected:
        out["note"] = ("DISCONNECTED -- the inequality ell+br>=|G| is stated for "
                       "CONNECTED graphs; not scored.")
        return out
    inv = core.lines_bridges_invariant(n, edges)
    out.update({
        "ell": inv["ell"],
        "br": inv["br"],
        "lhs_ell_plus_br": inv["lhs"],
        "predicate_holds": inv["predicate_holds"],   # ell+br >= n
        "is_counterexample": inv["is_counterexample"],  # ell+br < n
        "bridgeless": inv["bridgeless"],
        "bridge_list": inv["bridge_list"],
        "lines": inv["lines"],
    })
    return out


# --------------------------------------------------------------------------- #
#  Exact enumeration census  (full geng -c scan)
# --------------------------------------------------------------------------- #

def enumerate_counterexamples(n, store_witnesses=True, max_witnesses=None):
    """EXACT census of counter-examples (ell+br<n) among ALL connected graphs
    of order n.  Returns counts split bridgeless vs bridge-containing, plus
    optionally the explicit witnesses (graph6-free: edge lists)."""
    total = 0
    n_ce = 0
    n_ce_bridgeless = 0
    n_ce_bridge = 0
    witnesses = []
    for (gn, edges) in core.connected_graphs(n):
        total += 1
        inv = core.lines_bridges_invariant(gn, edges)
        if inv["is_counterexample"]:
            n_ce += 1
            if inv["bridgeless"]:
                n_ce_bridgeless += 1
            else:
                n_ce_bridge += 1
            if store_witnesses and (max_witnesses is None or len(witnesses) < max_witnesses):
                witnesses.append({
                    "edges": [list(e) for e in edges],
                    "ell": inv["ell"], "br": inv["br"],
                    "lhs": inv["lhs"], "bridgeless": inv["bridgeless"],
                    "bridge_list": inv["bridge_list"],
                })
    return {
        "n": n,
        "n_connected_graphs": total,
        "n_counterexamples": n_ce,
        "n_counterexamples_bridgeless": n_ce_bridgeless,
        "n_counterexamples_with_bridge": n_ce_bridge,
        "witnesses": witnesses,
    }


# --------------------------------------------------------------------------- #
#  Named built-in constructions
# --------------------------------------------------------------------------- #

def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def path(n):
    return n, [(i, i + 1) for i in range(n - 1)]


def complete(n):
    from itertools import combinations
    return n, list(combinations(range(n), 2))


_BUILDERS = {
    "c4": lambda: cycle(4),
    "c5": lambda: cycle(5),
    "c6": lambda: cycle(6),
    "p4": lambda: path(4),
    "k4": lambda: complete(4),
}


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="check a named built-in construction")
    p_chk.add_argument("name", choices=sorted(_BUILDERS))

    p_enum = sub.add_parser("enumerate", help="EXACT counter-example census for order n")
    p_enum.add_argument("n", type=int)
    p_enum.add_argument("--no-witnesses", action="store_true")
    p_enum.add_argument("--max-witnesses", type=int, default=None)

    p_edges = sub.add_parser("edges", help="check an explicit edge list: n then 'u-v,u-v,...'")
    p_edges.add_argument("n", type=int)
    p_edges.add_argument("edges", help="comma-separated u-v pairs, e.g. 0-1,1-2,2-3,3-0")

    args = ap.parse_args()
    if args.cmd == "check":
        n, edges = _BUILDERS[args.name]()
        res = check_construction(n, edges, name=args.name)
    elif args.cmd == "enumerate":
        res = enumerate_counterexamples(
            args.n,
            store_witnesses=not args.no_witnesses,
            max_witnesses=args.max_witnesses,
        )
    elif args.cmd == "edges":
        edges = []
        for tok in args.edges.split(","):
            u, v = tok.split("-")
            edges.append((int(u), int(v)))
        res = check_construction(args.n, edges, name="edges")

    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
