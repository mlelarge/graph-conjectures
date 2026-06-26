# Chen-Chvatal lines + bridges (Conjecture 2.2) — STATUS

Mirror of ledger.json. Updated 2026-06-05 (Round 5).

## Central question
Is the set of connected, pendant-free BAD graphs (ell(G)+br(G) < |G|, ell = # metric-betweenness
lines, br = # bridges) FINITE and equal to the explicit F_0 of Figs 1-3 (12 graphs)? Equivalently:
does the pendant-free bad set stabilise? (The no-pendant variant is KNOWN FALSE — long-bridge
substitution gives infinitely many.)

## Where open_crux stands
- **Part (a) disproof-witness search**: exhausted through n=10 (9,808,209 pendant-free, 0 bad;
  |bad|=12=|F_0|, confined to n in {4,5,6,8}). n=11 full sweep launched, not yet completed.
- **Part (b') = H5** ("pendant-free + diam>=4 => ell>=n"): SOLE live structural lever. The
  **explicit subset-of-lines line-counting axis is now EXHAUSTED** — FOUR charging mechanisms
  barred: diametral-pairs, spine (G3), pencil/bipencil (G5), and Round-5 pair-indexed /
  shell×shell (G8). No subset-of-lines functional reaches >=n on all diam>=4 pendant-free n<=9.
  Genuine near-misses **far_ge2** (floor -1/0) and **f_far2** (floor -1/-2) miss n by exactly 1 —
  symbolic targets, not functionals.

## Live hypotheses
- **H1** F_0 = the 12 graphs; no bad graph of order >=9. — open-supported (n<=10 clean).
- **H3** every bad graph is bridgeless (br=0). — open-supported (all 12 have br=0).
- **H4** every bad graph has diam<=3. — open-supported (all diam in {2,3}; diam>=4 clean n<=10).
- **H5** pendant-free + diam>=4 => ell>=n. — open; explicit line-counting axis EXHAUSTED (4 barred).
- **H6/H7** pencil (G5) / pair-indexed (G8) charges — DEAD.
- **H8** (NEW) structural/induction (peeling) route: delete a peripheral vertex, track exact
  ell-delta, recover >=1 fresh line per vertex; O(1) deficit suggests it closes. — needs-spec.
- **H9** (NEW) pendant-free + diam>=4 => twin-free (verified n<=10). — supported but INERT for H5.

## Last 2 decisions
- **D4** (R4): barred peripheral-pencil/bipencil charge (G5) — 3rd H5 mechanism; redirected to pair-indexed.
- **D5** (R5): barred pair-indexed/shell×shell charge (G8) — 4th mechanism, CLOSES the explicit
  line-counting axis. Three other proposals refuted by their own oracle gates: margin-floor
  non-monotone M(8,9,10)=1,2,1 (G9); F_far<n on 4 n=10 graphs (G10); twin-free split inert (G11).
  Residual H5 route is now structural-induction (H8) or a far_ge2-deficit symbolic argument.

## needs_human / recommend_handback
- needs_human: null.
- recommend_handback: not yet — H8 (structural-induction) and the far_ge2 single-line-deficit
  symbolic argument are untried; H3/H4 direct attacks also open. The explicit-functional axis is
  exhausted, but a non-counting route remains. If H8 also yields no exact ell-recursion, the next
  step is genuine human math input (an inductive line-creation lemma).
