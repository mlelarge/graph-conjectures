# D75: Two-auxiliary-vertex EQ_3 splitter search — the last fanout escape hatch

## 0. Result

This note runs the decisive escape-hatch experiment that D74 left open
(its §5 "Open (n >= 8, >= 2 auxiliary vertices)" item): can **two
auxiliary vertices**, added to an n = 7 EQ_3 base gadget and made part of
the equality-enforcing mechanism (not inert padding), produce a
**faithful free-bit splitter** — a tournament realizing

    R_T = EQ_3 = { 000, 111 }

on three vertex-disjoint ports, with **joint output capacity on BOTH
equality vectors**: some realizing LFO of 000 and some of 111, each
leaving all six port endpoints at back-degree <= 1, so each port can
still accept one D72-style clause loader?

**Verdict: no.**  Across the full searched scope — all 31 distinct n = 7
EQ_3 base gadgets (up to port-respecting isomorphism), each extended by
two auxiliary vertices in every one of the 2^15 = 32768 arc-orientations,
plus a structured pure-auxiliary-coupling topology — **5900 of the
1,015,808 brute extensions keep R_T = EQ_3, and NONE gains joint capacity
on even one equality vector**, let alone both.  The two auxiliaries do
not free the port endpoints.

This **extends the Fanout Barrier evidence** from the n = 7 census (D73)
and the one-auxiliary extension (D74) to the two-auxiliary regime over an
n = 7 base.  It is strong support for — but, as always, not a proof of —
the conjecture that tournament Path-FAS admits no faithful free-bit
splitter, hence no NP-hardness reduction via the D72 clause gadget.

## 1. Why this is the decisive experiment

The hardness route after D72 is fully localized:

  * D72: a genuine exactly-2-in-3 **clause** gadget exists.  A 2-in-3-SAT
    reduction needs only **fanout** — copying one free variable bit to
    >= 3 clauses.
  * Sharing one port pair across 3 clauses is degree-blocked (each clause
    loader consumes back-degree at the same endpoints; the linear-forest
    budget caps each vertex at back-degree 2).
  * The only escape is a **splitter**: a gadget realizing EQ_3 on three
    *disjoint* ports with residual capacity at all six endpoints on both
    equality vectors, so the bit can be read by three independent
    clauses.
  * D73: at n <= 7, EQ_3 gadgets have R_comp = empty — capacity on
    NEITHER equality vector — and top/bottom padding cannot change a port
    back-degree.
  * D74: a forward split (x -> y, z) can get joint capacity on 111, a
    reverse split (y, z -> x) on 000, but no single piece on BOTH; and a
    **one**-auxiliary extension of a pinned n = 7 EQ_3 gadget (13 of 128
    orientations keep EQ_3) gains capacity on neither.

D74 §5 names the precise remaining hole: **two private auxiliary
vertices**, positioned so the equality-enforcing back-arcs land on the
auxiliaries rather than on the ports, freeing the port endpoints to
retain capacity.  The structural Fanout Barrier (D74 §4) predicts this
fails — a propagated bit's carrier is a sub-path of the max-degree-2
back-arc graph, with only two endpoints, so occurrence <= 2 — but the
prediction is unproven, and the auxiliary route is exactly where it could
break.  This note tests it exhaustively over the n = 7 base.

## 2. The search object

A **two-aux extension** of an n = 7 EQ_3 base gadget G (with disjoint
ports P and orientation o) is a 9-vertex tournament T:

  * the induced sub-tournament on the 7 base vertices equals G;
  * the two auxiliary vertices 7, 8 have **arbitrary** orientations on
    every arc incident to them — both the aux-aux arc {7,8} and all
    2 x 7 = 14 aux-base arcs — giving 2^15 = 32768 extensions per base.

The auxiliaries are therefore NOT padding: an auxiliary may point into a
port (loader-like, raising a port's back-degree) or be pointed at
(sink-like, absorbing back-arcs), or interconnect.  This fully covers the
"auxiliaries absorb the equality back-arcs" hypothesis for the on-top
construction.

For each extension we compute, over all valid LFOs:

    R_T   = { oriented port-bit vector of sigma : sigma a valid LFO of T }
    joint = { b in R_T : some witness LFO leaves all six port endpoints
                         at back-degree <= 1 }

and ask whether R_T = EQ_3 and EQ_3 ⊆ joint (faithful splitter) or at
least joint ∩ EQ_3 != empty (capacity on one equality vector).

## 3. Optimizations

The brute object is 31 bases x 2^15 extensions, each an n = 9 LFO
problem.  A naive n! brute LFO enumeration is ~4.4 s per n = 9
tournament, so the naive cost is ~31 x 32768 x 4.4 s ≈ 50 days.  Four
optimizations bring it under half an hour.

**(1) Pruned backtracking LFO enumerator (`enum_lfos_deg`).**  Instead of
checking all 9! orders, build the order left to right.  When vertex x is
appended after the placed prefix, its new back-arcs are exactly x -> p
for already-placed p with an arc x -> p; if adding them pushes any
endpoint to back-degree > 2 or closes an undirected cycle (union-find),
no completion repairs it, so the prefix is pruned.  Measured ~12 ms per
n = 9 tournament — a ~350x speedup.  **Validated against the brute-force
enumerator** on random n = 7 tournaments (exact set equality of LFO
position-vectors) and on back-degree vectors against the verifier.

**(2) Early R_T rejection (`_relation_joint_with_eq_pruning`).**  Most of
the 2^15 extensions do not realize EQ_3.  The enumerator aborts the
moment any completed LFO yields a port vector outside {000,111} (after
orientation): such a vector proves R_T != EQ_3, so the extension is
rejected without enumerating its remaining LFOs.  Extensions whose R_T is
a strict subset of EQ_3 (e.g. only {000}) never abort but are rejected by
the final `R != EQ3` test; extensions with no valid LFO yield R = empty
and are rejected.  All three rejection cases are sound.

**(3) Multiple base gadgets (`collect_eq3_bases`).**  Rather than the one
pinned constant, every distinct n = 7 (T, ports, orient) realizing
R_T = EQ_3 is collected over all 456 iso-class representatives, all
disjoint 3-port-tuples, and all 2^3 orientations, then normalized so the
ports occupy fixed positions (0,1),(2,3),(4,5) and deduplicated by the
resulting labeled matrix.  This yields **31 distinct labeled base
gadgets** — every n = 7 EQ_3 gadget up to port-respecting isomorphism.

**(4) Structured pure-auxiliary-coupling search
(`structured_compose_search`).**  A complementary topology that does NOT
reuse a pre-existing n = 7 EQ_3 sub-gadget: three disjoint ports with the
six port vertices held at a fixed transitive baseline (forcing NO port
relation on their own), two auxiliaries 6, 7 with all arcs incident to
them free (the aux-aux arc plus 2 x 6 aux-port arcs = 13 free arcs,
2^13 = 8192 masks), and a top-padding vertex 8 (every vertex -> 8, arcs
fixed) that raises the auxiliary score windows so an auxiliary can act as
a *forced* router/loader (cf. D72's score-window separation, gap >= 5).
Here the **only** mechanism that can force equality is the auxiliary
coupling — the literal D74 §5 escape.

Parallelism: the 31 bases are independent, run across 12 fork-based
worker processes.  Wall time ~30 minutes (the pinned base alone is ~8
min serially; the full 31-base sweep finishes in ~30 min on 16 cores).

## 4. Scope and results

### 4.1 Single-base anchors (independently confirmed serially)

| base | n_aux | extensions | R_T = EQ_3 kept | one-equality capacity | both-equality capacity |
|---|---|---|---|---|---|
| pinned D74 gadget | 1 | 128 | 13 | 0 | 0 |
| pinned D74 gadget | 2 | 32768 | 220 | **0** | **0** |

The pinned-gadget two-aux run (220 EQ_3-preserving extensions, zero
capacity on either equality vector) was computed once serially (471 s)
and once inside the parallel sweep; the two agree.  Note the jump from 13
EQ_3-preserving extensions (one aux) to 220 (two aux): the second
auxiliary gives the equality mechanism far more room, yet capacity stays
at exactly zero.

### 4.2 Full sweep over all 31 bases

| quantity | value |
|---|---|
| distinct n = 7 EQ_3 bases | 31 |
| extensions per base | 32768 |
| total extensions enumerated | 31 x 32768 = 1,015,808 |
| extensions keeping R_T = EQ_3 | **5900** |
| with joint capacity on one equality vector | **0** |
| with joint capacity on both {000,111} | **0** |

Per-base EQ_3-preserving counts vary structurally (84, 154, 188, 202,
216, 220, 240 across the 31 bases) — the bases are genuinely different
equality mechanisms, not relabelings of one — yet every single one has
**zero** capacity on either equality vector.

### 4.3 Structured pure-coupling topology

| quantity | value |
|---|---|
| topology | 3 ports (transitive baseline) + 2 aux + 1 top-pad |
| extensions enumerated | 2^13 = 8192 (arcs incident to the 2 aux, PAD fixed) |
| extensions keeping R_T = EQ_3 | **0** |
| with capacity on one / both equality vectors | **0 / 0** |

With the inter-port arcs held transitive (so they force no port
relation) and only the two auxiliaries free, no orientation even forces
R_T = EQ_3 — two auxiliaries cannot enforce all-equality on three
disjoint ports *through coupling alone*, let alone with residual
capacity.  (The brute sweep covers the on-top construction where the
base sub-gadget already enforces EQ_3; this structured sweep covers the
complementary case where the auxiliaries must do the enforcing, and they
cannot.)

Across **every** searched configuration, no two-auxiliary EQ_3 gadget has
joint output capacity on even one equality vector.

## 5. What a positive find would have required (and how it is checked)

`verify_splitter(T, ports, orient)` is the independent acceptance gate
for any positive find, routing through the brute-force LFO enumerator
(the trust root `valid_lfos` / `verify`), NOT the fast enumerator.  A
claimed splitter must pass ALL of:

  1. T is a valid tournament (exactly one arc per pair, no self-loops);
  2. the three ports are pairwise vertex-disjoint (six distinct
     vertices);
  3. R_T = {000,111} on the ports under the orientation, computed from
     the brute-force LFO set;
  4. some LFO realizes 000 with all six port endpoints at back-degree
     <= 1, AND some LFO realizes 111 likewise (joint capacity on both
     equality vectors).

No extension reached gate 4 on either equality vector, so the gate never
fired positively.  Its accept path is exercised in the tests by the
structural decomposition check, and its reject path by the bare gadget
(R_T = EQ_3 but no capacity).  This guards against the census artifacts
that have previously bitten this project: shared-vertex ports
(gate 2), orientation bugs (gate 3 uses the explicit orientation), and
lenient-vs-strict capacity confusion (gate 4 requires an actual
per-endpoint degree witness, not a relation-level shadow).

## 6. Honest scope statement

**Established by this note (the precise negative).**  No faithful free-bit
EQ_3 splitter arises from:

  * any of the 31 n = 7 EQ_3 base gadgets (all such gadgets up to
    port-respecting isomorphism),
  * extended by exactly two auxiliary vertices,
  * in any of the 2^15 arc-orientations incident to those auxiliaries,
  * nor from the structured pure-auxiliary-coupling topology on 9
    vertices with a transitive inter-port baseline.

Over 1,015,808 + 8192 enumerated extensions, **5900 keep R_T = EQ_3 and
zero have joint capacity on even one equality vector**.

**NOT established (what remains open).**  This is **not** a proof of the
Fanout Barrier.  The search does not cover:

  * **bases other than n = 7**: a 9-vertex EQ_3 gadget whose induced
    7-vertex sub-tournament does NOT itself realize EQ_3 (the equality is
    enforced jointly by base + aux) is only partly covered — the
    structured topology probes one such family (transitive inter-port
    baseline), but not all n = 9 EQ_3 gadgets, which would require a
    full n = 9 census (2^36 labeled / ~6880-ish iso-classes restricted to
    EQ_3, future work);
  * **>= 3 auxiliary vertices** / n >= 10;
  * **non-EQ faithful mechanisms**: a faithful free-bit copy must realize
    EQ on both values (D74 §2), so EQ is the right target, but a gadget
    realizing a larger relation that *projects* to a faithful copy under
    composition is not ruled out here.

So the honest read is: **no two-aux splitter exists over an n = 7 EQ_3
base (and the one structured n = 9 coupling family)** — which closes the
specific escape D74 §5 flagged for the n = 7 base, and adds substantial
weight to the Fanout Barrier conjecture, while leaving the all-sizes
statement to the companion proof effort.

The companion agent is attempting to PROVE the Fanout Barrier (no
faithful splitter at any size) from the max-degree-2 structure.  This
note's exhaustive negative over the most natural escape topology is
consistent with that theorem; had it found a splitter, the theorem would
be false, so the negative is the supporting (not deciding) evidence.

## 7. Files and tests

| artefact | location |
|---|---|
| Two-aux search (enumerator, base collection, brute + structured) | `scripts/two_aux_eq3_search.py` |
| Independent verifier of a positive find | `scripts/two_aux_eq3_search.py` (`verify_splitter`) |
| Tests (enumerator-vs-brute, base count, pinned no-capacity, verifier) | `tests/test_two_aux_eq3_search.py` |
| One-aux baseline (D74) | `scripts/implication_fanout_census.py` |
| EQ_3 no-capacity census (D73) | `docs/fanout_splitter_census.md` |
| 2-in-3 clause gadget (D72) | `docs/port_loader_realizability.md` |

## 8. Citations

  * 1-in-3 / 2-in-3-SAT NP-completeness: Schaefer 1978,
    DOI 10.1145/800133.804350.
  * Degree-2 / wire-saturation barrier: Theorem 5.1,
    `docs/J_hardness_via_wires.md`.
