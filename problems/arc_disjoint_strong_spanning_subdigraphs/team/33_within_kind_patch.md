# 33 — Within-kind disjointness patch: replace broken submodularity by plain Edmonds applied twice

Author: Structural Digraph Specialist
Date: 2026-05-17
Status: Drop-in replacement for the broken submodularity-cascade step
shared by `team/27_r3star_hard_case_edmonds.md` lines 197–207 and
`team/29_route_c1_recoloring.md` §1.2 lines 86–98, per
`team/05_audit.md` Appendix A.13 (verdict §A.13.4 / recommendation
§A.13.7). **Within-kind disjointness is VERIFIED-VERBATIM** via two
clean independent applications of Theorem 2.5 of BJG–Yeo 2020
(Edmonds' branching theorem), one to $D^\bullet$ and one to
$\overleftarrow{D^\bullet}$. No matroid union. No submodularity
detour. No new citations.

---

## §1 — The broken passage and the fix in one sentence

### §1.1 The broken passage, verbatim from `team/27_*` lines 197–207

> "[…] This is automatic in Edmonds' theorem applied independently to
> out- and in-branchings rooted at $r$, since the theorem allows the
> union; one then refines the choice by picking $T_i^-$ inside
> $A^\bullet \setminus T_i^+$, which is still $\ge 2$-arc-strong from
> $r$ by the inequality
>
> $$d_{(D^\bullet \setminus T_i^+)}^-(X) \ge d_{D^\bullet}^-(X) - 1 \ge 2$$
>
> for every $X$ (since $T_i^+$ contributes at most one arc to any
> $\delta^-(X)$, being a branching)."

The parenthetical "$T_i^+$ contributes at most one arc to any
$\delta^-(X)$" is **false**. Per audit A.13 §A.13.5 (citing
`team/32_*` §2.3):

$$|T_i^+ \cap \delta^-(X)| = \#\{\text{connected components of } T_i^+[X]\},$$

which is $\geq 1$ but not bounded above by $1$ in general (e.g., if
$T_i^+$ branches out-degree $\geq 2$ at a non-root $u$ and $X$ is the
union of descendants of two distinct children of $u$, then
$T_i^+ \cap \delta^-(X)$ has $\geq 2$ arcs).

### §1.2 The fix in one sentence

Apply Theorem 2.5 of BJG–Yeo 2020 **independently twice** — once to
$D^\bullet$ (delivering $T_1^+, T_2^+$ arc-disjoint), once to
$\overleftarrow{D^\bullet}$ (delivering $T_1^-, T_2^-$ arc-disjoint in
$D^\bullet$) — and **do not** further refine $T_i^-$ to lie outside
$T_i^+$.

---

## §2 — Replacement text for `team/27_*` lines 197–207

The following is the precise drop-in replacement for `team/27_*`
lines 197–207, retaining the surrounding context (lines 180–196,
208–onwards) unchanged.

> **Within-kind disjointness via Edmonds applied twice.** We use only
> Theorem 2.5 of BJG–Yeo 2020 (Edmonds' branching theorem), in the
> verbatim form quoted in `team/05_audit.md` Appendix A.5 Source 2
> (line 946):
>
> > **Theorem 2.5.** A directed multigraph $D = (V, A)$ with a vertex
> > $z$ has $k$ arc-disjoint out-branchings rooted at $z$ if and only
> > if $d^-(X) \geq k$ for all non-empty $X \subseteq V \setminus
> > \{z\}$.
>
> Apply Theorem 2.5 to $D^\bullet$ with $z = r$ and $k = 2$: since
> $D^\bullet$ is 3-arc-strong, $d_{D^\bullet}^-(X) \ge 3 \ge 2$ for
> every non-empty $X \subseteq V^\bullet \setminus \{r\}$; hence
> there exist arc-disjoint out-branchings $T_1^+, T_2^+$ rooted at
> $r$ with $T_1^+ \cap T_2^+ = \emptyset$.
>
> Apply Theorem 2.5 to the reverse digraph $\overleftarrow{D^\bullet}$
> with $z = r$ and $k = 2$: arc-reversal preserves arc-connectivity,
> so $\overleftarrow{D^\bullet}$ is also 3-arc-strong, and
> $d_{\overleftarrow{D^\bullet}}^-(X) = d_{D^\bullet}^+(X) \ge 3 \ge
> 2$ for every non-empty $X \subseteq V^\bullet \setminus \{r\}$.
> The theorem yields two arc-disjoint out-branchings of
> $\overleftarrow{D^\bullet}$ rooted at $r$; their arc-reversals are
> two arc-disjoint in-branchings $T_1^-, T_2^-$ of $D^\bullet$
> rooted at $r$, with $T_1^- \cap T_2^- = \emptyset$.
>
> The two applications are **independent**. Within-kind disjointness
> ($T_1^+ \cap T_2^+ = \emptyset$ and $T_1^- \cap T_2^- = \emptyset$)
> is automatic by construction. **Across kinds, the families
> $\{T_1^+, T_2^+\}$ and $\{T_1^-, T_2^-\}$ may share arcs freely;
> we make no cross-kind disjointness claim here.** Cross-color
> cross-kind sharing (an arc in $T_1^+ \cap T_2^-$ or in
> $T_2^+ \cap T_1^-$) is resolved by the re-coloring step of
> `team/29_*` §3 (subject to Conjecture L for termination).

This replacement is `(C2)` of audit A.13 §A.13.1, verified verbatim
in §A.13.4 from the proof of BJG 2009 Theorem 7.10.1
(`/tmp/bjg_book.txt` lines 19740–19747).

---

## §3 — Replacement text for `team/29_*` §1.2 lines 86–98

The block in `team/29_*` lines 86–98 is the "refined" submodularity
re-statement that quotes the broken `team/27_*` argument. It must be
replaced. Lines 70–85 of `team/29_*` (the two clean Edmonds
applications) are correct and remain; lines 99–110 (downstream WK
labelling, cross-kind disclaimer) remain. The replacement is for
lines 86–98 only.

> **Within-kind disjointness (corrected; replaces `team/27_*` lines
> 197–207, per audit A.13 §A.13.5–§A.13.7).** The two applications of
> Theorem 2.5 stated above (lines 78–85) already deliver
>
> $$T_1^+ \cap T_2^+ = \emptyset \quad \text{and} \quad T_1^- \cap T_2^- = \emptyset.$$
>
> No further refinement is needed or claimed. In particular, we do
> **not** assert $T_i^+ \cap T_i^- = \emptyset$: the submodularity
> argument of `team/27_*` lines 197–207 that purported to show this
> via
>
> $$d_{(D^\bullet \setminus T_i^+)}^-(X) \ge d_{D^\bullet}^-(X) - 1 \ge 2$$
>
> relied on the false inequality "$|T_i^+ \cap \delta^-(X)| \le 1$";
> see audit `team/05_audit.md` Appendix A.13 §A.13.5 for the explicit
> counter-instance (multiple components of $T_i^+[X]$ each
> contributing one arc to $\delta^-(X)$). Tag this conclusion as
> $\mathrm{(WK)}$:
>
> $$T_1^+ \cap T_2^+ = \emptyset, \quad T_1^- \cap T_2^- = \emptyset. \tag{WK}$$

Lines 99 onwards of `team/29_*` ("Within-kind disjointness across the
two colors is also automatic …" and the "What we do NOT assume"
block) are already aligned with this corrected (WK) and remain
unchanged. The line-101 equation `T_i^+ \cap T_i^- = \emptyset` is
**removed** with the rest of lines 86–98; it was the unjustified
upgrade.

---

## §4 — Downstream impact

The §2/§3 replacements preserve everything the rest of `team/27_*`,
`team/29_*`, `team/30_*`, `team/31_*` rests on, with one explicit
change in claim that the downstream files are already designed for.

**(a) Within-kind disjointness claim (preserved).**
$T_1^+ \cap T_2^+ = \emptyset$ and $T_1^- \cap T_2^- = \emptyset$ are
retained. This is what `team/27_*` §3.2 ("Strong connectivity of
each color class") actually uses: each color $i$ has its own
out-branching $T_i^+$ for reach-from-$r$ and its own in-branching
$T_i^-$ for reach-to-$r$, with the two colors' out-branchings (resp.
in-branchings) arc-disjoint. The audit confirms in A.13 §A.13.5 that
`team/27_*` §3.2 "lines 234–243 … uses only the existence of $T_i^+$
as an out-branching and $T_i^-$ as an in-branching, with no
cross-kind arc-disjointness invoked."

**(b) §3.4 16-profile side-label casework at $r$ (preserved).**
The 16-profile counting requires four **distinct branching arcs at
$r$**: $T_i^+$ contributes one out-arc at $r$ (the unique
$T_i^+$-out-arc of $r$, $i \in \{1, 2\}$), and $T_j^-$ contributes
one in-arc at $r$ ($j \in \{1, 2\}$). The four arcs are distinct
because out-arcs at $r$ and in-arcs at $r$ are disjoint as arc sets
(distinct head/tail patterns at $r$), and within out-arcs we have
$T_1^+ \cap T_2^+ = \emptyset$, within in-arcs we have
$T_1^- \cap T_2^- = \emptyset$. This is the structural observation
of `team/29_*` §1.3 ("Why cross-kind sharing at $r$ is impossible"),
which is independent of the submodularity step and therefore
unaffected.

**(c) Conjecture L's role (preserved).**
Conjecture L governs termination of the R3⋆-HC re-coloring algorithm
(`team/29_*` §3, `team/30_*` §§1–4, `team/31_*` proof attempt). It is
invoked precisely when cross-kind sharing
$T_1^+ \cap T_2^- \ne \emptyset$ or $T_2^+ \cap T_1^- \ne \emptyset$
must be resolved. The replacements in §§2–3 above leave that sharing
in place — they do not over-claim cross-kind disjointness — so
Conjecture L's role is unchanged. The R3⋆-HC proof chain remains
conditional on Conjecture L exactly as before.

**(d) F3 (cross-kind disjointness at $\lambda \ge 4$) (not revived).**
This patch fixes only the within-kind step. (F3) — cross-kind
arc-disjointness of all four $\{T_1^+, T_2^+, T_1^-, T_2^-\}$ — is
**still NOT-FOUND** per audit A.13 §§A.13.3, A.13.6. The patch does
not weaken nor strengthen the audit's verdict on (F3). The "matroid
union" route attempted in `team/32_*` for (F3) is still off-limits
under the hard rule (A.13 §A.13.6).

**(e) Silent dependencies on the broken submodularity (flagged).**
The Specialist has re-read `team/27_*` §§3.2–3.4, `team/29_*` §§2–4,
`team/30_*` §§1–4, `team/31_*` §§1–5 for any silent dependency on
$T_i^+ \cap T_i^- = \emptyset$ (the color-internal cross-kind
disjointness that the broken submodularity tried to upgrade to).
**None found.** The downstream uses are uniformly of the within-kind
form $T_1^+ \cap T_2^+ = T_1^- \cap T_2^- = \emptyset$ together with
the cross-kind sharing being non-empty in general (which is exactly
what RECOLOR is built to handle). If a later reading uncovers a
silent dependency, it will be flagged in a separate patch.

---

## §5 — Status

- **Within-kind disjointness:** **VERIFIED-VERBATIM** via Theorem 2.5
  of BJG–Yeo 2020 (Edmonds' branching theorem) applied independently
  to $D^\bullet$ and to $\overleftarrow{D^\bullet}$. No
  submodularity. No matroid union. No new citations. Audit A.13
  §A.13.4 endorses this as the published form of (C2).
- **The R3⋆-HC proof chain** rests on:
  (a) the patched within-kind step (§§2–3 above), now solid;
  (b) the RECOLOR algorithm of `team/29_*` §3, handling cross-kind
      sharing by re-coloring;
  (c) **Conjecture L** (open), which governs termination of RECOLOR.
- **Theorem 1** (the R3⋆-HC consequence: 3-arc-strong $(1,0)$-near-
  split digraphs decompose into two arc-disjoint strong spanning
  sub-digraphs) is **conditional on Conjecture L**. The
  within-kind step is no longer a conditionality; only Conjecture L
  is.

End of `team/33_within_kind_patch.md`.
