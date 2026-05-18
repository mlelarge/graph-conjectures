# Attack plan: Bang-Jensen–Yeo good-decomposition conjecture

**Conjecture (Bang-Jensen & Yeo, OPG 2013-03-02).** There exists an integer $K$ such that every $K$-arc-strong digraph has a *strong arc decomposition*, i.e. an arc-partition $A(D) = A_1 \mathbin{\dot\cup} A_2$ such that both $(V, A_1)$ and $(V, A_2)$ are strongly connected.

Plan v4, 2026-05-16. v3 revised after `review.md` v2; v4 applies the 5 sentence-level corrections from `team/05_audit.md` (round-1 audit).

## Working equivalence used throughout

A 2-coloring of $A(D)$ is a strong arc decomposition iff **every directed cut $\delta^+(X)$, $\emptyset \neq X \subsetneq V$, contains an arc of each color.** So we are looking for a simultaneous bichromatic covering of all $2^n - 2$ directed cuts.

A necessary condition is 2-arc-strongness. It is not sufficient: known 2-arc-strong obstructions include $S_4$, squares of even directed cycles inside locally semicomplete digraphs, the four exceptional 2-arc-strong semicomplete compositions of Bang-Jensen–Gutin–Yeo 2020, and the 2-arc-strong split-digraph obstructions characterized by Ai–He–Li–Qin–Wang 2024.

> **Note on the split-digraph literature.** Bang-Jensen–Wang 2025 prove every 3-arc-strong split digraph has a strong arc decomposition and give **infinite 2-vertex-strong** ("2-strong" in their terminology) split digraphs without one; these examples show vertex-connectivity 2 is insufficient, but they do not by themselves give an infinite 2-arc-strong split obstruction family. The source for actual 2-arc-strong split exceptions is Ai–He–Li–Qin–Wang 2024, who give a complete characterization. Those exceptions — not the 2-vertex-strong examples — are the right benchmark for the verifier.

## Bedrock claims

1. **Edmonds gives only a one-sided packing.** For a $k$-arc-strong $D$ and any chosen root $r$, Edmonds' branching theorem yields $k$ arc-disjoint out-branchings $T_1^+, \dots, T_k^+$ rooted at $r$ and, separately, $k$ arc-disjoint in-branchings rooted at $r$. The two packings overlap on arcs. A strong arc decomposition immediately yields arc-disjoint in/out branching pairs inside each color class with a chosen root; the converse — that an "arc-disjoint good pair" $(T^+, T^-)$ gives strong color classes — is weaker, since the union $T^+ \cup T^-$ is strong but says nothing about the remaining arcs. So Edmonds-style attacks need an explicit repair step, not just a pairing.
2. **Strong connectivity is not a matroid.** Frank's results rule out Nash-Williams / Tutte-style spanning-tree packing as a direct lift. The deeper reason is the *simultaneous directed cut-covering* formulation above: choices on overlapping cuts can force contradictions.
3. **NP-completeness on 2-regular digraphs.** Deciding strong arc decomposition is NP-complete (Bang-Jensen–Yeo), already so for 2-regular digraphs. The correct inference is: **any positive theorem must use large arc-connectivity structurally**, because low-degree / low-connectivity recognition is hard. This does *not* rule out polynomially checkable structure theorems at fixed large $K$.
4. **Lower-bound silence.** No published infinite family of $\geq 3$-arc-strong digraphs without strong arc decomposition is known. Known 2-arc-strong bad families (semicomplete $S_4$; squares of even directed cycles in locally semicomplete; the 4 BJG–Yeo 2020 exceptional semicomplete compositions; Ai–He–Li–Qin–Wang's 2-arc-strong split exceptions) all sit at arc-connectivity 2. The meta-hypothesis this points to is:

   > **(WC3) Every 3-arc-strong digraph has a strong arc decomposition.**

   If true, it solves Bang-Jensen–Yeo with $K = 3$. If false, an infinite 3-arc-strong bad family is a publishable counterexample and reshapes the conjecture's plausible $K$. Either way, WC3 is the right working conjecture.

5. **Ear induction has a global obstruction.** A Hamilton directed cycle is minimally strong; on its own it contributes nothing to a two-color strong decomposition, and adding a single chord is far from enough. Any ear induction must add ears in *bundles* with a reserve structure guaranteeing each color class accumulates enough directed-cut coverage on every prefix.

6. **Directed splitting-off theorems** (Mader, Frank) can preserve prescribed local arc-connectivities under explicit admissibility hypotheses, but strong arc decompositions do not automatically lift through such operations. A general splitting-off reduction is therefore not available; the right object is a *controlled lifting lemma* with explicit color-compatibility constraints (see Track C1).

## The EC-log lemma (short, attempted on paper first)

The original "Eulerian flagship" was a slogan. The honest first Eulerian milestone is the logarithmic statement, and it is not a high-risk directed-cut-counting program — it reduces to **undirected** Karger cut counting.

**Reduction.** Let $D$ be Eulerian and let $G$ be its underlying undirected multigraph. For every $\emptyset \neq X \subsetneq V(D)$,
$$|\delta_D^+(X)| = |\delta_D^-(X)|, \qquad d_G(X) = |\delta_D^+(X)| + |\delta_D^-(X)| = 2\,|\delta_D^+(X)|.$$
Hence if $\lambda(D) := \min_X |\delta_D^+(X)|$, the undirected edge-connectivity of $G$ is $\lambda_G = 2\lambda(D)$, and a directed cut in $D$ of size $s$ is an undirected cut in $G$ of size $2s$.

**Lemma (EC-log target).** There is an absolute constant $C$ such that every Eulerian digraph $D$ with $\lambda(D) \geq C \log_2 n$ has a strong arc decomposition.

**Proof outline.** Color each arc of $D$ independently red/blue with probability $1/2$. A directed cut $\delta^+(X)$ of size $s$ is monochromatic with probability $\le 2^{1-s}$. Group cuts by their size in bands $j\lambda \le |\delta^+(X)| < (j+1)\lambda$; in $G$, these are undirected cuts of size $< (j+1)\cdot 2\lambda = (j+1)\lambda_G$, hence at most $(j+1)$ times the undirected min-cut. Karger's cut-counting theorem (JACM 2000) bounds the number of such undirected cuts by $n^{2(j+1)}$. The expected number of monochromatic directed cuts is therefore at most
$$\sum_{j \geq 1} n^{2(j+1)} \cdot 2^{1 - j\lambda} \;=\; 2 n^2 \sum_{j \geq 1} \Bigl(\tfrac{n^2}{2^\lambda}\Bigr)^j.$$
For $\lambda \geq C \log_2 n$ with $C > 4$, the ratio $n^2 / 2^\lambda < 1/n^{C-2}$ is summable and the expectation is $< 1$ for large $n$ (small $n$ absorbed by increasing $C$). The first-moment method then yields a 2-coloring with no monochromatic directed cut, i.e. a strong arc decomposition. $\square$

EC-log was drafted on paper in week 1; see `team/04_ec_log_proof.md` for the proof with $C = 6$, $n_0 = 3$. The first-moment argument suffices — no alteration step is needed. *(Edit 2026-05-18: this line previously read "$C = 5$, $n_0 = 2$ (or $C' = 6$ with no $n_0$ caveat)"; the $C = 5$ headline was retracted in `CORRECTNESS_REVIEW_2026_05_18.md` §2.5 because the inequality $5\log_2 n > 4\log_2 n + 3$ requires $n \ge 9$, not $n \ge 4$.)*

What remains genuinely hard after EC-log:
- Removing Eulerianness.
- Replacing $\log n$ by a constant.
- Either of these reverts the problem to its full directed-cut-counting difficulty, for which there is no clean off-the-shelf undirected analogue (cf. Cen–Li–Nanongkai–Saranurak, FOCS 2021, on directed min-cuts).

## Two-track plan after EC-log

Tracks B and C run from day 1 once the verifier is up. They share infrastructure (SAT/ILP) and feed each other.

### Track B — counterexample / lower-bound

Primary question: **Is WC3 true?** Hunt for a 3-arc-strong digraph with no strong arc decomposition.

Vehicles (priority order, sharpest first):

1. **Laminar systems of tight 3-cuts engineered to force incompatible color choices.** Most conceptually promising. A bad 3-arc-strong example, if it exists, likely comes from a global 2-SAT-style obstruction over a family of tight directed cuts.
2. **Eulerian 3-arc-strong digraphs with many minimum directed cuts.** Eulerianness limits flexibility while preserving connectivity; many tight cuts maximize the chance of a global conflict. (Note: EC-log rules out the *high-$\lambda$* Eulerian regime, so the target window is $\lambda(D) = 3$ exactly, with cut-rich structure.)
3. **Gluings of known 2-arc-strong obstruction templates along controlled 3-arc interfaces.** Templates: Ai–He–Li–Qin–Wang 2024 split exceptions; the four BJG–Yeo 2020 semicomplete-composition exceptions; squares of even directed cycles; $S_4$. *Do not* use the Bang-Jensen–Wang 2-vertex-strong split examples here — those are not 2-arc-strong and gluing them across 3-arc interfaces may just repair an unrelated vertex-connectivity defect.
4. **Orientations of small 4- or 6-edge-connected undirected graphs**, choosing asymmetric orientations to break each edge's symmetry while preserving directed arc-strength.
5. **Iterated substitution** of 2-arc-strong obstruction templates into themselves, tracking which directed cuts remain tight.
6. **Lexicographic blow-ups $H[\overline{K_t}]$** — use, but expect them to become positive examples once $t$ grows (composition theorems).
7. **Cayley digraphs on small non-abelian groups** — vertex-transitivity tends to provide balanced circulations and make decomposition easier; mostly a control / sanity-check family.

### Track C — controlled-lifting and structural

**C1. Candidate lifting lemma to extract.** From the Bang-Jensen–Wang split-digraph proof, attempt to extract a reusable lemma of the following shape (the lemma is *conjectural* until proved; see `team/02_structural_program.md` for the first-pass extraction, candidate statement **CL1**, and three explicit unresolved TODOs):

> If $D'$ is obtained from $D$ by splitting off arc pairs at a vertex $v$, and $D'$ has a strong arc decomposition satisfying explicit color-compatibility constraints at $v$, then $D$ has a strong arc decomposition.

Apply to one new class beyond {semicomplete, locally semicomplete, semicomplete compositions, split digraphs}. Candidate classes:

- **near-split digraphs** (controlled perturbations of split structure);
- **in-locally / out-locally semicomplete digraphs** (one-sided round decomposition; not subsumed by the existing locally semicomplete theorem);
- **digraphs with bounded independence number**.

*Quasi-transitive digraphs* are **definitively absorbed** by Bang-Jensen–Gutin–Yeo 2020 Theorem 1.6 via the Bang-Jensen–Huang 1995 recursive structure: every strong quasi-transitive digraph $Q$ can be written as $T[H_1, \dots, H_t]$ with $T$ strong semicomplete and $H_i$ arbitrary, and BJG–Yeo 2020 handles exactly this composition setting. Removed from the C1 candidate-class list.

**C2. Eulerian program beyond EC-log.** Conditional on EC-log being proved cleanly (~2 weeks), the next two targets are:
- (a) replace $\log n$ by a constant for Eulerian digraphs;
- (b) extend EC-log to digraphs with prescribed degree-balance defect (e.g. $\big|\,|\delta^+(X)| - |\delta^-(X)|\,\big| \leq f(\lambda)$).
Both are high-risk; (b) is the natural bridge to non-Eulerian inputs.

## Computational backbone (Track A — runs first, then continues serving B and C)

Drop blind isomorph-free generation. Verifier-first, with an explicit certificate contract.

**Verifier contract.**

1. **First implementation: ILP / cut-separation.** Variables $x_e \in \{0,1\}$ (one bit per arc). For every nonempty proper $X \subsetneq V$,
   $$1 \;\le\; \sum_{e \in \delta^+(X)} x_e \;\le\; |\delta^+(X)| - 1.$$
   Separate violated cuts lazily by min-cut computations in each implied color class. This is the unambiguous statement of strong arc decomposition and the right baseline.
2. **SAT implementation: arborescence witnesses, not vague reachability.** For each color $c \in \{R, B\}$ and each direction $\sigma \in \{+, -\}$, select a rooted $\sigma$-branching whose arcs are constrained to color $c$. One out-branching and one in-branching per color jointly certify strongness of that color. This avoids transitive-closure encodings that silently accept invalid decompositions or blow up in size.
3. **Cross-check** SAT against ILP on every benchmark.

**Validation set (must run before scaling).** UNSAT: $S_4$; squares of even directed cycles; the four BJG–Yeo 2020 exceptional 2-arc-strong semicomplete compositions; the small members of the Ai–He–Li–Qin–Wang 2024 2-arc-strong split exceptions. SAT: small positive instances in each of the four solved classes, plus several 3-arc-strong digraphs across families.

**Structured candidate generation, not blind enumeration.** Target families: minimally $k$-arc-strong digraphs; Eulerian $k$-arc-strong digraphs with many small cuts; gadget compositions preserving exactly 3 arcs across interfaces; small Cayley digraphs on $|G| \le 24$; split and near-split perturbations; the Track-B vehicles 1–4 above.

**Obstruction extraction.** On UNSAT instances, extract a minimal unsat core over cut/color constraints. Translate the core into a human-readable obstruction: a laminar (or near-laminar) family of directed cuts whose required color choices are inconsistent under a small 2-SAT instance. This is the bridge from solver output to a structural counterexample family.

**Honest negative result language.** A finite search can only conclude: *no bad 3-arc-strong digraph was found up to $n \le N$ in the searched family $\mathcal{F}$*, with $N$ and $\mathcal{F}$ explicit. Avoid "$f(3) = \infty$" or any phrasing implying an infinite search range.

## Phased roadmap

| Phase | Duration | Deliverable | Risk |
|------|----------|-------------|------|
| 0 — literature & benchmark correction | Week 1 | Corrected bibliography separating 2-strong from 2-arc-strong split families; table of known positive classes and thresholds; benchmark list of 2-arc-strong exceptions (including Ai–He–Li–Qin–Wang 2024 split exceptions); quasi-transitive "check if absorbed" note. | low |
| 1 — EC-log on paper | Weeks 1–2 | Written proof of the EC-log lemma using the Eulerian-to-undirected reduction + Karger cut counting. Identify any gap. | low–medium |
| 2 — verifier (ILP first, SAT after) | Weeks 2–5 | ILP/cut-separation model with lazy separation; SAT model with arborescence witnesses; cross-check on the validation set. | medium (engineering) |
| 3 — counterexample search | Weeks 5–8, continuing | Search Track-B vehicles 1–4 on 2-arc-strong obstruction templates glued along 3-arc interfaces. Either a 3-arc-strong bad example (then minimize, then attempt infinite extension) or a documented negative search report with a conjectural obstruction classification. | medium; high upside |
| 4 — controlled-lifting program | Months 2–6, parallel to 3 | Generalized lifting lemma à la Bang-Jensen–Wang; application to one new class (near-split / one-sided locally semicomplete / bounded independence number). | high but mathematically meaningful |
| 5 — Eulerian beyond EC-log | Starts only after EC-log is in writing | Constant-$C$ Eulerian theorem, or extension to bounded-defect non-Eulerian inputs. | high |
| 6 — write-up | Rolling | (i) EC-log note (short, low-stakes); (ii) counterexample note if Phase 3 succeeds; (iii) structural paper if Phase 4 yields a new class; (iv) Eulerian-beyond-EC-log paper if Phase 5 becomes precise. | low |

**Biggest single risk:** Phase 4 (controlled lifting) depends on the split-digraph proof technique being extractable into a class-agnostic lemma. If extraction fails, Phase 4 becomes unfocused exploration; in that case shift weight to Phase 3 + Phase 5(b).

## Known prior work

**Semicomplete digraphs (the foundational characterization).**
- J. Bang-Jensen, A. Yeo, *Decomposing $k$-arc-strong tournaments into strong spanning subdigraphs*, Combinatorica 24 (2004), 331–349. Source of the semicomplete characterization (every 2-arc-strong semicomplete digraph $\neq S_4$ has a strong arc decomposition) and of the tournament decomposition framework reused widely thereafter. So every 3-arc-strong semicomplete digraph has a strong arc decomposition.

**Locally semicomplete digraphs.**
- J. Bang-Jensen, J. Huang, *Decomposing locally semicomplete digraphs into strong spanning subdigraphs*, J. Combin. Theory Ser. B 102 (2012), 701–714. DOI `10.1016/j.jctb.2011.09.001`. Every 2-arc-strong locally semicomplete digraph not equal to the square of an even directed cycle has a strong arc decomposition, polynomial-time constructible. Hence every 3-arc-strong locally semicomplete digraph has one.

**Semicomplete compositions.**
- Y. Sun, G. Gutin, J. Ai, *Arc-disjoint strong spanning subdigraphs in compositions and products of digraphs*, Discrete Math. 342 (2019), 2297–2305. Handles the $|V(H_i)| \geq 2$ subcase with **three** exceptional digraphs (no $S_4$, since $|V(H_i)| \geq 2$ excludes it); the full four-exception characterisation including $S_4$ is BJG–Yeo 2020 below.
- J. Bang-Jensen, G. Gutin, A. Yeo, *Arc-disjoint strong spanning subdigraphs of semicomplete compositions*, J. Graph Theory 95 (2020), 267–289. arXiv:1903.12225. Complete characterization: a strong semicomplete composition $T[H_1, \dots, H_t]$ has a strong arc decomposition iff it is 2-arc-strong and is not one of four explicit exceptional digraphs. Every 3-arc-strong semicomplete composition has one.

**Split digraphs (corrected reading).**
- J. Bang-Jensen, Y. Wang, *Strong arc decompositions of split digraphs*, J. Graph Theory 108 (2025), 5–26. arXiv:2309.06904. Every 3-arc-strong split digraph has a strong arc decomposition, polynomial-time constructible. Infinite families of **2-vertex-strong** split digraphs without strong arc decomposition exist; these show vertex-connectivity 2 is insufficient but are not, by themselves, an infinite 2-arc-strong split obstruction family.
- J. Ai, F. He, Z. Li, Z. Qin, C. Wang, *A complete characterization of split digraphs with a strong arc decomposition*, arXiv:2408.02260 (2024). The actual source for 2-arc-strong split exceptions; these are the right benchmarks for the verifier.
- (Related, for context.) *Arc-disjoint in- and out-branchings in semicomplete split digraphs*, Discrete Appl. Math. 375 (2025), 259–268. Introduction quotes the Ai et al. 2-arc-strong split characterization.

**Hardness.**
- J. Bang-Jensen, A. Yeo (theorem cited as Theorem 1.1 in Bang-Jensen–Wang 2025): deciding strong arc decomposition is NP-complete, already so for 2-regular digraphs. The book treatment is Bang-Jensen–Gutin, *Digraphs: Theory, Algorithms and Applications* (2nd ed., Springer 2009), Theorem 13.10.1.

**Probabilistic / cut counting (used in EC-log).**
- D. R. Karger, *Minimum Cuts in Near-Linear Time*, J. ACM 47 (2000), 46–76. arXiv:cs/9812007. Undirected cut-counting bound $n^{2k}$ used directly via the Eulerian reduction.
- R. Cen, J. Li, D. Nanongkai, D. Panigrahi, K. Quanrud, T. Saranurak, *Minimum Cuts in Directed Graphs via Partial Sparsification*, FOCS 2021. arXiv:2111.08959. Cautionary reference: directed cut counting is delicate, which is why EC-log routes through the underlying undirected multigraph rather than a directed analogue.

**Survey.**
- J. Bang-Jensen, M. Kriesell, *Disjoint sub(di)graphs in digraphs*, Electron. Notes Discrete Math. 34 (2009), 179–183.

## Open decision before starting

Phase 0–2 (literature, EC-log, verifier) is a fixed ~5-week prefix. After that:

- **Weight to Phase 3 (counterexample search).** Fastest possible publishable artifact if WC3 is false; documented dead-end if WC3 is true, but the dead-end is itself informative and tells Phase 4 / 5 what to target.
- **Weight to Phase 4 (controlled-lifting / new class).** Slower; payoff is a genuine new positive theorem extending the BJG–Yeo / BJ–Huang / BJ–Wang line.
- **Equal weight, with Phase 5 as a low-priority side track once EC-log is written up.** Recommended; Phases 3 and 4 share the verifier and the obstruction-extraction pipeline, and EC-log already gives a short publishable note independently.
