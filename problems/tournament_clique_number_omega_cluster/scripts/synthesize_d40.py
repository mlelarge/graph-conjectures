import os
#!/usr/bin/env python3
"""D40 synthesis: integrate the four-proposal round into ledger.json (lead agent)."""
import json, io

LP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ledger.json')
d = json.load(open(LP))
assert d["decision_log"][-1]["id"] == "D39"
DATE = d["updated_at"]  # reuse, do not fabricate a clock

# ---------------- round note (prepend D40) ----------------
d40_note = (
    "D40 (FRONTIER ADVANCED -- TWO promotions to proved; the Aubian-Coulomb preprint's own open question SETTLED affirmatively at k=4; "
    "a new generic existence floor; a candidate H19 proof mechanism isolated; ell(6) still EMPTY). FOUR proposals. "
    "(1) H20 DISCRIMINATOR (queued lever 1) RAN on the full set of known ov=4-critical circulant witnesses: ZERO H20-input hits -- "
    "none is simultaneously dic=4 and 4-dic-vertex-critical; clean XOR on that scope (dic=ov=4 => dic-NON-critical; dic-vertex-criticality "
    "only when dic=5=ov+1); skeptic corrected the claimed census 15->17 (omitted C3[AC_7] order 21 and C3[AC_9] order 27, both conform, "
    "both are themselves circulants by machine-verified relabeling) -- a census-completeness process lapse recorded. BUT the XOR barrier "
    "reading DIED THE SAME ROUND: proposal (4)'s exhaustive circulant census found the Prop-6.2 input two objects away from the known-witness "
    "list, so the exclusivity was an artifact of HOW the known witnesses had been found (dom/id-clique sandwich + lex), not a law -> G50. "
    "Facts kept: QR_19 dic=4 NOT 4-dic-vertex-critical (so the level-4 IFF analogue predicts C3[QR_19] NOT 5-critical -- untested); AC4_21 "
    "dic=5; SIX verified 5-dic-vertex-critical ov=4 circulants (4 at n=25 + C3[AC_7] o21 + C3[AC_9] o27, the G49 signature without lex). "
    "(2) NEW PROVED P21: complete one-vertex-extension census -- every order-10 tournament with ov>=4 would extend one of the 1146 P9b "
    "order-9 ov=3 classes (subadditivity), ALL 1146x512=586752 extensions decided, ZERO with ov>=4; verifier re-derived the FULL n=9 census "
    "from scratch (191536 classes, hist matches P9b) and re-decided all 586752 extensions using only certificate-checked SAT models (zero "
    "UNSAT-trust residue) => NO tournament of order<=10 has omega_vec>=4; smallest omega_vec=4 order is in [11,19]; supersedes G17's "
    "circulant-only n=10 exclusion. (3) POTENTIAL-SUM MECHANISM for H19 -> NEW H21: there EXISTS an optimal order sigma of H such that "
    "ordering C3[H] by key(c,v)=e(c)+d_sigma(v), e=(1,1,2), tie-break (d,c,pos), gives backedge clique exactly ov(H)+1 -- survives the "
    "EXHAUSTIVE generic census of ALL ov=3 inners of order<=9 (13 order-8 exhaustive + 1146 order-9, the 36 cap-200 stragglers settled by "
    "exhaustive sigma enumeration at sigma 241-874) + 10/10 random generic n=10; the ov=2 control H7 FAILS exhaustively (min merged clique "
    "4>3), localizing the D35/H16 width-2 anomaly inside the mechanism. WARNINGS: skeptic's k=4 probe on C3[QR_19] is actively negative "
    "(49214 optimal sigmas x 6 tie-breaks, min merged clique 6, never 5; non-exhaustive, and ov(C3[QR_19]) itself undecided in {5,6}); "
    "witness density decays steeply (max sigmas-to-success 4/874/31666 at n=8/9/10). empirical_not_proof: k=3 census support only. "
    "(4) NEW PROVED P22 (the round's headline): EXHAUSTIVE dic census of ALL circulant tournaments of odd order 11..29 (32736 labelled "
    "generator sets, 1520 unit-orbit classes; reproduces Neumann-Lara DM 135 ground truth -- minimum 4-dichromatic order 11, unique witness "
    "QR_11) finds TWO non-isomorphic order-25 circulants H1*=C25(1,2,3,4,5,6,7,9,10,12,14,17) and H2*=C25(1,2,3,4,5,6,7,9,11,12,15,17) "
    "that are 4-dic-vertex-critical AND 4-omega_vec-critical (ov=dic=4): the preprint's open object ('we don't know if such tournaments "
    "exist for k>=4', verbatim local PDF) EXISTS. The Prop 6.2 lift FIRES once: C3[H1*], C3[H2*] (order 75, vertex-transitive) are "
    "5-omega_vec-critical -- the first post-lex Prop-6.2 lifts, and two NEW inner-ov=4 confirmations of H19 at circulant scope. But it does "
    "NOT iterate: dic(C3[H*])>=6 > ov=5 (4-dic and 5-dic UNSAT), so the dic-ov gap re-opens at the lift even on a non-lex circulant base "
    "with ov=dic at the bottom -- H20's barrier upgraded from 'lex towers' to 'one C3 lift on every base tested'. The k=6 gate via Prop 6.2 "
    "is now: find a 5-dic-vertex-critical tournament with ov=5 -- exhaustively ABSENT among circulants of odd order<=29 (all 226 such "
    "classes have ov<=4); n=31 timed out at 880s (shardable). NET: frontier ADVANCED on three axes (P21 floor; P22 existence + order-75 "
    "5-critical lifts; H21 mechanism); next levers: census shards n in {31,33,35}, H21 k=4 strike on C3[H1*]/C3[H2*] (where ov=5 is PROVEN), "
    "symbolic sigma-existence at k=3.\n\n"
)
d["_round_note"] = d40_note + d["_round_note"]

# ---------------- benchmark.derived_measurements (append) ----------------
d["benchmark"]["derived_measurements"].append(
    "D40 layer: (a) EXISTENCE FLOOR (P21, proved): NO tournament of order<=10 has omega_vec>=4 (complete 586752-candidate one-vertex-extension "
    "census over the 1146 P9b order-9 ov=3 classes; independently re-derived end-to-end); smallest omega_vec=4 order is in [11,19]. "
    "(b) DIC-OV ALIGNMENT (P22, proved existential + exhaustive circulant-scope negatives): among ALL circulant tournaments of odd order<=29 "
    "(1520 unit-orbit classes), exactly TWO are 4-dic-vertex-critical with ov=4 (H1*, H2*, both order 25) -- the Aubian-Coulomb Prop-6.2 input "
    "at k=4; ALL 226 5-dic-vertex-critical classes have ov<=4 (no k=5 input below order 31). (c) NEW 5-omega_vec-critical vertex-transitive "
    "tournaments at order 75: C3[H1*], C3[H2*] (first Prop-6.2 lifts; peers of P19/P20, larger -- ell(5)>=49 unchanged); dic(C3[H*])>=6>ov=5 "
    "so the lift does not iterate. (d) KNOWN ov=4-critical witnesses dic profile (D40/G50): QR_19 + reverse dic=4 NOT dic-critical; AC4_21 "
    "dic=5 not critical; of the 12 n=25 sandwich witnesses, 8 have dic=4 non-critical and 4 (indices 4,7,8,9) are 5-dic-vertex-critical with "
    "dic=5=ov+1; C3[AC_7] o21 and C3[AC_9] o27 likewise 5-dic-vertex-critical with ov=4."
)

# ---------------- proved: P21, P22 ----------------
d["proved"].append({
    "id": "P21",
    "can_enter_proved": True,
    "claim_form": "universal (finite class, exhaustively decided -- a complete census fact, P5/P9b promotion class)",
    "claim": "NO tournament on <=10 vertices has omega_vec>=4; the smallest omega_vec=4 tournament has order >=11 (hence in [11,19], P15 giving 19). "
             "Mechanism: by subadditivity omega_vec(T)<=omega_vec(T-v)+1 (symbolic lemma, audited) and the complete order-9 census (P9b: max ov=3, "
             "1146 ov=3 iso classes among 191536), every order-10 T with ov>=4 is, up to iso, a one-vertex extension of a stored order-9 ov=3 class; "
             "ALL 1146x512=586752 extensions decided: ZERO have ov>=4. Replaces G17's circulant-only sub-19 exclusion with a GENERIC floor at n=10; "
             "the ell(4) ladder is generic-empty through order 10.",
    "source": "D40; verify.confirmed=true, can_enter_proved=true. Original: scripts/extend_n10_ov4_census.py (sound explicit-order filter, witness "
              "orders exact-checked at construction; 0 survivors, 0 SAT fallbacks; integrity + calibration legs passed), data/extend_n10_census_empty.json, "
              "data/extend_n10_shard_{0..3}.json. Skeptic: line-by-line filter/encoding/shard audit, 127 filter-bypassed exact bb(10,ub=4) probes incl. "
              "adversarial patterns (all <=3), input-poisoning probe (86/86 independently generated order-9 ov=3 mutants iso-match the stored 1146). "
              "Verifier: independent from-scratch n=9 census over ALL 191536 gentourng classes reproduces P9b exactly; stored 1146 proven iso-EQUAL via "
              "nauty labelg; all 586752 extensions independently re-decided with certificate-checked SAT models ONLY (every extension SAT for no-K4 with "
              "the model order clique-checked; zero UNSAT-trust residue)."
})
d["proved"].append({
    "id": "P22",
    "can_enter_proved": True,
    "claim_form": "existential (two verified constructions) + exhaustive circulant-scope census facts",
    "claim": "The Aubian-Coulomb 'Clique Number of Tournaments II' OPEN INPUT EXISTS AT k=4 (preprint, verbatim from the local PDF: 'we don't know if "
             "such tournaments exist for k>=4'): TWO non-isomorphic order-25 circulant tournaments H1*=C25({1,2,3,4,5,6,7,9,10,12,14,17}) and "
             "H2*=C25({1,2,3,4,5,6,7,9,11,12,15,17}) are simultaneously 4-dic-vertex-critical AND 4-omega_vec-critical (omega_vec=dic=4; deletion "
             "ov=3 and dic=3; vertex-transitive). CONSEQUENCE (Prop 6.2 + full computational verification): C3[H1*] and C3[H2*] (order 75, "
             "vertex-transitive) are 5-omega_vec-critical -- the first post-lex Prop-6.2 lifts (peers of P19/P20 at larger order; ell(5)>=49 "
             "unchanged) and two inner-ov=4 confirmations of H19 at circulant scope. THE LIFT DOES NOT ITERATE: dic(C3[H*])>=6 > ov=5 (4-dic and "
             "5-dic UNSAT), so no k=6 object follows. SCOPED EXHAUSTIVE NEGATIVES (circulant family, odd order<=29 ONLY -- not generic universals): "
             "of 70 4-dic-vertex-critical unit-orbit classes exactly the two winners have ov=4; ALL 226 5-dic-vertex-critical classes have ov<=4 "
             "(no k=5 Prop-6.2 input below order 31); discovered by an exhaustive dic census of ALL 32736 labelled generator sets (1520 orbit "
             "classes), externally validated against Neumann-Lara DM 135 (minimum 4-dichromatic order 11, unique witness QR_11, reproduced incl. "
             "raw brute force).",
    "source": "D40; verify.confirmed=true, can_enter_proved=true (existential bar: every UNSAT leg two-solver Cadical153+Minisat22, every SAT leg "
              "witness-verified with independent clique/acyclicity code, encodings re-derived from scratch by the verifier, full census independently "
              "reproduced with matching per-order counts 4/6/16/16/30/88/94/208/472/586; the lift's 5-criticality lower bound is a short symbolic "
              "argument checked by the verifier, not a citation). Caveats: UNSAT legs certificate-free (no DRAT); AC4_21 byproduct single-pipeline. "
              "Scripts scripts/census_dic_circulant.py, scripts/census_ov_step3.py, scripts/census_lift_step4.py; data data/census_{dic_circulant,"
              "ov_step3,lift_step4}.json. Citations verified: NL-Urrutia DM 49(1984) is r>=3, r!=4 (NOT 'every r>=2'); NL DM 170(1997); NL DM 135(1994) "
              "reproduced computationally; nothing load-bearing rests on the literature (census regenerated the class)."
})

# ---------------- open_crux rewrite ----------------
d["open_crux"] = (
    "Conj 5.10 PROVEN k=3,4,5 (AC_n / AC_n[C3] / AC_n[AC_n]; red-team-passed). k>=6 OPEN; ell(6) EMPTY (no verified omega_vec>=6 tournament). "
    "ROUTE MAP after D40: (1) H19 VALUE lever (omega_vec(C3[H])<=ov(H)+1 for ov(H)>=3) is alive and now MECHANIZED at k=3: the potential-sum "
    "merged order (H21: key(c,v)=e(c)+d_sigma(v), e=(1,1,2), tie-break (d,c,pos), sigma existential over optimal orders of H) achieves clique "
    "exactly ov+1 on the EXHAUSTIVE generic census of ALL ov=3 inners of order<=9 plus 10/10 random n=10, and the ov=2 control fails -- but the "
    "mechanism is UNVERIFIED beyond k=3 with one active negative signal (C3[QR_19]: 49214 optimal sigmas never below merged clique 6, non-exhaustive); "
    "the missing step is SYMBOLIC sigma-existence at k=3, or a k=4 merged-clique-5 witness -- concrete new target: C3[H1*]/C3[H2*] (order 75), where "
    "ov=5 is PROVEN (P22), so H21 predicts some optimal sigma of H* reaches merged clique exactly 5. H19 itself gained two inner-ov=4 circulant-scope "
    "confirmations (C3[H1*]=C3[H2*]=5=4+1, proven values). (2) Prop 6.2 dic-lift: the preprint's open input EXISTS at k=4 (P22) and the lift FIRED "
    "once (order-75 5-critical lifts) but does NOT iterate -- dic(C3[H*])>=6>ov=5; the dic-ov gap re-opens at EVERY C3 lift tested, lex or not (H20 "
    "barrier upgraded). The k=6 gate via Prop 6.2 is now precisely: find a 5-dic-vertex-critical tournament with omega_vec=5. Supply status: "
    "exhaustively ABSENT among circulants of odd order<=29 (all 226 5-dic-vc classes have ov<=4); next supply = census shards at odd n in {31,33,35} "
    "(n=31 timed out unsharded), non-vertex-transitive constructions (no exhaustive reach), or proving some order-75 lift is itself the k=5 input "
    "(dead: dic>=6 there). (3) Generic/random k=6 hunts DEAD (G48/H18: 40/40 random n in {45..67} no-K6 SAT sub-second; 42 sampled circulants "
    "n in {37..49} likewise); smallest omega_vec=4 tournament is PROVED order>=11 (P21), so generic k-witness orders start high. (4) QR_19[AC_7] "
    "(order 133): ov=6 EXACT, vertex-transitive, 6-criticality UNRESOLVED (deletion in {5,6}), SAT-walled (G47) -- needs a 132-vertex no-K6 UNSAT "
    "or a lucky clique-5 order; additionally the level-4 IFF analogue (QR_19 NOT 4-dic-vertex-critical, D40) predicts C3[QR_19] is NOT 5-critical "
    "(untested). The XOR reading 'ov-alignment excludes dic-criticality' is DEAD (G50): it held on the 17 previously-known ov=4-critical witnesses "
    "but P22's exhaustive census found aligned objects immediately outside that biased sample."
)

# ---------------- live_hypotheses: update H19, H20; add H21 ----------------
for h in d["live_hypotheses"]:
    if h["id"] == "H19":
        h["status"] += (
            " D40 UPDATE: (a) a candidate PROOF MECHANISM is isolated -> H21 (potential-sum merged order; survives the same exhaustive "
            "generic census 13+1146 + 10/10 random n=10; ov=2 control fails exhaustively, localizing the width-2 anomaly inside the "
            "mechanism); (b) TWO new inner-ov=4 datapoints at circulant scope: omega_vec(C3[H1*])=omega_vec(C3[H2*])=5=4+1 PROVEN (P22, "
            "order 75) -- the first proven H19-conforming values with inner ov=4 (structured scope; the generic inner-ov>=4 layer starts "
            "at order 19 per P21+P15 and is census-unreachable); (c) caution: C3[QR_19] value still undecided in {5,6}, and the H21 k=4 "
            "probe there is actively negative (min merged clique 6 over 49214 sigmas)."
        )
    if h["id"] == "H20":
        h["statement"] = (
            "DIC-CRITICALITY LIFT (Aubian-Coulomb Prop 6.2) + DIC-GAP BARRIER, REVISED at D40. Positive: the preprint's required input "
            "(k-dic-vertex-critical with omega_vec=k) EXISTS at k=4 -- P22's H1*/H2* (order 25, found by exhaustive circulant census, NOT "
            "among the previously-known witnesses) -- and the lift fires: C3[H*] (order 75) is 5-omega_vec-critical. Conditional IFF leg "
            "(C3[H] 4-critical IFF H 3-dic-vertex-critical) still census-confirmed at inner order<=8. Barrier (UPGRADED): the dic-ov gap "
            "re-opens at EVERY C3 lift tested, lex-built or not -- dic(C3[H*])>=6 > ov=5 even though the base has ov=dic=4 -- so Prop 6.2 "
            "fires at most ONCE per supply object and cannot self-iterate; each level k needs a FRESH k-dic-vertex-critical ov=k object. "
            "k=6 gate = a 5-dic-vertex-critical tournament with ov=5: exhaustively absent among circulants of odd order<=29 (all 226 "
            "classes ov<=4; P22). On the 17 previously-known ov=4-critical witnesses dic-criticality and ov-alignment are mutually "
            "exclusive (D40/G50 facts: QR_19 dic=4 non-critical; AC4_21 dic=5; the only dic-critical ones have dic=5=ov+1) -- but that "
            "XOR is a sample artifact, not a law (H1*/H2* break it)."
        )
        h["prediction"] = (
            "NEXT DISCRIMINATORS: (a) census shards odd n in {31,33,35} hunting a 5-dic-vertex-critical circulant with ov=5 (no-K5 UNSAT) "
            "-- any hit makes C3[that] the FIRST 6-omega_vec-critical tournament; (b) the level-4 IFF analogue predicts C3[QR_19] (order 57) "
            "is NOT 5-omega_vec-critical (QR_19 is not 4-dic-vertex-critical) -- a falsifiable untested prediction; (c) KILL of the barrier "
            "leg: any base with ov=dic=k whose C3 lift keeps dic=k+1=ov (would let Prop 6.2 iterate)."
        )
        h["status"] = (
            "REVISED (D40). Input-existence leg PROMOTED (P22, can_enter_proved). Barrier leg holds on every C3 lift computed to date "
            "(C3[AC_7] dic 5 vs ov 4; C3[H1*]/C3[H2*] dic>=6 vs ov 5; lex towers per G49) -- structural conjecture supported by exact "
            "two-solver computations, not a theorem. The k=5-input negative is EXHAUSTIVE only for circulants of odd order<=29."
        )
d["live_hypotheses"].append({
    "id": "H21",
    "claim_form": "universal (scoped conjecture with an existential inner quantifier; supported at k=3, order<=9 generic census scope)",
    "statement": "POTENTIAL-SUM MECHANISM for H19 (candidate uniform proof skeleton): for every tournament H with ov(H)=k>=3 there EXISTS an "
                 "optimal order sigma of H (backedge clique exactly k) such that ordering C3[H] by key(c,v)=e(c)+d_sigma(v) -- e=(1,1,2) on the "
                 "outer C3, d_sigma(v)=size of the largest backedge clique of H^sigma with sigma-maximum v -- with the single deterministic "
                 "tie-break (d, c, sigma-pos), gives backedge clique exactly k+1. Clique <= max(e)+max(d)-1 = k+1 is the same first-moment "
                 "potential bookkeeping that proved the k=4/5 upper bounds; only sigma is existential.",
    "prediction": "CONFIRM: a symbolic characterization of the load-bearing sigma property at k=3 (mine the 36 hard n=9 classes: what makes "
                  "sigma 241-874 work where 1-240 fail), or a k=4 instance with merged clique exactly 5 -- concrete target C3[H1*]/C3[H2*] "
                  "(P22: ov=5 PROVEN, so H21 predicts a witness sigma exists). KILL: any H with ov(H)>=3 where EXHAUSTIVE optimal-sigma "
                  "enumeration never gets the merged clique below k+2 (note C3[QR_19] is a PARTIAL negative: 49214 sigmas x 6 tie-breaks, "
                  "min 6, non-exhaustive, and its true value in {5,6} is itself undecided).",
    "status": "NEW (D40, the round's mechanism survivor). Survives the EXHAUSTIVE generic census of ALL ov=3 inners of order<=9 (13 order-8 "
              "exhaustive-over-sigmas + 1146 order-9, the 36 cap-200 stragglers settled by exhaustive enumeration; every witness "
              "core.omega_of_order-verified; independently re-implemented and reproduced) + 10/10 random generic n=10. The ov=2 control H7 "
              "FAILS exhaustively (48 optimal sigmas, min merged clique 4>3) -- the width-2 anomaly is localized INSIDE the mechanism. "
              "WARNING legs: witness density decays steeply (max sigmas-to-success 4/874/31666 at n=8/9/10), so tower-scale use cannot "
              "assume small sigma caps; zero positive evidence beyond k=3. empirical_not_proof bars promotion; the symbolic content (WHY "
              "an optimal sigma with this key always exists at k=3) is entirely open."
})

# ---------------- graveyard: G50 ----------------
d["graveyard"].append({
    "id": "G50",
    "claim": "H20 DISCRIMINATOR / XOR-BARRIER on the known ov=4-critical witnesses (D40 lever 1): some known ov=4-critical circulant (QR_19, "
             "AC4_21, the 12 n=25 sandwich witnesses, + skeptic-added C3[AC_7], C3[AC_9]) is dic=4 AND 4-dic-vertex-critical, unlocking the "
             "C3 lift at order 57/63; hardened into the barrier reading 'ov-alignment and dic-vertex-criticality are mutually exclusive'",
    "kill": "KILL branch fired 17/17 (zero H20-input hits; exact two-solver SAT, independently re-verified): on the known-witness scope the "
            "XOR holds (dic=ov=4 => non-critical; dic-critical only when dic=5=ov+1). BUT the BARRIER reading is DEAD: the same round's "
            "exhaustive circulant dic census (P22) found two order-25 circulants with ov=dic=4 AND 4-dic-vertex-criticality just outside the "
            "known-witness list -- the exclusivity was a selection artifact of the dom/id-clique-sandwich + lex provenance of the known "
            "witnesses, the worst possible sample for a universal (universal_needs_generic_census in action). Never re-propose 'no ov=4-critical "
            "tournament is 4-dic-vertex-critical' -- it is FALSE. Salvage kept: QR_19 (+reverse) dic=4 NOT 4-dic-vertex-critical (=> level-4 IFF "
            "analogue predicts C3[QR_19] NOT 5-critical, untested); AC4_21 dic=5 not critical; SIX verified 5-dic-vertex-critical ov=4 circulants "
            "(n25 indices 4,7,8,9 + C3[AC_7] o21 + C3[AC_9] o27). Process warning: the proposal's 'ALL 15 known' was factually false (>=17); "
            "census-of-own-class completeness must be checked against the ledger before claiming full scope. Artifacts: "
            "scripts/h20_discriminator_dic_qr19_ac421.py, data/h20_discriminator_qr19_ac421.json."
})

# ---------------- decision_log: D40 ----------------
d["decision_log"].append({
    "id": "D40",
    "summary": "FOUR-PROPOSAL ROUND (" + DATE + "): TWO PROMOTIONS (P21, P22), ONE NEW MECHANISM HYPOTHESIS (H21), ONE GRAVEYARD (G50); the "
               "Aubian-Coulomb preprint's open question SETTLED affirmatively at k=4; ell(6) still EMPTY. (1) H20 discriminator: zero hits on "
               "all 17 known ov=4-critical circulant witnesses (skeptic completed the census 15->17); XOR signature held there but was killed "
               "as a barrier by (4) -> G50; byproducts QR_19 dic=4 non-critical, AC4_21 dic=5, six 5-dic-vc ov=4 circulants. (2) P21 PROVED: "
               "complete 586752-extension census (P9b base + subadditivity; verifier re-derived everything from scratch, certificate-checked "
               "SAT only) => no order-10 tournament has omega_vec>=4; smallest ov=4 order in [11,19]. (3) H21 NEW: potential-sum merged order "
               "(key e(c)+d_sigma(v), tie-break (d,c,pos), sigma existential) hits clique ov+1 on the EXHAUSTIVE generic ov=3 census order<=9 "
               "+ 10/10 random n=10; ov=2 control fails exhaustively; k=4 probe on C3[QR_19] actively negative (min 6 over 49214 sigmas); "
               "k=3-scope support only. (4) P22 PROVED (headline): exhaustive circulant dic census odd n<=29 (1520 orbit classes, Neumann-Lara "
               "validated) finds H1*/H2* (order 25) with ov=dic=4 AND 4-dic-vertex-criticality; Prop 6.2 lift fires ONCE -- C3[H1*]/C3[H2*] "
               "(order 75, vertex-transitive) are 5-omega_vec-critical, two proven inner-ov=4 H19 confirmations -- but does NOT iterate "
               "(dic(C3[H*])>=6>ov=5); all 226 5-dic-vc circulant classes (odd n<=29) have ov<=4, so the k=6 gate (a 5-dic-vc tournament with "
               "ov=5) has no circulant supply below order 31. FRONTIER ADVANCED: new proved floor (P21), the open input found + first post-lex "
               "lifts at order 75 (P22), a uniform candidate proof object for H19 (H21), and the k=6 gate reduced to a single concrete supply "
               "question. NEXT: census shards n in {31,33,35}; H21 k=4 strike on C3[H1*] (ov=5 proven); symbolic sigma-existence at k=3; "
               "test the prediction C3[QR_19] NOT 5-critical.",
    "frontier_advanced": True
})

# ---------------- next_action / handback ----------------
d["next_action"] = (
    "Three engine-feasible levers, priority order. (1) k=5 PROP-6.2 INPUT HUNT (the direct k=6 gate): extend the exhaustive circulant dic census "
    "to odd n in {31,33,35} hunting a 5-dic-vertex-critical circulant with omega_vec=5 (no-K5 UNSAT x2 solvers + clique-5 witness order). MUST be "
    "sharded (n=31 died at 880s unsharded): split the 2^15 generator sets per n into foreground timeout-guarded blocks; any hit makes C3[that] "
    "(order 3n<=105) the FIRST 6-omega_vec-critical tournament via the now-PROVEN-fireable Prop 6.2 route (P22). (2) H21 k=4 STRIKE on the new "
    "P22 objects: run the potential-sum optimal-sigma sweep on C3[H1*]/C3[H2*] (order 75) where, unlike C3[QR_19], the target value ov=5 is "
    "PROVEN -- a merged order with clique exactly 5 is the first k=4 confirmation of the mechanism; exhaustive failure at feasible sigma depth = "
    "strong evidence H21 is k=3-only, refocusing H19 on a different skeleton. Cheap add-on: decide ov(C3[QR_19]) in {5,6} if any new template "
    "reaches clique 5, and test the standing prediction that C3[QR_19] is NOT 5-critical. (3) H21 SYMBOLIC MINING: on the 36 hard n=9 classes, "
    "extract what distinguishes the first WORKING sigma (rank 241-874) from the failing ones -- the load-bearing sigma property is the missing "
    "hypothesis of a symbolic k=3 proof. DO NOT retry: general H16 (FALSE); 'no ov=4-critical tournament is 4-dic-vertex-critical' (FALSE, G50/P22); "
    "first-moment/random k=6 hunts (G48); lex-tower dic-lifts (G49); QR_19[AC_7] deletion search at exhausted depth (G47); r=5 circulant census "
    "below order 31 (exhausted, P22)."
)
d["_recommend_handback_detail"] = (
    "CLEAR at D40 (stays cleared). The computational frontier is NOT exhausted: three live engine levers (sharded n in {31,33,35} dic census for "
    "the k=5 Prop-6.2 input; H21 potential-sum k=4 strike on the order-75 P22 lifts where ov=5 is proven; sigma-property mining on the 36 hard "
    "k=3 classes). Handback becomes appropriate only if all three fail; the human targets would then be (a) symbolic H19/H21 (sigma-existence at "
    "k=3), and (b) a non-computational supply of a 5-dic-vertex-critical tournament with omega_vec=5 (the preprint's open question, now settled "
    "at k=4 by P22 but open at k=5)."
)
d["needs_human"] = False
d["recommend_handback"] = False
d["recommend_handback_flag"] = False
d["frontier_advanced"] = True

with open(LP, "w") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("ledger rewritten OK")
json.load(open(LP))
print("re-parse OK; decision_log tail:", json.load(open(LP))["decision_log"][-1]["id"])
