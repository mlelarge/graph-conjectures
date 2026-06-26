import math

LOG2 = math.log(2.0)

def log2(x):
    return math.log(x) / LOG2

def S(n, C):
    """Sum over k of (#cuts of out-size k) * P(monochromatic).
    Eulerian: undirected cut size = 2k, lambda_G = 2*lambda_arc.
    Karger: #{X : |delta^+(X)| = k} <= n^{2k/lambda_arc} where lambda_arc >= C*log2 n.
    A monochromatic directed cut (all k arcs one colour) under uniform 2-colouring:
      prob = 2 * 2^{-k} = 2^{1-k}  (two colours).
    Per unordered bipartition there are TWO directed cuts (delta^+(X), delta^+(V\X));
    we keep a leading factor 'two_cuts' to absorb that (proposal caveat iii).
    Returns (S, S_doubled) in raw scale, computed in log-space for stability.
    """
    lam = max(1, math.ceil(C * log2(n)))
    a = 2.0 / lam  # exponent base: n^{2k/lam} = exp(k * a * ln n)
    ln_n = math.log(n)
    kmax = (n * n) // 4  # max possible out-cut size (loose upper bound)
    total = 0.0
    total_dbl = 0.0
    for k in range(lam, kmax + 1):
        # log of term: (2k/lam)*ln n + (1-k)*ln2
        log_term = (k * a) * ln_n + (1 - k) * LOG2
        if log_term < -80.0 and k > lam:
            # terms negligible and (since ratio<1) decreasing -> safe to break
            break
        t = math.exp(log_term)
        total += t
        total_dbl += 2.0 * t
    # geometric ratio of consecutive terms: n^{2/lam} / 2 = exp(a*ln n)/2
    ratio = math.exp(a * ln_n) / 2.0
    return total, total_dbl, lam, ratio

def find_n0(C, nmax):
    worst_n = None
    worst_S = -1.0
    worst_Sdbl = -1.0
    last_bad_single = 0
    last_bad_dbl = 0
    max_ratio = 0.0
    n = 3
    # sweep; for very large n the inner sum is cheap due to early break
    while n <= nmax:
        s, sd, lam, ratio = S(n, C)
        max_ratio = max(max_ratio, ratio)
        if s >= 1.0:
            last_bad_single = n
        if sd >= 1.0:
            last_bad_dbl = n
        if s > worst_S:
            worst_S = s; worst_n = n
        if sd > worst_Sdbl:
            worst_Sdbl = sd
        # coarse stepping once large to keep runtime bounded but still exact at sampled pts
        if n < 2000:
            n += 1
        elif n < 100000:
            n += 7
        else:
            n += 1009
    return {
        "C": C,
        "n0_single": last_bad_single + 1,   # smallest n with S(n)<1 for all >= this
        "n0_doubled": last_bad_dbl + 1,
        "worst_S_single": worst_S,
        "worst_S_doubled": worst_Sdbl,
        "max_geom_ratio": max_ratio,
    }

if __name__ == "__main__":
    for C in (3.0,):
        for nmax in (10**6,):
            r = find_n0(C, nmax)
            print(f"C={C}  nmax={nmax}")
            print(f"  n0 (single-cut sum  S<1 thereafter) = {r['n0_single']}")
            print(f"  n0 (doubled  2S<1 thereafter)        = {r['n0_doubled']}")
            print(f"  worst S(single) over sweep           = {r['worst_S_single']:.4f}")
            print(f"  worst S(doubled) over sweep          = {r['worst_S_doubled']:.4f}")
            print(f"  max geometric ratio n^(2/lam)/2      = {r['max_geom_ratio']:.6f}  (must be <1 for tail convergence)")
    # also report S at a few specific n for transparency
    print("--- per-n detail (C=3) ---")
    for n in [3,5,8,9,10,11,12,13,16,20,32,64,128,1000,10**6]:
        s, sd, lam, ratio = S(n, 3.0)
        print(f"  n={n:>7}  lam={lam:>3}  S={s:.5e}  2S={sd:.5e}  ratio={ratio:.5f}")
