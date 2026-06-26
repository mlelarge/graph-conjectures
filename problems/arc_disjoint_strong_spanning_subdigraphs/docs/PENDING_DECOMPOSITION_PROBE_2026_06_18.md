# D49: pending-decomposition split-off probe

Date: 2026-06-18.

Artifact:

    scripts/pending_decomposition_probe.py

Status: diagnostic evidence, not a theorem.  This is the first concrete
test of the split-digraph proof technology suggested by the literature
survey.

## Probe

For each near-split host, take the independent-side vertices
`s in V1 \ {p,q}` and choose two split-off paths

    x -> s -> y

with `x,y` in the semicomplete side `V2`.  Replace those two paths by
two core arcs `x -> y`, run the exact SAD verifier on the resulting
semicomplete core, and inspect the red/blue witness.  A `pending-hit`
means:

* the split-off core has a SAD;
* for each independent vertex `s`, its two split arcs receive opposite
  colours;
* replacing those coloured split arcs by the original two-step paths
  gives the pending-lift pattern used in the split-digraph literature.

This does not handle the chord endpoints `p,q`, and it is not a proof of
the published split-digraph theorems.  It is a local test of whether the
technology is aligned with our witness geometry.

## Results

Run:

    .venv/bin/python scripts/pending_decomposition_probe.py

Output summary:

* `rho_headless_D17_and_D47_host`: `pending-hit`.
* `dominated_D18_host`: `pending-hit`.
* `relay_free_D19_host`: `pending-hit`.
* `core_embedding_D28_host`: `no-pending-hit`; all 18 split choices had
  core SAD `UNSAT`, with best core lambda 1.
* `saturation_kernel_D38_host`: `pending-hit`.
* `chain_kernel_D42_host`: `pending-hit`.

The D42 hit is the important positive signal.  It uses the three
independent-side forced-chain vertices in the host labels
`9,11,13` and finds opposite-colour split arcs for all three:

    colours_by_s={9: ('R','B'), 11: ('B','R'), 13: ('B','R')}

Representative split paths:

    7  -> 9  -> 10
    8  -> 9  -> 4
    6  -> 11 -> 12
    15 -> 11 -> 4
    2  -> 13 -> 6
    16 -> 13 -> 14

Thus the D42 sealed chain kernel, which defeated universal `X_P`
recipes, is compatible with a split-off/pending-completion pattern.  This
is exactly the proof technology missing from fixed-`U` B3+ one-shot
repairs: the colours are chosen after the split core is decomposed.

## Interpretation

D47 remains a fixed-`U` one-shot B3+ defeat, but its host also has a
pending split-off hit.  That supports the post-D48 diagnosis: D47 kills
the local fixed-`U` formulation, not the global completion mechanism.

D28 is the warning case.  Its tournament-core geometry is not handled by
this naive two-split probe; the split core remains only 1-arc-strong in
the tested choices.  Any pending-decomposition proof must either:

1. use a different split choice / allow a larger critical path-pair
   operation for D28; or
2. treat the D28 tournament core by the existing multi-w/cut-avoidance
   mechanism instead of pending completion.

## Next target

The next useful script is a colour-prescribed version:

    pending_decomposition_prescribed_probe.py

It should force one chosen split arc through each independent vertex to
be red and the other blue, instead of relying on the SAT witness's
arbitrary colouring.  That would distinguish:

* robust pending decompositions, where prescribed split colours always
  complete; from
* accidental oracle colourings.

After that, try to phrase a pending Missing Entry Lemma: in a
non-degenerate sealed multi-crossing chain kernel, the forced chain
vertices admit split-off path pairs whose core SAD lifts to a completion
or supplies the B3+ entry.

## D50 follow-up

The colour-prescribed version has now been added as
`scripts/pending_decomposition_prescribed_probe.py`.  It confirms
prescribed hits on D17/D47 host, D18, D19, D38, and D42.  D42 succeeds on
the first split choice with forced opposite colours through all three
independent forced-chain vertices.  D28 remains no-hit in the naive
two-split formulation.
