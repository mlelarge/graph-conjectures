import sys, os, math, random, signal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.g_saturated_alpha import build_saturated, exact_alpha
from scripts import core

class TO(Exception): pass
def _h(s, f): raise TO()

def avec_capped(n, arcs, timeout=120):
    signal.signal(signal.SIGALRM, _h)
    signal.alarm(timeout)
    try:
        r = core.acyclic_number(n, arcs)
        signal.alarm(0)
        return r
    except TO:
        signal.alarm(0)
        return None

def random_orient(G, rng):
    arcs = []
    for (u, v) in G.edges():
        if rng.random() < 0.5:
            arcs.append((u, v))
        else:
            arcs.append((v, u))
    return arcs

def main():
    import ast
    ns = ast.literal_eval(os.environ.get("ASAT_NS", "[30, 40, 50, 60, 70]"))
    seeds = ast.literal_eval(os.environ.get("ASAT_SEEDS", "[0, 1, 2]"))
    n_orient = int(os.environ.get("ASAT_NORIENT", "3"))
    print(f"{'n':>4} {'a_vec':>6} {'alpha':>6} {'a/sqrt(nlogn)':>13} {'a/(sqrtn*logn)':>15} {'alpha/sqrt(nlogn)':>17}", flush=True)
    rows = []
    for n in ns:
        logn = math.log(n)
        snl = math.sqrt(n * logn)         # sqrt(n log n)
        snln = math.sqrt(n) * logn        # sqrt(n) log n
        worst_avec = -1
        worst_alpha = None
        worst_alpha_at = None
        any_to = False
        for s in seeds:
            G = build_saturated(n, s)
            alpha = exact_alpha(G, timeout=120)
            rng = random.Random(1000 * s + 7)
            for o in range(n_orient):
                arcs = random_orient(G, rng)
                av = avec_capped(n, arcs, timeout=120)
                if av is None:
                    any_to = True
                    continue
                if av > worst_avec:
                    worst_avec = av
                    worst_alpha = alpha
                    worst_alpha_at = alpha
        if worst_avec < 0:
            print(f"{n:>4}  ALL TIMEOUT")
            continue
        a = worst_avec
        al = worst_alpha if worst_alpha is not None else float('nan')
        print(f"{n:>4} {a:>6} {str(al):>6} {a/snl:13.3f} {a/snln:15.3f} "
              f"{(al/snl if worst_alpha else float('nan')):17.3f}"
              + ("  (some orient timed out)" if any_to else ""), flush=True)
        rows.append((n, a, al, a/snl, a/snln, (al/snl if worst_alpha else None)))
    # summary
    if rows:
        col = [r[3] for r in rows]
        mean = sum(col)/len(col)
        var = sum((x-mean)**2 for x in col)/len(col)
        cv = math.sqrt(var)/mean
        ratio = col[-1]/col[0]
        print(f"\nSUMMARY a_vec/sqrt(n log n): first={col[0]:.3f} last={col[-1]:.3f} "
              f"ratio={ratio:.3f} CV={cv:.4f}")
        col2 = [r[4] for r in rows]
        print(f"SUMMARY a_vec/(sqrt(n) log n): first={col2[0]:.3f} last={col2[-1]:.3f} "
              f"ratio={col2[-1]/col2[0]:.3f}")
        ac = [r[5] for r in rows if r[5] is not None]
        if len(ac) >= 2:
            print(f"SUMMARY alpha/sqrt(n log n): first={ac[0]:.3f} last={ac[-1]:.3f} "
                  f"ratio={ac[-1]/ac[0]:.3f}")
        print(f"\nCONFIRM if ratio<1.10 & CV<0.06 ; KILL if ratio>1.12")

if __name__ == "__main__":
    main()
