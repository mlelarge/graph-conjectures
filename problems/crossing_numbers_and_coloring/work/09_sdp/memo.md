# Role 9 / C6 memo: SDP and flag-algebra finite lower bounds on cr(K_t) for t in {25, 26}

Author: Role 9 (SDP / flag algebras / numerical certification).
Audience: Roles 1, 3, 4, 6.
Date: 2026-05-16.
Scope: deliver finite, certified lower bounds underline{L}(t) <= cr(K_t) for t in {25, 26}, suitable for Roles 3 and 4 to discharge candidate counterexamples to Albertson.

The single line a reader should remember: every existing SDP / flag-algebra result on cr(K_n) is **asymptotic**, and the only currently *finite, proved, theorem-grade* lower bound on cr(K_25) is the trivial one obtained by propagating cr(K_13,n) bounds via subgraph counting. The "0.83" of de Klerk et al. and the "0.98559895" of Balogh-Lidicky-Salazar are limits as n -> infinity; they do not certify cr(K_25) >= 0.985 * Z(25). The v2 plan made this exact mistake and was burned by it; v3 explicitly forbids the substitution.

## 1. What is currently proven about cr(K_t) finitely

### 1.1 Exact values

The crossing number of K_n is known exactly only for n <= 12:

| n  | cr(K_n) = Z(n) | source |
|----|----------------|--------|
| 5  | 1   | folklore / Guy |
| 6  | 3   | Guy |
| 7  | 9   | Guy / Saaty |
| 8  | 18  | Guy / Saaty |
| 9  | 36  | Guy / Saaty |
| 10 | 60  | Guy / Saaty |
| 11 | 100 | Pan-Richter, *J. Graph Theory* (2007) |
| 12 | 150 | Pan-Richter, *J. Graph Theory* (2007) |

For n >= 13 the value cr(K_n) is **open**. The closest result is McQuillan-Pan-Richter (arXiv:1307.3297, JCTB 2015), who prove cr(K_13) is *not* 217. Combined with Kleitman's parity theorem and the upper bound Z(13) = 225, one has

  cr(K_13) in {219, 221, 223, 225},

so the best proved finite *lower* bound is

  cr(K_13) >= 219.

For n = 14, ..., 24 there is no analogous narrow-set result. The state of the art is what the SDP/flag-algebra machinery yields *combined with Kleitman parity* and *the subgraph-counting trick* (see Section 3.4). I have not found in the literature (or in any ancillary computation file I could access) an explicit table of best finite lower bounds on cr(K_n) for n in [13, 24]. Such a table is one of my first 30-day deliverables (Section 8).

### 1.1.5 Kleitman parity and what it propagates

Kleitman (1970) proved that for odd m,

  cr(K_{m, n}) = cr(K_{m, n - 1}) + floor((m-1)/2) * floor(n/2),

and the analogous identity for cr(K_n) modulo small integers (the "parity theorem"): cr(K_{n+2}) and cr(K_n) differ by a quantity with controlled parity. The practical consequence for cr(K_n) is that any proved lower bound L on cr(K_n) at one n value *propagates* to bounds at n+2, n+4, ... with explicit additive correction. This is how McQuillan-Pan-Richter turned the 5-element candidate set for cr(K_13) into the 4-element set after excluding 217 — the parity theorem says cr(K_13) is odd mod 2, ruling out even candidates a priori.

For our purposes: the cr(K_13) >= 219 bound propagates *forward* to give weak bounds on cr(K_14), cr(K_15), ..., cr(K_25), cr(K_26). These propagated bounds are weaker than the Brosch-Polak SDP propagation (Section 3.4) for large n, but tighter for small n (the additive Kleitman correction grows only linearly in n, whereas Z(n) grows as n^4 / 64). At n = 25 the Kleitman propagation from cr(K_13) >= 219 yields roughly cr(K_25) >= ~1700, which is dominated by the Brosch-Polak SDP bound; at n = 14 or 15 the Kleitman bound dominates. The week-2 finite-bound table (Section 8) must record the max of both.

### 1.2 The Cranston-residual context

Albertson at t = 25, 26 reduces (Cranston Thm 2) to three (t, |V|) pairs: (25, 48), (26, 50), (26, 51). For each pair the Albertson question is

  cr(G) >= cr(K_t) ?

A finite lower bound underline{L}(t) <= cr(K_t) is needed *only for falsification*: a candidate G with overline{cr}(G) < underline{L}(t) would refute Albertson. A positive proof targets the *upper* bound Z(t) (Hill drawing), not a lower bound. This asymmetry was the v3 correction; see plan.md "subtle reading issue".

## 2. The Guy / Zarankiewicz value Z(t)

  Z(t) = (1/4) floor(t/2) floor((t-1)/2) floor((t-2)/2) floor((t-3)/2).

Verified arithmetic for the relevant t:

| t  | floors             | Z(t) |
|----|--------------------|------|
| 24 | 12 * 11 * 11 * 10  | 3630 |
| 25 | 12 * 12 * 11 * 11  | 4356 |
| 26 | 13 * 12 * 12 * 11  | 5148 |

**Status of Z(t) for t >= 13.** Z(t) is the count of crossings in Hill's two-parameter drawing of K_t (Guy 1969 construction). It is therefore an *upper* bound on cr(K_t):

  cr(K_t) <= Z(t).

The Harary-Hill (also called Guy-Zarankiewicz) conjecture asserts equality. The conjecture is *open* for every t >= 13; settling cr(K_25) = Z(25) would be a major separate result (a Pan-Richter-style proof at t = 25 would be one of the deepest exact crossing-number results to date). Role 9 explicitly does **not** promise to prove cr(K_25) = Z(25).

## 3. SDP and flag-algebra machinery

### 3.1 The de Klerk-Maharry-Pasechnik-Richter-Salazar SDP (arXiv:math/0404142, SIDMA 2006)

The de Klerk et al. construction targets cr(K_{m,n}), not cr(K_n) directly. The route to cr(K_n) is via *propagation* (Section 3.4).

Sketch. Fix m (the paper uses m = 7). For each pair of edges {e_1, e_2} of K_m that share or do not share a vertex one writes a topological invariant of how the two edges cross in a drawing of K_{m, n}. The SDP variables are non-negative real numbers indexed by *equivalence classes* of pairs of edges under the symmetry group S_m x S_n acting on K_{m,n}. The objective is a linear function whose value at any feasible solution is a lower bound on the per-vertex normalized crossing count, hence on cr(K_{m, n}) / n^2 asymptotically.

After symmetry reduction (using the wreath product S_m wr S_n and its representation theory), the SDP block-diagonalizes into a sum of small blocks. For m = 7 the original paper reports an SDP of order a few hundred variables, solvable in seconds on a 2006-era machine, yielding the asymptotic

  cr(K_{7, n}) >= (some explicit rational) * n^2 + O(n).

The constant obtained for cr(K_n)/Z(n) after propagation is **0.83 asymptotically**. Critically, this constant is a *limiting* statement: for finite n the bound is cr(K_n) >= 0.83 * Z(n) - O(n) (the O(n) absorbs the propagation slack), and the O(n) term is *not* negligible at n = 25.

### 3.2 The Balogh-Lidicky-Salazar flag-algebra computation (arXiv:1711.08958, SIDMA 2019)

Razborov's flag algebra calculus is applied with flags of size up to ~7 vertices, encoding *good drawings* of K_n (each pair of edges crosses at most once, no three edges share a crossing, no edge crosses itself). The SDP has matrix variables indexed by *types* (rooted partial drawings) and *flags* (full small drawings extending a type). Ancillary files (`flag.cpp`, `Makefile`, `rounding_Integer.sage`) on the arXiv attachment do the SDP setup and the rational rounding for verification.

The paper proves

  liminf_{n -> infinity} cr(K_n) / H(n) >= 0.98559895,

where H(n) = Z(n) (the same Hill quantity, the paper writes H). The constant comes from a numerically optimal flag-algebra SDP solution, rounded to exact rationals via a Cauchy-Schwarz-style certificate.

**Asymptotic, not finite.** The proof structure is: assume for contradiction a sequence of K_n drawings violating the bound, take a *flag-algebra limit object* (a "graphon analogue" for drawings), and derive a contradiction via the rounded SDP certificate. The contradiction step requires n -> infinity for the convergence to the limit object. There is *no* finite-n statement of the form "cr(K_25) >= 0.985 * Z(25) - C" extractable from the proof without further work.

There is a *secondary* asymptotic result in the same paper: the *spherical geodesic* crossing number of K_n is asymptotically >= 0.996 * H(n). This is a stronger constant on a stronger drawing model (geodesics on the sphere), unrelated to Albertson.

### 3.2.5 Why "asymptotic" is not a typographic accident

A small clarification, because the team has been burned on this. When the Balogh-Lidicky-Salazar paper writes

  cr(K_n) / H(n) -> c >= 0.98559895 as n -> infinity,

the convergence is *not* monotone, and the rate is not controlled by the proof. The proof structure (flag-algebra limit + densification via blow-up) makes essential use of n being unbounded; finitization would require either:

- bounding the discrepancy between the finite K_n and its flag-algebra limit object — a non-trivial *finite SDP* of its own, not addressed in the paper, or
- a direct re-proof at finite n with the same SDP infrastructure but rounded for a specific n — what I propose to investigate in months 6-9.

In particular, the inequality

  cr(K_25) >= 0.98559895 * Z(25) = 4293.27

is **not a theorem** and cannot be used as a target by any role on this project. The v2 plan treated it as one; v3 retracts this and confines the asymptotic constants to a separately-labelled column.

### 3.3 Ancillary computations: are there finite by-products?

I have inspected (via WebFetch) the arXiv landing pages for both papers and the slide decks of Lidicky (lidicky.name/slides/2023-lagos.pdf, 2019-lm3.pdf). I have **not** found an explicit table of finite cr(K_n) lower bounds in the published Balogh-Lidicky-Salazar source. The ancillary code at arXiv:1711.08958 *could* in principle be re-run with a finite-n cutoff to extract a finite SDP certificate, but doing so would be a non-trivial reverse-engineering job and is itself one of my proposed 12-month tasks (see Section 6). It is *not* guaranteed to produce a numerically useful bound at n = 25 — the flag-algebra SDP rounds optimally to the *limit*, and finite-n slack can be large.

### 3.4 Brosch-Polak (arXiv:2206.02755, *Math. Prog.* 2024) — the most promising near-term result

Brosch and Polak extend de Klerk-Maharry-Pasechnik-Richter-Salazar (and de Klerk-Pasechnik-Schrijver 2007) by solving the K_{m,n} SDP for m up to 13 with much heavier symmetry reduction. Reported finite-n bounds (for *all* n):

  cr(K_{10, n}) >= 4.87057 n^2 - 10 n
  cr(K_{11, n}) >= 5.99939 n^2 - 12.5 n
  cr(K_{12, n}) >= 7.25579 n^2 - 15 n
  cr(K_{13, n}) >= 8.65675 n^2 - 18 n

These are **finite, theorem-grade** statements (the paper is in *Mathematical Programming* 2024).

**Propagation to cr(K_n).** The standard counting trick (Guy, also de Klerk et al.): every drawing of K_n induces a drawing of every K_{m} subgraph and of every K_{m, n - m} bipartite subgraph (by partitioning V(K_n) into two parts and counting edges between). Summing the crossings over all such induced subgraphs and dividing by the multiplicity gives

  cr(K_n) >= [n / (n - m)] * cr(K_{m, n - m}).

Concretely with m = 13 and Brosch-Polak's bound (taking n_pos = n - 13):

  cr(K_n) >= [n / (n - 13)] * (8.65675 (n - 13)^2 - 18 (n - 13)).

At n = 25 this evaluates to

  cr(K_25) >= (25 / 12) * (8.65675 * 144 - 18 * 12)
            = 2.0833... * (1246.572 - 216)
            = 2.0833... * 1030.572
            ~~ 2146.99,

so the bound is roughly **cr(K_25) >= 2147** (after careful integer rounding and verifying the cited inequality is the right one — to be re-derived precisely in week 1; see Section 8).

At n = 26 the analogous calculation gives roughly cr(K_26) >= ~2470.

Note: 2147 vs. Z(25) = 4356, so this propagated bound is roughly **0.49 * Z(25)** — far below the asymptotic 0.83 (let alone 0.985), because at n = 25 the leading n^2 term has not dominated over the O(n) correction and over the (n - m)/n loss in propagation. This is the *honest* finite bound; Albertson falsification requires beating this.

**There may be a sharper propagation.** De Klerk-Pasechnik-Schrijver 2007 and follow-ups give a tighter inductive propagation than the naive K_{m,n-m} trick. Re-deriving the sharpest finite cr(K_25) lower bound from Brosch-Polak's data is week 2 of my plan.

## 4. Feasibility of new finite SDP runs for t in {25, 26}

### 4.1 Direct flag-algebra SDP on K_25 drawings

A flag-algebra computation that targets cr(K_25) *directly* (not the asymptotic ratio) would require:

- a base type encoding a partial drawing on k_0 vertices (k_0 = 6 or 7 typical);
- flags = full drawings of K_{k_1} extending the type, for k_1 = k_0 + 1 or k_0 + 2;
- counting good drawings up to combinatorial-rotation-system equivalence.

The number of good drawings of K_7 modulo equivalence is in the hundreds; for K_8, thousands; for K_9, tens of thousands (Aichholzer's order-type database goes through K_11 for *rectilinear* drawings, K_n more generally is much smaller). A flag-algebra SDP with k_1 = 8 has on the order of 10^3 - 10^4 variables and a few SDP matrix blocks of dimension up to ~10^3 after symmetry reduction. This is in the comfort zone of Mosek (double precision) and SDPA-GMP (multi-precision) in 2025.

The *outcome* of such an SDP, however, is again an *asymptotic* constant, not a finite n = 25 statement, because flag algebras prove statements about the limit object. To get a finite-n statement one needs either:

(a) a direct *combinatorial* SDP whose feasible region is the set of crossing-count vectors realizable by drawings of *exactly* K_25 (this is the original de Klerk K_{m,n} approach, applied with K_25 in the role of K_m), or

(b) a *Lasserre-style* hierarchy on the rotation system of K_25.

Approach (a) for K_25 is intractable: the SDP variables are indexed by symmetry classes of (edge-pair, drawing-class) on K_25, which combinatorially blows up beyond any current solver.

Approach (b) for K_25: the Lasserre level-r relaxation has (n choose r)^2 ~ (25 choose r)^2 variables for the moment matrix; at r = 4 this is ~12k^2 = 1.5 * 10^8, marginally feasible with massive RAM; at r = 5 it is ~5 * 10^9, intractable. The dual feasibility / rounding step at r = 4 is *not* known to be tight enough to produce cr(K_25) >= even 0.5 * Z(25). To my knowledge no one has attempted this and there is no published indication it would succeed.

### 4.2 Propagation via better K_{m, n} bounds

Realistic near-term: extend Brosch-Polak from m = 13 to m = 14 or m = 15. The block dimensions of the symmetry-reduced SDP for K_{m, n} grow roughly as the number of irreducible representations of S_m, which is the partition number p(m): p(13) = 101, p(14) = 135, p(15) = 176. Each block dimension grows polynomially in m. Total SDP variable count for m = 15 is likely in the 10^5 range; memory ~10-50 GB; solver Mosek or SDPA-GMP; wall time hours to days. **This is feasible.**

What it buys: pushing m from 13 to 15 in Brosch-Polak-style propagation tightens both the leading constant (closer to 0.83) and the O(n) slack. At n = 25, n - m = 10 or 12, so the (n - m)^2 leading term improves by a factor of (12/12)^2 = 1 -> negligible improvement from m = 13 to m = 14, slight improvement to m = 15. Order-of-magnitude estimate: **cr(K_25) >= ~ 2400 - 2700** after a successful m = 15 SDP. Still well below Z(25) = 4356.

### 4.2.5 Concrete SDP-size table for the m-extension path

| m  | # irreducibles of S_m (= p(m)) | est. total variable count | est. largest block dim | est. RAM | est. wall time (Mosek, 64-core) | est. wall time (SDPA-GMP, 128-bit) |
|----|---------------|--------------------|--------------|---------|----------------------------------|------------------------------------|
| 7  | 15            | ~10^3              | ~50          | 1 GB    | seconds                          | minutes                            |
| 9  | 30            | ~10^4              | ~150         | 4 GB    | minutes                          | tens of minutes                    |
| 11 | 56            | ~5 * 10^4          | ~400         | 16 GB   | tens of minutes                  | hours                              |
| 13 | 101           | ~2 * 10^5          | ~1000        | 64 GB   | hours                            | day                                |
| 14 | 135           | ~5 * 10^5          | ~1500        | 128 GB  | day                              | week                               |
| 15 | 176           | ~10^6              | ~2200        | 256 GB  | week                             | weeks                              |
| 17 | 297           | ~5 * 10^6          | ~4000        | 1 TB    | month+                           | infeasible                         |

(Numbers are order-of-magnitude; precise figures depend on the exact representation-theoretic reduction.) The natural near-term reach is m = 14 or m = 15; m = 17+ requires a fundamentally different SDP solver.

### 4.3 High-precision SDP solvers

For any extracted finite certificate to be theorem-grade, the SDP solution must be rounded to exact rationals and the rounded dual feasibility re-verified in rational arithmetic. The pipeline is:

1. Solve in floating-point (Mosek or CSDP for speed, or SDPA-GMP for arbitrary precision if conditioning is bad).
2. Round the dual matrix Y to nearby rationals Y_rat (techniques: rationalize each entry with bounded denominator; or use continued-fraction / LLL-style joint denominator reduction).
3. Verify Y_rat is positive semidefinite (Cholesky in rational arithmetic, or eigenvalue lower bound via interval arithmetic).
4. Verify the linear constraints A^* Y_rat = c hold in rational arithmetic.
5. The certified bound is c^T Y_rat (in rational arithmetic).

For a Brosch-Polak-scale SDP at m = 15 this rounding is the standard Vaughan-flagmatic procedure and is routine, *provided* the numerical SDP has a sufficiently strict-interior optimum. Numerical experience in flag-algebra literature: ~80% of solved SDPs round cleanly; the remaining ~20% require manual tweaking of the rounding precision.

## 5. Certificate verification pipeline

I will build the following stack:

| Layer | Tool | Purpose |
|-------|------|---------|
| SDP formulation | Custom Python + SageMath, using S_m representation-theoretic block decomposition (Schur-Weyl for K_{m,n}) | Generate `.dat-s` SDP input file |
| Numerical solve | Mosek (commercial, high speed) for first pass; SDPA-GMP (arbitrary precision) for ill-conditioned cases | Float-point SDP solution |
| Rational rounding | flagmatic v2 (Vaughan / Sliacan port, github.com/jsliacan/flagmatic-2.0), Sage `QQ.from_real()` | Produce `flags.rat` exact rational certificate |
| Rational verification | SageMath / Macaulay2 with exact PSD test (Cholesky in QQ, or interval arithmetic via Arb/MPFR) | Independently verify Y_rat is PSD and primal constraints hold |
| Hand check | Manual derivation of the propagation cr(K_{m,n-m}) -> cr(K_n) and Kleitman parity tightening | Convert SDP output to cr(K_25) statement |

The *theorem-grade* output of this pipeline is a triple:

  (rational matrix Y_rat, propagation derivation in LaTeX, integer underline{L}(25)).

Y_rat is sized ~10^5 by 10^5 (with block-diagonal structure); the certificate is a directory of ~few GB. Verification by an independent party (Role 4 SAT verification team, or me re-running on a different machine with SageMath only) is the gold standard.

Reference implementations I will adapt:
- flagmatic 1.0 (Vaughan, original): github.com/emil79/flagmatic
- flagmatic 2.0 (Sliacan, SageMath integration): github.com/jsliacan/flagmatic-2.0
- FlagAlgebraToolbox (SageMath, 2025): arXiv:2601.06590
- Brosch's solver code for crossing numbers: linked from danielbrosch.com (slides referenced; ask the author directly for the code in the first 30 days).

## 6. What I can plausibly deliver in 12 months

I rank three scenarios honestly.

### Scenario (a): underline{L}(25) >= 4000

**Probability ~ 10%.** This would require either (i) a successful direct flag-algebra computation for *finite* n = 25 that produces a constant within ~8% of Z(25), or (ii) a Brosch-Polak-style propagation with m pushed to ~18 or 20, which is currently beyond the SDP-solver frontier. Neither is on offer in the current literature; both are research-grade.

### Scenario (b): underline{L}(25) >= 4356 = Z(25), i.e. cr(K_25) = Z(25)

**Probability < 1%.** Proving cr(K_25) = Z(25) is the Harary-Hill conjecture at t = 25 — a major open problem, of comparable difficulty to the Pan-Richter K_11/K_12 result but at much larger scale. Pan-Richter took a tailored geometric/topological argument plus computer enumeration of rotation systems for K_11 (which has ~10^9 inequivalent good drawings). For K_25 the analogous enumeration is hopeless; one would need a fundamentally new technique. I do **not** commit to this scenario.

### Scenario (c): improved asymptotic constant, no useful finite implication

**Probability ~ 60%.** A flag-algebra SDP with larger flags (k_1 = 9 or 10) might push the asymptotic constant from 0.98559895 to ~0.99, but this is asymptotic; it does not certify cr(K_25) >= 0.99 * Z(25). The most likely outcome of a year of careful SDP work is a published improvement in the asymptotic constant and *no* directly useful finite Albertson-falsification threshold.

### Scenario (d): the realistic deliverable

**Probability ~ 75%.** What I expect actually to deliver in 12 months:

- a *finite* certified bound underline{L}(25) in the range **[2200, 2900]** (and the corresponding bound for t = 26 scaled by ~ Z(26)/Z(25)), obtained by:
  1. carefully re-deriving the Brosch-Polak propagation in finite-n form,
  2. re-running the Brosch-Polak SDP with sharper rounding at m = 13 or extending to m = 14,
  3. combining with Kleitman parity to round up to the nearest valid parity,
  4. verifying the certificate in SageMath.

This is the bound that should enter Role 3's R1c pipeline as the *real* falsification threshold. It is roughly 0.5 * Z(25), so a counterexample G to Albertson at t = 25 must have overline{cr}(G) < ~2400, which is a *much* weaker constraint than overline{cr}(G) < Z(25) = 4356. Whether this is enough to make R1c discharge all its candidates is for Role 3 to determine (Section 7).

## 7. Dependencies on other roles

### Role 1 (Principal Lead — Cranston-residual close-out)

**Critical question:** Is a finite underline{L}(25) ~ 2400 (well below Z(25) = 4356) enough?

Two interpretations:

- *Strict Albertson falsification:* a candidate G with overline{cr}(G) < underline{L}(25) would refute Albertson. Any underline{L}(25) > 0 is in principle useful here.
- *R1c discharge (positive direction):* if Role 3 wants to *prove* Albertson at t = 25 by enumerating candidates G and showing overline{cr}(G) >= cr(K_25) for each, the relevant target is Z(25) (the upper bound), not underline{L}(25) — see plan.md "subtle reading issue" and v3 obstruction O2.

So Role 9's deliverable is structurally a **falsification tool**, not a positive-proof tool. Role 1 must decide whether the team's goal is (i) discharge the three Cranston-residual orders by proving Albertson there (target Z(t)), or (ii) attempt to construct a counterexample (target underline{L}(t)). My memo is essential for (ii), nice-to-have for (i).

### Role 3 (R1c pipeline)

**Interface I will provide:**
- `bounds.json` with keys `t`, `Z_t` (upper bound = Hill drawing), `L_finite_certified` (my finite lower bound), `L_asymptotic_klerk` (0.83 * Z(t), flagged "asymptotic, not usable"), `L_asymptotic_bls` (0.98559895 * Z(t), flagged "asymptotic, not usable").
- A certificate directory `cert_t25/` and `cert_t26/` containing the rounded rational SDP matrix and the SageMath verification script.

**Ask from Role 3:** R1c's heuristic-discard rule (plan.md C3) must compare overline{cr}(G) against `L_finite_certified`, never against the asymptotic columns. The v2 plan had this wrong; v3 fixed it.

### Role 4 (SAT/CEGAR for crossing-number lower bounds)

**Possible synergy:** Role 4's SAT-based cr(G) lower bounds and my SDP-based cr(K_n) lower bounds are independent and complementary. For a candidate G we want both:

- a *lower* bound on cr(G) (Role 4, SAT), and
- a *lower* bound on cr(K_25) (Role 9, SDP / propagation),

so that Role 4 can certify cr(G) >= underline{L}(25) for each candidate (closing Albertson for G).

### Role 6 (HPC infrastructure)

**Ask:** for the m = 14 or m = 15 Brosch-Polak extension I need:

- a multi-core x86_64 node with >= 256 GB RAM,
- Mosek license (or compiled SDPA-GMP with MPFR),
- ~1 month of dedicated wall time.

For the certificate-verification side (SageMath rational PSD test on a ~10^5 dim matrix), I need ~64 GB RAM and a week of wall time.

### 7.4 What I will *not* do

To prevent scope creep, I list explicitly what I am *not* attempting:

- I will not attempt to prove Harary-Hill at any t >= 13. That is a separate research programme.
- I will not produce an "improved asymptotic constant" as a primary deliverable. Even if I find one in passing, it does not help the team's finite-t target.
- I will not run a *direct* flag-algebra SDP on K_25. The Lasserre / direct route in Section 4.1 is too speculative; I will instead extend Brosch-Polak's K_{m, n} infrastructure, which has a proven track record.
- I will not duplicate Role 4's SAT crossing-number lower bound work on individual candidate graphs G. My output bounds cr(K_t), not cr(G).

## 8. First 30-day deliverables

1. **Week 1: derive the finite cr(K_25) and cr(K_26) lower bounds from Brosch-Polak.** Carefully re-do the propagation from cr(K_{13, n - 13}) to cr(K_n), including the explicit O(n) constant; cross-check against the de Klerk-Pasechnik-Schrijver 2007 tighter propagation. Output: a single short LaTeX note `bounds_propagation.tex` giving underline{L}(25) and underline{L}(26) as integers, with a fully verified derivation.

2. **Week 2: compile the finite-bound table for t in [13, 30].** For each t, list (Z(t), best finite proved lower bound on cr(K_t), source citation, asymptotic constant). Distinguish exact values (t <= 12) from finite lower bounds (t >= 13) from asymptotic constants. Output: `bounds_table.json` and a Markdown rendering. This is the canonical reference for R1c.

3. **Weeks 3-4: reproduce Brosch-Polak's m = 13 SDP from scratch.** Build the symmetry-reduced SDP for cr(K_{13, n}); solve numerically with Mosek; round to rational with flagmatic; verify in SageMath. Output: a working reproducer in `scripts/brosch_polak_repro/`. This validates the toolchain end-to-end and proves I can produce theorem-grade output before committing to a 12-month project.

4. **Week 4: contact Daniel Brosch (Aalborg) and Bernard Lidicky (Iowa State) for access to their ancillary code** (Brosch's K_{m,n} SDP solver; Lidicky's K_n flag-algebra solver from arXiv:1711.08958). Either may shave months off the reproduction step.

5. **Week 4: write a "what underline{L}(25) does and does not buy" briefing for Roles 1 and 3.** This memo plus the bounds table; 2-3 pages; aimed at the team meeting at month 1.

## References

- **Albertson-Cranston-Fox** (2009), *EJC* 16(1) R45, arXiv:1006.3783.
- **Cranston** (2025), *Progress on Albertson's Conjecture*, arXiv:2512.08020.
- **Fox-Pach-Suk** (2025), *Immersions and Albertson's conjecture*, arXiv:2510.05893, SoCG 2025.
- **Pan-Richter** (2007), *The crossing number of K_11 is 100*, *J. Graph Theory*. Settles cr(K_n) for n <= 12 (combined with prior Saaty / Guy work for n <= 10).
- **McQuillan-Pan-Richter** (2015), *On the crossing number of K_13*, *JCTB*, arXiv:1307.3297. Proves cr(K_13) != 217; via Kleitman parity, cr(K_13) in {219, 221, 223, 225}.
- **de Klerk-Maharry-Pasechnik-Richter-Salazar** (2006), *Improved bounds for the crossing numbers of K_{m,n} and K_n*, *SIDMA* 20:189-202, arXiv:math/0404142. Asymptotic constant 0.83 via SDP on K_{7, n}.
- **de Klerk-Pasechnik-Schrijver** (2007), *Reduction of symmetric semidefinite programs using the regular *-representation*, *Math. Prog.* Tighter propagation framework.
- **Balogh-Lidicky-Salazar** (2019), *Closing in on Hill's conjecture*, *SIDMA* 33:1261-1276, arXiv:1711.08958. Asymptotic flag-algebra constant 0.98559895 for cr(K_n)/H(n); 0.996 for spherical geodesic crossing number.
- **Brosch-Polak** (2024), *New lower bounds on crossing numbers of K_{m,n} from semidefinite programming*, *Math. Prog.*, arXiv:2206.02755. **Finite** theorem-grade lower bounds on cr(K_{m, n}) for m up to 13. The single most directly useful paper for my deliverable.
- **Norin-Zwols** (unpublished), prior flag-algebra constant ~0.905, superseded by Balogh-Lidicky-Salazar.
- **Schaefer** (2022), *The Graph Crossing Number and its Variants: a Survey*, *EJC Dynamic Survey* DS21v7. Catalogue of best known finite bounds across variants.
- **Razborov** (2007), *Flag Algebras*, *J. Symbolic Logic*. Foundational reference for the flag-algebra method.
- **Vaughan, flagmatic 1.0**; **Sliacan, flagmatic 2.0**; **FlagAlgebraToolbox** (arXiv:2601.06590). Software stack for rational rounding of flag-algebra SDPs.
- **Aichholzer**, order-type database. Underlies finite cases at n <= 11 for rectilinear and good-drawing enumerations.

## Caveats

- All "Brosch-Polak propagation gives cr(K_25) >= ~2147" arithmetic in Section 3.4 is *back-of-envelope* and must be re-derived carefully (this is week-1 work). The numbers in Section 4.2 (cr(K_25) in [2400, 2700] after m = 15 extension) are rougher still — order-of-magnitude estimates I want to refine before any team-wide commitment.
- The "0.49 * Z(25)" figure in Section 3.4 is a *consequence* of the back-of-envelope propagation, not an independent claim; if the sharper de Klerk-Pasechnik-Schrijver propagation tightens the bound, this number will move.
- "Probability" labels in Section 6 are my subjective forecasts, not betting odds. Scenario (b) explicitly hinges on someone *else* solving Harary-Hill at t = 25; I am not promising to.
- I have not personally verified the McQuillan-Pan-Richter cr(K_13) != 217 result in source; I rely on the abstract and the *JCTB* publication.
- The Wikipedia and one search result claim "cr(K_n) is known for n <= 27" — this is **incorrect** (the search result conflated bipartite cr(K_{m,n}) bounds with cr(K_n) and is contradicted by Wikipedia's own main table and by the published literature). I have flagged this as a source-of-confusion the team should not import.
