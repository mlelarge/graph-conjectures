# Path-FAS in tournaments: a sharpened reformulation and a methods-barrier map

**Scope.** This note concerns the *path* case of Problem 4.4 of Aboulker,
Aubian & Lopes — equivalently the **linear-forest feedback-arc-set** problem on
tournaments. It is, to our knowledge, open. The note does two things:

1. it places the problem in its **degreewidth** context, which makes precise
   why the neighbouring cases (matching, max-degree-2, forests) are already
   settled and pins the open difficulty to a single feature — *acyclicity*;
2. it gives two exact, tournament-specific **reformulations** (a directed
   3/4-cycle transversal and an "apex-cut" CSP) and a **map of why every
   standard polynomial technique stalls**, all at the same global obstruction.

It is **not** a proof that Path-FAS is in P, nor that it is NP-hard. The honest
reading of the barrier map is: *the standard polynomial toolkits do not see the
structure; the complexity remains open.* All empirical statements are finite
verification (`n ≤ K`), not theorems, and are marked as such; load-bearing
citations were checked against the primary sources.

---

## 1. Definitions and the degreewidth context

Let `T` be a tournament. For an order `≺`, the **back-arc graph** `B_≺` is the
undirected graph of arcs `u→v` with `v ≺ u`. For a class `C` of undirected
graphs, a **`C`-FAS** is a feedback arc set whose underlying graph lies in `C`
(Aboulker–Aubian–Lopes [AAL]). Two facts make the framing clean:

- `F` is a FAS iff `F ⊇ B_≺` for some order `≺`; minimally `F = B_≺`.
- A subgraph of a `C`-graph need not be in `C`, but for the classes here it is
  (paths/forests/matchings/bounded-degree are all subgraph-closed), so a
  `C`-FAS exists iff **some order has `B_≺ ∈ C`**.

**Degreewidth** (Davot, Isenmann, Roy & Thiebaut [DIRT]):
`Δ*(T) = min over orders of the maximum back-degree` = the least `k` such that
some order has `B_≺` of maximum degree `≤ k`. Then `C = {max-degree ≤ k}` gives

> a max-degree-`k` `C`-FAS exists **iff** `Δ*(T) ≤ k`.

This aligns the whole `C`-FAS landscape with degreewidth thresholds:

| `C` | `C`-FAS = | complexity | reference |
|---|---|---|---|
| empty (`k=0`) | `Δ*=0`, transitive | trivial | — |
| matching (`max-deg ≤1`) | `Δ*≤1` = **sparse** | **`O(n³)`** | DIRT (arXiv:2212.06007) |
| `max-deg ≤2` | `Δ*≤2` | **FPT** `k^{O(k)}n+O(n²)` | Keeney–Lokshtanov (WG 2024) |
| **paths / linear forests** | **`Δ*≤2` ∧ acyclic** | **OPEN** | AAL Problem 4.4 |
| forests | — | **NP-complete** | AAL (arXiv:2402.10782) |

(For oriented graphs rather than tournaments, deciding `Δ*≤k` is NP-complete
for every `k≥1` — Aboulker, Oijid, Petit, Rocton & Simon, arXiv:2407.19270 —
so the tournament structure is essential to the polynomial cases above.)

**The point.** The matching case (Problem 4.4, `C = max-deg ≤1`) is *exactly*
sparse-tournament recognition `Δ*≤1`, hence cubic by DIRT; the `max-deg ≤2`
case is `Δ*≤2`, polynomial (indeed FPT) by Keeney–Lokshtanov. A **linear
forest is precisely a max-degree-2 graph that is also acyclic.** So the open
path case is

> **`Path-FAS = (Δ*(T) ≤ 2) ∧ (some max-back-degree-≤2 order has an acyclic
> back-arc graph)`.**

The first conjunct is decidable in polynomial time (above). The entire residual
difficulty is the **acyclicity refinement** on the `Δ*=2` layer — the one thing
no degreewidth result captures. Everything below is about that residual.

---

## 2. Reformulations of the acyclicity residual

Write `LFO` for the equivalent statement: *some order has `B_≺` a linear
forest.* Two exact, tournament-specific reformulations sharpen `LFO`.

### 2.1 Directed 3/4-cycle transversal

> **Lemma (3/4-cycle).** Let `F ⊆ A(T)` be a linear forest. Then `T−F` is
> acyclic **iff** `T−F` has no directed 3-cycle and no directed 4-cycle.
> Hence **`Path-FAS ⟺ there is a linear forest `F` hitting every directed
> 3-cycle and every directed 4-cycle of `T`.**

*Proof.* If `T−F` has a directed cycle, take a shortest one `C`, of length `ℓ`.
Any chord of `C`, in either orientation, closes a strictly shorter directed
cycle out of `C`-arcs plus that chord; so if a chord were in `T−F` it would
contradict minimality — every chord of `C` lies in `F`. For `ℓ ≥ 6` each
vertex of `C` is incident to `≥ ℓ−3 ≥ 3` chords in `F`, exceeding the
linear-forest degree bound. For `ℓ = 5` the five chords form a 5-cycle inside
`F`, contradicting acyclicity of `F`. So a surviving shortest cycle has length
`3` or `4`. ∎

*Verification.* Lemma checked (linear forest `F`: `T−F` acyclic ⟺ no directed
3/4-cycle) with 0 violations on random `n≤8`; the full equivalence vs the
brute-force decider with 0 disagreements exhaustively over `n≤5`; a witness
(`n=4`, `F = {0→2, 1→3}`) confirms the directed-4-cycle constraints are
necessary, not cosmetic.

*Provenance caveat.* The shortest-cycle/chord argument is a **standard
feedback-arc-set technique**, so the *method* is folklore; the specific
statement for linear-forest `F` (Path-FAS = 3/4-cycle transversal) does not
appear in AAL and is not obvious in its cited FAS references
([Bessy et al., kernels], [Chen–Hu–Zang, min-max]), but those two were checked
only by title/abstract — they should be read before any novelty claim.

### 2.2 The apex-cut CSP (triangle layer)

For a vertex `v` and an unknown linear forest `F`, write `P_v = N_F(v)`; since
`F` is a linear forest, `|P_v| ≤ 2`. Let the **apex-cut graph** `C_v` have an
edge `ab` for each directed triangle `v→a→b→v` (i.e. `a∈N⁺(v)`, `b∈N⁻(v)`,
`a→b`).

> **Apex-cut lemma.** `F` hits every directed triangle iff for every `v`,
> `E(C_v − P_v) ⊆ F` — every cut-arc whose endpoints are not protected at `v`
> is forced into `F`.

This turns generic 3-uniform triangle-hitting into a **finite-domain CSP**:
each vertex chooses `P_v` (`|P_v|≤2`, with `C_v−P_v` a linear forest); symmetry
`u∈P_v ⟺ v∈P_u`; forced-edge implications. `Path-FAS` is then this CSP plus the
two global checks *`F` is a linear forest* and *`F` hits every directed
4-cycle*. (Lemma verified 0/1600; the CSP decider equals the brute-force
Path-FAS decider on all 33 866 tournaments `n≤6`.)

The apex-cut form is a useful diagnostic: arc-consistency alone refutes a large
fraction of certified NO instances (n=9: ~47%) with bounded search elsewhere.
But it is not a polynomial algorithm (see §3), and the triangle CSP is only the
triangle layer — the 4-cycle hitting and the global forest acyclicity remain.

---

## 3. The methods-barrier map

Every standard route to a polynomial algorithm has been pushed and stalls at
the **same** obstruction. We record the routes and the precise reason each
fails; the routes are closed *as routes*, which is **not** a claim that no
polynomial algorithm exists.

| Route | Outcome | Reason |
|---|---|---|
| Forward / score-window DP | **lower bound** | `2^Ω(n)` states (toggle fooling set, D70): the back-arc-forest component *history* explodes; the family lives at `Δ*=2`, so it is an acyclicity obstruction, not a degree one. |
| Polynomial-size prefix DAG (from `Δ*≤2`) | open but blocked | nodes (prefix *sets*) are polynomial, but a path must accumulate a graphic-matroid-independent label set; retaining that connectivity online is the D70 explosion. |
| Cutting-plane / cycle-cut LP | **blocked** | the full directed+undirected cycle-cut LP is feasible-fractional on the vast majority of certified NO instances (20/20 at `n=7`, 546/572 at `n=8`); no Farkas/LP certificate. |
| Matroid intersection / coverage / ISR / rainbow | mismatch | Path-FAS is matroid-*constrained hitting* with *shared* representatives, not an injective independent transversal; linear forests are not a matroid; cycle-hitting are covering lower bounds, not a second independence system. |
| Linear/graphic matroid parity | mismatch | covering disjunctions (`≥1` of 3/4 arcs) are not parity/pairing constraints. |
| Representative families | exponential | the graphic matroid has rank `Θ(n)`; representative-set size is exponential in rank, and the `Δ*≤2` diameter bound gives no rank collapse — D70 is a lower bound against exactly this compression. |
| Apex-cut CSP — AC completeness | **refuted** | many certified NOs survive arc-consistency with an acyclic mandatory-forced graph (witness `8#1079`); local consistency carries no NO information. |
| Apex-cut CSP — bounded width | **fails** | the post-AC variable-interaction (primal) graph can be **complete**, primal treewidth up to `n−1`; no bounded-primal-width DP. |
| Apex-cut CSP — 2-SAT collapse | **fails** | residual constraints (degree-≤2 cardinality, 4-ary 4-cycle clauses, global acyclicity) are not binary bijunctive; domains stay large. |
| Classical paradigms (matroid / LP-integral / finite-forbidden / 2-SAT) | dead | each fails at *undirected acyclicity of the back-arc graph*. Minimal-NO obstruction set is infinite (20 → 572 → 5560 at `n=7,8,9`), so no finite forbidden-subtournament characterization. |
| AAL-style / clause-and-fanout hardness reductions | blocked | the degree-2 budget caps variable fan-out at 2; bounded-occurrence CSPs are polynomial. A genuine 2-in-3 clause gadget exists, but the residual "faithful splitter" (capacity-form Lemma C) survives all `n≤9` checks — no fanout. |

**The single obstruction.** In every language the same object resists:
**the selected/back-arc forest's connectivity and acyclicity is a global
property.** The degree layer (`Δ*≤2`) is local and polynomial; the acyclicity
layer is global. Concretely it surfaces as a *near-complete interaction graph*
(`tw(J) ≈ n` on minimal NOs; complete post-AC apex primal graph) and as the
`2^Ω(n)` forward lower bound. Different encodings relocate this into cleaner
tournament-specific language but do not break it.

---

## 4. What is settled, what is open, what is ours

**Settled (prior art — credited, not claimed):**
- matching / `Δ*≤1` = sparse: cubic (DIRT). This answers the `C=max-deg-1`
  half of AAL Problem 4.4.
- `max-deg ≤2` / `Δ*≤2`: FPT, hence polynomial for fixed `k` (Keeney–
  Lokshtanov).
- forest-FAS: NP-complete (AAL).
- oriented-graph `Δ*≤k`: NP-complete, all `k≥1` (Aboulker et al.).

**Open:** the path case (Path-FAS = `Δ*≤2 ∧` acyclic). Neither `∈ P` nor
NP-hard is known.

**What this note contributes** (subject to the §2.1 provenance caveat): the two
exact reformulations (3/4-cycle transversal; apex-cut CSP) that isolate the
open difficulty to the acyclicity residual on the `Δ*=2` layer, and the
documented barrier map showing the standard toolkit does not resolve it. We
make **no** claim of a complexity result for Path-FAS.

---

## 5. What a resolution would require

- **For `∈ P`:** a *non-forward, global* certificate or construction — the
  forward/local routes are provably or empirically exhausted, and the live
  obstruction is global forest acyclicity over a near-complete interaction.
- **For NP-hardness:** a reduction living inside the restricted class of
  tournament directed-3/4-cycle hypergraphs (bounded local density: ≤2 cyclic
  triangles per 4-set), respecting the degree-2 fan-out cap that has blocked
  every clause-and-fanout attempt so far.
- A natural decisive sub-question: the **expressiveness dichotomy** — which
  3/4-uniform hypergraphs arise as a tournament's directed-3/4-cycle
  hypergraph — which would point the effort toward P or toward hardness.

---

## 6. Reproduction and detailed records

- 3/4-cycle reduction and dead static shortcuts: `docs/q2_nonforward_attack.md`,
  tests in `tests/test_q2_acyclicity_core.py`.
- Apex-cut CSP, AC/width/2-SAT analysis: `docs/q2_apex_cut_attack.md`,
  `scripts/q2_apex_cut_probe.py`.
- Degreewidth context, `Δ*≤2` recognition, prior-art corrections:
  `docs/q1_polynomial_writeup.md`, `docs/q1_degreewidth_recognition.md`,
  `docs/degreewidth_direction.md`.
- Matching-FAS = `Δ*≤1` = sparse (prior art): `README.md`, `docs/lemmas.md`.
- Forward-DP lower bound: `docs/forward_dp_lower_bound.md`; cutting-plane:
  `docs/cutting_plane_audit_status.md`; literature scope:
  `docs/q2_literature_scope_independent_transversal.md`;
  full landscape: `docs/LANDSCAPE.md`.

**References.**
- P. Aboulker, G. Aubian, R. Lopes. *Finding forest-orderings of tournaments
  is NP-complete.* arXiv:2402.10782. (Problem 4.4; forest-FAS NP-complete.)
- T. Davot, L. Isenmann, S. Roy, J. Thiebaut. *Degreewidth: a New Parameter for
  Solving Problems on Tournaments.* arXiv:2212.06007 (WG 2023). (Sparse =
  degreewidth 1, cubic; computing degreewidth NP-hard.)
- R. Keeney, D. Lokshtanov. *Degreewidth on Semi-Complete Digraphs.* WG 2024.
  (FPT degreewidth, `k^{O(k)}n+O(n²)`; oriented `Δ*≤2` NP-hard.)
- P. Aboulker, B. Oijid, R. Petit, M. Rocton, A. Simon. *Computing the
  degreewidth of a digraph is hard.* arXiv:2407.19270 (DMTCS 2026).
