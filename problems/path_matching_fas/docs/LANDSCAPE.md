# Path-FAS landscape — what is proved, what is dead, where to go

**Consolidation pass, 2026-05-30.** This is the master map over the ~40 docs in this
folder. It supersedes the stale "Status" narrative in `README.md` (which trails off
around the D67 era). Target: **Aboulker–Aubian–Lopes Problem 4.4**, path/linear-forest
half — does a tournament `T` admit an order whose back-arc graph is a **linear forest**
(LFO)? Both `Path-FAS ∈ P` and `Path-FAS NP-hard` remain **OPEN**.

Convention below: **THEOREM** = rigorous proof in-folder; **CERTIFIED** = exhaustive
finite check (verification, not proof); **REFUTED** = killed by a named witness;
**OPEN** = live.

---

## 1. What is actually proved (the theorem inventory)

### Settled adjacent result
- **Matching-FAS ∈ P** — THEOREM (`lemmas.md`, Thm 1 + Lemmas 2–5 + Thm 2). Full
  `O(n³)` algorithm: pick one arc per cyclic-3-cycle module, then 2-SAT. (Novelty vs
  modular-decomposition / FAS literature still unchecked — see README caveat.) The
  proof does **not** transfer to the path case (degree-2 V-shapes break the
  no-shortcut obstruction).

### Reformulations the whole attack rests on (all THEOREM)
- **Equivalence** (`path_fas.md`): `Path-FAS(T)=YES ⇔ ∃` order with back-arc graph a
  linear forest. Hereditary under induced subtournaments.
- **Score-window lemma** (`score_window.md`): `deg_{B_≺}(v) ≥ |i_≺(v) − d⁻(v)|`, so in
  any LFO every vertex sits in a width-5 window `I_v = [d⁻(v)−2, d⁻(v)+2]`. After Hall
  pruning at most 9 windows are active at any cut (THEOREM).
- **Forced/flexible split** (`score_window.md`): disjoint windows ⇒ the pair order is
  forced; overlapping ⇒ flexible. `H` = forced-backedge digraph, `G_flex` =
  overlap graph, `J = H ∪ G_flex` the interaction graph.

### Positive algorithmic theorems (genuine `P`/FPT islands)
- **FPT by |H|** — THEOREM (`J_width_conjecture.md` §5.2, `J_pathwidth_dp.md`):
  `pw(J), tw(J) ≤ 8 + 2|H|`, giving a DP in `f(|H|)·poly(n)`. **Polynomial whenever the
  forced-backedge count `|H|` is bounded.** (DP correctness is CERTIFIED on ≥36k
  tournaments `n≤9` + n=12 templates, not formally proved.)
- **Fork-tree tournaments ∈ P** — THEOREM (`exchange_proof_draft.md`, Thm 65.A, via
  cycle-projection on cyclic-ladder cores). This is the only fully-closed positive
  result on a non-trivial LFO subfamily; it was exactly the adversarial family that
  produced the 2^(n/4) sleeping-block blow-ups.
- **Degreewidth corollaries** (`degreewidth_direction.md`): `Δ*(T) ≤ 1 ⇒ YES` (poly,
  cubic, arXiv:2212.06007); `Δ*=0 ⇒ YES` trivially.

### The decisive impossibility theorem
- **Forward-DP lower bound (D70)** — THEOREM (`forward_dp_lower_bound.md` §3.4):
  *any* sound forward score-window DP needs `2^((n−7)/4) = 2^Ω(n)` states on the padded
  toggle family. Clean dichotomy with D66: **forward score-window DP is polynomial iff
  `|H|` is bounded.** This single theorem retroactively kills the entire forward-DP
  cluster (see §2) — they are corollaries, not independent failures.

### Negative-route structural theorems (why no natural reduction lands)
Three independent, proved barriers, each closing a reduction family:
- **Thm 5.1 interior-degree saturation** (`J_hardness_via_wires.md`): an interior vertex
  of a forced `H`-path spends *both* its back-arcs on its path neighbours ⇒ each wire
  carries ≤2 clause attachments ⇒ wire reductions give bounded-occurrence-2 SAT (poly).
- **Thm 6.1 global back-arc budget** (`reversed_matching_hardness.md`): the back-arc
  graph of any LFO is a linear forest (≤ n−1 edges, vertex-disjoint paths) ⇒ any
  back-arc-encoded reduction can only realize linear-forest constraint graphs ⇒ K₃, C₅,
  arbitrary clause graphs unreachable.
- **Thm 3.1 monotonicity** (`nonbackarc_hardness.md`): on the consecutive-toggle
  substrate LFO-feasibility is downward-closed in the toggle vector ⇒ only **monotone**
  CSPs are encodable ⇒ no both-polarity NP-hard CSP. (All-zero always feasible.)

### Clause gadget that DOES exist (so the barrier is fanout, not the clause)
- **2-in-3 clause gadget** — THEOREM by explicit construction (`port_loader_realizability.md`,
  D72): a 14-vertex tournament realizes exactly the non-Schaefer relation `{011,101,110}`
  on three ports, with forced loaders pinning every port to back-degree ≤1. So a single
  NP-hard clause *is* expressible; the **only** missing ingredient for a hardness
  reduction is **fanout** (reusing a variable across ≥3 clauses under the degree-2 cap).

---

## 2. The route graveyard (what is closed, and by what)

| Route | Status | Killer |
|---|---|---|
| All forward DPs (active-frontier, visible-latent, wake-horizon, sleeping-block, global-counter, σ-trace, exchange-repair) | **DEAD** | D70 lower bound (2^Ω(n)); individual collisions at n=7/12 are instances |
| Naive frontier / degree-only / active-bag DP | REFUTED | reversed-matching family; n=7 component witness (partition is load-bearing) |
| Visible-latent DP | REFUTED | skew n=12 witness (same signature, different extendability) |
| Dormant matching quotient (multiset aggregate) | REFUTED | n=12 `one_block`: union-find merge topology is irreducibly global |
| Cutting-plane / cycle-cut LP | **BLOCKED** | full LP feasible-fractional on 20/20 (n=7) and 546/572 (n=8) minimal-NOs — integrality gap on ~95%, no Farkas certificate |
| Matroid intersection / LP-integral / coNP-finite-obstruction / 2-SAT | DEAD | each fails at *undirected acyclicity of the back-arc graph* — it is global, not a matroid, not finitely forbidden, not 2-CNF (`nonsweep_path_fas.md`) |
| Finite forbidden-subtournament list | DEAD | minimal-NO count grows 20 → 572 → 5560 at n=7,8,9; n=8/n=9 minimals are genuine, not inflated |
| Wire-based hardness | DEAD | Thm 5.1 |
| Back-arc-encoded hardness (incl. reversed-matching → 3-COLORING) | DEAD | Thm 6.1 |
| Toggle/flex-encoded hardness (incl. betweenness) | DEAD | Thm 3.1 |
| Direct AAL forest-FAS transplant | DEAD | AAL's unbounded-degree "star" states violate the degree-2 cap |
| J-width = absolute constant conjecture | REFUTED | random-skew family: tw(J) ≈ Θ(n^0.86), grows ≈ |H|/2 + 5 |

**The recurring wall, both directions.** The positive side dies on *acyclicity is global*;
the negative side dies on *feasibility is monotone + back-degree is capped at 2*. They are
mirror images of the same degree-2 ∧ acyclic coupling.

---

## 3. The one crux open conjecture: the Fanout Barrier (Lemma C)

The whole hardness question now funnels to a single isolated combinatorial statement
(`fanout_barrier_status.md`, `fanout_barrier_theorem.md`):

> **Capacity-form Lemma C.** No EQ₂ gadget has joint capacity on both equality values —
> equivalently, no EQ₂ gadget is simultaneously **cap-00** and **iso-11**. (By Lemma R,
> all-n, the full 3-port "free-bit splitter" barrier reduces to this 2-port statement.)

If **TRUE**: no faithful fanout splitter exists ⇒ a variable feeds ≤2 clauses ⇒ the
clause-and-fanout hardness route is dead ⇒ strong (not conclusive) evidence for `P`.
If **FALSE** (a splitter exists at some n): the D72 clause gadget + that splitter could
give a genuine NP-hardness reduction.

Status: **CERTIFIED `cap_both = 0` for n ≤ 9** (n=9: 81875 EQ₂ gadgets, 1806 cap-00,
108 iso-11, 0 both). Sub-lemmas PROVED all-n: Lemma R (projection), Lemma I (internal-arc
dictionary), cap-11 = iso-11, 3-cycle characterization, adjacent-port flip, cap-00 ⇒
`|C|≤2`, and the **nested case is fully closed**. But **eight distinct proof mechanisms
were refuted or exhausted** (one-value Lemma C; non-adjacent flip; 11-saturation; local
deletion; rung compression; crossing splice — always a degree-3 overflow; out-degree
separator; relation-level mining) and the two-aux EQ₃ search (1M+ extensions, 0 capacity
gain) supports but does not prove it. The obstruction is localized to a **crux degree-3
wall** on a *growing* crossing-iso-11 family (1 at n=8 → 12 at n=9); no global
certificate. **Route officially PAUSED** as a documented open subproblem.

---

## 4. The live reframing: degreewidth (D92, newest)

`degreewidth_direction.md` recasts the problem through degreewidth `Δ*(T)` =
min-over-orders max-back-degree (arXiv:2212.06007):

| `Δ*` | back-arc graph | Path-FAS | |
|---|---|---|---|
| ≤ 1 | matching | **YES** | poly (cubic) — THEOREM |
| 2 | paths **+ cycles** | **YES iff some degree-2 order is acyclic** | **the open core** |
| ≥ 3 | — | **NO** | THEOREM (`YES ⇒ Δ*≤2`, contrapositive) |

So `Path-FAS = (Δ*≤1) ∨ (Δ*=2 ∧ ∃ acyclic degree-2 order)`, and **all the difficulty is
the `Δ*=2` acyclicity layer** — the `Δ*=2` band carries *both* YES and NO instances
(n=6 census: 15648 YES already have `Δ*=2`), so even recognizing `Δ*≤2` does not decide
the problem. Two sharp open sub-questions:

- **(Q1)** Is `Δ*(T) ≤ 2` poly-decidable? (Computing `Δ*` is NP-hard in general, but
  `Δ*≤1` is cubic; the fixed threshold `k=2` is the open gateway. The general
  NP-hardness reduction does **not** transfer to the fixed value 2.)
- **(Q2)** Among `Δ*=2` tournaments, is "∃ acyclic degree-2 order" polynomial? This is
  the genuine residual; minimal-NO `Δ*=2` instances are exactly the `large_width_no`
  family.

This is a **reframing, not a solution** — but it is the cleanest one, it is anchored to
published work, and unlike every forward-DP idea it is **not killed by D70** (a degree-2
acyclic order is a global object, not a forward sweep).

---

## 5. Promising directions, ranked

1. **The `Δ*=2` acyclicity question (Q2), and Q1 for the fixed threshold `k=2`.** The
   single cleanest live target. Concrete first moves: adapt the cubic `Δ*≤1`
   recognition or the `Δ*`-NP-hardness construction of arXiv:2212.06007 to the *value 2*
   (settles Q1); mine the `Δ*=2 = large_width_no` minimal-NO core for what forces a cycle
   in every degree-2 order (attacks Q2). A poly answer to Q1 already gives a poly
   NO-certificate for the degree-obstructed majority.

2. **A non-forward / structural poly algorithm.** D70 rules out forward DPs but explicitly
   leaves open (i) a poly *certificate* checkable without a sweep, and (ii) a non-sweep
   order (matroid-parity-style, or the "ordering-aware treewidth DP" flagged unrefuted in
   `general_path_fas_dp.md`). The degree-2 ∧ acyclic coupling that kills every naive
   paradigm is the thing such an algorithm must exploit head-on.

3. **Generalize the fork-tree theorem (65.A) toward general tournaments.** It is the only
   closed positive subfamily; its cycle-projection machinery is the most developed proof
   asset in the folder. The obvious quotients/treewidth liftings are refuted, so this
   needs the non-forward pivot of #2 — but it is the warmest start.

4. **Settle Lemma C (the Fanout Barrier).** Won't resolve `P` vs hardness by itself, but
   proving it formally closes the clause-and-fanout hardness route (tipping the balance to
   `P`), and the problem is now a clean, isolated 2-port statement with one identified
   wall (the crux degree-3 family). Needs a genuinely new, *global* argument — every
   local/statistical mechanism is spent.

**Honest balance.** The cumulative evidence leans mildly toward `Path-FAS ∈ P`: three
proved theorems plus a fanout cap block every natural hardness reduction, and the one
surviving hardness hope (Lemma C false) has 0 supporting instances through n=9. But this
is suggestive, not conclusive — and a poly algorithm, if it exists, must be cleverly
**non-forward** (D70). The most likely path to a *resolution* (either direction) runs
through the `Δ*=2` acyclicity layer of §4.

---

## 6. Census facts (CERTIFIED, for reference)

Exact non-isomorphic LFO census: n=7 → 436 YES / 20 NO; n=8 → 5016 / 1864; n=9 →
67221 / 124315. Minimal obstructions (no induced lower-order NO): 20 (n=7), 572 (n=8),
5560 (n=9) — an **infinite, growing** obstruction set. On every minimal NO the forced
graph `H` is empty and `tw(J) ≥ n−3`, so the score-window framework saturates exactly on
the hard instances. Sources: `path_fas_structure.md`, `minimal_no_obstruction_catalogue.md`.
