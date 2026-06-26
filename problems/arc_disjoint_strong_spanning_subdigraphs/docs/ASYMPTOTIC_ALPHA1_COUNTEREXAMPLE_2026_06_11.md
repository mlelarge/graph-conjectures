# Alpha=1 core and minimum-cut lift audit

Date: 2026-06-11.

## Verdict

The proposed alpha=1 core is false for general multidigraphs.  There are
lambda-arc-strong multidigraphs on \(n\) vertices with \(2^{n-2}\) distinct
global minimum out-cut arc-sets.  The same family refutes EPK-2's proposed
two-arborescence determination by a direct pigeonhole argument.

The proposed minimum-cut-only EC-log lift also does not follow from the
available ingredients:

1. directed global minimum-cut sides need not form a laminar family;
2. making every minimum cut bichromatic does not imply that every directed
   cut is bichromatic;
3. the counterexample event system already misses the symmetric Local Lemma
   criterion by a constant factor.

This does not refute a general-digraph logarithmic-lambda SAD theorem.  It
refutes the stated counting/EPK-2/minimum-cut-only route to that theorem.

## 1. Exponential family

For \(k\geq 2\), define the multidigraph \(B_k\) on

\[
V(B_k)=\{s,t,p_1,\ldots,p_k\}.
\]

For every \(i\), include:

* one arc \(s p_i\);
* one arc \(p_i t\);
* \(k-1\) parallel arcs \(p_i s\);
* \(k-1\) parallel arcs \(t p_i\).

Also include \(k\) parallel arcs \(t s\).  Parallel arcs are distinct members
of an arc-set.

### Proposition 1

\(\lambda(B_k)=k\).

### Proof

Let \(P=\{p_1,\ldots,p_k\}\), let
\(S=X\cap P\), and write \(j=|S|\).  There are four cases.

* If \(s\in X\) and \(t\notin X\), exactly the \(k-j\) arcs
  \(s p_i\) with \(p_i\notin S\) and the \(j\) arcs \(p_i t\) with
  \(p_i\in S\) leave \(X\).  Hence \(d^+(X)=k\).
* If \(s,t\notin X\), then \(X=S\neq\varnothing\).  Every \(p_i\in S\)
  sends one arc to \(t\) and \(k-1\) arcs to \(s\), so
  \(d^+(X)=jk\geq k\).
* If \(s\notin X\) and \(t\in X\), then the \(t s\) bundle contributes
  \(k\), and for every \(p_i\), either \(t p_i\) or \(p_i s\) contributes
  \(k-1\).  Thus \(d^+(X)=k+k(k-1)=k^2\).
* If \(s,t\in X\), then \(P\setminus S\neq\varnothing\).  Every omitted
  \(p_i\) receives one leaving arc from \(s\) and \(k-1\) leaving arcs
  from \(t\), so \(d^+(X)=k(k-j)\geq k\).

The first case supplies cuts of size \(k\), proving the claim. \(\square\)

### Proposition 2

\(B_k\) has at least \(2^k=2^{n-2}\) distinct global minimum out-cut
arc-sets.

### Proof

For each \(S\subseteq P\), put \(X_S=\{s\}\cup S\).  Proposition 1 and the
first case above give

\[
\delta^+(X_S)
=\{s p_i:p_i\notin S\}\mathbin{\dot\cup}
  \{p_i t:p_i\in S\}.
\]

For each \(i\), the cut contains exactly one of the two distinct arcs
\(s p_i,p_i t\), and the choice records whether \(p_i\) belongs to \(S\).
The \(2^k\) arc-sets are therefore distinct and minimum. \(\square\)

In particular, at \(k=8\), \(n=10\) and

\[
2^k=256>2(n-1)^2=162.
\]

Thus the proposed bound on all distinct minimum out-cut arc-sets is false,
even up to the stated leading constant.

## 2. EPK-2 is false

Fix root \(r=t\).  Every side \(X_S\) above avoids \(r\).  The proved
Transversal Lemma says that, for every packing of \(k\) arc-disjoint spanning
in-arborescences to \(r\), every minimum cut intersects each packed tree in
exactly one arc.

For any ordered pair \((T_a,T_b)\), its signature

\[
F\longmapsto(F\cap T_a,F\cap T_b)
\]

therefore has at most

\[
|T_a||T_b|=(n-1)^2=(k+1)^2
\]

possible values.  But the \(2^k\) minimum arc-sets above all avoid \(t\).
Already at \(k=6\),

\[
2^6=64>(7)^2=49.
\]

Hence no packing and no ordered tree pair can make the signature injective.
EPK-2 is false.

This pinpoints why Karger's undirected 2-respect argument does not transfer.
In an undirected tree, deleting the one or two crossed tree edges determines
the cut side (up to complementation).  In a directed in-arborescence, naming
the one outgoing cut arc does not determine which other rooted subtrees lie
on that side.  The family \(B_k\) stores \(k\) independent choices in exactly
that missing information.

The Transversal Lemma itself is unaffected and remains proved.

## 3. Literature check

Karger's paper is:

* D. R. Karger, "Minimum Cuts in Near-Linear Time", *Journal of the ACM*
  47(1) (2000), 46-76, DOI
  [10.1145/331605.331608](https://doi.org/10.1145/331605.331608);
  author manuscript [arXiv:cs/9812007](https://arxiv.org/abs/cs/9812007).

Its relevant mechanism is the undirected spanning-tree packing statement:
an alpha-minimum cut \(2\alpha\)-constrains some packed tree.  The subsequent
count uses the fact that a chosen set of tree edges determines a unique
undirected cut.  That last fact is the non-transferable step above.

The classical branching reference is:

* J. Edmonds, "Edge-disjoint branchings", in R. Rustin (ed.),
  *Combinatorial Algorithms*, Courant Computer Science Symposium 9,
  Algorithmics Press, pp. 91ff., cited as 1972 in Karger's bibliography and
  often catalogued as 1973.

The original chapter was not located in an openly accessible primary-source
scan during this audit.  Karger's primary paper cites it as 1972, page 91.
The exact theorem used here is the standard root-cut characterization for
packing arc-disjoint spanning branchings.  No stronger two-tree cut
determination statement is supplied by that theorem.

## 4. Minimum cuts are not laminar

The minimum-cut sides \(\{X_S:S\subseteq P\}\) in \(B_k\) form a Boolean
lattice.  For example, \(X_{\{p_1\}}\) and \(X_{\{p_2\}}\) intersect but
neither contains the other, and the full family has exponentially many
incomparable members.  Thus there is no general laminar family of directed
global minimum out-cuts on which to run the indicated alteration.

The associated monochromatic events also defeat the elementary symmetric
Local Lemma test.  Each has probability \(p=2^{1-k}\).  Two such events are
arc-disjoint only when their bit strings are complementary, so the dependency
degree is \(d=2^k-2\).  Consequently

\[
e p(d+1)=e\,2^{1-k}(2^k-1)=2e(1-2^{-k})>1.
\]

This does not rule out every asymmetric or grouped-event Local Lemma proof.
It rules out the proposed laminar/symmetric implementation.

## 5. Minimum-cut bichromaticity is insufficient

There is a separate logical gap: even a coloring that makes every global
minimum out-cut bichromatic need not be a SAD coloring.

Take the complete bidirected graph \(K_4^*\), with partition
\(A=\{0,3\}\), \(B=\{1,2\}\).  Color all arcs internal to \(A\) or \(B\)
red and all arcs between \(A\) and \(B\) blue.  Every minimum out-cut has
size three and is a singleton or co-singleton cut.  Such a cut contains one
red internal arc and two blue cross-arcs, so every minimum cut is
bichromatic.  However, both \(\delta^+(A)\) and \(\delta^+(B)\) are entirely
blue.  The red spanning subdigraph is not strongly connected.

Replacing every arc by \(q\) parallel copies gives the same obstruction at
arbitrarily large \(\lambda=3q\).  Therefore a minimum-cut-only event
avoidance argument cannot conclude SAD without a genuinely new theorem that
also controls nonminimum cuts.  The example refutes the naive implication
even in the high-connectivity regime.

## 6. Consequence

The following project hypotheses must be retired:

* H5-DKSTAR-CORE: false, by \(B_k\);
* H6-EPK2: false, by the \(k=6\), root-\(t\) pigeonhole;
* "directed global minimum cuts are laminar": false;
* "bichromatize only the minimum cuts, then infer SAD": false.

The Eulerian EC-log theorem is unchanged.  A general-digraph logarithmic-
lambda SAD theorem, if true, needs control of nonminimum directed cuts or a
different structural/probabilistic mechanism; it does not follow from the
alpha=1 core proposed here.
