# Submission packet — D16 (Bisection-width Crossing Lemma for spectral expanders)

> **REINSTATED 2026-05-17.** Earlier marked "SUPERSEDED by Option B" when D18 combined D15+D16 was the plan; D18 has since been withdrawn because Observation 1 (the D15 content) is provably false at $t = 5$ (Voigt 1993 planar graph with $\chi_\ell = 5$, $\operatorname{cr} = 0$). The D16 spectral content is now reinstated as the active **Paper 2** of the bundle, with four senior-referee fixes applied (odd-$n$ floor in spectral bisection bound, PST proof bookkeeping, BK-threshold-compliant numerical illustration, corrected Ore-scope claim). See `../D16_expander_crossing_paper/README.md` for the patch details.

## Title

**A bisection-width Crossing Lemma for regular spectral expanders, with an Albertson corollary**

## Source

- `../D16_expander_crossing_paper/expander_crossing.tex` (30 KB)
- `../D16_expander_crossing_paper/expander_crossing.pdf` (9 pages)

## Abstract (as drafted in `.tex`, ready to paste)

> We package the Pach–Spencer–Tóth bisection-width Crossing Lemma together with Alon's spectral bisection bound for regular spectral expanders into a single explicit inequality: for every $d_0$-regular graph $G$ on $n$ vertices with second adjacency eigenvalue $|\lambda_2(G)| \le \theta d_0$, $\operatorname{cr}(G) \ge (1 - \theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$. Both inputs are classical; the contribution is the explicit packaging of the spectral parameter $\theta$ inside the Crossing-Lemma constant, which to our knowledge has not been written down in this form. We then deduce an Albertson-type corollary on $t$-critical $d_0$-regular spectral expanders, and are explicit that the result does not address the Cranston residual triples $(t, n) \in \{(25, 48), (26, 50), (26, 51)\}$ — Ore compositions of $K_{26}$ are not spectral expanders. The constant $1/1280$ comes from a self-contained inline derivation through the dual bisection inequality; the sharper Pach–Spencer–Tóth form replaces $1/1280$ by $1/640$.

## Author line

Placeholder: `(draft) Marc Lelarge \thanks{\texttt{marc.lelarge@gmail.com}.}`

**Decision pending:** consider co-authors with spectral-graph-theory expertise. The paper is essentially "make explicit what was implicit in PST + Alon"; a spectral-expert co-author would lend authority to the framing.

**"Email first" recommendation:** **Light email to Janos Pach or Andrew Suk** mentioning that this is a follow-on to the FPS framework used in D8, in the same batch. Not strictly necessary since the paper does not modify any of their results, but courteous.

## Primary journal target

**Journal of Graph Theory** — regular article.

- Fit: 9-page paper, one main theorem (Crossing-Lemma variant), one corollary (Albertson on a structural sub-class). JGT is the natural home for results that mix bisection-width / spectral / topological graph theory.
- Submission via Wiley Online Library.
- Expected turnaround 4–9 months.

## Fallback journal targets

1. **Combinatorica** — better prestige; might find this too modest in scope. Try only if there's appetite.
2. **Discrete Applied Mathematics** — viable for the bisection-width framing.
3. **European Journal of Combinatorics** — same level as JGT; viable backup.

## arXiv category

**Primary:** `math.CO` (Combinatorics)

**Cross-list:** `cs.DM` (Discrete Mathematics) — bisection width has strong CS connections and the paper would be of interest to that community.

## 3-sentence cover note (for editor)

> We package two classical ingredients — the Pach–Spencer–Tóth bisection-width Crossing Lemma and Alon's spectral bisection lower bound — into a single explicit Crossing Lemma with the spectral gap $\theta$ appearing in the leading constant: $\operatorname{cr}(G) \ge (1 - \theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$ for $d_0$-regular $G$ with $|\lambda_2| \le \theta d_0$. To our knowledge this is the first Crossing-Lemma inequality with an explicit spectral coefficient, and it gives a strict improvement over the Bungener–Kaufmann density-based Crossing Lemma whenever $G$ is moderately dense and spectrally well-separated. We record an Albertson-type corollary on regular spectral-expander critical graphs and are explicit in §5 about the limitation: the corollary is non-vacuous only above $n \gtrsim 30 t$ under the headline constant, well above the Cranston-residual regime $n \approx 2t$.

## Provenance / history

- D13 R2c attack memo: direct min-degree-aware sharpening of the Crossing Lemma failed cleanly (random-sampling proof loses $d_0$ at the iteration-stopping step).
- D13 §6 proposed the bisection-width fallback as $T_1'$ with constants $/256$ and $-n^2/16$ — neither correct.
- D16 corrected the constants:
  - PST's bisection inequality has $1/40$ (optimised) or $1/80$ (squared-dual inline); Alon gives $1/4$ inside, squared $1/16$ outside.
  - Combined: $1/640$ (sharper) or $1/1280$ (self-contained), with $d_0^2 n / 16$ as the second term (not $n^2/16$, because $\sum_v \deg(v)^2 = d_0^2 n$ for regular $G$).
- Headline: D16 uses the self-contained $1/1280$ form; remarks explain the $1/640$ strengthening.
- Self-citation removed (the paper had `\bibitem{D16}` referring to itself; cleaned up in QA pass D17b).

## Open items before submission

- Confirm author list.
- Decide whether to invoke the sharper $1/640$ in the headline by re-proving PST's optimised constant inline (one extra page of work) before submission.
- Confirm the literature claim "to our knowledge no Crossing-Lemma inequality has an explicit $\theta$" via a brief literature pass.
- Coordinate arXiv posting with D8 and D15 (same-day burst recommended).
