# Review of v3 + team memos (post-team-launch audit)

Senior pass on plan v3 plus the nine role memos in
`problems/crossing_numbers_and_coloring/work/`.

## Main correction

**The claimed $25$-Ore family at $(25, 48)$ cannot exist.**

Ore composition preserves
$$|V(G)| \equiv 1 \pmod{k - 1}.$$

For $k = 25$, the admissible Ore orders are
$$25,\ 49,\ 73,\ 97,\ \dots$$
**not $48$.** So Role 2's memo claim — "the $25$-Ore family at $(25, 48)$ is essentially a single graph" — is false. The congruence alone kills it.

The real Ore corner is $(26, 51)$, because
$$51 \equiv 1 \pmod{25}.$$

So v4 must not make $25$-Ore at $(25, 48)$ the critical path. The corrected residual breakdown:

- **$(25, 48)$**: no $25$-Ore extremal graph by the Ore-order congruence; all candidates are non-Ore, so the right structural lever is the **non-Ore Kostochka–Yancey strengthening**.
- **$(26, 50)$**: no $26$-Ore extremal graph, since $50 \equiv 0 \pmod{25}$.
- **$(26, 51)$**: the Ore case exists and is plausibly the single one-composition graph from two $K_{26}$s; this is the correct **Ore corner** to isolate.

## The three v4 fixes from the team memos that should land

### 1. Edge-connectivity attribution

$(k-1)$-edge-connectivity of $k$-critical graphs is **Dirac 1953**, not Kostochka–Stiebitz. Kostochka–Stiebitz belongs in the sparse-critical-graph **edge-density** chain, not as the source of edge-connectivity. Fix in plan v3 lines 272–273, 821, 874, and revision-history line 119–120.

### 2. Add Kostochka–Yancey

The trivial $|E| \ge (t-1) n / 2$ bound is obsolete at the residual orders. The Kostochka–Yancey bound (arXiv:1209.1050) gives:

| Order | KY $|E|$ lower bound | Trivial $(t-1)n/2$ |
|---|---|---|
| $(25, 48)$ | $\ge 587$ | $576$ |
| $(26, 50)$ | $\ge 637$ | $625$ |
| $(26, 51)$ | $\ge 649$ | $638$ |

And the **non-Ore strengthening**:

| Order | non-Ore KY $|E|$ |
|---|---|
| $(25, 48)$ | $\ge 588$ |
| $(26, 50)$ | $\ge 638$ |
| $(26, 51)$ | $\ge 650$ |

This is real constraint mass for SAT/CEGAR — make it a mandatory R1a encoding constraint.

### 3. BK threshold: qualify, do not assert

The Büngener–Kaufmann arXiv abstract (`arXiv:2409.01733`) states $m > 6.77 n$ for the $c > 1/27.48$ Crossing Lemma constant. Cranston / FPS sometimes invoke $6.95n$, apparently as a safer invoked threshold. v4 should **not** state "BK threshold is $6.95$" without qualification. Correct phrasing: BK abstract gives $6.77$; Cranston invokes $6.95$; verify the PDF theorem statement and use the sharper value only when the exact hypothesis is confirmed.

## Strategic assessment

The compute-team consensus across Roles 3, 4, 5, 6 is correct: **unrestricted $(25, 48)$ closure is not a 12-month target.** It is not even a responsible compute target without a structural coverage theorem. SAT, enumeration, and exact crossing-number certification at $n \approx 50, m \approx 600$ are all too large.

So **Track A** should be demoted to:

> **Track A = subfamily certification + counterexample hunt** — not "close $t = 25$".

The real positive-proof track is **Track B**:

- **R5** — improve Fox–Pach–Suk chromatic-index lemma.
- **R2c** — minimum-degree-aware Crossing Lemma.
- **R3** — structural subclass theorem.

Role 9 is also right that **finite lower bounds for $cr(K_{25})$ matter for falsification, not for positive proof.** If the PI wants a positive theorem, Role 9 is secondary.

## Bright spot

Role 7's $9/16 \to 0.55$ observation is the most plausible 12-month theorem, but it is **not yet a theorem-shaped claim**. It should become a focused v4 route:

> **R5a: Re-derive FPS Claim 3.7 with Case 2b isolated.**
> - Goal: prove whether $9/16$ is a real obstruction or an artifact.
> - Minimum publishable outcome: any $c < 9/16$.
> - Stretch: $c = 11/20$.
> - Dream: $c = 1/2$.

Do not oversell "one careful re-derivation away." The right phrasing is: **"This is the highest-leverage local calculation in the whole plan."**

## v4 priority order

1. Fix Dirac / KY / BK threshold.
2. Delete the false $25$-Ore critical path.
3. Add an Ore-congruence subsection.
4. Make $(26, 51)$ the only Ore residual corner.
5. Make non-Ore KY surplus a mandatory SAT constraint.
6. Demote unrestricted Track A.
7. Promote R5a as the main 12-month theorem target.

## Sources checked

- Kostochka–Yancey, `arXiv:1209.1050`.
- Büngener–Kaufmann, `arXiv:2409.01733`.
- Fox–Pach–Suk, `arXiv:2510.05893` / SoCG 2025.
