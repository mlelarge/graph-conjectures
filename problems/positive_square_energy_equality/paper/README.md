# Paper source — *Towards positive-square-energy equality on 2-trees*

This directory holds the LaTeX source for the arXiv submission targeting
Conjecture 9.2 of Akbari–Kumar–Mohar–Pragada–Zhang
(arXiv:2506.07264) restricted to the 2-tree class.

## Build

```bash
make           # build main.pdf via latexmk
make watch     # live preview
make clean     # remove intermediate files, keep PDF
make distclean # wipe everything including PDF
make final     # build with \stub markers stripped (for submission)
```

Requires `latexmk` and a TeX distribution with `amsart`, `amsmath`,
`amssymb`, `hyperref`, `cleveref`, `booktabs`, `xcolor`, `enumitem`.
Note: `todonotes` is **not** used — the paper uses an in-preamble
`\stub{...}` macro that renders an orange [TODO] callout. Tested with
TeX Live 2024.

## Layout

```
paper/
├── main.tex                # entry point
├── preamble.tex            # packages, theorem envs, macros
├── abstract.tex            # ~180 words
├── references.bib          # bib entries (TBD details flagged)
├── sections/
│   ├── 01_intro.tex
│   ├── 02_notation_corollaries.tex
│   ├── 03_lprime_reformulation.tex
│   ├── 04_subfamily_theorems.tex
│   ├── 05_moment_form_ansatz.tex
│   ├── 06_failure_modes.tex
│   └── 07_open_problems.tex
├── appendices/
│   ├── A_reproducibility.tex
│   └── B_fixtures.tex
├── Makefile
└── README.md
```

Each section file is independently editable so multiple authors can
work in parallel without merge conflicts. The `preamble.tex` file holds
all theorem environments and notation macros — extend it rather than
defining macros inside section files.

## Working with `\stub`

The paper uses an in-preamble `\stub{...}` macro (provided in
`preamble.tex` via `\providecommand`) that renders an orange [TODO]
callout containing the description of what content should go in that
spot. Each `\stub{...}` describes exactly what prose + math is intended;
replace it inline as the section is fleshed out. A `\todo{...}` alias
forwards to `\stub` for legacy compatibility.

For the submission build, `make final` appends a one-line
`\renewcommand{\stub}[1]{}` to `preamble.tex` (and restores it
afterwards) so all `\stub` markers are silently swallowed.

## Status

Skeleton with mathematical content threaded through. Tracking grid:

| Section | Status | Owner |
|---|---|---|
| §1 Intro | skeleton, `\stub` markers, contributions list current as of v15 | TBD |
| §2 Notation + Corollaries A, B | skeleton | TBD |
| §3 (L') reformulation | skeleton; (L') correctly stated as a conjecture | TBD |
| §4 Subfamily theorems | skeleton (5 theorems stubbed) | TBD |
| §5 Moment-form ansatz | skeleton (B1, two-sided CS, diam-$\le 2$, b.minor, Stieltjes stubbed) | TBD |
| §6 Failure modes | skeleton (F1–F10 stubbed) | TBD |
| §7 Open problems | skeleton (Problems A, B stubbed; B reframed around $\Ivs \ge \threshold$) | TBD |
| App A Reproducibility | skeleton | TBD |
| App B Fixtures | skeleton (table format committed, F1–F10 rows) | TBD |
| `references.bib` | seeded; EFGW / Elphick--Linz / BBG entries corrected in v15 | TBD |

## Theorem-to-test cross reference (lives in `appendices/A_reproducibility.tex`)

The submission protocol: every numbered Theorem in the paper has a
regression test in the parent repo's `tests/` directory. Don't promote
a `\todo` to prose without confirming the test exists and passes.

## Style notes

- Use the macros in `preamble.tex` (`\sminus`, `\dminus`, `\Wm`,
  `\Monem`, `\Iinf{L}`, etc.) rather than rolling local notation. This
  keeps cross-references uniform if the normalisation (or threshold
  value) is later refined.
- AMS theorem numbering is by-section (`\newtheorem{theorem}{Theorem}[section]`).
  Lemmas, propositions, corollaries share the counter with theorems.
- Use `\Cref{...}` (cleveref) for typed references: emits
  "Theorem 4.1", "Lemma 5.3", etc.
- BibTeX keys are listed in `references.bib`; update *there* when adding
  citations, not inline.
- F2/F3 (the $\|w\|^2 = 4$ bug and the single-scalar threshold trap)
  are the kinds of errors that can sneak back into a draft. The
  preamble macros and the failure-modes section together act as a guard;
  cross-check before promoting prose.
