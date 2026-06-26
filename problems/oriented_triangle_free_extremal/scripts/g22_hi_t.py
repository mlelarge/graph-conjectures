"""G22 continuation: t=11..18 (n=121..198), all 32 orientations, direct flushed output."""
import os, sys, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from g22_grotzsch_bb import GROTZSCH, backward_blowup, _balanced_orientation

def main():
    edges = GROTZSCH
    orients = {"acyclic_lohi": [(a, b) for (a, b) in edges],
               "balanced": _balanced_orientation(edges, 11)}
    for s in range(30):
        rnd = random.Random(100 + s)
        orients["rand%d" % s] = [(a, b) if rnd.random() < 0.5 else (b, a) for (a, b) in edges]
    found = []
    for t in range(11, 19):
        n = 11 * t
        for nm, o in orients.items():
            arcs = backward_blowup(o, t)
            ok_or = core.is_oriented(arcs)
            ok_tf = core.is_triangle_free(n, arcs)
            if not (ok_or and ok_tf):
                print("t=%2d n=%3d %-12s NOT(or=%s tf=%s)" % (t, n, nm, ok_or, ok_tf), flush=True)
                continue
            t0 = time.time()
            r = core.is_k_dicolourable(n, arcs, 3)
            print("t=%2d n=%3d %-12s 3dicol=%s (%.1fs)" % (t, n, nm, r, time.time()-t0), flush=True)
            if r is False:
                found.append((n, t, nm))
        if found:
            break
    print("FOUND_NON3DICOL:", found, flush=True)

if __name__ == "__main__":
    main()
