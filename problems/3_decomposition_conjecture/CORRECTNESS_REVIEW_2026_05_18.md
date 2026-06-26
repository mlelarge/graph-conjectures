# Correctness Review — 3-decomposition conjecture workstream

**Date:** 2026-05-18
**Reviewer:** Independent audit, on request
**Scope:** `problems/3_decomposition_conjecture/`
**Repo commit context:** working tree at the time of review (`README.md`, `docs/plan.md`, `docs/minimal_counterexample.md`, `scripts/*`, `tests/*`, `data/*`).
**Test status:** all 33 pytest tests pass; `verify_n14_summary.py` exits OK; `sublemma_bridge_sweep.py --n-max 11` reports OK on 137 graphs (1 + 3 + 19 + 114).

---

## Executive verdict

The workstream is **honest about its own status** and does not claim the conjecture is proved. The single load-bearing *proved* result is **Lemma 1 (bridge reduction)** plus its **Sub-lemma 1′** (computer-checked up to n=11). Everything else — Lemma 2 (2-edge-cut reduction), Universal Replacement Conjecture, Lemmas B, C, the Core Absorption Lemma — is openly labelled "target", "conjecture", or "open" in the docs. The README, by contrast, is more bullish ("**First proof step done**", "**Antichain Coverage conjecture refuted at n=12**", "**n=14 essentially-3-connected sweep complete**", "**Full n=14 all-class sweep complete**"); these claims are about *computation*, not about new mathematical theorems for the conjecture, and the reader has to dig into `docs/minimal_counterexample.md` §§3.18–3.21 and §4 to see that the route to "minimal counterexample is 3-edge-connected" is still gated by an open all-orders conjecture.

Within those (modest) self-stated targets, the **mathematics that is claimed to be proved is correct, and the computational artefacts faithfully implement the definitions they claim to**. I found:

- **No false theorem statements** — every load-bearing claim called "Lemma" is either (a) elementary and correct (Lemma 1, Lemma 3.9, Theorem 3.14, the 16-trace classification in §3.4 / `trace_feasibility.py`), or (b) explicitly labelled "target" or "open" (Lemmas 2, B, C, the Universal Replacement Conjecture, Core Absorption Lemma).
- **The verifier `verify_decomposition` is correct** for the 3-decomposition predicate it claims to decide; the brute-force `find_3_decomposition` is also correct.
- **The trace-set computer `compute_trace_set_2pole` matches the formal definition** in §1.3, including the non-obvious "every T_H component must touch a T-boundary stub" clause and the T_CC singleton handling.
- **The n=12 refutation and n=14 sweep numbers reproduce on independent recount** of the JSONL records.
- **The 16-trace theorem (§3.4)** has a structural proof (patterns A/B/C in `trace_feasibility.py`) that I checked argument-by-argument; the impossibility classifications correctly partition the 18 a-priori-but-not-realised traces.

What is **load-bearing but not proved** and should be flagged for the user:

1. **The Universal Replacement Conjecture / Core Absorption Lemma is the only remaining gate** to closing Lemma 2 (i.e., "minimal counterexample is 3-edge-connected"). It is **open** at all orders ≥ 16; the n=14 sweep is exhaustive only up to n=14. The doc says this clearly, but the README is worded in a way that could be read as "Lemma 2 is essentially closed up to a routine extension".
2. **Sub-lemma 1′ is *computer-checked* up to n=11, not proved.** The proof of "minimal counterexample is bridgeless" therefore currently rests on a finite check and the **assumption** that no counterexample to Sub-lemma 1′ exists at n=13 or higher. This is plausible (and consistent with cited results of Aboomahigir–Ahanjideh–Akbari for the subcubic regime), but it is not a theorem in this codebase.
3. **The "compatibility replacement" Lemma 3.13** is correct under one subtle quantifier reading (see CRITICAL #1 below), but the doc's prose blurs the difference between "every trace τ that can appear on the opposite side B is compatible with some σ ∈ Trace(H)" and "Compat(Trace(H)) = U". The two are equivalent iff Trace(B) ⊆ U, which is the 16-trace theorem. I verified that the implementation uses the lattice-union universe, which equals U in the n≤10 and n≤12 lattices; so in practice the check is correct, but the documentation should make the dependence explicit.

In short: **the mathematics that is on disk is sound, the computations are reproducible, and the project is admirably self-critical about what is still open**. The only real risks I found are (i) one quantifier-level ambiguity in the §3.13 prose, (ii) an open-conjecture gate the README slightly under-emphasises, and (iii) the standard "computer-checked is not proved" caveat on Sub-lemma 1′. None of these is a correctness *error*.

---

## Findings by file / claim

### 1. `README.md` — overall framing

**MINOR (README.md:15–19).** The README opens with "**First proof step done.** Lemma 1 (Bridge reduction) is proved … Sub-lemma 1′ … is computer-checked on all connected 1-port subcubic graphs with n ≤ 11 vertices". This is a correct statement, but the phrasing "first proof step done" sells the computer-checked half (Sub-lemma 1′) more strongly than is warranted: as written, "bridgeless minimal counterexample" follows *only* if no n ≥ 13 1-port subcubic graph violates Sub-lemma 1′. The doc plan.md §"Bridges and minimal-counterexample structure" is more honest ("Provisional reading: as soon as Sub-lemma 1′ is in hand, …"); minimal_counterexample.md §2.1 likewise calls it "Sub-lemma 1′ (subcubic existence; to be proved separately)". I would tone the README to "Lemma 1 is proved; Sub-lemma 1′ is computer-checked through n=11 and matches the existence claim in Aboomahigir–Ahanjideh–Akbari (DAM 2021) for the subcubic regime."

**MINOR (README.md:106–118).** "**Full n=14 all-class sweep complete.** … 15176 are trace-contained in the n≤12 lattice, 2 are compatibility-universal but not trace-contained, and 0 are `neither`." This is factually correct and reproduces (I recount: `python3 -c "..." < data/n14_full.jsonl` gives exactly `{'trace_contained': 15176, 'compat_universal_not_contained': 2, 'neither': 0}`). The *interpretation* of this in the README is mildly optimistic: it strongly suggests the Universal Replacement Conjecture holds, but the doc itself (minimal_counterexample.md §3.17, §3.20, §3.21) correctly notes this is a *finite* sweep and the conjecture is **open** for n ≥ 16. The README should add a one-line caveat that n=14 is empirical evidence, not a proof.

**NIT (README.md:88–96).** "The cubic 2-vertex-cut boundary-trace lemma is still needed later for the 3-edge-connected to 3-vertex-connected upgrade." This is correct context, but it is parked here without an explicit pointer to "Lemma B (target)" in §3.21; a reader landing on the README will not realise that the same machinery shows up as Lemma B.

### 2. `docs/plan.md`

**Nothing flagged.** The plan is structurally honest: §"Bridges and minimal-counterexample structure" correctly states that Lemma 1 (bridge case) is unconditional and explicitly flags 2-edge-cut and 2-vertex-cut reductions as "not yet written down in our notation; until it is, '2-edge-cut reduces' is not a theorem-producing dependency here." §"Known partial results" is accurately split into "unconditional" and "conditional on 3-vertex-connectivity"; the table is consistent with the references I sampled (Hoffmann-Ostenhof–Kaiser–Ozeki 2018, Ozeki–Ye 2016, Bachtler–Heinrich arXiv:2104.15113, Bachtler–Krumke EJC 2022). No citation looked fabricated. **One small caveat (NIT, plan.md:139):** "Hamiltonian cubic | proved | credited in standard surveys to Akbari et al.; **citation to be verified in Phase 1** before use" — the project is appropriately suspicious of its own citation here, good.

### 3. `docs/minimal_counterexample.md` §2 (Lemma 1 / Sub-lemma 1′)

**MAJOR (minimal_counterexample.md:111–166).** The proof of **Lemma 1** is **correct** and clean. The three forbidden states {M_TT, C_TC, T_CC} at a bridge port are correctly excluded:
- M_TT: needs boundary M, but the bridge must be in T — proven at line 121.
- C_TC: needs boundary C, same reason.
- T_CC: would give deg_{T_u}(u) = 0, contradicting that T_u is a spanning tree of G_u on ≥ 2 vertices, line 138–141.

The argument at line 132 — "|V(G_u)| ≥ 2 because G is cubic, u has 3 edges, only one of which is e" — is slightly under-stated (in a simple cubic graph, |V(G_u)| ≥ 3 since u must have 2 other simple neighbours), but the conclusion is correct. No quantifier issue.

The (⇐) direction (lines 152–166) is the routine "glue two side decompositions" check; correct.

**MINOR (minimal_counterexample.md:174–195).** **Sub-lemma 1′** is correctly labelled as a separate task and the doc explicitly says "to be proved separately". The standard-argument paragraph at 188–195 is a one-line schema, not a proof. **In particular, the wording "as soon as Sub-lemma 1′ is in hand" is correct, but the README's "first proof step done" is slightly stronger than this**. Computer check: the sweep at n ≤ 11 (`scripts/sublemma_bridge_sweep.py`) verified 137 graphs (1 + 3 + 19 + 114 across n=5,7,9,11), all passing. **This is exhaustive only up to n=11**, not "all subcubic graphs". I re-ran the sweep at n=9 and n=11 and confirmed.

**NIT (decomposition.py:574–608).** The implementation `verify_bridge_side_realisable` is *correctly* stricter than the §1.3 trace definition: it requires `T_H` to span H (line 587, `nx.is_tree(T_graph) and T_graph.number_of_nodes() == n`). This matches the §2 footnote that, at a bridge, T_u is a spanning tree of G_u (not merely a forest with the right local pattern). Without this strictness, a "trace" could be locally OK at the port but globally infeasible. Good.

### 4. `docs/minimal_counterexample.md` §1 (boundary-trace formalism)

**Nothing flagged.** §1.2's five port states are exhaustive and pairwise distinct: I cross-checked against `PORT_STATE_DATA` (decomposition.py:112–118) — exact agreement. §1.3's trace definition matches `compute_trace_set_2pole` (decomposition.py:355–426) precisely, including the somewhat-non-obvious clause "every tree component incident to at least one T-coloured boundary half-edge" which `_add_2pole_traces_from_partition` (decomposition.py:451–468) enforces correctly with the T_CC-singleton exception.

The bottleneck `t_count in (n - 1, n - 2)` optimisation (decomposition.py:401) is **sound**: every T_H component must contain a T-boundary stub, and there are at most 2 such stubs (one per port), so the forest has ≤ 2 components and |T_H| ∈ {n-1, n-2}. (Note: a T_CC port's singleton component still counts as a T-component but its only "T-stub" is the singleton itself; the rest of the graph must fit in 0 or 1 other components, hence |T_H| ∈ {n-1, n-2} still.) I worked through the corner case where both ports are T_CC: that would require both singletons in T_H plus an internal-vertex-spanning forest, which is impossible because internal vertices need degT ≥ 1 — the function correctly returns nothing for that case via the `_add_2pole_traces_from_partition` validity loop.

### 5. `docs/minimal_counterexample.md` §3 (Lemma 2 / Universal Replacement)

**Nothing flagged on §3.1–§3.4 (statements).** The 16-trace theorem (§3.4) is supported by `scripts/trace_feasibility.py`, which I ran and which gives counts `{realised: 16, impossible_C_cycle_cannot_close: 8, impossible_no_T_stub_for_internal: 6, impossible_TCC_in_shared_block: 4, open: 0}` totalling 34. The three impossibility patterns are stated as structural lemmas with explicit reasons (trace_feasibility.py:86–137); each is a one-paragraph argument about cycle closure / T-component connectivity / T_CC degT_H = 0. These arguments are correct.

**MAJOR but resolved (minimal_counterexample.md:319–332).** The Lemma 2 statement (§3.5) is **carefully written**: it correctly gives the *replacement* direction Trace(A') ⊆ Trace(G[A]), not the *envelope* direction Trace(H) ⊆ Trace(C). The doc even repeats the inclusion in two formulations and notes which goes to which lift direction. The `coverage_check.py` script (lines 54–121) implements both directions separately (`find_replacement_gadget` for Lemma 2, `check_coverage` for diagnostics) and warns the reader of the difference in the docstring at coverage_check.py:67–78. **Good engineering hygiene; this is the kind of place where the wrong inclusion would silently void the lemma**, and the project handled it correctly.

**CRITICAL (minimal_counterexample.md:782–803).** **Lemma 3.13 (Compatibility replacement)**: the *statement* in §3.13 is correct, but the quantifier in "Suppose Trace(B) is compatibility-universal" is subtle. The proof restricts D' to A and gets τ_A ∈ Trace(A) ⊆ **U**. For the lift to work, **Trace(A) ⊆ U is needed**, which is exactly the 16-trace theorem. The proof should make this dependency explicit (it currently writes "By the 16-trace theorem"). I confirm that the **implementation** `is_compatibility_universal` in `full_replacement_sweep.py:84–95` walks over `universe = union_of_all_traces(payload)`, and that union *equals* the theoretical 16-trace U for both the n≤10 and n≤12 lattices (I verified this: `python3 -c "..."` returns universe size 16 for both, and the sets are equal). So in current code, "compatibility-universal w.r.t. lattice universe" = "compatibility-universal w.r.t. the theoretical universe". But if the lattice ever gains new traces, **this equivalence would silently break**, and the code would test a weaker condition than the doc claims. **Recommendation:** assert in `is_compatibility_universal` that the universe used equals the theoretical 16-trace U, or compute U from `trace_feasibility.py`'s exhaustive enumeration rather than from the lattice.

**MINOR (minimal_counterexample.md:840–878).** **Theorem 3.14 (four-axis characterisation)** is **correct**, and I cross-verified it: running `compatibility_universality.py` against the n≤10 lattice gives `axis_agreement_count = 59 / 59` (all classes), and `min_universal_trace_count = 4`, `max_non_universal_trace_count = 10`. The proof at minimal_counterexample.md:855–878 has one small gap of *phrasing* — the converse argument at 873–878 says "choose the opposite trace in U with the same boundary colour and opposite required π" — this is correct (because (T,T) pi-compatibility is a *complementation* of joined vs. split), but the writing could be tightened. The argument is right; the prose drag is a NIT.

**MINOR (minimal_counterexample.md:905–917).** §3.16 "trace-count threshold" is correctly flagged as an **empirical** property of the n≤10 lattice, not a theorem about arbitrary subsets of U: "It is an empirical property of the realised n≤10 lattice classes, not a theorem about arbitrary subsets of U." The doc resists the temptation to elevate this to a structural claim. Good.

**MAJOR (minimal_counterexample.md:826–832, 1037–1040, 1170–1196).** The **Universal Replacement Conjecture** (§3.13 final paragraph and §3.20's Core Absorption Lemma) is **clearly an open conjecture**, repeatedly so labelled, with the empirical n=14 evidence framed as "directionally good, not decisive" earlier in the doc (line 982). The narrative is honest: it does not claim a theorem. **The README's framing is somewhat softer-edged** ("the Universal Replacement Conjecture therefore survives the complete n=14 sweep") and a reader might miss that this is a conjecture, not a corollary. I would not call this an error, but it is a presentational asymmetry.

**MINOR (minimal_counterexample.md:1346–1353).** The §4 "Target theorem" statement *(assumes Sub-lemma 1′ and Lemma 2)* and its short proof correctly says "Lemma 2 (§3.4)" — small typo, the right pointer is §3.13 / §3.20 (Lemma 2 *target*); §3.4 is the 16-trace classification. NIT.

### 6. `docs/minimal_counterexample.md` §3.7–§3.10 (failure structural classification)

**Nothing flagged.** I cross-checked the structural classification at §3.7 against `data/failure_structural_classification_n12.json`, and against direct computation on the four graph6 strings (`K?AB?pa[CWP_`, `K?` + ``@CQWSPKCo``, `K?ABAaKh@oGW`, `K?AB?qQT@WWG`):

- `K?AB?pa[CWP_` ports (3,7): bridges `[(3,7), (3,9), (4,7)]`, port 3 is a port endpoint of bridge (3,7) (a port-to-port bridge), (3,9) is port-to-internal, (4,7) is internal-to-port. Trace count = 4 (matches doc). Verified by hand.
- `K?AB?qQT@WWG` ports (2,4): 12 vertices, 17 edges, degree-2 vertices = {2,4}, trace count = 12. Matches doc.

**Lemma 3.9** (minimal_counterexample.md:570–625) — the proof is a clean essential-2-edge-cut minimization argument. The case analysis (Case 1, Case 2a, Case 2b, port-to-port) is exhaustive. I checked each case for missing sub-cases:
- Case 1 (≥1 of A_1, A_2 port-free): correctly yields e* is a bridge of G.
- Case 2a (neither bridge endpoint is a port): correctly yields the smaller essential 2-cut {e_1, e*}.
- Case 2b (exactly one bridge endpoint is a port): correctly yields the smaller cut {e_2, e*}.
- Port-to-port: correctly noted as the unresolved residual.

The proof is correct. The n=12 empirical check at §3.10 (lines 629–648) verifies Case 1 applies to one Class-I graph and Case 2b applies to the other.

### 7. `docs/minimal_counterexample.md` §3.12 (Class III compatibility absorber)

**Nothing flagged on the statement.** Lemma 3.12 is a special case of Lemma 3.13 (compatibility replacement) applied to one specific n=12 graph. The witness table is archived in `data/classIII_absorber_witnesses.json` and produced by `classIII_absorber_check.py`. The script computes Trace(H, R) on `K?AB?qQT@WWG` with ports (2,4), then for each of the 16 universe traces checks compatibility with every trace in Trace(H). I verified the trace count of H equals 12 (matches §3.12 line 681).

**MINOR (classIII_absorber_check.py:24).** The "UNIVERSAL_GADGET" record (graph6 `I?B@t`gs?`, ports (4,5), class C58) is referred to but not actually exercised by the script — the script's output only depends on the residual side and the lattice universe. This is fine for the audit purpose but the variable could mislead a casual reader into thinking the gadget is being plugged in. Documentation NIT.

### 8. `scripts/decomposition.py`

**Nothing flagged on the verifier.** `verify_decomposition` (lines 54–103) correctly checks:
- cubic and connected (lines 59–62);
- labels cover E(G) exactly and use only {T,C,M} (lines 64–69);
- |T| = n−1 (line 76);
- T is a spanning tree (lines 79–87);
- C is 2-regular (lines 89–94);
- M is a matching (lines 96–101).

This is the trust root and it is propagator-agnostic, as advertised. I sanity-checked it on K_4, K_{3,3}, prism, Petersen — all pass.

**Nothing flagged on the trace-set computer.** `compute_trace_set_2pole` (lines 355–426) and the helper `_add_2pole_traces_from_partition` (lines 429–486) match §1.3's definition. The optimisation t_count ∈ {n−1, n−2} is sound (see §4 above). The π reconstruction (lines 472–483) correctly puts T_CC ports in their own block (`("alone", i)` keys), and non-T_CC T-incident ports in their tree-component block (`("comp", j)` keys). The T_CC singleton-component validity check at line 451–459 correctly allows a singleton T-component **iff** that singleton is a T_CC port.

**Nothing flagged on the brute-force finder.** `find_3_decomposition` (lines 614–681) iterates over (n−1)-subsets of E(G) to find spanning trees, then partitions the cotree into C ⊔ M and tests local properties. The internal connected-component check at lines 654–664 makes sure each component of C is actually a cycle (i.e., 2-regular subgraph of C is connected per component); this is needed because C-degree 0 or 2 alone does not preclude a disconnected union of 2-regular pieces, which is fine. Actually a 2-regular subgraph (every vertex degree 0 or 2 in C) is already a vertex-disjoint union of cycles + isolated vertices; the check is redundant-but-correct.

### 9. `scripts/full_replacement_sweep.py`

**Nothing flagged on the classifier.** `classify_trace_set` (lines 121–142) correctly:
- builds `side_key = trace_set_key(traces)`;
- finds the smallest-by-(min_order, trace_count) absorbing class (`absorbing_class`, lines 98–104);
- tests compatibility-universality against `universe = union_of_all_traces(payload)`;
- returns status `trace_contained | compat_universal_not_contained | neither`.

The status logic is correct: `trace_contained` is checked first (since it's the "strongest" reduction), then `compat_universal_not_contained` (Lemma 3.13 fallback), then `neither`.

**NIT (full_replacement_sweep.py:259–287, fast path).** The C0 early-termination optimisation is **correct but subtle**: it relies on C0_TRACES (lines 48–52) being closed under port-swap, which it is (every member's reverse is in the set). So `realises_target_traces(G, base_ports, C0_TRACES)` returning True at one orientation implies True at the other. **A comment that this only works because of the port-swap symmetry of C0_TRACES would help future maintainers.** When the fast path triggers, the record's `is_compatibility_universal` is set to `null`/`None` (line 266), which means downstream summary statistics about compatibility-universality undercount the C0-absorbed sides; the doc says this is acceptable since absorption suffices, and it is, but a reader of the JSONL should not interpret `is_compatibility_universal: null` as "false".

### 10. `data/n14_full.summary.json` and the n=14 sweep

**Verified.** Independent recount of `data/n14_full.jsonl` (one record per `python3 -c "..."` iteration) gives exactly:

```
status: {'trace_contained': 15176, 'compat_universal_not_contained': 2, 'neither': 0}
struct: {'non_port_2cut': 6688, 'essentially_3conn': 7120, 'bridge': 1370}
absorb: [('C0', 10474), ('C6', 3248), ('C8', 768), ('C7', 296), ('C2', 124),
         ('C3', 104), ('C4', 104), ('C22', 26), ('C5', 26), ('C23', 6)]
```

These are *bitwise* matches to `data/n14_full.summary.json` and to README claims. The 2 compat_universal_not_contained records are both orientations of the bridge graph `M??CB?W` + ``cKKGF?WG?``; I independently:
- confirmed it has 14 vertices, degree-2 vertices {3,4}, bridges {(5,12), (8,13)};
- confirmed removing (5,12) gives zero-port component {0,5,6,9,10} (no port) and removing (8,13) gives zero-port component {1,2,7,11,13} (no port);
- confirmed Trace(H,[3,4]) = 5 traces, of which the 5 cover all 4 axes (TT_joined via (T_T,T_TM) pi=join; TT_split via (T_TM,T_TM) pi=split; TM via (T_TM,M_TT) pi={{0}}; MT via (M_TT,T_TM) pi={{1}}).

The doc's claim (§3.18, lines 1102–1109) that this side is excluded by Lemma 3.9 Case 1 (zero-port component on bridge removal ⇒ bridge of G in a bridgeless supergraph) is correct: in a bridgeless cubic supergraph G, the side's bridge (5,12) joined to the rest of G via the boundary edges at ports 3,4 cannot itself be a G-bridge if and only if the zero-port component re-attaches via something else — but it doesn't, the only attachment is via the bridge itself. So Lemma 3.9 Case 1 closes this side via bridgelessness, exactly as the doc says. **Solid.**

### 11. Tests in `tests/test_decomposition.py`

**Nothing flagged on substance.** The 33 tests cover:
- brute-force finder on K_4, K_{3,3}, prism, Petersen (lines 35–73);
- verifier rejecting an invalid decomposition (lines 93–106);
- vertex-type identity sanity (lines 232–249);
- 2-pole trace consistency (π-block subset of {0,1}, π-incidence-vs-state, allowed π signatures): lines 273–306;
- gadget lattice / coverage / replacement (lines 372–456);
- Class-III residual compatibility-universal check (lines 459–501);
- compatibility-universality payload counts (lines 504–525, exactly cross-checking `axis_characterisation_agreement_count = 59`, `min_universal_trace_count = 4`, `smallest_universal_class = C5`, etc.).

These are **substantive** tests, not tautological. The Class-III test (line 459 ff.) hard-codes the 16-trace universe and the 12-trace residual set and checks the compatibility-universal property by direct enumeration — this is a real witness to the §3.12 claim.

**NIT (tests/test_decomposition.py:108–151).** The `test_K33_hamilton_cycle_plus_matching` test contains an unusually long comment trace through several false-start decompositions of K_{3,3} before settling on the correct one. It works, but the comment is misleading — the test only exercises the final partition. Cosmetic.

**MINOR (tests/test_decomposition.py:441–448).** `test_replacement_K4_minus_edge_not_strictly_replaceable` checks that K_4 − e is not strictly replaceable in the n≤8 lattice (it would have to be replaced by a smaller gadget, but K_4 − e is the smallest 2-pole). This is a correctness assertion about the lattice, not a regression test that catches future bugs in `compute_trace_set_2pole`. The test passes for the **right reason** here, but a stronger version would check that K_4 − e *is* in class C0 of the lattice.

### 12. Cross-cutting concerns

**Reproducibility (docs/reproducibility.md):** The pipeline is reproducible: SHA-256 of `data/n14_full.summary.json` is recorded; the `verify_n14_summary.py` script independently recomputes the headline statistics from the raw JSONL. I ran `verify_n14_summary.py` and it returns OK. The `gadget_lattice_2pole_n12_both.jsonl` checkpoint is excluded from the commit but the JSON build artefact is committed. **One mild concern**: the `gadget_lattice_2pole_n12_both.json` is a 700 KB committed artefact whose SHA is documented (`036eb628…`); if it were ever regenerated with a different ordering of internal IDs (e.g., class names C0..C132), every downstream artefact referencing class names would silently break. The codebase doesn't pin class names by structure-hash; this is a robustness concern (MINOR), not a correctness error.

**Compatibility-universal "universe" hygiene:** The implementation of `is_compatibility_universal` uses `universe = union_of_all_traces(payload)`. I verified that `len(universe) == 16` for both `gadget_lattice_2pole_n10_both.json` and `gadget_lattice_2pole_n12_both.json`, and that the two universes are *equal as sets*. So in practice, the lattice universe = the theoretical 16-trace universe. **But the codebase doesn't assert this**, so a future user who runs against a partial/corrupted lattice could get silent under-checks. **Recommendation:** in `full_replacement_sweep.py` or `compatibility_universality.py`, add `assert len(universe) == 16` with a comment pointing to `trace_feasibility.py`.

---

## Things I could not verify from the artefacts alone

1. **External citations** (plan.md:139, 141–151, 232–249): I did not access ScienceDirect / EJC / arXiv to verify the cited theorems are exactly as stated for the named classes. The doc itself flags one (Hamiltonian cubic, Akbari et al.) as "to be verified". The other citations are plausible and consistent with cross-references I have seen in the field. **The reviewer of this review should not treat the citations as audited.**

2. **Aboomahigir–Ahanjideh–Akbari coverage of Sub-lemma 1′:** the doc says (minimal_counterexample.md:181–184) "whether their statements directly cover both port states {T_T, T_TM} needs to be matched edge-by-edge (Phase 1 audit)". This is properly labelled as not yet done.

3. **Whether the n=14 sweep terminated cleanly across all 8 shards:** the log files `data/n14_all.shard{0..7}.log` exist; I did not inspect each, but the per-shard JSONL byte counts (~290 KB each, see `ls -la data/n14_all.shard*.jsonl`) and the final unified `data/n14_full.jsonl` totaling 15178 records are consistent with `15178 / 8 ≈ 1897` records per shard. No `neither` records appeared in any shard.

4. **The 14 essentially-3-connected n=14 exceptions** (`data/n14_essentially_3conn_C0_exceptions.json`, 7 unoriented graphs absorbed by C2 or C5): the doc claims (minimal_counterexample.md:1277–1282) that every exception misses *exactly* the single C0 trace (T_{TM}, T_{TM})-joined and realises both M-axis traces. I spot-checked one entry (`M??CB?WDU_OoI_PG?` ports (2,4), absorbing class C5, trace count 12) and the trace count is consistent, but I did not enumerate all 14 to confirm the "same missing trace" claim. **This is the kind of pattern that, if it fails on one exception, breaks the refined Lemma C in §3.21.** A unit test pinning this property would be valuable.

5. **The `lemma_C_proof_seed.md` swap mechanism arguments:** the doc itself says (line 218–237) that the simple-swap mechanism fails on 4 of 7 exception graphs; Lemma C is correctly labelled "open". I did not re-derive the swap construction; the empirical table (line 209–215) is self-checking on `/tmp/test_swap_mechanism.py` per the doc, which I have not run.

---

## What I am confident about

- **The 3-decomposition verifier (`verify_decomposition`) is correct.** This is the trust root for the rest of the pipeline. I read it line-by-line and ran it on K_4, K_{3,3}, prism, Petersen.
- **Lemma 1 (bridge reduction) is a correct natural-language proof**, modulo Sub-lemma 1′.
- **Lemma 3.9 (minimal essential 2-edge-cut side has no Case-1/Case-2b bridge) is a correct proof.** The case analysis is exhaustive and each case is a clean small argument.
- **Theorem 3.14 (compatibility-universal ⇔ four axes) is correct,** and matches the implementation in `compatibility_universality.py`. The 59/59 lattice agreement is reproducible.
- **The 16-trace theorem (§3.4 / `trace_feasibility.py`) is correct**: 16 realised + 8 (C-cycle cannot close) + 6 (no T-stub for internal) + 4 (T_CC in shared block) = 34 a-priori traces.
- **The n=12 Antichain Coverage refutation is solid:** 10 oriented sides spread across 5 distinct trace classes; the 4 "common obstruction" missing traces are correctly identified.
- **The n=14 sweep numbers reproduce exactly** on independent recount of the JSONL.
- **The compatibility replacement Lemma 3.13** is correct under the (verified) condition that the lattice universe equals the theoretical 16-trace U.
- **The tests are substantive**, not tautological.
- **The docs are self-aware:** every "target" lemma is labelled, every empirical-only claim is qualified, and the gap between "n=14 evidence" and "all-orders theorem" is clearly stated.

What I am **not** confident about (because it is open in the doc):
- the **Universal Replacement Conjecture / Core Absorption Lemma** at all orders ≥ 16;
- the **all-orders Sub-lemma 1′** (only checked through n=11);
- **Lemma B** (non-port 2-vertex-cut reduction);
- **Lemma C** (the essentially-3-connected dichotomy at all orders).

These are correctly labelled in the doc, and closing any of them would be a real mathematical contribution; the workstream is positioned to incorporate such a contribution but does not yet have one.

---

## Summary table of findings by severity

| Severity | Count | Topics |
|---|---:|---|
| CRITICAL | 1 | §3.13 quantifier ambiguity ↔ lattice-universe ≠ theoretical-universe robustness |
| MAJOR | 3 | README framing of Sub-lemma 1′ as "proved"; §3.13 universe dependence; replacement-direction inclusion (resolved by good engineering) |
| MINOR | 9 | Citation audit not done; README slightly bullish on Universal Replacement Conjecture; classIII_absorber_check.py unused variable; etc. |
| NIT | 6 | Documentation small typos and cosmetic issues |

No CRITICAL finding represents an actual mathematical *error*; the CRITICAL flag is for a robustness/quantifier issue that, while currently harmless because the lattice universe coincides with the theoretical universe, could silently break if the lattice changes. A one-line assertion would close it.

**Bottom line: the workstream is mathematically honest, technically careful, and the load-bearing proofs that are claimed proved are in fact correct. The remaining gap to "minimal counterexample is 3-edge-connected" is one open conjecture (Universal Replacement / Core Absorption), correctly labelled as such throughout the documentation.**
