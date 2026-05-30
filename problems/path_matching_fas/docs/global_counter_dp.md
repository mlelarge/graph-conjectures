# Global-counter DP for Path-FAS: exploiting LFO forest constraints

This note investigates the **alternative positive route** to settling
Aboulker–Aubian–Lopes Problem 4.4 (arXiv:2402.10782): exploit the
*linear-forest* global constraint on the LFO back-arc graph to
compress the per-bag DP state on the interaction graph
`J(T) = H(T) ∪ G_flex(T)`.

The route is *orthogonal* to the dormant-matching-quotient lemma
attempt: instead of quotienting many independent forced components into
a polynomial aggregate, we ask whether the **partition** piece of the
DP state can be replaced by a **bounded-state global counter** while
still enforcing the linear-forest (degree ≤ 2 + acyclic) constraint.

Implementations: `scripts/global_counter_dp_probe.py`
Tests:           `tests/test_global_counter_dp.py`
Companion docs:  `docs/J_pathwidth_dp.md`,
                 `docs/J_width_conjecture.md`,
                 `docs/forced_frontier_probe.md`.

## 1. Why the J-pathwidth DP is not polynomial

Recap of the prior agent's result (D66):

* `docs/J_width_conjecture.md` (D66): under Hall feasibility on
  score windows, `pw(J), tw(J) ≤ 8 + 2|H|`.
* `docs/J_pathwidth_dp.md`: the σ-on-bag DP runs in time
  `n^{O(1)} · S(w)` where `S(w) = (w+1)! · 3^{w+1} · Bell(w+1)` and
  `w` is the pathwidth of `J`.
* `docs/forced_frontier_probe.md` (D67): the naive
  "two endpoints per live H-component" compression of the forced
  frontier is exhausted on reversed-matching families
  (≈ `2|H|` even after compression).  Polynomial-time hopes from this
  side require either a global multiset quotient of many dormant
  components (the sister-agent's track) or a different state
  compression.

So the J-pathwidth DP is FPT in `|H|` but exponential when `|H| = Θ(n)`
(generic random tournaments at fixed flip-density `1/8`).

The full DP state per bag is `(σ, degree, comp)` with sizes
`(w+1)!`, `3^{w+1}`, `Bell(w+1)`.  Of these, `(w+1)!` *dominates* for
`w ≥ 5`.  Compressing only `Bell(w+1)` (the partition) saves at most a
constant factor over the dominant σ-permutation.  **This is the
fundamental cap on the present route's payoff for polynomial-time
hopes.**

We document the route anyway because:

1. The forest counter may turn out to be *all* the partition info that
   matters — a clean structural lemma in its own right.
2. The diagnostic clarifies whether the linear-forest constraint
   contributes anything beyond degree.
3. Composed with a *future* σ-compression (e.g., the dormant-matching
   quotient applied to σ on long H-paths), the partition compression
   could be a useful ingredient.

## 2. Candidate global counters

We instantiate three variants of the J-pathwidth DP, all with the same
σ and degree pieces, replacing `comp` differently.

### 2.1 Variant A — drop `comp`

State key: `(σ, deg)`.  No cycle detection at all.

This is the most aggressive: we test whether the degree constraint
alone is sufficient.  The acceptance condition becomes "max degree 2
on the loaded back-arc subgraph", without acyclicity.

A degree-2-bounded subgraph is a disjoint union of paths and cycles.
So Variant A over-accepts tournaments whose LFO back-arc graph has a
2-regular component (a directed even cycle, alternating with the LFO
orientation).  It is the cleanest baseline.

### 2.2 Variant B — replace `comp` by `(num_open_paths, num_deg1_bag)`

State key: `(σ, deg, num_open_paths, num_deg1_bag)`.

* `num_open_paths` = number of partition classes of the loaded
  back-arc forest that intersect the current bag (i.e. classes with
  ≥ 1 bag-vertex of positive degree).
* `num_deg1_bag` = number of bag vertices of degree exactly 1.

The auxiliary state value carries a full union-find on all vertices
seen so far; cycle checks during introduce use the auxiliary UF.  When
multiple state values map to the same key, the implementation keeps
the **first arrival** (deterministic but tie-break-dependent).

This is the "forest counter" candidate: the global statistics
sufficient to summarize the forest structure independent of which
specific bag-vertex pairs share a component.

### 2.3 Variant C — bag-vertex-only partition

State key: `(σ, deg, bag_partition)` where `bag_partition` labels each
bag vertex by the smallest bag-vertex in its loaded-edge component
(no forgotten-vertex labels).

Variant C is a sanity check.  It is structurally equivalent to the
full J-pathwidth DP (which already canonicalises by smallest-σ-rank
representative), so it must agree with `path_fas_J_pathwidth_dp` on
every input.

## 3. Empirical sufficiency results

All numbers via `scripts/global_counter_dp_probe.py` and
`tests/test_global_counter_dp.py`, seed `20260527`.

### 3.1 Variant A: collides as expected

| n  | trials                  | A vs BF agree |
|----|-------------------------|---------------|
| 3  | 8 exhaustive            | 8/8           |
| 4  | 64 exhaustive           | 64/64         |
| 5  | 1024 exhaustive         | 1024/1024     |
| 6  | 32768 exhaustive        | 32768/32768   |
| 7  | 500 random              | 492/500       |
| 7  | 20 minimal NO catalogue | 11/20         |

At `n ≤ 6`, no tournament's LFO admits an even-cycle back-arc graph
(the score-window-respecting LFOs at these sizes are forest already
under degree-2).  At `n = 7` Variant A wrongly accepts ≥ 8 random
instances and 9 of 20 minimal NO instances.  This is the expected
behavior — Variant A is too coarse.

### 3.2 Variant B: empirically sound across the test suite

| n  | trials                  | B vs BF agree |
|----|-------------------------|---------------|
| 3  | 8 exhaustive            | 8/8           |
| 4  | 64 exhaustive           | 64/64         |
| 5  | 1024 exhaustive         | 1024/1024     |
| 6  | 32768 exhaustive        | 32768/32768   |
| 7  | 2000 random             | 2000/2000     |
| 8  | 500 random              | 500/500       |
| 9  | 30 random               | 30/30         |
| 7  | 20 minimal NO catalogue | 20/20         |
| 7..11 | 2000 random-skew      | 2000/2000     |

Additionally:

* **Tie-break independence.**  Re-running Variant B with the
  *lex-min* vs *lex-max* partition signature as the tie-break (so the
  surviving state-value at each key differs) gives **identical**
  verdicts on 500 random n=7 instances and 200 random n=8 instances.
  This is consistent with — but does not prove — partition
  irrelevance.
* **Lossy vs full collapse.**  An augmented probe (
  `_variant_b_full_enum.py` in the temporary scratch) keeps **all**
  distinct partitions per `(σ, deg, num_open, num_deg1)` key and
  compared with the lossy variant on 300 random n=7 instances, 100
  random n=8, 40 random n=9, and 2000 random skew n=7..11.  The
  lossy collapse never disagrees with the full enumeration.
* **Diverse collapses do happen.**  The collapse-statistics probe
  found 158 cases at n=7 (over 200 trials) where two state values
  with the same Variant-B key had genuinely different bag-partition
  signatures.  So the lossy step is exercised — but the verdict
  remains correct.

We have not found a tournament at n ≤ 11 where Variant B disagrees
with the full DP or with brute force.

### 3.3 Variant C: matches full DP

| n  | trials                  | C vs BF agree |
|----|-------------------------|---------------|
| 3  | 8 exhaustive            | 8/8           |
| 4  | 64 exhaustive           | 64/64         |
| 5  | 1024 exhaustive         | 1024/1024     |
| 6  | 32768 exhaustive        | 32768/32768   |
| 7  | 200 random              | 200/200       |
| 7  | 20 minimal NO catalogue | 20/20         |

As expected — Variant C only changes how `comp` is *labelled*, not
what equivalence is recorded, so it is the same DP as
`J_pathwidth_dp` with smaller value-of-state objects.

## 4. Theoretical analysis

Variant B's empirical success is striking but the lossy step is
**not** unconditionally sound.  We give a hand-crafted potential
counter-scenario, then explain why it does not actually arise in
score-window tournaments.

### 4.1 The hand-crafted partition-irrelevance failure mode

Consider an abstract DP state at bag `B = {a, b, c, d}` with
σ = (a, b, c, d), `deg = (1, 1, 1, 1)`, `num_deg1_bag = 4`,
`num_open_paths = 2`.

Two consistent partitions with this profile are:

* `comp_1 = {{a, b}, {c, d}}`,
* `comp_2 = {{a, c}, {b, d}}`.

Now suppose a future introduce step adds a vertex `v` that must load
back-arcs to both `a` and `b` (so `v`'s degree becomes 2 with
neighbours `a, b`).  Then:

* In `comp_1`: `a, b` already share a path component.  Adding `{v, a}`
  and `{v, b}` would close `a - ... - b` via `v`, **creating a cycle**.
  INFEASIBLE.
* In `comp_2`: `a, b` are in different components.  Loading is
  SAFE.

So `comp_1` and `comp_2` extend differently — and Variant B keeps only
one.  If it kept `comp_1`, it wrongly rejects `T` when a valid LFO
exists.  If it kept `comp_2`, it accepts (correctly).

Variant B is therefore *not* automatically sound at the abstract
level.

### 4.2 Why the failure mode does not manifest empirically

Claim: in score-window tournaments under the J-pathwidth DP, the
partitions `comp_1, comp_2` of the previous subsection are **not both
reachable as different DP traces** with the same `(σ, deg, num_open,
num_deg1)`.

The intuition.  Within a bag B, the loaded-edge subgraph
**on bag-vertices only** is entirely determined by σ on B and the
J-edges among bag vertices: a J-edge `{u, v}` with `u, v ∈ B` is
loaded iff the T-arc between them points "backward" in σ.  So no DP
trace has freedom over bag-only loaded edges.

The only nondeterminism is *how forgotten vertices' σ-positions were
chosen at the time they were in the bag*, which controls which
forgotten ↔ bag-vertex edges were loaded and thus how forgotten
vertices link bag vertices via the partition.

In random instances at n ≤ 11, the empirical fact is: this residual
nondeterminism does **not** produce two different traces with the
distinguishing partition `comp_1` vs `comp_2`.  But we have **not
proved** this in general.

### 4.3 What a proof attempt would require

A clean partition-irrelevance lemma would have to say:

> **Lemma (conjectural).**  If two DP traces reach bag B with the same
> `(σ, deg, num_open, num_deg1)`, then for every bag-vertex pair `u, v`
> they place `u, v` in the same loaded-edge component or in different
> components consistently.

This is a strong "partition is determined by counters" claim, and the
hand-crafted abstract example of §4.1 violates it.  So the lemma can
only hold *modulo the score-window structure of feasible J-pathwidth
DP traces*.

We do not have a structural proof of this.  The closest argument is:

(i)  Loaded edges among bag vertices are σ-determined (no choice).
(ii) Loaded edges between bag and forgotten vertices were chosen at
     past introduce steps; their loadings are σ-determined relative
     to σ on the previous bag.
(iii) Forgotten ↔ forgotten loadings are similarly fixed.

So all loaded edges in the trace are forced by σ on the **entire
introduction sequence**, not just σ on B.

Two traces reaching the same (σ, deg, num_open, num_deg1) at bag B
must have produced the same σ on every preceding bag intersected
with each bag mass — except where forgotten vertices'
introduce-positions can differ.

A vertex `w` already forgotten was introduced at some earlier bag
`B_w`.  At that time, its σ-position relative to the *then-bag-mates*
was chosen.  Two traces could disagree on `w`'s σ-position relative to
some bag mate `m` if both were in `B_w` and `{w, m}` was a J-edge
**but**:

* If `{w, m}` is a J-edge and `w, m` are in some common bag, both must
  load the edge if backward, or not if forward.  The choice of σ
  controls which.  So different traces *can* differ on the σ-position
  of `w` relative to `m`, leading to a different loaded-edge set.

Hence different traces *do* reach (σ, deg, num_open, num_deg1) at bag
B with different partitions in principle.  The question is: which of
the four partition pairs distinguishable by `num_open, num_deg1` is
*realised* by the DP traces?

**Open structural question.**  Does the score-window DP have the
property that all realised traces at the same (σ, deg, num_open,
num_deg1) have the same partition class on each bag-vertex pair?
Empirically yes at n ≤ 11.  We do not have a proof.

### 4.4 Even if Variant B is sound, this does NOT yield Path-FAS ∈ P

Suppose the partition-irrelevance lemma were true.  The Variant B
state is then `(σ, deg, num_open, num_deg1)`.

Sizes per bag of width `w + 1`:

| component        | size |
|------------------|------|
| σ (permutation)  | (w + 1)! |
| deg              | 3^{w + 1} |
| num_open         | ≤ w + 1 |
| num_deg1_bag     | ≤ w + 1 |

Total: `(w + 1)! · 3^{w + 1} · (w + 1)^2`.

For `w = 8 + 2|H|` (the proved width bound), this is still
**super-exponential in `|H|`**.  At random-skew `|H| = Θ(n)`, the
state count is `Θ(n)! · 3^{Θ(n)}` — much larger than polynomial in
`n`.

The dominant factor is the σ permutation, NOT the partition.  Even
perfectly removing the partition piece (replacing `Bell(w + 1)` by
`(w + 1)^2`) saves at most a sub-exponential factor.

This is documented in §3.4 of `docs/J_pathwidth_dp.md` and confirmed
by the present analysis: **the σ-on-bag component is what blocks the
polynomial-time route.**

For Path-FAS ∈ P via the J-pathwidth DP, σ must be replaced by
something polynomial in `n`, OR the bag size itself must be O(log n).
Neither is achieved by the global-counter route.

## 5. Verdict

* **Variant A** (drop `comp`) over-accepts; documented failures at
  n = 7 minimal NO catalogue.  Refuted as a polynomial DP.

* **Variant B** (counter + auxiliary UF, lossy first-arrival
  collapse) is empirically sound on **every** test we ran:
  - 33800+ exhaustive instances at n ≤ 6,
  - 2530 random instances at n ∈ {7, 8, 9},
  - 20 minimal NO instances at n = 7,
  - 2000 random-skew instances at n ∈ {7, …, 11}.
  Tie-break independent (min vs max partition signature give the same
  answer in 700 tested instances).  Lossy vs full enumeration agree
  in 2440 tested instances.  But we have **not proved** soundness.

* **Variant C** (bag-vertex-only partition) is structurally
  equivalent to the full DP and passes all tests.

The most important honest finding: **even if Variant B is fully
sound, this does not give Path-FAS ∈ P.**  The dominant cost of the
J-pathwidth DP is the σ-permutation per bag, not the partition.
Compressing the partition saves at most a sub-exponential factor
(Bell(w+1) → polynomial in w), which is dominated by (w+1)! anyway.

A polynomial-time algorithm on random-skew tournaments
(`|H| = Θ(n)`, `pw(J) = Θ(n)`) requires compressing **σ itself** —
e.g., via the dormant-matching quotient lemma (sister-agent's track)
or a totally different state encoding.

## 6. Implications for Aboulker Problem 4.4

The global-counter route does **not** settle Problem 4.4.  The
findings are:

1. **No polynomial-time algorithm emerges.**  Even granting an unproved
   partition-irrelevance lemma, the σ-permutation dominates the cost.

2. **The forest constraint contributes more than degree.**  Variant A
   (drop comp, only degree) collides at n = 7.  So the linear-forest
   structure cannot be reduced to degree alone; **some** partition
   information is needed.

3. **An unexplained empirical regularity.**  Variant B passes every
   test despite being lossy.  Either:
   (a) The partition information beyond `num_open, num_deg1` is
       indeed structurally irrelevant in score-window tournaments
       (a strong but conceivable structural lemma we do not have);
   (b) The cases distinguishable by partition simply do not arise at
       the small n we tested, and Variant B will fail at larger n /
       higher pathwidth.

   Direct disambiguation requires either:
   - A theoretical proof of the partition-irrelevance lemma, OR
   - An adversarial tournament at larger n with pathwidth ≥ 10
     and matching pattern stressing the multi-load scenario, plus a
     way to certify the brute-force verdict.

4. **Combination potential.**  Variant B's partition compression
   composes with any future σ-compression.  If the
   dormant-matching-quotient lemma succeeds, Variant B might give an
   additional constant-factor savings on the resulting DP.

5. **Negative diagnostic for orthogonality.**  Our route was meant to
   be orthogonal to the dormant-matching-quotient direction.  Both
   share the same bottleneck (σ permutation), so neither alone
   suffices.  A polynomial algorithm needs *both* a σ-compression
   AND a partition-compression simultaneously.

### Decisive verdict

> **The LFO forest-constraint route compresses the per-bag partition
> piece of the J-pathwidth DP from `Bell(w+1)` to a polynomial in `w`,
> EMPIRICALLY soundly at n ≤ 11 (proof open).  But the σ-permutation
> piece — `(w+1)!` per bag — is unchanged, so the resulting DP is no
> closer to polynomial in `n` than the original.  Path-FAS ∈ P is
> NOT settled by this route.**

A theorem-grade reading: the forest-counter route refutes the
*partial* hope that comp-compression alone could yield polynomial
time.  It does not refute Path-FAS ∈ P, but it relocates the
obstruction firmly to the σ piece.

## 7. Reproduction

```bash
# Smoke (small) — Variants A, B, C exhaustive at n=4..5
uv run python problems/path_matching_fas/scripts/global_counter_dp_probe.py \
  --all-variants --n 4 --exhaustive

uv run python problems/path_matching_fas/scripts/global_counter_dp_probe.py \
  --all-variants --n 5 --exhaustive

# Single-variant random samples
uv run python problems/path_matching_fas/scripts/global_counter_dp_probe.py \
  --variant B --n 7 --count 2000

# Full pytest harness
uv run python -m pytest problems/path_matching_fas/tests/test_global_counter_dp.py -v

# All-variants × all-n grid (slow: ~3 min)
uv run python problems/path_matching_fas/scripts/global_counter_dp_probe.py --all-n
```

All scripts use the project's `uv`-managed virtualenv with
`networkx == 3.6.1`.

## 8. Citations

* Aboulker, P., Aubian, G., Charbit, P., Lopes, R., *Finding
  forest-orderings of tournaments is NP-complete*, arXiv:2402.10782
  (2024).  Problem 4.4 is the open Dec-Path-FAS question.

* Coppersmith, D., Fleischer, L., Rurda, A., *Ordering by Weighted
  Number of Wins Gives a Good Ranking for Weighted Tournaments*, ACM
  Trans. Algorithms 6(3), Article 55 (2010),
  doi:[10.1145/1798596.1798608](https://doi.org/10.1145/1798596.1798608).
  Source for the score-window / backdegree-2 reading.

* Bodlaender, H.L., Cygan, M., Kratsch, S., Nederlof, J.,
  *Deterministic single exponential time algorithms for connectivity
  problems parameterized by treewidth*, Inf. Comput. 243 (2015),
  86–111, doi:[10.1016/j.ic.2014.12.008](https://doi.org/10.1016/j.ic.2014.12.008).
  The "rank-based approach": compresses partition-state from
  `Bell(w)` to `2^O(w)`.  Confirms the partition piece is reducible to
  single-exponential, but does not affect the σ piece.

* Bodlaender, H.L., *Discovering treewidth*, SOFSEM 2005,
  doi:[10.1007/978-3-540-30577-4_1](https://doi.org/10.1007/978-3-540-30577-4_1).
  Min-fill-in / min-degree heuristics underlying the empirical
  pathwidth measurements in `docs/J_width_conjecture.md`.
