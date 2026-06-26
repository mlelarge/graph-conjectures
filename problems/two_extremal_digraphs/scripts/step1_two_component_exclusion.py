#!/usr/bin/env python3
"""
Audit the criticality reduction behind the two-component exclusion theorem.

The theorem itself is symbolic (docs/three_connected_wheel.md, Step 1a):

    3-connected + 2-extremal  =>  F_D cannot have exactly two components.

This script checks the finite, data-facing parts of that proof:

  * R5's K4 witness: the equations making every cross arc bichromatic are
    inconsistent, although the digraph is 2-dicolourable and not opposite-cross;
  * every genuine two-component 2-extremal member in L_3..L_7 has no internal
    bad dicycle;
  * its single arcs are exactly two arc-disjoint directed cycles, one for each
    relative flip parity.

The final tight-cut/Steiner-separator step has no positive 3-connected example
to inspect (the theorem says none exists); it is proved in the document.
"""

import itertools
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from fd_cover_cuts import general_flip_profile, k2_profile  # noqa: E402
from fd_flip_cube import (  # noqa: E402
    cycle_bad_partials,
    f_components_and_bits,
    simple_directed_cycles,
)
from r4_opposite_cross_casework import (  # noqa: E402
    cross_arc_parities,
    k4_both_arc_parity_not_cover,
)
from seam_invariant import split_digons_singles  # noqa: E402
from step1b_fd_connectivity import vertex_connectivity  # noqa: E402


def load_truth():
    for n in range(3, 8):
        path = os.path.join(ROOT, "data", f"L_{n}.json")
        with open(path) as f:
            rows = json.load(f)
        for index, row in enumerate(rows):
            raw = row["arcs"] if isinstance(row, dict) else row
            yield n, index, frozenset(map(tuple, raw))


def cycle_arcs(cycle):
    return frozenset(
        (cycle[i], cycle[(i + 1) % len(cycle)])
        for i in range(len(cycle))
    )


def two_component_cycle_reduction(n, arcs):
    digons, singles = split_digons_singles(n, arcs)
    comp, bit, comps = f_components_and_bits(n, digons)
    if comp is None or len(comps) != 2:
        return None

    internal = set()
    families = {0: set(), 1: set()}
    for cycle in simple_directed_cycles(n, singles):
        for partial in cycle_bad_partials(cycle, comp, bit, 2):
            values = dict(partial)
            if len(values) == 1:
                internal.add(tuple(cycle))
            elif len(values) == 2:
                families[values[0] ^ values[1]].add(tuple(cycle))

    family_arcs = {
        delta: {cycle_arcs(cycle) for cycle in cycles}
        for delta, cycles in families.items()
    }
    cores = {}
    for delta in (0, 1):
        if not family_arcs[delta]:
            cores[delta] = frozenset()
        else:
            cores[delta] = frozenset.intersection(*family_arcs[delta])

    return {
        "internal": internal,
        "families": families,
        "cores": cores,
        "single_arcs": frozenset(singles),
        "core_union": cores[0] | cores[1],
        "core_intersection": cores[0] & cores[1],
    }


def check_k4_correction():
    n, arcs = k4_both_arc_parity_not_cover()
    profile = k2_profile(n, arcs)
    parities = {row[3] for row in cross_arc_parities(n, arcs)}
    assert parities == {0, 1}
    assert profile["mode"] == "none"
    assert not profile["covered"]
    assert H.chi_vec(n, arcs) == 2
    return profile


def k3_affine_cover_audit():
    """Check the finite affine facts used by the k=3 line-cover proof."""
    points = frozenset(itertools.product((0, 1), repeat=2))
    constraints = []

    for value in (0, 1):
        constraints.append(
            {
                "name": f"x1={value}",
                "bad": frozenset(x for x in points if x[0] == value),
                "support": frozenset((0, 1)),
            }
        )
        constraints.append(
            {
                "name": f"x2={value}",
                "bad": frozenset(x for x in points if x[1] == value),
                "support": frozenset((0, 2)),
            }
        )
        constraints.append(
            {
                "name": f"x1^x2={value}",
                "bad": frozenset(
                    x for x in points if (x[0] ^ x[1]) == value
                ),
                "support": frozenset((1, 2)),
            }
        )
    for point in points:
        constraints.append(
            {
                "name": f"point-{point}",
                "bad": frozenset((point,)),
                "support": frozenset((0, 1, 2)),
            }
        )

    covers = []
    for cover in itertools.combinations(constraints, 3):
        if frozenset().union(*(row["bad"] for row in cover)) != points:
            continue
        if any(
            frozenset().union(
                *(row["bad"] for j, row in enumerate(cover) if j != i)
            )
            == points
            for i in range(3)
        ):
            continue
        covers.append(cover)

    assert covers
    for cover in covers:
        lines = [row for row in cover if len(row["bad"]) == 2]
        assert lines
        for line in lines:
            others = [row for row in cover if row is not line]
            assert all(len(line["bad"] | row["bad"]) >= 3 for row in others)

            # If both other cycles visit a component used by the line cycle,
            # they share another component. This is the outside-component
            # fact used to keep them on the same side of a tight tree cut.
            for component in line["support"]:
                if all(component in row["support"] for row in others):
                    common_outside = (
                        (
                            others[0]["support"]
                            & others[1]["support"]
                        )
                        - frozenset((component,))
                    )
                    assert common_outside
    return covers


def directed_theta_audit():
    """Exhaustively test the elementary shared-arc theta fact through n=6."""

    def canonical_cycle(cycle):
        return min(
            tuple(cycle[i:] + cycle[:i])
            for i in range(len(cycle))
        )

    counts = Counter()
    for n in range(3, 7):
        cycles = set()
        for length in range(3, n + 1):
            for vertices in itertools.permutations(range(n), length):
                cycles.add(canonical_cycle(list(vertices)))
        cycles = sorted(cycles)
        arc_sets = [cycle_arcs(cycle) for cycle in cycles]

        for i, j in itertools.combinations(range(len(cycles)), 2):
            common = arc_sets[i] & arc_sets[j]
            if not common:
                continue
            union = arc_sets[i] | arc_sets[j]
            if any((v, u) in union for u, v in union):
                continue
            common_vertices = {v for arc in common for v in arc}
            assert any(
                H._maxflow_unit(n, union, u, v) >= 2
                for u in common_vertices
                for v in common_vertices
                if u != v
            )
            counts[n] += 1
    return counts


def pure_point_stress_audit():
    """Check two sharp k=3 near-misses; both fail exactly at lambda >= 3."""
    n = 9
    forest = (
        (0, 1),
        (1, 2),
        (3, 4),
        (4, 5),
        (6, 7),
        (7, 8),
    )
    component = tuple(v // 3 for v in range(n))
    bit = (0, 1, 0) * 3
    omega = tuple((0, x1, x2) for x1, x2 in itertools.product((0, 1), repeat=2))

    examples = {
        "overlap": (
            (0, 3, 8, 6),
            (0, 3, 7),
            (0, 2, 4, 8, 6),
            (1, 3, 8, 5),
        ),
        "arc-disjoint": (
            (2, 3, 6),
            (2, 5, 7),
            (0, 4, 6),
            (1, 8, 3),
        ),
    }

    def bad_points(cycle):
        return frozenset(
            flip
            for flip in omega
            if len(
                {
                    bit[v] ^ flip[component[v]]
                    for v in cycle
                }
            )
            == 1
        )

    rows = {}
    for name, cycles in examples.items():
        cycle_edge_sets = tuple(cycle_arcs(cycle) for cycle in cycles)
        singles = frozenset().union(*cycle_edge_sets)
        digon_arcs = frozenset(
            arc
            for u, v in forest
            for arc in ((u, v), (v, u))
        )
        arcs = singles | digon_arcs

        assert {
            next(iter(bad_points(cycle)))
            for cycle in cycles
        } == set(omega)
        assert all(len(bad_points(cycle)) == 1 for cycle in cycles)

        all_bad_cycles = []
        for cycle in simple_directed_cycles(n, singles):
            bad = bad_points(cycle)
            if bad:
                all_bad_cycles.append((cycle, bad))
        assert all(len(bad) == 1 for _, bad in all_bad_cycles)

        if name == "arc-disjoint":
            assert sum(map(len, cycle_edge_sets)) == len(singles)
            counts = Counter(
                next(iter(bad))
                for _, bad in all_bad_cycles
            )
            assert counts == Counter({flip: 1 for flip in omega})
        else:
            assert sum(map(len, cycle_edge_sets)) > len(singles)

        assert H.is_eulerian_deg(n, arcs)
        assert H.chi_vec(n, arcs) == 3
        assert all(H.chi_vec(n, arcs - {arc}) <= 2 for arc in arcs)
        assert vertex_connectivity(n, arcs) >= 3
        assert H.lambda_D(n, arcs) >= 3
        rows[name] = {
            "lambda": H.lambda_D(n, arcs),
            "kappa": vertex_connectivity(n, arcs),
            "bad_cycles": len(all_bad_cycles),
        }
    return rows


def main():
    k4 = check_k4_correction()
    print("# R5 correction")
    print("  all-cross equations consistent: False")
    print(f"  opposite-cross mode: {k4['mode']}")
    print(f"  chi_vec: {k4['chi_vec']}")

    covers = k3_affine_cover_audit()
    theta_counts = directed_theta_audit()
    print("# k=3 line-cover proof")
    print(f"  essential affine three-covers: {len(covers)}")
    print("  every cover has a line and passes the outside-component test")
    print(f"  shared-arc theta pairs through n=6: {sum(theta_counts.values())}")

    stress = pure_point_stress_audit()
    print("# k=3 pure-point stress witnesses")
    for name, row in stress.items():
        print(
            f"  {name}: kappa={row['kappa']} lambda={row['lambda']} "
            f"bad-cycles={row['bad_cycles']}"
        )

    counts = Counter()
    failures = []
    for n, index, arcs in load_truth():
        row = two_component_cycle_reduction(n, arcs)
        if row is None:
            continue
        counts["members"] += 1
        ok = (
            not row["internal"]
            and len(row["families"][0]) == 1
            and len(row["families"][1]) == 1
            and row["core_union"] == row["single_arcs"]
            and not row["core_intersection"]
        )
        counts["passed"] += int(ok)
        if not ok:
            failures.append((n, index, row))

    print("# L_3..L_7 two-component criticality reduction")
    print(f"  members: {counts['members']}")
    print(f"  passed: {counts['passed']}")
    print(f"  failures: {len(failures)}")
    for n, index, row in failures[:3]:
        print(f"  failure L_{n}[{index}]: {row}")

    k3_members = k3_passed = 0
    for n, index, arcs in load_truth():
        profile = general_flip_profile(n, arcs)
        if not profile or profile["k"] != 3:
            continue
        k3_members += 1
        cover = profile["minimum_cover"]
        union = set()
        total = 0
        for cycle_row in cover or ():
            arcs_in_cycle = cycle_arcs(cycle_row["cycle"])
            union.update(arcs_in_cycle)
            total += len(arcs_in_cycle)
        _, singles = split_digons_singles(n, arcs)
        support_sizes = sorted(
            min(cycle_row["support_sizes"])
            for cycle_row in (cover or ())
        )
        ok = (
            cover is not None
            and len(cover) in (3, 4)
            and (len(cover) == 3 or support_sizes == [3, 3, 3, 3])
            and union == set(singles)
            and total == len(union)
        )
        k3_passed += int(ok)
        if not ok:
            failures.append((n, index, profile))

    print("# L_3..L_7 three-component critical-cover shape")
    print(f"  members: {k3_members}")
    print(f"  classified and partitioned by cover cycles: {k3_passed}")
    print(f"  failures: {k3_members - k3_passed}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
