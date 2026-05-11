# Unit vector flows

Self-contained workstream attacking Jain's surviving unit-vector-flow
conjecture:

> Every bridgeless graph admits a flow whose nonzero edge values are unit
> vectors in $\mathbb{R}^3$, equivalently points of $S^2$.

The second conjecture in the Open Problem Garden entry, the proposed map
$q:S^2\to\{\pm1,\pm2,\pm3,\pm4\}$ compatible with antipodes and equidistant
great-circle triples, is no longer a live target: Ulyanov (2026) gives finite
counterexamples. This package focuses only on the surviving $S^2$-flow
existence conjecture.

## Goal

Either:

- **Disproof target.** Exhibit a bridgeless graph, preferably a cubic snark,
  with no $S^2$-flow, together with a reproducible algebraic or SOS certificate;
  or
- **Evidence / theorem target.** Push the certified search frontier and extract
  structural closure theorems or reductions from the cubic geometric
  characterization of Houdrouge--Miraftab--Morin.

## Status

Phases 1 (literature), 3 (regression), and 4 (small-snark sweep) complete.
Phase 2 has both a numerical oracle and a rigorous interval-Krawczyk certifier
on top of a Newton-refined pinned polynomial system. The sympy Gröbner
spike works only at toy size; the same square system is used as the negative
backend (a bridged cubic graph reduces to the unit ideal). See
[docs/plan.md](docs/plan.md).

**Headline result.** Every nontrivial snark up through 26 vertices in the
nauty `geng -d3 -D3 -tf` enumeration admits a replayable interval-Krawczyk
certificate of $S^2$-flow existence (347 graphs total).

| Order | Cubic girth-5 (geng) | Nontrivial snarks (χ′=4, cyc-λ ≥ 4) | Witness | Interval certified | Replay-verified |
|---:|---:|---:|---:|---:|---:|
| 10 | 1 | 1 | 1/1 | 1/1 | 1/1 |
| 14 | 9 | 0 | — | — | — |
| 16 | 49 | 0 | — | — | — |
| 18 | 455 | 2 | 2/2 | 2/2 | 2/2 |
| 20 | 5 783 | 6 | 6/6 | 6/6 | 6/6 |
| 22 | 90 938 | 20 | 20/20 | 20/20 | 20/20 |
| 24 | 1 620 479 | 38 | 38/38 | 38/38 | 38/38 |
| 26 | (streamed) | 280 | 280/280 | 280/280 | 280/280 |
| **Total** | | **347** | **347/347** | **347/347** | **347/347** |

The per-order counts match Brinkmann–Goedgebeur–Hägglund–Markström
(JCTB 2013). The certified count uses the *strict* nontrivial-snark
predicate (simple, cubic, bridgeless, girth ≥ 5, cyclically
4-edge-connected, χ′ = 4) implemented in
[scripts/catalogue.py](scripts/catalogue.py). The 3-edge-colourability
decision is SAT-based (Glucose 4 via `python-sat`); this is essential
at $n \geq 24$ because the backtrack search space ($3^m$) is too large
to certify chromatic index 4 by exhaustion. At $n = 26$,
[scripts/sweep_higher_order.sh](scripts/sweep_higher_order.sh)
streams each `geng res/mod` shard directly through the SAT filter,
so the raw catalogue (≈ 1.5 GB) is never materialised on disk;
only the 280 snark JSONL lines (≈ 100 KB) survive.

Each interval cert (schema v2) carries enough metadata for an independent
verifier to reconstruct the polynomial system from the graph6 string and
re-run the Krawczyk inclusion test from scratch; the verifier
[scripts/verify_sweep.py](scripts/verify_sweep.py) does exactly that via
[interval.replay_krawczyk](scripts/interval.py). All 67 certificates pass
a clean replay.

The negative-calibration test
([tests/test_negative_calibration.py](tests/test_negative_calibration.py))
confirms the pipeline rejects bridged cubic graphs: numerical search refuses
(rss ≥ 0.36) and sympy Gröbner produces the unit ideal in 0.03 s.

The frontier sweep is reproducible from the manifest at
[data/catalogues/nontrivial_snarks_n10_to_26.manifest.json](data/catalogues/nontrivial_snarks_n10_to_26.manifest.json),
which records the exact `nauty geng` commands per order, the nauty
version, every catalogue file's SHA-256, and a content hash of the
certificate directory. The verifier
[scripts/verify_sweep.py](scripts/verify_sweep.py) requires
``replay["ok"]`` AND ``verdict_matches_cert`` AND ``polynomial_hash_match``
for an interval cert to pass — pass ``--allow-hash-mismatch`` to relax
the hash check across SymPy versions.

The natural next mathematical step — a $\mathbb{Z}/n$- or
$\mathbb{Z}/(2n)$-equivariant closed-form construction for the flower
snarks — has been tried and rejected, with the analysis recorded in
[docs/flower_snarks.md](docs/flower_snarks.md). The full
$\mathbb{Z}/(2n)$ ansatz is closed-form-obstructed (it forces
$u_b = 0$ on the b-spoke orbit), and the relaxed $\mathbb{Z}/n$ ansatz
admits no numerical solution at $n \in \{5, 7, 9, 11, 13\}$
(800 random initialisations per order, residuals bounded below by
$\approx 0.22$). The flower snark family is positive numerically and
under interval Krawczyk, but a structural proof will need a less
symmetric construction (twisted equivariance, dihedral, or a
cycle-double-cover route per Mattiolo et al. 2025).

Interval certificates: [data/interval_certs/](data/interval_certs/);
catalogues: [data/catalogues/](data/catalogues/); numerical
sweep results: [data/sweep_results/](data/sweep_results/).

## Layout

```
docs/                 plan, literature notes, theorem/certificate notes
scripts/              graph generators, numerical oracle, algebraic/SOS hooks
data/                 snark catalogues, witnesses, infeasibility certificates
tests/                regression suite for known positive instances
Makefile              verification targets (see "Reproduction" below)
```

## Reproduction

### Setup

External requirements:

- Python 3.12+
- [nauty 2.9.3+](https://users.cecs.anu.edu.au/~bdm/nauty/) (Homebrew: `brew install nauty`) — only needed if you want to regenerate the cubic catalogues; the stored `data/catalogues/cubic_g5_n*.g6` files are sufficient for re-verification alone.

Python packages (use `uv` to honour the project's tooling preference):

```bash
# from the repository root, with the .venv already created at the repo level
uv pip install --python .venv/bin/python \
    networkx numpy scipy sympy mpmath python-sat pytest
```

### Verification (no regeneration)

The committed certificates are self-contained. The fast path is:

```bash
make -C problems/unit_vector_flows verify         # 41/41 tests
make -C problems/unit_vector_flows verify-certs   # 347/347 interval replays
```

`verify-certs` runs the independent replay in
[scripts/verify_sweep.py](scripts/verify_sweep.py), which reconstructs
each polynomial system from the certificate's `graph6` string, recomputes
the Krawczyk inclusion test in `mpmath.iv`, and requires `replay["ok"]`
AND `verdict_matches_cert` AND `polynomial_hash_match`. Expect ≈ 5 min
wall on a current laptop.

### Regeneration from scratch

To rebuild everything from `geng` upward (≈ 1 hour wall for n ≤ 24):

```bash
make -C problems/unit_vector_flows clean catalogue sweep certs verify-certs
```

Individual stages:

```bash
make -C problems/unit_vector_flows catalogue   # geng + SAT snark filter
make -C problems/unit_vector_flows sweep       # numerical witness sweep
make -C problems/unit_vector_flows certs       # Krawczyk interval certificates
```

## References

- H. Houdrouge, B. Miraftab, P. Morin, *2-dimensional unit vector flows*,
  arXiv:2602.21526, 2026.
- N. Ulyanov, *Graph Puzzles II.1: Counterexamples to Jain's Second Unit Vector
  Flows Conjecture*, arXiv:2603.23328, 2026.
- D. Mattiolo, G. Mazzuoccolo, J. Rajnik, G. Tabarelli, *On $d$-dimensional
  nowhere-zero $r$-flows on a graph*, arXiv:2304.14231, 2023.
- D. Mattiolo, G. Mazzuoccolo, J. Rajnik, G. Tabarelli, *Geometric description
  of $d$-dimensional flows of a graph*, arXiv:2510.19411, 2025.

Original problem record: <http://www.openproblemgarden.org/op/unit_vector_flows>.
