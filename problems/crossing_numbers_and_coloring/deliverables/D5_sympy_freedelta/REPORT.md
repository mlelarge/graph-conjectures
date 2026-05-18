# D5 — SymPy verification of FPS Claim 3.7 with $\delta$ free

> **WITHDRAWN / SUPERSEDED (2026-05-18).** The headline claim of this
> report — that re-tuning $\delta$ from $9/8$ to $\delta_1 \approx
> 1.11491$ yields $F^\star \approx 0.5574 < 9/16$ — is **false**. It
> rests on the silent assumption that $f_{2b}^{\max}(\delta) = \delta/2$
> at *every* $\delta \in (1, 5/4)$, but $f_{2b}$ is monotone in $\eta$
> on $[1/2, \eta_b)$ only for $\delta \ge -3 + \sqrt{17} \approx 1.12311$
> (see `case2b_check.py` / `case2b_check.log`). On $(1, -3 + \sqrt{17})$
> — which contains $\delta_1$ — the true $f_{2b}^{\max}(\delta_1)
> \approx 0.5654 > 9/16$, so no improvement is obtained. The corrected
> result is **D8** (`deliverables/D8_paper/sharpness_9_8.tex`), which
> proves $F(\delta) \ge 9/16$ on $(1, 5/4)$ with equality iff
> $\delta = 9/8$ via the witness identity
> $f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2 / [7(4\delta - 1)]$.
> The body of this file is preserved unchanged below as an error-mode
> archive; do not cite its conclusions.

**Date.** 2026-05-16.
**Goal.** Settle the D3 hypothesis that lowering $\delta$ from $9/8$ to $11/10$
gives a "free" improvement of FPS Lemma 2.3's constant from $9/16$ to $11/20$.
**Source under test.** Fox–Pach–Suk, arXiv:2510.05893v1, Section 3, Claim 3.7.
**Reconstruction.** `../D3_R5a_reconstruction.md`.

## Headline

| $\delta$ | $f_1 = \delta/2$ | $f_{2a}(\delta)$ | $f_{2b} = \delta/2$ | $F(\delta)$ | Binding |
|---|---|---|---|---|---|
| **$\delta^* \approx 1.1149075415$** | $0.5574537707$ | $0.5574537707$ | $0.5574537707$ | $\mathbf{0.5574537707}$ | $f_1 = f_{2a} = f_{2b}$ |
| $9/8 = 1.125$ (FPS) | $9/16 = 0.5625$ | $11/20 = 0.5500$ | $9/16 = 0.5625$ | $\mathbf{9/16 = 0.5625}$ | $f_1 = f_{2b}$ |
| $11/10 = 1.1$ (D3 hypothesis) | $0.5500$ | $0.5713$ | $0.5500$ | $\mathbf{0.5713}$ | $f_{2a}$ |

**Verdict.**

- **D3's hypothesis is wrong.** $f_{2a}(\delta)$ is *not* $\delta$-independent at $11/20$. Setting $\delta = 11/10$ makes things *worse*, not better ($F = 0.5713 > 9/16$).
- **But $9/16$ is not sharp either.** Re-tuning $\delta$ from $9/8$ to $\delta^* \approx 1.11491$ improves the constant from $9/16 = 0.5625$ to $F^* \approx 0.557454$. The improvement is **$\approx 0.005$, or $\approx 0.90\%$**.
- This *meets the MPO threshold* "any $c < 9/16$" in `review_v3.md` and the v4 plan's R5a tier list.
- It does **not** reach the stretch target $11/20 = 0.55$ or the dream target $1/2$.

## What I verified

All FPS Claim 3.7 numerical claims at $\delta = 9/8$ reproduced exactly:

- Case 1: $f_1(9/8) = 9/16$. ✓
- Case 2a stationary point: $\alpha^*(\eta, 9/8) = (9 - 3/\eta)/8 = 3(3\eta - 1)/(8\eta)$. ✓
- Case 2a value at $\alpha^*$: $f_{2a}(\eta, 9/8) = (3 + 1/\eta)/8 = (3\eta + 1)/(8\eta)$. ✓ (matches the FPS-printed form)
- Case 2a/2b boundary: $\eta_b(9/8) = 5/7$. ✓
- Case 2a maximum (at $\eta = 5/7$): $11/20$. ✓
- Case 2b at $\eta = 1/2$: $9/16$. ✓
- Overall max at $\delta = 9/8$: $9/16$. ✓

The D3-flagged sign discrepancy in FPS's printed Case-2b objective (`(2 + 1/η)/(8 − 7η)` vs. the algebraically correct `(2 − 1/η)/(8 − 7η)`) is **confirmed**: my SymPy derivation produces the `−` form. The final value $9/16$ at $\eta = 1/2$ is unaffected, so this is presumably a typo in FPS arXiv v1.

## What the experiment found

### General-$\delta$ formulas

After substituting $\gamma = \eta\alpha + (1-\eta)\delta$ (Case 2 constraint) and using the stationary point $\alpha^*(\eta, \delta) = \delta - \sqrt{\delta(\delta - 1)}/\eta$:

$$
f_{2a}(\eta, \delta) \;=\; -\frac{2\delta^{3/2}}{\sqrt{\delta - 1}} \;+\; \frac{2\sqrt{\delta}}{\sqrt{\delta - 1}} \;+\; \delta \;+\; \frac{\delta - 1}{\eta}.
$$

The Case 2a/2b boundary at $\alpha^* = \beta = 2 - 1/\eta$ gives

$$
\eta_b(\delta) \;=\; \frac{\sqrt{\delta(\delta - 1)} - 1}{\delta - 2}.
$$

At $\eta = \eta_b(\delta)$, $f_{2a}$ takes the value

$$
f_{2a}^{\max}(\delta) \;=\; \frac{-\delta^{5/2} - \delta^{3/2} + 2\sqrt{\delta} + (\delta^2 + 2\delta - 2)\sqrt{\delta - 1}}{-\delta^{3/2} + \sqrt{\delta} + \sqrt{\delta - 1}}.
$$

The Case 2b maximum is at $\eta = 1/2$ (so $\alpha = \beta = 0$), giving

$$
f_{2b}^{\max}(\delta) \;=\; \frac{\delta}{2}.
$$

Case 1 trivially gives $f_1^{\max}(\delta) = \delta/2$.

So the overall ceiling is

$$
F(\delta) \;=\; \max\bigl(\, \tfrac{\delta}{2},\ f_{2a}^{\max}(\delta) \,\bigr).
$$

### Behaviour of $f_{2a}^{\max}$ in $\delta$

$f_{2a}^{\max}(\delta)$ is U-shaped on $\delta \in (1, \infty)$:

- $\lim_{\delta \to 1^+} f_{2a}^{\max}(\delta) = 1$ (the high-degree case dominates).
- $f_{2a}^{\max}(9/8) = 11/20 = 0.5500$.
- $f_{2a}^{\max}$ has a minimum near $\delta \approx 1.2$ at value $\approx 0.534$.
- $f_{2a}^{\max}(4/3) = 2/3$.
- $f_{2a}^{\max}(\delta) \to \infty$ as $\delta \to \infty$.

### Where $F(\delta) = \max(\delta/2, f_{2a}^{\max})$ is minimised

The two branches $\delta/2$ (increasing) and $f_{2a}^{\max}$ (U-shaped) intersect at three real roots in $[1, 2]$:

| Root $\delta_i$ | $\delta_i/2 = f_{2a}^{\max}(\delta_i)$ | Comment |
|---|---|---|
| $\delta_1 \approx 1.114907541476756$ | $\approx 0.557453770738378$ | **the optimum** |
| $\delta_2 = 4/3$ | $2/3 \approx 0.666667$ | local equalisation, much worse |
| $\delta_3 = \phi = (1 + \sqrt 5)/2 \approx 1.618033988$ | $\phi/2 \approx 0.809017$ | even worse |

For $\delta \in (1, \delta_1)$: $f_{2a}^{\max}(\delta) > \delta/2$, so $F = f_{2a}^{\max}$ — decreasing as $\delta$ grows from $1$ toward $\delta_1$.
For $\delta \in (\delta_1, \delta_2)$: $f_{2a}^{\max}(\delta) < \delta/2$, so $F = \delta/2$ — increasing as $\delta$ grows.
The minimum of $F$ on $\delta > 1$ is therefore at $\delta_1$.

### Closed-form status of $\delta_1$

After clearing $\sqrt{\delta}, \sqrt{\delta - 1}$ by squaring, the equation $\delta/2 = f_{2a}^{\max}(\delta)$ becomes a polynomial in $\delta$. SymPy returns three real roots in $(1, 2)$: $\delta_1, 4/3, \phi$. The smallest, $\delta_1$, is the root of a residual cubic factor of the rationalised polynomial; I did not extract that cubic in radicals (the squaring picked up extraneous roots and I did not isolate the irreducible-cubic factor cleanly). The numerical value $\delta_1 \approx 1.114907541476756$ is reproducible to 15 digits via `mpmath` bisection.

**This is a 1-day TODO** if a closed form is needed for publication (`sp.minimal_polynomial(delta_1, x)` on the high-precision numerical value).

## Caveats — what this experiment does *not* settle

The Claim 3.7 optimisation is one piece of the FPS Lemma 2.3 machinery. The full argument also uses:

1. **Proposition 3.4** ($\mu = o(k)$) — bounded by FPS footnote 1's cap $|U(d)| \le k - k^{0.9}$. **This may force a lower bound on $\delta$**. The numerical optimum $\delta_1 \approx 1.115$ is below $9/8 = 1.125$; we must verify Proposition 3.4 still goes through at $\delta = \delta_1$ before publishing the improvement.
2. **Proposition 3.3** ($\Delta \le (c + o(1)) k$) — this is what Claim 3.7 establishes. Reducing $\delta$ does not directly threaten it.
3. **Section 3 case II** (FPS p. 11, $\ell = k - \phi(k)$) — handled separately by FPS via reduction to a $\beta = 1 - o(1)$ instance. May need re-verification at the new $\delta$.

**The single most important follow-up:** verify that Proposition 3.4 (multiplicity bound) is robust to $\delta \in [\delta_1, 9/8]$. If yes, the improvement $9/16 \to 0.557454$ is publishable as a standalone refinement of FPS Lemma 2.3. If no, $\delta = 9/8$ was forced by Proposition 3.4 and the improvement is illusory.

## Downstream impact (FPS Theorem 1.2)

FPS Theorem 1.2(ii) gives the asymptotic vertex bound $n < (1.64 - o(1)) k$ from $\chi'(H_i) \le (c + o(1)) k_i$ with $c = 9/16$. The exact derivation of the coefficient $1.64$ from $c$ is in FPS Section 2 (not reconstructed here). A naive linear-extrapolation estimate: if the coefficient is a smooth function $g(c)$ with $g(9/16) = 1.64$ and a local derivative on the order of $1$–$10$, then improving $c$ by $0.005$ improves the vertex coefficient by $\sim 0.005$–$0.05$, i.e. $1.64 \to \sim 1.645$–$1.69$. **This is not enough to close $t = 25$ or $t = 26$** (the residual orders $48, 50, 51$ remain far above any plausible improved vertex threshold) — but it is a publishable refinement of an SoCG 2025 result.

## Verdict for the R5a 30-day question

The PI's `INTEGRATION.md` (after v4 sync) lists three possible 30-day outcomes for R5a:

> (i) $c < 9/16$: immediate theorem target. Role 7 drafts the improvement.
> (ii) $c = 9/16$ binding: pivot R5a to "obstruction note" — still publishable.
> (iii) Algebra unclear: escalate to Role 8 for verification.

This experiment returns **outcome (i)**, **with caveats**:

- $c < 9/16$ is achievable in the Claim-3.7 algebra. Specifically $c \le F^* \approx 0.557454$ at $\delta = \delta_1 \approx 1.11491$.
- The improvement is **~0.9%**, not the dream $1/16 \approx 11\%$ (down to $1/2$).
- Publishability is conditional on Proposition 3.4 robustness at $\delta = \delta_1$.

**Recommended next steps (in priority order):**

1. **Verify Proposition 3.4 at $\delta = \delta_1$.** ~1–3 days. If FAIL, the FPS choice $\delta = 9/8$ was forced and the algebraic improvement is illusory; pivot R5a to outcome (ii).
2. **Extract the closed form for $\delta_1$ and $F^*$.** ~1 day via `sp.minimal_polynomial` on the high-precision numerical root.
3. **Re-derive FPS Theorem 1.2 vertex coefficient with the new $c$.** Compute exact downstream improvement to "$1.64$".
4. **Sanity-check the sign typo** in FPS arXiv v1 Case 2b objective (`+1/η` vs `−1/η`); cross-check against the SoCG 2025 published version.

If Step 1 passes, this is a publishable note: "Tightening the chromatic-index threshold in Fox–Pach–Suk's Lemma 2.3". Modest in absolute size, but a Track B v4 MPO hit in less than 1 week of work.

## Reproducibility

- Environment: `uv venv` + `uv pip install sympy` ($\to$ sympy 1.14.0).
- Run: `uv run freedelta.py` (full algebra + numerical scan) and `uv run closedform.py` (closed-form attempt — partial).
- Outputs: `run.log`, `closedform.log`.
- All numerical results above are exact rational / radical where possible, and reproduced to $\ge 10$ digits otherwise.
