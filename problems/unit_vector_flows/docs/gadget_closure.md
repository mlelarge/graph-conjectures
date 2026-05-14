# Gadget closure — Phase 3 result

Two constructive cubic-graph operations that preserve $S^2$-flow
existence are implemented and validated:

- **Triangle blow-up** ([scripts/triangle_blowup.py](../scripts/triangle_blowup.py))
- **3-edge-cut dot product** ([scripts/dot_product.py](../scripts/dot_product.py))

Both are *constructive* in the strong sense: given an $S^2$-flow
witness on the input graph(s), the new $S^2$-flow on the output graph
is produced in closed form and verified by the existing
`witness.verify_witness` at Kirchhoff residual $\sim 10^{-16}$.

## Theorem (informal)

> Let $\mathcal{F}_0$ be the set of 3 247 nontrivial snarks at $n \le 28$
> for which the [interval-Krawczyk theorem package](nontrivial_snarks_upto_28.md)
> certifies an $S^2$-flow. Let $\mathcal{F}$ be the closure of
> $\mathcal{F}_0$ under triangle blow-up and 3-edge-cut dot product.
> Then every $G \in \mathcal{F}$ admits a constructive $S^2$-flow,
> assembled from the base certificates and the closed-form gadget
> extensions.

$\mathcal{F}$ is *not* contained in the cubic-snark world: triangle
blow-up creates a 3-cycle, so the blown-up graph has girth $\le 3$ and
loses snark status. But $\mathcal{F}$ is strictly larger than
$\mathcal{F}_0$ as a class of cubic graphs admitting an $S^2$-flow,
and the construction is *parametric* in the gadget sequence (no
per-graph Krawczyk needed beyond the 3 247 base certs).

## Closed-form rules

### Triangle blow-up at $v \in G$

Original spoke values $f_1, f_2, f_3 \in S^2$ at $v$ with
$f_1 + f_2 + f_3 = 0$. New triangle edges get

$$
g_{12} = \frac{f_2 - f_1}{3} + \varepsilon \sqrt{\tfrac23}\,\hat n,
\qquad g_{13} = -f_1 - g_{12}, \qquad g_{23} = -f_2 + g_{12},
$$

with $\hat n = (f_3 \times (f_2 - f_1))/\|\cdot\|$ a unit normal and
$\varepsilon \in \{\pm 1\}$ the chirality. Each $g_{ij}$ is unit and
the three Kirchhoff equations at the new triangle vertices vanish
identically.

### Dot product $G_1 \oplus_\pi G_2$ at $v_1, v_2$ with permutation $\pi$

Let $T_1 = (f_1, f_2, f_3)$ be the boundary triple at $v_1$ in $G_1$,
$T_2 = (h_1, h_2, h_3)$ at $v_2$ in $G_2$. The through-edge
$u_i \leftrightarrow w_{\pi(i)}$ carries value $-f_i$. Consistency
forces $h_{\pi(i)} = -f_i$, i.e., $T_2$ must equal $-T_1$ under $\pi$
after rotating $G_2$'s flow by some $R \in \mathrm{SO}(3)$.

Such an $(R, \pi)$ exists whenever $T_1$ and $T_2$ have matching
chirality. `align_to_negation` enumerates the 6 perms and Kabsch-solves
for $R$; the first low-residual pair wins. If no perm works (opposite
chirality), the construction returns failure cleanly. In practice
witnesses found by Levenberg-Marquardt land on either chirality with
roughly equal probability, so a single retry with a different seed
flips $G_2$'s chirality and the gluing succeeds.

## Verified instances

| Operation | Input | Output | $\max$ Kirchhoff residual |
|---|---|---|---:|
| Triangle blow-up at $v=0$, $\varepsilon=+1$ | Petersen (10) | 12-vertex cubic | $1.6 \cdot 10^{-16}$ |
| Triangle blow-up | Blanuša-1 (18) | 20-vertex cubic | $1.4 \cdot 10^{-16}$ |
| Triangle blow-up | $J_5$ (20) | 22-vertex cubic | $1.7 \cdot 10^{-16}$ |
| Dot product | Petersen $\oplus$ Petersen | 18-vertex cubic | $1.9 \cdot 10^{-16}$ |
| Dot product | Petersen $\oplus$ Blanuša-1 | 26-vertex cubic | $4.6 \cdot 10^{-16}$ |
| Dot product | $J_5 \oplus J_5$ | 38-vertex cubic | $5.9 \cdot 10^{-16}$ |
| Iterated dot product | Petersen$^{\oplus 4}$ | 34-vertex cubic | $5.4 \cdot 10^{-16}$ |
| Iterated dot product | Petersen $\oplus J_5 \oplus$ Blanuša-1 | 44-vertex cubic | $4.5 \cdot 10^{-16}$ |

All are in [tests/test_triangle_blowup.py](../tests/test_triangle_blowup.py)
and [tests/test_dot_product.py](../tests/test_dot_product.py). The 8
gadget tests + the 4 weighted-CDC tests + the 5 H4 calibration tests
+ the 7 CDC structural tests + the 39 base regression tests now sum
to **71 / 71** passing.

## Cross-cuts

### With the weighted-CDC certificate

The weighted-CDC ansatz on a base snark gives a witness; the gadget
operations propagate that witness through triangle blow-up and dot
product. So if Petersen / Blanuša-2 / $J_5$ admit weighted-CDC
certificates (they do; see
[weighted_cdc_certificates.md](weighted_cdc_certificates.md)), then
every iterated gadget composition of those graphs also admits an
$S^2$-flow obtained by composing the weighted-CDC base with the
gadget extensions.

### With the failed flower-CDC attempt

The flower family $J_{2k+1}$ was *not* shown to admit an explicit
parametric CDC ([flower_snarks_cdc.md](flower_snarks_cdc.md)).
However, dot-product chains $J_5 \oplus J_5 \oplus \dots$ give a
constructive infinite sequence of $S^2$-flow-equipped cubic snarks
whose size grows linearly in the chain length. These chains are *not*
the flower snarks themselves, but they fill the same role for
"explicit infinite-family $S^2$-flow on snarks".

A direct decomposition $J_n \cong J_m \oplus X$ for some $X$ would
turn this into a true flower theorem. We have not constructed such
$X$; doing so is a graph-isomorphism task that's worth a focused
effort but not pursued here.

## What's not yet done

1. **Splice / 4-cut surgery (Phase 3c).** The third gadget in the
   original plan. Structurally heavier than dot product because a
   4-edge cut on a cubic graph generally leaves the two sides
   non-cubic; the gluing semantics need more care.
2. **Closure-set enumeration.** What graphs are reachable from
   $\mathcal{F}_0$ by $k$ gadget operations? A reachability search
   would give explicit infinite families.
3. **Flower-snark decomposition.** If $J_n$ is dot-product-reducible
   into smaller pieces, find the pieces. Open question;
   computationally expensive search.

## Files

- [scripts/triangle_blowup.py](../scripts/triangle_blowup.py)
- [scripts/dot_product.py](../scripts/dot_product.py)
- [tests/test_triangle_blowup.py](../tests/test_triangle_blowup.py)
- [tests/test_dot_product.py](../tests/test_dot_product.py)
- [docs/cdc_gadget_plan.md](cdc_gadget_plan.md) — original plan
- [docs/weighted_cdc_certificates.md](weighted_cdc_certificates.md) — Phase 1
- [docs/flower_snarks_cdc.md](flower_snarks_cdc.md) — Phase 2 wall
