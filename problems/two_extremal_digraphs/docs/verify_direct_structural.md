# Adversarial audit of `proof_direct_structural.md` (ANGLE 2, digon-forest)

**Auditor stance:** skeptical. A step is "proved" only if its argument is airtight;
empirical agreement over n ≤ 7 is EVIDENCE, never a proof. Each structural claim
was re-tested independently against every member of `L_3 … L_7` (8 members of
`L_6`, 39 of `L_7`, 40 non-base total), recomputing 2-extremality and genuine
block decompositions rather than trusting the recorded `has_*_seam` flags.

All tests use only the pure-Python primitives in `scripts/h2_oracle.py`
(`is_2extremal`, `_hajos_decompositions`, `_tree_join_decompositions`,
`_is_generalised_wheel`, `is_symmetric_odd_cycle`). No `.venv` was created.

---

## Summary verdict

| Step | Doc label | Audit verdict |
|---|---|---|
| **L1** (leaves carry single arcs) | proved | **PROVED — airtight.** Logic and data both clean (0 violations over L_3..L_7). |
| **D1-necessity** (Hajós merge ⇒ MC=1) | proved (reused) | **PROVED — airtight.** Verified that every genuine Hajós witness has a single join arc and yields a valid mixed 2-cut, 40/40. The contrapositive (MC=0 ⇒ no Hajós seam) is a genuine theorem. |
| **P1 flavour-pruning** | proved | **PROVED for the arc-cut statement; the as-stated separator-flavour reading is INCOMPLETE.** See caveat below. |
| **Prop 2.1** (gen-wheel recognizer sound) | proved (reused) | **Accepted as sound** (used only as a sufficient filter; soundness only — completeness not relied on here). |
| **S1** (non-base ⇒ U(D) not 3-connected) | conjectural | **EMPIRICALLY SUPPORTED ONLY.** 0 counterexamples n ≤ 7. The general proof is genuinely absent; the doc's own §3 sub-case analysis stalls and cannot even exclude `F_D = ∅`. |
| **S2** (mixed-cut OR non-edge-cut) | conjectural | **EMPIRICALLY SUPPORTED ONLY.** 40/40, 0 "neither". Independently reconfirmed. Not proved. |
| **D1 dichotomy** (MC≥1 ⟺ Hajós, MC=0 ⟺ tree-join) | nec. proved / suff. conjectural | **NECESSITY proved; SUFFICIENCY empirical only.** Independently: MC = genuine-Hajós-existence on all 40 members; reverse direction unproved. |
| **B-Hajós sufficiency** | conjectural | **EMPIRICAL ONLY (37/37).** The λ=2 / χ⃗=3 preservation core is genuinely open — the wall. |
| **B-tree sufficiency** | conjectural | **EMPIRICAL ONLY (3/3).** Genuine W3 A-blocks confirmed; general proof absent. |

**Bottom line.** The proof attempt's self-assessment is HONEST and ACCURATE.
Nothing labelled "proved" is false; nothing labelled "conjectural" secretly works.
No step is FALSE. But the load-bearing reductions S1, S2, B-Hajós, B-tree are
empirical only, exactly as the doc declares. **A-prime is NOT proved by this
angle.** The two genuinely-proved facts (L1, D1-necessity) do not by themselves
yield a seam for any non-base member; they only constrain its *type*.

---

## Per-step detail

### L1 — PROVED (airtight)

*Logic.* A leaf ℓ has digon-degree 1: digon {ℓ,p} gives arcs p→ℓ, ℓ→p. Eulerian
`outdeg(ℓ) ≥ 2` forces a second out-arc ℓ→x with x ≠ p; if x→ℓ existed, {ℓ,x}
would be a second digon, contradicting digon-degree 1, so ℓ→x is single.
Symmetric for in. The loopless / no-parallel-arc convention closes the only
loophole (x = p with a parallel arc is impossible). **Airtight.**

*Data.* 0 violations over all of `L_3 … L_7` (`test_L1` PASS; independently
reconfirmed). L1 is correctly labelled proved.

### D1-necessity — PROVED (airtight), and it is the one solid reduction

*Claim.* `D` has a directed-Hajós merge vertex ⇒ `MC(D) = 1`.

*Logic.* From Def 1.5 the join arc (u,w) is single (its reverse is absent: it is
a *new* added arc), and after deleting {u,w} the merge vertex v is an articulation
point separating the u-side from the w-side. Hence (v,{u,w}) is a mixed 2-cut.
This is exactly the underlying-graph shadow of the Hajós definition. **Rigorous.**

*Adversarial stress.* For every non-base member I re-derived all genuine Hajós
witnesses (u,w,v) directly (re-running the `_hajos_decompositions` internals and
filtering on `is_2extremal` of both sides). For all of them:
(i) the join arc (u,w) is **single** (w→u absent), and
(ii) (v,{u,w}) appears in `mixed_2_cuts(n,arcs)`.
**0 problems / 40 members.** The contrapositive MC=0 ⇒ no Hajós merge is therefore
a genuine theorem; the three MC=0 members are *provably* clause-(b)-only. Correct.

### P1 flavour-pruning — caveat (the as-stated reading is incomplete, but harmless)

The doc states P1 "leaves the only admissible 2-vertex separators as
{mixed, single-edge-vertex, non-edge pair}", reading "no digon is a 2-cut".
**Caveat for rigor:** P1 (proved) is that no digon is a 2-*arc*-cut (Menger). A
digon's two endpoints could a priori still be a 2-*vertex*-cut of U(D); these are
different notions and the doc conflates them in the prose. *Empirically this gap is
benign:* I checked directly — **no digon endpoint-pair vertex-separates U(D)** in
any non-base member (0/40). But the doc's one-line justification ("by P1") does not
rigorously establish that; it would need a separate argument. This does not break
anything downstream (S2 only needs mixed-or-nonedge, which holds), but the prose
overstates what P1 delivers. **Flag as: claim true on data, justification as
written is a non-sequitur.**

### S1 — empirical only (general proof genuinely absent)

*Re-test.* Over `L_3 … L_7`, the only members with U(D) vertex-connectivity ≥ 3
are exactly the generalised wheels (0 three-connected non-wheels). Confirmed
independently. So every non-base member has a 2-vertex separator. **0 breaks.**

*Proof status.* The doc's §3 attempts the hard direction (3-connected ⇒ wheel) in
three sub-cases and explicitly stalls in all three, including the embarrassing
admission that it "cannot even rule out `F_D = ∅` structurally." This is an honest
and correct self-assessment: S1 is **not proved**. It is the cleanest candidate
for an independent theorem but remains a conjecture verified n ≤ 7.

### S2 — empirical only

*Re-test (independent crosstab over the 40 non-base members):*

| | count |
|---|---:|
| mixed-cut AND non-edge-cut | 15 |
| mixed-cut only | 22 |
| non-edge-cut only | 3 |
| **neither (would break S2)** | **0** |

(Minor doc bookkeeping nit: the doc's table says "14 (also have MC≥1)" non-edge
cuts; I count 15 mc∧ne + 3 ne-only = 18 members with a non-edge cut. The
discrepancy is in the table only, not in any claim; S2 itself — "0 neither" —
holds.) I also confirmed no member's *only* 2-separators are "pure
single-edge-vertex" pairs uncovered by flavours (i)/(ii). **0 breaks, not proved.**

### D1 dichotomy — necessity proved (above); sufficiency empirical

*Independent reverse-direction test.* For all 40 non-base members I recomputed
`genuine_hajos(D)` = "∃ Hajós split into two strictly-smaller genuinely
2-extremal blocks", NOT trusting the recorded flag. Result:
`MC(D) == genuine_hajos(D)` on **all 40** members, and the recorded
`has_hajos_seam` flag matches the recomputed value on all 40. So the dichotomy
MC≥1 ⟺ Hajós-seam-exists holds 40/40 under independent recomputation. The
*reverse* implication (MC=1 ⇒ a genuine seam, i.e. the two sides are 2-extremal)
is the conjectural B-Hajós lemma; it is verified, not proved.

### B-Hajós / B-tree sufficiency — the wall, empirical only

* B-Hajós: all 37 Hajós members have recorded sides that I independently verified
  to be **genuinely 2-extremal and strictly smaller** (0 failures). The λ=2 /
  χ⃗=3 *preservation lemma* is not proved; this is the same `k=2` reduction-lemma
  wall the other angles hit. Correctly labelled the load-bearing open core.
* B-tree: the 3 tree-join members each genuinely decompose with a single
  **W3** A-block (`n=4`, `is_2extremal=True`, `is_generalised_wheel=True`,
  strictly smaller). Confirmed by enumerating `_tree_join_decompositions` and
  testing every block with `is_2extremal`. Verified 3/3, not proved.

---

## What survives as a rigorous theorem on this angle

1. **L1** — every digon-forest leaf carries a single-in and single-out arc.
2. **D1-necessity** — directed-Hajós merge ⇒ MC=1; hence MC=0 ⇒ no Hajós seam,
   forcing the three MC=0 members into clause (b). (Independent of any conjecture.)

Everything else (S1, S2, B-Hajós, B-tree, and the full dichotomy) is **empirically
supported over n ≤ 7 and unproved in general**, matching the doc's own labels.

## What is FALSE / overstated

- **Nothing structural is FALSE.** No claimed structural fact has a counterexample
  in `L_3 … L_7`.
- **One overstated justification:** the P1 flavour-pruning prose ("no digon is a
  2-cut, by P1") silently swaps arc-connectivity (what P1 proves) for
  vertex-connectivity (what the flavour-pruning needs). The conclusion happens to
  hold on all data (0/40 digon vertex-cuts) but the one-line justification is a
  non-sequitur and should be replaced by a real argument or relabelled empirical.

## Reproduction

```
cd problems/two_extremal_digraphs
python3 scripts/direct_structural_checks.py   # L1,S1,S2,D1 — all PASS
python3 scripts/seam_invariant.py             # MC rule 40/40 + consistency
```
plus the independent adversarial recomputations recorded above (genuine
2-extremality of every Hajós side and tree-join block; MC == genuine-Hajós on all
40; digon-pair vertex-cut census = 0; S2 "neither" census = 0).
