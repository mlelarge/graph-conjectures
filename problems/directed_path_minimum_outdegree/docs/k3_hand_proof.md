# Hand proof: Conjecture 1 for $\delta = 3$

**Result.** Every oriented graph $D$ with $\delta^+(D) \geq 3$ contains a
directed simple path of length $6$.

This closes the $\delta = 3$ case of Cheng--Keevash Conjecture 1 (the
oriented-graph version of Thomasse's path conjecture). It is a strengthening
of Cheng--Keevash Theorem 4, which gives only $\ell(D) \geq \lceil 1.5\delta
\rceil = 5$ for $\delta = 3$.

The proof is a structural argument that combines Cheng--Keevash Lemma 7 with
the oriented-graph average-outdegree bound and antiparallel constraints
arising from path and cycle arcs.

## Notation

For an oriented graph $D$:

- $\delta^+(D) = \min_v d^+(v)$ (minimum outdegree);
- $\ell(D) = $ length (in arcs) of a longest directed simple path;
- a directed cycle of length $g$ has $g$ arcs and $g$ vertices;
- $V(P), V(C)$ denote vertex sets of a path $P$ and cycle $C$;
- "antiparallel" means a pair $u \to v, v \to u$, forbidden in oriented graphs.

## Tools used

The proof uses three results:

- **Cheng--Keevash Theorem 4:** every oriented graph with $\delta^+ \geq
  \delta$ has $\ell \geq \lceil 1.5 \delta \rceil$. (For $\delta = 3$:
  $\ell \geq 5$.)
- **Cheng--Keevash Lemma 7 (and its proof internals):** if $\ell < 2\delta$,
  there exists an induced subgraph $S$ with $|S| \leq \delta$ and $\delta^+(S)
  \geq 2\delta - \ell$. The proof's specific construction yields $S = B^-$,
  the predecessors-in-cycle of $B = N^+(v_{a-1}) \cap V(C)$, where $C$ is the
  endpoint cycle.
- **The oriented-graph average bound:** in any oriented graph on at most $m$
  vertices, $\delta^+ \leq \lfloor (m-1)/2 \rfloor$, since the average
  outdegree is at most $(m-1)/2$.

## Proof

**Step 1: reductions.**

Assume for contradiction that $D$ is an oriented graph with $\delta^+(D) \geq
3$ and $\ell(D) \leq 5$. By Theorem 4, $\ell(D) \geq 5$, so $\ell(D) = 5$.

(R1) Pass to a sink strongly connected component $H_0$ of $D$. Out-arcs of
a sink SCC stay inside, so $\delta^+(H_0) \geq 3$. Paths in $H_0$ are paths
in $D$, so $\ell(H_0) \leq 5$; Theorem 4 forces $\ell(H_0) = 5$. Now $H_0$
is strongly connected, oriented, $\delta^+(H_0) \geq 3$, $\ell(H_0) = 5$.

(R2) Choose, for each vertex of $H_0$, exactly three of its outgoing arcs;
delete the rest. The resulting spanning subdigraph $H_1$ has $d^+(v) = 3$
for every $v$, but it is *not necessarily* strongly connected. Deleting
arcs cannot create new paths, so $\ell(H_1) \leq \ell(H_0) = 5$.

(R3) Pass to a sink strongly connected component $H$ of $H_1$. By
definition of sink SCC in $H_1$, every $v \in H$ has all its $H_1$-out-arcs
ending inside $H$. Since $v$ has exactly $3$ out-arcs in $H_1$, all three
lie in $H$. Hence $H$ is $3$-outregular. $H$ is oriented (sub-digraph of
oriented), strongly connected (by definition of SCC), and
$\ell(H) \leq \ell(H_1) \leq 5$. Theorem 4 applied to $H$ gives
$\ell(H) \geq 5$, hence $\ell(H) = 5$. The oriented average bound
$\delta^+ \leq (|V(H)| - 1)/2$ with $\delta^+(H) = 3$ gives
$|V(H)| \geq 7$.

Henceforth $D$ denotes $H$: a strongly connected $3$-outregular oriented
graph with $\ell(D) = 5$ and $|V(D)| \geq 7$.

**Step 2: pick a longest path with maximum cycle bound.**

Choose a longest directed simple path $P = v_0 v_1 v_2 v_3 v_4 v_5$, and
among all longest paths, choose one for which the *cycle bound* is maximal,
where the cycle bound is defined as follows. Let

$$
I = \{ i : v_5 \to v_i \}, \qquad a = \min I.
$$

By Lemma A (every out-neighbour of the endpoint lies on $P$), $I$ is the
index set of out-neighbours of $v_5$ among $\{v_0, \ldots, v_4\}$. Since
$|N^+(v_5)| = 3$, we have $|I| = 3$, so

$$
a \leq 5 - 3 = 2.
$$

By the strong-connectivity argument in Cheng--Keevash's proof of Lemma 7
(which uses $|V(D)| \geq 2\delta + 1$ and strong connectivity to extend the
path otherwise), $a \neq 0$. So $a \in \{1, 2\}$.

The cycle $C := v_a v_{a+1} \cdots v_5 v_a$ has $|V(C)| = 5 - a + 1 = 6 - a$
vertices.

**Step 3: apply Cheng--Keevash Lemma 7 to extract $S$.**

Define

$$
A = N^+(v_{a-1}) \cap \{v_0, \ldots, v_{a-1}\}, \qquad
B = N^+(v_{a-1}) \cap V(C),
$$

and let $B^- = \{u \in V(C) : uv \in A(C) \text{ for some } v \in B\}$ be the
set of predecessors-in-$C$ of vertices in $B$. Let $S$ be the subgraph of $D$
induced on $B^-$.

By Claim 11, $N^+(v_{a-1}) \subseteq V(P) = \{v_0, \ldots, v_5\}$. There is no
self-loop, so $A \cup B = N^+(v_{a-1})$ disjointly and $|A| + |B| = 3$.

By Lemma 7's proof (in particular the count $|C| \geq |S| - \delta^+(S) +
\delta$ derived from Claim 12), $S$ has $|S| \leq 3$ and

$$
\delta^+(S) \geq 2\delta - \ell(D) = 6 - 5 = 1,
$$

and $|V(C)| \geq |S| + \delta - \delta^+(S)$.

**Step 4: $|S| = 3$ and $a = 1$.**

In an oriented graph $S$ on at most $3$ vertices, the average outdegree is at
most $(|S| - 1)/2 \leq 1$, so $\delta^+(S) \leq \lfloor (|S| - 1)/2 \rfloor$.
Combined with $\delta^+(S) \geq 1$:

- $|S| = 1$: $\delta^+(S) = 0$, contradiction;
- $|S| = 2$: in oriented graph on 2 vertices, max outdegree is 1 for one
  vertex and 0 for the other, so $\delta^+(S) = 0$, contradiction;
- $|S| = 3$: forced.

Hence $|S| = 3$, and since $|S| = |B^-| = |B|$ (the predecessor map is a
bijection on $V(C)$), $|B| = 3$. Therefore $|A| = 0$.

The geometric bound gives $|V(C)| \geq 3 + 3 - \delta^+(S) \geq 3 + 3 - 1 =
5$. With $|V(C)| = 6 - a$, this forces $a \leq 1$, and combined with
$a \geq 1$:

$$
a = 1.
$$

So $V(C) = \{v_1, v_2, v_3, v_4, v_5\}$ and the cycle is $v_1 \to v_2 \to v_3
\to v_4 \to v_5 \to v_1$ (the last arc is the closing arc, present because
$a = 1$ means $v_5 \to v_1$).

**Step 5: $S$ is a directed triangle and $v_5 \in S$.**

$\delta^+(S) \geq 1$ and $\delta^+(S) \leq \lfloor 2/2 \rfloor = 1$, so
$\delta^+(S) = 1$ exactly. Sum of outdegrees in $S$ equals number of arcs in
$S$, between $3$ (each vertex has outdegree $\geq 1$) and $3$ (max in
oriented on 3 vertices). So exactly $3$ arcs, each vertex with $d^+_S = 1$.
Hence $S$ is a directed 3-cycle (the only oriented graph on 3 vertices with
each vertex of outdegree exactly 1).

$B = N^+(v_0) \subseteq V(C)$, with $|B| = 3$. Path arc $v_0 \to v_1$ gives
$v_1 \in B$. The predecessor of $v_1$ in $C$ is $v_5$, so

$$
v_5 \in B^- = V(S).
$$

**Step 6: each $s \in S$ sends arcs to both vertices of $V(C) \setminus S$.**

By Claim 12, $N^+(s) \subseteq V(C)$ for every $s \in B^- = V(S)$. Each $s$
has $d^+(s) = 3$ in $D$ (after the $3$-outregular reduction), $d^+_S(s) = 1$
within $S$, hence

$$
|N^+(s) \cap (V(C) \setminus S)| = 3 - 1 = 2.
$$

Since $|V(C) \setminus S| = 5 - 3 = 2$, every $s \in S$ sends an arc to each
vertex of $V(C) \setminus S$.

**Step 7: antiparallel closure forces $S \in \{\emptyset, V(C)\}$.**

The path arcs $v_i \to v_{i+1}$ for $i \in \{1, 2, 3, 4\}$ and the cycle
closing arc $v_5 \to v_1$ all lie in $D$. We derive five implications:

(P1) Suppose $v_2 \in S$ and $v_1 \in V(C) \setminus S$. Step 6 gives $v_2
     \to v_1$. Path arc $v_1 \to v_2$. Antiparallel — contradiction. So

$$
v_2 \in S \implies v_1 \in S.
$$

(P2) Same with $i=2$: $v_3 \in S \implies v_2 \in S$.

(P3) Same with $i=3$: $v_4 \in S \implies v_3 \in S$.

(P4) Same with $i=4$: $v_5 \in S \implies v_4 \in S$.

(C1) Suppose $v_1 \in S$ and $v_5 \in V(C) \setminus S$. Step 6 gives
     $v_1 \to v_5$. Cycle arc $v_5 \to v_1$. Antiparallel — contradiction. So

$$
v_1 \in S \implies v_5 \in S.
$$

The five implications together state that $S$ is closed under the cyclic
predecessor permutation

$$
\sigma : v_1 \mapsto v_5,\ v_2 \mapsto v_1,\ v_3 \mapsto v_2,\ v_4 \mapsto v_3,\ v_5 \mapsto v_4
$$

on $V(C)$. The permutation $\sigma$ is a single 5-cycle. Its only
$\sigma$-invariant subsets are $\emptyset$ and $V(C)$.

**Step 8: contradiction.**

By Step 5, $v_5 \in S$, so $S \neq \emptyset$. By Step 7, $S = V(C)$, hence
$|S| = 5$. By Step 4, $|S| = 3$. Contradiction.

Therefore $\ell(D) \neq 5$, so $\ell(D) \geq 6 = 2 \delta$. $\square$

## What this does and does not say

- The result holds for *every* oriented graph with $\delta^+ \geq 3$; there
  is no upper bound on $|V(D)|$. The proof never uses $n = 8$ or any other
  specific size; it uses only $|V(D)| \geq 7$ for the $a \neq 0$ step.
- The result strengthens Cheng--Keevash Theorem 4 from $\ell \geq 5$ to
  $\ell \geq 6$ for the case $\delta = 3$. It does not improve their general
  $1.5\delta$ asymptotic bound.
- The proof uses Lemma 7 essentially. It is not a self-contained elementary
  proof.
- The same approach for $\delta = 4$ kills $|S| = 3$ entirely (any $a$)
  and the score sequence $(1,1,1,1)$ at $|S| = 4$, but does not close the
  $(2,1,1,1)$, $(2,2,1,1)$, and $(3,1,1,1)$ score sequences at
  $|S| = 4, a = 1$. The cyclic-closure argument requires every
  $s \in S$ to reach all of $V(C) \setminus S$; this happens iff
  $d^+_S(s) = 1$ for every $s$.

## Possible extensions

- **$\delta = 4$.** At $\ell = 7$, Lemma 7 forces $|S| \in \{3, 4\}$ and
  $a \in \{1, 2\}$ in principle, but the $|S| = 3$ branches all die:
  $|B| = 3 \Rightarrow |A| = 1$, while $|A| \leq a - 1$ kills $a = 1$ and
  $a = 2$ forces $A = \{v_0\}$, i.e., $v_1 \to v_0$, antiparallel with the
  path arc $v_0 \to v_1$. So only $|S| = 4, a = 1$ survives, with
  $|V(C)| = 7$ and $v_7 \in S$. Branch by the internal score sequence of
  $S$ (oriented graph on 4 vertices with $\delta^+(S) = 1$):
  - $(1,1,1,1)$ (sum 4, every vertex of $S$ has $d^+_S = 1$ — does *not*
    have to be a directed 4-cycle; it can also be a directed triangle plus
    a vertex with one arc into the triangle): closure argument applies and
    contradicts $|S| < |V(C)| = 7$.
  - $(2,1,1,1)$ (sum 5): $S$ is forced to be a cyclic interval of 4
    consecutive vertices in $C$ with the unique outdegree-2 vertex at the
    interval start. Open subcase.
  - $(2,2,1,1)$ (sum 6, $S$ is the unique strong tournament on 4
    vertices up to isomorphism): genuine open subcase.
  - $(3,1,1,1)$ (sum 6, $S$ is one vertex dominating a directed 3-cycle
    on the other three; not strongly connected, but Lemma 7 does not
    require $S$ to be strong): the dominant vertex has $d^+_S = 3$ and
    sends only $\delta - 3 = 1$ arc to $V(C) \setminus S$, missing 2 of
    its 3 vertices. The closure argument has two leaks at the dominant
    vertex. However, the three vertices with $d^+_S = 1$ each send arcs
    to all of $V(C) \setminus S$, so the same partial-closure structure
    as $(2,1,1,1)$ applies: $S$ is forced to be a cyclic interval of
    4 consecutive vertices in $C$ with the dominant (outdegree-3)
    vertex at the interval start. Open subcase.
- **General $\delta$.** As $\delta$ grows, the gap $2\delta - \lceil 1.5
  \delta \rceil$ grows linearly, and $|S|$ has more shapes. The
  cyclic-closure argument is increasingly partial. New ideas required.
- **Indegree-deficient vertex (Jackson 1981).** This proof did not use the
  Jackson constraint. For larger $\delta$ (or for $n = 2\delta + 2$ analyses),
  the indegree-deficient vertex from Jackson is the natural next constraint
  to combine with the Cheng--Keevash structure. The Jackson statement should
  be confirmed against the 1981 primary source before being used in a
  publishable proof.

## Implication for the search project

The first computational pass for $k = 3$, scheduled in the plan with budgets
$2, 4, 12, 24, 48$ wall-clock hours per $n \in \{8, 9, 10, 11, 12, 13, 14\}$,
is now unnecessary for a counterexample search: $k = 3$ is settled.

The first genuinely open case is $\delta = 4$, where Cheng--Keevash gives
$\ell \geq 7$ and Conjecture 1 wants $\ell \geq 8$. The hand attack should
move to $\delta = 4$, $n = 10$ next.
