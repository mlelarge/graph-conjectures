# STATUS — Strong Arc Decomposition (SAD) / Bang-Jensen–Yeo

Updated: 2026-06-21 (D86: residual row-capacity red-teamed; root/spare
co-support capacity isolated.)

## Central question
Is there an absolute constant K such that every K-arc-strong digraph admits a SAD
(arcs split into two spanning strongly-connected subdigraphs)? Working conjecture
**WC3: K=3 suffices**. K=2 is FALSE (infinite obstruction families); no 3-arc-strong obstruction known.

## Proved
- **P1-ECLOG (D22/D25):** Eulerian, lambda^arc >= **3 log2 n => SAD for n>=17** (6 log2 n for 3<=n<=16); n_0=17 tight; Karger thesis Thm 4.7.6.
- **P8-ECLOG-N0CURVE (D34):** Eulerian explicit-n_0(C) CURVE — every fixed rational C>2, lambda>=ceil(C log2 n) suffices for n>=n_0(C); certified **n_0(29/10)=23, n_0(11/4)=57, n_0(5/2)=777**, closed-form crude n_0 for all C>2. Eulerian-only; barrier C=2.
- **P9-N4-UNBOUNDED-MULT (NEW, D41):** **WC3 at n<=4 is a THEOREM for ALL arc multiplicities.** MULT-4 decrement lemma (a lambda>=3 arc of mult>=4 loses a copy keeping lambda>=3) + LIFT lemma collapse the INFINITE n<=4 class onto the exhaustive 116-iso (M<=3) census (all oracle-SAT, ILP cross-checked). Finite-COMPLETE reduction, generic-census bar MET, scope **n<=4 ONLY**; does NOT support WC3 at n>=5.
- **P2-CL1** bilateral lifting; **P3-R3KS** conditional near-split (gap = CRUX-A).
- **P4..P7**: arc-set counting routes refuted (P4/P5); general L-exist false (P6); local L-exit package (P7).

## Open crux (live levers PURELY SYMBOLIC or tooling)
- **CRUX-A (Conjecture-L rescue):** D42 realizes the chain kernel and
  kills every universal `X=X_P` recipe (G46), but L-exist survives.
  D43 proves the free-entry extension B3+ and verifies a stronger
  one-shot repair on the same hard pair: rehang `p5` into the cage,
  absorb `{p4,p5}`, retain the original `U`, and obtain three strict
  exits. D44 makes this reproducible in
  `scripts/chain_crossing_selection_check.py`: on that hard pair there
  are 34 B3+ free-entry candidates, 32 one-shot repairs, and 2 forced
  chain-tail repairs. D45 adds `scripts/b3_selection_suite.py`, covering
  8 stable explicit hard pairs (`t_eq_u`, `rho_headless`, `dominated`,
  `relay_free`, `core_embedding`, `blocker_cex`, `saturation_kernel`,
  `chain_kernel`); all 8 have one-shot B3+ repairs with `U` unchanged.
  D46 attempts the symbolic proof and isolates the exact missing step:
  the **Missing Entry Lemma** must prove that every realizable chain
  kernel has a U-used forced crossing tail, or a `T`-ancestor inside its
  sealed block, outside the ancestor path `A`, with a U-free entry into
  the cage and B3+'s exit count. Literal `X_P union forced` absorption
  is false (G47); DT/OUT/CT/CL are not automatically portable to a new
  set. D47 adds a negative witness against the broader all-hard-pairs
  reading: `generalized_chain_kernel_b3_defeat.py` uses an alternate
  in-class D17 rho-headless hard pair with 5 valid B3+ candidates, 0
  good rows, all failing by exit count. This is a short-chain /
  exit-head-in-subtree core, not yet a D42-style sealed multi-crossing
  chain-kernel refutation. D48 adds
  `scripts/chain_kernel_degeneracy_classifier.py`, which labels D47 as
  `short-chain-exit-head-in-subtree` and D42 as
  `sealed-multi-crossing-b3-good` with U-used forced crossings
  `[10,12]`. A bounded lift search
  (`scripts/d47_lift_search.py`, seed 4701, 5000 trials) sampled 967
  D42 hard pairs, including 428 with multi-forced crossings; all were
  B3-good and no sealed-multi-crossing B3+ failure was found. This is
  evidence, not a proof. D49 surveys the recent split-digraph literature
  and adds `scripts/pending_decomposition_probe.py`: the split-off /
  pending-completion pattern works on D42's three independent forced-chain
  vertices and on D17/D18/D19/D38, but not on the D28 tournament-core
  host under the naive two-split probe. D50 strengthens this with
  `scripts/pending_decomposition_prescribed_probe.py`: the positive cases
  still complete when one split arc through each independent vertex is
  forced red and the other blue. D42 succeeds on the first split choice;
  D28 remains no-hit. D51 counts robustness: D17/D47, D18, D19, and D38
  have 18/18 split choices and 36/36 prescriptions SAT; D42 has 24/120
  sampled choices with some SAT prescription and 98/960 SAT prescribed
  orientations; D28 has 0/18 choices, 0/36 prescriptions, all split cores
  at `lambda=1`. D52 samples 2000 D42 split choices and finds
  `lambda_counts={0:813,1:921,2:258,3:8}`. Successful choices strongly
  correlate with `heads -> chainK` and `u -> chainK` split arcs, while
  `roots -> chainK` is failure-prone. D53 adds
  `scripts/d42_split_predicate_tester.py` and proves an exact finite
  certificate for the capped D42 suite: among all `80^3=512000` capped
  choices, the only core cuts of size at most one are
  `{2,3,4,5,7,8}`, `{2,3,4,5,6,7,8}`, and
  `{2,3,4,5,6,7,8,10}`. The predicate `u_chainK>=1` and
  `u_or_heads_chainK>=2` selects 56264 choices, all 56264 repair these
  cuts, with zero bad rows; exact capped-suite recall is
  `56264/84014=66.97%`. D54 translates this into the Chain-Feed
  Missing Entry Lemma skeleton: a non-degenerate sealed multi-crossing
  chain kernel should supply two pending split paths into distinct
  chain-successor vertices, one starting at `u` and the other from `u`
  or heads. The remaining unproved step is a feed-source audit for
  forced `I` vertices on the sealed path. D55 adds
  `scripts/chain_feed_source_audit.py`: D42 has feed options
  `(1,8,9),(5,8,9),(6,8,9),(1,10,11),(5,10,11),(6,10,11),(1,12,13)`
  in D-bullet labels, giving 11 valid two-feed pairs with distinct
  forced `I` vertices and at least one `u` source. D56 adds
  `scripts/chain_feed_deletion_stress.py`: all `2^7=128` deletion
  patterns of these feed arcs were tested. 56 preserve the structural
  gates, 25 kill all valid two-feed pairs, but every no-good pattern
  fails at `lambda(D^bullet)>=3`. The nearest structural survivors still
  have exactly one valid two-feed pair; deleting all three `u` feeds
  drops a prefix cut to size 2. D57 adds
  `scripts/chain_feed_repair_search.py`: after deleting feeds to kill
  all valid two-feed pairs, it tries adding up to three substitute arcs
  from non-`u/head` sources into forced `I` vertices. It checks 247975
  repaired variants and finds zero hits; every candidate either fails to
  repair the low prefix cut, collapses the cage, or creates a shorter
  `v -> rho` path before full lambda checking is needed. D58 adds
  `docs/PRESCRIBED_PENDING_MISSING_ENTRY_LEMMA_PROOF_2026_06_18.md`,
  proving the symbolic prefix-cut substitute obstruction: any non-`u/head`
  substitute repairing the early deficient prefix cuts either has tail
  outside the prefix, collapses the cage in `D-u`, or creates a forbidden
  shortcut on the unique sealed path. D59 adds
  `scripts/chain_prefix_profile_audit.py` and
  `docs/PREFIX_PROFILE_AUDIT_AND_D58_CORRECTION_2026_06_18.md`, correcting
  the D58 existence step: the D42 prefix-lift table also contains original
  chain repairs such as `v -> chainK` and `chainK -> chainK`. Thus
  `u_chainK>=1` and `u_or_heads_chainK>=2` is a proved sufficient
  three-cut repair criterion, but it is not yet forced by
  `lambda(D^bullet)>=3`. D60 adds
  `scripts/d42_cut_cover_inequality_audit.py` and
  `docs/EXACT_CUT_COVER_CRITERION_2026_06_18.md`: in the capped D42
  suite, a pending choice repairs the split core if and only if its six
  split arcs cover the three deficient cuts by at least `(1,2,1)`. Exact
  counts: `cover_success=84014`, `d53_selected=56264`, `d53_bad=0`,
  `non_d53_success=27750`, and `broad_repair_success=19364`. D61 adds
  `docs/GENERALIZED_CUT_COVER_SELECTION_LEMMA_2026_06_18.md`, proving
  the profile-form generalized cut-cover selection lemma.  The proof
  applies 3-arc-strongness to every `Q in {Q-,Q0,Q+}` with arbitrary
  pending vertices added, obtains the inequalities
  `sum_i min(e_i(Q),f_i(Q)) >= 3-b(Q)`, and uses an interval-compression
  lemma to pack the raw witnesses into legal local two-split choices
  covering `(1,2,1)`. D62 adds
  `scripts/d42_prefix_pending_profile_audit.py` and
  `docs/PREFIX_PLUS_PENDING_PROFILE_AUDIT_2026_06_18.md`: the formula
  `d^+(Q union J)=b(Q)+sum_{i notin J}e_i(Q)+sum_{i in J}f_i(Q)` is
  proved as bookkeeping under endpoint-cleanliness and verified on all
  D42 `Q union J` cuts.  The tight capacity rows are `Q0 union {9,11}`
  and `Q+ union {9,11}`, both with out-size 3. D63 adds
  `scripts/structural_core_prefix_redteam.py` and
  `docs/STRUCTURAL_CORE_PREFIX_PROFILE_REDTEAM_2026_06_18.md`: adding
  the reverse head arc `6->5` in D-bullet labels preserves the checked
  sealed-chain gates, `lambda(host)=lambda(D^bullet)=3`, the cage, the
  unique sealed path, the forced `D_O` arcs, the sealed `B*` out-cut, and
  the original hard gateway, but changes the old `Q-` cut from out-size
  `1` to out-size `2`. Thus exact `1,0,1` is not forced by the current
  sealed-block/CL/DT hypotheses. D64 adds
  `scripts/monotone_deficient_cut_cover_audit.py` and
  `docs/MONOTONE_DEFICIENT_PREFIX_CUT_COVER_2026_06_19.md`: for the
  candidate triad `Q-,Q0,Q+`, set the repair demand to
  `r_Q=max(0,2-d_C^+(Q))`. Under the structural promise that these are
  exactly the core cuts below two, a pending split choice repairs the
  split core iff its cover vector dominates `r`. The D61 interval
  compression proof works unchanged for any `r <= (1,2,1)`. The audit
  confirms D42 has `core_outs=(1,0,1)`, `requirements=(1,2,1)`,
  `success=84014`, while the D63 perturbation has `core_outs=(2,0,1)`,
  `requirements=(0,2,1)`, `success=87064`. D65 adds
  `scripts/semicomplete_zero_prefix_reduction_audit.py` and
  `docs/SEMICOMPLETE_ZERO_PREFIX_REDUCTION_2026_06_19.md`: once the
  sealed block supplies a zero split-core prefix `Q0`, semicompleteness
  decomposes every cut into internal, external-prefix, or mixed form.
  Mixed cuts satisfy an exact formula and are automatically large except
  for a single-exchange obstruction. The audit verifies the formula on
  all `520065` mixed cuts in both D42 and the D63 perturbation; minimum
  mixed out-size is `3` in D42 and `4` in D63. D66 adds
  `scripts/rho_entry_endpoint_cleanliness_redteam.py` and
  `docs/LOCAL_PROFILE_ENDPOINT_CLEANLINESS_REDTEAM_2026_06_19.md`:
  adding a single `rho -> head` label preserves the sealed-chain gates,
  `lambda=3`, the hard gateway, and the low split-core profile, but
  creates endpoint entries into `Q0` and `Q+`. Thus the old no-entry
  endpoint-cleanliness clause is not forced by sealed-block/CL/DT. The
  D62 out-cut formula remains valid because endpoint entries do not
  leave `Q union J`; the correct structural target is no rho-label exits
  from active prefixes. D67 adds
  `scripts/one_sided_prefix_pending_audit.py` and
  `docs/ONE_SIDED_PREFIX_PENDING_FORMULA_2026_06_19.md`: it proves the
  one-sided formula
  `d^+(Q union J)=b(Q)+sum_{i notin J}e_i(Q)+sum_{i in J}f_i(Q)` under
  pending independence, no pending/non-core correction terms, and no
  endpoint exits from `Q`; endpoint entries are allowed. The audit checks
  D42, D63, D66, and the combined D63+D66 variant. D68 adds
  `scripts/local_normal_form_audit.py` and
  `docs/LOCAL_NORMAL_FORM_CONTRACT_2026_06_19.md`: it states LNF-0..4,
  proves these local conditions imply the D65 monotone deficient-prefix
  profile, and audits the local witnesses across D42/D63/D66/combined.
  D42/D66 have the single internal low cut `Q-`; D63 variants have none;
  all variants have the same external low cut `Q0 union {10}`; no
  single-exchange low cut appears. D69 adds
  `scripts/local_normal_form_deletion_redteam.py` and
  `docs/LNF_DELETION_REDTEAM_2026_06_19.md`: all 36 relevant single
  deletions and 630 relevant pair deletions were checked. There are
  `290` pre-gate LNF violations, but `287` break near-split
  semicompleteness and the remaining `3` fail `lambda(D^bullet)>=3`;
  no sealed-chain/hard-gateway counterkernel survives.
  D70 adds `scripts/local_quotient_profile_audit.py` and
  `docs/LOCAL_QUOTIENT_LEMMA_PACKAGE_2026_06_19.md`: the local
  normal-form target is reduced to two quotient expansion statements,
  HBQ (small in-cuts of `Q0` are only actual singleton weak heads) and
  FSQ (small outside out-cuts are only the actual first successor).
  Under HBQ+FSQ, the single-exchange obstruction is impossible by the
  D65 formula: the weak-head singleton term, first-successor singleton
  term, and semicomplete back term contribute at least `1+1+1`.
  D71 adds `scripts/head_block_orientation_audit.py` and
  `docs/HEAD_BLOCK_ORIENTATION_LEMMA_2026_06_19.md`: HBQ follows from
  the concrete orientation package `Q0={u} union R union Z`, where
  `R` has C7-style reserve expansion, `u` feeds the ordered head string
  `Z`, `Z` hooks into `R`, and earlier heads point to later heads.
  The only possible low complement is the first head `{z1}`; extra
  reverse-head arcs simply deactivate it.
  D72 adds `scripts/first_successor_outside_audit.py` and
  `docs/FIRST_SUCCESSOR_OUTSIDE_CORE_LEMMA_2026_06_19.md`: FSQ follows
  from the outside-core certificate `O'=O\{w1}` with
  `lambda(C[O'])>=2`, exactly one first-successor outside exit, and at
  least two returns from `O'` to `w1`.  The audit verifies
  `lambda(C[O'])=2`, `delta^+({10})=[(10,23)]`, and ten returns to
  `10` in all D42/D63/D66 variants.
  D73 adds `scripts/sealed_block_primitive_certificate_audit.py` and
  `docs/SEALED_BLOCK_PRIMITIVE_CERTIFICATE_DERIVATION_2026_06_19.md`:
  HBO is now derived from C7 reserve expansion, the `u -> Z` root fan,
  C3 hooks from K-side heads into the cage reserve, and semicompleteness
  of the head block.  D71's total ordered-head hypothesis is stronger
  than necessary; a unique head-block source is the only possible weak
  singleton.  For OC, the first-successor exit and return terms follow
  in the active case, but `lambda(C[O\{w1}])>=2` remains a separate
  W-core two-support lemma W2 not yet proved by the written CL/DT notes.
  D74 adds `scripts/w2_reversal_redteam.py` and
  `docs/W2_REVERSAL_REDTEAM_2026_06_20.md`: reversing the D42 support
  arc `(11,18)` to `(18,11)` preserves the checked sealed-chain gates,
  `lambda(D^bullet)=lambda(host)=3`, the primitive head-block package,
  and a hard gateway pair (same `T`, reroute `U(11)=22`), but makes
  `lambda(C[O\{w1}])=1` through the outside-core cut `{12}` with sole
  internal exit `(12,23)`.  The full outside quotient still has only the
  allowed low cut `{10}` because `{12}` also exits to `w1` via
  `(12,10)`.  Therefore W2 is too strong; the next target is an
  attachment-aware outside-cut certificate proving FSQ directly.
  D75 adds `scripts/attached_outside_cut_audit.py` and
  `docs/ATTACHED_OUTSIDE_CUT_LEMMA_2026_06_20.md`: FSQ is proved from
  the attachment-aware outside-cut certificate AOC.  For
  `O'=O\{w1}`, AOC requires every nonempty `B subseteq O'` to satisfy
  `d^+_{O'}(B)+d(B,{w1})>=2`, and every nonempty proper
  `A subset O'` to satisfy
  `d^+_{O'}(A)+d({w1},O'\A)>=2`, with the singleton `{w1}` retaining
  its one allowed outside exit.  The audit verifies AOC on D42,
  D63/D66, and all D74 support-reversal combinations; the D74 tight row
  is exactly `{12}`, using `(12,23)+(12,10)` or `(12,23)+(10,23)`.
  D76 adds `scripts/aoc_reversal_redteam.py` and
  `docs/AOC_REVERSAL_REDTEAM_2026_06_20.md`: single-reversal red-teaming
  shows AOC is not forced by the currently checked sealed-chain gates
  alone.  Among 27 gate-preserving single reversals, exactly the two
  top-support reversals `(22,20)->(20,22)` and `(22,21)->(21,22)` break
  AOC and FSQ, while still admitting repaired hard gateways.  The new
  low outside cut is `{23}`.  The missing primitive is therefore a
  top-support two-exit clause from DT/root-spare support.
  D77 adds `scripts/top_support_clause_audit.py` and
  `docs/TOP_SUPPORT_CLAUSE_AUDIT_2026_06_20.md`: the proposed top-support
  clause `d^+_{O'}({tau})>=2`, where `w1->tau` is the unique
  first-successor outside exit, holds on D42/D63/D66/D74 variants and
  exactly filters the D76 AOC failures among all 27 gate-preserving
  single reversals.  In D42 labels, `tau=23` and the good variants have
  exits `(23,21),(23,22)`.
  D78 adds `scripts/top_support_dt_gap_audit.py` and
  `docs/TOP_SUPPORT_DT_GAP_2026_06_20.md`: the two D76 top-support
  reversals preserve the existing DT profile exactly (`P_v`, `R`,
  `R cap P_v`, `R cap X_P`) while failing top-support and AOC.  Thus
  current DT does not imply top-support; a strengthened support-ladder
  endpoint primitive is required.
  D79 adds `docs/SUPPORT_LADDER_ENDPOINT_LEMMA_2026_06_20.md`: defines
  SLE, the support-ladder endpoint primitive saying the unique
  first-successor support target `tau` has two lower support exits in
  `O'`, and proves immediately that SLE implies the D77 top-support
  two-exit clause.  The remaining AOC proof is now the nonterminal
  outside-cut expansion away from this endpoint singleton.
  D80 adds `scripts/endpoint_reduced_aoc_profile_audit.py` and
  `docs/ENDPOINT_REDUCED_AOC_PROFILE_2026_06_20.md`: after SLE, the
  only tight AOC rows in the accepted variants are the top-support row,
  the D74 middle-support attachment row `{12}`, and the root-complement
  row `O'\{14}`.  The next proof target is now concrete:
  middle-support attachment, root-complement return, and no other tight
  outside rows.
  D81 adds `docs/ENDPOINT_REDUCED_AOC_PROOF_2026_06_20.md`: under the
  explicit endpoint-reduced package ER-0--ER-4, AOC holds and the exact
  tight rows are symbolically classified.  Without the weak middle
  vertex, the tight rows are `{tau}` and `O'\{r0}` in the prescribed
  AOC directions; with the weak middle vertex they are `{m}`, `{tau}`,
  `{m,tau}`, and `O'\{r0}` in the prescribed directions.  The remaining
  derivation target is ER-2--ER-4 from sealed-block/CL/DT: middle-support
  attachment, root-complement return, and residual outside-support
  expansion.
  D82 adds `scripts/outside_support_clause_audit.py` and
  `docs/OUTSIDE_SUPPORT_ATTACHMENT_RETURN_LEMMAS_2026_06_20.md`: the
  active first-successor plus semicompleteness proves every
  `x in O'\{tau}` returns to `w1`, which supplies the weak middle
  attachment term.  A weak middle support arc `m -> tau` plus `w1 -> tau`
  and the SLE lower fan prove the `{m}`, `{m,tau}` rows.  Two root/spare
  predecessors into `r0` prove the root-complement return row.  The audit
  verifies these clauses and residual slack on D42/D63/D66/D74 variants.
  The sole remaining endpoint-reduced AOC derivation target is ER-4:
  residual support-ladder expansion/no-other-tight-row slack.
  D83 adds `scripts/residual_ladder_separator_audit.py` and
  `docs/RESIDUAL_LADDER_SEPARATOR_ER4_2026_06_20.md`: the residual
  ladder skeleton on blocks
  `M -> T -> S -> H -> L -> P -> R -> M`, together with the active
  first-successor attachments, forces every unlisted `eta` and `zeta`
  row to have value at least three.  The proof uses monotonicity: the
  skeleton is contained in every accepted D42/D63/D66/D74 normal form,
  and adding arcs only raises the counted AOC rows.  Thus ER-4 is proved
  at the support-ladder normal-form level.  Combined with D81/D82/D79,
  AOC and hence FSQ now follow from the endpoint-reduced support package.
  D84 adds `scripts/residual_ladder_skeleton_source_audit.py` and
  `docs/RESIDUAL_LADDER_SKELETON_DERIVATION_2026_06_20.md`: every D83
  skeleton arc is assigned to a named source clause: active
  first-successor returns, middle-to-top support, distance-graded R2
  boundaries, root/spare domination, terminal support backfan, and
  shortcut orientations.  The audit verifies that these categories equal
  the D83 skeleton and that the skeleton is contained in every accepted
  D42/D63/D66/D74 normal form.  D85 adds
  `scripts/source_clause_reversal_redteam.py` and
  `docs/SOURCE_CLAUSE_REVERSAL_REDTEAM_2026_06_21.md`: among the 27
  single-reversal variants preserving the current structural gates, 18
  are AOC-good while missing at least one D84 source arc, and the only
  missing-source AOC failures are the two `top_two_fan`/SLE failures.
  Thus exact D84 source containment is a sufficient skeleton, not a
  forced raw normal form.  D86 adds
  `scripts/residual_row_capacity_redteam.py` and
  `docs/RESIDUAL_ROW_CAPACITY_REDTEAM_2026_06_21.md`: the stronger
  residual `>=3` row-capacity target is still not forced by the current
  structural gates plus SLE.  Four gate-preserving, AOC-good reversals
  delete one `L -> P` counted entry and create a new residual
  co-root/spare zeta row of value two.  The next raw target is therefore
  the capacity-critical support package, starting with the root/spare
  co-support capacity clause, not a blanket RRSP promotion.
- **CRUX-B (WC3):** n<=4 (ALL multiplicities) now PROVED (P9). n>=5 / simple n>=7 open, foreground-infeasible. **D41 (G45):** Mader-pinching generator route partly closed — splitting-off half intact on multidigraphs (balanced (3,3) de-pinch site + lambda-preserving splitting always exist), but the minimal-degree COUNT pigeonhole FAILS (108/116 minimals have only 2 balanced vertices, profile [3,3,3,m]). A sound n=5 generator must derive exhaustiveness from splitting-off itself, not the degree count.
- **Asymptotic:** C=3 accepted (D25); explicit curve every C>2 PROVED (P8); barrier C=2 (r→1). **D41 (G44):** the Eulerian half-bundle-cactus structure route to C=2 is FALSE (the directed (a,b) profile is non-constant along a DKL cactus cycle; empty half-bundles). Still needs a dynamic-concentration mechanism.

## Live hypotheses
- **H1-GENERIC-CENSUS** — simple n<=6 + multi-arc n<=4 done, 0 UNSAT; n<=4 now PROVED for all M (P9); n=5 blocked on a generator (G33/G45; splitting-off half intact).
- **H2-LEXIST / H3-LSWAP** — chord-contraction fixed-root; v-target base case is the live form.
- **H4** — Eulerian C=3 done, explicit curve proved (P8); constant-lambda blocked (G18); half-bundle C=2 route dead (G44). **H5/H6 FALSE**. **H7** sound but insufficient.
- **H8-SPINE** — branch-2 chain kernel; all computational attacks dead (G28/G29/G35/G43); A'→A'''→IN(X_P) refuted in-class (D28/D30/D31/D34).
- **H9-FORCED-ARC** — forced-arc reachability reformulation of A'; FAMILY-SCOPED, forward implication only.
- **H10-VTARGET-INTERIOR** — universal cage-sparing and universal
  `X_P` forms FALSE (D38/G42 and D42/G46). Salvage is B3+ crossing
  selection from the cage, not enlargement of `X_P`.

## Last 2 decisions
- **D86 (2026-06-21):** Added
  `scripts/residual_row_capacity_redteam.py` and
  `docs/RESIDUAL_ROW_CAPACITY_REDTEAM_2026_06_21.md`.  This refutes
  promotion of residual row-capacity from the currently formalized raw
  gates alone: four SLE-preserving, AOC-good single reversals miss one
  `L -> P` entry and create an unlisted zeta row of value two.  The
  proof now needs an explicit root/spare co-support capacity clause from
  CL/DT.
- **D85 (2026-06-21):** Added
  `scripts/source_clause_reversal_redteam.py` and
  `docs/SOURCE_CLAUSE_REVERSAL_REDTEAM_2026_06_21.md`.  This red-teams
  the post-D84 target and shows exact D84 source containment is too
  strong under the current structural gates: 18 gate-preserving,
  AOC-good single reversals miss a D84 source arc; only `top_two_fan`
  failures break AOC.
## needs_human / recommend_handback
**needs_human = null. recommend_handback = null.** Live CRUX-A move:
prove the capacity-critical support clauses needed for ER-4 from raw
sealed-block/CL/DT/no-shortcut primitives.  D86 shows the first missing
one is root/spare co-support capacity: for each `p in P`, the row
`O' \ {p}` must have at least three counted entries into `p`.
After that, prove the first lower-support co-support capacity and the
weak-middle top-pair capacity clauses, then combine them with D82 active
attachment and D79 SLE to recover residual row-capacity.  D84 remains a
sufficient skeleton and D83 proves ER-4 from it, but D85-D86 show that
neither exact source containment nor residual `>=3` capacity is forced
by the currently checked gates alone.  D73 gives primitive HBO, D71
gives HBQ, D70 gives LNF-3, D67 handles prefix-plus-pending bookkeeping,
D65 handles global cut reduction, and D64 handles cut-cover algebra. In
parallel or afterward, prove or cite the external colour-prescribed
semicomplete pending-completion theorem needed for the lift. Keep D28
separate as tournament-core / cut-avoidance unless richer critical
path-pair machinery repairs its lambda-1 core.
