"""GROUND the proposal: D_n = Delta(AC_n, AC_n, AC_n) is 4-omega_vec-critical
for every odd n>=7.

AC_n = Cay(Z/n, g) with g = {1..m-1} u {m+1}, m=(n-1)//2  (the P13 3-critical base).
D_n  = delta(AC_n, AC_n, AC_n)  on order 3n.

Falsifiable prediction (from proposal):
  omega_vec(D_n) == 4  AND  every deletion D_n - v has omega_vec == 3,
  for EVERY odd n>=7.

KILL conditions:
  * some block-orbit-representative deletion D_n - v has omega_vec == 4
    (no-K4 SAT UNSAT on the deletion), OR
  * omega_vec(D_n) != 4 (no-K5 SAT UNSAT giving >=5, or no-K4 SAT SAT giving <=3).

We use the validated generalized no-K-clique SAT oracle (build_cnf_no_kclique).
omega_vec >= K  iff  no-K-clique CNF UNSAT.
We compute omega_vec(D_n) exactly as: largest K with CNF(K) UNSAT  ==  smallest K
with CNF(K+1) SAT.  Concretely:
  ge3 = (no-K3 UNSAT), ge4 = (no-K4 UNSAT), ge5 = (no-K5 UNSAT).
  omega_vec == 4  iff  ge4 and not ge5.

Vertex-transitivity of D_n: block-cyclic shift v -> v+n (mod 3n) maps block b to
block b+1, and within-block rotation x->x+1 maps the AC_n copy onto itself.
=> the automorphism group is transitive on the 3n vertices, so ALL deletions are
isomorphic.  We MACHINE-CHECK transitivity (the two generators ARE automorphisms),
then it suffices to test ONE deletion.  We test deletion of vertex 0 (and, as an
extra guard, vertex n and vertex 2n, one per block) explicitly.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
import constructions as C
from search_4critical_circulant import (build_cnf_no_kclique,
                                         omega_vec_ge_K_via_sat,
                                         circ_arcs, identity_order_clique,
                                         best_order_upper)


def ac_gen(n):
    m = (n - 1) // 2
    g = set(range(1, m)) | {m + 1}
    return g


def ac_n(n):
    g = ac_gen(n)
    return n, circ_arcs(n, g)


def is_automorphism(n, arcs, perm):
    """perm: list mapping vertex i -> perm[i]. True iff arc-preserving."""
    beats = core.beats_matrix(n, arcs)
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if beats[u][v] != beats[perm[u]][perm[v]]:
                return False
    return True


def check_transitivity(n, arcs):
    """D_n on 3n vertices. block-shift: v -> (v + n) % (3n) maps block b->b+1.
    within-block rotation on block 0: x -> (x+1)%n on [0,n), identity elsewhere?
    A genuine automorphism must act consistently. The clean transitive generators:
      sigma: v -> (v + n) % (3n)             [block cyclic shift]
      tau  : within each block, x -> base + ((x-base+1)%n)  [simultaneous rotation]
    We check both are automorphisms, then verify the orbit of 0 is all 3n vertices.
    """
    N = 3 * n
    sigma = [(v + n) % N for v in range(N)]
    # simultaneous within-block rotation
    tau = []
    for v in range(N):
        b = v // n
        x = v % n
        tau.append(b * n + (x + 1) % n)
    sigma_ok = is_automorphism(N, arcs, sigma)
    tau_ok = is_automorphism(N, arcs, tau)
    # orbit of vertex 0 under <sigma, tau>
    orbit = {0}
    frontier = [0]
    gens = [sigma, tau]
    while frontier:
        v = frontier.pop()
        for gp in gens:
            w = gp[v]
            if w not in orbit:
                orbit.add(w)
                frontier.append(w)
    transitive = (len(orbit) == N)
    return {"sigma_is_aut": sigma_ok, "tau_is_aut": tau_ok,
            "orbit_size_of_0": len(orbit), "transitive": transitive}


def omega_vec_exact_via_sat(N, arcs, kmax=6):
    """Exact omega_vec via the no-K-clique SAT ladder.
    omega_vec = max K with CNF(no-K-clique) UNSAT.
    Returns (omega_vec, details).  ge[K] = (omega_vec >= K)."""
    ge = {}
    times = {}
    for K in range(2, kmax + 1):
        geK, dt, ncl = omega_vec_ge_K_via_sat(N, arcs, K)
        ge[K] = geK
        times[K] = round(dt, 3)
        if not geK:
            # omega_vec < K, so omega_vec = K-1
            return K - 1, {"ge": ge, "times": times}
    return kmax, {"ge": ge, "times": times}


def main():
    Ns = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [7, 9, 11, 13, 15]
    out = {"Ns": Ns, "results": []}
    overall_deadline = time.time() + 1700
    for n in Ns:
        if time.time() > overall_deadline:
            out["results"].append({"n": n, "status": "skipped_time"})
            print(f"n={n}: SKIPPED (global time)", flush=True)
            continue
        t0 = time.time()
        N = 3 * n
        g = ac_gen(n)
        acn = ac_n(n)
        # sanity: AC_n is a valid tournament generator
        negg = set((-d) % n for d in g)
        gen_ok = (not (g & negg)) and (len(g) == (n - 1) // 2)
        Dn = C.delta(acn, acn, acn)
        Nn, arcs = Dn
        assert Nn == N
        is_tour = core.is_tournament(N, arcs)
        # transitivity check
        trans = check_transitivity(n, arcs)
        # omega_vec(D_n) exact via SAT ladder
        ov, ovd = omega_vec_exact_via_sat(N, arcs, kmax=6)
        # deletions: one rep per block (0, n, 2n)
        del_recs = []
        for v in (0, n, 2 * n):
            nn, sub = core.subtournament(N, arcs, [w for w in range(N) if w != v])
            dov, dovd = omega_vec_exact_via_sat(nn, sub, kmax=6)
            del_recs.append({"deleted_vertex": v, "omega_vec": dov, "ge": dovd["ge"]})
            print(f"    n={n} delete v={v}: omega_vec(D_n - v) = {dov}", flush=True)
        dt = time.time() - t0
        # prediction: ov==4 and all deletions==3
        all_del = [r["omega_vec"] for r in del_recs]
        pred_ok = (ov == 4) and all(d == 3 for d in all_del)
        rec = {"n": n, "order": N, "gen": sorted(g), "gen_valid": gen_ok,
               "is_tournament": is_tour, "transitivity": trans,
               "omega_vec_Dn": ov, "omega_vec_detail": ovd,
               "deletions": del_recs, "all_deletion_omega_vec": all_del,
               "prediction_holds": pred_ok, "seconds": round(dt, 1)}
        out["results"].append(rec)
        print(f"n={n} order={N}: omega_vec(D_n)={ov}  deletions={all_del}  "
              f"transitive={trans['transitive']}  PRED_OK={pred_ok}  ({dt:.1f}s)",
              flush=True)
    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "ground_delta_fold_k4.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== SUMMARY ===", flush=True)
    print(json.dumps(out["results"], indent=2), flush=True)


if __name__ == "__main__":
    main()
