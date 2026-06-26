# Growth of the iterated directed triangle and the critical-tournament questions

Let

$$
\widetilde S_1=TT_1,\qquad
\widetilde S_{n+1}=C_3[\widetilde S_n],
$$

and write

$$
w_n=\vec\omega(\widetilde S_n),\qquad
d_n=\vec\chi(\widetilde S_n).
$$

This note records what the H19 refutation actually changes, and what it does
not change, about Question 5.9 and Conjecture 5.10.

## 1. Exact dichromatic growth

The dichromatic numbers satisfy

$$
\boxed{d_1=1,\qquad d_{n+1}=\left\lceil\frac{3d_n}{2}\right\rceil.}
$$

For the lower bound, a colour can occur in at most two of the three top
copies: otherwise one vertex of that colour from each copy forms a directed
triangle. Counting colour-copy incidences gives
$3d_n\le2d_{n+1}$.

For the upper bound, put $q=d_n$.

- If $q=2s$, use three disjoint palettes of size $s$, one for each pair of
  top copies. Each copy receives the two pair-palettes incident with it.
- If $q=2s+1$, use pair-palettes of sizes $s+1,s,s$ and one additional
  colour in the copy incident with the two size-$s$ palettes.

Every global colour occurs in at most two top copies. Its union is acyclic
because the arcs between two copies all point in one direction. This uses
exactly $\lceil3q/2\rceil$ colours.

Consequently

$$
d_n=\Theta((3/2)^{n-1}),
$$

with initial values

$$
1,2,3,5,8,12,18,27,41,62,\ldots.
$$

## 2. Current bounds for clique number

The original first-vertex argument gives

$$
w_{n+1}\ge w_n+1,
$$

and hence $w_n\ge n$. The partial-order-decomposition theorem gives

$$
d_n\le w_n^3,
$$

because $pod(\widetilde S_n)=3$ for $n\ge2$. The upper bound $3$ is preserved
by substitution; the lower bound holds
because $\widetilde S_n$ contains a directed triangle, whose three arcs
cannot be covered by fewer than three transitive digraphs. Therefore

$$
\boxed{
\max\{n,\lceil d_n^{1/3}\rceil\}
\le w_n\le d_n.
}
$$

Asymptotically this is

$$
(3/2)^{(n-1)/3+o(n)}
\le w_n\le
5^{(n-1)/4+o(n)}.
$$

In terms of $N=3^{n-1}$ vertices,

$$
N^{0.12302\ldots+o(1)}
\le w_n\le
N^{0.36624\ldots+o(1)}.
$$

The known exact values are

$$
w_1=1,\quad w_2=2,\quad w_3=3,\quad w_4=4,\quad \boxed{w_5=5}.
$$

$w_5=5$ is now **proved** by exact no-$K_6$ SAT on $\widetilde S_5$ (order 81): the
no-$K_6$ linear-ordering CNF is SAT on both Cadical153 and Minisat22, and the reconstructed
order has backedge clique $5$ (independently checked by `core.omega_of_order`); the proven
lower bound $w_5\ge5$ pins it. Reproduce: `scripts/decide_w5_stilde.py` (29.9M transitive
6-chains, ~14s). Consequence via §3 (submultiplicativity / Fekete inf):
$$
\rho\;\le\;w_5^{1/4}\;=\;5^{1/4}\;\approx\;1.49535\;<\;\tfrac32 .
$$
So the growth constant is $\rho\in[(3/2)^{1/3},\,5^{1/4}]\approx[1.1447,\,1.4953]$ — the
strict bound $\rho<3/2$ is now established. Note $w_n=n$ for all $n\le5$, so H19 holds at
every small level; in particular $\widetilde S_4$ is **not** an H19 counterexample (the
failure is genuinely further out, before level 24 by the exact $d_{24}=18206$ bound).

## 3. A genuine exponential growth constant

Put $B_i=\widetilde S_{i+1}$. Lexicographic associativity gives

$$
B_{i+j}\cong B_i[B_j].
$$

For arbitrary tournaments $T,H$, order optimal copies of $H$ contiguously in
an optimal order of $T$. A backedge clique meets at most
$\vec\omega(T)$ blocks and at most $\vec\omega(H)$ vertices in each block, so

$$
\vec\omega(T[H])\le\vec\omega(T)\vec\omega(H).
$$

Thus $b_i=\vec\omega(B_i)$ is submultiplicative:

$$
b_{i+j}\le b_i b_j.
$$

Fekete's lemma applied to $\log b_i$ proves that the limit

$$
\rho=\lim_{i\to\infty}b_i^{1/i}
$$

exists, and

$$
\boxed{(3/2)^{1/3}\le\rho\le5^{1/4}.}
$$

Equivalently, the polynomial exponent

$$
\alpha=\lim_{n\to\infty}
\frac{\log w_n}{\log |V(\widetilde S_n)|}
=\log_3\rho
$$

exists and lies in

$$
0.12302\ldots\le\alpha\le0.36624\ldots.
$$

A finite exact value can improve the upper base: any certificate
$w_m\le u$ gives

$$
\rho\le u^{1/(m-1)}.
$$

The exact value $w_5=5$ gives
$\rho\le5^{1/4}=1.49535\ldots<3/2$.

## 4. Exact transitive-subtournament counting

Let

$$
F_n(x)=\sum_r t_{n,r}x^r,
$$

where $t_{n,r}$ is the number of transitive $r$-vertex subtournaments of
$\widetilde S_n$, including the empty set. A transitive set meets at most two
top copies, and arbitrary transitive sets in two copies combine transitively.
Hence

$$
\boxed{
F_1(x)=1+x,\qquad
F_{n+1}(x)=3F_n(x)^2-3F_n(x)+1.
}
$$

For a uniformly random vertex order, a fixed transitive $r$-set is a
backedge clique with probability $1/r!$. Therefore

$$
t_{n,r}<r!
\quad\Longrightarrow\quad
w_n\le r-1.
$$

This exact recurrence gives a clean route for studying random-order and
entropy constructions. On the computed levels it does not beat the
dichromatic upper bound, so an upper-exponent improvement likely needs a
structured order rather than an unconditioned random order.

## 5. Consequence for H19

If H19 held at every step of the tower, the exact values
$w_3=3$ and the recursion would give $w_n\le n$ for all $n\ge3$.
But

$$
d_{24}=18206,\qquad
w_{24}\ge\lceil18206^{1/3}\rceil=27>24.
$$

Thus H19 fails at some step

$$
C_3[\widetilde S_j]=\widetilde S_{j+1},
\qquad 3\le j\le23.
$$

The argument does not locate the first failure. Since $w_5=5$, H19 holds
through that level. The first open step is whether $w_6=6$.

## 6. Question 5.9 and Conjecture 5.10

For a fixed $k$, every tournament of clique number at least $k$ contains an
inclusion-minimal induced subtournament $K$ of clique number at least $k$.
Subadditivity across $V(K-v)\cup\{v\}$ shows

$$
\vec\omega(K)=k,\qquad
\vec\omega(K-v)=k-1
$$

for every vertex $v$. Thus $K$ is $k$-$\vec\omega$-critical.

It follows that, for each fixed $k$, the following are equivalent:

1. there is a bounded-size certificate at threshold exactly $k$;
2. $k$-critical tournaments have bounded order;
3. there are only finitely many $k$-critical tournaments up to isomorphism.

The repository's infinite critical families at $k=3,4,5$ therefore answer
Question 5.9 negatively already at each of those thresholds. Globally,
Question 5.9 is already answered **no**.

Conjecture 5.10 is stronger: it asserts infinitely many $k$-critical
tournaments for every $k\ge3$. It is proved here for $k=3,4,5$ and remains
open for $k\ge6$.

The tower does not settle that issue:

- Since $w_n\ge n$, it guarantees at least one $k$-critical induced
  subtournament for every $k$.
- Its nesting also gives a fixed bounded witness $\widetilde S_k$ inside every
  later tower member, so the tower itself is not a source of unbounded
  minimal certificates at fixed $k$.
- Infinitely many H19-violating steps occur at increasing clique levels; that
  does not produce infinitely many critical tournaments at one fixed level.

The February 2026 paper *Characterizing Large Clique Number in Tournaments*
proves the weaker non-identity statement: sufficiently large clique number
$f(k)$ forces a bounded $k$-certificate. It confirms Conjecture 5.8, not
Question 5.9, and is compatible with infinite critical families at fixed
small $k$.

So the H19 refutation changes the **construction program**, not the logical
status of Question 5.9 or Conjecture 5.10. It kills the proposed uniform
value-lifting lemma for a $k=6$ family; a new criticality construction remains
necessary.

## 7. The growth constant $\rho$ and the computational frontier

Combining §1–§3: the limit $\rho=\lim_n w_n^{1/(n-1)}$ exists (submultiplicativity
$\vec\omega(A[B])\le\vec\omega(A)\vec\omega(B)$ + $\widetilde S_{i+j-1}=\widetilde S_i[\widetilde S_j]$ + Fekete, so $\rho=\inf_n w_n^{1/(n-1)}$) and
$$\boxed{\ \rho\in[(3/2)^{1/3},\,5^{1/4}]\approx[1.1447,\,1.4953].\ }$$
Upper from $w_5=5$; lower from $d_n\le w_n^3$ with $d_n\sim(3/2)^n$. **Exactly known:
$w_n=n$ for $n\le5$** (all by no-$K_{n+1}$ SAT); additivity holds at every small level.

**The first unknown value is $n=6$.** $w_6=\vec\omega(\widetilde S_6)$ (order 243, known
$\in[6,9]$) is past every exact method tried (2026-06-12):
- direct no-$K_7$ SAT: $>1.2\times10^8$ transitive 7-chains, CNF infeasible;
- lazy CEGAR: does not converge — unconstrained orders sit at clique $\sim27$, so
  forbidding 7-cliques one at a time never bites;
- single *shared*-order interleaving overestimates: it yields $c_4=5$ though $w_4=4$,
  and $c_6=9$–$13$ — so it cannot certify $w_6$;
- local search fails even with a fast bitset max-clique (`scripts/fast_clique.py`,
  ~3500$\times$ faster than the networkx oracle on a specific order, verified). Rejecting
  a clique-raising move is cheap (early-exit once a $(K{+}1)$-clique is found), but every
  ACCEPTED move that keeps the clique at $K$ requires a near-full search to *verify*
  $\max=K$ on the dense order-243 backedge graph — intrinsically slow — so the descent
  does not converge to a useful $w_6$ bound. (Had it reached clique 6 it would give
  $\rho\le6^{1/5}=1.431$; clique 7 gives $7^{1/5}=1.476$.)

So **pinning $\rho$ is now a theoretical problem**, not a computational one. The crux:
does $\vec\omega(\widetilde S_n)$ grow like $d_n^{1/3}\sim(3/2)^{n/3}$ (i.e. the $pod=3$
bound is asymptotically tight, giving $\rho=(3/2)^{1/3}$), or strictly faster?

The pod-tightness question has now been reduced more sharply.  The three
canonical first-difference posets define layer heights $q_0,q_1,q_2$ for
every order of $B_k=\widetilde S_{k+1}$.  If $Q=q_0q_1q_2$, $M$ is the number of occupied rank triples,
and $K$ is the full backedge clique, then
$$
\frac{K^3}{(3/2)^k}
=\frac{K^3}{Q}\frac{Q}{M}\frac{M2^k}{3^k}.
$$
All factors are at least one.  Thus tightness requires a simultaneous
near-minimization of the canonical layer volume $Q$ and the full mixed-colour
clique $K$.

Writing $L_k=\min Q$, exact SAT gives
$$
L_1=2,\quad L_2=4,\quad L_3=8,\quad L_4=15.
$$
The sequence is submultiplicative, so
$\lambda=\lim L_k^{1/k}$ exists and $\rho^3\ge\lambda\ge3/2$.
Proving $\lambda>3/2$ is now the cleanest strict-growth target.  At depth
$4$, a minimum-volume order has $(q_0,q_1,q_2)=(1,3,5)$ but full clique
$11$, whereas a certified width-$5$ order has $(5,5,5)$.  This finite
Pareto separation explains why optimizing either statistic alone is
insufficient.

See `docs/stilde_pod_tightness.md` and
`scripts/decide_stilde_layer_product.py`.

### Remaining targets
1. Decide $w_6$ (additivity at $n=6$?) — needs a fast max-clique / symmetry-reduced
   $\vec\omega$ solver at order 243, or a structural argument.
2. Prove a canonical layer-volume gap $\lambda>3/2$, or construct orders with
   $L_k=(3/2)^{k+o(k)}$.
3. Self-similar order construction with per-level growth $<3/2$ would lower the upper
   exponent below $5^{1/4}$.
4. Criticality (separate from $\rho$): classify minimal $k$-cores inside $\widetilde S_n$,
   tracking whether their orders stabilize or grow with $n$ (bears on Conjecture 5.10).

Numerical tables generated by `scripts/stilde_growth_bounds.py`; $w_5$ by
`scripts/decide_w5_stilde.py`.
