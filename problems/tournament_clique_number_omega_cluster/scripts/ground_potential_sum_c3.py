"""GROUND (potential-sum counting mechanism for H19).

Candidate lemma: for every tournament H with ov(H)=k>=3 there EXISTS an optimal
order sigma of H (backedge clique exactly k) and a tie-break from a small fixed
family such that the merged potential-sum order on C3[H] -- key(c,v) = e(c) +
d_sigma(v), e=(1,1,2) on the outer C3 (0->1->2->0), d_sigma(v) = size of the
largest backedge clique of H^sigma whose sigma-maximum is v -- has backedge
clique exactly k+1.

Legs:
  n8       : 13 generic ov=3 inner classes (data/scan_c3_inner_b3.json), sigma
             enumeration EXHAUSTIVE (prefix-pruned DFS over clique<=3 orders).
  n9       : 1146 generic ov=3 classes (data/skeptic_o9_ov3_classes.json),
             capped at 200 optimal sigmas per class or first success.
  controls : H7 (the H16 counterexample inner, ov=2 -> predicted FAIL,
             merged clique 4 > 3) and QR_7 (Paley(7), ov=3 -> predicted pass).

Every SUCCESS witness order is re-verified with core.omega_of_order (the exact
oracle clique computation); the fast bitmask clique is internal only.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

E_POT = (1, 1, 2)  # potential of the outer C3 copies 0<1<2

TIEBREAK_IDS = [
    "d,c,pos", "c,d,pos", "pos,rotor,c",
    "-d,c,pos", "-c,d,pos", "-pos,rotor,c",
]


def bitcount(x):
    return bin(x).count("1")


def max_clique_mask(adj, mask):
    """Exact max clique of the graph (adjacency bitmasks `adj`) induced on
    vertex set `mask`.  Branch on the minimum candidate vertex: every clique
    of `cand` either avoids v or contains v (then lives in c & adj[v], where
    c are the candidates strictly after v)."""
    best = 0

    def bk2(size, cand):
        nonlocal best
        if cand == 0:
            if size > best:
                best = size
            return
        if size + bitcount(cand) <= best:
            return
        c = cand
        while c:
            if size + bitcount(c) <= best:
                return
            v = (c & -c).bit_length() - 1
            c &= c - 1
            bk2(size + 1, c & adj[v])

    bk2(0, mask)
    return best


def beats_masks(n, arcs):
    """beats[u] = bitmask of vertices u beats."""
    m = [0] * n
    for (u, v) in arcs:
        m[u] |= 1 << v
    return m


def lex_compose(nT, arcsT, nH, arcsH):
    """T[H]: vertex (a,b) -> flat index a*nH+b (same convention as
    ground_lex_compose_c3.py)."""
    bT = [[False] * nT for _ in range(nT)]
    for (u, v) in arcsT:
        bT[u][v] = True
    bH = [[False] * nH for _ in range(nH)]
    for (u, v) in arcsH:
        bH[u][v] = True
    n = nT * nH
    arcs = []
    for a in range(nT):
        for b in range(nH):
            for ap in range(nT):
                for bp in range(nH):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[b][bp]):
                        arcs.append((a * nH + b, ap * nH + bp))
    return n, arcs


def merged_order(n, sigma_pos, d, tiebreak):
    """Order of the 3n vertices of C3[H] by key(c,v)=e(c)+d(v) + tie-break.
    Returns the flat-index order (prec-smallest first)."""
    verts = []
    for c in range(3):
        for v in range(n):
            key = E_POT[c] + d[v]
            pos = sigma_pos[v]
            rotor = (pos + c) % 3
            if tiebreak == 0:
                t = (key, d[v], c, pos)
            elif tiebreak == 1:
                t = (key, c, d[v], pos)
            elif tiebreak == 2:
                t = (key, pos, rotor, c)
            elif tiebreak == 3:
                t = (key, -d[v], c, pos)
            elif tiebreak == 4:
                t = (key, -c, d[v], pos)
            else:
                t = (key, -pos, rotor, c)
            verts.append((t, c * n + v))
    verts.sort()
    return [fv for (_, fv) in verts]


def backedge_adj_for_order(beatsC, order):
    """Adjacency bitmasks (indexed by POSITION in the order) of the backedge
    graph of C3[H] under `order`."""
    m = len(order)
    adj = [0] * m
    for i in range(m):
        a = order[i]
        for j in range(i + 1, m):
            b = order[j]
            if beatsC[b] >> a & 1:  # backward arc b->a
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return adj


def attack_class(nH, arcsH, k, sigma_cap, deadline=None):
    """Enumerate optimal orders sigma (backedge clique == k) of H by
    prefix-pruned DFS; for each, try the 6 tie-breaks on C3[H].  Stop at first
    success (merged clique == k+1) or after sigma_cap sigmas (None =
    exhaustive).  Returns a result dict."""
    beatsH = beats_masks(nH, arcsH)
    nC, arcsC = lex_compose(3, [(0, 1), (1, 2), (2, 0)], nH, arcsH)
    beatsC = beats_masks(nC, arcsC)

    target = k + 1
    full = (1 << nH) - 1
    badj = [0] * nH  # partial backedge adjacency among placed vertices
    order = []
    dvals = [0] * nH
    state = {
        "sigmas": 0, "success": None, "min_merged": None,
        "merged_hist": {}, "exhausted": True, "timed_out": False,
    }

    def try_sigma():
        sigma_pos = [0] * nH
        for i, v in enumerate(order):
            sigma_pos[v] = i
        for tb in range(6):
            mo = merged_order(nH, sigma_pos, dvals, tb)
            adj = backedge_adj_for_order(beatsC, mo)
            w = max_clique_mask(adj, (1 << nC) - 1)
            state["merged_hist"][w] = state["merged_hist"].get(w, 0) + 1
            if state["min_merged"] is None or w < state["min_merged"]:
                state["min_merged"] = w
                state["min_witness"] = {"sigma": list(order), "tiebreak": tb,
                                        "merged_clique": w, "order": mo}
            if w == target:
                # re-verify with the exact oracle routine
                w2 = core.omega_of_order(nC, arcsC, mo)
                assert w2 == w, f"bitmask clique {w} != core {w2}"
                state["success"] = {
                    "sigma": list(order), "d": list(dvals), "tiebreak": tb,
                    "tiebreak_rule": TIEBREAK_IDS[tb],
                    "merged_clique_core_verified": w2,
                    "merged_order": mo,
                }
                return True
        return False

    def dfs(placed):
        if state["success"] is not None:
            return True
        if deadline is not None and time.time() > deadline:
            state["timed_out"] = True
            state["exhausted"] = False
            return True
        if placed == full:
            state["sigmas"] += 1
            if try_sigma():
                return True
            if sigma_cap is not None and state["sigmas"] >= sigma_cap:
                state["exhausted"] = False
                return True
            return False
        rest = full & ~placed
        c = rest
        while c:
            v = (c & -c).bit_length() - 1
            c &= c - 1
            nb = beatsH[v] & placed          # predecessors u with arc v->u
            dv = 1 + max_clique_mask(badj, nb) if nb else 1
            if dv > k:
                continue                      # prefix clique would exceed k
            # append v
            badj[v] = nb
            undo = []
            m = nb
            while m:
                u = (m & -m).bit_length() - 1
                m &= m - 1
                badj[u] |= 1 << v
                undo.append(u)
            order.append(v)
            dvals[v] = dv
            if dfs(placed | (1 << v)):
                return True
            order.pop()
            badj[v] = 0
            for u in undo:
                badj[u] &= ~(1 << v)
        return False

    dfs(0)
    res = {
        "n": nH, "k": k, "target": target,
        "sigmas_tried": state["sigmas"],
        "exhausted_over_optimal_sigmas": state["exhausted"],
        "timed_out": state["timed_out"],
        "pass": state["success"] is not None,
        "min_merged_clique": state["min_merged"],
        "merged_clique_histogram": {str(a): b for a, b in sorted(state["merged_hist"].items())},
    }
    if state["success"] is not None:
        res["witness"] = {kk: vv for kk, vv in state["success"].items() if kk != "merged_order"}
        res["witness"]["merged_order"] = state["success"]["merged_order"]
    elif "min_witness" in state:
        # re-verify the best (minimum) failure value with core as well
        mw = state["min_witness"]
        w2 = core.omega_of_order(nC, arcsC, mw["order"])
        assert w2 == mw["merged_clique"]
        res["min_witness"] = {"sigma": mw["sigma"], "tiebreak": mw["tiebreak"],
                              "merged_clique_core_verified": w2}
    return res


def qr7():
    arcs = []
    for i in range(7):
        for s in (1, 2, 4):
            arcs.append((i, (i + s) % 7))
    return 7, arcs


def main():
    leg = sys.argv[1]
    t0 = time.time()
    out = {"leg": leg, "tiebreaks": TIEBREAK_IDS, "e_potential": list(E_POT)}

    if leg == "n8":
        d = json.load(open(os.path.join(DATA, "scan_c3_inner_b3.json")))
        classes = d["per_class"]
        results = []
        for i, cl in enumerate(classes):
            arcs = [tuple(a) for a in cl["inner_arcs"]]
            ov = core.omega_vec(8, arcs)
            assert ov == 3, f"class {i}: ov={ov}!=3"
            r = attack_class(8, arcs, 3, sigma_cap=None,
                             deadline=time.time() + 600)
            r["inner_class_index"] = cl["inner_class_index"]
            results.append(r)
            print(f"[n8 {i}] idx={cl['inner_class_index']} pass={r['pass']} "
                  f"sigmas={r['sigmas_tried']} min={r['min_merged_clique']} "
                  f"hist={r['merged_clique_histogram']}", flush=True)
        out["results"] = results
        out["n_pass"] = sum(r["pass"] for r in results)
        out["n_classes"] = len(results)

    elif leg == "controls":
        results = {}
        # H7: the H16 counterexample inner, ov=2 -> predicted FAIL (merged 4>3)
        h = json.load(open(os.path.join(DATA, "h16_counterexample.json")))
        arcs7 = [tuple(a) for a in h["H7"]["arcs"]]
        ov = core.omega_vec(7, arcs7)
        assert ov == 2, f"H7 ov={ov}!=2"
        r = attack_class(7, arcs7, 2, sigma_cap=None,
                         deadline=time.time() + 300)
        results["H7_inner_ov2"] = r
        print(f"[control H7] pass={r['pass']} sigmas={r['sigmas_tried']} "
              f"min={r['min_merged_clique']} hist={r['merged_clique_histogram']}",
              flush=True)
        # QR_7 (Paley(7)), ov=3 -> predicted pass
        n7, aq = qr7()
        ov = core.omega_vec(n7, aq)
        assert ov == 3, f"QR_7 ov={ov}!=3"
        r = attack_class(7, aq, 3, sigma_cap=None, deadline=time.time() + 300)
        results["QR7_inner_ov3"] = r
        print(f"[control QR7] pass={r['pass']} sigmas={r['sigmas_tried']} "
              f"min={r['min_merged_clique']}", flush=True)
        out["results"] = results

    elif leg == "n9":
        start, end = int(sys.argv[2]), int(sys.argv[3])
        s = json.load(open(os.path.join(DATA, "skeptic_o9_ov3_classes.json")))
        classes = s["classes"][start:end]
        results = []
        fails = 0
        for i, cl in enumerate(classes):
            arcs = [tuple(a) for a in cl["arcs"]]
            r = attack_class(9, arcs, 3, sigma_cap=200,
                             deadline=time.time() + 30)
            r["class_index"] = cl["class_index"]
            results.append(r)
            if not r["pass"]:
                fails += 1
                print(f"[n9 {start+i}] idx={cl['class_index']} FAIL "
                      f"sigmas={r['sigmas_tried']} min={r['min_merged_clique']}",
                      flush=True)
            if (i + 1) % 100 == 0:
                print(f"[n9] {start+i+1} done, fails={fails}, "
                      f"{time.time()-t0:.0f}s", flush=True)
        out["range"] = [start, end]
        out["results"] = [
            {kk: r[kk] for kk in ("class_index", "pass", "sigmas_tried",
                                  "exhausted_over_optimal_sigmas", "timed_out",
                                  "min_merged_clique")}
            for r in results]
        out["fail_details"] = [r for r in results if not r["pass"]]
        out["n_pass"] = sum(r["pass"] for r in results)
        out["n_classes"] = len(results)
        # sample witnesses for audit
        out["sample_witnesses"] = [
            {"class_index": r["class_index"], "witness": r["witness"]}
            for r in results[:3] if r.get("witness")]

    out["elapsed_seconds"] = round(time.time() - t0, 2)
    suffix = leg if leg != "n9" else f"n9_{sys.argv[2]}_{sys.argv[3]}"
    path = os.path.join(DATA, f"ground_potential_sum_c3_{suffix}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"WROTE {path} elapsed={out['elapsed_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
