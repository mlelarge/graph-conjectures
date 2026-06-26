# Comparison with *Clique Number of Tournaments II*

_Last checked against the repository on June 7, 2026 (through D38)._

## Sources and scope

This note compares:

- Guillaume Aubian and Samuel Coulomb, *Clique Number of Tournaments II*,
  preprint dated June 6, 2026
  ([local PDF](Downloads/Clique_Number_of_tournaments_II.pdf));
- the results recorded in this repository under
  `problems/tournament_clique_number_omega_cluster/`, in particular:
  - [the `k=3` proof](proof_conj_5_10_k3.md);
  - [the value proof for `AC_n[C3]`](proof_omega_AC_n_C3.md);
  - [the deletion proof for `AC_n[C3]`](proof_deletion_AC_n_C3.md);
  - [the `k=5` proof for `AC_n[AC_n]`](proof_AC_n_AC_n_k5.md);
  - [the unified `k=3,4,5` account](conjecture_5_10_k345_unified.md);
  - [the refutation of the proposed substitution upper bound](h16_substitution_upper_bound.md);
  - [the H16 certificate generator](../scripts/certify_h16_counterexample.py)
    and [certificate manifest](../data/h16_cert/certificate.json);
  - [`ledger.json`](../ledger.json), which is the authoritative status record.

The preprint's critical-tournament results are in Section 6 (printed pages
16-17). Its complexity theorem is Theorem 1.1/Section 3, its approximation
results are in Section 5, and its `chi_vec`-bounding results are in Section 4.

The authoritative ledger now extends through D38. P20 remains promoted to
`can_enter_proved=true`, so Conjecture 5.10 is proved in the repository for
`k=3,4,5`. The mathematical frontier has not moved beyond D35: no new value of
`k` has been settled. Decisions D36-D38 instead strengthen the record by
completing omitted `k=5` casework, exporting independently checkable
certificates for the H16 counterexample, correcting the certificate encoding,
and systematically removing claims that exceeded the scope of sampled data.

The main comparison concerns directed clique number, critical tournaments,
Conjecture 5.10, and Question 5.9. The preprint is substantially broader, so its
complexity, approximation, and `chi`-boundedness results are summarized
separately near the end.

## Common notation

For a tournament `T` and a total order `prec` of its vertices, the backedge
graph `T^prec` has an edge `uv`, with `u prec v`, when the tournament arc is
`v -> u`. The directed clique number is

```text
omega_vec(T) = min_prec omega(T^prec).
```

A tournament is `k`-`omega_vec`-critical when

```text
omega_vec(T) = k
and
omega_vec(T-v) = k-1 for every vertex v.
```

For odd `N=2m+1 >= 7`, the repository writes

```text
AC_N = Cay(Z/N, {1,...,m-1} union {m+1}).
```

The preprint's tournament `T_{2n+1}` in Proposition 6.1 has generator set

```text
{1,...,n-1} union {n+1}.
```

Thus, after setting `N=2n+1`, the two definitions are identical:

```text
T_{2n+1} = AC_{2n+1}.
```

For lexicographic substitution, `S[H]` means that every vertex of the outer
tournament `S` is replaced by a copy of the inner tournament `H`. Therefore

```text
Delta(H,H,H) = C3[H].
```

This direction matters. In general,

```text
C3[AC_N] != AC_N[C3] != AC_N[AC_N].
```

The first two have the same order `3N`, but the definitions use opposite
substitution directions. A direct isomorphism check made for this comparison
gives non-isomorphism for `N=7,9,11`; no all-`N` non-isomorphism theorem is
needed below.

## Executive comparison

| Level | Preprint | Repository | Relationship |
|---|---|---|---|
| `k=3` | Proposition 6.1: `AC_N` is `3`-critical for every odd `N>=7` | P13: the same family and theorem | Exact overlap in statement and construction; different proofs |
| `k=4` | Proposition 6.2: `C3[AC_N]=Delta(AC_N,AC_N,AC_N)` is `4`-critical | P16+P18: `AC_N[C3]` is `4`-critical | Same conclusion, opposite product direction; checked non-isomorphic for `N=7,9,11` |
| Earlier repo `k=4` route | The preprint proves the Delta family | G22 had found and verified exactly this Delta family but lacked a valid uniform proof | The preprint supplies the missing theorem for the old G22 candidate |
| `k=5` | No explicit or unconditional `5`-critical family | P19+P20: `AC_N[AC_N]` is `5`-critical for every odd `N>=7`; omitted casework repaired in D36-D38 | New result relative to the supplied preprint |
| General substitution | No additive formula for `omega_vec(S[H])` is claimed | D35 refutes `omega_vec(S[H])<=omega_vec(S)+omega_vec(H)-1`; D36-D37 add proof-producing CNF/DRAT artifacts | New structural result in the repository; no contradiction with the preprint |
| `k>=6` | Conditional infinitude unless `P=NP`; no explicit family | Open; no explicit `6`-critical witness is recorded, H16 is closed, and direct searches give negative evidence on explicitly limited scopes | Neither source gives an unconditional explicit family |
| Question 5.9 | Negative at `k=3,4` follows from Propositions 6.1 and 6.2, although not formulated that way | Explicitly proved negative at `k=3,4,5` | Repository adds the `k=5` negative result and spells out the monotonicity argument |

## 1. The `k=3` result

### Preprint result

Proposition 6.1 states that, for every integer `n>=3`,

```text
T_{2n+1} = AC_{2n+1}
```

is `3`-`omega_vec`-critical.

Its proof has two main inputs.

1. For an arbitrary vertex order, take its last vertex `v_i`. Several specified
   out-neighbours of `v_i` are adjacent to it in the backedge graph. Three of
   those neighbours form a directed triangle, so two are adjacent in every
   backedge graph. Together with `v_i`, they give a backedge triangle. This
   proves `omega_vec(AC_N) >= 3`.
2. The proof invokes the theorem of Neumann-Lara and Urrutia that this same
   tournament is `3`-dichromatic-critical. Since
   `omega_vec <= dichromatic number`, every vertex deletion has directed clique
   number at most `2`. This supplies the deletion upper bound used for
   criticality.

The proof is short and conceptually driven by the known dichromatic-critical
family.

### Repository result

P13 proves the same theorem:

```text
AC_N is 3-omega_vec-critical for every odd N>=7.
```

The repository proof is more explicit about the directed clique number itself.

1. In the identity order, every backedge gap is at least `m`, so a backedge
   clique has size at most `3`.
2. The only backedge triangle in this order is `{0,m,2m}`.
3. The lower bound is obtained from `dom(AC_N)>=3` and the known inequality
   `dom(T)<=omega_vec(T)`. The domination statement is reduced to and proved by
   the autocorrelation identity

   ```text
   min_{t != 0} |N_0 intersect (N_0+t)| = 2.
   ```

4. Deleting `0` removes the unique identity-order backedge triangle, giving
   `omega_vec(AC_N-0)<=2`; an explicit surviving directed triangle gives the
   reverse inequality.
5. Vertex-transitivity extends the deletion statement to every vertex.

### Exact overlap and differences

The theorem and the family are exactly the same. The proof dependencies differ:

- the preprint relies on the previously known `3`-dichromatic-criticality of
  `AC_N`;
- the repository gives a direct backedge-order proof of the upper and deletion
  bounds, plus a domination/autocorrelation proof of the lower bound.

The repository also explicitly derives the failure of Question 5.9 at `k=3`.
Every proper subtournament of a `3`-critical `AC_N` lies in some deletion
`AC_N-v`, hence has directed clique number at most `2`. Since `|AC_N|` is
unbounded, no function `ell(3)` can exist.

This failure is also an immediate consequence of the preprint's Proposition
6.1, but the preprint does not formulate the result in the language of Question
5.9.

## 2. The `k=4` results

### Preprint construction: `C3[AC_N]`

Proposition 6.2 proves that

```text
Delta(AC_N,AC_N,AC_N) = C3[AC_N]
```

is `4`-`omega_vec`-critical for every odd `N>=7`.

For the lower bound, take the first vertex of an arbitrary ordering, say in
block `A`. Every vertex of the preceding cyclic block `C` is adjacent to it in
the backedge graph. Since `omega_vec(C)=3`, this forces a backedge `K4`.

For deletion, suppose `x` is deleted from block `A`. Choose vertices `b` and
`c` in the other two blocks, and use `2`-dicolourings

```text
(A1,A2), (B1,B2), (C1,C2)
```

of `A-x`, `B-b`, and `C-c`. The preprint orders the remaining vertices as

```text
b < c < A1 < B1 < C1 < A2 < B2 < C2
```

with topological orders inside the colour classes. It then checks that the
resulting backedge graph is `K4`-free. Thus every deletion has directed clique
number `3`.

The construction uses the fact that `AC_N` is `3`-dichromatic-critical, not
only `3`-`omega_vec`-critical.

### Repository construction: `AC_N[C3]`

P16 and P18 prove that the reverse product

```text
AC_N[C3]
```

is `4`-`omega_vec`-critical for every odd `N>=7`.

The value proof uses:

- the general lexicographic lower bound

  ```text
  omega_vec(S[H]) >= omega_vec(S)+omega_vec(H)-1;
  ```

- a merged order with key `c(t)+d(h)`;
- a key-class analysis excluding a backedge `K5`.

The deletion proof uses a different order, `d_then_c`, with five bands. Its
case analysis establishes:

```text
number from the h in {1,2} layers
  + number from the h=0 layer
<= 3.
```

The difficult case is the `(2,2)` configuration, ruled out by the
incompatibility

```text
not(1+delta in g and m+1+delta in g).
```

### Relationship to the old G22 candidate

Before the final `AC_N[C3]` proof was obtained, the repository investigated

```text
D_N = Delta(AC_N,AC_N,AC_N).
```

This is exactly the preprint's `C3[AC_N]` family. The repository verified
`omega_vec(D_N)=4` and the deletion value `3` over a substantial finite range,
but recorded the proposed uniform proof as G22 because:

- the claimed Delta upper-bound lemma did not exist in the cited source;
- the uniform deletion argument had not been supplied;
- finite verification was correctly not treated as a theorem.

Proposition 6.2 of the preprint supplies the missing rigorous proof. Thus the
preprint does not merely reach the same `k=4` conclusion: it validates an exact
construction that appears in the repository's historical research record.

### What is genuinely different

The final repository theorem and the preprint theorem are not duplicate
constructions:

```text
preprint:   C3[AC_N]  = three large AC_N blocks in a directed 3-cycle;
repository: AC_N[C3] = N small C3 blocks arranged according to AC_N.
```

They have the same order `3N` and are both vertex-transitive and `4`-critical,
but they use opposite substitution directions and different proof mechanisms.

Consequently there are two explicit infinite `4`-critical families available
from the combined record.

As at `k=3`, either family directly implies that Question 5.9 fails at `k=4`.
The repository states and proves this consequence explicitly.

## 3. The new `k=5` theorem in the repository

### Statement

P19+P20 prove:

> For every odd `N=2m+1>=7`, the lexicographic product
> `AC_N[AC_N]` is `5`-`omega_vec`-critical.

Equivalently,

```text
omega_vec(AC_N[AC_N]) = 5
```

and, for every vertex `v`,

```text
omega_vec(AC_N[AC_N]-v) = 4.
```

The orders `N^2` are unbounded, so this is an infinite explicit family. It
proves Conjecture 5.10 at `k=5` and gives a negative answer to Question 5.9 at
`k=5`.

### Role of P19

P19 is the finite seed and discovery certificate:

```text
AC_7[AC_7]
```

has order `49`, directed clique number `5`, and every vertex deletion has
directed clique number `4`.

The computation isolated two useful orders:

- the merged-sum order for the full tournament;
- the `inner_then_outer` order for a vertex deletion.

P19 alone is an explicit `5`-critical tournament and gives the finite lower
bound `ell(5)>=49`, but a single tournament does not prove Conjecture 5.10.

### Role of P20

P20 turns the P19 pattern into a uniform theorem for all odd `N>=7`.

Let a vertex of `AC_N[AC_N]` be `(a,b)`, with outer coordinate `a` and inner
coordinate `b`. Use the three-level potential

```text
c(t) = 3  if t=0,
       2  if 1<=t<=m,
       1  if m+1<=t<=2m.
```

The main proof components are as follows.

#### Full-tournament lower bound

The general lexicographic lower bound gives

```text
omega_vec(AC_N[AC_N])
  >= omega_vec(AC_N)+omega_vec(AC_N)-1
  = 3+3-1
  = 5.
```

#### Deletion lower bound

After deleting `(0,0)`, the remaining tournament contains

```text
(AC_N-0)[AC_N].
```

Therefore

```text
omega_vec(AC_N[AC_N]-(0,0))
  >= omega_vec(AC_N-0)+omega_vec(AC_N)-1
  = 2+3-1
  = 4.
```

#### Deletion upper bound

Order the surviving vertices by

```text
(c(b), c(a), a, b).
```

The pair `(c(b),c(a))` defines one of eight surviving cells in

```text
{1,2,3}^2 minus {(3,3)}.
```

The proof first shows that a backedge clique contains at most one vertex from
each cell. It then rules out every five-cell clique. The obstruction is
organized as 20 listed infeasible cell sets:

- 10 triples;
- 4 outer-source quadruples;
- 6 square quadruples.

They are closed by two symbolic mechanisms.

1. **Forced-value chains.** The almost-consecutive generator arithmetic forces
   outer coordinates to `m+1`, to `m`, or into an interval disjoint from `g`,
   after which another required backward arc is impossible.
2. **Square obstruction and Lemma H17.** For
   `x in H=[m+1,2m]` and `y in L=[1,m]`, the common in-neighbourhood

   ```text
   N^-(x) intersect N^-(y)
   ```

   lies in a single band. More precisely, it lies in `[0,m-1]` when
   `x-y<=m`, and in `[m+1,2m-1]` when `x-y>=m+1`. It therefore cannot contain
   simultaneously the high-band and low-band representatives required by a
   square configuration.

In the repaired proof, the ten triples and four outer-source quadruples each
have an explicit residue chain. The six square quadruples are handled by their
common alternating high/low-band pattern: a same-block equality branch
contradicts tournament antisymmetry, while the all-distinct branch contradicts
Lemma H17. The argument needs exactly these two facts:

1. each of the 20 listed cell sets is symbolically infeasible;
2. every one of the `C(8,5)=56` five-cell subsets contains at least one listed
   obstruction.

It does not require the 20 sets to be the exact or inclusion-minimal
obstructions.

This proves

```text
omega_vec(AC_N[AC_N]-(0,0)) <= 4.
```

Together with the lower bound, the deletion value is exactly `4`.
Vertex-transitivity gives the same value for every deletion.

#### Full-tournament upper bound

The value upper bound is a corollary of the deletion argument. In the chosen
cell order, `(0,0)` is the unique `(3,3)` vertex. A backedge clique either:

- omits `(0,0)`, and hence has size at most `4`; or
- contains `(0,0)`, and has at most four additional vertices.

Thus the full backedge graph has clique number at most `5`, completing

```text
omega_vec(AC_N[AC_N]) = 5.
```

### Verification and red-team status

The proof is not being promoted from finite data alone.

- The finite computations discovered the cell structure and checked the
  obstruction list.
- The final proof supplies uniform residue arguments and the interval proof of
  Lemma H17.
- Seven adversarial checks reproduced the load-bearing claims.
- The red-team found one false band-`L` arc statement. The correct statement is

  ```text
  -a in g iff a=m, for a in [1,m].
  ```

  The affected mirror arguments were rewritten using the forced value `a=m`.
- After correction, P20 was promoted to `can_enter_proved=true` in D28.
- D36 then found a genuine incompleteness in the written proof: the four
  outer-source quadruples had been asserted by "the same chains" with finite
  checks standing in for a uniform derivation, and the description of the six
  squares was inaccurate. The proof file now writes all four chains explicitly
  and gives the correct alternating-band argument for all six squares.
- D37-D38 removed the unsupported claim that the 20-set list was the exact
  minimal obstruction list. The theorem only uses symbolic infeasibility of
  the listed sets and the finite, `n`-independent coverage of the 56
  five-subsets. A mechanical scope-overclaim lint now reports zero flags
  across the ledger and Markdown documentation.

Thus the current post-D36 proof is complete. The later decisions are proof and
scope repairs, not a new construction or a change in the theorem's statement.

### Comparison with the preprint

The supplied preprint has no explicit `5`-`omega_vec`-critical tournament and
no unconditional infinite `5`-critical family.

Its final observation says that the `k=4` Delta construction generalizes if one
starts from a `k`-dichromatic-critical tournament `T` satisfying
`omega_vec(T)=k`. The authors explicitly state that they do not know whether
such tournaments exist for `k>=4`.

The repository's `AC_N[AC_N]` theorem bypasses that missing input:

- it does not require a `4`-dichromatic-critical base;
- it uses two copies of the `3`-critical almost-consecutive family;
- its criticality proof is based on a product-specific cell order and
  residue structure.

Therefore P19+P20 are genuinely beyond the explicit critical-tournament
results in the supplied preprint.

## 4. Conjecture 5.10 and Question 5.9

### Unconditional explicit results

Combining the two sources gives:

| `k` | Explicit infinite family | Source |
|---|---|---|
| `3` | `AC_N` | Both preprint Proposition 6.1 and repository P13 |
| `4` | `C3[AC_N]` | Preprint Proposition 6.2 |
| `4` | `AC_N[C3]` | Repository P16+P18 |
| `5` | `AC_N[AC_N]` | Repository P19+P20 |

Thus Conjecture 5.10 is unconditionally proved for `k=3,4,5`.

For each displayed family, criticality gives a direct negative answer to
Question 5.9 at that value of `k`: every proper subtournament lies in a
one-vertex deletion and therefore has directed clique number at most `k-1`.

The repository explicitly records:

```text
no ell(3), no ell(4), and no ell(5).
```

### Conditional result from complexity

Theorem 1.1 of the preprint proves that, for every fixed `r>=3`, deciding

```text
omega_vec(T) <= r
```

is NP-complete.

Section 6 uses this to state that, for every `k>=4`, there must be infinitely
many `k`-`omega_vec`-critical tournaments unless `P=NP`. The reasoning is that
if only finitely many critical obstructions existed, testing for their induced
presence would give a polynomial recognition algorithm for the corresponding
threshold.

This is important evidence for the full conjecture, but it differs from the
repository theorems in three ways:

- it is conditional on `P!=NP`;
- it is nonconstructive;
- it does not identify a family or prove criticality of explicit tournaments.

The repository results for `k=3,4,5` are unconditional and constructive.

### Remaining gap

Neither source proves Conjecture 5.10 unconditionally for every `k>=3`.

The repository's current open range is `k>=6`, and no explicit
`6`-`omega_vec`-critical tournament is currently recorded. In the repository's
internal terminology, the `k=6` witness slot is still empty; this is not a
claim that Question 5.9 has a positive answer at `k=6`. The general
substitution lower bound

```text
omega_vec(S[H]) >= omega_vec(S)+omega_vec(H)-1
```

is proved, but the formerly proposed matching upper bound is **false**. An
order-7 tournament `H` satisfies

```text
omega_vec(C3) = omega_vec(H) = 2,
omega_vec(C3[H]) = 4,
omega_vec(H[C3]) = 3.
```

The product `C3[H]` is itself `4`-critical: every one-vertex deletion has
directed clique number exactly `3`. It is also minimal for fixed outer factor
`C3`: an exhaustive isomorphism-class census finds no counterexample with
`|H|<=6` and exactly three among the `456` order-7 classes.

D36-D37 upgraded the computational lower bound to an independently checkable
certificate package. Two distinct no-`K4` ordering encodings, consecutive-chain
and all-pairs-backward, each produce a DIMACS CNF with `210` variables,
`10194` clauses, and `2214` forbidden transitive four-sets. For each encoding
the repository stores:

- the DIMACS CNF and its SHA-256 checksum;
- a Cadical DRAT refutation;
- a redundant UNSAT result from both `Cadical153` and `Minisat22`.

D37 caught that the first exported formulas used the reversed order direction.
The literal direction was corrected and all CNFs, checksums, DRAT proofs, and
solver results were regenerated. The current artifacts are in
[`data/h16_cert/`](../data/h16_cert/).

Thus substitution is directional and `omega_vec-1` is not additive. The valid
general upper bound is only

```text
omega_vec(S[H]) <= omega_vec(S) * omega_vec(H),
```

obtained from block-respecting optimal orders; the counterexample attains
equality `2*2=4`. The earlier block-laminarity lemma remains true, but it does
not prove additivity: the induced block and within-block orders are arbitrary,
whereas `omega_vec` is a minimum over all orders. The simple merged potentials
for `AC_N[C3]` and `AC_N[AC_N]` remain valid special arithmetic constructions,
but they cannot be promoted to a universal law.

The preprint's proposed generalization encounters a different-looking but
related shortage: it would need suitable `k`-dichromatic-critical tournaments
with directed clique number exactly `k` for `k>=4`.

### New `k=6` search information after D28

The newer repository rounds D29-D38 do not prove the `k=6` case. D29-D35
provide the search results below; D36-D38 correct their quantifier and scope
wording:

- no explicit `6`-critical tournament or family has been found;
- in a sample of `42` single-orbit circulants of orders `37` through `49`
  whose identity order has clique number `6`, every sampled tournament admits
  an order of clique number at most `5`; this was not an exhaustive census of
  those orders;
- for the domination-number route, the exhaustive order-37 circulant census
  has maximum domination number `4`; additional samples through order `65`
  also top out at `4`, and the checked Paley tournaments through order `251`
  have domination number at most `5`. Only the order-37 statement is
  exhaustive, so these computations do not prove that domination number `6`
  is absent below order `67`;
- `QR_67` remains unresolved with `omega_vec(QR_67)` in `{5,6}`;
- the exact positive value `omega_vec(QR_19[AC_7])=6` is known, but
  `6`-criticality has not been established, so it does not provide the missing
  witness;
- the iterated outer-`C3` Delta tower fails criticality at its first relevant
  test: all deletions of the order-27 level retain value at least `4`;
- the old side claim that domination number at least `4` forces a Paley
  circulant is false; many off-Paley examples occur, but their domination
  number still stops at `4`, so this correction does not open a `k=6` route.

Accordingly, the live repository directions are now a special arithmetic
criticality-lifting theorem tailored to the `AC_N` constructions, or a genuinely
new parametric family with direct upper, lower, and deletion certificates.
None of these negative computations changes the preprint comparison: its
conditional complexity argument remains valid, but it gives neither an
explicit family nor a construction at `k=6`.

## 5. Proof-method comparison

| Issue | Preprint method | Repository method |
|---|---|---|
| `k=3` lower bound | Last vertex plus a directed triangle among selected neighbours | Domination number plus an exact autocorrelation lemma |
| `k=3` deletion upper bound | Imported `3`-dichromatic-criticality | Unique identity-order backedge triangle |
| `k=4` construction | Outer `C3`, inner `AC_N` | Outer `AC_N`, inner `C3` |
| `k=4` deletion | Six acyclic colour classes arranged in a global order | Five explicit potential bands and residue casework |
| `k=5` | No construction | Outer and inner `AC_N`; eight-cell deletion analysis |
| General product tool | Generalization from suitable dichromatic-critical inputs | General lex lower bound and product upper bound; additive upper bound refuted; sharper upper bounds only for special arithmetic products |
| Computational role | Small Python checks appear in gadget sections | Exact oracle, SAT encodings, template search, symbolic proof and red-team, proof-producing CNF/DRAT artifacts, and scope-overclaim lint |

The two approaches are complementary. The preprint exploits dichromatic
criticality to obtain concise proofs. The repository develops direct
`omega_vec` orderings and arithmetic certificates, which makes the `k=5`
construction possible without a higher dichromatic-critical base.

## 6. Other repository results absent from the preprint

Within this problem folder, the repository also contains:

- a general proof of the lexicographic lower bound

  ```text
  omega_vec(S[H]) >= omega_vec(S)+omega_vec(H)-1;
  ```

- explicit isolated `4`-critical circulants, including `Paley(19)` and an
  order-21 circulant;
- a verified `5`-critical cyclic product `AC_7[AC_9]`;
- exact branch-and-bound and SAT encodings for directed clique thresholds;
- extensive negative data on naive Paley, repeated-`C3`, and nested-product
  generalizations;
- the explicit order-7 refutation of H16, including the quantifier error in
  the earlier block-laminarity reduction;
- two independently encoded no-`K4` CNFs with checksums and DRAT
  refutations for the H16 counterexample;
- a new `4`-critical tournament `C3[H]` of order `21`, whose two width-`2`
  factors attain the universal multiplicative upper bound.

These results are not claimed in the supplied preprint. Some are computational
constructions or research diagnostics rather than general theorems; the ledger
marks that distinction explicitly.

## 7. Major preprint results outside the repository's scope

The preprint proves or develops several results not addressed by this folder.

### Complexity

- Theorem 1.1: for every fixed `k>=3`, deciding
  `omega_vec(T)<=k` is NP-complete.
- Theorem 3.8 gives the base `k=3` reduction from 3-SAT.
- Computing directed clique number is therefore NP-hard.
- The fixed threshold `k=2` remains open in the preprint.

### `chi`-bounding tournaments

The preprint studies the tournament analogue of the Gyarfás-Sumner program.
Among its contributions:

- `U_5` is shown to be `chi_vec`-bounding;
- a family of ordered graphs `M_n` is proved `chi`-bounding;
- necessary conditions for a tournament to be `chi_vec`-bounding are derived;
- explicit counterexamples are given to the conjecture that admitting a forest
  backedge graph is sufficient for being `chi_vec`-bounding;
- additional counterexamples are derived from incomparable ordered graphs and
  the Blanche Descartes construction.
- using an announced theorem that ordered matchings are `chi`-bounding, the
  preprint deduces that every class of tournaments of bounded twin-width is
  `chi_vec`-bounded.

None of this is a target of the present tournament-criticality folder.

### Approximation and bounded certificates

Using the Crew-Fan-Koerts-Moore-Spirkl unavoidable-family theorem, the preprint
records:

- a non-identity local-to-global certificate theorem with functions `f(k)` and
  `ell(k)`;
- a polynomial-time gap algorithm certifying either
  `omega_vec(T)>=k` or `omega_vec(T)<f(k)`;
- an explicit algorithmic result that, when `omega_vec(T)<=2`, constructs an
  ordering whose backedge graph has clique number at most `100`.

These statements are compatible with the repository's negative answers to
Question 5.9. The preprint's certificate theorem permits a threshold `f(k)`
strictly larger than `k`; the critical families prove that the identity
threshold cannot work for `k=3,4,5`.

### Perfect tournaments

The preprint observes that the family `AC_N` is perfect in the directed sense
used there and raises the classification of perfect tournaments as a question.
This is not developed in the repository.

## 8. Novelty and provenance cautions

This comparison is mathematical, not a priority determination.

- The supplied PDF is dated June 6, 2026.
- The repository proof artifacts were edited on June 6-7, 2026.
- The preprint credits the `3`- and `4`-critical families to Aboulker, Charbit,
  and Thomassé.
- The repository contains an automated/human research history, including
  candidates found computationally before they were promoted to theorems.

The safe claims relative to the supplied materials are:

1. The repository's P13 and preprint Proposition 6.1 prove the same `k=3`
   family.
2. Preprint Proposition 6.2 proves the exact Delta family recorded earlier as
   repository candidate G22.
3. The repository's final `k=4` family `AC_N[C3]` is different from the
   preprint's `C3[AC_N]`.
4. The explicit infinite `k=5` family `AC_N[AC_N]` does not appear in the
   supplied preprint.
5. The D35 counterexample to additive substitution, and the resulting
   order-21 `4`-critical tournament, do not appear in the supplied preprint;
   the preprint itself does not assert the refuted law.

Any stronger statement such as "first in the literature" requires a separate
literature and chronology check.

## 9. Concise conclusion

The overlap is exact at `k=3`, and the preprint also proves one of the
repository's earlier `k=4` candidate families. The repository contains a
second, reverse-product `k=4` family. Its main additional theorem is
the now-complete, post-D36-repaired P19+P20 result:

```text
AC_N[AC_N] is 5-omega_vec-critical for every odd N>=7.
```

Hence the combined unconditional picture is:

```text
Conjecture 5.10 is proved for k=3,4,5,
Question 5.9 fails at k=3,4,5,
the universal additive substitution route is false,
no explicit 6-critical witness is currently known,
and the explicit/unconditional problem remains open for k>=6.
```
