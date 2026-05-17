# Submission packet — D8 (R5a sharpness)

## Title

**An algebraic explanation for the degree threshold $9/8$ in Fox–Pach–Suk's bound towards Albertson's conjecture**

## Source

- `../D8_paper/sharpness_9_8.tex` (32 KB, 568 lines)
- `../D8_paper/sharpness_9_8.pdf` (7 pages, 295 KB)
- Retracted-draft companion: `../D8_paper/tighter_fps_RETRACTED.pdf` (preserved with banner)

## Abstract (as drafted in `.tex`, ready to paste)

> In their proof of Lemma 2.3 towards Albertson's conjecture (arXiv:2510.05893, SoCG 2025), Fox, Pach, and Suk introduce a degree threshold $d := \delta k$ and fix $\delta = 9/8$ without justification. We show that this choice is sharp within their Vizing–Gupta plus semi-random framework. Concretely, defining $F(\delta)$ to be the supremum of the three-case Claim 3.7 objective at a given $\delta$, we prove that $F(\delta) \ge 9/16$ for every $\delta \in (1, 5/4)$, with equality if and only if $\delta = 9/8$. The proof of the strict inequality $F(\delta) > 9/16$ for $\delta \in (1, 9/8)$ is analytic and short: at the witness point $\eta = 4/7$ in Case 2b, $f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2 / [7(4\delta - 1)] > 0$ for $\delta \neq 9/8$. Two structural reasons underlie this sharpness: the Case 2b objective has nonpositive derivative in $\eta$ at $\eta = 1/2$ iff $\delta \ge -3 + \sqrt{17} \approx 1.12311$ (the FPS choice $\delta = 9/8 = 1.125$ sits just above), and the Case 1 / Case 2a equalisation cubic $\delta^3 + 3\delta^2 - \delta - 4 = 0$ has its $(1, 5/4)$-root at $\delta_1 \approx 1.114907 < -3 + \sqrt{17}$ — exactly the regime where the Case 2b monotonicity assumption used in deriving it is violated. Any improvement to the Lemma 2.3 constant $c = 9/16$ must therefore come from outside this Claim 3.7 optimisation as currently formulated.

## Author line

Placeholder in `.tex`: `(draft) Marc Lelarge \thanks{\texttt{marc.lelarge@gmail.com}.}`

**Decision pending:** Marc to confirm whether to add co-authors. Plausible co-authors include Role 7 (the agent that did the FPS-PDF deep read and located Case 2b as the binding case) — though that is an AI artifact and would not appear as a human co-author.

**"Email first" recommendation:** **Email Fox, Pach, and Suk before posting.** This paper is a sharpness theorem on their result; it does not contradict anything they wrote, but they may want to see it before the arXiv timestamp. Suggested wording: "We've written a short note showing that your choice $\delta = 9/8$ is optimal inside your Claim 3.7 framework via a clean witness identity at $\eta = 4/7$. Attached for your information before we post. We are happy to incorporate any clarifications or to coordinate the arXiv posting with you."

## Primary journal target

**Discrete Mathematics** — "Note" section.

- Fit: 7-page focused note with one theorem, one elementary proof, clean structural insight on a recent SoCG result. *Discrete Math*'s Note section regularly publishes such items.
- Submission via Elsevier Editorial System; no submission fee.
- Expected turnaround 3–6 months.

## Fallback journal targets

1. **Electronic Journal of Combinatorics** — open access, no APC. Similar fit; slightly slower historically.
2. **Combinatorics, Probability and Computing** — better fit if the note is expanded with a probabilistic angle (currently not present, so secondary).
3. **arXiv only.** If neither journal lands, the paper has independent value as a preprint companion to FPS, especially if FPS themselves cite or link to it.

## arXiv category

**Primary:** `math.CO` (Combinatorics)

**Cross-list:** none needed; the paper is purely combinatorial.

## 3-sentence cover note (for editor)

> This is a short note that proves the choice of degree threshold $\delta = 9/8$ in the recent Fox–Pach–Suk SoCG 2025 paper on Albertson's conjecture (arXiv:2510.05893) is sharp within their three-case Claim 3.7 optimisation, via a clean witness identity at $\eta = 4/7$ giving $f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2 / [7(4\delta - 1)]$. The proof is elementary (no random sampling, no probabilistic estimates) and structurally explains the choice $9/8$ as sitting just above the critical value $-3 + \sqrt{17}$ where the Case 2b monotonicity-in-$\eta$ argument breaks. The result implies that any improvement of the FPS Lemma 2.3 constant $9/16$ must change one of the structural inputs (Vizing–Gupta, the multiplicity bound, or the semi-random construction itself), and we outline three concrete routes in §6.

## Provenance / history

- Initial attack: tighter-FPS draft proposed an improvement $9/16 \to F^* \approx 0.5574$.
- Senior referee fix #3 (Case 2b monotonicity) revealed that the proof silently assumed monotonicity for all $\delta$, when in fact it transitions at $-3 + \sqrt{17}$.
- Numerical check (`case2b_check.py`) confirmed the assumption fails at the proposed $\delta_1$, and $F(\delta_1) > 9/16$.
- The original draft was retracted with a banner (preserved as `tighter_fps_RETRACTED.pdf`).
- A clean obstruction note was written; the witness identity $f_{2b}(4/7, \delta) - 9/16 = 12(\delta - 9/8)^2/[7(4\delta-1)]$ then closed the analytic sign gap and elevated the note from EC to theorem-grade.

## Open items before submission

- Confirm author list.
- Confirm "email FPS first" decision (recommended yes).
- Coordinate arXiv posting with D15 and D16 (same-day burst recommended).
