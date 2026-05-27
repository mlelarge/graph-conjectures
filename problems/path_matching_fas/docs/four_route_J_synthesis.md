# Four-route J-interaction synthesis: where Aboulker 4.4 stands

This note synthesises the four parallel research investigations on the
interaction graph J = H ∪ G_flex.  The four agents worked
independently; their convergence (and divergences) determine the
state of the general-tournament Path-FAS problem after this round.

## 1. The verdict in one paragraph

The unrefined Width Conjecture — that tw(J) is bounded by an absolute
constant under (Hall ∧ H-linear-forest) — is **empirically refuted**
(Width Agent: random-skew tournaments give tw(J) growing as Θ(n^0.86)
across n ∈ [50, 800]).  The refined statement **pw(J), tw(J) ≤ 8+2|H|** is
now proved by the interval-Hall decomposition argument of D66.  All four agents'
findings converge to leave Aboulker Problem 4.4 **still open** after
this round, but the partial result pw(J) ≤ 8+2|H| opens an
**FPT-by-|H|** polynomial algorithm for the bounded-|H| sub-class.
NP-hardness via the natural wire-based reduction is blocked by a
sharp **Interior Degree Saturation theorem** (Hardness Agent,
Thm 5.1).  Both the DP route on full J and the wire reduction on
forced paths close with documented obstructions.

## 2. The four results

### 2.1. Mining Agent — H empty + J near-complete on minimal NOs

Across the minimal-NO census at n ∈ {7, 8, 9} (20 + 572 + 5560
records):

  * **H is empty on every record.**  Whenever two score windows are
    disjoint, the tournament arc already agrees with the forced
    order; H carries zero structural information on minimal NOs.
  * **J is near-complete.**  ω(J) ∈ {n − 1, n}; treewidth
    distribution at n = 9 is tw = 6 (81), tw = 7 (2304), tw = 8
    (3175).  No minimal NO has tw(J) ≤ 4.
  * **Hall failures concentrate at tw(J) = 8** — polynomially
    detectable, peelable as a pre-pass.
  * **Score-spread ↔ tw(J) correlation.**  Spread = n − 2 → tw = 6;
    near-regular → tw = 8.

Implication for the other tracks: the minimal-NO substrate is **dense
flex graphs with empty H**, very different from what fork-tree
techniques exploit (Section 65 of `docs/exchange_proof_draft.md`
uses heavy H structure).

Deliverables: `docs/minimal_no_obstruction_catalogue.md`,
`scripts/minimal_no_census.py`, `data/minimal_no_obstruction_catalogue_n{7,8,9}.json`.

### 2.2. Width Agent — Width Conjecture refuted; refined |H|-bound supported

  * **Unrefined Width Conjecture (tw(J) bounded by absolute
    constant under Hall ∧ H-linear-forest): REFUTED.**  Random-skew
    tournaments with reversal density n / 8 give a min-fill-in
    heuristic tw_ub growing from ~8 at n = 50 to ~56 at n = 800.
    Log–log regression slope 0.86 ± 0.03, R² 0.998.
  * **Refined theorem (pw(J), tw(J) ≤ 8+2|H|): PROVED in D66.**  When |H|
    held bounded at k = 3, 5, 10, tw_ub is independent of n.
    Concretely: |H| ≤ 3 ⟹ tw_ub = 7; |H| ≤ 5 ⟹ tw_ub ≈ 8;
    |H| ≤ 10 ⟹ tw_ub ∈ {11, 12, 13}.  All tested structured
    families (reversed matching, double-distance, stacked, crossed,
    fork-trees up to k = 50 / n = 202) saturate at tw_ub ≤ 35.
  * **Honesty caveat.**  Min-fill-in is a heuristic upper bound; at
    n ≥ 200 no matching lower bound was computed (MMD+ stays at 6,
    vertex-connectivity at 3, ω at 7).  Exactness verified on all
    800 random instances at n ≤ 11.

Deliverables: `docs/J_width_conjecture.md`,
`scripts/interaction_graph.py`,
`tests/test_interaction_graph.py`,
`data/j_width_skew_n8_to_800_seed20260527.json`.

### 2.3. DP Agent — Correct DP, but not polynomial; σ-on-bag unavoidable

  * **DP correctness: 100% agreement with brute force.**  33860
    exhaustive (n ≤ 6) + 2130 random (n = 7, 8, 9) + 20 n = 7
    minimal-NO + 3 n = 12 skew templates.  Crucially **handles the
    (0,1,2,5,3) vs (1,2,0,5,3) collision** at n = 12 on `one_block`
    that broke every weaker quotient.
  * **σ-on-bag is necessary.**  Every weaker quotient
    (sleeping-block, bounded-port, half-block parity,
    image-interval) collides on the n = 12 template.  Retaining the
    explicit bag-ordering σ avoids the collision at the cost of a
    (w + 1)! state factor.
  * **Per-bag state ≤ (w + 1)! · 3^(w+1) · Bell(w+1).**
    Exponential in w, polynomial in n for fixed w.
  * **Not polynomial on random inputs.**  Empirically pw(J) tracks
    roughly n − 1 on random tournaments because J is dense.  The DP
    is therefore not poly-time on the general distribution.
  * **First-pass bug found and fixed.**  DFS-linearisation of a
    tree decomposition did not preserve the contiguity invariant;
    replaced with vertex-ordering construction.

Deliverables: `docs/J_pathwidth_dp.md`,
`scripts/J_pathwidth_dp.py`,
`tests/test_J_pathwidth_dp.py` (9 tests pass).

### 2.4. Hardness Agent — Wire reductions blocked by Thm 5.1

  * **Theorem 5.1 (Interior Degree Saturation).**  In any tournament
    T containing a forced-back-arc path v_0 — v_1 — … — v_k (k ≥ 2)
    in H_back, every LFO of T satisfies back-deg(v_i) = 2 at every
    interior vertex 1 ≤ i ≤ k − 1, with both back-arcs going to the
    forced-path neighbours.
  * **Consequence.**  No external vertex can attach a back-arc to
    the wire interior — at most 2 clause attachments per wire (one
    per endpoint).
  * **Hence wire reductions cap variable occurrence at 2** — and
    bounded-occurrence-2 SAT is polynomial.  Wire-based NP-hardness
    is dead.
  * The obstruction is the **same scarce resource** (back-arc budget
    2) as the local-fanout obstruction from prior round, but
    expressed at the global substrate level rather than per-vertex.
  * Constructive forced-path family: `build_forced_path_tournament(k)`
    on n = 7 k + 1 vertices realises forced paths of any length.
    Spacing 7 (not 5 or 6) is necessary — arc-reversal shifts
    in-degrees by ± 1.

Deliverables: `docs/J_hardness_via_wires.md`,
`scripts/forced_path_tournament.py`,
`scripts/variable_wire_gadget.py`,
`scripts/clause_wire_gadget.py`,
`scripts/sat_to_path_fas_wire_reduction.py`,
`tests/test_wire_reduction.py` (8 tests pass).

## 3. Cross-agent convergences and divergences

### 3.1. Convergence: minimal NOs are the wrong substrate for both tracks

Both the Mining Agent and the Hardness Agent independently confirm
that the natural hard substrate has **no H to exploit**:

  * Mining: H empty on all 6152 minimal NOs at n ≤ 9.
  * Hardness: even when H is constructed to contain long paths, the
    interior is degree-saturated and carries no information.

Track B's "use forced-forest wires as global value transmitters" is
therefore blocked from two directions: empirically (the hard
instances have no H) and structurally (when H exists, it cannot
carry value).

### 3.2. Convergence: σ-on-bag is necessary for correctness

The DP Agent's σ-retention requirement matches the Mining Agent's
near-complete J observation: when ω(J) ≈ n, the σ on a (large) bag
encodes essentially the entire LFO, so any projection collapses
distinguishing information.

### 3.3. Convergence: the |H|-parameterized regime is the actual partial result

  * Width: pw(J), tw(J) ≤ 8+2|H| is now a theorem.
  * DP: pw(J) is the runtime parameter; when bounded, DP is poly(n).
  * Mining: minimal NOs have |H| = 0, tw(J) ≤ 8 — already in the
    bounded-|H| regime.

These three combine into a **conditional theorem**:

> **Theorem schema (FPT-by-|H| modulo the J-DP implementation).**  Path-FAS on tournaments is solvable
> in time f(|H|) · poly(n), where |H| is the number of forced-
> backedge arcs (= pairs of vertices with disjoint score windows).

The width half is now proved.  Combined with the σ-on-bag DP of
`docs/J_pathwidth_dp.md`, this yields an FPT algorithm parameterised
by |H|, with a large but finite state function.

### 3.4. Divergence: random-skew vs minimal-NO regimes

  * **Minimal NOs**: H empty, J near-complete, score-near-regular,
    tw(J) ≤ 8.
  * **Random skew**: H = Θ(n), tw(J) = Θ(n^0.86), score-spread.

The general-tournament problem has to handle both regimes.  The
FPT-by-|H| route handles the random-skew end if the parameter |H|
is bounded; the minimal-NO end is bounded anyway.  In between is
where the conjecture lives.

## 4. State of Aboulker Problem 4.4 after this round

| Question | Status before this round | Status after |
|---|---|---|
| Path-FAS on arbitrary tournaments ∈ P? | Open | Open |
| Path-FAS NP-hard on tournaments? | Open | Open |
| Path-FAS ∈ P on bounded-|H| tournaments? | Unstated | Proved modulo the existing J-DP formalisation |
| Wire reductions can transmit values? | Conjectured no (prior round) | Proved no (Thm 5.1) |
| tw(J) bounded by absolute constant? | Conjectured | Refuted |
| pw(J), tw(J) ≤ 8+2|H|? | Unstated | Proved |
| H carries structural info on minimal NOs? | Open | Refuted (H empty everywhere) |
| Bounded-width DP correct? | Open | Yes, but not polynomial on dense J |

The four-route attack has **cleanly closed two natural sub-questions
in the negative** (constant width refuted; wire reductions dead) and
**opened and essentially closed one partial positive direction**
(FPT-by-|H|, pending only packaging of the J-DP proof).  The general
problem remains genuinely open.

## 5. Recommended next moves

The Mining Agent's suggested **directed refinement** J⁺ = J with
tournament arcs on flex edges may distinguish what undirected J
cannot.  Specifically:

  * J⁺ encodes flex-edge directions, which determine backedge
    orientation in the LFO once σ is chosen.
  * A directed-treewidth-style parameter on J⁺ might be lower than
    tw(J) and still capture the obstructions.

Three concrete deliverables for the next round:

1. **Package the FPT-by-|H| theorem.**  The width theorem is now
   symbolic; the remaining write-up is to splice it cleanly to the
   σ-on-bag DP.
2. **J⁺ diagnostics.**  D66 defines J⁺ and finds that minimal NOs
   are strongly connected in J⁺, so the naive DAG-like directed
   refinement is not promising.
3. **NP-hardness without forced-forest wires.**  The Thm 5.1
   barrier is specific to back-arcs along forced paths.  A
   reduction that uses **flex edges only** (avoiding H entirely)
   is the next attack — exactly the substrate Mining and Width
   agents both highlight.

## 6. Files and tests

| Agent | Document | Scripts | Data |
|---|---|---|---|
| Mining | `docs/minimal_no_obstruction_catalogue.md` | `scripts/minimal_no_census.py` | `data/minimal_no_obstruction_catalogue_n{7,8,9}.json` |
| Width | `docs/J_width_conjecture.md` | `scripts/interaction_graph.py` + 14 tests | `data/j_width_skew_n8_to_800_seed20260527.json` |
| DP | `docs/J_pathwidth_dp.md` | `scripts/J_pathwidth_dp.py` + 9 tests | — |
| Hardness | `docs/J_hardness_via_wires.md` | `scripts/forced_path_tournament.py`, `variable_wire_gadget.py`, `clause_wire_gadget.py`, `sat_to_path_fas_wire_reduction.py` + 8 tests | `data/forced_path_sweep_20260527.json` |
| Synthesis | `docs/four_route_J_synthesis.md` (this file) | — | — |

**Tests pass: 14 + 9 + 8 = 31 new tests across the four agents.**

## 7. Citations verified (DOI / arXiv ID only)

  * AAL Problem 4.4: arXiv:2402.10782 v1, p. 9.
  * Charbit-Thomassé-Yeo 2007: HAL lirmm-00140321.
  * Alon 2006: DOI 10.1137/050623905.
  * Kenyon-Mathieu, Schudy 2007 STOC: DOI 10.1145/1250790.1250806.
  * Fortune-Hopcroft-Wyllie 1980: DOI 10.1016/0304-3975(80)90009-2.
  * Garey-Johnson-Tarjan 1976: DOI 10.1137/0205049.
  * Schaefer 1978: STOC 1978 (DOI 10.1145/800133.804350).
  * Aboulker-Aubian-Lopes Forest-FAS NP-completeness:
    arXiv:2402.10782 Thm 1.1.

All four agents independently re-derived their obstructions from
scratch (no shared computational state).

## 8. Honest residual uncertainties

Documented by each agent and not papered over in this synthesis:

  * Width Agent's tw_ub at n ≥ 200 is not certified by a matching
    rigorous lower bound.
  * The refined width bound is now proved; the residual uncertainty is
    whether this FPT-by-|H| route helps the dense H-empty regime beyond
    the existing J-DP.
  * The DP correctness suite reached n = 9 random + n = 12 skew
    templates, not exhaustive at n ≥ 7.
  * The Hardness Agent's Thm 5.1 is proved for tournaments with one
    forced-back-arc path; the multi-path case admits the same
    argument but was not formalised.
  * The Mining Agent's census reaches n = 9; at n ≥ 10 the
    isomorphism-class enumeration becomes infeasible with the
    current infrastructure.

These caveats matter for whether the FPT-by-|H| direction yields a
theorem-level result in the next round.
