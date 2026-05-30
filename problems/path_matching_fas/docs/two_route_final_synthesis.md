# Two-route synthesis: acyclicity vs monotonicity

This note synthesises the two parallel investigations launched after
D70 closed the forward-DP route.  The forward bag-DP being dead
(D70: 2^Ω(n) lower bound), exactly two routes remained:

  * **Positive**: a non-sweep polynomial algorithm.
  * **Negative**: an NP-hardness reduction that does not encode in the
    back-arc graph (Theorems 5.1 and 6.1 close back-arc encodings).

Both returned honest negatives with a sharp unifying obstruction.  The
two obstructions are mirror images, and together they pin down exactly
why Aboulker Problem 4.4 is hard to resolve in either direction.

## 1. The two unifying obstructions

### Positive route — acyclicity is the barrier

(`docs/nonsweep_path_fas.md`.)  Path-FAS YES ⟺ T has a feedback arc
set S that is a linear forest (T − S acyclic ∧ S max-degree-2 acyclic).
All four standard polynomial paradigms fail, each at undirected
acyclicity of the back-arc graph:

| paradigm | failure | minimal witness |
|---|---|---|
| matroid intersection | acyclic-subgraph system is not a matroid | n=4 exchange-axiom violation |
| LP/ILP | triangle+deg-2 polytope fractional & unsound | NO-record-0 contains undirected 4-cycle |
| coNP / forbidden subtournament | minimal NOs unbounded (20→572→5560) | n=8 minimal NO with all 7-subsets YES |
| 2-SAT / CSP | order transitivity is ternary (Horn-3) | window matching only necessary |

A **sound** cutting-plane oracle (directed + undirected cycle cuts)
decides Path-FAS correctly (0 mismatches, n ≤ 7) but is **not proved
polynomial**.  The positive route is not refuted, only inaccessible to
all four standard paradigms.

### Negative route — monotonicity is the barrier

(`docs/nonbackarc_hardness.md`.)  A genuine non-back-arc coupling
exists (toggle variable + linker chain + closing probe), bypassing
both Theorems 5.1 and 6.1 — but it yields a reduction from **monotone
CNF-SAT**, which is in P.  The reason:

**Theorem 3.1 (Monotonicity Obstruction — scoped to the consecutive-
toggle substrate).**  For the *consecutive-toggle* substrate (each
variable a swap of an adjacent pair), Path-FAS feasibility is
monotone-decreasing in the toggle vector ε: flipping ε_i from 1 to 0
swaps a consecutive pair and only *removes* one back-arc, leaving
everything else fixed, and "linear forest" is closed under edge
deletion, so feasibility can only improve.

**Two corrections to the earlier overclaim.**

  1. *Scope.*  Theorem 3.1 is NOT about arbitrary Path-FAS encodings.
     It is specifically about the consecutive-toggle substrate, where
     lowering a toggle deletes exactly one back-edge and disturbs
     nothing else.  A *non-consecutive / global* ordering primitive
     could in principle evade it — that is exactly why Q7.1 (§4) is
     open.
  2. *Consequence, stated sharply.*  The correct conclusion is not the
     broad "monotone CSPs are all in P."  It is: the feasibility
     relations realised by this substrate are **downward-closed**, so
     the all-zero assignment is always feasible unless extra
     nonmonotone forcing is introduced.  That kills SAT-style hardness
     *for this substrate* — a SAT reduction needs an instance whose
     all-false assignment can be infeasible, which a downward-closed
     relation forbids.  It says nothing about substrates Theorem 3.1
     does not cover.

Supporting obstructions:

  * **Degree-2 fanout cap reappears** in the ordering encoding: each
    toggle variable supports ≤ 2 clause attachments (at f_i, g_i); a
    third overloads the back-arc budget.  Encoding-independent, same
    scarce resource as Theorem 5.1.
  * **Betweenness is unrealizable** (Opatrny 1979, DOI 10.1137/0208008):
    exhaustively over all 1024 tournaments on n = 5, no trio's LFO
    relative-order set equals or refines the betweenness set
    {xyz, zyx}; the smallest nonempty relative-order set has size ≥ 3.
    The LFO order-restriction is too "thick."  (Proved at n = 5 only;
    n = 6 not completed — stated honestly.)
  * **The one non-monotone primitive** (the D68 `one_block` collision)
    does not compose: its distinguishing information lives in the
    global union-find merge state, which is exactly the unsolved fanout
    problem under the degree-2 cap.

## 2. Why the two obstructions are mirror images

The positive route dies because **acyclicity is global and non-local**
(not a matroid, not finitely forbidden, not 2-SAT).  The negative route
dies because **feasibility is monotone** (only removing back-arcs helps)
and the back-arc budget is **degree-2 bounded**.

These are the same coin:

  * *Monotonicity* (negative-route barrier) is exactly what makes the
    problem *not obviously NP-hard*: a monotone problem with polynomial
    minimal obstruction recognition would be in P.
  * *Acyclicity-is-global* (positive-route barrier) is exactly what
    makes the problem *not obviously in P*: the obstruction set is
    unbounded and non-local.

So Path-FAS sits in a genuine gap: monotone enough to resist
NP-hardness, global enough to resist standard polynomial paradigms.

## 3. The honest aggregate verdict

After this round, the cumulative evidence **leans toward Path-FAS ∈ P**
but does not prove it:

  * Hardness *over the consecutive-toggle substrate* is blocked:
    Theorem 3.1 makes its relations downward-closed (all-zero always
    feasible), and the degree-2 fanout cap + order-thickness limit
    coupling.  This does NOT cover non-consecutive/global primitives
    (Q7.1).
  * The back-arc route to hardness is closed (Thm 6.1); the forced-wire
    route is closed (Thm 5.1); the ordering route is closed by
    monotonicity.
  * The positive route has a *sound* decision oracle (cutting planes)
    that is correct on every tested instance; only its polynomial
    runtime is unproved.

This is consistent with the fork-tree result (Section 65), where the
constrained problem turned out to be in P via the V6'' classifier — a
monotone (negative-Horn) structure.  The Monotonicity Theorem T48.1 of
the fork-tree work is the special case of Theorem 3.1 here.

## 4. The decisive next question

Both agents converge on one sharp question (the negative route's
Question 7.1):

> **Is there a composable non-monotone ordering primitive?**  A
> tournament gadget whose Path-FAS feasibility is a *non-monotone*
> function of an ordering choice, AND whose distinguishing state can be
> propagated to other gadgets within the degree-2 back-arc budget.

  * If **no** (provable impossibility): the non-back-arc route is closed
    as decisively as Theorem 6.1 closed the back-arc route.  Combined
    with the back-arc and wire barriers, this would make NP-hardness via
    any local-gadget reduction impossible — strong evidence for
    Path-FAS ∈ P, and a mandate to push the cutting-plane oracle to a
    polynomial bound.
  * If **yes** (a composable non-monotone primitive is found): it is the
    substrate for a genuine 3-SAT reduction, settling NP-hardness.

The `one_block` collision is the unique known non-monotone primitive;
the open problem is whether its merge-state distinction can be coupled
across gadgets under the degree-2 cap — exactly the fanout problem in a
new guise.

## 5. Files and tests

| route | document | scripts | tests |
|---|---|---|---|
| positive (non-sweep) | `docs/nonsweep_path_fas.md` | `scripts/nonsweep_path_fas.py` | `tests/test_nonsweep_path_fas.py` (7 pass) |
| negative (non-back-arc) | `docs/nonbackarc_hardness.md` | `scripts/nonbackarc_hardness.py` | `tests/test_nonbackarc_hardness.py` (16 pass) |
| synthesis | `docs/two_route_final_synthesis.md` (this) | — | — |

## 6. Honest residual uncertainties

  * The non-sweep cutting-plane oracle is sound and empirically correct
    (n ≤ 7) but **not proved polynomial**; its cut count could blow up.
  * The betweenness-unrealizability proof is exhaustive at **n = 5
    only**; n = 6 was not completed.
  * NO-instance coverage for the positive route came from the certified
    minimal-NO catalogue (n ≤ 9), not random sampling (random small
    tournaments are almost all YES).
  * The Monotonicity Obstruction is proved for the toggle/consecutive-
    swap parameterization; whether *every* ordering encoding is forced
    to be monotone is the content of open Question 7.1.

## 7. Citations verified (DOI / arXiv id)

  * AAL Problem 4.4: arXiv:2402.10782.
  * Opatrny betweenness NP-completeness 1979: DOI 10.1137/0208008.
  * Kenyon-Mathieu, Schudy FAS PTAS 2007: DOI 10.1145/1250790.1250806.
  * Schaefer dichotomy 1978: DOI 10.1145/800133.804350.
  * Edmonds matroid intersection 1970 (matroid route reference).

Both agents cross-validated the FF decider against
`decide_path_fas_bruteforce` (180 random tournaments n = 7, 8, 9, 0
mismatches) before trusting any n ≤ 10 verdict.
