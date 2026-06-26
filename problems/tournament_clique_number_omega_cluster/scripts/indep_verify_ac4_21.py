"""FULLY INDEPENDENT re-verification of AC4_21 = Cay(Z/21, g={1,2,4,7,8,9,11,15,16,18}).

Everything below is re-implemented from scratch (own beats matrix, own backedge-clique
via own Bron-Kerbosch, own no-K-clique SAT encoding) and cross-checked against the
canonical core.omega_vec_bruteforce. Goal: decide whether AC4_21 is 4-omega_vec-critical
WITHOUT trusting the prior agent's scripts.
"""
import sys, os, json, time, itertools, random
sys.path.insert(0, os.path.dirname(__file__))
import core  # only for cross-check vs canonical brute force
from pysat.solvers import Cadical153, Minisat22
from pysat.formula import CNF

N = 21
G = {1, 2, 4, 7, 8, 9, 11, 15, 16, 18}


def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def mk_beats(n, arcs):
    b = [[False] * n for _ in range(n)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def bron_kerbosch_max(adj, nodes):
    """Own max-clique size on undirected graph given as adjacency sets."""
    best = [0]
    def expand(R, P, X):
        if not P and not X:
            if R > best[0]:
                best[0] = R
            return
        if R + len(P) <= best[0]:
            return
        # pivot
        pu = max(P | X, key=lambda u: len(adj[u] & P)) if (P | X) else None
        cand = list(P - (adj[pu] if pu is not None else set()))
        for v in cand:
            expand(R + 1, P & adj[v], X & adj[v])
            P = P - {v}
            X = X | {v}
    expand(0, set(nodes), set())
    return best[0]


def omega_of_order_indep(n, beats, order):
    """Backedge clique for one order, own implementation."""
    pos = {v: i for i, v in enumerate(order)}
    adj = {v: set() for v in range(n)}
    for i in range(n):
        a = order[i]
        for j in range(i + 1, n):
            b = order[j]  # a prec b
            if beats[b][a]:  # backward arc => edge a-b
                adj[a].add(b)
                adj[b].add(a)
    return bron_kerbosch_max(adj, range(n))


# ---- own no-K-clique SAT encoding (re-derived) ----
def build_no_kclique_cnf(n, beats, K):
    idx = {}
    nv = [0]
    def lit(u, v):
        if (u, v) in idx:
            return idx[(u, v)]
        if (v, u) in idx:
            return -idx[(v, u)]
        nv[0] += 1
        idx[(u, v)] = nv[0]
        return nv[0]
    cnf = CNF()
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    # transitivity: (u<v)&(v<w) => (u<w)
    for u in range(n):
        for v in range(n):
            if v == u:
                continue
            for w in range(n):
                if w == u or w == v:
                    continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    nclq = 0
    # for each transitive K-subset (source->...->sink), forbid the reverse linear order
    for S in itertools.combinations(range(n), K):
        outdeg = {x: sum(1 for y in S if y != x and beats[x][y]) for x in S}
        if sorted(outdeg.values()) != list(range(K)):
            continue
        order = sorted(S, key=lambda x: -outdeg[x])  # s_1 source ... s_K sink
        if not all(beats[order[a]][order[b]] for a in range(K) for b in range(a + 1, K)):
            continue
        # backedge K-clique <=> all K placed in reverse: s_K < s_{K-1} < ... < s_1
        # forbid conjunction of consecutive reversed atoms (s_{i+1}<s_i):
        # clause = OR_i (s_i < s_{i+1})
        cnf.append([lit(order[i], order[i + 1]) for i in range(K - 1)])
        nclq += 1
    return cnf, nclq


def omega_vec_ge_K(n, beats, K, both=True):
    cnf, nclq = build_no_kclique_cnf(n, beats, K)
    sols = {}
    for name, S in ([("cadical", Cadical153), ("minisat", Minisat22)] if both else
                    [("cadical", Cadical153)]):
        with S(bootstrap_with=cnf.clauses) as s:
            sols[name] = s.solve()
    if both:
        assert sols["cadical"] == sols["minisat"], f"solver disagree {sols}"
    ge = not sols["cadical"]  # UNSAT => omega_vec >= K
    return ge, sols, nclq


def validate_vs_bruteforce(trials=400):
    """My SAT encoding vs canonical core.omega_vec_bruteforce on random tournaments,
    K in {2,3,4,5}. n in {5,6,7} so brute force is exact."""
    rng = random.Random(98765)
    mism = []
    for _ in range(trials):
        n = rng.choice([5, 6, 7])
        arcs = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.5:
                    arcs.append((u, v))
                else:
                    arcs.append((v, u))
        beats = mk_beats(n, arcs)
        ov = core.omega_vec_bruteforce(n, arcs)
        for K in (2, 3, 4, 5):
            ge, _, _ = omega_vec_ge_K(n, beats, K, both=False)
            if ge != (ov >= K):
                mism.append({"n": n, "arcs": arcs, "ov": ov, "K": K, "sat_ge": ge})
    return mism


def main():
    out = {}
    arcs = circ_arcs(N, G)
    beats = mk_beats(N, arcs)

    # (0) tournament validity, own check
    negg = set((-d) % N for d in G)
    out["is_tournament"] = core.is_tournament(N, arcs)
    out["g_partition_ok"] = (G & negg == set()) and (G | negg == set(range(1, N))) and len(G) == (N - 1) // 2
    print("tournament:", out["is_tournament"], "partition_ok:", out["g_partition_ok"], flush=True)

    # (1) INDEPENDENT validation of my SAT encoding vs canonical brute force
    t0 = time.time()
    mism = validate_vs_bruteforce(trials=500)
    out["sat_validation_mismatches"] = mism
    out["sat_validation_ok"] = (len(mism) == 0)
    print(f"SAT-vs-bruteforce validation: {len(mism)} mismatches "
          f"(500 random n in 5,6,7; K=2,3,4,5) in {time.time()-t0:.1f}s", flush=True)
    assert not mism, "encoding unsound -- ABORT"

    # (2) UPPER omega_vec<=4 via an explicit order (own Bron-Kerbosch),
    #     cross-checked against canonical core.omega_of_order
    best_up, best_order = N, None
    for r in range(N):
        o = [(i + r) % N for i in range(N)]
        w = omega_of_order_indep(N, beats, o)
        if w < best_up:
            best_up, best_order = w, o
    # also try random orders
    rng = random.Random(11)
    for _ in range(800):
        o = list(range(N)); rng.shuffle(o)
        w = omega_of_order_indep(N, beats, o)
        if w < best_up:
            best_up, best_order = w, o
    out["omega_vec_upper_indep_bk"] = best_up
    out["omega_vec_upper_canonical_crosscheck"] = core.omega_of_order(N, arcs, best_order)
    print(f"UPPER omega_vec <= {best_up} (own BK); canonical on same order = "
          f"{out['omega_vec_upper_canonical_crosscheck']}", flush=True)

    # (3) LOWER omega_vec>=4 and not >=5, both solvers
    ge4, s4, n4 = omega_vec_ge_K(N, beats, 4)
    ge5, s5, n5 = omega_vec_ge_K(N, beats, 5)
    out["omega_vec_ge4"] = {"ge": ge4, "solvers": s4, "nforbid": n4}
    out["omega_vec_ge5"] = {"ge": ge5, "solvers": s5, "nforbid": n5}
    print(f"LOWER: omega_vec>=4 (no-K4 UNSAT)={ge4} ; omega_vec>=5={ge5}", flush=True)
    out["omega_vec_exact"] = 4 if (ge4 and not ge5 and best_up <= 4) else "INCONCLUSIVE"

    # (4) deletion of vertex 0: own check, omega_vec(T-0)=3
    keep = [w for w in range(N) if w != 0]
    nn, sub = core.subtournament(N, arcs, keep)
    sbeats = mk_beats(nn, sub)
    # upper <= 3
    dbest, dorder = nn, None
    for r in range(nn):
        o = [(i + r) % nn for i in range(nn)]
        w = omega_of_order_indep(nn, sbeats, o)
        if w < dbest:
            dbest, dorder = w, o
    for _ in range(800):
        o = list(range(nn)); rng.shuffle(o)
        w = omega_of_order_indep(nn, sbeats, o)
        if w < dbest:
            dbest, dorder = w, o
    dge3, ds3, _ = omega_vec_ge_K(nn, sbeats, 3)
    dge4, ds4, _ = omega_vec_ge_K(nn, sbeats, 4)
    out["deletion0"] = {"upper_indep": dbest,
                        "upper_canonical_crosscheck": core.omega_of_order(nn, sub, dorder),
                        "ge3": dge3, "ge4": dge4, "solvers_ge3": ds3, "solvers_ge4": ds4}
    del3 = (dge3 and not dge4 and dbest <= 3)
    out["deletion0_omega_vec_exact"] = 3 if del3 else "INCONCLUSIVE"
    print(f"DELETION(T-0): upper={dbest} ge3={dge3} ge4={dge4} => omega_vec(T-0)="
          f"{out['deletion0_omega_vec_exact']}", flush=True)

    out["is_4_omega_vec_critical"] = (out["omega_vec_exact"] == 4 and del3)
    print("\n*** is_4_omega_vec_critical:", out["is_4_omega_vec_critical"], "***", flush=True)

    dp = os.path.join(os.path.dirname(__file__), "..", "data", "indep_verify_ac4_21.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", os.path.abspath(dp))


if __name__ == "__main__":
    main()
