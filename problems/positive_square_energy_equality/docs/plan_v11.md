# Plan: prove (a tractable slice of) Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang

Source: arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*, June 2025.

**Revision history.**

- **v11** (this version): incorporates the reviewer pass on the Phase 7
  joint-invariant ansatz search. Two headline outcomes:
  1. **A non-falsified candidate ansatz exists**, but the v10 framing
     "Conjecture 7.1 retired, joint-invariant Conjecture v10.1 replaces it
     with form open" was both right and wrong. **Right**: the natural
     $17/16$ / $17/32$ single-scalar threshold form is dead. **Wrong**:
     v10's F7 said "single-scalar selector thresholds are categorically
     wrong"; the agent showed that at an empirically-fitted threshold
     $T \ll 17/32$, even single-scalar candidates like $W^-(v)$ or
     $|M_1^-(v)|$ survive on the corpus. v11 softens F7 accordingly.
  2. **The "candidate" is not yet a conjecture.** The Phase-7 agent
     identified the Cauchy–Schwarz-motivated functional
     $$I(v) := W^-(v) + (M_1^-(v))^2 / M_2^-(v), \quad T \approx 0.4122$$
     with a Stage-1 "gap" of $0.4523$ on a 1063-graph corpus, and zero
     violations on Stage-2 held-out random 2-trees. Role 5's audit
     verified the Stage-1 numbers exactly, but identified that the
     **0.4523 headline is a condition-(a) statistic, not an
     implication-margin statistic**. The true margin on the implication
     direction (b) — $\min\{\delta^-(v) - 17/16 : I(v) \ge T\}$ on the
     all-ears corpus — is **0.082** in the worst observed case at
     $n \le 100$, drops to **0.082** at $n = 500$, and shows no sign of
     stabilising as $n$ grows. The implication is empirically alive but
     **thin**, not robust.
  3. **Renaming.** v11 calls $I, T$ the **candidate ansatz**, not
     "Conjecture v10.2". Reserve "Conjecture" for once an analytical
     sketch of either (a) or (b) is on the table.
  4. **Corpus strengthening.** Phase-7 stopped at $n = 200$ for random
     2-trees, so the implication direction (b) was tested against
     **only 2 bad ears** (BT$(50, 2)$ and BT$(100, 2)$ tails). Role 5
     ran extensions: 30 random seeds at $n = 500$ (7 bad ears), 5 seeds
     at $n = 1000$ (2 bad ears), BT$(k, 2)$ for $k \in \{200, 300, 500\}$
     (additional structured tail ears). Still **no violations**, but the
     implication margin tightens, not loosens, with $n$. **v11 mandates**
     the regression suite be extended to 50 seeds at
     $n \in \{500, 1000, 2000\}$ and to BT$(k, 2)$ for
     $k \in \{200, 500, 1000\}$.
  5. **Threshold-tightening.** $T = 0.4122$ is the trivial Stage-1
     midpoint between the worst max-degsum ear's $I$ value and the best
     bad ear's $I$ value. A smaller threshold *expands* the set of ears
     against which (b) is tested, sharpening the analytical target. v11
     recommends $T = 0.25$ (closer to the upper bound of the bad-ear
     side) as the working threshold for the proof attack.
  6. **F7 softened.** v10's "single-scalar selector thresholds are
     categorically wrong" was a clean retirement of the naturally-scaled
     $17/16$ / $17/32$ thresholds. v11 records the distinction: those
     thresholds *are* categorically wrong; other thresholds may survive
     on a finite corpus but the window closes asymptotically (the
     bad-ear $\max W^-$ approaches the max-degsum-ear $\min W^-$ from
     below as the structured family grows). A non-trivial **joint
     invariant** widens the window robustly; a single scalar does not.
- **v10**: retired Conjecture 7.1; recorded 5c rigorously closed for
  $n \le 2000$ via Demmel–Kahan; introduced Conjecture v10.1 with form
  open; added F7, F8, F9; opened O5e.3 (joint-invariant search) and
  O5c.3 (non-simple-loop BBG analogue).
- **v9**: reviewer pass — $\|w\|^2 = 2$ bug fix; Conjecture 7.1
  renormalised; fans / spider Case II downgraded; F5, F6, O5c.1,
  O5c.2, O5e.1, O5e.2, O7.1.
- **v8**: Phase 4 — books / 2-paths-asymptotic / BT proved; max-degsum
  selector replaces v7 O2 as the new headline target.
- **v7**: Phase 3 universal-lemma falsification; trace identity;
  existential ear-selection lemma (L').
- **v6**: mathematician pass — 2-trees as first serious target.
- **v5**: domination $\le 2$ connected, $s^+$ only; $P_3$-removal
  sign-specific; Conj 9.1 adjacent evidence.
- **v4**: domination scoped; $K_1$ endpoint; $s^+$ residue refined.
- **v3**: six logical corrections — EFGW connected, $\ell < k/16 + 1$
  sufficient not necessary, Lemma 3.1 no support restriction, etc.
- **v2**: dropped false connectivity-via-$P_3$-removal; dropped
  $-A$ dualization.
- **v1**: original draft.

What v11 calls **unconditionally established** (carried from v10): the
clique-tree formalization of 2-trees; the trace identity $\delta^+ + \delta^- = 4$
at any degree-2 simplicial ear; books $B_k$ for all $k \ge 2$; the BT$(k, 2)$
asymptotic; the 2-paths Szegő asymptotic $\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi)$;
$\delta^-(L_n) \ge 17/16 + 1/4$ for $n \in [4, 2000]$ via Demmel–Kahan;
the negative result that the single-scalar $W^-$ threshold at the
naturally-scaled $17/32$ value is empirically falsified by $L_6$
($W^-(L_6, v^*) = 0.380$); the clique-tree identity
$M_2 = \sigma(v) + 2|T_{ab}(H)|$; the Cauchy–Schwarz bound
$W^-(v) \ge (M_1^-(v))^2 / M_2^-(v)$.

What v11 records as **empirically unfalsified but not yet proved**:
the candidate ansatz $I(v) = W^-(v) + (M_1^-(v))^2 / M_2^-(v)$ at
$T = 0.4122$ (or v11-recommended $T = 0.25$) over a corpus of 1063 graphs
plus Role 5's extension (BT$(k, 2)$ for $k \le 500$, random
2-trees at $n \le 1000$). 467/467 tests passing.

## The conjecture (verbatim, Section 9 of the source paper)

Let $G$ be a **connected** graph of order $n$.
- **(i)** $s^+(G) = n - 1$ iff $G$ is a tree.
- **(ii)** $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.

Notation: $\lambda_1 \ge \cdots \ge \lambda_n$ are the adjacency eigenvalues of $G$;
$s^+(G) := \sum_{\lambda_i > 0} \lambda_i^2$, $s^-(G) := \sum_{\lambda_i < 0} \lambda_i^2$;
$\mathrm{tr}(A^2) = 2m = s^+ + s^-$.

## Why this conjecture, and the honest tractability verdict

Unchanged from v8/v9/v10.

## Background, easy direction, and central obstruction

Unchanged from v8. Crude telescoping bound is $s^\pm(G) \ge n + k/16 - \ell$;
$P_3$-removal slack $17/16$ actively selects cut vertices; this is the
fatal obstruction outside strongly-structured classes.

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

### Phase 4–7 progress (carried over)

**Phase 4 — proved subfamilies:**
- Books $B_k$ (unconditional): $\delta^-(B_k) = 2 - 4/(\sqrt{8k+1} + \sqrt{8k-7})$.
- 2-paths Szegő asymptotic: $\delta^-_\infty(L) = (32\pi - 27\sqrt 3)/(12\pi)$.
- BT$(k, 2)$ bad-ear asymptotic: $\delta^-_\infty(\mathrm{BT}) \approx 1.0353$.

**Phase 5 — bug fix + statuses:** $\|w\|^2 = 2$ correction propagated;
status boxes; regression fixture.

**Phase 6 — 5c rigorous closure:** $\delta^-(L_n) \ge 17/16 + 1/4$ for
$n \in [4, 2000]$ via Demmel–Kahan + mpmath at dps = 50. Tail
$n > 2000$ open (O5c.3).

**Phase 6 — Conjecture 7.1 retirement (with v11 nuance):** the
naturally-scaled $17/32$ single-scalar $W^-$ threshold is empirically
falsified on $L_6$ ($W^-(L_6, v^*) = 0.380 < 17/32 \approx 0.531$). The
structural reason $K_3 \to K_2$ has $W^- = 0$ with $\delta^- = 1$ is
about the **Case B new eigenvalue**, not the corpus min of $W^-$. **The
v10 framing "categorically wrong" overstated the case.** A smaller-than-natural
threshold may survive — see Phase 7 below.

### Phase 7 progress (new in v11)

The Phase 7 search swept degree-$\le 2$ polynomial functionals of
$(W^-, W^0, c_{n-1}^2, M_1^-, M_2^-)$ on a corpus of 1063 graphs
(2628 max-degsum + 8890 all-ear records). Role 5's audit independently
verified the Stage-1 numbers and ran an expanded Stage-2 stress test
(30 random seeds at $n = 500$, 5 at $n = 1000$, BT$(k, 2)$ for
$k \in \{200, 300, 500\}$).

#### Candidate ansatz (not yet a conjecture)

$$\boxed{\;I(v) := W^-(v) + \frac{(M_1^-(v))^2}{M_2^-(v)}\;}$$

(with the convention $I(v) := W^-(v)$ when $M_2^-(v) = 0$; not exercised
on the corpus).

**Stage-1 corpus statistics:**
- $\min_{v^*} I = 0.6384$ (at an `enum_n10` graph, vertex 6).
- $\max_{\text{bad } v} I = 0.1861$ (at BT$(50, 2)$ tail).
- Condition-(a) Stage-1 gap $= 0.4523$.

**Implication margin** (the statistic that matters for proof use):
- $\min\{\delta^-(v) - 17/16 : I(v) \ge T\} = 0.082$ on the corpus, at a
  random 2-tree non-max-degsum ear with $I \approx 0.4546$ and
  $\delta^- \approx 1.1446$.
- The margin **does not loosen** as $n$ grows; Role 5's $n = 500, 1000$
  extension finds the same $\approx 0.082$.

#### What's empirically falsified, archived

The Phase-7 search falsified 19 candidates, archived in
`tests/fixtures/joint_invariant_falsified.json`. Examples: $W^0$ alone,
$c_1^2 / \mu_{\max}$, $1/\mu_{\max}^2$, $W^+ / \mu_{\max}^2$. All
defeated by the BT$(k, 2)$ tail family.

#### What's empirically unfalsified (but not yet conjectures)

Multiple candidates survive the corpus, at empirically-fitted thresholds:

| Candidate $I$ | $T$ | $\min_{v^*} I$ | $\max_{\text{bad}} I$ | Implication slack |
|---|---:|---:|---:|---:|
| $W^- + (M_1^-)^2 / M_2^-$ | 0.4122 | 0.6384 | 0.1861 | **0.082** |
| $W^-$ alone | 0.2366 | 0.3332 | 0.1400 | (lower bound TBD) |
| $|M_1^-|$ alone | 0.4089 | 0.5233 | (TBD) | (TBD) |
| $W^- + c_1^2/\mu_{\max}^2$ | 0.2575 | TBD | TBD | TBD |
| $|M_1^-| + c_1^2/\mu_{\max}^2$ | 0.4257 | TBD | TBD | TBD |

The Cauchy–Schwarz form survives because $W^-$ alone is robust at the
natural endpoints and $(M_1^-)^2 / M_2^-$ adds discriminating power at the
boundary cases (where $W^-$ alone is closest to the bad-ear threshold).

### Candidate ansatz, restated for v11

> **Candidate ansatz (v11).** For every 2-tree $G$ on $n \ge 4$
> vertices with max-degsum simplicial ear $v^*$ and $H = G - v^*$:
> (a) $I(v^*) = W^-(v^*) + (M_1^-(v^*))^2 / M_2^-(v^*) \ge T$, and
> (b) $I(v) \ge T \;\Rightarrow\; \delta^-(v) \ge 17/16$,
> for some threshold $T$ to be analytically derived. Empirical:
> $T = 0.4122$ holds with Stage-1 condition-(a) gap $0.4523$
> and implication-margin $\approx 0.082$ on the
> Phase-7 + Role-5-extended corpus. **v11-recommended working threshold:
> $T = 0.25$ (closer to $\max_{\text{bad}} I = 0.186$), which expands the
> bad-ear test set for sharper analytical attack.**

The proof obligations:
- (a) is structural: show that max-degsum implies $I \ge T$ via clique-tree
  data and the moment identities $M_2 = \sigma + 2 |T_{ab}|$ and
  Cauchy–Schwarz $W^- \ge (M_1^-)^2 / M_2^-$.
- (b) is spectral: show via the secular equation that $I(v) \ge T$ forces
  the new eigenvalue $\alpha(v)$ to satisfy $\alpha^2 + W^- \ge 17/16$ (so
  $\delta^-(v) \ge 17/16$).

Both are **open**.

### Refined selector conjecture (carried from v8)

> **Max-degsum selector.** For every 2-tree $G$ on $n \ge 4$, the
> simplicial degree-2 ear $v^*$ maximizing
> $\deg_{G - v^*}(a) + \deg_{G - v^*}(b)$ satisfies
> $\min(\delta^+(v^*), \delta^-(v^*)) \ge 17/16$.

Unchanged and still the headline target. Empirical: 725 / 725 at
$n \le 10$ (min 1.2940); BT$(50, 2)$, BT$(100, 2)$; Role 5 extended to
$n = 500, 1000$ and BT$(k, 2)$ for $k \le 500$, still zero violations.

The v11 attack route: **prove the candidate ansatz** $\Rightarrow$ L'
$\Rightarrow$ max-degsum selector $\Rightarrow$ Conj 9.2 on 2-trees.

## Revised step-by-step plan (v11)

| # | Goal | Technique | Effort | Status |
|---|------|-----------|--------|--------|
| 1 | Easy directions | Bipartite-symmetry; explicit $K_n$ spectrum | inline | **proved** |
| 2 | Corollary A (claw-free, $\Delta \ge 3$) | Thm 1.1 + paths/cycles | paragraph | drafted |
| 3 | Corollary B ($\mathrm{diam} \le 2$) | Thm 1.2 + check $K_{1,n-1}, C_5$ | paragraph | drafted |
| 4 | Short note on steps 1–3 | Exposition | 1–2 weeks | drafts merged; needs polish |
| 5a | (L') on books $B_k$ for $k \ge 2$ | Closed-form spectrum | done | **proved** |
| 5b | (L') on 2-paths $L_n$ asymptotic | Szegő for pentadiagonal sym Toeplitz | done | **proved** |
| 5c | (L') on 2-paths $L_n$ at finite $n$ | Demmel–Kahan a-posteriori + mpmath confirmatory | done for $n \le 2000$ | **rigorous for $n \in [4, 2000]$** |
| 5c.tail | (L') on 2-paths $L_n$ for $n > 2000$ | Non-simple-loop BBG analogue (O5c.3) | research | open |
| 5d | BT$(k, 2)$ bad-ear asymptotic | Symmetry quotient + cubic resolvents | done | **proved** |
| 5e | Headline: max-degsum selector for general 2-trees | Candidate ansatz (a) + (b) | open-ended | candidate identified; (a), (b) open |
| 5e.candidate.a | $I(v^*) \ge T$ structurally | Clique-tree + moment identity + Cauchy–Schwarz | research | open |
| 5e.candidate.b | $I(v) \ge T \Rightarrow \delta^-(v) \ge 17/16$ | Secular equation + new-eigenvalue bound | research | open |
| 5e-a | Structural diagnostics route | Clique-tree functional + Schur complement + moments | done as diagnostic | delivers identities, no threshold |
| 5e-b | Interlacing diagnostics route | Cauchy interlacing + secular handoff | done as diagnostic | delivers handoff, no floor |
| 5f | (L') on fans $F_n$ | Hub + path decomp; DK extension | done for $n \le 200$ | **FP-certified $n \le 200$; tail via 5c-tail** |
| 5g | (L') on multi-arm spider 2-trees | Symmetry + interlacing | partial | Case I = books (redundant); Case II conditional on O5e.1 |
| 6 | If 5e succeeds, prove 9.2 for 2-trees | Telescope to $K_3$ | short | gated on 5e |
| 7 | Fallback: residue-control classes | Block-cut tree, perfect elim, SDP/Gluing | open | not started |
| 8 | Near-extremal sanity ($n \le 30$) | Direct spectrum / Cauchy | 1 week | not started |

5a–5d remain proved. **5c remains closed for $n \le 2000$.** 5e is the
headline, now with an **explicit candidate ansatz** but two open analytical
obligations (5e.candidate.a, .b). 5e-a and 5e-b retain their diagnostic
status — they produce the structural and spectral *language* for the proof
of the candidate ansatz but not the proof itself.

## Three attack vectors (unchanged)

V1, V2, V3. Edge-monotonicity removed in v2.

## Failure modes to guard against

- **F1.** Residue-component count $\ell$ is the whole problem.
- **F2.** Tacit reliance on EFGW in subclasses where it is open.
- **F3.** Near-extremal traps in part (ii).
- **F4.** Regularity not preserved by induced vertex deletion.
- **F5.** "Floating-point certified" $\ne$ interval-arithmetic certified.
- **F6.** BBG-type asymptotic constants assume simple-loop symbol; ours
  fails.
- **F7 (softened in v11).** Single-scalar selector thresholds at the
  **naturally-scaled** values $17/16$ ($\|w\|^2 = 4$ era) or $17/32$
  ($\|w\|^2 = 2$ era) are categorically wrong. **But** a smaller
  empirically-fitted threshold may survive on a finite corpus — at
  least until structured adversarial families ($\mathrm{BT}(k, t)$ with
  $k \to \infty$, $t \ge 2$) close the window. The candidate ansatz
  $I = W^- + (M_1^-)^2 / M_2^-$ at $T = 0.4122$ is robust on the current
  corpus; $W^-$ alone at $T = 0.2366$ is robust only because the corpus
  stops at $n \le 1000$. v11 mandates the regression suite extend to
  $n \in \{500, 1000, 2000\}$ to stress-test single-scalar candidates,
  with the expectation that they will eventually fail while the joint
  $I$ survives.
- **F8.** mpmath @ high-precision $\ne$ interval arithmetic.
- **F9.** Case B (new eigenvalue) carries $\delta^-$ without $W^-$
  support. Any selector lemma must include a Case B branch.
- **F10 (new in v11). The Stage-1 "gap" between $\min_{v^*} I$ and
  $\max_{\text{bad}} I$ is a condition-(a) statistic, not an
  implication-margin statistic.** The metric that matters for analytical
  proof of (b) is $\min\{\delta^-(v) - 17/16 : I(v) \ge T\}$ on the
  all-ears corpus. v10's headline "gap 0.4523" is misleading; the real
  margin on the implication direction is $\approx 0.082$ and shows no
  sign of stabilising as $n$ grows. v11 reframes statistics accordingly.

## Concrete next action (v11)

The candidate ansatz is on the table. The work pivots from "search for a
candidate" to "prove (a) and (b) for the specific candidate".

1. **Prove condition (a) structurally.** Show
   $$W^-(v^*) + \frac{(M_1^-(v^*))^2}{M_2^-(v^*)} \ge T$$
   at the max-degsum ear $v^*$ via clique-tree data and the moment identity
   $M_2(v) = \sigma(v) + 2 |T_{ab}(H)|$ from
   `lprime_5e_a_structural.md`. The tighter v11 target is $T = 0.25$;
   the looser fallback is $T = 0.4122$. Sub-targets:
   - Establish $M_2(v^*) \ge $ explicit constant from $\sigma(v^*) \ge 5$.
   - Establish $M_2^-(v^*) \ge $ explicit fraction of $M_2(v^*)$.
   - Combine via Cauchy–Schwarz to bound $W^-(v^*) + (M_1^-)^2/M_2^-$.
2. **Prove condition (b) via secular equation.** Show that if
   $W^-(v) + (M_1^-(v))^2 / M_2^-(v) \ge T$, then the secular equation
   $\lambda = \sum c_i^2 / (\lambda - \mu_i)$ has its smallest root
   $\alpha(v)$ satisfying $\alpha(v)^2 \ge 17/16 - W^-(v)$. This is
   secular-equation analysis at high precision; the entries $c_i^2$ sum
   to $\|w\|^2 = 2$ and the moments $M_k^-$ control the negative-side
   spectrum of $A(H)$.
3. **Strengthen the corpus per v11 mandate.** Extend
   `data/joint_invariant_scan.json` with:
   - 50 random 2-tree seeds at $n \in \{500, 1000, 2000\}$.
   - BT$(k, 2)$ for $k \in \{200, 500, 1000\}$.
   - BT$(k, 3)$, BT$(k, 4)$, BT$(k, 5)$ for $k \in \{5, 10, 25, 50\}$.
   - Caterpillar 2-trees and stacked-book 2-trees as new adversarial
     families.
   Re-run the ansatz search with the strengthened corpus; if the candidate
   $I, T$ still survives, the empirical case strengthens.
4. **Tighten threshold to $T = 0.25$.** Currently the test
   `test_joint_invariant_candidates.py` uses the Stage-1 midpoint
   $T = 0.4122$. v11 recommends a second test at the tighter $T = 0.25$
   to expand the bad-ear set against which (b) is tested.
5. **Reconcile F7 with the agent's single-scalar finding.** Either:
   (a) Add a regression test that demonstrates $W^-$ alone at $T = 0.2366$
       is falsified at some $n > 1000$ (likely a random 2-tree where the
       max-degsum ear's $W^-$ dips below the BT-tail $W^-$); or
   (b) Accept that single-scalar candidates may survive at low thresholds
       and that the strength of the joint invariant is robustness, not
       categorical non-existence of single-scalars.
6. **Polish steps 2–3 corollaries** (carried).

## Critical reading (carried from v10)

arXiv:2506.07264 (source), arXiv:1409.2079 (EFGW), arXiv:2303.11930 (Abiad
et al., $\le 2$ positive eigenvalues), arXiv:2311.11530 (Elphick–Linz),
arXiv:2410.09830 (Tang–Liu–Wang), arXiv:2409.15504 (Zhang, $n/2$ lower
bound), arXiv:2409.18220 (Akbari–Kumar–Mohar–Pragada, $3n/4$ lower bound),
Bogoya–Böttcher–Grudsky 2018 (simple-loop BBG, with the caveat that the
hypothesis fails for our symbol — O5c.3), Demmel *Applied Numerical Linear
Algebra* (Thm 5.5 a-posteriori), Wilkinson *The Algebraic Eigenvalue Problem*,
Avram–Parter 1988.

## Open subobligations (v11)

- (**O5e.1**) Book-arm monotonicity for multi-arm spiders.
- (**O5e.2**) Fan rigorous closure at $n > 200$ (folds into 5c.tail).
- (**O5e.3**) Joint-invariant ansatz — Phase 7 delivered a non-falsified
  candidate; **conditions (a) and (b) still open** as
  5e.candidate.a / 5e.candidate.b.
- (**O5c.1**) Interval-arithmetic for $n \le 200$ — resolved by Demmel–Kahan
  in v10.
- (**O5c.3**) Non-simple-loop BBG analogue for $n > 2000$.
- (**O11.1, new in v11**) Establish the explicit value of $T$ in the
  candidate ansatz from the structural proof of (a), not from empirical
  Stage-1 midpoint. The Phase-7 value $T = 0.4122$ has no analytical
  derivation; the v11 working value $T = 0.25$ is recommended for
  tightening the implication test but also needs analytical grounding.

## Open subtasks (status updated in v11)

- `scripts/spectrum_check.py` — **implemented**.
- `scripts/mpmath_certify.py` — **implemented** (5c).
- `scripts/two_tree_enum.py` — **implemented**.
- `scripts/joint_invariant_features.py` — **implemented (v10)**.
- `scripts/build_joint_invariant_corpus.py` — **implemented (v10)**.
- `scripts/joint_invariant_ansatz_search.py` — **implemented (v10)**.
- `tests/two_tree_ear_gain.py` — **implemented**.
- `tests/test_lprime_subfamilies.py` — **implemented**.
- `tests/test_max_degsum_selector.py` — **implemented**.
- `tests/test_two_path_finite_n.py` — **implemented**.
- `tests/test_two_path_widom_tightness.py` — **implemented**.
- `tests/test_mpmath_certify.py` — **implemented**.
- `tests/test_w_norm_squared_invariant.py` — **implemented**.
- `tests/test_joint_invariant_candidates.py` — **implemented (v10)**;
  11 tests passing.
- `tests/fixtures/joint_invariant_falsified.json` — **populated (v10)**
  with 19 falsified candidates.
- `tests/p3_removal_witness.py` — fallback, **not started**.
- `tests/near_extremal_sanity.py` — fallback, **not started**.
- **(v11 NEW)** `scripts/build_joint_invariant_corpus_extended.py` —
  build the v11-mandated extension (random 2-trees at
  $n \in \{500, 1000, 2000\}$ with 50 seeds each; BT$(k, t)$ for
  $k \in \{200, 500, 1000\}$ and $t \in \{2, 3, 4, 5\}$; caterpillar +
  stacked-book families).
- **(v11 NEW)** `tests/test_joint_invariant_candidates_v11.py` —
  retest the candidate at the tighter $T = 0.25$ and on the extended
  corpus.
- **(v11 NEW)** `data/joint_invariant_implication_margin.json` —
  record the implication-margin statistic $\min\{\delta^- - 17/16 :
  I(v) \ge T\}$ as a function of $n$ and threshold $T$, to track whether
  the margin stabilises or shrinks.

The Phase-3 universal-lemma regression
(`tests/fixtures/two_tree_universal_counterexamples.json`) and v9
$\|w\|^2 = 2$ regression
(`tests/fixtures/w_norm_squared_is_2.json`) are kept permanently.
