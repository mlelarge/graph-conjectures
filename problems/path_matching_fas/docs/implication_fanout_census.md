# D74: Implication-style fanout census

## 0. Why and what

D73 ruled out EQ-style (all-equal) capacity splitters at n ≤ 7
(padding-robust), but only for the all-equal relation, which forbids 6
of 8 vectors and saturates the ports.  Implication relations forbid
only 3 vectors, so they load the ports less and might retain capacity.
This is the live escape D73 left open.

Two role-sensitive implication relations on ports (x, y, z):

    Forward split  x→y, x→z :  R = {000,001,010,011,111}  (x SOURCE, y,z OUTPUTS)
    Reverse split  y→x, z→x :  R = {000,100,101,110,111}  (x SINK, y,z SOURCES)

## 1. Census results (disjoint 3-ports, all orientations, iso-reps)

| n | fwd/rev realizable as R_T | **output-port capacity** | **full (all-port) capacity** |
|---|---|---|---|
| 6 | yes (148 each) | **yes** | **no** |
| 7 | yes (3370 each) | **yes** | **no** |

The new positive signal vs EQ: **implication output ports DO carry
capacity** (EQ had none).

**Correction to an earlier overclaim.**  The claim "the source
saturates on its active value in every example" was based on the first
example and is FALSE in general.  The aggregate audit
(`refined_capacity_audit`) shows that *some* forward-split gadget DOES
have joint (all-port) capacity on 111 (the active branching vector),
and the source CAN have capacity on a source-bit-1 vector.  So
branching does not always saturate the source.

The correct, universal obstruction is the **equality slice**.  For a
forward/reverse piece used inside an EQ composition, what matters is
joint capacity on the equality vectors {000, 111}, not on all
implication-allowed vectors.  The refined audit (n = 6 and 7):

| n | fwd: 111 ∈ joint | fwd: {000,111} ⊆ joint | rev: 000 ∈ joint | rev: {000,111} ⊆ joint |
|---|---|---|---|---|
| 6 | **yes** | **no** | **yes** | **no** |
| 7 | **yes** | **no** | **yes** | **no** |

So a forward split can have joint capacity on 111, a reverse split on
000, but **no single split has joint capacity on BOTH equality
vectors** — and an EQ_3 splitter feeding a *free* variable needs both
(the variable ranges over 0 and 1).  This is the precise binding
constraint, replacing the incorrect "source saturates" reading.

## 2. The faithfulness obstruction (why implication capacity does not help)

Even granting implication output capacity, implication wiring cannot
carry a *free* variable bit to multiple clauses:

  * A 2-in-3-SAT reduction needs each clause to read a variable's
    *exact* value (both 0 and 1).  A **faithful copy** of a free bit to
    an output is precisely the EQ relation (output = input on both
    values).
  * Implication x→y gives only output ≥ input: when x = 0 the output
    may still be 1, so a clause could read "true" for a false variable.
    This is a *relaxation*, not a copy — it does not faithfully encode
    the variable.
  * Forward + reverse implication pp-composed on the same three ports
    is x→y,z ∧ y,z→x = **x = y = z = EQ_3** — back to the all-equal
    relation D73 found to have no capacity.

So a *faithful* fanout requires EQ, and EQ has no capacity at n ≤ 7
(D73).  Implication carries capacity but only monotone (non-faithful)
propagation, which builds Horn-relaxed instances, not exact 2-in-3.

## 3. Combined fanout verdict (n ≤ 7)

| mechanism | capacity at n ≤ 7 | faithful free-bit copy |
|---|---|---|
| EQ (all-equal) | **no** (D73) | yes (but blocked) |
| implication (Horn) | output: yes; full: no | **no** (relaxation only) |

Neither mechanism yields a faithful occurrence-≥3 fanout at n ≤ 7:
EQ copy is capacity-blocked; implication carries capacity on at most
one equality value, but a faithful free-bit splitter needs both.

## 4. The structural barrier (supported, not proven)

The back-arc graph of any LFO is a linear forest — **max-degree 2, no
branching vertex**.  A bit carried by a port pair propagates through
vertices it shares with other gadgets; its carrier is a sub-forest of
the (max-degree-2) back-arc graph, i.e. a union of paths.  A path has
exactly 2 endpoints, and only a degree-≤-1 endpoint can absorb a new
clause attachment.  Hence:

> **Fanout barrier (conjecture).**  No tournament gadget realizes a
> faithful free-bit splitter: a relation forcing all of {000,111} on
> three disjoint ports with joint output capacity on *both* equality
> values.  Equivalently, the degree-2 budget allows equality-slice
> capacity on one value but not both.

The implication census is the gadget-level evidence (refined audit,
n = 6, 7): a forward split can have joint capacity on 111 and a reverse
split on 000 — branching with capacity on ONE equality side IS possible
— **but no piece has equality-slice capacity on both 000 and 111**.
A free variable ranges over both values, so a faithful splitter would
need both; lacking it, the encodable formulas cannot fan a free bit to
≥ 3 clauses, leaving only read-≤-2 instances, which are polynomial.

## 4b. Composition-capacity probe (the equality-slice escape)

The dangerous escape the joint==R bar missed: a forward piece needs
joint capacity only on the equality slice, and the composition into
EQ_3 needs joint capacity on {000,111} *for the composed gadget*.
Probes:

  * **Piece level (n = 6, 7):** no forward/reverse split has joint
    capacity on both equality vectors (table in §1).  Each can get one
    (111 for forward, 000 for reverse), never both.
  * **Auxiliary-vertex extension (n = 8):** extending a D73 n = 7 EQ_3
    gadget by one auxiliary vertex (all 128 arc-orientations): 13 keep
    R_T = EQ_3, but **none** gains joint capacity on even one equality
    vector, let alone both.  One auxiliary vertex does not free port
    capacity.

So at every checked size the EQ_3-with-equality-slice-capacity object
does not appear.

## 5. Honest status

  * **Established (n ≤ 7, + 1-aux n = 8):** neither EQ nor implication
    gives a faithful capacity fanout.  No gadget has joint capacity on
    both equality vectors {000,111}.  (The earlier "source always
    saturates on its active value" claim is RETRACTED — a single
    forward split can have 111-joint capacity; it just never has both.)
  * **Open (n ≥ 8, ≥ 2 auxiliary vertices):** a forward+reverse
    pp-composition into EQ_3 with ≥ 2 private auxiliary vertices (so the
    equality-enforcing back-arcs land on auxiliaries, not ports) has
    NOT been ruled out.  This is the precise remaining escape hatch.
    The structural barrier (§4) predicts no, but it is unproven, and
    the auxiliary route is exactly where it could fail.
  * **Not censused:** the full n = 8 EQ_3-capacity census (6880
    iso-classes) and multi-aux compositions (n ≥ 9).

## 6. Decisive next experiments

  1. **n = 8 EQ_3-capacity census** (extend reps to 6880 classes) — does
    a capacity copy appear once 12-ish vertices are available?  This
    directly tests the composition escape.
  2. **Prove the Fanout barrier (§4)** from max-degree-2: a propagated
    free bit's carrier is a path with 2 endpoints, so occurrence ≤ 2.
    If proved, NP-hardness via this gadget framework is closed and the
    P-lean becomes a structural theorem.

## 7. Files and tests

| artefact | location |
|---|---|
| Implication census + role-sensitive capacity | `scripts/implication_fanout_census.py` |
| Tests | `tests/test_implication_fanout_census.py` |
| EQ splitter census (D73) | `docs/fanout_splitter_census.md` |
| 2-in-3 clause gadget (D72) | `docs/port_loader_realizability.md` |

## 8. Citations

  * 1-in-3 / 2-in-3-SAT NP-completeness: Schaefer 1978,
    DOI 10.1145/800133.804350.
  * Horn-SAT in P (implication-only instances): classical.
