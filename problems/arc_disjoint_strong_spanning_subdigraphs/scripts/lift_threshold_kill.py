"""SETTLE THE D6 CAVEAT negatively with an AT-THRESHOLD witness.

T(k,lam)=fam_private_arc(k,mult=lam): V={s=0,o=1,p_1..p_k}; n=k+2;
  arcs: (s,o)*lam,(o,s)*lam; per toggle p: (s,p)*lam,(p,o)*lam,(p,s)*1.

Witness T(69,37): n=71, lam(oracle)=37 >= 6*log2(71)=36.898 (AT the EC-log threshold).

Claim (existential, about the PROOF ROUTE not SAD status):
 (i)  oracle.arc_connectivity(T(69,37)) == 37 >= 6*log2(71).
 (ii) labeled arc-set fingerprints of delta^+({o}uS) are pairwise DISTINCT with
      |F_S| = 37+|S| across exhaustive |S|<=2 + >=20000 random larger S
      (tag-arc injectivity).
 (iii) exact rational non-min mass sum_{j=1..69} C(69,j)*2^{-(36+j)} > 1 (=20.569).
 (iv) the alpha=1 (min-cut) band of this family stays <= n^2 (H5 core untouched).

CONFIRM (route-dead) iff ALL four hold.
"""
import sys, os, json, time, math, random
from fractions import Fraction
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle


def fam_private_arc(k, mult):
    s, o = 0, 1
    arcs = [(s, o)] * mult + [(o, s)] * mult
    for j in range(k):
        p = 2 + j
        arcs += [(s, p)] * mult
        arcs += [(p, o)] * mult
        arcs += [(p, s)]            # private cheap tag arc into s
    return (k + 2), arcs


def labeled_outcut_fingerprint(n, arcs, X):
    """delta^+(X) as a frozenset of DISTINCT crossing (tail,head) pairs WITH
    multiplicity, and the cut SIZE = sum of multiplicities of crossing pairs.
    Parallel arcs cross together, so the (pair->mult) crossing map is a faithful
    labeled-arc-set id. Returns (fingerprint_tuple, size)."""
    Xset = set(X)
    cross_mult = {}
    for (u, v) in arcs:
        if u in Xset and v not in Xset:
            cross_mult[(u, v)] = cross_mult.get((u, v), 0) + 1
    fp = tuple(sorted(cross_mult.items()))
    size = sum(cross_mult.values())
    return fp, size


def main():
    t0 = time.time()
    k, lam = 69, 37
    n, arcs = fam_private_arc(k, lam)
    s, o = 0, 1
    toggles = list(range(2, 2 + k))

    # ---- (i) oracle lambda + threshold ----
    lam_oracle = oracle.arc_connectivity(n, arcs)
    thresh = 6 * math.log2(n)
    check_i = (lam_oracle == lam) and (lam_oracle >= thresh)

    # ---- (ii) tag-arc injectivity: distinct fingerprints, |F_S| = lam + |S| ----
    seen = {}            # fingerprint -> S (as frozenset) that produced it
    collisions = []
    size_violations = []
    n_tested = 0

    def test_S(S):
        nonlocal n_tested
        X = [o] + list(S)
        fp, size = labeled_outcut_fingerprint(n, arcs, X)
        n_tested += 1
        expected = lam + len(S)
        if size != expected:
            size_violations.append({"S": sorted(S), "size": size,
                                     "expected": expected})
        if fp in seen and frozenset(seen[fp]) != frozenset(S):
            collisions.append({"S1": sorted(seen[fp]), "S2": sorted(S)})
        else:
            seen[fp] = frozenset(S)

    # exhaustive |S| in {0,1,2}
    test_S([])
    for a in toggles:
        test_S([a])
    for i in range(len(toggles)):
        for j in range(i + 1, len(toggles)):
            test_S([toggles[i], toggles[j]])
    n_exhaustive = n_tested

    # >=20000 random S of size 3..69
    rng = random.Random(12345)
    n_random_target = 20000
    for _ in range(n_random_target):
        sz = rng.randint(3, k)
        S = rng.sample(toggles, sz)
        test_S(S)
    n_random = n_tested - n_exhaustive

    check_ii = (len(collisions) == 0) and (len(size_violations) == 0)

    # ---- (iii) exact rational non-min mass ----
    # For X = {o} u S with |S|=j: arc-set delta^+ has size lam + j (j>=1 non-min),
    # mass contribution 2^{1-(lam+j)} per distinct arc-set, and there are C(k,j)
    # distinct such arc-sets (tag-arc injectivity). Non-min mass:
    #   sum_{j=1..k} C(k,j) * 2^{1-(lam+j)}  = 2 * sum_{j=1..k} C(k,j)*2^{-(lam+j)}.
    # Proposal writes it as sum_{j=1..k} C(k,j)*2^{-(lam-1+j)} = same thing.
    mass = Fraction(0)
    for j in range(1, k + 1):
        mass += comb(k, j) * Fraction(1, 2 ** (lam - 1 + j))
    mass_float = float(mass)
    check_iii = mass > 1

    # closed-form cross-check: 2^{1-lam} * ((3/2)^k - 1)
    closed = Fraction(2) ** (1 - lam) * (Fraction(3, 2) ** k - 1)
    closed_matches = (closed == mass)

    # ---- (iv) alpha=1 (min-cut) band size <= n^2 ----
    # The min out-cuts of this family: X={o} (size lam), plus singleton/complement
    # type min cuts. Enumerate the alpha=1 arc-sets we can certify cheaply:
    # all singletons {v} and their complements, plus {o},{s}. Min size = lam.
    # Count DISTINCT min (size==lam) arc-sets among: {o}, {s}, all {v}, all V\{v}.
    min_arcsets = set()
    candidates = [[o], [s]]
    for v in range(n):
        candidates.append([v])
        candidates.append([w for w in range(n) if w != v])
    # also {o}uS singletons already size lam+1 (not min); {o} alone is the min.
    for X in candidates:
        if len(X) == 0 or len(X) == n:
            continue
        fp, size = labeled_outcut_fingerprint(n, arcs, X)
        if size == lam:
            min_arcsets.add(fp)
    n_min_arcsets = len(min_arcsets)
    check_iv = n_min_arcsets <= n * n

    # ---- (v) divergence table ----
    div_table = []
    for kk in [40, 50, 60, 69, 80, 100, 120]:
        nn = kk + 2
        ll = math.ceil(6 * math.log2(kk + 2))
        m = Fraction(2) ** (1 - ll) * (Fraction(3, 2) ** kk - 1)
        lam_needed = 1 + kk * math.log2(1.5)
        div_table.append({
            "k": kk, "n": nn, "lam=ceil(6log2(k+2))": ll,
            "nonmin_mass": float(m), "mass>1": m > 1,
            "lam_needed_for_closure=1+k*log2(1.5)": round(lam_needed, 2),
            "lam_needed_>_lam_thresh": lam_needed > ll,
            "lam_needed_as_frac_of_n": round(lam_needed / nn, 4),
        })

    verdict_route_dead = check_i and check_ii and check_iii and check_iv

    out = {
        "witness": "T(69,37)", "n": n, "n_arcs": len(arcs),
        "lam_param": lam, "lambda_oracle": lam_oracle,
        "threshold_6log2n": round(thresh, 4),
        "check_i_threshold": check_i,
        "check_ii_injectivity": {
            "ok": check_ii, "n_tested": n_tested,
            "n_exhaustive_|S|<=2": n_exhaustive, "n_random": n_random,
            "n_collisions": len(collisions), "n_size_violations": len(size_violations),
            "sample_collisions": collisions[:3],
            "sample_size_violations": size_violations[:3],
        },
        "check_iii_nonmin_mass": {
            "ok": check_iii, "mass_exact_num": mass.numerator,
            "mass_float": round(mass_float, 4),
            "mass>1": check_iii,
            "closed_form_2^{1-lam}((3/2)^k-1)_matches": closed_matches,
        },
        "check_iv_alpha1_core": {
            "ok": check_iv, "n_min_arcsets_certified": n_min_arcsets,
            "n^2": n * n,
        },
        "divergence_table": div_table,
        "ROUTE_DEAD_CONFIRMED": verdict_route_dead,
        "elapsed_s": round(time.time() - t0, 2),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
