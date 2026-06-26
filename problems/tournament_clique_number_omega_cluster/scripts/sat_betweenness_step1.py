"""STEP 1 of the literature-reduction proposal: validate the SAT encoding.

CLAIM: omega_vec(T) <= 2  IFF  phi_T is SATISFIABLE over total orders, where
phi_T forbids, for every TRANSITIVE TRIPLE (a,b,c) (c->a, c->b, b->a), the single
linear arrangement a<b<c (the 'fully-reversed' placement that makes a triangle in
the backedge graph).

We encode total orders with ordering atoms x_{u,v} = (u<v), the standard
linear-ordering / betweenness CNF:
  - antisymmetry/totality:  x_{u,v} XOR x_{v,u}  (use single var p_{u,v}=u<v, v<u = not)
  - transitivity:  (u<v) & (v<w) -> (u<w)   for all ordered triples
  - forbidden:  for each transitive triple (a,b,c): NOT( a<b & b<c )
       [a<b & b<c => a<c by transitivity, so this forbids exactly a<b<c]

A triangle a<b<c in the backedge graph needs edges a-b,a-c,b-c, i.e. arcs
b->a, c->a, c->b: c beats a,b and b beats a = a transitive triple with source c,
sink a, placed increasing a<b<c.  Forbidding a<b AND b<c kills that one arrangement.

SAT  <=> some total order is triangle-free  <=> omega_vec<=2.
UNSAT <=> every order has a triangle           <=> omega_vec>=3.

Cross-check vs the canonical oracle (omega_vec_bb / triangle-free DFS) on the
family C_p(g), g(p)={1..(p-3)/2} U {(p+1)/2}, and consecutive controls.
"""
import os
import sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from pysat.solvers import Minisat22
from pysat.formula import CNF


def transitive_triples(n, beats):
    """All (a,b,c) with c->a, c->b, b->a  (c source, a sink, transitive)."""
    tt = []
    for a in range(n):
        for b in range(n):
            if b == a: continue
            for c in range(n):
                if c == a or c == b: continue
                if beats[c][a] and beats[c][b] and beats[b][a]:
                    tt.append((a, b, c))
    return tt


def build_cnf(n, arcs):
    beats = core.beats_matrix(n, arcs)
    # var(u,v) = literal meaning u<v.  Use one variable per ordered pair with
    # var(v,u) = -var(u,v).
    idx = {}
    nv = 0
    def lit(u, v):
        nonlocal nv
        if (u, v) in idx:
            return idx[(u, v)]
        if (v, u) in idx:
            return -idx[(v, u)]
        nv += 1
        idx[(u, v)] = nv
        return nv
    cnf = CNF()
    # totality is automatic (one var per pair, sign = direction). Need transitivity.
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                # (u<v) & (v<w) -> (u<w):  (-uv | -vw | uw)
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    tts = transitive_triples(n, beats)
    # canonicalize each forbidden clause to dedupe (a<b<c is order-specific)
    for (a, b, c) in tts:
        # forbid a<b AND b<c  =>  clause (-(a<b) | -(b<c)) = (b<a | c<b)
        cnf.append([lit(b, a), lit(c, b)])
    return cnf, len(tts)


def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def ac_g(p):
    return set(range(1, (p - 3) // 2 + 1)) | {(p + 1) // 2}


def oracle_triangle_free(n, arcs):
    """canonical: omega_vec<=2 ?  via omega_vec_bb (exact)."""
    return core.omega_vec_bb(n, arcs, ub=3) <= 2


def main():
    out = {"cases": []}
    # the AC family + controls
    cases = []
    for p in [7, 11, 13]:
        cases.append((f"AC{p}", p, ac_g(p)))
    # consecutive controls (known omega_vec=2 => SAT)
    cases.append(("consec7", 7, {1, 2, 3}))
    cases.append(("consec11", 11, {1, 2, 3, 4, 5}))
    # QR_7 (omega_vec=3 => UNSAT)
    cases.append(("QR7", 7, {1, 2, 4}))
    for name, p, g in cases:
        arcs = circ_arcs(p, g)
        cnf, ntt = build_cnf(p, arcs)
        t0 = time.time()
        with Minisat22(bootstrap_with=cnf.clauses) as m:
            sat = m.solve()
        dt = time.time() - t0
        # oracle ground truth (exact)
        t1 = time.time()
        ov = core.omega_vec_bb(p, arcs, ub=4)
        odt = time.time() - t1
        sat_says_le2 = sat
        oracle_le2 = (ov <= 2)
        agree = (sat_says_le2 == oracle_le2)
        rec = {"name": name, "p": p, "g": sorted(g), "n_transitive_triples": ntt,
               "SAT": sat, "sat_predicts_omega_vec_le2": sat_says_le2,
               "oracle_omega_vec": ov, "oracle_le2": oracle_le2,
               "AGREE": agree, "sat_time_s": round(dt, 3), "oracle_time_s": round(odt, 2)}
        out["cases"].append(rec)
        print(f"{name:10s} p={p:2d} |g|={len(g)} ntt={ntt:4d} "
              f"SAT={str(sat):5s} oracle_ov={ov} le2_match={agree} "
              f"({dt:.3f}s sat / {odt:.2f}s oracle)")
    out["all_agree"] = all(c["AGREE"] for c in out["cases"])
    print("\nALL ENCODING AGREE WITH ORACLE:", out["all_agree"])
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sat_betweenness_step1.json'), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
