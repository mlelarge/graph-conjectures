# Earth–Moon literature notes

Companion to [docs/plan.md](plan.md). Phase-0 audit deliverable.

## Conventions

Following [problems/pebbling_cartesian_product/docs/literature_notes.md](../../pebbling_cartesian_product/docs/literature_notes.md):

- **Primary** — quoted directly from the cited paper (PDF, arXiv, or DOI page).
- **Secondary (paraphrase)** — paraphrased from a paper or trusted source we read.
- **Repo data** — taken from a code artefact distributed with a paper.
- **User-summary (to verify)** — communicated to the project by a human collaborator
  with knowledge of the source. Promote to primary by direct PDF quote before any
  publication-grade use.

## Notation

- A graph $G$ is **biplanar** when its edge set decomposes as $E(G) = E_1 \sqcup E_2$
  with each $G_i = (V(G), E_i)$ planar. Equivalently, the *thickness* of $G$ is
  at most $2$.
- $\chi_{\rm EM} := \sup\{ \chi(G) : G \text{ biplanar} \}$.

## Kirchweger, Scheucher, Szeider — "SAT-Based Generation of Planar Graphs", SAT 2023

The methodological backbone for the project; tooling reuse vs. reimplementation
is gated on what they shipped and where.

- **Citation.** M. Kirchweger, M. Scheucher, S. Szeider. *SAT-Based Generation of
  Planar Graphs.* In *26th International Conference on Theory and Applications of
  Satisfiability Testing (SAT 2023)*, LIPIcs vol. 271, paper 14, Schloss Dagstuhl,
  2023. DOI: [10.4230/LIPIcs.SAT.2023.14](https://doi.org/10.4230/LIPIcs.SAT.2023.14).
- **Source code (announced in paper).** SAT modulo Symmetries (SMS):
  [github.com/markirch/sat-modulo-symmetries](https://github.com/markirch/sat-modulo-symmetries),
  MIT licensed, C++ + Python.
- **Local pin.** This project's vendored clone is at commit
  `cf890fda5e9da0f749a40b638998bbbf2a1cd092`, `git describe` =
  `v2.0.0-2-gcf890fd`, committed 2025-10-31. The SAT 2023 paper described
  the `v1.0.0` release; we are on a slightly later mainline with two extra
  commits on top of `v2.0.0`. The planarity propagator and `--earthmoon*`
  CLI flags are in mainline at this pin.
- **Documentation.** [sat-modulo-symmetries.readthedocs.io](https://sat-modulo-symmetries.readthedocs.io/).

### Abstract — primary

Verbatim from the DROPS landing page:

> To test a graph's planarity in SAT-based graph generation we develop SAT
> encodings with dynamic symmetry breaking as facilitated in the SAT modulo
> Symmetry (SMS) framework. We implement and compare encodings based on three
> planarity criteria. In particular, we consider two eager encodings utilizing
> order-based and universal-set-based planarity criteria, and a lazy encoding
> based on Kuratowski's theorem. The performance and scalability of these
> encodings are compared on two prominent problems from combinatorics: the
> computation of planar Turán numbers and the Earth-Moon problem. We further
> showcase the power of SMS equipped with a planarity encoding by verifying
> and extending several integer sequences from the Online Encyclopedia of
> Integer Sequences (OEIS) related to planar graph enumeration. Furthermore,
> we extend the SMS framework to directed graphs which might be of independent
> interest.

### Encoding details — repo data

The planarity encoding is in mainline SMS at
[`src/graphPropagators/planarity.{hpp,cpp}`](../external/sat-modulo-symmetries/src/graphPropagators/),
with a Python wrapper at
[`encodings/planarity.py`](../external/sat-modulo-symmetries/encodings/planarity.py).
Documented in [`docs/applications.md`](../external/sat-modulo-symmetries/docs/applications.md)
under "Planar graphs, Earth-Moon Problem, planar Turán Numbers and ...".

The SAT 2023 paper described the `v1.0.0` release. **For Earth–Moon
reproductions we pin the local clone to `v1.0.0`**; an inspection of the
`v2.0.0`-mainline clone (`v2.0.0-2-gcf890fd`) showed API drift in
`encodings/planarity.py` and removal of the `--thickness2` CLI flag from
`smsg`'s options — see [`spike_sms_build.md`](spike_sms_build.md) for
the full audit. Use `v1.0.0` for any solver run whose output is meant to
be cited.

Three planarity encodings are exposed as command-line flags:

- **Kuratowski (lazy)**: `--planar` on `pysms.graph_builder`, with a propagator
  invoked at frequency $1/5$ (every fifth node in the SAT search; on a positive
  hit a Kuratowski subgraph is extracted and used to generate a blocking clause).
- **Schnyder order (eager)**: `--planar_schnyder` on `encodings/planarity.py`.
- **Universal set (eager)**: `--planar_universal` on `encodings/planarity.py`.

For the Earth–Moon problem specifically, `encodings/planarity.py --earthmoon c`
adds the following automatic constraints (per [`docs/applications.md:166`](../external/sat-modulo-symmetries/docs/applications.md)):

> Automatically, some assumptions are made when using the parameter `--earthmoon c`
>
> - The graph $G_1$ is maximal planar
> - $K_5$ and $K_{3,3}$ are excluded explicitly as subgraph for both $G_1$ and $G_2$.
> - The underlying graph has minimum degree $\geq c - 1$.

The decomposition is encoded on a directed graph (per the abstract's directed-SMS
extension): an antiparallel arc pair encodes a layer-1 edge, a single arc a
layer-2 edge. The thickness-2 layer-2 propagator is enabled with
`--args-SMS " --thickness2 5"`, mirroring the frequency-$1/5$ check on layer 1.

### Earth–Moon results in the shipping code — repo data

The repo ships **two named candidate tests** for biplanarity, both of which are
direct hits for our plan:

- `--earthmoon_candidate1` (n=19): tests whether
  $C_5[K_{4,4,4,4,3}] = C_5[4,4,4,4,3]$ is biplanar
  ([`encodings/planarity.py:217-223`](../external/sat-modulo-symmetries/encodings/planarity.py)).
  *Per user-summary (to verify against PDF body): this case was certified
  non-biplanar in ~12 hours of solver time.*
- `--earthmoon_candidate2` (n=28): tests whether
  $C_7[K_4] = C_7\boxtimes K_4$ — exactly our Phase 4 headline target — is
  biplanar
  ([`encodings/planarity.py:217,225-228`](../external/sat-modulo-symmetries/encodings/planarity.py)).

The fact that `candidate2` is shipped as a named CLI option but no result on it
appears in the abstract strongly suggests **KSS attempted it and it did not
terminate**, leaving $C_7[K_4]$ open. This reframes our Phase 4: we are not
pioneering a SAT attack on $C_7[K_4]$, we are picking up where KSS stopped.

The $n \le 13$ "every biplanar graph is 9-colourable" result is a separate
SMS run (Earth-Moon search at $n \le 13$, $\chi \ge 10$ proves UNSAT). User-summary,
to verify against PDF body for the exact bound.

### Decision: what we fork, imitate, ignore — revised

The candidate-flag discovery flips the architecture:

- **Use SMS directly** for the Phase 4 candidate runs and the Phase 5 joint search.
  Reimplementing a local oracle that competes with `--earthmoon_candidate2`
  would be reproducing KSS line-for-line. Concretely:
  - Run `--earthmoon_candidate2` ourselves on better hardware / with longer
    budgets than the original team likely used. If it terminates UNSAT we have
    a Phase 4 ruling; if it terminates SAT we have a counterexample.
  - Run `--earthmoon` with our own weighted-blowup encodings for the Phase 4
    sweep over $(2r+1, a_1, \dots, a_{2r+1})$.
- **Local lazy-Kuratowski CEGAR** drops to a *secondary verifier*: take any
  positive certificate SMS emits and replay it through `networkx.check_planarity`
  on each layer, in our own Python. Defends against bugs in either codebase.
- **Ignore.** The Schnyder-order and universal-set planarity encodings — KSS
  found Kuratowski faster.

### Resolved / remaining

Resolved by the spike:

- Planarity encodings live in mainline `main`, tagged `v1.0.0`. Not a branch.
- Earth-Moon-specific encoding is exposed at the CLI; we do not need to
  reverse-engineer it.
- $C_7[K_4]$ is `--earthmoon_candidate2`. They built the test, did not publish
  a result.

Remaining for direct PDF quote (still user-summary):

- Exact bound for the "all biplanar graphs on $n \le N$ are 9-colourable" claim
  ($N = 13$ per user; verify against PDF table).
- Reported wall-clock / solver budget for `candidate1`.
- Whether `candidate2` was reported as run-and-timed-out, or merely scaffolded.

### Spike notes — local build status

Build prerequisites per [`build-and-install.sh`](../external/sat-modulo-symmetries/build-and-install.sh)
and the RtD getting-started page:

- C++20 compiler, Boost ≥ 1.74, CMake ≥ 3.12, Python + pip.
- CaDiCaL submodule (init via `git submodule update --init --recursive`).
- Build: `./build-and-install.sh -l` (local install into `~/.local/`, no sudo).

Status on this machine (darwin, 2026-05-10): `cmake`, `c++`, `nproc` not in
PATH; build script's `nproc --all` line will fail on macOS regardless. Boost
not installed.

Minimum to unblock the build:

```bash
brew install cmake boost coreutils
xcode-select --install   # if Xcode CLT not already present
```

`coreutils` provides `gnproc`; the script's `nproc --all` line still needs
either a shim or a tiny patch (e.g. replace with `sysctl -n hw.ncpu` on
darwin). I have not run `brew install` — that's a system-level change and
needs your sign-off.

## Boutin, Gethner, Sulanke — 2008

*Placeholder.* To collect from the published version: full title, journal,
volume/pages, exact statement of which 9-critical thickness-2 graphs they
construct, the count by graph order, and any computer-search documentation.
First pass via [DBLP](https://dblp.org/pid/23/4366).

## Gethner, Sulanke — 2009

*Placeholder.* Infinite family of 9-critical thickness-2 graphs. Collect the
exact parametric construction and the smallest member by order, since both
are needed as regression inputs to the Phase 1 oracle.

## Catlin / Gethner clique-blowup line

*Placeholder.* Original Catlin reference for clique blowups of odd cycles as
chromatic-extremal graphs; Gethner's deployment of blowups in the Earth–Moon
context. Used as the construction template behind Phase 4.

## Kostochka, Yancey — 2014

- **Citation.** A. V. Kostochka, M. Yancey. *Ore's conjecture for $k = 4$ and
  Grötzsch's theorem.* *Combinatorica* 34 (2014), 781–797. The general $k$-critical
  density bound is in their companion paper *Density of $k$-critical graphs*
  ([arXiv:1209.4255](https://arxiv.org/abs/1209.4255)), JCTB 2014.
- **Statement — paraphrase, to verify against PDF.** Every $k$-critical graph $G$
  on $n$ vertices satisfies
  $$|E(G)| \ge \frac{(k+1)(k-2)}{2(k-1)} n - \frac{k(k-3)}{2(k-1)}.$$
- **Specialisation $k = 12$.** $|E(G)| \ge (65 n - 54)/11$.
- **Earth–Moon application.** Combined with $|E(G)| \le 6n - 12 = (66 n - 132)/11$,
  the inequalities are jointly satisfiable only for $n \ge 78$. A density
  strengthening exploiting $K_9$-freeness — adding any $c\,n$, $c > 0$ — closes
  $\chi_{\rm EM} \le 11$. This is the Phase 6 target.

## Mansfield — 1983

- **Citation.** A. Mansfield. *Determining the thickness of graphs is NP-hard.*
  *Math. Proc. Camb. Phil. Soc.* 93 (1983), 9–23.
- **Implication.** Biplanarity testing is NP-hard, so polynomial-time oracle is
  off the table. Justifies the SAT-based approach in Phase 1.

## Hutchinson — 1993

- **Citation.** J. P. Hutchinson. *Coloring ordinary maps, maps of empires and
  maps of the moon.* *Math. Mag.* 66 (1993), 211–226.
- **Use.** Survey / framing reference; not load-bearing.

## Sulanke / Gardner — 1974/1980

- **Construction.** The graph $K_6 + C_5$ (join of $K_6$ and the 5-cycle) is
  biplanar with $\chi = 9$, witnessing $\chi_{\rm EM} \ge 9$. Attributed to
  Sulanke (private communication, 1974); reported by Gardner in *Sci. Amer.*
  242 (1980), 14–22.
- *Promote to primary by direct quote from the Gardner column.*

## Heawood — 1890

- **Citation.** P. J. Heawood. *Map Colour Theorems.* *Quart. J. Pure Appl. Math.*
  24 (1890), 332–338. Source of the upper bound $\chi_{\rm EM} \le 12$ via
  $\delta(G) \le 11$ and induction.
