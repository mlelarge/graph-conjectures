"""Step (2): cross-validate the mixed-block value law
   omega_vec(T[H_*]) = ov(T) + max_c ov(H_c) - 1
against exact core.omega_vec for small outer T and arbitrary per-block H_c
(orders <= 12 exact).  Focus on the load-bearing case: exactly one block is
TT_2 (ov=1) and the rest are C3 (ov=2) -> law predicts ov(T)+2-1 = ov(T)+1,
matching the FULL T[C3] value (= ov(T)+1), i.e. NO drop relative to T[C3]?!

CAREFUL: the proposal's drop claim is ov(T[H_*]) = ov(T[C3]) - 1, with H_* having
ONE TT_2 and the rest C3.  ov(T[C3]) = ov(T)+2-1 = ov(T)+1.  The mixed law as the
proposal states it gives ov(T[H_*]) = ov(T) + max_c ov(H_c) - 1.  Since max_c is
still 2 (the C3 blocks dominate the TT_2), the naive max-law predicts ov(T)+1 = NO
drop.  The proposal's DROP requires the max-law to FAIL here (the single TT_2 must
*cost* the +1).  So this sweep checks which formula is right:
   max-law  : ov(T[H_*]) = ov(T) + max_c ov(H_c) - 1   (no drop; predicts ov(T)+1)
   proposal : ov(T[H_*]) = ov(T[C3]) - 1 = ov(T)        (drop)
We measure exactly and report which holds.
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core


def c3():
    return 3, [(0, 1), (1, 2), (2, 0)]


def tt2():
    return 2, [(0, 1)]


def tt1():
    return 1, []


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


def main():
    out = []
    nC, aC = c3()
    nTT, aTT = tt2()
    n1, a1 = tt1()
    # outer candidates (small, exact)
    outers = {"C3": c3()}  # ov=2
    # AC_7 outer with all-C3 except one block -> order can exceed 12, skip exact;
    # here we restrict to exact-feasible orders (<=12).
    # block menus
    menus = {"C3": (nC, aC), "TT2": (nTT, aTT), "TT1": (n1, a1)}
    ov_block = {"C3": 2, "TT2": 1, "TT1": 1}

    for oname, (nT, aT) in outers.items():
        ovT = core.omega_vec(nT, aT)
        # all assignments of menu items to the nT blocks (limit total order<=12)
        for combo in itertools.product(menus.keys(), repeat=nT):
            blocks = [menus[c] for c in combo]
            tot = sum(b[0] for b in blocks)
            if tot > 12:
                continue
            nM, aM = mixed_sub(nT, aT, blocks)
            ov = core.omega_vec(nM, aM)
            maxc = max(ov_block[c] for c in combo)
            max_law = ovT + maxc - 1
            # ov(T[C3]) = ovT + 2 - 1
            ovTC3 = ovT + 1
            rec = {"outer": oname, "blocks": list(combo), "order": tot,
                   "ov_exact": ov, "ovT": ovT, "maxc": maxc,
                   "max_law_pred": max_law, "max_law_ok": ov == max_law,
                   "ovT[C3]": ovTC3, "drop_from_TC3": ovTC3 - ov}
            out.append(rec)

    # summary
    max_law_fails = [r for r in out if not r["max_law_ok"]]
    print("total mixed products tested:", len(out))
    print("max-law (ov = ovT + max_c ov(H_c) - 1) FAILURES:", len(max_law_fails))
    for r in max_law_fails:
        print("  FAIL", r["blocks"], "order", r["order"], "ov", r["ov_exact"],
              "max_law_pred", r["max_law_pred"])
    # focus: exactly one TT2, rest C3
    print("\n--- one TT2 + rest C3 (the proposal's drop case) ---")
    for r in out:
        b = r["blocks"]
        if b.count("TT2") == 1 and b.count("C3") == len(b) - 1:
            print("  blocks", b, "order", r["order"], "ov", r["ov_exact"],
                  "ovT[C3]", r["ovT[C3]"], "drop_from_TC3", r["drop_from_TC3"],
                  "max_law_pred", r["max_law_pred"], "max_law_ok", r["max_law_ok"])
    with open(os.path.join(os.path.dirname(__file__), "..", "data",
                           "ground_mixed_law_sweep.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
