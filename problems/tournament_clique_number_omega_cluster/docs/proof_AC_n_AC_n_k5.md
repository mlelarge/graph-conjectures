# AC_n[AC_n] is 5-ω̄-critical for every odd n ≥ 7  (Conjecture 5.10 at k=5)

`AC_n = Cay(ℤ/n, g)`, `n=2m+1`, `g={1,…,m−1}∪{m+1}`; arc `i→j ⟺ (j−i) mod n ∈ g`.
`T := AC_n[AC_n]` is the lexicographic substitution: vertex `(a,b)`, `a,b∈ℤ/n`, and
`(a,b)→(a',b') ⟺ [a≠a' ∧ (a'−a)∈g]` or `[a=a' ∧ (b'−b)∈g]`. `a` = **outer**, `b` = **inner**.

**Theorem.** For every odd `n≥7`, `T=AC_n[AC_n]` is `5`-ω̄-critical:
`ω̄(T)=5` and `ω̄(T−v)=4` for every vertex `v`. Hence `{AC_n[AC_n] : odd n≥7}` is an
**infinite family of 5-ω̄-critical tournaments** ⇒ **Conjecture 5.10 at k=5**, and
**Question 5.9 fails at k=5**.

`T` is vertex-transitive (`(x,y)↦(x+s,y+t)` are automorphisms), so it suffices to delete
`v=(0,0)`. As in the k=3/k=4 proofs, `ω̄(D)=min over orders ≺ of ω(backedge graph)`; a
backedge clique is a set listed by `≺` in reverse-topological order (every later vertex
beats every earlier one).

Throughout, `c(t) = 3` if `t=0`, `2` if `1≤t≤m`, `1` if `m+1≤t≤2m` — the AC_n
identity-order potential (largest backedge clique with minimum `t`; unique triangle
`{0,m,2m}`, P13).

## 1. Value: `ω̄(T)=5`

**Lower bound `≥5`.** The general lexicographic lower bound (proved in
`proof_omega_AC_n_C3.md`): `ω̄(S[H]) ≥ ω̄(S)+ω̄(H)−1` for any tournaments `S,H`. With
`S=H=AC_n` and `ω̄(AC_n)=3` (P13): `ω̄(T) ≥ 3+3−1 = 5`.

**Upper bound `≤5`.** Order the `n²` vertices ascending by the **merged-sum key**
`(c(a)+c(b), a, b)`. Machine-checked: under this order `ω(backedge graph)=5` for all odd
`n` tested (to `n=49` exact / order via the oracle), and all the arc-facts that bound the
key-class interactions are `n`-independent. This is the `k=5` instance of the
same numerical inequality formerly proposed as H16, proved here only from the special `AC_n`
arithmetic; the value `5` is also independently confirmed by the no-`K6` SAT
oracle (`ω̄<6`) and no-`K5` UNSAT (`ω̄≥5`) on `AC_7[AC_7]`. Hence `ω̄(T)=5`.

## 2. Deletion, lower bound: `ω̄(T−(0,0)) ≥ 4`

`T−(0,0)` **contains the induced sub-tournament** on `{(a,b): a≠0}` (it also retains every `(0,b)`,
`b≠0`); that induced sub-tournament is `(AC_n−0)[AC_n]` (outer with vertex `0` deleted, full inner).
By monotonicity, the lexicographic lower bound, and `ω̄(AC_n−0)=2` (P13 criticality):
`ω̄(T−(0,0)) ≥ ω̄((AC_n−0)[AC_n]) ≥ ω̄(AC_n−0)+ω̄(AC_n)−1 = 2+3−1 = 4.`

## 3. Deletion, upper bound: `ω̄(T−(0,0)) ≤ 4`  (the inner_then_outer order)

Order the `n²−1` survivors ascending by **`inner_then_outer`**:
`key(a,b) = (c(b),\, c(a),\, a,\, b)`  (inner potential first). The **cell** of a vertex is
`χ(a,b) = (c(b),c(a)) ∈ {1,2,3}²`; the deleted `(0,0)` is the only vertex of cell `(3,3)`,
so survivors occupy the **8 cells** `{1,2,3}² \setminus {(3,3)}`.

### 3.1 One vertex per cell

**Within a single cell there are no backedges.** Fix a cell `(β,α)`. Two vertices `(a,b),(a',b')`
in it have `c(b)=c(b')=β` and `c(a)=c(a')=α`, so `b,b'` lie in one of the length-`m` monotone
intervals `[m+1,2m]` (`β=1`) or `[1,m]` (`β=2`) — or `b=b'=0` (`β=3`) — and likewise `a,a'`.
- *Different outer* `a≠a'`: both in one length-`m` interval, so `(a−a') mod n ∈ [m+2,2m]∪[1,m−1]`;
  with the earlier-in-order vertex having the smaller `a`, the backedge condition `(a_{earlier}−a_{later})∈g`
  needs a residue in `[m+2,2m]` — **disjoint from `g`**. No backedge.
- *Same outer, different inner* `a=a', b≠b'`: identically, the inner gap lands in `[m+2,2m]∉g`. No backedge.

Hence **every backedge clique `S` has at most one vertex per cell**, so `|S| ≤ 8`, and `χ`
injects `S` into the `8` cells. It remains to show **no `5` cells host a simultaneous backedge
clique.**

### 3.2 Lemma A: at most 2 cells of inner band `c(b)=3` ... (only `(3,1),(3,2)` remain), and the band caps

Group the 8 cells by inner band `c(b)`: band 1 `= {(1,1),(1,2),(1,3)}`, band 2 `= {(2,1),(2,2),(2,3)}`,
band 3 `= {(3,1),(3,2)}` (cell `(3,3)` deleted). By §3.1, `n_j := |S∩\text{band }j|` counts distinct
occupied cells, so immediately `n₁,n₂ ≤ 3` and `n₃ ≤ 2`. The clean form of `n₃≤2`: band 3 is
`I₃={(a,0):a≠0}=AC_n−0` under the order `[m+1,…,2m,1,…,m]`; within each half (`[m+1,2m]` and `[1,m]`)
consecutive outer gaps land in `[m+2,2m]∉g`, so there is **no backedge inside a half** ⇒ at most one
vertex from each half ⇒ `n₃≤2` (no appeal to P13 needed).

### 3.3 Lemma B: no 5 cells are simultaneously realizable

By §3.1 a backedge clique is a choice of distinct cells plus one representative per cell with all pairs
backward (the higher cell's representative beats the lower's). We record the **beat conditions**: for
representatives `(a_H,b_H)` (higher cell) and `(a_L,b_L)` (lower),

> `(a_H,b_H)` beats `(a_L,b_L)` ⟺ `(a_L−a_H)∈g` if `a_H≠a_L`, else `(b_L−b_H)∈g`.

Different `c(a)` forces different outer band, hence `a_H≠a_L` (outer condition); equal `c(a)` leaves both
possibilities (the cells may share a block). The four **arc-facts** we use repeatedly (`n=2m+1`,
`g={1,…,m−1}∪{m+1}`):
- `a∈[m+1,2m]`: `a∈g ⟺ a=m+1`, and `(−a)≡n−a∈g ⟺ a∈[m+2,2m]`;
- `a∈[1,m]`: `a∈g ⟺ a∈[1,m−1]`, and `(−a)≡n−a∈g ⟺ a=m` (since `n−a∈[m+1,2m]` meets `g` only at `m+1`);
- for `a,a'` in one length-`m` interval the gap `(a−a')` has residue in `[m+2,2m]∪[1,m−1]`, in `g` only
  when `a>a'` with `a−a'≤m−1` (never the wrap value `m+1`).

(The asymmetry between the two bands — `(−a)∈g` selects the *interval* `[m+2,2m]` in band `H` but the single
point `a=m` in band `L` — is genuine; the `c(a)=1↔2` "mirror" triples below close by the band-`L` facts, not
by a naïve swap.)

The 8 cells in key order are `(1,1)≺(1,2)≺(1,3)≺(2,1)≺(2,2)≺(2,3)≺(3,1)≺(3,2)`. We use a fixed list of
**20 infeasible cell-sets** — 10 triples, 10 quadruples. Two facts give `ω̄(T−(0,0))≤4`: (a) **each of the
20 is infeasible** (proved symbolically below, `n`-independent); and (b) **every 5-subset of the 8 cells
contains one of the 20** as a subset — a purely combinatorial statement about these listed cell-sets and the
8 cells (`C(8,5)=56` checks, independent of `n`). Together: any backedge clique injects into the 8 cells
(§3.1), cannot occupy 5 of them (else it would contain an infeasible set), so has `≤4` vertices. We do **not**
claim the list is the *minimal/exact* set of all minimal obstructions — only (a) and (b), which suffice.
We prove each of the 20.

**(I) The 10 triples** form five `c(a)=1 ↔ 2` "mirror" pairs. We give the band-`H` (`c(a)=1`) chain of each
pair in full; the band-`L` (`c(a)=2`) mirror closes by the **same forced-value chain read through the band-`L`
arc-facts** — written out after the list (it is *not* a literal swap: where band `H` forces a coordinate into
`[m+2,2m]`, band `L` forces it to the single value `m`).

- `{(1,1),(1,3),(2,1)}` (≅`{(1,2),(1,3),(2,2)}`): reps `x=(a₁,b₁)∈(1,1)`, `y=(0,b₂)∈(1,3)`, `z=(a₃,b₃)∈(2,1)`.
  `y` beats `x`: `a₁∈g`, `a₁∈[m+1,2m]` ⟹ **`a₁=m+1`**. `z` beats `y`: `(−a₃)∈g`, `a₃∈[m+1,2m]` ⟹
  **`a₃∈[m+2,2m]`** (so `a₃≠m+1=a₁`). `z` beats `x`: same band, `a₃≠a₁` ⟹ `(a₁−a₃)=(m+1−a₃)∈g`; but
  `m+1−a₃∈[m+2,2m]` (mod `n`) ∉ `g`. **Contradiction.**
- `{(1,1),(1,3),(3,1)}` (≅`{(1,2),(1,3),(3,2)}`): reps `x∈(1,1)`, `y=(0,b₂)∈(1,3)`, `z=(a₃,0)∈(3,1)`.
  `y` beats `x` ⟹ `a₁=m+1`. `z` beats `y`: `(−a₃)∈g` ⟹ `a₃∈[m+2,2m]`. `z` beats `x` (same band, `a₃≠a₁`):
  `(m+1−a₃)∈g`, false as above. **Contradiction.**
- `{(1,1),(2,3),(3,1)}` (≅`{(1,2),(2,3),(3,2)}`): reps `x=(a₁,b₁)∈(1,1)`, `y=(0,b₂)∈(2,3)`, `z=(a₃,0)∈(3,1)`.
  `y` beats `x`: `a₁∈g` ⟹ `a₁=m+1`. `z` beats `y`: `(−a₃)∈g` ⟹ `a₃∈[m+2,2m]`. `z` beats `x`:
  `(m+1−a₃)∈g`, false. **Contradiction.**
- `{(2,1),(2,3),(3,1)}` (≅`{(2,2),(2,3),(3,2)}`): identical chain (`x∈(2,1)`, `a₁=m+1`; `z∈(3,1)`,
  `a₃∈[m+2,2m]`; `z` beats `x` needs `(m+1−a₃)∈g`, false). **Contradiction.**
- `{(1,3),(2,1),(2,3)}` (≅`{(1,3),(2,2),(2,3)}`): reps `u=(0,b₁)∈(1,3)`, `v=(a₂,b₂)∈(2,1)`, `w=(0,b₃)∈(2,3)`.
  `v` beats `u`: `(−a₂)∈g`, `a₂∈[m+1,2m]` ⟹ `a₂∈[m+2,2m]`. `w` beats `v`: `w=(0,·)`, `a₂≠0` ⟹ `a₂∈g`, i.e.
  `a₂=m+1` — contradicting `a₂∈[m+2,2m]`. **Contradiction.**

*Band-`L` mirrors.* In each mirror the `c(a)=1` cells become `c(a)=2`, so the outer coordinates lie in
`[1,m]` and the band-`L` arc-facts apply. The first four mirrors `{(1,2),(1,3),(2,2)}`, `{(1,2),(1,3),(3,2)}`,
`{(1,2),(2,3),(3,2)}`, `{(2,2),(2,3),(3,2)}`: `y`(=`(0,·)`) beats `x=(a₁,·)` forces `a₁∈g`, `a₁∈[1,m]` ⟹
`a₁∈[1,m−1]`; `z=(a₃,·)` beaten-condition `(−a₃)∈g`, `a₃∈[1,m]` ⟹ **`a₃=m`** (the band-`L` fact); then `z`
beats `x` within band `L` needs `(a₁−a₃)=(a₁−m)∈g`, but `(a₁−m)≡a₁+m+1∈[m+2,2m]∉g`. **Contradiction.** The
fifth mirror `{(1,3),(2,2),(2,3)}`: `v=(a₂,·)∈(2,2)` beats `u=(0,·)` forces `(−a₂)∈g` ⟹ `a₂=m`; then
`w=(0,·)` beats `v` needs `a₂∈g`, but `a₂=m∉g`. **Contradiction.**

**(II) The 4 "outer-source" quadruples**, each with its explicit chain (`H:=[m+1,2m]`, `L:=[1,m]`; the
`c(a)=3` cell is the outer source `a=0`; cells listed in key order; every step uses the §3.3 arc-facts and is
verified `n`-independent for `m=3..200`):

- `{(1,1),(1,2),(2,1),(2,3)}`: reps `p∈(1,1)` `(a_p∈H)`, `q∈(1,2)` `(a_q∈L)`, `r∈(2,1)` `(a_r∈H)`,
  `s=(0,·)∈(2,3)` (top). `s` beats `p,r` ⟹ `a_p,a_r∈g` ⟹ `a_p=a_r=m+1` (so `p,r` share block `m+1`). Then
  `q≻p` needs `a_q→m+1` `((m+1−a_q)∈g)` while `r≻q` needs `m+1→a_q` `((a_q−(m+1))∈g)` — opposite arcs between
  blocks `a_q` and `m+1`, impossible (tournament antisymmetry). **Contradiction.**
- `{(1,2),(2,1),(2,2),(2,3)}`: reps `p∈(1,2)` `(a_p∈L)`, `q∈(2,1)` `(a_q∈H)`, `r∈(2,2)` `(a_r∈L)`,
  `s=(0,·)∈(2,3)`. `s` beats `q` ⟹ `a_q=m+1`; `s` beats `p,r` ⟹ `a_p,a_r∈[1,m−1]`. `q≻p`:
  `(a_p−(m+1))≡a_p+m∈g` ⟹ `a_p=1`. `r≻q`: `(m+1−a_r)∈g` ⟹ `a_r∈[2,m]`. `r≻p` (both in `L`, `a_r≠1`):
  `(1−a_r)≡2m+2−a_r∈[m+2,2m]∉g` — false. **Contradiction.**
- `{(1,3),(2,1),(2,2),(3,1)}`: reps `p=(0,·)∈(1,3)` (bottom), `q∈(2,1)` `(a_q∈H)`, `r∈(2,2)` `(a_r∈L)`,
  `s=(a_s,0)∈(3,1)` `(a_s∈H)`. Each of `q,r,s` beats `p`: `(−a_q)∈g`⟹`a_q∈[m+2,2m]`, `(−a_r)∈g`⟹`a_r=m`,
  `(−a_s)∈g`⟹`a_s∈[m+2,2m]`. `r≻q` `((a_q−m)∈g)` ⟹ `a_q∈[m+2,2m−1]`. `s≻r` `((m−a_s)∈g)` ⟹ `a_s=2m`. `s≻q`
  (both in `H`, `a_s=2m≠a_q`): `(a_q−2m)≡a_q+1∈[m+3,2m]∉g` — false. **Contradiction.**
- `{(1,3),(2,2),(3,1),(3,2)}`: reps `p=(0,·)∈(1,3)` (bottom), `q∈(2,2)` `(a_q∈L)`, `r=(a_r,0)∈(3,1)`
  `(a_r∈H)`, `s=(a_s,0)∈(3,2)` `(a_s∈L)`. Each of `q,r,s` beats `p`: `(−a_q)∈g`⟹`a_q=m`, `(−a_r)∈g`⟹
  `a_r∈[m+2,2m]`, `(−a_s)∈g`⟹`a_s=m` (so `q,s` share block `m`). `r≻q` `((m−a_r)∈g)` ⟹ `a_r=2m`. `s≻r`:
  `(a_r−a_s)=(2m−m)=m∈g`? No, `m∉g` — false. **Contradiction.**

**(III) The 6 "square" quadruples** are the analogue of the k=4 `(2,2)`-lemma. The base square
`{(1,1),(1,2),(2,1),(2,2)}` has reps in key order `p∈(1,1) ≺ q∈(1,2) ≺ r∈(2,1) ≺ s∈(2,2)`, with outer
coordinates `a_p,a_r∈[m+1,2m]=:H` and `a_q,a_s∈[1,m]=:L`. The six backedges are: `q≻p`, `r≻q`, `s≻r`
(pure outer, distinct bands), `s≻p` (outer), and `r≻p`, `s≻q` (same outer band — these branch on whether
the two reps share a block). Split:

- **`a_r=a_p`** (so `r,p` share a block): then `r≻q` is `(a_q−a_r)=(a_q−a_p)∈g`, while `q≻p` is
  `(a_p−a_q)∈g` — both cannot hold (`AC_n` is a tournament: exactly one of `±(a_p−a_q)` is in `g`).
  **Contradiction.** (Either choice of the `s`–`q` branch.)
- **`a_s=a_q`** (so `s,q` share a block): then `s≻r` is `(a_r−a_s)=(a_r−a_q)∈g`, while `r≻q` is
  `(a_q−a_r)∈g` — both impossible. **Contradiction.**
- **`a_r≠a_p` and `a_s≠a_q`** (all four blocks distinct): now `r≻p` and `s≻q` are outer too, and the six
  conditions include `r≻p, s≻p` (`a_p∈H` beaten by both `a_r∈H` and `a_s∈L`) and `r≻q, s≻q` (`a_q∈L`
  beaten by both `a_r,a_s`). Equivalently `a_r∈H` and `a_s∈L` are **both** common in-neighbours of the pair
  `{a_p∈H, a_q∈L}` — one in each band. This is impossible by **Lemma H17 (§3.6, proved):** for `x∈H`,
  `y∈L`, the set `N^-(x)∩N^-(y)` lies in a single band, so it cannot contain both `a_r∈H` and `a_s∈L`.
  **Contradiction.**

The **six** square quadruples are
`{(1,1),(1,2),(2,1),(2,2)}`, `{(1,1),(1,2),(2,1),(3,2)}`, `{(1,1),(1,2),(3,1),(3,2)}`,
`{(1,1),(2,2),(3,1),(3,2)}`, `{(1,2),(2,1),(2,2),(3,1)}`, `{(2,1),(2,2),(3,1),(3,2)}` (several differ from
the base square in more than one cell — they are **not** "one cell replaced"). What they share is the
**outer-band pattern**: in key order the `c(a)` values alternate `H,L,H,L` (or `L,H,L,H`), i.e. **two cells
in band `H` and two in band `L`**. The base-square argument is therefore generic and applies to all six
verbatim: write the two band-`H` reps and two band-`L` reps; the two *same-band* cell-pairs branch on
block-coincidence:
- **equality branch** (two same-band reps share a block): two of the six backedges become the opposite arcs
  `x→y` and `y→x` between the shared block and a third block — impossible by tournament antisymmetry (exactly
  as the base square's `a_r=a_p` / `a_s=a_q` branches);
- **all-distinct branch** (all four outer coords distinct): the six outer backedges force one band-`H` rep
  and one band-`L` rep to be **common in-neighbours, one in each band, of the other band-`H` and band-`L`
  rep** — impossible by **Lemma H17 (§3.6, proved):** `N^-(x)∩N^-(y)` is single-band for `x∈H,y∈L`.

  **Contradiction** in every branch, for each of the six squares (verified `n`-independent: equality branches
  die by antisymmetry and all-distinct branches are infeasible, `n=7,9,11,…`). 

All 20 listed sets are infeasible, and every 5-cell subset of the 8 contains one; so **no 5 cells are
realizable**. Every case runs on exactly two mechanisms, **both proven**: the outer-source forced-value
chains (I)/(II), explicit above and verified `n`-independent (`m=3..200`), using only the §3.3 arc-facts and
tournament antisymmetry; and the `(2,2)`-square split (III), whose all-distinct branch is **Lemma H17
(§3.6)**. Hence `ω̄(T−(0,0)) ≤ 4`. ∎

### 3.4 Conclusion of §3

By §3.1 a backedge clique uses distinct cells, by §3.3 at most 4 of them, so `ω̄(T−(0,0)) ≤ 4`. ∎

### 3.5 Value upper bound `ω̄(T) ≤ 5` (corollary)

The cell argument §3.1 applies verbatim to all of `T` (9 cells, `(3,3)={(0,0)}` now present). A backedge
clique `K` of `T` either omits `(0,0)` — then `K⊆T−(0,0)`, so `|K|≤4` by §3.4 — or contains `(0,0)`, the
unique cell-`(3,3)` vertex and the `≺`-maximum; then `K\setminus{(0,0)}` is a backedge clique of `T−(0,0)`,
of size `≤4`, so `|K|≤5`. Hence `ω̄(T)≤5`, and with §1's lower bound `ω̄(T)=5`.

### 3.6 Lemma H17 (in-neighbourhood lemma)

> For every `x∈H:=[m+1,2m]` and `y∈L:=[1,m]`, the common in-neighbourhood
> `N^-(x)∩N^-(y)` in `AC_n` lies entirely in one band: it is contained in `[0,m−1]` if
> `δ:=x−y ≤ m`, and in `[m+1,2m−1]` if `δ ≥ m+1`. In particular it never contains both an
> `H`-residue and an `L`-residue.

*Proof.* In `AC_n`, `N^-(v)=v−g`, and `g={1,…,m+1}\setminus\{m\}` is the integer interval `[1,m+1]`
with the point `m` removed. Hence `N^-(v)=[v−m−1,\,v−1]\setminus\{v−m\}` — an arc of `m+1` consecutive
residues minus one interior point.

For `x∈H`: `x−m−1∈[0,m−1]` and `x−1∈[m,2m−1]`, both in `[0,2m]`, so `A_x:=[x−m−1,x−1]` is a genuine
(non-wrapping) interval. For `y∈L`: `y−1∈[0,m−1]` but `y−m−1≡y+m∈[m+1,2m]`, so `A_y:=[y−m−1,y−1]` wraps:
`A_y=[y+m,\,2m]\cup[0,\,y−1]`. Now `N^-(x)∩N^-(y)⊆A_x∩A_y`, and since `y≤m<m+1≤x` we have `x>y`,
`δ=x−y∈[1,2m−1]`. Compute `A_x∩A_y`:

- `A_x∩[0,y−1]=[x−m−1,\,x−1]∩[0,\,y−1]`. As `x−m−1≥0` and `y−1≤x−1`, this is `[x−m−1,\,y−1]`, **nonempty
  iff** `x−m−1≤y−1`, i.e. `δ=x−y≤m`. When `δ≤m` it equals `[x−m−1,\,y−1]⊆[0,\,m−1]`.
- `A_x∩[y+m,\,2m]=[x−m−1,\,x−1]∩[y+m,\,2m]`. As `x−1≤2m−1<2m` and `x−m−1≤y+m` (always, since
  `δ≤2m`), this is `[y+m,\,x−1]`, **nonempty iff** `y+m≤x−1`, i.e. `δ≥m+1`. When `δ≥m+1` we also get
  `x=y+δ≥1+(m+1)=m+2`, so `x−1≥m+1`, and it equals `[y+m,\,x−1]⊆[m+1,\,2m−1]`.

The two ranges `δ≤m` and `δ≥m+1` are exclusive, and exactly one of the two pieces is nonempty in each.
Therefore `N^-(x)∩N^-(y)⊆A_x∩A_y` is contained in `[0,m−1]` (band `L∪\{0\}`, no `H`) when `δ≤m`, and in
`[m+1,2m−1]` (band `H`, no `L`) when `δ≥m+1`. ∎  *(Verified exhaustively for all `x∈H,y∈L`, odd `n` to
`n=39`.)*

## 4. Criticality and Conjecture 5.10 at k=5

Combining §2–§3, `ω̄(T−(0,0)) = 4`; by vertex-transitivity `ω̄(T−v)=4` for every `v`. With
`ω̄(T)=5` (§1), `T=AC_n[AC_n]` is **5-ω̄-critical** for every odd `n≥7`. Distinct `n` give
distinct orders, so this is an infinite family ⇒ **Conjecture 5.10 holds at k=5**.

**Question 5.9 at k=5.** Every proper subtournament `A⊊T` omits a vertex `v`, so `A⊆T−v`
and `ω̄(A) ≤ ω̄(T−v) = 4` by monotonicity. Thus the only subtournament of `T` certifying
`ω̄≥5` is `T` itself, of order `n²`, which is unbounded ⇒ no `ℓ(5)` exists, i.e.
**Question 5.9 fails at k=5.**

## 5. Verification status

- **Fully symbolic:** value lower bound `≥5` (lex lemma + P13); deletion lower bound `≥4`
  (induced `(AC_n−0)[AC_n]`); **§3.1 one vertex per cell** (no backedge within a cell — the
  monotone-`m`-interval/`[m+2,2m]∉g` argument, no P13 needed); the band caps `n₁,n₂≤3`,
  `n₃≤2` (§3.2, the clean half-interval argument); the Q5.9 monotonicity argument.
- **Casework (§3.3):** `ω̄(T−(0,0))≤4 ⟺` no 5 of the 8 cells realizable `⟺` the **20 listed
  infeasible cell-sets** are infeasible. All 20 are derived in full by two **proven** mechanisms —
  the outer-source forced-value chains (§3.3 (I) 10 triples + (II) 4 quads, every step an explicit
  `n`-independent arc-fact verified `m=3..200`) and the `(2,2)`-square split (§3.3 (III) all six
  squares listed, equality branches → antisymmetry, all-distinct branch → **Lemma H17 (§3.6,
  proved)**). The value bound `ω̄(T)≤5` is a corollary (§3.5). The two load-bearing facts are both
  established without finite extrapolation: (a) each of the 20 sets is **infeasible by a symbolic
  proof** (not a finite `n` check), and (b) **every 5-subset of the 8 cells contains one of the 20**
  — a finite combinatorial fact about the cell-sets (`C(8,5)=56` checks, `n`-independent). We do
  **not** claim the 20 are *exactly* the minimal obstructions (that was only spot-checked to `n=27`
  and is not needed).
- **Reviews (2026-06-07):** (a) 7-skeptic red-team — 0 BROKEN, 1 GAP, a false arc-fact `(−a)∉g`
  for `a∈[1,m]` (truth `(−a)∈g ⟺ a=m`) in the band-`L` mirror triples; fixed. (b) Second review —
  the (II) quads had been *asserted* ("same chains") with finite `n≤27` standing in for proof, and
  the (III) "other five squares replace one `c(b)=2` cell" was *false* (several differ in >1 cell);
  fixed by writing the 4 quad chains explicitly and the correct alternating-`H,L` square abstraction
  (all six listed), each `n`-independent. **Status: COMPLETE — k=5 closed.**

## Relation to the failed general composition law (H16)

The §1/§3 upper bounds have the same numerical form as the formerly proposed general law
`ω̄(S[H]) ≤ ω̄(S)+ω̄(H)−1`, but H16 is false: some width-2 tournament `H` satisfies
`ω̄(C₃[H])=4`. Nothing in the proof here uses that universal statement.

For the much narrower case of **outer `S=AC_n`**, the merged order
`(c_AC(a)+rank_H(b))` is still known to work for `H∈{C₃, AC_n, AC_n−0}`. A uniform
outer-`AC_n` lemma would be a new special theorem and could still support an induction, but it
cannot be inferred from substitution alone; the counterexample shows that additional arithmetic
structure is indispensable.
