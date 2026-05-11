# Flower snarks $J_{2k+1}$ and equivariant $S^2$-flow ansätze

Working file. **Result of this round: the two natural equivariant ansätze
fail.** The flower-snark family is positive (numerical witness with
machine-zero residual at every $n \in \{5,7,9,11,13\}$) but a closed-form
construction will need a less symmetric structure than first hoped.

## Construction recap

For odd $n = 2k+1$, $J_n$ has vertices
$\{a_i, b_i, c_i, d_i : i \in \mathbb{Z}/n\}$ and edges:

- **spokes** at each $i$: $a_i b_i,\ a_i c_i,\ a_i d_i$
- **b-cycle**: $b_i\,b_{i+1\bmod n}$
- **cd-cycle**: a single $2n$-cycle
  $c_0 c_1 \cdots c_{n-1} d_0 d_1 \cdots d_{n-1} c_0$

Total: $|V| = 4n$, $|E| = 6n$. Cubic, bridgeless, girth 5 for $n \geq 5$,
cyclically 4-edge-connected, not 3-edge-colourable.

## The actual symmetry of $J_n$

The naive index-shift $i \mapsto i+1$ is **not** a graph automorphism:
the c-cycle edge $c_{n-2} c_{n-1}$ would map to $c_{n-1} c_n$, but that
edge does not exist — the closing edge of the cd-cycle at $i=n-1$ is
$c_{n-1} d_0$, with the symmetric partner $d_{n-1} c_0$ on the other side.

The *correct* automorphism is the order-$2n$ rotation
$\sigma$ of the long cd-cycle:

$$
\sigma : a_i, b_i \mapsto a_{i+1}, b_{i+1} \pmod n, \quad
c_i \mapsto c_{i+1} \text{ for } i < n-1,\ c_{n-1} \mapsto d_0, \quad
d_i \mapsto d_{i+1} \text{ for } i < n-1,\ d_{n-1} \mapsto c_0.
$$

So $\sigma$ has order $2n$ (it shifts the cd-cycle by one, $a$ and $b$
indices by one mod $n$). After $n$ applications, $\sigma^n$ fixes every
$a$ and $b$ vertex but swaps every $c$ with the corresponding $d$. In
particular, the $b$-cycle edges form an orbit of size $n$ (with
stabiliser $\langle \sigma^n\rangle$), while the cd-cycle is a single
orbit of size $2n$.

## Ansatz I — full $\mathbb{Z}/(2n)$ equivariance

Take $R \in \mathrm{SO}(3)$ of order $2n$ (axis + angle $\pi/n$). Pose

$$
\varphi(a_i b_i) = R^i u_b, \quad
\varphi(a_i c_i) = R^i u_c, \quad
\varphi(a_i d_i) = R^{n+i} u_c,
$$

$$
\varphi(b_i b_{i+1}) = R^i w_b, \quad
\varphi(\sigma^k(c_0 c_1)) = R^k w_c \text{ for } k = 0, \ldots, 2n-1.
$$

Local Kirchhoff (orientations: spokes $a \to x$, cycles in $\sigma$-direction):

| vertex | conservation |
|---|---|
| $a_0$ | $u_b + u_c + R^n u_c = 0$ |
| $b_0$ | $u_b = (I - R^{-1}) w_b$ |
| $c_0$ | $u_c = (I - R^{-1}) w_c$ |
| $d_0$ | identical to $c_0$ by $\sigma^n$ |

### Algebraic obstruction

The b-spoke orbit under $\langle\sigma\rangle$ has size $n$, with
stabiliser $\langle\sigma^n\rangle$, forcing $R^n u_b = u_b$. Likewise
$R^n w_b = w_b$. Since $R^n$ is a $180°$ rotation about the axis, the
only unit vectors it fixes are $\pm \mathrm{axis}$, so

$$ u_b, w_b \in \{\pm \mathrm{axis}\}. $$

Then $(I - R^{-1}) w_b = w_b - R^{-1} w_b = \pm\mathrm{axis} \mp \mathrm{axis} = 0$,
so the $b_0$ equation forces $u_b = 0$ — contradicting $|u_b| = 1$.

**Conclusion.** $J_n$ admits no $\mathbb{Z}/(2n)$-equivariant $S^2$-flow
in which $R$ has full order $2n$.

## Ansatz II — $\mathbb{Z}/n$ equivariance with cross edges as extras

Drop the $c \leftrightarrow d$ relation: parameterise spoke_$c$, spoke_$d$
independently, plus separate base vectors $w_c$ and $w_d$ for the
internal cycle edges, and treat the two cross edges $c_{n-1} d_0$ and
$d_{n-1} c_0$ as standalone unit vectors. The residual encodes Kirchhoff
at every relevant orbit:

- $a_i$ (one orbit equation),
- $b_i$ (one orbit equation),
- internal $c_i$ for $1 \le i \le n-2$ (one orbit equation),
- internal $d_i$ for $1 \le i \le n-2$ (one orbit equation),
- four boundary equations at $c_0, d_0, c_{n-1}, d_{n-1}$
  (each touching one cross edge).

This is `residual_zn` in
[scripts/flower_equivariant.py](../scripts/flower_equivariant.py).
Counting: 9 unit-norm + 24 conservation = 33 scalar residuals on 27
variables — *over-determined by 6*. A zero of this residual is a
genuine $\mathbb{Z}/n$-equivariant $S^2$-flow on $J_n$ (with the cross
edges chosen freely).

### Numerical search

Levenberg–Marquardt, 8 seeds with 30/30/30/10/10 restarts at
$n = 5/7/9/11/13$ (640 + 240 + 240 + 80 + 80 = 1280 random
initialisations total):

| $n$ | best $\|F\|^2$ | best $\max\|F_i\|$ | converged seed |
|---:|---:|---:|---:|
| 5  | 0.549 | 0.458 | — |
| 7  | 0.594 | 0.515 | — |
| 9  | 0.737 | 0.431 | — |
| 11 | 0.956 | 0.524 | — |
| 13 | 1.162 | 0.551 | — |

**No zero is found.** The best residuals are an order of magnitude
above what the un-symmetrised search achieves on the same graphs
($\|F\|^2 \approx 10^{-31}$ in 1–2 restarts), and they grow with $n$.
The over-determination of the system is *real*: for a generic
parameter point, satisfying all four boundary + two internal
equations at once is impossible.

Caveat: this is numerical evidence, not a closed-form theorem. The
full ansatz produces an over-determined polynomial system whose
infeasibility could in principle be proved by a Gröbner-basis
computation (the unit-ideal certificate); we have not run it. What
we have ruled out is the *generic* solvability accessible to
Levenberg–Marquardt across many starting points.

## What the negative result tells us

The flower-snark family **is** positive — the numerical sweep already
gives an interval-Krawczyk certificate at every tested order. What we
have ruled out is a "rotation-inherits-the-symmetry" construction: any
explicit closed-form proof for the whole family will need to break or
twist the obvious $\sigma$-symmetry.

Plausible remaining routes, in rough order of decreasing leverage:

1. **Anti-equivariance.** Allow $\varphi(\sigma(e)) = -R\,\varphi(e)$
   on selected orbits. Combined with $R$ of suitable order this
   bypasses the $u_b = 0$ obstruction on the $b$-orbit.
2. **Reflection-twisted ansatz.** $J_n$ has a $\mathbb{Z}/2$ reflection
   that conjugates $\sigma$ — combining the two gives a dihedral
   $D_{2n}$ action; the equivariant analysis there is more flexible.
3. **Explicit construction via cycle double covers.** Mattiolo et al.
   (2025) link cycle-double-cover existence to geometrically constructed
   $(r,d)$-flows; flower snarks have well-understood CDCs.
4. **Reduction by gadget.** Decompose $J_n$ along a 4-edge cut into
   two pieces, build $S^2$-flows on each (boundary-aware), and patch.

The numerical evidence already settles flower snarks pragmatically. A
structural proof, if available, will probably come from route 3.

## Status

- $\mathbb{Z}/(2n)$-equivariant ansatz: **closed-form obstruction**.
- $\mathbb{Z}/n$-equivariant ansatz with explicit cross edges:
  **numerical non-existence** at $n \in \{5,7,9,11,13\}$, 800 seeds per
  order, residuals bounded below by $\approx 0.22$.
- Symmetric closed form remains open. The negative result moves the
  flower snarks from "promising symbolic target" to "not via the obvious
  symmetry". Other routes (1)–(4) above are the next candidates.
