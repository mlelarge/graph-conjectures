# Review of `plan.md` v2

## Verdict

The revised plan is a major improvement over v1. It no longer pretends that
the residue after \(P_3\)-removal is connected, and it correctly identifies
the residue-component count \(\ell\) as the central obstruction.

The document is now a reasonable research triage note, not a fake proof plan.
But several factual and logical issues remain. These should be corrected before
using the plan as a basis for a write-up or for assigning subtasks.

## What v2 Fixed

The fatal flaw in v1 was the claim that connectivity propagates through
\(P_3\)-removal. v2 correctly removes that claim.

The basic obstruction is now stated correctly. If one iterates the improved
\(P_3\)-removal lemma until no induced \(P_3\) remains, the residue is a
disjoint union of cliques, not a single clique. If \(k\) vertices are removed
and the residue has \(\ell\) clique components, then the crude lower bound is
\[
s^\pm(G)\ge n+\frac{k}{16}-\ell.
\]
Thus the route lives or dies by controlling \(\ell\), not by invoking
connectivity.

v2 also correctly records that Lemma 2.4 of arXiv:2506.07264 already applies
to both \(s^+\) and \(s^-\). No dualization through \(-A\) or a bipartite
double cover is needed.

Finally, v2 correctly downgrades the old Variant 3 from a "4-8 week genuine
theorem" to a speculative research direction.

## Remaining Corrections

### 1. EFGW is misstated

The background section says that EFGW is for graphs with no isolated vertex.
That is false as written. The conjecture is for connected graphs.

Disconnected graphs with no isolated vertices can violate the \(n-1\) lower
bound. For example, \(2K_3\) has \(n=6\), but each \(K_3\) contributes
\(s^-=2\), so
\[
s^-(2K_3)=4<5=n-1.
\]

Correct wording:

> EFGW: for every connected graph \(G\) of order \(n\),
> \(\min\{s^+(G),s^-(G)\}\ge n-1\).

### 2. "9.2(i) implies EFGW for unicyclic graphs" is too strong

The plan says that 9.2(i) implies EFGW for unicyclic graphs. It does not.

Conjecture 9.2(i) says
\[
s^+(G)=n-1 \quad\Longleftrightarrow\quad G\text{ is a tree}.
\]
For a non-tree, this only rules out equality. It does not rule out
\(s^+(G)<n-1\). So 9.2(i) alone does not imply the EFGW lower bound for
unicyclic graphs.

The intended point is weaker and should be stated that way:

> Natural proof strategies for 9.2(i) run into the same unicyclic obstruction
> as the EFGW programme, because proving strictness by a lower-bound argument
> would require controlling sparse non-bipartite unicyclic graphs.

### 3. The clique-residue formula is exact only for \(s^-\)

The plan writes
\[
s^\pm(\text{residue})=\sum_j(n_j-1).
\]
This is false for \(s^+\).

For a clique \(K_t\),
\[
s^-(K_t)=t-1,\qquad s^+(K_t)=(t-1)^2.
\]
Therefore, for a residue \(K_{n_1}\sqcup\cdots\sqcup K_{n_\ell}\),
\[
s^-(\text{residue})=\sum_j(n_j-1)=n-k-\ell,
\]
but
\[
s^+(\text{residue})=\sum_j(n_j-1)^2\ge \sum_j(n_j-1)=n-k-\ell.
\]

The displayed lower bound \(s^\pm(G)\ge n+k/16-\ell\) still works for both
signs as a lower bound, but the equality statement must be corrected.

### 4. The condition \(\ell<k/16+1\) is sufficient for the crude bound, not intrinsic

The plan says one "needs"
\[
\ell<\frac{k}{16}+1
\]
to force strictness. More precisely, this is needed only if one uses the crude
residue lower bound \(s^\pm(\text{residue})\ge n-k-\ell\).

For \(s^+\), clique residues can contribute substantially more:
\[
\sum_j(n_j-1)^2.
\]
So \(\ell<k/16+1\) is a sufficient condition for the simple telescoping
argument, not a necessary condition for the theorem.

### 5. The SDP lemma is misstated

The plan describes Lemma 3.1 as
\[
s^+(G)=\inf_{M\succeq 0}\|A+M\|_F^2
\]
"over \(M\) with zero diagonal off the support of \(A\)."

That support restriction is not in the displayed lemma in the source paper.
The source statement is simply over positive semidefinite \(M\):
\[
s^+(G)=\inf_{M\succeq 0}\|A(G)+M\|_F^2.
\]

If a constrained SDP is intended, it needs a separate citation or proof. As
written, remove the support condition.

### 6. The Elphick-Linz citation is overstated

The plan says Elphick-Linz notes that \(K_n\) is the only graph with
\(s^-\le n-1\). That is false as written because trees also have
\(s^-=n-1\).

Replace it with:

> Trees and complete graphs are the two obvious equality families for
> \(s^-=n-1\), and the asymmetry literature explains why \(K_n\) is a special
> second extremal point for \(s^-\).

## Assessment of the Proposed Deliverables

### Corollary A: claw-free graphs

This is sound and very short.

Theorem 1.1 of arXiv:2506.07264 gives \(s^+(G)\ge n\) for connected claw-free
graphs with \(\Delta\ge 3\). Hence \(s^+=n-1\) is impossible there. If
\(\Delta\le 2\), a connected graph is a path or a cycle; paths are trees, and
cycles have \(s^+>n-1\).

This is a clean corollary, but it is not substantial new mathematics.

### Corollary B: diameter at most 2

This is also sound and short.

Diameter \(1\) gives \(G=K_n\), and
\[
s^+(K_n)=(n-1)^2,
\]
so \(s^+=n-1\) only for \(K_2\). For diameter exactly \(2\), Theorem 1.2 of
arXiv:2506.07264 gives \(s^+(G)\ge n\), except for \(K_{1,n-1}\) and \(C_5\).
The star is a tree, and
\[
s^+(C_5)=4.763932\ldots>4.
\]

Again: useful as an internal deliverable, but too small to carry a paper by
itself.

## Strategic Assessment

The central research problem is now correctly identified:

> Find a class where valid \(P_3\)-removal sequences keep the clique-residue
> component count \(\ell\) under control, or abandon \(P_3\)-removal for a
> different structural/spectral argument.

The suggested classes are plausible places to look, but the plan should be
more suspicious of them.

- **Block graphs:** structural control is strong, but \(P_3\)-removal may
  repeatedly delete articulation vertices. That is exactly the bad behavior.
- **Chordal graphs:** perfect elimination orderings delete simplicial
  vertices, but Lemma 2.4 does not say the simplicial vertex is the one with
  \(17/16\) gain. Compatibility between elimination order and spectral slack
  must be proved.
- **2-connected graphs:** initial 2-connectivity does not prevent later
  removals from creating many components. The block-cut tree of the residue
  may help, but this is not automatic.
- **Cactus/unicyclic subclasses:** these are attractive because the structure
  is nearly one-dimensional, but they are also close to the known bottleneck.

So the right posture is: these are search directions, not expected theorems.

## Recommended Edits to `plan.md`

1. Replace "for \(G\) with no isolated vertex" by "for connected \(G\)" in the
   EFGW background.
2. Replace "9.2(i) implies EFGW for unicyclic graphs" by a weaker statement
   about proof strategies meeting the unicyclic obstruction.
3. Correct the clique-residue energy formula:
   \[
   s^-(\text{residue})=n-k-\ell,\qquad
   s^+(\text{residue})=\sum_j(n_j-1)^2\ge n-k-\ell.
   \]
4. Rephrase \(\ell<k/16+1\) as a sufficient condition for the crude
   telescoping argument, not a necessary condition for the theorem.
5. Remove the unsupported SDP support restriction.
6. Fix the Elphick-Linz citation about \(K_n\) and \(s^-\le n-1\).
7. Downgrade "publishable as a short note" to "clean internal note" unless a
   genuinely new class-specific equality result is added.

## Bottom Line

v2 is now honest and mathematically useful. It correctly identifies the main
obstruction and stops overselling the old \(P_3\)-removal route.

But it is still not a proof plan for a serious new theorem. It is a good map
of where the proof breaks. The next real mathematical task is not writing the
corollaries; it is finding, or disproving, a class-specific mechanism that
controls \(\ell\) under valid \(P_3\)-removal.

## Sources Checked

- arXiv:2506.07264, *Refinement of a conjecture on positive square energy of graphs*
- arXiv:2311.11530, *Symmetry and asymmetry between positive and negative square energies of graphs*
- arXiv:2303.11930, *Positive and Negative Square Energies of Graphs*
