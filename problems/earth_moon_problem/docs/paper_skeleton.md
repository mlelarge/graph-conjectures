# Manuscript skeleton — Earth–Moon partial results

Working title and structure for a short note collecting the
computational and theoretical partials accumulated so far. Not a draft;
scaffolding only.

## Working title

> Computational exclusion of clique-blowup candidates for the Earth–Moon
> problem, and small-$n$ progress on the upper bound

(Or similar — alternatives: "On the chromatic number of biplanar graphs",
"Two refutations and one structural reduction for the Earth–Moon problem".)

## Abstract sketch (in keywords)

- Background: $\chi_{\rm EM}$, the Earth–Moon problem of Ringel, bounded
  $9 \le \chi_{\rm EM} \le 12$ since 1980, no improvement in 45+ years.
- Computational contribution: settle two new 19-vertex weighted clique
  blowups (a third 19-vertex case, KSS's $C_5[4,4,4,4,3]$, is
  reproduced as a calibration baseline) together with the 28-vertex
  headline $C_7[K_4]$ ($\chi = 10$, $\omega = 8$, $K_9$-free,
  edge-feasible) as non-biplanar via SAT-modulo-symmetry.
  Conclude: every blowup $C_{2r+1}[K_{a_1}, \dots]$ with $n \le 30$,
  $\omega \le 8$, $\chi \ge 10$, $|E| \le 6n - 12$ is non-biplanar.
- Theoretical contribution: any 12-critical $K_9$-free biplanar graph has
  $n \ge 89$ (Kostochka–Yancey 2014 + Kostochka–Yancey Brooks-type 2018 +
  Gould–Larsen–Postle 2022 Lemma 3.3 → every 12-Ore graph contains $K_{11}$,
  so $K_9$-freeness gives non-Ore, so Brooks-type applies; routine
  arithmetic gives the bound).
- Open: close $n \ge 89$ to prove $\chi_{\rm EM} \le 11$. Reduces to a
  bespoke discharging argument at $k = 12$, $K_9$-free; the existing
  literature (KS 2000 + Johansson, GP 2022 + Postle Conjecture) is
  shown to fall 30× short in explicit constants.

## Sections (proposed)

### 1. Introduction and statement of results

- History of $\chi_{\rm EM}$.
- Sulanke 1973 lower bound construction.
- KSS 2023 SMS framework (the directed-graph encoding for biplanarity).
- Our results, stated as Theorems A, B, C below.

### 2. Computational results

**Theorem A.** Every odd-cycle clique blowup $C_{2r+1}[K_{a_1}, \dots, K_{a_{2r+1}}]$
with $n = \sum a_i \le 30$, $\omega = \max_i (a_i + a_{i+1}) \le 8$,
$\chi \ge 10$, and $|E| \le 6n - 12$ is non-biplanar.

*Proof.* The constraints have exactly four canonical-form solutions:
$C_5[4,4,4,4,3]$, $C_5[3,3,5,3,5]$, $C_5[3,4,4,3,5]$, $C_7[K_4]$. Each
is verified non-biplanar by SAT-modulo-symmetry runs on the v1.0.0 SMS
pin, with full provenance recorded in
[`data/`](../data). $\square$

Sub-sub-sections:
- 2.1 The enumerator (cycle_blowup.py).
- 2.2 The SMS encoding wrapper (earthmoon_blowup.py).
- 2.3 Run details and certificates.
- 2.4 Discussion: KSS published candidate1 ($C_5[4,4,4,4,3]$); the other
  three are new.

### 3. Lower bound on a hypothetical counterexample's order

**Theorem B.** Any 12-critical $K_9$-free biplanar graph has at least
89 vertices.

*Proof.* Combine KY 2014 (Theorem 3) with KY 2018 (Theorem 6, the
Brooks-type result). Show: every 12-Ore graph contains $K_{11}$ via
GP 2022 Lemma 3.3 (since 12-Ore graphs have linearly many disjoint
$K_{11}$ subgraphs). So a $K_9$-free 12-critical graph is non-12-Ore;
Brooks-type then gives $|E| \ge \lceil(65n - 43)/11\rceil$, which
combined with biplanarity's $|E| \le 6n - 12$ forces $n \ge 89$. $\square$

### 4. Reduction of $\chi_{\rm EM} \le 11$ to a finite density problem

**Theorem C.** $\chi_{\rm EM} \le 11$ follows from the lemma: every
12-critical $K_9$-free graph $G$ on $n \ge 89$ vertices satisfies

$$|E(G)| \ge \lceil(65n - 43)/11\rceil + \lfloor (n - 88)/11 \rfloor.$$

Equivalently, $|E(G)| \ge 6n - 11$.

*Discussion.* The hypothetical counterexample at $n = 89$ has
$\rho_{12}(G) = 86 = y_{12}$ exactly, i.e. sits on the Brooks-type
bound; one extra edge of potential closes the upper bound.

### 5. Limits of the published asymptotic literature at $k = 12$

A short audit demonstrating that the natural attacks fail:

- Kostochka–Stiebitz 2000 + Johansson: requires Johansson constant
  $c_9 \le 0.2$, while modern bounds (Molloy 2019; Davies–Kang–Pirot–Sereni)
  give $c_9$ in the range 8–1800.
- Gould–Larsen–Postle 2022 + Postle Conjecture 1.6: open at $k = 12$
  (proved only at $k = 5, 6$ and $k \ge 33$); explicit
  $\varepsilon_{12}^{GP} \approx 0.00271$ vs the required
  $\varepsilon_{12} \ge 1/11 \approx 0.0909$, off by 30×.

This is essentially [`upper_bound_notes.md`](upper_bound_notes.md)
distilled to publication form.

### 6. Open problems

- The target lemma in Theorem C; suggest the Gallai-forest discharging
  attack of [`phase6_discharge_attempt.md`](phase6_discharge_attempt.md).
- Tighten by relaxing $K_9$-free to $K_t$-free for $t \in \{8, 7\}$;
  these encode richer 12-critical families but the framework should be
  the same.

## Appendices

- A. Reproducibility: SMS commit pin, patches, run-script invocations
  (extracted from [`spike_sms_build.md`](spike_sms_build.md) +
  [`docs/phase4_results.md`](phase4_results.md)).
- B. Computer-verifiable certificates: graph6 strings for each blowup,
  exit codes, solver statistics.

## Length target

10–15 pages. The computational part is fairly self-contained (1–2 pages
plus a results table). The lower-bound theorem and audit are short
arithmetic and citation. The bulk is the discussion of what remains and
why the standard asymptotic results don't close it — which is the
genuinely new contribution beyond the runs.

## Status

Skeleton only. Real writing should wait until either:
- the bespoke discharging argument either closes or shows specifically
  what extra ingredient is missing, OR
- enough time passes that the Phase 4 result alone (Theorem A) is
  worth publishing as a short computational note.
