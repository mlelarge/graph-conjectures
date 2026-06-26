# A cancellation-argument sketch for the H19 value leg

**Status: historical research program — H19 is refuted.** The iterated
directed-triangle family $B_i=C_3[B_{i-1}]$ contradicts the proposed bound by
$i=23$: H19 would give $\vec\omega(B_{23})\le24$, while the exact
dichromatic recurrence and partial-order-decomposition theorem give
$\vec\omega(B_{23})\ge\lceil18206^{1/3}\rceil=27$. See
`docs/h19_refutation.md` for the proof. The Route-2 selection conjectures below
therefore cannot hold uniformly, though the proved H25 identity and the finite
object calculations remain valid.

This note proposed a route to the then-open width-2 confinement bound
$$\textbf{(H19)}\qquad \vec\omega(C_3[H])\le \vec\omega(H)+1\quad(\vec\omega(H)=k\ge 3),$$
building on the **proved** H25 split-sum identity (`docs/h25_split_sum_identity.md`).
Pieces are tagged **[proved]**, **[provable]** (clean, expected routine), or
**[open]** according to their historical status. The failed uniform scheduling
lemma is now known to be false.

Notation as in the H25 note: $m=|V(H)|$; copies $V_0,V_1,V_2$ of $C_3[H]$; cyclic
pairs $(Y,X)\in\{(1,0),(2,1),(0,2)\}$ (arc $X\to Y$ in $C_3$); $\beta(\cdot)$ the
induced backedge clique number.

---

## 1. H19 as a lattice-path scheduling problem  [proved reduction]

Fix an inner order $\sigma_c$ for each copy $c$ and record its **prefix** and
**suffix** backedge-clique step profiles
$$f_c(a)=\omega\!\big(H^{\sigma_c}[\text{first }a]\big),\qquad
  g_c(b)=\omega\!\big(H^{\sigma_c}[\text{last }b]\big),\qquad a,b\in\{0,\dots,m\}.$$
Both are non-decreasing, $f_c(0)=g_c(0)=0$, and $f_c(m)=g_c(m)=\omega(H^{\sigma_c})$,
which is $=k$ for an **optimal** inner order and $\ge k$ always.

An interleaving $\prec$ of the three copies is exactly a **monotone lattice path**
$(j_0,j_1,j_2):(0,0,0)\rightsquigarrow(m,m,m)$ in $\{0,\dots,m\}^3$ that increments one
coordinate per step ($j_c=$ number of copy-$c$ vertices before the current split).
By the H25 identity, $\omega((C_3[H])^\prec)\le k+1$ **iff** at every point of the path
$$f_1(j_1)+g_0(m-j_0)\le k{+}1,\quad
  f_2(j_2)+g_1(m-j_1)\le k{+}1,\quad
  f_0(j_0)+g_2(m-j_2)\le k{+}1. \tag{C}$$
So **H19 $\iff$** for every $H$ ($k\ge3$) there exist inner orders
$\sigma_0,\sigma_1,\sigma_2$ and a monotone path satisfying (C) throughout. (The
endpoint forces each $\omega(H^{\sigma_c})\le k+1$. One might hope to restrict to
**optimal** inner orders $\omega(H^{\sigma_c})=k$ — the search space of
`scripts/h25_path_feasibility.py` and of the §8–§11 escaper analysis — but this is **NOT**
WLOG: the SAT-verified clique-5 witness for $C_3[\mathrm{AC}_7[C_3]]$ uses a
width-$(k{+}1)=5$ inner order in one copy, §13. So the optimal-order program is
sufficient-not-complete; some $H$ need a non-optimal inner order.) The reachability script
decides the optimal-order version (monotone grid-reachability avoiding the three "bad sets"
$f_Y(a)+g_X(m-c)\ge k{+}2$).

**The fundamental tension [proved].** For one optimal order, cutting a maximum
clique $K$ ($|K|=k$) at position $j$ splits it into a prefix-clique and a suffix-clique,
so
$$f_\sigma(j)+g_\sigma(m-j)\ \ge\ k\qquad\text{for all }j. \tag{$\ast$}$$
The same-order prefix and complementary suffix can never *both* be small — this is why
the bound is $k+1$, not $k$, and is the entire difficulty.

---

## 2. The easy regime: a single *tight* order  [provable]

Call an optimal order $\sigma$ of $H$ **tight** if it meets ($\ast$) with one unit of
slack:
$$f_\sigma(j)+g_\sigma(m-j)\le k+1\qquad\text{for all }j$$
(equivalently the sum is always $k$ or $k+1$: the prefix clique and complementary
suffix clique never *both* spike).

> **Proposition (single-order cancellation).** If $H$ has a tight order $\sigma$, then
> the **lockstep round-robin** interleaving of three copies of $\sigma$ satisfies (C),
> hence $\vec\omega(C_3[H])\le k+1$.

*Why.* Drive the path through the diagonal $j_0=j_1=j_2$ (advance $0,1,2,0,1,2,\dots$),
so the three coordinates differ by at most one. At a diagonal point $j_0=j_1=j_2=j$ each
constraint in (C) is $f_\sigma(j)+g_\sigma(m-j)\le k+1$ — exactly tightness. The only
care is the **cyclic seam**: in each round one pair momentarily has its head one step
ahead of its tail. Routing each round so the tail of the seam pair advances *before* its
head removes two of the three seams; the third, cyclic, seam lands where the implicated
copy is at a diagonal point and is absorbed by the unit of slack in tightness. (Making
this seam bookkeeping fully rigorous is the **[provable]** part; the diagonal points
carry the real content.)

This explains the order-75 witnesses $C_3[H_1^\*],C_3[H_2^\*]$: each uses **one shared**
optimal inner order — they have a tight order, and lockstep does the rest.

---

## 3. The hard mechanism: genuine cancellation can occur  [open]

The original order-57 $\mathrm{QR}_{19}$ gold witness demonstrates genuine
cross-copy cancellation: it uses three distinct optimal orders, two with internal
split-sum $6=k+2$, while every cross sum stays at most $5=k+1$. This proves that a
successful construction may pair locally over-budget profiles and rescue them
dynamically.

It does **not** prove that cancellation or distinct orders are necessary for
$\mathrm{QR}_{19}$. The later Route-2 audit (§12) found that the gold witness's copy-2
order is itself a tight full raiser with $D=(3,4,5)$; repeating that one order in all
three copies is cycle-free and gives another clique-5 construction. The hard regime
therefore remains a possible mechanism, not a required normal form.

### 3.1 The cancellation mechanism: rotating phases

Concentrate each copy's clique growth. For an order $\sigma$, its prefix profile climbs
$0\to k$; call the position interval where $f_\sigma$ crosses from $\le k-1$ to $k$ its
**ramp** $R(\sigma)\subseteq[0,m]$ (and symmetrically a suffix ramp). A cross constraint
$f_Y(j_Y)+g_X(m-j_X)\le k+1$ is in danger only when **both** the head $Y$ is on its
prefix ramp *and* the tail $X$ is still before its suffix ramp (suffix clique still near
$k$). Choose the three orders so their ramps are **staggered** at phases
$\approx 0,\tfrac{m}{3},\tfrac{2m}{3}$, and route the path as a **rotating leader**: at
each phase exactly one copy is "crossing," and the path advances that copy through its
ramp while the other two sit at ramp-free heights (one already past — small suffix; one
not yet started — small prefix). Cyclicity, fatal for a *static* assignment, is now an
*asset*: there are three pairs and three phases, and a rotation matches them so each pair
is loaded in only one disjoint window.

Cancellation, precisely: a copy may violate ($\ast$)-with-slack *internally*
($f+g=k+2$), but in (C) its prefix is paired with a **different** copy's suffix; if that
partner has already crossed (suffix $\le 1$ below $k$) the cross sum is back to $\le k+1$.

### 3.2 The proposed scheduling lemma  [refuted]

> **Schedulability Conjecture (refuted).** For every $H$ with $\vec\omega(H)=k\ge3$ there is an
> ordered triple of optimal inner orders whose prefix/suffix ramps admit a monotone
> rotating path satisfying (C). Equivalently: the three "bad sets"
> $B_{YX}=\{f_Y(a)+g_X(m-c)\ge k+2\}$ do not jointly block monotone $(0,0,0)\to(m,m,m)$
> reachability for some optimal-order triple.

This was the open content of the program. The iterated directed-triangle
refutation proves that the statement is false.

---

## 4. Historical candidate routes to the Schedulability Conjecture

1. **Interval-scheduling / Hall-type [combinatorial].** Model each copy by its ramp
   interval; (C) fails only on overlaps of a head-ramp with a not-yet-crossed tail.
   Show the ramps of three optimal orders can be rotated so the three obstruction
   windows are pairwise disjoint — a defect/Hall condition on ramp widths. *Risk:* a
   single order's ramp could be wide (clique builds slowly), so width $<m/3$ is not free;
   one likely needs to *choose* orders minimizing ramp width (an inner optimization).

2. **Amortized potential along the path [analytic].** Define a potential
   $\Phi=\sum_{(Y,X)}\big(f_Y(j_Y)+g_X(m-j_X)\big)$ and bound its **maximum** (not sum)
   along a greedy path that always advances the coordinate reducing the current binding
   constraint. A discharging argument that each unit of $f_Y$ increase is matched by a
   $g_X$ decrease at the partner would cap the max cross sum at $k+1$. This is the direct
   descendant of the potential-sum bookkeeping that proved the $k=4,5$ cases (P16, P20),
   now made *dynamic* (the static version is dead, H21/H22).

3. **Probabilistic / second-moment [averaging].** Take three *independent uniformly
   random* optimal orders and a uniformly random rotation phase; bound
   $\mathbb E[\max_{(Y,X),p}(f_Y+g_X)]$, or show
   $\Pr[\text{some }(C)\text{ violated}]<1$. The lower-tension ($\ast$) gives the mean
   $\approx k$; concentration of the ramp position around its phase would give the
   max $\le k+1$ whp. This is the "second-moment" route named in the handback; it would
   prove H19 **non-constructively**. *Risk:* optimal orders of a fixed $H$ are highly
   correlated/atypical (the G62 finding: a uniform random interleave hit the gold target
   with probability $0/800$), so the averaging must be over *optimal* orders, not all
   orders, and may need anti-concentration input specific to $\vec\omega$.

---

## 5. Falsifiable checkpoints (engine-testable, foreground-feasible)

The sketch makes sharp finite predictions; each is a single bounded oracle scan
(`h25_path_feasibility.py` already implements the core check):

- **C1.** *Every* tournament with $\vec\omega=3$ (exhaustive $n\le 9$ census) admits a
  feasible optimal-order triple at bound $4$. **[expected PASS — already the basis of
  H19 at $k=3$; re-confirms reduction.]**
- **C2.** Among $\{H_1^\*,H_2^\*,\mathrm{QR}_{19}\}$: $H_1^\*,H_2^\*$ feasible with **one**
  shared (tight) order; $\mathrm{QR}_{19}$ feasible only with **three** staggered orders.
  **[PASS = the D45 data; this is the model's anchor.]**
- **C3 (the discriminator).** The three feasible orders for $\mathrm{QR}_{19}$ have
  **ramps at staggered phases** ($\approx0,m/3,2m/3$) and the witnessing path is a
  **rotating leader**. If instead the gold path is *not* rotation-structured, route (1)/(3)
  weaken and route (2) (potential) is favored.
- **C4 (potential test).** Along the greedy "reduce-the-binding-constraint" path on each
  proven object, does the running max cross sum stay $\le k+1$? A single counterexample
  kills route (2) as stated.
- **C5 (falsify the whole program).** Find any $H$ ($k\ge3$) for which **no** optimal-order
  triple is path-feasible at $k+1$. This would **refute H19 itself** (not just the
  sketch), since the reduction in §1 is an iff. None found to date; this is the highest-
  value scan to push offline to inner order $\ge 19$.

---

## 6. Honest assessment

- **Solid:** the §1 reduction is a theorem (via H25); the §2 single-order regime is
  essentially a proof and covers all currently-known *easy* cases; the difficulty is
  isolated to one clean statement (Schedulability Conjecture).
- **Resolution:** §3.2 is false uniformly over $H$; the iterated directed-triangle
  family defeats every proposed route.
- **Historical next step:** checkpoint **C3** on $\mathrm{QR}_{19}$ was used to choose
  among routes (1)/(2)/(3). **Result below.**

---

## 7. Checkpoint C3 — result on the $\mathrm{QR}_{19}$ gold path

Ran `scripts/c3_gold_path_analysis.py` (analysis of the verified order-57 gold witness
against H25; foreground). Findings:

- **(i) Three distinct optimal inner orders in this witness [confirmed].** The three copies use three
  *different* permutations of $\mathrm{QR}_{19}$, each with full inner backedge clique
  $=4=k$ (optimal-inner). This describes the SAT-found witness only; §12 later finds a
  separate shared-order solution.
- **(i$'$) Cancellation is genuinely used [confirmed — the key point].** Internal
  split-sums $\max_a[f_c(a)+g_c(m-a)]$ are **6, 6, 5** for copies $0,1,2$: two of the
  three copies exceed the tight budget $k+1=5$ *internally*, yet **every cross-sum stays
  $\le 5$** (max H25 value along the path $=5$, zero points over budget). This is exactly
  the §3 hard mechanism — local over-budget cancelled by cross-copy pairing. Copy 2 is
  tight; copies 0 and 1 are not.
- **(ii) Staggered ramps [partial].** Copies reach full clique $k$ at positions
  $a=9,16,19$ (fractions $0.47,0.84,1.0$), spread $0.53\,m$ — genuinely staggered, but
  **back-loaded**, not the idealized $0,\tfrac13,\tfrac23$. The clean "phases at thirds"
  picture of route (1) is only loosely borne out.
- **(iii) Rotating leader [confirmed, strongly].** The binding cyclic pair sequence along
  the path is
  $$(0,2)\to(1,0)\to(2,1)\to(1,0)\to(2,1)\to(1,0)\to(2,1)\to(1,0)\to(2,1),$$
  hitting all $3/3$ cyclic pairs and then **alternating** between them. Moreover, when a
  pair $(Y,X)$ is at budget, the path advances the **head $Y$ only in the minority** of
  steps (e.g. $5/21$): it preferentially advances the *tail* $X$ (or the third copy),
  which lowers $g_X(m-j_X)$ and **relieves the binding constraint**.

**Interpretation.** The gold path is a rotating-leader schedule driven by *binding-
constraint relief*, not by clean ramp-thirds. This **favors route (2)** (amortized
potential / greedy "advance to relieve the binding pair") over the pure interval-
scheduling route (1): the data shows an explicit greedy relief dynamic. Route (1)'s
staggering is present but irregular, so a Hall-type width argument would need slack.
Route (3) remains open and untouched by this test.

---

## 8. Route (2) sharpened: the credit / no-deadlock formulation

Replace the global potential $\Phi$ by a local **credit** account (one per arc) and a
**deadlock-freedom** target. With
$$r_c(j)\ :=\ k-g_c(m-j)\qquad(\text{non-decreasing},\ 0\to k\text{ as }j:0\to m),$$
each cross constraint $f_Y(j_Y)+g_X(m-j_X)\le k+1$ becomes $f_Y(j_Y)-r_X(j_X)\le 1$, i.e.
the **credit on arc $X\to Y$**
$$\mathrm{cred}_{(Y,X)}\ :=\ 1+r_X(j_X)-f_Y(j_Y)\ \ge\ 0$$
is exactly the (un-violated) constraint. A unit step in copy $c$: **consumes** one
incoming credit when $f_c$ rises ($c$ is the head of pair $(c,\mathrm{pred}\,c)$),
**creates** one outgoing credit when $r_c$ rises ($c$ is the tail of pair
$(\mathrm{succ}\,c,c)$), and is otherwise free. A state is **safe** iff all three credits
$\ge 0$ (= "not bad"); a **legal move** advances some copy to a safe state; a
**dead-end** is a reachable safe non-terminal state with no legal move.

> **Target (No-Deadlock Lemma).** Choose three inner orders so that **no reachable safe
> state is a dead end.** Then any greedy legal-step run strictly increases $j_0+j_1+j_2$
> and must reach $(m,m,m)$, so $\vec\omega(C_3[H])\le k+1$ — no global potential needed.

This is strictly cleaner than bounding $\Phi$: it localizes the obligation to **ruling
out a cyclic three-way deadlock**.

### 8.1 The deadlock certificate is the pure cyclic wait  [computed]

`scripts/route2_credit_deadlock.py` builds the safe-state graph for a profile triple and
records minimal dead-ends. On $C_3[\mathrm{QR}_{19}]$:

- **Gold triple [feasible, robust].** $632$ safe states, **all $632$ reachable**,
  **$0$ dead-ends** — `FEASIBLE_NO_DEADLOCK = True`. Once the three gold profiles are
  fixed, *every* greedy tie-break wins; navigation is free.
- **Common enumerated shared orders [deadlock diagonally].** Every shared profile in the
  capped audit fails at a diagonal state $(j,j,j)$ where all three credits are $0$.
  This is a real obstruction for non-escaping shared maps, but it is not universal:
  the rare gold copy-2 profile escapes at every level and works when repeated (§12).

### 8.2 Audit of "$\mathrm{QR}_{19}$ needs three distinct orders"  [refuted]

The capped enumeration initially suggested that no shared order works:

| shared single order, by true width | enumerated | terminal-reachable |
|---|---|---|
| width $4$ (optimal) | $1222$ | $0$ |
| width $5$ ($=k+1$) | $2778$ | $0$ |

That inference was false because the profile enumeration was capped and missed the rare
gold escaper. Repeating the gold copy-2 optimal order, whose map is
$D=(3,4,5)$, gives **one shared order** with no cyclic wait: $2642$ safe states, all
$2642$ reachable, zero dead-ends. The explicit greedy interleaving has backedge clique
$5$, independently verified by `core.omega_of_order`.

Correct conclusion: the SAT-found witness uses three distinct orders, but the minimum
number of distinct inner orders for $\mathrm{QR}_{19}$ is **one**. The capped
$0/1222$ and $0/2778$ figures measure how rare the useful shared profile is; they do not
exclude it.

> **Bug fixed (2026-06-12).** `h25_path_feasibility.py:optimal_profiles` recorded a
> completed order without checking its full clique $=k$, silently emitting width-$(k+1)$
> orders as "optimal" (the DFS prunes proper prefixes $>k$, but a full order can first hit
> $k+1$ on its last vertex). Patched to filter on $f[m]=k$; the gold control is unchanged
> ($632/632/0$). Earlier engine `min_distinct`/`feasible_H` figures were over a mislabeled
> mix and should be read as width-$\le k{+}1$, not optimal; the SAT-verified value
> $\vec\omega(C_3[\mathrm{QR}_{19}])=5$ (P23) is independent and stands.

### 8.3 The historical crux, restated as deadlock-avoidance

> **Selection Conjecture (Route 2 form; refuted).** For every $H$ with $\vec\omega(H)=k\ge3$ there
> is a triple of optimal inner orders whose profiles admit **no reachable cyclic-diagonal
> deadlock** (equivalently: the three "bad sets" leave a dead-end-free monotone route).

Within this program, the gold data said navigation was free *given* good profiles; the
difficulty was producing the triple. **Historical data limitation:** the cancellation regime (inner-$\mathrm{ov}\ge4$)
has exactly **one** witness, $\mathrm{QR}_{19}$ — the $k=3$ layer is degenerate (tight
shared orders exist) and the next generic inner-$\mathrm{ov}\ge4$ objects start past the
census wall at order $19$. So extracting a *uniform* selection criterion is data-starved:
it needs either offline generation of more inner-$\mathrm{ov}\ge4$ witnesses, or a
structural argument that the symmetry-breaking the gold triple exhibits is always
available.

### 8.4 Candidate criterion: cycle-free demand/relief maps

The credit equations compress the deadlock question from the full
$(m+1)^3$ lattice to at most $k-1$ events per inner order. For an optimal order
$\sigma$, let $d_\sigma(t)$ be the unique position just before its prefix profile rises
from $t-1$ to $t$, for $2\le t\le k$. Define the **demand/relief map**
$$D_\sigma(t)\ :=\ 2+r_\sigma\!\left(d_\sigma(t)\right).$$
Values outside $\{2,\dots,k\}$ are allowed; they simply leave the possible demand-level
range.

> **Lemma (cyclic-wait characterization) [proved].** For three optimal profiles
> $\sigma_0,\sigma_1,\sigma_2$, a safe non-terminal state is a dead-end iff it is
> $$\bigl(d_{\sigma_0}(t_0),d_{\sigma_1}(t_1),d_{\sigma_2}(t_2)\bigr)$$
> for levels satisfying
> $$t_1=D_{\sigma_0}(t_0),\qquad
>   t_2=D_{\sigma_1}(t_1),\qquad
>   t_0=D_{\sigma_2}(t_2). \tag{DR}$$

Indeed, advancing copy $c$ can fail only when its prefix clique is about to rise and
its incoming credit is zero. If all three moves fail, these two conditions hold
cyclically and give (DR). Conversely, (DR) makes all three credits zero at the stated
demand positions, and every move consumes one of them. A non-terminal dead-end cannot
have a finished copy: a finished tail has relief $k$, giving its successor strictly
positive incoming credit.

Thus the strongest witness-supported selection criterion is not merely "spread the
full-clique ramps." It is:

> **Demand/Relief Cycle-Breaking Conjecture (refuted).** For every tournament $H$ with
> $\vec\omega(H)=k\ge3$, there exist three optimal orders
> $\sigma_0,\sigma_1,\sigma_2$ such that (DR) has no solution in
> $\{2,\dots,k\}^3$. Equivalently, the partial composition
> $D_{\sigma_2}\circ D_{\sigma_1}\circ D_{\sigma_0}$ has no fixed point whose two
> intermediate values remain in $\{2,\dots,k\}$.

This conjecture is stronger than the Selection Conjecture in §8.3: it excludes **all**
safe dead-ends, including unreachable ones. If true, it implies the No-Deadlock Lemma
and hence H19.

For the $\mathrm{QR}_{19}$ gold triple ($k=4$), the maps on levels $2,3,4$ are
$$D_0=(2,3,3),\qquad D_1=(2,4,4),\qquad D_2=(3,4,5),$$
so the cyclic composition has no admissible fixed point. By contrast, shared-order
triples have a common fixed demand level, producing the observed diagonal triple-zero.
In an independent check of $1300$ enumerated optimal profiles, $t=2$ was fixed in every
shared map; the broader capped audit in §8.2 found the same diagonal deadlock signature.
This exactly captures the gold witness's useful "staggering": not geometric spacing by
itself, but **incompatible demand/relief levels around the directed cycle**.

`scripts/route2_credit_deadlock.py` now computes these maps and verifies that their
cyclic-wait states equal the safe dead-ends found by the full lattice checker. The
criterion is precise and falsifiable, but its universal quantifier remains supported by
only the single cancellation-regime witness $\mathrm{QR}_{19}$.

---

## 10. The monotone fixed-point obstruction — why an *escaper* is necessary  [proved + verified]

The demand-relief maps have a property that turns the cycle-breaking criterion from a
search into a structural requirement.

**Each $D_\sigma$ is non-decreasing.** $D_\sigma(t)=2+r_\sigma(d_\sigma(t))$ with
$r_\sigma(j)=k-g_\sigma(m-j)$; both the demand position $d_\sigma(t)$ and the relief
$r_\sigma$ are non-decreasing in $t$, so $D_\sigma$ is non-decreasing (verified: all
sampled optimal profiles). Call $\sigma$ an **escaper** if $D_\sigma(t)>k$ for some $t$
(its demand pushes a successor level above $k$).

> **Escaper Necessity (theorem).** If none of $\sigma_0,\sigma_1,\sigma_2$ is an escaper,
> the triple has a cyclic-wait deadlock — so a feasible (cycle-broken) triple **must
> contain at least one escaper.**
>
> *Proof.* If no map escapes, each $D_{\sigma_c}$ is a total self-map of the finite chain
> $\{2,\dots,k\}$, and so is the composition $\Phi=D_{\sigma_2}\circ D_{\sigma_1}\circ
> D_{\sigma_0}$. A composition of non-decreasing maps is non-decreasing, and a
> non-decreasing total self-map of a finite chain has a fixed point (Knaster–Tarski).
> That fixed point is a cyclic-wait solution, i.e. a safe dead-end. $\square$

**Verified.** Over the *entire* space of $35$ non-decreasing maps $\{1..4\}\to\{2..5\}$,
all $35^3=42875$ triples were checked: **$0$** are cycle-free without an escaper — the
theorem with no exception. The characterization "cyclic-wait fixed points $=$ safe
dead-ends" held on **$500/500$** random triples (300 on $\mathrm{QR}_{19}$, 200 on
$\mathrm{AC}_7$, $k=3$).

**What an escaper is, structurally.** $D_\sigma(t)>k \iff r_\sigma(d_\sigma(t))\ge k-1
\iff g_\sigma\big(m-d_\sigma(t)\big)\le 1$: at the position where the prefix clique rises
to level $t$, the complementary **suffix is almost backedge-acyclic** (clique $\le 1$).
For the original gold this is copy $2$: its full clique forms only at the *last* vertex
($d(k)=m{-}1$, ramp fraction $1.0$ in §7), leaving a one-vertex tail — exactly the
"back-loaded" order. So the escaper is the **late-blooming optimal order**, and the §7
staggering finding ("copy 2 back-loaded, full clique at $a=m$") is the *same fact* as
"copy 2 is the escaper." In the original witness its partners
$D_0=(2,3,3),D_1=(2,4,4)$ feed every start level into that escape. More strongly,
$D_2(t)=t+1$ on every relevant level, so copy 2 repeated three times already has no
fixed point and needs no partners (§12).

**Rarity, quantified.** Escaper orders are rare for $\mathrm{QR}_{19}$: **$0$** among the
first $\sim120$–$400$ enumerated optimal profiles (all of which have $D(2)=2$ and stay in
range, giving the $(2,2,2)$ diagonal cycle); the gold's escaper comes from the SAT-found
witness, not the common enumeration. This *explains* the measure-atypicality (G62): a
random optimal triple almost never contains an escaper, so almost never breaks the cycle.

### 10.1 The conjecture in its sharpest form

> **Escaper Conjecture (Route-2 form; refuted as a conjunction).** Every tournament $H$ with
> $\vec\omega(H)=k\ge3$ has an **escaper** optimal order — equivalently, an optimal order
> $\sigma$ with an almost-acyclic tail: $g_\sigma(m-d_\sigma(t))\le 1$ for some level $t$
> (so $D_\sigma(t)>k$) — together with two partner optimal orders whose composition sends
> every start level in $\{2,\dots,k\}$ into the escape.

The Escaper Necessity theorem makes the first clause *necessary*. The claimed
sufficiency-with-partners and its uniform form are false. Historically, this
formulation reduced the question to a single optimal order's **suffix profile** (a
near-acyclic tail at a clique-level crossing), but the iterated-triangle refutation
shows that no such uniform construction can prove H19.

---

## 11. First foothold: escapers exist for all *critical* tournaments  [proved]

The Escaper Necessity theorem (§10) makes "$H$ has an escaper" a prerequisite for H19's
cancellation argument. Here that clause is **proved** for the critical case — which is
exactly where the problem's witnesses and the $k{=}6$ construction targets live.

> **Theorem (escaper existence, critical case).** Let $H$ be $k$-$\vec\omega$-critical
> ($\vec\omega(H)=k$ and $\vec\omega(H-v)=k-1$ for every vertex $v$), $k\ge1$. Then $H$ has
> a level-$k$ escaper optimal order.
>
> *Construction.* Pick any vertex $v$. By criticality $\vec\omega(H-v)=k-1$, so some order
> $\tau$ of $H-v$ has $\omega((H-v)^\tau)=k-1$. Put $\sigma=(\tau,v)$ — $v$ **last**.
>
> *Proof.* The prefix of $\sigma$ (all but the last vertex) is $\tau$ on $H-v$, clique
> $k-1$. Appending the single vertex $v$ raises the backedge clique by at most $1$, so
> $\omega(H^\sigma)\le k$; and $\omega(H^\sigma)\ge\vec\omega(H)=k$, hence $=k$ ($\sigma$
> optimal). Then $f_\sigma(m-1)=k-1$, $f_\sigma(m)=k$, so $d_\sigma(k)=m-1$ and the suffix
> is the single vertex $\{v\}$: $g_\sigma(1)=1\le1$, giving $D_\sigma(k)=2+(k-1)=k+1>k$. So
> $\sigma$ is an escaper. $\square$

The produced map is the canonical shift $D_\sigma(t)=t+1$ around level $k$ — the same
shape as the gold's copy-2 escaper.

**Verified.** On $\mathrm{AC}_7$ (3-critical): $\sigma=(1,2,3,4,5,6,0)$ has
$\omega(\mathrm{AC}_7^\sigma)=3$, $f(6)=2$, $D_\sigma=(2,3,4)$ — an escaper. The theorem is
general, so it applies verbatim to $\mathrm{QR}_{19}$ (4-critical, P15) and to every
critical tournament; no per-object $\vec\omega$ computation is needed (which is why this
sidesteps the order-$\ge19$ census wall that blocks the engine).

**What this closes, and what remains.**
- **Closed:** the *existence* clause of the Escaper Conjecture (§10.1) for **all critical
  $H$** — in particular for QR₁₉, the $\tilde S_n$/$\mathrm{AC}_n$ critical families, and
  the critical inner factors targeted by the $k{=}6$ construction.
- **Open (a) — full raiser or partners.** Escaper existence is necessary but a
  level-$k$ escape alone may leave lower fixed levels. It suffices either to choose an
  append order with $D_\sigma(t)>t$ for every $2\le t\le k$ (a **full raiser**, which
  can be repeated in all copies), or to find partners routing all lower fixed levels
  into the top escape.
- **Open (b) — non-critical $H$.** The append construction needs a *critical vertex*
  ($\vec\omega(H-v)=k-1$). A non-minimal $H$ can have $\vec\omega(H-v)=k$ for all $v$; then
  a level-$k$ escaper need not arise this way (a lower-level $t<k$ escaper might still
  exist). Since H19 quantifies over all $\vec\omega\ge3$ tournaments, closing the universal
  statement needs this case — but every $\vec\omega=k$ tournament *contains* a critical
  induced subtournament with $\vec\omega=k$, so a reduction to the critical case is the
  plausible bridge.

This is the first uniform (infinite-family) advance on the Route-2 program that does **not**
depend on the single QR₁₉ witness: it proves a needed structural feature for an entire,
relevant class of tournaments from criticality alone.

---

## 12. Append-built partner experiment  [implemented]

`scripts/route2_append_partners.py` implements the §11 construction and searches the
resulting demand maps. Every positive result is checked twice: by the cycle criterion
and by an explicit greedy interleaving whose product backedge clique is recomputed with
`core.omega_of_order`. Results are saved in
`data/route2_append_partners.json`.

### 12.1 Full raisers eliminate partners on all tested $k=3$ critical objects

For $k=3$, a full raiser has map $(D(2),D(3))=(3,4)$. Such an append-built order was
found for:

- $\mathrm{AC}_7,\mathrm{AC}_9,\mathrm{AC}_{11}$;
- both saved order-8 $3$-$\vec\omega$-critical isomorphism classes;
- $\widetilde S_3$.

For the $\mathrm{AC}_n$ family the canonical shift
$$\sigma=(1,2,\dots,n-1,0)$$
has $D=(3,4)$ for every tested odd $n\in\{7,9,11,13,17,19,23\}$. Repeating the same
order in all three copies is cycle-free and gives a core-verified clique-4 order of
$C_3[\mathrm{AC}_n]$ on the scripted targets.

### 12.2 QR19: the partner problem disappears for the known escaper

The gold copy-2 order is append-built and has
$$D=(3,4,5),$$
so it is a full raiser. Repeating it three times yields $2642$ safe/reachable states,
zero dead-ends, and an explicit core-verified clique-5 order of
$C_3[\mathrm{QR}_{19}]$. This refutes the former capped-audit conclusion that
$\mathrm{QR}_{19}$ requires distinct inner orders.

### 12.3 First genuine partner test: $\mathrm{AC}_7[C_3]$

Appending the deleted vertex to the proved `d_then_c` order of
$\mathrm{AC}_n[C_3]-(0,0)$ gives the uniform map
$$D=(3,3,5),$$
which escapes at level $4$ but fixes level $3$. A bounded adjacent-swap BFS around the
$n=7$ deletion template examined $6381$ states and found only
$$D\in\{(3,3,5),(2,3,5),(2,2,5)\};$$
no triple from these maps is cycle-free. This is a scoped negative for that connected
neighborhood, not a universal failure of append-built partners.

**Updated crux.** The critical-case problem is now: prove that every critical tournament
has either (i) a full-raiser append order, or (ii) append-built maps whose cyclic
composition sends every lower fixed level into the guaranteed level-$k$ escape.

---

## 13. AC₇[C₃] resolved by direct SAT: H19 holds; optimal-inner is NOT WLOG  [proved]

The append-partner experiment (`scripts/route2_append_partners.py`) found no full-raiser /
cycle-free triple for the substitution-critical $\mathrm{AC}_7[C_3]$ (order 21, $k=4$),
raising the question of whether H19 could **fail** there (which would have made
$C_3[\mathrm{AC}_7[C_3]]$ a first $\vec\omega\ge6$ object). It does not.

**Decided directly by the P23 method** (no-$K_6$ linear-ordering SAT, the same encoding
that pinned $\vec\omega(C_3[\mathrm{QR}_{19}])=5$): on $C_3[\mathrm{AC}_7[C_3]]$ (order 63,
$=$ the tower $C_3{\to}\mathrm{AC}_7{\to}C_3$ by lex associativity), the no-$K_6$ CNF is
**SAT on both Cadical153 and Minisat22**, and the reconstructed order has backedge clique
$5$ (independently checked by `core.omega_of_order`). With the lex lower bound $5$:
$$\boxed{\ \vec\omega(C_3[\mathrm{AC}_7[C_3]])=5\ }\qquad\Rightarrow\qquad\textbf{H19 holds for }\mathrm{AC}_7[C_3].$$
This is a new inner-$\mathrm{ov}=4$ datapoint for H19 — the **first substitution-critical**
one, beyond the circulants $\mathrm{QR}_{19},H_1^\*,H_2^\*$.

**Why the Route-2 (optimal-order) search missed it — optimal-inner is not WLOG.**
Decomposing the SAT witness into its three copy-induced inner orders:

| copy | inner backedge clique (width) | demand-map |
|---|---|---|
| 0 | **5** ($=k{+}1$, NON-optimal) | n/a (width $>k$) |
| 1 | 4 (optimal) | $(2,3,4,4)$ |
| 2 | 4 (optimal) | $(2,2,3,5)$ |

So the witness uses a **width-$(k{+}1)$ inner order** in copy 0. The H25/Route-2 feasibility
search (and the escaper/full-raiser analysis of §8–§11) is restricted to **optimal** inner
orders, so it provably cannot see this witness. Conclusion: the "optimal-inner suffices"
sub-conjecture is **false in general** (at least, the natural witness here is non-optimal),
and the optimal-order escaper program is **sufficient-not-complete** — some critical $H$
(notably substitution criticals) satisfy H19 only via a non-optimal inner order.

**Methodological upshot.** The no-$K_6$ SAT decides H19 **directly, per $H$**, for any inner
$H$ with $C_3[H]$ of tractable order ($\lesssim 63$, i.e. $|H|\lesssim 20$). This is a real
unblock past the "only $\mathrm{QR}_{19}$" data starvation: H19 can now be *verified* on
many inner-$\mathrm{ov}=4$ critical tournaments (a counterexample would refute H19; broad
confirmation strengthens it) — empirical verification, not a proof, but no longer gated on
the order-19 census wall for this question.

> **Correction (provenance).** Two exploratory scripts, `route2_ac7c3_feasibility.py` and
> `route2_ac7c3_feasibility_broad.py`, passed `build_ac_c3(7)`'s third return value ($=3$,
> the inner $C_3$ size) as the lattice order instead of $n=21$; both their outputs ("0
> feasible" and "all feasible") are invalid and superseded by the SAT result above.

### 13.1 Batch no-K₆ verification of H19 over inner-ov=4 criticals

`scripts/batch_h19_noK6.py` runs the no-$K_6$ decision on $C_3[H]$ for a set of inner-ov=4
critical $H$ (both solvers; witness clique re-checked by `core.omega_of_order`):

| $H$ | family | $C_3[H]$ order | $\vec\omega(C_3[H])$ |
|---|---|---|---|
| $\mathrm{QR}_{19}$ | circulant | 57 | 5 |
| $\mathrm{AC4}_{21}$ | circulant | 63 | 5 |
| $\mathrm{AC}_7[C_3]$ | substitution | 63 | 5 |
| $C_3[H_7]$ | substitution | 63 | 5 |
| $H_1^\*$ | circulant | 75 | 5 |
| $H_2^\*$ | circulant | 75 | 5 |
| $\mathrm{AC}_9[C_3]$ | substitution | 81 | 5 |

**H19 holds (= ov+1 = 5) on all seven**, across both the circulant and the substitution
families — no $\vec\omega\ge6$ object. $\mathrm{AC}_{11}[C_3]$ (order 99) and
$\mathrm{AC}_{13}[C_3]$ (order 117) timed out on transitive-6-chain enumeration (a tooling
limit, not a result). **Scope caveat:** these are two STRUCTURED families, not a generic
census; the universal H19 is now well-supported at inner-ov=4 (7 datapoints vs the prior 4)
but does not extend uniformly. The no-$K_6$ SAT remains a per-$H$ decision tool.
