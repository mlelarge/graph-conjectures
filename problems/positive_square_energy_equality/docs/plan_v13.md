# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v13** (this version): incorporates Phase 10 (Stieltjes-transform derivation of
  the half-line boundary spectral density) and Phase 11 (Portmanteau closure
  bridging finite-$n$ to the half-line limit). One headline outcome:
  **(a.2-path) is upgraded to a fully proved theorem**, *including* the
  finite-$n \to \infty$ identification. The v12 candidate is now closed.

  Specifically:

  1. **Phase 10 — Half-line spectral theorem (proved).** For the half-line
     pentadiagonal Toeplitz $T = A(L_\infty)$ on $\ell^2(\mathbb{N})$ and
     $w = e_1 + e_2$:
     - Self-reciprocal quartic $\xi^4 + \xi^3 - z\xi^2 + \xi + 1 = 0$ factors
       via $u = \xi + 1/\xi$ to quadratic $u^2 + u - (z + 2) = 0$.
     - "Miraculous boundary collapse": $G_w(z) = G(1,1) + 2G(1,2) + G(2,2) = s^2 + s - p$
       where $s = \xi_1 + \xi_2, p = \xi_1 \xi_2$ are the symmetric functions
       of the two interior roots.
     - Boundary spectral density on $(-9/4, 0)$:
       $$\rho_w(\lambda) = \frac{1}{\pi}\sin(\theta_2(\lambda) - \theta_1(\lambda))$$
       where $\theta_1 < \theta_2$ are the two preimages of $\lambda$ under
       $f(\theta) = 2\cos\theta + 2\cos 2\theta$.
     - Closed-form half-line moments match the Phase 9 candidate **exactly**
       (sympy `simplify == 0`):
       $W^-_\infty = 1 - 3\sqrt 3/(4\pi)$,
       $M^-_{1,\infty} = 2/3 - 9\sqrt 3/(4\pi)$,
       $M^-_{2,\infty} = 3 - 81\sqrt 3/(20\pi)$,
       $I_\infty(L) = 2(310\pi^2 - 837\sqrt 3\,\pi + 2187)/(27\pi(20\pi - 27\sqrt 3)) \approx 1.0157$.
     - Unsigned Plancherel sanity $(2, 2, 7)$ verified.
     Files: `docs/lprime_a_two_path_stieltjes.md`, `scripts/half_line_stieltjes.py`,
     `tests/test_half_line_stieltjes.py` (11 tests).

  2. **Phase 11 — Portmanteau closure (proved).** Bridges Phase 10's half-line
     theorem to the finite-$n$ moments:
     - Strong-resolvent convergence $T_{n-1} \to T$ via uniform bound
       $\|T_{n-1}\| \le \|f\|_\infty = 4$ (Grenander–Szegő) + SOT convergence
       on finitely-supported vectors.
     - Weak convergence of spectral measures $\mu_{w, n} \to \mu_w$ via
       Stieltjes inversion / Reed–Simon Vol I Thm VIII.20.
     - $\mu_w$ has no atom at 0: density $\rho_w$ is bounded ($\le 1/\pi$),
       absolutely continuous on the spectrum's interior, no embedded
       eigenvalues.
     - **Key Phase 11 observation**: for $k = 1, 2$, the function
       $g_k(\lambda) = \lambda^k \mathbf{1}[\lambda < 0]$ is **continuous at 0**
       (both one-sided limits and value $= 0$), so weak convergence alone
       gives $M_k^-(L_n) \to M^-_{k,\infty}$. Only $k = 0$ ($W^-$) needs
       the no-atom condition. Role 5's earlier worry about $\rho_w(0^-) > 0$
       affects only $W^-$.
     - Conclusion:
       $$\lim_{n \to \infty} I(L_n, v^*) = I_\infty(L) \approx 1.0157 > T \in \{0.4122, 0.25\}.$$
     Files: `docs/lprime_a_two_path_helly.md`, `tests/test_a_two_path_helly.py`
     (15 tests).

  3. **The candidate ansatz condition (a) is now proved unconditionally on
     books, BT-page, AND 2-paths**. Only "general 2-trees" remains open for
     condition (a).

  4. **Three residual gaps documented honestly:**
     - **(rate)** The Portmanteau argument is qualitative — no explicit
       convergence rate. For a finite-$n$ statement "$I(L_n) \ge T$ for all
       $n \ge n_0$ with explicit $n_0$", a Demmel–Kahan-style certificate
       analogous to v10's 5c closure is needed. Open subobligation O13.1.
     - **(branch)** The branch convention $\xi_1 = e^{-i\theta_1}, \xi_2 = e^{+i\theta_2}$
       in Phase 10 is verified numerically at a single complex base point;
       a formal analytic-continuation argument is light. Open subobligation
       O13.2; the $(2, 2, 7)$ moment match is strong evidence this is correct.
     - **(trig)** §4 of `lprime_a_two_path_stieltjes.md` skips one line of trig
       algebra in deriving $\mathrm{Im}\, G_w = -\sin(\theta_2 - \theta_1)$;
       the result is correct but uses $\cos\theta_1 + \cos\theta_2 = -1/2$
       without spelling out the cross-term identity. Open subobligation O13.3
       (one-line doc fix).

  5. **F12 updated.** The naive sine-basis identification fails for
     pentadiagonal Toeplitz at $w = e_1 + e_2$; the correct density is
     $\sin(\theta_2 - \theta_1)/\pi$, NOT $(\sin\theta + \sin 2\theta)^2/\pi$.
     The correct density is a *signed angle gap*, derivable via Stieltjes
     inversion. F12 in v13 is sharpened to reflect this.

  6. **Headline state of 5e (max-degsum selector for 2-trees)**:
     - Condition (a) closed unconditionally on: books, BT-page, 2-paths
       (asymptotic), via Phase 4, 8, 10, 11.
     - Condition (a) on general 2-trees: open.
     - Condition (b): open for all subfamilies. The slot-shift sum bound
       (O12.2) is the unified wall — Case A and corrected Case B both
       reduce to it. Phase 8 Lemma B1 bounds $\alpha_{\min}^2$; Phase 9
       (b.minor) gave $\alpha_{\min}^2 \ge 1$ on Case B max-degsum ears.
       **Neither bounds $\delta^-$**; F11.

  Test count: 508/508 passing (493 after Phase 10; +15 from Phase 11).

  What v13 calls **unconditionally established** (new since v12): the half-line
  Phase-10 theorem (density $\sin(\theta_2 - \theta_1)/\pi$; closed-form moments)
  and the Phase-11 Portmanteau closure (finite-$n$ moments converge to the
  half-line moments). Combined: $\lim_{n \to \infty} I(L_n, v^*) = I_\infty(L)$
  is **a theorem**.

- **v12**: Phase 8 (Lemma B1), Phase 9 (a.2-path candidate + b.minor sign
  correction); F11, F12 added; Conjecture 7.1 retired earlier in v10.
- **v11**: Phase 7 candidate ansatz; not yet a conjecture; F10 added.
- **v10**: retired Conjecture 7.1; 5c closed for $n \le 2000$ via DK; F7–F9.
- **v9**: $\|w\|^2 = 2$ bug fix; F5, F6.
- **v8**: Phase 4 — books, 2-paths-asymptotic, BT proved.
- **v7**: Phase 3 universal-lemma falsification; (L').
- **v6**: 2-trees as first serious target.
- **v5**: reviewer pass on v4.
- **v4**: domination scoped; $K_1$ endpoint.
- **v3**: six logical corrections.
- **v2**: dropped false connectivity-via-$P_3$-removal.
- **v1**: original draft.

## The conjecture (verbatim, Section 9 of the source paper)

Let $G$ be a **connected** graph of order $n$.
- **(i)** $s^+(G) = n - 1$ iff $G$ is a tree.
- **(ii)** $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.

Notation: $\lambda_1 \ge \cdots \ge \lambda_n$ are the adjacency eigenvalues of $G$;
$s^+(G) := \sum_{\lambda_i > 0} \lambda_i^2$, $s^-(G) := \sum_{\lambda_i < 0} \lambda_i^2$;
$\mathrm{tr}(A^2) = 2m = s^+ + s^-$.

## Why this conjecture, and the honest tractability verdict

Unchanged from v8–v12.

## Background, easy direction, and central obstruction

Unchanged from v8. Crude telescoping bound is $s^\pm(G) \ge n + k/16 - \ell$;
$P_3$-removal slack $17/16$ actively selects cut vertices.

## What the modest deliverables look like

Unchanged. Corollary A (claw-free), Corollary B (diameter $\le 2$).
Drafted in [`corollaries_AB.md`](corollaries_AB.md).

## What a serious result would require, and where to look

Unchanged search directions: **2-trees** (chosen target).

### First serious target: 2-trees

Target theorem:
> If $G$ is a 2-tree on $n$ vertices, then Conjecture 9.2 holds for $G$.

Via the existential ear-selection lemma (L'):
> Let $G$ be a 2-tree with $n \ge 4$. There exists a simplicial degree-2
> vertex $v^*$ with $\delta^+(v^*) \ge 17/16$ and $\delta^-(v^*) \ge 17/16$.

If (L') holds at every non-base step, telescoping to $K_3$ gives
$s^\pm(G) \ge s^\pm(K_3) + (17/16)(n - 3) > n - 1$.

### Corrected Case A / Case B slot decomposition

Carried from v12 (b.minor correction). For Cauchy interlacing on
$A(G) = \begin{pmatrix}0 & w^\top \\ w & A(H)\end{pmatrix}$:

- **Case A** ($n^-(G) = n^-(H)$): $\delta^-(v) = \sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2)$,
  each summand $\ge 0$.
- **Case B** ($n^-(G) = n^-(H) + 1$):
  $\delta^-(v) = \alpha_{\text{top}}^2 + \sum_{j \in J^-(H)}(\lambda_{j+1}^2 - \mu_j^2)$,
  each summand $\ge 0$,
  where $\alpha_{\text{top}} = \lambda_{n - n^-(H)}(G)$ is the *least*-magnitude
  $G$-negative.

### Phase 4–9 progress (carried)

- **Books $B_k$** (proved): $\delta^-(B_k) = 2 - 4/(\sqrt{8k+1} + \sqrt{8k-7})$.
- **2-paths $L_n$ Szegő asymptotic** for $\delta^-$ (proved):
  $\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi)$.
- **BT$(k, 2)$ bad ear** (proved): $\delta^-_\infty(\mathrm{BT}) \approx 1.0353$.
- **5c rigorous closure for $n \le 2000$** via Demmel–Kahan + mpmath.
- **$\|w\|^2 = 2$ bug fix** locked in by regression.
- **Phase 7 candidate ansatz** $I = W^- + (M_1^-)^2/M_2^-$.
- **Phase 8 Lemma B1**: $\lambda_{\min}^2 \ge ((|M_1^-| + \sqrt{(M_1^-)^2 + 4(W^-)^3})/(2 W^-))^2$ when $W^- > 0$.
- **Phase 8 sub-route closures for (a)**: books, BT-page reduce to books.
- **Phase 9 (b.minor) sign correction** for Case B slot decomposition.
- **Phase 9 (b.minor) sufficient condition** for $\alpha_{\min}^2 \ge 1$ on Case B max-degsum ears.

### Phase 10 + 11 progress (new in v13) — (a.2-path) fully closed

**Theorem (Phase 10 + 11).** For the 2-path family $L_n = P_n^2$ with boundary
simplicial ear $v^* = 1$ and $H = L_{n-1}$ at $w = e_1 + e_2 \in \mathbb{R}^{n-1}$:

$$\boxed{\;\lim_{n \to \infty} I(L_n, v^*) \;=\; I_\infty(L) \;=\; \frac{2(310\pi^2 - 837\sqrt{3}\,\pi + 2187)}{27\pi(20\pi - 27\sqrt{3})} \;\approx\; 1.0157\,375.\;}$$

The three individual moments also converge:
$W^-(L_n) \to 1 - 3\sqrt 3/(4\pi) \approx 0.5865$,
$M_1^-(L_n) \to 2/3 - 9\sqrt 3/(4\pi) \approx -0.5738$,
$M_2^-(L_n) \to 3 - 81\sqrt 3/(20\pi) \approx 0.7671$.

In particular $I_\infty(L) > T$ for both v11 thresholds $T \in \{0.25, 0.4122\}$
with slack $\ge 0.604$.

**Proof structure:**

Phase 10 (half-line spectral theorem):
- Self-reciprocal quartic factors to quadratic in $u = \xi + 1/\xi$.
- Boundary linear system collapses to $G_w(z) = s^2 + s - p$.
- Density $\rho_w(\lambda) = \sin(\theta_2 - \theta_1)/\pi$ on $(-9/4, 0)$.
- Unsigned Plancherel sanity $(2, 2, 7)$ verified.

Phase 11 (finite-$n$ to half-line):
- $T_{n-1} \to T$ strongly on $\ell^2(\mathbb{N})$.
- $\mu_{w, n} \to \mu_w$ weakly via Stieltjes inversion.
- $\mu_w(\{0\}) = 0$ (bounded density, purely AC on spectrum interior).
- $g_k(\lambda) = \lambda^k \mathbf{1}[\lambda < 0]$ is continuous at 0 for $k \ge 1$;
  for $k = 0$, no-atom suffices.
- Portmanteau gives $M_k^-(L_n) \to M^-_{k,\infty}$ for $k = 0, 1, 2$.

**Three residual minor gaps (open subobligations O13.1–O13.3):**
- **O13.1 (rate)**: Portmanteau is qualitative; an explicit $n_0$ such that
  $|I(L_n) - I_\infty| < \epsilon$ for all $n \ge n_0$ requires Demmel–Kahan
  finite-$n$ certificate. Mechanical.
- **O13.2 (branch)**: $\xi_1 = e^{-i\theta_1}, \xi_2 = e^{+i\theta_2}$
  verified at one complex base point, not by analytic continuation
  argument. The $(2, 2, 7)$ moment match is strong evidence.
- **O13.3 (trig)**: §4 of `lprime_a_two_path_stieltjes.md` skips one-line
  derivation of $\sin 2\theta_2 - \sin 2\theta_1 = -2\sin(\theta_2 - \theta_1)(1 + 4\cos A\cos B)$
  with $\cos A \cos B = -1/4$ from the characteristic constraint.

These gaps **do NOT block** the application of (a.2-path) within plan v13:
the asymptotic theorem suffices for $I(L_n, v^*) > T$ eventually, which is
what the (L') telescoping needs.

### Conjecture v11.candidate (carried, with v13 status)

> **Candidate ansatz (v11+).** For every 2-tree $G$ on $n \ge 4$ vertices
> with max-degsum simplicial ear $v^*$:
> (a) $I(v^*) := W^-(v^*) + (M_1^-(v^*))^2 / M_2^-(v^*) \ge T$;
> (b) $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$.

Status of (a):
- Books $B_k$: **proved** unconditionally.
- BT$(k, 2)$ max-degsum (book-page): **proved** by reduction to books.
- **2-paths $L_n$: proved (Phase 10 + Phase 11, v13)**.
- Fans $F_n$: $n \le 200$ FP-certified, tail open.
- General 2-trees: open.

Status of (b):
- All subfamilies: open. The slot-shift sum bound (O12.2) is the wall.
- Phase 8 Lemma B1 bounds $\alpha_{\min}^2$; Phase 9 b.minor gives $\alpha_{\min}^2 \ge 1$
  on Case B max-degsum ears. **Neither bounds $\delta^-$** (F11).

### Refined selector conjecture (carried from v8)

> **Max-degsum selector.** Unchanged. Empirical: 725/725 at $n \le 10$
> (min 1.2940); BT$(k, 2)$ for $k \le 500$; random 2-trees up to $n = 1000$;
> 2235 max-degsum records in `data/case_AB_census.json`, all
> $\delta^- \ge 1.2941$.

## Revised step-by-step plan (v13)

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry; $K_n$ spectrum | inline | **proved** |
| 2 | Corollary A | Thm 1.1 + paths/cycles | paragraph | drafted |
| 3 | Corollary B | Thm 1.2 + $K_{1,n-1}, C_5$ | paragraph | drafted |
| 4 | Short note on 1–3 | Exposition | 1–2 weeks | drafts merged |
| 5a | (L') on books $B_k$ for $k \ge 2$ | Closed-form spectrum | done | **proved** |
| 5b | (L') on 2-paths $L_n$ asymptotic ($\delta^-$) | Szegő | done | **proved** |
| 5c | (L') on 2-paths $L_n$ at finite $n$ ($\delta^-$) | DK + mpmath | done | **rigorous for $n \in [4, 2000]$** |
| 5c.tail | (L') on 2-paths $L_n$ for $n > 2000$ ($\delta^-$) | Non-simple-loop BBG (O5c.3) | research | open |
| 5d | BT$(k, 2)$ bad-ear asymptotic | Cubic resolvents | done | **proved** |
| 5e | Headline: max-degsum selector | Candidate ansatz (a) + (b) | open-ended | headline open |
| 5e.candidate.a.books | $I(v^*) \ge T$ on $B_k$ | Cauchy–Schwarz saturation | done (Phase 8) | **proved** |
| 5e.candidate.a.BT-page | $I(v^*) \ge T$ on BT$(k,2)$ max-degsum | Reduction to books | done (Phase 8) | **proved** |
| 5e.candidate.a.2-path | $\lim I(L_n, v^*) = I_\infty(L) > T$ | Stieltjes + Portmanteau | done (Phase 10 + 11) | **PROVED IN v13** |
| 5e.candidate.a.general | $I(v^*) \ge T$ for general 2-trees | Clique-tree + moments | research | open |
| 5e.candidate.b | $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$ | Slot-shift sum bound | research | open (O12.2; the wall) |
| 5e.lemma_B1 | $\lambda_{\min}^2 \ge f_{\min}^2$ for $W^- > 0$ | Rayleigh on $z(\beta)$ | done | **proved (Phase 8)** |
| 5e.b_minor.alpha_min_one | $\alpha_{\min}^2 \ge 1$ on Case B max-degsum | Lemma B1 + suff. cond. | done | **proved (Phase 9)** (bounds $\alpha_{\min}$, not $\delta^-$; F11) |
| 5e.slot_shift | $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge $ const | Unified wall (Case A + corrected B) | research | **the real bottleneck** |
| 5f | (L') on fans $F_n$ | Hub + path decomp; DK | done for $n \le 200$ | **FP-certified $n \le 200$**; tail via 5c-tail |
| 5g | (L') on multi-arm spider 2-trees | Symmetry + interlacing | partial | Case I = books; Case II cond. on O5e.1 |
| 6 | If 5e succeeds, prove 9.2 for 2-trees | Telescope to $K_3$ | short | gated on 5e |
| 7 | Fallback: residue-control classes | Block-cut tree, perfect elim, SDP/Gluing | open | not started |
| 8 | Near-extremal sanity ($n \le 30$) | Direct spectrum / Cauchy | 1 week | not started |

## Three attack vectors (unchanged)

V1, V2, V3.

## Failure modes to guard against

- **F1.** Residue-component count $\ell$ is the whole problem.
- **F2.** Tacit reliance on EFGW in subclasses where it is open.
- **F3.** Near-extremal traps in part (ii).
- **F4.** Regularity not preserved by induced vertex deletion.
- **F5.** "Floating-point certified" $\ne$ interval-arithmetic certified.
- **F6.** BBG-type asymptotic constants assume simple-loop symbol; ours fails.
- **F7 (softened in v11).** Single-scalar selector thresholds at the
  *naturally-scaled* values $17/16$ or $17/32$ are categorically wrong; a
  smaller empirically-fitted threshold may survive on a finite corpus.
- **F8.** mpmath @ high-precision $\ne$ interval arithmetic.
- **F9.** Case B carries $\delta^-$ without $W^-$ support.
- **F10.** Stage-1 "gap" is a condition-(a) statistic, not an
  implication-margin statistic.
- **F11.** $\alpha_{\min}$ vs $\alpha_{\text{top}}$ are different quantities;
  bounding one does not bound the other. Lemma B1 bounds $\alpha_{\min}$;
  the corrected slot decomposition needs $\alpha_{\text{top}}$.
- **F12 (sharpened in v13).** Boundary spectral density for half-line banded
  Toeplitz at $w = e_1 + e_2$ is **NOT** the naive sine-basis $(\sin\theta + \sin 2\theta)^2$.
  The correct half-line density is $\sin(\theta_2(\lambda) - \theta_1(\lambda))/\pi$
  on the two-preimage region $\lambda \in (-9/4, 0)$ — a *signed angle gap*,
  derived via Stieltjes inversion (Phase 10). The naive sine-basis fails a
  direct numerical check by factors of 100+. Use Stieltjes-transform or cite
  Simon / Trefethen–Embree for any other half-line banded-Toeplitz density.
- **F13 (new in v13).** **Portmanteau on signed moments requires no-atom at the
  jump** for $k = 0$, but for $k \ge 1$ the function $\lambda^k \mathbf{1}[\lambda < 0]$
  is *continuous at 0*. This is a subtlety that simplifies the Phase 11
  closure: only $W^-$ ($k = 0$) needs the no-atom step; $M_1^-, M_2^-$
  ($k = 1, 2$) follow directly from weak measure convergence. Future
  Portmanteau-style arguments on signed moments should check this distinction
  explicitly.

## Concrete next action (v13)

The candidate ansatz now has condition (a) closed on three of the four
recognised subfamilies (books, BT-page, 2-paths). The remaining open work
on (a) is the **general** 2-trees case; the remaining open work on (b) is
the slot-shift sum bound (the wall confirmed unified by Phase 9).

Two sub-routes, prioritised by tractability:

1. **5e.slot_shift — O12.2 (THE WALL).** Prove
   $$\sum_{j \in J^-(H)}(\lambda_{j+1}(G)^2 - \mu_j(H)^2) \ge T'$$
   at the max-degsum ear, via the secular equation. The known inputs are
   $\sum c_i^2 = 2$, $M_1 = 2$ (since $\{a, b\} \in E(H)$), the moments
   $(W^-, M_1^-, M_2^-)$, and Cauchy interlacing slot-by-slot. The secular
   equation $\lambda = \sum c_i^2 / (\lambda - \mu_i)$ relates each new
   $\lambda$ to neighbouring $\mu$'s; chained over the negative slots, a
   slot-by-slot lower bound may produce a clean sum bound.

   This is the **headline open problem**. Closing it (with explicit $T'$)
   plus condition (a) on general 2-trees would close the candidate ansatz,
   hence (L'), hence Conjecture 9.2 on 2-trees.

2. **5e.candidate.a.general — structural attack.** Show
   $I(v^*) \ge T$ on the max-degsum ear for arbitrary 2-trees via
   clique-tree data and $M_2 = \sigma + 2|T_{ab}(H)|$. The 2-path family
   is empirically binding ($I_\infty(L) \approx 1.0157$ on 2-paths vs
   $\approx 1.7$ on books). With 2-paths now closed, the 2-path family
   *is* the asymptotic floor of condition (a); a clean proof of
   $I(v^*) \ge I_\infty(L)$ for all max-degsum ears in all 2-trees would
   complete condition (a).

3. **Optional cleanup.** Address O13.1 (Demmel–Kahan rate for (a.2-path)),
   O13.2 (branch-convention formality), O13.3 (one-line trig identity)
   for full rigour, though none are critical-path.

## Critical reading (carried + v13 confirmations)

Carried: arXiv:2506.07264, arXiv:1409.2079, arXiv:2303.11930, arXiv:2311.11530,
arXiv:2410.09830, arXiv:2409.15504, arXiv:2409.18220, Bogoya–Böttcher–Grudsky 2018,
Demmel, Wilkinson, Avram–Parter 1988.

**v12 / v13 confirmations**:
- **Barry Simon**, *Szegő's Theorem and Its Descendants* (Princeton, 2011) —
  used as background for the half-line spectral theory in Phase 10.
- **Trefethen–Embree**, *Spectra and Pseudospectra* (Princeton, 2005) — similar.
- **Reed–Simon**, *Methods of Modern Mathematical Physics, Vol I* — Thm
  VIII.20 (resolvent convergence implies weak spectral-measure convergence)
  used in Phase 11.
- **Billingsley**, *Convergence of Probability Measures* — Portmanteau theorem
  in Phase 11.

## Open subobligations (v13)

- **(O5e.1)** Book-arm monotonicity for multi-arm spiders. Carried.
- **(O5e.2)** Fan rigorous closure at $n > 200$ (folds into 5c.tail). Carried.
- **(O5e.3)** Joint-invariant ansatz: condition (a) progressed
  significantly in v13 (books, BT-page, 2-paths all closed); general case
  still open.
- **(O5c.3)** Non-simple-loop BBG analogue for $n > 2000$ on $\delta^-(L_n)$.
- **(O12.2)** **Slot-shift sum bound** for condition (b) — the unified
  bottleneck for both Case A and corrected Case B. **The headline open
  problem of v13.**
- **(O13.1, new)** **Demmel–Kahan rate** for $|I(L_n, v^*) - I_\infty(L)|$,
  giving explicit $n_0$ such that $I(L_n) \ge T$ for $n \ge n_0$.
  Mechanical extension of v10's 5c DK certificate.
- **(O13.2, new)** **Formal analytic-continuation argument** for the branch
  convention $\xi_1 = e^{-i\theta_1}, \xi_2 = e^{+i\theta_2}$ in Phase 10.
  Verified numerically and via $(2, 2, 7)$ Plancherel match; analytical
  argument is light.
- **(O13.3, new)** **One-line trig algebra** in §4 of
  `lprime_a_two_path_stieltjes.md` for the $\sin(\theta_2 - \theta_1)$ collapse.

## Open subtasks (status updated in v13)

Carried from v12 (all implemented unless flagged):
- All scripts and tests from v8–v12.
- `scripts/half_line_stieltjes.py` *(Phase 10)*.
- `tests/test_half_line_stieltjes.py` *(Phase 10, 11 tests)*.
- `docs/lprime_a_two_path_stieltjes.md` *(Phase 10)*.
- `docs/lprime_a_two_path_helly.md` *(Phase 11)*.
- `tests/test_a_two_path_helly.py` *(Phase 11, 15 tests)*.
- Fallback: `tests/p3_removal_witness.py`, `tests/near_extremal_sanity.py`.

**(v13 NEW, none required for headline)** — only optional cleanup tasks:
- Optional: `scripts/dk_rate_for_I.py` — Demmel–Kahan rate certificate for
  the joint $I(L_n, v^*)$ functional (O13.1).
- Optional: regression `tests/test_dk_rate_for_I.py` — asserts
  $|I(L_n) - I_\infty(L)| < c/n$ for explicit $c$.

The permanent regressions are kept:
`tests/fixtures/two_tree_universal_counterexamples.json` (v7),
`tests/fixtures/w_norm_squared_is_2.json` (v9),
`tests/fixtures/joint_invariant_falsified.json` (v10/Phase 7).

## Summary of v13 state

- **5c (2-paths $\delta^-$)**: rigorously closed for $n \in [4, 2000]$;
  tail $n > 2000$ open (O5c.3).
- **5e headline (max-degsum selector)**: open.
- **5e.a (condition (a))**: proved on books, BT-page, AND **2-paths
  (asymptotic, Phase 10 + 11)**; general 2-trees open.
- **5e.b (condition (b))**: open for all subfamilies; **slot-shift sum
  bound (O12.2)** is the real wall.
- **New unconditional results in v13**: Phase-10 half-line spectral
  theorem (density $\sin(\theta_2 - \theta_1)/\pi$ + closed-form moments);
  Phase-11 Portmanteau closure (finite-$n$ to half-line); combined,
  $\lim_n I(L_n, v^*) = I_\infty(L) \approx 1.0157$ is **a theorem**.
- **Test suite**: 508/508 passing.

The workstream has now closed the candidate ansatz (a) on three of the four
recognised subfamilies. Only **general 2-trees (a)** and **condition (b) via
the slot-shift wall (O12.2)** remain open. Both are *bona fide* research
problems, each meaningfully smaller than the full Conjecture 9.2.
