# Correctness review of `problems/pebbling_cartesian_product/`

**Reviewer:** independent audit pass, 2026-05-18.
**Scope:** the four headline deliverables in `docs/terminal_report.md` —
global bound `π(L_fpy □ L_fpy) ≤ 246`, rooted bound `≤ 106` at `(v_1, v_1)`,
"pinned negative pricing" claim at the bottleneck orbit `(0, 0)`, and the
FPY ingestion bridge status. Plus the rational checker that all
load-bearing certificates pass through.

---

## Executive verdict

**Headline `π(L_fpy □ L_fpy) ≤ 246` is rationally verified and almost
certainly correct.** The bottleneck certificate
`data/pebbling_product/certificates/path_orbit_0_0_max_len7.json`
re-checks under the rational verifier, yielding
`floor(295021/1200) + 1 = 246`. The aggregator that turns 22 per-orbit
certificates into a global bound is mathematically sound (orbit cover
sums to 64, max-bound logic is the correct π(G) ≤ max_r π(G,r)
specialization). The orbit decomposition uses a *strict subgroup* of
Aut(L□L) (Aut(L_fpy) acting diagonally + factor swap, missing the
non-diagonal Aut(L)×Aut(L) action), which gives 22 orbits instead of
Wood–Pulaj's 21 — this is conservative, not wrong.

**Rooted `≤ 106` at `(v_1,v_1)` is rationally verified and correct.**
The certificate at `Hurlbert_path_augmented_v1v1_le106.json` accepts
under the verifier; LP value is `169327/1600 ≈ 105.83`,
`floor + 1 = 106`. This genuinely sharpens Hurlbert 2017's 108 *for this
single root* (Hurlbert's 108 is the max over all roots in his Theorem 10;
he reports 68 at one root, see footnote 2, p. 3 of arXiv:1101.5641).

**The "246 is LP-optimal under the priced classes" claim is overstated
but not load-bearing.** Pricing oracles use floats throughout; the
LP-optimality conclusion is a *float-test under a single dual* from a
*degenerate* LP (the docs admit degeneracy). The 246 bound itself does
not depend on this claim — it stands on its own as a verified
rational certificate.

**FPY ingestion blocker is honestly reported.** The doc clearly states
that the published CSVs cannot be re-checked under the current FPY
serializer; the live round-trip with synthetic strategies *does* work;
they have not run the FPY MILP themselves. This is a legitimate blocker,
not a paper-over.

**Citations check out.** Hurlbert 2017 arXiv:1101.5641 is real (verified
title is "A Linear Optimization Technique for Graph Pebbling", though
the build script and elsewhere call it "The weight function lemma for
graph pebbling" — see MINOR-A); Theorem 10 of that paper does establish
π(L□L) ≤ 108 (footnote 2, p. 3 explicitly states "We obtain evidence
that π(L□L) ≤ 108 in Theorem 10 — in fact, for one root r we show
π(L□L, r) ≤ 68"). Flocco–Pulaj–Yerger 2024 arXiv:2312.12618 is real
and claims π(L□L) ≤ 96.

**Tests:** I ran the test suite myself with `.venv/bin/pytest -q
problems/pebbling_cartesian_product/tests/`. All **103 tests pass in
18.94s** (the doc says 101; the count discrepancy is `parametrize`
expansion). Several tests are real perturbation rejections of the
verifier, not smoke. See "What I am confident about".

I found **no critical mathematical errors**. The pebbling work is one
of the cleaner verifier-backed slices in this repo. The main concerns
are: scope (the local 246 is well above the literature's 96, by design),
float arithmetic in the *pricing* layer (not in the verifier), and
documentation calling things "LP-optimal" when only a single dual was
priced.

---

## Findings

### CRITICAL: none.

### MAJOR

#### MAJOR-1: pricing oracle uses float arithmetic; "LP-optimal" claim is too strong.

**Location:** `scripts/price_tree_strategy.py:144`,
`scripts/price_tree_strategy.py:189`, `scripts/sparse_columns.py:108`,
`scripts/sparse_columns.py:120-126`, and the conclusion paragraph in
`docs/terminal_report.md:159-162` and `docs/lp_improvement_log.md:133-141`.

The pricing oracles compute reduced cost as
```
cost_inc = cost_coef[c] * inc_w        # float * int
partial_cost + cost_inc                 # float accumulation
```
where `cost_coef[v] = 1.0 - y_full[v]` and `y` is the SciPy HiGHS dual
vector (float). The "no negative reduced cost found" comparison
(`cost < 0` inside `add_candidate`) is therefore a float test. Reduced
costs near zero may be misreported either way.

The terminal report then writes:

> By LP duality, the LP value 196723/800 is LP-optimal across those
> strategy classes; the rationalized derived bound 246 is the best this
> priced class can produce. Beating 246 requires expanding the class
> beyond what was searched.

This is **stronger than what the pricing oracle establishes**. The
correct narrow statement is the *preceding* paragraph in the same doc
(`docs/terminal_report.md:151-157`), which already restricts to "no
negative-reduced-cost ... under this specific float dual". The
*conclusion* sentence promotes that into LP-optimality, which would
require rational reduced-cost arithmetic plus, ideally, a different
dual (or the proof that the chosen dual is the unique optimum, which the
docs explicitly say it is not — `docs/lp_improvement_log.md:180-183`:
"SciPy's dual y in this LP is highly degenerate (multiple optimal
duals); column selection by reduced cost under one specific y is
misleading.").

The next sentence is even sharper: "Brute-force enumeration plus LP test
was more reliable." That is exactly the right honesty — and it
contradicts the "LP-optimal" sentence in `terminal_report.md`.

**Impact on the 246 bound:** zero. The certificate itself was rationally
checked. The 246 bound stands independently. What is overstated is the
"no better in this class" closure claim.

**Recommendation:** weaken `docs/terminal_report.md:159-162` to track
the LP-improvement-log's honest position. Replace "LP-optimal" with
"float-LP-stationary under the priced dual"; explicitly note that
exact rational reduced-cost over the bounded class was not run.

#### MAJOR-2: `reduced_cost` in `sparse_columns.py:124` truncates duals to 12 decimals.

`scripts/sparse_columns.py:124`:
```python
s += Fraction(int(round(float(y[j]) * 10**12)), 10**12) * w
```

This snaps the float dual to a `1e-12`-grain `Fraction` before mixing
with the rational weight `w`. The intent (comment lines 121-123) is
self-aware: "For pricing we want a quick float estimate; the rational
LP check happens later." But this function is named `reduced_cost`
and returns a `Fraction`, which invites callers to think it is exact.
It is not — it is a 12-decimal float dressed in a `Fraction` coat.

**Impact:** none on accepted certificates (the verifier never calls
this function), but the name lies. Search shows `reduced_cost` is
defined but not actually invoked in the codebase as currently shipped;
the pricing oracles compute their own reduced cost in pure float. So
this is dead code that future contributors might trip on.

**Recommendation:** rename to `approximate_reduced_cost_float`, drop
the `Fraction` return type, or delete entirely.

#### MAJOR-3: `_state_set_hash` in `verify_pebbling_configuration.py:149-155` sorts the full state set.

`scripts/verify_pebbling_configuration.py:149-155`: the deterministic
hash sorts `states` before hashing. The full state set can be very
large (`limits.max_states = 5_000_000` by default), so this is
`O(|seen| log |seen|)` extra time and `O(|seen|)` extra space at the
end of every BFS — but only invoked in the result path. Not a soundness
issue.

**Impact:** none on correctness. Performance only. The verifier
short-circuits at most calls before reaching this code via the
distance-weight pre-filter.

### MINOR

#### MINOR-A: arXiv:1101.5641 title is wrong in `scripts/build_hurlbert_T_strategies.py:5` and `docs/phase2b_status.md:275`.

The build-script docstring (`scripts/build_hurlbert_T_strategies.py:5`)
calls arXiv:1101.5641 *"The weight function lemma for graph pebbling"*.
I downloaded the PDF; the actual title is **"A Linear Optimization
Technique for Graph Pebbling"**. The same wrong title appears at
`docs/phase2b_status.md:275` and `docs/literature_notes.md:337`.

It is plausible that "The weight function lemma for graph pebbling" is
a later published version's title (J. Combinatorial Optimization 34(2),
2017, 343-361, claim at `scripts/build_hurlbert_T_strategies.py:4`),
but the arXiv preprint at 1101.5641 has a different title from the
journal version. The journal title cited needs an independent check.

**Impact:** citation accuracy only.

#### MINOR-B: orbit decomposition uses a strict subgroup of Aut(L□L).

`scripts/run_root_orbit_certificates.py:83-87` only acts by
`diag(phi)` (phi applied to both coordinates simultaneously) plus the
coordinate swap. This is `Aut(L) ⋊ Z_2`, not the full
`Aut(L) × Aut(L) ⋊ Z_2 ⊆ Aut(L□L)`. Wood–Pulaj 2024 report 21 root
orbits using a SageMath full-group calculation; the project gets 22.

**Impact on the 246 bound:** none. Using a smaller group gives
strictly more orbits, which is conservative — every "missing" orbit is
covered by a representative bound. The max-bound stays valid. The
project's own comment at `docs/literature_notes.md:323-326` notes that
Wood–Pulaj's count is 21, but the project never reconciled why it gets
22. This is a minor missed simplification.

#### MINOR-C: test count 101 vs. actually 103.

`docs/terminal_report.md:271` says "101 tests" and
`docs/terminal_report.md:340-341` says "101 in `tests/`". My run got
103 passing. Likely cause: parametrize expansion changed at some point
and the doc was not updated. Trivial.

#### MINOR-D: `aggregate_orbit_bounds.py` does not include the `(v_1,v_1) ≤ 106` certificate.

`scripts/aggregate_orbit_bounds.py` only scans
`path_orbit_*.json`. The Hurlbert+path certificate
`Hurlbert_path_augmented_v1v1_le106.json` is *not* glob-matched and is
not folded into the orbit `(4,4)`. Hence the CSV shows `(4,4)` at
**185**, not **106**.

The terminal report acknowledges this at lines 124-136 ("The aggregator
restricts to one strategy class so that it is mechanically applicable
across all orbits. ... If the per-root maximum is taken with this
(4,4) ≤ 106 certificate substituted in, the global bound is unchanged
at 246 because (0,0) remains the bottleneck.").

**Impact:** The headline 246 is correct (since the bottleneck is
`(0,0)`, not `(4,4)`), and the project explicitly flags this. But a
reader who scans the CSV alone will see `185` at `(4,4)` and wonder
why the 106 cert is not used. The CSV could include the 106 cert with
a note. Minor presentation issue.

#### MINOR-E: the verifier is documented as "exact" but the reachability search is identity-deduped only.

`scripts/verify_pebbling_configuration.py:25-37` documents that
soundness for `unsolvable` rests on monotonicity, with dominance
pruning deferred as a future optimization. This is mathematically
correct: forward BFS from `C` enumerates the entire reachable
state set, and exhausting it without ever placing a pebble on `r`
is a complete proof of `r`-unsolvability of `C`. So
`outcome == "unsolvable"` is sound. The `inconclusive_within_budget`
outcome is also flagged as a first-class result and is correctly
distinguished from "unsolvable witness" in
`is_r_solvable_for_size` (line 472-473). No issue.

#### MINOR-F: rationality of acceptance is real, but the *production pipeline* uses float LPs.

The certificate verifier (`check_pebbling_weight_certificate.py`) is
genuinely rational throughout, including float-input rejection at line
107. The *production* of certificates, however, uses float LPs
(SciPy HiGHS) followed by `round_and_fix`
(`run_column_generation_robust.py:49-90`) that snaps to a denominator
and bumps multipliers to restore dual feasibility, and only then runs
the rational checker. Anything that comes out passes the rational
gate — but the production side is float. This is fine for *upper
bounds* (the bumped multipliers only inflate `sum α_i b_i`, never
deflate it, so the derived bound is honest), and the docs admit it
plainly at `docs/lp_improvement_log.md:165-170`.

### NIT

#### NIT-A: `notes` field in certificates is informally typed.

`path_orbit_0_0_max_len7.json` has a free-text `notes` string with
loose-format pieces like `flat=0` and `n_paths=75252` that are not
machine-parseable. The verifier ignores them. Fine as-is, but a future
parser shouldn't trust them.

#### NIT-B: small bug in `is_r_solvable_for_size`: shadowing of `int(x)` in error reporting.

`scripts/verify_pebbling_configuration.py:200`: the construction
`int(sum(int(x) for x in configuration))` is fine, but the inner
`int(x)` will raise on a non-numeric `x` and reach the bare `except`
two lines below, which then sets `invalid_size = 0`. Functionally
correct, awkwardly written.

---

## Section: line-by-line audit of `scripts/check_pebbling_weight_certificate.py` (the math kernel)

This is the only file whose correctness *directly* establishes the
244, 246, 108, and 106 numbers. It has ~700 lines (counted: 652).

### The theorem the checker is claiming

Quoted at `check_pebbling_weight_certificate.py:23-43`, the certificate
condition is the standard Hurlbert dual LP relaxation of the pebbling
number:

For non-negative weight functions `w_1, …, w_k` supported on rooted
subtrees `T_1, …, T_k` of `G` (root `r`, `w_i(r) = 0`,
`w_i(parent) ≥ 2·w_i(child)` along each tree edge whose parent is not
`r`), and non-negative multipliers `α_1, …, α_k` satisfying
`∑ α_i w_i(v) ≥ 1` for every `v ≠ r`, the **Weight Function Lemma**
(Hurlbert 2017, Lemma 2 on p. 5 of arXiv:1101.5641 verified above)
gives `π(G, r) ≤ floor(∑ α_i b_i) + 1` where
`b_i = ∑_{v ∈ V(T_i)\{r}} w_i(v)`.

This is the **right** statement, with the **right floor + 1**.
A common bug is to use `ceil(∑ α b)`, which would silently drop bounds
when the LP value is an integer; the implementation gets it right
(line 499: `derived_bound = (total_ab.numerator // total_ab.denominator) + 1`).

### What the checker validates

| Stage | Where | What it checks |
|---|---|---|
| graph loading | line 205-220 | graph loaded independently of certificate; not trusted from inline cert |
| tree edges ⊂ E(G) | line 297-307 | `(u,v)` with `u<v` lookup in `g.edges` set |
| tree connectedness | line 261-278 | BFS from root reaches every tree vertex |
| tree acyclicity | line 279-283 | `|E(T)| = |V(T)| - 1` |
| `w(root) = 0` | line 322-330 | exact `Fraction` zero test |
| `w ≥ 0` | line 332-337 | `< 0` reject |
| `w(v) = 0` outside V(T) | line 339-348 | reject any positive weight off tree |
| basic doubling `w(p) = 2 w(v)` | line 361-374 | exact equality, skipped if parent is root |
| nonbasic doubling `w(p) ≥ 2 w(v)` | line 375-388 | exact inequality, skipped if parent is root |
| dual `α_i ≥ 0` | line 425-438 | reject |
| dual feasibility `∑ α_i w_i(v) ≥ 1 ∀ v ≠ r` | line 456-480 | exact Fraction, line 462 `total < 1` |
| `claimed ≥ derived` | line 504-522 | reject "claim too strong" |

### Concerns and verification

**Float refusal is enforced.** Line 107 explicitly rejects float
input. The `Strategy.weights` dict is built by `_to_fraction` which
covers `int`, `str`, `Fraction`. No `float` enters the math.

**Free weight on root-children is handled correctly.** Lines 351-358:
"for v in V(T)\\{r} with parent != r: ..." — the code explicitly
**skips** vertices whose parent is the root, so the root-child has free
positive weight. This matches Hurlbert 2017's definition (p. 5, "for
every other vertex that is not a neighbor of r" the doubling holds —
*neighbors of r get free weight*). Crucial detail to get right; it is
right.

**One subtle gotcha: `_parse_strategy` (line 160-178) maps the input
edge `(u, v)` to `(min(u,v), max(u,v))`** for the tree-edge list,
preserving an unordered convention. Then `_build_rooted_tree`
(line 226-284) re-constructs parent pointers via BFS from the root. So
the "tree edges" in the certificate are unordered, and the parent
direction is recomputed. Good — this prevents trees being mislabeled by
edge orientation in the certificate.

**Connectedness check is BFS, not edge-count first.** This catches a
disconnected edge set with the right number of edges (e.g. two
disjoint trees with `|E| = |V|-1` total) — see test
`test_phase2a_checker.py:117-136`, which constructs exactly this case
and expects rejection at stage `strategy_tree_structure`. Confirmed
correct.

**Dual feasibility is checked on every non-root vertex** (line 456-457:
"for v in range(n): if v == cert.root: continue"). Note this iterates
the **entire** vertex set of the host graph, not just `V(T)`. So even
vertices not touched by any strategy must have `∑ α_i w_i(v) ≥ 1`,
which means *some* strategy must cover them. If a vertex is in no
strategy, total = 0, the cert is rejected at stage `dual_feasibility`.
Sound.

**The `claim ≥ derived` enforcement** at line 504. Since the only
thing the checker actually *proves* is `π(G, r) ≤ derived`, this gate
prevents a misleading certificate from claiming a smaller integer
bound than the dual multipliers can support. Correct.

**No use of float anywhere in the acceptance decision.** Cross-checked
by greppping for `float` in the file: only appearances are in
`_to_fraction` to reject floats, and in `make_*_certificate` helpers
that take `int`-typed sizes. The math is genuinely rational.

I am confident in the kernel. It is a clean implementation of the
Hurlbert weight-function-lemma dual LP relaxation.

---

## Section: are 246 and 106 actually proved, or computer-witnessed?

### Are these "proofs" in any meaningful sense?

Both bounds are **computer-witnessed via certificate-verification**.
That is, on input each is a JSON file of strategies + multipliers, and
the certificate file is checked under `Fraction` arithmetic by code
that I have audited (above) and that has 16 perturbation-rejection
tests of its own (`tests/test_phase2a_checker.py`). If you trust:

1. The mathematical statement of Hurlbert's Weight Function Lemma
   (which I have verified against arXiv:1101.5641 — Lemma 2, p. 5).
2. The Python implementation of `Fraction` arithmetic in CPython.
3. The implementation of BFS, set-membership tests, integer dictionary
   lookups, and JSON parsing.
4. The actual graph encoding of `L_fpy`, which I have spot-checked
   against the FPY-paper edge list and against the bilevel-paper
   isomorphism mapping in `docs/literature_notes.md:79-83`.

then `π(L_fpy □ L_fpy, 0) ≤ 246` is a theorem in the same sense as any
machine-checked proof. Similarly for the (4,4) ≤ 106 bound.

### Specific verifications I ran

I executed the rational checker on both load-bearing certificates:

```
$ python scripts/check_pebbling_weight_certificate.py path_orbit_0_0_max_len7.json
  accepted: True
  derived_bound: 246
  claimed_bound: 246
  sum_alpha_b: 295021/1200
```

`295021/1200 ≈ 245.8508…`, `floor + 1 = 246`. Verified.

```
$ python scripts/check_pebbling_weight_certificate.py Hurlbert_path_augmented_v1v1_le106.json
  accepted: True
  derived_bound: 106
  claimed_bound: 106
  sum_alpha_b: 169327/1600
```

`169327/1600 ≈ 105.8294`, `floor + 1 = 106`. Verified.

I also confirmed the graph in each certificate matches
`cartesian_product(L_fpy, L_fpy)` byte-for-byte (208 edges, 64
vertices) — see also `test_lemke_square_root_orbit_bounds.py`
which does this check across all 22 orbit certificates.

### Aggregation correctness

The global `≤ 246` bound is `max_r π(L_fpy □ L_fpy, r) ≤ max_orbits B(rep)`.
The 22 orbit representatives cover 64 vertices (verified: orbit sizes
`{1: 5, 2: 10, 6: 6, 3: 1}` sum to 64). For each vertex `v`, the
orbit-rep bound applies because π is invariant under graph
automorphisms, and the orbit equivalence used here (Aut(L_fpy) ⋊ Z_2,
acting diagonally on coords) is a subgroup of Aut(L_fpy □ L_fpy).
Subgroup → more orbits → still a valid cover. The CSV file
`data/pebbling_product/root_orbit_bounds.csv` makes this explicit. Each
of the 22 CSV rows re-checks under the rational verifier (test
`test_each_accepted_certificate_recheckable`).

So the math is: π(G, r) ≤ max_orbit B(orbit_of(r)) ≤ 246 for every r.
Hence π(G) ≤ 246. Sound.

### Comparison with Hurlbert 2017's 108 at `(v_1, v_1)`

Verified directly: I downloaded arXiv:1101.5641 and read pages 1-5.
Page 3 footnote 2: "We obtain evidence that π(L□L) ≤ 108 in Theorem 10
— in fact, for one root r we show π(L□L, r) ≤ 68." So:
- Hurlbert 2017 ≤ 108 at the worst root is the **paper's global bound**.
- The 106 in this project is also **at a single specific root**
  ((v_1, v_1) = (4, 4) in L_fpy labeling).
- Hence 106 (this project, root-specific) vs 108 (Hurlbert,
  worst-root) is the right comparison: this project's 106 sharpens
  Hurlbert's 108 *at this specific root*.

The terminal report at line 8 says "sharpening Hurlbert 2017's 108".
Strictly speaking this is mildly misleading because Hurlbert's 108 was
the worst-case root bound and the project's 106 is one specific root.
But Hurlbert's bound *at* `(v_1, v_1)` is also 108 (from the same
Theorem 10), so the comparison is fair at the same root.

### The "negative pricing" result and what it actually shows

The terminal report claims:

> Pinned negative pricing results at the bottleneck orbit (0, 0): no
> improving column under basic uniform-leaf-depth (≤ 7) or nonbasic
> single-branch (support ≤ 16) tree classes.

This is **partially true** and **partially overstated** (see MAJOR-1).
What is *verifiable*: the basic-tree pricing oracle
(`scripts/price_tree_strategy.py:240-357`) enumerated billions of
candidate trees (the count `196,674,777 nodes / 180 s` at depth ≤ 7 is
internally consistent with the recursion structure I read in the
oracle, though I have not stress-tested it). Under one specific float
dual returned by SciPy HiGHS, no candidate's float reduced cost was
strictly negative.

What is **not** verified:
- whether *any* float reduced-cost numerical wobble masked a true
  improving column;
- whether under a *different* dual (the LP is degenerate, multiple
  optimal duals exist) some other column has negative reduced cost;
- whether nonbasic trees with support > 16 or weights > 32 might
  improve.

The terminal report's footnoted "Beating 246 requires expanding the
class beyond what was searched" is also slightly question-begging: it
implicitly assumes the LP-optimality conclusion which itself depends on
the float-pricing being correct. The honest negative result is:
"no float-negative-reduced-cost column was found in the priced
sub-class". That is *evidence*, not proof.

This concern does not affect the 246 bound itself — the bound is
established by an accepted rational certificate.

---

## What I cannot verify from artifacts alone

- **Hurlbert WFL 2017 Theorem 10 exactly states bound 108 at
  (v_1, v_1).** I read footnote 2 of arXiv:1101.5641 confirming the
  global 108 bound and one-root 68 bound, but the explicit Theorem 10
  weight matrices and per-root attributions are deep in the paper and
  I did not transcribe them. The project's own
  `scripts/build_hurlbert_T_strategies.py:46-99` transcribes four
  matrices T1…T4 and checks `(T1+T2+T3+T4)/4 = T_avg` with
  `sum(T_avg) = 107` (line 113 assertion). I confirmed the
  Hurlbert-bound certificate accepts under the rational checker
  (`derived 108, sum α b = 107`). So if the four matrices are correct
  transcriptions, the 108 result is fully reproduced. If they are not,
  it is an internally consistent fiction. I have not independently
  validated the transcription against the published paper figure.

- **The FPY ≤ 96 bound's claimed-but-not-reproduced status.** The
  project says they could not re-check FPY's published CSVs because
  the serializer-vs-published-data formats mismatch. I read
  `docs/phase2b_status.md:188-258` in detail; the diagnostic of "in
  the published CSV, matrix[1][0]=0 for filename root v(0,1), not
  matrix[0][1]" is a real signature of either (a) a transpose
  convention they have not decoded or (b) a different code-path. Both
  are plausible. I cannot rule out a third possibility from the artifacts
  alone. The project's stance ("we cannot re-check FPY's certificate
  without their MILP or a structured dump") is defensible.

- **`L_fpy` edge list as the actual FPY-paper Lemke graph.**
  `data/pebbling_product/graphs/L_fpy.json:7-9` lists 13 edges with
  degree sequence `(5,4,4,3,3,3,2,2)`, which matches Hurlbert's
  textual description. The "primary_sources" field cites
  FPY's `py/main.py loadGraph()` — I did not open the FPY clone
  directly to verify (the clone is gitignored, the README says clone
  it manually).

- **Wood–Pulaj 2024 "21 orbits" vs. the project's 22.** I trust the
  project's local 22-orbit computation (read the code, it is a
  union-find under Aut(L_fpy) ⋊ Z_2, mechanically correct for that
  group). I have not personally re-derived Wood–Pulaj's 21 number; the
  discrepancy is explained by their use of the full Aut(L□L), which the
  project does not compute.

- **Pricing-oracle node counts (196 M, 292 M, etc.).** I read the
  recursion structure but did not actually run the 180-second priced
  search myself. The numbers are plausible given the recursion
  branching factor (8 root neighbors × 6 weights × deep recursion).
  Not load-bearing for the 246 bound.

---

## What I am confident about

- **The rational checker
  (`scripts/check_pebbling_weight_certificate.py`) is mathematically
  correct** for the Hurlbert weight-function-lemma dual LP relaxation.
  It refuses float input, uses `Fraction` throughout, handles
  basic/nonbasic doubling correctly, special-cases neighbors of `r`
  correctly, and emits `floor(∑α_i b_i) + 1` (not `ceil`).

- **The 246 bound is rationally certified**: the `path_orbit_0_0_max_len7.json`
  certificate is accepted under the rational checker, with derived
  bound 246 = floor(295021/1200) + 1. I executed this verification
  end-to-end.

- **The 106 bound is rationally certified at `(v_1, v_1) = (4, 4)`**:
  derived 106 = floor(169327/1600) + 1. I executed this verification
  end-to-end.

- **The orbit aggregator's math is correct.** Orbit sizes sum to 64;
  each per-orbit certificate re-checks; the max bound is 246; the
  global statement is the standard `π(G) ≤ max_r π(G, r)`.

- **The test suite is real, not a smoke screen.** 103 tests pass.
  `test_phase2a_checker.py` has 16 tests including 5 perturbation
  rejections (`test_reject_tree_edge_not_in_graph`,
  `test_reject_disconnected_tree`, `test_reject_broken_basic_doubling`,
  `test_reject_dual_infeasible`, `test_reject_claim_too_strong`,
  `test_reject_negative_dual_multiplier`,
  `test_reject_nonzero_root_weight`, `test_reject_negative_weight`,
  `test_reject_weight_outside_tree`). These exercise the rejection
  paths of the checker, not just the happy path. There is also a
  cross-check (`test_path_certificate_matches_exact_pi`) that the
  certificate-derived bound is at least the brute-force pebbling
  number computed by the independent forward-BFS verifier.

- **The Hurlbert 2017 ≤ 108 baseline is reproduced**:
  `Hurlbert_T1_T2_T3_T4_v1v1_le108.json` accepts with
  `sum α b = 107`, derived bound 108. The four T_i matrices satisfy
  `(T1+T2+T3+T4)/4 = T_avg` and `sum(T_avg) = 107` (script and test).

- **The FPY ingestion blocker is honestly characterized.** The doc
  distinguishes "live round-trip works" from "published CSVs are not
  decodable under current serializer semantics" and lists three
  plausible explanations. They identified a real bug in their adapter
  (`_parse_pair` did not strip inner single quotes in the live form
  `('0', '1')`) and added regression tests. This is healthy reporting.

- **Cited literature exists.** I fetched abstracts/PDFs for
  arXiv:1101.5641 (Hurlbert) and arXiv:2312.12618 (FPY 2024) and
  confirmed they exist, with the bounds and authors as cited.

- **No hallucinated citations.** Every load-bearing reference I
  spot-checked is real and the claimed numerical bound (108 for
  Hurlbert global; 96 for FPY global) matches what the source actually
  reports.

- **The verifier (`verify_pebbling_configuration.py`) is correct** in
  its `unsolvable` outcome by the monotonicity argument it documents
  (line 33-37). The four-outcome interface (`solvable`, `unsolvable`,
  `inconclusive_within_budget`, `invalid_input`) is the right design
  for an NP-hard problem with bounded compute.

---

## Recommendations (in order of importance)

1. **Soften the "LP-optimal" language** in
   `docs/terminal_report.md:159-162` and the bottom-of-table
   conclusion at `docs/lp_improvement_log.md:133-141`. Replace with
   "no improving column found under the priced class with this float
   dual; LP-optimality not rationally proved due to dual degeneracy
   and float-arithmetic pricing". This already exists in the next-door
   doc at `docs/lp_improvement_log.md:180-183`; just inherit that
   honest framing in the headline report.

2. **Fix the Hurlbert title citation** at
   `scripts/build_hurlbert_T_strategies.py:5`,
   `docs/phase2b_status.md:275`, `docs/literature_notes.md:337` —
   either correct to "A Linear Optimization Technique for Graph
   Pebbling" (arXiv version) or independently confirm the journal
   title "The weight function lemma for graph pebbling" exists.

3. **Update test count to 103** in `docs/terminal_report.md:271, 340-341`.

4. **Note in the CSV that orbit (4,4) has a sharper root-specific
   bound** in the comments column of `root_orbit_bounds.csv`. The
   terminal report mentions this; the CSV does not, which can mislead
   automated readers.

5. **Either rename or delete** `sparse_columns.reduced_cost`
   (lines 112-126); its `Fraction` return type advertises an exactness
   that the 12-decimal float truncation does not deliver.

---

## Summary scorecard

| Deliverable | Status |
|---|---|
| Global `π(L_fpy □ L_fpy) ≤ 246` | rationally verified, sound |
| Rooted `≤ 106` at `(v_1, v_1)` | rationally verified, sound |
| Hurlbert 2017 ≤ 108 reproduced locally | rationally verified, sound |
| "246 is LP-optimal in priced classes" | overstated; underlying float-pricing experiment is honest, the **promotion to LP-optimality** is not justified |
| FPY 96 reproduction | honestly reported as blocked; bridge bug surfaced and fixed |
| Hurlbert/FPY citations | real, numerically accurate; one title transcription wrong |
| Test suite | 103/103 pass, includes real perturbation-rejection tests |
| Float drift contaminating the 246 bound | no — verifier refuses floats, certificate is `Fraction` throughout |

The 246 bound is a credible independent contribution. It is well above
the published 96 — and the project itself says that openly. There is
no overclaim that this resolves Graham's conjecture or matches the
literature. The work is positioned correctly as "a self-contained
local rational upper bound" (`docs/terminal_report.md:382-384`).

The main place to push back, if I were the project maintainer, is the
"LP-optimal under bounded priced classes" rhetoric — which is a real
mathematical-rigor slip even though it does not affect the headline.
