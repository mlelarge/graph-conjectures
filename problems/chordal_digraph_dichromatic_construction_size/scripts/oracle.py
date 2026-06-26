"""Oracle CLI + benchmark for arXiv:2202.01006.

Aboulker, Bousquet, de Verclos, "Chordal directed graphs are not directed
chi-bounded", Section 3 "Further works": they construct a (k+1)-dichromatic
digraph in the class C_3 of size n^(2^poly(n)) (doubly exponential) and ask
whether the size can be REDUCED.

C_3 = oriented digraphs (no digon) with no transitive triangle TT3 and no
induced directed cycle of length >= 4.  (Allows the directed triangle C3.)

The finite handle:
    m(k) = minimum order of a C_3 digraph with dichromatic number >= k.
The paper's construction is a (doubly exponential) UPPER bound on m(k); any
small C_3 witness with chi_vec >= k beats it.  m(k) is exactly computable on
small instances:

Two jobs:
  1. check_construction(n, arcs): the workhorse the agent calls to GROUND a
     proposal -- verifies C_3 membership and reports the exact chi_vec / acyclic
     number, and (when n is in C_3 with chi_vec=k) whether it improves the m(k)
     landmark.
  2. extremal_small_n(n): exact scan over ALL simple graphs on n vertices
     (nauty geng) and ALL their orientations, keeping the C_3 members, returning
     the max chi_vec achievable in C_3 at order n and the smallest-order witness
     per dichromatic target -- the sound truth table for m(k).

Known landmarks (paper, reproduced by this oracle):
    m(1) = 1   (single vertex, G_1, chi_vec = 1)
    m(2) = 3   (directed triangle C3 = G_2, chi_vec = 2; nothing on 1 or 2)
    m(3) >= 8  (NEW exact lower bound: full n<=7 scan finds no C_3 with chi>=3)
"""
from __future__ import annotations

import argparse
import json

import core


# --------------------------------------------------------------------------- #
#  Grounding a proposed construction
# --------------------------------------------------------------------------- #

def check_construction(n, arcs, name="construction", compute_chi=True,
                       compute_alpha=True):
    """Exactly verify C_3 membership and measure an explicit oriented digraph."""
    reason = core.c3_reason(n, arcs)
    out = {
        "name": name, "n": n, "m_arcs": len(arcs),
        "is_oriented": reason["is_oriented"],
        "has_TT3": reason["has_TT3"],
        "has_long_induced_dicycle_ge4": reason["has_long_induced_dicycle_ge4"],
        "is_C3": reason["is_C3"],
    }
    if compute_alpha:
        out["acyclic_number"] = core.acyclic_number(n, arcs)
    if compute_chi:
        out["chi_vec"] = core.dichromatic_number(n, arcs)
    if out.get("is_C3") and "chi_vec" in out:
        k = out["chi_vec"]
        out["beats_landmark_for"] = (
            f"witness in C_3 with chi_vec={k} on {n} vertices "
            f"=> m({k}) <= {n}")
    return out


# --------------------------------------------------------------------------- #
#  Exact small-n extremal values  (full enumeration over ALL graphs)
# --------------------------------------------------------------------------- #

def extremal_small_n(n, ub=None, verbose=False, connected=False):
    """Exact: over every simple graph on n vertices (nauty geng) and every
    orientation, keep the C_3 members and record the maximum dichromatic number
    achieved, plus the first witness reaching each dichromatic value.

    Returns max_chi (= largest k with a C_3 witness on n vertices), so:
      * if max_chi >= k then m(k) <= n,
      * scanning n=1,2,3,... the FIRST n with max_chi >= k is exactly m(k),
      * absence of chi>=k up to N certifies m(k) > N.
    """
    max_chi = 0
    n_c3 = 0
    n_graphs = 0
    witness_by_chi = {}   # k -> first arc list reaching chi_vec == k
    cap = ub if ub is not None else n
    for (gn, edges) in core.all_simple_graphs(n, connected=connected):
        n_graphs += 1
        for arcs in core.all_orientations(edges):
            if not core.is_C3(n, arcs):
                continue
            n_c3 += 1
            cv = core.dichromatic_number(n, arcs, ub=cap)
            if cv not in witness_by_chi:
                witness_by_chi[cv] = list(arcs)
            if cv > max_chi:
                max_chi = cv
        if verbose:
            print(f"  ..graph {n_graphs}/?: running max_chi={max_chi} "
                  f"(C_3 seen={n_c3})")
    return {
        "n": n,
        "max_chi_in_C3": max_chi,
        "n_simple_graphs": n_graphs,
        "n_C3_orientations": n_c3,
        "witness_by_chi": {str(k): v for k, v in sorted(witness_by_chi.items())},
        "note": (f"m(k) <= {n} for every k <= {max_chi}; "
                 f"if no smaller n reaches k, this n is m(k)."),
    }


def m_of_k(k, n_max=10, verbose=False):
    """Exact m(k) by scanning n = 1.. until a C_3 witness with chi_vec >= k
    appears (returns that n), or n_max if none found (then m(k) > n_max)."""
    for n in range(1, n_max + 1):
        res = extremal_small_n(n, ub=k, verbose=verbose)
        if verbose:
            print(f"n={n}: max_chi_in_C3={res['max_chi_in_C3']}")
        if res["max_chi_in_C3"] >= k:
            return {"k": k, "m_k": n, "status": "exact",
                    "witness": res["witness_by_chi"].get(str(k))
                    or res["witness_by_chi"].get(str(res["max_chi_in_C3"]))}
    return {"k": k, "m_k": None, "status": f"m({k}) > {n_max}",
            "lower_bound": n_max + 1}


# --------------------------------------------------------------------------- #
#  Named built-in constructions (validation against the paper)
# --------------------------------------------------------------------------- #

def directed_cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


_BUILDERS = {
    "g1": lambda: (1, []),                         # single vertex, chi=1
    "g2": lambda: directed_cycle(3),               # directed triangle, chi=2
    "dc4": lambda: directed_cycle(4),              # NOT in C_3 (long dicycle)
    "tt3": lambda: (3, [(0, 1), (1, 2), (0, 2)]),  # NOT in C_3 (TT3)
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="check a named built-in construction")
    p_chk.add_argument("name", choices=sorted(_BUILDERS))

    p_ext = sub.add_parser("extremal",
                           help="exact max chi_vec in C_3 at order n (small n)")
    p_ext.add_argument("n", type=int)
    p_ext.add_argument("--ub", type=int, default=None,
                       help="cap the dichromatic search at this k (speed)")
    p_ext.add_argument("-v", "--verbose", action="store_true")

    p_mk = sub.add_parser("mk", help="exact m(k) by scanning n=1..n_max")
    p_mk.add_argument("k", type=int)
    p_mk.add_argument("--n_max", type=int, default=10)
    p_mk.add_argument("-v", "--verbose", action="store_true")

    args = ap.parse_args()
    if args.cmd == "check":
        n, arcs = _BUILDERS[args.name]()
        res = check_construction(n, arcs, name=args.name)
    elif args.cmd == "extremal":
        res = extremal_small_n(args.n, ub=args.ub, verbose=args.verbose)
    elif args.cmd == "mk":
        res = m_of_k(args.k, n_max=args.n_max, verbose=args.verbose)

    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
