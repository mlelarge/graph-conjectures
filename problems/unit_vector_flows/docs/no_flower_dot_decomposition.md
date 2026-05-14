# No flower-snark dot decomposition

Short structural lemma closing the "is $J_n$ a dot product of smaller
pieces?" question.

## Lemma

Let $G = G_1 \oplus_\pi G_2$ be a nondegenerate 3-edge-cut dot product
of two connected cubic graphs $G_1, G_2$, each containing a cycle.
Then the three through-edges of the gluing form a *cyclic*
3-edge cut of $G$.

*Proof.* The three through-edges $\{u_i w_{\pi(i)} : i = 1, 2, 3\}$
disconnect $G$ into the two pieces $G_1 \setminus \{v_1\}$ and
$G_2 \setminus \{v_2\}$. Each piece contains a cycle by hypothesis
(the assumption that $G_1, G_2$ are themselves "nontrivial", i.e.
have more than one vertex and at least one cycle). Therefore the
three-edge cut leaves two components each containing a cycle, which
is the definition of a cyclic 3-edge cut. $\square$

## Corollary

> A cyclically 4-edge-connected cubic graph cannot be expressed as
> a nontrivial 3-edge-cut dot product of two cubic graphs each
> containing a cycle.

In particular: **flower snarks $J_n$ admit no nontrivial dot
decomposition.** The classification of nontrivial snarks at $n \le 28$
in the [theorem package](nontrivial_snarks_upto_28.md) confirms
cyclic edge-connectivity $\ge 4$ for the entire family, so the same
statement holds for *every* graph in that catalogue. The dot product
gadget cannot generate the flower family (or any nontrivial snark in
the catalogue) by gluing smaller cubic pieces.

## Computational verification

`cyclic_edge_connectivity_at_most(G, 3)` in
[scripts/catalogue.py](../scripts/catalogue.py) probes for cyclic
edge cuts of size at most 3. It returns ``None`` (no such cut exists)
on every graph in the nontrivial-snark catalogue, including all
flower snarks $J_n$ for $n \in \{5, 7, 9, 11, 13\}$ that we test in
[tests/test_no_flower_dot_decomposition.py](../tests/test_no_flower_dot_decomposition.py).

## Consequence for Phase 3

The dot product gadget closure
([gadget_closure.md](gadget_closure.md)) is therefore *strictly
disjoint* from the nontrivial-snark catalogue (the closure builds
graphs *with* cyclic 3-cuts; the catalogue *excludes* them).

A natural follow-up is whether a *4-cut* splice
([splice4.md](splice4.md)) could decompose the flower family. The
answer is no, and in a stronger form than expected. The brute
enumeration `cyclic_edge_connectivity_at_most(G, k)` returns

| Graph | $n$ | $m$ | cyclic-edge-conn |
|---|---:|---:|---:|
| $J_5$ | 20 | 30 | $5$ |
| $J_7$ | 28 | 42 | $\ge 6$ |
| $J_9$ | 36 | 54 | $\ge 6$ |
| $J_{11}$ | 44 | 66 | $\ge 6$ |
| $J_{13}$ | 52 | 78 | $\ge 6$ |

So $J_5$ is cyclically *exactly* 5-edge-connected; for $n \ge 7$ the
cyclic-edge-connectivity jumps to $\ge 6$. Neither the 3-cut dot
product nor the 4-cut splice can decompose these graphs into smaller
cubic pieces; for $n \ge 7$ not even a 5-cut surgery would suffice.
