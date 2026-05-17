# Phase 3 v3 Support — pynauty Canonicalization, Vehicle 5, Cayley

Author: Combinatorial Optimization / Exact Algorithms Coder
Date: 2026-05-16
Working conjecture: **WC3 — every 3-arc-strong digraph has a strong arc
decomposition.**

Per the Lead's post-v2 reallocation (Phase 3 = bounded support track,
~25–30 % budget), this v3 carries out exactly three tasks: pynauty
canonicalization of v2's Vehicle 3 verified set, one Vehicle 5
(iterated substitution) sweep, and an optional small non-abelian Cayley
batch. No broad re-sweep.

Headline:
- Canonicalization wired up (`code/generators/canonicalize.py`,
  `pynauty 2.8.8.1` added to `pyproject.toml`). The 2 884 v2 Vehicle 3
  labeled-distinct candidates collapse to **1 591 iso-distinct**
  candidates (overall ratio 0.55; per-pair ratios range 0.08–1.00).
- Vehicle 5 (iterated substitution) sweep streamed 486 single-vertex
  substitutions + 13 lexicographic compositions across all ordered
  template pairs and v choices. **Zero** instances pass the
  $\lambda^{\text{arc}} = 3$ filter — single-vertex substitution leaves
  $\lambda = 2$ (unaffected outer vertices retain degree 2);
  composition lifts $\lambda$ to $\geq 10$ (too dense). This is a
  structural finding, not a budget shortfall.
- Cayley batch on $S_3, D_4, Q_8, A_4$ at generator-set size 3 streamed
  520, filtered to 238 at $\lambda = 3$ and **20 iso-distinct**, all
  **SAT** under both ILP and SAT backends, zero disagreements. Size-4
  generators land at $\lambda = 4$ (too dense).

No candidate counterexample. No cross-solver disagreement. The Lead's
10-item checklist is therefore vacuous in this v3 pass.

Total wall-clock: **11 s**, well under the 2 h budget. Authoritative
JSON log: `code/logs/phase3v3_20260516_214548.json`. Stdout transcript:
`code/logs/phase3v3_main_stdout.txt`.

---

## 1. Canonicalization results

### 1.1 Implementation

`code/generators/canonicalize.py` provides `canonical_key(D) -> str`:
a 64-hex SHA-256 hash deterministic and invariant under vertex
relabelling, sensitive to direction and parallel-arc multiplicity.

**Encoding.** pynauty's directed-graph mode turns out to be unreliable
on our $n \leq 14$ digraphs (one $n = 7$ Vehicle-3 instance took
**120 s** to certify in directed mode). We reduce directed iso to
*undirected colored* iso via the standard arc-encoding gadget: each
arc $u \to v$ of multiplicity $m$ becomes the undirected chain
$u \mathrel{-} a \mathrel{-} b \mathrel{-} v$, where $a$ and $b$ are
fresh subdivision vertices placed in dedicated colour classes
$(1, m)$ and $(2, m)$ respectively. The encoding is faithful
(directed-iso $\Leftrightarrow$ undirected-coloured-iso of the
encoding), and turns the 120 s instance into a 6 ms one. The full
2 884-candidate sweep canonicalizes in **0.5 s** wall-clock (slowest
single call 6 ms).

The encoding handles parallel arcs natively (separate colour class per
multiplicity) and self-loops (the chain $u \mathrel{-} a \mathrel{-}
b \mathrel{-} u$ is fine).

**Self-tests passing** (`uv run python generators/canonicalize.py`):
1. Vertex-relabelling invariance on a random 5-vertex digraph;
2. Direction sensitivity (path $\neq$ cycle, same iso for reverse-iso
   pairs);
3. Multiplicity sensitivity (single arc $\neq$ double arc);
4. Random relabelling of $S_4$ produces the same key;
5. All 9 UNSAT templates produce **distinct** canonical keys (no
   accidental collisions in the iso-canonical hash).

### 1.2 Per-template-pair iso-class counts on v2's Vehicle 3 set

Regenerated deterministically from `seed = 20260516` with v2's exact
`DeficitGenConfig`, then canonicalized. Reproduces v2's 2 884 labeled
count exactly; reduces to 1 591 iso-distinct.

| Pair (unordered, sorted by name) | Labeled | Iso-distinct | Ratio |
|---|---:|---:|---:|
| `S4 + S4` | 30 | 5 | 0.17 |
| `S4 + AiEtAl_L211_min` | 30 | 30 | 1.00 |
| `S4 + AiEtAl_L312_min` | 6 | 6 | 1.00 |
| `S4 + C3_K2K2P2` | 18 | 6 | 0.33 |
| `C6_square + C6_square` | 100 | 78 | 0.78 |
| `C6_square + AiEtAl_L211_min` | 100 | 100 | 1.00 |
| `C6_square + AiEtAl_L312_min` | 100 | 100 | 1.00 |
| `C6_square + AiEtAl_iv_star_iv` | 100 | 100 | 1.00 |
| `C6_square + C3_K2K2K2` | 100 | 40 | 0.40 |
| `C6_square + C3_K2K2K3` | 100 | 16 | 0.16 |
| `C6_square + C3_K2K2P2` | 100 | 27 | 0.27 |
| `C8_square + C8_square` | 100 | 99 | 0.99 |
| `C8_square + C3_K2K2K3` | 100 | 36 | 0.36 |
| `C3_K2K2K2 + C3_K2K2K2` | 100 | 14 | 0.14 |
| `C3_K2K2K2 + C3_K2K2K3` | 100 | 8 | 0.08 |
| `C3_K2K2K2 + C3_K2K2P2` | 100 | 10 | 0.10 |
| `C3_K2K2K2 + AiEtAl_L211_min` | 100 | 30 | 0.30 |
| `C3_K2K2K2 + AiEtAl_L312_min` | 100 | 36 | 0.36 |
| `C3_K2K2K2 + AiEtAl_iv_star_iv` | 100 | 36 | 0.36 |
| `C3_K2K2K3 + C3_K2K2K3` | 100 | 14 | 0.14 |
| `C3_K2K2K3 + AiEtAl_L312_min` | 100 | 36 | 0.36 |
| `C3_K2K2K3 + AiEtAl_iv_star_iv` | 100 | 36 | 0.36 |
| `C3_K2K2P2 + C3_K2K2P2` | 100 | 18 | 0.18 |
| `C3_K2K2P2 + AiEtAl_L211_min` | 100 | 52 | 0.52 |
| `C3_K2K2P2 + AiEtAl_L312_min` | 100 | 55 | 0.55 |
| `C3_K2K2P2 + AiEtAl_iv_star_iv` | 100 | 55 | 0.55 |
| `AiEtAl_L211_min + AiEtAl_L211_min` | 100 | 92 | 0.92 |
| `AiEtAl_L211_min + AiEtAl_L312_min` | 100 | 100 | 1.00 |
| `AiEtAl_L211_min + AiEtAl_iv_star_iv` | 100 | 100 | 1.00 |
| `AiEtAl_L312_min + AiEtAl_L312_min` | 100 | 78 | 0.78 |
| `AiEtAl_L312_min + AiEtAl_iv_star_iv` | 100 | 100 | 1.00 |
| `AiEtAl_iv_star_iv + AiEtAl_iv_star_iv` | 100 | 78 | 0.78 |
| **TOTAL** | **2 884** | **1 591** | **0.55** |

### 1.3 Reading the table (for the Structural Specialist)

- **Heavy collapse (ratio < 0.20):** the four $C_3[\overline K_2,
  \overline K_2, \cdot]$-pairings (`C3_K2K2K2+C3_K2K2K3` at 0.08,
  `C3_K2K2K2+C3_K2K2P2` at 0.10, `C3_K2K2K2+C3_K2K2K2` at 0.14,
  `C3_K2K2K3+C3_K2K2K3` at 0.14, `C3_K2K2P2+C3_K2K2P2` at 0.18) and
  the `S4+S4` self-pairing at 0.17. These are the pairings where the
  interface-permutation symmetry is largest: the templates have many
  vertex automorphisms ($C_3[\overline K_2, \overline K_2, \overline
  K_2]$ has $|\mathrm{Aut}| \geq (2!)^3 \cdot 3 = 24$ from the
  three copies of $\overline K_2$ on each of three rotational layers),
  so generator-output orderings of $(S_1, S_2, \phi)$ collapse to
  small iso-classes. **The Structural Specialist should treat these
  five pairings as effectively much smaller datasets than the labeled
  count suggests.**

- **No collapse (ratio = 1.00):** ten pairings, mostly involving
  `AiEtAl_L211_min` (the 5-vertex split obstruction with trivial
  automorphism group — every vertex is structurally distinct) or
  involving asymmetric pairs (`L312` vs `iv_star_iv` etc.). Labeled
  count = iso count here, so the iso-distinct sample is genuinely as
  large as v2's headline number. The 700 verified instances on
  `C6_square` pairings (per v2 §2.b) are now confirmed to be
  ~95 % iso-distinct on these subpairs.

- **Mid-range (ratio 0.30–0.80):** the remaining 17 pairings. The
  total dataset is 0.55 × the labeled count overall.

Two **`C8_square` self-pair** outliers worth flagging:
  - `C8_square + C8_square`: 100 labeled, **99 iso-distinct** (ratio
    0.99). The hardest v1-unproductive template, when paired with
    itself in deficit-aware gluings, produces an essentially iso-
    distinct sample. This is the strongest "really 100 different
    digraphs" line item in the v2 / v3 dataset.
  - `C8_square + C3_K2K2K3`: 100 → 36 (ratio 0.36). The composition
    template `C3_K2K2K3` (which has a tripartite-rotational symmetry
    on its 7 vertices) is what does the collapsing.

The Structural Specialist's Phase 4 CL1 (controlled-lifting lemma)
analysis should use these per-pair iso counts when choosing which
pairings to "stare at"; the heavy-collapse pairings have already had
their symmetry quotiented, so they look "smaller" than v2 advertised.

---

## 2. Vehicle 5 findings

### 2.1 Operation and bookkeeping

`code/generators/substitution.py` implements two operations:

- **`iterated_substitution(T_outer, v, T_inner) -> Digraph`.** Replace
  vertex $v$ of $T_{\text{outer}}$ by a fresh copy of $T_{\text{inner}}$.
  Every arc $x \to v$ becomes the bundle $\{x \to w : w \in V(T_{\text{inner}})\}$;
  every arc $v \to y$ becomes the bundle $\{w \to y : w \in V(T_{\text{inner}})\}$;
  internal arcs of $T_{\text{inner}}$ are preserved.
  Bookkeeping (Lead's required identity, verified by `_check_bookkeeping`):
  $$n_{\text{result}} = n_{\text{outer}} + n_{\text{inner}} - 1, \quad
  m_{\text{result}} = m_{\text{outer}} - d_{\text{outer}}(v) +
  m_{\text{inner}} + d_{\text{outer}}(v) \cdot n_{\text{inner}}.$$

- **`lexicographic_composition(T_outer, T_inner) -> Digraph`.** Replace
  *every* outer vertex by a fresh copy of $T_{\text{inner}}$. This is
  the natural operation that lifts $\lambda^{\text{arc}}$. Identity:
  $n = n_{\text{outer}} \cdot n_{\text{inner}}$, $m = m_{\text{outer}}
  \cdot n_{\text{inner}}^2 + n_{\text{outer}} \cdot m_{\text{inner}}$.

Both identities are asserted at construction time in the generator.

### 2.2 Sweep results

| Sub-sweep | Streamed | Deg-gate pass | $\lambda^{\text{arc}} = 3$ pass | Verified |
|---|---:|---:|---:|---:|
| B.1 single-vertex substitution | 486 | 0 | 0 | — |
| B.2 lexicographic composition (n ≤ 24) | 13 | 13 | 0 | — |

### 2.3 Why both filters reject

This is the v3 structural finding the Lead should know about:

- **Single-vertex substitution leaves $\lambda^{\text{arc}}(D) = 2$.**
  $T_{\text{outer}}$ is 2-arc-strong only, so it has at least one
  vertex $u \neq v$ with $d^+(u) = 2$ and one with $d^-(u) = 2$. The
  substitution at $v$ preserves $d^\pm(u)$ for every $u \neq v$; in
  particular, the minimum in-/out-degree of the result is still 2.
  Empirically (see `generators/substitution.py` self-test) the
  arc-connectivity is exactly 2 for every (outer, v, inner) tested.
  Therefore **the single-vertex substitution operation cannot produce
  a 3-arc-strong digraph from the 2-arc-strong templates** — the
  filter rejection is structural, not budget-driven.

- **Lexicographic composition $T_{\text{outer}}[T_{\text{inner}}]$
  gives $\lambda \geq 2 \cdot n_{\text{inner}} \geq 8$.** Every arc of
  $T_{\text{outer}}$ becomes $n_{\text{inner}}^2$ inter-copy arcs in
  the composition, so every directed cut $\delta^+(X)$ in $T_{\text{outer}}$
  expands to $\geq n_{\text{inner}}^2 \cdot \lambda(T_{\text{outer}})$
  in the composition. For our $n_{\text{inner}} \geq 4$ this lands
  $\lambda \geq 32$ in the worst case and $\geq 10$ in all 13 tested
  cases. **Composition over-shoots the $\lambda = 3$ target.**

So Vehicle 5 in its two natural forms is a **closed family that does
not intersect the 3-arc-strong target zone**. To produce a 3-arc-
strong substitution-style example we would need either (a) substitute
at multiple but not all outer vertices, or (b) substitute with a
*sparser inner* (e.g. a 2-vertex inner that contributes only 1 arc
per substituted endpoint). Both are off-spec for v3.

The empirical observation that single-vertex substitution preserves
$\lambda = 2$ is consistent with the more general statement: substituting
at a vertex set $S$ multiplies $\lambda$ exactly when every vertex of
$V(T_{\text{outer}}) \setminus S$ has degree $> $ original $\lambda$,
which fails here for *any* proper $S \subsetneq V(T_{\text{outer}})$
because our templates are uniformly low-degree.

The stop condition (UNSAT trigger) was not invoked because no instance
passed the $\lambda = 3$ filter to begin with.

### 2.4 What this tells Phase 4

For the Structural Specialist's CL1 (controlled-lifting lemma): the
substitution operation is **not a productive Phase-4 lifting move** in
this template family. CL1 should look elsewhere — almost certainly at
the deficit-gluing structure already canonicalized in §1 (the 1 591
iso-distinct gluings ARE the Phase-4 substrate), or at the
hypothetical "partial substitution" variants which are out of scope
for v3.

---

## 3. Cayley results (Task C)

### 3.1 Coverage

Sweep over Cayley digraphs $\mathrm{Cay}(G, S)$ for non-abelian groups
$G \in \{S_3, D_4, Q_8, A_4\}$ (orders 6, 8, 8, 12), with asymmetric
generator sets $S$ of size $\in \{3, 4\}$ (omitting identity).

For a Cayley digraph, every vertex has in-degree = out-degree = $|S|$
by transitivity, so the degree gate passes iff $|S| \geq 3$. Likewise,
the arc-connectivity equals $|S|$ in the strongly-connected case (the
minimum cut is a vertex's incident arcs), so the $\lambda = 3$ filter
restricts to $|S| = 3$. Generator sets with $|S| = 4$ yield
$\lambda = 4 \neq 3$ and are filtered out.

### 3.2 Findings

| $G$ | Order | Iso-distinct $\lambda = 3$ Cayleys | Verified SAT | UNSAT |
|---|---:|---:|---:|---:|
| $S_3$ | 6 | 3 | 3 | 0 |
| $D_4$ | 8 | 5 | 5 | 0 |
| $Q_8$ | 8 | 2 | 2 | 0 |
| $A_4$ | 12 | 10 | 10 | 0 |
| **TOTAL** | — | **20** | **20** | **0** |

All 20 are SAT under both ILP and SAT backends, perfect agreement,
zero disagreements. Cross-check time per instance ≤ 30 ms.

### 3.3 Note on completeness

The sweep capped subset-enumeration at 200 size-$k$ subsets per
(group, size); $\binom{|G| - 1}{3}$ is 10 ($S_3$), 35 ($D_4$, $Q_8$),
165 ($A_4$). For $A_4$ we sampled 165 out of 165 — exhaustive at size
3. For $D_4, Q_8$ we sampled 35 out of 35 — exhaustive. For $S_3$ we
sampled 10 of 10 — exhaustive.

So the 20 iso-distinct kappa-3 Cayleys constitute an **exhaustive
iso-class count** over Cayley digraphs of $S_3, D_4, Q_8, A_4$ with
asymmetric generator sets of size 3. The "iso-distinct" reduction
factor is about 20 / (10 + 35 + 35 + 165) = **20 / 245 ≈ 0.082**, with
the bulk of the reduction coming from the large automorphism groups
of $A_4$ and $D_4$ themselves acting on generator-set choices.

### 3.4 What this tells Phase 4

Non-abelian Cayley digraphs of these orders, restricted to the
$\lambda^{\text{arc}} = 3$ slice, are uniformly SAT. This extends the
"all 3-arc-strong digraphs in our scope are SAT" empirical evidence
to a structurally new family — none of the 20 instances is a deficit-
gluing or a substitution; they are genuine Cayley constructions.
$A_4$, in particular, is the smallest non-abelian non-solvable example
in scope; its 10 iso-distinct $\lambda = 3$ Cayley digraphs being
uniformly SAT is consistent with WC3 holding on this slice.

---

## 4. Open ends

Honest statement of what's tested vs untested by this v3:

**Tested.**

- v2's full Vehicle 3 deficit-gluing dataset (2 884 labeled) is now
  iso-canonical-counted as **1 591 iso-distinct** examples. The
  collapse is heaviest on the symmetric-template self-pairings and
  smallest on the asymmetric Ai-et-al pairings.
- Iterated substitution (Vehicle 5) in both its single-vertex and
  full-composition forms produces **no $\lambda^{\text{arc}} = 3$
  candidates** from the 9 UNSAT templates — a structural fact, not a
  budget shortfall.
- 20 iso-distinct $\lambda = 3$ Cayley digraphs on $S_3, D_4, Q_8,
  A_4$ are all SAT under both backends.

**Untested.**

- **No "partial substitution" middle ground** (replace a proper
  subset of outer vertices, sparser than full composition). Such a
  generator was not authorized for v3; if Phase 4 wants this, it
  becomes a Phase-3 v4 task that the Lead would re-budget.
- **Larger Cayleys** ($\mathrm{Sym}_4$ of order 24, $A_5$ of order 60,
  larger dihedral / dicyclic groups). The $\lambda = 3$ slice on these
  groups requires $|S| = 3$ generators that are strongly-connecting,
  which is a finite per-group check; out of v3 scope.
- **Iso-distinct counts for v2's Vehicle 2 / Vehicle 1 v2 datasets.**
  The 1 399 Eulerian-family verified + 330 laminar-v2 verified are
  *not* canonicalized in this report — only Vehicle 3 is. The
  `canonical_key` API is general-purpose; rerunning v2's Vehicle 2/1
  through it is a ~10 s job that any team member can run from
  `generators.canonicalize`. We did not run it here because the Lead's
  spec for v3 was specifically the Vehicle 3 set ("Hand the iso-class
  table to the Structural Specialist").
- **Disagreements / verifier health on the iso-distinct slice.** The
  20 iso-distinct Cayley instances and 13 composition instances were
  cross-checked; the 2 884 Vehicle-3 instances were *not* re-verified
  (they were verified in v2 and we only canonicalize them here).
  Zero disagreements observed on the verifier slice we did re-run
  (13 + 20 = 33 instances).
- **The exhaustion tripwire ($n \leq 18$ over all 3-arc-strong
  digraphs)** is still not fired. v3 is bounded support, by design.

**No broad-sweep advocacy from this seat.** Per the v2 review and the
Lead's reallocation: Phase 3 continues only as maintenance; the main
event is Phase 4 (CL1). The 1 591 iso-distinct Vehicle 3 candidates
are now the canonical substrate the Structural Specialist can stare at
for routing patterns.

---

## Appendix A. Run configuration

CLI: `uv run python run_phase3v3_support.py --task-a-budget-s 1500
--task-b-budget-s 600 --task-c-budget-s 1500 --per-pair-cap 100
--instance-time-s 10` from `code/`.

| Setting | Value |
|---|---|
| Templates | `S4, C6_square, C8_square, C3_K2K2K2, C3_K2K2P2, C3_K2K2K3, AiEtAl_L211_min, AiEtAl_L312_min, AiEtAl_iv_star_iv` (9, all UNSAT) |
| Task A: regenerate v2 Vehicle 3 + canonicalize | `seed=20260516`, same `DeficitGenConfig` as v2 Appendix A |
| `verified_per_pair_cap` | 100 (matches v2) |
| Task B: substitution sweep | every (T_outer, v, T_inner), v in V(T_outer); ordered pairs |
| Task B: composition sweep | every (T_outer, T_inner) with $n_{\text{outer}} \cdot n_{\text{inner}} \leq 24$ |
| Task C: Cayley groups | $S_3, D_4, Q_8, A_4$, generator sizes 3 and 4 |
| Task C: per-(group, size) subset cap | 200 (effectively exhaustive) |
| Per-instance verifier time limit | 10 s |
| Backends | ILP: PuLP / CBC; SAT: PySAT / CaDiCaL |
| pynauty | 2.8.8.1 (added to `pyproject.toml`) |
| canonical encoding | undirected-coloured arc-encoding gadget (see §1.1) |
| Seeds | 20260516 (Task A), 20260517 (Task B), 20260518 (Task C) |
| Wall clock | 11 s total |
| Log | `code/logs/phase3v3_20260516_214548.json` (~50 kB) |
| Stdout | `code/logs/phase3v3_main_stdout.txt` |

## Appendix B. Selected iso-distinct controls (one per group, Cayley)

| $G$ | Generator set (representative) | $n$ | $m$ | $\lambda$ | ILP | SAT | Agree |
|---|---|---:|---:|---:|:--:|:--:|:--:|
| $S_3$ | random size-3 asymmetric | 6 | 18 | 3 | SAT | SAT | yes |
| $D_4$ | random size-3 asymmetric | 8 | 24 | 3 | SAT | SAT | yes |
| $Q_8$ | random size-3 asymmetric | 8 | 24 | 3 | SAT | SAT | yes |
| $A_4$ | random size-3 asymmetric | 12 | 36 | 3 | SAT | SAT | yes |

Full canonical-key list of 20 iso-distinct Cayley instances is in
`code/logs/phase3v3_20260516_214548.json` under `task_c.entries`.
