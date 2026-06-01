# Q2 apex-cut attack

This note records a new non-forward angle on Path-FAS after the 3/4-cycle
reduction in `q2_nonforward_attack.md`.

The outcome is not a polynomial algorithm.  It is a sharper exact
reformulation of the triangle side, plus strong evidence that the known
minimal NO instances are governed by a small local-consistency obstruction.

## 1. The apex-cut identity

Let `F` be the unknown selected edge set.  For a vertex `v`, write

```text
P_v = N_F(v).
```

Since `F` must be a linear forest, every feasible witness has

```text
|P_v| <= 2.
```

Split the tournament around `v`:

```text
A_v = N^+(v),   B_v = N^-(v).
```

Define the **apex-cut graph** `C_v` as the bipartite graph on
`A_v ∪ B_v` with an edge `ab` when

```text
v -> a,   a -> b,   b -> v.
```

Equivalently, `ab ∈ C_v` iff `v,a,b` form the directed triangle

```text
v -> a -> b -> v.
```

Then for every selected set `F`:

> **Apex-cut lemma.**  `F` hits every directed triangle of `T` iff, for every
> vertex `v`,
>
> ```text
> E(C_v - P_v) ⊆ F.
> ```

**Proof.**  If `ab ∈ C_v` and neither `a` nor `b` lies in `P_v`, then the two
edges incident with `v` in the triangle `v -> a -> b -> v` are not selected.
To hit the triangle, `ab` must be selected.  This proves the forward
direction.

Conversely, take any directed triangle `x -> y -> z -> x`.  It appears in the
apex-cut graph `C_x` as the edge `yz`.  If neither edge incident with `x` is
selected, then `y,z ∉ P_x`, so the apex-cut condition forces `yz ∈ F`.  Hence
the triangle is hit. ∎

So directed-triangle hitting is not an arbitrary 3-uniform hitting-set
condition.  It is a family of vertex-apex closure conditions where each apex
may protect at most two endpoints.

## 2. Immediate necessary local filter

For a proposed protector set `P_v` with `|P_v|≤2`, the edges forced by `v` are

```text
Forced(v,P_v) = E(C_v - P_v).
```

In any Path-FAS witness, this forced graph is a subgraph of the final linear
forest `F`.  Therefore it must itself be a linear forest.

This gives a polynomial local filter:

```text
D_v = { P⊆V\{v} : |P|≤2 and C_v - P is a linear forest }.
```

If some `D_v` is empty, the tournament is immediately Path-FAS NO.

This is stronger than the cycle-count certificate: it uses the topology of
how directed triangles cross a single apex, not just how many triangles exist.

## 3. The apex CSP

The local domains `D_v` define a finite-domain CSP.

Variable:

```text
v chooses P_v ∈ D_v.
```

Pairwise symmetry:

```text
u ∈ P_v  iff  v ∈ P_u.
```

Forced-edge implications:

```text
if xy ∈ Forced(v,P_v), then y ∈ P_x and x ∈ P_y.
```

A global assignment defines

```text
F = { uv : u ∈ P_v }.
```

If the assignment satisfies the pairwise constraints, then `F` hits every
directed triangle.  Path-FAS additionally requires:

```text
F is a linear forest,
F hits every directed 4-cycle.
```

The current probe uses AC-3-style arc consistency on the binary implications,
then exact backtracking with the final global forest and 4-cycle checks.  This
is still an exponential algorithm in the worst case.  The point is to expose
whether the apex formulation has a much smaller residual than the old
order-prefix state space.

Implementation:

```text
scripts/q2_apex_cut_probe.py
```

Regression tests:

```text
tests/test_q2_acyclicity_core.py
```

## 4. Validation

Pinned tests:

* The apex-cut closure condition is equivalent to directed-triangle hitting
  over all edge subsets of all tournaments on `n=4`.
* The apex CSP agrees with the brute-force Path-FAS decider on all tournaments
  with `n≤5`.
* The apex CSP refutes every certified `n=7` minimal NO instance, with search
  exhausted.

Command:

```text
./.venv/bin/python -m unittest tests/test_q2_acyclicity_core.py
```

Result:

```text
Ran 17 tests in 36.077s
OK
```

## 5. Catalogue results

On certified minimal-NO catalogues:

| catalogue | records | arc-consistency empty | exact search found YES | not exhausted | max search nodes |
|---|---:|---:|---:|---:|---:|
| `n=7` | 20 | 4 | 0 | 0 | 74 |
| `n=8` | 572 | 186 | 0 | 0 | 61 |
| `n=9` | 5560 | 2661 | 0 | 0 | 3131 |

For `n=8`, the maximum post-AC domain sum was `132`; for `n=9`, it was
`196`.  Thus the apex formulation absolutely crushes the known minimal NO
catalogues: over 47% of the `n=9` records die by local consistency alone, and
the worst full exact search used only `3131` nodes.

This is the first Q2 formulation in the project where the certified
acyclicity-core NO instances look small for a structural reason rather than
because degree-2 orders happen to be few.

## 6. Positive-side caveat

The probe is not a polynomial algorithm.  Synthetic YES instances generated
from a transitive order plus a random linear forest are usually easy, but not
uniformly:

```text
n=8  known YES, 10 samples: max 101 nodes, avg 16.7
n=10 known YES, 10 samples: max 22110 nodes, avg 2286.0
n=12 known YES, 10 samples: max 19480 nodes, avg 2557.2
n=14 known YES, 10 samples: max 344 nodes, avg 46.0
n=16 one sample hit the 200000 node cap before finding the planted witness
```

So the naive backtracking order is not the proof.  The important fact is that
the NO side has become highly structured; the YES side still needs a
constructive selection rule.

## 7. New proof target

The old Q2 target was:

```text
find a linear forest hitting all directed 3- and 4-cycles.
```

The apex-cut target is sharper:

> **Apex-CSP polynomiality target.**  For tournaments, the CSP whose domains
> are the local protector sets `D_v` and whose constraints are symmetry plus
> forced-edge implications has a polynomial-time decision procedure after
> adding the global forest and directed-4-cycle checks.

There are three plausible ways this could become a proof:

1. **Arc-consistency completeness on NO.**  Prove that if the AC closure is
   nonempty and the induced forced graph is cycle-free, then a valid witness
   can be constructed.  The catalogue evidence is consistent with this for
   minimal NOs but not yet a theorem.
2. **Bounded residual structure.**  Prove that after AC, the residual
   variable-interaction graph has bounded treewidth/pathwidth or decomposes
   into paths/cycles.  Then the remaining CSP is polynomial by a standard
   bounded-width DP that is not an order-prefix DP.
3. **2-SAT collapse.**  Show that every domain `D_v` has a canonical small
   basis after AC, so the remaining choices can be encoded by binary
   protector flips.  This would be the true degree-2 analogue of the
   matching-FAS 2-SAT proof.

The next attack should inspect the worst residual instances:

```text
n=9 worst: 9#121950, post-AC domain sum 99, search nodes 3131
```

and mine their residual CSPs for one of the three structures above.

## 8. Honest status

This angle does not prove `Path-FAS ∈ P`.  It does produce a new exact
triangle-closure formulation and a very strong empirical compression of the
minimal-NO core.

The old generic formulation was a matroid-constrained hitting problem.  The
new formulation is tournament-specific: every vertex gets at most two
protectors, and all unprotected cyclic-cross edges are forced.  That is the
first post-Q1 attack that looks structurally different from the dead
matroid/LP/forward-DP routes.

