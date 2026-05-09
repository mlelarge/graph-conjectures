# Pebbling product: literature audit

Audit deliverable for Phase 0 of `PEBBLING_CARTESIAN_PRODUCT_COUNTEREXAMPLE_PLAN.md`.

Each claim below is sourced as one of the following:

- **Primary** — quoted directly from the cited paper.
- **Secondary (paraphrase)** — paraphrased by a later paper that we read,
  with the original paper named but not directly transcribed.
- **Repo data** — taken from a code artefact (e.g. an authors' GitHub
  repository) distributed alongside a peer-reviewed paper, used as ground
  truth for machine-readable graph data when the paper itself only shows
  figures.

The source kind is marked next to each claim. Repo data and secondary
paraphrases are working assumptions; promote them to primary as the audit
deepens. Bound kinds are controlled by the `known_bounds.csv` schema below.

## Conventions

- $\Box$ denotes the Cartesian product. Older papers write $G\times H$.
- $\pi(G)$ denotes the pebbling number; some sources write $p(G)$ or $f(G)$.
  This project uses $\pi$.
- A graph is **class 0** when $\pi(G)=|V(G)|$, the trivial lower bound.

## Original Lemke graph $L$

### Hurlbert primary description

From Glenn Hurlbert, *A Survey of Graph Pebbling*, arXiv:math/0406024 (text
extracted from the arXiv PDF; lines 322–326):

> Until recently, the only graph known not to have the 2-pebbling property
> was the Lemke graph $L$, whose vertex set is $\{a,b,c,d,w,x,y,z\}$ and
> whose edge set consists of the union of the complete bipartite graphs
> $\{a\}\times\{b,c,d\}$ and $\{b,c,d\}\times\{w,z\}$ with the path
> $w,x,y,z,a$.

Expanded edges:

- $\{a\}\times\{b,c,d\}$: `a-b, a-c, a-d`
- $\{b,c,d\}\times\{w,z\}$: `b-w, b-z, c-w, c-z, d-w, d-z`
- Path $w\,x\,y\,z\,a$: `w-x, x-y, y-z, z-a`

Total: 13 edges, 8 vertices. Degree sequence: $(5,4,4,3,3,3,2,2)$ where
$\deg(z)=5$, $\deg(a)=\deg(w)=4$, $\deg(b)=\deg(c)=\deg(d)=3$,
$\deg(x)=\deg(y)=2$.

### 2-pebbling failure witness (Hurlbert)

> let $D(a,b,c,d,w,x,y,z)=(8,1,1,1,0,0,0,1)$. It is impossible to move two
> pebbles to the root $x$.

Configuration size 12, support size 5. Threshold for 2-pebbling at root $x$
with $\pi(L)=8$ is $2\pi(L)-q(D)+1 = 16-5+1 = 12$, so this configuration is
exactly on the 2-pebbling threshold and witnesses the failure.

### Cross-check: Wood (KenanWood) bilevel-programming repo (repo data)

Source kind: **repo data** (not a primary-source transcription). The
edge list below is taken verbatim from `pebbling_number_bilevel.py`
distributed in
`https://github.com/KenanWood/Bilevel-Programming-for-Pebbling-Numbers`,
the code repository associated with Wood–Pulaj 2024 (arXiv:2411.19314,
"Bilevel Programming for Pebbling Numbers of Lemke Graph Products"). The
paper itself shows the original Lemke graph as a figure (Figure 1) but
does not transcribe its edges in text. Used here only to cross-check
against Hurlbert's textual edge list above.

Lemke Graph 0 (vertices labelled 1..8):

```
edges = [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,1),
         (3,6),(3,8),(4,7),(5,7),(5,8),(7,8)]
```

13 edges, degree sequence $(5,4,4,3,3,3,2,2)$ matching Hurlbert.

Explicit isomorphism Hurlbert $\to$ bilevel labels 1..8:

| Hurlbert | a | b | c | d | w | x | y | z |
|---|---|---|---|---|---|---|---|---|
| Bilevel  | 5 | 4 | 6 | 8 | 3 | 2 | 1 | 7 |

All 13 edges of the Hurlbert description appear in the bilevel edge list and
vice versa. The two descriptions are the same graph.

This project encodes $L$ on vertex set $\{0,1,\dots,7\}$ via the bilevel
labels minus 1.

## Other minimal 8-vertex Lemke graphs $L_1,L_2$ (repo data)

Source kind: **repo data**. From the same Wood bilevel-programming repo
(`pebbling_number_bilevel.py`). Naming convention: the repo's "Lemke
Graph 0" is the original Lemke graph above, called $L$ in this project.
The other two minimal graphs in the repo are renamed here for clarity:

- $L_1$ = repo "Lemke Graph 1":
  ```
  [(1,2),(1,6),(2,3),(2,6),(3,4),(3,7),(4,5),(4,7),
   (4,8),(5,6),(6,7),(6,8)]
  ```
  12 edges.

- $L_2$ = repo "Lemke Graph 2":
  ```
  [(1,2),(1,6),(2,3),(3,4),(3,5),(3,7),(4,5),(4,7),
   (4,8),(5,6),(5,8),(6,7),(6,8),(7,8)]
  ```
  14 edges.

The primary-source paper for the existence and minimality of these graphs
is Cusack, Green, Bekmetjev, Powers, *Graph Pebbling Algorithms and Lemke
Graphs*, Discrete Applied Mathematics 262 (2019), but its edge lists were
not transcribed for this audit. The repo edge lists are tied to the
bilevel paper's verified computation and are taken as ground truth here
**pending** a Cusack et al. transcription.

## Counting and minimality of 8-vertex Lemke graphs

Source kind: **secondary (paraphrase)**. Wood–Pulaj 2024 paraphrase a
result of Cusack–Green–Bekmetjev–Powers (Discrete Applied Mathematics
262, 2019); we have not transcribed the corresponding statement from
Cusack et al. directly. Wood–Pulaj 2024 (arXiv:2411.19314, lines
166–168) says:

> Let $\mathcal{L}$ be the set of all Lemke graphs on 8 vertices, up to
> isomorphism. Note that $|\mathcal{L}|=22$, and there are exactly three
> minimal Lemke graphs in $\mathcal{L}$ [5]; all 8-vertex Lemke graphs
> contain one of the three minimal ones.

Cite Cusack et al. for the result; do not cite Wood–Pulaj for the count
itself. The above is recorded as a working audit fact, not as an
in-house transcription.

## $\pi(L)$ for the three minimal Lemke graphs

Source kind: **secondary (paraphrase)**. Wood–Pulaj 2024 (line 635, with
paraphrased surrounding context) state that the three minimal 8-vertex
Lemke graphs are class 0 and that every 8-vertex Lemke graph has
pebbling number 8. We have not transcribed the corresponding statement
from Cusack–Green–Bekmetjev–Powers, which is the underlying primary
reference.

We have, however, **reproduced** $\pi(L)=\pi(L_1)=\pi(L_2)=8$ locally by
brute-force verification (`scripts/verify_pebbling_configuration.py`,
acceptance tests `tests/test_phase1_acceptance.py::test_pi_lemke_factor_is_8`).
That reproduction is in-house ground truth for these three graphs and
upgrades the audit status from "secondary" to "verified locally".

Status: `certified_upper_bound` with respect to the cited paper, and
locally reproduced for $L,L_1,L_2$.

## Graham's conjecture

Standard form (Graham, 1989, via Chung's hypercube paper):

$$\pi(G\Box H) \le \pi(G)\pi(H)\quad\text{for connected }G,H.$$

For the Lemke square the prediction is $\pi(L\Box L)\le 64$, and the trivial
lower bound is $|V(L\Box L)|=64$. So:

- if $\pi(L\Box L)=64$: Graham is tight on $L\Box L$ ($L\Box L$ is class 0);
- if $\pi(L\Box L)>64$: Graham fails.

Equivalently: Graham holds for $L\Box L$ iff $L\Box L$ is class 0.

## Bounds on $\pi(L\Box L)$

### `known_bounds.csv` schema

Records under `data/pebbling_product/known_bounds.csv` separate **kinds
of bound** from **value forms** so that heuristics never sit in the same
numeric column as certified theorems. Schema:

| Column | Meaning |
|---|---|
| `product` | graph or product name |
| `root_orbit` | root or root-orbit identifier (`all` if uniform) |
| `kind` | one of the controlled vocabulary below |
| `numeric_value` | integer when the bound is a single integer; empty otherwise |
| `text_value` | free text for non-numeric or qualified statements (e.g. ``~85``, ``pi_4(LxL) <= 64``) |
| `source` | citation |
| `certificate_path` | local or external path to a checkable certificate |
| `notes` | free text |

Allowed values for `kind`:

- `certified_upper_bound`: rationally checkable certificate or theorem;
- `trivial_lower_bound`: ``|V(G)|`` or other monotone lower bound;
- `support_restricted_certified`: certified bound that only holds when
  configurations are restricted (e.g. support-4 in Wood–Pulaj 2024);
  the qualifier lives in `text_value`;
- `heuristic_upper_value`: solver output or floating-point computation;
- `folklore_or_secondary`: useful clue, not a claim. Graham's predicted
  bound is recorded under this kind because it is a conjectural target,
  not a theorem.

No MILP or solver output is recorded as `certified_upper_bound` until a
separate rational checker verifies the certificate.

### Flocco–Pulaj–Yerger 2024

Title: *Automating weight function generation in graph pebbling*, Discrete
Applied Mathematics 347 (2024) 155–174. arXiv:2312.12618.

Theorem 4.2 (line 1410 of arXiv PDF):

> Let $L$ be the Lemke graph. Then $\pi(L\Box L,(r_1,r_2))\le 96$, for all
> $(r_1,r_2)\in L\Box L$.

Method: tree-strategy and symmetric-tree-strategy MILP, verified per-root,
hardest root is $(v_1,v_1)$ with 10 symmetric tree strategies (20 total
certificates).

LP relaxation lower bound on the certified value: 63.0 for each root
(footnote 5, line 1434). The MILP integer-feasible best for $r=(v_1,v_1)$ is
96 with a 33.8% gap to optimality.

Repo with certificates: `https://github.com/dominicflocco/Graph_Pebbling`.

Status: `certified_upper_bound`. Primary numeric bound to reproduce in
Phase 2b.

### Wood–Pulaj 2024 (support-restricted)

arXiv:2411.19314, Theorem 1 (line 175):

> For all $L',L''\in\mathcal{L}$, $\pi_4(L'\Box L'')\le \pi(L')\pi(L'')$.

Here $\pi_4$ is the support-4-restricted pebbling number: every distribution
of size $\pi_4$ with support of size $\le 4$ is solvable. The bound applies
to **all 22 8-vertex Lemke graphs** $L',L''$, not just the original $L$.

This is **not** a bound on $\pi(L\Box L)$. It is a bound on
$\pi_4(L\Box L)$. It does not certify Graham; it provides strong evidence
restricted to the support-4 regime.

Status: `support_restricted_certified` for $\pi_4$. Complementary, not a full
certified bound on $\pi(L\Box L)$.

### Kenter–Skipper–Wilson 2020 (heuristic)

Title: *Computing bounds on product graph pebbling numbers*, Theoretical
Computer Science 803 (2020), 160–177. arXiv:1905.08683.

Per Flocco et al. line 1422:

> [Our method] proved useful in improving the pebbling bounds on the Lemke
> square found in [Kenter–Skipper–Wilson].

Detailed numerical Kenter–Skipper–Wilson bounds for $L\Box L$ are reported
in the 2020 paper at heuristic / solver-output level. The "Kenter $\approx$
85" number sometimes circulated is `heuristic_upper_value` until verified
against a rational certificate. Not transcribed here; needs primary-paper
audit before use.

### Best post-2024 certified bound

After freshness check (arXiv pebbling search, May 2026):

- Flocco–Pulaj–Yerger 2024 ($\le 96$, certified, Theorem 4.2) is the most
  recent known certified upper bound on $\pi(L\Box L)$.
- Yang–Yerger–Zhou 2024/2025 (arXiv:2310.00580) introduce non-tree weight
  functions for $Q_4$ and lollipop graphs but explicitly leave the
  application to $L\Box L$ as an open question (line 941–942):
  > Can we use these new weight functions to improve the bound of the
  > pebbling number of $L\Box L$?
- Wood–Pulaj 2024 (arXiv:2411.19314) bounds $\pi_4(L\Box L)$, not
  $\pi(L\Box L)$.

So as of the audit date (2026-05-08), the best certified upper bound on
$\pi(L\Box L)$ remains 96.

## Other product results cited

### Gao–Yin 2017

*Lemke graphs and Graham's pebbling conjecture*, Discrete Mathematics
340(9), 2318–2332.

Verifies Graham for products of 8-vertex Lemke graphs with trees and with
complete graphs. Does **not** cover product of two 8-vertex Lemke graphs.

Status: `certified_upper_bound` (theorem, in cited paper). Restricts the
counterexample search frontier away from these factor families.

### Pleanmani 2020

*Graham's pebbling conjecture holds for the product of a graph and a
sufficiently large complete graph*, Theory and Applications of Graphs 7(1).

For any connected graph $G$, $\pi(G\Box K_n)\le \pi(G)\pi(K_n)$ for $n$
sufficiently large relative to parameters of $G$. Status as above.

### Xia–Pan–Xu–Cheng 2017

arXiv:1705.00191. Verifies Graham for Cartesian products of middle graphs
of certain even cycles. Tangential to the Lemke product attack.

## Computational complexity

Pebbling decision problems are hard:

- Single-configuration $r$-reachability: NP-hard (Milans–Clark 2006).
- Pebbling number decision: harder still, $\Pi_2^P$-complete in general.

Reference: Milans, Clark, *The complexity of graph pebbling*, SIAM Journal
on Discrete Mathematics 20(3) (2006), 769–798.

Implication: a single-configuration unsolvability check on $L\Box L$ (64
vertices, 64 pebbles) may exceed any practical resource budget. The
verifier must therefore expose `inconclusive_within_budget` as a
first-class outcome.

## Automorphism orbits of $L\Box L$

Wood–Pulaj 2024, line 516–518:

> Obtaining graph automorphism orbits from SageMath, for $L\Box L$, we
> obtain a reduction from checking 64 roots, down to 21 roots, partly
> because of the "slice" symmetry of product graphs.

So $L\Box L$ has 21 root orbits under $\mathrm{Aut}(L\Box L)$, including
the coordinate swap. Phase 3 root-orbit reduction in the plan should match
this number when computed locally.

## Source links

- Hurlbert survey: `https://arxiv.org/abs/math/0406024`
- Bilevel programming paper: `https://arxiv.org/abs/2411.19314`
  - Code: `https://github.com/KenanWood/Bilevel-Programming-for-Pebbling-Numbers`
- Flocco–Pulaj–Yerger: `https://arxiv.org/abs/2312.12618`
  (DAM 347 (2024) 155–174)
  - Code/certs: `https://github.com/dominicflocco/Graph_Pebbling`
- Kenter–Skipper–Wilson: `https://arxiv.org/abs/1905.08683`
- Hurlbert weight-function lemma: `https://arxiv.org/abs/1101.5641`
- Yang–Yerger–Zhou: `https://arxiv.org/abs/2310.00580`
- Cusack–Green–Bekmetjev–Powers (Lemke graph algorithms):
  `https://digitalcommons.hope.edu/cgi/viewcontent.cgi?article=2634&context=faculty_publications`
- Pleanmani 2020: `https://digitalcommons.georgiasouthern.edu/tag/vol7/iss1/1/`
- Xia–Pan–Xu–Cheng: `https://arxiv.org/abs/1705.00191`

## Phase-0 stop condition

Met:

- Edge lists for $L,L_1,L_2$ pinned (cross-checked between Hurlbert and the
  Wood bilevel repo for $L$).
- $\pi(L)=\pi(L_1)=\pi(L_2)=8$ reproduced locally in Phase 1 tests.
- 22 Lemke graphs on 8 vertices and three minimal ones recorded.
- Best certified $\pi(L\Box L)\le 96$ (Flocco–Pulaj–Yerger).
- 21 root orbits for $L\Box L$.
- `known_bounds.csv` written under `data/pebbling_product/`.
