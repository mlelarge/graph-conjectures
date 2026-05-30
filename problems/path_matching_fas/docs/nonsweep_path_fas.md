# Non-sweep routes to tournament Path-FAS

> **Follow-up (D91): the exact cutting-plane oracle of §3 was audited on the
> certified minimal-NO catalogues — see
> [`cutting_plane_audit_status.md`](cutting_plane_audit_status.md).
> Verdict: the LP/cycle-cut route is BLOCKED — the full directed+undirected
> cycle-cut LP is feasible-fractional on 20/20 n=7 and 546/572 n=8
> minimal-NOs (only 26 LP-certifiable). This quantifies the §6 "not
> LP-integral" finding with explicit fractional witnesses.**

Aboulker–Aubian–Lopes Problem 4.4 (arXiv:2402.10782): given a tournament
`T`, decide whether some linear order has a **linear-forest** back-arc
graph.  The forward dynamic-programming route is now provably closed
(Section 1).  This note attacks the *only remaining positive route* — a
genuinely **non-sweep** algorithm — through four classical lenses: matroid
intersection, the FAS LP/ILP, certificate/coNP structure, and CSP/2-SAT.

The verdict (Section 6) is negative-with-structure: **every natural
non-sweep formulation fails at a single, identifiable obstruction — the
*undirected acyclicity* of the back-arc graph is not a matroid condition,
not LP-integral, and not 2-SAT-expressible.**  Each failure is pinned to a
minimal explicit witness.  No polynomial algorithm is claimed; an honest
obstruction is given for each route.

All code is in [`scripts/nonsweep_path_fas.py`](../scripts/nonsweep_path_fas.py);
tests in [`tests/test_nonsweep_path_fas.py`](../tests/test_nonsweep_path_fas.py)
(7 pass).  Ground truth is
[`scripts/path_fas.py::decide_path_fas_bruteforce`](../scripts/path_fas.py).

---

## 1. Recap: why the forward-DP route is closed (D66 / D70)

The reformulation we use throughout
([`docs/path_fas.md`](path_fas.md)) is:

> **Path-FAS YES ⟺ `T` has a feedback arc set `S ⊆ A(T)` whose underlying
> undirected graph is a linear forest** (max-degree ≤ 2 and acyclic).

Equivalently: there is a linear order whose set of back-arcs is a linear
forest.  (If `S` is a linear-forest FAS, a topological order of `T − S`
has back-arc set `B ⊆ S`, itself a linear forest; conversely any
linear-forest back-arc set is a linear-forest FAS.)  This equivalence is
verified exhaustively for `n ≤ 5` and on random `n = 6, 7` in
`ReformulationTest`.

Two theorems bound the *forward* route:

* **D66** ([`docs/J_width_conjecture.md`](J_width_conjecture.md)): for the
  score-window interaction graph `J = H ∪ G_flex`, `pw(J), tw(J) ≤ 8 + 2|H|`.
  Hence Path-FAS ∈ FPT(`|H|`): polynomial when the number of forced
  backedges `|H|` is bounded.

* **D70** ([`docs/forward_dp_lower_bound.md`](forward_dp_lower_bound.md)):
  any *forward score-window DP* — any algorithm whose state after a
  position-prefix is a function of the prefix — needs `2^Ω(n)` states.  The
  toggle-pair fooling set forces `2^(n/4)` pairwise extension-
  distinguishable prefixes.

The toggle family has `|H| = Θ(n)`, so forward DP is polynomial **iff**
`|H|` is bounded, and unbounded `|H|` defeats every left-to-right sweep.
The remaining positive hope must therefore be a method that does **not**
read the order off a single positional sweep.  That is the subject here.

---

## 2. Matroid / degree-constrained-FAS formulation

The reformulation invites a matroid-intersection attack à la Edmonds: a
linear-forest FAS `S` must satisfy two independence-style conditions:

* (A) the underlying undirected graph of `S` is a **linear forest**
  (forest of paths);
* (B) the complementary kept arcs `T − S` are **directed-acyclic**
  (`S` is a FAS).

If both (A) and (B) were matroids on the ground set `A(T)`, then a maximum
common independent set (Edmonds' matroid intersection, polynomial) would
decide whether a large-enough common-independent `S` is also a FAS — and
the whole problem would collapse to a polynomial search.  Each of the
three matroid hopes **fails**, with a minimal witness.

### 2.1 The acyclic-subgraph system of a tournament is not a matroid

The set of directed-acyclic arc-subsets of a digraph is an *independence
system* (downward closed) but generally not a matroid.  For tournaments we
exhibit the smallest violation.

> **Witness (n = 4).** `T` with arcs
> `{0→3, 1→0, 2→0, 2→1, 3→1, 3→2}`.  Take
> `I = {0→3, 1→0, 2→0}` and `J = {1→0, 2→0, 3→1, 3→2}`.  Both are acyclic,
> `|I| = 3 < 4 = |J|`, yet **no** `e ∈ J − I = {3→1, 3→2}` keeps `I + e`
> acyclic (adding either closes the 3-cycle through vertex 0).

This violates the matroid exchange axiom (`test_acyclic_system_not_matroid_witness`).
At the structural level, maximal acyclic subgraphs of a tournament have
*different sizes* — e.g. on a random `n = 5` tournament we found maximal
acyclic subgraphs of sizes `{5, 6, 7, 8}` simultaneously.  (Transitive
tournaments are the degenerate case where the whole arc set is the unique
maximal acyclic subgraph; every non-transitive instance exhibits the
spread.)  So **(B) is not a matroid condition**, and the FAS side of the
intersection is unavailable.

### 2.2 Linear forests are not a matroid either

The "max-degree ≤ 2 ∧ acyclic" condition (A) is the intersection of the
graphic matroid (forest) with a degree constraint — but the *conjunction*
is not a matroid.

> **Witness.** Ground set = edges of a triangle plus a pendant,
> `{ab, bc, ca, cd}`.  Maximal linear forests have sizes **2 and 3**
> simultaneously: `{bc, ca}` is maximal (adding `ab` makes a triangle;
> adding `cd` makes `deg(c) = 3`), while `{ab, bc, cd}` is a size-3
> maximal linear forest.

Different maximal-independent sizes ⇒ not a matroid.  (Max-degree-≤-2 alone
is the *b-matching* polytope, polynomial via Edmonds but not a matroid;
forest alone is the graphic matroid; their intersection — linear forests —
is neither.)

### 2.3 Consequence

Path-FAS is the search for `S` that is **simultaneously** a non-matroid
linear forest (A) and a non-matroid FAS (B).  Neither (A) nor (B) is a
matroid, so two-matroid intersection does not apply, and there is no
three-matroid polynomial result to fall back on (matroid intersection of
three matroids is already NP-hard).  The structural reason — and the one
that recurs in every subsequent route — is that **acyclicity is the
binding constraint**: undirected acyclicity (A) and directed acyclicity
(B) are both "global" graphic-cycle conditions, the precise place where
matroid *intersection* (good) degrades into matroid *parity / 3-matroid*
(hard).

The honest reading: the matroid route is dead, not by a width blow-up but
by a min-cardinality structural fact provable on `n = 4`.

---

## 3. LP / ILP integrality experiments

### 3.1 The model

For a tournament, `T − S` acyclic ⟺ `T − S` has no directed cycle.  By
Moon's theorem a tournament is acyclic iff it has no cyclic triangle, but
this is *not* true of the deletion `T − S`, which is no longer a
tournament — deleting an arc leaves a missing pair, not a reversed pair, so
longer directed cycles can survive even when every triangle is hit.  The
natural LP/ILP therefore uses, with a 0/1 variable `x_a` per arc
(`x_a = 1` ⟺ `a ∈ S`):

* **triangle (FAS-relaxation):** `Σ_{a ∈ tri} x_a ≥ 1` for every cyclic
  triangle;
* **degree ≤ 2:** `Σ_{a ∋ v} x_a ≤ 2` for every vertex `v`.

This is `_build_ilp` in the script.  Two things must be measured: is the
triangle relaxation *sound* (does it model acyclicity?), and is the
polytope integral?

### 3.2 Result: the relaxation is unsound and the polytope is fractional

On the 20 **certified minimal-NO** `n = 7` tournaments
(`data/minimal_no_obstruction_catalogue_n7.json`):

* The triangle+degree **LP relaxation is feasible on all 20** NO
  instances.  LP feasibility does *not* certify YES.
* The LP optimum is **fractional on 16/20**: values `4.5, 5.25, 5.333, …`.
  So the triangle+degree polytope is **not integral**
  (`test` evidence; `lp_relaxation_value`).
* The integer relaxed model (`ilp_linear_forest_fas_feasible`) is feasible
  on 16/20 NO instances yet the rounded `S` is **not a genuine FAS** — the
  relaxation gap (`test_relaxation_gap_witness`).

The mechanism of the gap is the cleanest single finding of this note:

> **The degree-≤-2 constraint enforces max-degree but NOT undirected
> acyclicity.**  On NO record 0, the model returns
> `S = {0→6, 3→1, 3→2, 4→1, 4→2, 6→5}`.  Here `T − S` *is* directed-
> acyclic and every vertex of `S` has degree ≤ 2, yet `S` is **not a linear
> forest**: its underlying graph contains the undirected 4-cycle
> `3–1–4–2–3` (`test_degree_constraint_alone_allows_undirected_cycle`).

So a degree-bounded directed FAS can hide an undirected cycle.  This is the
LP shadow of the Section 2 fact: undirected acyclicity is not captured by
any local (triangle/degree) inequality.

### 3.3 An exact cutting-plane oracle (sound, but not poly)

To get a *correct* non-sweep decision procedure we add two families of
lazy cuts to the integer program (`ilp_exact_linear_forest_fas`):

1. **directed-cycle cuts:** if `T − S` still has a directed cycle `C`,
   add `Σ_{a ∈ C} x_a ≥ 1` (S must break C);
2. **undirected-cycle cuts:** if the underlying graph of `S` has an
   undirected cycle `U`, add `Σ_{a ∈ U} x_a ≤ |U| − 1` (at least one edge
   of `U` must leave `S`).

We re-solve and repeat until both are clean (genuine linear-forest FAS) or
the model is infeasible (certified NO).  This is correct as a decision
oracle:

* **Random `n = 3..7`: 0 mismatches vs brute force** (`test_exact_ilp_random`).
* **All 20 certified `n = 7` minimal NOs: 0 mismatches**
  (the relaxed model gave 9 false positives here; the two cut families fix
  every one).  Cuts needed per instance: median 4, **max 20**.

The first family was already standard FAS cutting-plane; the *second* is
forced by Path-FAS specifically and is what closes the relaxation gap of
§3.2.  But the oracle is **not proved polynomial**: the number of
undirected-cycle cuts is unbounded in principle, and the fractional optima
of §3.2 show the LP relaxation gives no integral starting point.  The
Kenyon–Mathieu / Schudy PTAS (STOC 2007, DOI
[10.1145/1250790.1250806](https://doi.org/10.1145/1250790.1250806))
addresses *minimum* FAS size, not the *shape* (degree/acyclicity) of the
FAS, so it does not transfer: a near-minimum FAS of a tournament need not
be — and on NO instances cannot be — a linear forest.

**LP/ILP verdict.** The natural FAS polytope plus degree-≤-2 is *not*
integral and the linear inequality models are unsound (they miss
undirected acyclicity).  A sound model requires unboundedly many cycle
cuts; no polynomial separation/integrality is in evidence.

---

## 4. Certificate / coNP analysis for NO instances

YES has an obvious polynomial certificate: the order (verify the back-arc
graph is a linear forest in `O(n²)`).  So **Path-FAS ∈ NP**.  Is there a
polynomial certificate for NO (which would place Path-FAS in NP ∩ coNP,
evidence against NP-hardness)?

### 4.1 The hereditary obstruction certificate does not bound

Path-FAS-NO is **hereditary** ([`docs/path_fas.md`](path_fas.md)): every
induced subtournament of a YES is a YES, so an induced *minimal NO* would
be a forbidden-subtournament certificate.  If minimal NOs had bounded size,
NO ∈ coNP would follow immediately (exhibit the bounded obstruction).
**They do not.**

Using the certified minimal-NO census
(`data/minimal_no_obstruction_catalogue_n{7,8,9}.json`):

* Minimal NOs exist at `n = 7, 8, 9`, with counts **exploding**
  `20 → 572 → 5560`.
* An `n = 8` minimal NO has **every** 7-vertex induced subtournament YES
  (verified directly on the first 8 records: each is a genuine NO, and all
  `C(8,7) = 8` induced 7-subsets are YES).  So the obstruction is genuinely
  size-8, not an inflated `n = 7` obstruction.

Hence **there is no finite forbidden-induced-subtournament
characterization**: obstruction size grows with `n`.  The naive coNP
certificate (a bounded induced obstruction) does not exist.

### 4.2 What this leaves open

This does *not* prove NO ∉ coNP — only that the *local/hereditary* witness
is unbounded.  A coNP certificate, if one exists, must be **non-local**
(a global infeasibility argument such as a Farkas/LP-duality certificate or
a fractional packing of cycles).  But §3 shows the natural LP is neither
integral nor sound, so its dual does not furnish a clean integral
certificate.  We did not find a polynomial NO certificate, and the
hereditary route to one is closed.  This is *weak negative evidence* that
Path-FAS is not in coNP via any obvious obstruction theory — and therefore
weak evidence consistent with NP-hardness (the sister agent's route).

---

## 5. CSP / 2-SAT / matching formulation

The score windows ([`docs/score_window.md`](score_window.md)) confine each
vertex `v` to position interval `[d⁻(v) − 2, d⁻(v) + 2]`.  A non-sequential
approach would set up a global constraint system over the order and solve
it as 2-SAT (if expressible) or bipartite matching (vertices ↔ positions).

### 5.1 Bipartite matching captures only the window assignment

Assigning vertices to positions inside their score windows is a bipartite
matching / Hall feasibility problem, and it *is* polynomial — but it is
only a **necessary** condition (Hall feasibility), not sufficient.  The
minimal-NO census confirms this: 3 of the 20 `n = 7` NOs are Hall-failures
(detected polynomially), but **17 are Hall-feasible NOs** — the window
matching succeeds yet no valid order exists.  Matching alone cannot see the
back-arc degree/acyclicity interaction across positions.

### 5.2 The pairwise-precedence encoding is not 2-SAT

The natural Boolean encoding uses `p_{uv}` = "`u` precedes `v`".  Two
constraint types are needed:

* **transitivity of the order:** `p_{uv} ∧ p_{vw} → p_{uw}` — an inherently
  **ternary** (Horn-3) implication, not expressible in 2-CNF;
* **degree ≤ 2 of the back-arc graph:** "at most two of the (≥ 3) arcs at
  `v` are backward" — a **cardinality constraint over ≥ 3 literals**, again
  not 2-CNF.

Neither is 2-SAT (`two_sat_attempt` returns the structural reason).  This
is not a soft failure: transitivity is the canonical example of a relation
that is *not* 2-SAT-definable, and it is unavoidable because the object we
search for is a total order.  The acyclicity that broke the matroid and LP
routes reappears here as non-2-SAT transitivity.  A Horn-3 / dual-Horn
encoding exists but Horn-3-SAT with the cardinality caps is not in the
2-SAT (hence not the guaranteed-polynomial) fragment; it is exactly as hard
as the problem.

**CSP verdict.** The polynomial fragments (bipartite matching / Hall /
2-SAT) capture only the *necessary* window-assignment layer; the
*sufficient* layer (transitive order + degree-bounded acyclic back-arcs)
escapes every polynomial CSP fragment, at the same acyclicity obstruction.

---

## 6. Verdict

No polynomial non-sweep algorithm was found.  Every natural non-sweep
formulation fails at one identifiable obstruction, and each failure is
pinned to a concrete minimal witness:

| Route | Polynomial primitive | Obstruction | Minimal witness |
|---|---|---|---|
| Matroid intersection (§2) | Edmonds 2-matroid intersection | acyclic-subgraph system and linear forests are each **non-matroids** | `n = 4` tournament (exchange-axiom violation); triangle+pendant graph (LF sizes 2 and 3) |
| FAS LP / ILP (§3) | LP / integral polytope | triangle+degree polytope is **fractional** and **unsound** (degree ≤ 2 permits undirected cycles in `S`) | NO-record 0: `S` is a degree-≤-2 directed FAS but contains the undirected 4-cycle `3–1–4–2–3` |
| coNP certificate (§4) | bounded forbidden subtournament | obstruction size **unbounded** (counts `20→572→5560`; size-8 minimal NO with all 7-subsets YES) | the `n = 8` minimal-NO records |
| CSP / 2-SAT / matching (§5) | 2-SAT, bipartite matching | order transitivity is **Horn-3 not 2-SAT**; window matching is only **necessary** (17/20 NOs are Hall-feasible) | the 17 Hall-feasible `n = 7` minimal NOs |

**The single recurring obstruction is acyclicity.**  Undirected
acyclicity of the back-arc graph (and directed acyclicity of its
complement) is the property that is simultaneously: not a matroid (so no
matroid intersection), not LP-integral and not local-inequality-soundable
(so no FAS-polytope route), not finitely forbidden (so no hereditary coNP
certificate), and not 2-SAT-expressible (transitivity is ternary).  Each
of the four classical polynomial toolkits degrades at exactly this point.

What survives as a *correct but not-proven-polynomial* artefact is the
two-family cutting-plane oracle of §3.3 (directed-cycle + undirected-cycle
cuts), validated at 0 mismatches against brute force on random `n ≤ 7` and
all 20 certified `n = 7` minimal NOs.  It is the honest non-sweep
counterpart of the closed forward DP: correct, general, and exponential in
the worst case (cut count unbounded; up to 20 cuts already at `n = 7`).

**Status of Problem 4.4 after this round:** still open.  The positive
non-sweep route is not refuted (no proof that Path-FAS ∉ P) but is shown to
be inaccessible to all four standard polynomial paradigms, each blocked by
the acyclicity obstruction.  This is consistent with — and mildly
supportive of — the negative (NP-hardness) route pursued in parallel: the
problem resists exactly the structure (matroid/LP/coNP/2-SAT) that
polynomial problems usually possess.

---

## 7. Files and tests

| Artefact | Location |
|---|---|
| Non-sweep formulations + exact cutting-plane oracle | [`scripts/nonsweep_path_fas.py`](../scripts/nonsweep_path_fas.py) |
| Tests (reformulation, exact ILP, obstruction witnesses) | [`tests/test_nonsweep_path_fas.py`](../tests/test_nonsweep_path_fas.py) — 7 pass |
| Ground truth | [`scripts/path_fas.py`](../scripts/path_fas.py) |
| Certified minimal-NO census | `data/minimal_no_obstruction_catalogue_n{7,8,9}.json` |

## 8. Citations (DOI / arXiv id)

* Aboulker, Aubian, Charbit, Lopes. *Finding forest-orderings of
  tournaments is NP-complete.* arXiv:2402.10782 (2024). Problem 4.4.
* Kenyon-Mathieu, Schudy. *How to rank with few errors.* STOC 2007,
  DOI [10.1145/1250790.1250806](https://doi.org/10.1145/1250790.1250806).
  (PTAS for minimum FAS on tournaments; minimises size, not FAS shape.)
* Edmonds. *Matroid intersection.* Annals of Discrete Mathematics 4
  (1979) 39–49, DOI
  [10.1016/S0167-5060(08)70817-3](https://doi.org/10.1016/S0167-5060(08)70817-3).
* Moon. *Topics on Tournaments.* Holt, Rinehart and Winston, 1968.
  (Tournament acyclic ⟺ no cyclic triangle.)
* Coppersmith, Fleischer, Rurda. *Ordering by weighted number of wins
  gives a good ranking for weighted tournaments.* ACM Trans. Algorithms
  6(3) Art. 55 (2010), DOI
  [10.1145/1798596.1798608](https://doi.org/10.1145/1798596.1798608).
  (Indegree/score-window proxy.)
* Schaefer. *The complexity of satisfiability problems.* STOC 1978,
  DOI [10.1145/800133.804350](https://doi.org/10.1145/800133.804350).
  (2-SAT dichotomy; transitivity is outside the Schaefer-tractable
  fragment.)
