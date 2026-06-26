# H25 — The two-copy split-sum identity for $C_3$-outer products

**Status: proved (structural theorem), human-checkable.** The identity below is a
sound combinatorial fact about *every* total order of $C_3[H]$. It was isolated by
the research engine (decision D44) as the salvaged sound leg of a refuted
"DSS-merge" proposal. H19 has since been refuted by the iterated directed-triangle
family (`docs/h19_refutation.md`), so the identity now describes exactly where its
proposed confinement fails. Computationally corroborated (see §6); the proof in §3
stands on its own.

---

## 1. Notation

We follow the notation of Aboulker–Aubian–Charbit–… *"Clique number of tournaments"*
(arXiv:2310.04265), abbreviated **[CNT]** below.

- $C_3$ is the **directed triangle** on $\{0,1,2\}$ with arcs $0\to1\to2\to0$.
  It is the cyclic triangle; it contains **no transitive triple**.
- For a tournament $H$, the **lexicographic substitution** $C_3[H]$ has vertex set
  $\{0,1,2\}\times V(H)$ and an arc
  $$(a,b)\to(a',b')\quad\Longleftrightarrow\quad \big(a\ne a'\text{ and } a\to a'\text{ in }C_3\big)\ \ \text{or}\ \ \big(a=a'\text{ and } b\to b'\text{ in }H\big).$$
  Write $V_a=\{a\}\times V(H)$ for the three **copies** ($a\in\{0,1,2\}$); each
  $C_3[H][V_a]\cong H$. Across copies the arcs follow $C_3$ wholesale:
  $V_a \Ra V_{a'}$ whenever $a\to a'$ in $C_3$.
- For a total order $\prec$ of a tournament $T$, the **backedge graph** $T^\prec$ is
  the undirected graph on $V(T)$ with edge $uv$ iff $u\prec v$ and $vu\in A(T)$
  (the arc is *backward*). The **clique number of $T$** is
  $$\diomega(T)\;=\;\min_{\prec}\ \omega(T^\prec)\qquad\text{([CNT], Def.\ of }\diomega).$$
  Throughout we abbreviate $\diomega$ as $\vec\omega$. (In the ledger this invariant
  is `omega_vec`; for a tournament $H$ we also write $\mathrm{ov}(H)=\vec\omega(H)$.)
- Fix a total order $\prec$ of $C_3[H]$ and enumerate its vertices
  $v_1\prec v_2\prec\cdots\prec v_N$, $N=3|V(H)|$. For a split position
  $p\in\{0,1,\dots,N\}$ put $P_{<p}=\{v_1,\dots,v_p\}$ and $P_{\ge p}=\{v_{p+1},\dots,v_N\}$.
- For a vertex subset $S$, let $\beta(S)=\omega\big((C_3[H])^\prec[S]\big)$ be the
  clique number of the backedge graph **induced on $S$** under $\prec$. For
  $S\subseteq V_a$ this is just the backedge clique number of $H$ under the order that
  $\prec$ induces on that copy.

---

## 2. The statement

> **Theorem (H25).** For every tournament $H$ and every total order $\prec$ of $C_3[H]$,
> $$\boxed{\;\omega\big((C_3[H])^\prec\big)\;=\;\max_{(Y,X)\,:\,X\to Y}\ \ \max_{0\le p\le N}\ \Big[\ \beta\big(V_Y\cap P_{<p}\big)\ +\ \beta\big(V_X\cap P_{\ge p}\big)\ \Big]\;}$$
> where the outer maximum is over the three ordered copy-pairs $(Y,X)$ for which $X\to Y$
> is an arc of $C_3$, namely $(Y,X)\in\{(1,0),(2,1),(0,2)\}$.

In words: the clique number of *any* ordering of $C_3[H]$ is exactly the best, over the
three cyclic copy-pairs and over a single split point, of "a backedge clique of the
*head* copy taken from a prefix" **plus** "a backedge clique of the *tail* copy taken
from the complementary suffix." The two pieces combine for free because every
prefix-head/suffix-tail cross pair is automatically a backedge.

---

## 3. Proof

The theorem is immediate from two lemmas.

### Lemma 1 (two-copy confinement)

*For every total order $\prec$ of $C_3[H]$, every clique of $(C_3[H])^\prec$ is contained
in the union of at most two of the copies $V_0,V_1,V_2$.*

**Proof.** First note how cross-copy pairs behave. Take $u\in V_a$, $v\in V_{a'}$ with
$a\ne a'$ and $u\prec v$. The pair $uv$ is a backedge edge iff $v\to u$, and across
copies $v\to u$ holds iff $a'\to a$ in $C_3$ — the $H$-coordinates are irrelevant. Thus:

> a cross-copy pair is a backedge edge **iff the $\prec$-later copy beats the $\prec$-earlier copy in $C_3$.** $(\star)$

Suppose a clique $K$ met all three copies, and pick $x_a\in K\cap V_a$ for $a=0,1,2$.
Order these three by $\prec$, say $x_{c_1}\prec x_{c_2}\prec x_{c_3}$ with $\{c_1,c_2,c_3\}=\{0,1,2\}$.
Since $K$ is a clique, all three pairs are backedge edges, so by $(\star)$ the later
copy beats the earlier in each pair:
$$c_3\to c_2,\qquad c_3\to c_1,\qquad c_2\to c_1\quad\text{in }C_3 .$$
That makes $c_1,c_2,c_3$ a **transitive triple** of $C_3$. But $C_3$ is the cyclic
triangle and has no transitive triple — contradiction. $\square$

### Lemma 2 (the cross part is a staircase)

*Let $X\to Y$ be an arc of $C_3$. For $y\in V_Y$ and $x\in V_X$, the pair $\{x,y\}$ is a
backedge edge iff $y\prec x$. Consequently a set $K\subseteq V_Y\cup V_X$ is a clique of
$(C_3[H])^\prec$ iff*
1. *$K\cap V_Y$ is a backedge clique (inside the $Y$-copy), and*
2. *$K\cap V_X$ is a backedge clique (inside the $X$-copy), and*
3. *every vertex of $K\cap V_Y$ precedes every vertex of $K\cap V_X$.*

**Proof.** Apply $(\star)$ to the pair $\{x,y\}$. If $y\prec x$ the later copy is $X$ and
$X\to Y$ holds, so it is an edge. If $x\prec y$ the later copy is $Y$ and we would need
$Y\to X$, which fails since $X\to Y$; so it is a non-edge. This proves the first claim,
and (3) is exactly the requirement that all cross pairs be edges; (1) and (2) are the
within-copy requirements. $\square$

### Proof of the Theorem

Write $R$ for the right-hand side.

**($\le$)** Let $K$ be a maximum clique, $|K|=\omega((C_3[H])^\prec)$. By Lemma 1 it lies
in some $V_Y\cup V_X$; relabel so that $X\to Y$ (one of the two copies is the head of the
$C_3$ arc). Let $p$ be the position just after the last $\prec$-element of $K\cap V_Y$
(take $p=0$ if $K\cap V_Y=\varnothing$). By Lemma 2(3) every vertex of $K\cap V_X$ comes
after every vertex of $K\cap V_Y$, hence after position $p$; so
$K\cap V_Y\subseteq V_Y\cap P_{<p}$ and $K\cap V_X\subseteq V_X\cap P_{\ge p}$. Therefore
$$|K| = |K\cap V_Y| + |K\cap V_X| \le \beta(V_Y\cap P_{<p}) + \beta(V_X\cap P_{\ge p}) \le R .$$

**($\ge$)** Fix any admissible pair $(Y,X)$ with $X\to Y$ and any split $p$. Let $A$ be a
maximum backedge clique of $V_Y\cap P_{<p}$ and $B$ a maximum backedge clique of
$V_X\cap P_{\ge p}$, so $|A|=\beta(V_Y\cap P_{<p})$ and $|B|=\beta(V_X\cap P_{\ge p})$.
Every $a\in A$ lies in $P_{<p}$ and every $b\in B$ in $P_{\ge p}$, so $a\prec b$; by
Lemma 2 the pair $ab$ is an edge. Since $A$ and $B$ are themselves cliques, $A\cup B$ is a
clique, of size $\beta(V_Y\cap P_{<p})+\beta(V_X\cap P_{\ge p})$. Hence
$\omega((C_3[H])^\prec)\ge$ this value; maximizing over $(Y,X)$ and $p$ gives
$\omega((C_3[H])^\prec)\ge R$. $\qquad\blacksquare$

**Remarks.**
- Single-copy cliques are the degenerate splits ($B=\varnothing$ or $A=\varnothing$), so
  the formula already dominates each $\beta(V_a)$.
- As $p$ increases, $\beta(V_Y\cap P_{<p})$ is non-decreasing and
  $\beta(V_X\cap P_{\ge p})$ non-increasing: each copy contributes a monotone **step
  profile**, and the identity reads off the best complementary prefix/suffix sum across
  the three cyclic pairs. This step-profile pair is the "interleaving signature" referred
  to in the ledger (H22), now made exact.

---

## 4. Consequence: an exact reformulation of $\vec\omega(C_3[H])$ and of H19

Minimizing the Theorem over all orders $\prec$:
$$\vec\omega\big(C_3[H]\big)\;=\;\min_{\prec}\ \max_{(Y,X):X\to Y}\ \max_{p}\Big[\beta(V_Y\cap P_{<p})+\beta(V_X\cap P_{\ge p})\Big]. \tag{$\dagger$}$$

The substitution **lower** bound (the "lex lower bound" proved in the ledger; with
$\vec\omega(C_3)=2$) gives
$$\vec\omega(C_3[H])\ \ge\ \vec\omega(C_3)+\vec\omega(H)-1\ =\ \vec\omega(H)+1 .$$

So the open **width-2 confinement conjecture**
$$\textbf{(H19)}\qquad \vec\omega(C_3[H])\ \le\ \vec\omega(H)+1\quad\text{whenever }\vec\omega(H)\ge 3$$
is, by $(\dagger)$, **equivalent** to the following existential statement:

> **(H19$'$)** For every tournament $H$ with $\vec\omega(H)=k\ge 3$ there exist total
> orders $\sigma_0,\sigma_1,\sigma_2$ of the three copies and an interleaving of them into
> one order $\prec$ of $C_3[H]$ such that **all three** cyclic-pair split-sums are
> $\le k+1$; i.e. for each $(Y,X)\in\{(1,0),(2,1),(0,2)\}$ and every split $p$,
> $$\beta(V_Y\cap P_{<p})+\beta(V_X\cap P_{\ge p})\ \le\ k+1 .$$

This is the precise residual obligation. H25 has reduced "control the clique number of a
57- or 75-vertex object" to "control three monotone step profiles and their interleaving."

---

## 5. Why a *uniform static* recipe cannot discharge H19$'$ (engine findings D42–D45)

The engine settled the natural first attempt — "use a single, statically chosen optimal
inner order in all three copies and merge by a fixed key" — in the **negative**, on the
only three proven inner-$\mathrm{ov}=4$ witnesses available
($H_1^\*$, $H_2^\*$ of order 25 — Aubian–Coulomb's $k=4$ inputs, P22 — and $\mathrm{QR}_{19}=\mathrm{Pal}(19)$, P15):

- For $C_3[H_1^\*],C_3[H_2^\*]$ (order 75) a **single shared** optimal inner order works:
  one $\sigma$ with copy step-profile $(4,4,5)$ realizes a clique-5 order; the cross-copy
  switches are $d$-monotone (a static-key merge produces exactly this shape).
- For $C_3[\mathrm{QR}_{19}]$ (order 57, $\vec\omega=5$ exactly, P23), the original
  clique-5 witness uses three distinct inner orders and genuine cross-copy cancellation.
  However, the capped shared-profile audit missed its rare copy-2 escaper:
  that one optimal order has $D=(3,4,5)$ and works when repeated in all three copies,
  giving a separate shared-order clique-5 construction. Thus D42–D45 killed the
  **static $(d,c,\mathrm{pos})$ merge rule** (all $49214$ tested sigmas overshoot), not
  arbitrary interleavings of one shared order.

Hence (D44/H22) the displayed gold witnesses are structurally incompatible with any
uniform static $d$-keyed merge. This does not imply that per-copy-distinct orders are
necessary: dynamic interleaving of a suitably chosen shared escaper can also work. The
remaining route to H19 is selection of suitable step profiles (full raisers or
cycle-breaking partners) followed by the H25 dynamic interleaving.

---

## 6. Computational corroboration

`scripts/ground_twocopy_identity.py` verifies, against the exact oracle
(`core.backedge_graph` / `core.clique_number`), both halves of the structural content:

1. the split-sum **formula equals** the directly computed backedge clique number, and
2. **no maximum clique meets all three copies** (Lemma 1),

on (a) the gold clique-5 witness order of $C_3[\mathrm{QR}_{19}]$
(`data/ground_h21_skeleton_sat.json`, order 57) and (b) $20$ random tournaments $H$ of
orders $4$–$7$, $10$ random orders of $C_3[H]$ each. Zero mismatches and zero three-copy
cliques were found. The split-sum profiles underlying H19$'$ are computed by the
$O(n^3)$ grid-reachability decision procedure `scripts/h25_path_feasibility.py`
(validated by controls: the $\vec\omega=2$ inner $H_7$ is infeasible at $3$; the
$\mathrm{QR}_{19}$ gold is feasible at $5$).

These are sanity checks; the identity itself is a theorem (§3) and does not rest on them.

---

## 7. Relation to prior work

[CNT] (arXiv:2310.04265) introduces $\diomega$, the backedge graph, the composition
$\Ra$, and the substitution operation, and proves that $\dic$-boundedness is preserved
under substitution together with the lower bound $\diomega(\tilde S_n)\ge n$. In the
source examined here I did **not** find an *exact* composition formula for
$\diomega(C_3[H])$ (the substitution results there are one-directional / boundedness
statements). H25 supplies such an exact identity for the $C_3$-outer case, and isolates
the finite object — the three step profiles — on which the substitution **upper** bound
$\vec\omega(C_3[H])\le\vec\omega(H)+1$ hinges.

> ⚠️ The project ledger refers to this as "the composition identity that [CNT]
> **Lemma 3.8** (lower-bound-only) is missing." I could not match a literal "Lemma 3.8"
> in the local source, so **the precise lemma number/attribution should be checked
> against the published version before citing** (per the project's citation-verification
> discipline). The mathematical content above is independent of that attribution.

---

## 8. Resolution: H19$'$ is false

The iterated family $B_0=TT_1$, $B_i=C_3[B_{i-1}]$ refutes H19 and hence H19$'$.
If H19$'$ held at every step, then
$\vec\omega(B_{23})\le24$. But
$pod(B_{23})\le3$ and
$\vec\chi(B_{23})=18206$ imply
$\vec\omega(B_{23})\ge\lceil18206^{1/3}\rceil=27$.
See `docs/h19_refutation.md` for the self-contained argument.

Thus for at least one $i\in\{3,\ldots,23\}$, every choice of inner orders and
interleaving has an H25 cyclic-pair split-sum exceeding
$\vec\omega(B_{i-1})+1$.
