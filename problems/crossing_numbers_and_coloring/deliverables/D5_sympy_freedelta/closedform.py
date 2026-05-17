"""
D5b — Try to extract a closed form for the optimal delta and the resulting
constant.

From freedelta.py we know:
  - F(delta) = max(delta/2, f_2a(delta))  (since f_2b(delta) = delta/2)
  - The minimum is at the smallest root of delta/2 = f_2a(delta).
  - Numerically: delta* ~ 1.1149075415, F* ~ 0.5574537707.
  - The cubic-like resultant has three real roots in [1, 2]: ~1.1149, 4/3,
    and phi = (1+sqrt(5))/2 ~ 1.6180.

Goal: identify the closed form of the smallest root.
"""

import sympy as sp

delta = sp.symbols('delta', real=True, positive=True)

# Use the closed form from freedelta.py for f_2a at the boundary eta_b(delta).
# Rebuild from scratch.
alpha, eta = sp.symbols('alpha eta', real=True, positive=True)
f_raw = sp.symbols('f_raw', cls=sp.Function)(alpha, eta, delta)  # not used directly
gamma_case2 = eta * alpha + (1 - eta) * delta
f_case2 = (gamma_case2) - alpha * (delta - 1) / (delta - gamma_case2)
alpha_star = delta - sp.sqrt(delta) * sp.sqrt(delta - 1) / eta
eta_b = (sp.sqrt(delta) * sp.sqrt(delta - 1) - 1) / (delta - 2)

f_2a_at_eta_b = sp.simplify(f_case2.subs(alpha, alpha_star).subs(eta, eta_b))

# Equation: delta/2 = f_2a(delta)
eq = sp.Eq(delta / 2, f_2a_at_eta_b)
print(f'Equation:  {eq}')

# Rationalise: multiply by denominators, clear sqrt's by substitution.
# Let s = sqrt(delta), t = sqrt(delta - 1).  Then s^2 - t^2 = 1.
s, t = sp.symbols('s t', real=True, positive=True)
sub = {sp.sqrt(delta): s, sp.sqrt(delta - 1): t}
# Replace delta in numerator using s^2.
expr_lhs = (delta / 2).subs(delta, s**2).subs(sub)
expr_rhs = f_2a_at_eta_b.subs(delta, s**2).subs(sub)
eq_st = sp.Eq(expr_lhs, expr_rhs)
print(f'In (s, t):  {sp.simplify(eq_st.lhs - eq_st.rhs)}')

# Substitute t = sqrt(s^2 - 1) and solve in s.
# Or: clear denominators, square once to remove t, then solve.
poly_st = sp.together(sp.simplify(eq_st.lhs - eq_st.rhs))
num, den = sp.fraction(poly_st)
print(f'Numerator polynomial in (s, t): {sp.expand(num)}')
print(f'Denominator: {den}')

# Substitute t^2 = s^2 - 1 to eliminate t^2 occurrences.
num_simp = sp.expand(num)
# Eliminate t by collecting in t.
num_in_t = sp.Poly(num_simp, t)
print(f'Numerator collected in t: {num_in_t.as_expr()}')
deg_t = num_in_t.degree()
print(f'Degree in t: {deg_t}')

# Split into "even-in-t" and "odd-in-t":  P + Q*t,  then equation P = -Q*t  =>  P^2 = Q^2 * (s^2 - 1)
coeffs_t = num_in_t.all_coeffs()  # highest degree first
P = sum(c if (deg_t - i) % 2 == 0 else 0 for i, c in enumerate(coeffs_t))
Q = sum((c / t if (deg_t - i) % 2 == 1 else 0) for i, c in enumerate(coeffs_t))
print(f'P (even in t) = {sp.expand(P)}')
print(f'Q (odd in t / t) = {sp.expand(Q)}')

# Rationalised equation in s only:  P^2 - Q^2 * (s^2 - 1) = 0
rationalised = sp.expand(P**2 - Q**2 * (s**2 - 1))
print(f'Rationalised polynomial in s alone: {rationalised}')

# Substitute back s = sqrt(delta) (s^2 = delta)
rat_in_delta = rationalised.subs(s, sp.sqrt(delta))
rat_in_delta = sp.expand(rat_in_delta)
print(f'In delta: {rat_in_delta}')

# This should be a polynomial in delta.
poly_delta = sp.Poly(rat_in_delta, delta)
print(f'Degree in delta: {poly_delta.degree()}')
print(f'Leading coefficient: {poly_delta.LC()}')

# Factor over Q.
factored = sp.factor(rat_in_delta)
print(f'Factored: {factored}')

# Find rational roots
rational_roots = sp.solve(rat_in_delta, delta)
print(f'All roots (some may be extraneous from squaring): {rational_roots}')

# Numerically check
for r in rational_roots:
    try:
        r_num = complex(r)
        if abs(r_num.imag) < 1e-10 and r_num.real > 1.0:
            r_real = r_num.real
            # check whether it satisfies the original (unsquared) equation
            lhs = float((delta / 2).subs(delta, sp.Float(r_real)))
            rhs = float(f_2a_at_eta_b.subs(delta, sp.Float(r_real)))
            residual = lhs - rhs
            note = 'ORIGINAL ROOT' if abs(residual) < 1e-8 else 'extraneous'
            print(f'  delta = {r_real:.10f}  lhs={lhs:.8f} rhs={rhs:.8f}  {note}')
    except Exception as e:
        print(f'  could not eval {r}: {e}')

# Also: compute the value F* = delta*/2 at the smallest real root.
print()
print('Numerical answer:')
smallest = min(
    (complex(r).real for r in rational_roots
     if abs(complex(r).imag) < 1e-10 and complex(r).real > 1.05),
    default=None,
)
if smallest is not None:
    print(f'  delta*    = {smallest:.15f}')
    print(f'  F*        = delta*/2 = {smallest/2:.15f}')
    print(f'  9/16      = {9/16:.15f}')
    print(f'  saving    = 9/16 - F* = {9/16 - smallest/2:.15f}')
    print(f'  % gain    = {100 * (9/16 - smallest/2) / (9/16):.4f}%')
