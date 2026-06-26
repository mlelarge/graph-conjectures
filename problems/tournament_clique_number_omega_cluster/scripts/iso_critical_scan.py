"""Branch (a) / H1+H4 experiment: exhaustive ISO-CLASS scan of all
3-omega_vec-critical tournaments at orders 7, 8, 9, using nauty `gentourng`
(one representative per isomorphism class).

For each iso class we compute exact omega_vec (brute force n<=7, branch-and-bound
n=8,9 -- both sound and cross-checked in core), test 3-omega_vec-criticality,
and -- critically for H4 -- whether the witness is WHOLE-TOURNAMENT 3-critical
(its own minimal certifying subtournament order == n, i.e. no proper subtournament
already has omega_vec>=3).

Output per n:
  - n_iso_classes              (sanity vs known nauty tournament counts)
  - omega_vec histogram over ALL iso classes
  - num 3-omega_vec-critical iso classes
  - num WHOLE-TOURNAMENT 3-critical iso classes (min_cert_order == n)
  - max order observed for a whole-tournament-3-critical class (== n if any)
  - example arc sets

This DIRECTLY maps the whole-tournament-3-critical window (H4): if it is
non-empty at 9 but EMPTY at 8 and grows/caps, that bounds ell(3).
"""
from __future__ import annotations

import json
import subprocess
import sys
from itertools import combinations

import core


GENTOURNG = "gentourng"


def gentourng_classes(n):
    """Yield arc lists, one per iso class of tournaments on n vertices.

    gentourng default output: upper triangle row by row in ascii, bit for each
    pair (i,j), i<j, in lexicographic order; bit=1 => arc i->j, bit=0 => arc j->i
    (verified vs n=3: '111'=TT_3, '101'=directed C3)."""
    proc = subprocess.run([GENTOURNG, str(n)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"gentourng {n} failed: {proc.stderr}")
    pairs = list(combinations(range(n), 2))
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        bits = line
        assert len(bits) == len(pairs), (len(bits), len(pairs), line)
        arcs = []
        for b, (i, j) in zip(bits, pairs):
            if b == "1":
                arcs.append((i, j))
            else:
                arcs.append((j, i))
        yield arcs


def min_cert_order(n, arcs, k):
    """Smallest subtournament order with omega_vec>=k (== n iff whole-tournament
    critical for that k). Returns the order."""
    sz, _ = core.min_subtournament_order_for_k(n, arcs, k)
    return sz


def scan(n, k=3, method="auto"):
    omega_hist = {}
    n_iso = 0
    crit = []                 # all k-critical
    whole = []                # whole-tournament k-critical (min_cert==n)
    for arcs in gentourng_classes(n):
        n_iso += 1
        w = core.omega_vec(n, arcs, method=method)
        omega_hist[w] = omega_hist.get(w, 0) + 1
        if w == k and core.is_k_omega_vec_critical(n, arcs, k):
            mc = min_cert_order(n, arcs, k)
            rec = {"arcs": arcs, "min_cert_order": mc}
            crit.append(rec)
            if mc == n:
                whole.append(rec)
    return {
        "n": n,
        "k": k,
        "n_iso_classes": n_iso,
        "omega_vec_histogram": {str(a): b for a, b in sorted(omega_hist.items())},
        "num_k_critical_iso": len(crit),
        "num_whole_tournament_k_critical_iso": len(whole),
        "whole_tournament_present": len(whole) > 0,
        "critical_examples": crit[:5],
        "whole_examples": whole[:5],
    }


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [7, 8, 9]
    out = {}
    for n in ns:
        method = "bruteforce" if n <= 7 else "bb"
        res = scan(n, 3, method=method)
        out[str(n)] = res
        print(json.dumps(res, indent=2), flush=True)
    with open("data/iso_critical_scan.json", "w") as f:
        json.dump(out, f, indent=2)
