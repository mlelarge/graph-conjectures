# Jain's $S^2$-flow conjecture -- attack plan

## Headline

The Open Problem Garden entry contains two logically separate conjectures.
The finite-labeling conjecture is dead: Ulyanov (arXiv:2603.23328, submitted
2026-03-24) constructs finite point sets on $S^2$ that cannot be labeled by
$\{\pm1,\pm2,\pm3,\pm4\}$ under Jain's triple-sum rule. The live target is
Jain's $S^2$-flow conjecture:

> Every bridgeless graph admits a nowhere-zero flow with every edge value a
> unit vector in $\mathbb{R}^3$.

For disproof, the first serious hunting ground is cubic bridgeless graphs,
especially snarks. This is a search for an obstruction to a continuous
geometric flow, not for a new obstruction to ordinary integer 5-flows.

## Verified reductions and cautions

### Cubic reduction

Houdrouge--Miraftab--Morin give splitting/suppression rules showing that if
the reduced lower-degree/cubic graph has an $A$-flow, then the original graph
has an $A$-flow. Thus a minimal counterexample can be taken cubic in the usual
flow-theoretic sense after bridge exclusion and degree reductions.

This reduction is one-way as stated in their Lemma 6. Do not casually claim
that every non-cubic obstruction is equivalent to a cubic obstruction unless
the direction needed for minimal-counterexample transfer has been checked.

### Vertex geometry

At a cubic vertex, after orienting incident edges outward and absorbing signs
into the vectors, Kirchhoff conservation is

$$v_1+v_2+v_3=0,\qquad v_i\in S^2.$$

This is equivalent to the three vectors being coplanar with pairwise angle
$2\pi/3$; geometrically they are a 120-degree triple on a great circle. This
is Observation 9 in Houdrouge--Miraftab--Morin.

### 4-flow positives

Any cubic graph with a nowhere-zero 4-flow is a positive instance for
$S^2$-flows by the standard three-coordinate construction from three
$\mathbb{Z}_2$-flows. Hence the first plausible counterexamples are snarks:
bridgeless cubic graphs with no nowhere-zero 4-flow. For computational triage,
restrict further to the usual nontrivial snarks: simple, girth at least 5,
cyclically 4-edge-connected.

This is a search restriction, not a theorem that all non-snark cases are
irrelevant in every formulation.

## Phase 1 -- literature audit

Primary documents:

1. Houdrouge--Miraftab--Morin 2026, arXiv:2602.21526.
2. Ulyanov 2026, arXiv:2603.23328.
3. Mattiolo--Mazzuoccolo--Rajnik--Tabarelli 2023, arXiv:2304.14231.
4. Mattiolo--Mazzuoccolo--Rajnik--Tabarelli 2025, arXiv:2510.19411.

Deliverables:

- Transcribe the exact statement and proof dependencies of HMM Theorem 1
  (cubic graph has an $S^2$-flow iff it has an equiangular $S^2$-immersion).
- Extract all known positive families in HMM: Petersen, generalized Petersen
  variants, bipartite characterization for one/two image points, injection,
  and triangle blow-up closure.
- Audit whether HMM give any actual negative examples. Current evidence:
  none in the abstract or theorem list; they are building positive structure.
- Determine exactly what the rank/odd-coordinate-free theorem does and does
  not imply. It is a sufficient condition for an $S^2$-flow to yield a
  nowhere-zero 4-flow, not a general obstruction to $S^2$-flows on snarks.
- For MMRT 2025, record the precise cycle-double-cover hypotheses. Their
  oriented $d$-cycle double cover implications live in dimensions indexed by
  $d$; they do not by themselves give a cheap obstruction to $S^2$-flows.

## Phase 2 -- decision oracle

Implement `has_s2_flow(G) -> {True, False, Unknown}` for cubic graphs.

### Necessary algebraic formulation

Use edge vectors $x_e\in\mathbb{R}^3$ with constraints

$$\|x_e\|^2=1,\qquad \sum_{e\ni v}\sigma(v,e)x_e=0.$$

For $m$ edges and $n$ vertices, this gives $3n+m$ polynomial equations in
$3m$ real variables. For connected cubic graphs $m=3n/2$, so the naive count
is square: $3m=3n+m=9n/2$. But the vertex-conservation equations have three
global dependencies, one per coordinate, since every edge contributes once
with each sign. Thus before quotienting rotations the independent count is
$3m-3$ equations in $3m$ variables; after pinning the global
$\mathrm{SO}(3)$ symmetry, the algebraic problem should be treated as
generically rigid rather than overdetermined.

Better first reductions:

- fix an arbitrary orientation and absorb signs through $\sigma(v,e)$;
- quotient global $\mathrm{SO}(3)$ by pinning one vertex triple to
  $(1,0,0)$, $(-1/2,\sqrt3/2,0)$, $(-1/2,-\sqrt3/2,0)$;
- prefer Gram variables $g_{ef}=x_e\cdot x_f$ for certificate searches when
  possible;
- at every cubic vertex impose local Gram entries $g_{ef}=-1/2$ for incident
  pairs after sign normalization.

The goal is not just to solve equations; it is to produce certificates that
survive independent verification.

### Numerical witness engine

Build a nonlinear least-squares search minimizing

$$\sum_v \left\|\sum_{e\ni v}\sigma(v,e)x_e\right\|^2+
\lambda\sum_e(\|x_e\|^2-1)^2.$$

Use randomized restarts, global rotation pinning, and a hard residual threshold
such as $10^{-10}$ for storing a witness. A numerical witness proves existence
only after rational/algebraic reconstruction or robust interval verification.
Failure to converge proves nothing.

### Exact / certified routes

- Grobner basis or real quantifier elimination for small graphs.
- Sum-of-squares / SDP infeasibility certificates for larger graphs, with
  rationalized certificates when possible.
- Interval arithmetic around a numerical witness for positive certificates.
- Independent verifier that checks every stored witness or certificate without
  trusting the search code.

The SOS route is the best bet for a disproof certificate. The Grobner route
is likely to saturate quickly.

## Phase 3 -- regression suite

Before testing snarks, the oracle must pass known positives.

| Graph/family | Expected | Reason |
|---|---|---|
| Bipartite cubic graphs | True | $S^1$/$Z_3$ structure gives unit-vector flows in the cubic bipartite case |
| Cubic graphs with NZ 4-flow | True | three $\mathbb{Z}_2$-flow coordinate construction |
| Petersen graph | True | HMM explicitly give an equiangular $S^2$-immersion |
| HMM generalized Petersen variants | True | positive family from HMM |
| Triangle blow-ups of positives | True | HMM triangle blow-up closure |

Do not use Petersen as a negative calibration. It must return `True`.

## Phase 4 -- snark sweep

Search order:

| Family | Order | Purpose |
|---|---:|---|
| Petersen | 10 | positive sanity check |
| Blanusa snarks | 18 | first classical nontrivial snarks |
| Flower snarks $J_{2k+1}$ | 20--28 initially | structured Isaacs family |
| Loupekine / Goldberg snarks | 22--40 | classical benchmarks |
| cyclically 5-edge-connected snarks | up to 36 | catalogue sweep |
| generated snarks | 38--46 | snarkhunter / Brinkmann--Steffen frontier |

Bucket the sweep by graph family. Each bucket records:

- graph6 or sparse6 input;
- automorphism group size if available;
- numerical residual distribution over restarts;
- exact/SOS status;
- witness or certificate path;
- timeout and solver version.

A single certified `False` is a disproof. A numerical nonconvergence is only a
lead.

## Phase 5 -- alternate obstruction routes

### Rank obstruction

HMM Theorem 3 says an $S^2$-flow satisfying a rank at most 2 and
odd-coordinate-free condition yields a nowhere-zero 4-flow. For a snark, no
such flow can exist. Therefore, for a snark with an $S^2$-flow, every
$S^2$-flow must violate that rank/odd-coordinate-free hypothesis.

This can guide searches for "low-complexity" flows, but it is not an
obstruction to arbitrary $S^2$-flows.

### Cycle-double-cover route

MMRT 2025 proves equivalences and implications for geometrically constructed
$(r,d)$-flows from suitable cycle double covers. Treat this as a way to
construct positive flows or upper bounds, not as an immediate no-go criterion.

An obstruction would require proving that every $S^2$-flow induces one of
their suitable cycle-double-cover structures. That implication is not in the
abstract and must not be assumed.

### Finite point-set strengthening

Ulyanov's result kills the proposed global finite labeling map to
$\{\pm1,\ldots,\pm4\}$, but it does not kill $S^2$-flow existence. A viable
fallback is to formulate and disprove finite-image strengthenings:

- every snark has an $S^2$-flow using at most $N$ antipodal pairs;
- every snark has a flow from a prescribed symmetric finite subset of $S^2$;
- every $S^2$-flow can be deformed to one with algebraic coordinates of bounded
  degree.

These are secondary targets. They should not be confused with Jain's original
existence conjecture.

## Phase 6 -- exits

If every tested snark admits a certified $S^2$-flow:

- publish a search frontier with certificates;
- isolate structural operations preserving $S^2$-flows;
- try to prove the conjecture for named snark families;
- search higher-degree bridgeless graphs only if the cubic reduction audit
  reveals a genuine gap.

If a counterexample appears:

- independently verify it by at least two methods;
- minimize under edge/vertex reductions;
- produce a human-readable obstruction statement;
- archive graph, solver logs, certificate, and verifier.

## Immediate engineering tasks

1. Add graph import/export utilities for graph6/sparse6 and named snark
   constructors.
2. Implement the numerical witness search with rotation pinning.
3. Add regression tests for Petersen, and cubic NZ 4-flow positives.
4. Add a certificate schema for witnesses and infeasibility outputs.
5. Spike one exact backend on Petersen and Blanusa-sized instances.
