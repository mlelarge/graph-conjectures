"""(b) UPPER bound omega_vec(AC_7[C3[C3]]) <= 5 via the NSS merged-key order.

The witnessing order = sort vertices (a outer in AC_7, b inner in C3[C3]) by key
  ( cAC(a) + cH(b),  ... tie-break ),
where c(.) is the NSS longest-prec-DECREASING-path potential of each factor
under its omega_vec-optimal order (max value = ov of that factor = 3).  This is
the exact technique cited (Refs/2310.04265.tex:522-524).  Report the backedge
clique number under this merged-key order = a valid UPPER bound on omega_vec.

We DERIVE the per-factor potentials from the factor's optimal order via the
decreasing-path DP, rather than hard-coding the AC_7 band formula, so it applies
to the composite inner C3[C3] too.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core, networkx as nx
import constructions as C
from law_exact_sweep import lex_compose


def circ(p, g):
    return [(i, j) for i in range(p) for j in range(p)
            if i != j and ((j - i) % p) in g]


def optimal_order(n, arcs):
    beats = core.beats_matrix(n, arcs)
    best, bw = None, n + 1
    for perm in itertools.permutations(range(n)):
        w = core.omega_of_order(n, arcs, list(perm))
        if w < bw:
            bw, best = w, list(perm)
            if bw == 1:
                break
    return best, bw, beats


def nss_potential(order, beats):
    """phi(x) = #vertices of a longest prec-DECREASING path in the backedge graph
    ending at x. Backedge edge a-b (a before b) iff b beats a.  A decreasing path
    x1>x2>... in prec means indices descending; potential = clique-bounding
    longest-decreasing chain ending at x.  Compute by DP over positions."""
    pos = {v: i for i, v in enumerate(order)}
    n = len(order)
    # backedge adjacency
    adj = {v: set() for v in order}
    for i in range(n):
        a = order[i]
        for j in range(i + 1, n):
            b = order[j]
            if beats[b][a]:
                adj[a].add(b); adj[b].add(a)
    # phi(x): longest decreasing (in prec) path in backedge graph ending at x.
    # process in prec order; phi(x)=1+max phi(y) over y prec x with edge y-x.
    phi = {}
    for i in range(n):
        x = order[i]
        best = 0
        for j in range(i):
            y = order[j]
            if y in adj[x]:
                best = max(best, phi[y])
        phi[x] = best + 1
    return phi


def clique_of_order(beats, order):
    g = nx.Graph(); g.add_nodes_from(order)
    L = len(order)
    for i in range(L):
        a = order[i]
        for j in range(i + 1, L):
            b = order[j]
            if beats[b][a]:
                g.add_edge(a, b)
    return max((len(c) for c in nx.find_cliques(g)), default=0)


def main():
    C3 = C.directed_C3()
    nH, aH = lex_compose(C3[0], C3[1], C3[0], C3[1])   # C3[C3] order 9
    aAC = circ(7, {1, 2, 4})

    oAC, wAC, bAC = optimal_order(7, aAC)
    oH, wH, bH = optimal_order(nH, aH)
    print(f"AC7 opt order omega={wAC}; C3[C3] opt order omega={wH}", flush=True)

    cAC = nss_potential(oAC, bAC)   # values 1..3
    cH = nss_potential(oH, bH)      # values 1..3
    print("AC7 potential values:", sorted(cAC.values()), flush=True)
    print("C3[C3] potential values:", sorted(cH.values()), flush=True)

    nb, ab = lex_compose(7, aAC, nH, aH)
    beats = core.beats_matrix(nb, ab)

    # merged-key order: vertex f -> outer a=f//9, inner b=f%9
    def key(f):
        a = f // 9; b = f % 9
        return (cAC[a] + cH[b], cAC[a], cH[b], a, b)
    order = sorted(range(nb), key=key)
    w = clique_of_order(beats, order)
    print(f"MERGED-KEY (NSS) order backedge clique (UPPER bound) = {w}", flush=True)
    print(f"prediction pred = ovAC + ovH - 1 = 3+3-1 = 5; "
          f"{'UPPER<=5 OK' if w <= 5 else 'UPPER>5'}", flush=True)

    # also report best over a few merged-key tie-break variants
    variants = {}
    for kf, name in [
        (lambda f: (cAC[f // 9] + cH[f % 9], cH[f % 9], cAC[f // 9], f // 9, f % 9), "innerfirst_tie"),
        (lambda f: (cH[f % 9] + cAC[f // 9], f // 9, f % 9), "plain"),
    ]:
        o = sorted(range(nb), key=kf)
        variants[name] = clique_of_order(beats, o)
    print("variants:", variants, flush=True)


if __name__ == "__main__":
    main()
