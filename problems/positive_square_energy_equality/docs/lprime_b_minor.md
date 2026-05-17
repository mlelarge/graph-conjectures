# Phase 9 (b.minor) — attacking $\delta^-(v^*) \ge 1$ for 2-trees

Companion to `plan_v11.md` step 5e and the Phase 8 sketch in
`lprime_attack_v11.md` §5 ("Next concrete attack"). Phase 9 target,
restated:

> **(b.minor).** Let $G$ be a 2-tree on $n \ge 4$ vertices, $v^*$ the
> max-degsum simplicial degree-2 ear of $G$. Then $\delta^-(v^*) \ge 1$.

This is one step beyond the trivial $\delta^-(v^*) \ge 0$ (which is the
honest interlacing-only floor recorded in `lprime_5e_b_interlacing.md`
§3.2). The numerical floor on the all-2-trees-$n \le 10$ corpus is
$\delta^-(v^*) \ge 1.2941$ (`I}iSSGI@O`, $n = 10$, Case B), so
$\delta^-(v^*) \ge 1$ has slack $\approx 0.29$ at the empirical worst case.

**Honest verdict up front.** Phase 9 does **not** close $\delta^-(v^*) \ge 1$
unconditionally. Phase 9 *does* close two strictly-weaker statements:

1. **Lemma B1 applied at any max-degsum ear of any 2-tree in the corpus
   yields $\alpha_{\min}^2 := \lambda_{\min}(A(G))^2 \ge f_{\min}^2 \ge
   1.833$.** This is a strict lower bound on the *most-negative*
   eigenvalue of $A(G)$, not on $\delta^-(v^*)$. The Phase 8 prompt's
   claim "$\delta^- \ge \alpha^2$ in Case B" is **false**: with the
   correctly-signed slot decomposition, Case B has
   $\delta^- = \alpha_{\text{top}}^2 + \sum \text{(nonneg slot-shifts)}$,
   where $\alpha_{\text{top}}$ is the *least*-magnitude $G$-negative,
   not $\lambda_{\min}$. Empirically $\alpha_{\text{top}}^2$ can be as
   small as $8.6 \cdot 10^{-4}$ on $L_{30}$, so Lemma B1 alone cannot
   close (b.minor).

2. **Empirically, $\delta^-(v^*) \ge 1.294$ holds across a
   2235-record census** covering enumerated 2-trees on $n \in [4, 10]$
   (1476 records), BT$(k, 2)$ for $k \in \{2, 5, 10, 25, 50, 100\}$
   (187 records), books $B_k$ for $k \in [2, 30]$ (464 records),
   $L_n$ for $n \in [4, 30]$ (54 records), and $F_n$ for $n \in [4, 30]$
   (54 records). The headline (b.minor) is therefore strongly
   empirically supported but analytically open.

What Phase 9 *adds*: (i) a corrected slot decomposition for Case B,
(ii) the closed-form lemma "$f_{\min}^2 \ge 1$ iff $|M_1^-| \ge
W^-(1 - W^-)$ when $W^- \le 1$", and (iii) explicit identification of
the open structural step.

---

## 1. Setup and the slot decomposition (corrected)

Let $G$ be a 2-tree on $n \ge 4$ vertices, $v$ a simplicial degree-2
ear with supporting edge $\{a, b\} \in E(H)$ where $H = G - v$.
Order vertices so $v$ is first:
$$A(G) = \begin{pmatrix} 0 & w^\top \\ w & A(H) \end{pmatrix},
\qquad w = e_a + e_b, \qquad \|w\|^2 = 2.$$

Diagonalise $A(H) = \sum_i \mu_i u_i u_i^\top$ with
$\mu_1 \ge \mu_2 \ge \cdots \ge \mu_{n-1}$, set
$c_i = w^\top u_i = u_i(a) + u_i(b)$, so $\sum_i c_i^2 = 2$.
Walk moments $M_k^\pm := \sum_{\mu_i \gtrless 0} c_i^2 \mu_i^k$,
weights $W^\pm := \sum_{\mu_i \gtrless 0} c_i^2$.

Cauchy interlacing gives
$$\lambda_i(G) \ge \mu_i(H) \ge \lambda_{i+1}(G), \qquad i = 1, \ldots, n-1, \tag{C}$$
and $n^-(G) \in \{n^-(H), n^-(H) + 1\}$.

### 1.1 Sign-correct slot decomposition

**Pairing convention.** Pair $\lambda_{i+1}(G)$ with $\mu_i(H)$ for
$i = 1, \ldots, n-1$. By (C), $\lambda_{i+1}(G) \le \mu_i(H)$, hence
when both are negative, $|\lambda_{i+1}| \ge |\mu_i|$, giving
$\lambda_{i+1}^2 - \mu_i^2 \ge 0$.

Writing
$$\delta^-(v) = s^-(G) - s^-(H)
   = \sum_{i=1}^{n} \lambda_i^2 \mathbf 1[\lambda_i < 0]
   - \sum_{i=1}^{n-1} \mu_i^2 \mathbf 1[\mu_i < 0],$$
and re-indexing the $G$-sum by $i \mapsto i + 1$ (using
$\lambda_1 > 0$ for $n \ge 2$, so the $i = 0$ term vanishes), one obtains
$$\boxed{\,\delta^-(v) = \sum_{i=1}^{n-1} \bigl(\lambda_{i+1}^2 \mathbf 1[\lambda_{i+1} < 0]
   - \mu_i^2 \mathbf 1[\mu_i < 0]\bigr).\,} \tag{Slot}$$

- **Case A** ($n^-(G) = n^-(H)$). Every slot $i$ has
  $\lambda_{i+1} < 0 \iff \mu_i < 0$, so each summand reduces to
  $\lambda_{i+1}^2 - \mu_i^2 \ge 0$ (in $J^- := \{i : \mu_i < 0\}$)
  or $0$ (off $J^-$).

- **Case B** ($n^-(G) = n^-(H) + 1$). There is exactly one slot
  $i_0 \notin J^-$ with $\lambda_{i_0+1} < 0$ and $\mu_{i_0} \ge 0$
  (the slot where the extra negative appears in $G$). Set
  $\alpha_{\text{top}} := \lambda_{i_0 + 1}(G) = \lambda_{n - n^-(H)}(G)$
  (the *least*-magnitude $G$-negative). Then
  $$\delta^-(v) = \alpha_{\text{top}}^2 + \sum_{i \in J^-} (\lambda_{i+1}^2 - \mu_i^2),$$
  with each summand $\ge 0$.

### 1.2 Sign mistake in the Phase 8 sketch

The Phase 8 prompt and `lprime_attack_v11.md` informally write Case B as
$$\delta^- = \alpha^2 + \sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2),
\qquad \alpha := \lambda_n(G) = \lambda_{\min}(A(G)),$$
with the claim that the slot-shifts are $\ge 0$. **This is incorrect**:
if $\alpha$ is identified with $\lambda_n = \lambda_{\min}$, then in
the slot pairing the bottom-slot pair $(\lambda_n, \mu_{n-1})$ has
$\lambda_n^2 - \mu_{n-1}^2 \ge 0$ (which is correct), but then the
remaining "new" $\alpha^2$ term double-counts. The corrected
identification is $\alpha_{\text{top}} := \lambda_{n - n^-(H)}$, the
*top* of $G$'s negative spectrum.

**Numerical check on the worst Case B record** (`I}iSSGI@O`, $n = 10$,
$v = 8$, $\delta^- = 1.2941$):

| quantity | value |
|---|---:|
| $\lambda_n(G) = \lambda_{\min}$ | $-2.2179$ |
| $\mu_{n-1}(H)$ | $-2.1136$ |
| $\alpha_{\min}^2 = \lambda_n^2$ | $4.9189$ |
| $\alpha_{\text{top}}^2 = \lambda_{n - n^-(H)}^2 = \lambda_5(G)^2$ | $0.1861$ |
| slot-shift sum $\sum_{i \in J^-}$ | $1.1080$ |
| $\delta^-$ recomputed | $0.1861 + 1.1080 = 1.2941$ ✓ |
| $\lambda_n^2 + \sum (\lambda_{j+1}^2 - \mu_j^2)$ (the *wrong* formula) | $4.9189 + 1.1080 = 6.0269$ ✗ |

So Lemma B1 bounds $\alpha_{\min}^2$, but the relevant quantity in the
slot decomposition is $\alpha_{\text{top}}^2$, which is unrelated to
Lemma B1.

---

## 2. Case A / Case B census (Task 1)

`scripts/case_AB_census.py` produces `data/case_AB_census.json` over the
following 2-tree corpus, restricted to **max-degsum simplicial degree-2
ears**:

- enumerated 2-trees, $n \in [4, 10]$ (724 graphs, 1476 max-degsum
  records when ties are exploded);
- BT$(k, 2)$ for $k \in \{2, 5, 10, 25, 50, 100\}$ (187 records);
- books $B_k$, $k \in [2, 30]$ (464 records);
- 2-paths $L_n$, $n \in [4, 30]$ (54 records);
- fans $F_n$, $n \in [4, 30]$ (54 records).

Total: **2235 records (1945 Case A, 290 Case B)**.

### 2.1 Headline numbers

| statistic | value | argmin |
|---|---:|---|
| $\min \delta^-(v^*)$ overall | $1.2941$ | enum $n=10$, `I}iSSGI@O`, Case B |
| $\min \delta^-(v^*)$ Case A | $1.4144$ | enum $n=10$, `I}iPOgI@O` |
| $\min \delta^-(v^*)$ Case B | $1.2941$ | enum $n=10$, `I}iSSGI@O` |
| $\min \alpha_{\min}^2$ Case B (Lemma B1's target) | $2.6180$ | enum $n=5$, `D}g` |
| $\min \alpha_{\text{top}}^2$ Case B (slot-decomp target) | $0.00086$ | $L_{30}$ endpoint |
| $\min f_{\min}^2$ Case B (Lemma B1 bound on $\alpha_{\min}^2$) | $1.8327$ | enum $n=10$, `I}qcaOH?W` |
| $\min \text{slot\_shift\_max}$ Case A | $0.2771$ | $L_{22}$ endpoint |

### 2.2 Distribution Case A vs Case B

| family | Case A | Case B |
|---|---:|---:|
| enumerated $n \le 10$ | 1250 | 226 |
| BT$(k, 2)$ | 185 | 2 |
| books $B_k$ | 464 | 0 |
| 2-paths $L_n$ | 18 | 36 |
| fans $F_n$ | 28 | 26 |

Books are always Case A (the spine's $\mu_{n-1}(K_{1,k-1}^{++}) = 0$
keeps $n^-$ constant). BT max-degsum ears are also overwhelmingly
Case A. 2-paths and fans are roughly 50/50, with the Case B records
concentrating on shorter 2-paths.

By $n$ within enumeration:

| $n$ | Case A | Case B |
|---:|---:|---:|
| 4  | 2   | 0   |
| 5  | 3   | 2   |
| 6  | 11  | 2   |
| 7  | 23  | 3   |
| 8  | 73  | 15  |
| 9  | 234 | 42  |
| 10 | 904 | 162 |

Case B fraction stabilises around $18\%$ at $n = 10$. The hardest
records (smallest $\delta^-$) are all Case B at $n = 10$.

---

## 3. Task 2 — The Case B route via Lemma B1: why it does not close

### 3.1 Lemma B1 (restated)

For any simplicial degree-2 ear $v$ with $W^-(v) > 0$,
$$\alpha_{\min}^2 := \lambda_{\min}(A(G))^2 \;\ge\; f_{\min}^2 \;:=\;
\left(\frac{|M_1^-(v)| + \sqrt{(M_1^-(v))^2 + 4\,(W^-(v))^3}}{2\,W^-(v)}\right)^2.$$

This is proved in `lprime_attack_v11.md` §2 by a trial-vector
Rayleigh-quotient argument.

### 3.2 The prompt's intended route, and why it fails

The Phase 9 task statement asserts:

> in Case B, $\delta^-(v^*) \ge \alpha^2$ (since the slot-shifts are
> $\ge 0$ and $\alpha^2 \ge f_{\min}^2$). So it suffices to show
> $f_{\min}^2 \ge 1$ at max-degsum ears.

As §1.2 documents, the slot-shifts in Case B with $\alpha := \lambda_n$
are *not* in general $\ge 0$. The sign-correct identification of the
"extra" eigenvalue puts it at the top of $G$'s negatives, not the bottom.
So **the inequality $\delta^- \ge \alpha_{\min}^2$ is empirically false**.
The worst Case B record gives $\delta^- = 1.29 < 4.92 = \alpha_{\min}^2$.

### 3.3 Closed-form analysis of $f_{\min}^2 \ge 1$

**Lemma (sufficient condition for $f_{\min}^2 \ge 1$).**
Suppose $W^- > 0$. Then
$$f_{\min}^2 \ge 1 \quad \Longleftrightarrow \quad |M_1^-| \ge W^-(1 - W^-).$$
(With the convention that the right side is treated as $-\infty$ when
$W^- > 1$, in which case the inequality is automatic.)

*Proof.* $f_{\min}^2 \ge 1 \iff f_{\min} \le -1$ (since $f_{\min} < 0$
when $W^- > 0$ as in `lprime_attack_v11.md` §2), iff
$$|M_1^-| + \sqrt{(M_1^-)^2 + 4(W^-)^3} \ge 2 W^-.$$
If $|M_1^-| \ge 2W^-$, the inequality is trivial. Otherwise
$2W^- - |M_1^-| \ge 0$ and we may square:
$$(M_1^-)^2 + 4(W^-)^3 \ge (2W^- - |M_1^-|)^2
= 4(W^-)^2 - 4W^- |M_1^-| + (M_1^-)^2,$$
which simplifies to $(W^-)^3 \ge (W^-)^2 - W^- |M_1^-|$, i.e.
$|M_1^-| \ge W^- - (W^-)^2 = W^-(1 - W^-)$. $\square$

**Empirical check.** On the entire 2235-record census, every record
with $W^- > 0$ satisfies $|M_1^-| \ge W^-(1 - W^-)$. The worst ratio
$|M_1^-| / (W^-(1 - W^-))$ on max-degsum ears:

- Case B: $2.0951$ (attained on $L_5$, $W^- = 0.5149$, $|M_1^-| = 0.5233$);
- Case A: $2.4173$ (attained on $L_{28}$, $W^- = 0.6061$, $|M_1^-| = 0.5771$).

Hence empirically $f_{\min}^2 \ge $ (something larger than $1$):
the empirical minimum is $f_{\min}^2 = 1.8327$ on Case B max-degsum
records (enum $n=10$, `I}qcaOH?W`) and $1.8327$ across all max-degsum
records.

**Closed-form lower bound on $f_{\min}^2$ at max-degsum ears: open.**
A clique-tree-only structural argument that $|M_1^-(v^*)| \ge
W^-(v^*)(1 - W^-(v^*))$ would close the Lemma B1 step of (b.minor)
*if* the slot-decomposition issue were resolved. It is not.

### 3.4 What the lemma B1 route actually proves

Combining Lemma B1 with §3.3, on every max-degsum ear of every
2-tree in the census,
$$\alpha_{\min}^2 \;\ge\; f_{\min}^2 \;\ge\; 1.8327 > 1.$$
This is a uniform spectral lower bound on the most-negative
eigenvalue of $A(G)$. It is **not** a lower bound on $\delta^-$.
The relation
$$s^-(G) \;\ge\; \alpha_{\min}^2 \;\ge\; 1.8327$$
follows trivially, and gives $\delta^-(v^*) \ge 1.8327 - s^-(H)$,
which is useless when $s^-(H)$ is large.

---

## 4. Task 3 — The Case A slot-sum route: also open

In Case A, by (Slot) the decomposition simplifies to
$$\delta^-(v) = \sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2)$$
with each summand $\ge 0$. The natural per-slot lower bound
$$\delta^- \ge \max_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2)$$
fails: on $L_{22}$ at max-degsum, $\max_j (\lambda_{j+1}^2 - \mu_j^2) =
0.2771 < 1$. The actual $\delta^- = 1.4284$ on $L_{22}$ comes from
the *sum* of many small positive slot-shifts.

### 4.1 Why summing many slot-shifts is hard

For the secular equation in Case A,
$$\lambda - q_H(\lambda) = 0, \qquad q_H(\lambda) = \sum_i \frac{c_i^2}{\lambda - \mu_i},$$
has $|J^-|$ roots in the negative pole intervals. Each root
$\lambda_{j+1}$ sits in the interval $(\mu_j, \mu_{j-1})$ (with
$\mu_0 := +\infty$). The slot-shift $\lambda_{j+1}^2 - \mu_j^2 =
(\lambda_{j+1} - \mu_j)(\lambda_{j+1} + \mu_j)$ depends on (a) how far
$\lambda_{j+1}$ moves up from the pole at $\mu_j$, and (b) the sign and
magnitude of $\mu_{j-1}$.

By the moment constraint $M_1 = w^\top A(H) w = 2$ (since
$\{a, b\} \in E(H)$, so
$w^\top A(H) w = (A(H))_{aa} + 2 (A(H))_{ab} + (A(H))_{bb} = 2$), and
$\sum c_i^2 = 2$, the secular equation embeds a finite trace
constraint, but local slot bounds do not extract a constant uniform
lower bound. **The Case A sum-of-slots bound is the same obstruction
identified in `lprime_5e_b_interlacing.md` §2 and remains open.**

### 4.2 What Case A buys

The genuine non-trivial Case A bound from interlacing alone is:
**$\delta^-(v) \ge 0$** (with equality iff every slot summand is $0$,
which empirically never happens at max-degsum ears).
This was already in `lprime_5e_b_interlacing.md` §3.2. Phase 9 adds
no new floor.

---

## 5. Task 4 — Cannot assemble (b.minor)

With Tasks 2 and 3 both open, the (b.minor) target is not closed by
Phase 9. The closest assembled statement is:

> **Phase 9 partial.** Let $G$ be any 2-tree in the census (enumerated
> $n \le 10$, BT$(k, 2)$ for $k \le 100$, $B_k$ for $k \le 30$, $L_n$
> and $F_n$ for $n \le 30$) and $v^*$ a max-degsum simplicial degree-2
> ear of $G$. Then $\delta^-(v^*) \ge 1.2941$.

This is just the census output; it has no analytical content beyond
the empirical scan.

The properly-stated open obligations:

| step | status |
|---|---|
| Sign-correct (Slot) decomposition | recorded (§1) |
| Lemma B1 gives $\alpha_{\min}^2 \ge f_{\min}^2$ | proved in `lprime_attack_v11.md` §2 |
| Empirically $f_{\min}^2 \ge 1.83$ on max-degsum corpus | recorded (§3.3) |
| Closed-form proof that $|M_1^-(v^*)| \ge W^-(v^*)(1 - W^-(v^*))$ | **open** |
| Bound $\delta^- \ge \alpha_{\text{top}}^2$ in Case B (true but vacuous: $\alpha_{\text{top}}^2$ can be $\approx 10^{-3}$) | recorded as identity, not a useful bound |
| Bound $\sum_{j \in J^-}(\lambda_{j+1}^2 - \mu_j^2) \ge $ const | **open** in both Case A and Case B |
| Conclude $\delta^-(v^*) \ge 1$ | **open** |

---

## 6. Task 5 — Honest verdict

**Did Phase 9 prove $\delta^-(v^*) \ge 1$?** No. Neither unconditionally
nor in Case B alone.

**What Phase 9 produces.**

1. **Sign correction** to the Phase 8 sketch's Case B slot decomposition
   (§1.2). The "new" eigenvalue in Case B is at the top of $G$'s
   negative range ($\alpha_{\text{top}}$), not the bottom
   ($\alpha_{\min}$); Lemma B1 bounds the wrong quantity for the
   intended route.

2. **Closed-form sufficient condition for $f_{\min}^2 \ge 1$**:
   $|M_1^-| \ge W^-(1 - W^-)$ when $W^- \le 1$, automatic when
   $W^- > 1$. Empirically holds with $\ge 2 \times$ margin on the
   2235-record census.

3. **A clean census**, `data/case_AB_census.json`, with 2235 records
   and the explicit Case A / Case B classification, the slot-shift
   sum, $\alpha_{\min}^2$, $\alpha_{\text{top}}^2$, $f_{\min}^2$,
   $(W^-, M_1^-, M_2^-)$. The empirical floor $\delta^-(v^*) \ge
   1.2941$ is uniform across the corpus.

**What would close (b.minor).**

The empirical evidence makes (b.minor) at most one structural step
away. The two routes:

- **Route via $\alpha_{\text{top}}^2$ + slot-sum lower bound.** Combine
  a uniform lower bound on the secular root $\alpha_{\text{top}}$ (Case
  B only) with a uniform lower bound on the slot-shift sum (both Cases).
  The slot-shift sum bound is the same content as condition (b) of the
  v11 candidate ansatz, restricted to threshold $T = 1$ — the
  problem hasn't gotten easier by dropping from $17/16$ to $1$.

- **Route via a global identity.** Find an identity for
  $\delta^-(v)$ from the clique-tree structure of $G$ and a moment
  inequality. The $M_1 = 2$, $M_2(v) = \sigma(v) + 2|T_{ab}(H)|$
  identities are part of this; a closed-form $\delta^-$ in terms of
  $(W^\pm, M_k^\pm)$ alone does not exist (it requires all of
  $A(H)$'s spectral data).

The (b.minor) target is **easier than the headline** $\delta^- \ge 17/16$
by exactly the ratio $1 / (17/16) = 16/17 \approx 0.94$, i.e. by
roughly $6\%$ of slack. Since the empirical floor is $1.2941$ (slack
$0.29$ over $1$, slack $0.23$ over $17/16$), the (b.minor) attack is
*not* a strictly easier proof — it requires the same slot-shift sum
bound as the headline, just with a slightly slacker target.

---

## Files referenced

- `docs/plan_v11.md`
- `docs/lprime_attack_v11.md`
- `docs/lprime_5e_b_interlacing.md`
- `docs/lprime_max_degsum.md`
- `docs/lprime_books.md`
- `docs/lprime_two_paths.md`
- `scripts/case_AB_census.py` (new)
- `scripts/joint_invariant_features.py`
- `scripts/two_tree_enum.py`
- `scripts/extreme_family.py`
- `scripts/spectrum_check.py`
- `data/case_AB_census.json` (new)
- `tests/test_b_minor.py` (new)
