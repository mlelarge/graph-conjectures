"""ECLOG C=3 HALF-INTEGRAL-form certifier (proposal Step 1, GROUNDING).

Computes EXACTLY the sum the proposal defines:
    H(n) = 2 * sum_{k=lam}^{K(n)} 2^{2*alpha_k} * C(n, 2*alpha_k) * 2^{1-k}
with
    alpha_k = ceil(2k/lam)/2,   lam = ceil(3 log2 n).
(The honest factor 2 = two directed cuts per bipartition. The Karger half-integral
per-size count is 2^{2 alpha} C(n, 2 alpha).)

It ALSO recomputes the existing geometric loose-alpha bound
    G(n) = head/(1-r),  head = 4 n^2 2^{-lam}, r = n^{2/lam}/2
(the form already in eclog_c3_shell_check.py) to cross-check the band.

We report, honestly, what is true vs what the proposal PREDICTED:
  prediction (a): H(n) < 1 for every n >= 17 in 17<=n<=5000, n_0* = 17, FAIL if n_0*>24
  prediction: H(n) <= c/n closed-form dominator for all n >= N.
"""
import math

LOG2 = math.log(2.0)
log2 = lambda x: math.log(x) / LOG2


def lam_of(n):
    return math.ceil(3 * math.log(n) / LOG2)


def comb(n, r):
    # exact integer binomial; r is an integer here (2*alpha_k is integer)
    return math.comb(n, r)


def H_halfintegral(n):
    """Exact half-integral-form first-moment sum H(n) as the proposal defines it."""
    lam = lam_of(n)
    tot = 0.0
    k = lam
    # alpha_k = ceil(2k/lam)/2 -> 2*alpha_k = ceil(2k/lam) =: s (an integer >= 2 since k>=lam)
    # the binomial C(n, s) is 0 once s > n; the directed-cut size k can in principle
    # run to ~n^2/4 but C(n, ceil(2k/lam)) vanishes for ceil(2k/lam) > n, i.e.
    # k > n*lam/2.  Cap there (terms are exactly 0 beyond).
    kmax = (n * lam) // 2 + 1
    while k <= kmax:
        s = math.ceil(2 * k / lam)          # = 2*alpha_k, integer
        if s > n:
            break                            # C(n,s)=0 for all larger k
        # term = 2^s * C(n,s) * 2^{1-k}; compute in natural-log space to avoid overflow
        log_term = s * LOG2 + math.lgamma(n + 1) - math.lgamma(s + 1) - math.lgamma(n - s + 1) + (1 - k) * LOG2
        tot += math.exp(log_term)
        k += 1
    return 2.0 * tot


def G_geom(n):
    lam = lam_of(n)
    head = 4 * n * n * 2.0 ** (-lam)
    r = (n ** (2.0 / lam)) / 2.0
    return head / (1 - r)


def main():
    # ---- (a) sweep 17..5000: H(n) < 1 ?  find first n_0* where it holds onward ----
    # SINGLE PASS: record all n in [17,5000] with H(n) >= 1.
    bad = []
    worst = -1.0; worst_n = None
    Hvals = {}
    for n in range(17, 5001):
        h = H_halfintegral(n)
        Hvals[n] = h
        if h > worst:
            worst = h; worst_n = n
        if h >= 1.0:
            bad.append(n)
    # honest n_0*: max(bad)+1 if bad nonempty (H<1 from there onward in swept range), else 17
    if bad:
        n0_star = max(bad) + 1
    else:
        n0_star = 17
    print(f"(a) H(n) half-integral sweep 17..5000:")
    print(f"    worst H = {worst:.5f} at n = {worst_n}")
    print(f"    # n with H(n) >= 1 : {len(bad)}  {'(first few: ' + str(bad[:12]) + ')' if bad else ''}")
    print(f"    honest n_0* (H<1 onward) = {n0_star}")

    # ---- explicit table at the claimed boundary ----
    print("    table:")
    for n in [17, 18, 19, 20, 21, 22, 23, 24, 25, 30, 40, 64, 100, 256, 1000]:
        print(f"      n={n:5d}  lam={lam_of(n):3d}  H={H_halfintegral(n):.5f}   G_geom={G_geom(n):.5f}")

    # ---- (iv) cross-check band H(n) vs the loose geometric G(n) ----
    band = [H_halfintegral(n) / G_geom(n) for n in [17, 20, 32, 64, 128, 256, 1024]]
    print(f"(iv) band H/G_geom over n in [17..1024]: [{min(band):.4f}, {max(band):.4f}]")
    print(f"     -> the doc's claim 'rounding only IMPROVES constants' (H <= G) is "
          f"{'TRUE' if max(band) <= 1.0 + 1e-9 else 'FALSE'} "
          f"(max ratio {max(band):.4f}).")

    # ---- verdict on the proposal's prediction (a) ----
    pred_a_ok = (not bad) or (n0_star <= 24)
    print()
    print(f"PREDICTION (a) [H(n)<1 for all n>=17, n_0* in [17,24]]: "
          f"{'CONFIRMED' if (not bad and n0_star == 17) else ('PARTIAL n_0*=%d' % n0_star if pred_a_ok else 'REFUTED')}")
    if bad:
        print(f"   NOTE: H(n) >= 1 occurs at n in {bad[:20]} -- the half-integral sum is NOT < 1 from 17 on.")


if __name__ == "__main__":
    main()
