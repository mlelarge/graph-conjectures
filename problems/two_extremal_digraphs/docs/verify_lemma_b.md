# Adversarial audit of `proof_lemma_b.md` (Lemma B, reduction soundness)

**Auditor stance:** skeptical. A step is "proved" only if it is an airtight
mathematical argument; empirical agreement over `L₃..L₇` and finite sweeps is
EVIDENCE, never proof. Every structural claim was re-tested computationally with
the sound primitives of `scripts/h2_oracle.py` against **every** member of
`L₃..L₇` (the complete truth sets: `|L₃|=1, |L₄|=1, |L₅|=3, |L₆|=8, |L₇|=39`).

Verdict legend: **SURVIVES (proved)** / **SURVIVES (empirical only)** /
**FALSE** / **NOT TESTED / weak evidence**.

---

## Summary table

| Step | Claim in proof | Logic verdict | Computational verdict |
|---|---|---|---|
| strictly smaller | `|Sᵢ|<n` | **proved** (airtight) | n/a |
| **B0** unique crossing arc | only `A–B` arc is `(u,w)` | **proved** (airtight) | 0/52 violations |
| join arc is SINGLE | `(w,u)∉A(D)` | **proved** (corollary of B0) | 0/52 (no digon join) |
| **B1 (E)** in=out≥2 | degree split at v | **proved up to `≥2`**; the `≥2` value relies on a `λ=2` dicut step that the proof admits is not fully isolated (gap #7) | identity 0/52; deg≥2 0/52 |
| **(S)** strong | Eulerian+connected underlying | **proved** (airtight) | 0/104 piece failures |
| **(C)** underlying 2-conn (clause a) | size-2 interface fan | **sketched only** | 0/104 piece failures |
| **B2 (Λ≤2)** | `λ(Dᵢ)≤λ(D)` reroute | **proved** (airtight, given single-arc) | 0/4511 + 0/104 |
| **B3 (Λ≥2)** | strong+Euler+mindeg2⇒λ≥2 | **true theorem** (prose muddled, claim standard & correct) | 0/24437 random + 0/104 |
| **(X) U** χ⃗(Dᵢ)≤3 | added-arc bound | **OPEN** | 0/104 (all χ⃗=3) |
| **(X) L** χ⃗(Dᵢ)≥3 | Hajós-criticality gluing | **OPEN — load-bearing** | 0/104 (all χ⃗=3) |
| clause (b) S,C,Λ≤2 | parallel to clause (a) | **sketched only** | 0/6 blocks fail; **all 6 are W₃ (base)** |
| clause (b) X | parity-gated gluing | **OPEN** | 0/6 |

Overall: the proof's self-assessment is **accurate and honest**. The four
"structural" conditions (E,S,Λ) are genuinely proved for clause (a); (C) is
genuinely only sketched; the entire dichromatic condition (X) is open in both
clauses; clause (b)'s structural conditions are sketched and, crucially, the
empirical evidence for them is degenerate (see below).

---

## Per-step audit

### strictly smaller — SURVIVES (proved)
`|S₁|,|S₂|<n` is built into the seam definition (`2≤|Sᵢ|<n`) and the oracle's
acceptance criterion. Airtight.

### Lemma B0 (unique crossing arc) — SURVIVES (proved)
*Logic:* every non-join arc lies inside `S₁` or inside `S₂` (oracle acceptance
criterion / third seam bullet). An arc inside `S₁` has both ends in `A∪{v}`, so
cannot join `A` to `B`; symmetrically inside `S₂`. Hence the only `A–B` arc is
`(u,w)`. Airtight.
*Computation:* over all 52 Hajós seams of the non-base members of `L₃..L₇`, the
set of `A–B` arcs equals exactly `{(u,w)}` — **0 violations** (`/tmp/audit2.py`).

**Important corollary (the single-arc property is NOT an extra assumption).** The
proof leans on `(u,w)` being a single arc (no reverse) in (S) and B2. This is a
*consequence* of B0, not an axiom: if `(w,u)` were present it would be a second
`A–B` arc, contradicting B0. So within every seam the oracle accepts, the
join arc is automatically single — verified directly: 0/52 seams have a digon
join arc (`/tmp/audit1.py`). The proof's reliance on single-arc-ness is therefore
sound. (Note: the oracle `_hajos_decompositions` does iterate digon arcs as
join-arc *candidates*, but B0/the inside-`S₁`-or-`S₂` filter rejects any that
would leave a second crossing arc, so no accepted seam has a digon join arc.)

### Lemma B1 (E): in=out≥2 — SURVIVES as in=out (proved); the `≥2` value SURVIVES empirically and is provable but the proof does not isolate it
*Logic for `indeg=outdeg`:* The Eulerian set-balance identity across the set `S₁`
(`#arcs out of S₁ = #arcs into S₁`) gives `vout_{S₂}+1 = vin_{S₂}` and
symmetrically `vin_{S₁}+1 = vout_{S₁}`; re-adding `(u,v)` to the `S₁` side and
`(v,w)` to the `S₂` side then exactly restores balance at `v`. For `x≠v` the
incident arcs are unchanged (or, at `x=u`, `(u,w)` is swapped for `(u,v)`),
preserving balance. **This part is airtight** and the exact decomposition is
verified: set-balance `out_{S₁}=in_{S₁}` 0/52, identity
`vout_{S₁}=vin_{S₁}+1 ∧ vin_{S₂}=vout_{S₂}+1` 0/52 (`/tmp/audit2.py`,
`/tmp/audit3.py`).

*The `≥2` value:* The proof needs `outdeg_{D₁}(v)=vout_{S₁}≥2`, i.e.
`vin_{S₁}≥1`. The proof's own text flags this as the "one place a one-line
strong-connectivity / `λ=2` dicut appeal is needed" and **does not isolate it as a
proved sub-step** (gap #7, acknowledged). The fact itself holds: `vin_{S₁}≥1`
and `vout_{S₂}≥1` on all 52 seams (`/tmp/audit3.py`), hence
`outdeg_{D₁}(v),indeg_{D₂}(v)≥2` 0/52 (`/tmp/audit2.py`). It is provable (D
strong ⇒ `v` has an in-neighbour; by B0 every in-neighbour of `v` lies in `S₁`
or `S₂`; the set-balance forces at least one on each side once `λ=2` rules out a
1-arc dicut at `v`), but the proof leaves it at the sketch level. **Verdict:
in=out PROVED; in=out≥2 EMPIRICALLY CONFIRMED and provable, but the proof does
not fully carry the `≥2` step.**

### (S) strong (clause a) — SURVIVES (proved)
*Logic:* `D₁` is Eulerian (B1); an Eulerian digraph is strong iff its underlying
graph is connected (Eulerian ⇒ each weak component is strong). `U(D₁) =
U(D[S₁])+{u,v}` is connected because `U(D)−{u,w}` splits into the `A∪{v}` and
`B∪{v}` sides meeting only at `v` (B0 ⇒ `{u,w}` is the unique `A–B` edge), each
side connected since `U(D)` is 2-connected. Airtight (the cited lemma "Eulerian
⇒ strong iff weakly connected" is standard and correct).
*Computation:* `is_strong` true for all 104 pieces (`/tmp/audit4.py`).

### (C) underlying 2-connected (clause a) — SKETCHED ONLY (not proved); SURVIVES empirically
The proof itself labels this **[sketched]** and writes "[open detail]: turning
'the flank inherits 2-connectivity because its interface has size 2' into a
line-by-line argument requires the fan/Menger version … standard but not written
out here." Honest. **Not a completed proof.**
*Computation:* `is_2connected` true for all 104 pieces (`/tmp/audit4.py`,
`/tmp/audit6.py` indirectly via 2-extremality). Empirically solid; logically a
gap.

### Lemma B2 (Λ upper, `λ(Dᵢ)≤2`) — SURVIVES (proved)
*Logic:* Take `k` arc-disjoint `s→t` paths in `Dᵢ`. Their arcs are all in
`D[Sᵢ]` except the single added arc `eᵢ`, which (being one arc) is used by at
most one path. Replace that one occurrence by `(u,w)` plus a fixed `w⇝v` detour
inside `S₂` (exists: `D[S₂]` strong). The other `k−1` paths use only `S₁`-arcs,
which are arc-disjoint from `(u,w)` and from the `S₂` detour. So the `k` walks
are arc-disjoint in `D`, giving `k≤λ(D)=2`. I checked this argument line by line:
the disjointness holds precisely because the non-substituted paths are confined
to one side. **Airtight given the single-arc property (which B0 supplies).**
*Computation:* `λ(piece)≤λ(join)` 0/4511 random joins; all 104 pieces have
`λ=2` exactly (`/tmp/audit6.py` shows χ-range; `check_B1` shows λ).

### Lemma B3 (Λ lower, `λ(Dᵢ)≥2`) — SURVIVES (true theorem; proof prose is muddled but the claim is standard and correct)
The written proof is garbled ("the cut vertex on the tail side would have an
unmatched out-arc"), but the *statement* — strong + Eulerian + min-degree-2 ⇒
no 1-arc cut ⇒ `λ≥2` — is a standard, true fact. Clean argument: an Eulerian
digraph decomposes into arc-disjoint closed directed trails; a single out-cut arc
`δ⁺(W)={e}` forces `δ⁻(W)={e'}` by balance, but then the closed-trail through any
out-arc of a vertex in `W` (min-out-degree ≥2 guarantees one besides the cut)
cannot return, contradicting strong/closed-trail structure. **Claim correct.**
*Computation:* 0 violations over 24,437 random strong-Eulerian-mindeg2 digraphs
(`/tmp/audit10.py`); all 104 pieces have `λ=2`. **SURVIVES** (recommend
replacing the prose with the closed-trail argument).

### (X) Conditional U (`χ⃗(Dᵢ)≤3`) — OPEN (correctly labelled)
`χ⃗(D[Sᵢ])≤χ⃗(D)=3` is proved (subdigraph monotonicity). The added arc could a
priori push χ⃗ to 4; the proof gives no argument that it does not. **OPEN.**
*Computation:* all 104 Hajós pieces and 6 tree-join blocks have `χ⃗=3` exactly
(never 4) — `/tmp/audit6.py`. Strong evidence, no proof.

### (X) Conditional L (`χ⃗(Dᵢ)≥3`) — OPEN, the load-bearing step (correctly labelled)
The gluing of two seam-agreeing `≤2`-dicolourings into a `≤2`-dicolouring of `D`
is asserted as "plausible" but the proof explicitly states it "did NOT prove the
gluing produces a valid 2-dicolouring of all of `D` — directed acyclicity of
colour classes across the seam is not verified." This is the digraph analogue of
the classical Hajós lower bound and is genuinely unproved. **OPEN.**
*Adversarial tests I ran:*
- Exhaustive: over every oracle Hajós/tree-join decomposition of every member of
  `L₃..L₇`, every piece has `χ⃗` **exactly 3** — min=max=3, 0 instances of χ⃗≤2
  (`/tmp/audit6.py`). So L never fails on the truth sets.
- I searched for a piece passing E+S+C+λ≤2 but with `χ⃗≠3`, and joined it with
  every small 2-extremal piece over all arc choices: **0 of 1680 joins were
  2-extremal** (`/tmp/audit5.py`) — could not manufacture a counterexample.
- The proof's own `check_B4`: 4,156,584 broken-piece joins, **0** 2-extremal —
  reproduced (`scripts/lemma_b_checks.py --adversarial`).
All consistent with U+L, none a proof. **OPEN.**

### §4.1 warning ("generic directed join does not preserve χ⃗") — SURVIVES (correct, important)
This is a genuine obstruction, correctly used to argue (X) cannot be quoted from
a generic join lemma. It strengthens the audit's view that U and L are the real
difficulty.

### Clause (b) tree-join A-blocks — strictly-smaller + (E) proved; **S,C,Λ≤2 SKETCHED**; X OPEN; **evidence is DEGENERATE**
*Logic:* "strictly smaller" and (E) (re-added interface digon restores balance at
`x,y`, internal vertices keep `D`-degrees) are sound. S, C, Λ≤2 are asserted
"by the same flank arguments as §2–§3" with the size-2 interface `{x,y}` in the
role of the merge vertex — i.e. **sketched, not written line-by-line** (proof's
own label). X is open for the same reason as clause (a), additionally gated by
the even-leaf-path B-parity (Lemma C of `proof_attempt.md`), which is not carried
out.

**New finding (weakens the empirical support).** Over the complete truth sets
`L₃..L₇`, the tree-join inverse produces **only 6 A-blocks, and every one is W₃**
(size 4 = a base object: generalised wheel) — **0 genuinely-recursive (non-base)
A-blocks** (`/tmp/audit7.py`). The 3 tree-join-only members (`L₇.7,14,36`) each
split into two W₃ bases. Consequences:
1. Clause (b)'s *descent into a strictly-smaller non-trivial 2-extremal block* is
   **never exercised** on the available data — every block is a base, so the
   induction terminates immediately and the recursive structural conditions are
   only ever checked on W₃.
2. Combined with the oracle's `max_internal=2` cap (gap #6, completeness hole in
   `_tree_join_decompositions`), clause-(b) evidence for S/C/Λ/X on non-trivial
   blocks is **absent**, not merely "sketched." The 0-failure claim for clause
   (b) is over 6 instances, all the same base object.

---

## Cross-cutting checks (all PASS, all evidence-not-proof)
- 41/41 non-base members of `L₃..L₇` admit a seam (38 Hajós, 3 tree-join);
  **0 obstructions** (`/tmp/audit9.py`). (Matches the seam_search ground truth;
  the count is 41 not 40 because the 1 non-base `L₅` member is included.)
- All 104 Hajós pieces satisfy all five 2-extremality conditions, 0 failures
  (`/tmp/audit4.py`).
- B4 adversarial reproduced exactly: 4,156,584 broken-piece joins, 0 2-extremal.

---

## Bottom line for the adversarial verifier

**Nothing in the proof is FALSE.** No step was broken by any member of
`L₃..L₇` or by any adversarial sweep. The proof's labelling is honest.

**Genuinely proved (airtight), clause (a):** strictly-smaller; B0; the single-arc
property (as a corollary of B0); (E) `indeg=outdeg`; (S) strong; (Λ) `λ=2` both
bounds (B2 upper is airtight; B3 lower is a correct standard theorem with
salvageable prose).

**Proved-modulo-one-line:** the `indeg=outdeg≥2` *value* `≥2` at the merge vertex
(B1) leans on an un-isolated `λ=2`/strong dicut step (proof gap #7). True and
provable, not fully written.

**Only sketched (NOT proved):** (C) underlying 2-connectivity (clause a); and all
of (S),(C),(Λ≤2) for clause (b).

**OPEN (the real content):** condition (X) `χ⃗=3` in **both** clauses —
Conditional U (≤3) and Conditional L (≥3, the load-bearing Hajós-criticality
gluing). The proof never closes these and says so. My independent adversarial
searches (1680 χ-violating joins, 4.16M broken-piece joins, full L₃..L₇
exhaustion) failed to produce any counterexample, but produced **no proof**.

**Additional weakness I surface beyond the proof's own gap list:** clause (b)'s
empirical support is **degenerate** — every tree-join A-block over the complete
truth sets is the base object W₃, so the non-trivial recursive descent for
clause (b) (S, C, Λ, X on a strictly-smaller non-base block) is *untested*, and
the `max_internal=2` oracle cap means larger tree shapes are not even searched.
Treat clause (b)'s "sketched" conditions as having essentially no non-trivial
empirical backing, not as "0-failure verified."

**Reproduction:** all probes are in `/tmp/audit{1..10}.py` (pure Python, import
`scripts/h2_oracle.py`, no deps). The proof's own
`python3 scripts/lemma_b_checks.py --adversarial` reproduces B1–B4 and PASSes.
No `.venv` was created during this audit (no networkx needed).
