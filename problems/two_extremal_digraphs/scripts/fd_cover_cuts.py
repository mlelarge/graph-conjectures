#!/usr/bin/env python3
"""
Cut census for the k=2 flip-cover obstruction in Step 1b'.

When the digon forest F_D has exactly two components, the flip cube has four
points.  The bad single-dicycle sets have a simple form:

  * an internal same-parity single dicycle in one F-component is already bad for
    every flip assignment;
  * otherwise every bad cross dicycle cuts out one of the two parity classes
    x_0 xor x_1 = delta, so covering the cube requires both deltas.

This script audits that dichotomy against:

  * the truth set L_3..L_7;
  * the two-star near-miss/stress families from fd_flip_cube.py.

The point is not to prove Step 1b'.  It isolates the remaining proof target:
for k=2, rule out the two cover modes under U(D) 3-connected + MC(D)=0.
"""

import itertools
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import h2_oracle as H  # noqa: E402
from fd_flip_cube import (  # noqa: E402
    analyse,
    partial_contains,
    cycle_bad_partials,
    f_components_and_bits,
    load_truth,
    simple_directed_cycles,
    two_star_arcs,
    two_star_near_miss_rows,
)
from seam_invariant import mixed_2_cuts, split_digons_singles  # noqa: E402
from step1b_fd_connectivity import vertex_connectivity  # noqa: E402


def underlying_edges(arcs):
    return {frozenset((u, v)) for u, v in arcs if u != v}


def components_after_vertices(n, edges, removed):
    removed = set(removed)
    adj = {v: set() for v in range(n) if v not in removed}
    for e in edges:
        a, b = tuple(e)
        if a in removed or b in removed:
            continue
        adj[a].add(b)
        adj[b].add(a)

    comps = []
    seen = set()
    for start in adj:
        if start in seen:
            continue
        comp = []
        stack = [start]
        seen.add(start)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(tuple(sorted(comp)))
    return tuple(sorted(comps, key=lambda c: (len(c), c)))


def vertex_2_cuts(n, arcs):
    edges = underlying_edges(arcs)
    out = []
    for pair in itertools.combinations(range(n), 2):
        comps = components_after_vertices(n, edges, pair)
        if len(comps) > 1:
            out.append((pair, comps, frozenset(pair) in edges))
    return out


def partial_dict(partial):
    return dict(partial)


def k2_cycle_signature(cycle, comp, bit):
    partials = cycle_bad_partials(cycle, comp, bit, 2)
    if not partials:
        return None
    supports = {tuple(sorted(c for c, _ in partial)) for partial in partials}
    if len(supports) != 1:
        raise AssertionError((cycle, partials))
    support = next(iter(supports))
    if len(support) == 1:
        return {
            "kind": "internal",
            "component": support[0],
            "cycle": cycle,
            "partials": partials,
        }
    if len(support) == 2:
        d0 = partial_dict(partials[0])
        delta = d0[0] ^ d0[1]
        return {
            "kind": "cross",
            "delta": delta,
            "cycle": cycle,
            "partials": partials,
        }
    return {
        "kind": f"wide-{len(support)}",
        "support": support,
        "cycle": cycle,
        "partials": partials,
    }


def k2_profile(n, arcs):
    digons, singles = split_digons_singles(n, arcs)
    comp, bit, comps = f_components_and_bits(n, digons)
    if comp is None or len(comps) != 2:
        return None

    internal = []
    cross = []
    other = []
    for cycle in simple_directed_cycles(n, singles):
        sig = k2_cycle_signature(cycle, comp, bit)
        if sig is None:
            continue
        if sig["kind"] == "internal":
            internal.append(sig)
        elif sig["kind"] == "cross":
            cross.append(sig)
        else:
            other.append(sig)

    deltas = {sig["delta"] for sig in cross}
    if internal:
        mode = "internal"
    elif deltas == {0, 1}:
        mode = "opposite-cross"
    elif deltas:
        mode = f"one-cross-{next(iter(deltas))}"
    else:
        mode = "none"

    a = analyse(n, arcs)
    cuts = vertex_2_cuts(n, arcs)
    return {
        "mode": mode,
        "covered": a["covered"],
        "deltas": tuple(sorted(deltas)),
        "internal_count": len(internal),
        "cross_count": len(cross),
        "other_count": len(other),
        "internal_examples": internal[:3],
        "cross_examples": cross[:4],
        "kappa_U": vertex_connectivity(n, arcs),
        "lambda_repo": H.lambda_D(n, arcs),
        "MC": len(mixed_2_cuts(n, arcs)),
        "chi_vec": H.chi_vec(n, arcs),
        "is_2extremal": H.is_2extremal(n, arcs),
        "vertex_2_cuts": cuts,
        "nonedge_2_cuts": [cut for cut in cuts if not cut[2]],
    }


def cycle_masks(k, partials):
    return {
        mask
        for mask in range(1 << k)
        if any(partial_contains(mask, partial) for partial in partials)
    }


def minimum_cycle_cover(k, cycle_rows):
    target = set(range(1 << k))
    for r in range(1, min(5, len(cycle_rows)) + 1):
        for combo in itertools.combinations(cycle_rows, r):
            covered = set()
            for row in combo:
                covered |= row["masks"]
            if covered == target:
                return combo
    return None


def general_flip_profile(n, arcs):
    digons, singles = split_digons_singles(n, arcs)
    comp, bit, comps = f_components_and_bits(n, digons)
    if comp is None:
        return None

    k = len(comps)
    cycle_rows = []
    for cycle in simple_directed_cycles(n, singles):
        partials = cycle_bad_partials(cycle, comp, bit, k)
        if not partials:
            continue
        supports = tuple(
            sorted(tuple(sorted(c for c, _ in partial)) for partial in partials)
        )
        cycle_rows.append({
            "cycle": cycle,
            "partials": partials,
            "supports": supports,
            "support_sizes": tuple(sorted({len(s) for s in supports})),
            "masks": cycle_masks(k, partials),
        })

    a = analyse(n, arcs)
    min_cover = minimum_cycle_cover(k, cycle_rows) if a["covered"] else None
    cuts = vertex_2_cuts(n, arcs)
    return {
        "k": k,
        "components": tuple(tuple(sorted(c)) for c in comps),
        "covered": a["covered"],
        "covered_count": a["covered_count"],
        "cube_size": a["cube_size"],
        "partial_size_hist": dict(sorted(a["partial_size_hist"].items())),
        "cycle_count": len(cycle_rows),
        "cycles": cycle_rows,
        "minimum_cover": min_cover,
        "kappa_U": vertex_connectivity(n, arcs),
        "lambda_repo": H.lambda_D(n, arcs),
        "MC": len(mixed_2_cuts(n, arcs)),
        "chi_vec": H.chi_vec(n, arcs),
        "is_2extremal": H.is_2extremal(n, arcs),
        "vertex_2_cuts": cuts,
        "nonedge_2_cuts": [cut for cut in cuts if not cut[2]],
    }


def print_profile(prefix, name, n, arcs, profile):
    print(f"# {prefix}: {name}")
    print(f"  n={n} mode={profile['mode']} covered={profile['covered']} "
          f"deltas={profile['deltas']} internal={profile['internal_count']} "
          f"cross={profile['cross_count']} other={profile['other_count']}")
    print(f"  kappa_U={profile['kappa_U']} lambda_repo={profile['lambda_repo']} "
          f"MC={profile['MC']} chi_vec={profile['chi_vec']} "
          f"is_2extremal={profile['is_2extremal']}")
    print(f"  vertex_2_cuts={len(profile['vertex_2_cuts'])} "
          f"nonedge_2_cuts={len(profile['nonedge_2_cuts'])}")
    if profile["vertex_2_cuts"]:
        pair, comps, adjacent = profile["vertex_2_cuts"][0]
        print(f"  first_2cut pair={pair} adjacent={adjacent} comps={comps}")
    if profile["internal_examples"]:
        ex = profile["internal_examples"][0]
        print(f"  internal_cycle_example={ex['cycle']}")
    if profile["cross_examples"]:
        exs = [(ex["cycle"], ex["delta"]) for ex in profile["cross_examples"]]
        print(f"  cross_cycle_examples={exs}")


def print_general_profile(prefix, name, n, profile):
    print(f"# {prefix}: {name}")
    print(f"  n={n} k={profile['k']} covered={profile['covered']} "
          f"covered_count={profile['covered_count']}/{profile['cube_size']} "
          f"partial_size_hist={profile['partial_size_hist']}")
    print(f"  kappa_U={profile['kappa_U']} lambda_repo={profile['lambda_repo']} "
          f"MC={profile['MC']} chi_vec={profile['chi_vec']} "
          f"is_2extremal={profile['is_2extremal']}")
    print(f"  components={profile['components']}")
    print(f"  vertex_2_cuts={len(profile['vertex_2_cuts'])} "
          f"nonedge_2_cuts={len(profile['nonedge_2_cuts'])}")
    if profile["vertex_2_cuts"]:
        pair, comps, adjacent = profile["vertex_2_cuts"][0]
        print(f"  first_2cut pair={pair} adjacent={adjacent} comps={comps}")
    print(f"  single_dicycle_count_with_bad_partials={profile['cycle_count']}")
    if profile["minimum_cover"]:
        print("  minimum_cover_cycles:")
        for row in profile["minimum_cover"]:
            print(f"    cycle={row['cycle']} support_sizes={row['support_sizes']} "
                  f"masks={sorted(row['masks'])}")
    else:
        print("  minimum_cover_cycles=None")


def audit_truth():
    print("# truth set k=2 disconnected-F_D audit (L3..L7, excluding SOC)")
    counts = Counter()
    examples = {}
    total = 0
    for name, n, arcs in load_truth(7):
        if H.is_symmetric_odd_cycle(n, arcs):
            continue
        profile = k2_profile(n, arcs)
        if profile is None:
            continue
        total += 1
        key = (
            profile["mode"],
            profile["covered"],
            profile["kappa_U"],
            profile["MC"],
            bool(profile["nonedge_2_cuts"]),
        )
        counts[key] += 1
        examples.setdefault(key, (name, n, arcs, profile))
    print(f"  total k=2 members: {total}")
    print("  # key = (mode, covered, kappa_U, MC-count, has_nonedge_2cut)")
    for key, count in sorted(counts.items(), key=lambda kv: (kv[0], kv[1])):
        print(f"  {key}: {count}")
    print()
    for key in sorted(examples):
        name, n, arcs, profile = examples[key]
        print_profile("truth example", name, n, arcs, profile)
    print()


def audit_truth_k3_plus():
    print("# truth set k>=3 disconnected-F_D audit (L3..L7, excluding SOC)")
    rows = []
    counts = Counter()
    for name, n, arcs in load_truth(7):
        if H.is_symmetric_odd_cycle(n, arcs):
            continue
        profile = general_flip_profile(n, arcs)
        if profile is None or profile["k"] < 3:
            continue
        rows.append((name, n, arcs, profile))
        key = (
            profile["k"],
            profile["covered"],
            profile["kappa_U"],
            profile["MC"],
            bool(profile["nonedge_2_cuts"]),
            tuple(profile["partial_size_hist"].items()),
        )
        counts[key] += 1
    print(f"  total k>=3 members: {len(rows)}")
    print("  # key = (k, covered, kappa_U, MC-count, has_nonedge_2cut, partial_size_hist)")
    for key, count in sorted(counts.items(), key=lambda kv: (kv[0], kv[1])):
        print(f"  {key}: {count}")
    print()
    for name, n, arcs, profile in rows:
        print_general_profile("truth k>=3 example", name, n, profile)
    print()


def audit_two_star_3_3():
    print("# two digon 3-stars: near-miss k=2 profiles")
    counts = Counter()
    examples = {}
    for outmap, row in two_star_near_miss_rows():
        n = row["n"]
        arcs = two_star_arcs(3, 3, outmap)[1]
        profile = k2_profile(n, arcs)
        key = (
            profile["mode"],
            profile["covered"],
            profile["kappa_U"],
            profile["MC"],
            tuple(profile["deltas"]),
        )
        counts[key] += 1
        examples.setdefault(key, (dict(sorted(outmap.items())), n, arcs, profile))
    print("  # key = (mode, covered, kappa_U, MC-count, cross_deltas)")
    for key, count in sorted(counts.items(), key=lambda kv: (kv[0], kv[1])):
        print(f"  {key}: {count}")
    if examples:
        outmap, n, arcs, profile = next(iter(examples.values()))
        print(f"  first_outmap={outmap}")
        print_profile("two-star 3+3 example", "near-miss", n, arcs, profile)
    print()


def audit_two_star_4_4():
    print("# two digon 4-stars: covered-layout k=2 profiles")
    leaves = list(range(2, 10))
    counts = Counter()
    covered = 0
    examples = {}
    for perm in itertools.permutations(leaves):
        outmap = dict(zip(leaves, perm))
        if any(a == b for a, b in outmap.items()):
            continue
        if any(outmap.get(b) == a for a, b in outmap.items()):
            continue
        n, arcs = two_star_arcs(4, 4, outmap)
        profile = k2_profile(n, arcs)
        if not profile["covered"]:
            continue
        covered += 1
        key = (
            profile["mode"],
            profile["kappa_U"],
            profile["MC"],
            profile["chi_vec"],
            profile["is_2extremal"],
            bool(profile["nonedge_2_cuts"]),
        )
        counts[key] += 1
        examples.setdefault(key, (dict(sorted(outmap.items())), n, arcs, profile))
    print(f"  covered layouts: {covered}")
    print("  # key = (mode, kappa_U, MC-count, chi_vec, is_2extremal, has_nonedge_2cut)")
    for key, count in sorted(counts.items(), key=lambda kv: (kv[0], kv[1])):
        print(f"  {key}: {count}")
    print()
    for key in sorted(examples):
        outmap, n, arcs, profile = examples[key]
        print(f"  outmap={outmap}")
        print_profile("two-star 4+4 covered example", str(key), n, arcs, profile)
    print()


def audit_truth_k_histogram():
    counts = Counter()
    for name, n, arcs in load_truth(7):
        if H.is_symmetric_odd_cycle(n, arcs):
            continue
        digons, _ = split_digons_singles(n, arcs)
        comp, bit, comps = f_components_and_bits(n, digons)
        if comp is None:
            counts[("not-forest", None)] += 1
        else:
            counts[(len(comps), vertex_connectivity(n, arcs))] += 1
    print("# truth set F_D component histogram (non-SOC L3..L7)")
    print("  # key = (components_of_F_D, kappa_U)")
    for key, count in sorted(counts.items()):
        print(f"  {key}: {count}")
    print()


def main():
    audit_truth_k_histogram()
    audit_truth()
    audit_truth_k3_plus()
    audit_two_star_3_3()
    audit_two_star_4_4()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
