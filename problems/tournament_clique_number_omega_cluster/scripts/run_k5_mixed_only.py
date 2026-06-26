"""LEAN k=5 decider: skip full-value (ov(AC_7[AC_7])=5 by proved substitution law
P16: ov(T[H])=ov(T)+ov(H)-1=3+3-1).  Test ONLY the mixed deletion order-48:
one inner AC_7 block -> (AC_7 - v0), predict ov=4 uniformly (ge4 UNSAT, ge5 SAT).
Each SAT call is an OS-timeout-bounded subprocess.  Foreground.
"""
import sys, os, json, subprocess, time
sys.path.insert(0, os.path.dirname(__file__))
import core

HERE = os.path.dirname(__file__)
PY = os.path.join(HERE, "..", ".venv", "bin", "python")


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
        return {"K": K, "ge": None, "error": (p.stderr or "")[-300:], "wall": round(dt, 1)}
    return json.loads(p.stdout.strip())


def main():
    out = {}
    t0 = time.time()
    nA, aA = ac(7)
    out["full_value_by_proved_law"] = "ov(AC_7[AC_7]) = ov(AC_7)+ov(AC_7)-1 = 3+3-1 = 5"

    nA0, aA0 = core.subtournament(nA, aA, [w for w in range(nA) if w != 0])
    ov_A0 = core.omega_vec(nA0, aA0)
    out["AC7_minus_v0_ov"] = ov_A0
    print("AC_7 - v0 order", nA0, "ov", ov_A0, "(want 2 since AC_7 is 3-critical)", flush=True)

    recs = []
    for pos in [0, 1, 2, 3, 6]:
        blk = [(nA, aA)] * nA
        blk[pos] = (nA0, aA0)
        g4 = sat_call((nA, aA), blk, 4, 200)
        print(f"  pos={pos} ge4={g4}", flush=True)
        g5 = sat_call((nA, aA), blk, 5, 200)
        print(f"  pos={pos} ge5={g5}", flush=True)
        ov = 4 if (g4.get("ge") is True and g5.get("ge") is False) else None
        recs.append({"pos": pos, "ge4": g4, "ge5": g5, "ov": ov})
        print(f"  => pos={pos} ov={ov}", flush=True)
    out["mixed_order48"] = recs
    out["all_drop_to_4"] = all(r["ov"] == 4 for r in recs)
    out["any_no_drop_ov5"] = any(r["ov"] == 5 for r in recs)
    out["any_inconclusive"] = any(r["ov"] is None for r in recs)
    out["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "..", "data", "run_k5_mixed_only.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("=== SUMMARY ===", flush=True)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
