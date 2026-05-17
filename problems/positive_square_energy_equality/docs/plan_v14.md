# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v14** (this version): incorporates Phase 12 — the two-week strategic
  branch on (A) the positive-side ceiling lemma and (B) Thm 8.1 hypothesis
  weakening. **Both branches returned clean negative results.** The net
  effect is to *exhaust the plausible tractable routes* to the headline
  candidate ansatz condition (b), and to pivot the workstream from
  research-attack mode to paper-writing mode. Three headline outcomes:

  1. **Phase 12.A — Positive-side ceiling lemma derived; trace-identity
     reformulation does not break the slot-shift wall.** A clean dual
     **Lemma B1+** was derived via the trial vector $z_+(\beta) = \tilde w_+ + \beta e_v$:
     $$\lambda_{\max}(A(G)) \ge \frac{M_1^+(v) + \sqrt{(M_1^+(v))^2 + 4 W^+(v)^3}}{2 W^+(v)}, \quad W^+(v) > 0.$$
     **However:**
     - Under the trace identity $\delta^+ + \delta^- = 4$, the target $\delta^- \ge 1$
       flips to $\delta^+ \le 3$, and the Rayleigh-trial-vector direction
       flips with it. Lemma B1+ gives a *lower* bound on $\lambda_{\max}^2$
       (the maximally positive eigenvalue); $\delta^+ \le 3$ requires an
       *upper* bound. The trial-vector technique can't deliver this.
     - The "asymmetry between $s^+$ and $s^-$" hypothesis (Elphick–Linz)
       was the strategic motivation: maybe the positive side admits a
       cleaner ceiling. **Empirically FALSIFIED.** Tightness ratios on the
       2235-record max-degsum corpus: positive-side mean $1.164$, negative-side
       mean $1.137$ — within 3%. The positive side is NOT structurally
       tighter. Mirror F11 (now F11+) fires: $\alpha^+_{\text{top}}$ can be
       as small as $1.98 \times 10^{-5}$ on $L_n$ Case B$_+$, while Lemma B1+
       bounds $\alpha^+_{\min} = \lambda_{\max}$.
     - **Modest new side-fact (proved):** $\lambda_{\max}(A(G)) \ge 2$
       unconditionally at every max-degsum simplicial degree-2 ear of every
       2-tree with $n \ge 4$ (using $M_1 = 2$ + Lemma B1+). Sharp on
       $B_2 = K_4 - e$. Publishable footnote.

  2. **Phase 12.B — Thm 8.1 weakening is upstream-bound and uniformly
     inapplicable.** The constant $17 = 1 + 16$ in the hypothesis
     $\alpha(G)\omega(G) \le n/17$ comes directly from $\epsilon = 1/16$ in
     Zhang's improved $P_3$-removal lemma (Lemma 2.4 of the source paper).
     Improving 17 means improving Zhang's $\epsilon$ — research on Zhang
     2024, not on Conj 9.2.

     **Empirical result (1795-graph corpus, $n \le 14$):** **ZERO graphs
     satisfy $\alpha\omega \le n/17$.** Across all connected graphs from the
     atlas + random ER samples. Thm 8.1's practical content lives in dense
     random graphs $G(n, 1/2)$, a regime where Conj 1.1 was already known
     via hyper-energetic methods.

     **2-trees specifically: $\alpha\omega \approx n$**, so the route never
     engages on the chosen workstream target.

     **Verdict:** not worth a person-month. Diagnostic infrastructure
     preserved (`scripts/alpha_omega_exploration.py`,
     `data/alpha_omega_corpus.json`) so the verdict can be reconfirmed in
     seconds by future investigators.

  3. **Pivot to paper-writing mode.** With Phase 12's negative results
     closing both plausible attack branches, the remaining critical-path
     open problem is **O12.2 — the slot-shift sum bound** (condition (b)
     of the candidate ansatz). This is genuinely research-grade and
     estimated 6 person-months to 2 years for a dedicated expert. The
     cost/value calculus now strongly favours **banking the substantial
     proved results as a paper** rather than continuing to attack (b).

     The paper's contribution stack (proposed) and its target are
     documented in §"Paper outline (v14)" below.

  Two new failure modes (F14, F15) record the Phase 12 lessons.

  What v14 calls **unconditionally established** (new since v13):
  - Lemma B1+ (Rayleigh ceiling on $\lambda_{\max}$ via $(W^+, M_1^+)$).
  - $\lambda_{\max}(A(G)) \ge 2$ at max-degsum simplicial deg-2 ears of
    2-trees with $n \ge 4$, sharp on $B_2$.
  - Empirical: zero connected graphs at $n \le 14$ satisfy
    $\alpha\omega \le n/17$.

  **Carried** unconditionally: Phase 10+11 (a.2-path) theorem, all earlier
  proved subfamilies, the corrected Case B slot decomposition, Lemma B1,
  Phase 9 b.minor sufficient condition.

  Test suite: **519/519 passing** (508 after v13 Phase 11; +11 from Phase 12.A).

- **v13**: Phase 10 (Stieltjes-transform half-line spectral theorem) +
  Phase 11 (Portmanteau closure); (a.2-path) upgraded to fully proved
  theorem. F12 sharpened, F13 added.
- **v12**: Phase 8 (Lemma B1) + Phase 9 (a.2-path candidate, b.minor sign
  correction); F11, F12 added; sign error in Phase 8 §3.2 retracted.
- **v11**: Phase 7 candidate ansatz; not yet a conjecture; F10 added.
- **v10**: retired Conjecture 7.1; 5c closed for $n \le 2000$ via DK;
  F7, F8, F9.
- **v9**: $\|w\|^2 = 2$ bug fix; F5, F6.
- **v8**: Phase 4 — books, 2-paths-asymptotic, BT proved.
- **v7**: Phase 3 universal-lemma falsification; (L').
- **v6**: 2-trees as first serious target.
- **v5–v1**: earlier revisions.

## The conjecture (verbatim, Section 9 of the source paper)

Let $G$ be a **connected** graph of order $n$.
- **(i)** $s^+(G) = n - 1$ iff $G$ is a tree.
- **(ii)** $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.

## Why this conjecture, and the honest tractability verdict

Unchanged from v8–v13.

## Background, easy direction, and central obstruction

Unchanged from v8. Crude telescoping bound is $s^\pm(G) \ge n + k/16 - \ell$;
$P_3$-removal slack $17/16$ actively selects cut vertices.

## What the modest deliverables look like

Unchanged. Corollary A (claw-free), Corollary B (diameter $\le 2$).
Drafted in [`corollaries_AB.md`](corollaries_AB.md).

## What a serious result would require, and where to look

Unchanged search directions: 2-trees (chosen target).

### First serious target: 2-trees

Target theorem (carried unchanged):
> If $G$ is a 2-tree on $n$ vertices, then Conjecture 9.2 holds for $G$.

Via (L'):
> Let $G$ be a 2-tree with $n \ge 4$. There exists a simplicial degree-2
> vertex $v^*$ with $\delta^+(v^*) \ge 17/16$ and $\delta^-(v^*) \ge 17/16$.

### Corrected Case A / Case B slot decomposition

Carried from v12.

### Phase 4–11 progress (carried)

- Books $B_k$, 2-paths Szegő asymptotic, BT bad ear (Phase 4).
- 5c rigorous closure for $n \le 2000$ (Phase 6).
- Phase 7 candidate ansatz $I = W^- + (M_1^-)^2/M_2^-$ at $T = 0.4122$.
- Phase 8 Lemma B1 + sub-route closures for (a) on books, BT-page.
- Phase 9 (a.2-path) candidate closed form + (b.minor) sign correction
  and $\alpha_{\min}^2 \ge 1$ on Case B max-degsum.
- Phase 10 + 11: $\lim_n I(L_n, v^*) = I_\infty(L) \approx 1.0157$ as a
  **theorem** via Stieltjes + Portmanteau.

### Phase 12 progress (new in v14) — two negative results

**Phase 12.A — Positive-side ceiling lemma (Lemma B1+).**

Lemma B1+ (proved):
> Let $G$ be a 2-tree on $n \ge 4$ vertices and $v$ a simplicial degree-2
> ear with $W^+(v) > 0$. Then
> $$\lambda_{\max}(A(G)) \ge \frac{M_1^+(v) + \sqrt{(M_1^+(v))^2 + 4 W^+(v)^3}}{2 W^+(v)}.$$

Empirical results on the 2235-record max-degsum corpus:
- Mean tightness ratio $\lambda_{\max}/f^+_{\max} = 1.164$; max $1.788$;
  min $1.000$ (tight on books, sharp at $B_2$).
- $\max \delta^+(v^*) = 2.7059$ (slack $0.29$ to the $\delta^+ \le 3$ target).
- **Negative-side tightness ratio for Lemma B1**: $1.137$. Within 3% of
  the positive side. **The asymmetry hypothesis is falsified.**

The trace-identity reformulation $\delta^- \ge 1 \iff \delta^+ \le 3$ does
NOT decouple the wall: the Rayleigh trial-vector flips direction with
the target, so Lemma B1+ gives the *wrong-direction* bound. F14 (new).

**Modest new side-fact (proved):** Using $M_1 = 2$ at any max-degsum ear
(since $\{a, b\} \in E(H)$), Lemma B1+ gives unconditionally
$\lambda_{\max}(A(G)) \ge 2$ at every max-degsum simplicial deg-2 ear of
every 2-tree on $n \ge 4$ vertices. Sharp on $B_2 = K_4 - e$.

Files (Phase 12.A): `docs/lprime_positive_side_ceiling.md`,
`scripts/positive_side_ceiling.py`,
`tests/test_positive_side_ceiling.py` (11 tests),
`data/positive_side_ceiling_census.json`.

**Phase 12.B — Thm 8.1 hypothesis weakening is dormant.**

Thm 8.1 of arXiv:2506.07264: if $G$ is connected with $\alpha(G)\omega(G) \le n/17$,
then $\min(s^+, s^-) \ge n$, hence Conj 9.2 holds for $G$. The constant
$17 = 1 + 16$ enters as $c = \epsilon/(1+\epsilon)$ with $\epsilon = 1/16$
from Zhang's improved $P_3$-removal (Lemma 2.4 of the source paper).

**Empirical exploration on 1795-graph corpus** ($n = 2, \ldots, 14$, atlas
+ random ER samples):
- **ZERO graphs satisfy $\alpha\omega \le n/17$.** Even at $n = 14$, no
  graph crosses the threshold.
- The smallest $\alpha\omega/n$ in the corpus is $0.32$ at the friendship-graph
  $F_3$ family; the infimum among violators is $\sim 1.0$ on dense random.
- **2-trees** have $\alpha\omega \approx n$ (since $\omega = 3$ and
  $\alpha \ge n/3$), so Thm 8.1 is uniformly inapplicable.

**Verdict.** Thm 8.1's practical content is the dense random regime
$G(n, 1/2)$, where Conj 1.1 was already known via hyper-energetic
methods. Improving 17 requires research on Zhang 2024's polynomial-inequality
constants, **upstream of this workstream**. Not worth a person-month.
F15 (new).

Files (Phase 12.B): `docs/lprime_alpha_omega_weakening.md`,
`scripts/alpha_omega_exploration.py`,
`data/alpha_omega_corpus.json` (688 kB, 1795 records).

### Candidate ansatz (v11+) — status after Phase 12

> $I(v) := W^-(v) + (M_1^-(v))^2 / M_2^-(v)$ at threshold $T \approx 0.4122$.

Condition (a):
- Books $B_k$ ($k \ge 2$): **proved** unconditionally.
- BT$(k, 2)$ max-degsum (book-page): **proved** by reduction to books.
- 2-paths $L_n$: **proved** (Phase 10 + 11; finite-$n \to \infty$).
- Fans $F_n$: $n \le 200$ FP-certified, tail open.
- **General 2-trees: open.**

Condition (b):
- All subfamilies: **open**. The slot-shift sum bound (O12.2) is the
  unified wall. Phase 8 Lemma B1 + Phase 9 b.minor + Phase 12.A Lemma B1+
  all bound $\alpha_{\min}^2$ or $\alpha^+_{\min}^2$ — none bounds
  $\delta^-$ or $\delta^+$ directly (F11, F11+).

### Refined selector conjecture (carried from v8)

> **Max-degsum selector.** Unchanged. Empirical: 725/725 at $n \le 10$;
> BT$(k, 2)$ for $k \le 500$; random 2-trees up to $n = 1000$; 2235
> max-degsum records in `data/case_AB_census.json`, all
> $\delta^- \ge 1.2941$.

## Revised step-by-step plan (v14)

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry; $K_n$ spectrum | inline | **proved** |
| 2 | Corollary A | Thm 1.1 + paths/cycles | paragraph | drafted |
| 3 | Corollary B | Thm 1.2 + $K_{1,n-1}, C_5$ | paragraph | drafted |
| 4 | Short note on 1–3 | Exposition | 1–2 weeks | drafts merged |
| 5a | (L') on books $B_k$ | Closed form | done | **proved** |
| 5b | (L') on 2-paths Szegő ($\delta^-$) | Symbol $f = 2\cos\theta + 2\cos 2\theta$ | done | **proved** |
| 5c | $\delta^-(L_n) \ge 17/16$, $n \le 2000$ | DK + mpmath | done | **rigorous** |
| 5c.tail | $\delta^-(L_n)$ for $n > 2000$ | Non-simple-loop BBG (O5c.3) | research | open |
| 5d | BT$(k, 2)$ bad-ear | Cubic resolvents | done | **proved** |
| 5e | Headline: max-degsum selector | Candidate ansatz (a) + (b) | open | headline open |
| 5e.a.books | $I(v^*) \ge T$ on $B_k$ | Cauchy–Schwarz saturation | done | **proved** |
| 5e.a.BT-page | $I(v^*) \ge T$ on BT max-degsum | Reduction to books | done | **proved** |
| 5e.a.2-path | $\lim I(L_n, v^*) = I_\infty(L) > T$ | Stieltjes + Portmanteau | done | **proved (Phase 10 + 11)** |
| 5e.a.general | $I(v^*) \ge T$ for general 2-trees | Clique-tree + moments | research | open (estimated 1–3 person-months) |
| 5e.b | $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$ | Slot-shift sum bound | research | open (O12.2; estimated 6 person-months to 2 years; **the wall**) |
| 5e.lemma_B1 | $\lambda_{\min}^2$ Rayleigh lower bound | Trial vector $z(\beta)$ | done | **proved (Phase 8)** |
| 5e.lemma_B1plus | $\lambda_{\max}^2$ Rayleigh lower bound | Trial vector $z_+(\beta)$ | done | **proved (Phase 12.A)** |
| 5e.lambda_max_geq_2 | $\lambda_{\max}(A(G)) \ge 2$ at max-degsum ears | $M_1 = 2$ + Lemma B1+ | done | **proved (Phase 12.A)**, sharp on $B_2$ |
| 5e.b_minor.alpha_min_one | $\alpha_{\min}^2 \ge 1$ on Case B max-degsum | Lemma B1 + suff. cond. | done | **proved (Phase 9)** (F11) |
| 5e.slot_shift | $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge $ const | Unified wall | **research; THE wall** | open |
| 5f | (L') on fans $F_n$ | Hub + path; DK | done for $n \le 200$ | tail via 5c-tail |
| 5g | (L') on multi-arm spider 2-trees | Symmetry + interlacing | partial | Case I = books; Case II cond. on O5e.1 |
| 6 | If 5e succeeds, prove 9.2 for 2-trees | Telescope to $K_3$ | short | gated on 5e |
| 7 | Fallback: residue-control / $\alpha\omega$ classes | Block-cut, perfect elim, SDP | **dormant after Phase 12.B** | $\alpha\omega$ route empirically inapplicable; other fallbacks remain open as research |
| 8 | Near-extremal sanity ($n \le 30$) | Direct spectrum / Cauchy | 1 week | not started (low priority) |

The headline open critical-path items are now **just two**:
- **5e.a.general** (1–3 person-months, tractable; the clique-tree machinery already exists).
- **5e.slot_shift / O12.2** (6 person-months to 2 years; the wall).

All other open items are either fallback or low-priority cleanup.

## Three attack vectors (unchanged)

V1, V2, V3.

## Failure modes to guard against

- **F1.** Residue-component count $\ell$ is the whole problem.
- **F2.** Tacit reliance on EFGW in subclasses where it is open.
- **F3.** Near-extremal traps in part (ii).
- **F4.** Regularity not preserved by induced vertex deletion.
- **F5.** "Floating-point certified" $\ne$ interval-arithmetic certified.
- **F6.** BBG-type asymptotic constants assume simple-loop symbol; ours fails.
- **F7.** Single-scalar selector thresholds at the naturally-scaled values
  $17/16$ or $17/32$ are categorically wrong (smaller empirical thresholds
  may survive on a finite corpus).
- **F8.** mpmath @ high-precision $\ne$ interval arithmetic.
- **F9.** Case B carries $\delta^-$ without $W^-$ support.
- **F10.** Stage-1 "gap" is a condition-(a) statistic, not an
  implication-margin statistic.
- **F11.** $\alpha_{\min}$ vs $\alpha_{\text{top}}$ are different
  quantities; bounding one does not bound the other.
- **F12.** Boundary spectral density for half-line banded Toeplitz is the
  signed angle gap $\sin(\theta_2 - \theta_1)/\pi$, NOT the naive
  $(\sin\theta + \sin 2\theta)^2/\pi$.
- **F13.** Portmanteau on signed moments: $\lambda^k \mathbf{1}[\lambda < 0]$
  is continuous at 0 for $k \ge 1$; only $k = 0$ needs the no-atom step.
- **F14 (new in v14).** **The trace-identity reformulation does not
  decouple the slot-shift wall.** $\delta^- \ge 1 \iff \delta^+ \le 3$
  flips the target direction, and the Rayleigh trial-vector machinery
  flips with it: Lemma B1+ gives a *lower* bound on $\lambda_{\max}^2$,
  whereas the slot decomposition needs an *upper* bound on
  $(\alpha^+_{\text{top}})^2$. Under the trace identity, the positive-side
  wall and O12.2 carry **identical analytical content**. The
  "$s^+$/$s^-$ asymmetry could provide a wedge" strategic hypothesis is
  **empirically falsified** (positive vs negative Lemma B1 tightness
  ratios within 3% on 2235 records).
- **F15 (new in v14).** **Thm 8.1's hypothesis $\alpha(G)\omega(G) \le n/17$
  is empirically inapplicable.** Zero connected graphs at $n \le 14$
  satisfy it. 2-trees specifically have $\alpha\omega \approx n$ and are
  uniformly excluded. Thm 8.1's practical content is dense random
  $G(n, 1/2)$ where Conj 1.1 was known by other methods. Weakening the
  constant 17 requires improving Zhang 2024's $P_3$-removal slack —
  research **upstream** of this workstream. Verdict: not a viable
  fallback route for the 2-tree slice of Conj 9.2.

## Concrete next action (v14)

The workstream pivots from research-attack to paper-writing. Two parallel
tracks:

### Track 1 — Paper preparation (primary)

Draft the arXiv submission with the 11-item contribution stack (see
"Paper outline" below). Estimated 4–8 weeks for a clean draft + 1–2
weeks for internal review. Target venue: JCTB / JCTSer A / Combinatorica
or arXiv-first with a follow-up journal submission.

### Track 2 — 5e.a.general (secondary, optional)

If person-months are available *in parallel* with paper-writing, attack
condition (a) for general 2-trees via the clique-tree machinery in
`lprime_5e_a_structural.md`. The empirical floor is now pinned exactly:
$I_\infty(L) \approx 1.0157$ on 2-paths is the binding case. The proof
target: $I(v^*) \ge I_\infty(L)$ for every max-degsum ear of every 2-tree.
Schur-complement induction on the clique tree, with $L_n$ as the base.

If 5e.a.general lands, it strengthens the paper (condition (a) becomes
unconditional on 2-trees) but does not change the headline status of
condition (b).

### Not on critical path

- O12.2 / 5e.slot_shift remains the wall. **Do not commit person-months
  here.** Wait for external feedback / a breakthrough from another area
  (Toda flow / Jacobi-matrix perturbation theory / a Cauchy-style integral
  identification).
- 5c.tail ($n > 2000$ via non-simple-loop BBG) is mechanical extension;
  not critical-path.
- Fallback routes (residue-control beyond Thm 8.1, block graphs, chordal
  beyond treewidth 2) remain dormant.

## Paper outline (v14)

Working title: **"The 2-tree ear-selection lemma and the joint-invariant
ansatz for positive square energy"** (or similar — Akbari–Mohar–Zhang
will cite this when Conj 9.2 finally falls).

### Contribution stack

1. **Corollaries A, B** — claw-free ($\Delta \ge 3$) and diameter-$\le 2$
   slices of 9.2(i), as direct corollaries of Thms 1.1, 1.2 of the source
   paper. Short.
2. **Books $B_k$ closed form**: $\delta^-(B_k) = 2 - 4/(\sqrt{8k+1}+\sqrt{8k-7})$.
3. **2-paths Szegő closed form** for $\delta^-$:
   $\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi)$.
4. **BT$(k, 2)$ bad-ear asymptotic**: $\delta^-_\infty(\mathrm{BT}) \approx 1.0353 < 17/16$,
   the structural family that refuted the universal ear lemma.
5. **Demmel–Kahan rigorous certificate** for $\delta^-(L_n) \ge 17/16 + 1/4$,
   all $n \in [4, 2000]$.
6. **The (L') framework** — the existential ear-selection lemma as the
   right reformulation after the universal-form falsification.
7. **The candidate ansatz** $I = W^- + (M_1^-)^2/M_2^-$ at $T = 0.4122$,
   robust on 1063+ graph corpus.
8. **Phase 8 Lemma B1** + **Phase 12.A Lemma B1+** — Rayleigh closed-form
   bounds on $\lambda_{\min}, \lambda_{\max}$ from $(W^\pm, M_1^\pm)$. Tight
   on books. Corollary: $\lambda_{\max}(A(G)) \ge 2$ at every max-degsum
   simplicial deg-2 ear of every 2-tree with $n \ge 4$, sharp on $B_2$.
9. **Phase 9 (b.minor)** sufficient condition $|M_1^-| \ge W^-(1 - W^-)$
   gives $\alpha_{\min}^2 \ge 1$ on Case B max-degsum ears.
10. **Phase 10 + 11: $\lim_n I(L_n, v^*) = I_\infty(L) \approx 1.0157$**
    as a theorem via the Stieltjes-transform identification of the
    half-line boundary spectral density $\sin(\theta_2 - \theta_1)/\pi$
    plus Portmanteau closure for the finite-$n$ moments.
11. **Failure-modes appendix** — the negative knowledge encoding the
    $\|w\|^2 = 4 \to 2$ bug, the false universal lemma, the single-scalar
    selector retirement, the Phase 8 sign error, the naive sine-basis
    falsification for the boundary density, the trace-identity-symmetry
    falsification (Phase 12.A), the $\alpha\omega$-route uniform
    inapplicability (Phase 12.B), and the corrected slot decomposition.
    This is the "lessons learned" section saving the next researcher months.

### Open problems explicitly listed

- **Conjecture v11.candidate (max-degsum selector)**: condition (a) on
  general 2-trees (likely months); condition (b) for all subfamilies
  (the wall, likely years).
- **O12.2**: the slot-shift sum bound — *the* analytical bottleneck.
- **The full Conj 9.2** — 2-trees is one slice; the residue-control and
  $\alpha\omega$-regime routes remain dormant.

### Suggested venues

- **arXiv first** as a research note: combinatorics + spectral theory + numerical analysis crossover.
- **JCT B / JCT A / Combinatorica** for the journal version after community feedback.
- The Akbari–Kumar–Mohar–Pragada–Zhang follow-up (arXiv:2506.07264 has been moving forward — check if they have addressed any of our open subobligations).

## Critical reading (unchanged from v13)

Carried: arXiv:2506.07264, arXiv:1409.2079 (EFGW), arXiv:2303.11930,
arXiv:2311.11530, arXiv:2410.09830, arXiv:2409.15504, arXiv:2409.18220,
Bogoya–Böttcher–Grudsky 2018, Demmel, Wilkinson, Avram–Parter 1988, Simon
2011, Trefethen–Embree 2005, Reed–Simon Vol I, Billingsley.

## Open subobligations (v14)

- **(O5e.1)** Book-arm monotonicity for multi-arm spiders. **Status: low priority** for paper.
- **(O5e.2)** Fan rigorous closure at $n > 200$. **Status: deferred to 5c-tail**.
- **(O5e.3)** Joint-invariant ansatz: (a) on books, BT-page, 2-paths
  closed; **(a) on general 2-trees** = 5e.a.general open (Track 2 of v14).
- **(O5c.3)** Non-simple-loop BBG analogue for $n > 2000$. **Mechanical;**
  defer until the paper is on arXiv.
- **(O12.2)** **Slot-shift sum bound** — **THE wall**. Do not attack; wait
  for external breakthrough or community feedback after paper.
- **(O13.1)** DK rate for (a.2-path) — mechanical; defer.
- **(O13.2)** Branch convention formality — minor; defer.
- **(O13.3)** Trig line in §4 of `lprime_a_two_path_stieltjes.md` — one-line
  cleanup; do during paper preparation.

## Open subtasks (status updated in v14)

Carried from v13 (all implemented unless flagged).

**(v14 NEW — Phase 12)**:
- `scripts/positive_side_ceiling.py` — Phase 12.A Lemma B1+ exploration.
- `tests/test_positive_side_ceiling.py` — 11 tests, all passing.
- `data/positive_side_ceiling_census.json` — 2235-record corpus.
- `docs/lprime_positive_side_ceiling.md` — Phase 12.A research note.
- `scripts/alpha_omega_exploration.py` — Phase 12.B exploration.
- `data/alpha_omega_corpus.json` — 1795-graph corpus.
- `docs/lprime_alpha_omega_weakening.md` — Phase 12.B research note.

**(v14 NEW — paper-writing track)**:
- `paper/` — new subdirectory for the arXiv submission draft.
- `paper/outline.md` — explicit 11-section outline matching the
  contribution stack above.
- `paper/figures/` — TikZ / Python-generated figures (corpus scatter
  plots, BT family illustration, etc.).
- `paper/bibliography.bib` — references compiled from `Critical reading`.

The permanent regression fixtures are kept:
`tests/fixtures/two_tree_universal_counterexamples.json` (v7),
`tests/fixtures/w_norm_squared_is_2.json` (v9),
`tests/fixtures/joint_invariant_falsified.json` (v10 / Phase 7),
`tests/fixtures/case_B_slot_decomposition.json` (v12, if created).

## Summary of v14 state

- **5c (2-paths $\delta^-$)**: rigorous $n \in [4, 2000]$; tail $n > 2000$
  open (O5c.3, mechanical).
- **5e headline (max-degsum selector)**: open.
- **5e.a (condition (a))**: proved on books, BT-page, **2-paths
  (asymptotic, Phase 10 + 11)**; general 2-trees open (1–3 person-months).
- **5e.b (condition (b))**: open for all subfamilies; **slot-shift sum
  bound (O12.2) is the wall** (6 person-months to 2 years).
- **Phase 12 negative results recorded**: trace-identity reformulation
  doesn't decouple the wall (F14); Thm 8.1 weakening dormant (F15).
- **Test suite**: 519/519 passing.
- **Workstream pivot**: research-attack mode → **paper-writing mode**.
  Target: arXiv draft 4–8 weeks; journal submission after feedback.
  Track 2 (5e.a.general) is optional parallel research.

The workstream has produced 11 named contributions and 15 catalogued
failure modes. The candidate ansatz (a) is proved on 3 of 4 recognised
subfamilies; (b) is open with a precisely-identified wall. Conjecture 9.2
on 2-trees remains open — but the path to it is now mapped, with the
remaining work scoped to two concrete problems of widely-different
difficulty.
