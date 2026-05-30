# D68: Dormant-Matching Quotient Lemma — refuted

## Verdict, up front

The Dormant-Matching Quotient Lemma, in its natural multiset
formulation, is **refuted** by a minimal collision on the `one_block`
tournament at n = 12.

> **Refutation.**  There exist a tournament `T` (the `one_block`
> template, n = 12, Hall-feasible, H a 2-edge matching) and two valid
> length-5 prefixes `(0, 3, 1, 4, 2)` and `(1, 2, 0, 4, 3)` such that
>   * they have identical augmented signature (visible-latent on the
>     active band plus the multiset aggregate over dormant H-components),
>   * but `(0, 3, 1, 4, 2)` does *not* extend to a Path-FAS-feasible
>     LFO, while `(1, 2, 0, 4, 3)` does.
> The root cause is the union-find component partition on the loaded
> backedges: in the first prefix the dormant pair `{0, 10}` is in the
> same component as active vertex 4, whereas in the second the two
> dormant pairs `{0, 10}` and `{1, 9}` are in a common component
> separate from 4.  No multiset of local (type, degree, ports) tuples
> can witness that distinction.

Consequence:
  * The FPT-by-`|H|` theorem from D66 remains intact (it does not rely
    on the quotient lemma).
  * The naive "polynomial-size aggregate over dormant H-components"
    compression cannot reduce the `8 + 2|H|` bound to anything depending
    only on the active band and a multiset count.
  * The minimal collision pair on `one_block` is the natural substrate
    for the next NP-hardness attempt: it shows that the global
    union-find structure linking dormant H-components to the active
    band carries information that cannot be summarized locally.

The implementation is in
[`scripts/dormant_quotient_probe.py`](../scripts/dormant_quotient_probe.py)
and the pinned regression tests in
[`tests/test_dormant_quotient.py`](../tests/test_dormant_quotient.py).

---

## 1. Precise statement of the lemma

Let `T` be a tournament with Hall-feasible score windows of radius 2,
let `H` and `G_flex` be its forced-backedge and flexible graphs (see
`docs/J_width_conjecture.md` §1), and let `J = H ∪ G_flex`.  For a
valid prefix `σ_prefix = (v_0, ..., v_{p-1})` of a hypothetical LFO of
`T`, define at sweep position `p`:

* **active band**: `A_p = { v ∈ V(T) : lo_v ≤ p ≤ hi_v }`, where
  `[lo_v, hi_v]` is the score window of `v`.
* **closed**: vertices with `hi_v < p` (their window ended; in a
  valid prefix they have been placed).
* **future**: vertices with `lo_v > p` (not yet placed; their window
  starts after `p`).
* a **dormant H-component** of the prefix is a connected component `C`
  of the underlying undirected graph of `H` such that
    1. `C ∩ A_p = ∅` (no vertex of `C` lies in the active band),
    2. `C` has at least one closed and one future vertex.
  Equivalently, `C` "straddles" the sweep without intersecting it.

The forced backedges of `H` are pre-loaded at initialization
(`_initial_forced_state` in `lfo_forced_flexible.py`), so every
H-edge contributes one unit of loaded-back-edge degree to each of its
endpoints; the union-find partition merges endpoints of every
H-edge.  By the time the sweep reaches position `p`, the closed
endpoint of a dormant H-edge has been placed in the prefix, but the
union-find component of that edge persists.

**Dormant-Matching Quotient Lemma (proposed, refuted below).**  Fix `T`
and define the **local profile** of a dormant H-component `C` at
position `p`:

    profile(C; p) = (
        type(C),                                # canonical iso type
        sorted [ (status(v), deg(v), ports(v)) for v in C ],
    )

where
  * `type(C)` is a canonical encoding of the H-component's shape
    (currently the sorted tuple of H-degrees of its vertices; for a
    matching edge this is `(1, 1)`);
  * `status(v) ∈ {"closed", "future"}`;
  * `deg(v)` is the current loaded-back-edge degree of `v` (already
    including the H-edge);
  * `ports(v)` is the sorted set of *positions in the active band* `A_p`
    (canonicalized as indices `0, 1, …, |A_p| − 1` into the sorted
    list of active vertices) to which `v` could attach via a flex edge.

Define the **dormant aggregate** at position `p` as the multiset of
all dormant profiles:

    agg(σ_prefix; p) := multiset { profile(C; p) : C dormant H-component }.

The proposed lemma is:

> **Lemma (refuted).**  For two valid prefixes `σ_A`, `σ_B` of length
> `p` with the same active-band-local state (i.e., the same
> visible-latent signature, see `ff_signature_probe.py`) and the same
> dormant aggregate `agg(σ_A; p) = agg(σ_B; p)`, the two prefixes have
> the same Path-FAS extendability: both extend to an LFO or neither
> does.

The lemma asserts that dormant H-components are *interchangeable as a
multiset*; their individual identities, beyond `(type, state, ports)`,
do not affect extendability.

The polynomial-size bound is the obvious upshot.  By Hall feasibility
`|A_p| ≤ 9`, so per dormant profile the (type, state, ports) tuple has
at most `O(1) × 9 × 2^9 ≈ 4600` possible values.  The aggregate is then
a multiset of size at most `|H|` over an alphabet of size `O(1)`, with
total information content `O(|H| · log |H|)`.  Combined with the
visible-latent signature (whose state space is at most polynomial in
`n`), the augmented signature would have polynomial size — and the
DP state would no longer carry the `2|H|` endpoint blow-up.

---

## 2. Aggregate signature: precise definition

`scripts/dormant_quotient_probe.py` implements
`dormant_components_at(T, pos, prefix, radius=2)` returning a list of
profile dicts in the form

```
{
    "type": (1, 1),                     # for a matching edge
    "vertices_state": (
        ("closed", deg_closed, ports_closed),
        ("future", deg_future, ports_future),
    ),
}
```

with `ports_*` a sorted tuple of indices into the sorted active band.

The function `aggregate_signature(profiles)` returns a sorted tuple of
`(type, vertices_state)` pairs — a canonical hashable form of the
multiset.

The function `augmented_signature(T, prefix)` returns a tuple
`(visible_latent_signature(...), aggregate_signature(...))` which is
the natural extension of the visible-latent DP signature
(`ff_signature_probe.py`).

Note the careful canonicalization:

* `ports` are encoded as *positional indices* into the active band, not
  global vertex labels.  This is necessary to give the aggregate any
  hope of being polynomial-size: two dormant components whose ports
  point to the same active-band slots but to "different" active vertices
  by global label would otherwise have different aggregates.  With
  positional canonicalization, the aggregate is invariant under any
  relabelling that preserves the active band's position structure.
* `vertices_state` for each profile is sorted to make the profile
  label-invariant within a component.
* The aggregate is sorted to make it multiset-invariant across
  components.

This is the strongest natural multiset signature: it uses the active
band's positional skeleton to anchor the dormant components, but does
not distinguish components beyond their per-vertex profiles.

---

## 3. Empirical probe results

### 3.1 Reversed-matching family: no collisions

The script searches for two distinct valid prefixes of length `p`
that share their augmented signature but have different `has_completion_ff`
verdicts.  We restrict to prefixes where at least one dormant
H-component is present (otherwise the lemma is vacuous).

For the reversed-matching family `T_m` on `n = 2m` vertices, the full
sweep search at every dormant-rich position `p ∈ [4, m]` and `m ∈
{10, 11, 12}` finds **no collision**:

| `m` | `p` | dormant-prefix count | augmented classes | result |
|----:|----:|---------------------:|------------------:|-------:|
| 10  |  4  | 12                   | 12                | OK     |
| 10  |  5  | 20                   | 19                | OK     |
| 10  |  6  | 33                   | 31                | OK     |
| 10  |  7  | 54                   | 50                | OK     |
| 10  |  8  | 142                  | 130               | OK     |
| 10  |  9  | 502                  | 460               | OK     |
| 10  | 10  | 1393                 | (large)           | OK     |
| 11  |  6  | 33                   | 31                | OK     |
| 11  |  8  | 88                   | 80                | OK     |
| 11  | 10  | 816                  | (large)           | OK     |
| 12  |  6  | 33                   | 31                | OK     |
| 12  | 12  | 3668                 | (very large)      | OK     |

In each row, the augmented signature is collision-free: no two valid
length-`p` prefixes sharing it have differing extendability.

Notice the augmented signature does *more* work than the visible-latent
signature on this family: visible-latent alone has very few classes
(e.g., 12 at `m = 12, p = 8`).  Even so, this is consistent with the
lemma on the reversed-matching family, because every prefix in a
visible-latent class has the same extendability.  So the reversed
matching is a *clean* family — it is not a refuter.

### 3.2 The `one_block` collision is a true refuter

The `one_block` tournament from `sleeping_block_skew_sweep.SKEW_TEMPLATES`
(used since `docs/exchange_proof_draft.md` to refute every previously
proposed local DP) is the canonical small (n = 12) hard instance.

At `p = 5` (active band `{4, 5, 6, 7}`, dormant pairs `{0, 10}` and
`{1, 9}`), the augmented signature partitions valid prefixes into 22
classes.  Among these classes, **4 contain prefixes of differing
extendability**.  The minimal collision pair is

    A = (0, 3, 1, 4, 2)   — NOT extendable
    B = (1, 2, 0, 4, 3)   — extendable

Both share

    augmented_signature = (
      visible_latent: (5, (4,5,6,7), (4,), …, …, …),
      dormant_aggregate: (
        ((1, 1), (("closed", 2, (0,1,2)), ("future", 1, (0,1,2,3)))),
        ((1, 1), (("closed", 2, (0,1,2)), ("future", 1, (0,1,2,3)))),
      ),
    )

(They have identical dormant profiles: each is a matching edge with
closed-degree 2, future-degree 1, and the *same* port positions in the
active band.)

But their **union-find component partitions on the loaded backedges**
differ:

    Prefix A components:
      {0, 2, 4, 10}     ← dormant {0,10} merged with active 4 and closed 2
      {1, 3, 9}         ← dormant {1,9} merged with closed 3 only
    Prefix B components:
      {0, 1, 9, 10}     ← dormants {0,10} and {1,9} merged together
      {2, 3, 4}         ← active 4 and closed 2, 3 separate from dormants

This *global merge structure* is what the dormant aggregate cannot
see, and it is exactly what determines whether the prefix extends.

The minimality of this collision is supported by random sampling: in
250 random skew tournaments at n ∈ {8, ..., 12} with various flip
counts and seeds, no collision was found at smaller n.  The
`one_block` collision at n = 12 is therefore the smallest documented
refuter; while we did not exhaustively search every tournament at
n ≤ 12 (about 2 × 10⁶ tournaments at n = 11, 10⁹ at n = 12), it would
take substantially more compute to claim n = 12 is minimal in the
exhaustive sense.  The combinatorial structure
(two-component dormant matching collapsing through an active port) is
clean enough to suggest n = 12 is genuinely tight.

### 3.3 The augmented signature is strictly finer than visible-latent

The `one_block` collision is *not* an artefact of visible-latent
already being collision-vulnerable.  Both prefixes have the same
visible-latent signature *and* the same dormant aggregate, so even the
finer augmented signature fails to distinguish them.

On the `one_block` n = 12 instance at p = 5:

  * 93 total valid prefixes,
  * 9 visible-latent classes (2 of which are ext-collided),
  * 22 augmented classes (4 of which are ext-collided).

The augmented signature is strictly finer (refines vis-latent classes)
but still insufficient.

### 3.4 Reproduction

```bash
uv run python scripts/dormant_quotient_probe.py \
    --family reversed_matching --m-range 8,9,10,11,12 --depth 6

uv run python scripts/dormant_quotient_probe.py \
    --family random_skew --n-range 16,20,24 --depth 6

uv run python scripts/dormant_quotient_probe.py \
    --T "$(cat scripts/_one_block.json)"   # if exported

uv run pytest tests/test_dormant_quotient.py -v
```

---

## 4. Theoretical proof attempt — why it fails

### 4.1 The natural permutation-of-identities argument

The clean proof attempt for the lemma proceeds as follows.

> **Attempted proof.**  Let `σ_A` and `σ_B` be valid length-`p`
> prefixes with the same augmented signature.  By the multiset
> equality of dormant aggregates, there is a bijection `Φ` between the
> dormant H-components of A and those of B that preserves
> `(type, state, ports)`.  For any completion `τ_A` of `σ_A` to a full
> LFO, define `τ_B` by following `τ_A` step-by-step:
>
>   - Active-band steps: track the active-band state which matches
>     between A and B by assumption.
>   - Steps placing a vertex from a dormant component: if `τ_A` places
>     `v` from dormant component `C_A`, place the corresponding vertex
>     `Φ(v) ∈ Φ(C_A)` in `τ_B`.
>
> Then `τ_B` is a valid completion of `σ_B`.  ∎

This argument has a **fatal gap**: the bijection `Φ` between dormant
components is a *local* relabeling, but the global linear-forest
constraints (degree ≤ 2 everywhere, no cycle in the entire back-arc
graph) are not local.  Specifically:

  * When two distinct dormant components `C, C'` in prefix A are
    independent (different roots in the union-find), placing a flex
    backedge in the completion that links them creates one larger
    component — fine.
  * But if in prefix B those same two dormant components are *already
    merged* (same root), then any flex backedge from the active band
    that *would* link `Φ(C)` to `Φ(C')` *creates a cycle in B*, even
    though it does not create a cycle in A.

The bijection `Φ` cannot fix this: it works at the level of dormant
components individually, but the global merge structure (encoded by
the root labels of dormant vertices in the union-find) is not part of
the aggregate.

### 4.2 The collision precisely exhibits this gap

The `one_block` collision shows the failure in its cleanest form.  In
prefix A, dormant component `{0, 10}` is glued to the active vertex 4
(through a chain of flexible loaded backedges that the active 4
participates in), while the other dormant `{1, 9}` is not.  In prefix
B, the two dormant components are glued to each other, but neither is
glued to active 4.

Now, the future flex-edge choices ahead include a flex edge between
the active vertex 4 and one of the dormant vertices (say 9 or 10),
loaded when that dormant vertex is finally introduced.  In prefix B
this flex edge merges the {0, 1, 9, 10} component with active 4,
yielding a 5-vertex linear-forest path that is still a valid linear
forest.  In prefix A this same flex edge would attempt to merge
{0, 4, 10, 2} with `{1, 9}` through the active vertex 4 — but if a
*second* flex edge then also tries to merge things, a cycle appears.

The empirical refutation matches: B extends, A does not.

### 4.3 What would a correct lemma look like?

A correct quotient lemma would have to record, per dormant component
`C`, not just `(type, state, ports)` but also the **canonicalized
union-find root label** that links `C` to the rest of the state.
Explicitly:

  * partition `V(T) \ A_p` into union-find roots,
  * for each dormant component `C`, record the root containing it
    (canonicalized — say by sorting roots by their minimum active-band
    representative, treating roots without any active representative
    as fresh anonymous labels).

This is equivalent to keeping the full union-find partition's
restriction to *dormant vertices plus a representative of each active
component they touch* — i.e., the same information the J-pathwidth DP
already keeps in its `comp` field.  So the "polynomial-size aggregate"
ambition is incompatible with the global linear-forest constraint.

In particular, the aggregate must distinguish dormant components that
sit in different active-anchored components — and the number of such
distinct "anchored-partition" classes per active band of size `≤ 9` is
at most Bell(9) = 21147.  This is polynomial in `n`, **but only if we
treat the active-band component partition as the anchor**, i.e., the
J-pathwidth DP state is unchanged.  The aggregate then becomes
"multiset of (type, state, ports, anchor-class)" which is just
"per-anchor-class count of dormant profiles".

That is a polynomial aggregate, but it is **not** the bare multiset of
local profiles — it inherits the active-band partition's complexity.
We have not refuted this *anchor-augmented* aggregate; the next probe
should test it explicitly.

### 4.4 Honest status of the proof attempt

The permutation-of-identities proof has a documented fatal gap.  The
gap is **not** a technical inconvenience: the `one_block` collision
realises it as a concrete obstruction.  The natural fix
(anchor-augmented aggregate) does not satisfy the lemma's
"individual identities replaced by polynomial-size aggregate" slogan,
because the anchor labels are *not* polynomial in `|H|` alone; they
depend on the active-band partition, which itself can have up to
Bell(9) ≈ 2 × 10⁴ classes.

So there is no proof of the lemma as stated.

---

## 5. Decisive verdict — refuted

| claim | status |
|---|---|
| Dormant aggregate (multiset of (type, state, ports)) determines extendability, given visible-latent state | **REFUTED** by `one_block`, n=12, p=5 |
| Anchor-augmented aggregate (with active-band partition labels) determines extendability | **OPEN** (not refuted, not proved; future work) |
| FPT-by-`|H|` theorem (D66) remains valid | unchanged |
| Reversed-matching family is not the refuter | confirmed empirically (no collision in 100s of probes) |
| The collision substrate is the `one_block` active-active-port + dormant-merge interaction | confirmed |

The minimal collision is logged in
`tests/test_dormant_quotient.py::test_one_block_collision_*` for
regression purposes.

---

## 6. Implications

### 6.1 For the FPT-by-`|H|` algorithm

No change: the FPT-by-`|H|` theorem follows from the proved bound
`pw(J), tw(J) ≤ 8 + 2|H|` and the σ-on-bag DP (`J_pathwidth_dp.py`),
neither of which depend on a dormant quotient.  The algorithm remains
correct, and Path-FAS remains polynomial on every tournament class
with `|H| = O(log n)`.

### 6.2 For Aboulker Problem 4.4 (Path-FAS on general tournaments)

The naive route "augment the visible-latent DP with a dormant
multiset aggregate" is closed.  Two directions remain:

  * **(positive)** Test the **anchor-augmented** aggregate.  This would
    be a sound DP state if and only if it is fine enough to detect
    every visible-latent collision *that has identical anchored
    dormant aggregate*.  No theoretical reason to expect it to fail,
    but no proof either.  At a minimum, it would replace `2|H|` with
    a per-anchor-count summary, which on random-skew tournaments
    grows much slower (anchor count is at most Bell(9), the dormant
    count grows linearly).  Polynomial only if the active-band
    partition is bounded.
  * **(negative)** The `one_block` collision is the natural substrate
    for a hardness reduction.  Specifically, the structure
    "dormant matching pair whose component-merge with active vertices
    differs across prefixes" can probably encode the disjoint-paths
    problem or 3-COLOURABILITY.  Concretely, an instance with `k`
    such dormant matchings, each independently choosable to merge
    with one of two specific active vertices, gives `2^k` reachable
    augmented signatures — but if extendability depends on a global
    parity, the gadget could be the substrate for an NP-hardness
    reduction.

The next round's mathematical target is therefore either:

  1.  Implement the anchor-augmented aggregate, search for refuters,
      and either prove correctness or document the next collision.
  2.  Extract a clean gadget from the `one_block` collision and study
      it as a candidate variable gadget for SAT-to-Path-FAS reduction.

### 6.3 Honest assessment

The Dormant-Matching Quotient Lemma, as posed, is refuted.  The
refutation is small, clean, and structurally informative: it points to
the **global union-find partition** as the irreducible piece of state
that any sound DP must keep.  This is consistent with the broader
picture from `docs/exchange_proof_draft.md`: every weaker DP state
(active-only, visible-latent, sleeping-block, half-block-parity) was
refuted by collisions in the n = 12 skew templates; the dormant
aggregate is one more such projection, and it falls to the same
collision.

The FPT-by-`|H|` theorem is the right level of generality the current
toolkit can prove.  Pushing beyond it requires either a richer DP
state (anchor-augmented) or a hardness route through gadgets seeded by
the `one_block` collision.

---

## 7. Files / Artifacts

  * [`scripts/dormant_quotient_probe.py`](../scripts/dormant_quotient_probe.py)
    — implementation of `dormant_components_at`, `aggregate_signature`,
    `augmented_signature`, and `find_collision`.  CLI runner for the
    reversed-matching and random-skew families.
  * [`tests/test_dormant_quotient.py`](../tests/test_dormant_quotient.py)
    — 15 regression tests pinning the empirical no-collision on
    reversed-matching m ∈ {8..12} and the refuting collision on
    `one_block` n = 12.
  * [`docs/forced_frontier_probe.md`](forced_frontier_probe.md) §4 —
    the original lemma statement and the family of obstructions it was
    designed to defuse.
  * [`docs/J_width_conjecture.md`](J_width_conjecture.md) — the proved
    `pw(J), tw(J) ≤ 8 + 2|H|` theorem (still valid).
  * [`docs/J_pathwidth_dp.md`](J_pathwidth_dp.md) — the σ-on-bag DP
    whose state space is what any dormant quotient was hoping to
    compress.
  * [`docs/exchange_proof_draft.md`](exchange_proof_draft.md) §14.2 —
    documents the `one_block` collision pair `(0, 1, 2, 5, 3)` vs
    `(1, 2, 0, 5, 3)` and the family of weaker DP refutations.

## 8. Citations

  * Aboulker, P.; Aubian, G.; Charbit, P.; Lopes, R.  *Finding
    forest-orderings of tournaments is NP-complete*.  arXiv:2402.10782
    (2024).  Source of Problem 4.4.
  * Coppersmith, D.; Fleischer, L.; Rurda, A.  *Ordering by Weighted
    Number of Wins gives a Good Ranking for Weighted Tournaments*.
    ACM Trans. Algorithms 6(3), Article 55 (2010).
    doi:[10.1145/1798596.1798608](https://doi.org/10.1145/1798596.1798608).
    Source of the score-window theorem (radius-2 LFO localization).
  * Bodlaender, H. L.  *Discovering Treewidth*.  SOFSEM 2005.
    doi:[10.1007/978-3-540-30577-4_1](https://doi.org/10.1007/978-3-540-30577-4_1).
    Background on treewidth measurement.
