"""UPPER bound on minimum resolution refutation width via a CDCL solver's
DRUP/DRAT proof: the maximum width among the LEARNED clauses of a refutation is
an upper bound on a refutation width achievable by *some* refutation the solver
realizes (each learned clause is RUP-derivable; the learned-clause widths bound
the 'effective' width of the produced certificate).

This is a HEURISTIC UPPER bound (DRAT != pure resolution), reported as such. It
does NOT prove minimum width. Combined with the EXACT width-2 lower bound
(W(p)>=3 for all p, from saturation reaching fixpoint), it brackets W(p).
"""
import os
import sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sat_refutation_width as RW
from pysat.solvers import Cadical153


def measure(p):
    g = RW.ac_g(p); arcs = RW.circ_arcs(p, g)
    clauses = RW.build_clauses(p, arcs)
    # convert frozenset clauses to int lists
    cls = [list(c) for c in clauses]
    s = Cadical153(bootstrap_with=cls, with_proof=True)
    t0 = time.time()
    sat = s.solve()
    dt = time.time() - t0
    proof = s.get_proof() if not sat else None
    s.delete()
    if sat:
        return {"p": p, "SAT": True}
    # proof lines: list of strings, learned clauses (and 'd' deletions)
    widths = []
    nlearned = 0
    for line in proof:
        line = line.strip()
        if line.startswith("d"):
            continue
        toks = line.split()
        # last token is '0'
        lits = [t for t in toks if t != "0" and t != "d"]
        if not lits:
            widths.append(0)  # empty clause
        else:
            widths.append(len(lits))
        nlearned += 1
    return {"p": p, "SAT": False, "n_input_clauses": len(cls),
            "n_proof_lines": nlearned,
            "max_learned_width": max(widths) if widths else None,
            "median_learned_width": sorted(widths)[len(widths)//2] if widths else None,
            "solve_time_s": round(dt, 2)}


if __name__ == "__main__":
    import json
    out = []
    for p in [7, 11, 13, 17, 19]:
        r = measure(p)
        out.append(r)
        print(p, json.dumps(r))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'proof_width_upper.json'), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out))
