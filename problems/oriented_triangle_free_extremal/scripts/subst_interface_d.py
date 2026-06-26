"""Ground the interface-degree amplification proposal.

S_{ell,d}(H): ell copies of H=D25 on a directed ell-cycle. Internal arcs = D25
arcs in each copy. Interface copy c -> copy c+1: for each vertex x of H, send
forward arcs x_c -> ((x+a) mod 25)_{c+1} for a in offset-set A, |A|=d.

Triangle-freeness enforced by construction: reject any A for which some internal
edge {x,y} of D25 has its forward-neighbour sets overlapping (a common
interface-target would make x,y,target a triangle since x-y is an edge and both
point to target). We also call core.is_triangle_free as the hard check before
solving. Then call core.dichromatic_number(N, arcs, ub=4).
"""
import sys, itertools
sys.path.insert(0, "scripts")
import core
import constructions as C

H_n, H_arcs = C.D25()  # 25, arcs
assert H_n == 25

# underlying undirected edges of D25 (for the disjoint-neighbour pruning)
H_edges = [tuple(sorted(e)) for e in {frozenset((u, v)) for (u, v) in H_arcs}]


def build(ell, A):
    """Build S_{ell,d}(D25) with offset set A (tuple of shifts mod 25)."""
    N = ell * 25
    def vid(c, x):
        return (c % ell) * 25 + (x % 25)
    arcs = []
    # internal copies
    for c in range(ell):
        for (u, v) in H_arcs:
            arcs.append((vid(c, u), vid(c, v)))
    # forward interface
    for c in range(ell):
        for x in range(25):
            for a in A:
                arcs.append((vid(c, x), vid(c + 1, (x + a) % 25)))
    return N, arcs


def interface_disjoint(A):
    """Quick prune: for every internal edge {x,y}, forward-target sets disjoint."""
    for (x, y) in H_edges:
        tx = {(x + a) % 25 for a in A}
        ty = {(y + a) % 25 for a in A}
        if tx & ty:
            return False
    return True


def run(ell_list, d_list, max_n=209):
    found = []
    for d in d_list:
        # enumerate offset-sets A of size d over shifts 1..24 (shift 0 would
        # create a digon with the internal/backward structure; we keep forward
        # shifts non-zero). We allow all d-subsets of {1..24}.
        cand = [A for A in itertools.combinations(range(1, 25), d)
                if interface_disjoint(A)]
        print(f"[d={d}] {len(cand)} disjoint-pruned offset-sets out of "
              f"{len(list(itertools.combinations(range(1,25), d)))}", flush=True)
        for ell in ell_list:
            N = ell * 25
            tested = 0
            tf_ok = 0
            for A in cand:
                Narcs, arcs = build(ell, A)
                if not core.is_triangle_free(Narcs, arcs):
                    continue
                tf_ok += 1
                if not core.is_oriented(arcs):
                    continue
                tested += 1
                chi = core.dichromatic_number(Narcs, arcs, ub=4)
                if chi >= 4:
                    print(f"  *** CHI=4 HIT ell={ell} d={d} A={A} N={N} chi={chi}",
                          flush=True)
                    found.append((ell, d, A, N, chi))
                    return found  # stop at first hit
            print(f"  ell={ell} N={N}: tested {tested} triangle-free oriented "
                  f"instances (tf_ok={tf_ok}); all chi_vec<=3", flush=True)
    return found


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ell", type=int, nargs="+", default=[3])
    ap.add_argument("--d", type=int, nargs="+", default=[2])
    args = ap.parse_args()
    res = run(args.ell, args.d)
    print("FOUND:", res, flush=True)
