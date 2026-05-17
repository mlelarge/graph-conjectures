# D8/D9/D10 — Paper directory

Two artifacts:

## 1. `sharpness_9_8.tex` / `sharpness_9_8.pdf` (current, 7 pages)

**Title.** An algebraic explanation for the degree threshold $9/8$ in Fox–Pach–Suk's bound towards Albertson's conjecture.

**Status.** Theorem-grade. Compiles cleanly with `pdflatex` (TeX Live 2024); a handful of routine `hyperref` warnings about math shifts in PDF strings are emitted but no errors and no missing references or overfull boxes.

**Main theorem.**
> Let $F: (1, 5/4) \to \mathbb R$ denote the supremum of FPS Claim 3.7's three-case objective at degree threshold $\delta$. Then $F(\delta) \ge 9/16$ for every $\delta \in (1, 5/4)$, with equality if and only if $\delta = 9/8$.

The FPS-admissible range $(1, 5/4)$ comes from FPS Claim 3.6's hypothesis $4d < 5k$; the larger optimisation-defined range $(1, 4/3)$ where Case 2b is meaningful is identified separately.

**Proof structure.**

- For $\delta \in [9/8, 5/4)$: trivial, $F(\delta) \ge f_1(\delta) = \delta/2 \ge 9/16$.
- At $\delta = 9/8$: $F(9/8) = 9/16$ by FPS Claim 3.7.
- For $\delta \in (1, 9/8)$: **witness identity** (Lemma 7),
$$f_{2b}\!\left(\tfrac{4}{7}, \delta\right) - \tfrac{9}{16} \;=\; \frac{12\,(\delta - 9/8)^2}{7\,(4\delta - 1)} \;>\; 0,$$
so $F(\delta) \ge f_{2b}^{\max}(\delta) \ge f_{2b}(4/7, \delta) > 9/16$.

The witness $\eta = 4/7$ lies in the Case 2b interval for $\delta < (41 + 7\sqrt{37})/66 \approx 1.266$, covering all of $(1, 5/4]$.

**Structural insights (not load-bearing but explanatory).**

- *Why $\delta = 9/8$?* Lemma 4 gives $\partial f_{2b}/\partial \eta|_{\eta=1/2} = -(\delta^2 + 6\delta - 8)/\delta$, vanishing at $\delta_{\mathrm{crit}} = -3 + \sqrt{17} \approx 1.12311$. The FPS choice $\delta = 9/8 = 1.125$ sits just $0.002$ above this threshold — just inside the regime where FPS's monotonicity-in-$\eta$ argument for Case 2b is valid. (Their proof structure requires this; the witness identity does not.)
- *Why $\eta = 4/7$?* Remark 9 explains: at $\delta = 9/8$, $P(s, 9/8) = -s(4s - 1)^2/8$ has two roots in $s = \alpha = 2 - 1/\eta$, namely $s = 0$ (FPS's $\eta = 1/2$) and $s = 1/4$ ($\eta = 4/7$). The factorisation $P(1/4, \delta) = 12(\delta - 9/8)^2$ shows the second root persists as a strict-inequality witness for every $\delta \ne 9/8$.
- *The cubic remnant.* The "naive" optimisation (assuming $f_{2b}^{\max} = \delta/2$ at every $\delta$ — false in general) gives the irreducible cubic $\delta^3 + 3\delta^2 - \delta - 4 = 0$ with root $\delta_1 = -1 + (4/\sqrt{3})\cos((1/3)\arccos(3\sqrt{3}/16)) \approx 1.114907$. Since $\delta_1 < \delta_{\mathrm{crit}}$, the assumption fails precisely at the cubic root, and $\delta_1$ is not the optimum.

**Implications (§7).** Three concrete routes to beat $9/16$:
1. Replace Vizing–Gupta with Goldberg–Seymour / Kahn-type bounds on the fractional chromatic index of the auxiliary multigraph $H$.
2. Sharpen the multiplicity bound from $\mu(H) = o(k)$ to $\mu(H) \le (m + o(1))k$ with explicit $m < 1$.
3. Modify the semi-random construction.

## 2. `tighter_fps_RETRACTED.tex` / `tighter_fps_RETRACTED.pdf` (retracted, 8 pages)

**Status.** **RETRACTED 2026-05-16.** Retraction banner at the top of the document.

**The error.** The original draft claimed $F^\star \approx 0.5574 < 9/16$ at $\delta_1 \approx 1.114907$. The proof of Lemma 6 (Case 2b) silently assumed FPS's monotonicity-in-$\eta$ claim holds for every $\delta$, when in fact it transitions at $\delta_{\mathrm{crit}} = -3 + \sqrt{17}$. At $\delta_1$, the true $f_{2b}^{\max}(\delta_1) \approx 0.5654$, so $F(\delta_1) > F(9/8) = 9/16$.

**Why the file is preserved.** The cubic factorisation, the Cardano closed form, the FPS sign-typo check, and the Proposition 3.4 robustness check (D6) are all still mathematically correct. The retracted PDF is a self-contained record of how the error was discovered.

## Where the math lives

- `../D3_R5a_reconstruction.md` — faithful reconstruction of FPS Claim 3.7.
- `../D5_sympy_freedelta/freedelta.py` — *original* SymPy script with the silent-assumption bug noted at line ~165.
- `../D5_sympy_freedelta/case2b_check.py` — the corrected check that uncovered the error: $df_{2b}/d\eta|_{\eta=1/2}$ factors as $-(\delta^2 + 6\delta - 8)/\delta$, vanishing at $-3 + \sqrt{17}$.
- `../D5_sympy_freedelta/witness.py` — the SymPy script verifying the witness identity $f_{2b}(4/7, \delta) - 9/16 = 3(8\delta - 9)^2/[112(4\delta - 1)]$.
- `../D5_sympy_freedelta/D6_prop34_check.md` — Proposition 3.4 robustness check; still mathematically correct, no longer load-bearing for any positive result.

## R5a status (per `../../work/01_principal_lead/INTEGRATION.md`)

**Closed.** Outcome (ii): $c = 9/16$ binding. **Theorem-grade sharpness note shipped.** Any improvement of Lemma 2.3 requires a different attack (§7 routes).

## Suggested next steps

1. **Email FPS** with the note. The witness identity may interest them as a clean way to state the sharpness of their constant.
2. **Author list.** Decide on co-authors before posting.
3. **Journal target.** *Discrete Mathematics* "Note" section or *Electronic Journal of Combinatorics* short paper. The note is now self-contained, 7 pages, with an elementary proof — a good fit for either venue.

## Reproducibility

- `pdflatex sharpness_9_8.tex` × 2 (one pass for refs). No errors, no undefined references, no overfull boxes.
- Witness identity: `uv run ../D5_sympy_freedelta/witness.py`.
- Case 2b monotonicity-transition: `uv run ../D5_sympy_freedelta/case2b_check.py`.
- SymPy 1.14, TeX Live 2024.
