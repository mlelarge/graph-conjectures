"""GROUND: lexicographic composition family L_n := AC_n[C3].

AC_n = Cay(Z/n, g={1..m-1}∪{m+1}), n=2m+1 >= 7  (proven 3-critical, P13).
C3   = directed triangle (0->1->2->0), omega_vec = 2 (proven 2-critical).

Lex composition T[H]: vertices (a,b), arc (a,b)->(a',b') iff
  beats_T[a][a']  OR  (a==a' AND beats_H[b][b']).

CLAIM: L_n is 4-omega_vec-critical for odd n>=7.
Falsifiable prediction: omega_vec(L_n)=4 EXACTLY and every single-vertex
deletion has omega_vec=3 EXACTLY, at n=7,9,11,13 (orders 21,27,33,39).

Lower/upper certifier = generalized no-K-clique SAT oracle (validated K=2..5).
Also cross-validate the composition LAW omega_vec(T[H])=ov(T)+ov(H)-1 on
exact-feasible small orders via core.omega_vec.
"""
import sys, os, json, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
from search_4critical_circulant import (
    circ_arcs, omega_vec_ge_K_via_sat, best_order_upper, validate_sat_oracle,
)


def ac_gen(n):
    """g = {1..m-1} ∪ {m+1}, n=2m+1."""
    assert n % 2 == 1
    m = (n - 1) // 2
    g = set(range(1, m)) | {m + 1}
    return g


def c3():
    """Directed triangle 0->1->2->0 as (n, arcs)."""
    return 3, [(0, 1), (1, 2), (2, 0)]


def lex_compose(nT, arcsT, nH, arcsH):
    """T[H]: vertex (a,b) -> flat index a*nH + b."""
    bT = core.beats_matrix(nT, arcsT)
    bH = core.beats_matrix(nH, arcsH)
    n = nT * nH
    arcs = []
    def idx(a, b):
        return a * nH + b
    for a in range(nT):
        for b in range(nH):
            for ap in range(nT):
                for bp in range(nH):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[b][bp]):
                        arcs.append((idx(a, b), idx(ap, bp)))
    # arcs currently lists each ordered beat; keep only the directed arcs (one per pair)
    return n, arcs


def omega_vec_exact_or_none(n, arcs, feasible_n=12):
    if n <= feasible_n:
        return core.omega_vec(n, arcs)
    return None


class Timeout(Exception):
    pass


def main():
    out = {}
    t_start = time.time()

    # (0) re-validate the SAT oracle in-process (foreground)
    allok, _ = validate_sat_oracle()
    out["sat_oracle_validated"] = allok
    if not allok:
        print("SAT ORACLE FAILED VALIDATION", flush=True)
        print(json.dumps(out))
        return

    nC, aC = c3()

    # (1) LAW cross-validation on exact-feasible small orders
    print("\n=== LAW omega_vec(T[H]) = ov(T)+ov(H)-1 (exact, small orders) ===", flush=True)
    law = []
    # C3[C3] order 9
    n99, a99 = lex_compose(nC, aC, nC, aC)
    assert core.is_tournament(n99, a99), "C3[C3] not a tournament"
    ov_c3c3 = core.omega_vec(n99, a99)
    law.append({"name": "C3[C3]", "order": n99, "ov": ov_c3c3,
                "law_pred": 2 + 2 - 1, "agree": ov_c3c3 == 3})
    print(f"  C3[C3] order={n99} ov={ov_c3c3} law=3 agree={ov_c3c3==3}", flush=True)
    # C3[TT2] order 6 (TT2 = single arc 0->1, omega_vec=1)
    nT2, aT2 = 2, [(0, 1)]
    n6, a6 = lex_compose(nC, aC, nT2, aT2)
    assert core.is_tournament(n6, a6)
    ov_c3tt2 = core.omega_vec(n6, a6)
    law.append({"name": "C3[TT2]", "order": n6, "ov": ov_c3tt2,
                "law_pred": 2 + 1 - 1, "agree": ov_c3tt2 == 2})
    print(f"  C3[TT2] order={n6} ov={ov_c3tt2} law=2 agree={ov_c3tt2==2}", flush=True)
    # TT2[C3] order 6
    n6b, a6b = lex_compose(nT2, aT2, nC, aC)
    assert core.is_tournament(n6b, a6b)
    ov_tt2c3 = core.omega_vec(n6b, a6b)
    law.append({"name": "TT2[C3]", "order": n6b, "ov": ov_tt2c3,
                "law_pred": 1 + 2 - 1, "agree": ov_tt2c3 == 2})
    print(f"  TT2[C3] order={n6b} ov={ov_tt2c3} law=2 agree={ov_tt2c3==2}", flush=True)
    # AC7[TT2] order 14 -> too big for exact; AC7 order 7 ov=3, use exact AC7 alone
    nAC7, aAC7 = 7, circ_arcs(7, ac_gen(7))
    assert core.is_tournament(nAC7, aAC7)
    ov_ac7 = core.omega_vec(nAC7, aAC7)
    law.append({"name": "AC7", "order": 7, "ov": ov_ac7, "law_pred": 3,
                "agree": ov_ac7 == 3})
    print(f"  AC7 order=7 ov={ov_ac7} (expect 3) agree={ov_ac7==3}", flush=True)
    out["law"] = law

    # (2) MAIN: L_n = AC_n[C3] for n=7,9,11,13
    print("\n=== L_n = AC_n[C3] (SAT oracle) ===", flush=True)
    results = []
    for n in [7, 9, 11, 13]:
        if time.time() - t_start > 820:
            results.append({"n": n, "status": "skipped_time"})
            print(f"  n={n}: skipped (time budget)", flush=True)
            continue
        g = ac_gen(n)
        nAC, aAC = n, circ_arcs(n, g)
        assert core.is_tournament(nAC, aAC), f"AC_{n} not a tournament"
        N, A = lex_compose(nAC, aAC, nC, aC)
        assert core.is_tournament(N, A), f"L_{n} not a tournament"
        rec = {"n": n, "order": N, "is_tournament": True}

        # whole-tournament omega_vec
        ge4, dt4, ncl4 = omega_vec_ge_K_via_sat(N, A, 4)   # UNSAT => >=4
        ge5, dt5, ncl5 = omega_vec_ge_K_via_sat(N, A, 5)   # UNSAT => >=5
        upper = best_order_upper(N, A, tries=100)
        rec.update({"ge4": ge4, "ge5": ge5, "best_upper": upper})
        # omega_vec == 4 iff ge4 and not ge5 and upper==4
        ov_is4 = ge4 and (not ge5) and (upper == 4)
        rec["omega_vec_eq4"] = ov_is4
        print(f"  L_{n} order={N}: ge4(UNSAT no-K4)={ge4} ge5={ge5} "
              f"best_upper={upper} => omega_vec==4? {ov_is4} "
              f"(t4={dt4:.3f}s t5={dt5:.3f}s)", flush=True)

        # criticality: deletions. NOT vertex-transitive in general (block structure),
        # so we must NOT rely on a single deletion. Sweep ALL N positions but with
        # a per-deletion SAT (fast). For thoroughness check every vertex.
        del_results = []
        all_del_3 = True
        for v in range(N):
            if time.time() - t_start > 980:
                rec["deletion_status"] = f"partial_time_at_v={v}"
                all_del_3 = None
                break
            nn, sub = core.subtournament(N, A, [w for w in range(N) if w != v])
            dge3, _, _ = omega_vec_ge_K_via_sat(nn, sub, 3)   # >=3
            dge4, _, _ = omega_vec_ge_K_via_sat(nn, sub, 4)   # >=4
            dup = best_order_upper(nn, sub, tries=60)
            is3 = dge3 and (not dge4) and dup <= 3
            del_results.append({"v": v, "ge3": dge3, "ge4": dge4, "upper": dup, "is3": is3})
            if not is3:
                all_del_3 = False
        # summarize
        n_is3 = sum(1 for d in del_results if d["is3"])
        rec["deletions_checked"] = len(del_results)
        rec["deletions_eq3"] = n_is3
        rec["all_deletions_eq3"] = all_del_3
        # show any non-3 deletion
        bad = [d for d in del_results if not d["is3"]]
        rec["bad_deletions"] = bad[:10]
        print(f"  L_{n}: deletions checked={len(del_results)} eq3={n_is3} "
              f"all_eq3={all_del_3} bad(first few)={bad[:3]}", flush=True)

        rec["is_4_critical"] = bool(ov_is4 and all_del_3 is True)
        results.append(rec)
        print(f"  => L_{n} 4-omega_vec-critical? {rec['is_4_critical']}", flush=True)

    out["L_n"] = results
    out["elapsed_s"] = round(time.time() - t_start, 1)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "ground_lex_compose_c3.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== SUMMARY ===", flush=True)
    print(json.dumps({"law": law,
                      "L_n": [{k: r.get(k) for k in
                               ("n", "order", "omega_vec_eq4", "ge4", "ge5",
                                "best_upper", "deletions_checked", "deletions_eq3",
                                "all_deletions_eq3", "is_4_critical", "status")}
                              for r in results]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
