"""Vehicle 3 (v2): deficit-aware gluings of 2-arc-strong obstruction templates.

This is a complete redesign of the v1 generator `glue.py`. The v1 generator
brute-force-enumerated (interface, bridge-pattern, bridge-arcs) triples and
relied on a post-hoc kappa' = 3 filter, which crushed templates whose
interior degree-2 vertices were never touched by bridges (5 of 9 UNSAT
templates produced zero verified 3-arc-strong gluings).

v2 inverts the order:

  1. For each ordered pair (T_1, T_2) and interface size |S| in {3, 4, 5},
     enumerate interfaces (S_1, S_2, phi).
  2. Compute the per-vertex out-/in-deficit at every non-interface vertex
     of T_1 and T_2 (each template is 2-arc-strong, so deficits are 0 or 1).
  3. Compute the minimum total number `b12` of bridges T_1 -> T_2 needed
     and `b21` of bridges T_2 -> T_1 needed so that, after gluing,
     every non-interface vertex of T_i reaches out-degree >= 3 and
     in-degree >= 3. Interface vertices over-shoot easily and are skipped.
  4. Enumerate bridge assignments that *exactly* satisfy the per-vertex
     deficit demands. This is a balanced bipartite multi-assignment
     problem; we backtrack with strong pruning.
  5. Verify lambda^{arc} = 3 (a vertex-degree gate is necessary but not
     sufficient).

The per-pair search is capped at MAX_VERIFIED_PER_PAIR to ensure
diversity rather than exhaustion.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Iterator

from digraph import Digraph
from benchmarks import Benchmark


# ----------------------------------------------------------------------------
# Glued-instance dataclass (mirrors v1 but with deficit metadata)
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class DeficitGluedInstance:
    """A deficit-aware glued digraph candidate."""

    name: str
    n: int
    arcs: tuple[tuple[int, int], ...]
    template1: str
    template2: str
    S1: tuple[int, ...]
    S2: tuple[int, ...]
    phi: tuple[tuple[int, int], ...]
    bridges_12: tuple[tuple[int, int], ...]  # T1 -> T2 bridges (post-relabel)
    bridges_21: tuple[tuple[int, int], ...]  # T2 -> T1 bridges (post-relabel)
    deficit_summary: tuple[int, int, int, int]  # (out1, in1, out2, in2) non-interface totals

    def build(self) -> Digraph:
        return Digraph.from_arcs(range(self.n), list(self.arcs))


# ----------------------------------------------------------------------------
# Deficit accounting
# ----------------------------------------------------------------------------


def _template_degrees(T: Benchmark) -> tuple[dict[int, int], dict[int, int]]:
    outd = {v: 0 for v in range(T.n)}
    ind = {v: 0 for v in range(T.n)}
    for u, v in T.arcs:
        outd[u] += 1
        ind[v] += 1
    return outd, ind


def _per_vertex_deficits(
    T: Benchmark,
) -> tuple[dict[int, int], dict[int, int]]:
    """Return (out_deficit, in_deficit) dicts per vertex of T,
    where deficit_x(v) = max(0, 3 - d_x(v)).

    For our 2-arc-strong templates these are all 0 or 1.
    """
    outd, ind = _template_degrees(T)
    out_def = {v: max(0, 3 - outd[v]) for v in range(T.n)}
    in_def = {v: max(0, 3 - ind[v]) for v in range(T.n)}
    return out_def, in_def


# ----------------------------------------------------------------------------
# Gluing primitive (variable interface size)
# ----------------------------------------------------------------------------


def _glue_along_interface(
    T1: Benchmark,
    T2: Benchmark,
    S1: tuple[int, ...],
    S2: tuple[int, ...],
    phi: tuple[tuple[int, int], ...],
) -> tuple[int, list[tuple[int, int]], dict[int, int], dict[int, int]]:
    """Same shape as v1's _glue_along_interface, but |S| is no longer fixed."""
    s = len(S1)
    assert len(S2) == s and len(phi) == s

    V1 = list(range(T1.n))
    V2 = list(range(T2.n))
    V1_non = [v for v in V1 if v not in S1]
    V2_non = [v for v in V2 if v not in S2]

    n_non1 = len(V1_non)
    n_non2 = len(V2_non)

    relabel1: dict[int, int] = {}
    relabel2: dict[int, int] = {}

    # Side-1 non-interface vertices: 0 .. n_non1-1
    for i, v in enumerate(sorted(V1_non)):
        relabel1[v] = i
    # Interface (shared): n_non1 .. n_non1 + s - 1, in the order given by S1
    for i, sv in enumerate(S1):
        relabel1[sv] = n_non1 + i
    # Apply phi to put S2 onto the same labels
    s2_to_s1 = {b: a for a, b in phi}
    for s2 in S2:
        s1 = s2_to_s1[s2]
        relabel2[s2] = relabel1[s1]
    # Side-2 non-interface vertices: n_non1 + s .. n_non1 + s + n_non2 - 1
    for i, v in enumerate(sorted(V2_non)):
        relabel2[v] = n_non1 + s + i

    n = n_non1 + s + n_non2

    arcs: list[tuple[int, int]] = []
    for u, v in T1.arcs:
        arcs.append((relabel1[u], relabel1[v]))
    for u, v in T2.arcs:
        arcs.append((relabel2[u], relabel2[v]))

    return n, arcs, relabel1, relabel2


# ----------------------------------------------------------------------------
# Bridge enumeration via balanced-demand backtracking
# ----------------------------------------------------------------------------


def _enumerate_bridges_one_direction(
    tail_demands: list[tuple[int, int]],
    head_demands: list[tuple[int, int]],
    max_yield: int,
) -> Iterator[list[tuple[int, int]]]:
    """Enumerate multisets of arcs (tail, head) where each `tail` appears
    exactly `tail_demands[i][1]` times among the tails, ditto for heads.

    `tail_demands[i] = (label, count_required)`; sum of counts on tails ==
    sum of counts on heads == number of bridges. We allow parallel arcs
    in the bridge multiset (same (tail, head) more than once is fine).

    Backtracking, returning the bridge multiset as a sorted tuple for
    canonical iteration.
    """
    # Total bridge count
    n_b = sum(c for _, c in tail_demands)
    assert n_b == sum(c for _, c in head_demands)

    # Expand demand to a list of "slots" by tail, but we backtrack by
    # head-assignment for each slot. To avoid producing the same multiset
    # multiple times via slot permutations, we fix a canonical slot order
    # (group by tail label, then sequentially) and require non-decreasing
    # head label within each tail-group's slot block.
    tail_seq: list[int] = []
    for tl, c in tail_demands:
        for _ in range(c):
            tail_seq.append(tl)
    # head_avail[label] = remaining demand for this head label
    head_avail: dict[int, int] = {h: c for h, c in head_demands}
    head_labels_sorted = [h for h, _ in head_demands]

    out_count = [0]
    bridges: list[tuple[int, int]] = []

    def backtrack(slot_idx: int, last_head_for_this_tail: int | None) -> Iterator[list[tuple[int, int]]]:
        nonlocal bridges
        if out_count[0] >= max_yield:
            return
        if slot_idx == n_b:
            yield list(bridges)
            out_count[0] += 1
            return
        t = tail_seq[slot_idx]
        new_tail_group = (
            slot_idx == 0 or tail_seq[slot_idx - 1] != t
        )
        # Allowed heads: head label h with head_avail[h] > 0, and if not
        # new_tail_group then h >= last_head_for_this_tail (canonicalize).
        for h in head_labels_sorted:
            if head_avail[h] <= 0:
                continue
            if not new_tail_group and last_head_for_this_tail is not None and h < last_head_for_this_tail:
                continue
            head_avail[h] -= 1
            bridges.append((t, h))
            yield from backtrack(slot_idx + 1, h)
            bridges.pop()
            head_avail[h] += 1
            if out_count[0] >= max_yield:
                return

    yield from backtrack(0, None)


def _enumerate_paired_bridges(
    out_demands_1: dict[int, int],  # tail label (in T1) -> required out-bridges from this tail
    in_demands_2: dict[int, int],   # head label (in T2) -> required in-bridges to this head
    out_demands_2: dict[int, int],
    in_demands_1: dict[int, int],
    max_yield: int,
) -> Iterator[tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]]:
    """Yield (bridges_12, bridges_21) tuples satisfying the four demands.

    Demands:
     - bridges_12 contributes 1 to T1-tail out-count and 1 to T2-head in-count;
     - bridges_21 contributes 1 to T2-tail out-count and 1 to T1-head in-count.

    Each tail/head label in the dict appears with the *exact* count required.
    """
    tail_demands_12 = sorted([(l, c) for l, c in out_demands_1.items() if c > 0])
    head_demands_12 = sorted([(l, c) for l, c in in_demands_2.items() if c > 0])
    tail_demands_21 = sorted([(l, c) for l, c in out_demands_2.items() if c > 0])
    head_demands_21 = sorted([(l, c) for l, c in in_demands_1.items() if c > 0])

    n12_required = sum(c for _, c in tail_demands_12)
    n12_required_head = sum(c for _, c in head_demands_12)
    n21_required = sum(c for _, c in tail_demands_21)
    n21_required_head = sum(c for _, c in head_demands_21)

    # If tail-sum != head-sum on one side we cannot satisfy demand exactly;
    # the caller will already have lifted demands to make this true.
    if n12_required != n12_required_head:
        return
    if n21_required != n21_required_head:
        return

    out_count = [0]

    # The two halves are independent.
    if n12_required == 0:
        list12_iter: Iterator[list[tuple[int, int]]] = iter([[]])
    else:
        list12_iter = _enumerate_bridges_one_direction(
            tail_demands_12, head_demands_12, max_yield
        )

    for b12 in list12_iter:
        if out_count[0] >= max_yield:
            return
        if n21_required == 0:
            list21_iter: Iterator[list[tuple[int, int]]] = iter([[]])
        else:
            list21_iter = _enumerate_bridges_one_direction(
                tail_demands_21, head_demands_21, max_yield - out_count[0]
            )
        for b21 in list21_iter:
            yield tuple(b12), tuple(b21)
            out_count[0] += 1
            if out_count[0] >= max_yield:
                return


# ----------------------------------------------------------------------------
# Public configuration
# ----------------------------------------------------------------------------


@dataclass
class DeficitGenConfig:
    """Configuration of the deficit-aware gluing sweep."""

    interface_sizes: tuple[int, ...] = (3, 4, 5)
    # Cap on interfaces tested per ordered pair of templates per size.
    max_interfaces_per_pair_per_size: int = 60
    # Cap on (b12, b21) bridge-assignment pairs per interface (across all
    # extra slack levels combined).
    max_bridges_per_interface: int = 32
    # When demand-sums on the two directions are unequal, we can add
    # "slack" bridges (touching arbitrary non-interface vertices). The
    # slack is at most this many extra bridges per direction, but we
    # prefer slack = 0 (exact match).
    max_extra_slack_per_direction: int = 1
    allow_self_glue: bool = True
    ordered_pairs: bool = True
    # We reject anything that does not have arc-connectivity *exactly* 3.
    require_arc_conn_exactly_3: bool = True
    # Cap of total verified-3-arc-strong instances kept per template pair.
    verified_per_pair_cap: int = 400
    seed: int = 20260516


# ----------------------------------------------------------------------------
# Interface enumeration with deterministic-but-shuffled order
# ----------------------------------------------------------------------------


def _enumerate_interfaces(
    T1: Benchmark, T2: Benchmark, s: int, max_count: int
) -> Iterator[tuple[tuple[int, ...], tuple[int, ...], tuple[tuple[int, int], ...]]]:
    """Yield (S1, S2, phi) triples with |S1| = |S2| = s."""
    if s > T1.n or s > T2.n:
        return
    count = 0
    for S1 in itertools.combinations(range(T1.n), s):
        for S2 in itertools.combinations(range(T2.n), s):
            for perm in itertools.permutations(S2):
                phi = tuple(zip(S1, perm))
                yield S1, S2, phi
                count += 1
                if count >= max_count:
                    return


# ----------------------------------------------------------------------------
# Main generator
# ----------------------------------------------------------------------------


def generate_deficit_gluings(
    templates: list[Benchmark],
    config: DeficitGenConfig,
) -> Iterator[DeficitGluedInstance]:
    """Stream DeficitGluedInstance candidates.

    For each template pair and interface, compute deficits and enumerate
    bridge assignments that exactly match each non-interface vertex's
    in/out deficit (templates here are 2-arc-strong, so each non-interface
    vertex's deficit is 0 or 1).
    """
    if config.ordered_pairs:
        pair_iter: Iterator[tuple[Benchmark, Benchmark]] = itertools.product(
            templates, templates
        )
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

        out_def1, in_def1 = _per_vertex_deficits(T1)
        out_def2, in_def2 = _per_vertex_deficits(T2)

        for s in config.interface_sizes:
            for S1, S2, phi in _enumerate_interfaces(
                T1, T2, s, config.max_interfaces_per_pair_per_size
            ):
                # Compute non-interface deficits (the relevant numbers).
                non1 = [v for v in range(T1.n) if v not in S1]
                non2 = [v for v in range(T2.n) if v not in S2]

                # Relabel so we can describe demands in the post-glue labeling.
                n, base_arcs, relabel1, relabel2 = _glue_along_interface(
                    T1, T2, S1, S2, phi
                )

                # Out-demand from non-interface T1 (must be satisfied by T1 -> T2 bridges).
                out_dem_1 = {relabel1[v]: out_def1[v] for v in non1 if out_def1[v] > 0}
                in_dem_2 = {relabel2[v]: in_def2[v] for v in non2 if in_def2[v] > 0}
                out_dem_2 = {relabel2[v]: out_def2[v] for v in non2 if out_def2[v] > 0}
                in_dem_1 = {relabel1[v]: in_def1[v] for v in non1 if in_def1[v] > 0}

                sum_out_1 = sum(out_dem_1.values())
                sum_in_2 = sum(in_dem_2.values())
                sum_out_2 = sum(out_dem_2.values())
                sum_in_1 = sum(in_dem_1.values())

                # The minimum number of T1->T2 bridges is max(sum_out_1, sum_in_2).
                # If they are unequal, we have to "pad" the smaller side by sending
                # extra bridges into vertices that already meet the floor; we permit
                # at most `max_extra_slack_per_direction` such extras per direction.
                target_12 = max(sum_out_1, sum_in_2)
                slack_tail_12 = target_12 - sum_out_1
                slack_head_12 = target_12 - sum_in_2
                target_21 = max(sum_out_2, sum_in_1)
                slack_tail_21 = target_21 - sum_out_2
                slack_head_21 = target_21 - sum_in_1

                if (
                    slack_tail_12 > config.max_extra_slack_per_direction
                    or slack_head_12 > config.max_extra_slack_per_direction
                    or slack_tail_21 > config.max_extra_slack_per_direction
                    or slack_head_21 > config.max_extra_slack_per_direction
                ):
                    continue
                if target_12 + target_21 == 0:
                    # No bridges needed: gluing already 3-arc-strong from interface alone.
                    # Possible if all non-interface deficits are 0 (rare; would mean
                    # the interface S_i covers exactly the deg-2 vertices of T_i).
                    pass

                # If we have slack to fill, lift the demand by adding "free"
                # tail/head choices among the appropriate non-interface vertices.
                # We add one extra unit at a time to each non-interface vertex
                # that already has deficit 0, but cap at `max_extra_slack`.
                # To keep enumeration bounded, we just pick the first eligible
                # vertex deterministically per slack unit.
                def _pad(dem: dict[int, int], non_labels: list[int], slack: int) -> dict[int, int]:
                    if slack <= 0:
                        return dem
                    out = dict(dem)
                    added = 0
                    for v in non_labels:
                        if added >= slack:
                            break
                        out[v] = out.get(v, 0) + 1
                        added += 1
                    return out

                non1_labels = sorted(relabel1[v] for v in non1)
                non2_labels = sorted(relabel2[v] for v in non2)
                out_dem_1_p = _pad(out_dem_1, non1_labels, slack_tail_12)
                in_dem_2_p = _pad(in_dem_2, non2_labels, slack_head_12)
                out_dem_2_p = _pad(out_dem_2, non2_labels, slack_tail_21)
                in_dem_1_p = _pad(in_dem_1, non1_labels, slack_head_21)

                # Enumerate bridge multisets.
                for b12, b21 in _enumerate_paired_bridges(
                    out_dem_1_p,
                    in_dem_2_p,
                    out_dem_2_p,
                    in_dem_1_p,
                    config.max_bridges_per_interface,
                ):
                    arcs = (
                        tuple(base_arcs)
                        + tuple(b12)
                        + tuple(b21)
                    )
                    summary = (sum_out_1, sum_in_1, sum_out_2, sum_in_2)
                    name = (
                        f"glueD[{T1.name}+{T2.name}]"
                        f"_s{s}_S1{''.join(str(x) for x in S1)}"
                        f"_S2{''.join(str(x) for x in S2)}"
                        f"_phi{''.join(str(b) for _, b in phi)}"
                        f"_b12n{len(b12)}_b21n{len(b21)}"
                        f"_h{abs(hash(arcs)) % (1 << 32):08x}"
                    )
                    yield DeficitGluedInstance(
                        name=name,
                        n=n,
                        arcs=arcs,
                        template1=T1.name,
                        template2=T2.name,
                        S1=tuple(S1),
                        S2=tuple(S2),
                        phi=tuple(phi),
                        bridges_12=tuple(b12),
                        bridges_21=tuple(b21),
                        deficit_summary=summary,
                    )


# ----------------------------------------------------------------------------
# Convenience: degree-feasibility pre-gate (no min-cut needed)
# ----------------------------------------------------------------------------


def vertex_degree_feasible(arcs: list[tuple[int, int]], n: int) -> bool:
    """Quick necessary condition for 3-arc-strong: every vertex has
    out-degree and in-degree >= 3."""
    outd = [0] * n
    ind = [0] * n
    for u, v in arcs:
        outd[u] += 1
        ind[v] += 1
    return all(d >= 3 for d in outd) and all(d >= 3 for d in ind)


def passes_arc_strong_3(D: Digraph, exact: bool = True) -> bool:
    """True iff D is 3-arc-strong; iff arc-connectivity is exactly 3 when
    `exact` is set. Mirrors v1's `glue.passes_arc_strong_3`."""
    if not D.is_strongly_connected():
        return False
    k = D.arc_connectivity()
    if exact:
        return k == 3
    return k >= 3
