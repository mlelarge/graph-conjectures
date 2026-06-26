# Theorem DT: obligation (a) of the X_P program is a theorem

Date: 2026-06-12.  Companion to `O2B_PRESCRIBED_BRANCHING_2026_06_11.md`
(the A-prime chain) and ledger D30–D32.  Verifier:
`scripts/distinct_tails_theorem_check.py` (all six witnesses).

**Theorem DT.**  Let `D` be the chord contraction of a simple 3-arc-strong
`(1,0)`-near-split host, with a strictly rho-headless `t=u` hard gateway at
`a = (u, v)`.  Let `P_v` be a shortest `v -> rho` path in `D - u`, let
`X_P` be the v-target absorption set (the no-path-to-u closure form,
D30), and let `R = {k in K : k -> rho}`.  Then:

1. `d^-(rho) >= 5` and `|R| >= 3`;
2. `|R cap V(P_v)| <= 1`;
3. at least TWO members of `R` lie in `X_P`, and each contributes a
   `rho`-arc in `delta^+(X_P) \ {a}` — hence `delta^+(X_P) \ {a}`
   carries arcs at `>= 2` DISTINCT TAILS, every label of which is free
   of every `T` with `X_a^T = X_P`.

In particular the in-class single-tail configuration (the round-11 G37
claim) is IMPOSSIBLE.

**Proof.**
(1) The host is 3-arc-strong, so `d^-_host(p), d^-_host(q) >= 3`.  The
chord is the unique `V_1`-internal arc, so
`d^-_D(rho) = d^-_host(p) + d^-_host(q) - 1 >= 5`.
Every `rho`-in-arc of `D` has a `K`-tail: `I \ {rho}`-vertices have none
(`V_1` is independent), `u` has none (strict rho-headlessness), cage
vertices have none (gatedness, C1).  Each `k in K` carries at most TWO
`rho`-labels (one host arc to `p`, one to `q`; the host is simple), so
`|R| >= ceil(5/2) = 3`.

(2) If `v in R` then `P_v = [v, rho]` and `R cap V(P_v) = {v}`.
Otherwise let `m_i` be the `i`-th interior vertex of
`P_v = [v, m_1, ..., m_k, rho]`; `m_i in R` gives a `v -> rho` path of
length `i + 1`, so shortestness forces `i = k`: at most the LAST
interior vertex lies in `R`.

(3) By (1)+(2), `|R \ V(P_v)| >= 2`.  Each such `r` avoids the cage
(gated vertices have no `rho`-arcs), is not `u`, and is never removed by
the `J`-closure: `r in K` keeps its cage hooks, whose heads lie in the
cage `subseteq X` and the cage reaches `u` inside `X`; so `r in X_P`.
Its arc `r -> rho` leaves `X_P`: an exit at tail `r`.  Two distinct such
tails exist.  Label-freeness: any `T` with `X_a^T = X_P` assigns every
`X_P`-vertex an arc INSIDE `X_P` (an out-arc leaving `X_P` would remove
the vertex from `X_a^T`), assigns `u` the arc `a`, and assigns outside
vertices arcs outside; so no boundary arc other than `a` carries a
`T`-label.  QED.

**Corollary (shape of obligation (b)).**  The two guaranteed exits are
`rho`-arcs at distinct `X_P`-internal rho-tails — exactly the T2-style
prescription pair.  Obligation (b) therefore reduces to: choose `T`
(in-`X_P` in-arborescence to `u`, plus `a`, plus an outside
in-arborescence) such that every vertex reaches `rho` in the prescribed
residual `D-hat(T, (r_1,rho), (r_2,rho))`.  Note `U` needs NO
in-`X_P` arborescence (the D31/G40 Edmonds-rooted-2 condition was a
TOOL'S precondition, not a necessity: on the D30 blocker witness the
good pair routes the internal-out-degree-1 vertices straight out
through their own boundary arcs).

**Status of the round-11 G37 claim.**  The claimed in-class single-tail
witness was never checked in.  A faithful reproduction (deleting
`k_4`'s two out-cut arcs from the D17 witness) does produce the
single-tail boundary and `lambda(contraction) = 3` — but
`lambda(host) = 2`: OUT OF CLASS (the G32 failure mode: checking the
contraction's connectivity and not the host's).  Theorem DT shows no
in-class instance can exist, so the G37 graveyard entry records a
refuted-claim, not a refuted-lemma.

---

# Lemma OUT: obligation (b)'s outside part (D33)

**Lemma OUT.**  Setting of Theorem DT; let `r_1, r_2` be the two
DT-exits' tails, let `T = T_in + a + T_out` be ANY tree of the X_P
program (`T_in` an in-`X_P` in-arborescence to `u`, `T_out` ANY
in-arborescence of `D[O u {rho}]` rooted `rho`, where
`O = (V(P_v) \ {rho}) u J`), and let
`D-hat = D-hat(T, (r_1,rho), (r_2,rho))` be the prescribed residual.
Then EVERY `O`-vertex reaches `X_P` in `D-hat`, in at most two steps.

**Proof.**
First, `J` is the ONE-ROUND closure and consists of path-fans: a
`J`-vertex `x` lies in `I`, has no `I`-arcs (V_1-independence) and no
`rho`-arcs, so it is stranded iff `N+(x) subseteq V(P_v)`; all of its
`d+(x) >= 3` arcs are multiplicity-1 arcs onto path vertices.  (No
cascade: no `K`-vertex is removed, because its cage hooks give a path to
`u`; every remaining `I`-vertex starts such a path with an arc to a
remaining `K`-vertex; and `I`-`I` arcs do not exist.)

(1) The path `P_v` avoids `C_u`: it lies in `D-u`, while every
`C_u \ {u}` vertex needs `u` on every path to `rho`.  The closure removes
only `I`-vertices, so `C_u subseteq X_P`.  Hence every vertex in
`O cap K` lies in `K \ C_u` and carries ALL
its C3 cage hooks (`>= |K_1| >= 2` arcs into `K cap C_u \ {u}
subseteq X_P`).  No part of `T` can consume a hook: `T_in`-arcs and `a`
have tails in `X_P u {u}`; `T_out`-arcs have heads in `O u {rho}`,
while hooks head the cage; the prescriptions touch only
`r_1, r_2 in X_P`.  So `O cap K` reaches `X_P` in ONE step, for every
choice of `T_out`.

(2) `O cap I` (path-`I` vertices and `J`-vertices): all out-arcs go to
`K`, each with multiplicity 1, and at least three exist
(`lambda >= 3`); `T` consumes exactly ONE of them (the vertex's
`T_out`-arc).  At least two survive; each surviving head lies in
`K cap X_P` (done) or `K cap O` (one more step by (1)).

(3) Equivalently, no nonempty `D-hat`-closed `Y subseteq O` exists: `Y`
can contain no `K`-vertex by (1), hence no `I`-vertex by (2) (its
surviving heads are `K`-vertices outside `Y`).  QED.

**Consequence.**  Obligation (b) of the X_P program REDUCES TO ITS
INSIDE STATEMENT: prove that some `T_in` leaves
`D-hat[X_P]`-reachability of `{r_1, r_2}` from every `X_P`-vertex
(then `r_i -> rho` by prescription; `O`-vertices follow by Lemma OUT,
landing anywhere in `X_P`).  The outside contributes NOTHING further --
no chain bookkeeping, no `J`-leaf analysis, no `T_out` care is needed.
Verifier: `scripts/obligation_b_outside_check.py`.
