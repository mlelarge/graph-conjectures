"""Ground QR_19[AC_7] as candidate first k=6 omega_vec object, using the EXACT
canonical merged-sum construction that proved the single-level upper bounds
(P18 AC_n[C3], P19/P20 AC_n[AC_m]).

Canonical merged key (proof_omega_AC_n_C3.md, search_deletion_template_k5.py):
  vertex (o,a) [o=outer coord, a=inner coord], flat = o*ni + a
  key = c_outer(o) + c_inner(a)
  sort ascending by (key, o, a)   [coords as tie-break, exactly items.sort((x0,x1))]

c_inner = AC_7 potential: c(0)=3, c(1..m)=2, c(m+1..2m)=1  (m=3).
c_outer = QR_19 potential = largest QR_19 backedge-clique whose min element (in
          QR_19's identity order) is o.

Sanity gate: reproduce AC_7[C3]=4 and AC_7[AC_7]=5 with the SAME pipeline before
trusting the QR_19[AC_7] number.
"""
import sys
sys.path.insert(0, 'scripts')
import core, lexlib
import networkx as nx


def circ(n, g):
    gs = set(x % n for x in g)
    arcs = [(i, j) for i in range(n) for j in range(n)
            if i != j and (j - i) % n in gs]
    return n, arcs


def ac7():
    return lexlib.AC(7, [1, 2, 4])


def c3():
    return (3, [(0, 1), (1, 2), (2, 0)])


def ac_potential(t, m=3):
    """AC_n identity-order potential c(t)=3 if t=0; 2 if 1<=t<=m; 1 if m+1<=t<=2m."""
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1


def c3_potential(h):
    return 2 if h == 0 else 1


def beats(n, arcs):
    b = [[False] * n for _ in range(n)]
    for (u, v) in arcs:
        b[u][v] = True
    return b


def identity_potential(n, arcs):
    """c(v) = largest backedge-clique in the IDENTITY order whose prec-min
    element is v.  Identity order: 0 prec 1 prec ... prec n-1; edge a-b (a<b)
    iff arc b->a (b beats a)."""
    b = beats(n, arcs)
    adj = {v: set() for v in range(n)}
    for a in range(n):
        for bb in range(a + 1, n):
            if b[bb][a]:
                adj[a].add(bb)
                adj[bb].add(a)
    pot = {}
    for v in range(n):
        cand = [u for u in adj[v] if u > v]
        sub = nx.Graph()
        sub.add_nodes_from(cand)
        for i, x in enumerate(cand):
            for y in cand[i + 1:]:
                if y in adj[x]:
                    sub.add_edge(x, y)
        mc = max((len(c) for c in nx.find_cliques(sub)), default=0) if cand else 0
        pot[v] = 1 + mc
    return pot


def merged_sum_order(no, ni, cout, cin):
    """Build the canonical merged-sum order on the lex product, flat = o*ni + a,
    key=(cout(o)+cin(a), o, a)."""
    items = []
    for o in range(no):
        for a in range(ni):
            flat = o * ni + a
            items.append(((cout(o) + cin(a), o, a), flat))
    items.sort(key=lambda x: x[0])
    return [flat for _, flat in items]


def run(outer, inner, cout, cin, label, expect=None):
    N, arcs = lexlib.lex_substitute(outer, inner)
    assert core.is_tournament(N, arcs), f"{label}: not a tournament"
    no = outer[0]
    ni = inner[0]
    order = merged_sum_order(no, ni, cout, cin)
    assert sorted(order) == list(range(N))
    U = core.omega_of_order(N, arcs, order)
    idw = core.omega_of_order(N, arcs, list(range(N)))
    tag = ""
    if expect is not None:
        tag = "  OK" if U == expect else f"  *** MISMATCH expect {expect} ***"
    print(f"[{label}] N={N} arcs={len(arcs)} tournament; "
          f"identity-clique={idw}; merged-sum U={U}{tag}", flush=True)
    return U


def main():
    print("=== SANITY GATE: canonical merged-sum on known single-level products ===",
          flush=True)
    u1 = run(ac7(), c3(), ac_potential, c3_potential, "AC_7[C3]", expect=4)
    u2 = run(ac7(), ac7(), ac_potential, ac_potential, "AC_7[AC_7]", expect=5)
    gate_ok = (u1 == 4 and u2 == 5)
    print(f"SANITY GATE {'PASSED' if gate_ok else 'FAILED'}\n", flush=True)

    print("=== TARGET QR_19[AC_7] ===", flush=True)
    qg = sorted({(x * x) % 19 for x in range(1, 19)})
    print("QR_19 g =", qg, flush=True)
    qr19 = circ(19, qg)
    print("omega_vec(QR_19) =", core.omega_vec(*qr19, method='bb'), flush=True)
    print("omega_vec(AC_7)  =", core.omega_vec(*ac7()), flush=True)
    cout = identity_potential(*qr19)
    print("QR_19 identity-order potential (per vertex 0..18):",
          [cout[v] for v in range(19)], flush=True)
    cfun = lambda o: cout[o]
    U = run(qr19, ac7(), cfun, ac_potential, "QR_19[AC_7]")

    print("\n=== RESULT ===", flush=True)
    print("PROVEN lower bound omega_vec(QR_19[AC_7]) >= 4+3-1 = 6 (lex law)",
          flush=True)
    print(f"merged-sum upper U = {U}", flush=True)
    print(f"two-sided bound [6, {U}]", flush=True)
    if not gate_ok:
        print("WARNING: sanity gate FAILED -> merged-sum pipeline untrustworthy",
              flush=True)
    if U == 6:
        print("=> omega_vec(QR_19[AC_7]) = 6 EXACTLY (FIRST k=6 witness, ell(6)>=133)",
              flush=True)
    else:
        print(f"=> KILL: merged-sum gives clique {U} >= 7 (single-level merged "
              f"upper bound FAILS for ov=4 outer)", flush=True)


if __name__ == "__main__":
    main()
