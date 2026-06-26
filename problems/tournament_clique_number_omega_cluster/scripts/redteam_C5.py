"""INDEPENDENT red-team of claim C5 (proof_omega_AC_n_C3 + proof_deletion).

Built from scratch. Does NOT import core/oracle. AC_n and AC_n[C3] are
constructed directly from definitions. omega_vec is computed two ways:
  (1) direct backedge-clique for a fixed order (sanity / lower-witness),
  (2) generalized no-K_{k+1} SAT betweenness oracle for EXACT bounds:
        omega_vec <= k   iff  the "no K_{k+1} in any backedge graph" CNF is SAT
        omega_vec >= k   iff  the "no K_k"      CNF is UNSAT.
"""
import sys, itertools, argparse, json
from pysat.solvers import Minisat22
from pysat.formula import CNF
import networkx as nx


# ---------- direct construction of AC_n and AC_n[C3] ----------

def ac_g(m):
    """connection set g = {1..m-1} U {m+1}, n = 2m+1."""
    return set(range(1, m)) | {m + 1}

def ac_n_beats(m):
    """AC_n: beats[i][j] iff (j-i) mod n in g.  Returns (n, beats matrix)."""
    n = 2 * m + 1
    g = ac_g(m)
    beats = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if (j - i) % n in g:
                beats[i][j] = True
    return n, beats

def assert_tournament(N, beats, label=""):
    for i in range(N):
        for j in range(i + 1, N):
            if beats[i][j] == beats[j][i]:
                raise AssertionError(f"{label}: pair ({i},{j}) not a tournament: "
                                     f"beats[i][j]={beats[i][j]} beats[j][i]={beats[j][i]}")
    return True

def c3_beats():
    # 0->1->2->0
    b = [[False]*3 for _ in range(3)]
    b[0][1] = b[1][2] = b[2][0] = True
    return b

def lex_substitution_beats(m):
    """AC_n[C3]. Vertices (t,h), t in [0,n), h in [0,3).
    arc (t,h)->(t',h') iff (t!=t' and t->t' in AC_n) or (t==t' and h->h' in C3).
    Returns (N, beats, idx) where idx maps (t,h)->vertex id and inv maps back."""
    n, ac = ac_n_beats(m)
    c3 = c3_beats()
    verts = [(t, h) for t in range(n) for h in range(3)]
    idx = {v: i for i, v in enumerate(verts)}
    N = len(verts)
    beats = [[False] * N for _ in range(N)]
    for (t, h) in verts:
        for (t2, h2) in verts:
            if (t, h) == (t2, h2):
                continue
            if t != t2:
                arc = ac[t][t2]
            else:
                arc = c3[h][h2]
            beats[idx[(t, h)]][idx[(t2, h2)]] = arc
    return N, beats, idx, verts, n


# ---------- direct backedge clique for a FIXED order ----------

def backedge_clique_number(N, beats, order):
    g = nx.Graph(); g.add_nodes_from(range(N))
    pos = {v: i for i, v in enumerate(order)}
    for a in range(N):
        for b in range(a + 1, N):
            u, v = order[a], order[b]   # u precedes v
            if beats[v][u]:             # backward arc v->u
                g.add_edge(u, v)
    return max((len(c) for c in nx.find_cliques(g)), default=1)


# ---------- generalized no-K_{k} SAT betweenness oracle ----------

def build_no_clique_cnf(N, beats, k):
    """CNF that is SAT iff there is a total order whose backedge graph has NO K_k.

    Order vars: p(u,v) means u<v (u precedes v).  p(v,u) = -p(u,v).
    Transitivity: (u<v)&(v<w) -> (u<w).
    Backedge edge between u,v exists (in any fixed order) iff the LATER one beats
    the EARLIER one. For a candidate clique set Q={q_0..q_{k-1}}, all pairs must
    be backedges. Given a linear order of Q, pair (earlier x, later y) is an edge
    iff beats[y][x]. So Q is a backedge clique under SOME order iff there's a
    linear arrangement of Q with every (earlier,later) pair a backward arc.

    Equivalent: Q forms a clique iff for the chosen order restricted to Q, for
    every pair {x,y}, the later beats the earlier. We forbid, for every k-subset
    Q and every permutation pi of Q, the conjunction of order literals realizing
    pi WHEN that permutation makes all pairs backedges.

    A permutation x_0<x_1<...<x_{k-1} makes all pairs backedges iff for all i<j,
    beats[x_j][x_i]. Forbid that arrangement: clause = OR over i<j of NOT(x_i<x_j)
    ... but we only need the covering pairs of the linear order. Standard trick:
    forbid the chain x_0<x_1, x_1<x_2, ..., x_{k-2}<x_{k-1} (transitivity gives
    the rest). Clause: (x_0>x_1) OR (x_1>x_2) OR ... OR (x_{k-2}>x_{k-1}).
    """
    idx = {}; nv = [0]
    def lit(u, v):
        if (u, v) in idx: return idx[(u, v)]
        if (v, u) in idx: return -idx[(v, u)]
        nv[0] += 1; idx[(u, v)] = nv[0]; return nv[0]
    cnf = CNF()
    # transitivity
    for u in range(N):
        for v in range(N):
            if v == u: continue
            for w in range(N):
                if w == u or w == v: continue
                # (u<v) & (v<w) -> (u<w)
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])
    # forbid every k-clique realization
    for Q in itertools.combinations(range(N), k):
        for perm in itertools.permutations(Q):
            # this arrangement is a clique iff later beats earlier for all i<j;
            # since transitivity handles non-adjacent pairs, require all C(k,2)
            ok = True
            for i in range(k):
                for j in range(i + 1, k):
                    if not beats[perm[j]][perm[i]]:
                        ok = False; break
                if not ok: break
            if not ok:
                continue
            # forbid chain perm[0]<perm[1]<...<perm[k-1]
            clause = [-lit(perm[i], perm[i + 1]) for i in range(k - 1)]
            cnf.append(clause)
    return cnf

def omega_vec_sat_at_most(N, beats, k):
    """True iff omega_vec <= k (i.e. exists order with no K_{k+1})."""
    cnf = build_no_clique_cnf(N, beats, k + 1)
    with Minisat22(bootstrap_with=cnf.clauses) as s:
        return s.solve()

def omega_vec_exact(N, beats, lo=1, hi=None):
    """Exact omega_vec by binary-ish probing with SAT oracle."""
    if hi is None: hi = N
    # find smallest k with omega_vec <= k
    k = lo
    while k <= hi:
        if omega_vec_sat_at_most(N, beats, k):
            return k
        k += 1
    return hi


# ---------- vertex-transitivity check ----------

def is_vertex_transitive(N, beats):
    """Check AC_n[C3] is vertex-transitive by exhibiting, for the rotation
    automorphism t->t+1 (mod n) on AC_n lifted to blocks, that it's an
    automorphism and acts transitively on blocks; plus C3 rotation handles h.
    We verify directly: build automorphisms (t,h)->(t+s mod n, h) for all s and
    (t,h)->(t, h+r mod 3)?? -- but block rotation only gives n orbits of size 3.
    Need within-block transitivity too. AC_n[C3]: is C3 vertex-transitive? yes.
    So group generated by block-rotation x within-block-rotation acts
    transitively. We VERIFY each generator is an automorphism and orbit = all.
    """
    n = N // 3
    # generator A: (t,h) -> (t+1 mod n, h)   [block rotation]
    # generator B: (t,h) -> (t, (h+1) mod 3) [within-block C3 rotation]
    verts = [(t, h) for t in range(n) for h in range(3)]
    idx = {v: i for i, v in enumerate(verts)}
    def perm_from(f):
        return [idx[f(verts[i])] for i in range(N)]
    def is_auto(p):
        for i in range(N):
            for j in range(N):
                if i == j: continue
                if beats[i][j] != beats[p[i]][p[j]]:
                    return False
        return True
    A = perm_from(lambda v: ((v[0] + 1) % n, v[1]))
    B = perm_from(lambda v: (v[0], (v[1] + 1) % 3))
    autoA = is_auto(A); autoB = is_auto(B)
    # orbit of vertex 0 under <A,B>
    from collections import deque
    gens = [A, B]
    orbit = {0}; dq = deque([0])
    while dq:
        x = dq.popleft()
        for p in gens:
            y = p[x]
            if y not in orbit:
                orbit.add(y); dq.append(y)
    return {"A_block_rot_is_auto": autoA, "B_c3_rot_is_auto": autoB,
            "orbit_size": len(orbit), "N": N,
            "vertex_transitive": autoA and autoB and len(orbit) == N}


# ---------- the lower-bound lex witnesses ----------

def omega_vec_at_least_4(N, beats):
    """True iff omega_vec >= 4, i.e. NO order avoids a K4: no-K4 CNF UNSAT."""
    cnf = build_no_clique_cnf(N, beats, 4)
    with Minisat22(bootstrap_with=cnf.clauses) as s:
        sat = s.solve()
    return not sat  # UNSAT => every order has K4 => omega_vec>=4

def omega_vec_at_least_3(N, beats):
    cnf = build_no_clique_cnf(N, beats, 3)
    with Minisat22(bootstrap_with=cnf.clauses) as s:
        sat = s.solve()
    return not sat

def find_lex_4clique(m):
    """Independently realize the proof's 'fatten the source rep' witness.
    Build merged order key(t,h)=c(t)+d(h); find an explicit 4-clique in the
    backedge graph of that order. Returns the 4 vertices and verifies they are
    pairwise backedges under the order."""
    N, beats, idx, verts, n = lex_substitution_beats(m)
    def c(t):
        if t == 0: return 3
        if 1 <= t <= m: return 2
        return 1
    def d(h):
        return 2 if h == 0 else 1
    order = sorted(range(N), key=lambda i: (c(verts[i][0]) + d(verts[i][1]),
                                            verts[i][0], verts[i][1]))
    g = nx.Graph(); g.add_nodes_from(range(N))
    pos = {v: p for p, v in enumerate(order)}
    for a in range(N):
        for b in range(a+1, N):
            u, v = order[a], order[b]
            if beats[v][u]:
                g.add_edge(u, v)
    cliques = list(nx.find_cliques(g))
    mx = max(len(c_) for c_ in cliques)
    best = max(cliques, key=len)
    return {"m": m, "merged_order_clique_number": mx,
            "example_max_clique_verts": [verts[i] for i in best]}

def deletion_lb_witness(m):
    """Lower bound omega_vec(AC_n[C3]-v) >= 3 via constant-h copy (h=1).
    The induced subdigraph on {(t,1): t} is a full AC_n. We verify it has
    omega_vec=3 (so any order of the deleted graph has a backedge K3 inside)."""
    N, beats, idx, verts, n = lex_substitution_beats(m)
    # constant h=1 copy (avoids deleted v=(0,0))
    sub = [idx[(t, 1)] for t in range(n)]
    sub_idx = {v: i for i, v in enumerate(sub)}
    nn = len(sub)
    bsub = [[beats[sub[a]][sub[b]] for b in range(nn)] for a in range(nn)]
    w = omega_vec_exact(nn, bsub, lo=1)
    return {"m": m, "n": n, "constant_h1_copy_omega_vec": w}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, nargs="+", default=[3,4,5,6,7])
    ap.add_argument("--mode", default="all",
                    choices=["all","omega","deletion","vt","fixedorder","lb"])
    ap.add_argument("--sat-cap-N", type=int, default=33,
                    help="skip SAT exact above this N (k+1-clique enum blows up)")
    args = ap.parse_args()

    results = []
    for m in args.m:
        rec = {"m": m, "n": 2*m+1}
        N, beats, idx, verts, n = lex_substitution_beats(m)
        rec["N"] = N
        assert_tournament(N, beats, f"AC_{n}[C3]")
        # also assert AC_n itself
        nA, ac = ac_n_beats(m)
        assert_tournament(nA, ac, f"AC_{n}")
        rec["is_tournament"] = True

        if args.mode in ("all","vt"):
            rec["vt"] = is_vertex_transitive(N, beats)

        if args.mode == "lb":
            # C5 core: omega_vec(AC_n[C3]) >= 4  and the lex witness realizes 4
            rec["omega_vec_ge_4"] = omega_vec_at_least_4(N, beats)
            rec["lex_witness"] = find_lex_4clique(m)
            # deletion lower bound >= 3 via constant-h copy
            rec["lb_witness"] = deletion_lb_witness(m)
            keep = [i for i in range(N) if i != idx[(0,0)]]
            nn = len(keep)
            bdel = [[beats[keep[a]][keep[b]] for b in range(nn)] for a in range(nn)]
            rec["minus_v00_omega_ge_3"] = omega_vec_at_least_3(nn, bdel)

        if args.mode in ("all","omega") and N <= args.sat_cap_N:
            w = omega_vec_exact(N, beats, lo=1)
            rec["omega_vec_AC_C3"] = w

        if args.mode in ("all","deletion"):
            # delete v=(0,0)
            keep = [i for i in range(N) if i != idx[(0,0)]]
            kidx = {v: i for i, v in enumerate(keep)}
            nn = len(keep)
            bdel = [[beats[keep[a]][keep[b]] for b in range(nn)] for a in range(nn)]
            rec["lb_witness"] = deletion_lb_witness(m)
            if nn <= args.sat_cap_N:
                wdel = omega_vec_exact(nn, bdel, lo=1)
                rec["omega_vec_AC_C3_minus_v00"] = wdel
            # also delete a NON-(0,0) vertex to stress vertex-transitivity claim
            keep2 = [i for i in range(N) if i != idx[(0,1)]]
            nn2 = len(keep2)
            bdel2 = [[beats[keep2[a]][keep2[b]] for b in range(nn2)] for a in range(nn2)]
            if nn2 <= args.sat_cap_N:
                rec["omega_vec_AC_C3_minus_v01"] = omega_vec_exact(nn2, bdel2, lo=1)

        results.append(rec)
        print(json.dumps(rec, default=str))
        sys.stdout.flush()

    print("=== SUMMARY ===")
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    main()
