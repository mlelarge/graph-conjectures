# STATUS — chordal_digraph_dichromatic_construction_size (round 5, 2026-06-06)

Mirror of ledger.json. Source of truth is the ledger.

## Central question
Paper arXiv:2202.01006 (Aboulker–Bousquet–de Verclos) builds, for every k, a digraph in
C_3 (oriented; no transitive triangle TT3; no induced directed cycle of length ≥ 4) with
dichromatic number k+1 and DOUBLY-EXPONENTIAL order. Section 3 asks: can the example shrink?
Finite handle: m(k) = min order of a C_3 digraph with chi_vec ≥ k. True growth of m(k) is open.

## Where the bracket stands (NO BOUND MOVED IN R5)
m(1)=1 (P1), m(2)=3 (P2) — EXACT, in proved[]. m(3): **10 ≤ m(3) ≤ (paper doubly-exp)**.
m(3) ≥ 8 is proved[] (P3). m(3) ≥ 9 (R3) and m(3) ≥ 10 (R4) are SOUND finite-n lower bounds,
NOT in proved[] (empirical_not_proof gate). m(3) ≥ 11 is NOT yet established.

## open_crux — both sides
- LOWER side: m(3) ≥ 10 stands (sound complete n≤9 scan; 12.6M C_3 digraphs, max_chi=2).
  R5 ENGINEERING-ONLY: the n=10 enumerator now EXISTS (scripts/m3_lb_scan_n10.py — streaming
  geng + disjoint shards; the n=9 script could not enumerate n=10 in 300s), cross-validated
  n=6/7/8, shard partition verified disjoint+exhaustive. But only SHARD 0/200 run (max_chi=2,
  no witness) = SOUND PARTIAL; m(3)≥11 UNESTABLISHED. ~100 CPU-hr campaign remains; geng is
  sparse-first, so the dense edge band (plausible witness location) is unscanned.
  ALL THREE asymptotic-lower-bound routes now dead: degeneracy threshold (G11), clique bound
  (G12), linear-acyclic-set/peeling (G13 — engine gives only a constant on sparse digraphs).
- UPPER / small-witness side: EXHAUSTED across all canonical operators. Closed families:
  G_2-products (G1–G4), Fano/K7 (G7 + R5's G14: single-shared-vertex Fano IS K7), blow-ups
  (G8), Mycielskian/apex-cones (G10), line/shift-digraph (R5's G15: L(triangle) is a fixed
  point; all in-C_3 iterates cap chi=2). Barrier: chi-lift → dense local connectivity → TT3.

## live_hypotheses
- H1 (m(3) small ≤20): strongly weakened. H2 (fast m(k) growth): finite lower bound supported,
  asymptotic form untouched. H4 (local couplings can't lift chi): supported, now broadly.
- H3 REFUTED (G1). H5 (n=8→m(3)≥9) CONFIRMED. H6 (n=9→m(3)≥10) CONFIRMED — both discharged.
- H7 (n=10→m(3)≥11): TRACTABILITY SOLVED, CAMPAIGN REMAINING — shard 0/200 done.
- H8 NEW (proposed R5): dense-first/stratified shard ordering — scan densest K4-free band
  first to turn the n=10 grind into a witness-first small-witness (m(3)=10 coup) hunt.

## Last 2 decisions
- D4 (R4): H6 CONFIRMED m(3)≥10; refuted Mycielskian (G10), degeneracy threshold (G11),
  clique-bound lemma L (G12). Frontier advanced.
- D5 (R5): ZERO bound movement, ZERO new survivors. One engineering deliverable (H7 n=10
  tractability solved, shard 0/200). Refuted peeling=free-lunch (G13), Fano=K7=G7 (G14),
  line/shift=chi-lift⇒TT3 (G15). Frontier NOT advanced — kills are variants of dead families.

## next_action / needs_human / recommend_handback
next_action: complete the H7 n=10 campaign — PREFERRED via H8 dense-first ordering (witness-first
hunt that still completes to sound m(3)≥11 if empty), else the full 200-shard disjoint partition
(NO --limit), cross-validated vs n≤9. needs_human: null. The ASYMPTOTIC growth of m(k) is now
exhausted on EVERY computational lever — only genuine human math remains (lower-bound the paper's
iterated-substitution order, or an entropy/probabilistic-deletion bound for the no-TT3-AND-
no-long-induced-dicycle pair); the oracle cannot certify an asymptotic proof.
