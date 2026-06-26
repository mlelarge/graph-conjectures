"""H3 / HM-digirth-Brooks necessary-condition test.

Proposal: Harutyunyan-Mohar (EJC 2011) chi_vec(D) <= (1-e^-13) Dtilde(D) for
digon-free digraphs, with Dtilde = max_v sqrt(d+(v) d-(v)).  Triangle-free
oriented => digon-free => (claimed) applicable.  Contrapositive necessary
condition: chi_vec>=3 forces Dtilde >= 3/(1-e^-13) = 3.0000068, i.e. some vertex
with d+(v)*d-(v) >= 10.

CONFIRM: every chi_vec>=3 oriented triangle-free graph has max_v d+*d- >= 10.
KILL  : even one chi_vec>=3 witness with all vertices d+*d- <= 9 (Dtilde < 3).
"""
from __future__ import annotations
import itertools, math, sys
import core

THRESH = 10  # ceil((3/(1-e^-13))^2)

def deg_product_max(n, arcs):
    dout = [0]*n; din = [0]*n
    for (u, v) in arcs:
        dout[u] += 1; din[v] += 1
    return max(dout[v]*din[v] for v in range(n))

def run(nmin, nmax, connected=False, orient_cap=None):
    killers = []          # chi>=3 witnesses with max d+*d- <= 9
    confirm_witnesses = 0 # chi>=3 witnesses with max d+*d- >= 10
    min_prod_over_witnesses = None
    examples = []
    for n in range(nmin, nmax+1):
        ng = 0; nor = 0; nwit = 0
        for (gn, edges) in core.triangle_free_graphs(n, connected=connected):
            ng += 1
            m = len(edges)
            orients = core.all_orientations(edges)
            for arcs in orients:
                nor += 1
                # chi_vec capped at 3: we only care whether chi_vec>=3
                if core.is_k_dicolourable(n, arcs, 2):
                    continue  # chi_vec <= 2
                # chi_vec >= 3
                nwit += 1
                p = deg_product_max(n, arcs)
                if min_prod_over_witnesses is None or p < min_prod_over_witnesses:
                    min_prod_over_witnesses = p
                if p <= 9:
                    killers.append((n, p, list(arcs)))
                else:
                    confirm_witnesses += 1
                if len(examples) < 5:
                    examples.append((n, p, m))
        print(f"n={n}: tri_free_graphs={ng} orientations={nor} chi>=3_witnesses={nwit}", flush=True)
    return killers, confirm_witnesses, min_prod_over_witnesses, examples

if __name__ == "__main__":
    nmin = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    connected = "-c" in sys.argv
    killers, conf, minp, ex = run(nmin, nmax, connected=connected)
    print("="*60)
    print(f"THRESHOLD (d+*d- >= {THRESH} required for chi>=3 per HM-necessary)")
    print(f"chi>=3 witnesses with max d+*d- >= 10 (CONFIRM): {conf}")
    print(f"chi>=3 witnesses with max d+*d- <= 9  (KILL)   : {len(killers)}")
    print(f"min over all chi>=3 witnesses of (max_v d+*d-) : {minp}")
    if killers:
        n, p, arcs = killers[0]
        print(f"FIRST KILLER: n={n}, max d+*d- = {p} (< 10), arcs={arcs}")
        # certify with oracle: oriented, triangle-free, chi_vec
        print("  is_oriented      :", core.is_oriented(arcs))
        print("  is_triangle_free :", core.is_triangle_free(n, arcs))
        print("  chi_vec (exact)  :", core.dichromatic_number(n, arcs))
        print("  Dtilde           :", math.sqrt(p))
        print(f"VERDICT: KILL (HM bound does not give Dtilde>=3 necessary at chi=3)")
    else:
        print("VERDICT: CONFIRM signature held over enumerated range")
