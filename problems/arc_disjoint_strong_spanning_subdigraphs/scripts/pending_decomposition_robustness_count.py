"""Count robustness of colour-prescribed pending split-off choices.

D50 established that prescribed opposite-colour split arcs complete on
the positive witness hosts, including the D42 chain kernel.  This script
counts how robust that is under a deterministic bounded enumeration:
for each sampled split-off choice, test every red/blue orientation of
the two split arcs through each independent-side vertex.

The D42 search space is large, so the count is explicitly capped and
reported as sampled evidence.  The smaller one-independent-vertex cases
are exhausted under the same local-choice cap used by the D49/D50 probes.
"""
from __future__ import annotations

import itertools
import os
import random
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from digraph import Digraph  # noqa: E402
from pending_decomposition_prescribed_probe import verify_sat_with_forced_colours  # noqa: E402
from pending_decomposition_probe import (  # noqa: E402
    SEED,
    cases,
    global_choice_iter,
    local_split_choices,
    occurrence_keys,
    relabel_core_arcs,
)


MAX_ROBUST_CHOICES = 120


def robustness_for_case(case, rng):
    host = list(case.host_arcs)
    host_set = set(host)
    stable = tuple(v for v in case.v1 if v not in (0, 1))
    core_arcs = relabel_core_arcs(host, case.v2)
    rel = {v: i for i, v in enumerate(case.v2)}

    per_vertex = {}
    for s in stable:
        choices = local_split_choices(host_set, case.v2, s, rng)
        if not choices:
            return {
                "name": case.name,
                "stable": stable,
                "status": "no-two-split-choice",
                "bad_vertex": s,
            }
        per_vertex[s] = choices

    if not stable:
        return {"name": case.name, "stable": stable, "status": "no-stable-vertices"}

    local_counts = {s: len(per_vertex[s]) for s in stable}
    total_global = 1
    for count in local_counts.values():
        total_global *= count

    choice_count = 0
    choice_with_any_sat = 0
    choice_with_all_sat = 0
    total_prescriptions = 0
    sat_prescriptions = 0
    lambda_counts = Counter()
    sad_status_counts = Counter()
    first_hit = None
    best_lambda = None
    best_split_paths = None

    for choice in global_choice_iter(per_vertex, rng):
        if choice_count >= MAX_ROBUST_CHOICES:
            break
        choice_count += 1

        split_arcs = []
        split_meta = []
        for s in stable:
            for x, y in choice[s]:
                arc = (rel[x], rel[y])
                split_arcs.append(arc)
                split_meta.append((s, x, y, arc))

        all_arcs = core_arcs + split_arcs
        all_keys = occurrence_keys(all_arcs)
        split_keys = all_keys[len(core_arcs):]
        D = Digraph.from_arcs(range(len(case.v2)), all_arcs)
        lam = D.arc_connectivity()
        lambda_counts[lam] += 1
        if best_lambda is None or lam > best_lambda:
            best_lambda = lam
            best_split_paths = list(split_meta)

        by_s = {}
        for s in stable:
            by_s[s] = [i for i, meta in enumerate(split_meta) if meta[0] == s]
            assert len(by_s[s]) == 2, (case.name, s, by_s[s])

        sat_for_choice = 0
        orientations = list(itertools.product((0, 1), repeat=len(stable)))
        for orientation_bits in orientations:
            total_prescriptions += 1
            forced = {}
            prescription = {}
            for s, bit in zip(stable, orientation_bits):
                first, second = by_s[s]
                red_i, blue_i = (first, second) if bit == 0 else (second, first)
                forced[split_keys[red_i]] = "R"
                forced[split_keys[blue_i]] = "B"
                prescription[s] = (
                    (split_meta[red_i], "R"),
                    (split_meta[blue_i], "B"),
                )

            res = verify_sat_with_forced_colours(D, forced)
            sad_status_counts[res["status"]] += 1
            if res["status"] == "SAT":
                sat_prescriptions += 1
                sat_for_choice += 1
                if first_hit is None:
                    first_hit = {
                        "choice_index": choice_count,
                        "lambda": lam,
                        "prescription": prescription,
                        "split_paths": list(split_meta),
                    }

        if sat_for_choice:
            choice_with_any_sat += 1
        if sat_for_choice == len(orientations):
            choice_with_all_sat += 1

    return {
        "name": case.name,
        "stable": stable,
        "status": "counted",
        "local_counts": local_counts,
        "total_global_choices_under_local_cap": total_global,
        "sampled_choices": choice_count,
        "choice_with_any_sat": choice_with_any_sat,
        "choice_with_all_sat": choice_with_all_sat,
        "total_prescriptions": total_prescriptions,
        "sat_prescriptions": sat_prescriptions,
        "lambda_counts": dict(sorted(lambda_counts.items())),
        "sad_status_counts": dict(sorted(sad_status_counts.items())),
        "first_hit": first_hit,
        "best_lambda": best_lambda,
        "best_split_paths": best_split_paths,
    }


def pct(num, den):
    if den == 0:
        return "0.0%"
    return f"{100.0 * num / den:.1f}%"


def main():
    rng = random.Random(SEED)
    rows = [robustness_for_case(case, rng) for case in cases()]
    print("Prescribed pending split-off robustness count")
    print(f"seed={SEED} max_choices_per_case={MAX_ROBUST_CHOICES}")
    for r in rows:
        print(f"{r['name']}: status={r['status']} stable={r.get('stable')}")
        if r["status"] != "counted":
            continue
        print(
            f"  local_counts={r['local_counts']} "
            f"global_under_cap={r['total_global_choices_under_local_cap']} "
            f"sampled={r['sampled_choices']}"
        )
        print(
            f"  choices_any_sat={r['choice_with_any_sat']}/"
            f"{r['sampled_choices']} ({pct(r['choice_with_any_sat'], r['sampled_choices'])}) "
            f"choices_all_sat={r['choice_with_all_sat']}/"
            f"{r['sampled_choices']} ({pct(r['choice_with_all_sat'], r['sampled_choices'])})"
        )
        print(
            f"  sat_prescriptions={r['sat_prescriptions']}/"
            f"{r['total_prescriptions']} "
            f"({pct(r['sat_prescriptions'], r['total_prescriptions'])})"
        )
        print(
            f"  lambda_counts={r['lambda_counts']} "
            f"sad_status_counts={r['sad_status_counts']}"
        )
        if r["first_hit"]:
            print(
                f"  first_hit_choice={r['first_hit']['choice_index']} "
                f"lambda={r['first_hit']['lambda']} "
                f"prescription={r['first_hit']['prescription']}"
            )
        else:
            print(
                f"  no_hit; best_lambda={r['best_lambda']} "
                f"best_split_paths={r['best_split_paths']}"
            )

    d42 = next(r for r in rows if r["name"] == "chain_kernel_D42_host")
    d28 = next(r for r in rows if r["name"] == "core_embedding_D28_host")
    assert d42["sat_prescriptions"] > 0, d42
    assert d42["choice_with_any_sat"] > 0, d42
    assert d28["sat_prescriptions"] == 0, d28
    assert max(d28["lambda_counts"]) == 1, d28
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
