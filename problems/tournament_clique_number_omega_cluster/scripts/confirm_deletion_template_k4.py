"""Confirm the winning template d_then_c: order AC_n[C3]-(0,0) ascending by
(d(h), c(t), t, h) has backedge clique EXACTLY 3, uniformly.  Controls:
 (1) the SAME template on the FULL AC_n[C3] (no deletion) -> should be >=4
     (so the deletion is genuinely doing the work, not the template alone),
 (2) deletion clique = 3 over a WIDER n range (7..45),
 (3) SAT no-K-clique cross-check omega_vec(AC_n[C3]-0) = 3 at n=7,9,11,13,15.
Foreground, hard alarm.
"""
import sys, os, json, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from ground_lex_compose_c3 import ac_gen, c3, lex_compose
from search_4critical_circulant import circ_arcs, omega_vec_ge_K_via_sat


class Timeout(Exception):
    pass


def _alarm(s, f):
    raise Timeout()


def c_of(t, m):
    if t == 0:
        return 3
    if 1 <= t <= m:
        return 2
    return 1


def d_of(h):
    return 2 if h == 0 else 1


def keyfn(t, h, m):
    # winning template: primary d(h), secondary c(t)
    return (d_of(h), c_of(t, m))


def build(n):
    m = (n - 1) // 2
    g = ac_gen(n)
    nAC, aAC = n, circ_arcs(n, g)
    nC, aC = c3()
    N, A = lex_compose(nAC, aAC, nC, aC)
    return N, A, m


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


def order_template(m, deleted):
    n = 2 * m + 1
    items = []
    for t in range(n):
        for h in range(3):
            flat = t * 3 + h
            if flat == deleted:
                continue
            items.append((keyfn(t, h, m), t, h, flat))
    items.sort(key=lambda x: (x[0], x[1], x[2]))
    return [it[3] for it in items]


def main():
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(int(os.environ.get("HARD_TIMEOUT", "850")))
    out = {}
    try:
        ns = list(range(7, 46, 2))
        del_clique = {}
        full_clique = {}
        for n in ns:
            N, A, m = build(n)
            beats = core.beats_matrix(N, A)
            # deletion order (drop flat 0)
            od = order_template(m, deleted=0)
            del_clique[n] = clique_of_order(N, beats, od)
            # FULL graph with same template (no deletion): build full order
            items = []
            for t in range(n):
                for h in range(3):
                    items.append((keyfn(t, h, m), t, h, t * 3 + h))
            items.sort(key=lambda x: (x[0], x[1], x[2]))
            ofull = [it[3] for it in items]
            full_clique[n] = clique_of_order(N, beats, ofull)
            print(f"n={n}: deletion clique={del_clique[n]}  full clique={full_clique[n]}",
                  flush=True)
        out["deletion_clique"] = del_clique
        out["full_clique_same_template"] = full_clique
        out["deletion_all_le3"] = all(v <= 3 for v in del_clique.values())
        out["deletion_all_eq3"] = all(v == 3 for v in del_clique.values())

        sat = {}
        for n in [7, 9, 11, 13, 15]:
            N, A, m = build(n)
            survivors = [i for i in range(N) if i != 0]
            relabel = {v: i for i, v in enumerate(survivors)}
            subarcs = [(relabel[u], relabel[v]) for (u, v) in A
                       if u != 0 and v != 0]
            Nsub = len(survivors)
            ge4, dt4, _ = omega_vec_ge_K_via_sat(Nsub, subarcs, 4)
            ge3, dt3, _ = omega_vec_ge_K_via_sat(Nsub, subarcs, 3)
            sat[n] = {"ge4": bool(ge4), "ge3": bool(ge3),
                      "omega_vec_eq3": (bool(ge3) and not bool(ge4))}
            print(f"SAT n={n}: omega_vec(AC_n[C3]-0)=3? {sat[n]['omega_vec_eq3']} "
                  f"(>=3 {ge3}, >=4 {ge4})", flush=True)
        out["sat_check"] = sat
        out["sat_all_eq3"] = all(v["omega_vec_eq3"] for v in sat.values())
    except Timeout:
        out["status"] = "TIMEOUT"
        print("TIMEOUT", flush=True)
    finally:
        signal.alarm(0)
    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "confirm_deletion_template_k4.json")
    with open(dp, "w") as f:
        json.dump(out, f, indent=1)
    print("WROTE", dp, flush=True)


if __name__ == "__main__":
    main()
