# O2: the cage canonicalization — proved core, residual gap

Date: 2026-06-11.  Companion to `ABSORPTION_REPAIR_LEMMA_2026_06_11.md`
(whose Lemmas B1–B3 it strengthens and partially supersedes) and to the
witness `scripts/gateway_t_eq_u_witness.py`.

Status: O2 is NOT fully proved.  What is proved: the t=u gateway theory is
CANONICAL — it depends only on (D^bullet, u), not on the pair (T,U) — via
the cage C_u; absorption targets, sealing, the two-tail criterion, and a
3-packing inside the cage are all proved at this canonical level.  The
residual gap is isolated in (O2a*) and (O2b*) at the end.

## Setting

\(D^\bullet\), \(I\), \(K\), \(\rho\), \(\lambda\ge3\) as before.  Fix
\(u\ne\rho\) and \(a=(u,v)\).  "Path" means directed path in
\(D^\bullet\).

## Lemma C1 (the cage)

Define \(C_u:=\{u\}\cup\{x: \text{every }x\to\rho\text{ path passes
through }u\}\).

1. Every arc with tail in \(C_u\setminus\{u\}\) has head in \(C_u\)
   (\(C_u\) is u-gated), and every u-gated set \(Y\) (\(u\in Y\),
   \(\rho\notin Y\), all of \(\delta^+(Y)\) tailed at \(u\)) satisfies
   \(Y\subseteq C_u\).
2. Every \(x\in C_u\) reaches \(u\) inside \(C_u\); every
   \(z\notin C_u\) reaches \(\rho\) avoiding \(C_u\) entirely.
3. An in-arborescence containing \(a\) exists iff \(v\notin C_u\); in
   that case \(X_a^T\supseteq C_u\) for EVERY such \(T\), with equality
   realizable.

**Proof.**  (1) If \(x\in C_u\setminus\{u\}\) had an arc to
\(z\notin C_u\), appending \(z\)'s u-avoiding \(\rho\)-path to \(x\to z\)
gives \(x\) a u-avoiding path: contradiction.  For a u-gated \(Y\) and
\(x\in Y\setminus\{u\}\): any \(x\to\rho\) path starts in \(Y\), and as
long as it stays in \(Y\setminus\{u\}\) its arcs cannot leave \(Y\); since
\(\rho\notin Y\) it must eventually leave, which only happens at \(u\).
(2) For \(x\in C_u\): take any \(x\to\rho\) path and its prefix up to the
first visit of \(u\); an intermediate vertex \(z\) of the prefix with a
u-avoiding \(\rho\)-path would hand that path to \(x\), so the prefix
stays in \(C_u\).  For \(z\notin C_u\): a u-avoiding path that entered
\(C_u\setminus\{u\}\) could no longer avoid \(u\) by (1).
(3) If \(v\in C_u\): \(v\)'s \(T\)-path passes \(u\) while \(u\)'s passes
\(v\) — a cycle; so no \(T\ni a\).  If \(v\notin C_u\): every
\(x\in C_u\setminus\{u\}\) has its \(T\)-path to \(\rho\) pass \(u\),
hence use \(a\): \(x\in X_a^T\).  Equality: assemble an in-arborescence of
\(C_u\) rooted \(u\) (exists by (2)), the arc \(a\), and an
in-arborescence of \(V\setminus C_u\) rooted \(\rho\) inside
\(D^\bullet-C_u\) (exists by (2)).  \(\square\)

## Lemma C2 (canonical gateway set; absorption is forced)

Suppose \(v\notin C_u\) and \(2\le|C_u|\).  Then every pair with
\(X_a^T=C_u\) has exactly one \(U\)-exit and is failing.  Consequently a
good pair at \(a\) must have \(X\supsetneq C_u\).  Conversely, any t=u
gateway pair has a u-gated set, hence \(X\subseteq C_u\); combined with
\(X\supseteq C_u\) from C1(3): **if a t=u hard gateway exists at \(a\),
its set is uniquely \(C_u\), and \(|C_u|\ge2\).**

(C1(3) proves existence of a single \(T\ni a\), NOT of an arc-disjoint
PAIR with \(X=C_u\); so "\(|C_u|\ge2\) implies a gateway pair exists" is
not claimed.  The proof program does not need it: it only repairs the
gateways that exist.)

**Proof.**  \(\delta^+(C_u)\subseteq\delta^+(u)\) and \(U\) has one
out-arc at \(u\); reachability forces at least one exit.  One exit =
failing (Lemma 2.1).  A gateway set is u-gated by Lemma 11.1 (t=u), so
\(X\subseteq C_u\) by C1(1).  \(\square\)

This removes the pair (T,U) from the problem: D10's witness has
\(C_u=\{u,k_a,k_b,k_c\}\), and C1(3) predicts its three no-pair arcs
\((u,k_i)\) exactly (heads inside the cage).

## Lemma C3 (reserve, hooks, outside-nonemptiness at the cage)

If \(|C_u|\ge2\): \(|K\cap C_u\setminus\{u\}|\ge2\);
\(V\setminus C_u\setminus\{\rho\}\ne\varnothing\) (so \(|C_u|\le n-2\)
automatically); \(K\setminus C_u\ne\varnothing\); and every
\(w\in K\setminus C_u\) sends an arc to every
\(k_1\in K\cap C_u\setminus\{u\}\).

**Proof.**  The first and last claims are the proofs of B1 and B2 with
the u-gated SET \(C_u\) in place of the gateway pair's \(X\): they only
ever used "all arcs leaving have tail \(u\)", independence of \(I\),
absence of \(\rho\leftrightarrow I\setminus\{\rho\}\) arcs, simplicity
off \(\rho\), and \(\lambda\ge3\).

The middle claims do NOT follow from Lemma 11.2 verbatim (its proof used
intermediacy of \(X\), which is not assumed for \(C_u\)).  Instead: if
\(V\setminus C_u=\{\rho\}\), then \(\delta^+(C_u)\) consists of arcs
\(u\to\rho\) only, of total multiplicity \(\le2\), contradicting
\(\lambda\ge3\).  So some \(y\in V\setminus C_u\setminus\{\rho\}\)
exists.  If moreover \(K\subseteq C_u\), pick such a \(y\); then
\(y\in I\setminus\{\rho\}\), all its in-arcs come from \(K\subseteq
C_u\), every such arc crosses \(\delta^+(C_u)\) and so has tail \(u\)
with multiplicity \(\le1\); hence \(d^-(y)\le1<3\), a contradiction.
\(\square\)

## Lemma C4 (canonical absorption sets)

For \(w\in K\setminus C_u\) let
\(B_w:=\{z\notin C_u\cup\{w\}:\ z\text{ has no }\rho\text{-path avoiding }
C_u\cup\{w\}\}\) and \(X^*_w:=C_u\cup\{w\}\cup B_w\).  Then:

1. (sealing) every arc with tail in \(B_w\) has head in \(X^*_w\); hence
   \(\operatorname{tails}(\delta^+(X^*_w))\subseteq\{u,w\}\);
2. (escape) \(w\) has at least one arc leaving \(X^*_w\);
3. (realizability) if \(v\notin X^*_w\) and \(|X^*_w|\le n-2\), there is
   \(T^*\ni a\) with \(X_a^{T^*}=X^*_w\) exactly, using the hook
   \(w\to k_1\) of C3.

**Proof.**  (1) An arc \(z\to z''\) with \(z\in B_w\),
\(z''\notin X^*_w\) hands \(z\) the forbidden path (\(z''\) reaches
\(\rho\) avoiding \(C_u\cup\{w\}\), and avoiding \(B_w\) automatically:
a \(B_w\)-vertex on that path would inherit it).  Tails: \(C_u\)-side
tails are \(u\) (C1(1)), \(B_w\) is sealed, leaving \(u,w\).
(2) Otherwise all of \(w\)'s arcs enter \(X^*_w\); any \(w\to\rho\) path
then continues inside \(X^*_w\) until it exits, and by (1) it exits at
\(u\) — every \(w\)-path passes \(u\), i.e. \(w\in C_u\), contradiction.
(3) Inside, what is needed is that every vertex of \(X^*_w\) reaches
\(u\) INSIDE \(X^*_w\); then an internal in-arborescence rooted at \(u\)
exists.  For \(C_u\)-vertices this is C1(2).  For \(z\in B_w\): \(z\notin
C_u\), so \(z\) has a \(C_u\)-avoiding \(\rho\)-path (C1(2)); since
\(z\in B_w\) that path must meet \(C_u\cup\{w\}\), hence meets \(w\); its
prefix up to \(w\) stays in \(B_w\) (an intermediate \(z'\notin B_w\)
would have a \(C_u\cup\{w\}\)-avoiding path, and the prefix — which
avoids \(C_u\) and stops before \(w\) — would hand it to \(z\)).  So
every \(z\in B_w\) reaches \(w\) inside \(B_w\cup\{w\}\); note the bare
definition of \(B_w\) alone would only give "reaches \(C_u\cup\{w\}\)
inside \(X^*_w\)", which is already sufficient here.  Then \(w\to k_1\)
enters \(C_u\), and \(u\to v\) is the arc \(a\).
Outside: every \(z\notin X^*_w\) reaches \(\rho\) avoiding
\(C_u\cup\{w\}\), and avoiding \(B_w\) automatically (a \(B_w\)-vertex on
the path would inherit the avoidance).  Exactness as in C1(3).
\(\square\)

## Lemma C5 (two-tail criterion)

Write \(AV_u:=\delta^+(C_u)\setminus\{a\}\) (\(|AV_u|\ge2\), all tailed at
\(u\), none usable by \(T^*\) beyond \(a\)).  \(X^*_w\) admits designated
\(U^*\)-exit arcs at TWO distinct tails iff some arc of \(AV_u\) has head
outside \(X^*_w\) (the \(w\)-side exit always exists by C4(2)).  Arcs of
\(AV_u\) with head \(\rho\) always qualify.

## Lemma C6 (pathology bounds for the head-escape)

1. If \(AV_u\) has two distinct heads \(z_0\ne z_1\) in
   \(K\setminus C_u\): not both "\(z_1\in B_{z_0}\) and
   \(z_0\in B_{z_1}\)" (a \(z_0\)-path through \(z_1\) ends with a
   \(z_1\)-path that cannot re-pass \(z_0\)); so choosing \(w\) as the
   trapping one gives the other as an escaped head.
2. (suffix lemma) If some head \(z_0\)'s every \(C_u\)-avoiding path
   passes every vertex of \(K\setminus C_u\setminus\{z_0\}\), then the
   last such vertex \(w^*\) on any one path has the DIRECT arc
   \(w^*\to\rho\): the suffix after \(w^*\) contains no further
   \(K\)-vertices, two consecutive \(I\)-vertices are impossible
   (independence), and \(I\)-vertices have no arcs to \(\rho\), so the
   suffix is the single arc \(w^*\to\rho\).

## Lemma C7 (3-packing inside the cage — the tool O2b needs)

\(D^\bullet[C_u]\) contains THREE arc-disjoint spanning in-arborescences
rooted at \(u\).

**Proof.**  For nonempty \(Y\subseteq C_u\setminus\{u\}\):
\(|\delta^+_{D^\bullet}(Y)|\ge3\) by 3-arc-strongness, and every such arc
has tail in \(C_u\setminus\{u\}\), hence head in \(C_u\) (C1(1)) — the
whole cut survives inside \(D^\bullet[C_u]\).  So every \(Y\) avoiding
\(u\) has out-cut \(\ge3\) within the cage, and Edmonds' branching theorem
gives the packing.  \(\square\)

In particular \(T^*\)'s inside part can be chosen as ONE arb of the
packing, leaving residual out-degree \(\ge2\) toward \(u\) across every
inside cut — exactly the slack a disjoint \(U^*\) needs inside.

## What remains of O2

* **(O2a*) head-escape in the degenerate trap.**  Choose
  \(w\in K\setminus C_u\) with: some \(AV_u\)-head outside
  \(B_w\cup\{w\}\) (C5), \(v\notin X^*_w\), and \(|X^*_w|\le n-2\).
  C6 covers two-K-head and exhausted-chain configurations; the open
  residue is a single K-head (or I-heads only) jointly trapped behind
  every candidate \(w\), entangled with the \(v\)- and size-constraints.
  Multi-vertex absorption (\(X^*=C_u\cup\{w,w'\}\cup B_{w,w'}\)) is
  available and unformalized.
* **(O2b*) the glue — a PRESCRIBED-OUT-ARC branching problem.**  Given
  \(T^*\) (C4(3), inside part from the C7 packing) and the two designated
  exit arcs \(e_u\) at \(u\) and \(e_w\) at \(w\), prove \(U^*\) exists:
  an in-arborescence arc-disjoint from \(T^*\) CONTAINING both.
  CORRECT equivalent form: every vertex reaches \(\rho\) in the
  prescribed residual
  \[
  \widehat D(T^*,e_u,e_w):=
  \bigl(D^\bullet-\text{labels}(T^*)\bigr)
  \ \text{with the out-arc sets at }u,w\text{ replaced by }
  \{e_u\},\{e_w\},
  \]
  i.e. after deleting every COMPETING out-arc at the two prescribed
  tails.  (The earlier formulation — plain reachability in
  \(D^\bullet-T^*\) — is FALSE as an equivalence: it guarantees some
  residual in-arborescence but not one through the prescribed arcs,
  which may force a cycle.  With the out-arcs at \(u,w\) forced, the
  reverse-BFS construction makes the equivalence exact.)
  Inside the cage C7 gives 2-residual across every cut and \(AV_u\) is
  wholly unused by \(T^*\); the open part is \(\widehat D\)-reachability
  OUTSIDE the cage, where \(T^*\) may consume a vertex's only
  outside-escape (such a vertex must re-enter \(X^*_w\) in
  \(\widehat D\) and exit via \(e_u\)/\(e_w\) — the chase needs to be
  made well-founded).

Both residues are finite-checkable per instance.  The checked-in
verification of C1–C7 and of O2a*/O2b* (in the corrected prescribed-arc
form) is `scripts/cage_canonicalization_check.py`; see ledger D12/D13.
