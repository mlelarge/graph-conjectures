"""Colour-prescribed pending-decomposition split-off probe.

D49 found pending-style split-off hits by inspecting the arbitrary
red/blue colouring returned by the SAD SAT solver.  This strengthens that
diagnostic: after choosing two split arcs through each independent-side
vertex, we force one split arc to be red and the other blue and then ask
whether the split core still has a SAD.

This is still a witness-level probe, not a theorem.  A hit says the
pending-decomposition pattern is robust to prescribed split colours for
that split choice, which is closer to the published split-digraph proof
technology than relying on solver luck.
"""
from __future__ import annotations

import itertools
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from digraph import Digraph  # noqa: E402
from pending_decomposition_probe import (  # noqa: E402
    MAX_GLOBAL_CHOICES,
    SEED,
    cases,
    global_choice_iter,
    local_split_choices,
    occurrence_keys,
    relabel_core_arcs,
)
from pysat.solvers import Solver  # noqa: E402
from verifier_ilp import _validate_witness  # noqa: E402
from verifier_sat import _build_cnf  # noqa: E402


def verify_sat_with_forced_colours(D, forced_colours, solver_name="cadical153"):
    """Return SAT/UNSAT while forcing selected arc keys to R/B colours."""
    gate = None
    # Avoid importing verifier_sat.verify_sat's private sanity gate path here:
    # the probe cases all have n>=2, and the forced core may legitimately have
    # lambda < 2, in which case the CNF will simply be UNSAT.
    if gate is not None:
        return gate

    cnf, _vpool, x_vars, _t_vars, _level_vars = _build_cnf(D)
    for arc_key, colour in forced_colours.items():
        lit = x_vars[arc_key]
        if colour == "R":
            cnf.append([lit])
        elif colour == "B":
            cnf.append([-lit])
        else:
            raise ValueError((arc_key, colour))

    with Solver(name=solver_name, bootstrap_with=cnf) as solver:
        sat = solver.solve()
        if not sat:
            return {"status": "UNSAT", "witness": None}
        true_set = set(l for l in solver.get_model() if l > 0)
        red, blue = [], []
        for e in D.arcs():
            if x_vars[e] in true_set:
                red.append(e)
            else:
                blue.append(e)
        if not _validate_witness(D, red, blue):
            return {"status": "UNKNOWN", "witness": None}
        return {"status": "SAT", "witness": (red, blue)}


def prescribed_probe(case, rng):
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

    tried_choices = 0
    tried_prescriptions = 0
    sat_prescriptions = 0
    best = None

    for choice in global_choice_iter(per_vertex, rng):
        tried_choices += 1
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
        core_lambda = D.arc_connectivity()

        by_s = {}
        for s in stable:
            by_s[s] = [i for i, meta in enumerate(split_meta) if meta[0] == s]
            assert len(by_s[s]) == 2, (case.name, s, by_s[s])

        for orientation_bits in itertools.product((0, 1), repeat=len(stable)):
            tried_prescriptions += 1
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
            if res["status"] == "SAT":
                sat_prescriptions += 1
                return {
                    "name": case.name,
                    "stable": stable,
                    "status": "prescribed-hit",
                    "tried_choices": tried_choices,
                    "tried_prescriptions": tried_prescriptions,
                    "sat_prescriptions": sat_prescriptions,
                    "core_lambda": core_lambda,
                    "prescription": prescription,
                    "split_paths": split_meta,
                }

        if best is None or core_lambda > best.get("core_lambda", -1):
            best = {
                "core_lambda": core_lambda,
                "choice": choice,
                "split_paths": split_meta,
            }

        if tried_choices >= MAX_GLOBAL_CHOICES:
            break

    return {
        "name": case.name,
        "stable": stable,
        "status": "no-prescribed-hit",
        "tried_choices": tried_choices,
        "tried_prescriptions": tried_prescriptions,
        "sat_prescriptions": sat_prescriptions,
        "best": best,
    }


def main():
    rng = random.Random(SEED)
    rows = [prescribed_probe(case, rng) for case in cases()]
    print("Colour-prescribed pending decomposition probe")
    print(f"seed={SEED}")
    for row in rows:
        print(
            f"{row['name']}: status={row['status']} "
            f"stable={row.get('stable')}"
        )
        if row["status"] in {"prescribed-hit", "no-prescribed-hit"}:
            print(
                f"  tried_choices={row['tried_choices']} "
                f"tried_prescriptions={row['tried_prescriptions']} "
                f"sat_prescriptions={row['sat_prescriptions']}"
            )
        if row["status"] == "prescribed-hit":
            print(f"  core_lambda={row['core_lambda']}")
            print(f"  prescription={row['prescription']}")
            print(f"  split_paths={row['split_paths']}")
        elif row.get("best"):
            print(
                f"  best_core_lambda={row['best']['core_lambda']} "
                f"best_split_paths={row['best']['split_paths']}"
            )

    assert any(
        r["name"] == "chain_kernel_D42_host" and r["status"] == "prescribed-hit"
        for r in rows
    )
    assert any(
        r["name"] == "core_embedding_D28_host" and r["status"] == "no-prescribed-hit"
        for r in rows
    )
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
