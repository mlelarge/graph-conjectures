"""INDEPENDENT re-verification of the potential-sum mechanism for H19.

Own code throughout (composition, d_sigma, tie-breaks, brute-force sigma
enumeration); the ONLY shared components are the canonical exact oracle
routines core.omega_of_order / core.omega_vec.

Legs:
  A. H7 control (ov=2): FULL brute force over all 7! orders; find optimal
     (clique-2) sigmas; for each, all 6 tie-breaks on C3[H7]; expect min
     merged clique 4 (> 3), i.e. FAIL, exhaustively.
  B. Two n=8 classes (2138, 6770): FULL brute force over all 8! orders to
     find optimal (clique-3) sigmas, then verify SOME (sigma, tiebreak)
     gives merged clique EXACTLY 4 on C3[H] via core.omega_of_order.
  C. Three hard n=9 classes (108879, 185188, 190299): verify ov(H)=3
     exactly (core.omega_vec), then DFS-enumerate optimal sigmas with OWN
     code and find a witness; verify merged clique 4 via core.omega_of_order
     on an independently built C3[H].
  D. ov(H)=3 spot-check on a seeded random sample of n=9 classes.
"""

import itertools
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

E = (1, 1, 2)


def my_compose_c3(nH, arcsH):
    """C3[H], outer 0->1->2->0, written independently: vertex (c,v) -> c*nH+v.
    Arc (c,v)->(c',v') iff c->c' in C3, or c==c' and v->v' in H."""
    outer = {(0, 1), (1, 2), (2, 0)}
    aset = set(arcsH)
    arcs = []
    for c in range(3):
        for cp in range(3):
            for v in range(nH):
                for vp in range(nH):
                    if (c, cp) in outer:
                        arcs.append((c * nH + v, cp * nH + vp))
                    elif c == cp and (v, vp) in aset:
                        arcs.append((c * nH + v, cp * nH + vp))
    return 3 * nH, arcs


def backedge_graph(nH, arcsH, sigma):
    """Backedge graph edges of H under order sigma (list, sigma[0] first)."""
    pos = {v: i for i, v in enumerate(sigma)}
    aset = set(arcsH)
    edges = set()
    for u in range(nH):
        for v in range(nH):
            if u != v and (v, u) in aset and pos[u] < pos[v]:
                edges.add(frozenset((u, v)))
    return edges


def clique_number(n, edges):
    """Brute-force max clique (own code, subsets)."""
    best = 1 if n else 0
    verts = list(range(n))
    for r in range(2, n + 1):
        found = False
        for comb in itertools.combinations(verts, r):
            if all(frozenset((a, b)) in edges
                   for a, b in itertools.combinations(comb, 2)):
                found = True
                break
        if found:
            best = r
        else:
            break
    return best


def d_sigma(nH, edges, sigma):
    """d[v] = size of largest backedge clique whose sigma-maximum is v."""
    pos = {v: i for i, v in enumerate(sigma)}
    d = {}
    for v in range(nH):
        preds = [u for u in range(nH)
                 if pos[u] < pos[v] and frozenset((u, v)) in edges]
        best = 1
        for r in range(1, len(preds) + 1):
            for comb in itertools.combinations(preds, r):
                if all(frozenset((a, b)) in edges
                       for a, b in itertools.combinations(comb, 2)):
                    best = max(best, r + 1)
        d[v] = best
    return d


def merged_orders(nH, sigma, d):
    """The 6 tie-break merged orders on C3[H] (flat index c*nH+v)."""
    pos = {v: i for i, v in enumerate(sigma)}
    outs = []
    for tb in range(6):
        items = []
        for c in range(3):
            for v in range(nH):
                key = E[c] + d[v]
                rotor = (pos[v] + c) % 3
                t = [(key, d[v], c, pos[v]),
                     (key, c, d[v], pos[v]),
                     (key, pos[v], rotor, c),
                     (key, -d[v], c, pos[v]),
                     (key, -c, d[v], pos[v]),
                     (key, -pos[v], rotor, c)][tb]
                items.append((t, c * nH + v))
        items.sort()
        outs.append([fv for (_, fv) in items])
    return outs


def attack_with_sigmas(nH, arcsH, k, sigmas, nC, arcsC, verbose=""):
    """Try every sigma in `sigmas` (each must have backedge clique == k);
    return (pass, min_merged, n_evals, witness)."""
    minm, witness, evals = None, None, 0
    for sigma in sigmas:
        edges = backedge_graph(nH, arcsH, sigma)
        assert clique_number(nH, edges) == k
        d = d_sigma(nH, edges, sigma)
        assert max(d.values()) == k
        for tb, mo in enumerate(merged_orders(nH, sigma, d)):
            w = core.omega_of_order(nC, arcsC, mo)
            evals += 1
            if minm is None or w < minm:
                minm = w
            if w == k + 1 and witness is None:
                witness = (list(sigma), tb, w)
                return True, minm, evals, witness
    return False, minm, evals, witness


def main():
    t0 = time.time()
    report = {}

    # ---- Leg A: H7 control --------------------------------------------
    h = json.load(open(os.path.join(DATA, "h16_counterexample.json")))
    arcs7 = [tuple(a) for a in h["H7"]["arcs"]]
    ov7 = core.omega_vec(7, arcs7)
    assert ov7 == 2, ov7
    opt = [list(p) for p in itertools.permutations(range(7))
           if clique_number(7, backedge_graph(7, arcs7, p)) == 2]
    nC7, arcsC7 = my_compose_c3(7, arcs7)
    # do NOT stop at first low value: sweep everything, track global min
    allvals = []
    for sigma in opt:
        edges = backedge_graph(7, arcs7, sigma)
        d = d_sigma(7, edges, sigma)
        for mo in merged_orders(7, sigma, d):
            allvals.append(core.omega_of_order(nC7, arcsC7, mo))
    hist = {}
    for w in allvals:
        hist[w] = hist.get(w, 0) + 1
    report["H7"] = {"ov": ov7, "n_optimal_sigmas": len(opt),
                    "merged_hist": hist, "min": min(allvals),
                    "fails_as_predicted": min(allvals) > 3}
    print("[A] H7: optimal sigmas =", len(opt), "merged hist =", hist,
          "min =", min(allvals), flush=True)

    # ---- Leg B: two n=8 classes ---------------------------------------
    d8 = json.load(open(os.path.join(DATA, "scan_c3_inner_b3.json")))
    by8 = {c["inner_class_index"]: c for c in d8["per_class"]}
    report["n8"] = {}
    for idx in (2138, 6770):
        arcs = [tuple(a) for a in by8[idx]["inner_arcs"]]
        assert core.omega_vec(8, arcs) == 3
        nC, arcsC = my_compose_c3(8, arcs)
        ok, minm, evals, wit = (False, None, 0, None)
        n_opt = 0
        for p in itertools.permutations(range(8)):
            if clique_number(8, backedge_graph(8, arcs, p)) != 3:
                continue
            n_opt += 1
            ok, minm_, ev, wit = attack_with_sigmas(
                8, arcs, 3, [list(p)], nC, arcsC)
            minm = minm_ if minm is None else min(minm, minm_)
            evals += ev
            if ok:
                break
        report["n8"][idx] = {"pass": ok, "optimal_sigmas_tried": n_opt,
                             "witness_tiebreak": wit[1] if wit else None,
                             "merged_clique": wit[2] if wit else None}
        print(f"[B] n8 idx={idx}: pass={ok} after {n_opt} optimal sigmas, "
              f"witness tb={wit[1] if wit else None}, clique={wit[2] if wit else None}",
              flush=True)

    # ---- Leg C: three hard n=9 classes --------------------------------
    s9 = json.load(open(os.path.join(DATA, "skeptic_o9_ov3_classes.json")))
    by9 = {c["class_index"]: c for c in s9["classes"]}
    report["n9_hard"] = {}
    for idx in (108879, 185188, 190299):
        arcs = [tuple(a) for a in by9[idx]["arcs"]]
        ov = core.omega_vec(9, arcs)
        assert ov == 3, (idx, ov)
        nC, arcsC = my_compose_c3(9, arcs)
        # own DFS over optimal sigmas: prefix prune on backedge clique
        aset = set(arcs)
        found = [None]
        cnt = [0]

        def dfs(order, rem):
            if found[0] is not None:
                return
            if not rem:
                cnt[0] += 1
                ok, _, _, wit = attack_with_sigmas(
                    9, arcs, 3, [order], nC, arcsC)
                if ok:
                    found[0] = (list(order), wit, cnt[0])
                return
            for v in sorted(rem):
                no = order + [v]
                # prefix backedge edges among placed vertices: for i<j in no,
                # edge iff the later-placed vertex beats the earlier one
                pedges = set()
                for i in range(len(no)):
                    for j in range(i + 1, len(no)):
                        if (no[j], no[i]) in aset:
                            pedges.add(frozenset((no[i], no[j])))
                # clique containing v among placed
                preds = [u for u in no[:-1] if frozenset((u, v)) in pedges]
                best = 1
                for r in range(1, len(preds) + 1):
                    for comb in itertools.combinations(preds, r):
                        if all(frozenset((a, b)) in pedges
                               for a, b in itertools.combinations(comb, 2)):
                            best = max(best, r + 1)
                if best > 3:
                    continue
                dfs(no, rem - {v})
                if found[0] is not None:
                    return

        dfs([], set(range(9)))
        sig, wit, nth = found[0]
        report["n9_hard"][idx] = {"ov": ov, "pass": True,
                                  "witness_sigma": sig,
                                  "witness_tiebreak": wit[1],
                                  "merged_clique": wit[2],
                                  "nth_optimal_sigma": nth}
        print(f"[C] n9 idx={idx}: ov=3, witness at optimal sigma #{nth}, "
              f"tb={wit[1]}, merged clique={wit[2]}", flush=True)

    # ---- Leg D: ov spot-check on random n=9 classes -------------------
    random.seed(20260610)
    sample = random.sample([c["class_index"] for c in s9["classes"]], 12)
    bad = []
    for idx in sample:
        arcs = [tuple(a) for a in by9[idx]["arcs"]]
        if core.omega_vec(9, arcs) != 3:
            bad.append(idx)
    report["n9_ov_spotcheck"] = {"sample": sample, "bad": bad}
    print("[D] ov=3 spot-check on", len(sample), "random n=9 classes; bad =",
          bad, flush=True)

    report["elapsed"] = round(time.time() - t0, 1)
    out = os.path.join(DATA, "indep_verify_potential_sum_c3.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=1, default=str)
    print("WROTE", out, "elapsed", report["elapsed"], "s", flush=True)


if __name__ == "__main__":
    main()
