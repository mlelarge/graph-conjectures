"""Vehicle 6: gluings of SAD-decomposable 3-arc-strong inner parts.

The setup for CL1 (`team/08_phase4_lifting_lemma_v1.md` §2):

  Given two 3-arc-strong digraphs T_1, T_2 each admitting a SAD, glue them
  along an interface S (|S| in {1, 2, 3, 4}) by vertex identification and
  add bridge arcs b^+ : T_1 -> T_2 and b^- : T_2 -> T_1.

  We require b^+ >= 2 and b^- >= 2 (CL1 hypothesis 2). The total bridge
  count b^+ + b^- ranges over 4..10. The merged digraph D has
  lambda(D) >= 3 by inheritance from each side (each side is already
  3-arc-strong on its own). We accept D iff lambda(D) == 3 *exactly*
  (Vehicle 6's target regime per the spec).

  Bridge tails on the T_1 side are non-interface vertices of T_1; bridge
  heads on the T_1 side (for b^- arcs) are also non-interface T_1
  vertices. Same on the T_2 side. (Bridges to/from the interface would
  be reducible to non-bridge arcs, and the lemma treats them as part of
  the interface; we exclude them here.)

  We *do not* try to be exhaustive: the generator yields a randomized
  stream of candidates, with the seed under user control, and the
  caller is expected to set a streamed-count cap.

The interface |S| = 1 case is allowed (and easy: there are no per-side
strong-connectivity obstructions inside the interface itself).
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Iterator

from digraph import Digraph
from generators.sad_inner_parts import SadInnerPart


# ----------------------------------------------------------------------------
# Glued instance dataclass
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class SadGluedInstance:
    """A Vehicle 6 glued digraph candidate."""

    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    part1_name: str
    part2_name: str
    S1: tuple[int, ...]  # interface vertices in T_1's labelling
    S2: tuple[int, ...]  # interface vertices in T_2's labelling
    phi: tuple[tuple[int, int], ...]  # bijection (s1, s2)
    bridges_12: tuple[tuple[int, int], ...]  # T_1 -> T_2 bridges (post-relabel)
    bridges_21: tuple[tuple[int, int], ...]  # T_2 -> T_1 bridges (post-relabel)
    # Provenance — let downstream code recover the partition pieces.
    n_non1: int
    s: int
    # Re-labelling tables so callers can map the SAD witnesses on each
    # part back to the merged vertex labels.
    relabel1: tuple[tuple[int, int], ...]  # list of (T1_label, merged_label)
    relabel2: tuple[tuple[int, int], ...]  # list of (T2_label, merged_label)

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# Gluing primitive (variable interface size)
# ----------------------------------------------------------------------------


def _glue_along_interface(
    T1: SadInnerPart,
    T2: SadInnerPart,
    S1: tuple[int, ...],
    S2: tuple[int, ...],
    phi: tuple[tuple[int, int], ...],
) -> tuple[int, list[tuple[int, int]], dict[int, int], dict[int, int]]:
    """Merge T_1 and T_2 along the interface S_1 -- phi --> S_2. The
    merged labelling places side-1 non-interface vertices in
    [0, T1.n - |S|), the interface in [T1.n - |S|, T1.n), and side-2
    non-interface vertices in [T1.n, T1.n + T2.n - |S|). Shared interface
    arcs that appear in both T_1[S_1] and T_2[S_2] (mapped by phi) are
    intentionally kept as parallel arcs — we do *not* merge them — so
    that the merged digraph is the union of A(T_1) and A(T_2) as
    multisets after relabelling.
    """
    s = len(S1)
    assert len(S2) == s and len(phi) == s

    V1_non = sorted(v for v in range(T1.n) if v not in S1)
    V2_non = sorted(v for v in range(T2.n) if v not in S2)

    relabel1: dict[int, int] = {}
    relabel2: dict[int, int] = {}

    for i, v in enumerate(V1_non):
        relabel1[v] = i
    n_non1 = len(V1_non)
    for i, sv in enumerate(S1):
        relabel1[sv] = n_non1 + i

    s2_to_s1 = {b: a for a, b in phi}
    for s2 in S2:
        s1_label = s2_to_s1[s2]
        relabel2[s2] = relabel1[s1_label]
    for i, v in enumerate(V2_non):
        relabel2[v] = n_non1 + s + i

    n = n_non1 + s + len(V2_non)

    arcs: list[tuple[int, int]] = []
    for u, v in T1.arcs:
        arcs.append((relabel1[u], relabel1[v]))
    for u, v in T2.arcs:
        arcs.append((relabel2[u], relabel2[v]))

    return n, arcs, relabel1, relabel2


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------


@dataclass
class SadGenConfig:
    """Configuration of the Vehicle 6 sweep."""

    # Interface sizes to enumerate
    interface_sizes: tuple[int, ...] = (1, 2, 3, 4)
    # Total number of (b+, b-) bridge-count pairs per interface; we sample
    # uniformly from this set.
    bridge_count_pairs: tuple[tuple[int, int], ...] = (
        (2, 2), (2, 3), (3, 2), (3, 3),
        (2, 4), (4, 2), (3, 4), (4, 3),
        (4, 4), (2, 5), (5, 2),
    )
    # Maximum number of interfaces (S1, S2, phi) per ordered template pair
    # to try. (Combinatorially large; we randomly sample.)
    interfaces_per_pair: int = 30
    # For each (interface, b+, b-) combination, attempt this many random
    # bridge assignments.
    bridges_per_setup: int = 4
    # Random seed for the generator
    seed: int = 20260516


# ----------------------------------------------------------------------------
# Bridge enumeration
# ----------------------------------------------------------------------------


def _random_bridge_set(
    rng: random.Random,
    tails: list[int],
    heads: list[int],
    count: int,
    allow_parallel: bool = False,
) -> list[tuple[int, int]] | None:
    """Pick `count` arcs with tails in `tails`, heads in `heads`. Returns
    None if no valid set is possible (e.g., heads or tails empty)."""
    if not tails or not heads:
        return None
    bridges: list[tuple[int, int]] = []
    used: set[tuple[int, int]] = set()
    attempts = 0
    while len(bridges) < count and attempts < 1000:
        attempts += 1
        u = rng.choice(tails)
        v = rng.choice(heads)
        if not allow_parallel and (u, v) in used:
            continue
        bridges.append((u, v))
        used.add((u, v))
    if len(bridges) < count:
        return None
    return bridges


# ----------------------------------------------------------------------------
# Interface enumeration
# ----------------------------------------------------------------------------


def _random_interfaces(
    rng: random.Random,
    T1: SadInnerPart,
    T2: SadInnerPart,
    s: int,
    count: int,
) -> Iterator[tuple[tuple[int, ...], tuple[int, ...], tuple[tuple[int, int], ...]]]:
    """Yield up to `count` random (S1, S2, phi) triples with |S| = s."""
    if s > T1.n or s > T2.n:
        return
    V1 = list(range(T1.n))
    V2 = list(range(T2.n))
    emitted = 0
    while emitted < count:
        S1 = tuple(sorted(rng.sample(V1, s)))
        S2 = tuple(sorted(rng.sample(V2, s)))
        perm = list(S2)
        rng.shuffle(perm)
        phi = tuple(zip(S1, perm))
        yield S1, S2, phi
        emitted += 1


# ----------------------------------------------------------------------------
# Main generator
# ----------------------------------------------------------------------------


def generate_sad_gluings(
    parts: list[SadInnerPart],
    config: SadGenConfig,
    ordered_pairs: bool = True,
) -> Iterator[SadGluedInstance]:
    """Stream SadGluedInstance candidates."""
    rng = random.Random(config.seed)
    if ordered_pairs:
        pair_iter: list[tuple[SadInnerPart, SadInnerPart]] = list(
            itertools.product(parts, parts)
        )
    else:
        pair_iter = [
            (a, b)
            for i, a in enumerate(parts)
            for j, b in enumerate(parts)
            if i <= j
        ]
    rng.shuffle(pair_iter)

    # Map bridge_count_pairs by sum so we can vary "total bridges" smoothly.
    bcp_by_sum: dict[int, list[tuple[int, int]]] = {}
    for bp, bm in config.bridge_count_pairs:
        bcp_by_sum.setdefault(bp + bm, []).append((bp, bm))

    for T1, T2 in pair_iter:
        for s in config.interface_sizes:
            if s > T1.n or s > T2.n:
                continue
            # Interface size 1 with a part of size 1 makes no sense — skip
            # any case where the non-interface side is empty.
            if T1.n - s < 1 or T2.n - s < 1:
                continue

            for S1, S2, phi in _random_interfaces(
                rng, T1, T2, s, config.interfaces_per_pair
            ):
                n_glue, base_arcs, relabel1, relabel2 = _glue_along_interface(
                    T1, T2, S1, S2, phi
                )

                # Tail/head pools for bridges: non-interface vertices only.
                non1 = [relabel1[v] for v in range(T1.n) if v not in S1]
                non2 = [relabel2[v] for v in range(T2.n) if v not in S2]

                # If either side has no non-interface vertices, no bridges
                # are possible — skip.
                if not non1 or not non2:
                    continue

                for bp, bm in config.bridge_count_pairs:
                    for _ in range(config.bridges_per_setup):
                        b12 = _random_bridge_set(rng, non1, non2, bp, allow_parallel=False)
                        if b12 is None:
                            continue
                        b21 = _random_bridge_set(rng, non2, non1, bm, allow_parallel=False)
                        if b21 is None:
                            continue
                        arcs = (
                            tuple(base_arcs)
                            + tuple(b12)
                            + tuple(b21)
                        )
                        h = abs(hash(arcs)) % (1 << 32)
                        name = (
                            f"glueSAD[{T1.name}+{T2.name}]"
                            f"_s{s}_b{bp}{bm}_h{h:08x}"
                        )
                        yield SadGluedInstance(
                            name=name,
                            n=n_glue,
                            arcs=arcs,
                            part1_name=T1.name,
                            part2_name=T2.name,
                            S1=tuple(S1),
                            S2=tuple(S2),
                            phi=tuple(phi),
                            bridges_12=tuple(b12),
                            bridges_21=tuple(b21),
                            n_non1=len(non1),
                            s=s,
                            relabel1=tuple(relabel1.items()),
                            relabel2=tuple(relabel2.items()),
                        )


# ----------------------------------------------------------------------------
# Convenience: lambda exactness check
# ----------------------------------------------------------------------------


def passes_arc_strong_exactly_3(D: Digraph) -> bool:
    """True iff arc-connectivity is exactly 3."""
    if not D.is_strongly_connected():
        return False
    return D.arc_connectivity() == 3


def passes_arc_strong_at_least_3(D: Digraph) -> bool:
    """True iff arc-connectivity is at least 3."""
    if not D.is_strongly_connected():
        return False
    return D.arc_connectivity() >= 3


def vertex_degree_feasible(arcs: list[tuple[int, int]], n: int) -> bool:
    """Necessary condition: every vertex out-degree and in-degree >= 3."""
    outd = [0] * n
    ind = [0] * n
    for u, v in arcs:
        outd[u] += 1
        ind[v] += 1
    return all(d >= 3 for d in outd) and all(d >= 3 for d in ind)


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------


if __name__ == "__main__":
    from generators.sad_inner_parts import build_library

    parts = build_library()
    print(f"library: {len(parts)} parts")

    cfg = SadGenConfig(
        interface_sizes=(2, 3),
        bridge_count_pairs=((2, 2), (3, 2), (3, 3)),
        interfaces_per_pair=2,
        bridges_per_setup=1,
        seed=0,
    )

    streamed = 0
    kappa3 = 0
    higher = 0
    for inst in generate_sad_gluings(parts[:3], cfg, ordered_pairs=False):
        streamed += 1
        D = inst.build()
        if not vertex_degree_feasible(list(inst.arcs), inst.n):
            continue
        if passes_arc_strong_exactly_3(D):
            kappa3 += 1
        elif D.arc_connectivity() > 3:
            higher += 1
        if streamed >= 80:
            break
    print(f"streamed={streamed} kappa=3 exactly: {kappa3}, kappa>3: {higher}")
