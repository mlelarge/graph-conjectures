# D70: Forward-DP lower bound via the toggle-pair fooling set

## 0. What this closes

The D68/D69 rounds chased a polynomial bag-DP for Path-FAS by
compressing the per-bag state: sleeping-block (Section 16),
dormant-matching aggregate (D68), low-hit σ-trace (D69).  Each was
refuted or shown not to compress.  This note proves the **common
cause**: every *forward* score-window DP — any algorithm whose state
after a position-prefix is a function of that prefix — requires
2^Ω(n) states.  The three signature failures are corollaries of one
fundamental lower bound.

This is the negative resolution of the D69 §7 dichotomy: the low-hit
σ-trace does not compress because **no forward signature can**.

## 1. Empirical pre-check (D69 measurement)

On the reversed-matching family (|H| = m, pw(J) = Θ(n)), the low-hit
σ-trace quotient achieves vanishing compression:

| m | n | full DP states | trace classes | ratio |
|---|---|---|---|---|
| 5 | 10 | 70 | 68 | 0.971 |
| 6 | 12 | 151 | 147 | 0.974 |
| 7 | 14 | 357 | 357 | 1.000 |
| 8 | 16 | 864 | 864 | 1.000 |

The ratio → 1; the absolute count grows ≈ 2.6^m.  The trace
reconstructs σ.  This motivated proving a lower bound for *all*
forward signatures, not just the trace.

## 2. The model

A **forward score-window DP** for Path-FAS is any algorithm that:

  * fixes a vertex-processing order consistent with score windows
    (every vertex placed within its radius-2 window — Section 16's
    score-window theorem forces this up to bounded slack);
  * after processing a prefix of placed vertices, summarises it into
    a **state** `σ(prefix)`;
  * the state is **sound**: if `σ(P) = σ(P')` for two prefixes ending
    at the same cut, then for every suffix R, `P · R` is a valid LFO
    iff `P' · R` is.

Sleeping-block (Section 16), J-pathwidth (`docs/J_pathwidth_dp.md`),
dormant aggregate (D68), and low-hit σ-trace (D69) are all instances:
each defines a particular `σ`.  The state count of any such DP is at
least the number of pairwise **extension-distinguishable** prefixes —
prefixes P, P' for which some suffix R extends one but not the other.

## 3. The fooling set

### 3.1. Construction

Toggle-pair family on the prefix vertices (Section 16.1), for k ≥ 4:

    a_i = 2i,   b_i = 2i+1            (i = 0..k-1)   [prefix]
    f_i = 2k+2i, g_i = 2k+2i+1        (i = 0..k-1)   [suffix block]

Transitive base (u → v iff u < v), then reverse f_i → a_i and
g_i → b_i.  For k ≥ 4 these are forced backedges (disjoint windows,
Section 16.1).

**Padding + probe (the suffix that distinguishes).**  Fix a gadget j.
Add `pad = 6` transitive padding vertices above the f/g block, and a
single probe vertex z at the very top, reversing **z → f_j** and
**z → g_j**.  Total n = 4k + 7.

The toggle prefix `P_ε` (ε ∈ {0,1}^k) places pair i as (a_i, b_i) if
ε_i = 0, else (b_i, a_i).

### 3.2. Lemma A (probe window-invariance)

*Adding the padding and the gadget-j probe leaves the score window of
every prefix vertex a_i, b_i unchanged.*

Every prefix vertex has lower index than every padding vertex and the
probe z, and all those arcs keep the transitive orientation
a_i → (pad), a_i → z.  So no prefix vertex gains an in-edge; its
in-degree, hence its radius-2 window, is identical to the base toggle
family.  ∎ (Verified: `verify_prefix_windows_probe_invariant`, k = 4, 5,
0 mismatches.)

Lemma A is the soundness condition for the fooling set: the prefix
processing is **identical** across all probe-j tournaments, so the DP
reaches the same state-candidates regardless of which probe follows.

### 3.3. Lemma B (probe distinguishes its gadget)

*With the gadget-j probe, `P_ε` extends to a valid LFO iff ε_j = 0.*

Within gadget j the only flexible edge is a_j → b_j (overlapping
windows).  If ε_j = 1 the prefix places b_j before a_j, so a_j → b_j is
a backedge and loads; together with the forced f_j → a_j and
g_j → b_j the gadget's back-arc graph is the path
f_j — a_j — b_j — g_j, so **f_j ∼ g_j** (same component).  If ε_j = 0
the gadget contributes the two disjoint edges f_j — a_j and b_j — g_j,
so **f_j ≁ g_j**.

The padding pushes z's window strictly above f_j's and g_j's windows
(d⁻(z) = n − 3, d⁻(f_j), d⁻(g_j) ≤ 2k+2j+1 ≤ 4k − 1, and pad = 6
forces disjointness), so z → f_j and z → g_j are **forced backedges**:
they load in every valid LFO.  They give z degree 2 and raise f_j, g_j
to degree 2.

  * ε_j = 1: f_j ∼ g_j already; the two probe loads z–f_j, z–g_j close
    the cycle z — f_j — a_j — b_j — g_j — z.  No valid LFO.  **Not
    extendable.**
  * ε_j = 0: f_j ≁ g_j; the probe joins the two components through z
    into one path a_j — f_j — z — g_j — b_j.  Linear forest preserved.
    **Extendable.**

∎ (Verified: `verify_fooling_set`, k = 4 (64 checks) and k = 5 (160
checks), 0 violations.)

### 3.4. Theorem (forward-DP lower bound)

*Any sound forward score-window DP for Path-FAS requires at least
2^k = 2^((n−7)/4) = 2^Ω(n) states on the padded toggle family.*

**Proof.**  Consider the 2^k toggle prefixes {P_ε : ε ∈ {0,1}^k}, all
ending at the cut c = 2k.  By Lemma A every probe-j tournament shares
the same prefix windows, so all P_ε are legitimate prefixes of every
probe tournament.  Take ε ≠ ε′, differing at gadget j.  By Lemma B the
gadget-j suffix R_j extends P_ε iff ε_j = 0, and extends P_{ε′} iff
ε′_j = 0; since ε_j ≠ ε′_j exactly one of P_ε · R_j, P_{ε′} · R_j is a
valid LFO.  Hence P_ε and P_{ε′} are extension-distinguishable, so a
sound DP must assign them different states.  The 2^k prefixes are
therefore pairwise distinct states.  ∎

## 4. Corollaries

**Corollary 4.1 (subsumes Section 16).**  The sleeping-block signature
is a forward signature, so it inherits the 2^Ω(n) bound.  Section 16's
2^(n/4) count is the special case where the state is read off as the
component-equality vector (f_i ∼ g_i).

**Corollary 4.2 (explains D69).**  The low-hit σ-trace is a forward
signature; hence it cannot compress below 2^Ω(n) on the toggle/
reversed-matching families.  The D69 measurement (ratio → 1) is this
bound made visible.

**Corollary 4.3 (subsumes D68).**  The dormant-matching aggregate is a
forward signature; the n = 12 `one_block` refutation is one instance of
the general obstruction.

## 5. Consistency with the FPT-by-|H| theorem (D66)

The padded toggle family has |H| = 2k = (n−7)/2 = Θ(n) forced
backedges (the f_i → a_i and g_i → b_i pairs, plus the two probe arcs).
The D66 theorem pw(J), tw(J) ≤ 8 + 2|H| gives only an Θ(n) width
bound here, so it makes **no** polynomiality claim on this family.  No
contradiction: the FPT-by-|H| algorithm is polynomial exactly when |H|
is bounded, and the toggle family is the large-|H| regime.

Together, D66 and D70 give a clean dichotomy for the forward-DP route:

> Forward score-window DP for Path-FAS is polynomial **iff** |H| is
> bounded.  Bounded |H| ⇒ pw(J) ≤ 8 + 2|H| ⇒ poly DP (D66).
> Unbounded |H| ⇒ 2^Ω(n) states on the toggle family (D70).

## 6. Scope and what it does NOT close

The bound is on **forward** DPs that process vertices in score-window
(position) order and summarise the prefix.  It does **not** rule out:

  * algorithms that process vertices in a non-position order;
  * non-DP algorithms (algebraic, LP/SDP, matroid-intersection style);
  * a polynomial *certificate* checkable without a forward sweep.

So D70 closes the bag-DP positive route that D68/D69 pursued, but does
**not** settle Aboulker Problem 4.4.  It redirects the positive route
to genuinely non-sweep methods, and the negative route to a non-back-arc
hardness encoding (Theorem 6.1 of `docs/reversed_matching_hardness.md`
still blocks back-arc reductions).

## 7. Files and tests

| artefact | location |
|---|---|
| Fooling-set construction + verifier | `scripts/toggle_fooling_set.py` |
| Tests (window-invariance + distinguishability, k = 4) | `tests/test_toggle_fooling_set.py` (6 pass) |
| Empirical k = 5 confirmation | `verify_fooling_set(5)`: 0 / 160 violations |

## 8. Verdict

The forward bag-DP route to Path-FAS ∈ P is **closed**: the toggle-pair
fooling set forces 2^Ω(n) pairwise-distinguishable prefix states, so no
forward score-window DP is polynomial in the large-|H| regime.  This
unifies and explains every signature failure of the D68/D69 rounds.

Combined with D66, the forward-DP route is now completely characterised:
polynomial iff |H| is bounded.  The next positive attempt must be a
non-sweep algorithm; the next negative attempt must avoid back-arc
encodings.
