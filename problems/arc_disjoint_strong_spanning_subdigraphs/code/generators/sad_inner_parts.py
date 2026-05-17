"""SAD-decomposable 3-arc-strong inner-part library for Phase-4 Vehicle 6.

Each entry is a `SadInnerPart` dataclass exposing:

  * `build()`               -> Digraph
  * `lambda_arc`            advertised arc-connectivity (verified at module
                            import time by `_self_check`)
  * `sad_witness()`         -> (red_arcs, blue_arcs) tuple where each list
                            is a sub-multiset of A(D) that is strongly
                            spanning by construction. This is a *constructed*
                            SAD witness, not solver output; we still cross-
                            verify it on each call.

Entries

  K_n^*   : bidirected complete digraph for n in {3, 4, 5, 6}; lambda = n-1.
            SAD: 2-cycle on each pair is split between colors symmetrically.

  QR_7    : Paley tournament on 7 vertices; lambda = 3 (cross-checked by
            `verify_sat`).

  QR_11   : Paley tournament on 11 vertices; lambda = 5 (Wikipedia /
            arc-connectivity = (n - 1) / 2 for the Paley tournament).

  C3_compositions : C_3[H_1, H_2, H_3] for several non-exception choices.
                    The 2020 BJG-Yeo exceptions are exactly C_3[Kbar_a,
                    Kbar_b, Kbar_c] with (a, b, c) in
                    {(2,2,2), (2,2,3)} plus C_3[Kbar_2, Kbar_2, P2bar] and
                    S_4 itself. Anything outside that list is fair game.

  C4_Kbar3 : C_4[Kbar_3], the 4-cycle composition with 3-vertex independent
             sets in each layer. Total n = 12, m = 36, every arc is a
             cross-layer arc; lambda = 3 by inspection (each layer has
             out-degree 3 from each vertex, deletion of any 2 arcs leaves
             at least one arc to the next layer).

  Cn_tripled : directed cycle on n vertices with each arc tripled (so
               every vertex has out-degree 3 and in-degree 3); Eulerian,
               lambda = 3, SAD by simply giving one copy to color R and
               distributing the remaining two copies of each arc so that
               each color spans (two copies of each arc to one color,
               one to the other; alternating choice along the cycle).

Hard rule: every entry's lambda and SAD witness are independently
verified at module import time by `_self_check` (a single call from the
test driver). If any entry fails, an AssertionError is raised before any
gluing is attempted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from digraph import Digraph


# ----------------------------------------------------------------------------
# Dataclass
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class SadInnerPart:
    """A 3-arc-strong digraph with a constructed SAD witness."""

    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    lambda_arc: int  # advertised; >= 3
    red_idx: tuple[int, ...]  # indices into `arcs` that go in the R class
    blue_idx: tuple[int, ...]  # indices into `arcs` that go in the B class
    family: str = ""

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))

    def sad_witness(self) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        red = [self.arcs[i] for i in self.red_idx]
        blue = [self.arcs[i] for i in self.blue_idx]
        return red, blue


# ----------------------------------------------------------------------------
# K_n^* : bidirected complete digraph
# ----------------------------------------------------------------------------


def make_K_star(n: int) -> SadInnerPart:
    """Bidirected complete digraph K_n^* with n vertices, n*(n-1) arcs.
    SAD: for the 2-cycle on each unordered pair {i, j} (i < j), put i -> j
    in R and j -> i in B. Each color class is then a *tournament*
    orientation of K_n (red = "upward", blue = "downward"), and since
    n >= 3 a transitive tournament is not strong --- so we need to be
    more careful. Instead: each color is the same circular tournament
    "rotation". Construction: arc i -> j is R iff (j - i) mod n is in
    {1, ..., floor((n-1)/2)} (i.e. "forward semicircle"); arc i -> j is
    B iff (j - i) mod n is in {floor((n-1)/2)+1, ..., n-1} ("backward
    semicircle"). For odd n this gives a tournament on each side that is
    a rotational tournament; for even n there's one "diametral" pair and
    we put it in the side that needs it.

    Actually the simplest correct construction: for the 2-cycle on each
    pair {i, j}, put one arc in R and the other in B, choosing the side
    so that the resulting R, B are each Hamiltonian cycles (or contain
    one).

    Easiest: take R = "directed Hamiltonian cycle on 0..n-1" plus enough
    additional arcs to span; B = complement inside K_n^*. We just need
    each color to be strongly connected, which is satisfied for n >= 3
    by giving R the cycle (0, 1, 2, ..., n-1, 0) and B = everything else.
    Both colors then contain a Hamiltonian directed cycle (R explicitly;
    B contains (0, n-1, n-2, ..., 1, 0) which is the reverse Hamilton).
    """
    arcs: list[tuple[int, int]] = []
    arc_index: dict[tuple[int, int], int] = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            arc_index[(i, j)] = len(arcs)
            arcs.append((i, j))

    red_idx: list[int] = []
    blue_idx: list[int] = []
    # Hamilton cycle 0 -> 1 -> ... -> n-1 -> 0 in R.
    red_arcs_set: set[tuple[int, int]] = set()
    for i in range(n):
        j = (i + 1) % n
        red_arcs_set.add((i, j))
    # Reverse Hamilton cycle in B.
    blue_arcs_set: set[tuple[int, int]] = set()
    for i in range(n):
        j = (i - 1) % n
        blue_arcs_set.add((i, j))
    # Allocate the two cycles; remaining arcs (if any) split so each
    # color still has both directions. The simple rule: put arc (i, j)
    # with j == (i + 1) % n in R; (i, j) with j == (i - 1) % n in B;
    # remaining arcs go to R if (j - i) mod n <= n/2 else B.
    half = n // 2
    for (i, j), idx in arc_index.items():
        d = (j - i) % n
        if (i, j) in red_arcs_set:
            red_idx.append(idx)
        elif (i, j) in blue_arcs_set:
            blue_idx.append(idx)
        else:
            if d <= half:
                red_idx.append(idx)
            else:
                blue_idx.append(idx)

    return SadInnerPart(
        name=f"K{n}_star",
        n=n,
        arcs=tuple(arcs),
        lambda_arc=n - 1,
        red_idx=tuple(red_idx),
        blue_idx=tuple(blue_idx),
        family="K_n_star",
    )


# ----------------------------------------------------------------------------
# Paley tournaments QR_p (p prime, p == 3 mod 4)
# ----------------------------------------------------------------------------


def _quadratic_residues(p: int) -> set[int]:
    return {(x * x) % p for x in range(1, p)}


def make_Paley(p: int) -> SadInnerPart:
    """Paley tournament QR_p on p vertices.

    Arcs: i -> j iff (j - i) mod p is a nonzero quadratic residue. Requires
    p prime and p == 3 mod 4 (so -1 is a non-residue, making the
    tournament well-defined).

    Arc-connectivity: (p - 1) / 2 (standard fact about the doubly
    regular Paley tournament).

    SAD: by Bang-Jensen & Yeo 2004 every 2-arc-strong tournament other
    than S_4 has a SAD; for QR_p with p >= 7 we already verify lambda >=
    3 by construction, so the existence of a SAD is guaranteed but we
    leave the witness to the SAT solver (no closed-form SAD that I am
    aware of). We will run `verify_sat` once at module-import time and
    embed the solver's witness into the dataclass.
    """
    qr = _quadratic_residues(p)
    arcs: list[tuple[int, int]] = []
    for i in range(p):
        for j in range(p):
            if i == j:
                continue
            if (j - i) % p in qr:
                arcs.append((i, j))
    # SAD witness will be filled by `_self_check` (solver-derived).
    return SadInnerPart(
        name=f"QR{p}_Paley",
        n=p,
        arcs=tuple(arcs),
        lambda_arc=(p - 1) // 2,
        red_idx=tuple(),
        blue_idx=tuple(),
        family="Paley_tournament",
    )


# ----------------------------------------------------------------------------
# Composition C_m[H_1, ..., H_m]
# ----------------------------------------------------------------------------


def _compose_cycle(
    m: int, sizes: tuple[int, ...], inner_arcs: list[tuple[int, int]]
) -> tuple[int, list[tuple[int, int]]]:
    """C_m[H_1, ..., H_m]. Inter-layer arcs from i to (i+1) mod m for every
    layer pair; intra-layer arcs from `inner_arcs` (already in the global
    vertex numbering).
    """
    assert len(sizes) == m
    starts = [0] * m
    for i in range(1, m):
        starts[i] = starts[i - 1] + sizes[i - 1]
    n = starts[-1] + sizes[-1]
    layers = [list(range(starts[i], starts[i] + sizes[i])) for i in range(m)]
    arcs: list[tuple[int, int]] = []
    for i in range(m):
        nxt = (i + 1) % m
        for u in layers[i]:
            for v in layers[nxt]:
                arcs.append((u, v))
    arcs.extend(inner_arcs)
    return n, arcs


def make_C4_Kbar3() -> SadInnerPart:
    """C_4[Kbar_3]: directed 4-cycle with 3 vertices per layer. n = 12,
    m = 4 * 3 * 3 = 36 arcs, lambda = 3.

    SAD construction. The 4-cycle has layers L_0, L_1, L_2, L_3. Each
    inter-layer "bundle" between L_i and L_{i+1} has 9 arcs (3 tails *
    3 heads). To get a 3-arc-strong subgraph in each color we need every
    layer-bundle to contribute >= 1 arc to each color, so that each
    color contains a directed walk hitting all four layers. We need
    *strong connectivity* in each color, which means each color
    independently realizes a strongly connected subdigraph spanning all
    12 vertices.

    Concrete construction:
      * R color: for each layer L_i, pick a bijection f_i : L_i -> L_{i+1}
        and include the 3 arcs of that bijection. R then contains 4 * 3
        = 12 arcs, forming a union of disjoint directed cycles through
        all 12 vertices (specifically, 3 disjoint 4-cycles when each
        f_i is the identity); since 3 disjoint cycles are not strongly
        connected, we choose the f_i's so that the composition
        f_3 . f_2 . f_1 . f_0 is a single 3-cycle on L_0 (rather than the
        identity), making R into a single Hamilton directed 12-cycle.
        Choose f_0 = f_2 = identity, f_1(k) = k, f_3(k) = (k + 1) mod 3.
        Composition: f_3 . f_2 . f_1 . f_0 (k) = (k + 1) mod 3 — a single
        3-cycle on L_0. So R is one Hamilton cycle of length 12.

      * B color: the remaining 36 - 12 = 24 arcs. To check B is strong:
        in each bundle we have 9 - 3 = 6 arcs (all but the chosen
        bijection edges). Since we have 6 arcs in each bundle, B has
        at least one arc from any vertex of L_i to L_{i+1} (in fact at
        least 2). B is strongly connected because every vertex can reach
        every other along the 4-cycle of bundles using these abundant
        arcs.
    """
    n, arcs_list = _compose_cycle(4, (3, 3, 3, 3), inner_arcs=[])
    # Layers: L_0 = {0,1,2}, L_1 = {3,4,5}, L_2 = {6,7,8}, L_3 = {9,10,11}.

    # Chosen bijections f_i : L_i -> L_{i+1}:
    #   f_0(0)=3, f_0(1)=4, f_0(2)=5    (identity)
    #   f_1(3)=6, f_1(4)=7, f_1(5)=8    (identity)
    #   f_2(6)=9, f_2(7)=10, f_2(8)=11  (identity)
    #   f_3(9)=1, f_3(10)=2, f_3(11)=0  (cyclic shift)
    # Composition f_3 o f_2 o f_1 o f_0:
    #   0 -> 3 -> 6 -> 9 -> 1; 1 -> 4 -> 7 -> 10 -> 2; 2 -> 5 -> 8 -> 11 -> 0.
    # Hamilton 12-cycle through all vertices. Good.
    red_arcs = {
        (0, 3), (1, 4), (2, 5),
        (3, 6), (4, 7), (5, 8),
        (6, 9), (7, 10), (8, 11),
        (9, 1), (10, 2), (11, 0),
    }
    red_idx: list[int] = []
    blue_idx: list[int] = []
    for i, a in enumerate(arcs_list):
        if a in red_arcs:
            red_idx.append(i)
        else:
            blue_idx.append(i)

    return SadInnerPart(
        name="C4_Kbar3",
        n=n,
        arcs=tuple(arcs_list),
        lambda_arc=3,
        red_idx=tuple(red_idx),
        blue_idx=tuple(blue_idx),
        family="composition",
    )


def make_C3_K3_K2_K2() -> SadInnerPart:
    """C_3[Kbar_3, Kbar_2, Kbar_2]: 3-cycle composition with layer sizes
    (3, 2, 2). n = 7, m = 3*2 + 2*2 + 2*3 = 6+4+6 = 16, lambda = 3 (each
    layer-to-next bundle has min(out-fan, in-fan) >= 2; the smallest
    bundle is L_1->L_2 with 2*2 = 4 arcs, so each cut is >= 4 except
    those crossing the in-bundle from L_0 (size 6) and out-bundle to L_0
    from L_2 (size 6). Single-vertex out-cuts have size min(out-degree)
    >= 4 in L_0 (out-degree 2) ... wait. Each L_0 vertex has out-degree
    only 2 (to L_1's two vertices). So actually lambda <= 2 here.

    Let me recompute. L_0 has 3 vertices each with out-deg 2; L_1 has 2
    vertices each with out-deg 2; L_2 has 2 vertices each with out-deg 3.
    So min(out-degree) = 2, hence lambda <= 2. This is NOT 3-arc-strong.

    So skip this one — keep only configurations with min(layer size) >= 3
    OR add intra-layer arcs. Let's leave this function out of the library.
    """
    raise NotImplementedError(
        "C_3[Kbar_3, Kbar_2, Kbar_2] is only 2-arc-strong; not used."
    )


def make_C3_K3_K3_K3() -> SadInnerPart:
    """C_3[Kbar_3, Kbar_3, Kbar_3]: n = 9, m = 27, every vertex out-degree 3
    and in-degree 3. Eulerian. lambda = 3 (each bundle has 9 arcs; any
    out-cut has size >= 3 by inspection: a singleton out-cut has size 3,
    a 2-element subset of one layer has out-cut 6 - 0 = 6 or 6 - (#int arcs)
    but there are no intra-layer arcs so size 6; any cross-layer subset
    similarly >= 3). Not in BJG-Yeo's 2020 exceptions list (those are
    (2,2,2), (2,2,3) for Kbar-only and (2,2,P2)).

    SAD: each bundle L_i -> L_{i+1} has 9 arcs. We want each color to
    contain a strongly connected spanning subdigraph. Construction
    (analogue of C_4[Kbar_3]'s Hamilton-cycle trick):
      Color R: one bijection per bundle, choosing bijections whose
      composition is a single 3-cycle on L_0.
        f_0 = identity (0->3, 1->4, 2->5);
        f_1 = identity (3->6, 4->7, 5->8);
        f_2 = cyclic shift (6->1, 7->2, 8->0).
        Composition f_2 o f_1 o f_0: 0 -> 3 -> 6 -> 1; 1 -> 4 -> 7 -> 2;
                                    2 -> 5 -> 8 -> 0.
      R has 9 arcs forming a single Hamilton 9-cycle. Strong: yes.
      Color B: remaining 18 arcs. Strong: B contains, in each bundle, 6
      arcs (all 9 minus the bijection). Two vertices in the same layer
      can reach each other via the 3-cycle of layers (and B has plenty
      of arcs to choose from in each bundle), so B is strong.
    """
    n, arcs_list = _compose_cycle(3, (3, 3, 3), inner_arcs=[])
    # Layers: L_0 = {0,1,2}, L_1 = {3,4,5}, L_2 = {6,7,8}.
    red_arcs = {
        (0, 3), (1, 4), (2, 5),
        (3, 6), (4, 7), (5, 8),
        (6, 1), (7, 2), (8, 0),
    }
    red_idx: list[int] = []
    blue_idx: list[int] = []
    for i, a in enumerate(arcs_list):
        if a in red_arcs:
            red_idx.append(i)
        else:
            blue_idx.append(i)
    return SadInnerPart(
        name="C3_Kbar3x3",
        n=n,
        arcs=tuple(arcs_list),
        lambda_arc=3,
        red_idx=tuple(red_idx),
        blue_idx=tuple(blue_idx),
        family="composition",
    )


# ----------------------------------------------------------------------------
# C_n with arc multiplicity 3
# ----------------------------------------------------------------------------


def make_Cn_tripled(n: int) -> SadInnerPart:
    """Directed cycle C_n with each arc tripled: vertices 0..n-1, three
    parallel arcs i -> (i+1) mod n for every i. Total arcs = 3n. Every
    vertex has in-degree 3 and out-degree 3 (Eulerian). lambda = 3.

    SAD construction. We need each color to be strongly spanning, i.e.,
    contain a directed Hamilton-or-spanning cycle. The directed cycle
    itself needs n arcs to span. We have 3 copies of each of n arcs =
    3n arcs total. Allocate 2 copies to R and 1 copy to B for *every*
    arc. Then R contains 2n arcs (in fact, the doubled cycle, which is
    strongly connected — it has lambda 2). B contains n arcs (the
    directed cycle once, strongly connected, lambda 1). Both strong, so
    valid SAD. Note: this leaves each color spanning, but R is
    1-arc-thicker than B in every bundle; alternatively split (1,2) on
    half the bundles and (2,1) on the other half for a more balanced
    SAD. We use the (2,1) construction since it's simpler.
    """
    arcs: list[tuple[int, int]] = []
    for i in range(n):
        for _ in range(3):
            arcs.append((i, (i + 1) % n))
    red_idx: list[int] = []
    blue_idx: list[int] = []
    # Within each block of 3 successive arcs (same (u, v)), put indices
    # 0, 1 in R and index 2 in B.
    for blk in range(n):
        base = 3 * blk
        red_idx.append(base + 0)
        red_idx.append(base + 1)
        blue_idx.append(base + 2)
    return SadInnerPart(
        name=f"C{n}_tripled",
        n=n,
        arcs=tuple(arcs),
        lambda_arc=3,
        red_idx=tuple(red_idx),
        blue_idx=tuple(blue_idx),
        family="cycle_tripled",
    )


# ----------------------------------------------------------------------------
# Self-checks
# ----------------------------------------------------------------------------


def _verify_part_lambda(part: SadInnerPart) -> tuple[int, bool]:
    """Returns (lambda_arc, strong) computed via Digraph.arc_connectivity."""
    D = part.build()
    return D.arc_connectivity(), D.is_strongly_connected()


def _verify_sad_witness(part: SadInnerPart) -> bool:
    """Re-validate the embedded SAD witness, if any."""
    red, blue = part.sad_witness()
    if not red or not blue:
        return False
    if len(red) + len(blue) != len(part.arcs):
        return False
    D = part.build()
    R = Digraph.from_arcs(range(part.n), red)
    B = Digraph.from_arcs(range(part.n), blue)
    return R.is_strongly_connected() and B.is_strongly_connected()


def _solve_sad_for_paley(part: SadInnerPart) -> SadInnerPart:
    """For Paley tournaments we don't have a closed-form SAD; call the
    SAT verifier once and embed the witness."""
    from verifier_sat import verify_sat

    D = part.build()
    res = verify_sat(D, time_limit_s=30.0)
    if res["status"] != "SAT":
        raise AssertionError(
            f"{part.name}: SAT verifier did not return SAT ({res['status']})"
        )
    red_arcs, blue_arcs = res["witness"]
    # Witness uses (u, v, k); strip the parallel-arc key (Paley is simple).
    red_pairs = [(u, v) for (u, v, _k) in red_arcs]
    blue_pairs = [(u, v) for (u, v, _k) in blue_arcs]
    # Build index lists into part.arcs.
    arcs = list(part.arcs)
    # Each arc appears at most once in Paley (simple), so a dict suffices.
    arc_to_idx: dict[tuple[int, int], int] = {a: i for i, a in enumerate(arcs)}
    red_idx = sorted(arc_to_idx[a] for a in red_pairs)
    blue_idx = sorted(arc_to_idx[a] for a in blue_pairs)
    return SadInnerPart(
        name=part.name,
        n=part.n,
        arcs=part.arcs,
        lambda_arc=part.lambda_arc,
        red_idx=tuple(red_idx),
        blue_idx=tuple(blue_idx),
        family=part.family,
    )


def build_library() -> list[SadInnerPart]:
    """Build the inner-part library; raises AssertionError on any failure.

    Returns a list of `SadInnerPart` instances all of which:
      * have lambda_arc >= 3 (verified);
      * have a valid SAD witness (verified by independent re-check).
    """
    parts: list[SadInnerPart] = []

    # K_n^* for n in {4, 5, 6}: K_3^* has lambda = 2 (each vertex's
    # out-degree is 2), so it falls below the 3-arc-strong floor and is
    # excluded from the library. We keep the family entry for K_3 for
    # completeness in the docstring but do not use it in the sweep.
    for nval in (4, 5, 6):
        p = make_K_star(nval)
        parts.append(p)

    # Paley tournaments (witnesses filled by SAT)
    for pval in (7, 11):
        p = make_Paley(pval)
        p = _solve_sad_for_paley(p)
        parts.append(p)

    # Composition C_4[Kbar_3]
    parts.append(make_C4_Kbar3())

    # Composition C_3[Kbar_3, Kbar_3, Kbar_3]
    parts.append(make_C3_K3_K3_K3())

    # Tripled directed cycles
    for nval in (4, 5, 6):
        parts.append(make_Cn_tripled(nval))

    # Final verification pass.
    for p in parts:
        lam, strong = _verify_part_lambda(p)
        assert strong, f"{p.name}: not strongly connected!"
        assert lam == p.lambda_arc, (
            f"{p.name}: advertised lambda={p.lambda_arc}, computed={lam}"
        )
        assert lam >= 3, f"{p.name}: lambda={lam} < 3!"
        ok = _verify_sad_witness(p)
        assert ok, f"{p.name}: SAD witness invalid"

    return parts


# ----------------------------------------------------------------------------
# CLI: print library summary
# ----------------------------------------------------------------------------


if __name__ == "__main__":
    lib = build_library()
    print(f"SAD-inner-part library: {len(lib)} entries")
    print(f"{'name':16s}  {'n':>3s}  {'m':>4s}  {'lambda':>6s}  {'family':18s}")
    for p in lib:
        print(
            f"{p.name:16s}  {p.n:3d}  {len(p.arcs):4d}  {p.lambda_arc:6d}  {p.family:18s}"
        )
