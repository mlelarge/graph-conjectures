"""Parent: for each (n,c,seed) spawn deg_child.py with a HARD os.killpg timeout.
Aggregates best (min a*) per n, computes witness-set degeneracy d*, prints the
decision table. This is the robust ground_plan runner (timeouts actually kill).
"""
import json
import math
import os
import signal
import subprocess
import sys
import time

PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.venv', 'bin', 'python')
CHILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deg_child.py')

NS = [20, 30, 40, 50, 60]
CS = [1.5, 2.0]
SEEDS = [0, 1, 2]
TIMEOUT = 90  # hard wall-clock per instance


def run_instance(n, c, s, timeout):
    proc = subprocess.Popen(
        [PY, CHILD, str(n), str(c), str(s)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, preexec_fn=os.setsid)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        proc.communicate()
        return None
    if proc.returncode != 0 or not out.strip():
        return None
    return json.loads(out.strip().splitlines()[-1])


def avg_degree_in_set(edges, S):
    Sset = set(S)
    e_in = sum(1 for (u, v) in edges if u in Sset and v in Sset)
    return 2.0 * e_in / len(S), e_in


def main():
    rows = []
    for n in NS:
        best = None  # (a, S, edges, c, s)
        for c in CS:
            for s in SEEDS:
                t0 = time.time()
                res = run_instance(n, c, s, TIMEOUT)
                if res is None:
                    print(f"   [n={n} c={c} seed={s}] TIMEOUT/skip "
                          f"({time.time()-t0:.1f}s)", flush=True)
                    continue
                a = res["a"]; S = res["S"]; edges = [tuple(e) for e in res["edges"]]
                print(f"   [n={n} c={c} seed={s}] a={a} "
                      f"({time.time()-t0:.1f}s)", flush=True)
                if best is None or a < best[0]:
                    best = (a, S, edges, c, s)
        if best is None:
            print(f"n={n}: ALL skipped", flush=True)
            continue
        a, S, edges, c, s = best
        d_star, e_in = avg_degree_in_set(edges, S)
        lemma24 = 2.0 * math.log2(n)
        sqrt_logn = math.sqrt(math.log(n)); logn = math.log(n)
        rows.append((n, a, len(S), e_in, d_star, lemma24,
                     d_star / sqrt_logn, d_star / logn, c, s))
        print(f"n={n:>3} a*={a:>3} |S*|={len(S):>3} e_in={e_in:>4} "
              f"d*={d_star:.4f} 2log2n={lemma24:.4f} "
              f"d*/sqrt(logn)={d_star/sqrt_logn:.4f} "
              f"d*/logn={d_star/logn:.4f} (best c={c} seed={s})", flush=True)

    print("\n=== SUMMARY TABLE ===", flush=True)
    print(f"{'n':>4} {'a*':>4} {'|S*|':>5} {'d*':>8} {'2log2n':>8} "
          f"{'d*/sqrt(logn)':>14} {'d*/logn':>9}", flush=True)
    r1, r2, gaps = [], [], []
    for (n, a, sz, e_in, d_star, lemma24, rr1, rr2, c, s) in rows:
        print(f"{n:>4} {a:>4} {sz:>5} {d_star:>8.4f} {lemma24:>8.4f} "
              f"{rr1:>14.4f} {rr2:>9.4f}", flush=True)
        r1.append(rr1); r2.append(rr2); gaps.append(lemma24 - d_star)

    def flat(v):
        m = sum(v) / len(v); return (max(v) - min(v)) / m, m
    fr1, m1 = flat(r1); fr2, m2 = flat(r2)
    print(f"\nd*/sqrt(logn): {[f'{x:.3f}' for x in r1]}  mean={m1:.4f} "
          f"range/mean={fr1:.4f} [CONFIRM<0.20]", flush=True)
    print(f"d*/logn:       {[f'{x:.3f}' for x in r2]}  mean={m2:.4f} "
          f"range/mean={fr2:.4f} [KILL<0.20]", flush=True)
    print(f"Lemma2.4 gap (2log2n-d*): {[f'{g:.3f}' for g in gaps]}", flush=True)
    print(f"d* values: {[f'{row[4]:.3f}' for row in rows]} "
          f"(is d* roughly CONSTANT?)", flush=True)
    print("\n=== DECISION ===", flush=True)
    print(f"flatness d*/sqrt(logn)={fr1:.4f}  vs  d*/logn={fr2:.4f}", flush=True)
    if fr1 < 0.20 and fr1 < fr2 and all(g > 0 for g in gaps):
        print("VERDICT-SIGNAL: CONFIRM", flush=True)
    elif fr2 < 0.20 and fr2 < fr1:
        print("VERDICT-SIGNAL: KILL", flush=True)
    else:
        print("VERDICT-SIGNAL: AMBIGUOUS", flush=True)


if __name__ == "__main__":
    main()
