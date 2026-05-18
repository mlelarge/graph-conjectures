# Fix verification report — 2026-05-18

**Verifier:** independent verification pass following the targeted fixes
the mathematician applied in response to
`CORRECTNESS_REVIEW_2026_05_18.md`.

## Verdict

Both claimed fixes (MAJOR-1 LP-optimality softening; MINOR-A Hurlbert
title) landed in the four files named. The new
`docs/terminal_report.md:159-167` paragraph admits float pricing, admits
degeneracy with the cited cross-reference, and uses the exact phrase
"empirical evidence, not a proof of LP-optimality". The Hurlbert title
is now "A Linear Optimization Technique for Graph Pebbling" in
`scripts/build_hurlbert_T_strategies.py:4-5`,
`docs/phase2b_status.md:272-275`, and (newly, for consistency)
`tests/test_hurlbert_T1_T2_T3_T4_certificate.py:4-5`. Test suite is
green at 103/103 — same count as the original audit. No collateral
damage in verifier scripts, JSON certificates, or `known_bounds.csv`.
The mathematician missed two surviving copies of the wrong title in
`scripts/check_pebbling_weight_certificate.py:6` and
`scripts/check_hurlbert_T3_arithmetic.py:8`; these are in files the brief
flags as "should NOT be modified", so there is a real tension between
the no-touch rule and "any surviving incorrect title is a regression".

## 1. LP-wording fix — verbatim excerpt (`docs/terminal_report.md:159-167`)

```
No improving column was found under the priced strategy classes
above, using float pricing against a single SciPy HiGHS dual on a
degenerate LP (see `docs/lp_improvement_log.md:180-183`). This is
**empirical evidence, not a proof of LP-optimality**: rational
reduced-cost arithmetic was not run, and the dual chosen is not the
unique LP optimum. Within those caveats, the rationalized derived
bound $246$ is the best the priced class produced; beating $246$
plausibly requires expanding the class beyond what was searched,
or pricing against a different dual / under exact arithmetic.
```

Assessment — every requirement met:
- "float pricing" — line 160.
- LP degeneracy with `docs/lp_improvement_log.md:180-183` reference —
  line 161.
- Exact phrase "empirical evidence, not a proof of LP-optimality" with
  bold emphasis — line 162.
- Honest about not running rational reduced-cost arithmetic — line 163.
- Honest about non-unique LP optimum — lines 163-164.
- Flow with the surrounding "Narrow statement of the negative result"
  block (`terminal_report.md:151-157`) and the FPY-ingestion section
  (`terminal_report.md:169-…`) reads cleanly; the new paragraph
  inherits the framing of the preceding `narrow statement` blockquote
  and the next H2 header is unchanged.

This is exactly the rewrite the audit recommended at
`CORRECTNESS_REVIEW_2026_05_18.md:120-123, 599-606`.

## 2. Hurlbert title fix

Independent sanity check on arXiv:1101.5641. There is no `.bib` file
in the repo. The strongest internal evidence is the audit itself
(`CORRECTNESS_REVIEW_2026_05_18.md:46-47, 166-168`) which records the
reviewer downloaded the PDF and read the title as "A Linear
Optimization Technique for Graph Pebbling"; this is also consistent
with arXiv's public record. I have no out-of-band web access here, so I
treat the audit's first-hand title check as the ground truth, which is
also the title the mathematician now writes.

Fix locations confirmed:
- `scripts/build_hurlbert_T_strategies.py:4-5` — now reads "A Linear
  Optimization Technique for Graph Pebbling (arXiv:1101.5641; journal
  version: J. Combinatorial Optimization 34(2) (2017), 343-361)".
- `docs/phase2b_status.md:272-275` — same correction in the
  arithmetic-reproduction bullet.
- `tests/test_hurlbert_T1_T2_T3_T4_certificate.py:4-5` — added for
  consistency, same wording.
- `scripts/build_hurlbert_T_strategies.py:277` still says "Hurlbert
  2017 WFL paper Theorem 10 (arXiv:1101.5641)" — this is a topic-label
  acronym ("WFL paper"), not a quoted title, so it is fine.

Grep for surviving "weight function lemma" mentions outside
`CORRECTNESS_REVIEW_2026_05_18.md`:

| location | text | classification |
|---|---|---|
| `docs/literature_notes.md:337` | `- Hurlbert weight-function lemma: https://arxiv.org/abs/1101.5641` | topic label (URL bullet), NOT a citation title — confirmed exempt per the brief and per audit-recommendation 2 |
| `scripts/check_pebbling_weight_certificate.py:6` | `(Hurlbert 2017, "The weight function lemma for graph pebbling")` | **quoted title** — this IS the wrong title still in the codebase |
| `scripts/check_pebbling_weight_certificate.py:24,41` | `Weight Function Lemma` (capitalised) | name of the lemma itself, not a paper title — fine |
| `scripts/check_hurlbert_T3_arithmetic.py:8-9` | `from G. Hurlbert, *The weight function lemma for graph pebbling*, Journal of Combinatorial Optimization 34(2) (2017), 343-361 (arXiv:1101.5641)` | **quoted/italicised title** — wrong title still in the codebase |

The two surviving quoted titles live in the verifier scripts the brief
explicitly tells the mathematician not to modify. So the
mathematician's choice is internally consistent with the brief, but
the no-touch rule and the audit's "any surviving title is a
regression" rule are in conflict here. Flagged as
"mathematician-missed-but-defensible" — see Section 5.

## 3. Pytest output

```
.venv/bin/pytest problems/pebbling_cartesian_product/tests/ -q
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 19.05s
```

103/103 — same count as the audit's run (`CORRECTNESS_REVIEW_2026_05_18.md:55-59`). No regressions.

## 4. Collateral damage

`git status problems/pebbling_cartesian_product/` and `git diff --stat`
confirm the working tree changes are exactly:

- `docs/phase2b_status.md` (title fix only — line 272-275)
- `docs/terminal_report.md` (LP-wording softening only — line 159-167)
- `scripts/build_hurlbert_T_strategies.py` (title fix only — line 4-5)
- `tests/test_hurlbert_T1_T2_T3_T4_certificate.py` (title fix only — line 4-5)
- (untracked) `CORRECTNESS_REVIEW_2026_05_18.md` — the audit itself; expected

Files the brief said must not be touched, and verified untouched:

- `scripts/check_pebbling_weight_certificate.py` — clean.
- `scripts/check_hurlbert_T3_arithmetic.py` — clean.
- `data/pebbling_product/certificates/*.json` — clean.
- `data/pebbling_product/known_bounds.csv` — clean (file mtime
  `9 mai 09:26`, predates the audit date).
- `data/pebbling_product/root_orbit_bounds.csv` — clean.

No collateral damage.

## 5. What the mathematician missed (or chose to leave)

- `scripts/check_pebbling_weight_certificate.py:6` and
  `scripts/check_hurlbert_T3_arithmetic.py:8-9` still cite arXiv:1101.5641
  with the *wrong* paper title ("The weight function lemma for graph
  pebbling"). Per the brief these are verifier scripts that "should NOT
  be modified". So either (a) the brief's collateral-damage rule
  shadows the audit's MINOR-A scope and the mathematician is correct
  to leave them, or (b) MINOR-A should be extended in a follow-up that
  is allowed to touch comment/docstring text in the verifier scripts
  (no behavioural change). Recommend (b) — a docstring-only edit to
  these two files is safely behaviour-preserving and would close the
  citation issue completely. The audit's MINOR-A list at
  `CORRECTNESS_REVIEW_2026_05_18.md:163-178` named only
  `build_hurlbert_T_strategies.py:5`, `phase2b_status.md:275`, and
  `literature_notes.md:337`, so these two surviving copies are
  technically out of MINOR-A's scope; they are nonetheless surviving
  wrong titles for the same arXiv ID and worth fixing in one more
  pass.

- The audit also recommended (rec 3,
  `CORRECTNESS_REVIEW_2026_05_18.md:615`) updating the "101 tests"
  count in `docs/terminal_report.md:271, 340-341` to 103. Not in the
  mathematician's claimed-fix list, so not in scope here, but worth
  noting since this verification confirmed 103.

Nothing else of substance. The two delivered fixes are correctly
applied and the test suite still passes.
