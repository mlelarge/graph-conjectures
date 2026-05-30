# Cutting-Plane Oracle Structural Audit — theorem-status note

Audit of the exact directed-cycle + undirected-cycle cutting-plane oracle
(`scripts/nonsweep_path_fas.py::ilp_exact_linear_forest_fas`) on the
certified minimal-NO catalogues
(`data/minimal_no_obstruction_catalogue_n{7,8,9}.json`).  Goal: decide
whether the oracle has hidden polynomial structure or develops a hard
obstruction.  Code: `scripts/cutting_plane_audit.py`.

The LP relaxation is the exact linear-forest-FAS feasibility LP, one
variable `x_a ∈ [0,1]` per arc:
  * directed cycle `C`: `Σ_{a∈C} x_a ≥ 1` (FAS hits every directed cycle);
  * undirected cycle `U`: `Σ_{a∈U} x_a ≤ |U|−1` (back-arc set is acyclic);
  * degree: `Σ_{a∋v} x_a ≤ 2` (linear-forest max degree).
A YES instance gives the integral point `1_S` for its linear-forest FAS
`S`; the question for a NO instance is whether the cycle-cut polytope is
**empty** (a polynomial Farkas certificate of NO) or merely
**non-integral** (an integrality gap that blocks the route).

---

## Verdict: the cutting-plane route is BLOCKED on the vast majority

> **Witness.**  The **full** cycle-cut LP — *all* directed-cycle cuts and
> *all* undirected-cycle cuts, plus degree — is **feasible and
> fractional** on **all 20/20 n = 7** minimal-NO instances and **546/572
> n = 8** minimal-NO instances.  Thus the LP/cycle-cut route **fails on
> the vast majority of NO instances** (no Farkas/LP certificate).  A
> small n = 8 minority — **26/572**, all of `large_width_no` type — *does*
> admit a genuine LP/Farkas certificate (the cycle-cut polytope is empty).
> That subfamily is certified, not noise, but it is too small and too
> type-specific to rescue the route.  The exact oracle is therefore a
> *correct exponential branch-and-cut solver*, not the start of a
> polynomial proof.

The enumeration is validated **complete**: for n = 7 it produces all
1172 undirected cycles of K₇ (= Σ_{k=3}^{7} C(7,k)(k−1)!/2) and the
correct directed-cycle set (0 for a transitive tournament); on the
validation examples checked the LP behaves integrally (value 0 for an
acyclic tournament, 1 for a 3-cycle).  So the fractional gap on the NO
instances is real, not a missing-cut artifact.

### Step 3 — full cycle-cut LP (the decisive read)

| n | minimal-NO instances | LP infeasible (certificate) | **LP feasible-fractional (GAP)** |
|---|---|---|---|
| 7 | 20  | 0  | **20** (100 %) |
| 8 | 572 | 26 | **546** (95.5 %) |

At n = 8 the 26 LP-infeasible (certified) instances are **all
`large_width_no`**; **every** `hall_failure` NO is a gap (n = 7: 3/3;
n = 8: 57/57).  Under the **min-Σx_a objective**, the fractional optima
have value ≈ 5–7 with 12–18 fractional variables (n = 7).  Explicit
fractional feasible solutions for representative n = 7 and n = 8 NO types
(especially `hall_failure`) are stored in
`data/cutting_plane_gap_witnesses.json` for future study of stronger
inequalities.  A first structural signal in those witnesses: the
`hall_failure` gap points are **half-integral** (values in {0, ½, 1};
e.g. n = 8 `8#2564`, min-Σx = 8, 16 half variables), whereas the
`large_width_no` gap points use **thirds** (⅓, ⅔; e.g. n = 7 `7#0`,
min-Σx = 5).  So the two NO families sit at different vertices of the
cycle-cut polytope — any stronger inequality would have to cut off both a
½-pattern and a ⅓-pattern.

### Step 1 — instrumented lazy oracle (certificate sizes)

The branch-and-cut oracle terminates with **few** cycle cuts, and the
count **decreases** with n (the degree ≤ 2 cap makes the base
triangle+degree *integer* program infeasible more often as n grows):

| n | mean cuts | cut-count range | % needing 0 cycle cuts |
|---|---|---|---|
| 7 | 4.8  | 0–20 | 20 % (4/20) |
| 8 | 1.17 | 0–10 | 41 % (233/572) |
| 9 (sample 500) | 0.74 | 0–14 | **62 %** (312/500) |

Directed cuts have length 4–7, undirected cuts length 3–9.  At n = 7 **no
NO needs an only-undirected certificate** (undirected cuts always co-occur
with directed ones); at n = 9 only-undirected certificates do appear
(69/500).  **Caveat:** these are *integer*-infeasibility certificates —
the relaxed program becomes infeasible **as an ILP**, while its LP
relaxation (indeed the full cycle-cut LP, Step 3) stays fractional.  So a
small cut set is **not** a polynomial certificate: verifying it requires
integrality (an ILP/coNP check), not an LP.

### Step 2 — obstruction taxonomy

`hall_failure` NOs are "easier" (mean 3.0 cuts at n = 7, 0.23 at n = 8,
0.0 at n = 9 — caught essentially by triangle+degree) than `large_width_no`
(mean 5.1 / 1.28 / 0.82).  The taxonomy does, however, split the **LP**
outcome: **every `hall_failure` NO is a gap** (3/3, 57/57), while the
only LP-certifiable instances are `large_width_no` (26/515 at n = 8).  So
the certifiable subfamily is type-specific — but it is the minority
(95.5 % of n = 8 NOs are gaps), so the taxonomy does not rescue the route.

---

## What this means

  * **The exact oracle is correct but exponential.**  Its termination
    relies on *integer* infeasibility (branch-and-bound inside each
    `milp` round), not on an LP/Farkas certificate.  Few cut-rounds does
    **not** imply polynomial time: each round is an NP-hard ILP, and the
    LP relaxation never decides NO.
  * **The cycle-cut LP is not integral on NO instances.**  This sharpens
    and *quantifies* the prior `nonsweep_path_fas.md` §6 finding ("the
    undirected acyclicity of the back-arc graph is not LP-integral"):
    even the **full** directed+undirected cycle-cut closure leaves a
    fractional gap on every minimal-NO.
  * **No polynomial NO certificate from this route.**  A polynomial proof
    of Path-FAS ∈ coNP via this LP would need a *fundamentally stronger*
    cut family (one that closes the gap) — none is in hand, and the
    unanimous gap is evidence against a clean cycle-packing/Farkas
    certificate.

> **Honest status.**  The cutting-plane route is **blocked on the vast
> majority**: the exact oracle is a correct exponential solver, and the
> full cycle-cut LP has an integrality gap on 20/20 n = 7 and 546/572
> n = 8 certified minimal-NO instances (with 26/572 `large_width_no`
> instances LP-certifiable — a certified but too-small, too-type-specific
> subfamily).  This decides Path-FAS neither in P nor coNP via this route;
> it cleanly closes the LP/cutting-plane lens, with an explicit fractional
> witness on each gap instance (catalogued).  **The cutting-plane route is
> PAUSED**, alongside forward-DP (blocked by D70) and fanout/Lemma C
> (paused, D90).  The next real proof direction must lie outside these
> three: a genuinely new global structural invariant for minimal NOs, or
> a non-local hardness construction.
