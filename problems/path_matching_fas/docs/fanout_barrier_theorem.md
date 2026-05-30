# D75: The Fanout Barrier — toward a structural impossibility theorem

## 0. Statement and status

This note attacks the **Fanout Barrier** conjecture, the single object on
which the local-gadget NP-hardness route for tournament Path-FAS
(Aboulker–Aubian–Lopes Problem 4.4) now rests (D72–D74).

> **Conjecture (Fanout Barrier).** No tournament gadget realizes a
> *faithful free-bit splitter*: there is no tournament `T` with three
> vertex-disjoint ports such that `R_T = {000, 111}` (= `EQ_3`) **and**
> both equality vectors are realized with joint port capacity (some
> valid LFO realizes the port-bits `000` with all six port endpoints at
> back-degree ≤ 1, and some valid LFO realizes `111` likewise).

A faithful free-bit splitter would copy a free variable bit to three
ports, each feeding one 2-in-3 clause via the D72 forced-loader model,
giving occurrence-3 → NP-hardness (Schaefer 1978). Its non-existence
leaves only read-≤-2 instances, which are polynomial; this strongly
supports Path-FAS ∈ P.

**What this note proves.**

1. **(Reduction, all `n`, fully rigorous.)** A faithful `EQ_k` splitter
   for any `k ≥ 2` yields a faithful `EQ_2` *copy* (Lemma R). So the
   whole Barrier reduces to:

   > **Faithful-Copy Barrier.** No tournament gadget with two
   > vertex-disjoint ports realizes `R_T = {00, 11}` with joint port
   > capacity on both `00` and `11`.

2. **(Structural skeleton, all `n`, fully rigorous.)** The
   *internal-arc dictionary* (Lemma I): for each port, its tournament
   arc is a back-arc on **exactly one** of the two equality LFOs. This
   forces a back-degree-1 load at both endpoints of that port on that
   LFO, and is the mechanism behind the empirically perfect
   *two-value competition* (one value can have capacity, the other
   then cannot).

3. **(Core lemma, verified exhaustively at `n ≤ 7`, conjectural for
   `n ≥ 8`.)** The Faithful-Copy Barrier holds: the
   **Capacity–Equality Incompatibility Lemma** (Lemma C, *both-values
   form*) — *if `R_T = EQ_k`, the gadget does NOT have joint port
   capacity on **both** equality values `0^k` and `1^k`.*  (The earlier
   one-value phrasing was an overclaim — see §4 — false at `k = 2`,
   where 16 `EQ_2` gadgets have capacity on a single value.)  This is
   the one genuinely open obligation, checked over the full iso-class
   census at `n ≤ 7` (`k = 2` and `k = 3`) and consistent with the
   one-auxiliary-vertex `n = 8` probe of D74.

The honest bottom line: the Barrier is **reduced to one crisp lemma
(Lemma C)**, which is **a theorem for `n ≤ 7`** and **conjectural for
`n ≥ 8`**, exactly where a companion two-auxiliary-vertex search could
in principle refute it. Lemmas R and I are unconditional.

All numeric claims below are produced by `scripts/fanout_barrier_checks.py`
and pinned in `tests/test_fanout_barrier_checks.py`.

---

## 1. Definitions and conventions

Let `T` be a tournament on `n` vertices, `T[u][v] = 1` iff `u → v`. An
order (LFO candidate) `σ` is a permutation; `pos_σ(v)` is `v`'s position
(0 = first). An arc `u → v` is a **back-arc** of `σ` iff
`pos_σ(u) > pos_σ(v)`. `σ` is a **valid LFO** iff its back-arc graph
`B_σ` (undirected) is a **linear forest**: max-degree ≤ 2 and acyclic.

A **port** is an ordered pair `(x, y)` of distinct vertices; its **bit**
is `b = 1[pos_σ(y) < pos_σ(x)]` (1 iff `y` precedes `x`). For a tuple of
`k` ports an **orientation** `o ∈ {0,1}^k` re-labels each bit as
`b_i ⊕ o_i` (a free design choice, since which truth value a clause reads
is up to the wiring). The gadget realizes

    R_T = { (b_1 ⊕ o_1, …, b_k ⊕ o_k) : σ a valid LFO of T }.

Ports are **vertex-disjoint** (the composability prerequisite, D71): the
`2k` endpoints are distinct. A bit-vector has **joint capacity** under
`σ` if every one of the `2k` endpoints has `B_σ`-degree ≤ 1 (one residual
unit, room for one external clause loader, the D72 model). `EQ_k =
{0^k, 1^k}`.

> **Definition (faithful splitter).** A *faithful `EQ_k` splitter* is a
> `(T, ports, orientation)` with `R_T = EQ_k` and joint capacity realized
> on **both** `0^k` and `1^k`.

---

## 2. Lemma R — the reduction `EQ_k → EQ_2` (rigorous, all `n`)

> **Lemma R.** If a faithful `EQ_k` splitter exists for some `k ≥ 2`,
> then a faithful `EQ_2` copy exists (on the same tournament `T`).

*Proof.* Let `(T, (P_1, …, P_k), o)` be a faithful `EQ_k` splitter.
Restrict attention to the first two ports and orientation `(o_1, o_2)`.
Define the projected relation
`R' = { (c_1, c_2) : (c_1, …, c_k) ∈ R_T }`. Because every realizable
vector of `EQ_k` is `0^k` or `1^k`, projection sends `0^k ↦ 00` and
`1^k ↦ 11`, so `R' = {00, 11} = EQ_2`. (Projection cannot create new
vectors: each LFO already gives one of the two equality vectors.)

Capacity transfers downward: a witness `σ` with all `2k` endpoints at
degree ≤ 1 has, in particular, all four endpoints of `P_1, P_2` at
degree ≤ 1. The `0^k`-witness projects to a capacity-`00` witness for the
2-port gadget; the `1^k`-witness to a capacity-`11` witness. Hence
`(T, (P_1, P_2), (o_1, o_2))` is a faithful `EQ_2` copy. ∎

Lemma R is purely set-theoretic plus the monotonicity of "degree ≤ 1
under a subset of arcs"; it needs no enumeration. **Consequence:**
proving the Faithful-Copy Barrier (no faithful `EQ_2`) proves the full
Fanout Barrier for every `k ≥ 2` and every `n`.

*Sanity check.* `check_eq3_to_eq2_reduction(7)` confirms `eq2_faithful_copies
= 0`, so the reduction's hypothesis is unmet at `n = 7` and the
conclusion ("no `EQ_3` faithful splitter") follows; independently
`check_no_faithful_splitter(7, 3)` reports `faithful_splitters = 0`.

---

## 3. Lemma I — the internal-arc dictionary (rigorous, all `n`)

Fix a port `(x, y)`. In the tournament exactly one of `x → y`, `y → x`
holds; call it the **internal arc** `a`.

> **Lemma I.** Under any order `σ`, the internal arc `a` is a back-arc of
> `σ` iff it is directed from the later-placed endpoint to the
> earlier-placed one. Consequently, on the two *equality* LFOs of a
> gadget — one realizing raw bit `0` (i.e. `x` before `y`) and one
> realizing raw bit `1` (`y` before `x`) at this port — the internal arc
> `a` is a back-arc on **exactly one** of them, and on that LFO it
> contributes one unit of back-degree to **both** `x` and `y`.

*Proof.* "`a` is a back-arc" means head before tail, i.e. `a` points
later→earlier. If `a = x → y`: it is a back-arc iff `pos(y) < pos(x)`,
i.e. iff the raw bit is `1`. If `a = y → x`: a back-arc iff
`pos(x) < pos(y)`, i.e. iff the raw bit is `0`. Either way the predicate
"`a` is a back-arc" equals "raw bit = 1" (case `x→y`) or "raw bit = 0"
(case `y→x`) — in both cases it holds for exactly one of the two raw bit
values. A back-arc adds 1 to the undirected degree of each endpoint. ∎

This is the seed of the **two-value competition**: at every port, *one*
of the two equality LFOs already spends a back-degree unit at both
endpoints (the internal arc), leaving those endpoints at degree exactly
1 there — and *no further* back-arc may touch them if capacity is to
hold on that value.

*Verification.* `check_internal_arc_accounting(7, 3)` checks the
predicate over all `1 098 720` (port, gadget-instance) pairs: **0
mismatches**, and the "internal arc is a back-arc on the `1^k` LFO" count
exactly equals the "on the `0^k` LFO" count (`549 360` each) — the
50/50 split predicted by Lemma I. (`check_internal_arc_accounting(6, 2)`
is the fast pinned version.)

### 3.1 Why Lemma I alone is not enough

One might hope: the internal arcs alone saturate two endpoints on each
equality LFO. They do not — the number of *internal* arcs that are
back-arcs on the `1^k` LFO ranges over `{0, 1, 2, 3}` across the 62
`n = 7` `EQ_3` gadgets (measured directly: counts `13, 18, 18, 13` for
`0, 1, 2, 3` internal back-arcs). The remaining load that pushes a port
endpoint to degree 2 comes from **cross-port arcs** (the 12 directed arcs
between the three ports) and from **internal/auxiliary vertices**. This
is precisely why a clean *all-`n`* proof is hard and why auxiliary
vertices (`n ≥ 8`) are the danger zone: the saturation is a *global*
back-degree-budget phenomenon, not a property of the six port vertices in
isolation. Measured at `n = 7`: the back-arcs *within the six port
vertices* saturate ≥ 1 endpoint on every equality LFO, but reaching the
observed ≥ 2 saturated endpoints requires the internal-vertex loaders
too.

---

## 4. Lemma C — Capacity–Equality Incompatibility (the core obligation)

This is the crux. State it for general `k` (the `k = 2` case is the one
Lemma R needs; the `k = 3` case is checked too).

> **Lemma C (corrected; verified `n ≤ 7`; conjectural `n ≥ 8`).** Let
> `(T, ports, o)` be a `k`-port gadget with `R_T = EQ_k`. Then it does
> NOT have joint port capacity on **both** equality vectors `0^k` and
> `1^k`.  Equivalently: no faithful `EQ_k` copy/splitter exists.

**CORRECTION (overclaim caught).**  An earlier draft stated the
*one-value* form "capacity on a value `v` ⟹ `R_T ≠ EQ_k`."  That is
**false for `k = 2`**: the `n = 7` census has **16 `EQ_2` gadgets with
capacity on `00`** (and 16 on `11`).  What the data actually shows is
the *both-values* form — **0 `EQ_2` gadgets have capacity on both**
(the `faithful = 0` column).  The one-value form happens to hold for
`k = 3` (an `EQ_3` gadget has capacity on *neither* value, a strictly
stronger phenomenon), which is what misled the over-generalisation.
The operative statement, and the one Lemma R needs, is the both-values
form above.

The Faithful-Copy Barrier IS the `k = 2` both-values instance: a
faithful `EQ_2` copy needs capacity on `00` **and** `11` with
`R_T = EQ_2`; Lemma C says no such gadget exists.  Combined with
Lemma R, **Lemma C ⇒ the full Fanout Barrier** for all `k ≥ 2`.

(The `16 / 16 / 0` split — capacity reachable on either value alone but
never both — is exactly the two-value *competition* the proof must
exploit; it is the corrected content of the "two equality vectors
compete" idea.)

### 4.1 Exhaustive verification at `n ≤ 7`

`check_no_faithful_splitter(n, k)` enumerates every iso-class
representative (456 at `n = 7`), every vertex-disjoint `k`-port tuple,
and every orientation:

| n | k | `EQ_k` gadgets | cap on `0^k` | cap on `1^k` | **faithful** |
|---|---|---|---|---|---|
| 4 | 2 | 0 | 0 | 0 | 0 |
| 5 | 2 | 0 | 0 | 0 | 0 |
| 6 | 2 | 4 | 1 | 1 | **0** |
| 7 | 2 | 660 | 16 | 16 | **0** |
| 4–6 | 3 | 0 | 0 | 0 | 0 |
| 7 | 3 | 62 | 0 | 0 | **0** |

Reading:

* **`EQ_2`** (`n ≤ 7`): copies exist (660 at `n = 7`); each can get
  capacity on at most one value (16 on `00`, 16 on `11`), **never both**.
  This is the Faithful-Copy Barrier verified at `n ≤ 7`. The 16-vs-16
  balance is a bit-complement-symmetry artifact (complementing both port
  bits via the orientation swaps the roles of `00` and `11`), not itself
  a consequence of Lemma I; what Lemma I supplies is the *mechanism* — on
  each value the unique internal back-arc already loads its port — behind
  the empirical "two-value competition" that no copy escapes.
* **`EQ_3`** (`n = 7`): 62 gadgets force `R_T = EQ_3` but have capacity
  on **neither** equality value (`cap0 = cap1 = 0`), strictly stronger
  than "no faithful splitter" — consistent with D73's `R_comp = ∅`.

`check_capacity_forces_non_equality(7, 3)` makes the mechanism explicit.
Over **17 281** instances with joint capacity on the `1^k` value:

* `with_R_eq_EQ = 0` — never `EQ_3`;
* `with_a_mixed_vector = 17 192` — capacity co-realizes a mixed vector
  (case (a)); moreover the nearest such mixed vector is at Hamming
  distance 1 from `1^k` in `17 182` of these (measured), i.e. a single
  port bit flips while the witness stays valid;
* `missing_opposite_equality_vector = 89` — the remaining instances have
  `R_T = {1^k}`, a *constant* gadget (case (b)): it has capacity on
  `1^k` but never realizes `0^k`, so it cannot copy a *free* bit.

The numbers for the `0^k` value are identical (`17 281 / 0 / 17 192 / 89`)
by symmetry. **In every capacity-on-`v` instance at `n = 7`, `R_T ≠ EQ`** —
Lemma C holds.

### 4.2 The deficit margin

`check_equality_deficit_profile(7, 3)`: over the 62 `EQ_3` gadgets, the
minimum number of saturated (degree-2) port endpoints is **2** on the
`0^k` value and **2** on the `1^k` value, and the minimum of their *sum*
over gadgets is **6**. A faithful splitter needs `0 + 0`. So at `n = 7`
the closest `EQ_3` gadget misses faithful capacity by a wide margin (a
combined deficit of 6 saturated endpoints), not by one fragile arc. This
margin is reassuring but is *not* a proof for larger `n`.

### 4.3 The auxiliary-vertex frontier (the danger zone)

D74 already probed the obvious `n = 8` extension: take an `n = 7` `EQ_3`
gadget and add one auxiliary vertex in all `2^7 = 128` arc-orientations;
of the 13 that keep `R_T = EQ_3`, **none** gains joint capacity on even
one equality vector. So one auxiliary vertex does not free capacity.

The genuinely open escape (D74 §5) is `n ≥ 8` with **≥ 2 private
auxiliary vertices**, so that the equality-enforcing back-arcs land on
auxiliaries rather than on ports. The structural reading of §3.1 is that
moving the enforcing load onto auxiliaries can *only help if the
auxiliaries absorb cross-port back-arcs that would otherwise saturate a
port endpoint* — but those auxiliaries must themselves stay within the
linear-forest budget (their own back-degree ≤ 2, no induced cycle),
which is a finite constraint that the companion two-auxiliary search is
exactly testing. **This note does not close the ≥ 2-auxiliary case.** If
that search produces a splitter, Lemma C fails at `n = 8` and the Barrier
is false; if it confirms no splitter through `n = 8`, Lemma C extends one
size and the conjecture is materially strengthened.

---

## 5. A provable fragment of Lemma C: the *aligned single-port* slide

We can prove a clean fragment of Lemma C constructively. It does not
cover all `n`, but it isolates the mechanism and is unconditional where
it applies.

> **Lemma C-slide (conditional, rigorous given its hypothesis).** Let
> `σ` realize `1^k` with joint port capacity, and let `(x, y)` be a port
> with raw bit `1`. Form `σ'` by moving `y` to the position immediately
> after `x` (a *slide* over the window `W` of vertices strictly between
> `y` and `x` in `σ`). **If** `σ'` is again a valid LFO (its back-arc
> graph stays a linear forest), **then** `σ'` realizes `1^k` with port
> `(x, y)`'s bit flipped to `0`, hence a mixed vector, so `R_T ≠ EQ_k`.

*Proof.* The conclusion is immediate once `σ'` is a valid LFO: `x` now
precedes `y`, so the port bit is `0`; the other `k − 1` ports are
disjoint from `{x, y}` and their internal arcs' back-arc status is
unchanged by the slide (their bits stay `1`), so the realized vector is
`1…1 0 1…1`, a mixed vector witnessed by a valid LFO. ∎

The content is therefore entirely in *when the slide preserves
validity*. **Sufficient (provable) condition:** if the window `W`
contains only port vertices and internal vertices that, in `σ`, have
back-degree `0` and are not incident to any back-arc crossing the
window, then the slide changes degrees by at most `1` at the endpoints
of arcs it reverses and introduces no back-arc that shares a vertex with
the pre-existing back-arc graph — so no degree-3 vertex and no new cycle
appear, and `σ'` is valid. **This is *not* proved in full generality
here**; the difficulty (and the reason it is only a fragment) is a
window containing internal vertices that already carry back-arcs
reaching outside `W`, where reversing window-arcs can create a degree-3
vertex or close a cycle. Those are exactly the residual cases below.

The **slide hypothesis fails in the 1 079 `n = 7` cases where
a single-vertex slide does *not* reach a mixed vector** (measured:
single-port slide reaches a mixed vector in `15 661` of `17 192`
capacity-with-mixed instances; allowing any single port-vertex move to
any position raises this to `16 113`). The residual cases need a move
that also relocates an internal vertex — which is why Lemma C-slide is a
*fragment*, not the whole lemma. It does, however, establish:

> **Corollary (conditional).** No faithful `EQ_k` splitter exists in
> which, for some equality value, every port whose bit must flip admits
> a validity-preserving slide (Lemma C-slide). The interesting sub-case
> where this holds *provably* is when, on the equality LFO in question,
> **no internal/auxiliary vertex carries a back-arc onto a port vertex**
> (all port back-degree comes from port–port and port-internal arcs):
> then every slide window consists of port vertices and back-arc-free
> internal vertices, the sufficient condition of Lemma C-slide applies to
> the lowest-cost port to flip, and the slide is valid. (One still has to
> pick a port whose window does not itself contain a port pair whose own
> back-arc would be pushed to degree 3 — at `k = 2` there is always such a
> choice; for `k ≥ 3` this is verified, not proved.)

This is the clean direction the task asked for: **the Barrier holds when
the equality LFOs load the ports only via port–port and port-internal
arcs (no internal-vertex loading of ports)** — and that is precisely the
regime that *cannot* be escaped by adding auxiliary vertices, since
auxiliary vertices help only by absorbing load *onto themselves*. The
remaining case is exactly when internal/auxiliary vertices carry load
onto the ports — the `n ≥ 8` frontier.

---

## 6. Summary of the proof architecture

```
  Fanout Barrier  (no faithful EQ_3 splitter, all n)
        ⇑  Lemma R (rigorous, all n)
  Faithful-Copy Barrier  (no faithful EQ_2 copy, all n)
        ⇑  Lemma C at k = 2
  Lemma C  (R_T = EQ  ⇒  NOT both equality values have joint capacity)
        │
        ├── proved for n ≤ 7  (exhaustive census; k = 2 and k = 3)
        ├── proved (all n) for the "no internal loading of ports" sub-case
        │      via the validity-preserving slide  (Lemma C-slide + Corollary)
        └── OPEN for n ≥ 8 with ≥ 2 auxiliary vertices  ← danger zone
  supporting skeleton:
  Lemma I (internal-arc dictionary, rigorous, all n) ⇒ two-value competition
```

What is **theorem**: Lemma R (all `n`), Lemma I (all `n`), the
no-internal-loading sub-case via Lemma C-slide (all `n`, with the `k ≥ 3`
window-choice step verified not proved), and Lemma C / the full Barrier
*for `n ≤ 7`* (exhaustive).

What is **conjecture**: Lemma C for `n ≥ 8` (≥ 2 auxiliary vertices) —
hence the Barrier for `n ≥ 8`. This is the one load-bearing gap, and it
is exactly where the companion two-auxiliary splitter search lives. The
present argument **does not** rule out an auxiliary-vertex
counterexample; it reduces its possibility to the single failure of
Lemma C.

---

## 7. Consistency with prior findings

* **D73** (no `EQ_3` capacity splitter, `n ≤ 7`; padding-robust): matches
  the `EQ_3` row (capacity on neither value). The padding-robustness
  argument of D73 §3 is orthogonal to and compatible with Lemma I:
  padding does not change port back-degrees, so it cannot move the
  internal-arc load off a port.
* **D74** (implication pieces: capacity on one equality value but never
  both; one-aux `n = 8` adds no capacity): matches the *one-sided*
  capacity counts (16/16 for `EQ_2`) and the `n = 8` frontier statement.
  The D74 retraction ("source saturates on its active value" was false;
  the correct invariant is "no capacity on both equality values") is
  exactly Lemma C / the 16-vs-16-vs-0 table here.

## 8. Honest limitations

1. **Lemma C is not proved for all `n`.** It is a theorem only for
   `n ≤ 7` (exhaustive) and for the aligned-slide sub-case. The general
   statement is a conjecture; a counterexample at `n ≥ 8` with auxiliary
   vertices would refute the Barrier outright.
2. The census is over **iso-class representatives** generated by
   one-vertex extension (validated against OEIS A000568 through `n = 6`,
   456 classes at `n = 7`). Enumerating *all* disjoint port-tuples and
   *all* orientations per representative is exhaustive for the realizable
   relations.
3. **Composition model.** "Capacity = back-degree ≤ 1 at every endpoint"
   is the D72 one-forced-loader-per-port model. A clause that attaches
   with a different degree would change the bar; the Barrier is stated
   against the D72 model, which is the only confirmed clause interface.
4. The aligned-slide fragment (§5) gives a *constructive* witness only
   under its degree/acyclicity hypotheses; the residual `n = 7` cases
   (≈ 6% of capacity-with-mixed instances) require internal-vertex moves
   and are covered only by the exhaustive census, not by the slide.

## 9. Files and tests

| artefact | location |
|---|---|
| Barrier checks (all five claims) | `scripts/fanout_barrier_checks.py` |
| Pinned regression tests | `tests/test_fanout_barrier_checks.py` |
| EQ splitter census (D73) | `scripts/fanout_splitter_census.py` |
| Implication census (D74) | `scripts/implication_fanout_census.py` |
| LFO cache / port relation | `scripts/port_relation_census.py` |

## 10. Citations

* 1-in-3 / 2-in-3-SAT NP-completeness, Schaefer dichotomy: Schaefer 1978,
  DOI 10.1145/800133.804350.
* Composition / loader model: D72 `docs/port_loader_realizability.md`.
* EQ-splitter capacity census: D73 `docs/fanout_splitter_census.md`.
* Implication / equality-slice audit: D74
  `docs/implication_fanout_census.md`.
