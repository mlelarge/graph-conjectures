# Review of `attack_plan.md` v3

Date: 2026-05-16

## Executive verdict

Version 3 is now a credible attack plan. The two serious defects in v2 have
been fixed:

1. The split-digraph literature is now correctly separated into
   2-vertex-strong examples from Bang-Jensen--Wang and 2-arc-strong exceptions
   from Ai--He--Li--Qin--Wang.
2. The Eulerian logarithmic milestone is now correctly routed through
   undirected Karger cut counting via the underlying multigraph.

This is no longer just a speculative strategy document. It has a sensible
first theorem, a concrete verifier contract, a corrected benchmark list, and a
counterexample search focused on the right obstruction templates.

I would make only minor edits before starting:

- add a factor of 2 in the EC-log union bound for the two orientations of each
  undirected cut;
- remove the phrase "alteration finish" from the EC-log proof outline, because
  expectation \(<1\) already gives a coloring with no bad directed cut;
- explicitly say that Karger's bound is used for the underlying undirected
  **multigraph**;
- treat the SAT solver as secondary to the ILP/cut-separation implementation,
  not as equal priority from the first engineering sprint.

The answer to "do we need an expert coder?" is: not for the EC-log theorem, yes
for the computational backbone if the goal is reliable counterexample search
rather than toy experiments.

## Mathematical assessment

### WC3 is the right north star

The plan's organizing conjecture is now exactly right:

> (WC3) Every 3-arc-strong digraph has a strong arc decomposition.

Known positive classes line up with this: semicomplete digraphs,
locally semicomplete digraphs, semicomplete compositions, and split digraphs
all satisfy a 3-arc-strong positive theorem. Known obstructions live at
arc-connectivity 2.

This does not make WC3 likely in any formal sense, but it makes it the right
problem to attack. A 3-arc-strong counterexample family would be publishable
and would reset expectations. A failure to find one, especially after a
structured search over genuine 2-arc-strong obstruction templates, would
strengthen the case for a positive \(K=3\) program.

### Literature corrections are now satisfactory

The plan now correctly records:

- Bang-Jensen--Yeo: semicomplete characterization, \(S_4\) as the exception.
- Bang-Jensen--Huang: locally semicomplete characterization, squares of even
  directed cycles as the exceptions.
- Bang-Jensen--Gutin--Yeo: semicomplete compositions, four exceptional
  digraphs.
- Bang-Jensen--Wang: every 3-arc-strong split digraph works, plus infinite
  2-vertex-strong bad examples.
- Ai--He--Li--Qin--Wang: actual 2-arc-strong split obstruction
  characterization.

That is the right benchmark landscape.

### EC-log proof is basically sound

The Eulerian reduction is correct. If \(D\) is Eulerian and \(G\) is the
underlying undirected multigraph, then for every nontrivial \(X\),

\[
d_G(X)=|\delta_D^+(X)|+|\delta_D^-(X)|=2|\delta_D^+(X)|.
\]

Thus directed cuts of size \(s\) in \(D\) correspond to undirected cuts of size
\(2s\) in \(G\). Karger's undirected near-minimum cut-counting theorem applies
to \(G\).

The proof needs only a small bookkeeping correction: each undirected cut
\(\{X,V\setminus X\}\) corresponds to two directed cuts,
\(\delta^+(X)\) and \(\delta^+(V\setminus X)\). This adds a harmless factor of
2 to the expectation bound. With \(\lambda\ge C\log_2 n\) and \(C>4\), the
argument still goes through.

The proof outline currently says:

> "A union-bound / alteration finish..."

No alteration is needed if the expected number of bad directed cuts is \(<1\).
The probabilistic method directly gives a coloring with zero bad cuts.

Suggested replacement:

> By the first moment method, if this expectation is \(<1\), there exists a
> 2-coloring with no monochromatic directed cut.

### Track B is now pointed at the right objects

The counterexample search now correctly prioritizes:

- laminar systems of tight 3-cuts;
- Eulerian \(\lambda=3\) cut-rich examples;
- gluing genuine 2-arc-strong obstruction templates along controlled 3-arc
  interfaces.

That is much better than searching random dense examples or arbitrary
2-vertex-strong split examples.

One warning: gluing \(S_4\), even-cycle squares, semicomplete-composition
exceptions, and split exceptions may destroy the obstruction quickly. The
search should log not just SAT/UNSAT but also:

- the minimum directed cuts before and after gluing;
- which old tight cuts survive;
- whether the UNSAT core uses local cuts, interface cuts, or new global cuts.

Without that metadata, computation will not teach much.

### Track C is appropriately risky

The controlled-lifting program is still the mathematically hard part. The plan
now states the risk correctly: extracting a class-agnostic lemma from the
split-digraph proof may fail.

Near-split and one-sided locally semicomplete classes are plausible next
targets. Bounded independence number is more ambitious. The quasi-transitive
note is now cautious enough.

## Computational assessment

### Do you need an expert coder?

For Phase 1, no. EC-log is a paper proof. A coder is irrelevant there.

For Phases 2-3, yes, unless the goal is only small toy experiments. A reliable
SAT/ILP/cut-separation pipeline is not hard in the sense of software scale, but
it is very easy to get subtly wrong. The key risk is not performance; it is
certification.

The needed person is not a generic application developer. The useful profile is
a combinatorial optimization / graph algorithms coder who is comfortable with:

- max-flow/min-cut separation;
- integer programming with lazy constraints, preferably Gurobi;
- SAT or PySAT/CaDiCaL if SAT is pursued;
- graph isomorphism/canonical labeling, ideally `nauty`, `Traces`, or Sage;
- generating and checking small extremal digraph families;
- writing independent validators for every claimed SAT/UNSAT output.

An expert coder is most valuable for three tasks:

1. Implementing the ILP/cut-separation model correctly.
2. Building reproducible generators for obstruction-template gluing.
3. Producing machine-checkable certificates or at least independently
   verifiable logs for every interesting UNSAT/SAT case.

If only one implementation exists, do ILP first. SAT can wait. The ILP model is
closer to the mathematics and easier to audit.

### Recommended engineering stack

Use a small, boring stack:

- Python for orchestration.
- `networkx` or `igraph` for graph plumbing.
- Gurobi for ILP with lazy cut separation.
- A custom min-cut separator for each color class.
- `pynauty`, Sage, or external `nauty/Traces` for canonicalization.
- Optional PySAT/CaDiCaL only after the ILP baseline is trusted.

Do not start with a sophisticated SAT encoding. Start with the cut formulation:

\[
1\le \sum_{e\in\delta^+(X)}x_e\le |\delta^+(X)|-1.
\]

For a proposed coloring, separation is simple:

- check whether the red subdigraph is strong;
- if not, extract a violated directed cut;
- check whether the blue subdigraph is strong;
- if not, extract a violated directed cut.

That gives an exact lazy-constraint loop.

## Remaining edits to `attack_plan.md`

I recommend these small textual changes.

### EC-log bookkeeping

In the proof outline, after invoking Karger, add:

> Each undirected cut accounts for at most two directed cuts, one for each side.
> This only changes the expectation by a factor of 2.

Then replace:

> "A union-bound / alteration finish..."

with:

> "By the first moment method, the expectation being \(<1\) implies the
> existence of a coloring with no monochromatic directed cut."

### Phase 2 wording

The SAT implementation should be explicitly second:

> Build ILP/cut-separation first. Add SAT/arborescence witnesses only after the
> ILP baseline has passed the benchmark suite.

This is a better engineering order.

### EC-log risk

The risk for Phase 1 should probably be "low" rather than "low-medium", unless
the intended write-up needs optimized constants. The theorem as stated should
follow from standard Karger counting with a generous constant.

## Bottom line

The plan is now good enough to start.

Do Phase 1 immediately: write EC-log cleanly, with the factor-of-two cut
bookkeeping. Then build the ILP verifier before touching SAT. For the coding
work, use an expert graph/optimization coder if available; otherwise keep the
scope narrow and insist on independent validators from day one.

