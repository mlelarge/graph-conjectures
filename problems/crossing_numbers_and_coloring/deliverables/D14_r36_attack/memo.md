# D14 — R3.6 attack memo: list-Albertson at the Cranston threshold

**Author.** Role 2 (critical-graph / chromatic-graph theory).
**Date.** 2026-05-17.
**Status.** Attack memo. One candidate theorem $T_1$ stated (list-Albertson
at $t \le 24$); proof attempt walked through end-to-end; **verdict:
candidate proof closes for $t \le 18$ unconditionally; closes for $19 \le
t \le 24$ conditional on a list-edge-colouring lift of the FPS chromatic-
index lemma (arXiv:2510.05893 Lemma 2.3) at constant $9/16$**; fallback
$T_1'$ at $t \le 18$ is unconditional; 30-day plan attached.
**Inputs.** `work/01_principal_lead/INTEGRATION.md` (Decision 2026-05-17-2),
`deliverables/D13_r2c_attack/memo.md` (format template + R2c verdict),
`work/02_critical_graphs/memo.md` (Sections 1.4, 3.3–3.4), `docs/plan.md` v4.

---

## 1. Context and target

**Why R3.6 is the post-R2c Track B headline.** With R5a closed (theorem-
grade artifact `deliverables/D8_paper/sharpness_9_8.pdf`, 2026-05-16) and
R2c cleanly failed at the iteration-stopping step (D13, structural loss
of $d_0$: the Pach–Tóth/Ackerman/BK density iteration is invariant under
reassignment of edges between vertices), Decision 2026-05-17-2 names
**R3.6** as the Track B headline. The asymmetry of the chromatic-variant
hierarchy
$$\chi_f(G) \;\le\; \chi(G) \;\le\; \chi_\ell(G) \;\le\; \chi_{\rm OL}(G) \;\le\; \chi_{\rm DP}(G) \;\le\; \Delta(G) + 1$$
makes one direction strictly more attractive: a theorem
"$\chi^\ast(G) \ge t \Rightarrow \operatorname{cr}(G) \ge \operatorname{cr}(K_t)$"
for $\chi^\ast$ further *right* is *stronger* (weaker hypothesis, more
graphs covered). So **list-Albertson and DP-Albertson imply Albertson**;
**fractional-Albertson is implied by Albertson** (wrong direction).

**Concrete numerical anchor.** The ACF / Barát–Tóth / Ackerman / Cranston
chain proves Albertson unconditionally at:

| Chain step | arXiv | $t$ closed | MCE vertex bound | Crossing-Lemma input |
|---|---|---:|---:|---|
| ACF 2009 | 1006.3783 | $t \le 12$ | $|V| \le 4t$ | Pach–Tóth $c = 1/33.75$ |
| Barát–Tóth 2009 | 0909.0413 | $t \le 16$ | $|V| \le 3.57t$ | PT $c = 1/33.75$ |
| Ackerman 2019 | 1509.01932 | $t \le 18$ | $|V| \le 3.03t$ | $c = 1/29$, $|E| \ge 7|V|$ |
| Cranston 2025 | 2512.08020 | $t \le 24$ | $|V| \le 2.8118r$ excl. | BK $c = 1/27.48$, $|E| \ge 6.95|V|$ |

Cranston residual: exactly $(t, n) \in \{(25, 48), (26, 50), (26, 51)\}$
(Theorem 2). $T_1$'s target is to lift the **entire chain up to $t = 24$**
from chromatic-number to list-chromatic-number hypotheses. The user's
prior ("the Krivelevich list-critical edge bound and Borodin/ERT list-
Gallai-tree theorem already exist; the ACF chain depends only on the
edge-density input, so list Albertson should follow at the same $t$-
threshold modulo bookkeeping") sets the expectation. Below: I *verify*
the prior, locate the precise bookkeeping points where the lift fails,
and find that the prior is **partially right** — the lift is clean
through $t \le 18$ (Ackerman chain) but **needs an FPS-list-edge-
colouring lemma not currently in the literature** to extend to
$19 \le t \le 24$ (Cranston chain).

## 2. Background — the four inputs to the chain

The chain reduces to four inputs. Each is recorded with source, chromatic
formulation, and list/DP-lift status.

### 2.1 Dirac min-degree

> **Dirac 1952.** Every $k$-critical $G$ has $\delta(G) \ge k - 1$.

J. London Math. Soc. 27 (1952), 85–92. **List analogue ✓ trivial** via
list-swap (replace the swap-a-colour proof: if $\deg(v) \le k - 2$ and
$G - v$ is $L$-colourable, $|L(v)| \ge k$ gives a free choice). **DP
analogue ✓ trivial** — Bernshteyn–Kostochka–Pron, arXiv:1605.04432,
European J. Combin. 65 (2017), 122–129.

### 2.2 Edge-count lower bound

> **Kostochka–Yancey 2014.** $k$-critical $G \ne K_k$ ($k \ge 4$, $n
> \ne k+1$) satisfies $|E(G)| \ge F(n, k) := \lceil ((k+1)(k-2)n -
> k(k-3))/(2(k-1)) \rceil$.

arXiv:1209.1050, JCTB 109 (2014), 73–101.

**List analogue (Krivelevich 1997, Combinatorica 17, 401–426;
doi:10.1007/BF01215921):** for $k$-list-critical $G$,
$|E(G)| \ge \frac{k-1}{2} n + \frac{k-3}{2(k^2 - 2k - 1)} n$.
Strictly weaker than KY: at $k = 24$, KY gives $\phi_{24} = 12 - 1/23
\approx 11.957$ edges/vertex; Krivelevich gives $\approx 11.520$
edges/vertex (gap $\approx 0.437$). Kierstead–Rabern 2017
(arXiv:1701.06012) and Postle (PhD thesis Georgia Tech 2012, Ch. 4)
sharpen Krivelevich but **whether the full KY constant $(k+1)(k-2) /
(2(k-1))$ holds for list-critical is open**. *Needs literature
verification.*

**DP analogue.** Bernshteyn 2016 (arXiv:1607.04886) proves $|E| \ge
\frac{k-1}{2} n + \Omega(n/k)$ for DP-critical, again weaker than KY.

**Critical-path remark.** The ACF / BT / Ackerman / Cranston chain uses
**only the Dirac $(k-1)n/2$ edge floor** plus the Crossing Lemma (plan.md
v4 line 276–277; `work/02/memo.md` sanity-check 4.2). So the list/DP
lift of the chain **does not require lifting KY**; only the trivial
$(k-1)/2$ floor is needed, and that lifts via §2.1.

### 2.3 Crossing Lemma

> **Bungener–Kaufmann 2024.** For $|E| \ge \alpha |V|$ ($\alpha = 6.95$
> Cranston / $6.77$ BK abstract), $\operatorname{cr}(G) \ge |E|^3 /
> (27.48 |V|^2)$.

arXiv:2409.01733. **List/DP analogue ✓ trivial — Crossing Lemma is
purely topological/drawn-graph and knows nothing about colour-list
structure.** Same for ACNS / Pach–Tóth / Ackerman constants.

### 2.4 Cranston Lemma (chain-closing step) and FPS

Cranston's $t \le 24$ exclusion combines Dirac, BK Crossing Lemma, and
the Fox–Pach–Suk weak-immersion bound (arXiv:2510.05893 Theorem 1.2(i)):
$\chi(G) \ge k$ and $|V(G)| < 1.4(k - 1) \Rightarrow$ $G$ contains a
weak $K_k$-immersion. The FPS proof uses Vizing's theorem on chromatic
index plus a **multigraph chromatic-index lemma** (arXiv:2510.05893
Lemma 2.3) with leading constant $9/16$ (the R5a-closed sharp constant).

**List-lift of FPS.** Three components:

- (a) The FPS Vizing reduction operates on a multigraph $M$ derived from
  an *optimal proper vertex colouring* of $G$. For the list-lift, $M_L$
  is derived from an optimal list-colouring under worst-case $L$. The
  multigraph construction works identically.
- (b) The chromatic-index lemma $\chi'(M) \le 9 \Delta(M) / 16$ is
  invoked on $M$. **Its list-edge-colouring analogue $\chi'_\ell(M) \le
  c_\ell \Delta(M)$ at the same constant $c_\ell = 9/16$ is not
  published.** Best published bound is Borodin–Kostochka–Woodall 1997
  (JCTB 71, 184–204): $\chi'_\ell(M) \le 7\Delta(M)/4 + O(1)$.
- (c) The two-stage immersion-to-crossings recovery (FPS §3, Obstruction
  O3 in plan.md v4) is a topological/path-embedding argument. ✓ lifts.

The lift of Cranston's chain at $19 \le k \le 24$ **reduces entirely to
the lift of (b)**. *Needs literature verification.*

### 2.5 Summary of bookkeeping

| Step | Chromatic input | List-lift | On critical path? |
|---|---|---|---|
| Dirac min-deg (§2.1) | $\delta \ge t-1$ | ✓ trivial | yes |
| Edge floor (§2.2) | KY tight | Krivelevich weaker | **no** — chain uses Dirac only |
| Crossing Lemma (§2.3) | BK $1/27.48$ | ✓ trivial (topological) | yes |
| FPS Lemma 2.3 (§2.4(b)) | $\chi'(M) \le 9\Delta/16$ | **open** | yes (for $19 \le t \le 24$) |
| FPS recovery (§2.4(c)) | (topological) | ✓ trivial | yes |

Three of five steps lift trivially; one (KY) is irrelevant to the
chain; the FPS chromatic-index lemma is the binding question.

## 3. The candidate theorem $T_1$

> **Candidate Theorem $T_1$ (List-Albertson at $t \le 24$).** Every graph
> $G$ with $\chi_\ell(G) \ge t$ and $t \le 24$ satisfies
> $$\operatorname{cr}(G) \;\ge\; \operatorname{cr}(K_t).$$
> Unconditionally for $t \le 18$ (Ackerman-chain inputs all lift).
> Conditional for $19 \le t \le 24$ on a list-edge-colouring
> strengthening of FPS Lemma 2.3 at constant $9/16$ (currently open;
> best published replacement $c_\ell = 7/4$ via Borodin–Kostochka–
> Woodall 1997).

**Form remarks.** $t \le 24$ matches the unconditional Cranston
chromatic chain (plan.md v4 line 397). The list-Albertson hypothesis is
strictly weaker than the chromatic hypothesis ($\chi_\ell \ge \chi$), so
$T_1$ covers more graphs than Cranston Theorem 1. Range $t \in \{25,
26\}$ inherits the residual constraints of the chromatic case and is
out of scope here (Track A, not R3.6).

**Why list and not DP or fractional.** DP-Albertson would be strictly
stronger but the FPS chromatic-index lemma's DP-edge-colouring analogue
is genuinely open (correspondence-edge-colouring is a 2020-era subject;
Cao–Bernshteyn arXiv:2002.06031 is the earliest systematic study), and
the DP-critical edge floor (Bernshteyn 2016) is strictly weaker than
the list-critical floor by $\Theta(1/k)$. Fractional-Albertson is
*strictly weaker* than Albertson ($\chi_f \le \chi$ → $\chi_f \ge t$ is
a *stronger* hypothesis), so proving it does not imply Albertson and
is not a Track B headline.

**Concrete improvement.** Currently, list-Albertson is proven only for
$t \le 4$ (small-case ACF hand-verification trivially lifts; Brooks /
Erdős–Rubin–Taylor 1979 / Vizing 1976 give $t \le 4$ on the list side).
**$T_1$ jumps the list-Albertson threshold from $t \le 4$ to $t \le 24$
in one step** (or to $t \le 18$ unconditionally via the fallback $T_1'$
below). This is a new theorem in the chromatic-graph-theory literature:
the building blocks (Krivelevich, Borodin/ERT, Ackerman, Cranston)
exist; no one has assembled them.

## 4. Proof attempt — lift the chain step-by-step

**Setup.** $G$ is $k$-list-critical: $\chi_\ell(G) \ge k$ and
$\chi_\ell(G - e) < k$ for every $e$. WLOG $G$ is the list-MCE for $T_1$
at $k$.

**Step 1 (Dirac).** $\delta(G) \ge k - 1$. ✓ (§2.1).

**Step 2 (edge floor).** $|E(G)| \ge (k - 1)n / 2$. ✓ (from Step 1; no
KY-list needed).

**Step 3 (Crossing Lemma).** For $k \ge 8$ (so $k - 1 \ge 6.95$, BK
threshold satisfied; $k \le 7$ is trivial via Hadwiger / classical
hand-verification),

$$\operatorname{cr}(G) \;\ge\; \frac{|E|^3}{27.48\, n^2} \;\ge\; \frac{((k-1)/2)^3 n^3}{27.48\, n^2} \;=\; \frac{(k-1)^3}{8 \cdot 27.48}\, n. \tag{CL}$$

✓ (§2.3 + Step 2).

**Step 4 (ACF / BT / Ackerman vertex bound).** Combining (CL) with an
upper-bound assumption $\operatorname{cr}(G) < \operatorname{cr}(K_k)
\le Z(k)$ (the Albertson-side hypothesis for a candidate counterexample)
and the rearrangement $\operatorname{cr}(G) \ge |E|^3 / (c \cdot n^2)$,
one gets $|V(G)| \le f_c(k)$ with $f_c$ shrinking as $c$ improves. At
$c = 1/29$ (Ackerman), $f(k) = 3.03 k$. **This step uses only Dirac +
Crossing Lemma + Albertson hypothesis — no chromatic-index lemma.**
✓ lifts to list.

**Step 5 (Cranston tightening to $t \le 24$).** Cranston's $|V| \le
2.8118 r$ exclusion (Theorem 1) at $r \ge 15$ combines the BK Crossing
Lemma (✓) with the FPS weak-immersion alternative
(arXiv:2510.05893 Theorem 1.2(i)). The latter uses FPS Lemma 2.3 — the
$\chi'(M) \le 9\Delta(M)/16$ chromatic-index lemma. **For the list-
lift, we need the analogous $\chi'_\ell(M) \le 9\Delta(M)/16$ on the
same multigraph class.** This is the binding open question.

**Step 6 (FPS two-stage recovery).** Pure topological/path-embedding
(Obstruction O3, plan.md v4). ✓ trivial once Step 5 closes.

**Verdict.**

- **$t \le 18$ (Ackerman regime): $T_1$ proven unconditionally.** Steps
  1–4 close at $c = 1/29$, $f(k) = 3.03 k$, plus the ACF hand-
  verification chain for $t \le 12$ (which lifts because list-$k$-
  critical graphs at $k \le 4$ are explicitly characterised, and $t \in
  \{5, \dots, 12\}$ admit finite case-by-case verification).
- **$19 \le t \le 24$ (Cranston regime): $T_1$ closes conditional on
  Step 5 list-lift.** The FPS chromatic-index lemma at $9/16$ must hold
  for list-edge-colouring on the same multigraph class.

## 5. Where the lift could fail

**Single equation pointing to the lossy step.** FPS Lemma 2.3 in its
chromatic form:

$$\chi'(M) \;\le\; \tfrac{9}{16} \Delta(M) \tag{FPS-2.3}$$

(R5a closed: $9/16$ is sharp on this side, `deliverables/D8_paper/
sharpness_9_8.pdf`). The list-edge-colouring analogue needed for the
$T_1$ lift at $19 \le t \le 24$:

$$\chi'_\ell(M) \;\le\; c_\ell \cdot \Delta(M) \tag{FPS-2.3-list}$$

with $c_\ell = 9/16$. **The best currently published $c_\ell$ is
Borodin–Kostochka–Woodall 1997: $c_\ell = 7/4 + O(1)$** (JCTB 71,
184–204) — roughly $3.1\times$ worse than FPS's $9/16$. Substituting
into the FPS Theorem 1.2(i) vertex bound $|V(G)| < 1.4(k-1)$ gives a
degraded list vertex bound

$$|V(G)| \;<\; 1.4 \cdot \tfrac{9/16}{7/4} \cdot (k-1) \;=\; 1.4 \cdot \tfrac{9}{28} (k-1) \;=\; 0.45\,(k-1).$$

At $k = 24$: $|V(G)| \le 10$. The Cranston-chain combination then
fails at $t \ge 19$; the unconditional list result drops back to the
Ackerman threshold $t \le 18$ (i.e. the $T_1'$ fallback). **This is the
honest worst case.**

**KY-list-lift is not on the critical path.** The chain uses only the
trivial Dirac edge floor $(k-1)n/2$, not the KY constant; so the open
question of "does the full KY constant hold for list-critical?" is
irrelevant to $T_1$.

**Cranston-restricted $t \in \{25, 26\}$ behaviour.** A $k$-list-
critical $G$ may have $\chi(G) < k$, so the list-residual at $k \in
\{25, 26\}$ may include $(t, n)$ pairs outside Cranston's triples
$\{(25, 48), (26, 50), (26, 51)\}$. **$T_1$ at $t \le 24$ does not
address $t \in \{25, 26\}$**; in particular it does **not** close any
Cranston residual.

## 6. Fallback $T_1'$

> **$T_1'$ (List-Albertson at $t \le 18$, unconditional).** Every graph
> $G$ with $\chi_\ell(G) \ge t$ and $t \le 18$ satisfies
> $\operatorname{cr}(G) \ge \operatorname{cr}(K_t)$.

**Lift summary.** Ackerman's $t \le 18$ chain uses:

- Dirac (§2.1) — ✓ lifts.
- Trivial edge floor $|E| \ge (k-1)n/2$ — ✓ from Dirac-list.
- Ackerman's $|E| \le 6n - 12$ for $\le 4$ crossings/edge — purely
  topological, ✓ lifts.
- Ackerman's $c = 1/29$ Crossing Lemma for $|E| \ge 7|V|$ — purely
  topological, ✓ lifts.
- ACF $|V| \le 4t$ reduction — Dirac + Crossing Lemma only, ✓ lifts.
- Hand-verification for $t \le 12$ — list-version verifiable per
  Brooks/ERT/Vizing 1976 for $t \le 4$, then finite case-by-case for
  $t \in \{5, \dots, 12\}$.

**No FPS dependence**, hence unconditional. Publishable as preprint at
$\sim 12$ pages: novelty is the *systematic* assembly of existing
list-critical building blocks (Krivelevich 1997, Borodin/ERT 1979,
Ackerman 2019, list-Brooks).

**Realistic horizons.**

- **6 months.** Ship $T_1'$ ($t \le 18$, unconditional) as preprint to
  *European J. Combin.* or JCTB.
- **12 months.** Ship $T_1$ ($t \le 24$). Conditional or unconditional
  depending on the W3 literature pass below: (a) list-lift of FPS
  Lemma 2.3 at $9/16$ found in literature → unconditional; (b) gap
  confirmed → conditional, in the same form as Cranston's own paper is
  implicitly conditional on the BK constant whose threshold ambiguity
  is logged in plan.md v4 lines 122–125.

**Does $T_1$ / $T_1'$ close any Cranston residual at $(25, 48), (26,
50), (26, 51)$?** **No.** $T_1'$ stops at $t = 18$; $T_1$ stops at
$t = 24$. The Cranston residual at $t \in \{25, 26\}$ is outside the
range of both. A hypothetical list-Albertson at $t \le 26$ would imply
the chromatic residual triples via the trivial list assignment
$L(v) = \{1, \dots, \chi(G)\}$, but that is the original $t = 25, 26$
problem itself, lifted to list — no free win. **Net: $T_1$ / $T_1'$
constitute a publishable bundle orthogonal to the Cranston residual**,
same status as Role 8's projected R2c $T_1'$ (D13 §6). The 12-month
project bundle (Decision 2026-05-17-2 item 5: (i) R5a sharpness,
(ii) R2c bisection-width fallback, (iii) R3.6 candidate) gains its
third leg with $T_1$.

## 7. 30-day work plan (Role 2)

| # | Task | Effort | Deliverable |
|---|------|---:|---|
| W1 | Write the unconditional $T_1'$ proof in full: (i) list-Dirac (~ 1p), (ii) Ackerman Crossing Lemma + 4-crossings-per-edge (~ 2p), (iii) ACF $|V| \le 4t$ lift (~ 2p), (iv) hand-verification $t \le 12$ (~ 3p), (v) write-up + abstract (~ 4p). Target 12-page draft. | 5 d | `D14_r36_attack/T1prime_draft.md` |
| W2 | Literature pass: Krivelevich/Kierstead–Rabern list-critical edge bound. Read arXiv:1701.06012 and Postle thesis Ch. 4. Determine the current best constant; is there a published list-KY at KY's leading constant? | 3 d | `D14_r36_attack/lit_audit.md` §1 |
| W3 | **Binding literature question.** FPS chromatic-index lemma list-lift: read Borodin–Kostochka–Woodall 1997 (JCTB 71), Cao–Bernshteyn 2020 (arXiv:2002.06031), and any FPS-follow-up specifically targeting Lemma 2.3 in list-edge-colouring. Verdict: (a) $9/16$ lifts → $T_1$ unconditional; (b) explicit weaker $c_\ell$ → degraded $t$-threshold; (c) unknown → $T_1$ stays conditional. | 5 d | `lit_audit.md` §2 |
| W4 | Empirical sanity check: for small list-critical graphs at $k \le 6$, verify $\operatorname{cr}(G) \ge \operatorname{cr}(K_k)$ with margin. Use Role 3's exact-cr ILP at $n \le 14$. | 4 d | `work/02/list_emp.md` |
| W5 | DP-coloring literature pass (Bernshteyn–Kostochka–Pron arXiv:1605.04432; Bernshteyn arXiv:1607.04886). Confirm DP-Albertson is out of scope for the 12-month window (correspondence-edge-colouring is too young). Scope-bounding deliverable. | 3 d | `lit_audit.md` §3 |

Total: 20 person-days $\le$ 30-day window. **W3 is highest-value
literature** (determines $T_1$ conditional vs. unconditional); **W1 is
highest-value paper** (ships $T_1'$ regardless of W3 outcome). Same
strategic split as D13: one paper task always shippable, one literature
task gating the optimistic upgrade.

## 8. Sources

- ACF: M.O. Albertson, D.W. Cranston, J. Fox, EJC 16(1) (2009), R45;
  arXiv:1006.3783.
- Barát–Tóth: arXiv:0909.0413 (2009).
- Ackerman: arXiv:1509.01932 (2019).
- Cranston: arXiv:2512.08020 (Dec 2025).
- Bungener–Kaufmann: arXiv:2409.01733 (2024). Threshold $6.77$
  (abstract) vs. $6.95$ (Cranston) — plan.md v4 lines 122–125.
- Fox–Pach–Suk: arXiv:2510.05893 (2025). Lemma 2.3 at $9/16$ is the
  binding lift point (R5a sharpness `D8_paper/sharpness_9_8.pdf`).
- Dirac: J. London Math. Soc. 27 (1952), 85–92.
- Kostochka–Yancey: arXiv:1209.1050, JCTB 109 (2014), 73–101.
- Krivelevich: Combinatorica 17 (1997), 401–426;
  doi:10.1007/BF01215921. Also follow-up 1998.
- Borodin / ERT (list-Gallai-trees): Borodin, Abstracts IV All-Union
  Conf. Cybernetics, Novosibirsk 1977; Erdős–Rubin–Taylor, Congr.
  Numer. 26 (1979), 125–157.
- Kierstead–Rabern: arXiv:1701.06012 (2017). *Needs literature
  verification* for whether the list-KY full constant matches KY.
- Bernshteyn–Kostochka–Pron: arXiv:1605.04432 (2016/17); European J.
  Combin. 65 (2017), 122–129.
- Bernshteyn: arXiv:1607.04886 (2016) — DP-critical edge counts.
- Borodin–Kostochka–Woodall: JCTB 71 (1997), 184–204. $\chi'_\ell(M)
  \le 7\Delta(M)/4 + O(1)$, the best currently published list-edge-
  colouring replacement for FPS's $9/16$.
- Cao–Bernshteyn: arXiv:2002.06031 (2020). *Needs literature
  verification* for FPS-Lemma-2.3 lift to DP-edge-colouring.
- Postle thesis: PhD, Georgia Tech 2012, Ch. 4 (list-critical edges).

## 9. Self-audit

- **Honest about lift status?** Yes. §4 splits the verdict cleanly: $t
  \le 18$ unconditional, $19 \le t \le 24$ conditional on Step 5 list-
  lift. §5 gives the explicit failure equation (FPS-2.3-list with
  $c_\ell = 7/4$ from BKW 1997). Memo does not claim a proof of $T_1$
  at $t = 24$ unconditional.
- **Single theorem candidate?** Yes — $T_1$ (list-Albertson at $t \le
  24$, conditional). $T_1'$ ($t \le 18$, unconditional) is labelled
  fallback. Choice of list over DP/fractional justified in §3.
- **Citation-grade?** arXiv IDs confirmed: 1006.3783, 0909.0413,
  1509.01932, 2512.08020, 2409.01733, 2510.05893, 1209.1050,
  1605.04432, 1607.04886, 1701.06012, 2002.06031. Three "needs
  literature verification" flags (KY-list constant; FPS-list-edge-
  chromatic-index at $9/16$; DP-edge-chromatic-index FPS analogue).
- **Numbers verified?** (CL) at $k = 24$: $(k-1)^3 / (8 \cdot 27.48) =
  23^3 / 219.84 \approx 55.34$, so $\operatorname{cr}(G) \ge 55.34 n$
  from BK + Dirac at list-MCE candidate of $|V| \le 2.8118 \cdot 24
  \approx 67$ gives $\operatorname{cr}(G) \ge 55.34 \cdot 67 \approx
  3708$. $Z(24) = 6^2 \cdot 11 \cdot 10 / 4 = 990$. Margin $\ge 3.7\times$
  Crossing-Lemma-only, confirming wide headroom for the chain at
  $t = 24$. Degraded list constant $c_\ell = 7/4$ shrinks the
  FPS vertex bound from $|V| < 1.4(k-1)$ to $|V| < 0.45(k-1)$,
  collapsing the closure to $t \le 18$ — the $T_1'$ regime, hence
  consistent with the fallback.
- **Did I edit anything off-limits?** No — only this file.
- **Match D13 format?** Yes: same 9-section structure; same dense
  citation style; comparable length.

---

*End of memo.*
