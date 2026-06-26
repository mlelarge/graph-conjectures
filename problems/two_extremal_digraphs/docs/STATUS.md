# STATUS — Conjecture 9.2 (arXiv:2304.04690 §9): 2-extremal digraph <=> H_2

Mirror of ledger.json. Last update: 2026-06-07 (decision D5).

## Central question
Conj 9.2: a loopless digraph (digons allowed) is 2-EXTREMAL (strong, underlying-2-connected,
lambda=2, chi_vec=3) iff it lies in H_2 (symmetric odd cycles, closed under directed Hajos join +
2-Hajos tree join). Easy inclusion H_2 ⊆ 2-extremal proved (P1); open direction is 2-extremal => H_2.

## Open crux — Step 1 (3-connected case)
Goal: 3-connected 2-extremal => F_D (digon graph) is a SPANNING TREE (no digon-free cut, exclude
k(F_D)>=2). With T3 this is the ONLY gap in "3-connected 2-extremal => generalised wheel".
- k=2 EXCLUDED (T4); k=3 reduced (T5) to the single residual P4 (H3); k>=4 open (H4).
- The barrier is DICHROMATIC CRITICALITY (chi_vec=3), NOT connectivity (D3, reinforced D4). So the
  live lever is the colouring hyp H6.

## H6 frontier (PRIMARY) — after D5
H6: a 3-conn lambda=2 Eulerian digraph with a digon-free cut (k(F_D)>=2) is 2-dicolourable (chi<=2).
Antecedent NON-VACUOUS (D4) and empirically robust (0 chi=3 kills: truth set L3..L7 + ~150 generic
witnesses across D4/D5). TWO whole families of mechanism are now EXHAUSTED:
- LOCAL-INTERFACE-GLUING is DEAD (D5): the gluing of the two side-2-dicolourings across the 2-fwd/
  2-bwd cut is NOT controlled by any local invariant of the 4 crossing arcs. Width (G15) and the
  crossing-arc pairing / cyclic-order (H7/G17 census: 13 signatures, all 100% glue, zero discrimination)
  both fail; the surviving "local-merge-always-succeeds" statement is a TAUTOLOGY = chi_vec=2 (any
  global 2-dicolouring restricts and glues with zero-swap), hence circular with H6. chi=2 vs chi=3 is
  a GLOBAL acyclicity property, not a local glue rule.
- FLIP-SPACE / KRAFT COUNTING is BLOCKED at one named step (G7, G19): the c=1 whole-cube cover by a
  single MONOCHROMATIC INTRA-COMPONENT dicycle gives chi=3 at arbitrary k, so the codimension count
  has zero separation until that cover is excluded. Both counting attempts ASSUMED it away.

## Isolated open lemma — H8 (NEW, D5)
H8 (NO INTERNAL BAD DICYCLE): in a 3-conn lambda_D=2 Eulerian digon-free-cut digraph, no F_D component
carries an internal single-arc dicycle that is monochromatic under its own canonical bipartition. This
is the exact step both flip-space attempts buried (a T4 ingredient at k=2). Once H8 holds, (star)
restricts to CROSSING dicycles and only THEN can a counting/Steiner argument close H6.

## Live hypotheses
- H6 — criticality barrier; PRIMARY; antecedent non-vacuous; local-interface + flip-space routes dead.
- H8 — NEW (D5): no internal monochromatic bad dicycle for k>=2 (NOT assuming chi=3). The residual.
- H7 — interface-gluing; REFUTED (D5, G17): pairing invariant non-discriminating, local-merge tautological.
- H3 — P4 (k=3 residual); live but DEMOTED.   H4 — Step 1 for k>=4; open, likely subsumed by H6.
- H5 — connectivity-form hub barrier; REFUTED (D3).   H2 — DISPROVE 9.2 via search n>=10; clean to n<=9.

## Last decisions
- D4: four proposals refuted (G13-G16); NET ADVANCE = H6 antecedent confirmed NON-VACUOUS via generic
  census + four obvious levers killed; H6 sharpened to H7 (unknown 2/2-interface gluing invariant).
- D5: four proposals refuted (G17-G20); NET ADVANCE = the LOCAL-INTERFACE-GLUING family is exhausted
  (gluing is global, not a local crossing-arc invariant) and the flip-space count is blocked at one
  named lemma; isolated the new open lemma H8 (no internal bad dicycle for k>=2).

## needs_human / handback
needs_human: false. recommend_handback: false. H8 is a fresh, sharply-stated structural lemma with an
honest engine-able grounding step (classify internal vs crossing dicycles on the SOUND truth sets
L3..L7, uncapped cycle list); the frontier is NOT exhausted. WARNING (D5): any generic census MUST
enumerate ALL directed single-arc cycles — the cyc_cap truncation is what made G19's n=8 search vacuous.
