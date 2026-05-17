# 16 — OLS strong-arc-decomposition novelty check

Author: Proof Auditor / Literature Reviewer
Date: 2026-05-16
Status: Deliverable for the Route B literature gate
(`team/13_publishability_decision.md` §5). Due 2026-06-06; delivered
early.

Companions: `team/05_audit.md` Appendix A.5 (the round-2 CL1 novelty
check, NOVEL verdict); `team/11_cl1_proof_v1.md` §5.1, §6.2
(Structural Specialist's CL1 statement and the publication
self-assessment); `team/13_publishability_decision.md` §3, §4 (Lead's
Route B commitment with OLS as the target class).

Scope. The CL1 lemma itself was found NOVEL in round 2
(`team/05_audit.md` Appendix A.5). The *application*'s novelty is the
present question: is the claim "every 3-arc-strong OLS digraph has a
strong arc decomposition, modulo the four BJG–Yeo 2020 exceptions" a
published theorem, an immediate corollary of a published theorem, or
genuinely new?

---

## §1 — The Route B theorem statement (verbatim)

From `team/13_publishability_decision.md` §4, the precise Route-B
target as committed by the Lead:

> Every 3-arc-strong out-locally-semicomplete digraph admits a strong
> arc decomposition, modulo the exception family inherited from
> BJG–Yeo 2020's semicomplete-composition obstructions
> ($S_4$, $\vec C_3[\overline K_2^3]$,
> $\vec C_3[\overline K_2, \overline K_2, P_2]$,
> $\vec C_3[\overline K_2, \overline K_2, \overline K_3]$) when they
> appear as the round-component kernel.

Call this Theorem B for brevity. The four exceptions are inherited
because the round-decomposition kernel that CL1 consumes is, in the
OLS regime, a semicomplete component; BJG–Yeo 2020 Theorem 1.4 lists
exactly these four obstructions for semicomplete-composition SAD.

## §2 — OLS class boundaries

Class definitions (verbatim from `team/02_structural_program.md` §3
Rank 1 and from Bang-Jensen 1990 §1):

- **OLS** (out-locally-semicomplete). For every $v\in V(D)$, the
  out-neighborhood $N^+(v)$ induces a semicomplete digraph. No
  constraint on $N^-(v)$.
- **ILS** (in-locally-semicomplete). For every $v$, $N^-(v)$ is
  semicomplete. No constraint on $N^+(v)$.
- **LS** (locally semicomplete) = OLS $\cap$ ILS. Both neighborhoods
  semicomplete. This is the class Bang-Jensen 1990 introduced and
  Bang-Jensen–Huang 2012 (JCTB) classified for SAD.

Strict containment LS $\subsetneq$ OLS holds: any digraph with a
vertex $v$ such that $N^-(v) = \{u_1, u_2\}$ and $u_1u_2, u_2u_1
\notin A(D)$, but with the OLS condition holding everywhere, is
OLS but not ILS, hence not LS. Such examples are abundant (e.g., a
source vertex feeding a tournament that itself has more than one
predecessor structure inside a larger digraph).

The novelty question reduces to: **does any published theorem assert
a SAD result whose hypothesis is *implied by* "3-arc-strong OLS"?**
A theorem on LS does not suffice (LS $\subsetneq$ OLS), unless its
proof is one-sided in a way that ports to OLS without modification —
which the Auditor must check, not just assert.

## §3 — Precedent table

Sources surveyed by direct PDF read where open
(arXiv:2309.06904v1 → `/tmp/bjwang2025.txt`,
arXiv:2408.02260v1 → `/tmp/aietal2024.txt`,
arXiv:1903.12225 already in `team/05` Appendix A.5,
the Bang-Jensen–Guo classification preprint
`cs.rhul.ac.uk/.../classif2.pdf` → `/tmp/bjguo_classif.txt`),
by abstract for paywalled (BJ 1990; BJ–Huang 1995/2012; BJ–Huang–Prisner
1993; Huang 1995; BJG textbook Ch. 5; BJG–Gutin 2018 Springer
"Classes of Digraphs" Ch. 6), and by cross-reference for the
remainder. Verbatim quotation marked **[verbatim]**; secondary
paraphrase marked **[2°]**.

| Source | Result on the OLS / LS / ILS class | Relation to Route B theorem (Theorem B) | Verdict |
|---|---|---|---|
| **Bang-Jensen 1990** [2°] (J. Graph Theory 14, 371–390). Introduces LS digraphs. Main results: Hamiltonian path; strong $\Rightarrow$ Hamiltonian cycle. No SAD theorem. | **Two-sided** LS throughout (verified via Bang-Jensen–Guo 2004, `/tmp/bjguo_classif.txt` line 26: "*for every vertex $x$ the set of in-neighbors and the set of out-neighbors each induce a semicomplete digraph*"). | OLS $\supsetneq$ LS not addressed. | No implication for Theorem B. |
| **Bang-Jensen–Huang–Prisner 1993** [2°] (JCTB 59, 267–287). In-tournament digraphs (oriented version of ILS). Main result: every strong in-tournament is Hamiltonian; by symmetry, the same for out-tournaments. | One-sided class, but conclusion is Hamiltonicity, not SAD. One Hamilton cycle does not give two arc-disjoint strong spanning subdigraphs. | None. | No implication for Theorem B. |
| **Bang-Jensen 1995 / Huang 1995** [2°]. Round decomposition for connected LS digraphs (completed in Bang-Jensen–Guo 2004 Theorem 3.12, `/tmp/bjguo_classif.txt` line 132). | Round decomposition uses **two-sided** LS hypothesis. The Lead's `team/13` §4 footing — "Strong OLS digraphs admit a round decomposition (BJ–Huang 1995 / Huang 1995)" — is **stronger than what the literature actually proves**: published statements are LS-only. The Lead's claim is a *conjecture*, not a citation. | If true, OLS gets a kernel-extraction tool; but truth must be re-proved in `team/14_*`. No SAD follows even on optimistic reading. | Caveat (c) in §4 below. |
| **Bang-Jensen–Huang 2012** (JCTB 102, 701–714, "Decomposing locally semicomplete digraphs into strong spanning subdigraphs"). The flagship LS-SAD paper. **[verbatim via `/tmp/bjwang2025.txt` lines 82–84]** "*Theorem 1.3 [7] A 2-arc-strong locally semicomplete digraph $D$ has a strong arc decomposition if and only if $D$ is not the square of an even cycle. Every 3-arc-strong locally semicomplete digraph has a strong arc decomposition.*" | Hypothesis is **two-sided** LS. Proof (per `team/05` A.5 §3) uses round decomposition + recursion to BJ–Yeo 2004; both ingredients are LS-only as published. Structural Specialist in `team/02` §3 Rank 1: "ILS strictly contains locally semicomplete and is **not** subsumed by BJ–Huang 2012 (whose classification needs both-sided local semicompleteness)." | OLS $\supsetneq$ LS strictly. BJ–Huang 2012's statement does not cover OLS. | **Not subsumed** by BJ–Huang 2012 (modulo paywall residue on proof — see §4). |
| **Bang-Jensen–Gutin–Yeo 2020** (arXiv:1903.12225). Composition SAD: every 2-arc-strong semicomplete composition $T[H_1,\ldots,H_t]$ has a SAD iff it is not one of four exceptions ($S_4$; $\vec C_3[\overline K_2^3]$; $\vec C_3[\overline K_2, \overline K_2, P_2]$; $\vec C_3[\overline K_2,\overline K_2,\overline K_3]$). | Semicomplete-composition $\ne$ OLS; the two classes are incomparable ($\vec C_3[\overline K_3]$ is a semicomplete composition but not OLS: $N^+(v) \subset V(H_{i+1})$ is arc-less). | Theorem B *inherits* the four exceptions as an exclusion clause whenever a round-component is a semicomplete composition matching one of the four — CL1 has no kernel to lift in that case. This is folklore-correct citation, not novelty. | BJG–Yeo 2020 contributes the **exception list** to Theorem B; does **not** prove Theorem B. |
| **Bang-Jensen–Wang 2025** (arXiv:2309.06904). Split-digraph SAD. Direct PDF read of `/tmp/bjwang2025.txt`: `grep -i "in-locally\|out-locally\|in-tournament\|out-tournament\|in-semicomplete\|out-semicomplete\|OLS\|ILS"` returns **zero hits**. "locally semicomplete" mentions (lines 17, 18, 77, 82, 83, 1008) all refer to BJ–Huang 2012 in the two-sided sense. | No mention of OLS, no extension, no open problem about it. Split $\not\subseteq$ OLS and vice versa. | None. | No implication for Theorem B. |
| **Ai–He–Li–Qin–Wang 2024** (arXiv:2408.02260). Split-digraph 2-arc-strong SAD characterization. Direct PDF read of `/tmp/aietal2024.txt`: same grep returns **zero hits**; "locally semicomplete" mentions (lines 19, 85, 87, 1359) refer only to BJ–Huang 2012. | No mention of OLS. | None. | No implication for Theorem B. |
| **Bang-Jensen–Gutin** *Digraphs*, 2nd ed. (Springer 2009) **Ch. 5 (Locally Semicomplete Digraphs)** [2°; ToC and downstream citations only]. The chapter title plus consistent secondary references confirm two-sided LS treatment. No SAD-for-OLS theorem is invoked in any downstream paper (BJG–Yeo 2020, BJ–Wang 2025, Ai et al. 2024) when citing Ch. 5. | LS-only. | None. | No implication for Theorem B. |
| **Bang-Jensen–Gutin (eds.)** *Classes of Directed Graphs* (Springer 2018) **Ch. 6 "Locally Semicomplete Digraphs and Generalizations"** [paywalled; WebFetch redirected to authentication]. The chapter title's "generalizations" suggests it covers OLS, ILS, in-tournaments, out-tournaments, but the contents are unverifiable. Downstream papers (BJ–Wang 2025, Ai et al. 2024) cite this volume but do not quote any SAD theorem from it. | Likely covers OLS as a class but not Theorem B; **paywall residue** (§4 caveat (a)). | Unverified. | **CANNOT-DETERMINE residual** — §4. |
| **arXiv:2103.07886** "Decomposing and colouring some locally semicomplete digraphs". Theorem (WebFetch summary): every oriented graph with $N^+(v)$ a transitive tournament admits a 2-coloring of *vertices* into acyclic subdigraphs. | *Vertex*-partition into acyclic, not *arc*-partition into strong. Orthogonal problem on a sub-case of OLS. | None. | No implication for Theorem B. |
| **arXiv:2104.11019** "arc-locally (out/in)-semicomplete digraphs". *Arc*-locally semicomplete is a per-arc condition ($N^?(x) \cup N^?(y)$ semicomplete for every arc $xy$), unrelated to the per-vertex OLS condition. Structural characterization, no SAD. | Different class, no SAD. | None. | No implication for Theorem B. |
| **Bang-Jensen–Yeo 2004** [paywalled; via BJ–Wang 2025 Theorem 1.2 verbatim restatement]. Every 2-arc-strong semicomplete digraph $\ne S_4$ has a SAD. | Semicomplete-only; semicomplete $\subsetneq$ LS $\subsetneq$ OLS. | Theorem B specializes correctly to semicomplete (four exceptions reduce to $\{S_4\}$) but Theorem B is not implied. | No implication for Theorem B. |
| **Other recent branching / spanning results** — Bang-Jensen 2024 (arXiv:2302.06177, arc-disjoint $B^+_u, B^-_v$ in semicomplete digraphs); Bang-Jensen 2023 (spanning Eulerian in semicomplete); arXiv:2003.02107 (good pair in digraphs of independence number $\le 2$); arXiv:1906.08052 (good pair in compositions); Bang-Jensen–Kriesell 2009 survey. | All semicomplete-only, composition-only, independence-number-only, or expository. None is OLS-scoped. Good pair $\ne$ SAD (good pair gives one $(B^+, B^-)$ pair, SAD requires partitioning *all* of $A(D)$ into two strong spanning subdigraphs). | None. | No implication for Theorem B. |

**Summary of the table.** No surveyed source proves, claims, conjectures, or even mentions an SAD theorem for OLS. The only SAD theorems on classes containing tournaments are: (a) BJ–Yeo 2004 (semicomplete), (b) BJ–Huang 2012 (LS, two-sided), (c) BJG–Yeo 2020 (semicomplete compositions), (d) BJ–Wang 2025 (3-arc-strong split), (e) Ai et al. 2024 (2-arc-strong split characterization). None of (a)–(e) implies Theorem B because (a)–(c) require two-sided structure that OLS lacks, and (d)–(e) are about a class incomparable to OLS.

## §4 — Final novelty verdict for Route B

**Verdict: NOVEL with a CANNOT-DETERMINE residue.**

### What is novel

1. **No published SAD theorem for OLS.** The class is named in surveys
   (Bang-Jensen–Gutin 2018, Ch. 6 of *Classes of Directed Graphs*, by
   title) but no SAD result, not even at high arc-connectivity, has
   been published. The Structural Specialist's own statement in
   `team/02` §3 Rank 1 — "ILS strictly contains locally semicomplete
   and is **not** subsumed by BJ–Huang 2012 (whose classification
   needs both-sided local semicompleteness)" — was confirmed by the
   precedent table: every SAD result on locally-semicomplete-flavored
   classes uses the *two-sided* hypothesis essential to round
   decomposition.

2. **The CL1-engine itself is novel** (round-2 audit, `team/05`
   Appendix A.5, NOVEL). Applying a novel engine to a class not
   previously decomposed is, by default, a novel theorem.

3. **The exception list inherited from BJG–Yeo 2020 is folklore-correct.**
   The four exceptions ($S_4$ etc.) are the obvious obstructions
   whenever a round-component is a semicomplete composition, and
   their appearance in Theorem B's statement is mathematically forced
   rather than novel; this is a citation-tier component, not a
   novelty-tier one.

### CANNOT-DETERMINE residue

Three caveats prevent a fully clean NOVEL verdict:

(a) **Springer 2018 Chapter 6** "Locally Semicomplete Digraphs and
    Generalizations" (Galeana-Sánchez–Goldfeder, in
    Bang-Jensen–Gutin's *Classes of Directed Graphs* edited volume)
    is paywalled and the WebFetch attempt redirects to authentication.
    The chapter title's "Generalizations" wording is the single piece
    of evidence that an OLS-SAD theorem might lurk there, citing
    earlier unpublished or grey-literature work. The Auditor could
    not verify the chapter's contents. **Probability of an
    OLS-SAD theorem in this chapter: low** (no downstream paper —
    BJ–Wang 2025, Ai et al. 2024, BJG–Yeo 2020 — cites the chapter
    for any SAD result; if such a theorem existed, it would be the
    natural antecedent to BJ–Wang 2025's introduction, which it is
    not), but not zero. **Action: the Lead must secure library access
    to this chapter before submission.**

(b) **BJ–Huang 2012** itself remains paywalled (no arXiv preprint;
    JCTB DOI 10.1016/j.jctb.2011.09.001). `team/05` Appendix A.5 §A.5.6
    flagged the same residue for CL1. The paper's *statement* (LS-only)
    is known verbatim via BJ–Wang 2025 quotation; the *proof* is not.
    If the proof contains an inline lemma that is one-sided in the
    relevant direction — e.g., "for any digraph whose out-neighborhoods
    are semicomplete and which is 3-arc-strong, the round-component
    decomposition exists" — then BJ–Huang 2012 *also* covers OLS via
    its proof's reach, even though its statement does not. This would
    promote the verdict from NOVEL to DERIVATIVE-OF-X. The Auditor
    cannot exclude this without reading the proof. **Action: same as
    (a).**

(c) **The Lead's round-decomposition footing for OLS is not in the
    literature.** `team/13` §4 says "Strong OLS digraphs admit a round
    decomposition (BJ–Huang 1995 / Huang 1995); each component is
    semicomplete, hence SAD-decomposable via BJG–Yeo 2020." The
    published round decomposition theorem (Bang-Jensen 1995; Huang 1995;
    finalized in Bang-Jensen–Guo 2004) is for **two-sided LS**, not
    OLS. The Lead's claim is therefore a *conjecture about OLS*, not
    a citation. Whether it is true — i.e., whether every strong OLS
    digraph has a round decomposition into semicomplete components —
    is the first sub-question the Structural Specialist must answer
    in `team/14_route_b_ols_extraction.md`. If false, Route B's
    kernel extraction stalls and the §6.1 tripwire of `team/13` fires.
    **This is not a literature gap; it is a mathematical gap in the
    Lead's program.** The Auditor flags it here so the Structural
    Specialist's deliverable does not silently assume it.

The verdict therefore reads more precisely:

> **NOVEL pending (a), (b), and (c).** With high confidence, Theorem B
> is not in the published literature on SAD. With moderate confidence,
> it is not inline-derivable from BJ–Huang 2012's proof. With low
> confidence, the Springer 2018 Chapter 6 does not pre-empt it. The
> Lead's round-decomposition footing (c) is a mathematical conjecture,
> not a citation, and its resolution is the Structural Specialist's
> first deliverable.

## §5 — Implications for the Lead's decision matrix

Mapping to the four branches of `team/13_publishability_decision.md`
§3 (now applied to the *application* novelty rather than the *lemma*
novelty):

- **NOVEL (this verdict).** Route B fires: full headline product
  targeting JCTB. The paper is "Strong arc decompositions of
  3-arc-strong out-locally-semicomplete digraphs," with CL1
  (`team/11`) as the engine and the BJG–Yeo 2020 exceptions as the
  exclusion clause. The 6-week tripwire of `team/13` §6 still applies
  to the kernel-extraction *mathematics* (§4 caveat (c)), independent
  of this novelty verdict.

- **DERIVATIVE-OF-X (not the verdict, but the contingency).** If
  caveat (a) or (b) flips — i.e., Springer 2018 Ch. 6 or BJ–Huang
  2012's proof contains an OLS-SAD result — Theorem B's headline
  status downgrades. Mitigation: reframe as "first proof of OLS-SAD
  via bridge-coloring lifting (CL1) rather than via round-decomposition
  recursion," which preserves a venue tier above J. Graph Theory if
  the CL1 lemma's novelty (round-2 audit) is intact. The mitigation
  is plausible because CL1's bilateral form is *not* derivable from
  any one-sided proof technique in the BJ–Huang lineage.

- **EQUIVALENT-TO-Y.** Cannot fire from the surveyed literature:
  no theorem in any source is "the same as Theorem B modulo
  notation." The class boundaries are too narrowly demarcated for
  EQUIVALENT to be a credible verdict.

- **CANNOT-DETERMINE.** Partially fires for caveats (a) and (b).
  Mitigation: treat the present verdict as the actionable one
  (proceed with Route B as if NOVEL); resolve caveats (a) and (b)
  before submission by securing library access. This matches the
  Lead's existing instruction in `team/13` §3 CANNOT-DETERMINE row
  ("proceed but secure paywalled sources before submission").

### Branch that fires

**Branch fired: NOVEL (with paywall-conditional residue).** The
Lead's Route B selection stands. The Structural Specialist's
`team/14_route_b_ols_extraction.md` deliverable should proceed on the
mathematical assumption that (c) is true — i.e., a round
decomposition exists for strong OLS digraphs — and either prove it as
part of the deliverable or document the obstruction (per the §6.1
tripwire). The Coder's `team/15_v6_ols_empirical.md` deliverable
proceeds as planned. The Auditor commits to closing caveats (a) and
(b) by 2026-06-20 if institutional access is granted in time.

### Recommended pre-submission checklist (Lead-actionable)

1. Acquire and read **Bang-Jensen–Gutin (eds.) 2018, *Classes of
   Directed Graphs*, Ch. 6** ("Locally Semicomplete Digraphs and
   Generalizations"). Specifically grep the chapter for "strong arc
   decomposition," "arc-disjoint spanning," and "out-locally
   semicomplete." If a Theorem B analogue appears, the verdict
   downgrades.

2. Acquire and read **Bang-Jensen–Huang 2012** (JCTB 102, 701–714)
   in full. Read §3 of the proof for any inline statement that
   uses only one-sided LS. If found, Theorem B is DERIVATIVE-OF
   BJ–Huang 2012's inline lemma; reframe accordingly.

3. Ask the Structural Specialist to confirm or refute the round
   decomposition extension to OLS as the first half of
   `team/14_route_b_ols_extraction.md`. This closes the
   mathematical-not-literature gap (c) flagged above.

## §6 — Internal consistency checks

- `team/11_cl1_proof_v1.md` §6.2 already flagged "CL1 + a class
  application (e.g., the rank-1 ILS / OLS class)" as the safe route;
  this audit confirms OLS is unblocked. ILS would receive the same
  verdict by reversal.

- `team/05_audit.md` Appendix A.5 §A.5.6 already flagged the same
  paywall residue at BJ–Huang 2012. A single library-access pass
  closes both the CL1 and the Route B residues.

- The four exceptions in `team/13` §4 match `team/05` §1 table
  line 154 verbatim; the exception list is authoritative.

- Refreshed prior for the *application* novelty (vs. the lemma):
  NOVEL ~60 %, CANNOT-DETERMINE ~30 %, DERIVATIVE ~10 %,
  EQUIVALENT $< 1$ %. Realized verdict is in the modal bin.

---

**Bottom line.** Theorem B (Route B's headline) is **novel relative
to the surveyed literature on SAD**, with the paywall-conditional
residue at Bang-Jensen–Gutin (eds.) 2018 Ch. 6 and Bang-Jensen–Huang
2012 noted and assigned to a single pre-submission library-access
pass. The Lead's Route B selection stands; the Structural Specialist
should proceed with `team/14_*` on the OLS extraction, treating the
round-decomposition extension to OLS as a mathematical sub-claim to
prove rather than a citation. JCTB remains the appropriate venue
target.
