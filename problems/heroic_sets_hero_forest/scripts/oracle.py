"""Oracle CLI + benchmark for arXiv:2009.13319, CONJECTURE 4.2 (hero + oriented
forest heroic-set dichotomy) and its concrete Section-6 sub-cases.

Aboulker, Charbit, Naserasr, "Extension of the Gyarfas-Sumner conjecture to
digraphs."  Conjecture 4.2: for a hero H and an oriented forest F, the set
{ K2_digon, H, F } is HEROIC (Forb_ind has BOUNDED dichromatic number) iff F is a
disjoint union of oriented stars OR H is a transitive tournament.

WHAT THIS ORACLE DOES, SOUNDLY AND EXACTLY:
  1. check_construction(n, arcs): the workhorse a GROUND agent calls -- reports
     is_oriented / is_triangle_free / chi_d / acyclic_number and (optional) which
     named forbidden digraphs occur as INDUCED subdigraphs, hence whether the
     object lies in a given Forb_ind class.
  2. measure_heroic_set(F, n_max): sweep all oriented triangle-free digraphs up to
     n_max, keep those in Forb_ind(F), report the chi_d distribution, the MAX
     chi_d, the smallest n attaining each value, and a witness.  Given a
     claimed_bound it FLAGS any member exceeding it (a SOUND DISPROOF of that
     bound).  This is the falsifier/measurer the engine drives.
  3. thm_6_1 / conj_6_2: reproduce the paper's two concrete landmarks exactly.
  4. tower(k) / cycle_substitution(k, base): exact finite identities (Thm 2.1,
     the chi_d=k tournament tower) for cross-checking the chi_d engine.

DISCIPLINE GATE (asymptotic quantifier).  "Heroic"/"bounded" ranges over an
INFINITE class.  Finite enumeration can SOUNDLY DISPROVE a claimed finite bound
(a member with larger chi_d) or accumulate supporting evidence, but CANNOT prove
boundedness.  It CAN exactly settle finite landmarks (Thm 6.1 chi_d=2; tower /
substitution identities).  An oracle "consistent up to n" is EVIDENCE, never a
proof -- see ledger.discipline_gates.empirical_not_proof.
"""
from __future__ import annotations

import argparse
import json

import core


# --------------------------------------------------------------------------- #
#  Named families  (forbidden-set specs)
# --------------------------------------------------------------------------- #

_NAMED = {
    "K2_digon": core.K2_digon,        # the digon  (forbidding it == oriented)
    "C3": core.C3,                    # directed triangle ->C3
    "arrowK2_K1": core.arrowK2_plus_K1,  # ->K2 + K1  (Thm 6.1 third member)
    "S2+": core.S2_plus,              # out-star
    "S2-": core.S2_minus,             # in-star
    "P+2": lambda: core.P_plus(2),
    "P+3": lambda: core.P_plus(3),
    "K1": core.K1,
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

    forbidden: optional list of named digraphs to test induced-containment of;
    if given, also reports whether the object is in Forb_ind(those)."""
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
        cont = {hn: core.contains_induced((n, arcs), named(hn)) for hn in forbidden}
        out["contains_induced"] = cont
        out["in_Forb_ind"] = not any(cont.values())
    return out


# --------------------------------------------------------------------------- #
#  2. Measure / red-team a claimed heroic-set bound
# --------------------------------------------------------------------------- #

def measure_heroic_set(F_names, n_max, claimed_bound=None, verbose=False,
                       keep_witness_arcs=True):
    """Sweep all ORIENTED TRIANGLE-FREE digraphs up to n_max; keep those in
    Forb_ind(F); report the chi_d distribution, the max, the smallest n attaining
    each value, and a max witness.  If claimed_bound is given, FLAG any member
    with chi_d > claimed_bound (a SOUND DISPROOF of that bound).

    Because we enumerate oriented (digon-free) triangle-free graphs, any F member
    that is the digon (K2_digon) or contains a triangle / directed-C3 is excluded
    STRUCTURALLY; remaining filtering is by the other F members via induced
    containment.  (So passing F = [K2_digon, C3, X] is equivalent to filtering by
    X alone on this enumeration -- both are accepted.)"""
    F = [named(x) for x in F_names]
    chi_counts, first_attained = {}, {}
    max_chi, witness, violation = 0, None, None
    n_kept, n_total = 0, 0
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
                first_attained[chi] = {"n": n, "arcs": list(map(list, arcs))}
            if chi > max_chi:
                max_chi = chi
                witness = {"n": n, "chi_d": chi}
                if keep_witness_arcs:
                    witness["arcs"] = list(map(list, arcs))
            if (claimed_bound is not None and chi > claimed_bound
                    and violation is None):
                violation = {"n": n, "arcs": list(map(list, arcs)), "chi_d": chi}
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
        "first_attained_n": {str(k): v["n"] for k, v in sorted(first_attained.items())},
        "claimed_bound": claimed_bound,
        "bound_violated": violation is not None,
        "violation_witness": violation,
        "note": ("ASYMPTOTIC: consistency up to n_max is EVIDENCE, not a proof of "
                 "heroicity; a violation_witness IS a sound disproof of the bound."),
    }


# --------------------------------------------------------------------------- #
#  3. The two concrete Section-6 landmarks
# --------------------------------------------------------------------------- #

def thm_6_1(n_max=6, verbose=False):
    """Theorem 6.1 (PROVED, EXACT): chi_d(Forb_ind(K2_digon, ->C3, ->K2+K1)) = 2.
    Every {digon, ->C3, ->K2+K1}-free oriented graph is 2-dicolourable and 2 is
    attained.  Returns the exact sweep; claimed_bound=2 must NOT be violated."""
    return measure_heroic_set(["K2_digon", "C3", "arrowK2_K1"], n_max,
                              claimed_bound=2, verbose=verbose)


def conj_6_2(n_max=7, verbose=False):
    """Conjecture 6.2 (OPEN): chi_d(Forb_ind(K2_digon, ->C3, S2+)) = 2.
    Falsifier/measurer: returns the exact sweep up to n_max; a member with
    chi_d>2 would DISPROVE the conjecture (none through the verified range)."""
    return measure_heroic_set(["K2_digon", "C3", "S2+"], n_max,
                              claimed_bound=2, verbose=verbose)


# --------------------------------------------------------------------------- #
#  4. Tower and cycle substitution (exact finite identities)
# --------------------------------------------------------------------------- #

def tower(k):
    n, arcs = core.tournament_tower(k)
    chi = core.dichromatic_number(n, arcs)
    return {"k": k, "n": n, "m_arcs": len(arcs), "chi_d": chi,
            "expected_chi_d": k, "matches": chi == k}


def cycle_substitution(k, base_name):
    base = named(base_name)
    base_chi = core.dichromatic_number(*base)
    comp = core.substitute_into_cycle([base] * k)
    comp_chi = core.dichromatic_number(*comp)
    return {"k": k, "base": base_name, "chi_d_base": base_chi,
            "chi_d_C_k_of_base": comp_chi, "expected": base_chi + 1,
            "matches": comp_chi == base_chi + 1}


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="ground an explicit digraph (JSON arcs)")
    p_chk.add_argument("n", type=int)
    p_chk.add_argument("arcs", help='JSON list of [u,v] pairs, e.g. "[[0,1],[1,2]]"')
    p_chk.add_argument("--forbidden", nargs="*", default=None,
                       help=f"named digraphs to test; known: {sorted(_NAMED)}")
    p_chk.add_argument("--name", default="construction")

    p_meas = sub.add_parser("measure", help="sweep Forb_ind(F) up to n_max")
    p_meas.add_argument("n_max", type=int)
    p_meas.add_argument("--forbidden", nargs="+", required=True)
    p_meas.add_argument("--claimed-bound", type=int, default=None)
    p_meas.add_argument("-v", "--verbose", action="store_true")

    p_t61 = sub.add_parser("thm61", help="reproduce Theorem 6.1 chi_d=2 landmark")
    p_t61.add_argument("n_max", type=int, nargs="?", default=6)
    p_t61.add_argument("-v", "--verbose", action="store_true")

    p_c62 = sub.add_parser("conj62", help="Conjecture 6.2 S2+ falsifier/measurer")
    p_c62.add_argument("n_max", type=int, nargs="?", default=7)
    p_c62.add_argument("-v", "--verbose", action="store_true")

    p_tow = sub.add_parser("tower", help="tournament tower D_k, chi_d(D_k)=k")
    p_tow.add_argument("k", type=int)

    p_sub = sub.add_parser("cyclesub", help="chi_d(C_k(base))=chi_d(base)+1")
    p_sub.add_argument("k", type=int)
    p_sub.add_argument("base", choices=sorted(_NAMED))

    args = ap.parse_args()
    if args.cmd == "check":
        res = check_construction(args.n, json.loads(args.arcs), name=args.name,
                                 forbidden=args.forbidden)
    elif args.cmd == "measure":
        res = measure_heroic_set(args.forbidden, args.n_max,
                                 claimed_bound=args.claimed_bound,
                                 verbose=args.verbose)
    elif args.cmd == "thm61":
        res = thm_6_1(args.n_max, verbose=args.verbose)
    elif args.cmd == "conj62":
        res = conj_6_2(args.n_max, verbose=args.verbose)
    elif args.cmd == "tower":
        res = tower(args.k)
    elif args.cmd == "cyclesub":
        res = cycle_substitution(args.k, args.base)
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
