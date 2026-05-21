# Attack plan — Path-FAS and Matching-FAS

> **Historical document.** This plan has been executed for the matching
> case. The structural lemmas conjectured in Phase 2 below are proved
> in [`lemmas.md`](lemmas.md), and the polynomial-time decider is
> implemented in [`../scripts/poly_mfas.py`](../scripts/poly_mfas.py).
> The path case (Phase 4) remains open. The text below is preserved as
> the original triage; consult `lemmas.md` and the top-level
> [`../README.md`](../README.md) for the actual results.

## Notation

- $T = (V, A)$: a tournament on $n$ vertices.
- A **FAS** of $T$ is a set $F \subseteq A$ such that $T \setminus F$ is acyclic.
  If $\prec$ is a topological order of $T \setminus F$, then the back-arc
  set $B_\prec(T)$ is contained in $F$. Conversely, every back-arc set of
  a total order is a FAS.
- $\underline{F}$: the undirected graph obtained from $F$ by forgetting arc
  orientations. Since $T$ is a tournament, no two arcs of $A$ share both
  endpoints, so $\underline{F}$ is a simple graph.
- $f(T)$: minimum FAS size of $T$.

## Two cases of Problem 4.4

- **MFAS** (matching case): does $T$ admit a FAS $F$ with $\underline{F}$ a
  graph of max degree $\le 1$ (matching)?
- **PFAS** (path case): does $T$ admit a FAS $F$ with $\underline{F}$ a path?
  (We interpret "path" as a connected graph with two endpoints of degree 1
  and all internal vertices of degree 2; under this interpretation $|F| \le
  n-1$ and exactly $|F|+1$ vertices are touched.)

We focus first on MFAS — its constraint (every vertex incident to $\le 1$
back-arc) is local and prima facie polynomially testable.

## Structural observations

### O1. Existence forces near-transitivity

If $T$ has a matching-FAS $F$, then $|F| \le \lfloor n/2 \rfloor$, so
$f(T) \le \lfloor n/2 \rfloor$. By Erdős–Moon, a random tournament has
$f(T) = \binom{n}{2}/2 - O(n^{3/2})$, which exceeds $n/2$ for all $n \ge 5$.
So almost every tournament is a NO instance, and the interesting subclass
is *very* near-transitive.

### O2. Local back-degree rewrite

Fix an order $\prec$ with positions $1, \ldots, n$. Define for each $v$:

- $d^-(v)$ = in-degree of $v$ in $T$;
- $\beta(v)$ = number of back-arcs in $T^{\prec}$ incident to $v$.

A short calculation (see [structural.py](../scripts/structural.py)) gives,
for $v$ at position $i$,
$$ \beta(v) = (i - 1) + d^-(v) - 2 \cdot |\{u \in N^-(v) : u \prec v\}|. $$

So $\beta(v) \le 1$ iff
$$ |\{u \in N^-(v) : u \prec v\}| \ge \lceil (i + d^-(v) - 2)/2 \rceil $$
and similarly $\beta(v) \ge 0$ gives an upper bound; together a
**window-of-width-$\le 1$** constraint on the number of in-neighbors of $v$
placed before $v$.

### O3. Matching-FAS ↔ "back-degree-$\le 1$ ordering"

The MFAS question is: does there exist an order $\prec$ on $V$ such that
every vertex has $\le 1$ back-arc?

### O4. Bottom and top vertices

If $\beta(v) = 0$, then $v$ is at position $i$ with exactly the *right*
number of in-neighbors before it; in particular the vertex placed at
position 1 has $\beta = 0$ iff it has in-degree 0 (it is a *king* / source
in $T \setminus F$), and the vertex at position $n$ has $\beta = 0$ iff it
has out-degree 0 in $T \setminus F$.

The two endpoints of $\prec$ are very constrained: position 1 must be in
$\{v : d^-(v) \le 1\}$ (vertex with $\le 1$ in-neighbor in $T$, since all
in-neighbors of position-1 lie after it and contribute to $\beta$) and
position $n$ must be in $\{v : d^+(v) \le 1\}$.

## Phased plan

### Phase 0 — instrumentation

- [ ] Verifier `verify(T, perm)` returning the back-arc set and a dict
  with `count`, `max_degree`, `is_matching`, `is_linear_forest`,
  `is_path`, `is_forest`.
- [ ] Brute-force `decide_mfas(T)` and `decide_pfas(T)` by enumeration.
- [ ] Unit tests on hand-checked tournaments.

### Phase 1 — empirical sweep

- [ ] Enumerate all non-isomorphic tournaments for $n = 3, 4, 5, 6, 7$ (and
  $n=8$ if feasible) using a canonical-form key. Count YES/NO for MFAS
  and PFAS, dump score sequences and example tournaments to
  `data/sweep_results.json`.
- [ ] Look for an OEIS-style sequence — is the YES-count a known quantity
  (related e.g. to "near-transitive" tournaments)?
- [ ] Identify small NO instances and any structural obstruction common
  to them (forbidden subtournament? minimum FAS exceeds $n/2$ trivially?
  some refined invariant?).

### Phase 2 — structural lemmas for MFAS

Working hypothesis: MFAS is polynomial.

- [ ] **Lemma candidate A.** If $T$ has a matching-FAS, then the
  *underlying* graph of the *unique* minimum FAS is a matching, and the
  minimum FAS is unique (up to permutation of independent arcs). If this
  is true, MFAS reduces to "is min FAS a matching?", which would be
  polynomially testable if min FAS itself is computable in
  poly-time *under the promise that it is a matching*.
- [ ] **Lemma candidate B.** Reformulate as a 2-SAT instance: variables
  $x_{uv} \in \{0,1\}$ encoding $u \prec v$; constraints (transitivity,
  $\beta(v) \le 1$ for each $v$) modeled as 2-SAT or as
  matroid-intersection. Watch out: transitivity is $n$-ary, not 2-ary;
  but ordering can be encoded by linear extensions of a partial order.
- [ ] **Lemma candidate C.** The matching-FAS, if it exists, is forced
  by local 3-vertex obstructions: cyclic triangles must each contribute
  exactly one back-arc, and these contributions must be vertex-disjoint
  across all triangles. This gives a constraint hypergraph; check if it
  is always 2-colorable / satisfiable in poly time.

If one of A/B/C produces a poly-time algorithm, run the algorithm
against the Phase 1 sweep to certify correctness on $n \le 8$.

### Phase 3 — NP-hardness reduction for MFAS (alternative)

If Phase 2 stalls:

- [ ] Try to reduce some known NP-hard problem (e.g., 3-SAT or matching-
  feedback-vertex-set) to MFAS, using the forest-FAS reduction in the
  source paper as a template. The source paper's gadgets force the FAS
  to be a forest; we need finer gadgets that force max-degree 1.

### Phase 4 — PFAS (path case)

PFAS asks the FAS to be a single path. Since paths are connected
linear forests, the path case is *more* restrictive than the linear-
forest case: $|F| \le n-1$, exactly $|F|-1$ vertices have back-degree 2
and exactly 2 have back-degree 1.

- [ ] First decide a relaxation: is there a FAS whose underlying graph is a
  **linear forest** (every component a path)? This bounds back-degree by 2
  and may admit a 2-SAT / matroid argument.
- [ ] Then add the connectivity constraint. The path case may turn out
  NP-hard while the linear-forest case is polynomial — that gap would
  itself be publishable.

## Deliverables

- **Lemma sheet** in `docs/lemmas.md` once any structural lemma is proved.
- **Algorithm** in `scripts/decide_mfas.py` once a candidate poly-time
  procedure exists, validated against the Phase 1 sweep.
- **Honest negative report** if no progress is made beyond instrumentation
  — that itself is the next-iteration starting point.

## What this attack will *not* attempt

- We do not attempt to resolve the related Problem 4.1 (triangle-free
  FAS) — it is in the same paper but is a separate question.
- We do not attempt to improve the source paper's NP-hardness for the
  *forest* case — that is already proved (Theorem 1.1).
