# NP-hardness direction for general-tournament Path-FAS

This note investigates whether Aboulker–Aubian–Lopes Problem 4.4 (the
Path-FAS half) admits an NP-hardness reduction.  The conclusion is
honest and negative: at the time of writing, no reduction is known, the
"obvious" route from Min-FAS-on-tournaments **does not** work, and a
catalogue of failed local-gadget attempts is consistent with the
Path-FAS-in-P hypothesis.  Sections 1–2 nail the problem statement and
citations; Section 3 explains the non-reduction; Section 4 records the
SAT-gadget attempt; Section 5 states the honest verdict.

The fork-tree adversarial subfamily is now closed in P (Section 65 of
`docs/exchange_proof_draft.md`), so this document concerns only the
remaining general-tournament case.

## 1. The precise decision problem in Problem 4.4

### 1.1. Source

The problem is stated in:

> Pierre Aboulker, Guillaume Aubian, Pierre Charbit, Raul Lopes.
> *Finding forest-orderings of tournaments is NP-complete.*
> arXiv:[2402.10782](https://arxiv.org/abs/2402.10782) (2024).

Verbatim, on page 9 of the arXiv v1 PDF (`/tmp/aal.txt` line 688):

> **Problem 4.4.**  What is the complexity of the C-FAS Problem when C
> is the set of all paths?  when C is the set of graphs with maximum
> degree 1?

The C-FAS problem on a tournament T is defined (paper §1) as:

> Given a class C of undirected graphs, decide whether T admits a
> feedback arc set F ⊆ A(T) such that the underlying undirected graph
> of F lies in C.

So Problem 4.4 is purely a **decision problem**:

> **(Dec-Path-FAS).**  Given a tournament T, decide whether there exists
> a feedback arc set F ⊆ A(T) whose underlying undirected graph is a
> path.

There is **no prefix, no constraint set, no optimization**.  The
"constrained Path-FAS" referenced inside `docs/exchange_proof_draft.md`
Sections 47, 65 is a *subroutine* used in the fork-tree algorithm
(constrained extendability of a partial toggle assignment) — it is not
the question Aboulker asks.  Aboulker's Problem 4.4 is the bare
existence decision problem.

### 1.2. Equivalent formulations

Two equivalent formulations are recorded in `docs/path_fas.md`:

(F1) Existence of an order ≺ on V(T) such that the back-arc graph
B_≺(T) is a linear forest (max degree ≤ 2, acyclic).

(F2) Existence of F ⊆ A(T) such that T − F is acyclic and the
underlying graph of F is a path.

Equivalence (F1 ⇔ F2) is proved in `docs/path_fas.md`: any linear
forest can be completed to a path by adding extra arcs, and any subgraph
of a path is a linear forest.  Both formulations are pure decision.

## 2. Status of Min-FAS on tournaments and why it does not transfer

### 2.1. Citations

| Result | Source | Identifier |
|---|---|---|
| Min-FAS on tournaments is NP-hard | Charbit, Thomassé, Yeo, *Comb. Probab. Comput.* 16(1):1–4, 2007 | HAL [lirmm-00140321](https://hal.science/lirmm-00140321) |
| Independent proof + inapproximability | Alon, *SIAM J. Discrete Math.* 20(1):137–142, 2006 | [DOI 10.1137/050623905](https://doi.org/10.1137/050623905) |
| PTAS for Min-FAS on tournaments | Kenyon-Mathieu, Schudy, STOC 2007, 95–103 | [DOI 10.1145/1250790.1250806](https://doi.org/10.1145/1250790.1250806) |
| Forest-FAS on tournaments is NP-complete | Aboulker, Aubian, Lopes, 2024 | [arXiv:2402.10782](https://arxiv.org/abs/2402.10782), Thm 1.1 |

### 2.2. Why Min-FAS-NP-hardness does NOT imply Path-FAS NP-hardness

The naive intuition is "Path-FAS is more constrained than Min-FAS, so
it is at least as hard."  This intuition is wrong: the two problems
test orthogonal properties of T.

Concretely:

* **Min-FAS** is the *cardinality* optimisation: minimise |F| over all
  feedback arc sets F.  As a decision: "does T have a FAS of size ≤ k?"
* **Path-FAS** is a *shape* membership: does some F have its underlying
  graph isomorphic to a path?  No cardinality constraint.

There is no inclusion either way:

* A min-cardinality FAS need not be a path.  E.g. the Paley tournament
  Q(7) has minimum FAS size 7, and the minimum FAS attained by the
  lex-min ordering has underlying graph with degree sequence
  `(3, 3, 2, 2, 2, 1, 1)` — not a path.  (Verified in code; see § 2.3.)
* A path-shaped FAS need not be minimum.  Adding "extra" tournament
  arcs to a back-arc linear forest to complete it to a path (Step in
  the equivalence F1 ⇔ F2) generically inflates |F|.

Equivalent observation: Min-FAS-NP-hardness reduces an arbitrary
Min-FAS instance on a tournament T₀ to "(T₀, k): is min FAS ≤ k?".  To
reduce **this** to Path-FAS, one would have to build a tournament T
such that "T has a path-FAS" iff "T₀ has a FAS of size ≤ k".  No such
construction is known, and the structural obstruction is concrete: the
path-shape constraint is on a low-degree quantity (the *graph* of F),
while Min-FAS bounds a high-degree quantity (its *cardinality*).

In particular, the Aboulker–Aubian–Lopes paper proves *forest-FAS* is
NP-hard (their Theorem 1.1) via an explicit reduction from 3-SAT, and
the **same paper poses Path-FAS as open** (their Problem 4.4).  This is
itself strong evidence: if Min-FAS-NP-hardness automatically transferred
to Path-FAS, the authors would not have asked.

### 2.3. Small-instance verification

`scripts/path_fas.py::decide_path_fas_bruteforce` and a 7-vertex Paley
computation give (run with `uv run python` from the package root):

```
Q(7) Path-FAS YES?  False
Min FAS size for Q(7):  7
A min FAS:  [(3,0),(4,1),(5,0),(5,2),(6,0),(6,1),(6,3)]
Underlying degree sequence:  [3, 3, 2, 2, 2, 1, 1]
```

Q(7) is Path-FAS NO purely from the size bound n − 1 = 6 < 7.  But the
attained min FAS is also non-path in shape — vertex 6 has degree 3.
This is exactly the data the obstruction predicts.

`tests/test_path_fas.py::FOREST_NOT_PATH_FAS` exhibits the
complementary separation: a 7-vertex tournament with min FAS size 5 ≤
n − 1, hence the size bound passes, yet Path-FAS is NO (all 5040
orderings produce a back-arc graph that is either non-forest or has a
degree-3 vertex).

Both witnesses are pinned in the existing test suite (passing).

## 3. Why no reduction is known: the gadget catalogue

The natural reduction template, transplanted from the AAL forest-FAS
proof, requires three pieces:

1. **Variable gadget.**  A small sub-tournament with exactly two LFOs,
   corresponding to truth value 0 / 1 at a designated port pair.
2. **Clause gadget.**  A small sub-tournament whose port-bit relation
   equals (or contains) a known NP-hard CSP constraint.
3. **Fanout / wire.**  A sub-tournament that broadcasts the variable's
   truth value to k clause occurrences, *forcing* all copies to agree.

For Path-FAS, the prior project has built precise verifiers for these
gadgets (`scripts/np_hardness_gadget_verifier.py`,
`scripts/np_hardness_reduction.py`).  Their findings are:

### 3.1. Variable gadget — exists

The **Section 16 toggle** (4-vertex gadget from D6 of the proof draft)
is a valid two-state variable gadget.  Its port-bit truth table is
9 LFOs for bit=False and 4 LFOs for bit=True; both bits are realised
and no other state is.  See § 43.2 of `docs/exchange_proof_draft.md`.

In addition, `docs/hardness_route.md` records an explicit 9-vertex
*rigid* path-state variable block with a single LFO whose back-arc
graph is a Hamiltonian path of degree 1 at the anchor (Section
"Anchor-safe path rigidity is achievable").

### 3.2. Clause gadget — exists for NAE-3SAT only

The **cyclic triangle** on 3 vertices realises *exactly* the 6
non-constant 3-bit patterns under the placement-bit semantic — the
NAE-3SAT allowed set.  Two constant patterns (FFF, TTT) are forbidden.
This is the exact NAE-3SAT clause relation.

No 3-vertex gadget realises the 1-in-3-SAT clause relation; an
exhaustive search over the 4 non-isomorphic 3-vertex tournaments fails
(§ 43.1 of `docs/exchange_proof_draft.md`).

Since NAE-3SAT is NP-complete (Schaefer 1978), the clause-half of the
reduction is in principle workable.

### 3.3. Fanout gadget — does NOT exist, locally

The fanout obligation is: a tournament fragment W on O(k) vertices,
with one input port (a, b) and k output ports
(a^{(1)}, b^{(1)}), …, (a^{(k)}, b^{(k)}), such that the LFO truth
table of W consists of exactly the two assignments
(0, 0, …, 0) and (1, 1, …, 1).

This is the equality relation R_eq^{(k)} = { (0)^k, (1)^k } realised by
a small tournament gadget.  It is the central open obligation for the
hardness route.

**Empirical record.**  Beyond what is summarised in § 43.3 of the proof
draft, the file `docs/hardness_route.md` documents:

| Search target | Outcome |
|---|---|
| AAL Figure-1 block transplanted to Path-FAS | Fails: rigid block has forced max degree 4 in the unique forest-ordering |
| 7-vertex two-state port block | Exists: gives R/L states but no spare degree at inactive ports |
| 1- and 2-vertex padding extensions of the 7-block (32 768 cases) | 0 strict inactive-spare extensions |
| Random n = 8, 50 000 samples | 0 |
| Random n = 9, 20 000 samples | 0 |
| Single external "clause" wiring, 128 orientations | 0 strict; 1 relaxed (fragile, exploits an isolated vertex in the R-state path decomposition) |
| Two external vertices, 32 768 orientations | 0 strict, 0 robust relaxed |
| Aligned fork-tree fanout at k = 2 | Realises the full 4-element binary relation, NOT equality fanout |

The cumulative negative evidence is summarised in `hardness_route.md`
Section "Status of the hardness route".

### 3.4. The structural reason behind the gadget failure

The Path-FAS local LFO constraint is "every vertex has back-degree ≤ 2,
no back-arc cycle."  This is a hard degree-2 budget *per vertex*.

In a fanout gadget at k copies, the broadcast vertex must touch all k
copies with back-arcs in some LFO (to "enforce" them).  But the same
broadcast vertex can have at most 2 back-arcs total in any single
ordering.  Hence the local-broadcast template fails for k ≥ 3.

The "asymmetric wiring" salvage attempts to push the enforcement onto
distributed pairs, but the empirical record (§ 3.3) shows the spare
degree just is not there.  The score-window theorem
(`docs/score_window.md`, §1 of `exchange_proof_draft.md`) further
forces every vertex into a width-5 position window of its in-degree,
limiting the freedom available for adversarial wiring.

This is *not* a proof that no fanout gadget exists at any size n.  It
is, however, a structural obstruction that has resisted every local
search and every search-driven combinatorial extension over the entire
n ≤ 9 enumeration plus 100k+ random extensions at n ∈ {7, 8, 9}.  See
`docs/fanout_interface.md` for the formal definitions and pinned tests
(`tests/test_fanout_interface.py`, 19 passing tests).

## 4. Direct 3-SAT (NAE-3SAT) reduction — attempt and obstruction

The reduction template specialises to NAE-3SAT (since the clause gadget
exists in § 3.2):

```
input:    Φ = NAE-3SAT formula on n variables, m clauses
output:   T_Φ tournament

build:
  for each variable v in Φ:
      attach a Section-16 toggle T_v with port (a_v, b_v)
  for each clause C = (l₁, l₂, l₃):
      attach a cyclic triangle T_C with ports (p₁, p₂, p₃)
      wire p_i to (the output of fanout of l_i's variable port)
```

Composition step ("wire p_i to fanout output") is where the construction
**fails**, because the fanout from § 3.3 does not exist.  Direct
identification of each clause port with the variable's port (i.e. each
literal port *is* the variable's b_v vertex) yields a tournament whose
LFOs do not respect the variable assignment globally: § 43.5 of the
proof draft records that without a fanout, soundness (← direction) is
"unattackable."

`scripts/np_hardness_reduction.py::build_nae3sat_skeleton` emits this
construction with the variable-to-clause linkage flagged
`fanout_NOT_IMPLEMENTED`, exactly to record the gap.  Running the
smoke-tests:

```
uv run python scripts/np_hardness_reduction.py
```

prints the variable gadget's verified truth table, the clause gadget's
verified NAE-3SAT match, and the skeleton with the open fanout slot.

The status board for the five reduction tasks (§ 43.6 of the proof
draft) is unchanged:

| Task | Status |
|---|---|
| T1 variable gadget | done — Section 16 toggle |
| T2 fanout — equality relation R_eq^{(k)} | **open**, strong negative empirical evidence |
| T3 clause (NAE-3SAT) | done — cyclic triangle |
| T3 clause (1-in-3-SAT) | failed in isolation; no 3-vertex gadget |
| T4 composition (full T_Φ) | not constructible without T2 |
| T5 iff proof (both directions) | not started; (←) blocked on T2 |

## 5. Alternative reduction sources

### 5.1. Min Linear Arrangement

Min Linear Arrangement (MLA) is NP-hard on general graphs (Garey,
Johnson, Stockmeyer 1976).  On tournaments, MLA is implicitly studied
under "Kemeny ranking" / "FAS minimisation" — they coincide with Min-FAS
since the linear-arrangement cost on a tournament is exactly the number
of back-arcs.  Hence MLA on tournaments ≡ Min-FAS on tournaments, and
the obstruction of § 2.2 applies verbatim.  This route adds nothing.

### 5.2. Triangle-FAS, the other open AAL question

Aboulker–Aubian–Lopes Problem 4.1 asks the same C-FAS question for C =
triangle-free graphs.  It is also open.  A reduction Triangle-FAS →
Path-FAS would not help here (both are open).  A reduction in the
opposite direction would, but no such reduction is known.

### 5.3. Forest-FAS

Forest-FAS on tournaments **is** NP-hard (AAL Thm 1.1).  Any reduction
Forest-FAS → Path-FAS would prove Path-FAS NP-hard.  The natural
attempt is exactly the AAL gadget transplant, which fails at § 3.3 (the
inactive-port degree-2 budget).  We have no other candidate.

## 6. Honest verdict

### 6.1. Status

**Unresolved.**  Path-FAS on general tournaments is neither known to be
in P nor known to be NP-hard.

### 6.2. What we did NOT prove

* We do not prove NP-hardness.  All attempted reductions fail at the
  fanout / variable-broadcast step.
* We do not prove membership in P.  The negative evidence against
  fanout existence is empirical and partial; no impossibility theorem
  is known.

### 6.3. Where the structural evidence points

The cumulative empirical record now spans:

* Exact LFO censuses at n ≤ 9 (191 536 non-iso tournaments at n = 9,
  inclusive of minimal NO obstructions).
* Gadget-level enumerations: 7-, 8-, 9-vertex two-state blocks; all
  AAL-block transplants; single- and double-external wiring of the
  7-vertex two-state block.
* Schaefer-style classification: every fork-tree relation R(π) at
  k ≤ 7 is Horn, not bijunctive (D34, D35).  Horn is one of Schaefer's
  six tractable classes.
* The fork-tree subfamily — the natural adversarial family for any
  reduction — has its constrained Path-FAS extendability problem
  decided in O(k) time (Theorem 65.A).

This pattern (no broken gadget at any tested size, every classifiable
sub-problem landing in a tractable Schaefer class) is more consistent
with Path-FAS being in P than with it being NP-hard.  It is *not* a
proof of either.

### 6.4. The sharpest open questions

1. **The Fanout Question (T2).**  Does there exist a tournament
   fragment realising the equality relation R_eq^{(k)} at the
   placement-bit semantic, for k ≥ 3?  An impossibility theorem here
   would essentially close the AAL-style reduction route and reduce
   the problem to a structural / DP attack for the positive side.

2. **The Horn-Oracle Conjecture (47.4).**  Is there a polynomial-time
   algorithm that, given (k, π, S), decides whether S is a minimal
   fatal toggle support of fork-tree(k, π)?  A positive answer combined
   with the fork-tree closing theorem (Section 65) would put the
   adversarial subfamily fully in P, leaving only the non-fork-tree
   tournaments to attack.

3. **The bounded-treewidth DP.**  The score-window theorem bounds
   every vertex within a width-5 position interval of its in-degree.
   This produces a natural "interval-bag" DP state.  The current
   negative result (`docs/score_window.md`) is that the naive
   active-bag DP fails because component connectivity through expired
   vertices is load-bearing.  The right quotient remains open.

### 6.5. Reading guide

For the reader picking up this problem fresh:

* The problem statement and small separating examples:
  `docs/path_fas.md`, `docs/path_fas_structure.md`.
* The gadget-level negative record: `docs/hardness_route.md` and
  `docs/fanout_interface.md`.
* The DP attack and its current bottleneck:
  `docs/exchange_proof_draft.md` Sections 1, 41–65 (with the closed
  fork-tree case as Theorem 65.A).
* The reduction-side scripts and their tests:
  `scripts/np_hardness_reduction.py`,
  `scripts/np_hardness_gadget_verifier.py`, and the
  `tests/test_np_hardness_*.py` files.

The honest summary is that NP-hardness of Path-FAS on tournaments is
**open**, the obvious reductions fail at a specific, well-characterised
step (broadcast under a degree-2 budget), and the empirical record over
the last several months of intense gadget search is mildly suggestive
of Path-FAS ∈ P.  No theorem in either direction is yet available.
