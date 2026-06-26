"""INDEPENDENT red-team of C1: omega_vec(AC_n[C3]) = 4 for all odd n>=7.

Built from scratch. AC_n = Cay(Z/n, {1..m-1} U {m+1}), n=2m+1.
AC_n[C3] = lex substitution: vertex (t,h), t in Z/n, h in {0,1,2}, C3=0->1->2->0.
Arc (t,h)->(t',h') iff t->t' in AC_n (t!=t') or (t==t' and h->h' in C3).

omega_vec(D) = min over total orders of clique-number of backedge graph.
no-K_{K} SAT  <=> some order's backedge graph is K_K-free <=> omega_vec <= K-1.
no-K_{K} UNSAT <=> omega_vec >= K.

So: omega_vec <= 4  iff  no-K5 CNF SAT.
    omega_vec >= 4  iff  no-K4 CNF UNSAT.
"""
import sys, time, itertools, argparse
from pysat.solvers import Cadical153
from pysat.formula import CNF


def ac_generator(n):
    assert n % 2 == 1
    m = (n - 1) // 2
    g = set(range(1, m)) | {m + 1}
    return m, g


def ac_arcs(n):
    """Arcs of AC_n on vertices 0..n-1."""
    m, g = ac_generator(n)
    arcs = []
    for i in range(n):
        for d in g:
            arcs.append((i, (i + d) % n))
    return arcs


def is_tournament(n, arcs):
    s = set()
    for (u, v) in arcs:
        if u == v:
            return False
        if (u, v) in s or (v, u) in s:
            return False
        s.add((u, v))
    return len(s) == n * (n - 1) // 2


def lex_C3(n):
    """AC_n[C3]: returns (N, beats) where N=3n, beats[u][v] True iff u->v.
    vertex id = 3*t + h.  C3 arcs: 0->1, 1->2, 2->0."""
    m, g = ac_generator(n)
    inset = [False] * n
    for d in g:
        inset[d] = True
    # AC arc t->t' iff (t'-t) mod n in g
    N = 3 * n
    beats = [[False] * N for _ in range(N)]
    c3 = [[False, True, False], [False, False, True], [True, False, False]]
    for t in range(n):
        for tp in range(n):
            if t == tp:
                continue
            d = (tp - t) % n
            tbeats = inset[d]
            for h in range(3):
                for hp in range(3):
                    if tbeats:
                        beats[3 * t + h][3 * tp + hp] = True
    for t in range(n):
        for h in range(3):
            for hp in range(3):
                if h != hp and c3[h][hp]:
                    beats[3 * t + h][3 * t + hp] = True
    return N, beats


def check_beats_tournament(N, beats):
    for u in range(N):
        if beats[u][u]:
            return False, f"loop at {u}"
        for v in range(u + 1, N):
            a, b = beats[u][v], beats[v][u]
            if a == b:
                return False, f"pair {u},{v} both={a}"
    return True, "ok"


def transitive_ksubsets(N, beats, K):
    """Yield acyclic orders (s_1..s_K) of each transitive K-subset (s_a->s_b for a<b)."""
    rng = range(N)
    for S in itertools.combinations(rng, K):
        outdeg = {}
        for x in S:
            outdeg[x] = sum(1 for y in S if y != x and beats[x][y])
        if sorted(outdeg.values()) != list(range(K)):
            continue
        order = sorted(S, key=lambda x: -outdeg[x])
        if all(beats[order[a]][order[b]] for a in range(K) for b in range(a + 1, K)):
            yield order


def build_cnf_no_kclique(N, beats, K):
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
    for u in range(N):
        for v in range(u + 1, N):
            lit(u, v)
    # transitivity of the order
    for u in range(N):
        for v in range(N):
            if v == u:
                continue
            for w in range(N):
                if w == u or w == v:
                    continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    ncl = 0
    for order in transitive_ksubsets(N, beats, K):
        clause = [lit(order[i], order[i + 1]) for i in range(K - 1)]
        cnf.append(clause)
        ncl += 1
    return cnf, ncl


def omega_vec_ge_K(N, beats, K, timeout=None):
    cnf, ncl = build_cnf_no_kclique(N, beats, K)
    t0 = time.time()
    with Cadical153(bootstrap_with=cnf.clauses) as m:
        sat = m.solve()
    return (not sat), time.time() - t0, ncl


def run(n, verbose=True):
    N, beats = lex_C3(n)
    okt, msg = check_beats_tournament(N, beats)
    if not okt:
        return {"n": n, "N": N, "ERROR_not_tournament": msg}
    # >=4 : no-K4 UNSAT
    ge4, t4, ncl4 = omega_vec_ge_K(N, beats, 4)
    # <=4 : no-K5 SAT (ge5 False)
    ge5, t5, ncl5 = omega_vec_ge_K(N, beats, 5)
    val = "?"
    if ge4 and not ge5:
        val = 4
    elif not ge4:
        val = "<4"
    elif ge5:
        val = ">=5"
    rec = {"n": n, "N": N, "omega_vec_ge4": ge4, "omega_vec_ge5": ge5,
           "VALUE": val, "K4_clauses": ncl4, "K5_clauses": ncl5,
           "t_ge4_s": round(t4, 2), "t_ge5_s": round(t5, 2)}
    if verbose:
        print(f"n={n:3d} N={N:3d} ge4={ge4} ge5={ge5} => omega_vec={val} "
              f"(t4={t4:.2f}s t5={t5:.2f}s ncl4={ncl4} ncl5={ncl5})", flush=True)
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ns", type=int, nargs="+")
    args = ap.parse_args()
    results = []
    for n in args.ns:
        results.append(run(n))
    bad = [r for r in results if r.get("VALUE") != 4]
    print("\n=== SUMMARY ===")
    for r in results:
        print(r)
    print("ALL == 4:", len(bad) == 0, "| anomalies:", bad)
