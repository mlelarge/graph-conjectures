"""Verify AC7[AC7] is a 5-omega_vec witness: omega_vec == 5 exactly, and the
inner_then_outer deletion order certifies omega_vec(-0) == 4 (5-critical, since
vertex-transitive).  Foreground, signal.alarm timeout."""
import sys, os, json, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core, networkx as nx
from ground_lex_compose_c3 import ac_gen, lex_compose
from search_4critical_circulant import circ_arcs, omega_vec_ge_K_via_sat


class Timeout(Exception):
    pass
def _alarm(s, f):
    raise Timeout()


def c_of(t, m=3):
    return 3 if t == 0 else (2 if 1 <= t <= m else 1)


def clique_of_order(beats, order):
    g = nx.Graph(); g.add_nodes_from(order); L = len(order)
    for i in range(L):
        a = order[i]
        for j in range(i + 1, L):
            b = order[j]
            if beats[b][a]:
                g.add_edge(a, b)
    return max((len(c) for c in nx.find_cliques(g)), default=0)


def main():
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(int(os.environ.get("HARD_TIMEOUT", "560")))
    out = {}
    try:
        g = ac_gen(7); nAC, aAC = 7, circ_arcs(7, g)
        N, A = lex_compose(nAC, aAC, nAC, aAC)
        assert core.is_tournament(N, A)
        beats = core.beats_matrix(N, A)
        out["order"] = N

        # UPPER bound omega_vec <= 5 via merged-key order on full tournament
        full_order = sorted(range(N), key=lambda f: (c_of(f // 7) + c_of(f % 7), f // 7, f % 7))
        full_clique = clique_of_order(beats, full_order)
        out["merged_order_full_clique"] = full_clique
        print("merged-order full clique (upper bound) =", full_clique, flush=True)

        # LOWER bound omega_vec >= 5 via no-K5 SAT UNSAT
        t = time.time(); ge5, dt5, _ = omega_vec_ge_K_via_sat(N, A, 5)
        out["full_ge5"] = bool(ge5); out["dt5"] = round(dt5, 3)
        print("full >=5 (no-K5 UNSAT)?", ge5, f"({dt5:.2f}s)", flush=True)
        t = time.time(); ge6, dt6, _ = omega_vec_ge_K_via_sat(N, A, 6)
        out["full_ge6"] = bool(ge6); out["dt6"] = round(dt6, 3)
        print("full >=6 (no-K6 UNSAT)?", ge6, f"({dt6:.2f}s)", flush=True)
        out["omega_vec_eq5"] = bool(ge5 and (not ge6) and full_clique == 5)
        print("=> omega_vec(AC7[AC7]) == 5 exactly?", out["omega_vec_eq5"], flush=True)

        # DELETION v=0: inner_then_outer order key=(c(b),c(a)); clique
        deleted = 0
        order = sorted([f for f in range(N) if f != deleted],
                       key=lambda f: (c_of(f % 7), c_of(f // 7), f // 7, f % 7))
        del_clique = clique_of_order(beats, order)
        out["deletion_inner_then_outer_clique"] = del_clique
        print("deletion inner_then_outer clique (upper) =", del_clique, flush=True)

        # SAT confirm deletion omega_vec == 4 exactly
        survivors = [i for i in range(N) if i != deleted]
        relabel = {v: i for i, v in enumerate(survivors)}
        sub = [(relabel[u], relabel[v]) for (u, v) in A if u in relabel and v in relabel]
        Nsub = len(survivors)
        dge5, dts5, _ = omega_vec_ge_K_via_sat(Nsub, sub, 5)   # UNSAT => >=5
        dge4, dts4, _ = omega_vec_ge_K_via_sat(Nsub, sub, 4)   # UNSAT => >=4
        out["deletion_ge5"] = bool(dge5); out["deletion_ge4"] = bool(dge4)
        out["deletion_omega_vec_eq4"] = bool(dge4 and (not dge5) and del_clique == 4)
        print(f"deletion(-0): >=5? {dge5}  >=4? {dge4}  => omega_vec(-0)==4? "
              f"{out['deletion_omega_vec_eq4']}", flush=True)

        out["is_5_critical_witness"] = bool(
            out["omega_vec_eq5"] and out["deletion_omega_vec_eq4"])
        print("=> AC7[AC7] is a 5-omega_vec-critical witness (vertex-transitive)?",
              out["is_5_critical_witness"], flush=True)
    except Timeout:
        out["status"] = "TIMEOUT"; print("TIMEOUT", flush=True)
    finally:
        signal.alarm(0)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "verify_k5_ac7ac7.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=1)
    print("WROTE", dp, flush=True)


if __name__ == "__main__":
    main()
