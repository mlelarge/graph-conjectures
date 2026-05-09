# Phase 2b status: certificate reproduction gate

This file records the Phase 2b outcome from
`PEBBLING_CARTESIAN_PRODUCT_COUNTEREXAMPLE_PLAN.md`.

## Summary

Phase 2b is **passed at the Hurlbert L□L scale**: a full four-strategy
rational certificate for $\pi(L\Box L,(v_1,v_1))\le 108$ from
Hurlbert 2017 Theorem 10 has been transcribed, encoded with explicit
tree structure, and verified end-to-end by
`scripts/check_pebbling_weight_certificate.py` under exact rational
arithmetic. Derived bound $= 108 =$ claimed.

The Flocco–Pulaj–Yerger 96 certificate is **still paused** for the
reasons documented below (their public CSV format diverges from their
own save code).

## Smoke tests that passed

- `data/pebbling_product/certificates/P3_root0_le4.json`,
  `P4_root0_le8.json`, `K1_3_root0_le4.json` — single-strategy
  hand-derived bounds.
- `data/pebbling_product/certificates/C4_root0_le4.json` — two basic
  Hurlbert path strategies (CCW and CW) with dual multipliers
  $(1/4, 1/4)$, derived $\lfloor 7/2\rfloor + 1 = 4 = \pi(C_4)$.

These are useful as: (i) a validation that the rational checker parses,
verifies, and rejects perturbations; (ii) a working demo of the
multi-strategy averaging pattern Hurlbert uses for $L\Box L$. They are
not equivalent to a published-certificate reproduction.

## What does not pass yet: published $L\Box L$ certificate

Reproducing the $\pi(L\Box L)\le 96$ bound (Flocco–Pulaj–Yerger 2024,
Theorem 4.2) is **not** achieved. The relevant facts:

1. **Their certificates are public**, in
   `https://github.com/dominicflocco/Graph_Pebbling`,
   `results/lemke square/experiments/ls-bounds-updated/`.
   Each root $(r_1, r_2)$ has multiple files
   `ls_sym_cert<i>-v(r1, r2).csv` (an 8x8 weight matrix) and
   `ls_sym_edges<i>-v(r1, r2).csv` (a directed-edge list of the
   underlying subtree strategy on $V(L\Box L)$).

2. **Their weights are stored as floats**, not rationals. Most entries
   are integer-valued (0, 1, 2, 4, 8, 16) but the published CSVs also
   contain values such as `31.56`, `3.25`, `1.75`. Of these, `3.25`
   and `1.75` are exact dyadic rationals; `31.56` is a rounded LP
   value whose true rational form is not in the CSV.

3. **The dual multipliers are not in the public files.** The paper
   says the $r=(v_1, v_1)$ bound uses 10 symmetric tree strategies (and
   6 strategies for other roots) but the FPY repo does not separately
   record the LP dual values $\alpha_i$.

4. **The $r=(v_1,v_1)$ certificates are not in `ls-bounds-updated/`**
   — our checker would have to first reconstruct what root indexing
   the repo uses (presumably 0-based, matching their `v(0, 0)` = first
   factor's first vertex).

So re-checking $\pi(L\Box L)\le 96$ end-to-end requires an
**ingestion adapter** of bounded scope, not an MILP generator:

- a) parse the weight CSV into an integer-vertex matrix;
- b) parse the edges CSV into a directed-tree subgraph of $L\Box L$;
- c) reconstruct rationals from the stored decimals (exact for dyadic
  values; for `31.56`-style rounded entries, treat as a hint and either
  re-solve a small LP to find a rational close to it, or refuse the
  cert and request the LP solution at higher precision);
- d) determine the dual multipliers $\alpha_i$ — either uniform
  $1/k$ (the "averaging" form Hurlbert uses) or by re-running the LP
  master problem with the strategies as fixed inputs;
- e) feed the resulting JSON to
  `scripts/check_pebbling_weight_certificate.py` and check the
  derived bound.

This is closer to a one- to two-week ingestion task than an MILP
implementation. The earlier draft of this file overstated the cost.

## What unblocks the $L\Box L$ reproduction (revised)

In order of effort:

1. **Write a `flocco_pulaj_yerger_ingest.py` adapter** that downloads
   the per-root cert and edges CSVs, parses them, and emits one
   certificate JSON per root. Use Python's `decimal.Decimal` to convert
   the published floats to exact `Fraction` (this preserves any value
   stored to a finite number of decimal places, including `31.56`).
   Run our rational checker on the emitted certificates. Resolve any
   per-root mismatches between (sum of strategy weights, derived
   bound, and the paper's reported per-root bound) one root at a time.

2. **Hand-transcribe Hurlbert 2017 Theorem 10's $T_3$ matrix** for
   $r=(v_1, v_1)$ and supply a valid supporting tree if the aggregate
   matrix is to be checked as one nonbasic strategy. The matrix itself
   is described in text (lines 439–447 of the arXiv PDF), so the
   weights are mechanical; the tree/strategy structure still has to be
   made explicit. Expected derived bound, if this encoding validates:
   $108$.

3. **Re-run the FPY MILP** (would require Gurobi or rewriting their
   model under HiGHS or CBC). Out of scope for this iteration.

The plan's pre-committed pivot rule still applies: do not advance to
Phase 3 on $L\Box L$ as if the certificate gate had passed. Until at
least step 1 above is executed and a verified bound is rationally
checked locally, Phase 2b is **paused**.

## Acceptance summary

| Target | Phase 2b status | Evidence |
|---|---|---|
| Path $P_n$ smoke | smoke passed | `tests/test_phase2a_checker.py` |
| Star $K_{1,k}$ smoke | smoke passed | same |
| $C_4\le 4$ via 2 averaged strategies | smoke passed (synthetic) | `data/pebbling_product/certificates/C4_root0_le4.json` |
| FPY repo CSV ingestion (parsing) | adapter built | `scripts/ingest_flocco_pulaj_yerger.py`, `tests/test_phase2b_fpy_ingest.py` |
| FPY $L\Box L \le 96$ certificate | **paused, blockers identified** | see "FPY format diagnostics" below |
| Hurlbert 2017 Theorem 10 $T_3$ matrix arithmetic | passed (arithmetic only) | `tests/test_hurlbert_T3_arithmetic.py` |
| **Hurlbert 2017 Theorem 10 four-strategy certificate ($L\Box L\le 108$)** | **passed (full rational certificate)** | `data/pebbling_product/certificates/Hurlbert_T1_T2_T3_T4_v1v1_le108.json`, `tests/test_hurlbert_T1_T2_T3_T4_certificate.py` |

## FPY format diagnostics (2026-05-09)

Live download of `ls_sym_cert0-v(0, 1).csv` and `ls_sym_edges0-v(0, 1).csv`
plus 15 sibling certificates was successful. Parsing succeeds.
End-to-end checker run reveals three concrete blockers, all in the FPY
side, none in our checker:

1. **Two distinct vertex labellings of $L$ are involved.** The FPY repo
   uses its own labelling
   $(0,1),(0,2),(1,3),(2,4),(2,5),(2,6),(3,4),(3,5),(3,6),(3,7),(4,7),(5,7),(6,7)$
   (from `py/main.py` `loadGraph()`), distinct from Hurlbert's. Stored as
   `data/pebbling_product/graphs/L_fpy.json` with the explicit
   isomorphism back to our $L$. Local $\pi(L_{\rm fpy})=8$ confirmed
   ($8$-vertex Lemke is class 0 regardless of relabelling).

2. **The weight matrix is transposed relative to filename coordinates.**
   For filename `v(0, 1)`, the root weight is found at `matrix[1][0]`,
   not `matrix[0][1]`. Equivalently, `matrix[i][j]` is the weight at
   vertex $(j, i)$ in the row–column convention of the matrix CSV.
   Confirmed empirically: under the transposed reading, `matrix[1][0]=0`
   for `v(0, 1)`, matching the required root weight $w(r)=0$.

3. **The edges file is not a literal rooted tree.** Under the
   `col0 = parent, col1 = child` convention, vertex $(2, 3)$ has two
   incoming edges, and the only vertex with no incoming edge is
   $(0, 3)$, **not** the filename root $(0, 1)$. So the edges CSV
   uses some other convention than (parent, child)-pairs of a tree
   rooted at the filename root: it might encode tree edges of a
   rotated / re-labeled tree, or encode the strategy as a non-basic
   structure that we have not decoded. Under
   `col0 = child, col1 = parent`, eight different vertices have
   in-degree $> 1$, so that interpretation is even further from a
   rooted tree.

Despite the failures above, the **weight side** of the certificate is
parseable and gives a numerically meaningful upper bound assuming the
FPY MILP enforces uniform $\alpha = 1/T$ averaging
(see `automating_weights.txt` lines 893–901, eq. 3.10):

$$\pi(L\Box L, r)\le \left\lfloor \frac{\sum_t b_t}{T}\right\rfloor + 1.$$

For root $v(0, 1)$ with $T=16$:

$$\sum_t b_t = \frac{29978}{25}, \qquad \frac{1}{T}\sum_t b_t = \frac{14989}{200} \approx 74.945,$$

so the implied bound for this root is $\le 75$, well below 96. That is
plausible: the FPY paper reports per-root bounds in a Table 3 the abstract
of which is paraphrased "the pebbling bound dropped below 96 for all
roots $r\ne (v_1, v_1)$, and often very quickly" (extracted PDF, lines
1426–1428). But we have **not** verified it because tree-structure
validation fails on the edges file as written.

## What I learned from FPY's source code

`py/TreeStrategy.py` defines:

```python
def saveCertificate(self, filename):
    n = int(math.sqrt(len(self.graph.nodes)))
    cert = np.zeros((n, n))
    for v in list(self.nodes):
        i = int(v[2])
        j = int(v[7])
        cert[i][j] = round(self.getWeight(v), 4)
    pd.DataFrame(cert).to_csv(filename)
```

The hard-coded character offsets `v[2]` and `v[7]` only line up if
NetworkX renders cartesian-product vertices with a leading character
(e.g., a leading space). With the standard NetworkX rendering
``"(i, j)"`` (six characters for single-digit indices), those offsets
land on a comma and on out-of-range, which would crash. The fact that
a CSV exists at all means the actual `v` strings at runtime had a
different format than ``str((i, j))``. Without running their code, we
cannot reverse this unambiguously from the CSV alone.

`py/main.py` calls `strategies[t].saveCertificate("ls_sym_cert"+ str(t)
+ "-v" + str(graph.root) + ".csv")`, so the filename is hand-built and
the **filename root and the matrix's actual zero-weight vertex come
from different code paths** (the filename uses `str(graph.root)`, the
matrix uses positional character extraction from per-vertex strings).
This is consistent with the empirical mismatch we saw on
`ls_sym_cert0-v(0, 1).csv` (root reads as $(0, 1)$ from the filename
but the matrix puts the zero at `matrix[1][0]`, and the edges file
implies a root at $(0, 3)$ instead).

The edges file is written by `pd.DataFrame(self.edges).to_csv(...)`
(NetworkX-style `(source, target)` columns). Each `paths[t]` is the
set of MILP arc variables `X[t][(i, j)].x = 1`, written without
deduplication or post-processing. The published file having 35 arcs on
35 vertices, with one vertex of in-degree 2, suggests either: (a) the
solver returned a fractional / non-tree-integer point that was rounded
into the saved arc list; or (b) the code path that produced the
`ls-bounds-updated/` data is not the one in the current `main` branch.

## Concrete next steps to actually pass the FPY gate

1. **Run their code locally** (clone the repo, install Gurobi or
   CPLEX, call `treeStrategyOptSymCrank()` on the Lemke square at
   root $(0,1)$) and capture the in-memory `paths[t]` and
   `weight_func[t]` BEFORE serialization. That gives ground truth
   without CSV-format reverse-engineering. This requires a commercial
   solver license.

2. **Or contact Flocco–Pulaj–Yerger** for a structured (non-CSV) dump
   of the per-strategy weights and tree edges as JSON or pickle.

3. **Hurlbert 2017 Theorem 10 arithmetic reproduction** (the precursor
   step). The 8×8 averaged matrix $T_{\rm avg}$ from *G. Hurlbert,
   The weight function lemma for graph pebbling*, J. Combinatorial
   Optimization 34(2) (2017), 343–361 (arXiv:1101.5641, **not** the
   math/0406024 survey), Theorem 10, was transcribed into
   `data/pebbling_product/certificates/Hurlbert_T3_v1v1_arithmetic.json`
   and its arithmetic conditions verified by
   `scripts/check_hurlbert_T3_arithmetic.py` (root $=0$, every other
   entry $\ge 1$, sum $=107$, derived bound $108$). This is
   arithmetic-only and does **not** by itself constitute an
   independent rational certificate.

4. **Hurlbert 2017 Theorem 10 four-strategy certificate**: **done**.
   The four basic-row weight matrices $T_1, T_2, T_3, T_4$ from
   Figure 5 of arXiv:1101.5641 were transcribed from the
   layout-preserving PDF text extraction (verified by
   $(T_1+T_2+T_3+T_4)/4 = T_{\rm avg}$, sum $107$). The Hurlbert WFL
   paper uses a Lemke-graph vertex labelling distinct from FPY's:
   exhaustive search over 8! relabellings produced 12 valid
   labellings under the nonbasic doubling rule (degree sequence of
   $v_1\dots v_8$: $3, 5, 4, 2, 3, *, *, 4$). One was selected and
   recorded in `scripts/build_hurlbert_T_strategies.py` as
   `WFL_TO_FPY = (4, 3, 2, 1, 5, 0, 6, 7)`. Tree edges for each
   strategy were generated by greedy BFS from the root respecting
   $w(v^+)\ge 2w(v)$. The full four-strategy certificate with dual
   multipliers $(1/4,1/4,1/4,1/4)$ is at
   `data/pebbling_product/certificates/Hurlbert_T1_T2_T3_T4_v1v1_le108.json`.
   The rational checker accepts it: per-strategy $b_T$ values
   $(100, 114, 102, 112)$ summing to $428 = 4 \cdot 107$, so
   $\sum_i \alpha_i b_i = 107$ and derived bound
   $\lfloor 107\rfloor + 1 = 108$. Cross-checked by
   `tests/test_hurlbert_T1_T2_T3_T4_certificate.py`.

5. **Flocco–Pulaj–Yerger 96 certificate**: still paused for the
   format-decoding reasons documented in "FPY format diagnostics"
   above. With Hurlbert's 108 now rationally checked locally, FPY 96
   is no longer the gating step; it is an *improvement* of an
   already-passed gate.
