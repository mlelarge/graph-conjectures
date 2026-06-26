# STATUS — Conjecture 3.12 (bounded-tww tournaments are chiVec-bounded)

_Mirror of ledger.json. Updated 2026-06-06 (D6)._ Paper: arXiv:2310.04265.

## Central question
For fixed k, is the class {tww(T) <= k} chi-arrow-bounded — i.e. is there a binding function f
with chiVec(T) <= f(omegaVec(T))? Asymptotic existence claim; oracle cannot certify TRUE.
Seeded lean = DISPROVE (find a bounded-tww, bounded-omegaVec, growing-chiVec family).

## Where open_crux stands now (D6: computational levers at/near EXHAUSTION)
- DISPROVE side: closed at the floor. Beyond S_k=D_k (P5)/S~_m/R_k/non-C3 prime towers (G12), D6 showed
  the omega-lift lockstep survives even DIRECT two-vertex addition at n=11: all 36288 tww<=1 extensions
  of the 20 n=9 prime chi>omega seeds are chiVec<=3 (G15, landmark n11_local_extension_lockstep). Only a
  full n=11 tww<=1 omega<=2 census remains (compute-infeasible, structurally implausible).
- PROVE side: difficulty LOCATED (closure-OUTSIDE tww<=1, D4) and REACHING THE PRIMES (20 prime witnesses
  at n=9, D5). D6 KILLED the three concrete mechanisms that tried to convert this into a proof:
  - H10 structure-extraction SPENT (G14): the 20 primes' minimal chiVec=3 core is the FORCED size-8 cell
    (omega=2 forbids Paley P7, which has omega=3) and is itself a C3-substitution object Q6[C3] — NO new
    non-substitution prime invariant; chi>omega at the primes is the SAME C3-substitution mechanism.
  - Local-to-global induction (arXiv:1702.01607, REAL & correctly cited) PROVABLY does not close (G17):
    the universal lift f is strictly super-identity, no n-independent fixed point, oracle-PROVEN to
    compound +1/level on S_k. The 'delta=1' invariant is a vacuous constant; reduction is circular.
  - Linear amortized floor omega>=ceil((chi+1)/2) is asymptotically FALSE (G16): contradicts the proven
    omegaVec(D_n)>=log_9(n) tower — the true binding function on tww<=1 is LOGARITHMIC, not linear.
- BST/Conj-3.16 route is the load-bearing open quantity (bstOmega<=g(omegaVec)), no shortcut (G13);
  beta census is size-forced-vacuous below n=11 (G6/G7).

## Live hypotheses
- H1 SUPERSEDED (P5). H2 DEAD->G1. H3 SPENT<n=11 (G6). H4 DEAD->G2. H5 RESOLVED (log_9 internal, gate MET).
- H6 — finer-invariant recursion: SOLE SURVIVOR, but CONSTRAINED (D6) to: reproduces LOG omega-growth
  (not linear, G16), forced by C3-substitution branch structure (G14), NOT a naive out-nbhd lift (G17).
- H7 — Neumann-Lara floor (4-dichromatic => n>=11) hard disprove barrier.
- H8 — closure census RUN (difficulty closure-OUTSIDE tww<=1). H9 — beta lever RUN, size-forced-vacuous, SPENT.
- H10 — structure-extraction on the 20 n=9 primes: RUN and SPENT (forced core / substitution-built, G14).
- H11 — **NEW (D6)**: residual disprove = full n=11 tww<=1 omega<=2 census (local-extension route CLOSED, G15);
  compute-infeasible by naive gentourng; disprove side at the wall.

## Proved (oracle-verified)
P1 chiVec(S_k)=k (k<=5). P2 omegaVec(S_k)=1,2,2,3 (k<=4). P3 tww(S_k)=tww(S~_m)=1.
P4 omegaVec(S~_m)>=m. P5 S_k iso D_k (k=1..5; structural identity only). (No new entries — all D6 proposals refuted/failed.)

## Last decisions
- D5 — chi>omega reaches the PRIMES (20 witnesses at n=9, G11) + lockstep through non-C3 primes (G12); H9 SPENT; H10 spawned.
- D6 — ALL four refuted/failed; ONE new barrier (lockstep under direct vertex-addition at n=11, G15). PRIMARY lever
  H10 SPENT (forced/substitution-built core, G14); two PROVE routes closed with hard barriers (local-to-global no
  fixed point G17; linear floor false G16). Only constrained-H6 survives.

## needs_human / recommend_handback
needs_human: null.
recommend_handback: SET. The computational frontier is exhausted on all runnable levers — census, structure-
extraction, and explicit-construction routes are all spent inside the Neumann-Lara chiVec<=3 band, and the three
D6 proof-mechanisms are killed with hard barriers. What remains is HUMAN MATH the oracle cannot certify: supply a
finer invariant whose recursion reproduces the LOGARITHMIC omegaVec-growth and is forced by the C3-substitution
branch structure (constrained H6), OR prove Conj 3.16 (bstOmega<=g(omegaVec) on closure-outside tww<=1). Both are
asymptotic statements; no finite oracle computation can establish them.
