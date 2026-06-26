# D67: One-Sided Prefix-Plus-Pending Formula

Date: 2026-06-19.

Artifact: `scripts/one_sided_prefix_pending_audit.py`.

## Purpose

D66 refuted the old two-sided endpoint-cleanliness condition.  Endpoint
entries into an active prefix are not forced by sealed-block/CL/DT and
are not needed for directed out-cuts.

This note records the corrected positive statement: the
prefix-plus-pending formula only needs one-sided rho-exit cleanliness.

## One-Sided Formula

Let `C` be the split semicomplete core obtained by deleting pending
vertices `I`.  Let `Q subseteq V(C)` and `J subseteq I`.  Assume:

1. pending vertices are independent;
2. pending vertices have no arcs to non-core vertices in the relevant
   host calculation;
3. `Q` has no out-arcs to the chord endpoints.

Endpoint entries into `Q` are allowed.

Write

    b(Q)   = |delta_C^+(Q)|,
    e_i(Q) = |A(Q, i)|,
    f_i(Q) = |A(i, C \ Q)|.

Then in the original host

    |delta^+(Q union J)|
      = b(Q)
        + sum_{i notin J} e_i(Q)
        + sum_{i in J} f_i(Q).                 (PP1)

### Proof

Partition arcs leaving `Q union J` by their tail.

Arcs with tail in `Q` and head in `C \ Q` contribute exactly `b(Q)`.
Arcs with tail in `Q` and head a pending vertex contribute only when
that pending vertex is outside `J`, giving
`sum_{i notin J} e_i(Q)`.  Arcs with tail in `Q` and head a chord
endpoint would be extra correction terms, and are excluded by assumption
3.

For a pending vertex `i`, if `i notin J`, then arcs out of `i` have tail
outside `Q union J` and do not contribute.  If `i in J`, the contributing
arcs are exactly the arcs from `i` to `C \ Q`, giving `f_i(Q)`.
Assumptions 1 and 2 remove arcs from `i` to other pending or non-core
vertices.

Finally, arcs from a chord endpoint into `Q union J` have tail outside
the cut, so they are never counted by the directed out-cut.  Thus no
no-entry hypothesis is needed.  QED.

## Capacity Consequence

If the original host is 3-arc-strong, then (PP1) is at least three for
every `J`.  Minimizing independently over each pending vertex gives

    sum_i min(e_i(Q), f_i(Q)) >= 3 - b(Q).      (CAP1)

This is the same capacity inequality used by D61/D64.  D66 only changes
which endpoint-cleanliness hypotheses are legitimate.

## Rho-Exit Cleanliness From CL

Work in `D^bullet`, with `rho` the contracted chord endpoint.  Let `B`
be the sealed CL block and let `I_B` be the forced pending tails removed
from the split core.  Put

    Q0 = B \ I_B.

CL says every arc from the sealed block into the outside closure is a
forced chain crossing, except possibly the terminal `p_k -> rho` label.
In the nonterminal multi-crossing block used for the active middle
prefix, every forced crossing leaving `B` has its tail in `I_B`.  After
the split core deletes `I_B`, no vertex of `Q0` has an arc to `rho`.
Thus `Q0` has no host out-arc to a chord endpoint.

For an internal side prefix `Q0 \ {h}`, deleting a vertex cannot create
a rho-exit, so one-sided cleanliness is inherited.

For a successor prefix `Q0 union {w1}`, where `w1` is the first chain
successor after the middle block, one-sided cleanliness is equivalent to
`w1` not being the terminal rho-tail.  In the nonterminal
multi-crossing case this follows from the sealed shortest path: if
`w1 -> rho` existed, then the path

    v -> ... -> i1 -> w1 -> rho

would terminate at the first successor and would bypass the later forced
crossings.  That contradicts the assumed multi-crossing sealed path.

So every active prefix used in the D64/D65 profile has the required
one-sided rho-exit cleanliness.

## Audit

The executable audit checks four variants:

    D42 original,
    D63 reverse-head perturbation,
    D66 rho-entry perturbation,
    D63 + D66 combined.

For each variant, each `Q in {Q-,Q0,Q+}`, and every
`J subseteq {9,11,13}`, it verifies (PP1), 3-arc-strongness of
`Q union J`, absence of endpoint exits, and absence of pending/non-core
correction terms.

The two rho-entry variants have endpoint entries

    endpoint_entries(Q0) = [(0,6)],
    endpoint_entries(Q+) = [(0,6)],

yet (PP1) still holds.

The combined variant also confirms compatibility with D63:

    core_outs(Q-,Q0,Q+) = (2,0,1),
    endpoint_entries(Q0)=endpoint_entries(Q+)=[(0,6)].

## Consequence

D67 replaces the obsolete D62 endpoint-cleanliness requirement by the
correct one-sided condition:

> For prefix-plus-pending out-cut algebra, active prefixes must have no
> rho-label exits.  Rho-label entries are allowed.

The remaining D65 structural target is now purely local: prove the
head-block/internal-cut lemma, the first-successor/external-prefix
lemma, and the single-exchange exclusion in the nonterminal
sealed multi-crossing normal form.
