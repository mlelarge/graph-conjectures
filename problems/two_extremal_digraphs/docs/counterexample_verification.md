# Red-team verification of flagged Conjecture 9.2 candidate(s)

**Date:** 2026-05-30
**Verifier:** independent red-team pass (code in `scripts/redteam_verify.py`,
`scripts/redteam_closure.py`; does **not** import `h2_oracle.py`).
**Conjecture 9.2** (arXiv:2304.04690 §9): a digraph is 2-extremal **iff** it lies in H₂.

## Candidate under review

```
n = 7
arcs = [[0,3],[0,4],[1,5],[1,6],[2,4],[2,5],[3,1],[3,5],
        [4,0],[4,2],[4,6],[5,1],[5,2],[5,3],[6,0],[6,4]]
```
Flagged by the cross-check as 2-extremal but allegedly **not** in H₂ (oracle reported
0 Hajós-join inverses and 0 tree-join inverses, with the explicit caveat that its
inverse searches are not certified complete).

## (1) 2-extremality — independently recomputed (from scratch, networkx)

| property | value | method |
|---|---|---|
| strongly connected | **True** | `nx.is_strongly_connected` |
| underlying 2-connected | **True** | `nx.is_biconnected` |
| λ(D) = max ordered-pair arc-disjoint dipaths | **2** | unit-cap max-flow over all (x,y) |
| χ⃗(D) | **3** | from-scratch backtracking dicolouring with symmetry break |

⇒ the candidate **is genuinely 2-extremal**. Degree sequence: four vertices at
(out,in)=(2,2), two (4,5) at (3,3), one (6) at (2,2). Confirmed.

## (2) H₂ membership — VERDICT: the candidate IS in H₂ (flag does NOT survive)

### Structural decomposition (hand verification)

Split the arc set into **digons** and **single arcs**:

- digons: `{0-4, 1-5, 2-4, 2-5, 3-5, 4-6}`  (6 digons)
- single arcs: `0→3, 3→1, 1→6, 6→0`  (one directed 4-cycle)

**Key fact:** the 6 digon-edges form a **spanning tree** T on the 7 vertices
(7 nodes, 6 edges, acyclic, connected — a caterpillar):

```
        0   6            1   3
         \ /              \ /
          4 ----- 2 ----- 5         (backbone 4—2—5)
```
- internal vertices: 2 (deg 2), 4 (deg 3), 5 (deg 3)
- **leaves: {0, 6} at node 4 and {1, 3} at node 5** — exactly the four single-arc vertices.

This is precisely the shape of a **2-Hajós tree join with empty A = generalised wheel**
(Def 9.1): every tree edge is a B-edge (realised as a digon), no A-edge digraph
substitution, and the four single arcs are the **peripheral directed cycle on the leaves**.

**Parity condition (Def 9.1) holds.** With A = ∅ all edges are B-edges, so the
requirement "every leaf-to-leaf path uses an even number of B-edges" reduces to
"every leaf-to-leaf path in T has even length":

| leaf pair | tree path | length | parity |
|---|---|---|---|
| 0,1 | 0-4-2-5-1 | 4 | even |
| 0,3 | 0-4-2-5-3 | 4 | even |
| 0,6 | 0-4-6 | 2 | even |
| 1,3 | 1-5-3 | 2 | even |
| 1,6 | 1-5-2-4-6 | 4 | even |
| 3,6 | 3-5-2-4-6 | 4 | even |

All even ⇒ parity condition satisfied.

**Planar leaf order matches the peripheral cycle.** The caterpillar's plane boundary
order keeps node-4's leaves {0,6} consecutive and node-5's leaves {1,3} consecutive.
The candidate's peripheral cycle 0→3→1→6→0 has circular order (0,3,1,6) = (…6,0 | 3,1…):
node-4 leaves {6,0} consecutive, node-5 leaves {3,1} consecutive — a valid planar
circular leaf order of the caterpillar.

### Independent constructive confirmation (second, independently-coded search)

`scripts/redteam_closure.py` builds the H₂ closure forward from below (symmetric odd
cycles, closed under directed Hajós join and the full 2-Hajós tree join including empty-A
generalised wheels). Reconstructing the generalised wheel directly from the digon-tree T
and peripheral cycle, then comparing **canonical forms** (brute-force over all 7!
relabelings) against the candidate:

```
candidate canon == generalised-wheel(T, peripheral 0→3→1→6→0) canon  →  True
```
(True for every valid planar leaf order tried: [0,3,1,6],[6,0,3,1],[0,6,3,1],[0,6,1,3].)

So the candidate is **literally one of the H₂ generalised-wheel base constructions.**

### Why the oracle missed it / why no Hajós inverse exists

- The underlying graph has **no cut vertex** (articulation points = ∅), so it cannot be a
  directed Hajós join of two smaller pieces (the merged vertex of a Hajós join is always a
  cut vertex). The oracle's "0 Hajós-join inverses" is correct and consistent.
- The only underlying 2-vertex-cut is **{4,5}** (the two degree-3 vertices), separating the
  isolated digon-leaf {2} from {0,1,3,6}. The original oracle's `_tree_join_decompositions`
  searched for **non-empty-A** tree-join inverses (its documented gap) and **did not test the
  empty-A generalised-wheel realisation**, which is exactly the construction that produces
  this digraph. That gap — not a true absence — caused the false flag.

### Validation of the independent closure builder

`redteam_closure.py` at MAXN=5 reproduces the paper-known truth sets exactly:
|L₃|=1, |L₄|=1, |L₅|=3, every member 2-extremal (0 non-2-extremal). This corroborates the
builder before relying on it.

## Conclusion

| flag | genuinely 2-extremal? | in H₂? | survives as counterexample? |
|---|---|---|---|
| n=7 candidate above | **YES** | **YES (generalised wheel)** | **NO — refuted** |

**No flag survives.** The n=7 candidate is 2-extremal but is a generalised wheel (empty-A
2-Hajós tree join over a caterpillar digon-tree with even leaf-to-leaf parity), hence an H₂
base member. It is **NOT** a counterexample to Conjecture 9.2. The flag was an oracle
incompleteness artifact (missing empty-A tree-join realisation), exactly the
"oracle gap, not counterexample" failure mode the README warns about.

**Conjecture 9.2 still survives to n=7 with zero verified counterexamples.**

Recommended fix to the production oracle: add the empty-A generalised-wheel test
(detect a spanning digon-tree whose leaves carry the single-arc peripheral directed cycle
and satisfy the even leaf-to-leaf parity condition) to `is_in_H2`.
