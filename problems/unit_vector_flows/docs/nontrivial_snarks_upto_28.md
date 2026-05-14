# Theorem (computer-assisted)

> Every nontrivial snark on at most 28 vertices admits an
> $S^2$-flow.

## Statement

Let a *nontrivial snark* be a simple, cubic, bridgeless graph with girth
at least 5, cyclically 4-edge-connected, and chromatic index 4. There
are exactly 3 247 such graphs on at most 28 vertices, distributed by
order as 1 (Petersen, $n=10$), 2 (the Blanuša snarks, $n=18$), 6
($n=20$), 20 ($n=22$), 38 ($n=24$), 280 ($n=26$), and 2 900 ($n=28$).
For each one, we exhibit a flow $\varphi : E(G) \to S^2 \subset
\mathbb{R}^3$ with Kirchhoff's law at every vertex, and provide a
replayable interval-Krawczyk certificate of its existence.

These counts match the enumeration of Brinkmann, Goedgebeur, Hägglund,
and Markström, *Generation and properties of snarks*, J. Combinatorial
Theory Ser. B **103** (2013), 468–488.

## Computer assistance protocol

The proof is by enumeration plus interval verification:

1. **Enumeration.** For $n \in \{10, 14, 16, 18, 20, 22, 24, 26\}$, all
   connected cubic graphs of girth at least 5 are produced by Brendan
   McKay and Adolfo Piperno's `nauty` package, version 2.9.3, via
   `geng -d3 -D3 -c -tf -q n`. At $n = 26$ the enumeration is sharded
   across 8 `geng res/mod` parallel processes and streamed directly
   through the SAT filter via
   [scripts/sweep_higher_order.sh](../scripts/sweep_higher_order.sh);
   no raw 26-vertex catalogue is materialised on disk. **At $n = 28$**,
   the `geng + SAT` pipeline projected at multi-day wall time. We
   switch to `snarkhunter` (Brinkmann–Goedgebeur–McKay,
   `caagt.ugent.be/cubic/snarkhunter-2.0b.zip`, built locally against
   `libnautyL1.a` from the same nauty install). Snarkhunter generates
   nontrivial snarks directly via an even-2-factor lookahead during
   canonical-orderly generation, so no chi-3 filter is needed:

   ```bash
   external/snarkhunter-2.0b/snarkhunter-64 28 5 S s C4 o g \
       > data/catalogues/nontrivial_snarks_n28.g6
   ```

   Single-threaded CPU time at $n = 28$: 1 453 s (24 min), producing
   2 900 nontrivial snarks directly in graph6 format.
2. **Filtering.** [scripts/catalogue.py](../scripts/catalogue.py)
   classifies each graph and retains the nontrivial snarks. The
   chromatic-index test is a 3-edge-colour backtrack with girth-5
   pruning; the cyclic-edge-connectivity test enumerates all edge
   subsets of size at most 3 and verifies each leaves at most one
   component containing a cycle.
3. **Numerical witness.** For each nontrivial snark,
   [scripts/witness.py](../scripts/witness.py) finds a candidate flow
   by Levenberg–Marquardt on the polynomial Kirchhoff + unit-norm
   residual, with multi-seed retry to avoid saddle plateaus.
4. **Rigorous certification.** [scripts/interval.py](../scripts/interval.py)
   rotates the witness into a pinning gauge that fixes the global
   $\mathrm{SO}(3)$ symmetry, builds a *square* polynomial system over
   $\mathbb{Q}[s]/(s^2 - 3)$ by adjoining a symbol $s$ for $\sqrt{3}$,
   refines the candidate by Newton in `mpmath` at 50 decimal digits, and
   applies the Krawczyk operator on a box of half-width $10^{-5}$
   centred at the refined solution. The Krawczyk inclusion test runs
   entirely in `mpmath.iv` interval arithmetic. A componentwise strict
   inclusion certifies the existence of a unique real solution in the
   box. (See Krawczyk, *Newton-Algorithmen zur Bestimmung von Nullstellen
   mit Fehlerschranken*, 1969, and Rump, *Verification methods*, 2010.)
5. **Independent replay.**
   [scripts/verify_sweep.py](../scripts/verify_sweep.py) reads each
   stored certificate, reconstructs the polynomial system from the
   `graph6` string and pinning metadata, recomputes the Krawczyk
   inclusion from scratch, and demands `replay["ok"]` AND
   `verdict_matches_cert` AND `polynomial_hash_match` for the cert to
   be accepted.

## Reproduction

```bash
# fast path: rebuild the snark JSONL at orders 10..24 with stored cubic_g5 files
make catalogue
make sweep
make certs
make verify-certs

# n=26: stream geng output through the filter, 8 parallel shards
scripts/sweep_higher_order.sh 26

# n=28: direct snark generation via snarkhunter (10^3 faster than geng+SAT)
external/snarkhunter-2.0b/snarkhunter-64 28 5 S s C4 o g \
    > data/catalogues/nontrivial_snarks_n28.g6

# common sweep + interval + replay (parallel batches at n=28)
python scripts/sweep.py --from-catalogue data/catalogues/nontrivial_snarks_n28.g6 \
    --out data/sweep_results/nontrivial_n28 --restarts 200
python scripts/interval.py data/sweep_results/nontrivial_n28/*.json \
    --radius 1e-5 --dps 50 --out data/interval_certs/nontrivial_n28
python scripts/verify_sweep.py data/interval_certs/nontrivial_n28
```

Expected output: `3247/3247 certificates verified` for the combined frontier.

## Manifest and integrity

| Item | Path | SHA-256 |
|---|---|---|
| Combined catalogue (3 247 g6 lines) | [data/catalogues/nontrivial_snarks_n10_to_28.g6](../data/catalogues/nontrivial_snarks_n10_to_28.g6) | `c31fb35b912c4ed6fe17755b2d8fdbe2b28c7982c99d9fda5b2cd24ad3af63af` |
| Manifest | [data/catalogues/nontrivial_snarks_n10_to_28.manifest.json](../data/catalogues/nontrivial_snarks_n10_to_28.manifest.json) | (recomputable from contents) |
| Certificate directory hash | [data/interval_certs/nontrivial_n10_to_28/](../data/interval_certs/nontrivial_n10_to_28/) | `96494be0708f5908ed49b342bbbcf183ad98ccce50ff475c5fa6dafaa2149a9e` |

The manifest is the single source of truth for the enumeration: it
lists `geng` commands per order, the nauty version (2.9.3), per-order
counts, and the SHA-256 of every catalogue and intermediate file.

The 3-edge-colourability decision used in `scripts/catalogue.py` is
SAT-based (Glucose 4 via `python-sat`); this is essential at $n \geq 24$
because the naive backtrack search space ($3^m$, with $m = 39$ at
$n = 26$) is far larger than the time budget needed to certify
chromatic index 4 by exhaustion. At $n = 28$ even the SAT filter is
not the rate-limiting step — `geng` itself emits $\approx 7 \cdot 10^9$
girth-5 cubic graphs and `snarkhunter` skips that entirely via the
even-2-factor lookahead.

## Counts by order

| $n$ | enumeration | nontrivial snarks |
|---:|:---|---:|
| 10 | geng: 1 | 1 |
| 14 | geng: 9 | 0 |
| 16 | geng: 49 | 0 |
| 18 | geng: 455 | 2 |
| 20 | geng: 5 783 | 6 |
| 22 | geng: 90 938 | 20 |
| 24 | geng: 1 620 479 | 38 |
| 26 | geng (streamed) | 280 |
| 28 | snarkhunter (direct) | 2 900 |
| **Total** | | **3 247** |

(There are no snarks at $n \in \{11, 12, 13, 15, 17, 19, 21, 23, 25, 27\}$
because the smallest snark is the Petersen graph at $n = 10$ and snarks
have even order. The Petersen graph is the unique snark at $n = 10$;
on $n = 12, 14, 16$ no cubic, bridgeless, girth-5 graph fails to be
3-edge-colourable.)

The enumeration at $n = 24$ was generated by 8 parallel
`geng res/mod` shards summing to exactly 1 620 479; this matches the
counts of Brinkmann et al. (2013). At $n = 26$ the raw enumeration
would be a multi-gigabyte file, so the pipeline streams each shard's
output directly through the SAT filter via
[scripts/sweep_higher_order.sh](../scripts/sweep_higher_order.sh) and
keeps only the per-shard nontrivial-snark JSONL plus a `.done` marker
for resumability.

At $n = 28$ even the streaming `geng + SAT` pipeline was projected at
multi-day wall time. The switch to `snarkhunter` cut single-threaded
wall to 24 min (CPU 1 453 s). The 2 900 snark count matches Brinkmann
et al. exactly. Krawczyk certification was parallelised across 8
batches via `xargs` (≈ 70 min wall total for 2 900 graphs at
$m = 42$), and replay verification similarly.

## Pushing beyond $n = 24$

The same pipeline applies unchanged to higher orders; the binding cost
is the `geng -d3 -D3 -c -tf -q n` enumeration. Indicative wall times
on this machine (Apple Silicon):

- $n = 22$: 161 s for ≈90 938 girth-5 cubic graphs.
- $n = 24$: completed by 8 parallel `geng res/mod` shards, producing
  exactly 1 620 479 connected cubic girth-5 graphs and 38 nontrivial snarks.
- $n = 26$: expected to produce roughly 28 million connected cubic
  girth-5 graphs; at the observed sharded throughput this is an offline
  multi-hour run.

Pushing the theorem to $n = 26$ therefore requires either an offline
`geng` run (with `res/mod` sharding for parallelism) or swapping the
generator to `snarkhunter` (Brinkmann–Goedgebeur), which generates
snarks directly. The catalogue and certifier code are agnostic to the
generator: feed any graph6 catalogue through `scripts/sweep.py
--from-catalogue` and the rest of the pipeline runs unchanged.

## What this does and does not say

This theorem is a computer-assisted statement about a *finite* class.
It does not refute Jain's first conjecture (every bridgeless graph
admits an $S^2$-flow), nor does it prove it. It is a positive
existence result on the natural reduced frontier through 24 vertices,
delivered with provenance metadata and a replay path that an
independent verifier can re-execute end-to-end on any machine running
`mpmath`, `sympy`, `numpy`, and a current `nauty`.
