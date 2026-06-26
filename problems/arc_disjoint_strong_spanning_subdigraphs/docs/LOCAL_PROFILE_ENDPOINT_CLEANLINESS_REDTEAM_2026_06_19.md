# D66: Local Profile Proof Boundary and Endpoint-Cleanliness Red-Team

Date: 2026-06-19.

Artifact: `scripts/rho_entry_endpoint_cleanliness_redteam.py`.

## Verdict

The requested package cannot be proved exactly as stated from the
current sealed-block/CL/DT hypotheses if "endpoint-cleanliness" includes
absence of chord-endpoint entries into the active prefix.

Rho-label exits from an active prefix are structural and are the only
endpoint condition needed for the D62 prefix-plus-pending out-cut
formula.  Rho-label entries into an active prefix are not forced by
sealed-block/CL/DT and are harmless for directed out-cut bookkeeping.

## Red-Team Perturbation

Start from the D42 chain kernel and add one D-bullet arc

    rho -> h

where `h` is a head vertex.  In the checked D42 labels this is

    0 -> 5       in D-bullet labels,
    0 -> 6       in host labels.

The executable audit verifies that this perturbation preserves:

    simple (1,0)-near-split host,
    sealed-chain structural gates,
    lambda(host)=lambda(D^bullet)=3,
    the original hard gateway U-exit,
    the split-core low-cut profile.

The low core cuts remain exactly

    Q- = {2,3,4,5,7,8}          out=1,
    Q0 = {2,3,4,5,6,7,8}        out=0,
    Q+ = {2,3,4,5,6,7,8,10}     out=1.

But endpoint entries appear:

    endpoint_entries(Q0) = [(0,6)],
    endpoint_entries(Q+) = [(0,6)].

Endpoint exits remain empty for all three prefixes.

Thus the old D62 cleanliness condition "no chord endpoint enters a
deficient prefix" is not a theorem of sealed-block/CL/DT.

## Why The Entry Condition Is Unnecessary

For a prefix `Q` and pending set `J`, the D62 formula concerns the
directed out-cut of

    Q union J

in the original host.  An endpoint entry has tail outside `Q union J`
and head inside `Q union J`; it is not counted by the directed out-cut.

The red-team script checks that, even after adding `rho -> h`, the
formula

    d^+(Q union J)
      = b(Q)
        + sum_{i notin J} e_i(Q)
        + sum_{i in J} f_i(Q)

still holds for every `Q in {Q-,Q0,Q+}` and every
`J subseteq {9,11,13}`.

Therefore the correct endpoint condition for the pending cut algebra is
one-sided:

> no active prefix has a rho-label exit.

Endpoint entries may be present.

## Rho-Exit Cleanliness From CL

Let `B` be the sealed CL block and let `I_B` be the forced pending tails
deleted in the split core.  Put

    Q0 = B \ I_B.

CL says that every arc leaving `B` is a forced chain crossing, up to the
possible terminal `p_k -> rho` label.  In a nonterminal sealed
multi-crossing block, the forced crossings leaving `B` have tails in
`I_B`; the terminal `rho` tail, if present, lies outside the middle
prefix or is part of the terminal block rather than the active `Q0`.

Hence no vertex of `Q0` has a rho-label exit, and no active side prefix
obtained by deleting a head from `Q0` can acquire a rho-label exit.
For the successor prefix `Q0 union {w1}`, rho-exit cleanliness is the
local condition that the first successor `w1` is not the terminal
rho-tail.  This is exactly the nonterminal multi-crossing case used by
D42.

So the provable and needed cleanliness statement is:

    endpoint_exits(Q) = empty

for every active prefix `Q`.  The stronger
`endpoint_entries(Q)=empty` statement is false.

## Local Low-Cut Conditions

D65 already proves the global semicomplete reduction.  Once `Q0` is a
zero prefix, every possible low split-core cut is one of:

1. an internal cut inside `C[Q0]`;
2. an external-prefix cut `Q0 union B`;
3. a single-exchange mixed cut `(Q0 \ {h}) union {w}`.

The remaining local proof target must therefore be stated without the
false endpoint-entry clause:

> In the nonterminal sealed multi-crossing normal form, the only active
> internal low cuts are the one-head-deleted prefixes whose actual
> out-size is below two; the only active external-prefix low cut is the
> first-successor prefix when its actual out-size is below two; and the
> single-exchange obstruction is excluded by the internal in-neighbour
> supplied by cage hooks, the cage packing, and the `u -> AV_u` heads.

The last sentence is the correct local theorem to prove next.  D66 does
not promote it as fully proved from the written CL/DT notes, because the
current CL statement records the sealed boundary classification but does
not spell out all head-block and first-successor local normal-form
axioms needed for the internal/external classification.

## Consequence

The proof stack should be adjusted as follows:

1. Replace D62 endpoint-cleanliness by **rho-exit cleanliness**.
2. Keep endpoint entries out of the structural target; they are neither
   forced nor needed.
3. Continue the D65 local proof only after the head-block and
   first-successor normal-form facts are stated explicitly as CL/DT
   consequences or as separate lemmas.

This preserves the D64/D65 pending-decomposition route and prevents the
proof from depending on a false no-entry assertion.
