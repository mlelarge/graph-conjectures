"""SKEPTIC independent attack on the AC4_21 4-omega_vec-critical claim.

The load-bearing leg is omega_vec(AC4_21) >= 4, decided ONLY by the no-K4 SAT
encoding (exact bb infeasible at n=21). I re-implement EVERYTHING from scratch,
with a DIFFERENT clique-detection clause structure, and validate against exact
core.omega_vec / omega_vec_bb on circulants up to n=13 (exact bb feasible there).

Independent encoding choice: instead of "forbid the reverse placement of a
transitive K-subset", I encode the backedge-graph clique directly. A K-clique in
the backedge graph for the order < is a set of K vertices {v1..vK} such that for
every pair, the LATER one (in <) beats the EARLIER one. I forbid, for EACH
ordered K-tuple that is a transitive chain top->...->sink, the FULL set of
pairwise reversed atoms (a clause over all C(K,2) atoms, not just consecutive).
This is logically the SAME forbidden set but a DIFFERENT (stronger-looking,
but equivalent under transitivity) clause -- a genuine cross-check of the
proposal's "consecutive-only" minimization.
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(__file__))
import core
from pysat.solvers import Cadical153, Minisat22
from pysat.formula import CNF

N = 21
G = {1, 2, 4, 7, 8, 9, 11, 15, 16, 18}


def circ_arcs(p, g):
    return [(i, (i + d) % p) for i in range(p) for d in g]


def build_cnf_full_clause(n, arcs, K):
    """Independent CNF: SAT iff some order's backedge graph is K_K-free.
    For each transitive K-subset (acyclic order s_1->..->s_K, s_a beats s_b a<b),
    the backedge K-clique appears iff the order places s_K<...<s_1, i.e. ALL
    pairs s_b < s_a for a<b. Forbid via clause OR_{a<b}(s_a < s_b)  [C(K,2) lits].
    """
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
    for S in itertools.combinations(range(n), K):
        outdeg = {x: sum(1 for y in S if y != x and beats[x][y]) for x in S}
        if sorted(outdeg.values()) != list(range(K)):
            continue
        order = sorted(S, key=lambda x: -outdeg[x])  # s_1=source .. s_K=sink
        if not all(beats[order[a]][order[b]] for a in range(K) for b in range(a + 1, K)):
            continue
        # forbid s_K<...<s_1: ALL pairs (s_a < s_b) for a<b  (full-clause variant)
        clause = [lit(order[a], order[b]) for a in range(K) for b in range(a + 1, K)]
        cnf.append(clause)
        nclq += 1
    return cnf, nclq


def ge_K(n, arcs, K):
    cnf, _ = build_cnf_full_clause(n, arcs, K)
    with Cadical153(bootstrap_with=cnf.clauses) as s:
        sat_c = s.solve()
    with Minisat22(bootstrap_with=cnf.clauses) as s:
        sat_m = s.solve()
    assert sat_c == sat_m, f"solver disagree K={K}"
    return not sat_c  # ge_K iff UNSAT


def validate_against_exact():
    """Validate my INDEPENDENT full-clause encoding vs exact core.omega_vec
    on circulants up to n=13 (exact bb feasible), K=2,3,4,5. Plus 400 random
    tournaments n in {5,6,7,8} K=2,3,4. ZERO mismatches required."""
    mism = []
    # circulants n<=13
    for p in [7, 9, 11, 13]:
        m = (p - 1) // 2
        pairs = [(d, p - d) for d in range(1, m + 1)]
        seen = 0
        for mask in range(1 << m):
            g = set(pairs[b][1] if (mask >> b) & 1 else pairs[b][0] for b in range(m))
            negg = set((-d) % p for d in g)
            if g & negg or len(g) != m:
                continue
            seen += 1
            if seen > 30:  # sample 30 valid generators per p
                break
            arcs = circ_arcs(p, g)
            ov = core.omega_vec(p, arcs)
            for K in (2, 3, 4, 5):
                pred = ge_K(p, arcs, K)
                truth = ov >= K
                if pred != truth:
                    mism.append(("circ", p, sorted(g), K, ov, pred))
    # random tournaments
    rng = random.Random(99)
    for n in [5, 6, 7, 8]:
        for _ in range(100):
            arcs = []
            for i in range(n):
                for j in range(i + 1, n):
                    arcs.append((i, j) if rng.random() < 0.5 else (j, i))
            ov = core.omega_vec(n, arcs)
            for K in (2, 3, 4):
                pred = ge_K(n, arcs, K)
                truth = ov >= K
                if pred != truth:
                    mism.append(("rand", n, arcs, K, ov, pred))
    return mism


def main():
    arcs = circ_arcs(N, G)
    print("is_tournament:", core.is_tournament(N, arcs), flush=True)

    # 1. independent encoding validation
    mism = validate_against_exact()
    print(f"INDEP full-clause encoding mismatches vs exact omega_vec: {len(mism)}", flush=True)
    if mism:
        print("MISMATCHES:", mism[:5], flush=True)
        print("ENCODING UNSOUND -> lower bound NOT trustworthy", flush=True)
        return

    # 2. independent upper bound via Bron-Kerbosch (core.omega_of_order) over rotations
    best = min(core.omega_of_order(N, arcs, [(i + r) % N for i in range(N)]) for r in range(N))
    id_clique = core.omega_of_order(N, arcs, list(range(N)))
    print(f"UPPER (min over rotations, exact BK clique): {best}; identity-order clique: {id_clique}", flush=True)

    # 3. independent lower bound (full-clause encoding) K=4 and K=5
    ge4 = ge_K(N, arcs, 4)
    ge5 = ge_K(N, arcs, 5)
    print(f"INDEP omega_vec>=4: {ge4}; omega_vec>=5: {ge5}", flush=True)
    ov = 4 if (ge4 and not ge5 and best <= 4) else "INCONCLUSIVE"
    print(f"=> omega_vec(AC4_21) = {ov}", flush=True)

    # 4. deletion of vertex 0 (independent)
    nn, sub = core.subtournament(N, arcs, [w for w in range(N) if w != 0])
    dge3 = ge_K(nn, sub, 3)
    dge4 = ge_K(nn, sub, 4)
    dup = min(core.omega_of_order(nn, sub, p) for p in
              [list(range(nn))] + [random.Random(s).sample(range(nn), nn) for s in range(50)])
    print(f"deletion0: ge3={dge3} ge4={dge4} upper={dup}", flush=True)
    delov = 3 if (dge3 and not dge4 and dup <= 3) else "INCONCLUSIVE"
    print(f"=> omega_vec(AC4_21 - 0) = {delov}", flush=True)

    crit = (ov == 4 and delov == 3)
    print(f"\n*** INDEP is_4_omega_vec_critical: {crit} ***", flush=True)


if __name__ == "__main__":
    main()
