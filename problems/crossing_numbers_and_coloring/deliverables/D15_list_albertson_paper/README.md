# D15 — List-coloring Albertson up to chromatic number 18

## Artifact

- `list_albertson_le_18.tex` / `list_albertson_le_18.pdf` (9 pages compiled).

## Main theorem

> Let $G$ be a graph and let $t \le 18$ be an integer. If
> $\chi_\ell(G) \ge t$, then $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$.

This is strictly stronger than the corresponding unconditional case
of Albertson's conjecture at $t \le 18$ (Ackerman 2019,
arXiv:1509.01932), since $\chi_\ell(G) \ge \chi(G)$ for every graph.
A DP-coloring corollary is included (same proof, replace list-Dirac
with DP-Dirac).

## Proof structure

The paper is essentially an "assembly" result: the
Albertson--Cranston--Fox~/ Bar\'at--T\'oth~/ Ackerman chain that
proves the ordinary Albertson conjecture at $t \le 18$ uses its
$\chi$-hypothesis only through

1. the Dirac minimum-degree bound on critical graphs
   ($\delta(G) \ge t - 1$), and
2. the resulting average edge floor
   ($|E(G)| \ge \tfrac{t-1}{2}|V(G)|$).

Both inputs lift verbatim to list-coloring via a one-line list-swap
argument (list-Dirac). The remaining ingredients in the chain --
the Pach--T\'oth and Ackerman Crossing-Lemma constants, the
four-crossings-per-edge bound $|E| \le 6|V| - 12$, and the
combinatorial bookkeeping reducing an MCE to $|V| \le 3.03 t$ --
are topological / geometric and reference no colouring whatsoever.

The list-Brooks theorem of Borodin (1977) and Erd\H{o}s--Rubin--Taylor
(1979) is stated for completeness but turns out not to be needed
on the critical path; we use only the average edge floor.

## Boundary: $t \le 18$ vs. $t \ge 19$

The threshold $t = 18$ is inherited from Ackerman. The recent
extension of Albertson to $t \le 24$ by Cranston (2025,
arXiv:2512.08020) uses the Fox--Pach--Suk chromatic-index lemma
(arXiv:2510.05893, Lemma 2.3) at the sharp constant $9/16$. The
list-edge-colouring analogue of that lemma at the same constant
is open; the best published list-edge-coloring bound is
Borodin--Kostochka--Woodall 1997 (JCTB 71, 184--204) with leading
constant $7/4$, which is a factor $\sim 3.1$ worse than $9/16$ and
collapses the Fox--Pach--Suk vertex bound far below the Ackerman
threshold. The paper includes a conditional Theorem~2 stating that
if the list-Fox--Pach--Suk constant matched the non-list one, the
same proof would give list-Albertson at $t \le 24$.

## Relationship to other deliverables

- **D8 (R5a, sharpness $9/8$)** — companion note proving that the
  Fox--Pach--Suk constant $9/16$ in their Lemma 2.3 is sharp within
  the Vizing--Gupta + semi-random framework. Cited from this paper
  as the structural reason that the list-side boundary at $t = 18$
  cannot be pushed by re-tuning the FPS parameter.
- **D13 (R2c attack memo)** — orthogonal track on bisection-width
  attacks on the chromatic-number side of Albertson. Independent.
- **D14 (R3.6 attack memo)** — the predecessor of this paper.
  Identifies the candidate theorem $T_1$ (list-Albertson at $t \le
  24$, conditional on the FPS list-edge-colouring lift) and the
  unconditional fallback $T_1'$ (list-Albertson at $t \le 18$).
  This paper writes up $T_1'$.

The D14 memo notes that list-Albertson at $t \le 18$ does **not**
close any of the Cranston residual triples $(25, 48), (26, 50),
(26, 51)$, which remain open under both the chromatic and the
list version of the conjecture.

## Compile / reproduce

```
cd deliverables/D15_list_albertson_paper
pdflatex -interaction=nonstopmode -halt-on-error list_albertson_le_18.tex
pdflatex -interaction=nonstopmode -halt-on-error list_albertson_le_18.tex
```

TeX Live 2024; only routine `hyperref` math-shift warnings about
PDF strings in section titles are emitted. No errors, no undefined
references, no overfull or underfull boxes.

## Status

**WITHDRAWN (2026-05-17).** The main theorem stated above is **false**
at $t = 5$: Voigt (1993) constructs a planar graph $G$ with
$\chi_\ell(G) = 5$ (planar graphs are $5$-choosable by Thomassen 1994,
and Voigt's example is not $4$-choosable) and $\operatorname{cr}(G) = 0
< 1 = \operatorname{cr}(K_5)$, directly refuting the theorem at $t = 5$.
The "lifts for free" argument is also structurally wrong independent of
the $t = 5$ failure: the ACF / BT / Ackerman chain does not use
$\chi \ge t$ only through $\delta \ge t - 1$ (Ackerman §3.1 invokes the
critical-graph edge-count function $f_r(n)$, whose list-coloring
analogue — Krivelevich 1997 — is provably weaker). See the withdrawal
banner at the top of `list_albertson_le_18.tex` (lines 33--60) for the
full retraction note. The paper must not be resurrected without a
fresh proof; the bundling paper D18 that wrapped this note as
"Observation 1" is similarly withdrawn.
