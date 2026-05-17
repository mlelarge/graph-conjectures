# Findings — Bang-Jensen–Yeo attack, project close-out

Date: 2026-05-17. This document is the honest knowledge state of the
project, replacing `paper/draft_v1.md` (which was framed for publication
and over-claimed the hard case of $(1, 0)$-near-split — see the user's
`paper/review_v1.md` for the blocking finding). What follows is what
the team actually established, what was refuted, and what remains open.

The original problem: Bang-Jensen and Yeo (2004) conjectured that there
exists an absolute constant $K$ such that every $K$-arc-strong digraph
admits a strong arc decomposition (SAD) — a partition of $A(D)$ into
two parts each of which is spanning and strongly connected. The working
conjecture **WC3** posits $K = 3$. The project pursued WC3 along several
fronts; below is what they produced.

---

## §1 — What is proved (unconditionally)

### Theorem 1 (EC-log). Logarithmic-arc-strength Eulerian digraphs admit a SAD.

*There is an absolute constant $C = 5$ such that every Eulerian digraph
$D$ on $n \geq 4$ vertices with $\lambda^{\mathrm{arc}}(D) \geq C \log_2 n$
admits a SAD.*

**Proof location:** `team/04_ec_log_proof.md`; reproduced as §3 of
`paper/draft_v1.md`.

**Method:** for Eulerian $D$, the underlying multigraph $G$ satisfies
$d_G(X) = 2|\delta_D^+(X)|$ for every $\emptyset \neq X \subsetneq V$,
so directed cuts in $D$ correspond two-to-one to undirected cuts in $G$
with size factor 2. Karger's cut-counting bound (JACM 2000) gives
$O(n^{2\alpha})$ undirected cuts of size at most $\alpha \lambda_G$.
Random 2-coloring of $A(D)$ with first-moment closure on the geometric
series. Constant $C = 5$ has roughly one to seven units of slack in the
relevant range; the asymptotic limit of the method is $C \to 4^+$.

**Honest scope:** the proof needs $\lambda$ growing at least
logarithmically. Constant-$\lambda$ Eulerian theorems are not
accessible by this argument. Eulerianness is essential — without it the
$d_G(X) = 2|\delta_D^+(X)|$ identity fails.

### Theorem 2 (CL1 — bilateral lifting lemma).

*Let $D = (V, A)$ be a digraph with $V = V_1 \sqcup V_2$. If*

1. *each induced subdigraph $D[V_i]$ admits a SAD, and*
2. *the bridge arc set $A_{12} \cup A_{21}$ between $V_1$ and $V_2$
   admits a 2-coloring with each (direction, color) class non-empty,*

*then $D$ admits a SAD.*

**Proof location:** `team/11_cl1_proof_v1.md` (R2 branching-witness
form); reproduced as §4 of `paper/draft_v1.md`.

**Method:** Edmonds-stitching of out- and in-arborescences at a common
root, using hypothesis (2) to assign one bridge per (direction, color).
The bilateral form is novel: prior lifting lemmas in the lineage
(Bang-Jensen–Wang 2025 Lemma 2.4 in particular) are *kernel-shell
asymmetric* — one part carries the SAD, the other is an arc-less shell
absorbed by 2-in / 2-out attachments. CL1 partitions every arc,
including internal arcs of both parts.

**Auditor verdict (NOVEL):** `team/05_audit.md` Appendix A.5 confirmed
no published precedent in BJ–Yeo 2004 / BJ–Huang 2012 / BJG–Yeo 2020 /
BJ–Wang 2025 / Ai et al. 2024 / BJG 2009 textbook / Schrijver Vol B
(within the audit's reach). Paywall residue: Hell–Hernández-Cruz 2017
unverified.

### Theorem 3 (R3⋆-KS — $(1, 0)$-near-split kernel-shell case).

*Let $D$ be a 3-arc-strong $(1, 0)$-near-split digraph: $V = V_1 \sqcup V_2$,
$V_2$ semicomplete, exactly one $V_1$-internal arc $e_0 = (p, q)$, $|V_2|
\geq 3$. Let $D^\bullet$ be the contraction of $e_0$. If $D^\bullet[V_2]$
admits a SAD, then $D$ admits a SAD.*

**Proof location:** `team/26_side_compatible_sad_proof.md` (patched to a
labelled-arc attachment argument); reproduced as §5.2 of
`paper/draft_v1.md`.

**Method:** 3-arc-strongness of $D$ + the unique-chord structure forces
$|R_p^+| \geq 2, |R_q^+| \geq 3, |R_p^-| \geq 3, |R_q^-| \geq 2$ at the
contracted vertex $r = p^\bullet$. A counting argument shows the four
demand-classes (one $q$-reaching witness per color + one $p \to q$
witness in the good color) fit inside the supply with slack at least 1
per class. The labelled-arc attachment observation (proved in-document)
sidesteps the multigraph parallelism issue at $r$.

**Note on naming:** this was Theorem 4 in `paper/draft_v1.md`; renumbered
to Theorem 3 here because Theorem 3 of the draft (the full conditional
$(1, 0)$-near-split SAD) does not survive (see §3 below).

---

## §2 — What is refuted

### Conjecture L (as stated in `paper/draft_v1.md` lines 936–945) is false.

The original statement was a universal quantification: for every
3-arc-strong directed multigraph $D^\bullet$, every pair of arc-disjoint
spanning in-arborescences $T^-, U^-$ rooted at $r$, and every $a \in T^-$,
some $U^-$-exit arc from $X_a^{T^-}$ has subtree intersection strictly
smaller than $X_a^{T^-}$.

**Counterexample** (from the user's `paper/review_v1.md`, building on
`team/31_*` lines 126–128):

Let $V = \{r, u, v_1, w\}$,
$T^- = \{(v_1, u), (u, r), (w, r)\}$,
$U^- = \{(u, v_1), (v_1, r), (w, v_1)\}$,
$a = (u, r) \in T^-$,
$X = X_a^{T^-} = \{u, v_1\}$.

The unique $U^-$-exit from $X$ is $b = (v_1, r)$. Its $U^-$-subtree
rooted at $v_1$ is $\{v_1, u, w\}$, so $X_b^{U^-} \cap X = \{u, v_1\} = X$
— not a strict subset.

Embed in the complete bidirected digraph $K_4^*$ on $\{r, u, v_1, w\}$:
$K_4^*$ has 12 arcs, $\lambda^{\mathrm{arc}}(K_4^*) = 3$, and the same $T^-,
U^-$ remain arc-disjoint spanning in-arborescences inside $K_4^*$. The
subtree structure is unchanged. **Conjecture L fails on a 3-arc-strong
host.**

The team's working notes (`team/31_*` lines 126–128) explicitly recorded
that "Conjecture L can fail for an arbitrary arc-disjoint pair of
in-branchings, including pairs lying inside a 3-arc-strong host." The
publication draft `paper/draft_v1.md` framed L as "open, with 11 869
SAT-instance empirical support," which **contradicts the working
notes** and conflates "main property holds empirically" with
"sub-claim holds pointwise."

### F3 (cross-kind disjointness at $\lambda \geq 4$): NOT a theorem.

The proposed "for $\lambda(D^\bullet) \geq 4$, there exist 2 arc-disjoint
out-arborescences + 2 arc-disjoint in-arborescences with all four
mutually arc-disjoint" is NOT a corollary of any published result the
audit could find (`team/05_audit.md` Appendix A.13). Cross-kind joint
packing is exactly Thomassen's open conjecture (Bang-Jensen–Bessy–
Havet–Yeo 2022, arXiv:2003.02107) and **NP-complete in general** even
at $k = 1$ with $r_1 = r_2$ (BJG 2009 Theorem 9.9.2; Nagamochi–
Kamiyama 2014 survey §3.4). Matroid union applies to *same-direction*
packing only — that is, Edmonds' theorem, already in the toolkit.

The Specialist's fourfold pattern (`feedback_citation_verification.md`)
included three claims that F3 / cross-kind packing / matroid union
would close the hard case. All four claims were over-attributions; the
audit closed each one.

### OLS (out-locally-semicomplete) Route B does not exist as written.

The Lead's `team/13_publishability_decision.md` §4 committed to "Route B
via the BJG–Yeo composition theorem in the round-decomposition setting
for OLS digraphs." The Specialist's `team/14_*` derived an OLS-SAD
theorem citing a "Theorem RD" round-decomposition for OLS. The audit
(`team/05_audit.md` Appendix A.6) found three independent failures: a
phantom JCTB page range, a misnumbered BJG 2009 textbook theorem, and a
result claimed as published that is in fact **Bang-Jensen–Gutin 1998
Problem 6.8** — a 28-year open structural characterization problem for
locally in-semicomplete digraphs. The team correctly pivoted Route B to
$(1, 0)$-near-split (`team/13_*` §7 amendment) and preserved OLS in
`team/17_ols_rd_problem.md` as a side notebook.

---

## §3 — What is open

### The full 3-arc-strong $(1, 0)$-near-split SAD theorem.

When $D^\bullet[V_2]$ does **not** admit a SAD (the hard case
H1a/H1b/H2 of `team/27_*`), the kernel-shell proof of §1 above does not
apply. The RECOLOR algorithm of `team/29_*` was an attempt; its
termination depends on Conjecture L, which is refuted. **Status: open.**

### Two candidate rescue formulations for Conjecture L.

Both stated honestly as open problems, no claim of empirical support:

**(L-exist)** *For every 3-arc-strong directed multigraph $D^\bullet$
and every $a \in A(D^\bullet)$, there **exists** a pair of arc-disjoint
spanning in-arborescences $T^-, U^-$ rooted at the head of $a$ such
that some $U^-$-exit from $X_a^{T^-}$ has subtree intersection strictly
smaller than $X_a^{T^-}$.*

**(L-swap)** *For every 3-arc-strong $D^\bullet$, every arc-disjoint
pair $(T^-, U^-)$, and every $a \in T^-$ witnessing a funnel failure,
there is a local arc-swap on $T^-$ and $U^-$ that yields a new
arc-disjoint pair satisfying the strict-subset property at $a$ (or
shifts the failure to an arc closer to the root).*

Whether either holds is the team's natural next question.

### The Bang-Jensen–Yeo conjecture for general 3-arc-strong digraphs (WC3).

Untouched. Empirical evidence (11 869 instances, 0 UNSAT, see §4 below)
is consistent with WC3 but does not approach a proof. The project's
counterexample search (Phase 3 v1/v2/v3 support: gluings, Eulerian
$K_{6,6}$ / circulants / perturbed bidirected, laminar tight-3-cuts,
substitution, Cayley) covered roughly 13 000 labeled-distinct
$\lambda = 3$ instances without finding a single $\lambda = 3$ UNSAT.
This is a meaningful negative-evidence result on the structured
counterexample-generation families the team tried; it does not say
anything about adversarial constructions outside those families.

### OLS / ILS structural characterizations.

BJ–Gutin 1998 Problem 6.8 remains open after 28 years. The team's
attempt at a round-decomposition theorem for OLS was scoped down
(`team/17_*`) when its 28-year-open nature was confirmed.

---

## §4 — Empirical state

| Sweep | Instances tested | $\lambda^{\mathrm{arc}} = 3$ verified | UNSAT | ILP–SAT disagreements |
|---|---:|---:|---:|---:|
| Phase 3 v1 (gluings, naive) | 269 760 streamed | 1 640 | 0 | 0 |
| Phase 3 v2 (deficit-aware + Eulerian + laminar) | 20 972 streamed | 4 613 | 0 | 0 |
| Phase 3 v3 support (Vehicle 5 substitution + Cayley) | 731 | 20 | 0 | 0 |
| Phase 4 Vehicle 6 (SAD-decomposable inner parts) | 5 000 streamed | 2 471 | 0 | 0 |
| Route B near-split broad sweep | 7 374 | 7 374 | 0 | 0 |
| Route B (H1b, H2) residuals | 4 495 | 4 495 | 0 | 0 |
| **Total** | **~310 000 streamed** | **~20 600 verified** | **0** | **0** |

Within the project's structured candidate-generation families, no
$\lambda = 3$ UNSAT instance has been found. The verifier (ILP cut-
separation + SAT with arborescence witnesses) is cross-checked on every
candidate; zero solver disagreements. This is the strongest single
piece of evidence that the verifier is internally consistent on the
input slice. It is **not** a proof of WC3.

A separate finding: the 2-arc-strong $(1, 0)$-near-split exception
family is **6 canonical instances** not isomorphic to any catalogue
member (Bang-Jensen–Yeo 2004 / Bang-Jensen–Huang 2012 / BJG–Yeo 2020 /
Ai et al. 2024 including all known arc-reverses) in either orientation.
All six are **internal-arc-dependent**: removing the $V_1$-internal arc
$e_0$ destroys 2-arc-strongness, so the obstruction is genuinely tied
to the chord. These are candidates for a future companion theorem on
2-arc-strong $(1, 0)$-near-split digraphs.

---

## §5 — Meta-lessons (project process)

Two patterns the team encountered repeatedly, captured in
`memory/feedback_citation_verification.md` and
`memory/feedback_conjecture_framing.md`:

**Citation over-attribution (four occurrences):** the Structural
Specialist agent in this project produced phantom citations on four
load-bearing claims: OLS Theorem RD (audit A.6); B.3 dashed arcs (A.4 /
A.9); cross-kind Edmonds disjointness misnumbered (A.10); F3 / matroid
union for cross-kind packing (A.13). Pattern: confident
"by Frank/BJG/Schrijver Theorem $X.Y.Z$" invocations that fail
verbatim verification. The escalation rule is: for any load-bearing
citation, demand a verbatim quote *before* the Auditor's polish pass.

**Lead-summary over-framing (one occurrence, this project):** the
Lead agent's `paper/draft_v1.md` aggregated the team's content toward
publishability, framing Conjecture L as "open, empirically supported"
when the working notes explicitly recorded the funnel obstruction at
3-arc-strong hosts. The seventh-pass Auditor verified citations and
conditionality wording but did not red-team the conjecture itself. The
correction rule: for any conjecture the team relies on, demand a
*content* red-team (small-instance counterexample search) separate from
the citation-discipline audit.

The user's $K_4^*$-embedding refutation of Conjecture L is a two-minute
check. That such a check was missing from the agent loop is the
project's most useful procedural lesson.

---

## §6 — Pointers

**Proofs (audit-cleared, reproducible):**
- `team/04_ec_log_proof.md` — EC-log lemma (Theorem 1 above).
- `team/11_cl1_proof_v1.md` — CL1 bilateral lifting (Theorem 2 above).
- `team/26_side_compatible_sad_proof.md` — R3⋆-KS kernel-shell (Theorem 3 above).
- `team/05_audit.md` Appendices A.1–A.14 — literature audit, fourteen forensic appendices.

**Working notes (preserved for future revisits):**
- `team/21_*` — chord contraction step.
- `team/27_*` — original hard-case Edmonds approach (gap at §3.1.1).
- `team/29_*` — RECOLOR algorithm (within-kind patched).
- `team/30_*` — termination analysis with Conjecture L identified.
- `team/31_*` — Conjecture L proof attempt with funnel obstruction; lines 126–128 are the negative finding that the user's review surfaces.
- `team/32_*` — F3 4-arc-strong attempt (failed; cross-kind packing is open / NP-hard).
- `team/33_*` — within-kind submodularity patch (direct double-Edmonds).
- `team/17_*` — OLS notebook, frozen as side problem (Problem 6.8 of BJ–Gutin 1998).

**Computational infrastructure:**
- `code/` — uv-managed Python; ILP/cut-separation verifier (`verifier_ilp.py`); SAT verifier with arborescence witnesses (`verifier_sat.py`); 12 canonical benchmarks (`benchmarks.py`); generators for gluings, deficit-aware, Eulerian, laminar v2, near-split, OLS, SAD-inner-parts, substitution, canonicalize (`generators/`); empirical logs in `code/logs/`.
- `code/benchmarks.py` ships 12 instances after the team's catalogue extension (S_4, $C_{2k}^{(2)}$ for $k = 2, 3, 4$, four BJG–Yeo composition exceptions, smallest Ai et al. 2024 split exceptions Lemma 2.11 / 3.12 / $(iv)^* \times (iv)$, and SAT controls $QR_7, K_5^*, C_5$ doubled).

**Superseded:**
- `paper/draft_v1.md` — publishing-framed draft with the Conjecture L mis-framing; carries a SUPERSEDED notice at the top pointing here.
- `paper/outline.md` — outline for `draft_v1.md`, also superseded.
- `paper/review_v1.md` — user's review surfacing the Conjecture L refutation.

---

## §7 — What a future session would do

Not actionable in this session; recorded for continuity.

1. **Attempt (L-exist) or (L-swap)** for Conjecture L's existential or
   swap-repair rescue. The funnel obstruction is concrete and small;
   the swap-repair line in `team/31_*` §4 already closed the
   $|E^+_a| = 1$ + free-arc-parallel-to-$a$ subcase. Pushing to other
   subcases is the natural mathematical continuation.

2. **2-arc-strong $(1, 0)$-near-split companion theorem.** The 6
   internal-arc-dependent canonical exceptions are a finite-looking
   list; whether they extend to an infinite parametric family is open.
   The Coder's near-split generator can enumerate higher $(|V_1|, |V_2|)$
   to test.

3. **Constant-$\lambda$ Eulerian SAD.** Theorem 1 gives $\lambda \geq C
   \log_2 n$. Whether constant $\lambda$ suffices for Eulerian digraphs
   is open; the obvious union-bound technique caps out at $\Theta(\log n)$
   (Karger's bound is asymptotically tight).

4. **OLS structural characterization (BJ–Gutin 1998 Problem 6.8).**
   28-year open. Out of scope for the current project budget; preserved
   in `team/17_*` as a side note.

That is the project's actual output.
