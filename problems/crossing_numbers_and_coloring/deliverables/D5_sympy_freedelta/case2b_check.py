"""
case2b_check.py
================

D5 / D8 silently assumed FPS's monotonicity-in-eta claim for Case 2b holds
at *every* delta, not only at delta = 9/8 where FPS prove it.

This script tests that assumption directly:

  For each delta in a scan,
    - compute df_2b/d eta(eta = 1/2);
    - if it is non-negative, f_2b is NOT maximised at eta = 1/2,
      so f_2b^max(delta) > delta/2 and the D8 chain breaks.

  Then numerically maximise f_2b(eta) over the full Case 2b interval
  [1/2, eta_b(delta)) and report the true f_2b^max(delta).

  Combine with f_1(delta) = delta/2 and f_2a^max(delta) (closed-form)
  to compute the true F(delta) = max of the three.

  Report whether any admissible delta in (1, 5/4) gives F(delta) < 9/16.

If the verdict is "no improvement", the D8 paper claim is invalid and
must be retracted.
"""

import sympy as sp
import math

delta_s, eta_s = sp.symbols('delta eta', real=True, positive=True)

# Case 2b: alpha = beta = 2 - 1/eta, gamma = eta*alpha + (1-eta)*delta
alpha_2b = 2 - 1/eta_s
gamma_2b = eta_s * alpha_2b + (1 - eta_s) * delta_s  # = 2*eta - 1 + (1-eta)*delta
f_2b_sym = gamma_2b - alpha_2b * (delta_s - 1) / (delta_s - gamma_2b)
f_2b_sym = sp.simplify(f_2b_sym)

print('f_2b(eta, delta) =', f_2b_sym)
print()

# df_2b / d eta
df2b = sp.simplify(sp.diff(f_2b_sym, eta_s))
print('df_2b/d eta =', df2b)
print()

# Evaluate df_2b/d eta at eta = 1/2 as a function of delta.
df2b_at_half = sp.simplify(df2b.subs(eta_s, sp.Rational(1, 2)))
print('df_2b/d eta at eta = 1/2  =', df2b_at_half)
print()

# Factor it
df2b_at_half_factored = sp.factor(df2b_at_half)
print('factored:', df2b_at_half_factored)
print()

# Find roots of df_2b/d eta at eta = 1/2 in delta
roots = sp.solve(df2b_at_half, delta_s)
print('delta values where df_2b/d eta (eta=1/2) = 0:')
for r in roots:
    rn = complex(r.evalf())
    if abs(rn.imag) < 1e-12:
        print(f'    delta = {r}   ~= {rn.real}')
print()

# The critical delta where Case 2b monotonicity at eta=1/2 transitions
print('delta_crit = -3 + sqrt(17) =', float(sp.sqrt(17) - 3))
print('9/8 =', 9/8)
print()

# Numerical scan of true f_2b^max(delta) and F(delta).
# Pure float for speed; use scipy.optimize-like 1D maximisation by golden section.

def alpha_v(eta, delta): return 2 - 1/eta
def gamma_v(eta, delta): return eta * alpha_v(eta, delta) + (1 - eta) * delta

def f_2b(eta, delta):
    g = gamma_v(eta, delta)
    return g - alpha_v(eta, delta) * (delta - 1) / (delta - g)

def eta_b(delta):
    return (math.sqrt(delta * (delta - 1)) - 1) / (delta - 2)

def f_2a_max(delta):
    # closed form derived in D5; equivalent to delta - 2*sqrt(d(d-1)) + (d-1)/eta_b
    return delta - 2 * math.sqrt(delta * (delta - 1)) + (delta - 1) / eta_b(delta)

def f_1(delta):
    return delta / 2

def maximise_f2b(delta, n=4001):
    """Brute-force 1D scan of f_2b(eta, delta) on [0.5, eta_b(delta) - 1e-5]."""
    lo = 0.5
    hi = eta_b(delta) - 1e-6
    if hi <= lo:
        return float('nan'), float('nan')
    best_eta, best_f = lo, f_2b(lo, delta)
    for i in range(1, n):
        eta = lo + (hi - lo) * i / (n - 1)
        try:
            v = f_2b(eta, delta)
            if v > best_f:
                best_f = v
                best_eta = eta
        except Exception:
            pass
    return best_eta, best_f

print()
print('Numerical scan over delta in (1, 5/4):')
print(f"{'delta':>10}  {'f_1':>10}  {'f_2a':>10}  {'f_2b(eta=1/2)':>14}  "
      f"{'f_2b_max':>10}  {'argmax_eta':>10}  {'F':>10}")

best_F = float('inf')
best_delta = None
for delta in [1.005, 1.01, 1.02, 1.05, 1.08, 1.10,
              1.114907541476756,           # D5's delta_1
              1.115, 1.118, 1.120,
              1.123, 1.1231, -3 + math.sqrt(17),  # delta_crit
              1.124, 1.1245, 1.125,        # 9/8
              1.13, 1.14, 1.15, 1.20, 1.24]:
    f1v = f_1(delta)
    f2av = f_2a_max(delta)
    f2b_at_half = f_2b(0.5 + 1e-9, delta)  # avoid division by zero
    eta_max, f2b_max = maximise_f2b(delta)
    F = max(f1v, f2av, f2b_max)
    if F < best_F:
        best_F = F
        best_delta = delta
    print(f"{delta:>10.6f}  {f1v:>10.6f}  {f2av:>10.6f}  {f2b_at_half:>14.6f}  "
          f"{f2b_max:>10.6f}  {eta_max:>10.6f}  {F:>10.6f}")

print()
print(f'BEST delta found: {best_delta}')
print(f'BEST F value    : {best_F}')
print(f'9/16            : {9/16}')
print()
if best_F < 9/16 - 1e-6:
    print('*** Improvement EXISTS at the reported delta ***')
elif abs(best_F - 9/16) < 1e-6:
    print('*** No improvement: FPS choice 9/8 is optimal (tied within tolerance) ***')
else:
    print(f'*** No improvement: FPS 9/16 = {9/16} is strictly smaller than best F = {best_F} ***')
