# Submission packet — D15 (List-Albertson $t \le 18$)

> **WITHDRAWN 2026-05-17.** The main theorem is provably false at $t = 5$: a planar graph of Voigt 1993 has $\chi_\ell = 5$ (every planar graph is 5-choosable by Thomassen 1994; Voigt's example is not 4-choosable) and $\operatorname{cr} = 0 < 1 = \operatorname{cr}(K_5)$, directly falsifying "$\chi_\ell(G) \ge t$ and $t \le 18 \Rightarrow \operatorname{cr}(G) \ge \operatorname{cr}(K_t)$" at $t = 5$. The structural cause is that the ACF/BT/Ackerman chain does not in fact use $\chi$ only through Dirac's $\delta \ge t - 1$: Ackerman §3.1 uses the minimum-edge-count function $f_r(n)$ for $r$-critical graphs, and the list-critical analogue (Krivelevich 1997) gives a weaker edge floor, so the "lifts for free" claim is unjustified even apart from the counterexample. The combined paper D18 that embedded this result is also withdrawn. The D15 source remains for historical record.

## Title

**List-coloring Albertson up to chromatic number 18**

## Source

- `../D15_list_albertson_paper/list_albertson_le_18.tex` (~32 KB)
- `../D15_list_albertson_paper/list_albertson_le_18.pdf` (9 pages)

## Abstract (as drafted in `.tex`, ready to paste)

> We prove the list-coloring version of Albertson's conjecture for chromatic numbers up to $18$: every graph $G$ with $\chi_\ell(G) \ge t$ and $t \le 18$ satisfies $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$. The proof is a clean lift of the Albertson–Cranston–Fox / Barát–Tóth / Ackerman chain (unconditional ordinary Albertson at $t \le 18$, arXiv:1006.3783, 0909.0413, 1509.01932) from chromatic to list-chromatic: each step uses only the Dirac minimum-degree bound $\delta(G) \ge t - 1$, which holds verbatim for list-critical graphs (Erdős–Rubin–Taylor 1979). The same proof yields the DP-coloring version (every DP-$t$-critical graph is list-$t$-critical). We also prove a conditional theorem extending the unconditional range to $t \le 24$ (matching the Cranston extension, arXiv:2512.08020), conditional on a list-edge-coloring version of Fox–Pach–Suk Lemma 2.3 at constant $9/16$; the best published list-edge-coloring substitute (Borodin–Kostochka–Woodall 1997, JCTB 71) gives only $\approx 7/4$, which falls short of the threshold.

## Author line

Placeholder: `(draft) Marc Lelarge \thanks{\texttt{marc.lelarge@gmail.com}.}`

**Decision pending:** consider co-authors with expertise in list-coloring (e.g., DP-coloring specialists) for the credibility lift on the §5 conditional extension. Honest framing: this paper is an assembly result, not a deep new theorem.

**"Email first" recommendation:** **None required.** This is an assembly result that doesn't pre-empt or contradict anyone's prior work. If posted around the same time as D8, the FPS team will see D15 alongside D8.

## Primary journal target

**European Journal of Combinatorics** — "Short Communication" or regular article.

- Fit: 9-page paper assembling four classical results (ACF/BT/Ackerman/ERT) into a new list-coloring statement. Established journal for combinatorics; appropriate for assembly results when the assembly is non-obvious and the resulting statement is itself new.
- Submission via Elsevier Editorial System.
- Expected turnaround 4–8 months.

## Fallback journal targets

1. **Journal of Combinatorial Theory, Series B** — higher prestige; might find this too modest in scope. Try first only if there's appetite.
2. **Electronic Journal of Combinatorics** — open access, no APC. Solid backup.
3. **Discrete Mathematics** — viable, but EJC is the more natural list-coloring venue.

## arXiv category

**Primary:** `math.CO` (Combinatorics)

**Cross-list:** consider `math.CO` only; the paper is purely combinatorial.

## 3-sentence cover note (for editor)

> We prove the list-coloring (and DP-coloring) version of Albertson's conjecture for chromatic numbers up to $18$: $\chi_\ell(G) \ge t$ with $t \le 18$ implies $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$. The argument is a clean lift of the existing Albertson–Cranston–Fox / Barát–Tóth / Ackerman proof chain; we verify that each step uses only Dirac's $\delta \ge t - 1$ bound, which holds verbatim for list-critical graphs (Erdős–Rubin–Taylor 1979). The boundary at $t = 18$ is structural: extending to Cranston's range $t \le 24$ requires a list-edge-coloring version of Fox–Pach–Suk's Lemma 2.3 at constant $9/16$, currently unavailable; we state this as a conditional Theorem 2.

## Provenance / history

- Identified as the front-runner Track B target after R5a was closed (D8) and R2c attack failed (D13).
- D14 attack memo verified that the ACF/BT/Ackerman chain uses chromatic number only through Dirac, and that list-Dirac (ERT 1979) gives the same input.
- D14 also identified the FPS list-version constant gap as the obstacle to extending past $t = 18$.
- Paper draft (D15) assembled the lift in 9 pages, with the conditional Theorem 2 as the §5 honest framing of the obstruction.

## Open items before submission

- Confirm author list.
- Decide whether to first attempt JCTB (higher prestige, longer wait) or go straight to EJC.
- Optional: brief literature pass to confirm no one has published this lift between Ackerman 2019 and now (the D14 memo flagged this as "needs verification").
- Coordinate arXiv posting with D8 and D16 (same-day burst recommended).
