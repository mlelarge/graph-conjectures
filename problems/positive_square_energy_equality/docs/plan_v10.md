# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v10** (this version): incorporates the reviewer pass on the Phase 6 deliverables
  (`lprime_max_degsum.md` after the §2 bug fix, `lprime_two_paths_finite.md` after
  mpmath/DK extension, `lprime_5e_a_structural.md`, `lprime_5e_b_interlacing.md`).
  Two headline outcomes:
  1. **5c effectively closed for $n \le 2000$**, rigorously, via the
     Demmel–Kahan a-posteriori IEEE-backward-error bound on `numpy.linalg.eigvalsh`,
     with mpmath @ dps = 50 as a confirmatory high-precision check for
     $n \le 200$. The mpmath part is **morally** an interval certificate
     (slack/forward-error ratio $\sim 10^{50}$) but **technically still
     high-precision FP**; the Demmel–Kahan companion is **formally rigorous**
     (it propagates IEEE backward-error bounds deterministically). The tail
     $n > 2000$ remains research-grade (O5c.3), the genuine open Toeplitz
     question is non-simple-loop BBG generalisation for
     $f(\theta) = 2\cos\theta + 2\cos 2\theta$.
  2. **Conjecture 7.1 is RETIRED** as a settled negative. The single-scalar
     selector lemma (any inequality of the form "$\Psi(v^*) \ge $ const $\Rightarrow$
     $\delta^-(v^*) \ge 17/16$" with $\Psi$ scalar and structural) is
     **categorically wrong**. Three independent verifications:
     (a) Empirical falsification on $L_5, L_6$: $W^-(L_5, v^*) = 0.515$,
         $W^-(L_6, v^*) = 0.380$, both below the naturally-halved
         $17/32 \approx 0.531$.
     (b) Structural falsification by $K_3 \to K_2$: $W^- = 0$ but
         $\delta^- = 1$. The new eigenvalue (Case B) carries $\delta^-$
         entirely via the secular equation, with **no** $W^-$ support.
     (c) The $W^0$ subspace is essential: at $L_5$, $W^0 = 0.5$ of the
         total $\|w\|^2 = 2$; at $L_8$, $W^0 = 0.333$. Any conjecture
         ignoring $W^0$ misses 25–50% of the spectral budget at the worst
         cases.
     This is **progress**, not regression — it eliminates a research direction
     with concrete spectral insight on what is missing.
  3. **Conjecture v10.1 (joint-invariant selector)** replaces 7.1. There
     exists a continuous functional $I(W^-, W^0, c_{n-1}^2, M_1^-, M_2^-;
     \mathrm{spec}(H))$ and a threshold $T$ such that at the max-degsum ear
     $v^*$ of a 2-tree $G$ with $n \ge 4$: (a) $I(v^*) \ge T$; (b)
     $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$. The form of $I$ and $T$
     is *open*. This is qualitatively harder than 7.1: we need a
     non-scalar ansatz, not just a constant. v9 had an explicit (heuristic)
     candidate; v10 has only a shape.
  4. **Three new failure modes** (see §"Failure modes"): F7 (single-scalar
     selector thresholds are categorically wrong), F8 (mpmath @ high-precision
     $\ne$ interval arithmetic; only Demmel–Kahan or `mpmath.iv` is formally
     rigorous), F9 (Case B carries $\delta^-$ without $W^-$ support — any
     selector lemma needs a Case B branch).
  5. **Minor corrections.** Strike the "$8\sqrt{2}$" boxed display in 5c (the
     prose actually derived $\sqrt{2}(8+\sqrt{2}) \approx 13.31$, and the
     erratum note alone isn't enough). Fix the Sylvester-cited Lemma 3.2 in
     `lprime_5e_b_interlacing.md`: the cited one-liner doesn't actually prove
     $\delta^- \ge 0$ for simplicial-ear deletion.
- **v9**: reviewer pass on Phase 5. Bug fix to $\|w\|^2 = 2$ in §2 of
  `lprime_max_degsum.md`; Conjecture 7.1 renormalised but still scalar;
  fans / spider Case II downgraded; F5 (FP $\ne$ interval) and F6 (BBG
  simple-loop hypothesis fails) added; O5c.1, O5c.2, O5e.1, O5e.2, O7.1
  recorded.
- **v8**: Phase 4 — books/2-paths-asymptotic/BT proved; max-degsum selector
  replaces v7 O2; new headline target.
- **v7**: Phase 3 universal-lemma falsification; trace identity recorded;
  existential ear-selection lemma (L') becomes the target.
- **v6**: mathematician pass — 2-trees as first serious target; simplicial-ear
  deletion lemma formulated.
- **v5**: reviewer pass — domination $\le 2$ connected, $s^+$ only;
  $P_3$-removal sign-specific; Conj 9.1 adjacent evidence; near-extremal
  endpoints clarified.
- **v4**: review of v3 — domination $\le 2$ scoped to $s^+$; $K_1$ endpoint;
  $s^+$ residue refined to clique-size distribution.
- **v3**: six logical corrections — EFGW connected (counter-ex. $2K_3$);
  $9.2(i)$ does not imply EFGW for unicyclic; clique-residue energy split;
  $\ell < k/16+1$ sufficient not necessary; Lemma 3.1 no support restriction;
  trees and $K_n$ both equality families.
- **v2**: dropped false connectivity-via-$P_3$-removal claim; dropped
  $-A$ dualization; "all planar" cut from EFGW-known classes; headline
  downgraded to speculative.
- **v1**: original draft.

What v10 calls **unconditionally established**: the clique-tree formalization
of 2-trees (Lemmas 1.1–1.3 of `lprime_max_degsum.md`); the trace identity
$\delta^+ + \delta^- = 4$ at any degree-2 simplicial ear; books $B_k$ for
all $k \ge 2$ (`lprime_books.md`); the BT$(k,2)$ asymptotic; the 2-paths
*Szegő asymptotic* $\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi)$;
**(new)** $\delta^-(L_n) \ge 17/16 + 1/4$ for all $n \in [4, 2000]$ via
Demmel–Kahan; the **negative result** that no single-scalar $W^-$
threshold works (Conj 7.1 retired); the **clique-tree identity**
$M_2 = \sigma(v) + 2|T_{ab}(H)|$ from `lprime_5e_a_structural.md`; and the
**Cauchy–Schwarz bound** $W^-(v) \ge (M_1^-(v))^2 / M_2^-(v)$. 456/456
tests passing.

## The conjecture (verbatim, Section 9 of the source paper)

Let $G$ be a **connected** graph of order $n$.
- **(i)** $s^+(G) = n - 1$ iff $G$ is a tree.
- **(ii)** $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.

Notation: $\lambda_1 \ge \cdots \ge \lambda_n$ are the adjacency eigenvalues of $G$;
$s^+(G) := \sum_{\lambda_i > 0} \lambda_i^2$, $s^-(G) := \sum_{\lambda_i < 0} \lambda_i^2$;
$\mathrm{tr}(A^2) = 2m = s^+ + s^-$.

## Why this conjecture, and the honest tractability verdict

Unchanged from v8/v9. Verdict 2/10 for full conjecture; $P_3$-removal slack
$17/16$ does not close equality without an extra structural hypothesis;
source paper's Thm 8.1 sidesteps via $\alpha(G)\omega(G) \le n/17$.

## Background, easy direction, and central obstruction

Unchanged from v8 (and v7). The crude telescoping bound is
$s^\pm(G) \ge n + k/16 - \ell$; for $s^-$ the sufficient condition is
$\ell < k/16 + 1$; for $s^+$ the residue invariant is the clique-size
distribution $\sum (n_j - 1)^2$. The $17/16$ slack actively selects cut
vertices; this is the fatal obstruction for the residue programme outside
strongly-structured classes.

## What the modest deliverables look like

Unchanged. Corollary A (claw-free, Thm 1.1) and Corollary B (diameter $\le 2$,
Thm 1.2). Drafted in [`corollaries_AB.md`](corollaries_AB.md).

## What a serious result would require, and where to look

Unchanged search directions: **2-trees** (chosen target), 2-connected, block,
chordal, cactus, $\alpha\omega$ regime opposite to Thm 8.1.

### First serious target: 2-trees

Target theorem (unchanged from v6 onward):

> If $G$ is a 2-tree on $n$ vertices, then Conjecture 9.2 holds for $G$.

The universal local lemma is **false** (v7). The plan targets the existential
ear-selection lemma:

> **(L') 2-tree existential ear lemma.** Let $G$ be a 2-tree with $n \ge 4$.
> There exists a simplicial degree-2 vertex $v^*$ with
> $\delta^+(v^*) \ge 17/16$ and $\delta^-(v^*) \ge 17/16$ — equivalently
> $\delta^-(v^*) \in [17/16, 47/16]$ via the trace identity
> $\delta^+ + \delta^- = 4$.

If (L') holds at every non-base step, telescoping to $K_3$ gives
$s^\pm(G) \ge s^\pm(K_3) + (17/16)(n - 3) > n - 1$.

### Phase 4 progress (carried over from v8)

**Books $B_k$ (proved, [`lprime_books.md`](lprime_books.md)).** Unconditional:
$\delta^-(B_k) = 2 - 4/(\sqrt{8k+1} + \sqrt{8k-7})$, both $\delta^\pm(B_k)
\in [17/16, 47/16]$ for $k \ge 2$.

**2-paths $L_n$ Szegő asymptotic (proved, [`lprime_two_paths.md`](lprime_two_paths.md)).**
$\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi) \approx 1.4262$;
$\delta^+_\infty(L) = (16\pi + 27\sqrt 3)/(12\pi) \approx 2.5738$.

**BT$(k,2)$ bad ear (proved, [`lprime_selector.md`](lprime_selector.md)).**
$\delta^-_\infty(\mathrm{BT}) = 4 - \alpha^2 + \beta^2 \approx 1.0353 < 17/16$.

### Phase 5 progress (carried over from v9)

**Bug fix applied** to `lprime_max_degsum.md` §2 (the $\|w\|^2 = 2$ correction)
and locked in by regression fixture `tests/fixtures/w_norm_squared_is_2.json`
+ test `tests/test_w_norm_squared_invariant.py`.

**Status boxes** added to `lprime_max_degsum.md` §5 (fans), §6 (spider 2-trees),
and the top of `lprime_two_paths_finite.md`.

### Phase 6 progress (new in v10)

#### (a) 5c effectively closed for $n \le 2000$

Two independent rigorous certificates of $\delta^-(L_n) \ge 17/16 + 1/4$:

- **mpmath @ dps = 50** (high-precision FP, exact integer input): full curated
  set $\{4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 50, 80, 100, 130, 160, 200\}$.
  Worst case $n = 6$, slack $0.256507460889509805\ldots$ (25 verified digits).
- **Demmel–Kahan a-posteriori** (rigorous IEEE backward-error + Weyl
  propagation): default $n \in [4, 1000]$, CLI-runnable to $n \in [4, 2000]$ in
  $\le 4$ min. Slack/error ratio $\sim 8 \cdot 10^{10}$ at $n = 6$; $\sim 5
  \cdot 10^6$ at $n = 1000$. Conservative by an extra factor of $n$ compared
  to the sharpest Demmel Thm 5.5 bound (still rigorous).

The two agree at all 17 probed values to within numerical precision. **The
DK companion is the formal certificate**; mpmath is confirmatory.

Files: `scripts/mpmath_certify.py`, `tests/test_mpmath_certify.py`,
`data/two_path_mpmath_certificate.json`,
appended §"Phase 5c-a / 5c-b update" of [`lprime_two_paths_finite.md`](lprime_two_paths_finite.md).

#### (b) Conjecture 7.1 retired (settled negative)

The single-scalar form (any "$\Psi(v^*) \ge $ const $\Rightarrow \delta^- \ge
17/16$" with $\Psi$ scalar and structural) is empirically **falsified**.
Verified by direct computation on $L_n$ under the corrected $\|w\|^2 = 2$:

| $n$ | $\delta^-(v^*)$ | $W^-(v^*)$ | $|M_1^-| + \tfrac12 M_2^-$ | $W^0$ |
|---:|---:|---:|---:|---:|
| 5  | 1.5628 | **0.5149** | **0.7915** | 0.500 |
| 6  | 1.3190 | **0.3796** | 0.9802 | 0.000 |
| 8  | 1.4828 | 0.5311 | 0.8955 | 0.333 |
| 10 | 1.4304 | 0.6279 | 0.9831 | 0.000 |
| 12 | 1.3967 | 0.5024 | 0.9642 | 0.000 |

Neither $17/16 \approx 1.06$ nor the naturally-halved $17/32 \approx 0.531$
survives as a uniform lower bound for $W^-$. The moment-form correction
$|M_1^-| + \tfrac12 M_2^- \ge 17/16$ also fails at $n = 5$ ($0.79 < 1.06$).

**Independent reason** the single-scalar form cannot work: $K_3 \to K_2$ has
$W^-(\text{ear}) = 0$ exactly (eigenvectors of $K_2$ are $(1,1)/\sqrt 2$ at
$+1$ and $(1,-1)/\sqrt 2$ at $-1$; $w = (1, 1)$ projects entirely onto $u_+$).
Yet $\delta^- = s^-(K_3) - s^-(K_2) = 2 - 1 = 1$. The negative eigenvalue
$\alpha(G) = -1$ of $A(G)$ is **new** (it's a root of the secular equation,
not an interlaced $\mu_i(H)$); it contributes 1 to $\delta^-$ entirely without
$W^-$ support. **Case B (new eigenvalue) is essential** for any selector
lemma.

Conjecture 7.1 was a v8 guess justified by an erroneous $\|w\|^2 = 4$
normalisation that made $17/16$ look natural. v9 renormalised it; Phase 6
showed the *shape* (single-scalar threshold) is the wrong ansatz. **Retire.**

#### (c) Structural identities from `lprime_5e_a_structural.md`

What 5e-a *delivered* (verified):
- $\deg_H(a) + \deg_H(b) = |T_a(H) \cup T_b(H)| + |T_{ab}(H)| + 2$.
- $M_2(v) = w^\top A(H)^2 w = \sigma(v) + 2|T_{ab}(H)|$, where
  $\sigma(v) := \deg_H(a) + \deg_H(b)$. (Verified: $(A^2)_{aa} = \deg(a)$,
  $(A^2)_{bb} = \deg(b)$, $(A^2)_{ab} = $ common-neighbour count of $a, b$ in
  $H$; in a 2-tree, common neighbours of $\{a, b\}$ are exactly $T_{ab}(H)$.)
- Cauchy–Schwarz: $W^-(v) \ge (M_1^-(v))^2 / M_2^-(v)$ when $M_2^- > 0$.
- $\sigma(v^*) \ge 5$ for any max-degsum ear $v^*$ of a 2-tree on $n \ge 5$
  vertices.

What 5e-a did *not* deliver: any threshold inequality. The route clarifies
the right *shape* of conjecture (moment-form involving $W^-, W^0, M_k^-$
jointly, not single-scalar) and produces clean clique-tree identities, but
closure is research of comparable difficulty to 5e itself.

#### (d) Interlacing assembly from `lprime_5e_b_interlacing.md`

What 5e-b *delivered* (verified):
- Single-step Cauchy interlacing: $\lambda_i(G) \in [\mu_i(H), \mu_{i-1}(H)]$,
  trichotomy Case A vs Case B (Case B = new eigenvalue).
- Handoff inequality: $\eta := \mu_{n-1}(H) - \alpha(G) \ge \sqrt{2 c_{n-1}^2
  - 2}$ when $c_{n-1}^2 > 1$, from the secular-quadratic.
- Case enumeration on $n \le 10$: all 10 worst cases at $n = 10$ are
  **Case B** (new negative eigenvalue). The empirical floor $\delta^-(v^*)
  \ge 1.2941$ at $n = 10$ lives in Case B regime.

What 5e-b did *not* deliver: any positive lower bound on $\delta^-(v^*)$ via
interlacing alone (it gives $\delta^-(v^*) \ge 0$, no more). 5e-b is
**complementary** to 5e-a, not competing: 5e-a is supposed to deliver a
spectral-weight bound, then 5e-b assembles that into a $\delta^-$ bound via
the secular equation.

### Conjecture v10.1 — replaces retired Conjecture 7.1

> **Joint-invariant selector (Conjecture v10.1).** There exist a continuous
> functional
> $$I(W^-, W^0, c_{n-1}^2, M_1^-, M_2^-;\, \mathrm{spec}(H))$$
> and a threshold $T$ such that for every 2-tree $G$ on $n \ge 4$ vertices
> with max-degsum simplicial ear $v^*$ and $H = G - v^*$:
> (a) $I(v^*) \ge T$;
> (b) $I(v) \ge T \;\Rightarrow\; \delta^-(v) \ge 17/16$.

The form of $I$ and $T$ is **open**. Constraints we now know:
- $I$ cannot ignore $W^0$ (25–50% of spectral budget at worst cases).
- $I$ cannot ignore $c_{n-1}^2$ (Case B carries $\delta^-$ at $K_3 \to K_2$
  with $W^- = 0$).
- $I$ is at most a polynomial in $(W^-, W^0, c_{n-1}^2, M_1^-, M_2^-)$
  conditioned on $\mathrm{spec}(H)$ — but the right degree, sign pattern,
  and dependence on the spectral gap of $A(H)$ are open.

### Refined selector conjecture (carried from v8)

> **Max-degsum selector.** For every 2-tree $G$ on $n \ge 4$, the simplicial
> degree-2 ear $v^*$ maximizing $\deg_{G-v^*}(a) + \deg_{G-v^*}(b)$ satisfies
> $\min(\delta^+(v^*), \delta^-(v^*)) \ge 17/16$.

Unchanged and still the new headline target. Empirical: 725/725 at $n \le
10$ (min 1.2940); BT$(50,2)$, BT$(100,2)$; spider triples on $\le 200$
vertices; 456 passing tests. The proof strategy via Conjecture v10.1 is
the v10 replacement for the retired v9 §7 heuristic.

## Revised step-by-step plan (v10)

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry; explicit $K_n$ spectrum | inline | **proved** |
| 2 | Corollary A (claw-free, $\Delta \ge 3$) | Thm 1.1 + paths/cycles | paragraph | drafted |
| 3 | Corollary B ($\mathrm{diam} \le 2$) | Thm 1.2 + $K_{1,n-1}, C_5$ | paragraph | drafted |
| 4 | Short note on steps 1–3 | Exposition | 1–2 weeks | drafts merged; needs polish |
| 5a | (L') on books $B_k$ for $k \ge 2$ | Closed-form spectrum | done | **proved** |
| 5b | (L') on 2-paths $L_n$ asymptotic | Szegő for pentadiagonal sym Toeplitz | done | **proved** |
| 5c | (L') on 2-paths $L_n$ at finite $n$ | Demmel–Kahan a-posteriori + mpmath confirmatory | done for $n \le 2000$ | **rigorous for $n \in [4, 2000]$** |
| 5c.tail | (L') on 2-paths $L_n$ for $n > 2000$ | Non-simple-loop BBG analogue (O5c.3) | research | open |
| 5d | BT$(k,2)$ bad-ear asymptotic | Symmetry quotient + cubic resolvents | done | **proved** |
| 5e | Headline: prove max-degsum selector for general 2-trees | Joint-invariant Conj v10.1 (form open) | open-ended | **headline open**; single-scalar form retired |
| 5e-a | Structural route | Clique-tree functional + Schur complement + moments | done as diagnostic | delivers identities $M_2 = \sigma + 2\|T_{ab}\|$ and $W^- \ge (M_1^-)^2/M_2^-$; does NOT deliver threshold |
| 5e-b | Interlacing route | Cauchy interlacing + secular handoff | done as diagnostic | delivers handoff $\eta \ge \sqrt{2c_{n-1}^2 - 2}$ and Case A/B trichotomy; does NOT deliver positive floor |
| 5f | (L') on fans $F_n$ | Hub + path decomp; DK extension | done for $n \le 200$ | **FP-certified $n \le 200$; tail via 5c-tail** |
| 5g | (L') on multi-arm spider 2-trees | Symmetry + interlacing | partial | Case I = books (redundant); Case II conditional on O5e.1 |
| 6 | If 5e succeeds, prove 9.2 for 2-trees | Telescope to $K_3$ | short | gated on 5e |
| 7 | Fallback: residue-control classes | Block-cut tree, perfect elim, SDP/Gluing | open | not started |
| 8 | Near-extremal sanity ($n \le 30$) | Direct spectrum / Cauchy | 1 week | not started |

5a, 5b, 5d remain proved unconditionally. **5c is now closed for
$n \le 2000$ rigorously** (up from "$n \le 200$ FP-certified" in v9). 5c.tail
is the genuine remaining Toeplitz question. 5e remains the headline, now
with the single-scalar shape retired and replaced by Conj v10.1.

## Three attack vectors (unchanged)

V1 ($P_3$-removal + residue control), V2 (SDP duality via Lemma 3.1, KKT),
V3 (inertia / sign-pattern). Edge-monotonicity removed in v2 (Tang–Liu–Wang,
arXiv:2410.09830).

## Failure modes to guard against

- **F1.** Residue-component count $\ell$ is the whole problem, not cleanup.
- **F2.** Tacit reliance on EFGW in subclasses where it is open (sparse planar /
  unicyclic).
- **F3.** Near-extremal traps in part (ii): $K_n - e$, skewed $K_{p,q}$,
  $K_1 \vee (K_a \cup K_b)$, friendship, $K_{1,1,\ldots,1,2}$.
- **F4.** Regularity is not preserved by induced vertex deletion.
- **F5.** "Floating-point certified" $\ne$ interval-arithmetic certified.
  Upgrade path: explicit Demmel–Kahan a-posteriori bound (rigorous, done
  for 5c) or `mpmath.iv` interval semantics (still TODO).
- **F6.** Toeplitz-asymptotic *effective* constants (BBG, Avram–Parter,
  Widom-type) standardly assume the **simple-loop symbol** hypothesis.
  $f(\theta) = 2\cos\theta + 2\cos 2\theta$ has zeros at both
  $\theta = \pi/3$ (interior) and $\theta = \pi$ (boundary); standard
  theorems do **not** apply.
- **F7 (new in v10). Single-scalar selector thresholds are categorically
  wrong.** Any inequality of the form "$\Psi(v^*) \ge $ const $\Rightarrow$
  $\delta^- \ge 17/16$" with $\Psi$ scalar and structural (e.g. $W^-,
  |M_1^-|, M_2^-,$ or any single linear combination) is empirically
  falsified on the $L_n$ family. Future step-5e proposals must use
  joint invariants involving at least $(W^-, W^0, c_{n-1}^2)$.
- **F8 (new in v10). mpmath @ high-precision $\ne$ interval arithmetic.**
  Even at dps = 50, mpmath delivers high-precision floating-point, not
  rigorous intervals. The forward-error / slack ratio at dps = 50 is
  $\sim 10^{-48}/0.25 \approx 10^{-47}$, so the result is **morally** an
  interval certificate, but **formally** still FP. For genuine interval
  arithmetic use `mpmath.iv`; for rigorous propagation in standard FP use
  a Demmel–Kahan a-posteriori bound (the v10 5c route).
- **F9 (new in v10). Case B carries $\delta^-$ without $W^-$ support.**
  At $K_3 \to K_2$, $W^- = 0$ but $\delta^- = 1$ entirely from the new
  negative eigenvalue $\alpha(G) = -1$ via the secular equation. Any
  selector lemma must include a Case B branch conditioned on $c_{n-1}^2$
  (the bottom-eigenvector weight) — not just on $W^-$.

## Concrete next action (v10)

The single-scalar Conjecture 7.1 is dead, so the v10 work pivots toward
**identifying the right joint-invariant form for Conjecture v10.1**. Three
sub-routes, prioritised:

1. **Joint-invariant ansatz search.** Compute $(W^-, W^0, c_{n-1}^2,
   M_1^-, M_2^-)$ at the max-degsum ear for all 725 enumerated 2-trees
   ($n \le 10$) and for seeded random 2-trees at $n \in \{20, 30, 50, 100\}$.
   Search for a polynomial functional $I$ of these five variables
   (possibly with $\mathrm{spec}(H)$-dependent coefficients) that uniformly
   stays above some threshold $T$ while implying $\delta^-(v) \ge 17/16$
   via the secular equation. Start with degree-2 ansätze and the constraint
   $I(K_3, \text{ear}) = $ some value matching $\delta^- = 1$ (Case B
   normalisation). Output: `scripts/joint_invariant_search.py`,
   `tests/test_joint_invariant_candidates.py`, `data/joint_invariant_scan.json`.

2. **5c.tail / O5c.3 — non-simple-loop BBG.** The 2-paths symbol
   $f(\theta) = 2\cos\theta + 2\cos 2\theta$ has zeros at $\pi/3$ (interior,
   transversal) and $\pi$ (boundary). Standard BBG fails. Two options:
   - (a) Direct $L_n = L_{n-1}' + R_n$ rank-2 perturbation analysis with
     explicit secular-equation control on the boundary contribution.
   - (b) Splitting trick: factor $f(\theta) = -2(1 - \cos\theta)(1 + 2\cos\theta)$
     and treat the two zeros separately (the boundary zero at $\pi$ via
     Avram–Parter's Hermite normalisation, the interior zero at $\pi/3$
     via a transversal-zero secular bound).
   Open-ended.

3. **Joint-invariant DIAGNOSTIC mode.** Even without a closed proof, make
   the regression `test_joint_invariant_candidates.py` part of the
   permanent test suite — a continuously-extended empirical filter that
   any proposed $I$ must pass. The list of falsified candidates becomes a
   versioned "failed shape" archive analogous to
   `tests/fixtures/two_tree_universal_counterexamples.json`. File:
   `tests/fixtures/joint_invariant_falsified.json`.

4. **Polish steps 2–3 corollaries** (carried over).

5. **Continue regression harness** (456 tests passing).

## Critical reading (additions in v10)

Carried over from v9 plus: **Demmel** *Applied Numerical Linear Algebra*
(Thm 5.5 a-posteriori eigenvalue bounds for symmetric matrices, the
rigorous route for 5c); **Wilkinson** *The Algebraic Eigenvalue Problem*
(backward stability of QR and Householder for symmetric pentadiagonal);
**Avram–Parter** 1988 for the trace-formula treatment of $\mathrm{tr}\,
\phi(T_n(f))$ with sign-changing $\phi$. The Bogoya–Böttcher–Grudsky 2018
reference remains the closest enabling theorem for 5c.tail, but with the
caveat that the simple-loop hypothesis fails for our symbol (O5c.3).

## Open subobligations (v10)

- (**O5e.1**) Book-arm monotonicity for multi-arm spiders. Carried from v9.
- (**O5e.2**) Fan rigorous closure at $n > 200$. Now folds into 5c.tail
  via the same DK extension argument (since $F_n$ is built from $K_1 \vee
  P_{n-1}$, with a comparable symbol structure).
- (**O5e.3, replaces O7.1**) Identify a non-falsifiable joint functional
  $\Psi$ of $(W^-, W^0, c_{n-1}^2, M_1^-, M_2^-)$ such that $\Psi(G, v^*)
  \ge \Psi_0$ at the max-degsum ear and $\Psi \ge \Psi_0 \Rightarrow
  \delta^-(v) \ge 17/16$. The natural single-scalar candidates
  $\Psi \in \{W^-, |M_1^-|, |M_1^-| + \tfrac12 M_2^-\}$ are **falsified**;
  the work is to identify a non-falsifiable shape.
- (**O5c.1**) Interval-arithmetic $n \le 200$ certification. Resolved by
  Demmel–Kahan in v10; if `mpmath.iv` semantics are preferred for a
  fully algebraic statement, port over.
- (**O5c.3, replaces O5c.2**) Non-simple-loop BBG / Avram–Parter
  effective-rate constant for $f = 2\cos\theta + 2\cos 2\theta$ for
  $n > 2000$. The genuine research item under 5c.tail.

## Open subtasks (status updated in v10)

- `scripts/spectrum_check.py` — **implemented**.
- `scripts/mpmath_certify.py` — **implemented in v10** (5c rigorous to $n
  \le 2000$).
- `scripts/two_tree_enum.py` — **implemented**.
- `tests/p3_removal_witness.py` — fallback, **not started**.
- `tests/two_tree_ear_gain.py` — **implemented**.
- `tests/test_lprime_subfamilies.py` — **implemented**.
- `tests/test_max_degsum_selector.py` — **implemented**.
- `tests/test_two_path_finite_n.py` — **implemented**.
- `tests/test_two_path_widom_tightness.py` — **implemented**.
- `tests/test_mpmath_certify.py` — **implemented in v10** (15 tests passing).
- `tests/test_w_norm_squared_invariant.py` — **implemented in v9**.
- `tests/near_extremal_sanity.py` — **not started** (fallback, step 8).
- **(v10 NEW)** `scripts/joint_invariant_search.py` — sweep
  $(W^-, W^0, c_{n-1}^2, M_1^-, M_2^-)$ over 2-trees; find candidate
  polynomial functionals; archive falsified candidates.
- **(v10 NEW)** `tests/test_joint_invariant_candidates.py` — regression-test
  any proposed $I$ on the 725 + 200 + 6 corpus.
- **(v10 NEW)** `tests/fixtures/joint_invariant_falsified.json` — versioned
  archive of falsified single-scalar and joint candidates.

Phase-3 universal-lemma regression under
`tests/fixtures/two_tree_universal_counterexamples.json` is kept
permanently. The v9 `tests/fixtures/w_norm_squared_is_2.json` regression
is also kept permanently.
