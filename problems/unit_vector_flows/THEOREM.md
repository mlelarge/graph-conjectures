# Computer-assisted theorem on $S^2$-flows

## Statement

> **Theorem.** *Every nontrivial snark on at most 28 vertices admits an
> $S^2$-flow.*

A *nontrivial snark* is a simple connected cubic graph that is
bridgeless, has girth at least 5, is cyclically 4-edge-connected, and
has chromatic index 4. An *$S^2$-flow* on a graph $G$ assigns to each
edge a unit vector in $\mathbb{R}^3$ so that, at every vertex, the
oriented sum of the incident vectors is zero (Kirchhoff conservation).

There are exactly **3 247** such graphs on at most 28 vertices, with
the per-order distribution

| $n$  | 10 | 18 | 20 | 22 | 24 | 26   | 28    | **total** |
|-----:|---:|---:|---:|---:|---:|-----:|------:|----------:|
| count | 1  | 2  | 6  | 20 | 38 | 280  | 2 900 | **3 247** |

(no snarks exist at $n \in \{11, 12, 13, 14, 15, 16, 17, 19, 21, 23,
25, 27\}$; the Petersen graph at $n = 10$ is the smallest snark).

For each one we exhibit a flow $\varphi : E(G) \to S^2 \subset
\mathbb{R}^3$ and provide an *independently replayable*
interval-Krawczyk certificate of its existence.

## Provenance

Enumeration matches the catalogue of Brinkmann, Goedgebeur, Hägglund,
and Markström, *Generation and properties of snarks*, J. Combinatorial
Theory Ser. B **103** (2013), 468–488. Concretely:

- $n \in \{10, 14, 16, 18, 20, 22, 24\}$: full enumeration of
  connected cubic graphs of girth $\geq 5$ via
  [nauty](https://users.cecs.anu.edu.au/~bdm/nauty/) 2.9.3
  `geng -d3 -D3 -c -tf -q n`; filtered to nontrivial snarks by a
  SAT-based 3-edge-colourability test (Glucose 4 via `python-sat`) and
  brute cyclic-4-edge-connectivity check in
  [scripts/catalogue.py](scripts/catalogue.py).
- $n = 26$: same pipeline, but each `geng res/mod` shard is streamed
  directly through the SAT filter
  ([scripts/sweep_higher_order.sh](scripts/sweep_higher_order.sh)) so
  the 1.5 GB raw catalogue is never materialised on disk.
- $n = 28$: direct generation via
  [snarkhunter](https://caagt.ugent.be/cubic/) (Brinkmann, Goedgebeur,
  McKay), which skips the chi-3 colouring step by integrating an
  even-2-factor lookahead into the canonical-orderly generation. Built
  locally against the same nauty install; CPU 1 453 s single-thread
  for 2 900 graphs. Not committed to the repo; reproduce via
  `external/snarkhunter-2.0b.zip` from the URL above plus
  `make 64bit CC=clang`.

## Certifier

For each graph $G$:

1. **Numerical witness.** Levenberg–Marquardt on the polynomial system
   of vertex Kirchhoff residuals + unit-norm constraints, with
   multi-seed retry to avoid saddle plateaus
   ([scripts/witness.py](scripts/witness.py)).
2. **Gauge fix + Newton refinement.** Rotate the witness into a pinning
   gauge that fixes the global $\mathrm{SO}(3)$ symmetry, then refine in
   `mpmath` at 50 decimal digits with a square pinned polynomial
   system over $\mathbb{Q}[s]/(s^2 - 3)$
   ([scripts/interval.py](scripts/interval.py)).
3. **Interval Krawczyk.** Build the interval box $[c - 10^{-5}, c +
   10^{-5}]$ around the refined centre and apply the Krawczyk operator
   $K(\mathbf{I}) = c - Y F(c) + (E - Y J(\mathbf{I}))(\mathbf{I} -
   c)$ entirely in `mpmath.iv` interval arithmetic, with $Y = J(c)^{-1}$
   computed at the same precision. If $K(\mathbf{I}) \subset
   \mathrm{int}(\mathbf{I})$ componentwise then $F$ has a unique real
   zero in $\mathbf{I}$ (Krawczyk's theorem), and the corresponding
   unit vectors are an $S^2$-flow on $G$.

Each certificate is a JSON document at schema version 2 with the
graph6 string, canonical edge order, pinning data, dropped redundant
vertex, free-variable list, polynomial-system SHA-256, decimal-string
centre, per-coordinate Krawczyk margins, and full provenance metadata.

## Replay

The cert is *replayable*: an independent verifier reconstructs the
polynomial system from the stored `graph6` string, recomputes the
Krawczyk operator using its own arithmetic, and demands

```
replay["ok"]  AND  verdict_matches_cert  AND  polynomial_hash_match.
```

To re-execute the entire verification end-to-end on a fresh clone:

```bash
git clone https://github.com/mlelarge/graph-conjectures.git
cd graph-conjectures/problems/unit_vector_flows
uv pip install --python ../../.venv/bin/python \
    networkx numpy scipy sympy mpmath python-sat pytest
make verify        # 41/41 regression tests, ~10 s
make verify-certs  # replay all 3247 certs, ~70 min sequential
```

Expected output: `3247/3247 certificates verified`.

## Manifest and integrity

| Item | Path | SHA-256 |
|---|---|---|
| Combined catalogue (3 247 g6 lines) | `data/catalogues/nontrivial_snarks_n10_to_28.g6` | `c31fb35b912c4ed6fe17755b2d8fdbe2b28c7982c99d9fda5b2cd24ad3af63af` |
| Manifest (per-order counts, generator commands, intermediate hashes) | `data/catalogues/nontrivial_snarks_n10_to_28.manifest.json` | (recompute from contents) |
| Certificate directory | `data/interval_certs/nontrivial_n10_to_28/` | `96494be0708f5908ed49b342bbbcf183ad98ccce50ff475c5fa6dafaa2149a9e` |
| Snarkhunter source archive (n=28 generator) | not committed; fetch from caagt.ugent.be | (upstream-managed) |

## Limitations

- The theorem is a finite statement about a specific class of
  reasonable size. It does not refute Jain's first conjecture (every
  bridgeless graph admits an $S^2$-flow) and does not prove it for any
  infinite family.
- The trust base of the proof includes: `nauty` and `snarkhunter` as
  enumerators; `mpmath.iv` for interval arithmetic; `sympy` for
  polynomial-system construction; the Krawczyk theorem itself (a
  standard result). A bug in any of these components could in
  principle invalidate the certificates; the cross-version replay
  protocol with `polynomial_hash_match` provides some defence, but is
  not a substitute for a formally verified pipeline.
- Two unsuccessful structural attempts on the flower-snark family
  $J_{2k+1}$ are recorded as a *negative* result in
  [docs/flower_snarks.md](docs/flower_snarks.md): the
  $\mathbb{Z}/(2n)$-equivariant ansatz is closed-form-obstructed
  (forces $u_b = 0$), and the relaxed $\mathbb{Z}/n$-equivariant
  ansatz admits no numerical solution for $n \in \{5, 7, 9, 11, 13\}$
  across 1 280 random initialisations.

## References

- K. Jain, *Unit vector flows*, Open Problem Garden, 2007 —
  http://www.openproblemgarden.org/op/unit_vector_flows
- H. Houdrouge, B. Miraftab, P. Morin, *2-dimensional unit vector
  flows*, arXiv:2602.21526, 2026.
- N. Ulyanov, *Graph Puzzles II.1: Counterexamples to Jain's Second
  Unit Vector Flows Conjecture*, arXiv:2603.23328, 2026.
- D. Mattiolo, G. Mazzuoccolo, J. Rajnik, G. Tabarelli, *Geometric
  description of $d$-dimensional flows of a graph*, arXiv:2510.19411,
  2025.
- G. Brinkmann, J. Goedgebeur, J. Hägglund, K. Markström, *Generation
  and properties of snarks*, J. Combin. Theory Ser. B **103** (2013),
  468–488.
- R. Krawczyk, *Newton-Algorithmen zur Bestimmung von Nullstellen mit
  Fehlerschranken*, Computing 4 (1969), 187–201.
