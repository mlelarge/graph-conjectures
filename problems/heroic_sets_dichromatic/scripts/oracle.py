"""Oracle CLI + benchmark for arXiv:2009.13319 (heroic sets / dichromatic).

Aboulker, Charbit, Naserasr, "Extension of the Gyarfas-Sumner conjecture to
digraphs."  Problem 1.2: for which finite sets F of digraphs does Forb_ind(F)
have BOUNDED dichromatic number (such F are *heroic*)?

What this oracle does SOUNDLY and EXACTLY:
  1. check_construction(n, arcs): the workhorse the agent calls to GROUND a
     proposal -- reports is_oriented / is_triangle_free / chi_d, and (optional)
     which named forbidden digraphs it contains as INDUCED subdigraphs.
  2. measure_heroic_set(F, n_max): sweep all oriented triangle-free digraphs up
     to n_max, keep those in Forb_ind(F), and report the MAX chi_d observed plus
     any witness -- this RED-TEAMS a claimed bound (a witness exceeding the bound
     is a sound DISPROOF) and exactly settles finite-target subclaims.
  3. tower(k): the unbounded-dichromatic tournament tower D_k with chi_d(D_k)=k.
  4. cycle_substitution(k, base): Thm 2.1 chi_d(C_k(D))=chi_d(D)+1.

CAVEAT (a discipline gate, not a bug): "heroic"/"bounded" is an ASYMPTOTIC
quantifier.  Finite enumeration can DISPROVE a claimed heroic set (witness with
large chi_d) or supply supporting evidence, but CANNOT prove boundedness.  It
CAN exactly settle finite-target landmarks (Thm 6.5 chi_d=2; Thm 2.1 identity;
tower values).
"""
from __future__ import annotations

import argparse
import json

import core


# --------------------------------------------------------------------------- #
#  Named families  (for the CLI / forbidden-set specs)
# --------------------------------------------------------------------------- #

_NAMED = {
    "K1": core.K1,
    "K2sym": core.K2sym,
    "K2sym_bar": core.K2sym_bar,
    "C3": core.C3,
    "P+3": lambda: core.P_plus(3),
    "P+4": lambda: core.P_plus(4),
    "P+2": lambda: core.P_plus(2),
}


def named(name):
    if name not in _NAMED:
        raise KeyError(f"unknown digraph '{name}'; known: {sorted(_NAMED)}")
    return _NAMED[name]()


# --------------------------------------------------------------------------- #
#  1. Grounding a single construction
# --------------------------------------------------------------------------- #

def check_construction(n, arcs, name="construction", forbidden=None):
    """Exactly verify and measure one explicit digraph.

    forbidden: optional list of digraph names to test induced-containment of."""
    arcs = [tuple(a) for a in arcs]
    out = {
        "name": name,
        "n": n,
        "m_arcs": len(arcs),
        "is_oriented": core.is_oriented(arcs),
        "is_triangle_free": core.is_triangle_free(n, arcs),
        "chi_d": core.dichromatic_number(n, arcs),
        "acyclic_number": core.acyclic_number(n, arcs),
    }
    if forbidden:
        cont = {}
        for hn in forbidden:
            H = named(hn)
            cont[hn] = core.contains_induced((n, arcs), H)
        out["contains_induced"] = cont
        out["in_Forb_ind"] = not any(cont.values())
    return out


# --------------------------------------------------------------------------- #
#  2. Measure / red-team a claimed heroic set
# --------------------------------------------------------------------------- #

def measure_heroic_set(F_names, n_max, claimed_bound=None, verbose=False):
    """Sweep all ORIENTED TRIANGLE-FREE digraphs up to n_max; keep those in
    Forb_ind(F); report the distribution of chi_d, the max, a witness, and (if
    claimed_bound given) whether any member exceeds it (a sound DISPROOF).

    Note: by enumerating oriented (digon-free) triangle-free graphs, any F
    member that is a digon (K2sym) or contains a triangle/3-cycle (C3) is
    automatically excluded structurally; the remaining filtering is by the
    other F members (e.g. P+3) via induced containment.
    """
    F = [named(x) for x in F_names]
    chi_counts = {}
    max_chi = 0
    witness = None
    first_attained = {}     # chi value -> smallest n attaining it
    n_kept = 0
    n_total = 0
    violation = None
    for n in range(1, n_max + 1):
        kept_n = 0
        for (dn, arcs) in core.oriented_triangle_free_digraphs(n):
            n_total += 1
            if not core.avoids_all((dn, arcs), F):
                continue
            n_kept += 1
            kept_n += 1
            chi = core.dichromatic_number(dn, arcs)
            chi_counts[chi] = chi_counts.get(chi, 0) + 1
            if chi not in first_attained:
                first_attained[chi] = {"n": n, "arcs": list(arcs)}
            if chi > max_chi:
                max_chi = chi
                witness = {"n": n, "arcs": list(arcs), "chi_d": chi}
            if claimed_bound is not None and chi > claimed_bound and violation is None:
                violation = {"n": n, "arcs": list(arcs), "chi_d": chi}
        if verbose:
            print(f"  n={n}: kept {kept_n} in Forb_ind  (running max chi_d={max_chi})")
    return {
        "forbidden_set": F_names,
        "n_max": n_max,
        "n_total_enumerated": n_total,
        "n_in_Forb_ind": n_kept,
        "chi_d_distribution": dict(sorted(chi_counts.items())),
        "max_chi_d": max_chi,
        "max_witness": witness,
        "first_attained": {str(k): v["n"] for k, v in sorted(first_attained.items())},
        "claimed_bound": claimed_bound,
        "bound_violated": violation is not None,
        "violation_witness": violation,
    }


# --------------------------------------------------------------------------- #
#  3 & 4.  Tower and cycle substitution (exact finite landmarks)
# --------------------------------------------------------------------------- #

def tower(k):
    n, arcs = core.tournament_tower(k)
    return {
        "k": k,
        "n": n,
        "m_arcs": len(arcs),
        "chi_d": core.dichromatic_number(n, arcs),
        "expected_chi_d": k,
        "matches": core.dichromatic_number(n, arcs) == k,
    }


def cycle_substitution(k, base_name):
    base = named(base_name)
    base_chi = core.dichromatic_number(*base)
    comp = core.substitute_into_cycle([base] * k)
    comp_chi = core.dichromatic_number(*comp)
    return {
        "k": k,
        "base": base_name,
        "chi_d_base": base_chi,
        "chi_d_C_k_of_base": comp_chi,
        "expected": base_chi + 1,
        "matches": comp_chi == base_chi + 1,
    }


# --------------------------------------------------------------------------- #
#  Benchmark landmark: the paper's Thm 6.5 known value
# --------------------------------------------------------------------------- #

def thm_6_5(n_max=6):
    """chi_d(Forb_ind(K2sym, C3, P+3)) = 2  (Theorem 6.5):
    every triangle-free oriented graph with no induced directed P+(3) is
    2-dicolourable, and 2 is attained.  Returns the exact sweep result."""
    return measure_heroic_set(["K2sym", "C3", "P+3"], n_max, claimed_bound=2)


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="ground an explicit digraph (JSON arcs)")
    p_chk.add_argument("n", type=int)
    p_chk.add_argument("arcs", help='JSON list of [u,v] pairs, e.g. "[[0,1],[1,2]]"')
    p_chk.add_argument("--forbidden", nargs="*", default=None,
                       help="named digraphs to test induced-containment of")
    p_chk.add_argument("--name", default="construction")

    p_meas = sub.add_parser("measure", help="sweep Forb_ind(F) up to n_max")
    p_meas.add_argument("n_max", type=int)
    p_meas.add_argument("--forbidden", nargs="+", required=True)
    p_meas.add_argument("--claimed-bound", type=int, default=None)
    p_meas.add_argument("-v", "--verbose", action="store_true")

    p_t65 = sub.add_parser("thm65", help="reproduce Theorem 6.5 chi_d=2 landmark")
    p_t65.add_argument("n_max", type=int, nargs="?", default=6)
    p_t65.add_argument("-v", "--verbose", action="store_true")

    p_tow = sub.add_parser("tower", help="tournament tower D_k, chi_d(D_k)=k")
    p_tow.add_argument("k", type=int)

    p_sub = sub.add_parser("cyclesub", help="Thm 2.1 chi_d(C_k(base))=chi_d(base)+1")
    p_sub.add_argument("k", type=int)
    p_sub.add_argument("base", choices=sorted(_NAMED))

    args = ap.parse_args()
    if args.cmd == "check":
        arcs = json.loads(args.arcs)
        res = check_construction(args.n, arcs, name=args.name,
                                 forbidden=args.forbidden)
    elif args.cmd == "measure":
        res = measure_heroic_set(args.forbidden, args.n_max,
                                 claimed_bound=args.claimed_bound,
                                 verbose=args.verbose)
    elif args.cmd == "thm65":
        res = measure_heroic_set(["K2sym", "C3", "P+3"], args.n_max,
                                 claimed_bound=2, verbose=args.verbose)
    elif args.cmd == "tower":
        res = tower(args.k)
    elif args.cmd == "cyclesub":
        res = cycle_substitution(args.k, args.base)

    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
