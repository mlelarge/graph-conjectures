"""Oracle CLI + benchmark for arXiv:2403.02298.

Two jobs:
  1. check_construction(n, arcs): the workhorse the agent calls to GROUND a
     proposal -- verifies it is an oriented triangle-free graph and reports the
     exact alpha_vec / chi_vec together with where they sit against the
     conjectured benchmark scales.
  2. extremal_small_n(n): exact a_vec(n), t_vec(n) by full enumeration of
     oriented triangle-free graphs (small n only) -- the sound truth table.

Benchmark (the fixed yardstick every proposal is scored against; abstract of the
paper, natural logs):
     (1/sqrt2 - e) sqrt(n log n)  <=  a_vec(n)  <=  (107/8) sqrt(n) log n
     (8/107) sqrt(n)/log n        <=  t_vec(n)  <=  (sqrt2 + e) sqrt(n/log n)
  Conjecture 3:  a_vec(n) = Theta(sqrt(n log n))     [tighten the upper bound]
  Conjecture 4:  t_vec(n) = Theta(sqrt(n/log n))     [tighten the lower bound]
The open gap is a factor sqrt(log n) on each.
"""
from __future__ import annotations

import argparse
import math

import core
import constructions as C


# --------------------------------------------------------------------------- #
#  Benchmark scales
# --------------------------------------------------------------------------- #

def benchmark(n):
    if n < 2:
        return {}
    ln = math.log(n)
    return {
        "a_lower_proved": (1 / math.sqrt(2)) * math.sqrt(n * ln),
        "a_upper_proved": (107 / 8) * math.sqrt(n) * ln,
        "a_conj_scale": math.sqrt(n * ln),                  # sqrt(n log n)
        "t_lower_proved": (8 / 107) * math.sqrt(n) / ln,
        "t_upper_proved": math.sqrt(2) * math.sqrt(n / ln),
        "t_conj_scale": math.sqrt(n / ln),                  # sqrt(n/log n)
    }


# --------------------------------------------------------------------------- #
#  Grounding a proposed construction
# --------------------------------------------------------------------------- #

def check_construction(n, arcs, name="construction", compute_chi=True,
                       compute_alpha=True):
    """Exactly verify and measure an explicit oriented graph."""
    oriented = core.is_oriented(arcs)
    tri_free = core.is_triangle_free(n, arcs)
    out = {
        "name": name, "n": n, "m_arcs": len(arcs),
        "is_oriented": oriented, "is_triangle_free": tri_free,
    }
    if compute_alpha:
        out["alpha_vec"] = core.acyclic_number(n, arcs)
    if compute_chi:
        out["chi_vec"] = core.dichromatic_number(n, arcs)
    bm = benchmark(n)
    if bm:
        if "alpha_vec" in out:
            out["alpha_over_conj_scale"] = out["alpha_vec"] / bm["a_conj_scale"]
            out["alpha_within_proved_band"] = (
                bm["a_lower_proved"] <= out["alpha_vec"] <= bm["a_upper_proved"])
        if "chi_vec" in out:
            out["chi_over_conj_scale"] = out["chi_vec"] / bm["t_conj_scale"]
        out["benchmark"] = bm
    return out


def is_dicritical(n, arcs, k):
    """True iff chi_vec=k and deleting any single vertex drops chi_vec below k."""
    if core.dichromatic_number(n, arcs) != k:
        return False
    for w in range(n):
        keep = [v for v in range(n) if v != w]
        relabel = {v: i for i, v in enumerate(keep)}
        sub = [(relabel[u], relabel[v]) for (u, v) in arcs if u != w and v != w]
        if core.dichromatic_number(n - 1, sub) >= k:
            return False
    return True


# --------------------------------------------------------------------------- #
#  Exact small-n extremal values  (full enumeration)
# --------------------------------------------------------------------------- #

def extremal_small_n(n, max_edges_for_full=None, verbose=False):
    """Exact a_vec(n) = min alpha_vec and t_vec(n) = max chi_vec over all
    oriented triangle-free graphs of order n, by enumerating triangle-free
    graphs (geng -t) and all their orientations.  Small n only."""
    a_vec = n            # min acyclic number (upper-bounded by n)
    t_vec = 0            # max dichromatic number
    a_witness = t_witness = None
    n_graphs = 0
    for (gn, edges) in core.triangle_free_graphs(n):
        n_graphs += 1
        if max_edges_for_full is not None and len(edges) > max_edges_for_full:
            continue
        for arcs in core.all_orientations(edges):
            av = core.acyclic_number(n, arcs)
            if av < a_vec:
                a_vec, a_witness = av, list(arcs)
            cv = core.dichromatic_number(n, arcs, ub=t_vec + 1)
            if cv > t_vec:
                # cv may be the sentinel (t_vec+2) when the true chi_vec exceeds
                # the cap; recompute uncapped so the running max is never
                # under-reported.  The cap above is only a speed bound for the
                # common below-max case, so this exact recompute is rare.
                cv = core.dichromatic_number(n, arcs)
                t_vec, t_witness = cv, list(arcs)
        if verbose:
            print(f"  ..graph {n_graphs}: running a_vec={a_vec} t_vec={t_vec}")
    return {"n": n, "a_vec": a_vec, "t_vec": t_vec,
            "n_triangle_free_graphs": n_graphs,
            "a_witness": a_witness, "t_witness": t_witness}


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

_BUILDERS = {
    "d25": lambda: C.D25(),
    "paley7": lambda: C.paley_tournament(7),
    "paley11": lambda: C.paley_tournament(11),
    "tt5": lambda: C.transitive_tournament(5),
    "dc4": lambda: C.directed_cycle(4),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="check a named built-in construction")
    p_chk.add_argument("name", choices=sorted(_BUILDERS))

    p_blow = sub.add_parser("blowup", help="check ell-backward-blowup of C_ell")
    p_blow.add_argument("ell", type=int)
    p_blow.add_argument("m", type=int)

    p_ext = sub.add_parser("extremal", help="exact a_vec(n), t_vec(n) (small n)")
    p_ext.add_argument("n", type=int)
    p_ext.add_argument("-v", "--verbose", action="store_true")

    args = ap.parse_args()
    if args.cmd == "check":
        n, arcs = _BUILDERS[args.name]()
        res = check_construction(n, arcs, name=args.name)
    elif args.cmd == "blowup":
        n, arcs = C.backward_blowup_directed_cycle(args.ell, args.m)
        res = check_construction(n, arcs, name=f"C{args.ell}<-{args.m}")
    elif args.cmd == "extremal":
        res = extremal_small_n(args.n, verbose=args.verbose)

    import json
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
