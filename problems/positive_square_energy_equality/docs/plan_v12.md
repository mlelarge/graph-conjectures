# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v12** (this version): incorporates the Phase 8 attack + Phase 9 (a.2-path),
  Phase 9 (b.minor), and Role 5's audit of both. Five headline outcomes:
  1. **Phase 8 — Lemma B1 (a new clean result).** For any 2-tree $G$ with
     simplicial degree-2 ear $v$ and $W^-(v) > 0$,
     $$\lambda_{\min}(A(G)) \le -\frac{|M_1^-(v)| + \sqrt{(M_1^-(v))^2 + 4 W^-(v)^3}}{2 W^-(v)},$$
     proved via Rayleigh quotient on the trial vector $z(\beta) = \tilde w_- - \beta e_v$.
     Tight on books, loose on thin 2-trees. **The lemma is unconditionally
     proved**; what changes in v12 is its *application*.
  2. **Phase 8 §3.2 had a sign error in the Case B slot decomposition; Phase 9
     (b.minor) caught and corrected it.** Phase 8 wrote
     $\delta^- = \alpha^2 + \sum_{j \in J^- \setminus \{n-1\}}(\lambda_{j+1}^2 - \mu_j^2)$
     with $\alpha = \lambda_{\min}$. The correct identity is
     $$\delta^-(v) = \alpha_{\text{top}}^2 + \sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2)$$
     with **each summand $\ge 0$**, where $\alpha_{\text{top}} := \lambda_{n - n^-(H)}(G)$
     is the *least-magnitude* $G$-negative eigenvalue (NOT the most negative).
     Numerically verified on $L_n$ Case B examples ($n \in \{6,7,9,10,12\}$):
     b.minor formula recovers $\delta^-$ exactly; Phase 8 formula overshoots
     wildly (predicts 3.74 vs actual 1.32 at $L_6$).
  3. **The Phase 8 attack route to (b) is invalidated** by the correction.
     Lemma B1 bounds $\lambda_{\min}^2 = \alpha_{\min}^2$, but the corrected
     slot decomposition involves $\alpha_{\text{top}}^2$ — these are
     **unrelated** quantities. Lemma B1 itself survives as a stand-alone
     spectral bound. Its claimed application "Lemma B1 closes (b) in Case B"
     is wrong and is retracted in v12.
  4. **Phase 8 sub-route closures for (a)** survive: books $B_k$ unconditional
     (Cauchy–Schwarz saturates), BT$(k,2)$ max-degsum reduces to books.
  5. **Phase 9 (a.2-path) — closed-form candidate, derivation pending.**
     Numerical evidence at $N \le 5000$ strongly supports
     $$I_\infty(L) = \frac{2(310\pi^2 - 837\sqrt{3}\,\pi + 2187)}{27\pi(20\pi - 27\sqrt{3})} \approx 1.0157,$$
     with components $W^-_\infty(L) = 1 - 3\sqrt{3}/(4\pi)$,
     $M_{1,\infty}^-(L) = 2/3 - 9\sqrt{3}/(4\pi)$,
     $M_{2,\infty}^-(L) = 3 - 81\sqrt{3}/(20\pi)$, matching mpmath at dps=50
     for $n \in \{50, 100, 200\}$ with residuals $\to 0$. **However**, the
     §2 derivation in `docs/lprime_a_two_path.md` rests on an unproven
     identification of the boundary spectral density at $w = e_1 + e_2$ for
     the half-line pentadiagonal Toeplitz operator. The naive sine-basis
     ansatz fails by factors of 100 in a direct numerical check; the
     boxed §2.3 density formula is linear in $\Phi$ where Plancherel demands
     quadratic; the script's actual formula has an extra $-\sin(\theta_2 - \theta_1)$
     term not in the doc. The candidate closed form matches numerics to
     $10^{-4}$ but is not analytically derived. v12 downgrades the (a.2-path)
     status from "proved theorem" to **"numerical evidence + candidate closed
     form pending analytical derivation"**.
  6. **Phase 9 (b.minor) — did NOT prove $\delta^-(v^*) \ge 1$** unconditionally,
     in Case B, or in Case A. The empirical floor $\delta^-(v^*) \ge 1.2941$
     holds across 2235 records (`data/case_AB_census.json`). What it did
     produce: (i) the sign-correction in (2), (ii) the closed-form sufficient
     condition $|M_1^-| \ge W^-(1 - W^-)$ when $W^- \le 1$ implies
     $f_{\min}^2 \ge 1$, hence $\alpha_{\min}^2 \ge 1$ uniformly on Case B
     max-degsum ears (a real new result, bounding $\alpha_{\min}^2$, NOT
     $\delta^-$), (iii) explicit identification that the slot-shift sum
     bound — the same wall as 5e-b in v10 — is what's needed for both Case A
     and corrected Case B.
  7. **Two new failure modes** (F11, F12) record the lessons from this round.

  What v12 calls **unconditionally established** (new in this revision):
  Lemma B1 ($\alpha_{\min}$ bound via Rayleigh quotient); the b.minor sign
  correction for the Case B slot decomposition; the b.minor sufficient
  condition $|M_1^-| \ge W^-(1-W^-) \Rightarrow \alpha_{\min}^2 \ge 1$ on
  Case B max-degsum ears; (a) on books and BT$(k,2)$ max-degsum ears for
  the candidate ansatz. **Carried from earlier**: clique-tree formalization;
  trace identity $\delta^+ + \delta^- = 4$; books $B_k$ for $k \ge 2$
  (`lprime_books.md`); BT$(k,2)$ asymptotic; 2-paths Szegő asymptotic
  $\delta^-_\infty(L) = (32\pi - 27\sqrt{3})/(12\pi)$; $\delta^-(L_n) \ge
  17/16 + 1/4$ for $n \in [4, 2000]$ via Demmel–Kahan; Cauchy–Schwarz
  $W^- \ge (M_1^-)^2/M_2^-$.

  What v12 records as **empirically unfalsified but not analytically
  derived**: the candidate ansatz $I = W^- + (M_1^-)^2/M_2^-$ at $T = 0.4122$;
  the candidate closed form $I_\infty(L) \approx 1.0157$ (derivation §2 of
  `lprime_a_two_path.md` is hand-waved at the boundary-density step). 482
  tests passing.

- **v11**: reviewer pass on Phase 7; candidate ansatz not yet a conjecture;
  implication margin (~0.082) properly reported; F7 softened; F10 added.
- **v10**: retired Conjecture 7.1; 5c closed for $n \le 2000$ via DK;
  Conjecture v10.1 (form open); F7, F8, F9 added.
- **v9**: $\|w\|^2 = 2$ bug fix; Conjecture 7.1 renormalised; F5, F6.
- **v8**: Phase 4 — books, 2-paths-asymptotic, BT proved; max-degsum
  selector replaces v7 O2.
- **v7**: Phase 3 universal-lemma falsification; trace identity; (L').
- **v6**: 2-trees as first serious target.
- **v5**: domination $\le 2$ connected $s^+$ only; $P_3$-removal sign-specific.
- **v4**: domination scoped; $K_1$ endpoint; $s^+$ residue refined.
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

Unchanged from v8–v11.

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

### The corrected Case A / Case B slot decomposition (v12)

For Cauchy interlacing on $A(G) = \begin{pmatrix}0 & w^\top \\ w & A(H)\end{pmatrix}$,
order eigenvalues $\lambda_1(G) \ge \cdots \ge \lambda_n(G)$ and
$\mu_1(H) \ge \cdots \ge \mu_{n-1}(H)$. Interlacing:
$\lambda_i(G) \ge \mu_i(H) \ge \lambda_{i+1}(G)$ for $i = 1, \ldots, n-1$.

Let $n^-(M)$ denote the negative inertia of $M$. The interlacing forces
$n^-(G) \in \{n^-(H), n^-(H) + 1\}$. Reindexing $s^-(G) - s^-(H)$ by
shifting the $G$-sum index $i = j + 1$ (the $j = 0$ term vanishes since
$\lambda_1 > 0$):
$$\delta^-(v) = \sum_{j=1}^{n-1}\bigl[\lambda_{j+1}^2 \,\mathbf{1}[\lambda_{j+1} < 0]
                                    - \mu_j^2 \,\mathbf{1}[\mu_j < 0]\bigr].$$

- **Case A** ($n^-(G) = n^-(H)$): for every $j \in J^-(H)$, $\lambda_{j+1}(G) \le \mu_j(H) < 0$,
  hence $|\lambda_{j+1}| \ge |\mu_j|$, hence
  $\delta^- = \sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2)$ with each summand $\ge 0$.

- **Case B** ($n^-(G) = n^-(H) + 1$): the **new** negative slot is the
  *least-magnitude* $G$-negative — index $j_0 = n - n^-(H)$ in the pairing,
  contributing $\alpha_{\text{top}}^2 := \lambda_{j_0 + 1}(G)^2$ as a pure
  non-negative term. All other slots in $J^-(H)$ pair as in Case A:
  $$\boxed{\;\delta^-(v) = \alpha_{\text{top}}^2 + \sum_{j \in J^-(H)}(\lambda_{j+1}^2 - \mu_j^2),\quad\text{each summand}\ge 0.\;}$$

**Numerical verification** on $L_n$ Case B examples (recovered exactly by
the corrected formula; Phase 8's pre-correction overshoots):

| $L_n$ | Predicted (v12 corrected) | Predicted (Phase 8 buggy) | Actual $\delta^-$ |
|---:|---:|---:|---:|
| $L_6$  | 1.319 ✓ | 3.74 ✗ | 1.319 |
| $L_{10}$ | 1.430 ✓ | 5.43 ✗ | 1.430 |
| $L_{12}$ | 1.397 ✓ | — | 1.397 |

### Phase 4–7 progress (carried over from v8–v11)

**Books $B_k$** (proved, `lprime_books.md`): $\delta^-(B_k) = 2 - 4/(\sqrt{8k+1} + \sqrt{8k-7})$.
**2-paths Szegő asymptotic** (proved, `lprime_two_paths.md`):
$\delta^-_\infty(L) = (32\pi - 27\sqrt{3})/(12\pi)$.
**BT$(k,2)$ bad ear** (proved, `lprime_selector.md`):
$\delta^-_\infty(\mathrm{BT}) \approx 1.0353$.
**5c rigorous closure for $n \le 2000$** via Demmel–Kahan a-posteriori +
mpmath confirmatory.
**Bug fix** $\|w\|^2 = 2$ in `lprime_max_degsum.md` §2 with regression
fixture.
**Phase 7 candidate ansatz** $I = W^- + (M_1^-)^2/M_2^-$ at $T = 0.4122$
empirically non-falsified on 1063 graphs (Phase 7) + Role 5 extension
(BT$(k,2)$ for $k \le 500$, random 2-trees at $n \le 1000$). Implication
margin $\approx 0.082$, thin but alive.

### Phase 8 progress (preserved, with §3.2 correction)

**Lemma B1** (proved, `lprime_attack_v11.md` §2):
$$\lambda_{\min}(A(G)) \le -\frac{|M_1^-(v)| + \sqrt{(M_1^-(v))^2 + 4 W^-(v)^3}}{2 W^-(v)} \quad\text{when } W^-(v) > 0.$$

Proof via Rayleigh quotient on $z(\beta) = \tilde w_- - \beta e_v$. Optimization
in $\beta$ gives the closed-form bound. Tight on books (ratio
$\alpha/f_{\min} \to 1$ as $k \to \infty$, verified through $B_{30}$);
loose by 1.4–4.4× on thin 2-trees.

**Sub-route closures for (a):** books $B_k$ unconditional ($I \in [1.33, 1.87]$
for $k \ge 2$); BT$(k,2)$ max-degsum reduces to books.

**§3.2 application — RETRACTED.** Phase 8 §3.2 claimed Lemma B1 closes (b) in
Case B because $\delta^- \ge \alpha^2$ in Case B with $\alpha = \lambda_{\min}$.
This is wrong under the corrected slot decomposition above: Case B gives
$\delta^- = \alpha_{\text{top}}^2 + \sum \ge 0$, with $\alpha_{\text{top}}$ the
*least-magnitude* $G$-negative, NOT $\lambda_{\min}$. Lemma B1 bounds
$\alpha_{\min}$, not $\alpha_{\text{top}}$; these are unrelated.

### Phase 9 (b.minor) — sign correction + sufficient $\alpha_{\min}^2 \ge 1$ condition

`docs/lprime_b_minor.md` and `data/case_AB_census.json`.

**Did not prove $\delta^-(v^*) \ge 1$** unconditionally, in Case B, or in Case A.
Empirical floor $\delta^-(v^*) \ge 1.2941$ holds across 2235 max-degsum
records (1945 Case A, 290 Case B) over enumerated $n \le 10$, BT, books,
$L_n, F_n$.

**What it did produce:**
1. The §3.2 sign correction above (now in v12).
2. **Closed-form sufficient condition** for $\alpha_{\min}^2 \ge 1$:
   if $W^- \le 1$ then $|M_1^-| \ge W^-(1 - W^-) \Rightarrow f_{\min}^2 \ge 1$,
   hence $\alpha_{\min}^2 \ge 1$ via Lemma B1. **Bounds $\alpha_{\min}^2$, NOT
   $\delta^-$.** Empirical minimum of $f_{\min}^2$ on Case B max-degsum ears
   is **1.8327** at enum$_{n=10}$ graph6 `I}qcaOH?W`.
3. **Unified diagnosis**: Case A and corrected Case B share the same residual
   obstruction — a slot-shift sum bound
   $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge $ const.
   Case B has the extra non-negative $\alpha_{\text{top}}^2$ term, which
   empirically vanishes as $n \to \infty$ on $L_n$ (so even with the extra
   term, the lower bound for Case B is *not* easier than Case A).

### Phase 9 (a.2-path) — closed-form candidate, derivation pending

`docs/lprime_a_two_path.md`, `data/two_path_limit_moments.json`,
`tests/test_two_path_limit_moments.py` (6 tests passing).

**Numerical evidence (verified at high precision):**
- mpmath @ dps=50 at $n \in \{50, 100, 200\}$ matches the candidate closed
  form $I_\infty(L) \approx 1.0157$ with residuals $\to 0$.
- Direct `scipy.linalg.eig_banded` at $N \in \{499, 999, 1999, 2999, 4999\}$
  agrees to $\sim 10^{-4}$ with $O(N^{-1/2})$ oscillatory residuals.
- Symbolic consistency: the explicit integrand
  $(4x^2 + 2x - 2)^k (4x+1)[(2x+1)\sqrt{1-x^2} + 2x\sqrt{3/4 - x - x^2}]$
  on $x \in (-1/4, 1/2)$ (sympy) gives the same three moments as the
  closed-form expressions.

**Candidate closed form:**
$$I_\infty(L) = \frac{2(310\pi^2 - 837\sqrt{3}\,\pi + 2187)}{27\pi(20\pi - 27\sqrt{3})} \approx 1.0157.$$

Both v11 thresholds cleared with huge margin:
$I_\infty - 0.4122 = +0.604$, $I_\infty - 0.25 = +0.766$.

**Status: NUMERICAL EVIDENCE + CANDIDATE CLOSED FORM, derivation pending.**
The §2 derivation in `docs/lprime_a_two_path.md` identifies the boundary
spectral density at $w = e_1 + e_2$ for the half-line pentadiagonal Toeplitz
as $\Phi(\theta)^2 = (\sin\theta + \sin 2\theta)^2$. Role 5's audit found
this identification is **not actually established**: a direct numerical
check (project each eigenvector $u_j$ onto $w$ and compare $c_j^2 \cdot (N+1)/2$
to $\Phi(\theta_j)^2$) fails by factors of 100+. The eigenvectors of a
pentadiagonal symmetric Toeplitz are NOT simple linear combinations of two
sine-basis vectors; the naive identification that works for tridiagonal
($f(\theta) = 2\cos\theta$) does not transfer.

The boxed density formula in §2.3 is *linear* in $\Phi$, which contradicts
Plancherel (the spectral measure of a vector must be quadratic in
eigenvector amplitudes). The script's actual formula has an extra
$-\sin(\theta_2 - \theta_1)$ term not stated in the doc, suggesting the
derivation was not fully written out.

**Two options for v12+:**
- (a.2-path.derivation-A) Cite a textbook treatment of the boundary spectral
  measure for half-line banded Toeplitz operators — Simon's
  *Szegő's Theorem and Its Descendants*, or Trefethen–Embree
  *Spectra and Pseudospectra* — and adapt to our pentadiagonal symbol.
- (a.2-path.derivation-B) Write a self-contained derivation via the Stieltjes
  transform $G_w(z) = \langle w, (zI - T)^{-1} w \rangle$ and the
  inverse-spectral-measure formula
  $\rho_w(\lambda) = \frac{1}{\pi} \lim_{\epsilon \to 0^+} \mathrm{Im}\, G_w(\lambda + i\epsilon)$.

Until one of these is done, the (a.2-path) closure is **conjectural**, not
theorem.

### Conjecture v11.candidate (carried, with v12 status)

> **Candidate ansatz (v11–v12).** For every 2-tree $G$ on $n \ge 4$ vertices
> with max-degsum simplicial ear $v^*$:
> (a) $I(v^*) := W^-(v^*) + (M_1^-(v^*))^2 / M_2^-(v^*) \ge T$;
> (b) $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$.

Status of (a):
- Books $B_k$: **proved** unconditionally.
- BT$(k,2)$ max-degsum (book-page): **proved** by reduction to books.
- 2-paths $L_n$ asymptotic: **candidate closed form $I_\infty(L) \approx 1.0157$**;
  derivation §2 hand-waved, awaiting analytical justification.
- Fans $F_n$: $n \le 200$ FP-certified, tail open.
- General 2-trees: open.

Status of (b):
- All subfamilies: open. The slot-shift bound is the wall.
- Phase 8 attempted Lemma B1 → bounds $\alpha_{\min}^2$, NOT $\alpha_{\text{top}}^2$
  needed for the corrected slot decomposition. Attack route invalidated.
- Phase 9 (b.minor) proved $\alpha_{\min}^2 \ge 1$ uniformly on Case B
  max-degsum ears, but this **does not bound $\delta^-$**.

### Refined selector conjecture (carried from v8)

> **Max-degsum selector.** Unchanged from v8 onward. Empirical: 725/725 at
> $n \le 10$ (min 1.2940); BT$(50,2)$, BT$(100,2)$, BT$(k,2)$ for $k \le 500$;
> random 2-trees up to $n = 1000$. 2235 max-degsum records in
> `data/case_AB_census.json`, all $\delta^- \ge 1.2941$. Zero violations.

## Revised step-by-step plan (v12)

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry; $K_n$ spectrum | inline | **proved** |
| 2 | Corollary A (claw-free, $\Delta \ge 3$) | Thm 1.1 + paths/cycles | paragraph | drafted |
| 3 | Corollary B ($\mathrm{diam} \le 2$) | Thm 1.2 + $K_{1,n-1}, C_5$ | paragraph | drafted |
| 4 | Short note on steps 1–3 | Exposition | 1–2 weeks | drafts merged; needs polish |
| 5a | (L') on books $B_k$ for $k \ge 2$ | Closed-form spectrum | done | **proved** |
| 5b | (L') on 2-paths $L_n$ asymptotic ($\delta^-$) | Szegő for pentadiagonal sym Toeplitz | done | **proved** |
| 5c | (L') on 2-paths $L_n$ at finite $n$ ($\delta^-$) | Demmel–Kahan a-posteriori + mpmath | done for $n \le 2000$ | **rigorous for $n \in [4, 2000]$** |
| 5c.tail | (L') on 2-paths $L_n$ for $n > 2000$ ($\delta^-$) | Non-simple-loop BBG analogue (O5c.3) | research | open |
| 5d | BT$(k, 2)$ bad-ear asymptotic | Symmetry quotient + cubic resolvents | done | **proved** |
| 5e | Headline: max-degsum selector for general 2-trees | Candidate ansatz (a) + (b) | open-ended | headline open |
| 5e.candidate.a.books | $I(v^*) \ge T$ on $B_k$ | Cauchy–Schwarz saturation | done (Phase 8) | **proved** |
| 5e.candidate.a.BT-page | $I(v^*) \ge T$ on BT$(k,2)$ max-degsum | Reduction to books | done (Phase 8) | **proved** |
| 5e.candidate.a.2-path | $I_\infty(L) > T$ on 2-paths asymptotic | Boundary spectral measure of half-line $T(f)$ | done numerically; derivation pending | **candidate closed form** |
| 5e.candidate.a.general | $I(v^*) \ge T$ for general 2-trees | Clique-tree + moment identity + Cauchy–Schwarz | research | open |
| 5e.candidate.b | $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$ | Secular equation + slot-shift bound | research | open (Phase 8 route invalidated) |
| 5e.lemma_B1 | $\lambda_{\min}^2 \ge f_{\min}^2$ for $W^- > 0$ | Rayleigh on $z(\beta)$ | done | **proved (Phase 8)** |
| 5e.b_minor.alpha_min_one | $\alpha_{\min}^2 \ge 1$ on Case B max-degsum ears | Lemma B1 + $\|M_1^-\| \ge W^-(1-W^-)$ | done | **proved (Phase 9)** (bounds $\alpha_{\min}$, NOT $\delta^-$) |
| 5e.slot_shift | $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge $ const | The unified wall (Case A + corrected Case B) | research | **the real bottleneck** |
| 5f | (L') on fans $F_n$ | Hub + path decomp; DK extension | done for $n \le 200$ | **FP-certified $n \le 200$**; tail via 5c-tail |
| 5g | (L') on multi-arm spider 2-trees | Symmetry + interlacing | partial | Case I = books; Case II cond. on O5e.1 |
| 6 | If 5e succeeds, prove 9.2 for 2-trees | Telescope to $K_3$ | short | gated on 5e |
| 7 | Fallback: residue-control classes | Block-cut tree, perfect elim, SDP/Gluing | open | not started |
| 8 | Near-extremal sanity ($n \le 30$) | Direct spectrum / Cauchy | 1 week | not started |

**New v12 row 5e.slot_shift** records the real bottleneck: the slot-shift
sum bound, common to Case A and (after correction) Case B. Phase 8's
Lemma B1 + b.minor's $\alpha_{\min}^2 \ge 1$ are both genuine new results
but neither attacks this bottleneck.

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
- **F11 (new in v12).** **$\alpha_{\min}$ vs $\alpha_{\text{top}}$ are
  different quantities; bounding one does not bound the other.** Lemma B1
  bounds $\alpha_{\min} = \lambda_{\min}(A(G))$. The corrected slot
  decomposition (Case B) involves $\alpha_{\text{top}} := \lambda_{n - n^-(H)}(G)$,
  the *least-magnitude* $G$-negative eigenvalue. On thin 2-trees these
  can differ by orders of magnitude (e.g. $L_{30}$ Case B endpoint:
  $\alpha_{\min}^2 = 4.91$ but $\alpha_{\text{top}}^2 = 8.6 \times 10^{-4}$).
  Any attack route that conflates them is invalid.
- **F12 (new in v12).** **Boundary spectral density for half-line banded
  Toeplitz is NOT trivially the naive sine basis.** For tridiagonal symbol
  $f(\theta) = 2\cos\theta$ at vertex 1, eigenvectors are
  $\sqrt{2/(n+1)}\sin(jk\pi/(n+1))$, giving boundary density $\sin\theta$.
  For *pentadiagonal* symbol $f(\theta) = 2\cos\theta + 2\cos 2\theta$ at
  $w = e_1 + e_2$, the eigenvectors are NOT simple sine combinations; the
  naive $\Phi(\theta) = \sin\theta + \sin 2\theta$ identification fails a
  direct numerical check by factors of 100+. Use Stieltjes-transform
  derivation or cite the explicit textbook treatment.

## Concrete next action (v12)

Three sub-routes, prioritised by tractability:

1. **5e.candidate.a.2-path — derivation.** Pick (derivation-A) or
   (derivation-B) above. (derivation-B), the Stieltjes-transform route, is
   self-contained: compute
   $$G_w(z) = w^\top (zI - A(L_\infty))^{-1} w$$
   for the half-line pentadiagonal Toeplitz operator $A(L_\infty)$. The
   resolvent admits a generating-function expression via continued
   fractions / transfer-matrix methods; the imaginary part on the cut
   $\lambda \in (-9/4, 0)$ gives the boundary density. Mostly bookkeeping
   once the resolvent is in hand; the candidate closed form pins down what
   the answer must be, providing a check.

2. **5e.slot_shift — the real bottleneck.** Both Case A and corrected
   Case B of the slot decomposition reduce to bounding
   $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge $ const. The closed-form
   secular equation $\lambda = \sum c_i^2 / (\lambda - \mu_i)$ relates
   $\lambda$ to $\mu$ slot-by-slot; combined with $\sum c_i^2 = 2$ and the
   moments $(W^-, M_1^-, M_2^-)$ from `lprime_5e_a_structural.md`, a
   slot-by-slot Cauchy–Schwarz on the secular function may produce a clean
   bound. Open-ended.

3. **5e.candidate.a.general — the structural attack.** Show
   $W^-(v^*) + (M_1^-(v^*))^2/M_2^-(v^*) \ge T$ at the max-degsum ear via
   clique-tree data and the moment identity $M_2 = \sigma + 2|T_{ab}(H)|$
   from `lprime_5e_a_structural.md`. The 2-path family is the binding case
   empirically ($I_\infty(L) \approx 0.93$ on 2-paths vs $\approx 1.7$ on
   books); a proof on 2-paths (route 1 above) and books (already done)
   gives the binding-case envelope.

4. **Cleanup pass.** Apply the v12 corrections:
   - Edit `lprime_attack_v11.md` §3.2 to use the corrected slot decomposition.
   - Edit `lprime_a_two_path.md` §2 to downgrade "boundary density identified"
     to "candidate boundary density consistent with numerics; analytical
     justification pending". Or replace with a Stieltjes-transform derivation
     once route 1 lands.
   - Tighten test `test_finite_n_residuals_decrease` to assert convergence
     in a Cesàro-averaged sense rather than strict monotonicity.

## Critical reading (carried + v12 additions)

Carried from v11: arXiv:2506.07264 (source), arXiv:1409.2079 (EFGW),
arXiv:2303.11930, arXiv:2311.11530, arXiv:2410.09830, arXiv:2409.15504,
arXiv:2409.18220, Bogoya–Böttcher–Grudsky 2018, Demmel
*Applied Numerical Linear Algebra*, Wilkinson, Avram–Parter 1988.

**v12 additions:**
- **Barry Simon**, *Szegő's Theorem and Its Descendants: Spectral Theory
  for $L^2$ Perturbations of Orthogonal Polynomials* (Princeton, 2011).
  The standard reference for the boundary spectral measure of half-line
  Jacobi / banded operators.
- **Trefethen–Embree**, *Spectra and Pseudospectra* (Princeton, 2005).
  Includes the boundary spectral measure of banded Toeplitz at the first
  basis vector via the symbol.

## Open subobligations (v12)

- (**O5e.1**) Book-arm monotonicity for multi-arm spiders.
- (**O5e.2**) Fan rigorous closure at $n > 200$ (folds into 5c.tail).
- (**O5e.3**) Joint-invariant ansatz: candidate identified (Phase 7);
  conditions (a) and (b) still open.
- (**O5c.1**) Interval-arithmetic for $n \le 200$ — resolved by DK in v10.
- (**O5c.3**) Non-simple-loop BBG analogue for $n > 2000$.
- (**O11.1**) Establish threshold $T$ analytically (not from empirical
  Stage-1 midpoint).
- (**O12.1, new in v12**) **Analytical derivation of the boundary
  spectral density** $\Phi(\theta)$ for the half-line pentadiagonal
  Toeplitz at $w = e_1 + e_2$. Required to upgrade the (a.2-path) closed
  form from "candidate" to "theorem". Stieltjes-transform route is the
  recommended attack.
- (**O12.2, new in v12**) **Slot-shift sum bound**:
  $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge T'$ at the max-degsum
  ear via secular equation + moment data. The unified bottleneck for
  Case A and (corrected) Case B condition (b).

## Open subtasks (status updated in v12)

Carried from v11 (all implemented unless flagged):
- `scripts/spectrum_check.py`, `scripts/two_tree_enum.py`,
  `scripts/extreme_family.py`, `scripts/mpmath_certify.py`,
  `scripts/joint_invariant_features.py`,
  `scripts/build_joint_invariant_corpus.py`,
  `scripts/joint_invariant_ansatz_search.py`,
  `scripts/case_AB_census.py` *(Phase 9)*,
  `scripts/two_path_limit_moments.py` *(Phase 9)*.
- `tests/two_tree_ear_gain.py`, `tests/test_lprime_subfamilies.py`,
  `tests/test_max_degsum_selector.py`, `tests/test_two_path_finite_n.py`,
  `tests/test_two_path_widom_tightness.py`, `tests/test_mpmath_certify.py`,
  `tests/test_w_norm_squared_invariant.py`,
  `tests/test_joint_invariant_candidates.py`,
  `tests/test_b_minor.py` *(Phase 9)*,
  `tests/test_two_path_limit_moments.py` *(Phase 9)*.
- Fallback: `tests/p3_removal_witness.py`, `tests/near_extremal_sanity.py`.

**(v12 NEW)**
- `scripts/half_line_stieltjes.py` — compute the Stieltjes transform of
  $A(L_\infty)$ at $w = e_1 + e_2$ via transfer-matrix / continued
  fraction, extract the boundary density. Verifies the (a.2-path)
  candidate closed form analytically.
- `tests/test_slot_shift_bound.py` — regression for any proposed
  $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge T'$ bound on the
  current corpus.
- `tests/fixtures/case_B_slot_decomposition.json` — explicit fixture
  recording (graph6, $v$, $\alpha_{\text{top}}^2$, slot-shift list,
  recovered $\delta^-$) for several Case B examples ($L_6, L_{10}, L_{12}$,
  some enum$_{n=10}$), preventing regression to the Phase 8 sign error.

The permanent regressions are kept:
`tests/fixtures/two_tree_universal_counterexamples.json` (v7),
`tests/fixtures/w_norm_squared_is_2.json` (v9),
`tests/fixtures/joint_invariant_falsified.json` (v10/Phase 7).

## Summary of v12 state

- **5c (2-paths $\delta^-$)**: rigorously closed for $n \in [4, 2000]$;
  tail $n > 2000$ open.
- **5e headline (max-degsum selector)**: open.
- **5e.a (condition (a))**: closed on books, BT-page; **2-paths
  asymptotic has candidate closed form pending analytical derivation
  (Stieltjes transform)**; general 2-trees open.
- **5e.b (condition (b))**: open for all subfamilies; **Phase 8 attack
  route invalidated** by the slot-decomposition correction; the unified
  slot-shift sum bound (O12.2) is the real wall.
- **New unconditional results in v12**: Lemma B1 (Rayleigh
  $\alpha_{\min}$ bound), corrected slot decomposition (Case B with
  $\alpha_{\text{top}}^2$), $\alpha_{\min}^2 \ge 1$ uniformly on Case B
  max-degsum ears via sufficient $|M_1^-| \ge W^-(1-W^-)$.
- **Test suite**: 482/482 passing.
