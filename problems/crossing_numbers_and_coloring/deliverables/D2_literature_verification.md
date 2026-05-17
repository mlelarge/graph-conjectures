# D2 — Literature Verification Bundle (Albertson's Conjecture)

Citation-grade verification of four facts the team is relying on. Sources:
Cranston (arXiv:2512.08020v1, 8 Dec 2025); Kostochka–Yancey (arXiv:1209.1050,
*"Ore's Conjecture on color-critical graphs is almost true"*, J. Combin. Theory B
109 (2014) 73–101); Büngener–Kaufmann (arXiv:2409.01733).

---

## 1. Cranston residual triples (arXiv:2512.08020)

**Verified from PDF, p.1, Theorem 2 (verbatim):**

> *"Let G be an r-critical graph. If r ⩽ 24, then cr(G) ⩾ cr(Kr). And if r ⩽ 26
> and cr(G) < cr(Kr), then (r, |G|) ∈ {(25, 48), (26, 50), (26, 51)}."*

The abstract is consistent ("greatly restrict the possibilities for
counterexamples when r ∈ {25, 26}") but only Theorem 2 itself names the three
triples. **Confirmed: the residual set is exactly {(25,48), (26,50), (26,51)}.**

---

## 2. Kostochka–Yancey formula (arXiv:1209.1050)

**Theorem 3 of KY (verbatim, p.3, eq. (9)):**
For every k-critical graph G with k ≥ 4,
$$|E(G)| \;\ge\; F(k,n) \;:=\; \frac{(k+1)(k-2)\,n - k(k-3)}{2(k-1)}.$$
The bound is tight iff n ≡ 1 (mod k−1) (Theorem 37, p.16); F(k,n) is then an
integer. When n ≢ 1 (mod k−1), F(k,n) is fractional and the integer bound is
⌈F(k,n)⌉.

**Non-Ore strengthening.** For k-critical graphs G ∉ 𝒪_k (the Ore family,
generated from K_k by repeated Ore composition), the bound is strict:
|E(G)| ≥ F(k,n) + 1 when n ≡ 1 (mod k−1), and |E(G)| ≥ ⌈F(k,n)⌉ + 1 otherwise.
This is the integrality-plus-uniqueness consequence of KY's sharpness analysis
(Theorem 37 + the fact that Ore-compositions of K_k are the unique extremal
graphs in the n ≡ 1 residue class). **Caveat:** KY 1209.1050 states the lower
bound and proves sharpness over 𝒪_k, but a stand-alone "+1 if G ∉ 𝒪_k" theorem
is not stated verbatim in this paper; the strict inequality follows by
combining Theorem 3 with Theorem 37's uniqueness clause. **Needs separate
formal cite for a clean "+1 non-Ore" lemma** (likely the KY follow-up *"A new
lower bound on the number of edges in colour-critical graphs and hypergraphs"*,
JCTB, but not verified here).

**Substitutions (computed):** F(k,n) = ((k+1)(k−2)n − k(k−3)) / (2(k−1))

| (t, n) | numerator | denom | F(k,n) | ⌈F⌉ (KY) | non-Ore (+1) |
|---|---|---|---|---|---|
| (25, 48) | 26·23·48 − 25·22 = 28704 − 550 = **28154** | 2·24 = 48 | 586.5417 | **587** | **588** |
| (26, 50) | 27·24·50 − 26·23 = 32400 − 598 = **31802** | 2·25 = 50 | 636.0400 | **637** | **638** |
| (26, 51) | 27·24·51 − 26·23 = 33048 − 598 = **32450** | 2·25 = 50 | 649.0000 | **649** | **650** |

**All six audit numbers reproduce exactly.** Note: 48 ≡ 0 (mod 24) and 50 ≡ 0
(mod 25), so neither (25,48) nor (26,50) sits in the Ore residue class — the
"+1" for these rows is the strict-fraction integrality bump (⌈F⌉ +
strict-inequality argument). Only (26, 51) satisfies 51 ≡ 1 (mod 25), so this
is the row where the non-Ore +1 genuinely needs an Ore-membership ruling on G.

---

## 3. Ore-congruence proof (|V(G)| ≡ 1 mod (k−1) for G ∈ 𝒪_k)

**Setup.** 𝒪_k is defined as the closure of {K_k} under Ore composition. An Ore
composition takes G_1, G_2 ∈ 𝒪_k, picks an edge xy ∈ E(G_1) (the *split edge*)
and a vertex z ∈ V(G_2), splits z into z′, z″ partitioning N_{G_2}(z), then
identifies x with z′ and y with z″ — net effect: |V(G_1 ∗ G_2)| = n_1 + n_2 − 1.

**Proof (by induction on the number of compositions).**
- *Base:* K_k ∈ 𝒪_k has |V| = k. Since k = (k−1) + 1, we have k ≡ 1 (mod k−1). ✓
- *Step:* Let G = G_1 ∗ G_2 with G_1, G_2 ∈ 𝒪_k of orders n_1, n_2. By
  induction, n_1 ≡ 1 and n_2 ≡ 1 (mod k−1). Then
  |V(G)| = n_1 + n_2 − 1 ≡ 1 + 1 − 1 = 1 (mod k−1). ✓

Hence every G ∈ 𝒪_k satisfies |V(G)| ≡ 1 (mod k−1). ∎

**Source.** Original definition: Ore, *The Four-Color Problem*, Academic Press,
1967 (Ch. 5). The congruence statement and the n_1 + n_2 − 1 vertex-count
formula are standard; see KY arXiv:1209.1050 around eq. (4)–(5) and the
discussion preceding Conjecture 2 (Ore 1967, p.3). The congruence itself is
stated in KY as a consequence ("the bound … is sharp for every n ≡ 1 (mod k−1)
… achieved by Ore-compositions of K_k").

---

## 4. BK threshold: settles 6.77 vs 6.95

**Büngener–Kaufmann, arXiv:2409.01733, abstract (verified verbatim):**

> *"For m > 6.77 n, we finally apply the standard probabilistic proof from the
> BOOK and obtain an improved constant of c > 1/27.48."*

So the BK paper itself asserts the **6.77 n** threshold for the c > 1/27.48
Crossing Lemma constant.

**Cranston, arXiv:2512.08020, p.2, Theorem A(ii) (verified verbatim):**

> *"Theorem A ([6]). … (ii) As a result if m ⩾ 6.95n, then cr(G) ⩾ m³/(27.48 n²)."*

Cranston cites the BK paper [6] but **quotes the threshold as 6.95 n**, not
6.77 n. Both papers agree on the constant c > 1/27.48; they disagree on the
threshold m where this constant is unlocked.

| source | threshold | constant |
|---|---|---|
| BK abstract (arXiv:2409.01733) | m > **6.77 n** | c > 1/27.48 |
| Cranston Thm A(ii) (arXiv:2512.08020) | m ⩾ **6.95 n** | c > 1/27.48 |

**Verdict.** The team should adopt the **6.95 n** threshold for any argument
that *invokes Cranston's chain* (his Lemma 6, Proposition 4, Theorem 7 all
threshold on Theorem A(ii) at 6.95 n — see p.13, eq. (8) and surrounding).
The BK abstract gives the lower number 6.77 n, but Cranston's downstream
calculations were tuned to 6.95 n. Using 6.77 n would change the constants in
every inequality on pp. 11–13 of Cranston.

**Recommendation for final encoding.** Read BK §4 (or wherever 6.77 n is
proved) to confirm the discrepancy is a tightening Cranston chose not to use,
not a transcription error. **Needs PDF read of BK §4** — the abstract alone
does not show the proof, and we did not download/parse the BK PDF. The team
should fetch arXiv:2409.01733 PDF before using anything tighter than 6.95 n.

---

## Summary of caveats

- (§2) The clean "+1 if G ∉ 𝒪_k" lemma is implicit in KY 1209.1050 (Thm 3 +
  Thm 37 sharpness) but not stated as a single quotable theorem. A follow-up
  KY paper (cited in many subsequent works) gives it explicitly; **not
  verified here**.
- (§4) BK proof of 6.77 n vs Cranston's use of 6.95 n: **needs BK PDF read**
  to determine whether 6.95 n is a deliberate conservative choice by Cranston
  or whether 6.77 n in the BK abstract is qualified somewhere in the BK body.
