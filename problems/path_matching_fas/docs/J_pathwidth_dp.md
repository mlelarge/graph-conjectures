# Path-FAS DP on a path decomposition of J = H ∪ G_flex

This note specifies and tests a path-decomposition dynamic program
for the formal Path-FAS decision problem (Aboulker–Aubian–Lopes
Problem 4.4) on a general tournament `T`.

Implementation: `scripts/J_pathwidth_dp.py`
Tests: `tests/test_J_pathwidth_dp.py`, `scripts/J_pathwidth_dp_probe.py`

## 1. The interaction graph J

Fix a tournament `T` on vertex set `V = [n]` with score window
`I_v = [d^-(v) - 2, d^-(v) + 2]` for each vertex `v` (the
necessary-position interval; see `docs/score_window.md`).

For every unordered pair `{u, v}`:

- **Forced pair.** `I_u` and `I_v` are disjoint; then every LFO must
  place them in the unique order consistent with the windows.  If the
  T-arc agrees with that forced order, no backedge is contributed; if
  the T-arc disagrees, the pair contributes a *forced backedge* in
  every LFO.  The set of forced-backedge pairs is the
  **forced backedge graph H**.
- **Flexible pair.** `I_u ∩ I_v ≠ ∅`.  The LFO is free to choose the
  relative order of `u` and `v`; the T-arc becomes a backedge in one
  of the two orders and a forward arc in the other.  All such pairs
  form the **flex graph G_flex**.

The **interaction graph** is `J(T) := H ∪ G_flex` on the same vertex
set.  By construction:

> Every pair `{u, v}` that *could* be a backedge in some
> score-window-respecting LFO is an edge of `J(T)`.

Equivalently, if `{u, v} ∉ J(T)`, then either the LFO direction
between `u` and `v` is forced and the T-arc agrees with it
(forward arc, never a backedge), or they are forced with the T-arc
disagreeing (forced backedge, an H-edge).  In particular, every
T-arc that *can* be a back-arc under some LFO lives between J-adjacent
vertices.

## 2. The DP

### 2.1 State

Given a (nice) path decomposition `B_0, ..., B_t` of `J`, the DP
maintains at each bag `B_i` the set of reachable states

```
state = (sigma, degree, comp)
```

where

- `sigma`: a tuple giving the **LFO order** restricted to `B_i`
  (a linear order on the bag vertices);
- `degree`: per bag-vertex, current loaded-backedge degree
  in `{0, 1, 2}` (residual capacity = `2 - degree`);
- `comp`: the union-find partition on bag vertices induced by the
  already-loaded backedges (which bag vertices are in the same
  loaded-backedge component).

Canonicalization: `comp` is relabeled so each class's representative
is the bag vertex with the *smallest σ-rank* in that class.  The
signature `(sigma, degree, comp)` is hashable.

### 2.2 Transitions

Nice path decompositions have only two transition kinds:

- **Introduce v.**  `B_{i+1} = B_i ∪ {v}` with `v ∉ B_i`.  We
  enumerate every admissible σ-position for `v`:
  - For each existing bag-mate `u`, we enforce the **forced
    inequality** `must_precede(v, u)` (windows force `v < u`) or
    `must_precede(u, v)` — these positions are eliminated.
  - For each remaining σ-position, we then check every `J`-edge
    `{v, u}` with `u ∈ B_i`: the T-arc between `v` and `u` is a
    backedge under σ iff it points "backwards" in σ.  If so, **load**
    the edge: bump degrees of both endpoints, union components, check
    degree ≤ 2 and acyclicity (rejecting the state on violation).

- **Forget v.**  `B_{i+1} = B_i \ {v}`.  Drop `v` from σ, `degree`,
  `comp`.  By the path-decomposition invariant, `v` has no `J`-edge
  to any vertex of any future bag, so its degree/component is now
  final.

### 2.3 Acceptance

At the final empty bag `B_t = ∅`, every vertex has been
introduced and forgotten exactly once.  Any state surviving to this
point witnesses a *consistent* assignment of relative orders to all
J-edges, equivalent to an LFO whose back-arc graph is loaded entirely
on J and has all degrees ≤ 2 and no cycles — i.e. a linear forest.
Therefore the DP returns `True` iff `T` admits a formal Path-FAS.

### 2.4 Correctness theorem (sketch)

**Theorem.**  Let `T` be a tournament and `(B_0, ..., B_t)` a path
decomposition of `J(T)`.  Then the DP defined above returns `True` iff
`T` admits a Path-FAS.

*Soundness.*  Suppose a state `(sigma, degree, comp)` survives at
`B_t = ∅`.  Walk back through the transition log to assemble a total
order `pi` of `V(T)` (extending σ as it grew).  Every J-edge `{u, v}`
was processed once, when both `u` and `v` were in some bag together
(by the path-decomposition property), and the load/no-load decision
was made consistently with their σ-ranks at that moment.  Since
σ-ranks are append-only on σ's relative order (introduce never
changes existing σ-pairs, forget never changes anything), the final
linear order pi induces the same backedge graph that was loaded by
the DP.  The DP maintained degree ≤ 2 and acyclic-component
invariants, so the back-arc graph under pi is a linear forest.  All
non-J pairs are either forward (forced + T-arc agrees) or forced
backedges (forced + T-arc disagrees) — both kinds are correctly
accounted for, the forced backedges being H-edges of J.
[The forced inequalities ensure `pi` respects the score windows; the
remaining linear-extension freedom is irrelevant because non-J pairs
contribute no backedge dependence.]

*Completeness.*  Conversely, suppose `T` has a Path-FAS witnessed by
LFO `pi^*`.  For each bag `B_i`, set `sigma := pi^*` restricted to
`B_i` (i.e. the relative σ-order from `pi^*`), `degree` = current
loaded-backedge degree of bag vertices under `pi^*`, `comp` =
loaded-backedge components.  This state is reachable by the DP via
the transition log built from `pi^*` itself.  At `B_t = ∅` the state
is trivially the accepting empty state.  □

## 3. Runtime

### 3.1 Per-bag state count

At bag size `w + 1 = |B_i|`:

- σ ranges over permutations of `B_i`:   `(w + 1)!`
- `degree` ranges over `{0, 1, 2}^{w + 1}`:   `3^{w + 1}`
- `comp` ranges over partitions of `B_i`:   `Bell(w + 1)`

Naive upper bound on per-bag state count:
`S(w) := (w + 1)! · 3^{w + 1} · Bell(w + 1)`.

For small `w`:

| `w` | `(w+1)!` | `3^(w+1)` | `Bell(w+1)` | `S(w)` |
|----:|---------:|----------:|------------:|-------:|
|   2 |       6  |        27 |          5  |    810 |
|   3 |      24  |        81 |         15  |  29160 |
|   4 |     120  |       243 |         52  |   1.5M |
|   5 |     720  |       729 |        203  |   107M |
|   6 |    5040  |      2187 |        877  |   9.7G |
|   7 |   40320  |      6561 |       4140  |   1.1T |
|   8 |  362880  |     19683 |      21147  | 151T   |

In practice the survival rate is far below `S(w)`; the constraints
(degree ≤ 2, acyclic, forced inequalities, and J-edge loadings)
prune nearly all of these.  On the n ≤ 9 random samples we measured
end-to-end DP times of milliseconds (Section 5).  But the **bound is
exponential in `w`**, so the DP is polynomial in `n` only for
*bounded* `w`.

### 3.2 Width theorem and FPT consequence

The old constant-width hope is false as a general route.  The correct
statement is the refined bound proved in `docs/J_width_conjecture.md`
and encoded in `scripts/interaction_graph.py`:

> If the score windows are Hall-feasible and H has h forced-backedge
> arcs, then
> \[
>   \operatorname{pw}(J),\operatorname{tw}(J)\le 8+2h .
> \]

Proof in one line: the flexible graph is a Hall-bounded interval graph
with pathwidth at most 8; adding all endpoints of H to every interval
bag covers the forced edges and increases width by at most
`2|H|`.

Therefore this DP gives a genuine partial algorithm:

> **FPT-by-|H| theorem.**  Path-FAS on tournaments is decidable in
> time
> \[
>   n^{O(1)}\cdot S(8+2|H|)
> \]
> where \(S(w)=(w+1)!\,3^{w+1}\,\mathrm{Bell}(w+1)\).
> In particular, the problem is polynomial on every class with
> bounded \(|H|\), and fixed-parameter tractable parameterised by
> \(|H|\).

This theorem is deliberately weaker than a polynomial-time algorithm
for arbitrary tournaments.  Random-skew instances have \(|H|=\Theta(n)\),
so the bound becomes exponential there.

### 3.3 Pathwidth of J in practice

Empirically (`flex_graph_treewidth.py`, `interaction_graph.py`, and
direct measurement here):
- n = 12 skew templates: our heuristic produces path-decomp width
  `7, 9, 6` on `one_block`, `skew_induction`, `wake1_failure`
  respectively (an upper bound; min-fill-in `tw` was 6, 8, 5).
- n random-skew tournaments: `pw(J)` / `tw(J)` grows with the number
  of forced backedges.  The refined theorem explains this as an
  \(|H|\)-dependence, not as a mysterious flexible-graph phenomenon.
- minimal NO tournaments at n ≤ 9 have H empty or tiny but dense
  flexible graphs, so their J-width is near n at these small sizes;
  they do not contradict the FPT-by-|H| theorem because n itself is
  small in that catalogue.

### 3.4 Dominant state component

Per the table in §3.1, `(w+1)!` dominates `Bell(w+1)` for `w ≥ 5`
(since `Bell(k) ≈ k!/(ln(k))^k`).  The expensive piece is the σ
permutation — i.e., **the LFO order on bag vertices**.  This is the
correct piece to attack:

- It might be reducible to an equivalence class — two σ that agree on
  the forced inequalities and on every J-edge's load status are
  interchangeable.  But the load status itself is a function of σ, so
  the equivalence-class quotient is not obviously smaller.
- One could collapse σ to its "level-set decomposition" along the
  forced partial order's antichains.  Untested.

The next-largest piece is `3^{w+1}` for degrees.  This is a hard
floor because the linear-forest condition cares about every degree.

## 4. Empirical correctness results

All tests use `uv run pytest` with seed `20260527`.

| Setting              | Tournaments | DP ≡ BF |
|----------------------|------------:|--------:|
| exhaustive n = 3     |           8 |     8/8 |
| exhaustive n = 4     |          64 |   64/64 |
| exhaustive n = 5     |        1024 | 1024/1024 |
| exhaustive n = 6     |       32768 | 32768/32768 |
| random n = 7         |        2000 | 2000/2000 |
| random n = 8         |         100 | 100/100 |
| random n = 9         |          30 |   30/30 |
| 20 n = 7 minimal NO  |          20 |   20/20 |
| n = 12 skew templates|           3 | 3/3 (vs FF solver) |

(The n = 12 brute force is too slow — 12! ≈ 479M permutations — so the
n = 12 row uses the exact `find_lfo_order_forced_flexible` solver as
oracle instead, which is itself cross-validated against brute force
through n = 7 elsewhere in this repository.)

Across all tested cases (≥ 36 000 tournaments at n ≤ 9 plus the three
documented n = 12 skew templates and all 20 n = 7 minimal NO
instances) the J-pathwidth DP agrees with brute force / FF.  The n = 6
exhaustive sweep is the strongest guarantee: every tournament at
n = 6 is classified correctly.  The n = 12 skew templates exercise
the previously-documented `one_block` collision pair
`(0, 1, 2, 5, 3)` vs `(1, 2, 0, 5, 3)` — both DP and FF return YES on
`one_block`, NO on `skew_induction`, YES on `wake1_failure`, in
agreement with §14.2 of `docs/exchange_proof_draft.md`.

### 4.1 Probing the documented failure modes

The `docs/general_path_fas_dp.md` collision pair
`(0, 1, 2, 5, 3)` vs `(1, 2, 0, 5, 3)` on `one_block` (n = 12) is the
canonical failure of every weaker state quotient.  Our DP **does not**
suffer from this collision, because its σ component records the full
LFO restricted to the bag: any pair of σ's that disagree on the
relative order of bag vertices have different state keys, and they
extend differently.  In particular, the forgotten vertices' merging
into a future-relevant component is captured by `comp` (forgotten
vertex IDs persist as component representatives until a still-in-bag
vertex inherits the role at canonicalization).

The collision is therefore *only* a problem if one tries to project
σ out of the state; our DP keeps σ explicitly and pays for it.

## 5. Honest Verdict

The DP is **correct** on every test we ran (exhaustive at n ≤ 6,
random at n ∈ {7, 8, 9}, all n = 7 minimal NO instances).  But its
runtime is exponential in pathwidth `w(J)`.

Three honest takeaways:

1. **As a bounded-|H| algorithm**, this DP now gives a theorem:
   since `pw(J) ≤ 8+2|H|`, Path-FAS is FPT in \(|H|\) and polynomial
   whenever \(|H|\) is bounded.

2. **As a correctness specification**, this DP is a clean reduction
   of Path-FAS to "is the loaded-backedge subgraph of J a linear
   forest?".  Every previously-tried weaker state encoding
   (sleeping-block, bounded-port, half-block parity, image-interval —
   see Sections 1–3 of `docs/general_path_fas_dp.md`) was a
   *projection* of this DP's state, and each documented projection
   collides on the n = 12 `one_block` instance.  Our DP avoids the
   collision precisely because it retains σ exactly.

3. **What remains for a general polynomial algorithm?**  Either
   compress the forced-backedge part so the `2|H|` endpoint term does
   not appear in every bag, or prove hardness in the regime where H is
   large.  The first diagnostic for that compression route is
   `scripts/forced_frontier_probe.py`; it shows that a naive
   "two endpoints per live H-component" compression is already linear
   on the reversed-matching family.

## 6. Reproduction

```
uv run python scripts/J_pathwidth_dp.py --smoke
uv run python -m pytest tests/test_J_pathwidth_dp.py -v
uv run python scripts/J_pathwidth_dp_probe.py --n 7 --count 2000
uv run python scripts/J_pathwidth_dp_probe.py --n 8 --count 100
```

All scripts use the project's `uv`-managed virtualenv with
`networkx == 3.6.1`.
