"""ECLOG C=3 shell certifier (G10-salvage Step 2), with HONEST corrections.

The proposal's closed-form bound
    B(n) = 4 n^2 2^{-lam} + 4 (n^2)^{1-e} / (e-1),   lam = ceil(3 log2 n), e = lam/(2 log2 n)
is checked, but it is ALSO compared against the exact two-directed-cut Karger
first-moment sum
    2S(n) = 4 * sum_{k >= lam} n^{2k/lam} 2^{-k}
and against its EXACT geometric closed form
    G(n) = head / (1 - r),   head = 4 n^2 2^{-lam},  r = n^{2/lam} / 2  (< 1).

FINDINGS asserted here:
  (A) B(n) is NOT an upper bound on the true expectation: B(n) ~ 0.61 * 2S(n).
      So a proof that uses B(n) as the first-moment bound is WRONG; the correct
      certifiable bound is the geometric closed form G(n) = head/(1-r) = 2S(n).
  (B) G(n) < 1 for ALL n >= 17  (worst 0.9423 at n=20)  -> theorem holds, n_0 = 17.
  (C) G(n) >= 1 somewhere in [13,17): G(16) = 1.2118 -> n_0 = 13 is FALSE
      (this is the same too-small-n_0 error class that graveyarded G10).
  (D) symbolic tail domination: r = n^{2/lam}/2 <= 2^{-1/3} < 1 exactly for the
      "flat" n (when lam = 3 log2 n), giving the convergent geometric tail.

So the SCIENTIFIC theorem (threshold 3 log2 n, n_0 = 17) is certified by G(n),
NOT by the proposal's B(n); the proposal's B(n)<1-for-n>=17 holds only
coincidentally and its n_0 = 13 claim is refuted.
"""
import math
import numpy as np

log2 = lambda x: np.log(x) / np.log(2.0)
LOG2 = math.log(2.0)


def lam_of(n):
    return math.ceil(3 * math.log(n) / LOG2)


def B_scalar(n):
    lam = lam_of(n)
    e = lam / (2 * math.log(n) / LOG2)
    return 4 * n * n * 2.0 ** (-lam) + 4 * (n * n) ** (1 - e) / (e - 1)


def G_scalar(n):
    """Exact geometric closed form of the honest two-cut first-moment sum."""
    lam = lam_of(n)
    head = 4 * n * n * 2.0 ** (-lam)
    r = (n ** (2.0 / lam)) / 2.0
    return head / (1 - r)


def exact_2S(n):
    lam = lam_of(n)
    a = 2.0 / lam
    ln_n = math.log(n)
    kmax = (n * n) // 4
    tot = 0.0
    for k in range(lam, kmax + 1):
        lt = (k * a) * ln_n + (1 - k) * LOG2
        if lt < -80 and k > lam:
            break
        tot += math.exp(lt)
    return 2.0 * tot


def main():
    # --- (A) B(n) under-counts the true expectation (NOT an upper bound) ---
    ratios = []
    for n in [13, 17, 18, 19, 20, 24, 32, 64, 128, 256, 1024, 4096]:
        ratios.append(exact_2S(n) / B_scalar(n))
    minr, maxr = min(ratios), max(ratios)
    assert minr > 1.0, f"B(n) claimed >= 2S(n) but min ratio {minr} <= 1"
    print(f"(A) PASS: B(n) UNDER-counts true 2S(n); ratio 2S/B in [{minr:.3f}, {maxr:.3f}] (>1 => B is NOT a valid upper bound).")

    # --- B == G consistency (B is the geometric form with one extra slack term?) ---
    # Confirm the EXACT geometric form equals the exact sum.
    for n in [17, 20, 32, 64, 128, 256]:
        assert abs(G_scalar(n) - exact_2S(n)) < 1e-6 * max(1, exact_2S(n)), (n, G_scalar(n), exact_2S(n))
    print("    (G(n) = head/(1-r) reproduces the exact two-cut Karger sum 2S(n).)")

    # --- (B) honest bound G(n) < 1 for all 17 <= n <= 2^20 (vectorized-equivalent sweep) ---
    worst = -1.0; worstn = None; bad = []
    head_dom_ok = True; rmax = 0.0
    for n in range(17, 2 ** 20 + 1):
        g = G_scalar(n)
        if g > worst:
            worst = g; worstn = n
        if g >= 1.0:
            bad.append(n)
        lam = lam_of(n)
        head = 4 * n * n * 2.0 ** (-lam)
        r = (n ** (2.0 / lam)) / 2.0
        if head > 4.0 / n + 1e-12:        # head = 4 n^2 2^{-lam} <= 4 n^2 n^{-3} = 4/n
            head_dom_ok = False
        rmax = max(rmax, r)
    assert not bad, f"G(n) >= 1 at n>=17: {bad[:10]}"
    assert worst < 1.0
    print(f"(B) PASS: honest bound G(n) < 1 for ALL 17 <= n <= 2^20 (worst {worst:.5f} at n={worstn}); 0 kills => theorem holds with n_0 = 17.")

    # --- (D) HONEST symbolic dominator (replaces the proposal's wrong head<=4/n & tail<=8/n=>12/n) ---
    # head <= 4/n exactly (n^{-lam} <= n^{-3}); r <= 2^{-1/3} exactly (lam >= 3 log2 n).
    # => G(n) = head/(1-r) <= (4/n)/(1 - 2^{-1/3}) = (4/(1-2^{-1/3}))/n = 19.39.../n,
    #    which is < 1 for n >= 20; n in {17,18,19} discharged by direct evaluation above.
    assert head_dom_ok, "head <= 4/n dominator failed"
    assert rmax <= 2.0 ** (-1.0 / 3) + 1e-12, f"r exceeded 2^(-1/3): {rmax}"
    Csym = 4.0 / (1 - 2.0 ** (-1.0 / 3))
    assert Csym / 20.0 < 1.0 and Csym / 19.0 > 1.0, Csym  # threshold is n>=20 for the one-liner
    for n in (17, 18, 19):
        assert G_scalar(n) < 1.0
    print(f"    (D) PASS: HONEST symbolic dominator G(n) <= {Csym:.3f}/n (head<=4/n, r<=2^(-1/3)) => G<1 for n>=20; n=17,18,19 by direct eval.")

    # --- (C) n_0 = 13 is FALSE: G(n) >= 1 somewhere in [13,17) ---
    bad_low = [n for n in range(13, 17) if G_scalar(n) >= 1.0]
    assert bad_low, "expected G(n) >= 1 in [13,17) to refute n_0=13"
    print(f"(C) PASS: n_0 = 13 REFUTED -- honest bound G(n) >= 1 at n in {bad_low} (G(16) = {G_scalar(16):.4f}); honest n_0 = 17.")

    # --- G10 consistency: at n=10 even the under-counting B already fails ---
    assert B_scalar(10) >= 1.0, f"expected B(10)>=1, got {B_scalar(10)}"
    print(f"    (G10 consistency: B(10) = {B_scalar(10):.4f} >= 1, B(13) = {B_scalar(13):.4f}, B(17) = {B_scalar(17):.4f}.)")

    # --- ratio bound: r <= 2^{-1/3} on flat n where lam = 3 log2 n exactly ---
    # n = 2^(j) gives lam = 3j, r = (2^j)^{2/(3j)}/2 = 2^{2/3}/2 = 2^{-1/3}.
    for j in [4, 5, 6, 7, 8, 10, 15, 20]:
        n = 2 ** j
        lam = lam_of(n); r = (n ** (2.0 / lam)) / 2.0
        assert abs(r - 2 ** (-1.0 / 3)) < 1e-12, (n, r)
    print(f"    tail ratio on powers of two: r = 2^(-1/3) = {2**(-1/3):.5f} exactly (geometric tail convergent).")

    print("\nCERTIFIER VERDICT: theorem 'Eulerian + lambda >= 3 log2 n => SAD for n >= 17' "
          "is arithmetically certified by the HONEST geometric bound G(n)=head/(1-r); "
          "the proposal's B(n) is an under-count (invalid as the first-moment bound) and "
          "its n_0=13 claim is FALSE (true n_0 = 17, matching the salvaged P1.round1_note).")


if __name__ == "__main__":
    main()
