"""
D7 — Extract the minimal polynomial of delta_1 over Q.

From freedelta.py we know the equation delta/2 = f_2a_max(delta).  Clearing
the two square roots sqrt(delta), sqrt(delta-1) by squaring gives a
polynomial in delta over Q that has, among its real roots in (1, 2):
  - delta_1 ~ 1.114907541476756
  - 4/3
  - phi = (1 + sqrt 5)/2

We isolate the minimal polynomial of delta_1 by computing the full
rationalised polynomial and factoring out the obvious factors.
"""

import sympy as sp

delta = sp.symbols('delta', real=True, positive=True)

# f_2a_max(delta) -- closed form from freedelta.py output.
# alpha_star = delta - sqrt(delta) * sqrt(delta - 1) / eta
# eta_b      = (sqrt(delta)*sqrt(delta - 1) - 1) / (delta - 2)
# f_2a_max(delta) = f_2(alpha_star, eta_b) =
#   (-delta**(5/2) - delta**(3/2) + 2*sqrt(delta) + delta**2*sqrt(delta - 1)
#     + 2*delta*sqrt(delta - 1) - 2*sqrt(delta - 1))
#  /(-delta**(3/2) + sqrt(delta) + sqrt(delta - 1))

s = sp.sqrt(delta)
t = sp.sqrt(delta - 1)
f2a = (-s**5 - s**3 + 2*s + delta**2 * t + 2 * delta * t - 2 * t) \
      / (-s**3 + s + t)
# Equation: delta/2 = f2a  <=>  N - (delta/2)*D = 0
num = (-s**5 - s**3 + 2*s + delta**2 * t + 2 * delta * t - 2 * t)
den = (-s**3 + s + t)
eq = num - (delta / 2) * den
eq = sp.expand(eq)
print('Equation in s, t:')
print(eq)

# Separate the s-part and t-part: eq = A(s) + B(s)*t  -- because every t
# appears to power 1 only (s = sqrt(delta), t = sqrt(delta-1); we have no t^2).
A = eq.coeff(t, 0)
B = eq.coeff(t, 1)
print()
print('A(s) =', sp.expand(A))
print('B(s) =', sp.expand(B))

# Equation A + B*t = 0   =>   A = -B*t   =>   A^2 = B^2 * (s^2 - 1)
rationalised = sp.expand(A**2 - B**2 * (s**2 - 1))
print()
print('Rationalised in s alone: degree', sp.Poly(rationalised, s).degree())
print(rationalised)

# Now substitute s^2 = delta to get a polynomial in delta.
# Check that rationalised has only even powers of s -- this is required.
poly_in_s = sp.Poly(rationalised, s)
if any(c != 0 for i, c in enumerate(poly_in_s.all_coeffs()) if (poly_in_s.degree() - i) % 2 == 1):
    print('WARNING: odd s-powers remain; check derivation')
else:
    print('All s-powers are even -- can substitute s^2 = delta cleanly.')

# Replace s -> sqrt(delta), then s^(2k) -> delta^k.
poly_delta_full = rationalised.subs(s, sp.sqrt(delta))
poly_delta_full = sp.expand(poly_delta_full)
print()
print('Polynomial in delta:')
print(poly_delta_full)
P = sp.Poly(poly_delta_full, delta)
print('Degree in delta:', P.degree())

# Factor over Q
fact = sp.factor(poly_delta_full)
print()
print('Factored over Q:')
print(fact)

# Identify the irreducible factor whose smallest root in (1, 2) is delta_1.
# Use Sturm's theorem or just numerical bisection on each factor.
factors = sp.Mul.make_args(fact)
for f in factors:
    if f.has(delta):
        # Extract base if it's a power
        if f.is_Pow:
            base = f.base
        else:
            base = f
        if base.has(delta):
            # Find real roots of base in (1, 2)
            roots = sp.solve(base, delta)
            for r in roots:
                try:
                    r_num = complex(r.evalf())
                    if abs(r_num.imag) < 1e-10:
                        rr = r_num.real
                        if 1.0 < rr < 2.0:
                            print(f'  factor {base} has real root in (1,2): {rr:.15f}')
                except Exception:
                    pass

# Direct approach: divide out (delta - 4/3) and (delta**2 - delta - 1) = 0,
# whose roots are phi, 1-phi.
poly_q = sp.Poly(poly_delta_full, delta, domain='QQ')
print()
print('Polynomial as QQ-poly:', poly_q)

# Divide by (delta - 4/3) = (3*delta - 4)/3
g1 = sp.Poly(3 * delta - 4, delta, domain='QQ')
g2 = sp.Poly(delta**2 - delta - 1, delta, domain='QQ')

q1, r1 = sp.div(poly_q, g1, domain='QQ')
print('After dividing by (3*delta - 4): remainder =', r1)
if r1.is_zero:
    poly_q = q1
    print('  quotient degree', poly_q.degree())

q2, r2 = sp.div(poly_q, g2, domain='QQ')
print('After dividing by (delta^2 - delta - 1): remainder =', r2)
if r2.is_zero:
    poly_q = q2
    print('  quotient degree', poly_q.degree())

# Continue dividing as long as possible
for g in [g1, g2]:
    while True:
        q, r = sp.div(poly_q, g, domain='QQ')
        if r.is_zero:
            poly_q = q
            print('  divided by', g.as_expr(), 'again, new degree', poly_q.degree())
        else:
            break

print()
print('Residual polynomial (should contain delta_1 as a root):')
print(poly_q.as_expr())
print('Degree:', poly_q.degree())
print('Leading coeff:', poly_q.LC())
print('Squarefree factorization:', sp.sqf_list(poly_q.as_expr(), delta))

# Find real roots in (1, 2)
print()
print('Real roots in (1, 2) of residual polynomial:')
real_roots = sp.solve(poly_q.as_expr(), delta)
for r in real_roots:
    try:
        r_num = complex(r.evalf(30))
        if abs(r_num.imag) < 1e-15:
            rr = r_num.real
            if 0.9 < rr < 2.0:
                print(f'  delta = {rr}')
    except Exception:
        pass

# Also: find roots numerically with high precision
print()
print('High-precision numerical roots of residual polynomial:')
poly_expr = poly_q.as_expr()
roots_numeric = sp.nroots(sp.Poly(poly_expr, delta), n=30)
for r in roots_numeric:
    try:
        r_complex = complex(r)
        if abs(r_complex.imag) < 1e-15:
            print(f'  {r_complex.real}')
    except Exception:
        print(f'  {r}')

# Identify the unique root close to 1.114907541
target = 1.114907541476756
print()
print(f'Looking for root closest to {target}:')
best = min(roots_numeric, key=lambda r: abs(complex(r).real - target) + 100 * abs(complex(r).imag))
print(f'  Best match: {best}')
print(f'  Difference from target: {abs(complex(best).real - target):.2e}')

# Minimal polynomial via sympy
print()
print('Minimal polynomial of delta_1 over Q (via minimal_polynomial):')
mp = sp.minimal_polynomial(sp.Float(target, 30), delta)
print(mp)
print('Factored:', sp.factor(mp))
