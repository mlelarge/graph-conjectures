"""EXHAUSTIVE dic census of ALL circulant tournaments on Z/n, odd n in a range.

STEP 1: enumerate all generator sets g (one of {d, n-d} per pair, so 2^{(n-1)/2}
sets = the COMPLETE class), dedupe under multiplication-by-unit equivalence
(units of Z/n include -1, so reversal is covered); for each class rep decide
dic via the validated mono-triangle-free SAT encoding (ground_lift_lemma_step1).
STEP 2: for each dic=4 rep, vertex-criticality = dic(T-0)<=3 (3-dicolouring SAT
on the single deletion; all deletions isomorphic by circulant vertex-transitivity).
STEP 3 is run separately (no-K4 SAT ladder on survivors).

Soundness of the dedup: x -> u*x (u a unit) is an isomorphism C(g) -> C(u*g);
dic, omega_vec, vertex-criticality are isomorphism-invariant. Completeness:
every generator set appears in exactly one unit-orbit; we keep one rep per orbit
and record orbit size; sum of orbit sizes must equal 2^{(n-1)/2} (checked).
"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(__file__))
from ground_lift_lemma_step1 import dicolorable, directed_triangles, sub
from math import gcd


def circ_arcs(n, g):
    return [(i, (i + d) % n) for i in range(n) for d in g]


def all_generator_orbits(n):
    """Yield (rep_g_frozenset, orbit_size) one per unit-equivalence class;
    enumerate ALL 2^{(n-1)/2} generator sets, canonicalize by min over units."""
    pairs = [(d, n - d) for d in range(1, (n + 1) // 2)]
    units = [u for u in range(1, n) if gcd(u, n) == 1]
    seen = {}
    total = 0
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        g = frozenset(p[b] for p, b in zip(pairs, bits))
        total += 1
        canon = min(tuple(sorted((u * d) % n for d in g)) for u in units)
        seen.setdefault(canon, 0)
        seen[canon] += 1
    assert total == 2 ** len(pairs)
    return [(frozenset(c), cnt) for c, cnt in sorted(seen.items())], total


def dic_of_circ(n, g, kmax=6):
    arcs = circ_arcs(n, g)
    tris = directed_triangles(n, arcs)
    for k in range(1, kmax + 1):
        if dicolorable(n, arcs, k, tris):
            return k, arcs
    return kmax + 1, arcs  # means > kmax


def main():
    ns = [int(x) for x in sys.argv[1:]] or [11, 13, 15, 17, 19, 21, 23, 25, 27]
    out = {}
    for n in ns:
        t0 = time.time()
        orbits, total = all_generator_orbits(n)
        rows = []
        hist = {}
        for g, osz in orbits:
            k, arcs = dic_of_circ(n, g)
            hist[k] = hist.get(k, 0) + osz
            row = {"g": sorted(g), "orbit": osz, "dic": k}
            if k >= 4:
                # vertex-criticality: dic(T-0) <= k-1 ? (one deletion suffices, VT)
                nn, aa = sub(n, arcs, 0)
                row["del_dic_le_km1"] = bool(dicolorable(nn, aa, k - 1))
                row["vertex_critical"] = row["del_dic_le_km1"]
            rows.append(row)
        dt = time.time() - t0
        out[n] = {"n": n, "total_gen_sets": total, "n_orbits": len(orbits),
                  "dic_hist_labelled": hist, "time_s": round(dt, 1),
                  "dic_ge4": [r for r in rows if r["dic"] >= 4]}
        print(f"n={n}: {total} gen sets, {len(orbits)} unit-orbits, "
              f"dic hist (labelled) {hist}, dic>=4 reps: "
              f"{len(out[n]['dic_ge4'])}, {dt:.1f}s", flush=True)
        for r in out[n]["dic_ge4"]:
            print("   ", r, flush=True)
    path = os.path.join(os.path.dirname(__file__), '..', 'data',
                        'census_dic_circulant.json')
    # merge with existing file if present
    old = {}
    if os.path.exists(path):
        old = json.load(open(path))
    old.update({str(k): v for k, v in out.items()})
    json.dump(old, open(path, 'w'), indent=1)
    print("saved", path)


if __name__ == "__main__":
    main()
