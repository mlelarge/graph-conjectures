"""H3 red-team: sweep oriented K4-free P+(3)-free digraphs, compare observed
max chi_d against the paper's abstract bound of 414.

The abstract of arXiv:2009.13319 states: oriented K4-free graphs with no induced
P+(3) have chi_d <= 414.  H3 conjectures this bound is far from tight (observed
max chi_d is a small single-digit constant on all enumerable n).

This is a SUFFICIENCY/boundedness red-team on a C3-FORBIDDING-superset class
(K4-free allows triangles but forbids K4; P+(3)-free is the second forbidden
member).  Enumeration cannot PROVE boundedness, but:
  * a witness whose chi_d climbs with n would refine the abstract bound from
    BELOW (and is the engine's only decisive computational outcome here);
  * sustained small chi_d accumulates supporting evidence.

NOTE: K4-free graphs are dense (triangles allowed), so 2^|E| orientations
explode fast.  We cap per-graph edge count to keep the orientation blow-up
tractable and report exactly how many graphs/orientations were (skipped) so the
result is an HONEST partial sweep, never a silently-truncated one.

Forbidden set F = {K2sym (auto: we enumerate oriented = digon-free),
                   P+(3)}.  K4-free is enforced structurally by geng -k.
We do NOT forbid C3 (triangles are allowed in this class) -- that is the whole
point of H3 vs the triangle-free Thm 6.5 landmark.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys

import core

P3 = core.P_plus(3)  # induced obstruction


def sweep(n_max, max_edges=None, max_orient=None, claimed_bound=414):
    """Sweep oriented K4-free P+(3)-free digraphs up to n_max.

    max_edges: skip any underlying graph with more than this many edges
               (its 2^|E| orientations would be too many).  None = no cap.
    max_orient: hard cap on orientations enumerated per graph (sampled? no --
               we skip the graph entirely if over cap, to stay EXACT/honest).
    """
    chi_counts = {}
    max_chi = 0
    witness = None
    first_attained = {}
    n_kept = 0
    n_orient_total = 0
    n_graphs = 0
    n_graphs_skipped = 0
    violation = None
    per_n = []

    for n in range(1, n_max + 1):
        kept_n = 0
        max_chi_n = 0
        graphs_n = 0
        skipped_n = 0
        orient_n = 0
        for (gn, edges) in core.k4_free_graphs(n):
            graphs_n += 1
            n_graphs += 1
            m = len(edges)
            n_orient = 1 << m
            if (max_edges is not None and m > max_edges) or \
               (max_orient is not None and n_orient > max_orient):
                skipped_n += 1
                n_graphs_skipped += 1
                continue
            for arcs in core.all_orientations(edges):
                orient_n += 1
                n_orient_total += 1
                D = (n, arcs)
                # oriented (digon-free) is guaranteed by all_orientations;
                # K4-free guaranteed by geng -k.  Only need P+(3)-free.
                if core.contains_induced(D, P3):
                    continue
                n_kept += 1
                kept_n += 1
                chi = core.dichromatic_number(n, arcs)
                chi_counts[chi] = chi_counts.get(chi, 0) + 1
                if chi not in first_attained:
                    first_attained[chi] = n
                if chi > max_chi_n:
                    max_chi_n = chi
                if chi > max_chi:
                    max_chi = chi
                    witness = {"n": n, "arcs": list(arcs), "chi_d": chi}
                if claimed_bound is not None and chi > claimed_bound \
                        and violation is None:
                    violation = {"n": n, "arcs": list(arcs), "chi_d": chi}
        per_n.append({
            "n": n,
            "graphs": graphs_n,
            "graphs_skipped_edgecap": skipped_n,
            "orientations": orient_n,
            "kept_in_Forb": kept_n,
            "max_chi_d_at_n": max_chi_n,
        })
        print(f"  n={n}: {graphs_n} K4-free graphs "
              f"({skipped_n} skipped >max_edges={max_edges}), "
              f"{orient_n} orientations, {kept_n} kept, "
              f"max chi_d so far={max_chi}", file=sys.stderr, flush=True)

    return {
        "hypothesis": "H3",
        "forbidden_set": ["K2sym(structural:oriented)", "P+3"],
        "class": "oriented K4-free P+(3)-free digraphs",
        "n_max": n_max,
        "max_edges_cap": max_edges,
        "max_orient_cap": max_orient,
        "n_graphs": n_graphs,
        "n_graphs_skipped": n_graphs_skipped,
        "n_orientations_enumerated": n_orient_total,
        "n_in_Forb_ind": n_kept,
        "chi_d_distribution": dict(sorted(chi_counts.items())),
        "max_chi_d": max_chi,
        "max_witness": witness,
        "first_attained_n": {str(k): v for k, v in sorted(first_attained.items())},
        "claimed_bound": claimed_bound,
        "bound_violated": violation is not None,
        "violation_witness": violation,
        "per_n": per_n,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("n_max", type=int)
    ap.add_argument("--max-edges", type=int, default=None,
                    help="skip underlying graphs with more edges (orient blow-up)")
    ap.add_argument("--max-orient", type=int, default=None,
                    help="skip graphs whose 2^|E| exceeds this")
    ap.add_argument("--claimed-bound", type=int, default=414)
    args = ap.parse_args()
    res = sweep(args.n_max, max_edges=args.max_edges,
                max_orient=args.max_orient, claimed_bound=args.claimed_bound)
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
