# Review of `plan.md` v2

Date: 2026-05-16.

This review supersedes the previous review of `plan.md` v1.  The current
`plan.md` is already a v2 rewrite responding to that earlier critique.  The
question now is not whether v1 was wrong, but whether v2 is clean enough to
drive a serious mathematical or computational project.

## Verdict

The v2 plan is much better than v1.  It correctly absorbs several major
corrections:

- Cranston's residual cases for `r in {25,26}` are the three exact pairs
  `(25,48)`, `(26,50)`, `(26,51)`, not a broad interval.
- Fox-Pach-Suk's result has two different vertex regimes: the finite
  `1.4k - 0.6` weak-immersion bound and the asymptotic `(1.64-o(1))k`
  bound.
- A weak immersion of `K_k` is not by itself a certificate for Albertson's
  conjecture; the Fox-Pach-Suk crossing argument has a separate crossing-loss
  and crossing-recovery step.
- The current crossing-lemma constant used by Cranston is the
  Bungener-Kaufmann `1/27.48` bound, not Ackerman's older `1/29`.
- Brute enumeration of 25-critical graphs on 48 vertices is correctly demoted
  from a plausible near-term route to a speculative research-grade search.

But the v2 document is still not mathematically clean enough.  The remaining
problems are not cosmetic.  There is a proof-direction error about lower and
upper bounds for `cr(K_t)`, an unjustified use of asymptotic complete-graph
crossing-number bounds at `t=25`, a bad value of `Z(25)`, and several
bibliographic or structural mistakes.  These would corrupt downstream scripts
or search criteria if left in place.

## Major issues

### 1. The proof-direction logic for `cr(K_t)` is wrong

Location: `plan.md`, "A subtle reading issue", especially the paragraph
beginning "Proving Albertson for a new `t` is easier...".

The plan says that for a positive proof "any proven lower bound
`L(t) <= cr(K_t)` can be plugged into the right-hand side."  This is false.

To prove Albertson for chromatic number `t`, one must prove

```text
cr(G) >= cr(K_t).
```

If all we know is a lower bound

```text
L(t) <= cr(K_t),
```

then proving `cr(G) >= L(t)` does not imply `cr(G) >= cr(K_t)`.  It proves a
weaker statement.

What works for a positive proof is either:

- prove `cr(G) >= cr(K_t)` directly, using the actual value; or
- prove `cr(G) >= U(t)` where `U(t)` is a known upper bound for `cr(K_t)`.

This is why proving against the Hill/Zarankiewicz value `Z(t)` works:

```text
cr(K_t) <= Z(t).
```

So `cr(G) >= Z(t)` implies `cr(G) >= cr(K_t)`.  Lower bounds on `cr(K_t)` are
useful for falsification, not for proving Albertson.

The same error reappears in Obstruction O2, where the plan says a new proof
may "work with `underline{cr}(K_t) >= 0.985 Z(t)` as the proven lower bound on
the right-hand side."  That is backwards.  A lower bound on `cr(K_t)` is not
a sufficient right-hand-side target for a positive proof.

### 2. The asymptotic `0.985 Z(t)` lower bound is used as if it were finite

Locations: `plan.md` P3, C2, C3, C5, C6, and several occurrences of
`0.985 * Z(t)`.

Balogh, Lidicky, and Salazar prove an asymptotic statement: the limiting ratio
`cr(K_n)/H(n)` is greater than `0.98559895`.  Cranston cites this as saying
Hill's conjecture is asymptotically tight up to a factor around `0.985`.

That is not the same as a certified lower bound for `cr(K_25)` or `cr(K_26)`.
The plan repeatedly treats

```text
cr(K_t) >= 0.985 Z(t)
```

as an operational finite bound for `t=25,26`.  This is not justified unless
one extracts an explicit finite-`n` certificate from the source paper or its
ancillary computations.  The plan currently does not do that.

For finite counterexample search, the correct workflow is:

1. Record exact known values for `t <= 12`.
2. For `13 <= t <= 26`, record only finite lower bounds that are actually
   proved for those specific `t`.
3. Keep asymptotic constants in a separate column, clearly marked as not
   immediately usable for finite certification.

### 3. `Z(25)` is computed incorrectly

Location: `plan.md`, P3.

The plan states:

```text
Z(25) = 4,050.
```

This is wrong.  From the formula in the plan,

```text
Z(25) = (1/4) floor(25/2) floor(24/2) floor(23/2) floor(22/2)
      = (1/4) * 12 * 12 * 11 * 11
      = 4356.
```

Therefore:

```text
0.985 * Z(25)  = 4290.66
0.9855 * Z(25) = 4292.838
```

not approximately `3989`.  Even if the `0.985` finite-threshold use were
legitimate, the numeric threshold in P3 would still be wrong.

For reference:

```text
Z(24) = 3630
Z(25) = 4356
Z(26) = 5148
```

### 4. The `1.212r` vs. `1.228r` Cranston issue is mishandled

Locations: revision history and Cranston bullet.

The plan says it rejects the reviewer's correction about `1.212r` after
rechecking the arXiv.  That rejection is too strong.

Cranston's paper states in Theorem 1:

```text
1.212r <= |G| <= 1.768r
```

and later proves the cleaner body theorem:

```text
1.228r <= |G| <= 1.768r.
```

The document should distinguish these two layers:

- Theorem 1 gives the headline `1.212r` lower endpoint.
- Theorem 4 gives the body result `1.228r <= |G| <= 1.768r`.
- Additional propositions and tables fill in the remaining finite/improved
  lower endpoint behavior.

Keeping only `1.228r` as if the `1.212r` concern were merely bookkeeping is
misleading.

### 5. The Albertson-Cranston-Fox citation is wrong

Locations: revision history and Critical Reading.

The plan cites:

```text
arXiv:0909.2945
Electron. J. Combin. 17 (2010) R67
```

for Albertson-Cranston-Fox, "Crossings, colorings, and cliques."  This is
wrong.

The correct citation is:

```text
M. O. Albertson, D. W. Cranston, and J. Fox,
"Crossings, colorings, and cliques",
Electronic Journal of Combinatorics 16(1) (2009), Research Paper 45,
arXiv:1006.3783.
```

The local source search and Cranston's own bibliography both confirm
`arXiv:1006.3783`, not `0909.2945`.

### 6. The finite Fox-Pach-Suk threshold is slightly misstated

Locations: Fox-Pach-Suk background bullet and C1.

The arXiv theorem says:

```text
n < 1.4k - 0.6.
```

For integer `n`, this gives:

```text
k = 25: n < 34.4, so n <= 34.
k = 26: n < 35.8, so n <= 35.
```

The SoCG abstract phrases the result as "at most `1.4(k-1)` vertices", which
for `k=25` gives `n <= 33` if interpreted literally.  The plan blends these
forms and writes `n <= 33` for `k=25` while also citing `n < 1.4k - 0.6`.

This does not affect the residual Cranston cases, since `48,50,51` are far
above either threshold.  But the plan should be exact:

- arXiv Theorem 1.2(i): `n < 1.4k - 0.6`;
- SoCG statement: at most `1.4(k-1)` vertices;
- for `k=25`, use `34` if citing the arXiv inequality and `33` only if
  explicitly using the SoCG form.

### 7. Vertex-connectivity is not forced

Location: R1b.

The plan proposes restricting to graphs with "vertex-connectivity equal to 24"
and says "the lower bound is forced."  This is wrong.

For color-critical graphs, strong edge-connectivity properties are available,
and the plan correctly discusses `(t-1)`-edge-connectivity elsewhere.  But
high vertex-connectivity is not forced in general for `t`-critical graphs.
Critical graphs can have small vertex cuts.

Replace this with either:

- edge-connectivity equal to `t-1`; or
- vertex-connectivity as a genuine optional structural restriction, explicitly
  not without loss of generality.

### 8. The heuristic discard rule is invalid

Location: R1c.

The plan says to generate random candidates, compute heuristic upper bounds,
and "discard any `G` for which `overline{cr}(G) >= Z(25)`."

That is not valid.  A heuristic upper bound above `Z(25)` proves nothing about
the true crossing number.  It only says the drawing heuristic failed to find a
small drawing.

Valid discard rules are of the following form:

- discard if a certified lower bound proves `cr(G) >= Z(t)`, which proves the
  strong form for that `G`;
- discard as a likely candidate only heuristically, but do not record this as a
  mathematical elimination.

The current wording would lead a search pipeline to throw away possible
counterexamples because of bad drawings.

### 9. The `K_{t-1}`-minor-free subsection imports Hadwiger as if it were known

Location: Route R3.

The plan says that `K_{t-1}`-minor-free graphs are vacuous for threshold `t`
because Hadwiger says they have chromatic number at most `t-1`.

Hadwiger is open in the relevant range.  This cannot be used as a theorem.
At most the plan can say:

- conditional on Hadwiger, the class is vacuous;
- unconditionally, this is not a useful route unless restricted to ranges where
  Hadwiger is known.

Calling this "folklore" is too casual and mathematically dangerous.

### 10. The Kneser example has the wrong chromatic number

Location: Route R4.

The plan lists `K(2t-1,t-1)` as a sparse `t`-chromatic example.  But Lovasz's
formula gives

```text
chi(K(n,k)) = n - 2k + 2.
```

For `K(2t-1,t-1)` this is

```text
(2t-1) - 2(t-1) + 2 = 3.
```

So this family is 3-chromatic, not `t`-chromatic.  The later general form
`K(2k+t-2,k)` is the correct chromatic-`t` Kneser family.

### 11. The Mycielski crossing-number prediction is incoherent as written

Location: C5 / P2.

The plan says Mycielski graphs are "exponentially sparse in vertices for their
chromatic number" and predicts

```text
overline{cr}(M_t) / Z(t) -> infinity.
```

This needs to be rewritten.  "Sparse in vertices" is the wrong phrase:
iterated Mycielski graphs have exponentially many vertices in the chromatic
number while remaining triangle-free and relatively sparse in edges.  Whether
their crossing numbers force the stated ratio is not established by the text.

If this remains as a pre-registered computational prediction, state it only as
a heuristic conjecture to test, not as an asymptotic fact.

## What is solid in v2

### Cranston residual triples

The v2 correction is right: Cranston's Theorem 2 says that if `G` is
`r`-critical, `r <= 26`, and `cr(G) < cr(K_r)`, then

```text
(r, |G|) in {(25,48), (26,50), (26,51)}.
```

This is the correct finite target for the `t=25,26` discussion.

### Weak immersion correction

The v2 correction of the Fox-Pach-Suk logic is basically right.  A weak
immersion is not a one-line route to `cr(G) >= cr(K_k)`.  The argument needs:

1. a weak immersion scaffold;
2. a bound of the form `cr(G') >= cr(K_r) - error`;
3. recovery of enough crossings from edges outside the immersion subgraph.

Cranston's Appendix A gives the finite form:

```text
cr(G') >= cr(K_r) - n(n-r)(n+2r)/8.
```

The simplified `r^3/2` language is appropriate only in the asymptotic
`n < (1.64-epsilon)r` regime.

### Tractability verdict

The broad tractability rating is fair:

- full Albertson conjecture: `1/10`;
- closing `t=25,26`: at most `2/10`;
- structural subclass result: maybe `3/10`.

I would not raise the finite computational closure above `2/10`.  Exact
crossing-number computation on graphs with roughly 50 vertices and 600 edges is
itself a serious research problem, and enumerating critical graphs at those
orders is not remotely routine.

## Recommended v3 changes

Before implementing scripts or launching computation, make the following
edits.

1. Rewrite the "subtle reading issue" section:
   - upper bounds on `cr(K_t)` are useful for positive proofs;
   - lower bounds on `cr(K_t)` are useful for falsification;
   - asymptotic lower bounds are not finite certificates.

2. Fix all `Z(25)` arithmetic:
   - `Z(25)=4356`;
   - `0.985 Z(25) ~= 4290.66`;
   - `0.98559895 Z(25) ~= 4293.27`.

3. Separate finite and asymptotic complete-graph crossing-number bounds in C6.

4. Replace the ACF citation with:
   - EJC `16(1)` (2009), Research Paper 45;
   - arXiv:`1006.3783`.

5. Distinguish Cranston Theorem 1's `1.212r` headline range from Theorem 4's
   `1.228r` body theorem.

6. Fix the finite Fox-Pach-Suk threshold language for `k=25`.

7. Remove the claim that vertex-connectivity `24` is forced.

8. Correct the R1c heuristic discard rule.

9. Mark the `K_{t-1}`-minor-free route as conditional on Hadwiger, not
   unconditional.

10. Replace `K(2t-1,t-1)` with the correct chromatic-`t` Kneser family
    `K(2k+t-2,k)`.

## Sources checked

- Daniel W. Cranston, "Progress on Albertson's Conjecture", arXiv:`2512.08020`.
- Jacob Fox, Janos Pach, Andrew Suk, "Immersions and Albertson's conjecture",
  arXiv:`2510.05893`; SoCG 2025 version, LIPIcs.SoCG.2025.50.
- Aaron Bungener and Michael Kaufmann, "Improving the Crossing Lemma by
  Characterizing Dense 2-Planar and 3-Planar Graphs", arXiv:`2409.01733`.
- Jozsef Balogh, Bernard Lidicky, Gelasio Salazar, "Closing in on Hill's
  conjecture", arXiv:`1711.08958`, SIAM J. Discrete Math. 33 (2019),
  1261-1276.
- E. de Klerk, J. Maharry, D. V. Pasechnik, R. B. Richter, G. Salazar,
  "Improved bounds for the crossing numbers of K_{m,n} and K_n",
  arXiv:`math/0404142`, SIAM J. Discrete Math. 20 (2006), 189-202.
- M. O. Albertson, D. W. Cranston, J. Fox, "Crossings, colorings, and cliques",
  Electronic Journal of Combinatorics 16(1) (2009), Research Paper 45,
  arXiv:`1006.3783`.
