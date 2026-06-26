"""Cross-verify the red-team finding two independent ways:
 (A) my from-scratch beats() vs the repo lex_compose/core tournament;
 (B) the explicit 8-vertex set is genuinely a transitive (acyclic) subtournament
     and forms a backedge clique under SOME order, computed via core.omega_vec on
     the induced subtournament.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import core
from ground_lex_compose_c3 import ac_gen, lex_compose
from search_4critical_circulant import circ_arcs


def ac_g(n):
    m = (n - 1) // 2
    return set(range(1, m)) | {m + 1}


def beats_scratch(u, v, n, g):
    a, b = u; a2, b2 = v
    if a != a2:
        return (a2 - a) % n in g
    return (b2 - b) % n in g


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    g = ac_g(n)

    # Build T = AC_n[AC_n] via repo lex_compose
    nAC, aAC = n, circ_arcs(n, g)
    assert core.is_tournament(nAC, aAC)
    N, A = lex_compose(nAC, aAC, nAC, aAC)
    assert core.is_tournament(N, A), "T not a tournament"
    beats = core.beats_matrix(N, A)

    def idx(a, b):
        return a * n + b

    # (A) consistency check: scratch beats == repo beats for all ordered pairs
    mism = 0
    for a in range(n):
        for b in range(n):
            for a2 in range(n):
                for b2 in range(n):
                    if (a, b) == (a2, b2):
                        continue
                    s = beats_scratch((a, b), (a2, b2), n, g)
                    r = beats[idx(a, b)][idx(a2, b2)]
                    if s != r:
                        mism += 1
    print(f"n={n}: scratch-vs-repo beats mismatches = {mism}")

    # The 8-vertex candidate from redteam_cells (one per cell, all 8 cells)
    m = (n - 1) // 2
    cand = [(m + 2, m + 2), (1, m + 2), (0, m + 2),
            (m + 2, 1), (1, 1), (0, 1),
            (m + 2, 0), (1, 0)]
    # Note redteam used a=4 at n=7 (=m+2=4). Recompute generically below instead.
    # Verify it's a transitive subtournament: induced subtournament acyclic.
    verts = cand
    flat = [idx(a, b) for (a, b) in verts]
    nn, sub = core.subtournament(N, A, flat)
    ov = core.omega_vec(nn, sub)
    print(f"n={n}: candidate 8-set induced subtournament order={nn} omega_vec={ov}")
    print(f"   verts={verts}")
    # If it's an acyclic (transitive) tournament on 8 vertices, omega_vec==8.
    # Print the cells.
    def cval(t):
        if t == 0: return 3
        if 1 <= t <= m: return 2
        return 1
    cells = [(cval(b), cval(a)) for (a, b) in verts]
    print(f"   cells={cells}  (distinct: {len(set(cells))})")

    # confirm acyclic by score sequence under scratch beats
    outdeg = sorted(sum(1 for v in verts if v != u and beats_scratch(u, v, n, g))
                    for u in verts)
    print(f"   out-degree score sequence within set = {outdeg}  (transitive iff {list(range(8))})")

    # also: what does omega_vec of the WHOLE deleted tournament say?
    surv = [idx(a, b) for a in range(n) for b in range(n) if (a, b) != (0, 0)]
    nn2, sub2 = core.subtournament(N, A, surv)
    if nn2 <= 12:
        ovd = core.omega_vec(nn2, sub2)
        print(f"n={n}: omega_vec(T-(0,0)) via core (order={nn2}) = {ovd}  (proof claims 4)")


if __name__ == "__main__":
    main()
