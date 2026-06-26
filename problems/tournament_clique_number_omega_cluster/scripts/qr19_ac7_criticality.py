"""Certify QR_19[AC_7] (order 133) as the FIRST explicit 6-omega_vec-critical
tournament, SAT-free.

Four legs (claim_form: EXISTENTIAL — explicit witnesses only, no universal law):
  L1  omega_vec(T) >= 6:  proven lex LOWER bound (Lemma 3.8 fattening) +
      P15 ov(QR_19)=4 + P13 ov(AC_7)=3  =>  4+3-1 = 6.        [free, cited]
  L2  omega_vec(T) <= 6:  ONE explicit order of T with backedge clique 6
      (re-pin of D34; the merged-sum order gives 7, so clique-guided local
      search is required).                                     [this script]
  L3  omega_vec(T-(0,0)) >= 5:  blocks {1..18} induce (QR_19-0)[AC_7];
      P15 criticality gives ov(QR_19-0)=3 exactly; lex lower 3+3-1=5. [free]
  L4  omega_vec(T-(0,0)) <= 5:  ONE explicit order of T-(0,0) with backedge
      clique 5 (template sweep, then clique-guided search).    [this script]
  L5  vertex-transitivity: outer rotation (o,a)->(o+1,a) and inner rotation
      (o,a)->(o,a+1) are automorphisms generating a transitive group (machine
      checked), so ONE deletion settles all 133.               [this script]

Run stages foreground:  .venv/bin/python scripts/qr19_ac7_criticality.py <stage>
  stage in {build, templates, full, del}
"""
import sys, os, json, time, random, signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core, lexlib
import networkx as nx
from ground_qr19_ac7_k6 import circ, ac7, identity_potential, ac_potential, \
    merged_sum_order

DATA = os.path.join(HERE, "..", "data", "qr19_ac7_criticality.json")
QR_G = [1, 4, 5, 6, 7, 9, 11, 16, 17]          # quadratic residues mod 19
NO, NI = 19, 7


class Timeout(Exception):
    pass


def _alarm(s, f):
    raise Timeout()


def build():
    QR = circ(19, QR_G)
    A7 = ac7()
    N, arcs = lexlib.lex_substitute(QR, A7)
    assert core.is_tournament(N, arcs)
    return N, arcs, QR


def flat(o, a):
    return o * NI + a


def check_transitive(N, beats):
    sigma = [flat((v // NI + 1) % NO, v % NI) for v in range(N)]
    tau = [flat(v // NI, (v % NI + 1) % NI) for v in range(N)]

    def is_auto(p):
        for u in range(N):
            for v in range(N):
                if u != v and beats[u][v] != beats[p[u]][p[v]]:
                    return False
        return True

    ok_s, ok_t = is_auto(sigma), is_auto(tau)
    orbit = {0}
    fr = [0]
    while fr:
        x = fr.pop()
        for p in (sigma, tau):
            if p[x] not in orbit:
                orbit.add(p[x])
                fr.append(p[x])
    return ok_s, ok_t, len(orbit) == N


# ---------------------------------------------------------------- evaluation
def eval_order(beats, order):
    """(clique_number w, EXACT count of maximal cliques of size w, sample list
    of max cliques).  ENUMERATION IS COMPLETE (no cap): w is exact.  An earlier
    capped version under-reported w (caught by the omega_of_order recheck)."""
    g = nx.Graph()
    g.add_nodes_from(order)
    L = len(order)
    for i in range(L):
        a = order[i]
        for j in range(i + 1, L):
            b = order[j]
            if beats[b][a]:
                g.add_edge(a, b)
    w, cnt, sample = 1, 0, []
    for c in nx.find_cliques(g):
        if len(c) > w:
            w, cnt, sample = len(c), 1, [list(c)]
        elif len(c) == w:
            cnt += 1
            if len(sample) < 50:
                sample.append(list(c))
    return w, cnt, sample


def local_search(beats, init_order, target, budget_s, seed, label,
                 restarts=1000):
    """Clique-guided hill climbing with sideways moves and restarts.
    Move: pick a vertex of a current maximum clique, reinsert at a random
    position.  Energy = (w, count_of_max_cliques), lexicographic."""
    rng = random.Random(seed)
    t0 = time.time()
    best_order, (bw, bc, bs) = list(init_order), eval_order(beats, init_order)
    print(f"[{label}] init clique={bw} count={bc}", flush=True)
    gbest_order, gbw = list(best_order), bw
    rs = 0
    evals = 0
    while time.time() - t0 < budget_s and gbw > target and rs < restarts:
        rs += 1
        # restart: perturb global best (or init) with a few random moves
        cur = list(gbest_order)
        for _ in range(rng.randrange(0, 6)):
            i = rng.randrange(len(cur))
            v = cur.pop(i)
            cur.insert(rng.randrange(len(cur) + 1), v)
        cw, cc, cs = eval_order(beats, cur)
        evals += 1
        stall = 0
        while time.time() - t0 < budget_s and cw > target and stall < 400:
            cl = cs[rng.randrange(len(cs))] if cs else [cur[0]]
            v = cl[rng.randrange(len(cl))]
            cand = list(cur)
            cand.remove(v)
            cand.insert(rng.randrange(len(cand) + 1), v)
            nw, ncnt, ns = eval_order(beats, cand)
            evals += 1
            if (nw, ncnt) <= (cw, cc):
                if (nw, ncnt) < (cw, cc):
                    stall = 0
                else:
                    stall += 1
                cur, cw, cc, cs = cand, nw, ncnt, ns
            else:
                stall += 1
            if cw < gbw:
                gbw, gbest_order = cw, list(cur)
                print(f"[{label}] new best clique={cw} count={cc} "
                      f"(t={time.time()-t0:.0f}s evals={evals})", flush=True)
        if cw < gbw:
            gbw, gbest_order = cw, list(cur)
    print(f"[{label}] DONE best={gbw} target={target} restarts={rs} "
          f"evals={evals} t={time.time()-t0:.0f}s", flush=True)
    return gbw, gbest_order


# ------------------------------------------------------------ template sweep
def deletion_templates(qpot):
    """12 keys mirroring search_deletion_template_k5 (P19's machinery), with
    c_outer = QR_19 identity potential (values 1..4), c_inner = AC_7 potential."""
    co = lambda o: qpot[o]
    ci = lambda a: ac_potential(a)
    T = []
    T.append(("base_merged", lambda o, a: (co(o) + ci(a),)))
    T.append(("inner_then_outer", lambda o, a: (ci(a), co(o))))
    T.append(("outer_then_inner", lambda o, a: (co(o), ci(a))))
    T.append(("merged_innerfirst", lambda o, a: (co(o) + ci(a), ci(a), co(o))))
    T.append(("merged_outerfirst", lambda o, a: (co(o) + ci(a), co(o), ci(a))))
    T.append(("inner_b0_last", lambda o, a: (co(o) + ci(a), 1 if a == 0 else 0, co(o))))
    T.append(("inner_b0_first", lambda o, a: (co(o) + ci(a), 0 if a == 0 else 1, co(o))))
    T.append(("band_o_then_a", lambda o, a: (co(o), a)))
    T.append(("band_a_then_o", lambda o, a: (ci(a), o)))
    T.append(("demote_o0", lambda o, a: ((1 if o == 0 else co(o)) + ci(a),)))
    T.append(("demote_a0", lambda o, a: (co(o) + (1 if a == 0 else ci(a)),)))
    T.append(("demote_both0", lambda o, a: ((1 if o == 0 else co(o)) +
                                            (1 if a == 0 else ci(a)),)))
    return T


def template_order(N, keyfn, deleted):
    items = []
    for v in range(N):
        if v == deleted:
            continue
        o, a = v // NI, v % NI
        items.append((keyfn(o, a), o, a, v))
    items.sort(key=lambda x: (x[0], x[1], x[2]))
    return [it[3] for it in items]


def load_data():
    if os.path.exists(DATA):
        with open(DATA) as f:
            return json.load(f)
    return {}


def save_data(d):
    with open(DATA, "w") as f:
        json.dump(d, f, indent=1)
    print("WROTE", DATA, flush=True)


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "build"
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(int(os.environ.get("HARD_TIMEOUT", "880")))
    N, arcs, QR = build()
    beats = core.beats_matrix(N, arcs)
    out = load_data()

    if stage == "build":
        ok_s, ok_t, trans = check_transitive(N, beats)
        out["build"] = {"N": N, "arcs": len(arcs),
                        "is_tournament": True,
                        "outer_rotation_automorphism": ok_s,
                        "inner_rotation_automorphism": ok_t,
                        "vertex_transitive": trans}
        print(out["build"], flush=True)
        save_data(out)
        return

    if stage == "templates":
        qpot = identity_potential(*QR)
        res = []
        for tname, keyfn in deletion_templates(qpot):
            order = template_order(N, keyfn, deleted=0)
            w, cnt, _ = eval_order(beats, order)
            print(f"  [{tname}] deletion clique = {w} (maxcliques={cnt})"
                  + ("  <<< CLIQUE<=5" if w <= 5 else ""), flush=True)
            rec = {"template": tname, "deletion_clique": w, "le5": w <= 5}
            if w <= 5:
                rec["order"] = order
            res.append(rec)
        out["templates"] = res
        out["template_winners"] = [r["template"] for r in res if r["le5"]]
        save_data(out)
        return

    if stage == "full":
        # L2: re-pin omega_vec(T) <= 6 with an explicit order
        qpot = identity_potential(*QR)
        init = merged_sum_order(NO, NI, lambda o: qpot[o],
                                lambda a: ac_potential(a))
        budget = float(os.environ.get("BUDGET_S", "800"))
        seed = int(os.environ.get("SEED", "1"))
        w, order = local_search(beats, init, target=6, budget_s=budget,
                                seed=seed, label="fullT")
        # independent recheck with core.omega_of_order
        w2 = core.omega_of_order(N, arcs, order)
        assert w2 == w, (w, w2)
        out["full_T"] = {"best_clique": w, "recheck": w2,
                         "order": order if w <= 6 else None}
        save_data(out)
        return

    if stage == "del":
        # L4: explicit order of T - (0,0) with clique <= 5
        qpot = identity_potential(*QR)
        # init: best template order (or merged-sum minus vertex 0)
        init = None
        if "templates" in out:
            best = min(out["templates"], key=lambda r: r["deletion_clique"])
            tmap = dict(deletion_templates(qpot))
            init = template_order(N, tmap[best["template"]], deleted=0)
            print(f"init from template {best['template']} "
                  f"(clique {best['deletion_clique']})", flush=True)
        if init is None:
            init = [v for v in merged_sum_order(
                NO, NI, lambda o: qpot[o], lambda a: ac_potential(a)) if v != 0]
        budget = float(os.environ.get("BUDGET_S", "800"))
        seed = int(os.environ.get("SEED", "11"))
        w, order = local_search(beats, init, target=5, budget_s=budget,
                                seed=seed, label="delT")
        assert 0 not in order and len(order) == N - 1
        # independent recheck on the RELABELED deletion subtournament
        survivors = sorted(order)
        relab = {v: i for i, v in enumerate(survivors)}
        sub = [(relab[u], relab[v]) for (u, v) in arcs
               if u in relab and v in relab]
        assert core.is_tournament(N - 1, sub)
        w2 = core.omega_of_order(N - 1, sub, [relab[v] for v in order])
        assert w2 == w, (w, w2)
        out["deletion"] = {"best_clique": w, "recheck_relabel": w2,
                           "order": order if w <= 5 else None}
        save_data(out)
        return

    if stage == "del3":
        # KILL-bar grinder: many short clique-guided SA restarts on the
        # deletion T-(0,0), diversified inits, cumulative count in JSON.
        rng = random.Random(int(os.environ.get("SEED", "1001")))
        budget = float(os.environ.get("BUDGET_S", "520"))
        stall_max = int(os.environ.get("STALL", "150"))
        t0 = time.time()
        qpot = identity_potential(*QR)
        tmap = deletion_templates(qpot)
        inits = [template_order(N, kf, deleted=0) for _, kf in tmap]
        # add best previous orders if recorded
        hist = out.get("del3", {"restarts": 0, "best_w": 99, "runs": []})
        gbw, gborder = 99, None
        for o_ in inits:
            w, c, s = eval_order(beats, o_)
            if w < gbw:
                gbw, gborder = w, list(o_)
        print(f"[del3] best template init clique={gbw}", flush=True)
        rs_this, evals = 0, 0
        while time.time() - t0 < budget and gbw > 5:
            rs_this += 1
            if rng.random() < 0.5 and gborder is not None:
                cur = list(gborder)
            else:
                cur = list(inits[rng.randrange(len(inits))])
            for _ in range(rng.randrange(2, 12)):
                i = rng.randrange(len(cur))
                v = cur.pop(i)
                cur.insert(rng.randrange(len(cur) + 1), v)
            cw, cc, cs = eval_order(beats, cur)
            evals += 1
            stall = 0
            maxe = int(os.environ.get("MAXE", "250"))
            re_evals = 0
            while (time.time() - t0 < budget and cw > 5
                   and stall < stall_max and re_evals < maxe):
                re_evals += 1
                cl = cs[rng.randrange(len(cs))] if cs else [cur[0]]
                v = cl[rng.randrange(len(cl))]
                cand = list(cur)
                cand.remove(v)
                cand.insert(rng.randrange(len(cand) + 1), v)
                nw, ncnt, ns = eval_order(beats, cand)
                evals += 1
                if (nw, ncnt) <= (cw, cc) or rng.random() < 0.02:
                    if (nw, ncnt) < (cw, cc):
                        stall = 0
                    else:
                        stall += 1
                    cur, cw, cc, cs = cand, nw, ncnt, ns
                else:
                    stall += 1
                if cw < gbw:
                    gbw, gborder = cw, list(cur)
                    print(f"[del3] NEW BEST clique={cw} cnt={cc} "
                          f"(restart {rs_this}, t={time.time()-t0:.0f}s)",
                          flush=True)
        hist["restarts"] += rs_this
        hist["best_w"] = min(hist["best_w"], gbw)
        hist["runs"].append({"seed": int(os.environ.get("SEED", "1001")),
                             "restarts": rs_this, "evals": evals,
                             "best_w": gbw, "t": round(time.time() - t0)})
        out["del3"] = hist
        print(f"[del3] run done: {rs_this} restarts, evals={evals}, "
              f"best={gbw}; CUMULATIVE restarts={hist['restarts']} "
              f"best={hist['best_w']}", flush=True)
        if gbw <= 5 and gborder is not None:
            survivors = sorted(gborder)
            relab = {u: i for i, u in enumerate(survivors)}
            sub = [(relab[x], relab[y]) for (x, y) in arcs
                   if x in relab and y in relab]
            w2 = core.omega_of_order(N - 1, sub, [relab[u] for u in gborder])
            assert w2 == gbw
            out["deletion"] = {"best_clique": w2, "recheck_relabel": w2,
                               "order": gborder}
        save_data(out)
        return

    if stage == "del2":
        # Equivalent target via L5 transitivity: find an order of FULL T with
        # backedge clique 6 such that SOME vertex v lies in EVERY 6-clique.
        # Then the restriction to T-v has clique 5, and the automorphism
        # sigma^{-o} tau^{-a} maps v=(o,a) to (0,0).
        rng = random.Random(int(os.environ.get("SEED", "101")))
        budget = float(os.environ.get("BUDGET_S", "800"))
        t0 = time.time()

        def eval_full(order):
            """(w, cnt, samples, hitters) — hitters = vertices in EVERY
            max-size clique (complete enumeration)."""
            g = nx.Graph()
            g.add_nodes_from(order)
            L = len(order)
            for i in range(L):
                a = order[i]
                for j in range(i + 1, L):
                    b = order[j]
                    if beats[b][a]:
                        g.add_edge(a, b)
            w, cnt, sample, inter = 1, 0, [], None
            for c in nx.find_cliques(g):
                if len(c) > w:
                    w, cnt, sample, inter = len(c), 1, [list(c)], set(c)
                elif len(c) == w:
                    cnt += 1
                    inter &= set(c)
                    if len(sample) < 50:
                        sample.append(list(c))
            return w, cnt, sample, (inter or set())

        init = out.get("full_T", {}).get("order")
        if init is None:
            qpot = identity_potential(*QR)
            init = merged_sum_order(NO, NI, lambda o: qpot[o],
                                    lambda a: ac_potential(a))
        cur = list(init)
        cw, cc, cs, hit = eval_full(cur)
        print(f"[del2] init w={cw} cnt={cc} hitters={sorted(hit)}", flush=True)
        best = (cw, cc)
        gorder, g_w, g_cnt, g_hit = list(cur), cw, cc, hit
        evals = 0
        while time.time() - t0 < budget:
            if (cw == 6 and hit) or cw <= 5:
                break
            cl = cs[rng.randrange(len(cs))]
            v = cl[rng.randrange(len(cl))]
            # try several insert positions, take the best
            cands = []
            base = list(cur)
            base.remove(v)
            for _ in range(4):
                cand = list(base)
                cand.insert(rng.randrange(len(cand) + 1), v)
                e = eval_full(cand)
                evals += 1
                cands.append((e[:2], cand, e))
            cands.sort(key=lambda x: x[0])
            (nw, ncnt), cand, e = cands[0]
            # accept if not worse, else annealed accept
            if (nw, ncnt) <= (cw, cc) or rng.random() < 0.03:
                cur, cw, cc, cs, hit = cand, nw, ncnt, e[2], e[3]
            if (cw, cc) < (g_w, g_cnt):
                gorder, g_w, g_cnt, g_hit = list(cur), cw, cc, hit
                if g_cnt % 1 == 0:
                    print(f"[del2] best w={g_w} cnt={g_cnt} "
                          f"|hitters|={len(g_hit)} t={time.time()-t0:.0f}s "
                          f"evals={evals}", flush=True)
        print(f"[del2] END w={cw} cnt={cc} hitters={sorted(hit)} "
              f"(global best w={g_w} cnt={g_cnt}) evals={evals}", flush=True)
        success = (cw == 6 and hit) or cw <= 5
        if success:
            if cw <= 5:
                v = cur[0]  # any vertex; restriction still has clique <=5
            else:
                v = sorted(hit)[0]
            o, a = v // NI, v % NI
            # automorphism g = sigma^{(19-o)%19} then tau^{(7-a)%7}: maps v->(0,0)
            def gmap(u):
                uo, ua = u // NI, u % NI
                return flat((uo + (NO - o)) % NO, (ua + (NI - a)) % NI)
            # check gmap is an automorphism (machine check, cheap)
            ok_auto = all(beats[x][y] == beats[gmap(x)][gmap(y)]
                          for x in range(N) for y in range(N) if x != y)
            assert ok_auto and gmap(v) == 0
            del_order = [gmap(u) for u in cur if u != v]
            assert 0 not in del_order and len(del_order) == N - 1
            survivors = sorted(del_order)
            relab = {u: i for i, u in enumerate(survivors)}
            sub = [(relab[x], relab[y]) for (x, y) in arcs
                   if x in relab and y in relab]
            assert core.is_tournament(N - 1, sub)
            w2 = core.omega_of_order(N - 1, sub, [relab[u] for u in del_order])
            print(f"[del2] deletion order clique (exact recheck) = {w2}",
                  flush=True)
            out["deletion"] = {"best_clique": w2, "recheck_relabel": w2,
                               "via": f"hitter v={v}=(o={o},a={a}) mapped to (0,0)",
                               "order": del_order if w2 <= 5 else None}
        else:
            prev = out.get("deletion", {})
            out.setdefault("del2_attempts", []).append(
                {"end_w": cw, "end_cnt": cc, "best_w": g_w, "best_cnt": g_cnt,
                 "evals": evals, "seed": int(os.environ.get("SEED", "101"))})
        save_data(out)
        return

    if stage == "summary":
        # assemble + independently re-verify the four-leg certificate
        b = out.get("build", {})
        ft = out.get("full_T", {})
        dl = out.get("deletion", {})
        ok = {}
        ok["L5_vertex_transitive"] = bool(b.get("vertex_transitive"))
        # L2 re-verify
        if ft.get("order"):
            ok["L2_fullT_clique"] = core.omega_of_order(N, arcs, ft["order"])
        # L4 re-verify on relabeled deletion
        if dl.get("order"):
            order = dl["order"]
            survivors = sorted(order)
            relab = {v: i for i, v in enumerate(survivors)}
            sub = [(relab[u], relab[v]) for (u, v) in arcs
                   if u in relab and v in relab]
            ok["L4_deletion_clique"] = core.omega_of_order(
                N - 1, sub, [relab[v] for v in order])
        ok["L1_lower_full"] = "ov(QR_19)=4 (P15) + ov(AC_7)=3 (P13) + lex lower bound (Lemma 3.8): ov(T)>=4+3-1=6"
        ok["L3_lower_deletion"] = "blocks 1..18 induce (QR_19-0)[AC_7]; ov(QR_19-0)=3 (P15 criticality) + ov(AC_7)=3 + lex lower: ov(T-(0,0))>=3+3-1=5"
        ok["certified_6_critical"] = (
            ok.get("L2_fullT_clique") == 6 and
            ok.get("L4_deletion_clique") == 5 and
            ok["L5_vertex_transitive"])
        out["certificate"] = ok
        print(json.dumps(ok, indent=1), flush=True)
        save_data(out)
        return

    raise SystemExit(f"unknown stage {stage}")


if __name__ == "__main__":
    try:
        main()
    except Timeout:
        print("HARD TIMEOUT", flush=True)
