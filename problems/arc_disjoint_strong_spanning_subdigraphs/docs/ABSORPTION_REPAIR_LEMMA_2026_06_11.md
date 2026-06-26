# Absorption Repair Lemma — proved core, residual obligations

Date: 2026-06-11.  Companion to `CRUX_A_LEXIST_PROOF_ATTEMPT_2026_06_11.md`
(notation of Sections 5, 10, 11) and to the D10 witness
`scripts/gateway_t_eq_u_witness.py`.

Status: the absorption SURGERY is proved (Lemmas B1–B3 below), with an
exact good-pair criterion and a guaranteed leaf one-shot sub-case (B3').
What remains open is bookkeeping, not mechanism: the all-ancestors case
(O1), the exit-count guarantee / loop control when no one-shot choice
exists (O2), and the two boundary lemmas plus rho-side labels carried
over from D10 (O3, O4).

## Setting

\(D^\bullet\) a 3-arc-strong chord contraction, \(V=I\mathbin{\dot\cup}K\),
\(\rho\in I\) the contracted root, \(I\) independent with no
\(\rho\leftrightarrow I\setminus\{\rho\}\) arcs, \(K\) simple semicomplete,
all arcs not incident with \(\rho\) simple.  Fixed-root pair \((T,U)\),
\(a=(u,v)\in T\), \(X=X_a^T\) intermediate, failing, in the gateway (5.1),
and **\(t=u\)**: every arc of \(\delta^+(X)\) has tail \(u\)
(Lemma 11.1).  Write

\[
K_1=(K\cap X)\setminus\{u\},\qquad
A=\text{the }T\text{-ancestors of }u
  =V(vT\rho)\ (\text{the }T\text{-path from }v\text{ to }\rho),
\]

and for \(w\notin X\) let \(S_w=X_w^T\) be the \(T\)-subtree below \(w\)'s
out-arc \(e_w\) (so \(w\in S_w\)).

## Lemma B1 (the inner semicomplete reserve)

In every \(t=u\) gateway, \(|K_1|\ge 2\).

**Proof.**  Every \(x\in X\setminus\{u\}\) has all out-arcs inside \(X\)
(its arcs cannot leave \(X\), Lemma 11.1 with all tails \(=u\)).

If some \(x\in (I\cap X)\setminus\{u\}\) exists: its out-arcs go only to
\(K\) (\(I\) independent, no arcs to \(\rho\) from \(I\setminus\{\rho\}\)),
hence into \(K\cap X\), each with multiplicity one (\(x\ne\rho\)).  So
\(3\le d^+(x)\le |K\cap X|\), giving \(|K_1|\ge 3-[u\in K]\ge 2\).

Otherwise \(X\subseteq\{u\}\cup K_1\).  If \(|K_1|\le 1\) then
\(|X|\le 2\), so \(|X|=2\) and \(X=\{u,k_1\}\).  All out-arcs of \(k_1\)
stay in \(X\), i.e. go to \(u\); the arc \(k_1\to u\) is simple
(\(k_1,u\ne\rho\)), so \(d^+(k_1)\le 1<3\), contradicting
3-arc-strongness.  \(\square\)

## Lemma B2 (a U-free hook always exists)

In every \(t=u\) gateway, every \(w\in K\setminus X\) (nonempty by
Lemma 11.2) satisfies: \(w\to k_1\in D^\bullet\) for **every**
\(k_1\in K_1\); none of these arcs is in \(T\); and at least one of them is
not in \(U\).

**Proof.**  \(k_1\to w\) would leave \(X\) with tail \(k_1\ne u\),
forbidden; semicompleteness of \(K\) forces \(w\to k_1\).  If
\(w\to k_1\in T\) then \(w\)'s \(T\)-path enters \(X\), uses the unique
\(T\)-exit \(a\), and \(w\in X\) — contradiction.  \(U\) contains exactly
one out-arc of \(w\), while \(|K_1|\ge 2\) (Lemma B1) supplies two distinct
hooks; the hooks are simple arcs (no endpoint is \(\rho\)), so at least one
is entirely free of \(U\).  \(\square\)

## Lemma B3 (absorption surgery, exact criterion)

Let \(w\in K\setminus(X\cup A)\) and let \((w,k_1)\) be a \(U\)-free hook
(Lemma B2).  Put

\[
T'=T-e_w+(w,k_1).
\]

Then:

1. \(T'\) is a spanning in-arborescence rooted at \(\rho\), arc-disjoint
   from \(U\), with \(a\in T'\);
2. \(X_a^{T'}=X\mathbin{\dot\cup} S_w\), and \(\rho\notin X_a^{T'}\);
3. with \(U\) unchanged and \(X'=X\cup S_w\),
   \[
   |U\cap\delta^+(X')|
   =[\,y\notin X'\,]+\#\{s\in S_w:\ s\text{'s }U\text{-out-arc leaves }X'\},
   \]
   where \(b=(u,y)\) is the unique \(U\)-exit of \(X\);
4. if that count is \(\ge2\) and \(|X'|\le n-2\), then \((T',U)\) is a
   **good pair** at \(a\) (Lemma 2.1).

**Proof.**
(1) \(w\ne\rho\), so \(e_w\) exists and the out-degree pattern is
preserved; \(e_w\ne a\) since \(w\ne u\).  Acyclicity: the new path from
\(w\) runs \(w\to k_1\to\cdots\to u\to v\to\cdots\to\rho\).  The segment
inside \(X\) avoids \(w\) (\(w\notin X\)); the segment from \(v\) is the
\(A\)-chain, which avoids \(w\) because \(w\notin A\); and \(e_w\) is on
neither segment, so neither was changed.  Every other vertex's path is
either unchanged or passes through \(w\) and continues along the new
route.  Disjointness: the added arc is \(U\)-free by choice.

(2) Paths of vertices of \(X\) are unchanged (they use within-\(X\) arcs,
\(a\), then the \(A\)-chain; \(e_w\) lies on none of these), so
\(X\subseteq X_a^{T'}\).  Every \(s\in S_w\) now routes through \(w\to
k_1\to\cdots\to u\) and uses \(a\).  Any \(z\notin X\cup S_w\) had a path
avoiding both \(a\) and \(w\); it is unchanged.  The union is disjoint
since \(S_w\cap X=\varnothing\) (\(w\)'s old subtree met \(X\) nowhere:
its members' paths used \(e_w\), not \(a\)).  \(\rho\) is the root.

(3) Tails of \(U\)-arcs leaving \(X'\) lie in \(X'=X\cup S_w\).  From
\(X\): every vertex of \(X\setminus\{u\}\) has its \(U\)-out-arc inside
\(X\) (the gateway's single exit is \(b\)), and \(b\) leaves \(X'\) iff
\(y\notin X'\).  From \(S_w\): each vertex has exactly one \(U\)-out-arc;
count those leaving \(X'\).

(4) Two exits give a strict exit by Lemma 2.1; intermediacy is the
\(|X'|\le n-2\) hypothesis (\(|X'|\ge|X|\ge2\)).  \(\square\)

## Lemma B3' (leaf one-shot)

If moreover \(w\) is a \(T\)-leaf (\(S_w=\{w\}\)), \(y\ne w\), and \(w\)'s
\(U\)-out-arc leaves \(X\cup\{w\}\), then \((T',U)\) is good whenever
\(|X|+1\le n-2\).

**Proof.**  The count in B3(3) is \(1+1=2\).  \(\square\)

## Lemma B3+ (free-entry absorption, D43)

The semicomplete hook in B3 is only an existence device.  More generally,
let \(w\notin X\cup A\) and suppose there is any arc \(d=(w,c)\) with
\(c\in X\) and \(d\notin U\).  Then

\[
T'=T-e_w+d
\]

has all conclusions of B3, with the same exact exit-count criterion.
The proof of B3 uses no other property of \(w\), \(c\), or the hook.

On the D42 chain-kernel witness, take \(w=p_5\), \(c\) in the cage, and
keep the original hard-pair \(U\).  The absorbed old \(T\)-subtree is
\(\{p_4,p_5\}\), and \(U\) has three strict exits from the enlarged set.
This is checked in `scripts/chain_kernel_witness.py`.

This is exactly the repair observed on the D10 witness: \(w=k_3\),
\(S_w=\{w\}\), \(y=\rho\ne w\), \(U\)-arc \((k_3,\rho)\) leaves, and
\(X'=\{u,k_a,k_b,k_c,k_3\}\) with the two exits
\(\{(u,\rho),(k_3,\rho)\}\).

## What this proves, and what it does not

Proved: in every \(t=u\) gateway, absorption hooks exist (B1, B2), and for
every non-ancestor \(w\in K\setminus X\) the surgery is valid with an
exact, checkable good-pair criterion (B3), including a guaranteed one-shot
sub-case (B3').  No shrink/absorb ping-pong arises in the one-shot regime:
the repair produces a good pair directly, with \(U\) untouched.

## Machine verification (D10 witness, all 19,800 hard gateways)

Exhaustive red-team on `scripts/gateway_t_eq_u_witness.py`'s contraction:

* **B1, B2: zero violations** across all 19,800 hard gateways
  (\(|K_1|\ge2\) always; a \(U\)-free hook always exists for every
  non-ancestor candidate).
* The \(U\)-**unchanged** one-shot (B3 criterion) repairs only 3,564
  (18%); 12,144 fail the exit count with every candidate \(w\), and
  4,092 (21%) are **all-ancestors** cases (\(K\setminus X\subseteq A\)) —
  the earlier draft's "unobserved" expectation for O1 was wrong.
* Grouping the 19,800 pairs by their \((a,T)\) configuration gives
  **135 distinct configs, and all 135 are repaired**:
  105/105 non-ancestor configs by the exact surgery
  \(T'=T-e_w+(w,k_1)\) together with a **re-chosen** \(U'\)
  (arc-disjoint from \(T'\), \(\ge2\) exits from \(X'\), strict exit
  verified directly), and 30/30 all-ancestor configs by an enlarged-\(X\)
  good pair with \(T\) rebuilt outside \(X\) (\(X^*\supsetneq X\),
  intermediate).

So the absorption MECHANISM accounts for every hard gateway on the
witness; what is unproven is existence in general, isolated in O1/O2
below.

Open obligations:

* **O1 (all-ancestors case).**  If \(K\setminus X\subseteq A\), the local
  surgery always creates a cycle (the \(A\)-chain passes through every
  candidate \(w\)), and \(T\) must be rebuilt outside \(X\) instead.
  REAL and frequent: 4,092/19,800 pairs (30/135 configs) on the witness,
  all repaired by the rebuild in the liberal test.  Needs a lemma:
  some \(w\in K\setminus X\) can be re-hung after re-routing the
  \(A\)-chain around it (the chain has \(\ge2\) vertex-disjoint
  alternatives by 3-arc-strongness — to be written).
* **O2 (\(U'\)-existence).**  With \(U\) re-chosen the surgery repaired
  105/105 configs; the missing lemma is: given \(T'\) with intermediate
  \(X'=X\sqcup S_w\), there is an in-arborescence \(U'\) arc-disjoint
  from \(T'\) with two exits from \(X'\).  Note \(u\) retains \(\ge2\)
  non-\(T'\) external arcs (\(|\delta^+(X)|\ge3\), all at \(u\), only
  \(a\in T'\)), but their heads may land in \(S_w\); the two-exit supply
  must be argued from \(\lambda\ge3\) plus the wedge.  An Edmonds-type
  extension argument (does one in-arborescence always leave room for a
  second with prescribed exits?) is the indicated route.
* **O3 (boundaries).**  \(|X|=1\) leaf and \(|X|=n-1\) root lemmas
  (team/30 gap; both ends now load-bearing).
* **O4 (rho-side labels).**  Repairs through \(\rho\) (the S5 \(z=\rho\)
  case and absorption exits \((w,\rho)\)) must respect the labelled
  two-preimage choice at the contracted root for the RECOLOR payoff.
