# Literature notes: directed path of length twice the minimum outdegree

Working problem: every oriented graph with minimum outdegree $k$ contains a
directed simple path of length $2k$.

These notes distinguish three levels of confidence:

- **located:** the source exists and the relevant section was found;
- **transcribed:** the exact statement was copied verbatim into these notes;
- **usable:** the statement has been checked enough to act as a filter, lemma,
  or test oracle.

## Source status

| Source | Status | Notes |
|---|---|---|
| OPG local scrape, node 46359 | located | Slug says `directed_cycle...`; title and statement say directed path. |
| Cheng--Keevash, arXiv:2402.16776v4 (21 Aug 2024) | transcribed and usable | Full PDF read; all numbered statements copied below. |
| Cheng--Keevash, SIDMA 38(4), 3134-3139 | located | Journal version; constants match arXiv v4. |
| Bai--Manoussakis, SIDMA 33(4):2444-2451, 2019 (arXiv:1805.02999) | located | Disproves Thomasse for every even $g\geq4$; their construction is generalised in Cheng--Keevash Prop 2. |
| Jackson, J. Graph Theory 5(2):145-157, 1981 | transcribed via secondary | Min-semidegree result; see below. |
| Sullivan, arXiv:math/0605646, 2006 | located | Caccetta-Haggkvist survey. |
| OPG live page | unreachable | Local scrape used. |
| MathSciNet/Zentralblatt | not checked | Not strictly needed any more. |

Source URLs:

- OPG canonical URL:
  `http://www.openproblemgarden.org/op/directed_cycle_of_length_twice_the_minimum_outdegree`
- arXiv record: `https://arxiv.org/abs/2402.16776`
- journal PDF copy: `https://people.maths.ox.ac.uk/keevash/papers/LongDirectedPathJournal.pdf`
- DOI landing page: `https://doi.org/10.1137/24M1648375`
- Bai--Manoussakis arXiv: `https://arxiv.org/abs/1805.02999`
- Sullivan survey: `https://arxiv.org/abs/math/0605646`

## OPG statement

OPG local scrape:

- title: `Directed path of length twice the minimum outdegree`
- statement: every oriented graph with minimum outdegree $k$ contains a
  directed path of length $2k$.
- conclusion: this is the path conjecture; the slug name is misleading.

## Cheng--Keevash 2024: verbatim statements

### Conjecture 1 (Thomasse, oriented graph version)

> Any oriented graph with minimum out-degree $\delta$ contains a directed path of length $2\delta$.

This is the target problem.

### Stronger Thomasse girth conjecture (refuted for $g\geq 4$)

The paper attributes to Thomasse the strengthening: any digraph with minimum
out-degree $\delta$ and girth $g$ contains a directed path of length
$\delta(g-1)$. Bai--Manoussakis 2019 disproves this for every even $g\geq 4$;
Cheng--Keevash Proposition 2 extends the disproof to every $g\geq 4$.

### Proposition 2 (counterexample family for the girth strengthening)

> For every $g \geq 2$ and $\delta \geq 1$ there exists a digraph $D$ with girth $g$ and $\delta^+(D) \geq \delta$ such that any directed path has length at most $\frac{g\delta+g-2}{2}$ if $g$ is even or $\frac{(g+1)\delta+g-3}{2}$ if $g$ is odd.

The construction is $D_{a,b}$ defined in Section 2 of the paper.

#### Construction of $D_{a,b}$

- Start from $\overrightarrow{K}_{\delta+1}$, the complete directed graph on
  $\delta+1$ vertices.
- The $k$-lift on a vertex $v$: delete all arcs with tail $v$, add $k-1$
  disjoint sets of $\delta$ new vertices $U_{v,1},\ldots,U_{v,k-1}$, write
  $U_{v,0}:=\{v\}$ and $U_{v,k}:=N^+(v)$, and add all arcs from $U_{v,i-1}$
  to $U_{v,i}$ for $1\leq i\leq k$. A 1-lift does nothing. Every lift
  preserves the property that all out-degrees are $\delta$.
- $D_{a,b} := \overrightarrow{K}_{\delta+1}^{\uparrow}(a,b,\ldots,b)$:
  $a$-lift one vertex $v_1$ and $b$-lift each other vertex.

#### Claim 6 (verbatim)

> The girth of $D_{a,b}$ is $a+b$ and the longest path has length $\delta b + a - 1$.

Choices for Proposition 2: $a=b=g/2$ for even $g$, $a=(g-1)/2$ and $b=(g+1)/2$
for odd $g$.

#### Important corollary for this project

None of these $D_{a,b}$ refutes Conjecture 1. Their longest path is always
$\geq 2\delta$ for $g\geq 3$:

| $g$ | $a,b$ | longest path |
|---|---|---|
| 3 | 1,2 | $2\delta$ (tight) |
| 4 | 2,2 | $2\delta+1$ |
| 5 | 2,3 | $3\delta+1$ |
| 6 | 3,3 | $3\delta+2$ |

So the $D_{a,b}$ family is a useful seed for the verifier (it ought to report
$L\geq 2\delta$ on every such graph) but it cannot itself be the
counterexample we are looking for. $D_{1,2}$ at $g=3$ is the most informative
seed: it sits exactly at $L=2\delta$.

### Theorem 3 (general girth lower bound)

> Every digraph $D$ with girth $g$ and $\delta^+(D) \geq \delta$ contains a directed path of length $2\delta(1-\frac{1}{g})$.

(The proof actually gives $\geq 2\delta(1-1/g) + 1$.)

### Theorem 4 (oriented and girth-4 lower bounds)

> Every oriented graph $D$ with $\delta^+(D) \geq \delta$ contains a directed path of length $1.5\delta$. Every digraph $D$ with $\delta^+(D) \geq \delta$ and girth $g \geq 4$ contains a directed path of length $1.6535\delta$.

The $1.5$ for oriented graphs comes from $\delta^+(S)\leq\frac{|S|-1}{2}\leq
\frac{\delta-1}{2}$ in oriented $S$, plugged into Lemma 7. The $1.6535$ for
girth $\geq 4$ comes from $\delta^+(S)<0.3465\delta$ via the
Hladky--Kral--Norin bound on Caccetta-Haggkvist for triangles
(Theorem 9 below).

### Theorem 5 (almost-regular lower bound)

> For every $C > 0$ there exists $c > 0$ such that if $D$ is a $(C,d)$-regular digraph with girth $g$ then $D$ contains a directed path of length at least $cdg/\log d$.

Here $(C,d)$-regular means $d^+(v)\geq d$ and $d^-(v)\leq Cd$.

### Lemma 7 (the key lemma, verbatim)

> If $D$ is an oriented graph with $\delta^+(D) \geq \delta$ then $D$ either contains a directed path of length $2\delta$ or an induced subgraph $S$ such that $|S| \leq \delta$ and $\delta^+(S) \geq 2\delta - \ell(D)$.

**Resolved: there is no usable $+1$ strengthening.** The published proof
closes with `\ell(D) = |P| \geq 2\delta+1-\delta^+(S)`, but in the geometric
step $|P|$ silently denotes $|V(P)| = \ell(D)+1$, not the arc count. Reverting
to arc count gives back exactly the headline bound $\delta^+(S) \geq 2\delta -
\ell(D)$. Use the lemma exactly as stated.

### Theorem 8 (Chvatal--Szemeredi 1983, used as black box)

> Every digraph $D$ with order $n$ and $\delta^+(D) \geq \delta$ contains a directed cycle of length at most $\lceil \frac{2n}{\delta+1} \rceil$.

### Theorem 9 (Hladky--Kral--Norin 2017, used as black box)

> Every oriented graph with order $n$ and minimum out-degree $0.3465 n$ contains a directed triangle.

### Conjecture 16 (Cheng--Keevash's own weaker form)

> There is some $c > 0$ such that $\ell(D) \geq c \cdot g(D) \cdot \delta^+(D)$ for any digraph $D$.

By Proposition 2, $c \leq 1/2$.

## Implication for this project: $\delta\leq 3$ is already closed

Apply Lemma 7. For a counterexample, $\ell(D)\leq 2\delta-1$, so the lemma
forces $\delta^+(S)\geq 2\delta-(2\delta-1) = 1$.

Combine with the oriented-graph average bound
$\delta^+(S)\leq \lfloor(|S|-1)/2\rfloor \leq \lfloor(\delta-1)/2\rfloor$.

| $\delta$ | $\lfloor(\delta-1)/2\rfloor$ | required $\delta^+(S)\geq 1$ | counterexample possible? |
|---:|---:|:---:|---|
| 2 | 0 | impossible | NO. **$\delta=2$ closed.** |
| 3 | 1 | tight | yes by Lemma 7 alone, but ruled out by cyclic-closure (this project). **$\delta=3$ closed.** |
| 4 | 1 | tight | yes. Open. |
| 5 | 2 | yes | open. |

For $\delta=2$: any $S$ with $|S|\leq 2$ is either empty, a single vertex
(outdegree $0$ in $S$), or two vertices with at most $1$ arc (one of them
has outdegree $0$ in $S$). In every case $\delta^+(S)=0$, contradicting
$\delta^+(S)\geq 1$. Hence $\ell(D)\geq 2\delta=4$ and Conjecture 1 holds for
$\delta=2$.

**Conclusion: the $\delta=2$ case of Conjecture 1 is a theorem already.**

The $\delta=3$ case is also closed (this project), via Lemma 7 plus the
oriented average bound plus an antiparallel cyclic-closure argument; see
`k3_hand_proof.md`.

The $\delta = 4, n = 10$ case is also closed (this project), via hand
proofs for score sequences $(1,1,1,1)$, $(2,1,1,1)$, $(3,1,1,1)$ plus
a computer-aided closure for $(2,2,1,1)$; see
`k4_n10_proof.md`.

The $\delta = 4, n = 11$ case is closed (this project,
computer-aided): `k4_n11_proof.md`. The
score-profile-aware miner (`scripts/k4_score_profile_miner.py`)
covers all four score sequences at $n = 11$:

- $(1,1,1,1)$: 0 valid $(S, T)$ configurations (no $\sigma$-invariant
  4-subset of the 7-cycle). Structurally impossible at any $n$.
- $(2,1,1,1)$: 4 configurations × 1.6M completions = 6.4M.
- $(2,2,1,1)$: 24 configurations, 91.6M completions.
- $(3,1,1,1)$: 4 configurations × 5M completions = 20M.

Total: 32 configurations, 117,992,940 completions, 0 obstructions.

(Audit-trail note: an earlier version of this entry mistakenly
claimed the closure followed from `scripts/k4_general_miner.py`,
which only covered $(2,2,1,1)$. The fix was to add a
score-profile-aware miner that handles all four cases.)

**The first genuinely open case is therefore $\delta = 4, n \geq 12$.**

For $\delta\geq 5$, Theorem 4 gives only
$\ell(D)\geq\lceil(3\delta+1)/2\rceil\leq 2\delta-2$. The gap from
proof-bound to conjecture grows.

## Jackson 1981: stronger hypothesis settles the conjecture

Jackson, "Long paths and cycles in oriented graphs", J. Graph Theory 5(2),
145--157 (1981).

Statement (transcribed via secondary source; should be confirmed against the
journal article when convenient):

> Every oriented graph $D$ with $\delta^0(D) \geq k$ contains a directed Hamilton cycle when $|V(D)| \leq 2k+2$, and a directed path of length $2k$ when $|V(D)| > 2k+2$.

Here $\delta^0(D) := \min(\delta^+(D), \delta^-(D))$ is the minimum semidegree.

### Implication for this project (key)

Jackson's hypothesis is strictly stronger than ours: he assumes $\delta^- \geq
k$ as well as $\delta^+ \geq k$. Conjecture 1 only assumes $\delta^+ \geq k$.
A counterexample to Conjecture 1 must therefore violate Jackson's hypothesis,
i.e. have at least one vertex with $d^-(v) < k$.

In the $n=2k+2$ first-excess regime:

- a counterexample with $\delta^+\geq k$ at $n=2k+2$ contains a vertex $v_*$
  with $d^-(v_*)\leq k-1$;
- after the $k$-outregular reduction, $\sum_v d^-(v) = (2k+2)k$ so
  $\bar d^- = k$; some vertex has $d^-\geq k+1$;
- in an oriented graph on $n=2k+2$, $d^+(v)+d^-(v)+m(v)=2k+1$ with $m(v)$ the
  non-neighbour count. With $d^+(v)=k$ this gives $d^-(v)+m(v)=k+1$;
- so $d^-(v_*)\leq k-1$ iff $m(v_*)\geq 2$. The indegree-deficient vertex has
  at least two non-neighbours;
- total non-edges $=k+1$, so $v_*$ alone uses $\geq 2$ of the $k+1$ non-edges.

This is a concrete structural lever for the hand attack and a SAT branching
heuristic.

## Candidate extension lemmas

Let $P=v_0v_1\cdots v_L$ be a longest directed simple path in an oriented
graph $D$.

### Lemma A: endpoint closure

Every out-neighbour of $v_L$ lies on $P$. Symmetrically (in the reverse
digraph), every in-neighbour of $v_0$ lies on $P$.

Clause form for a chosen path $P$:

- for each $x\notin V(P)$, forbid $v_L\to x$;
- for each $x\notin V(P)$, forbid $x\to v_0$.

### Lemma B: insertion blocker (chord lemma)

For every $x\notin V(P)$ and every $1\leq i\leq L$, it is impossible to have
both $v_{i-1}\to x$ and $x\to v_i$, because then
$v_0\cdots v_{i-1} x v_i \cdots v_L$ is a longer directed simple path.

Clause form: $\neg a_{v_{i-1},x}\vee \neg a_{x,v_i}$.

### Lemma C: directed rotation

If $v_L\to v_i$ and $v_{i-1}\to v_L$ for some $1\leq i\leq L-1$, then
$v_0v_1\cdots v_{i-1}v_Lv_i\cdots v_{L-1}$ is a directed simple path of length
$L$ ending at $v_{L-1}$. Apply Lemma A to this rotated path to derive new
forbidden arcs from $v_{L-1}$. This is conditional, not an unconditional
clause.

### Lemma D: endpoint cycle bound (used inside Cheng--Keevash Lemma 7)

Let $I=\{i : v_L\to v_i\}$. Then $|I|\geq k$ (Lemma A plus
$\delta^+\geq k$), and if $a=\min I$ then $v_av_{a+1}\cdots v_Lv_a$ is a
directed cycle of length $L-a+1\geq k+1$ (since $\min I\leq L-k$).

This is exactly the "cycle bound" Cheng--Keevash use in the proof of
Lemma 7 (Section 4 of arXiv:2402.16776).

### Lemma E (derived from Cheng--Keevash Lemma 7 + oriented bound)

If $D$ is an oriented graph with $\delta^+(D)\geq\delta$ and $\ell(D)<2\delta$,
then there exists an induced subgraph $S$ on at most $\delta$ vertices with
$\delta^+(S)\geq 2\delta-\ell(D)$, and additionally
$\delta^+(S)\leq\lfloor(|S|-1)/2\rfloor$. Combined this rules out $\delta=2$,
and forces $S$ to look like a directed triangle (or larger oriented graph
with $\delta^+(S)=1$) for $\delta\in\{3,4\}$.

## First-excess hand attack: $n = 2k + 2$

This is the first possible order after the regular-tournament equality case.
Assume a counterexample $D$ exists with $n=2k+2$ and $k\geq 3$ (the $k=2$
case is closed).

### Reductions

- **$k$-outregular reduction.** Deleting arcs cannot create a new directed
  path. Choose exactly $k$ outgoing arcs from each vertex, obtaining a
  spanning subdigraph $D'$ with $d^+_{D'}(v)=k$ everywhere and still no path
  of length $2k$.
- **Strong connectivity.** A sink SCC of order $\geq 2k+1$ is forced; order
  $2k+1$ would be a regular tournament, hence Hamiltonian, contradiction. So
  the sink SCC at this size is the whole graph.
- **Almost-tournament structure.** $|A(D')|=(2k+2)k$ while
  $\binom{2k+2}{2}=(2k+2)k+(k+1)$, so the underlying simple graph is
  $K_{2k+2}$ with exactly $k+1$ missing unordered pairs. Total non-neighbour
  count $\sum_v m(v)=2(k+1)$, average $1$ per vertex.
- **Indegree-deficient vertex** (Jackson 1981). $D'$ contains a vertex $v_*$
  with $d^-(v_*)\leq k-1$, equivalently with $m(v_*)\geq 2$ non-neighbours.
  This $v_*$ alone uses $\geq 2$ of the $k+1$ non-edges.
- **Cheng--Keevash dense witness $S$** (Lemma E). Since $\ell(D)\leq 2k-1$,
  there is an induced subgraph $S$, $|S|\leq k$, with $\delta^+(S)\geq 1$. So
  $S$ contains a directed cycle (every vertex has an out-neighbour in $S$).

### Hand-proof route for $k=3$ (DONE; see `k3_hand_proof.md`)

The hand attack closed $k=3$ at every $n \geq 7$, not just $n=8$. The key
step was to use Cheng--Keevash's specific Lemma 7 construction
$S = B^- = \mathrm{pred}_C(B)$ together with an antiparallel cyclic-closure
argument on the endpoint cycle. Jackson 1981's indegree-deficient vertex
was *not* needed for $k=3$.

The $k=4, n=10$ case is closed; see `k4_n10_proof.md`.
The $k=4, n=11$ case is closed (computer-aided); see
`k4_n11_proof.md`. The next genuinely open target is
$k=4, n \geq 12$.

## Random sampler choice

Do not use an unspecified "near-regular random graph" phrase.

Primary sampler for $n=2k+2$:

1. seed with $D_{1,2}$ at the relevant $\delta$ (which is $k$-outregular,
   girth $3$, longest path exactly $2k$);
2. apply a switch chain preserving $d^+(v)=k$ for every vertex: replace arcs
   $u\to a$ and $w\to b$ by $u\to b$ and $w\to a$ when this creates no loop,
   duplicate arc, or antiparallel pair;
3. record burn-in and thinning; do not claim the chain is uniform unless
   separately justified; on $k$-outregular oriented graphs irreducibility is
   non-trivial.

Secondary sampler:

- tournament rejection sampling with $\delta^+\geq k$, clearly labelled
  high-density and not near-minimal.

The baseline table must record the sampler name, seed, burn-in, thinning, and
acceptance rate.

## Canonical blocking commitment

SAT must not be allowed to churn on relabelled copies.

For $k\leq 4$ exact runs:

- compute a canonical label for every rejected model;
- preferred tool: pynauty (one `uv pip install pynauty`);
- when rejecting a model, add clauses excluding its residual orbit, not just
  the single labelled assignment.

For larger runs:

- canonical memoization remains mandatory;
- if full orbit blocking is too expensive, record the skipped orbit size and
  treat the result as heuristic rather than exact.

## Computational stop rules

The $\delta=2$ case is closed by Cheng-Keevash. The $\delta=3$ case is
closed by this project's hand proof (`k3_hand_proof.md`),
modulo the cross-read caveat. The $\delta=4, n=10$ case is closed by
this project (`k4_n10_proof.md`). The $\delta=4, n=11$
case is closed (computer-aided) by this project
(`k4_n11_proof.md`). **Do not run SAT for $k\leq 3$, or
for $k=4, n \in \{10, 11\}$.**

The first genuinely open SAT case for $k=4$ is $n \geq 12$:

- exact search must cover $12 \leq n \leq 13$;
- $14 \leq n \leq 15$ are stretch exact targets with explicit
  wall-clock caps;
- no statement beyond $n \leq 15$ may be described as computationally
  checked for $k=4$.

If no counterexample appears through $n=15$, switch effort to a hand
or miner-extended proof for $k=4$ rather than continuing open-ended
enumeration. Note: the local miner closes $n=10$ via a deterministic
forcing chain that exploits $|V(D)\setminus V(P)| = 2$; at $n=11$ that
chain is weaker but the (much larger) brute-force enumeration still
terminates in 10 minutes. At $n \geq 12$ enumeration costs grow and
SAT may become the right tool.

## Remaining checks (lower priority)

- Bai--Manoussakis arXiv 1805.02999: read the original even-$g$ construction
  to confirm the lift recipe matches Cheng--Keevash Section 2.
- Sullivan survey arXiv math/0605646: search for any pre-2024 partial result
  on $\delta=3$ specifically.
- Jackson 1981 journal article: confirm the exact bound $|V(D)|\leq 2k+2$ for
  the Hamilton cycle conclusion against the published version.
- Papers citing Cheng--Keevash since publication: a Google Scholar /
  Semantic Scholar search may surface a small-$\delta$ improvement we have
  missed.
