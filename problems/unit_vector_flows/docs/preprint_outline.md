# Preprint outline — Computer-assisted $S^2$-flow theorems on cubic graphs

A consolidated outline for a single self-contained preprint built from
the artefacts already in this repository. The package is publishable
as is: it does **not** claim to settle Jain's first conjecture, but
provides a sharp finite theorem plus a constructive closure theorem
plus negative obstructions, all with replayable certificates.

Working title:

> **Replayable $S^2$-flow certificates on cubic graphs: a finite
> theorem to 28 vertices and a constructive closure.**

Target venue: combinatorics + computer-assisted-proof journal
(*Mathematics of Computation*, *Experimental Mathematics*, *JCTB* if
the obstruction story carries the paper). Estimated length: 25–35
pages plus reproducibility appendix.

## Section budget (rough)

| # | Section | Pages |
|---:|---|---:|
| 1 | Introduction and disambiguation of Jain's two conjectures | 2 |
| 2 | Definitions: $S^2$-flows, cubic reductions, snarks | 2 |
| 3 | Interval-Krawczyk certification method | 4 |
| 4 | Enumeration theorem through 28 vertices | 3 |
| 5 | CDC obstruction: oriented 4-CDC $\Rightarrow$ NZ 4-flow on cubic | 3 |
| 6 | Gadget closure theorem | 4 |
| 7 | Decomposition frontier and replayable membership | 3 |
| 8 | Failed flower routes | 3 |
| 9 | Reproducibility appendix | 2 |

---

## 1. Introduction and disambiguation

**Goal.** Set the problem, separate Jain's two conjectures clearly,
and state the headline result.

**Key paragraphs.**

- Jain's first conjecture: every bridgeless graph admits an
  $S^2$-flow.
  *(unsettled; what this paper studies.)*
- Jain's second conjecture: there exists $q : S^2 \to \{\pm 1, \pm 2,
  \pm 3, \pm 4\}$ with $q(-x) = -q(x)$ and zero-sum on every
  equilateral great-circle triple. **Disproved** by
  Ulyanov (2026, arXiv:2603.23328) with two finite point-set
  counterexamples; SAT-certified and Lean-verified.
- HMM (2026, arXiv:2602.21526v1) gives the geometric characterisation
  (Theorem 1: cubic + $S^2$-flow $\Leftrightarrow$ equiangular
  $S^2$-immersion) and a rank obstruction (Theorem 3:
  $\operatorname{rank} S_{\mathbb Q}(\varphi) \le 2$ + odd-coordinate-free
  $\Rightarrow$ NZ 4-flow).
- MMRT 2025 ([cdc_negative_calibration.md](cdc_negative_calibration.md))
  gives the CDC linkage: oriented $d$-CDC $\Rightarrow$ $H_d$-flow
  $\Rightarrow$ $S^{d-2}$-flow. The corollary at $d = 4$ rules out
  oriented 4-CDCs on snarks.

**Headline result.** Two theorems, one upper-bound and one
constructive:

> **Theorem A.** Every nontrivial snark on at most 28 vertices admits
> an $S^2$-flow.

> **Theorem B.** The class of cubic graphs that admit a constructive
> $S^2$-flow is closed under triangle blow-up and 3-edge-cut dot
> product. Starting from the 3 247 certified base graphs of
> Theorem A, the resulting closure contains a strict superset, with
> explicit decomposition certificates for membership.

**Disclaimer.** Jain's first conjecture remains open; our results
neither prove nor refute it. We do, however, give the largest finite
$S^2$-flow certification to date, identify CDC as the wrong route
for snarks, and exhaust three natural structural attacks on flower
snarks.

**Citations.** Jain (unpublished; cited via HMM); HMM
(arXiv:2602.21526v1); Ulyanov (arXiv:2603.23328v1); MMRT 2025
(*Cycle double covers in cubic graphs*).

---

## 2. Definitions: $S^2$-flows, cubic reductions, snarks

**Goal.** Compact but complete definitions to make Sections 3–8
mechanical.

**Definitions to give.**

- Cubic graph; bridgeless cubic graph.
- $A$-flow for an abelian group $A$; nowhere-zero flow.
- $S^2$-flow $\varphi : E(G) \to S^2$, with sign convention at each
  vertex.
- Pinning gauge: $\mathrm{SO}(3)$ symmetry of the system; fix by
  setting $\varphi$ at vertex $0$ to a canonical 120-degree triple.
- Drop-redundant vertex: each vertex's Kirchhoff equation is a vector
  identity; the sum over all vertices is zero, so on a connected
  cubic graph we drop one vertex's Kirchhoff to get a square
  polynomial system.
- Snark; nontrivial snark (girth $\ge 5$, cyclically $\ge 4$-edge-
  connected, chromatic index 4).
- Cycle double cover (CDC); oriented CDC; $H_d$-flow.

**Lemma (vertex-Kirchhoff has rank 3 linear redundancy).** The vertex
Kirchhoff equations on a connected cubic graph carry 3 dependencies;
after gauge-fixing and dropping any vertex's Kirchhoff, the resulting
polynomial system in $|E| - 3$ free variables is square.

Sources: see [scripts/exact.py](../scripts/exact.py) and
[scripts/witness.py](../scripts/witness.py).

---

## 3. Interval-Krawczyk certification method

**Goal.** Explain how each individual $S^2$-flow is *rigorously*
certified, and what a replayable certificate file contains.

**Subsections.**

### 3.1 Numerical witness search

Levenberg–Marquardt on the Kirchhoff + unit-norm system in
`scripts/witness.py`. Multi-seed retry with seed rotation to escape
saddle plateaus. Discussion of witness selection by Jacobian
conditioning (rule out near-singular branches at higher orders).

### 3.2 Gauge fix and Newton refinement

Pinning rotation to align vertex $0$'s spokes with the canonical
120-degree triple in the $xy$-plane. Newton refinement in `mpmath` at
50 decimal digits, working over $\mathbb{Q}[s]/(s^2 - 3)$ to keep
$\sqrt{3}$ exact. Drop-redundant-vertex to get a square system.

### 3.3 Interval Krawczyk

Krawczyk operator
$$
K(\mathbf{I}) = c - Y F(c) + (E - Y J(\mathbf{I}))(\mathbf{I} - c)
$$
with $Y = J(c)^{-1}$ at 50-digit precision and $\mathbf{I} = [c -
10^{-5}, c + 10^{-5}]$. Theorem (Krawczyk): if $K(\mathbf{I}) \subset
\mathrm{int}(\mathbf{I})$ then $F$ has a unique zero in $\mathbf{I}$.

Implementation in [scripts/interval.py](../scripts/interval.py); the
key numerical points (use point-eval $F(c)$ not interval-eval, use
`modules=None` in `sympy.lambdify` to keep float exactness on
half-integer coefficients) get a short technical note.

### 3.4 Schema-v2 replayable certificate

JSON document containing graph6, canonical edge order, pinning data,
dropped redundant vertex, free-variable list, polynomial-system
SHA-256, decimal-string centre, per-coordinate Krawczyk margins, full
provenance metadata. Replay tool reproduces the verdict bit-for-bit
on a different machine. See
[docs/external_replay](external_replay/) for the cold-environment
sanity check that confirmed all 3 247 certificates re-verify.

**Pointer.** [scripts/certificate.py](../scripts/certificate.py),
[scripts/sweep.py](../scripts/sweep.py),
[scripts/verify_sweep.py](../scripts/verify_sweep.py).

---

## 4. Enumeration theorem through 28 vertices

**Goal.** State Theorem A with the catalogue construction.

> **Theorem A.** *Every nontrivial snark on at most 28 vertices admits
> an $S^2$-flow.*

**Proof structure.**

1. Enumerate all nontrivial snarks at $n \le 28$. Match the
   Brinkmann–Goedgebeur–Hägglund–Markström catalogue (3 247 graphs;
   per-order distribution table). For $n \le 24$: nauty `geng -d3 -D3
   -c -tf -q n` + SAT-based $\chi'$ test (Glucose 4 via
   `python-sat`) + brute cyclic-4-edge-connectivity. For $n = 26$:
   sharded stream of the same pipeline. For $n = 28$: direct
   generation via Brinkmann–Goedgebeur–McKay `snarkhunter` (skips
   $\chi'$ via even-2-factor lookahead).

2. Apply the Section 3 certifier to each. All 3 247 certificates
   verify, with maximum Krawczyk margin under $10^{-3}$ and
   point-residual under $10^{-20}$.

3. Replay all 3 247 in a cold environment to confirm portability.

**Table.** Per-order count, mean Krawczyk margin, mean wall-clock,
peak memory.

**Citations.** Brinkmann et al., *Generation and properties of
snarks*, JCTB 103 (2013) 468–488. Brinkmann–Goedgebeur–McKay
(snarkhunter).

**Pointer.** [docs/nontrivial_snarks_upto_28.md](nontrivial_snarks_upto_28.md),
[THEOREM.md](../THEOREM.md), and the catalogue files in
[data/catalogues/](../data/catalogues/).

---

## 5. CDC obstruction: oriented 4-CDC $\Rightarrow$ NZ 4-flow

**Goal.** Show that the CDC route is dead for snarks, and document
the structural lemma + computational calibration.

**Lemma (negative CDC calibration).** Let $G$ be a cubic graph
admitting an oriented 4-CDC. Then $G$ has a nowhere-zero $\mathbb{Z}_2
\oplus \mathbb{Z}_2$-flow, hence a nowhere-zero 4-flow, hence
$\chi'(G) = 3$. So **a snark cannot have an oriented 4-CDC.**

**Proof.** MMRT 2025 Theorem 4 specialised to $d = 4$: oriented
$d$-CDC $\Leftrightarrow$ $H_d$-flow on cubic graphs, where $H_d$ is
the boundary group of the $(d-1)$-cube. At $d = 4$, $H_4$-flow values
restricted to coordinates $\bmod 2$ give a $\mathbb{Z}_2^2$-flow that
is nowhere zero by the unit-vector constraint.

**Computational calibration.** [scripts/cdc.py](../scripts/cdc.py)
implements the chain $H_4$-flow $\to$ $\mathbb{Z}_2^2$-flow $\to$
NZ 4-flow $\to$ $\chi' = 3$ certifier. Run on Petersen / Blanuša /
$J_5$ as triple-negative calibration:
[tests/test_cdc_negative_calibration.py](../tests/test_cdc_negative_calibration.py).

**Consequence.** The original Phase 2 plan (find oriented 4-CDCs on
snarks) is closed negatively. The right relaxation is **weighted CDC**:
continuous cycle vectors in $\Sigma_4 \cong S^2$, no orientation
hypothesis. See [docs/weighted_cdc_certificates.md](weighted_cdc_certificates.md):
explicit weighted-CDC certificates on Petersen, Blanuša-2, $J_5$,
each combining with the gadget extensions of Section 6.

---

## 6. Gadget closure theorem

**Goal.** Construct the closure $\mathcal{F} \supsetneq \mathcal{F}_0$.

**Operations.** Both preserve cubicity and admit closed-form
$S^2$-flow extensions.

### 6.1 Triangle blow-up

Replace a degree-3 vertex $v$ with a triangle $\{v_1, v_2, v_3\}$,
each $v_i$ inheriting one of $v$'s spokes. Closed-form flow extension
(HMM 2026, refined here):

$$
g_{12} = \frac{f_2 - f_1}{3} + \varepsilon \sqrt{\tfrac{2}{3}}\,\hat n,
\quad g_{13} = -f_1 - g_{12}, \quad g_{23} = -f_2 + g_{12}
$$

with $\hat n = (f_3 \times (f_2 - f_1)) / \lVert\cdot\rVert$ and
chirality $\varepsilon \in \{\pm 1\}$. Verified in
[scripts/triangle_blowup.py](../scripts/triangle_blowup.py) at
Kirchhoff residual $\sim 10^{-16}$.

### 6.2 Three-edge-cut dot product

$G_1 \oplus_\pi G_2$: glue at vertices $v_1 \in G_1, v_2 \in G_2$ via
three through-edges with permutation $\pi$. Flow consistency forces
the boundary triple of $G_2$ to equal $-T_1 \circ \pi$ after some
$R \in \mathrm{SO}(3)$. `align_to_negation` Kabsch-searches the six
permutations; succeeds when the two witnesses have matching
chirality (which a single retry with a different seed flips).
Verified in [scripts/dot_product.py](../scripts/dot_product.py).

### 6.3 The closure theorem

> **Theorem B.** Let $\mathcal{F}_0$ be the set of 3 247 nontrivial
> snarks at $n \le 28$ certified in Theorem A. Let $\mathcal{F}$ be
> the closure of $\mathcal{F}_0$ under triangle blow-up and 3-edge-cut
> dot product. Every $G \in \mathcal{F}$ admits a constructive
> $S^2$-flow, produced by composing the gadget flow extensions from
> the base certificates.

**Verified instances.** Eight gadget tests at Kirchhoff residual
$\le 5.9 \cdot 10^{-16}$: triangle blow-up of Petersen, Blanuša-1,
$J_5$; dot products $\mathrm{Petersen} \oplus \mathrm{Petersen}$,
$\mathrm{Petersen} \oplus \mathrm{Blanuša}_1$, $J_5 \oplus J_5$;
iterated chains $\mathrm{Petersen}^{\oplus 4}$ and $\mathrm{Petersen}
\oplus J_5 \oplus \mathrm{Blanuša}_1$. See
[docs/gadget_closure.md](gadget_closure.md) Table.

**Note.** $\mathcal{F}$ is *not* contained in the snark world (triangle
blow-up shatters girth $\ge 5$). It is, however, strictly larger than
$\mathcal{F}_0$ as a class of cubic graphs with a constructive
$S^2$-flow, and the construction is parametric in the gadget
sequence — no per-graph Krawczyk needed beyond the 3 247 base
certificates.

---

## 7. Decomposition frontier and replayable membership

**Goal.** Inverse direction of Section 6: a decision procedure for
$\mathcal{F}$-membership and a structural reading of the catalogue.

### 7.1 Inverse operations

- **Inverse triangle reduction.** A triangle in a cubic graph is
  *contractible* iff its three vertices have three pairwise-distinct
  external neighbours; contracting collapses the triangle to a single
  degree-3 vertex.
- **Inverse 3-edge-cut dot product.** A cyclic 3-edge cut splits $G$
  into two parts each containing a cycle; adding a fresh vertex on
  each side connected to the 3 cut-edge endpoints gives the two
  cubic pieces whose dot product is $G$.

Algorithms in [scripts/gadget_decompose.py](../scripts/gadget_decompose.py).
Canonical-graph6 hashing via nauty `labelg` for isomorphism-correct
memoisation.

### 7.2 The frontier result

> **Theorem C.** Every nontrivial snark in $\mathcal{F}_0$ is
> irreducible under both inverse operations. The catalogue **is** the
> base of the closure.

**Proof.** By definition every nontrivial snark has girth $\ge 5$ (no
triangles) and is cyclically $\ge 4$-edge-connected (no cyclic 3-cuts).
An exhaustive scan of all 3 247 catalogue graphs confirms: 0
contractible triangles, 0 cyclic 3-edge cuts.

### 7.3 Replayable membership certificates

For any cubic graph $G$, `decompose_tree(G, base)` returns either a
`DecompTree` whose leaves are base graphs, or `None`. The tree is a
*replayable certificate of $\mathcal{F}$-membership*: a third party
runs the inverse operations on $G$, follows the tree to its leaves,
re-verifies each leaf certificate, and re-assembles the $S^2$-flow.

> **Corollary.** Membership in $\mathcal{F}$ is decidable in time
> polynomial in $|V(G)|$ on small graphs (the cyclic-3-cut search
> dominates at $O(m^3)$ per decompose step). Each positive answer
> comes with a tree of operation labels totalling at most $|V(G)|$
> bits.

**Table of verified positive examples.**

| Construction | $n$ | Tree depth | Leaves |
|---|---:|---:|---|
| `blowup(Petersen, 0)` | 12 | 1 | {Petersen} |
| double blowup | 14 | 2 | {Petersen} |
| `Petersen.Petersen` | 18 | 1 | {P, P} |
| `Petersen.Petersen.Blanuša_1` | 34 | 2 | {P, P, B$_1$} |
| blow-up of triple chain | 36 | 3 | {P, P, B$_1$} |

(All from [docs/gadget_decomposition_frontier.md](gadget_decomposition_frontier.md).)

---

## 8. Failed flower routes

**Goal.** Document the three independent obstructions encountered
when attacking flower snarks $J_{2k+1}$ directly. This is a
**negative** section, written honestly, because:

1. It rules out the obvious extensions of Section 6 to the flower
   family;
2. It guides future work — the obstructions are structural, not
   computational.

### 8.1 CDC parity obstruction

A parametric CDC ansatz on $J_n$ requires every star's pass-count
triple $(b\text{-}c, b\text{-}d, c\text{-}d)$ to be $(1, 1, 1)$; each
length-6 shuttle covers exactly 2 stars; $n_T \times 2 = n$ forces $n$
even — contradicting $n = 2k + 1$ odd. See
[docs/flower_snarks_cdc.md](flower_snarks_cdc.md). The weighted-CDC
relaxation does succeed on Petersen, Blanuša-2, $J_5$, but not
parametrically on the family.

### 8.2 Dot/splice gadget decomposition

> **Lemma (no flower dot/splice decomposition).** $J_5$ is cyclically
> exactly 5-edge-connected; for $k \ge 3$, $J_{2k+1}$ is cyclically
> $\ge 6$-edge-connected (verified empirically through $J_{13}$).
> Therefore no 3-cut or 4-cut decomposition of $J_n$ into smaller
> cubic pieces exists.

Proofs and computational verification in
[docs/no_flower_dot_decomposition.md](no_flower_dot_decomposition.md)
and [docs/splice4.md](splice4.md).

### 8.3 Direct monodromy / two-scale ansatz

The $S^2$-flow problem on $J_{2k+1}$ reduces (via spoke elimination)
to a 3-dim discrete dynamical system on the conservation surface,
with monodromy $T^n(X_0) = \pi(X_0)$ (the $\pi$ is the c/d twist).
The certified witnesses are transverse fixed points modulo the
$\mathrm{SO}(3)$ gauge (rank-2 reduced Jacobian, $|\det J_{\text{red}}|
\ge 6$ for $J_5, J_7, J_{11}$).

But two follow-up tests failed:

- **No smooth asymptotic limit on LM-random witnesses.** $|S|$
  varies, $\beta$-Fourier spectrum stays high-frequency. See
  [docs/flower_asymptotic.md](flower_asymptotic.md).
- **No stable small-period two-scale model.**
  $X_i \approx R^i Y_{i \bmod p}$ fits give RMS residuals
  $\mathcal{O}(1)$, worsening with $n$; best $p \equiv p_{\max}$
  (overfitting); structural divisibility forbids $p = 2, 4$ on odd
  $n$. See [docs/flower_twoscale.md](flower_twoscale.md).

**Conclusion.** Three independent natural structural routes
(structural CDC, gadget decomposition, monodromy two-scale) all hit
walls on $J_{2k+1}$. We leave the flower question open; the
infrastructure built for it is available for future ansatz attacks.

---

## 9. Reproducibility appendix

**Goal.** Make the whole package replayable bit-for-bit on a clean
machine.

**Contents.**

- Hardware / OS used (single laptop class; CPU model).
- Software stack (Python 3.12, mpmath 1.3, sympy 1.13, networkx 3.6,
  scipy 1.14, nauty 2.9.3, snarkhunter 2.0b, python-sat 1.8).
- Build instructions (`uv venv`, `uv pip install -r requirements.txt`,
  build nauty + snarkhunter from source).
- Replay protocol:
  1. `make verify` — full pytest suite (184 tests, $\sim$ 2 min).
  2. `make verify-certs` — replay all 3 247 interval-Krawczyk
     certificates ($\sim$ 30 min single-thread).
  3. `make catalogue` — regenerate the catalogue from scratch
     ($\sim$ 30 min through $n = 26$; $n = 28$ needs snarkhunter,
     $\sim$ 25 min).
  4. `make manifest` — verify catalogue SHA-256 against the manifest.
- File-level provenance: schema-v2 certificate format,
  graph6 canonicalisation contract, version-pinned dependencies.

Cold-environment replay log already recorded:
[docs/external_replay](external_replay/) — 3 247 / 3 247 re-verified
on an unrelated machine.

---

## Citation list

- **[HMM26]** Houdrouge, Miraftab, Morin. *2-dimensional unit vector
  flows.* arXiv:2602.21526v1, 2026-02-25.
- **[Uly26]** Ulyanov. *Graph Puzzles II.1: Counterexamples to Jain's
  Second Unit Vector Flows Conjecture.* arXiv:2603.23328v1,
  2026-03-24.
- **[MMRT25]** Mattiolo, Mazzuoccolo, Rajnik, Tabarelli. *Cycle double
  covers in cubic graphs.* 2025. (Cited for Theorem 4: oriented
  $d$-CDC $\Leftrightarrow$ $H_d$-flow $\Rightarrow$ $S^{d-2}$-flow.)
- **[BGHM13]** Brinkmann, Goedgebeur, Hägglund, Markström. *Generation
  and properties of snarks.* JCTB 103 (2013) 468–488.
- **[BGM]** Brinkmann, Goedgebeur, McKay. snarkhunter (software).
  https://caagt.ugent.be/cubic/

---

## Open follow-on questions (not for this paper)

- Jain's first conjecture itself: still open.
- Characterise $\mathcal{F}$ as a class of cubic graphs.
- $|\mathcal{F}_k|$ enumeration for small $k$.
- Other named snark families (Goldberg, Loupekine, generalised
  Petersen $\mathrm{GP}(m, k)$) — does any admit a uniform
  $S^2$-flow construction?

These are listed at the end of the paper as a research agenda; none
is needed for the package above.

---

## What this outline does *not* yet have

- Actual LaTeX / paper text. The outline gives section-level claims
  and pointers; turning each into a polished section is the next
  writing pass.
- A figure inventory. Likely figures: schematic of a single
  certificate; gadget operation diagrams (triangle blow-up, dot
  product); decomposition tree of a sample composition;
  catalogue size table.
- A "limitations and future work" paragraph beyond the bullet list
  above.

These are all small additions on top of the structure here. The
substance — theorems, proofs, code, certificates — is all present in
this repository.
