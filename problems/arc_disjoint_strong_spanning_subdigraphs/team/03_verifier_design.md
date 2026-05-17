# Verifier design — Strong Arc Decomposition (SAD)

Team role: Combinatorial Optimization / Exact Algorithms Coder.
Round-1 deliverable, design half. Pairs with `code/` under the same parent
directory. Conforms to `attack_plan.md` v3 §"Computational backbone" and to
`review.md` v2 Issue 3 (certificate-style requirement).

## 1. Exact problem statement

**Input.** A finite digraph `D = (V, A)`, encoded as a `networkx.MultiDiGraph`
to allow parallel arcs. We do not assume simplicity. We assume `|V| >= 2`.

**Output.** `SAT` together with a 2-partition `A = A_R \dot\cup A_B` such that
both `(V, A_R)` and `(V, A_B)` are strongly connected, or `UNSAT` together with
a refutation certificate (see §5). Either answer must be machine-checkable.

**Working equivalence.** A 2-coloring `x : A -> {R, B}` is a strong arc
decomposition iff every directed cut contains an arc of each color:
```
for all 0 != X subsetneq V:    1 <= |{e in delta^+(X) : x(e) = R}| <= |delta^+(X)| - 1.
```
Equivalently the same family of cut inequalities written with the indicator
`x_e in {0,1}` of "arc `e` is red".

**Necessary conditions** (sanity-checked upfront, not used for SAT
declarations): `D` must be strongly connected and 2-arc-strong. If either
fails we return `UNSAT` with the corresponding witness cut, without invoking
the optimizer.

## 2. ILP / cut-separation formulation (primary backend)

### Variables and base model

One binary per arc:
```
x_e in {0,1}    for every e in A(D)            (x_e = 1 means red)
```
No objective. We solve a feasibility ILP.

### Cut constraints (exponential, separated lazily)

For every nonempty proper `X subsetneq V`:
```
sum_{e in delta^+(X)} x_e          >= 1            (red leaves X)
sum_{e in delta^+(X)} (1 - x_e)    >= 1            (blue leaves X)
```
Equivalent compact form: `1 <= sum_{e in delta^+(X)} x_e <= |delta^+(X)| - 1`.

There are `2^n - 2` such inequalities. We never enumerate them. Instead we run
a feasibility solve with a **lazy callback**:

1. Pull the current integer assignment `\hat x` from the solver.
2. Build `D_R = (V, {e : \hat x_e = 1})` and `D_B = (V, {e : \hat x_e = 0})`.
3. For each color, decide strong connectivity by Tarjan / Kosaraju.
4. If `D_R` is not strong, pick any SCC `S` whose out-arcs in `D_R` are zero
   while it has an out-arc in `D` (it must, by case analysis); equivalently
   the smaller side of a violated directed cut. Add the red-cover cut.
5. Symmetrically for `D_B`.
6. If both colors are strong, accept.

For fractional relaxations at internal nodes we use a stronger separation:
for the currently relaxed `\bar x`, compute min `s-t` cut in the directed
capacitated graph with capacities `\bar x` (for red) and `1 - \bar x` (for
blue) for all pairs (or, in practice, for a designated root `r` to all other
vertices; this suffices because strong connectivity is equivalent to
"root-to-all" plus "all-to-root"). Any cut of value `< 1` is added as a
violated lazy cut. We default to integer-only callbacks for correctness; the
fractional separator is enabled as a tightening heuristic.

### Symmetry breaking

The color swap `R <-> B` is the unique non-trivial automorphism of the model.
We break it by fixing `x_{e_0} = 1` where `e_0` is the lexicographically
smallest arc by `(u, v, k)`. This halves the search space and does not change
feasibility.

### Backends

- **Gurobi** if available: use `Model.optimize` with
  `Model.Params.LazyConstraints = 1` and a `cbLazy` callback. Best
  performance, but optional.
- **PuLP + CBC** fallback (default for this repo, since Gurobi is not on the
  user's box): CBC does not support lazy callbacks. We run a **cutting-plane
  outer loop**: solve, separate violated cuts in Python, add them as
  permanent constraints, re-solve, until feasibility or proven infeasibility.
  This is mathematically equivalent and correct, only slower.

In either backend we cap iteration count and time; on timeout we return
`UNKNOWN` (never `SAT` or `UNSAT`).

## 3. SAT formulation with arborescence witnesses (cross-check backend)

### Variables

For each arc `e in A`:
```
x_e             color bit, 1 = red, 0 = blue
```
Choose roots `r_R`, `r_B in V` (default `r_R = r_B = v_0`, the first vertex).
For each color `c in {R, B}` and each direction `sigma in {out, in}` we
encode a single rooted `sigma`-branching `T_c^sigma`:

```
t^{c, sigma}_e in {0, 1}             arc e is in T_c^sigma
```

### Branching constraints

A rooted `out`-branching at `r` is a spanning subdigraph in which every
non-root vertex has in-degree exactly 1 and all arcs point away from `r`. We
encode:

1. **In-degree-one for non-roots.** For each `v != r_c` and color `c`,
   direction `out`:
   ```
   sum_{e = (u,v) in A} t^{c, out}_e = 1.
   ```
   For direction `in` (in-branching at `r_c`), out-degree of non-roots is 1:
   ```
   sum_{e = (v,u) in A} t^{c, in}_e = 1.
   ```
2. **Color compatibility.** An arc may be used in color `c`'s branching only
   if it is colored `c`:
   ```
   t^{R, sigma}_e -> x_e          equivalently (~t^{R, sigma}_e \/ x_e)
   t^{B, sigma}_e -> ~x_e          equivalently (~t^{B, sigma}_e \/ ~x_e)
   ```
3. **Connectedness / acyclicity of each branching.** In-degree-one plus
   reachability from the root is the cleanest condition. We use the standard
   *Miller-Tucker-Zemlin-style layer encoding for branchings*, expressed as a
   topological order:
   - introduce integer level variables `ell^{c, sigma}_v in [0, n-1]`,
     `ell^{c, sigma}_{r_c} = 0`;
   - if `t^{c, out}_{(u,v)} = 1` then `ell^{c, out}_v >= ell^{c, out}_u + 1`;
   - if `t^{c, in}_{(u,v)} = 1` then `ell^{c, in}_u >= ell^{c, in}_v + 1`.
   Integer levels are realized in CNF as direct or unary encoding of
   `ell in [0, n-1]`. For small `n` we use the unary "thermometer" encoding.
4. **Reach all vertices.** Because every non-root has degree 1 into / out of
   the branching and the levels prevent a cycle, the branching is a spanning
   tree of the right orientation iff it is connected. The in-degree-one and
   acyclicity constraints together with `n - 1` arcs (we enforce
   `sum_e t^{c, sigma}_e = n - 1`) already force a spanning arborescence;
   we add `sum t = n - 1` as a redundant but useful pruning constraint.

### Why arborescence witnesses, not transitive closure

A transitive-closure encoding (`reach(c, u, v)`) needs `O(n^2)` variables
plus `O(n^3)` Floyd-Warshall clauses **per color**, and silently accepts
solutions where the "reachability matrix" is over-asserted. The arborescence
encoding has `O(|A|)` color variables plus `O(n log n)` level bits per
(color, direction), and the witness is checkable in linear time outside the
solver. This is the form `attack_plan.md` v3 §"Computational backbone" item 2
mandates.

### Solver

`python-sat` (pysat) with CaDiCaL or Glucose 4. We use pseudo-boolean
encoding (via `pysat.card`) for the `=1` and `= n - 1` cardinality
constraints (sequential counter encoding). If a user has `ortools` we offer
a CP-SAT alternative that handles the cardinalities natively; the contract
is the same.

## 4. Cross-check protocol

For every benchmark instance:

1. Run `verify_ilp(D)` and `verify_sat(D)`.
2. Both must return one of `SAT`, `UNSAT`, or `UNKNOWN`.
3. **Disagreement on `SAT` vs `UNSAT` is a fatal error** and aborts the test
   suite with a non-zero exit code. Such an event indicates a bug in one of
   the two backends and must be triaged before any further use.
4. If both return `SAT`, **both** witness pairs `(A_R, A_B)` are independently
   re-validated outside the solver by:
   - `networkx.is_strongly_connected((V, A_R))`,
   - `networkx.is_strongly_connected((V, A_B))`,
   - `A_R \cap A_B == {}` and `A_R \cup A_B == A`.
   Any failure is fatal.
5. If both return `UNSAT`, we require at least one to produce a refutation
   certificate (§5). The other may emit only the boolean result; we log this.
6. If exactly one returns `UNKNOWN`, the suite passes if the determinate
   answer is consistent with the expected label (recorded in `benchmarks.py`)
   and we log a warning. If both return `UNKNOWN` the case is reported as
   inconclusive.

The cross-check is implemented in `code/cross_check.py`.

## 5. Obstruction extraction on UNSAT

We need a human-readable obstruction, not a 100k-line solver log.

### From the ILP backend

The lazy callback maintains the full list of cuts it added. When the solver
declares infeasibility we apply a **deletion filter** in the spirit of a
Quickxplain / minimal-unsat-core routine:

1. Let `C` be the set of accumulated cut constraints used during the proof of
   infeasibility (Gurobi can hand back an IIS; for CBC we run the deletion
   filter from scratch).
2. Drop one cut, re-solve. If infeasible, keep it dropped. Else restore.
3. Continue until no cut is droppable.
4. The remainder is a (locally) minimal unsat core of cuts.

We then attempt to lay the cores out as a laminar family:

- Sort by side-of-cut size `|X|`.
- Walk pairs `(X_i, X_j)`. If they cross (`X_i \cap X_j`, `X_i \setminus X_j`,
  `X_j \setminus X_i`, `V \setminus (X_i \cup X_j)` all nonempty), record the
  crossing as a "near-laminar" deviation and emit the pair as is.
- Otherwise output the family as a forest in the inclusion order.

### From the SAT backend

`pysat` supports UNSAT cores via the assumption-based interface. We add the
core cut/color constraints under assumption literals, ask the solver for the
core after `UNSAT`, then **translate selectors back to cut/color
constraints** in the same human-readable format as the ILP path. This makes
the two cores cross-comparable.

### Output format

`obstruction.json` per UNSAT instance, schema:
```
{
  "instance": "<name>",
  "backend": "ilp" | "sat",
  "cuts": [
    {"X": [v_0, v_1, ...], "size": k, "role": "red_cover" | "blue_cover"},
    ...
  ],
  "laminar": bool,
  "crossings": [[i, j], ...],
  "comment": "<free text>"
}
```

## 6. Benchmark validation set

Hard requirement: each benchmark records `name`, `vertices`, `arcs` (multiset),
`expected: SAT | UNSAT`, and `source`. See `code/benchmarks.py`.

### UNSAT side (must be UNSAT on a correct verifier)

- **`S_4`** — the 4-vertex tournament obstruction from
  Bang-Jensen & Yeo, *Decomposing k-arc-strong tournaments...*, Combinatorica
  24 (2004). Standard semicomplete witness that 2-arc-strong is not
  sufficient.
- **`C_{2k}^2`** for `k = 2, 3, 4` — the square of the directed cycle on
  `2k` vertices, viewed as a locally semicomplete digraph. Bang-Jensen &
  Huang, JCTB 102 (2012), establish these as the only 2-arc-strong locally
  semicomplete exceptions.

### SAT side (must be SAT on a correct verifier)

- **A small positive 2-arc-strong semicomplete digraph** — any 2-arc-strong
  tournament on `n >= 5` distinct from `S_4`, e.g. the doubly regular
  tournament on 7 vertices (`QR(7)`). Decomposability follows from
  Bang-Jensen & Yeo 2004.
- **A 3-arc-strong instance** — `K_5^*` (the complete bidirected graph on 5
  vertices, every unordered pair gives both arcs). 4-arc-strong, so by any
  positive theorem `>= 3`-arc-strong it is decomposable. The solver verifies
  this directly.

Benchmarks beyond this minimal list (semicomplete-composition exceptions,
Ai–He–Li–Qin–Wang split exceptions) require the team's math half to provide
the explicit arc lists. Those are recorded as `# TODO: source citation` stubs
in `benchmarks.py` and **not** counted toward round-1 pass/fail.

## 7. Expected outcomes

For the minimal validation set above, with both backends:

| name | n | expected | reason |
|------|---|----------|--------|
| S4 | 4 | UNSAT | Bang-Jensen–Yeo 2004 |
| C4_square | 4 | UNSAT | BJ–Huang 2012 |
| C6_square | 6 | UNSAT | BJ–Huang 2012 |
| C8_square | 8 | UNSAT | BJ–Huang 2012 |
| QR7_tournament | 7 | SAT | Bang-Jensen–Yeo 2004 (any 2-arc-strong tournament != S4) |
| K5_bidirected | 5 | SAT | 4-arc-strong; any positive K=3 theorem |
| C5_doubled | 5 | SAT | sanity: a 2-arc-strong circulant |

The cross-check script asserts agreement and prints a green pass table.

## 8. Critical correctness rules (also restated in `code/README.md`)

1. **Lazy cuts only.** Never enumerate `2^n - 2` cuts upfront.
2. **Branching encoding enforces color.** `t^{c, sigma}_e -> (x_e == c)`
   clauses are mandatory and tested by a unit check on a tiny manual case.
3. **Independent witness re-validation.** Every `SAT` answer is re-checked by
   recomputing `networkx.is_strongly_connected` on each color class before
   returning. Failure of re-validation is a fatal bug, not a soft warning.
4. **Never declare `UNSAT` without a proof artifact.** Either an unsat core
   from the solver, or — in the cutting-plane outer loop with CBC — the final
   list of separated cuts together with a proof that the resulting LP has no
   integer feasible solution (the solver-level infeasibility certificate).
5. **`UNKNOWN` is allowed on timeout.** It is treated as inconclusive and
   never collapses to `UNSAT`.
