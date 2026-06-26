"""Fast depth-6 L_6 map: positional SAT per sigma-cyclic-rep cap triple, with a
WALL-CLOCK timeout per solve (subprocess + os.killpg), not a conflict budget.

A conflict budget does not bound wall-clock at depth 6 (3M conflicts ~ 2h on hard
instances, since the 16M-clause CNF has a tiny conflict rate).  Here each solve is
its own subprocess in its own session; if it exceeds TIMEOUT seconds we kill the
whole process group.  14 concurrent, sigma cyclic dedup.

Usage: run_L6_walltime.py [LO HI TIMEOUT_SEC]    (defaults 28 48 300)
"""
import sys, os, time, json, itertools, signal, subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PY = os.path.join(PROJ, ".venv", "bin", "python")
LO, HI = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (28, 48)
TIMEOUT = int(sys.argv[3]) if len(sys.argv) > 3 else 300
WORKERS = 14

try:
    os.setpgrp()
except OSError:
    pass

WORKER_CODE = (
    "import sys; sys.path.insert(0, %r);"
    "from decide_layer_positional import decide_caps_positional as d;"
    "r = d(6, tuple(map(int, sys.argv[1:4])));"
    "print('RESULT', 'SAT' if r['sat'] else ('UNSAT' if r['sat'] is False else 'UNK'),"
    " r.get('verified_heights'), flush=True)"
) % os.path.join(PROJ, "scripts")


def cyc_rep(c):
    return min((c, (c[1], c[2], c[0]), (c[2], c[0], c[1])))


def solve(caps):
    t = time.time()
    p = subprocess.Popen(
        [PY, "-c", WORKER_CODE, str(caps[0]), str(caps[1]), str(caps[2])],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        start_new_session=True,
    )
    try:
        out, _ = p.communicate(timeout=TIMEOUT)
        status = "UNKNOWN"
        for line in out.splitlines():
            if line.startswith("RESULT"):
                status = line.split()[1].replace("UNK", "UNKNOWN")
        return caps, caps[0]*caps[1]*caps[2], status, round(time.time()-t)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.communicate()
        return caps, caps[0]*caps[1]*caps[2], "TIMEOUT", round(time.time()-t)


def main():
    reps = {}
    for c in itertools.product(range(1, HI + 1), repeat=3):
        pr = c[0]*c[1]*c[2]
        if LO <= pr <= HI:
            reps.setdefault(cyc_rep(c), pr)
    cands = sorted(reps, key=lambda c: (reps[c], c))
    print(f"# L_6 walltime map: {len(cands)} reps, product [{LO},{HI}], "
          f"timeout={TIMEOUT}s, workers={WORKERS}", flush=True)
    log = open(os.path.join(PROJ, "data", "L6_walltime.log"), "w")
    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for res in ex.map(solve, cands):
            results.append(res)
            line = f"caps={res[0]} product={res[1]} {res[2]} {res[3]}s"
            print(line, flush=True); log.write(line + "\n"); log.flush()
    sat = [r for r in results if r[2] == "SAT"]
    upper = min((r[1] for r in sat), default=None)
    by_prod = {}
    for r in results:
        by_prod.setdefault(r[1], []).append(r[2])
    lower = None
    for pr in sorted(by_prod):
        if all(s == "UNSAT" for s in by_prod[pr]):
            lower = pr
        else:
            break
    summary = {"upper_min_SAT": upper, "all_unsat_through": lower,
               "n_sat": len(sat),
               "n_unsat": sum(1 for r in results if r[2] == "UNSAT"),
               "n_unresolved": sum(1 for r in results if r[2] in ("UNKNOWN", "TIMEOUT"))}
    print("# SUMMARY:", summary, flush=True)
    log.write(f"# SUMMARY: {summary}\n")
    json.dump({"results": [list(r) for r in results], "summary": summary,
               "timeout_s": TIMEOUT},
              open(os.path.join(PROJ, "data", "L6_walltime.json"), "w"))


if __name__ == "__main__":
    main()
