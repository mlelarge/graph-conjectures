"""RED-TEAM C2 (P18): omega_vec(AC_n[C3] - v) = 3 for all odd n>=7 and ALL v.

Independent re-implementation. Everything built from scratch except:
  - SAT solver (pysat Cadical) and the no-K-clique CNF construction (which I
    re-derive below INLINE so I am not trusting the project's encoding blindly).
  - I cross-validate my SAT oracle vs an exact brute-force omega_vec on small
    instances before trusting it on large n.

Definitions:
  AC_n = Cay(Z/n, g), n=2m+1, g = {1..m-1} U {m+1}.
  C3 = 0->1->2->0.
  AC_n[C3] lex substitution: vertex (t,h), t in Z/n, h in {0,1,2}.
    arc (t,h)->(t',h') iff (t!=t' and (t'-t) mod n in g) or (t==t' and h->h' in C3).

  backedge clique under order prec: set S s.t. every pair is a backward arc, i.e.
  S is placed in reverse-topological order. omega_vec = min over orders of max
  backedge clique. A backedge clique induces a TRANSITIVE subtournament (placed
  reversed). Conversely any transitive subtournament can be placed reversed.
"""
import sys, os, itertools, time, argparse
import networkx as nx
from pysat.solvers import Cadical153
from pysat.formula import CNF


# ---------- build AC_n[C3] - deleted vertices : as a beats matrix ----------

def ac_gen(n):
    assert n % 2 == 1 and n >= 3
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}

def build_AC_C3(n):
    """Return (N, beats) for AC_n[C3], vertices indexed (t,h) -> t*3+h, N=3n."""
    g = ac_gen(n)
    N = 3 * n
    def idx(t, h):
        return (t % n) * 3 + h
    beats = [[False] * N for _ in range(N)]
    c3 = [[False]*3 for _ in range(3)]
    # 0->1,1->2,2->0
    c3[0][1] = c3[1][2] = c3[2][0] = True
    for t in range(n):
        for h in range(3):
            for tp in range(n):
                for hp in range(3):
                    if t == tp and h == hp:
                        continue
                    if t != tp:
                        if (tp - t) % n in g:
                            beats[idx(t,h)][idx(tp,hp)] = True
                    else:
                        if c3[h][hp]:
                            beats[idx(t,h)][idx(tp,hp)] = True
    return N, beats, idx

def delete_vertex(N, beats, drop):
    """Return (N', beats') with vertex `drop` removed, relabelled."""
    keep = [v for v in range(N) if v != drop]
    relab = {v: i for i, v in enumerate(keep)}
    Np = len(keep)
    nb = [[False]*Np for _ in range(Np)]
    for v in keep:
        for w in keep:
            if v != w and beats[v][w]:
                nb[relab[v]][relab[w]] = True
    return Np, nb

def check_tournament(N, beats):
    for u in range(N):
        for v in range(u+1, N):
            if beats[u][v] == beats[v][u]:
                return False
    return True


# ---------- exact omega_vec (brute force over orders) for validation ----------

def omega_vec_exact(N, beats):
    best = N
    rng = range(N)
    for order in itertools.permutations(rng):
        g = nx.Graph(); g.add_nodes_from(rng)
        for i in range(N):
            a = order[i]
            for j in range(i+1, N):
                b = order[j]
                if beats[b][a]:
                    g.add_edge(a, b)
        w = max((len(c) for c in nx.find_cliques(g)), default=1)
        if w < best:
            best = w
            if best <= 1:
                return best
    return best


# ---------- my own no-K-clique SAT oracle (re-derived inline) ----------

def transitive_ksubsets(N, beats, K):
    """Yield acyclic order (source..sink) for each transitive K-subset."""
    for S in itertools.combinations(range(N), K):
        outdeg = {x: sum(1 for y in S if y != x and beats[x][y]) for x in S}
        if sorted(outdeg.values()) != list(range(K)):
            continue
        order = sorted(S, key=lambda x: -outdeg[x])
        if all(beats[order[a]][order[b]] for a in range(K) for b in range(a+1, K)):
            yield order

def omega_vec_ge_K_sat(N, beats, K):
    """True iff omega_vec >= K, via UNSAT of 'exists order with no backedge K-clique'.

    Vars x_{u,v} = (u prec v). Clauses: transitivity; and for each transitive
    K-subset with acyclic order (s1..sK) (s1 source), forbid placing it fully
    reversed (sK prec ... prec s1) i.e. clause OR_i (s_i prec s_{i+1}).
    """
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
        for v in range(u+1, N):
            lit(u, v)
    for u in range(N):
        for v in range(N):
            if v == u: continue
            for w in range(N):
                if w in (u, v): continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    nclq = 0
    for order in transitive_ksubsets(N, beats, K):
        clause = [lit(order[i], order[i+1]) for i in range(K-1)]
        cnf.append(clause)
        nclq += 1
    with Cadical153(bootstrap_with=cnf.clauses) as s:
        sat = s.solve()
    return (not sat), nclq


def omega_vec_via_sat(N, beats, kmax=6):
    """Return exact omega_vec by finding largest K with omega>=K (UNSAT at K, SAT at K+1)."""
    val = 0
    for K in range(1, kmax+1):
        ge, _ = omega_vec_ge_K_sat(N, beats, K)
        if ge:
            val = K
        else:
            return val
    return val  # >= kmax


# ---------------------------- main ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--ns", type=str, default="")
    ap.add_argument("--allv", type=str, default="",
                    help="comma odd n: check ALL deleted vertices via SAT")
    ap.add_argument("--samplev", type=str, default="",
                    help="comma odd n: check a SAMPLE of deleted v (0,m,m+1 etc) via SAT")
    args = ap.parse_args()

    if args.validate:
        # validate SAT oracle vs exact brute force on small full + deleted instances
        print("=== VALIDATION SAT vs exact brute-force ===", flush=True)
        ok = True
        for n in [7]:
            N, beats, idx = build_AC_C3(n)
            assert check_tournament(N, beats), "AC_n[C3] not a tournament!"
            # too big (21) for full brute force; validate on small circulant + C3 etc.
        # validate on small tournaments where brute force is feasible (<=8 vertices)
        import random
        random.seed(1)
        # C3[C3] is 9 vertices -> feasible-ish (9! = 362880). do it.
        # build a few random small tournaments
        for trial in range(6):
            Nn = random.randint(4, 7)
            bm = [[False]*Nn for _ in range(Nn)]
            for u in range(Nn):
                for v in range(u+1, Nn):
                    if random.random() < 0.5: bm[u][v] = True
                    else: bm[v][u] = True
            exact = omega_vec_exact(Nn, bm)
            viasat = omega_vec_via_sat(Nn, bm)
            agree = exact == viasat
            ok = ok and agree
            print(f"  rand N={Nn}: exact={exact} sat={viasat} agree={agree}", flush=True)
        # AC7 deleted single vertex (N=20) -> exact infeasible; just print SAT
        print(f"VALIDATION ALL AGREE: {ok}", flush=True)
        return

    if args.allv:
        for n in [int(x) for x in args.allv.split(",") if x]:
            t0 = time.time()
            N, beats, idx = build_AC_C3(n)
            assert check_tournament(N, beats)
            results = {}
            bad = []
            for drop in range(N):
                Np, nb = delete_vertex(N, beats, drop)
                ge3, _ = omega_vec_ge_K_sat(Np, nb, 3)
                ge4, _ = omega_vec_ge_K_sat(Np, nb, 4)
                val = 3 if (ge3 and not ge4) else (4 if ge4 else "<3")
                results[drop] = val
                if val != 3:
                    bad.append((drop, val))
            distinct = sorted(set(results.values()), key=str)
            print(f"n={n} N={N} ALLv: distinct omega_vec values among deletions = {distinct} "
                  f"| #!=3 = {len(bad)} | bad={bad[:10]} | t={time.time()-t0:.1f}s", flush=True)
        return

    if args.samplev:
        for n in [int(x) for x in args.samplev.split(",") if x]:
            t0 = time.time()
            m = (n-1)//2
            N, beats, idx = build_AC_C3(n)
            assert check_tournament(N, beats)
            # sample several structurally-distinct deleted vertices (t,h)
            samples = [(0,0),(0,1),(0,2),(1,0),(1,1),(m,0),(m,1),(m+1,0),(m+1,2),
                       (2*m,0),(2*m,1),(m-1,2)]
            bad = []
            for (t,h) in samples:
                drop = idx(t,h)
                Np, nb = delete_vertex(N, beats, drop)
                ge3, _ = omega_vec_ge_K_sat(Np, nb, 3)
                ge4, _ = omega_vec_ge_K_sat(Np, nb, 4)
                val = 3 if (ge3 and not ge4) else (4 if ge4 else "<3")
                if val != 3:
                    bad.append(((t,h), val))
                print(f"  n={n} del (t={t},h={h}): ge3={ge3} ge4={ge4} ov={val}", flush=True)
            print(f"n={n} N={N} SAMPLEv done #!=3={len(bad)} bad={bad} t={time.time()-t0:.1f}s",
                  flush=True)
        return

    # default: full-graph omega_vec=4 sanity + deletion (0,0) for given ns
    ns = [int(x) for x in args.ns.split(",") if x] or [7,9,11]
    for n in ns:
        t0 = time.time()
        N, beats, idx = build_AC_C3(n)
        assert check_tournament(N, beats)
        # full
        g4, _ = omega_vec_ge_K_sat(N, beats, 4)
        g5, _ = omega_vec_ge_K_sat(N, beats, 5)
        full = 4 if (g4 and not g5) else ("5+" if g5 else "<4")
        # delete (0,0)
        Np, nb = delete_vertex(N, beats, idx(0,0))
        d3, _ = omega_vec_ge_K_sat(Np, nb, 3)
        d4, _ = omega_vec_ge_K_sat(Np, nb, 4)
        dval = 3 if (d3 and not d4) else (4 if d4 else "<3")
        print(f"n={n} N={N}: full omega_vec={full} | del(0,0) omega_vec={dval} "
              f"| t={time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
