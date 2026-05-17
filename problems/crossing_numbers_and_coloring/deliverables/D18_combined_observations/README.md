# D18 -- Two structural observations in the neighbourhood of Albertson's conjecture

This directory contains the combined paper that bundles the two
side-observations previously written up as D15 and D16 into a
single short note. The bundling decision is recorded in
`../D17_submission_packets/bundling_recommendation.md` (Option B).

## What the paper combines

- **Observation 1 (D15)**: List-Albertson at $t \le 18$. The
  Albertson--Cranston--Fox / Bar\'at--T\'oth / Ackerman chain lifts
  verbatim to list-coloring via the list versions of Dirac's and
  Brooks' theorems. Lives in Section 2 of the combined paper.
- **Observation 2 (D16)**: A bisection-width Crossing Lemma for
  regular spectral expanders. Packages
  Pach--Spencer--T\'oth + Alon (expander mixing lemma) into a
  single explicit-$\theta$ inequality, with an Albertson-type
  corollary on regular spectral-expander critical graphs. Lives in
  Section 3 of the combined paper.
- A common Section 4 ("Common scope and limitations") records once
  that neither observation closes the Cranston residual at
  $t \in \{25, 26\}$, and points to the companion paper D8 for the
  orthogonal Fox--Pach--Suk Lemma~2.3 sharpness side.

## Changes made during the merge

1. **D16 abstract overstatement softened.** The original D16
   abstract claimed the result was "the first Crossing-Lemma
   improvement specifically tailored to graphs whose spectrum is
   well-separated". This was softened to "we are not aware of an
   earlier Crossing-Lemma inequality with explicit spectral
   dependence", matching the hedge used in D16's own Section 1.
2. **D13 cross-reference removed.** The original D16 cited an
   internal team memo (D13) on a min-degree-aware Crossing Lemma
   attack that will not be published. The reference is replaced by
   a one-sentence summary in the Acknowledgements section ("the
   present packaging emerged from an attempt at a direct
   min-degree-aware Crossing Lemma that failed cleanly, the
   density-iteration machinery being degree-sequence-insensitive at
   its iteration-stopping step").
3. **D15 cross-reference removed.** Since D15 content is now in the
   same paper, D16's `\cite{D15}` (used in the Albertson corollary
   preliminaries) is replaced by an internal `\Cref{lem:list-dirac}`
   reference.
4. **D8 cross-references preserved.** Both D15 and D16 cite the R5a
   sharpness paper (D8); in the merged paper a single
   `\bibitem{D8}` covers both citation sites.
5. **Bibliographies merged.** Duplicates dropped: `Ackerman`,
   `Albertson`, `BK24`, `Cranston`, `Diestel`, `Dirac1952`, `FPS`.
   The combined bibliography has 32 entries.
6. **Unified notation.** Union of D15's and D16's preambles:
   `\DeclareMathOperator{\crN}{cr}` (shared, kept once),
   `\DeclareMathOperator{\chl}{\chi_{\ell}}` and
   `\DeclareMathOperator{\chDP}{\chi_{\mathrm{DP}}}` (from D15),
   `\DeclareMathOperator{\bw}{bw}` and `\newcommand{\eps}{\varepsilon}`
   (from D16), plus `\NN`, `\RR` (shared).
7. **Honesty note rephrased.** D15's explicit "Honesty note"
   paragraph is preserved but rephrased to cover both observations:
   "Both observations recorded here are not so much new theorems as
   observations that existing chains of theorems lift or package to
   one degree of generality higher."
8. **Theorems renumbered.** Theorem 1 = list-Albertson (formerly
   D15 Theorem 1.3); Theorem 2 = expander Crossing Lemma (formerly
   D16 Theorem 1.1). Internal labels updated to `thm:main-list` and
   `thm:main-spec` respectively.

## Compile status

- Source: `two_structural_observations.tex`
- Compiled via: `pdflatex -interaction=nonstopmode -halt-on-error`
  (TeX Live 2024, two passes for cross-references)
- Output: `two_structural_observations.pdf`, **15 pages**, target
  range 12--16 met
- Status: zero LaTeX errors, zero undefined references, no
  overfull boxes, no underfull box warnings
- Preamble matches the D8 stylistic template (`amsmath`, `amssymb`,
  `amsthm`, `booktabs`, `cleveref`, `hyperref`)

## Status

**Ready for submission**, pending author/journal decisions in the
companion D17 submission packet directory.
