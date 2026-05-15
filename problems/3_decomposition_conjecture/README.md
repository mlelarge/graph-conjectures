# 3-Decomposition Conjecture

Workstream attacking the Hoffmann-Ostenhof / Arthur conjecture
(OPG posting 2017-01-24, originally Hoffmann-Ostenhof 2011):

> Every connected cubic graph $G$ has a decomposition $E(G) = T \sqcup C \sqcup M$
> where $T$ is a spanning tree, $C$ is a 2-regular subgraph (possibly empty),
> and $M$ is a matching (possibly empty).

See [docs/plan.md](docs/plan.md) for the strategic plan, vertex-typing
reformulation, known partial results, and the seven-phase attack.

## Status

**First proof step done.** Lemma 1 (Bridge reduction) is proved in
[docs/minimal_counterexample.md](docs/minimal_counterexample.md) §2 and
Sub-lemma 1' (the subcubic existence step it depends on) is
computer-checked on all connected 1-port subcubic graphs with $n \le 11$
vertices via [scripts/sublemma_bridge_sweep.py](scripts/sublemma_bridge_sweep.py).

Foundational primitives in [scripts/decomposition.py](scripts/decomposition.py):

- `verify_decomposition(G, labels)` — checks any candidate
  $(T, C, M)$ partition. Propagator-agnostic; the trust root.
- `find_3_decomposition(G)` — brute-force finder (tractable for
  $|E| \le \sim 16$).
- `compute_trace_set(H, ports)` — bare-bones trace-set computer
  (chi only).
- `compute_trace_set_2pole(H, [r1, r2])` — full 2-pole trace-set
  computer, including the tree-connectivity partition $\pi$. This is
  the substrate for Lemma 2 (essential 2-edge-cut reduction) and the
  gadget-containment lattice.
- `verify_bridge_side_realisable(H, port)` — Sub-lemma 1' single check;
  spanning-tree-strict (T_H must span H, not merely be a forest).
- `scripts/gadget_lattice.py` — enumerates ordered 2-pole gadgets via
  nauty, computes full trace sets, groups identical trace sets, and
  writes the trace-set inclusion lattice. Current generated artefact:
  `data/gadget_lattice_2pole_n10_both.json` (274 oriented gadgets, 59
  trace classes, 113 cover edges, unique maximal class `C58` with 16
  traces). The $n \le 12$ lattice build is checkpointed in
  `data/gadget_lattice_2pole_n12_both.jsonl`.
- `scripts/coverage_check.py` — given an arbitrary 2-pole side
  $(H, R)$, compute $\mathrm{Trace}(H, R)$ and support both directions:
  envelope coverage $\mathrm{Trace}(H) \subseteq \mathrm{Trace}(C)$ and
  Lemma-2 replacement $\mathrm{Trace}(C) \subseteq \mathrm{Trace}(H)$.
- `scripts/coverage_sweep.py` — applies the envelope check to every
  oriented 2-pole subcubic graph at a given $n$; it surfaces "new"
  traces not realised by any small gadget, but does **not** test the
  replacement direction.
- `scripts/replacement_sweep.py` — applies the Lemma-2 replacement check
  to every oriented 2-pole subcubic graph at a given $n$. This is the
  correct empirical test for the Antichain Coverage conjecture.
- `scripts/full_replacement_sweep.py` — reproducible, resumable full
  sweep with structural classes, absorbing class ids, compatibility
  status, and per-side JSONL records.
- `scripts/classIII_absorber_check.py` — verifies the compatibility-
  domination replacement for the residual n=12 Class-III side and writes
  its 16-trace witness table.
- `scripts/compatibility_universality.py` — computes compatibility-
  universal lattice classes and checks the n=12 replacement failures.

Regression suite in [tests/test_decomposition.py](tests/test_decomposition.py)
(33 tests, all passing): $K_4$, $K_{3,3}$, the triangular prism, the
Petersen graph ($n = 10$, $|E| = 15$); 6 tests on the 2-pole trace
computer (K_4-minus-edge as a 2-pole side; subdivided prism, 8 vertices,
11 edges, 11 traces); tests on envelope coverage and replacement-direction
checks against the in-memory small lattice.

**Antichain Coverage conjecture refuted at $n = 12$** (see
[docs/minimal_counterexample.md](docs/minimal_counterexample.md) §3.6;
data: [data/replacement_sweep_n12.json](data/replacement_sweep_n12.json)).
Of 1670 oriented 2-pole sides at $n = 12$, **10 are not replaceable** by
any smaller-order lattice gadget — concentrated in 5 distinct trace
sets, all missing the same 4 "common obstruction" traces. Lemma 2 cannot
close from the n≤10 lattice alone.

**Structural classification of the 10 failures** (see
[docs/minimal_counterexample.md](docs/minimal_counterexample.md) §3.7;
data:
[data/failure_structural_classification_n12.json](data/failure_structural_classification_n12.json)):
6 oriented failures have an internal bridge/articulation, 2 have a
non-port-trivial 2-vertex-cut, and the remaining 2 orientations are one
essentially 3-connected graph6 pattern, `K?AB?qQT@WWG` with ports
$(2,4)$. All 5 distinct failure trace sets are compatibility-universal,
so the n=12 failure set is absorbed by compatibility replacement using a
6-vertex universal gadget from class `C5`. The live proof gap is no
longer Class II at n=12; it is the all-orders **Universal Replacement
Conjecture**: every essential 2-edge-cut side of order at least 12 should
be either trace-contained by a smaller lattice class or compatibility-
universal. Compatibility-universal now has a four-axis characterisation:
boundary `(T,T)` joined, boundary `(T,T)` split, boundary `(T,M)`, and
boundary `(M,T)`. In the n≤10 lattice, every class with at least 11
traces is compatibility-universal; the n=12 failure #1 is an atomic
4-trace universal set, one trace per axis. The cubic 2-vertex-cut
boundary-trace lemma is still needed later for the 3-edge-connected to
3-vertex-connected upgrade.

**n=14 essentially-3-connected sweep complete.** Against the n≤12
lattice, all 7120 oriented essentially-3-connected sides at n=14 are
trace-contained; none require compatibility fallback. Absorption is
concentrated in three minimal n≤12 lattice classes: `C0` absorbs 7106
sides, `C2` absorbs 10, and `C5` absorbs 4. This `C5` is the n≤12 class
id, not the earlier n≤10 universal class id. See
[data/n14_essentially_3conn_full.summary.json](data/n14_essentially_3conn_full.summary.json).

**Full n=14 all-class sweep complete.** Across all 15178 oriented
2-pole subcubic sides, 15176 are trace-contained in the n≤12 lattice, 2
are compatibility-universal but not trace-contained, and 0 are `neither`.
The two compatibility-only records are the two orientations of the same
bridge-class graph6 ``M??CB?W`cKKGF?WG?`` with ports $(3,4)/(4,3)$ and
$|\mathrm{Trace}|=5$; this side is also eliminated by the minimal-side
bridge lemma because its bridges cut off zero-port components. The
trace-contained records are absorbed by a 10-class n≤12 lattice core:
`C0`, `C2`, `C3`, `C4`, `C5`, `C6`, `C7`, `C8`, `C22`, `C23`. Data:
[data/n14_full.summary.json](data/n14_full.summary.json), with the full
JSONL archive currently at
[data/n14_essentially_3conn_full.jsonl](data/n14_essentially_3conn_full.jsonl)
despite the historical filename.

The plan runs two parallel tracks:

- **Track A** — replay Zhang-Szeider (CP 2025, LIPIcs vol. 340 #39), ingest
  their reducible-template library, build an independent verifier for the
  local-behaviour-table formalism, search beyond their bounds.
- **Track B** — minimal-counterexample structural theory. Unconditional
  shape of $G^\star$: bridgeless (2-edge-connected), non-Hamiltonian,
  non-traceable, non-planar, contains a claw, no 2-factor of exactly
  three cycles, $n \ge 30$. Further shape (3-edge-connected; no
  $\mathbb{RP}^2$/torus/Klein-bottle embedding; triangle-free; tree-width
  $\ge 4$) is **conditional on the 2-edge-cut and 2-vertex-cut reductions**
  (Phase 5.0). Closing those is the highest-leverage internal lemma; it
  upgrades every conditional bullet.

Generic discharging on cubic graphs is *not* a phase: there is no global
Euler reservoir on non-planar cubic graphs.

## Layout (intended)

```
docs/                 plan, literature notes, discharging log
scripts/              SAT oracle, verifier, configuration miner
data/                 cubic-graph catalogues, decomposition certificates
tests/                regression suite on known positives
```

Original problem record:
<http://www.openproblemgarden.org/op/3_decomposition_conjecture>.
