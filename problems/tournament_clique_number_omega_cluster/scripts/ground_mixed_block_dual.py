"""GROUND the 'mixed TT_2 block = deletion' value-recursion dual.

Claim under test (proposal): deleting a vertex (a,b) from T[C3] equals the MIXED
lexicographic substitution T[H_*] where block a = TT_2 (= C3 minus a vertex) and
every other block = C3.  Predicted value-recursion:
   omega_vec(T[H_*]) = omega_vec(T[C3]) - 1
for EVERY choice of which block carries the TT_2, when T is critical.

We test exactly (core.omega_vec, n<=12) and via the validated no-K-clique SAT
oracle (any K) above the exact wall.  All foreground, hard alarm timeout.
"""
import sys, os, json, time, signal, itertools
sys.path.insert(0, os.path.dirname(__file__))
import core
from search_4critical_circulant import (omega_vec_ge_K_via_sat, validate_sat_oracle,
                                        circ_arcs)


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
    """T[blocks]: outer tournament T, per-outer-vertex inner block list `blocks`
    (each (nb, ab)).  Lex order: (a,b) beats (ap,bp) iff a beats ap in T, or
    a==ap and b beats bp inside block a."""
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
    """Uniform T[H]."""
    return mixed_sub(nT, arcsT, [(nH, arcsH)] * nT)


def ov_value(n, arcs, exact_cap=12, sat_max_K=8):
    """Exact omega_vec if n<=exact_cap, else via SAT no-K-clique scan upward.
    Returns (value, how)."""
    if core.is_tournament(n, arcs) is False:
        raise ValueError("not a tournament")
    if n <= exact_cap:
        return core.omega_vec(n, arcs), "exact"
    # SAT: find smallest K with ge_K False (omega_vec = K-1), i.e. scan K=2.. up
    val = None
    for K in range(2, sat_max_K + 1):
        ge, dt, ncl = omega_vec_ge_K_via_sat(n, arcs, K)
        if not ge:
            val = K - 1
            break
    return val, "sat"


class TO(Exception):
    pass


def alarm(sec):
    def h(*a):
        raise TO()
    signal.signal(signal.SIGALRM, h)
    signal.alarm(sec)


def main():
    out = {"tests": []}
    t0 = time.time()

    allok, _ = validate_sat_oracle()
    out["sat_oracle_validated"] = allok
    print("sat_oracle_ok=", allok, flush=True)

    nC, aC = c3()
    nTT, aTT = tt2()

    # ---- (i) C3[C3] exact baseline ----
    nCC, aCC = lex2(nC, aC, nC, aC)
    ov_CC = core.omega_vec(nCC, aCC)
    # replace block-0 by TT2 (= delete one inner vertex at outer 0)
    blocks = [(nTT, aTT)] + [(nC, aC)] * (nC - 1)
    nM, aM = mixed_sub(nC, aC, blocks)
    ov_M = core.omega_vec(nM, aM)
    # also: explicit deletion (C3[C3]) - vertex (0,2)  [delete inner vtx 2 at outer 0]
    del_v = 0 * nC + 2
    nD, aD = core.subtournament(nCC, aCC, [w for w in range(nCC) if w != del_v])
    ov_D = core.omega_vec(nD, aD)
    rec_i = {"name": "C3[C3]", "order_full": nCC, "ov_full": ov_CC,
             "order_mixed_TT2_block0": nM, "ov_mixed": ov_M,
             "ov_explicit_deletion": ov_D,
             "predicted_drop": ov_CC - 1,
             "mixed_eq_deletion": (ov_M == ov_D),
             "drop_holds": (ov_M == ov_CC - 1)}
    out["tests"].append(rec_i)
    print("(i) C3[C3]:", rec_i, flush=True)

    # uniformity over block position for C3[C3]
    pos_vals = []
    for pos in range(nC):
        blk = [(nC, aC)] * nC
        blk[pos] = (nTT, aTT)
        nMp, aMp = mixed_sub(nC, aC, blk)
        pos_vals.append(core.omega_vec(nMp, aMp))
    out["C3C3_block_position_ov"] = pos_vals
    print("(i') C3[C3] per-block-position ov:", pos_vals, "(want all =", ov_CC - 1, ")", flush=True)

    # ---- (ii) AC_7[C3], full and mixed (SAT) ----
    nA, aA = ac(7)  # order 7
    nAC, aAC = lex2(nA, aA, nC, aC)  # order 21
    # full value via SAT (>=4 true, >=5 false expected)
    ge4_full, _, _ = omega_vec_ge_K_via_sat(nAC, aAC, 4)
    ge5_full, _, _ = omega_vec_ge_K_via_sat(nAC, aAC, 5)
    ov_AC_full = 4 if (ge4_full and not ge5_full) else None
    # mixed: each outer-AC vertex carries C3 except one carries TT2; sweep all 7 positions
    ac_pos = []
    for pos in range(nA):
        blk = [(nC, aC)] * nA
        blk[pos] = (nTT, aTT)
        nMx, aMx = mixed_sub(nA, aA, blk)
        ge3, _, _ = omega_vec_ge_K_via_sat(nMx, aMx, 3)
        ge4, _, _ = omega_vec_ge_K_via_sat(nMx, aMx, 4)
        ov = 3 if (ge3 and not ge4) else ("?", ge3, ge4)
        ac_pos.append({"pos": pos, "order": nMx, "ge3": ge3, "ge4": ge4, "ov": ov})
        print(f"(ii) AC_7[H*] TT2@{pos} order={nMx} ge3={ge3} ge4={ge4} ov={ov}", flush=True)
    rec_ii = {"name": "AC_7[C3]", "order_full": nAC,
              "ge4_full": ge4_full, "ge5_full": ge5_full, "ov_full": ov_AC_full,
              "predicted_drop": (ov_AC_full - 1) if ov_AC_full else None,
              "per_position": ac_pos,
              "all_drop_to_3": all(r["ov"] == 3 for r in ac_pos)}
    out["tests"].append(rec_ii)

    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=2), flush=True)
    with open(os.path.join(os.path.dirname(__file__), "..", "data",
                           "ground_mixed_block_dual.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
