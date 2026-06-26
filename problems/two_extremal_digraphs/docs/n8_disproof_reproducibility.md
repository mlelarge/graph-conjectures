# n=8 disproof — frozen reproducibility note

Date frozen: 2026-06-04.

## Result (frozen)

**No non-planar 2-extremal digraph exists on 8 vertices — fully certified, gap-free.**
Hence no counterexample to Conjecture 9.2 arises at `n=8` from the
"H₂ ⇒ planar" angle (a non-planar 2-extremal would refute 9.2, since H₂ ⇒ planar
is proved — see `planarity_of_2extremal.md`).

## Scope

- Universe: **all 2-connected, minimum-degree-≥2 simple graphs on `n=8`**, via
  `nauty geng -C -d2 8`, restricted to the **non-planar** ones (4230 of them; a
  planar 2-extremal would not be a counterexample). The non-planar count by edge
  bucket is tabulated below.
- Each tested for the existence of a **2-extremal orientation** (digon/forward/
  backward per edge) by the exact methods below.

## Counts (from `data/n8_disproof_ckpt.json`)

| edge counts | non-planar graphs | method | result |
|---|---|---|---|
| `|E| = 9..23` | 4210 | exact Eulerian-pruned orientation search | 0 admit |
| `|E| = 24..28` | 20 | 15 by κ'≤4 lemma, 5 by forest-constrained exhaustive search | 0 admit |
| **total** | **4230** | — | **0 admit; 0 capped; 0 counterexamples** |

Split: **lemma-certified (κ'(U)≥5): 15;  searched-to-exhaustion: 4215;  budget-capped: 0.**

## The two certification methods

1. **Exact Eulerian-pruned search** (`scripts/planarity_search.two_extremal_orientations`,
   validated edge-for-edge against the naïve `3^{|E|}` enumeration via
   `planarity_search.py --validate`). A 2-extremal digraph is Eulerian, so only
   Eulerian orientations of `G − (digon set)` are candidates; the digon set ranges
   over the parity-coset of the cycle space, restricted to **forests** (F_D is
   provably a forest). This is exhaustive and far smaller than `3^{|E|}`.
2. **Edge-connectivity lemma [PROVED].** *2-extremal ⇒ **maximum local
   edge-connectivity** `λ'(U(D)) ≤ 4`* — no vertex pair has `≥5` edge-disjoint
   paths (proof in `planarity_of_2extremal.md`: for Eulerian `D`,
   `λ_D(u,v) ≥ λ'_U(u,v)/2`, and `λ(D)=2`). So any graph with a pair of `≥5`
   edge-disjoint paths (`λ'≥5`, one Gomory-Hu computation) cannot host a 2-extremal
   orientation — certified with no search. This is **stronger** than the global
   `κ'(U)≤4` (a corollary). (Verified: all 52 truth-set members have `λ'(U) ≤ 4`.)
   *Historical note:* the original `n=8` run used the weaker `κ'(U)≥5` filter (15
   of the 20 dense graphs); the strong `λ'≥5` form (introduced for `n=9`) subsumes
   it and certifies the same dense `n=8` graphs.

## Exact commands

```bash
# main sweep (checkpointed, resumable; uses the κ'≤4 lemma filter + forest search):
PYTHONPATH=problems/two_extremal_digraphs/scripts \
  .venv/bin/python problems/two_extremal_digraphs/scripts/n8_disproof.py --n 8

# read-only audit of the checkpoint at any time:
.venv/bin/python problems/two_extremal_digraphs/scripts/disproof_checkpoint_summary.py --n 8
```
(`.venv` = the repo-root environment carrying `networkx`; `geng` resolved from PATH.)

## Runtime

`|E|≤23` exhaustive sweep: a few minutes. Dense `|E|≥24`: the 15 lemma cases are
instant; the 5 forest-constrained residuals are ≤10⁶ candidate digraphs each,
seconds–minutes total. The full certification is well under an hour on one core.

## Provenance / state

- Branch `main`; this work is **uncommitted** (untracked docs under
  `problems/two_extremal_digraphs/docs/` and checkpoints under `.../data/`).
- Checkpoint of record: `data/n8_disproof_ckpt.json` (buckets `|E|=9..28`, all
  `done`, `capped=0`, `counterexamples=[]`).
- Re-verify the verdict from the checkpoint with `disproof_checkpoint_summary.py`;
  re-verify any future hit with `verify_counterexample.py`.

## Caveat (honest scope)

This certifies **no non-planar 2-extremal digraph at `n=8`**. It does **not**
enumerate the full `n=8` 2-extremal *truth set* (the planar ones), and it does not
prove CONJECTURE-P (`2-extremal ⇒ planar`) — it confirms it has no `n≤8`
counterexample. The structural conjecture (Conj 9.2) remains open.
