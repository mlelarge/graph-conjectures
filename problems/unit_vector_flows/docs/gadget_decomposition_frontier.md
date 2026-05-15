# Gadget decomposition frontier — inverse operations and reachability

[gadget_closure.md](gadget_closure.md) gives the **forward** direction:
given a cubic graph in the certified base $\mathcal{F}_0$ (the 3 247
nontrivial snarks at $n \le 28$), apply triangle blow-up or 3-edge-cut
dot product to grow $S^2$-flow-equipped cubic graphs. This file
documents the **inverse** direction: given a cubic graph $G$,
decompose it back to base by detecting and undoing those two gadget
operations.

The two algorithms (one per gadget) plus a graph6-memoised dynamic
program are in
[scripts/gadget_decompose.py](../scripts/gadget_decompose.py).

## Inverse operations

### Inverse triangle reduction

A triangle $\{u_1, u_2, u_3\} \subset V(G)$ in a cubic graph $G$ is
**contractible** iff each $u_i$ has exactly one external neighbour
$e_i$ and $e_1, e_2, e_3$ are pairwise distinct. The contraction
removes the three triangle vertices, adds a fresh vertex $v$ adjacent
to $\{e_1, e_2, e_3\}$, and yields a simple cubic graph with
$|V(G)| - 2$ vertices.

Inverse correctness: if $G' = $ blow-up of $G$ at $v$, then the new
triangle in $G'$ is contractible, and contracting it produces $G$ up
to isomorphism.

Implementation: `find_contractible_triangles(G)` enumerates by
triple-of-vertices; `contract_triangle(G, triangle)` performs the
contraction.

### Inverse 3-edge-cut dot product

A **cyclic 3-edge cut** is a set $C = \{e_1, e_2, e_3\} \subset E(G)$
whose removal disconnects $G$ into exactly two components, each
containing a cycle. To **split** $G$ at $C$: take each side and add a
fresh vertex adjacent to the three cut-edge endpoints on that side.
The result is a pair of cubic graphs whose 3-edge-cut dot product (at
the two fresh vertices) is isomorphic to $G$.

Implementation: `find_cyclic_3_cuts(G)` enumerates by triple-of-edges
(brute, $\binom{m}{3}$ — feasible for $m \le 50$);
`split_at_3_cut(G, cut)` performs the split.

### Isomorphism via canonical graph6

Two graphs are isomorphic iff their **canonical graph6** strings
(produced by `nauty`'s `labelg`) are equal. `canonical_graph6(G)`
wraps the local `labelg` invocation; with `labelg` absent it falls
back to a vertex-sorted relabelling (strictly weaker than nauty
canonicalisation). The decomposition DP keys all memoised states on
canonical graph6 strings.

## Decomposition tree DP

`decompose_tree(G, base)` returns a `DecompTree` whose internal nodes
are tagged `TRIANGLE` or `DOT` and whose leaves are graph6 strings in
the base set, or `None` if no such tree exists. Memoisation prevents
re-decomposition of any subgraph.

```text
DecompTree(op="TRIANGLE", graph6=..., children=[
    DecompTree(op="DOT", graph6=..., children=[
        DecompTree(op="BASE", graph6=...),  # in base
        DecompTree(op="BASE", graph6=...),
    ]),
])
```

The tree is a **replayable certificate**: given the operation tree
and base certificates, the constructive $S^2$-flow on $G$ is recovered
by composing `triangle_blowup_flow` / `dot_product_witness` from the
leaves up.

## Frontier result: the catalogue is the base

Scanning all 3 247 nontrivial snarks at $n \le 28$:

| Diagnostic | Count |
|---|---:|
| Graphs with a contractible triangle | $0$ |
| Graphs with a cyclic 3-edge cut (checked $n \le 22$, total 29 graphs) | $0$ |
| Graphs with a cyclic 3-edge cut ($n \ge 24$, by catalogue construction) | $0$ |

Every nontrivial snark in the catalogue is **irreducible** under both
inverse operations — exactly as expected from the definition:

- girth $\ge 5 \Rightarrow$ no triangles $\Rightarrow$ inverse-triangle
  inapplicable;
- cyclically $\ge 4$-edge-connected $\Rightarrow$ no cyclic 3-cuts
  $\Rightarrow$ inverse-dot inapplicable.

So the catalogue **is** the irreducible-frontier base. There is no
shrinking it further by these two gadgets.

## Positive results: gadget-generated graphs decompose cleanly

The decomposition DP correctly reverses every gadget composition
tested:

| Construction | $n$ | Tree depth | Leaves |
|---|---:|---:|---|
| `triangle_blowup(Petersen, v=0)` | 12 | 1 | $\{\text{Petersen}\}$ |
| Double `triangle_blowup` on Petersen | 14 | 2 | $\{\text{Petersen}\}$ |
| `dot_product(Petersen, Petersen)` | 18 | 1 | $\{\text{Petersen}^{\times 2}\}$ |
| `dot_product(Petersen, Blanuša_1)` | 26 | 1 | $\{\text{Petersen}, \text{Blanuša}_1\}$ |
| Triple chain `Petersen.Petersen.Blanuša_1` | 34 | 2 | 3 base leaves |
| Triple chain + blow-up at $v=0$ | 36 | 3 | 3 base leaves |

For every constructively generated graph, the decomposition tree
recovers the original construction (up to the freedom in choosing
which contractible triangle / which cyclic 3-cut to undo first).

## Theorem (constructive corollary)

> Let $\mathcal{F}_0$ be the certified base (3 247 nontrivial snarks
> at $n \le 28$, each equipped with an interval-Krawczyk
> $S^2$-flow certificate). Let $G$ be any cubic graph that
> :func:`decompose_tree` returns a non-trivial tree for, with all
> leaves in $\mathcal{F}_0$. Then $G$ admits a constructive
> $S^2$-flow: assemble the witness by composing
> `triangle_blowup_flow` and `dot_product_witness` from the leaves
> up, following the operation tree.
>
> The constructive witness is verified at machine precision by
> `witness.verify_witness` (max Kirchhoff residual $\sim 10^{-16}$
> in every recorded test).

## What this says about $\mathcal{F}$

Let $\mathcal{F}$ be the closure of $\mathcal{F}_0$ under the two
gadget operations. The decomposition tree algorithm gives a
**decision procedure** for membership: $G \in \mathcal{F}$ iff
`decompose_tree(G, base(F_0))` returns a non-None tree.

Three open questions, none currently approached:

1. **Characterise $\mathcal{F}$ structurally.** Is there a
   syntactic property of cubic graphs (girth bound, cyclic
   connectivity bound, etc.) that characterises $\mathcal{F}$?
   Likely no clean syntactic answer: triangle blow-up shatters
   girth, dot product shatters cyclic 4-connectivity.

2. **Size of $\mathcal{F}_k$.** Define $\mathcal{F}_k$ as the
   gadget-reachable set after $k$ rounds starting from
   $\mathcal{F}_0$. How fast does $|\mathcal{F}_k|$ grow? An
   enumeration over the cubic graphs at $n = 10, 12, 14$ would
   give a concrete count.

3. **Membership for specific named families.** Are flower snarks
   $J_{2k+1}$ in $\mathcal{F}$? They have no triangles and are
   cyclically $\ge 5$-edge-connected, so they are *irreducible*
   under these two operations. Since they are not in the certified
   base $\mathcal{F}_0$ for $n > 28$, they are *outside* $\mathcal{F}$
   by our definition. (Confirming the
   [splice4.md](splice4.md) /
   [no_flower_dot_decomposition.md](no_flower_dot_decomposition.md)
   negative results from a different angle.)

## Files

- [scripts/gadget_decompose.py](../scripts/gadget_decompose.py) — algorithms + canonical graph6 + DP
- [tests/test_gadget_decompose.py](../tests/test_gadget_decompose.py) — 14 tests
- [docs/gadget_closure.md](gadget_closure.md) — forward direction (gadget compositions)
- [scripts/triangle_blowup.py](../scripts/triangle_blowup.py) — forward triangle blow-up
- [scripts/dot_product.py](../scripts/dot_product.py) — forward 3-edge-cut dot product
- [data/catalogues/nontrivial_snarks_n10_to_28.g6](../data/catalogues/) — the certified base
