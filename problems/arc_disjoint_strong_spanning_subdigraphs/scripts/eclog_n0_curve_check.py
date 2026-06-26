"""eclog_n0_curve_check.py -- EXACT-INTEGER certificate for the explicit-n_0(C)
COROLLARY of P1-ECLOG (standing target C in the round note).

For every fixed rational C = C_num / C_den > 2, the two-directed-cut first moment
is, with lambda(n) := ceil(C * log2 n) = min{L : 2^(L*C_den) >= n^C_num},

    G(n) = head / (1 - r),   head = 4 n^2 / 2^lambda,   r = n^(2/lambda) / 2.

The accepted D22 / D25 argument (docs/ECLOG_C3_SYMBOLIC_2026_06_12.md,
scripts/eclog_c3_exact_check.py) is the C=3 instance.  This script reproduces
that exact-arithmetic test for a *curve* of C values, with NO floating point in
any load-bearing comparison.

EXACT G<1 test (identical algebra to eclog_c3_exact_check, now with the general
lambda(n)): given 0 < r < 1,

    G(n) < 1
  <=> 4 n^2 / 2^lambda < 1 - n^(2/lambda)/2
  <=> n^(2/lambda) < 2 - 8 n^2 / 2^lambda = A / 2^lambda,  A := 2^(lambda+1) - 8 n^2
  <=> (A > 0 and, raising to the lambda-th power)  n^2 * (2^lambda)^lambda < A^lambda.

Pure bigint comparison.  G(n) >= 1 is its exact negation (A <= 0, OR the bigint
inequality fails).

n_0^crude(C): the accepted closed form from the D25 dominator
    G(n) <= 4 n^(2-C) / (1 - 2^(2/C - 1)),
i.e. n_0^crude(C) = ceil( (4 / (1 - 2^(2/C-1)))^(1/(C-2)) ), computed here by an
EXACT integer search (no float): the smallest n with 4 n^(2-C) < 1 - 2^(2/C-1),
bracketed rationally.  We need a SOUND (upper) rational bracket of 2^(2/C - 1)
to lower-bound (1 - 2^(2/C-1)); 2^(2/C-1) = 2^(2 C_den/C_num) / 2, and a sound
upper bracket is t/2 where t is the smallest integer with t^C_num >= 2^(2 C_den)
(the ceil C_num-th root of 2^(2 C_den)), so 2^(2/C) <= t and 2^(2/C-1) <= t/2.
The dominator inequality 4 n^(2-C) < 1 - t/2 (with 1 - t/2 > 0) in exact
integer form: 1 - t/2 > 0 <=> t < 2 (i.e. C > 2, the method's barrier); and
4 n^(C-2) ... -> n^(C_num-2 C_den) form below.

n_0^exact(C) <= n_0^crude(C): descend n from n_0^crude(C) and report the LEAST n
such that G(m) < 1 for every m in [n, n_0^crude(C)] (a contiguous tail).
"""
from __future__ import annotations
from fractions import Fraction


def ceil_root(value: int, k: int) -> int:
    """smallest integer t with t**k >= value  (value >= 0, k >= 1)."""
    if value <= 0:
        return 0
    # integer bisection for smallest t with t**k >= value (no float anywhere).
    lo, hi = 1, 1 << -(-(value.bit_length()) // k)   # hi = 2^ceil(bits/k) >= root
    while hi ** k < value:                            # safety widen (rare)
        hi <<= 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid ** k >= value:
            hi = mid
        else:
            lo = mid + 1
    return lo


def lam(n: int, c_num: int, c_den: int) -> int:
    """lambda(n) = ceil(C log2 n) = min{L : 2^(L*c_den) >= n**c_num}."""
    target = n ** c_num
    L = 1
    while (1 << (L * c_den)) < target:
        L += 1
    return L


def G_less_than_1_exact(n: int, c_num: int, c_den: int) -> bool:
    """Exact bigint test: G(n) < 1 with the general lambda(n)."""
    L = lam(n, c_num, c_den)
    A = (1 << (L + 1)) - 8 * n * n
    if A <= 0:
        return False                      # head alone >= 1
    # n^(2/L) < A / 2^L  <=>  n^2 * (2^L)^L < A^L
    return n * n * (1 << (L * L)) < A ** L


def upper_bracket_pow2(exp_num: int, exp_den: int, B: int = 64) -> Fraction:
    """SOUND rational upper bracket a/2^B >= 2^(exp_num/exp_den).
    Smallest a with (a/2^B)^exp_den >= 2^exp_num, i.e.
    a^exp_den >= 2^(exp_num + B*exp_den)  (exp_num may be negative)."""
    target = exp_num + B * exp_den          # = exp_num + B*exp_den
    if target < 0:
        # 2^(exp_num/exp_den) is tiny; a=1 with a^exp_den=1 >= 2^target (<1) ok
        return Fraction(1, 1 << B)
    a = ceil_root(1 << target, exp_den)     # a >= 2^((exp_num+B exp_den)/exp_den)
    return Fraction(a, 1 << B)              # = a/2^B >= 2^(exp_num/exp_den)


def n0_crude(c_num: int, c_den: int) -> int:
    """Smallest n with the accepted dominator 4 n^(2-C) < 1 - 2^(2/C-1),
    using a SOUND high-resolution upper bracket of 2^(2/C-1)."""
    # 2/C - 1 = (2 c_den - c_num)/c_num  (negative since C>2). Upper bracket:
    ub = upper_bracket_pow2(2 * c_den - c_num, c_num)   # >= 2^(2/C-1)
    denom = 1 - ub                                       # <= 1 - 2^(2/C-1)
    if denom <= 0:
        raise ValueError("dominator denominator non-positive: C<=2 barrier")
    # need 4 n^(2-C) < denom, i.e. 4 < denom * n^(C-2).  C-2=(c_num-2 c_den)/c_den.
    # raise to c_den: 4^c_den < denom^c_den * n^(c_num-2 c_den).  Fraction-exact.
    p = c_num - 2 * c_den                                # > 0 since C > 2
    lhs = Fraction(4 ** c_den)
    n = 1
    while not (lhs < (denom ** c_den) * (n ** p)):
        n += 1
    return n


def certify(c_num: int, c_den: int):
    crude = n0_crude(c_num, c_den)
    # descend, finding least n with G<1 contiguously up to crude
    n = crude
    while n >= 1 and G_less_than_1_exact(n, c_num, c_den):
        n -= 1
    exact = n + 1                                  # least n with G<1 on [exact, crude]
    # verify contiguity of the [exact, crude] block (every n has G<1)
    block_ok = all(G_less_than_1_exact(m, c_num, c_den) for m in range(exact, crude + 1))
    # boundary honesty: G(exact-1) >= 1
    boundary_ok = (exact == 1) or (not G_less_than_1_exact(exact - 1, c_num, c_den))
    # tail-handoff integer inequalities at crude: head<=4 n^(2-C) and r<=2^(2/C-1)
    L = lam(crude, c_num, c_den)
    head_ok = (1 << (L * c_den)) >= crude ** c_num         # 2^lam >= n^C  (head form)
    # RATIO tail inequality (prediction 2):  r = n^(2/L)/2 <= 2^(2/C - 1).
    #   Because lambda(n) = ceil(C log2 n) >= C log2 n, we have 2/L <= 2/(C log2 n)
    #   = (2/C)/log2 n, so n^(2/L) = 2^((2/L) log2 n) <= 2^(2/C), giving r <= 2^(2/C-1).
    #   Exact integer form:  n^(2/L) <= 2^(2/C)  <=>  (n^(2/L))^(L*C_num) <= (2^(2/C))^(L*C_num)
    #   <=> n^(2 C_num) <= 2^(2 L C_den).  Pure bigint.
    ratio_ok = crude ** (2 * c_num) <= (1 << (2 * L * c_den))
    # report r at crude via a SOUND high-resolution upper bracket of n^(2/L):
    # bracket n^(2/L) directly: smallest a with (a/2^B)^L >= n^2, so a/2^B >= n^(2/L).
    B = 64
    a = ceil_root(crude ** 2 << (B * L), L)        # a >= 2^B * n^(2/L)
    r_upper = Fraction(a, 1 << (B + 1))            # = (a/2^B)/2 >= n^(2/L)/2 = r
    head_val = Fraction(4 * crude * crude, 1 << L)
    G_upper = head_val / (1 - r_upper) if r_upper < 1 else None
    return {
        "C": f"{c_num}/{c_den}",
        "C_float": c_num / c_den,
        "n0_crude": crude,
        "n0_exact": exact,
        "lam_crude": L,
        "block_ok": block_ok,
        "boundary_ok": boundary_ok,
        "head_ok": head_ok,
        "ratio_ok": ratio_ok,
        "r_upper<1": r_upper < 1,
        "G_upper_at_crude": G_upper,
    }


def main():
    Cs = [(5, 2), (11, 4), (3, 1), (7, 2), (4, 1), (5, 1)]
    # (1) consistency anchor: n0_exact(3) must be exactly 17.
    anchor = certify(3, 1)
    assert anchor["n0_exact"] == 17, \
        f"ANCHOR FAIL: n0_exact(3) = {anchor['n0_exact']} != 17"
    assert lam(17, 3, 1) == 13, f"lam(17) = {lam(17,3,1)} != 13"
    assert G_less_than_1_exact(16, 3, 1) is False, "G(16)>=1 violated"
    print(f"ANCHOR ok: n0_exact(3)=17, lam(17)=13, G(16)>=1.\n")
    print(f"{'C':>6} {'n0_crude':>9} {'n0_exact':>9} {'lam_crd':>7} "
          f"{'block':>6} {'bndry':>6} {'head':>5} {'ratio':>6} {'G_up<1':>7}")
    all_pass = True
    rows = []
    for c_num, c_den in Cs:
        r = certify(c_num, c_den)
        rows.append(r)
        gpass = (r["G_upper_at_crude"] is not None) and (r["G_upper_at_crude"] < 1)
        ok = (r["block_ok"] and r["boundary_ok"] and r["head_ok"]
              and r["ratio_ok"] and gpass)
        all_pass = all_pass and ok
        print(f"{r['C']:>6} {r['n0_crude']:>9} {r['n0_exact']:>9} "
              f"{r['lam_crude']:>7} {str(r['block_ok']):>6} "
              f"{str(r['boundary_ok']):>6} {str(r['head_ok']):>5} "
              f"{str(r['ratio_ok']):>6} {str(gpass):>7}")
    print()
    for r in rows:
        print(f"C={r['C']:>5}: n0_exact={r['n0_exact']:>4}  "
              f"n0_crude={r['n0_crude']:>5}  G_upper(n0_crude)="
              f"{r['G_upper_at_crude']}")
    print(f"\nALL PASS: {all_pass}")
    if not all_pass:
        raise SystemExit("CURVE CERTIFICATE FAILED")


if __name__ == "__main__":
    main()
