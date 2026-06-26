# CRUX-A / L-exist: structural proof attempt

Date: 2026-06-11

Status: partial advance, not a proof.  The funnel geometry simplifies
substantially, and a strict subtree-decrease move is proved in all cases
except a specific gateway configuration.  The chord-contraction
hypothesis is essential: the analogous statement for arbitrary
3-arc-strong multidigraphs is false even in the intermediate-cut regime.
There is also an explicit boundary obligation: iteration of the shrink
move may reach \(|X|=1\), where the strict-exit property is impossible,
and the separate RECOLOR leaf case has not been proved.

## 1. Scope and notation

Let \(D\) be a directed multigraph, let \(r\) be a root, and let
\(T,U\) be arc-disjoint spanning in-arborescences rooted at \(r\).
For \(a=(u,v)\in T\), write

\[
X=X_a^T
\]

for the \(T\)-subtree below \(a\).  Thus \(r\notin X\), \(u\in X\),
and

\[
T\cap\delta^+(X)=\{a\}.
\]

The concrete `L-exist` formulation in `paper/findings.md` takes
\(r=v=\operatorname{head}(a)\) and asks for the existence of such a
pair.  The original RECOLOR application instead has a previously fixed
root (the contracted vertex) and an arbitrary internal arc \(a\).
The local lemmas below apply to either formulation once a pair
\((T,U)\) containing \(a\) is available, but the two global
quantifier statements are not the same; see Section 8.

Only the intermediate range

\[
2\le |X|\le |V(D)|-2
\]

is considered below.

## 2. Exact characterization of a funnel failure

The existing notes allow several \(U\)-exits whose subtrees all
contain \(X\).  This cannot occur.

**Lemma 2.1 (one-exit criterion).**  Let \(U\) be an in-arborescence
rooted at \(r\), and let \(\varnothing\ne X\subseteq V(D)\setminus
\{r\}\).  The following are equivalent.

1. No \(b\in U\cap\delta^+(X)\) satisfies
   \(X_b^U\cap X\subsetneq X\).
2. \(|U\cap\delta^+(X)|=1\).

**Proof.**
Every \(U\)-walk from \(X\) to \(r\) exits \(X\), so the exit set is
nonempty.

If the exit set is \(\{b\}\), every \(x\in X\) has a \(U\)-walk to
\(r\) using \(b\).  Hence \(X\subseteq X_b^U\), so
\(X_b^U\cap X=X\).

Conversely, suppose no exit gives strict inclusion.  Then
\(X\subseteq X_b^U\) for every exit \(b\).  If
\(b_i=(t_i,s_i)\), \(i=1,2\), are two exits, then \(t_2\in X\subseteq
X_{b_1}^U\), so \(t_2\) is a \(U\)-descendant of \(t_1\).  Symmetrically
\(t_1\) is a \(U\)-descendant of \(t_2\).  Antisymmetry of the ancestor
relation gives \(t_1=t_2\).  A non-root vertex has one \(U\)-out-arc,
so \(b_1=b_2\).  This remains true for multidigraphs: although parallel
copies are distinct arcs, an arc-set in-arborescence chooses exactly one
out-arc at each non-root vertex.  Thus there is exactly one exit.
\(\square\)

Consequently, the desired strict-subtree exit is equivalent to

\[
|U\cap\delta^+(X)|\ge 2. \tag{2.1}
\]

In particular, the multi-exit alternating funnel described in
`team/31_conjecture_L_proof_attempt.md` Section 3.3 and
`paper/draft_v1.md` Section 6.2 is not a possible failure mode.

## 3. The free third exit

**Lemma 3.1 (free-exit lemma).**  Suppose \(D\) is 3-arc-strong and
\(U\) fails (2.1) on the \(T\)-subtree \(X=X_a^T\).  Then

\[
\delta^+(X)\setminus (T\cup U)\ne\varnothing.
\]

**Proof.**
We have \(T\cap\delta^+(X)=\{a\}\), while Lemma 2.1 gives
\(U\cap\delta^+(X)=\{b\}\).  The two arcs are distinct because
\(T\cap U=\varnothing\).  Since \(|\delta^+(X)|\ge 3\), a third arc is
outside \(T\cup U\).  \(\square\)

This removes the purported tight case
\(|U\cap\delta^+(X)|=2\) with no free arc: if there are two \(U\)-exits,
the desired conclusion already holds.

## 4. A rigorous subtree-shrink move

Let \(c=(w,z)\in\delta^+(X)\setminus(T\cup U)\) be a free exit.

**Lemma 4.1 (shrink away from the distinguished tail).**  If
\(w\ne u=\operatorname{tail}(a)\), let \(e_w\) be the unique
\(T\)-out-arc of \(w\), and put

\[
T'=T-e_w+c.
\]

Then \(T'\) is an in-arborescence rooted at \(r\), it is arc-disjoint
from \(U\), it still contains \(a\), and

\[
X_a^{T'}=X\setminus X_{e_w}^T\subsetneq X. \tag{4.1}
\]

**Proof.**
The \(T\)-subtree \(X_{e_w}^T\) is contained in \(X\), whereas
\(z\notin X\).  Moreover, the \(T\)-path from \(z\) to \(r\) avoids
\(X\): if it entered \(X\), it would later leave through the unique
\(T\)-exit \(a\), so the \(T\)-path from \(z\) would use \(a\), which
would put \(z\) in \(X=X_a^T\), a contradiction.  Replacing the parent
arc of \(w\) by \(c=(w,z)\) therefore creates no directed cycle and
reconnects the whole subtree at \(w\) to the root side of \(T-a\).
The new arc is free, so arc-disjointness from \(U\) is preserved.
Exactly the vertices of \(X_{e_w}^T\) cease to use \(a\), proving
(4.1).  \(\square\)

Thus a failing pair can be replaced by a good pair immediately if
\(U\) has two exits from the smaller set in (4.1); otherwise the
failure has moved to a strictly smaller \(a\)-subtree.  Iteration
terminates either at a good pair, at the singleton boundary
\(X=\{u\}\), or at a set for which every free exit has tail \(u\).

The singleton outcome is not a success: no strict exit can exist from
a singleton.  The earlier RECOLOR notes refer to separate leaf
casework, but `team/30_route_c1_termination.md` Sections 5.3 and 7.2
explicitly leave its leaf/non-leaf closure incomplete.  Thus Lemma 4.1
proves strict progress away from the gateway, but a complete iteration
still requires either that boundary casework or a potential that
prevents singleton termination.

## 5. The remaining gateway configuration

After exhaustive use of Lemma 4.1, the only unresolved configuration
has

\[
U\cap\delta^+(X)=\{b\},\qquad
\delta^+(X)\setminus(T\cup U)\subseteq\delta^+(u). \tag{5.1}
\]

Write \(b=(t,y)\).

If \(t\ne u\), the \(U\)-out-arc of \(u\) is internal to \(X\).
For a free arc \(c=(u,z)\), replacing that internal arc by \(c\)
would create the required two exits \(b,c\), provided

\[
z\notin X_u^U. \tag{5.2}
\]

Indeed, let \(e_u\) be the \(U\)-out-arc of \(u\) and set
\(U'=U-e_u+c\).  Since \(z\notin X_u^U\), this replacement creates no
cycle; every vertex still reaches \(r\).  The added arc is free, so
\(U'\) remains arc-disjoint from \(T\).  Since \(t\ne u\), the old
exit \(b\) survives, and \(b,c\) are two distinct \(U'\)-exits from
\(X\).  Lemma 2.1 finishes the repair.  This proves the general
safe-target swap directly; it is broader than the parallel-free-arc
example closed in `team/31_conjecture_L_proof_attempt.md` Section 4.4.

The residual is therefore:

* every free \(c=(u,z)\) has \(z\in X_u^U\setminus X\); or
* \(t=u\), in which case changing the unique \(U\)-out-arc of \(u\)
  merely replaces one exit by another.

The first alternative is a genuine directed-cycle obstruction, not
a lack of cut capacity.  It calls for a two-arc cycle push.

## 6. A closed two-arc cycle-push subcase

Assume \(t\ne u\).  Let \(p\) be the \(U\)-parent of \(u\), let
\(c=(u,z)\) be a free exit with \(z\in X_u^U\setminus X\), and write
the \(U\)-path from \(z\) to \(u\) as

\[
z=v_0\to v_1\to\cdots\to v_k=u.
\]

**Lemma 6.1 (two-arc push).**  If \(d=(z,p)\) is an arc outside
\(T\cup U\), then

\[
U'=U-\{(u,p),(z,v_1)\}+\{(u,z),(z,p)\}
\]

is an in-arborescence rooted at \(r\), is arc-disjoint from \(T\),
and has at least the two exits \(b\) and \(c\) from \(X\).

**Proof.**
The replacement changes only the out-arcs of \(u\) and \(z\).  The
old path segment \(z\to\cdots\to u\to p\) is replaced by
\(v_1\to\cdots\to u\to z\to p\), while \(z\) no longer points to
\(v_1\).  Here \(v_1\ne p\): \(p\) is a strict \(U\)-ancestor of
\(u\), whereas \(v_1\) is a \(U\)-descendant of \(u\); equality would
create a directed cycle in \(U\).  Hence no directed cycle is created
and every vertex still reaches \(r\).

Both added arcs avoid \(T\).  The exit \(b\) survives: because
\(t\ne u\), it is not \((u,p)\), and it is not \((z,v_1)\) because
its tail \(t\) lies in \(X\) whereas \(z\notin X\).  Thus \(b\) and
\(c\) are two distinct \(U'\)-exits from \(X\).  Lemma 2.1 gives the
desired strict exit.  \(\square\)

There is a useful chord-contraction instance of this lemma.  Let
\(K=V_2\) denote the simple semicomplete part.  If \(z,p\in K\),
\(p\ne t\), and (5.1) holds, then \(p\to z\) cannot be present:
it would be an exit from \(X\) with tail \(p\ne u,t\).  Semicompleteness
therefore forces \(z\to p\).  This arc is not in \(T\), since otherwise
\(z\) would already be a \(T\)-descendant of \(u\), and it is not in
\(U\), since \(p\) is a strict \(U\)-ancestor of \(u\) while \(z\) is
a \(U\)-descendant of \(u\).  Hence Lemma 6.1 applies.

What remains after Lemma 6.1 consists of configurations where the
relevant vertices meet the independent side of the split
multidigraph, where \(p=t\), or where \(t=u\).  These are precisely
the cases in which semicompleteness alone does not supply the
cycle-breaking arc \(z\to p\).

The gateway also forces a useful domination pattern inside the
semicomplete part.  Let \(K=V_2\).  For

\[
k_1\in (K\cap X)\setminus\{u,t\},\qquad k_2\in K\setminus X,
\]

the arc \(k_1\to k_2\) would be an exit from \(X\).  It cannot be the
unique \(T\)-exit \(a\), the unique \(U\)-exit \(b\), or a free exit
allowed by (5.1), because its tail is neither \(u\) nor \(t\).
Therefore it is absent, and semicompleteness forces
\(k_2\to k_1\).  Hence \(K\setminus X\) fully in-dominates
\((K\cap X)\setminus\{u,t\}\).  This rigid bipartition is a concrete
remaining handle on the cases \(t=u\) and \(p=t\); the separate regime
\(K\cap X\subseteq\{u,t\}\) must instead use the independent-side or
labelled two-preimage structure at the contracted root.

## 7. Why the chord-contraction hypothesis is essential

The intermediate-cut statement is false for arbitrary
3-arc-strong multidigraphs.

Let \(D\) have vertices \(\{0,1,2,3\}\).  For each edge of the
undirected path

\[
1-0-2-3
\]

put three parallel arcs in each direction.  Every nontrivial directed
cut has size at least three, so \(D\) is 3-arc-strong.

Take \(a\) to be any copy of \(0\to2\), and root at
\(r=2=\operatorname{head}(a)\).  In every in-arborescence \(T\)
containing \(a\), vertex \(1\) must route through \(0\), while vertex
\(3\) routes directly to \(2\).  Therefore

\[
X_a^T=\{0,1\},
\]

which is intermediate.  Every arc leaving \(\{0,1\}\) has tail \(0\).
Consequently every in-arborescence \(U\) has exactly one exit from
\(\{0,1\}\), and Lemma 2.1 shows that no pair can satisfy L-exist.

This is machine-confirmed by `scripts/lexist_path_counterexample.py`.
The oracle reports \(\lambda(D)=3\), and there are 27 spanning
in-arborescences rooted at \(2\).  For each fixed labelled copy of
\(0\to2\), there are 72 ordered arc-disjoint pairs with that copy in
\(T\), all failing; aggregating over the three possible copies gives
216 pairs and zero strict exits.  The multidigraph is Eulerian, since
every support edge is replaced by the same number of arcs in each
direction.  Thus Eulerianness does not rescue general L-exist.

This graph is not a chord contraction of the near-split type: on four
vertices such a contraction has a semicomplete part of size at least
three, whereas the support graph above has no semicomplete
three-vertex induced subdigraph.

Thus any complete proof must use the semicomplete/split structure
and, possibly, the labelled two-preimage constraints at the contracted
vertex.  A proof from 3-arc-strongness alone is impossible.

## 8. Quantifier and payoff caveat

The concrete L-exist statement currently implemented by
`scripts/check_lexist.py` roots both arborescences at
\(\operatorname{head}(a)\).  The RECOLOR argument in
`team/29_route_c1_recoloring.md` and
`team/30_route_c1_termination.md` uses arborescences rooted at the
fixed contracted vertex and applies the subtree step to an arbitrary
internal shared arc.

Therefore a proof of the current head-rooted L-exist statement does
not, by itself, make the near-split theorem unconditional.  Sections
10 and 11 avoid this mismatch by formulating the candidate directly
for pairs rooted at the contracted vertex.  Proving that fixed-root
statement, including availability of the required pair for each
processed arc, would remove the need for a rerooting argument.

The dedicated `scripts/check_lexist_fixedroot.py` checker uses that
fixed root and filters explicitly to the intermediate regime.  Its
finite survival result is recorded in Section 11; it is evidence, not
a proof.

There is a second payoff dependency: a Lemma 4.1 sequence can reach
\(|X|=1\).  The strict-exit statement then becomes impossible, and
the leaf/non-leaf RECOLOR closure cited in earlier status text is not
proved; `team/30_route_c1_termination.md` explicitly records this gap.
Any unconditional near-split theorem therefore still needs a written
singleton boundary argument in addition to the fixed-root intermediate
statement.

## 9. Current proof frontier

The following statements are now proved:

1. A funnel failure is exactly a one-exit event.
2. Every failure has a free third exit.
3. A free exit whose tail is not \(\operatorname{tail}(a)\) strictly
   shrinks the \(a\)-subtree while preserving the pair.
4. A safe free exit at \(\operatorname{tail}(a)\) repairs \(U\)
   directly.
5. A semicomplete two-arc push repairs a substantial unsafe-target
   subcase.
6. The path-pivot exchange of Lemma 10.1 repairs any gateway with the
   two stated \(K\)-pivots.
7. Every gateway has exit tails in \(\{u,t\}\), both sides of the
   \(K\)-wedge are nonempty, and the outside side fully in-dominates
   the inside side.

The primary unresolved symbolic core is the Candidate Irreducible
Gateway Emptiness Lemma:

* \(t=u\);
* every free target lying in \(X_u^U\setminus X\); and
* preventing or closing singleton termination of the shrink iteration.

The preferred route is to prove that every gateway is safely
repairable.  If this is false, Section 10 gives the fallback: force
the two \(K\)-pivots by a secondary well-founded potential and apply
the path-pivot exchange.

## 10. Candidate fixed-root gateway lemma

The following formulation isolates a single chord-contraction-specific
claim.  It also avoids using \(p\) both for an endpoint of the original
chord and for the \(U\)-parent of \(u\).

Let \(D^\bullet\) be the chord contraction of a simple
3-arc-strong \((1,0)\)-near-split digraph.  Write

\[
V(D^\bullet)=I\mathbin{\dot\cup}K,
\]

where \(I\) is independent, \(K\) is simple semicomplete, and
\(\rho\in I\) is the contracted vertex.  Fix \(\rho\) as the root and
fix an arc \(a=(u,v)\).  Consider only arc-disjoint pairs
\((T,U)\) of spanning in-arborescences rooted at \(\rho\), with
\(a\in T\).

Suppose, for contradiction, that this fixed-root family is nonempty
but contains no good pair, and that some member has
\(2\le |X_a^T|\le |V(D^\bullet)|-2\).  Thus every eligible pair is a
failing pair.  Choose one, put \(X=X_a^T\), and normalize it by:

1. minimizing \(|X|\);
2. subject to that, maximizing the \(U\)-distance from \(u\) to the
   unique exit tail \(t\);
3. subject to that, minimizing the number of \(I\)-vertices on the
   relevant unsafe \(U\)-cycle interval, over all free exits
   \(c=(u,z)\).

Here the first minimization is understood after the separate leaf
lemma has discharged a possible \(|X|=1\) endpoint.  Lemma 4.1 then
puts the pair in the gateway

\[
U\cap\delta^+(X)=\{b=(t,y)\},\qquad
\delta^+(X)\setminus(T\cup U)\subseteq\delta^+(u). \tag{10.1}
\]

For a free unsafe exit \(c=(u,z)\), write \(zUu\) for the directed
\(U\)-path from \(z\) to \(u\), and \(uUt\) for the directed
\(U\)-path from \(u\) to \(t\).  More precisely, the third coordinate
is

\[
\iota(T,U)=\min_c\left|I\cap
\left(V(zUu-u)\cup V(uUt-\{u,t\})\right)\right|,
\]

where the minimum is over the free unsafe exits \(c=(u,z)\).

**Candidate Gateway Lemma (fixed-root \(K\)-pivot form).**  A
normalized failing intermediate pair satisfying (10.1) has a free
unsafe exit \(c=(u,z)\) and vertices

\[
q\in (K\setminus X)\cap V(zUu-u),\qquad
h\in (K\cap X)\cap V(uUt-\{u,t\}). \tag{10.2}
\]

Thus \(q\) is a semicomplete-side vertex on the descendant part of the
unsafe cycle, while \(h\) is a semicomplete-side vertex strictly
between \(u\) and the unique exit tail \(t\).

The content of the candidate is exactly the elimination, by
root-preserving exchanges that improve the normalization potential, of
the three residual patterns:

* \(t=u\), when the second set in (10.2) is empty;
* the \(U\)-parent of \(u\) equals \(t\), when it is again empty; and
* an independent-side obstruction, when one of the two required
  path intervals contains only \(I\)-vertices at the possible pivot
  positions.

Independence of \(I\) forces every nontrivial \(I\)-run on a \(U\)-path
to be separated by \(K\)-vertices.  The proposed proof obligation is
to use those adjacent \(K\)-vertices to increase
\(\operatorname{dist}_U(u,t)\) or decrease the number of
\(I\)-vertices on the unsafe interval.  If such a move reaches
\(\rho\), the labelled two-preimage degree reserves at \(\rho\) are
the intended final source of an unused attachment.  All other moves
should avoid arcs incident with \(\rho\), so the fixed root and its
side labels remain unchanged.

The payoff of (10.2) is immediate from the already proved
in-domination wedge.

**Lemma 10.1 (path-pivot repair).**  If a gateway pair has
\(c,q,h\) as in (10.2), then it can be repaired by a two-arc exchange
in \(U\).

**Proof.**
Let \(m\) be the \(U\)-parent of \(u\), and let \(q^+\) be the
\(U\)-parent of \(q\).  Since

\[
q\in K\setminus X,\qquad
h\in (K\cap X)\setminus\{u,t\},
\]

the in-domination wedge forces \(q\to h\).  This arc is not in \(T\):
otherwise the \(T\)-path from \(q\) would enter \(X\) at \(h\), use
the unique \(T\)-exit \(a\), and put \(q\) in \(X\).  It is not in
\(U\), since the \(U\)-out-arc of \(q\) is \(q\to q^+\), while
\(q^+\) lies at or below \(u\) on \(zUu\) and \(h\) is strictly above
\(u\) on \(uUt\).

Set

\[
U'=U-\{(u,m),(q,q^+)\}+\{(u,z),(q,h)\}. \tag{10.3}
\]

The exchange cuts the old cycle interval between \(q\) and \(q^+\).
The old segment

\[
z\longrightarrow\cdots\longrightarrow q\longrightarrow q^+
\longrightarrow\cdots\longrightarrow u\longrightarrow m
\longrightarrow\cdots\longrightarrow h
\]

is replaced by

\[
q^+\longrightarrow\cdots\longrightarrow u\longrightarrow z
\longrightarrow\cdots\longrightarrow q\longrightarrow h.
\]

Hence every vertex still reaches \(\rho\), and no directed cycle is
created.  Both added arcs avoid \(T\), so \(U'\) is arc-disjoint from
\(T\).  The existence of \(h\) implies \(t\ne u\), and \(q\notin X\);
therefore neither removed arc is \(b\).  Thus both \(b\) and
\(c=(u,z)\) are \(U'\)-exits from \(X\), and Lemma 2.1 gives a strict
exit.

The exchange leaves \(T\), \(a\), and the root fixed.  Here \(u,m,h\)
lie in \(X\), while \(z,q,q^+\) lie on a \(U\)-path that reaches \(u\)
before reaching the root.  Thus no changed arc is incident with
\(\rho\), and the exchange does not alter a labelled arc at the
contracted root.  \(\square\)

Consequently, the candidate gateway lemma, the singleton leaf lemma,
and no additional rerooting argument would prove the fixed-root
intermediate L-exist statement needed by RECOLOR.  The tripled-path
counterexample from Section 7 fails precisely at (10.2): there
\(t=u\), and there is no semicomplete-side interior pivot \(h\).

## 11. Gateway red-team and the stronger surviving target

The first fixed-root checker version appeared to report that no
failing pair in the tested chord contractions was a gateway pair.
That diagnostic was not exhaustive: after finding the first good pair
for an arc, it broke out of the pair-enumeration loops.  Its
`failing_pairs` and `gateway_pairs` counters therefore described only
the prefix before that good pair.

Raw gateway emptiness is false even on the tested population.  Here is
a six-vertex chord-contraction witness.  Let

\[
I=\{0,1\},\qquad K=\{2,3,4,5\},\qquad \rho=0,
\]

and let the arcs, with multiplicities shown as exponents, be

\[
\begin{aligned}
&0\to2,\ 0\to3,\ (0\to4)^2,\ (0\to5)^2,\\
&1\to2,\ 1\to3,\ 1\to4,\\
&2\to0,\ 2\to1,\ 2\to4,\\
&3\to1,\ 3\to2,\ 3\to4,\\
&(4\to0)^2,\ 4\to1,\ 4\to3,\ 4\to5,\\
&(5\to0)^2,\ 5\to2,\ 5\to3.
\end{aligned} \tag{11.1}
\]

This multidigraph has \(\lambda=3\).  Take \(a=(4,5)\) and

\[
\begin{aligned}
T&=\{1\to2,\ 2\to4,\ 3\to1,\ 4\to5,\ 5\to0\},\\
U&=\{1\to3,\ 2\to0,\ 3\to2,\ 4\to1,\ 5\to0\},
\end{aligned}
\]

using different copies of \(5\to0\).  Then

\[
X_a^T=\{1,2,3,4\},\qquad
U\cap\delta^+(X)=\{2\to0\},
\]

and every free exit is a copy of \(4\to0\).  Thus this is a failing
gateway pair with \(u=4\) and \(t=2\).  It is not an obstruction:
\(0\notin X_4^U\), so \(4\to0\) is a safe target and the Section 5
swap repairs it immediately.

The corrected exhaustive diagnostic distinguishes such pairs from
the genuinely unresolved gateways.  It suggests the following
replacement for raw gateway emptiness.

Across the six tested cells
\((2,3),(3,3),(2,4),(2,5),(3,4),(4,3)\), the corrected run examined
1,075 distinct contractions and 18,927 arcs.  Fixed-root L-exist had
zero failures.  Lemma 2.1 had zero violations in 84,380,752 pair
checks.  Among 15,928,977 failing intermediate pairs there were
exactly 282 gateways: all 282 were safe-target repairable, and zero
were irreducible.

**Candidate Irreducible Gateway Emptiness Lemma.**  Let \(D^\bullet\)
be a 3-arc-strong chord contraction, rooted at its contracted vertex
\(\rho\).  If a fixed-root arc-disjoint pair \((T,U)\), with
\(a=(u,v)\in T\) and \(2\le |X_a^T|\le n-2\), is failing and satisfies
the gateway condition (5.1), then \(t\ne u\) and there is a free exit

\[
c=(u,z)\qquad\text{with}\qquad z\notin X_u^U. \tag{11.2}
\]

Equivalently, every gateway is already in the safe-target subcase of
Section 5.  If this candidate holds, Lemma 4.1 and the safe-target
swap close every intermediate fixed-root pair; Section 10 remains the
fallback if an irreducible gateway exists at larger scope.

Two structural reductions toward (11.2) are already rigorous.

**Lemma 11.1 (two-tail concentration).**  In any gateway pair,
every arc of \(\delta^+(X)\) has tail in \(\{u,t\}\).  If \(t\ne u\),
then \(b=(t,y)\) is the only arc of \(D^\bullet\) leaving \(X\) with
tail \(t\), counted with multiplicity.

**Proof.**
The only \(T\)-exit is \(a\), with tail \(u\); the only \(U\)-exit is
\(b\), with tail \(t\); and (5.1) puts every free exit at \(u\).
Every arc is in \(T\), in \(U\), or free.  This proves the first
claim.  If \(t\ne u\), a second exit at \(t\) could be neither \(a\)
nor \(b\), hence would be a free exit with tail different from \(u\),
contrary to (5.1).  \(\square\)

**Lemma 11.2 (both sides of the \(K\)-wedge are nonempty).**  In a
gateway pair,

\[
K\setminus X\ne\varnothing,\qquad
(K\cap X)\setminus\{u,t\}\ne\varnothing. \tag{11.3}
\]

**Proof.**
Suppose first that \(K\subseteq X\).  Since \(X\) is intermediate and
\(\rho\notin X\), there is a vertex
\(y\in I\setminus(X\cup\{\rho\})\).  All in-arcs of \(y\) come from
\(K\), because \(I\) is independent.  Every such arc leaves \(X\),
so Lemma 11.1 says its tail is \(u\) or \(t\).  Arcs into
\(y\ne\rho\) have multiplicity one in a chord contraction.  Hence
\(d^-(y)\le2\), contradicting 3-arc-strongness.

Now suppose \((K\cap X)\setminus\{u,t\}=\varnothing\).  If
\(x\in X\setminus\{u,t\}\), then \(x\in I\).  All its out-arcs go to
\(K\), and Lemma 11.1 forbids it from sending an arc outside \(X\).
Thus all its out-neighbors lie in
\(K\cap X\subseteq\{u,t\}\).  These arcs have multiplicity one, so
\(d^+(x)\le2\), again impossible.  Therefore \(X\subseteq\{u,t\}\).
The intermediate lower bound gives \(X=\{u,t\}\) and \(u\ne t\).
By Lemma 11.1, \(t\) has only the single external out-arc \(b\), and
inside \(X\) it has at most the simple arc \(t\to u\).  Hence
\(d^+(t)\le2\), a final contradiction.  \(\square\)

Combining Lemma 11.2 with the earlier wedge gives the nonvacuous
domination

\[
K\setminus X\ \longrightarrow\
(K\cap X)\setminus\{u,t\}. \tag{11.4}
\]

Thus the remaining proof of (11.2) is sharply localized: use (11.4),
the \(U\)-ancestor geometry, and the independent-side degree
constraints to rule out \(t=u\) and the case in which every free
target belongs to \(X_u^U\setminus X\).  The path-pivot lemma of
Section 10 already repairs the latter whenever the two required
\(K\)-pivots occur.
