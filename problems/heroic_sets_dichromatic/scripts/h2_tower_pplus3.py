#!/usr/bin/env python3
"""H2 red-team: are the tournament-tower digraphs D_k induced-P+(3)-free?

If yes, {D_k} is an unbounded-chi_d family inside Forb_ind(K2sym, P+3),
which DISPROVES that Forb_ind(K2sym, P+3) is heroic (the H2 lever).

For each k we report: n, chi_d, contains induced K2sym (digon),
contains induced P+(3), and membership in Forb_ind(K2sym, P+3).
"""
import json
import sys

from core import (
    tournament_tower, K2sym, P_plus, contains_induced, dichromatic_number,
)


def main(kmax=5):
    K2 = K2sym()
    P3 = P_plus(3)
    rows = []
    for k in range(1, kmax + 1):
        n, arcs = tournament_tower(k)
        has_digon = contains_induced((n, arcs), K2)
        has_p3 = contains_induced((n, arcs), P3)
        chi = dichromatic_number(n, arcs)
        in_forb = (not has_digon) and (not has_p3)
        rows.append({
            "k": k,
            "n": n,
            "m_arcs": len(arcs),
            "chi_d": chi,
            "contains_induced_K2sym": has_digon,
            "contains_induced_Pplus3": has_p3,
            "in_Forb_ind_K2sym_Pplus3": in_forb,
        })
    out = {
        "experiment": "H2 tower induced-P+3-free test",
        "rows": rows,
        "all_in_Forb": all(r["in_Forb_ind_K2sym_Pplus3"] for r in rows),
        "chi_d_grows_with_k": [r["chi_d"] for r in rows],
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(kmax)
