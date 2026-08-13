# Relations between conjectures

`data/relations.json` is a directed relation graph over the full conjecture
corpus: the 227 Open Problem Garden problems (`opg:<slug>`) and the 762
arXiv-mined conjectures/problems/questions (`arxiv:<safe_id>__NN`). It records
which conjecture **implies** which, which pairs are **equivalent**, and which
entries are **duplicates** of each other across the two corpora.

**190 relations** survived adversarial verification, out of 207 candidates:

| relation       | confirmed | plausible | meaning                                            |
|----------------|----------:|----------:|----------------------------------------------------|
| implies        |       139 |         4 | truth of `source` forces truth of `target`         |
| equivalent_to  |         8 |         1 | each implies the other                             |
| same_conjecture|        15 |         1 | same statement appearing in both corpora           |
| related_only   |        22 |         0 | documented connection, but no implication          |

Every edge carries the verified direction, a referee argument precise enough
to check by hand, citations when the confirmation is literature-based, and
provenance (how many independent finder agents proposed it, and whether it
survived the re-attack pass).

**"Verified" means checked by adversarial AI referees** against the full
statements and, where applicable, the literature — it does **not** mean
formally verified. None of the arguments have been machine-checked in a proof
assistant such as Rocq or Lean; they are short informal mathematical arguments
that a human (or a formalization effort) can audit.

## Pipeline

The graph was produced by a four-stage multi-agent pipeline
(working files in `data/relations_work/`):

```
phase 0   build_phase0.py       deterministic merge: 989 nodes, identity merges
                                from the 44 manually confirmed arxiv↔OPG matches,
                                seed edges (49 OPG cross-mentions with quotes,
                                12 unverified fuzzy matches, 148 internal-ref hints)
phase A   18 tagging agents     topic cluster + one-line formal gist + canonical
                                invariant names per statement  → tags.json
phase B   17 finder agents      14 per-cluster (2 lenses each on the two biggest
                                clusters), 1 cross-cluster over the gist table,
                                2 over cross-cluster invariant groups
                                → 335 raw candidates → 176 deduped  → candidates.json
phase C   59 verifier agents    52 refute-by-default referees (4 edges each,
                                web search allowed, direction re-derived from the
                                statements) + 7 re-attack skeptics on the 54
                                confirmations resting on an argument alone
                                → verdicts.json → data/relations.json
```

Design choices that mattered:

- **Refute by default.** Verifiers confirm only on a rigorous short argument
  (hypothesis-class containment, parameter monotonicity, standard duality or
  reduction), an explicit statement in the problem's own discussion, or a
  literature citation. Plausible-sounding sketches that could not be justified
  were killed: 17 of 207 candidates were refuted, 3 more downgraded to
  "no relation".
- **Direction discipline.** "A implies B" edges are the ones where getting the
  direction wrong is worst; verifiers re-derive the direction from the
  statements rather than trusting the finder, and one edge was flipped.
- **Second skeptic pass.** Confirmations backed by argument alone (no citation)
  were re-attacked by fresh agents told to find the hole; all 54 held.

## What the refutations caught

- Two fuzzy arXiv↔OPG matches were false, both riding on the generic label
  "Question 1" (`e205`, `e206` in `data/relations_work/verdicts.json`).
- A name collision between two distinct Grünbaum conjectures (`e195`).
- The folklore "5-flow ⇒ cycle double cover" route misattributes Jamshy–Tarsi:
  their theorem starts from the shortest-cycle-cover conjecture, not the 5-flow
  conjecture (`e169`).
- Aharoni's rainbow generalization of Caccetta–Häggkvist is related to, but not
  the same as, Caccetta–Häggkvist (`e204`).

## Status-propagation audit

Confirmed edges let review statuses flow: if A ⇒ B and A is solved, B is
solved; if B is disproved, so is A. Four inconsistencies between the verified
graph and the literature-review dataset surfaced:

1. `arxiv:1802.03727__02` (dense bipartite subgraphs in triangle-free graphs,
   **solved**) ⇒ `arxiv:1802.03727__03` (large-girth version, **open**) — the
   girth ≥ 4 case *is* the triangle-free case, so the second review likely
   missed the resolving paper.
2. `arxiv:2509.07174__00` (coarse Menger, surface-embedded, **partial**) is the
   same conjecture as `arxiv:2509.08762__00` (coarse Menger, bounded genus,
   **solved**) — one of the two reviews is stale.
3. `arxiv:2306.04710__02` (Δ(1,2,2) hero in {K₁+P⃗₂}-free digraphs, **open**)
   ⇒ `arxiv:2202.13306__00` (Δ(1,2,2) hero in oriented complete multipartite
   graphs, **disproved**) — oriented complete multipartite digraphs are
   {K₁+P⃗₂}-free, so the counterexample disproves the source conjecture too.
4. `arxiv:1710.11281__01` (cop number bounded by genus, **solved**) ⇒
   `arxiv:1710.11281__04` (cop number finiteness on bounded surfaces,
   **partial**) — medium confidence (the argument uses Gromov's systolic
   inequality).

These are flagged, not yet fixed: each needs a human glance before the review
JSONs are edited.

## Structure of the graph

Biggest hubs by confirmed implication/equivalence degree: the **cycle double
cover conjecture** (8), **Gyárfás–Sumner** (5), the **5-flow conjecture** (5),
**Petersen coloring** (4), **Caccetta–Häggkvist** (4), and the majority
3-coloring conjecture for digraphs (4). No implication 2-cycles appeared, so
there are no hidden equivalences beyond the declared ones.

## Reproducibility and limitations

`data/relations_work/` keeps the pipeline provenance: `build_phase0.py`
(deterministic phase 0; regenerates the node table and batches from the
checked-in data), `tags.json` (phase A output), `candidates.json` (phase B
output incl. finder sketches), `verdicts.json` (all 207 referee verdicts,
including the refutations with reasons). Reviews were generated with Claude
(Sonnet for tagging, Fable for finding/verification) in August 2026.

Caveats:

- The verification is adversarial AI review, not formal verification: no
  argument has been checked in Rocq, Lean, or any other proof assistant.
- Recall is bounded by the finders: an unproposed edge is an unfound edge.
  Within-cluster coverage is double for the two biggest clusters only.
- The 6 `plausible` edges and 22 `related_only` links are kept but labeled —
  they need literature follow-up before being treated as implications.
- Like the literature reviews, the graph is advisory and should be
  spot-checked before being relied on for research decisions.
