#!/usr/bin/env python3
"""Publication-grade certificate for the H16 refutation: omega_vec(C3[H])>=4.

The lower bound rests on the no-K4 ordering-CNF being UNSAT. This script EXPORTS,
for two independent CNF encodings:
  - the DIMACS CNF  (data/h16_cert/*.cnf)  + SHA256 checksum
  - the DRAT refutation proof from Cadical  (data/h16_cert/*.drat)
so the UNSAT result is independently checkable by any external verified checker:
      drat-trim <cnf> <drat>            (expect "s VERIFIED")
We also confirm UNSAT under a SECOND solver (Minisat22) for redundancy. The two
encodings differ in their clique-forbidding clauses (consecutive-chain vs
all-pairs-backward), giving genuinely different CNFs over the same order variables.
"""
import sys, os, json, hashlib, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
from law_exact_sweep import lex_compose
from pysat.formula import CNF
from pysat.solvers import Cadical153, Minisat22

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "h16_cert")
os.makedirs(OUT, exist_ok=True)

# H (gentourng class 307) and C3[H]
arcs_str = "01 02 30 40 05 60 12 13 14 51 61 23 24 25 62 34 53 36 45 46 56".split()
H = [(int(s[0]), int(s[1])) for s in arcs_str]
C3 = [(0, 1), (1, 2), (2, 0)]
N, A = lex_compose(3, C3, 7, H)            # C3[H], order 21
beats = core.beats_matrix(N, A)
assert core.omega_vec(7, H) == 2, "omega_vec(H) must be 2"

# order variables x[u<v]
idx = {}
def lit(u, v):
    if (u, v) in idx: return idx[(u, v)]
    if (v, u) in idx: return -idx[(v, u)]
    idx[(u, v)] = len(idx) + 1
    return idx[(u, v)]
for u in range(N):
    for v in range(u + 1, N): lit(u, v)
TRANS = []
for u in range(N):
    for v in range(N):
        if v == u: continue
        for w in range(N):
            if w in (u, v): continue
            TRANS.append([-lit(u, v), -lit(v, w), lit(u, w)])

def transitive_4sets():
    # yield, for each transitive 4-set, the (unique) order `perm` under which the four
    # vertices form a BACKEDGE clique: perm[i] < perm[j] (i<j) yet perm[j] beats perm[i].
    for S in itertools.combinations(range(N), 4):
        for perm in itertools.permutations(S):
            if all(beats[perm[j]][perm[i]] for i in range(4) for j in range(i + 1, 4)):
                yield perm
                break

def cnf_chain():
    # encoding 1: for each backedge-order perm[0]<...<perm[3], FORBID that order
    # (consecutive form): clause = OR_i (perm[i+1] < perm[i]).  A model is an order with
    # NO backedge K4 -> omega_vec <= 3; UNSAT -> every order has a backedge K4 -> omega_vec >= 4.
    c = CNF(); [c.append(cl) for cl in TRANS]
    nclq = 0
    for perm in transitive_4sets():
        c.append([lit(perm[i + 1], perm[i]) for i in range(3)]); nclq += 1
    return c, nclq

def cnf_allpairs():
    # encoding 2: same forbidden backedge-orders, all-pairs form: clause = OR_{i<j} (perm[j] < perm[i]).
    c = CNF(); [c.append(cl) for cl in TRANS]
    nclq = 0
    for perm in transitive_4sets():
        c.append([lit(perm[j], perm[i]) for i in range(4) for j in range(i + 1, 4)]); nclq += 1
    return c, nclq

def sha256_dimacs(cnf):
    body = f"p cnf {len(idx)} {len(cnf.clauses)}\n" + "".join(" ".join(map(str, cl)) + " 0\n" for cl in cnf.clauses)
    return body, hashlib.sha256(body.encode()).hexdigest()

cert = {"object": "C3[H], H=gentourng order-7 class 307", "order": N, "omega_vec_H": 2,
        "claim": "omega_vec(C3[H]) >= 4  (no-K4 ordering CNF UNSAT)", "encodings": []}
for name, build in [("chain", cnf_chain), ("allpairs", cnf_allpairs)]:
    cnf, nclq = build()
    body, sha = sha256_dimacs(cnf)
    cnf_path = os.path.join(OUT, f"noK4_{name}.cnf")
    open(cnf_path, "w").write(body)
    # Cadical with DRAT proof
    with Cadical153(bootstrap_with=cnf.clauses, with_proof=True) as m:
        sat_c = m.solve(); proof = m.get_proof() if not sat_c else None
    drat_path = os.path.join(OUT, f"noK4_{name}.drat")
    if proof is not None:
        open(drat_path, "w").write("\n".join(proof) + "\n")
    with Minisat22(bootstrap_with=cnf.clauses) as m2:
        sat_m = m2.solve()
    cert["encodings"].append({
        "name": name, "vars": len(idx), "clauses": len(cnf.clauses), "forbidden_4sets": nclq,
        "cadical_unsat": (not sat_c), "minisat_unsat": (not sat_m),
        "cnf_file": os.path.relpath(cnf_path), "cnf_sha256": sha,
        "drat_file": os.path.relpath(drat_path) if proof is not None else None,
        "drat_lines": len(proof) if proof is not None else 0,
    })
cert["both_encodings_unsat_both_solvers"] = all(
    e["cadical_unsat"] and e["minisat_unsat"] for e in cert["encodings"])
cert["external_check"] = "drat-trim <cnf_file> <drat_file>  (expect 's VERIFIED'); CNFs are plain DIMACS, any solver can re-decide UNSAT."
json.dump(cert, open(os.path.join(OUT, "certificate.json"), "w"), indent=2)
print(json.dumps(cert, indent=2))
