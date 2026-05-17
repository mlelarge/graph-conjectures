# Review of `draft_v1.md`

Date: 2026-05-17

## Verdict

Do **not** submit `draft_v1.md` as it stands.

The citation discipline and conditionality labelling are much improved,
but the load-bearing Conjecture L in Section 6 is false as written. The
draft's own funnel example, after monotone augmentation to a 3-arc-strong
host, gives a counterexample to Conjecture L. This is not a cosmetic
issue; it invalidates the conditional hard-case theorem in its current
form.

## Blocking Finding 1: Conjecture L Is False As Stated

In `paper/draft_v1.md` lines 936--945, Conjecture L says:

> For every 3-arc-strong directed multigraph `D^\bullet`, every pair of
> arc-disjoint spanning in-arborescences `T^-, U^-` rooted at `r`, and
> every `a in T^-`, some `U^-`-exit arc from `X_a^{T^-}` has subtree
> intersection strictly smaller than `X_a^{T^-}`.

This universal statement over arbitrary pairs `(T^-, U^-)` is false.

The draft's Example 6.1 already gives the failing pair:

```text
V = {r, u, v1, w}
T^- = {(v1,u), (u,r), (w,r)}
U^- = {(u,v1), (v1,r), (w,v1)}
a = (u,r)
X = {u, v1}
```

The unique `U^-`-exit from `X` is `b = (v1,r)`. Its `U^-`-subtree is
`{v1,u,w}`, so

```text
X_b^{U^-} cap X = {u,v1} = X,
```

not a strict subset.

The only caveat in the draft is that this six-arc host is not
3-arc-strong. But that caveat does not save Conjecture L, because the
same two arborescences can sit inside a 3-arc-strong supergraph.
For example, take the complete bidirected digraph on `{r,u,v1,w}`.
It has arc-connectivity 3. The same `T^-` and `U^-` remain arc-disjoint
spanning in-arborescences rooted at `r`, and their subtree structure is
unchanged. Therefore Conjecture L still fails.

This is also recorded explicitly in `team/31_conjecture_L_proof_attempt.md`
lines 126--128:

> Conjecture L can fail for an arbitrary arc-disjoint pair of
> in-branchings, including pairs lying inside a 3-arc-strong host.

So the draft currently contradicts the team's own working notes.

## Consequences

1. `paper/draft_v1.md` lines 774--801 cannot be used as the
   load-bearing termination mechanism for RECOLOR.

2. Theorem 5.6 is not a meaningful conditional theorem under the stated
   Conjecture L. It is conditional on a false universal statement.

3. Theorem 3 should not be advertised as a conditional near-split SAD
   theorem until Conjecture L is replaced by a true statement. The likely
   replacement is one of the two rescue formulations already identified
   in `team/31_*`:

   - an **existential-choice** statement: there exists a suitable pair
     `(T^-, U^-)` satisfying the subtree condition for all needed arcs;
   - a **swap-repair** statement: an arbitrary pair can be locally
     modified to obtain the strict-decrease property at the needed arc.

4. Section 6.5's empirical-support paragraph must be rewritten. SAT
   outcomes for near-split instances do not indirectly verify Conjecture
   L as stated, because SAD existence may be witnessed by a different
   decomposition even when a particular branching pair violates L.

## Blocking Finding 2: Lemma 5.4 Is Not Proven In The Draft

Even ignoring the false Conjecture L statement, Lemma 5.4 is not proved
at submission standard. Lines 794--801 say the proof requires a
potential on an auxiliary digraph and that the technical proof is in the
team's working notes. That is not acceptable for a submitted theorem.

If a corrected Conjecture L' is introduced, the paper must include the
full termination proof from L' to RECOLOR termination, either in the
body or as an appendix.

## Minor Fixes

1. `paper/draft_v1.md` line 41 defines the out-cut incorrectly:

```text
v \notin V \setminus X
```

should be

```text
v \notin X
```

or equivalently `v in V \setminus X`.

2. Section 3.4's small-`n` direct check says a 2-arc-strong digraph on
two vertices consists of doubled antiparallel arcs. That is a multigraph
statement, while the paper's default convention is simple digraphs unless
otherwise stated. Either call the `n=2` case vacuous under the simple
convention, or explicitly extend Theorem 1 to Eulerian multidigraphs.

## Recommendation

Freeze submission. Keep Theorems 1, 2, and 4. Demote Theorem 3 from a
paper theorem to an open conditional program until the hard-case
condition is replaced by a true Conjecture L' and the RECOLOR
termination proof is written in full.

