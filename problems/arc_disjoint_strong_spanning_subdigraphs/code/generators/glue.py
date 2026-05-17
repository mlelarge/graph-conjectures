"""Vehicle 3 generator: gluings of 2-arc-strong obstruction templates.

Construction:

Let T1 = (V1, A1), T2 = (V2, A2) be two 2-arc-strong templates from the
benchmark list. Pick 3-element subsets S1 ⊂ V1, S2 ⊂ V2 and a bijection
phi: S1 → S2 ("the interface"). The glued digraph G has vertex set

    V(G) = (V1 \ S1) ∪ S1 ∪ rel(V2 \ S2)

where rel relabels V2 \ S2 with fresh integer labels and S1 plays the role
of the merged interface. Arcs of T2 incident to S2 are remapped via phi^{-1}.

So far, every vertex in V(G) has the same in/out-degree it had in its
original template; the digraph is the *disjoint union* of T1 and T2
along the merged S1 = phi(S2). Because each Ti is 2-arc-strong, every cut
of the glued digraph has size at least 2 *as long as it does not separate
the two sides through the interface*.

We add three bridge arcs crossing the interface — each bridge arc is
incident to at least one non-interface vertex on each side — to lift the
global arc-connectivity from 2 to (exactly) 3.

Bridge arc structure (default): each of the three bridges has tail in
either (V1 \ S1) or rel(V2 \ S2), and head in the other side. We enumerate
the 2^3 = 8 direction patterns (each bridge can be 1→2 or 2→1) and for
each, sample bridge endpoints from a small budget of representative
non-interface vertices to keep the candidate count tractable.

Each candidate is then verified for arc-connectivity ≥ 3 (we reject any
candidate with kappa' != 3 — we want *exactly* 3 to avoid spurious cases).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Iterator

from digraph import Digraph
from benchmarks import Benchmark


# ----------------------------------------------------------------------------
# Glued-instance representation
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class GluedInstance:
    """A glued digraph candidate with the provenance of every arc.

    Attributes
    ----------
    name : human-readable name
    n : number of vertices
    arcs : list of (u, v) arc pairs (allowing parallel arcs)
    template1, template2 : names of the two source templates
    S1 : interface vertices in T1 (the labels in template1)
    S2 : interface vertices in T2 (the labels in template2)
    phi : tuple (s1_i, s2_i) pairs giving the bijection S1 -> S2
    bridge_arcs : the three bridge arcs in the (post-relabeling) labels
    bridge_pattern : tuple of "12" or "21" describing each bridge direction
    """

    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    template1: str
    template2: str
    S1: tuple[int, ...]
    S2: tuple[int, ...]
    phi: tuple[tuple[int, int], ...]
    bridge_arcs: tuple[tuple[int, int], ...]
    bridge_pattern: tuple[str, ...]

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# Core gluing primitive
# ----------------------------------------------------------------------------


def _glue_along_interface(
    T1: Benchmark,
    T2: Benchmark,
    S1: tuple[int, ...],
    S2: tuple[int, ...],
    phi: tuple[tuple[int, int], ...],
) -> tuple[int, list[tuple[int, int]], dict[int, int], dict[int, int]]:
    """Return (n, arcs, relabel1, relabel2) for the glued (no-bridges) digraph.

    Convention:
     - Side-1 non-interface vertices keep labels 0..(n1 - 3 - 1), in
       sorted order of their original T1 labels. Actually we relabel
       freshly to integers: side-1 non-interface gets labels 0..|V1\\S1|-1,
       interface gets labels |V1\\S1|..|V1\\S1|+2, side-2 non-interface
       gets labels |V1\\S1|+3..(total - 1).
     - relabel1[v] = new label of T1-vertex v.
     - relabel2[v] = new label of T2-vertex v.

    The bijection phi maps S1 labels to S2 labels; under it, S1's
    relabeled values equal S2's relabeled values.
    """
    V1 = list(range(T1.n))
    V2 = list(range(T2.n))
    V1_non = [v for v in V1 if v not in S1]
    V2_non = [v for v in V2 if v not in S2]

    n_non1 = len(V1_non)
    n_non2 = len(V2_non)

    relabel1: dict[int, int] = {}
    relabel2: dict[int, int] = {}

    # Side-1 non-interface vertices: 0..n_non1-1
    for i, v in enumerate(sorted(V1_non)):
        relabel1[v] = i
    # Interface (shared): n_non1..n_non1+2 in the order given by S1
    for i, s in enumerate(S1):
        relabel1[s] = n_non1 + i
    # Apply phi to put S2 onto the same labels
    s1_to_s2 = dict(phi)
    s2_to_s1 = {b: a for a, b in phi}
    for s2 in S2:
        s1 = s2_to_s1[s2]
        relabel2[s2] = relabel1[s1]
    # Side-2 non-interface vertices: n_non1+3..n_non1+3+n_non2-1
    for i, v in enumerate(sorted(V2_non)):
        relabel2[v] = n_non1 + 3 + i

    n = n_non1 + 3 + n_non2

    arcs: list[tuple[int, int]] = []
    for u, v in T1.arcs:
        arcs.append((relabel1[u], relabel1[v]))
    for u, v in T2.arcs:
        arcs.append((relabel2[u], relabel2[v]))

    return n, arcs, relabel1, relabel2


# ----------------------------------------------------------------------------
# Candidate enumeration
# ----------------------------------------------------------------------------


@dataclass
class GenConfig:
    """Configuration of the gluing sweep."""

    # Cap on interfaces tested per ordered pair of templates. Each interface
    # is (S1, S2, phi) so the combinatorial count blows up; cap with this.
    max_interfaces_per_pair: int = 60
    # Cap on bridge sets tried per interface (per number-of-bridges value).
    # Bridge sets are picked heuristically from a small budget of
    # representative endpoint pairs.
    max_bridges_per_interface: int = 24
    # Number of bridge arcs to place crossing the interface. The Phase-3
    # spec calls for 3 ("Add three bridge arcs...") but arithmetically
    # 3 bridges cannot lift the gluing of two 2-regular templates to
    # lambda = 3, so we expose this for the extended sweep. Default = 3.
    num_bridges: int = 3
    # Whether to allow same-template gluings (T1 = T2). Default yes.
    allow_self_glue: bool = True
    # Whether to consider only ordered or unordered template pairs.
    ordered_pairs: bool = True
    # Reject candidates with arc-connectivity != 3 (we want exactly 3).
    require_arc_conn_exactly_3: bool = True
    # Random seed for any random sampling.
    seed: int = 20260516


def enumerate_interfaces(
    T1: Benchmark, T2: Benchmark, max_count: int
) -> Iterator[tuple[tuple[int, ...], tuple[int, ...], tuple[tuple[int, int], ...]]]:
    """Yield (S1, S2, phi) triples in a canonical, deterministic order.

    S1 ranges over 3-subsets of V(T1); S2 over 3-subsets of V(T2); phi over
    all 6 bijections S1 → S2.
    """
    count = 0
    for S1 in itertools.combinations(range(T1.n), 3):
        for S2 in itertools.combinations(range(T2.n), 3):
            for perm in itertools.permutations(S2):
                phi = tuple(zip(S1, perm))
                yield S1, S2, phi
                count += 1
                if count >= max_count:
                    return


def _candidate_bridges(
    n: int,
    non1_labels: list[int],
    non2_labels: list[int],
    pattern: tuple[str, ...],
    max_per_pattern: int,
) -> Iterator[tuple[tuple[int, int], ...]]:
    """Enumerate tuples of bridge arcs respecting `pattern`.

    Each entry of `pattern` is "12" (arc goes side1 -> side2) or "21".
    For pattern "12", a bridge is (u, v) with u in non1_labels, v in
    non2_labels.

    To keep the count tractable and avoid wasting time on certainly-bad
    candidates (parallel bridges between the same pair), we require
    distinct (tail, head) pairs only when at least len(non1)+len(non2)
    distinct endpoints are available. When a side has < 2 non-interface
    vertices we fall back to permitting parallel arcs in that pattern slot.
    """
    if not non1_labels or not non2_labels:
        return
    count = 0
    sides = []
    for p in pattern:
        if p == "12":
            sides.append([(u, v) for u in non1_labels for v in non2_labels])
        else:
            sides.append([(u, v) for u in non2_labels for v in non1_labels])
    # If either side has only one non-interface vertex, parallel bridges
    # become unavoidable and we permit them.
    permit_parallel = min(len(non1_labels), len(non2_labels)) <= 1

    for combo in itertools.product(*sides):
        if not permit_parallel and len(set(combo)) < len(combo):
            continue
        yield combo
        count += 1
        if count >= max_per_pattern:
            return


def generate_gluings(
    templates: list[Benchmark], config: GenConfig
) -> Iterator[GluedInstance]:
    """Stream GluedInstance candidates.

    Order: outer loop over (T1, T2) template pairs, then interfaces, then
    bridge direction patterns, then bridge arc triples.
    """
    pair_iter: Iterator[tuple[Benchmark, Benchmark]]
    if config.ordered_pairs:
        pair_iter = itertools.product(templates, templates)
    else:
        pair_iter = (
            (a, b)
            for i, a in enumerate(templates)
            for j, b in enumerate(templates)
            if i <= j
        )

    for T1, T2 in pair_iter:
        if T1.name == T2.name and not config.allow_self_glue:
            continue

        for S1, S2, phi in enumerate_interfaces(T1, T2, config.max_interfaces_per_pair):
            n, base_arcs, relabel1, relabel2 = _glue_along_interface(T1, T2, S1, S2, phi)
            non1 = sorted([relabel1[v] for v in range(T1.n) if v not in S1])
            non2 = sorted([relabel2[v] for v in range(T2.n) if v not in S2])
            k = config.num_bridges

            for pattern in itertools.product(["12", "21"], repeat=k):
                bridges_yielded = 0
                for bridges in _candidate_bridges(
                    n, non1, non2, pattern, config.max_bridges_per_interface
                ):
                    bridges_yielded += 1
                    if bridges_yielded > config.max_bridges_per_interface:
                        break
                    arcs = tuple(base_arcs) + bridges
                    name = (
                        f"glue[{T1.name}+{T2.name}]"
                        f"_S1{''.join(str(s) for s in S1)}"
                        f"_S2{''.join(str(s) for s in S2)}"
                        f"_phi{''.join(str(b) for _, b in phi)}"
                        f"_p{''.join(pattern)}"
                        f"_b{bridges_yielded}"
                    )
                    yield GluedInstance(
                        name=name,
                        n=n,
                        arcs=arcs,
                        template1=T1.name,
                        template2=T2.name,
                        S1=S1,
                        S2=S2,
                        phi=phi,
                        bridge_arcs=bridges,
                        bridge_pattern=pattern,
                    )


# ----------------------------------------------------------------------------
# Convenience
# ----------------------------------------------------------------------------


def passes_arc_strong_3(D: Digraph, exact: bool = True) -> bool:
    """True iff D is 3-arc-strong; iff arc-connectivity is exactly 3 when
    `exact` is set."""
    if not D.is_strongly_connected():
        return False
    k = D.arc_connectivity()
    if exact:
        return k == 3
    return k >= 3
