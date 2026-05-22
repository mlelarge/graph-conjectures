# Hardness route for the path half

This note records the current state of the attempt to adapt the
Aboulker-Aubian-Lopes forest-FAS reduction to Path-FAS / linear-forest
orderings (LFO).

## What carries over for free

AAL reduce from 3-SAT to forest-ordering. Their Section 3.2 proves:

> If the constructed tournament $T_{\mathcal I}$ has a forest-ordering,
> then the 3-SAT instance $\mathcal I$ is satisfiable.

Since every LFO is a forest-ordering, this implication already applies
to the path problem. Any path-hardness adaptation only has to rebuild
the other direction:

> If $\mathcal I$ is satisfiable, construct an ordering whose backedge
> graph is a linear forest.

## Direct reuse of the AAL construction fails

The failure is not subtle. AAL's Figure 1 tournament is used as a
rigid block $M_x$: it has a unique forest-ordering. In that unique
order, however, the backedge tree has degree 4.

The identity-order backedges of the AAL block are

$$
(3,0),(4,0),(5,0),(5,2),(6,1),(7,0),(7,1),
$$

with degree sequence $(4,2,1,1,1,2,1,2)$. Thus vertex 0 has degree 4.
Because the block has a unique forest-ordering, every forest-ordering
of the whole AAL tournament restricts to this induced backedge tree on
the block. Therefore the original AAL tournament has no LFO, regardless
of the SAT instance.

This is verified by
[`../scripts/path_rigid_block.py`](../scripts/path_rigid_block.py).

## Anchor-safe path rigidity is achievable

The first blocker is removable, but the initial 8-vertex replacement was
not strong enough. AAL's false state creates the extra backedge
$x\ell_x$. Therefore the distinguished anchor $\ell_x$ must have spare
degree in the forced path.

A random search over identity-order Hamiltonian-path backedge sets found
a 9-vertex tournament with a unique forest-ordering whose forced
backedge graph is a Hamiltonian path and whose leftmost anchor vertex
has degree 1.

The replacement tournament is:

```text
[0, 1, 1, 1, 1, 0, 1, 1, 1]
[0, 0, 1, 1, 0, 1, 1, 0, 1]
[0, 0, 0, 1, 1, 0, 1, 1, 0]
[0, 0, 0, 0, 1, 1, 0, 0, 1]
[0, 1, 0, 0, 0, 1, 1, 1, 0]
[1, 0, 1, 0, 0, 0, 1, 1, 1]
[0, 0, 0, 1, 0, 0, 0, 1, 1]
[0, 1, 0, 1, 0, 0, 0, 0, 1]
[0, 0, 1, 0, 1, 0, 0, 0, 0]
```

In the identity order, the backedges are

$$
(4,1),(5,0),(5,2),(6,3),(7,1),(7,3),(8,2),(8,4),
$$

whose underlying graph is the path

$$
0 - 5 - 2 - 8 - 4 - 1 - 7 - 3 - 6.
$$

Exhaustive enumeration over all $9!$ orders gives:

| property | count |
|---|---:|
| forest-orderings | 1 |
| linear-forest orderings | 1 |
| exact path backedge orderings | 1 |

The anchor vertex 0 has degree 1, so adding the false-state edge
$x\ell_x$ keeps its degree at most 2. This is the right rigid core for a
path-state replacement.

The certificate and search harness are in
[`../scripts/path_rigid_block.py`](../scripts/path_rigid_block.py).

## The remaining obstruction is the AAL star state

Replacing $M_x$ does not solve the reduction. In AAL's satisfying
assignment ordering:

- if $x$ is true, every vertex of $Y_x$ is adjacent to $x$ in the
  backedge graph;
- if $x$ is false, every vertex of $N_x$ is adjacent to $x$ in the
  backedge graph.

These are stars. Their centers have degree $|Y_x|$ or $|N_x|$, and
those sizes are at least 5 and 2, growing with occurrence count in the
variable gadgets. Forest-FAS tolerates this; LFO does not.

Therefore the next real construction problem is a **path-state block**:
replace the AAL local state gadget by a bounded-degree chain while
preserving the logic of the reduction.

A viable block must expose terminal pairs/5-tuples playing the roles of
$N_x$ and $Y_x$ while satisfying these constraints:

1. In any LFO, the block has exactly two possible states, corresponding
   to $x \prec \ell_x$ and $\ell_x \prec x$.
2. In either state, every internal vertex has backdegree at most 2.
3. Back-arc matchings to opposite literals still force the coherence
   contradictions used in AAL Lemma 3.3.
4. The clause arcs still force the all-false contradiction used in AAL
   Lemma 3.4.

## First two-state port block

The finite search has found a genuine two-state 7-vertex port block.
Use labels

$$
x=0,\quad \ell=1,\quad N=\{2,3\},\quad Y=\{4,5\},\quad q=6.
$$

The tournament matrix is:

```text
[0, 1, 0, 0, 0, 1, 0]
[0, 0, 1, 0, 1, 1, 0]
[1, 0, 0, 1, 0, 0, 1]
[1, 1, 0, 0, 0, 0, 0]
[1, 0, 1, 1, 0, 1, 0]
[0, 0, 1, 1, 0, 0, 1]
[1, 1, 0, 1, 1, 0, 0]
```

Exhaustive enumeration over all $7!$ orders gives exactly two LFO
orders:

| state | order | useful port signature |
|---|---|---|
| $R$ ($\ell\prec x$) | $q,\ell,y_1,y_2,n_1,n_2,x$ | $N=\{n_1,n_2\}$ are endpoints of one path component |
| $L$ ($x\prec\ell$) | $q,y_1,x,\ell,y_2,n_1,n_2$ | $Y=\{y_1,y_2\}$ are endpoints of one path component |

This is the first nontrivial evidence that a path replacement of the AAL
state machinery is feasible: the truth state can select one of two port
pairs as path endpoints without producing any extra LFO states.

It is still not the final gadget. In the $L$ state, the inactive
$N$-ports both already have degree 2. In the $R$ state, one inactive
$Y$-port has degree 2. If external back-arc matchings are forced to hit
inactive ports, this block has no spare degree there. A stronger block
must either:

1. leave inactive ports with spare degree, or
2. orient/order the external links so they are backedges only when both
   endpoints are in the active state, or
3. redesign the coherence/clause wiring so inactive ports are never hit.

A random search of 100000 seven-vertex tournaments with the stricter
"inactive ports also have spare degree" criterion found no example.
Further searches also failed to find this stronger object:

| search family | result |
|---|---|
| random $n=8$, 50000 samples | no strict inactive-spare block |
| random $n=9$, 20000 samples | no strict inactive-spare block |
| all one-auxiliary extensions of the recorded 7-block, 128 tournaments | no strict inactive-spare block; 20 exact two-state extensions, 2 active-port candidates |
| all two-auxiliary extensions of the recorded 7-block, 32768 tournaments | no strict inactive-spare block; 622 exact two-state extensions, 4 active-port candidates |

This is not an impossibility proof, but it changes the next target.
Naively padding the first 7-vertex block is not producing spare inactive
ports. The more plausible route is now **asymmetric external wiring**:
make external backedges appear only on active ports, or redesign the
coherence/clause wiring so inactive ports are never hit.

## Asymmetric external wiring also fails locally

I attacked the asymmetric-wiring target directly. Add one external
"clause" vertex $c$ to the 7-vertex two-state port block, with all 7
arcs $c \leftrightarrow \text{block}$ orientable freely. Then a valid
clause-style wiring would need:

- a combined LFO whose 7-block restriction is the $L$ state, in which
  $c$'s back-arcs land only on $Y$ ports;
- a combined LFO whose 7-block restriction is the $R$ state, in which
  $c$'s back-arcs land only on $N$ ports.

Because the bare 7-block has exactly two LFO orderings (the $L$ and
$R$ orderings), every combined LFO of the 8-vertex tournament is an
insertion of $c$ into one of these. So the search is finite:
$2^7 \cdot 8 = 1024$ combinations per state.

Results from
[`../scripts/external_wiring_search.py`](../scripts/external_wiring_search.py):

| criterion | count / 128 |
|---|---:|
| any L-state LFO | 20 |
| any R-state LFO | 32 |
| both states have an LFO | 8 |
| both clean (no inactive port hits) | 4 |
| L state has an active (Y) hit | 16 |
| R state has an active (N) hit | 24 |
| **strict: clean in both states AND active hits in both** | **0** |
| relaxed: active hits in both states (inactive hits to spare-degree vertices tolerated) | **1** |

The single relaxed candidate is the orientation
$(d_x, d_\ell, d_{n_1}, d_{n_2}, d_{y_1}, d_{y_2}, d_q) = (0,0,0,1,1,0,0)$,
i.e., $T$ contains the arcs $c \to n_2$, $c \to y_1$, and the rest are
$\text{block} \to c$. Its witnesses are:

- L state, insertion at position 6: $c$ has back-arc to $y_1$ (active),
  no inactive hits.
- R state, insertion at position 7: $c$ has back-arcs to $n_2$ (active)
  *and* to $y_1$. The $y_1$ hit is "inactive" semantically but is
  tolerated because $y_1$ is the isolated vertex of the R-state path
  decomposition (spare degree 2).

This is fragile. The wiring works *only* because the R state's
back-arc graph leaves $y_1$ isolated. For a hardness reduction, this
means the clause logic must accept "noise" hits on $Y$ ports while the
variable is in the false state, which conflicts with the AAL semantics
where $Y$ ports are forbidden in the false state.

## Two external vertices do not compose

I extended the search to two external vertices $c_1, c_2$ with the
$2^{15} = 32{,}768$ orientations of $c_i \leftrightarrow \text{block}$
arcs plus the $c_1 \leftrightarrow c_2$ arc. See
[`../scripts/external_wiring_two.py`](../scripts/external_wiring_two.py).

| criterion | count / 32768 |
|---|---:|
| any L-state LFO | 592 |
| any R-state LFO | 1408 |
| both states have an LFO | 94 |
| L active hit at some external | 78 (of 94) |
| R active hit at some external | 34 (of 94) |
| both states have *some* active hit | 26 |
| **both states have active hits at *both* externals** | **0** |

The "both" criterion is the right one for an AAL-style clause vertex
that touches multiple variables and contributes a back-arc at each. It
is empty across the entire 32k-orientation space.

The 26 "at least one active hit per state" candidates all have one
external playing the role of the single-vertex success above, while
the other external is a no-back-arc passive insertion (e.g.,
$c_1 = (0,0,0,0,0,0,0)$ means $c_1$ sits at the end of the order and
contributes no back-arc to any block vertex). That is not a real
compositional reduction; it is the single-vertex case dressed up.

## Status of the hardness route

The cumulative negative evidence is:

1. AAL Figure 1 rigid block has forced max-degree 4 → unusable.
2. 7-vertex two-state port block exists with the right L/R semantics,
   but has no spare degree at inactive ports.
3. Padding the 7-block by 1-2 auxiliaries does not gain spare degree.
4. Random search at $n \in \{8, 9\}$ does not find an "inactive-spare"
   variant.
5. Single-external asymmetric wiring with strict semantics: 0 cases;
   relaxed semantics: 1 case, fragile.
6. Two-external asymmetric wiring even with relaxed semantics that
   requires both externals to be active: 0 cases.

The AAL forest-FAS reduction does **not** straightforwardly adapt to
Path-FAS using the kind of local-gadget machinery explored here. To
make progress, one of the following is needed:

- a **larger** rigid two-state variable gadget where both inactive
  port sets retain spare degree (the search beyond $n = 9$ has not
  been done);
- a **different reduction template** entirely (e.g., not from 3-SAT,
  or with a non-AAL gadget skeleton);
- a **structural argument** that LFO is in P (e.g., via modular
  decomposition + bounded-treewidth dynamic programming on the
  remaining components), which would explain the empirical absence of
  hard local obstructions.

The empirical findings here are arguably more consistent with the
third option than with the first two: every "natural" hardness
construction we have tried bumps against the same degree-2 + acyclic
coupling, and we have not been able to engineer an adversarial gadget
that exploits this coupling. This is suggestive, not conclusive.

The scripts under this folder make further attempts cheap to run:
`external_wiring_search.py` and `external_wiring_two.py` give the
single- and double-vertex enumerations, and `path_state_signature.py`
gives a re-usable LFO signature engine for any candidate gadget.

The signature enumerator and search harness are in
[`../scripts/path_state_signature.py`](../scripts/path_state_signature.py).
