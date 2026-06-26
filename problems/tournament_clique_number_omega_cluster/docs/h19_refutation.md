# H19 is false: the iterated directed-triangle refutation

**Status: proved refutation.** The proposed bound

$$
\tag{H19}
\vec\omega(C_3[H])\leq \vec\omega(H)+1
\qquad\text{whenever }\vec\omega(H)\geq3
$$

cannot hold for every tournament $H$.

The counterexample is forced inside the standard iterated directed-triangle
family. Let

$$
B_0=TT_1,\qquad B_i=C_3[B_{i-1}]\quad(i\geq1).
$$

Thus $B_i=\widetilde S_{i+1}$ in the repository's notation and
$|V(B_i)|=3^i$.

## Theorem

There are infinitely many indices $i\geq3$ such that

$$
\vec\omega(B_i)>\vec\omega(B_{i-1})+1.
$$

Moreover, at least one such index lies in $\{3,\ldots,23\}$. Consequently H19
is false, with $H=B_{i-1}$ for infinitely many indices.

## Proof

Write $w_i=\vec\omega(B_i)$.

First, $w_2=3$. The standard substitution lower bound gives
$w_2\geq2+2-1=3$. Conversely, $B_2=C_3[C_3]$ has a $3$-dicolouring:
use colour sets $\{1,2\}$, $\{2,3\}$, and $\{3,1\}$ on its three outer
copies. Each colour meets at most two copies, whose union is ordered in one
direction, so every colour class is acyclic. Hence
$w_2\leq\vec\chi(B_2)\leq3$.

Assume H19. The known lower bound
$\vec\omega(\widetilde S_n)\geq n$ gives $w_j\geq j+1$, so
$w_{i-1}\geq3$ for every $i\geq3$. H19 therefore applies at every subsequent
step:

$$
w_i=\vec\omega(C_3[B_{i-1}])\leq w_{i-1}+1.
$$

Starting from $w_2=3$, induction gives

$$
\tag{1} w_i\leq i+1\qquad(i\geq2).
$$

Now use the partial order decomposition number $pod(D)$, the minimum number
of partial-order digraphs whose arc sets cover $A(D)$. Two facts are enough:

1. For every digraph $D$,
   $$
   \tag{2}\vec\chi(D)\leq\vec\omega(D)^{pod(D)}.
   $$
   Indeed, in an optimal backedge order, the backedge graph contributed by
   each partial order is a perfect comparability graph and is colourable with
   at most $\vec\omega(D)$ colours. The tuple of these colourings properly
   colours the full backedge graph.

2. $pod(B_i)\leq3$ for every $i$. The three arcs of $C_3$ give a
   three-part partial-order decomposition. To see that substitution preserves
   this bound, take decompositions $P_1,\ldots,P_m$ and
   $P'_1,\ldots,P'_m$ of the outer and substituted digraphs. For every $r$,
   substitute $P'_r$ for the replaced vertex in $P_r$. The resulting
   relation is still acyclic and transitive, and the $m$ resulting arc sets
   cover the substituted digraph.

Also,

$$
\tag{3}\vec\chi(B_i)\geq\frac32\,\vec\chi(B_{i-1}).
$$

To see this, consider any dicolouring of the three copies of $B_{i-1}$ in
$B_i$. A colour cannot occur in all three copies, since one vertex of that
colour from each copy would form a monochromatic directed triangle. Counting
colour-copy incidences gives
$3\vec\chi(B_{i-1})\leq2\vec\chi(B_i)$.

In fact the matching palette construction gives the exact recurrence

$$
\vec\chi(B_0)=1,\qquad
\vec\chi(B_i)=\left\lceil\frac32\vec\chi(B_{i-1})\right\rceil.
$$

Combining this with (2) and $pod(B_i)\leq3$ yields

$$
\tag{4}w_i\geq\left\lceil\vec\chi(B_i)^{1/3}\right\rceil
\geq(3/2)^{i/3}.
$$

At $i=23$, the exact recurrence gives $\vec\chi(B_{23})=18206$, so
equations (1) and (4) are incompatible:

$$
w_{23}\leq24,
\qquad
w_{23}\geq\left\lceil18206^{1/3}\right\rceil=27.
$$

Therefore at least one step $i\in\{3,\ldots,23\}$ violates H19.

Finally, if only finitely many steps violated H19, then from some index onward
$w_i\leq w_{i-1}+1$, making $w_i=O(i)$. This contradicts the exponential lower
bound (4). Hence infinitely many steps violate H19. $\square$

## Consequences

- The Route-2 Selection, Cycle-Breaking, and full-raiser-or-partners
  conjectures cannot hold uniformly.
- H25 remains a valid identity, but its desired path need not exist for every
  $H$.
- The argument proves existence of a counterexample among
  $B_2,\ldots,B_{22}$ as inner tournaments and infinitely many later
  counterexamples. It does not identify the first failing index.

The input (2), substitution closure of $pod$, and the bound (4) are from
Aboulker et al., *Decomposing tournaments into comparability graphs*,
[arXiv:2606.07748](https://arxiv.org/abs/2606.07748), submitted June 5, 2026.
