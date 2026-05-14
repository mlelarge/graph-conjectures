# 4-edge-cut splice — Phase 3c

The third gadget in the original [Phase 3 plan](cdc_gadget_plan.md): cut
a cubic graph along a cyclic 4-edge cut $C \subset E(G)$ and re-glue
the two pieces along a chosen matching of their boundaries. Together
with [triangle blow-up](../scripts/triangle_blowup.py) and
[dot product](../scripts/dot_product.py), this completes the trio of
structural surgeries that preserve $S^2$-flow existence in closed form.

## Setup

A **4-bordered cubic piece** $G_i$ is a connected graph in which four
distinguished *boundary* vertices have degree 2 and all other vertices
have degree 3. The boundary vertices come with an order
$\bigl(b_1^{(i)}, b_2^{(i)}, b_3^{(i)}, b_4^{(i)}\bigr)$.

The **splice** $G_1 \oplus_4^\mu G_2$ along a bijection
$\mu : \{1,2,3,4\} \to \{1,2,3,4\}$ adds four through-edges
$b_i^{(1)} b_{\mu(i)}^{(2)}$. The result is a connected cubic graph.

Inverse: given a cubic graph $G$ and a cyclic 4-edge cut
$C = \{e_1, e_2, e_3, e_4\}$, removing $C$ leaves two 4-bordered cubic
pieces whose splice (with the natural matching) is $G$.

## Boundary 4-tuple

Suppose $G_i$ carries a partial $S^2$-flow $\varphi_i$ satisfying
Kirchhoff at every *internal* vertex. The Kirchhoff equation at a
boundary vertex $b_j^{(i)}$ has a deficit of one term — the value of
the cut edge that closes the equation. Define the **boundary 4-tuple**

$$
T_i \,=\, (t_1^{(i)}, t_2^{(i)}, t_3^{(i)}, t_4^{(i)})
\quad\text{with}\quad
t_j^{(i)} \;=\; -\!\!\!\sum_{e \ni b_j^{(i)}} \!\! \sigma_i(b_j^{(i)}, e)\,\varphi_i(e),
$$

so $t_j^{(i)}$ equals the value of the cut edge incident to
$b_j^{(i)}$, oriented *outward* from the piece. Summing
$\varphi_i(\text{vertex})$ over all of $G_i$, the global Kirchhoff
identity forces

$$
\sum_{j=1}^4 t_j^{(i)} \;=\; 0.
$$

Each $t_j^{(i)}$ is a unit vector if the partial flow is a unit-vector
flow on $G_i$'s internal edges *and* the missing cut-edge value would
be a unit vector — i.e., $T_i$ is a 4-tuple on $S^2$ summing to zero.

## Splice condition

For the splice to admit an $S^2$-flow extending $\varphi_1$ and (a
rotation of) $\varphi_2$, the through-edge values must satisfy
Kirchhoff at *both* of their endpoints. At $b_i^{(1)}$: the cut-edge
value oriented outward equals $t_i^{(1)}$. At $b_{\mu(i)}^{(2)}$: the
same edge is incoming, so its outward value is $-t_i^{(1)}$. Kirchhoff
then forces (after rotating $\varphi_2$ by some $R \in \mathrm{SO}(3)$):

$$
R\,t_{\mu(i)}^{(2)} \;=\; -t_i^{(1)}, \quad i = 1, 2, 3, 4.
$$

The negation convention is the splice analogue of the dot product
alignment $R\,T_2[\pi(i)] = -T_1[i]$, with a $4 \times 3$ matching
instead of $3 \times 3$.

## Moduli space

The space of 4-tuples of unit vectors in $\mathbb{R}^3$ summing to
zero, modulo $\mathrm{SO}(3)$, has dimension
$4 \cdot 2 - 3 = 5$. Generically two such 4-tuples are *not*
$\mathrm{SO}(3)$-equivalent under any permutation. Contrast with the
3-tuple case (dot product): there the moduli space is $3 \cdot 2 - 3
= 3$ minus the $2$-dimensional "sum to zero" constraint $= 1$, i.e., a
single chirality parameter — a generic 3-tuple is determined up to
$\mathrm{SO}(3)$ by its chirality alone, so alignment almost always
succeeds (subject to flipping a witness chirality with a retry).

Practically: when the two boundary 4-tuples come from *generic*
witnesses on the two pieces, alignment fails. This is why the gadget
is structurally heavier than dot product. The cases where alignment
*does* succeed correspond to the special 4-cut geometries that already
exist in the original cubic graph — i.e., the *inverse* cut.

## Implementation

[scripts/splice4.py](../scripts/splice4.py) provides:

- `find_cyclic_4_cuts(G, max_cuts=None)` — enumerate cyclic 4-edge
  cuts of $G$. Brute search over $\binom{m}{4}$ subsets; checks that
  the residue has $\ge 2$ components each containing a cycle. Feasible
  for $m \lesssim 70$ (Petersen, Blanuša, $J_5, J_7, J_9, J_{11}$).
- `cut_at_4(G, cut)` — slice $G$ along a given 4-cut into the two
  4-bordered cubic pieces, returning the boundary vertex lists in the
  cut-edge order and the original-to-piece relabel maps.
- `boundary_4tuple(piece, witness, boundary)` — compute the
  $4 \times 3$ boundary tuple given a (partial) flow on the piece.
- `align_4tuples(T2, T1, tol)` — search the 24 permutations for the
  $(R, \pi)$ with $R\,T_2[\pi] = -T_1$, returning the first whose
  Kabsch residual is below $\mathrm{tol}$.
- `splice4_witness(piece_1, witness_1, boundary_1, piece_2, witness_2,
  boundary_2, matching=None, tol=1e-7)` — assemble the spliced graph,
  rotate the second flow, write the through-edge values, and verify
  the resulting full $S^2$-flow via `verify_witness`.

## Verified instances

| Operation | Input | Boundary 4-tuple match | $\max$ Kirchhoff residual |
|---|---|---:|---:|
| Self-splice round-trip | Blanuša-1 (18) | $T_2 = -T_1$ exactly | $3.8 \cdot 10^{-16}$ |

The self-splice test in
[tests/test_splice4.py](../tests/test_splice4.py) cuts Blanuša-1 at its
unique cyclic 4-cut, restricts the global witness to the two pieces,
re-splices, and verifies the spliced flow. Alignment recovers
$R = I$ and the identity permutation as expected.

The four alignment unit tests cover the achiral tetrahedral 4-tuple,
its negation, and a generic non-trivial $(R, \pi)$ pair.

## Flower snarks: a structural wall

The eventual goal — reach the flower family $J_{2k+1}$ by gluing
smaller cubic pieces — fails for the same reason as the dot product,
just one step later. Empirically (via `find_cyclic_4_cuts`):

| Graph | $n$ | $m$ | cyclic 4-cuts found |
|---|---:|---:|---:|
| $J_5$ | 20 | 30 | 0 |
| $J_7$ | 28 | 42 | 0 |
| $J_9$ | 36 | 54 | 0 |
| $J_{11}$ | 44 | 66 | 0 |

These graphs are *cyclically $\ge 5$-edge-connected*, not just
cyclically 4-edge-connected as the textbook bound states. So neither a
3-edge-cut dot product
([no_flower_dot_decomposition.md](no_flower_dot_decomposition.md))
nor a 4-edge-cut splice can decompose them into smaller cubic pieces.

Reaching the flower family by gadget composition would require a
5-edge-cut splice or beyond. The 5-cut case is genuinely heavier: the
moduli of 5 unit vectors summing to zero in $\mathbb{R}^3$ has
dimension $5 \cdot 2 - 3 = 7$ modulo $\mathrm{SO}(3)$, and the
removed pieces are no longer "almost cubic" — boundary vertices have
degree 2 in the same way, but coordinating five through-edges' values
against a 7-dimensional moduli space is a substantial step beyond the
SO(3) Kabsch trick.

## What the splice *does* cover

The splice is the right tool for the cubic-snark world *outside* the
flower family — most nontrivial snarks at $n \le 28$ are cyclically
exactly 4-edge-connected (the catalogue's `cyclic_edge_conn_at_most`
column distinguishes them). Combined with triangle blow-up and dot
product, the closure under these three gadgets is therefore much
larger than the closure under blow-up and dot product alone, while
still excluding the flower family.

A complete *closure-set enumeration* — what graphs are reachable from
the certified base $\mathcal{F}_0$ by $k$ gadget operations — remains
a useful open subproject (see
[gadget_closure.md](gadget_closure.md) "What's not yet done").

## Files

- [scripts/splice4.py](../scripts/splice4.py)
- [tests/test_splice4.py](../tests/test_splice4.py)
- [docs/no_flower_dot_decomposition.md](no_flower_dot_decomposition.md) — the analogous 3-cut obstruction
- [docs/gadget_closure.md](gadget_closure.md) — Phase 3 summary
