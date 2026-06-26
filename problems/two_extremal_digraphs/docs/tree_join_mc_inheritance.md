# Tree-join MC inheritance probe

Date: 2026-06-01.

## Target

The current obstruction for Conjecture 9.2 is the `MC=0` side of Lemma A:
does every non-base 2-extremal digraph with no directed-Hajos seam admit a
non-empty-A 2-Hajos tree-join seam?

This pass tests a sharper structural principle:

> **MC-inheritance heuristic.** If an A-block in a 2-Hajos tree join has a mixed
> 2-cut `(v,e)` leaving a component with neither designated interface endpoint,
> then the whole joined digraph should also have `MC=1`.

If true, an `MC=0` tree-join can only use A-blocks whose mixed cuts are all
absorbed by the interface endpoints, or A-blocks that are themselves `MC=0`.
That is a useful reduction of the recursive `MC=0` case.

## Result

I added `scripts/tree_join_mc_inheritance.py`, a bounded forward-construction
probe. It builds one-A-edge 2-Hajos tree joins from small plane-tree templates
and A-blocks in `L_3,...,L_7`, then checks whether a persistent mixed cut in
the A-block survives as `MC=1` in the output.  Here "persistent" means that
after deleting `(v,e)` inside the block, at least one separated component
contains neither interface endpoint.

Run:

```bash
uv run python problems/two_extremal_digraphs/scripts/tree_join_mc_inheritance.py
```

Output summary after switching to labelled deduplication and the default
`max_output_n = 9`:

```text
outputs tested: 771
violations: 0
```

The status table was:

| block base? | block has MC? | block has persistent MC? | output has MC? | output base? | count |
|---|---:|---:|---:|---:|---:|
| no | no | no | no | no | 45 |
| no | yes | no | yes | no | 402 |
| no | yes | yes | yes | no | 168 |
| yes | no | no | no | yes | 156 |

So there are **zero** sampled cases where a persistent mixed cut in the A-block
disappears in the whole join.

## New recursive MC=0 evidence

The probe also removes an important weakness in the previous status notes. The
`MC=0` tree-join regime is **not only a W3-block phenomenon** in forward
constructions.

The script constructs 45 labelled `n=9` 2-extremal, non-base, non-Hajos,
`MC=0` outputs by using one of the three `n=7` tree-join-only members
(`L7.7`, `L7.14`, `L7.36`) as the single A-block in a parity-valid `path3`
tree join. Grouped by A-block:

- `L7.7`: 15 labelled outputs,
- `L7.14`: 15 labelled outputs,
- `L7.36`: 15 labelled outputs.

Each output has:

- `output_mc = 0`,
- no directed-Hajos decomposition found by `_hajos_decompositions`,
- `output_base = false`,
- A-block non-base and `MC=0`.

This is the first local evidence exercising recursive `MC=0` tree-join
descent beyond a single `W3` A-block. It is generated evidence, not a complete
truth-set enumeration at `n=9`.

## Update 2026-06-01b — the heuristic is now a PROVED lemma (absorption probe)

The one-A-edge probe above could not actually stress the lemma: it builds joins
whose single A-edge touches a leaf, and in that regime **no** block mixed cut is
ever absorbed — verified 792/792 survive (split 168/624 by the *old, stale*
`persistent` guard, which the corrected predicate below shows was mislabelling:
all 792 are in fact interface-free). So "0 violations" there was uninformative
about the supposed `persistent` clause.

`scripts/tree_join_mc_absorption.py` closes this. It builds joins with **interior
A-edges**, **up to two A-edges**, and rims of size 2 (`path4`) **and `≥3`**
(`spider3`/`cat3`/`h`) — exactly the configurations in which external structure
could bridge a block cut. Over **5223 distinct 2-extremal outputs / 4276
block-cut triples** (rim breakdown: 4390 at rim=2, 576 at rim=3, 257 at rim=4):

```text
(interface_free, separates_interface, survived) = (True, False, True): 4276/4276
Q-VIOLATION  interface-free cuts absorbed (REFUTES lemma): 0
interface-separating cuts observed                       : 0
```

Here `interface_free` is the **corrected** persistence predicate
(`has_interface_free_component`): unlike the earlier
`tree_join_mc_inheritance.cut_has_interface_free_component`, it does **not**
short-circuit to `False` when the cut vertex is an interface endpoint — those
cuts are persistent too (proof step 3). Under the corrected predicate **every**
block mixed cut is interface-free, so the tally is a single row. (The earlier
probe's `persistent`/`non-persistent` split was an artifact of that stale guard;
it is superseded here.)

The reason absorption never fires is **structural, not numerical**, and it
upgrades the heuristic to a lemma with an `n`-independent proof:

> **Lemma (MC-inheritance, proved).** Every mixed 2-cut of every A-block survives
> as a mixed 2-cut of any 2-Hajós tree join.

*Proof.* (1) The interface `(p,q)` is a **digon** (Def 9.1: `[uᵢ,vᵢ] ⊆ A(Dᵢ)`),
so the underlying edge `p–q` exists and is **not single**. (2) A mixed 2-cut
deletes a vertex `v` and a **single** edge `e`; since `e` is single, `e ≠ {p,q}`,
and the digon edge is removed only if `v ∈ {p,q}`. So a mixed cut never puts
`p,q` in distinct components — it **never separates the interface**
(empirically 0/264 over all of `L₃..L₇`). (3) A mixed cut has `≥2` components;
with only two interface vertices, "no interface-free component" would force
exactly two components splitting `p,q`, impossible by (2). Hence **every block
mixed cut is persistent** (and if `v ∈ {p,q}` the other interface vertex still
leaves an interface-free component). (4) The interface-free component `C` is
internal to `Dᵢ`; external structure attaches to `Dᵢ` only at `p,q ∉ C`, so `C`
stays isolated in `U(D′)−v′−e′` and `e′` stays single (at least one endpoint
internal, only `Dᵢ` feeds arcs there). So `(v′,e′)` is a mixed cut of the output. ∎

The earlier "persistent / interface-free component" framing was the **wrong
abstraction**: the `persistent` hypothesis is *automatic* — it holds for every
mixed cut — because the interface is a digon and a digon cannot be split by a
mixed 2-cut.

### Corollary used by R-b (proved)

`MC(output) ≥ Σ MC(Aᵢ-block)`. This needs the surviving cuts to be **distinct**:
the map `(cut_v, cut_e) ↦ (mp[cut_v], {mp[a], mp[b]})` is injective because each
block's per-A-edge vertex map `mp` is injective on that block's vertices, and
distinct A-blocks share only the interface/tree nodes (interiors are fresh and
pairwise disjoint) — and no block cut edge is the interface digon, so two block
cuts can collide only if they were equal. Survival + injectivity give the
inequality. Cross-checked **in-script** (`tree_join_mc_absorption.py`): **1841
distinct `MC=0` outputs**, `0` outputs with `out_mc < Σ block_mc`, `0` cut-map
injectivity/survival failures. Hence:

> An `MC=0` 2-Hajós tree join uses **only `MC=0` A-blocks** (plus base objects).

So recursive `MC=0` descent stays inside the `MC=0` class — a tree join can never
launder an `MC≥1` block into an `MC=0` output. The 45-labelled / **11-iso-class**
`n=9` examples (the `L7.7/14/36` blocks are all `MC=0`) are consistent with this.

## Consequence — the remaining target

The inheritance lemma is **settled**; it is no longer the open part. The residual
structural target for R-b is purely the **existence** half:

> given a non-base `MC=0` 2-extremal `D`, exhibit a valid even-`B`-parity rim and
> an `(A,B)` partition with strictly-smaller `MC=0` (or base) 2-extremal blocks.

The inheritance lemma constrains the *blocks* of such a decomposition but does not
*produce* the decomposition; that mechanism (rim cycle + `(A,B)` partition + block
placement) is still missing, as in `seam_k2_degradation.md §3.2`.

*Caveat.* The Lemma's proof is general (`n`-independent) but should be independently
red-teamed before it is treated as load-bearing; the empirical backstop (every
number reproducible from `tree_join_mc_absorption.py`) is 4276/4276 cuts
interface-free & surviving, 0 interface-separating cuts (also 0/264 over raw
blocks `L₃..L₇`), and the corollary checks (1841 `MC=0` outputs, 0 violations) —
not the proof.
