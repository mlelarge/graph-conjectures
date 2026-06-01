# Q2 non-forward attack after Q1

This note records the first attack on the acyclicity core after D103 closed
Q1.  The conclusion is not a polynomial algorithm for Path-FAS.  It is a
sharper reduction of the remaining difficulty:

* Q1 gives a polynomial-size graph of degree-feasible prefix **sets**.
* Q2 asks for a path through that graph whose accumulated back-arc labels form
  a forest.
* The scalar shortcut "minimize the number of degree-2 back-arcs" is false.
* Under a selected linear forest, the directed acyclicity side localizes to
  directed cycles of length `3` and `4`; the global part left is exactly the
  selected-forest topology.
* The exact static problem is now a polynomial-size covering system plus a
  graphic/degree independence constraint:

  ```text
  choose a linear forest F hitting every directed 3-cycle and directed 4-cycle.
  ```

## 1. Q1 does not collapse Q2

D103 proves that same-size degree-feasible reachable prefix sets have diameter
at most `8`.  Hence the degree-only prefix-set graph has polynomial size.
This does not contradict D70.

In the D70 toggle family, the `2^k` prefixes

```text
P_epsilon = product_i (a_i,b_i) or (b_i,a_i)
```

all place the same vertex set:

```text
{a_0,b_0, ..., a_{k-1},b_{k-1}}.
```

The exponential information is not the prefix set.  It is the component
history of the partially built back-arc forest: for each gadget, whether
`f_i` and `g_i` are already connected.  The probe distinguishes exactly that
connectivity bit.  Thus Q1 compresses the degree layer, while Q2 still has to
decide a global forest-independence condition over exponentially many
histories through the same prefix-set node.

## 2. Polynomial prefix DAG with graphic-matroid labels

Let `G_deg(T)` be the layered DAG whose nodes are degree-feasible reachable
prefix sets and whose arcs are legal one-vertex extensions

```text
S -> S ∪ {u}
```

with

```text
bd(u | S) = 2|N^+(u) ∩ S| + d^-(u) - |S| ≤ 2.
```

By D103, `G_deg(T)` has `n^{O(1)}` nodes and arcs for fixed threshold `2`.

Label the transition `S -> S∪{u}` by the set

```text
L(u,S) = { {u,w} : w ∉ S∪{u} and w -> u in T }.
```

These are exactly the back-arcs incident with the newly placed vertex whose
other endpoint is still in the future.  Every final back-arc is charged once,
to its earlier endpoint in the order.

Therefore:

> **Q2 as labelled path.**  A tournament has a Path-FAS order with
> `Δ*≤2` iff `G_deg(T)` has an `∅`-to-`V` path such that the union of its
> transition labels is acyclic as an undirected graph.

The degree bound is already enforced by the legality of each transition:
when a vertex is placed, all its final incident back-arcs are fixed and have
size at most `2`.  What remains is exactly graphic-matroid independence of the
accumulated labels.

This is non-forward in the right sense: the underlying graph is polynomial,
but the hard object is a path with a global matroid constraint.  Generic
matroid-labelled path problems are not automatically polynomial, and D70 is
the concrete warning that retaining the needed connectivity online gives
`2^Ω(n)` states.

## 3. The min-edge shortcut is false

A tempting scalar replacement for acyclicity is:

> Accept iff some degree-2 order has at most `n-1` back-arcs.

This is false.  The following 7-vertex tournament has exactly one degree-2
order; that order has `n-1 = 6` back-arcs, but its back-arc graph contains a
5-cycle, and no acyclic degree-2 order exists.

```text
[0, 1, 1, 1, 1, 0, 0]
[0, 0, 0, 0, 1, 1, 0]
[0, 1, 0, 1, 0, 0, 1]
[0, 1, 0, 0, 0, 1, 1]
[0, 0, 1, 1, 0, 1, 0]
[1, 0, 1, 0, 0, 0, 1]
[1, 1, 0, 0, 1, 0, 0]
```

The unique degree-2 order is

```text
(0, 4, 3, 5, 2, 6, 1),
```

with back-arc component signature

```text
max_degree = 2, cycle_lengths = [5].
```

So Q2 cannot be reduced to shortest degree-2 ordering over `G_deg(T)`.
Component topology is genuinely load-bearing.

## 4. Directed cycles localize to lengths 3 and 4

There is, however, a useful non-forward structural simplification.

**Lemma 4.1.**  Let `F ⊆ A(T)` be a feedback-candidate whose underlying
undirected graph is a linear forest.  Then `T-F` is acyclic iff `T-F` has no
directed cycle of length `3` or `4`.

**Proof.**  One direction is immediate.  Conversely, suppose `T-F` has a
directed cycle, and choose a shortest one

```text
C = v_1 -> v_2 -> ... -> v_l -> v_1.
```

If `l ≥ 4`, then any chord between two nonconsecutive vertices of `C`, if
present in `T-F`, creates a shorter directed cycle: one orientation closes
one of the two directed subpaths of `C`, and the opposite orientation closes
the other.  Hence every chord of `C` must lie in `F`.

For `l ≥ 6`, each vertex of `C` is incident with at least `l-3 ≥ 3` chords
inside `F`, contradicting the maximum-degree-2 condition of a linear forest.
For `l = 5`, the five chords of `C` form a 5-cycle in the underlying graph of
`F`, contradicting acyclicity of `F`.  Therefore a shortest directed cycle in
`T-F` has length at most `4`. ∎

Thus Path-FAS has the exact static formulation:

> Choose a set `F` of tournament arcs whose underlying graph is a linear
> forest and which hits every directed 3-cycle and every directed 4-cycle of
> `T`.

Here is the full equivalence, to avoid the old triangle-only confusion.

* If `σ` is a Path-FAS order, its back-arc set `B_σ` is a linear forest and
  `T-B_σ` is acyclic, hence `B_σ` hits every directed 3- and 4-cycle.
* Conversely, if a linear forest `F` hits every directed 3- and 4-cycle, then
  Lemma 4.1 makes `T-F` acyclic.  Any topological order `σ` of `T-F` has
  `B_σ ⊆ F`, so `B_σ` is also a linear forest.  Thus `σ` is a Path-FAS
  order.

The directed-FAS side is local, with `O(n^4)` lower-bound constraints.  The
remaining global difficulty is not directed acyclicity of `T-F`; it is the
requirement that the selected hitting set `F` itself be a linear forest.

## 5. Static shortcuts that are dead

The 3/4-cycle theorem is sharp in both directions that matter.

### 5.1 Triangle-only is false even with a linear forest

On vertices `{0,1,2,3}`, orient

```text
0 -> 1 -> 2 -> 3 -> 0
```

and orient the diagonals as

```text
0 -> 2,  1 -> 3.
```

Let

```text
F = {0->2, 1->3}.
```

Then `F` is a matching, hence a linear forest.  It hits every directed
triangle: the only cyclic triangles are `0->1->3->0` and `0->2->3->0`, and
each contains one selected diagonal.  But `T-F` still contains the directed
4-cycle

```text
0 -> 1 -> 2 -> 3 -> 0.
```

So directed 4-cycle constraints are not cosmetic; they are the exact missing
piece in the old triangle relaxation.

### 5.2 Degree-2 FAS is false without selected acyclicity

The other tempting relaxation is:

```text
choose F with max selected-degree <= 2 such that T-F is acyclic.
```

This is also false.  The first certified `n=7` minimal-NO record has a set

```text
S = {0->6, 3->1, 3->2, 4->1, 4->2, 6->5}
```

with max selected-degree `2` and `T-S` acyclic.  Equivalently, `S` hits all
directed cycles, hence all directed 3- and 4-cycles.  But the underlying graph
of `S` contains the undirected 4-cycle

```text
3 - 1 - 4 - 2 - 3,
```

so `S` is not a linear forest; the tournament is a Path-FAS NO.  This witness
is the static version of the Q2 obstruction: all directed constraints are
already satisfied, and only the selected-forest topology fails.

## 6. Exact 0-1 formulation

The static theorem gives the cleanest non-forward integer model.  For every
tournament arc `e`, let `x_e = 1` mean `e ∈ F`.  Then Path-FAS is equivalent
to feasibility of

```text
x_e ∈ {0,1}

sum_{e incident with v} x_e <= 2                         for every vertex v
sum_{e in C} x_e >= 1                                    for every directed 3- or 4-cycle C
sum_{e in U} x_e <= |U|-1                                for every undirected cycle U
```

Here `U` denotes the tournament arcs carried by the edges of the underlying
undirected cycle.  For integral `x`, these cycle inequalities say exactly
that the selected graph has no undirected cycle.  For the LP/optimization
view one should use the equivalent graphic-matroid rank description

```text
sum_{e inside X} x_e <= |X|-1                             for every nonempty X⊆V,
```

which has standard polynomial separation.

This is an exact formulation, but it is not a polynomial algorithm.  The
covering constraints are polynomially many (`O(n^4)`), and the forest
constraints have standard polynomial separation, but the resulting LP is not
integral: the older full directed+undirected cycle-cut LP audit already found
fractional feasible points on NO instances.  Integer feasibility here is a
matroid-constrained covering problem, not Edmonds matroid intersection: the
cycle-hitting inequalities are lower bounds, not membership in a second
matroid.

## 7. Status

This attack does not prove `Path-FAS ∈ P`.  It does narrow the problem to two
equivalent non-forward formulations:

1. **Labelled-path formulation:** find an `∅`-to-`V` path in the polynomial
   Q1 prefix DAG whose accumulated labels are graphic-matroid independent.
2. **Static local-cycle formulation:** find a linear forest hitting all
   directed 3- and 4-cycles of the tournament.

Both formulations isolate the same remaining obstruction: forest topology of
the selected/back-arc graph.  The D70 family shows why this topology cannot be
tracked by a forward state without exponential blow-up; the min-edge witness
shows it cannot be replaced by a scalar objective; the static witnesses above
show it cannot be replaced by triangle-only hitting or by degree-2 FAS.

The real Q2 target is therefore sharply stated:

> Is the linear-forest transversal problem for the directed 3- and 4-cycles
> of a tournament decidable in polynomial time?

I do not currently have that algorithm.  The non-forward attack has reduced
the directed side to polynomially many local constraints, but the selected
forest topology is still a global graphic-matroid independence condition
coupled to covering lower bounds.

The next literature pass is scoped in
`docs/q2_literature_scope_independent_transversal.md`.  The key warning for
that pass is that Q2 is an independent **hitting** problem with shared
representatives, not a standard rainbow/independent-transversal problem with
distinct representatives.

## 8. Tests

The pinned tests are in `tests/test_q2_acyclicity_core.py`:

* `test_toggle_explosion_is_history_not_prefix_set_count`;
* `test_min_degree2_edge_count_shortcut_is_false`;
* `test_static_3_4_linear_forest_formulation_matches_bruteforce`;
* `test_triangle_only_static_formulation_is_false`;
* `test_degree2_fas_without_forest_topology_is_false`;
* `test_linear_forest_fas_needs_only_directed_3_and_4_cycles`.

## 9. Attempt at a polynomial algorithm — outcome

I attempted a polynomial algorithm for the linear-forest 3/4-cycle transversal
(equivalently Path-FAS ∈ P).  It did **not** succeed.  One proved byproduct
and the reasons the natural routes fail:

**Cycle-count necessary condition (PROVED, poly NO-certificate).**
> If `T` is Path-FAS YES, then `T` has at most `(n−1)(n−2)` directed 3-cycles
> (and `O(n³)` directed 4-cycles).

*Proof.*  A witnessing `F` is a linear forest, so `|F| ≤ n−1`.  Each arc
`(a,b) ∈ F` lies in exactly `|N⁺(b) ∩ N⁻(a)| ≤ n−2` directed 3-cycles.  Since
`F` hits every directed 3-cycle, `#3-cycles ≤ Σ_{e∈F}(3-cycles through e)
≤ (n−1)(n−2)`.  The 4-cycle bound is analogous (`≤ (n−1)·O(n²)`). ∎

Verified: 0 violations over all tournaments `n≤6` (max #3-cycles over YES is
well under the bound).  So "`#3-cycles > (n−1)(n−2)`" is a polynomial-time
**NO** certificate.

**But this does not decide the problem.**  It is *necessary, not sufficient*,
and useless on the hard instances: every certified minimal-NO at `n=7,8` has
**few** 3-cycles (ranges `[9,14]` and `[12,20]`, all far below the bounds
`30`, `42`).  The acyclicity-core NOs are nearly transitive; the obstruction
is the forest **topology** of the transversal, not an abundance of cycles.

**Why the natural poly routes fail (recap).**
- *LP relaxation:* not decisive.  The new formulation (3/4-cycle covering +
  degree-≤2 + forest rank) has *fewer* covering constraints than the old full
  cycle-cut LP, which was already fractional-feasible on NO instances; so the
  relaxation is still fractional-feasible on NOs.
- *Matroid intersection:* not applicable.  The cycle-hitting constraints are
  covering lower bounds, not membership in a second matroid; and linear
  forests are not a matroid (forest ∩ degree-≤2).
- *Forward DP on the Q1 prefix DAG:* dead by D70 (`2^Ω(n)` to track the
  back-arc forest component history through a shared prefix-set node).

**Status.**  No polynomial algorithm found.  Path-FAS ∈ P remains open,
pinned to: a linear-forest (graphic-matroid-independent) transversal of the
directed 3- and 4-cycles, on the near-transitive acyclicity-core where cycle
counts are small and the only obstruction is selected-forest topology.
