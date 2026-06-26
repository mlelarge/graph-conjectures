"""Ground the literature-reduction proposal: import the EXPLICIT vertex-critical
5-dichromatic circulant family of Neumann-Lara (DMGT 20 (2000) 197-207), namely
Prop 6.5:  F5 = { C3[ C_{2m+1}(I_{m,m}) ] : m >= 3 },  and oracle-test the smallest
members for (dic=5, vertex-critical, omega_vec=5).

Definitions (paper sec 2): I_m={1..m}; I_{m,j}=I_m u {2m+1-j} - {j} in Z_{2m+1}.
So I_{m,m}={1..m-1} u {m+1}.  m=3 -> Z7, I_{3,3}={1,2,4}=AC_7.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from lexlib import AC, lex_substitute, is_tournament, C3
from ground_lift_lemma_step1 import dic, dic_vertex_critical
from pysat.formula import CNF
from pysat.solvers import Cadical153


def Imm(m):
    n = 2 * m + 1
    g = sorted(set(range(1, m)) | {m + 1})
    return n, g


def out_masks(n, arcs):
    out = [0] * n
    for (u, v) in arcs:
        out[u] |= (1 << v)
    return out


def enumerate_transitive_sets(n, out, K):
    """All transitive (acyclic) K-subsets as source-first chains; each set once."""
    chains = []

    def rec(chosen, cand_mask):
        if len(chosen) == K:
            chains.append(tuple(chosen)); return
        m = cand_mask
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            rec(chosen + [v], cand_mask & out[v])
    for s in range(n):
        rec([s], out[s])
    return chains


def decide_ov_ge5(n, arcs):
    """no-K5 SAT: build a tournament order (transitive tournament var x_uv) avoiding
    any monochromatic K5 (transitive 5-set). SAT  => exists order with omega(backedge)<=4
    => ov<=4.  UNSAT => every order has a transitive 5-set in forward dir => ov>=5.
    Returns (ov_ge5: bool, n_trans5, solve_s)."""
    out = out_masks(n, arcs)
    chains = enumerate_transitive_sets(n, out, 5)
    idx = {}; nv = [0]

    def lit(u, v):
        if (u, v) in idx: return idx[(u, v)]
        if (v, u) in idx: return -idx[(v, u)]
        nv[0] += 1; idx[(u, v)] = nv[0]; return nv[0]
    for u in range(n):
        for v in range(u + 1, n):
            lit(u, v)
    cnf = CNF()
    for u in range(n):
        for v in range(n):
            if v == u: continue
            for w in range(n):
                if w == u or w == v: continue
                cnf.append([-lit(u, v), -lit(v, w), lit(u, w)])  # transitivity of order
    for ch in chains:
        cnf.append([lit(ch[i], ch[i + 1]) for i in range(4)])    # forbid this K5 forward
    t = time.time()
    with Cadical153(bootstrap_with=cnf.clauses) as mdl:
        sat = mdl.solve()
    return (not sat), len(chains), round(time.time() - t, 1)


def analyze(m):
    n_in, g = Imm(m)
    inner = AC(n_in, g)
    assert is_tournament(*inner), (n_in, g)
    N, arcs = lex_substitute(C3, inner)          # C3[C_{2m+1}(I_{m,m})], order 3(2m+1)
    assert is_tournament(N, arcs)
    d = dic(N, arcs, kmax=7)
    crit, dels = dic_vertex_critical(N, arcs, d, vt=False)
    ov_ge5, n_t5, sat_s = decide_ov_ge5(N, arcs)
    return dict(m=m, inner_n=n_in, inner_g=g, order=N, dic=d,
                dic_vertex_critical=crit, omega_vec_ge5=ov_ge5,
                n_transitive5=n_t5, noK5_sat_s=sat_s,
                del_dic_values=sorted(set(v for _, v in dels)))


if __name__ == "__main__":
    ms = [int(x) for x in sys.argv[1:]] or [3]
    for m in ms:
        r = analyze(m)
        print(f"F5 m={m}: C3[C_{r['inner_n']}({r['inner_g']})] order={r['order']} "
              f"dic={r['dic']} vc={r['dic_vertex_critical']} "
              f"del_dic={r['del_dic_values']} omega_vec>=5? {r['omega_vec_ge5']} "
              f"(n_trans5={r['n_transitive5']}, noK5_SAT_s={r['noK5_sat_s']})",
              flush=True)
        print("  CHECK dic==5:", r['dic'] == 5, " vc:", r['dic_vertex_critical'],
              " omega_vec>=5:", r['omega_vec_ge5'], flush=True)
