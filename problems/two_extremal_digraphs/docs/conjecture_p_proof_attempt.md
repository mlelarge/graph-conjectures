# Attempt to prove CONJECTURE-P (2-extremal ⇒ U(D) planar), and why it too is circular

Date: 2026-06-03. Follows `docs/planarity_of_2extremal.md`.

> **Verdict up front.** The natural (and only evident) route to prove
> `2-extremal ⇒ planar` is the Tutte 2-sum reduction. Two of its ingredients are
> **proved cleanly** (3-connected ⇒ `MC=0`; 2-sum preserves planarity), and the
> **base case** (3-connected 2-extremal ⇒ generalised wheel) is strongly supported. But the
> **inductive step** — splitting `D` at a 2-vertex-cut into smaller *2-extremal*
> pieces — is exactly the seam-existence machinery (R-a/R-b), and the base case is
> the 3-connected special case of Conjecture 9.2. So an independent proof of
> CONJECTURE-P reduces to the **same open core** as the main conjecture. No
> independent proof obtained; the precise circularity is mapped below.

## Strategy: Tutte 2-sum reduction

`U(D)` is 2-connected. By the Tutte decomposition, a 2-connected graph is planar
**iff every 3-connected component (brick) is planar**; equivalently, at a
2-vertex-cut `{a,b}` splitting `U(D)=G₁∪G₂` (`G₁∩G₂={a,b}`), `U(D)` is planar iff
`G₁+ab` and `G₂+ab` are both planar. Induct: base = 3-connected; step = a 2-cut
exists.

## Proved ingredients

### (P1) 3-connected ⇒ `MC=0`. **[PROVED]**

If `U(D)` is 3-vertex-connected then for any vertex `v`, `U(D)−v` is 2-connected,
hence **bridgeless**; so deleting any single edge from `U(D)−v` keeps it connected.
Thus no `(vertex v, single edge e)` pair disconnects `U(D)` — `MC(D)=0`.
*(Consistent: all 3-connected truth-set members are `MC=0`.)*

### (P2) 2-sum preserves planarity. **[KNOWN]**

`U(D)` planar iff `G₁+ab`, `G₂+ab` planar (standard 2-clique-sum fact).

### (P3) `H₂ ⇒ planar`. **[PROVED — `planarity_of_2extremal.md`]**

(Used only to note consistency; not an input to the forward proof.)

## Base case: 3-connected 2-extremal ⇒ U(D) is a GENERALISED wheel

> **Correction (2026-06-03, post-review).** The earlier draft claimed the
> classical hub-and-rim *wheel*. That is **false**: a non-star, empty-A 2-Hajós
> tree join can be 3-connected without being a classical wheel. Verified
> counterexample (`n=10`, **3-regular**, planar): tree = root with three internal
> children, each carrying two leaves, all edges B (empty A). The repo confirms
> `is_2extremal=True`, `MC=[]`, `_is_generalised_wheel=True`, `node_connectivity=3`,
> and it is **not** a classical wheel (every vertex has degree 3, no hub). So the
> correct base statement is **generalised wheel**, and my `n≤7` experiment only
> ever saw classical wheels because the smallest non-classical 3-connected
> generalised wheel needs `n ≥ 8`.

**Evidence [VERIFIED, exact].** From `scripts/planarity_search.py` (Eulerian-pruned
*exact* enumeration — validated edge-for-edge against the naïve `3^{|E|}` count on
C5/W4/W5/K4/prism/K3,3/K5), among all 3-connected graphs every graph that admits a
2-extremal orientation does so only as a **generalised wheel**:

| n | 3-connected graphs | admit a 2-extremal orientation | admit but NOT all generalised-wheel |
|---|---|---|---|
| 5 | 3   | 1 | 0 |
| 6 | 17  | 1 | 0 |
| 7 | 136 | 1 | 0 |

(At `n≤7` the one admitting graph per `n` is the classical wheel `W_{n-1}`;
non-classical 3-connected generalised wheels first occur at `n=8`. `0` graphs admit
a 2-extremal orientation that is *not* a generalised wheel.)

(Plus: the only 3-connected members of the genuine truth set `L₃..L₇` are
`W₃,W₄,W₅,W₆` — classical wheels, because non-classical 3-connected generalised
wheels first appear at `n≥8`, e.g. the `n=10` 3-regular example above.) These
counts are now **exact** (the Eulerian-pruned search has no cap), superseding the
earlier capped sweep.

**Proof status.** By (P1) such a `D` has `MC=0`, so it is not a directed-Hajós join
(which carries a `(v,\{u,w\})` mixed cut). And any **non-empty-A** 2-Hajós tree
join has a 2-vertex-cut: a block `D_i` with interface digon `{u_i,v_i}` has ≥1
private internal vertex, and deleting `{u_i,v_i}` isolates the block interior. So a
3-connected member must be **empty-A = a generalised wheel** (not necessarily the
*star-tree* one — non-star empty-A tree joins can be 3-connected, as the `n=10`
example shows). **Hence `3-connected 2-extremal ∈ H₂ ⇒ generalised wheel`.** But
concluding `∈ H₂` is precisely the **3-connected special case of Conjecture 9.2** —
*not* independently established here. So the base case is reduced to (a special
case of) the conjecture, not closed.

## Inductive step: a 2-vertex-cut splits `D` into smaller 2-extremal pieces — **CIRCULAR**

For the induction, at a 2-vertex-cut `{a,b}` we need `G₁+ab`, `G₂+ab` to be
underlying graphs of *smaller 2-extremal* digraphs (so the IH "2-extremal ⇒ planar"
applies). Splitting a 2-extremal `D` at a small cut into 2-extremal pieces (adding
a digon/arc across `{a,b}` on each side) **is exactly the seam-existence /
factorisation problem** — AAC's Lemma 5.4 (mixed-cut ⇒ directed-Hajós factor) and
the tree-join inverse (R-a/R-b). That is the open core attacked all session.

Crucially, planarity offers **no shortcut**: the 2-sum needs `G_i+ab` planar, and
the only handle on that is the IH, which applies **only** to 2-extremal graphs — so
the pieces *must* be shown 2-extremal, i.e. the cut must factorise. There is no
weaker, purely-topological induction because `G_i+ab` for an arbitrary split is not
given planar.

## Net

`CONJECTURE-P` is sandwiched between two faces of Conjecture 9.2:
- its **base case** = the 3-connected case of 9.2 ("3-connected 2-extremal ⇒
  generalised wheel");
- its **inductive step** = seam existence (R-a/R-b) at 2-cuts.

So every evident route to prove `2-extremal ⇒ planar` independently **reduces to
the main conjecture's open core**. This explains why the necessary-condition form
is not a cheaper foothold. What remains genuinely actionable from route (a):

1. **Disprove**: hunt a non-planar 2-extremal digraph (would refute 9.2 outright;
   needs a non-`H₂` generator or the `n=8` enumeration — the Eulerian-pruned
   `geng` search now covers sparse `n=7,8` exactly, see `planarity_search.py`).
2. **Prove the 3-connected case of 9.2** (= base case = "3-connected 2-extremal ⇒
   **generalised wheel**") as a self-contained sub-theorem; with (P1) it is the
   `MC=0`, no-2-vertex-cut case (so: `MC=0` + no 2-vertex-cut ⇒ empty-A generalised
   wheel), possibly more tractable than the full conjecture but still open.

## Reproduce

```bash
PYTHONPATH=problems/two_extremal_digraphs/scripts \
  .venv/bin/python problems/two_extremal_digraphs/scripts/planarity_search.py
```
`scripts/planarity_search.py` runs the `K₅`/`K₃,₃` test, the 3-connected
generalised-wheel classification, and the sparse-non-planar disproof sweep, using
an **exact** Eulerian-pruned 2-extremal-orientation enumerator (no cap). Run
`--validate` to compare it against the naïve `3^{|E|}` reference on small graphs
(C5/W4/W5/W6/K4/K3,3/K5/prism/octahedron — all match), `--quick` for the fast
subset, `--three-nmax N` / `--sparse-nmax N` to bound the sweeps. Reuses
`h2_oracle`; needs `networkx`; finds `geng` via `PATH`.
