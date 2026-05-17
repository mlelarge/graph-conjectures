# Plan: prove (or disprove) a tractable slice of Albertson's Conjecture

Source: M. O. Albertson, posted at openproblemgarden.org/op/crossing_numbers_and_coloring (2007/2009). High importance, open since 2007. Wide literature; current state recorded in the local snapshot
`/Users/lelarge/Recherche/graph-conjectures/site/op/crossing_numbers_and_coloring/index.html`.

## Revision history

- **v4** (this version, 2026-05-16): rewrite after the senior post-team-launch
  audit in `docs/review_v3.md`. Major changes (one short sentence each):
  - **Fixed edge-connectivity attribution:** $(t-1)$-edge-connectivity of
    $t$-critical graphs is **Dirac 1953**, not Kostochka–Stiebitz.
  - **Added Kostochka–Yancey edge-density bounds** (arXiv:1209.1050) at the
    three Cranston residual orders, in both the standard and the non-Ore
    strengthening form, with the exact numbers from the audit.
  - **Qualified the BK Crossing-Lemma threshold:** the arXiv abstract gives
    $|E| \ge 6.77|V|$; Cranston invokes $6.95|V|$; the PDF should be checked
    before either is used as the sole gating threshold.
  - **Deleted the false $25$-Ore critical path** at $(25, 48)$: the Ore-order
    congruence $|V| \equiv 1 \pmod{k-1}$ excludes $48$ for $k = 25$.
  - **Added an Ore-congruence subsection** with the one-line proof and the
    consequence for each Cranston residual order.
  - **Marked $(26, 51)$ as the only Ore residual corner** and noted the
    plausible (but not proven) "small one-composition family from two
    $K_{26}$s" reading — assigned to Role 5 for explicit enumeration.
  - **Made the non-Ore Kostochka–Yancey surplus a mandatory R1a SAT/CEGAR
    constraint:** the edge-count lower bound built into the CP/SAT model is
    the non-Ore KY bound at each residual order.
  - **Demoted unrestricted Track A** to "subfamily certification +
    counterexample hunt" per the Role 3/4/5/6 compute-team consensus;
    "close $t = 25$" is no longer the 12-month target.
  - **Promoted R5a** (re-derive FPS Claim 3.7 with Case 2b isolated) as the
    main 12-month theorem target: the highest-leverage local calculation in
    the whole plan, with publishable / stretch / dream tiers at $c < 9/16$,
    $11/20$, $1/2$.
  - **Tractability rescored.** Closure of $t = 25, 26$ stays at $2/10$ but
    is no longer the headline deliverable; the R5a target is scored
    separately at $3/10$. Full conjecture remains $1/10$.

- **v3** (2026-05-16): substantive rewrite after the v2 review.
  Major changes:
  - **Proof-direction logic for $\operatorname{cr}(K_t)$ fixed.** v2 said a *lower*
    bound $L(t) \le \operatorname{cr}(K_t)$ could be plugged into the right-hand side
    of Albertson. That is backwards. To *prove* Albertson one needs $\operatorname{cr}(G)
    \ge U(t)$ for an *upper* bound $U(t) \ge \operatorname{cr}(K_t)$ (so $Z(t)$ works
    because $\operatorname{cr}(K_t) \le Z(t)$). Lower bounds on $\operatorname{cr}(K_t)$
    are useful for *falsification*. The "subtle reading issue" section and Obstruction
    O2 are rewritten; the asymptotic $\sim 0.985 Z(t)$ figure has been moved into the
    falsification side throughout.
  - **$Z(25)$ corrected** from $4{,}050$ to $4{,}356$ (the v2 figure was a transcription
    error). Verified: $Z(25) = \tfrac14 \cdot 12 \cdot 12 \cdot 11 \cdot 11 = 4356$.
    Also recorded $Z(24) = 3630$, $Z(26) = 5148$. P3, C2, C3, C6 all updated.
  - **Asymptotic vs. finite separation.** Balogh–Lidický–Salazar (arXiv:1711.08958)
    prove $\operatorname{cr}(K_n) / H(n) \to c$ with $c \ge 0.98559895$ *asymptotically*;
    this is **not** a certified finite lower bound on $\operatorname{cr}(K_{25})$ or
    $\operatorname{cr}(K_{26})$. v2 used $0.985 \cdot Z(t)$ as if it were an operational
    finite threshold; this has been removed. The only finite certified lower bound on
    $\operatorname{cr}(K_n)$ for $n$ in the open range is what is recorded in the
    literature for that specific $n$ (e.g. exact computer-assisted values where known,
    or the proven small-$n$ values from Pan–Richter). The de Klerk et al. $0.83$
    asymptotic constant is also asymptotic; do not use it for finite certification
    without extracting the explicit constants from the source.
  - **ACF arXiv ID corrected** from `0909.2945` (an unrelated 2009 physics paper on
    iron-pnictide superconductors) to **`1006.3783`**, and the journal venue from
    EJC 17 (2010) R67 to **EJC 16(1) (2009), Research Paper 45**. This is the original
    Albertson–Cranston–Fox paper. Revision history v2 quoted the wrong ID.
  - **Cranston $1.212r$ vs. $1.228r$ distinction restored.** v2 rejected this reviewer
    correction; v2 was wrong. Cranston's Theorem 1 (headline) gives the range
    $1.212\,r \le |G| \le 1.768\,r$ as exclusion zone; the body Theorem 4 proves the
    cleaner $1.228\,r \le |G| \le 1.768\,r$. The two layers are both real, and the plan
    now records them as distinct.
  - **Finite Fox–Pach–Suk threshold disambiguated.** The arXiv Theorem 1.2(i) inequality
    $n < 1.4k - 0.6$ gives $n \le 34$ for $k = 25$ and $n \le 35$ for $k = 26$. The
    SoCG abstract phrases the same result as "$\le 1.4(k-1)$ vertices", which gives
    $n \le 33$ for $k = 25$ and $n \le 35$ for $k = 26$. v2 blended these. v3 cites
    both forms explicitly. The residual orders $48, 50, 51$ remain far above either
    threshold, so this does not change R1.
  - **Vertex-connectivity claim in R1b removed.** v2 said $25$-critical graphs have
    vertex-connectivity $\ge 24$ "forced". This is false: $t$-critical graphs do have
    $\delta \ge t - 1$ (Dirac) and a sharpening to $(t-1)$-*edge*-connectivity holds
    (Dirac 1953 — see v4 attribution fix above), but vertex connectivity is *not* in
    general forced to $t - 1$ (critical graphs can have small vertex cuts). R1b now
    lists vertex-connectivity as a genuine optional structural restriction.
  - **R1c heuristic discard rule corrected.** v2 said to discard $G$ whose heuristic
    upper bound $\overline{\operatorname{cr}}(G) \ge Z(25)$. This is invalid: a
    heuristic upper bound that is large says nothing about the actual crossing number.
    Valid discard rules require a *certified lower bound* on $\operatorname{cr}(G)$.
    R1c is rewritten so heuristic upper bounds are used only to *flag candidates* for
    further exact-bound investigation, never as eliminations.
  - **Hadwiger-conditional flag added to R3.** v2 claimed $K_{t-1}$-minor-free graphs
    are vacuous at threshold $t$ "by Hadwiger" — but Hadwiger is open in this range.
    The bullet is rephrased: conditional on Hadwiger this class is vacuous; otherwise
    it requires restriction to ranges where Hadwiger is proven ($t \le 6$).
  - **Kneser chromatic number fixed.** v2 listed $K(2t-1, t-1)$ as a sparse $t$-chromatic
    family; Lovász's formula gives $\chi(K(2t-1, t-1)) = (2t-1) - 2(t-1) + 2 = 3$, so
    this is 3-chromatic, not $t$-chromatic. The correct $t$-chromatic Kneser family is
    $K(2k + t - 2,\, k)$. Route R4 and C5 updated.
  - **Mycielski prediction rephrased.** v2 said Mycielski graphs are "exponentially
    sparse in vertices for their chromatic number" — wrong phrasing; iterated Mycielski
    graphs have *exponentially many vertices* in $\chi$ (so they are sparse per chromatic
    number in a different sense). P2 is restated as a heuristic conjecture to test, not
    an asymptotic fact.
  - **Tractability scores unchanged** (full conjecture $1/10$, $t = 25, 26$ closure
    $2/10$, structural sub-result $3/10$). The reviewer endorsed the v2 scores; the
    factual corrections in v3 do not push them in either direction.

- **v2** (2026-05-16): substantive rewrite after the v1 review.
  Major changes:
  - Cranston's residual window for $t \in \{25, 26\}$ is **not** an interval to be
    extracted — Cranston's Theorem 2 already pins it to the three exact pairs
    $(t,|G|) \in \{(25,48),\,(26,50),\,(26,51)\}$. Route R1, Steps 1, 3–6, the C1
    script and prediction P1 are rewritten against these three specific orders.
  - The Fox–Pach–Suk bound is two-tier: $n < 1.4k - 0.6$ (arXiv version, all $k$)
    and $n < (1.64 - \varepsilon)k$ (arXiv version, $k$ sufficiently large per Cranston
    $\gtrsim 2^{70}$). The plan now uses $1.4(k-1)$ for the finite cases relevant to
    $t = 25, 26$ and quotes $(1.64 - o(1))k$ only as the asymptotic statement.
  - The "weak immersion $\Rightarrow \operatorname{cr}(G) \ge \operatorname{cr}(K_k)$"
    line in v1 was wrong. Fox–Pach–Suk actually prove a two-stage deduction: a
    near-immersion bound $\operatorname{cr}(G') \ge \operatorname{cr}(K_r) - r^3/2$ plus
    at least $r^3/2$ extra crossings recovered from $E(G) \setminus E(G')$. The
    Fox–Pach–Suk bullet, Obstruction O3, C7, and the counterexample-anatomy section are
    rewritten accordingly.
  - Crossing Lemma constant updated from Ackerman's $1/29$ (for $|E| \ge 7|V|$) to
    Bungener–Kaufmann's $1/27.48$ (constant verified; threshold quoted as $6.95|V|$ by
    Cranston, but the BK abstract gives $6.77|V|$ — see the v4 qualification note in
    the Background section).
  - Cranston's exclusion zones written in their sharper body form $|G| \ge 2.8118 r$
    and $1.228 r \le |G| \le 1.768 r$, with the Ackerman $3.03 r$ and Barát–Tóth
    $3.57 r$ intermediates now in the chain.
  - de Klerk SDP constant corrected from the guessed $0.8594 / 0.86$ to the proven
    $0.83$ (arXiv:math/0404142); the state-of-the-art $\sim 0.985$ figure quoted by
    Cranston is recorded as the operational benchmark, with the reference to be
    extracted from Cranston [4].
  - Route R1 is demoted: brute `nauty` enumeration of $25$-critical graphs on 48
    vertices with $\delta \ge 24$ has zero chance of terminating. R1 is recast as a
    SAT/CEGAR-style search or as a *structurally restricted* sub-enumeration, and is
    no longer the recommended top-line target without that restriction.
  - Added the **Hajós lineage** subsection: Catlin (1979) refuted Hajós for $t \ge 7$
    and Erdős–Fajtlowicz showed almost all graphs are counterexamples; Lescure–Meyniel
    is precisely the weak-immersion weakening that survives Catlin.
  - Added the $\operatorname{cr}(K_t)$-vs-$Z(t)$ practical consequence (since corrected
    in v3): discard candidates against the best known *lower* bound on
    $\operatorname{cr}(K_t)$ for falsification, not for positive proof.
  - Route R5 is sharpened: the concrete handle is the chromatic-index lemma (Lemma
    2.3 of arXiv:2510.05893), where pushing $9/16$ further down is the actual lever.
  - Tractability for the "definite sub-slice" lowered from $3/10$ to $2/10$ for
    closing $t = 25, 26$; $3/10$ is retained for a structural sub-result via R3.
  - Added the missing-angle subsection: crossing-number variants (rectilinear, pair,
    odd, $k$-planar), Schaefer's catalogue, fractional / list / DP-chromatic
    Albertson, and crossing-Lemma improvements for graphs of given minimum degree.
  - Misc: added arXiv ID for ACF (the v2 entry quoted $0909.2945$, corrected in v3 to
    $1006.3783$); attributed minimum-degree result to Dirac (1952); renamed scripts
    to match the target object; added Pan–Richter citation. Acknowledged the
    reviewer's quote of Cranston's wording on the immersion bound for the new
    "1.768r" framing.

- **v1**: original draft (2026-05-16). A serious survey of the Albertson landscape,
  but drafted from arXiv abstracts only; several numerical claims and one structural
  argument were materially off.

## The conjecture (verbatim)

> **Conjecture (Albertson, 2007).** Every graph $G$ with $\chi(G) \ge t$ satisfies
> $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$.

Notation. $\chi(G)$ is the chromatic number; $\operatorname{cr}(G)$ is the (planar) crossing
number — the minimum number of edge crossings in any drawing of $G$ in the plane. The
conjectured exact value of $\operatorname{cr}(K_t)$ is the Guy/Zarankiewicz quantity
$$Z(t) \;:=\; \frac14\Bigl\lfloor\frac{t}{2}\Bigr\rfloor
                  \Bigl\lfloor\frac{t-1}{2}\Bigr\rfloor
                  \Bigl\lfloor\frac{t-2}{2}\Bigr\rfloor
                  \Bigl\lfloor\frac{t-3}{2}\Bigr\rfloor,$$
which is the best known *upper* bound for $\operatorname{cr}(K_t)$ and is proven to equal
$\operatorname{cr}(K_t)$ for $t \le 12$ (Pan–Richter 2007 for $t = 11, 12$; Guy/Saaty for
$t \le 10$ with refinements by McQuillan–Richter and others). For $t \ge 13$ the
*equality* $\operatorname{cr}(K_t) = Z(t)$ is open.

Useful exact values: $Z(11) = 100$, $Z(12) = 150$, $Z(24) = 3630$, $Z(25) = 4356$,
$Z(26) = 5148$.

### A subtle reading issue (corrected in v3 — must be settled before any claim)

The literature consistently treats the conjecture as
$\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$, where the right-hand side is the
**actual** crossing number. Because $\operatorname{cr}(K_t) \le Z(t)$, any inequality
proved against the conjectured value $Z(t)$ is *stronger* than what Albertson asks for.
The progress papers (ACF, Barát–Tóth, Ackerman, Cranston) verify Albertson by separately
proving $\operatorname{cr}(G) \ge Z(t) \ge \operatorname{cr}(K_t)$ in the relevant ranges,
so the distinction never bites in their proofs for $t \le 24$.

The two directions cut **asymmetrically** with respect to upper and lower bounds on
$\operatorname{cr}(K_t)$:

- **To *prove* Albertson** for a new $t$, one needs $\operatorname{cr}(G) \ge U(t)$ for
  some $U(t)$ satisfying $U(t) \ge \operatorname{cr}(K_t)$, i.e. an **upper** bound on
  $\operatorname{cr}(K_t)$. The Hill–Zarankiewicz value $Z(t)$ is exactly such an upper
  bound (it is the count of crossings in a known drawing of $K_t$), so proving the
  strong form $\operatorname{cr}(G) \ge Z(t)$ implies Albertson. Lower bounds on
  $\operatorname{cr}(K_t)$ are **not** useful for a positive proof — proving
  $\operatorname{cr}(G) \ge L(t)$ where $L(t) \le \operatorname{cr}(K_t)$ is a *weaker*
  conclusion than Albertson, not a stronger one. (v2 stated this backwards; v3 corrects.)
- **To *falsify* Albertson**, one needs $\overline{\operatorname{cr}}(G) <
  \operatorname{cr}(K_t)$. Since $\operatorname{cr}(K_t)$ is itself unknown for
  $t \ge 13$, an upper bound $\overline{\operatorname{cr}}(G) < Z(t)$ does **not**
  falsify Albertson — only the *strong form* $\operatorname{cr}(G) \ge Z(t)$. To
  falsify Albertson one must exhibit $\overline{\operatorname{cr}}(G) <
  \underline{\operatorname{cr}}(K_t)$ for the best known *lower* bound on
  $\operatorname{cr}(K_t)$. **This is where lower bounds on $\operatorname{cr}(K_t)$
  enter.** Per Balogh–Lidický–Salazar (arXiv:1711.08958, SIAM J. Discrete Math. 33
  (2019)), the *asymptotic* ratio satisfies $\liminf_{n} \operatorname{cr}(K_n)/Z(n)
  \ge 0.98559895$; this is **not** a certified finite lower bound on
  $\operatorname{cr}(K_{25})$ or $\operatorname{cr}(K_{26})$. For finite $t$ in the
  open range, one must use either an exact value (where one is known) or a finite
  certified lower bound extracted from the source — the asymptotic constant alone
  does not certify any single $t$.

The cleanest operational rules, both used in the plan below:

- **Positive proof at finite $t$:** target $\operatorname{cr}(G) \ge Z(t)$. This both
  proves Albertson and proves the strong form, and matches the progress papers.
- **Falsification at finite $t$:** target $\overline{\operatorname{cr}}(G) <
  \underline{L}(t)$ where $\underline{L}(t)$ is a *finite, certified* lower bound on
  $\operatorname{cr}(K_t)$ — not an extrapolation of an asymptotic constant.

## Honest tractability verdict (rescored in v4)

| target | v3 | v4 | reasoning |
|---|---|---|---|
| Full conjecture | $1/10$ | $1/10$ | 19 years open, no new technique on the horizon. |
| Close $t = 25, 26$ (unrestricted) | $2/10$ | $2/10$ | Now demoted from headline deliverable — see Track A rewrite. |
| Structural sub-result via R3 | $3/10$ | $3/10$ | Unchanged. |
| **R5a — re-derive FPS Claim 3.7 with Case 2b isolated** | n/a | $3/10$ | New v4 target. Local, well-scoped, calibrated against a known calculation. |
| Sub-family certification at a Cranston residual (Track A demoted) | n/a | $3/10$ | Realistic 12-month win: rule out counterexamples in a named family. |

The conjecture is 19 years old, has resisted every major crossing-number toolkit, and
the last decade of progress has incrementally pushed $t$ by one or two at a time using
global edge counts plus the Crossing Lemma. The constants chain
$$4r \;\to\; 3.57r \;\to\; 3.03r \;\to\; 2.8118r$$
(ACF 2009 $\to$ Barát–Tóth 2009 $\to$ Ackerman 2019 $\to$ Cranston 2025) is *itself*
evidence for Obstruction O1: one constant improvement per paper, no new technique.
Reasons:

- The "easy direction" — for a $t$-chromatic graph with minimum degree $\ge t-1$ apply
  the Crossing Lemma — yields a bound of the form $\operatorname{cr}(G) \ge c \cdot t^4$,
  but $\operatorname{cr}(K_t)$ is itself of order $t^4/64$. Whether the constants line
  up is a delicate fight, and that fight is exactly what has been refined for fifteen
  years to push from $t \le 12$ to $t \le 24$.
- The conjecture has *no slack* for small $t$: $\operatorname{cr}(K_5) = 1$,
  $\operatorname{cr}(K_6) = 3$, and the small cases are checked by hand. Where slack
  appears (the asymptotic regime $t \to \infty$), it is precisely the regime where the
  proven Crossing Lemma constants are too weak.
- The conjecture might be **false**. A counterexample is a graph $G$ with $\chi(G) = t$
  and $\operatorname{cr}(G) < \operatorname{cr}(K_t)$. Cranston (Dec 2025) rules out
  counterexamples in a wide range of orders for the open $t$, but every excluded order
  range was previously a candidate; the *next* unsearched range could contain one.
- Cranston's bounds (see below) reduce the open counterexample question for $t = 25, 26$
  to a finite computational problem with exactly **three** unknown $(t, |G|)$ pairs.
  Brute enumeration is infeasible at those orders; the "tractable slice" is structurally
  restricted or SAT-encoded sub-search, not a full enumeration.

The value of this plan is in mapping the terrain, ranking realistic structural
sub-targets (R5a, R2c, R3), and identifying a falsifiable computational *sub-family*
target (Track A demoted) at the three Cranston-residual orders.

## Hajós lineage (added in v2)

Albertson sits in a chain of structural conjectures relating chromatic number to a
$K_t$-substructure:

- **Hadwiger (1943, open).** $\chi(G) \ge t \Rightarrow G$ has $K_t$ as a minor.
- **Hajós (1961, refuted).** $\chi(G) \ge t \Rightarrow G$ has $K_t$ as a subdivision.
  Catlin (1979) gave counterexamples for every $t \ge 7$, and Erdős–Fajtlowicz (1981)
  showed that almost every graph is a counterexample.
- **Lescure–Meyniel (1989, weak immersion).** $\chi(G) \ge t \Rightarrow G$ has $K_t$
  as a *weak immersion* (i.e. $t$ vertices pairwise joined by edge-disjoint paths,
  paths allowed to share internal vertices). This is the post-Catlin weakening of
  Hajós: subdivision ($\to$ paths internally vertex-disjoint) is replaced by weak
  immersion ($\to$ paths only edge-disjoint). Open in general; proved by Fox–Pach–Suk
  for $|V(G)| < 1.4k - 0.6$ unconditionally (arXiv Theorem 1.2(i)), and for
  $|V(G)| \le (1.64 - o(1))k$ for $k$ sufficiently large in the arXiv version
  (Theorem 1.2(ii)).
- **Albertson (2007).** $\chi(G) \ge t \Rightarrow \operatorname{cr}(G) \ge
  \operatorname{cr}(K_t)$. Substitutes the structural "contains $K_t$ in some sense"
  with a metric "crosses at least as much as $K_t$".

The Hajós refutation matters here for two reasons:

1. The *stronger* structural conjecture (Hajós) fails badly. The fact that
   Lescure–Meyniel — the *weakest* surviving structural form — remains open and is
   regarded as comparable in difficulty to Hadwiger should temper any optimism about
   resolving Albertson via Routes R3 / R5 that would implicitly need full
   Lescure–Meyniel.
2. The Fox–Pach–Suk argument *is* a partial Lescure–Meyniel result combined with a
   crossing recovery; both ingredients are necessary, and a Lescure–Meyniel proof
   alone would not suffice to close Albertson (see Obstruction O3 below for why).

## Background and what is easy / known

Throughout, $G$ is a graph with $\chi(G) \ge t$, and a *minimum counterexample* (MCE) is
such a $G$ minimizing $|V(G)|$ subject to $\operatorname{cr}(G) < \operatorname{cr}(K_t)$.
Standard reductions:

- **Criticality.** An MCE is $t$-critical: $\chi(G - v) < t$ for every $v$. So $G$ has
  minimum degree $\delta(G) \ge t - 1$ (Dirac 1952).
- **Connectivity (attribution fixed in v4).** An MCE is 2-connected; moreover it is
  $(t-1)$-edge-connected by **Dirac (1953)** — the original
  $(t-1)$-edge-connectivity theorem for $t$-critical graphs. v3 attributed this
  to Kostochka–Stiebitz, which was wrong: Kostochka–Stiebitz belongs in the
  sparse-critical-graph **edge-density** chain (and contributes to the
  Kostochka–Yancey bound below), not as the source of edge-connectivity. Vertex
  connectivity of $t$-critical graphs is **not** in general forced to $t - 1$ —
  critical graphs can have small vertex cuts (Kostochka–Yancey $k$-Ore graphs are
  the standard witness, with $\kappa = 2$).
- **Edge count (trivial form).** $|E(G)| \ge \frac{t-1}{2}|V(G)|$ (a direct
  consequence of $\delta \ge t-1$).
- **Edge count (Kostochka–Yancey, added in v4).** Kostochka–Yancey (arXiv:1209.1050)
  prove a strictly stronger edge-density bound for $k$-critical graphs, with the
  bound tight precisely on the $k$-Ore graphs. At the three Cranston residual
  orders this gives the numbers in the table below (audit-supplied, not
  independently re-derived in v4):

  | order $(t, n)$ | trivial $(t-1)n/2$ | KY bound | non-Ore strengthening |
  |---|---|---|---|
  | $(25, 48)$ | $576$ | $\ge 587$ | $\ge 588$ |
  | $(26, 50)$ | $625$ | $\ge 637$ | $\ge 638$ |
  | $(26, 51)$ | $638$ | $\ge 649$ | $\ge 650$ |

  The "non-Ore" column applies whenever $G$ is *not* a $k$-Ore graph; equality in
  the KY bound is achieved exactly on the Ore graphs, and Kostochka–Yancey prove
  a $+1$ surplus for the non-Ore case. This is real constraint mass for SAT/CEGAR
  (see R1a) — at $(25, 48)$, the trivial $576$-edge floor is twelve edges below
  the KY non-Ore floor of $588$, which substantially shrinks the SAT search space.
- **Crossing Lemma (Bungener–Kaufmann, cited by Cranston 2025 as Theorem A(ii)
  of arXiv:2512.08020; threshold qualified in v4).** For every graph with
  $|E(G)| \ge \alpha \cdot |V(G)|$ (with $\alpha$ as discussed below),
  $$\operatorname{cr}(G) \;\ge\; \frac{|E(G)|^3}{27.48\,|V(G)|^2}.$$
  The constant $1/27.48$ is settled. The threshold $\alpha$, however, has a
  cross-reference discrepancy:
  - The Bungener–Kaufmann arXiv abstract (arXiv:2409.01733) gives $\alpha = 6.77$
    (i.e. $m > 6.77 n$).
  - Cranston's body invokes $\alpha = 6.95$ as the operational threshold.
  Until the BK PDF is read in full and the precise theorem hypothesis is confirmed,
  v4 quotes both: the sharper $6.77|V|$ form from the BK abstract, and the
  $6.95|V|$ form Cranston actually uses. Operational reading: use the
  Cranston-style $6.95|V|$ as the safe gating threshold for any proof that
  cross-references Cranston, and only invoke $6.77|V|$ when the BK PDF has been
  confirmed to give that hypothesis directly. (Probabilistic-team memo
  `work/08_probabilistic/memo.md` flags this as Deliverable D1, 30-day ask.)
  This is a small but non-trivial improvement on Ackerman's $1/29$ for
  $|E| \ge 7|V|$ (arXiv:1509.01932, 2019), and it is what drives Cranston's
  $2.8118r$ exclusion. With $|E| > 4|V|$ the constant degrades further to
  roughly $1/64$.
- **Albertson–Cranston–Fox (ACF), 2009 (arXiv:1006.3783, EJC 16(1) (2009) R45).**
  Combining criticality, edge count, and the Crossing Lemma yields that an MCE has
  $|V(G)| \le 4t$. This is the original bound; Albertson was verified by hand for
  $t \le 12$ by exhausting small dense graphs. (v2 quoted the wrong arXiv ID and
  journal venue; v3 corrects.)
- **Barát–Tóth, 2009 (arXiv:0909.0413).** Sharpened the ACF chain to verify Albertson
  for $t \le 16$ and bound an MCE by $|V| \le 3.57\,t$.
- **Ackerman, 2015/2019 (arXiv:1509.01932).** Main result: a graph drawn in the plane
  with at most $4$ crossings per edge has at most $6|V|-12$ edges. Plugging this back
  into the ACF argument with the improved Crossing Lemma constant $c > 1/29$ extends
  Albertson to $t \le 18$, and improves the MCE bound to $|V| \le 3.03\,t$.
- **Fox–Pach–Suk, 2025 (arXiv:2510.05893, with conference version at SoCG 2025,
  LIPIcs.SoCG.2025.50).** Two-tier vertex bound for the weak immersion (Theorem 1.2):
  - **(i, arXiv form)** If $|V(G)| < 1.4\,k - 0.6$, then $G$ contains a weak
    immersion of $K_k$. Unconditional in $k$. For integer $n$: $k = 25$ gives
    $n < 34.4$, so $n \le 34$; $k = 26$ gives $n < 35.8$, so $n \le 35$.
  - **(i, SoCG abstract form)** The same theorem stated as "at most $1.4(k-1)$
    vertices" gives $n \le 33$ for $k = 25$ and $n \le 35$ for $k = 26$. These two
    forms differ by one at $k = 25$; v3 cites both to avoid the v2 blending.
  - **(ii)** For every $\varepsilon > 0$ and $k$ sufficiently large (Cranston reads
    "sufficiently large" as $k \gtrsim 2^{70}$, making (ii) useless for any finite $k$
    of computational interest), if $|V(G)| < (1.64 - \varepsilon)k$, then $G$ contains
    a weak immersion of $K_k$.

  The deduction "weak immersion $\Rightarrow$ Albertson" is *not* a one-line
  observation; see Obstruction O3 for the two-stage argument.

  For $t \in \{25, 26\}$ the relevant Fox–Pach–Suk bound is (i): under either form,
  the threshold is $\le 35$, while the residual orders $48, 50, 51$ are far above the
  threshold — precisely because (ii) does *not* apply at these $k$. The choice between
  the arXiv and SoCG forms does not change R1.
- **Cranston, 2025 (arXiv:2512.08020).** Two layers of exclusion:
  - **Theorem 1 (headline, abstract-level).** $|G| \ge 2.8118\,r$ is excluded for an
    MCE, and the middle range $1.212\,r \le |G| \le 1.768\,r$ is excluded.
  - **Body Theorem 3.** $|G| \ge 2.8118\,r$ excluded for an MCE when $r \ge 15$.
  - **Body Theorem 4.** $1.228\,r \le |G| \le 1.768\,r$ excluded for all $r$ in the
    open range. So the body theorem gives a *slightly larger* excluded interval than
    the headline (the headline cuts off at $1.212$, the body at $1.228$). The
    intervening band $1.212 r \le |G| < 1.228 r$ is excluded by Theorem 1 / other
    propositions but not by Theorem 4 alone. v2 collapsed these two layers; v3 restores
    them as distinct.
  - **Asymptotic tightening for very large $r$:** $1.10\,r \le |G| \le 1.768\,r$
    excluded for $r \ge 125{,}000$; $1.05\,r \le |G| \le 1.768\,r$ excluded for
    $r \ge 825{,}000$.
  - **Cranston Theorem 2 (the headline residual for finite $t$).** "Let $G$ be an
    $r$-critical graph. If $r \le 24$, then $\operatorname{cr}(G) \ge
    \operatorname{cr}(K_r)$. And if $r \le 26$ and $\operatorname{cr}(G) <
    \operatorname{cr}(K_r)$, then $(r, |G|) \in \{(25, 48),\, (26, 50),\, (26, 51)\}$."
    So the residual is **three exact $(t, n)$ pairs**, not a range.

### Ore-congruence subsection (added in v4)

The Ore composition $O(G_1, G_2)$ of two $k$-critical graphs $G_1, G_2 \in
\mathcal{O}_k$ of orders $n_1, n_2$ is itself $k$-critical and has order
$$|V(O(G_1, G_2))| \;=\; n_1 + n_2 - 1.$$
With base case $K_k \in \mathcal{O}_k$ at order $k \equiv 1 \pmod{k-1}$, induction on
the recursion preserves the congruence
$$|V(G)| \;\equiv\; 1 \pmod{k - 1} \qquad \text{for every } G \in \mathcal{O}_k.$$

(This is the standard Kostochka–Yancey / Ore-construction fact;
arXiv:1209.1050.)

Applied to the three Cranston residual orders:

- **$(25, 48)$.** $k - 1 = 24$. $48 \bmod 24 = 0 \ne 1$, so **no $25$-Ore graph
  exists on $48$ vertices.** The Role 2 memo claim that "the $25$-Ore family at
  $(25, 48)$ is essentially a single graph" is therefore *false*; the family is
  empty. All candidate MCEs at $(25, 48)$ are non-Ore, so the right structural
  lever at this corner is the non-Ore Kostochka–Yancey strengthening
  ($|E| \ge 588$).
- **$(26, 50)$.** $k - 1 = 25$. $50 \bmod 25 = 0 \ne 1$, so **no $26$-Ore graph
  exists on $50$ vertices.** Same conclusion: all candidates are non-Ore;
  $|E| \ge 638$.
- **$(26, 51)$.** $k - 1 = 25$. $51 \bmod 25 = 1$, so $51 \equiv 1 \pmod{25}$.
  **This is the only Cranston residual order where Ore graphs can exist.**

### The single Ore corner: $(26, 51)$

Because $51 = 26 + 26 - 1$ is the order of *one* Ore composition of two copies of
$K_{26}$, the $26$-Ore family on $51$ vertices is generated by such a composition.
The composition operation involves a choice of an edge in one copy and a vertex in
the other, modulo automorphism, so the number of non-isomorphic Ore compositions
$O(K_{26}, K_{26})$ on $51$ vertices is **plausibly small but needs explicit
enumeration** (do not assert "single"; the precise count was not independently
verified in v4 — Role 2's intuition is that this is a small set up to isomorphism,
but Role 2's matching claim at $(25, 48)$ was wrong, so it has to be checked).
This enumeration is **assigned to Role 5** (enumeration / canonical-form
specialist) as a concrete deliverable; see Step 1.5 below.

Note: the constraint is plus, not minus. Even at $(26, 51)$, a candidate MCE
need not be Ore — it could also be non-Ore. The KY non-Ore bound $|E| \ge 650$
applies to those; the $|E| \ge 649$ Ore-equality bound applies to the (small,
enumerable) Ore corner. The SAT/CEGAR encoding in R1a uses the non-Ore floor
$|E| \ge 650$ for the non-Ore part of the search and verifies the Ore part by
explicit enumeration.

Easy positive cases (no real content):

- **Planar.** $\operatorname{cr}(G) = 0$ and $\chi(G) \le 4$ by the Four Colour Theorem
  (Appel–Haken), so $t \le 4$ and $\operatorname{cr}(K_t) = 0$. $\checkmark$
- **$1$-planar.** $\chi(G) \le 7$ (Borodin) and $\operatorname{cr}(G) \le |E(G)|$;
  small-case checks give the conjecture for $t \le 7$. Not a new theorem here.
- **Line graphs / quasi-line.** Conjecturally tractable by Reed-style arguments; not
  pursued in this plan.

## The central obstruction(s)

There are three obstructions, each separately fatal.

**Obstruction O1 — the constant gap.** Every existing proof feeds the
criticality-plus-Crossing-Lemma calculation
$$\operatorname{cr}(G) \;\ge\; \frac{|E(G)|^3}{27.48\,|V(G)|^2}
   \;\ge\; \frac{(t-1)^3 |V(G)|}{27.48 \cdot 8}$$
into $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$. With $\operatorname{cr}(K_t)$ of
order $t^4/64$, the chain forces $|V(G)| \ge t/(\text{small constant})$ — exactly the lower
bound side of the Cranston window. The upper bound side (an MCE has few vertices) comes
from the same chain. To close *both* sides one needs a constant improvement that has not
materialized in 15 years. With the Crossing Lemma constant having moved from Pach–Tóth's
$1/64$ through $1/31.1$ (Pach–Radoičić–Tardos–Tóth 2006) to $1/29$ (Ackerman 2019) to
$1/27.48$ (Bungener–Kaufmann 2024), the *increments* have been steadily shrinking. Each
constant improvement translates into pushing Albertson by at most one or two values of
$t$.

**Obstruction O2 — the Zarankiewicz unknown (rewritten in v3).**
$\operatorname{cr}(K_t)$ is *itself* unknown for $t \ge 13$. The asymmetry between proving
and falsifying Albertson against this unknown (see "subtle reading issue") makes any
operational comparison sensitive to *which side* of the equality is invoked:

- **Positive proof:** target $\operatorname{cr}(G) \ge Z(t)$, the proven *upper* bound
  on $\operatorname{cr}(K_t)$. Every progress paper does this.
- **Falsification:** target $\overline{\operatorname{cr}}(G) < \underline{L}(t)$ for
  a finite certified *lower* bound $\underline{L}(t) \le \operatorname{cr}(K_t)$. The
  asymptotic ratio results (de Klerk et al. $\ge 0.83 \cdot Z(n)$; Balogh–Lidický–
  Salazar $\ge 0.98559895 \cdot Z(n)$ asymptotically) are **not** finite certificates.
  For falsification at finite $t \in \{25, 26\}$, one must extract an explicit finite
  lower bound from the literature (or compute one), and use only that.

The v2 plan repeatedly substituted $0.985 \cdot Z(t)$ as a finite operational threshold;
this has been removed in v3.

**Obstruction O3 — the structural / immersion gap.** Fox–Pach–Suk's argument is a
*two-stage* deduction, and the v1 plan misrepresented it. Quoting Cranston's Section 1
paraphrase:

> "[Fox–Pach–Suk] showed that if $G$ is $r$-critical and $|G| \le r(1.64 - o(1))$, then
> $G$ contains a weak immersion $G'$ of $K_r$. They proved that $\operatorname{cr}(G')
> \ge \operatorname{cr}(K_r) - r^3/2$ and found at least $r^3/2$ other crossings in
> $G - E(G')$."

The deduction is therefore: **(a)** find a weak $K_r$ immersion $G'$ in $G$; **(b)** bound
the crossing number of the *immersion subgraph* by $\operatorname{cr}(K_r) - r^3/2$
(weaker than $\operatorname{cr}(K_r)$); **(c)** recover the missing $r^3/2$ crossings
from the edges of $G$ that are *not* used by the immersion. Step (b) is non-trivial
because the edge-disjoint paths of the immersion can share vertices, so contracting them
does not yield a topological drawing of $K_r$. Step (c) is the technical heart of
Fox–Pach–Suk: bounding the count of "wasted" crossings outside the immersion subgraph.

The simplified $r^3/2$ language is appropriate only in the asymptotic
$|V(G)| < (1.64 - o(1))r$ regime; Cranston's Appendix A gives the more precise finite
form $\operatorname{cr}(G') \ge \operatorname{cr}(K_r) - n(n-r)(n+2r)/8$.

Consequences:

- The Lescure–Meyniel conjecture *taken alone* does **not** imply Albertson. The full
  Fox–Pach–Suk argument requires the second-stage crossing recovery; absent that, a
  weak immersion of $K_k$ in $G$ gives at best $\operatorname{cr}(G') \ge
  \operatorname{cr}(K_k) - O(k^3)$, which is the wrong order of magnitude in $k$
  (since $\operatorname{cr}(K_k) \sim k^4$).
- An "immersion witness" search (C7) is informative only in tandem with a bound on
  the extra crossings outside the immersion subgraph; finding a weak immersion of
  $K_t$ in a candidate $G$ does not by itself certify $G$ satisfies Albertson.
- Pushing the Fox–Pach–Suk vertex bound from $1.4(k - 1)$ to $1.768r$ (the Cranston
  upper-window cutoff) closes Cranston's window for *all sufficiently large* $t$
  unconditionally, but only if the second-stage crossing recovery continues to work
  in that wider range. The plan's Routes R5 / R5a address both stages.

## Two-track strategy (v4)

Per `work/01_principal_lead/INTEGRATION.md`, the team is split into two tracks
over a 12-month horizon. The split is not symmetric: Track B is the
higher-probability path for *some* publishable theorem.

- **Track A — subfamily certification + counterexample hunt.** No longer aims
  at closing $t = 25$ unrestricted. Aims at (i) explicit enumeration of the
  $(26, 51)$ Ore corner, (ii) SAT/CEGAR refutation of named non-Ore
  sub-families at $(25, 48), (26, 50), (26, 51)$, (iii) heuristic
  counterexample sweeps with rigorous lower-bound discard (R1c). 12-month
  goal: a paper of the form "Albertson holds on the class $\mathcal{C}$ at
  the Cranston residual orders" for some explicit named $\mathcal{C}$, plus
  the Ore-corner verdict at $(26, 51)$. Owned by Roles 2, 3, 4, 5, 6.
- **Track B — structural / asymptotic.** Owns the actual mathematical
  sub-targets R2c, R3, R5, **R5a**. 12-month goal: at least one of R2c, R5a,
  R3.6 ships as a draft publishable on its own. R5a is the headline target;
  R2c is the fallback. Owned by Roles 7, 8 (with Role 9 secondary).

## Candidate attack routes, ranked by realism (v4)

Each route is marked **proven / plausible / speculative**.

### Route R1 — Track A: subfamily certification at the three Cranston-residual orders (v4 demotion)

Cranston's Theorem 2 pins the residual MCE possibilities to
$(t,|G|) \in \{(25, 48),\, (26, 50),\, (26, 51)\}$. The v3 framing "close $t = 25, 26$"
is withdrawn in v4: the compute-team consensus across Roles 3, 4, 5, 6 is that
unrestricted closure is **not a 12-month target** and is not even a responsible
compute target without a structural coverage theorem. SAT, enumeration, and exact
crossing-number certification at $n \approx 50, m \approx 600$ are all too large.
The v4 Track A target is therefore *subfamily certification + counterexample hunt*,
not closure.

The computational problem at each order:

- For $t = 25$, the family of $25$-critical graphs on exactly $48$ vertices with
  $\delta \ge 24$ and $|E| \ge 588$ (non-Ore KY) — there are no Ore candidates
  (Ore-congruence section above).
- For $t = 26, n = 50$, the family with $\delta \ge 25$ and $|E| \ge 638$ (non-Ore KY)
  — again, no Ore candidates.
- For $t = 26, n = 51$, the family with $\delta \ge 25$, split into:
  - *Non-Ore part:* $|E| \ge 650$.
  - *Ore part:* the (plausibly small, needs explicit enumeration) family of Ore
    compositions $O(K_{26}, K_{26})$ on $51$ vertices.

Brute `nauty` enumeration is infeasible. The three honest paths forward, all
sub-family targets:

1. **R1a (SAT / CEGAR; v4 mandatory KY constraint).** Encode
   $\{\delta \ge t-1,\;t\text{-critical},\;(t-1)\text{-edge-connected (Dirac
   1953)},\;|E| \ge \text{KY-non-Ore floor},\;
   \overline{\operatorname{cr}}(G) < Z(t)\}$ as a CDCL-friendly SAT/CP instance,
   with the crossing-number bound as the CEGAR refinement loop. **The edge-count
   lower bound built into the SAT model must be the non-Ore Kostochka–Yancey
   bound at each residual order** ($\ge 588, 638, 650$), not the trivial
   $(t-1)n/2$ floor. This is a mandatory v4 constraint: it removes 12, 13, and
   12 edges' worth of solution candidates at $(25, 48), (26, 50), (26, 51)$
   respectively, which compounds with the criticality clauses. Adding it post-hoc
   as a CEGAR refinement is wasteful — bake it in.

   The criticality constraint is the hardest to encode (a $\forall v$ over
   $\chi(G - v)$ certificates); the practical workaround is to encode "contains
   a specified $t$-critical subgraph as spanning" and iterate over plausible
   $t$-critical kernels (e.g., $K_{t-1}$-cores plus small gadgets). State of the
   art for crossing-number SAT on $n \sim 50, m \sim 600$ is at or beyond the
   boundary; this would itself be a publishable engineering effort even without
   a verdict on Albertson. **Track A scope:** prove non-existence within a
   specific named sub-family (e.g. graphs with a fixed $K_{24}$-core in a fixed
   position) and report exactly the fraction of the residual MCE space that
   sub-family covers.

2. **R1b (structural restriction).** Restrict to a sub-family of $t$-critical
   graphs at the residual orders that admits efficient generation. Candidate
   restrictions:
   - graphs containing $K_{t-1}$ as a subgraph (forces an "outside" set whose
     adjacency to the $K_{t-1}$ is highly constrained);
   - graphs obtained from $K_t$ by edge-deleting and vertex-identifying
     ("blow-down" graphs) — a natural candidate counterexample family;
   - graphs with **edge-connectivity** equal to $t - 1$ (forced by Dirac 1953);
     and, *as a genuine optional restriction* (not forced), graphs with
     vertex-connectivity exactly $t - 1$;
   - graphs containing two disjoint copies of $K_{12}$ joined by a specified
     bipartite structure (mimicking a "doubled half" of $K_{25}$);
   - **Ore compositions of $K_{26}$ at $(26, 51)$** (added in v4, the only Ore
     residual; assigned to Role 5).

   Each restriction covers a *fraction* of the residual MCE space, and that
   fraction must be made explicit. R1b is honest about being a sub-family
   result: it does *not* close the conjecture.

3. **R1c (heuristic + lower-bound discard, no enumeration).** Generate random
   $t$-critical graphs at the residual orders. For each candidate $G$:
   - Compute a heuristic *upper* bound $\overline{\operatorname{cr}}(G)$ via
     planarisation (OGDF). Use this only to *flag* $G$ as a candidate worth
     deeper investigation, **never as an elimination**.
   - Compute a *certified lower* bound $\underline{\operatorname{cr}}(G)$ via
     the ILP of Buchheim–Chimani or the SAT encoding of Chimani–Mutzel.
     **Discard** $G$ as not a counterexample if
     $\underline{\operatorname{cr}}(G) \ge Z(t)$ (proving the strong form for
     that $G$). This is the only valid elimination.
   - Flag $G$ for further work if $\overline{\operatorname{cr}}(G) <
     \underline{L}(t)$ for the finite certified lower bound on
     $\operatorname{cr}(K_t)$. Such $G$ are candidate counterexamples.

   This cannot close $t = 25$ in either direction by itself, but it can
   falsify Albertson if a candidate counterexample survives the lower-bound
   squeeze against a finite certified $\underline{L}(t)$.

**Falsifiable target.** Track A is now scoped as: (a) explicit enumeration of
the Ore corner at $(26, 51)$ and verdict on whether any of those Ore graphs
violate Albertson (R1b for the Ore-restricted family); (b) SAT/CEGAR
non-existence proof within one named non-Ore sub-family at each residual
order; (c) counterexample hunt via R1c. 12-month upside: a sub-family paper
plus the Ore-corner verdict. Closure of the unrestricted conjecture is not
on the 12-month horizon (compute-team consensus, `work/01_principal_lead/INTEGRATION.md`).

### Route R2 — sharpen the Crossing Lemma constant on critical graphs (plausible)

Bungener–Kaufmann's $1/27.48$ bound (cited above, with the $6.77$ vs $6.95$
threshold qualification) holds for *all* graphs with $|E| \ge \alpha|V|$. For
$t$-critical graphs there is more structure: minimum degree $\ge t - 1$, the KY
non-Ore edge surplus, and a stronger edge density than the Crossing Lemma assumes.
A targeted constant improvement *for the family of $t$-critical graphs* would
translate directly into pushing Albertson by one or two more $t$. Three concrete
sub-targets:

1. **R2a.** For $t$-critical graphs with $|E| \ge \alpha t |V|$, prove
   $\operatorname{cr}(G) \ge c'(\alpha) \cdot |E|^3/|V|^2$ with
   $c'(\alpha) > 1/27.48$. The Crossing Lemma proof via random sampling has slack
   exactly when the graph has minimum degree well above the lemma's threshold.
2. **R2b.** Refine Ackerman's $6|V|-12$ bound on $\le 4$-crossings-per-edge
   drawings to *critical* graphs.
3. **R2c (added in v2, sharpened in v4).** Improve the Crossing Lemma for graphs
   with **minimum degree $\ge \delta_0$**. Pach–Tóth and follow-ups have
   minimum-degree-aware versions; with $\delta_0 = t - 1$ the relevant family is
   exactly $t$-critical graphs. The probabilistic-team memo
   (`work/08_probabilistic/memo.md`) records a commitment target of pushing
   $2.8118t \to 2.5t$ for $t$-critical graphs via a min-degree-aware refinement,
   or $2.8118t \to 2.7t$ as a generic Crossing-Lemma improvement.

**Status.** Plausible. The random-sampling proof of the Crossing Lemma has known
slack, and there is now a sequence of *four* published constant improvements
(Pach–Tóth 1997, Pach–Radoičić–Tardos–Tóth 2006, Ackerman 2019, Bungener–Kaufmann
2024), each gaining at most a few percent. Realistic 6–12 month payoff: improve
the constant by another $\le 5\%$, push Albertson from $t \le 24$ to $t \le 25$
unconditionally, not "close two values".

### Route R3 — Albertson on a structural subclass (plausible)

Prove the conjecture unconditionally on a class $\mathcal{C}$ closed under taking
$t$-critical subgraphs. Candidate classes, with the specific reason each might (or might
not) work:

1. **$K_{t-1}$-minor-free graphs (Hadwiger-conditional; corrected in v3).** *Conditional
   on Hadwiger*, these have $\chi \le t - 1$, so Albertson is vacuous for them at
   threshold $t$. **Hadwiger is open** for $t \ge 7$, however, so unconditionally this
   bullet only gives a vacuous theorem in the small-$t$ range where Hadwiger is proven
   ($t \le 6$, Robertson–Seymour–Thomas for $t = 6$). For the open Albertson range
   $t \in \{19, \ldots, 26\}$, this is not a free theorem and cannot be cited as
   folklore. (v2 cited it as folklore; v3 corrects.) The contrapositive — *any MCE
   has a $K_{t-1}$ minor under Hadwiger* — remains a useful conditional structural
   handle, not a tool.
2. **Quasi-line graphs / line graphs.** Reed-style chromatic-number control plus the fact
   that line graphs of dense graphs inherit crossing-number lower bounds. The catch is
   that for $L(K_n)$ the crossing number is itself an open question, so the substitution
   is not trivial.
3. **Graphs with a $K_{t}$-immersion of bounded depth.** Strengthening of Fox–Pach–Suk:
   if the immersion paths have bounded length, the crossing recovery in stage (c) of
   Obstruction O3 is more controllable. This is the structural target most aligned with
   the Fox–Pach–Suk machinery.
4. **Joins and blow-ups of small chromatic graphs.** $\chi(G \vee H) = \chi(G) + \chi(H)$;
   $\operatorname{cr}$ behaves super-multiplicatively under joins for dense $G, H$. May
   yield exact equalities along the conjecture rather than strict inequalities — a useful
   sanity check that an attempted proof does not over-shoot.
5. **Apex / near-planar / $k$-planar classes (added in v2).** A graph with
   $\operatorname{cr}(G) \le c$ has $\chi(G) \le f(c)$ (Schaefer's *Crossing Number of
   Graphs*, CRC 2018). This ties chromatic number directly to crossing number and gives
   a non-trivial verification of Albertson for low-crossing classes — for instance,
   $1$-planar gives $t \le 7$ and Albertson is automatic in that range. Higher
   $k$-planar classes are an open direction.
6. **Fractional / list / DP-chromatic Albertson (added in v2).** Bernshteyn, Kostochka,
   and others have studied list-chromatic and DP-chromatic analogues of Hadwiger-style
   conjectures. A *fractional* Albertson result (replacing $\chi$ with $\chi_f$ or the
   list chromatic number) is plausible as a side-product of an R3 attack, and would be
   publishable on its own.
7. **$k$-Ore graphs at residual orders (added in v4).** A targeted theorem of the
   form "every $26$-Ore graph on $51$ vertices satisfies Albertson" is the
   minimal R3 sub-result triggered by the v4 Ore-congruence observation. Since
   the family is plausibly enumerable (Role 5 deliverable), this is a tractable
   sub-theorem rather than a research programme.

**Realism.** (3), (5), and (7) are the most directly aligned with current
technique; (6) is a publishable adjacency.

### Route R4 — search for a counterexample (speculative-but-non-zero)

The conjecture might be false. Concrete strategies:

1. **Random $t$-critical search at the Cranston residuals.** Focus C5-style heuristic
   bounds on the three pairs $(25, 48), (26, 50), (26, 51)$ where MCE existence is open.
   See R1c above.
2. **Adversarial drawings.** Take a known sparse $t$-chromatic graph (Mycielski $M_t$,
   Kneser / Schrijver graphs in the *correct* chromatic-$t$ parameter range, or a
   Borsuk-style hypergraph realization) and compute an upper bound on its crossing
   number heuristically. If any heuristic upper bound falls below a *finite, certified*
   lower bound on $\operatorname{cr}(K_t)$ for the corresponding $t$, that is a
   candidate counterexample to investigate rigorously. Most likely outcome: nothing.
3. **Kneser and Schrijver graphs (chromatic number corrected in v3).** By Lovász,
   $\chi(K(n, k)) = n - 2k + 2$. The correct chromatic-$t$ Kneser family is therefore
   $K(2k + t - 2,\, k)$ — for any $k \ge 1$, this gives a $t$-chromatic Kneser graph,
   with $k$ as a free sparsity parameter. (v2 listed $K(2t-1, t-1)$, which by the
   formula is $3$-chromatic regardless of $t$ — corrected.) Schrijver subgraphs
   $SG(n, k)$ inherit the same chromatic number while being vertex-critical. For
   chromatic-$25$ candidates, $K(25, 1) = K_{25}$ (uninteresting), $K(26, 2)$, $K(27,
   3)$, …, $K(2k + 23,\, k)$ for various $k$ are all candidate sparse $25$-chromatic
   graphs. Skoviera and others have handled specific small Kneser crossing-number
   cases; before running heuristics, those references should be checked. A
   computational upper bound is a falsifiable target.

**Status.** Speculative. The conjecture is widely believed; a counterexample would be a
major event. But the search cost is bounded and the payoff is unbounded, so a modest
computational allocation is justified.

### Route R5 — adapt Fox–Pach–Suk to handle larger $|V|$ (speculative)

Push the $1.4(k-1)$ unconditional bound (or the asymptotic $(1.64 - o(1))k$ bound) to
$\ge 1.768r$, which would close the Cranston window for all sufficiently large $t$.
This requires improving the *chromatic-index* lemma at the core of Fox–Pach–Suk:

- The $1.4(k-1)$ bound (Theorem 1.2(i) of arXiv:2510.05893) uses Shannon's classical
  $3\Delta/2$ chromatic-index bound for multigraphs (Lemma 2.2(i) of the same paper).
- The $(1.64 - o(1))k$ bound (Theorem 1.2(ii)) uses a careful refinement of the
  chromatic-index bound to a "$9/16$" leading constant in Lemma 2.3.

The concrete R5 lever is therefore: **improve Lemma 2.3 of arXiv:2510.05893 from
$9/16$ to something smaller.** This is a chromatic-index / multigraph edge-colouring
question, not a crossing-number question. Pushing $9/16 \to 1/2$ would close the upper
asymptotic constant from $1.64$ towards $2$; pushing further requires a Vizing-style
refinement that may be a problem in its own right.

In addition, R5 requires the second-stage crossing recovery (Obstruction O3 step (c))
to continue to give $\Theta(r^3)$ extra crossings as the vertex bound grows. The
crossing recovery in Fox–Pach–Suk is tied to the immersion structure and may not scale
without further work. v2 makes this a sub-target rather than a free corollary of
chromatic-index improvement.

### Route R5a — Re-derive FPS Claim 3.7 with Case 2b isolated (promoted to headline 12-month theorem target in v4)

**This is the highest-leverage local calculation in the whole plan.**

Per `work/07_immersion/memo.md` Section 1d, the $9/16$ in Lemma 2.3 of
arXiv:2510.05893 emerges from a deterministic optimisation in Claim 3.7 of the
FPS proof. The optimum is attained at $11/20 = 0.55$ on one branch and at
$9/16 = 0.5625$ on the other (the binding branch is "Case 2b"). Whether $9/16$
is a **real obstruction** (the binding case really is at $9/16$) or an
**artifact** of the case split (Case 2b can be handled differently and the
binding case is actually $11/20$, or $1/2$, or even better) is a local
chromatic-index / multigraph edge-colouring question that can be settled in a
self-contained re-derivation.

**Target.** Re-derive FPS Claim 3.7 with Case 2b isolated and treated by a
separate argument. Determine the *actual* binding constant.

**Tiered outcomes (do not oversell — this is the *highest-leverage* local
calculation, not a one-line corollary):**

- **Minimum publishable outcome.** Any $c < 9/16$. Even $c = 0.56$ would be
  publishable as a refinement of the FPS chromatic-index lemma and would
  push the FPS vertex threshold beyond $1.64k$, which would in turn push
  Albertson's unrestricted regime by one $t$ asymptotically.
- **Stretch outcome.** $c = 11/20 = 0.55$. This is exactly the
  "other branch" optimum of the FPS deterministic argument: if Case 2b can be
  bypassed, $11/20$ is the natural next constant. The Role 7 memo (Target T1
  in `work/07_immersion/memo.md`) gives the structural reason this is the
  realistic 12-month commitment, since Goldberg–Seymour-style chromatic-index
  refinements have headroom precisely at the multigraph edge-colouring step.
- **Dream outcome.** $c = 1/2$. This would close the FPS bound to
  $1 + (1 - 1/2) + (\text{FPS recovery slack}) \ge 1.5\,k + \varepsilon$, and
  combined with R2c would close the Cranston window asymptotically.
  Open-ended; the Role 7 memo describes this as a multi-year target.

**Framing (mandatory).** **The highest-leverage local calculation in the whole
plan.** Do not phrase it as "one careful re-derivation away" — it is *one
careful re-derivation away from a verdict on whether $9/16$ is real*, which is
not the same as "one careful re-derivation away from $c < 9/16$". The
re-derivation might confirm $9/16$ is binding, in which case the publishable
deliverable shrinks to "$9/16$ is the FPS lower bound, with Case 2b as the
obstructing case" — useful, but not a new headline. The Role 7 memo Target T1
estimates "high but not overwhelming" probability for $c < 9/16$ on a 12-month
horizon; Target T2 for $c < 1/2$ is 12–24 months; Target T3 is open-ended.

**Why R5a is the v4 headline target:**

1. **Local and self-contained.** Re-deriving one claim from one paper is a
   pen-and-paper job, not a research programme.
2. **Calibrated against a known calculation.** The FPS Claim 3.7 argument is
   explicit; any improvement is directly comparable to it.
3. **Strictly publishable at minimum.** Any $c < 9/16$ is a refinement of the
   FPS lemma, regardless of whether it closes Cranston's window.
4. **Compounds with R2c.** A min-degree-aware Crossing-Lemma improvement
   (R2c) and a smaller $c$ in FPS Lemma 2.3 (R5a) feed multiplicatively into
   the Cranston window closure for sufficiently large $t$.

**Owner.** Role 7 (immersion / chromatic-index specialist), per the Role 7
memo's commitment.

**Dependency on R5 (full).** R5a is a strict sub-target of R5. A successful
R5a gives the chromatic-index input; R5 still needs the crossing-recovery
input (Obstruction O3 stage (c)) to scale with the new vertex bound. A
successful R5a alone does *not* close Albertson; it is a calibration target
and a publishable refinement of the FPS toolkit.

## Computational subtasks (Python / SageMath / SAT)

These are the concrete things one could do in the next 1–6 months. Each is falsifiable.

1. **C1 — `scripts/cranston_residual.py`.** Hard-code the Cranston Theorem 2 residual
   triples $(25, 48), (26, 50), (26, 51)$. Compute the implied constraints for each:
   $\delta \ge t - 1$ (so $|E| \ge 576$ for $t = 25$; $|E| \ge 625$ for $t = 26, n =
   50$; $|E| \ge 638$ for $t = 26, n = 51$); the **KY non-Ore floor**
   ($|E| \ge 588, 638, 650$); the upper-end exclusion $|G| < 2.8118\,t$ (which
   $48 < 70.3$ and $50, 51 < 73.1$ both satisfy); and the Fox–Pach–Suk lower
   bound: both the arXiv form $1.4t - 0.6$ (giving $34, 35, 35$) and the SoCG
   form $1.4(t-1)$ (giving $33, 35, 35$), which $48, 50, 51$ all clear by a
   wide margin. Also record the Ore-congruence verdict per order
   ($(25, 48)$ none, $(26, 50)$ none, $(26, 51)$ Ore corner exists). Output:
   a structured spec of the search space for R1.
1.5. **C1.5 — `scripts/ore_corner_enumerate.py` (added in v4, Role 5).**
   Enumerate the $26$-Ore graphs on $51$ vertices: all Ore compositions
   $O(K_{26}, K_{26})$ up to isomorphism. Output: the explicit list (plausibly
   small — Role 2's claim of "single" at $(25, 48)$ was wrong, so do not
   pre-assert a count). For each, compute heuristic $\overline{\operatorname{cr}}$
   and certified $\underline{\operatorname{cr}}$ via C3. This is the
   Ore-corner subset of Track A.
2. **C2 — `scripts/sat_critical_search.py`.** Build a SAT encoding for
   "$t$-critical graph on $n$ vertices with $\delta \ge t - 1$ **and
   $|E| \ge$ KY-non-Ore floor** and $\overline{\operatorname{cr}}(G) < Z(t)$"
   — note the KY constraint is **mandatory at the encoding level**, not a CEGAR
   refinement. Use CEGAR with an OGDF-based crossing-number upper bound oracle.
   Falsifiable target: even at $n = 48$, the encoding should at least
   *terminate* on small structurally restricted sub-cases (e.g. graphs with a
   fixed $K_{24}$ subgraph in a fixed position); if it does not terminate even
   there, the SAT path is infeasible at scale.
3. **C3 — `scripts/cr_bounds_48v.py`.** For each candidate $G$ on the three
   Cranston residual orders, compute:
   - heuristic upper bound $\overline{\operatorname{cr}}(G)$ (OGDF / `pycrossings` / Sage);
   - certified lower bound $\underline{\operatorname{cr}}(G)$ (Buchheim–Chimani ILP or
     Chimani–Mutzel SAT).
   **Valid eliminations:** discard $G$ if $\underline{\operatorname{cr}}(G) \ge Z(t)$.
   **Invalid:** do **not** discard on a large $\overline{\operatorname{cr}}(G)$.
   Flag $G$ if $\overline{\operatorname{cr}}(G) < \underline{L}(t)$.
4. **C4 — `scripts/crossing_lemma_refinement.py`.** Numerical exploration of route R2:
   for random $t$-critical graphs at small $t$ ($t \le 20$), measure
   $\operatorname{cr}(G) / (|E|^3 / |V|^2)$ empirically and check whether the empirical
   constant is bounded away from $1/27.48$. If it is, R2 has empirical legs. Also
   stratify by $\delta(G)$ (R2c) and by spectral gap.
5. **C5 — `tests/mycielski_kneser_cr.py`.** Direct heuristic crossing-number bounds for
   Mycielskian $M_t$, Kneser $K(2k + t - 2,\, k)$, Schrijver $SG(2k + t - 2, k)$, and
   generalised Mycielskian families with $\chi = t$ for $t = 13, \ldots, 30$. Output:
   a table of $\overline{\operatorname{cr}}(G) / Z(t)$.
   **Heuristic predictions (to test, not asserted):**
   - For $t \le 30$, the iterated Mycielskian $M_t$ has $|V(M_t)|$ exponential in
     $t$ but a structure that *empirically* tends to produce large crossing numbers.
     The plausible conjecture to test is $\overline{\operatorname{cr}}(M_t) / Z(t) \to
     \infty$ as $t$ grows.
   - For $K(2k + t - 2,\, k)$ with $\chi = t$, the heuristic upper bound is expected
     to be comparable to $Z(t)$ to within a constant factor.
6. **C6 — `scripts/zarankiewicz_lower_bounds.py`.** For each $t \in \{13, \ldots, 26\}$
   maintain **two separate columns** in the output table:
   - **Finite certified lower bounds** on $\operatorname{cr}(K_t)$ for that specific
     $t$. This is the column to use for finite-$t$ falsification (R1c, C3).
   - **Asymptotic constants** for $\operatorname{cr}(K_n) / Z(n)$ (de Klerk et al.
     $\ge 0.83$; Balogh–Lidický–Salazar $\ge 0.98559895$). Both are *asymptotic*,
     and should be marked clearly as **not directly usable for finite-$t$
     certification**.
7. **C7 — `scripts/immersion_witness.py`.** For each candidate counterexample $G$ from
   C3, search for a $K_{\chi(G)}$ weak immersion $G'$ **and** estimate the number of
   crossings in $E(G) \setminus E(G')$. By Obstruction O3, a weak immersion alone is
   *not* a witness for Albertson; absence is not a falsification.
8. **C8 — `scripts/fps_claim37_recheck.py` (added in v4, supports R5a).** Symbolic
   re-derivation of FPS Claim 3.7 with Case 2b isolated. Use `sympy` to walk the
   deterministic optimisation case by case, and produce the exact constant on
   each branch. Falsifiable target: reproduce $9/16$ and $11/20$ on the two
   known branches, then test whether Case 2b admits an alternative case split.
   This is a small symbolic compute job, not a search problem.

## Numbered step-by-step plan (v4)

| # | Goal | Technique | Effort | Track | Status |
|---|------|-----------|--------|-------|--------|
| 1 | Verify Cranston Theorem 2 residual triples; record Dirac, KY (standard + non-Ore), Ore-congruence verdicts | Re-read arXiv:2512.08020 + arXiv:1209.1050 | 1 day | both | not started |
| 1.5 | Enumerate $26$-Ore graphs on $51$ vertices (Ore corner) | C1.5 + canonical-form library | 2 weeks | A | not started |
| 2 | Compile table: for each $t \in \{13, \ldots, 30\}$, $Z(t)$, finite certified $\operatorname{cr}(K_t)$ lower bounds, asymptotic constants, Cranston exclusion, FPS bound | Literature reading + small Python | 1 week | both | not started |
| 3 | Implement C1 + C2 (SAT skeleton with mandatory KY non-Ore constraint); test SAT termination on small sub-cases | SAT solver, OGDF crossing oracle | 4–8 weeks | A | not started |
| 4 | Implement C3 (heuristic + ILP/SAT crossing-number bounds at $n = 48, 50, 51$) | OGDF, Buchheim–Chimani ILP, Chimani–Mutzel SAT | 4–8 weeks | A | not started |
| 5 | Run R1a (SAT/CEGAR) within named non-Ore sub-families at $(25, 48), (26, 50), (26, 51)$; either eliminate the sub-family or output a flagged candidate counterexample | Compute cluster | open-ended | A | not started |
| 6 | Resolve the Ore corner at $(26, 51)$ via C3 on the C1.5 enumeration | C3 pipeline | 2–4 weeks | A | not started |
| 7 | Implement C5 with $K(2k + t - 2, k)$ Kneser family and Mycielski as heuristic conjecture to test | Sage graph library | 2–3 weeks | A | not started |
| 8 | **R5a:** re-derive FPS Claim 3.7 with Case 2b isolated; aim for $c < 9/16$ (publishable), $11/20$ (stretch), $1/2$ (dream) | Pen-and-paper + C8 symbolic check | 6–12 months | B | not started |
| 9 | R2c: min-degree-refined Crossing Lemma constant for $t$-critical graphs | Probabilistic / spectral random sampling refinement | 6–12 months | B | not started |
| 10 | If R5a or R2c ships: write up. R3 (esp. R3.3, R3.5, R3.7) as publishable fallback | Choice depends on R5a / R2c outcome | open-ended | B | not started |

Steps 1–2 are guaranteed deliverables (literature synthesis). Steps 1.5, 3–7 are a
Track A engineering programme with sub-family-restricted goals. Step 8 (R5a) is the
v4 headline mathematical target. Step 9 (R2c) is the Track B fallback. Step 10
is the publish-or-pivot decision point.

## What a counterexample would look like

A graph $G$ with $\chi(G) = t$ and $\operatorname{cr}(G) < \operatorname{cr}(K_t)$. From
the reductions above, the *smallest* such $G$ for $t \in \{25, 26\}$ has one of three
exact orders, $|V(G)| \in \{48, 50, 51\}$. Common features:

- minimum degree $\ge t - 1$ (so $\delta \ge 24$ at $t = 25$);
- $|E(G)| \ge$ KY non-Ore floor at the corresponding order ($588, 638, 650$ — the
  trivial $(t-1)n/2$ floor is now subsumed);
- 2-connected and $(t-1)$-edge-connected (Dirac 1953) — but **not** necessarily
  $(t-1)$-vertex-connected; $k$-Ore witnesses give $\kappa = 2$ even at high $\delta$;
- not equal to $K_t$ (which has $\operatorname{cr}(K_t)$ on the nose), and not a "blow-up"
  of $K_t$ (those preserve crossing-number lower bounds);
- at $(25, 48)$ and $(26, 50)$, the candidate is **not $k$-Ore** (Ore-congruence
  excludes it); at $(26, 51)$, the candidate could be Ore (in the small enumerable
  family from C1.5) or non-Ore;
- **either** does not contain a weak $K_t$ immersion (in which case the Fox–Pach–Suk
  vertex bound $\le 1.4(t - 1)$ is consistent with this), **or** does contain a weak
  $K_t$ immersion $G'$ for which the second-stage crossing recovery does not produce
  enough extra crossings in $G - E(G')$ (a "Fox–Pach–Suk-evading" graph);
- structurally novel: avoids all the families currently understood (line graphs,
  Mycielski, the chromatic-$t$ Kneser family, planar joins, …);
- *and* satisfies $\overline{\operatorname{cr}}(G) < \underline{L}(t)$ for the
  finite certified lower bound on $\operatorname{cr}(K_t)$ — without this, the
  candidate falsifies only the *strong form*, not Albertson itself (cf. Obstruction O2).

Such a graph is *not* automatically a counterexample to Lescure–Meyniel.

## Falsifiable predictions

- **P1.** The brute enumeration of $25$-critical graphs on exactly $48$ vertices with
  $\delta \ge 24$ does **not** terminate within a 1-year compute budget on a 256-core
  cluster, even with aggressive `nauty` canonical-form pruning. (This prediction is
  unchanged from v3 and supports the v4 Track A demotion.)
- **P1a (added in v4).** The $26$-Ore family on $51$ vertices, enumerated by C1.5,
  has at most a few thousand non-isomorphic members. *Not a theorem* — Role 5 must
  enumerate to confirm. If the count is much larger, the Ore corner is itself a
  research problem and Track A's $(26, 51)$ Ore-restricted leg must be re-scoped.
- **P1b (added in v4).** No member of the $26$-Ore family on $51$ vertices is a
  counterexample to Albertson, i.e. every such $G$ has $\operatorname{cr}(G) \ge
  \operatorname{cr}(K_{26})$. Reasoning: Ore composition is structurally rigid;
  the composition $O(K_{26}, K_{26})$ inherits two embedded $K_{25}$s with high
  forced crossing count. To be tested by C3, not asserted.
- **P2.** For every $t \le 30$, the iterated Mycielskian $M_t$ has heuristic
  crossing number $\overline{\operatorname{cr}}(M_t) / Z(t)$ that **empirically
  diverges** as $t$ grows. Heuristic conjecture, not theorem.
- **P3.** For a candidate MCE $G$ at $t = 25, n = 48$:
  - $\overline{\operatorname{cr}}(G) < Z(25) = 4356$ would falsify the **strong form**
    of Albertson for $G$. This does **not** falsify Albertson itself.
  - $\overline{\operatorname{cr}}(G) < \underline{L}(25)$ for a finite certified
    lower bound $\underline{L}(25) \le \operatorname{cr}(K_{25})$ would falsify
    Albertson outright. The asymptotic BLS constant $0.98559895$ applied naively
    gives $4293.27$, but this is **not** a certified finite lower bound.
- **P4 (added in v4).** R5a will produce a constant $c \le 9/16$ on a 12-month
  horizon, with significant probability that $c < 9/16$ is the actual outcome
  (Role 7 memo Target T1 estimate). The exact value of $c$ is the verdict on
  whether $9/16$ is a real obstruction (Case 2b binding) or an artifact (Case 2b
  can be bypassed).

## Failure modes to guard against

- **F1. Confusing $\operatorname{cr}(K_t)$ with $Z(t)$.** For $t \ge 13$ these are not
  known to be equal. Every proof must specify which side it uses; every counterexample
  search must specify which inequality it is testing.
- **F1b. Confusing asymptotic ratios with finite certificates.** The Balogh–Lidický–
  Salazar $0.98559895$ and de Klerk et al. $0.83$ are *asymptotic*; they do not
  certify $\operatorname{cr}(K_{25}) \ge 0.985 \cdot Z(25)$ as a finite statement.
- **F2. Constant degradation in the Crossing Lemma chain.** Going from
  $|E| \ge 6.95|V|$ (or $6.77|V|$, BK PDF pending — see Background) down to
  $|E| \ge 4|V|$ drops the constant to roughly $1/64$. Any new proof must track
  which threshold is being used.
- **F3. Criticality is not preserved by induced subgraph deletion.** Removing a vertex
  from a $t$-critical graph drops the chromatic number. Any inductive proof must use a
  different reduction (block decomposition, edge contraction, immersion, Ore
  composition).
- **F4. Heuristic crossing-number upper bounds are not eliminations.** A heuristic
  $\overline{\operatorname{cr}}(G) \ge L$ is *not* evidence that
  $\operatorname{cr}(G) \ge L$. Only certified *lower* bounds can eliminate candidates.
- **F5. Enumeration of $t$-critical graphs blows up at the Cranston residual orders.**
  Bare `nauty` enumeration is infeasible; R1 must either restrict structurally
  (R1b) or recast as SAT (R1a). A pipeline that depends on raw enumeration will
  not terminate. The v4 KY non-Ore floor reduces the SAT search space but does
  not rescue raw enumeration.
- **F6. Conflating weak immersion with Albertson.** Fox–Pach–Suk is a two-stage
  argument (Obstruction O3); a weak $K_t$ immersion alone does not certify Albertson
  for the host graph, and absence of a weak immersion does not refute it.
- **F7. Confusing edge-connectivity and vertex-connectivity for critical graphs.**
  The $(t-1)$-edge-connectivity theorem (Dirac 1953) does **not** force
  vertex-connectivity $\ge t - 1$ — $k$-Ore graphs witness $\kappa = 2$.
  Restrictions to high vertex-connectivity in R1b are optional, not forced.
- **F8 (added in v4). Confusing edge-connectivity attribution.** The
  $(t-1)$-edge-connectivity theorem is **Dirac 1953**, not Kostochka–Stiebitz.
  Kostochka–Stiebitz belongs in the sparse-critical-graph edge-density chain that
  feeds into the Kostochka–Yancey bound; do not conflate.
- **F9 (added in v4). False Ore claims.** Ore composition preserves
  $|V| \equiv 1 \pmod{k-1}$. Any claim that "the $k$-Ore family at order $n$ is
  small / single / non-trivial" without first checking the congruence is invalid.
  v3 contained one such error (the Role 2 memo at $(25, 48)$, now retracted).
- **F10 (added in v4). Overselling R5a.** R5a is a *re-derivation* of one claim in
  one paper. The publishable minimum ($c < 9/16$) is a refinement of the FPS
  chromatic-index lemma, not a closure of Albertson. Do not phrase R5a as "one
  re-derivation from Albertson"; phrase it as "the highest-leverage local
  calculation in the whole plan", and accept that the verdict might confirm
  $9/16$ as the binding constant.

## Critical reading

- **Original conjecture.** M. O. Albertson, "Chromatic number, independence ratio, and
  crossing number" (2007); openproblemgarden.org/op/crossing_numbers_and_coloring.
- **arXiv:1006.3783** — Albertson–Cranston–Fox, "Crossings, colorings, and cliques",
  *Electronic Journal of Combinatorics* **16(1)** (2009), Research Paper 45. Original
  MCE bound $|V| \le 4t$.
- **arXiv:0909.0413** — Barát–Tóth, *Towards the Albertson Conjecture* (2009).
  Extension to $t \le 16$, MCE bound to $3.57t$.
- **arXiv:1509.01932** — Ackerman, *On topological graphs with at most four crossings per
  edge* (2015/2019). $\le 4$ crossings per edge $\Rightarrow$ $|E| \le 6|V|-12$.
  Improves Crossing Lemma constant to $1/29$, extends Albertson to $t \le 18$.
- **arXiv:2510.05893** — Fox–Pach–Suk, *Immersions and Albertson's conjecture* (Oct
  2025; SoCG 2025 version at LIPIcs.SoCG.2025.50). Theorem 1.2(i, arXiv form):
  $n < 1.4k - 0.6$. Theorem 1.2(i, SoCG form): $\le 1.4(k-1)$. Theorem 1.2(ii):
  $n < (1.64 - \varepsilon)k$ for $k$ sufficiently large. Lemma 2.3 with the
  $9/16$ constant is the R5a / Track B target. Claim 3.7 is the proof of the
  binding case; Case 2b is the obstructing sub-case to be isolated.
- **arXiv:2512.08020** — Cranston, *Progress on Albertson's Conjecture* (Dec 2025).
  Theorem 1, body Theorems 3, 4, Theorem 2 residual $(r, |G|) \in \{(25, 48),
  (26, 50), (26, 51)\}$, Appendix A finite Fox–Pach–Suk crossing-loss bound, and
  reference to Bungener–Kaufmann.
- **arXiv:2409.01733** — Bungener–Kaufmann, *Improving the Crossing Lemma by
  Characterizing Dense 2-Planar and 3-Planar Graphs* (2024). Source of the
  $1/27.48$ constant. **Threshold discrepancy:** arXiv abstract gives
  $|E| > 6.77|V|$; Cranston invokes $|E| \ge 6.95|V|$. PDF read pending
  (Role 8 deliverable D1).
- **arXiv:1209.1050** — Kostochka–Yancey, *Ore's conjecture on color-critical
  graphs is almost true*. Edge-density bound for $k$-critical graphs, tight on
  $k$-Ore graphs. Source of the v4 KY (standard) and non-Ore-strengthened
  bounds at the three Cranston residual orders.
- **arXiv:1711.08958** — Balogh–Lidický–Salazar, *Closing in on Hill's conjecture*,
  *SIAM J. Discrete Math.* **33** (2019), 1261–1276. **Asymptotic** ratio
  $\liminf_n \operatorname{cr}(K_n)/H(n) \ge 0.98559895$. **Not a finite-$n$
  certificate.**
- **Pan–Richter, 2007** — "The crossing number of $K_{11}$ is 100", *J. Graph Theory*.
- **arXiv:math/0404142** — de Klerk–Maharry–Pasechnik–Richter–Salazar, *Improved bounds
  for the crossing numbers of $K_{m,n}$ and $K_n$*, *SIAM J. Discrete Math.* **20**
  (2006), 189–202. **Asymptotic** ratio $\operatorname{cr}(K_n) / Z(n) \ge 0.83$.
- **Pach–Tóth (1997), Pach–Radoičić–Tardos–Tóth (2006), Ackerman (2019),
  Bungener–Kaufmann (2024)** — the chain of Crossing Lemma constant improvements.
- **Lescure–Meyniel (1989)** — weak immersion conjecture, structural backbone of
  Fox–Pach–Suk.
- **Catlin (1979)** — counterexamples to Hajós for $t \ge 7$.
- **Erdős–Fajtlowicz (1981)** — "On the conjecture of Hajós".
- **Dirac (1952)** — $\delta \ge t - 1$ bound on $t$-critical graphs.
- **Dirac (1953)** — $(t-1)$-edge-connectivity of $t$-critical graphs (v4 corrected
  attribution; was previously misassigned to Kostochka–Stiebitz).
- **Ore (1967)** — Ore composition of color-critical graphs; the construction that
  preserves $|V| \equiv 1 \pmod{k-1}$ and that underlies the Kostochka–Yancey
  extremal family.
- **Lovász (1978)** — chromatic number of Kneser graphs.
- **Schaefer, *The Crossing Number of Graphs* (CRC, 2018)** — catalogue of
  crossing-number variants.

## Things that remain to be verified (transparency)

- **BK threshold (Role 8 deliverable D1, 30-day ask).** Resolve the $6.77|V|$ vs
  $6.95|V|$ discrepancy by reading the arXiv:2409.01733 PDF and recording the
  verbatim theorem statement. Update Background / Obstruction O1 / F2 once
  confirmed.
- **A finite, certified lower bound** $\underline{L}(t)$ on $\operatorname{cr}(K_t)$
  for $t \in \{25, 26\}$. The asymptotic constants $0.83$ and $0.98559895$ are
  not such bounds. If the ancillary computations of Balogh–Lidický–Salazar's
  flag-algebra SDP yield explicit finite constants, those should be extracted.
- **Cranston body Theorems 3, 4 vs. headline Theorem 1.** The $1.212r$ vs. $1.228r$
  distinction is restored in v3 and unchanged in v4; cross-check against the
  published version.
- **Crossing-number lower-bound machinery scale.** Buchheim–Chimani ILP / Chimani–
  Mutzel SAT at $n \sim 50, m \sim 600$ is at or beyond the current state of the
  art; may itself require a research effort.
- **$(26, 51)$ Ore enumeration.** The claim that the family is "plausibly small"
  needs to be confirmed by C1.5. P1a sets the falsifiable benchmark; if the
  count exceeds a few thousand, the Ore corner becomes a research problem and
  Track A's Ore leg must be re-scoped.
- **KY non-Ore numbers $587, 588, 637, 638, 649, 650$.** These were supplied by
  the senior audit in `docs/review_v3.md`; the v4 plan trusts them without
  independent re-derivation. A re-derivation from arXiv:1209.1050 is a 1-day
  literature task and should be done before any Track A SAT model is committed
  to production.
- **R5a Case 2b.** Whether "Case 2b" of FPS Claim 3.7 is in fact the binding
  case (Role 7 memo Section 1d), and whether it can be bypassed. C8 is the
  symbolic check; the actual case-isolation work is pen-and-paper R5a.
