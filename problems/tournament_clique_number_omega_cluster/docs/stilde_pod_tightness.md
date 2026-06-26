# The pod-tightness problem for the iterated directed triangle

Put

$$
B_k=C_3^k[TT_1]=\widetilde S_{k+1},
\qquad
W_k=\vec\omega(B_k).
$$

Thus $|V(B_k)|=3^k$, the largest transitive subtournament has order
$2^k$, and

$$
\vec\chi(B_k)=\Theta((3/2)^k).
$$

The known growth constant is

$$
\rho=\lim_{k\to\infty}W_k^{1/k},
\qquad
(3/2)^{1/3}\le\rho\le5^{1/4}.
$$

This note isolates exactly what must happen for the lower endpoint to be
tight.

## 1. The canonical three posets

Represent a vertex of $B_k$ by a word in $\{0,1,2\}^k$. For distinct words
$x,y$, let $j$ be their first differing coordinate. The tournament arc is
$x\to y$ when $y_j=x_j+1\pmod3$.

Colour this arc by $c=x_j$. Let $P_c^k$ contain the arcs of colour $c$.
Each $P_c^k$ is a partial order. Indeed, suppose $x\to y$ and $y\to z$
both have colour $c$, and their first differing coordinates are $p$ and
$q$. We cannot have $p=q$. If $p<q$, then $x$ and $z$ first differ at
$p$ as $c,c+1$; the case $q<p$ is symmetric. Thus $x\to z$ also has
colour $c$.

Fix a total order $\pi$ of $V(B_k)$. Let $Q_c(\pi)$ be the suborder of
$P_c^k$ consisting of arcs that are backward in $\pi$, and put

$$
q_c(\pi)=\operatorname{height}Q_c(\pi).
$$

If $K(\pi)$ is the clique number of the full backedge graph, then

$$
q_c(\pi)\le K(\pi)
\quad(c=0,1,2).
$$

## 2. Rank cells and the exact losses in the cubic proof

Let $r_c(v)$ be the longest-chain rank of $v$ in $Q_c(\pi)$. Vertices
with the same rank triple

$$
R(v)=(r_0(v),r_1(v),r_2(v))
$$

have no backward arc between them: a backward arc has some colour $c$,
and its endpoints have different $r_c$-ranks. Consequently every rank
cell is transitive.

Let

$$
Q(\pi)=q_0(\pi)q_1(\pi)q_2(\pi)
$$

and let $M(\pi)$ be the number of occupied rank triples. Then

$$
\boxed{
\vec\chi(B_k)\le\chi(B(B_k,\pi))
\le M(\pi)\le Q(\pi)\le K(\pi)^3.
}
\tag{1}
$$

Also, every transitive set in $B_k$ has at most $2^k$ vertices: it meets
at most two top modules, and induction gives the bound. Hence

$$
3^k\le M(\pi)2^k.
\tag{2}
$$

Equations (1)--(2) give a self-contained version of the pod-cube lower
bound. More importantly, they factor its slack exactly:

$$
\boxed{
\frac{K(\pi)^3}{(3/2)^k}
=
\frac{K(\pi)^3}{Q(\pi)}
\cdot
\frac{Q(\pi)}{M(\pi)}
\cdot
\frac{M(\pi)2^k}{3^k}.
}
\tag{3}
$$

All three factors are at least one. Therefore
$\rho=(3/2)^{1/3}$ holds if and only if there is a sequence of orders
for which all three factors in (3) are subexponential.

This is much stronger than merely asking for three balanced layer
heights.

## 3. Generic comparability arguments cannot improve the exponent

Chudnovsky, Cook, Davies, Kim, and Oum proved in June 2026 that for every
$d,k$ there is a graph $G$ which is a union of $d$ comparability graphs
and satisfies

$$
\omega(G)=k,\qquad \chi(G)=k^d.
$$

Thus the product-colouring exponent $d$ is exactly sharp for arbitrary
unions of $d$ comparability graphs. In particular, no improvement of the
cube can use only the statement

> the backedge graph is a union of three comparability graphs.

An improvement for $B_k$ must use the common first-difference geometry
of $P_0^k,P_1^k,P_2^k$, or the fact that these layers arise
simultaneously from one tournament order. The extremal construction in
that paper does not settle this more rigid problem.

Reference: Chudnovsky--Cook--Davies--Kim--Oum, *On the chromatic number
of the union of comparability graphs*,
[arXiv:2606.09415](https://arxiv.org/abs/2606.09415).

## 4. The canonical layer-volume parameter

Define

$$
L_k=\min_\pi Q(\pi).
$$

The ordinary lexicographic order gives $L_k\le2^k$: two canonical posets
have no backward arc and the third has a backward chain of size $2^k$.
Equation (1) gives

$$
\vec\chi(B_k)\le L_k.
$$

The sequence $(L_k)$ is submultiplicative. Given orders of $B_a$ and
$B_b$, order $B_{a+b}=B_a[B_b]$ blockwise. A backward $P_c$-chain meets
at most $q_c(B_a)$ blocks and uses at most $q_c(B_b)$ vertices in each,
and equality is obtained by composing maximum chains. Therefore the
three $q_c$ values multiply coordinatewise, and

$$
L_{a+b}\le L_aL_b.
$$

Consequently the limit

$$
\lambda=\lim_{k\to\infty}L_k^{1/k}
$$

exists, with

$$
\frac32\le\lambda\le2,
\qquad
\rho^3\ge\lambda.
\tag{4}
$$

Proving $\lambda>3/2$ would immediately prove that the pod-cube lower
bound is not tight for the tower.

## 5. Exact finite layer volumes

The SAT encoding in `scripts/decide_stilde_layer_product.py` bounds each
$q_c$ directly by forbidding reversed chains in $P_c^k$. It gives

$$
\boxed{
L_1=2,\qquad L_2=4,\qquad L_3=8,\qquad L_4=15.
}
$$

At depth $3$, all cap triples with product below $8$ are UNSAT, while
there is an order with

$$
(q_0,q_1,q_2)=(2,2,2),\qquad K=4.
$$

This order is simultaneously layer-volume-minimal and
$\vec\omega$-optimal, but it still has

$$
K^3/Q=64/8=8.
$$

At depth $4$, all cap triples with product below $15$ are UNSAT. The
only feasible cap permutations below $16$ are the permutations of
$(1,3,5)$. One such order has

$$
Q=15,\qquad M=15,\qquad K=11.
$$

In the opposite direction, a certified width-$5$ order has

$$
K=5,\qquad(q_0,q_1,q_2)=(5,5,5),\qquad Q=125.
$$

These are two points on the finite Pareto frontier; they do not prove
that the joint optimum at depth $4$ is either endpoint.

The lesson is decisive: minimizing the pod volume and minimizing the
full mixed-colour clique are already different objectives at depth
$4$.

Reproduce the exact decisions with

```bash
.venv/bin/python scripts/decide_stilde_layer_product.py \
  --depth 3 --cross-check
.venv/bin/python scripts/decide_stilde_layer_product.py \
  --depth 4 --cross-check
.venv/bin/python scripts/decide_stilde_layer_product.py \
  --depth 3 --clique-cap 4 --cross-check
```

### 5.1 Depth 5: first probes (exact value $L_5=24$ later resolved in §11)

Depth-5 ($\widetilde S_6$, order 243) probes with the same encoding:

| caps | product | SAT? | time |
|---|---|---|---|
| $(2,2,3)$ | 12 | UNSAT | 43s |
| $(1,3,4)$ | 12 | UNSAT | 76s |
| $(2,2,4)$ | 16 | UNSAT | 386s |
| $(3,3,3)$ | 27 | **SAT** | 39s |

So among *buildable* cap triples, $16<L_5\le27$ — the layer volume does **not**
collapse toward $d_6=12$. **Caveat:** as at depth 4, the true minimiser is expected to
be a *skewed* triple (depth 4's optimum was $(1,3,5)$ with a height-5 layer); a height-$\ge5$
layer at depth 5 needs $\ge6$-chains in a poset (the height-4 enumeration is already
$1.98\times10^7$ chains/poset), so the exact $L_5$ is computationally out of reach. **Depth 4
is the exact frontier** for $L_k$, exactly as it is for $w_n$.

**What the data says about $\lambda$ — CORRECTED (see §11).** The claim above that
"depth 4 is the exact frontier" is **superseded**: §11 computes $L_5=24$ exactly with a
level-labeling SAT encoding. With the full exact sequence
$$L_k=2,4,8,15,24\quad(k=1,\dots,5),\qquad
L_k^{1/k}=2,\;2,\;2,\;1.968,\;1.888\ \Rightarrow\ \lambda\le 24^{1/5}=1.888,$$
and $\lambda\ge3/2$ (§4), so $\lambda\in[1.5,1.888]$.

An earlier version of this paragraph read the ratio to the dichromatic number as
"growing" evidence for $\lambda\approx1.9$–$2$. **That reading is retracted, for two
reasons.** (i) The ratio was mis-labeled $L_k/d_{k+1}$; the printed values
$1,\tfrac43,\tfrac85,\tfrac{15}8$ are $L_k/d_k$ (with $d_k=2,3,5,8$), not $L_k/d_{k+1}$.
(ii) More importantly, $L_k/d_k=1,1.33,1.60,1.875,\mathbf{2.0}$ is the *rising left flank
of a transient hump*: a cubic-over-exponential ratio must rise for small $k$ and then
decay to $0$, since $d_k=\Theta((3/2)^k)$ is exponential. Extrapolating its up-slope to
$\lambda\approx2$ is exactly the pre-asymptotic error exposed in §11. The decisive
correction is the **step ratio**, which is *falling*:
$$\frac{L_k}{L_{k-1}}=2,\;2,\;1.875,\;\mathbf{1.6}\quad(k=2,\dots,5),$$
dropping toward $3/2$. So the data now **leans toward $\lambda=3/2$ (pod-tight)**, the
opposite of the earlier reading; the consequence $\rho\gtrsim1.24$ is withdrawn and only
the proven $\rho\ge(3/2)^{1/3}=1.1447$ survives. $\lambda\in[3/2,1.888]$ remains genuinely
open. Proving $\lambda>3/2$ still requires an asymptotic *lower* bound on $L_k$ beyond
$d_k$ (the $L_k^{1/k}$ values only bound $\lambda$ from above); the structural route
(§6–§9) is unchanged.

## 6. The correct asymptotic dichotomy

For an order $\pi$, consider the pair

$$
(Q(\pi),K(\pi)).
$$

Pod-tightness is equivalent to the existence of orders $\pi_k$ with

$$
Q(\pi_k)=(3/2)^{k+o(k)}
\quad\text{and}\quad
\frac{K(\pi_k)^3}{Q(\pi_k)}=e^{o(k)}.
\tag{5}
$$

There are therefore two independent ways to prove strict growth:

1. **Layer-volume gap:** prove $\lambda>3/2$.
2. **Pareto separation:** prove that every order with
   $Q(\pi)\le(3/2+o(1))^k$ has
   $K(\pi)^3/Q(\pi)\ge(1+\varepsilon)^k$ for some fixed
   $\varepsilon>0$.

Conversely, a proof of pod-tightness must build orders satisfying both
requirements in (5). Optimizing either coordinate alone is insufficient.

## 7. A structural route through near-maximal fibres

A transitive subset of $B_k$ is represented by a rooted ternary tree in
which each occupied node has at most two occupied children. If $X$ is
uniform on such a set $S$, the entropy chain rule gives

$$
\log_2|S|
\le
\sum_{j=1}^k
\Pr[\text{the occupied prefix of }X\text{ has two children at level }j].
$$

Thus a transitive set of size $2^{k-o(k)}$ must branch into two children
at all but $o(k)$ levels along a typical leaf.

If (3) were asymptotically tight, almost all of the rank-box volume
would be occupied up to a subexponential multiplicative deficit, and a
size-biased typical rank cell would have size $2^{k-o(k)}$ on the
exponential scale. The cells would therefore form an almost-tiling by
near-complete binary subtrees, while their ranks must simultaneously be
generated by predecessor chains in the three cyclic posets.

This yields a concrete theoretical target:

> Prove that disjoint rank cells generated by the three canonical
> predecessor relations cannot almost-tile the ternary tree by
> near-complete binary subtrees.

Any exponential deficit in this tiling proves $\rho>(3/2)^{1/3}$.

### 7.1 Entropy diagnostic on the SAT-optimal orders (empirical)

`scripts/stilde_rank_entropy.py` measures, for a given order $\pi$, the
per-level Shannon entropy of the rank-triple (fibre) distribution
$H_{\text{rank}}/k$ and the conditional within-fibre entropy
$H_{\text{cond}}/k$, with $H_{\text{rank}}+H_{\text{cond}}=\log_2 3$ per
level by the chain rule.

Pod-tightness ($M\approx(3/2)^k$ fibres, each of size $\approx 2^k$) would
force $H_{\text{rank}}/k\to\log_2(3/2)=0.585$ and $H_{\text{cond}}/k\to1$.
Applied to the **minimum-volume witness orders** returned by
`decide_stilde_layer_product.py`:

| order | $k$ | occupied fibres $M$ | box $Q$ | $\log_2 M/k$ | $H_{\text{rank}}/k$ | $H_{\text{cond}}/k$ |
|---|---|---|---|---|---|---|
| min-vol $(2,2,2)$, $K{=}4$ | 3 | 7 | 8 | 0.936 | 0.889 | 0.696 |
| min-vol $(1,3,5)$, $K{=}11$ | 4 | 15 | 15 | 0.977 | 0.908 | 0.677 |
| width-opt $(5,5,5)$, $K{=}5$ | 4 | — | 125 | — | 1.016 | 0.569 |

Two readings within the depth-$\le4$ window:

1. **$M/Q\approx1$** (7/8, 15/15): the minimum-volume orders already
   almost-fill their rank box, so there is *no §7 tiling deficit inside the
   box* to exploit. The cells do almost-tile — the box is simply too big.
2. **$\log_2 M/k$ rises** ($0.936\to0.977$ toward $1$) within this window.

⚠️ **Interpretation corrected (see §11).** An earlier version read item 2 as
corroborating $\lambda\approx2$. That is **retracted**: the rise is the same
pre-asymptotic transient as the §5.1 ratio (a cubic-regime artifact — $L_k$
matches the cake numbers $2,4,8,15$ for $k\le4$, see §11), not an asymptotic
signal. Once $L_5=24$ is included, $\lambda\le1.888$ and the step ratio falls
to $1.6$, so the entropy diagnostic is **consistent with $\lambda=3/2$**, not
$\lambda\approx2$. The diagnostic measures a transient and supplies no
asymptotic lower bound; that must still come from the structural recursion
(§9).

## 8. Recommended next proof target

The most economical next theorem is the layer-volume gap

$$
\boxed{\lambda>3/2.}
$$

It avoids the full mixed-colour clique and asks only for a simultaneous
Erdős--Szekeres theorem for the three recursive posets. The recursive
state must retain prefix/suffix chain profiles inside the three top
modules; the scalar triple $(q_0,q_1,q_2)$ is not closed under arbitrary
interleaving.

If this fails and constructions drive $L_k$ down to
$(3/2)^{k+o(k)}$, the next target is the Pareto-separation statement in
§6. Either outcome advances the true growth-rate question.

## 9. The crossing recursion, and why scalar routes fail

This section records the recursion for the layer heights $q_c$ under the
substitution $B_k=C_3[B_{k-1}]$, proves it, and then reports two natural
lower-bound routes that it suggests — **both of which we refute
computationally.** The upshot sharpens §8: a proof of $\lambda>3/2$ cannot
use any *scalar* (per-colour or per-cell) invariant; it must carry the
prefix/suffix profile.

### 9.1 The crossing recursion (proved)

Decompose $B_k$ into modules $M_0,M_1,M_2$ (top coordinate fixed), each a
copy of $B_{k-1}$, with the cyclic inter-module relation $M_b\Rightarrow
M_{b+1}$ carrying colour $b$ at the top coordinate. A backward colour-$c$
chain in an order $\pi$ is $P_c$-increasing and $\pi$-decreasing. Because
the only *top-level* colour-$c$ comparabilities run $M_c\Rightarrow
M_{c+1}$, and an $M_{c+2}$ vertex is $P_c$-incomparable to every $M_c$ and
$M_{c+1}$ vertex, every colour-$c$ chain lies **either** entirely inside
$M_{c+2}$, **or** inside $M_c\cup M_{c+1}$, crossing once — with the $M_c$
part on the $\pi$-suffix (large positions, since $M_c$ is $P_c$-below
$M_{c+1}$ hence $\pi$-above) and the $M_{c+1}$ part on the prefix. Hence

$$
\boxed{\;
q_c(\pi)=\max\Big(\,q_c(\pi|_{M_{c+2}}),\;
\max_{p}\big[\,\mathrm{suf}_c(M_c,p)+\mathrm{pre}_c(M_{c+1},p)\,\big]\Big)
\;}
\tag{9.1}
$$

where $\mathrm{suf}_c(M,p)$ / $\mathrm{pre}_c(M,p)$ are the longest backward
colour-$c$ chains in module $M$ at $\pi$-positions $\ge p$ / $<p$.

**Verification.** `scripts/stilde_crossing_recursion.py` checks (9.1)
against the direct computation of $q_c$ **exhaustively** for all $6$ orders
at depth 1 and all $362{,}880=9!$ orders at depth 2, plus $2000$ random
orders at depth 3. (Test: `tests/test_stilde_crossing_recursion.py`.)

### 9.2 Refuted route A — the cyclic crossing-sum obstruction

The recursion invites the intuition: the three crossings are cyclically
linked (colour $c$'s sum needs $M_c$ *late* and $M_{c+1}$ *early* in $\pi$;
the three "late$\succ$early" demands form a 3-cycle), so the minimiser
cannot make all three crossings degenerate to a $\max$ — at least one
colour is forced into a genuine **sum** $X_c=a_c^{(c)}+a_{c+1}^{(c)}$,
which would lift the product.

**This is false.** On the depth-4 minimum-volume optimum
($L_4=15$, witness order from `decide_stilde_layer_product.py`):

| colour $c$ | within $(M_c,M_{c+1},M_{c+2})$ | crossing $X_c$ | $q_c$ | sum? |
|---|---|---|---|---|
| 0 | $(1,1,1)$ | 1 | 1 | no |
| 1 | $(2,3,3)$ | 3 | 3 | no |
| 2 | $(5,3,5)$ | 5 | 5 | no |

All three crossings are degenerate ($X_c=\max$), yet the order is optimal.
The minimiser escapes the cyclic tension not by balancing the crossings but
by making **one colour globally cheap** ($q_0=1$: colour 0 nearly
backward-free) and absorbing the cost into the skewed split $(1,3,5)$. The
3-cycle obstruction never binds because a colour with $q_c=1$ has nothing to
sum.

### 9.3 Refuted route B — amplifying the rank-cell count

Since $L_k=\min_\pi Q(\pi)\ge\min_\pi M(\pi)$ (occupied rank-triples,
eq. (1)), it would suffice to show $\min_\pi M(\pi)>(3/2+\varepsilon)^k$.

**This collapses.** $M(\pi)$ is one *specific* proper colouring of the
backedge graph, so $\min_\pi M(\pi)\ge\vec\chi(B_k)$; and exhaustively over
all $9!$ depth-2 orders,

$$
\min_\pi M(B_2)=3=\vec\chi(B_2).
$$

The rank-cell colouring already achieves the dichromatic optimum, so this
lower bound cannot exceed $\vec\chi\sim(3/2)^k$. (The order that *minimises*
$M$ is **not** the one that minimises $Q$: the min-$Q$ optimum fills its
rank box, $M\approx Q$, but the box is large; the min-$M$ optimum has a
small, skewed box. You cannot have both small — that conflict *is* the
problem, and no single scalar sees it.)

### 9.4 What survives, and the sharpened target

The gap $L_k>\vec\chi(B_k)$ lives entirely in $Q/M$ at the $Q$-minimiser —
the $Q$-minimising order **cannot simultaneously** minimise $M$. Both
refutations point to the same cause: every scalar summary ($q_c$ per
colour, $M$ per order) is **not closed** under the substitution-plus-
interleaving of (9.1), because the crossing term reads the *position
profile* $p\mapsto(\mathrm{suf}_c,\mathrm{pre}_c)$, not a single height.

This is the precise content of §8's "retain prefix/suffix chain profiles."
The remaining lemma, now sharply stated:

> **Profile-closure lemma (open).** Find a profile invariant
> $\Pi(\pi)$ — recording, per module and colour, the staircase
> $p\mapsto\mathrm{suf}_c(\cdot,p)$ — that (i) reproduces itself under
> (9.1) across the three interleaved modules, and (ii) forces
> $q_0q_1q_2\ge\alpha^k$ for some explicit $\alpha>3/2$.

A *single-step* multiplicative bound $L_k\ge\alpha L_{k-1}$ with
$\alpha>3/2$ would suffice (and would imply $\lambda\ge\alpha$), but §9.2–9.3
show it cannot be obtained from the scalar triple alone; the induction
hypothesis must be the profile $\Pi$.

**Status:** $\lambda>3/2$ remains **open**. This section contributes the
proved recursion (9.1), removes two dead scalar routes, and reduces the
problem to the profile-closure lemma. (The depth-$\le4$ data once read as
"$\lambda\approx2$" is reinterpreted in §11: with the exact $L_5=24$ added,
$\lambda\le1.888$ and the evidence now leans toward $\lambda=3/2$.)

## 10. First profile-closure engine

The profile-closure lemma now has an exact finite formulation, implemented in
`scripts/stilde_profile_closure.py`.

For an induced order $\sigma$ of one $B_{k-1}$ module, define the full
per-colour staircases

$$
f^\sigma_c(a)=\text{height of }Q_c\text{ on the first }a\text{ vertices of }\sigma,
\qquad
g^\sigma_c(b)=\text{height of }Q_c\text{ on the last }b\text{ vertices of }\sigma.
$$

A global order of $B_k=C_3[B_{k-1}]$ is equivalently three module orders
$\sigma_0,\sigma_1,\sigma_2$ plus a monotone lattice path

$$
n(p)=(n_0(p),n_1(p),n_2(p))\in\{0,\ldots,m\}^3,\qquad m=3^{k-1},
$$

where $n_b(p)$ counts how many vertices of $M_b$ occur before the split $p$.
Substituting this into (9.1) gives the closed profile formula

$$
q_c=\max\Big(
q_c(\sigma_{c+2}),\
\max_{n\text{ on path}}\big[
g^{\sigma_c}_c(m-n_c)+f^{\sigma_{c+1}}_c(n_{c+1})
\big]\Big).
\tag{10.1}
$$

Thus, for fixed module profiles, deciding whether $q_c\le h_c$ for all
$c$ is exactly a monotone-grid reachability problem: forbid every state $n$
where one of the three split sums exceeds its cap, and also require the
far-module heights $q_c(\sigma_{c+2})\le h_c$.

This is the desired closure object. It depends on the full staircases
$(f_c,g_c)_{c=0}^2$, not only on the terminal height triple. The test suite
now checks that (10.1) reproduces direct $q_c$ computations on all depth-1
orders and sampled depth-2 orders, and that the reachability formulation
recovers $L_1=2$ and $L_2=4$.

### 10.1 First computational facts

Using cached relation matrices and dynamic programming over positions, the
script enumerates all depth-2 profile classes:

$$
\#\{\text{distinct full staircases of }B_2\}=131{,}046
\quad\text{from }9!=362{,}880\text{ orders.}
$$

This is already too large for naive triple enumeration at the next step.
For example, at the balanced depth-3 cap $(2,2,2)$, the crude far-module
eligibility filter still leaves $60{,}784$ profiles for each module. So the
next engine pass must quotient or dominate profiles; raw state enumeration is
not a proof strategy.

The known SAT witness for $B_3$ with caps $(2,2,2)$ has module profile heights

$$
(1,2,2),\quad(1,2,2),\quad(2,2,2),
$$

and all three crossing maxima in (10.1) equal $2$. This gives the first
positive calibration profile for the closure engine: balanced caps are not
achieved by three identical local profiles, but by two colour-0-cheap modules
plus one balanced module, with the lattice path staggering their staircases.

### 10.2 Immediate next invariant target

The profile state should be compressed by **dominance**, not by terminal
height. For fixed module label $b$ and cap triple $h$, a profile $\sigma$
only contributes through:

1. the single far constraint $q_{b+1}(\sigma)\le h_{b+1}$, and
2. two one-coordinate staircases used in split sums:
   $g^\sigma_b(m-n_b)$ as a suffix source and
   $f^\sigma_{b-1}(n_b)$ as a prefix target (indices mod $3$).

So the next tractable object is the Pareto frontier of these two relevant
staircases per labelled module. If that frontier stays exponentially small
and its reachability obstruction forces product growth $>\alpha^k$, this
would become the profile-closure proof of $\lambda>3/2$. If the frontier
contains low-cap paths indefinitely, it gives the construction side of the
dichotomy.

## 11. The depth-5 frontier, the cake-number coincidence, and the corrected $\lambda$

This section supersedes the §5.1 caveat "depth 4 is the exact frontier." A new
SAT encoding reaches depth 5 exactly, which both kills a seductive numerical
coincidence and corrects the $\lambda$ reading of §5.1/§7.1.

### 11.1 Level-labeling SAT: the depth-5 frontier is reachable

The chain-enumeration encoding of `decide_stilde_layer_product.py` forbids every
reversed $(\text{cap}+1)$-chain; for $\text{cap}\ge5$ this is $\sim2\times10^7$
chains per poset, the stated reason $L_5$ was "out of reach."
`scripts/decide_layer_labeling.py` replaces it by a **level labeling**: bound
$\mathrm{height}(Q_c)\le\text{cap}_c$ with thermometer variables
$a_{c,v,t}=[\,\mathrm{lvl}_c(v)\ge t\,]$ and the implication

$$
(\text{arc }u\to v\text{ of colour }c\text{ is backward in }\pi)\ \Longrightarrow\
\mathrm{lvl}_c(u)<\mathrm{lvl}_c(v),
$$

so a backward colour-$c$ chain forces $\mathrm{lvl}_c$ to increase strictly along
it. This is $O(\#\text{colour-}c\text{ pairs}\cdot\text{cap}_c)$ clauses instead
of $O(\#(\text{cap}{+}1)\text{-chains})$. The order $\pi$ is a tournament with no
directed triangle (2 clauses per unordered triple). The encoding was
cross-checked against the chain encoding on **all 128** cap triples at depths
$2,3$ (0 mismatches) and reconfirms $L_4=15$; each depth-5 decision is $\sim6$ s.

A lazy-transitivity (CEGAR) variant, `scripts/decide_layer_lazy.py`, omits the
$O(n^3)$ triangle clauses and adds only violated directed 3-cycles on demand
(big-int bitset detection); it matches the eager solver on depth 4 and is the
route toward depth 6 (where the eager $1.3\times10^8$ triangle clauses are
infeasible).

### 11.2 $L_5=24$, exact

A rigorous scan (`scripts/run_L5_scan.py`, 185 cap triples, product $\le 27$)
gives

$$
\boxed{L_5 = 24,}
$$

certified: **every cap triple of product $\le 23$ is UNSAT**, and $(2,3,4)$
(product 24) is SAT. So the exact sequence is now

$$
L_1,\dots,L_5 = 2,\ 4,\ 8,\ 15,\ 24 .
$$

The optimal cap multisets are $\{1,3,5\}$ at depth 4 and $\{2,3,4\}$ at depth 5 —
both small-cap, both summing to 9. Feasibility is invariant under cyclic rotation
of $(q_0,q_1,q_2)$, because $\sigma(w)=w+\mathbf 1\pmod 3$ is an automorphism of
$B_k$ shifting every arc colour $c\mapsto c+1$ (verified depths $2,3$); this gives
a $3\times$ dedup of the scan.

### 11.3 The cake-number coincidence is refuted

$2,4,8,15$ are exactly the **cake numbers** $\mathrm{cake}(k)=\sum_{i=0}^3\binom
ki=(k^3+5k+6)/6$ (OEIS A000125, confirmed; the sequence has **no** known
poset/tournament interpretation). This briefly suggested a polynomial
pre-asymptotic regime. It is a **4-point coincidence**:

- A cubic is determined by 4 points, and $\mathrm{cake}$ is not even the only
  natural cubic through $2,4,8,15$: $2^k-\binom{k-1}3$ also fits and predicts
  $L_5=28$. The two cubics predict $26$ and $28$; **the exact $L_5=24$ refutes
  both.**
- $\mathrm{cake}$ is polynomial, but $L_k\ge\vec\chi(B_k)=\Theta((3/2)^k)$ is
  exponential, so $\mathrm{cake}(k)=L_k$ must fail by $k=14$
  ($\vec\chi(B_{14})=473>470=\mathrm{cake}(14)$) regardless. It in fact already
  fails at $k=5$.
- The cake value tracks the *box volume* $Q=q_0q_1q_2$, not the occupied-cell
  count $M$ (at depth 3, the $(2,2,2)$ optimum has $M=7\ne8$); and $\mathrm{cake}
  (k)$'s prime factorizations ($26=2\cdot13$) cannot be plausible small-cap
  boxes. No size-$\le3$ / rank-triple bijection exists.

### 11.4 Corrected $\lambda$, and the literature status

With $L_5=24$:

$$
L_k^{1/k}=2,2,2,1.968,1.888\ \Rightarrow\ \lambda\le 24^{1/5}=1.888,
\qquad
\frac{L_k}{L_{k-1}}=2,2,1.875,\mathbf{1.6}.
$$

The step ratio is **falling toward $3/2$**. The §5.1/§7.1 inference
"$\lambda\approx1.9$–$2$" was the rising left flank of the transient hump
$L_k/d_k$ (which, on the cake fit, peaks near $k=7$ and decays through $1$ at
$k=14$); it is **retracted**. The honest bracket is $\lambda\in[3/2,\,1.888]$,
with the trend now **leaning toward $\lambda=3/2$ (pod-tight)** — the opposite of
the depth-$\le4$ reading. Consequently the earlier $\rho\gtrsim1.24$ is withdrawn;
only the proven $\rho\ge(3/2)^{1/3}=1.1447$ stands.

This is consistent with the literature: the growth constant of
$\vec\omega(\widetilde S_n)$ (equivalently $\lambda$) is **not known** anywhere.
The 2023 paper (arXiv:2310.04265) explicitly flags "the lower bound
$\vec\omega(\widetilde S_n)\ge n$ could be far from tight" and leaves polynomial
$\vec\chi$-boundedness open; the pod paper (arXiv:2606.07748) supplies only the
one-sided $\vec\omega(B_k)\ge(3/2)^{k/3}$. The $L_k/\lambda$ analysis is
project-internal.

### 11.5 Construction bounds (what is provable now)

- **Lexicographic order gives exactly $(1,1,2^k)$**, so $L_k\le 2^k$: every
  backward arc forces $x_j=2,y_j=0$ at the first difference (colour 2 only), so
  all backward arcs pile into one colour. Exhaustively, *every* generalized-lex /
  coordinate-wise word-key order has product $\ge 2^k$ — the sub-$2^k$ regime is
  unreachable by any monotone key.
- The $L_4=15$ optimum uses **three genuinely independent modules** with distinct
  height profiles $(1,3,3),(1,2,5),(1,3,5)$ — not rotations or colour-permutations
  of one another. So no fixed recursive template (which derives the three modules
  from one previous order by symmetry) can reach $15$; beating $2^k$ provably needs
  the interleaving that the scalar triple cannot capture (§9.4). This is the
  constructive face of the profile-closure obstruction.
- Block substitution $B_{a+b}=B_a[B_b]$ multiplies heights coordinatewise; from
  the depth-4 optimum, $B_8=B_4[B_4]$ has heights $(1,9,25)$, product $225=15^2$,
  certifying $\lambda\le 15^{1/4}=1.968$ (now improved to $1.888$ by $L_5$).

### 11.6 Status and next steps

- **Done:** depth-5 frontier cracked (level-labeling SAT); $L_5=24$ exact; cake
  and the rival cubic refuted; $\lambda\le1.888$; the "$\lambda\approx2$" reading
  corrected to lean toward $\lambda=3/2$.
- **Next data point $L_6$ — attempted, currently out of reach.** Depth 6 has
  $729$ vertices: the eager labeling needs $1.3\times10^8$ no-3-cycle clauses
  (infeasible), and the lazy CEGAR **does not converge** — five cap triples
  (products $24$–$40$) each ran $290$–$2120$ refinement rounds and timed out at
  $>1200$ s without resolving SAT or UNSAT. So only the submultiplicative bracket
  $L_6\in[\vec\chi(B_6),\,L_5L_1]=[18,48]$ is known. A step ratio $L_6/L_5\approx
  1.5$ would be strong evidence for pod-tightness $\lambda=3/2$; reaching $L_6$
  needs a better order encoding — symmetry-breaking on the $\sigma$-orbits (the
  cyclic automorphism quotients the search $3\times$ and a within-block fix more),
  or a positional/$O(n\log n)$ order encoding instead of pairwise transitivity.
- **Theory unchanged:** $\lambda>3/2$ vs $\lambda=3/2$ is genuinely open; the
  profile-closure lemma (§9.4/§10.2) remains the structural target, now with the
  prior toward $\lambda=3/2$ rather than away from it.

### 11.7 First depth-6 encoding improvement: binary-key order variables

The positional encoding option is now concrete:
`scripts/decide_layer_positional.py` keeps the level-labeling height constraints
but replaces pairwise transitivity by binary keys. Each vertex $v$ receives a
key $r_v$, and the induced order is

$$
u\prec v \quad\Longleftrightarrow\quad (r_u,u)<(r_v,v).
$$

The vertex-id tie-break is important: every satisfying assignment is a genuine
total order, while every total order is still representable by assigning
distinct increasing keys. So this is equisatisfiable with the original total
order encoding and needs comparator clauses rather than directed-triangle
clauses.

Verification:

- It matches the eager labeling encoding on all cap triples
  $\{1,2,3\}^3$ at depths $2,3$.
- It matches the depth-4 frontier checks: $(1,3,5)$ SAT and $(2,2,3)$ UNSAT.
- The combined stilde/SAT test suite has 20 passing tests after adding the
  positional cross-checks.

For the representative depth-6 candidate $(3,3,4)$ the new CNF builds in
foreground time:

$$
n=729,\quad \lceil\log_2 n\rceil=10,\quad
265{,}356\text{ pair comparators},\quad
2{,}665{,}954\text{ vars},\quad
16{,}278{,}085\text{ clauses}.
$$

This removes the explicit $1.3\times10^8$-clause blocker. It does **not** yet
compute $L_6$: a first bounded solve of $(3,3,4)$ still failed to return within
one minute on this machine. The next computational target is therefore sharper:
add symmetry/domain constraints and solver tuning on top of the binary-key
encoding, rather than continuing lazy transitivity CEGAR.

### 11.8 Symmetry breaking is (almost) unavailable: $\mathrm{Aut}(B_k)=C_3$

The natural hope — break the order's automorphism symmetry to shrink the depth-6
search — **mostly fails**, for a structural reason worth recording.

**$\mathrm{Aut}(B_k)=C_3$, generated by $\sigma(w)=w+\mathbf 1\pmod 3$.** Computed
exhaustively for $B_2$: the full direction-preserving automorphism group has order
$3$ (only $\{\mathrm{id},\sigma,\sigma^2\}$), and they induce exactly the cyclic
colour permutations $\{\mathrm{id},(012),(021)\}$; the **colour-preserving**
subgroup is **trivial**. The wreath-product intuition $\mathrm{Aut}(H)\wr C_3$
fails because applying a colour-shifting sub-automorphism to a single module makes
the induced colour map inconsistent across modules, so it is not an automorphism
of the coloured tournament.

**Consequence for SAT symmetry breaking.** An automorphism $\varphi$ maps a
solution for caps $h$ to one for caps $\psi^{-1}(h)$, where $\psi\in C_3$ is the
induced colour rotation. So $\varphi$ is a symmetry of the cap-$h$ *instance* iff
$\psi(h)=h$:

- skewed caps (the optima $(1,3,5),(2,3,4)$, and every non-diagonal triple) are
  fixed only by $\psi=\mathrm{id}$, i.e. the **trivial** group — *no* within-instance
  symmetry to break;
- only the diagonal $(h,h,h)$ admits $\sigma$ (a factor $3$), and those are not the
  optima.

So the only usable symmetry is the **scan-level cyclic dedup** of cap triples
(test one representative of each $\{(a,b,c),(b,c,a),(c,a,b)\}$ class), giving $3\times$
fewer solves but no speed-up per instance. The real levers for $L_6$ are therefore
parallelism, conflict budgets, and the cyclic dedup — not symmetry constraints.

**Calibration (depth 6, positional encoding).** Even the trivial lexicographic
order $(1,1,2^6)$ solves in $\approx25$ s (almost all CNF *build*: $16$M clauses),
and the easy $(5,5,5)$ in $\approx78$ s; skewed near-optimal triples need
$\gg 8\times10^6$ conflicts ($(2,4,4)$ ran $43$ min without resolving). So exact
$L_6$ (all-below-UNSAT certified) is out of practical reach; a parallel scan over
$\sigma$-cyclic-rep triples can only **bracket** $L_6$ (small products that resolve
UNSAT give a lower bound; larger products that resolve SAT give an upper bound;
the hard middle stays UNKNOWN). `scripts/run_L6_parallel.py`.

### 11.9 Rank-domain constraints on the binary-key encoding

The first non-group domain constraints have been added to
`scripts/decide_layer_positional.py`:

- `--range-keys` constrains every binary key to lie in $\{0,\ldots,n-1\}$.
- `--distinct-keys` additionally forces all keys to be distinct, so the key
  assignment is literally a permutation of ranks $0,\ldots,n-1$ when combined
  with `--range-keys`.

Both constraints are sound: every total order can be represented by assigning
its vertices the distinct ranks $0,\ldots,n-1$. They only remove redundant key
assignments (ties and unused gaps), not orders.

Cross-checks: with both options enabled, the positional encoding matches the
eager labeling decisions on selected SAT/UNSAT cap triples at depths $2,3$; the
encoding test file passes.

For the depth-6 representative $(3,3,4)$:

| mode | vars | clauses | comment |
|---|---:|---:|---|
| binary key | 2,665,954 | 16,278,085 | §11.7 baseline |
| `--range-keys` | 2,665,954 | 16,281,001 | essentially free |
| `--range-keys --distinct-keys` | 6,204,034 | 37,067,221 | permutation-rank model |

On the known depth-5 SAT boundary $(2,3,4)$, the permutation-rank mode builds
comfortably (552,259 vars / 3,274,750 clauses) but did not finish within a
90-second foreground run, so it is not an immediate speed-up. It remains a sound
solver variant for longer runs; the next SAT-side improvement should combine
these rank-domain constraints with solver selection, assumptions, or additional
problem-specific domain constraints.

### 11.10 Final depth-6 SAT verdict: $L_6$ is beyond practical SAT

A parallel scan over all $104$ $\sigma$-cyclic-rep cap triples of product $\in
[28,48]$ (`scripts/run_L6_walltime.py`, 14 workers, **wall-clock** 5-min timeout
per solve via `os.killpg` — a conflict budget does *not* bound wall-clock here:
3M conflicts $\approx 2$ h on a hard depth-6 instance) gives:

$$
\text{SAT } 0,\qquad \text{UNSAT } 21,\qquad \text{TIMEOUT } 83.
$$

- **No bracket improvement.** No triple resolved SAT (so no upper bound below the
  submultiplicative $L_6\le L_5L_1=48$), and *every balanced triple* (all caps
  $\ge2$) timed out at 5 min. Longer runs confirm the scale: balanced solves take
  $30$–$120$ min each, often still UNKNOWN (e.g. $(2,2,7)$ ran $123$ min $\to$
  UNKNOWN). So SAT cannot practically bracket $L_6$; **$L_6\in[18,48]$ stands.**
- The $21$ UNSATs are exactly the *degenerate* reps $(1,1,X)$, one per product
  $X=28,\dots,48$, each resolving in $2$–$4.5$ min.

**Clean byproduct (independent of $L_6$).** $(1,1,X)$ is UNSAT for *every*
$X\le 48$, while the lexicographic order realises $(1,1,2^6)=(1,1,64)$. This is
explained by a structural lemma:

> **Two-free-colours lemma.** If two of the three colours are backward-free
> ($q_a=q_b=1$), the third layer is forced to its maximum:
> $q_c=2^k$.

Proof. By cyclic symmetry assume the free colours are $0$ and $1$, so the missing
colour is $2$. Since $q_0=q_1=1$, the order $\pi$ has no backward $P_0$ or $P_1$
arc, hence is a linear extension of both $P_0$ and $P_1$.

Take two words $x,y\in\{0,1,2\}^k$, and let $j$ be their first differing
coordinate. If $(x_j,y_j)=(0,1)$ then $x<_{P_0}y$, so $x\prec y$; if
$(x_j,y_j)=(1,2)$ then $x<_{P_1}y$, so $x\prec y$. If $(x_j,y_j)=(0,2)$, choose
a word $z$ agreeing with $x,y$ before $j$, having $z_j=1$, and arbitrary suffix
(for instance the suffix of $y$). Then $x<_{P_0}z<_{P_1}y$, so again
$x\prec y$. Therefore $\pi$ refines the ordinary lexicographic order with digit
order $0<1<2$.

Now restrict to the $2^k$ words in $\{0,2\}^k$. In the colour-$2$ poset, these
form a chain under lexicographic order with digit order $2<0$, because every
first difference is $2\to0$. But $\pi$ orders the same set with digit order
$0<2$, the reverse chain order. Hence all consecutive colour-$2$ chain relations
are backward in $\pi$, so $q_2\ge2^k$. The reverse inequality is the usual
maximum-transitive-set bound for $B_k$ (or directly, a colour-$2$ chain chooses
only the two symbols $2,0$ at each coordinate), so $q_2=2^k$.

Thus the $(1,1,\cdot)$ face of the cap region bottoms out exactly at $2^k$. This
strengthens §11.5 from the *generalized-lex family* to *all* orders with two
empty colours.

**Bottom line on $L_6$.** Eager labeling (won't build), lazy CEGAR (doesn't
converge), positional SAT (builds but balanced solves take hours), key-domain
constraints (§11.9, no speed-up), automorphism symmetry (trivial, §11.8), and the
profile DP (generation doesn't compress, §12) have all been tried. $L_6$ is
genuinely beyond current methods; $[18,48]$ is the honest bracket, and the
$\lambda$ conclusion is unaffected ($\lambda\in[3/2,1.888]$, leaning pod-tight).

## 12. The profile-closure DP: decision compresses, generation does not

This section reports the outcome of building the §10.2 Pareto-compressed profile
DP. The result is a clean dichotomy that also **unifies the computational and
theoretical obstructions**: the *decision* layer compresses beautifully, but the
*generation* layer does not compress at all — and the reason is exactly the
profile non-closure of §9.4.

### 12.1 The decision layer compresses to a tiny frontier (works)

For a labelled module $b$ under target caps, only the projection
$(g_b,\,f_{b-1},\,q_{b+1})$ matters (the colour-$b$ suffix staircase, the
colour-$(b-1)$ prefix staircase, the colour-$(b+1)$ far height; §10.2). Dominance:
profile $A$ beats $B$ if $g_b^A\le g_b^B$ and $f_{b-1}^A\le f_{b-1}^B$ pointwise
and $q_{b+1}^A\le q_{b+1}^B$. Then $A$ makes every cap triple $B$ makes, so $B$ is
droppable. Measured on all $9!$ orders of $B_2$:

$$
131{,}046\text{ full profiles}\ \xrightarrow{\text{per-label Pareto}}\ \boxed{16}
\quad(\text{uniform }16/16/16\text{ by the cyclic }\sigma).
$$

With the compressed sets the profile-closure decision becomes $16^3=4096$ module
triples (vs the naive $131{,}046^3$), and it **reproduces $L_3=8$ instantly,
without SAT** (`scripts/stilde_profile_dp.py`; first SAT cap $(1,1,8)$). So the
decision side of §10.2 is correct, sound, and tractable.

### 12.2 The generation layer does not compress (the wall)

To reach $L_4$ one must *generate* the achievable $B_3$ profiles from $B_2$ ones.
A grid path-DP (`combine_dp`) was validated against brute force on $B_1\to B_2$
(0 mismatches / 20 triples). But its intermediate frontier is already the
**full interleaving count**. Measured on a single $B_2\to B_3$ triple, the number
of distinct partial rank-sequence states per grid layer is

$$
1,\,2,\,6,\,12,\,30,\,90,\,210,\,560,\,1680,\,4200,\,11{,}550,\dots
$$

and $1680=\binom{9}{3,3,3}$ is *exactly* the number of monotone paths to the
centre cell $(3,3,3)$. Even this coarse rank-sequence signature gives one state
per interleaving — **zero compression**.

**Why no sound mid-construction pruning exists.** At a fixed grid cell the placed
vertex *set* is path-independent, but the *order* (hence the prefix staircases
$f_c(a)=\max_{v\in\text{first }a}r_c(v)$) is not. Two partials with identical rank
vectors still have different prefix orders, so they realise different prefix
staircases — and the decision layer consumes the staircases, not just the heights.
Rank-vector dominance is therefore sound only for the terminal *height triple*,
not for the *profile*; and the suffix staircase of the final order is undetermined
until construction ends. There is no sound dominance on partial states, so the DP
cannot prune below the exponential path count.

### 12.3 One wall, two faces

The non-compressibility of generation is the **same** phenomenon as §9.4: the
prefix/suffix profile is not closed under substitution-plus-interleaving, because
the crossing split couples to the full interleaving (§9.1). Concretely, building a
parent's suffix staircase $g_b$ needs a child's colour-$b$ data over an interior
interval, which the compressed (or even full 6-staircase) child state does not
carry. So:

> The reason $\lambda>3/2$ resists a closed-invariant proof is the *same* reason
> $L_6$ resists a compressed-profile computation. The profile DP re-expresses the
> exponential interleaving search in the recursive language — which is the right
> language for *reasoning* and for the *decision* step, but it does not shrink the
> search that produces the profiles.

### 12.4 Consequence for $L_6$ and next steps

- The profile DP is **not** a cheaper route to $L_6$: generation reproduces the
  exponential search SAT already performs, without a mature solver's pruning. So
  the positional-SAT encoding (§11.7), heavy as it is, remains the only exact
  route to $L_6$; the profile DP is best kept as the decision/reasoning tool it
  excels at (the $16$-frontier makes profile-closure feasibility checks instant).
- The genuine openings are unchanged and now sharper: either (i) a *new* closed
  invariant that survives interleaving — necessarily richer than prefix/suffix
  staircases, since those provably do not close — or (ii) accept the order
  dependence and push SAT with symmetry/domain constraints (§11.7). The $16$-frontier
  is a hint that the *right* invariant, if it exists, is low-dimensional on the
  decision side; the open problem is making it closed on the generation side.

## 13. A closed repair exists: interval profiles, but it is too large

The precise reason prefix/suffix profiles fail is that a parent suffix/prefix
recursion can ask a child for a **contiguous interior interval**, not only an
initial or terminal segment. The direct closure repair is therefore:

$$
I_c^\pi(i,j)=\operatorname{height} Q_c(\pi[i,j)),
\qquad 0\le i\le j\le |B_k|.
$$

This interval matrix strictly contains the old prefix/suffix staircases:
$f_c(j)=I_c(0,j)$ and $g_c(j)=I_c(n-j,n)$.

For a fixed interleaving of three child orders, it is exactly closed. Let
$n_b(p)$ be the number of $M_b$ vertices before parent position $p$. Then for
any parent interval $[p,q)$,

$$
\boxed{
I_c^{\mathrm{parent}}(p,q)=
\max\left(
I_c^{M_{c+2}}\!\big(n_{c+2}(p),n_{c+2}(q)\big),\
\max_{p\le r\le q}
\left[
I_c^{M_c}\!\big(n_c(r),n_c(q)\big)
+I_c^{M_{c+1}}\!\big(n_{c+1}(p),n_{c+1}(r)\big)
\right]
\right).
}
\tag{13.1}
$$

This is just the crossing recursion (9.1) applied inside an arbitrary parent
interval. It is implemented and checked in `scripts/stilde_interval_profiles.py`:

- interval profiles recover the prefix/suffix staircases exactly;
- (13.1) matches direct interval-profile computation exhaustively at depth 1 and
  on sampled depth-2 orders.

So we did find an interleaving-closed invariant richer than prefix/suffix
staircases.

**But it is not the hoped-for invariant.** It is essentially order-level data.
On random $B_2$ orders:

| sample size | distinct interval profiles |
|---:|---:|
| 5,000 | 4,871 |
| 20,000 | 18,212 |

That is almost no compression. The interval profile repairs closure by carrying
exactly the missing interior information, but the price is a two-parameter matrix
per colour. It is useful as a diagnostic and a correctness target; it is not a
low-dimensional route to $L_6$ or to the $\lambda$ dichotomy.

**Revised target.** Any successful invariant must be a quotient of the interval
profile: rich enough to evaluate the interval split formula (13.1), but coarse
enough to identify many interleavings that have distinct interval matrices. The
$16$-frontier on the decision side says such a quotient might exist after caps
are fixed; the interval-profile experiment says the uncapped exact closure is
too fine.

## 14. Cap-truncated intervals and the isolation obstruction

The next natural quotient is cap-truncation. For a fixed target cap triple $h$,
record only

$$
J_c(i,j)=\min\{I_c(i,j),h_c+1\}.
$$

This is the exact information needed to know whether interval $[i,j)$ is over
cap in colour $c$. It is also closed under (13.1): once a child interval value is
$h_c+1$, it is absorbing for the colour-$c$ max/sum computation. This quotient is
implemented in `scripts/stilde_interval_quotients.py` and checked against the
full interval closure at depths $1,2$.

Empirically, however, it still does not compress. Random $B_2$ orders:

| caps | samples | distinct cap-truncated interval profiles |
|---|---:|---:|
| $(1,1,1)$ | 20,000 | 16,414 |
| $(1,1,2)$ | 20,000 | 17,108 |
| $(1,2,2)$ | 20,000 | 17,720 |
| $(2,2,2)$ | 20,000 | 18,212 |
| $(2,3,4)$ | 20,000 | 18,212 |
| $(3,3,4)$ | 20,000 | 18,212 |

So even height-$1/2$ interval information already distinguishes nearly every
random order.

There is also a structural reason no **exact** quotient of interval profiles can
work.

> **Interval isolation lemma.** Fix caps $h$. If two child orders have different
> cap-truncated interval profiles, then there is a one-level parent context whose
> cap-truncated interval profile distinguishes them. Hence the cap-truncated
> interval profile is already the semantic quotient for exact interval-profile
> generation.

Proof sketch. Suppose the two child profiles differ in colour $c$ on interval
$[i,j)$. Place that child as the far module $M_{c+2}$ in a parent. Interleave the
parent so the relevant child block is contiguous and the other two modules lie
outside the parent interval being queried. For that parent interval $[p,q)$, the
crossing term in (13.1) is zero and

$$
J_c^{\mathrm{parent}}(p,q)=J_c^{M_{c+2}}(i,j).
$$

Thus the parent directly reads the child interval entry. No smaller exact
closed quotient can identify the two children.

This closes the "exact quotient of interval profiles" route. Any useful invariant
must weaken the objective: it cannot generate exact parent interval profiles.
It must instead preserve only the inequalities needed for the final cap decision
or prove a lower-bound obstruction without attempting exact profile generation.

One representation remains useful: the minimal intervals with $J_c(i,j)\ge t$
form an antichain under containment (the "bad-span" antichain). It is sparse
on $B_2$ samples (roughly $31$--$40$ spans total over all colours/thresholds),
but it is equivalent to $J$ rather than a quotient. It may be a better data
structure for future experiments, not a theoretical compression by itself.

### 14.1 Dominance (lossy) compression also fails — the closed object is high-dimensional

The isolation lemma closes *exact* quotients. But $L_k=\min_\pi Q$ is a
*minimisation*, and the interval closure (13.1) is built only from
$\max,\min,+$ — hence **monotone**: if child $A\le B$ pointwise then
$\mathrm{closure}(A,\cdot)\le\mathrm{closure}(B,\cdot)$. So Pareto-minimal parents
arise only from Pareto-minimal children, and for the min objective it would
suffice to carry the **Pareto-minimal** interval profiles (lowest interval
heights) — a *lossy* compression the isolation lemma does **not** forbid (it
preserves distinctness, not dominance).

This is the last escape hatch, and it also fails: the Pareto-minimal frontier is
large. On random $B_2$ orders (lower interval heights = better):

| object | sample | distinct | **Pareto-minimal** |
|---|---:|---:|---:|
| full interval profile $I$ | 500 | 498 | 322 |
| full interval profile $I$ | 1500 | 1489 | 614 |
| full interval profile $I$ | 3000 | 2939 | **973** |
| cap-trunc $J$, caps $(1,1,1)$ | 3000 | 2873 | 613 |
| cap-trunc $J$, caps $(2,2,2)$ | 3000 | 2950 | 869 |
| cap-trunc $J$, caps $(2,3,4)$ | 3000 | 2953 | 857 |

The Pareto-minimal count grows with the sample (no saturation toward a small
constant) and stays a large fraction even under the most aggressive clipping
$(1,1,1)$ (values in $\{0,1,2\}$). So dominance compression of the *closed* object
is as infeasible as exact compression: combining a frontier of $\sim10^3$ children
needs $\sim10^9$ triples.

**The dichotomy, sharpened.** There is a genuine tension:

- the only *closed* object (interval profile, or its cap-truncation $J$) is
  intrinsically high-dimensional — the bad-span antichain has $\sim35$ degrees of
  freedom, and a $\sim35$-dim Pareto frontier is large (hundreds–thousands);
- the only *small-frontier* object (the $16$ per-label projection $(g_b,f_{b-1},
  q_{b+1})$, §12.1) is **not** closed — by the isolation lemma, generating it needs
  the full interval profile.

No object is **both** closed and small-frontier, exactly, *or* up to dominance. So
the recursive-DP route to $L_6$ / to the $\lambda$ dichotomy is closed in every
form we can formulate: exact quotient (isolation lemma), and lossy Pareto quotient
(this measurement). What survives is only what §14 already flagged — *abandon
exact generation*: either a one-sided inequality DP that bounds (not computes)
$L_k$, or a direct analytic obstruction for $\lambda>3/2$ vs $\lambda=3/2$ that
does not route through profile generation at all. The computational mapping of the
problem is complete; the dichotomy is now a purely analytic question.

## 15. A cleaner reduction of pod-tightness: the $q_0=1$ face

Every computational/compression route to $L_k$ is closed (§12, §14, §14.1). This
section opens a different attack on the *upper* side — pod-tightness $\lambda=3/2$
— via a restricted but much cleaner sub-problem.

**Definition.** The $q_0=1$ **face** restricts to orders with colour $0$
backward-free (i.e. $\pi$ a linear extension of $P_0$), and minimises the product
of the other two layers:
$$
F_k \;=\; \min\{\,q_1(\pi)\,q_2(\pi)\;:\;q_0(\pi)=1\,\}.
$$

**Why it is a valid reduction.** $L_k\le F_k$ (the face is a sub-family, and on it
$Q=1\cdot q_1q_2$). And $F$ is **submultiplicative**: $B_{a+b}=B_a[B_b]$ with both
factors on the face stays on the face ($q_0\le q_0\cdot q_0=1$), and heights
multiply coordinatewise, so $F_{a+b}\le F_aF_b$ (checked: $F_4=15\le F_2^2=16$,
$F_5=25\le F_1F_4=30$). Hence $\lambda_F:=\lim F_k^{1/k}$ exists, and since
$(3/2)^k\le L_k\le F_k$,
$$
\boxed{\;\lambda_F=3/2\ \Longrightarrow\ \lambda=3/2\ \text{(pod-tight)}.\;}
$$

**Exact data** (SAT with $\mathrm{cap}_0=1$; `scripts/stilde_q0_face.py`):
$$
F_1,\dots,F_5 \;=\; 2,\,4,\,8,\,15,\,25
\qquad(\text{vs }L_k=2,4,8,15,24).
$$
$F_k=L_k$ for $k\le4$ — the global optimum lies on the face through depth 4 — and
$F_5=25$ (optimum $(1,5,5)$) just above $L_5=24$ (the off-face $(2,3,4)$). The
$k\le3$ optima are *two-free* $(1,1,2^k)$; at $k=4$ the optimum switches to the
balanced $(1,3,5)$ with $M_2$ **split**.

**The data is consistent with pod-tightness but does not pin it** (⚠ this
paragraph's optimistic reading is corrected in §16: $F_k/2^k$ extrapolates instead
to $\lambda_F\approx1.66$, so $\lambda_F\in[3/2,1.904]$ is undetermined). Both
$(3/2)$-normalised ratios grow only *polynomially*:

| $k$ | $F_k$ | $F_k/(3/2)^k$ | $F_k/\vec\chi(B_k)$ |
|---|---:|---:|---:|
| 1 | 2 | 1.33 | 1.00 |
| 2 | 4 | 1.78 | 1.33 |
| 3 | 8 | 2.37 | 1.60 |
| 4 | 15 | 2.96 | 1.875 |
| 5 | 25 | 3.29 | 2.08 |

The ratio-of-ratios of $F_k/(3/2)^k$ is $1.33,1.33,1.25,1.11\to1$ (decelerating),
and $F_k/\vec\chi$ grows roughly linearly — both the signature of $F_k=\mathrm{poly}
\cdot(3/2)^k$, i.e. $\lambda_F=3/2$. (Caveat: 5 points; the cake episode (§11.3) is
the standing reminder not to over-read a short prefix.)

**Why the face is cleaner — and where it still stalls.** On the face $M_0$ is
entirely before $M_1$, so only $M_2$ floats: a *one*-dimensional interleaving, a
genuine 2-objective $(q_1,q_2)$ problem. Its relevant invariant
$(\mathrm{pre}_1,\mathrm{suf}_1,\mathrm{pre}_2,\mathrm{suf}_2)$ has a **small**
Pareto frontier at $B_2$ — only $53$ (exhaustive), with just $6$ height-pairs
$(1,4),(2,2),(2,3),(3,2),(3,3),(4,1)$ — versus the $\sim10^3$+ of the full
interval profile. But it **blows up at $B_3$** ($\ge1528$ on $4000$ samples, all
distinct): the staircase dimension returns, so a face-DP cannot compute $F_6{+}$.

**The construction structure (the open piece).** The depth-4 optimum decomposes as
$M_0=(1,3,3)$, $M_1=(1,2,5)$, $M_2=(1,3,5)$, giving parent
$(1,\,q_1(M_0),\,q_2(M_1))=(1,3,5)$ — i.e. $M_0$ is *cheap on $q_2$*, $M_1$ *cheap
on $q_1$*, and $M_2$ is a *self-similar copy* of the parent, split to keep both
crossings under the far terms. So pod-tightness now reduces to a concrete
**2-objective construction**:

> Build a family of $q_0=1$ orders of $B_k$ with $q_1q_2=(3/2)^{k+o(k)}$, via
> complementary-shape $M_0,M_1$ and a self-similarly split $M_2$.

This is strictly sharper than the original $\lambda$ dichotomy: one fewer
objective, a fixed inter-module order ($M_0<M_1$), and a single floating module.
It is the most attackable open form of pod-tightness the project has reached.

## 16. Attempting the explicit construction (and the corrected status)

We attempted to turn the §15 structure into a recursive construction proving
$\lambda_F=3/2$. The structure is real and clean; the construction is not closed by
any template we found, and forcing the issue corrects the §15 over-read.

**Decoded structure (exact, $F_4$ and $F_5$).** The face optimum $(1,A,B)$ has
$$
M_0=(1,A,b_0)\ (\text{cheap }q_2),\quad
M_1=(1,a_1,B)\ (\text{cheap }q_1),\quad
M_2=(1,A,B)\ (\text{self-similar}),
$$
with parent height $=(1,\,q_1(M_0),\,q_2(M_1))$, and $a_1=A-1$, $b_0=B-2$ in both
cases. $M_2$ is split so its colour-1 mass sits late and colour-2 mass early.
($F_4$: $M_0(1,3,3),M_1(1,2,5),M_2(1,3,5)$; $F_5$: $M_0(1,5,3),M_1(1,4,5),M_2(1,5,5)$.)

**The $M_2$ schedule is a clean 2-cut — the obstruction is the modules, not the
interleaving (corrected).** An initial templated run of
`scripts/stilde_face_construction.py` returned $16$ at depth 4, and we wrongly
concluded a fine multi-chunk interleaving was required. It is not. Feeding the
*exact* optimal modules $M_0(1,3,3),M_1(1,2,5),M_2(1,3,5)$ and sweeping the simple
**2-cut** schedule $[\,M_2[{:}s]\,][\,M_0\,][\,M_1\,][\,M_2[s{:}]\,]$ over all $s$,
the minimum is $\mathbf{15=F_4}$, attained at $s=8\approx m/3$. The earlier $16$
came from two avoidable causes: the coarse split set $\{0,m/4,m/2,3m/4,m\}$ *skips*
$s\approx m/3$, and the bounded Pareto frontier had dropped the needed
complementary modules. So the scheduling is solved (a 2-cut suffices); the real
wall is **generating the right module shapes** — the $(1,A,b_0),(1,a_1,B),(1,A,B)$
family with the right staircases, i.e. the same frontier blow-up as §15.

**Correction: $q_0=1$ itself is not the delicate part.** An earlier diagnostic
claimed random $M_2$ interleavings give $q_0=2$; that was a bug (a path built for
the wrong module size $m$). Under the exact face hypotheses — each child $q_0=1$
and every $M_0$ vertex before every $M_1$ vertex — §17 proves *every* $M_2$
interleaving keeps parent $q_0=1$ (re-verified: $q_0=1$ on all of $8000$ random
$M_2$ schedules at $m=27$). The face constraint is free; only the objective bites.

**Corrected status of $\lambda_F$.** The §15 "leans pod-tight" was an over-read.
From the exact $F_k=2,4,8,15,25$:

| extrapolation | reads | implies |
|---|---|---|
| $F_k/(3/2)^k$ ratio-of-ratios $\to1$ | poly$\cdot(3/2)^k$ | $\lambda_F=3/2$ |
| $F_k/2^k = 1,1,1,.94,.78$ ($\times.83$) | $(2\cdot.83)^k$ | $\lambda_F\approx1.66$ |

Both fit 5 points. So **$\lambda_F\in[3/2,\,1.904]$ is genuinely undetermined** —
the data is consistent with pod-tightness but does not establish it, and an equally
natural reading gives $\lambda_F\approx1.66>3/2$. (The cake episode, §11.3, is the
standing warning against the optimistic extrapolation.)

**Net (corrected).** The face has a fully decoded optimal structure, a *free*
$q_0=1$ constraint (§17), and a *simple* $M_2$ schedule (a 2-cut). The construction
still does not close, but the surviving obstruction is now sharply localised: it is
**module-shape generation** — producing the complementary family
$(1,A,b_0),(1,a_1,B),(1,A,B)$ with the staircases the 2-cut crossings read — which
is the §15 frontier blow-up, not the interleaving. So the open construction is a
**2-objective shape recursion** (clean 2-cut combination of small/self-similar
shapes); whether that family closes with product $(3/2)^{k+o(k)}$ is the remaining
question. Pod-tightness $\lambda=3/2$ stays open, and the data ($\lambda_F\in[3/2,
1.904]$) does not settle it either way.

## 17. The exact language of the $q_0=1$ face

The construction failure left one false impression: that face membership itself
requires a special fine interleaving. It does not. The $q_0=1$ language has an
exact elementary recursion.

Let a parent order $\pi$ of $B_k=C_3[B_{k-1}]$ have induced child orders
$\pi_0,\pi_1,\pi_2$ in the top modules $M_0,M_1,M_2$, and let
$n(t)=(n_0(t),n_1(t),n_2(t))$ be its top lattice path, with
$m=3^{k-1}$.

**Face-language theorem.**
$$
q_0(\pi)=1
\quad\Longleftrightarrow\quad
q_0(\pi_b)=1\ (b=0,1,2)
\ \text{and}\ 
n_1(t)>0\Rightarrow n_0(t)=m\ \text{for every }t.
$$
Equivalently: each child is on the face, and the top path places every $M_0$
vertex before every $M_1$ vertex. The module $M_2$ may float arbitrarily around
and between them.

**Proof.** Necessity is immediate inside each induced child. At the top level,
the only colour-0 comparabilities between distinct modules are the complete
relation $M_0<_{P_0}M_1$. If any $M_1$ vertex precedes an $M_0$ vertex in $\pi$,
that top colour-0 arc is backward and $q_0(\pi)\ge2$.

Conversely, assume the three child orders have $q_0=1$ and all $M_0$ vertices
precede all $M_1$ vertices. A colour-0 comparable pair is either inside one
module, where it is ordered forward by the child hypothesis, or it is a top-level
pair from $M_0$ to $M_1$, where it is ordered forward by the path hypothesis.
Pairs involving $M_2$ have top colour $1$ or $2$ unless they are inside $M_2$.
Thus no colour-0 arc is backward, so $q_0(\pi)=1$. $\square$

This was tested exhaustively on all $9!$ depth-2 orders and constructively on all
$84$ depth-2 valid face paths for every triple of face children
(`scripts/stilde_face_language.py`, `tests/test_stilde_face_language.py`).

**Consequence.** The face problem is cleaner than §16 made it look. The top path
is a two-stage one-dimensional interleaving:
first interleave $M_2$ with $M_0$, then interleave the remaining $M_2$ with
$M_1$. For such a path, the only active objective constraints are
$$
q_1(\pi)=
\max\!\left(q_1(M_0),\ \max_t[
\mathrm{suf}_1^{M_1}(m-n_1(t))+\mathrm{pre}_1^{M_2}(n_2(t))]\right),
$$
$$
q_2(\pi)=
\max\!\left(q_2(M_1),\ \max_t[
\mathrm{suf}_2^{M_2}(m-n_2(t))+\mathrm{pre}_2^{M_0}(n_0(t))]\right).
$$
So the remaining open construction is not "keep $q_0=1$"; that part is closed.
It is the sharper two-objective scheduling problem of floating $M_2$ so that the
two displayed maxima are simultaneously small enough to beat $2^k$.

## 18. The clean 2-cut reduction: exact formulas, 2-staircase state, exponential frontier

This is the cleanest form the construction (§16) has reached. With $q_0=1$ free
(§17) and the $M_2$ schedule a clean 2-cut $M_2[{:}s]\,|\,M_0\,|\,M_1\,|\,M_2[s{:}]$,
the parent layer heights reduce to **exact formulas** (validated: 0 mismatches vs
`closure_heights` over all $s$; `scripts/stilde_face_2cut.py`,
`tests/test_stilde_face_2cut.py`):

$$
Q_1=\max\!\big(q_1(M_0),\,q_1(M_2),\,q_1(M_1)+\mathrm{pre}_1(M_2,s)\big),\qquad
Q_2=\max\!\big(q_2(M_1),\,q_2(M_2),\,q_2(M_0)+\mathrm{suf}_2(M_2,m{-}s)\big).
$$

**The state collapses.** $M_0$ and $M_1$ enter *only as scalars* $q_1,q_2$; **only
$M_2$ carries staircases, and only two of them** — $\mathrm{pre}_1$ (its colour-1
prefix) and $\mathrm{suf}_2$ (its colour-2 suffix). So the per-module state needed
for the recursion is $(q_1,q_2,\mathrm{pre}_1,\mathrm{suf}_2)$, a 2-staircase
object — versus the 6-staircase / 4-staircase profiles of the general problem.
The $s$-sweep is a clean 1-parameter tradeoff: increasing $s$ raises
$\mathrm{pre}_1(M_2,s)$ and lowers $\mathrm{suf}_2(M_2,m{-}s)$, so a good $M_2$ is
one whose colour-1 mass is late and colour-2 mass early.

**It reproduces $F_4=15$ but the frontier is exponential.** Running the reduced
representative recursion (Pareto-prune by $(\mathrm{pre}_1,\mathrm{suf}_2)$, with
the bounded representative selection used in `stilde_face_2cut.py`):

| depth | $F_k$ | $(\mathrm{pre}_1,\mathrm{suf}_2)$ frontier |
|---|---:|---:|
| 2 | 4 | 10 |
| 3 | 8 | 54 |
| 4 | **15** | 274 |
| 5 | — | (capped) |

The frontier grows $\times\,5.4,\,5.07$ — i.e. $\approx\!\times5.2$ per level,
**exponential**. (Depth-5 with a bounded cap + sampled triples overshoots to $33$;
that is a search-completeness artifact — the formulas are exact, so a complete
search returns $F_5=25$ — not a property of the construction.)

**Net.** The clean 2-cut is the right object: it makes $q_0=1$ free, the schedule
a 1-parameter 2-cut, the heights exact closed formulas, and the state just two
staircases. This is strictly more tractable than the general profile (frontier
$\times5.2$ vs $\times\!\sim10$, §12.2). **But it is still exponential** — the
$(\mathrm{pre}_1,\mathrm{suf}_2)$ Pareto frontier blows up, so the construction
does not close computationally. The surviving obstruction is now pinned to one
precise quantity: *the growth rate of the 2-staircase $(\mathrm{pre}_1,
\mathrm{suf}_2)$ frontier*. Whether that frontier admits a polynomial generating
description (closing the construction, hence $\lambda=3/2$) is the residual open
question — the same staircase wall (§12, §14), now in its most attenuated and
explicit 2-objective form.

## 19. The 2-staircase state is exactly closed under the 2-cut

Section 18 used exact formulas for the terminal heights. The next check is whether
the reduced state itself is closed: can the parent
$(\mathrm{pre}_1,\mathrm{suf}_2)$ be computed without reconstructing the full
order or carrying interval profiles? For the clean 2-cut, yes.

Let
$$
\pi=[\,M_2[{:}s]\,]\,[\,M_0\,]\,[\,M_1\,]\,[\,M_2[s{:}]\,],
\qquad m=|M_i|.
$$
Write $P_b(a)=\mathrm{pre}_1^{M_b}(a)$ and
$S_b(a)=\mathrm{suf}_2^{M_b}(a)$. Then the parent prefix staircase
$P(t)=\mathrm{pre}_1^\pi(t)$ is
$$
P(t)=
\begin{cases}
P_2(t), & 0\le t\le s,\\
\max(P_2(s),P_0(t-s)), & s\le t\le s+m,\\
\max(q_1(M_0),P_1(t-s-m)+P_2(s)), & s+m\le t\le s+2m,\\
\max(q_1(M_0),q_1(M_1)+P_2(s),P_2(t-2m)), & s+2m\le t\le3m.
\end{cases}
$$
Similarly, if $R(t)$ is the colour-2 height of the suffix starting at parent
position $t$ (so $\mathrm{suf}_2^\pi(\ell)=R(3m-\ell)$), then
$$
R(t)=
\begin{cases}
\max(S_2(m-t),q_2(M_1),q_2(M_0)+S_2(m-s)), & 0\le t<s,\\
\max(q_2(M_1),S_0(m-t+s)+S_2(m-s)), & s\le t\le s+m,\\
\max(S_1(2m+s-t),S_2(m-s)), & s+m\le t\le s+2m,\\
S_2(3m-t), & s+2m\le t\le3m.
\end{cases}
$$
These formulas are implemented as `parent_state_2cut` in
`scripts/stilde_face_2cut.py` and validated in `tests/test_stilde_face_2cut.py`:
exhaustively for all $B_1\to B_2$ triples and all cuts, and for every cut of the
depth-4 face witness modules.

So the reduced algebra is exact: under the clean 2-cut, no hidden interval state
is being smuggled in. The remaining obstruction is genuinely the size/structure
of the closed 2-staircase Pareto frontier itself.

## 20. First growth proof attempt: jump-position antichains

With §19 in hand, we can separate two objects:

- the **representative recursion** used in §18 to find good constructions
  quickly (frontier sizes about $10,53,264$), and
- the **full closed 2-staircase algebra**, which keeps every Pareto-minimal
  $(\mathrm{pre}_1,\mathrm{suf}_2)$ state generated by the exact 2-cut formulas.

The full algebra is already much larger. Starting from the exact depth-2 reduced
frontier (10 states), one exact 2-cut closure step produces
$$
10^3\cdot 10=10000 \text{ candidates},\qquad
5832 \text{ distinct reduced states},\qquad
\boxed{488}\text{ Pareto-minimal states at depth 3}.
$$
Of these, $\boxed{124}$ have the same terminal height pair $(q_1,q_2)=(3,3)$.
Thus the frontier growth is not mainly height-pair diversity; it is staircase
breakpoint diversity. This is certified by
`scripts/stilde_2staircase_growth.py` and `tests/test_stilde_2staircase_growth.py`.

**Jump-vector normal form.** For a monotone staircase $X$ with terminal height
$h$, define its jump vector
$$
J(X)=(j_1,\ldots,j_h),\qquad
j_r=\min\{t:X(t)\ge r\}.
$$
For two staircases of the same terminal height,
$$
X\le Y \text{ pointwise}\quad\Longleftrightarrow\quad J(X)\ge J(Y)
\text{ coordinatewise}.
$$
So inside a fixed height pair $(q_1,q_2)$, dominance of reduced states is exactly
coordinatewise dominance on
$$
J(\mathrm{pre}_1)\times J(\mathrm{suf}_2)\in [0,3^k]^{q_1+q_2}
$$
with the order reversed in every coordinate. The 124 states in the $(3,3)$ slice
are therefore a genuine antichain in a 6-dimensional jump-position grid.

This also gives the clean local mechanism. Fix three child states and vary only
the cut $s$. If for $s<t$ one prefix jump moves right while one suffix jump moves
left, then neither resulting parent dominates the other:
$$
j_a(P_s)<j_a(P_t),\qquad j_b(S_s)>j_b(S_t).
$$
The five cuts $s=4,\ldots,8$ for the canonical depth-2 child triple
$(2,2),(2,2),(2,3)$ realise exactly this tradeoff and survive in the full
depth-3 Pareto frontier. This is the small certified antichain in
`sample_cut_antichain()`.

**Where the proof still fails.** The jump-vector lemma proves the structure of
the obstruction and gives a reusable antichain criterion. What is still missing
for an asymptotic theorem is the **external nondomination induction**: after
constructing many cut-tradeoff states at level $k+1$, one must prove that no
other generated state dominates them. At depth 3 this is checked exhaustively;
for general $k$ it would require a new invariant lower-bounding at least one
jump coordinate against all possible competing triples.

So the first proof attempt does not close $\lambda=3/2$, but it sharpens the
frontier question substantially:

> The closed 2-staircase frontier is a jump-position antichain problem. A
> polynomial generating description, if it exists, must describe these correlated
> high-dimensional antichains without enumerating their points; endpoint heights
> or scalar summaries cannot do it.

## 21. Proof start: the plateau-antichain lemma

The external nondomination problem can be split into two clean pieces. Work in
one generation step of the closed 2-staircase algebra, and let $\mathcal G$ be
the set of all generated states before Pareto pruning. For a height pair
$(A,B)$, write
$$
\mathcal G_{A,B}=\{X\in\mathcal G:(q_1(X),q_2(X))=(A,B)\}.
$$

**Plateau-antichain lemma.** Suppose a family
$\mathcal A\subseteq\mathcal G_{A,B}$ satisfies:

1. (**scalar isolation**) no state of $\mathcal G$ has
   $q_1\le A,\ q_2\le B$ unless its height pair is exactly $(A,B)$;
2. (**slice minimality**) every state of $\mathcal A$ is Pareto-minimal inside
   the fixed slice $\mathcal G_{A,B}$.

Then every state of $\mathcal A$ survives in the full Pareto frontier of
$\mathcal G$.

**Proof.** Let $X\in\mathcal A$, and suppose some generated state $Y\in\mathcal G$
dominates $X$ in the reduced two-staircase order. Dominance of staircases implies
dominance of endpoints, so $q_1(Y)\le A$ and $q_2(Y)\le B$. By scalar isolation,
$Y\in\mathcal G_{A,B}$. By slice minimality, $Y$ cannot strictly dominate $X$
inside that slice. Hence no generated state strictly dominates $X$, so $X$ is in
the full Pareto frontier. $\square$

This is the first usable proof mechanism for external nondomination. It says the
asymptotic antichain proof does **not** need to compare a proposed cut family
against every possible competing triple directly. It is enough to prove:

- a scalar lower-bound/endpoint-isolation statement for the plateau height pair;
- a fixed-slice jump-antichain statement, where dominance is just coordinatewise
  jump-position dominance (§20).

The depth-3 cut family from §20 satisfies this certificate exactly. In the full
one-step candidate set from the 10 depth-2 states:

- $(3,3)$ is scalar-isolated: no candidate has both endpoints $\le(3,3)$ with a
  different height pair;
- the five cuts $s=4,\ldots,8$ from child shapes $(2,2),(2,2),(2,3)$ are
  Pareto-minimal inside the $(3,3)$ slice;
- therefore those five states survive in the full depth-3 frontier.

This is implemented by `scalar_minimal_pair`, `slice_pareto_frontier`, and
`sample_cut_antichain` in `scripts/stilde_2staircase_growth.py`, with the
certificate checked in `tests/test_stilde_2staircase_growth.py`.

**What remains for an asymptotic proof.** The open analytic problem is now a
recursive plateau construction:

> For infinitely many levels, construct a height pair $(A_k,B_k)$ and a cut
> family $\mathcal A_k$ of super-polynomial size such that $(A_k,B_k)$ is
> scalar-isolated and $\mathcal A_k$ is a jump-position antichain inside the
> fixed slice.

Proving such a family gives an exponential lower bound on the closed frontier.
Conversely, proving every scalar-isolated slice has a polynomial jump-frontier
would be the first plausible route to a polynomial generating description. The
lemma is therefore the proof interface: scalar endpoint bounds on one side,
Sperner/jump-position antichains on the other.

## 22. Why the plateau proof does not yet finish

The natural attempt is to iterate the depth-3 plateau family from §21. This fails
in the scalar-isolation step, and the failure is now exact.

Let $\mathcal A_3$ be the five-cut family in the scalar-isolated $(3,3)$ slice.
Close it once using only the clean 2-cut algebra on $\mathcal A_3$. The restricted
frontier has
$$
|\mathrm{Pareto}(\mathcal A_3^3\times[0,27])|=580,
$$
with $485$ states in the large next slice $(5,5)$:
$$
(5,5):485,\qquad (4,6):60,\qquad (6,4):25,\qquad (3,6),(6,3):5\text{ each}.
$$
So the local antichain mechanism is strong: five states already generate a
hundreds-sized next frontier. But the slice $(5,5)$ is **not scalar-isolated** in
the full depth-4 algebra, because lower scalar boundary states such as $(4,4)$,
$(3,5)$, and $(5,3)$ exist. Thus §21 cannot be iterated with scalar isolation
alone.

This does **not** mean the $(5,5)$ family is dominated. Direct witness checks show
that standard lower boundary witnesses $(4,4)$, $(3,5)$, and $(5,3)$ dominate
none of the 485 restricted $(5,5)$ states. The obstruction is subtler: to finish
the proof one needs a **jump-separation inequality** excluding *all* lower scalar
competitors, not just the known witnesses.

The missing theorem can be stated cleanly. For a target family
$\mathcal A_{k+1}\subseteq\mathcal G_{A,B}$, prove that every generated state
$Y$ with $(q_1(Y),q_2(Y))\le(A,B)$ and $(q_1(Y),q_2(Y))\ne(A,B)$ fails to dominate
the family because one of its jump coordinates is too early:
$$
\exists r\le q_1(Y)\quad J_r(\mathrm{pre}_1^Y)<\min_{X\in\mathcal A_{k+1}}
J_r(\mathrm{pre}_1^X),
$$
or symmetrically
$$
\exists r\le q_2(Y)\quad J_r(\mathrm{suf}_2^Y)<\min_{X\in\mathcal A_{k+1}}
J_r(\mathrm{suf}_2^X).
$$
This is the exact replacement for scalar isolation. If such a delayed-jump
barrier can be proved recursively, the exponential antichain proof finishes. If
one proves the opposite — that lower scalar states can always cover the
cut-tradeoff antichain with polynomially many jump patterns — then the polynomial
frontier side becomes plausible.

So the proof is now reduced to a single extremal statement:

> Low endpoint heights force an early jump in at least one of the two staircases.

That statement is the analytic core. The current data supports it at the first
nontrivial step for the standard boundary witnesses, but a proof must quantify it
over the entire generated lower scalar region.

### 18.1 Why a low-product family is not self-consistent

For the *upper* bound $\lambda_F\le3/2$ it would suffice to exhibit a small
self-consistent family with product $(3/2)^{k+o(k)}$ — no nondomination needed.
The natural candidate (greedily keep the lowest-product states) **fails**, and the
failure is sharp. Running the closed recursion (`stilde_2staircase_growth`) but
keeping only states whose product equals the current optimum gives

$$
F_2^{\text{greedy}}=4,\quad F_3^{\text{greedy}}=8,\quad F_4^{\text{greedy}}=\mathbf{16}\ (\ne F_4=15).
$$

The reason: the depth-4 optimum $(1,3,5)$ is built from the depth-3 module $(1,3,5)$,
whose product is $15$ — *suboptimal at depth 3* (where $F_3=8$). A product-capped
frontier discards it, and the construction collapses to the lexicographic $2^k$.

So **the optimal construction provably requires suboptimal-product modules**, and
the set of such modules is the exponential frontier (488 at depth 3, §18). A
self-consistent family achieving $(3/2)^{k+o(k)}$, if one exists, cannot be the
low-product states alone — it must carry a growing reservoir of off-optimal
shapes. Whether that reservoir can be kept *small* (polynomial) is exactly the
open question, equivalent to bounding the jump-position antichain. This is the
final, sharpest form of the order-dependence wall (§9.4, §12, §14): the same
obstruction, now reduced to a single antichain-growth question in the closed
2-staircase algebra.

## 23. The delayed-jump barrier is false (and which way it points)

The §22 reduction asked to prove the **delayed-jump barrier**: every generated
lower-scalar state $Y$ (with $(q_1,q_2)\le(A,B)$, $\ne(A,B)$) fails to dominate the
cut-tradeoff family in slice $(A,B)$. We tested it computationally at the first
nontrivial step and it is **false**.

**The $(5,5)$ plateau family is entirely dominated.** Take $\mathcal A_3$ (the
five-cut $(3,3)$ family), close it once to the restricted frontier, and keep its
$485$ states in the $(5,5)$ slice (the family §22 hoped to iterate). Generate
depth-4 states from the full depth-3 frontier (488 states) and look for
lower-scalar dominators:

$$
\boxed{485/485 \text{ of the }(5,5)\text{ family are dominated}},\qquad
\text{0 survive.}
$$

Every one is dominated by a generated $(4,5)$ or $(5,4)$ state — exactly the two
boundary slices the §22 witness list ($(4,4),(3,5),(5,3)$) omitted. A verified
explicit instance: $Y=(1,5,4)$ (product 20) dominates $x=(1,5,5)$ (product 25),
with $\mathrm{pre}_1^Y\le\mathrm{pre}_1^x$ and $\mathrm{suf}_2^Y\le\mathrm{suf}_2^x$
pointwise ($Y\ne x$); `parent_state_2cut` is the validated closure, so $Y$ is a
genuine achievable state. (`tests/test_stilde_2staircase_growth.py::
test_delayed_jump_barrier_is_false`.)

**Consequence — the route flips.** The barrier was the proposed engine for an
*exponential* frontier lower bound (iterate the plateau, prove it survives). Its
failure kills that route: the plateau does not iterate, not because of scalar
isolation alone, but because the higher antichain is *covered* by lower-scalar
states. By §22's own dichotomy, "lower scalar states can always cover the
cut-tradeoff antichain" is precisely the **polynomial-frontier / pod-tight**
side. Here the entire $(5,5)$ antichain ($485$ states) is absorbed by just two
boundary slices $(4,5),(5,4)$.

**But this does not finish $\lambda=3/2$.** It is one closure step. It shows the
plateau-iteration *exponential* argument is dead and that *at this step* the
frontier concentrates on lower-scalar boundary slices — evidence for, not a proof
of, a polynomial frontier. A real pod-tightness proof now needs the **covering to
be shown recursively**: that at every level each high-scalar slice's jump-antichain
is dominated by polynomially many lower-scalar boundary states. That is the new,
sharper, and (per this evidence) more *plausible* target — the mirror image of the
delayed-jump barrier, now pointing toward $\lambda=3/2$ rather than away from it.

## 24. The polynomial-frontier route is not viable: the boundary antichain grows

§23 refuted the delayed-jump barrier and, by §22's dichotomy, pointed toward the
**polynomial-frontier** side. We tested whether that side can actually close
$\lambda=3/2$, and the answer is **no**: even the frontier *at the optimal product*
$F_k$ is a growing jump-antichain, so no covering theorem about high-scalar slices
can make the frontier polynomial.

**The boundary frontier grows.** Measure the Pareto-minimal states at product
exactly $F_k$ (the only product that matters for $F_k$):

| depth $k$ | $F_k$ | boundary Pareto states (product $=F_k$) | slices |
|---|---:|---:|---|
| 3 (exact) | 8 | $28$ | low |
| 4 (sampled, lower bound) | 15 | $\ge126$ | $(3,5){:}67,\ (5,3){:}59$ |

So the boundary antichain grows $\ge28\to126$ ($\times4.5$ in one step), and the
near-boundary frontier grows faster still (product $\le20$ at depth 4 already has
$\ge3253$ Pareto states). This is a $\le$ (sampled lower bound), so the true
growth is at least this large.

**Consequence — the route is dead.** A polynomial generating description requires
the *surviving* frontier to be polynomial. But the surviving frontier *at the
optimal product alone* is already a growing jump-antichain ($\ge126$ at depth 4,
in the boundary slices $(3,5),(5,3)$). The §23 covering of high-scalar slices does
not help: the obstruction is not the high slices, it is the boundary slices
themselves, which are not dominated (they are the minimum) and carry exponentially
growing jump-antichains. So:

> Neither side of the §22 dichotomy gives a clean theorem. The frontier is
> super-polynomial *even restricted to the optimal product* $F_k$, so the
> polynomial-frontier route to $\lambda=3/2$ is not viable; and §23 already killed
> the plateau-iteration exponential-lower-bound route.

**Honest status.** The whole closed-2-staircase program — exact formulas (§18),
exact closure (§19), jump-antichain reframing (§20), plateau lemma (§21), barrier
(§22), barrier-refutation (§23), boundary-growth (§24) — has mapped the obstruction
to its sharpest form and shown that *frontier-tracking cannot prove $\lambda=3/2$*:
the closed frontier is super-polynomial at every product level including the
optimal one. $\lambda=3/2$ remains genuinely open. A proof, if one exists, must be
a **direct asymptotic family argument** — exhibit orders with product
$(3/2)^{k+o(k)}$ without enumerating or tracking the Pareto frontier — or a direct
lower bound $\lambda>3/2$. The construction route, in every closed/compressed form,
is exhausted: finite computation and frontier algebra do not settle the dichotomy.

## 25. The Shearer pair-rigidity route is dominated by direct computation (engine-readiness screen, vector 1)

A 2026-06-20 scout panel (run to decide whether to launch the autonomous engine on
$\lambda$) surfaced exactly one candidate *finite* oracle — the **pair-marginal
rigidity gap** — distinct from the dead frontier-tracking program. We built and ran
it (`scripts/stilde_pair_marginal_screen.py`, data in
`data/pair_marginal_screen.json`). Verdict: the route cannot give the engine a
finite handle on $\lambda$, for a rigorous order-independent reason.

**The route.** For the rank triple $R(v)=(r_0,r_1,r_2)$ of a uniform vertex, with
pair marginals $H(r_c,r_{c+1})$ and gap
$g_c=\log_2(q_cq_{c+1})-H(r_c,r_{c+1})\ge0$, the chain

$$2\log_2 Q=\sum_c\log_2(q_cq_{c+1})=\sum_c\big[H(r_c,r_{c+1})+g_c\big]\ge 2H(R)+\sum_c g_c\ge 2d\log_2\tfrac32+\sum_c g_c$$

(Shearer $H(R)\le\frac12\sum_c H(r_c,r_{c+1})$; transitive-cell bound
$H(R)\ge d\log_2\frac32$) gives, writing $S=\sum_c g_c$,

$$\log_2 Q(\pi)\;\ge\; d\log_2\tfrac32+\tfrac12 S(\pi),\qquad
\lambda_{\mathrm{lb}}(\pi)=\tfrac32\cdot 2^{\,S(\pi)/2d}.$$

To beat $3/2$ the route must show $S(\pi^\*)/d\ge\delta>0$ at the minimizer,
non-decaying in $d$.

**Proposition (domination).** *For every order $\pi$,
$\lambda_{\mathrm{lb}}(\pi)\le Q(\pi)^{1/d}$; hence the strongest certificate this
route can produce at depth $d$ is $\le L_d^{1/d}$.*

*Proof.* The displayed inequality is a **lower** bound $B(\pi)=d\log_2\frac32+\frac12
S(\pi)$ on $\log_2 Q(\pi)$, so $B(\pi)\le\log_2 Q(\pi)$ and
$\lambda_{\mathrm{lb}}(\pi)=2^{B(\pi)/d}\le Q(\pi)^{1/d}$. Minimizing over $\pi$ gives
$\le L_d^{1/d}$. $\square$

Equivalently $S(\pi^\*)\le 2\big(\log_2 L_d-d\log_2\frac32\big)$ — the gap cannot
exceed twice the *true* log-excess of $L_d$ over $(3/2)^d$. So proving $\lambda>3/2$
via this route is equivalent to proving the gap **asymptotically saturates its own
excess cap** ($S(\pi^\*)=2(\log_2 L_d-d\log_2\frac32)-o(d)$) — a fresh asymptotic
statement, with **no finite oracle**, no easier than the original, and (crucially)
$L_d^{1/d}$ already converges to $\lambda$ from above by submultiplicativity, so the
Shearer machinery adds nothing a direct $L_d$ computation does not.

**Screen data** (witnesses at the $L_d$/$F_d$-optimal shapes; all invariants
$g_c\ge0$, Shearer, $H(R)\ge d\log_2\frac32$, cap — verified):

| depth | shape | $S$ | $S/d$ | excess cap | $S/\text{cap}$ | $\lambda_{\mathrm{lb}}$ | $L_d^{1/d}$ |
|---|---|---:|---:|---:|---:|---:|---:|
| 2 | $(1,1,4)$ | 0.327 | 0.163 | 1.660 | 0.20 | 1.587 | 2.000 |
| 2 | $(1,2,2)$ | 0.200 | 0.100 | 1.660 | 0.12 | 1.553 | 2.000 |
| 2 | **max over all 246 minimizers** | 0.714 | 0.357 | 1.660 | 0.43 | **1.698** | 2.000 |
| 3 | $(1,1,8)$ | 0.490 | 0.163 | 2.490 | 0.20 | 1.587 | 2.000 |
| 3 | $(1,2,4)$ | 0.724 | 0.241 | 2.490 | 0.29 | 1.631 | 2.000 |
| 3 | $(2,2,2)$ | 0.499 | 0.166 | 2.490 | 0.20 | 1.589 | 2.000 |
| 4 | $(1,3,5)$ | 0.464 | 0.116 | 3.134 | 0.15 | 1.562 | 1.968 |
| 5 | $(2,3,4)$ | 0.230 | 0.046 | 3.320 | 0.07 | 1.524 | 1.888 |
| 5 | $(1,5,5)$ | 0.296 | 0.059 | 3.438 | 0.09 | 1.531 | 1.531\* |

Every $\lambda_{\mathrm{lb}}\le L_d^{1/d}$ (Proposition, confirmed). The gap is a
**shrinking fraction of its cap** ($\approx0.20$ at $d{=}2,3\to0.07$–$0.09$ at
$d{=}5$): nowhere near the saturation $\lambda>3/2$ would require — weak lean toward
$\lambda=3/2$.

**Caveat (honest).** Single SAT witnesses *underestimate* $S$: the $d{=}2$
exhaustive max-over-minimizers (1.698) beats the solver witness (1.587). So the
single-witness $S/d$ trend is solver-dependent and must **not** be over-read as a
clean decay (the cake/H19 lesson). The load-bearing conclusion is the order-
independent Proposition, not the empirical trend.

**Engine verdict.** This was the one candidate finite oracle. The screen shows it
does not decide $\lambda$: the deciding step (does the rigidity gap saturate its cap
asymptotically?) is irreducibly analytic — the same wall all five scouted vectors
conceded. **No decision-relevant finite oracle exists**, so the autonomous engine
(breadth + finite-verify) has no well-posed target here; pointing it at $\lambda$
would default to the §24-futile finite scans. Recommendation stands: do not launch.

## 26. Direct analytic construction attempt: the balanced-cut invariant

After §18--§25, a proof of $\lambda=3/2$ must give a direct family of orders, not
a frontier enumeration. The cleanest possible invariant is a **balanced cut** in
the closed 2-cut algebra.

Let
$$
\beta=\sqrt{3/2},\qquad \eta=\beta-1.
$$
Suppose a $q_0=1$ state $X_k$ of $B_k$ has
$$
q_1(X_k),q_2(X_k)\le T_k
$$
and has a cut $s$ with
$$
\mathrm{pre}_1(X_k,s)\le \eta T_k+o(T_k),\qquad
\mathrm{suf}_2(X_k,3^k-s)\le \eta T_k+o(T_k).
$$
Then the clean 2-cut order
$$
X_{k+1}=X_k[{:}s]\;|\;X_k\;|\;X_k\;|\;X_k[s{:}]
$$
has, by the exact formulas of §18,
$$
q_1(X_{k+1}),q_2(X_{k+1})
\le (1+\eta)T_k+o(T_k)=\beta T_k+o(T_k).
$$
Iterating such a state would give
$$
q_1(X_k)q_2(X_k)\le \beta^{2k+o(k)}=(3/2)^{k+o(k)},
$$
and hence $\lambda=3/2$.

So the direct construction proof is reduced to one sharp invariant:

> Build $q_0=1$ states whose colour-1 prefix mass and colour-2 suffix mass have a
> common cut where both are at most $(\sqrt{3/2}-1+o(1))$ of the endpoint height.

This is a genuine analytic target, but the naive self-similar version fails. If
one starts from a symmetric depth-2 face state $(1,2,2)$ and at each step takes
three identical copies with the best clean 2-cut, the verified sequence is
$$
(1,2,2)\to(1,2,4)\to(1,4,4)\to(1,4,8)\to(1,8,8)\to\cdots,
$$
with products $4,8,16,32,64,\ldots$ — exactly the lexicographic $2^k$ regime, not
$(3/2)^k$. The reason is structural: identical copies have no cheap complementary
modules. One of the two crossings always pays the full old height, so the best
cut alternates between putting all of $M_2$ before or after the middle blocks.

Thus a successful direct construction cannot be purely self-similar in one state.
It must carry at least a small **portfolio** of complementary states: one cheap in
$q_2$, one cheap in $q_1$, and one balanced state supplying the cut. This matches
the decoded finite optima:
$$
(1,A,B)\quad\leftarrow\quad
M_0=(1,A,b_0),\quad M_1=(1,a_1,B),\quad M_2=(1,A,B).
$$

**Status.** This is the closest analytic proof skeleton currently available:
prove a portfolio version of the balanced-cut invariant, and $\lambda=3/2$
follows. But the portfolio invariant is exactly where the known finite optima use
off-product modules and where the frontier grows. I do not have the missing
portfolio construction. The proof is therefore not complete.

## 27. Portfolio cut certificate: local closure vs companion regeneration

The next useful target is not another frontier enumeration; it is to isolate the
portfolio step as an exact lemma.  Let $M_0,M_1,M_2$ be $q_0=1$ child states and
consider the clean 2-cut
$$
M_2[{:}s]\;|\;M_0\;|\;M_1\;|\;M_2[s{:}].
$$
Fix an endpoint target $(A,B)$. By the exact formulas of §18, this 2-cut has
parent heights at most $(1,A,B)$ if and only if
$$
\max(q_1(M_0),q_1(M_2))\le A,\qquad
\max(q_2(M_1),q_2(M_2))\le B,
$$
and there is a cut $s$ with
$$
\mathrm{pre}_1(M_2,s)\le A-q_1(M_1),\qquad
\mathrm{suf}_2(M_2,m-s)\le B-q_2(M_0).
$$
This is now implemented as `portfolio_cut_certificates` in
`scripts/stilde_face_2cut.py`.

The known face optima satisfy this certificate in its cleanest possible form:
$$
(1,3,5)\leftarrow (1,3,3),(1,2,5),(1,3,5)
$$
has cuts $s=8,9,10,11$ with required slack
$A-q_1(M_1)=1$ and $B-q_2(M_0)=2$, and
$$
(1,5,5)\leftarrow (1,5,3),(1,4,5),(1,5,5)
$$
has cuts $s=24,25,26,27$ with the same slack $(1,2)$.  These are checked in
`tests/test_stilde_face_2cut.py`, using the SAT depth-4 witness and the cached
depth-5 witness from `data/L5_refutation.json`.

So the local mechanism is no longer vague: a balanced module $M_2$ supplies a
small simultaneous cut, while $M_0$ is cheap in colour $2$ and $M_1$ is cheap in
colour $1$.  The 2-cut then preserves the endpoint pair $(A,B)$ exactly.

But this is still not an induction. The step produces the balanced parent
$(1,A,B)$; it does not automatically produce the next-level companions
$(1,A,B-2)$ and $(1,A-1,B)$.  For example, the depth-5 optimum
$(1,5,5)$ uses depth-4 companions $(1,5,3)$ and $(1,4,5)$, but the same
companions cannot exist at depth $5$: their products $15$ and $20$ would
contradict $L_5=24$.  Thus the remaining analytic problem is sharper than §26:

> **Companion-regeneration problem.** Construct a growing boundary of triples
> $(1,A_k,B_k-r_k)$, $(1,A_k-r'_k,B_k)$, $(1,A_k,B_k)$, with
> $A_kB_k\le (3/2)^{k+o(k)}$, such that the balanced state has a cut whose
> $\mathrm{pre}_1/\mathrm{suf}_2$ costs are absorbed by the two companion
> deficits.

Solving this regeneration problem would give a direct $\lambda=3/2$ construction.
Conversely, any attempted portfolio proof that only preserves endpoints, without
regenerating the cheap companions on a growing boundary, cannot close.

## 28. Regeneration is an M₂-structure problem, not a companion problem (F₆ probe)

§27 left companion regeneration as the open target. A constructive probe
(`scripts/stilde_portfolio_f6_bound.py`, `tests/test_stilde_portfolio_f6_bound.py`)
that tried to leverage the portfolio 2-cut for an *upper bound* on $F_6$ — a route
direct depth-6 face SAT could not reach (§11.10) — localizes the obstruction
sharply. The key structural fact from §18: in
$Q_1=\max(q_1M_0,q_1M_2,q_1M_1+\mathrm{pre}_1(M_2,s))$,
$Q_2=\max(q_2M_1,q_2M_2,q_2M_0+\mathrm{suf}_2(M_2,m{-}s))$, **the companions
$M_0,M_1$ enter only as scalars; only $M_2$ carries the two staircases.** So
regeneration is *entirely* about $M_2$.

Three reproducible facts (`diagnose()`):

1. **Companions are not the obstruction.** The three $(5,7)$-portfolio modules
   $(1,5,7),(1,5,5),(1,4,7)$ all exist at depth 5 (SAT, exact heights). Companion
   *existence* is free.

2. **An arbitrary $M_2$ of the right heights fails.** A generic SAT witness for
   $(1,5,7)@5$ gives best 2-cut product $\mathbf{60}$, heights $(1,5,12)$: $q_2(M_0)=5$
   and the $M_2$ colour-2 suffix $=7$ **stack** to $12$, because no single cut makes
   $\mathrm{pre}_1$ and $\mathrm{suf}_2$ small *simultaneously*. (Target was $35$.)

3. **The structured optimum fails too.** The depth-5 optimum $(1,5,5)$ — which *was*
   built by a portfolio cut and has the simultaneous small cut **at the depth-4
   scale** (cuts 24–27) — has **zero** cuts with $\mathrm{pre}_1\le2$ and
   $\mathrm{suf}_2\le2$ **at the depth-5 scale** (none even up to slack $(3,3)$). The
   simultaneous-cut property is **not preserved** when the module is used one level
   up: the portfolio step pushes $\mathrm{pre}_1$ and $\mathrm{suf}_2$ to full height
   in anti-phase. The naive fixed-shape self-similar recursion correspondingly breaks
   at depth 5.

**Sharpened target (replaces §27's framing).**

> **$M_2$-regeneration.** Construct a depth-$(k{-}1)$ face module of product $F_k$
> that admits a *simultaneous* small cut $\mathrm{pre}_1(M_2,s)\le r_1$ **and**
> $\mathrm{suf}_2(M_2,m{-}s)\le r_2$ at one $s$, with $r_1,r_2=O(1)$.

Companion existence and endpoint preservation are solved; the whole difficulty is
this one simultaneous-cut property of the self-similar module, and it is exactly
what the portfolio step destroys. **No $F_6$ upper bound follows** from the current
machinery, because we cannot produce such an $M_2$ at product $F_6$. The natural
next probe is a SAT search with the cut *position* as a variable — directly asking
whether a product-$F_6$ module with a simultaneous $O(1)$ cut exists at depth 5; a
NO would refute the portfolio route, a YES would give $F_6$ and a construction
template.

## 29. The portfolio mechanism breaks at depth 6 (simultaneous-cut SAT, F₆ ≤ 45)

§28 reduced the open target to a finite question: does a depth-5 face module of
product $F_6$ admit a *simultaneous* small cut? We built the SAT oracle for it
(`scripts/decide_simultaneous_cut.py`, `tests/test_decide_simultaneous_cut.py`).
The encoding adds, on top of the validated level-labeling height encoding, a cut
boolean per vertex constrained to a prefix of the order, plus two conditional
thermometers — colour-1 capped $r_1$ over before-cut pairs, colour-2 capped $r_2$
over after-cut pairs. Validated at depth 3: the $(1,3,5)$ module has a $(1,2)$ cut
(not a $(1,1)$ one), $(1,1,1)$ is infeasible — all `verified` against
`step_profile`.

**Result (depth 5, each target at the most permissive slack whose companions clear
the $F_5=25$ floor):**

| product | $(A,B)$ | slack | simultaneous cut? |
|---:|---|---|---|
| 35 | $(5,7)$ | $(1,2)$ | **UNSAT** |
| 35 | $(7,5)$ | $(2,1)$ | **UNSAT** |
| 36 | $(6,6)$ | $(1,1)$ | **UNSAT** |
| 40 | $(5,8)$ | $(1,3)$ | **UNSAT** |
| 42 | $(6,7)$ | $(2,2)$ | **UNSAT** |
| **45** | $(5,9)$ | $(2,4)$ | **SAT** (verified) |
| 48 | $(6,8)$ | $(2,3)$ | SAT |
| 49 | $(7,7)$ | $(3,3)$ | SAT |

**Two firm conclusions.**

1. **The clean slack-$(1,2)$ mechanism is dead at depth 6.** Every $(1,2)$-slack
   target is UNSAT; the simultaneous cut that produced $F_4=15$ and $F_5=25$ has no
   analogue at the $F_6$ product. Products $35,36,40,42$ are all unreachable by the
   portfolio. The "simultaneous $O(1)$ cut" of §28 does **not** exist at a product
   that would continue the trend — a clean *negative* answer to the §28 probe.

2. **$F_6 \le 45$, certified.** The minimum portfolio-reachable product is $45$,
   via $M_2=(1,5,9)$ with a verified $(2,4)$ cut and existing companions
   $(1,5,5),(1,3,9)$; `pod_profile` confirms a depth-6 face order of heights
   $(1,5,9)$, product $45$, $q_0=1$. This improves the submultiplicative bound
   $F_6\le F_5F_1=50$. But $45/(3/2)^6=3.95 > F_5/(3/2)^5=3.29$: the slack had to
   **grow** $(1,2)\to(2,4)$ and the ratio jumped up.

**Interpretation.** The portfolio 2-cut — the exact mechanism behind the clean
$F_4,F_5$ optima — does **not** extend to a pod-tight construction: at depth 6 it
needs growing slack and lands at product $45$, off the $(3/2)^k$ trend. This does
not settle $\lambda$ (the true $F_6$ could be below $45$ via a different
construction, and direct $F_6$ SAT is infeasible, §11.10), but it **closes the
portfolio route as a path to $\lambda=3/2$**: a single-cut self-similar recursion
with $O(1)$ slack cannot produce $B_6$'s face optimum. Either $\lambda_F>3/2$, or
the optimal construction changes character at depth 6 (multi-cut / non-self-similar)
— and the §28 reduction shows the obstruction is precisely the anti-phase of the
colour-1 prefix and colour-2 suffix, now SAT-proven at the $F_6$ product.

## 30. Two-cut extension: no $F_6<45$ in the three-piece portfolio family

The next natural relaxation is to let the floating module have a middle block:
$$
M_2[{:}s]\;|\;M_0\;|\;M_2[s{:}t]\;|\;M_1\;|\;M_2[t{:}],
\qquad 0\le s\le t\le m.
$$
On the $q_0=1$ face this still has exact scalar formulas:
$$
Q_1=\max(q_1M_0,q_1M_2,q_1M_1+\mathrm{pre}_1(M_2,t)),
$$
$$
Q_2=\max(q_2M_1,q_2M_2,q_2M_0+\mathrm{suf}_2(M_2,m-s)).
$$
So the middle block is counted by both tests: it lies after $M_0$ for the
colour-2 suffix and before $M_1$ for the colour-1 prefix. This is the cleanest
way to test whether the anti-phase obstruction in §29 was merely caused by
forcing $s=t$.

The SAT encoding (`scripts/decide_two_cut.py`) uses two prefix booleans:
`left(v)` for membership before the first cut and `right(v)` for membership
before the second cut, with `left => right`. The colour-1 conditional thermometer
is active on the `right` prefix; the colour-2 conditional thermometer is active on
the complement of the `left` prefix. The exact formulas and order reconstruction
are implemented as `parent_heights_3piece` / `order_3piece` and validated against
`closure_heights` on all $B_1\to B_2$ face triples.

We then scanned every ordered target pair $(A,B)$ with
$$
25\le AB<45,\qquad A,B\ge2,
$$
using the maximal companion slack allowed by the $F_5=25$ floor:
$$
r_1=A-\left\lceil\frac{25}{B}\right\rceil,\qquad
r_2=B-\left\lceil\frac{25}{A}\right\rceil.
$$
Zero-slack edge cases are included. The result is decisive for this family:
$$
\boxed{52\text{ targets tested};\quad 0\text{ SAT};\quad 52\text{ UNSAT}.}
$$
The ledger is saved in `data/two_cut_f6_scan.json`.

At the boundary, the oracle still sees the known construction:
$(A,B)=(5,9)$ with slack $(2,4)$ is SAT and verifies a depth-6 parent of heights
$(1,5,9)$, product $45$. In that model the two cuts coincide ($s=t=102$), so the
best two-cut construction collapses back to the one-cut portfolio witness.

**Conclusion.** Allowing one middle $M_2$ block does **not** improve the bound:
the three-piece portfolio family proves no $F_6<45$ construction. If $F_6<45$ is
true, it must use a genuinely different face schedule (more cuts, different
module roles, or a non-portfolio construction), not merely the two-cut relaxation
of §29.

## 31. 45 is a robust barrier across construction families (general interleaving)

§29 (one-cut) and §30 (two-cut) both plateau at product $45$. Two further facts
close the construction approach.

**The two-cut is the *complete* "$M_2$-floating, companions-as-blocks" family.**
The exact formulas depend on $M_2$ only through $\mathrm{pre}_1(M_2,t)$ and
$\mathrm{suf}_2(M_2,m-s)$ — i.e. only on *where* $M_0,M_1$ sit (positions $s\le t$).
Splitting $M_2$ into more pieces adds no parameters, so no $k$-cut ($k>2$) can beat
the two-cut. **The only remaining freedom is to split a companion** — let a full
interleaving have $M_0,M_1$ contribute staircases, not just scalars.

**General interleaving does not beat 45 either.** Tested via the §10 closure
(`scripts/probe_general_interleave_f6.py`): for the *structured* portfolio modules
($M_2$ = the simultaneous-$(2,4)$-cut $(1,5,9)$ witness, companions $(1,5,5)$,
$(1,3,9)$), the closure correctly sees the 2-cut path reach $(1,5,9)=45$ (visited
12433), but **no** full lattice-path interleaving reaches a face product below $45$.
(Arbitrary `decide_caps_labeling` witnesses cannot even reach 45 — min $50$ —
re-confirming §28: only structured modules realize the optimum.)

**Status after the construction scan.** The barrier $45$ is robust across the
one-cut, two-cut, and general-interleaving families. At this point this was only
the *construction* (upper) side:
$$
18 = d_6 = \vec\chi(B_6) \le L_6 \le F_6 \le 45 .
$$
So before using the boundary-cut lemma below, $F_6\in[18,45]$ was still a wide
range. $F_6\le45$ also tightens $L_6\le45$ (was $48$).

With the boundary-cut certificate of §32, $F_6=45$, so
$F_k=2,4,8,15,25,45$ gives roots
$F_k^{1/k}=2,2,2,1.968,1.904,\mathbf{1.886}$ (still falling, so $\lambda_F\le1.886$)
and ratios $F_k/(3/2)^k=1.33,1.78,2.37,2.96,3.29,\mathbf{3.95}$ (still rising).
**Both are consistent with $\lambda_F=3/2$ (a polynomial prefactor) and with
$\lambda_F>3/2$**; six points do not separate them — the same over-read trap as the
cake numbers, H19, and the retracted "$\lambda\approx2$". $\lambda$ remains genuinely
undetermined. The construction approach has reached its tractability ceiling at
$45$; a decisive answer needs a *direct asymptotic argument* (or the intractable
exact $F_6$), not another construction family.

## 32. Boundary-cut lower bound: the face value is exact, $F_6=45$

The preceding construction-side caution was too conservative: the same cut oracle
also supplies a lower bound for the *whole* $q_0=1$ face.

Let a depth-6 face order have heights at most $(1,A,B)$, and decompose the top
level into depth-5 modules $M_0,M_1,M_2$. Since $q_0=1$, the face language (§17)
forces every $M_0$ vertex to appear before every $M_1$ vertex. Take the separator
after all of $M_0$ and before any of $M_1$, and let $x$ be the number of $M_2$
vertices before that separator. Applying the exact closure formula at the lattice
state $(m,0,x)$ gives
$$
q_1(M_1)+\mathrm{pre}_1(M_2,x)\le A,\qquad
q_2(M_0)+\mathrm{suf}_2(M_2,m-x)\le B .
$$
The modules are themselves depth-5 face orders. Since $F_5=25$,
$$
q_1(M_1)\ge\left\lceil\frac{25}{B}\right\rceil,\qquad
q_2(M_0)\ge\left\lceil\frac{25}{A}\right\rceil,
$$
because $q_2(M_1)\le B$ and $q_1(M_0)\le A$. Hence every depth-6 face order with
caps $(1,A,B)$ forces a depth-5 $M_2$ with a simultaneous cut
$$
\mathrm{pre}_1(M_2,x)\le A-\left\lceil\frac{25}{B}\right\rceil,\qquad
\mathrm{suf}_2(M_2,m-x)\le B-\left\lceil\frac{25}{A}\right\rceil .
$$

This is a necessary condition for *any* face interleaving, not just for the
portfolio construction. The two-cut SAT scan of §30 is even more permissive than
this condition (one cut is the special case $s=t$), so its UNSAT results are valid
lower-bound certificates.

Now split the sub-$45$ cases:

- If $AB<25$, then the $M_2$ child itself would contradict $F_5=25$.
- If $A=1$ or $B=1$, the two-free-colours lemma (§11.10) forces the other face
  height at depth 6 to be $2^6=64$, so $AB<45$ is impossible.
- For $25\le AB<45$ and $A,B\ge2$, `data/two_cut_f6_scan.json` excludes every
  ordered target at the maximal boundary slack above: $52$ targets, $0$ SAT.

Therefore no depth-6 face order has $q_1q_2<45$, so $F_6\ge45$. The construction
from §29 gives $F_6\le45$ via $(1,5,9)$. Thus
$$
\boxed{F_6=45.}
$$
The certificate is implemented in `scripts/certify_F6_face_exact.py` and checked
by `tests/test_certify_F6_face_exact.py`.

This pins the face frontier one level farther, and tightens the global upper
bound to $L_6\le45$, but it does **not** settle the global value $L_6$:
$$
18=\vec\chi(B_6)\le L_6\le45=F_6.
$$
It also does not settle $\lambda$. The exact face sequence is now
$$
F_k=2,4,8,15,25,45\quad(k=1,\dots,6),
$$
with $F_6^{1/6}=1.886\ldots$ and $F_6/(3/2)^6=3.95\ldots$. As before, these six
points are compatible both with $\lambda_F=3/2$ plus a growing subexponential or
polynomial prefactor, and with $\lambda_F>3/2$. The next target remains
asymptotic: a direct lower bound or a closed-form infinite construction.
