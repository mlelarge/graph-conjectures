"""Independent lower bound on omega_vec via the dominant-set / SAT-free characterization.

KEY FACT (standard, also used in repo): omega_vec(D) = min over linear orders of the
clique number of the backedge graph. There is a classical reformulation:
omega_vec(D) >= k  iff  D contains a sub-tournament with NO acyclic ordering avoiding a
backedge K_k... Actually the clean independent certificate of a LOWER bound omega_vec>=k:

A LOWER bound omega_vec(D) >= k is certified by exhibiting a sub-tournament A such that
for EVERY linear order of A, the backedge graph has a clique of size >= k. The simplest
such certificate: a "dominated" structure. We instead use the direct LB via the known
identity omega_vec(D) = the minimum number of colors... no.

Cleanest independent approach: omega_vec(D) >= k iff there is NO ordering with backedge
clique < k. Equivalently, omega_vec(D) < k iff exists order with all backedge cliques <= k-1.
We test the lower bound by an EXACT exhaustive/heuristic search for an order achieving
backedge clique <= 4 on the full graph (n=7): if none exists, omega_vec >= 5 is confirmed.

Exhaustive over 49! is impossible. Instead use the SAT formulation independently:
variables = position assignment is hard. Use a different exact tool: ILP-free local search
to try to BEAT 5, plus the theoretical lower bound argument check.

Actually the rigorous independent lower bound here: omega_vec is invariant and we can
compute it EXACTLY for small n via the recursive 'minimum over orders' but that's #P-hard.
We instead cross-check the LEX LOWER BOUND lemma omega_vec(S[H]) >= omega_vec(S)+omega_vec(H)-1
by directly computing omega_vec(AC_n) exactly for n=7 via exhaustive order search (n=7 only
7 vertices -> 7! = 5040 orders, feasible), and omega_vec(AC_n - 0) (6 vertices, 720 orders).
Then the lex lemma gives a TRUE lower bound for the composition.
"""
import itertools, sys

def build_AC(n, delete=None):
    m = (n - 1) // 2
    g = {x % n for x in (set(range(1, m)) | {m + 1})}
    V = [x for x in range(n) if x != delete]
    def arc(u, v):
        return (v - u) % n in g
    return V, arc, m, g

def omega_vec_exact_small(V, arc):
    """Exact omega_vec by exhaustive min over all orders of backedge clique number.
    Only for small |V| (<= 8)."""
    import math
    Vl = list(V)
    N = len(Vl)
    best_over_orders = N + 1
    # precompute arc matrix
    idx = {v: i for i, v in enumerate(Vl)}
    A = [[False]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i != j:
                A[i][j] = arc(Vl[i], Vl[j])
    def max_clique_backedge(perm):
        # perm = order ascending; backedge edge between pos p<q iff arc(perm[q],perm[p])
        M = len(perm)
        adj = [0]*M
        for p in range(M):
            for q in range(p+1, M):
                if A[perm[q]][perm[p]]:
                    adj[p] |= (1 << q)
                    adj[q] |= (1 << p)
        best = [0]
        def bk(R, P):
            if P == 0:
                if R > best[0]: best[0] = R
                return
            if R + bin(P).count("1") <= best[0]:
                return
            PP = P
            while PP:
                v = (PP & -PP).bit_length() - 1
                bk(R+1, P & adj[v])
                P &= ~(1 << v)
                PP &= ~(1 << v)
        bk(0, (1 << M) - 1)
        return best[0]
    for perm in itertools.permutations(range(N)):
        w = max_clique_backedge(perm)
        if w < best_over_orders:
            best_over_orders = w
            if best_over_orders <= 1:
                break
    return best_over_orders

for n in [7, 9]:
    V, arc, m, g = build_AC(n)
    if n <= 9:
        w = omega_vec_exact_small(V, arc)
        Vd, arcd, _, _ = build_AC(n, delete=0)
        wd = omega_vec_exact_small(Vd, arc)
        print(f"AC_{n}: omega_vec={w}, AC_{n}-0: omega_vec={wd}")
        sys.stdout.flush()
