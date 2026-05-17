"""
witness.py
==========

Try the witness s = 1/4 (eta = 4/7) for f_2b > 9/16 on delta in (1, 5/4).
The hypothesis: P(s = 1/4, delta) factors as a perfect square times a
positive constant, giving an analytic proof that f_2b(4/7, delta) > 9/16
for every delta != 9/8 in the FPS-admissible range.
"""

import sympy as sp

s, delta, eta = sp.symbols('s delta eta', real=True, positive=True)

# Direct (eta, delta) parametrisation: alpha = beta = 2 - 1/eta,
# gamma = 2*eta - 1 + (1-eta)*delta.
alpha = 2 - 1/eta
gamma = eta * alpha + (1 - eta) * delta
f2b_eta = gamma - alpha * (delta - 1) / (delta - gamma)
f2b_eta = sp.simplify(f2b_eta)

# At eta = 4/7:
f2b_at_4_7 = sp.simplify(f2b_eta.subs(eta, sp.Rational(4, 7)))
print('f_2b(eta = 4/7, delta) =', f2b_at_4_7)
print()

diff = sp.simplify(f2b_at_4_7 - sp.Rational(9, 16))
print('f_2b(4/7, delta) - 9/16 =')
print(sp.together(diff))
print()
print('factored:')
print(sp.factor(diff))
print()

# Reparametrise to s = alpha = 2 - 1/eta.
# eta = 1/(2-s); cross-check the substituted formula:
f2b_s = f2b_eta.subs(eta, 1/(2 - s))
f2b_s = sp.simplify(f2b_s)
print('f_2b(s, delta) =', f2b_s)
print()

# f_2b - 9/16 as a function of (s, delta).
diff_s = sp.simplify(f2b_s - sp.Rational(9, 16))
print('f_2b(s, delta) - 9/16 =')
print(sp.together(diff_s))
print('factored:')
print(sp.factor(diff_s))
print()

# Substitute s = 1/4:
at_quarter = sp.simplify(diff_s.subs(s, sp.Rational(1, 4)))
print('At s = 1/4:')
print('  f_2b(s=1/4, delta) - 9/16 =', at_quarter)
print('  factored:', sp.factor(at_quarter))
print()

# Numerator polynomial P(s, delta) := 16(1-s)*(...)  - 9(2-s)(delta-s)
P = 16 * (1 - s) * (delta**2 - 4*s*delta + s**2*delta + 4*s - s**2) \
    - 9 * (2 - s) * (delta - s)
P = sp.expand(P)
print('P(s, delta) :=', P)
print()
print('P(1/4, delta) =', sp.expand(P.subs(s, sp.Rational(1, 4))))
print('factored:', sp.factor(P.subs(s, sp.Rational(1, 4))))
print()
print('P(0, delta) =', sp.expand(P.subs(s, 0)))
print('factored:', sp.factor(P.subs(s, 0)))
print()

# Also: at delta = 9/8, what does P(s, 9/8) factor as?
print('P(s, 9/8) =', sp.factor(P.subs(delta, sp.Rational(9, 8))))
print()

# Validate eta = 4/7 lies in the Case 2b interval [1/2, eta_b(delta)) for
# delta in (1, 9/8].  Solve eta_b(delta) = 4/7 for delta.
eta_b = (sp.sqrt(delta * (delta - 1)) - 1) / (delta - 2)
eq = sp.Eq(eta_b, sp.Rational(4, 7))
sols = sp.solve(eq, delta)
print('eta_b(delta) = 4/7  at  delta =', sols)
print()

# Numerical evaluation at a few delta values:
print('Numerical check of f_2b(4/7, delta) > 9/16 on (1, 9/8):')
print(f"{'delta':>10}  {'witness value':>15}  {'predicted':>15}  {'F bound':>15}")
for d_val in [1.01, 1.05, 1.10, 1.115, 1.120, 1.123, 1.124, 1.1249, 1.125, 1.13, 1.20]:
    fv = float(f2b_at_4_7.subs(delta, d_val))
    formula = 9/16 + 3 * (d_val - 9/8)**2 / (7 * (d_val - 1/4))
    bound = max(d_val / 2, fv)
    flag = '  *** =9/16' if abs(fv - 9/16) < 1e-12 else ''
    print(f'{d_val:>10.5f}  {fv:>15.10f}  {formula:>15.10f}  {bound:>15.10f}{flag}')
