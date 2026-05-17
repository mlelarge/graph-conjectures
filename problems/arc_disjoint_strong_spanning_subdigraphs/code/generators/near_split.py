"""(1,0)-near-split digraph generator for the Route-B sweep (amended pivot).

Definition. A digraph D is *(1,0)-near-split* if V(D) = V_1 \\dot\\cup V_2
with
  - D[V_2] semicomplete (every unordered pair {u, v} in V_2 has at least
    one of (u, v), (v, u) as an arc);
  - arcs between V_1 and V_2 are unrestricted (any subset of the 2|V_1||V_2|
    possible bridge ordered pairs);
  - **exactly one** arc inside V_1 (one ordered pair (a, b) with a, b in V_1,
    a != b, has the arc; all other within-V_1 ordered pairs have no arc).

The (0, 0)-case (no V_1-internal arc, V_1 independent) is the strict-split
class handled by Bang-Jensen–Wang 2025 and Ai et al. 2024. The (1, 0) class
is the smallest perturbation: an isolated "noise" arc inside V_1 plus the
usual split structure.

Three constructions, mirroring `generators/ols.py`:

  A — Exhaustive enumeration. For each small (|V_1|, |V_2|), enumerate
      canonical semicomplete D[V_2] (via pynauty); for each, enumerate
      every V_1-internal ordered pair; for each, enumerate or sample
      bridge subsets.

  B — Random sampling. For larger |V_2| (>= 5), random bridge subsets
      with rejection on the (1,0)-near-split predicate (which is
      satisfied by construction; the rejection is purely on
      lambda^arc gate).

  C — Reference exception list. The Ai et al. 2024 split (0,0)-near-split
      UNSAT instances, augmented with a single V_1-internal arc when
      |V_1| >= 2.

The (1, 0)-near-split predicate is verified by an *independent* function
`is_one_zero_near_split` applied AFTER construction. This satisfies the
hard rule: "the (1,0)-near-split property must be verified by an
independent predicate function, not just trusted from construction."
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Iterator

from digraph import Digraph
from generators.ols import is_semicomplete


# ----------------------------------------------------------------------------
# Independent (1,0)-near-split predicate
# ----------------------------------------------------------------------------


def is_one_zero_near_split(
    D: Digraph,
    V1: list[int],
    V2: list[int],
) -> tuple[bool, str]:
    """Independent check: D is (1,0)-near-split with the partition (V1, V2).

    Returns (ok, reason). On success ok=True and reason is empty. On
    failure ok=False and reason identifies the failed clause.
    """
    V = set(D.vertices())
    V1s, V2s = set(V1), set(V2)
    if V1s | V2s != V:
        return (False, f"V1 \\cup V2 != V (missing: {V - (V1s | V2s)})")
    if V1s & V2s:
        return (False, f"V1 \\cap V2 nonempty ({V1s & V2s})")
    arcset = set((int(u), int(v)) for u, v, _ in D.arcs())
    # No self-loops (consistent with our convention).
    for u, v in arcset:
        if u == v:
            return (False, f"self-loop {u} -> {u} present")
    # D[V_2] semicomplete.
    V2_sorted = sorted(V2s)
    for i in range(len(V2_sorted)):
        for j in range(i + 1, len(V2_sorted)):
            a, b = V2_sorted[i], V2_sorted[j]
            if (a, b) not in arcset and (b, a) not in arcset:
                return (False, f"V_2 not semicomplete: {a},{b} non-adjacent")
    # V_1-internal: count arcs.
    internal_count = 0
    for a in V1s:
        for b in V1s:
            if a != b and (a, b) in arcset:
                internal_count += 1
    if internal_count != 1:
        return (False, f"V_1-internal arc count = {internal_count} (need exactly 1)")
    return (True, "")


def is_strict_split(D: Digraph, V1: list[int], V2: list[int]) -> bool:
    """V_1 independent (no internal arcs), V_2 semicomplete.

    Used for the §3.b comparison: we want to compare (1,0)-near-split
    UNSAT against the strict-split (0,0) UNSAT family.
    """
    V = set(D.vertices())
    V1s, V2s = set(V1), set(V2)
    if V1s | V2s != V or (V1s & V2s):
        return False
    arcset = set((int(u), int(v)) for u, v, _ in D.arcs())
    for a in V1s:
        for b in V1s:
            if a != b and (a, b) in arcset:
                return False
    V2_sorted = sorted(V2s)
    for i in range(len(V2_sorted)):
        for j in range(i + 1, len(V2_sorted)):
            a, b = V2_sorted[i], V2_sorted[j]
            if (a, b) not in arcset and (b, a) not in arcset:
                return False
    return True


# ----------------------------------------------------------------------------
# NS instance dataclass
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class NSInstance:
    """A (1,0)-near-split digraph candidate with provenance."""

    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    V1: tuple[int, ...]
    V2: tuple[int, ...]
    internal_arc: tuple[int, int]
    construction: str  # "A_exhaustive", "B_random", "C_reference"

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# Semicomplete-on-V_2 enumerator (canonical-deduped)
# ----------------------------------------------------------------------------


def _enumerate_semicomplete_orientations(
    V2: list[int],
) -> Iterator[tuple[tuple[int, int], ...]]:
    """Yield every semicomplete arc-set on V_2.

    For each unordered pair {u, v} with u < v there are 3 choices: only
    u -> v, only v -> u, or both. We yield all 3^binom(|V_2|,2)
    possibilities (no canonical-dedup here — we let pynauty dedup at
    the driver level).
    """
    V = sorted(V2)
    pairs = [(V[i], V[j]) for i in range(len(V)) for j in range(i + 1, len(V))]
    # 0 = u -> v only, 1 = v -> u only, 2 = both
    for choices in itertools.product((0, 1, 2), repeat=len(pairs)):
        arcs: list[tuple[int, int]] = []
        for (u, v), c in zip(pairs, choices):
            if c == 0:
                arcs.append((u, v))
            elif c == 1:
                arcs.append((v, u))
            else:
                arcs.append((u, v))
                arcs.append((v, u))
        yield tuple(arcs)


# ----------------------------------------------------------------------------
# Bridge-subset enumeration / sampling
# ----------------------------------------------------------------------------


def _all_bridge_arcs(V1: list[int], V2: list[int]) -> list[tuple[int, int]]:
    """The 2 * |V_1| * |V_2| candidate bridge arcs (both directions)."""
    out: list[tuple[int, int]] = []
    for a in V1:
        for b in V2:
            out.append((a, b))
            out.append((b, a))
    return out


def _enumerate_bridge_subsets(
    bridges: list[tuple[int, int]],
    cap: int,
    rng: random.Random,
) -> Iterator[tuple[tuple[int, int], ...]]:
    """Yield subsets of `bridges` as tuples.

    If 2^len(bridges) <= cap, yields all subsets in deterministic order.
    Otherwise yields `cap` random subsets (sampled with bias toward
    moderate density: p in {0.3, 0.5, 0.7}).
    """
    nB = len(bridges)
    total = 1 << nB
    if total <= cap:
        for mask in range(total):
            subset = tuple(bridges[i] for i in range(nB) if (mask >> i) & 1)
            yield subset
        return
    densities = (0.3, 0.5, 0.7)
    for _ in range(cap):
        p = rng.choice(densities)
        subset = tuple(b for b in bridges if rng.random() < p)
        yield subset


# ----------------------------------------------------------------------------
# Construction A: exhaustive enumeration over small (|V_1|, |V_2|)
# ----------------------------------------------------------------------------


def enumerate_construction_A(
    v1_size: int,
    v2_size: int,
    seed: int = 20260516,
    cap_per_v2_orientation: int = 64,
    bridge_cap_per_pair: int = 32,
) -> Iterator[NSInstance]:
    """Exhaustive enumeration for given (|V_1|, |V_2|).

    Layout: V_1 = [0, v1_size), V_2 = [v1_size, v1_size + v2_size).

    For each semicomplete orientation of V_2 (up to a budget
    `cap_per_v2_orientation`, since 3^binom(v2_size,2) explodes), and
    each of the v1_size*(v1_size-1) ordered V_1-internal arcs, sample
    bridge subsets up to `bridge_cap_per_pair`.

    The result may contain isomorphic duplicates; the driver
    canonicalizes at log time.
    """
    rng = random.Random(seed + 100 * v1_size + v2_size)
    V1 = list(range(v1_size))
    V2 = list(range(v1_size, v1_size + v2_size))
    bridges = _all_bridge_arcs(V1, V2)

    # V_1-internal arc candidates: every ordered pair (a, b), a != b.
    internal_candidates = [
        (a, b) for a in V1 for b in V1 if a != b
    ]

    # Enumerate orientations of V_2.
    orientations = list(_enumerate_semicomplete_orientations(V2))
    rng.shuffle(orientations)
    orientations = orientations[:cap_per_v2_orientation]

    counter = 0
    for v2_arcs in orientations:
        for internal in internal_candidates:
            for bridge_subset in _enumerate_bridge_subsets(
                bridges, cap=bridge_cap_per_pair, rng=rng
            ):
                arcs = list(v2_arcs) + [internal] + list(bridge_subset)
                yield NSInstance(
                    name=(
                        f"A_NS[|V1|={v1_size},|V2|={v2_size},"
                        f"int=({internal[0]},{internal[1]}),k={counter}]"
                    ),
                    n=v1_size + v2_size,
                    arcs=tuple(arcs),
                    V1=tuple(V1),
                    V2=tuple(V2),
                    internal_arc=internal,
                    construction="A_exhaustive",
                )
                counter += 1


# ----------------------------------------------------------------------------
# Construction B: random sampling for larger (|V_1|, |V_2|)
# ----------------------------------------------------------------------------


def enumerate_construction_B(
    v1_size: int,
    v2_size: int,
    seed: int = 20260516,
    cap: int = 1000,
) -> Iterator[NSInstance]:
    """Random (1,0)-near-split instances for larger |V_2|.

    For each sample: pick V_2 orientation uniformly (each unordered pair
    independently one of {only fwd, only rev, both}, equal prob); pick a
    V_1-internal ordered pair uniformly; pick each bridge with random
    density.
    """
    rng = random.Random(seed + 7919 + 17 * v1_size + v2_size)
    V1 = list(range(v1_size))
    V2 = list(range(v1_size, v1_size + v2_size))
    bridges = _all_bridge_arcs(V1, V2)

    for k in range(cap):
        # V_2 orientation.
        v2_arcs: list[tuple[int, int]] = []
        for i in range(len(V2)):
            for j in range(i + 1, len(V2)):
                u, v = V2[i], V2[j]
                c = rng.choice((0, 1, 2))
                if c == 0:
                    v2_arcs.append((u, v))
                elif c == 1:
                    v2_arcs.append((v, u))
                else:
                    v2_arcs.append((u, v))
                    v2_arcs.append((v, u))

        # Internal V_1 arc.
        a = rng.choice(V1)
        b = rng.choice([x for x in V1 if x != a])
        internal = (a, b)

        # Bridge subset.
        p = rng.choice((0.35, 0.5, 0.65))
        bridge_subset = [br for br in bridges if rng.random() < p]
        arcs = v2_arcs + [internal] + bridge_subset
        yield NSInstance(
            name=f"B_NS[|V1|={v1_size},|V2|={v2_size},k={k}]",
            n=v1_size + v2_size,
            arcs=tuple(arcs),
            V1=tuple(V1),
            V2=tuple(V2),
            internal_arc=internal,
            construction="B_random",
        )


# ----------------------------------------------------------------------------
# Construction C: reference UNSAT (strict-split) extended with a V_1 arc
# ----------------------------------------------------------------------------


def reference_near_split_from_split(
    split_arcs: list[tuple[int, int]],
    V1: list[int],
    V2: list[int],
    internal: tuple[int, int],
) -> NSInstance:
    """Wrap an existing strict-split D + a V_1-internal arc into an
    NSInstance. The caller is responsible for providing valid V1/V2
    such that `split_arcs` is strictly split on (V1, V2).
    """
    arcs = list(split_arcs) + [internal]
    n = max(max(u, v) for u, v in arcs) + 1
    return NSInstance(
        name=f"C_ref[V1={V1},int=({internal[0]},{internal[1]})]",
        n=n,
        arcs=tuple(arcs),
        V1=tuple(V1),
        V2=tuple(V2),
        internal_arc=internal,
        construction="C_reference",
    )


def enumerate_construction_C() -> Iterator[NSInstance]:
    """Yield (1,0)-near-split extensions of the Ai et al. 2024 UNSAT
    strict-split benchmarks, by adding every possible V_1-internal arc
    when |V_1| >= 2.

    Note: AiEtAl_L211_min has |V_1| = 1 (vertex 4 only), so no extension
    is possible — we skip it.
    """
    # L312_min: V_1 = {u=4, v=5}, V_2 = {a=0, b=1, c=2, w=3}.
    L312_arcs = [
        (0, 1), (1, 2), (2, 0),
        (1, 4), (1, 5),
        (2, 5),
        (0, 4),
        (4, 0), (4, 3),
        (5, 1), (5, 3),
        (3, 0), (3, 1), (3, 2),
    ]
    L312_V1 = [4, 5]
    L312_V2 = [0, 1, 2, 3]
    for (a, b) in ((4, 5), (5, 4)):
        yield reference_near_split_from_split(L312_arcs, L312_V1, L312_V2, (a, b))

    # iv_star_iv: V_1 = {a=4, b=5}, V_2 = {v_1=0, v_2=1, v_3=2, v_4=3}.
    ivsiv_arcs = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (0, 2),
        (1, 3),
        (3, 4),
        (4, 1),
        (1, 4),
        (4, 2),
        (5, 0),
        (2, 5),
        (5, 2),
        (1, 5),
    ]
    ivsiv_V1 = [4, 5]
    ivsiv_V2 = [0, 1, 2, 3]
    for (a, b) in ((4, 5), (5, 4)):
        yield reference_near_split_from_split(ivsiv_arcs, ivsiv_V1, ivsiv_V2, (a, b))


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------


def _selftest() -> None:
    print("(1,0)-near-split generator self-test")
    # 1. Predicate sanity.
    # A trivial valid (1,0)-near-split: V_1 = {0, 1} with arc 0->1;
    # V_2 = {2, 3} with both 2-3 arcs; bridges 0->2, 3->0.
    arcs = [(0, 1), (2, 3), (3, 2), (0, 2), (3, 0)]
    D = Digraph.from_arcs(range(4), arcs)
    ok, why = is_one_zero_near_split(D, [0, 1], [2, 3])
    assert ok, f"expected (1,0)-NS to hold; got: {why}"
    # Two internal arcs -> fail.
    D2 = Digraph.from_arcs(range(4), arcs + [(1, 0)])
    ok2, why2 = is_one_zero_near_split(D2, [0, 1], [2, 3])
    assert not ok2 and "internal arc count" in why2
    # Zero internal arcs -> fail (it's strictly split, not (1,0)-NS).
    arcs3 = [(2, 3), (3, 2), (0, 2), (3, 0)]
    D3 = Digraph.from_arcs(range(4), arcs3)
    ok3, why3 = is_one_zero_near_split(D3, [0, 1], [2, 3])
    assert not ok3
    # V_2 not semicomplete -> fail. Use V_2 = {2,3,4} with only the
    # 2-3 pair adjacent: pair {2,4} and {3,4} non-adjacent.
    arcs4 = [(0, 1), (2, 3), (0, 2), (4, 0)]
    D4 = Digraph.from_arcs(range(5), arcs4)
    ok4, why4 = is_one_zero_near_split(D4, [0, 1], [2, 3, 4])
    assert not ok4 and "not semicomplete" in why4, f"got: {ok4}, why={why4}"
    print("  predicate tests: ok")

    # 2. Construction A: a few instances.
    n_emit = 0
    for inst in enumerate_construction_A(
        v1_size=2, v2_size=3,
        cap_per_v2_orientation=3,
        bridge_cap_per_pair=4,
    ):
        D = inst.build()
        ok, why = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
        assert ok, f"Construction A generated non-(1,0)-NS: {inst.name}: {why}"
        n_emit += 1
        if n_emit >= 5:
            break
    print(f"  Construction A: yielded {n_emit} valid (1,0)-NS instances")

    # 3. Construction B random.
    n_emit = 0
    for inst in enumerate_construction_B(v1_size=3, v2_size=5, cap=10):
        D = inst.build()
        ok, why = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
        assert ok, f"Construction B generated non-(1,0)-NS: {inst.name}: {why}"
        n_emit += 1
    print(f"  Construction B: {n_emit} valid (1,0)-NS instances")

    # 4. Construction C reference list.
    for inst in enumerate_construction_C():
        D = inst.build()
        ok, why = is_one_zero_near_split(D, list(inst.V1), list(inst.V2))
        assert ok, f"Construction C invalid: {inst.name}: {why}"
        print(
            f"  Construction C: {inst.name} n={inst.n} m={len(inst.arcs)} "
            f"strong={D.is_strongly_connected()} "
            f"lambda={D.arc_connectivity()}"
        )

    print("[OK] (1,0)-near-split self-test passed.")


if __name__ == "__main__":
    _selftest()
