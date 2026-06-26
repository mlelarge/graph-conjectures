# heroic_sets_hero_forest — STATUS (mirror of ledger.json)

Updated: 2026-06-06 (D5)

## Central question
Conjecture 4.2 (Aboulker-Charbit-Naserasr, arXiv:2009.13319): for a hero H and oriented
forest F, {K2_digon, H, F} is HEROIC (bounded chi_d) iff F is a union of oriented stars OR
H is transitive. 'Only if' = PROVED (P2). Open = the 'if' direction when exactly one holds.
Smallest beachhead = Conjecture 6.2: chi_d(Forb_ind(K2_digon, ->C3, S2+)) = 2 (H1).

## Open crux — where each side stands (D5)
- EMPIRICAL (refute-only): full-class EXHAUSTIVE n=8 RUN + CLEAN (575,016,219 oriented iso-free,
  85,395 in-class, max chi_d=2, ZERO chi_d>=3); circulants to n=30 all chi_d=2. n=9 is now
  DE-PRIORITIZED (G9: ~10^11-10^12 graphs, months-long, evidence-only, gate-barred). Not a lever.
- STRUCTURAL (the live problem): class NAMED = {oriented, ->C3-free, OUT-LOCAL-TOURNAMENT} (H5).
  D5 SHARPENED it into a precise TWO-HALF split (H7, oracle-confirmed n<=6, 0 mismatches):
  {non-round strong}=={non-locally-semicomplete}=={has embedded in-star S2-}.
  - HALF A (round/circulant, e.g. C10(1,2,3)): needs a closed-form acyclic 2-partition uniform in n.
    Candidate = ONE contiguous interval of length d in C_n<1..d> (oracle-valid; the alternate-interval
    rule is dead, G12). Now a sharp self-contained lemma to prove.
  - HALF B (small non-round residue): peels n<=6 to a round in-class core, but needs a uniform
    peel+reinsert INVARIANT (the gap that killed G7/G8/G12).
  Barriers: B1 contraction chi_d-preserving; B2 dense strong members have no low-degree seed;
  B3 (NEW) no min-FAS order linearizes back-arcs (C7(2,4) crossing-width>=2 at every cut).

## Proved
- P1: chi_d(Forb_ind(K2_digon, ->C3, ->K2+K1)) = 2 (Thm 6.1, structural).
- P2: 'only if' direction of Conj 4.2 (structural, via Forb_ind(K2,C3,P4) unbounded).

## Live hypotheses
- H1 (Conj 6.2, chi_d=2): SURVIVES — full class clean to n=8 (575M), circulants to n=30. Empirical.
- H2 (characterize+2-colour strong members): blocked by B1/B2/B3; redirected into H6/H7.
- H5 (durable positive): class identity = oriented ->C3-free out-local-tournament, all N+(x) transitive.
- H6 (direct 2-colouring target): SHARPENED D5 into HALF A (round circulant, contiguous-interval rule)
  + HALF B (non-round in-star peel invariant). No linearization (B3), no contraction/peel/sparsity.
- H7 (NEW, D5 survivor): localization identity {non-round}=={non-loc-semicomplete}=={embedded in-star};
  decomposes the crux into HALF A + HALF B. A renaming that isolates the two burdens, not a reduction.
- H3 (Conj 4.4, TT_k branch): untouched. H4 (clique-contraction): RETIRED (G3/G5).

## Graveyard (kill reasons)
G1/G2 out-deg<=1 false (TT_k in-class). G3 contraction chi_d-preserving. G4 m<=2n false n=7.
G5 round-quotient!=single-cycle. G6 SMC collapses to easy C_n<1..d>. G7 max-acyclic exchange unjustified.
G8 2-in-degeneracy false n=10. G9 (NEW) n=9 empirical intractable+unresolved. G10 (NEW) cycle-sub
chi_d=2 cap true-but-disjoint from non-substitutional hard case. G11 (NEW) two-interval = tautology;
min-FAS nesting FALSE (C7(2,4)) -> B3. G12 (NEW) round/in-star reduction: alternate-interval rule false
on C10(1,2,3), peel lacks invariant (identity survives as H7).

## Last decisions
- D4: full-class n=8 RUN + CLEAN (frontier n7->n8); G6/G7/G8 killed; barrier B2 + H6.
- D5: FOUR proposals all refuted; NO bound moved, but NEW survivor H7 (two-half split) + NEW barrier B3.
  Open_crux sharpened: HALF A (prove contiguous-interval colouring of C_n<1..d> uniform in n) +
  HALF B (uniform in-star peel invariant). H1 unscathed.

## needs_human / recommend_handback
- needs_human: null. recommend_handback: null — TWO sharp, self-contained structural sub-lemmas now
  isolated (HALF A interval-acyclicity for C_n<1..d>; HALF B peel invariant). Computational frontier
  NOT exhausted: HALF A is a concrete circulant-acyclicity proof the next round can attempt directly.
