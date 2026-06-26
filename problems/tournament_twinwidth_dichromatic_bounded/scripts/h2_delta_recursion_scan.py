"""H2: mine the recursion omegaVec(Delta(1, B, B)) as a function of omegaVec(B).

The open_crux is the growth rate of omegaVec(S_k), S_k = Delta(1, S_{k-1}, S_{k-1}).
The most promising non-enumerative lever (H2) is a closed-form recursion for
omegaVec(Delta(1, B, B)) in terms of omegaVec(B).  The ledger has only 5 data
points (TT1,TT2,TT3 -> 2 ; C3,S2 -> 2).  Here we exhaustively (up to iso, via
gentourng) enumerate ALL base tournaments B with nb <= NB_MAX, compute the exact
omegaVec(B) and the exact omegaVec(Delta(1,B,B)), and tabulate the map
  omegaVec(B)  -->  set of observed omegaVec(Delta(1,B,B)).

If this map is single-valued (a clean function), the recursion is settled and we
can iterate it along the S_k chain.  If for some w the image contains MORE than
one value, omegaVec(Delta(1,B,B)) is NOT determined by omegaVec(B) alone (the
recursion needs finer structure) -- itself a decisive, falsifiable finding.

Runs the EXACT oracle invariants (core.omega_vec); prints REAL numbers only.
"""
from __future__ import annotations

import json
import subprocess
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
import constructions as C


def all_tournaments(nb):
    """Yield arcs for each iso-class tournament on nb vertices via gentourng."""
    if nb == 1:
        yield []
        return
    proc = subprocess.run(["gentourng", "-q", str(nb)],
                          capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        s = "".join(c for c in line.strip() if c in "01")
        if len(s) != nb * (nb - 1) // 2:
            continue
        arcs = []
        idx = 0
        for i in range(nb):
            for j in range(i + 1, nb):
                arcs.append((i, j) if s[idx] == "1" else (j, i))
                idx += 1
        yield arcs


def main(nb_max=5):
    # map omegaVec(B) -> dict{ omegaVec(Delta(1,B,B)) : count }
    image = defaultdict(lambda: defaultdict(int))
    # also record an explicit witness arc-set for each (wB, wDelta) cell
    witness = {}
    per_size = {}
    for nb in range(1, nb_max + 1):
        cnt = 0
        for arcs in all_tournaments(nb):
            cnt += 1
            wB = core.omega_vec(nb, arcs)
            nD, aD = C.substitute_into_C3((nb, arcs),
                                          (nb, arcs),
                                          (1, []))  # Delta(B, B, 1) == cyclic
            # NOTE: S_k = Delta(1, S_{k-1}, S_{k-1}); the "1" part position is
            # irrelevant to omegaVec up to the cyclic symmetry of C3, but use the
            # EXACT same builder as the family for fidelity:
            nD, aD = C.substitute_into_C3((1, []), (nb, arcs), (nb, arcs))
            wD = core.omega_vec(nD, aD)
            image[wB][wD] += 1
            key = (wB, wD)
            if key not in witness:
                witness[key] = {"nb": nb, "arcs_B": arcs, "n_delta": nD}
        per_size[nb] = cnt
    # render
    out = {"nb_max": nb_max, "per_size_iso_counts": per_size,
           "recursion_map": {}, "single_valued": True, "multi_valued_at": []}
    for wB in sorted(image):
        cell = {str(wD): image[wB][wD] for wD in sorted(image[wB])}
        out["recursion_map"][str(wB)] = cell
        if len(image[wB]) > 1:
            out["single_valued"] = False
            out["multi_valued_at"].append(
                {"omega_B": wB,
                 "omega_delta_values": sorted(image[wB]),
                 "counts": cell})
    # S_k chain prediction if single-valued
    if out["single_valued"]:
        fmap = {wB: next(iter(image[wB])) for wB in image}
        chain = [1]  # omegaVec(S_1)=1
        ok = True
        for _ in range(2, 9):
            cur = chain[-1]
            if cur not in fmap:
                ok = False
                break
            chain.append(fmap[cur])
        out["predicted_omegaVec_S_chain"] = chain if ok else (chain, "incomplete: image misses a value")
        out["f_map"] = {str(k): v for k, v in sorted(fmap.items())}
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    nb_max = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(nb_max)
