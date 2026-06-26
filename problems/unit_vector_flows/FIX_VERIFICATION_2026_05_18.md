# Fix verification — unit_vector_flows

**Verifier:** independent fix-verification pass
**Date:** 2026-05-18
**Scope:** confirm that the targeted fixes claimed by the mathematician
were applied correctly in
`problems/unit_vector_flows/`,
relative to `CORRECTNESS_REVIEW_2026_05_18.md`.

---

## Verdict

The targeted fixes are **substantially applied and correct**. Sections 02
and 03 of the paper have been rewritten from bare-skeleton TODO scaffolds
into mathematically real prose; the load-bearing Lemma 2.5 now carries
an honest dimension-count proof; the Krawczyk-operator definition,
schema-v2 description, and numerical-gotchas paragraph have all been
expanded from "describe later" stubs into the actual content. Each
section retains exactly one focused option-B `\TODO` — the MMRT25
calibration transcription
(`paper/sections/02_preliminaries.tex:110`) and the Krawczyk--Moore bib
citation stub (`paper/sections/03_certification.tex:102`) — both of
which are bounded, well-scoped editorial notes rather than vague filler.
The stale-count fixes in `README.md`, `THEOREM.md`, and `Makefile` are
applied as claimed; the Ulyanov re-check is genuinely clean. The paper
compiles end-to-end with no undefined references and no missing
citations. One MINOR issue the mathematician missed:
`README.md:77` still says "All 67 certificates pass a clean replay" —
this is a third stale count that the fix list did not include.

---

## Paper §02 walkthrough

Read end-to-end (`paper/sections/02_preliminaries.tex` lines 1--208).
What was filled (option A):

- **Section 2.1 (`sec:prelim-flows`, lines 8--67):** Cubic-graph and
  bridgelessness definitions are in place
  (`02_preliminaries.tex:11--13`). Sign convention pinned to the
  codebase via `scripts/witness.py:orient`
  (`02_preliminaries.tex:14--20`). General $A$-flow definition
  (`:22--29`), then `Definition` of $\Sphere$-flow
  (`:31--43`) that matches `THEOREM.md:10--12` verbatim in content.
  Lemma 2.5 reference is consistent. The 120-degree triple lemma
  (`lem:120-degree`, `:45--62`) is stated and proved with the
  standard inner-product calculation $3 + 2\sum v_i \cdot v_j = 0$,
  matching `docs/plan.md:33--40` and `HMM26` Observation 9.

- **Section 2.2 (`sec:prelim-snarks`, lines 69--90):** Standard cyclic
  edge-connectivity and snark definitions. The `definition` block
  (`:79--83`) defines "nontrivial snark" as girth $\ge 5$ and
  cyclically $4$-edge-connected, which matches `THEOREM.md:8--10` and
  the BGHM-2013 convention. The reference to BGHM13 and snarkhunter
  is consistent with `refs.bib`.

- **Section 2.3 (`sec:prelim-cdc`, lines 92--108):** CDC and oriented
  CDC are defined. $H_d$-flow is introduced in MMRT25's sense
  (`:99--102`), and the $d=4$ specialisation ("oriented 4-CDC $\equiv$
  $H_4$-flow $\Rightarrow$ nowhere-zero 4-flow") is stated as the
  calibration used in §5. **One focused TODO survives** at
  `02_preliminaries.tex:110--114` — explicitly flagged as an option-B
  stub asking for verbatim transcription of MMRT25 Theorem 4 from the
  source paper. The TODO is bounded (one specific external citation),
  not vague.

- **Section 2.4 (`sec:prelim-gauge`, lines 116--146):** The
  $\SO(3)$-equivariance argument is in place. The pinning gauge to
  $((1,0,0), (-1/2, s/2, 0), (-1/2, -s/2, 0))$ with $s^2 - 3 = 0$ is
  written out explicitly (`:127--134`) and points to
  `scripts/exact.py:build_ideal`. Variable-elimination accounting
  ("nine of the original $3|E|$ scalar variables eliminated, Kirchhoff
  at vertex 0 identically satisfied") matches the code's actual
  behaviour and the original audit's §3.1 count.

- **Lemma 2.5 (`lem:square-system`, `:148--168`)** and its **proof**
  (`:170--201`) are present. The proof has two parts:
  * (i) Linear-dependency argument
    (`:171--184`). The dependency count is established by the
    standard "every edge contributes $+\varphi(e)$ and
    $-\varphi(e)$ exactly once to the sum" calculation
    (`:175--177`), plus a citation of the rank of the incidence
    matrix of a connected oriented graph ($|V|-1$) to argue that no
    further dependency exists.
  * (ii) Dimension count after pinning + drop
    (`:186--201`). The arithmetic $3(|V|-1) - 3 + |E| - 3 + 1 =
    3|V| + |E| - 8 = 9|V|/2 - 8$ in both polynomials and free
    variables matches the audit's §3.1 verification.

  **Note:** part (ii) argues counts (number of polynomials =
  number of unknowns = $9|V|/2 - 8$) rather than algebraic
  independence of the resulting equations. This is fine for the
  rest of the proof: the Krawczyk operator verifies Jacobian
  nonsingularity at the certified centre by §3.4 of the audit, and
  Lemma 2.5 is only used to establish squareness. The proof
  honestly establishes the dimension count, which is what the rest
  of the paper invokes.

No vague `\TODO{...}` placeholders remain. The one surviving TODO at
line 110 is a focused option-B note on MMRT25 Theorem 4 transcription,
exactly as the mathematician claimed.

---

## Paper §03 walkthrough

Read end-to-end (`paper/sections/03_certification.tex` lines 1--205).

- **Lead paragraph** (`:1--20`): outlines the four-stage pipeline
  (witness, refinement, Krawczyk, schema-v2) and names the
  implementing files.
- **§3.1 Numerical witness search** (`sec:certification-witness`,
  `:22--50`): LM with `scipy.optimize.least_squares(method="lm")`,
  $\|F\| \le 10^{-10}$ acceptance threshold, multi-seed retry, two
  failure modes (saddle plateau, near-singular Jacobian) with the
  seed-rotation remedy. Matches the code at
  `scripts/witness.py:75--127` as the audit verified.
- **§3.2 Gauge fix + Newton refinement**
  (`sec:certification-refine`, `:52--73`): rotation into the pinning
  gauge of §2.4 plus Newton at 50 dps using `mpmath.lu_solve`
  iteratively. Empirical centre residual $|F(c)| \approx 10^{-51}$
  is recorded (`:70--73`), matching the audit's spot-check.
- **§3.3 Interval Krawczyk** (`sec:certification-krawczyk`,
  `:75--151`): the Krawczyk operator formula
  $K(\mathbf{I}) = c - YF(c) + (E - YJ(\mathbf{I}))(\mathbf{I} - c)$
  appears as an equation `eq:krawczyk-operator` (`:86--89`), with
  $Y = J(c)^{-1}$ and box radius $r = 10^{-5}$. The
  **Krawczyk--Moore theorem** is stated as `thm:krawczyk`
  (`:100--113`): on $C^1$ neighbourhoods of $\mathbf{I}$, strict
  componentwise inclusion implies existence, uniqueness, and
  Jacobian regularity. This statement is the standard one cited in
  the audit's §3.4. The corollary
  `cor:s2-flow-from-zero` (`:123--129`) makes the bridge from "zero
  of $F$ in $\mathbf{I}$" to "$\Sphere$-flow on $G$" explicit. The
  **Numerical gotchas** paragraph (`:131--151`) is now real prose,
  not a placeholder: it explains why $F(c)$ is evaluated at the
  point and why `lambdify(modules=None)` is used. Both points
  match the audit's §3.3.
- **§3.4 Schema-v2 replayable certificate**
  (`sec:certification-replay`, `:153--205`): the eight-bullet field
  list of the JSON document (`:159--175`) matches the cert format
  the audit's §5 spot-checked. The five-step replay procedure
  (`:179--191`) is given with file/line pointers to
  `verify_sweep.py:verify_one` and `interval.py:replay_krawczyk`,
  and is consistent with the audit's §2.8 verification. The
  `--allow-hash-mismatch` defensive option (`:200--204`) and the
  cold-environment replay log in `docs/external_replay/` are
  mentioned.

**One focused TODO survives** at `03_certification.tex:102--104`,
inside the statement of `thm:krawczyk`, asking for a `refs.bib`
entry for Krawczyk 1969 and/or Moore 1977. This is a citation stub,
not vague prose; the theorem statement and proof structure are
written out. This matches the mathematician's option-B claim.

No vague `\TODO{...}` placeholders remain in §03.

---

## Ulyanov framing grep result

```
grep -rni "quaternion|S\^3|S\^{3}|Sphere\^3" .
```
returns three matches — all three are *inside*
`CORRECTNESS_REVIEW_2026_05_18.md` lines 52, 400, 401, which is the
audit document discussing the misdescription that existed only in the
review prompt. **No quaternion / $S^3$-flow language appears anywhere
in the package source.** Confirmed clean. The mathematician's claim
that this fix was a no-op is correct.

---

## Counts assessment

- `pytest --collect-only` reports `184 tests collected in 0.52s`,
  matching the new claim everywhere.
- `README.md:144` says `184/184 tests`; `README.md:145` says
  `3247/3247 interval replays`. Both correct.
- `Makefile:24` says `pytest regression (184 tests, ~6s)`. Correct.
- `Makefile:25` says `replay 3247 interval certificates`. Correct.
- `THEOREM.md:98` says `184/184 regression tests`; `THEOREM.md:99`
  and `:102` say `3247`. Correct.
- **MISS** — `README.md:77` still says
  `All 67 certificates pass a clean replay`. This is a third stale
  count that the mathematician did **not** mention in the fix list
  but is logically in the same category as the "41 tests" /
  "347/347" fixes. Should also have been updated to `3247`. MINOR
  documentation drift, not a math issue.

---

## LaTeX-build result

`make` in `paper/` (Makefile drives `pdflatex; bibtex; pdflatex;
pdflatex`) **succeeds**. Final line of compile:
```
Output written on main.pdf (16 pages, 482962 bytes).
```
No `Undefined reference`, no `Citation ... undefined`, no
`LaTeX Error` in `main.log`. Only cosmetic warnings (Overfull \\hbox
on long inline code paths in `\TODO{...}` blocks elsewhere; standard
`hyperref` warnings about math characters in section titles for the
PDF outline). All `\cref{...}` references to `lem:square-system`,
`def:s2-flow`, `eq:krawczyk-operator`, `thm:krawczyk`,
`cor:s2-flow-from-zero`, `sec:certification-krawczyk`,
`sec:prelim-gauge` resolve.

One minor BibTeX-log artefact: the new TODO comment block at the
top of `refs.bib` contains the strings ``@misc{Jain07,...}`` and
``@article{Krawczyk69,...}`` inside `%`-prefixed comment lines.
BibTeX scans for `@` regardless of `%` and emits two warnings
(`main.blg`):
```
"}" immediately follows a field name---line 11 of file refs.bib
"}" immediately follows a field name---line 16 of file refs.bib
I'm skipping whatever remains of this entry
```
These warnings do **not** affect the bibliography output
(`main.bbl` contains the 7 expected entries: `BGHM13`,
`snarkhunter`, `HMM26`, `python_sat`, `MMRT25`, `Uly26`, `mpmath`,
plus `nauty` — actually 8, all the real entries). The warnings are
harmless to compilation but are introduced by the new comment
block; a clean fix would be to drop the literal `@` from the
comment text (e.g. write "Add a misc entry keyed Jain07" instead
of "`@misc{Jain07,...}`"). MINOR cosmetic.

---

## Collateral-damage check

- `git diff --stat HEAD problems/unit_vector_flows/scripts/`
  returns empty — `scripts/` untouched. ✓
- `git diff --stat HEAD problems/unit_vector_flows/data/` returns
  empty — `data/` untouched. ✓
- `git diff --stat HEAD problems/unit_vector_flows/CORRECTNESS_REVIEW_2026_05_18.md`
  returns empty — the audit document is preserved verbatim (and is
  in fact an untracked new file, as expected). ✓
- Section labels and theorem/lemma/definition labels in 02 and 03
  are preserved (`sec:preliminaries`, `sec:prelim-flows`,
  `sec:prelim-snarks`, `sec:prelim-cdc`, `sec:prelim-gauge`,
  `lem:120-degree`, `def:s2-flow`, `def:nontrivial-snark`,
  `lem:square-system`; `sec:certification`,
  `sec:certification-witness`, `sec:certification-refine`,
  `sec:certification-krawczyk`, `sec:certification-replay`,
  `eq:krawczyk-operator`, `thm:krawczyk`, `cor:s2-flow-from-zero`).
  Cross-checked the original (`git show HEAD:...`) and the new file;
  no label was renamed or dropped. ✓
- Sections 01, 04, 05, 06, 07, 08, 09 in `paper/sections/` are
  untouched (verified by `git diff` returning empty for all). ✓
- `paper/main.tex` and `paper/Makefile` untouched. ✓

No accidentally-deleted equations or section headings.

---

## Things the mathematician missed

1. **README.md:77** — the stale count "All 67 certificates pass a
   clean replay" was not updated. The fix list mentioned only the
   `41 tests` → `184 tests` and `347/347` → `3247/3247` swaps, but
   the `67` figure in the body prose (which is clearly an even
   staler residual from an earlier iteration) is in the same
   category. Should be `3247`. MINOR.

2. **`refs.bib` TODO comment block triggers BibTeX warnings**. The
   substantive content of the block is fine and lists exactly the
   three items the mathematician described (MMRT25 metadata, Jain
   2007 OPG entry, Krawczyk 1969 entry). But because the comment
   text quotes `@misc{Jain07,...}` and `@article{Krawczyk69,...}`
   literally, BibTeX sees the `@` and tries to parse them as
   entries, then emits two skip-warnings. This is harmless to the
   compiled bibliography (the 7 real entries all appear in
   `main.bbl`) but is observable noise. Trivial to fix by escaping
   the `@` (e.g. "at-misc entry keyed Jain07") or by rephrasing.
   COSMETIC.

3. **Lemma 2.5 (ii) argues counts, not independence.** The proof
   counts polynomials and free variables on both sides
   (`02_preliminaries.tex:186--201`) and matches them to
   $9|V|/2 - 8$. This is what the lemma statement asks for
   ("the resulting polynomial system together with ... has exactly
   $|E| - 3 + 1$ polynomials ... in the same number of free
   variables"), so the proof discharges the stated claim. But
   "square" in the strong sense (full-rank Jacobian generically)
   is left to the Krawczyk certification itself to verify per-graph.
   This is not a defect of the fix — the lemma as stated is about
   counts, and the proof establishes the counts — but readers may
   want a forward pointer to §3.3 explaining where Jacobian
   nonsingularity is actually checked. NIT.

4. **Definition of "$A$-flow" at lines 22--26 omits the
   nowhere-zero condition** in the general $A$-flow case, then says
   on `:25--26` "A flow is *nowhere-zero* if $\varphi(e) \ne 0$ for
   every $e$." This is fine — the nowhere-zero condition is then
   noted to be automatic for $\Sphere$-flows (`:42`). Consistent
   with the standard convention. No issue, just worth noting that
   the definition order is "$A$-flow first, then nowhere-zero as a
   property, then $\Sphere$-flow."

---

## Bottom line

The five claimed fixes are all genuine and substantially correct.
The only material miss is `README.md:77` ("67 certificates"), which
is in the same documentation-drift category as the count fixes the
mathematician did make, and is a one-character edit away from clean.
The new Lemma 2.5 proof discharges the lemma statement; the §03
prose is real, not placeholder. The paper compiles, no broken
references, no fabricated bib entries. `scripts/`, `data/`, and the
audit document itself are untouched. **The fix pass is acceptable**;
recommend a tiny follow-up to (a) update `README.md:77` to `3247`,
and (b) escape the `@` characters in the new `refs.bib` TODO comment
block.
