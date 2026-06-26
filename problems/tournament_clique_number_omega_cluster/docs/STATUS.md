# STATUS — tournament clique number / omega_vec-cluster (Q5.9 / Conj 5.10)

_D45 ledger mirror plus post-D45 corrections. Updated 2026-06-13.
`ledger.json` remains frozen as the historical D45 record._

## Iterated-triangle growth frontier
- For the canonical three first-difference posets of
  $B_k=\widetilde S_{k+1}$, let $q_c(\pi)$ be the maximum backward chain
  in layer $c$ and $L_k=\min_\pi q_0q_1q_2$.
- Rank triples give
  $\vec\chi(B_k)\le q_0q_1q_2\le K(\pi)^3$.
  The sequence $L_k$ is submultiplicative, so
  $\lambda=\lim L_k^{1/k}$ exists and
  $\rho^3\ge\lambda\ge3/2$.
- Exact SAT gives
  $L_1=2,L_2=4,L_3=8,L_4=15,\mathbf{L_5=24}$ (depth 5 added 2026-06-17, §11).
  At depth 3, $(q_0,q_1,q_2)=(2,2,2)$ is compatible with the optimal
  full clique $K=4$. At depth 4, a minimum-volume $(1,3,5)$ order has
  full clique $11$, while a known optimal $K=5$ order has layer profile
  $(5,5,5)$. The joint Pareto frontier, not either scalar alone, controls
  pod-tightness. **$\lambda\le 24^{1/5}=1.888$**; step ratio
  $L_k/L_{k-1}=2,2,1.875,1.6$ falls toward $3/2$.
- Chudnovsky--Cook--Davies--Kim--Oum (arXiv:2606.09415, June 8, 2026) prove
  that the exponent $d$ is exactly sharp for arbitrary unions of $d$
  comparability graphs. Any improvement here must use the tower's shared
  first-difference geometry.
- Current theoretical target: prove $\lambda>3/2$, or prove a Pareto
  separation between near-minimum layer volume and the full mixed-colour
  clique. See `docs/stilde_pod_tightness.md`.
- **2026-06-17 progress (`docs/stilde_pod_tightness.md` §7.1, §9).**
  (a) Entropy diagnostic on the SAT-optimal min-volume orders corroborates
  $\lambda\approx2$: $\log_2 M/k$ rises $0.936\to0.977$ toward $1$ (i.e.
  $\sim2^k$ fibres), not the $0.585$ pod-tightness needs.
  (b) Proved + exhaustively verified ($9!$ depth-2 orders) the **crossing
  recursion** (9.1) for $q_c$ under $B_k=C_3[B_{k-1}]$.
  (c) **Two scalar lower-bound routes refuted:** the cyclic crossing-sum
  obstruction (depth-4 optimum skews to $(1,3,5)$, kills all three
  crossings via $q_0=1$) and rank-cell amplification ($\min_\pi
  M(B_2)=\vec\chi(B_2)=3$, collapses to $\vec\chi$). $\lambda>3/2$ now
  reduced to the **profile-closure lemma** (prefix/suffix invariant);
  scalar invariants provably insufficient. $\lambda>3/2$ still open.
- **2026-06-17 first crack at profile closure (`docs/stilde_pod_tightness.md`
  §10).** Added `scripts/stilde_profile_closure.py` and
  `tests/test_stilde_profile_closure.py`. The closure state is now exact:
  three module orders plus a monotone path in `{0..3^(k-1)}^3`, with forbidden
  states given by the suffix+prefix inequalities (10.1). Tests verify the
  formula against direct `q_c` and recover `L_1=2,L_2=4`; all 15 stilde tests
  pass. Depth-2 already has 131,046 distinct full staircase profiles, so the
  next step is dominance/Pareto compression of the two relevant staircases per
  labelled module, not raw profile triple enumeration.
- **2026-06-17 depth-5 frontier + cake refutation + $\lambda$ correction
  (`docs/stilde_pod_tightness.md` §11; corrected §5.1/§7.1/§9.4).** New
  **level-labeling SAT** (`scripts/decide_layer_labeling.py`, +lazy CEGAR
  `decide_layer_lazy.py`, tests `test_decide_layer_labeling.py`) bounds
  $\mathrm{height}(Q_c)\le\mathrm{cap}$ via thermometer level vars instead of
  chain enumeration — cracks the depth-5 frontier the old encoding could not
  reach. Rigorous scan (`scripts/run_L5_scan.py`): **$L_5=24$ exact** (all
  product-$\le23$ UNSAT; $(2,3,4)$ SAT). (a) **Cake refuted:** $2,4,8,15$ are the
  cake numbers (OEIS A000125) but that is a 4-point coincidence — cake$(5)=26$
  and a rival cubic $2^k-\binom{k-1}3$ predict 26/28, both killed by $L_5=24$.
  (b) **$\lambda$ corrected:** $\lambda\le1.888$; the prior "$\lambda\approx2$"
  (§5.1/§7.1) was the rising flank of a pre-asymptotic transient and is
  retracted; step ratio falls to 1.6, evidence now **leans toward $\lambda=3/2$
  (pod-tight)**, opposite the old reading. (c) **Lit (workflow-verified):** the
  growth constant $\rho/\lambda$ is NOT known anywhere; published = one-sided
  $\rho\ge(3/2)^{1/3}$ (2606.07748); 2310.04265 flags the gap open. Also proved
  the cyclic automorphism $\sigma(w)=w+\mathbf1\bmod3$ (colour shift) ⇒ cap
  feasibility is cyclic-rotation invariant. Depth 6 OUT OF REACH for current
  methods ($L_6\in[18,48]$ from submultiplicativity only): eager labeling needs
  $1.3\times10^8$ clauses; lazy CEGAR does not converge (5 triples, products
  24–40, each 290–2120 rounds, all timed out $>1200$s). $L_6$ needs
  symmetry-breaking or a positional order encoding.
- **2026-06-17 first L6 encoding improvement (`docs/stilde_pod_tightness.md`
  §11.7).** Added `scripts/decide_layer_positional.py`: binary key per vertex,
  order by `(key, vertex_id)`, same level-labeling height constraints. This is
  equisatisfiable with a total-order search (ties are real id tie-breaks; every
  total order has distinct-key representation) and replaces $O(n^3)$
  transitivity by $O(n^2\log n)$ comparator clauses. Cross-checks pass against
  eager labeling on depths 2,3 and the depth-4 frontier; 20 stilde/SAT tests
  pass. Depth-6 `(3,3,4)` now builds as 2,665,954 vars / 16,278,085 clauses
  instead of 1.3e8 triangle clauses. A bounded solve still did not return within
  one minute, so $L_6$ remains unknown; next layer is symmetry/domain constraints
  and solver tuning on top of binary-key encoding.
- **2026-06-17 binary-key domain constraints (`docs/stilde_pod_tightness.md`
  §11.9).** Added `--range-keys` and `--distinct-keys` to
  `decide_layer_positional.py`. Soundness: every total order has a distinct
  rank representation in `0..n-1`, so these remove redundant key assignments
  (ties/gaps), not orders. Cross-checks with both flags match eager labeling on
  selected depth-2/3 SAT/UNSAT cases; encoding tests pass. Depth-6 `(3,3,4)`
  sizes: range-only 2,665,954 vars / 16,281,001 clauses; permutation-rank mode
  6,204,034 vars / 37,067,221 clauses. Depth-5 `(2,3,4)` permutation-rank mode
  builds but did not solve within a 90s foreground run, so this is a sound
  long-run variant, not a bracket improvement. $L_6\in[18,48]$ still.
- **2026-06-17 profile-closure DP: decision compresses, generation does NOT
  (`docs/stilde_pod_tightness.md` §12; `scripts/stilde_profile_dp.py`,
  `tests/test_stilde_profile_dp.py`).** Built and tested the §10.2 Pareto DP.
  DECISION side works: $131{,}046$ full $B_2$ profiles → **16 per-label
  Pareto-minimal** (uniform 16/16/16 by $\sigma$); decision over $16^3$ (vs naive
  $131\text{k}^3$) **reproduces $L_3=8$ instantly, no SAT**. GENERATION side fails:
  the grid path-DP frontier for $B_2\to B_3$ is the **full interleaving count**
  ($1,2,6,\dots,1680{=}\binom9{3,3,3},4200,11550,\dots$) — ZERO compression,
  because partial states can't be soundly Pareto-dominated (prefix/suffix
  staircases are order-dependent, not rank-determined). KEY UNIFICATION: this is
  the SAME wall as §9.4 — the profile is not closed under interleaving, so $L_6$
  resists compressed-profile computation for the same reason $\lambda>3/2$ resists
  a closed-invariant proof. CONSEQUENCE: profile DP is NOT a cheaper $L_6$ route
  (it re-derives SAT's exponential search); positional SAT (§11.7) stays the only
  exact route; profile DP is best kept as the decision/reasoning tool (16-frontier
  makes feasibility checks instant). $L_6\in[18,48]$ still.
- **2026-06-18 final $L_6$ SAT verdict — beyond practical SAT (§11.8/§11.10;
  `scripts/run_L6_walltime.py`).** Symmetry settled: $\mathrm{Aut}(B_k)=C_3$
  (computed; colour-preserving subgroup trivial), so within-instance symmetry
  breaking is unavailable for skewed caps — only $\sigma$ cyclic-dedup of the cap
  scan helps. Wall-clock parallel map (14 workers, 5-min `killpg` timeout, conf
  budgets useless: 3M conflicts $\approx2$h/instance) over all 104 cyclic-rep
  triples product $[28,48]$: **SAT 0, UNSAT 21, TIMEOUT 83**. Every balanced
  triple times out (longer runs: 30–120 min each, often UNKNOWN); no SAT. **No
  bracket improvement: $L_6\in[18,48]$ stands.** All routes now exhausted (eager,
  CEGAR, positional, key-domain, symmetry, profile-DP). Clean byproduct: $(1,1,X)$
  UNSAT for all $X\le48$ ⇒ likely lemma "two backward-free colours force the third
  $=2^k$" (strengthens §11.5 to all orders). $\lambda\in[3/2,1.888]$ unaffected.
- **2026-06-18 one-sided analytic bound nailed (§11.10;
  `scripts/stilde_two_free_lemma.py`, `tests/test_stilde_two_free_lemma.py`).**
  Proved the two-free-colours lemma: if two colours are backward-free
  ($q_a=q_b=1$), the missing colour has $q_c=2^k$. WLOG free colours 0,1 force
  the order to refine lex digit order $0<1<2$; the $\{0,2\}^k$ subcube is then a
  reversed colour-2 chain of size $2^k$. This exactly explains the $(1,1,X)$
  UNSAT face and is the first clean one-sided obstruction, but it does not touch
  balanced caps.
- **2026-06-18 closed-invariant probe (`docs/stilde_pod_tightness.md` §13;
  `scripts/stilde_interval_profiles.py`, `tests/test_stilde_interval_profiles.py`).**
  Found the exact closure repair: full interval profiles
  $I_c(i,j)=\mathrm{height}\,Q_c(\pi[i,j))$. They strictly contain prefix/suffix
  profiles and satisfy the interval crossing formula (13.1); tests verify exact
  recovery of prefix/suffix and closure against direct computation. Verdict:
  closed but too large. Random $B_2$ samples have almost no compression
  (4,871 distinct interval profiles in 5,000 orders; 18,212 in 20,000). The next
  theoretical target is therefore a quotient of the interval profile, not the
  raw interval profile itself.
- **2026-06-18 quotient probe (`docs/stilde_pod_tightness.md` §14;
  `scripts/stilde_interval_quotients.py`, `tests/test_stilde_interval_quotients.py`).**
  Cap-truncated interval profiles
  $J_c(i,j)=\min(I_c(i,j),h_c+1)$ are closed and verified, but still barely
  compress random $B_2$ orders (20k samples: 16,414 distinct even for caps
  `(1,1,1)`, and 18,212 for `(2,2,2)`, `(2,3,4)`, `(3,3,4)`). Proved the
  interval isolation lemma: any differing child interval entry can be isolated
  as the far module in a one-level parent context, so no smaller quotient can
  preserve exact interval-profile generation. Next target must preserve only
  final cap-decision inequalities or prove lower-bound obstructions, not exact
  generated profiles.
- **2026-06-18 dominance (lossy) compression also fails (§14.1).** The isolation
  lemma closes *exact* quotients; tested the remaining *lossy* escape: since
  $L_k=\min$ and the interval closure (13.1) is monotone ($\max/\min/+$),
  Pareto-minimal parents come only from Pareto-minimal children, so carrying
  Pareto-minimal interval profiles would suffice — and is NOT forbidden by the
  isolation lemma. **But the Pareto-minimal frontier is large**: on $B_2$ samples
  it grows $322\to614\to973$ (500/1500/3000 samples, full $I$) and stays $\ge613$
  even for cap-trunc $J$ at $(1,1,1)$. SHARPENED DICHOTOMY: the only *closed*
  object (interval profile) is intrinsically $\sim35$-dim (bad-span antichain) ⇒
  large Pareto frontier; the only *small-frontier* object (16 per-label
  projection) is not closed (isolation lemma). **No object is both closed and
  small-frontier, exact OR up to dominance** ⇒ the recursive-DP route to $L_6$/the
  $\lambda$ dichotomy is closed in every form. What survives: a one-sided
  *bounding* DP, or a direct analytic $\lambda$ argument not routing through
  profile generation. The computational mapping is complete; the dichotomy is now
  purely analytic.
- **2026-06-18 cleaner pod-tightness reduction: the $q_0=1$ face (§15;
  `scripts/stilde_q0_face.py`, `tests/test_stilde_q0_face.py`).** Define
  $F_k=\min\{q_1q_2:q_0=1\}$ (orders extending $P_0$). PROVED: $L_k\le F_k$, $F$
  submultiplicative ⇒ $\lambda_F=\lim F_k^{1/k}$ exists, and **$\lambda_F=3/2\Rightarrow
  \lambda=3/2$ (pod-tight)**. Exact $F_1{:}5=2,4,8,15,\mathbf{25}$ ($=L_k$ for
  $k\le4$; $F_5=25$ via $(1,5,5)$ vs off-face $L_5=24$). The data is consistent
  with pod-tightness but does **not** pin it: §16 corrected the earlier optimistic
  read, since $F_k/2^k=1,1,1,.94,.78$ also extrapolates naturally to
  $\lambda_F\approx1.66$. The face is a genuine 2-objective problem
  ($M_0$ before $M_1$, only $M_2$ floats): its frontier is SMALL at $B_2$ (53
  exhaustive, 6 height-pairs) but BLOWS UP at $B_3$ ($\ge1528$), so a face-DP can't
  reach $F_6$ either. STRUCTURE: depth-4 optimum $= M_0(1,3,3)\,/\,M_1(1,2,5)\,/\,
  M_2(1,3,5\,\text{self-similar, split})$ ⇒ parent $(1,q_1(M_0),q_2(M_1))$.
  Pod-tightness now reduces to a concrete construction: $q_0=1$ orders with
  $q_1q_2=(3/2)^{k+o(k)}$ via complementary $M_0,M_1$ + self-similar split $M_2$ —
  the most attackable open form reached.
- **2026-06-18 construction attempt — structure decoded, but does NOT close
  (§16; `scripts/stilde_face_construction.py`, `tests/test_stilde_face_construction.py`).**
  Decoded the exact face-optimum recursion (consistent $F_4,F_5$): parent $(1,A,B)=
  M_0(1,A,b_0)\,|\,M_1(1,a_1,B)$, $M_2(1,A,B)$ self-similar split, parent $=(1,q_1(M_0),
  q_2(M_1))$, with $a_1{=}A{-}1$, $b_0{=}B{-}2$. SCHEDULING IS A CLEAN 2-CUT
  (corrected — NOT fine interleaving): with the exact optimal modules, sweeping the
  2-cut $[M_2[:s]][M_0][M_1][M_2[s:]]$ over all $s$ hits $F_4{=}15$ at $s{=}8{\approx}m/3$.
  The earlier templated "16" came from a coarse split set skipping $s{\approx}m/3$ +
  a bounded frontier dropping the complementary modules — NOT from needing fine
  interleaving. So the wall is **module-shape generation** (the $(1,A,b_0),(1,a_1,B),
  (1,A,B)$ family with the right staircases = §15 frontier blow-up), reframed as a
  2-objective shape recursion with clean 2-cut combination. CORRECTED $\lambda_F$:
  §15 "leans pod-tight" was an over-read — $F_k/2^k=1,1,1,.94,.78$ extrapolates to
  $\lambda_F{\approx}1.66$, so $\lambda_F\in[3/2,1.904]$ UNDETERMINED. $\lambda=3/2$
  stays open.
- **2026-06-18 exact language of the $q_0=1$ face (§17;
  `scripts/stilde_face_language.py`, `tests/test_stilde_face_language.py`).**
  Corrected the "q0 is delicate" over-read. PROVED: a parent order has $q_0=1$
  iff all three child orders have $q_0=1$ and the top path places every $M_0$
  vertex before every $M_1$ vertex; $M_2$ can float arbitrarily. Exhaustive
  depth-2 verification over all $9!$ orders gives exactly 2268 face orders, and
  all 84 valid depth-2 paths preserve $q_0=1$ for every triple of face children.
  So the face language is closed and simple; the remaining wall is purely the
  two-objective scheduling of $M_2$ to keep the $q_1,q_2$ crossing maxima below
  the $2^k$ lex regime.
- **2026-06-18 clean 2-cut reduction — exact formulas, 2-staircase state, but
  exponential frontier (§18; `scripts/stilde_face_2cut.py`,
  `tests/test_stilde_face_2cut.py`).** The $M_2$ schedule is a clean 2-cut, and the
  parent heights reduce to EXACT validated formulas: $Q_1=\max(q_1M_0,q_1M_2,q_1M_1
  +\mathrm{pre}_1(M_2,s))$, $Q_2=\max(q_2M_1,q_2M_2,q_2M_0+\mathrm{suf}_2(M_2,m{-}s))$
  (0 mismatches vs closure_heights). STATE COLLAPSES: $M_0,M_1$ enter only as
  scalars; ONLY $M_2$ carries 2 staircases ($\mathrm{pre}_1,\mathrm{suf}_2$) — a
  2-objective, 1-parameter ($s$) problem. The reduced recursion REPRODUCES $F_4=15$.
  BUT the $(\mathrm{pre}_1,\mathrm{suf}_2)$ Pareto frontier grows $\times5.4,5.07
  \approx\times5.2$/level (10,54,274) = EXPONENTIAL ⇒ construction does not close
  (depth-5 "33" was a cap+sampling artifact; formulas exact ⇒ full search gives 25).
  Strictly more tractable than the general profile ($\times5.2$ vs $\times{\sim}10$)
  but same staircase wall in attenuated 2-objective form. Residual open question
  pinned to ONE quantity: does the 2-staircase frontier admit a polynomial
  generating description? (yes ⇒ $\lambda=3/2$). $\lambda=3/2$ open.
- **2026-06-19 exact 2-staircase closure under the clean 2-cut (§19;
  `parent_state_2cut`).** Strengthened §18 from terminal-height formulas to full
  state closure: the parent $\mathrm{pre}_1,\mathrm{suf}_2$ staircases have
  explicit four-region max/+ formulas in terms of the three child
  $(q_1,q_2,\mathrm{pre}_1,\mathrm{suf}_2)$ states and the cut $s$. Validated
  exhaustively for all $B_1\to B_2$ triples/all cuts and on every cut of the
  depth-4 face witness modules. Consequence: the clean 2-cut algebra is genuinely
  closed; the residual obstruction is not hidden interval data but the growth of
  the closed 2-staircase Pareto frontier itself.
- **2026-06-19 first growth proof attempt: jump-position antichains (§20;
  `scripts/stilde_2staircase_growth.py`,
  `tests/test_stilde_2staircase_growth.py`).** Important correction/strengthening:
  the §18 sizes (about 10,53,264) are the bounded representative recursion, not the
  full closed algebra. Exact one-step closure from the 10 depth-2 states gives
  10000 candidates, 5832 distinct reduced states, and **488** Pareto-minimal
  depth-3 states; **124** already have the same height pair $(3,3)$. PROVED
  structural normal form: for fixed terminal heights, pointwise staircase
  dominance is coordinatewise dominance of jump positions in reverse, so the
  frontier is a high-dimensional jump-position antichain. A five-cut family
  ($s=4,\dots,8$) from child shapes $(2,2),(2,2),(2,3)$ is a certified antichain
  surviving in the full depth-3 frontier. Still missing for an asymptotic theorem:
  external nondomination induction, i.e. a way to prove no competing triple
  dominates the recursively generated cut-tradeoff states.
- **2026-06-19 proof start: plateau-antichain lemma (§21).** Split external
  nondomination into two independent obligations. If a generated cut family lies
  in a fixed height-pair slice $(A,B)$, the pair is scalar-isolated (no generated
  state has both endpoints $\le(A,B)$ except the same pair), and the family is
  Pareto-minimal inside that slice, then the family survives in the full frontier.
  This converts the asymptotic frontier problem into a recursive plateau
  construction: prove scalar endpoint isolation plus a fixed-slice
  jump-position antichain. The depth-3 five-cut family satisfies the certificate
  exactly (`scalar_minimal_pair`, `slice_pareto_frontier`,
  `sample_cut_antichain`; test added). This is a genuine proof interface, but the
  recursive plateau induction is still open.
- **2026-06-19 attempted finish: scalar plateau induction fails; delayed-jump
  barrier is the exact missing theorem (§22).** Iterating the depth-3 five-cut
  family locally gives a large restricted next frontier (580 states, 485 in the
  $(5,5)$ slice), so the antichain mechanism is real. But $(5,5)$ is not
  scalar-isolated in the full depth-4 algebra because lower boundary states such
  as $(4,4),(3,5),(5,3)$ exist; scalar isolation alone cannot iterate. Direct
  witness checks show the standard lower boundary witnesses dominate none of the
  485 restricted $(5,5)$ states, so the right missing statement is sharper:
  a delayed-jump barrier saying every lower-scalar competitor must have some
  $\mathrm{pre}_1$ or $\mathrm{suf}_2$ jump too early to dominate the recursive
  cut family. This is the remaining analytic core; no complete proof yet.
- **2026-06-19 the delayed-jump barrier is FALSE (§23;
  `tests/test_stilde_2staircase_growth.py`).** Tested the §22 analytic core
  computationally: it fails at the first step. The $(5,5)$ plateau family ($485$
  states from closing the five-cut $(3,3)$ family) is **entirely dominated** —
  $\mathbf{485/485}$, zero survive — by generated lower-scalar $(4,5)$ and $(5,4)$
  states, exactly the two boundary slices the §22 witness list ($(4,4),(3,5),(5,3)$)
  omitted. Verified explicit instance: $Y=(1,5,4)$ dominates $x=(1,5,5)$ pointwise
  on both staircases (`parent_state_2cut` is the validated closure). So the barrier
  is false and the plateau-iteration **exponential**-frontier route is dead.
  DIRECTION FLIP: by §22's own dichotomy, "lower-scalar states cover the
  cut-tradeoff antichain" is the **polynomial-frontier / pod-tight** side — and the
  whole $(5,5)$ antichain is absorbed by just $(4,5),(5,4)$. So the evidence now
  points TOWARD $\lambda=3/2$, not away. NOT a proof: it is one closure step; a real
  pod-tightness proof needs the covering shown RECURSIVELY (every high-scalar slice
  dominated by polynomially many lower-scalar boundary states at every level) — the
  new, sharper, more-plausible target. $\lambda=3/2$ open.
- **2026-06-19 polynomial-frontier route NOT VIABLE — boundary antichain grows
  (§24).** Tested whether the §23 "pod-tight side" can actually close $\lambda=3/2$
  via a polynomial frontier. NO: the frontier *at the optimal product $F_k$* is
  itself a growing jump-antichain. Boundary Pareto states (product $=F_k$): depth-3
  EXACT $=28$ (product 8); depth-4 $\ge126$ (sampled lower bound, slices
  $(3,5),(5,3)$) — grows $\ge\times4.5$ in one step; near-boundary (product $\le20$)
  $\ge3253$ at depth 4. So §23's covering of high-scalar slices is irrelevant — the
  obstruction is the boundary slices, which are the minimum (not dominated) and
  carry exponential antichains. NEITHER §22 dichotomy side gives a theorem:
  exponential-lower-bound route dead (§23), polynomial-frontier route dead (§24,
  super-polynomial even at $F_k$). CONCLUSION: frontier-tracking CANNOT prove
  $\lambda=3/2$; the whole closed-2-staircase program (§18–§24) is exhausted. A
  proof must be a DIRECT asymptotic family argument (exhibit orders of product
  $(3/2)^{k+o(k)}$ without tracking the frontier) or a direct $\lambda>3/2$ lower
  bound. $\lambda=3/2$ genuinely open; finite computation + frontier algebra do not
  settle it.
- **2026-06-20 engine-readiness screen — Shearer pair-rigidity route DOMINATED
  (§25).** Question "is it a good time to launch the autonomous engine on λ?": NO.
  A scout panel (5 fresh attack vectors + literature grounding) surfaced exactly one
  candidate FINITE oracle — the pair-marginal rigidity gap g_c=log₂(q_cq_{c+1})−
  H(r_c,r_{c+1}) (vector 1, Shearer/Loomis-Whitney). Built + ran it
  (`scripts/stilde_pair_marginal_screen.py`, `data/pair_marginal_screen.json`, 3
  tests green). RIGOROUS Proposition: λ_lb(π)=(3/2)·2^{S(π)/2d}≤Q(π)^{1/d} for every
  order (the Shearer chain is a LOWER bound on log₂Q, so per-level ≤Q^{1/d}); hence
  the best certificate ≤ L_d^{1/d}, which already → λ from above by
  submultiplicativity. So proving λ>3/2 this way ⟺ proving the gap asymptotically
  SATURATES its excess cap 2(log₂L_d−d·log₂(3/2)) — a fresh asymptotic claim, NO
  finite oracle. Screen data: gap is a SHRINKING fraction of its cap (≈0.20 at
  d=2,3 → 0.07–0.09 at d=5), weak lean to λ=3/2. HONEST caveat: single SAT witnesses
  underestimate S (d=2 exhaustive max-over-246-minimizers λ_lb=1.698 > solver
  witness 1.587), so the empirical trend is solver-dependent — the load-bearing
  result is the order-independent Proposition, not the trend. ENGINE VERDICT: no
  decision-relevant finite oracle exists (the deciding step is irreducibly analytic,
  the wall all 5 vectors conceded) → do NOT launch; the existing ledger.json is
  also wrong-scoped (omega_vec 5.9/5.10, recommend_handback_flag=true). λ=3/2 stays
  genuinely open; the live targets remain a direct asymptotic family construction or
  a direct λ>3/2 lower bound, neither finite-checkable.
- **2026-06-20 direct analytic construction attempt: balanced-cut invariant
  (§26).** Derived the clean conditional construction: if a $q_0=1$ state with
  endpoint height $T_k$ has a cut where both relevant staircases are
  $\le(\sqrt{3/2}-1+o(1))T_k$, then three clean-2-cut copies give endpoint growth
  $\sqrt{3/2}+o(1)$ and hence product $(3/2)^{k+o(k)}$; this would prove
  $\lambda=3/2$. Tested the naive one-state self-similar version and it fails
  structurally: starting from $(1,2,2)$, best identical-copy 2-cuts yield
  $(1,2,4)\to(1,4,4)\to(1,4,8)\to(1,8,8)$, i.e. product $2^k$. A successful
  direct proof must carry a portfolio of complementary states (cheap $q_2$, cheap
  $q_1$, balanced cut state), exactly as finite optima do. Missing piece:
  a portfolio balanced-cut invariant. No complete proof.
- **2026-06-20 portfolio cut certificate (§27;
  `portfolio_cut_certificates`).** Isolated the exact local portfolio lemma for the
  clean 2-cut: target $(A,B)$ is preserved iff the endpoint inequalities hold and
  some cut satisfies `pre1 <= A-q1(M1)` and `suf2 <= B-q2(M0)`. The finite face
  optima certify the same slack pattern: depth 4
  $(1,3,5)\leftarrow(1,3,3),(1,2,5),(1,3,5)$ has cuts 8--11 with slack $(1,2)$;
  depth 5 $(1,5,5)\leftarrow(1,5,3),(1,4,5),(1,5,5)$ has cuts 24--27 with slack
  $(1,2)$. This proves the local mechanism but sharpens the remaining open target:
  endpoint preservation is not enough; a proof of $\lambda=3/2$ must regenerate the
  cheap companion modules on a growing boundary.
- **2026-06-20 regeneration is an M₂-structure problem (§28;
  `scripts/stilde_portfolio_f6_bound.py`, `tests/test_stilde_portfolio_f6_bound.py`,
  2 tests green).** A constructive probe to upper-bound $F_6$ via the portfolio
  2-cut (a route direct depth-6 face SAT cannot reach, §11.10) localizes the
  obstruction. From the §18 formulas the companions $M_0,M_1$ enter ONLY as scalars;
  only $M_2$ carries staircases — so regeneration is entirely about $M_2$. Three
  reproducible facts: (1) the $(5,7)$-portfolio companions $(1,5,7),(1,5,5),(1,4,7)$
  all EXIST at depth 5 (companion existence is free, NOT the obstruction); (2) an
  arbitrary $(1,5,7)@5$ witness gives best 2-cut product 60 / heights $(1,5,12)$ —
  $q_2(M_0){=}5$ and the $M_2$ suffix $7$ STACK because no cut suppresses $\mathrm{pre}_1$
  and $\mathrm{suf}_2$ together (target was 35); (3) the structured depth-5 optimum
  $(1,5,5)$ has ZERO simultaneous $(\le2,\le2)$ cuts at the depth-5 scale (none even
  at slack $(3,3)$) — the portfolio step destroys the simultaneous-cut property, so
  it is not preserved one level up, and the naive self-similar recursion breaks at
  depth 5. SHARPENED target: construct a depth-$(k{-}1)$ module of product $F_k$ with
  a simultaneous $O(1)$ cut ($\mathrm{pre}_1\le r_1$ AND $\mathrm{suf}_2\le r_2$ at one
  $s$). NO $F_6$ bound follows yet. Natural next probe: SAT with the cut POSITION as
  a variable — does a product-$F_6$ module with a simultaneous $O(1)$ cut exist at
  depth 5? NO refutes the portfolio route; YES gives $F_6$ + a construction template.
- **2026-06-20 simultaneous-cut SAT — portfolio mechanism BREAKS at depth 6, $F_6\le45$
  (§29; `scripts/decide_simultaneous_cut.py`, `tests/test_decide_simultaneous_cut.py`,
  3 tests green).** Built the §28 oracle: SAT for "does a depth-5 face module of
  heights $\le(1,A,B)$ admit a simultaneous cut ($\mathrm{pre}_1\le r_1$ AND
  $\mathrm{suf}_2\le r_2$)?" — cut boolean per vertex constrained to a prefix, plus
  two conditional thermometers. Validated at depth 3 ($(1,3,5)$ has a $(1,2)$ cut,
  not $(1,1)$; $(1,1,1)$ infeasible), all `verified` vs `step_profile`. RESULT
  (each target at most-permissive slack with companions clearing the $F_5{=}25$
  floor): products $35,36,40,42$ ALL **UNSAT**; min reachable $=\mathbf{45}$ at
  $(5,9)$ slack $(2,4)$ (SAT, verified). So (1) the clean slack-$(1,2)$ mechanism
  that produced $F_4{=}15,F_5{=}25$ is DEAD at depth 6 (every $(1,2)$-target UNSAT);
  the "simultaneous $O(1)$ cut" of §28 does NOT exist at a trend-continuing product.
  (2) $F_6\le45$ CERTIFIED (depth-6 order $(1,5,9)$ via $M_2{=}(1,5,9)$ + companions
  $(1,5,5),(1,3,9)$, `pod_profile` q0=1), improving submultiplicative $F_6\le50$;
  but $45/(3/2)^6{=}3.95 > F_5$ ratio $3.29$ — slack GREW $(1,2)\to(2,4)$, ratio
  jumped. CLOSES the portfolio route as a path to $\lambda=3/2$: a single-cut
  self-similar recursion with $O(1)$ slack cannot build $B_6$'s face optimum. Does
  NOT settle $\lambda$ (true $F_6$ could be $<45$ non-portfolio; direct $F_6$ SAT
  infeasible §11.10). Either $\lambda_F>3/2$ or the optimal construction changes
  character at depth 6 (multi-cut / non-self-similar).
- **2026-06-20 two-cut extension — no $F_6<45$ in the three-piece portfolio family
  (§30; `scripts/decide_two_cut.py`, `data/two_cut_f6_scan.json`,
  `tests/test_decide_two_cut.py`).** Extended the cut oracle to the schedule
  $M_2[:s]\,M_0\,M_2[s:t]\,M_1\,M_2[t:]$ with two nested prefix booleans
  (`left => right`). Exact face formulas:
  $Q_1=\max(q_1M_0,q_1M_2,q_1M_1+\mathrm{pre}_1(M_2,t))$ and
  $Q_2=\max(q_2M_1,q_2M_2,q_2M_0+\mathrm{suf}_2(M_2,m-s))$, validated against
  `closure_heights`; zero-slack cuts are handled by forcing the relevant block
  empty. Exhaustive scan over every ordered target $(A,B)$ with
  $25\le AB<45$, $A,B\ge2$, at maximal companion slack
  $(A-\lceil25/B\rceil,\ B-\lceil25/A\rceil)$: **52 targets, 0 SAT, 52 UNSAT**.
  Boundary check $(5,9)$ slack $(2,4)$ remains SAT/certified with product 45, and
  the model has coincident cuts $s=t=102$, i.e. it collapses to the one-cut witness.
  So one middle $M_2$ block does NOT improve $F_6\le45$; any $F_6<45$ construction
  must be beyond this three-piece portfolio family.
- **2026-06-21 general interleaving — 45 is a robust barrier (§31;
  `scripts/probe_general_interleave_f6.py`,
  `tests/test_probe_general_interleave_f6.py`, green).** Two facts close the
  construction side. (1) STRUCTURAL: the two-cut is the COMPLETE
  "$M_2$-floating, companions-as-blocks" family — the formulas depend on $M_2$
  only via $\mathrm{pre}_1(M_2,t),\mathrm{suf}_2(M_2,m{-}s)$ = where $M_0,M_1$ sit,
  so extra $M_2$-cuts add no parameters; beating 45 REQUIRES splitting a companion.
  (2) PROBE: a full lattice-path interleaving (§10 closure) of the STRUCTURED
  portfolio modules ($M_2{=}(1,5,9)$ simultaneous-$(2,4)$-cut witness, companions
  $(1,5,5),(1,3,9)$) — letting companions contribute staircases, not just scalars —
  sees the 2-cut reach $(1,5,9)=45$ but reaches NOTHING below 45 (arbitrary
  witnesses can't even reach 45, min 50 — §28 structure-matters confirmed). NET:
  45 is robust across one-cut/two-cut/general-interleaving. At the construction
  stage this was only the UPPER side:
  $18=d_6=\vec\chi(B_6)\le L_6\le F_6\le45$ (and $F_6\le45$ tightens
  $L_6\le45$, was 48). The boundary-cut lower bound in §32 upgrades the face value
  to exact. OVER-READ CAUTION: with $F_6=45$, roots
  $F_k^{1/k}=2,2,2,1.968,1.904,1.886$ (falling, $\lambda_F\le1.886$) and ratios
  $F_k/(3/2)^k=1.33{\to}3.95$ (rising) are BOTH consistent with $\lambda_F=3/2$
  (poly prefactor) AND $\lambda_F>3/2$ — 6 points don't separate them (cake/H19/
  $\lambda{\approx}2$ trap). Construction approach has hit its ceiling at 45; a
  decisive answer needs a DIRECT asymptotic argument, not another family.
- **2026-06-21 boundary-cut lower bound — exact face value $F_6=45$ (§32;
  `scripts/certify_F6_face_exact.py`, `tests/test_certify_F6_face_exact.py`).**
  The separator after all $M_0$ and before any $M_1$ in every $q_0=1$ parent
  forces a simultaneous cut in the $M_2$ child:
  $\mathrm{pre}_1(M_2,x)\le A-\lceil25/B\rceil$ and
  $\mathrm{suf}_2(M_2,m-x)\le B-\lceil25/A\rceil$. Thus the §30 cut SAT scan is
  not only a construction test; it is a lower-bound certificate for the whole
  face. Cases $AB<25$ are excluded by the $M_2$ child and $F_5=25$; cases $A=1$
  or $B=1$ are excluded by the two-free-colours lemma; the remaining
  $25\le AB<45$, $A,B\ge2$ cases are exactly the 52-row
  `two_cut_f6_scan.json` ledger, all UNSAT. Together with the certified
  $(1,5,9)$ construction, this proves $\boxed{F_6=45}$. Global remains
  $18=\vec\chi(B_6)\le L_6\le45$; $\lambda$ still open, with exact face sequence
  $2,4,8,15,25,45$.

## H19 resolution
- **H19 is false.** For $B_0=TT_1$ and $B_i=C_3[B_{i-1}]$ (equivalently
  $B_i=\widetilde S_{i+1}$), H19 would imply
  $\vec\omega(B_{23})\le24$.
- Aboulker et al., *Decomposing tournaments into comparability graphs*
  (arXiv:2606.07748, June 5, 2026) prove
  $\vec\chi(D)\le\vec\omega(D)^{pod(D)}$. Here $pod(B_i)=3$ and the exact
  recurrence gives $\vec\chi(B_{23})=18206$, so
  $\vec\omega(B_{23})\ge\lceil18206^{1/3}\rceil=27$.
- Therefore some $i\in\{3,\ldots,23\}$ satisfies
  $\vec\omega(C_3[B_{i-1}])>\vec\omega(B_{i-1})+1$.
  See `docs/h19_refutation.md`.
- The D45 citation-sweep conclusion G66 missed this direct implication of
  arXiv:2606.07748 and is superseded.

## Post-D45 Route-2 history
- H25 remains proved; credit/no-deadlock and demand/relief fixed-point formulations
  are implemented.
- Escaper necessity is proved, and every critical tournament has an append-built
  level-k escaper.
- **Correction:** QR19 does not require three distinct inner orders. Its gold copy-2
  order has `D=(3,4,5)` and works when repeated: 2642 safe states, all reachable,
  zero dead-ends, with a core-verified clique-5 interleaving. D44 killed the static
  `(d,c,pos)` merge, not arbitrary shared-order interleavings.
- `scripts/route2_append_partners.py` finds shared full raisers on AC7, AC9, AC11,
  both saved order-8 critical classes, S~3, and QR19. The canonical AC_n shift has
  `D=(3,4)` for every tested odd n from 7 through 23.
- First unresolved partner test: the proved append order for AC_n[C3] has
  `D=(3,3,5)`, fixing level 3. A bounded 6381-state adjacent-swap search on
  AC7[C3] found only `(3,3,5)`, `(2,3,5)`, `(2,2,5)` and no cycle-free triple.
- These finite results remain correct, but the proposed uniform
  full-raiser-or-partners theorem is false because it would imply H19.

## Question 5.9 and Conjecture 5.10
- **Question 5.9 is already answered negatively** in this repository: the
  infinite $3$-$\vec\omega$-critical family alone rules out an identity-threshold
  certificate function. The $k=4,5$ families give two further fixed-threshold
  failures.
- **Conjecture 5.10** asks for infinitely many $k$-$\vec\omega$-critical
  tournaments at every $k\ge3$. It is proved for $k=3,4,5$ and remains open
  for $k\ge6$.
- Since $\vec\omega(\widetilde S_n)\ge n$, at least one $k$-critical tournament
  exists for every $k$ by taking a minimal induced $k$-core. The open issue is
  infinitude at each fixed $k$, not existence.
- The February 2026 bounded-certificate theorem confirms the weaker
  non-identity Conjecture 5.8; it does not settle Question 5.9.

## Open crux — two legs
SUPPLY leg for an explicit infinite $6$-critical family (Prop-6.2 dic-lift,
needs a 5-dic-vertex-critical tournament with omega_vec=5):
  CLOSED to the engine. dic>ov gap of +1 (H20) holds on FOUR structured classes (G52/G53/G58/G60);
  literature pre- AND post-2023 exhausted (G53/G60 + D45 G66: full 3-paper citing corpus of
  2310.04265 supplies nothing); foreground circulant census infeasible (G57); C3[QR_19] 5-criticality
  reduces (verified, orbit 57) to ONE no-K5 UNSAT bit but that bit is foreground-INFEASIBLE (G61).
  Residual = offline/cluster compute or analytic (non-construction) supply.
VALUE leg: **CLOSED NEGATIVE.** H19 is refuted by the iterated directed-triangle
  family. Route 2 remains useful for individual positive instances but cannot be
  uniform.

## Live hypotheses (status)
- H19: **REFUTED.** A counterexample exists among the inner tournaments
  $B_2,\ldots,B_{22}$.
- H20 (structural barrier): dic>ov gap of +1 on 4 structured classes; SUPPLY leg closed to engine.
- H21 DEAD as a proof route (static potential-sum; superseded by the H22 kill).
- H22 RESOLVED-NEGATIVE (D44), correctly scoped: no uniform static d-keyed merge realizes
  the displayed gold orders. QR19 does not force distinct inner orders under arbitrary
  dynamic interleaving.
- H25 (structural identity): two-copy split-sum identity for C3-outer products — omega(C3[H]^prec)
  = max over 3 cyclic copy-pairs (Y,X) of max_p[omega_be(Y-prefix<p)+omega_be(X-suffix>=p)]. Sound,
  exhaustive nH<=2. Post-D45: paired with demand/relief maps and append-built escapers.

## Last decisions
- D44: 0 promotions, G61-G63. H22 CONFIRMED-NEGATIVE — static-merge route closed; G61/G62/G63 killed
  the SAT-criticality bit, random first-moment, and universal DSS. H25 salvaged. frontier_advanced=TRUE.
- D45 (historical; superseded on the VALUE leg by Route 2): 0 promotions, G64-G66.
  G64 (generic ov=5 hunt n=43 all-SAT),
  G65 (k=3 lattice-path census scope-biased, min_distinct=1 degenerate), G66 (post-2023 literature
  retired). frontier_advanced=FALSE — last probe run + 3 re-kills of dead families.

## needs_human / recommend_handback
The H19 VALUE leg is closed negatively. The remaining computational question is to
identify the first failing iterated-triangle index. The independent SUPPLY leg remains
as D45: offline/cluster compute or an analytic supply of a
5-dic-vertex-critical tournament with ov=5.
