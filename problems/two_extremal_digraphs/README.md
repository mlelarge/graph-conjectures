# Characterizing 2-extremal digraphs (Aboulker–Aubian–Charbit, Conjecture 9.2)

**Source:** *Digraph Colouring and Arc-Connectivity*, arXiv:2304.04690, Section 9.
**Status target:** open. Selected 2026-05-29 as the most attackable still-open Aboulker
conjecture (recon score 7/10, lean **disprove**), excluding the Path-FAS problem
(arXiv:2402.10782) which is owned by a separate team.

## The conjecture

Work with loopless digraphs without parallel arcs (digons `[x,y] = {xy, yx}` allowed).

- **Dichromatic number** `χ⃗(D)`: min `k` such that `V(D)` partitions into `k` classes each
  inducing an **acyclic** subdigraph.
- **Local arc-connectivity** `λ(x,y)`: max arc-disjoint `x→y` dipaths (= min `x,y`-dicut, Menger);
  `λ(D) = max` over ordered pairs.
- `D` is **k-extremal** if it is strong, biconnected (underlying graph 2-connected), and
  `χ⃗(D) = λ(D) + 1 = k+1`. So **2-extremal** means `λ(D)=2` and `χ⃗(D)=3`.
  (Lemma 4.1 of the paper: every k-extremal `D` is Eulerian and `(k+1)`-dicritical.)
- **Directed Hajós join** (Def 1.5) and **2-Hajós tree join** (Def 9.1, carries an
  *even-leaf-path parity* condition on the `B`-edges) are two composition operations.
- **`H₂`** = smallest digraph class containing all **symmetric odd cycles** and closed under
  the directed Hajós join and the 2-Hajós tree join. The paper proves (routine) **`H₂ ⊆ {2-extremal}`**.

> **Conjecture 9.2.** A digraph is 2-extremal **iff** it belongs to `H₂`.

The paper proves the analogous structure theorem for **all `k ≥ 3`** (Thm 1.8); `k=1` is just the
directed cycles. **Only `k=2` is open** — the `k≥3` min-dicut induction (Lemma 3.3) degrades
at `k=2` (two colour classes can cross a size-2 dicut), and the 2-Hajós parity condition is the
suspected repair.

## Goal

Either **exhibit a verified 2-extremal digraph outside `H₂`** (disprove — the recon lean), or
**prove the structure theorem** via min-dicut induction with the parity repair.
A single verified counterexample settles it.

## State of play (from recon probe, 2026-05-29)

- Truth set fully enumerated for **n ≤ 5**: `|L₃|=1, |L₄|=1, |L₅|=3`; **every** member
  independently matched to a named `H₂` construction. **Conjecture survives to n=5, zero counterexamples.**
  - `L₃ = {sym C₃}`; `L₄ = {directed wheel W₃}`; `L₅ = {sym C₅, W₄, Hajós join C₃#C₃}`.
- Structural fact surfaced: **generalised wheels** (2-Hajós tree join with empty `A`) are an
  *irreducible* `H₂` base family — directed Hajós joins alone miss `W₃, W₄`.
- **Two blockers (engineering, not math walls):**
  1. Pure-Python enumeration stalls at n=6 (blind `~4¹⁵` DFS). Fix: generate by **orienting
     2-connected underlying simple graphs with Eulerian-balance**, canonical-dedup via nauty/VF2.
  2. The `H₂` oracle is **sound but incomplete** — it omits general non-empty-`A` 2-Hajós tree
     joins. A "not-in-`H₂`" flag is currently an *oracle gap, not a counterexample* until the
     full recursive recognizer exists.
- The paper's own nontrivial example lives at **n=8** (Figure 11) — the regime we must reach.

## Method discipline

- **Empirical survival is verification, never a theorem.** Report "survives to n=K" or
  "counterexample at n=K (independently re-verified)".
- Every flagged candidate must be re-checked by a **second, independently-coded** oracle and a
  recomputation of `χ⃗, λ`, biconnectivity, strongness before it is called a counterexample.

## Layout

- `scripts/` — enumerators, the `H₂` recognizer, cross-checks. `enumerate_2extremal_v0_recon.py`
  is the seed from recon (validated primitives: `χ⃗` backtracking dicolouring, `λ` unit-cap max-flow,
  2-extremal test; sanity-checked on sym C₃/C₅/C₇ and the even-cycle negative control).
- `docs/` — proof attempts, lemma status, decision log.
- `tests/` — oracle soundness tests (known `H₂` members must recognize as in-`H₂`).
- `data/` — enumerated truth sets `Lₙ`.

Secondary track (different conjecture, same paper-mining batch): `../unvd_vertex_deletion/`
(arXiv:2410.23566 Conjecture 9 — `unvd(D) ≤ C·unvd(D−v)`; recon found the max internal ratio is
exactly 2.0 for all DAGs with `unvd ≤ 6`).
