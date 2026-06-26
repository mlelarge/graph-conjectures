"""GROUND the coprime-CRT lex-product proposal: AC_7[AC_9], order 63.

Claims to test:
 (A) P = AC_7[AC_9] is a tournament.
 (B) P is a CIRCULANT on Z_63 (CRT relabel x with x%7=t (mod7-coordinate via *9 inverse),
     x%9=h): the arc set is invariant under x -> x+1 mod 63; |connection set| = 31 = (63-1)/2.
 (C) omega_vec(P) = 5 EXACTLY:
       upper: merged-sum key order gives backedge clique 5;
       lower: no-K5 SAT UNSAT (omega_vec>=5), no-K6 SAT SAT (omega_vec<=5).
 (D) CRITICALITY (the real falsifiable test): on the 62-vertex deletion P-(0,0):
       - no-K4 SAT UNSAT  => omega_vec(deletion) >= 4
       - some deletion-order template achieves backedge clique 4 => omega_vec(deletion) <= 4
       If BOTH: by Z_63 vertex-transitivity all 63 deletions = 4 => P is 5-critical (CONFIRM).
       If every order walls at >=5 (no-K5 deletion UNSAT, no drop): NOT critical (KILL).

Foreground, signal.alarm hard timeout.
"""
import sys, os, json, time, signal, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core, networkx as nx
from ground_lex_compose_c3 import ac_gen, lex_compose
from search_4critical_circulant import circ_arcs, omega_vec_ge_K_via_sat, best_order_upper


class Timeout(Exception):
    pass
def _alarm(s, f):
    raise Timeout()


def c_of(t, m):
    """AC_n single-coordinate weight: 3 if 0, 2 if 1..m, else 1.  m=(n-1)//2."""
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


def check_circulant_Z(N, A, n_outer, n_inner):
    """P on vertices flat = t*n_inner + h (t in Z_{n_outer}, h in Z_{n_inner}),
    gcd=1.  CRT bijection to Z_N: x -> (x % n_outer, x % n_inner).  Map each flat
    (t,h) to the UNIQUE x in [0,N) with x%n_outer==t and x%n_inner==h.  Then test
    whether the arc set is invariant under x -> x+1 mod N (i.e. P is a Z_N circulant),
    and report the connection set S = {(y-x) mod N : x->y}."""
    N_outer, N_inner = n_outer, n_inner
    assert N == N_outer * N_inner
    # CRT: flat (t,h) -> x
    flat_to_x = {}
    for t in range(N_outer):
        for h in range(N_inner):
            for x in range(N):
                if x % N_outer == t and x % N_inner == h:
                    flat_to_x[t * N_inner + h] = x
                    break
    assert len(set(flat_to_x.values())) == N, "CRT relabel not a bijection"
    # arc set in Z_N coords
    arcset_Z = set((flat_to_x[u], flat_to_x[v]) for (u, v) in A)
    # connection set S = differences for arcs out of 0
    S = sorted(set((y - x) % N for (x, y) in arcset_Z if x == 0))
    # invariance under +1
    shifted = set(((x + 1) % N, (y + 1) % N) for (x, y) in arcset_Z)
    is_circ = (shifted == arcset_Z)
    # double check: arc x->y iff (y-x)%N in S, for ALL x
    Sset = set(S)
    consistent = all(((y - x) % N in Sset) for (x, y) in arcset_Z) and \
                 (len(arcset_Z) == N * len(S) // 1 // 1) if is_circ else False
    return is_circ, S


def main():
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(int(os.environ.get("HARD_TIMEOUT", "850")))
    out = {}
    try:
        # ---- (A) build AC_7[AC_9] ----
        n_out, n_in = 7, 9
        g_out = ac_gen(n_out); g_in = ac_gen(n_in)
        m_out, m_in = (n_out - 1) // 2, (n_in - 1) // 2
        a_out = circ_arcs(n_out, g_out); a_in = circ_arcs(n_in, g_in)
        assert core.is_tournament(n_out, a_out)
        assert core.is_tournament(n_in, a_in)
        N, A = lex_compose(n_out, a_out, n_in, a_in)
        out["order"] = N
        out["is_tournament"] = core.is_tournament(N, A)
        print(f"AC_7[AC_9] order={N} is_tournament={out['is_tournament']}", flush=True)
        assert out["is_tournament"]
        beats = core.beats_matrix(N, A)

        # ---- (B) circulant on Z_63 ----
        is_circ, S = check_circulant_Z(N, A, n_out, n_in)
        out["is_Z63_circulant"] = bool(is_circ)
        out["connection_set_size"] = len(S)
        out["connection_set"] = S
        print(f"is Z_{N} circulant (arc set +1-invariant)? {is_circ}; "
              f"|connection set|={len(S)} (expect {(N-1)//2})", flush=True)

        # ---- (C) omega_vec(P) ----
        # UPPER: merged-sum key order
        full_order = sorted(range(N),
                            key=lambda f: (c_of(f // n_in, m_out) + c_of(f % n_in, m_in),
                                           f // n_in, f % n_in))
        full_clique = clique_of_order(beats, full_order)
        out["merged_order_full_clique_upper"] = full_clique
        print(f"merged-sum order full clique (upper bound) = {full_clique}", flush=True)
        # also a few random/rotation orders for a tighter upper bound sanity
        up = best_order_upper(N, A, tries=80)
        out["best_order_upper"] = up
        print(f"best_order_upper (rand+rot) = {up}", flush=True)

        # LOWER: no-K5 SAT (UNSAT => >=5), no-K6 SAT (SAT => <=5)
        ge5, dt5, _ = omega_vec_ge_K_via_sat(N, A, 5)
        out["full_ge5"] = bool(ge5); out["dt5"] = round(dt5, 3)
        print(f"full >=5 (no-K5 UNSAT)? {ge5}  ({dt5:.2f}s)", flush=True)
        ge6, dt6, _ = omega_vec_ge_K_via_sat(N, A, 6)
        out["full_ge6"] = bool(ge6); out["dt6"] = round(dt6, 3)
        print(f"full >=6 (no-K6 UNSAT)? {ge6}  ({dt6:.2f}s)", flush=True)
        omega_vec_eq5 = bool(ge5 and (not ge6) and min(full_clique, up) == 5)
        out["omega_vec_eq5"] = omega_vec_eq5
        print(f"=> omega_vec(AC_7[AC_9]) == 5 exactly? {omega_vec_eq5}", flush=True)

        # ---- (D) CRITICALITY: deletion of vertex (0,0) = flat index 0 ----
        deleted = 0
        survivors = [i for i in range(N) if i != deleted]
        relabel = {v: i for i, v in enumerate(survivors)}
        Nsub = len(survivors)
        sub = [(relabel[u], relabel[v]) for (u, v) in A if u in relabel and v in relabel]
        assert core.is_tournament(Nsub, sub)

        # (a) lower bound on deletion: no-K4 UNSAT => >=4 ; no-K5 => >=5 (the KILL check)
        dge5, dts5, _ = omega_vec_ge_K_via_sat(Nsub, sub, 5)   # UNSAT => deletion>=5 (NO DROP => KILL)
        out["deletion_ge5"] = bool(dge5); out["dt_del5"] = round(dts5, 3)
        print(f"deletion(-0) >=5 (no-K5 UNSAT)? {dge5}  ({dts5:.2f}s)  "
              f"[True => NO DROP => KILL]", flush=True)
        dge4, dts4, _ = omega_vec_ge_K_via_sat(Nsub, sub, 4)   # UNSAT => deletion>=4
        out["deletion_ge4"] = bool(dge4); out["dt_del4"] = round(dts4, 3)
        print(f"deletion(-0) >=4 (no-K4 UNSAT)? {dge4}  ({dts4:.2f}s)", flush=True)

        # (b) UPPER bound on deletion: search deletion-order templates for clique 4.
        # Coordinates of a survivor f: t=f//n_in, h=f%n_in.  Template = sort key built
        # from (c_of(t), c_of(h)) in various orderings (P19-style band templates).
        def keyfun(f, mode):
            t, h = f // n_in, f % n_in
            ct, ch = c_of(t, m_out), c_of(h, m_in)
            if mode == "inner_then_outer":   # P19 winner template
                return (ch, ct, t, h)
            if mode == "outer_then_inner":
                return (ct, ch, t, h)
            if mode == "sum":
                return (ct + ch, t, h)
            if mode == "sum_inner_tiebreak":
                return (ct + ch, ch, ct, t, h)
            if mode == "inner_then_outer_rev":
                return (-ch, -ct, t, h)
            if mode == "outer_then_inner_rev":
                return (-ct, -ch, t, h)
            if mode == "inner_only":
                return (ch, t, h)
            if mode == "outer_only":
                return (ct, t, h)
            if mode == "innerval_then_outer":
                return (h, ct, t)
            if mode == "outerval_then_inner":
                return (t, ch, h)
            if mode == "inner_then_outer_flath":
                return (ch, ct, h, t)
            if mode == "outer_then_inner_flatt":
                return (ct, ch, t, h)
            return (f,)
        templates = ["inner_then_outer", "outer_then_inner", "sum", "sum_inner_tiebreak",
                     "inner_then_outer_rev", "outer_then_inner_rev", "inner_only",
                     "outer_only", "innerval_then_outer", "outerval_then_inner",
                     "inner_then_outer_flath", "outer_then_inner_flatt"]
        del_beats = core.beats_matrix(Nsub, sub)
        # map survivor index -> original flat for key computation
        inv = {i: v for v, i in relabel.items()}
        tmpl_results = {}
        best_tmpl_clique = None; best_tmpl = None
        for mode in templates:
            order = sorted(range(Nsub), key=lambda i: keyfun(inv[i], mode))
            cl = clique_of_order(del_beats, order)
            tmpl_results[mode] = cl
            if best_tmpl_clique is None or cl < best_tmpl_clique:
                best_tmpl_clique = cl; best_tmpl = mode
            print(f"  deletion template {mode:28s} backedge clique = {cl}", flush=True)
        # also random/rotation upper bound on the deletion
        del_up_rand = best_order_upper(Nsub, sub, tries=200)
        out["deletion_template_cliques"] = tmpl_results
        out["deletion_best_template"] = best_tmpl
        out["deletion_best_template_clique"] = best_tmpl_clique
        out["deletion_best_order_upper_rand"] = del_up_rand
        del_upper = min(best_tmpl_clique, del_up_rand)
        out["deletion_upper"] = del_upper
        print(f"deletion best template = {best_tmpl} clique={best_tmpl_clique}; "
              f"rand/rot upper={del_up_rand}; => deletion upper = {del_upper}", flush=True)

        # VERDICT on criticality
        deletion_eq4 = bool(dge4 and (not dge5) and del_upper == 4)
        out["deletion_omega_vec_eq4"] = deletion_eq4
        print(f"=> omega_vec(deletion -0) == 4 exactly? {deletion_eq4}", flush=True)

        out["is_5_critical_witness"] = bool(omega_vec_eq5 and deletion_eq4)
        print(f"=> AC_7[AC_9] is 5-omega_vec-critical (vertex-transitive)? "
              f"{out['is_5_critical_witness']}", flush=True)

        # Explicit CONFIRM / KILL branch flags from the proposal
        out["CONFIRM"] = bool(deletion_eq4 and omega_vec_eq5)
        out["KILL_no_drop"] = bool(dge5)   # deletion still has a K5 => omega_vec(del)>=5
    except Timeout:
        out["status"] = "TIMEOUT"; print("TIMEOUT", flush=True)
    finally:
        signal.alarm(0)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "ground_coprime_crt_k5.json")
    os.makedirs(os.path.dirname(os.path.abspath(dp)), exist_ok=True)
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("WROTE", os.path.abspath(dp), flush=True)
    print("FINAL", json.dumps({k: out.get(k) for k in
          ("order", "is_tournament", "is_Z63_circulant", "connection_set_size",
           "merged_order_full_clique_upper", "best_order_upper", "full_ge5", "full_ge6",
           "omega_vec_eq5", "deletion_ge5", "deletion_ge4", "deletion_best_template_clique",
           "deletion_best_order_upper_rand", "deletion_upper", "deletion_omega_vec_eq4",
           "is_5_critical_witness", "CONFIRM", "KILL_no_drop", "status")}), flush=True)


if __name__ == "__main__":
    main()
