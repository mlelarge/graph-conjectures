# Adversarial verification of `proof_condL_dicut_acyclicity.md`

**Verifier role.** Adversarial — break the proof, not be charitable. Target:
Conditional L (the load-bearing open lemma toward Conjecture 9.2 of
arXiv:2304.04690). The document splits Conditional L into L1 (directed-Hajós lower
bound), L2 (glue/upper bound), L3 (criticality descent) and L4 (residual open).

**Method.** (1) Every load-bearing citation re-pulled from the *primary source PDFs*
(arXiv:1908.04096 for BJSS; arXiv:2304.04690 for AAC) via `pdftotext -layout`, not
from the prior-agent literature memos. (2) The L1 splice argument tested
computationally against 47 524 directed-Hajós joins (sym cycles, directed cycles,
bidirected K4, 2-vertex digons, random strong digraphs) with the spliced cycle
constructed and checked, plus criticality descent on 820 dicritical joins
(`scripts/adv_condL_verify.py`).

**Bottom line.** The COLOURING CORE (L1, L2, L3) is **rigorously correct at the value
the induction needs (BJSS-k = 3 / χ⃗ = 3)** — the splice argument is sound and the
citations, re-pulled from source, support it *at k = 3*. BUT the document contains
two real defects: **(D1)** every "verbatim" quote of BJSS Theorem 2(b)(c)(d) states
hypothesis **`k ≥ 2`**, whereas the arXiv source states **`k ≥ 3`** — a misquotation
of a load-bearing citation (non-fatal, because the needed instance is k = 3, but the
doc's "hold for k ≥ 2, hence at k = 2 (our χ⃗ = 3 case)" reasoning is index-confused);
and **(D2)** L4(i)'s claim that the tree-join lower bound "is NOT open — cite
Lemma 6.7 (k = 2)" **conflates Definition 1.6 with Definition 9.1**: Lemma 6.7 is about
the Def-1.6 Hajós tree join (every edge a block); Conjecture 9.2's `H₂` uses the
Def-9.1 *2-Hajós* tree join (A/B edge-partition, B-edges plain digons, even-parity
condition) — a strictly different construction Lemma 6.7 does not cover. L4(i) is
therefore **NOT closed by citation**; it is OPEN (or needs a Def-9.1 → Def-1.6
reduction the doc does not supply and that is obstructed by the B-digons/parity).

---

## 1. Citations re-pulled from primary source (MEMORY: do not trust pdftotext memos)

### 1.1 BJSS directed Hajós join = Def 1.5 — CONFIRMED

arXiv:1908.04096, §3 (verbatim):
> "Let D1 and D2 be two disjoint digraphs and select an arc u1 v1 and an arc v2 u2.
> Let D be the digraph obtained from the union D1 ∪ D2 by deleting the arcs u1 v1 as
> well as v2 u2, identifying the vertices v1 and v2 to a new vertex v, and adding the
> arc u1 u2. … D = D1 ▽ D2."

With u1 = u, u2 = w, this is Def 1.5 exactly. The doc's §0/§1 construction match is
**correct**.

### 1.2 BJSS Theorem 2 — CONFIRMED STATEMENT, but HYPOTHESIS MISQUOTED

arXiv:1908.04096, Theorem 2 (Hajós Construction), **verbatim**:
> "(a) χ⃗(D) ≥ min{ χ⃗(D1), χ⃗(D2)}.
> (b) If χ⃗(D1) = χ⃗(D2) = k and **k ≥ 3**, then χ⃗(D) = k.
> (c) If both D1 and D2 are k-critical and **k ≥ 3**, then D is k-critical.
> (d) If D is k-critical and **k ≥ 3**, then both D1 and D2 are k-critical."

The proof of (a) is exactly the splice `C1 ∪ C2 − u1v1 − v2u2 + u1u2`, **verbatim**
as quoted in the doc and memos. Part (a) carries **no k-hypothesis** — good.

**DEFECT D1.** The doc (`proof_condL_dicut_acyclicity.md` §3 L2 quote, §4 L3 quote)
and BOTH literature memos (`conditional_l_external_lit.md` §1, `conditional_l_literature.md`)
state parts (b)(c)(d) with "**k ≥ 2**". The arXiv source says "**k ≥ 3**." This is a
misquotation of the exact hypothesis of a load-bearing citation. Per project policy
("a misquoted theorem kills the step"; "phantom citations are worse than none"), it is
flagged. **It is NOT fatal**, because:

> A 2-extremal digraph has χ⃗ = 3, hence (Lemma 4.1 of AAC, §1.4 below) is
> **3-dicritical = BJSS 3-critical**. The induction consumes Theorem 2(b)(c)(d) at the
> value **k = 3**, and **3 ≥ 3**, so the source's actual hypothesis is satisfied.

The doc's phrasing in `proof_condL_hajos_lower_bound.md` §2 — *"All hold for k ≥ 2,
hence at k = 2 (our χ⃗ = 3 case)"* — is index-confused: "our χ⃗ = 3 case" is BJSS
**k = 3**, not k = 2. The conclusion (the theorems apply) is right; the stated reason
(k = 2) is wrong. Computationally 2(b) also happens to hold at BJSS-k = 2 (324
chi=2-pair joins, 0 violations), so the k ≥ 3 restriction in BJSS is conservative for
(b) on these instances — but that is irrelevant: the doc must cite the hypothesis the
source actually states, and must invoke it at k = 3.

### 1.3 AAC Lemma 5.3 / Claim 5.3.1 — CONFIRMED (and consistent with citing BJSS at 3)

arXiv:2304.04690, Lemma 5.3 (k ≥ 1), verbatim opening:
> "Claim 5.3.1 (Theorem 2 in [3]). D is k+1-dicritical if and only if both D1 and D2
> are."

So AAC itself invokes BJSS Thm 2 at **(k+1)-dicritical**. For Conjecture 9.2 (AAC
k = 2) the needed instance is **(k+1) = 3-dicritical = BJSS Thm 2 at 3** — valid.
(AAC's own Lemma 5.3 is stated for k ≥ 1, so AAC at k = 1 would invoke BJSS at
2-dicritical, outside BJSS's stated k ≥ 3 — but that is off the 9.2 path and is AAC's
issue, not the doc's.)

### 1.4 AAC Lemma 4.1 — CONFIRMED (non-circularity of L3 is sound)

arXiv:2304.04690, line 488, verbatim:
> "Lemma 4.1. Let k ≥ 1, and let D be a k-extremal digraph. Then D is Eulerian,
> (k+1)-dicritical and …"

So 2-extremal ⇒ 3-dicritical. The doc's non-circularity argument (L3 applies to the
literal join because a 2-extremal D is in fact 3-dicritical) is **sound**.

### 1.5 AAC Lemma 6.7 vs Definition 9.1 — the L4(i) DEFECT

arXiv:2304.04690, **Lemma 6.7 (k ≥ 2)**, verbatim:
> "Let k ≥ 2. Let D, D1, …, Dn be digraphs such that D is a Hajós tree join of the Di.
> Then D is k-extremal if and only if all digraphs D1, …, Dn are k-extremal."

Its proof opens "Let D = T(D1,…,Dn;C) where T, C, D1,…,Dn are as in **Definition 1.6**."
The forward lower bound is indeed k-general (no k ≥ 3). **But Definition 1.6 is NOT
Definition 9.1.** Re-pulled verbatim:

- **Def 1.6 (Hajós tree join):** a plane tree with edges {u1v1,…,unvn}; for *each*
  edge a digraph Di with `[ui,vi] ⊆ A(Di)`; D = (the Di − [ui,vi]) + peripheral cycle.
  **No (A,B) partition, no plain-digon B-edges, no parity condition.**
- **Def 9.1 (2-Hajós tree join):** a plane tree, a **partition (A,B)** of its edges
  "such that every leaf-to-leaf path in T contains an **even number of edges of B**";
  each A-edge carries a block Di, **each B-edge becomes a plain digon**, plus the
  peripheral cycle. "If A = ∅, the result is a generalised wheel."

`H₂` (Conjecture 9.2) is closed under the **Def-9.1** 2-Hajós tree join.

**DEFECT D2.** `proof_condL_dicut_acyclicity.md` §5 L4(i) asserts:
> "the tree-join half of Conditional L is already a theorem at k=2, citable as Lemma
> 6.7 … L4(i) is NOT open after all for the lower bound — cite Lemma 6.7 (k=2) … What
> remains is only matching the team's abstract tree-join seam … to Def 9.1's
> T(D1,…;C) so Lemma 6.7 applies verbatim; that is a parsing/structural identification."

This is **wrong**. Lemma 6.7 covers Def 1.6, whose every edge is a block; it never
mentions an A/B partition, plain-digon B-edges, or the even-parity condition that are
**constitutive** of Def 9.1. The B-edges of Def 9.1 are plain digons, NOT blocks
`Di − [ui,vi]`; trying to view a B-digon as a Def-1.6 block Di = the digon makes
`Di − [ui,vi]` empty, which does not reproduce the digon. And the even-parity-of-B
condition has no counterpart in Def 1.6. So Def 9.1 is **not** a verbatim instance of
Def 1.6, and the "parsing/structural identification" the doc claims does not exist as
stated. **L4(i) is OPEN for the lower bound**, contrary to the doc's headline; at most
it reduces to a non-trivial Def-9.1 → Def-1.6 reduction that the doc neither supplies
nor shows to be possible (and the B-digons/parity obstruct the naive attempt).

(Note: AAC §9 itself only says membership "is a routine work to check" — it gives *no*
lemma number for the Def-9.1 forward direction, consistent with L4(i) being genuinely
unproved in the literature.)

---

## 2. The L1 splice argument (the "open heart") — logic

L1's proof (doc §2, and the cleaner `proof_condL_hajos_lower_bound.md` §3) is the
splice. Adversarial reading of each load-bearing step:

- **"A monochromatic dicycle C1 of D1 must use the deleted arc u→v1."** Sound:
  `D1 − uv1 = D[S1] ⊆ D`, and φ is acyclic on D, so any mono dicycle of D1 not using
  `uv1` would be a mono dicycle of D — impossible. The only arc of D1 absent from D is
  exactly `u→v1`, so C1 uses it. ✓
- **Colour pinning φ(u)=φ(v)=φ(w).** C1 mono and contains `u→v1=u→v` ⇒ φ(u)=φ(v); C2
  mono and contains `v2→w=v→w` ⇒ φ(w)=φ(v). ✓
- **Splice is a SINGLE simple directed cycle.** P1 = C1 − (u→v) is a `v⇝u` dipath in
  S1; P2 = C2 − (v→w) is a `w⇝v` dipath in S2; W = (u→w)·P2·P1. Internal vertices of P1
  ⊆ S1∖{v}, of P2 ⊆ S2∖{v}, and S1∩S2 = {v}, so they meet only at v. Adversarial edge
  cases checked: u ≠ w always (u keeps its D1 label, w is fresh from D2; both ≠ v); no
  vertex repeats except the closing v. ✓ A closed directed walk all in one colour
  contains a mono dicycle ⇒ contradicts φ valid on D. ✓

**The cross-seam acyclicity that `lemma_a_proof.md` §3/§5 flagged "unverified" is
genuinely verified by this splice.** It matches BJSS's own one-line
`C1 ∪ C2 − u1v1 − v2u2 + u1u2` (verbatim, §1.2 above). **L1 is PROVED.**

**Computational corroboration (evidence only; `scripts/adv_condL_verify.py`):**
- 47 524 directed-Hajós joins over an adversarial piece pool (sym C3/C5/C7, directed
  C3/C4/C5, bidirected K4, 2-vertex digon, 15 random strong digraphs), all arc
  choices: **0 lower-bound failures**.
- **Splice claim** (heart of L1): for every 2-dicolouring of every join, at least one
  side-restriction is a valid 2-dicolouring of its piece — **0 failures** over the
  joins with n ≤ 11.
- **Splice construction**: 46 068 spliced objects built from manufactured
  side-dicycles C1, C2 and checked to be genuine *simple* directed cycles in D — **0
  non-cycles**. Directly validates proof step 3.
- **Criticality descent (L3)**: 820 3-dicritical joins, both pieces 3-dicritical in
  every case — **0 failures**.

This is evidence, not proof; but it fails to refute L1/L2/L3, consistent with their
being theorems.

---

## 3. Per-step verdict

| Step | Claim | Verdict |
|---|---|---|
| **L1** | χ⃗(D₁▽D₂) ≥ min χ⃗(Dᵢ); cross-seam splice | **PROVED.** Logic airtight; = BJSS Thm 2(a) (no k-hyp), re-pulled verbatim; 0/47 524 + 0/46 068 computational. |
| **L2** | seam-agreeing glue, χ⃗(D)=k | **PROVED at the needed value k=3.** = BJSS Thm 2(b). **Citation MISQUOTED** (doc says k≥2; source says k≥3). Application valid because the instance is k=3. |
| **L3** | criticality descent, literal join | **PROVED at k=3.** = BJSS Thm 2(c)(d) **misquoted as k≥2** (source k≥3); applied at k=3 (valid). Non-circularity via AAC Lemma 4.1 (re-pulled, real). The doc's own "minimality transport by citation" caveat stands. |
| **L4(i)** | tree-join lower bound "= Lemma 6.7 (k=2)" | **OVERCLAIM / OPEN.** Lemma 6.7 is about **Def 1.6**, NOT the **Def-9.1** 2-Hajós tree join of Conjecture 9.2 (A/B partition, B-digons, even parity). The "parsing/structural identification" the doc invokes does not exist as stated. **Lower bound for the Def-9.1 seam is NOT closed by citation.** |
| **L4(ii)** | cut ⇒ factorisation (Lemma A sufficiency) | **OPEN** — correctly labelled by the doc; structural/connectivity, outside BJSS; AAC's k=2 decomposition has no analogue (its Thm 5.1 is k≥3). Concur. |
| **L4(iii)** | 2-extremal ⇒ 3-dicritical seam survival | Reduces to L4(ii) for the literal join via Lemma 4.1; concur. |

---

## 4. Net verdict

**Is the proof airtight? NO — but the colouring CORE is sound.**

- **L1, L2, L3 are mathematically correct at the value the induction needs (k = 3 /
  χ⃗ = 3).** The splice/cross-seam-acyclicity argument — the thing `lemma_a_proof.md`
  §3/§5 called the "genuinely OPEN heart" — is **PROVED** for the **literal directed
  Hajós join**. The doc's headline correction (that the directed-Hajós-join instance is
  BJSS Thm 2, not open) is **substantively right**.

- **Two real defects must be fixed before the doc is publishable:**
  - **D1 (cosmetic-to-load-bearing):** the BJSS Thm 2(b)(c)(d) hypothesis is **k ≥ 3**,
    not k ≥ 2 as the doc and both memos quote. Replace every "k ≥ 2" by "k ≥ 3" and
    state the application is at **k = 3** (justified by χ⃗ = 3 + Lemma 4.1), removing the
    index-confused "hence at k = 2" phrasing. Non-fatal, but a misquoted citation.
  - **D2 (substantive):** L4(i) is **NOT** closed by Lemma 6.7. Lemma 6.7 ⇒ Def 1.6
    ≠ Def 9.1. The tree-join lower bound for the **2-Hajós tree join** (B-digons +
    even-parity) is genuinely **OPEN** (or requires an unstated, non-trivial reduction).
    The doc's claim "L4(i) is NOT open after all" is an **overclaim** and must be
    downgraded to OPEN.

- **L4(ii) (cut ⇒ factorisation / Lemma A sufficiency) remains OPEN** — the doc says so
  and is correct; it is the genuine structural wall.

So: the **directed-Hajós-join** half of Conditional L is proved (colouring wall down
for that seam). The **2-Hajós-tree-join** half (L4(i)) is **still open** — the doc
mistakenly declared it closed by miscitation. The connectivity wall (L4(ii)) stands.
Conditional L as a whole (which must cover the Def-9.1 tree-join seam used by `H₂`) is
therefore **NOT fully proved** by this document.

---

### Provenance
- BJSS Thm 2 + directed-Hajós-join def: arXiv:1908.04096, §3 / Thm 2, re-pulled
  `pdftotext -layout` this pass. Hypothesis **k ≥ 3** for (b)(c)(d); (a) has none.
- AAC Lemma 4.1 (k≥1), Lemma 5.3/Claim 5.3.1, Lemma 6.7 (k≥2, Def 1.6), Def 1.6,
  Def 9.1, Conjecture 9.2: arXiv:2304.04690, re-pulled this pass.
- Computational: `scripts/adv_condL_verify.py` (reuses `scripts/h2_oracle.py`
  primitives) — 47 524 joins / 46 068 splice constructions / 820 dicritical joins,
  0 failures. Evidence only. No `.venv` created; no files outside
  `two_extremal_digraphs/` touched.
