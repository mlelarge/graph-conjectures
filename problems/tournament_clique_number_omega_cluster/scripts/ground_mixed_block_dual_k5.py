"""DECISIVE k=5 test of the mixed-TT2-block = deletion value-recursion.

X = (AC_7[C3])[C3]  order 63 (target).  Predict omega_vec(X)=5 and that the
MIXED substitution X[H_*] with exactly one innermost C3 block replaced by TT2
gives omega_vec = 4 (= 5-1), UNIFORMLY across block positions.  Fallback to the
smaller AC_7[AC_7] (order 49) recursion if SAT walls.

All foreground; per-SAT-call alarm so a single call cannot hang the turn.
"""
import sys, os, json, time, signal
sys.path.insert(0, os.path.dirname(__file__))
import core
from search_4critical_circulant import omega_vec_ge_K_via_sat


def c3():
    return 3, [(0, 1), (1, 2), (2, 0)]


def tt2():
    return 2, [(0, 1)]


def ac(n):
    m = (n - 1) // 2
    g = set(range(1, m)) | {m + 1}
    arcs = [(i, j) for i in range(n) for j in range(n)
            if i != j and ((j - i) % n) in g]
    return n, arcs


def mixed_sub(nT, arcsT, blocks):
    bT = core.beats_matrix(nT, arcsT)
    bH = [core.beats_matrix(nb, ab) for (nb, ab) in blocks]
    offset = []
    o = 0
    for (nb, _) in blocks:
        offset.append(o)
        o += nb
    arcs = []
    for a in range(nT):
        na = blocks[a][0]
        for b in range(na):
            for ap in range(nT):
                nap = blocks[ap][0]
                for bp in range(nap):
                    if a == ap and b == bp:
                        continue
                    if bT[a][ap] or (a == ap and bH[a][b][bp]):
                        arcs.append((offset[a] + b, offset[ap] + bp))
    return o, arcs


def lex2(nT, arcsT, nH, arcsH):
    return mixed_sub(nT, arcsT, [(nH, arcsH)] * nT)


class TO(Exception):
    pass


def with_alarm(sec, fn, *a, **k):
    def h(*_):
        raise TO()
    old = signal.signal(signal.SIGALRM, h)
    signal.alarm(sec)
    try:
        return fn(*a, **k)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def sat_ge(n, arcs, K, sec=250):
    try:
        ge, dt, ncl = with_alarm(sec, omega_vec_ge_K_via_sat, n, arcs, K)
        return {"K": K, "ge": ge, "t": round(dt, 2), "ncl": ncl}
    except TO:
        return {"K": K, "ge": None, "t": ">%ds" % sec, "timeout": True}


def main():
    out = {"k5": {}}
    t0 = time.time()
    nC, aC = c3()
    nTT, aTT = tt2()
    nA, aA = ac(7)

    # ---------- TARGET: X = (AC_7[C3])[C3] order 63 ----------
    nA7C3, aA7C3 = lex2(nA, aA, nC, aC)          # order 21, ov=4
    nX, aX = lex2(nA7C3, aA7C3, nC, aC)          # order 63
    print("TARGET X order", nX, flush=True)
    out["k5"]["target_order"] = nX

    # full value: expect ge5 True, ge6 False  (ov=5)
    f5 = sat_ge(nX, aX, 5, sec=300)
    print("X full ge5:", f5, flush=True)
    f6 = sat_ge(nX, aX, 6, sec=300)
    print("X full ge6:", f6, flush=True)
    out["k5"]["full"] = {"ge5": f5, "ge6": f6}

    # mixed: replace one INNERMOST C3 by TT2 (order 62).  innermost block index
    # ranges over the 21 outer (AC_7[C3]) vertices.  We test a few positions
    # (each outer-vertex's innermost C3 -> TT2) and check uniformity.
    # mixed_sub on outer = AC_7[C3] (order 21), blocks indexed by its 21 vertices.
    mixed_recs = []
    test_positions = [0, 1, 2, 3, 7, 10, 20]   # spread across outer vertices
    for pos in test_positions:
        blk = [(nC, aC)] * nA7C3
        blk[pos] = (nTT, aTT)
        nMx, aMx = mixed_sub(nA7C3, aA7C3, blk)   # order 62
        g4 = sat_ge(nMx, aMx, 4, sec=250)
        g5 = sat_ge(nMx, aMx, 5, sec=250)
        ov = 4 if (g4.get("ge") is True and g5.get("ge") is False) else None
        rec = {"pos": pos, "order": nMx, "ge4": g4, "ge5": g5, "ov": ov}
        mixed_recs.append(rec)
        print("X[H*] TT2@inner", pos, "order", nMx, "ge4", g4.get("ge"),
              "ge5", g5.get("ge"), "ov", ov, flush=True)
    out["k5"]["mixed_target"] = mixed_recs

    # ---------- FALLBACK: AC_7[AC_7] order 49, mixed deletion ----------
    # only if target walled (any None among full/mixed)
    walled = (f5.get("ge") is None or f6.get("ge") is None or
              any(r["ov"] is None for r in mixed_recs))
    out["k5"]["target_walled"] = walled
    if walled:
        print("TARGET WALLED -> fallback AC_7[AC_7]", flush=True)
        nAA, aAA = lex2(nA, aA, nA, aA)   # order 49, ov(AC7)+ov(AC7)-1 = 3+3-1 = 5
        out["k5"]["fallback_order"] = nAA
        ff5 = sat_ge(nAA, aAA, 5, sec=250)
        ff6 = sat_ge(nAA, aAA, 6, sec=250)
        print("AC7[AC7] full ge5", ff5.get("ge"), "ge6", ff6.get("ge"), flush=True)
        out["k5"]["fallback_full"] = {"ge5": ff5, "ge6": ff6}
        # mixed: one inner AC_7 block -> AC_7 minus a vertex (order 48).
        # AC_7 minus vertex 0:
        nA0, aA0 = core.subtournament(nA, aA, [w for w in range(nA) if w != 0])
        ov_A0 = core.omega_vec(nA0, aA0)   # should be 2 (AC_7 is 3-critical)
        out["k5"]["AC7_minus_v_ov"] = ov_A0
        fb_recs = []
        for pos in [0, 1, 3, 6]:
            blk = [(nA, aA)] * nA
            blk[pos] = (nA0, aA0)
            nMx, aMx = mixed_sub(nA, aA, blk)   # order 48
            g4 = sat_ge(nMx, aMx, 4, sec=250)
            g5 = sat_ge(nMx, aMx, 5, sec=250)
            ov = 4 if (g4.get("ge") is True and g5.get("ge") is False) else None
            fb_recs.append({"pos": pos, "order": nMx, "ge4": g4, "ge5": g5, "ov": ov})
            print("AC7[H*] (AC7-v)@", pos, "order", nMx, "ge4", g4.get("ge"),
                  "ge5", g5.get("ge"), "ov", ov, flush=True)
        out["k5"]["fallback_mixed"] = fb_recs

    out["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(os.path.dirname(__file__), "..", "data",
                           "ground_mixed_block_dual_k5.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("=== SUMMARY ===", flush=True)
    print(json.dumps(out["k5"], indent=2), flush=True)


if __name__ == "__main__":
    main()
