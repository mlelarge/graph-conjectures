# Correctness review — positive_square_energy_equality, 2026‑05‑18

Reviewer: independent audit pass.
Scope: full `problems/positive_square_energy_equality/` tree, paper draft
(`paper/main.tex` + sections + appendices), the `docs/plan_v14.md` plan,
the load-bearing `scripts/` (`half_line_stieltjes.py`,
`mpmath_certify.py`, `two_path_limit_moments.py`,
`positive_side_ceiling.py`), and the 539-test test suite.
Target conjecture: Akbari–Kumar–Mohar–Pragada–Zhang Conjecture 9.2
(arXiv:2506.07264, June 2025), restricted to the 2-tree slice.

## Executive verdict

The project's headline claim — *Conjecture 9.2 for 2-trees* — is **NOT
proved**. The paper draft is internally honest about this, and the
plan v14 also flags the workstream as having pivoted from
research-attack to paper-writing mode. What is in scope here is a more
limited evaluation: do the *named* results in the contribution stack
actually hold, are the proofs in the LaTeX sources mathematically
sound, and do the negative results (failure-modes catalogue) survive
red-team scrutiny? The verdict is:

1. **Books closed form `δ⁻(B_k) = 2 − 4/(√(8k+1) + √(8k−7))` — CORRECT**
   for `k ≥ 2`. The eigenvalue derivation in
   `paper/sections/04_subfamily_theorems.tex:47–128` is clean, the
   formula matches a from-scratch numerical recomputation to
   floating-point precision at `k = 2, 3, 4, 5`, and the algebraic
   reduction `√(8k+1) − √(8k−7) = 8/(√(8k+1)+√(8k−7))` is correct.
   `B_1 = K_3` is correctly excluded (`δ⁻(K_3) = 1 < 17/16`; the
   formula evaluates to `1` at `k = 1` but the page-deletion identity
   `B_1 − v = K_2` then makes the recursion change shape).

2. **2-paths Szegő Cesàro `c⁻ = (32π − 27√3)/(12π) ≈ 1.4262` — CORRECT
   as a Cesàro statement** (per-vertex average `s⁻(L_n)/n → c⁻`).
   The trig integration in
   `paper/sections/04_subfamily_theorems.tex:208–235` is reproducible
   exactly, and numerical Cesàro convergence is confirmed.
   **MAJOR caveat:** the paper carefully *separates* the Cesàro
   `s⁻(L_n)/n → c⁻` (proved) from the first-difference statement
   `δ⁻(L_n) → c⁻` (not proved at the asymptotic level — only
   empirical on `n ≤ 200` and finite-n via DK on `n ≤ 1000`). This
   separation is mathematically necessary (a sequence `a_n/n → c`
   does not generally imply `a_n − a_{n−1} → c`) and is honestly
   flagged in the abstract and `Remark 4.4`.

3. **Stieltjes / `I_∞(L)` identification — CORRECT.**
   The closed form `I_∞(L) = 2(310π² − 837√3 π + 2187)/(27π(20π − 27√3))`
   matches independent sympy recomputation **to 140+ digits** (zero
   symbolic difference between the two stated forms). The derivation
   in `paper/sections/04_subfamily_theorems.tex:637–841` (Stieltjes
   transform), `sections/05_moment_form_ansatz.tex:633–706`
   (closed-form assembly), and `scripts/half_line_stieltjes.py` is
   coherent.

4. **`δ⁻(L_n) ≥ 17/16` finite-n rigorous bound — engineering-rigorous,
   NOT interval-rigorous, and *up to `n = 1000`* (not `n ≤ 2000`
   as the README/plan claim — see CRITICAL discrepancy below).**

5. **BT(k,2) bad-tail-ear asymptotic `4 − α² + β² ≈ 1.0353` — CORRECT
   as a computational/asymptotic statement** and reproducible from
   the cubics `P_G = 2x³ − 7x − 3`, `P_H = 2x³ + 2x² − 3x − 2`. The
   `\thm:BT-asymptotic` is honestly stated as conditional on the
   secular-rate subobligation `a_± − b_± = O(1/√k)`, which is *not*
   fully written out. This is a known stub.

6. **Lemma B1 (Rayleigh lower bound on `λ_min²`) and Lemma B1+ (lower
   bound on `λ_max²`) — CORRECT.** The algebraic identity
   `(1 − u)² + 4u = (1 + u)²` underpinning the `Lem:bminor-amin`
   step holds symbolically (sympy verified). The F7 sign-error
   carry-forward is honestly catalogued.

7. **Headline open piece — the existential ear-selection lemma `(L')`
   — IS open** and is correctly framed as
   `Conjecture (thm:Lprime)` in `paper/sections/03_lprime_reformulation.tex:78–85`,
   not as a theorem. Proposition 3.5
   (`prop:Lprime-implies-92`, the telescope to `K_3`) is clean and
   correct.

8. **`(b.minor)` / `lem:bminor-amin` — provably establishes
   `α_min² ≥ 1` only**, NOT `δ⁻(maxdeg) ≥ 1`. The paper says this
   explicitly in `Remark 5.10 (rem:bminor-F11)` and
   `Remark 5.11 (rem:bminor-gap)`. The "F11 caveat" — that
   `α_min` and `α_top` are different quantities — is real, and the
   paper does not paper over the gap.

9. **Failure modes F1–F10 (F14–F15 in plan terminology) are real
   negative results**, supported by either regression fixtures, an
   explicit counterexample graph6 string, or a clean structural
   reason. F4 (naive sine-basis density) and F6 (α·ω fallback) are
   particularly informative.

10. **Citations Akbari–Kumar–Mohar–Pragada–Zhang (arXiv:2506.07264)
    and Elphick–Farber–Goldberg–Wocjan (arXiv:1409.2079) verified
    against arXiv abstracts**: both papers exist with the stated
    titles and topics. The EFGW reference is correctly characterised
    as a *conjectured* bound (still open in general).

11. **Stubs in `paper/`**: I find **no `\stub{}` or `\todo{}` calls
    remaining in any of the seven section files or the two appendix
    files**. The `\stub` macro is defined in `paper/preamble.tex`
    and the paper README documents its use during drafting, but
    every section file is rendered fully without orange [TODO]
    boxes. This is a paper that has reached "draft complete" stage.

The bottom line: this is **honest, careful research output**. The
hardest claim (the full `(L')` lemma, and through it 9.2 for 2-trees)
is *not* claimed; everything that is claimed is, modulo two
identified caveats, supportable. The single non-trivial
discrepancy is the **`n = 1000` vs `n = 2000` range** of the
Demmel–Kahan certificate (see CRITICAL below).

---

## Findings by file / section

### CRITICAL

**[CRITICAL] Range discrepancy: DK certificate is `n ∈ [4, 1000]`,
not `n ∈ [4, 2000]` as the plan/review brief states.**
- `paper/sections/01_intro.tex:99–102` claims `n ≤ 1000`.
- `paper/sections/04_subfamily_theorems.tex:506, 512, 525` all say
  `n ∈ [4, 1000]`.
- `paper/abstract.tex:13` says `n ≤ 1000`.
- `tests/test_mpmath_certify.py:124–134` tests up to `n = 1000`.
- `scripts/mpmath_certify.py:328` argparse default `--n-max-dk = 1000`.
- However, `docs/plan_v14.md:236` table line says
  `δ⁻(L_n) ≥ 17/16, n ≤ 2000 ... done | rigorous`, and
  the user's review brief asserts `n ∈ [4, 2000]`.
- `docs/plan_v10.md` says "5c closed for n ≤ 2000 via DK".

The paper is **internally consistent** at `n = 1000`. The plan v14
table line is **stale documentation** carried over from earlier
plan versions. The actual certified range is `n ∈ [4, 1000]`.
Recommended: update the plan v14 step-table to match the paper.

**[CRITICAL] Demmel–Kahan envelope constant: paper uses `c ≤ 10⁴`,
script uses `c = 10`. The paper bound is provably safe but lets
3 orders of magnitude of safety margin sit unused; the script bound
is closer to what's published in the LAPACK literature but is
*tighter* than the paper claims.**
- `paper/sections/04_subfamily_theorems.tex:551–558`: "we adopt the
  conservative working envelope `c ≤ 10⁴` (which is overshooting any
  published constant by at least one order of magnitude)".
- `scripts/mpmath_certify.py:69`: `DK_CONST = 10.0`.
- `scripts/mpmath_certify.py:172`: "We use `c = DK_CONST = 10` as
  a safe upper bound".
- This is not a logical inconsistency — `10 < 10⁴`, so any certificate
  valid under `c ≤ 10⁴` is *a fortiori* valid for the actual
  computational pipeline under `c = 10`. But the *paper-stated*
  envelope is much weaker than the *script-implemented* envelope.
  This is fine as a hedge; readers should know that the script
  gives `~10⁻¹²` per-eigenvalue error at `n = 200` while the paper
  bounds it by `8.88 · 10⁻⁹`, both far below the slack.
- The honest status of the constant — that no fully formal LAPACK
  `dsyevd` derivation is given — is documented in
  `Remark 4.6 (rem:fp-vs-interval)` and Appendix A. This is
  appropriate for an *engineering*-rigorous, not interval-rigorous,
  certificate.

### MAJOR

**[MAJOR] `δ⁻(L_n) ≥ 21/16` finite-range bound is the
"engineering-rigorous" floor, NOT the asymptotic bound.**
The abstract claims (line 13) `δ⁻(L_n) ≥ 21/16` for `n ≤ 1000` and
that the corresponding *asymptotic* statement
`δ⁻(L_n) → c_1⁻` (which is what would close `(L')` on 2-paths in
the limit) is an open subobligation O13.1. The empirical worst
case is `δ⁻(L_6) ≈ 1.319007`, which sits **`0.0065` above 21/16 =
1.3125**, so the certified slack-to-21/16 is `~0.0065`, NOT `0.257`
as one might read into the prose. The slack `0.257` is to `17/16`,
not to `21/16`. The paper occasionally says "slack `0.257` to
`17/16`" precisely, but the framing "`≥ 17/16 + 1/4`" is potentially
misleading: the certificate is `δ⁻(L_n) ≥ 17/16 + 1/4`, and at
`n = 6` the certificate is exactly `1.319007 ± 10⁻⁴ ≥ 1.3125` —
slack of only `0.0065`, not `0.25`. The factor `1/4` is the
*declared* slack target, not the *empirical* slack. This is
clarified at `paper/sections/04_subfamily_theorems.tex:586–593`,
but a careless reader could read "+1/4" as a safety margin baked
into the analysis. **Recommendation: rephrase**.

**[MAJOR] Reduction map (L' implies 9.2 on 2-trees) — the proof in
`Proposition 3.5 (prop:Lprime-implies-92)` correctly terminates the
induction at `K_3`, not `K_2`.** This is correct: if one induced
down to `K_2` one would need `δ⁻ = 2 − 1 = 1 < 17/16`. The note
at lines 144–148 explicitly addresses this and accumulates the
right base value `s⁻(K_3) = 2`, `s⁺(K_3) = 4`. The arithmetic
`2 + (17/16)(n − 3) = n − 1 + (n − 3)/16 > n − 1` for `n ≥ 4` is
correct. Note this also covers part (i) (`s⁺(G) = n − 1`) and
part (ii) (`s⁻(G) = n − 1`) of Conjecture 9.2 simultaneously on
the 2-tree class: 2-trees with `n ≥ 4` are not trees (they have
`n − 2` triangles), so equality cannot occur; and `K_n` for
`n ≥ 4` is not a 2-tree (has treewidth `n − 1 ≥ 3`).

**[MAJOR] Condition (b) is open for *every* subfamily, including
those where condition (a) is proved.** This is well-flagged in
`paper/sections/05_moment_form_ansatz.tex:280` and in plan v14
under "Condition (b)". The chain
`(a) ∧ (b) ⇒ (L') at v* ⇒ Conj 9.2 on 2-trees` cannot be invoked
to close the headline on books or 2-paths *because the (b)
direction is never closed*. The books and 2-paths are closed by
*direct* computation (`δ⁻(B_k)` closed form; `δ⁻(L_n) ≥ 17/16`
DK certificate), not via `(a) ∧ (b)`. This makes the moment-form
ansatz infrastructure feel like scaffolding for an unproved
program; the paper acknowledges this in
`Remark 5.13 (rem:bminor-gap)` and `Problem A
(prob:slot-shift)`. This is honest, not bullshit. But it does
mean the contribution stack is partially load-bearing on
material that does not advance the headline.

**[MAJOR] `lem:cs-two-sided` (the two-sided Cauchy–Schwarz
structural bound) gives `I(v) ≥ 0.396`, falling 0.016 short of
`T = 0.4122` on the corpus minimum.** This is admitted in the
paper at `sections/05_moment_form_ansatz.tex:420–432` (Remark
"Structural-sufficiency gap"). It means *the named structural
lower bound does not by itself close condition (a) on general
2-trees*; the paper relies on empirical
`min I(v*) = 0.6384` instead. The gap is "small" empirically but
analytically significant (an analytical proof of (a) on general
2-trees is open subproblem `prob:general-a`, characterised as
needing a *fifth* clique-tree quantity).

### MINOR

**[MINOR] Plan v14 says "test suite 519/519 passing" but the
test suite has 539 tests** (`pytest --collect-only` returns
`539 tests collected`; full run yields `539 passed`). The plan
likely under-counts by 20 or pulls a number from an older
revision. The paper Appendix A says `539 tests` (correct).

**[MINOR] Stub macro infrastructure in `paper/preamble.tex` is
preserved but unused.** Grepping the section/appendix files for
`\stub` or `\todo` returns *zero* matches in any of the seven
section files; the appendices have two `% TODO`-style comments in
the LaTeX (one in `A_reproducibility.tex` mentions "TBD" for repo
URL and git hash). The paper is past the stub-filled drafting
phase. The `Makefile` `final` target that swallows `\stub`
arguments is therefore moot for the present state of the draft.
This is good — but the README's table at
`paper/README.md:70–76` ("§1 Intro skeleton, `\stub` markers")
is stale; it describes an earlier revision.

**[MINOR] Reference bib stubs.**
- `references.bib` has three entries with `note = {Bibliographic
details to be completed.}` (AbiadEtAl2023, TLW2024, AKMP2024) and
`AvramParter1988` is missing volume/page.
- The author list of the paper itself is `\author{TBD}` and the
GitHub URL is `<TBD>`. These are pre-submission gaps.

**[MINOR] `(rem:Pjkl)` in `02_notation_corollaries.tex:76–82`
asserts that Corollary A delegates the heavy lifting on claw-free
`Δ ≥ 3` to Theorem 1.1 of AKMPZ2025.** I have not verified that
Theorem 1.1 has the exact form claimed (`s⁺ ≥ n` strict for
connected claw-free `Δ ≥ 3`). This is one citation hop deeper
than I am willing to make without inspecting AKMPZ2025 directly.
The plan reference to "Theorem 1.1 + 1.2" is consistent across
the project, but the user's `claudeMd` flags exactly this kind of
"citation from an agent" as worth independent verification —
flagging.

**[MINOR] Corollary B's `diam = 1` sub-case`** (`G = K_n` →
`s⁺ = (n−1)²`) is handled in the docs `corollaries_AB.md` lines
58–64 *with the case `n = 2`*, and the paper version in
`02_notation_corollaries.tex:94–98` says "the hypothesis
`s⁺(G) = n − 1` then forces `n = 2`, and `G = K_2` is a tree".
This is correct: `(n − 1)² = n − 1 ⇒ n − 1 ∈ {0, 1}`. (Recall
the conjecture assumes `G` connected of order `n`, with `n ≥ 1`
implicit; for `n = 1`, `K_1` is trivially a tree.) Both the paper
and the docs handle this consistently.

**[MINOR] `paper/abstract.tex:9` says `≈ 1.4262 for the *average*
square energy per vertex`, while line 13 then states the
finite-n DK floor as `δ⁻(L_n) ≥ 21/16` for `n ≤ 1000`.** Two
different quantities (Cesàro average vs first-difference). The
paper is precise about this *within* the body
(`Theorem 4.2 (thm:2path-szego)` vs
`Theorem 4.5 (thm:2path-DK)`), and `Remark 4.4
(rem:2path-first-difference)` is the bridge. A non-careful reader
of the abstract could conflate the two.

### NIT

**[NIT] `paper/abstract.tex:18`** writes `\BTkt{k}{2}` but never
introduces the family before the abstract. (The body section
04 introduces it.) Not a problem since `\BTkt{k}{2}` is purely
notational at this point and the reader can infer the structure
from the prose.

**[NIT] Numerical values stated to many digits in the prose.**
E.g. `δ⁻_∞(BT) ≈ 1.0353` is correct (my recomputation gives
`1.03527975...`); `min δ⁻(v*) ≥ 1.29405` is correct to displayed
precision. `inf I(v*) = 0.6384` and `I_∞(L) ≈ 1.0157` were checked
to within `~0.0001`.

---

## Stubs in `paper/paper.pdf` — exhaustive list

I performed two passes: (1) `grep -rn '\\stub\|\\todo' paper/`,
which returned **zero matches in any of the section files**; (2)
search for `% TODO`, `TBD`, `placeholder`, `stub` in the same
files. Summary:

- `paper/preamble.tex` defines `\stub{}` and `\todo{}` and forwards
  one to the other (lines 26–35). These are macros, not invocations.
- `paper/main.tex:9` — `\author{TBD}` and
  `paper/main.tex:10` — author-list TODO comment.
- `paper/main.tex:15` — `<TBD>` GitHub URL,
  `paper/main.tex:16` — `git commit hash: TBD`.
- `paper/appendices/A_reproducibility.tex:6` — same `<TBD>` repo
  and commit-hash placeholder.
- `paper/abstract.tex` — no stubs.
- `paper/sections/01_intro.tex` — no stubs.
- `paper/sections/02_notation_corollaries.tex` — no stubs.
- `paper/sections/03_lprime_reformulation.tex` — no stubs.
- `paper/sections/04_subfamily_theorems.tex` — no stubs. **But:**
  Proposition `thm:BT-asymptotic` is stated *conditional on the
  secular-rate subobligation*; the proof body explicitly says at
  lines 473–488 that the leading-eigenvalue square-difference
  cancellation `a_± − b_± = O(1/√k)` is "sketched at the level of
  the secular equation but not fully closed". This is a load-bearing
  conditional, not a typographical stub.
- `paper/sections/05_moment_form_ansatz.tex` — no stubs. Lemma B1
  proof is full; `lem:cs-two-sided` proof is full;
  `lem:bminor-amin` proof is full; `thm:moment-form-stieltjes`
  proof refers to `tests/test_half_line_stieltjes.py` for symbolic
  verification of the closed-form moments. The reference is OK,
  but the proof body is not fully self-contained: the symbolic
  closed forms for `W⁻_∞`, `M¹⁻_∞`, `M²⁻_∞` are stated rather
  than derived in the paper, with the script left as the
  derivation artefact.
- `paper/sections/06_failure_modes.tex` — no stubs.
- `paper/sections/07_open_problems.tex` — no stubs.
- `paper/appendices/A_reproducibility.tex` — only the `<TBD>` URL.
- `paper/appendices/B_fixtures.tex` — no stubs.

**Verdict on stubs:**
- *Typographical*: only the four `TBD` placeholders for author
list, git hash, and GitHub URL. Cosmetic.
- *Structural conditional* (load-bearing but flagged):
  - The BT(k,2) asymptotic conditional on the `O(1/√k)` secular
    rate (`thm:BT-asymptotic`).
  - The DK certificate conditional on the `dsyevd` backward-error
    envelope `c ≤ 10⁴` (`thm:2path-DK`).
  - The `δ⁻(L_n) → c_1⁻` asymptotic first-difference (recorded as
    open subobligation O13.1, not claimed as a theorem).
  - The `(L')` ear-selection lemma itself — stated as a
    *conjecture*, which is honest.

All four "structural conditionals" are explicitly flagged in
their theorem/proposition statements as conditional. The paper
**does not** claim things as proved while quietly relying on
unwritten lemmas.

---

## The 17/16 (and 21/16) bound — does Demmel–Kahan cover [4, 2000]?

**Short answer.** The current artefact covers `n ∈ [4, 1000]`,
not `n ∈ [4, 2000]`. The plan v14 step-table line "5c closed for
n ≤ 2000" is **stale documentation**; the actual covered range
in the paper, the scripts, and the tests is `[4, 1000]`.

**Long answer.** The DK certification scheme has the following
structure:
1. Numerical computation of `s⁻(L_n)` via
   `numpy.linalg.eigvalsh` for each `n ∈ [4, 1000]`
   (`scripts/mpmath_certify.py:fp_spectrum_with_dk_bound`).
2. A-posteriori forward-error bound
   `|tilde λ_i − λ_i| ≤ c · n · ε · ‖A(L_n)‖₂`
   with `c ≤ 10⁴` (paper) or `c = 10` (script), both safe under
   any published constant for backward-stable symmetric
   eigensolvers (Demmel's "Applied Numerical Linear Algebra"
   Theorem 5.5, LAPACK Users' Guide §4.7).
3. Propagation to `s⁻` via `|δ(λ²)| ≤ 2|λ|·|δλ|`, summing over
   ≤ `n` negative eigenvalues, giving
   `|tilde s⁻ − s⁻| ≤ 2 · c · n² · ε · ‖A‖²`.
4. Triangle inequality for `δ⁻(L_n) = s⁻(L_n) − s⁻(L_{n−1})`.
5. Worst-case slack: `δ⁻(L_6) ≈ 1.319007`, error bound
   `≤ 1.42 · 10⁻⁴` at `n = 1000`, slack to `17/16` is
   `~0.257`, dominating the error by 3 orders of magnitude.

I personally verified:
- The DK propagation arithmetic in
  `scripts/mpmath_certify.py:155–192` is correct (Frobenius vs
  spectral norm careful, sign-flip term included).
- The slack at `n = 6` is genuine: `1.319007 − 17/16 = 0.2565`,
  reproducible in double precision and confirmed via mpmath at 50
  digits (the JSON `data/two_path_mpmath_certificate.json:31–37`
  records `slack_rigorous_lower = 0.2565074608851736`).
- The base case `n = 4` *is* checked, with
  `δ⁻(L_4) ≈ 1.4384` (= `δ⁻(B_2) = (7 − √17)/2`, since `L_4 = B_2`).
- The full DK test runs in `~38 seconds` and passes for
  `n ∈ [4, 1000]` (`tests/test_mpmath_certify.py:test_dk_certify_n4_to_n1000`).
- The full test suite of `539` tests passes (`pytest -q` returns
  `539 passed in 141.44s`).

**What is NOT covered by DK:**
- `n > 1000` (scripts default cap, *not* `n > 2000`).
- A formal derivation of an explicit envelope constant for the
  exact LAPACK `dsyevd` pipeline. The paper is honest that
  this is conditional on a "conservative working envelope".

**Is the certificate *interval*-rigorous?** No. The paper itself
flags this in `Remark 4.6 (rem:fp-vs-interval)` as failure mode
F8. An upgrade via `mpmath.iv` or Krawczyk-style verified
eigensolver is described as "mechanical but beyond the scope of
this paper". This is correct: as long as the reader accepts the
working envelope `c ≤ 10⁴`, the certificate is rigorous; the
remaining gap is to make the constant itself formally certified.

**Conclusion on DK:** The certificate is real, the base case is
checked, the slack dominates the error by orders of magnitude
at every `n ∈ [4, 1000]`, and the implementation is correct.
The **claim "n ≤ 2000"** in plan v14 and in the review brief is
**not supported by current artifacts**; the actual range is
`n ≤ 1000`. The (mechanical) extension to `n > 1000` requires
no new mathematics but does require running the script with a
higher cap; this has *not* been done in the present repository
state.

---

## The slot-shift wall — is it really a wall, or under-creativity?

The slot-shift sum bound `(prob:slot-shift)` is, by the project's
own assessment, the analytical bottleneck (estimated "6 person-months
to 2 years"). My assessment:

**It is genuinely a wall, not under-creativity.** Reasons:

1. **The cancellation regime is real.** On the `BT(k=50, 2)`
   tail-ear example, `α_min² ≈ 90` and `μ_{n−1}² ≈ 90`, but their
   difference is `δ⁻ ≈ 1.06` (about 1% of either quantity). Any
   bound that controls `α_min²` alone — like Lemma B1 — cannot
   conclude anything sharp about `δ⁻` because the lower bound on
   `α_min²` and the lower bound on `μ_{n−1}²` would have to
   *match to within 1%*, well beyond what Rayleigh-style bounds
   deliver.

2. **The F11 caveat is structural.** The slot decomposition needs
   `α_top²` (the *least*-magnitude `G`-negative eigenvalue), not
   `α_min²` (the *most*-negative). On `L_30`, `α_top² ≈ 8.6·10⁻⁴`
   while `α_min² ≈ 4.91` — three orders of magnitude separation,
   confirming that the two quantities cannot be substituted for
   each other. The corrected Case-B identity at
   `Remark 5.13 (rem:bminor-gap)` uses `α_top²` in the corrected
   form.

3. **The trace-identity reformulation (F14) provably does not
   decouple the wall.** The argument in
   `plan_v14.md:288–297` is clean: `δ⁻ ≥ 1 ⇔ δ⁺ ≤ 3`, and the
   Rayleigh trial-vector technique gives a *lower* bound on
   `λ_max²`, hence on `δ⁺` — the wrong direction. The mirror
   asymmetry hypothesised by Elphick–Linz is empirically falsified
   on the 2235-record corpus (positive-side and negative-side
   Lemma-B1 tightness ratios within 3% of each other). The
   strategic motivation for trying the positive side is therefore
   dead.

4. **`α·ω` fallback (F15) is structurally inapplicable.**
   Empirically zero connected graphs at `n ≤ 14` satisfy
   `α·ω ≤ n/17`; for 2-trees specifically, `ω = 3` and `α ≥ n/3`
   so `α·ω ≈ n` uniformly. The constant `17` is upstream-bound
   (it traces back to `ε = 1/16` in Zhang 2024's `P_3`-removal
   lemma). Improving 17 is *not* part of this workstream.

5. **The pure quantitative slot-shift sum**
   `Σ_{j ∈ J⁻} (λ_{j+1}² − μ_j²) ≥ const` has no standard tool
   delivering it. Lehmann–Goerisch / Temple / Aronszajn are too
   weak in the cancellation regime; the paper at
   `paper/sections/07_open_problems.tex:50–58` suggests possible
   tools (Cauchy-style integral on the secular function, or a
   strict-slack chordal-graph Sylvester refinement) but no
   concrete attack lands.

**Is there a residual concern that the project is missing a
workaround?** I cannot rule it out from artefacts alone — that
is exactly the kind of conjecture-level gap that requires expert
domain knowledge to assess. But the project has been
*systematically* exploring the natural attack vectors (trace
identity, asymmetry, residue control, max-degsum selector,
common-spine-edge characterisation, etc.) and each one
empirically or structurally fails. The 15 catalogued failure
modes are evidence of a thorough red-team programme. The wall
designation is defensible.

---

## What I cannot verify from artifacts alone

1. **The full statement and proof of Theorems 1.1 and 1.2 of
   AKMPZ2025** (used in Corollaries A and B). I verified that
   the paper exists with the correct topic, but the precise
   form of Theorems 1.1, 1.2, 8.1 is one citation hop away.

2. **The exact value of the LAPACK `dsyevd` envelope constant.**
   The paper uses a hedged `c ≤ 10⁴`; the script uses `c = 10`.
   No formal derivation is given for either.

3. **The full proof of the BT(k,2) `O(1/√k)` secular-rate
   cancellation.** The paper sketches the argument but does
   not formalise it; the numerical verification is robust.

4. **The general-2-trees condition (a) bound at the
   "structural-sufficiency gap" of `~0.016`.** Empirical
   `min I(v*) = 0.6384` clears the threshold by `~0.23`, but
   the four-moment lower bound delivers only `~0.396`. Whether
   the fifth clique-tree quantity (eccentricity / depth) closes
   this is genuinely open.

5. **Whether the *full* Conjecture 9.2 — beyond 2-trees — is
   attackable by the moment-form ansatz framework developed
   here.** The paper says (and I concur) that the analytical
   content "is plausibly orthogonal to the moment-form framework
   developed here" for general chordal or arbitrary graphs.

6. **Whether `K_4` is excluded from the 2-tree class via
   treewidth.** I checked: `K_4` has treewidth `3`, not `2`, so
   it is correctly excluded. The induction stops at `K_3` (the
   unique 2-tree on `3` vertices, treewidth `2`).

---

## What I am confident about

1. **Books closed form `δ⁻(B_k) = 2 − 4/(√(8k+1) + √(8k−7))`** for
   `k ≥ 2`. Algebra checks, numerics check, formula matches
   small-k recomputation to machine precision.

2. **Cesàro Szegő limit `c⁻ = (32π − 27√3)/(12π)`.** Verified by
   direct trig integration; closed form and decimal expansion
   agree.

3. **`I_∞(L) = 2(310π² − 837√3π + 2187)/(27π(20π − 27√3)) ≈ 1.0157`.**
   Verified symbolically against the constituent moments
   `W⁻_∞ = 1 − 3√3/(4π)`, `M¹⁻_∞ = 2/3 − 9√3/(4π)`,
   `M²⁻_∞ = 3 − 81√3/(20π)`. Zero symbolic difference between
   the assembled `M₀ + M₁²/M₂` form and the stated rational form.

4. **BT(k,2) asymptotic value `4 − α² + β² ≈ 1.0353 < 17/16`.**
   Cubics `2x³ − 7x − 3` and `2x³ + 2x² − 3x − 2` have the
   stated positive roots; squared sum computes the stated value;
   the BT family at `k = 50, 100, 200` numerically converges to
   the asymptote. Refutes the *universal* form of `(L')`.

5. **The `||w||² = 2` identity** (`paper/sections/03_lprime_reformulation.tex:16–22`),
   not `= 4`. F2 is a real bug that was corrected.

6. **The Reduction-Map Proposition (`prop:Lprime-implies-92`)**
   terminates correctly at `K_3` with the right base values
   `s⁻(K_3) = 2`, `s⁺(K_3) = 4`, and gives the correct strict
   inequality `s⁻(G) > n − 1` for every 2-tree on `n ≥ 4`
   vertices — *if* `(L')` holds. The implication chain is sound.

7. **F1 (universal `(L')` is false), F4 (boundary density is
   `sin(θ₂ − θ₁)/π`, not the naive `(sin θ + sin 2θ)²/π`),
   F7 (sign error caught at `L_5`), F10 (caterpillar minimiser
   `I}qcHG`GO` at `n = 10` with `I(v*) = 0.6384`, below
   `I_∞(L)`).** All four are real, structural negative results,
   not just data-points.

8. **The test suite covers each named theorem with at least one
   regression-locked test** (`paper/appendices/A_reproducibility.tex:145–161`
   cross-reference table). 539 tests pass.

9. **The `s⁺ = n − 1` (iff tree) / `s⁻ = n − 1` (iff tree or
   `K_n`) "iff" semantics are correctly handled**: the easy
   `(⇐)` direction is established in
   `paper/sections/02_notation_corollaries.tex:37–47` from the
   bipartite-symmetry of tree spectra and the explicit `K_n`
   spectrum `{n − 1, −1, …, −1}`. The substantive `(⇒)`
   direction is what the paper attacks.

10. **The arXiv references exist with the claimed content.**
    arXiv:2506.07264 (Akbari–Kumar–Mohar–Pragada–Zhang) is the
    correct source paper. arXiv:1409.2079 (Elphick–Farber–Goldberg–Wocjan)
    is correctly cited as a conjecture, not a theorem.

---

## Final verdict

**This is a careful, honest, partially-complete research project.**
The named results — book closed form, Cesàro Szegő limit, BT
asymptotic, Stieltjes `I_∞(L)` closed form, Lemma B1 / B1+, DK
finite-n certificate, two-sided CS lower bound, common-spine-edge
characterisation, and the `(L')`-reformulation framework — are
correct or honestly stated as conditional / open. The headline
target (Conjecture 9.2 on 2-trees) is *not* closed; the paper
does not claim otherwise. The 15 catalogued failure modes
(F1–F15) substantially de-risk future work by saving the next
researcher months of dead-end attempts.

**Recommended minor edits before submission:**
1. Reconcile the `n ≤ 1000` (paper, scripts, tests) vs
   `n ≤ 2000` (plan v14 table) discrepancy.
2. Reconcile `c ≤ 10⁴` (paper) vs `c = 10` (script). State the
   tighter, script-implemented constant in the paper.
3. Update `paper/README.md:70–76` (currently describes a
   stub-filled draft; the actual draft has no stubs).
4. Fill in `TBD` placeholders (author list, GitHub URL, git
   commit hash, three `references.bib` `note` fields).
5. Update plan v14 test-count "519" to "539".
6. Clarify the abstract: "engineering-rigorous" vs
   "interval-rigorous", and "Cesàro" vs "first-difference".

**The wall (slot-shift sum bound, condition (b)) is real.** The
project's pivot from research-attack to paper-writing mode is
the right call given the cost/value calculus. The mathematical
content delivered is substantive even without closing the
headline.

---

*Reviewer note.* I have not modified any other files. This review
file is the only artefact produced by this audit pass.
