# Correctness review: directed-path minimum-outdegree project

**Date:** 2026-05-18
**Scope:** `problems/directed_path_minimum_outdegree/`
**Reviewer:** independent audit (not the project authors)

## Executive verdict

The project's three packaged theorems are, after deep reading and partial
re-execution:

- **δ = 3, all n ≥ 7, hand proof**
  (`docs/k3_hand_proof.md`): **correct**. The proof is a clean, fully
  self-contained structural argument that combines Cheng–Keevash
  Lemma 7 with the oriented-graph average bound and antiparallel
  cyclic-closure on the endpoint cycle. I find no logical gap.
- **δ = 4, n = 10, hand + computer-aided**
  (`docs/k4_n10_proof.md` + appendix + miners + certificate):
  **correct, with high mechanical confidence**. The certificate
  (`data/k4_n10_certificate.json`, 3 664 completions, ~10 MB) was
  re-verified end-to-end by me with `scripts/k4_verify_certificate.py`
  and passes every mechanical check (hash, 4-outregularity, oriented,
  forced arcs, Claim 12, Lemma A reverse, score sequence, witness
  path containment + simplicity + length ≥ 8). The independent
  re-derivation `scripts/k4_independent_check.py` was also re-run and
  agrees on 24/24 closed, 3 664 completions, 0 obstructions.
- **δ = 4, n = 11, computer-aided**
  (`docs/k4_n11_proof.md`): **correct conditional on the soundness
  of the local forcing rules and the integrity of two co-designed
  pipelines**. I partially re-ran `k4_score_profile_miner.py 11`
  (first three (2,1,1,1) configurations, 1 602 603 completions each
  in ~9.4 s on this laptop) and the numbers reproduce. The
  full 117 992 940-completion run is plausible at the claimed
  ~21-minute wall-clock. **However**, the "two independent
  pipelines" claim is materially weaker than its presentation in the
  proof file; see the dedicated section below.

The conjecture being attacked (Cheng–Keevash Conjecture 1) is
correctly transcribed against the actual paper (arXiv:2402.16776v4)
which I downloaded and read end-to-end. **Conjecture 1 is *not*
literally attributed to Thomassé in the paper**; the paper attributes
to Thomassé the stronger girth conjecture (`δ(g − 1)`), and presents
Conjecture 1 as the oriented-graph corollary (the focused special
case `g = 3`). The project's docs do flag this provenance correctly
in `docs/plan.md` line 92, but the README and headline language are
loose about it. MINOR.

I am not aware of any silent assumption that breaks the claimed
proofs. The most load-bearing assumption is the soundness of the
declared forcing-rule list (R-loop, R-path, R-cycle, R-T, R-F3,
R-Claim12, R-LemmaA-rev, R-AP, R-out, R-score, R-VCS, P1, P2), and I
believe each rule is sound under the assumed configuration; see the
dedicated Lemma 7 section.

## Findings, severity-tagged

### CRITICAL

None.

### MAJOR

**M1. The "two independent pipelines" framing at n = 11 is
overstated.** `docs/k4_n11_proof.md` lines 197–214 advertise a
"trust-boundary"-defining cross-check between
`scripts/k4_score_profile_miner.py` and
`scripts/k4_score_profile_independent_check.py`. The two files do
not share imports, and the second contains its own re-implementations
of `cycle_succ`/`cycle_pred`, `enumerate_score_profile_configs`,
`derive_forced`, `enumerate_completions`, and
`has_path_of_length_at_least_8`. **But they execute the *same
algorithm against the same declarative rule list*** — line-by-line
the propagation loop in `k4_score_profile_miner.py` (lines 163–238)
is structurally identical to the loop in
`k4_score_profile_independent_check.py` (lines 178–253), down to the
order in which P1/P2 inferences are applied and the choice to
maintain `forced`/`forbidden` as flat sets of ordered pairs. The
two files were almost certainly co-authored from the same
specification, possibly the same template. A shared-specification
bug — e.g. a wrong rule, or a misapplication of Claim 12 — would
persist in both. The cross-check defends against transcription
errors and indexing slips, **not** against rule-soundness errors.
The proof text would be more accurate to call this "two
implementations of the same specification".

I do not see any actual rule-level error, but the
trust-boundary claim should not be read as a substantive
algorithmic-independence check.

**M2. No per-completion certificate exists at n = 11; the closure
is reproduction-only.** The proof file (`docs/k4_n11_proof.md`
lines 181–194) explicitly defends this choice on storage grounds
(~tens to hundreds of GB), which is reasonable. The consequence,
clearly stated by the authors, is that the n = 11 closure cannot be
mechanically rechecked the way n = 10 can. Anyone replicating must
re-run the miner. The recorded stdout SHA-256 hashes
(`docs/k4_n11_proof.md` lines 166–170) help — but only if a
reproducer's environment matches Python 3.12.4 / macOS Darwin
25.4.0 byte-for-byte. A *hash-only* per-completion certificate
(arc-set hash + length-8 path) would be ~20 GB raw or ~1 GB
sample-compressed and would close this gap; it is mentioned in the
file as a possible future step.

**M3. Score-sequence enforcement at completion time is implicit.**
In `scripts/k4_score_profile_miner.py` lines 305–333 the recursive
enumerator filters arcs by the `(CYCLE_VERTICES - {v}) - excluded -
confirmed` candidate pool, and only checks
`count[u] == DELTA` (4-outregularity) when the recursion bottoms
out. The score-sequence split (e.g. for a U-vertex: 2 S-arcs, 2
V(C)\S-arcs) is enforced **only through the prior forced/forbidden
propagation**, not by an extra per-completion validity check
analogous to the audit's score check in `scripts/k4_audit.py`
lines 99–115 or the verifier's score check in
`scripts/k4_verify_certificate.py` lines 139–146. **In practice this
appears to be OK** because P1/P2 propagation always resolves the
S/(V(C)\S) split completely before enumeration starts (the
`free_choices` partitions each S-vertex's residual candidates into
exactly one of S or V(C)\S, never both). I verified this by
inspecting the post-propagation `cand` sets for several
configurations: in every case I checked, an S-vertex's residual
candidates lie entirely in one half. **But this property is not
asserted, tested, or documented**; if a future change to the
propagation rules left some S-vertex with mixed-half residual
candidates, the enumerator would silently emit completions that
violate the score sequence yet still get checked for length-8 paths.
A 3-line post-completion assertion (per-S-vertex S-outdegree equals
target) would harden this. The n = 10 audit (`k4_audit.py`) does
include this check; the n = 11 miner does not.

### MINOR

**Mn1. Conjecture 1 attribution.** `README.md` line 4 says
"Cheng–Keevash Conjecture 1 (Thomassé's directed-path conjecture)".
`/tmp/ck.txt` lines 23–28 (the actual paper) attribute to Thomassé
**only the stronger girth strengthening** ("any digraph with minimum
out-degree δ and girth g contains a directed path of length
δ(g − 1)"). Conjecture 1, the oriented-graph version, is stated by
Cheng–Keevash without an attribution line and is the special case
g = 3 of the girth conjecture (which is the only `g` for which
Thomassé's statement is not refuted by Bai–Manoussakis /
Cheng–Keevash Prop 2). `docs/plan.md` lines 91–106 already flag the
slug/name issue, but the headline framing across `README.md`,
`docs/k3_hand_proof.md` line 6, and `docs/k4_n10_proof.md` line 8
would be cleaner if it said "the oriented-graph case (g = 3) of
Thomassé's conjecture". The result and proof are unaffected.

**Mn2. Lemma 7's "+1 issue" surfaces in the literature notes but is
under-emphasised in the proof files.** I verified by reading the
actual published proof (`/tmp/ck.txt` lines 227–234, the last
paragraph of Section 4) that the stated Lemma 7 gives
`δ⁺(S) ≥ 2δ − ℓ(D)` (PDF text line 119) but the proof closes with
`δ⁺(S) ≥ 2δ + 1 − ℓ(D)` (PDF text line 234). The discrepancy is
indeed a notation slip: `|P|` is used in two senses (vertex count =
ℓ(D) + 1 and arc count = ℓ(D)). The project correctly uses the
weaker headline bound; this is noted in `docs/literature_notes.md`
lines 130–132 and `docs/plan.md` lines 71–74. **However**, the
weaker bound is exactly tight for δ = 4, ℓ = 7 (`δ⁺(S) ≥ 1`); the
stronger version `δ⁺(S) ≥ 2δ + 1 − ℓ(D) = 2` would have killed
the (2,2,1,1), (2,1,1,1), (3,1,1,1) cases immediately at n = 10
via the oriented average bound `δ⁺(S) ≤ ⌊(|S|−1)/2⌋ = 1`. If the
"+1 strengthening" is in fact correct (the proof's geometric step
gives `|P| ≥ |A| + 1 + |C|` and `|A| + |B| = δ`, leading to
`ℓ(D) = |P| − 1` arc-length or `|P|` vertex-count), the project's
careful conservatism is unnecessary work — but their conservatism
is safe. I do not see a way to recover the +1 cleanly without
re-reading the paper carefully in arc-counting normal form, which
the authors decline to do.

**Mn3. The `k4_local_miner.py` and `k4_independent_check.py`
exhibit the same M1 caveat at n = 10.** Both are co-designed from
the same forced-arc rule list. The cross-check (`24/24 closed, 3664
completions`) is genuine and matches the certificate, but it is
again a cross-check of *implementations of a shared specification*,
not of independent specifications. The strongest mechanical leg of
the n = 10 proof is the certificate verifier
(`scripts/k4_verify_certificate.py`), which checks the
completed-graph properties **declaratively** (score sequence, Claim
12, Lemma A reverse, antiparallel, 4-outregular, length-8 path
containment) and does not re-derive forced arcs. That is the only
component whose pass is not vulnerable to a rule-derivation bug.

**Mn4. The k4 n10 path search uses DFS with a hard cap on path
length** (target = 8; `scripts/k4_local_miner.py` lines 52–69,
`scripts/k4_independent_check.py` lines 281–313,
`scripts/k4_verify_certificate.py` lines 149–158). This is correct
for the question "does a length-≥ 8 path exist" but is **not** the
longest-path search. There is a separate standalone verifier
`scripts/verify_directed_path_counterexample.py` that does compute
the longest path. This is fine for the theorem (we only need ℓ ≥ 8
to refute ℓ = 7) but could be confusing if someone reused these
helpers for a different question (e.g. ℓ = 9, ℓ = 10 questions).

**Mn5. The (3,1,1,1) Case (II) listed length-8 path in
`docs/k4_partial_appendix.md` lines 486–495** uses
`v_3 → t` justified "by allowed-target count at n = 10". This
relies on the F4–F6 chain being tight enough to force at least one
of `v_3 → x, v_3 → y`. I traced the chain manually for Case (II)
and it does close, but the appendix is a little terse here; the
reader should consult the F4–F6 derivation in the (2,1,1,1) Case
(II) above (lines 282–323) for the parallel argument. This is a
docs-clarity nit, not a math bug.

**Mn6. `scripts/k4_general_miner.py` is dead code now superseded by
the score-profile miner**, but is still present and might confuse a
new reader. `docs/k4_n11_proof.md` line 261 explicitly tells the
reader not to use it as the closure tool, which is the right
mitigation; a `DEPRECATED` filename or banner inside the file would
be even safer.

### NIT

**Nt1. `scripts/k4_score_profile_independent_check.py` line 394**
has a Python operator-precedence quirk:
`if result is None or len(result) == 2 and isinstance(result[1], str)`.
Same pattern at `scripts/k4_score_profile_miner.py` line 278,
`scripts/k4_independent_check.py` line 332. Reads as
`A or (B and C)` (which is the intended meaning) but easy to
misread. Not a bug.

**Nt2. `scripts/k4_local_miner.py` line 250** returns a 4-tuple
`(forced, forbidden, out_confirmed, out_excluded)` while
`derive_forced` callers in line 264 check
`if result is None or len(result) == 2`. The 2-element return is
the error path. The dispatch is correct but brittle; a typed
`@dataclass` would clarify.

**Nt3. The OPG slug
`directed_cycle_of_length_twice_the_minimum_outdegree` (per
`docs/plan.md` line 95) suggests a *cycle* conjecture, but the
project attacks the *path* problem.** This is acknowledged in
`docs/plan.md` lines 92–106. The project should not be republished
under a misleading slug without a forward-pointing note.

## Lemma 7: exact statement check

I downloaded the Cheng–Keevash paper PDF
(`https://arxiv.org/pdf/2402.16776v4`) and converted it to text
(`/tmp/ck.txt`). The verbatim statements are at:

- **Conjecture 1** (PDF line 28):
  > Any oriented graph with minimum out-degree δ contains a directed
  > path of length 2δ.

  ✅ Matches `docs/literature_notes.md` line 49 and
  `docs/k3_hand_proof.md` headline.

- **Lemma 7** (PDF lines 118–119):
  > If D is an oriented graph with δ⁺(D) ≥ δ then D either contains
  > a directed path of length 2δ or an induced subgraph S such that
  > |S| ≤ δ and δ⁺(S) ≥ 2δ − ℓ(D).

  ✅ Matches `docs/literature_notes.md` lines 124–126 verbatim.

- **End-of-proof line** (PDF line 234):
  > ℓ(D) = |P| ≥ 2δ + 1 − δ⁺(S) and δ⁺(S) ≥ 2δ + 1 − ℓ(D).
  > This completes the proof of Lemma 7.

  This is the source of the "+1 strengthening" discussion. The
  project conservatively uses the weaker headline bound, which is
  safe but possibly leaves a strict improvement on the table; see
  Mn2.

- **S = B⁻ construction** (PDF lines 216–217):
  > Let A = N⁺(v_{a−1}) ∩ {v_0,...,v_{a−1}} and
  > B = N⁺(v_{a−1}) ∩ V(C). Also, let B⁻ = {u : u ∈ V(C),
  > uv ∈ A(C) for some v ∈ B}.

  ✅ Matches `docs/k4_n10_proof.md` lines 80–88 and
  `docs/k3_hand_proof.md` lines 96–119.

- **Claim 12** (PDF lines 218–226): N⁺(B⁻) ⊆ V(C). ✅ Matches
  project's R-Claim12 rule.

- **Claim 11** (PDF lines 182–215): every vertex in N⁺(v_{a−1})
  must be on P. ✅ Matches project's usage in F3.

The "a ≠ 0" step in the proof of Lemma 7 (PDF line 180) uses
`|V(D)| ≥ 2δ + 1` and strong connectivity. The project's reductions
R1–R3 establish these conditions before invoking Lemma 7, so a ≥ 1
is valid in the project's setting.

**No hidden assumption.** The lemma is stated for oriented graphs
(not arbitrary digraphs). The project's reductions explicitly
preserve "oriented" through R1/R2/R3
(`docs/k4_n10_proof.md` lines 33–58). The minimum-outdegree
condition is δ⁺ ≥ δ, and the project enforces δ⁺ = δ (exact) after
R2, which is strictly stronger than what Lemma 7 needs.

**One subtle point worth flagging**: Lemma 7's statement guarantees
`δ⁺(S) ≥ 2δ − ℓ(D)`. The project's chain of reasoning at δ = 4
proceeds by *fixing* δ⁺(S) = 1 (since 2δ − ℓ(D) = 1 with ℓ = 7,
and the oriented bound caps at ⌊(|S|−1)/2⌋ = 1 for |S| = 4). This
is the only value of δ⁺(S) that survives. The case `δ⁺(S) = 0` is
excluded by the lemma (we need ≥ 1), and `δ⁺(S) ≥ 2` is excluded
by the oriented average bound. Hence the score profiles enumerated
((1,1,1,1), (2,1,1,1), (2,2,1,1), (3,1,1,1)) are exhaustive for
oriented graphs on 4 vertices with δ⁺(S) = 1. I have verified this
enumeration is complete: any oriented graph on 4 vertices with
δ⁺(S) ≥ 1 has internal arc count between 4 and 6 (since max
oriented arcs on 4 vertices is `C(4,2) = 6`, and minimum is 4 for
δ⁺ = 1). The score sequence of S sums to the internal arc count,
so sum ∈ {4, 5, 6, 6} = {(1,1,1,1), (2,1,1,1), (2,2,1,1) or
(3,1,1,1)}. ✓

## The n = 11 verification: is it really exhaustive?

The claim is that 32 configurations × ~1.6M–6.9M completions each
= 117 992 940 total completions, all containing a length-8 path,
exhaustively cover the surviving Lemma 7 case at δ = 4, n = 11.

**Configuration enumeration is exhaustive given the framework.**
I independently re-counted the 32 = 0 + 4 + 24 + 4 configurations
by brute-force enumeration over `C(6,3) · C(4, |T|)` raw pairs
(`v_7 ∈ S, |S| = 4`, `T` chosen by score profile,
`σ(T) ⊆ S`). Counts match the project's claim exactly.
The (1,1,1,1) case is structurally 0 because σ(S) ⊆ S with
|S| = 4 contradicts σ being a 7-cycle (only invariant subsets are
∅ and V(C)). ✓

**Completion enumeration is sound** given the forced/forbidden
constraints, **provided** every forcing rule is sound (which I
believe). The enumeration uses DFS over free choices, applying
antiparallel during recursion (`scripts/k4_score_profile_miner.py`
line 336: `valid_cand = [w for w in cand if (w, v) not in arcs]`).
This is correct for oriented graphs.

**Free-choice ordering is heuristic only**
(`scripts/k4_score_profile_miner.py` line 295: smallest-cand-first).
It does not affect correctness, only performance.

**Length-8 path search is a standard DFS** (lines 243–268). Path
simplicity is enforced by a `visited` set. Length is measured in
arcs (the recursion's `length` parameter increments by 1 per arc
and triggers at `length >= target = 8`). Correct by inspection.

**Two issues I cannot fully resolve from the artifacts**:

1. **Did the actual 117M-completion run terminate?** The proof
   reports `0 obstructions` and `~21 minutes wall-clock`, with the
   stdout SHA-256 hash `2e6bd6...` recorded. I ran a partial replay
   (the first three (2,1,1,1) configs at n = 11) and confirmed
   1 602 603 completions per config in ~9.4s on my hardware. I did
   not run the full 21-minute pipeline. The numbers are
   self-consistent: 4 × 1 602 603 + 24 × (range 1.6M–6.9M, mean
   3.815M) + 4 × 5 002 128 ≈ 6 410 412 + 91 574 016 + 20 008 512 =
   117 992 940. The "(2,2,1,1) per-config range 1 620 762–6 945 136"
   in `docs/k4_n11_proof.md` line 128 is plausible given the n = 10
   per-config range 18–343 from
   `scripts/k4_score_profile_independent_check.py` n = 10 output
   (forced count 19–28, free count 5–8, so the n = 11 counts with
   forced 19–22 and more free choices would expand by orders of
   magnitude).

2. **Could the search have missed completions due to a propagation
   bug?** This would be a *soundness* issue if a "forced" arc were
   actually only conditional, leading to enumeration over a strict
   *subset* of valid completions. Then a completion outside this
   subset that lacks a length-8 path could be missed. I have
   inspected each rule (R-loop, R-path, R-cycle, R-T, R-F3,
   R-Claim12, R-LemmaA-rev, R-AP, P1, P2) and find no error. P1
   forcing requires `unconfirmed == need`; P2 exclusion requires
   `need == 0`. Both are correct local consequences of the
   counting constraints. R-T, R-Claim12, R-F3, R-LemmaA-rev are
   direct consequences of Lemma 7's proof internals (Claim 11,
   Claim 12) plus the longest-path endpoint argument.

**Soundness of the n = 11 setup** also requires that the case
analysis used to *get* to (|S| = 4, a = 1, V(C) = {v_1, ..., v_7})
is exhaustive at n = 11. I checked this:

- `|V(D)| ∈ {9, 10, 11}` after R1/R2/R3 (Cheng–Keevash Theorem 4 +
  oriented bound).
- `|V(D)| = 9`: regular tournament, Hamilton path (Camion + Rédei).
  Closed.
- `|V(D)| = 10`: closed by `k4_n10_proof.md`. Closed.
- `|V(D)| = 11`: this file's case.

This is correct: the R-reductions can produce a smaller sink SCC
than the original graph, so a counterexample at n = 11 might reduce
to a counterexample at n ≤ 11 inside the sink SCC. The proof
correctly handles this by closing n ≤ 10 first.

`|S| = 3` is closed by the same argument as in the n = 10 proof
(Lemma 2, `docs/k4_n10_proof.md` lines 98–108): `|A| = 1` requires
`a = 2`, then `A = {v_0}` requires `v_1 → v_0`, antiparallel with
the path arc `v_0 → v_1`. ✓

`a = 1` is forced because `|V(C)| ≥ |S| + δ - δ⁺(S) = 7`, and
`|V(C)| = 8 - a ≤ 7` iff `a ≥ 1`. ✓

So the n = 11 setup is correctly reduced to the (|S| = 4, a = 1,
v_7 ∈ S, score profile in {(1,1,1,1), (2,1,1,1), (2,2,1,1),
(3,1,1,1)}) case-split, and the case-split is exhaustively
enumerated.

## What I cannot verify from artifacts alone

1. **The full 117,992,940-completion n = 11 run.** I confirmed the
   first 3 (2,1,1,1) configurations (4.8M completions) and the
   completion counts match the claim exactly. Extrapolating, I
   estimate the full run on my hardware would take ~10–20 minutes,
   consistent with the recorded ~21 minutes. **But I did not run
   it.**

2. **The integrity of stdout SHA-256 hashes** recorded in the
   proof files (e.g.
   `docs/k4_n10_proof.md` lines 290–295,
   `docs/k4_n11_proof.md` lines 167–170). These are only useful as
   reproducibility evidence if a reproducer's environment matches
   byte-for-byte (Python 3.12.4, macOS Darwin 25.4.0). I cannot
   verify them without setting up an identical sandbox.

3. **The hand proof of (2,1,1,1) and (3,1,1,1) at n = 10** is laid
   out across `docs/k4_partial_appendix.md` lines 151–532. I traced
   Case (I) of (2,1,1,1) and Case (II) of (2,1,1,1) by hand, both
   of which work. The other cases (III, IV for each profile) are
   cyclic shifts and I did not re-trace them; the appendix's
   argument that cyclic shifts close them is plausible but I have
   not done the work.

4. **Cheng–Keevash Theorem 4 statement-vs-use.** The proof claims
   ℓ(D) ≥ 1.5δ for oriented graphs. The project applies this as
   "ℓ(D) ≥ ⌈1.5 · 4⌉ = 6" at δ = 4 (`docs/k4_n10_proof.md`
   line 49). The paper (PDF line 40) gives "1.5δ" without an
   explicit ceiling. For δ = 4 the bound is "ℓ(D) ≥ 6" because
   ℓ is an integer; for δ = 3 it is ℓ ≥ 5 (`docs/k3_hand_proof.md`
   line 32). Both readings are correct.

5. **Jackson 1981's statement** is via secondary source only;
   `docs/literature_notes.md` line 209 flags this explicitly and
   the project does not depend on it for any proof. I did not
   check the primary source either.

## What I am confident about

- **Lemma 7 is stated correctly** in
  `docs/literature_notes.md` and used soundly in the proofs.
- **The R1/R2/R3 reductions are correct** and preserve "oriented"
  and "δ⁺ ≥ δ".
- **The δ = 3 proof in `k3_hand_proof.md` is rigorous** and does
  not have hidden tournament-vs-oriented-graph slips. Steps 1–8
  trace cleanly. The only universe-quantified parameter is
  `|V(D)| ≥ 7`, established by the oriented average bound on δ⁺(D)
  ≥ 3.
- **The δ = 4, n = 10 closure is mechanically robust.** The
  certificate is a self-checking artifact; the verifier checks
  declarative end-state properties (not the rule derivation), so it
  is *immune* to a rule-derivation bug. If any of the 3 664
  completions lacked a length-8 path, the verifier would catch it.
  The forced-arc verification is a soundness check that the
  rules' fixed-point is consistent with each enumerated completion,
  which is a necessary but not sufficient condition for the
  theorem.
- **The configuration enumeration at n = 11 is complete** for each
  of the four score profiles, as independently re-verified by me.
- **The Conjecture 1 transcription** matches the paper verbatim.
- **The (1,1,1,1) "structurally impossible at any n" argument**
  is correct: σ permutes the 7-cycle V(C), and a 4-element subset
  invariant under a 7-cycle is impossible.
- **The score-profile-aware miner correctly handles all four
  score profiles** for any n ≥ 10, given correct forcing rules.
- **The cyclic-interval mini-lemma** (`docs/k4_n10_proof.md`
  lines 159–190) is proved correctly for both (2,1,1,1) and
  (3,1,1,1) profiles, since both have |T| = 3.

## Recommendations

(Marked by anticipated effort.)

- **[Low.] Add a per-completion assertion to
  `scripts/k4_score_profile_miner.py`** at the point a completion
  is accepted (line 321), checking the score sequence and Claim 12
  on the assembled arc set, mirroring `scripts/k4_audit.py`
  lines 99–123. This costs negligible time per completion and
  closes the implicit-score-enforcement gap (M3).

- **[Low.] Update headline language** in `README.md` and proof file
  abstracts so that "Conjecture 1" is attributed accurately:
  "the oriented-graph case (g = 3) of Thomassé's directed-path
  conjecture, formalised by Cheng–Keevash as their Conjecture 1".

- **[Medium.] Generate a hash-only certificate at n = 11**
  (one arc-set hash + one length-8 witness path per completion;
  ~20 GB raw, ~1 GB gz). This would replace the
  "trust the miner" stance with a mechanically reproducible
  end-state check, addressing M2.

- **[Medium.] Add a third pipeline implementing the same
  configuration-and-completion search with a different
  parameterisation** (e.g., a CSP/SAT encoding, or a brute-force
  enumeration without forced-arc propagation that just enumerates
  all 4-outregular oriented graphs on the prescribed cycle and
  filters by Claim 12 etc.), to defend against shared-specification
  bugs (M1). Even a single config at n = 11 cross-checked this way
  would substantially strengthen the closure.

- **[Low.] Mark `scripts/k4_general_miner.py` as deprecated**
  in-file, addressing Mn6.

- **[Stretch.] Re-examine whether the +1 strengthening of Lemma 7
  is actually usable** (Mn2). If so, the δ = 4 case might close
  much more cleanly at every n, since `δ⁺(S) ≥ 2` on `|S| ≤ 4` is
  impossible by the oriented average bound, killing the whole
  case-split at δ = 4. The project's notes already mention this is
  "resolved as a notation slip", but a careful arc-vs-vertex audit
  of the geometric step would be worth one final pass.

## Summary table

| Item | Verdict | Confidence | Notes |
|---|---|---|---|
| Conjecture 1 statement | correct | high | verified against arXiv 2402.16776v4 |
| Lemma 7 statement | correct | high | verified verbatim against the paper |
| R1/R2/R3 reductions | correct | high | preserve oriented + δ⁺ ≥ δ |
| δ = 3 hand proof | correct | high | traced end-to-end |
| δ = 4, n = 10 closure | correct | high | certificate independently verified by me |
| δ = 4, n = 10 hand cases | correct | medium-high | traced (2,1,1,1) cases I and II by hand |
| δ = 4, n = 10 computer cases | correct | high | 3664 completions verified mechanically |
| δ = 4, n = 11 closure | correct | medium-high | partial reproduction; rule-soundness defended |
| Two-pipeline n = 10 cross-check | genuine implementation diversity, not algorithmic | medium | M3 / Mn3 |
| Two-pipeline n = 11 cross-check | same | medium | M1 |
| Hand proof of (3,1,1,1) at n = 10 | correct | medium-high | the dominator-S structure analysis verified |
| (1,1,1,1) structural impossibility | correct | high | sigma 7-cycle argument |
| Score-profile enumeration | exhaustive | high | independently brute-force re-counted |
| Forcing rule R-T | sound | high | direct Claim 12 + score consequence |
| Forcing rule R-Claim12 | sound | high | direct Claim 12 |
| Forcing rule R-F3 | sound | high | direct construction of B = succ_C(S), a = 1 |
| Forcing rule R-LemmaA-rev | sound | high | Lemma A applied to reverse digraph |
| Iterative P1 / P2 | sound | high | local counting consequence |
| Path-existence DFS | correct | high | standard DFS with visited set |
| Certificate schema | correct | high | matches verifier's expectations |
| Certificate verifier | correct | high | re-ran end-to-end on 3664 completions |
| Jackson 1981 statement | unverified | low | secondary source only; project does not depend on it |

## Final word

The project does not appear to overstate any closure. The δ = 3
hand proof is genuinely solid; the δ = 4, n = 10 closure is
mechanically self-certifying via the JSON certificate; the δ = 4,
n = 11 closure is real but rests on the soundness of one
declarative forcing-rule specification implemented by two scripts
that share that specification. The audit-trail note in
`docs/k4_n11_proof.md` lines 12–32 is honest about the earlier
mis-claim (the old `k4_general_miner.py` only covered (2,2,1,1)).
The score-profile-aware miner is the right fix.

The most actionable correctness gap is M3 (score-sequence
enforcement is implicit at n = 11), which is plausibly OK in
practice but should be made explicit. The trust-boundary
overselling of "two independent pipelines" (M1) is a presentation
issue, not a correctness issue. The n = 11 closure would be
substantially strengthened by an actual third pipeline using a
materially different approach (SAT, naive enumeration, or even a
hash-only certificate).

— end of review —
