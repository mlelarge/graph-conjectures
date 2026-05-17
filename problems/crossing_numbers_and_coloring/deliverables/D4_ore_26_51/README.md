# D4: 26-Ore graphs on 51 vertices

Week-1 Track A deliverable. Enumerates all 26-Ore graphs on exactly 51
vertices, up to isomorphism, with full canonical-form dedup.

## Result

There are **exactly 12** non-isomorphic 26-Ore graphs on 51 vertices, namely
the DHGO compositions $K_{26} * K_{26}$ parameterised by the partition size
$|A| \in \{1, 2, \dots, 12\}$.

Every one of them has $|V| = 51$, $|E| = 649$, $\delta = 25 = k-1$, and
$\omega(G) \ge 25$. They are all 26-critical by Kostochka-Yancey's
criticality-preservation theorem (KY arXiv:1209.1050, Theorem 1).

## Background and definition

Reference: A. Kostochka and M. Yancey, "Ore's Conjecture on color-critical
graphs is almost true", arXiv:1209.1050, *J. Combin. Theory Ser. B* 109 (2014),
73-101. Section 2 of that paper defines the class $\mathcal{O}_k$ of
**$k$-Ore graphs** and the **DHGO (Dirac-Haggkvist-Gallai-Ore) composition**
(sometimes just "Ore composition" in the literature).

**Definition (KY Section 2, DHGO composition).** Given $G_1, G_2 \in
\mathcal{O}_k$ with $|V(G_i)| = n_i$, pick:

1. an edge $xy \in E(G_1)$ whose endpoint $y$ has $\deg_{G_1}(y) = k - 1$
   (call $y$ the *low* vertex of $G_1$),
2. a vertex $z \in V(G_2)$ with $\deg_{G_2}(z) = k - 1$,
3. a partition $N_{G_2}(z) = A \sqcup B$ into two nonempty parts.

Build $G_1 * G_2$ by:

* deleting edge $xy$ from $G_1$,
* deleting vertex $z$ from $G_2$,
* identifying $x$ with all vertices of $A$ (i.e. adding edges from $x$ to each
  former neighbour of $z$ in $A$, with the elements of $A$ remaining as
  distinct vertices),
* identifying $y$ with all vertices of $B$ (similarly).

The result has $|V(G_1 * G_2)| = n_1 + n_2 - 1$ vertices.

**Important reading note.** The phrase "identify $x$ with the vertices in
$A$" in KY does **not** mean collapse $A$ into a single vertex. It means:
$x$ inherits $z$'s edges into $A$ (i.e., one new edge $xa$ for each $a \in A$),
while the elements of $A$ stay as distinct vertices of $G_1 * G_2$. This
matches the count $n_1 + n_2 - 1$ (only $z$ is removed, no vertex of $A$ or
$B$ is). The script `ore_compose.py` follows this reading and is canary-
checked against $K_4 * K_4$ (see below).

The class $\mathcal{O}_k$ is the smallest class of graphs that contains $K_k$
and is closed under DHGO composition. **KY Theorem 1** states that every
graph in $\mathcal{O}_k$ is $k$-critical (and conversely, $k$-Ore graphs are
characterised as the extremal cases of the KY edge bound — see Theorem 17 of
Kostochka's lecture notes).

## Parameter analysis for $K_{26} * K_{26}$

Take $G_1 = G_2 = K_{26}$. Then:

* every vertex of $K_{26}$ has degree exactly $25 = k - 1$, so choice (2) of
  $z$ is unique up to automorphisms of $K_{26}$;
* the edge $xy$ in (1): $K_{26}$ is edge-transitive, so the choice is unique
  up to relabelling;
* $K_{26}$ has $\mathrm{Aut}(K_{26}) = S_{26}$ acting on all vertices, so
  $N_{K_{26}}(z) = V(K_{26}) \setminus \{z\} = K_{25}$ as a graph, and the
  symmetric group $S_{25}$ acts on $N(z)$ — i.e. all 25 neighbours of $z$
  play interchangeable roles;
* therefore the partition $N_{K_{26}}(z) = A \sqcup B$ matters only through
  the *sizes* $(|A|, |B|)$, with $|A| + |B| = 25$ and both $\ge 1$.

Letting $|A| = a$, $|A| \in \{1, 2, \dots, 24\}$ a priori. The remaining
ambiguity is the symmetry $A \leftrightarrow B$, which corresponds to
swapping the roles of $x$ and $y$. Under this swap, $a \mapsto 25 - a$. Since
$25$ is odd there is no fixed point, so the 24 raw values $\{1, \dots, 24\}$
pair into 12 orbits

$$ \{1, 24\},\ \{2, 23\},\ \{3, 22\},\ \dots,\ \{12, 13\}. $$

So *a priori* there are at most 12 isomorphism classes. The enumeration
script then verifies by canonical-form dedup (pynauty's `certificate()`,
SHA-256 hashed) that all 12 are pairwise non-isomorphic; we confirm this is
indeed the case (Section "Per-graph table" below).

## Construction script

`ore_compose.py` self-contained, uses `networkx` for graph construction and
`pynauty` for canonical labelling. CLI:

```
python ore_compose.py --partition-size A     # 1 <= A <= 24
python ore_compose.py --all                   # default a-range 1..12
python ore_compose.py --all --a-range 1..24  # to see the (1,24), (2,23)... collapse
```

The script's `ore_compose_k26_k26(a)` function builds the graph on vertex
labels $\{0, 1, \dots, 50\}$ where:

* `0..25` = $V(G_1) = V(K_{26})$, with $x = 0$, $y = 1$;
* `26..50` = $V(G_2) \setminus \{z\} = K_{25}$ on those 25 labels;
* $A = \{26, \dots, 25 + a\}$, $B = \{26 + a, \dots, 50\}$;
* edges: $E(K_{26}) \setminus \{xy\}$ on $\{0,\dots,25\}$, plus $E(K_{25})$
  on $\{26,\dots,50\}$, plus $\{(0, a) : a \in A\}$, plus
  $\{(1, b) : b \in B\}$.

Per-vertex degree in the output (sanity-checked, see "Sanity checks" below):

* $\deg(x) = 24 + |A|$ (lost edge to $y$, gained $|A|$ to $A$);
* $\deg(y) = 24 + |B| = 24 + (25 - |A|) = 49 - |A|$;
* every other vertex has degree exactly $25 = k - 1$.

So $\delta(G) = 25$ always, and $\Delta(G) = \max(24 + a, 49 - a) =
\max(24 + a, 49 - a)$; for $a = 1$ this is $\max(25, 48) = 48$, for $a = 12$
it is $\max(36, 37) = 37$.

## Artifacts

* `ore_26_51.g6` — 12 lines, one graph6-encoded representative per
  isomorphism class, in order of increasing $|A|$ (so line $i$ corresponds
  to $|A| = i$);
* `ore_26_51.dimacs/ore_26_51_aXX.dimacs` for $XX \in \{01, \dots, 12\}$ —
  DIMACS edge-list files for direct solver consumption.

## Per-graph table

All 12 isomorphism classes:

| $|A|$ | $|B|$ | $|E|$ | $\delta$ | $\Delta$ | pynauty canon SHA-256 prefix |
|-------|-------|-------|----------|----------|------------------------------|
| 1     | 24    | 649   | 25       | 48       | `8df2459749c696c5`           |
| 2     | 23    | 649   | 25       | 47       | `c869017f377c057e`           |
| 3     | 22    | 649   | 25       | 46       | `7f3135cde8af5e2c`           |
| 4     | 21    | 649   | 25       | 45       | `3156607bcd52b43c`           |
| 5     | 20    | 649   | 25       | 44       | `32dba439bb341aee`           |
| 6     | 19    | 649   | 25       | 43       | `aeed502cdbd3f2cb`           |
| 7     | 18    | 649   | 25       | 42       | `38e00f6b110b3c3f`           |
| 8     | 17    | 649   | 25       | 41       | `3bbe3de8a697015a`           |
| 9     | 16    | 649   | 25       | 40       | `7b0a3397e587b55c`           |
| 10    | 15    | 649   | 25       | 39       | `8bdaf843e6572e23`           |
| 11    | 14    | 649   | 25       | 38       | `9a825fe8850576b3`           |
| 12    | 13    | 649   | 25       | 37       | `bd9f4ec156d8547e`           |

All 12 SHA-256 canonical certificates are pairwise distinct, certifying the
12 graphs are pairwise non-isomorphic. (The certificates are produced by
`pynauty.certificate()` which returns a canonical fingerprint of the
isomorphism class; SHA-256 of that gives a short readable handle. Pinned
versions: `pynauty == 2.8.8.1`, which wraps `nauty 2.8`.)

## Sanity checks performed

1. **Order and edge count.** Each of the 12 graphs has $|V| = 51$ and
   $|E| = 649$. The latter matches the **Kostochka-Yancey extremal bound**
   $F(n, k) = \lceil ((k+1)(k-2)n - k(k-3)) / (2(k-1)) \rceil$:
   $F(51, 26) = \lceil (27\cdot 24\cdot 51 - 26\cdot 23)/50 \rceil = 649$.
   So each of the 12 graphs is on the KY extremal bound, consistent with
   being $k$-Ore.

2. **Degree sequence.** Every vertex has degree $\ge 25 = k - 1$ (Dirac).
   The exact pattern matches the formula above ($\deg(x) = 24+a$,
   $\deg(y) = 49-a$, all others $25$).

3. **Clique structure.** For every $a$, both $\{0\} \cup \{2,\dots,25\}$ and
   $\{1\} \cup \{2,\dots,25\}$ induce $K_{25}$ (300 edges each), giving
   $\omega(G) \ge 25$ and hence $\chi(G) \ge 25$ trivially.

4. **Connectivity.** All 12 graphs are connected (`nx.is_connected`).

5. **Canonical-form dedup.** All 12 pynauty certificates are pairwise
   distinct. Cross-validated against `networkx.is_isomorphic` on the pairs
   $(a=1, a=24)$ — iso, and $(a=1, a=2)$ — non-iso; both agree with the
   pynauty cert.

6. **$A \leftrightarrow B$ symmetry.** $\mathrm{cert}(a) =
   \mathrm{cert}(25 - a)$ for each $a \in \{1,\dots,12\}$, verified
   directly (e.g. $a = 12$ vs. $a = 13$).

7. **Round-trip through `ore_26_51.g6`.** Reading the 12 graph6 lines back
   into networkx and re-computing certs yields the same 12-element set.

8. **Canary at $k = 4$: $K_4 * K_4$.** Both partition sizes $a \in \{1, 2\}$
   produce a 7-vertex, 11-edge graph that is **4-chromatic and 4-critical**
   (brute-forced: not 3-colorable; $G - v$ is 3-colorable for every $v$).
   This is the Moser spindle, the unique 4-Ore graph on 7 vertices.

9. **Canary at $k = 5$: $K_5 * K_5$.** Produces a 9-vertex, 19-edge graph
   for $a \in \{1, 2, 3\}$; canonical certs collapse $a = 1$ with $a = 3$
   (the $a \mapsto k - 1 - a$ symmetry), leaving 2 distinct classes, both
   verified 5-chromatic by brute force.

## On 26-criticality at $n = 51$

Direct verification of $\chi(G) = 26$ at $|V| = 51$ is infeasible by brute
force. We invoke **KY Theorem 1** (criticality preservation under DHGO
composition): if $G_1, G_2 \in \mathcal{O}_k$ then $G_1 * G_2 \in
\mathcal{O}_k$, and every graph in $\mathcal{O}_k$ is $k$-critical. Since
$K_{26} \in \mathcal{O}_{26}$ (base case), any output of $K_{26} * K_{26}$
via DHGO is in $\mathcal{O}_{26}$ and so is $26$-critical:
$\chi(G) \ge 26$ and $G - v$ is 25-colorable for every $v$. The canaries
at $k = 4, 5$ empirically confirm preservation; the $|E| = 649 = F(51, 26)$
extremal-edge identity is independent evidence that the outputs are
genuinely in $\mathcal{O}_{26}$. The senior memo
(`work/02_critical_graphs/memo.md`, Section 2.2) cites the same
KY-preservation argument as the operational basis for treating these
graphs as 26-critical.

## Caveats and reading notes

* **The "identify" wording in KY Section 2 is mildly ambiguous on first
  reading.** "Identify $x$ with the vertices in $A$" could be read as
  "collapse $A$ to a single vertex $x$", which would give the wrong vertex
  count $n_1 + n_2 - 1 - |A|$ instead of $n_1 + n_2 - 1$. We use the
  arithmetically-correct reading: each $a \in A$ becomes a *new neighbour*
  of $x$, and $A$'s vertices stay distinct in the output. This is the
  reading endorsed by Section 1.4 of Kostochka's 2016 lecture notes ("DHGO
  composition adds $k - 1$ vertices per step from $K_k$, so $|V| \in
  \{k, 2k - 1, 3k - 2, \dots\}$ in the orbit of $K_k$"); for $k = 26$ this
  gives $|V| = 26, 51, 76, \dots$, matching our $n = 51$ for one
  composition step.

* **Role 5's memo claimed "essentially unique up to automorphism"** for the
  $25$-Ore graph on 48 vertices (`work/02_critical_graphs/memo.md`, Section
  2.2 (c)). That claim is *informal* in the memo and not formally
  asserted as a theorem. Our enumeration here for $k = 26, n = 51$ shows
  **12** distinct isomorphism classes, not one. The same arithmetic applies
  at $k = 25, n = 48$: the partition $|A| \sqcup |B|$ of the 24 neighbours
  of $z$ in $K_{25}$ gives $|A| \in \{1, \dots, 11\}$ distinct classes
  under the symmetry $|A| \mapsto 24 - |A|$ (which has fixed point
  $|A| = 12$, so the count is 12 classes total: 11 paired plus 1 fixed).
  This suggests the senior memo at Section 2.2 (c) is mildly underestimating
  the count, which the team should note before treating "the $25$-Ore
  graph on 48 vertices" as a singleton. (Not in scope for D4 to fix; flagged
  here for follow-up.)

* **`pynauty` installed cleanly via `uv pip install pynauty`** (pynauty
  bundles nauty internals; no system `nauty` needed). The fallback path in
  `canonical_certificate` uses a non-canonical edge-list SHA-256 and prints
  a stderr warning — never triggered here. No system-dependency gaps.

## Reproducing

```
uv venv .venv --python 3.12 && uv pip install networkx pynauty
.venv/bin/python ore_compose.py --all > ore_26_51.g6
```

DIMACS regeneration is a 6-line snippet calling `to_dimacs` on each `a` in
`range(1, 13)`; see `ore_compose.py`'s `to_dimacs()` function.
