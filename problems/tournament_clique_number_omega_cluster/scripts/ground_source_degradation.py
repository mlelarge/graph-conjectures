"""GROUND the literature-reduction (source-degradation) proposal.

For AC_n[C3] - (0,0) at odd n in {7,9,11,13,15}:
  (a) omega_vec via SAT no-K-clique oracle: expect ge3=True, ge4=False  => omega_vec=3
  (b) dic (dichromatic number) via exact <=k acyclic-partition decision: expect dic=4
  (c) non-uniform substitution identity: AC_n[C3]-(0,0) == AC_n[H_*] with
      H_0 = TT_2 (single arc, omega_vec=1), H_t = C3 (omega_vec=2) for t!=0
      -- same order, same omega_vec (and we check graph isomorphism via canonical signature).

CONFIRM iff omega_vec=3 AND dic=4 uniformly across the tested n.
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
from search_4critical_circulant import (
    circ_arcs, omega_vec_ge_K_via_sat, best_order_upper, validate_sat_oracle,
)
from ground_lex_compose_c3 import ac_gen, c3, lex_compose


def nonuniform_subst(nT, arcsT, Hmap):
    """AC_n[H_*]: at outer vertex a, substitute the digraph Hmap[a]=(nH,arcsH).
    Flat indexing offsets prefix-sum of block sizes. Arc (a,b)->(a',b') iff
    beats_T[a][a'] OR (a==a' and beats_{Hmap[a]}[b][b'])."""
    bT = core.beats_matrix(nT, arcsT)
    sizes = [Hmap[a][0] for a in range(nT)]
    offset = [0] * nT
    for a in range(1, nT):
        offset[a] = offset[a - 1] + sizes[a - 1]
    N = sum(sizes)
    bH = {a: core.beats_matrix(Hmap[a][0], Hmap[a][1]) for a in range(nT)}
    arcs = []
    def idx(a, b):
        return offset[a] + b
    for a in range(nT):
        for b in range(sizes[a]):
            for ap in range(nT):
                for bp in range(sizes[ap]):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[a][b][bp]):
                        arcs.append((idx(a, b), idx(ap, bp)))
    return N, arcs


def dic_le_k(n, arcs, k):
    """True iff the digraph can be partitioned into <=k classes each inducing an
    ACYCLIC subdigraph (dichromatic number <= k). Backtracking over vertices;
    a class is acyclic-extendable iff adding v keeps that color class acyclic.
    We test acyclicity of an induced subdigraph by Kahn topological sort.
    Symmetry-broken: vertex 0 always color 0; new colors introduced in order."""
    beats = core.beats_matrix(n, arcs)
    # adjacency lists restricted later
    color = [-1] * n

    def class_acyclic(verts):
        """Kahn topological feasibility of induced subdigraph on `verts`."""
        vs = list(verts)
        idxset = set(vs)
        indeg = {v: 0 for v in vs}
        adj = {v: [] for v in vs}
        for u in vs:
            for w in vs:
                if u != w and beats[u][w]:
                    adj[u].append(w)
                    indeg[w] += 1
        # Kahn
        from collections import deque
        q = deque([v for v in vs if indeg[v] == 0])
        seen = 0
        while q:
            x = q.popleft()
            seen += 1
            for w in adj[x]:
                indeg[w] -= 1
                if indeg[w] == 0:
                    q.append(w)
        return seen == len(vs)

    # incremental: maintain per-color vertex lists; check acyclicity on add.
    classes = [[] for _ in range(k)]

    def recurse(v, used_colors):
        if v == n:
            return True
        # symmetry breaking: only allow up to used_colors+1 colors (new color last)
        limit = min(k, used_colors + 1)
        for c in range(limit):
            classes[c].append(v)
            if class_acyclic(classes[c]):
                nc = used_colors + (1 if c == used_colors else 0)
                if recurse(v + 1, nc):
                    return True
            classes[c].pop()
        return False

    return recurse(0, 0)


def dic_exact(n, arcs, kmax=6):
    for k in range(1, kmax + 1):
        if dic_le_k(n, arcs, k):
            return k
    return None


def canon_sig(n, arcs):
    """Cheap iso signature: sorted out-degree sequence + sorted in-degree, plus
    sorted multiset of (outdeg(u),outdeg(v)) over arcs. Not a full canonical form
    but a strong invariant; we mainly rely on order + omega_vec equality anyway."""
    beats = core.beats_matrix(n, arcs)
    outdeg = [sum(beats[u]) for u in range(n)]
    indeg = [sum(beats[w][u] for w in range(n)) for u in range(n)]
    arc_sig = sorted((outdeg[u], outdeg[v]) for (u, v) in arcs)
    return (sorted(outdeg), sorted(indeg), arc_sig)


def main():
    t0 = time.time()
    out = {}
    allok, _ = validate_sat_oracle()
    out["sat_oracle_validated"] = allok
    if not allok:
        print("SAT ORACLE FAILED", flush=True)
        print(json.dumps(out)); return

    # sanity: dic backtracker on known small objects
    print("\n=== dic sanity ===", flush=True)
    nC, aC = c3()
    dic_c3 = dic_exact(nC, aC)
    # C3 is a single directed cycle: not acyclic with 1 color, dic=2
    print(f"  dic(C3) = {dic_c3} (expect 2)", flush=True)
    nT2, aT2 = 2, [(0, 1)]
    dic_tt2 = dic_exact(nT2, aT2)
    print(f"  dic(TT_2) = {dic_tt2} (expect 1)", flush=True)
    # TT_3 transitive => acyclic => dic 1
    dic_tt3 = dic_exact(3, [(0, 1), (0, 2), (1, 2)])
    print(f"  dic(TT_3) = {dic_tt3} (expect 1)", flush=True)
    out["dic_sanity"] = {"C3": dic_c3, "TT2": dic_tt2, "TT3": dic_tt3}

    nC, aC = c3()
    rows = []
    for n in [7, 9, 11, 13, 15]:
        if time.time() - t0 > 820:
            rows.append({"n": n, "status": "skipped_time"})
            print(f"  n={n}: skipped time", flush=True)
            continue
        g = ac_gen(n)
        nAC, aAC = n, circ_arcs(n, g)
        assert core.is_tournament(nAC, aAC)
        N, A = lex_compose(nAC, aAC, nC, aC)
        assert core.is_tournament(N, A)
        # delete flat index 0 = (0,0): the source rep of vertex 0's block
        keep = [w for w in range(N) if w != 0]
        nd, ad = core.subtournament(N, A, keep)
        assert core.is_tournament(nd, ad)

        # (a) omega_vec of the deletion
        ge3, _, _ = omega_vec_ge_K_via_sat(nd, ad, 3)
        ge4, _, _ = omega_vec_ge_K_via_sat(nd, ad, 4)
        upper = best_order_upper(nd, ad, tries=200)
        ov = None
        if ge3 and not ge4:
            ov = 3 if upper <= 3 else upper
        elif not ge3:
            ov = upper
        else:  # ge4
            ov = max(4, 0)
        ov_eq3 = (ge3 and not ge4 and upper <= 3)

        # (b) dic of the deletion
        td = time.time()
        dic = dic_exact(nd, ad, kmax=6)
        dt_dic = time.time() - td
        dic_eq4 = (dic == 4)

        # (c) non-uniform substitution identity: H_0=TT_2, H_t=C3 else
        Hmap = {0: (2, [(0, 1)])}
        for a in range(1, n):
            Hmap[a] = (3, [(0, 1), (1, 2), (2, 0)])
        Ns, As = nonuniform_subst(nAC, aAC, Hmap)
        same_order = (Ns == nd)
        # omega_vec of the substitution object
        s_ge3, _, _ = omega_vec_ge_K_via_sat(Ns, As, 3)
        s_ge4, _, _ = omega_vec_ge_K_via_sat(Ns, As, 4)
        s_up = best_order_upper(Ns, As, tries=200)
        s_ov_eq3 = (s_ge3 and not s_ge4 and s_up <= 3)
        sig_match = (canon_sig(nd, ad) == canon_sig(Ns, As))

        rec = {
            "n": n, "deletion_order": nd,
            "del_ge3": ge3, "del_ge4": ge4, "del_upper": upper,
            "del_omega_vec_eq3": ov_eq3, "del_omega_vec_value": ov,
            "dic": dic, "dic_eq4": dic_eq4, "dic_time_s": round(dt_dic, 2),
            "subst_order": Ns, "subst_same_order": same_order,
            "subst_omega_vec_eq3": s_ov_eq3, "subst_iso_signature_match": sig_match,
        }
        rows.append(rec)
        print(f"  n={n} delN={nd}: omega_vec ge3={ge3} ge4={ge4} up={upper} "
              f"=>=3?{ov_eq3} | dic={dic}(=4?{dic_eq4},{dt_dic:.1f}s) | "
              f"subst sameord={same_order} ov=3?{s_ov_eq3} sig={sig_match}", flush=True)

    out["rows"] = rows
    out["elapsed_s"] = round(time.time() - t0, 1)

    # verdict logic
    tested = [r for r in rows if "del_omega_vec_eq3" in r]
    all_ov3 = all(r["del_omega_vec_eq3"] for r in tested) and len(tested) > 0
    all_dic4 = all(r["dic_eq4"] for r in tested) and len(tested) > 0
    any_ov_ge4 = any(r.get("del_ge4") for r in tested)
    any_dic3 = any(r.get("dic") == 3 for r in tested)
    out["all_omega_vec_eq3"] = all_ov3
    out["all_dic_eq4"] = all_dic4
    out["KILL_some_ov_ge4"] = any_ov_ge4
    out["KILL_some_dic_eq3"] = any_dic3
    out["CONFIRM"] = bool(all_ov3 and all_dic4 and not any_ov_ge4 and not any_dic3)

    dp = os.path.join(os.path.dirname(__file__), "..", "data",
                      "ground_source_degradation.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== SUMMARY ===", flush=True)
    print(json.dumps({k: out[k] for k in
                      ("all_omega_vec_eq3", "all_dic_eq4", "KILL_some_ov_ge4",
                       "KILL_some_dic_eq3", "CONFIRM", "elapsed_s")}, indent=2), flush=True)
    print(json.dumps(rows, indent=2), flush=True)


if __name__ == "__main__":
    main()
