"""
D5 — SymPy verification of Fox-Pach-Suk Claim 3.7 with delta as a free parameter.

Setup (per D3_R5a_reconstruction.md):

    Objective (FPS (6)):
        f(alpha, beta, gamma; delta) = gamma - alpha * (delta - 1) / (delta - gamma)

    Constraints:
        0 <= alpha <= beta <= 1
        0 <= gamma <= alpha + (delta - alpha) * (1 - beta) / (2 - beta)

    Reparametrise: eta = 1 - (1 - beta)/(2 - beta) in [1/2, 1].
    Equivalently  beta = 2 - 1/eta.

    In Case 2 (the constraint on gamma is tight):
        gamma = alpha + (delta - alpha)*(1 - eta) = eta*alpha + (1 - eta)*delta.

    Case 1: alpha = 0, gamma = delta*(1-beta)/(2-beta). Max over beta at beta=0
            gives f_1(delta) = delta/2.

    Case 2: stationarity in alpha gives an interior optimum alpha*(eta, delta).
            If alpha*(eta, delta) <= beta(eta) = 2 - 1/eta, that's Case 2a.
            Otherwise the optimum is forced to alpha = beta = 2 - 1/eta -> Case 2b.

For delta = 9/8 FPS get:
    Case 1   = 9/16  (= delta/2)
    Case 2a  = 11/20 (at eta = 5/7, the boundary)
    Case 2b  = 9/16  (at eta = 1/2, the lower endpoint)
    Overall  = max = 9/16.

The question: as a function of delta, what is the overall max
    F(delta) = max(f_1(delta), f_2a*(delta), f_2b*(delta))
and what delta minimises it?

Hypothesis from the D3 reconstruction: f_2a is delta-independent (= 11/20),
while f_1 and f_2b both scale as delta/2. If so, the optimal delta is 11/10
(where delta/2 = 11/20) and the FPS constant improves from 9/16 to 11/20.

Run:   uv run freedelta.py
"""

import sympy as sp

# Symbols
alpha, beta, gamma, eta, delta = sp.symbols('alpha beta gamma eta delta',
                                             real=True, positive=True)

# Objective (FPS (6))
f_raw = gamma - alpha * (delta - 1) / (delta - gamma)

# ----------------------------------------------------------------------
# Step 1: Case 1.   alpha = 0, gamma at upper bound delta*(1-beta)/(2-beta).
# ----------------------------------------------------------------------
print('=' * 70)
print('CASE 1:  alpha = 0,  gamma = delta*(1 - beta)/(2 - beta)')
print('=' * 70)

f_case1 = f_raw.subs({
    alpha: 0,
    gamma: delta * (1 - beta) / (2 - beta),
})
f_case1 = sp.simplify(f_case1)
print(f'  f_1(beta, delta) = {f_case1}')

# decreasing in beta on [0,1] -> max at beta=0
f1_max = sp.simplify(f_case1.subs(beta, 0))
print(f'  max over beta in [0,1]: f_1 = {f1_max}')
print(f'  At delta = 9/8: f_1 = {f1_max.subs(delta, sp.Rational(9, 8))}')

# ----------------------------------------------------------------------
# Step 2: Case 2.   Substitute gamma = eta*alpha + (1-eta)*delta.
#         Find alpha*(eta, delta) by stationarity.
# ----------------------------------------------------------------------
print('=' * 70)
print('CASE 2:  gamma = eta*alpha + (1 - eta)*delta  (constraint tight)')
print('=' * 70)

gamma_case2 = eta * alpha + (1 - eta) * delta
f_case2 = f_raw.subs(gamma, gamma_case2)
f_case2 = sp.simplify(f_case2)
print(f'  f_2(alpha, eta, delta) = {f_case2}')

# Stationarity in alpha
df2_dalpha = sp.diff(f_case2, alpha)
df2_dalpha = sp.simplify(df2_dalpha)
print(f'  d/dalpha f_2 = {df2_dalpha}')

alpha_star = sp.solve(df2_dalpha, alpha)
print(f'  stationary points alpha*: {alpha_star}')

# FPS at delta = 9/8 gets alpha* = (9 - 3/eta)/8.
# Pick the root that matches FPS in the delta = 9/8 limit.
for cand in alpha_star:
    val = sp.simplify(cand.subs(delta, sp.Rational(9, 8)))
    fps_form = sp.Rational(9, 8) - 3 / (sp.Rational(8) * eta)  # = (9 - 3/eta)/8
    fps_form = sp.simplify(fps_form - sp.Rational(0))  # canonicalise
    print(f'    candidate alpha*(eta, 9/8) = {val};  FPS = (9 - 3/eta)/8 = {sp.simplify(fps_form)}')

# Pick the FPS root:
# FPS's alpha* = (9 - 3/eta)/8 in the delta=9/8 case.
# Generic-delta analogue (from the quadratic solution below):
alpha_star_generic = None
for cand in alpha_star:
    test = sp.simplify(cand.subs(delta, sp.Rational(9, 8))
                       - (sp.Rational(9, 8) - 3 / (8 * eta)))
    if test == 0:
        alpha_star_generic = cand
        break
if alpha_star_generic is None:
    # Heuristic: pick the smaller positive root.
    real_pos = [c for c in alpha_star
                if sp.simplify(c.subs({delta: sp.Rational(9, 8), eta: sp.Rational(3, 4)})) > 0]
    alpha_star_generic = min(real_pos, key=lambda c: sp.simplify(
        c.subs({delta: sp.Rational(9, 8), eta: sp.Rational(3, 4)})))

print(f'  alpha*(eta, delta) = {sp.simplify(alpha_star_generic)}')
print(f'  alpha*(eta, 9/8)   = {sp.simplify(alpha_star_generic.subs(delta, sp.Rational(9, 8)))}')
print(f'  At eta = 5/7, delta = 9/8: alpha* = '
      f'{sp.simplify(alpha_star_generic.subs({delta: sp.Rational(9, 8), eta: sp.Rational(5, 7)}))}'
      f'  (FPS: 3/4)')

# ----------------------------------------------------------------------
# Step 3: Case 2a value (alpha = alpha*, eta in [eta_boundary, 1])
# ----------------------------------------------------------------------
print('=' * 70)
print('CASE 2a:  alpha = alpha*(eta, delta),  eta >= eta_boundary')
print('=' * 70)

f_case2a_eta = f_case2.subs(alpha, alpha_star_generic)
f_case2a_eta = sp.simplify(f_case2a_eta)
print(f'  f_2a(eta, delta) = {f_case2a_eta}')

print(f'  At delta = 9/8: f_2a(eta) = {sp.simplify(f_case2a_eta.subs(delta, sp.Rational(9, 8)))}')
print(f'  FPS form was (3 + 1/eta)/8.  Check at eta = 5/7:')
fps_2a_at_5_7 = (sp.Rational(3) + sp.Rational(7, 5)) / 8
print(f'    FPS:  (3 + 7/5)/8 = {fps_2a_at_5_7} = {sp.nsimplify(fps_2a_at_5_7)}')
print(f'    Ours: f_2a(5/7, 9/8) = {sp.simplify(f_case2a_eta.subs({delta: sp.Rational(9, 8), eta: sp.Rational(5, 7)}))}')

# Behaviour of f_2a in eta -- compute derivative
df2a_deta = sp.simplify(sp.diff(f_case2a_eta, eta))
print(f'  d/d eta f_2a = {df2a_deta}')
print(f'  At delta = 9/8: d/d eta f_2a = {sp.simplify(df2a_deta.subs(delta, sp.Rational(9, 8)))}')

# The Case 2a / 2b boundary is alpha*(eta, delta) = beta(eta) = 2 - 1/eta.
print()
print('  Case 2a/2b boundary: alpha*(eta, delta) = 2 - 1/eta')
boundary_eq = sp.Eq(alpha_star_generic, 2 - 1 / eta)
eta_boundary = sp.solve(boundary_eq, eta)
print(f'  Solutions for eta_boundary(delta): {eta_boundary}')
for sol in eta_boundary:
    val_at_9_8 = sp.simplify(sol.subs(delta, sp.Rational(9, 8)))
    print(f'    eta_boundary(9/8) candidate = {val_at_9_8}   (FPS gives 5/7)')

# Pick the FPS root for the boundary
eta_b = None
for sol in eta_boundary:
    if sp.simplify(sol.subs(delta, sp.Rational(9, 8)) - sp.Rational(5, 7)) == 0:
        eta_b = sol
        break
if eta_b is None:
    # numerical fallback
    eta_b = min(eta_boundary, key=lambda s: abs(
        complex(s.subs(delta, sp.Rational(9, 8))) - 5 / 7))
print(f'  eta_boundary(delta) = {sp.simplify(eta_b)}')

# Case 2a value at the boundary eta = eta_b
f_case2a_at_boundary = sp.simplify(f_case2a_eta.subs(eta, eta_b))
print(f'  f_2a at the boundary eta = eta_b(delta):')
print(f'    f_2a(eta_b, delta) = {f_case2a_at_boundary}')
print(f'    At delta = 9/8: {sp.simplify(f_case2a_at_boundary.subs(delta, sp.Rational(9, 8)))}'
      f'  (FPS: 11/20)')

# Also evaluate Case 2a at the other endpoint eta = 1 (corresponds to beta = 1)
# Maximum of Case 2a over its eta-range
f2a_max = sp.simplify(f_case2a_at_boundary)  # since f_2a is decreasing in eta
print(f'  max over Case 2a interval: f_2a = {f2a_max}  (since f_2a is decreasing in eta)')

# ----------------------------------------------------------------------
# Step 4: Case 2b value (alpha = beta = 2 - 1/eta, eta in [1/2, eta_boundary))
# ----------------------------------------------------------------------
print('=' * 70)
print('CASE 2b:  alpha = beta = 2 - 1/eta,  eta in [1/2, eta_boundary)')
print('=' * 70)

# Replace alpha with 2 - 1/eta in f_case2
f_case2b_eta = f_case2.subs(alpha, 2 - 1 / eta)
f_case2b_eta = sp.simplify(f_case2b_eta)
print(f'  f_2b(eta, delta) = {f_case2b_eta}')

print(f'  At delta = 9/8: {sp.simplify(f_case2b_eta.subs(delta, sp.Rational(9, 8)))}')
print(f'  At delta = 9/8, eta = 1/2: '
      f'{sp.simplify(f_case2b_eta.subs({delta: sp.Rational(9, 8), eta: sp.Rational(1, 2)}))}'
      f'  (FPS: 9/16)')

# Behaviour in eta
df2b_deta = sp.simplify(sp.diff(f_case2b_eta, eta))
print(f'  d/d eta f_2b = {df2b_deta}')
print(f'  At delta = 9/8: d/d eta f_2b = {sp.simplify(df2b_deta.subs(delta, sp.Rational(9, 8)))}')

# FPS claim: f_2b decreasing in eta on [1/2, eta_boundary), so max at eta = 1/2
f_case2b_at_half = sp.simplify(f_case2b_eta.subs(eta, sp.Rational(1, 2)))
print(f'  f_2b(eta = 1/2, delta) = {f_case2b_at_half}')

f2b_max = f_case2b_at_half
print(f'  max over Case 2b interval: f_2b = {f2b_max}  (assuming decreasing in eta)')

# ----------------------------------------------------------------------
# Step 5: Combine and find the optimal delta
# ----------------------------------------------------------------------
print('=' * 70)
print('OVERALL F(delta) = max(f_1, f_2a, f_2b) and the optimal delta')
print('=' * 70)

print(f'  f_1 (delta)     = {f1_max}')
print(f'  f_2a(delta)     = {f2a_max}')
print(f'  f_2b(delta)     = {f2b_max}')

# Per FPS at delta=9/8: f1 = 9/16, f_2a = 11/20, f_2b = 9/16, max = 9/16.
print()
print('  Sanity check at delta = 9/8:')
for label, expr in [('f_1', f1_max), ('f_2a', f2a_max), ('f_2b', f2b_max)]:
    print(f'    {label}(9/8) = {sp.simplify(expr.subs(delta, sp.Rational(9, 8)))}')

# Solve f_1(delta) = f_2a(delta), i.e. delta/2 = 11/20  =>  delta = 11/10.
print()
print('  Equalising f_1(delta) = f_2a(delta):')
eq_1_2a = sp.Eq(f1_max, f2a_max)
sols_1_2a = sp.solve(eq_1_2a, delta)
print(f'    delta = {sols_1_2a}')

print('  Equalising f_2b(delta) = f_2a(delta):')
eq_2b_2a = sp.Eq(f2b_max, f2a_max)
sols_2b_2a = sp.solve(eq_2b_2a, delta)
print(f'    delta = {sols_2b_2a}')

# f_2a involves sqrt(delta - 1), so it's real only for delta >= 1.
# Scan delta >= 1.
print()
print('  Numerical scan: F(delta) on a grid (delta >= 1 required by sqrt(delta-1))')
print(f'    {"delta":>8}  {"f_1":>10}  {"f_2a":>10}  {"f_2b":>10}  {"F":>10}')
for d_val in [sp.Rational(d_num, d_den)
              for (d_num, d_den) in
              [(1001, 1000), (101, 100), (105, 100), (108, 100),
               (11, 10), (1125, 1000),  # 9/8
               (115, 100), (12, 10), (125, 100), (13, 10),
               (4, 3), (15, 10)]]:
    try:
        f1v = float(f1_max.subs(delta, d_val))
        f2av = float(f2a_max.subs(delta, d_val))
        f2bv = float(f2b_max.subs(delta, d_val))
        Fv = max(f1v, f2av, f2bv)
        print(f'    {float(d_val):>8.4f}  {f1v:>10.6f}  {f2av:>10.6f}  '
              f'{f2bv:>10.6f}  {Fv:>10.6f}')
    except (TypeError, ValueError) as e:
        print(f'    {float(d_val):>8.4f}  (complex or out of domain: {e})')

# Limit as delta -> 1+
print()
print('  Asymptotic behaviour as delta -> 1+:')
print(f'    lim f_1(delta)  = {sp.limit(f1_max,  delta, 1, "+")}')
print(f'    lim f_2a(delta) = {sp.limit(f2a_max, delta, 1, "+")}')
print(f'    lim f_2b(delta) = {sp.limit(f2b_max, delta, 1, "+")}')

# Behaviour of f_2a in delta
df2a_ddelta = sp.simplify(sp.diff(f2a_max, delta))
print()
print(f'  d/d delta f_2a = {df2a_ddelta}')
print(f'  Sign of d/d delta f_2a at delta = 9/8: '
      f'{float(df2a_ddelta.subs(delta, sp.Rational(9, 8))):.6f}'
      f'  (positive => f_2a increasing in delta)')

# Fine scan to find the minimum of F(delta) precisely.
print()
print('  Fine scan around delta = 9/8 = 1.125:')
print(f'    {"delta":>10}  {"f_1":>10}  {"f_2a":>10}  {"F":>10}  {"binding":>10}')
import sympy as sp_
best_delta, best_F = None, float('inf')
for d_int in range(1100, 1151):  # 1.100 to 1.150 step 0.001
    d_val = sp.Rational(d_int, 1000)
    try:
        f1v = float(f1_max.subs(delta, d_val))
        f2av = float(f2a_max.subs(delta, d_val))
        Fv = max(f1v, f2av)
        binding = 'f_1=f_2b' if f1v >= f2av else 'f_2a'
        if d_int % 5 == 0 or abs(f1v - f2av) < 1e-4:
            print(f'    {float(d_val):>10.4f}  {f1v:>10.6f}  {f2av:>10.6f}  '
                  f'{Fv:>10.6f}  {binding:>10}')
        if Fv < best_F:
            best_F = Fv
            best_delta = d_val
    except (TypeError, ValueError):
        pass

print()
print(f'  Best delta in fine scan: {float(best_delta):.4f}  with F = {best_F:.6f}')

# Solve f_1(delta) = f_2a(delta) numerically near delta = 9/8 = 1.125
print()
print('  Numerical root-find of delta/2 = f_2a(delta) near 1.125:')
try:
    crossover = sp.nsolve(f1_max - f2a_max, delta, 1.12, prec=30)
    print(f'    crossover delta* = {crossover}')
    print(f'    F(delta*)        = {float(f1_max.subs(delta, crossover)):.10f}')
    print(f'    Compare 9/16     = {float(sp.Rational(9, 16)):.10f}')
    print(f'    Compare 11/20    = {float(sp.Rational(11, 20)):.10f}')
except Exception as e:
    print(f'    nsolve failed: {e}')

# Symbolically simplify f_2a(delta) and try to find the exact root delta/2 = f_2a(delta)
print()
print('  Symbolic attempt: rationalise the equation delta/2 = f_2a(delta) and solve.')
# Multiply through: 2*f_2a(delta) - delta = 0.  Bring to a polynomial in delta by
# eliminating sqrt(delta) and sqrt(delta-1).
eq = sp.simplify(2 * f2a_max - delta)
eq_radsimp = sp.radsimp(eq)
print(f'    Equation: 2*f_2a - delta = {eq_radsimp}')

# Substitute u = sqrt(delta), v = sqrt(delta - 1); then u^2 - v^2 = 1.
# Direct numeric search for *all* real roots of f_1 = f_2a in [1, 2]
print()
print('  All real roots of f_1(delta) = f_2a(delta) in [1, 2]:')
g = sp.lambdify(delta, f1_max - f2a_max, modules='math')
import math
prev_d, prev_g = 1.001, None
roots = []
try:
    prev_g = g(prev_d)
except Exception:
    pass
for k in range(1, 1001):
    cur_d = 1.001 + k * (2.0 - 1.001) / 1000.0
    try:
        cur_g = g(cur_d)
        if prev_g is not None and prev_g * cur_g < 0:
            # bisect
            lo, hi = prev_d, cur_d
            for _ in range(60):
                mid = (lo + hi) / 2
                gm = g(mid)
                if gm == 0:
                    break
                if g(lo) * gm < 0:
                    hi = mid
                else:
                    lo = mid
            root = (lo + hi) / 2
            roots.append(root)
        prev_d, prev_g = cur_d, cur_g
    except Exception:
        prev_g = None
        prev_d = cur_d

for r in roots:
    print(f'    delta = {r:.10f}  (f_1 = f_2a = {r / 2:.10f})')

print()
print('  KEY: the minimum of F(delta) = max(delta/2, f_2a(delta)) is at the')
print('  smaller of these roots, since f_2a is decreasing then increasing.')

# Verdict
print()
print('=' * 70)
print('VERDICT')
print('=' * 70)
F_at_9_8 = max(
    sp.simplify(f1_max.subs(delta, sp.Rational(9, 8))),
    sp.simplify(f2a_max.subs(delta, sp.Rational(9, 8))),
    sp.simplify(f2b_max.subs(delta, sp.Rational(9, 8))),
)
F_at_11_10 = max(
    sp.simplify(f1_max.subs(delta, sp.Rational(11, 10))),
    sp.simplify(f2a_max.subs(delta, sp.Rational(11, 10))),
    sp.simplify(f2b_max.subs(delta, sp.Rational(11, 10))),
)
print(f'  F(9/8)  = {F_at_9_8}   = {float(F_at_9_8):.6f}')
print(f'  F(11/10) = {F_at_11_10}  = {float(F_at_11_10):.6f}')
if F_at_11_10 < F_at_9_8:
    saving = F_at_9_8 - F_at_11_10
    print(f'  *** delta = 11/10 IMPROVES the bound: {F_at_9_8} -> {F_at_11_10}'
          f'  (gain = {saving} = {float(saving):.6f})')
elif F_at_11_10 > F_at_9_8:
    print(f'  delta = 11/10 is WORSE.')
else:
    print(f'  No change.')
