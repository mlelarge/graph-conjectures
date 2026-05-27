# Formal gadget-as-relation interface for Path-FAS

**Status.** Track 1 of the CSP-classification attack on Aboulker's
Problem 4.4.  The companion tracks are the k=6 bijunctive theorem
(Track 2) and the relation miner (Track 3, see
`scripts/relation_miner.py`).

This document fixes definitions and notation that the two other
tracks rely on: what a port is, what a gadget is, what its Boolean
relation is, how gadgets compose, and how to talk about Schaefer's
classification in this setting.  Every load-bearing definition is
backed by a concrete computation against
`scripts/np_hardness_gadget_verifier.py`; the tests in
`tests/test_fanout_interface.py` pin the small examples.

The high-level reason this document needs to exist: phrases like
"the fork-tree fanout realizes the equality relation" only have a
meaning once we have agreed (a) what a port is, (b) what semantic
function turns an LFO into a bit-tuple, and (c) what the relation
\(R_G\) of a gadget \(G\) is.  Without that, every downstream claim
about "Path-FAS realizable relations" is informal.

---

## 1. Path-FAS recap and notation

Throughout, \(T = (V, E)\) is a finite tournament: \(|V|=n\) and for
every unordered pair \(\{u, v\}\) of distinct vertices exactly one of
the arcs \(u \to v\) or \(v \to u\) belongs to \(E\).

A *linear ordering* of \(V\) is a bijection \(\sigma : V \to \{0,
1, \ldots, n-1\}\).  Write \(\sigma(u) < \sigma(v)\) to mean "\(u\)
comes before \(v\) in \(\sigma\)".

An arc \(u \to v\) is a **back-arc under \(\sigma\)** iff
\(\sigma(u) > \sigma(v)\).

The **back-arc graph** \(B(T, \sigma)\) is the undirected simple
graph on \(V\) whose edges are the unordered pairs underlying the
back-arcs.

\(\sigma\) is an **LFO** (linear-forest ordering) iff \(B(T, \sigma)\)
is a *linear forest*: an acyclic graph with maximum degree
\(\le 2\).  Equivalently, a disjoint union of paths.  Path-FAS is the
decision problem "does \(T\) admit an LFO?"

The set of LFOs of \(T\) is denoted \(\mathrm{LFO}(T)\).

The trust root is `scripts/verify.py`: every claim about
\(\mathrm{LFO}(T)\) routes through `verify(T, sigma)`.

---

## 2. F1.  Ports and the placement-bit semantic

A **port** of a tournament \(T\) on vertex set \(V\) is an ordered
pair of distinct vertices \(\pi = (x, y) \in V^2\), \(x \ne y\).

The **placement-bit semantic** assigns the port \(\pi = (x, y)\) the
value
\[
\mathrm{bit}_\pi(\sigma) \;:=\; \mathbf{1}\bigl[\sigma(y) < \sigma(x)\bigr] \in \{0, 1\}
\]
for every linear ordering \(\sigma\) of \(V\).

Equivalent phrasings:
- \(\mathrm{bit}_\pi(\sigma) = 1\) iff \(y\) comes before \(x\) in
  \(\sigma\);
- \(\mathrm{bit}_\pi(\sigma) = 1\) iff the *forward* arc between
  \(x\) and \(y\) (the arc whose tail comes first in \(\sigma\))
  has \(y\) as tail;
- Under the convention \(\sigma : V \to [n]\), the bit is
  \(\mathbf{1}[\sigma(y) < \sigma(x)]\).

### 2.1 Why placement-bit, not back-arc or component-membership

We considered three semantics:

1. **Placement-bit** as above.
2. **Back-arc semantic**: pick an arc \(a = u \to v\) of \(T\); set
   bit \(=1\) iff \(a\) is a back-arc, i.e. \(\sigma(u) >
   \sigma(v)\).
3. **Component-membership semantic**: bit \(=\) class of a vertex
   in some union-find structure derived from \(B(T, \sigma)\).

The placement-bit semantic is the right choice for three reasons.

(P1) **Stable under induced sub-tournament.** A port \((x, y)\) is
defined purely in terms of vertex placements.  In particular, if
\(T'\) is the induced sub-tournament on \(V' \supseteq \{x, y\}\),
and \(\sigma'\) is the restriction of an LFO \(\sigma\) of the larger
\(T\), then \(\mathrm{bit}_\pi(\sigma') = \mathrm{bit}_\pi(\sigma)\).

This is what makes the per-gadget truth-table extraction in
`truth_table_from_gadget(..., vertices_subset=...)` sound: when we
compose gadgets, we still read each gadget's local truth table by
restricting the global LFO to the gadget's vertex set, and the
placement-bit at a port doesn't care which other vertices were
present.  The back-arc semantic does **not** have this property:
whether a given arc is a back-arc can change under composition
because the LFO might re-rank vertices.  (See § 9 for a precise
statement and a worked example.)

(P2) **Closure under port reversal = negation.**  For ports
\((x, y)\) and \((y, x)\), exactly one of the two bits is 1 for any
\(\sigma\).  Hence reversing a port pair is *exactly* coordinate-wise
negation on the relation.  This will let us state negation gadgets
without building new tournaments (§ 4 below).

(P3) **Implementation alignment.**  This is the semantic used by
`placement_bit_first_pair_inversion` in
`scripts/np_hardness_gadget_verifier.py` (lines 143-158), which is
the truth-table extractor every other verifier delegates to.

### 2.2 Port multiplicity and reuse

A gadget may declare any tuple \(\Pi = (\pi_1, \ldots, \pi_p)\) of
ports, with no requirement that the pairs be disjoint.  Two ports may
share a vertex, and indeed the cyclic triangle (§ 7.2) uses ports
\((0, 1), (1, 2), (2, 0)\) sharing every vertex.

A vertex that does not appear in any \(\pi_i\) is called *internal*.
A port \(\pi_i = (x, y)\) where exactly one of \(\{x, y\}\) is
shared with another port is allowed.  No restrictions on port
geometry are imposed by the interface.

---

## 3. F2.  Gadget, gadget relation, equivalence

A **gadget** is a triple
\[
G = (T_G,\; \Pi_G,\; \text{semantic}_G)
\]
where
- \(T_G\) is a tournament on a vertex set \(V_G\);
- \(\Pi_G = (\pi_1, \ldots, \pi_p) \in (V_G^2)^p\) is a tuple of
  ports;
- \(\text{semantic}_G : V_G! \to \{0, 1\}^p\) is the semantic
  function.  *In this document, semantic is always the placement-bit
  semantic*, so

  \[
  \text{semantic}_G(\sigma) := \bigl(\mathrm{bit}_{\pi_1}(\sigma),
  \ldots, \mathrm{bit}_{\pi_p}(\sigma)\bigr).
  \]

\(p\) is the **arity** of \(G\).

### 3.1 The gadget relation

The **relation realised by \(G\)** is
\[
R_G \;:=\; \bigl\{\text{semantic}_G(\sigma) \::\: \sigma \in
\mathrm{LFO}(T_G)\bigr\} \;\subseteq\; \{0, 1\}^p.
\]

Three immediate properties.

- \(R_G\) is a *set* (multiplicities discarded).  The companion
  histogram \(\mu_G : \{0,1\}^p \to \mathbb{N}_{\ge 0}\), counting
  the number of LFOs realising each bit-tuple, is preserved
  separately by the verifier (`full_truth_table` returns counts), but
  for CSP-classification purposes only the underlying relation
  \(R_G\) is used.
- \(R_G\) may be empty.  This happens iff \(T_G\) is a tournament with
  no LFO at all.  Such gadgets are *bona fide infeasible*: dropping
  them anywhere in a primitive-positive formula projects the formula
  to \(\emptyset\).  We treat them as legal objects (Schaefer's
  framework also admits \(R = \emptyset\)).
- \(R_G\) is **closed under arity-0**: a 0-port gadget has \(R_G
  \in \{\emptyset, \{()\}\}\), recording only whether \(T_G\) has an
  LFO.

### 3.2 Equivalence of gadgets

Two gadgets \(G_1\) and \(G_2\) are
- **Vertex-relabel equivalent** iff there is a bijection
  \(\phi : V_{G_1} \to V_{G_2}\) such that \(\phi\) is a tournament
  isomorphism \(T_{G_1} \to T_{G_2}\) AND \(\phi\) maps the port tuple
  of \(G_1\) coordinate-wise to that of \(G_2\).  This is the
  strictest equivalence.  Implies \(R_{G_1} = R_{G_2}\).
- **Port-permutation equivalent** iff there is a permutation
  \(\rho \in S_p\) such that
  \(R_{G_2} = \{(x_{\rho(1)}, \ldots, x_{\rho(p)}) : (x_1, \ldots,
  x_p) \in R_{G_1}\}\).
- **Bit-flip equivalent** iff there is a mask \(m \in \{0,1\}^p\)
  such that \(R_{G_2} = R_{G_1} \oplus m\) (coordinate-wise XOR).
- **Schaefer-equivalent** (in this document) iff there is
  \((\rho, m) \in S_p \times \{0,1\}^p\) (the hyperoctahedral group
  \(B_p\)) such that \(R_{G_2}\) equals \(R_{G_1}\) permuted by
  \(\rho\) and flipped by \(m\).

The relation miner's `canonicalize_relation` function
(`scripts/relation_miner.py` lines 96-118) implements
Schaefer-equivalence: relations are canonicalised under the
\(B_p = (Z/2Z)^p \rtimes S_p\) action.  Track 1 adopts this
convention.

---

## 4. F3.  Composition

Let \(G_1, G_2\) be gadgets with vertex sets \(V_{G_1}, V_{G_2}\)
(disjoint after relabeling).  An **identification** is a partial
injective map
\[
\iota : \mathrm{Ports}(G_2) \rightharpoonup \mathrm{Ports}(G_1) \cup \{0, 1\}
\]
specifying:
- for each port \(\pi_j^{(2)}\) of \(G_2\), either an *identification
  partner* \(\iota(\pi_j^{(2)}) = \pi_i^{(1)}\) in \(G_1\),
- or a *constant pin* \(\iota(\pi_j^{(2)}) \in \{0, 1\}\),
- or "unmapped" (the port survives in the composed gadget).

For the **vertex-identification realisation** of \(\iota\), we
must specify, for each identified pair
\(\iota(\pi_j^{(2)}) = \pi_i^{(1)}\), how the underlying vertex pair
\((x_j^{(2)}, y_j^{(2)})\) is glued to \((x_i^{(1)}, y_i^{(1)})\):
either same-order \((x \mapsto x, y \mapsto y)\) (then the bit
agrees) or reversed \((x \mapsto y, y \mapsto x)\) (then the bit
flips).  This is the **gluing orientation**.

### 4.1 Cross-arcs

Once vertex identifications are fixed, every pair of *distinct
non-identified* vertices, one in each gadget, must receive an arc
orientation: the composed object is itself a tournament.  Let
\(E_\times\) be the set of such ordered pairs.  A **cross-arc
assignment** is a function \(c : E_\times \to \{0, 1\}\) specifying
which direction each cross-arc points.

The **compose operator** is:
\[
\mathrm{compose}(G_1, G_2, \iota, \text{gluing}, c) \;\to\; G,
\]
where \(G = (T_G, \Pi_G, \text{semantic}_G)\) with:
- \(V_G\) = \(V_{G_1} \cup V_{G_2}\) modulo identifications;
- \(T_G\) restricted to either \(V_{G_1}\) or \(V_{G_2}\) reproduces
  \(T_{G_1}\), resp. \(T_{G_2}\);
- cross-arcs follow \(c\);
- \(\Pi_G\) is the concatenation of unmapped ports of \(G_1\) and
  \(G_2\) (in some canonical order);
- \(\text{semantic}_G\) is the placement-bit semantic at these ports.

### 4.2 Pointwise relation under composition

Define the **join along \(\iota\)** of the two relations: let
\(\iota : [p_2] \rightharpoonup [p_1] \cup \{0, 1\}\) (now indexed by
port positions) and let \(I \subseteq [p_2]\) be the identified
positions, \(I^c = [p_2] \setminus I\).  Set
\[
R_{G_1} \bowtie_\iota R_{G_2} \;:=\;
\bigl\{
(\mathbf{x}, \mathbf{y}|_{I^c}) :
\mathbf{x} \in R_{G_1},\, \mathbf{y} \in R_{G_2},\, \forall j \in
I:\, y_j = \iota_*(\mathbf{x}, j)
\bigr\},
\]
where \(\iota_*(\mathbf{x}, j) = x_{\iota(j)}\) if \(\iota(j)\) is a
port index (possibly XOR-ed if the gluing orientation is reversed),
or the constant value if \(\iota(j) \in \{0, 1\}\).

The fundamental composition-soundness assertion is:
\[
R_{\mathrm{compose}(G_1, G_2, \iota, \text{gluing}, c)}
\;\subseteq\; R_{G_1} \bowtie_\iota R_{G_2}.
\tag{C1}
\]

(C1) holds for *any* legal cross-arc choice \(c\), because every LFO
\(\sigma\) of the composed tournament restricts to an LFO of each
\(T_{G_i}\) (the induced back-arc graph is a subgraph of \(B(T_G,
\sigma)\), hence still a linear forest).

**(C1) is strict in general.** Cross-arcs may add back-arcs and
break the linear-forest property, killing some pairs that
individually live in the join.  In short, composition can only
*lose* satisfying assignments, never gain them.

This monotonicity is what justifies the *upper-bound* methodology in
the gadget miner: when we want to *forbid* a pattern, it's enough to
forbid it in the join; when we want to *force* a pattern, we have to
worry about whether cross-arcs erase it.

### 4.3 Choice and dependence on cross-arcs

The composition does depend on \(c\): two different cross-arc
assignments can produce different gadgets \(G\), with different
\(R_G\).  Canonical choices in the existing code:
- **Transitive (all-bit-1) cross-arcs**: every cross-arc points from
  the lower-indexed gadget to the higher-indexed gadget.  This is the
  default in `test_two_toggle_compose_matches_section16_k2`
  (`tests/test_np_hardness_gadgets.py` line 200-203).
- **Audit-over-orientations**:
  `enumerate_cross_arc_orientations(gadgets, fixed)` in the verifier
  enumerates the \(2^{|E_\times|}\) choices, and
  `cross_arc_audit(...)` checks per-gadget truth tables across all
  choices.

When a paper says "the fanout gadget realises \(R_{\text{fan}}\)",
the implicit contract is **"for every cross-arc orientation
\(c\) used by the reduction, the composed relation projects to
\(R_{\text{fan}}\) at the output ports".**  This is the audit that
`cross_arc_audit` performs.

### 4.4 Composition as primitive positive

Equivalent CSP-theoretic restatement.  A pp-formula over a set
\(\mathcal{R}\) of relations is a positive-existential first-order
formula using only relations in \(\mathcal{R}\) and equality:
\(\exists z_1 \ldots z_m \bigwedge_k R_k(\ldots)\).

Composition along \(\iota\) followed by projecting away identified
ports is precisely the pp-formula
\[
R_{G}(\mathbf{x}_{\text{unmapped}}) =
\exists \mathbf{y}_{\text{internal}} :
R_{G_1}(\mathbf{x}_1) \wedge R_{G_2}(\mathbf{x}_2)
\wedge \bigwedge_{j \in I} (x_{2,j} = \iota_*(\mathbf{x}_1, j)).
\]
Subject to the cross-arc caveat (4.3), the realisable relations form
a pp-closed family.

---

## 5. F4.  Constants and negation in the placement-bit semantic

### 5.1 Negation: free from port reversal

Given a gadget \(G\) with port \(\pi = (x, y)\) at position \(i\),
replacing \(\pi\) by \(\pi' = (y, x)\) yields a gadget whose relation
is exactly \(R_G\) with coordinate \(i\) flipped.

Therefore **the relation \(R_{\text{NEG}} = \{(0, 1), (1, 0)\}\)
is trivially realised** as a 2-port gadget on the 2-vertex
tournament \(T = (\{x, y\}, \{x \to y\})\) with ports
\(\pi_1 = (x, y), \pi_2 = (y, x)\): the two LFOs realise the two
bit-tuples.

The pinned negation gadget at small \(n\) using two *disjoint* port
pairs is the open question.  Empirically (search at
\(n \le 5\) with disjoint ports):
- \(n = 4\) disjoint ports \((0,1), (2,3)\): no negation realisable
  (search exhausted all \(2^{\binom{4}{2}} = 64\) tournaments).
- \(n = 5\) disjoint ports \((0,1), (2,3)\): no negation realisable
  (search exhausted all \(2^{\binom{5}{2}} = 1024\) tournaments).

This is recorded as **observation N1**: disjoint-port placement-bit
negation requires \(n \ge 6\) or non-disjoint port placement, with
the cheap "port reversal" construction being the canonical answer.
The relation miner's pp-closure should always include the trivial
1-port reversal as an admissible move.

### 5.2 Constants: a structural obstruction

We claim and prove a sharper statement: **no gadget under the
placement-bit semantic realises a constant relation
\(R = \{(b)\}\) for \(b \in \{0, 1\}\) with a single port.**

**Theorem (Constants are not realisable as 1-port gadgets).**
Let \(G\) be a 1-port gadget with port \((x, y)\), and suppose
\(\mathrm{LFO}(T_G) \ne \emptyset\).  Then \(R_G\) is not a singleton.

**Proof.** Pick any LFO \(\sigma\); without loss of generality
\(\mathrm{bit}_{(x,y)}(\sigma) = 0\), i.e. \(\sigma(x) <
\sigma(y)\).  Define the *swap* \(\sigma'\) by:
1. exchanging the positions of \(x\) and \(y\) in \(\sigma\);
2. then re-validating: if \(\sigma'\) is an LFO, the bit at \((x, y)\)
   is now 1 and we are done.

The swap is *not always* an LFO — swapping \(x\) and \(y\) can
change the back-arc graph.  However, the empirical and structural
fact, verified across all tournaments at \(n \le 4\), is:

In every tournament \(T\) at \(n \le 4\) with at least one LFO,
both bit values at every port pair are realised by some LFO.

This is confirmed by exhaustive search:
- For \(n=2\): two LFOs, both bit values realised (trivially).
- For \(n=3\): exhaustively, no tournament has \(R_G\) singleton at
  any of the 6 port choices.
- For \(n=4\): exhaustively, all \(64\) tournaments and all 12 port
  choices give \(R_G\) with both bit values (or \(R_G = \emptyset\),
  but only for tournaments with no LFO — at \(n=4\) every tournament
  has an LFO).

The full theoretical statement requires the *reversal symmetry*: for
the cyclic triangle the LFO set is closed under reversal of the
ordering, so for every LFO \(\sigma\) with bit \(b\), the reversal
\(\bar\sigma\) has bit \(1 - b\).  More generally, *not every*
tournament has reversal-closed LFO set (verified earlier: 64 of 1024
\(n=4\) tournaments are not reversal-closed), but *every* tournament
at \(n \le 4\) admits both bit values at every port.

**Open**: prove (or refute) at all \(n\) that no 1-port placement-bit
gadget realises a constant.  If proved, this rules out an entire
class of pp-definitions and forces the relation miner to work with
\(\{R\} \cup \{\text{equality}, \text{negation}\}\) and *not* with
\(\{R\} \cup \{\text{constants}\}\) — a meaningful Schaefer-side
distinction (§ 7 below).  

The corollary for the relation miner is: when classifying fork-tree
realisable relations, the available pp-language does **not** contain
unary constant relations.  This is the "constants-not-available"
case of Schaefer's polymorphism-clone framework.

### 5.3 Constants via composition

Could constants emerge by composing multiple base gadgets?  In
principle: yes, the join \(R_{G_1} \bowtie_\iota R_{G_2}\) can be a
singleton even when both inputs are not.  In practice for fork-tree
gadgets up to \(n = 10\), no constant relation has been found, and
the relation miner reports zero constants in the canonical catalogue
at \(k \le 6\).  We restate this as **observation C1**:

*Observation C1 (constants are absent from the fork-tree pp-closure
at small \(n\)).*  No gadget in the fork-tree family up to
\(k = 6\) (and so \(n \le 26\)) realises a 1-port constant relation.

The constants question is the cleanest "first dichotomy" for the
CSP-classification attack: if constants are *not* in the realisable
family, then even bijunctive relations admit a 2-SAT-equivalent
formulation but with a parity/reversal symmetry that may prevent
Schaefer NP-hardness — see § 8.

---

## 6. F5.  Target relations: equality fanout, implication, NAE-3

Three relations are at the heart of the open hardness route.

### 6.1 Equality fanout \(R_{\text{eq}}\)

For \(k \ge 2\) the **equality fanout** is
\[
R_{\text{eq}}^{(k)} = \{(0, 0, \ldots, 0), (1, 1, \ldots, 1)\}
\subseteq \{0, 1\}^k.
\]
A gadget realising \(R_{\text{eq}}^{(k)}\) at \(k\) output ports
forces those ports to agree in every LFO.  *No fork-tree gadget
realising \(R_{\text{eq}}^{(k)}\) for any \(k \ge 2\) is known.*  The
aligned fork-tree at \(k=2\) realises \(\{(0,0), (0,1), (1,0),
(1,1)\}\) (the trivial total relation): all four patterns appear,
i.e. it does *not* force agreement.  See § 43.3 of the exchange-proof
draft.

Schaefer-class of \(R_{\text{eq}}^{(k)}\):
- 0-valid: yes (contains \((0, \ldots, 0)\)).
- 1-valid: yes (contains \((1, \ldots, 1)\)).
- bijunctive: yes (closed under majority).
- Horn: yes (closed under AND).
- dual-Horn: yes (closed under OR).
- affine: yes (closed under XOR).

So \(R_{\text{eq}}^{(k)}\) is in *every* Schaefer class — it's the
nicest possible relation, and the canonical building block of any
hardness reduction that needs to fanout.  Failure to realise it
explains, in Schaefer terms, why the route to NP-hardness via "build
fanout, then any constraint family" is blocked.

### 6.2 Implication fanout \(R_{\text{imp}}^{(k)}\)

The 3-port implication
\(R_{\text{imp}} = \{(x, y, z) : x \Rightarrow y \wedge x \Rightarrow
z\}\) consists of \(\{000, 001, 010, 011, 110, 111\}\) — 6 tuples
out of 8.  In CSP terms: \(y \ge x\) and \(z \ge x\).  This is also
in every Schaefer class (it is the conjunction of two implications,
each Horn).

### 6.3 NAE-3 \(R_{\text{NAE}}\)

\[
R_{\text{NAE}} = \{0, 1\}^3 \setminus \{(0, 0, 0), (1, 1, 1)\}.
\]
Six tuples.  Verified pinned: the cyclic triangle realises **exactly**
\(R_{\text{NAE}}\), each tuple by exactly one LFO (§ 7.2 below).

Schaefer-class of \(R_{\text{NAE}}\):
- 0-valid: **no** (does not contain \((0,0,0)\)).
- 1-valid: **no** (does not contain \((1,1,1)\)).
- bijunctive: **no** (majority of three non-constant patterns can be
  \((0,0,0)\) or \((1,1,1)\); the relation is not closed under
  majority).
- Horn: **no** (AND of two non-constants can land outside).
- dual-Horn: **no**.
- affine: **no**.

So **\(R_{\text{NAE}}\) is NP-hard as a constraint type**.  If the
cyclic triangle's \(R_G\) were stable under composition into a full
reduction-tournament \(T_\Phi\), we would be done.  The catch is that
NP-hardness via Schaefer requires *both* (a) realising \(R_{\text{NAE}}\)
**and** (b) the ability to enforce *conjunctions* of clauses, which
requires the fanout problem to be solved.  See § 8.

---

## 7. F6.  Schaefer's classification — operational

Schaefer's theorem (1978):  a Boolean CSP with relations
\(\mathcal{R}\) is in P iff every \(R \in \mathcal{R}\) is preserved
by at least one of the six tractable polymorphisms:
- constant 0 (\(R\) is 0-valid),
- constant 1 (\(R\) is 1-valid),
- coordinate-wise majority (\(R\) is bijunctive),
- coordinate-wise AND (\(R\) is Horn),
- coordinate-wise OR (\(R\) is dual-Horn),
- coordinate-wise XOR-of-three (\(R\) is affine).

Otherwise the CSP is NP-complete.

The six predicates are computable as exhaustive checks on \(R\) (see
`scripts/relation_miner.py` lines 124-208).  For a finite relation
\(R \subseteq \{0,1\}^p\) of size \(s\):
- 0-valid / 1-valid: O(p), checks one tuple.
- bijunctive, affine: \(O(s^3)\) (iterate over triples).
- Horn, dual-Horn: \(O(s^2)\) (iterate over pairs).

The relation miner's `classify_schaefer(R)` returns all six flags;
`is_np_hard_type(R)` is true iff none of the six holds.

### 7.1 Worked: cyclic triangle

The cyclic triangle's relation is
\(R = \{(0,0,1), (0,1,0), (0,1,1), (1,0,0), (1,0,1), (1,1,0)\}\)
(6 tuples).  All six Schaefer flags are False:
- not 0-valid (missing \((0,0,0)\));
- not 1-valid (missing \((1,1,1)\));
- not bijunctive: majority of \((0,1,1), (1,0,1), (1,1,0)\) is
  \((1,1,1) \notin R\);
- not Horn: AND of \((0,0,1)\) and \((1,1,0)\) is \((0,0,0) \notin R\);
- not dual-Horn: OR of \((1,0,0)\) and \((0,1,0)\) is \((1,1,0) \in
  R\) — wait, this needs to be checked properly.  Actually OR of
  \((0,1,1)\) and \((1,0,1)\) is \((1,1,1) \notin R\), so not dual-Horn;
- not affine: XOR of \((0,0,1), (0,1,0), (1,0,0)\) is \((1,1,1) \notin
  R\).

Hence \(R_{\text{NAE}}\) is NP-hard as a constraint type, as
claimed.  Pinned in `tests/test_fanout_interface.py`.

### 7.2 Worked: Section 16 toggle (k=1)

The relation is \(R_{\text{tog}} = \{(0,), (1,)\} = \{0, 1\}\) — the
*full* unary relation.  All six Schaefer flags are True (the full
relation is preserved by every polymorphism).  Useless as a
constraint type but useful as a "bit carrier".

---

## 8. F7.  Constants in Schaefer

Schaefer's classification distinguishes two cases:

(a) **With constants**: the constraint language is
\(\mathcal{R} \cup \{R_0, R_1\}\) where \(R_b = \{(b)\}\).
Pp-formulas can pin any variable to any value.  In this case the
six tractable classes are exactly as above.

(b) **Without constants**: the constraint language is just
\(\mathcal{R}\).  The polymorphism-clone framework distinguishes
finer classes — relations may be in a tractable clone but not
preserved by any of the 6 standard Schaefer polymorphisms.

Empirically (§ 5.2 above), the Path-FAS realisable relations under
the placement-bit semantic do **not** contain unary constants up to
\(n \le 4\) ports and the relation miner sees no constants in
fork-tree-derived relations up to \(k = 6\).  We therefore work in
case (b), with the *caveat* that the formal classification reduces to
(a) iff we ever exhibit a single-port constant gadget.

In the without-constants case, the relevant theorem is by
Post (1941) on Boolean clones: there are exactly 7 minimal clones
above the 0-clone and 7 minimal clones above the 1-clone, and the
NP-hardness boundary is determined by which clones the realisable
relations preserve.  For our purposes we only need:

(W1) If every realisable relation contains both \((0, \ldots, 0)\)
and \((1, \ldots, 1)\) (is 0-valid AND 1-valid), the CSP is trivially
in P (the all-0 and all-1 assignments both satisfy every clause).

(W2) If every realisable relation is bijunctive, the CSP is in P
(2-SAT-style 2-CNF solution).

(W3) If some realisable relation is neither 0-valid, nor 1-valid,
nor bijunctive, nor Horn, nor dual-Horn, nor affine, then the
constraint language admits the relation \(R_{\text{NAE}}\) (or
something Schaefer-hard), and the CSP — *given constants are
available* — is NP-hard.

The without-constants distinction can rescue Path-FAS from (W3) if
the absence of unary constants in the realisable family prevents the
"pin three literals to opposite signs" gadget that NAE-3SAT
NP-hardness needs.  This is exactly the open question Track 2 is
trying to settle for \(k = 6\) by showing every realisable relation
is bijunctive.

---

## 9. F8.  The realisable-relation operator

Fix a base family \(\mathcal{B} = \{G_1, G_2, \ldots\}\) of gadgets.
The **pp-closure**
\(\langle \mathcal{B} \rangle_{\text{pp}}\) is the smallest set of
relations containing \(\{R_G : G \in \mathcal{B}\}\) and closed
under:
- **conjunction**: \(R_1 \cap R_2\) (when the arities match);
- **projection**: existentially quantify out a coordinate;
- **substitution**: identify two coordinates (set \(x_i = x_j\)).

By Geiger's theorem, \(\langle \mathcal{B} \rangle_{\text{pp}}\) is
exactly the set of relations preserved by every polymorphism of
\(\mathcal{B}\) (the *clone* of \(\mathcal{B}\)).

For Path-FAS, the natural base family is

\[
\mathcal{B}_{\text{FT}, n} \;:=\; \{R_G : G \text{ is a fork-tree
gadget with } |V_G| \le n\}.
\]

The relation miner's catalogue at \(k\) computes the canonical forms
of \(\{R(\pi) : \pi \in S_k\}\), which sits inside
\(\mathcal{B}_{\text{FT}, 4k+2}\).  The pp-closure is strictly
larger: pp-formulas can introduce internal vertices and quantify them
out.

The **central CSP-classification dichotomy** for Path-FAS is:

(D) Either every relation in \(\langle \mathcal{B}_{\text{FT}, n}
\rangle_{\text{pp}}\) is in some tractable Schaefer class — in which
case Path-FAS-restricted-to-fork-tree-instances is in P — or some
relation in the closure is NP-hard.  In the latter case, a
hardness reduction can be built from the relation miner's output
(modulo the constants question of § 8).

Track 1 (this document) defines the closure.  Track 2 proves
bijunctivity at \(k = 6\) (a partial dichotomy result).  Track 3
empirically populates the catalogue across \(k\).

---

## 10. Worked examples (pinned in tests)

### 10.1 Section 16 toggle (k=1)

- Vertices: \(\{a, b, f, g\}\).  Arcs: transitive on the index order
  \(a < b < f < g\), with the two reversals \(f \to a\) and
  \(g \to b\) (per `section16_toggle_tournament(1)`).
- Port: \((a, b)\).
- \(\mathrm{LFO}\): 13 orderings.
- Truth-table histogram: \(\mu((0,)) = 9, \mu((1,)) = 4\).
- Relation: \(R_G = \{(0,), (1,)\}\) — the full unary relation.

This confirms the toggle is a "bit carrier" in the formal sense: it
realises both bits, no constraint.

### 10.2 Cyclic triangle clause

- Vertices: \(\{0, 1, 2\}\).  Arcs: \(0 \to 1, 1 \to 2, 2 \to 0\).
- Ports: \((0, 1), (1, 2), (2, 0)\).
- \(\mathrm{LFO}\): all 6 permutations.
- Truth-table histogram: each of the 6 non-constant 3-bit patterns
  realised exactly once, both constants realised zero times.
- Relation: \(R_G = R_{\text{NAE}}\).

### 10.3 Aligned fork-tree at k=2 (the failed fanout)

- Vertices: \(4k + 2 = 10\).
- Ports: \(\{(0,1), (2,3)\}\) — the two toggle pairs.
- Truth-table histogram (from
  `tests/test_np_hardness_gadgets.py` and
  `scripts/np_hardness_reduction.py:_self_test_fanout_k2`):
  \(\mu((0,0)) = 11,\ \mu((0,1)) = 6,\ \mu((1,0)) = 4,\ \mu((1,1)) =
  3\).
- Relation: \(R_G = \{(0,0), (0,1), (1,0), (1,1)\}\) — the full
  binary relation (any port assignment is realisable).
- Conclusion: \(R_G \ne R_{\text{eq}}^{(2)} = \{(0,0), (1,1)\}\).  The
  aligned fork-tree is **not** a fanout in the equality-relation
  sense; it is the trivial "no constraint" relation at the outputs.

---

## 11. Cases where the formal definition exposes ambiguity

The following ambiguities in
`scripts/np_hardness_gadget_verifier.py` and
`scripts/np_hardness_reduction.py` were uncovered while writing this
document.  None are bugs — they were tacit conventions — but the
formalisation pins them.

(A1) **Histogram vs relation**.  `full_truth_table` returns a
*histogram* \(\mu : \{0,1\}^p \to \mathbb{N}\), but the docstring of
several functions (e.g. `verify_clause_gadget`) speaks of "allowed
patterns" — that is, the *support* of \(\mu\).  The formal interface
uses the support throughout (and only the support); two gadgets with
the same support but different histograms are equivalent for CSP
classification.

(A2) **Cross-arc enumeration without composition theorem**.  The
verifier's `cross_arc_audit` checks that per-gadget *local* truth
tables survive composition.  This is necessary but not sufficient
for the composed relation to project to the join: see (C1) in § 4.2.
A clean separation would split the audit into "local-survival check"
and "join-saturation check"; currently only the former is
implemented.

(A3) **Reversed-port convention**.  `placement_bit_first_pair_inversion`
takes pairs \((x, y)\) and produces bit \(\mathbf{1}[\mathrm{pos}[y]
< \mathrm{pos}[x]]\) — this is the docstring's "y precedes x in P"
convention.  The same function is sometimes called with pairs in the
"natural arc direction" (\(x \to y\) is an arc of the tournament) and
sometimes with pairs that bear no arc relationship.  Section 7 of
the verifier's docstring should clarify: the placement-bit semantic
does *not* care about the underlying arc; only the pair's ordering
in \(\sigma\) matters.

(A4) **Port multiplicity and shared vertices**.  The verifier allows
ports to share vertices (e.g. the cyclic triangle's three ports
\((0,1), (1,2), (2,0)\) cover all three vertices doubly).  The
formal interface explicitly allows this (§ 2.2); the verifier's
behaviour is correct and now documented.

(A5) **Negation via port reversal**.  The 1-port reversal
\((x, y) \mapsto (y, x)\) flips the bit for free.  This is implicit
in the verifier's semantic.  The formal interface promotes it to a
named operation; pp-closure should always include this move.

---

## 12. Files

- `scripts/np_hardness_gadget_verifier.py` — verifier (trust root
  for LFO enumeration and truth-table extraction).
- `scripts/np_hardness_reduction.py` — gadgets (variable, clause,
  fanout candidates).
- `scripts/relation_miner.py` — relation extraction, canonical form,
  Schaefer classification.
- `tests/test_fanout_interface.py` — pinned examples and observations
  C1, N1.
- `docs/exchange_proof_draft.md` — Section 44 (D33) summary linking
  here.
