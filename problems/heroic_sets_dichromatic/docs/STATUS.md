# Heroic Sets / Dichromatic — Status

**Paper:** arXiv:2009.13319 (Aboulker, Charbit, Naserasr). **Record:** Problem 1.2.
**Updated:** 2026-06-05 (round 3).

## Central question
Characterize the finite sets F of digraphs that are HEROIC: Forb_ind(F) (avoid every
member as an INDUCED subdigraph) has BOUNDED dichromatic number chi_d. Digraph analog of
Gyarfas–Sumner + hero tournaments. Conjectured answer = Conjecture 4.2 (substitution-closure
of transitive tournaments + directed-cycle blowups, plus the digon obstruction).

## Open crux — where each side stands
- **Necessity ("only if") half: CLOSED as already-known** (paper Section 6.1, C4 tower).
- **Disproof side (digon+path, no triangle): CLOSED.** Tournament tower → Forb_ind(K2,P+(m))
  non-heroic for every m>=2 (H2). The triangle member is LOAD-BEARING.
- **Sufficiency ("if") / boundedness half: OPEN — the only live direction.** Candidate
  H1 = {K2, K3, P+(k)}. ROUND-3 CORRECTION (vs primary PDF lines 315/613): the forbidden
  triangle member is **K3** (UNDIRECTED = all orientations TT3+C3 = triangle-free), NOT the
  directed C3 prior rounds wrote; the oracle's triangle-free sweep already realizes this class.
  Every enumerative / structural-invariant route is now dead; the real path is a SYMBOLIC
  nice-set argument = human math.

## Live hypotheses
- **H1** (OPEN): {K2,K3,P+(k)} heroic for all k. Boundedness evidence for k=3 now n<=8
  (0 chi_d>=3 over 151439 members). Bounded-FVS route to a proof is DEAD (G5).
- **H2** (RESOLVED disproof; NOT 'proved' per empirical gate): Forb_ind(K2,P+(m)) non-heroic,
  all m>=2; tower is a tournament, chi_d=k; oracle-verified k<=6/n=63.
- **H3** (AUDIT, downgraded): K4-free P+3-free sweep n<=7, max_chi_d=2 — but the paper already
  PROVES this bounded (<=8 with digons forbidden, line 626/695; <=414 without, Thm 6.9 line 858).
  Near-zero evidential weight; kill condition structurally impossible. Enumerator now wired.
- **H4** (PARTIAL): triangle-free bound-2 is only a finite landmark (n<=8 / Grotzsch n=11);
  Harutyunyan–Mohar [11] large-n chi_d>=3 triangle-free UNVERIFIED vs primary source.

## Graveyard (do not re-propose)
- **G1** no triangle-free chi_d>=3 seed n<=20. **G2** P+(2) lever vacuous + bundle FALSE.
- **G3** necessity reduction = already-published. **G4** C4-tower "disproof of H1" — relabeling:
  D_3 contains an induced TT3 (=K3), so NOT in the genuine class; no disproof.
- **G5** bounded-FVS lever — FVS jumps 2→3 at n=8, decoupled from chi_d (stays 2); no bound.
- **G6** P+(4) high-girth reduction — high girth FORCES induced P+(4) (chordless dicycles ≥6;
  PDF 231-241 oriented-forest argument); intuition inverted; H1(k=4) survives.

## Last decisions
- **D2**: Round 2 — H2 resolved (disproof); G1/G2/G3 killed; sufficiency isolated; H4 added.
- **D3**: Round 3 — NO frontier advance; 4 levers killed (G4,G5,G6 + H3 downgrade); K3-vs-C3
  relabeling corrected vs primary PDF; P1 landmark extended to n=8.

## Next action
Two thin verification-flavored levers: (1) verify Harutyunyan–Mohar [11] vs primary source (H4);
(2) optionally extend the P1 triangle-free landmark to n=9. Do NOT re-attempt G1/G2/G3/G4/G5/G6.

## needs_human / handback
needs_human: null. **recommend_handback: YES** — computational frontier on H1 sufficiency is
exhausted (enumerative disproofs dead, FVS invariant refuted, K4-free sweep is audit). NEEDED:
a symbolic nice-set boundedness argument (every member of Forb_ind(K2,K3,P+(k)) admits a nice
set ⇒ chi_d <= f(k) by induction), in the style of Thm 6.5 / Lemma 6.4 — human math the oracle
cannot certify. Remaining cheap tasks (H4 citation, n=9) are evidence-hardening only.
