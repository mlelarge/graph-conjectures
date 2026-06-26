# D42 review: the next target is crossing selection, not termination

The D42 chain-kernel witness is sound after one metadata correction:
the host cell is `(5,19)`, not `(5,18)`.  The host has 24 vertices and
the contraction has 23.

## Correction to the proposed recipe

The formula

    X* = X_P union {forced O-vertices}

does not reproduce either verified repair on the witness.  It retains
all of `X_P`; the successful sets are instead small supersets of the
cage.  No existing "re-close" operation removes the retained K-vertices.

The claim that all prior machinery is independent of the choice of X is
also too strong:

* DT uses shortestness of `P_v` and the placement of rho-tails in `X_P`;
* OUT uses the path-plus-J structure of the complement;
* CT uses the `I -> K -> cage -> u` internal strata;
* CL classifies forced tails using the specific `X_P/O` split.

Those results remain valid at `X_P`; they do not automatically transfer
to an adaptively changed set.

## Free-entry absorption

The proved B3 surgery does not intrinsically require its new arc to be a
semicomplete hook.  The hook was only the device guaranteeing a free arc.

**Lemma B3+ (free-entry absorption).**  Let `(T,U)` be a failing pair at
`a`, with set `X`, unique U-exit `b=(u,y)`, and let `A` be the T-ancestor
path above `u`.  For `w notin X union A`, let `S_w` be its old T-subtree.
If there is an arc `d=(w,c)` with `c in X` and `d notin U`, then

    T' = T - e_w + d

is an in-arborescence arc-disjoint from U and

    X_a^{T'} = X disjoint-union S_w.

Moreover `(T',U)` is good whenever `|X union S_w| <= n-2` and

    [y notin X union S_w]
      + #{s in S_w : U(s) notin X union S_w} >= 2.

The proof is exactly B3: only the existence and U-freeness of `d` are
used after the hook lemmas.

On D42 choose `w=p5`.  The free entry is `p5->cage`,
`S_w={p4,p5}`, and the original U has exits

    (u,p3), (p4,ladder), (p5,p6).

The checked witness now asserts this one-shot repair explicitly.

Resume check D44: `scripts/chain_crossing_selection_check.py` extracts
the same hard pair and enumerates the B3+ condition directly.  It finds
34 free-entry candidates, 32 one-shot B3+ repairs, and 2 repairs at the
forced chain tail `p5=12`, via entries `(12,2)` and `(12,3)`.  This is
witness-level support for the selection target, not a proof of the
universal Chain Crossing Selection Lemma.

Resume check D45: `scripts/b3_selection_suite.py` applies the same exact
B3+ criterion to the stable explicit hard-gateway inventory:
`t_eq_u(D10)`, `rho_headless(D17)`, `dominated(D18)`,
`relay_free(D19)`, `core_embedding(D28)`, `blocker_cex(D30)`,
`saturation_kernel(D38)`, and `chain_kernel(D42)`.  All 8 have one-shot
B3+ repairs with `U` unchanged.  The branch-1 dynamic construction script
is not included because it currently fails its own host-lambda assertion
and is not stable in-class evidence in this workspace.

## Candidate chain lemma

The correct narrow target is:

**Chain Crossing Selection Lemma.**  In every in-class chain kernel that
also admits a hard gateway pair at the cage, some choice of hard pair
contains a forced crossing tail `w` (or a T-ancestor of that tail inside
the sealed block) satisfying B3+'s free-entry and exit-count conditions.

This would repair the chain kernel directly.  It is materially narrower
than re-running DT/OUT/AS/SAT/CT/CL on a new set and is falsifiable on a
single explicit pair.

If one-shot selection fails and repeated absorption is needed, the
termination part is automatic provided the sets are nested:

    X_0 proper-subset X_1 proper-subset ... .

The potential `n-1-|X_i|` decreases at every step, so no infinite
seal/absorb/re-seal sequence exists.  The genuine obligations are:

1. find a valid free-entry move after each re-seal;
2. keep the enlarged set intermediate, or invoke the boundary lemma;
3. never reset or shrink X during "re-closure".

Thus the research question is availability of monotone progress, not
well-foundedness once monotonicity has been established.
