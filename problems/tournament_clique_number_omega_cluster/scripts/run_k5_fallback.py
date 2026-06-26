"""Driver: k=5 fallback decider via OS-timeout-bounded SAT subprocesses.

AC_7[AC_7] order 49 (predicted ov=5 = 3+3-1).  Mixed: one inner AC_7 block ->
AC_7 minus a vertex (order 48), predicted ov=4 uniformly across block positions.
Each SAT call is a separate `timeout SEC python sat_one_call.py ...` so it is
hard-killable.  All foreground.
"""
import sys, os, json, subprocess, time
sys.path.insert(0, os.path.dirname(__file__))
import core

HERE = os.path.dirname(__file__)
PY = os.path.join(HERE, "..", ".venv", "bin", "python")


def c3():
    return 3, [(0, 1), (1, 2), (2, 0)]


def ac(n):
    m = (n - 1) // 2
    g = set(range(1, m)) | {m + 1}
    arcs = [(i, j) for i in range(n) for j in range(n)
            if i != j and ((j - i) % n) in g]
    return n, arcs


def sat_call(outer, blocks, K, sec):
    payload = {"outer": [outer[0], [list(e) for e in outer[1]]],
               "blocks": [[nb, [list(e) for e in ab]] for (nb, ab) in blocks],
               "K": K}
    cmd = ["timeout", str(sec), PY, os.path.join(HERE, "sat_one_call.py"),
           json.dumps(payload)]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    if p.returncode == 124:
        return {"K": K, "ge": None, "timeout": True, "wall": round(dt, 1)}
    if p.returncode != 0:
        return {"K": K, "ge": None, "error": p.stderr[-400:], "wall": round(dt, 1)}
    return json.loads(p.stdout.strip())


def main():
    out = {}
    t0 = time.time()
    nA, aA = ac(7)
    nC, aC = c3()

    # ----- FALLBACK A: AC_7[AC_7] order 49 -----
    blocks_full = [(nA, aA)] * nA          # AC_7[AC_7]
    print("AC_7[AC_7] order 49: full value", flush=True)
    f5 = sat_call((nA, aA), blocks_full, 5, 280)
    print("  ge5:", f5, flush=True)
    f6 = sat_call((nA, aA), blocks_full, 6, 280)
    print("  ge6:", f6, flush=True)
    ov_full = 5 if (f5.get("ge") is True and f6.get("ge") is False) else None
    out["AC7AC7_full"] = {"ge5": f5, "ge6": f6, "ov": ov_full}

    # AC_7 minus vertex 0 (the downgraded block), exact ov
    nA0, aA0 = core.subtournament(nA, aA, [w for w in range(nA) if w != 0])
    ov_A0 = core.omega_vec(nA0, aA0)
    out["AC7_minus_v0_ov"] = ov_A0
    print("AC_7 - v0 order", nA0, "ov", ov_A0, "(want 2)", flush=True)

    # mixed: one inner AC_7 block -> (AC_7 - v0), order 48; sweep positions
    pos_recs = []
    for pos in [0, 1, 3, 6]:
        blk = [(nA, aA)] * nA
        blk[pos] = (nA0, aA0)
        g4 = sat_call((nA, aA), blk, 4, 250)
        g5 = sat_call((nA, aA), blk, 5, 250)
        ov = 4 if (g4.get("ge") is True and g5.get("ge") is False) else None
        rec = {"pos": pos, "ge4": g4, "ge5": g5, "ov": ov}
        pos_recs.append(rec)
        print(f"  AC7[H*] (AC7-v0)@{pos}: ge4={g4.get('ge')} ge5={g5.get('ge')} ov={ov}",
              flush=True)
    out["AC7AC7_mixed"] = pos_recs
    out["mixed_all_drop_to_4"] = all(r["ov"] == 4 for r in pos_recs)
    out["mixed_any_no_drop"] = any(r["ov"] == 5 for r in pos_recs)

    out["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "..", "data", "run_k5_fallback.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("=== SUMMARY ===", flush=True)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
