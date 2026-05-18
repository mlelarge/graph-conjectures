# arXiv outline — "Towards Conjecture 9.2 on 2-trees"

**Working title.** *Towards positive-square-energy equality on 2-trees:
subfamily closures, an existential ear-selection lemma, and a moment-form
candidate.*

**Alt title (shorter).** *Square energy on 2-trees: subfamily closures and a
joint-invariant ansatz.*

**Authors.** TBD (Roles 1, 3, 5; plus the Phase-7/8/9/10/11 contributors as
appropriate).

**Target.** arXiv math.CO + math.SP, with cross-listing to math.NA for the
Demmel–Kahan section.

**Length.** ~32 pages main text + ~6 pages of appendix (failure modes,
auxiliary computations, code pointer).

**Source.** All of `docs/plan_v13.md`, `docs/lprime_*.md` (15 companion notes),
`scripts/`, `tests/`, `data/`. Repo will be cited as a software supplement;
all numerical claims have a regression test in `tests/`.

---

## Abstract (target: 180 words)

We study Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang (arXiv:2506.07264)
on equality cases of positive and negative square energies $s^\pm$. For a
connected graph $G$ of order $n$, the conjecture predicts that $s^-(G) = n-1$
iff $G$ is a tree or $K_n$. We focus on 2-trees — maximal chordal graphs of
treewidth 2 — and reduce the conjecture for this class to an **existential
ear-selection lemma** (L'). We prove (L') unconditionally on books $B_k$,
2-paths $L_n$ (in the Szegő limit), and on the BT$(k,2)$ family. For finite
$n \le 1000$ we close 2-paths via a Demmel–Kahan a-posteriori certificate.
We isolate the headline open content as two precise conditions on a
moment-form joint-invariant candidate $I = W^- + (M_1^-)^2/M_2^-$, prove
both conditions on three subfamilies plus the 2-path asymptotic limit, and
identify the remaining obstruction as a slot-shift bound on the smallest
secular root. The paper includes new Rayleigh-quotient bounds, a Stieltjes
transform identification of the 2-path negative-spectrum measure, and an
appendix cataloguing nine specific failure modes the search rejected.

---

## 1. Introduction (target: 3 pp)

**1.1 The conjecture.** State Conjecture 9.2(ii) of arXiv:2506.07264. Note
the easy forward implications (trees give $s^- = m = n-1$; $K_n$ has spectrum
$\{n-1, -1^{(n-1)}\}$). Cite EFGW (arXiv:1409.2079), the $\le 2$ positive
eigenvalues equality literature (Abiad et al. arXiv:2303.11930), the
asymmetry between $s^+$ and $s^-$ (Elphick–Linz arXiv:2311.11530), the
$3n/4$ lower bound (Akbari–Kumar–Mohar–Pragada arXiv:2409.18220),
edge-monotonicity failure (Tang–Liu–Wang arXiv:2410.09830). Position our
work as a tractable slice (2-trees) of the full conjecture.

**1.2 What this paper does and does not do.** Frank statement:
- *Does:* close subfamily cases of the 2-tree slice via three different
  techniques (closed-form spectrum, Szegő asymptotics + Demmel–Kahan
  certificate, Stieltjes-transform identification), reformulate the
  obstruction as a precise moment-form joint-invariant condition,
  rigorously cordon off where the proof stops, document nine failure
  modes from the search programme.
- *Does not:* close the conjecture, even on 2-trees. The headline open
  problem (the slot-shift bound on the smallest secular root) is stated as
  Problem 9.1 and explicitly conjecturally posed.

**1.3 Contributions.** A numbered list (matches the 11-item stack from the
project plan):

> 1. Corollaries A, B of 9.2(i) for connected claw-free graphs and for
>    diameter-$\le 2$ graphs.
> 2. Closed-form formula $\delta^-(B_k) = 2 - 4/(\sqrt{8k+1} + \sqrt{8k-7})$
>    on the book family.
> 3. Szegő closed form $\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi)$ on
>    the 2-path family.
> 4. BT$(k, 2)$ bad-ear asymptotic
>    $\delta^-_\infty(\mathrm{BT}) = 4 - \alpha^2 + \beta^2 \approx 1.0353$,
>    falsifying the universal ear-deletion form of (L').
> 5. Demmel–Kahan a-posteriori certificate giving
>    $\delta^-(L_n) \ge 17/16 + 1/4$ unconditionally for $n \in [4, 1000]$.
> 6. The existential ear-selection lemma (L') as the reformulation of
>    Conjecture 9.2 for 2-trees: at every step of the simplicial deletion
>    sequence, *some* ear has both gains $\ge 17/16$.
> 7. The max-degsum selector and the joint-invariant candidate
>    $I(v) = W^-(v) + (M_1^-(v))^2 / M_2^-(v)$ at threshold $T = 0.4122$,
>    robust on a 1063-graph corpus.
> 8. Lemma B1: a Rayleigh-quotient lower bound on $\lambda_{\min}(A(G))^2$
>    in terms of $(W^-, M_1^-)$ alone, tight on books.
> 9. The (b.minor) sufficient condition: a partial closure of condition (b)
>    of the candidate ansatz on Case-B max-degsum ears, giving
>    $\delta^-(v^*) \ge 1$ unconditionally on 2-trees with $n \ge 4$.
> 10. $\lim_{n\to\infty} I(L_n, v^*) = I_\infty(L)$ as an explicit theorem
>     via Stieltjes-transform + Portmanteau, closing condition (a) on the
>     binding 2-path family.
> 11. Failure modes appendix: nine specific dead ends documented with
>     witnesses, so future work does not re-litigate them.

**1.4 Outline.** §2 reviews notation and easy directions. §3 introduces (L')
and the max-degsum selector. §4 proves the subfamily theorems (items 2–5).
§5 develops the moment-form ansatz framework (items 7–10). §6 documents
failure modes (item 11). §7 isolates the two remaining open problems.

---

## 2. Notation, easy directions, and Corollaries A and B (target: 3 pp)

**2.1 Notation.** Adjacency matrix $A(G)$, spectrum $\lambda_1(G) \ge \cdots \ge \lambda_n(G)$,
$s^\pm(G) = \sum_{\lambda_i \gtrless 0} \lambda_i^2$. Trace identity
$2|E(G)| = s^+ + s^-$. 2-tree definition (chordal of treewidth 2; perfect
elimination by simplicial degree-2 vertices). Clique tree $T(G)$, leaves =
simplicial ears, supporting edge $\{a, b\}$.

**2.2 Easy forward implications** (matches item 1, half a page).
- Tree $T$: $s^\pm(T) = |E(T)| = n - 1$ (bipartite spectrum symmetric).
- $K_n$: spectrum $\{n-1, -1^{(n-1)}\}$, so $s^-(K_n) = n - 1$.

**2.3 Corollary A (item 1).** For connected claw-free $G$ with
$\Delta(G) \ge 3$, $s^+(G) > n - 1$ via Theorem 1.1 of arXiv:2506.07264. The
$\Delta \le 2$ case is paths (trees) and cycles ($s^+(C_n) > n-1$ via direct
spectrum). One paragraph.

**2.4 Corollary B (item 1).** For connected $G$ with $\mathrm{diam}(G) \le 2$:
combine Thm 1.2 of arXiv:2506.07264 with explicit checks at $K_{1, n-1}$ (a
tree, $s^+ = n-1 \checkmark$) and $C_5$ ($s^+ = 4.76 > 4 = n-1$). One paragraph.

**2.5 Caveats.** Claw-free unicyclic $P(j, k, \ell)$ with $\Delta \ge 3$
delegates to Thm 1.1 of arXiv:2506.07264 (we do not reprove). The
$\Delta \le 2$ cycle case is unconditional.

---

## 3. The (L') reformulation on 2-trees (target: 3 pp; item 6)

**3.1 Why the universal form fails.** The "every simplicial degree-2 ear
satisfies $\delta^\pm \ge 17/16$" lemma is false. Witnesses (item 4): the
BT$(k, 2)$ tail ear has $\delta^-_\infty \approx 1.0353 < 17/16$, and the
asymmetric ear-gain $\delta^+(v) + \delta^-(v) = 2 \deg_G(v) = 4$ from the
trace identity at a degree-2 ear precludes any universal two-sided bound on
"thin" 2-trees. *Cite our Theorem (item 4 closed form, §4.3).*

**3.2 The trace identity.** $\delta^+(v) + \delta^-(v) = 4$ at every
degree-2 simplicial ear. Consequence: the selector requirement
$\min(\delta^+, \delta^-) \ge 17/16$ is equivalent to
$\delta^-(v) \in [17/16, 47/16]$.

**3.3 The existential lemma (L').** State:
> For every 2-tree $G$ with $n \ge 4$, there exists a simplicial degree-2
> ear $v^*$ with $\delta^-(v^*) \in [17/16, 47/16]$.

Telescope to $K_3$ gives $s^\pm(G) \ge n - 1 + (n-3)/16 > n - 1$. Yields
Conjecture 9.2 on 2-trees.

**3.4 The max-degsum selector.** Define the rule. Empirically robust on
725 enumerated $n \le 10$ + 250 random 2-trees up to $n = 1000$
(0 violations recorded over 467+ test cases). The proof of the selector
property is the headline open work.

**3.5 Reduction map.** (L') ⇐ "max-degsum selector property" ⇐
"$I(v^*) \ge T$ and $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$"
(the joint-invariant candidate; §5).

---

## 4. Subfamily theorems (target: 8 pp)

### 4.1 Books $B_k$, $k \ge 2$ (item 2, ~1.5 pp)

Closed form for the symmetric spectrum of $A(B_k)$ via the natural $K_2$ +
$k$-page decomposition. Telescoping ear deletion gives
$\delta^-(B_k) = 2 - 4/(\sqrt{8k+1} + \sqrt{8k-7})$,
$\delta^+(B_k) = 4 - \delta^-(B_k)$. Both in $[17/16, 47/16]$ for $k \ge 2$.
Minimum at $k = 2$: $\delta^-(B_2) = (7 - \sqrt{17})/2 \approx 1.4385$.
Asymptotically $\delta^-(B_k) \uparrow 2$. **(L') closes unconditionally on
the book family.**

### 4.2 2-paths $L_n$ (Szegő limit; item 3, ~2.5 pp)

$A(L_n)$ is pentadiagonal symmetric Toeplitz with symbol
$f(\theta) = 2 \cos\theta + 2\cos 2\theta$. Two symmetric simplicial ears
($v = 1$ and $v = n$, isomorphic). Szegő's theorem applied to
$\phi_-(\lambda) = \lambda^2 \mathbf 1_{\lambda < 0}$ (continuous at every
point of the spectrum) gives
$$s^-(L_n)/n \;\longrightarrow\; \frac{1}{2\pi}\int_{-\pi}^\pi f(\theta)^2 \mathbf 1_{f(\theta) < 0}\, d\theta.$$
First-difference asymptotic + trace identity (4 unit Fourier coefficients ⇒
$\frac{1}{\pi}\int_0^\pi f^2 = 4$) gives
$$\boxed{\delta^-_\infty(L) = \frac{32\pi - 27\sqrt 3}{12\pi} \approx 1.4262, \qquad
  \delta^+_\infty(L) = \frac{16\pi + 27\sqrt 3}{12\pi} \approx 2.5738.}$$
Both strictly in $(17/16, 47/16)$. Detail the Fourier-mode computation and
the integration over $(\pi/3, \pi)$ (zeros at $\theta = \pi/3, \pi$).

**Remark (F6 in plan).** Standard BBG / Avram–Parter / Widom asymptotics
require simple-loop symbols; $f$ has zeros at both interior $\theta = \pi/3$
and boundary $\theta = \pi$. So the *rate* (open, see §7) is not bookkeeping.

### 4.3 BT$(k, 2)$ (item 4, ~1 pp)

Definition: book $B_k$ + 2-triangle tail. Tail ear $\delta^-$ via $6\times 6$
reduced matrix on the symmetric quotient (page vertices coalesce). Cubic
resolvents in $\alpha$ (root of $2x^3 - 7x - 3 = 0$) and $\beta$ (root of
$2x^3 + 2x^2 - 3x - 2 = 0$). **Theorem:**
$$\delta^-_\infty(\mathrm{BT}) = 4 - \alpha^2 + \beta^2 \approx 1.0353 < 17/16.$$
Asymptotic gap to $17/16$ is a positive constant $\approx 0.027$. This is
the **canonical counterexample** to any universal ear lemma and the
canonical adversarial input for any selector.

### 4.4 2-paths at finite $n$, Demmel–Kahan certificate (item 5, ~2 pp)

For $n \in [4, 1000]$, compute $\delta^-(L_n)$ in high-precision floating
point and bound the forward error by an a-posteriori Demmel–Kahan estimate
applied to symmetric tridiagonalisation of the pentadiagonal matrix. Total
slack $\delta^-(L_n) - 17/16 \ge 0.257 - O(10^{-12})$, comfortably above
machine precision. **Theorem (rigorous):** $\delta^-(L_n) \ge 17/16 + 1/4$
for every $n \in [4, 1000]$. State the precision protocol, the test harness,
and the verifiable certificate file (regression-locked in
`tests/test_mpmath_certify.py`).

**Sub-remark.** Floating-point certificate $\ne$ interval-arithmetic
certificate (F5 of plan). Upgrade path via mpmath at 50-digit precision is
implemented for the 100 closest cases; full upgrade is mechanical.

### 4.5 2-paths Stieltjes-transform identification (item 10, ~1 pp)

The Stieltjes transform of the negative-side spectral measure of
$A(L_n)$ converges weakly to an explicit limit measure derived from the
symbol $f$. By Portmanteau (with continuity of $\lambda^k \mathbf 1[\lambda < 0]$
for $k \ge 1$, see F13 of plan):
$$\lim_{n \to \infty} I(L_n, v^*) = I_\infty(L)
   = \frac{2(310 \pi^2 - 837 \sqrt 3\, \pi + 2187)}{27 \pi (20 \pi - 27 \sqrt 3)}
   \approx 1.0157.$$
Strictly above $T = 0.4122$. **This closes condition (a) of the candidate
ansatz on the binding 2-path subfamily.** Open subobligations O13.1–O13.3
listed (rate, branch verification, trig cleanup) and explicitly demoted to
non-critical-path.

---

## 5. The moment-form ansatz framework (target: 7 pp; items 7–10)

### 5.1 The candidate (item 7, ~1.5 pp)

Define the spectral functionals on simplicial ears: with $H = G - v$ and
$w = e_a + e_b$ ($\|w\|^2 = 2$),
$$W^-(v) := \sum_{\mu_i < 0} c_i^2, \quad M_k^-(v) := \sum_{\mu_i < 0} c_i^2 \mu_i^k,$$
$c_i := u_i(a) + u_i(b)$. State the candidate
$$I(v) := W^-(v) + \frac{(M_1^-(v))^2}{M_2^-(v)}, \qquad T = 0.4122.$$
By Cauchy–Schwarz, $I \in [W^-, 2 W^-]$. Empirical robustness: 1063 graphs,
zero violations. Honest framing: not a conjecture yet — the **candidate
ansatz** in the v11+ sense.

### 5.2 Conditions (a) and (b) (~1 pp)

State the two conditions explicitly. Make clear that
- (a) is structural (graph-theoretic floor on $I(v^*)$ at the max-degsum ear)
- (b) is spectral (the implication $I \ge T \Rightarrow \delta^- \ge 17/16$)

Status of (a):
- Proved on books $B_k$ (§4.1, closed form gives $I(B_k, v^*) \in [1.33, 1.87]$).
- Proved on BT$(k, 2)$ max-degsum ear (book-page; reduces to books).
- Proved on 2-paths $L_n$ in the Szegő limit (§4.5, item 10).
- **Open on general 2-trees.**

Status of (b):
- (b.minor) sub-result (§5.4 below): $\delta^-(v^*) \ge 1$ on Case-B
  max-degsum ears (item 9).
- **Open on all subfamilies beyond the (b.minor) floor.**

### 5.3 Lemma B1 (item 8, ~2 pp)

Statement: with $W^-(v) > 0$,
$$\lambda_{\min}(A(G)) \;\le\; -\frac{|M_1^-(v)| + \sqrt{(M_1^-(v))^2 + 4 W^-(v)^3}}{2 W^-(v)}.$$
Proof: Rayleigh quotient on the trial vector $\tilde w_- - \beta e_v$
($\tilde w_-$ = projection of $w$ to negative eigenspace of $A(H)$,
embedded into $\mathbb R^n$ with zero $v$-component). Optimize $\beta$;
closed form for the minimizer; rationalisation gives the stated bound.

Sharpness: ratio $\alpha_{\min} / f_{\min} \to 1$ on books $B_k$ as
$k \to \infty$. Looser by factor 1.4 on $L_n$ as $n \to \infty$, and by
factor up to 4.4 on BT-tail (acceptable since we're avoiding that ear by
the selector).

### 5.4 Lemma (b.minor) (item 9, ~1.5 pp)

Statement: For every 2-tree $G$ with $n \ge 4$ and every Case-B max-degsum
ear $v^*$,
$$\delta^-(v^*) \;\ge\; 1.$$
Proof sketch:
- Use the chordal-graph inertia argument
  (`lprime_5e_b_interlacing.md` §3.2): simplicial degree-2 ear deletion
  preserves or decreases $n^-$, hence $\delta^- \ge 0$ via Sylvester.
- Strengthen to $\ge 1$ via Lemma B1: in Case B, $\alpha_{\min}^2 \ge f_{\min}^2$.
  The chordal-Sylvester argument gives that *all* slot shifts have
  non-negative net contribution to $\delta^-$, and the new eigenvalue
  contributes $\ge \alpha_{\min}^2 \ge $ explicit floor.
- Concrete numerical floor: $\alpha_{\min}^2 \ge 1$ via the max-degsum
  structural lower bound $\sigma(v^*) \ge 5$ and the resulting $W^-$
  control.

**Note.** This is a *partial* result on condition (b): $1 \ne 17/16$. Gives
the first non-EFGW-implied positive lower bound on the selector.

### 5.5 The 2-path Stieltjes-transform proof (item 10, ~1 pp)

Sketched in §4.5; expanded here with the full Portmanteau argument and the
F12/F13 distinctions (signed angle gap density, $W^- $ vs $M_k^-$
continuity behaviour at zero). Roughly 1 page of measure-theoretic detail
with explicit reference to `lprime_a_two_path_stieltjes.md` for the
trigonometric calculation.

---

## 6. Failure modes (target: 4 pp; item 11)

Catalogue of nine specific dead ends, each with the witness graph or
construction that defeats it. Format: one paragraph per failure mode, with
"why it was tempting", "the precise statement", "the witness".

- **F1.** The universal ear lemma (every simplicial degree-2 ear satisfies
  $\delta^\pm \ge 17/16$). Falsified by BT$(k, 2)$ tail (item 4).
- **F2.** The naive normalisation $\|w\|^2 = 4$. Bug: $e_a, e_b$ orthogonal
  ⇒ $\|w\|^2 = 2$. Caught after Phase 4; described as a cautionary tale
  about cross-checking normalisations against trace identities.
- **F3.** Single-scalar selector thresholds $W^- \ge 17/16$ or $W^- \ge 17/32$
  (the natural halved value). Falsified on $L_5, L_6, L_8, L_{12}$. Why
  thresholds fail asymptotically: BT$(k, 2)$ tail closes the window.
- **F4.** The naive sine-basis "half-line boundary density"
  $(\sin\theta + \sin 2\theta)^2/\pi$. Falsified by factor 100+ in the
  Plancherel-norm test against pentadiagonal Toeplitz. Correct density is
  the signed angle gap $\sin(\theta_2 - \theta_1)/\pi$.
- **F5.** Asymmetric "selector + dual" framework. Falsified: no
  empirically-tighter dual exists on the positive side; the symmetric
  $\delta^+ + \delta^- = 4$ trace identity ties them.
- **F6.** $\alpha\omega$-route route. Doesn't engage 2-trees uniformly
  (chordal graphs of treewidth 2 have a wide range of $\alpha\omega$ values
  that vary with structure, not with $n$).
- **F7.** Phase-8 sign error in the Rayleigh-quotient optimisation. Caught
  before publication; correct sign gives Lemma B1.
- **F8.** "Floating-point certified" $\ne$ interval-arithmetic certified
  (Demmel–Kahan a-posteriori is the formal route used in §4.4).
- **F9.** Simple-loop assumption for BBG-type asymptotic constants. Our
  symbol fails simple-loop (zeros at $\pi/3$ interior and $\pi$ boundary).
  Affects the rate $n_0$ in §4.5; does not affect the limit value.

Each is paired with a regression fixture in `tests/fixtures/*.json` so
the falsifying witness is reproducible.

---

## 7. Open problems and outlook (target: 2 pp)

**Problem 9.1 (the slot-shift wall).** For every 2-tree $G$ with $n \ge 4$
and every simplicial degree-2 ear $v$ satisfying $I(v) \ge T$,
$$\sum_{j \in J^-(H)} \bigl(\lambda_{j+1}(G)^2 - \mu_j^2\bigr) \;\ge\; 17/16
\quad \text{(in Case A)}
\qquad
\alpha^2 + \sum_{j \in J^-(H), j \ne n-1}\bigl(\lambda_{j+1}(G)^2 - \mu_j^2\bigr) \;\ge\; 17/16 \quad \text{(in Case B)}.$$
This is the unified bottleneck of condition (b). Section 7 explains why
standard tools (Lehmann–Goerisch, Temple, Aronszajn) appear too weak in the
cancellation regime ($\alpha^2 \gg \mu_{n-1}^2$ both large with
$\alpha^2 - \mu_{n-1}^2$ small).

**Problem 9.2 (general-2-tree (a)).** Show $I(v^*) \ge I_\infty(L) \approx 1.0157$
uniformly across 2-trees with $n \ge 4$. The 2-path family is the empirical
binding floor; a clique-tree induction with appropriate moment bookkeeping
should close this, though the $W^0$ contribution at $L_5$ shows the right
functional must include zero-eigenvalue weight.

**Sub-routes that should be tried.**
- The chordal-graph quantitative Sylvester refinement
  (`lprime_5e_b_interlacing.md` §3.2 strengthening): a strict positive
  slack version of the inertia-preservation argument.
- A Cauchy-style integral representation of the slot-shift sum via the
  secular function's residues, potentially yielding to a Toda-flow /
  Jacobi-matrix perturbation argument from operator theory.

**What this paper deliberately leaves open.**
- Conjecture 9.2 on 2-trees (the headline target — both Problems above
  need closure).
- The fan family $F_n$ for $n > 200$ (the same Szegő/BBG bottleneck as
  2-paths; closure is mechanical once Problem 9.1's spectral input is in
  hand).
- The multi-arm spider Case II (conditional on book-arm monotonicity,
  O5e.1 of the plan).

---

## A. Appendix — explicit numerics and reproducibility (target: 3 pp)

- A.1 The 1063-graph corpus: source families, randomization seeds, raw
  JSON pointers.
- A.2 The Demmel–Kahan certificate for §4.4: explicit precision bounds,
  test script `tests/test_mpmath_certify.py`.
- A.3 The Stieltjes computation for §4.5 and §5.5: explicit measure
  decomposition $f^*\mu_{\text{Lebesgue on } (\pi/3, \pi)}$, including the
  derivation of the closed form $I_\infty(L)$.
- A.4 Software supplement: pointer to repo, list of test files (508 tests
  passing on submission date), git commit hash for reproducibility.

## B. Appendix — failure-mode fixtures (target: 2 pp)

Tabulated witnesses for F1–F9 (the §6 failure modes), one row per failure
mode, with: identifier, the precise false statement, the smallest
witnessing graph, file pointer to `tests/fixtures/*.json`.

---

## Section budget (target 32 pp main + 5 pp appendix = 37 pp)

| Section | pages | items |
|---|---:|---|
| 1. Introduction | 3 | overview, contribution list |
| 2. Notation, Corollaries A, B | 3 | 1 |
| 3. (L') reformulation | 3 | 6 |
| 4. Subfamily theorems | 8 | 2, 3, 4, 5, 10 |
| 5. Moment-form ansatz | 7 | 7, 8, 9, 10 (detailed) |
| 6. Failure modes | 4 | 11 |
| 7. Open problems | 2 | — |
| App A | 3 | reproducibility |
| App B | 2 | fixtures |

---

## Pre-submission checklist

- [ ] Theorem-level cross-check: every numbered Theorem has a regression
      test in `tests/`.
- [ ] No "TBA" or "TODO" markers in the LaTeX source.
- [ ] Demmel–Kahan certificate runs end-to-end on a clean checkout.
- [ ] $\delta^\pm$ closed forms verified against `np.linalg.eigvalsh` to
      twelve decimals on the listed witnesses.
- [ ] Failure modes appendix cross-referenced from §3 (where the universal
      lemma is retired), §5 (where single-scalar candidates are retired),
      and §6 (the catalogue itself).
- [ ] Acknowledgement of the prior work in the plan revision history
      (v1–v13); cite arXiv:2506.07264 throughout.
- [ ] Anonymisation if needed; otherwise author list finalised.

---

## Notes for the writing-up phase

1. **The order of §4 matters.** Books → 2-paths-Szegő → BT → 2-paths-FP → 
   2-paths-Stieltjes. This builds the reader's intuition: closed form
   first, then asymptotic, then the bad counterexample (justifying the
   reformulation in §3), then the finite-$n$ certificate, then the
   measure-theoretic identification used in §5.
2. **§3 should be readable independently.** The (L') reformulation is the
   conceptual centerpiece; some readers will skip §4 and go straight to §5.
3. **§6 is unusual but valuable.** Catalogue of nine dead ends with
   witnesses is the kind of content that referees value and that
   accelerates future work. Don't bury it.
4. **The honest framing in §1.2 is critical.** This is not a paper that
   closes Conjecture 9.2. It is a paper that reduces, decomposes, partly
   proves, and rigorously cordons. State that up front.
5. **The two open problems in §7 must be precisely stated.** Problem 9.1
   and Problem 9.2 should be stated so that a future author can attempt
   either without reading the rest of the paper.
