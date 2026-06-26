"""Independent re-verification of the candidate 4-omega_vec-critical circulant
n=21, g={1,2,4,7,8,9,11,15,16,18}, found by search_4critical_circulant.py.

Checks (all SOUND, exact where feasible):
 (1) valid tournament: g sqcup -g = {1..20}, |g|=10=(21-1)/2.
 (2) vertex-transitive: x->x+1 mod 21 is an automorphism (automatic for circulant).
 (3) UPPER omega_vec<=4: an explicit order whose backedge clique is exactly 4
     (exact core.omega_of_order; min over all 21 rotations).
 (4) LOWER omega_vec>=4: SAT no-K4 CNF UNSAT under BOTH Cadical153 AND Minisat22
     (=> every order has a K4 => omega_vec>=4). Encoding soundness re-validated
     vs exact core.omega_vec on small circulants (both K=3,4 directions).
 (5) deletion (vertex 0): omega_vec(T-0)=3 EXACTLY:
       upper<=3 via explicit order (exact omega_of_order);
       lower>=3 via SAT no-K3 UNSAT (both solvers);
       and <=3 via SAT no-K4 SAT (a K4-free order exists).
     Vertex-transitivity => all 21 deletions isomorphic => T is 4-omega_vec-critical.
"""
import sys, os, json, time, itertools, random
sys.path.insert(0, os.path.dirname(__file__))
import core
from pysat.solvers import Cadical153, Minisat22
from pysat.formula import CNF

N = 21
G = {1, 2, 4, 7, 8, 9, 11, 15, 16, 18}


def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def transitive_ksubsets_order(n, beats, K):
    for S in itertools.combinations(range(n), K):
        outdeg = {x: sum(1 for y in S if y != x and beats[x][y]) for x in S}
        if sorted(outdeg.values()) != list(range(K)):
            continue
        order = sorted(S, key=lambda x: -outdeg[x])
        if all(beats[order[a]][order[b]] for a in range(K) for b in range(a + 1, K)):
            yield order


def build_cnf_no_kclique(n, arcs, K):
    beats = core.beats_matrix(n, arcs)
    idx = {}; nv = 0
    def lit(u, v):
        nonlocal nv
        if (u, v) in idx: return idx[(u, v)]
        if (v, u) in idx: return -idx[(v, u)]
        nv += 1; idx[(u, v)] = nv; return nv
    cnf = CNF()
    for u in range(n):
        for v in range(u + 1, n): lit(u, v)
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    nclq = 0
    for order in transitive_ksubsets_order(n, beats, K):
        cnf.append([lit(order[i], order[i + 1]) for i in range(K - 1)])
        nclq += 1
    return cnf, nclq


def sat_ge_K(n, arcs, K):
    """omega_vec>=K iff no-K-clique CNF UNSAT. Run BOTH solvers; assert agreement."""
    cnf, nclq = build_cnf_no_kclique(n, arcs, K)
    res = {}
    for name, Solver in [("cadical", Cadical153), ("minisat", Minisat22)]:
        t0 = time.time()
        with Solver(bootstrap_with=cnf.clauses) as s:
            sat = s.solve()
        res[name] = {"sat": sat, "time_s": round(time.time() - t0, 4)}
    assert res["cadical"]["sat"] == res["minisat"]["sat"], "solver disagreement!"
    ge = not res["cadical"]["sat"]
    return ge, res, nclq


def revalidate_encoding():
    """Re-confirm the no-K-clique SAT encoding == exact omega_vec on small circulants."""
    cases = [(7, {1, 2, 4}), (7, {1, 2, 3}), (9, {1, 2, 3, 5}), (9, {1, 2, 4, 7}),
             (11, {1, 2, 3, 4, 6}), (11, {1, 2, 3, 4, 5})]
    recs = []; ok = True
    for p, g in cases:
        negg = set((-d) % p for d in g)
        if g & negg or len(g) != (p - 1) // 2:
            continue
        arcs = circ_arcs(p, g)
        ov = core.omega_vec(p, arcs)
        for K in (3, 4):
            ge, _, _ = sat_ge_K(p, arcs, K)
            agree = (ge == (ov >= K))
            ok = ok and agree
            recs.append({"p": p, "g": sorted(g), "ov": ov, "K": K,
                         "sat_ge": ge, "agree": agree})
    return ok, recs


def best_order_upper_exact(n, arcs, tries=400, seed=7):
    rng = random.Random(seed)
    base = list(range(n))
    best = core.omega_of_order(n, arcs, base)
    best_order = base[:]
    for r in range(n):
        o = [(i + r) % n for i in range(n)]
        w = core.omega_of_order(n, arcs, o)
        if w < best: best, best_order = w, o
    for _ in range(tries):
        o = base[:]; rng.shuffle(o)
        w = core.omega_of_order(n, arcs, o)
        if w < best: best, best_order = w, o
    return best, best_order


def main():
    out = {}
    arcs = circ_arcs(N, G)
    # (1) tournament
    negg = set((-d) % N for d in G)
    out["is_tournament"] = core.is_tournament(N, arcs)
    out["g"] = sorted(G)
    out["neg_g"] = sorted(negg)
    out["g_partition_ok"] = (G & negg == set()) and (G | negg == set(range(1, N))) and len(G) == (N - 1) // 2
    print("is_tournament:", out["is_tournament"], "partition_ok:", out["g_partition_ok"], flush=True)

    # encoding re-validation
    enc_ok, enc_recs = revalidate_encoding()
    out["encoding_revalidation_ok"] = enc_ok
    out["encoding_cases"] = enc_recs
    print("encoding revalidation all agree:", enc_ok, flush=True)
    assert enc_ok, "encoding failed re-validation"

    # (3) UPPER omega_vec<=4
    up, up_order = best_order_upper_exact(N, arcs, tries=500)
    out["omega_vec_upper"] = up
    out["upper_witness_order"] = up_order
    print("omega_vec upper (exact omega_of_order, best of rotations+random):", up, flush=True)

    # (4) LOWER omega_vec>=4
    ge4, res4, ncl4 = sat_ge_K(N, arcs, 4)
    ge5, res5, ncl5 = sat_ge_K(N, arcs, 5)
    out["sat_omega_vec_ge4"] = {"ge4": ge4, "solvers": res4, "nclauses": ncl4}
    out["sat_omega_vec_ge5"] = {"ge5": ge5, "solvers": res5, "nclauses": ncl5}
    print(f"omega_vec>=4 (no-K4 UNSAT): {ge4}  | omega_vec>=5: {ge5}", flush=True)
    out["omega_vec_exact"] = 4 if (ge4 and up <= 4 and not ge5) else "INCONCLUSIVE"
    print("=> omega_vec(T) =", out["omega_vec_exact"], flush=True)

    # (5) deletion of vertex 0
    nn, sub = core.subtournament(N, arcs, [w for w in range(N) if w != 0])
    dup, dup_order = best_order_upper_exact(nn, sub, tries=500)
    dge3, dres3, _ = sat_ge_K(nn, sub, 3)
    dge4, dres4, _ = sat_ge_K(nn, sub, 4)
    out["deletion0"] = {"upper_exact": dup, "ge3_sat": dge3, "ge4_sat": dge4,
                        "solvers_ge3": dres3, "solvers_ge4": dres4}
    del_exact = 3 if (dge3 and not dge4 and dup <= 3) else "INCONCLUSIVE"
    out["deletion0_omega_vec_exact"] = del_exact
    print(f"deletion(T-0): upper={dup} ge3={dge3} ge4={dge4} => omega_vec(T-0) = {del_exact}", flush=True)

    out["is_4_omega_vec_critical"] = (out["omega_vec_exact"] == 4 and del_exact == 3)
    out["criticality_argument"] = ("circulant => vertex-transitive (x->x+1 mod 21 "
        "automorphism) => all 21 single-vertex deletions isomorphic; deletion of "
        "vertex 0 has omega_vec=3 => all deletions=3 => T is 4-omega_vec-critical")
    print("\n*** is 4-omega_vec-critical:", out["is_4_omega_vec_critical"], "***", flush=True)

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "verify_4critical_n21.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
