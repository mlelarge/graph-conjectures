# Submission packet — D18 (combined Two Structural Observations)

> **WITHDRAWN 2026-05-17.** Observation 1 of the combined paper is provably false at $t = 5$: a planar graph of Voigt 1993 has $\chi_\ell = 5$ and $\operatorname{cr} = 0 < 1 = \operatorname{cr}(K_5)$, contradicting the list-Albertson claim. The structural cause (Ackerman's chain uses $f_r(n)$ critical-graph edge floors, not merely Dirac) means even repairing the $t = 5$ counterexample would require a list-critical-edge-floor input that does not exist at the right strength. The D18 source is preserved with a banner; **the D16 spectral content is reinstated as Paper 2 (see `paper_D16.md`).**

**This packet is historical only.** Active submission plan is **D8 + D16**.

---

(Original packet content follows for traceability.)

## Title

**Two structural observations in the neighbourhood of Albertson's conjecture**

## Source

- `../D18_combined_observations/two_structural_observations.tex` (~55 KB, 15 pages)
- `../D18_combined_observations/two_structural_observations.pdf` (15 pages, ~340 KB)
- Bundled README: `../D18_combined_observations/README.md`

## Abstract (as drafted in `.tex`, ready to paste)

> We record two observations arising from an analysis of the structural slacks in the chain of partial results towards Albertson's conjecture. **First**, the Albertson–Cranston–Fox / Barát–Tóth / Ackerman chain establishing the conjecture unconditionally at chromatic number up to $t = 18$ depends on its $\chi$-hypothesis only through the Dirac minimum-degree bound, which lifts verbatim to list-coloring via the list versions of Dirac's and Brooks' theorems (Borodin 1977; Erdős–Rubin–Taylor 1979). Assembling these observations gives list-Albertson at $t \le 18$, strictly stronger than ordinary Albertson at the same range. **Second**, the Pach–Spencer–Tóth bisection-width Crossing Lemma, combined with Alon's spectral bisection lower bound, yields an explicit-$\theta$ Crossing Lemma for $d_0$-regular spectral $\theta$-expanders, $\operatorname{cr}(G) \ge (1-\theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$, with an Albertson-type corollary on regular spectral-expander critical graphs. We are not aware of an earlier Crossing-Lemma inequality with explicit spectral dependence. Neither observation closes the Cranston residual at $t \in \{25, 26\}$; both are recorded as side-observations in the structural neighbourhood of the conjecture.

## Author line

Placeholder: `(draft) Marc Lelarge \thanks{marc.lelarge@gmail.com}`

**Decision pending:** consider co-author(s) with expertise in either list-coloring (Observation 1) or spectral graph theory (Observation 2). Solo authorship is viable since both observations are honestly framed as assembly/packaging.

**"Email first" recommendation:**
- **Cranston** — Observation 1 §3 cites his $t \le 24$ extension; courteous heads-up worth sending.
- **Borodin / Kostochka / Woodall** — Observation 1 §3 hinges on a list-edge-coloring constant from their 1997 paper. Worth a "is there a sharper unpublished version?" email before posting.
- **Pach / Spencer / Tóth** — Observation 2 packages their bisection-width Crossing Lemma; courteous "we made this explicit" email.
- **No need to email Ackerman** — D18 lifts his Albertson chain to lists rather than competing with it.

## Primary journal target

**Discrete Mathematics** — regular article (not Note, since 15 pages).

- Fit: 15-page paper assembling two unrelated-but-related structural observations on a classical conjecture; honest framing as "observations" not "new theorems". *Discrete Math* publishes such bundled-observation papers.
- Submission via Elsevier Editorial System.
- Expected turnaround 4–8 months.

## Fallback journal targets

1. **European Journal of Combinatorics** — equivalent venue, possibly slightly better fit for the list-coloring half.
2. **Electronic Journal of Combinatorics** — open access, no APC; solid backup.
3. **Journal of Graph Theory** — would prefer the spectral-expander half; less natural for the combined paper.

## arXiv category

**Primary:** `math.CO` (Combinatorics)

**Cross-list:** consider `cs.DM` (Discrete Mathematics) — the spectral-expander half (Observation 2) has CS-side interest via bisection-width / VLSI / graph layout connections.

## 3-sentence cover note (for editor)

> We record two structural observations on Albertson's conjecture, $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$ for graphs of chromatic number at least $t$. (i) The unconditional chain through chromatic number $t = 18$ (Albertson–Cranston–Fox / Barát–Tóth / Ackerman) lifts to list-coloring through the list versions of Dirac's and Brooks' theorems, giving list-Albertson at $t \le 18$ and DP-Albertson at $t \le 18$ as a corollary; the boundary at $t = 18$ is structural and we explain in §2.3 why the same lift does not currently extend to Cranston's $t \le 24$. (ii) The Pach–Spencer–Tóth bisection-width Crossing Lemma, combined with Alon's spectral bisection bound, yields a Crossing-Lemma inequality with explicit dependence on the spectral parameter $\theta$ — $\operatorname{cr}(G) \ge (1-\theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$ for $d_0$-regular $\theta$-spectral expanders — together with an Albertson-type corollary on regular spectral-expander critical graphs (honestly vacuous in the Dirac-floor regime). Neither observation closes the Cranston residual at $t \in \{25, 26\}$; both are recorded as structural side-observations, with the companion preprint (D8 in this bundle) handling the FPS Lemma 2.3 sharpness side independently.

## Provenance / history

- D15 + D16 emerged independently as Track B targets after R5a was closed (D8 sharpness theorem).
- Each was originally drafted as a stand-alone paper (~9 pages).
- A bundling review (`bundling_recommendation.md`, 2026-05-17) concluded that both are honestly-modest "assembly" results and reading more honestly when combined.
- Implementation: editorial assembly merged the two into a single 15-page paper. No new mathematics; one stylistic patch applied (D16's "first Crossing-Lemma improvement..." overstatement softened to "we are not aware of an earlier ..." to match D16's own §1 hedge).
- Removed D16's `\cite{D13}` (internal team memo; replaced with one-sentence trajectory note in Acknowledgements).
- Removed D16's `\cite{D15}` (now internal cross-reference).
- Kept D16's `\cite{D8}` (the R5a sharpness paper remains a separately-submitted companion).

## Open items before submission

- Confirm author list.
- Decide whether *Discrete Math* (currently primary) or EJC is the right venue.
- Coordinate arXiv posting with D8 (same-day posting; D18 cites D8).
- Send "email first" notes per the matrix above.

## Files no longer being separately submitted

- `paper_D15.md` and `paper_D16.md` in this directory are **superseded by this packet**. The standalone source files at `../D15_list_albertson_paper/` and `../D16_expander_crossing_paper/` are preserved for traceability but **should not be posted**.
