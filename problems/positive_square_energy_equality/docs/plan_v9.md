# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v9** (this version): incorporates the reviewer pass on the Phase 5 deliverables
  (`lprime_max_degsum.md`, `lprime_two_paths_finite.md`). Headline changes:
  1. **Math bug fix.** In `lprime_max_degsum.md` §2, the assertion
     $\|w\|^2 = (e_a + e_b)^\top(e_a + e_b) = 2 + 2 A(H)_{ab} = 4$ is **wrong**.
     For $a \ne b$, $e_a, e_b$ are orthogonal standard basis vectors, so
     $\|w\|^2 = 2$, not $4$. The "$4$" the agent wanted is the *trace identity*
     $\delta^+ + \delta^- = 2\deg_G(v) = 4$, which is independent and correct.
     Consequence: $\sum c_i^2 = 2$ (not $4$); Conjecture 7.1's normalization
     must be redone; the heuristic "Conj 7.1 $\Rightarrow$ max-degsum selector"
     in §7 is even weaker than first stated, and the threshold $17/16$ is *not*
     obviously the natural one under the corrected normalization.
  2. **Fans downgraded.** §5 of `lprime_max_degsum.md` claims the selector is
     proved unconditionally on fans. It is not. The proof uses the same
     finite-$n$ + Szegő-asymptotic split as 5c, which we accept as
     *conditionally closed*. Fans are now: $n \le 200$ floating-point-certified;
     $n > 200$ conditional on the same Szegő-rate constant as 5c.
  3. **Spider 2-trees downgraded.** §6 of `lprime_max_degsum.md` proves only
     **Case I** unconditionally (one-arm spiders, which are exactly books — and
     this was already in `lprime_books.md`). **Case II** (multi-arm spiders) is
     conditional on a book-arm monotonicity claim that is *admitted*, recorded
     here as open subobligation O5e.1.
  4. **Conjecture 7.1 reformulated** with $\sum c_i^2 = 2$ and the explicit
     remark that the secular equation alone does not give the claimed
     lower bound on $\delta^-$ from a control on $W^- := \sum_{\mu_i < 0} c_i^2$.
     §7's "implication" in `lprime_max_degsum.md` is a heuristic, not a proof.
  5. **5c re-statused.** For 2-paths $L_n$: $n \in [4, 200]$ is *floating-point
     certified* with slack $\ge 0.257$ from the Szegő limit; $n > 200$ is
     conditional on a BBG-type effective constant for the symbol
     $f(\theta) = 2\cos\theta + 2\cos 2\theta$. **The standard BBG hypothesis
     (Bogoya–Böttcher–Grudsky 2018) assumes simple-loop symbols** — ours has
     zeros at both an interior point ($\theta = \pi/3$) and at the boundary
     ($\theta = \pi$), so the standard theorem **does not apply**. Tail closure
     for $n > 200$ is therefore not "1–2 pages of bookkeeping"; it is
     genuinely research-grade. The "$8\sqrt 2$" rank-2 bound stated in passing
     in `lprime_two_paths_finite.md` is sloppy — the bound the prose actually
     derives is $\sqrt 2 (8 + \sqrt 2) \approx 13.31$; the *conclusion* (too
     coarse to close $n > 200$ alone) is unchanged.
  6. **New F5.** "Floating-point certified" $\ne$ interval-arithmetic
     certified. The 5c / fan certificates use `numpy.linalg.eigvalsh` with
     observed forward error $\sim 3\cdot 10^{-12}$ against slack $0.257$, so
     they are *morally* rigorous but not formally rigorous until upgraded to
     `mpmath`, interval arithmetic, or a Demmel–Kahan a-posteriori bound.
  7. **New F6.** Toeplitz-asymptotic constants (BBG, Avram–Parter,
     Widom-type) standardly assume the *simple-loop symbol* hypothesis. Our
     symbol fails this (boundary zero at $\theta = \pi$). Any plan that
     invokes "the Szegő-rate constant" without redoing the asymptotic for a
     non-simple-loop symbol is wishful.

  What v9 still calls **unconditionally established** (after the reviewer pass):
  the clique-tree formalization of 2-trees (Lemmas 1.1–1.3 of
  `lprime_max_degsum.md`); the trace identity $\delta^+ + \delta^- = 4$ at any
  degree-2 simplicial ear; the Cauchy interlacing slot decomposition (as a
  diagnostic, not by itself a proof); books $B_k$ for all $k \ge 2$ as in
  `lprime_books.md` (this is the one-arm spider case re-derived in §6 Case I);
  the BT$(k,2)$ asymptotic; the 2-paths *Szegő asymptotic* $\delta^-_\infty(L) =
  (32\pi - 27\sqrt 3)/(12\pi)$; and 433/433 tests passing including the
  max-degsum selector verified empirically on 725 + 200 + 6 cases (n ≤ 10 + BT
  + spider triples).

- **v8**: incorporated Phase 4 progress on (L'). Recorded the closed-form proof
  for **books $B_k$** and the Szegő asymptotic for **2-paths $L_n$** as proved
  subfamily theorems, plus the BT$(k,2)$ bad-ear asymptotic. Promoted the
  trace-identity observation to the Szegő limit (no boundary anomaly for
  pentadiagonal symmetric Toeplitz with exactly $4$ unit Fourier coefficients).
  Replaced v7's selector conjecture (O2) by the **max-degsum selector**:
  $\min(\delta^+, \delta^-) \ge 17/16$ at the max-degsum ear, verified on all
  725 enumerated 2-trees with $n \le 10$ and on $\mathrm{BT}(50,2)$,
  $\mathrm{BT}(100,2)$. Identified two open problems: finite-$n$ rigorous proof
  for 2-paths and a proof of the max-degsum selector for general 2-trees (new
  headline target).
- **v7**: incorporated the Phase 3 falsification of the universal 2-tree ear
  lemma. The plan now records the trace identity, the structured
  $\mathrm{BT}(k,2)$ and random counterexamples to "every ear works", and
  replaces the target by the existential ear-selection lemma (L').
- **v6**: mathematician pass — 2-trees made the first serious target;
  simplicial-ear deletion lemma formulated as the local spectral inequality.
  Explicitly *not* an application of induced-$P_3$ removal (a 2-tree ear lies
  in a triangle).
- **v5**: reviewer pass — domination number $\le 2$ explicitly **connected**
  and only cited for $s^+$; $P_3$-removal sign-specific; Conj 9.1 described as
  adjacent evidence; computational subtasks specify the optimization objective;
  near-extremal tests exclude allowed tree/$K_n$ endpoints.
- **v4**: review of v3 — domination $\le 2$ only $s^+$; removed global ranking
  of 9.2(i) vs 9.2(ii); refined $s^+$ residue condition; clarified existential
  $P_3$-removal; added $K_1$ endpoint.
- **v3**: six logical corrections — EFGW connected; 9.2(i) does not literally
  imply EFGW for unicyclic; residue energy is $\sum (n_j - 1)$ vs
  $\sum (n_j - 1)^2$; $\ell < k/16 + 1$ sufficient not necessary; Lemma 3.1 has
  no support restriction; trees and $K_n$ both equality families for $s^- = n - 1$.
- **v2**: dropped false connectivity propagation through $P_3$-removal; dropped
  spurious "dualize via $-A$"; dropped "all planar" from EFGW-known; downgraded
  headline route to speculative.
- **v1**: original draft.

## The conjecture (verbatim, Section 9 of the source paper)

Let $G$ be a **connected** graph of order $n$.
- **(i)** $s^+(G) = n - 1$ iff $G$ is a tree.
- **(ii)** $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.

Notation: $\lambda_1 \ge \cdots \ge \lambda_n$ are the adjacency eigenvalues of $G$;
$s^+(G) := \sum_{\lambda_i > 0} \lambda_i^2$, $s^-(G) := \sum_{\lambda_i < 0} \lambda_i^2$;
$\mathrm{tr}(A^2) = 2m = s^+ + s^-$.

## Why this conjecture, and the honest tractability verdict

Unchanged from v8. Verdict 2/10 for full conjecture; $P_3$-removal slack $17/16$
does not close equality without an extra structural hypothesis; source paper's
Thm 8.1 sidesteps via $\alpha(G)\omega(G) \le n/17$.

## Background, easy direction, and central obstruction

Unchanged from v8 (and v7). The crude telescoping bound is
$s^\pm(G) \ge n + k/16 - \ell$; for $s^-$ the sufficient condition is
$\ell < k/16 + 1$; for $s^+$ the residue invariant is the clique-size
distribution $\sum (n_j - 1)^2$. The $17/16$ slack actively selects cut
vertices; this is the fatal obstruction for the residue programme outside
strongly-structured classes.

## What the modest deliverables look like

Unchanged from v8. **Corollary A** (9.2(i) for connected claw-free, via Thm 1.1
of arXiv:2506.07264) and **Corollary B** (9.2(i) for diameter $\le 2$, via
Thm 1.2). Drafted in [`corollaries_AB.md`](corollaries_AB.md).

## What a serious result would require, and where to look

Unchanged search directions: **2-trees** (chosen target), 2-connected, block,
chordal, cactus, $\alpha\omega$ regime opposite to Thm 8.1. See v8.

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
$\delta^-(B_k) = 2 - 4/(\sqrt{8k+1} + \sqrt{8k-7})$, $\delta^+(B_k) = 4 - \delta^-(B_k)$,
both in $[17/16, 47/16]$ for all $k \ge 2$. Minimum at $k = 2$:
$\delta^-(B_2) = (7 - \sqrt{17})/2 \approx 1.4385$.

**2-paths $L_n$ Szegő asymptotic (proved, [`lprime_two_paths.md`](lprime_two_paths.md)).**
$\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi) \approx 1.4262$;
$\delta^+_\infty(L) = (16\pi + 27\sqrt 3)/(12\pi) \approx 2.5738$. Both
$> 17/16$ strictly. Trace identity in the limit follows from the symbol
having exactly $4$ unit Fourier coefficients.

**BT$(k,2)$ bad ear (proved, [`lprime_selector.md`](lprime_selector.md)).**
$\delta^-_\infty(\mathrm{BT}) = 4 - \alpha^2 + \beta^2 \approx 1.0353 < 17/16$,
where $\alpha, \beta$ are explicit cubic roots. **The selector must actively
avoid the bad tail ear**, by a constant gap, in the limit.

### Phase 5 progress (new in v9, with reviewer corrections applied)

**Phase 5 deliverables (in `lprime_max_degsum.md`, `lprime_two_paths_finite.md`,
`test_max_degsum_selector.py`, `test_two_path_finite_n.py`).** 433/433 tests
passing; max-degsum selector verified empirically on 725 + 200 + 6 cases.

The reviewer pass forces three downgrades:

| Item | What `lprime_max_degsum.md` / `lprime_two_paths_finite.md` claims | What v9 records |
|---|---|---|
| Clique-tree formalization (Lemmas 1.1–1.3) | Proved | **Proved** — unaffected |
| Trace identity $\delta^+ + \delta^- = 4$ | Proved | **Proved** — unaffected |
| §2 Schur reduction with $\|w\|^2 = 4$ | Stated | **Math bug** — $\|w\|^2 = 2$; fix and propagate (see §"Bug fix" below) |
| Cauchy interlacing slot decomposition (§3) | Lemma + heuristic | **Diagnostic only** — not a proof on its own |
| Fans $F_n$, max-degsum selector unconditional | "Proved" | **Downgraded**: $n \le 200$ FP-certified; $n > 200$ conditional on 5c-type Szegő rate |
| Spider 2-trees Case I (one-arm) | Proved | **Proved but redundant** — identical to books |
| Spider 2-trees Case II (multi-arm) | Proved | **Conditional** on book-arm monotonicity (O5e.1) |
| Conjecture 7.1 $\Rightarrow$ max-degsum selector | "Implies" via secular | **Heuristic only** — needs reformulation under $\|w\|^2 = 2$; even then the secular equation does not yield the claimed clean lower bound on $\delta^-$ from $W^-$ alone |
| 2-paths $L_n$, $n \in [4, 200]$ "certified" | "Rigorous" | **FP-certified only** (forward error $\sim 3\cdot 10^{-12}$ vs slack $0.257$); rigour requires interval arithmetic or Demmel–Kahan |
| 2-paths $L_n$, $n > 200$ "1–2 pages" | Tail closure claimed near-trivial | **Research-grade** — standard BBG/Widom requires simple-loop symbol; ours has interior+boundary zeros |
| "$8\sqrt 2$" rank-2 bound in 5c | Stated | Prose actually gives $\sqrt 2(8 + \sqrt 2) \approx 13.31$; conclusion unchanged but derivation sloppy |
| Edge-uniform random 2-tree sampling | Sampling | **Cosmetic**: edge-uniform, not isomorphism-uniform; OK as counterexample harness, not as sampling-based proof |

**Bug fix (to apply to `lprime_max_degsum.md` §2 in a separate pass).**
The block form is correct,
$$A(G) = \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix},\qquad w = e_a + e_b.$$
For $a \ne b$, $e_a^\top e_b = 0$, so
$$\|w\|^2 = e_a^\top e_a + 2 e_a^\top e_b + e_b^\top e_b = 1 + 0 + 1 = 2.$$
The constant "$4$" the original text wanted is the trace identity
$\mathrm{tr}(A(G)^2) - \mathrm{tr}(A(H)^2) = 2\deg_G(v) = 4$, which is a
*different* derivation (it computes
$2 \deg_G(v) = 2 (e_a^\top A(G) e_a + \cdots) = 2 \cdot 2$, with $\deg_G(v) = 2$).
The two are not the same quantity. Downstream consequences:

- (2.1) becomes $\sum_i c_i^2 = \|w\|^2 = 2$. (Not $4$.)
- The secular equation (2.2) is unchanged in form: $\lambda = \sum_i c_i^2 / (\lambda - \mu_i)$.
- The trace identity (2.3), $\delta^+ + \delta^- = 4$, is **unchanged** — it comes
  from $\mathrm{tr}(A(G)^2) - \mathrm{tr}(A(H)^2)$, not from $\|w\|^2$.
- The condition $\delta^-(v) \in [17/16, 47/16]$ for (L') is **unchanged**, since
  it follows from the trace identity.
- **Conjecture 7.1** (in `lprime_max_degsum.md` §7) — restated below.

### Conjecture 7.1, restated under the correct $\|w\|^2 = 2$ normalization

Let $W^-(v) := \sum_{i:\, \mu_i(H) < 0} c_i(v)^2$ and $W^+(v) := \sum_{i:\, \mu_i(H) > 0} c_i(v)^2$, where
$c_i(v) = u_i(a) + u_i(b)$. Then $W^-(v) + W^+(v) + W^0(v) = \|w\|^2 = 2$.

> **Conjecture 7.1 (v9, renormalised).** For every 2-tree $G$ with $n \ge 4$
> and every simplicial degree-$2$ ear $v$ with supporting edge $\{a, b\}$
> maximizing $\deg_H(a) + \deg_H(b)$ in $H = G - v$, the negative spectral
> weight on $H$ satisfies
> $$W^-(v) \;\ge\; W^-_*\,, \qquad \text{for some explicit }W^-_*\,.$$
> The conjectured threshold $W^-_*$ that would yield $\delta^-(v) \ge 17/16$
> via the secular equation is **not** $17/16$ itself; under $\|w\|^2 = 2$ the
> natural threshold drops accordingly and must be re-derived from the secular
> equation $\lambda = \sum c_i^2 / (\lambda - \mu_i)$ together with Cauchy
> interlacing. **The reformulation is open work.**

**Why this matters.** Under the buggy $\|w\|^2 = 4$ the agent could plausibly
argue $17/16$ as the natural threshold from "$\sum c_i^2 = 4$" matched against
$\delta^- = 17/16$. That argument vanishes under $\|w\|^2 = 2$. So even the
*statement* of Conjecture 7.1 needs work before §7's heuristic implication
chain can be rewritten as a proof attempt.

### Refined selector conjecture (carried from v8)

> **Max-degsum selector.** For every 2-tree $G$ on $n \ge 4$, the simplicial
> degree-2 ear $v^*$ maximizing $\deg_{G-v^*}(a) + \deg_{G-v^*}(b)$ satisfies
> $\min(\delta^+(v^*), \delta^-(v^*)) \ge 17/16$.

This conjecture is unchanged from v8 and remains the new headline target.
Empirical: 725/725 at $n \le 10$ (min $1.2940$); BT$(50,2)$, BT$(100,2)$;
spider triples on $\le 200$ vertices; 433 passing tests.

The proof strategy in `lprime_max_degsum.md` §7 (via Conjecture 7.1) is
currently a heuristic, not a proof, and is further weakened by the $\|w\|^2$ fix.

## Revised step-by-step plan (v9)

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry; explicit $K_n$ spectrum | inline | **proved** |
| 2 | Corollary A (9.2(i) for claw-free, $\Delta \ge 3$) | Thm 1.1 + paths/cycles | paragraph | drafted |
| 3 | Corollary B (9.2(i) for $\mathrm{diam} \le 2$) | Thm 1.2 + check $K_{1,n-1}, C_5$ | paragraph | drafted |
| 4 | Short note (3–5 pp) on steps 1–3 | Exposition | 1–2 weeks | drafts merged; needs polish |
| 5a | (L') on books $B_k$ for $k \ge 2$ | Closed-form spectrum | done | **proved** |
| 5b | (L') on 2-paths $L_n$ asymptotic | Szegő for pentadiagonal sym Toeplitz | done | **proved** |
| 5c | (L') on 2-paths $L_n$ at finite $n$ | (a) interval-arithmetic + (b) non-simple-loop BBG / Widom analogue | research | **$n \le 200$ FP-certified; $n > 200$ open** |
| 5d | BT$(k,2)$ bad-ear asymptotic | Symmetry quotient + cubic resolvents | done | **proved** |
| 5e | Headline: prove max-degsum selector for general 2-trees | Clique-tree induction + Schur complement (Conj 7.1 reformulated) | open-ended | **headline open** |
| 5f | (L') on fans $F_n$ | Hub + path decomposition + secular eq | mid | **$n \le 200$ FP-certified; $n > 200$ conditional on 5c-type rate** |
| 5g | (L') on multi-arm spider 2-trees | Symmetry quotient + interlacing | mid | **Case I = books (redundant); Case II conditional on O5e.1** |
| 6 | If 5e succeeds, prove 9.2 for 2-trees | Telescope to $K_3$ | short | gated on 5e |
| 7 | Fallback: residue-control classes | Block-cut tree, perfect elimination, SDP/Gluing | open | not started |
| 8 | Near-extremal sanity ($n \le 30$) | Direct spectrum / Cauchy | 1 week | not started |

5a, 5b, 5d remain proved. 5c, 5f, 5g are *partially closed and partially
conditional* — the conditional half is now explicitly mapped to the same
non-simple-loop Toeplitz obstruction. 5e is the genuinely open mathematical
problem, the headline target.

## Three attack vectors (unchanged)

V1 ($P_3$-removal + residue control), V2 (SDP duality via Lemma 3.1, KKT), V3
(inertia / sign-pattern). See v7/v8 for honest catches. Edge-monotonicity
removed in v2 (Tang–Liu–Wang).

## Failure modes to guard against

- **F1.** Residue-component count $\ell$ is the whole problem, not cleanup.
- **F2.** Tacit reliance on EFGW in subclasses where it is open (sparse planar /
  unicyclic).
- **F3.** Near-extremal traps in part (ii): $K_n - e$, skewed $K_{p,q}$,
  $K_1 \vee (K_a \cup K_b)$, friendship, $K_{1,1,\ldots,1,2}$.
- **F4.** Regularity is not preserved by induced vertex deletion.
- **F5 (new in v9).** "Floating-point certified" $\ne$ interval-arithmetic
  certified. The 5c / 5f certificates use `numpy.linalg.eigvalsh`; observed
  forward error $\sim 3 \cdot 10^{-12}$ against slack $0.257$ is morally
  rigorous but not formally rigorous. Upgrade path: `mpmath` with declared
  precision, an `intervalarithmetic` Python library, or a Demmel–Kahan
  a-posteriori bound applied to the certified eigenvalues. Until then,
  publishable claims must say "verified numerically with high precision",
  not "proved".
- **F6 (new in v9).** Toeplitz-asymptotic *effective* constants — BBG
  (Bogoya–Böttcher–Grudsky 2018), Avram–Parter, Widom-type secular — are
  standardly stated under the **simple-loop symbol** hypothesis. The 2-paths
  symbol $f(\theta) = 2\cos\theta + 2\cos 2\theta$ has zeros at both an
  interior point $\theta = \pi/3$ and the boundary $\theta = \pi$, so the
  simple-loop hypothesis **fails**. Invoking "the Szegő rate" without an
  asymptotic analysis tailored to a non-simple-loop symbol is wishful, not
  bookkeeping. Any plan step that proposes to "close the tail by Szegő" must
  cite a non-simple-loop analogue or prove one.

## Concrete next action (v9)

1. **Bug fix pass** on `lprime_max_degsum.md`: change every $\|w\|^2 = 4$
   to $\|w\|^2 = 2$ in §2; rewrite (2.1) with $\sum c_i^2 = 2$; reformulate
   Conjecture 7.1 with the renormalised threshold $W^-_*$ derived from the
   secular equation under $\|w\|^2 = 2$; rewrite §7's implication argument
   as a *heuristic* not a proof. ~1 day.
2. **Status-fix pass** on `lprime_max_degsum.md` and `lprime_two_paths_finite.md`:
   add unambiguous "Status" boxes at the top of §5 (fans) and §6 (spider
   2-trees) recording the v9 downgrade. Add a "Status" box at the top of
   `lprime_two_paths_finite.md` recording (5c) as $n \le 200$ FP-certified +
   $n > 200$ open. ~½ day.
3. **Step 5e (headline).** Two parallel attacks:
   - **5e-a (structural).** Use the clique tree of the 2-tree. Prove that the
     max-degsum simplicial ear's supporting edge $\{a, b\}$ lies in a triangle
     whose third vertex has highest degree in $H$, then express
     $\sum_{i: \mu_i(H) < 0} c_i(v)^2$ as a structural functional of the
     clique-tree neighbourhood of $\{a, b\}$ via Schur complement on $A(H)$.
     This is the right form of "Conjecture 7.1" under the corrected
     normalisation.
   - **5e-b (interlacing).** Iterate Cauchy interlacing across the perfect
     elimination order; bound the negative-spectrum "slot deficits" by
     induction. Less ambitious but more mechanical; should at minimum
     produce a constant-factor bound that rules out $\delta^- < 1$.
4. **Step 5c.**
   - **5c-a.** Upgrade $n \le 200$ from FP to interval-arithmetic certified
     (`mpmath` at 50 digits; assert slack $\ge 0.25$). This makes the small-$n$
     half formally rigorous. ~1 day.
   - **5c-b.** Attack $n > 200$ by direct interlacing on the explicit
     pentadiagonal eigenvalue closed form, *not* by invoking BBG/Widom (which
     does not apply). Use $L_n = L_{n-1} + \text{rank-}2$ update with explicit
     eigenvector basis. Open-ended.
5. **Continue regression harness** (433 tests passing). Once any
   reformulation of Conjecture 7.1 is in place, add a regression
   `test_w_minus_lower_bound.py` measuring $W^-(v^*) - W^-_*$ on the same
   725 + 200 + 6 corpus.

## Critical reading (additions in v9)

Carried over from v8 plus: **Bogoya–Böttcher–Grudsky 2018** for the
simple-loop hypothesis (precise statement of which asymptotic constants are
controlled and under what symbol hypotheses); **Widom 1958** for the original
secular equation for finite Toeplitz; and standard numerical-linear-algebra
references for **Demmel–Kahan** a-posteriori eigenvalue bounds (a route to
formalising "FP-certified" without rewriting the harness in interval
arithmetic). Note these are *enabling* references for moving 5c into
formal-rigour status, not new results we cite.

## Open subobligations (v9)

- (**O5e.1**) **Book-arm monotonicity for multi-arm spiders** (carried from
  the Case II downgrade of `lprime_max_degsum.md` §6). For a spider 2-tree
  $S(k_1, k_2, k_3)$ with $k_1 \ge k_2 \ge k_3 \ge 1$, show that
  $\delta^-$ at the max-degsum ear is monotone non-increasing in $k_1$ at
  fixed $(k_2, k_3)$. Currently *admitted* in §6 Case II.
- (**O5e.2**) **Fan rigorous closure at $n > 200$**. Same blocker as 5c.
- (**O5c.1**) **Interval-arithmetic $n \le 200$ certification for 2-paths**
  (and fans). Mechanical with `mpmath`; promote to formal rigour.
- (**O5c.2**) **Non-simple-loop secular-rate constant** for
  $f = 2\cos\theta + 2\cos 2\theta$. The genuine research item under 5c-b.
- (**O7.1**) **Conjecture 7.1 reformulation** under $\|w\|^2 = 2$. Required
  before any "Conj 7.1 $\Rightarrow$ selector" argument can be written down
  as a proof.

## Open subtasks (status updated)

- `scripts/spectrum_check.py` — **implemented**.
- `tests/p3_removal_witness.py` — fallback, **not started**.
- `tests/two_tree_ear_gain.py` — **implemented**; $n \le 10$ data in
  `data/two_tree_ear_gains_n*.json`.
- `tests/test_lprime_subfamilies.py` — books + 2-paths $n \le 200$ + BT +
  fans + spiders. **Implemented**; part of 433 passing tests.
- `tests/test_max_degsum_selector.py` — **implemented**; seeded random
  2-trees at $n \in \{20, 30, 50, 100\}$.
- `tests/test_two_path_finite_n.py` — **implemented**.
- `tests/test_two_path_widom_tightness.py` — **implemented**.
- `tests/near_extremal_sanity.py` — **not started** (fallback, step 8).
- (**v9 NEW**) `tests/test_w_minus_lower_bound.py` — once O7.1 produces a
  reformulated Conjecture 7.1 with an explicit $W^-_*$, regression-test
  $W^-(v^*) \ge W^-_*$ on the 725 + 200 + 6 corpus.
- (**v9 NEW**) `scripts/mpmath_certify.py` — interval-arithmetic upgrade of
  the $n \le 200$ FP certificates for 2-paths and fans (O5c.1).
- (**v9 NEW**) `tests/fixtures/w_norm_squared_is_2.json` — small-case
  regression preventing the $\|w\|^2 = 4$ bug from being silently
  reintroduced.

These subtasks reflect v9 state. The Phase-3 universal-lemma regression
under `tests/fixtures/two_tree_universal_counterexamples.json` is kept
permanently.
