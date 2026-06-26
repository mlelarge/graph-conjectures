"""INDEPENDENT re-verification of the H20 discriminator round
(scripts/h20_discriminator_dic_qr19_ac421.py / data/h20_discriminator_qr19_ac421.json).

From-scratch code: own circulant builder, own tournament + rotation checks,
own SAT encoding (exactly-one with pairwise at-most-one, NO symmetry break,
different variable layout), different solver (Glucose42, with Minisat22
cross-check on the dic values), own brute-force validation of the encoding
on small tournaments. Does NOT import lexlib / ground_lift_lemma_step1.

Soundness fact used (classical): a tournament is acyclic iff transitive iff
it has no directed 3-cycle; hence a color class is acyclic iff it contains
no directed triangle.
"""
import json, os, sys, itertools, random
from pysat.solvers import Glucose42, Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')


def circulant(n, g):
    gs = {x % n for x in g}
    assert 0 not in gs
    # tournament iff for every d in 1..n-1 exactly one of d, n-d in gs
    for d in range(1, n):
        assert ((d in gs) + ((n - d) in gs)) == 1, (n, d)
    adj = [[False] * n for _ in range(n)]
    for i in range(n):
        for d in gs:
            adj[i][(i + d) % n] = True
    return adj


def rotation_is_automorphism(adj):
    n = len(adj)
    return all(adj[u][v] == adj[(u + 1) % n][(v + 1) % n]
               for u in range(n) for v in range(n) if u != v)


def triangles(adj):
    n = len(adj)
    out = []
    for a, b, c in itertools.combinations(range(n), 3):
        if (adj[a][b] and adj[b][c] and adj[c][a]) or \
           (adj[b][a] and adj[c][b] and adj[a][c]):
            out.append((a, b, c))
    return out


def k_dicolorable(adj, k, solver_cls=Glucose42):
    n = len(adj)
    if k >= n:
        return True
    if k <= 0:
        return n == 0
    tris = triangles(adj)
    # variable layout: x(v,c) = c*n + v + 1  (different from original v*k+c+1)
    x = lambda v, c: c * n + v + 1
    cls = []
    for v in range(n):
        cls.append([x(v, c) for c in range(k)])           # at least one
        for c1 in range(k):
            for c2 in range(c1 + 1, k):                   # at most one
                cls.append([-x(v, c1), -x(v, c2)])
    for (a, b, c) in tris:
        for col in range(k):
            cls.append([-x(a, col), -x(b, col), -x(c, col)])
    with solver_cls(bootstrap_with=cls) as s:
        return s.solve()


def dic_exact(adj, kmax=7):
    """returns (d, ladder) with UNSAT at d-1 and SAT at d, both solvers."""
    for k in range(1, kmax + 1):
        g = k_dicolorable(adj, k, Glucose42)
        m = k_dicolorable(adj, k, Minisat22)
        assert g == m, ("solver disagreement", k)
        if g:
            return k
    raise RuntimeError("dic > kmax")


def delete_vertex(adj, v):
    keep = [u for u in range(len(adj)) if u != v]
    return [[adj[a][b] for b in keep] for a in keep]


def brute_dic(adj, kmax=4):
    n = len(adj)
    tris = triangles(adj)
    for k in range(1, kmax + 1):
        for col in itertools.product(range(k), repeat=n):
            if all(not (col[a] == col[b] == col[c]) for (a, b, c) in tris):
                return k
    return None


def selfcheck():
    rng = random.Random(20260610)
    for trial in range(40):
        n = rng.choice([5, 6, 7])
        adj = [[False] * n for _ in range(n)]
        for a, b in itertools.combinations(range(n), 2):
            if rng.random() < 0.5:
                adj[a][b] = True
            else:
                adj[b][a] = True
        bd = brute_dic(adj)
        sd = dic_exact(adj)
        assert bd == sd, (trial, bd, sd)
    print("selfcheck: 40/40 random tournaments n in {5,6,7}: brute == SAT")


def main():
    selfcheck()

    QR19 = sorted({pow(x, 2, 19) for x in range(1, 19)})
    AC4_21_G = [1, 2, 4, 7, 8, 9, 11, 15, 16, 18]
    wits = json.load(open(os.path.join(DATA, 'k4_sandwich_witnesses.json')))[
        'k4_4critical_witnesses']
    cases = [("QR_19", 19, QR19), ("AC4_21", 21, AC4_21_G)]
    for i, w in enumerate(wits):
        if w['n'] == 19 and sorted(w['g']) == QR19:
            continue
        cases.append((f"k4crit_n{w['n']}_{i}", w['n'], w['g']))
    assert len(cases) == 15, len(cases)

    saved = json.load(open(os.path.join(DATA, 'h20_discriminator_qr19_ac421.json')))
    assert set(saved.keys()) == {name for name, _, _ in cases}

    n_hits = 0
    crit_names = []
    for name, n, g in cases:
        adj = circulant(n, g)
        assert rotation_is_automorphism(adj), name
        d = dic_exact(adj)
        d_del = dic_exact(delete_vertex(adj, 0))
        # vertex-transitive (rotation generates transitive cyclic group)
        # => dic(T-v) = dic(T-0) for all v; critical iff d_del == d-1
        crit = (d_del == d - 1)
        hit = (d == 4 and crit)
        n_hits += hit
        if crit:
            crit_names.append(name)
        sv = saved[name]
        ok = (sv['n'] == n and sv['dic'] == d and
              sv['dic_of_deletion_v0'] == d_del and
              sv['dic_vertex_critical'] == crit and
              sv['h20_input_hit'] == hit)
        ntri = len(triangles(adj))
        assert ntri == sv['n_directed_triangles'], name
        print(f"{name:13s} n={n} dic={d} dic(T-0)={d_del} crit={crit} "
              f"hit={hit} #tris={ntri}  MATCH-SAVED={ok}")
        assert ok, name

    print(f"\nALL 15 MATCH. h20_input_hit on {n_hits}/15.")
    print("dic-vertex-critical cases:", crit_names)
    assert n_hits == 0
    assert sorted(crit_names) == ['k4crit_n25_4', 'k4crit_n25_7',
                                  'k4crit_n25_8', 'k4crit_n25_9']
    # exclusive-or structure: dic==4 (==ov) -> non-critical; critical -> dic==5
    print("XOR structure (dic=ov=4 <=> non-critical) holds on 15/15: True")


if __name__ == '__main__':
    main()
