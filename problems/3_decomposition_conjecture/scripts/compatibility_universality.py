#!/usr/bin/env python3
"""Compute compatibility-universal trace classes.

A 2-pole trace set S is compatibility-universal if every trace in the
16-trace universe can be glued to at least one trace in S.  This is the
criterion used in docs/minimal_counterexample.md §3.13.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from decomposition import BOUNDARY_COLOUR, are_2pole_traces_compatible
from gadget_lattice import trace_json, trace_key_from_json, trace_set_key_from_json


def trace_from_key(key):
    chi, pi = key
    return (chi, frozenset(frozenset(block) for block in pi))


def is_compatibility_universal(trace_set: set, universe: set) -> tuple[bool, list]:
    missing = []
    trace_rows = [trace_from_key(t) for t in trace_set]
    for opposite in sorted(universe):
        opposite_row = trace_from_key(opposite)
        if not any(are_2pole_traces_compatible(row, opposite_row) for row in trace_rows):
            missing.append(opposite)
    return not missing, missing


def axis_signature(trace_set: set) -> dict[str, bool]:
    """Return the four axes from docs/minimal_counterexample.md §3.14."""
    axes = {
        "TT_joined": False,
        "TT_split": False,
        "TM": False,
        "MT": False,
    }
    for chi, pi in trace_set:
        boundary = tuple(BOUNDARY_COLOUR[state] for state in chi)
        if boundary == ("T", "T") and pi == ((0, 1),):
            axes["TT_joined"] = True
        elif boundary == ("T", "T") and pi == ((0,), (1,)):
            axes["TT_split"] = True
        elif boundary == ("T", "M"):
            axes["TM"] = True
        elif boundary == ("M", "T"):
            axes["MT"] = True
    return axes


def has_all_axes(trace_set: set) -> bool:
    return all(axis_signature(trace_set).values())


def build_payload(lattice_path: Path, replacement_sweep_path: Path | None = None) -> dict[str, Any]:
    lattice = json.loads(lattice_path.read_text())
    universe = {
        trace_key_from_json(trace)
        for cls in lattice["classes"]
        for trace in cls["traces"]
    }

    per_class = []
    axis_agreement_count = 0
    for cls in lattice["classes"]:
        trace_set = trace_set_key_from_json(cls["traces"])
        universal, missing = is_compatibility_universal(set(trace_set), universe)
        axes = axis_signature(set(trace_set))
        all_axes = all(axes.values())
        if universal == all_axes:
            axis_agreement_count += 1
        per_class.append(
            {
                "id": cls["id"],
                "min_order": cls["min_order"],
                "trace_count": cls["trace_count"],
                "member_count": cls["member_count"],
                "compatibility_universal": universal,
                "axis_signature": axes,
                "all_axes_present": all_axes,
                "missing_opposite_traces": [trace_json(t) for t in missing],
            }
        )

    universal_classes = [row for row in per_class if row["compatibility_universal"]]
    non_universal_classes = [row for row in per_class if not row["compatibility_universal"]]
    smallest = min(
        universal_classes,
        key=lambda row: (row["min_order"], row["trace_count"], row["id"]),
    )
    min_universal_trace_count = min(row["trace_count"] for row in universal_classes)
    max_non_universal_trace_count = max(row["trace_count"] for row in non_universal_classes)
    atomic_universal_classes = [
        {
            "id": row["id"],
            "min_order": row["min_order"],
            "trace_count": row["trace_count"],
            "member_count": row["member_count"],
        }
        for row in universal_classes
        if row["trace_count"] == min_universal_trace_count
    ]

    payload: dict[str, Any] = {
        "lattice": str(lattice_path),
        "lattice_class_count": len(lattice["classes"]),
        "universe_size": len(universe),
        "compatibility_universal_class_count": len(universal_classes),
        "axis_characterisation_agreement_count": axis_agreement_count,
        "trace_count_threshold": {
            "min_universal_trace_count": min_universal_trace_count,
            "max_non_universal_trace_count": max_non_universal_trace_count,
            "all_classes_with_trace_count_at_least_11_are_universal": all(
                row["compatibility_universal"] or row["trace_count"] <= 10
                for row in per_class
            ),
        },
        "atomic_universal_classes": atomic_universal_classes,
        "smallest_universal_class": {
            "id": smallest["id"],
            "min_order": smallest["min_order"],
            "trace_count": smallest["trace_count"],
            "member_count": smallest["member_count"],
            "compatibility_universal": True,
        },
        "per_class": per_class,
    }

    if replacement_sweep_path:
        sweep = json.loads(replacement_sweep_path.read_text())
        failure_rows = []
        for failure in sweep["summary"]["failure_trace_sets"]:
            trace_set = trace_set_key_from_json(failure["traces"])
            universal, missing = is_compatibility_universal(set(trace_set), universe)
            axes = axis_signature(set(trace_set))
            failure_rows.append(
                {
                    "graph6": failure["first_graph6"],
                    "ports": failure["first_ports"],
                    "occurrences": failure["occurrences"],
                    "trace_count": failure["side_trace_count"],
                    "compatibility_universal": universal,
                    "axis_signature": axes,
                    "all_axes_present": all(axes.values()),
                    "missing_opposite_traces": [trace_json(t) for t in missing],
                }
            )
        payload["n12_failures_universality"] = failure_rows
        if failure_rows:
            min_failure_universal_trace_count = min(
                row["trace_count"]
                for row in failure_rows
                if row["compatibility_universal"]
            )
            payload["n12_atomic_universal_failures"] = [
                row
                for row in failure_rows
                if row["compatibility_universal"]
                and row["trace_count"] == min_failure_universal_trace_count
            ]

    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    ap.add_argument(
        "--lattice",
        type=Path,
        default=root / "data" / "gadget_lattice_2pole_n10_both.json",
    )
    ap.add_argument(
        "--replacement-sweep",
        type=Path,
        default=root / "data" / "replacement_sweep_n12.json",
    )
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    payload = build_payload(args.lattice, args.replacement_sweep)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
