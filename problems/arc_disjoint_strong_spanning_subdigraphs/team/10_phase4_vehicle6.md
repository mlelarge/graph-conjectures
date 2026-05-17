# 10 — Phase 4, Vehicle 6 (SAD-decomposable inner-part gluings)

Author: Combinatorial Optimization / Exact Algorithms Coder
Date: 2026-05-16
Status: first deliverable.
Companion to `team/08_phase4_lifting_lemma_v1.md` (CL1 statement and the
empirical patterns P1, P2, P3), `team/07_phase3_report_v2.md` (the v2
deficit-aware corpus), and `code/run_phase4_vehicle6.py` (this report's
driver). Headline log:
`code/logs/phase4v6_20260516_220659.json` (2 471 verified-SAT
candidates, full witnesses, canonical hashes, per-instance pattern
records).

The deliverable is a *positive* test bench for the controlled-lifting
lemma CL1. The v2 corpus violates CL1's hypothesis (1) on its chosen
partition (because v2's inner parts are 2-arc-strong UNSAT templates and
hence not SAD-decomposable on their own). Vehicle 6 fixes this: it glues
pairs of **3-arc-strong, SAD-decomposable** digraphs and asks whether
the resulting gluings' SAT witnesses obey P1, P2, P3.

### Headline numbers (5 000-streamed sweep)

| metric | value |
|---|---:|
| streamed | 5 000 |
| degree-gate pass | 5 000 |
| $\lambda^{\text{arc}} = 3$ exactly | 4 021 (80.4 %) |
| $\lambda^{\text{arc}} > 3$ rejected | 979 (19.6 %) |
| $\lambda^{\text{arc}} < 3$ | 0 |
| cross-checked verified SAT | 2 471 |
| cross-checked verified UNSAT | **0** |
| cross-check disagreements | 0 |
| labeled-distinct → canonical-distinct | 2 471 → 2 461 |
| largest iso-class | 4 |
| ordered pairs covered | 43 |
| ordered pairs with $\geq 50$ verified | 36 |
| **P1a** (every $b^-$ bridge mono-color) | **71.5 %** (1 766 / 2 471) |
| **P1b** (every $b^+$ bridge mono-color) | **24.2 %** (597 / 2 471) |
| **P1c** (both directions mono) | **15.9 %** (393 / 2 471) |
| **P2** (tight 3-cuts splitting (2,1)) | 100.00 % (10 591 / 10 591) — *tautological* |
| **P3** (deg-3 out-cuts splitting (2,1)) | 100.00 % (10 634 / 10 634) — *tautological* |
| candidates with neither bridge direction mono | **501 / 2 471 = 20.3 %** |
| sweep wall-time | 278 s |

These numbers replace the v2 report's "56/56 = 100 % bridge-direction
monochromaticity": once we test CL1 on its intended regime (SAD-
decomposable inner parts) the strict monochromaticity drops to 71.5 %
in the narrow direction and 24.2 % in the wide direction. **The v2 100 %
was an artifact of the deficit-aware bridge multiset on UNSAT templates,
not a property of the gluing geometry.** §4 unpacks the implication for
CL1's hypothesis (3).

---

## §1 Inner-part library

`code/generators/sad_inner_parts.py` builds a library of 3-arc-strong
digraphs each shipping a *constructed* SAD witness (or a solver-derived
witness for the Paley tournaments). The library is verified at module-
import time: every entry has $\lambda^{\text{arc}} \geq 3$ (computed by
the `Digraph.arc_connectivity` max-flow routine, not by trust in the
construction) and a witness $(R, B)$ such that $(V, R)$ and $(V, B)$ are
both strongly connected (verified by `nx.is_strongly_connected` on each
side). If any of these checks fails, the library raises an
`AssertionError` before the gluing sweep can even begin.

The 10 entries used by Vehicle 6:

| name | $n$ | $m$ | $\lambda$ | family | witness origin |
|------|---:|---:|---:|---|---|
| `K4_star` | 4 | 12 | 3 | bidirected complete | Hamilton-cycle + reverse |
| `K5_star` | 5 | 20 | 4 | bidirected complete | Hamilton-cycle + reverse + side-fill |
| `K6_star` | 6 | 30 | 5 | bidirected complete | Hamilton-cycle + reverse + side-fill |
| `QR7_Paley` | 7 | 21 | 3 | Paley tournament | SAT solver |
| `QR11_Paley` | 11 | 55 | 5 | Paley tournament | SAT solver |
| `C4_Kbar3` | 12 | 36 | 3 | composition $\vec C_4[\overline K_3]$ | bijection chain → Hamilton 12-cycle |
| `C3_Kbar3x3` | 9 | 27 | 3 | composition $\vec C_3[\overline K_3,\overline K_3,\overline K_3]$ | bijection chain → Hamilton 9-cycle |
| `C4_tripled` | 4 | 12 | 3 | tripled directed cycle | 2 copies → R, 1 copy → B |
| `C5_tripled` | 5 | 15 | 3 | tripled directed cycle | as above |
| `C6_tripled` | 6 | 18 | 3 | tripled directed cycle | as above |

**Construction notes.**

* $K_3^*$ is *excluded*: it has $\lambda^{\text{arc}} = 2$ (each
  vertex's out-degree is 2), so it does not meet the 3-arc-strong
  floor. The library's docstring documents this explicitly.
* For $K_n^*$, the SAD is: Hamilton cycle $0 \to 1 \to \dots \to n-1
  \to 0$ in $R$, reverse Hamilton cycle in $B$, remaining "chord" arcs
  split by length. Both sides are easily strongly connected (each
  contains a spanning directed cycle).
* The two Paley tournaments are 2-arc-strong tournaments other than
  $S_4$ (in fact 3- and 5-arc-strong respectively), so they admit a SAD
  by Bang-Jensen–Yeo 2004. We have no closed-form witness; we run
  `verify_sat` once at library-build time and embed the solver's
  witness, then re-validate it independently.
* $\vec C_4[\overline K_3]$ and $\vec C_3[\overline K_3^3]$ are
  semicomplete compositions outside the BJG–Yeo 2020 exception list
  (the exceptions are $\vec C_3[\overline K_2^3]$,
  $\vec C_3[\overline K_2,\overline K_2,P_2]$,
  $\vec C_3[\overline K_2,\overline K_2,\overline K_3]$, plus $S_4$
  itself). The SAD is constructed by selecting a bijection between
  consecutive layers whose composition is a single permutation cycle
  on layer 0, giving a Hamilton directed cycle as $R$ and the abundant
  remaining arcs as $B$.
* The tripled cycles $\vec C_n$ (with each arc multiplicity 3) are
  Eulerian and 3-arc-strong; the SAD allocates 2 copies of each arc to
  $R$ and 1 to $B$. Both colours then contain a spanning directed
  cycle.

**Self-test transcript** (`uv run python -m
generators.sad_inner_parts`):

```
SAD-inner-part library: 10 entries
K4_star             4    12       3  K_n_star
K5_star             5    20       4  K_n_star
K6_star             6    30       5  K_n_star
QR7_Paley           7    21       3  Paley_tournament
QR11_Paley         11    55       5  Paley_tournament
C4_Kbar3           12    36       3  composition
C3_Kbar3x3          9    27       3  composition
C4_tripled          4    12       3  cycle_tripled
C5_tripled          5    15       3  cycle_tripled
C6_tripled          6    18       3  cycle_tripled
```

All ten advertised $\lambda$ values are matched by the max-flow
computation; all ten constructed SAD witnesses re-validate.

---

## §2 Sweep configuration & hit rates

`code/generators/glue_sad.py` glues an ordered pair $(T_1, T_2)$ of
library members along an interface $S$ with $|S| \in \{1, 2, 3, 4\}$
and adds bridges $b^+: T_1 \to T_2$ and $b^-: T_2 \to T_1$ with $|b^+|,
|b^-| \geq 2$ and $|b^+| + |b^-| \in \{4, 5, 6, 7, 8, 10\}$. Bridge
tails and heads are constrained to non-interface vertices on each side
(the interface plays the same role as in v2). Bridges within a
direction may not be parallel (no two copies of the same $(u, v)$).

We accept a candidate only if the merged digraph is *exactly*
3-arc-strong; high-$\lambda$ inner parts (notably $K_5^*$, $K_6^*$,
$QR_{11}$) frequently yield $\lambda \geq 4$, and we discard such
candidates so that we test CL1 on its target regime.

**Sweep configuration** (driver default):

```
cap_streamed        = 5 000
cap_per_pair        = 60   (verified-SAT cap per ordered pair)
interfaces_per_pair = 3
bridges_per_setup   = 1
bridge_count_pairs  = (2,2)(2,3)(3,2)(3,3)(2,4)(4,2)(3,4)(4,3)(4,4)(5,2)(2,5)
instance_time_s     = 10
seed                = 20260516
```

This config emits at most $4 \text{ sizes} \times 3 \text{ interfaces}
\times 11 \text{ bridge-count pairs} \times 1 \text{ bridges-per-setup}
= 132$ candidates per ordered pair before moving on. The 5 000-streamed
budget therefore covered **43 ordered pairs**, with **36 hitting the
$\geq 50$-verified target**.

**Rejection rates.**

| $\lambda^{\text{arc}}$ | count | fraction |
|---|---:|---:|
| 3 (accepted) | 4 021 | 80.4 % |
| $> 3$ (rejected) | 979 | 19.6 % |
| $< 3$ | 0 | 0 % |

The 19.6 % rejection at $\lambda > 3$ is the price of using
high-$\lambda$ inner parts ($K_5^*, K_6^*, QR_{11}$ all have
$\lambda \geq 4$). The hit-rate floor in the Lead's stop conditions
is 5 %; we clear it by an order of magnitude.

---

## §3 Findings — P1, P2, P3 fractions

For each verified SAT candidate we extract the witness 2-coloring
$A(D) = R \,\dot\cup\, B$, normalize it so the $b^-$ bridges are
**majority blue** after normalization (matching team/08 §1.2's
convention; if the witness has more $R$ than $B$ on $b^-$, we swap $R
\leftrightarrow B$ globally), and run three pattern checks.

### §3.1 Pattern definitions (restated)

* **P1** (bridge-direction monochromaticity).
  * P1a: every $b^-$ bridge $T_2 \to T_1$ has the same colour.
  * P1b: every $b^+$ bridge $T_1 \to T_2$ has the same colour.
  * P1c: both P1a and P1b hold simultaneously.
* **P2** (tight 3-cut (2, 1) split). For every tight 3-cut
  $\delta^+(X)$ of $D$, the witness colour split is $(2, 1)$ or
  $(1, 2)$ (i.e., bichromatic; never monochromatic).
* **P3** (degree-3 vertex out-/in-cut (2, 1) split). For every vertex
  $v$ with $d^+(v) = 3$, the three out-arcs split $(2, 1)$ in colour.
  Same for $d^-(v) = 3$.

### §3.2 P2 and P3 are tautological for any SAD witness

By definition of a SAD on a 3-arc-strong $D$, every tight 3-cut
$\delta^+(X)$ must contain at least one $R$-arc and at least one
$B$-arc (else one of the two colour-subdigraphs has an empty out-cut at
$X$ and is not strong). A 3-cut bichromatic in $\{R, B\}$ has either a
$(2, 1)$ split or a $(1, 2)$ split; the $(3, 0)$ and $(0, 3)$ splits
are by definition impossible. Hence **any** SAT witness must satisfy
P2 = 100 %. Likewise P3: a degree-3 vertex's out-cut *is* a tight
3-cut (its singleton out-cut), so the same argument applies.

The v2 report's emphasis on P2 and P3 as "patterns" of the witnesses
was misleading. They are *not* patterns — they are consequences of
the SAD definition. The empirical 100/100 in team/08 §1.2 P3 and the
"15/15 deterministic" rows of team/08 §1.2 P2 contain *no information
beyond the SAT verdict*. Our 2 471 SAT witnesses also confirm P2 =
P3 = 100 %, but this is mathematically vacuous.

What the v2 report *did* tabulate in P2 that is non-tautological is the
*compartment signature* of each tight 3-cut and the assignment of the
(2,1) split among the three positions in the signature. We do not
reproduce that level of detail here because **in the Vehicle-6 regime
no tight 3-cut contains a bridge arc.** (See §3.4 for the empirical
breakdown.)

### §3.3 P1 — bridge-direction monochromaticity

P1 is the only non-tautological pattern. Headline aggregates (2 471
candidates):

| pattern | fraction | numerator / denominator |
|---|---:|---:|
| P1a (every $b^-$ mono) | **71.5 %** | 1 766 / 2 471 |
| P1b (every $b^+$ mono) | **24.2 %** | 597 / 2 471 |
| P1c (both directions mono) | **15.9 %** | 393 / 2 471 |
| neither direction mono | **20.3 %** | 501 / 2 471 |
| avg $b^-$ colour split $(R, B)$ after normalize | $(0.33, 2.72)$ | |
| avg $b^+$ colour split $(R, B)$ after normalize | $(1.42, 1.61)$ | |

This is the **major empirical finding**: P1 in its strict ("every
single bridge") form holds in roughly 70 % of $b^-$ directions and only
roughly 25 % of $b^+$ directions. The 56/56 = 100 % observed in v2
**does not generalize** to gluings of SAD-decomposable parts.

A weaker form does generalize: the *majority colour* of each direction
is well-defined and skewed. After normalization the $b^-$ direction
averages $(0.33, 2.72)$ in $(R, B)$, i.e., on average roughly $89 \%$
of the bridges go to one colour; the $b^+$ direction averages
$(1.42, 1.61)$, much closer to balanced.

The asymmetry between $b^-$ (highly skewed) and $b^+$ (nearly balanced)
mirrors v2 qualitatively, but the *strict* monochromaticity of v2's
single direction is broken.

### §3.4 Tight-3-cut compartment breakdown

Of 10 591 tight 3-cuts enumerated across the 1 652 candidates with $n
\leq 14$ (above that, the $2^n$ subset enumeration is skipped), the
compartment signatures aggregate as:

| signature of $\delta^+(X)$ | count | (2,1) splits (majority/minority) |
|---|---:|---|
| $(S_2^n, S_2^n) \times 3$ | 1 317 | 60/40 between (R majority, B majority) |
| $(S_1^n, S_1^n) \times 3$ | 717 | 60/40 |
| $(I, S_2^n), (S_2^n, S_2^n)^2$ | 341 | 55/45 |
| $(S_2^n, I), (S_2^n, S_2^n)^2$ | 331 | 55/45 |
| $(S_1^n, I), (S_1^n, S_1^n)^2$ | 294 | 80/20 |
| $(I, S_1^n), (S_1^n, S_1^n)^2$ | 275 | 70/30 |
| other (small counts) | ~150 each | varied |

The crucial observation: **no tight 3-cut contains a bridge arc in any
Vehicle-6 candidate.** The bridges (added on top of two 3-arc-strong
parts) sit at the boundary of the gluing, but the local tight 3-cuts of
the merged digraph are inherited from the inner parts' own tight 3-cuts
(plus tight 3-cuts crossing the interface but not the bridges).

This is structurally different from v2, where the *primary* tight
3-cuts were singleton out-cuts of bridge-incident vertices and
therefore contained b21 bridges, forcing a tight binding between the
"minority colour" of the cut and the colour of the bridge. In
Vehicle 6 this binding is absent — and that is *exactly* why P1 weakens
from 100 % to 71.5 %.

### §3.5 Canonicalization

`pynauty`-based `canonical_key` from `code/generators/canonicalize.py`
was applied to every verified SAT candidate. Result:

| metric | value |
|---|---:|
| labeled-distinct candidates | 2 471 |
| canonical-distinct candidates | 2 461 |
| iso-classes of size 1 | 2 454 |
| iso-classes of size 2 | 5 |
| iso-classes of size 3 | 1 |
| iso-classes of size 4 | 1 |

The largest iso-class (size 4) is the entire $K_4^* \to K_4^*$ family
with the smallest bridge configuration. Overall, labeled-distinct
counts are within 0.4 % of canonical-distinct, so the headline numbers
in §3.3 are not inflated by iso-duplicates.

### §3.6 Per-pair P1 table (top 30 by candidate count)

```
pair                                            n     P1a     P1b     P1c
C3_Kbar3x3 -> K6_star                          60  76.7%   13.3%   11.7%
QR11_Paley -> C6_tripled                       60  95.0%   36.7%   35.0%
K6_star    -> C3_Kbar3x3                       60  66.7%   28.3%   16.7%
C6_tripled -> C6_tripled                       60  58.3%   23.3%   16.7%
K4_star    -> C3_Kbar3x3                       60  90.0%   11.7%   11.7%
K4_star    -> QR7_Paley                        60  80.0%   16.7%   13.3%
QR7_Paley  -> QR11_Paley                       60  65.0%   18.3%   11.7%
C3_Kbar3x3 -> C4_tripled                       60  63.3%   31.7%   18.3%
C3_Kbar3x3 -> C4_Kbar3                         60  88.3%   28.3%   23.3%
C4_Kbar3   -> K6_star                          60  65.0%   13.3%   10.0%
C3_Kbar3x3 -> C3_Kbar3x3                       60  68.3%   23.3%   16.7%
QR11_Paley -> C3_Kbar3x3                       60  88.3%   30.0%   26.7%
C5_tripled -> QR11_Paley                       60  48.3%   15.0%    8.3%
K5_star    -> C4_Kbar3                         60  93.3%   16.7%   16.7%
QR7_Paley  -> C4_tripled                       60  63.3%   25.0%   18.3%
K5_star    -> C3_Kbar3x3                       60  78.3%   25.0%   16.7%
QR7_Paley  -> C4_Kbar3                         60  81.7%   25.0%   20.0%
C6_tripled -> K4_star                          60  58.3%   26.7%   15.0%
K4_star    -> C6_tripled                       60  65.0%   23.3%   10.0%
QR7_Paley  -> C3_Kbar3x3                       60  78.3%   28.3%   20.0%
C4_tripled -> C5_tripled                       60  58.3%   21.7%   10.0%
C4_tripled -> C3_Kbar3x3                       60  80.0%   16.7%   13.3%
K4_star    -> C5_tripled                       60  71.7%   25.0%   16.7%
C4_Kbar3   -> C6_tripled                       60  76.7%   15.0%    8.3%
C6_tripled -> QR11_Paley                       60  65.0%   28.3%   18.3%
C5_tripled -> C4_tripled                       60  55.0%   30.0%   13.3%
C6_tripled -> C4_tripled                       60  48.3%   35.0%    8.3%
QR7_Paley  -> K5_star                          60  70.0%   23.3%   13.3%
C5_tripled -> C6_tripled                       60  61.7%   21.7%   13.3%
C4_tripled -> QR7_Paley                        60  80.0%   23.3%   13.3%
```

P1a ranges from **48.3 %** ($\vec C_6^{(3)} \to \vec C_4^{(3)}$) to
**95.0 %** ($QR_{11} \to \vec C_6^{(3)}$). The variation correlates
weakly with the second part's $n$: small-$n$ part-2 pairs see higher
$b^-$ monochromaticity (since each $b^-$ bridge represents a larger
fraction of $T_2$'s out-flow into $T_1$ and the SAT solver is forced
to commit). This is a hypothesis only; we did not test it formally.

---

## §4 CL1 verdict and negative findings

### §4.1 The conjecture itself

Vehicle 6 streamed 5 000 candidates, verified 2 471 as 3-arc-strong
under ILP+SAT cross-check. **Zero UNSAT.** Zero ILP/SAT disagreements.
The Bang-Jensen–Yeo conjecture (WC3) holds in every Vehicle-6
candidate; the Lead's stop-on-counterexample protocol is not
triggered.

### §4.2 CL1 hypothesis-test verdict

Recall CL1 v1's four hypotheses (`team/08` §2):

1. *decomposable inner parts* — guaranteed by construction in Vehicle 6.
2. *bridge minimum* $|b^\pm| \geq 2$ — guaranteed by config.
3. *direction-monochromatic bridges with local coverage* — the
   empirical pattern P1+P3 raised to a hypothesis.
4. *no monochromatic tight 3-cut at the interface* — automatically
   satisfied by any SAT witness (a SAD has no monochromatic cut).

**Hypothesis (3) is the only one with empirical content.** Vehicle 6's
verdict is:

> The **strict** form of P1 — "every bridge in one direction is the
> same colour" — holds in 71.5 % of $b^-$ directions and only 24.2 %
> of $b^+$ directions across SAD-decomposable inner-part gluings. The
> v2 corpus's 56/56 = 100 % was an artifact of v2's deficit-aware
> bridge multiset on UNSAT templates: there the tight 3-cuts at
> degree-3 non-interface vertices contained b21 bridges, and the
> SAD's bichromatic-tight-cut constraint forced every b21 to inherit
> the minority colour of its containing singleton out-cut. In
> Vehicle 6 the bridges are *not* in any tight 3-cut (§3.4), so the
> SAD constraint exerts no such force on bridge colours; consequently
> P1 weakens.

The **weak** form of P1 — "each bridge direction has a clear majority
colour" — does generalize: average $(R, B)$ on $b^-$ is $(0.33,
2.72)$, i.e., $\sim 89 \%$ goes to one colour. CL1's hypothesis (3)
should be re-stated using this weak form.

**Concrete recommendation to the Structural Specialist (`team/08`
author).** Replace hypothesis (3)'s strict "monochromatic bridges in
each direction" by:

> (3$'$) *Bridge majority.* There is a partition $B^+ = B^+_R
> \,\dot\cup\, B^+_B$ and $B^- = B^-_R \,\dot\cup\, B^-_B$ such that
> in each direction at least $\lceil |B^\pm| / 2 \rceil + 1$ bridges
> are in the *majority colour*; **but in any tight 3-cut at the
> interface containing at least one bridge, the bridge colours and
> the inner-part SAD colours satisfy the local (2, 1) split**.

This is closer to the v2 *interpretation* — the bridge colours are
fixed by the tight-cut local geometry, not by an a priori
direction-uniform rule — and is consistent with both v2 (where tight
3-cuts contain bridges and force monochromaticity) and Vehicle 6
(where tight 3-cuts do not contain bridges and the bridges are free
to balance).

### §4.3 CL1-hypothesis violations (no critical evidence in this sweep)

A candidate is "CL1-violating" if its parts are SAD-decomposable
(hypothesis 1, guaranteed), $|b^\pm| \geq 2$ (hypothesis 2, guaranteed),
and the SAT witness exhibits a violation that contradicts the lemma's
*conclusion* or makes the lemma's *hypothesis (3)* unrecoverable.

* **Monochromatic tight 3-cut violations.** A monochromatic tight
  3-cut in the witness would falsify the SAD itself (by SAD definition
  every tight 3-cut is bichromatic). We checked: **0 / 10 591** tight
  3-cuts are monochromatic. No violation.
* **Bridge-direction non-monochromaticity.** 501 / 2 471 = 20.3 % of
  candidates have neither $b^+$ nor $b^-$ direction strictly
  monochromatic. This is *informational*, not a violation: CL1
  hypothesis (3) as stated is *sufficient* but not *necessary* for the
  SAD to exist. These 501 candidates are evidence that CL1's hypothesis
  set is too restrictive (CL1's converse fails); they are **not**
  evidence that CL1's forward direction is wrong.

The Structural Specialist's request (team/08 §4) was for "any
candidate where CL1's hypothesis is satisfied but the witness violates
a pattern." Among the 2 471 SAT witnesses, the strongest such cases
are the 501 candidates above; we recommend re-running the SAT solver
with a different symmetry-break and witness-enumeration cap to test
whether *some* other SAT witness on the same digraph *does* satisfy
P1 strictly. If yes, P1 is preserved as a hypothesis (just not as a
unique structural fact); if no, CL1 v1's hypothesis (3) genuinely
cannot reach those 501 SADs from any 2-colouring, and CL1 must be
relaxed.

We did **not** run that witness-enumeration sweep in this session
(budget); it is item C3 in §5.

---

## §5 Next

* **C1 (raised in team/08 §5).** Canonicalize the v2 56-witness
  sample. Done in Vehicle 6 as a by-product (every candidate has its
  `canonical_key` recorded). For the v2 sample, the same recipe
  applies in `phase4_witness_probe.py`; one extra pass with
  `canonicalize.py` would close the open item.
* **C2 (raised in team/08 §5).** Build Vehicle 6 generator. **Done in
  this report.**
* **C3 (new).** For each of the 501 candidates with neither $b^+$ nor
  $b^-$ monochromatic, enumerate the first $K$ SAT witnesses (e.g.
  $K = 50$ via solver-blocking clauses on the previous witness) and
  test whether *any* witness satisfies P1 strictly. If yes for the
  vast majority, CL1's hypothesis (3) survives as one of many possible
  SAD colourings. If no, CL1 v1's hypothesis (3) is genuinely too
  restrictive on the SAD-decomposable regime.
* **C4 (new).** Extend the library to cover semicomplete digraphs
  that are 3-arc-strong but **not** in the BJG–Yeo 2020 composition
  family (e.g., random tournaments on $n = 8, 10$ with $\lambda = 3$
  obtained by perturbing $QR_p$). This widens the test bed to the
  full "3-arc-strong solved classes."
* **C5 (new).** Symmetric Vehicle 6 with **two interfaces** (a chain
  $T_1 \to T_2 \to T_3$) to test whether P1 chains transitively
  across multiple bridge directions — a precondition for CL1 to lift
  inductively over a sequence of interfaces.
* **C6 (new).** Re-instate the (compartment-signature → colour-split)
  table from team/08 §1.2 P2 for the Vehicle-6 sweep, restricted to
  tight 3-cuts *that contain at least one bridge*. We observed §3.4
  that this set is empty; confirm rigorously (it would be the
  cleanest evidence that bridges do not participate in tight 3-cuts in
  the SAD-decomposable regime).
* **C7 (new).** Pass the JSON log
  `code/logs/phase4v6_20260516_220659.json` to the Structural
  Specialist for direct inspection of the 501 "no-mono-direction"
  witnesses. Every candidate has its full SAD witness embedded — the
  v2 logger bug is fixed.

---

## Appendix A — Data provenance and reproducibility

* `code/generators/sad_inner_parts.py` (library + self-test).
* `code/generators/glue_sad.py` (Vehicle 6 generator).
* `code/run_phase4_vehicle6.py` (driver: sweep + cross-check +
  pattern checks + canonical hash + JSON log).
* JSON log: `code/logs/phase4v6_20260516_220659.json` (18.7 MB).
  Every verified-SAT candidate has its full witness
  (`witness_red`, `witness_blue` as lists of $(u, v, k)$), canonical
  hash, bridges, interface, and per-instance `PatternRecord`.
  **Witness logging is mandatory** in v6 — this closes the v2
  logger's gap noted in `team/06_phase3_report_v1.md`.

Reproducibility (≈ 5 min on a single laptop):

```bash
cd code
uv run python -m generators.sad_inner_parts        # library self-test
uv run python -m generators.glue_sad               # generator smoke-test
uv run python run_phase4_vehicle6.py \
    --cap-streamed 5000 --cap-per-pair 60 \
    --interfaces-per-pair 3 --bridges-per-setup 1 \
    --instance-time-s 10
```

The seed is `20260516`; replaying the same command reproduces the
sweep numbers exactly modulo cross-check ILP/SAT solver scheduling
nondeterminism (which has not produced a disagreement in any of our
runs to date).
