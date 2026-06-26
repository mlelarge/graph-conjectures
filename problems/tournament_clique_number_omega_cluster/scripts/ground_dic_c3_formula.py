"""Ground the UNIVERSAL claim: for EVERY tournament H, dic(C3[H]) = ceil(3*dic(H)/2).

C3[H] = lex_substitute(directed_C3(), H): three blocks (one per outer C3 vertex);
inside a block arcs follow H, between distinct blocks arcs follow the outer C3.

dic = exact dichromatic number via the validated mono-triangle-free SAT decision
(ground_lift_lemma_step1.dic / dicolorable).

UNIVERSAL discipline: exhaustive GENERIC census of all tournaments via gentourng
(nauty), full iso classes, not a structured sub-family. ONE counterexample kills it.

Phases:
  --phase 4567  : exhaustive census n=4,5,6,7 (all iso classes from gentourng)
  --phase generic7 : (covered by 7 above; kept for compat) random-sample fallback
  --phase spots : named structured spot checks (consistency only)
"""
import sys, os, json, time, subprocess, math, itertools
sys.path.insert(0, os.path.dirname(__file__))
from ground_lift_lemma_step1 import dic, dicolorable, directed_triangles
from lexlib import lex_substitute, is_tournament
from constructions import directed_C3

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')


def ceil_3k_2(k):
    return (3 * k + 1) // 2  # ceil(3k/2)


def gentourng_classes(n):
    """All tournaments of order n up to iso, via nauty gentourng.
    Output format: one tournament per line, n then upper-triangle digraph6-ish.
    We use gentourng -z? Actually gentourng prints adjacency. Parse robustly."""
    # gentourng prints in 'tournament' format: for each line, first int is n,
    # then for i<j a bit: 1 if i->j else 0 (row-major over i<j). Use default output.
    out = subprocess.run(['gentourng', str(n)], capture_output=True, text=True,
                         timeout=600)
    if out.returncode != 0:
        raise RuntimeError("gentourng failed: " + out.stderr[:500])
    classes = []
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        # format: "n bits..." where bits are the C(n,2) orientations as one token
        # gentourng default: prints n then a string of 0/1 of length C(n,2)
        if len(parts) >= 2 and parts[0] == str(n):
            bits = parts[1]
        elif len(parts) == 1 and set(line) <= set('01') and len(line) == n*(n-1)//2:
            bits = line
        else:
            # try: whole line minus leading n
            bits = ''.join(c for c in line if c in '01')
        arcs = []
        idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                if idx >= len(bits):
                    break
                if bits[idx] == '1':
                    arcs.append((i, j))
                else:
                    arcs.append((j, i))
                idx += 1
        if idx != n * (n - 1) // 2:
            raise RuntimeError(f"parse mismatch line={line!r} idx={idx}")
        classes.append(arcs)
    return classes


def check_one(n, arcs):
    assert is_tournament(n, arcs)
    dH = dic(n, arcs, kmax=4)
    assert dH is not None, "dic(H) > 4 unexpected at this order"
    N, A = lex_substitute(directed_C3(), (n, arcs))
    dC = dic(N, A, kmax=7)
    assert dC is not None, "dic(C3[H]) > 7 unexpected"
    pred = ceil_3k_2(dH)
    return dH, dC, pred, (dC == pred)


def phase_census(ns):
    result = {}
    violations = []
    for n in ns:
        t0 = time.time()
        classes = gentourng_classes(n)
        nbad = 0
        hist = {}
        for arcs in classes:
            dH, dC, pred, ok = check_one(n, arcs)
            key = (dH, dC)
            hist[str(key)] = hist.get(str(key), 0) + 1
            if not ok:
                nbad += 1
                violations.append({"n": n, "arcs": arcs, "dic_H": dH,
                                   "dic_C3H": dC, "pred_ceil_3k_2": pred})
        dt = time.time() - t0
        result[n] = {"n_iso_classes": len(classes), "violations": nbad,
                     "hist_(dicH,dicC3H)": hist, "time_s": round(dt, 1)}
        print(f"n={n}: {len(classes)} iso classes, violations={nbad}, "
              f"hist(dicH,dicC3H)={hist}, {dt:.1f}s", flush=True)
    return result, violations


def main():
    phase = "4567"
    for a in sys.argv[1:]:
        if a.startswith("--phase"):
            phase = a.split("=", 1)[1] if "=" in a else None
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if phase is None and args:
        phase = args[0]

    out = {"phase": phase}
    if phase in ("4567", "456", "4567all"):
        ns = [4, 5, 6, 7] if phase != "456" else [4, 5, 6]
        res, viol = phase_census(ns)
        out["census"] = res
        out["violations"] = viol
        out["verdict"] = "PASS (no violations)" if not viol else f"FAIL: {len(viol)} violations"
        print("VERDICT:", out["verdict"], flush=True)
    elif phase == "small":
        res, viol = phase_census([4, 5])
        out["census"] = res
        out["violations"] = viol
        out["verdict"] = "PASS" if not viol else f"FAIL: {len(viol)}"
        print("VERDICT:", out["verdict"], flush=True)
    elif phase == "spots":
        spots = {}
        # C3[C3]: dic(C3)=2 -> pred ceil(6/2)=3
        for name, (n, arcs) in [("C3", directed_C3())]:
            spots[name] = check_one(n, arcs)
            print(name, "(dicH,dicC3H,pred,ok)=", spots[name], flush=True)
        out["spots"] = {k: list(v) for k, v in spots.items()}

    path = os.path.join(DATA, f'dic_c3_formula_census_{phase}.json')
    json.dump(out, open(path, 'w'), indent=1)
    print("wrote", path, flush=True)


if __name__ == '__main__':
    main()
