# O2b*: the merged interior packing and the rho-head theorem

Date: 2026-06-11.  Companion to `O2_CAGE_CANONICALIZATION_2026_06_11.md`
(notation: cage \(C_u\), \(B_w\), \(X^*_w=C_u\cup\{w\}\cup B_w\),
\(AV_u=\delta^+(C_u)\setminus\{a\}\), prescribed residual
\(\widehat D(T^*,e_u,e_w)\)).

Status: O2b* is PROVED whenever \(AV_u\) contains an arc \(u\to\rho\)
(Theorem T1) — in particular on the D10 witness, where \(u\in K\) carries
\((u\to\rho)^2\).  The no-rho-head residue is named and narrowed at the
end.  The inside of the problem is closed unconditionally by a new
packing lemma (D1) that supersedes the separate C7/T_B treatment and
handles \(B_w\ne\varnothing\) uniformly.

Throughout: \(w\in K\setminus C_u\) with \(v\notin X^*_w\) and
\(|X^*_w|\le n-2\) (the O2a* size/placement conditions; note the
head-escape condition of O2a* is automatic here since \(\rho\notin
X^*_w\) always).  Write \(O:=V\setminus X^*_w\setminus\{\rho\}\) and
\(D_O:=D^\bullet[O\cup\{\rho\}]\).

## Lemma D1 (merged interior 3-packing)

Let \(H\) be \(D^\bullet[X^*_w]\) with \(u\) and \(w\) identified to a
single root \(s\).  Then \(H\) contains three arc-disjoint spanning
in-arborescences \(F_1,F_2,F_3\) rooted at \(s\).  Moreover every
\(F_i\)-path starting in \(C_u\setminus\{u\}\) stays inside the cage and
enters \(s\) through \(u\).

**Proof.**  For nonempty \(Y\subseteq X^*_w\setminus\{u,w\}\): every arc
with tail in \(Y\cap(C_u\setminus\{u\})\) has head in \(C_u\) (C1(1)),
and every arc with tail in \(Y\cap B_w\) has head in \(X^*_w\) (C4(1)
sealing).  So the FULL cut \(\delta^+_{D^\bullet}(Y)\), of size \(\ge3\)
by 3-arc-strongness, survives inside \(H\) (heads at \(u\) or \(w\)
become \(s\)).  Edmonds' branching theorem gives the packing.

Lifting convention: the identification preserves labeled arcs — every
arc of \(H\) is a labeled arc of \(D^\bullet[X^*_w]\) with its original
endpoints, only the names \(u,w\) being replaced by \(s\).  Write
\(\widetilde F_i\) for the lift of \(F_i\): the same labeled arc set,
read in \(D^\bullet[X^*_w]\).  The \(\widetilde F_i\) are arc-disjoint,
assign one out-arc to every interior vertex, and their maximal paths end
with an arc whose ORIGINAL head is \(u\) or \(w\).  The cage-path claim,
stated for the lifts: arcs tailed in \(C_u\setminus\{u\}\) head inside
\(C_u\), and \(w\notin C_u\), so a \(\widetilde F_i\)-path starting in
the cage can only terminate with an arc whose original head is \(u\).
Below, \(F_i\) always means \(\widetilde F_i\).  \(\square\)

D1 supersedes the earlier C7-plus-\(T_B\) assembly: one \(F_i\) serves
as the entire interior of \(T^*\), for \(B_w\) empty or not.

## Lemma D2 (the packing-based T\*)

Let \(k_1\in K\cap C_u\setminus\{u\}\) be any hook target (C3) and
\(T_{\mathrm{out}}\) any in-arborescence of \(D_O\) rooted \(\rho\)
(exists by C4(3)).  Then

\[
T^*:=F_1\ \cup\ \{(w,k_1)\}\ \cup\ \{a\}\ \cup\ T_{\mathrm{out}}
\]

is a spanning in-arborescence rooted \(\rho\) with
\(X_a^{T^*}=X^*_w\) exactly, and for every nonempty
\(Y\subseteq X^*_w\setminus\{u,w\}\) the \(T^*\)-residual keeps
\(\ge2\) arcs of \(\delta^+(Y)\) (namely the \(F_2,F_3\) crossings).

**Proof.**  Interior vertices follow \(F_1\) to \(u\) or \(w\); from
\(w\), the hook enters the cage and the cage flows to \(u\) (D1), so no
cycle arises and every \(X^*_w\)-vertex uses \(a\); outside vertices
avoid \(X^*_w\) (C4(3)); exactness as before.  \(F_2,F_3\) are
arc-disjoint from \(F_1\) and tailed in the interior, hence from the
hook, \(a\), and \(T_{\mathrm{out}}\); each crosses every interior cut
at least once.  \(\square\)

The four blocking \(T^*\)s found on the witness (60/64 admit a
prescribed-exit \(U^*\), 4/64 do not) are exactly interior stars that
consume the FULL minimum interior cut \(\delta^+(\{k_a,k_b,k_c\})=3\) —
the configuration D2 provably excludes.

## Theorem T1 (rho-head O2b*)

Suppose some arc \(u\to\rho\) lies in \(AV_u\).  Choose
\(e_u:=(u,\rho)\) and \(e_w:=\) any arc of \(w\) leaving \(X^*_w\)
(C4(2)).  Then with \(T^*\) as in D2, EVERY vertex reaches \(\rho\) in
\(\widehat D(T^*,e_u,e_w)\).  Hence \(U^*\) exists, \((T^*,U^*)\) is
arc-disjoint with two \(U^*\)-exits from \(X^*_w\), and the gateway at
\(a\) is repaired.

**Proof.**  Write \(\widehat D\) for the prescribed residual.  Note
\(e_u\notin T^*\) (its only \(u\)-arc is \(a\)) and \(e_w\notin T^*\)
(its only \(w\)-arc is the hook); if \(e_u\) shares the simple arc
\(u\to\rho\) with nothing of \(T^*\), a label is free (and the
multiplicity-2 case only helps).

1. *Cage interior.*  \(F_2\subseteq\widehat D\): it is arc-disjoint
   from \(F_1\), tailed in the interior (so untouched by the hook,
   \(a\), \(T_{\mathrm{out}}\), and the prescriptions at \(u,w\)).
   Every cage-interior vertex follows \(F_2\) inside the cage to \(u\)
   (D1), then \(e_u=(u,\rho)\): reaches \(\rho\).
2. *\(u\) and \(w\).*  \(u\to\rho\) directly.  \(w\to e_w\to z_w\in
   O\cup\{\rho\}\); the \(O\) case is step 4.
3. *\(B_w\).*  Follow \(F_2\): the path ends at \(u\) (done) or at
   \(w\), and \(w\) is handled by step 2.
4. *Every vertex of \(K\setminus C_u\) reaches the cage in
   \(\widehat D\).*  By C3, every \(k\in K\setminus C_u\) carries ALL
   \(|K_1|\ge2\) distinct hooks into \(K\cap C_u\setminus\{u\}\), and
   \(T^*\) consumes exactly ONE out-arc at \(k\) — its
   \(T_{\mathrm{out}}\)-arc if \(k\in O\) (a \(D_O\)-arc, never a hook),
   its \(F_1\)-arc if \(k\in B_w\) (possibly a hook, but only one) —
   while the prescriptions touch only \(u,w\).  So at least one hook
   survives in \(\widehat D\): \(k\) reaches the cage interior, then
   step 1.  This covers \(K\cap O\) AND \(K\cap B_w\).
5. *Outside \(I\)-vertices, by rank.*  Every \(y\in I\cap O\) has all
   out-arcs into \(K\), each simple, at least three in total, and
   \(T^*\) consumes exactly one (its \(T_{\mathrm{out}}\)-arc): at
   least two survive, with two DISTINCT heads in \(K\) (simplicity off
   \(\rho\)), so at most one head is \(w\) and some surviving head lies
   in \(K\cap C_u\) (step 1) or \(K\setminus C_u\) (step 4 — note the
   head may lie in \(K\cap B_w\), which step 4 now covers).
   This covers \(z_w\) as well.  \(\square\)

On the D10 witness \(u\) carries \((u\to\rho)^2\in AV_u\), so T1 applies
to every admissible \(w\): O2b* HOLDS there with proof, consistent with
the 60/64 statistics (the 4 exceptions are non-D2 interiors).

## The rho-headless case

Rho-headless gateways EXIST in-class, so no impossibility shortcut is
available: `scripts/rho_headless_witness.py` builds a (3,6)-cell host
whose contraction has \(u\in I\) (hence NO \(u\to\rho\) arc can exist),
cage \(\{u,k_a,k_b,k_c\}\), an explicit verified rho-headless hard
gateway, and fixed-root L-exist holding at every \(u\)-external arc.

"Rho-headless" means \(AV_u\) contains no arc with head \(\rho\).  This
splits into two cases, and the structural fact below needs the strict
one:

* **strictly rho-headless**: NO arc \(u\to\rho\) exists in \(D^\bullet\)
  (forced when \(u\in I\)); then \(u\notin R\) below;
* **unique-root-head**: \(a=(u,\rho)\) IS the unique \(u\to\rho\) label
  (\(u\in K\), multiplicity 1).  Then \(u\in R\), \(v=\rho\), and only
  \(|R\setminus\{u\}|\ge1\) follows (the remaining \(\ge2\) labels may
  sit on a single multiplicity-2 tail).  This case is retained as a
  SEPARATE residue item below; note \(v=\rho\) makes the
  \(v\)-placement constraint vacuous there.

Free structural fact (strictly rho-headless case).  Let
\(R:=\{k\in K:\ k\to\rho\in D^\bullet\}\) be the rho-tails.  Then
\(d^-(\rho)\ge3\), every \(\rho\)-in-arc comes from \(K\) with
multiplicity \(\le2\), \(R\cap C_u\subseteq\{u\}\), and \(u\notin R\);
hence

\[
R\subseteq K\setminus C_u,\qquad |R|\ge2.
\]

## Theorem T2 (rho-tail absorption)

Suppose the gateway is rho-headless and there are \(w\in R\setminus\{v\}\)
with \(v\notin X^*_w\) and \(|X^*_w|\le n-2\), and an \(AV_u\)-arc
\(e_u=(u,z_0)\) with \(z_0\notin X^*_w\), such that at least one of:

1. \(z_0\in R\setminus\{w\}\), and a label of \((z_0,\rho)\) survives
   some valid \(T_{\mathrm{out}}\) — unconditional when
   \(\operatorname{mult}(z_0\to\rho)=2\), and otherwise the checkable
   condition that some in-arborescence of \(D_O\) avoids
   \((z_0,\rho)\);
2. \(z_0\to w\in D^\bullet\).

Then with \(e_w:=(w,\rho)\) and \(T^*\) as in D2 — where, in case 1, the
\(T_{\mathrm{out}}\) component of \(T^*\) is CHOSEN to be the in-arb of
\(D_O\) whose existence the hypothesis asserts (the one sparing a
\((z_0,\rho)\) label) — every vertex reaches \(\rho\) in
\(\widehat D(T^*,e_u,e_w)\); hence \(U^*\) exists and the gateway at
\(a\) is repaired.

**Proof.**  Both prescribed arcs leave \(X^*_w\) (\(z_0\notin X^*_w\);
\(\rho\notin X^*_w\)), giving the two exits.  Steps 1, 3, 4, 5 of T1's
proof are rho-head-independent: every vertex reaches \(u\) or \(w\) in
\(\widehat D\).  \(w\to\rho\) directly by \(e_w\).  For \(u\):
\(u\to z_0\) by \(e_u\), then (1) the surviving \((z_0,\rho)\)-label, or
(2) the arc \((z_0,w)\) — whose head lies in \(X^*_w\), so it is not a
\(D_O\)-arc and \(T_{\mathrm{out}}\) cannot consume it, and whose tail
is neither interior nor \(u,w\), so \(F_1\), the hook and \(a\) do not
contain it — followed by \(e_w=(w,\rho)\).  \(\square\)

On the rho-headless witness, T2 applies directly (absorb \(w=k_3\),
\(\operatorname{mult}(k_3\to\rho)=2\); \(e_u=(u,k_4)\) with
\(k_4\in R\), and \(k_4\) has another \(D_O\)-arc): 135/144 of the
\(T^*\)s with \(X=X^*\) admit the prescribed \(U^*\), the rest being
interior-cut consumers excluded by D2.

## Theorem T3 (relay repair) and the dominated witness

The K-head full-domination branch of the residue EXISTS in-class and is
NOT an obstruction.  `scripts/dominated_witness.py` builds a (3,9)-cell
host with \(u\in I\) (strictly rho-headless), cage
\(\{u,k_a,k_b,k_c\}\), \(AV_u\)-heads \(\{h_2,h_3\}\subseteq K\), and
\(R=\{r_1,r_2,r_3\}\) (rho-multiplicities 2,1,2) FULLY DOMINATING the
heads (\(r\to h_i\) for all six pairs, no reverses, no head a rho-tail):
both T2 hypotheses fail for every admissible \((w,z_0)\).  The verified
hard gateway at \(a=(u,h_1)\) is nevertheless repaired by a RELAY
through \(v=h_1\):

**Theorem T3 (two-step relay).**  Strictly rho-headless gateway; suppose
there are an admissible \(w\in R\setminus\{v\}\), an escaped
\(AV_u\)-head \(h\), and a vertex \(o\in O\) with \((h,o),(o,w)\in
D^\bullet\), such that some in-arborescence \(T_{\mathrm{out}}\) of
\(D_O\) omits \((h,o)\).  Then with that \(T_{\mathrm{out}}\) in D2's
\(T^*\), prescriptions \(e_u:=(u,h)\), \(e_w:=(w,\rho)\): every vertex
reaches \(\rho\) in \(\widehat D\), and the gateway is repaired.

**Proof.**  Two exits as in T2.  Steps 1, 3, 4, 5 of T1 are unchanged.
For \(u\): \(u\to h\) by \(e_u\); \((h,o)\) survives (it is a
\(D_O\)-arc omitted by the chosen \(T_{\mathrm{out}}\), and no other
part of \(T^*\) contains arcs tailed at \(h\in O\)); \((o,w)\) has head
in \(X^*_w\), so it is not a \(D_O\)-arc and survives unconditionally;
then \(e_w=(w,\rho)\).  \(\square\)

On the witness: \(h=h_2\), \(o=h_1=v\) (note \(v\in O\) always, and the
domination constraint does NOT apply to \(v\) — it is not an
\(AV_u\)-head), \(w=r_2\), \(T_{\mathrm{out}}(h_2)=(h_2,h_3)\) spares
\((h_2,h_1)\); the explicit good pair is asserted by the script.

## Proposition RF (K-dominated relay-free gateways exist)

The two-step relay in T3 is not forced.  The checked-in witness
`scripts/relay_free_witness.py` is a simple (3,12)-cell host whose chord
contraction is 3-arc-strong and has a strictly rho-headless hard gateway
with:

* cage \(C_u=\{u,k_a,k_b,k_c\}\);
* two escaped \(AV_u\)-heads \(h_2,h_3\in K\);
* three admissible rho-tails \(R=\{r_1,r_2,r_3\}\);
* \(r\to h_i\) and no \(h_i\to r\) for every \(r\in R\), \(i=2,3\);
* no \(o\in O\) with \(h_i\to o\to r\), for any \(i\) and any \(r\in R\).

The construction inserts a three-vertex layer \(L\) and orients
\[
h_i\to v\to L\to R\to\rho,\qquad R\to\{h_i,v\},\qquad L\to h_i.
\]
Thus each escaped head reaches \(\rho\), but its only direct outside
out-neighbours are \(v\) and the other escaped head, neither of which has
an arc into \(R\).  Consequently both T2 alternatives and every T3 relay
fail for every admissible pair \((r,h_i)\).  The script independently
asserts class membership, host and contraction connectivity \(3\), the
explicit arc-disjoint hard gateway pair, admissibility, domination, and
relay-freeness.

## Theorem T4 (multi-step relay)

The longer-path relay lemma Proposition RF calls for.  Strictly
rho-headless gateway; suppose there are an admissible
\(w\in R\setminus\{v\}\), an escaped \(AV_u\)-head \(h\), and a directed
path

\[
P:\ h=o_0\to o_1\to\cdots\to o_m\to w,\qquad o_i\in O,
\]

such that every \(O\)-vertex reaches \(\rho\) in \(D_O-A_O(P)\), where
\(A_O(P)\) is the set of \(P\)-arcs with head in \(O\) (the final arc
\((o_m,w)\) has head in \(X^*_w\) and is never a \(D_O\)-arc).  Then
with \(T_{\mathrm{out}}:=\) any in-arborescence of \(D_O-A_O(P)\), the
D2 \(T^*\), and prescriptions \(e_u:=(u,h)\), \(e_w:=(w,\rho)\): every
vertex reaches \(\rho\) in \(\widehat D\), and the gateway is repaired.

**Proof.**  The deletion hypothesis makes \(T_{\mathrm{out}}\) exist and
avoid every arc of \(A_O(P)\), so all of \(P\)'s \(D_O\)-arcs survive in
\(\widehat D\); \((o_m,w)\) survives unconditionally (head in
\(X^*_w\): not a \(D_O\)-arc, and no other \(T^*\)-part contains arcs
tailed in \(O\)).  Two exits as in T2; steps 1, 3, 4, 5 of T1 unchanged;
\(u\to h\to o_1\to\cdots\to w\to\rho\).  T3 is the case \(m=1\).
\(\square\)

T4 repairs the Proposition-RF witness: \(P:\ h_2\to v\to\ell\to r_1\)
(the layered route, \(m=2\)), \(A_O(P)=\{(h_2,v),(v,\ell)\}\), both
sparable since \(h_2\) keeps \((h_2,h_3)\) and \(v\) keeps two other
\(L\)-arcs.  `scripts/t4_relay_repair_check.py` asserts the T4
hypothesis and the explicit good pair on that witness — confirming in
particular that the relay-free witness is NOT a fixed-root L-exist
counterexample at its gateway arc (unverifiable there by enumeration,
\(n=14\)).

## The residue after T1–T4 (open, four-branched)

NOT a single configuration.  What remains of O2b* is the rho-headless
gateways in which T2, T3 and T4 are ALL inapplicable for every choice,
which splits as:

1. **No admissible rho-tail \(w\)** at all (every \(w\in
   R\setminus\{v\}\) fails \(v\)-placement, the size bound, or
   head-escape) — absorption must use non-rho-tails or multiple
   vertices.
2. **\(z_0\in K\) branch**: \(w\to z_0\) (full domination), no T3 relay,
   AND no T4 path: every \(h\)-to-\(w\) path through \(O\) has some
   \(D_O\)-arc whose deletion (jointly with the rest of \(A_O(P)\))
   disconnects some \(O\)-vertex from \(\rho\) — i.e. every relay route
   is load-bearing for \(T_{\mathrm{out}}\) itself.  Since \(h\) DOES
   reach \(\rho\) in \(D_O\) and the first \(R\)-vertex on any such path
   is a candidate \(w\), this branch requires forced single-escape
   chains; unobserved.
3. **\(z_0\in I\) branch** (possible when \(u\in K\)): \(w\to z_0\) or
   NO adjacency between \(z_0\) and \(w\) (semicompleteness forces
   nothing between \(I\) and \(K\)); T2(ii) loses its lever, but T4
   applies verbatim when its path-and-deletion hypothesis holds (the
   relay path may pass through \(I\cap O\) freely).
4. **Unique-root-head case** (\(a=(u,\rho)\) the only \(u\to\rho\)
   label): \(u\in R\), only \(|R\setminus\{u\}|\ge1\) guaranteed;
   \(v=\rho\) (placement vacuous); uncharted.

Instruments available for all branches: multi-vertex absorption (every
\(K\setminus C_u\) vertex has its C3 hook; prescriptions \((r,\rho)\)
at absorbed rho-tails give exits), arcs into the absorbed set are
unconsumable, per-vertex residual abundance (T-out takes one arc each),
and the overshoot bound: absorbing ALL of \(R\) forces
\(X^*=V\setminus\{\rho\}\) (every \(\rho\)-path ends in \(R\)), the
root boundary.
