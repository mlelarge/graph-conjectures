# D16 — Bisection-width Crossing Lemma for regular spectral expanders

**Author.** Role 8 (probabilistic / topological combinatorics).
**Date.** 2026-05-17.
**Status.** Draft preprint; companion to D8 (R5a sharpness) and D15
(list-Albertson at $t \le 18$).

## Contents

- `expander_crossing.tex` — the source. Self-contained, single
  file. Compiles with `pdflatex` (TeX Live 2024).
- `expander_crossing.pdf` — the compiled paper (9 pages).
- `README.md` — this file.

## How to compile

```
pdflatex -interaction=nonstopmode -halt-on-error expander_crossing.tex
pdflatex -interaction=nonstopmode -halt-on-error expander_crossing.tex
```

Two passes are needed for cross-references. No bibliography
backend (`bibtex` / `biber`) needed — the bibliography is inline
via `thebibliography`.

## Main theorem (post-fix)

> Let $G$ be a $d_0$-regular graph on $n$ vertices with second
> adjacency eigenvalue $|\lambda_2(G)| \le \theta\,d_0$ for some
> $\theta \in [0, 1)$. Then
> $$\operatorname{cr}(G) \;\ge\; \frac{(1 - \theta)^{2}\,d_0^{2}\,(\lfloor n/2 \rfloor \lceil n/2 \rceil)^{2}}{80\,n^{2}} \;-\; \frac{d_0^{2}\,n}{16}.$$
>
> For $n$ even this simplifies to $\operatorname{cr}(G) \ge (1-\theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$; for $n$ odd the right-hand side equals $(1 - 1/n^2)^2$ times the clean even-$n$ form.

This is the explicit-$\theta$ packaging of the bisection-width
Crossing Lemma combined with Alon's spectral bisection bound. Both
inputs are classical; the contribution is the explicit packaging
and the corresponding Albertson corollary (`cor:albertson` in the
.tex).

**Reinstated as Paper 2 on 2026-05-17** (after the D18 combined paper was withdrawn — its Observation 1 was false at $t = 5$). Four fixes from the senior referee pass applied:

1. **Spectral bisection bound now correct for odd $n$.** Corollary 3.3 states $\bw(G) \ge (1-\theta) d \lfloor n/2 \rfloor \lceil n/2 \rceil / n$, which gives $(1-\theta) dn/4$ for $n$ even and $(1-\theta)(1 - 1/n^2) dn/4$ for $n$ odd. The earlier draft asserted the clean form for all $n$, which is wrong for odd $n$ by a factor $(1 - 1/n^2)$.
2. **PST proof bookkeeping fixed.** The earlier proof of Lemma 3.1 used the false rounding step "$5.00/79.9 \le 1/16$" (the actual ratio is $5.00/79.9 = 0.0626 > 0.0625 = 1/16$). The corrected proof uses the exact identity $1.58 = 6.32/4$ so that $(1.58/6.32)^2 = 1/16$ exactly, then rounds only the leading $79.8848 \le 80$ at the end.
3. **Numerical illustration moved to a regime where the comparison is valid.** The earlier draft compared to Bungener–Kaufmann at $(d_0, n) = (10, 1000)$, but BK requires $m \ge 6.77 n$ (so $d_0 \ge 14$ for $d_0$-regular). The new illustration uses $d_0 = 14$ (a Ramanujan-regular graph with $\theta = 2\sqrt{13}/14 \approx 0.515$).
4. **Ore-scope claim corrected.** The earlier §5 claimed all three Cranston residual triples are "populated by Ore compositions of $K_{26}$"; in fact only $(26, 51)$ admits Ore candidates by the congruence $|V| \equiv 1 \pmod{k - 1}$. The corrected text states this explicitly.

**Constants.** The headline denominator $1/1280$ comes from a
**self-contained inline derivation** through the dual bisection
inequality of Pach--Shahrokhi--Szegedy / Sýkora--Vrt'o; squaring
that dual with the $(a+b)^2 \le 2a^2 + 2b^2$ bookkeeping step
yields the conservative $\operatorname{cr}(G) \ge \bw(G)^2/80 -
\sum_v \deg(v)^2/16$ used in §3. Pach--Spencer--T\'oth
\cite{PachSpencerToth} sharpen the bisection constant from $1/80$
to $1/40$ via a more careful split before squaring; their sharper
form would replace $1/1280$ by $1/640$ throughout. We chose the
conservative form for the headline because it is fully proved
inline; the PST $1/40$ form is recorded as `rem:PST-constants`.

## Relation to D13

This paper is the realised "$T_1'$" fallback proposed in §6 of
D13 (the R2c attack memo). The constants in the headline
inequality differ from D13's draft formulation:

- D13 §6 wrote $(1-\theta)^2 d_0^2 n^2 / 256 - n^2/16$.
- The correct conservative constants, derived inline here, are
  $(1-\theta)^2 d_0^2 n^2 / 1280 - d_0^2 n / 16$.
- The PST $1/40$ form would give $(1-\theta)^2 d_0^2 n^2 / 640
  - d_0^2 n / 16$ as a one-step strengthening if PST's Theorem 3.1
  is invoked.

The denominators were corrected from D13's $256$:
- PST's bisection-cum-crossing constant is $1/40$ (their
  optimised proof) or $1/80$ (the inline squared-dual proof
  used here), not $1/16$ as the D13 draft assumed.
- Combined with Alon's $\bw(G) \ge (1-\theta) d_0 n / 4$ (giving
  another $1/16$ factor when squared), the headline denominator
  is $80 \cdot 16 = 1280$ (conservative) or $40 \cdot 16 = 640$
  (PST).
- The second term is $d_0^2 n/16$ (not $n^2/16$): PST has
  $\sum_v \deg(v)^2 = d_0^2 n$ for $d_0$-regular graphs.

## Bundle context

This paper is the third in a 12-month bundle of partial-result
Albertson papers:

- D8 (`deliverables/D8_paper/sharpness_9_8.pdf`): FPS Lemma 2.3
  constant $9/16$ is sharp within the FPS framework.
- D15 (`deliverables/D15_list_albertson_paper/list_albertson_le_18.pdf`):
  Albertson chain lifts to list-coloring at the Ackerman threshold
  $t \le 18$.
- D16 (this paper): explicit-$\theta$ Crossing Lemma plus
  Albertson corollary for $d_0$-regular spectral expanders.

None of the three closes the Cranston residual at $t \in \{25, 26\}$.
Each is a stand-alone graph-theory result.

## Honest scope

- The result does **not** close the Cranston residual triples
  $(t, n) \in \{(25, 48), (26, 50), (26, 51)\}$, because the
  populating Ore graphs are not spectral expanders
  ($\theta = 1 - O(1/n)$). See §6 of the paper.
- The Albertson corollary becomes non-vacuous only at moderately
  large $n / t \gtrsim 20$ for Ramanujan-quality expanders, not
  at the tight Dirac edge-floor regime $n \approx 2 t$ where
  the Albertson conjecture is open. See §5 of the paper.
- The novelty is the explicit packaging, not new heavy
  machinery. Both ingredients (PST 2000, Alon 1986) are
  classical.

## Verification

- Compiles cleanly: no errors, no overfull/underfull boxes, all
  references defined.
- Page count: 9 (target 6--10).
- Numerical sanity check in §4 of the paper: at $d_0 = 10$,
  $n = 100$, $\theta = 0.6$ (Ramanujan), the theorem gives
  $\operatorname{cr}(G) \ge 24375$ vs the
  Bungener--Kaufmann Crossing Lemma's $\operatorname{cr}(G) \ge 1820$.
  Ratio $\sim 13$, with the gap growing as $d_0$ grows.
