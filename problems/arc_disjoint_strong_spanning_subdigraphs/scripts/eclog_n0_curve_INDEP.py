"""INDEPENDENT re-verification (from scratch) of the explicit-n_0(C) corollary
of P1-ECLOG.  Does NOT import or trust scripts/eclog_n0_curve_check.py.

Two INDEPENDENT pathways for the load-bearing predicate G(n) < 1, cross-checked:

  PATH A (bigint, raise-to-power):  G(n) < 1  with G = head/(1-r),
    head = 4 n^2 / 2^L,  r = n^(2/L)/2,  A := 2^(L+1) - 8 n^2 :
      need A > 0 and  n^(2/L) < A / 2^L  <=>  n^2 (2^L)^L < A^L.

  PATH B (exact Fraction with sound rational brackets of n^(2/L)):
    Let q = n^(2/L).  We bracket q exactly between rationals q_lo <= q <= q_hi
    (q_lo = (floor B-resolution root)/2^B, q_hi = (ceil root)/2^B).  Then
      G_hi = (4 n^2 / 2^L) / (1 - q_hi/2)   (an UPPER bound on G, valid if q_hi<2)
      G_lo = (4 n^2 / 2^L) / (1 - q_lo/2)   (a LOWER bound on G)
    so  G < 1  is CERTIFIED if G_hi < 1, and  G >= 1  is CERTIFIED if G_lo >= 1.
    With B large the bracket separates the two except on a measure-zero set;
    we assert PATH A and PATH B never contradict, and PATH B resolves every
    queried n (no straddle), which proves they compute the same predicate.

lambda(n) = ceil(C log2 n) = min{L : 2^(L c_den) >= n^c_num}, recomputed here.

n0_crude(C) = ceil((4/(1-2^(2/C-1)))^(1/(C-2))) via an independent exact search
using a sound UPPER bracket of 2^(2/C-1).
"""
from __future__ import annotations
from fractions import Fraction


# ---------- integer roots (independent bisection) ----------
def iroot_floor(value: int, k: int) -> int:
    """largest t with t**k <= value (value>=0,k>=1)."""
    if value < 0:
        raise ValueError
    if value == 0:
        return 0
    lo, hi = 0, 1
    while hi ** k <= value:
        hi <<= 1
    # now lo**k<=value<hi**k ... binary search for largest t with t**k<=value
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if mid ** k <= value:
            lo = mid
        else:
            hi = mid
    return lo


def iroot_ceil(value: int, k: int) -> int:
    """smallest t with t**k >= value."""
    if value <= 0:
        return 0
    f = iroot_floor(value, k)
    return f if f ** k == value else f + 1


# ---------- lambda(n) recomputed from scratch ----------
def lam(n: int, c_num: int, c_den: int) -> int:
    tgt = n ** c_num
    L = 1
    while (1 << (L * c_den)) < tgt:
        L += 1
    return L


# ---------- PATH A ----------
def G_lt1_A(n: int, c_num: int, c_den: int) -> bool:
    L = lam(n, c_num, c_den)
    A = (1 << (L + 1)) - 8 * n * n
    if A <= 0:
        return False
    return n * n * (1 << (L * L)) < A ** L


# ---------- PATH B (independent: exact Fraction brackets of n^(2/L)) ----------
def G_lt1_B(n: int, c_num: int, c_den: int, B: int = 256):
    """Return ('LT1'|'GE1'|'STRADDLE', G_hi, G_lo) certified independently."""
    L = lam(n, c_num, c_den)
    # q = n^(2/L); bracket q in [q_lo, q_hi] with q = ( n^2 )^(1/L).
    val = n ** 2
    # (a/2^B)^L >= val  <=> a^L >= val * 2^(B L). ceil root:
    a_hi = iroot_ceil(val << (B * L), L)      # a_hi/2^B >= q
    a_lo = iroot_floor(val << (B * L), L)     # a_lo/2^B <= q
    q_hi = Fraction(a_hi, 1 << B)
    q_lo = Fraction(a_lo, 1 << B)
    assert q_lo <= q_hi
    # sanity: q_lo^L <= val <= q_hi^L  (exact, via Fraction)
    assert q_lo ** L <= Fraction(val) <= q_hi ** L
    head = Fraction(4 * n * n, 1 << L)
    # G_hi uses the LARGER r (q_hi) -> larger G -> upper bound on G
    G_hi = head / (1 - q_hi / 2) if q_hi < 2 else None
    G_lo = head / (1 - q_lo / 2) if q_lo < 2 else None
    if G_hi is not None and G_hi < 1:
        verdict = "LT1"
    elif (q_lo >= 2) or (G_lo is not None and G_lo >= 1):
        verdict = "GE1"
    else:
        verdict = "STRADDLE"
    return verdict, G_hi, G_lo


def cross_check_predicate(n, c_num, c_den):
    a = G_lt1_A(n, c_num, c_den)
    v, g_hi, g_lo = G_lt1_B(n, c_num, c_den)
    if v == "STRADDLE":
        raise AssertionError(f"PATH B straddled at n={n}, C={c_num}/{c_den}")
    b = (v == "LT1")
    if a != b:
        raise AssertionError(
            f"PATH A/B DISAGREE at n={n} C={c_num}/{c_den}: A={a} B={v} "
            f"G_hi={g_hi} G_lo={g_lo}")
    return a


# ---------- n0_crude (independent exact search) ----------
def upper_bracket_2_pow(num: int, den: int, B: int = 256) -> Fraction:
    """sound rational UPPER bracket of 2^(num/den)."""
    e = num + B * den
    if e < 0:
        return Fraction(1, 1 << B)
    a = iroot_ceil(1 << e, den)        # a >= 2^((num+B den)/den)
    return Fraction(a, 1 << B)


def n0_crude(c_num: int, c_den: int) -> int:
    # 2^(2/C - 1) = 2^((2 c_den - c_num)/c_num).  upper bracket:
    ub = upper_bracket_2_pow(2 * c_den - c_num, c_num)
    denom = 1 - ub                      # <= 1 - 2^(2/C-1)
    if denom <= 0:
        raise ValueError("C<=2 barrier")
    # need 4 n^(2-C) < denom  <=>  4 < denom * n^(C-2);  C-2=(c_num-2c_den)/c_den
    p = c_num - 2 * c_den
    lhs = Fraction(4 ** c_den)
    n = 1
    while not (lhs < (denom ** c_den) * Fraction(n ** p)):
        n += 1
    return n


def certify(c_num, c_den):
    crude = n0_crude(c_num, c_den)
    # descend using the CROSS-CHECKED predicate
    n = crude
    while n >= 1 and cross_check_predicate(n, c_num, c_den):
        n -= 1
    exact = n + 1
    block_ok = all(cross_check_predicate(m, c_num, c_den)
                   for m in range(exact, crude + 1))
    boundary_ok = (exact == 1) or (not cross_check_predicate(exact - 1, c_num, c_den))
    L = lam(crude, c_num, c_den)
    head_ok = (1 << (L * c_den)) >= crude ** c_num
    ratio_ok = crude ** (2 * c_num) <= (1 << (2 * L * c_den))
    v, g_hi, g_lo = G_lt1_B(crude, c_num, c_den)
    return dict(C=f"{c_num}/{c_den}", crude=crude, exact=exact, L=L,
                block_ok=block_ok, boundary_ok=boundary_ok,
                head_ok=head_ok, ratio_ok=ratio_ok, G_hi=g_hi,
                G_hi_lt1=(g_hi is not None and g_hi < 1))


def main():
    Cs = [(5, 2), (11, 4), (3, 1), (7, 2), (4, 1), (5, 1)]

    # --- ANCHOR (independent): the C=3 D22 facts ---
    assert lam(17, 3, 1) == 13, lam(17, 3, 1)
    assert lam(16, 3, 1) == 12, lam(16, 3, 1)
    # G(17)<1, G(16)>=1, G(15)>=1 -- the proved tightness anchor
    assert cross_check_predicate(17, 3, 1) is True, "G(17)<1 failed"
    assert cross_check_predicate(16, 3, 1) is False, "G(16)>=1 violated"
    assert cross_check_predicate(15, 3, 1) is False, "G(15)>=1 violated"
    a3 = certify(3, 1)
    assert a3["exact"] == 17, a3["exact"]
    print(f"ANCHOR ok: n0_exact(3)=17, lam(17)=13, G(15)>=1, G(16)>=1, G(17)<1.\n")

    print(f"{'C':>6} {'crude':>6} {'exact':>6} {'L':>4} {'blk':>5} "
          f"{'bnd':>5} {'head':>5} {'ratio':>6} {'Ghi<1':>6}")
    all_pass = True
    rows = []
    for cn, cd in Cs:
        r = certify(cn, cd)
        rows.append(r)
        ok = (r["block_ok"] and r["boundary_ok"] and r["head_ok"]
              and r["ratio_ok"] and r["G_hi_lt1"])
        all_pass = all_pass and ok
        print(f"{r['C']:>6} {r['crude']:>6} {r['exact']:>6} {r['L']:>4} "
              f"{str(r['block_ok']):>5} {str(r['boundary_ok']):>5} "
              f"{str(r['head_ok']):>5} {str(r['ratio_ok']):>6} "
              f"{str(r['G_hi_lt1']):>6}")
    print()
    for r in rows:
        print(f"C={r['C']:>5}: exact={r['exact']:>4} crude={r['crude']:>5} "
              f"G_upper(crude)={r['G_hi']}")
    print(f"\nALL PASS (independent): {all_pass}")
    if not all_pass:
        raise SystemExit("INDEPENDENT CURVE CERTIFICATE FAILED")


if __name__ == "__main__":
    main()
