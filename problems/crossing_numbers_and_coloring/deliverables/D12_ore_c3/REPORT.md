# D12 — C3 attempt on the 12 $(26, 51)$ Ore-corner graphs

**Date.** 2026-05-17.
**Input.** The 12 graphs from `../D4_ore_26_51/ore_26_51.g6` (Ore compositions $K_{26} * K_{26}$, all with $|V| = 51$, $|E| = 649$, $\delta = 25$, $\omega \ge 25$, $26$-critical).
**Goal.** Certify $\mathrm{cr}(G) \ge Z(26) = 5148$ for every $G$ in the family, giving a finite "no Ore counterexample at $(26, 51)$" result.
**Verdict.** **Insufficient.** With the lower bounds accessible without an exact MILP/SAT crossing-number solver, the best certified bound across the family is $\approx 3825$ from the Bungener–Kaufmann Crossing Lemma, well short of $Z(26) = 5148$ (gap $\approx 1323$).

## Per-graph results

See `lower_bounds.log` for the full table. All 12 graphs have the same $(n, m, \omega) = (51, 649, \ge 25)$, so the certified-bound values are identical up to the skewness heuristic.

| Bound | Value | Source | Certified? |
|---|---:|---|---|
| Euler $m - 3n + 6$ | $502$ | trivial | yes |
| Pach–Tóth $m^3 / (64 n^2)$ | $1642.15$ | Crossing Lemma, $m \ge 4n$ | yes |
| Bungener–Kaufmann $m^3 / (27.48 n^2)$ | $3824.52$ | Crossing Lemma, $m \ge 6.95 n$ | yes |
| $\mathrm{cr}(K_{12}) = 150$ | $150$ | $\omega \ge 25 > 12$, but proven $\mathrm{cr}(K_t)$ only for $t \le 12$ | yes |
| Greedy planarisation count | ~530 | heuristic; **not** a true lower bound on cr | no |

Best certified lower bound: $\max(502, 1642, 3825, 150) = 3825$.

Target: $Z(26) = 5148$.

Gap: $5148 - 3825 = 1323$, i.e., the certified bound is $\approx 74\%$ of the target. **0 / 12 graphs certified.**

## Why the easy bounds fall short

For Ore $G$ on $(n, m) = (51, 649)$, the BK Crossing Lemma gives the asymptotically-best generic-graph bound and dominates Euler / Pach–Tóth / clique-subgraph. The shortfall comes from the constant $1/27.48$ in the Crossing Lemma: it is sharp (or near-sharp) for *random* dense graphs, but specific dense graphs may have much larger crossing numbers. In particular, $\mathrm{cr}(K_{26}) \ge Z(26) = 5148$ (conjecturally) but the best *proven* finite lower bound on $\mathrm{cr}(K_{26})$ comes precisely from BK-style Crossing Lemma arguments, which give $\approx 5148 \cdot 0.74 \approx 3810$ — close to our $3825$ for the Ore family. This is no coincidence: $K_{26} \subseteq G$ would give a clean reduction (subgraph monotonicity), but the Ore composition has $\omega \ge 25$, not $\omega \ge 26$, so we lose one in the clique parameter.

## What would close the gap

Three options, in increasing order of effort:

1. **A finite certified lower bound on $\mathrm{cr}(K_{25})$ or $\mathrm{cr}(K_{26})$.** Since each Ore $G$ contains $K_{25}$ as a subgraph (the first $K_{26}$ minus its deleted edge contains $K_{25}$), $\mathrm{cr}(G) \ge \mathrm{cr}(K_{25})$. The conjectured value is $Z(25) = 4356$; a proven finite bound of $\ge Z(26) = 5148$ would *not* help via this route (it would have to exceed $Z(25)$, which would itself be a major result). The flag-algebra SDP machinery (de Klerk, Balogh–Lidický–Salazar) gives asymptotic constants only; rationalising them to finite small-$n$ certificates is a research project on its own.

2. **An exact MILP solve via Chimani–Mutzel / Buchheim–Chimani crossing-number ILP.** The state of the art for *exact* $\mathrm{cr}(G)$ is around $n \le 12$ for dense graphs; at $n = 51, m = 649$ this is essentially out of reach without months of dedicated solver work. The per-instance LP relaxation might yield a tighter lower bound than the Crossing Lemma but its tightness on dense graphs at this scale is unmeasured.

3. **A min-degree-aware Crossing Lemma improvement (R2c).** Each Ore graph has $\delta = 25 = t - 1$ — high minimum degree relative to $n$. The standard Crossing Lemma proof discards this; any improvement that uses $\delta(G) \ge t - 1$ would push the BK constant up. This is exactly the new Track B research target identified in the integration addendum.

## How the lower bounds were computed

`lower_bounds.py` loads the 12 graphs from D4's `ore_26_51.g6` and computes:

- **Euler bound:** $\mathrm{cr}(G) \ge m - 3n + 6$ when $G$ is non-planar simple.
- **Crossing Lemma** in three variants: Pach–Tóth ($c = 1/64$, $\alpha = 4$), Ackerman ($c = 1/29$, $\alpha = 6.95$), Bungener–Kaufmann ($c = 1/27.48$, $\alpha = 6.95$). The BK constant is the strongest *certified* generic constant in the literature; we use $\alpha = 6.95$ following the Cranston-cited form even though the BK abstract states $m > 6.77n$.
- **Clique-subgraph bound:** $\mathrm{cr}(G) \ge \mathrm{cr}(K_\omega)$, capped at $\mathrm{cr}(K_{12}) = 150$ since $\mathrm{cr}(K_t)$ is only proven for $t \le 12$.
- **Skewness greedy:** repeated planarisation; reported for context only because the count is not a true lower bound on $\mathrm{cr}(G)$ (a single edge can lie in many Kuratowski subgraphs, so the deletion count over-estimates $\mathrm{sk}(G)$).

`omega` is hardcoded as $25$ rather than computed via `networkx.find_cliques` (which is exponential on $K_{25}$-rich graphs and was the bottleneck of the initial run).

## Project-status implication

D12 is the immediate Track A target identified in the 2026-05-17 INTEGRATION addendum. The verdict is that the target as stated — *certified* $\mathrm{cr}(G) \ge Z(26)$ for all 12 — is **not reachable with off-the-shelf bounds**. Reaching it requires either (i) major investment in exact crossing-number solvers at $n = 51, m = 649$ (state-of-the-art research engineering), (ii) a sharper finite $\mathrm{cr}(K_t)$ bound for $t \in \{25, 26\}$ from SDP / flag-algebra work (Role 9), or (iii) the R2c min-degree-aware Crossing Lemma (Role 8), which is also the front-running Track B target.

**Recommendation.** Park D12 as a milestone awaiting either (ii) or (iii). The 12-graph artifact (D4) and this lower-bound analysis (D12) suffice to bound future work: any solver or new bound that can certify even one of the 12 produces a publishable partial Track A result.

## Reproducibility

- Environment: `uv venv` + `uv pip install networkx pynauty`.
- Run: `uv run lower_bounds.py`.
- Outputs: `lower_bounds.log` (full table).
- Tested with networkx 3.6.1 on macOS.
