# Lemmas - Matching-FAS for tournaments is polynomial

## Setup

Let $T$ be a tournament on vertex set $V$, $|V| = n$, with arc set $A(T)$.
A **matching FAS** of $T$ is a FAS $F \subseteq A(T)$ such that the
underlying undirected graph $\underline{F}$ has maximum degree $\le 1$.
For $M \subseteq A(T)$, write $T \oplus M$ for the tournament obtained
from $T$ by reversing exactly the arcs of $M$.

For a total order $\prec$ on $V$, let

$$
B_\prec(T)=\{(v,u)\in A(T): u\prec v\}
$$

be the set of back-arcs of $T$ with respect to $\prec$.

The useful normalization is slightly weaker than the often-quoted
"FAS = back-arc set" slogan:

- If $F$ is a FAS, then any topological order $\prec$ of $T-F$ satisfies
  $B_\prec(T)\subseteq F$.
- Conversely, $B_\prec(T)$ is itself a FAS for every total order $\prec$.

Therefore

> $T$ has a matching FAS iff there exists a total order $\prec$ on $V$
> whose back-arc set is a matching, iff there exists a matching
> $M \subseteq A(T)$ such that $T \oplus M$ is transitive,
> where $T \oplus M$ is $T$ with each arc of $M$ reversed.

Indeed, if $F$ is a matching FAS and $\prec$ is a topological order of
$T-F$, then $B_\prec(T)\subseteq F$, hence $B_\prec(T)$ is a matching,
and $T\oplus B_\prec(T)$ is the transitive tournament ordered by
$\prec$. This proves the first implication and gives the second with
$M=B_\prec(T)$.

Conversely, if $M$ is a matching and $T\oplus M$ is transitive, let
$\prec$ be its transitive order. Then every arc of $M$ is a back-arc of
$T$ with respect to $\prec$, and no arc outside $M$ is: arcs outside $M$
were not reversed and therefore agree with the transitive order. Thus
$M=B_\prec(T)$. In particular, $T-M$ is a subdigraph of the acyclic
tournament $T\oplus M$, so $M$ is a matching FAS.

## Definitions

- An arc $(u, v) \in A(T)$ is a **no-shortcut arc** if there is no
  $w \in V \setminus \{u, v\}$ with $u \to w$ and $w \to v$ in $T$.
  Equivalently, $N^+(u) \cap N^-(v) = \emptyset$.
- A 3-element subset $\{a, b, c\}$ of $V$ is a **cyclic 3-cycle** if its
  arcs in $T$ form a directed 3-cycle, and a **transitive triangle**
  otherwise.
- For a transitive triangle on $\{a, b, c\}$ with linear order
  $a \succ b \succ c$, the **long arc** is $(a, c)$.
- A subset $X \subseteq V$ is a **module** of $T$ if every
  $w \in V \setminus X$ has the same arc direction to every vertex of
  $X$ (either $w \to x$ for all $x \in X$, or $x \to w$ for all $x \in X$).
- A **cyclic module** means a 3-vertex set that is both a cyclic
  3-cycle and a module.

## Observation 0 (3-vertex arc reversals)

The following two elementary facts are used repeatedly.

1. If $a\to b\to c\to a$ is a directed triangle, then reversing any one
   of its three arcs gives a transitive triangle:
   - reverse $a\to b$: $b\to c\to a$ and $b\to a$;
   - reverse $b\to c$: $c\to a\to b$ and $c\to b$;
   - reverse $c\to a$: $a\to b\to c$ and $a\to c$.
2. If $a\succ b\succ c$ is a transitive triangle, with arcs
   $a\to b$, $b\to c$, and $a\to c$, then reversing a short arc keeps the
   triangle transitive, while reversing the long arc makes it cyclic:
   - reverse $a\to b$: $b\to a\to c$ and $b\to c$;
   - reverse $b\to c$: $a\to c\to b$ and $a\to b$;
   - reverse $a\to c$: $a\to b\to c\to a$.

## Theorem 1 (MFAS structural characterization)

For a matching $M\subseteq A(T)$, $T\oplus M$ is transitive iff
$M$ satisfies:

- **(N)** every arc of $M$ is a no-shortcut arc;
- **(C)** every cyclic 3-cycle of $T$ contains exactly one arc of $M$.

Consequently, $T$ has a matching FAS iff there exists a matching
$M \subseteq A(T)$ satisfying **(N)** and **(C)**.

### Proof

A tournament is transitive iff every 3-vertex subtournament is
transitive. The forward implication is immediate. For the reverse,
a non-transitive tournament contains a directed cycle. Choose a shortest
directed cycle $v_1\to v_2\to\cdots\to v_k\to v_1$. If $k\ge 4$, then
the chord between $v_1$ and $v_3$ gives a contradiction: if
$v_3\to v_1$, then $v_1\to v_2\to v_3\to v_1$ is a directed triangle;
if $v_1\to v_3$, then
$v_1\to v_3\to v_4\to\cdots\to v_k\to v_1$ is a shorter directed cycle.
Thus a non-transitive tournament contains a directed triangle.

Fix a 3-vertex set $Q=\{a,b,c\}$. Since $M$ is a matching, at most one
arc of $T[Q]$ lies in $M$.

First suppose $T\oplus M$ is transitive. If $T[Q]$ is cyclic, then
$Q$ cannot contain zero arcs of $M$, because otherwise it remains cyclic
in $T\oplus M$. Thus every cyclic triangle of $T$ contains exactly one
arc of $M$, proving **(C)**.

Now take any $e=(u,v)\in M$. If there existed $w$ with
$u\to w\to v$ in $T$, then $T[\{u,w,v\}]$ would be the transitive
triangle ordered $u\succ w\succ v$, and $e$ would be its long arc.
Since $M$ is a matching, neither $(u,w)$ nor $(w,v)$ belongs to $M$.
Thus $T\oplus M$ reverses exactly the long arc on this triple. By
Observation 0 this creates a cyclic triangle, contradicting the
transitivity of $T\oplus M$. Hence $e$ is no-shortcut. This proves
**(N)**.

Conversely suppose **(N)** and **(C)** hold. We show that every
3-vertex subtournament of $T\oplus M$ is transitive.

If $T[Q]$ is cyclic, then by **(C)** exactly one of its arcs is reversed;
by Observation 0, reversing one arc of a directed triangle always makes
it transitive.
If $T[Q]$ is transitive, then either no arc of $Q$ is reversed, in which
case it remains transitive, or exactly one arc $e$ is reversed. In the
latter case, **(N)** says that $e$ is not the long arc of this transitive
triangle. By Observation 0, reversing either short arc of a transitive
triangle keeps it transitive. Thus $T\oplus M$ is transitive on every
triple, hence is transitive.

The final equivalence with matching FAS follows from the normalization
in the setup. $\square$

## Lemma 2 (cyclic 3-cycles with all arcs no-shortcut are exactly the cyclic modules)

A cyclic 3-cycle $X = \{a, b, c\}$ of $T$ has all 3 arcs no-shortcut
iff $X$ is a module of $T$.

### Proof

WLOG $X$ has arcs $a \to b, b \to c, c \to a$. Pick any
$w \in V \setminus X$.

Let

$$
S(w)=\{x\in X: x\to w\}.
$$

Thus $x\in S(w)$ means that $x$ dominates $w$, while
$x\notin S(w)$ means that $w$ dominates $x$.

The three possible shortcuts through $w$ are exactly:

- $a\to w\to b$, i.e. $a\in S(w)$ and $b\notin S(w)$;
- $b\to w\to c$, i.e. $b\in S(w)$ and $c\notin S(w)$;
- $c\to w\to a$, i.e. $c\in S(w)$ and $a\notin S(w)$.

Therefore the three arcs of $X$ are all no-shortcut iff, for every
outside vertex $w$,

$$
a\in S(w)\Rightarrow b\in S(w),\qquad
b\in S(w)\Rightarrow c\in S(w),\qquad
c\in S(w)\Rightarrow a\in S(w).
$$

These cyclic implications force $S(w)$ to be either empty or all of
$X$: if one of $a,b,c$ lies in $S(w)$, all three do; if none lies in
$S(w)$, $S(w)=\emptyset$. The case $S(w)=X$ says $X\to w$, and the case
$S(w)=\emptyset$ says $w\to X$.

Thus every outside vertex has a uniform direction to $X$, exactly the
definition of a module. The converse is the same argument read
backwards: if every outside vertex is uniform to $X$, then for each
$w$ the set $S(w)$ is either $\emptyset$ or $X$, so none of the three
shortcut patterns occurs. $\square$

## Lemma 3 (vertex-disjointness)

Let $X$ and $Y$ be two distinct cyclic-3-cycle modules of $T$. Then
$X \cap Y = \emptyset$.

### Proof

Suppose $X\cap Y\ne\emptyset$ and $X\ne Y$. Since both sets have size
3, there are two cases.

First suppose $|X\cap Y|=2$. Write $X=\{a,b,c\}$ and $Y=\{a,b,d\}$,
where $c\ne d$, naming $a$ and $b$ so that the shared arc is
$a\to b$. Since both triples are cyclic and both contain the arc
$a\to b$, their remaining arcs must satisfy

$$
b\to c\to a,\qquad b\to d\to a.
$$

But $X$ is a module and $d\notin X$. The arcs $d\to a$ and $b\to d$
show that $d$ is not uniform to $X$: $d$ dominates $a$, while $b$
dominates $d$. This contradicts the module property of $X$.

Now suppose $|X\cap Y|=1$, say $X\cap Y=\{a\}$.

Let $X = \{a, b, c\}$ with cycle $a \to b \to c \to a$, and
$Y = \{a, d, e\}$ with cycle $a \to d \to e \to a$; this is just a
choice of names for the two vertices of $Y\setminus\{a\}$.

Apply $Y$-module to $b$ (which is in $V \setminus Y$): the three arcs
between $b$ and $\{a, d, e\}$ all point the same way. From $X$,
$a \to b$, so $b$ is dominated by $a$; by uniformity, $b$ is dominated
by all of $Y$: $d \to b$, $e \to b$.

Apply $Y$-module to $c$: from $X$, $c \to a$, so $c$ dominates $a$; by
uniformity, $c$ dominates all of $Y$: $c \to d$, $c \to e$.

Now apply $X$-module to $d$. From above, $d \to b$ (so $d$ does not
get dominated by $b$ — $d$ dominates $b$), and $c \to d$ (so $d$ does
not dominate $c$). The arcs $d \to b$ and $c \to d$ have opposite
directions, so $d$'s arc directions to $X$ are *not* uniform.
Contradiction with $X$ being a module.

Hence $X \cap Y = \emptyset$. $\square$

## Lemma 4 (no arc of a cyclic module is in any other cyclic 3-cycle)

Let $X$ be a cyclic 3-cycle that is a module of $T$, and let $Y$ be a
cyclic 3-cycle different from $X$. Then $Y$ contains no arc of $X$.

### Proof

Suppose instead that $Y$ shares an arc $e$ with $X$. Relabel the
vertices of $X$ so that $X=\{a,b,c\}$ with
$a\to b\to c\to a$ and $e=(a,b)$. Then
$Y=\{a,b,d\}$ for some $d\notin X$.

$Y$ is a cyclic 3-cycle through arc $a \to b$, so its cycle structure
is $a \to b \to d \to a$, giving arcs $b \to d$ and $d \to a$ in $T$.

$X$ is a module, so $d \in V \setminus X$ has a uniform arc direction
to $\{a, b, c\}$. Two cases:

- $d \to \{a, b, c\}$: then $d \to a$, $d \to b$, $d \to c$. But
  $Y$ has $b \to d$, contradiction.
- $\{a, b, c\} \to d$: then $a \to d$. But $Y$ has $d \to a$,
  contradiction.

Hence no such $Y$ exists. $\square$

## Lemma 5 (cyclic modules have no incident outside no-shortcut arcs)

Let $X$ be a cyclic module of $T$. If $w\in V\setminus X$ and
$x\in X$, then the arc between $w$ and $x$ is not no-shortcut.

### Proof

Relabel $X=\{a,b,c\}$ with $a\to b\to c\to a$. Since $X$ is a module,
either $w\to X$ or $X\to w$.

Suppose first that $w\to X$. For any $x\in X$, let $y$ be the
predecessor of $x$ on the directed cycle inside $X$, so $y\to x$.
Then $w\to y\to x$, so the arc $w\to x$ has a shortcut.

Suppose instead that $X\to w$. For any $x\in X$, let $y$ be the
successor of $x$ on the directed cycle inside $X$, so $x\to y$.
Then $x\to y\to w$, so the arc $x\to w$ has a shortcut.

Thus no arc between $X$ and $V\setminus X$ is no-shortcut. $\square$

## Theorem 2 (MFAS in P)

The matching-FAS decision problem on tournaments is in polynomial time.
Specifically, the following algorithm decides it in $O(n^3)$ time:

1. **Enumerate** all cyclic 3-cycles $\mathcal{C}$ of $T$ ($O(n^3)$).
2. **Compute** the no-shortcut arc set $A^* \subseteq A(T)$ ($O(n^3)$).
3. **Partition** $\mathcal{C}$:
   - $\mathcal{C}_3$ = cycles with all 3 arcs in $A^*$ (the cyclic
     modules, by Lemma 2).
   - $\mathcal{C}_2, \mathcal{C}_1, \mathcal{C}_0$ = cycles with 2, 1,
     and 0 arcs in $A^*$ respectively.
4. **Reject** if $\mathcal{C}_0 \ne \emptyset$ (some cyclic 3-cycle has
   no candidate arc).
5. **Pick one arc per module:** by Lemma 3 the modules are
   vertex-disjoint, by Lemma 4 no internal arc of a module appears in any
   other cyclic triangle, and by Lemma 5 no outside no-shortcut arc is
   incident with a module vertex. Thus choosing any one internal arc per
   module creates no matching conflict with the rest of the instance and
   covers exactly the corresponding module triangle. Add these selected
   arcs to $M$.
6. **2-SAT:** introduce a Boolean variable $x_e$ for every
   $e \in A^*$ outside cyclic modules. Add clauses:
   - For $C \in \mathcal{C}_1$ with unique $A^*$-arc $e$: force
     $x_e = 1$.
   - For $C \in \mathcal{C}_2$ with $A^*$-arcs $e_1, e_2$: enforce
     $x_{e_1} \oplus x_{e_2} = 1$ via the two clauses
     $(x_{e_1} \vee x_{e_2})$ and $(\neg x_{e_1} \vee \neg x_{e_2})$.
   - Matching: for every pair
     $e_1, e_2 \in A^* \setminus
     \bigcup_{X \in \mathcal{C}_3} A(T[X])$ sharing a vertex, add
     $(\neg x_{e_1} \vee \neg x_{e_2})$.
7. Return YES iff the 2-SAT system is satisfiable.

Correctness follows from Theorem 1 and Lemmas 2–5. Lemma 2 identifies
exactly the cyclic triangles with three candidate arcs as cyclic modules.
Lemmas 3–5 decouple those modules from one another and from the residual
candidate set. After the arbitrary one-arc-per-module choices, every
remaining cyclic triangle has either one or two available no-shortcut
arcs. The unit clauses and XOR clauses encode the requirement that each
such triangle receive exactly one selected arc, and the binary conflict
clauses encode precisely the requirement that the selected arcs form a
matching. Therefore a satisfying assignment is exactly a set $M$
satisfying Theorem 1, together with the preselected module arcs.

Time: $O(n^3)$. There are $O(n^3)$ cyclic triangles and the no-shortcut
arc set can be computed by checking each arc against all possible middle
vertices. The 2-SAT instance has $O(n^2)$ variables. It has $O(n^3)$
triangle clauses and $O(n^3)$ matching-conflict clauses, since for each
candidate arc $(u,v)$ there are only $O(n)$ candidate arcs incident with
$u$ or $v$. Linear-time 2-SAT therefore gives an $O(n^3)$ decision
algorithm.

## Open ends

- The **path-FAS** case (Problem 4.4, second half) is not addressed by
  these lemmas. The matching proof uses the fact that a matching can
  contribute at most one reversed arc to any triangle. A path-FAS has
  maximum degree 2, so a triangle can contain two selected arcs forming a
  "V". In that regime the long-arc obstruction from transitive triangles
  no longer reduces to a one-arc no-shortcut condition, and the 2-SAT
  encoding above does not transfer.
- The **path** case has $|F| \le n - 1$ (vs $|F| \le n/2$ for MFAS), so
  it admits a larger feasible region. Any path-FAS attack must also
  handle connectivity of the selected arcs, not just degree constraints.
- The proof above is a self-contained polynomial-time decision argument
  for matching-FAS. It does **not** claim novelty. The cyclic-module
  objects are ordinary tournament modules; before this is presented as a
  new result, the specific 2-SAT reduction should be checked against the
  tournament modular-decomposition and feedback-arc-set literature.
- The implementation has been informally cross-checked against brute
  force over the 74 non-isomorphic tournaments at $n \le 6$ and 150
  random samples at $n \in \{7, 8\}$ with zero disagreements (see
  `scripts/cross_check.py` and `scripts/random_check.py`). This is a
  smoke test, not a substitute for the proof or for adversarial testing.
