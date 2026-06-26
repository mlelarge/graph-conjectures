"""ASYMPTOTIC-ARGUMENT probe (proposal, NOT the queued executor sweep).

Claim under test: the k=4 deletion order d_then_c LIFTS RECURSIVELY by one more
C3-substitution. Define Y = (AC_n[C3])[C3] = AC_n[C3][C3], omega_vec(Y)=5 (law).
The proposed *recursive* deletion order on Y-(0,0,0):

  key(t,h2,h1) = (d(h1), d(h2), c(t), t, h2, h1)   ascending

where the OUTERMOST C3-layer coord h1 gives the primary d-band, the next C3-layer
h2 gives the secondary d-band, and (c(t),t) is the AC_n d_then_c tail.
d(0)=2,d(1)=d(2)=1 ;  c(0)=3,c=2 on[1,m],c=1 on[m+1,2m].

This is "outer-C3 d-band, then inner d_then_c", the SAME band recipe one layer up.

FALSIFIABLE PREDICTION (kills the recursive-lift hypothesis if it fails):
  backedge clique of this recursive order on Y-(0,0,0) == 4 (= k-1 for k=5),
  AND on the FULL Y (no deletion) == 5,
  for n=7 (order 63) and n=9 (order 81).
If the deletion clique is >4, the naive recursive lift FAILS and a NEW band
structure is needed at each layer (the real open content of H15).
"""
import sys, os, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from search_4critical_circulant import circ_arcs
from ground_lex_compose_c3 import lex_compose, ac_gen, c3


def _alarm(sig, frm):
    raise TimeoutError("hard timeout")


def build_Y(n):
    """Y = AC_n[C3][C3]. Returns (N, beats, m). Flat index = ((t*3)+h2)*3 + h1."""
    nAC, aAC = n, circ_arcs(n, ac_gen(n))
    nC, aC = c3()
    N1, A1 = lex_compose(nAC, aAC, nC, aC)      # X = AC_n[C3]
    N2, A2 = lex_compose(N1, A1, nC, aC)         # Y = X[C3]
    beats = core.beats_matrix(N2, A2)
    return N2, beats, (n - 1) // 2


def coords(flat):
    """flat = ((t*3)+h2)*3 + h1  ->  (t,h2,h1)."""
    h1 = flat % 3
    rest = flat // 3
    h2 = rest % 3
    t = rest // 3
    return t, h2, h1


def cval(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1


def d(h):
    return 2 if h == 0 else 1


def recursive_order(N, m, deleted):
    items = []
    for flat in range(N):
        if flat == deleted:
            continue
        t, h2, h1 = coords(flat)
        key = (d(h1), d(h2), cval(t, m), t, h2, h1)
        items.append((key, flat))
    items.sort()
    return [f for _, f in items]


def clique_of_order(N, beats, order):
    g = nx.Graph()
    g.add_nodes_from(order)
    L = len(order)
    for i in range(L):
        a = order[i]
        for j in range(i + 1, L):
            b = order[j]
            if beats[b][a]:
                g.add_edge(a, b)
    return max((len(c) for c in nx.find_cliques(g)), default=0)


def main():
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(int(os.environ.get("HARD_TIMEOUT", "850")))
    out = {}
    for n in [7, 9]:
        t0 = time.time()
        N, beats, m = build_Y(n)
        # deleted source = (0,0,0) = flat 0
        del_order = recursive_order(N, m, deleted=0)
        full_order = recursive_order(N, m, deleted=-1)  # no deletion
        cq_del = clique_of_order(N, beats, del_order)
        cq_full = clique_of_order(N, beats, full_order)
        out[n] = {
            "order": N,
            "clique_full_recursive_order": cq_full,
            "clique_deletion_recursive_order": cq_del,
            "pred_full": 5,
            "pred_del": 4,
            "full_ok": cq_full == 5,
            "del_ok": cq_del == 4,
            "secs": round(time.time() - t0, 1),
        }
        print(f"n={n} N={N}: full_order_clique={cq_full} (pred 5) "
              f"del(0,0,0)_clique={cq_del} (pred 4) [{out[n]['secs']}s]")
    import json
    print("JSON " + json.dumps(out))


if __name__ == "__main__":
    main()
