# 15 — V6-style empirical sweep on 3-arc-strong OLS digraphs

Author: Combinatorial Optimization / Exact Algorithms Coder
Date: 2026-05-16
Status: first deliverable for Route B (`team/13` §5 commits this file).
Companions: `team/10_phase4_vehicle6.md` (V6 generator + pattern checks
reused), `team/11_cl1_proof_v1.md` (CL1 final-form hypotheses),
`team/13_publishability_decision.md` (Route B target statement),
`code/generators/ols.py` (the OLS generator built for this report),
`code/run_route_b_ols.py` (the driver), and the headline log
`code/logs/route_b_ols_20260516_223612.json` (355 verified-SAT
candidates, full witnesses, canonical hashes, per-instance CL1
records).

The deliverable answers two questions from the Route B charter:

* (Q1) does the Route B theorem hold empirically — every 3-arc-strong
  out-locally-semicomplete (OLS) digraph admits a SAD?
* (Q2) is CL1 (final form, `team/11` §5.1) the operative lifting
  mechanism on Route B's class?

Verdicts in two lines:

* **Q1: YES on 355 verified SAT instances across 1 353 streamed
  candidates; zero UNSAT at $\lambda = 3$; zero ILP/SAT
  disagreements.**
* **Q2: NO, not via the naïve partition.** CL1's hypothesis (1) on the
  natural round-decomposition partition ($V_1 = C_1$ the anchor
  component, $V_2 = V \setminus V_1$) fails on **99.7 %** of the SAT
  sample (354 / 355): the remainder $V_2$ has $\lambda^{\text{arc}} = 0$
  for $p \geq 3$ because removing $C_1$ severs the round cycle. CL1's
  hypothesis (2) on the same partition holds **100 %** (355 / 355). The
  Route B theorem must therefore use either a different partition
  (e.g., $V_1 = C_1 \cup C_2$) or a different lifting scheme entirely.
  This is the central §4 diagnostic.

---

## §1 — Construction library

`code/generators/ols.py` (≈ 300 lines) builds three families of OLS
candidates. The OLS property — every $v$'s out-neighbourhood
$N^+(v)$ induces a semicomplete digraph — is verified by an
independent function `is_out_locally_semicomplete(D)` *after*
construction. Per the spec hard rule, the construction is **never
trusted** to imply OLS-ness; the empirical confirmation rate is
**1 353 / 1 353 = 100 %** (OLS-confirmation passes for every streamed
candidate in the production sweep, including the random
rejection-sampled instances).

### §1.1 Component shape catalog

The Construction-A enumerator uses these 7 semicomplete component
shapes (filtered from a larger catalog by an independent
`is_semicomplete` check):

| shape | $n$ | description |
|------|---:|---|
| `pt` | 1 | singleton |
| `K2*` | 2 | bidirected $K_2^*$ |
| `C3` | 3 | $\vec C_3$ |
| `K3*` | 3 | bidirected $K_3^*$ |
| `K4*` | 4 | bidirected $K_4^*$ |
| `S4` | 4 | $\vec C_4^{(2)} = S_4$, the BJG–Yeo 2020 exception |
| `QR7` | 7 | Paley tournament on 7 vertices |

`vec C_4` is **excluded** from the catalog because it is *not*
semicomplete (non-adjacent pairs $(0, 2)$ and $(1, 3)$). The catalog
filter runs `is_semicomplete` at module import; only passing shapes
are used.

### §1.2 Construction A — Round decompositions

Round digraph on components $C_1, \ldots, C_p$ ($p \geq 2$): every
vertex of $C_i$ dominates every vertex of $C_{i+1}$ (mod $p$). The
resulting digraph is OLS by construction (each vertex's
out-neighbourhood is a single $C_{i+1}$, semicomplete) and is the
canonical Bang-Jensen–Huang 1995 / Huang 1995 OLS form for the strong
case.

Enumeration parameters used in the production sweep:

```
p_values         = (2, 3, 4, 5)
max_n            = 16
shapes           = SEMICOMPLETE_SHAPES (7 entries above)
seed             = 20260516
cap_per_p        = 380
```

The enumerator emits up to 380 random combinations per $p$ value
(shuffled product of shapes), filtered to $4 \leq n \leq 16$. The
production sweep streamed **1 127** Construction-A instances.

### §1.3 Construction B — Semicomplete + appended tail

Start with a semicomplete component $T$; append a tail vertex $v$
with a random tournament-style orientation between $v$ and each
existing $u \in T$. Iterate up to 4 tails. The construction yields
*semicomplete* digraphs (a strict OLS subclass), used as a sanity
check.

Streamed: **76**; $\lambda = 3$ exactly: **14**; verified SAT: **14**;
verified UNSAT: **0**.

### §1.4 Construction C — Random OLS via rejection

Independently sample random digraphs (Erdős-Rényi directed,
$p_{\text{arc}} \in \{0.45, 0.55, 0.65\}$, $n \in \{5, 6, 7, 8\}$),
reject unless OLS. Slow but unbiased.

Streamed: **150**; $\lambda = 3$ exactly: **14**; verified SAT:
**14**; verified UNSAT: **0**.

---

## §2 — Sweep statistics

Production sweep configuration (`run_route_b_ols.py` defaults):

```
cap_A             = 1500   (Construction A candidates)
cap_B             = 80     (Construction B candidates)
cap_C             = 150    (Construction C candidates)
instance_time_s   = 15     (cross-check budget per instance)
seed              = 20260516
```

Mirroring V6's table format:

| metric | value |
|---|---:|
| streamed | 1 353 |
| OLS-confirmed (independent check) | 1 353 (100.0 %) |
| strongly connected | 1 342 |
| $\lambda^{\text{arc}} = 3$ exactly | **355 (26.2 %)** |
| $\lambda^{\text{arc}} > 3$ rejected | 372 (27.5 %) |
| $\lambda^{\text{arc}} < 3$ on strong instances | 615 (45.5 %) |
| not strongly connected | 11 (0.8 %) |
| cross-checked verified SAT | **355** |
| cross-checked verified UNSAT | **0** |
| cross-check disagreements | 0 |
| labeled-distinct → canonical-distinct | 355 → 258 |
| largest iso-class | 3 |
| wall-time | 32 s |

Hit-rate at the $\lambda = 3$ gate is **26.2 %**, comfortably above
the spec's 5 % floor. The 27.5 % rejection at $\lambda > 3$ reflects
the structural property that round decompositions with large
bidirected components (notably $K_4^*$, $QR_7$) push
$\lambda^{\text{arc}}$ up.

**Per-construction breakdown:**

| construction | streamed | $\lambda = 3$ | verified SAT |
|---|---:|---:|---:|
| A_round | 1 127 | 327 | **327** |
| B_tail | 76 | 14 | **14** |
| C_random | 150 | 14 | **14** |

---

## §3 — Headline findings

### §3.1 Q1: every 3-arc-strong OLS digraph admits a SAD (empirically)

**355 SAT, 0 UNSAT, 0 disagreements.** Across 1 353 OLS-confirmed
candidates and 355 verified instances at $\lambda^{\text{arc}} = 3$,
no $\lambda = 3$ OLS instance fails to admit a SAD. The Route B
theorem holds on the entire sample. The Lead's 10-item
counterexample protocol is *not* triggered. `team/12_candidate_counterexample.md`
is **not** written.

The empirical confirmation extends across:

- all three OLS construction families (A round decompositions, B
  semicomplete + tail, C random rejection sampling);
- $n$ from 4 through 16;
- $p$ (round component count) from 2 through 5;
- both vanilla shapes ($K_n^*$, $\vec C_n$, Paley) and the BJG–Yeo
  2020 *exception* family ($S_4$ appearing as a kernel component).

### §3.2 Q2: CL1 hypothesis-test fractions (compare V6's 71.5 % / 24.2 %)

For each SAT instance we picked the *natural* CL1 partition for
Construction A: $V_1 = C_1$ (the anchor round component), $V_2 = V
\setminus V_1$. For Constructions B and C we used a generic
"first-half / second-half by vertex index" partition. We then
checked CL1's two final-form hypotheses (`team/11` §5.1):

* (1) $D[V_1]$ and $D[V_2]$ each admit a SAD (intrinsic test:
  `verify_sat` on each induced subdigraph; trivial $n \leq 1$ parts
  are vacuously SAD-decomposable, status `NA`);
* (2) the bridge sets $B^+ = \delta_D^+(V_1)$ and $B^- = \delta_D^+(V_2)$
  admit a 2-coloring with each (direction, colour) class non-empty
  (read off the SAT witness directly).

Aggregate fractions across the 355 SAT candidates:

| hypothesis | fraction | numerator / denominator |
|---|---:|---:|
| **(1)** inner SAD-decomposability on natural partition | **0.28 %** | 1 / 355 |
| **(2)** bridge 2-coloring with each (direction, colour) non-empty | **100.00 %** | 355 / 355 |
| both | **0.28 %** | 1 / 355 |

This is a **dramatic** asymmetry, in opposite direction to V6's
b-mono pattern P1 (V6 found P1a at 71.5 % on the bridge-direction-
monochromaticity test). The reason is structural: in V6 each part
was a SAD-decomposable inner-part library entry by construction; in
the Route B sweep, the *naïve* partition $V_2 = V \setminus C_1$ is
**almost never strongly connected**, because removing one round
component $C_1$ severs the cycle $C_1 \to C_2 \to \cdots \to C_p \to C_1$
into the linear remainder $C_2 \to \cdots \to C_p$. For $p \geq 3$
this $V_2$ has $\lambda^{\text{arc}}(D[V_2]) = 0$ (no back-arcs from
$C_p$ to $C_2$), so $D[V_2]$ cannot admit a SAD on its own.

H1-failure breakdown (V1 status / V2 status):

| failure pattern | count | interpretation |
|---|---:|---|
| V1=UNSAT, V2=UNSAT | 192 | $C_1$ is too small / 2-arc-strong; $V_2$ has $\lambda = 0$ |
| V1=SAT, V2=UNSAT | 115 | $C_1$ is SAD-decomposable; $V_2$ is the unilateral remainder |
| V1=NA, V2=UNSAT | 40 | $C_1$ is a singleton (NA); $V_2$ has $\lambda = 0$ |
| V1=UNSAT, V2=SAT | 6 | rare: $V_2$ accidentally retains a back-edge |
| V1=UNSAT, V2=NA | 1 | rare: $C_2$ is a singleton, $C_1$ is the BJG–Yeo exception |
| **H1 passes** | **1** | $C_1 = K_3^*$, $C_2 = $ singleton (p=2, NA on $V_2$) |

**The single H1-passing instance is the degenerate $\text{round}[K_3^*,
\text{pt}]$ at $n = 4$** — a 3-vertex semicomplete with a single
singleton appendage. Not informative.

### §3.3 Q2 interpretation: CL1 is the wrong lifting mechanism for the
natural OLS partition

The Route B theorem is empirically true (§3.1), but **CL1 in its
final form (`team/11` §5.1) cannot be the proof engine via the
partition $V_1 = C_1$, $V_2 = V \setminus V_1$.** This is a critical
finding for the Structural Specialist's work on `team/14`. Two
possible repairs:

(a) **A different partition.** $V_1 = C_1 \cup C_2$, $V_2 = C_3 \cup
\cdots \cup C_p$. Then $D[V_1]$ contains a directed bipartite
tournament structure that *is* SAD-decomposable (it is itself a
2-component round digraph, hence solvable inductively); $D[V_2]$ is
the analogous $(p-2)$-component round digraph. The inductive base
case $p = 2$ uses both components as $V_1$ and $V_2$ directly. We
did not test this empirically in this sweep — recommended for
`team/15_v2_*` once the partition is refined.

(b) **A different lifting lemma.** CL1 may be the wrong tool;
Route B might need a *contraction* / *kernel-extraction* lemma
specific to round decompositions, in the style of Bang-Jensen–Huang
1995 (which establishes the round-decomposition structure theorem
for OLS).

Either way, the **empirical headline** is that CL1's *hypotheses*
are violated on the natural partition, while the *conclusion* (a SAD
exists) holds anyway. This is consistent with CL1's role as a
*sufficient* condition (`team/11` §4.4 G3): the converse is false,
and many digraphs admit a SAD without satisfying CL1.

---

## §4 — Diagnostic: BJG–Yeo 2020 exceptions as round-component kernels

The Route B target statement (`team/13` §4) explicitly says the
exception family from BJG–Yeo 2020 ($S_4$, $\vec C_3[\overline K_2^3]$,
$\vec C_3[\overline K_2, \overline K_2, P_2]$, $\vec C_3[\overline K_2,
\overline K_2, \overline K_3]$) must be handled separately when those
appear as the round-component kernel. The sweep contains 44 SAT
instances with $S_4$ as $C_1$:

| anchor shape | SAT count | H1 frac | H2 frac | notes |
|---|---:|---:|---:|---|
| K2* | 71 | 0.0 % | 100.0 % | $K_2^*$ has $\lambda = 1$, not SAD-decomposable |
| K3* | 58 | **1.7 %** | 100.0 % | $K_3^*$ has $\lambda = 2$, but it has a SAD; the 1 success is the degenerate $p = 2$ + pt case |
| C3 | 56 | 0.0 % | 100.0 % | $\vec C_3$ has $\lambda = 1$, no SAD on its own |
| **S4** | **44** | **0.0 %** | 100.0 % | **the BJG–Yeo exception**; $S_4$ has $\lambda = 2$ but is UNSAT |
| K4* | 40 | 0.0 % | 100.0 % | $K_4^*$ has $\lambda = 3$, SAD-decomposable, but $V_2$ always UNSAT |
| pt | 40 | 0.0 % | 100.0 % | singleton kernel; $V_1$ is NA |
| QR7 | 18 | 0.0 % | 100.0 % | Paley, $\lambda = 3$, SAD-decomposable; $V_2$ always UNSAT |

**The most important diagnostic.** With $C_1 = S_4$:

* $D[V_1] = S_4$ is **UNSAT** as a stand-alone digraph (it is the
  unique 2-arc-strong tournament with no SAD, per BJ–Yeo 2004; in
  our framework `verify_sat(S_4)` returns `UNSAT` and we record
  `v1_sad_status = "UNSAT"`).
* The full Route-B-style $D = \text{round}[S_4, C_2, \ldots]$ at
  $\lambda^{\text{arc}}(D) = 3$ is nevertheless **SAT** in every
  one of the 44 sampled cases.

This means **the OLS theorem covers strictly more than the union of
CL1-applicable parts**: when $S_4$ appears as a round-component
kernel, CL1 (with $V_1 = S_4$) does *not* apply (because hypothesis (1)
fails on $V_1$), yet the SAD exists. The Route B theorem therefore
**does not need an exception clause for $S_4$** in this regime: the
extra structure of the round decomposition (the all-arcs $S_4 \to
C_2$ and $C_p \to S_4$ bundles) lifts the SAD into existence even
when the local kernel is BJG–Yeo-2020-exceptional.

Concrete example (from the log):

* `round[S4-pt]`, $n = 5$, $V_1 = S_4$ (vertices $\{0, 1, 2, 3\}$),
  $V_2 = \{4\}$ a singleton. Bridges $+R/+B = 1/3$, $-R/-B = 1/3$.
  ILP and SAT both return SAT. The SAD exists.

**Recommendation to `team/13` / `team/14`.** The Route B target
statement should drop the BJG–Yeo-2020 exception clause for the
kernel-component case (at least for $S_4$; ditto $\vec
C_3[\overline K_2^3]$ etc., which we did not include in this sweep
but the same mechanism should apply). The Route B theorem's scope is
**strictly wider** than "CL1 applied to round decompositions": it
covers cases where the kernel is BJG–Yeo-exceptional.

This is a small but real refinement of the publication target.

---

## §5 — Coverage gaps

What this sweep did **not** cover:

(C1) **$p \geq 6$ round decompositions.** The enumerator caps $p$ at
5. Higher $p$ would multiply the diagnostic by combinatorial growth.
Recommended: extend to $p \in \{6, 7\}$ at the same $n \leq 16$ cap
and confirm the SAT verdict and H2 = 100 % hold.

(C2) **Large $|C_i|$.** The enumerator caps single components at $n
= 7$ (the largest shape is $QR_7$). Larger semicomplete components
$|C_i| \in \{8, 9, 10\}$ (e.g., $K_n^*$ for $n \geq 5$, or general
2-arc-strong tournaments) would test the regime where the kernel
alone might saturate the $n$ budget and force $V_2$ to be a trivial
appendage. The Lead's $n \leq 10$ instruction in `team/13` §5 is
satisfied by the current cap of 16.

(C3) **The other BJG–Yeo 2020 exceptions.** $\vec C_3[\overline
K_2^3]$, $\vec C_3[\overline K_2, \overline K_2, P_2]$, and $\vec
C_3[\overline K_2, \overline K_2, \overline K_3]$ were not included
as component shapes. They are semicomplete compositions, hence
semicomplete, hence valid round-component shapes; the §4 diagnostic
strongly suggests they will also lift to SAT in the OLS regime, but
this needs empirical confirmation.

(C4) **Refined partition $V_1 = C_1 \cup C_2$.** The §3.3
recommendation to retry CL1 with a richer partition needs an
empirical pass. Concretely: for each SAT instance with $p \geq 3$,
re-test CL1's hypotheses with $V_1 = C_1 \cup C_2$, $V_2 = C_3 \cup
\cdots \cup C_p$, and see if hypothesis (1) recovers. This is the
single most informative follow-up for the Structural Specialist.

(C5) **Bridge witness enumeration.** The current sweep records one
SAT witness per instance. CL1's bridge 2-coloring (hypothesis (2))
holds on that witness; but a sharper test asks "*does every SAT
witness* have bichromatic bridges, or just this one?" V6's open item
C3 raised the same question; we recommend extending the SAT solver
with blocking clauses to enumerate the first $K$ witnesses and check
bridge 2-coloring on each. Budget: ~1 day.

(C6) **Non-OLS controls.** We did not stream non-OLS 3-arc-strong
digraphs to confirm that the OLS property is doing the work (rather
than 3-arc-strongness alone). The full Phase-3 sweep
(`team/06_phase3_report_v1.md`) covers non-OLS instances at $\lambda
= 3$ and also reports 0 UNSAT, so the work of OLS is structural, not
empirical-existential. No action required here.

(C7) **Random rejection-sampling efficiency.** Construction C
rejected vastly more than it kept (cap_attempts = 12 000 to yield
150 OLS-passing instances). For $n \geq 9$ the rejection rate goes
to ~99.5 %; if Construction C becomes load-bearing we should switch
to a structural sampler (e.g., random round decompositions
post-filtered for $\lambda = 3$). For the current sweep the slow
sampler is fine.

---

## Appendix A — Reproducibility

```bash
cd code
uv run python -m generators.ols                # OLS generator self-test
uv run python run_route_b_ols.py \
    --cap-A 1500 --cap-B 80 --cap-C 150 \
    --instance-time-s 15
```

Seed: `20260516`. Wall-time ≈ 32 s on a single laptop.

Headline JSON log:
`code/logs/route_b_ols_20260516_223612.json` (2.7 MB). Every verified
SAT candidate includes:

* full witness 2-coloring (`witness_red`, `witness_blue` as lists of
  $(u, v, k)$ keyed arcs);
* canonical `pynauty`-derived hash for iso-class identification;
* full CL1 record (V_1, V_2 vertex lists, intrinsic SAD statuses,
  arc-counts and strong-connectivity for both colours restricted to
  each part, bridge counts per direction per colour);
* construction provenance (A_round / B_tail / C_random and
  component shapes).

## Appendix B — Files produced

* `code/generators/ols.py` (new) — OLS generator (Constructions A, B,
  C) plus the independent OLS / semicomplete predicates.
* `code/run_route_b_ols.py` (new) — Route B driver mirroring
  `code/run_phase4_vehicle6.py`.
* `code/logs/route_b_ols_20260516_223612.json` (new) — 355 verified
  SAT witnesses + canonical hashes + CL1 records.

## Appendix C — Compliance with hard rules

| rule | satisfied? | evidence |
|---|---|---|
| OLS verified by independent function | YES | `is_out_locally_semicomplete` runs in the sweep loop, after construction |
| witness logging mandatory | YES | every SAT entry has `witness_red`, `witness_blue` |
| hit-rate floor $\geq 5\%$ at $\lambda = 3$ | YES | 26.2 % (1 353 streamed → 355 verified) |
| canonicalize via `pynauty` | YES | `canonical_key` from `generators/canonicalize.py` applied to every SAT entry |
| stop on $\lambda = 3$ UNSAT | YES (untriggered) | sweep would have written `team/12_candidate_counterexample.md` and halted; no UNSAT found |
| cross-check ILP + SAT | YES | every SAT entry has both `ilp_status` and `sat_status` and `agree = True` |
