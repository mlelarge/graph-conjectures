"""eclog_explicit_n0.py -- EXACT-INTEGER explicit-n0(C) certificate for the
P1-ECLOG corollary (ledger standing target (C); D25 'every fixed C>2'):

  For every fixed rational C=p/q>2, lambda >= C log2 n suffices for n >= n0(C),
  with G(n) <= 4 n^{2-C} / (1 - rho) -> 0, rho a rational upper bound on
  2^{(2q-p)/p} = 2^{2/C - 1} < 1.

Modelled line-for-line on scripts/eclog_c3_exact_check.py.  No floating point;
every inequality is a big-integer comparison.

Per-size criterion (C-independent given lam): with
    lam_C(n) = min{ L : 2^{Lq} >= n^p }   ( = ceil(C log2 n) ),
the two-directed-cut first moment G(n) = (4 n^2 2^{-lam}) / (1 - n^{2/lam}/2)
satisfies  G(n) < 1  iff  A := 2^{lam+1} - 8 n^2 > 0  and
    n^2 * (2^{lam})^{lam} < A^{lam}            (pure bigint, the same reduction
as eclog_c3_exact_check.G_less_than_1_exact, just with lam = lam_C(n)).

NB: this per-n test is NOT monotone in n inside a fixed-lam block (it can pass
at the small-n end where lam just bumped, fail near the large-n end before the
next bump).  So the honest onset is
    n0(C) = 1 + max{ n in [4, Nmax] : test(n) is False }
i.e. the least n past which the test holds for ALL m in [n, Nmax].  Tightness:
test FAILS at n0-1 by construction.  The tail n > Nmax is closed symbolically.
"""
from __future__ import annotations

NMAX = 8192
C_GRID = [(29, 10), (11, 4), (5, 2)]   # 2.9, 2.75, 2.5


def lam_C(n: int, p: int, q: int) -> int:
    """min{L : 2^{Lq} >= n^p} = ceil(C log2 n)."""
    L = 1
    npow = n ** p
    while (1 << (L * q)) < npow:
        L += 1
    return L


def G_less_than_1_exact(n: int, lam: int) -> bool:
    """G(n) < 1 by the geometric-form bigint test (C-independent given lam)."""
    A = (1 << (lam + 1)) - 8 * n * n
    if A <= 0:
        return False                       # head alone >= 1
    return n * n * (1 << (lam * lam)) < A ** lam


def onset(p: int, q: int, nmax: int) -> tuple[int, int | None]:
    """(n0, last_fail) over [4, nmax]; n0 = 1 + last failing n."""
    last_fail = None
    for n in range(4, nmax + 1):
        if not G_less_than_1_exact(n, lam_C(n, p, q)):
            last_fail = n
    n0 = (last_fail + 1) if last_fail is not None else 4
    return n0, last_fail


def best_rho(p: int, q: int):
    """Rational rho = a/b < 1, a,b small, with rho >= 2^{(2q-p)/p}, i.e.
       a^p * 2^{p-2q} >= b^p   (2q-p < 0 for C>2).  Returns (a, b)."""
    assert p > 2 * q, "need C > 2 for rho < 1"
    # scan denominators; want the tightest (smallest) valid rho for a good n0.
    best = None
    for b in range(2, 200):
        for a in range(1, b):           # a/b < 1
            if a ** p * (1 << (p - 2 * q)) >= b ** p:
                if best is None or a * best[1] < best[0] * b:  # a/b < best
                    best = (a, b)
            # a increases -> rho increases, only need the smallest valid a
    return best


def main():
    summary = []
    for (p, q) in C_GRID:
        C = f"{p}/{q}"
        # (i) onset + tightness over [4, NMAX].
        n0, last_fail = onset(p, q, NMAX)
        lam0 = lam_C(n0, p, q)
        # block-passing: test true for all m in [n0, NMAX].
        assert all(G_less_than_1_exact(m, lam_C(m, p, q))
                   for m in range(n0, NMAX + 1)), f"C={C}: block has a failure"
        # tightness: FAILS at n0-1.
        assert not G_less_than_1_exact(n0 - 1, lam_C(n0 - 1, p, q)), \
            f"C={C}: test unexpectedly passes at n0-1={n0-1}"

        # (ii) symbolic tail n > NMAX via the dominator G(n) <= 4 n^{2-C}/(1-rho).
        a, b = best_rho(p, q)            # rho = a/b in [2^{2/C-1}, 1)
        assert a ** p * (1 << (p - 2 * q)) >= b ** p, "rho lower-bound check"
        assert a < b, "rho must be < 1"
        # The dominator 4 n^{2-C}/(1-rho) is < 1 once 4 n^{2-C} < 1 - rho,
        # i.e. 4 (b) < (b-a) n^{C-2} = (b-a) n^{(p-2q)/q}.  Raise to power q:
        #   (4 b)^q < (b-a)^q * n^{p-2q}.   Monotone increasing in n (p>2q),
        # so it suffices to check at n = NMAX+1 (then holds for all larger n).
        Nt = NMAX + 1
        lhs = (4 * b) ** q
        rhs = (b - a) ** q * Nt ** (p - 2 * q)
        assert lhs < rhs, f"C={C}: tail dominator fails at n={Nt}"
        # also confirm the per-n test itself holds at the seam n=NMAX+1
        assert G_less_than_1_exact(Nt, lam_C(Nt, p, q)), f"C={C}: seam test"

        # (iii) closed-form CRUDE bound, valid for every rational C>2:
        #   n0_crude(C) = ceil( (4/(1-rho))^{q/(p-2q)} )  (4 n^{2-C} < 1-rho).
        #   integer form: least N with (b-a)^q * N^{p-2q} >= (4 b)^q.
        num = (4 * b) ** q
        N = 1
        while (b - a) ** q * N ** (p - 2 * q) < num:
            N += 1
        n0_crude = N
        assert (b - a) ** q * n0_crude ** (p - 2 * q) >= num
        assert (b - a) ** q * (n0_crude - 1) ** (p - 2 * q) < num

        summary.append((C, n0, lam0, last_fail, (a, b), n0_crude))
        print(f"C={C}={p/q:.4f}: n0={n0} (lam_C(n0)={lam0}), "
              f"FAILS at n0-1={n0-1}; rho={a}/{b}; "
              f"tail-dominator<1 for n>={Nt}; n0_crude={n0_crude}")

    # (iv) closed-form crude n0 for a C where a [4,8192] scan is infeasible:
    #      C=21/10=2.1 (n0 ~ 1e21), one bigint check, no scan.
    p, q = 21, 10
    a, b = best_rho(p, q)
    num = (4 * b) ** q
    # solve least N with (b-a)^q N^{p-2q} >= num by integer bisection.
    lo, hi = 1, 1
    while (b - a) ** q * hi ** (p - 2 * q) < num:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if (b - a) ** q * mid ** (p - 2 * q) >= num:
            hi = mid
        else:
            lo = mid + 1
    n0_crude_21 = lo
    assert (b - a) ** q * n0_crude_21 ** (p - 2 * q) >= num
    assert (b - a) ** q * (n0_crude_21 - 1) ** (p - 2 * q) < num
    print(f"C=21/10=2.1 (scan infeasible): rho={a}/{b}, "
          f"closed-form n0_crude={n0_crude_21} (~{float(n0_crude_21):.3e}); "
          f"one bigint check, no scan")

    print("\nALL exact certificates PASS.")
    return summary


if __name__ == "__main__":
    main()
