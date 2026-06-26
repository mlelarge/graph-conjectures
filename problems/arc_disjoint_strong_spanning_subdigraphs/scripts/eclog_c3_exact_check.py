"""eclog_c3_exact_check.py -- EXACT-INTEGER certificate for Theorem ECLOG-3
(docs/ECLOG_C3_SYMBOLIC_2026_06_12.md), supplying the exact-arithmetic
verification the D22 promotion advertised but did not check in (D25 review,
finding 4).  No floating point anywhere; every inequality is an integer
comparison.

The theorem needs exactly these finitely many facts beyond the symbolic
Sections 1-6 (all with lam := lam_min(n) = min{L : 2^L >= n^3}, the worst
case since head and ratio both decrease in lam):

  (T1) head bound  : 2^lam >= n^3                  [definition of lam_min]
  (T2) ratio bound : n^6 <= 2^(2 lam)              [follows from (T1) squared]
  (T3) dominator   : G(n) <= (4/n)/(1 - 2^(-1/3)) < 1 for n >= 20
                     <=> 4/(1 - 2^(-1/3)) < 20 <=> 2^(-1/3) < 4/5
                     <=> (cube) 1/2 < 64/125.      [single integer fact]
  (T4) residuals   : G(n) < 1 at n = 17, 18, 19
                     <=> n^2 * 2^(lam^2) < (2^(lam+1) - 8 n^2)^lam ... see below
  (T5) tightness   : G(16) >= 1 (the argument FAILS at n = 16).

(T4)/(T5) derivation: G(n) = (4 n^2 2^-lam) / (1 - n^(2/lam)/2) and, given
0 < r < 1, G(n) < 1  <=>  n^(2/lam) < 2 - 8 n^2 / 2^lam = A / 2^lam with
A := 2^(lam+1) - 8 n^2 > 0  <=>  (raise to the lam-th power, both sides > 0)
n^2 * (2^lam)^lam < A^lam.  Pure bigint comparison.
"""
from __future__ import annotations


def lam_min(n: int) -> int:
    L = 1
    while (1 << L) < n ** 3:
        L += 1
    return L


def G_less_than_1_exact(n: int) -> bool:
    lam = lam_min(n)
    A = (1 << (lam + 1)) - 8 * n * n
    if A <= 0:
        return False                      # head alone >= 1 (r-test moot)
    return n * n * (1 << (lam * lam)) < A ** lam


def main():
    # (T1)+(T2): definitional for lam_min; assert for the residual sizes.
    for n in (16, 17, 18, 19, 20):
        lam = lam_min(n)
        assert (1 << lam) >= n ** 3                       # T1
        assert n ** 6 <= (1 << (2 * lam))                 # T2
    # (T3): the n>=20 dominator reduces to one cube comparison.
    assert 1 * 125 < 64 * 2, "cube check 1/2 < 64/125 failed"  # 125 < 128
    # (T4): residual sizes pass.
    for n in (17, 18, 19):
        assert G_less_than_1_exact(n), f"G({n}) < 1 FAILED"
    # (T5): tightness -- the argument must FAIL at n = 16.
    assert not G_less_than_1_exact(16), "G(16) < 1 unexpectedly holds"
    # monotonicity sanity at the boundary: larger lam only helps.
    for n in (17, 18, 19):
        lam = lam_min(n) + 1
        A = (1 << (lam + 1)) - 8 * n * n
        assert A > 0 and n * n * (1 << (lam * lam)) < A ** lam
    print("lam_min: 16->%d 17->%d 18->%d 19->%d" % tuple(
        lam_min(n) for n in (16, 17, 18, 19)))
    print("EXACT certificate: T1,T2 (head/ratio), T3 (n>=20 dominator, "
          "125<128), T4 (G<1 at 17,18,19), T5 (G(16)>=1): ALL PASS")


if __name__ == "__main__":
    main()
