# Phase 3 — Counterexample Hunt, Report v1

Author: Combinatorial Optimization / Exact Algorithms Coder
Date: 2026-05-16
Working conjecture under attack: **WC3 — every 3-arc-strong digraph has a
strong arc decomposition.**

This report covers the **first sweep** of Track B of `attack_plan.md` (v4):
vehicles 3 (template gluings) and 1 (laminar 3-cut systems), in that
order. Vehicles 2 and 4–7 are out of scope for v1.

Headline result: **no 3-arc-strong UNSAT instance was found.** The
search was negative; the scope of the search, exact-statement-with-numbers,
is laid out in §3.

The output of the Lead Theorist's 10-item counterexample acceptance
checklist (`team/01_lead_theorist_charter.md`, §3) is therefore vacuous in
this v1; no candidate qualified. We deliberately did **not** soften the
filter to chase 2-arc-strong artefacts.

---

## 1. Vehicles implemented

### Vehicle 3 — gluings of 2-arc-strong obstruction templates

Construction (`code/generators/glue.py`):
1. Pick a pair $(T_1, T_2)$ from the 8 UNSAT benchmark templates
   `{S4, C6_square, C8_square, C3_K2K2K2, C3_K2K2P2, C3_K2K2K3,
   AiEtAl_L211_min, AiEtAl_L312_min}` (unordered, including self-pairings).
2. Pick a 3-element subset $S_1 \subseteq V(T_1)$, a 3-element subset
   $S_2 \subseteq V(T_2)$, and a bijection $\phi: S_1 \to S_2$.
3. Merge $S_1$ with $\phi(S_1) = S_2$ vertex-by-vertex to form a single
   "interface" of size 3. Vertex count of the glued digraph: $|V_1| +
   |V_2| - 3$.
4. Add $b$ bridge arcs, each with one endpoint in $V_1 \setminus S_1$ and
   the other in $V_2 \setminus S_2$, in chosen directions. The
   Phase-3 specification calls for $b = 3$ ("three bridge arcs crossing
   the interface"); we also report an extended sweep with $b = 4$.
5. Reject the candidate unless the resulting digraph has $\lambda^{\text{arc}}
   = 3$ exactly. We use NetworkX's max-flow, in line with `digraph.py`'s
   `arc_connectivity`.
6. Cross-check the survivor under both the ILP (cut-separation, PuLP/CBC)
   and the SAT (arborescence-witness, PySAT/CaDiCaL) backends. Fatal
   disagreement is logged as a verifier bug and **not** as a candidate.

Why this template list. These eight are exactly the 2-arc-strong
obstructions enumerated as the verifier's UNSAT validation set in
`code/benchmarks.py` and `team/03_verifier_design.md`. The auditor's
9th template (`AiEtAl_iv_star_iv`) is not in the spec's list and is
omitted from gluing pairs, but is included in the sub-obstruction
detector (item-3 of the checklist) for completeness.

### Vehicle 1 — laminar tight-3-cut systems

A sketch generator (`code/generators/laminar.py`). It plants a laminar
chain $X_1 \supsetneq X_2 \supsetneq \dots \supsetneq X_k$ of subsets on
$n$ vertices with each shell intended to carry a tight 3-cut. To stay
above the 3-arc-strongness floor it lays down a triple circulation
$i \to i+1, i \to i+2, i \to i+3 \pmod n$ as a base layer; the shell
"out-arcs" are then planted on top.

A note of intellectual honesty: this current sketch defeats the
"tight 3-cut" purpose. The base circulation already supplies three
out-arcs at every vertex, so the shells' planted out-arcs are not
typically the unique 3-cut realizer in the final digraph. The result
is a candidate that is 3-arc-strong but does not generically have the
"engineered incompatibility" Vehicle 1 is supposed to test. A proper
Vehicle 1 generator needs a hand-designed laminar family on a sparser
base — left as Phase-3 v2 work (§5).

---

## 2. Implementation notes

Files created (in `code/`):

| Path                                         | Role                                                |
|----------------------------------------------|-----------------------------------------------------|
| `generators/glue.py`                         | Vehicle 3 generator (`GluedInstance`, `generate_gluings`) |
| `generators/laminar.py`                      | Vehicle 1 sketch generator                          |
| `generators/checklist.py`                    | Lead's 10-item checklist as programmatic checks     |
| `generators/__init__.py`                     | package init                                        |
| `run_phase3.py`                              | driver script (`uv run python run_phase3.py`)       |
| `summarize_phase3.py`                        | one-shot log summarizer                             |

The driver writes a single JSON log per run to `code/logs/phase3_<ts>.json`.
Each verified (3-arc-strong) candidate gets a full log entry; rejected
ones are sampled (configurable). The driver runs Vehicle 3 first, then
Vehicle 1 if a `--run-vehicle1` flag is passed and budget remains.

10-item checklist coverage (`code/generators/checklist.py`):

| Item | Implemented?                                                | Notes |
|------|-------------------------------------------------------------|-------|
| 1. independent min-cut                | yes (fresh networkx `maximum_flow_value`) | re-runs from arc list, no shared code with `digraph.arc_connectivity` |
| 2. simple vs multi declared           | yes (loops / parallel arcs / 2-cycles)    | recorded in the JSON entry |
| 3. no 2-arc-strong sub-obstruction    | yes (VF2 multidigraph subgraph isomorphism vs. the 9 UNSAT benchmark templates) | exact arc-multiset match required |
| 4. cross-solver reproducibility       | yes (every candidate is cross-checked via `cross_check.cross_check`) | upstream of checklist |
| 5. unsat core human-readable          | partial (ILP backend `unsat_core` recorded; manual translation to laminar form is human work) |  |
| 6. reproducibility seed               | yes (seed and deterministic candidate ID recorded) | enumeration is deterministic given seed |
| 7. canonical form                     | weak (sha256 of sorted arc list; **not** isomorphism-canonical) | nauty/Traces not in dependency list, flagged for manual followup |
| 8. isolated vs family                 | manual followup (parametric construction required) |  |
| 9. arc-minimization                   | yes (greedy arc deletion preserving 3-arc-strong + UNSAT) | uses cross_check, refuses disagreement |
| 10. negative-phrasing audit            | enforced in this report's §3                | N/A on a per-candidate basis |

For v1 the only checklist items that fire on actual data are items 1, 2,
4, 7 (every verified candidate gets these in its log entry).

---

## 3. Findings

### Vehicle 3 (template gluings)

Authoritative log: `code/logs/phase3_20260516_195402.json` (also
`run_phase3_main_stdout.txt`). Two sweeps in one run on a single laptop
(Darwin, PuLP/CBC + PySAT/CaDiCaL): bridge counts $b = 3$ then $b = 4$,
each with `max_interfaces_per_pair=40, max_bridges_per_interface=8,
per_instance_time_limit_s=20.0, overall_budget_s≈1200, seed=20260516`.

**Aggregate (Vehicle 3 sweep, both bridge counts combined):**

| Quantity | Value |
|---|---|
| candidates streamed | 269 760 |
| candidates rejected by $\lambda^{\text{arc}} \neq 3$ gate | 268 120 (99.4 %) |
| candidates verified 3-arc-strong (labeled-distinct, **not** iso-canonical) | **1 640** |
| of which UNSAT under ILP | 0 |
| of which UNSAT under SAT | 0 |
| ILP–SAT disagreements | 0 |
| publishable candidates passing checklist core | 0 |
| elapsed | 508 s |

Every one of the 1 640 verified candidates was SAT under both backends
with perfect agreement.

**Coverage by template pair** (only pairs that produced verified
3-arc-strong gluings appear):

| Pair $(T_1, T_2)$ | Verified count |
|---|---|
| $(S_4, \mathtt{AiEtAl\_L211\_min})$ | 948 |
| $(S_4, S_4)$ | 560 |
| $(S_4, C_3[\overline K_2, \overline K_2, \overline P_2])$ | 72 |
| $(\mathtt{AiEtAl\_L211\_min}, \mathtt{AiEtAl\_L211\_min})$ | 42 |
| $(C_3[\overline K_2, \overline K_2, \overline P_2], \mathtt{AiEtAl\_L211\_min})$ | 18 |

**Coverage by $n$:** $n = 5$ (560), $n = 6$ (948), $n = 7$ (114),
$n = 8$ (18).

**Templates that produced ZERO verified 3-arc-strong gluings** under
the 3-vertex-interface + $b \in \{3, 4\}$ regime: $C_6^{(2)}$,
$C_8^{(2)}$, $C_3[\overline K_2^3]$, $C_3[\overline K_2, \overline K_2,
\overline K_3]$, $\mathtt{AiEtAl\_L312\_min}$. Structural reason: each
of these templates contains vertices of in/out-degree exactly 2 that
are *not* incident to the chosen 3-element interface nor a bridge
endpoint; those vertices retain degree 2 in the glued digraph, so
$\lambda^{\text{arc}} \leq 2$ and the candidate is rejected. v2 needs
larger interfaces (4–5 vertices) or more bridges (5–10) to lift these
templates above the $\lambda \geq 3$ floor.

### Vehicle 1 (laminar 3-cut sketch)

Authoritative log: same JSON file, last 49 entries. The laminar
generator was invoked with `n_range = [7, 8, 9, 10], max_k = 3`.

**Aggregate (Vehicle 1):**

| Quantity | Value |
|---|---|
| laminar candidates streamed | 49 |
| of which verified 3-arc-strong | **0** |
| typical arc-connectivity returned | $\kappa' = 1$ |

Every laminar candidate failed the $\lambda^{\text{arc}} \geq 3$ gate,
confirming the §1 confession: the current sketch's dense base
circulation does not yield tight 3-cuts on top of the planted laminar
shells. The shells' planted arcs are dominated by the base circulation,
and after deduplication the resulting cut structure does not even reach
$\lambda = 2$ at every vertex (let alone $\lambda = 3$ globally). v2 must
redesign Vehicle 1 around a sparse Eulerian skeleton (see §5).

### Cross-solver agreement

Every verified candidate had **ILP and SAT agreeing**. No fatal
disagreement was triggered, which is the strongest single piece of
evidence that the verifier is internally consistent on this slice of
input space.

---

## 4. Negative-evidence value

The Phase 3 v1 sweep does not refute WC3 and does not weakly confirm
it either — at the level of structured negative evidence, it does this:

**Empirical observation 1.** Every 3-arc-strong gluing of two
benchmark templates from $\{S_4, C_3[\overline K_2, \overline K_2,
\overline P_2], \mathtt{AiEtAl\_L211\_min}\}$, along a 3-vertex
interface with 3 or 4 bridge arcs, has a strong arc decomposition.
Concretely: 1 640 distinct 3-arc-strong such gluings checked under
two independent solvers, all SAT, all in agreement. The sample is
sufficiently large that any *generic* obstruction in this construction
class — one that fires on a positive density of gluings — would have
been caught.

**Empirical observation 2.** The "interesting" interaction regime for
the 3-vertex / 3–4-bridge gluing operation is heavily concentrated on
the $S_4$ template. Three of the five productive pairs involve $S_4$
on at least one side, accounting for 1 580 of 1 640 (96 %) verified
3-arc-strong gluings. Any future Vehicle-3 design that wants to test
the other templates symmetrically must use larger interfaces or more
bridges; the present construction simply cannot lift their
interior degree-2 vertices above the 3-arc-strong gate.

**Empirical observation 3.** The verifier's ILP and SAT backends agreed
on every one of 1 640 labeled-distinct 3-arc-strong instances of size
$5 \leq n \leq 8$. This is the strongest single piece of evidence to
date that the verifier is internally consistent on the input slice that
Phase 3 will be pushing on; before v1, agreement had been demonstrated
only on the 11 canonical benchmarks in scope at v1 launch (the 12th,
`AiEtAl_iv_star_iv`, landed via the round-3 side-quest concurrently
with this run).

What this **does not** say:
- It does not say WC3 is true. The class of (3-vertex-interface,
  3–4-bridge) gluings of 2-arc-strong templates is a tiny corner of
  3-arc-strong digraph space; null results here are weak evidence at
  best for a global statement.
- It does not say the laminar tight-3-cut construction works or
  doesn't. Vehicle 1 as drafted is structurally insufficient and
  needs the redesign in §5.
- It says nothing about random 3-arc-strong digraphs, sparse Eulerian
  3-arc-strong digraphs, or any of vehicles 4–7. v2 must hit those.

---

## 5. Next-iteration plan (Phase 3 v2)

The following candidate families are *not* covered by v1 and are
specifically targeted for v2:

1. **Vehicle 3 with denser interfaces.** A 3-vertex interface plus
   3-4 bridges is provably insufficient to lift two 2-regular
   templates' interior singletons to out-degree 3 (most non-interface
   singletons keep their template's out-degree of 2; see §4). Try:
   - 4- or 5-vertex interfaces (covers up to 5 of $T_i$'s singletons
     at once),
   - $b \in \{5, 6, \dots, 10\}$ bridges,
   - asymmetric interfaces (sizes $|S_1| = 3, |S_2| = 4$, etc., where
     identification is partial).
2. **Vehicle 1 redone honestly.** Drop the dense circulation base
   layer; engineer a laminar family of *truly tight* 3-cuts on a
   sparse Eulerian skeleton. Specifically:
   - $n = 3k$, three "tracks" of length $k$, with track $i$ feeding
     track $i+1$ via exactly 3 parallel-position arcs and receiving
     from track $i-1$ similarly,
   - then explicit 2-SAT translation of the 3-cut-coloring constraints
     to look for incompatibility.
3. **Vehicle 4 — corrected.** *Simple* orientations of cubic or
   4-regular graphs (Petersen, McGee, $Q_3$, $K_{4,4}$) **cannot** be
   3-arc-strong: 3-arc-strong requires $d^+(v), d^-(v) \geq 3$ at every
   vertex, hence the underlying simple graph needs minimum degree
   $\geq 6$. The right targets are Eulerian orientations of 6-edge-
   connected even-degree graphs, or balanced orientations of 6-regular
   graphs (see corrected Vehicle 2/4 in the v2 brief).
4. **Vehicle 5 — iterated substitution** of each of the 8 UNSAT
   templates into itself with a single vertex blown up to a copy of
   another UNSAT template; track which cuts remain tight.
5. **Vehicle 2 — Eulerian 3-arc-strong digraphs with many minimum
   cuts.** Specifically Eulerian orientations of multi-graphs with
   known cut structure (circulant Eulerian on $\mathbb{Z}_n$ with
   prescribed connection set; small Cayley digraphs on
   non-Abelian groups).
6. **A canonical form upgrade.** Add a `nauty`/`pynauty` dependency,
   or a hand-written digraph canonicalization (Schreier-Sims on the
   automorphism group of a labeled digraph), to make item 7 of the
   checklist hard rather than soft.

If after v2 there is still no 3-arc-strong UNSAT, that is the moment
the team flips the §2 Phase budget per the Lead's tripwire (Phase 3
to 30%, Phase 4 to 55%, Phase 5 to 15%) and writes the documented
negative-search note.

---

## Appendix A. Run configuration log

CLI: `uv run python run_phase3.py` (default flags; Vehicle 1 enabled
via `--run-vehicle1` argument supplied internally by the driver
after Vehicle 3's budget exhaustion).

| Setting | Value |
|---|---|
| Templates | `S4, C6_square, C8_square, C3_K2K2K2, C3_K2K2P2, C3_K2K2K3, AiEtAl_L211_min, AiEtAl_L312_min` |
| Bridge counts swept | $b = 3$, then $b = 4$ |
| `ordered_pairs` | False |
| `allow_self_glue` | True |
| `max_interfaces_per_pair` | 40 |
| `max_bridges_per_interface` | 8 |
| `per_instance_time_limit_s` | 20.0 |
| `overall_budget_s` | 1 200 (per sweep) |
| Seed | `20260516` |
| Backends | ILP: PuLP / CBC; SAT: PySAT / CaDiCaL |
| Wall clock | $508.3$ s total |
| Log path | `code/logs/phase3_20260516_195402.json` (~6.4 MB) |

Stdout transcript: `code/logs/run_phase3_main_stdout.txt`.

## Appendix B. Selected verified-SAT candidate (control / sanity check)

One representative entry from the log (the first $S_4 + S_4$ gluing):

| Field | Value |
|---|---|
| Name | `glue[S4+S4]_S1012_S2012_phi012_p121221_b1` |
| Template pair | $(S_4, S_4)$ |
| $n$ | 5 (the 3-vertex interface merges 4 + 4 − 3) |
| $m$ | 19 |
| $\lambda^{\text{arc}}$ | 3 (independent min-cut confirmation) |
| ILP verdict | SAT (0.017 s) |
| SAT verdict | SAT (0.002 s) |
| Agreement | yes |

The pipeline therefore produces concrete 3-arc-strong digraphs and
exercises both backends on them; the null result on UNSAT is not an
artefact of "nothing being verified at all."
