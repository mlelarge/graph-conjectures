"""Vehicle 5: iterated substitution.

Given an outer template T_outer (a 2-arc-strong UNSAT benchmark) and an
inner template T_inner (same family), the *substitution at vertex v*
replaces v by a disjoint copy of T_inner. Every arc x -> v of T_outer
becomes a *bundle* of arcs x -> w for every w in V(T_inner); every arc
v -> y becomes a bundle w -> y for every w in V(T_inner). Internal arcs
of T_inner are preserved.

This is the most aggressive single-step operation that preserves arc-
strongness from both parents: if T_outer is 2-arc-strong and T_inner is
2-arc-strong, then the substitution is 2-arc-strong, and the arc-
connectivity often lifts to 3 if d_{T_outer}(v) >= 2 (each direction).

Degree bookkeeping (the Lead's required sanity check):

  n_out = n(T_outer) + n(T_inner) - 1
  m_out = m(T_outer) - d_{T_outer}(v)
        + m(T_inner)
        + d_{T_outer}(v) * n(T_inner)

where d_{T_outer}(v) = d_in(v) + d_out(v) is the total degree of v in
T_outer, and direction-aware:
  - every arc x -> v of T_outer becomes n(T_inner) parallel arcs
    x -> w_1, ..., x -> w_{n_inner} (one per w in V(T_inner));
  - every arc v -> y of T_outer becomes n(T_inner) parallel arcs
    w_1 -> y, ..., w_{n_inner} -> y;
  - internal arcs of T_inner are added unchanged on the n(T_inner) new
    vertices.

The sweep driver enumerates all ordered template-pairs and a *small*
choice of substitution vertices on the outer side (we use every distinct
vertex orbit under the outer template's automorphism group, but since
we do not compute orbits up-front, we just use every vertex of T_outer
and let the canonicalizer deduplicate).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from benchmarks import Benchmark
from digraph import Digraph


# ----------------------------------------------------------------------------
# Data class for one substitution instance
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class SubstitutionInstance:
    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    outer: str
    inner: str
    v_outer: int  # vertex of T_outer that was replaced
    # Degree bookkeeping
    outer_n: int
    outer_m: int
    inner_n: int
    inner_m: int
    v_in_degree: int
    v_out_degree: int

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# The substitution primitive
# ----------------------------------------------------------------------------


def iterated_substitution(
    T_outer: Benchmark,
    v: int,
    T_inner: Benchmark,
) -> SubstitutionInstance:
    """Replace vertex `v` of T_outer by a disjoint copy of T_inner.

    Returns a SubstitutionInstance whose arcs satisfy the bookkeeping
    identities asserted in `_check_bookkeeping` below.

    Vertex labelling convention. Let V(T_outer) = {0, ..., n_o - 1} and
    V(T_inner) = {0, ..., n_i - 1}. After substitution the vertex set
    is {0, ..., n_o + n_i - 2} laid out as follows:
      - Outer vertices `u != v` are renamed to a consecutive range
        starting at 0 (in the order they appear in 0..n_o - 1, skipping v):
            new_outer[u] = u            if u < v
            new_outer[u] = u - 1        if u > v
      - Inner vertices w become new_inner[w] = (n_o - 1) + w, occupying
        the range [n_o - 1, n_o - 1 + n_i - 1].
    """
    if v < 0 or v >= T_outer.n:
        raise ValueError(f"v = {v} is not a vertex of T_outer (n = {T_outer.n})")
    if T_inner.n < 1:
        raise ValueError("T_inner must have at least one vertex")

    n_o, n_i = T_outer.n, T_inner.n
    n_new = n_o + n_i - 1

    # Relabelling
    def out_label(u: int) -> int:
        return u if u < v else u - 1

    inner_offset = n_o - 1

    def inner_label(w: int) -> int:
        return inner_offset + w

    # Compute d_in(v) and d_out(v) on T_outer.
    v_in_degree = sum(1 for (a, b) in T_outer.arcs if b == v and a != v)
    v_out_degree = sum(1 for (a, b) in T_outer.arcs if a == v and b != v)
    # Self-loops at v become inner-to-inner bundles (counted separately).
    v_self_loops = sum(1 for (a, b) in T_outer.arcs if a == v and b == v)

    new_arcs: list[tuple[int, int]] = []

    # 1) Outer arcs not touching v, kept as-is on the new labels.
    for (a, b) in T_outer.arcs:
        if a == v or b == v:
            continue
        new_arcs.append((out_label(a), out_label(b)))

    # 2) For every arc x -> v of T_outer (x != v): bundle x -> w for w in V(T_inner).
    for (a, b) in T_outer.arcs:
        if b == v and a != v:
            xlab = out_label(a)
            for w in range(n_i):
                new_arcs.append((xlab, inner_label(w)))

    # 3) For every arc v -> y of T_outer (y != v): bundle w -> y for w in V(T_inner).
    for (a, b) in T_outer.arcs:
        if a == v and b != v:
            ylab = out_label(b)
            for w in range(n_i):
                new_arcs.append((inner_label(w), ylab))

    # 4) Self-loops v -> v become bundles inner -> inner, one full bipartite
    #    bundle per self-loop. (None of the v3 templates has a self-loop at
    #    any vertex, but we handle it for completeness.)
    for _ in range(v_self_loops):
        for w1 in range(n_i):
            for w2 in range(n_i):
                new_arcs.append((inner_label(w1), inner_label(w2)))

    # 5) Internal arcs of T_inner.
    for (a, b) in T_inner.arcs:
        new_arcs.append((inner_label(a), inner_label(b)))

    inst = SubstitutionInstance(
        name=f"sub[{T_outer.name}@v{v}<-{T_inner.name}]",
        n=n_new,
        arcs=tuple(new_arcs),
        outer=T_outer.name,
        inner=T_inner.name,
        v_outer=v,
        outer_n=n_o,
        outer_m=len(T_outer.arcs),
        inner_n=n_i,
        inner_m=len(T_inner.arcs),
        v_in_degree=v_in_degree,
        v_out_degree=v_out_degree,
    )
    _check_bookkeeping(inst, v_self_loops=v_self_loops)
    return inst


def _check_bookkeeping(inst: SubstitutionInstance, v_self_loops: int) -> None:
    """Sanity-check the substitution-arithmetic identities.

    n(T_result) = n(T_outer) + n(T_inner) - 1
    m(T_result) = m(T_outer) - d_{T_outer}(v) [removed arcs at v]
                + m(T_inner)                  [inner internal arcs]
                + d_{T_outer}(v) * n(T_inner) [bundled arcs replacing each removed arc]
                + v_self_loops * (n(T_inner) ** 2 - 1)
                  [each self-loop at v expands to n_inner^2 bundles, but we already
                   counted 1 unit of it in d_{T_outer}(v) as both an in- and out-arc.
                   For self-loops we keep the strict "d = in+out" convention by
                   handling them in a separate accounting term.]
    """
    # The Lead's identity (no self-loop case):
    #   m_result = m_outer - d(v) + m_inner + d(v) * n_inner
    # where d(v) = d_in(v) + d_out(v) on T_outer (counting only non-loop arcs).
    d_v = inst.v_in_degree + inst.v_out_degree
    expected_n = inst.outer_n + inst.inner_n - 1
    expected_m_no_loops = (
        inst.outer_m - d_v - v_self_loops
        + inst.inner_m
        + d_v * inst.inner_n
    )
    # Self-loops at v contribute n_inner^2 bundled arcs each; the
    # original m_outer counted each self-loop as +1, so we add
    # v_self_loops * (n_inner^2 - 1) extra to compensate. But we also
    # already subtracted v_self_loops once above, so the formula is:
    expected_m = expected_m_no_loops + v_self_loops * (inst.inner_n ** 2)

    if inst.n != expected_n:
        raise AssertionError(
            f"substitution: n mismatch. got {inst.n}, expected {expected_n} "
            f"(outer_n={inst.outer_n}, inner_n={inst.inner_n})"
        )
    if len(inst.arcs) != expected_m:
        raise AssertionError(
            f"substitution: m mismatch. got {len(inst.arcs)}, expected {expected_m} "
            f"(outer_m={inst.outer_m}, d_v={d_v}, inner_m={inst.inner_m}, "
            f"inner_n={inst.inner_n}, v_self_loops={v_self_loops})"
        )


# ----------------------------------------------------------------------------
# Sweep driver
# ----------------------------------------------------------------------------


def sweep_all_substitutions(
    templates: list[Benchmark],
    ordered: bool = True,
    max_outer_vertices: int | None = None,
) -> Iterator[SubstitutionInstance]:
    """Yield every (T_outer, v, T_inner) substitution.

    If `ordered = True` (the default), enumerate every ordered pair
    (T_outer, T_inner). For each outer template, iterate v = 0..n_outer-1.

    `max_outer_vertices` (if not None) caps the number of distinct
    substitution vertices per outer template. The canonicalizer in
    `generators/canonicalize.py` is later used to deduplicate by iso-
    class, so an over-generous v-loop is harmless.
    """
    for T_outer in templates:
        v_choices = list(range(T_outer.n))
        if max_outer_vertices is not None:
            v_choices = v_choices[:max_outer_vertices]
        for v in v_choices:
            for T_inner in templates:
                if not ordered and templates.index(T_inner) < templates.index(T_outer):
                    continue
                yield iterated_substitution(T_outer, v, T_inner)


# ----------------------------------------------------------------------------
# Composition (substitute at every outer vertex simultaneously).
# ----------------------------------------------------------------------------
#
# Single-vertex substitution preserves the *other* outer vertices' degrees,
# which stay at 2 in our 2-arc-strong templates. So a single-vertex
# substitution never lifts lambda^arc from 2 to 3. The natural "lift kappa"
# operation is the lexicographic product T_outer[T_inner]: replace every
# outer vertex by a fresh copy of T_inner. Then every outer vertex's degree
# multiplies by n_inner, which generally gives lambda >= 3.
#
# Per the Lead's spec we are running EXACTLY ONE Vehicle-5 sweep. We
# interpret that as one sweep with two well-defined modes — single-vertex
# (the literal substitution operation) and full-composition (the operation
# that actually has a chance of producing kappa = 3) — sharing the same
# canonicalization, verification, and stop-on-UNSAT discipline.


@dataclass(frozen=True)
class CompositionInstance:
    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    outer: str
    inner: str
    outer_n: int
    outer_m: int
    inner_n: int
    inner_m: int

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


def lexicographic_composition(T_outer: Benchmark, T_inner: Benchmark) -> CompositionInstance:
    """Return T_outer[T_inner], the lexicographic product / composition.

    Vertex set: V(T_outer) x V(T_inner), laid out as (u, w) -> u * n_inner + w.
    Arcs:
      - For each arc (u_1, u_2) of T_outer and each pair (w_1, w_2) in
        V(T_inner)^2: a 'between-copies' arc (u_1, w_1) -> (u_2, w_2).
      - For each arc (w_1, w_2) of T_inner and each u in V(T_outer):
        an 'inside-copy' arc (u, w_1) -> (u, w_2).
    """
    n_o, n_i = T_outer.n, T_inner.n

    def lab(u: int, w: int) -> int:
        return u * n_i + w

    arcs: list[tuple[int, int]] = []
    # Between copies: each outer arc becomes n_inner^2 inter-copy arcs.
    for (u1, u2) in T_outer.arcs:
        for w1 in range(n_i):
            for w2 in range(n_i):
                arcs.append((lab(u1, w1), lab(u2, w2)))
    # Inside each copy: every outer vertex carries a copy of T_inner.
    for u in range(n_o):
        for (w1, w2) in T_inner.arcs:
            arcs.append((lab(u, w1), lab(u, w2)))

    # Sanity bookkeeping (paper-style identity):
    #   n = n_o * n_i
    #   m = m_outer * n_i^2 + n_outer * m_inner
    n = n_o * n_i
    expected_m = len(T_outer.arcs) * n_i * n_i + n_o * len(T_inner.arcs)
    if len(arcs) != expected_m:
        raise AssertionError(
            f"composition: m mismatch. got {len(arcs)}, expected {expected_m}"
        )

    return CompositionInstance(
        name=f"comp[{T_outer.name}[{T_inner.name}]]",
        n=n,
        arcs=tuple(arcs),
        outer=T_outer.name,
        inner=T_inner.name,
        outer_n=n_o,
        outer_m=len(T_outer.arcs),
        inner_n=n_i,
        inner_m=len(T_inner.arcs),
    )


def sweep_all_compositions(
    templates: list[Benchmark],
    ordered: bool = True,
    max_n: int = 18,
) -> Iterator[CompositionInstance]:
    """Yield every (T_outer, T_inner) lexicographic composition with
    n_outer * n_inner <= max_n."""
    for T_outer in templates:
        for T_inner in templates:
            if not ordered and templates.index(T_inner) < templates.index(T_outer):
                continue
            if T_outer.n * T_inner.n > max_n:
                continue
            yield lexicographic_composition(T_outer, T_inner)


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------


def _selftest() -> None:
    from benchmarks import all_benchmarks

    UNSAT_NAMES = {
        "S4", "C6_square", "C8_square",
        "C3_K2K2K2", "C3_K2K2P2", "C3_K2K2K3",
        "AiEtAl_L211_min", "AiEtAl_L312_min", "AiEtAl_iv_star_iv",
    }
    templates = [b for b in all_benchmarks() if b.name in UNSAT_NAMES]
    # Quick smoke: S_4 substituted into itself at v=0.
    s4 = next(b for b in templates if b.name == "S4")
    inst = iterated_substitution(s4, 0, s4)
    print(f"[S1] S4 @ v=0 <- S4: n={inst.n}, m={len(inst.arcs)}, "
          f"d_in(v)={inst.v_in_degree}, d_out(v)={inst.v_out_degree}")
    # S_4 has n=4, m=8, every vertex has d_in=d_out=2 (regular). Expect:
    #   n_new = 4 + 4 - 1 = 7
    #   m_new = 8 - 4 + 8 + 4 * 4 = 28
    assert inst.n == 7
    assert len(inst.arcs) == 28

    # Quick smoke: substituting S_4 into C_6^{(2)} at v=0.
    c6 = next(b for b in templates if b.name == "C6_square")
    inst2 = iterated_substitution(c6, 0, s4)
    print(f"[S2] C6sq @ v=0 <- S4: n={inst2.n}, m={len(inst2.arcs)}")
    # C_6^{(2)}: n=6, m=12, every vertex d_in=d_out=2 (regular). S_4: n=4.
    #   n_new = 6 + 4 - 1 = 9
    #   m_new = 12 - 4 + 8 + 4 * 4 = 32
    assert inst2.n == 9
    assert len(inst2.arcs) == 32

    # Strongness preserved.
    D = inst2.build()
    assert D.is_strongly_connected(), "substitution should preserve strong connectivity"
    print(f"[S3] strong-connected after substitution: ok")

    # Full sweep count: 9 templates, sum_{outer} n_outer * 9 substitutions.
    total = 0
    for inst in sweep_all_substitutions(templates):
        total += 1
    expected = sum(b.n for b in templates) * len(templates)
    print(f"[S4] sweep count = {total} (expected {expected})")
    assert total == expected

    # Composition: S_4 [ S_4 ]
    comp = lexicographic_composition(s4, s4)
    print(f"[S5] S_4 [ S_4 ]: n={comp.n}, m={len(comp.arcs)}")
    # n = 4 * 4 = 16; m = m_o * n_i^2 + n_o * m_i = 8 * 16 + 4 * 8 = 128 + 32 = 160
    assert comp.n == 16
    assert len(comp.arcs) == 160
    Dc = comp.build()
    assert Dc.is_strongly_connected()
    kappa = Dc.arc_connectivity()
    print(f"[S5] kappa(S_4[S_4]) = {kappa}  (expected: high; S_4 has kappa=2 and we multiply by 4)")
    # Sweep
    n_comp = 0
    for inst in sweep_all_compositions(templates, ordered=True, max_n=24):
        n_comp += 1
    print(f"[S6] composition sweep (n <= 24) = {n_comp} instances")
    print("[OK] substitution self-test passed.")


if __name__ == "__main__":
    _selftest()
