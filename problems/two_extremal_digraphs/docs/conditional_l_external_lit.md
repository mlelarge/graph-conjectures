# Conditional L in the external literature — directed Hajós join & dichromatic number

**Analyst task.** Does "the directed Hajós join of two digraphs each with `χ⃗ ≥ k` has
`χ⃗ ≥ k`" (= Conditional L, the digraph Hajós lower bound) appear as a *theorem*? Who
proved it, where, with which number? What about the converse/decomposition direction
(if a Hajós join is `k`-dicritical, are the factors `k`-dicritical)? And the surrounding
directed Hajós/Ore criticality theory.

**Bottom line up front.** **YES — Conditional L is a published theorem.** It is
**Theorem 2(a)** of Bang-Jensen, Bellitto, Schweser & Stiebitz, *Hajós and Ore
constructions for digraphs*, **Electron. J. Combin. 27(1) (2020), #P1.63** (arXiv:1908.04096).
The **converse/decomposition** direction is **also a published theorem** there:
**Theorem 2(d)**. Both are stated and proved verbatim below from the EJC PDF. This means
the "load-bearing open heart of Lemma A and Lemma B" is, in its bare directed-Hajós-join
form, **NOT open in the literature** — it is a 5-line proof in BJSS 2020. The genuinely
open part is whatever is *specific to the 2-extremal gluing across a seam that is not
literally a directed Hajós join* (the tree-join / generalised-wheel seam of Def 9.1, and
the promotion of a `U(D)`-cut to a Hajós factorisation). See §4 for the exact boundary.

All quotes below were extracted from the EJC published PDF
(`https://www.combinatorics.org/ojs/index.php/eljc/article/download/v27i1p63/pdf/`,
converted with `pdftotext`; arrows over χ in the source denote the dichromatic number χ⃗).

---

## 0. The source paper (pinned)

> **Jørgen Bang-Jensen, Thomas Bellitto, Thomas Schweser, Michael Stiebitz.**
> *Hajós and Ore constructions for digraphs.* The Electronic Journal of Combinatorics
> **27(1)** (2020), Paper #P1.63. arXiv:1908.04096 (submitted 12 Aug 2019).

This is exactly the paper named in the task brief ("Bang-Jensen-Bellitto-Schweser-Stiebitz
directed Hajós"). I read the full text; it is the canonical reference for directed Hajós
theory and the dichromatic number.

### Definitions exactly as BJSS state them (so we know we are matching Conditional L)

**Dichromatic number / k-coloring (their §1, after Neumann-Lara [27]).** Quote:

> "Following Neumann-Lara [27], a k-coloring of a digraph D is a mapping
> φ : V(D) → {1,2,…,k}, such that for each color α ∈ {1,2,…,k} the color class
> φ⁻¹(α) = {v ∈ V(D) | φ(v) = α} induces an acyclic subdigraph of D, i.e. a subdigraph
> that does not contain any directed cycles. The dichromatic number χ⃗(D) of a digraph D
> is the minimum integer k ⩾ 0 such that D admits a k-coloring."

This is **identical** to the χ⃗ used in `docs/lemma_a_proof.md` (colour classes induce
acyclic subdigraphs; a "≤2-dicolouring" is a 2-coloring in their sense). Match confirmed.

**k-critical / dicritical.** Quote:

> "A digraph D is critical and k-critical if χ⃗(D) = k but χ⃗(D′) < k for each proper
> subdigraph of D."

(BJSS say "critical"; the target paper / your notes say "dicritical" — same object.)

**Directed Hajós join (their §3), attributed to Hoshino–Kawarabayashi [15].** Quote:

> "Let D1 and D2 be two disjoint digraphs and select an arc u1v1 of D1 as well as an arc
> v2u2 of D2. Let D be the digraph obtained from the union D1 ∪ D2 by deleting both arcs
> u1v1 and v2u2, identifying the vertices v1 and v2 to a new vertex v, and adding the arc
> u1u2. We say that D is the (directed) Hajós join of D1 and D2 and write
> D = (D1,v1,u1)▽(D2,v2,u2) or, briefly, D = D1▽D2."

**Match check against Def 1.5 in your brief.** Your brief: "from D1 with arc u→v1 and D2
with arc v2→w, delete those arcs, identify v1=v2=v, add arc u→w." BJSS: delete u1v1 (=u→v1)
and v2u2 (=v2→u2, i.e. v2→w with w=u2), identify v1=v2=v, add u1u2 (=u→w). **Identical
construction** (their u1=your u, their u2=your w). The directed Hajós join of the brief
**is** the BJSS directed Hajós join. The construction is originally due to **Hoshino &
Kawarabayashi, *The edge density of critical digraphs*, Combinatorica 35 (2015) 619–631**
(BJSS ref [15]); statement (c) below "has already been mentioned in [15, Proposition 2]".

---

## 1. CONDITIONAL L IS A THEOREM — BJSS Theorem 2(a) (the directed Hajós lower bound)

**Theorem 2 (Hajós Construction), BJSS 2020, verbatim:**

> "**Theorem 2 (Hajós Construction).** Let D = D1▽D2 be the Hajós join of two disjoint
> non-empty digraphs D1 and D2. Then, the following statements hold:
> **(a)** χ⃗(D) ⩾ min{χ⃗(D1), χ⃗(D2)}.
> **(b)** If χ⃗(D1) = χ⃗(D2) = k and k ⩾ 2, then χ⃗(D) = k.
> **(c)** If both D1 and D2 are k-critical and k ⩾ 2, then D is k-critical.
> **(d)** If D is k-critical and k ⩾ 2, then both D1 and D2 are k-critical."

**Part (a) IS Conditional L.** If both factors have χ⃗ ≥ k, then
`χ⃗(D) ≥ min{χ⃗(D1),χ⃗(D2)} ≥ k`. In the contrapositive form your team needs ("the
directed Hajós join of digraphs each not 2-dicolourable is not 2-dicolourable"): set k=3,
χ⃗(D1),χ⃗(D2) ≥ 3 ⇒ χ⃗(D) ≥ 3, i.e. D is not 2-dicolourable. **This is precisely the
"digraph Hajós lower bound" the synthesis calls OPEN.** It is published and proved.

**BJSS's proof of (a), verbatim (it is the across-the-seam acyclicity argument your
`lemma_a_proof.md §3` calls "the unverified heart"):**

> "For the proof of (a) let χ⃗(D) = k and let φ be a k-coloring of D. For i ∈ {1,2}, let
> φi denote the restriction of φ to Di, where φi(vi) = φ(v). We claim that either φ1 is a
> k-coloring of D1 or φ2 is a k-coloring of D2. Otherwise, in D1 there is a monochromatic
> directed cycle C1 that contains the arc u1v1 (as D1−u1v1 is a subdigraph of D and
> therefore k-colorable). Similar, in D2 there exists a monochromatic cycle C2 that
> contains the arc v2u2. But then, C1 ∪ C2 − u1v1 − v2u2 + u1u2 is a monochromatic
> directed cycle in D, a contradiction. This proves (a)."

This is the **complete** lower-bound argument: any monochromatic directed cycle in a
factor that is forced to use the deleted arc splices, **across the seam through the added
arc u1u2 = u→w and the identified vertex v**, into a monochromatic directed cycle of D.
The directed acyclicity "across the seam through the added arc u→w and the identified
vertex v" that the synthesis flags as unverified is handled here by the splice
`C1 ∪ C2 − u1v1 − v2u2 + u1u2`. **This closes Conditional L for the literal directed
Hajós join.**

**The gluing/upper-bound companion (Conditional U analogue) is Theorem 2(b), verbatim
proof:** for k-colorings φ1, φ2 of D1, D2 permuted so φ1(v1)=φ2(v2), the union φ is shown
to be a k-coloring of D because "D would contain a monochromatic directed cycle C with
{u1,u2,v} ⊆ V(C) and u1u2 ∈ A(C). But then, (C∩D1)+u1v1 is a monochromatic directed cycle
in D1, which is impossible." So **two seam-agreeing k-colorings DO glue** — Theorem 2(b)
is exactly the "two seam-agreeing ≤2-dicolourings glue to a ≤2-dicolouring of D" statement
of your §3, *proved*, for the directed-Hajós-join seam.

---

## 2. THE CONVERSE / DECOMPOSITION DIRECTION IS A THEOREM — BJSS Theorem 2(d)+(c)

The brief asks: "if a Hajós join is k-dicritical, are the factors k-dicritical?"

**Answer: YES, this is Theorem 2(d) (quoted above): "If D is k-critical and k ⩾ 2, then
both D1 and D2 are k-critical."** And the forward direction is 2(c): "If both D1 and D2
are k-critical and k ⩾ 2, then D is k-critical." So criticality is preserved **in both
directions** across a directed Hajós join. The proof of (d) (verbatim in BJSS) again uses
the splice `C1 ∪ C2 − u1v1 − v2u2 + u1u2` to derive a monochromatic cycle in D−a from
monochromatic cycles in the two factors.

**Relevance to your Lemma B.** Theorem 2(d) is exactly the descent your "Lemma B
(reduction soundness)" wants for the χ⃗=3 part *when the seam is a literal directed Hajós
join*: if the assembled D is 3-dicritical and D = D1▽D2, then each Di is 3-dicritical
(hence χ⃗(Di)=3). **BUT note the gap (see §4):** 2-extremal ≠ 3-dicritical. A 2-extremal
digraph has χ⃗=3 but need not be dicritical (it can have removable arcs). BJSS 2(d) gives
you criticality descent, not "2-extremal descent". The χ⃗(Di) ≥ 3 half does follow from
2(d) **provided** D itself is dicritical; for a non-dicritical 2-extremal D one must first
pass to a dicritical subdigraph, and the seam need not survive that passage. This is a
real, narrow gap — but it is about *2-extremality*, not about the Hajós lower bound, which
is settled.

---

## 3. The surrounding directed Hajós/Ore criticality theory (pinned, for context)

**Theorem 4 (the directed Hajós characterisation), verbatim:**

> "**Theorem 4.** Let k ⩾ 3 be an integer. A digraph has dichromatic number at least k
> if and only if it contains a Hajós-k-constructible subdigraph."

where (BJSS, end of §3): "the class of **Hajós-k-constructible** digraphs [is] the
smallest family of digraphs that contains all bidirected complete graphs of order k and
is closed under Hajós joins and identifying independent vertices." This is the directed
analogue of Hajós's 1961 theorem. **Identifying independent vertices** is their second
constructor: H = D/(I→v) with `χ⃗(D/I) ⩾ χ⃗(D)` (proved trivially: any coloring of D/I
extends to D). This is the digraph **Hajós/Ore** machine; the target conjecture's `H₂`
class (closed under directed Hajós join + a tree-join) is a **2-extremal-specialised
relative** of this Hajós-k-constructible class.

**Theorem 8 (strong connectivity is preserved), verbatim:**

> "**Theorem 8.** Let k ⩾ 3 be an integer and let D be a Hajós-k-constructible digraph.
> Then, D is strongly connected."
> Proof idea (verbatim): "if D1 and D2 are strongly connected, then the directed Hajós-join
> of D1 and D2 is strongly connected, too, as vertices on directed cycles are still on
> directed cycles after the Hajós join."

This **proves the (S) "strong" clause of your Lemma B for the directed-Hajós-join seam**
(your `verify_lemma_b.md` (S) clause), independently and rigorously. Worth citing in
Lemma B in place of the ad hoc "Eulerian + weakly connected ⇒ strong" line for the
assembly direction.

**Ore/Urquhart-type (needs the *bidirected* Hajós join too) — Theorems 10, 13:**
Theorem 13: "A digraph has dichromatic number at least k if and only if it is
Ore-k-constructible" (using directed **and** bidirected Hajós/Ore joins). The key warning
for your team — BJSS prove Urquhart's "is itself constructible" theorem **fails** for the
*directed* Hajós join alone and needs the **bidirected** join. This is structurally why
your `H₂` needed a second constructor (the tree-join) beyond the plain directed Hajós join.

**Gallai-type theorem for dicritical digraphs — Theorem 15** (low-vertex subdigraph
structure), using **Harutyunyan & Mohar** [14] "Gallai's theorem for list coloring of
digraphs" (SIAM J. Discrete Math.) as Theorem 16. This is the BJSS link to the
**Harutyunyan–Mohar** line named in the brief. (Harutyunyan–Mohar [13] "Strengthened
Brooks Theorem for digraphs of girth …" is the directed Brooks input.)

**Edge-density lower bound — Theorem 18 (digon-free (k+1)-critical):**
`2|A(D)| ⩾ (2k + k/(3k+1))|D|`. Context for criticality only; not load-bearing here.

**Origin of χ⃗:** Neumann-Lara [27], *The dichromatic number of a digraph*, J. Combin.
Theory Ser. B (the brief's "Neumann-Lara dichromatic number"). BJSS cite him as the source
of the k-coloring definition.

---

## 4. EXACT BOUNDARY: what BJSS settles vs. what stays open for Conjecture 9.2

**SETTLED by BJSS 2020 (stop re-deriving these):**
- Conditional L for a *literal* directed Hajós join D=D1▽D2: `χ⃗(D) ≥ min{χ⃗(D1),χ⃗(D2)}`
  — **Theorem 2(a)**. The cross-seam acyclicity is the splice
  `C1∪C2 − u1v1 − v2u2 + u1u2`.
- The gluing/upper bound `χ⃗(D)=k` when both factors are k — **Theorem 2(b)**.
- Criticality descent both ways across a directed Hajós join — **Theorem 2(c),(d)**.
- Strong connectivity preserved under the directed Hajós join — **Theorem 8**.
- The full Hajós characterisation `χ⃗ ≥ k ⇔ Hajós-k-constructible subdigraph` —
  **Theorem 4**.

**Therefore the part of `lemma_a_proof.md §3 / §5` that says "the digraph analogue of the
classical Hajós lower bound … is genuinely OPEN" is INACCURATE for the literal directed
Hajós join.** It is BJSS Theorem 2(a), with a complete 5-line proof. The "1680 χ-violating
joins / 4.16M broken-piece joins / no proof" search was searching for a theorem that
already exists.

**STILL GENUINELY OPEN (BJSS does NOT cover these), and this is where the real work is:**

1. **The non-directed-Hajós seam.** Conjecture 9.2's `H₂` is closed under the directed
   Hajós join **and** the "non-empty-A 2-Hajós tree-join" (Def 9.1) / generalised-wheel
   base. BJSS Theorem 2 is **only** about the directed Hajós join `D1▽D2`. For the
   *tree-join* seam (your clause (b)), there is **no BJSS theorem**; the splice
   `C1∪C2 − u1v1 − v2u2 + u1u2` is for a single added arc and a single identified vertex,
   not a seam distributed across a digon forest with an A-edge. **Conditional L for the
   tree-join seam is the actual open lemma** — and it is *not* in BJSS. The brief's framing
   of Conditional L as "the directed Hajós join … lower bound" is only half the target; the
   live half is the tree-join generalisation.

2. **Cut ⇒ factorisation (Lemma A sufficiency).** Promoting a mixed-2-cut of `U(D)` to a
   genuine directed-Hajós (or tree-join) factorisation of D is **not** a Hajós-coloring
   statement at all; BJSS says nothing about *recognising* a join from connectivity data.
   Theorem 2 assumes you are *given* D=D1▽D2. So `(A′-suff-a)`/`(A′-suff-b)` in
   `lemma_a_proof.md §4` remain open and are **outside BJSS's scope** — no external help.

3. **2-extremal ≠ k-dicritical.** Theorem 2(d) descends *criticality*; your Lemma B needs
   descent of *2-extremality* (χ⃗=3 **plus** Eulerian/strong/λ=2/2-connected-underlying).
   2(d) handles χ⃗ only after reducing to a dicritical subdigraph, and that reduction can
   destroy the seam. So Conditional L-via-2(d) closes χ⃗(Di) ≥ 3 **for the directed-Hajós
   seam on a dicritical D**, not for a general 2-extremal D. Narrow but real.

**Net effect on the project:** Conditional L should be **split**. Its directed-Hajós-join
instance is *closed by citation* (BJSS Thm 2(a),(b),(d) + Thm 8). The remaining open content
is (i) the **tree-join seam** lower bound (not in the literature — must be proved here, very
plausibly by extending the BJSS splice argument to the multi-seam Def-9.1 join), and
(ii) the **cut⇒factorisation** sufficiency, which is a connectivity/structure problem BJSS
does not address. Citing BJSS removes the directed-Hajós half of both "walls" and focuses
the remaining work precisely.

---

## 5. Caveats / what I could NOT verify

- I quoted from the **EJC published PDF** (pdftotext). The arXiv version (1908.04096) has
  the same theorem numbering per the abstract, but I did not line-by-line diff the two; if
  you cite a specific line, prefer the EJC #P1.63 PDF I read.
- **Hoshino–Kawarabayashi [15], Combinatorica 35 (2015) 619–631, "Proposition 2":** BJSS
  attribute the directed Hajós join and statement (c) to it. I did **not** obtain the
  Hoshino–Kawarabayashi paper itself; I only have BJSS's attribution. Do **not** cite
  "Hoshino–Kawarabayashi Proposition 2" verbatim without pulling that paper — I cannot
  confirm its exact statement. (The *construction* attribution is safe; the *lower-bound
  Theorem 2(a)* is a BJSS statement and proof.)
- **Stehlík, arXiv:1910.02454, "Critical digraphs with few vertices"** is BJSS ref [32];
  their Theorem 22 (k-critical digraph on ≤ 2k−1 vertices is a directed Hajós join /
  Dirac join) is relevant to *small* dicritical structure but I did not fetch Stehlík's
  paper; cite via BJSS or fetch directly before relying on it.
- I did **not** find any *separate* paper stating "directed Hajós join preserves
  χ⃗ ≥ k" — it lives inside BJSS Theorem 2. No competing/earlier independent statement
  surfaced (Hoshino–Kawarabayashi is the construction's origin, BJSS is the coloring
  theorem's origin among the sources I read).
- The target paper **Aboulker–Aubian–Charbit, arXiv:2304.04690, "Digraph Colouring and
  Arc-Connectivity"** — I confirmed (abstract + HAL thesis hit) that it "introduces a
  generalization of Hajós join that gives a new way to construct families of dicritical
  digraphs," consistent with `H₂`/Def 9.1 being a Hajós-type construction. I could **not**
  extract Conjecture 9.2 / the `H₂` definition / its citation of BJSS Thm 2 from the
  abstract page (full PDF body not rendered). Verify the in-paper citation of BJSS Thm 2
  by reading the 2304.04690 PDF directly.

---

## Sources

- Bang-Jensen, Bellitto, Schweser, Stiebitz, *Hajós and Ore constructions for digraphs*,
  Electron. J. Combin. 27(1) (2020) #P1.63 —
  https://www.combinatorics.org/ojs/index.php/eljc/article/view/v27i1p63
  (PDF: https://www.combinatorics.org/ojs/index.php/eljc/article/download/v27i1p63/pdf/);
  arXiv:1908.04096 — https://arxiv.org/pdf/1908.04096
- Aboulker, Aubian, Charbit, *Digraph Colouring and Arc-Connectivity*, arXiv:2304.04690 —
  https://arxiv.org/abs/2304.04690
- Hoshino, Kawarabayashi, *The edge density of critical digraphs*, Combinatorica 35 (2015)
  619–631 — https://link.springer.com/article/10.1007/s00493-014-2862-4 (NOT independently
  read; cited via BJSS [15])
- Neumann-Lara, *The dichromatic number of a digraph*, J. Combin. Theory Ser. B (BJSS [27])
- Harutyunyan, Mohar, *Gallai's theorem for list coloring of digraphs*, SIAM J. Discrete
  Math. (BJSS [14]); *Strengthened Brooks Theorem for digraphs of girth …* (BJSS [13])
- Stehlík, *Critical digraphs with few vertices*, arXiv:1910.02454 (BJSS [32]; NOT
  independently read)
