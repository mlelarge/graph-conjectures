# Path-FAS - corrected target and first obstructions

## Formal target

The exact connected-path back-arc condition is not the right formalization
of Problem 4.4.

Let $T$ be a tournament and let $F\subseteq A(T)$ be a FAS whose
underlying undirected graph is a path. If $\prec$ is a topological order
of $T-F$, then the back-arc set $B_\prec(T)$ is contained in $F$.
Therefore the back-arc graph is a subgraph of a path, hence a linear
forest.

Conversely, suppose some order $\prec$ has back-arc graph
$B_\prec(T)$ equal to a linear forest. Complete this linear forest to a
single path in the complete graph on $V(T)$ by joining path-component
endpoints, inserting isolated vertices anywhere if one wants a spanning
path. Let $F$ be the corresponding set of tournament arcs. Then
$B_\prec(T)\subseteq F$, and every arc of $T-F$ is forward with respect
to $\prec$; hence $T-F$ is acyclic. Thus $F$ is a path-shaped FAS.

So:

> $T$ has a path-FAS iff $T$ has an order whose back-arc graph is a
> linear forest.

The old `path` flag in `scripts/verify.py` means something stricter:
the back-arc graph itself is a connected path. It is useful only as a
diagnostic. The formal Problem 4.4 target is now `path_fas`, equivalently
`linear_forest`.

## Heredity

The linear-forest ordering property is hereditary under induced
subtournaments. If $\prec$ is an LFO order of $T$ and $X\subseteq V(T)$,
then the restriction of $\prec$ to $X$ has back-arc graph equal to a
subgraph of the original back-arc graph. A subgraph of a linear forest is
again a linear forest.

Consequently, every induced subtournament with no LFO is a certificate
that the ambient tournament has no LFO. This is why the exact $n=7$ NO
list is useful as a forbidden-subtournament test in
`path_fas_structure.md`.

## Relation with forest-FAS

The source paper proves NP-completeness for forest-FAS. Path-FAS is not
the same as forest-FAS: the back-arc graph must be a linear forest, not
an arbitrary forest.

Random brute-force checks already separate the notions. In one sample:

| $n$ | samples | matching | exact path | formal path / linear forest | forest | forest yes but formal path no |
|---:|---:|---:|---:|---:|---:|---:|
| 7 | 200 | 28 | 182 | 185 | 199 | 14 |
| 8 | 80 | 3 | 58 | 59 | 78 | 19 |
| 9 | 10 | 0 | 2 | 2 | 4 | 2 |

This is not a proof of complexity, but it kills two bad simplifications:

- exact connected-path backarcs are too restrictive;
- forest-orderings are too permissive.

## Triangle flip table

For a candidate set $M$ with $T\oplus M$ transitive, every triple must
remain transitive after the arcs of $M$ in that triple are reversed.
Unlike the matching case, a path-FAS candidate may use two arcs of a
triangle.

For a cyclic triangle $a\to b\to c\to a$:

- 0 flipped arcs: cyclic, forbidden;
- 1 flipped arc: transitive, allowed;
- 2 flipped arcs: transitive, allowed;
- 3 flipped arcs: cyclic, forbidden, and also impossible in a linear
  forest because it would form a triangle.

For a transitive triangle $a\succ b\succ c$, with long arc $a\to c$:

- 0 flipped arcs: transitive, allowed;
- 1 flipped short arc: transitive, allowed;
- 1 flipped long arc: cyclic, forbidden;
- 2 flipped arcs consisting of the two short arcs: cyclic, forbidden;
- 2 flipped arcs consisting of the long arc and one short arc:
  transitive, allowed;
- 3 flipped arcs: transitive, but impossible in a linear forest.

Thus the matching proof does not extend: the matching case collapses to
"every selected arc is no-shortcut and every cyclic triangle receives
exactly one selected arc." The path case has legitimate two-arc
V-shapes, and the long-arc obstruction is conditional on which other arc
of the triangle is selected.

## Small separating examples

`tests/test_path_fas.py` pins two useful 7-vertex examples.

1. Formal path-FAS YES but exact-path-backarcs NO. The back-arc graph of
   the witnessing order is a disconnected linear forest; adding one
   forward arc completes it to a path-shaped FAS.
2. Forest-FAS YES but formal path-FAS NO. This tournament has a
   forest-ordering, and even a minimum FAS of size 5, but every
   forest-ordering needs a degree-3 vertex somewhere. So the obstruction
   is not merely the size bound $|F|\le n-1$.

## Current status

The path half is now reduced to the **linear-forest ordering problem for
tournaments**:

> Does there exist a total order of $V(T)$ whose back-arc graph is a
> forest of maximum degree at most 2?

This is strictly between matching-FAS and forest-FAS. I do not yet have a
polynomial algorithm or an NP-hardness reduction for it.

The most plausible next attacks are:

1. Try to adapt the Aboulker-Aubian-Lopes forest-ordering reduction while
   replacing high-degree forest gadgets by chains of degree-2 gadgets.
2. Search for a bounded-width dynamic program parameterized by the
   number of backarcs, exploiting $|B_\prec(T)|\le n-1$.
3. Build adversarial families around the 7-vertex forest-not-path-FAS
   obstruction and test whether they compose under modular substitution.
