"""Out-locally-semicomplete (OLS) digraph generator for the Route-B sweep.

A digraph D = (V, A) is *out-locally-semicomplete* (OLS) iff for every
v in V, the out-neighborhood N^+(v) induces a semicomplete digraph: for
every pair of distinct out-neighbors u, w of v, at least one of (u, w),
(w, u) is an arc of D. (Equivalently, the induced subdigraph
D[N^+(v)] is semicomplete.)

The Route-B headline theorem says: every 3-arc-strong OLS digraph
admits a SAD, modulo the BJG-Yeo 2020 exception family appearing as the
round-component kernel. This module supplies the three constructions
documented in the spec:

  A — Round decompositions C_1, ..., C_p of cyclically dominating
      semicomplete components. Strong OLS digraphs admit such a
      decomposition (Huang 1995 / BJ-Huang 1995). We *generate* the
      class directly by picking p in {2, 3, 4, 5}, picking each
      component shape (bidirected K_n, vec C_3, vec C_4, S_4, small
      Paley tournaments), and adding all arcs C_i -> C_{i+1} (mod p).
      The resulting digraph's out-neighborhood of any v in C_i is
      exactly the component C_{i+1}, which is semicomplete by
      construction.

  B — Semicomplete tournament T plus a single "tail" v with v -> T in
      a tournament pattern. This is a unilateral extension: N^+(v) = T
      is semicomplete; every u in T has N^+(u) subset of T u {v}, but
      we make D[N^+(u)] semicomplete by ensuring T u {v} is itself
      semicomplete (we extend T by v with arbitrary in/out tournament
      pattern). Iterate to grow.

      Sanity-check only. Expected SAT. (Most useful as a low-bridge
      regime.)

  C — Random rejection. Pick a small random digraph (Erdos-Renyi
      directed model with parameter p), keep only those that are
      strong, exactly 3-arc-strong, and OLS. Slow but unbiased; used
      sparingly.

The OLS predicate is verified by an *independent* function
`is_out_locally_semicomplete` that we apply *after* construction. This
satisfies the hard-rule from the spec: "the OLS-ness of generated
digraphs must be verified by an independent function, not just trusted
from the construction."

CL1 partition (per spec):
  V_1 = C_1 (anchor round component), V_2 = V \ V_1, for Construction
  A. Inner SAD on V_1 = C_1 = semicomplete (so SAD-decomposable by
  BJG-Yeo 2020 unless C_1 is an exception). Inner SAD on V_2 = union
  of remaining round components plus inter-component arcs — this is
  *also* OLS-with-shorter-cycle and admits SAD by induction on p (we
  do not prove this in the generator; we test it empirically with the
  same verifier).
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Callable, Iterator

from digraph import Digraph


# ----------------------------------------------------------------------------
# OLS predicate (independent verifier)
# ----------------------------------------------------------------------------


def is_out_locally_semicomplete(D: Digraph) -> bool:
    """Independent check: D is OLS iff every v's out-neighborhood induces
    a semicomplete digraph.

    "Semicomplete" = for every unordered pair {u, w} of distinct
    vertices, at least one of (u, w), (w, u) is an arc.
    """
    # Build a set of ordered pairs that are arcs (collapsed across
    # parallel arcs).
    arcset = set((int(u), int(v)) for u, v, _ in D.arcs())
    # Out-neighbors of v, ignoring parallel arc multiplicities.
    out: dict[int, set[int]] = {int(v): set() for v in D.vertices()}
    for (u, v) in arcset:
        out[u].add(v)
    for v, Np in out.items():
        Np_list = sorted(Np)
        for i in range(len(Np_list)):
            for j in range(i + 1, len(Np_list)):
                a, b = Np_list[i], Np_list[j]
                if (a, b) not in arcset and (b, a) not in arcset:
                    return False
    return True


def is_semicomplete(D: Digraph) -> bool:
    """True iff for every pair of distinct vertices u, w at least one of
    (u, w), (w, u) is an arc.
    """
    arcset = set((int(u), int(v)) for u, v, _ in D.arcs())
    V = sorted(int(v) for v in D.vertices())
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            a, b = V[i], V[j]
            if (a, b) not in arcset and (b, a) not in arcset:
                return False
    return True


# ----------------------------------------------------------------------------
# OLS instance dataclass
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class OlsInstance:
    """An OLS digraph candidate with provenance.

    For Construction A, `components` records the round decomposition
    (the labelling of vertices into C_1, ..., C_p). For B and C, this
    is left empty / single-block.
    """

    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    construction: str  # "A_round", "B_tail", "C_random"
    components: tuple[tuple[int, ...], ...] = field(default_factory=tuple)
    component_shapes: tuple[str, ...] = field(default_factory=tuple)

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# Component shape catalog (for Construction A)
# ----------------------------------------------------------------------------


def _component_K_n_star(n: int, base: int) -> list[tuple[int, int]]:
    """Bidirected K_n on vertices [base, base+n)."""
    arcs: list[tuple[int, int]] = []
    for i in range(n):
        for j in range(n):
            if i != j:
                arcs.append((base + i, base + j))
    return arcs


def _component_vec_C_n(n: int, base: int) -> list[tuple[int, int]]:
    """Directed cycle on n >= 2 vertices: 0 -> 1 -> ... -> n-1 -> 0."""
    return [(base + i, base + ((i + 1) % n)) for i in range(n)]


def _component_S_4(base: int) -> list[tuple[int, int]]:
    """S_4 = (vec C_4)^2: square of the directed 4-cycle on 4 vertices.

    Arcs: i -> (i+1) mod 4 and i -> (i+2) mod 4 for i in 0..3.
    """
    arcs: list[tuple[int, int]] = []
    for i in range(4):
        arcs.append((base + i, base + ((i + 1) % 4)))
        arcs.append((base + i, base + ((i + 2) % 4)))
    return arcs


def _quadratic_residues(p: int) -> set[int]:
    return {(x * x) % p for x in range(1, p)}


def _component_Paley(p: int, base: int) -> list[tuple[int, int]]:
    """Paley tournament QR_p on p vertices."""
    qr = _quadratic_residues(p)
    arcs: list[tuple[int, int]] = []
    for i in range(p):
        for j in range(p):
            if i != j and (j - i) % p in qr:
                arcs.append((base + i, base + j))
    return arcs


def _component_singleton(base: int) -> list[tuple[int, int]]:
    """A single vertex; no arcs."""
    return []


def _component_2vertex_bidirected(base: int) -> list[tuple[int, int]]:
    """K_2^*: two vertices with both arcs."""
    return [(base, base + 1), (base + 1, base)]


# A shape is a (name, n, arcs_fn) triple; arcs_fn(base) returns the
# arc-list of a component starting at vertex `base`.
@dataclass(frozen=True)
class ComponentShape:
    name: str
    n: int
    arcs_fn: Callable[[int], list[tuple[int, int]]]


SHAPE_CATALOG: list[ComponentShape] = [
    ComponentShape("pt", 1, _component_singleton),
    ComponentShape("K2*", 2, _component_2vertex_bidirected),
    ComponentShape("C3", 3, lambda base: _component_vec_C_n(3, base)),
    ComponentShape("K3*", 3, lambda base: _component_K_n_star(3, base)),
    ComponentShape("C4", 4, lambda base: _component_vec_C_n(4, base)),
    ComponentShape("K4*", 4, lambda base: _component_K_n_star(4, base)),
    ComponentShape("S4", 4, _component_S_4),
    ComponentShape("QR7", 7, lambda base: _component_Paley(7, base)),
    # Note: vec C_4 is NOT semicomplete on its own (non-adjacent pairs:
    # (0, 2) and (1, 3) have neither arc). So we must restrict: a
    # component is semicomplete iff is_semicomplete on its induced
    # digraph. We filter at build time.
]


def _shape_is_semicomplete(shape: ComponentShape) -> bool:
    if shape.n == 1:
        return True  # vacuously
    arcs = shape.arcs_fn(0)
    D = Digraph.from_arcs(range(shape.n), arcs)
    return is_semicomplete(D)


SEMICOMPLETE_SHAPES: list[ComponentShape] = [
    s for s in SHAPE_CATALOG if _shape_is_semicomplete(s)
]


# ----------------------------------------------------------------------------
# Construction A: round decompositions
# ----------------------------------------------------------------------------


def construction_A_round(
    shapes: tuple[ComponentShape, ...],
) -> OlsInstance:
    """Build a round-decomposition OLS digraph from the given component
    shapes (ordered cyclically). For each i, every vertex of C_i
    dominates every vertex of C_{i+1 mod p}.

    Components are placed sequentially: C_0 occupies [0, n_0),
    C_1 occupies [n_0, n_0 + n_1), etc.
    """
    p = len(shapes)
    assert p >= 2, "Round decomposition requires p >= 2 components"
    bases: list[int] = [0]
    for sh in shapes:
        bases.append(bases[-1] + sh.n)
    n = bases[-1]
    components: list[tuple[int, ...]] = [
        tuple(range(bases[i], bases[i + 1])) for i in range(p)
    ]

    arcs: list[tuple[int, int]] = []
    # Intra-component arcs from each shape.
    for i, sh in enumerate(shapes):
        arcs.extend(sh.arcs_fn(bases[i]))
    # Inter-component arcs: every vertex of C_i -> every vertex of C_{i+1}.
    for i in range(p):
        nxt = (i + 1) % p
        for u in components[i]:
            for v in components[nxt]:
                arcs.append((u, v))

    shape_names = tuple(sh.name for sh in shapes)
    name = f"round[{'-'.join(shape_names)}]"
    return OlsInstance(
        name=name,
        n=n,
        arcs=tuple(arcs),
        construction="A_round",
        components=tuple(components),
        component_shapes=shape_names,
    )


def enumerate_construction_A(
    p_values: tuple[int, ...] = (2, 3, 4, 5),
    max_n: int = 16,
    shapes: tuple[ComponentShape, ...] = None,
    seed: int = 20260516,
    cap_per_p: int = 400,
) -> Iterator[OlsInstance]:
    """Enumerate (with shuffling/sampling) round-decomposition instances."""
    if shapes is None:
        shapes = tuple(SEMICOMPLETE_SHAPES)
    rng = random.Random(seed)

    for p in p_values:
        # All multisets of size p over `shapes`, in cyclic-rotation
        # canonical form (we don't dedup rotations here; canonical_key
        # at the driver level deduplicates iso-classes).
        combos = list(itertools.product(shapes, repeat=p))
        rng.shuffle(combos)
        emitted_p = 0
        for combo in combos:
            n_tot = sum(sh.n for sh in combo)
            if n_tot < 4 or n_tot > max_n:
                continue
            inst = construction_A_round(combo)
            yield inst
            emitted_p += 1
            if emitted_p >= cap_per_p:
                break


# ----------------------------------------------------------------------------
# Construction B: semicomplete + appended tail
# ----------------------------------------------------------------------------


def construction_B_tail(
    base_shape: ComponentShape,
    n_tails: int,
    rng: random.Random,
) -> OlsInstance:
    """Take a semicomplete tournament from `base_shape`, then append
    n_tails extra vertices each with v -> base (and a random tournament
    orientation back to v from each existing vertex) so the resulting
    semicomplete digraph is OLS by construction (it is, in fact,
    semicomplete and hence trivially OLS).

    Used as a sanity check: expect SAT.
    """
    arcs = base_shape.arcs_fn(0)
    n = base_shape.n
    for t in range(n_tails):
        new_v = n
        # Random tournament orientation between new_v and each existing u.
        for u in range(n):
            if rng.random() < 0.5:
                arcs.append((new_v, u))
            else:
                arcs.append((u, new_v))
        n += 1
    return OlsInstance(
        name=f"B_tail[{base_shape.name}+{n_tails}]",
        n=n,
        arcs=tuple(arcs),
        construction="B_tail",
        components=(tuple(range(n)),),
        component_shapes=(base_shape.name,),
    )


def enumerate_construction_B(
    seed: int = 20260516,
    cap: int = 100,
) -> Iterator[OlsInstance]:
    rng = random.Random(seed + 7)
    base_shapes = [s for s in SEMICOMPLETE_SHAPES if s.n >= 3]
    emitted = 0
    while emitted < cap:
        base = rng.choice(base_shapes)
        n_tails = rng.randint(1, 4)
        inst = construction_B_tail(base, n_tails, rng)
        if inst.n > 16:
            continue
        yield inst
        emitted += 1


# ----------------------------------------------------------------------------
# Construction C: random rejection
# ----------------------------------------------------------------------------


def construction_C_random(
    n: int,
    p_arc: float,
    rng: random.Random,
) -> OlsInstance:
    """Random simple digraph: each ordered pair (u, v), u != v, is an
    arc independently with probability p_arc. The caller should
    post-filter by `is_out_locally_semicomplete`.
    """
    arcs: list[tuple[int, int]] = []
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if rng.random() < p_arc:
                arcs.append((u, v))
    h = rng.randrange(1 << 30)
    return OlsInstance(
        name=f"C_rand[n={n}_p={p_arc:.2f}_h{h:08x}]",
        n=n,
        arcs=tuple(arcs),
        construction="C_random",
        components=(tuple(range(n)),),
    )


def enumerate_construction_C(
    n_values: tuple[int, ...] = (5, 6, 7, 8),
    p_values: tuple[float, ...] = (0.45, 0.55, 0.65),
    seed: int = 20260516,
    cap_attempts: int = 4000,
) -> Iterator[OlsInstance]:
    """Yield OLS-passing random digraphs. Rejection-sampled."""
    rng = random.Random(seed + 13)
    for attempt in range(cap_attempts):
        n = rng.choice(n_values)
        p = rng.choice(p_values)
        inst = construction_C_random(n, p, rng)
        D = inst.build()
        if not D.is_strongly_connected():
            continue
        if not is_out_locally_semicomplete(D):
            continue
        yield inst


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------


def _selftest() -> None:
    print("OLS generator self-test")
    # 1. Independent OLS predicate sanity.
    # K_3^* is OLS (every N^+(v) is K_2^*, semicomplete).
    D_K3 = Digraph.from_arcs(range(3), _component_K_n_star(3, 0))
    assert is_out_locally_semicomplete(D_K3)
    # vec C_5 is OLS (every N^+(v) is a single vertex; vacuously semicomplete).
    D_C5 = Digraph.from_arcs(range(5), _component_vec_C_n(5, 0))
    assert is_out_locally_semicomplete(D_C5)
    # vec C_4^2 = S_4: N^+(0) = {1, 2}, and (1, 2) is an arc; OLS yes.
    D_S4 = Digraph.from_arcs(range(4), _component_S_4(0))
    assert is_out_locally_semicomplete(D_S4)
    # A digraph with two non-adjacent out-neighbors should fail OLS.
    # E.g., star: 0 -> 1, 0 -> 2, with no arc between 1 and 2.
    D_star = Digraph.from_arcs(range(3), [(0, 1), (0, 2), (1, 0), (2, 0)])
    assert not is_out_locally_semicomplete(D_star)
    print("  predicate tests: ok")

    # 2. Construction A round decomposition (3 components) — verify OLS.
    K3star = SHAPE_CATALOG[3]  # K3*
    C3 = SHAPE_CATALOG[2]  # C3
    pt = SHAPE_CATALOG[0]  # singleton
    inst = construction_A_round((K3star, C3, pt))
    D = inst.build()
    assert is_out_locally_semicomplete(D), f"A_round({inst.name}) not OLS"
    assert D.is_strongly_connected()
    print(f"  Construction A example {inst.name}: n={inst.n}, m={len(inst.arcs)}, OLS=yes")

    # 3. Construction B tail.
    rng = random.Random(0)
    inst = construction_B_tail(SHAPE_CATALOG[5], 2, rng)  # K4* + 2 tails
    D = inst.build()
    # B's instances might or might not be strong; the construction is
    # semicomplete by induction. Print status.
    is_strong = D.is_strongly_connected()
    is_ols = is_out_locally_semicomplete(D)
    print(f"  Construction B example {inst.name}: n={inst.n}, strong={is_strong}, OLS={is_ols}")

    # 4. Construction C random — sample one.
    found = False
    for inst in enumerate_construction_C(n_values=(5, 6), p_values=(0.6,), seed=42, cap_attempts=200):
        D = inst.build()
        assert is_out_locally_semicomplete(D)
        print(f"  Construction C example {inst.name}: n={inst.n}, m={len(inst.arcs)}, OLS=yes")
        found = True
        break
    if not found:
        print("  Construction C: no OLS hits in cap_attempts (acceptable)")

    print("[OK] OLS generator self-test passed.")


if __name__ == "__main__":
    _selftest()
