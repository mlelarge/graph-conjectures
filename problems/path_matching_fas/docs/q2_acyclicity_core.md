# Q2: the acyclicity-core and where the D70 hardness lives

**Q2.** Among tournaments with `Δ*(T)=2`, is "∃ an acyclic degree-2 order"
(equivalently Path-FAS = YES) decidable in polynomial time?

A *degree-2 order* has max back-degree ≤ 2, so its back-arc graph is a
disjoint union of paths and cycles. Q2 asks whether the cycles can always
be avoided. The **acyclicity-core** = the `Δ*=2` minimal-NO instances
(= `large_width_no ∩ {Δ*=2}`): a degree-2 order exists but every one is
cyclic. Exact counts: **9 / 202 / 2316** at n = 7 / 8 / 9.

---

## 1. Critical diagnostic: the D70 forward-DP fooling family lives at Δ*=2

The project proved (D70, `docs/forward_dp_lower_bound.md`) that any forward
score-window DP for Path-FAS needs `2^Ω(n)` states, via the toggle / probe
fooling family. **Where does that family sit in the degreewidth split?**

Computed with the exact Held–Karp solver `scripts/degreewidth_exact.py`
(driver: `scripts/q2_d70_diagnostic.py`):

| family | n | Δ* |
|---|---|---|
| reversed matching `RM(m)` (base) | 2m, m=2..10 | **1** |
| toggle family (base) | 4k, k=1..5 | **1** |
| toggle **with probe** (the actual fooling instances) | 4k+7 | **2** |

The base substrates are `Δ*=1` (trivial YES; back-arc graph is a matching).
The **probe-augmented toggle tournaments — the genuine fooling instances —
are exactly `Δ*=2`**, i.e. they live inside the Q2 layer.

Moreover the fooling mechanism is **acyclicity, not degree**. For every
probe gadget `j` and every toggle prefix `ε`, the canonical completion has
max back-degree ≤ 2; when it fails (`ε_j = 1`) the back-arc graph contains
a **cycle** (the gadget path `f_j – a_j – b_j – g_j` closed by `z→f_j`,
`z→g_j`), never a degree-3 vertex. Across k = 2,3 there are **zero
degree-only failures** — the discriminator is purely cyclicity.

The fooling-set claim (`verify_fooling_set`) holds for k = 1,2,3:
prefix `P_ε` extends under the gadget-`j` probe **iff `ε_j = 0`**, and the
prefix score-windows are probe-invariant. So `2^k` prefixes are
extension-distinguishable using only the acyclicity decision at `Δ*=2`.

> **Diagnostic verdict (PROVED for the family, EMPIRICAL Δ* up to listed n).**
> The D70 `2^Ω(n)` forward-DP lower bound lives **entirely at `Δ*=2`** and is
> driven by the **acyclicity** question Q2 asks. **Q2 inherits the forward-DP
> lower bound.** Any polynomial Q2 algorithm must be **non-forward / global**;
> no score-window prefix DP can decide the acyclicity-core.

This is the "bad fork": Q2 is *not* more tractable than full Path-FAS for
forward methods. It does not settle P-vs-NP-hard for Q2 — it rules out the
one method (forward DP) that the degreewidth split might have rescued.

---

## 2. The set of degree-2 orders is NOT polynomially bounded

The natural positive route — "enumerate the degree-2 orders, test each for
acyclicity" — is **correct but exponential**. Counts of degree-2 orders
(`scripts/q2_core_cycle_analysis.enumerate_degree2_orders`):

| instance | n | #degree-2 orders |
|---|---|---|
| toggle+probe k=1 | 11 | 683 |
| toggle+probe k=2 | 15 | ~1390 |
| toggle+probe k=3 | 19 | ~7000–7900 |

This grows like `~3^k = 2^Ω(n)` — the same `2^k` blow-up as the fooling set.
The decision procedure `q2_decide` (degreewidth gate + enumerate degree-2
orders + acyclicity check) was **validated against the brute-force LFO
decider: 0 mismatches over 1600 random tournaments n ≤ 7** — so it is a
*correct* algorithm, just exponential.

**The small order counts on the minimal-NO core are a selection artifact.**
On the certified minimal-NO catalogues the #degree-2 orders is tiny
(n=7: 1–15; n=8: 1–8; n=9: 1–36), because minimal obstructions are tight.
But random `Δ*=2` tournaments already reach dozens, and the D70 family
reaches thousands at the same n. So "few degree-2 orders" is **not** a
structural property of `Δ*=2`; it is a property of *minimal* NOs.

---

## 3. Structure of the forced cycle on the core (EMPIRICAL, full catalogues)

For each acyclicity-core instance we enumerated **all** degree-2 orders and
recorded the cycle structure of each back-arc graph
(`scripts/q2_core_cycle_analysis.py`).

* **All confirmed NO**: `any_acyclic = False` for every core instance at
  n = 7, 8, 9 (re-derives the catalogue, independent of the `no_kind` tag).
* **Min number of cycles per order** (the best any degree-2 order does):

  | n | core | min-cycles = 1 | = 2 | = 3 |
  |---|---|---|---|---|
  | 7 | 9 | 9 | 0 | 0 |
  | 8 | 202 | 191 | 11 | 0 |
  | 9 | 2316 | 2245 | 70 | 1 |

  The overwhelming majority of core instances admit a degree-2 order whose
  back-arc graph is **a single forced cycle** plus paths. A small minority
  force 2 (or, once, 3) disjoint cycles.

* **Forced-cycle lengths** range over 3..n: at n=9 the min-cycle signature
  distribution spans `{3,4,5,6,7,8,9}` plus pairs `{(3,3),(3,4),(3,5),
  (3,6),(4,5),...}`. The cycle is a **global object whose length scales
  with n** — so a *finite forbidden-subgraph* characterization (which would
  give poly) is **implausible**: arbitrarily long induced forced cycles
  appear.

This matches the D70 picture: the obstruction is a back-arc *cycle* that
the order cannot break, and there can be exponentially many candidate
orders to rule out.

---

## 4. Bottom line and next step

* **Verdict on Q2:** unresolved, but the encouraging fork is **closed
  negatively** — the known `2^Ω(n)` hardness family sits squarely in the
  `Δ*=2` layer and is an acyclicity (not degree) obstruction, so Q2 is *as
  hard as full Path-FAS for any forward/score-window DP*. The residual hope
  for poly Q2 must come from a **global** method (flow/matroid/algebraic),
  not prefix dynamic programming, and 2-SAT is excluded for the same
  ternary-transitivity reason as full Path-FAS
  (`scripts/nonsweep_path_fas.two_sat_attempt`).

* **Sharpest localization.** The difficulty is *not* the local cycle
  (often a single short forced cycle) but the **exponential number of
  degree-2 orders** that a global certificate must simultaneously rule out;
  the D70 family realizes this with `~3^{n/4}` orders all of which must be
  shown cyclic.

* **Concrete next step.** Pursue a *global* (non-forward) certificate for
  "every degree-2 order is cyclic": e.g. an algebraic/parity invariant of
  the back-arc graph summed over the degree-2-order polytope, or a matroid
  union infeasibility certificate on the (pair-precedence, degree-budget)
  structure — and red-team it against the D70 probe family first, since that
  family is the minimal known witness that forward and enumeration methods
  both die. Confirm Q1 (`Δ*≤2` recognition) in parallel: it is the gate and
  is itself open.

### Tools (this round, all `q2_`-prefixed; no shared files modified)
* `scripts/q2_d70_diagnostic.py` — Δ* of the D70 families; acyclicity-vs-degree of fooling failures.
* `scripts/q2_core_cycle_analysis.py` — enumerate degree-2 orders, forced-cycle census; `q2_decide` validated vs brute force.
* `tests/test_q2_acyclicity_core.py` — regression checks for the above.
