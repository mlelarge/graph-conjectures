# H16 - the proposed omega-bar substitution upper bound is false

**Proposed statement.** For all tournaments `S,H`,

`omega_bar(S[H]) <= omega_bar(S)+omega_bar(H)-1`.

Together with the proved reverse inequality, this would have made
`omega_bar-1` additive under lexicographic substitution.

**Status: REFUTED.** There is a tournament `H` on seven vertices such that

`omega_bar(C3)=omega_bar(H)=2`, but `omega_bar(C3[H])=4`.

The proposed upper bound predicts `3`. The reverse product is asymmetric:
`omega_bar(H[C3])=3`.

## 1. A minimal order-7 inner factor

Let `H` have vertex set `{0,...,6}` and arcs

```text
01 02 30 40 05 60
12 13 14 51 61
23 24 25 62
34 53 36
45 46
56
```

Here `uv` means `u -> v`. In the identity order `0<1<...<6`, the backedge
graph has edge set

```text
03, 04, 06, 15, 16, 26, 35.
```

This is a 5-cycle

`0-3-5-1-6-0`

with pendant vertices `4` at `0` and `2` at `6`; in particular it is
triangle-free. Hence `omega_bar(H)<=2`. The directed triangle
`0->1->3->0` gives `omega_bar(H)>=2`, so

`omega_bar(H)=2`.

An exhaustive `gentourng` census gives the sharper finite statement:

- no inner tournament `H` of order at most `6` makes `C3[H]` violate the
  proposed bound;
- among the `456` isomorphism classes of order `7`, exactly `3` do;
- the displayed `H` is class `307` in the census used by the verification
  script.

Thus order `7` is minimal for a counterexample with fixed outer factor `C3`.

## 2. Exact value of the product

Set `T=C3[H]`, so `|T|=21`.

### Upper bound

Use the identity order on the three consecutive `H`-blocks, and the identity
order inside each block. Each block contributes a triangle-free backedge
graph. Between the first and third blocks all edges are backedges, while the
other two block pairs contribute none. Therefore a maximum backedge clique
uses an edge from each of those two blocks and has size `4`:

`omega_bar(T)<=4`.

The exact graph computation gives identity-order clique number `4`.

### Lower bound

The no-`K4` ordering CNF for `T` is unsatisfiable. **Independently checkable
certificate** (`scripts/certify_h16_counterexample.py` → `data/h16_cert/`): for *each* of two
encodings — consecutive-chain and all-pairs-backward, which produce CNFs with **different
SHA-256 checksums** (different clique-forbidding clauses over the same `2214` transitive
four-sets) — the script exports the **DIMACS CNF** (with checksum) and the **DRAT refutation
proof** from Cadical, and confirms UNSAT under **both** `Cadical153` *and* `Minisat22` (four
solver runs). The DIMACS CNFs are re-decidable by any external solver and the DRAT proofs are
verifiable by an independent checker:

```
drat-trim data/h16_cert/noK4_chain.cnf    data/h16_cert/noK4_chain.drat      # expect "s VERIFIED"
drat-trim data/h16_cert/noK4_allpairs.cnf data/h16_cert/noK4_allpairs.drat
```

UNSAT means every total order of `T` has a backedge `K4`, so

`omega_bar(T)>=4`.

Consequently

`omega_bar(C3[H])=4 > 2+2-1=3`.

The no-`K5` formulas are satisfiable under both encodings; the chain encoding
decodes to the identity order, whose clique number is independently recomputed
as `4`.

## 3. The failure is directional and critical

For the reverse substitution, the no-`K4` formula is satisfiable and decodes
to an order of clique number `3`. The standard substitution lower bound gives
the reverse inequality, hence

`omega_bar(H[C3])=3`.

Moreover, `C3[H]` is `4`-`omega_bar`-critical. Every one-vertex deletion has a
decoded width-`3` order. It also contains `C3[C3]`: after deleting a vertex,
the damaged copy of `H` still contains a directed triangle, as do the two
untouched copies. Since `omega_bar(C3[C3])=3`, every deletion has value exactly
`3`.

Thus two width-`2` factors can produce a critical width-`4` tournament and
attain the elementary multiplicative upper bound `2*2`.

## 4. What went wrong in the previous H16 reduction

The block-laminarity lemma itself is correct:

> In any order of `S[H]`, the vertices of a backedge clique that lie in two
> distinct substitution blocks cannot interleave. Ordering the touched blocks
> by their clique positions gives a backedge clique in `S` under that induced
> block order; the vertices inside each touched block form a backedge clique
> in `H` under the induced within-block order.

The invalid step was the next one. From this lemma one cannot conclude that
the clique touches at most `omega_bar(S)` blocks or uses at most
`omega_bar(H)` vertices per block. Both parameters are minima over all orders,
whereas the induced block and within-block orders above are arbitrary.

The simplest warning is a transitive triple: `omega_bar(TT3)=1`, but its
reverse order has a three-vertex backedge clique. An arbitrary induced order
therefore cannot be bounded by `omega_bar`.

The earlier "total fattening" reformulation inherited the same quantifier
error. Capping

`sum_s (|K_s|-1)`

does not imply the proposed bound unless the same order also bounds the number
of touched blocks by `omega_bar(S)`. H16 asserted that such simultaneous
control always exists; the counterexample proves that it does not.

The valid general upper bound remains

`omega_bar(S[H]) <= omega_bar(S) * omega_bar(H)`,

obtained by taking a block-respecting product of optimal orders. The
counterexample attains equality.

## 5. Consequences

1. `omega_bar-1` is not additive under substitution.
2. The proposed tree-depth/min-max characterization based on that additivity
   cannot exist in the stated form.
3. The H16 route from the proved `k=3,4,5` families to all `k>=6` is closed.
4. Special identities such as `omega_bar(AC_n[C3])=4` and
   `omega_bar(AC_n[AC_n])=5` remain valid because their proofs use additional
   arithmetic structure, not a general substitution law.
5. Positive datapoints such as `omega_bar(QR_19[AC_7])=6` are genuine but were
   non-discriminating; a universal statement cannot be inferred from them.

## 6. Reproduction

Run

```bash
uv run python \
  problems/tournament_clique_number_omega_cluster/scripts/refute_h16_substitution_law.py
```

The script writes `data/h16_counterexample.json` and checks:

- exact `omega_bar(H)=2` by all `7!` orders;
- both distinct SAT checks for `omega_bar(C3[H])=4`;
- `omega_bar(H[C3])=3`;
- all `21` deletion values;
- non-isomorphism with `AC_7[C3]` and `AC4_21`;
- the exhaustive inner-order census through order `7`.
