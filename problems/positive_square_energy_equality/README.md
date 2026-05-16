# Positive / Negative Square Energy Equality

Workstream targeting **Conjecture 9.2** of Akbari–Kumar–Mohar–Pragada–Zhang,
*Refinement of a conjecture on positive square energy of graphs*
([arXiv:2506.07264](https://arxiv.org/abs/2506.07264), June 2025).

> Let $G$ be a **connected** graph of order $n$.
> - **(i)** $s^+(G) = n - 1$ iff $G$ is a tree.
> - **(ii)** $s^-(G) = n - 1$ iff $G$ is a tree or a complete graph $K_n$.
>
> where $s^+(G)$ (resp. $s^-(G)$) is the sum of squares of the positive
> (resp. negative) eigenvalues of the adjacency matrix $A(G)$.

This is a refinement of the Elphick–Farber–Goldberg–Wocjan (EFGW) conjecture
$s^\pm(G) \ge n-1$ (open in general; theorem in many classes).

See [docs/plan.md](docs/plan.md) for the strategic plan (currently **v3**, after two
rounds of correction logged in [`docs/review.md`](docs/review.md)) and the tractability
audit.

## Status

**Plan v3 only.** No proof step started.

Honest verdict after the reviews:

- The full conjecture is **not** a 1–3 month project. 9.2(i) does not literally imply
  EFGW for unicyclic graphs, but every natural proof strategy meets the same
  obstruction. 9.2(ii) is strictly harder than (i) because $K_n$ is a second extremal
  point (trees and $K_n$ are both equality families for $s^- = n - 1$).
- EFGW is for **connected** graphs of order $n$ (not "no isolated vertex" — $2K_3$
  is a counterexample to that misstatement).
- The **headline route** of v1 (residue analysis via $P_3$-removal claiming "connected
  residue = single $K_t$") **does not work**: the $17/16$-slack lemma actively selects
  cut vertices, so the residue is naturally a disjoint union of $\ell \ge 1$ cliques.
  Correct accounting gives the crude bound $s^\pm(G) \ge n + k/16 - \ell$. The
  condition $\ell < k/16 + 1$ is *sufficient* for this crude argument but **not
  necessary** for the theorem — for $s^+$ the residue contributes $\sum (n_j - 1)^2$,
  which is generically much larger.
- The source paper handles its hardest cases via $\alpha(G)\omega(G) \le n/17$
  (Thm 8.1), not via connectivity.

What v3 delivers:

- **Corollary A** (9.2(i) for connected claw-free $G$) and **Corollary B**
  (9.2(i) for $\mathrm{diam}(G) \le 2$): short corollaries of Thms 1.1 and 1.2 of
  arXiv:2506.07264. Each is a paragraph; combined as a **clean internal note**, not
  a paper.
- **Research direction:** look for a class-specific lemma controlling $\ell$ under
  valid $P_3$-removal — block graphs, chordal graphs, cactus / unicyclic subclasses,
  or the $\alpha\omega \gg n/17$ regime are the candidates. Each has a specific reason
  it may fail (see plan.md). Open-ended; no estimate.

## Key reading

- arXiv:2506.07264 — source paper (Lemmas 2.4, 3.1–3.2; Thms 1.1–1.3, 7.1, 8.1–8.2; Prop. 9.1; Conjectures 9.1–9.3)
- arXiv:1409.2079 — original Elphick–Farber–Goldberg–Wocjan paper
- arXiv:2303.11930 — Abiad et al., equality cases for $\le 2$ positive eigenvalues
- arXiv:2311.11530 — Elphick–Linz, asymmetry between $s^+$ and $s^-$
- arXiv:2410.09830 — Tang–Liu–Wang, where edge-monotonicity fails
- arXiv:2409.15504 — Zhang, extremal values for the square energies
- arXiv:2409.18220 — Akbari–Kumar–Mohar–Pragada, $3n/4$ lower bound
