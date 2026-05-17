# 22 - R3-star inspection of the BJ-Wang construction

Date: 2026-05-17.

Role: Structural Specialist for the Bang-Jensen--Yeo near-split route.

Scope of this memo: inspect whether the residual un-contraction claim
R3-star in `team/21_near_split_contraction_proof.md` can be closed by a
direct inspection of Bang-Jensen--Wang 2025, specifically Lemma 2.4,
Lemma 2.5, Corollary 2, and the proof of Corollary 1 / Theorem 1.6.

Local sources inspected:

- `team/21_near_split_contraction_proof.md`, especially Sections 3.4,
  4.1--4.6, and 7.1.
- `team/05_audit.md`, especially Appendix A, Appendix A.5 Source 1,
  and Appendix A.8.
- `/tmp/bjwang2025.txt`, especially lines around Lemma 2.4, Lemma 2.5,
  Corollary 2, and the proof of Theorem 1.6.

## 1. Verdict

R3-star does **not** close by merely inspecting the published
Bang-Jensen--Wang construction.

The reason is precise. The BJ-Wang proof constructs a strong arc
decomposition of the contracted split multi-digraph \(D^\bullet\), but
the construction is blind to the two preimages \(p,q\) of the contracted
vertex \(p^\bullet\). It treats \(p^\bullet\) as an ordinary shell
vertex. The proof never tracks whether an incident labelled arc of
\(p^\bullet\) came from \(p\) or from \(q\). The needed un-contraction
property is exactly a constraint on those labels. Hence it is invisible
to the BJ-Wang invariant.

This is not evidence that R3-star is false. It says only that Route
(a), "close R3-star by BJ-Wang algorithm inspection", fails as a
complete proof. The next proof obligation is a side-aware coloring
lemma, either as a strengthening of the BJ-Wang construction or as a
separate SAD-coloring polytope lemma.

There is also a small correction to `team/21`: the last equivalence in
Section 4.5, "some SAD of \(D^\bullet\) has a \(q\)-reaching color",
is weaker than the actual liftability condition unless the other color
is already known to be good. No proof of that extra implication appears
in the inspected files.

## 2. Precise restatement of R3-star

Let \(D=(V,A)\) be a simple 3-arc-strong \((1,0)\)-near-split digraph
with split partition \(V=V_1\dot\cup V_2\), unique \(V_1\)-internal arc
\(e_0=(p,q)\), and \(|V_2|\ge 3\). Let \(D^\bullet\) be obtained by
contracting \(p,q\) to a single vertex \(r=p^\bullet\) and deleting the
loop image of \(e_0\). The contracted digraph is a split multi-digraph:
\[
V_1^\bullet=(V_1\setminus\{p,q\})\cup\{r\},\qquad V_2^\bullet=V_2.
\]

For a SAD \((A_1^\bullet,A_2^\bullet)\) of \(D^\bullet\), define
\[
D_i^\flat=(V,\pi^{-1}(A_i^\bullet))
\]
inside \(D-e_0\). Say:

- \(P_i\): \(D_i^\flat\) contains a directed \(p\to q\) path.
- \(Q_i\): \(D_i^\flat\) contains a directed \(q\to p\) path.
- Color \(i\) is **good** iff \(P_i\) and \(Q_i\) both hold.

Adding \(e_0=(p,q)\) to color \(i\) supplies \(P_i\) automatically, but
does not supply \(Q_i\). Therefore the exact liftability condition is:

\[
\exists i\in\{1,2\}\quad Q_i\ \text{and}\ P_{3-i}\ \text{and}\ Q_{3-i}.
\]

Equivalently:

\[
(Q_1\wedge P_2\wedge Q_2)\quad\text{or}\quad(Q_2\wedge P_1\wedge Q_1).
\]

This is the precise R3-star target. A merely \(q\)-reaching color is
not enough unless the opposite color is also good.

### Direction bookkeeping

For a color \(i\), a clean \(q\to p\) witness after un-contraction is a
closed walk through \(r\) in \(A_i^\bullet\) which:

1. leaves \(r\) along a labelled arc whose preimage leaves \(q\), say
   \(q\to x\), and
2. returns to \(r\) along a labelled arc whose preimage enters \(p\),
   say \(y\to p\).

Similarly, a clean \(p\to q\) witness leaves \(r\) along an arc whose
preimage leaves \(p\), and returns along an arc whose preimage enters
\(q\).

This matters because `team/21` Section 4.5 phrases the informal witness
with an in-arc whose preimage is \((v,q)\) and an out-arc whose preimage
is \((p,w)\). That pair witnesses \(p\to q\), not \(q\to p\). The formal
definitions in Section 4.2 are correct; the informal sentence in
Section 4.5 is direction-swapped.

## 3. What BJ-Wang Lemma 2.4 actually constructs

BJ-Wang Lemma 2.4 is the kernel-shell glue lemma. In the notation of
the paper:

- \(D\) is a directed multigraph.
- \(X\subseteq V(D)\).
- Every shell vertex \(x\in D-X\) has two in-neighbors and two
  out-neighbors in \(X\).
- \(D[X]\) has a SAD \((A_1,A_2)\).

The construction is:

1. for each shell vertex \(x\), choose two in-neighbors
   \(x_1^-,x_2^-\in X\) and two out-neighbors \(x_1^+,x_2^+\in X\);
2. add \(x_i^-x\) and \(xx_i^+\) to color \(i\), for \(i=1,2\);
3. distribute any unused arcs arbitrarily, since adding arcs to an
   already strong color preserves strong connectivity.

The proof is correct because color \(i\) can go from \(x\) into the
strong kernel \(X\) by \(xx_i^+\), move inside \(A_i[X]\), and return
to \(x\) by \(x_i^-x\).

For the contracted near-split digraph \(D^\bullet\), take
\(X=V_2\). The shell vertex \(r=p^\bullet\) has incident labelled arcs
of four kinds:

- \(R_p^+\): arcs \(r\to x\) whose preimage is \(p\to x\);
- \(R_q^+\): arcs \(r\to x\) whose preimage is \(q\to x\);
- \(R_p^-\): arcs \(x\to r\) whose preimage is \(x\to p\);
- \(R_q^-\): arcs \(x\to r\) whose preimage is \(x\to q\).

Lemma 2.4 sees only arcs \(r\to x\) and \(x\to r\). It does not see the
labels \(p\) and \(q\). Thus it guarantees one in-arc and one out-arc
of \(r\) in each color, but it does not guarantee that either color gets
the side-compatible pair
\[
R_q^+\ \text{and}\ R_p^-
\]
needed for \(q\to p\), nor that the other color gets both side-compatible
pairs needed to be good.

### Partial positive statement

If \(D^\bullet[V_2]\) itself has a SAD and one is allowed to choose the
Lemma 2.4 attachment arcs and all leftover incident arcs deliberately,
then the degree surplus at \(p,q\) often gives enough room to force a
liftable attachment pattern at \(r\). This is a useful special case.

It does **not** close R3-star, because BJ-Wang Corollary 1 is needed
exactly when \(D^\bullet[V_2]\) need not have a SAD. In the hard cases
the proof first creates a new semicomplete multi-digraph on \(V_2\) by
splitting off paths through shell vertices. The side labels at \(r\)
then enter through lifted splitting arcs, not merely through the simple
Lemma 2.4 attachment step.

## 4. What BJ-Wang Corollary 1 actually constructs

BJ-Wang Corollary 1 follows from Theorem 1.6. The proof spine is:

1. Work with a split digraph \(D=(V_1,V_2;A)\) where \(V_1\) is
   independent, \(D[V_2]\) is semicomplete, and each \(V_1\)-vertex has
   in- and out-degree at least 3.
2. If \(D[V_2]\) is already favorable, apply the kernel-shell machinery.
3. Otherwise choose a set \(Q\) of arc-disjoint paths with endpoints in
   \(V_2\) and internal vertices in \(V_1\), split off those paths, and
   obtain a directed multigraph \(D_Q[V_2]\).
4. Use the semicomplete multi-digraph SAD characterization on
   \(D_Q[V_2]\), or handle the exceptional \(S_4\)-type multigraphs by
   Lemma 2.7.
5. Lift splitting arcs back through the corresponding \(V_1\)-vertices
   as in Lemma 2.5.
6. Add spare in/out arcs to colors missing a shell vertex, and finally
   absorb any remaining shell vertices by Lemma 2.4.

The key lifting step is Lemma 2.5. After a SAD of \(D^*[V_2]\) is
chosen, the splitting arcs are lifted. This creates two strong
subdigraphs \(D_1,D_2\), each covering \(V_2\). For a shell vertex
\(t\in V(D_i)\setminus V(D_{3-i})\), the proof adds one unused in-arc
and one unused out-arc of \(t\) to the other color. Then Lemma 2.4
absorbs the still-uncovered shell vertices.

This proves a SAD of the original split digraph. It does not prove a
side-compatible SAD for an un-contracted near-split digraph.

## 5. The exact failure point

The failure point is Lemma 2.5's spare-arc step, plus its reuse in the
final proof of Theorem 1.6.

For an ordinary split digraph, all that matters is that each color gets
enough in/out incidence to make the shell vertex strongly attached to
the \(V_2\)-kernel. For the contracted vertex \(r=p^\bullet\), that is
not enough. A color may be strongly attached to \(V_2\) in
\(D^\bullet\) while, after un-contraction, all of its closed walks
through \(r\) become only \(p\to p\), only \(q\to q\), or only
\(p\to q\) motion. Such a color is strong before un-contraction and
non-strong after un-contraction.

The BJ-Wang proof never excludes this. More concretely:

- The choice of the path set \(Q\) is governed by the acyclic ordering
  and nice decomposition of \(D[V_2]\), and by the minimization of
  \(|W_Q^+|+|W_Q^-|\). It has no constraint involving a distinguished
  shell vertex \(r\) or side labels \(p,q\).
- The semicomplete multi-digraph theorem supplies a SAD of
  \(D_Q[V_2]\). It does not control which color receives which
  splitting arcs incident with \(r\).
- When splitting arcs are lifted in Lemma 2.5, the proof only preserves
  strong connectivity in the contracted split sense.
- If \(r\) lies in only one of \(D_1,D_2\), the proof adds an arbitrary
  unused in/out pair of \(r\) to the other color. It does not require
  the pair to be \(R_q^+\) with \(R_p^-\), or \(R_p^+\) with \(R_q^-\).
- If \(r\) lies in both \(D_1\) and \(D_2\), the spare-arc mechanism need
  not fire at all. This is explicitly relevant in the final
  Theorem 1.6 proof, where the special vertices \(t,t'\) can lie in
  both colors after the extra splitting paths \(Q'\).
- Lemma 2.7 handles exceptional semicomplete multi-digraph kernels by
  constructing cycles and applying Lemma 2.4. Those cycles are also
  side-blind after substituting \(r=p^\bullet\).

Therefore the BJ-Wang construction may well produce a liftable SAD in
all near-split instances, but the published proof does not contain the
invariant needed to certify that fact.

## 6. Consequence for Route B

The current proof of the 3-arc-strong \((1,0)\)-near-split theorem
remains conditional. The conditional statement should not say "modulo
some \(q\)-reaching color"; it should say "modulo existence of a
liftable SAD", where liftable means:

\[
\exists i\in\{1,2\}\quad
D_i^\flat+e_0\ \text{is strong and}\ D_{3-i}^\flat\ \text{is strong}.
\]

Equivalently, using the \(P_i,Q_i\) notation:

\[
\exists i\quad Q_i\wedge P_{3-i}\wedge Q_{3-i}.
\]

The multigraph extension of BJ-Wang remains usable for producing a SAD
of \(D^\bullet\). It does not solve the un-contraction problem.

## 7. What the polytope lemma must prove

The replacement lemma must be explicitly side-aware.

A clean formulation is:

**Side-compatible SAD lemma.** Let \(D\) be a simple 3-arc-strong
\((1,0)\)-near-split digraph with chord \(e_0=(p,q)\), and let
\(D^\bullet\) be the contracted split multi-digraph with contracted
vertex \(r=p^\bullet\). Then the SAD-coloring space of \(D^\bullet\)
contains a partition \((A_1^\bullet,A_2^\bullet)\) such that, after
un-contraction, either
\[
D_1^\flat+e_0\ \text{and}\ D_2^\flat
\]
are both strong, or
\[
D_2^\flat+e_0\ \text{and}\ D_1^\flat
\]
are both strong.

In cut form, the lemma says that the SAD polytope of \(D^\bullet\)
intersects one of the two liftability regions:
\[
L_i=\{(A_1^\bullet,A_2^\bullet):
(V,\pi^{-1}(A_i^\bullet)\cup\{e_0\})\ \text{strong and}\
(V,\pi^{-1}(A_{3-i}^\bullet))\ \text{strong}\}.
\]

Any proof of this lemma must do at least one of the following:

1. strengthen BJ-Wang's path-splitting construction so the special
   shell vertex \(r\) receives prescribed side-compatible pairs in the
   two colors;
2. prove a recoloring/exchange theorem for SADs of \(D^\bullet\), moving
   labelled arcs incident with \(r\) between colors while preserving
   both contracted color classes strong;
3. formulate and prove a min-cut/branching packing theorem with side
   constraints at \(r\), strong enough to force \(Q_i\) in one color and
   both \(P_{3-i},Q_{3-i}\) in the other.

The lemma cannot be replaced by ordinary BJ-Wang Corollary 1. Corollary
1 forgets precisely the labels that the un-contraction needs.

## 8. Recommended next move

Abandon the hope that a one-session citation/inspection of BJ-Wang
closes R3-star. The right next mathematical task is a self-contained
side-compatible SAD lemma.

The most promising first subcase is the direct kernel-shell case:
\(D^\bullet[V_2]\) already has a SAD. In that case one can try to prove
the side-compatible attachment statement directly by choosing the
Lemma 2.4 attachments and leftover arcs at \(r\). If successful, the
hard residual is narrowed to the true splitting-off cases in BJ-Wang's
Theorem 1.6 proof.

For the full theorem, the polytope/recoloring formulation is cleaner
than another blind pass through the BJ-Wang proof. The proof must keep
the four labelled incidence classes
\[
R_p^+,\ R_q^+,\ R_p^-,\ R_q^-
\]
visible from the start.

