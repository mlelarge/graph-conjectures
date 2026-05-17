# 18 — Novelty check for the amended Route B headline ($(1,0)$-near-split SAD)

Author: Proof Auditor / Literature Reviewer
Date: 2026-05-16
Status: bounded-scope (~1 h) public-source literature audit gating the
Lead's amended Route B in `team/13_publishability_decision.md` §7.
Companions: `team/02_structural_program.md` §3 rank-2 (Specialist's
introduction of $(k,0)$-near-split), `team/05_audit.md` Appendices A.1,
A.5, A.6 (the strict-split published baseline and the OLS phantom-
citation autopsy), `team/11_cl1_proof_v1.md` §5.1 (the R2-cleaned CL1
that Route B applies), `team/13_publishability_decision.md` §7
(amended Route B headline), `team/17_ols_rd_problem.md` (the
abandoned-as-load-bearing OLS route).

Primary PDFs opened in this session (`pdftotext -layout`):

- arXiv:2309.06904v1 (BJ–Wang 2025, J. Graph Theory 108, 5–26) →
  `/tmp/bjwang2025.txt` (1043 lines).
- arXiv:2408.02260v1 (Ai–He–Li–Qin–Wang 2024) →
  `/tmp/aihelxqw2024.txt` (1793 lines).
- arXiv: (Ai–Hao–Li–Shao 2025, *Arc-disjoint in- and out-branchings
  in semicomplete split digraphs*, DAM 2025; preprint at
  cfc.nankai.edu.cn) → `/tmp/cfc_arxdisj.txt` (663 lines).
- M. D. LaMar 2012, *Split digraphs*, Discrete Math. 312, 1314–1325 →
  `/tmp/lamar.txt` (1034 lines).

Paywalled / inaccessible: Hell–Hernández-Cruz 2017 (Discrete Applied
Mathematics 216, 609–617) and Bang-Jensen–Gutin 2018 *Classes of
Directed Graphs* (Springer Monographs), Chapter 6 ("Locally
Semicomplete Digraphs and Generalizations"). Both are addressed by
abstract / title and by their treatment in downstream literature; see
§3 rows 4 and 5.

---

## §1 — The amended Route B headline

Verbatim from `team/13_publishability_decision.md` §7:

> *Every 3-arc-strong $(1,0)$-near-split digraph admits a strong arc
> decomposition.*

**Definition ($(1,0)$-near-split).** A digraph $D = (V, A)$ is
$(1,0)$-near-split if $V = V_1 \,\dot\cup\, V_2$ with $V_2$ inducing a
semicomplete digraph, arcs between $V_1$ and $V_2$ unrestricted, and
**exactly one arc inside $V_1$** (so $V_1$ is independent except for
one arc). The $(k,0)$-near-split generalization allows up to (or
exactly) $k$ arcs inside $V_1$; $V_2$ remains semicomplete; the
bipartite arcs $A(V_1, V_2)$ are unrestricted. The $(0,0)$-case
($V_1$ fully independent) is the **strict split digraph** of BJ–Wang
2025 and Ai et al. 2024.

The headline is the smallest non-trivial step beyond strict split:
exactly one $V_1$-internal arc, no other relaxation.

---

## §2 — Why near-split sits between strict split and general digraphs

- **Strict split + 3-arc-strong SAD: solved.** Bang-Jensen–Wang 2025
  Theorem 1.6 (verbatim, /tmp/bjwang2025.txt line 139) proves *every
  3-arc-strong split digraph has a SAD, polytime*. Strict split here
  means $V_1$ independent.
- **Strict split + 2-arc-strong SAD: complete characterization.**
  Ai–He–Li–Qin–Wang 2024 Theorem 1.8 (verbatim, /tmp/aihelxqw2024.txt
  lines 114–116) characterizes the exceptions: explicit families in
  Lemma 2.11, Lemma 3.12, and Appendix structures (plus arc-reversals).
- **General 3-arc-strong digraph SAD: the BJ–Yeo conjecture.** Open
  for $K \geq 3$ (Conjecture 1.2 in /tmp/bjwang2025.txt line 65; the
  $K=3$ slice is the project's headline conjecture).
- **$(1,0)$-near-split is the smallest perturbation.** One internal
  arc inside $V_1$ breaks the "$V_1$ independent" hypothesis on which
  BJ–Wang's Lemma 3.3 ($(X, Y)$-path 2-feasibility) and Ai et al.'s
  splitting-off pairs (Definition 2.3, /tmp/aihelxqw2024.txt line 180)
  are built. Whether either toolchain absorbs one extra arc trivially
  or breaks is the technical question Route B has to answer in
  `team/19_*`.

The published literature splits into a *strict-split body of work*
(BJ–Wang 2025 + Ai et al. 2024 + Ai–Hao–Li–Shao 2025) and the
*general-digraph conjecture* with no recorded intermediate. The
$(k,0)$-near-split class proposed in `team/02` §3 is, to the
Auditor's knowledge, not a published class.

---

## §3 — Precedent table

The seven sources surveyed. For each, the row records what is
published, how it relates to the amended Route B headline, and a
verdict on whether it preempts (or trivially implies) that headline.

| # | Source | Result on split or near-split SAD | Relation to amended Route B | Verdict |
|---|---|---|---|---|
| 1 | **Bang-Jensen, Wang 2025**, *Strong arc decompositions of split digraphs*, J. Graph Theory 108 (2025), 5–26 (arXiv:2309.06904v1). | **Theorem 1.6** (verbatim, /tmp/bjwang2025.txt lines 139–141): *Let $D = (V_1, V_2; A)$ be a 2-arc-strong split digraph such that $V_1$ is an independent set and the subdigraph induced by $V_2$ is semicomplete. If every vertex of $V_1$ has both out- and in-degree at least 3 in $D$, then $D$ has a strong arc decomposition.* Section 4 produces an infinite family of 2-vertex-strong split digraphs without SAD (Propositions 4.5–4.6). Section 5 lists four open problems; none mention near-split. | The hypothesis is explicitly "$V_1$ is an independent set" (verbatim line 140). Figure 10 caption (lines 918–921): *"Split digraphs with vertex partition $V_1 \cup V_2$ such that $V_1$ is independent and $D\langle V_2 \rangle$ is semicomplete."* The infinite family has $V_1$ independent. No extension to one $V_1$-internal arc is stated, proved, or conjectured. The Section 5 open problems (1–4) ask about 2-arc-strength sharpness, minimum-degree-5 sharpness, 2-linkage, and 6-strong 2-linkage — none touch near-split. | **Does not preempt.** The BJ–Wang Theorem 1.6 statement explicitly requires $V_1$ independent; it is silent on $(1,0)$-near-split. Whether the *proof* extends is the technical T1 of `team/02` §1, but that is a research question for Route B, not a published claim. |
| 2 | **Ai, He, Li, Qin, Wang 2024**, *A complete characterization of split digraphs with a strong arc decomposition*, arXiv:2408.02260v1. | **Theorem 1.8** (verbatim, /tmp/aihelxqw2024.txt lines 114–116): *A 2-arc-strong split digraph $D = (V_1, V_2; A)$ has a strong arc decomposition if and only if $D$ is not isomorphic to any of the digraphs illustrated in Lemma 2.11, Lemma 3.12, the Appendix, or their arc-reversed versions (reverse all arcs).* Section 2 (line 143–144): *A digraph $D$ is a split digraph if $V(D)$ can be partitioned into two sets $V_1$ and $V_2$ such that $V_1$ is an independent set and $V_2$ induces a semicomplete digraph.* | Strict split throughout. All exceptions (Lemma 2.11: lines 268–277; Lemma 3.12: line 1306; Appendix B.2/B.3: $V_1 = \{a, b\}$ at line 1623, *independent*) have $V_1$ independent by hypothesis of the theorem. Splitting-off operation (Definition 2.3, line 180) is defined for $V_1$ on a path with endpoints in $V_2$; it has no recipe for an arc internal to $V_1$. No relaxation, no near-split discussion, no open problem on near-split. | **Does not preempt.** Theorem 1.8 is for 2-arc-strong strict split. The 3-arc-strong case of strict split was solved earlier by BJ–Wang 2025. Neither paper handles even one $V_1$-internal arc. |
| 3 | **Ai, Hao, Li, Shao 2025**, *Arc-disjoint in- and out-branchings in semicomplete split digraphs*, Discrete Applied Mathematics, 2025; preprint April 2025 (cfc.nankai.edu.cn). | Confirms Conjecture 4.1 of BJ–Wang 2025: *every 2-arc-strong **semicomplete** split digraph contains a good $(u, v)$-pair for every choice of $u, v$* (Abstract, /tmp/cfc_arxdisj.txt lines 12–18). | A weaker (good-pair, not SAD) result on a *stronger* class (*semicomplete* split: every $V_1$-vertex adjacent to every $V_2$-vertex). $V_1$ is still independent (verbatim line 16: *"$V_1$ is an independent set"*). No near-split. | **Does not preempt.** Different conclusion (good pair, not SAD) and different hypothesis (semicomplete split, stricter than split). $V_1$-internal arcs unaddressed. |
| 4 | **Bang-Jensen, Gutin (eds.)** *Classes of Directed Graphs* (Springer Monographs in Mathematics, 2018). | Paywalled. The Springer table of contents (verified by WebSearch and the SDU author page in `team/05` Appendix A.6 §A.6.2 Source 4) has chapters on Tournaments and Semicomplete, Acyclic, Euler, Planar, **Locally Semicomplete Digraphs and Generalizations**, Semicomplete Multipartite, Quasi-Transitive and Extensions, Bounded Width, Products, Miscellaneous Digraph Classes. **There is no chapter on split digraphs.** | The published structural-class corpus in 2018 had no chapter on split. The split-SAD line of work begins in 2023 (arXiv:2309.06904 submission). The book cannot contain a near-split SAD theorem because the split-SAD baseline did not yet exist. | **Does not preempt.** Insufficient lead time and no chapter exists; downstream surveys (BJ–Wang 2025, Ai et al. 2024) cite this book but never for a split-SAD or near-split result. |
| 5 | **Lamar, M. D.** 2012, *Split digraphs*, Discrete Math. 312, 1314–1325 (and arXiv:1005.2452). | Verbatim abstract (/tmp/lamar.txt lines 13–22): *"We generalize the class of split graphs to the directed case and show that these split digraphs can be identified from their degree sequences. […] a digraph is split if and only if its degree sequence satisfies one of the Fulkerson inequalities."* Definition 1.1 is the underlying-graph one. The paper's split digraph has the form $X = \{X^\pm, X^+, X^-, X^0\}$ where $X^\pm$ is a clique, $X^0$ is an independent set, and $\vec G[X^+]$, $\vec G[X^-]$ are unconstrained (Figure 1 caption, line 1314 region). | LaMar's "split digraph" is more general than BJ–Wang's (his $X^+, X^-$ are unrestricted), so it formally *contains* $(k,0)$-near-split as a special case. **But LaMar 2012 is purely about degree-sequence characterization (digraphicality)**, no SAD result, no strong-connectivity result. The class is defined but not studied for arc-disjoint decomposition. | **Does not preempt.** LaMar's broader split-digraph class is degree-sequence-defined and has no SAD theorem. The amended Route B headline is independent of LaMar 2012's content. |
| 6 | **Hell, P., Hernández-Cruz, C.** 2017, *Strict chordal and strict split digraphs*, Discrete Appl. Math. 216, 609–617. | Paywalled at ScienceDirect; HTTP 403 on the standard URL. WebSearch returns the title and the *Wikidata* abstract-free record. No arXiv preprint located in 30 minutes of search. From the journal's listed scope and follow-up work (Hell, Hernández-Cruz "Semi-strict Chordality of Digraphs", Springer 2024, *Graphs and Combinatorics* 40), the "strict" prefix in this line of research denotes a **forbidden-induced-subdigraph variant** of split (a digraph orientation must satisfy additional local conditions; not "split with one extra arc"). | The Auditor could not retrieve the precise definition of "strict split digraph" in Hell–Hernández-Cruz 2017. Inference from the publication trail (Min-Orderable Digraphs, Semi-strict Chordality 2024) is that the paper sits in the *chordal/Γ-free matrices* line of structural digraph research, not the SAD line. Bang-Jensen–Wang 2025, Ai et al. 2024, and Ai et al. 2025 — the three SAD-on-split papers — **do not cite Hell–Hernández-Cruz 2017** (verified by Ctrl-F on the references sections of all three preprints). | **CANNOT-DETERMINE without journal access**, but **likely does not preempt**. The "strict" qualifier in Hell–Hernández-Cruz appears to be unrelated to "$V_1$ has $k$ internal arcs"; it is about which oriented graphs whose underlying graphs are split are accepted, not a perturbation of the BJ–Wang split-digraph class. **Caveat: paywall-conditional.** |
| 7 | **WebSearch 2020–2025** for *"near-split digraph"*, *"almost split digraph"*, *"(k,0)-near-split"*, *"split + one edge"*, *"split-like digraph"*, *"quasi-split digraph"*, *"split digraph extension"* SAD. | Zero hits. The exact strings *"(k,0)-near-split"* and *"(1,0)-near-split"* return zero Google Scholar / web results. The string *"near-split digraph"* combined with *"arc decomposition"* returns zero hits. | The terminology proposed by the Structural Specialist in `team/02` §3 rank-2 appears to be **original to this project**. | **Does not preempt.** No matching published result located. |

---

## §4 — Final novelty verdict for the near-split Route B headline

**NOVEL**, with one **CANNOT-DETERMINE** caveat (Hell–Hernández-Cruz
2017, paywalled).

Justification:

1. **The amended headline is not a published theorem.** No surveyed
   source states or implies *every 3-arc-strong $(1,0)$-near-split
   digraph admits a strong arc decomposition*. BJ–Wang 2025 (the
   closest precedent, row 1) is for strict split, with $V_1$
   independent stated as a hypothesis (verbatim line 140). Ai et al.
   2024 (row 2) is for 2-arc-strong strict split; same hypothesis
   shape. Ai–Hao–Li–Shao 2025 (row 3) is for the *stronger*
   semicomplete-split class and proves the *weaker* good-pair
   conclusion. LaMar 2012 (row 5) defines a broader split-digraph
   class but only treats degree-sequence characterization. BJ–Gutin
   2018 (row 4) has no split-digraph chapter. WebSearch (row 7)
   returns no near-split SAD result.
2. **The headline is not an immediate corollary of BJ–Wang Theorem 1.6
   or Ai et al. Theorem 1.8.** Their hypotheses include "$V_1$ is an
   independent set." Adding one arc inside $V_1$ falsifies that
   hypothesis. The natural "absorb the extra arc by deleting it,
   applying the theorem, and inserting" reduction does not work:
   deleting an arc from a 3-arc-strong digraph may produce a
   2-arc-strong digraph that does not satisfy the BJ–Wang Theorem 1.6
   minimum-degree-3 hypothesis (BJ–Wang requires "every vertex of
   $V_1$ has both out- and in-degree at least 3 in $D$", verbatim
   line 140; deleting an arc can drop a $V_1$-vertex from
   in-degree 3 to in-degree 2). Conversely, "view the extra arc as a
   color-free edge and absorb into either color class" is not a
   published recipe in any surveyed source — the splitting-off /
   pending-decomposition / nice-decomposition apparatus of
   BJ–Wang and Ai et al. requires the path interior to lie in $V_1$
   *as an independent set* (Definition 2.3 of Ai et al.,
   /tmp/aihelxqw2024.txt line 180).

   The amended headline is therefore not "derivative-of-X" by any
   surveyed $X$. It requires a new structural argument — either a
   strengthening of CL1's lifting recipe to absorb one extra arc as
   a "free" residual arc on both colors, or a case analysis on the
   one extra arc's endpoints relative to the chosen kernel.
3. **Hell–Hernández-Cruz 2017 caveat.** This is a 2017 *Discrete
   Applied Mathematics* paper the Auditor could not retrieve in full.
   The "strict split" terminology in their title raises a flag, but
   downstream evidence (their 2024 *Semi-strict Chordality* sequel
   and the absence of any citation from BJ–Wang 2025 / Ai et al.
   2024 / Ai et al. 2025) suggests "strict" denotes a *stricter*
   orientation condition, not a perturbation of the BJ–Wang split
   class. The probability that this paper contains a SAD theorem on
   a $(1,0)$-near-split class is low but not zero.

**Recommendation.** Proceed with Route B as if **NOVEL**, with one
post-write-up library-access task (see §6.1 below) to resolve the
Hell–Hernández-Cruz caveat before submission.

---

## §5 — Implications for the Lead's decision matrix

`team/13_publishability_decision.md` §3 gave a four-row decision
matrix on the (CL1, Route B) novelty verdict. The amended Route B
shifts the class from OLS (struck down by `team/05` Appendix A.6 as
a 28-year open structural problem) to $(1,0)$-near-split.

**The NOVEL row of the §3 matrix fires.** Quoting verbatim:

> **NOVEL** | **B**, with **A** as a fallback short note if the
> class application stalls past the 6-week tripwire | NOVEL means
> CL1 is a genuinely new lemma in the literature. Route B is the
> highest-EV option: it earns JCTB tier on the back of a class
> theorem with CL1 as the engine, and the 6-week tripwire bounds
> downside.

Concretely:

- **Route B proceeds** with target class $(1,0)$-near-split. The
  Structural Specialist (deliverable `team/19_near_split_extraction.md`
  per `team/13` §7 amended assignments) executes the kernel-extraction
  and CL1-application argument; the Coder (deliverable
  `team/20_near_split_empirical.md` and `code/generators/near_split.py`)
  enumerates 3-arc-strong $(1,0)$-near-split digraphs at $n \leq 10$.
- **Route A (CL1 standalone)** remains the fallback short note if
  Route B's class extraction stalls at the 6-week tripwire.
- **The Hell–Hernández-Cruz 2017 caveat** does not block submission
  but should be resolved before final submission (§6.1 below).

The §3 matrix's NOVEL recommendation is unchanged: Route B with
$(1,0)$-near-split, with Route A as a registration-note fallback.

---

## §6 — Pitfalls and follow-ups

### §6.1 — Library access required (paywall residue)

**Resolution task before publication.** Obtain Hell–Hernández-Cruz
2017, *Strict chordal and strict split digraphs*, Discrete Appl.
Math. 216, 609–617. Read the definition of "strict split digraph"
(Section 2 or 3). Confirm that "strict" denotes a *stricter*
orientation condition (forbidden-subdigraph or orientation-of-split-
underlying-graph variant), **not** a perturbation of BJ–Wang's split
class allowing $V_1$-internal arcs. If the latter — if Hell–
Hernández-Cruz's "strict split" allows some $V_1$ internal arcs and
they prove a strong-arc-decomposition theorem on it — the §4 verdict
downgrades to **DERIVATIVE-OF-X** and the Route B framing must cite
them. If "strict" is the expected forbidden-subdigraph variant, the
§4 NOVEL verdict stands.

Estimated cost: 30 min with institutional Elsevier access.

### §6.2 — $(k, 0)$-near-split for $k \geq 2$

The amended Route B headline targets exactly $k = 1$. The team
should expect a referee to ask why $k = 1$ specifically. Two cases:

- **If CL1's residual-coverage hypothesis 4 extends to absorb the
  $V_1$-internal arc trivially** (e.g. one of its endpoints has the
  necessary spare in/out-arc budget at the $V_2$-side from
  3-arc-strongness), the proof extends to $(k, 0)$-near-split for
  $k = O(1)$ at no extra cost. **Audit recommendation:** the
  Specialist should write the proof of the headline as parametric
  in $k$ if possible, and only fall back to $k = 1$ if the analysis
  forces it. This produces a stronger published theorem if it goes
  through, and clarifies which residual-budget step is breaking
  otherwise.
- **If the $k = 1$ case is technically distinguished** (e.g. one
  internal arc admits an ad-hoc argument that does not extend), the
  Specialist should explicitly note in `team/19_*` why $k \geq 2$
  fails. A 6-month future-work item to settle $(2, 0)$-near-split
  would then become a credible sequel paper.

No surveyed source addresses $(k, 0)$-near-split for any $k \geq 1$,
so this is genuinely open ground at every $k$. Publication priority
for $k = 1$ does not preempt anyone.

### §6.3 — Does the Ai et al. 2024 split exception family extend to a $(1,0)$-near-split exception family?

This is the second referee-likely question. The Ai et al. exceptions
(Lemma 2.11: structural cases with $u \in V_1$, $x_1, x_2 \in V_2$;
Lemma 3.12: variant with $|V_2| \geq 4$; Appendix B.1/B.2/B.3: cases
with $|V_2| = 4$ and $D[V_2] \in \{S_4, S_{4,-1}, S_{4,-2}\}$;
$V_1 = \{a\}$ or $V_1 = \{a, b\}$ throughout) are *2-arc-strong*
exceptions. The amended Route B headline is for *3-arc-strong*
$(1,0)$-near-split, so these exceptions are not directly relevant —
BJ–Wang 2025 Theorem 1.6 shows the 3-arc-strong strict-split case
has *no* exceptions (every 3-arc-strong strict split digraph has a
SAD).

Two follow-up questions for the Coder (deliverable `team/20_*`):

1. Are there 2-arc-strong $(1,0)$-near-split digraphs without a SAD
   that are *not* arc-deletions of an Ai et al. 2024 strict-split
   exception? If yes, the $(1,0)$-near-split exception family at
   2-arc-strongness is genuinely new and warrants a separate
   characterization paper after the main 3-arc-strong result.
2. Are there 3-arc-strong $(1,0)$-near-split digraphs without a SAD
   at $n \leq 10$? If yes, the amended Route B headline is **false**
   and Route B re-pivots (per `team/13` §7 tripwire).

The Coder's empirical sweep (`team/20_*` / `code/generators/near_split.py`)
is the answer to both. The Auditor's prior, on the strength of the
BJ–Wang 3-arc-strong strict-split result and the absence of
$V_1$-internal-arc obstructions in the published exception families,
is that the empirical answer to (2) is **no UNSAT cases** — i.e. the
amended headline is true and the V6-style sweep produces zero
UNSAT cases, paralleling the 2 471-SAT clean record of
`team/10_phase4_vehicle6.md`.

### §6.4 — Re-cross-check the §3 BJ–Wang Section 4 infinite family

The Specialist may build CL1's kernel as $V_2$ semicomplete plus
absorb the one $V_1$-internal arc into the residual budget. The
BJ–Wang Figure 10 infinite-family construction (Proposition 4.5–4.6,
verbatim line 918 caption: *"Split digraphs with vertex partition
$V_1 \cup V_2$ such that $V_1$ is independent"*) is **2-vertex-strong
without a good $(u, v)$-pair** — i.e. it is not even 2-arc-strong in
the relevant sense, and $V_1$ is independent. The family does **not**
extend trivially to $(1,0)$-near-split with the same construction.
**Audit recommendation:** before writing `team/19_*`, the Specialist
should redo the Figure 10 construction with one $V_1$-internal arc
added and ask whether the modified digraph is still without a good
$(u, v)$-pair. If yes, the infinite family extends and the amended
headline at *2-vertex-strong* (= weaker than 2-arc-strong) is still
false; if no, the family does not extend, and the 3-arc-strong
headline retains its plausibility.

### §6.5 — One-line bibliographic correction to incorporate

Independent of the novelty verdict: the BJ–Wang 2025 published
volume and issue are *J. Graph Theory* **108** (2025), 5–26
(verified by the WebSearch / Wiley result row in the §3 table).
Several earlier `team/` notes use the 2024 J. Graph Theory submission
date; the 2025 publication year is correct in `team/13` and
elsewhere. No correction needed in `team/13` §7.

---

## §7 — Summary

**Verdict for `team/18`:** the amended Route B headline (*Every
3-arc-strong $(1,0)$-near-split digraph admits a strong arc
decomposition*) is **NOVEL** in the surveyed literature, conditional
on the §6.1 paywall residue (Hell–Hernández-Cruz 2017 *Strict
chordal and strict split digraphs*, Discrete Appl. Math. 216,
609–617). No surveyed source — BJ–Wang 2025, Ai et al. 2024,
Ai–Hao–Li–Shao 2025, LaMar 2012, BJ–Gutin 2018 *Classes of Directed
Graphs*, or WebSearch 2020–2025 — states or implies the headline,
and it is not an immediate corollary of any of them. The closest
precedent (BJ–Wang Theorem 1.6, 3-arc-strong strict-split SAD) has
"$V_1$ is an independent set" as an explicit hypothesis; the
$(1,0)$-near-split class adds one arc and is a genuinely new
structural setting for SAD research.

**Recommendation to the Lead:** the §3 NOVEL row of `team/13`'s
decision matrix fires. Route B with class $(1,0)$-near-split
proceeds. Route A (CL1 standalone) remains the 6-week-tripwire
fallback. Hell–Hernández-Cruz 2017 should be retrieved through
institutional access before submission to close the
paywall-conditional residue (§6.1); this is the only known unknown.
