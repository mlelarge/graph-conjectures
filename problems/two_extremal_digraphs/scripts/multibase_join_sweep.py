"""MULTI-BASE DIGON-FREE JOIN SWEEP — attack open_crux Step 1 / H6 from the join side.

Take two disjoint H_2 bases (symmetric odd cycles C3/C5/C7), relabel B after A,
connect them ONLY by balanced cross SINGLE arcs (no cross digon) so that the
digon-graph F_D has k>=2 components (a genuine digon-free cut), while BOTH sides
keep their odd-cycle obstruction. Optionally add INTERNAL single arcs inside each
base to raise capacity-degree at a chosen 'hub' vertex (mimic the H5 hub) and to
re-balance in=out>=2.

Target the corner H6 declares empty: 3-connected, Eulerian (in=out>=2),
k(F_D)>=2 (digon-free cut), lambda_D=2 AND chi_vec=3 -> is_2extremal with k>=2.

CONFIRM (kills H6): any output with kFD>=2, lambda=2, chi=3 (is_2extremal True).
KILL (supports H6): every kFD>=2 & chi=3 has lambda>=3, every lambda=2 has chi<=2.
"""
import sys, itertools
sys.path.insert(0, 'scripts')
import h2_oracle as H
from hub_cut_surgery import digon_components, capdeg, is_3connected, balance


def relabel(arcs, offset):
    return [(u + offset, v + offset) for (u, v) in arcs]


def balanced_cross_sets(n, a, base_arcs, cross_size, hub_internal_A, hub_internal_B,
                        hub_a, hub_b, max_sets=200000):
    """Enumerate balanced single-arc additions:
      - `cross_size` cross arcs between A=0..a-1 and B=a..n-1 (no cross digon),
        with #A->B == #B->A (so cut value is balanced),
      - optional internal single arcs inside A near hub_a and inside B near hub_b.
    We solve balance directly: every added arc set must restore in=out at every
    vertex with in=out>=2, no parallel with base, no new digon.
    """
    base = set(base_arcs)
    indeg, outdeg = balance(n, base_arcs)
    A = list(range(a)); B = list(range(a, n))

    # candidate cross arcs (no cross digon, no parallel)
    cross_ab = [(u, v) for u in A for v in B if (u, v) not in base and (v, u) not in base]
    cross_ba = [(u, v) for u in B for v in A if (u, v) not in base and (v, u) not in base]

    # candidate internal arcs touching a hub (to raise capacity degree)
    def internal_cands(verts, hub):
        c = []
        for u in verts:
            for v in verts:
                if u == v:
                    continue
                if (u, v) in base or (v, u) in base:
                    continue
                if hub in (u, v):
                    c.append((u, v))
        return c
    int_a = internal_cands(A, hub_a)
    int_b = internal_cands(B, hub_b)

    half = cross_size // 2
    results = []
    seen = set()
    count = 0
    iters = 0
    ITER_CAP = 8_000_000  # hard cap on inner-loop iterations to bound runtime
    # Pre-enumerate internal-arc option lists once (they are small).
    ia_opts = []
    for na in range(0, hub_internal_A + 1):
        for ia in itertools.combinations(int_a, na):
            ia_opts.append(list(ia))
    ib_opts = []
    for nb in range(0, hub_internal_B + 1):
        for ib in itertools.combinations(int_b, nb):
            ib_opts.append(list(ib))
    # choose half arcs A->B and half B->A
    for sab in itertools.combinations(cross_ab, half):
        for sba in itertools.combinations(cross_ba, half):
            cross = list(sab) + list(sba)
            for ia in ia_opts:
                for ib in ib_opts:
                    iters += 1
                    if iters > ITER_CAP:
                        print(f"    [ITER_CAP hit at {iters} iters; results so far={count}]", flush=True)
                        return results
                    add = cross + ia + ib
                    cs = set(add)
                    if len(cs) != len(add):
                        continue
                    # no digon among added
                    bad = False
                    for (u, v) in add:
                        if (v, u) in cs:
                            bad = True; break
                    if bad:
                        continue
                    ind = indeg[:]; outd = outdeg[:]
                    for (u, v) in add:
                        outd[u] += 1; ind[v] += 1
                    if all(ind[w] == outd[w] and outd[w] >= 2 for w in range(n)):
                        key = frozenset(add)
                        if key in seen:
                            continue
                        seen.add(key)
                        results.append(base_arcs + add)
                        count += 1
                        if count >= max_sets:
                            return results
    return results


def analyze(n, arcs, a):
    indeg, outdeg = balance(n, arcs)
    eul = all(indeg[v] == outdeg[v] and outdeg[v] >= 2 for v in range(n))
    if not eul:
        return None
    strong = H.is_strong(n, arcs)
    if not strong:
        return None
    two_conn = H.is_2connected(n, arcs)
    if not two_conn:
        return None
    three = is_3connected(n, arcs)
    k, _ = digon_components(n, arcs)
    lam = H.lambda_D(n, arcs)
    chi = None
    if lam == 2:
        chi = H.chi_vec(n, arcs)
    cap = capdeg(n, arcs)
    return dict(eul=eul, strong=strong, two_conn=two_conn, three=three,
                kFD=k, lam=lam, chi=chi, hub=max(cap), n=n, arcs=sorted(arcs))


def sweep_pair(baseA, baseB, cross_sizes, hi_a, hi_b, tag, max_sets=120000):
    (na, aarcs) = baseA
    (nb, barcs) = baseB
    a = na
    n = na + nb
    base_arcs = list(aarcs) + relabel(list(barcs), a)
    hub_a = 0
    hub_b = a  # first vertex of B
    print(f"\n===== {tag} (n={n}, a={a}) =====", flush=True)
    rows = []
    confirms = []
    hist = {}
    for cs in cross_sizes:
        cands = balanced_cross_sets(n, a, base_arcs, cs, hi_a, hi_b, hub_a, hub_b,
                                    max_sets=max_sets)
        nfilt = 0
        for cand in cands:
            res = analyze(n, cand, a)
            if res is None:
                continue
            if res['kFD'] < 2:
                continue  # join must keep a digon-free cut
            nfilt += 1
            rows.append(res)
            # histogram by failure mode
            if res['lam'] != 2:
                mode = f"lambda={res['lam']}"
            elif res['chi'] != 3:
                mode = f"chi={res['chi']}"
            else:
                mode = "TWO-EXTREMAL"
            sp = f"3conn={res['three']}"
            hist[(mode, sp)] = hist.get((mode, sp), 0) + 1
            if res['lam'] == 2 and res['chi'] == 3:
                confirms.append(res)
        print(f"  cross_size={cs}: {len(cands)} balanced sets, {nfilt} with kFD>=2 + strong + 2conn", flush=True)
    print("  FAILURE-MODE HISTOGRAM (mode, 3conn): count", flush=True)
    for k in sorted(hist, key=lambda x: (-hist[x], str(x))):
        print(f"    {k}: {hist[k]}", flush=True)
    # report any chi=3 with kFD>=2 (the rare interesting corner) even if lam!=2
    chi3 = [r for r in rows if r['chi'] == 3]
    print(f"  rows with chi=3 (lam==2 path): {len(chi3)}", flush=True)
    return rows, confirms


def main():
    C3 = H.sym_cycle(3)
    C5 = H.sym_cycle(5)
    C7 = H.sym_cycle(7)
    # oracle returns (n, frozenset); normalize to (n, list)
    C3 = (C3[0], list(C3[1]))
    C5 = (C5[0], list(C5[1]))
    C7 = (C7[0], list(C7[1]))

    all_confirms = []

    # cheapest first so results stream even if a later phase is heavy.
    # 1. two-C3 (n=6), cross 2,4, internal 2 each
    rows, conf = sweep_pair(C3, C3, [2, 4], 2, 2, "two-C3 join")
    all_confirms += conf

    # 2. C5 + C3 (n=8), cross 2,4, internal 1 each
    rows, conf = sweep_pair(C5, C3, [2, 4], 1, 1, "C5+C3 join")
    all_confirms += conf

    # 3. two-C5 (n=10), cross 2,4, internal 1 each (the explosive cross=6 split out)
    rows, conf = sweep_pair(C5, C5, [2, 4], 1, 1, "two-C5 join (cross<=4)")
    all_confirms += conf

    # 4. two-C5 (n=10) cross=6, NO internal (the probe-baseline family), capped
    rows, conf = sweep_pair(C5, C5, [6], 0, 0, "two-C5 join (cross=6)", max_sets=40000)
    all_confirms += conf

    # 5. C5 + C7 (n=12) cross 2,4 only, no internal (keep cheap)
    rows, conf = sweep_pair(C5, C7, [2, 4], 0, 0, "C5+C7 join", max_sets=40000)
    all_confirms += conf

    print("\n=========================================")
    if all_confirms:
        print(f"*** CONFIRM: {len(all_confirms)} candidate(s) with kFD>=2, lam=2, chi=3 (2-extremal): ***")
        for r in all_confirms:
            inh2 = H.is_in_H2(r['n'], r['arcs'])
            two = H.is_2extremal(r['n'], r['arcs'])
            print(f"  n={r['n']} kFD={r['kFD']} 3conn={r['three']} hub={r['hub']} "
                  f"is_2extremal={two} is_in_H2={inh2}")
            print(f"    arcs={r['arcs']}")
    else:
        print("KILL: NO output across the swept join family with kFD>=2, lam=2, chi=3.")
        print("      Every kFD>=2 & chi=3 has lambda>=3; every lambda=2 has chi<=2. H6 holds.")


if __name__ == "__main__":
    main()
