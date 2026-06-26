"""Fast width-w resolution saturation via a literal occurrence index.

SOUND & COMPLETE for existence of a width-w refutation (Ben-Sasson--Wigderson):
close the width<=w input clauses under resolution, keeping only resolvents of
width <= w; empty clause derivable iff a width-w refutation exists.

No subsumption (sound to omit; only affects size). Occurrence index: for each
literal l, the set of clauses containing l; a new clause C is resolved only with
clauses containing -l for some l in C. Each clause processed once as 'active'.
"""
import os
import sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sat_refutation_width as RW


def width_w_saturate(clauses, w, time_budget, track_parents=False):
    t0 = time.time()
    S = set(c for c in clauses if len(c) <= w)
    occ = {}
    for c in S:
        for l in c:
            occ.setdefault(l, []).append(c)
    parents = {c: None for c in S} if track_parents else None
    empty = frozenset()
    queue = list(S)
    qi = 0
    while qi < len(queue):
        if time.time() - t0 > time_budget:
            return ("timeout", len(S), None, time.time() - t0)
        c1 = queue[qi]; qi += 1
        # resolve c1 against clauses sharing a clashing literal
        for l in list(c1):
            for c2 in occ.get(-l, ()):
                # resolve on l (unique clashing literal requirement: only valid
                # resolvent if l is the ONLY clash; resolve() checks tautology)
                # produce resolvent on this specific l
                r = (c1 - {l}) | (c2 - {-l})
                if any(-y in r for y in r):
                    continue  # tautology
                if len(r) > w:
                    continue
                r = frozenset(r)
                if r in S:
                    continue
                S.add(r)
                if track_parents:
                    parents[r] = (c1, c2)
                for ll in r:
                    occ.setdefault(ll, []).append(r)
                queue.append(r)
                if not r:
                    used = RW.collect_cone(empty, parents) if track_parents else None
                    return ("refuted", len(S), used, time.time() - t0)
    return ("saturated", len(S), None, time.time() - t0)


if __name__ == "__main__":
    import json
    targets = [int(x) for x in sys.argv[1:2]] or [11]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 500
    for p in targets:
        g = RW.ac_g(p); arcs = RW.circ_arcs(p, g)
        cl = RW.build_clauses(p, arcs)
        status, ssz, used, dt = width_w_saturate(cl, w, budget, track_parents=(p <= 13))
        print(f"p={p} w={w}: {status} |S|={ssz} used_axioms={len(used) if used else None} ({dt:.1f}s)")
        if used is not None:
            print("  sigma-invariant cone:", RW.is_sigma_invariant(used, p))
