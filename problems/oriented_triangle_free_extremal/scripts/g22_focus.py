"""G22 focused decisive sweep: t=11..18, representative orientations, per-instance timeout."""
import os, sys, time, random, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from g22_grotzsch_bb import GROTZSCH, backward_blowup, _balanced_orientation

def call_with_timeout(fn, timeout_s):
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        try:
            res = fn()
            os.write(w, b"1" if res else b"0")
        except Exception:
            os.write(w, b"E")
        os._exit(0)
    os.close(w)
    t0 = time.time(); out = b""
    while True:
        wpid, _ = os.waitpid(pid, os.WNOHANG)
        if wpid == pid:
            out = os.read(r, 1); os.close(r)
            if out == b"1": return True
            if out == b"0": return False
            return "ERR"
        if time.time() - t0 > timeout_s:
            try: os.kill(pid, signal.SIGKILL); os.waitpid(pid, 0)
            except Exception: pass
            os.close(r); return "TIMEOUT"
        time.sleep(0.05)

def main():
    edges = GROTZSCH
    orients = {"acyclic_lohi": [(a, b) for (a, b) in edges],
               "balanced": _balanced_orientation(edges, 11)}
    for s in range(3):
        rnd = random.Random(100 + s)
        orients["rand%d" % s] = [(a, b) if rnd.random() < 0.5 else (b, a) for (a, b) in edges]
    # report which orientations are acyclic vs non-acyclic on the base
    for nm, o in orients.items():
        print("orient %-12s base_acyclic=%s" % (nm, core.is_acyclic(11, o)), flush=True)
    found = []; TIMEOUT = 200
    for t in range(11, 19):
        n = 11 * t
        for nm, o in orients.items():
            arcs = backward_blowup(o, t)
            if not (core.is_oriented(arcs) and core.is_triangle_free(n, arcs)):
                print("t=%2d n=%3d %-12s MALFORMED" % (t, n, nm), flush=True); continue
            t0 = time.time()
            r = call_with_timeout(lambda a=arcs, nn=n: core.is_k_dicolourable(nn, a, 3), TIMEOUT)
            print("t=%2d n=%3d %-12s 3dicol=%s (%.1fs)" % (t, n, nm, r, time.time()-t0), flush=True)
            if r is False:
                found.append((n, t, nm))
        if found: break
    print("FOUND_NON3DICOL:", found, flush=True)
    print("VERDICT:", "BEAT" if found else "NO_BEAT_KILL", flush=True)

if __name__ == "__main__":
    main()
